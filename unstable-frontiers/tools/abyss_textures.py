"""Draws the Rift Observatory's and the Astral Abyss's textures: the 16x16 blocks (procedural, seeded, so every run gives
the same pixels), the 16x16 items (pixel grids below, one character per pixel, '.' transparent) and the sky textures
(nebula band, eclipsed planet, drifting silhouettes). Run from the project folder: `python3 tools/abyss_textures.py`.
Original art; nothing is copied from another mod or from Minecraft."""
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers', 'textures')

# the Abyss palette: cold slate, violet shadow, teal starlight, a warm eclipse rim
SHALE = [(22, 20, 38), (32, 29, 52), (42, 38, 66), (54, 49, 82)]
BRICK = [(40, 38, 64), (58, 55, 88), (74, 70, 108), (92, 88, 128)]
MOSS = [(20, 70, 84), (32, 104, 112), (58, 150, 150), (120, 220, 210)]
LUMEN = [(70, 160, 220), (130, 210, 250), (200, 245, 255), (255, 255, 255)]
VIOLET = [(48, 20, 72), (86, 40, 126), (140, 80, 196), (210, 160, 255)]
GOLD = [(120, 70, 20), (196, 130, 40), (250, 200, 90), (255, 240, 180)]
ROSE = [(90, 20, 40), (160, 40, 70), (230, 90, 110), (255, 170, 170)]


