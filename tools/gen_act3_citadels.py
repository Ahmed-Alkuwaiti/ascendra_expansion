"""Act three citadels as vanilla structure templates (DataVersion 3465 = 1.20.1).

Paradox Keep    - a black gothic keep on a crag above a rift, a great clock tower at its heart.
                  Rite: synchronise three Clock Dials with the Master Clock (each dial drags its neighbour).
Spore Cathedral - a bone-white cathedral under mushroom domes, gripped by roots.
                  Rite: open all three Spore Valves before the first one closes again (12 seconds).
"""
import math
import random
from collections import deque

import gen_citadels2 as base
from gen_citadels2 import AIR, Grid, chest_nbt, lectern

base.PASSABLE.update({'minecraft:chain', 'minecraft:candle', 'minecraft:purple_candle', 'minecraft:magenta_candle', 'minecraft:white_candle',
                      'minecraft:amethyst_cluster', 'minecraft:large_amethyst_bud', 'minecraft:glow_lichen', 'minecraft:spore_blossom',
                      'minecraft:crimson_roots', 'minecraft:warped_roots', 'minecraft:nether_sprouts', 'minecraft:moss_carpet', 'minecraft:vine',
                      'minecraft:magenta_carpet', 'minecraft:purple_carpet', 'minecraft:pink_petals', 'minecraft:end_rod', 'minecraft:bell',
                      'minecraft:soul_lantern', 'minecraft:lantern', 'minecraft:water'})

# the Clock Dial rite: dials ordered west to east; touching dial i winds it and the next one (wrapping) forward an hour.
CLOCK_TARGET = 7                 # the Master Clock in the Hall of Hours stands at VII
CLOCK_INIT = (2, 9, 4)           # solvable: the parity of the dial sum matches the target (checked below)


def clock_moves(init, target):
    seen = {tuple(init): 0}
    q = deque([tuple(init)])
    while q:
        c = q.popleft()
        if c == (target,) * 3:
            return seen[c]
        for i in range(3):
            n = list(c)
            n[i] = (n[i] + 1) % 12
            n[(i + 1) % 3] = (n[(i + 1) % 3] + 1) % 12
            n = tuple(n)
            if n not in seen:
                seen[n] = seen[c] + 1
                q.append(n)
    return None


def trim_air(g, ymax):
    """Air only needs to be written where the world might have terrain or trees to clear; above that, leave it out."""
    for k in [k for k, v in g.b.items() if v[0] == AIR and k[1] > ymax]:
        del g.b[k]


# ------------------------------------------------------------------------------------------------ shared shapes
def stairs(facing, half='bottom'):
    return {'facing': facing, 'half': half, 'shape': 'straight', 'waterlogged': 'false'}


def chest(g, x, y, z, table, facing='north'):
    g.set(x, y, z, 'minecraft:chest', {'facing': facing, 'type': 'single', 'waterlogged': 'false'}, chest_nbt(table))


def lantern(g, x, y, z, soul=False, hanging=False):
    g.set(x, y, z, 'minecraft:soul_lantern' if soul else 'minecraft:lantern', {'hanging': str(hanging).lower(), 'waterlogged': 'false'})


def chain(g, x, y0, y1, z):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        g.set(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})


def cyl(g, cx, cz, r, y0, y1, pick, hollow=None):
    """A solid column of radius r; with hollow=k only the outer k-thick shell (the inside is cleared to air)."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d > r:
                continue
            for y in range(y0, y1 + 1):
                if hollow is not None and d < r - hollow:
                    g.set(x, y, z, AIR)
                else:
                    g.set(x, y, z, pick(x, y, z) if callable(pick) else pick)


def cone(g, cx, cz, r, y0, h, pick, power=1.0):
    """A cone (power > 1 bulges it into an ogive spire)."""
    for k in range(h):
        rr = r * (1 - (k / h)) ** (1 / power)
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for z in range(int(cz - r) - 1, int(cz + r) + 2):
                if math.hypot(x - cx, z - cz) <= rr + 0.25:
                    g.set(x, y0 + k, z, pick(x, y0 + k, z) if callable(pick) else pick)


def cap(g, cx, cy, cz, r, h, pick, gill=None, thick=1.6):
    """A mushroom cap: the upper half of a flattened ellipsoid shell, with gills on the underside."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d > r:
                continue
            top = cy + h * math.sqrt(max(0.0, 1 - (d / r) ** 2))
            for y in range(int(cy) - 1, int(top) + 1):
                inner = cy + (h - thick) * math.sqrt(max(0.0, 1 - (d / max(r - thick, 0.5)) ** 2)) if d < r - thick else cy - 1
                if y > inner or d > r - thick:
                    if y >= cy - (1 if d > r - 1.2 else 0):
                        g.set(x, y, z, pick(x, y, z, d) if callable(pick) else pick)
            if gill and d < r - thick and d > 1.5:
                g.set(x, cy, z, gill)


