"""Isometric previews of saved structure templates (.nbt), drawn from the file the game places.

Bars, chains, fences, walls and other thin blocks are drawn thin and see-through, slabs half height, so a preview reads
the way the structure does in game. These are renders of the template, not in-game screenshots.

python3 view.py name [--cut z] [--rot n] [--size px]
"""
import argparse
import hashlib
import math
import os

import nbtlib
from PIL import Image, ImageDraw

from kit import TEMPLATES

BASE = {
    'polished_blackstone_bricks': (52, 45, 54), 'cracked_polished_blackstone_bricks': (46, 40, 48), 'polished_blackstone': (58, 52, 62),
    'chiseled_polished_blackstone': (64, 58, 70), 'gilded_blackstone': (92, 70, 40), 'blackstone': (44, 38, 46),
    'polished_basalt': (92, 92, 98), 'basalt': (80, 80, 86), 'deepslate_tiles': (58, 58, 62), 'cracked_deepslate_tiles': (52, 52, 56),
    'deepslate_bricks': (72, 72, 76), 'cobbled_deepslate': (78, 78, 82), 'polished_deepslate': (74, 74, 78), 'deepslate': (82, 82, 88),
    'tuff': (110, 112, 104), 'tuff_bricks': (104, 106, 98), 'stone': (124, 124, 126), 'andesite': (136, 136, 138), 'gravel': (128, 122, 120),
    'iron_bars': (150, 156, 166), 'chain': (70, 76, 90), 'bone_block': (226, 220, 196), 'cobweb': (225, 225, 232),
    'shroomlight': (250, 160, 70), 'soul_lantern': (90, 220, 230), 'lantern': (245, 180, 80), 'end_rod': (245, 240, 225),
    'soul_campfire': (80, 200, 220), 'campfire': (240, 130, 40), 'dark_oak_planks': (70, 46, 24), 'dark_oak_log': (60, 46, 30),
    'stripped_dark_oak_log': (98, 76, 50), 'dark_oak_slab': (70, 46, 24), 'dark_oak_fence': (70, 46, 24), 'hay_block': (196, 168, 52),
    'mud': (62, 58, 62), 'packed_mud': (142, 106, 79), 'mud_bricks': (137, 103, 79), 'coarse_dirt': (119, 85, 59), 'rooted_dirt': (144, 103, 76),
    'dirt': (134, 96, 67), 'moss_block': (89, 109, 45), 'moss_carpet': (89, 109, 45), 'short_grass': (96, 128, 60), 'grass_block': (95, 140, 60),
    'white_wool': (232, 232, 230), 'turtle_egg': (220, 222, 190), 'skeleton_skull': (205, 205, 200), 'dead_bush': (130, 92, 50),
    'chest': (165, 112, 40), 'barrel': (134, 100, 58), 'lectern': (150, 110, 60), 'ladder': (130, 100, 58), 'red_mushroom_block': (190, 50, 45),
    'brown_mushroom_block': (149, 111, 81), 'mushroom_stem': (203, 196, 185), 'nether_wart_block': (120, 10, 12), 'crimson_roots': (130, 10, 40),
    'magma_block': (150, 66, 30), 'water': (40, 90, 170), 'lava': (255, 120, 20), 'sculk': (14, 34, 42), 'sculk_vein': (20, 70, 80),
    'stripped_spruce_log': (115, 89, 52), 'spruce_log': (58, 40, 22), 'spruce_planks': (114, 84, 48), 'spruce_fence': (114, 84, 48),
    'white_concrete_powder': (220, 220, 214), 'calcite': (223, 224, 220), 'dripstone_block': (134, 108, 92), 'pointed_dripstone': (150, 120, 100),
    'red_wool': (150, 38, 34), 'brown_wool': (114, 71, 40), 'black_wool': (24, 24, 28), 'light_gray_wool': (142, 142, 134),
    'gray_wool': (62, 68, 71), 'cartography_table': (100, 80, 60), 'crafting_table': (130, 95, 60), 'smoker': (90, 90, 95),
    'anvil': (70, 70, 74), 'cauldron': (60, 60, 64), 'glow_lichen': (112, 131, 119), 'vine': (40, 95, 30), 'hanging_roots': (160, 115, 90),
    'mangrove_roots': (74, 59, 38), 'muddy_mangrove_roots': (70, 59, 45), 'frogspawn': (100, 90, 120), 'slime_block': (110, 190, 90),
    'honeycomb_block': (229, 148, 29), 'honey_block': (240, 170, 40), 'bee_nest': (200, 160, 80), 'amethyst_block': (133, 97, 191),
    'crying_obsidian': (60, 10, 120), 'obsidian': (20, 18, 30), 'iron_block': (210, 210, 214), 'oxidized_copper': (82, 160, 136),
    'weathered_copper': (108, 154, 110), 'exposed_copper': (161, 125, 103), 'copper_block': (192, 107, 79), 'lightning_rod': (200, 110, 80),
    'astral_bricks': (66, 62, 98), 'chiseled_astral': (84, 80, 120), 'astral_shale': (38, 34, 58), 'starmoss': (40, 120, 124),
    'lumen_crystal': (140, 215, 250), 'rift_glass': (150, 100, 220), 'void_tendril': (90, 44, 130), 'void_cyst': (140, 80, 196),
    'abyss_gate': (60, 30, 90), 'rift_engine': (210, 170, 70), 'updraft_vent': (60, 150, 150), 'eclipse_altar': (200, 150, 60),
    'starbloom': (150, 220, 250), 'astral_ore': (60, 58, 86), 'oxidized_cut_copper': (82, 160, 136), 'weathered_cut_copper': (108, 154, 110),
    'chiseled_copper': (180, 110, 80), 'purple_stained_glass': (127, 63, 178), 'light_blue_stained_glass': (102, 153, 216),
    'redstone_lamp': (180, 110, 60), 'chitin_block': (96, 72, 46), 'ochre_froglight': (250, 220, 150), 'honey_block': (240, 170, 40), 'mycelium': (111, 99, 105), 'podzol': (91, 63, 24), 'target': (220, 200, 180), 'tinted_glass': (44, 38, 52), 'black_stained_glass': (30, 30, 34),
}
THIN = ('bars', 'chain', 'fence', '_wall', 'rod', 'lantern', 'ladder', 'cobweb', 'dead_bush', 'short_grass', 'roots', 'skull',
        'vine', 'lichen', 'campfire', 'torch', 'flower', 'mushroom', 'egg', 'pointed', 'sapling')
