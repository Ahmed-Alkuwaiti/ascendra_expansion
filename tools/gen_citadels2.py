"""Three independent citadels as vanilla structure templates (DataVersion 3465 = 1.20.1).

Rootbound  - a castle grown into a giant tree. Puzzle: plant four Spore Hearts.
Stormwatch - quartz spires on a rock crag.      Puzzle: lure Storm Wisps so their lightning charges three pylons.
Ashen      - a fortress in a lava cavern.       Puzzle: place twelve Soul Sigils in the sockets.
"""
import json
import math
import os
import random

import nbtlib
from nbtlib import Byte, Compound, Double, Int, List, String

from citadel_detail import (rootbound_detail, stormwatch_detail, ashen_detail, rootbound_gimmicks,
                            stormwatch_gimmicks, ashen_gimmicks)
from citadel_detail2 import rootbound_grand, stormwatch_grand, ashen_grand

OUT = __import__('paths').RES + '/data/aurelia/structures'
AIR = 'minecraft:air'
PASSABLE = {AIR, 'minecraft:lily_pad', 'minecraft:sweet_berry_bush', 'minecraft:end_rod', 'minecraft:cave_vines', 'minecraft:cave_vines_plant',
            'minecraft:skeleton_skull', 'minecraft:ladder', 'minecraft:cobweb', 'minecraft:moss_carpet', 'minecraft:red_mushroom', 'minecraft:brown_mushroom',
            'minecraft:soul_campfire', 'minecraft:lightning_rod', 'minecraft:soul_lantern', 'minecraft:red_wall_banner',
            'minecraft:fern', 'minecraft:grass', 'minecraft:tall_grass', 'minecraft:large_fern', 'minecraft:vine', 'minecraft:azalea',
            'minecraft:flowering_azalea', 'minecraft:lantern', 'minecraft:chain', 'minecraft:hanging_roots', 'minecraft:red_carpet',
            'minecraft:green_wall_banner', 'minecraft:light_blue_wall_banner', 'minecraft:cornflower', 'minecraft:blue_orchid',
            'minecraft:allium', 'minecraft:azure_bluet', 'minecraft:oxeye_daisy', 'minecraft:lily_of_the_valley', 'minecraft:poppy'}


class Grid:
    def __init__(self, W, H, L):
        self.W, self.H, self.L = W, H, L
        self.b = {}
        self.entities = []

    def set(self, x, y, z, name, props=None, nbt=None):
        x, y, z = int(x), int(y), int(z)
        if 0 <= x < self.W and 0 <= y < self.H and 0 <= z < self.L:
            self.b[(x, y, z)] = (name, tuple(sorted((props or {}).items())), nbt)

    def box(self, x1, y1, z1, x2, y2, z2, name, props=None):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, name, props)

    def get(self, x, y, z):
        return self.b.get((int(x), int(y), int(z)))

    def solid(self, x, y, z):
        c = self.get(x, y, z)
        return c is not None and c[0] not in PASSABLE and c[0] not in ('minecraft:water', 'minecraft:lava')   # never stand a guard on a fluid

    def free(self, x, y, z):
        c = self.get(x, y, z)
        return c is None or c[0] in PASSABLE

    def add_entity(self, eid, x, y, z):
        nbt = Compound({'id': String(eid), 'PersistenceRequired': Byte(1)})
        self.entities.append(Compound({
            'pos': List[Double]([Double(x + 0.5), Double(y), Double(z + 0.5)]),
            'blockPos': List[Int]([Int(int(x)), Int(int(y)), Int(int(z))]), 'nbt': nbt}))

    def ground_guard(self, eid, x, z, y_hint, height=2, radius=5):
        """Stand a guard on the nearest solid ground to (x, z); returns False if nowhere fits."""
        for r in range(radius + 1):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) != r:
                        continue
                    for y in range(y_hint + 14, y_hint - 4, -1):
                        if self.solid(x + dx, y - 1, z + dz) and all(self.free(x + dx, y + k, z + dz) for k in range(height)):
                            if not self.solid(x + dx, y - 1, z + dz):
                                continue
                            self.add_entity(eid, x + dx, y, z + dz)
                            return True
        print('  !! could not place', eid, 'near', x, z)
        return False

    def air_guard(self, eid, x, y, z):
        for k in range(0, 12):
            if all(self.free(x + a, y + k + b, z + c) for a in (0, 1) for b in (0, 1) for c in (0, 1)):
                self.add_entity(eid, x, y + k, z)
                return True
        print('  !! could not place flyer', eid)
        return False

    def save(self, name):
        palette, index, blocks = [], {}, []
        for (x, y, z), (bname, props, nbt) in sorted(self.b.items()):
            key = (bname, props)
            if key not in index:
                index[key] = len(palette)
                entry = Compound({'Name': String(bname)})
                if props:
                    entry['Properties'] = Compound({k: String(v) for k, v in props})
                palette.append(entry)
            blk = Compound({'pos': List[Int]([Int(x), Int(y), Int(z)]), 'state': Int(index[key])})
            if nbt is not None:
                blk['nbt'] = nbt
            blocks.append(blk)
        root = Compound({'DataVersion': Int(3465), 'size': List[Int]([Int(self.W), Int(self.H), Int(self.L)]),
                         'palette': List[Compound](palette), 'blocks': List[Compound](blocks),
                         'entities': List[Compound](self.entities)})
        os.makedirs(OUT, exist_ok=True)
        nbtlib.File(root, gzipped=True).save(f'{OUT}/{name}.nbt')
        print(f'{name}: {len(blocks)} blocks, {len(self.entities)} guards, size {self.W}x{self.H}x{self.L}')