def line(g, a, b, r, pick):
    n = int(max(abs(b[i] - a[i]) for i in range(3)) * 2) + 1
    for k in range(n + 1):
        t = k / n
        p = [a[i] + (b[i] - a[i]) * t for i in range(3)]
        rr = r(t) if callable(r) else r
        for x in range(int(p[0] - rr) - 1, int(p[0] + rr) + 2):
            for y in range(int(p[1] - rr) - 1, int(p[1] + rr) + 2):
                for z in range(int(p[2] - rr) - 1, int(p[2] + rr) + 2):
                    if (x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2 <= rr * rr + 0.3:
                        g.set(x, y, z, pick(x, y, z) if callable(pick) else pick)


def bez(g, a, c, b, r, pick):
    """A thick quadratic curve from a to b, bent toward c (roots, buttresses)."""
    n = int(max(abs(b[i] - a[i]) for i in range(3)) * 2) + 2
    for k in range(n + 1):
        t = k / n
        p = [(1 - t) ** 2 * a[i] + 2 * (1 - t) * t * c[i] + t * t * b[i] for i in range(3)]
        rr = r(t) if callable(r) else r
        for x in range(int(p[0] - rr) - 1, int(p[0] + rr) + 2):
            for y in range(int(p[1] - rr) - 1, int(p[1] + rr) + 2):
                for z in range(int(p[2] - rr) - 1, int(p[2] + rr) + 2):
                    if (x - p[0]) ** 2 + (y - p[1]) ** 2 + (z - p[2]) ** 2 <= rr * rr + 0.3:
                        g.set(x, y, z, pick(x, y, z) if callable(pick) else pick)


def blob(g, cx, cy, cz, rx, ry, rz, pick):
    for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1:
                    g.set(x, y, z, pick(x, y, z) if callable(pick) else pick)


def plane_put(g, cx, cy, cz, face, a, b, block, props=None, depth=0):
    """Paint on a vertical plane: face is the outward normal ('n','s','e','w'); a runs to the viewer's right, b up."""
    if face == 's':
        g.set(cx + a, cy + b, cz + depth, block, props)
    elif face == 'n':
        g.set(cx - a, cy + b, cz - depth, block, props)
    elif face == 'e':
        g.set(cx + depth, cy + b, cz - a, block, props)
    else:
        g.set(cx - depth, cy + b, cz + a, block, props)


def clock_face(g, cx, cy, cz, face, r, hour=7, minute=0, rim='minecraft:polished_blackstone', dial='minecraft:calcite',
               mark='minecraft:gold_block', hand='minecraft:blackstone', glow='minecraft:pearlescent_froglight'):
    """A great clock face flush on a wall: rim, twelve gold hour marks, two hands and a glowing heart."""
    for a in range(-r - 1, r + 2):
        for b in range(-r - 1, r + 2):
            d = math.hypot(a, b)
            if d <= r + 0.5:
                plane_put(g, cx, cy, cz, face, a, b, rim if d > r - 1.0 else dial)
                if d <= r - 1.0:
                    plane_put(g, cx, cy, cz, face, a, b, 'minecraft:polished_blackstone', depth=-1)
    for h in range(12):
        ang = h * math.pi / 6
        for rr in (r - 2.0, r - 2.8) if h % 3 == 0 else (r - 2.0,):
            plane_put(g, cx, cy, cz, face, round(rr * math.sin(ang)), round(rr * math.cos(ang)), mark)
    for ang, length in ((hour * math.pi / 6 + minute * math.pi / 360, r * 0.5), (minute * math.pi / 30, r * 0.8)):
        for k in range(int(length * 3) + 1):
            t = k / 3
            plane_put(g, cx, cy, cz, face, round(t * math.sin(ang)), round(t * math.cos(ang)), hand, depth=1)
    plane_put(g, cx, cy, cz, face, 0, 0, glow, {'axis': 'y'}, depth=1)


def gear(g, cx, cy, cz, face, r, teeth, block='minecraft:waxed_cut_copper', hub='minecraft:gold_block', depth=1):
    """A cog standing proud of a wall."""
    for a in range(-r - 2, r + 3):
        for b in range(-r - 2, r + 3):
            d = math.hypot(a, b)
            ang = math.atan2(b, a)
            tooth = (math.cos(ang * teeth) > 0.35) and r + 0.5 < d <= r + 1.6
            if (r - 1.6 < d <= r + 0.5) or tooth or d < 1.6:
                plane_put(g, cx, cy, cz, face, a, b, hub if d < 1.6 else block, depth=depth)
            elif d < r - 1.6 and any(abs(math.sin(ang - s * math.pi / 3)) * d < 0.7 for s in range(3)):
                plane_put(g, cx, cy, cz, face, a, b, block, depth=depth)


def statue(g, x0, y0, z0, facing, h, robe, trim, skin, eyes, held=None, overgrown=None, rnd=None):
    """A colossal hooded figure on a plinth. facing: 's' or 'n'. held: 'hourglass' (raised over the head) or 'orb' (cradled).
    overgrown: a list of (block, chance) to crust the robe with."""
    f = 1 if facing == 's' else -1

    def put(u, w, v, block, props=None):
        g.set(x0 + u * f, y0 + w, z0 + v * f, block, props)

    def pick_robe(u, w, v):
        if overgrown and rnd is not None:
            for blk, chance in overgrown:
                if rnd.random() < chance * (1.0 - w / h) * 1.6:
                    return blk
        return robe
    for u in range(-5, 6):                                         # the plinth
        for v in range(-5, 6):
            for w in range(0, 4):
                put(u, w, v, trim if (w == 3 or abs(u) == 5 or abs(v) == 5) else robe)
    base_w = 4
    for w in range(base_w, int(h * 0.74)):                        # the robe, flaring at the hem
        t = (w - base_w) / (h * 0.74 - base_w)
        ru, rv = 3.9 - 1.6 * t, 3.0 - 1.1 * t
        for u in range(-5, 6):
            for v in range(-5, 6):
                if (u / ru) ** 2 + (v / rv) ** 2 <= 1:
                    fold = (u % 2 == 0) and abs(v - rv) < 1.2 and t < 0.6
                    put(u, w, v, trim if fold else pick_robe(u, w, v))
    sw = int(h * 0.74)
    for w in range(sw, sw + 3):                                    # shoulders
        for u in range(-4, 5):
            for v in range(-2, 3):
                if (u / 4.4) ** 2 + (v / 2.4) ** 2 <= 1:
                    put(u, w, v, pick_robe(u, w, v))
    hw = sw + 3                                                    # the hood: a shell with a dark face and burning eyes
    for u in range(-3, 4):
        for v in range(-3, 4):
            for w in range(hw, hw + 6):
                d = math.sqrt((u / 2.6) ** 2 + (v / 2.8) ** 2 + ((w - hw - 2) / 3.2) ** 2)
                if d <= 1:
                    put(u, w, v, robe)
    for u in range(-1, 2):
        for w in range(hw + 1, hw + 4):
            put(u, w, 2, skin)
            put(u, w, 3, AIR)
    put(-1, hw + 2, 2, eyes)
    put(1, hw + 2, 2, eyes)
    put(0, hw + 5, -1, robe)
    put(0, hw + 6, -2, robe)                                       # the hood's peak, swept back
    if held == 'hourglass':                                        # both arms up, an hourglass held over the head
        for s in (-1, 1):
            for k in range(9):
                t = k / 8
                u, v, w = s * (4 - 2.2 * t), 0.5 + 0.8 * t, sw + 1 + (hw + 7 - sw) * t
                for du in (0, s):
                    put(round(u) + 0, round(w), round(v), pick_robe(u, w, v))
                    put(round(u) + du, round(w), round(v), pick_robe(u, w, v))
        top = hw + 8
        for w in range(top, top + 7):
            k = w - top
            r = 2 if k in (0, 6) else (1 if k in (1, 5) else 0)
            for u in range(-2, 3):
                for v in range(-2, 3):
                    if abs(u) <= r and abs(v) <= r:
                        put(u, w, v + 1, 'minecraft:gold_block' if k in (0, 6) else 'minecraft:purple_stained_glass')
            if k in (1, 2):
                put(0, w, 1, 'minecraft:sand' if k == 1 else 'minecraft:purple_stained_glass')
        put(0, top + 4, 1, 'minecraft:crying_obsidian')
        put(0, top + 5, 1, 'minecraft:amethyst_block')
        for s in (-1, 1):
            for w in range(top + 1, top + 6):
                put(s * 2, w, 3, 'minecraft:gold_block')
                put(s * 2, w, -1, 'minecraft:gold_block')
    elif held == 'orb':                                            # arms folded forward round a glowing spore orb
        for s in (-1, 1):
            for k in range(7):
                t = k / 6
                put(round(s * (4 - 3 * t)), round(sw - 1 - 3 * t), round(1 + 3 * t), pick_robe(0, sw, 0))
        for u in range(-2, 3):
            for v in range(2, 7):
                for w in range(sw - 7, sw - 2):
                    if (u / 1.9) ** 2 + ((v - 4) / 1.9) ** 2 + ((w - sw + 4.5) / 1.9) ** 2 <= 1:
                        put(u, w, v, 'minecraft:pearlescent_froglight', {'axis': 'y'})


def arch_bridge(g, x0, x1, z0, z1, deck, floor, spans, pier, deck_block, wall_block, rail_block, arch_lo=None):
    """A viaduct running along z with `spans` round arches (and a second, lower arcade if arch_lo is given)."""
    length = z1 - z0
    for z in range(z0, z1 + 1):
        for x in range(x0, x1 + 1):
            for y in range(floor, deck + 1):
                g.set(x, y, z, deck_block if y == deck else wall_block)
        for x in (x0 - 1, x1 + 1):
            g.set(x, deck, z, wall_block)
            g.set(x, deck + 1, z, rail_block)
    span = length / spans
    for k in range(spans):
        za, zb = z0 + k * span + pier, z0 + (k + 1) * span - pier
        mid, half = (za + zb) / 2, (zb - za) / 2
        spring = deck - 3 - half if arch_lo is None else arch_lo
        for z in range(int(za), int(zb) + 1):
            for y in range(floor, deck - 2):
                dz = (z - mid) / max(half, 0.5)
                if abs(dz) <= 1 and (y <= spring or ((y - spring) / max(half, 1)) ** 2 + dz * dz <= 1):
                    for x in range(x0 - 1, x1 + 2):
                        g.set(x, y, z, AIR)


# ================================================================================================ PARADOX KEEP
def paradox_keep():
    W = L = 97
    H = 126
    C = 48
    G = 9                     # the meadow surface in template space (the template starts nine blocks under it)
    P = G + 7                 # the top of the crag the keep stands on
    rnd = random.Random(1201)
    g = Grid(W, H, L)
    DT, DB, PD, CD = 'minecraft:deepslate_tiles', 'minecraft:deepslate_bricks', 'minecraft:polished_deepslate', 'minecraft:chiseled_deepslate'
    BS, PBB, GOLD = 'minecraft:blackstone', 'minecraft:polished_blackstone_bricks', 'minecraft:gold_block'
    PG, CO, AM = 'minecraft:purple_stained_glass', 'minecraft:crying_obsidian', 'minecraft:amethyst_block'
    PEARL = 'minecraft:pearlescent_froglight'

    def masonry(x, y, z):
        r = rnd.random()
        return DB if r < 0.62 else ('minecraft:cracked_deepslate_bricks' if r < 0.78 else (DT if r < 0.93 else PD))

    def rock(x, y, z):
        r = rnd.random()
        return 'minecraft:deepslate' if r < 0.4 else ('minecraft:tuff' if r < 0.62 else ('minecraft:stone' if r < 0.85 else 'minecraft:cobbled_deepslate'))

    CHASM = (71, 83)          # the rift, z range, crossing the meadow in front of the crag

    # ---- the land: meadow at G, the crag rising to P, the rift cutting across the south, glowing at the bottom
    for x in range(W):
        for z in range(L):
            d = math.hypot((x - C) / 46.0, (z - C) / 47.0)
            if d > 1.0:
                continue
            crag = math.hypot((x - C) / 37.0, (z - C + 9) / 33.0)
            top = G
            if crag < 1.0:
                top = P if crag < 0.86 else int(P - (crag - 0.86) / 0.14 * (P - G) + rnd.uniform(-1, 1))
            in_chasm = CHASM[0] <= z <= CHASM[1] and abs(x - C) < 40 - 0.12 * abs(z - 77) ** 2
            floor = 2 + int(abs(z - 77) * 0.35) if in_chasm else None
            for y in range(0, top + 1):
                if in_chasm and y > floor:
                    g.set(x, y, z, AIR)
                elif y == top and top == G and not in_chasm:
                    g.set(x, y, z, 'minecraft:grass_block')
                elif y >= top - 1 and top > G and crag < 0.86:
                    g.set(x, y, z, 'minecraft:cobbled_deepslate' if rnd.random() < 0.3 else 'minecraft:deepslate_tiles')
                else:
                    g.set(x, y, z, rock(x, y, z) if y > G - 3 or in_chasm else ('minecraft:dirt' if y > G - 3 else rock(x, y, z)))
            if in_chasm:
                g.set(x, floor, z, CO if rnd.random() < 0.35 else (AM if rnd.random() < 0.5 else 'minecraft:obsidian'))
                if rnd.random() < 0.18:
                    g.set(x, floor + 1, z, 'minecraft:amethyst_cluster', {'facing': 'up', 'waterlogged': 'false'})
                elif rnd.random() < 0.05:
                    g.set(x, floor, z, PEARL, {'axis': 'y'})
            elif top == G and rnd.random() < 0.05:
                g.set(x, G + 1, z, rnd.choice(['minecraft:grass', 'minecraft:fern', 'minecraft:allium']))
            for y in range(top + 1, H):
                if not (in_chasm and y <= G):
                    g.set(x, y, z, AIR)
    # purple cracks up the chasm walls
    for x in range(10, 87):
        for z in (CHASM[0], CHASM[1]):
            for y in range(3, G):
                c = g.get(x, y, z)
                if c and c[0] != AIR and rnd.random() < 0.12:
                    g.set(x, y, z, CO)

    # ---- the grand viaduct over the rift, and the stair up from the meadow
    BX0, BX1 = C - 3, C + 3
    arch_bridge(g, BX0, BX1, CHASM[0] - 2, CHASM[1] + 2, P, 1, 3, 1, PBB, DB, 'minecraft:polished_blackstone_brick_wall')
    for z in range(CHASM[0] - 2, CHASM[1] + 3):                       # lamps and spikes along the parapet
        if z % 3 == 0:
            for x in (BX0 - 1, BX1 + 1):
                g.set(x, P + 2, z, 'minecraft:polished_blackstone_brick_wall')
                lantern(g, x, P + 3, z, soul=True)
        g.set(C, P, z, CD if z % 4 == 0 else PBB)
    for z in range(CHASM[1] + 3, 96):                                 # the approach: a wide stair down to the meadow
        y = max(G, P - (z - CHASM[1] - 3))
        for x in range(BX0 - 2, BX1 + 3):
            for yy in range(G - 2, y):
                g.set(x, yy, z, DB)
            g.set(x, y, z, 'minecraft:polished_blackstone_brick_stairs' if y > G else PBB, stairs('north') if y > G else None)
            for yy in range(y + 1, y + 5):
                g.set(x, yy, z, AIR)
    # the two Hourkeepers: colossal hooded statues holding hourglasses over the approach
    for s in (-1, 1):
        statue(g, C + s * 13, G + 1, 88, 's', 30, DT, PBB, BS, CO, held='hourglass')

    # ---- the curtain wall: four round towers, a gatehouse, crenellations, purple glass
    X0, X1, Z0, Z1 = C - 27, C + 27, C - 31, C + 18
    WH = P + 16

    def wall_seg(xa, za, xb, zb):
        n = max(abs(xb - xa), abs(zb - za))
        for k in range(n + 1):
            x = xa + (xb - xa) * k // n
            z = za + (zb - za) * k // n
            for t in (-1, 0, 1):
                xx, zz = (x + t, z) if za == zb else (x, z + t)
                xx, zz = (x, z + t) if za == zb else (x + t, z)
                for y in range(P - 3, WH + 1):
                    g.set(xx, y, zz, masonry(xx, y, zz) if y < WH - 1 else PBB)
            for y in range(WH + 1, WH + 3):                           # merlons
                if k % 3 != 1:
                    xx, zz = (x, z - 1) if za == zb else (x - 1, z)
                    g.set(xx, y, zz, PBB)
                    xx, zz = (x, z + 1) if za == zb else (x + 1, z)
                    g.set(xx, y, zz, PBB)
            if k % 8 == 4:                                            # tall lancet windows
                for y in range(P + 6, P + 12):
                    for t in (-1, 0, 1):
                        xx, zz = (x, z + t) if za == zb else (x + t, z)
                        g.set(xx, y, zz, PG if t == 0 else masonry(xx, y, zz))
    wall_seg(X0, Z0, X1, Z0)
    wall_seg(X0, Z1, X1, Z1)
    wall_seg(X0, Z0, X0, Z1)
    wall_seg(X1, Z0, X1, Z1)
    # buttress piers on the outside of the long walls
    for z in range(Z0 + 6, Z1 - 3, 8):
        for xs, out in ((X0, -1), (X1, 1)):
            for k in range(1, 4):
                for y in range(P - 2, WH - 2 * k + 2):
                    g.set(xs + out * (k + 1), y, z, DT)
                    g.set(xs + out * (k + 1), y, z + 1, DT)
    # four corner towers with ogive roofs and gold finials
    for (tx, tz) in [(X0, Z0), (X1, Z0), (X0, Z1), (X1, Z1)]:
        top = P + 40
        cyl(g, tx, tz, 6, P - 4, top, masonry)
        cyl(g, tx, tz, 7, top - 4, top, PBB)
        for y in range(top + 1, top + 3):                              # crown of merlons
            for k in range(16):
                a = k * math.pi / 8
                if k % 2 == 0:
                    g.set(round(tx + 7 * math.cos(a)), y, round(tz + 7 * math.sin(a)), PBB)
        cone(g, tx, tz, 6.5, top + 1, 22, lambda x, y, z: DT if (y + x + z) % 7 else 'minecraft:purple_terracotta', power=1.6)
        for y in range(top + 23, top + 27):
            g.set(tx, y, tz, GOLD if y < top + 26 else 'minecraft:lightning_rod')
        for k in range(8):                                             # slit windows lit from within
            a = k * math.pi / 4 + 0.3
            for y in (P + 12, P + 13, P + 24, P + 25, P + 34, P + 35):
                g.set(round(tx + 6 * math.cos(a)), y, round(tz + 6 * math.sin(a)), PG)
        cyl(g, tx, tz, 4, P + 1, P + 1, PBB)
        g.set(tx, P + 2, tz, PEARL, {'axis': 'y'})
        gear(g, tx, P + 28, tz + (7 if tz == Z1 else -7), 's' if tz == Z1 else 'n', 3, 8, depth=0)
    # the gatehouse: twin towers, a pointed arch, a gold clock-ring over the gate
    for s in (-1, 1):
        gx = C + s * 7
        cyl(g, gx, Z1 + 1, 4, P - 3, P + 28, masonry)
        cone(g, gx, Z1 + 1, 4.5, P + 29, 14, DT, power=1.5)
        g.set(gx, P + 43, Z1 + 1, GOLD)
        g.set(gx, P + 44, Z1 + 1, 'minecraft:lightning_rod')
        for y in (P + 10, P + 11, P + 20, P + 21):
            g.set(gx, y, Z1 + 5, PG)
    for x in range(C - 4, C + 5):                                       # the gate passage through the wall
        for z in range(Z1 - 2, Z1 + 5):
            g.set(x, P, z, PBB)
            for y in range(P + 1, P + 9):
                inside = abs(x - C) <= 2 or (y <= P + 6 and abs(x - C) <= 3)
                if inside:
                    g.set(x, y, z, AIR)
    gear(g, C, P + 14, Z1 + 2, 's', 4, 10, block=GOLD, hub=CO, depth=0)
    for z in range(Z1 + 3, CHASM[0] - 1):                              # paved apron between the gate and the bridge
        for x in range(BX0 - 1, BX1 + 2):
            g.set(x, P, z, PBB if (x + z) % 2 else PD)
    for z in (Z1 + 6, Z1 + 9):
        g.set(C - 1, P, z, 'aurelia:time_snare')
        g.set(C + 1, P, z + 1, 'aurelia:time_snare')

    # ---- the courtyard: a clock-face floor, pillars, lamps
    for x in range(X0 + 2, X1 - 1):
        for z in range(Z0 + 2, Z1 - 1):
            g.set(x, P, z, PD if (x + z) % 3 else DT)
    for x in range(C - 14, C + 15):
        for z in range(C + 1, Z1 - 1):
            d = math.hypot(x - C, z - (C + 9))
            if d < 8.5:
                g.set(x, P, z, 'minecraft:polished_blackstone' if d > 7.5 else ('minecraft:calcite' if d > 1 else GOLD))
                for h in range(12):
                    a = h * math.pi / 6
                    g.set(round(C + 6.3 * math.sin(a)), P, round(C + 9 + 6.3 * math.cos(a)), GOLD)
    for k in range(7):
        g.set(C, P, C + 9 + k, BS)
    for k in range(5):
        g.set(C - k, P, C + 9 - k // 2, BS)
    for s in (-1, 1):                                                    # lamp-pillars round the yard
        for z in (C + 2, C + 10, Z1 - 4):
            for y in range(P + 1, P + 6):
                g.set(C + s * 18, y, z, PBB)
            lantern(g, C + s * 18, P + 6, z, soul=True)

    # ---- the great clock tower (south face of the keep), rising to a belfry and a needle spire
    TX0, TX1, TZ0, TZ1 = C - 7, C + 7, C - 10, C + 2
    TT = P + 66
    for x in range(TX0, TX1 + 1):
        for z in range(TZ0, TZ1 + 1):
            edge = x in (TX0, TX1) or z in (TZ0, TZ1)
            corner = x in (TX0, TX1) and z in (TZ0, TZ1)
            for y in range(P - 3, TT + 1):
                if edge:
                    g.set(x, y, z, PBB if corner else masonry(x, y, z))
                elif y > P and y < P + 8:
                    g.set(x, y, z, AIR)                                 # the vestibule
                elif y in (P, P + 8):
                    g.set(x, y, z, PD)
    for (cx, cz) in [(TX0, TZ0), (TX1, TZ0), (TX0, TZ1), (TX1, TZ1)]:    # corner buttresses that step in as they rise
        for y in range(P - 3, TT - 6):
            w = 2 if y < P + 30 else 1
            for a in range(-w, w + 1):
                for b in range(-w, w + 1):
                    g.set(cx + a, y, cz + b, PBB)
        for y in range(TT - 6, TT + 8):
            g.set(cx, y, cz, PBB if y < TT + 6 else GOLD)
    for (face, cx, cz) in [('s', C, TZ1 + 1), ('n', C, TZ0 - 1), ('e', TX1 + 1, C - 4), ('w', TX0 - 1, C - 4)]:
        clock_face(g, cx, P + 48, cz, face, 7, hour=CLOCK_TARGET, minute=0)
        for k in range(-8, 9):                                          # a gold frame and a gable over each face
            plane_put(g, cx, P + 57 - abs(k) // 2, cz, face, k, 0, GOLD if abs(k) == 8 or k == 0 else PBB)
        for a, b in [(-5, -14), (5, -14), (-5, -24), (5, -24)]:         # lancets below the clock
            for k in range(6):
                plane_put(g, cx, P + 48, cz, face, a, b + k, PG, depth=-1)
    gear(g, TX1 + 1, P + 24, C - 4, 'e', 5, 12, depth=0)
    gear(g, TX0 - 1, P + 30, C - 4, 'w', 4, 10, depth=0)
    gear(g, TX0 - 1, P + 21, C - 1, 'w', 2, 6, block=GOLD, depth=0)
    # the belfry: open arches on four sides, a great bell
    for x in range(TX0 + 1, TX1):
        for z in range(TZ0 + 1, TZ1):
            g.set(x, TT - 9, z, PD)
            for y in range(TT - 8, TT + 1):
                g.set(x, y, z, AIR)
    for y in range(TT - 8, TT - 1):
        for k in range(-3, 4):
            if abs(k) <= 2 or y < TT - 3:
                for (x, z) in [(C + k, TZ0), (C + k, TZ1), (TX0, C - 4 + k), (TX1, C - 4 + k)]:
                    if abs(k) < 3 or y < TT - 4:
                        g.set(x, y, z, AIR)
    g.set(C, TT, C - 4, PBB)
    g.set(C, TT - 1, C - 4, 'minecraft:bell', {'attachment': 'ceiling', 'facing': 'north', 'powered': 'false'})
    for x in range(TX0 - 1, TX1 + 2):
        for z in range(TZ0 - 1, TZ1 + 2):
            g.set(x, TT + 1, z, PBB)
    # the spire: an octagonal needle with lucarnes, ringed in gold, tipped with an eye
    cone(g, C, C - 4, 7.0, TT + 2, 36, lambda x, y, z: DT if (y % 6) else GOLD, power=1.25)
    for s in (-1, 1):
        for k in range(5):
            g.set(C + s * 4, TT + 6 + k, C - 4, PG)
            g.set(C, TT + 6 + k, C - 4 + s * 4, PG)
    for y in range(TT + 38, TT + 44):
        g.set(C, y, C - 4, GOLD)
    blob(g, C, TT + 45, C - 4, 1.6, 1.6, 1.6, CO)
    g.set(C, TT + 47, C - 4, 'minecraft:lightning_rod')
    # pinnacles on the parapet
    for s in (-1, 1):
        for y in range(TT + 2, TT + 9):
            g.set(C + s * 4, y, TZ1 + 1, PBB)
            g.set(C + s * 4, y, TZ0 - 1, PBB)
        g.set(C + s * 4, TT + 9, TZ1 + 1, GOLD)
        g.set(C + s * 4, TT + 9, TZ0 - 1, GOLD)

    # the vestibule: the sealed south door, the north door into the Hall of Hours
    for x in range(C - 2, C + 3):
        for y in range(P + 1, P + 7):
            if abs(x - C) <= 1 or y < P + 6:
                g.set(x, y, TZ1, 'aurelia:paradox_seal' if abs(x - C) <= 1 and y < P + 5 else (AIR if abs(x - C) <= 1 else masonry(x, y, TZ1)))
    for x in range(C - 1, C + 2):
        for y in range(P + 1, P + 5):
            g.set(x, y, TZ1, 'aurelia:paradox_seal')
            g.set(x, y, TZ0, AIR)
    for z in range(TZ1 + 1, TZ1 + 4):                                  # steps up from the yard
        for x in range(C - 2, C + 3):
            g.set(x, P, z, PBB)
    lantern(g, C - 4, P + 7, C - 4, soul=True, hanging=True)
    lantern(g, C + 4, P + 7, C - 4, soul=True, hanging=True)
    g.set(C - 3, P + 1, C - 4, 'aurelia:time_snare')
    g.set(C + 3, P + 1, C - 4, 'aurelia:time_snare')

    # ---- the Hall of Hours: a long gothic hall behind the tower, flying buttresses, a steep roof
    HX0, HX1, HZ0, HZ1 = C - 12, C + 12, Z0 + 3, TZ0
    HW = P + 20
    for x in range(HX0, HX1 + 1):
        for z in range(HZ0, HZ1 + 1):
            edge = x in (HX0, HX1) or z == HZ0
            for y in range(P - 3, HW + 1):
                if edge:
                    g.set(x, y, z, masonry(x, y, z))
                elif y == P:
                    g.set(x, y, z, 'minecraft:polished_blackstone' if (x + z) % 2 else PD)
                elif z < HZ1:
                    g.set(x, y, z, AIR)
    for k in range(13):                                                # the steep roof, gable ends north and south
        for x in range(HX0 - 1 + k, HX1 + 2 - k):
            for z in range(HZ0 - 1, HZ1 + 1):
                g.set(x, HW + 1 + k, z, DT if (x in (HX0 - 1 + k, HX1 + 1 - k)) else (DT if z in (HZ0 - 1,) else AIR))
        for z in range(HZ0 - 1, HZ1 + 1):
            g.set(HX0 - 1 + k, HW + 1 + k, z, DT)
            g.set(HX1 + 1 - k, HW + 1 + k, z, DT)
    for k in range(13):                                                # fill the north gable, with a rose window
        for x in range(HX0 - 1 + k, HX1 + 2 - k):
            d = math.hypot(x - C, HW + 1 + k - (HW + 5))
            g.set(x, HW + 1 + k, HZ0, PG if d < 3.5 and d > 0.8 else (GOLD if d <= 0.8 else masonry(x, 0, 0)))
    for x in range(HX0 + 1, HX1):                                      # a ribbed vault line under the roof
        for z in range(HZ0 + 1, HZ1, 4):
            g.set(x, HW, z, PBB)
    for z in range(HZ0 + 3, HZ1 - 1, 5):                                # windows and flying buttresses down both sides
        for s in (-1, 1):
            xw = C + s * 12
            for y in range(P + 5, P + 16):
                g.set(xw, y, z, PG)
                g.set(xw, y, z + 1, PG)
            g.set(xw, P + 16, z, GOLD)
            px = C + s * 19
            for y in range(P - 3, P + 14):
                for dz in (0, 1):
                    g.set(px, y, z + dz, PBB)
            for y in range(P + 14, P + 18):
                g.set(px, y, z, 'minecraft:polished_blackstone_brick_wall')
            g.set(px, P + 18, z, GOLD)
            line(g, (px, P + 13, z + 0.5), (xw + s, HW - 1, z + 0.5), 0.6, PBB)
    for x in (HX0 + 1, HX1 - 1):                                       # lamps along the walls
        for z in range(HZ0 + 3, HZ1, 5):
            g.set(x, P + 8, z, PEARL, {'axis': 'y'})
    # the rite: three Clock Dials on pedestals across the hall, the Master Clock over the portal in the north wall
    dial_z = HZ0 + 7
    for i, dx in enumerate((-6, 0, 6)):
        g.set(C + dx, P + 1, dial_z, PBB)
        g.set(C + dx, P + 2, dial_z, 'aurelia:clock_dial', {'hour': str(CLOCK_INIT[i]), 'filled': 'false'})
        for k in range(-1, 2):
            g.set(C + dx + k, P, dial_z + 1, GOLD)
    for x in range(C - 3, C + 4):                                      # the portal alcove, purple glass behind
        for y in range(P + 1, P + 8):
            g.set(x, y, HZ0 - 1, PG if abs(x - C) <= 2 and y < P + 7 else PBB)
            g.set(x, y, HZ0, AIR if abs(x - C) <= 2 and y < P + 7 else PBB)
    for x in range(C - 2, C + 3):
        g.set(x, P, HZ0, GOLD)
    g.set(C, P + 1, HZ0 + 1, 'aurelia:waygate', {'realm': 'clockwork', 'active': 'false'})
    g.set(C, P + 7, HZ0 + 1, 'aurelia:master_clock', {'hour': str(CLOCK_TARGET)})
    clock_face(g, C, P + 12, HZ0 + 1, 's', 3, hour=CLOCK_TARGET, rim=GOLD, mark=BS, glow=PEARL)
    for s in (-1, 1):
        for y in range(P + 1, P + 10):
            g.set(C + s * 4, y, HZ0 + 1, PBB if y < P + 9 else GOLD)
        g.set(C + s * 4, P + 10, HZ0 + 1, 'minecraft:purple_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
    lectern(g, C - 3, P + 1, HZ0 + 11, 'south', 'The Paradox Keep',
            ["Vexor kept the Sovereign's clocks. She asked him for one more hour, and then another. He learned to take them, "
             "and found he could not stop. Now he eats the hours of everything that wanders into his Rift.",
             "The Hall of Hours is barred by the Paradox Seal while the Hour Wardens stand.",
             "Set every dial to the hour of the Master Clock. But the dials are linked: touching one winds it AND the next one "
             "along the row (the last drags the first). Count before you turn."])
    for s in (-1, 1):                                                  # side chapels with chests
        for z in range(HZ1 - 8, HZ1 - 3):
            for y in range(P + 1, P + 5):
                g.set(C + s * 12, y, z, AIR)
            for k in range(1, 4):
                g.set(C + s * (12 + k), P, z, PD)
                for y in range(P + 1, P + 5):
                    g.set(C + s * (12 + k), y, z, AIR)
                g.set(C + s * (12 + k), P + 5, z, PBB)
            g.set(C + s * 16, P + 1, z, masonry(0, 0, 0))
            g.set(C + s * 16, P + 2, z, masonry(0, 0, 0))
        g.set(C + s * 16, P + 1, HZ1 - 6, AIR)
        chest(g, C + s * 15, P + 1, HZ1 - 6, 'aurelia:chests/paradox_cache', 'west' if s > 0 else 'east')
        g.set(C + s * 15, P + 4, HZ1 - 4, PEARL, {'axis': 'y'})
    for z in range(HZ0 + 9, HZ1 - 1, 3):                                # pillars of the nave
        for s in (-1, 1):
            for y in range(P + 1, HW):
                g.set(C + s * 8, y, z, PBB if y % 5 else CD)
    for z in range(HZ0 + 9, HZ1):                                      # a gold-threaded carpet
        g.set(C, P + 1, z, 'minecraft:purple_carpet')

    # ---- the drifting fragments: torn-off rock islands chained over the keep
    for (fx, fy, fz, fr) in [(C - 22, P + 58, C - 22, 5), (C + 24, P + 64, C - 14, 6), (C - 26, P + 70, C + 8, 4), (C + 20, P + 54, C + 10, 4),
                             (C + 2, P + 82, C - 24, 5)]:
        for x in range(fx - fr - 1, fx + fr + 2):
            for z in range(fz - fr - 1, fz + fr + 2):
                d = math.hypot(x - fx, z - fz)
                if d > fr:
                    continue
                depth = int((fr - d) * 1.8 + rnd.uniform(0, 1.5))
                for y in range(fy - depth, fy + 1):
                    g.set(x, y, z, rock(x, y, z) if y < fy else 'minecraft:deepslate_tiles')
                if rnd.random() < 0.06:
                    g.set(x, fy - depth, z, CO)
        for y in range(fy + 1, fy + 6):                                 # a broken pillar and a lamp on each
            g.set(fx, y, fz, PBB if y < fy + 5 else GOLD)
        lantern(g, fx + 1, fy + 1, fz, soul=True)
        for (cx, cz) in [(fx - fr + 1, fz), (fx + fr - 1, fz)]:
            bottom = fy - int(fr * 1.8) - 1
            chain(g, cx, max(bottom - 14, P + 30), bottom, cz)
        gear(g, fx, fy - 2, fz + fr, 's', 2, 6, block=GOLD, depth=0)

    # ---- garrison
    for (x, z) in [(C - 4, TZ1 + 6), (C + 4, TZ1 + 6), (C - 9, TZ1 + 3), (C + 9, TZ1 + 3)]:
        g.ground_guard('aurelia:hour_warden', x, z, P + 1, 4)
    for (x, y, z) in [(C - 12, P + 12, C + 12), (C + 12, P + 14, C + 6), (C - 14, P + 18, C + 6), (C + 2, P + 10, C + 15)]:
        g.air_guard('aurelia:secondhand', x, y, z)
    for (x, z) in [(C, CHASM[0] + 2), (C, CHASM[1] - 2), (C - 20, Z1 - 8), (C + 20, C - 6), (C - 20, C - 16), (C + 30, 86), (C - 30, 86)]:
        g.ground_guard('aurelia:gearskitter', x, z, P + 1 if z < CHASM[1] + 2 else G + 1, 2)
    trim_air(g, G + 34)
    g.save('paradox_keep')
    return g


# ================================================================================================ SPORE CATHEDRAL
VALVES = None             # filled in by spore_cathedral(): template positions of the three valves


def spore_cathedral():
    global VALVES
    W = L = 97
    H = 96
    C = 48
    G = 6                     # the forest floor in template space
    P = G + 6                 # the cathedral podium
    rnd = random.Random(1301)
    g = Grid(W, H, L)
    BONE, CAL, SMQ = 'minecraft:bone_block', 'minecraft:calcite', 'minecraft:smooth_quartz'
    MG, PKG = 'minecraft:magenta_stained_glass', 'minecraft:pink_stained_glass'
    STEM, ROOTS, MROOT = 'minecraft:mushroom_stem', 'minecraft:mangrove_roots', 'minecraft:muddy_mangrove_roots'
    PEARL = 'minecraft:pearlescent_froglight'
    CAPM = ['minecraft:magenta_terracotta', 'minecraft:magenta_concrete', 'minecraft:magenta_wool']

    def capblock(x, y, z, d=0):
        h = (x * 7 + y * 13 + z * 5) % 23
        if h == 0 or h == 11:
            return PEARL
        if h in (5, 17):
            return 'minecraft:white_concrete'
        return CAPM[(x + 2 * z + y) % 3]

    def wall(x, y, z):
        r = rnd.random()
        return CAL if r < 0.5 else (BONE if r < 0.8 else ('minecraft:diorite' if r < 0.9 else SMQ))

    def bone_axis(axis):
        return {'axis': axis}

    # ---- the forest floor: mycelium and moss, a clearing round the cathedral
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d > 47.5:
                continue
            for y in range(0, G):
                g.set(x, y, z, 'minecraft:dirt' if y > G - 3 else 'minecraft:stone')
            r = rnd.random()
            g.set(x, G, z, 'minecraft:mycelium' if r < 0.55 else ('minecraft:moss_block' if r < 0.8 else 'minecraft:podzol'))
            for y in range(G + 1, H):
                g.set(x, y, z, AIR)
            if r > 0.97:
                g.set(x, G + 1, z, rnd.choice(['minecraft:red_mushroom', 'minecraft:brown_mushroom', 'minecraft:fern', 'minecraft:crimson_roots']))

    # ---- the podium and the grand stair (south), a narthex landing before the doors
    PX0, PX1, PZ0, PZ1 = C - 33, C + 33, C - 36, C + 22
    for x in range(PX0, PX1 + 1):
        for z in range(PZ0, PZ1 + 1):
            edge = x in (PX0, PX1) or z in (PZ0, PZ1)
            for y in range(G, P + 1):
                g.set(x, y, z, (BONE if y == P else wall(x, y, z)) if not (y == P and not edge) else ('minecraft:polished_diorite' if (x + z) % 4 else CAL))
            if edge and (x + z) % 4 == 0:
                g.set(x, P + 1, z, 'minecraft:diorite_wall')
    SW = 9
    for z in range(PZ1 + 1, PZ1 + 1 + (P - G) * 2):
        step = (z - PZ1 - 1) // 2
        y = P - step
        for x in range(C - SW, C + SW + 1):
            for yy in range(G, y):
                g.set(x, yy, z, wall(x, yy, z))
            if (z - PZ1 - 1) % 2 == 0:
                g.set(x, y, z, 'minecraft:quartz_stairs', stairs('north'))
            else:
                g.set(x, y - 1, z, 'minecraft:quartz_slab', {'type': 'top', 'waterlogged': 'false'})
                g.set(x, y, z, AIR)
        for x in (C - SW - 1, C + SW + 1):                                # balustrades
            for yy in range(G, y + 2):
                g.set(x, yy, z, CAL if yy <= y else 'minecraft:diorite_wall')
    for k in (2, 6, 10):
        g.set(C - 3 + k // 2, P - (k // 2), PZ1 + 1 + k, 'aurelia:root_snare')
    # colossal, overgrown statues at the foot of the stair: hooded saints cradling spore lights, a cap grown through each hood
    for s in (-1, 1):
        sx, sz = C + s * 17, PZ1 + 12
        statue(g, sx, G + 1, sz, 's', 28, CAL, BONE, 'minecraft:blackstone', 'minecraft:shroomlight', held='orb',
               overgrown=[('minecraft:moss_block', 0.16), ('minecraft:mossy_cobblestone', 0.06), (ROOTS, 0.04)], rnd=rnd)
        cap(g, sx, G + 1 + 34, sz - 1, 6, 4, capblock, gill='minecraft:pink_terracotta')
        for y in range(G + 31, G + 35):
            g.set(sx, y, sz - 1, STEM)
        for k in range(6):                                              # vines hanging from the shoulders
            for y in range(G + 12, G + 22):
                if rnd.random() < 0.5:
                    pass

    # ---- the cathedral body: nave, transept, apse
    NX0, NX1, NZ0, NZ1 = C - 11, C + 11, C - 20, C + 19            # nave (the facade at NZ1)
    TX0, TX1, TZ0, TZ1 = C - 27, C + 27, C - 20, C - 4             # transept
    XC, ZC = C, C - 12                                             # the crossing, under the great dome
    HW = P + 24

    def inside(x, z):
        return (NX0 < x < NX1 and NZ0 < z < NZ1) or (TX0 < x < TX1 and TZ0 < z < TZ1) or math.hypot(x - XC, z - NZ0) < 9 and z <= NZ0 + 1

    def footprint(x, z):
        return (NX0 <= x <= NX1 and NZ0 <= z <= NZ1) or (TX0 <= x <= TX1 and TZ0 <= z <= TZ1) or math.hypot(x - XC, z - NZ0) <= 10 and z <= NZ0

    for x in range(TX0 - 1, TX1 + 2):
        for z in range(NZ0 - 11, NZ1 + 2):
            if not footprint(x, z):
                continue
            ins = inside(x, z)
            for y in range(P, HW + 1):
                if y == P:
                    g.set(x, y, z, ('minecraft:polished_diorite' if (x + z) % 2 else CAL) if ins else BONE)
                elif ins:
                    g.set(x, y, z, AIR)
                else:
                    g.set(x, y, z, BONE if y % 6 == 0 else wall(x, y, z))
    # lancet windows of magenta glass all round, bone mullions
    for x in range(TX0 - 1, TX1 + 2):
        for z in range(NZ0 - 11, NZ1 + 2):
            if footprint(x, z) and not inside(x, z):
                if (x + z) % 4 == 0 and not (abs(x - C) <= 4 and z >= NZ1 - 1):
                    for y in range(P + 5, P + 16):
                        g.set(x, y, z, MG if y < P + 15 else PEARL, {'axis': 'y'} if y == P + 15 else None)
    # roofs: a steep pitched roof over nave and transept arms, bone ridges, glowing mushroom spots
    def roof(x0, x1, z0, z1, along_z):
        span = (x1 - x0) if along_z else (z1 - z0)
        for k in range(span // 2 + 2):
            for x in range(x0 - 1, x1 + 2):
                for z in range(z0 - 1, z1 + 2):
                    a = (x - x0 + 1) if along_z else (z - z0 + 1)
                    b = (x1 + 1 - x) if along_z else (z1 + 1 - z)
                    if min(a, b) == k:
                        g.set(x, HW + 1 + k, z, capblock(x, HW + k, z) if k < span // 2 + 1 else BONE)
    roof(NX0, NX1, ZC + 9, NZ1, True)
    roof(TX0, XC - 10, TZ0, TZ1, False)
    roof(XC + 10, TX1, TZ0, TZ1, False)
    roof(NX0, NX1, NZ0 - 9, TZ0, True)
    # the drum and the great mushroom dome over the crossing
    cyl(g, XC, ZC, 11, HW - 2, HW + 10, lambda x, y, z: MG if (y > HW + 2 and y < HW + 9 and (x + z) % 3 == 0) else wall(x, y, z), hollow=1.5)
    for x in range(XC - 10, XC + 11):
        for z in range(ZC - 10, ZC + 11):
            if math.hypot(x - XC, z - ZC) < 9.6:
                for y in range(P + 1, HW + 11):
                    g.set(x, y, z, AIR)
    cap(g, XC, HW + 10, ZC, 21, 16, capblock, gill='minecraft:pink_terracotta', thick=1.7)
    for y in range(HW + 26, HW + 32):                                # a glowing finial
        g.set(XC, y, ZC, STEM if y < HW + 30 else PEARL, {'axis': 'y'} if y >= HW + 30 else None)
    cap(g, XC, HW + 31, ZC, 3, 2, capblock)
    for k in range(8):                                               # spore lamps hanging in the dome
        a = k * math.pi / 4
        x, z = round(XC + 6 * math.cos(a)), round(ZC + 6 * math.sin(a))
        for y in range(HW + 4, HW + 12):
            g.set(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
        g.set(x, HW + 3, z, 'minecraft:shroomlight')
    # two lesser domes over the transept arms
    for s in (-1, 1):
        dx = C + s * 19
        cyl(g, dx, ZC, 6, HW - 1, HW + 6, lambda x, y, z: MG if (y > HW + 1 and (x + z) % 3 == 0) else wall(x, y, z), hollow=1.2)
        cap(g, dx, HW + 6, ZC, 10, 8, capblock, gill='minecraft:pink_terracotta')
        g.set(dx, HW + 15, ZC, PEARL, {'axis': 'y'})
    # twin facade towers crowned with mushroom caps
    for s in (-1, 1):
        tx, tz = C + s * 15, NZ1 - 2
        for x in range(tx - 4, tx + 5):
            for z in range(tz - 4, tz + 5):
                edge = abs(x - tx) == 4 or abs(z - tz) == 4
                for y in range(G, P + 54):
                    if edge or y <= P:
                        g.set(x, y, z, BONE if (abs(x - tx) == 4 and abs(z - tz) == 4) else wall(x, y, z))
                    else:
                        g.set(x, y, z, AIR)
        for y in range(P + 8, P + 48, 8):                              # lancets
            for k in range(5):
                g.set(tx, y + k, tz + 4, MG)
                g.set(tx + s * 4, y + k, tz, MG)
        cyl(g, tx, tz, 4, P + 54, P + 60, STEM)
        cap(g, tx, P + 60, tz, 10, 9, capblock, gill='minecraft:pink_terracotta')
        g.set(tx, P + 70, tz, PEARL, {'axis': 'y'})
        for (cx, cz) in [(tx - 4, tz - 4), (tx + 4, tz - 4), (tx - 4, tz + 4), (tx + 4, tz + 4)]:
            for y in range(P + 54, P + 57):
                g.set(cx, y, cz, BONE)
    # the facade: a gable, a rose window, the great doors under a pointed arch
    for k in range(10):
        for x in range(NX0 + k, NX1 - k + 1):
            g.set(x, HW + 1 + k, NZ1, wall(x, 0, 0))
    for x in range(C - 7, C + 8):
        for y in range(P + 12, P + 27):
            d = math.hypot(x - C, y - (P + 19))
            if d <= 6.5:
                spoke = any(abs(math.sin(math.atan2(y - P - 19, x - C) - k * math.pi / 6)) * d < 0.6 for k in range(6))
                g.set(x, y, NZ1, BONE if (d > 5.6 or spoke or d < 1.2) else (MG if d > 3 else PKG))
                if d < 1.2:
                    g.set(x, y, NZ1, PEARL, {'axis': 'y'})
    for x in range(C - 4, C + 5):                                    # the arch: steps of bone around the door
        for y in range(P + 1, P + 12):
            dx = abs(x - C)
            if dx <= 2 and y <= P + 8 or (dx <= 1 and y <= P + 9):
                g.set(x, y, NZ1, 'aurelia:root_seal')
                g.set(x, y, NZ1 + 1, AIR)
            elif (dx - 1) ** 2 + max(0, y - P - 6) ** 2 * 0.6 <= 16:
                g.set(x, y, NZ1 + 1, BONE)
    for x in range(C - SW, C + SW + 1):                               # the narthex landing
        for z in range(NZ1 + 1, PZ1 + 1):
            if g.get(x, P + 1, z) and g.get(x, P + 1, z)[0] == 'minecraft:bone_block' and abs(x - C) <= 2:
                g.set(x, P + 1, z, AIR)

    # ---- roots: radiating over the ground from the podium, climbing as flying buttresses to the walls
    def rootpick(x, y, z):
        return MROOT if rnd.random() < 0.25 else (ROOTS if rnd.random() < 0.55 else STEM)
    for k in range(18):
        a = k * 2 * math.pi / 18 + rnd.uniform(-0.1, 0.1)
        if abs(math.sin(a) - 1) < 0.25 and math.cos(a) ** 2 < 0.12:     # keep the stair clear
            continue
        sx, sz = C + 33 * math.cos(a), C - 7 + 33 * math.sin(a)
        if C - SW - 3 < sx < C + SW + 3 and sz > PZ1 - 2:
            continue
        ex, ez = C + 46 * math.cos(a), C - 6 + 46 * math.sin(a)
        mx, mz = (sx + ex) / 2, (sz + ez) / 2
        bez(g, (sx, P, sz), (mx, P + 3, mz), (ex, G - 1, ez), lambda t: 2.3 * (1 - t) + 0.7, rootpick)
    for z in list(range(NZ0 + 2, TZ0 - 1, 6)) + list(range(TZ1 + 3, NZ1 - 5, 6)):   # root buttresses along the nave
        for s in (-1, 1):
            xw = C + s * 9
            fx = C + s * (21 if z > TZ1 else 17)
            if TZ0 <= z <= TZ1:
                continue
            for y in range(P, P + 12):
                for dx in (0, s):
                    for dz in (0, 1):
                        g.set(fx + dx, y, z + dz, rootpick(fx, y, z))
            g.set(fx, P + 12, z, PEARL, {'axis': 'y'})
            bez(g, (fx, P + 11, z + 0.5), (fx - s * 1, HW + 2, z + 0.5), (xw + s, HW - 2, z + 0.5), 1.1, rootpick)
    for s in (-1, 1):                                                  # roots gripping the transept ends
        for k in range(4):
            bez(g, (C + s * (TX1 - C + 1), HW - 2 - 4 * k, TZ0 + 3 + 3 * k), (C + s * (TX1 - C + 7), HW - 6 - 4 * k, TZ0 + 4 * k),
                (C + s * (TX1 - C + 12), G, TZ0 - 2 + 6 * k), 1.3, rootpick)

    # ---- giant mushrooms in the clearing
    for (mx, mz, h, r) in [(C - 36, C - 20, 22, 8), (C + 37, C - 26, 26, 9), (C - 38, C + 18, 18, 7), (C + 36, C + 22, 20, 7),
                           (C - 22, C - 40, 16, 6), (C + 18, C - 42, 14, 6), (C - 27, C + 38, 12, 5), (C + 28, C + 39, 13, 5)]:
        cyl(g, mx, mz, 1.6 if r > 6 else 1.2, G, G + h, STEM)
        cap(g, mx, G + h, mz, r, r * 0.7, capblock, gill='minecraft:pink_terracotta')
        for k in range(3):
            g.set(mx + rnd.choice((-3, 3)), G + h - 1, mz + rnd.choice((-3, 3)), 'minecraft:spore_blossom')

    # ---- inside: the spore pool under the dome, the portal on its dais, the three valves and their glowing veins
    POOL_R = 6.5
    for x in range(XC - 8, XC + 9):
        for z in range(ZC - 8, ZC + 9):
            d = math.hypot(x - XC, z - ZC)
            if 2.5 < d <= POOL_R and not (abs(x - XC) <= 1 or abs(z - ZC) <= 1):
                g.set(x, P - 2, z, PEARL, {'axis': 'y'})
                g.set(x, P - 1, z, 'minecraft:water', {'level': '0'})
                g.set(x, P, z, 'minecraft:water', {'level': '0'})
            elif POOL_R < d <= POOL_R + 1:
                g.set(x, P, z, BONE)
                if (x + z) % 3 == 0:
                    g.set(x, P + 1, z, 'minecraft:magenta_candle', {'candles': '2', 'lit': 'true', 'waterlogged': 'false'})
            elif d <= 2.5:
                g.set(x, P, z, 'minecraft:chiseled_quartz_block')
    g.set(XC, P + 1, ZC, 'aurelia:waygate', {'realm': 'mycelial', 'active': 'false'})
    for (x, z) in [(XC - 1, ZC - 1), (XC + 1, ZC - 1), (XC - 1, ZC + 1), (XC + 1, ZC + 1)]:
        g.set(x, P + 1, z, 'minecraft:end_rod', {'facing': 'up'})
    VALVES = [(XC - 15, P + 1, ZC), (XC + 15, P + 1, ZC), (XC, P + 1, NZ0 - 5)]
    for (vx, vy, vz) in VALVES:
        g.set(vx, vy - 1, vz, 'minecraft:chiseled_quartz_block')
        g.set(vx, vy, vz, 'aurelia:spore_valve', {'open': 'false', 'locked': 'false'})
        n = int(math.hypot(vx - XC, vz - ZC))
        for k in range(2, n - 7):                                        # a vein of light in the floor, from valve to pool
            t = k / n
            x, z = round(vx + (XC - vx) * t), round(vz + (ZC - vz) * t)
            g.set(x, P, z, 'minecraft:magenta_glazed_terracotta' if k % 3 else PEARL, {'facing': 'north'} if k % 3 else {'axis': 'y'})
        for y in range(vy + 1, vy + 4):                                  # the valve's pipe up into the vault
            g.set(vx, y + 3, vz, 'minecraft:waxed_copper_block' if y < vy + 3 else 'minecraft:waxed_cut_copper')
    lectern(g, XC + 4, P + 1, ZC + 9, 'south', 'The Spore Cathedral',
            ["The Bloom Mother was the Sovereign's gardener. When the crown was broken she went down into the dark under the roots "
             "and let the garden grow into her. What she sings now is not a hymn.",
             "The doors are barred by the Root Seal while the Husk Guards stand.",
             "Three valves feed the spore pool. Each one shuts itself again twelve heartbeats after it is opened. "
             "Open all three before the first one closes, and the pool will carry you down to her."])
    for (x, z) in [(XC + s * 7, z) for s in (-1, 1) for z in range(TZ1 + 4, NZ1 - 2, 5)]:   # nave columns of bone
        for y in range(P + 1, HW):
            g.set(x, y, z, BONE if y % 4 else PEARL, {'axis': 'y'})
    for s in (-1, 1):                                                   # side chapels in the transept arms with chests
        chest(g, C + s * 24, P + 1, TZ0 + 2, 'aurelia:chests/cathedral_cache', 'south')
        g.set(C + s * 23, P + 1, TZ0 + 2, 'minecraft:magenta_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})
    chest(g, XC, P + 1, NZ0 - 7, 'aurelia:chests/cathedral_cache', 'south')
    for z in range(TZ1 + 1, NZ1):
        g.set(C, P + 1, z, 'minecraft:magenta_carpet')
    for k in range(3):
        g.set(C + (1 if k % 2 else -1), P, TZ1 + 6 + 4 * k, 'aurelia:root_snare')
    for x in range(TX0 + 1, TX1):                                       # spore blossoms in the vault
        for z in range(NZ0 - 8, NZ1):
            if inside(x, z) and math.hypot(x - XC, z - ZC) > 10 and rnd.random() < 0.025:
                if g.get(x, HW + 1, z) is not None:
                    g.set(x, HW, z, 'minecraft:spore_blossom')

    # ---- garrison
    for (x, z) in [(C - 4, NZ1 + 2), (C + 4, NZ1 + 2), (C - 7, NZ1 + 1), (C + 7, NZ1 + 1)]:
        g.ground_guard('aurelia:husk_guard', x, z, P + 1, 3)
    for (x, y, z) in [(C, P + 8, C), (C - 4, P + 10, TZ1 + 2), (C + 10, P + 8, ZC), (C - 10, P + 8, ZC), (C, P + 14, C + 26)]:
        g.air_guard('aurelia:spore_drifter', x, y, z)
    for (x, z) in [(C - 25, C + 30), (C + 25, C + 30), (C - 38, C), (C + 38, C - 4), (C, C - 44), (C - 30, PZ0 - 4)]:
        g.ground_guard('aurelia:root_grub', x, z, G + 1, 1)
    trim_air(g, G + 34)
    g.save('spore_cathedral')
    return g


if __name__ == '__main__':
    moves = clock_moves(CLOCK_INIT, CLOCK_TARGET)
    assert moves is not None, 'the clock rite is unsolvable'
    print(f'clock rite: {CLOCK_INIT} -> {CLOCK_TARGET} in {moves} touches')
    paradox_keep()
    spore_cathedral()
