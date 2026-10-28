"""The Gibbet Spire: the frontier's common cage tower.

An octagonal birdcage spire on a rock plinth. Three caged tiers step inward, each ringed by a walkable ledge; a timber
stair winds round the outside from the plinth to the crown; gibbet cages hang from beams on every tier; the crown is a
domed birdcage holding the vault, lit by a brazier on a hook you can see from far off.

Fights: the Swarm Pen (ground insects), the Hatchery (nest defenders, the brood can be smashed), the Aerie (predators
burst from the hanging cages), the Crown (an alpha and its escorts; clearing it opens the vault cage).
"""
import math

from common import *
from kit import AIR, B, Build, h

W = L = 47
H = 100
C = 23
G = 6                       # local y of the surrounding ground
TIERS = [  # (floor y, apothem, height)
    (G + 5, 14, 16),
    (G + 22, 12, 15),
    (G + 38, 10, 14),
]
CROWN_Y = G + 53
CROWN_R = 9


def build():
    b = Build('gibbet_spire', W, H, L, seed=11)
    plinth(b)
    for i, (fy, r, ht) in enumerate(TIERS):
        tier(b, i, fy, r, ht)
    buttresses(b)
    ledges(b)
    crown(b)
    outer_stair(b)
    gibbets(b)
    interiors(b)
    zones(b)
    b.meta.update({'kind': 'cage_tower', 'title': 'Gibbet Spire', 'ground': G})
    return b


# ---------------------------------------------------------------- plinth: a rock knuckle the tower grips
def plinth(b):
    top = G + 4
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            edge = 21.5 + 2.2 * math.sin(math.atan2(z - C, x - C) * 5 + 1) + h(x, 0, z, 9) * 1.5
            if d > edge:
                continue
            # the rock slopes from the tower down to the ground line
            ytop = top if d < 16 else int(top - (d - 16) * 1.1 - h(x, 1, z, 4) * 1.5)
            for y in range(0, max(0, ytop) + 1):
                b.set(x, y, z, rock(x, y, z, 2))
            if ytop >= G and d >= 16 and h(x, 2, z, 7) < 0.35:
                b.set(x, ytop + 1, z, MOSS_CARPET if h(x, 3, z) < 0.5 else 'minecraft:short_grass')
    # the paved apron the tower stands on
    for x in range(W):
        for z in range(L):
            if in_octagon(x, z, C, C, 16):
                b.set(x, top, z, weathered(x, top, z, DEEP_TILE, DEEP_TILE_CRACK, salt=5, crack=0.25))
                if on_octagon_rim(x, z, C, C, 16) and h(x, 0, z, 1) < 0.8:
                    b.set(x, top + 1, z, wall('polished_blackstone_brick'))
                    if h(x, 1, z, 2) < 0.12:
                        b.set(x, top + 2, z, SKULL)
    # roots of chain anchoring the spire, and old bones in the rock
    for k in range(8):
        a = math.radians(45 * k + 10)
        p0 = (C + 13 * math.cos(a), top + 3, C + 13 * math.sin(a))
        p1 = (C + 21 * math.cos(a), G - 1, C + 21 * math.sin(a))
        b.line(p0, p1, CHAIN_Y)
    for k in range(14):
        x, z = C + int(19 * math.cos(k)), C + int(19 * math.sin(k * 1.7))
        if 0 <= x < W and 0 <= z < L and h(x, 0, z, 33) < 0.6:
            b.set(x, G + 1, z, BONE_X if k % 2 else BONE_Z)


