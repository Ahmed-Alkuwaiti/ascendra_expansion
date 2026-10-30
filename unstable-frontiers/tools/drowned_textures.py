"""Draws the Drowned Expanse's textures: 16x16 blocks (procedural and seeded, so every run gives the same pixels) and
16x16 items (pixel grids, one character per pixel, '.' transparent). Run from the project folder:
`python3 tools/drowned_textures.py`. Original art; nothing is copied from another mod or from Minecraft."""
import os
import random

from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers', 'textures')

# the Drowned palette: wet blue-grey slate, sea-green verdigris, pale coral light, brass fittings
SLATE = [(30, 40, 50), (42, 56, 68), (56, 72, 86), (74, 92, 108)]
BRICK = [(44, 62, 70), (60, 82, 90), (78, 102, 110), (100, 126, 132)]
VERDI = [(30, 90, 84), (48, 130, 118), (90, 176, 160), (170, 230, 214)]
CORAL = [(40, 120, 170), (80, 180, 220), (160, 230, 250), (240, 255, 255)]
BRASS = [(96, 66, 26), (160, 116, 46), (214, 170, 80), (250, 222, 150)]


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


def slate(seed):
    """Brine slate: wet layered stone with salt flecks."""
    r = random.Random(seed)
    img = grain(seed, SLATE)
    for band in (4, 10):
        for x in range(16):
            y = (band + (1 if r.random() < 0.2 else 0)) % 16
            img.putpixel((x, y), SLATE[0] + (255,))
    for _ in range(5):
        img.putpixel((r.randrange(16), r.randrange(16)), (180, 200, 206, 255))
    return img


def bricks(seed):
    r = random.Random(seed)
    img = grain(seed, BRICK[:3], (2, 4, 2))
    for y in range(16):
        for x in range(16):
            row = y // 4
            if y % 4 == 3 or (x + (4 if row % 2 else 0)) % 8 == 7:
                img.putpixel((x, y), SLATE[0] + (255,))
            elif y % 4 == 0 and r.random() < 0.4:
                img.putpixel((x, y), BRICK[3] + (255,))
            elif r.random() < 0.07:
                img.putpixel((x, y), VERDI[1] + (255,))           # barnacle-green stain
    return img


def chiseled(seed):
    """Chiseled brine: a carved wave with a lit pearl in it."""
    img = bricks(seed)
    for x in range(2, 14):
        for y in range(2, 14):
            img.putpixel((x, y), BRICK[1] + (255,))
    for x in range(2, 14):
        img.putpixel((x, 2), SLATE[0] + (255,))
        img.putpixel((x, 13), SLATE[0] + (255,))
        img.putpixel((2, x), SLATE[0] + (255,))
        img.putpixel((13, x), SLATE[0] + (255,))
    wave = [9, 8, 7, 7, 8, 9, 9, 8, 7, 7]
    for i, y in enumerate(wave):
        img.putpixel((3 + i, y), VERDI[2] + (255,))
        img.putpixel((3 + i, y + 1), VERDI[1] + (255,))
    for (x, y) in ((7, 5), (8, 5), (7, 6), (8, 6)):
        img.putpixel((x, y), CORAL[2] + (255,))
    img.putpixel((7, 5), CORAL[3] + (255,))
    return img


def coral(seed):
    """Lumen coral: branching pale-blue polyps that glow."""
    r = random.Random(seed)
    img = grain(seed, CORAL[:2], (3, 2))
    for _ in range(14):
        x, y = r.randrange(16), r.randrange(16)
        img.putpixel((x, y), CORAL[3] + (255,))
        for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
            if r.random() < 0.6:
                img.putpixel(((x + dx) % 16, (y + dy) % 16), CORAL[2] + (255,))
    return img


def vent_top():
    img = slate(41)
    for y in range(16):
        for x in range(16):
            d = ((x - 7.5) ** 2 + (y - 7.5) ** 2) ** 0.5
            if d < 2.5:
                img.putpixel((x, y), (200, 250, 255, 255) if d < 1.3 else (120, 210, 230, 255))
            elif d < 4.5:
                img.putpixel((x, y), VERDI[0] + (255,) if int(d * 3) % 2 else SLATE[0] + (255,))
            elif d < 5.5:
                img.putpixel((x, y), BRASS[1] + (255,))
    return img


def vent_side():
    img = slate(43)
    for x in range(16):
        img.putpixel((x, 0), BRASS[2] + (255,))
        img.putpixel((x, 1), BRASS[1] + (255,))
    for y in range(2, 16, 4):
        for x in (3, 12):
            img.putpixel((x, y), (140, 220, 235, 255))
    return img


