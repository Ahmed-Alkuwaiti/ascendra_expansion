"""Structures that fill the two act three realms (placed by the structure sets written in gen_act3_data.py).

Clockwork Rift: torn-off fragments of gothic keeps adrift in the void, clock spires, broken bridges hung on chains, and Hour Warden outposts.
Mycelial Deep:  giant magenta-capped fungal towers, root arches, and bone shrines of the Spore Choir.
"""
import math
import random

import gen_act3_citadels as c3
from gen_act3_citadels import (AIR, Grid, bez, blob, cap, chain, chest, clock_face, cone, cyl, gear, lantern, stairs)

DB, DT, PD = 'minecraft:deepslate_bricks', 'minecraft:deepslate_tiles', 'minecraft:polished_deepslate'
PBB, GOLD, PG, CO = 'minecraft:polished_blackstone_bricks', 'minecraft:gold_block', 'minecraft:purple_stained_glass', 'minecraft:crying_obsidian'
PEARL = 'minecraft:pearlescent_froglight'
BONE, CAL, STEM = 'minecraft:bone_block', 'minecraft:calcite', 'minecraft:mushroom_stem'
ROOTS, MROOT = 'minecraft:mangrove_roots', 'minecraft:muddy_mangrove_roots'


def rocky(rnd):
    def pick(x, y, z):
        r = rnd.random()
        return 'minecraft:deepslate' if r < 0.45 else ('minecraft:tuff' if r < 0.7 else ('minecraft:cobbled_deepslate' if r < 0.93 else CO))
    return pick


def masonry(rnd):
    def pick(x, y, z):
        r = rnd.random()
        return DB if r < 0.6 else ('minecraft:cracked_deepslate_bricks' if r < 0.8 else (DT if r < 0.93 else PD))
    return pick


def island(g, cx, cy, cz, r, rnd, depth=1.9, top='minecraft:deepslate_tiles'):
    """An inverted rock cone torn out of the ground, flat on top."""
    pick = rocky(rnd)
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d > r:
                continue
            dep = int((r - d) * depth + rnd.uniform(0, 2))
            for y in range(cy - dep, cy + 1):
                g.set(x, y, z, top if y == cy else pick(x, y, z))
            if rnd.random() < 0.08 and dep > 2:
                g.set(x, cy - dep - 1, z, 'minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': 'down', 'waterlogged': 'false'})


def gothic_wall(g, x0, z0, x1, z1, y0, h, rnd, windows=True, broken=0.0):
    pick = masonry(rnd)
    n = max(abs(x1 - x0), abs(z1 - z0))
    for k in range(n + 1):
        x = x0 + (x1 - x0) * k // max(n, 1)
        z = z0 + (z1 - z0) * k // max(n, 1)
        top = h - (int(rnd.uniform(0, h * broken) * (abs(k - n / 2) / (n / 2 + 0.1))) if broken else 0)
        for y in range(y0, y0 + top):
            win = windows and k % 4 == 2 and y0 + 3 <= y <= y0 + 7
            g.set(x, y, z, PG if win else pick(x, y, z))
        if not broken and k % 2 == 0:
            g.set(x, y0 + top, z, PBB)


