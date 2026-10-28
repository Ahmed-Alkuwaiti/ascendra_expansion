"""The Predator Rookery: a leaning crag crowned by a nest the size of a house.

The rock is streaked white below the rim (you see a rookery long before you see a predator). A ledge path spirals up the
outside; a cave at the foot climbs through the rock and comes out under the nest. On top: a bowl woven from whole trunks,
bone and hay, three giant eggs, the clutch cache, and long perch branches where the predators roost.

Fights: the roost (the residents wake when you set foot in the nest, or when you hit one) and the Rookmother (she comes
in from the sky once the roost is broken).
"""
import math

from common import *
from kit import AIR, B, Build, h

W, L, H = 55, 55, 104
G = 4
CX, CZ = 27, 27
TOP = 70                    # local y of the nest floor
LEAN = (5.0, -3.0)          # how far the crown leans over by the top


def centre(y):
    t = max(0.0, min(1.0, y / TOP))
    return CX - LEAN[0] / 2 + LEAN[0] * t ** 1.6, CZ - LEAN[1] / 2 + LEAN[1] * t ** 1.6


def radius(y, a):
    t = y / TOP
    base = 15.5 - 8.5 * t + (2.0 * math.sin(t * 9) if t < 0.9 else 0)
    flare = 3.5 * max(0.0, t - 0.86) / 0.14
    return base + flare + 1.6 * math.sin(a * 3 + y * 0.21) + 1.1 * math.sin(a * 7 - y * 0.13)


def build():
    b = Build('rookery', W, H, L, seed=31)
    crag(b)
    streaks(b)
    tunnel(b)
    ledge_path(b)
    nest(b)
    perches(b)
    eggs(b)
    zones(b)
    b.meta.update({'kind': 'rookery', 'title': 'Predator Rookery', 'ground': G})
    return b


def crag(b):
    for y in range(0, TOP + 1):
        cx, cz = centre(y)
        for x in range(W):
            for z in range(L):
                a = math.atan2(z - cz, x - cx)
                d = math.hypot(x - cx, z - cz)
                r = radius(y, a)
                if d <= r:
                    blk = rock(x, y, z, 12)
                    if y < 16 + 6 * h(x, 0, z, 3):
                        blk = 'minecraft:deepslate' if h(x, y, z, 4) < 0.6 else COBBLE_DEEP
                    if d > r - 1.2 and h(x, y, z, 5) < 0.12:
                        blk = MOSS if y < 30 else 'minecraft:calcite'
                    b.set(x, y, z, blk)
    # a skirt of fallen boulders and scree at the foot
    for k in range(26):
        a = k * 2.399
        d = 15 + (k * 7) % 9
        bx, bz = CX + d * math.cos(a), CZ + d * math.sin(a)
        rr = 1.4 + (k % 4) * 0.6
        b.ellipsoid(bx, G + rr * 0.4, bz, rr, rr * 0.8, rr, lambda x, y, z: rock(x, y, z, 13))


def streaks(b):
    """Guano and bone below the rim: white runs down the rock from the nest."""
    for k in range(30):
        a = k * 0.73 + 0.3
        y = TOP - 1
        cx, cz = centre(y)
        r = radius(y, a)
        x, z = cx + (r + 0.5) * math.cos(a), cz + (r + 0.5) * math.sin(a)
        length = 10 + (k * 11) % 26
        for dy in range(length):
            yy = y - dy
            cx2, cz2 = centre(yy)
            r2 = radius(yy, a)
            px, pz = round(cx2 + r2 * math.cos(a)), round(cz2 + r2 * math.sin(a))
            if b.solid(px, yy, pz):
                b.set(px, yy, pz, 'minecraft:calcite' if h(px, yy, pz, k) < 0.75 else 'minecraft:white_concrete_powder')
            if dy % 9 == 4 and h(px, yy, pz, 2) < 0.4:
                ox, oz = round(cx2 + (r2 + 1) * math.cos(a)), round(cz2 + (r2 + 1) * math.sin(a))
                b.set(ox, yy, oz, BONE_Y, over=False)


