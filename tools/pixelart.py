"""A small pixel-art engine for item sprites, in the style of hand-drawn Minecraft items.

Shapes (polygons, thick lines, tapered blades, ellipses, gems) are drawn in order onto a grid with no antialiasing. Each shape is
shaded on its own: lit edges facing the top-left, shaded edges facing the bottom-right, a shadow cast on anything drawn beneath
its rim. Materials are four-tone ramps with hue-shifted shading (cool shadows, warm light). The whole silhouette gets a dark
outline; glowing materials get a soft halo instead.
"""
import colorsys
import math
import random

import numpy as np
from PIL import Image, ImageDraw


def _hsv(c):
    return colorsys.rgb_to_hsv(*(v / 255 for v in c))


def _rgb(h, s, v):
    return tuple(int(round(max(0, min(1, x)) * 255)) for x in colorsys.hsv_to_rgb(h % 1.0, s, v))


def ramp(base, glow=False, sat=1.0):
    """Five tones from one colour: outline-dark, shadow, base, light, specular. Shadows lean toward blue, light toward yellow."""
    h, s, v = _hsv(base)
    s *= sat

    def shift(dh, ds, dv):
        hh = h + dh * (1 if (h < 0.15 or h > 0.65) else -1) * (0 if s < 0.08 else 1)
        return _rgb(hh, max(0, min(1, s + ds)), max(0, min(1, v + dv)))
    if glow:
        return [shift(0.0, 0.1, -0.35), shift(0.0, 0.05, -0.12), _rgb(h, s, v), shift(0.0, -0.35, 0.25), shift(0.0, -0.6, 0.4)]
    return [shift(0.04, 0.12, -0.5), shift(0.03, 0.08, -0.22), _rgb(h, s, v), shift(-0.03, -0.1, 0.16), shift(-0.05, -0.25, 0.3)]


class Mat:
    def __init__(self, base, glow=False, grain=None, sat=1.0, outline=None, flat=False):
        self.tones = ramp(base, glow, sat)
        self.glow = glow
        self.grain = grain          # None, 'wood', 'speckle', 'stripe'
        self.outline = outline      # explicit outline colour, else the darkest tone darkened further
        self.flat = flat            # no bevel (cloth, vines)