# ============================================================================================ Clockwork Rift
def rift_fragment(seed):
    """A torn-off corner of a keep: a rock island with a broken tower, a wall stub, a gear half-buried and chains trailing."""
    rnd = random.Random(seed)
    W = L = 29
    H = 50
    C = 14
    g = Grid(W, H, L)
    Y = 18
    island(g, C, Y, C, 11 + rnd.random() * 2, rnd)
    tx, tz = C + rnd.choice((-4, 4)), C + rnd.choice((-4, 4))
    th = 18 + rnd.randint(0, 10)
    cyl(g, tx, tz, 4, Y + 1, Y + th, masonry(rnd), hollow=1.2)
    for y in range(Y + th - 5, Y + th + 1):                         # the broken crown: jagged
        for x in range(tx - 4, tx + 5):
            for z in range(tz - 4, tz + 5):
                if g.get(x, y, z) and g.get(x, y, z)[0] != AIR and rnd.random() < (y - (Y + th - 6)) / 7:
                    g.set(x, y, z, AIR)
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        for y in (Y + 6, Y + 7, Y + 13, Y + 14):
            g.set(round(tx + 4 * math.cos(a)), y, round(tz + 4 * math.sin(a)), PG)
    gothic_wall(g, C - 9, C + rnd.choice((-3, 3)), C + 8, C + rnd.choice((-3, 3)), Y + 1, 9, rnd, broken=0.8)
    face = rnd.choice(['s', 'e'])
    gear(g, C + (2 if face == 's' else 9), Y + 1, C + (9 if face == 's' else 0), face, 5, 10, depth=0)
    clock_face(g, tx, Y + th - 9, tz + 4 if face == 's' else tz, face if face == 's' else 's', 3, hour=rnd.randint(0, 11), minute=rnd.randint(0, 59),
               rim='minecraft:gold_block')
    for (cx, cz) in [(C - 7, C + 2), (C + 6, C - 5), (C + 1, C + 8)]:
        top = None
        for y in range(Y, 0, -1):
            if g.get(cx, y, cz) is None:
                top = y
                break
        if top:
            chain(g, cx, max(1, top - rnd.randint(4, 12)), top, cz)
    lantern(g, C, Y + 1, C, soul=True)
    g.save(f'rift_fragment_{seed % 10}')


def rift_spire(seed):
    """A needle spire floating free, a clock face on each side, glowing purple at the root."""
    rnd = random.Random(seed)
    W = L = 23
    H = 82
    C = 11
    g = Grid(W, H, L)
    Y = 16
    island(g, C, Y, C, 8, rnd, depth=2.0)
    for x in range(C - 5, C + 6):
        for z in range(C - 5, C + 6):
            edge = abs(x - C) == 5 or abs(z - C) == 5
            corner = abs(x - C) == 5 and abs(z - C) == 5
            for y in range(Y + 1, Y + 40):
                if edge:
                    g.set(x, y, z, PBB if corner else masonry(rnd)(x, y, z))
                elif y in (Y + 1, Y + 20):
                    g.set(x, y, z, PD)
                else:
                    g.set(x, y, z, AIR)
    hour = rnd.randint(0, 11)
    for (face, cx, cz) in [('s', C, C + 6), ('n', C, C - 6), ('e', C + 6, C), ('w', C - 6, C)]:
        clock_face(g, cx, Y + 31, cz, face, 4, hour=hour, minute=rnd.randint(0, 59))
        for k in range(3):
            g.set(cx if face in 'ns' else cx, Y + 6 + k, cz, PG)
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            g.set(x, Y + 40, z, PBB)
    cone(g, C, C, 6.0, Y + 41, 24, lambda x, y, z: DT if y % 5 else GOLD, power=1.3)
    for y in range(Y + 65, Y + 70):
        g.set(C, y, C, GOLD)
    blob(g, C, Y + 71, C, 1.3, 1.3, 1.3, CO)
    for (cx, cz) in [(C - 5, C - 5), (C + 5, C - 5), (C - 5, C + 5), (C + 5, C + 5)]:
        for y in range(Y + 40, Y + 47):
            g.set(cx, y, cz, PBB if y < Y + 46 else GOLD)
    for x in range(C - 1, C + 2):                                    # a doorway on the south face
        for y in range(Y + 2, Y + 6):
            g.set(x, y, C + 5, AIR)
    for y in range(Y + 2, Y + 20):                                   # a ladder up the inside to the first floor
        g.set(C, y, C - 4, 'minecraft:ladder', {'facing': 'south', 'waterlogged': 'false'})
    g.set(C, Y + 20, C - 4, AIR)
    lantern(g, C + 2, Y + 21, C + 2, soul=True)
    g.save(f'rift_spire_{seed % 10}')