# ------------------------------------------------------------------ shared helpers
def disc(g, cx, cz, r, y, block, props=None):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            if (x - cx) ** 2 + (z - cz) ** 2 <= r * r:
                g.set(x, y, z, block, props)


def chest_nbt(table):
    return Compound({'id': String('minecraft:chest'), 'LootTable': String(table)})


def lectern(g, x, y, z, facing, title, pages):
    book = Compound({'id': String('minecraft:written_book'), 'Count': Byte(1), 'tag': Compound({
        'title': String(title), 'author': String('The Last Archivist'),
        'pages': List[String]([String(json.dumps({'text': p})) for p in pages])})})
    g.set(x, y, z, 'minecraft:lectern', {'facing': facing, 'has_book': 'true', 'powered': 'false'},
          Compound({'id': String('minecraft:lectern'), 'Page': Int(0), 'Book': book}))


def waygate(g, x, y, z, realm):
    g.set(x, y, z, 'aurelia:waygate', {'realm': realm, 'active': 'false'})


def sphere(g, cx, cy, cz, r, block, props=None, skip_below=None):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r and (skip_below is None or y > skip_below):
                    g.set(x, y, z, block, props)


LEAVES = {'persistent': 'true', 'distance': '7', 'waterlogged': 'false'}
LOG_Y = {'axis': 'y'}


