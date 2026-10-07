"""Realm structures, built to match the dimension reference art.

Gaudy Grove : forested stone pillars with waterfalls, mossy ruins (on top of amplified terrain)
Skyreach    : a void world of floating islands with cone undersides, ponds, waterfalls, blossom trees, tower ruins
The Hollow  : lava-island ziggurats, arched bridges and hanging stalactites (in the Nether-style cavern)
"""
import math
import random

from nbtlib import Compound, String

from gen_citadels2 import Grid, LEAVES, LOG_Y, chest_nbt, disc, sphere

AIR = 'minecraft:air'
FLOWERS = ['minecraft:cornflower', 'minecraft:blue_orchid', 'minecraft:allium', 'minecraft:azure_bluet',
           'minecraft:oxeye_daisy', 'minecraft:lily_of_the_valley', 'minecraft:poppy']


class Noise:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.cache = {}

    def _g(self, i, j):
        if (i, j) not in self.cache:
            self.cache[(i, j)] = self.r.random()
        return self.cache[(i, j)]

    def __call__(self, x, z, scale):
        gx, gz = x / scale, z / scale
        x0, z0 = math.floor(gx), math.floor(gz)
        tx, tz = gx - x0, gz - z0
        tx, tz = tx * tx * (3 - 2 * tx), tz * tz * (3 - 2 * tz)
        a = self._g(x0, z0) * (1 - tx) + self._g(x0 + 1, z0) * tx
        b = self._g(x0, z0 + 1) * (1 - tx) + self._g(x0 + 1, z0 + 1) * tx
        return a * (1 - tz) + b * tz


def rock(rnd):
    r = rnd.random()
    if r > 0.985:
        return 'aurelia:stormglass_ore'
    return ('minecraft:calcite' if r < 0.6 else 'minecraft:stone' if r < 0.8 else 'minecraft:andesite' if r < 0.9 else 'minecraft:tuff')


def blossom_tree(g, x, y, z, rnd, big=False):
    h = rnd.randint(5, 8) + (5 if big else 0)
    for dy in range(h):
        g.set(x, y + dy, z, 'minecraft:birch_log', LOG_Y)
        if big:
            g.set(x + 1, y + dy, z, 'minecraft:birch_log', LOG_Y)
    rr = 5 if big else 3
    for dx in range(-rr, rr + 1):
        for dy in range(-2, rr + 1):
            for dz in range(-rr, rr + 1):
                if dx * dx + (dy * 1.35) ** 2 + dz * dz <= rr * rr + 1 and rnd.random() < 0.9 and g.free(x + dx, y + h + dy, z + dz):
                    roll = rnd.random()
                    g.set(x + dx, y + h + dy, z + dz, 'minecraft:flowering_azalea_leaves' if roll < 0.5 else 'minecraft:birch_leaves' if roll < 0.8 else 'minecraft:azalea_leaves', LEAVES)


def jungle_tree(g, x, y, z, rnd):
    h = rnd.randint(9, 15)
    for dy in range(h):
        for ox in (0, 1):
            for oz in (0, 1):
                g.set(x + ox, y + dy, z + oz, 'minecraft:jungle_log', LOG_Y)
    for (cx, cy, cz, rr) in [(x, y + h, z, 5), (x + 4, y + h - 3, z + 2, 3), (x - 3, y + h - 2, z - 3, 3), (x + 1, y + h + 3, z, 3)]:
        for dx in range(-rr, rr + 1):
            for dy in range(-2, rr):
                for dz in range(-rr, rr + 1):
                    if dx * dx + (dy * 1.5) ** 2 + dz * dz <= rr * rr + 1 and rnd.random() < 0.88 and g.free(cx + dx, cy + dy, cz + dz):
                        g.set(cx + dx, cy + dy, cz + dz, 'minecraft:jungle_leaves', LEAVES)


def mushroom(g, x, y, z, rnd, big=False):
    h = rnd.randint(4, 9) + (3 if big else 0)
    cap = rnd.choice(['minecraft:red_mushroom_block', 'minecraft:brown_mushroom_block', 'minecraft:red_mushroom_block'])
    for dy in range(h):
        g.set(x, y + dy, z, 'minecraft:mushroom_stem')
    rr = rnd.randint(3, 5) + (1 if big else 0)
    for k, r in enumerate([rr, rr, rr - 1, max(1, rr - 2)]):
        for dx in range(-r, r + 1):
            for dz in range(-r, r + 1):
                if dx * dx + dz * dz <= r * r + r // 2:
                    g.set(x + dx, y + h + k, z + dz, cap)


def ground_cover(g, x, y, z, rnd, density=1.0):
    """Plants on the grass cell below (x, y, z). y is the air cell above the grass."""
    if not g.free(x, y, z):
        return
    roll = rnd.random() / density
    if roll < 0.14:
        g.set(x, y, z, rnd.choice(FLOWERS))
    elif roll < 0.30:
        g.set(x, y, z, 'minecraft:grass')
    elif roll < 0.38 and g.free(x, y + 1, z):
        g.set(x, y, z, 'minecraft:tall_grass', {'half': 'lower'})
        g.set(x, y + 1, z, 'minecraft:tall_grass', {'half': 'upper'})
    elif roll < 0.44:
        g.set(x, y, z, 'minecraft:fern')
    elif roll < 0.48 and g.free(x, y + 1, z):
        g.set(x, y, z, 'minecraft:large_fern', {'half': 'lower'})
        g.set(x, y + 1, z, 'minecraft:large_fern', {'half': 'upper'})


VINE_SIDE = {(1, 0): 'west', (-1, 0): 'east', (0, 1): 'north', (0, -1): 'south'}


def add_vines(g, rnd, ymin, ymax, chance, only=None, longest=8):
    """Vines hanging from exposed vertical faces (a vine records which side holds it)."""
    cells = [(k, v) for k, v in g.b.items() if ymin <= k[1] <= ymax and v[0] not in ('minecraft:air',)]
    for (x, y, z), (name, _, _) in cells:
        if only and name not in only:
            continue
        if rnd.random() > chance:
            continue
        for (dx, dz), face in VINE_SIDE.items():
            if g.free(x + dx, y, z + dz) and g.get(x + dx, y, z + dz) is None:
                length = rnd.randint(3, longest)
                for k in range(length):
                    if g.get(x + dx, y - k, z + dz) is None:
                        g.set(x + dx, y - k, z + dz, 'minecraft:vine', {face: 'true'})
                    else:
                        break
                break


