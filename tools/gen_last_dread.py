"""The Last Realm's dread: everything round the arena that the fight never touches, placed once by ArenaBuilder.last() before the
core (the core is re-placed at every fight, so it stays small; this is placed only when the realm is first built).

  the Abyssal Root   under the arena, a twisting black spire 85 blocks deep, ending in a vast violet eye that looks down into the void,
                     with eight tendrils curling out beneath the bridges
  the Eight Talons   bone claws that rise out of the tendrils between the bridges, climb past the rim and hook over the crown, so the
                     whole arena sits in a closing hand
  the Shattered Crown a broken ring of gold 64 blocks across hung over the arena in the talons' grip, two sectors torn out and drifting,
                     with the Heart (a black, violet-eyed orb) chained at its centre, watching the arena from above
  the Watchers       eight faceless hooded colossi, 46 tall, on floating rocks round the hub, each leaning on a planted greatsword,
                     facing the altar
  the Vertebrae      bone rings round every bridge, like walking the spine of something dead
  the Wreckage       broken pieces of checkered floor and pillars drifting at every height

It leaves out every cell the core, the pad, the bridges and the islands use, so the pieces never fight.
"""
import math
import random

from gen_act3_citadels import Grid, chain, lantern

W = L = 209
C = 104                       # the altar's column
F = 90                        # the standing level at the altar (the pad's surface is F - 1); the template's origin is c - (C, F, C)
H = 186
CORE_R = 31                   # the core's footprint (it reaches about 37 below the floor and 21 above)
ISLAND_D, ISLAND_R = 66, 19
BRIDGE_IN, BRIDGE_OUT = 25, 56

BONE = 'minecraft:bone_block'
BS, PB, PBB, GB = 'minecraft:blackstone', 'minecraft:polished_blackstone', 'minecraft:polished_blackstone_bricks', 'minecraft:gilded_blackstone'
CRY, OBS, BLK = 'minecraft:crying_obsidian', 'minecraft:obsidian', 'minecraft:black_concrete'
GOLD, RAWG = 'minecraft:gold_block', 'minecraft:raw_gold_block'
DT, PD, DS = 'minecraft:deepslate_tiles', 'minecraft:polished_deepslate', 'minecraft:deepslate'
MAG, PUR, TINT = 'minecraft:magenta_stained_glass', 'minecraft:purple_stained_glass', 'minecraft:tinted_glass'
PEARL = 'minecraft:pearlescent_froglight'
CAL, SS, CSS = 'minecraft:calcite', 'minecraft:smooth_sandstone', 'minecraft:chiseled_sandstone'
NETH = 'minecraft:netherite_block'
AX = {'axis': 'y'}


def h(x, y, z, salt=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (salt * 2654435761)) % 1000 / 1000.0


def reserved(x, y, z):
    """Cells the core, the pad, the bridges or the islands own."""
    dx, dz = x - C, z - C
    d = math.hypot(dx, dz)
    if d <= CORE_R and F - 40 <= y <= F + 22:
        return True
    if F - 8 <= y <= F + 4 and BRIDGE_IN - 2 <= d <= BRIDGE_OUT + 2:
        a = math.atan2(dz, dx)
        k = round(a / (math.pi / 4))
        rel = a - k * math.pi / 4
        if abs(d * math.sin(rel)) <= 4.6:
            return True
    for k in range(8):
        a = k * math.pi / 4
        ix, iz = C + ISLAND_D * math.cos(a), C + ISLAND_D * math.sin(a)
        if math.hypot(x - ix, z - iz) <= ISLAND_R and F - 44 <= y <= F + 42:
            return True
    return False