# ================================================================== ROOTBOUND CITADEL (Gaudy Grove)
def rootbound():
    W = L = 65
    H = 76
    C = 32
    G = 10
    rnd = random.Random(101)
    g = Grid(W, H, L)

    def r_out(y):
        return 9 + 7 * math.exp(-(y - G) / 7.0)

    # ground disc and a cleared volume above it
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= 31:
                for y in range(G + 1, H):
                    g.set(x, y, z, AIR)
                for y in range(0, G):
                    g.set(x, y, z, 'minecraft:dirt' if rnd.random() < 0.8 else 'minecraft:coarse_dirt')
                roll = rnd.random()
                if roll < 0.72:
                    g.set(x, G, z, 'minecraft:moss_block')
                elif roll < 0.86:
                    g.set(x, G, z, 'minecraft:grass_block', {'snowy': 'false'})
                else:
                    g.set(x, G, z, 'minecraft:podzol', {'snowy': 'false'})

    # the giant trunk: hollow ground-floor hall under a dome, solid above
    def r_in(y):
        if y <= G + 13:
            return 7
        return max(0, 7 - (y - (G + 13)))
    for y in range(G + 1, G + 50):
        ro, ri = r_out(y), r_in(y)
        for x in range(C - 17, C + 18):
            for z in range(C - 17, C + 18):
                d = math.hypot(x - C, z - C)
                if d <= ro:
                    if d <= ri:
                        g.set(x, y, z, AIR)
                    else:
                        roll = rnd.random()
                        if roll < 0.05 and d > ro - 1.5:
                            g.set(x, y, z, 'minecraft:moss_block')
                        elif roll < 0.30:
                            g.set(x, y, z, 'minecraft:stripped_dark_oak_log', LOG_Y)
                        else:
                            g.set(x, y, z, 'minecraft:dark_oak_log', LOG_Y)

    # roots running out and down into the ground, leaving the south side open for the entrance
    for k in range(8):
        ang = math.radians(15 + 45 * k)
        if abs(math.degrees(ang) - 90) < 22:
            continue
        for i in range(60):
            t = i / 59.0
            rr = 8 + 19 * t
            y = G + 1 + 9 * (1 - t) ** 2
            rad = 3.4 - 2.3 * t
            px, pz = C + rr * math.cos(ang), C + rr * math.sin(ang)
            sphere(g, px, y, pz, rad, 'minecraft:dark_oak_wood', LOG_Y, skip_below=G)

    # entrance corridor through the trunk and a stone path to the gate
    for z in range(C + 5, C + 24):
        for x in range(C - 2, C + 3):
            for y in range(G + 1, G + 7 + (1 if abs(x - C) < 2 else 0)):
                g.set(x, y, z, AIR)
        for x in range(C - 2, C + 3):
            g.set(x, G, z, 'minecraft:mossy_stone_bricks' if rnd.random() < 0.5 else 'minecraft:stone_bricks')
    for z in range(C + 24, C + 31):
        for x in range(C - 2, C + 3):
            g.set(x, G, z, 'minecraft:stone_bricks' if rnd.random() < 0.6 else 'minecraft:mossy_stone_bricks')

    # the portal hall inside the trunk
    for x in range(C - 8, C + 9):
        for z in range(C - 8, C + 9):
            d = math.hypot(x - C, z - C)
            if d <= 7:
                g.set(x, G, z, 'minecraft:mossy_stone_bricks' if 4.5 <= d else 'minecraft:stripped_dark_oak_log', None if d >= 4.5 else LOG_Y)
    frame = 'minecraft:stripped_dark_oak_log'
    for y in range(G + 1, G + 6):
        g.set(C - 2, y, C - 6, frame, LOG_Y)
        g.set(C + 2, y, C - 6, frame, LOG_Y)
    g.box(C - 2, G + 5, C - 6, C + 2, G + 5, C - 6, frame, {'axis': 'x'})
    for x in (C - 1, C, C + 1):
        for y in range(G + 1, G + 5):
            g.set(x, y, C - 6, 'minecraft:lime_stained_glass')
    waygate(g, C, G + 1, C - 6, 'grove')
    planters = [(C - 5, C - 1), (C + 5, C - 1), (C - 3, C + 4), (C + 3, C + 4)]
    for (px, pz) in planters:
        g.set(px, G + 1, pz, 'aurelia:spore_planter', {'filled': 'false'})
        steps = 12
        for i in range(1, steps):                     # glowing floor lines from each planter to the portal
            x = px + (C - px) * i / steps
            z = pz + (C - 5 - pz) * i / steps
            if i % 2 == 0:
                g.set(round(x), G, round(z), 'minecraft:verdant_froglight', {'axis': 'y'})
    for a in range(8):
        ang = math.radians(45 * a + 22)
        g.set(C + round(6.6 * math.cos(ang)), G + 9, C + round(6.6 * math.sin(ang)), 'minecraft:shroomlight')
    lectern(g, C - 5, G + 1, C + 3, 'east', 'The Rootbound Citadel',
            ["The Grove was the Sovereign's garden. Mossback planted a seed that was meant to bloom once. "
             "It has been blooming ever since, and the garden has stopped asking permission.",
             "The portal in this hall is shut. Four planters wait for Spore Hearts. Sporecaps carry them, and each "
             "tower holds a chest of spare seed. Plant all four and the way to the Grove opens."])

    # branches and canopy
    top = G + 50
    for k in range(5):
        ang = math.radians(72 * k + 20)
        for i in range(40):
            t = i / 39.0
            rr = 8 + 15 * t
            y = G + 36 + 8 * t
            sphere(g, C + rr * math.cos(ang), y, C + rr * math.sin(ang), 2.2 - 0.6 * t, 'minecraft:dark_oak_wood', LOG_Y)
        sphere(g, C + 23 * math.cos(ang), G + 46, C + 23 * math.sin(ang), 6, 'minecraft:dark_oak_leaves', LEAVES)
    for x in range(C - 26, C + 27):
        for y in range(top - 4, top + 14):
            for z in range(C - 26, C + 27):
                v = ((x - C) / 25.0) ** 2 + ((y - (top + 4)) / 9.0) ** 2 + ((z - C) / 25.0) ** 2
                if v <= 1 and rnd.random() < 0.82 and not g.solid(x, y, z):
                    g.set(x, y, z, 'minecraft:dark_oak_leaves' if rnd.random() < 0.8 else 'minecraft:oak_leaves', LEAVES)
    for _ in range(14):                           # shelf mushrooms growing out of the trunk
        ang = rnd.uniform(0, 6.28)
        y = rnd.randint(G + 14, G + 44)
        rr = r_out(y) + 1
        cx, cz = C + rr * math.cos(ang), C + rr * math.sin(ang)
        g.set(cx - 0.5 * math.cos(ang), y, cz - 0.5 * math.sin(ang), 'minecraft:mushroom_stem')
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if dx * dx + dz * dz <= 5 and g.free(round(cx + dx), y + 1, round(cz + dz)):
                    g.set(round(cx + dx), y + 1, round(cz + dz), 'minecraft:red_mushroom_block')

    # outer wall with a gate on the south side, four mushroom-capped towers on the diagonals
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 28.0 <= d <= 30.2:
                for y in range(G + 1, G + 10):
                    g.set(x, y, z, 'minecraft:mossy_stone_bricks' if rnd.random() < 0.75 else 'minecraft:mossy_cobblestone')
                if int(d * 3 + math.atan2(z - C, x - C) * 29 / 6.28) % 2 == 0:
                    g.set(x, G + 10, z, 'minecraft:mossy_stone_bricks')
    g.box(C - 3, G + 1, C + 27, C + 3, G + 7, C + 31, AIR)
    for gx in (C - 4, C + 4):
        g.box(gx, G + 1, C + 27, gx, G + 11, C + 30, 'minecraft:stripped_dark_oak_log', LOG_Y)
        g.set(gx, G + 12, C + 29, 'minecraft:shroomlight')
    g.box(C - 4, G + 8, C + 27, C + 4, G + 9, C + 30, 'minecraft:stripped_dark_oak_log', {'axis': 'x'})
    tower_hearts = 'aurelia:chests/rootbound_hearts'
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 20, C + sz * 20
        for x in range(tx - 3, tx + 4):
            for z in range(tz - 3, tz + 4):
                edge = abs(x - tx) == 3 or abs(z - tz) == 3
                for y in range(G + 1, G + 22):
                    g.set(x, y, z, ('minecraft:mossy_stone_bricks' if rnd.random() < 0.8 else 'minecraft:moss_block') if edge else AIR)
                g.set(x, G + 22, z, 'minecraft:mossy_cobblestone')
        door_x = tx - 3 * sx
        g.box(door_x, G + 1, tz - 1, door_x, G + 3, tz + 1, AIR)
        for y in (G + 9, G + 10):
            g.set(tx + 3 * sx, y, tz, 'minecraft:lime_stained_glass')
            g.set(tx, y, tz + 3 * sz, 'minecraft:lime_stained_glass')
        g.set(tx, G + 1, tz, 'minecraft:chest', {'facing': 'west' if sx > 0 else 'east', 'type': 'single', 'waterlogged': 'false'},
              chest_nbt(tower_hearts))
        for dy, r in enumerate([5, 5, 4, 3, 1]):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if dx * dx + dz * dz <= r * r + r // 2:
                        g.set(tx + dx, G + 23 + dy, tz + dz, 'minecraft:mushroom_stem' if rnd.random() < 0.12 else 'minecraft:red_mushroom_block')
    # lantern posts along the approach, mossy detail in the courtyard
    for z in range(C + 12, C + 28, 5):
        for px in (C - 4, C + 4):
            g.box(px, G + 1, z, px, G + 3, z, 'minecraft:mossy_cobblestone')
            g.set(px, G + 4, z, 'minecraft:shroomlight')
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 17 < d < 27.5 and g.get(x, G, z) and g.free(x, G + 1, z) and g.get(x, G + 1, z) is None:
                if rnd.random() < 0.10:
                    g.set(x, G + 1, z, 'minecraft:moss_carpet')
                elif rnd.random() < 0.03:
                    g.set(x, G + 1, z, rnd.choice(['minecraft:red_mushroom', 'minecraft:brown_mushroom']))

    rootbound_detail(g, C, G, rnd)
    rootbound_gimmicks(g, C, G, rnd)
    rootbound_grand(g, C, G, rnd)

    # garrison
    for (x, z) in [(C - 4, C + 25), (C + 4, C + 25), (C - 9, C + 13), (C + 9, C + 13)]:
        g.ground_guard('aurelia:bramble_sentinel', x, z, G + 1, 3)
    for (x, z) in [(C - 13, C + 14), (C + 13, C + 14), (C - 19, C - 4), (C + 19, C - 4), (C - 3, C - 20), (C + 8, C + 21)]:
        g.ground_guard('aurelia:sporecap', x, z, G + 1, 2)
    for (x, z) in [(C - 22, C + 4), (C + 22, C + 4), (C - 10, C - 22), (C + 12, C - 21)]:
        g.ground_guard('aurelia:rootstalker', x, z, G + 1, 2)
    g.save('rootbound_citadel')
    return g


