"""Landmarks for the realms' new biomes: one structure each, found only in its own biome.

  bloomwild         the Petal Shrine          a cherry-wood pavilion over a glowing heart, petals everywhere
  mossveil_thicket  the Sunken Idol           a giant mossy stone head half swallowed by the ground, green eyes burning
  cloud_meadows     the Windmill Isle         a floating meadow with a white windmill
  stormfront        the Lightning Spire       a black rock hung with a copper conductor, scorched and bone-strewn
  soulfire_wastes   the Soul Obelisk          a blackstone needle of soul lanterns over skull piles
  ember_deeps       the Hollow Forge          a basalt forge with a lava channel, anvils and a chimney
  kelp_forest       the Sunken Lighthouse     a broken prismarine lighthouse on the sea floor
  coral_graveyard   the Leviathan's Rest      giant ribs and a skull on the sea floor
  frozen_spires     the Frozen Knight         a giant knight sealed in ice, sword planted
  whisper_taiga     the Hunter's Lodge        a spruce lodge hung with antlers, a frozen pond
  glass_dunes       the Sunglass Spire        a cluster of red glass crystals capped in gold
  bone_flats        the Fallen Titan          a giant skeleton lying half buried
  gearfields        the Fallen Gear           a giant copper gear sunk into a floating rock, chains and pistons
  stopped_hour      the Stopped Clock         a great clock face on an amethyst outcrop, floating
  glowcap_hollows   the Glowcap Ring          a fairy ring of giant glowing mushrooms round a moss pool
  rootmaw           the Root Maw              roots twisted into a fanged arch

Each has a chest of its realm's lair loot. Writes the templates, and each one's structure, structure set, template pool and biome tag.
"""
import json
import math
import os
import random

import gen_citadels2
import paths
from gen_act3_citadels import AIR, Grid

