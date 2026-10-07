"""Isometric preview of a structure template (.nbt). Painter's algorithm over exposed faces, flat colours per block.

python3 render_structure.py out.png structure.nbt [--cut z] [--cutx x] [--rot n] [--hide water]
"""
import argparse
import hashlib
import math

import nbtlib
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    'cracked_stone_bricks': (118, 117, 118), 'chiseled_stone_bricks': (120, 119, 120), 'polished_andesite': (132, 135, 134), 'granite': (149, 103, 85),
    'cracked_deepslate_tiles': (52, 52, 53), 'cracked_polished_blackstone_bricks': (44, 37, 43), 'chiseled_polished_blackstone': (53, 48, 56),
    'smooth_red_sandstone': (181, 98, 31), 'cut_sandstone': (217, 206, 159), 'chiseled_sandstone': (216, 203, 155), 'smooth_sandstone': (223, 214, 170),
    'coarse_dirt': (119, 85, 59), 'rooted_dirt': (144, 103, 76), 'packed_mud': (142, 106, 79), 'blue_ice': (116, 167, 253),
    'vine': (40, 95, 30), 'glow_lichen': (112, 160, 130), 'moss_carpet': (89, 109, 45), 'hanging_roots': (160, 115, 90), 'cobweb': (220, 220, 225),
    'barrel': (134, 100, 58), 'bookshelf': (117, 94, 59), 'composter': (115, 75, 40), 'crafting_table': (130, 95, 60), 'cartography_table': (100, 80, 60),
    'smithing_table': (60, 60, 70), 'blast_furnace': (90, 90, 95), 'lodestone': (140, 140, 145), 'loom': (150, 120, 90), 'decorated_pot': (150, 85, 60),
    'skeleton_skull': (200, 200, 200), 'chain': (60, 64, 76), 'snow': (240, 250, 250), 'dead_bush': (120, 85, 40), 'poppy': (200, 30, 30),
    'dandelion': (240, 220, 40), 'allium': (180, 110, 230), 'blue_orchid': (40, 160, 230), 'oxeye_daisy': (230, 230, 220), 'cornflower': (70, 100, 220),
    'azure_bluet': (220, 230, 240), 'lily_of_the_valley': (240, 240, 240), 'sea_pickle': (110, 140, 50), 'white_candle': (230, 230, 230),
    'red_candle': (180, 40, 40), 'potted_fern': (110, 70, 50), 'potted_red_mushroom': (150, 60, 50), 'potted_cornflower': (110, 70, 50),
    'potted_wither_rose': (60, 50, 40), 'potted_crimson_fungus': (140, 40, 50),
    'basalt': (80, 81, 86), 'polished_basalt': (99, 98, 100), 'soul_soil': (75, 57, 46), 'soul_sand': (81, 62, 50), 'jungle_log': (85, 67, 25),
    'jungle_leaves': (48, 120, 30), 'cactus': (85, 127, 43), 'quartz_bricks': (234, 229, 221), 'quartz_block': (236, 230, 223), 'purple_wool': (122, 42, 173),
    'candle': (230, 210, 160), 'mushroom_stem_': (203, 196, 185), 'magma_block': (142, 63, 31), 'crimson_stem': (92, 25, 29), 'netherrack': (97, 38, 38),
    'deepslate': (80, 80, 84), 'tuff': (108, 109, 102), 'cracked_deepslate_bricks': (64, 64, 65), 'chiseled_deepslate': (54, 54, 54),
    'blackstone': (42, 36, 41), 'polished_blackstone_bricks': (48, 42, 48), 'polished_blackstone': (53, 48, 56), 'crying_obsidian': (60, 10, 120),
    'obsidian': (20, 18, 30), 'amethyst_block': (133, 97, 191), 'amethyst_cluster': (160, 120, 220), 'purple_stained_glass': (127, 63, 178),
    'purple_terracotta': (118, 70, 86), 'pearlescent_froglight': (245, 225, 240), 'waxed_cut_copper': (191, 106, 80), 'waxed_copper_block': (192, 107, 79),
    'purple_carpet': (121, 42, 172), 'bell': (250, 210, 80), 'lightning_rod': (200, 110, 80), 'chain': (60, 64, 76),
    'mycelium': (111, 99, 105), 'podzol': (91, 63, 24), 'mushroom_stem': (203, 196, 185), 'mangrove_roots': (74, 59, 38),
    'muddy_mangrove_roots': (70, 59, 45), 'magenta_terracotta': (149, 88, 108), 'magenta_concrete': (169, 48, 159), 'magenta_wool': (189, 68, 179),
    'magenta_stained_glass': (178, 76, 216), 'pink_stained_glass': (242, 127, 165), 'pink_terracotta': (161, 78, 78), 'white_concrete': (207, 213, 214),
    'smooth_quartz': (235, 229, 222), 'polished_diorite': (192, 193, 194), 'diorite': (188, 182, 183), 'chiseled_quartz_block': (231, 226, 218),
    'quartz': (235, 229, 222), 'magenta_glazed_terracotta': (208, 100, 191), 'magenta_carpet': (189, 68, 179), 'spore_blossom': (206, 96, 158),
    'mossy_cobblestone': (110, 118, 94), 'shroomlight': (240, 146, 70), 'end_rod': (240, 240, 230), 'purple_candle': (120, 50, 170),
    'magenta_candle': (190, 70, 180), 'crimson_roots': (126, 8, 41), 'red_mushroom_block': (200, 46, 45), 'brown_mushroom_block': (149, 111, 81),
    'gilded_blackstone': (56, 43, 38), 'cobblestone': (127, 127, 127), 'purpur_block': (169, 125, 169), 'purpur_pillar': (171, 129, 171),
    'copper_block': (192, 107, 79), 'cut_copper': (191, 106, 80), 'mud_bricks': (137, 103, 79), 'glow_lichen': (112, 131, 119),
    'warped_wart_block': (22, 119, 121), 'nether_wart_block': (114, 2, 2), 'pink_concrete': (213, 101, 142), 'white_terracotta': (209, 178, 161),
    'pink_wool': (237, 141, 172), 'verdant_froglight': (229, 244, 228), 'ochre_froglight_': (250, 236, 180), 'black_concrete': (8, 10, 15),
    'stripped_mangrove_log': (119, 54, 47), 'mangrove_log': (84, 66, 36), 'mud': (60, 57, 60), 'sculk_catalyst': (15, 32, 38),
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
       'sun_mirror': (240, 245, 255), 'sun_lens': (220, 60, 60), 'sun_seal': (230, 140, 60), 'sunflare_plate': (255, 240, 200),
       'clock_dial': (250, 215, 110), 'master_clock': (255, 235, 140), 'spore_valve': (120, 200, 120), 'paradox_seal': (150, 70, 220),
       'root_seal': (110, 70, 40), 'time_snare': (170, 120, 230), 'root_snare': (100, 70, 50), 'chronite_block': (130, 90, 210), 'bloomspore_block': (220, 90, 190)}