# ---------------------------------------------------------------- a caged tier
def tier(b, i, fy, r, ht):
    top = fy + ht
    for x in range(W):
        for z in range(L):
            if not in_octagon(x, z, C, C, r):
                continue
            # floor
            b.set(x, fy, z, weathered(x, fy, z, DEEP_TILE, DEEP_TILE_CRACK, salt=i, crack=0.2))
            rim = on_octagon_rim(x, z, C, C, r)
            ang = math.degrees(math.atan2(z - C, x - C)) % 45
            corner = rim and (ang < 6 or ang > 39)
            for y in range(fy + 1, top):
                dy = y - fy
                if not rim:
                    b.set(x, y, z, AIR)
                    continue
                if corner:
                    b.set(x, y, z, BASALT if dy % 6 else DARK_CHISEL)
                elif dy in (ht - 1,):
                    b.set(x, y, z, dark_stone(x, y, z))
                elif dy == ht // 2:
                    b.set(x, y, z, DARK_CHISEL if h(x, y, z, 2) < 0.5 else DARK_BRICK)
                elif dy == 1:
                    b.set(x, y, z, wall('polished_blackstone_brick'))
                else:
                    b.set(x, y, z, BARS)
            # cornice and corner spikes at the top of the tier
            if rim:
                b.set(x, top, z, dark_stone(x, top, z))
                if corner:
                    for k in range(1, 4):
                        b.set(x, top + k, z, wall('polished_blackstone_brick') if k < 3 else ROD_UP)
    # gaps: one bent-bar breach per side, at different heights per tier
    for s in range(8):
        a = math.radians(45 * s)
        for t in (-1, 0, 1):
            gx = round(C + (r - 0.5) * math.cos(a) - t * math.sin(a))
            gz = round(C + (r - 0.5) * math.sin(a) + t * math.cos(a))
            if (s + i) % 3 == 0:
                for y in range(fy + 2, fy + 5):
                    if b.get(gx, y, gz) == BARS:
                        b.set(gx, y, gz, AIR)
                        if h(gx, y, gz, 8) < 0.5:
                            b.set(gx, fy + 1, gz, B('iron_bars'))