def rift_bridge(seed):
    """A span of a broken bridge between two pier-stubs, hung from chains, with gaps you must jump."""
    rnd = random.Random(seed)
    W, L = 13, 49
    H = 40
    C = 6
    g = Grid(W, H, L)
    Y = 22
    for end in (4, L - 5):
        island(g, C, Y - 1, end, 5, rnd)
        for x in range(C - 3, C + 4):
            for y in range(Y - 1, Y + 8):
                g.set(x, y, end, masonry(rnd)(x, y, end) if abs(x - C) >= 2 or y > Y + 5 else AIR)
        g.set(C - 3, Y + 8, end, GOLD)
        g.set(C + 3, Y + 8, end, GOLD)
    for z in range(4, L - 4):
        sag = int(2 * math.sin(math.pi * (z - 4) / (L - 9)))
        gap = (L // 2 - 2 <= z <= L // 2) and seed % 2 == 0 or (z in (17, 31) and seed % 2 == 1)
        if gap:
            continue
        for x in range(C - 2, C + 3):
            g.set(x, Y - sag, z, PBB if abs(x - C) < 2 else DB)
            if rnd.random() < 0.06 and abs(x - C) == 2:
                g.set(x, Y - sag, z, AIR)
        for x in (C - 3, C + 3):
            g.set(x, Y - sag, z, DB)
            if z % 2 == 0:
                g.set(x, Y - sag + 1, z, 'minecraft:polished_blackstone_brick_wall')
        g.set(C, Y - sag - 1, z, DB)
        if z % 6 == 0:
            for x in (C - 3, C + 3):
                chain(g, x, Y - sag + 2, H - 1, z)
            lantern(g, C - 3, Y - sag + 2, z, soul=True, hanging=False) if z % 12 == 0 else None
    gear(g, C + 4, Y - 6, L // 2, 'e', 3, 8, block=GOLD, depth=0)
    g.save(f'rift_bridge_{seed % 10}')


def rift_outpost(seed):
    """An Hour Warden's watch-post: a small keep on an island, a clock over the door, a chest, guards."""
    rnd = random.Random(seed)
    W = L = 31
    H = 48
    C = 15
    g = Grid(W, H, L)
    Y = 16
    island(g, C, Y, C, 13, rnd)
    pick = masonry(rnd)
    X0, X1, Z0, Z1 = C - 6, C + 6, C - 6, C + 6
    for x in range(X0, X1 + 1):
        for z in range(Z0, Z1 + 1):
            edge = x in (X0, X1) or z in (Z0, Z1)
            for y in range(Y + 1, Y + 13):
                if edge:
                    win = (x + z) % 4 == 0 and Y + 4 <= y <= Y + 8
                    g.set(x, y, z, PG if win else pick(x, y, z))
                else:
                    g.set(x, y, z, AIR)
            g.set(x, Y, z, PD)
    for k in range(8):
        for x in range(X0 - 1 + k, X1 + 2 - k):
            for z in (Z0 - 1, Z1 + 1):
                pass
        for z in range(Z0 - 1, Z1 + 2):
            g.set(X0 - 1 + k, Y + 13 + k, z, DT)
            g.set(X1 + 1 - k, Y + 13 + k, z, DT)
        for x in range(X0 - 1 + k, X1 + 2 - k):
            g.set(x, Y + 13 + k, Z0, pick(x, 0, 0))
            g.set(x, Y + 13 + k, Z1, pick(x, 0, 0))
    for (tx, tz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
        cyl(g, tx, tz, 2, Y + 1, Y + 18, PBB)
        cone(g, tx, tz, 2.5, Y + 19, 7, DT)
        g.set(tx, Y + 26, tz, GOLD)
    for x in range(C - 1, C + 2):
        for y in range(Y + 1, Y + 5):
            g.set(x, y, Z1, AIR)
    clock_face(g, C, Y + 9, Z1 + 1, 's', 3, hour=rnd.randint(0, 11), rim=GOLD)
    chest(g, C, Y + 1, Z0 + 1, 'aurelia:chests/rift_outpost', 'south')
    g.set(C - 2, Y + 1, Z0 + 1, 'minecraft:purple_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
    g.set(C, Y + 1, C + 2, 'aurelia:time_snare')
    lantern(g, C, Y + 12, C, soul=True, hanging=True)
    gear(g, X0 - 1, Y + 7, C, 'w', 3, 8, depth=0)
    g.ground_guard('aurelia:hour_warden', C - 3, C, Y + 1, 3)
    g.ground_guard('aurelia:gearskitter', C + 9, C + 9, Y + 1, 3)
    g.ground_guard('aurelia:gearskitter', C - 9, C - 8, Y + 1, 3)
    g.air_guard('aurelia:secondhand', C + 3, Y + 4, C - 2)
    g.save(f'rift_outpost_{seed % 10}')


# ============================================================================================ Mycelial Deep
def capblock(x, y, z, d=0):
    h = (x * 7 + y * 13 + z * 5) % 23
    if h in (0, 11):
        return PEARL
    if h in (5, 17):
        return 'minecraft:white_concrete'
    return ['minecraft:magenta_terracotta', 'minecraft:magenta_concrete', 'minecraft:magenta_wool'][(x + 2 * z + y) % 3]


def fungal_tower(seed):
    """A giant glowing mushroom with a twisting stem, shelf fungi up its side, smaller caps clustered at its foot."""
    rnd = random.Random(seed)
    W = L = 33
    H = 56
    C = 16
    g = Grid(W, H, L)
    h = 30 + rnd.randint(0, 14)
    r = 9 + rnd.randint(0, 4)
    lean = (rnd.uniform(-3, 3), rnd.uniform(-3, 3))
    top = (C + lean[0], 3 + h, C + lean[1])
    bez(g, (C, 0, C), (C - lean[0], h * 0.5, C - lean[1]), top, lambda t: 2.8 - 1.2 * t, STEM)
    for k in range(6):                                                # root flare
        a = k * math.pi / 3 + rnd.uniform(0, 0.4)
        bez(g, (C, 4, C), (C + 4 * math.cos(a), 2, C + 4 * math.sin(a)), (C + 8 * math.cos(a), -1, C + 8 * math.sin(a)), 1.3, ROOTS)
    cap(g, top[0], top[1], top[2], r, r * 0.6, capblock, gill='minecraft:pink_terracotta')
    for k in range(3):                                                # shelf fungi
        t = 0.3 + 0.2 * k
        a = rnd.uniform(0, 2 * math.pi)
        px, py, pz = C + lean[0] * t + 2.8 * math.cos(a), 3 + h * t, C + lean[1] * t + 2.8 * math.sin(a)
        for x in range(int(px) - 3, int(px) + 4):
            for z in range(int(pz) - 3, int(pz) + 4):
                if math.hypot(x - px - math.cos(a), z - pz - math.sin(a)) < 2.8:
                    g.set(x, int(py), z, 'minecraft:pink_terracotta' if rnd.random() < 0.7 else PEARL)
    for k in range(4):                                                # little caps at the foot
        a = rnd.uniform(0, 2 * math.pi)
        mx, mz = C + 9 * math.cos(a), C + 9 * math.sin(a)
        mh = rnd.randint(4, 8)
        cyl(g, mx, mz, 0.8, 0, mh, STEM)
        cap(g, mx, mh, mz, 3 + rnd.random() * 1.5, 2, capblock)
    for k in range(5):
        a = rnd.uniform(0, 2 * math.pi)
        g.set(round(top[0] + (r - 3) * math.cos(a)), int(top[1]) - 1, round(top[2] + (r - 3) * math.sin(a)), 'minecraft:spore_blossom')
    g.save(f'fungal_tower_{seed % 10}')


def root_arch(seed):
    """Two great roots rising from the floor and meeting overhead, glowing nodes along them, caps sprouting from the crown."""
    rnd = random.Random(seed)
    W, L = 45, 15
    H = 34
    C = 7
    g = Grid(W, H, L)
    span = 34 + rnd.randint(0, 6)
    a, b = (W - span) // 2, (W + span) // 2
    peak = 22 + rnd.randint(0, 6)

    def pick(x, y, z):
        r = rnd.random()
        return MROOT if r < 0.2 else (ROOTS if r < 0.55 else STEM if r < 0.95 else PEARL)
    for strand in range(3):
        dz = (strand - 1) * 2
        bez(g, (a, 0, C + dz), (W / 2 + rnd.uniform(-4, 4), peak * 1.9, C + dz * 2), (b, 0, C - dz), lambda t: 2.2 - 0.9 * math.sin(math.pi * t), pick)
    for k in range(3):
        x = W // 2 + rnd.randint(-6, 6)
        cyl(g, x, C, 0.8, peak - 2, peak + 3, STEM)
        cap(g, x, peak + 3, C, 3.5, 2, capblock)
    for k in range(10):                                              # hanging roots under the arch
        x = rnd.randint(a + 6, b - 6)
        z = C + rnd.randint(-2, 2)
        for y in range(peak - 2, 0, -1):
            if g.get(x, y, z) is None:
                if g.get(x, y + 1, z) is not None and g.get(x, y + 1, z)[0] != 'minecraft:hanging_roots':
                    g.set(x, y, z, 'minecraft:hanging_roots', {'waterlogged': 'false'})
                break
    g.save(f'root_arch_{seed % 10}')


def spore_shrine(seed):
    """A small bone chapel of the Spore Choir under a magenta cap, a valve-fed pool, a chest and its keepers."""
    rnd = random.Random(seed)
    W = L = 29
    H = 32
    C = 14
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= 13.5:
                g.set(x, 0, z, 'minecraft:mycelium' if rnd.random() < 0.7 else 'minecraft:moss_block')
                for y in range(1, 14):
                    g.set(x, y, z, AIR)
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            d = math.hypot(x - C, z - C)
            if d <= 6.5:
                g.set(x, 1, z, CAL if d < 5.5 else BONE)
                for y in range(2, 9):
                    if d > 5.5:
                        win = (x + z) % 3 == 0 and 4 <= y <= 6
                        g.set(x, y, z, 'minecraft:magenta_stained_glass' if win else (BONE if y % 3 == 0 else CAL))
    for x in range(C - 1, C + 2):
        for y in range(2, 6):
            g.set(x, y, C + 6, AIR)
            g.set(x, y, C + 7, AIR)
    cap(g, C, 9, C, 10, 7, capblock, gill='minecraft:pink_terracotta')
    for x in range(C - 2, C + 3):
        for z in range(C - 2, C + 3):
            if math.hypot(x - C, z - C) < 2.2:
                g.set(x, 0, z, PEARL, {'axis': 'y'})
                g.set(x, 1, z, 'minecraft:water', {'level': '0'})
    chest(g, C, 2, C - 5, 'aurelia:chests/mycelial_outpost', 'south')
    for s in (-1, 1):
        g.set(C + s * 3, 2, C - 4, 'minecraft:magenta_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
        statue_x = C + s * 10
        cyl(g, statue_x, C + 6, 1.2, 1, 6, STEM)
        cap(g, statue_x, 6, C + 6, 3.5, 2.5, capblock)
    g.set(C + 3, 2, C + 3, 'aurelia:root_snare')
    g.ground_guard('aurelia:husk_guard', C - 3, C + 1, 2, 3)
    g.ground_guard('aurelia:root_grub', C + 9, C - 7, 1, 3)
    g.ground_guard('aurelia:root_grub', C - 9, C - 6, 1, 3)
    g.air_guard('aurelia:spore_drifter', C + 7, 6, C + 9)
    g.save(f'spore_shrine_{seed % 10}')


if __name__ == '__main__':
    for s in (2100, 2101, 2102):
        rift_fragment(s)
    for s in (2200, 2201):
        rift_spire(s)
    for s in (2300, 2301):
        rift_bridge(s)
    for s in (2400, 2401):
        rift_outpost(s)
    for s in (3100, 3101, 3102):
        fungal_tower(s)
    for s in (3200, 3201):
        root_arch(s)
    for s in (3300, 3301):
        spore_shrine(s)