# =============================================================== SKYREACH ISLANDS
def spire_blocks(g, cx, cz, y0, r0, r1, height, rod=3):
    for h in range(height):
        r = r0 - (r0 - r1) * (h / height) ** 1.15
        for x in range(int(cx - r0) - 1, int(cx + r0) + 2):
            for z in range(int(cz - r0) - 1, int(cz + r0) + 2):
                d = math.hypot(x - cx, z - cz)
                if d <= r + 0.4:
                    if d <= r - 1.8 and h < height - 6:
                        g.set(x, y0 + h, z, AIR)
                    else:
                        g.set(x, y0 + h, z, 'minecraft:chiseled_quartz_block' if h % 9 == 0 else 'minecraft:quartz_bricks')
        if h > 6 and h % 11 in (0, 1, 2) and r > 2.2:
            for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                g.set(cx + dx * round(r - 1), y0 + h, cz + dz * round(r - 1), 'minecraft:light_blue_stained_glass')
    g.set(cx, y0 + height, cz, 'minecraft:sea_lantern')
    for k in range(rod):
        g.set(cx, y0 + height + 1 + k, cz, 'minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})


def ruin_tower(g, cx, cz, y, rnd, radius=4):
    for dx in range(-radius - 1, radius + 2):
        for dz in range(-radius - 1, radius + 2):
            d = math.hypot(dx, dz)
            if radius - 0.8 <= d <= radius + 0.5:
                top = rnd.randint(7, 15)
                for k in range(top):
                    blk = rnd.choice(['minecraft:quartz_bricks', 'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:calcite', 'minecraft:cracked_stone_bricks'])
                    g.set(cx + dx, y + k, cz + dz, blk)
            elif d < radius - 0.8:
                g.set(cx + dx, y - 1, cz + dz, 'minecraft:smooth_quartz')
    for k in range(1, 5):                                     # doorway and windows
        for dx in (-1, 0, 1):
            g.set(cx + dx, y + k - 1, cz + radius, AIR)
    for k in (4, 5, 8):
        g.set(cx + radius, y + k, cz, 'minecraft:light_blue_stained_glass')
        g.set(cx - radius, y + k, cz, 'minecraft:light_blue_stained_glass')
    for (px, pz) in [(-9, 3), (8, -4), (4, 9), (-6, -8)]:
        for k in range(rnd.randint(3, 8)):
            g.set(cx + px, y + k, cz + pz, 'minecraft:quartz_pillar', LOG_Y)


def island(name, R, seed, kind):
    rnd = random.Random(seed)
    noise = Noise(seed)
    Y0 = 16
    D = int(R * 1.1) + 2
    top = Y0 + D
    extra = {'small': 14, 'medium': 22, 'large': 40, 'castle': 78, 'outpost': 40, 'shrine': 26}[kind]
    W = L = 2 * R + 16
    C = W // 2
    g = Grid(W, top + extra, L)
    edge_cache, ts = {}, {}
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            e = R * (1 + 0.14 * (noise(x, z, 9) - 0.5) * 2)
            if d <= e:
                ts[(x, z)] = top + int(round((noise(x + 40, z + 40, 7) - 0.5) * 2.4))
                edge_cache[(x, z)] = e

    # pond and waterfall channel (flatten first)
    pond = None
    a_w = rnd.uniform(0, 6.28)
    if kind in ('medium', 'large', 'castle'):
        pr = {'medium': 3.2, 'large': 5.2, 'castle': 5.5}[kind]
        pc = (C + (R * 0.28) * math.cos(a_w + 3.14), C + (R * 0.28) * math.sin(a_w + 3.14))
        pond = (pc, pr)
        for (x, z) in list(ts):
            if math.hypot(x - pc[0], z - pc[1]) <= pr + 2.5:
                ts[(x, z)] = top
        chan = set()
        for s in range(0, 120):
            t = s / 8.0
            x, z = round(pc[0] + t * math.cos(a_w)), round(pc[1] + t * math.sin(a_w))
            if (x, z) in ts and math.hypot(x - pc[0], z - pc[1]) > pr - 0.5:
                chan.add((x, z))
                ts[(x, z)] = top

    # the island body: grass, dirt, a calcite cone that narrows downward, hanging spikes below
    ymin_of = {}
    for (x, z), t in ts.items():
        d = math.hypot(x - C, z - C)
        f = d / edge_cache[(x, z)]
        ym = Y0 if f <= 0.12 else int(Y0 + (t - Y0) * ((f - 0.12) / 0.88) ** (1 / 0.7))
        ymin_of[(x, z)] = ym
        for y in range(ym, t + 1):
            if y == t:
                g.set(x, y, z, 'minecraft:grass_block', {'snowy': 'false'})
            elif y >= t - 3:
                g.set(x, y, z, 'minecraft:dirt' if y >= t - 2 else 'minecraft:coarse_dirt')
            else:
                g.set(x, y, z, rock(rnd))
    for _ in range(max(3, R // 2)):
        x, z = rnd.randint(C - int(R * 0.55), C + int(R * 0.55)), rnd.randint(C - int(R * 0.55), C + int(R * 0.55))
        if (x, z) not in ymin_of:
            continue
        ln = rnd.randint(4, 14)
        for i in range(ln):
            rad = max(0.0, 1.7 - 0.13 * i)
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if math.hypot(dx, dz) <= rad and ymin_of[(x, z)] - 1 - i >= 0:
                        g.set(x + dx, ymin_of[(x, z)] - 1 - i, z + dz, rock(rnd))
    if kind in ('large', 'castle'):                           # satellite rocks
        for _ in range(5):
            a = rnd.uniform(0, 6.28)
            sphere(g, C + (R + 6) * math.cos(a), top - rnd.randint(2, 12), C + (R + 6) * math.sin(a), rnd.uniform(1.8, 3.2), 'minecraft:calcite')

    # pond, then the waterfall channel
    if pond:
        (pcx, pcz), pr = pond
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - pcx, z - pcz)
                if d <= pr and (x, z) in ts:
                    g.set(x, top, z, 'minecraft:water', {'level': '0'})
                    g.set(x, top - 1, z, 'minecraft:water', {'level': '0'})
                    g.set(x, top - 2, z, 'minecraft:clay')
                elif d <= pr + 1.3 and (x, z) in ts:
                    g.set(x, top, z, 'minecraft:calcite' if rnd.random() < 0.7 else 'minecraft:stone')
        for (x, z) in chan:
            g.set(x, top, z, 'minecraft:water', {'level': '0'})
            g.set(x, top - 1, z, 'minecraft:dirt')

    # ruins, spires, trees, plants
    if kind == 'large':
        tx, tz = C + int((R * 0.45) * math.cos(a_w)), C + int((R * 0.45) * math.sin(a_w))
        ruin_tower(g, tx, tz, top + 1, rnd)
    if kind == 'castle':
        spire_blocks(g, C, C, top + 1, 8, 3, 60)
        for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            spire_blocks(g, C + sx * 19, C + sz * 19, top + 1, 4, 1.6, 38)
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if 8 < d <= 25 and (x, z) in ts and ts[(x, z)] == top and g.get(x, top, z)[0] == 'minecraft:grass_block':
                    g.set(x, top, z, 'minecraft:smooth_quartz' if int(d) % 6 else 'minecraft:quartz_bricks')
    if kind == 'outpost':
        sky_tower(g, C, C, top + 1, rnd)
    if kind == 'shrine':
        sky_shrine(g, C, C, top + 1, rnd)
    ntrees = {'small': 1, 'medium': 4, 'large': 9, 'castle': 8, 'outpost': 3, 'shrine': 3}[kind]
    for _ in range(ntrees * 4):
        if ntrees <= 0:
            break
        x, z = rnd.randint(2, W - 3), rnd.randint(2, L - 3)
        if (x, z) in ts and ts[(x, z)] == g_top(g, x, z) and g.get(x, ts[(x, z)], z)[0] == 'minecraft:grass_block' \
                and math.hypot(x - C, z - C) > (9 if kind == 'castle' else 0) and (kind != 'castle' or math.hypot(x - C, z - C) > 26) and (kind not in ('outpost', 'shrine') or math.hypot(x - C, z - C) > 11):
            if g.free(x, ts[(x, z)] + 1, z) and all(g.free(x + a, ts[(x, z)] + 1, z + b) for a in (-1, 0, 1) for b in (-1, 0, 1)):
                blossom_tree(g, x, ts[(x, z)] + 1, z, rnd, big=(kind in ('large', 'castle') and rnd.random() < 0.35))
                ntrees -= 1
    for (x, z), t in ts.items():
        if g.get(x, t, z) and g.get(x, t, z)[0] == 'minecraft:grass_block':
            ground_cover(g, x, t + 1, z, rnd, 1.0)
    add_vines(g, rnd, top - 5, top + 1, 0.045, longest=6, only={'minecraft:dirt', 'minecraft:coarse_dirt', 'minecraft:calcite', 'minecraft:grass_block'})
    if kind == 'outpost':
        g.ground_guard('aurelia:calcite_sentinel', C + 7, C + 3, top - 2 + 1, 3)
        g.air_guard('aurelia:storm_wisp', C - 6, top + 9, C + 5)
        g.air_guard('aurelia:storm_wisp', C + 5, top + 12, C - 6)
    if kind == 'shrine':
        g.air_guard('aurelia:gale_talon', C - 7, top + 8, C)
        g.air_guard('aurelia:gale_talon', C + 7, top + 10, C + 2)
        g.air_guard('aurelia:storm_wisp', C, top + 7, C - 8)
    g.save(name)


def g_top(g, x, z):
    for y in range(g.H - 1, -1, -1):
        c = g.get(x, y, z)
        if c is not None and c[0] not in ('minecraft:air',):
            return y
    return -1


# =============================================================== GROVE PILLARS AND RUINS
def pillar(name, Rb, Hh, seed):
    rnd = random.Random(seed)
    noise = Noise(seed)
    G0 = 8
    W = L = 2 * Rb + 22
    C = W // 2
    g = Grid(W, G0 + Hh + 34, L)
    for y in range(0, G0):
        disc(g, C, C, Rb + 3, y, 'minecraft:stone')
    topy = G0 + Hh
    radii = {}
    for h in range(Hh + 1):
        y = G0 + h
        flare = 3.4 * (max(0, h - (Hh - 9)) / 9.0) ** 1.4
        r = Rb * (1.0 - 0.12 * (h / Hh)) + 1.3 * math.sin(h / 4.5) + flare
        radii[y] = r
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                rr = r + (noise(x, z + y * 0.3, 6) - 0.5) * 3.0
                if d <= rr:
                    if d > rr - 1.6:
                        roll = rnd.random()
                        blk = ('minecraft:stone' if roll < 0.40 else 'minecraft:andesite' if roll < 0.65 else
                               'minecraft:mossy_cobblestone' if roll < 0.80 else 'minecraft:moss_block' if roll < 0.92 else 'minecraft:coarse_dirt' if roll < 0.975 else 'aurelia:verdant_ore')
                    else:
                        blk = 'minecraft:stone'
                    g.set(x, y, z, blk)
    # top: grass, pond, waterfall, trees, mushrooms, flowers
    a_w = rnd.uniform(0, 6.28)
    pc = (C + 0.3 * Rb * math.cos(a_w + 3.14), C + 0.3 * Rb * math.sin(a_w + 3.14))
    for x in range(W):
        for z in range(L):
            if g.get(x, topy, z):
                g.set(x, topy, z, 'minecraft:grass_block' if rnd.random() < 0.8 else 'minecraft:moss_block', {'snowy': 'false'} if True else None)
    g.b = {k: ((v[0], v[1] if v[0] == 'minecraft:grass_block' else (), v[2]) if v[0] in ('minecraft:moss_block',) else v) for k, v in g.b.items()}
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - pc[0], z - pc[1])
            if g.get(x, topy, z):
                if d <= 3.2:
                    g.set(x, topy, z, 'minecraft:water', {'level': '0'})
                    g.set(x, topy - 1, z, 'minecraft:water', {'level': '0'})
                elif d <= 4.4:
                    g.set(x, topy, z, 'minecraft:mossy_cobblestone')
    for s in range(0, 100):
        t = s / 5.0
        x, z = round(pc[0] + t * math.cos(a_w)), round(pc[1] + t * math.sin(a_w))
        if g.get(x, topy, z) and math.hypot(x - pc[0], z - pc[1]) > 2.5:
            g.set(x, topy, z, 'minecraft:water', {'level': '0'})
            if not g.get(x + round(math.cos(a_w)), topy, z + round(math.sin(a_w))):
                break
    for _ in range(90):
        x, z = rnd.randint(2, W - 3), rnd.randint(2, L - 3)
        c = g.get(x, topy, z)
        if not c or c[0] not in ('minecraft:grass_block', 'minecraft:moss_block'):
            continue
        r = rnd.random()
        if r < 0.28 and all(g.free(x + a, topy + 1, z + b) for a in (0, 1) for b in (0, 1)) and all(g.get(x + a, topy, z + b) for a in (0, 1) for b in (0, 1)):
            jungle_tree(g, x, topy + 1, z, rnd)
        elif r < 0.45:
            mushroom(g, x, topy + 1, z, rnd)
    for x in range(W):
        for z in range(L):
            c = g.get(x, topy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                ground_cover(g, x, topy + 1, z, rnd, 1.1)
    add_vines(g, rnd, G0 + 4, topy, 0.05, only={'minecraft:stone', 'minecraft:andesite', 'minecraft:mossy_cobblestone', 'minecraft:moss_block', 'minecraft:coarse_dirt'})
    for _ in range(14):                                       # boulders at the foot
        a = rnd.uniform(0, 6.28)
        sphere(g, C + (Rb + 1) * math.cos(a), G0 + 1, C + (Rb + 1) * math.sin(a), rnd.uniform(1.5, 3), 'minecraft:mossy_cobblestone', skip_below=G0 - 1)
    g.save(name)


def ruin(name, seed):
    rnd = random.Random(seed)
    W, L, H = 30, 20, 26
    g = Grid(W, H, L)
    Gy = 3
    cx, cz = W // 2, L // 2
    for x in range(W):
        for z in range(L):
            for y in range(0, Gy):
                if math.hypot((x - cx) / 14.0, (z - cz) / 9.0) <= 1:
                    g.set(x, y, z, 'minecraft:dirt')
            if math.hypot((x - cx) / 14.0, (z - cz) / 9.0) <= 1:
                g.set(x, Gy, z, 'minecraft:grass_block' if rnd.random() < 0.7 else 'minecraft:moss_block', {'snowy': 'false'} if False else None)
    g.b = {k: ((v[0], (('snowy', 'false'),) if v[0] == 'minecraft:grass_block' else (), v[2])) for k, v in g.b.items()}
    brick = lambda: rnd.choice(['minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:mossy_cobblestone'])
    for sx in (-1, 1):                                        # two pillars and the arch between them
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                for k in range(11 if sx > 0 else 8):
                    if rnd.random() > 0.05:
                        g.set(cx + sx * 7 + dx, Gy + 1 + k, cz + dz, brick())
    for i in range(0, 181, 6):
        a = math.radians(i)
        x, y = cx + 7 * math.cos(a), Gy + 9 + 5 * math.sin(a)
        for dz in range(-1, 2):
            if rnd.random() > 0.12:
                g.set(round(x), round(y), cz + dz, brick())
                g.set(round(x), round(y) + 1, cz + dz, brick())
    for (px, pz, h) in [(-10, 5, 4), (9, -5, 3), (2, 6, 5), (-4, -6, 3)]:
        for k in range(h):
            g.set(cx + px, Gy + 1 + k, cz + pz, brick())
    for x in range(cx - 5, cx + 6):                           # broken wall and stair
        for k in range(rnd.randint(1, 3)):
            g.set(x, Gy + 1 + k, cz + 6, brick())
    for k in range(4):
        g.set(cx - 3 + k, Gy + 1 + k // 2, cz - 4, 'minecraft:stone_brick_stairs', {'facing': 'east', 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'})
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                if g.free(x, Gy + 1, z):
                    ground_cover(g, x, Gy + 1, z, rnd, 1.4)
                    if rnd.random() < 0.05:
                        g.set(x, Gy + 1, z, rnd.choice(['minecraft:red_mushroom', 'minecraft:brown_mushroom']))
    add_vines(g, rnd, Gy + 2, Gy + 16, 0.35, only={'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:mossy_cobblestone', 'minecraft:cracked_stone_bricks'})
    g.save(name)


# =============================================================== HOLLOW: ZIGGURATS, ARCHES, STALACTITES
CAMP = {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}
STAIR = lambda f: {'facing': f, 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'}


def ziggurat(name, base, tiers, seed):
    rnd = random.Random(seed)
    F = 20
    W = L = base + 14
    C = W // 2
    g = Grid(W, F + tiers * 5 + 14, L)
    for y in range(F):                                        # rock plug the ziggurat stands on
        rr = base / 2 * (0.55 + 0.45 * (y / F) ** 0.6) + (rnd.random() - 0.5)
        disc(g, C, C, rr, y, 'minecraft:blackstone' if rnd.random() < 0.8 else 'minecraft:basalt')
    for t in range(tiers):
        hs = base // 2 - 3 * t
        y0 = F + 5 * t
        for dy in range(5):
            for x in range(C - hs, C + hs + 1):
                for z in range(C - hs, C + hs + 1):
                    edge = max(abs(x - C), abs(z - C)) >= hs - 1
                    roll = rnd.random()
                    g.set(x, y0 + dy, z, ('minecraft:chiseled_polished_blackstone' if dy % 5 == 4 and edge else
                                          'minecraft:cracked_polished_blackstone_bricks' if roll < 0.15 else 'minecraft:polished_blackstone_bricks') if edge or dy == 4 else 'minecraft:blackstone')
        for (fx, fz, face) in ((0, 1, 'north'), (0, -1, 'south'), (1, 0, 'west'), (-1, 0, 'east')):   # stairs on every side
            for w in range(-2, 3):
                for k in range(5):
                    x = C + fx * (hs + 1 + (4 - k) * 0) + (w if fz else 0)
                    z = C + fz * (hs + 1) + (w if fx else 0)
                    g.set(x - fx * 0, y0 + k, z, 'minecraft:polished_blackstone_brick_stairs', STAIR(face))
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            g.set(C + sx * (hs - 2), y0 + 5, C + sz * (hs - 2), 'minecraft:soul_campfire', CAMP)
        for _ in range(int(hs * 1.2)):
            x, z = rnd.randint(C - hs + 2, C + hs - 2), rnd.randint(C - hs + 2, C + hs - 2)
            if g.get(x, y0 + 5, z) is None:
                g.set(x, y0 + 5, z, rnd.choice(['minecraft:crimson_fungus', 'minecraft:nether_wart_block', 'minecraft:crimson_roots']))
    ty = F + tiers * 5
    for k in range(5):
        g.set(C, ty + k, C, 'minecraft:crying_obsidian')
    g.set(C, ty + 5, C, 'minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'})
    for (sx, sz) in ((-3, 0), (3, 0), (0, 3), (0, -3)):
        g.set(C + sx, ty, C + sz, 'minecraft:soul_campfire', CAMP)
    for x in range(C - 2, C + 3):                             # a lava pool in the top tier
        for z in range(C - 2, C + 3):
            if max(abs(x - C), abs(z - C)) == 2 and rnd.random() < 0.6:
                g.set(x, ty - 1, z, 'minecraft:lava', {'level': '0'})
    g.save(name)


def arch(name, span, seed):
    rnd = random.Random(seed)
    W, L, H = span + 20, 18, 46
    C = L // 2
    g = Grid(W, H, L)
    for sx in (-1, 1):                                        # feet: broad stepped piers
        px = W // 2 + sx * (span // 2)
        for y in range(0, 22):
            rr = 3 + (22 - y) * 0.12
            for x in range(int(px - rr - 1), int(px + rr + 2)):
                for z in range(C - 5, C + 6):
                    if abs(x - px) <= rr + 0.5 and abs(z - C) <= 4.5:
                        g.set(x, y, z, 'minecraft:blackstone' if rnd.random() < 0.7 else 'minecraft:polished_blackstone_bricks')
    for i in range(span + 1):                                 # the arched deck
        t = i / span
        x = W // 2 - span // 2 + i
        deck = 22 + int(round(8 * math.sin(math.pi * t)))
        for z in range(C - 3, C + 4):
            g.set(x, deck, z, 'minecraft:polished_blackstone_bricks')
            g.set(x, deck - 1, z, 'minecraft:cracked_polished_blackstone_bricks' if rnd.random() < 0.2 else 'minecraft:polished_blackstone_bricks')
            for k in range(2, 6):
                if abs(z - C) <= 1 and k < 4 or abs(z - C) <= 3 and k < 3:
                    g.set(x, deck - k, z, 'minecraft:blackstone')
        if i % 6 == 0:
            for z in (C - 3, C + 3):
                for k in range(1, 4):
                    g.set(x, deck + k, z, 'minecraft:polished_blackstone_brick_wall')
                g.set(x, deck + 4, z, 'minecraft:soul_campfire', CAMP)
        elif i % 2 == 0:
            for z in (C - 3, C + 3):
                g.set(x, deck + 1, z, 'minecraft:polished_blackstone_brick_wall')
    g.save(name)


def stalactite(name, seed):
    rnd = random.Random(seed)
    noise = Noise(seed)
    W = L = 34
    H = 48
    C = W // 2
    g = Grid(W, H, L)
    ln = rnd.randint(24, 46)
    r0 = rnd.uniform(6.5, 11)
    for k in range(ln + 1):
        y = H - 1 - k
        r = r0 * (1 - k / ln) ** 0.8 + 0.6 * math.sin(k / 3.0)
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d <= r + (noise(x, z + k * 0.4, 5) - 0.5) * 2:
                    roll = rnd.random()
                    g.set(x, y, z, 'minecraft:blackstone' if roll < 0.5 else 'minecraft:basalt' if roll < 0.75 else 'minecraft:smooth_basalt' if roll < 0.92 else 'minecraft:deepslate' if roll < 0.975 else 'aurelia:emberheart_ore')
        if k % 11 == 5 and r > 2:
            a = rnd.uniform(0, 6.28)
            g.set(C + (r - 1) * math.cos(a), y, C + (r - 1) * math.sin(a), 'minecraft:glowstone')
    for _ in range(3):                                        # small satellites
        a = rnd.uniform(0, 6.28)
        x0, z0 = C + (r0 + 3) * math.cos(a), C + (r0 + 3) * math.sin(a)
        for k in range(rnd.randint(5, 12)):
            rr = max(0.0, 1.8 - 0.2 * k)
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if math.hypot(dx, dz) <= rr:
                        g.set(x0 + dx, H - 1 - k, z0 + dz, 'minecraft:blackstone')
    g.save(name)


# =============================================================== OUTPOSTS (random structures with guards and loot)
def chest(g, x, y, z, table, facing='south'):
    g.set(x, y, z, 'minecraft:chest', {'facing': facing, 'type': 'single', 'waterlogged': 'false'},
          chest_nbt(f'aurelia:chests/{table}'))


def sky_tower(g, cx, cz, y, rnd):
    QB, QC = 'minecraft:quartz_bricks', 'minecraft:chiseled_quartz_block'
    H = 14
    for dx in range(-5, 6):
        for dz in range(-5, 6):
            d = math.hypot(dx, dz)
            if d <= 4.5:
                g.set(cx + dx, y - 1, cz + dz, 'minecraft:smooth_quartz')
                for k in range(H + 2):
                    if d >= 3.4:
                        if k < H:
                            g.set(cx + dx, y + k, cz + dz, QC if k % 5 == 4 else QB)
                        elif (dx + dz) % 2 == 0:
                            g.set(cx + dx, y + k, cz + dz, QB)             # crenellations
                    elif k == H - 1:
                        g.set(cx + dx, y + k, cz + dz, 'minecraft:smooth_quartz')   # the top floor
                    else:
                        g.set(cx + dx, y + k, cz + dz, AIR)
    for k in range(3):
        for dx in (-1, 0, 1):
            g.set(cx + dx, y + k, cz + 4, AIR)                             # door
    for k in range(H):                                                     # ladder up the inside of the north wall
        g.set(cx, y + k, cz - 3, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
    for k in (5, 9):
        g.set(cx + 4, y + k, cz, 'minecraft:light_blue_stained_glass')
        g.set(cx - 4, y + k, cz, 'minecraft:light_blue_stained_glass')
    chest(g, cx + 2, y + H, cz, 'skyreach_outpost', 'west')
    g.set(cx - 2, y + H, cz, 'minecraft:sea_lantern')
    g.set(cx, y + H, cz + 2, 'aurelia:stormglass_ore')
    g.set(cx + 6, y - 1, cz + 6, 'aurelia:gale_plate')                     # a launch pad beside the tower
    for (dx, dz) in ((6, -2), (-6, 3), (-3, -6)):
        g.set(cx + dx, y, cz + dz, 'aurelia:stormglass_ore')


def sky_shrine(g, cx, cz, y, rnd):
    for k in range(8):
        a = k * math.pi / 4
        px, pz = cx + 6 * math.cos(a), cz + 6 * math.sin(a)
        h = 5 + (k % 2) * 2
        for j in range(h):
            g.set(px, y + j, pz, 'minecraft:quartz_pillar', LOG_Y)
        g.set(px, y + h, pz, 'minecraft:chiseled_quartz_block')
        if k % 2 == 0:
            g.set(px, y + h + 1, pz, 'minecraft:sea_lantern')
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            g.set(cx + dx, y - 1, cz + dz, 'minecraft:smooth_quartz')
            if max(abs(dx), abs(dz)) <= 1:
                g.set(cx + dx, y, cz + dz, 'minecraft:quartz_bricks')
    chest(g, cx, y + 1, cz, 'skyreach_outpost')
    for (dx, dz) in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        g.set(cx + dx, y, cz + dz, 'aurelia:stormglass_ore')


def grove_ground(g, cx, cz, Gy, radius, rnd):
    for x in range(g.W):
        for z in range(g.L):
            if math.hypot(x - cx, z - cz) <= radius:
                for y in range(Gy):
                    g.set(x, y, z, 'minecraft:dirt')
                if rnd.random() < 0.75:
                    g.set(x, Gy, z, 'minecraft:grass_block', {'snowy': 'false'})
                else:
                    g.set(x, Gy, z, 'minecraft:moss_block')


def hut(g, cx, cz, y, rnd, cap='minecraft:red_mushroom_block', loot=None):
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            d = math.hypot(dx, dz)
            if 2.0 <= d <= 2.9:
                for k in range(3):
                    if not (dx == 0 and dz > 0 and k < 2):
                        g.set(cx + dx, y + k, cz + dz, 'minecraft:mushroom_stem')
            elif d < 2.0:
                for k in range(3):
                    g.set(cx + dx, y + k, cz + dz, AIR)
    for k, r in enumerate([4.2, 3.4, 2.2]):
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                if math.hypot(dx, dz) <= r:
                    g.set(cx + dx, y + 3 + k, cz + dz, cap)
    g.set(cx, y + 2, cz, 'minecraft:lantern', {'hanging': 'true', 'waterlogged': 'false'})
    if loot:
        chest(g, cx, y, cz - 1, loot)


def grove_outpost_tower(name, seed):
    rnd = random.Random(seed)
    W = L = 27
    C, Gy = W // 2, 3
    g = Grid(W, 30, L)
    grove_ground(g, C, C, Gy, 12, rnd)
    for x in range(W):                                                      # log palisade with a south gate
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 10.2 <= d <= 11.2 and not (abs(x - C) <= 1 and z > C):
                for k in range(rnd.randint(3, 5)):
                    g.set(x, Gy + 1 + k, z, 'minecraft:dark_oak_log', LOG_Y)
    for (sx, sz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):                   # tower legs, deck, rails, roof
        for k in range(15):
            g.set(C + sx, Gy + 1 + k, C + sz, 'minecraft:dark_oak_log', LOG_Y)
    for dx in range(-4, 5):
        for dz in range(-4, 5):
            g.set(C + dx, Gy + 10, C + dz, 'minecraft:dark_oak_planks')
            if max(abs(dx), abs(dz)) == 4 and (dx + dz) % 2 == 0:
                g.set(C + dx, Gy + 11, C + dz, 'minecraft:dark_oak_fence')
            if max(abs(dx), abs(dz)) <= 4:
                g.set(C + dx, Gy + 16, C + dz, 'minecraft:dark_oak_planks')
            if max(abs(dx), abs(dz)) <= 2:
                g.set(C + dx, Gy + 17, C + dz, 'minecraft:moss_block')
    for k in range(10):                                                     # central pole and ladder through the deck
        g.set(C, Gy + 1 + k, C, 'minecraft:stripped_dark_oak_log', LOG_Y)
        g.set(C, Gy + 1 + k, C + 1, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
    g.set(C, Gy + 10, C + 1, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
    chest(g, C - 2, Gy + 11, C - 2, 'grove_outpost')
    g.set(C + 2, Gy + 11, C - 2, 'minecraft:lantern', {'hanging': 'false', 'waterlogged': 'false'})
    g.set(C + 6, Gy + 1, C + 2, 'minecraft:campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})
    for (dx, dz) in ((-6, -4), (-7, -3), (5, -6)):
        g.set(C + dx, Gy + 1, C + dz, 'aurelia:verdant_ore')
    g.set(C, Gy, C + 9, 'aurelia:spore_vent')
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block') and math.hypot(x - C, z - C) < 9.5:
                ground_cover(g, x, Gy + 1, z, rnd, 0.9)
    g.ground_guard('aurelia:bramble_sentinel', C - 5, C + 5, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C + 6, C - 3, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C - 6, C - 1, Gy + 1, 3)
    g.ground_guard('aurelia:sporecap', C + 3, C + 7, Gy + 1, 3)
    g.save(name)


def grove_outpost_hamlet(name, seed):
    rnd = random.Random(seed)
    W = L = 31
    C, Gy = W // 2, 3
    g = Grid(W, 16, L)
    grove_ground(g, C, C, Gy, 14, rnd)
    hut(g, C - 7, C - 5, Gy + 1, rnd, 'minecraft:red_mushroom_block', 'grove_outpost')
    hut(g, C + 7, C - 4, Gy + 1, rnd, 'minecraft:brown_mushroom_block')
    hut(g, C, C + 8, Gy + 1, rnd, 'minecraft:red_mushroom_block')
    for dx in range(-2, 3):                                                 # a well
        for dz in range(-2, 3):
            d = math.hypot(dx, dz)
            if d <= 2.3:
                if d <= 1.2:
                    g.set(C + dx, Gy, C + dz, 'minecraft:water', {'level': '0'})
                else:
                    g.set(C + dx, Gy, C + dz, 'minecraft:mossy_cobblestone')
                    g.set(C + dx, Gy + 1, C + dz, 'minecraft:mossy_cobblestone')
    for (dx, dz) in ((10, 6), (-10, 5), (4, -11)):
        g.set(C + dx, Gy + 1, C + dz, 'aurelia:verdant_ore')
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                ground_cover(g, x, Gy + 1, z, rnd, 1.2)
    for (dx, dz) in ((-3, 3), (4, 3), (-2, -7)):
        g.ground_guard('aurelia:sporecap', C + dx, C + dz, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C + 9, C + 9, Gy + 1, 3)
    g.save(name)


def hollow_plug(g, C, F, radius, rnd):
    for y in range(F):
        rr = radius * (0.5 + 0.5 * (y / F) ** 0.6) + (rnd.random() - 0.5)
        for x in range(g.W):
            for z in range(g.L):
                if math.hypot(x - C, z - C) <= rr:
                    roll = rnd.random()
                    g.set(x, y, z, 'minecraft:blackstone' if roll < 0.75 else 'minecraft:basalt' if roll < 0.975 else 'aurelia:emberheart_ore')


def hollow_outpost_fort(name, seed):
    rnd = random.Random(seed)
    F = 20
    W = L = 33
    C = W // 2
    PB = 'minecraft:polished_blackstone_bricks'
    g = Grid(W, F + 22, L)
    hollow_plug(g, C, F, 14, rnd)
    for x in range(W):                                                      # low outer ring wall with a south gap
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 12 <= d <= 13.2 and not (abs(x - C) <= 2 and z > C):
                for k in range(2 + (x + z) % 2):
                    g.set(x, F + k, z, PB)
    for dx in range(-4, 5):                                                 # the keep
        for dz in range(-4, 5):
            edge = max(abs(dx), abs(dz)) == 4
            for k in range(13):
                if edge:
                    if k < 12 or (dx + dz) % 2 == 0:
                        g.set(C + dx, F + k, C + dz, 'minecraft:chiseled_polished_blackstone' if k in (5, 11) else PB)
                elif k in (6, 11):
                    g.set(C + dx, F + k, C + dz, PB)
    for k in range(3):
        for dx in (-1, 0, 1):
            g.set(C + dx, F + k, C + 4, AIR)
    for k in range(12):
        g.set(C + 3, F + k, C - 3, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
        if k in (6, 11):
            g.set(C + 3, F + k, C - 3, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
    chest(g, C - 2, F + 12, C, 'hollow_outpost', 'east')
    g.set(C, F + 12, C, 'minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'})
    for (dx, dz) in ((-8, -8), (8, -8), (-8, 8), (8, 8)):
        g.set(C + dx, F, C + dz, 'minecraft:soul_campfire', CAMP)
    for (dx, dz) in ((0, 9), (1, 11)):
        g.set(C + dx, F - 1, C + dz, 'aurelia:ember_vent')
    g.ground_guard('aurelia:ashbound_knight', C, C + 7, F - 1 + 1, 3)
    g.ground_guard('aurelia:cinder_hound', C - 7, C + 3, F - 1 + 1, 3)
    g.ground_guard('aurelia:cinder_hound', C + 7, C + 3, F - 1 + 1, 3)
    g.save(name)


def hollow_outpost_shrine(name, seed):
    rnd = random.Random(seed)
    F = 18
    W = L = 29
    C = W // 2
    g = Grid(W, F + 14, L)
    hollow_plug(g, C, F, 12, rnd)
    for k in range(6):
        a = k * math.pi / 3
        px, pz = C + 8 * math.cos(a), C + 8 * math.sin(a)
        h = 5 + (k % 2) * 3
        for j in range(h):
            g.set(px, F + j, pz, 'minecraft:obsidian' if j % 3 else 'minecraft:crying_obsidian')
        g.set(px, F + h, pz, 'minecraft:soul_campfire', CAMP)
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            g.set(C + dx, F, C + dz, 'minecraft:polished_blackstone_bricks')
    chest(g, C, F + 1, C, 'hollow_outpost')
    for (dx, dz) in ((2, 2), (-2, 2), (2, -2), (-2, -2)):
        g.set(C + dx, F + 1, C + dz, 'minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'})
    g.ground_guard('aurelia:soul_jailer', C + 5, C + 1, F - 1 + 1, 3)
    g.ground_guard('aurelia:soul_jailer', C - 5, C - 1, F - 1 + 1, 3)
    g.ground_guard('aurelia:cinder_hound', C, C + 6, F - 1 + 1, 3)
    g.save(name)


# =============================================================== DETAILED OUTPOSTS (these definitions replace the simple ones above)
PLANTLIKE = {'minecraft:grass', 'minecraft:tall_grass', 'minecraft:fern', 'minecraft:large_fern', 'minecraft:vine'} | set(FLOWERS)
HANGING = {'hanging': 'true', 'waterlogged': 'false'}
STANDING = {'hanging': 'false', 'waterlogged': 'false'}
SLAB_B = {'type': 'bottom', 'waterlogged': 'false'}
BARREL = {'facing': 'up', 'open': 'false'}
WALLB = 'minecraft:polished_blackstone_brick_wall'


def P(g, x, y, z, name, props=None, nbt=None):
    """Place only into empty space or over small plants."""
    c = g.get(x, y, z)
    if c is None or c[0] == AIR or c[0] in PLANTLIKE:
        g.set(x, y, z, name, props, nbt)
        return True
    return False


def ladder(facing):
    return {'facing': facing, 'waterlogged': 'false'}


def lamp(g, x, y, z, post='minecraft:dark_oak_fence', light='minecraft:lantern', height=2):
    for k in range(height):
        P(g, x, y + k, z, post)
    P(g, x, y + height, z, light, STANDING if 'lantern' in light else None)


def tent(g, x, y, z, length, wool):
    for i in range(length):
        for dx in (-2, 2):
            P(g, x + dx, y, z + i, wool)
        for dx in (-1, 1):
            P(g, x + dx, y + 1, z + i, wool)
        P(g, x, y + 2, z + i, wool)
    P(g, x, y, z + length - 1, 'minecraft:hay_block', LOG_Y)
    P(g, x, y + 1, z + 1, 'minecraft:lantern', HANGING)


def pike(g, x, y, z, rnd, wall=WALLB):
    P(g, x, y, z, wall)
    P(g, x, y + 1, z, wall)
    P(g, x, y + 2, z, 'minecraft:skeleton_skull', {'rotation': str(rnd.randint(0, 15))})


def sky_tower(g, cx, cz, y, rnd):
    QB, QC, QS = 'minecraft:quartz_bricks', 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz'
    H = 18
    for dx in range(-7, 8):
        for dz in range(-7, 8):
            d = math.hypot(dx, dz)
            if d <= 4.6:
                g.set(cx + dx, y - 1, cz + dz, QS)
                for k in range(H):
                    if d >= 3.5:
                        g.set(cx + dx, y + k, cz + dz, QC if k % 6 == 5 else 'minecraft:quartz_block' if rnd.random() < 0.15 else QB)
                    elif k in (5, 11):
                        g.set(cx + dx, y + k, cz + dz, QS)                       # upper floors
                    else:
                        g.set(cx + dx, y + k, cz + dz, AIR)
            if 4.6 < d <= 6.4:                                                     # balcony ring with posts
                g.set(cx + dx, y + 11, cz + dz, QS)
                if d > 5.5 and (dx + dz) % 2 == 0:
                    g.set(cx + dx, y + 12, cz + dz, QC)
            for k, r in enumerate([5.6, 4.7, 3.8, 2.8, 1.8, 0.8]):                 # conical copper roof
                if d <= r:
                    g.set(cx + dx, y + H + k, cz + dz, 'minecraft:cut_copper' if k == 0 else 'minecraft:oxidized_cut_copper')
    for k in range(3):
        g.set(cx, y + H + 6 + k, cz, 'minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})
    for k in range(3):                                                             # door, and a door onto the balcony
        for dx in (-1, 0, 1):
            g.set(cx + dx, y + k, cz + 4, AIR)
    for k in (12, 13):
        g.set(cx, y + k, cz + 4, AIR)
        g.set(cx + 4, y + k, cz, AIR)
    for k in range(0, 13):                                                         # ladder up the north wall, through both floors
        g.set(cx, y + k, cz - 3, 'minecraft:ladder', ladder('south'))
    for (k, glass) in ((3, 'minecraft:light_blue_stained_glass'), (8, 'minecraft:cyan_stained_glass'), (15, 'minecraft:light_blue_stained_glass')):
        for (dx, dz) in ((4, 0), (-4, 0), (3, 3), (-3, 3), (3, -3), (-3, -3)):
            if not (k == 3 and dz == 3):
                g.set(cx + dx, y + k, cz + dz, glass)
    for (dx, dz, face) in ((5, 0, 'east'), (-5, 0, 'west'), (0, -5, 'north')):
        P(g, cx + dx, y + 8, cz + dz, 'minecraft:light_blue_wall_banner', {'facing': face})
    P(g, cx - 2, y, cz - 2, 'minecraft:bookshelf')
    P(g, cx - 2, y + 1, cz - 2, 'minecraft:bookshelf')
    P(g, cx + 2, y, cz - 2, 'minecraft:barrel', BARREL)
    P(g, cx + 2, y, cz + 1, 'minecraft:lectern', {'facing': 'west', 'has_book': 'false', 'powered': 'false'})
    P(g, cx - 2, y + 6, cz + 1, 'minecraft:crafting_table')
    P(g, cx + 2, y + 6, cz + 1, 'minecraft:barrel', BARREL)
    P(g, cx, y + 10, cz, 'minecraft:sea_lantern')
    chest(g, cx + 2, y + 12, cz - 1, 'skyreach_outpost', 'west')
    P(g, cx - 2, y + 12, cz, 'aurelia:stormglass_ore')
    P(g, cx, y + 16, cz, 'minecraft:lantern', HANGING) if g.get(cx, y + 17, cz) else None
    for i in range(5, 12):                                                         # quartz path with end-rod lamps, gale plate at its end
        for dx in (-1, 0, 1):
            c = g.get(cx + dx, y - 1, cz + i)
            if c and c[0] == 'minecraft:grass_block':
                g.set(cx + dx, y - 1, cz + i, QS if dx == 0 else QB)
                if g.get(cx + dx, y, cz + i) and g.get(cx + dx, y, cz + i)[0] in PLANTLIKE:
                    g.set(cx + dx, y, cz + i, AIR)
                    if g.get(cx + dx, y + 1, cz + i) and g.get(cx + dx, y + 1, cz + i)[0] in PLANTLIKE:
                        g.set(cx + dx, y + 1, cz + i, AIR)
        if i % 3 == 0:
            for dx in (-2, 2):
                if g.get(cx + dx, y - 1, cz + i):
                    lamp(g, cx + dx, y, cz + i, 'minecraft:quartz_pillar', 'minecraft:end_rod', 2)
    g.set(cx + 7, y - 1, cz + 5, 'aurelia:gale_plate') if g.get(cx + 7, y - 1, cz + 5) else None
    for (dx, dz, h) in ((-8, 3, 4), (-7, -6, 2), (8, -5, 5)):
        if g.get(cx + dx, y - 1, cz + dz):
            for k in range(h):
                P(g, cx + dx, y + k, cz + dz, 'minecraft:quartz_pillar', LOG_Y)
            P(g, cx + dx + 1, y, cz + dz, 'aurelia:stormglass_ore')


def sky_shrine(g, cx, cz, y, rnd):
    QC, QS, QP = 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz', 'minecraft:quartz_pillar'
    for k in range(8):
        a = k * math.pi / 4
        px, pz = cx + 7 * math.cos(a), cz + 7 * math.sin(a)
        for j in range(7):
            g.set(px, y + j, pz, QP, LOG_Y)
        g.set(px, y + 7, pz, QC)
        if k % 2 == 0:
            g.set(px, y + 8, pz, 'minecraft:sea_lantern')
            g.set(px, y + 9, pz, 'minecraft:end_rod', {'facing': 'up'})
    for i in range(0, 360, 4):                                                     # a lintel ring joining the pillars, bells hanging from it
        a = math.radians(i)
        P(g, cx + 7 * math.cos(a), y + 7, cz + 7 * math.sin(a), 'minecraft:quartz_slab', {'type': 'top', 'waterlogged': 'false'})
    for i in (22, 112, 202, 292):
        a = math.radians(i)
        bx, bz = cx + 7 * math.cos(a), cz + 7 * math.sin(a)
        if g.get(bx, y + 7, bz):
            P(g, bx, y + 6, bz, 'minecraft:bell', {'attachment': 'ceiling', 'facing': 'north', 'powered': 'false'})
    for t, r in enumerate([4.3, 3.1, 1.9]):                                        # three-tier dais
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                if math.hypot(dx, dz) <= r:
                    g.set(cx + dx, y + t, cz + dz, QS if t < 2 else 'minecraft:quartz_bricks')
    chest(g, cx, y + 3, cz, 'skyreach_outpost')
    for (dx, dz) in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        g.set(cx + dx, y + 3, cz + dz, 'minecraft:white_candle', {'candles': str(rnd.randint(2, 4)), 'lit': 'true', 'waterlogged': 'false'})
    for (dx, dy, dz, b) in ((0, 9, 0, 'minecraft:sea_lantern'), (0, 10, 0, 'minecraft:amethyst_block'), (0, 8, 0, 'minecraft:amethyst_block'),
                            (1, 9, 0, 'minecraft:amethyst_block'), (-1, 9, 0, 'minecraft:amethyst_block'), (0, 9, 1, 'minecraft:amethyst_block'),
                            (0, 9, -1, 'minecraft:amethyst_block'), (0, 11, 0, 'minecraft:end_rod')):
        g.set(cx + dx, y + dy, cz + dz, b, {'facing': 'up'} if 'end_rod' in b else None)   # the floating crystal
    for (dx, dz) in ((3, 3), (-3, 3), (3, -3), (-3, -3)):
        P(g, cx + dx, y + 1, cz + dz, 'aurelia:stormglass_ore')


def grove_outpost_tower(name, seed):
    rnd = random.Random(seed)
    W = L = 35
    C, Gy = W // 2, 3
    g = Grid(W, 42, L)
    grove_ground(g, C, C, Gy, 16, rnd)
    LOG, PL, FENCE = 'minecraft:dark_oak_log', 'minecraft:spruce_planks', 'minecraft:dark_oak_fence'
    for x in range(W):                                                             # spiked palisade with a gatehouse
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 13.0 <= d <= 14.0 and not (abs(x - C) <= 1 and z > C):
                h = rnd.randint(4, 6)
                for k in range(h):
                    g.set(x, Gy + 1 + k, z, LOG, LOG_Y)
                g.set(x, Gy + 1 + h, z, FENCE)
    for sx in (-2, 2):
        for k in range(8):
            g.set(C + sx, Gy + 1 + k, C + 13, 'minecraft:stripped_dark_oak_log', LOG_Y)
        g.set(C + sx, Gy + 9, C + 13, 'minecraft:lantern', STANDING)
        P(g, C + sx, Gy + 5, C + 14, 'minecraft:green_wall_banner', {'facing': 'south'})
    for x in range(C - 2, C + 3):
        g.set(x, Gy + 8, C + 13, 'minecraft:stripped_dark_oak_log', {'axis': 'x'})
    g.set(C, Gy, C + 12, 'aurelia:spore_vent')
    for (sx, sz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):                           # tower legs with cross-bracing
        for k in range(16):
            g.set(C + sx, Gy + 1 + k, C + sz, LOG, LOG_Y)
    for k in range(1, 6):
        for s in (-1, 1):
            P(g, C - 3 + k, Gy + 2 + k, C + 3 * s, FENCE)
            P(g, C + 3 * s, Gy + 2 + k, C + 3 - k, FENCE)
            P(g, C + 3 - k, Gy + 7 + k if k < 5 else Gy + 11, C + 3 * s, FENCE)
    for dx in range(-5, 6):                                                        # deck, rail, cabin, stepped roof
        for dz in range(-5, 6):
            m = max(abs(dx), abs(dz))
            if m <= 5:
                g.set(C + dx, Gy + 12, C + dz, PL)
            if m == 5 and (dx + dz) % 2 == 0:
                g.set(C + dx, Gy + 13, C + dz, FENCE)
            if m == 3:
                corner = abs(dx) == 3 and abs(dz) == 3
                for k in (13, 14, 15):
                    window = k == 14 and (dx == 0 or dz == 0)
                    door = dz == 3 and dx == 0 and k < 15
                    if not window and not door:
                        g.set(C + dx, Gy + k, C + dz, 'minecraft:stripped_dark_oak_log' if corner else 'minecraft:dark_oak_planks', LOG_Y if corner else None)
            for k, half in enumerate([4, 3, 2, 1]):
                if m <= half:
                    g.set(C + dx, Gy + 16 + k, C + dz, 'minecraft:dark_oak_planks' if m == half else 'minecraft:spruce_planks')
    g.set(C, Gy + 20, C, FENCE)
    g.set(C, Gy + 21, C, 'minecraft:lantern', STANDING)
    for k in range(12):                                                            # central pole and ladder through the deck
        g.set(C, Gy + 1 + k, C, 'minecraft:stripped_dark_oak_log', LOG_Y)
        g.set(C, Gy + 1 + k, C + 1, 'minecraft:ladder', ladder('south'))
    chest(g, C - 2, Gy + 13, C - 2, 'grove_outpost')
    g.set(C + 2, Gy + 13, C - 2, 'minecraft:barrel', BARREL)
    g.set(C + 2, Gy + 13, C - 1, 'minecraft:crafting_table')
    g.set(C - 2, Gy + 13, C + 1, 'minecraft:hay_block', LOG_Y)
    g.set(C + 1, Gy + 15, C - 1, 'minecraft:lantern', HANGING)
    tent(g, C - 8, Gy + 1, C - 6, 4, 'minecraft:green_wool')                         # the yard
    tent(g, C + 8, Gy + 1, C - 8, 4, 'minecraft:lime_wool')
    P(g, C + 7, Gy + 1, C + 3, 'minecraft:campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})
    for (dx, dz, face) in ((7, 5, 'north'), (9, 3, 'west'), (5, 3, 'east')):
        P(g, C + dx, Gy + 1, C + dz, 'minecraft:spruce_stairs', STAIR(face))
    for k in range(3):
        P(g, C - 9 + k, Gy + 1, C + 6, LOG, {'axis': 'x'})
        if k < 2:
            P(g, C - 9 + k, Gy + 2, C + 6, LOG, {'axis': 'x'})
    P(g, C - 6, Gy + 1, C + 8, 'minecraft:barrel', BARREL)
    P(g, C - 5, Gy + 1, C + 8, 'minecraft:barrel', BARREL)
    P(g, C - 6, Gy + 2, C + 8, 'minecraft:barrel', BARREL)
    P(g, C + 9, Gy + 1, C + 8, 'minecraft:hay_block', LOG_Y)
    P(g, C + 9, Gy + 2, C + 8, 'minecraft:target')
    P(g, C - 10, Gy + 1, C - 1, 'minecraft:grindstone', {'face': 'floor', 'facing': 'north'})
    for dx in range(3):                                                            # an iron cage
        for dz in range(3):
            for k in range(3):
                if (dx != 1 or dz != 1) and not (dx == 1 and dz == 2 and k < 2):
                    P(g, C + 2 + dx, Gy + 1 + k, C - 11 + dz, 'minecraft:iron_bars')
            P(g, C + 2 + dx, Gy + 4, C - 11 + dz, 'minecraft:spruce_slab', SLAB_B)
    P(g, C + 3, Gy + 1, C - 10, 'minecraft:bone_block', LOG_Y)
    for (dx, dz) in ((-11, 4), (-11, 5), (10, -3), (-4, -11)):
        P(g, C + dx, Gy + 1, C + dz, 'aurelia:verdant_ore')
    for (dx, dz) in ((-4, 9), (4, 9), (-11, -4), (11, 1)):
        lamp(g, C + dx, Gy + 1, C + dz)
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block') and math.hypot(x - C, z - C) < 12.5:
                ground_cover(g, x, Gy + 1, z, rnd, 0.7)
    g.ground_guard('aurelia:bramble_sentinel', C - 4, C + 6, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C + 5, C - 3, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C - 6, C - 1, Gy + 1, 3)
    g.ground_guard('aurelia:sporecap', C + 3, C + 8, Gy + 1, 3)
    g.save(name)


def grove_outpost_hamlet(name, seed):
    rnd = random.Random(seed)
    W = L = 43
    C, Gy = W // 2, 3
    g = Grid(W, 22, L)
    grove_ground(g, C, C, Gy, 20, rnd)
    for dx in range(-8, 9):                                                        # the great hall: a giant mushroom
        for dz in range(-8, 9):
            d = math.hypot(dx, dz)
            if 3.0 <= d <= 3.9:
                for k in range(6):
                    if not (abs(dx) <= 0 and dz > 0 and k < 3) and not (k == 3 and (dx == 0 or dz == 0)):
                        g.set(C + dx, Gy + 1 + k, C + dz, 'minecraft:mushroom_stem')
            elif d < 3.0:
                g.set(C + dx, Gy, C + dz, 'minecraft:spruce_planks')
            for k, r in enumerate([7.4, 6.6, 5.4, 3.8, 2.0]):
                if d <= r and (k > 0 or d > 3.9):
                    g.set(C + dx, Gy + 7 + k, C + dz, 'minecraft:red_mushroom_block')
    chest(g, C, Gy + 1, C - 2, 'grove_outpost')
    g.set(C - 2, Gy + 1, C, 'minecraft:crafting_table')
    g.set(C + 2, Gy + 1, C, 'minecraft:barrel', BARREL)
    g.set(C, Gy + 6, C, 'minecraft:shroomlight')
    for i, (deg, cap) in enumerate([(35, 'minecraft:red_mushroom_block'), (145, 'minecraft:brown_mushroom_block'),
                                    (215, 'minecraft:red_mushroom_block'), (325, 'minecraft:brown_mushroom_block')]):
        a = math.radians(deg)
        hx, hz = int(C + 13 * math.cos(a)), int(C + 13 * math.sin(a))
        hut(g, hx, hz, Gy + 1, rnd, cap)
        g.set(hx, Gy, hz, 'minecraft:spruce_planks')
        P(g, hx - 1, Gy + 1, hz - 1, 'minecraft:barrel' if i % 2 else 'minecraft:hay_block', BARREL if i % 2 else LOG_Y)
        for t in range(4, 12):                                                     # paths to the hall
            px, pz = int(round(C + t * math.cos(a))), int(round(C + t * math.sin(a)))
            c = g.get(px, Gy, pz)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block') and g.get(px, Gy + 1, pz) is None:
                g.set(px, Gy, pz, 'minecraft:dirt_path')
    wx, wz = C + 9, C + 1                                                          # a roofed well
    for dx in range(-2, 3):
        for dz in range(-2, 3):
            d = math.hypot(dx, dz)
            if d <= 1.2:
                g.set(wx + dx, Gy, wz + dz, 'minecraft:water', {'level': '0'})
            elif d <= 2.3:
                g.set(wx + dx, Gy, wz + dz, 'minecraft:mossy_cobblestone')
                g.set(wx + dx, Gy + 1, wz + dz, 'minecraft:mossy_cobblestone')
    for (dx, dz) in ((-2, 0), (2, 0)):
        for k in (2, 3):
            g.set(wx + dx, Gy + k, wz + dz, 'minecraft:dark_oak_fence')
    for dx in range(-2, 3):
        g.set(wx + dx, Gy + 4, wz, 'minecraft:spruce_slab', SLAB_B)
    g.set(wx, Gy + 3, wz, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
    gx0, gz0 = C - 11, C - 2                                                       # a fenced berry garden
    for x in range(gx0, gx0 + 6):
        for z in range(gz0, gz0 + 5):
            edge = x in (gx0, gx0 + 5) or z in (gz0, gz0 + 4)
            if g.get(x, Gy, z) and g.get(x, Gy + 1, z) is None:
                if edge:
                    if not (x == gx0 + 5 and z == gz0 + 2):
                        g.set(x, Gy + 1, z, 'minecraft:dark_oak_fence')
                else:
                    g.set(x, Gy, z, 'minecraft:rooted_dirt')
                    g.set(x, Gy + 1, z, 'minecraft:sweet_berry_bush', {'age': str(rnd.choice([1, 2, 3]))})
    sx0, sz0 = C - 3, C + 9                                                        # a market stall with a striped awning
    for (dx, dz) in ((0, 0), (4, 0), (0, 2), (4, 2)):
        for k in (1, 2, 3):
            P(g, sx0 + dx, Gy + k, sz0 + dz, 'minecraft:dark_oak_fence')
    for dx in range(5):
        for dz in range(3):
            P(g, sx0 + dx, Gy + 4, sz0 + dz, 'minecraft:red_wool' if dx % 2 == 0 else 'minecraft:white_wool')
    for dx in (1, 2, 3):
        P(g, sx0 + dx, Gy + 1, sz0, 'minecraft:barrel', BARREL)
    P(g, sx0 + 2, Gy + 2, sz0, 'minecraft:red_mushroom')
    for (dx, dz) in ((5, 6), (-5, 6), (6, -6), (-6, -7), (0, -9), (13, 7), (-14, 5)):
        lamp(g, C + dx, Gy + 1, C + dz)
    for (dx, dz) in ((15, 6), (-15, 4), (4, -15), (-9, 12)):
        P(g, C + dx, Gy + 1, C + dz, 'aurelia:verdant_ore')
    for _ in range(5):
        a = rnd.uniform(0, 6.28)
        mx, mz = int(C + 17 * math.cos(a)), int(C + 17 * math.sin(a))
        if g.get(mx, Gy, mz) and all(g.get(mx + i, Gy + 1, mz + j) is None for i in (-1, 0, 1) for j in (-1, 0, 1)):
            mushroom(g, mx, Gy + 1, mz, rnd)
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                ground_cover(g, x, Gy + 1, z, rnd, 1.0)
    for (dx, dz) in ((-4, 5), (5, 4), (-3, -7), (7, -5)):
        g.ground_guard('aurelia:sporecap', C + dx, C + dz, Gy + 1, 3)
    g.ground_guard('aurelia:rootstalker', C + 10, C + 10, Gy + 1, 3)
    g.ground_guard('aurelia:bramble_sentinel', C, C + 6, Gy + 1, 3)
    g.save(name)


def hollow_outpost_fort(name, seed):
    rnd = random.Random(seed)
    F = 20
    W = L = 43
    C = W // 2
    PB, CPB, CHI = 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks', 'minecraft:chiseled_polished_blackstone'
    g = Grid(W, F + 26, L)
    hollow_plug(g, C, F, 20, rnd)
    brick = lambda: CPB if rnd.random() < 0.15 else PB
    for x in range(C - 14, C + 15):                                                # curtain wall with battlements and a south gate
        for z in range(C - 14, C + 15):
            m = max(abs(x - C), abs(z - C))
            if m == 14 and g.get(x, F - 1, z):
                gate = z == C + 14 and abs(x - C) <= 1
                for k in range(7):
                    if not (gate and k < 4):
                        g.set(x, F + k, z, brick())
                if (x + z) % 2 == 0:
                    g.set(x, F + 7, z, PB)
            if m == 13 and g.get(x, F - 1, z) and not (z == C + 13 and abs(x - C) <= 1):
                g.set(x, F + 5, z, 'minecraft:polished_blackstone_brick_slab', SLAB_B)   # wall-walk
    for sx in (-2, 2):
        for k in range(9):
            g.set(C + sx, F + k, C + 14, CHI)
        g.set(C + sx, F + 9, C + 14, 'minecraft:soul_lantern', STANDING)
        P(g, C + sx, F + 5, C + 15, 'minecraft:red_wall_banner', {'facing': 'south'})
    for x in (C - 1, C, C + 1):
        g.set(x, F + 4, C + 14, 'minecraft:iron_bars')
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):                           # round corner turrets with fire on top
        tx, tz = C + sx * 14, C + sz * 14
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                d = math.hypot(dx, dz)
                if d <= 2.6 and g.get(tx + dx, F - 1, tz + dz) is not None or d <= 2.6:
                    for k in range(-3, 11):
                        if d >= 1.5 or k in (-3, 10):
                            g.set(tx + dx, F + k, tz + dz, CHI if k in (4, 10) else brick())
                    if d >= 1.9 and (dx + dz) % 2 == 0:
                        g.set(tx + dx, F + 11, tz + dz, WALLB)
        g.set(tx, F + 11, tz, 'minecraft:soul_campfire', CAMP)
    for dx in range(-4, 5):                                                        # the keep: three floors, windows, battlements
        for dz in range(-4, 5):
            edge = max(abs(dx), abs(dz)) == 4
            x, z = C + dx, C - 3 + dz
            for k in range(17):
                if edge:
                    win = k in (8, 9, 13) and (dx == 0 or dz == 0)
                    g.set(x, F + k, z, 'minecraft:orange_stained_glass' if win else CHI if k in (5, 11, 16) else brick())
                elif k in (5, 11, 16):
                    g.set(x, F + k, z, 'minecraft:polished_blackstone')
                else:
                    g.set(x, F + k, z, AIR)
            if edge and (dx + dz) % 2 == 0:
                g.set(x, F + 17, z, PB)
                if abs(dx) == 4 and abs(dz) == 4:
                    g.set(x, F + 18, z, WALLB)
                    g.set(x, F + 19, z, 'minecraft:soul_lantern', STANDING)
    for k in range(3):
        for dx in (-1, 0, 1):
            g.set(C + dx, F + k, C + 1, AIR)
    for k in range(17):
        g.set(C + 3, F + k, C - 6, 'minecraft:ladder', ladder('south'))
    chest(g, C - 2, F + 17, C - 3, 'hollow_outpost', 'east')
    g.set(C - 3, F, C - 6, 'minecraft:smithing_table')
    g.set(C - 2, F, C - 6, 'minecraft:anvil', {'facing': 'north'})
    g.set(C - 3, F + 6, C - 6, 'minecraft:barrel', BARREL)
    g.set(C - 3, F + 6, C - 5, 'minecraft:barrel', BARREL)
    g.set(C, F + 4, C - 3, 'minecraft:soul_lantern', HANGING)
    g.set(C, F + 10, C - 3, 'minecraft:soul_lantern', HANGING)
    fx, fz = C + 9, C - 9                                                          # the forge
    g.set(fx, F, fz, 'minecraft:blast_furnace', {'facing': 'south', 'lit': 'true'})
    g.set(fx - 1, F, fz, 'minecraft:lava_cauldron')
    g.set(fx + 1, F, fz, 'minecraft:anvil', {'facing': 'east'})
    for k in range(1, 5):
        g.set(fx, F + k, fz, PB)
    g.set(fx, F + 5, fz, 'minecraft:campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'true', 'waterlogged': 'false'})
    for dx in range(3):                                                            # prison cages
        for dz in range(3):
            for k in range(3):
                if dx != 1 or dz != 1:
                    P(g, C - 11 + dx, F + k, C - 10 + dz, 'minecraft:iron_bars')
            P(g, C - 11 + dx, F + 3, C - 10 + dz, 'minecraft:polished_blackstone_brick_slab', SLAB_B)
    g.set(C - 10, F, C - 9, 'minecraft:bone_block', LOG_Y)
    for (dx, dz) in ((8, 6), (-8, 7)):                                             # sunken lava pools
        for i in (0, 1):
            for j in (0, 1):
                g.set(C + dx + i, F - 1, C + dz + j, 'minecraft:lava', {'level': '0'})
    for (dx, dz) in ((-5, 9), (5, 9), (-10, 2), (10, 1), (6, -11)):
        pike(g, C + dx, F, C + dz, rnd)
    for (dx, dz) in ((-11, 10), (11, 10), (-4, 11), (4, 11)):
        P(g, C + dx, F, C + dz, 'minecraft:soul_campfire', CAMP)
    for (dx, dz) in ((0, 16), (1, 18)):
        if g.get(C + dx, F - 1, C + dz):
            g.set(C + dx, F - 1, C + dz, 'aurelia:ember_vent')
    for (dx, dz) in ((12, -3), (-12, -4), (3, 12)):
        P(g, C + dx, F, C + dz, 'aurelia:emberheart_ore')
    g.ground_guard('aurelia:ashbound_knight', C, C + 8, F, 3)
    g.ground_guard('aurelia:cinder_hound', C - 7, C + 4, F, 3)
    g.ground_guard('aurelia:cinder_hound', C + 7, C + 4, F, 3)
    g.ground_guard('aurelia:soul_jailer', C + 5, C - 10, F, 3)
    g.save(name)


def hollow_outpost_shrine(name, seed):
    rnd = random.Random(seed)
    F = 18
    W = L = 37
    C = W // 2
    PB, CHI = 'minecraft:polished_blackstone_bricks', 'minecraft:chiseled_polished_blackstone'
    g = Grid(W, F + 20, L)
    hollow_plug(g, C, F, 17, rnd)
    for x in range(W):                                                             # a ring of soul sand with wither roses and soul fire
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 6.5 <= d <= 8.6 and g.get(x, F - 1, z):
                g.set(x, F - 1, z, 'minecraft:soul_soil' if rnd.random() < 0.6 else 'minecraft:soul_sand')
                roll = rnd.random()
                if roll < 0.14:
                    g.set(x, F, z, 'minecraft:wither_rose')
                elif roll < 0.22 and g.get(x, F - 1, z)[0] == 'minecraft:soul_soil':
                    g.set(x, F, z, 'minecraft:soul_fire')
    for k in range(8):                                                             # obsidian pillars with lantern arms
        a = k * math.pi / 4 + math.pi / 8
        px, pz = int(round(C + 11 * math.cos(a))), int(round(C + 11 * math.sin(a)))
        h = 7 + (k % 2) * 4
        for j in range(h):
            g.set(px, F + j, pz, 'minecraft:crying_obsidian' if j % 4 == 3 else 'minecraft:obsidian')
        g.set(px, F + h, pz, 'minecraft:soul_campfire', CAMP)
        ix, iz = px - int(round(math.cos(a))), pz - int(round(math.sin(a)))
        g.set(ix, F + h - 1, iz, WALLB)
        g.set(ix, F + h - 2, iz, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
        g.set(ix, F + h - 3, iz, 'minecraft:soul_lantern', HANGING)
    for t, half in enumerate([5, 4, 3]):                                           # the stepped dais and altar
        for dx in range(-half, half + 1):
            for dz in range(-half, half + 1):
                g.set(C + dx, F + t, C + dz, CHI if max(abs(dx), abs(dz)) == half and (dx + dz) % 3 == 0 else PB)
    for (dx, dz) in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        for k in range(3, 7):
            g.set(C + dx, F + k, C + dz, 'minecraft:obsidian')
        g.set(C + dx, F + 7, C + dz, 'minecraft:soul_lantern', STANDING)
    g.set(C, F + 3, C, 'minecraft:crying_obsidian')
    chest(g, C, F + 4, C, 'hollow_outpost')
    for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        g.set(C + dx, F + 3, C + dz, 'minecraft:black_candle', {'candles': str(rnd.randint(2, 4)), 'lit': 'true', 'waterlogged': 'false'})
    for sx in (-2, 2):                                                             # a gate arch on the south approach
        for k in range(6):
            g.set(C + sx, F + k, C + 13, CHI)
    for x in range(C - 2, C + 3):
        g.set(x, F + 6, C + 13, CHI)
    g.set(C, F + 5, C + 13, 'minecraft:soul_lantern', HANGING)
    for (dx, dz) in ((-9, 2), (9, -1), (5, 12), (-5, 12), (-12, -6), (12, 6)):
        if g.get(C + dx, F - 1, C + dz):
            pike(g, C + dx, F, C + dz, rnd)
    for (dx, dz) in ((-10, -9), (10, -9), (0, -13), (13, 0)):
        if g.get(C + dx, F - 1, C + dz):
            P(g, C + dx, F, C + dz, 'minecraft:bone_block', {'axis': rnd.choice(['x', 'z'])})
            P(g, C + dx + 1, F, C + dz, 'aurelia:emberheart_ore')
    g.ground_guard('aurelia:soul_jailer', C + 6, C + 1, F, 3)
    g.ground_guard('aurelia:soul_jailer', C - 6, C - 1, F, 3)
    g.ground_guard('aurelia:cinder_hound', C, C + 10, F, 3)
    g.save(name)


# ---- two more Grove ruins: a tower stump and a fallen colonnade
def ruin_stump(name, seed):
    rnd = random.Random(seed)
    W = L = 23
    Gy, C = 3, 11
    g = Grid(W, 22, L)
    grove_ground(g, C, C, Gy, 10, rnd)
    brick = lambda: rnd.choice(['minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks', 'minecraft:mossy_cobblestone'])
    for dx in range(-6, 7):
        for dz in range(-6, 7):
            d = math.hypot(dx, dz)
            ang = math.atan2(dz, dx)
            if 4.0 <= d <= 5.2:
                top = int(7 + 6 * (0.5 + 0.5 * math.sin(ang * 1.0 + 1.0)) + rnd.randint(-1, 1))
                for k in range(top):
                    if not (abs(dx) <= 1 and dz > 0 and k < 3) and not (k in (5, 6) and abs(math.sin(ang * 3)) > 0.95):
                        g.set(C + dx, Gy + 1 + k, C + dz, brick())
            elif d < 4.0:
                g.set(C + dx, Gy, C + dz, 'minecraft:stone_bricks' if rnd.random() < 0.5 else 'minecraft:moss_block')
    for i in range(14):                                                            # a broken inner stair
        a = i * 0.45
        g.set(C + 3 * math.cos(a), Gy + 1 + i // 2, C + 3 * math.sin(a), 'minecraft:stone_brick_slab', {'type': 'bottom' if i % 2 == 0 else 'top', 'waterlogged': 'false'})
    P(g, C, Gy + 1, C, 'minecraft:mossy_cobblestone')
    P(g, C, Gy + 2, C, 'minecraft:lantern', STANDING)
    P(g, C + 2, Gy + 1, C - 2, 'aurelia:verdant_ore')
    for _ in range(10):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(6, 9)
        P(g, C + r * math.cos(a), Gy + 1, C + r * math.sin(a), brick())
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                ground_cover(g, x, Gy + 1, z, rnd, 1.3)
    add_vines(g, rnd, Gy + 2, Gy + 16, 0.25, only={'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:mossy_cobblestone', 'minecraft:cracked_stone_bricks'})
    g.save(name)


def ruin_colonnade(name, seed):
    rnd = random.Random(seed)
    W, L, H = 33, 17, 16
    Gy = 3
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            if math.hypot((x - 16) / 16.0, (z - 8) / 8.0) <= 1:
                for y in range(Gy):
                    g.set(x, y, z, 'minecraft:dirt')
                g.set(x, Gy, z, 'minecraft:moss_block' if rnd.random() < 0.35 else 'minecraft:grass_block', None)
    g.b = {k: ((v[0], (('snowy', 'false'),) if v[0] == 'minecraft:grass_block' else v[1], v[2])) for k, v in g.b.items()}
    for x in range(5, 28):
        for z in (6, 7, 8, 9, 10):
            if g.get(x, Gy, z) and rnd.random() < 0.7:
                g.set(x, Gy, z, rnd.choice(['minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:cracked_stone_bricks']))
    for i, x in enumerate(range(6, 28, 4)):
        for z in (5, 11):
            standing = rnd.random() < 0.6
            h = rnd.randint(5, 8) if standing else rnd.randint(1, 2)
            for k in range(h):
                g.set(x, Gy + 1 + k, z, 'minecraft:quartz_pillar' if rnd.random() < 0.2 else 'minecraft:stone_bricks' if k % 3 else 'minecraft:chiseled_stone_bricks', LOG_Y if False else None)
            if standing and rnd.random() < 0.6:
                g.set(x, Gy + 1 + h, z, 'minecraft:mossy_stone_brick_slab', SLAB_B)
            if not standing:                                                       # the fallen shaft lies beside its base
                dz = 1 if z == 5 else -1
                for k in range(1, rnd.randint(3, 5)):
                    P(g, x + (k if i % 2 else -k), Gy + 1, z + 2 * dz, 'minecraft:stone_bricks')
    for x in (6, 10):                                                              # one surviving lintel
        pass
    for x in range(6, 11):
        if g.get(6, Gy + 5, 5) and g.get(10, Gy + 5, 5):
            P(g, x, Gy + 6, 5, 'minecraft:mossy_stone_bricks')
    P(g, 16, Gy + 1, 8, 'minecraft:chiseled_stone_bricks')
    P(g, 16, Gy + 2, 8, 'minecraft:lantern', STANDING)
    P(g, 20, Gy + 1, 8, 'aurelia:verdant_ore')
    for x in range(W):
        for z in range(L):
            c = g.get(x, Gy, z)
            if c and c[0] in ('minecraft:grass_block', 'minecraft:moss_block'):
                ground_cover(g, x, Gy + 1, z, rnd, 1.3)
    add_vines(g, rnd, Gy + 2, Gy + 12, 0.3, only={'minecraft:stone_bricks', 'minecraft:mossy_stone_bricks', 'minecraft:chiseled_stone_bricks', 'minecraft:quartz_pillar'})
    g.save(name)


# ---- richer ziggurats and arches: these wrap the base builders and decorate the saved grid before it is written
_base_ziggurat, _base_arch = ziggurat, arch


def ziggurat(name, base, tiers, seed):
    rnd = random.Random(seed + 500)
    saved = Grid.save

    def decorate(self, nm):
        C, F = self.W // 2, 20
        ty = F + tiers * 5
        for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):                       # a pillared temple on the summit
            for k in range(6):
                self.set(C + sx * 4, ty + k, C + sz * 4, 'minecraft:polished_blackstone' if k % 5 else 'minecraft:chiseled_polished_blackstone')
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                m = max(abs(dx), abs(dz))
                if m <= 5:
                    P(self, C + dx, ty + 6, C + dz, 'minecraft:polished_blackstone_brick_slab', SLAB_B) if m == 5 else P(self, C + dx, ty + 6, C + dz, 'minecraft:polished_blackstone_bricks')
                if m <= 3:
                    P(self, C + dx, ty + 7, C + dz, 'minecraft:deepslate_tiles')
                if m <= 1:
                    P(self, C + dx, ty + 8, C + dz, 'minecraft:deepslate_tiles')
        P(self, C, ty + 9, C, 'minecraft:soul_lantern', STANDING)
        P(self, C + 1, ty, C + 1, 'aurelia:emberheart_ore')
        P(self, C - 1, ty, C - 1, 'aurelia:emberheart_ore')
        for t in range(tiers):                                                     # obelisks on every tier corner, banners by the stairs
            hs = base // 2 - 3 * t
            y0 = F + 5 * t + 5
            for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                x, z = C + sx * hs, C + sz * hs
                for k in range(3):
                    P(self, x, y0 + k, z, WALLB)
                P(self, x, y0 + 3, z, 'minecraft:soul_lantern', STANDING)
            if t % 2 == 0:
                for sx in (-4, 4):
                    pike(self, C + sx, y0, C + hs - 1, rnd)
                    pike(self, C + sx, y0, C - hs + 1, rnd)
        saved(self, nm)
    Grid.save = decorate
    try:
        _base_ziggurat(name, base, tiers, seed)
    finally:
        Grid.save = saved


def arch(name, span, seed):
    rnd = random.Random(seed + 500)
    saved = Grid.save

    def decorate(self, nm):
        C = self.L // 2
        for i in range(span + 1):
            t = i / span
            x = self.W // 2 - span // 2 + i
            deck = 22 + int(round(8 * math.sin(math.pi * t)))
            if i % 5 == 2:                                                         # lanterns on chains under the deck
                for k in range(6, 6 + rnd.randint(2, 5)):
                    P(self, x, deck - k, C, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
                for k in range(14, 5, -1):
                    c = self.get(x, deck - k, C)
                    if c and c[0] == 'minecraft:chain':
                        P(self, x, deck - k - 1, C, 'minecraft:soul_lantern', HANGING)
                        break
            if i in (3, span - 3):
                pike(self, x, deck + 1, C - 2, rnd)
                pike(self, x, deck + 1, C + 2, rnd)
        for sx in (-1, 1):                                                         # a small gate arch at each end
            px = self.W // 2 + sx * (span // 2)
            for z in (C - 3, C + 3):
                for k in range(1, 7):
                    P(self, px, 22 + k, z, 'minecraft:chiseled_polished_blackstone')
            for z in range(C - 3, C + 4):
                P(self, px, 29, z, 'minecraft:polished_blackstone_bricks')
            P(self, px, 28, C, 'minecraft:soul_lantern', HANGING)
        saved(self, nm)
    Grid.save = decorate
    try:
        _base_arch(name, span, seed)
    finally:
        Grid.save = saved


if __name__ == '__main__':
    for i, (R, seed) in enumerate([(30, 11), (28, 12)]):
        island(f'sky_island_large_{i}', R, seed, 'large')
    island('sky_island_castle_0', 38, 21, 'castle')
    for i, (R, seed) in enumerate([(16, 31), (14, 32), (18, 33)]):
        island(f'sky_island_medium_{i}', R, seed, 'medium')
    for i, (R, seed) in enumerate([(8, 41), (7, 42), (9, 43)]):
        island(f'sky_island_small_{i}', R, seed, 'small')
    for i, (Rb, Hh, seed) in enumerate([(9, 46, 51), (11, 58, 52), (8, 70, 53), (12, 40, 54)]):
        pillar(f'grove_pillar_{i}', Rb, Hh, seed)
    for i in range(3):
        ruin(f'grove_ruin_{i}', 60 + i)
    for i, (base, tiers, seed) in enumerate([(40, 5, 71), (32, 4, 72)]):
        ziggurat(f'hollow_ziggurat_{i}', base, tiers, seed)
    for i, (span, seed) in enumerate([(40, 81), (34, 82)]):
        arch(f'hollow_arch_{i}', span, seed)
    for i in range(5):
        stalactite(f'hollow_stalactite_{i}', 90 + i)
    island('sky_outpost_0', 18, 101, 'outpost')
    island('sky_outpost_1', 16, 102, 'shrine')
    grove_outpost_tower('grove_outpost_0', 111)
    grove_outpost_hamlet('grove_outpost_1', 112)
    hollow_outpost_fort('hollow_outpost_0', 121)
    hollow_outpost_shrine('hollow_outpost_1', 122)
    ruin_stump('grove_ruin_3', 63)
    ruin_colonnade('grove_ruin_4', 64)