class Dread:
    def __init__(self):
        self.g = Grid(W, H, L)

    def put(self, x, y, z, b, props=None, over=True):
        x, y, z = int(round(x)), int(round(y)), int(round(z))
        if not (0 <= x < W and 0 <= y < H and 0 <= z < L) or reserved(x, y, z):
            return
        if not over and self.g.get(x, y, z) is not None:
            return
        self.g.set(x, y, z, b, props)

    def ball(self, cx, cy, cz, r, pick, over=True):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for y in range(int(cy - r) - 1, int(cy + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                        b = pick(x, y, z) if callable(pick) else pick
                        if b:
                            if isinstance(b, tuple):
                                self.put(x, y, z, b[0], b[1], over=over)
                            else:
                                self.put(x, y, z, b, over=over)

    def tube(self, pts, radius, pick, step=0.35):
        """A tube along a polyline, radius a function of the fraction along it."""
        segs = list(zip(pts, pts[1:]))
        lens = [math.dist(a, b) for a, b in segs]
        total = sum(lens)
        done = 0.0
        for (a, b), ln in zip(segs, lens):
            n = max(1, int(ln / step))
            for i in range(n):
                t = i / n
                p = [a[j] + (b[j] - a[j]) * t for j in range(3)]
                s = (done + ln * t) / total
                self.ball(p[0], p[1], p[2], radius(s), lambda x, y, z, s=s: pick(x, y, z, s))
            done += ln


def catmull(ctrl, n=80):
    """A smooth path through control points."""
    pts = [ctrl[0]] + ctrl + [ctrl[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n // (len(ctrl) - 1)):
            t = k / (n // (len(ctrl) - 1))
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(3)))
    out.append(ctrl[-1])
    return out


def polar(r, a, y):
    return (C + r * math.cos(a), y, C + r * math.sin(a))


# ================================================================================================ the Abyssal Root and the Eye
def root(d):
    top, bot = F - 33, 26
    for y in range(top, bot - 1, -1):
        t = (top - y) / (top - bot)
        r = 12.5 * (1 - t) ** 0.85 + 3.2
        for x in range(int(C - r) - 3, int(C + r) + 4):
            for z in range(int(C - r) - 3, int(C + r) + 4):
                dx, dz = x - C, z - C
                a = math.atan2(dz, dx)
                lobe = math.cos(6 * (a - t * 4.2))                      # six lobes twisting as it goes down
                re = r * (0.78 + 0.26 * lobe)
                dd = math.hypot(dx, dz)
                if dd <= re:
                    edge = dd > re - 1.3
                    if edge and lobe > 0.82:
                        b = CRY                                          # the ridges weep
                    elif edge:
                        b = OBS if h(x, y, z) < 0.35 else BS
                    else:
                        b = BS if h(x, y, z, 1) < 0.7 else BLK
                    d.put(x, y, z, b)
        if y % 7 == 0 and t < 0.85:                                     # drips off the ridges
            for k in range(6):
                a = k * math.pi / 3 + t * 4.2
                d.put(C + (r * 1.03) * math.cos(a), y - 1, C + (r * 1.03) * math.sin(a), 'minecraft:pointed_dripstone',
                      {'thickness': 'tip', 'vertical_direction': 'down', 'waterlogged': 'false'})
    # the Eye: a black orb ringed in violet, its pupil turned down into the void
    ey, er = 17, 8.5

    def eye(x, y, z):
        dx, dy, dz = x - C, y - ey, z - C
        dd = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dd < er - 2.2:
            return PEARL if dd < er - 3.5 else (MAG, None)
        down = -dy / max(dd, 0.01)                                      # 1 at the bottom of the orb
        if down > 0.93:
            return BLK                                                  # the pupil
        if down > 0.62:
            return MAG if h(x, y, z) < 0.8 else PUR                     # the iris
        if down > 0.5:
            return GOLD
        return OBS if h(x, y, z, 2) < 0.6 else (CRY if h(x, y, z, 3) < 0.4 else BLK)
    d.ball(C, ey, C, er, lambda x, y, z: (PEARL, AX) if eye(x, y, z) == PEARL else eye(x, y, z))
    for k in range(8):                                                  # tendrils, curling out under the bridges' gaps
        a = math.radians(22.5 + k * 45)
        ctrl = [polar(9, a, F - 40), polar(22, a, F - 52), polar(36, a, F - 50), polar(42, a, F - 38), polar(44, a, F - 28)]
        d.tube(catmull(ctrl), lambda s: 3.4 - 1.0 * s,
               lambda x, y, z, s: CRY if h(x, y, z) < 0.12 else (BS if h(x, y, z, 4) < 0.6 else OBS))
        ctrl2 = [polar(7, a + 0.4, F - 60), polar(18, a + 0.55, F - 70), polar(30, a + 0.7, F - 72), polar(36, a + 0.85, F - 64),
                 polar(34, a + 1.0, F - 56)]                             # and a lesser one below, curling back up
        d.tube(catmull(ctrl2), lambda s: 2.2 * (1 - s) + 0.6, lambda x, y, z, s: BS if s < 0.8 else OBS)


# ================================================================================================ the Eight Talons
def talons(d):
    for k in range(8):
        a = math.radians(22.5 + k * 45)
        ctrl = [polar(40, a, F - 32), polar(52, a, F - 14), polar(60, a, F + 8), polar(60, a, F + 34), polar(50, a, F + 60),
                polar(36, a, F + 77), polar(24, a, F + 76), polar(18.5, a, F + 64)]
        path = catmull(ctrl, n=140)
        ca, sa = math.cos(a), math.sin(a)

        def rad(s):
            r = 4.0 * (1 - s) ** 0.75 + 0.6
            for kn in (0.2, 0.42, 0.62, 0.8):                           # knuckles
                r += 1.2 * math.exp(-((s - kn) / 0.022) ** 2) * (1 - s * 0.6)
            return r

        def centre(s):
            return path[min(len(path) - 1, int(s * (len(path) - 1)))]

        def pick(x, y, z, s):
            for kn in (0.2, 0.42, 0.62, 0.8):
                if abs(s - kn) < 0.028:
                    return (CRY if h(x, y, z) < 0.3 else PBB), None
            if s > 0.88:
                return (OBS if s > 0.95 else BS), None
            p = centre(s)
            back = ((x - p[0]) * ca + (z - p[2]) * sa) / max(rad(s), 0.5)    # how far round to the talon's back it is
            if back > 0.35 or y - p[1] > rad(s) * 0.55:
                return (PB if h(x, y, z) < 0.6 else BS), None            # black plates armour its back
            return (BONE, AX) if h(x, y, z, 5) < 0.88 else ('minecraft:calcite', None)
        d.tube(path, rad, pick)
        # bone spurs off the back of the talon, pointing outward and up
        for i in range(10, len(path) - 24, 8):
            p = path[i]
            out = (math.cos(a), 0.6, math.sin(a))
            r0 = rad(i / len(path))
            for j in range(int(r0) + 1, int(r0) + 5):
                d.put(p[0] + out[0] * j, p[1] + out[1] * j, p[2] + out[2] * j, BONE, AX)
            d.put(p[0] + out[0] * (r0 + 5), p[1] + out[1] * (r0 + 5), p[2] + out[2] * (r0 + 5), 'minecraft:pointed_dripstone',
                  {'thickness': 'tip', 'vertical_direction': 'up', 'waterlogged': 'false'})


# ================================================================================================ the Shattered Crown and the Heart
CROWN_Y, CROWN_R, CROWN_r = F + 66, 32, 2.7
TORN = [(math.radians(100), math.radians(128), (7, 6, -2)), (math.radians(282), math.radians(304), (-5, -4, 5))]


def torn(a):
    a %= 2 * math.pi
    for lo, hi, off in TORN:
        if lo <= a <= hi:
            return off
    return None


def crown(d):
    rnd = random.Random(808)
    for x in range(C - CROWN_R - 4, C + CROWN_R + 5):
        for z in range(C - CROWN_R - 4, C + CROWN_R + 5):
            dx, dz = x - C, z - C
            rr = math.hypot(dx, dz)
            for y in range(int(CROWN_Y - CROWN_r) - 1, int(CROWN_Y + CROWN_r) + 2):
                q = math.hypot(rr - CROWN_R, (y - CROWN_Y) * 1.15)
                if q > CROWN_r:
                    continue
                a = math.atan2(dz, dx)
                outer = (rr - CROWN_R) > 0.6 or y > CROWN_Y + 1.2
                if abs((y - CROWN_Y)) < 0.6 and outer:
                    b = PEARL if (int(math.degrees(a)) % 15 == 0) else MAG       # a band of violet gems round the outside
                elif outer:
                    b = GOLD if h(x, y, z) < 0.55 else (RAWG if h(x, y, z, 6) < 0.6 else GB)
                else:
                    b = PB if h(x, y, z) < 0.7 else BS
                off = torn(a)
                if off:
                    if rnd.random() < 0.18:
                        continue                                                    # the torn sectors crumble as they drift
                    d.put(x + off[0], y + off[1], z + off[2], b, AX if b == PEARL else None)
                else:
                    d.put(x, y, z, b, AX if b == PEARL else None)
    # the points of the crown: tall ones over the bridges, short ones between them
    for k in range(16):
        a = math.radians(k * 22.5)
        tall = k % 2 == 0
        ht = 13 if tall else 6
        off = torn(a) or (0, 0, 0)
        cx, cz = C + CROWN_R * math.cos(a) + off[0], C + CROWN_R * math.sin(a) + off[2]
        y0 = CROWN_Y + 2 + off[1]
        for j in range(ht):
            r = (2.4 if tall else 1.6) * (1 - j / ht) + 0.3
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if math.hypot(x - cx, z - cz) <= r:
                        d.put(x, y0 + j, z, GOLD if j < ht - 2 else GB)
        if tall:                                                                    # a gem in each tall point
            d.put(cx, y0 + 4, cz, PEARL, AX)
            d.put(cx - math.sin(a), y0 + 4, cz + math.cos(a), MAG)
            d.put(cx + math.sin(a), y0 + 4, cz - math.cos(a), MAG)
            d.put(cx, y0 + ht, cz, CRY)
    # chains hanging under the ring, every one ending in a soul lantern
    for k in range(24):
        a = math.radians(k * 15 + 7.5)
        if torn(a):
            continue
        x, z = round(C + CROWN_R * math.cos(a)), round(C + CROWN_R * math.sin(a))
        ln = 4 + int(h(k, 1, 2) * 12)
        for y in range(int(CROWN_Y - CROWN_r) - ln, int(CROWN_Y - CROWN_r)):
            d.put(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
        d.put(x, int(CROWN_Y - CROWN_r) - ln - 1, z, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'})
    # the Heart: a black orb chained to the ring at its four points, its violet eye turned down on the arena
    hy, hr = CROWN_Y - 1, 6.2

    def heart(x, y, z):
        dx, dy, dz = x - C, y - hy, z - C
        dd = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dd < hr - 2:
            return (PEARL, AX)
        down = -dy / max(dd, 0.01)
        if down > 0.9:
            return BLK
        if down > 0.6:
            return MAG if h(x, y, z) < 0.85 else PUR
        if down > 0.5:
            return GOLD
        side = abs(math.sin(4 * math.atan2(dz, dx)))
        return CRY if side < 0.12 else (OBS if h(x, y, z, 7) < 0.7 else BLK)
    d.ball(C, hy, C, hr, heart)
    for (ux, uz, axis) in [(1, 0, 'x'), (-1, 0, 'x'), (0, 1, 'z'), (0, -1, 'z')]:
        for j in range(int(hr) + 1, CROWN_R - 2):
            d.put(C + ux * j, hy, C + uz * j, 'minecraft:chain', {'axis': axis, 'waterlogged': 'false'})
    for k in range(8):                                                              # spines on the heart's crown
        a = k * math.pi / 4
        for j in range(4):
            d.put(C + (hr - 1 + j * 0.6) * math.cos(a) * 0.6, hy + hr - 1 + j, C + (hr - 1 + j * 0.6) * math.sin(a) * 0.6, OBS)


# ================================================================================================ the Watchers
def watcher(d, a):
    """A hooded faceless colossus on a floating rock, both hands on the pommel of a planted greatsword, facing the altar."""
    R = 92
    X, Z = C + R * math.cos(a), C + R * math.sin(a)
    fx, fz = -math.cos(a), -math.sin(a)                 # forward, toward the altar
    rx, rz = -fz, fx                                    # right
    base = F - 14
    # the rock
    for x in range(int(X) - 12, int(X) + 13):
        for z in range(int(Z) - 12, int(Z) + 13):
            dd = math.hypot(x - X, z - Z)
            if dd > 11:
                continue
            dep = int((11 - dd) * 1.7 + h(x, 0, z) * 3)
            for y in range(base - dep, base):
                d.put(x, y, z, (CAL if h(x, y, z) < 0.5 else SS) if y == base - 1 else (BS if h(x, y, z, 8) < 0.65 else DS))
            if dep > 6 and h(x, 1, z) < 0.15:
                for y in range(base - dep - 1, base - dep - 4, -1):
                    d.put(x, y, z, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})

    def local(x, y, z):
        u = (x - X) * rx + (z - Z) * rz                 # right
        v = (x - X) * fx + (z - Z) * fz                 # forward
        w = y - base                                    # up
        # the plinth
        if w < 3 and abs(u) <= 6 and -6 <= v <= 6:
            return PBB if w == 2 or abs(u) > 5 or abs(v) > 5 else BS
        # the greatsword, planted in front, point in the stone
        if abs(u) < 1.0 and 6.2 <= v <= 8.0:
            if 2 <= w <= 22:
                return NETH                             # the blade
            if w == 23:
                return GOLD
            if 24 <= w <= 27:
                return BS                               # the grip
            if w == 28:
                return CRY                              # the pommel
        if w == 23 and abs(u) <= 3.8 and 6.2 <= v <= 8.0:
            return GOLD                                 # the crossguard
        # the robe: an ellipse flaring at the hem, leaning slightly toward the sword
        lean = max(0, w - 3) * 0.06
        if 3 <= w < 32:
            t = (w - 3) / 29
            ru, rv = 7.6 - 2.2 * t ** 0.8, 5.0 - 1.2 * t
            vv = v - lean
            if (u / ru) ** 2 + (vv / rv) ** 2 <= 1:
                inner = (u / (ru - 1.2)) ** 2 + (vv / (rv - 1.2)) ** 2 <= 1
                if inner and w > 4:
                    return None                         # hollow, so it is a shell
                if w in (4, 5) or w == 18:
                    return GOLD if w != 18 or h(x, y, z) < 0.7 else GB      # gold at the hem and the girdle
                fold = abs(u) % 2.2 < 0.6 and vv > 0 and t < 0.7
                return PD if fold else (DT if h(x, y, z) < 0.8 else DS)
        # the shoulders and the arms reaching forward to the pommel
        if 32 <= w < 36:
            if (u / 8.2) ** 2 + ((v - lean) / 3.8) ** 2 <= 1:          # a broad mantle, pauldrons of gold-edged stone
                if abs(u) > 6.2 and w == 35:
                    return OBS if h(x, y, z) < 0.5 else CRY            # spiked pauldron tops
                return GOLD if w == 32 else (DT if w < 35 else PD)
        if w in (36, 37, 38) and abs(u) >= 6.4 and abs(u) <= 7.2 and abs(v - lean) < 0.8:
            return OBS                                                  # the pauldron spikes
        for s in (-1, 1):
            for k in range(12):
                tt = k / 11
                au, av, aw = s * (6.4 - 5.6 * tt), (1.6 + lean) + (7.0 - 1.6 - lean) * tt, 32 - 4.5 * tt
                if (u - au) ** 2 + (v - av) ** 2 + (w - aw) ** 2 <= 2.4:
                    return DT
            if (u - s * 0.9) ** 2 + (v - 7.1) ** 2 + (w - 27.6) ** 2 <= 1.3:
                return 'minecraft:gray_concrete'        # the clasped hands, grey stone
        # the hood: a shell with a black void where the face should be, and two burning eyes
        hw0 = 36
        hv = v - lean - 0.6
        if hw0 <= w <= hw0 + 9:
            dd = math.sqrt((u / 3.6) ** 2 + (hv / 3.8) ** 2 + ((w - hw0 - 3.5) / 4.6) ** 2)
            if dd <= 1:
                if hv > 1.6 and abs(u) <= 2.2 and hw0 + 1 <= w <= hw0 + 6:
                    if w == hw0 + 4 and 0.5 < abs(u) < 1.7 and hv > 2.2:
                        return PEARL if hv < 3.4 else None      # two burning eyes in the dark
                    return BLK if hv < 3.2 else None
                return DT if h(x, y, z) < 0.85 else PD
        if w == hw0 + 10 and abs(u) < 0.7 and -2 < hv < 0:
            return DT                                   # the hood's peak
        return None

    for x in range(int(X) - 12, int(X) + 13):
        for z in range(int(Z) - 12, int(Z) + 13):
            for y in range(base, base + 49):
                b = local(x, y, z)
                if b:
                    d.put(x, y, z, b, AX if b == PEARL else None)
    # two soul fires at the plinth's front corners
    for s in (-1, 1):
        x, z = X + rx * s * 5 + fx * 5, Z + rz * s * 5 + fz * 5
        d.put(x, base + 3, z, 'minecraft:soul_campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'})


# ================================================================================================ the Vertebrae round the bridges
def vertebrae(d):
    for k in range(8):
        a = k * math.pi / 4
        ca, sa = math.cos(a), math.sin(a)
        for t in (33, 39, 45):
            cx, cz = C + t * ca, C + t * sa
            for x in range(int(cx) - 10, int(cx) + 11):
                for z in range(int(cz) - 10, int(cz) + 11):
                    along = (x - C) * ca + (z - C) * sa
                    off = -(x - C) * sa + (z - C) * ca
                    if abs(along - t) > 1.1:
                        continue
                    for y in range(F - 12, F + 9):
                        rr = math.hypot(off, (y - (F - 1)) * 1.0)
                        if 7.6 <= rr <= 9.0:
                            top = y > F + 5
                            b = PBB if top and abs(off) < 1.5 else (BONE if h(x, y, z) < 0.85 else 'minecraft:calcite')
                            d.put(x, y, z, b, AX if b == BONE else None)
            # spurs off the top of each ring, and a soul lantern hung from it over the walkway
            for j in range(10, 13):
                d.put(cx, F - 1 + j, cz, BONE, AX)
            d.put(cx, F - 1 + 13, cz, 'minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': 'up', 'waterlogged': 'false'})
            d.put(cx, F + 6, cz, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
            d.put(cx, F + 5, cz, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'})


# ================================================================================================ the Wreckage
def wreckage(d):
    rnd = random.Random(4242)
    placed = 0
    tries = 0
    while placed < 46 and tries < 2000:
        tries += 1
        r = rnd.uniform(36, 104)
        a = rnd.uniform(0, 2 * math.pi)
        y = rnd.randint(F - 55, F + 55)
        fx, fz = C + r * math.cos(a), C + r * math.sin(a)
        fr = rnd.uniform(1.6, 4.4)
        if any(reserved(int(fx + dx), y + dy, int(fz + dz)) for dx in (-5, 0, 5) for dz in (-5, 0, 5) for dy in (-6, 0, 6)):
            continue
        if d.g.get(int(fx), y, int(fz)) is not None:
            continue
        placed += 1
        tilt = rnd.uniform(-0.25, 0.25)
        for x in range(int(fx - fr) - 1, int(fx + fr) + 2):
            for z in range(int(fz - fr) - 1, int(fz + fr) + 2):
                dd = math.hypot(x - fx, z - fz)
                if dd > fr:
                    continue
                top = y + int((x - fx) * tilt)
                for yy in range(int(top - (fr - dd) * 1.6) - 1, top + 1):
                    if yy == top:
                        b = CAL if (x // 2 + z // 2) % 2 else PBB
                    else:
                        b = BS if h(x, yy, z) < 0.7 else (CRY if h(x, yy, z, 9) < 0.15 else DS)
                    d.put(x, yy, z, b, over=False)
        kind = rnd.random()
        if kind < 0.35:                                                 # a broken pillar stump
            ph = rnd.randint(2, 7)
            for yy in range(y + 1, y + 1 + ph):
                d.put(fx, yy, fz, CSS if yy == y + 1 else SS, over=False)
        elif kind < 0.55:                                               # a lantern hung under it
            for yy in range(y - int(fr * 1.6) - 6, y - int(fr * 1.6) - 1):
                d.put(fx, yy, fz, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'}, over=False)
            d.put(fx, y - int(fr * 1.6) - 7, fz, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'}, over=False)
        elif kind < 0.65:                                               # a skull left on it
            d.put(fx, y + 1, fz, 'minecraft:wither_skeleton_skull', {'rotation': str(rnd.randint(0, 15))}, over=False)


def main():
    d = Dread()
    root(d)
    talons(d)
    crown(d)
    for k in range(8):
        watcher(d, math.radians(22.5 + k * 45))
    vertebrae(d)
    wreckage(d)
    import gen_citadels2
    was = gen_citadels2.ENRICH
    gen_citadels2.ENRICH = False                                        # its detail is all its own; no ivy on the end of the world
    try:
        d.g.save('last_dread')
    finally:
        gen_citadels2.ENRICH = was
    return d.g


if __name__ == '__main__':
    main()