def save(img, *path):
    p = os.path.join(OUT, *path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    img.save(p)


def grain(seed, pal, weights=(3, 4, 3, 1)):
    r = random.Random(seed)
    img = Image.new('RGBA', (16, 16))
    for y in range(16):
        for x in range(16):
            img.putpixel((x, y), pal[r.choices(range(len(pal)), weights)[0]] + (255,))
    return img


def strata(seed):
    """Astral shale: layered slate, a few pale fracture lines."""
    r = random.Random(seed)
    img = grain(seed, SHALE)
    for band in (3, 8, 12):
        off = r.randint(-1, 1)
        for x in range(16):
            y = (band + off + (1 if r.random() < 0.25 else 0)) % 16
            img.putpixel((x, y), SHALE[0] + (255,))
            if r.random() < 0.3:
                img.putpixel((x, (y + 1) % 16), SHALE[3] + (255,))
    for _ in range(3):
        img.putpixel((r.randrange(16), r.randrange(16)), (150, 170, 220, 255))
    return img


def bricks(seed):
    r = random.Random(seed)
    img = grain(seed, BRICK[:3], (2, 4, 2))
    for y in range(16):
        for x in range(16):
            row = y // 4
            edge = y % 4 == 3 or (x + (4 if row % 2 else 0)) % 8 == 7
            if edge:
                img.putpixel((x, y), SHALE[0] + (255,))
            elif y % 4 == 0 and r.random() < 0.5:
                img.putpixel((x, y), BRICK[3] + (255,))
    return img


def chiseled(seed):
    """Chiseled astral: a carved star dial with a lit core."""
    img = bricks(seed)
    d = ImageDraw.Draw(img)
    d.rectangle((1, 1, 14, 14), outline=SHALE[0])
    d.rectangle((2, 2, 13, 13), fill=BRICK[1], outline=BRICK[3])
    for i in range(8):
        a = i * math.pi / 4
        ln = 5 if i % 2 == 0 else 3
        d.line((7.5, 7.5, 7.5 + math.cos(a) * ln, 7.5 + math.sin(a) * ln), fill=BRICK[0])
    d.rectangle((6, 6, 9, 9), fill=LUMEN[1])
    d.point([(7, 7), (8, 8)], fill=LUMEN[3])
    d.point([(7, 8), (8, 7)], fill=LUMEN[2])
    return img


def starmoss_top(seed):
    r = random.Random(seed)
    img = grain(seed, MOSS[:3], (3, 5, 2))
    for _ in range(6):
        img.putpixel((r.randrange(16), r.randrange(16)), MOSS[3] + (255,))
    return img


def starmoss_side(seed):
    r = random.Random(seed)
    img = strata(seed + 1)
    for x in range(16):
        h = 3 + r.randint(0, 2)
        for y in range(h):
            img.putpixel((x, y), MOSS[r.choice((0, 1, 1, 2))] + (255,))
        if r.random() < 0.3:
            img.putpixel((x, h), MOSS[0] + (255,))
    return img


def crystal(seed):
    """Lumen crystal: faceted pale-blue clusters."""
    r = random.Random(seed)
    img = Image.new('RGBA', (16, 16), LUMEN[0] + (255,))
    d = ImageDraw.Draw(img)
    for _ in range(7):
        x, y = r.randrange(16), r.randrange(16)
        s = r.randint(2, 4)
        d.polygon([(x, y - s), (x + s // 2 + 1, y), (x, y + s), (x - s // 2 - 1, y)], fill=LUMEN[r.randint(1, 2)], outline=LUMEN[0])
    for _ in range(5):
        img.putpixel((r.randrange(16), r.randrange(16)), LUMEN[3] + (255,))
    return img


def ore(seed):
    """Astral ore: shale with cold starmetal flecks."""
    r = random.Random(seed)
    img = strata(seed)
    for _ in range(5):
        x, y = r.randrange(1, 15), r.randrange(1, 15)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (r.choice((-1, 1)), 0)):
            img.putpixel(((x + dx) % 16, (y + dy) % 16), (196, 210, 236, 255))
        img.putpixel((x, y), (255, 255, 255, 255))
    return img


def rift_glass():
    img = Image.new('RGBA', (16, 16), (120, 80, 200, 70))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 15, 15), outline=(60, 40, 110, 230))
    d.line((3, 12, 12, 3), fill=(220, 190, 255, 140))
    d.line((4, 13, 13, 4), fill=(190, 150, 255, 90))
    d.point([(3, 3), (11, 11)], fill=(240, 230, 255, 200))
    return img


def starbloom():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line((8, 15, 8, 7), fill=MOSS[1])
    d.line((8, 12, 5, 10), fill=MOSS[1])
    d.line((8, 11, 11, 9), fill=MOSS[2])
    for i in range(5):
        a = -math.pi / 2 + i * 2 * math.pi / 5
        d.line((8, 5, 8 + math.cos(a) * 3.4, 5 + math.sin(a) * 3.4), fill=LUMEN[1])
    d.point((8, 5), fill=GOLD[3])
    d.point([(8, 4), (7, 5), (9, 5)], fill=LUMEN[3])
    return img


def tendril():
    r = random.Random(7)
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for sx in (3, 8, 12):
        x = sx
        for y in range(16 - r.randint(0, 5)):
            img.putpixel((x, y), VIOLET[1 if y < 8 else 0] + (255,))
            if r.random() < 0.3:
                x = max(1, min(14, x + r.choice((-1, 1))))
        img.putpixel((x, y), VIOLET[3] + (255,))
    return img


def cyst():
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((2, 3, 13, 15), fill=VIOLET[1], outline=VIOLET[0])
    d.ellipse((4, 5, 11, 13), fill=VIOLET[2])
    d.ellipse((6, 7, 9, 10), fill=LUMEN[2])
    d.point([(5, 6), (10, 12)], fill=VIOLET[3])
    return img


def gate(open_):
    if open_:
        img = Image.new('RGBA', (16, 16), (40, 10, 70, 190))
        r = random.Random(11)
        for _ in range(26):
            img.putpixel((r.randrange(16), r.randrange(16)), (r.randint(160, 230), r.randint(120, 200), 255, r.randint(140, 255)))
        return img
    img = bricks(41)
    d = ImageDraw.Draw(img)
    d.rectangle((3, 3, 12, 12), fill=SHALE[1], outline=SHALE[0])
    d.line((4, 4, 11, 11), fill=VIOLET[1])
    d.line((11, 4, 4, 11), fill=VIOLET[1])
    d.point([(7, 7), (8, 8)], fill=VIOLET[2])
    return img


def ring_top(active, color=LUMEN):
    img = bricks(55)
    d = ImageDraw.Draw(img)
    d.ellipse((1, 1, 14, 14), outline=GOLD[1] if active else BRICK[0])
    d.ellipse((4, 4, 11, 11), fill=color[2] if active else SHALE[0], outline=GOLD[2] if active else BRICK[3])
    if active:
        d.point([(7, 7), (8, 8), (7, 8), (8, 7)], fill=color[3])
    return img


def engine_side(active):
    img = bricks(62)
    d = ImageDraw.Draw(img)
    d.rectangle((2, 2, 13, 13), fill=SHALE[1], outline=GOLD[1] if active else BRICK[0])
    # three sockets: lens, heart, chart
    for i, c in enumerate((LUMEN[2], ROSE[2], GOLD[2])):
        x = 3 + i * 4
        d.rectangle((x, 6, x + 2, 9), fill=c if active else SHALE[0], outline=BRICK[3])
    if active:
        d.line((2, 12, 13, 12), fill=VIOLET[3])
    return img


def vent_side():
    img = bricks(73)
    d = ImageDraw.Draw(img)
    for x in (3, 7, 11):
        d.line((x, 2, x, 13), fill=MOSS[2])
        d.point((x, 2), fill=MOSS[3])
    return img


def vent_top():
    img = Image.new('RGBA', (16, 16), SHALE[0] + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 15, 15), outline=BRICK[2])
    for y in (3, 6, 9, 12):
        d.line((2, y, 13, y), fill=MOSS[2])
    d.point([(4, 6), (10, 9)], fill=MOSS[3])
    return img