D = paths.RES + '/data/aurelia'
WG = D + '/worldgen'
AX = {'axis': 'y'}
BONE = ('minecraft:bone_block', AX)
CHAIN = ('minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})


def h(x, y, z, salt=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (salt * 2654435761)) % 1000 / 1000.0


class B:
    def __init__(self, W, H, L, seed):
        self.g = Grid(W, H, L)
        self.W, self.H, self.L = W, H, L
        self.rnd = random.Random(seed)

    def put(self, x, y, z, b, props=None, over=True):
        x, y, z = int(round(x)), int(round(y)), int(round(z))
        if not (0 <= x < self.W and 0 <= y < self.H and 0 <= z < self.L):
            return
        if not over and self.g.get(x, y, z) is not None:
            return
        if isinstance(b, tuple):
            b, props = b
        self.g.set(x, y, z, b, props)

    def ball(self, cx, cy, cz, rx, pick, ry=None, rz=None, over=True):
        ry, rz = ry or rx, rz or rx
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1:
                        b = pick(x, y, z) if callable(pick) else pick
                        if b:
                            self.put(x, y, z, b, over=over)

    def tube(self, pts, radius, pick, step=0.4):
        segs = list(zip(pts, pts[1:]))
        lens = [math.dist(a, b) for a, b in segs]
        total = sum(lens) or 1
        done = 0.0
        for (a, b), ln in zip(segs, lens):
            n = max(1, int(ln / step))
            for i in range(n):
                t = i / n
                p = [a[j] + (b[j] - a[j]) * t for j in range(3)]
                s = (done + ln * t) / total
                self.ball(p[0], p[1], p[2], radius(s), (lambda x, y, z, s=s: pick(x, y, z, s)) if callable(pick) else pick)
            done += ln

    def column(self, cx, cz, r, y0, y1, pick, taper=0.0):
        for y in range(int(y0), int(y1)):
            rr = r * (1 - taper * (y - y0) / max(1, y1 - y0))
            for x in range(int(cx - rr) - 1, int(cx + rr) + 2):
                for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    if math.hypot(x - cx, z - cz) <= rr:
                        self.put(x, y, z, pick(x, y, z) if callable(pick) else pick)

    def box(self, x0, y0, z0, x1, y1, z1, pick, hollow=False):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    if hollow and x0 < x < x1 and z0 < z < z1 and y0 < y < y1:
                        self.put(x, y, z, AIR)
                        continue
                    self.put(x, y, z, pick(x, y, z) if callable(pick) else pick)

    def island(self, cx, cz, top, r, surface, under, depth=1.4):
        """A floating rock with its own ground (for the sky realms)."""
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                d = math.hypot(x - cx, z - cz)
                if d > r:
                    continue
                dep = int((r - d) * depth + h(x, 0, z) * 3)
                for y in range(top - dep, top + 1):
                    self.put(x, y, z, surface if y == top else under)

    def pad(self, cx, cz, top, r, surface, under, depth=6):
        """A base that runs down into the ground, so nothing floats on a slope."""
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                if math.hypot(x - cx, z - cz) <= r:
                    for y in range(max(0, top - depth), top + 1):
                        self.put(x, y, z, surface if y == top else under, over=False)

    def chest(self, x, y, z, realm, facing='north'):
        from gen_act3_citadels import chest
        chest(self.g, int(x), int(y), int(z), f'aurelia:chests/lair_{realm}', facing)


def lantern(soul=True, hanging=False):
    return ('minecraft:soul_lantern' if soul else 'minecraft:lantern', {'hanging': str(hanging).lower(), 'waterlogged': 'false'})


def fire(soul=False):
    return ('minecraft:soul_campfire' if soul else 'minecraft:campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})


# ================================================================================================ the landmarks (G is the ground level inside each template)
G = 8


def petal_shrine():
    b = B(31, 30, 31, 1)
    C = 15
    b.pad(C, C, G - 1, 12, 'minecraft:moss_block', 'minecraft:stone')
    b.box(C - 6, G - 1, C - 6, C + 6, G - 1, C + 6, lambda x, y, z: 'minecraft:cherry_planks' if (x + z) % 2 else 'minecraft:stripped_cherry_log')
    for (x, z) in [(C - 6, C - 6), (C + 6, C - 6), (C - 6, C + 6), (C + 6, C + 6)]:
        b.column(x, z, 0.6, G, G + 9, ('minecraft:cherry_log', AX))
    for k in range(3):                                                  # three tiers of curved roof
        r = 8 - k * 2.4
        y = G + 9 + k * 3
        for x in range(C - 9, C + 10):
            for z in range(C - 9, C + 10):
                d = max(abs(x - C), abs(z - C))
                if d <= r:
                    lift = 1 if d > r - 1.2 else 0
                    b.put(x, y + lift, z, 'minecraft:cherry_planks' if d < r - 1 else ('minecraft:pink_terracotta' if lift else 'minecraft:cherry_slab'),
                          {'type': 'bottom', 'waterlogged': 'false'} if d >= r - 1 and not lift else None)
    b.column(C, C, 0.6, G + 18, G + 22, ('minecraft:cherry_log', AX))
    b.put(C, G + 22, C, ('minecraft:pearlescent_froglight', AX))
    b.ball(C, G + 2, C, 1.6, lambda x, y, z: 'minecraft:pink_stained_glass' if h(x, y, z) < 0.7 else ('minecraft:pearlescent_froglight', AX))
    b.put(C, G, C, 'minecraft:chiseled_quartz_block')
    for k in range(8):                                                  # cherry trees round it
        a = k * math.pi / 4 + 0.3
        x, z = C + 11 * math.cos(a), C + 11 * math.sin(a)
        if b.rnd.random() < 0.7:
            b.column(x, z, 0.6, G, G + 5, ('minecraft:cherry_log', AX))
            b.ball(x, G + 6, z, 3, 'minecraft:cherry_leaves', ry=2)
    for _ in range(60):
        x, z = b.rnd.randint(2, 28), b.rnd.randint(2, 28)
        if math.hypot(x - C, z - C) <= 12 and b.g.get(x, G, z) is None:
            b.put(x, G, z, 'minecraft:pink_petals', {'facing': 'north', 'flower_amount': str(b.rnd.randint(1, 4))})
    b.chest(C, G, C + 4, 'grove')
    return b


def sunken_idol():
    b = B(29, 30, 29, 2)
    C = 14
    b.pad(C, C, G - 1, 12, 'minecraft:moss_block', 'minecraft:mossy_cobblestone')
    for x in range(C - 7, C + 8):
        for y in range(G - 6, G + 18):
            for z in range(C - 6, C + 7):
                u, w, v = x - C, y - G, z - C
                if (u / 7) ** 2 + ((w - 6) / 12) ** 2 + (v / 6) ** 2 <= 1:
                    face = v > 3.8
                    eye = face and abs(abs(u) - 3) < 1.3 and 8 <= w <= 9
                    mouth = face and abs(u) < 2.6 and w == 2
                    brow = face and abs(u) < 5.5 and w == 11
                    b.put(x, y, z, 'minecraft:verdant_froglight' if eye else ('minecraft:black_concrete' if mouth else
                          ('minecraft:mossy_stone_bricks' if brow else ('minecraft:mossy_cobblestone' if h(x, y, z) < 0.45 else 'minecraft:stone'))),
                          AX if eye else None)
    b.box(C - 2, G + 4, C + 6, C + 2, G + 7, C + 7, 'minecraft:mossy_stone_bricks')        # the nose
    for _ in range(80):
        x, y, z = b.rnd.randint(4, 24), b.rnd.randint(G, G + 17), b.rnd.randint(4, 24)
        if b.g.get(x, y, z) is None and b.g.get(x, y + 1, z) is not None:
            b.put(x, y, z, ('minecraft:vine', {'north': 'true', 'east': 'false', 'south': 'false', 'west': 'false', 'up': 'false'}))
    b.chest(C, G, C - 8, 'grove', 'south')
    return b


def windmill_isle():
    b = B(31, 46, 31, 3)
    C, T = 15, 16
    b.island(C, C, T, 13, 'minecraft:grass_block', 'minecraft:calcite', depth=1.1)
    b.column(C, C, 3.2, T + 1, T + 18, lambda x, y, z: 'minecraft:quartz_bricks' if (y % 5) else 'minecraft:chiseled_quartz_block', taper=0.3)
    b.column(C, C, 2.6, T + 18, T + 23, 'minecraft:spruce_planks', taper=0.7)
    hub = (C, T + 16, C + 3)
    for k in range(4):                                                  # four blades of white sail
        a = k * math.pi / 2 + 0.4
        for t in range(1, 12):
            x, y = hub[0] + math.cos(a) * t, hub[1] + math.sin(a) * t
            b.put(x, y, hub[2], ('minecraft:stripped_spruce_log', {'axis': 'z'}))
            for s in (1, 2):
                b.put(x - math.sin(a) * s, y + math.cos(a) * s, hub[2], 'minecraft:white_wool')
    b.put(*hub, 'minecraft:gold_block')
    b.box(C - 1, T + 1, C + 2, C + 1, T + 3, C + 3, AIR)
    for _ in range(70):
        x, z = b.rnd.randint(3, 27), b.rnd.randint(3, 27)
        if math.hypot(x - C, z - C) < 12 and b.g.get(x, T + 1, z) is None:
            b.put(x, T + 1, z, b.rnd.choice(['minecraft:cornflower', 'minecraft:oxeye_daisy', 'minecraft:allium', 'minecraft:grass', 'minecraft:azure_bluet']))
    b.chest(C, T + 1, C, 'skyreach')
    return b


def lightning_spire():
    b = B(27, 60, 27, 4)
    C, T = 13, 18
    b.island(C, C, T, 11, 'minecraft:tuff', 'minecraft:deepslate', depth=1.6)
    b.column(C, C, 2.0, T + 1, T + 36, lambda x, y, z: 'minecraft:oxidized_cut_copper' if y % 6 < 2 else 'minecraft:polished_blackstone_bricks', taper=0.5)
    for y in range(T + 4, T + 36, 6):
        for k in range(4):
            a = k * math.pi / 2 + y * 0.3
            for j in range(2, 5):
                b.put(C + math.cos(a) * j, y, C + math.sin(a) * j, 'minecraft:lightning_rod' if j == 4 else 'minecraft:copper_block',
                      {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'} if j == 4 else None)
    b.put(C, T + 37, C, ('minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'}))
    for _ in range(40):                                                 # scorch and bones
        x, z = b.rnd.randint(3, 23), b.rnd.randint(3, 23)
        if math.hypot(x - C, z - C) < 10:
            b.put(x, T, z, 'minecraft:black_concrete' if b.rnd.random() < 0.6 else 'minecraft:magma_block')
            if b.rnd.random() < 0.15:
                b.put(x, T + 1, z, 'minecraft:skeleton_skull' if b.rnd.random() < 0.5 else BONE)
    b.chest(C + 3, T + 1, C, 'skyreach')
    return b


def soul_obelisk():
    b = B(25, 40, 25, 5)
    C = 12
    b.pad(C, C, G - 1, 10, 'minecraft:soul_soil', 'minecraft:soul_sand')
    b.box(C - 3, G - 1, C - 3, C + 3, G + 1, C + 3, 'minecraft:polished_blackstone_bricks')
    for y in range(G + 2, G + 28):
        r = 2.2 * (1 - (y - G - 2) / 30)
        for x in range(C - 3, C + 4):
            for z in range(C - 3, C + 4):
                if max(abs(x - C), abs(z - C)) <= r:
                    b.put(x, y, z, 'minecraft:light_blue_stained_glass' if (y % 5 == 0 and max(abs(x - C), abs(z - C)) > r - 1) else 'minecraft:blackstone')
    b.put(C, G + 28, C, fire(True))
    for k in range(8):
        a = k * math.pi / 4
        x, z = C + 6 * math.cos(a), C + 6 * math.sin(a)
        b.column(x, z, 0.5, G, G + 3, 'minecraft:polished_blackstone_wall')
        b.put(x, G + 3, z, lantern(True))
        px, pz = C + 8.5 * math.cos(a + 0.3), C + 8.5 * math.sin(a + 0.3)    # skull piles
        b.put(px, G, pz, BONE)
        b.put(px, G + 1, pz, 'minecraft:skeleton_skull')
    b.chest(C, G + 2, C - 4, 'hollow', 'north')
    return b


def hollow_forge():
    b = B(29, 30, 29, 6)
    C = 14
    b.pad(C, C, G - 1, 12, 'minecraft:basalt', 'minecraft:blackstone')
    b.box(C - 8, G - 1, C - 6, C + 8, G + 7, C + 6, lambda x, y, z: 'minecraft:polished_basalt' if (x + y) % 4 == 0 else 'minecraft:polished_blackstone_bricks',
          hollow=True)
    for x in range(C - 8, C + 9):
        for z in range(C - 6, C + 7):
            b.put(x, G + 8, z, 'minecraft:blackstone_slab', {'type': 'bottom', 'waterlogged': 'false'})
    b.box(C - 7, G - 1, C - 1, C + 7, G - 1, C + 1, 'minecraft:lava')     # the lava channel through the floor
    b.box(C - 2, G, C + 6, C + 2, G + 4, C + 6, AIR)                     # the door
    b.column(C + 5, C - 4, 1.6, G + 8, G + 20, 'minecraft:bricks')
    b.put(C + 5, G + 20, C - 4, fire(False))
    for (x, z) in [(C - 5, C - 4), (C - 2, C - 4), (C + 1, C - 4)]:
        b.put(x, G, z, ('minecraft:blast_furnace', {'facing': 'south', 'lit': 'true'}))
    b.put(C - 4, G, C + 3, ('minecraft:anvil', {'facing': 'east'}))
    b.put(C + 4, G, C + 3, ('minecraft:smithing_table', None))
    b.chest(C - 6, G, C + 4, 'hollow', 'east')
    return b


def sunken_lighthouse():
    b = B(25, 40, 25, 7)
    C = 12
    b.pad(C, C, G - 1, 10, 'minecraft:sand', 'minecraft:sandstone')
    tilt = 0.16
    for y in range(G, G + 26):
        cx = C + (y - G) * tilt
        r = 3.6 - (y - G) * 0.05
        if y > G + 18 and h(0, y, 0) < 0.3:
            continue                                                    # broken off near the top
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(C - 5, C + 6):
                d = math.hypot(x - cx, z - C)
                if r - 1.2 < d <= r:
                    b.put(x, y, z, 'minecraft:prismarine_bricks' if (y // 4) % 2 else 'minecraft:dark_prismarine')
                elif d <= r - 1.2:
                    b.put(x, y, z, 'minecraft:water', {'level': '0'})
    b.ball(C + 26 * tilt, G + 26, C, 2.0, 'minecraft:sea_lantern')
    for _ in range(18):                                                 # fallen blocks and kelp
        x, z = b.rnd.randint(2, 22), b.rnd.randint(2, 22)
        b.put(x, G, z, 'minecraft:prismarine_bricks' if b.rnd.random() < 0.5 else ('minecraft:sea_pickle', {'pickles': '3', 'waterlogged': 'true'}))
    b.chest(C - 5, G, C, 'drowned', 'east')
    return b


def leviathans_rest():
    b = B(41, 26, 25, 8)
    Z = 12
    b.pad(20, Z, G - 1, 12, 'minecraft:gravel', 'minecraft:stone', depth=4)
    for x in range(6, 33, 4):                                           # ribs arching up out of the sea floor
        for s in (-1, 1):
            ctrl = [(x, G - 2, Z + s * 3), (x, G + 6, Z + s * 9), (x, G + 13, Z + s * 7), (x, G + 15, Z + s * 2)]
            b.tube([(c[0], c[1], c[2]) for c in ctrl], lambda t: 1.3 - 0.6 * t, lambda X, Y, W, t: BONE if h(X, Y, W) < 0.85 else 'minecraft:calcite')
    for x in range(4, 35):
        b.ball(x, G + 0.5 * math.sin(x / 4), Z, 1.4, BONE)             # the spine along the floor
    sx = 36                                                             # the skull, jaw dropped
    b.ball(sx, G + 3, Z, 3.5, lambda X, Y, W: BONE if ((X - sx) ** 2 + (Y - G - 3) ** 2 + (W - Z) ** 2) > 6 else None, ry=3, rz=4)
    b.put(sx + 2, G + 4, Z - 2, 'minecraft:sea_lantern')
    b.put(sx + 2, G + 4, Z + 2, 'minecraft:sea_lantern')
    b.chest(20, G, Z, 'drowned')
    return b


def frozen_knight():
    b = B(27, 40, 27, 9)
    C = 13
    b.pad(C, C, G - 1, 11, 'minecraft:snow_block', 'minecraft:packed_ice')
    # the knight, a grey figure standing, sealed in a glassy block of ice
    for y in range(G, G + 22):
        w = y - G
        for x in range(C - 5, C + 6):
            for z in range(C - 4, C + 5):
                u, v = x - C, z - C
                body = False
                if w < 9:
                    body = abs(abs(u) - 1.6) < 1.2 and abs(v) < 1.3          # legs
                elif w < 16:
                    body = abs(u) < 3.2 and abs(v) < 2.0                     # torso
                elif w < 17:
                    body = abs(u) < 4.4 and abs(v) < 2.2                     # pauldrons
                elif w < 21:
                    body = abs(u) < 1.6 and abs(v) < 1.6                     # helm
                if body:
                    visor = w == 19 and v < -1.0 and abs(u) < 1.2
                    b.put(x, y, z, 'minecraft:light_blue_stained_glass' if visor else ('minecraft:iron_block' if w >= 16 or h(x, y, z) < 0.5 else 'minecraft:light_gray_concrete'))
                elif abs(u) <= 5 and abs(v) <= 4 and w < 23:
                    b.put(x, y, z, 'minecraft:ice' if h(x, y, z) < 0.85 else 'minecraft:packed_ice', over=False)
    for y in range(G, G + 14):                                          # the sword, planted before it
        b.put(C, y, C - 5, 'minecraft:iron_block' if y < G + 11 else ('minecraft:gold_block' if y == G + 11 else 'minecraft:polished_deepslate'))
    for s in (-1, 1):
        b.put(C + s, G + 11, C - 5, 'minecraft:gold_block')
    for k in range(10):
        a = k * math.pi / 5
        x, z = C + 10 * math.cos(a), C + 10 * math.sin(a)
        for j in range(b.rnd.randint(4, 12)):
            b.put(x, G + j, z, 'minecraft:packed_ice' if j < 4 else 'minecraft:blue_ice')
    b.chest(C + 6, G, C, 'pale', 'west')
    return b


def hunters_lodge():
    b = B(27, 26, 27, 10)
    C = 13
    b.pad(C, C, G - 1, 12, 'minecraft:snow_block', 'minecraft:dirt')
    b.box(C - 6, G - 1, C - 4, C + 2, G + 5, C + 4, lambda x, y, z: ('minecraft:spruce_log', {'axis': 'x'}) if y % 2 else 'minecraft:spruce_planks', hollow=True)
    for k in range(6):                                                  # a steep roof
        for x in range(C - 7, C + 4):
            for z in (C - 5 + k, C + 5 - k):
                b.put(x, G + 6 + k, z, ('minecraft:spruce_stairs', {'facing': 'south' if z < C else 'north', 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'}))
                b.put(x, G + 7 + k, z, 'minecraft:snow', {'layers': '2'})
    b.box(C - 3, G, C + 4, C - 2, G + 2, C + 4, AIR)
    b.column(C - 5, C - 3, 0.6, G + 5, G + 13, 'minecraft:cobblestone')
    for s in (-1, 1):                                                   # antlers over the door
        for j in range(4):
            b.put(C - 2.5 + s * (1 + j * 0.6), G + 4 + j * 0.7, C + 5, BONE)
    b.put(C - 3, G + 1, C - 2, fire(False))
    for x in range(C + 5, C + 11):                                      # the frozen pond
        for z in range(C - 3, C + 4):
            if math.hypot(x - C - 8, z - C) < 3.2:
                b.put(x, G - 1, z, 'minecraft:ice')
    for (x, z) in [(C + 4, C - 6), (C - 8, C + 6), (C + 6, C + 7)]:
        b.column(x, z, 0.6, G, G + 7, ('minecraft:spruce_log', AX))
        b.ball(x, G + 8, z, 2.6, 'minecraft:spruce_leaves', ry=3)
    b.chest(C + 1, G, C - 3, 'pale', 'west')
    return b


def sunglass_spire():
    b = B(25, 40, 25, 11)
    C = 12
    b.pad(C, C, G - 1, 10, 'minecraft:red_sand', 'minecraft:red_sandstone')
    for k in range(9):
        a = k * 0.7
        r = 0 if k == 0 else 3.5 + b.rnd.random() * 2.5
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        ht = 26 if k == 0 else b.rnd.randint(8, 18)
        lean = (math.cos(a) * 0.15, math.sin(a) * 0.15) if k else (0, 0)
        for j in range(ht):
            rr = (2.4 if k == 0 else 1.4) * (1 - j / (ht + 2)) + 0.4
            cx, cz = x + lean[0] * j, z + lean[1] * j
            for xx in range(int(cx - rr) - 1, int(cx + rr) + 2):
                for zz in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    if max(abs(xx - cx), abs(zz - cz)) <= rr:
                        b.put(xx, G + j, zz, 'minecraft:red_stained_glass' if h(xx, j, zz) < 0.75 else 'minecraft:orange_stained_glass')
        if k == 0:
            b.ball(cx, G + ht, cz, 1.6, 'minecraft:gold_block')
            b.put(cx, G + ht + 2, cz, 'minecraft:ochre_froglight', AX)
    b.chest(C - 7, G, C, 'scarlet', 'east')
    return b


def fallen_titan():
    b = B(45, 22, 27, 12)
    Z = 13
    b.pad(22, Z, G - 1, 14, 'minecraft:red_sand', 'minecraft:terracotta', depth=4)
    sx, sz = 8, Z                                                       # the skull, on its side
    b.ball(sx, G + 3, sz, 4.5, lambda x, y, z: BONE if ((x - sx) ** 2 + (y - G - 3) ** 2 + (z - sz) ** 2) > 9 else None)
    for s in (-1, 1):
        b.put(sx - 4, G + 4, sz + s * 2, AIR)
    for x in range(12, 40):                                             # the spine
        b.ball(x, G + 0.5, Z, 1.2, BONE)
    for x in range(15, 30, 3):                                          # the ribs, half in the sand
        for s in (-1, 1):
            ctrl = [(x, G - 1, Z + s * 1), (x, G + 5, Z + s * 6), (x, G + 8, Z + s * 3)]
            b.tube(ctrl, lambda t: 0.9, BONE)
    for (x, z) in [(36, Z - 6), (40, Z + 6), (20, Z + 10), (18, Z - 10)]:   # an arm and a leg flung out
        b.tube([(x - 6, G, Z), (x, G + 1, z)], lambda t: 1.0, BONE)
    b.chest(24, G, Z + 3, 'scarlet')
    return b


def fallen_gear():
    b = B(31, 46, 31, 13)
    C, T = 15, 16
    b.island(C, C, T, 12, 'minecraft:deepslate_tiles', 'minecraft:deepslate', depth=1.5)
    r, teeth = 10, 14
    tilt = 0.5
    for i in range(-r - 3, r + 4):
        for j in range(-r - 3, r + 4):
            d = math.hypot(i, j)
            ang = math.atan2(j, i)
            if d <= r - 1 or (d <= r + 1.8 and math.cos(ang * teeth) > 0.25):
                if r * 0.45 < d < r * 0.6 or (d <= r - 1 and abs(math.sin(ang * 3)) > 0.4 and d < r * 0.8 and d > 2):
                    continue
                if j < -5:
                    continue                                            # the lower part is sunk in the rock
                for dep in (0, 1):
                    b.put(C + i, T + 4 + j, C + dep + int(j * tilt * 0.3), 'minecraft:gold_block' if d < 2 else 'minecraft:waxed_cut_copper')
    for k in range(4):
        x, z = C + b.rnd.randint(-8, 8), C + b.rnd.randint(-8, 8)
        b.put(x, T + 1, z, ('minecraft:piston', {'facing': 'up', 'extended': 'false'}))
        for y in range(T - 10, T - 2):
            b.put(x, y, z, CHAIN, over=False)
    b.chest(C + 6, T + 1, C - 6, 'clockwork')
    return b


def stopped_clock():
    b = B(29, 48, 29, 14)
    C, T = 14, 18
    b.island(C, C, T, 11, 'minecraft:amethyst_block', 'minecraft:calcite', depth=1.6)
    for _ in range(16):                                                 # amethyst crystals bristling from the rock
        a = b.rnd.uniform(0, 2 * math.pi)
        r = b.rnd.uniform(2, 10)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        for j in range(b.rnd.randint(2, 7)):
            b.put(x + math.cos(a) * j * 0.3, T + 1 + j, z + math.sin(a) * j * 0.3, 'minecraft:amethyst_block' if j < 3 else 'minecraft:purple_stained_glass')
    R = 9                                                               # the clock face, standing upright, facing south
    cy = T + R + 3
    for i in range(-R - 1, R + 2):
        for j in range(-R - 1, R + 2):
            d = math.hypot(i, j)
            if d <= R + 0.5:
                rim = d > R - 1
                b.put(C + i, cy + j, C, 'minecraft:gold_block' if rim else 'minecraft:calcite')
                b.put(C + i, cy + j, C - 1, 'minecraft:polished_deepslate')
    for k in range(12):
        a = k * math.pi / 6
        b.put(C + round(math.cos(a) * (R - 2)), cy + round(math.sin(a) * (R - 2)), C + 1, 'minecraft:black_concrete')
    for t in range(0, 7):                                               # the hands, stopped at a minute to midnight
        b.put(C, cy + t, C + 1, 'minecraft:polished_blackstone')
    for t in range(0, 5):
        b.put(C - t * 0.2, cy + t, C + 1, 'minecraft:polished_blackstone')
    b.put(C, cy, C + 1, ('minecraft:pearlescent_froglight', AX))
    b.column(C, C, 1.4, T + 1, cy - R, 'minecraft:polished_deepslate')
    b.chest(C + 4, T + 1, C + 3, 'clockwork', 'south')
    return b


def glowcap_ring():
    b = B(29, 26, 29, 15)
    C = 14
    b.pad(C, C, G - 1, 12, 'minecraft:moss_block', 'minecraft:dirt')
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            if math.hypot(x - C, z - C) < 3.6:
                b.put(x, G - 1, z, 'minecraft:water', {'level': '0'})
    b.put(C, G - 2, C, ('minecraft:pearlescent_froglight', AX))
    for k in range(9):
        a = k * 2 * math.pi / 9
        x, z = C + 9 * math.cos(a), C + 9 * math.sin(a)
        ht = b.rnd.randint(5, 10)
        b.column(x, z, 0.7, G, G + ht, 'minecraft:mushroom_stem')
        cr = 2.6 + b.rnd.random() * 1.4
        for xx in range(int(x - cr) - 1, int(x + cr) + 2):
            for zz in range(int(z - cr) - 1, int(z + cr) + 2):
                d = math.hypot(xx - x, zz - z)
                if d <= cr:
                    b.put(xx, G + ht + (1 if d < cr * 0.5 else 0), zz, 'minecraft:shroomlight' if h(xx, ht, zz) < 0.3 else 'minecraft:glowstone')
    for _ in range(40):
        x, z = b.rnd.randint(2, 26), b.rnd.randint(2, 26)
        if 4 < math.hypot(x - C, z - C) < 12 and b.g.get(x, G, z) is None:
            b.put(x, G, z, b.rnd.choice(['minecraft:moss_carpet', 'minecraft:brown_mushroom', 'minecraft:red_mushroom']))
    b.chest(C + 11, G, C, 'mycelial', 'west')
    return b


def root_maw():
    b = B(31, 30, 23, 16)
    C, Z = 15, 11
    b.pad(C, Z, G - 1, 11, 'minecraft:rooted_dirt', 'minecraft:dirt')
    for s in (-1, 1):                                                   # two great roots twisting up into an arch
        pts = [(C + s * 11, G - 2, Z + 2), (C + s * 10, G + 6, Z), (C + s * 7, G + 13, Z - 1), (C + s * 2, G + 17, Z), (C, G + 18, Z)]
        b.tube(pts, lambda t: 2.6 - 1.2 * t, lambda x, y, z, t: ('minecraft:mangrove_log', AX) if h(x, y, z) < 0.6 else 'minecraft:mangrove_roots')
    for k in range(-5, 6):                                              # fangs hanging from the arch and rising from the floor
        x = C + k * 1.6
        top = G + 17 - abs(k) * 0.9
        for j in range(3):
            b.put(x, top - 1 - j, Z, ('minecraft:pointed_dripstone', {'thickness': 'tip' if j == 2 else 'middle', 'vertical_direction': 'down', 'waterlogged': 'false'}))
        if abs(k) > 1:
            b.put(x, G, Z + 1, BONE)
            b.put(x, G + 1, Z + 1, ('minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': 'up', 'waterlogged': 'false'}))
    for _ in range(50):
        x, y, z = b.rnd.randint(2, 28), b.rnd.randint(G, G + 18), b.rnd.randint(2, 20)
        if b.g.get(x, y, z) is None and b.g.get(x, y + 1, z) is not None and b.g.get(x, y + 1, z)[0] != AIR:
            b.put(x, y, z, ('minecraft:hanging_roots', {'waterlogged': 'false'}))
    b.chest(C, G, Z - 4, 'mycelial', 'south')
    return b


# id: (biome, builder, realm, placement)
LANDMARKS = {
    'petal_shrine': ('bloomwild', petal_shrine, 'grove', 'surface'),
    'sunken_idol': ('mossveil_thicket', sunken_idol, 'grove', 'surface'),
    'windmill_isle': ('cloud_meadows', windmill_isle, 'skyreach', 'sky'),
    'lightning_spire': ('stormfront', lightning_spire, 'skyreach', 'sky'),
    'soul_obelisk': ('soulfire_wastes', soul_obelisk, 'hollow', 'cave'),
    'hollow_forge': ('ember_deeps', hollow_forge, 'hollow', 'cave'),
    'sunken_lighthouse': ('kelp_forest', sunken_lighthouse, 'drowned', 'seafloor'),
    'leviathans_rest': ('coral_graveyard', leviathans_rest, 'drowned', 'seafloor'),
    'frozen_knight': ('frozen_spires', frozen_knight, 'pale', 'surface'),
    'hunters_lodge': ('whisper_taiga', hunters_lodge, 'pale', 'surface'),
    'sunglass_spire': ('glass_dunes', sunglass_spire, 'scarlet', 'surface'),
    'fallen_titan': ('bone_flats', fallen_titan, 'scarlet', 'surface'),
    'fallen_gear': ('gearfields', fallen_gear, 'clockwork', 'sky'),
    'stopped_clock': ('stopped_hour', stopped_clock, 'clockwork', 'sky'),
    'glowcap_ring': ('glowcap_hollows', glowcap_ring, 'mycelial', 'cave'),
    'root_maw': ('rootmaw', root_maw, 'mycelial', 'cave'),
}
CAVE_Y = {'hollow': (33, 36), 'mycelial': (34, 52)}
SKY_Y = {'skyreach': (60, 140), 'clockwork': (80, 140)}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=2)


def main(only=None):
    for k, (lid, (biome, fn, realm, kind)) in enumerate(LANDMARKS.items()):
        if only and lid not in only:
            continue
        b = fn()
        was = gen_citadels2.ENRICH
        gen_citadels2.ENRICH = False
        try:
            b.g.save(f'landmark_{lid}')
        finally:
            gen_citadels2.ENRICH = was
        s = {'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/landmark_{lid}', 'step': 'surface_structures', 'terrain_adaptation': 'none',
             'start_pool': f'aurelia:landmark_{lid}/start', 'size': 1, 'max_distance_from_center': 80, 'use_expansion_hack': False, 'spawn_overrides': {}}
        if kind == 'surface':
            s['start_height'] = {'absolute': -G}
            s['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
            s['terrain_adaptation'] = 'beard_thin'
        elif kind == 'seafloor':
            s['start_height'] = {'absolute': -G}
            s['project_start_to_heightmap'] = 'OCEAN_FLOOR_WG'
        elif kind == 'cave':
            lo, hi = CAVE_Y[realm]
            s['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo - G}, 'max_inclusive': {'absolute': hi - G}}
            s['terrain_adaptation'] = 'beard_thin'
        else:
            lo, hi = SKY_Y[realm]
            s['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}
        dump(f'{WG}/structure/landmark_{lid}.json', s)
        dump(f'{WG}/structure_set/landmark_{lid}.json', {'structures': [{'structure': f'aurelia:landmark_{lid}', 'weight': 1}],
                                                         'placement': {'type': 'minecraft:random_spread', 'spacing': 14, 'separation': 6, 'salt': 91100000 + k}})
        dump(f'{WG}/template_pool/landmark_{lid}/start.json', {'fallback': 'minecraft:empty', 'elements': [
            {'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:landmark_{lid}',
                                      'processors': {'processors': []}, 'projection': 'rigid'}}]})
        dump(f'{D}/tags/worldgen/biome/has_structure/landmark_{lid}.json', {'replace': False, 'values': [f'aurelia:{biome}']})


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