def tunnel(b):
    """A cave at the foot that winds up through the rock to come out under the nest's rim."""
    pts = []
    for k in range(13):
        t = k / 12
        y = G + 1 + t * (TOP - G - 3)
        cx, cz = centre(y)
        a = 2.2 + t * 4.4
        rr = max(3.5, radius(y, a) - 4)
        pts.append((cx + rr * 0.6 * math.cos(a), y, cz + rr * 0.6 * math.sin(a)))
    mouth_a = 2.2
    cx, cz = centre(G + 1)
    pts.insert(0, (cx + 18 * math.cos(mouth_a), G + 1.5, cz + 18 * math.sin(mouth_a)))
    b.curve(pts, AIR, radius=lambda t: 1.9)
    # a floor of bone and gravel along the bottom of the tube, lanterns of a dead expedition
    for i, p in enumerate(pts):
        x, y, z = (round(v) for v in p)
        if b.get(x, y - 2, z) not in (None, AIR):
            b.set(x, y - 2, z, 'minecraft:gravel' if i % 2 else BONE_Y)
        if i % 3 == 1:
            b.set(x, y + 1, z, LANTERN)
    b.point('tunnel_mouth', round(pts[0][0]), round(pts[0][1]), round(pts[0][2]))
    b.meta['tunnel'] = [[round(p[0]), round(p[1]), round(p[2])] for p in pts]


def ledge_path(b):
    """Natural ledges spiralling up the outside: rock shelves with bone steps, a few gaps you have to jump."""
    turns = 2.4
    n = 1300
    for k in range(n):
        t = k / n
        y = G + 2 + t * (TOP - G - 4)
        a = -0.6 + t * turns * math.tau
        cx, cz = centre(y)
        r = radius(int(y), a)
        if 0.43 < (t * 37) % 1 < 0.47 and t > 0.2:
            continue          # a gap
        for w in (0.2, 1.2, 2.0):
            x, z = round(cx + (r + w) * math.cos(a)), round(cz + (r + w) * math.sin(a))
            yi = int(y)
            b.set(x, yi, z, ('minecraft:cobbled_deepslate' if h(x, yi, z, 6) < 0.5 else 'minecraft:tuff') if w > 0.5 else 'minecraft:tuff', over=False)
            if w > 1.5 and h(x, yi, z, 8) < 0.08:
                b.set(x, yi + 1, z, BONE_Y, over=False)
            b.set(x, yi + 1, z, AIR) if not b.solid(x, yi + 1, z) or w > 0.5 else None
            b.set(x, yi + 2, z, AIR) if w > 0.5 else None
        if k % 90 == 0:
            x, z = round(cx + (r + 2.6) * math.cos(a)), round(cz + (r + 2.6) * math.sin(a))
            b.set(x, int(y) + 1, z, SKULL if k % 180 else BONE_Y, over=False)


def nest(b):
    cx, cz = centre(TOP)
    R = 15.0
    # the bowl: woven trunks round the rim, a hay and wool lining, bone in the weave
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - cx, z - cz)
            if d > R + 1:
                continue
            depth = 3 - int(3 * (1 - (d / R) ** 2)) if d < R else 3
            for y in range(TOP - 3, TOP + 1):
                if y >= TOP - depth and d < R - 2.5:
                    continue
                q = h(x, y, z, 21)
                blk = HAY if q < 0.35 else ('minecraft:brown_wool' if q < 0.5 else ('minecraft:coarse_dirt' if q < 0.62 else B('stripped_spruce_log', axis='y')))
                b.set(x, y, z, blk)
            if d < R - 2.5:
                y = TOP - depth
                q = h(x, y, z, 23)
                b.set(x, y, z, HAY if q < 0.45 else ('minecraft:white_wool' if q < 0.55 else 'minecraft:brown_wool'))
                for y2 in range(y + 1, TOP + 5):
                    b.set(x, y2, z, AIR)
                if q > 0.93:
                    b.set(x, y + 1, z, BONE_Y if q > 0.97 else SKULL)
    # the woven wall: dozens of trunks laid round the rim at angles, sticking out past it
    for k in range(64):
        a0 = k * math.tau / 64 + h(k, 0, 0) * 0.3
        a1 = a0 + 0.5 + h(k, 1, 0) * 0.6
        y0 = TOP + (k % 4)
        r0, r1 = R - 1 + (k % 3), R + 1.5 - (k % 2)
        p0 = (cx + r0 * math.cos(a0), y0, cz + r0 * math.sin(a0))
        p1 = (cx + r1 * math.cos(a1), y0 + (k % 3) - 1, cz + r1 * math.sin(a1))
        dx, dz = abs(p1[0] - p0[0]), abs(p1[2] - p0[2])
        log = B('dark_oak_log' if k % 3 else 'stripped_spruce_log', axis='x' if dx > dz else 'z')
        b.line(p0, p1, log)
        if k % 5 == 0:
            b.set(round(p1[0]), round(p1[1]) + 1, round(p1[2]), 'minecraft:dead_bush', over=False)
        if k % 7 == 0:
            b.set(round(p0[0]), round(p0[1]) + 1, round(p0[2]), BONE_X if k % 2 else BONE_Z, over=False)
    # the clutch cache, half buried in the lining at the centre
    b.set(round(cx), TOP - 3, round(cz), HAY)
    b.chest(round(cx), TOP - 2, round(cz), 'chests/rookery_clutch', facing='south')
    b.set(round(cx), TOP - 1, round(cz), AIR)
    b.point('vault', round(cx), TOP - 2, round(cz))
    # where the tunnel comes out: an opening in the nest floor
    tx, ty, tz = b.meta['tunnel'][-1]
    for y in range(ty, TOP + 1):
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                b.set(tx + dx, y, tz + dz, AIR)


