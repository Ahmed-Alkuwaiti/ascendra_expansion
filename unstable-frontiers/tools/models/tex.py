"""Paints a model's box-UV texture atlas from each cube's material: a controlled, seeded pixel-art workflow.

Every face gets the material's pattern, light from above (top faces lighter, undersides darker) and a darker one-pixel
rim, so cubes read as separate plates. Materials marked glow are also written to a <name>_glowmask.png, which
GeckoLib's AutoGlowingGeoLayer draws at full brightness.
"""
from PIL import Image


def h(x, y, s=0):
    n = (x * 374761393 + y * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(len(a)))


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c[:3]) + tuple(c[3:])


class Material:
    """kind: chitin, plate, membrane, bone, eye, iron, flesh, glow. colors: base, dark, light (RGB or RGBA)."""

    def __init__(self, kind, base, dark=None, light=None, seed=1, glow=False, alpha=255, bands=0, rim=True, rust=(176, 92, 44)):
        self.kind = kind
        self.base = base
        self.dark = dark or shade(base, 0.6)
        self.light = light or shade(base, 1.35)
        self.seed = seed
        self.glow = glow
        self.alpha = alpha
        self.bands = bands
        self.rim = rim
        self.rust = rust

    def color(self, face, x, y, w, hgt):
        s = self.seed
        n = h(x, y, s)
        k = self.kind
        if k == 'chitin':
            # smooth lacquered chitin: a soft vertical gradient, sparse pits, and a glossy streak on the top
            g = y / max(1, hgt - 1) if face not in ('up', 'down') else 0.3
            c = mix(self.light, self.base, min(1.0, 0.35 + g)) if face != 'down' else self.base
            if n < 0.07:
                c = mix(c, self.dark, 0.45)
            if self.bands and face in ('north', 'south', 'east', 'west') and hgt > 3 and y % self.bands == self.bands - 1:
                c = mix(c, self.dark, 0.5)
            if face == 'up' and (x == w // 3 or x == w // 3 + 1) and h(0, y // 3, s) > 0.3:
                c = mix(c, self.light, 0.55)
        elif k == 'plate':
            g = y / max(1, hgt - 1) if face not in ('up', 'down') else 0.2
            c = mix(self.light, self.base, min(1.0, 0.3 + g))
            if n < 0.1:
                c = mix(c, self.dark, 0.35)
            if (x % 6 == 2 and y % 5 == 2) and w > 5 and hgt > 4:
                c = self.light                                      # rivet
            if self.rust and h(x // 2, y // 2, s + 1) > 0.88:
                c = mix(c, self.rust, 0.55)                         # rust (or lichen) bloom
        elif k == 'membrane':
            c = self.base
            if x % 6 == 0 or (y + x // 4) % 8 == 0:
                c = mix(self.base, self.dark, 0.6)                  # veins
            elif n > 0.97:
                c = mix(self.base, self.light, 0.5)
        elif k == 'bone':
            c = self.base if n > 0.25 else mix(self.base, self.dark, 0.3)
            if y % 4 == 0 and n > 0.6:
                c = mix(self.base, self.dark, 0.2)
        elif k == 'eye':
            c = self.light if (x == 0 and y == 0) else self.base
        elif k == 'iron':
            c = self.base if n > 0.3 else self.dark
            if n > 0.82:
                c = self.light                                      # rust
        elif k == 'flesh':
            c = self.base if n > 0.3 else self.dark
            if n > 0.92:
                c = self.light
        elif k == 'void':
            # night-sky hide: a deep gradient with scattered stars (the stars alone glow, see glows())
            g = y / max(1, hgt - 1) if face not in ('up', 'down') else (0.2 if face == 'up' else 0.9)
            c = mix(self.light, self.base, min(1.0, 0.25 + 0.75 * g))
            if n < 0.08:
                c = mix(c, self.dark, 0.5)
            if self.star(x, y):
                c = (255, 248, 220) if h(x, y, s + 5) > 0.4 else (150, 230, 255)
        elif k == 'glow':
            c = mix(self.base, self.light, 0.5 + 0.5 * h(x // 2, y // 2, s)) if n > 0.15 else self.dark
        else:
            c = self.base
        a = self.alpha
        if len(c) == 4:
            a, c = c[3], c[:3]
        light = {'up': 1.12, 'down': 0.7, 'north': 1.0, 'south': 0.85, 'east': 0.92, 'west': 0.92}[face]
        c = shade(c, light)
        if self.rim and (x == 0 or y == 0 or x == w - 1 or y == hgt - 1) and w > 2 and hgt > 2:
            c = shade(c, 0.72)
        return c + (a,)


def _star(self, x, y):
    return self.kind == 'void' and h(x, y, self.seed + 3) > (1.0 - self.stars)


def _glows(self, face, x, y):
    return self.glow or self.star(x, y)


Material.star = _star
Material.glows = _glows
Material.stars = 0.02


def faces(cube):
    w, hgt, d = cube.box()
    u, v = cube.uv
    return {'up': (u + d, v, w, d), 'down': (u + d + w, v, w, d), 'east': (u, v + d, d, hgt), 'north': (u + d, v + d, w, hgt),
            'west': (u + d + w, v + d, d, hgt), 'south': (u + 2 * d + w, v + d, w, hgt)}


def paint(model, path, extra=None):
    """Writes the atlas (and the glow mask if any material glows). extra(img, cube, faces) may add details."""
    img = Image.new('RGBA', (model.tex_w, model.tex_h), (0, 0, 0, 0))
    glow = Image.new('RGBA', (model.tex_w, model.tex_h), (0, 0, 0, 0))
    any_glow = False
    for b in model.bones:
        for c in b.cubes:
            m = c.material
            for face, (fx, fy, fw, fh) in faces(c).items():
                for y in range(fh):
                    for x in range(fw):
                        col = m.color(face, x, y, fw, fh)
                        img.putpixel((fx + x, fy + y), col)
                        if m.glows(face, x, y):
                            glow.putpixel((fx + x, fy + y), col[:3] + (255,))
                            any_glow = True
            if extra:
                extra(img, glow, c, faces(c))
    img.save(path)
    if any_glow or extra:
        if glow.getbbox():
            glow.save(path.replace('.png', '_glowmask.png'))
    return img
