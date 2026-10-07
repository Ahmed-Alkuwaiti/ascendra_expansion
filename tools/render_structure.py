"""Isometric preview of a structure template (.nbt). Painter's algorithm over exposed faces, flat colours per block.

python3 render_structure.py out.png structure.nbt [--cut z] [--cutx x] [--rot n] [--hide water]
"""
import argparse
import hashlib
import math

import nbtlib
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    'water': (40, 90, 170), 'lava': (255, 120, 20), 'sand': (219, 207, 163), 'red_sand': (190, 102, 33), 'gravel': (130, 124, 122),
    'stone': (125, 125, 125), 'andesite': (136, 136, 136), 'prismarine': (99, 156, 151), 'prismarine_bricks': (99, 171, 158),
    'dark_prismarine': (51, 91, 75), 'sea_lantern': (210, 230, 225), 'grass_block': (95, 159, 53), 'moss_block': (89, 109, 45),
    'dirt': (134, 96, 67), 'kelp_plant': (60, 110, 40), 'kelp': (60, 110, 40), 'seagrass': (50, 120, 40), 'dark_oak_planks': (66, 43, 20),
    'dark_oak_log': (60, 46, 26), 'stripped_dark_oak_log': (96, 76, 49), 'white_wool': (233, 236, 236), 'ladder': (125, 97, 55),
    'light_blue_stained_glass': (102, 153, 216), 'iron_bars': (110, 110, 110), 'chest': (160, 110, 40), 'lectern': (150, 110, 60),
    'snow_block': (240, 250, 250), 'snow': (240, 250, 250), 'packed_ice': (141, 180, 250), 'ice': (145, 183, 253), 'blue_ice': (116, 167, 253),
    'powder_snow': (248, 253, 253), 'stone_bricks': (122, 121, 122), 'mossy_stone_bricks': (115, 121, 105), 'cracked_stone_bricks': (118, 117, 118),
    'deepslate_tiles': (54, 54, 55), 'deepslate_bricks': (70, 70, 71), 'polished_deepslate': (72, 72, 73), 'cobbled_deepslate': (77, 77, 80),
    'spruce_planks': (114, 84, 48), 'spruce_log': (58, 37, 16), 'stripped_spruce_log': (115, 89, 52), 'calcite': (223, 224, 220),
    'white_stained_glass': (240, 240, 240), 'sculk': (12, 30, 36), 'sculk_vein': (8, 70, 80), 'soul_lantern': (90, 210, 220),
    'lantern': (230, 170, 80), 'campfire': (230, 120, 40), 'soul_campfire': (80, 200, 220), 'red_sandstone': (186, 99, 29),
    'cut_red_sandstone': (189, 101, 31), 'chiseled_red_sandstone': (183, 96, 27), 'smooth_red_sandstone': (181, 98, 31),
    'terracotta': (152, 94, 67), 'orange_terracotta': (161, 83, 37), 'red_terracotta': (143, 61, 46), 'yellow_terracotta': (186, 133, 35),
    'gold_block': (246, 208, 61), 'red_stained_glass': (153, 51, 51), 'orange_stained_glass': (216, 127, 51),
    'bone_block': (229, 225, 207), 'red_wool': (160, 39, 34), 'orange_wool': (240, 118, 19), 'yellow_wool': (248, 197, 39),
    'light_gray_wool': (142, 142, 134), 'bricks': (150, 97, 83), 'conduit': (160, 140, 110), 'spruce_leaves': (56, 86, 58), 'oak_leaves': (60, 120, 40), 'ochre_froglight': (250, 236, 180), 'shroomlight': (240, 146, 70), 'glowstone': (250, 210, 130),
}
AUR = {'tide_bell': (220, 180, 70), 'coral_seal': (226, 86, 110), 'waygate': (255, 220, 120), 'brine_grate': (40, 110, 110),
       'hush_stone': (200, 230, 255), 'rime_seal': (170, 214, 240), 'frost_rune': (120, 220, 255), 'sunwell': (255, 214, 90),
       'sun_mirror': (240, 245, 255), 'sun_lens': (220, 60, 60), 'sun_seal': (230, 140, 60), 'sunflare_plate': (255, 240, 200)}
ground_block = 'minecraft:grass_block'
SKIP = {'minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void'}
THIN = ('carpet', 'pressure_plate', 'rail', 'snow', 'vein', 'torch', 'candle')


def color(name):
    ns, key = name.split(':')
    if ns == 'aurelia':
        return AUR.get(key, (255, 0, 255))
    if key in COLORS:
        return COLORS[key]
    for k, c in COLORS.items():
        if key.endswith(k) or key.startswith(k):
            return c
    if 'coral' in key:
        return {'tube': (50, 90, 210), 'brain': (205, 90, 160), 'bubble': (160, 30, 160), 'fire': (165, 35, 45), 'horn': (215, 200, 70)}.get(key.split('_')[0], (200, 80, 120))
    h = hashlib.md5(key.encode()).digest()
    return (60 + h[0] % 160, 60 + h[1] % 160, 60 + h[2] % 160)