# ---------------------------------------------------------------------------------------------------- a library of materials
M = {
    'wood': Mat((122, 82, 48), grain='wood'), 'wood_d': Mat((84, 54, 34), grain='wood'), 'bark': Mat((92, 66, 40), grain='wood'),
    'leather': Mat((110, 66, 40), grain='stripe'), 'cloth_r': Mat((170, 30, 40)), 'cloth_b': Mat((40, 70, 160)),
    'iron': Mat((170, 176, 186)), 'steel': Mat((96, 104, 122)), 'dark': Mat((48, 46, 60)), 'black': Mat((30, 28, 38)),
    'gold': Mat((232, 180, 56)), 'brass': Mat((196, 150, 70)), 'bone': Mat((230, 222, 200)), 'white': Mat((236, 236, 244)),
    'moss': Mat((80, 150, 50), grain='speckle'), 'leaf': Mat((96, 176, 60)), 'vine': Mat((70, 140, 46), flat=True),
    'verdant': Mat((110, 230, 60), glow=True), 'verdant_m': Mat((60, 170, 60)),
    'sky': Mat((120, 220, 255), glow=True), 'sky_m': Mat((150, 196, 230)), 'aether': Mat((176, 214, 240)), 'storm': Mat((90, 190, 255), glow=True),
    'soul': Mat((70, 200, 255), glow=True), 'ember': Mat((255, 130, 40), glow=True), 'soulsteel': Mat((58, 62, 78)), 'rust': Mat((150, 70, 40)),
    'teal': Mat((40, 190, 170)), 'teal_g': Mat((80, 255, 220), glow=True), 'pearl': Mat((220, 240, 236)), 'coral': Mat((240, 120, 140)),
    'tidesteel': Mat((70, 170, 160)),
    'ice': Mat((170, 210, 250)), 'ice_g': Mat((200, 236, 255), glow=True), 'frost': Mat((226, 240, 255)), 'void_p': Mat((140, 80, 255), glow=True),
    'night': Mat((50, 44, 96)),
    'scarlet': Mat((220, 40, 60)), 'scarlet_g': Mat((255, 70, 90), glow=True), 'amber': Mat((255, 170, 40), glow=True), 'glass_r': Mat((250, 90, 110)),
    'chronite': Mat((120, 70, 200)), 'chrono_g': Mat((190, 110, 255), glow=True), 'clock': Mat((240, 230, 200)),
    'myc': Mat((170, 60, 190)), 'myc_g': Mat((250, 90, 240), glow=True), 'stalk': Mat((226, 214, 230)), 'myc_ingot': Mat((180, 150, 255)),
    'genesis': Mat((244, 242, 236)), 'abyss': Mat((18, 14, 26)), 'star': Mat((255, 250, 220), glow=True),
    'gem_g': Mat((90, 240, 90), glow=True), 'gem_c': Mat((90, 214, 255), glow=True), 'gem_o': Mat((255, 150, 40), glow=True),
    'gem_t': Mat((60, 240, 210), glow=True), 'gem_w': Mat((220, 240, 255), glow=True), 'gem_r': Mat((255, 60, 70), glow=True),
    'gem_y': Mat((255, 210, 70), glow=True), 'gem_m': Mat((255, 80, 220), glow=True), 'gem_v': Mat((170, 90, 255), glow=True),
    'string': Mat((220, 220, 210), flat=True), 'stone': Mat((120, 120, 128), grain='speckle'), 'deepslate': Mat((70, 70, 78), grain='speckle'),
}
GEMS = ['gem_g', 'gem_c', 'gem_o', 'gem_t', 'gem_w', 'gem_r', 'gem_y', 'gem_m']   # one per realm, realm order