def altar_side():
    img = bricks(88)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 15, 2), fill=GOLD[0])
    d.line((0, 1, 15, 1), fill=GOLD[2])
    d.ellipse((5, 6, 10, 11), fill=SHALE[0], outline=ROSE[1])
    d.point([(7, 8), (8, 9)], fill=ROSE[3])
    return img


def altar_top():
    img = Image.new('RGBA', (16, 16), SHALE[1] + (255,))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 15, 15), outline=GOLD[1])
    d.ellipse((2, 2, 13, 13), fill=GOLD[1])
    d.ellipse((4, 4, 11, 11), fill=(8, 6, 14))
    d.arc((3, 3, 12, 12), 200, 330, fill=GOLD[3])
    return img


def blocks():
    out = {
        'astral_shale': strata(1), 'astral_bricks': bricks(2), 'chiseled_astral': chiseled(3), 'starmoss_top': starmoss_top(4),
        'starmoss_side': starmoss_side(5), 'lumen_crystal': crystal(6), 'rift_glass': rift_glass(), 'astral_ore': ore(8),
        'starbloom': starbloom(), 'void_tendril': tendril(), 'void_cyst': cyst(), 'abyss_gate': gate(False), 'abyss_gate_open': gate(True),
        'rift_engine_top': ring_top(False), 'rift_engine_side': engine_side(False), 'rift_engine_active_top': ring_top(True, VIOLET),
        'rift_engine_active_side': engine_side(True), 'updraft_vent_top': vent_top(), 'updraft_vent_side': vent_side(),
        'eclipse_altar_top': altar_top(), 'eclipse_altar_side': altar_side()}
    for name, img in out.items():
        save(img, 'block', name + '.png')
    # the open gate shimmers: a 4-frame strip
    strip = Image.new('RGBA', (16, 64))
    for f in range(4):
        r = random.Random(100 + f)
        frame = Image.new('RGBA', (16, 16), (40, 10, 70, 190))
        for _ in range(26):
            frame.putpixel((r.randrange(16), r.randrange(16)), (r.randint(160, 230), r.randint(120, 200), 255, r.randint(140, 255)))
        strip.paste(frame, (0, f * 16))
    save(strip, 'block', 'abyss_gate_open.png')
    with open(os.path.join(OUT, 'block', 'abyss_gate_open.png.mcmeta'), 'w') as f:
        f.write('{"animation": {"frametime": 4, "interpolate": true}}\n')