def glyph():
    """A tide glyph: a weathered post stone with a carved arrow-and-wave mark (it glows only through goggles)."""
    img = slate(51)
    mark = ['......xx......',
            '.....xxxx.....',
            '....xx..xx....',
            '......xx......',
            '......xx......',
            '.x..x.xx.x..x.',
            'x.xx.x..x.xx.x',
            '..............',
            '.x..x....x..x.',
            'x.xx.x..x.xx.x']
    for j, row in enumerate(mark):
        for i, ch in enumerate(row):
            if ch == 'x':
                img.putpixel((1 + i, 3 + j), (96, 156, 160, 255))
    return img


def gate_frames():
    strip = Image.new('RGBA', (16, 64))
    for f in range(4):
        r = random.Random(200 + f)
        frame = Image.new('RGBA', (16, 16), (20, 80, 110, 170))
        for y in range(16):
            for x in range(16):
                if (x + y * 2 + f * 4) % 9 == 0:
                    frame.putpixel((x, y), (90, 200, 220, 200))
        for _ in range(16):
            frame.putpixel((r.randrange(16), r.randrange(16)), (200, 250, 255, r.randint(160, 240)))
        strip.paste(frame, (0, f * 16))
    return strip


def bell(abyssal):
    pal = [(30, 22, 40), (60, 44, 80), (100, 80, 130), (170, 150, 210)] if abyssal else BRASS
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    r = random.Random(61 if abyssal else 63)
    for y in range(16):
        for x in range(16):
            c = pal[1] if (x + y) % 5 else pal[0]
            if r.random() < 0.2:
                c = pal[2]
            if y < 2:
                c = pal[3]
            img.putpixel((x, y), c + (255,))
    return img


def blocks():
    out = {'brine_slate': slate(1), 'brine_bricks': bricks(2), 'chiseled_brine': chiseled(3), 'lumen_coral': coral(4),
           'breath_vent_top': vent_top(), 'breath_vent_side': vent_side(), 'tide_glyph': glyph(), 'tide_bell': bell(False),
           'abyssal_bell': bell(True)}
    for name, img in out.items():
        save(img, 'block', name + '.png')
    save(gate_frames(), 'block', 'tide_gate.png')
    with open(os.path.join(OUT, 'block', 'tide_gate.png.mcmeta'), 'w') as f:
        f.write('{"animation": {"frametime": 5, "interpolate": true}}\n')


# ------------------------------------------------------------------------------------------------------------ items
P = {'k': (12, 16, 22), 'l': (92, 62, 36), 'L': (136, 96, 56), 'g': (150, 200, 220), 'G': (210, 240, 250), 'w': (255, 255, 255),
     'b': BRASS[1], 'B': BRASS[2], 'Y': BRASS[3], 'o': BRASS[0], 'c': (110, 120, 130), 'C': (170, 180, 190), 'i': (70, 78, 90),
     'v': VERDI[1], 'V': VERDI[2], 'q': CORAL[1], 'Q': CORAL[2], 'u': (40, 30, 70), 'U': (90, 70, 140), 'x': (170, 150, 230),
     'r': (40, 120, 130), 'R': (80, 180, 180), 'p': (230, 220, 240), 'P': (250, 245, 255), 'm': (80, 20, 40), 's': (60, 60, 70)}

