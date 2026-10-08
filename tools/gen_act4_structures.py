"""The finale's structures (DataVersion 3465 = 1.20.1).

convergence_gate    - an overworld ruin: an octagonal gate of black and white stone on a stepped terrace, eight relic pedestals
                      before it, each with a crystal lamp and a glowing conduit to the gate. Place all eight relics to wake it.
last_core           - the Last Realm's arena: a ring of checkered stone round the landing pad, eight Realm Nodes on its rim and
                      eight bridges out to the islands. Placed by ArenaBuilder.last() round the pad (it leaves the pad's own cells alone).
last_island_<realm> - one floating island per realm at the far end of each bridge, each carrying a piece of its realm.
"""
import math
import random

import gen_act3_citadels as c3
from gen_act3_citadels import AIR, Grid, blob, cap, chain, chest, clock_face, cone, cyl, gear, lantern, lectern, statue, stairs
from gen_act3_realms import capblock

REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']
GLASS = {'grove': 'lime', 'skyreach': 'light_blue', 'hollow': 'orange', 'drowned': 'cyan', 'pale': 'white', 'scarlet': 'red',
         'clockwork': 'yellow', 'mycelial': 'magenta'}
HEAVY = {'grove': 'bramble_sentinel', 'skyreach': 'calcite_sentinel', 'hollow': 'ashbound_knight', 'drowned': 'coralclad_juggernaut',
         'pale': 'rimeguard', 'scarlet': 'sandglass_sentinel', 'clockwork': 'hour_warden', 'mycelial': 'husk_guard'}
NODE_BASE = {'grove': 'minecraft:moss_block', 'skyreach': 'minecraft:quartz_bricks', 'hollow': 'minecraft:magma_block',
             'drowned': 'minecraft:prismarine_bricks', 'pale': 'minecraft:packed_ice', 'scarlet': 'minecraft:cut_red_sandstone',
             'clockwork': 'minecraft:gold_block', 'mycelial': 'minecraft:bone_block'}
CAL, PBB, PB, GOLD = 'minecraft:calcite', 'minecraft:polished_blackstone_bricks', 'minecraft:polished_blackstone', 'minecraft:gold_block'
DT, SS, CSS = 'minecraft:deepslate_tiles', 'minecraft:smooth_sandstone', 'minecraft:chiseled_sandstone'
PEARL = 'minecraft:pearlescent_froglight'
CORE_R = 22                 # the Realm Nodes stand on this radius round the altar; Java uses the same number
BRIDGE_IN, BRIDGE_OUT = 27, 53
ISLAND_D = 66               # island centres stand this far from the altar
FLOOR = 40                  # the arena surface (the pad's surface level) in every last_* template


def glass(realm):
    return f'minecraft:{GLASS[realm]}_stained_glass'