HALF = ('_slab',)
FLAT = ('carpet', 'pressure_plate', 'rail', 'snow')


def base_color(name):
    key = name.split(':')[1]
    if key in BASE:
        return BASE[key]
    for k, c in BASE.items():
        if key.startswith(k) or key.endswith(k):
            return c
    for word, c in (('blackstone', (52, 45, 54)), ('deepslate', (70, 70, 74)), ('dark_oak', (70, 46, 24)), ('spruce', (100, 74, 44)),
                    ('mud', (120, 92, 70)), ('tuff', (106, 108, 100)), ('stone', (122, 122, 124)), ('bone', (226, 220, 196)),
                    ('wool', (200, 200, 200)), ('copper', (150, 120, 90))):
        if word in key:
            return c
    d = hashlib.md5(key.encode()).digest()
    return (70 + d[0] % 140, 70 + d[1] % 140, 70 + d[2] % 140)


def load(name):
    path = name if name.endswith('.nbt') else os.path.join(TEMPLATES, f'{name}.nbt')
    t = nbtlib.load(path)
    pal = [str(p['Name']) for p in t['palette']]
    return {tuple(int(v) for v in b['pos']): pal[int(b['state'])] for b in t['blocks']}, [int(v) for v in t['size']]


def render(name, out, cut=None, cutx=None, rot=0, size=1000, title=None, ground=None, bg=((24, 26, 34), (58, 62, 78)), ymax=None, hide=()):
    blocks, (W, H, L) = load(name)
    vis = {}
    for (x, y, z), n in blocks.items():
        if n in ('minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void'):
            continue
        for _ in range(rot % 4):
            x, z = L - 1 - z, x
        if cut is not None and z > cut:
            continue
        if cutx is not None and x > cutx:
            continue
        if ymax is not None and y > ymax:
            continue
        if any(k in n for k in hide):
            continue
        vis[(x, y, z)] = n
    if rot % 2:
        W, L = L, W
    if ground is not None:
        # surround the template with terrain up to the ground line, as it sits in the world (cells the template sets win)
        allp = set(blocks)
        for x in range(-4, W + 4):
            for z in range(-4, L + 4):
                if cut is not None and z > cut:
                    continue
                for y in range(max(0, ground - 3), ground + 1):
                    if (x, y, z) not in allp:
                        vis[(x, y, z)] = 'minecraft:grass_block' if y == ground else 'minecraft:dirt'
    xs = [p[0] for p in vis]; ys = [p[1] for p in vis]; zs = [p[2] for p in vis]
    x0, y0, z0 = min(xs), min(ys), min(zs)
    W, H, L = max(xs) - x0 + 1, max(ys) - y0 + 1, max(zs) - z0 + 1
    vis = {(x - x0, y - y0, z - z0): n for (x, y, z), n in vis.items()}
    opaque = {p for p, n in vis.items() if not any(t in n for t in THIN + HALF + FLAT) and 'glass' not in n and 'leaves' not in n}
    scale = size / (W + L) / 0.95
    sx, sy = scale * math.cos(math.radians(30)), scale * 0.5
    ox, oy = L * sx + 10, 20 + H * scale
    proj = lambda x, y, z: (ox + (x - z) * sx, oy + (x + z) * sy - y * scale)
    Wp, Hp = int(ox + W * sx + 10), int(oy + (W + L) * sy + 20)
    img = Image.new('RGB', (Wp, Hp))
    d = ImageDraw.Draw(img)
    for yy in range(Hp):
        f = yy / Hp
        d.line([(0, yy), (Wp, yy)], fill=tuple(int(bg[0][i] * (1 - f) + bg[1][i] * f) for i in range(3)))
    for (x, y, z) in sorted(vis, key=lambda p: (p[0] + p[2] + p[1], p[1])):
        n = vis[(x, y, z)]
        c = base_color(n)
        sh = lambda f: tuple(min(255, int(v * f)) for v in c)
        glow = any(k in n for k in ('shroomlight', 'lantern', 'campfire', 'end_rod', 'froglight', 'glowstone', 'lamp', 'lumen', 'rift_glass', 'crying'))
        if any(t in n for t in THIN):
            cx, cz = x + 0.5, z + 0.5
            if 'bars' in n:
                for t in (0.15, 0.5, 0.85):
                    d.line([proj(x + t, y, z + 1 - t), proj(x + t, y + 1, z + 1 - t)], fill=sh(0.95), width=max(1, int(scale / 7)))
                d.line([proj(x, y + 1, z + 1), proj(x + 1, y + 1, z)], fill=sh(0.75), width=max(1, int(scale / 8)))
            elif 'chain' in n:
                d.line([proj(cx, y, cz), proj(cx, y + 1, cz)], fill=sh(1.0), width=max(1, int(scale / 4)))
            elif 'cobweb' in n:
                d.line([proj(x, y, z + 0.5), proj(x + 1, y + 1, z + 0.5)], fill=sh(0.9), width=1)
                d.line([proj(x, y + 1, z + 0.5), proj(x + 1, y, z + 0.5)], fill=sh(0.9), width=1)
            elif 'fence' in n or '_wall' in n or 'rod' in n or 'ladder' in n:
                wdt = 0.5 if '_wall' in n else 0.25
                poly(d, proj, cx - wdt / 2, y, cz - wdt / 2, wdt, 1.0 if 'rod' not in n else 1.0, wdt, c, glow)
            else:
                poly(d, proj, x + 0.25, y, z + 0.25, 0.5, 0.5, 0.5, c, glow)
            continue
        hgt = 0.5 if any(t in n for t in HALF) else (0.12 if any(t in n for t in FLAT) else 1.0)
        yb = y + (0.5 if 'type=top' in n else 0)
        faces = []
        if (x, y + 1, z) not in opaque or hgt < 1:
            faces.append(([proj(x, y + hgt, z), proj(x + 1, y + hgt, z), proj(x + 1, y + hgt, z + 1), proj(x, y + hgt, z + 1)], 1.08))
        if (x + 1, y, z) not in opaque:
            faces.append(([proj(x + 1, y, z), proj(x + 1, y + hgt, z), proj(x + 1, y + hgt, z + 1), proj(x + 1, y, z + 1)], 0.8))
        if (x, y, z + 1) not in opaque:
            faces.append(([proj(x, y, z + 1), proj(x + 1, y, z + 1), proj(x + 1, y + hgt, z + 1), proj(x, y + hgt, z + 1)], 0.64))
        for pts, f in faces:
            col = c if glow else sh(f)
            d.polygon(pts, fill=col, outline=sh(f * 0.82) if scale > 7 and not glow else None)
    if title:
        d.text((12, 8), title, fill=(255, 220, 160))
    img.save(out)
    print('rendered', out, img.size)
    return img