class Sprite:
    def __init__(self, n=32, seed=1):
        self.n = n
        self.shapes = []            # (mask, mat, light)
        self.rnd = random.Random(seed)

    # -------------------------------------------------------------------------------------------- shapes
    def _mask(self, draw_fn):
        im = Image.new('L', (self.n, self.n), 0)
        draw_fn(ImageDraw.Draw(im))
        return np.array(im) > 0

    def poly(self, pts, mat, light=True):
        self.shapes.append((self._mask(lambda d: d.polygon([tuple(p) for p in pts], fill=255)), M[mat] if isinstance(mat, str) else mat, light))
        return self

    def rect(self, x0, y0, x1, y1, mat):
        return self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], mat)

    def ellipse(self, cx, cy, rx, ry, mat):
        self.shapes.append((self._mask(lambda d: d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)), M[mat], True))
        return self

    def line(self, p0, p1, w, mat, w1=None):
        """A straight band from p0 to p1, w wide at p0 and w1 at p1."""
        w1 = w if w1 is None else w1
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        return self.poly([(p0[0] + nx * w / 2, p0[1] + ny * w / 2), (p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2),
                          (p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2), (p0[0] - nx * w / 2, p0[1] - ny * w / 2)], mat)

    def path(self, pts, w, mat, w_end=None):
        """A thick polyline (vines, chains, curved hafts), tapering to w_end."""
        w_end = w if w_end is None else w_end
        for i in range(len(pts) - 1):
            a = w + (w_end - w) * i / (len(pts) - 1)
            b = w + (w_end - w) * (i + 1) / (len(pts) - 1)
            self.line(pts[i], pts[i + 1], a, mat, b)
            if i:
                self.ellipse(pts[i][0], pts[i][1], a / 2 - 0.01, a / 2 - 0.01, mat)
        return self

    def gem(self, cx, cy, r, mat):
        return self.poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], mat)

    def along(self, p0, p1, t, off=0.0):
        """The point a fraction t of the way from p0 to p1, pushed `off` to the side."""
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]
        L = math.hypot(dx, dy) or 1
        return (p0[0] + dx * t - dy / L * off, p0[1] + dy * t + dx / L * off)

    # -------------------------------------------------------------------------------------------- render
    def render(self, outline=True, halo=True):
        n = self.n
        sid = -np.ones((n, n), int)
        for i, (m, _, _) in enumerate(self.shapes):
            sid[m] = i
        out = np.zeros((n, n, 4), np.uint8)
        filled = sid >= 0

        def at(a, dx, dy, fill):
            b = np.full_like(a, fill)
            ys = slice(max(0, dy), n + min(0, dy))
            yd = slice(max(0, -dy), n + min(0, -dy))
            xs = slice(max(0, dx), n + min(0, dx))
            xd = slice(max(0, -dx), n + min(0, -dx))
            b[yd, xd] = a[ys, xs]
            return b
        up, left, down, right = at(sid, 0, -1, -1), at(sid, -1, 0, -1), at(sid, 0, 1, -1), at(sid, 1, 0, -1)
        up2, left2 = at(sid, 0, -2, -1), at(sid, -2, 0, -1)
        for i, (mask, mat, light) in enumerate(self.shapes):
            here = sid == i
            if not here.any():
                continue
            t = mat.tones
            tone = np.full((n, n), 2)
            if not mat.flat:
                lit = here & ((up != i) | (left != i))
                shade = here & ((down != i) | (right != i))
                tone[shade] = 1
                tone[lit & ~shade] = 3
                spec = here & (up != i) & (left != i) & (down == i) & (right == i)
                tone[spec] = 4
                # a shape drawn over this one casts a one-pixel shadow just below and right of its rim
                cast = here & (((up > i) & (up >= 0)) | ((left > i) & (left >= 0)))
                tone[cast] = 1
                # inner shine: a second band of light just inside the lit edge on larger shapes
                inner = here & (up == i) & (left == i) & ((up2 != i) | (left2 != i)) & (down == i) & (right == i)
                if mask.sum() > 40:
                    tone[inner & (tone == 2)] = 3
            if mat.grain:
                ys, xs = np.nonzero(here & (tone == 2))
                for y, x in zip(ys, xs):
                    r = self.rnd.random()
                    if mat.grain == 'wood' and ((x + 2 * y) % 5 == 0) and r < 0.8:
                        tone[y, x] = 1
                    elif mat.grain == 'speckle' and r < 0.22:
                        tone[y, x] = 1 if r < 0.12 else 3
                    elif mat.grain == 'stripe' and (x + y) % 3 == 0:
                        tone[y, x] = 1
            for k in range(5):
                sel = here & (tone == k)
                out[sel, :3] = t[k]
                out[sel, 3] = 255
        if outline:
            edge = ~filled & ((up >= 0) | (left >= 0) | (down >= 0) | (right >= 0))
            ys, xs = np.nonzero(edge)
            for y, x in zip(ys, xs):
                nb = [s for s in (up[y, x], left[y, x], down[y, x], right[y, x]) if s >= 0]
                mat = self.shapes[max(nb)][1]
                if mat.glow and halo:
                    c = mat.tones[1]
                    out[y, x] = (*c, 200)
                else:
                    c = mat.outline or tuple(int(v * 0.45) for v in mat.tones[0])
                    out[y, x] = (*c, 255)
        if halo:
            glow = np.zeros((n, n), bool)
            for i, (mask, mat, _) in enumerate(self.shapes):
                if mat.glow:
                    glow |= sid == i
            ring = np.zeros((n, n), bool)
            for dx in (-2, -1, 0, 1, 2):
                for dy in (-2, -1, 0, 1, 2):
                    if abs(dx) + abs(dy) <= 3:
                        ring |= at(glow, dx, dy, False)
            ring &= out[:, :, 3] == 0
            ys, xs = np.nonzero(ring)
            for y, x in zip(ys, xs):
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < n and 0 <= xx < n and glow[yy, xx]:
                        c = self.shapes[sid[yy, xx]][1].tones[2]
                        out[y, x] = (*c, 90)
                        break
        return Image.fromarray(out, 'RGBA')


def upscale(img, k):
    return img.resize((img.width * k, img.height * k), Image.NEAREST)
