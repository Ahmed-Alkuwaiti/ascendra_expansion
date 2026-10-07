"""Structures that fill the three outer realms (placed by the structure sets written in gen_act2_data.py).

Drowned Expanse: sunken spires, wrecks of the Sovereign's fleet, leviathan bones on the sea floor, reef shrines and a lighthouse.
Pale Wastes:     kneeling colossi of ice, ice spires, a frozen caravan and a hushed shrine.
Scarlet Sands:   red glass monoliths, a buried giant, a Sunseer camp and a glassworks.
"""
import math
import random

import gen_act2_citadels  # noqa: F401  (extends the passable set and the guard ground test)
from gen_citadels2 import AIR, Grid, chest_nbt, sphere

WATER = 'minecraft:water'
LEAF = {'persistent': 'true', 'distance': '7', 'waterlogged': 'false'}


def stairs(facing, half='bottom'):
    return {'facing': facing, 'half': half, 'shape': 'straight', 'waterlogged': 'false'}


def chest(g, x, y, z, table, facing='north', wet=False):
    g.set(x, y, z, 'minecraft:chest', {'facing': facing, 'type': 'single', 'waterlogged': str(wet).lower()}, chest_nbt(table))


def line(g, a, b, r, block, props=None, rnd=None, keep=0.0):
    n = int(max(abs(b[i] - a[i]) for i in range(3)) * 2) + 1
    for k in range(n + 1):
        t = k / n
        p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
        if rnd is None or rnd.random() >= keep:
            sphere(g, p[0], p[1], p[2], r, block, props)


# ===================================================================================== Drowned Expanse (sea level 96)
def drowned_spire(seed):
    """A drowned watchtower rising from the sea floor, broken off well above the waves. Placed 2 below the sea floor."""
    rnd = random.Random(seed)
    H = 62 + rnd.randint(0, 8)
    W = L = 21
    C = 10
    g = Grid(W, H, L)
    r0 = 5.5 + rnd.random()
    top = H - rnd.randint(2, 6)
    for y in range(0, top):
        r = r0 - y * 0.03
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d <= r:
                    broken = y > top - 8 and rnd.random() < (y - (top - 8)) / 10.0
                    if d > r - 1.4 and not broken:
                        roll = rnd.random()
                        g.set(x, y, z, 'minecraft:mossy_stone_bricks' if roll < 0.35 else ('minecraft:cracked_stone_bricks' if roll < 0.5 else
                                                                                         ('minecraft:prismarine_bricks' if roll < 0.65 else 'minecraft:stone_bricks')))
                    elif d <= r - 1.4 and y < 4:
                        g.set(x, y, z, 'minecraft:gravel')
        if y % 9 == 5:
            for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                g.set(C + dx * round(r - 0.7), y, C + dz * round(r - 0.7), 'minecraft:light_blue_stained_glass')
    for y in range(4, top - 4, 6):                                 # broken floors
        for x in range(W):
            for z in range(L):
                if math.hypot(x - C, z - C) < r0 - 1.5 and rnd.random() < 0.7:
                    g.set(x, y, z, 'minecraft:dark_oak_planks')
    for k in range(rnd.randint(4, 7)):                             # rubble and kelp at the foot
        a = rnd.uniform(0, 6.28)
        sphere(g, C + 8 * math.cos(a), 2, C + 8 * math.sin(a), rnd.uniform(1.2, 2.2), 'minecraft:mossy_cobblestone')
    for x in range(W):
        for z in range(L):
            if math.hypot(x - C, z - C) > r0 + 0.5 and g.get(x, 3, z) is None and rnd.random() < 0.12:
                for y in range(3, 3 + rnd.randint(4, 14)):
                    g.set(x, y, z, 'minecraft:kelp_plant')
    g.set(C, top - 1, C, 'minecraft:sea_lantern')
    chest(g, C, 5, C, 'aurelia:chests/drowned_outpost', wet=True)
    return g