def checker(x, y, z):
    return CAL if (x // 2 + z // 2) % 2 else PBB


# ================================================================================================ CONVERGENCE GATE
def convergence_gate():
    W = L = 81
    H = 74
    C = 40
    G = 6                    # the surface in template space (placed six under the surface)
    rnd = random.Random(4040)
    g = Grid(W, H, L)
    GZ = C - 16              # the gate's plane
    P = G + 9                # the gate terrace

    def stone(x, y, z):
        r = rnd.random()
        return 'minecraft:stone_bricks' if r < 0.45 else ('minecraft:cracked_stone_bricks' if r < 0.62 else
                                                          ('minecraft:mossy_stone_bricks' if r < 0.78 else 'minecraft:andesite'))
    # ---- ground, and the three-step terrace climbing north to the gate
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d > 40:
                continue
            for y in range(0, G):
                g.set(x, y, z, 'minecraft:stone' if y < G - 2 else 'minecraft:dirt')
            g.set(x, G, z, 'minecraft:grass_block' if rnd.random() < 0.8 else 'minecraft:coarse_dirt')
            for y in range(G + 1, G + 34):
                g.set(x, y, z, AIR)
    tiers = [(30, C + 20, G + 3), (26, C + 12, G + 6), (22, C + 4, P)]
    for half, zmax, top in tiers:
        for x in range(C - half, C + half + 1):
            for z in range(C - 36, zmax + 1):
                for y in range(G, top + 1):
                    edge = x in (C - half, C + half) or z == zmax
                    g.set(x, y, z, (checker(x, y, z) if y == top else (PBB if edge else stone(x, y, z))))
    for x in range(C - 22, C + 23):                                   # a gold line where each tier meets the next
        g.set(x, P, C + 4, GOLD if x % 3 == 0 else PBB)
    # the grand stair up the middle of every tier
    for z in range(C + 4, C + 30):
        y = min(P, G + max(0, (C + 30 - z) // 2))
        for x in range(C - 5, C + 6):
            for yy in range(G, y):
                g.set(x, yy, z, PBB)
            g.set(x, y, z, 'minecraft:polished_blackstone_brick_stairs' if y > G else PB, stairs('north') if y > G else None)
            for yy in range(y + 1, y + 6):
                g.set(x, yy, z, AIR)
        for x in (C - 6, C + 6):
            for yy in range(G, y + 2):
                g.set(x, yy, z, CAL if yy <= y else 'minecraft:polished_blackstone_brick_wall')
    # ---- the gate: an octagonal ring of checkered stone, a gold inner edge, a starfield behind, eight rune sockets
    GY = P + 15
    R_OUT, R_IN = 16.5, 10.5
    for x in range(C - 18, C + 19):
        for y in range(P, P + 34):
            a, b = x - C, y - GY
            d = max(abs(a), abs(b), (abs(a) + abs(b)) / 1.38)            # an octagon
            for z in (GZ - 1, GZ, GZ + 1):
                if R_IN <= d <= R_OUT and y >= P:
                    seg = int((math.atan2(b, a) + math.pi) / (2 * math.pi) * 24)
                    blk = CAL if seg % 2 else PBB
                    if d < R_IN + 1:
                        blk = GOLD
                    if d > R_OUT - 1 and z != GZ:
                        blk = DT
                    g.set(x, y, z, blk)
            if d < R_IN and y > P:
                g.set(x, y, GZ - 2, 'minecraft:black_concrete' if rnd.random() > 0.03 else 'minecraft:white_concrete')
                g.set(x, y, GZ - 1, AIR)
                g.set(x, y, GZ, AIR)
                g.set(x, y, GZ + 1, AIR)
    g.set(C, GY, GZ - 2, PEARL, {'axis': 'y'})
    for k, (dx, dy) in enumerate([(1, 0), (-1, 0), (0, 1), (0, -1)]):
        g.set(C + dx, GY + dy, GZ - 2, 'minecraft:end_rod', {'facing': 'south'})
    for k, realm in enumerate(REALMS):                                # sockets round the ring, lower left to lower right
        a = math.radians(200 - k * (220 / 7))
        sx, sy = round(C + 13.5 * math.cos(a)), round(GY + 13.5 * math.sin(a))
        for (dx, dy) in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            g.set(sx + dx, sy + dy, GZ + 1, glass(realm))
            g.set(sx + dx, sy + dy, GZ, PEARL, {'axis': 'y'})
        for (dx, dy) in [(-1, -1), (2, -1), (-1, 2), (2, 2)]:
            g.set(sx + dx, sy + dy, GZ + 2, GOLD)
    for x in range(C - 6, C + 7):                                    # the threshold, the portal in the gate's foot
        for z in range(GZ - 1, GZ + 2):
            g.set(x, P, z, GOLD if abs(x - C) <= 1 else PBB)
    g.set(C, P + 1, GZ, 'aurelia:waygate', {'realm': 'last', 'active': 'false'})
    # buttress-towers either side of the gate
    for s in (-1, 1):
        tx = C + s * 21
        for x in range(tx - 3, tx + 4):
            for z in range(GZ - 4, GZ + 3):
                for y in range(G, P + 40):
                    edge = abs(x - tx) == 3 or z in (GZ - 4, GZ + 2)
                    if edge or y < P + 1:
                        g.set(x, y, z, checker(x, y, z) if (y // 4) % 2 else PBB)
        cone(g, tx, GZ - 1, 4.5, P + 40, 12, DT, power=1.4)
        g.set(tx, P + 52, GZ - 1, GOLD)
        for y in range(P + 8, P + 36, 7):
            for k in range(3):
                g.set(tx, y + k, GZ + 2, 'minecraft:purple_stained_glass')
    # ---- eight pedestals in an arc before the gate, a crystal lamp behind each, a conduit of glass to the gate's foot
    PED = []
    for k, realm in enumerate(REALMS):
        a = math.radians(165 - k * (150 / 7))
        px, pz = round(C + 15 * math.cos(a)), round(GZ + 4 + 11 * math.sin(a))
        PED.append((px, pz, realm))
        for x in range(px - 1, px + 2):
            for z in range(pz - 1, pz + 2):
                g.set(x, P, z, PB)
        g.set(px, P + 1, pz, 'aurelia:relic_pedestal', {'realm': realm, 'filled': 'false'})
        bx, bz = round(px + 2.2 * math.cos(a)), round(pz + 2.2 * math.sin(a) * 0.4) - 1   # the lamp, set back from the pedestal
        bz = min(bz, pz - 2)
        for y in range(P + 1, P + 6):
            g.set(bx, y, bz, PBB if y < P + 5 else GOLD)
        for y in range(P + 6, P + 9):
            g.set(bx, y, bz, glass(realm))
        g.set(bx, P + 9, bz, PEARL, {'axis': 'y'})
        n = int(math.hypot(px - C, pz - GZ)) + 1                    # the conduit: a line of the realm's glass in the floor
        for i in range(2, n):
            t = i / n
            x, z = round(px + (C - px) * t), round(pz + (GZ + 1 - pz) * t)
            if g.get(x, P, z) and g.get(x, P, z)[0] != 'minecraft:gold_block':
                g.set(x, P, z, glass(realm))
    # ---- colossal broken colonnades down both sides of the terrace, a fallen column, floating debris on chains
    for s in (-1, 1):
        for i, z in enumerate(range(C - 6, C + 22, 7)):
            x = C + s * 26
            top = G + 22 + (i * 7) % 11
            y0 = g_top = (P if z <= C + 4 else (G + 6 if z <= C + 12 else G + 3))
            for y in range(y0 + 1, top):
                for dx in range(-1, 2):
                    for dz in range(-1, 2):
                        g.set(x + dx, y, z + dz, CAL if (y % 6) else PBB)
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    g.set(x + dx, y0 + 1, z + dz, PBB)
                    if i % 2 == 0:
                        g.set(x + dx, top, z + dz, PBB)
    for k in range(9):                                                # the fallen column
        g.set(C + 33 - k, G + 1, C + 26 - k // 3, CAL)
        g.set(C + 33 - k, G + 2, C + 26 - k // 3, CAL if k % 3 else PBB)
    for (fx, fy, fz, fr) in [(C - 22, P + 44, GZ + 8, 3), (C + 24, P + 48, GZ + 12, 4), (C - 8, P + 52, GZ - 6, 3), (C + 9, P + 40, GZ + 18, 2)]:
        for x in range(fx - fr, fx + fr + 1):
            for z in range(fz - fr, fz + fr + 1):
                d = math.hypot(x - fx, z - fz)
                if d <= fr:
                    for y in range(fy - int((fr - d) * 1.6) - 1, fy + 1):
                        g.set(x, y, z, checker(x, y, z) if y == fy else 'minecraft:blackstone')
        chain(g, fx, fy + 1, fy + 6, fz)
    lectern(g, C + 7, P + 1, C + 1, 'north', 'The Convergence Gate',
            ["Eight Wardens kept eight pieces of the Sovereign's crown. Each of them took something from her when she broke, and each "
             "left something of itself behind when it fell: a heart, a talon, a hand, a fang, a voice, a stinger, an eye, a seed.",
             "Lay each relic on its own pedestal. The gate will wake when all eight are home.",
             "On the other side is the place every realm was cut from, and the thing that cut them. It has no name of its own. "
             "We called it the Unmaker."])
    chest(g, C - 7, P + 1, C + 1, 'aurelia:chests/convergence_cache', 'north')
    # ---- the echoes: one heavy guard from each realm, standing watch by its pedestal
    for (px, pz, realm) in PED:
        g.ground_guard('aurelia:' + HEAVY[realm], px + (1 if px < C else -1), pz + 2, P + 1, 3)
    c3.trim_air(g, G + 34)
    g.save('convergence_gate')
    return g, PED


# ================================================================================================ THE LAST REALM: the core
def star(dx, dz):
    """On the lines of an eight-pointed star {8/3} whose points lie on the node spokes at radius 18."""
    pts = [(18 * math.cos(math.radians(k * 45)), 18 * math.sin(math.radians(k * 45))) for k in range(8)]
    for k in range(8):
        (x0, z0), (x1, z1) = pts[k], pts[(k + 3) % 8]
        ex, ez = x1 - x0, z1 - z0
        t = max(0.0, min(1.0, ((dx - x0) * ex + (dz - z0) * ez) / (ex * ex + ez * ez)))
        if math.hypot(dx - (x0 + t * ex), dz - (z0 + t * ez)) < 0.6:
            return True
    return False


def crack(dx, dz):
    """Thin jagged cracks running out from the star toward the rim."""
    a = math.degrees(math.atan2(dz, dx)) % 360
    d = math.hypot(dx, dz)
    for k in range(7):
        base = 26 + k * 51.4
        wob = 3.2 * math.sin(d * 0.9 + k) + 1.5 * math.sin(d * 2.3 + 2 * k)
        if abs(((a - base - wob * 57.3 / max(d, 1) + 180) % 360) - 180) * math.pi / 180 * d < 0.55:
            return True
    return False


def last_core():
    W = L = 113
    H = 84
    C = 56
    F = FLOOR
    rnd = random.Random(5050)
    g = Grid(W, H, L)

    def pad_cell(x, y, z):
        """The landing pad and its foundation, air above it, are RealmTravel's: the template leaves those cells alone."""
        return math.hypot(x - C, z - C) <= 12.6 and F - 6 <= y <= F + 15

    def put(x, y, z, b, props=None):
        if not pad_cell(x, y, z):
            g.set(x, y, z, b, props)
    # ---- the underside: an inverted cone of black stone shot with violet, dripping
    for x in range(C - 30, C + 31):
        for z in range(C - 30, C + 31):
            d = math.hypot(x - C, z - C)
            if d > 28.5:
                continue
            depth = int((28.5 - d) * 1.15 + rnd.uniform(0, 3))
            for y in range(F - depth, F):
                r = rnd.random()
                put(x, y, z, 'minecraft:blackstone' if r < 0.5 else ('minecraft:deepslate' if r < 0.8 else
                                                                     ('minecraft:crying_obsidian' if r < 0.9 else 'minecraft:obsidian')))
            if rnd.random() < 0.05:
                put(x, F - depth - 1, z, 'minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': 'down', 'waterlogged': 'false'})
    # ---- the arena floor: concentric rings of sandstone and black stone, a gold ring, radial lines toward the nodes
    for x in range(C - 29, C + 30):
        for z in range(C - 29, C + 30):
            d = math.hypot(x - C, z - C)
            if d > 28.5:
                continue
            ring = int(d) // 3
            b = SS if ring % 2 == 0 else PB
            if 18.5 < d < 19.5:
                b = GOLD
            if d > 26.5:
                b = PBB
            ang = math.degrees(math.atan2(z - C, x - C)) % 45
            if (ang < 2.5 or ang > 42.5) and 13 < d < 26:
                b = CSS
            if 12.8 < d < 18.6 and star(x - C, z - C):
                b = 'minecraft:crying_obsidian'                           # the eightfold star, weeping, inlaid round the pad
            elif 12.8 < d < 26.5 and crack(x - C, z - C):
                b = 'minecraft:black_concrete' if (x + z) % 3 else 'minecraft:crying_obsidian'
            put(x, F - 1, z, b)
            for y in range(F, F + 20):
                put(x, y, z, AIR)
            if 27 <= d <= 28.5:                                       # a rim of black teeth, broken where the bridges leave
                a = math.degrees(math.atan2(z - C, x - C)) % 45
                if 6 < a < 39:
                    tooth = int(1 + 4 * abs(math.sin(math.radians(math.degrees(math.atan2(z - C, x - C)) * 6))) ** 3)
                    for y in range(F, F + tooth):
                        put(x, y, z, 'minecraft:obsidian' if y < F + tooth - 1 else 'minecraft:blackstone')
                    if tooth == 1 and int(math.degrees(math.atan2(z - C, x - C))) % 15 == 0:
                        lantern(g, x, F + 1, z, soul=True)
    # ---- the Realm Nodes on their plinths
    for k, realm in enumerate(REALMS):
        a = math.radians(k * 45)
        nx, nz = C + round(CORE_R * math.cos(a)), C + round(CORE_R * math.sin(a))
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                put(nx + dx, F - 1, nz + dz, NODE_BASE[realm])
        put(nx, F, nz, PBB)
        put(nx, F + 1, nz, 'aurelia:realm_node', {'realm': realm, 'lit': 'false'})
        for (dx, dz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
            put(nx + dx, F, nz + dz, glass(realm))
    # ---- eight bridges out to the islands
    for k, realm in enumerate(REALMS):
        a = math.radians(k * 45)
        ca, sa = math.cos(a), math.sin(a)
        t = BRIDGE_IN - 1.0
        while t <= BRIDGE_OUT + 0.5:
            cx, cz = C + t * ca, C + t * sa
            for x in range(int(cx) - 4, int(cx) + 5):
                for z in range(int(cz) - 4, int(cz) + 5):
                    off = abs(-(x - cx) * sa + (z - cz) * ca)              # distance from the bridge's centre line
                    along = (x - C) * ca + (z - C) * sa
                    if along < BRIDGE_IN - 1 or along > BRIDGE_OUT + 1:
                        continue
                    if off <= 2.5:
                        put(x, F - 1, z, SS if off < 1.5 else PB)
                        sag = int(2.5 * math.sin(math.pi * (along - BRIDGE_IN) / (BRIDGE_OUT - BRIDGE_IN)))
                        put(x, F - 2, z, PBB)
                        if off < 1.6:
                            for y in range(F - 2 - sag - 1, F - 2):
                                put(x, y, z, PBB)
                    elif off <= 3.4:
                        put(x, F - 1, z, PBB)
                        put(x, F, z, 'minecraft:polished_blackstone_brick_wall')
            t += 0.5
        for t in (34, 42, 50):                                          # crystal lamps along the rail
            for sgn in (-1, 1):
                x, z = round(C + t * ca - sgn * 3 * sa), round(C + t * sa + sgn * 3 * ca)
                put(x, F + 1, z, 'minecraft:polished_blackstone_brick_wall')
                put(x, F + 2, z, glass(realm))
    # ---- chains and weeping stone under the rim (the drifting wreckage lives in last_dread now, which the fight never resets)
    for k in range(48):
        a = math.radians(k * 7.5 + 3.75)
        x, z = round(C + 27.5 * math.cos(a)), round(C + 27.5 * math.sin(a))
        ln = 3 + (k * 7) % 9
        for y in range(F - 2 - ln, F - 1):
            put(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
        put(x, F - 3 - ln, z, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'})
    for k in range(0):
        a = math.radians(22.5 + k * 45)
        r = rnd.uniform(34, 48)
        fx, fz, fy = C + r * math.cos(a), C + r * math.sin(a), F + rnd.randint(14, 34)
        fr = rnd.uniform(1.8, 3.5)
        for x in range(int(fx - fr) - 1, int(fx + fr) + 2):
            for z in range(int(fz - fr) - 1, int(fz + fr) + 2):
                d = math.hypot(x - fx, z - fz)
                if d <= fr:
                    for y in range(int(fy - (fr - d) * 1.5) - 1, int(fy) + 1):
                        put(x, y, z, checker(x, y, z) if y == int(fy) else 'minecraft:blackstone')
        if k % 2 == 0:
            chain(g, int(fx), int(fy) - 10, int(fy - fr * 1.5) - 2, int(fz))
    g.save('last_core')
    return g


# ================================================================================================ THE LAST REALM: the islands
def island_base(g, C, top_block, under, rnd, r=15.0, depth=1.6):
    for x in range(int(C - r) - 1, int(C + r) + 2):
        for z in range(int(C - r) - 1, int(C + r) + 2):
            d = math.hypot(x - C, z - C)
            if d > r:
                continue
            dep = int((r - d) * depth + rnd.uniform(0, 2.5))
            for y in range(FLOOR - 1 - dep, FLOOR):
                g.set(x, y, z, top_block(x, z) if y == FLOOR - 1 else under(x, y, z))
            if rnd.random() < 0.06 and dep > 3:
                g.set(x, FLOOR - dep - 2, z, 'minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': 'down', 'waterlogged': 'false'})


def pick(*opts):
    def f(x, y, z):
        h = (x * 73856093 ^ y * 19349663 ^ z * 83492791) % 100
        acc = 0
        for blk, w in opts:
            acc += w
            if h < acc:
                return blk
        return opts[-1][0]
    return f


def corrupt(g, C, rnd):
    """The Unmaker is eating every island: sculk and weeping obsidian creep over the ground, the underside sags into black roots,
    and pieces have broken away and hang below."""
    F = FLOOR
    top = {}
    low = {}
    for (x, y, z), v in list(g.b.items()):
        if v[0] in (AIR,):
            continue
        if y == F - 1:
            top[(x, z)] = True
        if y < F:
            low[(x, z)] = min(low.get((x, z), 99), y)
    for (x, z) in top:
        n = math.sin(x * 0.55 + 1.3) * math.cos(z * 0.47 - 0.4) + 0.6 * math.sin((x + z) * 0.31)
        if n > 0.55:
            g.set(x, F - 1, z, 'minecraft:sculk')
            if g.get(x, F, z) is None and rnd.random() < 0.08:
                g.set(x, F, z, 'minecraft:sculk_vein', {'down': 'true', 'up': 'false', 'north': 'false', 'south': 'false', 'east': 'false',
                                                       'west': 'false', 'waterlogged': 'false'})
        elif n > 0.4:
            g.set(x, F - 1, z, 'minecraft:crying_obsidian' if rnd.random() < 0.5 else 'minecraft:blackstone')
    for (x, z), y0 in low.items():                                       # the underside sags into black roots
        d = math.hypot(x - C, z - C)
        extra = int(max(0.0, 11 - d) * 1.0 + rnd.uniform(0, 3))
        for y in range(max(1, y0 - extra), y0):
            g.set(x, y, z, 'minecraft:crying_obsidian' if rnd.random() < 0.12 else ('minecraft:blackstone' if rnd.random() < 0.7 else 'minecraft:obsidian'))
        if extra > 4 and rnd.random() < 0.12:
            for y in range(max(1, y0 - extra - 5), max(1, y0 - extra)):
                g.set(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
    for k in range(3):                                                   # pieces broken away, hanging below
        a = rnd.uniform(0, 2 * math.pi)
        bx, bz, by = C + 11 * math.cos(a), C + 11 * math.sin(a), F - rnd.randint(14, 22)
        br = rnd.uniform(2.0, 3.2)
        for x in range(int(bx - br) - 1, int(bx + br) + 2):
            for z in range(int(bz - br) - 1, int(bz + br) + 2):
                dd = math.hypot(x - bx, z - bz)
                if dd > br or not (0 <= x < g.W and 0 <= z < g.L):
                    continue
                for y in range(int(by - (br - dd) * 1.8), int(by) + 1):
                    if g.get(x, y, z) is None:
                        g.set(x, y, z, 'minecraft:sculk' if y == int(by) else 'minecraft:blackstone')


def last_island(realm):
    W = L = 35
    H = 80
    C = 17
    F = FLOOR
    rnd = random.Random(sum(map(ord, realm)))
    g = Grid(W, H, L)
    if realm == 'grove':
        island_base(g, C, lambda x, z: 'minecraft:moss_block' if (x * z) % 5 == 0 else 'minecraft:grass_block',
                    pick(('minecraft:dirt', 30), ('minecraft:stone', 50), ('minecraft:mossy_cobblestone', 20)), rnd)
        for x in range(C - 1, C + 1):
            for z in range(C - 1, C + 1):
                for y in range(F, F + 16):
                    g.set(x, y, z, 'minecraft:jungle_log', {'axis': 'y'})
        blob(g, C, F + 17, C, 7, 4.5, 7, lambda x, y, z: 'minecraft:jungle_leaves' if (x + y + z) % 7 else 'minecraft:azalea_leaves')
        for (x, z) in [(C - 6, C + 5), (C + 7, C - 3), (C + 3, C + 8)]:
            for y in range(F, F + 5):
                g.set(x, y, z, 'minecraft:mushroom_stem')
            blob(g, x, F + 5, z, 2.5, 1, 2.5, 'minecraft:red_mushroom_block')
        for _ in range(30):
            x, z = rnd.randint(C - 12, C + 12), rnd.randint(C - 12, C + 12)
            if math.hypot(x - C, z - C) < 13 and g.get(x, F, z) is None:
                g.set(x, F, z, rnd.choice(['minecraft:fern', 'minecraft:allium', 'minecraft:blue_orchid', 'minecraft:grass']))
    elif realm == 'skyreach':
        island_base(g, C, lambda x, z: 'minecraft:grass_block', pick(('minecraft:calcite', 70), ('minecraft:diorite', 30)), rnd, depth=2.0)
        cyl(g, C, C, 2.5, F, F + 22, 'minecraft:quartz_bricks')
        cone(g, C, C, 3.0, F + 23, 10, 'minecraft:quartz_block', power=1.3)
        g.set(C, F + 33, C, GOLD)
        g.set(C, F + 34, C, 'minecraft:lightning_rod')
        for y in range(F + 4, F + 22, 6):
            for (dx, dz) in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                g.set(C + dx, y, C + dz, 'minecraft:light_blue_stained_glass')
        for (x, z) in [(C - 7, C - 5), (C + 6, C + 6)]:
            for y in range(F, F + 6):
                g.set(x, y, z, 'minecraft:cherry_log', {'axis': 'y'})
            blob(g, x, F + 7, z, 4, 2.5, 4, 'minecraft:cherry_leaves')
    elif realm == 'hollow':
        island_base(g, C, lambda x, z: 'minecraft:basalt' if (x + z) % 3 else 'minecraft:blackstone',
                    pick(('minecraft:blackstone', 60), ('minecraft:basalt', 30), ('minecraft:magma_block', 10)), rnd)
        for i, (hw, hh) in enumerate([(7, 3), (5, 3), (3, 3)]):
            y0 = F + i * 3
            for x in range(C - hw, C + hw + 1):
                for z in range(C - hw, C + hw + 1):
                    for y in range(y0, y0 + hh):
                        g.set(x, y, z, PBB if abs(x - C) == hw or abs(z - C) == hw else 'minecraft:blackstone')
        g.set(C, F + 9, C, 'minecraft:crying_obsidian')
        g.set(C, F + 10, C, 'minecraft:soul_fire')
        for (x, z) in [(C - 10, C + 4), (C + 9, C - 8)]:
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dz * dz <= 5:
                        g.set(x + dx, F - 1, z + dz, 'minecraft:lava', {'level': '0'})
    elif realm == 'drowned':
        island_base(g, C, lambda x, z: 'minecraft:sand' if (x + z) % 4 else 'minecraft:gravel',
                    pick(('minecraft:prismarine', 30), ('minecraft:stone', 50), ('minecraft:dark_prismarine', 20)), rnd)
        for x in range(C - 4, C + 5):
            for z in range(C - 4, C + 5):
                d = math.hypot(x - C, z - C)
                for y in range(F, F + 18 - int(d > 3) * rnd.randint(0, 8)):
                    if 2.5 < d <= 4.2:
                        g.set(x, y, z, 'minecraft:prismarine_bricks' if (y % 5) else 'minecraft:mossy_stone_bricks')
        g.set(C, F + 12, C, 'minecraft:sea_lantern')
        for (x, z) in [(C - 9, C + 5), (C + 8, C + 7), (C - 6, C - 9)]:
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dz * dz <= 5:
                        g.set(x + dx, F - 1, z + dz, 'minecraft:water', {'level': '0'})
            g.set(x, F - 2, z, 'minecraft:sea_lantern')
    elif realm == 'pale':
        island_base(g, C, lambda x, z: 'minecraft:snow_block', pick(('minecraft:packed_ice', 50), ('minecraft:snow_block', 30), ('minecraft:blue_ice', 20)), rnd)
        statue(g, C, F, C - 2, 's', 18, 'minecraft:packed_ice', 'minecraft:snow_block', 'minecraft:blue_ice', 'minecraft:soul_lantern')
        for (x, z, h) in [(C - 10, C + 6, 12), (C + 9, C + 8, 9), (C + 11, C - 6, 14), (C - 8, C - 9, 8)]:
            for y in range(F, F + h):
                g.set(x, y, z, 'minecraft:packed_ice')
                if y < F + h // 2:
                    for (dx, dz) in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        g.set(x + dx, y, z + dz, 'minecraft:packed_ice')
    elif realm == 'scarlet':
        bands = ['minecraft:terracotta', 'minecraft:orange_terracotta', 'minecraft:red_terracotta', 'minecraft:yellow_terracotta', 'minecraft:white_terracotta']
        island_base(g, C, lambda x, z: 'minecraft:red_sand', lambda x, y, z: bands[y % len(bands)], rnd)
        for x in range(C - 2, C + 3):
            for z in range(C - 1, C + 2):
                for y in range(F, F + 22 - abs(x - C) * 3):
                    g.set(x, y, z, 'minecraft:chiseled_red_sandstone' if y < F + 2 else 'minecraft:red_stained_glass')
        for _ in range(12):
            x, z = rnd.randint(C - 12, C + 12), rnd.randint(C - 12, C + 12)
            if math.hypot(x - C, z - C) < 13 and g.get(x, F, z) is None:
                g.set(x, F, z, 'minecraft:dead_bush')
    elif realm == 'clockwork':
        island_base(g, C, lambda x, z: DT, pick(('minecraft:deepslate', 50), ('minecraft:tuff', 30), ('minecraft:amethyst_block', 10),
                                               ('minecraft:crying_obsidian', 10)), rnd)
        for x in range(C - 3, C + 4):
            for z in range(C - 3, C + 4):
                edge = abs(x - C) == 3 or abs(z - C) == 3
                for y in range(F, F + 20):
                    if edge:
                        g.set(x, y, z, PBB)
        clock_face(g, C, F + 15, C + 4, 's', 3, hour=7, rim=GOLD)
        cone(g, C, C, 4.2, F + 20, 9, DT, power=1.3)
        g.set(C, F + 29, C, GOLD)
        gear(g, C - 4, F + 6, C, 'w', 3, 8, depth=0)
        gear(g, C + 4, F + 9, C, 'e', 2, 6, block=GOLD, depth=0)
    elif realm == 'mycelial':
        island_base(g, C, lambda x, z: 'minecraft:mycelium' if (x + 2 * z) % 4 else 'minecraft:magenta_terracotta',
                    pick(('minecraft:bone_block', 30), ('minecraft:calcite', 40), ('minecraft:dirt', 30)), rnd)
        cyl(g, C, C, 1.8, F, F + 16, 'minecraft:mushroom_stem')
        cap(g, C, F + 16, C, 9, 6, capblock, gill='minecraft:pink_terracotta')
        for (x, z, h) in [(C - 9, C + 4, 5), (C + 8, C - 6, 6), (C + 6, C + 9, 4)]:
            for y in range(F, F + h):
                g.set(x, y, z, 'minecraft:mushroom_stem')
            cap(g, x, F + h, z, 3, 2, capblock)
        for _ in range(16):
            x, z = rnd.randint(C - 13, C + 13), rnd.randint(C - 13, C + 13)
            if math.hypot(x - C, z - C) < 14:
                for y in range(F - 2, F - 6 - rnd.randint(0, 6), -1):
                    if g.get(x, y, z) is None:
                        g.set(x, y, z, 'minecraft:hanging_roots', {'waterlogged': 'false'})
                        break
    corrupt(g, C, rnd)
    # every island carries a small shrine with a chest, near the bridge end (toward the core, whichever way it is turned)
    for (x, z) in [(C, C + 11), (C, C - 11), (C + 11, C), (C - 11, C)]:
        g.set(x, F, z, PBB)
        g.set(x, F + 1, z, glass(realm))
        g.set(x, F + 2, z, PEARL, {'axis': 'y'})
    chest(g, C - 4, F, C + 11, 'aurelia:chests/last_' + realm, 'north')
    g.save(f'last_island_{realm}')
    return g


if __name__ == '__main__':
    convergence_gate()
    last_core()
    for r in REALMS:
        last_island(r)
    import gen_last_dread
    gen_last_dread.main()