# ================================================================== STORMWATCH CITADEL (Skyreach)
def stormwatch():
    W = L = 65
    H = 92
    C = 32
    G = 14
    rnd = random.Random(202)
    g = Grid(W, H, L)
    Q, QB, QC, QS = 'minecraft:quartz_bricks', 'minecraft:quartz_bricks', 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz'
    GLASS = 'minecraft:light_blue_stained_glass'
    ROD = {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'}

    # rock crag: a cone of calcite and stone, quartz plaza on top, grass at the rim
    for y in range(0, G + 1):
        rad = 30 * ((y + 4) / (G + 4.0)) ** 0.55
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C) + rnd.uniform(-0.8, 0.8)
                if d <= rad:
                    if y == G:
                        g.set(x, y, z, QS if d <= 24 else 'minecraft:grass_block', None if d <= 24 else {'snowy': 'false'})
                    else:
                        g.set(x, y, z, 'minecraft:calcite' if rnd.random() < 0.7 else 'minecraft:stone')
    for x in range(W):
        for z in range(L):
            if math.hypot(x - C, z - C) <= 31:
                for y in range(G + 1, H):
                    if g.get(x, y, z) is None:
                        g.set(x, y, z, AIR)
    for x in range(W):                                      # plaza rings and an octagon sigil
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= 24 and g.get(x, G, z):
                if int(d) in (6, 12, 18, 23):
                    g.set(x, G, z, QB)
                ang = math.atan2(z - C, x - C)
                oct_r = 15 / math.cos(((ang + math.pi / 8) % (math.pi / 4)) - math.pi / 8)
                if abs(d - oct_r) < 0.7:
                    g.set(x, G, z, 'minecraft:light_blue_concrete')
    for _ in range(7):                                      # trees on the grass rim
        a = rnd.uniform(0, 6.28)
        tx, tz = C + 27 * math.cos(a), C + 27 * math.sin(a)
        if math.hypot(tx - C, tz - C) < 28.5 and g.get(tx, G, tz) and g.get(tx, G, tz)[0] == 'minecraft:grass_block':
            for dy in range(1, 5):
                g.set(tx, G + dy, tz, 'minecraft:oak_log', LOG_Y)
            sphere(g, tx, G + 6, tz, 2.6, 'minecraft:oak_leaves', LEAVES)
    for a in (35, 155, 275):                                # waterfalls off the crag
        px, pz = C + 27 * math.cos(math.radians(a)), C + 27 * math.sin(math.radians(a))
        for y in range(G - 1, 0, -1):
            rad = 30 * ((y + 4) / (G + 4.0)) ** 0.55
            g.set(C + (rad - 0.5) * math.cos(math.radians(a)), y, C + (rad - 0.5) * math.sin(math.radians(a)), 'minecraft:water', {'level': '0'})

    def spire(cx, cz, r0, r1, height, hollow_to, rod_height):
        for h in range(height):
            r = r0 - (r0 - r1) * (h / height) ** 1.15
            for x in range(int(cx - r0) - 1, int(cx + r0) + 2):
                for z in range(int(cz - r0) - 1, int(cz + r0) + 2):
                    d = math.hypot(x - cx, z - cz)
                    if d <= r + 0.4:
                        inner = d <= r - 1.8 and h <= hollow_to
                        if inner:
                            g.set(x, G + 1 + h, z, AIR)
                        else:
                            band = h % 9 == 0
                            g.set(x, G + 1 + h, z, QC if band else Q)
            if h > 6 and h % 11 in (0, 1, 2) and r > 2.2:       # window slits on the four sides
                for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    g.set(cx + dx * round(r - 1), G + 1 + h, cz + dz * round(r - 1), GLASS)
        g.set(cx, G + 1 + height, cz, 'minecraft:sea_lantern')
        g.set(cx, G + 2 + height, cz, GLASS)
        for k in range(rod_height):
            g.set(cx, G + 3 + height + k, cz, 'minecraft:lightning_rod', ROD)

    spire(C, C, 9, 3, 60, 40, 4)                            # central spire
    # the portal room at the base: dome and floor
    for y in range(G + 1, G + 16):
        ri = 6.4 if y <= G + 11 else max(0.0, 6.4 - (y - (G + 11)) * 1.4)
        for x in range(C - 7, C + 8):
            for z in range(C - 7, C + 8):
                if math.hypot(x - C, z - C) <= ri:
                    g.set(x, y, z, AIR)
    for x in range(C - 7, C + 8):
        for z in range(C - 7, C + 8):
            d = math.hypot(x - C, z - C)
            if d <= 6.4:
                g.set(x, G, z, QS if int(d) % 2 == 0 else QB)
    for z in range(C + 6, C + 25):                          # doorway and approach
        for x in range(C - 2, C + 3):
            for y in range(G + 1, G + 7):
                if z <= C + 9:
                    g.set(x, y, z, AIR)
            g.set(x, G, z, QS)
    for y in range(G + 1, G + 6):
        g.set(C - 3, y, C + 8, 'minecraft:quartz_pillar', LOG_Y)
        g.set(C + 3, y, C + 8, 'minecraft:quartz_pillar', LOG_Y)
    g.box(C - 3, G + 6, C + 8, C + 3, G + 6, C + 8, QC)
    # portal alcove, pylons, copper circuit
    for x in (C - 1, C, C + 1):
        for y in range(G + 1, G + 5):
            g.set(x, y, C - 6, GLASS)
    for y in range(G + 1, G + 6):
        g.set(C - 2, y, C - 6, 'minecraft:copper_block')
        g.set(C + 2, y, C - 6, 'minecraft:copper_block')
    g.box(C - 2, G + 5, C - 6, C + 2, G + 5, C - 6, 'minecraft:cut_copper')
    waygate(g, C, G + 1, C - 6, 'skyreach')
    pylons = [(C - 4, C + 1), (C + 4, C + 1), (C, C - 2)]
    for (px, pz) in pylons:
        g.set(px, G + 1, pz, 'aurelia:storm_pylon', {'filled': 'false'})
        g.set(px, G + 2, pz, 'minecraft:lightning_rod', ROD)
        g.set(px, G + 3, pz, 'minecraft:lightning_rod', ROD)
        steps = 10
        for i in range(1, steps):
            g.set(round(px + (C - px) * i / steps), G, round(pz + (C - 1 - pz) * i / steps), 'minecraft:copper_block')
    for z in range(C - 5, C - 1):
        g.set(C, G, z, 'minecraft:copper_block')
    lectern(g, C - 5, G + 1, C + 3, 'east', 'The Stormwatch Citadel',
            ["The Tempest Roc kept the winds so well that the Sovereign built the highest citadel in Aurelia to listen to them. "
             "When the crown broke, the winds stopped listening back.",
             "The portal in this room is shut. Three pylons wait for lightning, and the Storm Wisps that haunt this "
             "citadel make plenty. Lure one close and stand beside a pylon when it strikes."])

    # four secondary spires, bridges to the central one
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        cx, cz = C + sx * 21, C + sz * 21
        spire(cx, cz, 5, 1.6, 40, 34, 3)
        # bridge: a straight deck at G+19 from the central spire to this one
        steps = int(math.hypot(cx - C, cz - C))
        for i in range(10, steps - 4):
            t = i / steps
            bx, bz = C + (cx - C) * t, C + (cz - C) * t
            for w in (-1, 0, 1):
                nx, nz = -(cz - C) / steps, (cx - C) / steps
                g.set(bx + nx * w, G + 19, bz + nz * w, QS)
            for w in (-2, 2):
                if i % 2 == 0:
                    g.set(bx + nx * w, G + 20, bz + nz * w, QC)
            if i % 6 == 0:
                for yy in range(G + 1, G + 19):
                    g.set(bx, yy, bz, 'minecraft:quartz_pillar', LOG_Y)
    # entrance arch at the plaza edge
    for y in range(G + 1, G + 13):
        g.set(C - 4, y, C + 24, 'minecraft:quartz_pillar', LOG_Y)
        g.set(C + 4, y, C + 24, 'minecraft:quartz_pillar', LOG_Y)
    g.box(C - 4, G + 13, C + 24, C + 4, G + 13, C + 24, QC)
    g.set(C - 4, G + 14, C + 24, 'minecraft:sea_lantern')
    g.set(C + 4, G + 14, C + 24, 'minecraft:sea_lantern')

    stormwatch_detail(g, C, G, rnd)
    stormwatch_gimmicks(g, C, G, rnd, lambda gg, x, y, z, table, facing: gg.set(x, y, z, 'minecraft:chest',
                        {'facing': facing, 'type': 'single', 'waterlogged': 'false'}, chest_nbt(table)))
    stormwatch_grand(g, C, G, rnd)

    # garrison
    for (x, z) in [(C - 4, C + 21), (C + 4, C + 21), (C - 11, C + 12), (C + 11, C + 12)]:
        g.ground_guard('aurelia:calcite_sentinel', x, z, G + 1, 3)
    for (x, y, z) in [(C - 3, G + 4, C + 3), (C + 3, G + 4, C + 3), (C - 14, G + 5, C), (C + 14, G + 5, C), (C, G + 6, C + 16)]:
        g.air_guard('aurelia:storm_wisp', x, y, z)
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        g.air_guard('aurelia:gale_talon', C + sx * 21 + 6 * sx, G + 32, C + sz * 21 + 6 * sz)
    g.save('stormwatch_citadel')
    return g