# ------------------------------------------------------------------------------------------------------------ items
P = {'k': (14, 12, 24), 'd': SHALE[2], 'g': BRICK[2], 'G': BRICK[3], 'b': LUMEN[0], 'B': LUMEN[1], 'w': LUMEN[3], 'c': LUMEN[2],
     'v': VIOLET[1], 'V': VIOLET[2], 'x': VIOLET[3], 'y': GOLD[1], 'Y': GOLD[2], 'z': GOLD[3], 'o': GOLD[0], 'r': ROSE[1], 'R': ROSE[2],
     'p': ROSE[3], 'm': MOSS[1], 'M': MOSS[2], 'n': (190, 200, 220), 'N': (230, 236, 248), 'i': (120, 128, 150), 's': (90, 60, 40),
     'S': (150, 110, 70), 'e': (8, 6, 14)}

ITEMS = {
    'focusing_lens': [
        '................',
        '.....kkkkkk.....',
        '....kyyyyyyk....',
        '...kyBBBBBByk...',
        '..kyBwccccBByk..',
        '..kyBcwcccbByk..',
        '..kyBccccccByk..',
        '..kyBcccccbByk..',
        '..kyBbcccbbByk..',
        '...kyBBBBBByk...',
        '....kyyyyyyk....',
        '.....kkYYkk.....',
        '.......yy.......',
        '......kyyk......',
        '.....koooook....',
        '................'],
    'coolant_heart': [
        '................',
        '.......kk.......',
        '......knnk......',
        '....kkknnkkk....',
        '...kbbBbbBbbk...',
        '..kbBcBBBBcBbk..',
        '..kbcwcBBccBbk..',
        '..kbBccBBcBBbk..',
        '..kbBBBBBBBBbk..',
        '...kbBcBBcBbk...',
        '....kbBBBBbk....',
        '.....kbBBbk.....',
        '......kbbk......',
        '.......kk.......',
        '................',
        '................'],
    'star_chart': [
        '................',
        '..kkkkkkkkkkkk..',
        '.kSssssssssssSk.',
        '.ksvvvvvvvvvvsk.',
        '.ksvwvvvvvvvvsk.',
        '.ksvvvVvvvwvvsk.',
        '.ksvvvvVvvvvvsk.',
        '.ksvvvvvVvvvvsk.',
        '.ksvvwvvvVVwvsk.',
        '.ksvvvvvvvvvvsk.',
        '.ksvvvvvwvvvvsk.',
        '.ksvvvvvvvvvvsk.',
        '.kSssssssssssSk.',
        '..kkkkkkkkkkkk..',
        '................',
        '................'],
    'astrolabe': [
        '................',
        '.......kk.......',
        '......kyyk......',
        '.....kkyykk.....',
        '...kkyYYYYykk...',
        '..kyYk.yy.kYyk..',
        '..kYk.kBBk.kYk..',
        '.kyY.kBwcBk.Yyk.',
        '.kyYyyBccByyYyk.',
        '.kyY.kBBBk..Yyk.',
        '..kYk.kkk..kYk..',
        '..kyYk.yy.kYyk..',
        '...kkyYYYYykk...',
        '.....kkyykk.....',
        '.......kk.......',
        '................'],
    'sigil_shard': [
        '................',
        '................',
        '.........kk.....',
        '........kRk.....',
        '.......kRpk.....',
        '......kvRRk.....',
        '.....kvVRpRk....',
        '....kvVVRRvk....',
        '....kvVxVRvk....',
        '...kvVVVvvk.....',
        '...kvVvvvk......',
        '....kvvvk.......',
        '.....kkk........',
        '................',
        '................',
        '................'],
    'eclipse_sigil': [
        '................',
        '.....kkkkkk.....',
        '...kkyYYYYykk...',
        '..kyYzeeeezYyk..',
        '..kYzeeeeeezYk..',
        '.kyzeeeeeeeezyk.',
        '.kYzeeeRReeezYk.',
        '.kYzeeRppReezYk.',
        '.kYzeeRppReezYk.',
        '.kYzeeeRReeezYk.',
        '.kyzeeeeeeeezyk.',
        '..kYzeeeeeezYk..',
        '..kyYzeeeezYyk..',
        '...kkyYYYYykk...',
        '.....kkkkkk.....',
        '................'],
    'raw_starmetal': [
        '................',
        '................',
        '.......kkk......',
        '.....kkinik.....',
        '....kinnNnik....',
        '...kinNnninik...',
        '...kinnninnik...',
        '..kiinnNnninik..',
        '..kinninnnniik..',
        '..kiinnnNnnik...',
        '...kiiinnniik...',
        '....kkiiiikk....',
        '......kkkk......',
        '................',
        '................',
        '................'],
    'starmetal_ingot': [
        '................',
        '................',
        '................',
        '................',
        '.....kkkkkkkk...',
        '....kNNNNNNnik..',
        '...kNNwNNNnnik..',
        '..kNNNNNNnnik...',
        '..kinnnnnniik...',
        '..kiiiiiiiik....',
        '...kkkkkkkk.....',
        '................',
        '................',
        '................',
        '................',
        '................'],
    'lumen_core': [
        '................',
        '................',
        '.......kk.......',
        '......kBBk......',
        '.....kBwcBk.....',
        '....kBcwccBk....',
        '...kBcccccbBk...',
        '..kBccwcccccBk..',
        '..kBcccccccbBk..',
        '...kBcccccbBk...',
        '....kBcccbBk....',
        '.....kBbbBk.....',
        '......kBBk......',
        '.......kk.......',
        '................',
        '................'],
    'eclipse_scale': [
        '................',
        '................',
        '.....kkkkkk.....',
        '...kkvvvvvvkk...',
        '..kvvVVVVVVvvk..',
        '..kvVVeeeeVVvk..',
        '.kvVVeexeeeVVvk.',
        '.kvVeeeeeeeeVvk.',
        '.kvVeeeeexeeVvk.',
        '..kvVeeeeeeVvk..',
        '..kvVVeeeeVVvk..',
        '...kvVVVVVVvk...',
        '....kvyyyyvk....',
        '.....kkzzkk.....',
        '................',
        '................'],
    'blinkstone': [
        '................',
        '................',
        '......kkkk......',
        '....kkmMMmkk....',
        '...kmMBBBBMmk...',
        '..kmMBwcccBMmk..',
        '..kMBccccccBMk..',
        '..kMBcceecccBk..',
        '..kMBcceeccBMk..',
        '..kmMBccccBMmk..',
        '...kmMBBBBMmk...',
        '....kkmMMmkk....',
        '......kkkk......',
        '................',
        '................',
        '................'],
    'corona': [
        '...........kkk..',
        '..........kzYk..',
        '.........kzYyk..',
        '........kzYyk...',
        '.......kzYyk....',
        '......kzYyk.....',
        '.....kzYyk......',
        '..k.kzYyk.......',
        '..kkzYyk........',
        '...kYyk.........',
        '..kyykRk........',
        '.kvvk.kRk.......',
        'kvVk...k........',
        'kVk.............',
        '.k..............',
        '................'],
    'star_bolt': [
        '................',
        '................',
        '................',
        '.......kk.......',
        '......kBBk......',
        '.....kBwwBk.....',
        '....kBwccwBk....',
        '...kBwcwwcwBk...',
        '...kBwcwwcwBk...',
        '....kBwccwBk....',
        '.....kBwwBk.....',
        '......kBBk......',
        '.......kk.......',
        '................',
        '................',
        '................'],
}