def perches(b):
    """Long branches out over the drop: where the roost sits, and where the Rookmother lands."""
    cx, cz = centre(TOP)
    b.meta['perches'] = []
    for k in range(6):
        a = k * math.tau / 6 + 0.4
        y = TOP + 2 + (k % 3) * 2
        p0 = (cx + 12 * math.cos(a), y - 2, cz + 12 * math.sin(a))
        p1 = (cx + 23 * math.cos(a), y + 2, cz + 23 * math.sin(a))
        axis = 'x' if abs(math.cos(a)) > abs(math.sin(a)) else 'z'
        mid = ((p0[0] + p1[0]) / 2, y + 2.5, (p0[2] + p1[2]) / 2)
        b.curve([p0, mid, p1], B('dark_oak_log', axis=axis), radius=lambda t: 1.1 - 0.5 * t)
        tip = (round(p1[0]), round(p1[1]) + 1, round(p1[2]))
        b.meta['perches'].append(list(tip))
        b.set(tip[0], tip[1] - 1, tip[2] + 1, BONE_Y, over=False)
        b.set(round(p1[0]), round(p1[1]) - 1, round(p1[2]), CHAIN_Y, over=False)
        b.set(round(p1[0]), round(p1[1]) - 2, round(p1[2]), SKULL, over=False)


def eggs(b):
    cx, cz = centre(TOP)
    for k, (dx, dz) in enumerate(((-5, 3), (4, 5), (2, -6))):
        ex, ez = cx + dx, cz + dz
        floor = TOP - 2
        b.ellipsoid(ex, floor + 2.6, ez, 1.7, 2.6, 1.7,
                    lambda x, y, z, k=k: 'minecraft:calcite' if h(x, y, z, k) < 0.78 else ('minecraft:smooth_quartz' if h(x, y, z, 9) < 0.6 else 'minecraft:packed_mud'))
        b.point(f'egg{k}', round(ex), floor + 1, round(ez))


def zones(b):
    cx, cz = centre(TOP)
    R = 14
    box = (round(cx - R), TOP - 3, round(cz - R), round(cx + R), TOP + 14, round(cz + R))
    sp = [tuple(p) for p in b.meta['perches']]
    nest_spots = [(round(cx + 6 * math.cos(a)), TOP - 1, round(cz + 6 * math.sin(a))) for a in (0, 2.1, 4.2)]
    b.zone('roost', 'The Roost', box, nest_spots, 'rookery_roost', kind='roost', flyers_at=sp,
           trigger=(box[0] + 2, TOP - 3, box[2] + 2, box[3] - 2, TOP + 6, box[5] - 2))
    sky = [(round(cx + 26 * math.cos(a)), TOP + 22, round(cz + 26 * math.sin(a))) for a in (0.5, 2.6, 4.7)]
    b.zone('rookmother', 'The Rookmother', box, sky, 'rookery_mother', kind='guardian', reward='rookery_talon', final=True,
           requires=['roost'], flyer_spawns=sky)
    tun = b.meta['tunnel']
    mid = tun[len(tun) // 2]
    b.zone('tunnel', 'Scavengers in the rock', (mid[0] - 6, mid[1] - 6, mid[2] - 6, mid[0] + 6, mid[1] + 6, mid[2] + 6),
           [tuple(p) for p in tun[4:9]], 'rookery_scavengers', kind='ambush', waves=1)


if __name__ == '__main__':
    build().save(foundation_level=0)