def render(path, out, cut=None, cutx=None, rot=0, hide=(), title=None, scale=None, bg=((28, 30, 40), (60, 66, 84)), size=1100, sea=None, ground=None):
    t = nbtlib.load(path)
    W, H, L = [int(v) for v in t['size']]
    pal = [str(p['Name']) for p in t['palette']]
    blocks = {}
    for b in t['blocks']:
        name = pal[int(b['state'])]
        if name in SKIP or any(h in name for h in hide):
            continue
        x, y, z = (int(v) for v in b['pos'])
        for _ in range(rot % 4):
            x, z = L - 1 - z, x
        if cut is not None and z > cut:
            continue
        if cutx is not None and x > cutx:
            continue
        blocks[(x, y, z)] = name
    if rot % 2:
        W, L = L, W
    # optional context: open sea up to a water line, or flat ground at a level, wherever the template leaves the world alone
    if sea is not None or ground is not None:
        cols = {}
        for (x, y, z) in blocks:
            cols.setdefault((x, z), []).append(y)
        for x in range(W):
            for z in range(L):
                if cut is not None and z > cut or cutx is not None and x > cutx:
                    continue
                if sea is not None and (x, sea, z) not in blocks:
                    blocks[(x, sea, z)] = 'minecraft:water'
                if ground is not None and (x, z) not in cols:
                    blocks[(x, ground, z)] = ground_block
    ents = []
    for e in t['entities']:
        x, y, z = (float(v) for v in e['pos'])
        for _ in range(rot % 4):
            x, z = L - z, x
        ents.append((x, y, z, str(e['nbt']['id']).split(':')[1]))
    opaque = {k for k, v in blocks.items() if not any(s in v for s in ('glass', 'water', 'leaves', 'bars', 'fence', 'wall', 'lantern', 'ladder')) and not any(s in v for s in THIN)}
    if scale is None:
        scale = size / (W + L) / 1.05
    sx, sy = scale * math.cos(math.radians(30)), scale * 0.5
    ox = L * sx + 20
    oy = 40 + H * scale

    def proj(x, y, z):
        return (ox + (x - z) * sx, oy + (x + z) * sy - y * scale)

    Wp, Hp = int(ox + W * sx + 20), int(oy + (W + L) * sy + 30)
    img = Image.new('RGB', (Wp, Hp))
    d = ImageDraw.Draw(img)
    for yy in range(Hp):
        f = yy / Hp
        d.line([(0, yy), (Wp, yy)], fill=tuple(int(bg[0][i] * (1 - f) + bg[1][i] * f) for i in range(3)))
    order = sorted(blocks, key=lambda p: (p[0] + p[2] + p[1], p[1]))
    for (x, y, z) in order:
        name = blocks[(x, y, z)]
        c = color(name)
        thin = any(s in name for s in THIN)
        h = 0.15 if thin else 1.0
        faces = []
        if (x, y + 1, z) not in opaque:
            faces.append(([proj(x, y + h, z), proj(x + 1, y + h, z), proj(x + 1, y + h, z + 1), proj(x, y + h, z + 1)], 1.0))
        if (x + 1, y, z) not in opaque:
            faces.append(([proj(x + 1, y, z), proj(x + 1, y + h, z), proj(x + 1, y + h, z + 1), proj(x + 1, y, z + 1)], 0.78))
        if (x, y, z + 1) not in opaque:
            faces.append(([proj(x, y, z + 1), proj(x + 1, y, z + 1), proj(x + 1, y + h, z + 1), proj(x, y + h, z + 1)], 0.62))
        for poly, shade in faces:
            col = tuple(int(v * shade) for v in c)
            if 'water' in name:
                col = tuple(int(v * 0.8) for v in col)
            d.polygon(poly, fill=col, outline=tuple(int(v * 0.8) for v in col) if scale > 6 else None)
    ecol = {'coralclad_juggernaut': (255, 255, 255), 'rimeguard': (255, 255, 255), 'sandglass_sentinel': (255, 255, 255),
            'tidecaller': (255, 90, 220), 'hushwraith': (255, 90, 220), 'sunseer': (255, 90, 220),
            'razorclaw': (255, 150, 40), 'rimefang': (255, 150, 40), 'glasswing_scarab': (255, 150, 40)}
    for (x, y, z, eid) in ents:
        px, py = proj(x, y + 1, z)
        r = max(4, scale * 0.7)
        d.ellipse([px - r, py - r, px + r, py + r], fill=ecol.get(eid, (90, 230, 255)), outline=(0, 0, 0), width=2)
    if title:
        try:
            f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
        except OSError:
            f = ImageFont.load_default()
        d.text((14, 10), title, fill=(255, 220, 160), font=f)
    img.save(out)
    print('wrote', out, f'{len(blocks)} blocks drawn, scale {scale:.1f}')
    return img


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('nbt')
    ap.add_argument('--cut', type=int)
    ap.add_argument('--cutx', type=int)
    ap.add_argument('--rot', type=int, default=0)
    ap.add_argument('--hide', nargs='*', default=[])
    ap.add_argument('--size', type=int, default=1100)
    ap.add_argument('--sea', type=int)
    ap.add_argument('--ground', type=int)
    ap.add_argument('--ground-block', default='minecraft:grass_block')
    a = ap.parse_args()
    ground_block = a.ground_block
    render(a.nbt, a.out, a.cut, a.cutx, a.rot, a.hide, size=a.size, sea=a.sea, ground=a.ground)