def items():
    for name, rows in ITEMS.items():
        assert len(rows) == 16 and all(len(r) == 16 for r in rows), name
        img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                if ch != '.':
                    img.putpixel((x, y), P[ch] + (255,))
        save(img, 'item', name + '.png')


# -------------------------------------------------------------------------------------------------------------- sky
def periodic_noise(w, h, cells, seed):
    """Value noise that wraps horizontally, so the nebula band tiles around the sky."""
    r = random.Random(seed)
    cx, cy = cells, max(2, cells * h // w)
    grid = [[r.random() for _ in range(cx)] for _ in range(cy + 1)]

    def f(t):
        return t * t * (3 - 2 * t)

    def at(x, y):
        gx, gy = x / w * cx, y / h * cy
        x0, y0 = int(gx), min(int(gy), cy - 1)
        tx, ty = f(gx - x0), f(gy - y0)
        a, b = grid[y0][x0 % cx], grid[y0][(x0 + 1) % cx]
        c, d = grid[y0 + 1][x0 % cx], grid[y0 + 1][(x0 + 1) % cx]
        return (a + (b - a) * tx) * (1 - ty) + (c + (d - c) * tx) * ty
    return at


def nebula():
    w, h = 512, 128
    layers = [periodic_noise(w, h, c, 900 + c) for c in (4, 8, 16, 32)]
    img = Image.new('RGBA', (w, h))
    for y in range(h):
        band = math.exp(-((y - h * 0.5) / (h * 0.24)) ** 2)
        for x in range(w):
            v = sum(l(x, y) * wgt for l, wgt in zip(layers, (0.45, 0.3, 0.17, 0.08)))
            v = max(0.0, (v - 0.38) / 0.62) * band
            hue = layers[1](x, (y + 40) % h)
            r_ = 70 + 140 * hue
            g_ = 40 + 60 * (1 - hue) + 50 * v
            b_ = 150 + 100 * (1 - hue)
            img.putpixel((x, y), (int(min(255, r_ * (0.5 + v))), int(min(255, g_ * (0.5 + v))), int(min(255, b_)), int(255 * min(1.0, v * 1.6))))
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    r = random.Random(5)
    for _ in range(260):
        x, y = r.randrange(w), int(h * 0.5 + r.gauss(0, h * 0.18)) % h
        img.putpixel((x, y), (255, 255, 255, r.randint(120, 255)))
    save(img, 'environment', 'abyss_nebula.png')


def planet():
    """A great dark world in eclipse: a black disc with a burning rim and a faint tilted ring."""
    s = 256
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    glow = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(30, 0, -1):
        a = int(110 * (1 - i / 30) ** 2)
        gd.ellipse((s / 2 - 80 - i * 1.6, s / 2 - 80 - i * 1.6, s / 2 + 80 + i * 1.6, s / 2 + 80 + i * 1.6), fill=(255, 150, 90, a))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse((s / 2 - 82, s / 2 - 82, s / 2 + 82, s / 2 + 82), fill=(255, 210, 150, 255))
    d.ellipse((s / 2 - 78, s / 2 - 80, s / 2 + 80, s / 2 + 78), fill=(10, 6, 18, 255))
    ring = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring)
    rd.ellipse((14, s / 2 - 22, s - 14, s / 2 + 22), outline=(170, 140, 230, 150), width=3)
    rd.ellipse((24, s / 2 - 16, s - 24, s / 2 + 16), outline=(120, 100, 200, 100), width=2)
    ring = ring.rotate(-18, resample=Image.BICUBIC)
    # the ring passes behind the disc on its upper half
    mask = Image.new('L', (s, s), 255)
    ImageDraw.Draw(mask).pieslice((s / 2 - 80, s / 2 - 80, s / 2 + 80, s / 2 + 80), 180 - 18, 360 - 18, fill=0)
    img.paste(ring, (0, 0), Image.composite(ring.getchannel('A'), Image.new('L', (s, s), 0), mask))
    save(img, 'environment', 'abyss_planet.png')


def drifter():
    """A far-off silhouette: a vast drifting thing with trailing fins, dark against the nebula, lit only along its back."""
    w, h = 256, 128
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    body = [(20, 66), (60, 50), (120, 44), (180, 48), (230, 60), (244, 66), (230, 72), (180, 80), (120, 84), (60, 80)]
    d.polygon(body, fill=(14, 10, 26, 235))
    for i, x in enumerate(range(70, 200, 26)):
        d.polygon([(x, 82), (x + 14, 82), (x - 8 + i * 2, 118 - i * 3)], fill=(14, 10, 26, 200))
        d.polygon([(x, 48), (x + 12, 46), (x - 10, 18 + i * 2)], fill=(14, 10, 26, 210))
    d.line(body[:6], fill=(150, 130, 220, 160), width=1)
    for x in (34, 40):
        d.point((x, 63), fill=(255, 200, 140, 255))
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    save(img, 'environment', 'abyss_drifter.png')


if __name__ == '__main__':
    blocks()
    items()
    nebula()
    planet()
    drifter()
    print('abyss textures written')