def drowned_wreck(seed):
    """One of the Sovereign's ships, half sunk and listing. Placed at y 89, so the waterline (y 95) is at template y 6."""
    rnd = random.Random(seed)
    W, H, L = 15, 28, 38
    g = Grid(W, H, L)
    C = 7
    WLINE = 6
    tilt = rnd.choice((-1, 1)) * 0.12
    for z in range(2, L - 2):
        t = (z - 2) / (L - 5)
        half = 5.5 * math.sin(math.pi * min(1.0, t * 1.15)) + 0.8
        for y in range(0, 9):
            hw = half * (0.45 + 0.55 * y / 8)
            for x in range(W):
                dx = x - C + (y - 4) * tilt * 3
                if abs(dx) <= hw:
                    shell = abs(dx) > hw - 1.0 or y == 0
                    if shell:
                        if rnd.random() < 0.9:
                            g.set(x, y, z, 'minecraft:dark_oak_planks' if y % 3 else 'minecraft:stripped_dark_oak_log', None if y % 3 else {'axis': 'z'})
                    else:
                        g.set(x, y, z, WATER if y <= WLINE else AIR, {'level': '0'} if y <= WLINE else None)
        if z % 3 == 0:
            g.set(C, 8, z, 'minecraft:dark_oak_planks')
    for x in range(W):                                             # deck over the flooded hold, with two hatches
        for z in range(3, L - 3):
            if g.get(x, 8, z) and g.get(x, 8, z)[0] == AIR and z not in (16, 17):
                g.set(x, 8, z, 'minecraft:spruce_planks')
    for (mz, mh) in ((12, 17), (24, 14)):                          # masts, one snapped
        snapped = rnd.random() < 0.5
        for y in range(1, 9 + (mh if not snapped else mh // 2)):
            g.set(C, y, mz, 'minecraft:dark_oak_log', {'axis': 'y'})
        if not snapped:
            for x in range(C - 5, C + 6):
                g.set(x, 9 + mh - 3, mz, 'minecraft:dark_oak_fence')
                for y in range(9 + mh - 9, 9 + mh - 3):
                    if rnd.random() < 0.7:
                        g.set(x, y, mz + 1, 'minecraft:white_wool' if rnd.random() < 0.8 else 'minecraft:light_gray_wool')
    for z in range(L - 6, L - 2):                                  # stern cabin
        for x in range(C - 3, C + 4):
            for y in range(9, 13):
                edge = x in (C - 3, C + 3) or z in (L - 6, L - 3)
                g.set(x, y, z, 'minecraft:dark_oak_planks' if edge else AIR)
            g.set(x, 13, z, 'minecraft:spruce_slab', {'type': 'bottom', 'waterlogged': 'false'})
    g.set(C, 10, L - 6, AIR)
    g.set(C, 11, L - 6, AIR)
    g.set(C, 12, L - 4, 'minecraft:lantern', {'hanging': 'true', 'waterlogged': 'false'})
    chest(g, C + 1, 9, L - 4, 'aurelia:chests/drowned_outpost', 'north')
    g.ground_guard('aurelia:tidecaller', C, 20, 9, 2)
    return g


def drowned_bones(seed):
    """The ribcage and skull of a leviathan, lying on the sea floor. Placed 3 below it."""
    rnd = random.Random(seed)
    W, H, L = 25, 24, 52
    g = Grid(W, H, L)
    C = 12
    BONE = 'minecraft:bone_block'
    curve = rnd.uniform(-0.15, 0.15)
    for z in range(6, L - 4):                                      # the spine
        x = C + math.sin(z * 0.12) * 3 * curve * 10
        sphere(g, x, 3, z, 1.3, BONE, {'axis': 'z'})
    for k in range(9):                                             # ribs
        z = 12 + k * 3.6
        x0 = C + math.sin(z * 0.12) * 3 * curve * 10
        h = 18 - abs(k - 3) * 1.5
        for side in (-1, 1):
            pts = [(x0 + side * 9 * math.sin(math.pi * t / 2), 3 + h * math.sin(math.pi * t), z) for t in [i / 10 for i in range(11)]]
            for a, b in zip(pts, pts[1:]):
                line(g, a, b, 0.7, BONE, {'axis': 'y'}, rnd, 0.08)
    sphere(g, C, 5, 4, 4.0, BONE, {'axis': 'y'})                    # the skull, half open
    sphere(g, C, 5, 1, 2.6, BONE, {'axis': 'y'})
    for (sx, sz) in ((-2, 2), (2, 2)):
        g.set(C + sx, 6, sz, 'minecraft:sea_lantern')
    for x in range(W):
        for z in range(L):
            if rnd.random() < 0.05 and g.get(x, 1, z) is None:
                g.set(x, 1, z, 'minecraft:seagrass')
            elif rnd.random() < 0.015:
                g.set(x, 1, z, 'minecraft:sea_pickle', {'pickles': '3', 'waterlogged': 'true'})
    for x in range(W):
        for z in range(L):
            g.set(x, 0, z, 'minecraft:sand' if rnd.random() < 0.8 else 'minecraft:gravel')
    chest(g, C, 1, 6, 'aurelia:chests/drowned_outpost', 'south', wet=True)
    return g


def drowned_outpost(seed):
    """0: a reef shrine on stilts at the waterline. 1: a drowned lighthouse on a rock. Placed at y 92 (waterline at template y 3)."""
    rnd = random.Random(seed)
    PB, DP = 'minecraft:prismarine_bricks', 'minecraft:dark_prismarine'
    if seed % 2 == 0:
        W = L = 25
        H = 20
        C = 12
        g = Grid(W, H, L)
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if d <= 10.5:
                    g.set(x, 5, z, PB if rnd.random() < 0.7 else 'minecraft:prismarine')
                    for y in range(6, H):
                        g.set(x, y, z, AIR)
                if d <= 10.5 and (x % 5 == 2 and z % 5 == 2):
                    for y in range(0, 5):
                        g.set(x, y, z, DP)
        for (px, pz) in [(C - 6, C - 6), (C + 6, C - 6), (C - 6, C + 6), (C + 6, C + 6)]:
            for y in range(6, 12):
                g.set(px, y, pz, PB)
            g.set(px, 12, pz, 'minecraft:sea_lantern')
        for x in range(C - 7, C + 8):
            for z in range(C - 7, C + 8):
                if max(abs(x - C), abs(z - C)) <= 7 and (abs(x - C) == 7 or abs(z - C) == 7):
                    g.set(x, 13, z, 'minecraft:dark_prismarine_slab', {'type': 'bottom', 'waterlogged': 'false'})
        for x in range(C - 2, C + 3):
            for z in range(C - 2, C + 3):
                g.set(x, 6, z, DP)
        g.set(C, 7, C, 'minecraft:conduit', {'waterlogged': 'false'})
        g.set(C, 7, C + 3, 'minecraft:bell', {'attachment': 'floor', 'facing': 'north', 'powered': 'false'})
        chest(g, C, 6, C - 4, 'aurelia:chests/drowned_outpost', 'south')
        for (x, z, e) in [(C - 4, C + 5, 'aurelia:coralclad_juggernaut'), (C + 4, C - 3, 'aurelia:tidecaller'),
                          (C - 5, C - 2, 'aurelia:razorclaw'), (C + 5, C + 4, 'aurelia:razorclaw')]:
            g.ground_guard(e, x, z, 6, 2)
        return g
    W = L = 23
    H = 40
    C = 11
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C) + rnd.uniform(-0.8, 0.8)
            if d <= 10:
                top = int(6 - d * 0.35)
                for y in range(0, top + 1):
                    g.set(x, y, z, 'minecraft:stone' if rnd.random() < 0.7 else 'minecraft:andesite')
                g.set(x, top, z, 'minecraft:grass_block' if top > 3 else 'minecraft:sand', {'snowy': 'false'} if top > 3 else None)
                for y in range(top + 1, H):
                    g.set(x, y, z, AIR)
    for y in range(5, 33):
        for x in range(C - 3, C + 4):
            for z in range(C - 3, C + 4):
                d = math.hypot(x - C, z - C)
                if d <= 3.2:
                    g.set(x, y, z, ('minecraft:white_concrete' if (y // 4) % 2 else 'minecraft:red_concrete') if d > 2.2 else AIR)
    for y in range(6, 33):
        g.set(C, y, C + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
    for x in range(C - 4, C + 5):
        for z in range(C - 4, C + 5):
            if math.hypot(x - C, z - C) <= 4.3:
                g.set(x, 33, z, PB)
    g.set(C, 33, C + 2, 'minecraft:ladder', {'facing': 'north', 'waterlogged': 'false'})
    for (dx, dz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
        for y in range(34, 37):
            g.set(C + dx, y, C + dz, 'minecraft:iron_bars')
    g.set(C, 35, C, 'minecraft:sea_lantern')
    g.box(C - 2, 37, C - 2, C + 2, 37, C + 2, DP)
    for y in range(5, 8):
        g.set(C + 3, y, C, AIR)
    chest(g, C - 1, 34, C - 1, 'aurelia:chests/drowned_outpost', 'south')
    for (x, z, e) in [(C - 6, C + 3, 'aurelia:coralclad_juggernaut'), (C + 6, C - 3, 'aurelia:tidecaller'), (C + 5, C + 5, 'aurelia:razorclaw')]:
        g.ground_guard(e, x, z, 6, 3)
    return g


# ===================================================================================== Pale Wastes
def pale_colossus(seed):
    """0: a kneeling colossus of ice with its hands over its face. 1: a fallen colossus head and an open hand in the snow."""
    rnd = random.Random(seed)
    PI, SN, CAL = 'minecraft:packed_ice', 'minecraft:snow_block', 'minecraft:calcite'
    if seed % 2 == 0:
        W, H, L = 25, 34, 25
        g = Grid(W, H, L)
        C = 12

        def body(x, y, z, r, b=PI):
            sphere(g, x, y, z, r, b)
        for x in range(W):                                         # snow drift base
            for z in range(L):
                d = math.hypot(x - C, z - C)
                for y in range(0, 5 - int(d * 0.25) if d < 18 else 1):
                    g.set(x, y, z, SN)
        line(g, (C - 4, 5, C + 4), (C - 4, 5, C - 5), 2.8, PI)       # shins on the ground, kneeling
        line(g, (C + 4, 5, C + 4), (C + 4, 5, C - 5), 2.8, PI)
        line(g, (C - 4, 6, C + 4), (C - 3, 13, C + 1), 3.0, PI)      # thighs
        line(g, (C + 4, 6, C + 4), (C + 3, 13, C + 1), 3.0, PI)
        line(g, (C, 13, C + 1), (C, 23, C + 3), 5.0, PI)             # torso, bowed forward
        body(C, 25, C + 6, 3.6, CAL)                                 # the bowed head
        for side in (-1, 1):
            line(g, (C + side * 5, 21, C + 3), (C + side * 4, 18, C + 8), 1.8, PI)   # arms
            line(g, (C + side * 4, 18, C + 8), (C + side * 1.5, 25, C + 9), 1.6, PI)  # forearms up to the face
            body(C + side * 1.2, 25.5, C + 9.2, 1.6, CAL)                            # hands over the face
        for k in range(16):                                          # a frost-cloak down the back
            a = math.radians(-60 + k * 8)
            line(g, (C + 6 * math.sin(a), 22, C - 1 + 2 * math.cos(a)), (C + 9 * math.sin(a), 4, C - 5 + 3 * math.cos(a)), 0.8,
                 'minecraft:snow_block' if k % 2 else 'minecraft:white_concrete')
        for x in range(W):
            for z in range(L):
                for y in range(H - 1, 0, -1):
                    if g.get(x, y, z) and g.get(x, y + 1, z) is None and rnd.random() < 0.5:
                        g.set(x, y + 1, z, 'minecraft:snow', {'layers': '2'})
                        break
        g.set(C, 1, C + 10, 'minecraft:soul_campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})
        for y in range(0, 1):
            g.set(C, y, C + 10, 'minecraft:stone_bricks')
        return g
    W, H, L = 34, 18, 26
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            g.set(x, 0, z, SN)
            g.set(x, 1, z, SN)
    sphere(g, 11, 6, 13, 7.5, PI, skip_below=1)                     # the head, half sunk, on its side
    for (ex, ez) in ((7, 9), (7, 17)):
        sphere(g, ex, 8, ez, 1.6, 'minecraft:blue_ice')
    for y in range(2, 8):                                            # a cracked crown of spikes
        for k in range(5):
            g.set(17 + y // 2, y + 4, 8 + k * 2, PI)
    for k in range(5):                                               # an open hand, fingers reaching up
        x0 = 24 + (k % 3) - 1
        z0 = 6 + k * 3
        line(g, (x0, 2, z0), (x0 + 1, 10 + (k % 2) * 3, z0), 1.0, PI)
    line(g, (21, 2, 12), (30, 2, 12), 3.5, PI)
    chest(g, 11, 2, 22, 'aurelia:chests/pale_outpost', 'north')
    return g


def pale_spire(seed):
    """Jagged spires of packed and blue ice, with frozen dead trees round the foot. Placed 3 below the surface."""
    rnd = random.Random(seed)
    W = L = 19
    H = 26 + seed * 6
    C = 9
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            for y in range(0, 3):
                g.set(x, y, z, 'minecraft:snow_block')
    for k in range(rnd.randint(3, 5)):
        bx, bz = C + rnd.uniform(-3, 3), C + rnd.uniform(-3, 3)
        h = rnd.randint(H // 2, H - 2)
        r0 = rnd.uniform(1.8, 3.2)
        lean = (rnd.uniform(-0.12, 0.12), rnd.uniform(-0.12, 0.12))
        for y in range(2, h):
            r = r0 * (1 - (y - 2) / h)
            sphere(g, bx + lean[0] * y, y, bz + lean[1] * y, max(0.5, r), 'minecraft:blue_ice' if rnd.random() < 0.25 else 'minecraft:packed_ice')
    for k in range(2):
        tx, tz = rnd.choice([(2, 2), (16, 3), (3, 15), (15, 15)])
        for y in range(3, 3 + rnd.randint(4, 7)):
            g.set(tx, y, tz, 'minecraft:spruce_log', {'axis': 'y'})
        g.set(tx + 1, y, tz, 'minecraft:spruce_log', {'axis': 'x'})
    return g


def pale_outpost(seed):
    """0: a frozen caravan round a brazier. 1: a hushed shrine with an empty bell frame."""
    rnd = random.Random(seed)
    W = L = 25
    H = 16
    C = 12
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            g.set(x, 0, z, 'minecraft:stone')
            g.set(x, 1, z, 'minecraft:snow_block')
            for y in range(2, H):
                g.set(x, y, z, AIR)
    CAMP = {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}
    if seed % 2 == 0:
        g.set(C, 2, C, 'minecraft:soul_campfire', CAMP)
        for (wx, wz, ax) in [(C - 7, C - 4, 'x'), (C + 5, C + 4, 'z'), (C - 2, C + 7, 'x')]:   # three wagons
            for i in range(-2, 3):
                for j in range(-1, 2):
                    x, z = (wx + i, wz + j) if ax == 'x' else (wx + j, wz + i)
                    g.set(x, 3, z, 'minecraft:spruce_planks')
                    if abs(j) == 1:
                        g.set(x, 4, z, 'minecraft:spruce_fence')
            for (i, j) in [(-2, -1), (2, -1), (-2, 1), (2, 1)]:
                x, z = (wx + i, wz + j) if ax == 'x' else (wx + j, wz + i)
                g.set(x, 2, z, 'minecraft:spruce_log', {'axis': 'z' if ax == 'x' else 'x'})
            for i in range(-2, 3):
                x, z = (wx + i, wz) if ax == 'x' else (wx, wz + i)
                g.set(x, 6, z, 'minecraft:white_wool')
                for j in (-1, 1):
                    x2, z2 = (wx + i, wz + j) if ax == 'x' else (wx + j, wz + i)
                    g.set(x2, 5, z2, 'minecraft:white_wool')
        chest(g, C - 7, 4, C - 4, 'aurelia:chests/pale_outpost', 'south')
        for (bx, bz) in [(C + 3, C - 5), (C - 4, C + 2)]:
            g.set(bx, 2, bz, 'minecraft:barrel', {'facing': 'up', 'open': 'false'})
        for (x, z, e) in [(C + 2, C + 2, 'aurelia:rimeguard'), (C - 3, C - 1, 'aurelia:hushwraith'),
                          (C + 6, C - 6, 'aurelia:rimefang'), (C - 6, C + 6, 'aurelia:rimefang')]:
            g.ground_guard(e, x, z, 2, 2)
        return g
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            if max(abs(x - C), abs(z - C)) <= 6:
                g.set(x, 2, z, 'minecraft:calcite' if (x + z) % 2 else 'minecraft:polished_diorite')
    for (px, pz) in [(C - 5, C - 5), (C + 5, C - 5), (C - 5, C + 5), (C + 5, C + 5)]:
        for y in range(3, 11):
            g.set(px, y, pz, 'minecraft:packed_ice' if y % 3 else 'minecraft:calcite')
    for x in range(C - 5, C + 6):
        for z in (C - 5, C + 5):
            g.set(x, 11, z, 'minecraft:spruce_planks')
            g.set(z, 11, x, 'minecraft:spruce_planks')
    g.box(C - 2, 10, C, C + 2, 10, C, 'minecraft:spruce_log', {'axis': 'x'})
    for y in range(7, 10):
        g.set(C, y, C, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
    for (cx, cz) in [(C - 2, C - 2), (C + 2, C - 2), (C - 2, C + 2), (C + 2, C + 2)]:
        g.set(cx, 3, cz, 'minecraft:white_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
    chest(g, C, 3, C - 3, 'aurelia:chests/pale_outpost', 'south')
    for (x, z, e) in [(C + 3, C + 3, 'aurelia:hushwraith'), (C - 8, C, 'aurelia:rimeguard'), (C + 8, C - 2, 'aurelia:rimefang')]:
        g.ground_guard(e, x, z, 3, 2)
    return g


# ===================================================================================== Scarlet Sands
def scarlet_monolith(seed):
    """Slabs and splinters of red glass and red sandstone, standing in a ring of sand. Placed 3 below the surface."""
    rnd = random.Random(seed)
    W = L = 17
    H = 24 + seed * 5
    C = 8
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            for y in range(0, 3):
                g.set(x, y, z, 'minecraft:red_sand')
    for k in range(rnd.randint(2, 4)):
        bx, bz = C + rnd.randint(-4, 4), C + rnd.randint(-4, 4)
        h = rnd.randint(8, H - 2)
        wx, wz = rnd.choice([(2, 0), (0, 2), (1, 1)])
        for y in range(2, h):
            for i in range(-wx, wx + 1):
                for j in range(-wz, wz + 1):
                    if y < h - 1 or (i == 0 and j == 0):
                        g.set(bx + i, y, bz + j, 'minecraft:red_stained_glass' if (y + k) % 5 else 'minecraft:red_sandstone')
        g.set(bx, h, bz, 'minecraft:gold_block' if rnd.random() < 0.3 else 'minecraft:red_stained_glass')
    for k in range(5):
        a = rnd.uniform(0, 6.28)
        g.set(C + round(6 * math.cos(a)), 3, C + round(6 * math.sin(a)), 'minecraft:red_stained_glass')
    return g


def scarlet_bones(seed):
    """A giant, buried to the ribs: a skull with glass eyes, a ribcage arching out of the sand, an arm reaching out."""
    rnd = random.Random(seed)
    W, H, L = 30, 26, 44
    g = Grid(W, H, L)
    C = 15
    BONE = 'minecraft:bone_block'
    for x in range(W):
        for z in range(L):
            for y in range(0, 6):
                g.set(x, y, z, 'minecraft:red_sand' if y > 3 else 'minecraft:red_sandstone')
    for k in range(7):
        z = 14 + k * 3.5
        h = 16 - abs(k - 2) * 1.6
        for side in (-1, 1):
            pts = [(C + side * 10 * math.sin(math.pi * t / 2), 5 + h * math.sin(math.pi * t), z) for t in [i / 12 for i in range(13)]]
            for a, b in zip(pts, pts[1:]):
                line(g, a, b, 0.75, BONE, {'axis': 'y'}, rnd, 0.06)
    sphere(g, C, 8, 7, 5.5, BONE, {'axis': 'y'}, skip_below=4)
    for (ex, ez) in ((C - 2, 2), (C + 2, 2)):
        sphere(g, ex, 9, ez, 1.3, 'minecraft:red_stained_glass')
    for y in range(4, 8):
        for x in range(C - 2, C + 3):
            g.set(x, y, 1, AIR if y < 6 else BONE)
    line(g, (C + 9, 6, 36), (C + 13, 12, 40), 1.4, BONE, {'axis': 'y'})
    for k in range(4):
        line(g, (C + 13, 12, 40), (C + 11 + k * 1.5, 17, 42), 0.6, BONE, {'axis': 'y'})
    chest(g, C, 6, 22, 'aurelia:chests/scarlet_outpost', 'north')
    return g


def scarlet_outpost(seed):
    """0: a Sunseer camp of striped tents round a mirror on a pole. 1: a glassworks with kilns and racks of glass."""
    rnd = random.Random(seed)
    W = L = 25
    H = 16
    C = 12
    g = Grid(W, H, L)
    for x in range(W):
        for z in range(L):
            g.set(x, 0, z, 'minecraft:red_sandstone')
            g.set(x, 1, z, 'minecraft:red_sand')
            for y in range(2, H):
                g.set(x, y, z, AIR)
    if seed % 2 == 0:
        for (tx, tz, col) in [(C - 6, C - 5, 'red'), (C + 6, C - 4, 'orange'), (C - 4, C + 6, 'red'), (C + 5, C + 6, 'yellow')]:
            for k in range(4):
                for i in range(-3 + k, 4 - k):
                    for j in range(-2, 3):
                        g.set(tx + i, 2 + k, tz + j, f'minecraft:{col}_wool' if (abs(i) == 3 - k or k == 3) else AIR)
            g.set(tx, 2, tz + 2, AIR)
            g.set(tx, 3, tz + 2, AIR)
        for y in range(2, 9):
            g.set(C, y, C, 'minecraft:dark_oak_fence')
        g.set(C, 9, C, 'minecraft:gold_block')
        g.set(C, 10, C, 'minecraft:glass')
        chest(g, C - 6, 2, C - 6, 'aurelia:chests/scarlet_outpost', 'south')
        for (x, z, e) in [(C + 2, C - 1, 'aurelia:sunseer'), (C - 2, C + 2, 'aurelia:sandglass_sentinel'),
                          (C + 8, C + 1, 'aurelia:glasswing_scarab'), (C - 9, C + 1, 'aurelia:glasswing_scarab')]:
            g.ground_guard(e, x, z, 2, 2)
        return g
    for x in range(C - 7, C + 8):
        for z in range(C - 5, C + 6):
            edge = x in (C - 7, C + 7) or z in (C - 5, C + 5)
            for y in range(2, 7):
                g.set(x, y, z, ('minecraft:cut_red_sandstone' if y < 6 else 'minecraft:smooth_red_sandstone') if edge else AIR)
            g.set(x, 7, z, 'minecraft:smooth_red_sandstone_slab', {'type': 'bottom', 'waterlogged': 'false'})
    for x in range(C - 1, C + 2):
        for y in range(2, 5):
            g.set(x, y, C + 5, AIR)
    for kx in (C - 5, C + 5):                                         # kilns
        for y in range(2, 5):
            g.set(kx, y, C - 3, 'minecraft:bricks')
        g.set(kx, 3, C - 2, 'minecraft:blast_furnace', {'facing': 'south', 'lit': 'true'})
        g.set(kx, 5, C - 3, 'minecraft:campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})
        for y in range(6, 10):
            g.set(kx, y, C - 3, 'minecraft:bricks')
    for z in range(C - 2, C + 3):                                     # racks of glass
        g.set(C, 2, z, 'minecraft:red_stained_glass')
        g.set(C, 3, z, 'minecraft:orange_stained_glass')
    chest(g, C + 6, 2, C + 3, 'aurelia:chests/scarlet_outpost', 'west')
    for (x, z, e) in [(C - 3, C + 2, 'aurelia:sunseer'), (C + 3, C + 8, 'aurelia:sandglass_sentinel'), (C - 9, C - 8, 'aurelia:glasswing_scarab')]:
        g.ground_guard(e, x, z, 2, 2)
    return g


BUILDS = [
    ('drowned_spire_{}', drowned_spire, 3), ('drowned_wreck_{}', drowned_wreck, 2), ('drowned_bones_{}', drowned_bones, 2),
    ('drowned_outpost_{}', drowned_outpost, 2), ('pale_colossus_{}', pale_colossus, 2), ('pale_spire_{}', pale_spire, 3),
    ('pale_outpost_{}', pale_outpost, 2), ('scarlet_monolith_{}', scarlet_monolith, 3), ('scarlet_bones_{}', scarlet_bones, 2),
    ('scarlet_outpost_{}', scarlet_outpost, 2),
]

if __name__ == '__main__':
    for name, fn, count in BUILDS:
        for i in range(count):
            fn(i).save(name.format(i))