def buttresses(b):
    """Stepped piers at every corner of every tier, with a pinnacle, and an overhanging cornice: the spire's silhouette."""
    for i, (fy, r, ht) in enumerate(TIERS):
        top = fy + ht
        for k in range(8):
            a = math.radians(45 * k + 22.5)
            ux, uz = math.cos(a), math.sin(a)
            base_y = G + 1 if i == 0 else fy - 1
            for y in range(base_y, top + 1):
                frac = (y - base_y) / max(1, top - base_y)
                reach = 3.2 - 2.0 * frac          # thick at the foot, slim at the top
                for d in [r * 1.0 + t * 0.5 for t in range(int(reach * 2) + 1)]:
                    for side in (-0.6, 0.6):
                        x = round(C + d * ux - side * uz)
                        z = round(C + d * uz + side * ux)
                        b.set(x, y, z, dark_stone(x, y, z) if (y - base_y) % 7 else DARK_CHISEL, over=False)
            # pinnacle
            px, pz = round(C + (r + 0.6) * ux), round(C + (r + 0.6) * uz)
            for k2, blk in enumerate([DARK_CHISEL, wall('polished_blackstone_brick'), wall('polished_blackstone_brick'), ROD_UP]):
                b.set(px, top + 1 + k2, pz, blk)
        # chain swags between neighbouring pinnacles, and a few torn banners under the cornice
        for k in range(8):
            a0, a1 = math.radians(45 * k + 22.5), math.radians(45 * k + 67.5)
            p0 = (C + (r + 0.6) * math.cos(a0), top + 2, C + (r + 0.6) * math.sin(a0))
            p1 = (C + (r + 0.6) * math.cos(a1), top + 2, C + (r + 0.6) * math.sin(a1))
            mid = ((p0[0] + p1[0]) / 2 * 1.04 - C * 0.04, top - 1, (p0[2] + p1[2]) / 2 * 1.04 - C * 0.04)
            if (k + i) % 2 == 0:
                b.curve([p0, mid, p1], CHAIN_X, over=False)
            if (k + i) % 3 == 1:
                am = math.radians(45 * k + 45)
                face = ['east', 'south', 'west', 'north'][int(((45 * k + 45 + 45) % 360) // 90)]
                bx, bz = round(C + (r + 1) * math.cos(am)), round(C + (r + 1) * math.sin(am))
                b.set(bx, top - 1, bz, B('red_wall_banner' if (k + i) % 2 else 'black_wall_banner', facing=face), over=False)
        # the cornice: a slab lip one block proud of the wall
        for x in range(W):
            for z in range(L):
                if in_octagon(x, z, C, C, r + 1) and not in_octagon(x, z, C, C, r):
                    b.set(x, top, z, slab('polished_blackstone_brick', 'top'), over=False)
                    if h(x, top, z, 77) < 0.5 and b.get(x, top - 1, z) in (None, AIR):
                        b.set(x, top - 1, z, B('polished_blackstone_brick_stairs', facing='north', half='top', shape='straight', waterlogged='false'), over=False)


def ledges(b):
    """The rim left where each tier steps in: a walkable ledge with a parapet and skulls on spikes."""
    for i in range(1, len(TIERS)):
        fy, r, _ = TIERS[i]
        rb = TIERS[i - 1][1]
        for x in range(W):
            for z in range(L):
                if in_octagon(x, z, C, C, rb) and not in_octagon(x, z, C, C, r):
                    b.set(x, fy, z, weathered(x, fy, z, DARK_BRICK, DARK_CRACK, salt=40 + i))
                    if on_octagon_rim(x, z, C, C, rb):
                        b.set(x, fy + 1, z, wall('polished_blackstone_brick') if h(x, fy, z, 3) < 0.85 else AIR)


# ---------------------------------------------------------------- the crown: a domed birdcage with the vault
def crown(b):
    fy = CROWN_Y
    r = CROWN_R
    for x in range(W):
        for z in range(L):
            if in_octagon(x, z, C, C, TIERS[-1][1]) and not in_octagon(x, z, C, C, r + 1):
                b.set(x, fy, z, dark_stone(x, fy, z))
            if math.hypot(x - C, z - C) <= r + 0.5:
                b.set(x, fy, z, weathered(x, fy, z, DEEP_TILE, DEEP_TILE_CRACK, salt=50))
    ry = 17
    for x in range(C - r - 1, C + r + 2):
        for z in range(C - r - 1, C + r + 2):
            for y in range(fy + 1, fy + ry + 1):
                d = ((x - C) / (r + 0.5)) ** 2 + ((y - fy) / ry) ** 2 + ((z - C) / (r + 0.5)) ** 2
                ang = math.degrees(math.atan2(z - C, x - C)) % 45
                if 0.82 <= d <= 1.0:
                    rib = ang < 5 or ang > 40
                    b.set(x, y, z, BASALT if rib else BARS)
                elif d < 0.82:
                    b.set(x, y, z, AIR)
    # gates where the outer stair arrives and on the far side
    for dz in (-1, 0, 1):
        for y in range(fy + 1, fy + 4):
            b.set(C + r, y, C + dz, AIR)
            b.set(C - r, y, C + dz, AIR)
    # apex ring, hook and brazier: the light you see from a distance
    top = fy + ry
    b.cylinder(C, C, 2.6, top - 1, top, lambda x, y, z: GILDED if h(x, y, z) < 0.4 else DARK_CHISEL)
    for y in range(top + 1, top + 9):
        b.set(C, y, C, CHAIN_Y)
    b.box(C - 1, top + 9, C - 1, C + 1, top + 9, C + 1, DARK_CHISEL)
    b.set(C, top + 10, C, B('soul_campfire', facing='north', lit='true', signal_fire='true', waterlogged='false'))
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        b.set(C + dx, top + 10, C + dz, SHROOM)
        b.set(C + 2 * dx, top + 9, C + 2 * dz, ROD_UP if dx else SHROOM)
    # chains hanging inside the dome, a lantern at each
    for k in range(6):
        a = math.radians(60 * k)
        x, z = round(C + 4 * math.cos(a)), round(C + 4 * math.sin(a))
        yb = fy + 7 + k % 3
        for y in range(yb, top - 2):
            if b.get(x, y, z) in (None, AIR):
                b.set(x, y, z, CHAIN_Y)
        b.set(x, yb - 1, z, SOUL_LANTERN)
    # the vault: a gilded cage on a dais; its front bars open when the crown is won
    b.cylinder(C, C, 2.5, fy + 1, fy + 1, GILDED)
    for x in range(C - 1, C + 2):
        for z in range(C - 1, C + 2):
            for y in range(fy + 2, fy + 5):
                edge = x in (C - 1, C + 1) or z in (C - 1, C + 1)
                b.set(x, y, z, B('iron_bars') if edge else AIR)
    b.box(C - 1, fy + 5, C - 1, C + 1, fy + 5, C + 1, GILDED)
    b.chest(C, fy + 2, C, 'chests/crown_vault', facing='south')
    b.point('vault', C, fy + 2, C)
    b.meta['gates'] = {'crown': [[C - 1, y, C + 1] for y in range(fy + 2, fy + 5)] + [[C, y, C + 1] for y in range(fy + 2, fy + 5)]
                       + [[C + 1, y, C + 1] for y in range(fy + 2, fy + 5)]}


# ---------------------------------------------------------------- the outer stair
def outer_stair(b):
    """A timber stair spiralling round the outside, two blocks wide, chain-railed, bracketed into the walls."""
    y0 = G + 5
    y1 = CROWN_Y
    turns = 2.1
    steps = 900
    last = None
    for k in range(steps + 1):
        t = k / steps
        theta = math.radians(-90) + t * turns * 2 * math.pi
        y = y0 + (y1 - y0) * t
        r_wall = next((r for fy, r, ht in TIERS if fy <= y < fy + ht + 1), CROWN_R + 1)
        if y >= CROWN_Y - 1:
            r_wall = TIERS[-1][1]
        rad = r_wall + 3.0
        for w in (0.0,):
            x = C + (rad + w) * math.cos(theta)
            z = C + (rad + w) * math.sin(theta)
            yi = int(y)
            xi, zi = round(x), round(z)
            if (xi, yi, zi) == last:
                continue
            b.set(xi, yi, zi, slab('dark_oak', 'top') if (y - yi) < 0.5 else OAK_DARK)
            b.set(xi, yi + 1, zi, AIR)
            b.set(xi, yi + 2, zi, AIR)
            if k % 9 == 0:
                ox_, oz_ = round(C + (rad + 1) * math.cos(theta)), round(C + (rad + 1) * math.sin(theta))
                b.set(ox_, yi + 1, oz_, fence(), over=False)
                b.set(ox_, yi + 2, oz_, CHAIN_Y if k % 54 else LANTERN_STAND, over=False)
        if k % 40 == 0:
            # a bracket back into the wall
            for d in range(int(r_wall) - 1, int(rad) + 1):
                bx, bz = round(C + d * math.cos(theta)), round(C + d * math.sin(theta))
                b.set(bx, int(y) - 1, bz, STRIPPED_X if abs(math.cos(theta)) > 0.7 else STRIPPED_Z, over=False)
        if k % 75 == 0:
            b.set(round(C + (rad + 1.6) * math.cos(theta)), int(y) + 3, round(C + (rad + 1.6) * math.sin(theta)), LANTERN, over=False)
    # where the stair meets each tier floor, a door through the bars
    for i, (fy, r, ht) in enumerate(TIERS):
        for s in range(8):
            a = math.radians(45 * s + 22.5)
            for t in (-1, 0, 1):
                x = round(C + (r - 0.5) * math.cos(a) - t * math.sin(a))
                z = round(C + (r - 0.5) * math.sin(a) + t * math.cos(a))
                for y in range(fy + 1, fy + 4):
                    near = any(b.get(x + dx, fy, z + dz) == OAK_DARK or b.get(x + dx, fy, z + dz) == 'minecraft:dark_oak_slab'
                               for dx in (-3, -2, -1, 0, 1, 2, 3) for dz in (-3, -2, -1, 0, 1, 2, 3))
                    if near and b.get(x, y, z) in (BARS, 'minecraft:polished_blackstone_brick_wall'):
                        b.set(x, y, z, AIR)


# ---------------------------------------------------------------- gibbet cages hung from beams
def gibbets(b):
    spots = [(0, 20, 6, 'bones'), (0, 160, 8, 'loot'), (0, 270, 5, 'empty'),
             (1, 70, 7, 'bones'), (1, 200, 6, 'flyer'), (1, 320, 9, 'loot'),
             (2, 120, 6, 'flyer'), (2, 240, 8, 'bones')]
    b.meta['gibbets'] = []
    for i, deg, drop, kind in spots:
        fy, r, ht = TIERS[i]
        top = fy + ht
        a = math.radians(deg)
        # beam out from the cornice
        for d in range(r - 1, r + 6):
            x, z = round(C + d * math.cos(a)), round(C + d * math.sin(a))
            b.set(x, top, z, DARK_LOG_X if abs(math.cos(a)) > 0.7 else DARK_LOG_Z)
        ex, ez = round(C + (r + 5) * math.cos(a)), round(C + (r + 5) * math.sin(a))
        cy = top - drop
        for y in range(cy + 4, top):
            b.set(ex, y, ez, CHAIN_Y)
        # the cage: 3x3 footprint, 3 tall, bars round a slab floor, a tapered cap
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                b.set(ex + dx, cy, ez + dz, slab('polished_blackstone', 'top'))
                for y in range(cy + 1, cy + 4):
                    b.set(ex + dx, y, ez + dz, B('iron_bars') if (dx or dz) else AIR)
                b.set(ex + dx, cy + 4, ez + dz, slab('polished_blackstone', 'bottom') if (dx or dz) else DARK_CHISEL)
        if kind == 'bones':
            b.set(ex, cy + 1, ez, SKULL)
            b.set(ex + 1, cy + 1, ez, BONE_X)
        elif kind == 'loot':
            b.chest(ex, cy + 1, ez, 'chests/gibbet', facing='south')
        elif kind == 'flyer':
            b.meta['gibbets'].append([ex, cy + 1, ez])
        b.hang_lantern(ex, cy - 1, ez, soul=(kind == 'flyer'))


# ---------------------------------------------------------------- each floor dressed for what lives there
def interiors(b):
    for i, (fy, r, ht) in enumerate(TIERS):
        # ladder up a basalt post near the north-east, through a hole in the floor above
        hx, hz = C + 4 - i * 2, C - r + 3
        top = TIERS[i + 1][0] if i + 1 < len(TIERS) else CROWN_Y
        for y in range(fy + 1, top + 1):
            b.set(hx, y, hz - 1, BASALT)
            b.set(hx, y, hz, B('ladder', facing='south', waterlogged='false'))
        # the loot pen: a small cage in the middle you can see from anywhere on the floor
        for x in range(C - 2, C + 3):
            for z in range(C - 2, C + 3):
                for y in range(fy + 1, fy + 5):
                    rim = abs(x - C) == 2 or abs(z - C) == 2
                    door = z == C + 2 and x == C and y < fy + 3
                    b.set(x, y, z, B('iron_bars') if rim and not door else AIR)
        b.set(C, fy + 1, C, GILDED)
        b.chest(C, fy + 2, C, ['chests/swarm_pen', 'chests/hatchery', 'chests/aerie'][i], facing='south')
        b.box(C - 2, fy + 5, C - 2, C + 2, fy + 5, C + 2, lambda x, y, z: slab('polished_blackstone', 'bottom'))
        # hanging light over the pen
        for y in range(fy + 6, fy + ht):
            b.set(C, y, C, CHAIN_Y)
        b.set(C, fy + 6, C, SOUL_LANTERN if i == 1 else LANTERN)
        for x in range(W):
            for z in range(L):
                if not in_octagon(x, z, C, C, r - 2) or (abs(x - C) <= 3 and abs(z - C) <= 3):
                    continue
                q = h(x, fy, z, 100 + i)
                near_wall = not in_octagon(x, z, C, C, r - 4)
                if i == 0:
                    if q < 0.08:
                        b.set(x, fy, z, COARSE)
                    if near_wall and q > 0.9:
                        b.set(x, fy + 1, z, BONE_Y if q > 0.96 else COBWEB)
                    if q < 0.03:
                        b.set(x, fy + 1, z, SKULL)
                elif i == 1:
                    if q < 0.12:
                        b.set(x, fy, z, MUD)
                        b.set(x, fy + 1, z, B('turtle_egg', eggs=1 + int(q * 30) % 4, hatch=0))
                    elif near_wall and q > 0.88:
                        b.set(x, fy + 1, z, 'minecraft:white_wool')
                        b.set(x, fy + 2, z, COBWEB)
                else:
                    if near_wall and q > 0.8:
                        b.set(x, fy + 1, z, HAY)
                        if q > 0.94:
                            b.set(x, fy + 2, z, 'minecraft:dead_bush')
                    elif q < 0.04:
                        b.set(x, fy + 1, z, BONE_X)
                # cobwebs high in the corners of every tier
                if near_wall and h(x, fy + ht - 2, z, 5) < 0.18:
                    b.set(x, fy + ht - 2, z, COBWEB)


def zones(b):
    names = ['swarm_pen', 'hatchery', 'aerie']
    titles = ['The Swarm Pen', 'The Hatchery', 'The Aerie']
    for i, (fy, r, ht) in enumerate(TIERS):
        a = r - 2
        box = (C - a, fy + 1, C - a, C + a, fy + ht - 1, C + a)
        sp = [(C + round(math.cos(math.radians(45 * k + 20)) * (r - 4)), fy + 1, C + round(math.sin(math.radians(45 * k + 20)) * (r - 4)))
              for k in range(8)]
        extra = {}
        if i == 1:
            extra['brood'] = 'minecraft:turtle_egg'
        kind = 'waves'
        if i == 2:
            kind = 'ambush'
            extra['release_from'] = b.meta.get('gibbets', [])
        b.zone(names[i], titles[i], box, sp, f'tower_{names[i]}', kind=kind, **extra)
    fy = CROWN_Y
    box = (C - CROWN_R + 1, fy + 1, C - CROWN_R + 1, C + CROWN_R - 1, fy + 12, C + CROWN_R - 1)
    sp = [(C + 5, fy + 1, C), (C - 5, fy + 1, C), (C, fy + 1, C - 5), (C, fy + 1, C + 5)]
    b.zone('crown', 'The Crown', box, sp, 'tower_crown', kind='guardian', gate='crown', reward='cage_trophy', final=True)


if __name__ == '__main__':
    build().save(foundation_level=0)
