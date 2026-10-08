"""Renders the whole mod for the preview gallery: Wardens, guards, citadels, portals, realm dioramas, realm structures and arenas.

python3 render_gallery.py OUT_DIR [section ...]     sections: bosses guards citadels portals structures dioramas arenas waygates
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image

import render_models as rm
import render_structure as rs

S = '../src/main/resources/data/aurelia/structures/'
TEX = '../src/main/resources/assets/aurelia/textures/block/'
rs.AUR.update({'root_heart': (210, 50, 60), 'warden_altar': (235, 205, 120), 'spore_planter': (150, 200, 90), 'storm_pylon': (120, 220, 255),
               'soul_socket': (90, 210, 220), 'bramble_seal': (90, 120, 40), 'storm_seal': (180, 220, 255), 'ash_seal': (120, 60, 40),
               'spore_vent': (150, 190, 80), 'gale_plate': (200, 240, 255), 'ember_vent': (255, 120, 40), 'verdant_ore': (90, 160, 90),
               'stormglass_ore': (140, 200, 230), 'emberheart_ore': (200, 90, 50)})

REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']
BG = {'grove': ((18, 36, 22), (64, 104, 56)), 'skyreach': ((60, 100, 150), (170, 205, 235)), 'hollow': ((14, 8, 18), (70, 28, 30)),
      'drowned': ((8, 26, 36), (24, 66, 76)), 'pale': ((44, 50, 62), (130, 140, 156)), 'scarlet': ((54, 18, 14), (150, 70, 40)),
      'clockwork': ((14, 6, 30), (74, 32, 118)), 'mycelial': ((22, 8, 28), (96, 40, 96))}
BOSS = {'grove': 'mossback_titan', 'skyreach': 'tempest_roc', 'hollow': 'hollow_king', 'drowned': 'vorath', 'pale': 'white_silence',
        'scarlet': 'kharzul', 'clockwork': 'vexor', 'mycelial': 'bloom_mother'}
GUARDS = {'grove': ['bramble_sentinel', 'sporecap', 'rootstalker'], 'skyreach': ['calcite_sentinel', 'storm_wisp', 'gale_talon'],
          'hollow': ['ashbound_knight', 'soul_jailer', 'cinder_hound'], 'drowned': ['coralclad_juggernaut', 'tidecaller', 'razorclaw'],
          'pale': ['rimeguard', 'hushwraith', 'rimefang'], 'scarlet': ['sandglass_sentinel', 'sunseer', 'glasswing_scarab'],
          'clockwork': ['hour_warden', 'secondhand', 'gearskitter'], 'mycelial': ['husk_guard', 'spore_drifter', 'root_grub']}
CITADEL = {'grove': 'rootbound_citadel', 'skyreach': 'stormwatch_citadel', 'hollow': 'ashen_citadel', 'drowned': 'tidewrack_citadel',
           'pale': 'rimefast_citadel', 'scarlet': 'sunscar_citadel', 'clockwork': 'paradox_keep', 'mycelial': 'spore_cathedral'}
STRUCTS = {'grove': ['grove_pillar_0', 'grove_pillar_2', 'grove_ruin_0', 'grove_ruin_3', 'grove_outpost_0', 'grove_outpost_1'],
           'skyreach': ['sky_island_castle_0', 'sky_island_large_0', 'sky_island_medium_1', 'sky_island_small_0', 'sky_outpost_0', 'sky_outpost_1'],
           'hollow': ['hollow_ziggurat_0', 'hollow_arch_0', 'hollow_stalactite_0', 'hollow_stalactite_3', 'hollow_outpost_0', 'hollow_outpost_1'],
           'drowned': ['drowned_spire_0', 'drowned_wreck_0', 'drowned_bones_0', 'drowned_outpost_0', 'drowned_outpost_1', 'drowned_wreck_1'],
           'pale': ['pale_colossus_0', 'pale_colossus_1', 'pale_spire_0', 'pale_spire_2', 'pale_outpost_0', 'pale_outpost_1'],
           'scarlet': ['scarlet_monolith_0', 'scarlet_monolith_2', 'scarlet_bones_0', 'scarlet_bones_1', 'scarlet_outpost_0', 'scarlet_outpost_1'],
           'clockwork': ['rift_fragment_0', 'rift_fragment_1', 'rift_spire_0', 'rift_bridge_0', 'rift_outpost_0', 'rift_outpost_1'],
           'mycelial': ['fungal_tower_0', 'fungal_tower_1', 'fungal_tower_2', 'root_arch_0', 'spore_shrine_0', 'root_arch_1']}


def save(img, path, q=84):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path, 'WEBP', quality=q, method=5)
    print('  ', path)


def realm_of(key):
    for r, gs in GUARDS.items():
        if key in gs:
            return r
    return next(r for r, b in BOSS.items() if b == key)


# ------------------------------------------------------------------------------------------------ models
def bosses(out):
    for realm, key in BOSS.items():
        parts, tex, glow = rm.build(key)
        sc = None
        row = []
        for yaw, pitch in [(-35, 14), (150, 18)]:
            im, s = rm.render(parts, tex, glow, yaw, pitch, size=620, bg=BG[realm], scale=sc)
            sc = s if sc is None else sc
            row.append(im)
        img = Image.new('RGB', (1240, 620))
        img.paste(row[0], (0, 0))
        img.paste(row[1], (620, 0))
        save(img, f'{out}/bosses/{key}.webp')


def guards(out):
    for realm, keys in GUARDS.items():
        for key in keys:
            parts, tex, glow = rm.build(key)
            im, _ = rm.render(parts, tex, glow, -35, 14, size=440, bg=BG[realm])
            save(im, f'{out}/guards/{key}.webp')


# ------------------------------------------------------------------------------------------------ citadels and portals
CUTS = {'rootbound_citadel': dict(cut=30), 'stormwatch_citadel': dict(cut=28), 'ashen_citadel': dict(cut=34),
        'tidewrack_citadel': dict(cut=30, hide=['water', 'kelp', 'seagrass']), 'rimefast_citadel': dict(rot=2, cutx=40),
        'sunscar_citadel': dict(cut=32), 'paradox_keep': dict(cutx=48), 'spore_cathedral': dict(cutx=48)}
EXT = {'tidewrack_citadel': dict(sea=22), 'rimefast_citadel': dict(rot=2)}


def citadels(out):
    import json
    off = json.load(open(os.path.join(os.path.dirname(__file__), '_cores', 'offsets.json')))
    for realm, name in CITADEL.items():
        a = rs.render(S + name + '.nbt', None, size=1100, bg=BG[realm], **EXT.get(name, {}))
        save(a, f'{out}/citadels/{name}_ext.webp')
        cut = {k: v + off.get(name, 0) if k in ('cut', 'cutx') else v for k, v in CUTS[name].items()}   # the keep sits inside its fortress
        b = rs.render(S + name + '.nbt', None, size=1100, bg=BG[realm], **cut)
        save(b, f'{out}/citadels/{name}_cut.webp')


RITE = ('waygate', 'spore_planter', 'storm_pylon', 'soul_socket', 'tide_bell', 'hush_stone', 'sun_mirror', 'sun_lens', 'sunwell', 'clock_dial',
        'master_clock', 'spore_valve', 'lectern')


def portal_box(name):
    """A box round the portal and its rite blocks, low enough to look down into the room, cut flush on the near (+x, +z) sides."""
    blocks, _, _ = rs.load(S + name + '.nbt')
    way = next(k for k, v in blocks.items() if v == 'aurelia:waygate')
    pts = [k for k, v in blocks.items() if v.split(':')[1] in RITE and abs(k[1] - way[1]) <= 8 and abs(k[0] - way[0]) <= 26 and abs(k[2] - way[2]) <= 26]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    z0, z1 = min(p[2] for p in pts), max(p[2] for p in pts)
    y0 = min(p[1] for p in pts)
    top = way[1] + 2 if name == 'tidewrack_citadel' else max(p[1] for p in pts) + 4     # the bell vault is a dome under rock
    return (x0 - 5, y0 - 2, z0 - 5, x1 + 2, top, z1 + 2)


def portals(out):
    for realm, name in CITADEL.items():
        img = rs.render(S + name + '.nbt', None, size=900, bg=BG[realm], box=portal_box(name))
        save(img, f'{out}/portals/{name}_rite.webp')


def waygates(out):
    tiles = []
    for realm in REALMS:
        for state in ('off', 'on'):
            t = Image.open(f'{TEX}waygate_{realm}_{state}_side.png').convert('RGBA').resize((128, 128), Image.NEAREST)
            tiles.append(t)
    img = Image.new('RGBA', (8 * 272, 128), (0, 0, 0, 0))
    for i, realm in enumerate(REALMS):
        img.paste(tiles[2 * i], (i * 272, 0))
        img.paste(tiles[2 * i + 1], (i * 272 + 136, 0))
    os.makedirs(f'{out}/portals', exist_ok=True)
    img.save(f'{out}/portals/waygates.png')
    print('  ', f'{out}/portals/waygates.png')


def lieutenants(out):
    from lieutenants import LIEUTENANTS
    for lt in LIEUTENANTS:
        bg = BG.get(lt['realm'], LAST_BG)
        parts, tex, glow = rm.build(lt['id'])
        sc = None
        row = []
        for yaw, pitch in [(-35, 14), (150, 18)]:
            im, s = rm.render(parts, tex, glow, yaw, pitch, size=520, bg=bg, scale=sc)
            sc = s if sc is None else sc
            row.append(im)
        img = Image.new('RGB', (1040, 520))
        img.paste(row[0], (0, 0))
        img.paste(row[1], (520, 0))
        save(img, f'{out}/lieutenants/{lt["id"]}.webp')


def lairs(out):
    from lieutenants import LIEUTENANTS
    for lt in LIEUTENANTS:
        img = rs.render(S + f'lair_{lt["id"]}.nbt', None, size=760, bg=BG.get(lt['realm'], LAST_BG))
        save(img, f'{out}/lairs/lair_{lt["id"]}.webp')


def structures(out):
    for realm, names in STRUCTS.items():
        for n in names:
            img = rs.render(S + n + '.nbt', None, size=520, bg=BG[realm])
            save(img, f'{out}/structures/{n}.webp')


# ------------------------------------------------------------------------------------------------ dioramas
def vnoise(seed, W, L, cell):
    rnd = np.random.default_rng(seed)
    gw, gl = W // cell + 3, L // cell + 3
    g = rnd.random((gw, gl))
    xs, zs = np.arange(W) / cell, np.arange(L) / cell
    xi, zi = xs.astype(int), zs.astype(int)
    xf, zf = xs - xi, zs - zi
    xf, zf = xf * xf * (3 - 2 * xf), zf * zf * (3 - 2 * zf)
    a = g[xi][:, zi]
    b = g[xi + 1][:, zi]
    c = g[xi][:, zi + 1]
    d = g[xi + 1][:, zi + 1]
    return (a * (1 - xf)[:, None] + b * xf[:, None]) * (1 - zf)[None, :] + (c * (1 - xf)[:, None] + d * xf[:, None]) * zf[None, :]


class Scene:
    def __init__(self):
        self.b = {}
        self.ents = []

    def set(self, x, y, z, name):
        self.b[(int(x), int(y), int(z))] = name if ':' in name else 'minecraft:' + name

    def get(self, x, y, z):
        return self.b.get((x, y, z))

    def place(self, name, x0, y0, z0, rot=0, keep_air=True):
        blocks, ents, _ = rs.load(S + name + '.nbt', rot)
        for (x, y, z), v in blocks.items():
            if v in ('minecraft:air', 'minecraft:cave_air', 'minecraft:structure_void'):
                if keep_air:
                    self.b.pop((x0 + x, y0 + y, z0 + z), None)
                continue
            self.b[(x0 + x, y0 + y, z0 + z)] = v

    def column(self, x, z, top, pick):
        for y in range(0, top + 1):
            self.set(x, y, z, pick(y, top))


def terrain(sc, W, L, height, surface, under='stone', sub='dirt', subdepth=3):
    for x in range(W):
        for z in range(L):
            h = int(height[x, z])
            for y in range(max(0, h - 7), h + 1):
                sc.set(x, y, z, surface(x, z, h) if y == h else (sub if y > h - subdepth else under))


def tree(sc, x, y, z, log, leaves, h, r, rnd):
    for k in range(h):
        sc.set(x, y + k, z, log)
    for dx in range(-r, r + 1):
        for dz in range(-r, r + 1):
            for dy in range(-1, r):
                if dx * dx + dz * dz + (dy * 1.6) ** 2 <= r * r + rnd.random() * 2:
                    if sc.get(x + dx, y + h + dy, z + dz) is None:
                        sc.set(x + dx, y + h + dy, z + dz, leaves)


def spruce(sc, x, y, z, h, rnd):
    for k in range(h):
        sc.set(x, y + k, z, 'spruce_log')
    for k in range(2, h + 2):
        r = max(0, int((h + 2 - k) * 0.45))
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if abs(dx) + abs(dz) <= r + (k % 2) and (dx or dz or k >= h):
                    if sc.get(x + dx, y + k, z + dz) is None:
                        sc.set(x + dx, y + k, z + dz, 'spruce_leaves')
    sc.set(x, y + h + 2, z, 'spruce_leaves')


def ground_at(height, x, z):
    return int(height[min(max(x, 0), height.shape[0] - 1), min(max(z, 0), height.shape[1] - 1)])


def diorama(realm):
    rnd = random.Random(hash(realm) % 1000)
    sc = Scene()
    W = L = 120
    if realm == 'grove':
        n = vnoise(11, W, L, 30) * 0.7 + vnoise(12, W, L, 10) * 0.3
        h = 8 + n * 26
        terrain(sc, W, L, h, lambda x, z, y: 'moss_block' if (x * 7 + z * 3) % 5 == 0 else 'grass_block')
        sc.place('grove_pillar_0', 6, ground_at(h, 16, 16) - 3, 6)
        sc.place('grove_ruin_0', 70, ground_at(h, 78, 20) - 1, 12)
        sc.place('grove_outpost_0', 48, ground_at(h, 64, 72) - 1, 54)
        for _ in range(55):
            x, z = rnd.randrange(4, W - 4), rnd.randrange(4, L - 4)
            if not any(sc.get(x, y, z) for y in range(int(h[x, z]) + 1, int(h[x, z]) + 6)):
                if rnd.random() < 0.2:
                    y = int(h[x, z]) + 1
                    for k in range(7):
                        sc.set(x, y + k, z, 'mushroom_stem')
                    for dx in range(-3, 4):
                        for dz in range(-3, 4):
                            if dx * dx + dz * dz <= 10:
                                sc.set(x + dx, y + 7, z + dz, 'red_mushroom_block')
                else:
                    tree(sc, x, int(h[x, z]) + 1, z, 'jungle_log', 'jungle_leaves', rnd.randint(5, 10), rnd.randint(2, 4), rnd)
        return sc, {}
    if realm == 'skyreach':
        for name, x, y, z in [('sky_island_castle_0', 30, 46, 30), ('sky_island_large_0', 0, 18, 70), ('sky_island_medium_1', 80, 30, 4),
                              ('sky_island_small_0', 4, 64, 8), ('sky_outpost_0', 82, 6, 76), ('sky_island_small_2', 60, 76, 92)]:
            sc.place(name, x, y, z, keep_air=False)
        return sc, {}
    if realm == 'hollow':
        n = vnoise(21, W, L, 24)
        h = 8 + n * 10
        terrain(sc, W, L, h, lambda x, z, y: 'basalt' if (x + z) % 4 else ('soul_soil' if (x * z) % 7 == 0 else 'blackstone'), under='blackstone', sub='blackstone')
        for x in range(W):
            for z in range(L):
                if h[x, z] < 11:
                    for y in range(int(h[x, z]) + 1, 12):
                        sc.set(x, y, z, 'lava')
        sc.place('hollow_ziggurat_0', 8, 10, 8, keep_air=False)
        sc.place('hollow_arch_0', 64, 8, 20, keep_air=False)
        sc.place('hollow_outpost_0', 60, ground_at(h, 76, 76), 60)
        for name, x, z in [('hollow_stalactite_0', 20, 70), ('hollow_stalactite_3', 96, 4), ('hollow_stalactite_1', 4, 96)]:
            blocks, _, (w, hh, l) = rs.load(S + name + '.nbt')
            sc.place(name, x, 76 - hh, z, keep_air=False)
        return sc, {}
    if realm == 'drowned':
        n = vnoise(31, W, L, 26) * 0.75 + vnoise(32, W, L, 9) * 0.25
        h = 2 + n * 30
        SEA = 24
        terrain(sc, W, L, h, lambda x, z, y: ('sand' if (x + z) % 3 else 'gravel') if y < SEA else 'grass_block')
        sc.place('drowned_spire_0', 20, ground_at(h, 30, 30) - 2, 20, keep_air=False)
        sc.place('drowned_wreck_0', 56, SEA - 8, 44, keep_air=False)
        sc.place('drowned_outpost_0', 8, ground_at(h, 20, 96) - 2, 84, keep_air=False)
        sc.place('drowned_bones_0', 64, ground_at(h, 70, 20), 4, keep_air=False)
        for x in range(W):
            for z in range(L):
                for y in range(int(h[x, z]) + 1, SEA + 1):
                    if (x, y, z) not in sc.b:
                        sc.set(x, y, z, 'water')
                if rnd.random() < 0.05 and h[x, z] < SEA - 3:
                    for k in range(rnd.randint(2, 7)):
                        if sc.get(x, int(h[x, z]) + 1 + k, z) == 'minecraft:water':
                            sc.set(x, int(h[x, z]) + 1 + k, z, 'kelp_plant')
        return sc, {}
    if realm == 'pale':
        n = vnoise(41, W, L, 28) * 0.7 + vnoise(42, W, L, 8) * 0.3
        h = 8 + n * 22
        terrain(sc, W, L, h, lambda x, z, y: 'packed_ice' if (vnoise(43, W, L, 14)[x, z] > 0.78) else 'snow_block', sub='snow_block')
        sc.place('pale_colossus_0', 14, ground_at(h, 30, 30) - 3, 14)
        sc.place('pale_spire_0', 80, ground_at(h, 90, 20) - 2, 8)
        sc.place('pale_outpost_0', 60, ground_at(h, 72, 76) - 1, 62)
        for _ in range(60):
            x, z = rnd.randrange(3, W - 3), rnd.randrange(3, L - 3)
            y = int(h[x, z]) + 1
            if any(sc.get(x, y + k, z) for k in range(4)):
                continue
            if rnd.random() < 0.25:
                for k in range(rnd.randint(6, 16)):
                    sc.set(x, y + k, z, 'packed_ice')
            else:
                spruce(sc, x, y, z, rnd.randint(6, 11), rnd)
        return sc, {}
    if realm == 'scarlet':
        n = vnoise(51, W, L, 22)
        mesa = vnoise(52, W, L, 34)
        h = 8 + n * 7
        h = np.where(mesa > 0.66, 30 + n * 4, h)
        BANDS = ['terracotta', 'orange_terracotta', 'red_terracotta', 'yellow_terracotta', 'terracotta', 'white_terracotta', 'red_terracotta']
        for x in range(W):
            for z in range(L):
                top = int(h[x, z])
                for y in range(max(0, top - 24), top + 1):
                    if top > 20 and y > 12:
                        sc.set(x, y, z, BANDS[y % len(BANDS)] if y < top else 'red_sand')
                    else:
                        sc.set(x, y, z, 'red_sand' if y >= top - 1 else 'red_sandstone')
        sc.place('scarlet_monolith_0', 10, ground_at(h, 16, 60) - 2, 50, keep_air=False)
        sc.place('scarlet_bones_0', 54, ground_at(h, 64, 70) - 2, 58, keep_air=False)
        sc.place('scarlet_outpost_0', 12, ground_at(h, 26, 98) - 1, 86)
        for _ in range(40):
            x, z = rnd.randrange(2, W - 2), rnd.randrange(2, L - 2)
            y = int(h[x, z]) + 1
            if sc.get(x, y, z) is None:
                sc.set(x, y, z, 'dead_bush' if rnd.random() < 0.6 else 'cactus')
        return sc, {}
    if realm == 'clockwork':
        for name, x, y, z in [('rift_spire_0', 44, 20, 8), ('rift_fragment_0', 2, 40, 60), ('rift_fragment_2', 84, 54, 40),
                              ('rift_bridge_0', 30, 34, 66), ('rift_outpost_0', 76, 6, 80), ('rift_fragment_1', 0, 70, 4)]:
            sc.place(name, x, y, z, keep_air=False)
        return sc, {}
    if realm == 'mycelial':
        n = vnoise(61, W, L, 26) * 0.7 + vnoise(62, W, L, 9) * 0.3
        h = 6 + n * 14
        terrain(sc, W, L, h, lambda x, z, y: 'mycelium' if (x * 3 + z) % 5 else ('magenta_terracotta' if (x + z) % 2 else 'white_terracotta'),
                sub='dirt')
        for x in range(W):
            for z in range(L):
                if h[x, z] < 9:
                    for y in range(int(h[x, z]) + 1, 10):
                        sc.set(x, y, z, 'water')
        sc.place('fungal_tower_0', 4, ground_at(h, 20, 20) - 1, 4, keep_air=False)
        sc.place('fungal_tower_2', 74, ground_at(h, 90, 30) - 1, 14, keep_air=False)
        sc.place('fungal_tower_1', 20, ground_at(h, 36, 90) - 1, 76, keep_air=False)
        sc.place('root_arch_0', 44, ground_at(h, 66, 56) - 1, 50, keep_air=False)
        sc.place('spore_shrine_0', 80, ground_at(h, 94, 90) - 1, 76)
        for _ in range(40):
            x, z = rnd.randrange(3, W - 3), rnd.randrange(3, L - 3)
            y = int(h[x, z]) + 1
            if sc.get(x, y, z) is None and y > 10:
                hh = rnd.randint(3, 9)
                for k in range(hh):
                    sc.set(x, y + k, z, 'mushroom_stem')
                r = 2 + hh // 3
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        if dx * dx + dz * dz <= r * r:
                            sc.set(x + dx, y + hh, z + dz, 'magenta_wool' if (dx + dz) % 4 else 'pearlescent_froglight')
        return sc, {}


def dioramas(out):
    for realm in REALMS:
        sc, opt = diorama(realm)
        blocks = {k: v for k, v in sc.b.items() if 'cut' not in opt or k[2] <= opt['cut']}
        img = rs.draw(blocks, [], 0, 0, 0, None, size=1200, bg=BG[realm], dots=False)
        save(img, f'{out}/realms/{realm}_diorama.webp')


# ------------------------------------------------------------------------------------------------ arenas (the boss on its pad)
PAD = {'grove': ('mossy_stone_bricks', 'stone_bricks', 'shroomlight'), 'skyreach': ('quartz_bricks', 'quartz_block', 'sea_lantern'),
       'hollow': ('polished_blackstone_bricks', 'blackstone', 'soul_lantern'), 'drowned': ('prismarine_bricks', 'dark_prismarine', 'sea_lantern'),
       'pale': ('calcite', 'packed_ice', 'soul_lantern'), 'scarlet': ('cut_red_sandstone', 'red_sandstone', 'ochre_froglight'),
       'clockwork': ('polished_deepslate', 'deepslate_tiles', 'pearlescent_froglight'), 'mycelial': ('mushroom_stem', 'bone_block', 'pearlescent_froglight')}


def arena(realm):
    sc = Scene()
    C, Y = 30, 12                      # the standing level; the pad surface is at Y - 1
    pad, found, light = PAD[realm]
    R = 12
    surround = {'grove': 'grass_block', 'hollow': 'basalt', 'pale': 'snow_block', 'scarlet': 'red_sand', 'mycelial': 'mycelium'}.get(realm)
    rnd = random.Random(7)
    for dx in range(-29, 30):
        for dz in range(-29, 30):
            d2 = dx * dx + dz * dz
            if d2 <= R * R:
                for dy in range(2, 7):
                    sc.set(C + dx, Y - dy, C + dz, found)
                sc.set(C + dx, Y - 1, C + dz, pad)
            elif surround and d2 <= 29 * 29:
                sc.set(C + dx, Y - 2 + (1 if rnd.random() < 0.2 else 0), C + dz, surround)
    for (cx, cz) in [(-8, -8), (8, -8), (-8, 8), (8, 8)]:
        for dy in range(4):
            sc.set(C + cx, Y + dy, C + cz, pad)
        sc.set(C + cx, Y + 4, C + cz, light)
    sc.set(C, Y, C, 'aurelia:warden_altar')
    sc.set(C, Y, C + 9, 'aurelia:waygate')
    if realm == 'grove':
        for (dx, dz) in [(9, -3), (-8, -5), (2, 10)]:
            sc.set(C + dx, Y, C + dz, 'aurelia:root_heart')
            sc.set(C + dx, Y + 1, C + dz, 'aurelia:root_heart')
    elif realm == 'drowned':
        for dx in range(-26, 27):
            for dz in range(-26, 27):
                d2 = dx * dx + dz * dz
                if R * R < d2 <= 26 * 26:
                    for dy in range(-8, -1):
                        sc.set(C + dx, Y + dy, C + dz, 'water')
        for (bx, bz) in [(11, 0), (-11, 0), (0, -11)]:
            sc.set(C + bx, Y, C + bz, 'aurelia:tide_bell')
    elif realm == 'pale':
        for (fx, fz) in [(9, 0), (-9, 0), (0, -9), (-6, 7)]:
            sc.set(C + fx, Y, C + fz, 'campfire')
    elif realm == 'scarlet':
        for (px, pz) in [(7, 0), (-7, 0), (0, -8), (4, 6)]:
            for dx in range(-1, 2):
                for dz in range(-1, 2):
                    for dy in range(6):
                        sc.set(C + px + dx, Y + dy, C + pz + dz, 'chiseled_red_sandstone' if dy == 5 else 'cut_red_sandstone')
    elif realm == 'clockwork':
        for dx in range(-14, 15):
            for dz in range(-14, 15):
                d = math.hypot(dx, dz)
                if 12 < d <= 14:
                    for dy in range(-6, 0):
                        sc.set(C + dx, Y + dy, C + dz, 'polished_blackstone_bricks')
                elif 10.5 < d <= 11.5:
                    sc.set(C + dx, Y - 1, C + dz, 'polished_blackstone')
        for k in range(12):
            a = k * math.pi / 6
            sc.set(C + round(math.cos(a) * 11), Y - 1, C + round(math.sin(a) * 11), 'gold_block')
            sc.set(C + round(math.cos(a) * 13), Y, C + round(math.sin(a) * 13), 'candle')
        for r in range(2, 10):
            sc.set(C + r, Y - 1, C, 'gold_block')
        for r in range(2, 7):
            sc.set(C, Y - 1, C - r, 'gold_block')
        for (dx, dz) in [(9, 3), (-9, 3), (0, -9)]:
            sc.set(C + dx, Y, C + dz, 'aurelia:clock_dial')
        for dy in range(4):
            sc.set(C, Y + dy, C - 12, 'gold_block' if dy == 3 else 'polished_blackstone_bricks')
        sc.set(C, Y + 4, C - 12, 'aurelia:master_clock')
    elif realm == 'mycelial':
        for k in range(10):
            a = k * math.pi / 5
            for r in range(3, 12, 2):
                sc.set(C + round(math.cos(a) * r), Y - 1, C + round(math.sin(a) * r), 'pearlescent_froglight')
        for (vx, vz) in [(10, 2), (-10, 2), (0, -11)]:
            sc.set(C + vx, Y, C + vz, 'aurelia:spore_valve')
        for k in range(8):
            a = k * math.pi / 4 + 0.4
            x, z = C + round(math.cos(a) * 12), C + round(math.sin(a) * 12)
            sc.set(x, Y, z, 'mushroom_stem')
            sc.set(x, Y + 1, z, 'mushroom_stem')
            sc.set(x, Y + 2, z, 'purple_wool')
    return sc


BOSS_SIZE = {'mossback_titan': 640, 'tempest_roc': 640, 'hollow_king': 660, 'vorath': 700, 'white_silence': 640, 'kharzul': 660,
             'vexor': 700, 'bloom_mother': 700}


def arenas(out):
    for realm in REALMS:
        sc = arena(realm)
        pad = rs.draw(sc.b, [], 0, 0, 0, None, size=760, bg=BG[realm], dots=False)
        key = BOSS[realm]
        parts, tex, glow = rm.build(key)
        im, _ = rm.render(parts, tex, glow, -40, 10, size=560, alpha=True)
        im = im.crop(im.getbbox())
        im.thumbnail((470, 560))
        W, H = 1280, max(pad.height, 600)
        card = Image.new('RGB', (W, H))
        top, bot = BG[realm]
        for y in range(H):
            f = y / H
            card.paste(tuple(int(top[i] * (1 - f) + bot[i] * f) for i in range(3)), (0, y, W, y + 1))
        card.paste(pad, (0, (H - pad.height) // 2))
        card = card.convert('RGBA')
        card.alpha_composite(im, (W - im.width - 40, (H - im.height) // 2))
        save(card.convert('RGB'), f'{out}/arenas/{realm}_arena.webp')


# ------------------------------------------------------------------------------------------------ the finale
LAST_REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']


def last_realm_scene(with_pad=True):
    """The Last Realm hub as ArenaBuilder.last() assembles it: the core round the pad, an island at the end of every bridge."""
    sc = Scene()
    C, F = 56, 40
    sc.place('last_core', 0, 0, 0, keep_air=False)
    for k, realm in enumerate(LAST_REALMS):
        a = math.radians(k * 45)
        sc.place(f'last_island_{realm}', C + round(66 * math.cos(a)) - 17, 0, C + round(66 * math.sin(a)) - 17, keep_air=False)
    if with_pad:
        for dx in range(-12, 13):
            for dz in range(-12, 13):
                if dx * dx + dz * dz <= 144:
                    for dy in range(2, 7):
                        sc.set(C + dx, F - dy, C + dz, 'blackstone')
                    sc.set(C + dx, F - 1, C + dz, 'smooth_sandstone' if (dx * dx + dz * dz) % 7 else 'chiseled_sandstone')
        for (cx, cz) in [(-8, -8), (8, -8), (-8, 8), (8, 8)]:
            for dy in range(4):
                sc.set(C + cx, F + dy, C + cz, 'smooth_sandstone')
            sc.set(C + cx, F + 4, C + cz, 'pearlescent_froglight')
        sc.set(C, F, C, 'aurelia:warden_altar')
        sc.set(C, F, C + 9, 'aurelia:waygate')
    return sc


rs.AUR.update({'relic_pedestal': (44, 38, 52), 'realm_node': (200, 150, 255), 'unmaking_anchor': (30, 20, 40)})
LAST_BG = ((6, 4, 14), (44, 24, 76))


def finale(out):
    import relics
    for key, name, boss, realm, fn in relics.RELICS:
        im = relics.render_relic(fn(), size=460, bg=BG[realm], on_pedestal=realm, yaw=-28, pitch=14)
        save(im, f'{out}/finale/relic_{key}.webp')
    im = relics.render_relic(relics.hand_of_genesis(), size=560, bg=LAST_BG, yaw=-24, pitch=10)
    save(im, f'{out}/finale/hand_of_genesis.webp')
    # the Unmaker, front and back
    parts, tex, glow = rm.build('unmaker')
    sc = None
    row = []
    for yaw, pitch in [(-25, 8), (155, 12)]:
        im, s = rm.render(parts, tex, glow, yaw, pitch, size=700, bg=LAST_BG, scale=sc)
        sc = s if sc is None else sc
        row.append(im)
    img = Image.new('RGB', (1400, 700))
    img.paste(row[0], (0, 0))
    img.paste(row[1], (700, 0))
    save(img, f'{out}/finale/unmaker.webp')
    # the Last Realm, whole, and the Unmaker over its arena
    scn = last_realm_scene()
    hub = rs.draw(scn.b, [], 0, 0, 0, None, size=1500, bg=LAST_BG, dots=False)
    save(hub, f'{out}/finale/last_realm.webp')
    boss, _ = rm.render(parts, tex, glow, -40, 6, size=900, alpha=True)
    boss = boss.crop(boss.getbbox())
    boss.thumbnail((470, 470))
    card = hub.convert('RGBA')
    card.alpha_composite(boss, ((card.width - boss.width) // 2, max(0, int(card.height * 0.53) - boss.height)))
    save(card.convert('RGB'), f'{out}/finale/unmaker_over_the_last_realm.webp')
    # the arena close up: core and pad only, the eight nodes on the rim
    core = Scene()
    for k, v in scn.b.items():
        if (k[0] - 56) ** 2 + (k[2] - 56) ** 2 <= 34 ** 2:
            core.b[k] = v
    save(rs.draw(core.b, [], 0, 0, 0, None, size=1100, bg=LAST_BG, dots=False), f'{out}/finale/last_arena.webp')
    # the Convergence Gate
    gate = S + 'convergence_gate.nbt'
    save(rs.render(gate, None, size=1100, bg=LAST_BG), f'{out}/finale/gate_ext.webp')
    save(rs.render(gate, None, size=1100, bg=LAST_BG, rot=1), f'{out}/finale/gate_side.webp')
    save(rs.render(gate, None, size=900, bg=LAST_BG, box=(20, 14, 18, 60, 34, 44)), f'{out}/finale/gate_rite.webp')
    for realm in LAST_REALMS:
        save(rs.render(S + f'last_island_{realm}.nbt', None, size=520, bg=LAST_BG), f'{out}/finale/island_{realm}.webp')


def gear(out):
    """Each realm's arsenal: the armor worn (front and back), the weapon sprite, the creature, and an icon strip of the four armor
    pieces, three tools, ore, two materials and food. Also the whole Tenfold Seal sheet for the finale chapter."""
    import arsenal_art as art
    import arsenal_sheet
    import gen_armor as ga
    from kit_data import ARSENAL, KIT, PIECES
    from pixelart import upscale
    I = '../src/main/resources/assets/aurelia/textures/'
    for realm in REALMS:
        k, a = KIT[realm], ARSENAL[realm]
        f, b = ga.render_preview(realm, size=620, bg=BG[realm])
        img = Image.new('RGB', (1240, 620))
        img.paste(f, (0, 0))
        img.paste(b, (620, 0))
        save(img, f'{out}/gear/{realm}_armor.webp')
        w = Image.new('RGBA', (512, 512), BG[realm][0] + (255,))
        w.alpha_composite(upscale(art.WEAPONS[realm][1]().render(), 8))
        save(w.convert('RGB'), f'{out}/gear/{realm}_weapon.webp')
        p, t, g = rm.build(k['critter'])
        im, _ = rm.render(p, t, g, -35, 16, size=520, bg=BG[realm])
        save(im, f'{out}/gear/{realm}_critter.webp')
        icons = [art.ICONS[x](realm).render() for x in PIECES] + [fn(realm).render() for fn in (art.pickaxe, art.axe, art.shovel)]
        icons += [arsenal_sheet.iso_block(art.ore(a['ore']).render(outline=False, halo=False), 16)]
        icons += [art.MATERIALS[m]().render() for m in dict.fromkeys([a['metal'], a['special']])]
        icons += [Image.open(I + f'item/{k["food"]}.png').convert('RGBA').resize((32, 32), Image.NEAREST)]
        strip = Image.new('RGBA', (len(icons) * 108 + 12, 120), BG[realm][0] + (255,))
        for n, ic in enumerate(icons):
            strip.alpha_composite(upscale(ic, 3), (12 + n * 108, 12))
        save(strip.convert('RGB'), f'{out}/gear/{realm}_items.webp')
    arsenal_sheet.main(f'{out}/finale/arsenals.jpg')
    Image.open(f'{out}/finale/arsenals.jpg').save(f'{out}/finale/arsenals.webp', quality=90)
    os.remove(f'{out}/finale/arsenals.jpg')


if __name__ == '__main__':
    out = sys.argv[1]
    secs = sys.argv[2:] or ['bosses', 'guards', 'citadels', 'portals', 'waygates', 'structures', 'dioramas', 'arenas', 'finale', 'gear', 'lieutenants', 'lairs']
    for s in secs:
        print(s)
        globals()[s](out)