def poly(d, proj, x, y, z, w, hgt, l, c, glow):
    sh = lambda f: tuple(min(255, int(v * f)) for v in c)
    d.polygon([proj(x, y + hgt, z), proj(x + w, y + hgt, z), proj(x + w, y + hgt, z + l), proj(x, y + hgt, z + l)], fill=c if glow else sh(1.05))
    d.polygon([proj(x + w, y, z), proj(x + w, y + hgt, z), proj(x + w, y + hgt, z + l), proj(x + w, y, z + l)], fill=c if glow else sh(0.8))
    d.polygon([proj(x, y, z + l), proj(x + w, y, z + l), proj(x + w, y + hgt, z + l), proj(x, y + hgt, z + l)], fill=c if glow else sh(0.64))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('name')
    ap.add_argument('--out')
    ap.add_argument('--cut', type=int)
    ap.add_argument('--cutx', type=int)
    ap.add_argument('--rot', type=int, default=0)
    ap.add_argument('--size', type=int, default=1000)
    ap.add_argument('--ground', type=int)
    ap.add_argument('--ymax', type=int)
    ap.add_argument('--hide', nargs='*', default=[])
    a = ap.parse_args()
    render(a.name, a.out or f'{a.name}.png', a.cut, a.cutx, a.rot, a.size, ground=a.ground, ymax=a.ymax, hide=a.hide)