ITEMS = {
    'abyssal_goggles': [
        '................',
        '................',
        '................',
        '................',
        '..kkkk....kkkk..',
        '.kbbbbk..kbbbbk.',
        'lkbGggbkkbGggbkl',
        'lkbgGgbbbbgGgbkl',
        'lkbggqbkkbggqbkl',
        '.kbbbbk..kbbbbk.',
        '..kkkk....kkkk..',
        '................',
        '................',
        '................',
        '................',
        '................'],
    'deep_sight_goggles': [
        '................',
        '................',
        '................',
        '.......YY.......',
        '..kkkk.bb.kkkk..',
        '.kYYYYk..kYYYYk.',
        'lkYRRRYkkYRRRYkl',
        'lkYRwRYYYYRwRYkl',
        'lkYRRrYkkYRRrYkl',
        '.kYYYYk..kYYYYk.',
        '..kkkk....kkkk..',
        '................',
        '................',
        '................',
        '................',
        '................'],
    'diving_rig': [
        '................',
        '.....kkkkkk.....',
        '....kbYBBBbk....',
        '...kcCCkkCCck...',
        '...kcCck.cCck...',
        '...kcCck.cCck...',
        '...kcCck.cCck...',
        '...kcCck.cCck...',
        '...kcCck.cCck...',
        '...kcCck.cCck...',
        '...kcicklcick...',
        '...kkkkLlkkkk...',
        '.......lL.......',
        '........ll......',
        '.........lk.....',
        '................'],
    'deep_rig': [
        '................',
        '.....kkkkkk.....',
        '....kYBBBBYk....',
        '...kvVVkkVVvk...',
        '...kvVvkkvVvk...',
        '..kkvVvkkvVvkk..',
        '..kbvVvkkvVvbk..',
        '..kbvVvkkvVvbk..',
        '..kkvVvkkvVvkk..',
        '...kvVvkkvVvk...',
        '...kvrvkkvrvk...',
        '...kkkkBBkkkk...',
        '.......bB.......',
        '........bb......',
        '.........bk.....',
        '................'],
    'swim_fins': [
        '................',
        '................',
        '...kk.....kk....',
        '..krrk...krrk...',
        '..krRk...krRk...',
        '..krRk...krRk...',
        '.krRRrk.krRRrk..',
        '.krRRrk.krRRrk..',
        'krRrRRrkrRrRRrk.',
        'krRrRRrkrRrRRrk.',
        'krrRrRrkrrRrRrk.',
        '.kkkkkk.kkkkkk..',
        '................',
        '................',
        '................',
        '................'],
    'breath_charm': [
        '................',
        '.....kkkkkk.....',
        '....k......k....',
        '...k........k...',
        '...k........k...',
        '....k......k....',
        '.....kbbbbk.....',
        '......kYYk......',
        '.....kQqqQk.....',
        '....kQPQqqQk....',
        '....kqQqqqQk....',
        '....kqqqqqqk....',
        '.....kQqqQk.....',
        '......kkkk......',
        '................',
        '................'],
    'echo_sounder': [
        '................',
        '.........k......',
        '........kGk.....',
        '...kkkkkkGk.....',
        '..kbbbbbbkk.....',
        '..kbkkkkkbk.....',
        '..kbkrRrkbk.....',
        '..kbkRwRkbk.....',
        '..kbkrRrkbk.....',
        '..kbkkkkkbk.....',
        '..kbYbYbYbk.....',
        '..kbbbbbbbk.....',
        '...kkkkkkk......',
        '................',
        '................',
        '................'],
    'pressure_valve': [
        '................',
        '......kkkk......',
        '.....kYBBYk.....',
        '......kbbk......',
        '.......kk.......',
        '.....kkbbkk.....',
        '....kBBbbBBk....',
        '...kBbkkkkbBk...',
        '...kBkCwCCkBk...',
        '...kBkCCCikBk...',
        '...kBbkkkkbBk...',
        '....kBBbbBBk....',
        '.....kkbbkk.....',
        '......kbbk......',
        '......kkkk......',
        '................'],
    'keel_plate': [
        '................',
        '................',
        '..kkkkkkkkkkk...',
        '.kcCCCCCCCCCik..',
        '.kCckCCCCkcCik..',
        '.kCCCCCvCCCCik..',
        '.kCCvCCCCCCvik..',
        '..kCCCCCCCCik...',
        '..kCckCCCkcik...',
        '...kCCCvCCik....',
        '...kCCCCCCik....',
        '....kCCCCik.....',
        '.....kiiik......',
        '......kkk.......',
        '................',
        '................'],
    'choir_pearl': [
        '................',
        '................',
        '.....kkkkkk.....',
        '....kpPPPppk....',
        '...kpPwPPpppk...',
        '...kpPPPpppqk...',
        '..kppPPpppppqk..',
        '..kpppppppppqk..',
        '..kpppppppqqqk..',
        '..kqppppppqqqk..',
        '...kqqpppqqqk...',
        '...kqqqqqqqqk...',
        '....kqqqqqqk....',
        '.....kkkkkk.....',
        '................',
        '................'],
    'abyssal_pearl': [
        '................',
        '................',
        '.....kkkkkk.....',
        '....kUUUUuuk....',
        '...kUxwUUuuuk...',
        '...kUxUUuuuuk...',
        '..kUUUUuuuuuuk..',
        '..kUUuuuuuuuuk..',
        '..kuuuuuuuuuRk..',
        '..kuuuuuuuuRRk..',
        '...kuuuuuuRRk...',
        '...kuuuuuuuuk...',
        '....kuuuuuuk....',
        '.....kkkkkk.....',
        '................',
        '................'],
    'undertow': [
        '.............kk.',
        '............kRk.',
        '...........kRrk.',
        '..........kRrk..',
        '.........kRrk...',
        '........kRrk....',
        '.......kRrk.....',
        '..kk..kRrk......',
        '..kbkkRrk.......',
        '...kbYrk........',
        '...kkbbk........',
        '..kllkbbk.......',
        '.kllk.kbk.......',
        'kllk...kk.......',
        'klk.............',
        'kk..............'],
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


if __name__ == '__main__':
    blocks()
    items()
    print('drowned textures written')