# ================================================================== ASHEN CITADEL (the Hollow)
def ashen():
    W = L = 81
    H = 76
    C = 40
    SURF = 66
    LAVA_TOP = 8
    rnd = random.Random(303)
    g = Grid(W, H, L)
    PB, CPB, BL, BS = 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks', 'minecraft:blackstone', 'minecraft:basalt'
    CRY = 'minecraft:crying_obsidian'
    CAMP = {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}

    def ell(x, y, z):
        return ((x - C) ** 2 + (z - C) ** 2) / 36.0 ** 2 + ((y - 26) / 24.0) ** 2

    # carve the cavern, line it with blackstone, and give it a lava lake
    for x in range(W):
        for z in range(L):
            for y in range(0, H):
                e = ell(x, y, z)
                if e < 1.0 and y >= LAVA_TOP + 1:
                    g.set(x, y, z, AIR)
                elif e < 1.14 and y >= LAVA_TOP - 4:
                    g.set(x, y, z, BL if rnd.random() < 0.8 else 'minecraft:smooth_basalt')
            d = math.hypot(x - C, z - C)
            if d < 36.5:
                for y in range(0, LAVA_TOP + 1):
                    if d < 34:
                        g.set(x, y, z, BS if y <= 3 else 'minecraft:lava', None if y <= 3 else {'level': '0'})
                    else:
                        g.set(x, y, z, BL)
    # the crater: a shaft up to the surface above the cavern
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= 12.5:
                for y in range(44, H):
                    g.set(x, y, z, AIR)
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 12.5 < d <= 14.5:
                for y in range(46, SURF + 2):
                    if g.get(x, y, z) is None:
                        g.set(x, y, z, BL if rnd.random() < 0.7 else 'minecraft:deepslate')

    # central basalt plateau, courtyard ring wall and brazier posts
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= 23:
                for y in range(4, 10):
                    g.set(x, y, z, BS if y < 9 else ('minecraft:smooth_basalt' if rnd.random() < 0.3 else BS))
    for a in range(0, 360, 6):
        for rr in (21.5, 22.5):
            x, z = C + rr * math.cos(math.radians(a)), C + rr * math.sin(math.radians(a))
            for y in range(10, 14):
                g.set(x, y, z, PB if y < 13 else CPB)
    for a in range(0, 360, 45):
        x, z = C + 22 * math.cos(math.radians(a)), C + 22 * math.sin(math.radians(a))
        for y in range(10, 16):
            g.set(x, y, z, PB)
        g.set(x, 16, z, 'minecraft:soul_campfire', CAMP)
    # lava-glow magma pillars up the cavern walls
    for a in range(0, 360, 40):
        x, z = C + 31 * math.cos(math.radians(a)), C + 31 * math.sin(math.radians(a))
        top = int(26 + 24 * math.sqrt(max(0, 1 - (31 / 36.0) ** 2)))
        for y in range(LAVA_TOP + 1, top - 1):
            g.set(x, y, z, 'minecraft:magma_block')

    # the keep: 25x25, walls two thick, four corner towers
    K0, K1 = C - 12, C + 12
    for x in range(K0, K1 + 1):
        for z in range(K0, K1 + 1):
            edge = x in (K0, K0 + 1, K1 - 1, K1) or z in (K0, K0 + 1, K1 - 1, K1)
            for y in range(10, 37):
                if edge:
                    g.set(x, y, z, CPB if rnd.random() < 0.2 else PB)
                else:
                    g.set(x, y, z, AIR)
            g.set(x, 9, z, 'minecraft:deepslate_tiles' if (x + z) % 2 == 0 else 'minecraft:polished_blackstone')
            g.set(x, 37, z, PB)
            g.set(x, 38, z, CPB)
    for x in range(K0, K1 + 1):
        for z in range(K0, K1 + 1):
            if (x in (K0, K1) or z in (K0, K1)) and (x + z) % 2 == 0:
                g.set(x, 39, z, PB)
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 12, C + sz * 12
        for x in range(tx - 3, tx + 4):
            for z in range(tz - 3, tz + 4):
                edge = abs(x - tx) == 3 or abs(z - tz) == 3
                for y in range(10, 49):
                    if edge:
                        g.set(x, y, z, CPB if rnd.random() < 0.25 else PB)
                    elif y > 37:
                        g.set(x, y, z, AIR)
                g.set(x, 49, z, PB)
        for dy in range(8):
            g.set(tx, 50 + dy, tz, 'minecraft:polished_blackstone_brick_wall')
        g.set(tx, 58, tz, CRY)
        for dy in range(6):
            for (ox, oz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
                g.set(tx + ox, 50 + dy, tz + oz, 'minecraft:polished_blackstone_brick_wall')
        g.set(tx - 3, 56, tz - 3, 'minecraft:soul_campfire', CAMP)
        g.set(tx + 3, 56, tz - 3, 'minecraft:soul_campfire', CAMP)

    # the spiral ramp from the crater down to the landing, ending on the south side (+z)
    def spiral(theta0):
        cells, y, th, r = [], SURF + 1, theta0, 10.5
        while y > 10:
            wall = 36 * math.sqrt(max(0.0, 1 - ((y - 26) / 24.0) ** 2)) - 2.6
            target = 10.5 if y >= 48 else max(10.5, wall)
            r += max(-0.5, min(0.5, target - r))
            th += 1.0 / max(r, 6)
            cells.append((C + r * math.cos(th), y, C + r * math.sin(th), th, r))
            y -= 1
        return cells, th, r
    best, best_err = 0.0, 9.0
    for k in range(0, 629):
        t0 = k * 0.01
        _, th_end, _ = spiral(t0)
        err = abs(((th_end - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi)
        if err < best_err:
            best, best_err = t0, err
    cells, th_end, r_end = spiral(best)
    for (x, y, z, th, r) in cells:
        tx, tz = -math.sin(th), math.cos(th)
        facing = ('east' if tx > 0 else 'west') if abs(tx) > abs(tz) else ('south' if tz > 0 else 'north')
        for w in (-1, 0, 1):
            wx, wz = x + math.cos(th) * w, z + math.sin(th) * w
            g.set(wx, y, wz, 'minecraft:polished_blackstone_brick_stairs',
                  {'facing': facing, 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'})
            for k in range(1, 3):
                g.set(wx, y - k, wz, PB)
    # landing and a causeway to the keep door (south side)
    lx, lz = C + r_end * math.cos(th_end), C + r_end * math.sin(th_end)
    disc(g, lx, lz, 5, 9, PB)
    for z in range(C + 12, int(lz) + 1):
        for x in range(C - 2, C + 3):
            for y in range(8, 10):
                g.set(x, y, z, PB)
            for y in range(10, 14):
                g.set(x, y, z, AIR)
        if z % 5 == 0:
            for px in (C - 3, C + 3):
                g.box(px, 9, z, px, 12, z, PB)
                g.set(px, 13, z, 'minecraft:soul_campfire', CAMP)
    g.box(C - 2, 10, K1 - 1, C + 2, 15, K1, AIR)            # keep door
    # the portal hall: pit, twelve sockets, waygate alcove, chests, lectern, lights
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            g.set(x, 9, z, 'minecraft:blue_stained_glass')
            g.set(x, 8, z, 'minecraft:black_concrete')
            g.set(x, 7, z, 'minecraft:blue_concrete' if rnd.random() < 0.18 else 'minecraft:black_concrete')
    sockets = [(C - 5, C - 3), (C - 5, C), (C - 5, C + 3), (C + 5, C - 3), (C + 5, C), (C + 5, C + 3),
               (C - 3, C - 5), (C, C - 5), (C + 3, C - 5), (C - 3, C + 5), (C, C + 5), (C + 3, C + 5)]
    for (x, z) in sockets:
        g.set(x, 10, z, 'aurelia:soul_socket', {'filled': 'false'})
        g.set(x, 9, z, PB)
    for x in (C - 1, C, C + 1):
        for y in range(10, 14):
            g.set(x, y, C - 11, 'minecraft:blue_stained_glass')
    for y in range(10, 15):
        g.set(C - 2, y, C - 10, CRY)
        g.set(C + 2, y, C - 10, CRY)
    g.box(C - 2, 14, C - 10, C + 2, 14, C - 10, CRY)
    waygate(g, C, 10, C - 10, 'hollow')
    for (cx, cz, face) in [(C - 9, C - 9, 'east'), (C + 9, C - 9, 'west'), (C - 9, C + 9, 'east'), (C + 9, C + 9, 'west')]:
        g.set(cx, 10, cz, 'minecraft:chest', {'facing': face, 'type': 'single', 'waterlogged': 'false'}, chest_nbt('aurelia:chests/ashen_sigils'))
    lectern(g, C + 4, 10, C + 8, 'north', 'The Ashen Citadel',
            ["The Hollow King did not choose his throne. He walked into the dark so that it would stop at him, and it has been "
             "pressing on him ever since. This citadel is what is left of the door he held shut.",
             "The portal at the far end is shut. Twelve sockets ring the pit and each wants a Soul Sigil. The Soul Jailers "
             "carry them, and four chests hold spares. Fill every socket."])
    for (px, pz) in [(C - 8, C - 3), (C + 8, C - 3), (C - 8, C + 4), (C + 8, C + 4)]:
        for y in range(10, 22):
            g.set(px, y, pz, PB)
        g.set(px, 22, pz, 'minecraft:soul_campfire', CAMP)
    for (lx2, lz2) in [(C - 6, C - 6), (C + 6, C - 6), (C - 6, C + 6), (C + 6, C + 6), (C, C - 8), (C, C + 8), (C - 9, C), (C + 9, C)]:
        g.set(lx2, 36, lz2, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'})
    for (bx, bz, face) in [(C - 7, C - 10, 'south'), (C + 7, C - 10, 'south'), (C - 7, C + 10, 'north'), (C + 7, C + 10, 'north')]:
        g.set(bx, 18, bz, 'minecraft:red_wall_banner', {'facing': face})

    ashen_detail(g, C, rnd, K1)
    ashen_gimmicks(g, C, rnd, K1)
    ashen_grand(g, C, rnd, K1)

    # garrison
    for (x, z) in [(C - 3, C + 17), (C + 3, C + 17)]:
        g.ground_guard('aurelia:ashbound_knight', x, z, 10, 3)
    for (x, z) in [(C - 18, C + 3), (C + 18, C + 3)]:        # outside the keep: the Ash Seal needs all four dead
        g.ground_guard('aurelia:ashbound_knight', x, z, 10, 3)
    for (x, z) in [(C - 7, C - 7), (C + 7, C - 7), (C - 7, C + 7), (C + 7, C + 7)]:
        g.ground_guard('aurelia:soul_jailer', x, z, 10, 3)
    for (x, z) in [(C - 17, C - 8), (C + 17, C - 8), (C - 15, C + 12), (C + 15, C + 12)]:
        g.ground_guard('aurelia:cinder_hound', x, z, 10, 2)
    g.save('ashen_citadel')
    return g



if __name__ == '__main__':
    rootbound()
    stormwatch()
    ashen()