ground_block = 'minecraft:grass_block'
SKIP = {'minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void', 'minecraft:glow_lichen'}   # lichen is a flat film in game
THIN = ('carpet', 'pressure_plate', 'rail', 'snow', 'vein', 'torch', 'candle')


DYES = {'white': (233, 236, 236), 'orange': (240, 118, 19), 'magenta': (189, 68, 179), 'light_blue': (58, 175, 217), 'yellow': (248, 197, 39),
        'lime': (112, 185, 25), 'pink': (237, 141, 172), 'gray': (62, 68, 71), 'light_gray': (142, 142, 134), 'cyan': (21, 137, 145),
        'purple': (121, 42, 172), 'blue': (53, 57, 157), 'brown': (114, 71, 40), 'green': (84, 109, 27), 'red': (160, 39, 34), 'black': (20, 21, 25)}


def color(name):
    ns, key = name.split(':')
    if key.endswith('_banner'):
        return DYES.get(key.replace('_wall_banner', '').replace('_banner', ''), (200, 200, 200))
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


def load(path, rot=0):
    """A template as ({(x, y, z): name}, [(x, y, z, id)], (W, H, L)), turned rot quarter turns."""
    t = nbtlib.load(path)
    W, H, L = [int(v) for v in t['size']]
    pal = [str(p['Name']) for p in t['palette']]
    blocks = {}
    for b in t['blocks']:
        x, y, z = (int(v) for v in b['pos'])
        for _ in range(rot % 4):
            x, z = L - 1 - z, x
        blocks[(x, y, z)] = pal[int(b['state'])]
    ents = []
    for e in t['entities']:
        x, y, z = (float(v) for v in e['pos'])
        for _ in range(rot % 4):
            x, z = L - z, x
        ents.append((x, y, z, str(e['nbt']['id']).split(':')[1]))
    return blocks, ents, ((L, H, W) if rot % 2 else (W, H, L))


def render(path, out, cut=None, cutx=None, rot=0, hide=(), title=None, scale=None, bg=((28, 30, 40), (60, 66, 84)), size=1100, sea=None, ground=None, box=None):
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
        if box is not None and not (box[0] <= x <= box[3] and box[1] <= y <= box[4] and box[2] <= z <= box[5]):
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
        if (cut is not None and z > cut + 1) or (cutx is not None and x > cutx + 1):
            continue
        if box is not None and not (box[0] <= x <= box[3] + 1 and box[2] <= z <= box[5] + 1 and box[1] <= y <= box[4]):
            continue
        ents.append((x, y, z, str(e['nbt']['id']).split(':')[1]))
    return draw(blocks, ents, W, H, L, out, title=title, scale=scale, bg=bg, size=size)


def draw(blocks, ents, W, H, L, out, title=None, scale=None, bg=((28, 30, 40), (60, 66, 84)), size=1100, dots=True):
    """Draws a block dict {(x, y, z): 'ns:name'} isometrically; ents are (x, y, z, id) guard markers."""
    if blocks:                                      # frame the picture on what is actually drawn
        x0 = min(k[0] for k in blocks); y0 = min(k[1] for k in blocks); z0 = min(k[2] for k in blocks)
        W = max(k[0] for k in blocks) - x0 + 1; H = max(k[1] for k in blocks) - y0 + 1; L = max(k[2] for k in blocks) - z0 + 1
        blocks = {(x - x0, y - y0, z - z0): v for (x, y, z), v in blocks.items()}
        ents = [(x - x0, y - y0, z - z0, e) for (x, y, z, e) in ents]
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
    for (x, y, z, eid) in (ents if dots else ()):
        px, py = proj(x, y + 1, z)
        r = max(4, scale * 0.7)
        d.ellipse([px - r, py - r, px + r, py + r], fill=ecol.get(eid, (90, 230, 255)), outline=(0, 0, 0), width=2)
    if title:
        try:
            f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
        except OSError:
            f = ImageFont.load_default()
        d.text((14, 10), title, fill=(255, 220, 160), font=f)
    if out:
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
