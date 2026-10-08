"""The Warden arenas: one template per realm, arena_<realm>, placed once round the landing pad by ArenaBuilder.decorate() (after the
pad is built, before the realm's gimmick blocks go in).

Every arena keeps the fight exactly as it was: the pad (radius 12, where the bosses fight and the gimmicks stand) is never touched,
nor the Drowned water ring, and the space over the battleground (out to radius 33, thirty blocks up) is kept open for the flyers.
Round that each realm gets its own setting:

  grove      a briar-walled clearing ringed by eight trophy totems, deer skulls on dead trunks, two great roots arching overhead
  skyreach   the Roc's nest: a floating ring of bones and dead wood, broken eggshells, giant feathers, eight storm-struck pylons
  hollow     a lava moat round the floor, a black wall of spikes, eight gibbet towers hung with cages, the Hollow King's empty throne
  drowned    the ribcage of a leviathan, its spine overhead and its skull at one end, round the water ring; drowned columns
  pale       a ring of ice spikes, eight weeping statues of ice, frozen chains, a floor cracked with blue ice
  scarlet    a sunken colosseum: tiers of red sandstone, eight sun obelisks, impaled spears, a giant scythe blade driven into the stone
  clockwork  a floating clock face: twelve hour pillars, standing gears, pendulum blades on gallows, gears and chains under it
  mycelial   a fleshy grotto: ten giant petals leaning in like a closing flower, glowing flesh pillars, spore pods hung from the roof
"""
import math
import random

import gen_citadels2
from gen_act3_citadels import AIR, Grid

W = L = 129
C = 64
F = 50                        # the standing level at the altar; the pad's surface is F - 1; origin = c - (C, F, C)
H = 116
PAD_R = 12.7
OPEN_R = 33.5                 # the battleground, kept open to F + 30
FLOAT = {'skyreach', 'clockwork'}
CAVE = {'hollow', 'mycelial'}
SURFACE = {'grove', 'pale', 'scarlet', 'drowned'}

AX = {'axis': 'y'}
BONE = 'minecraft:bone_block'
BS, PB, PBB = 'minecraft:blackstone', 'minecraft:polished_blackstone', 'minecraft:polished_blackstone_bricks'
CRY, OBS = 'minecraft:crying_obsidian', 'minecraft:obsidian'
CHAIN = ('minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})


def h(x, y, z, salt=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (salt * 2654435761)) % 1000 / 1000.0


def drip(direction='down'):
    return ('minecraft:pointed_dripstone', {'thickness': 'tip', 'vertical_direction': direction, 'waterlogged': 'false'})


def hanging_lantern(soul=True):
    return ('minecraft:soul_lantern' if soul else 'minecraft:lantern', {'hanging': 'true', 'waterlogged': 'false'})


def polar(r, a, y):
    return (C + r * math.cos(a), y, C + r * math.sin(a))


def catmull(ctrl, n=80):
    pts = [ctrl[0]] + ctrl + [ctrl[-1]]
    out = []
    per = max(2, n // (len(ctrl) - 1))
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(per):
            t = k / per
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t * t
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t ** 3) for j in range(3)))
    out.append(ctrl[-1])
    return out


class Arena:
    def __init__(self, realm):
        self.realm = realm
        self.g = Grid(W, H, L)
        self.rnd = random.Random(sum(map(ord, realm)) * 31)

    # ---------------------------------------------------------------- what the fight owns
    def reserved(self, x, y, z):
        d = math.hypot(x - C, z - C)
        if d <= PAD_R and F - 7 <= y <= F + 15:
            return True                                                  # the pad: RealmTravel's
        if self.realm == 'drowned' and d <= 26.6 and F - 15 <= y <= F + 22:
            return True                                                  # the water ring: ArenaBuilder.drowned's
        if self.realm == 'clockwork' and d <= 14.2 and F - 7 <= y <= F + 1:
            return True                                                  # the clock rim and its candles
        return False

    def put(self, x, y, z, b, props=None, over=True, open_ok=False):
        x, y, z = int(round(x)), int(round(y)), int(round(z))
        if not (0 <= x < W and 0 <= y < H and 0 <= z < L) or self.reserved(x, y, z):
            return
        if not open_ok and b != AIR and math.hypot(x - C, z - C) <= OPEN_R and F <= y <= F + 30:
            return                                                       # never build into the fight's air
        if not over:
            cur = self.g.get(x, y, z)
            if cur is not None and cur[0] != AIR:
                return
        if isinstance(b, tuple):
            b, props = b
        self.g.set(x, y, z, b, props)

    def ball(self, cx, cy, cz, r, pick, **kw):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            for y in range(int(cy - r) - 1, int(cy + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if (x - cx) ** 2 + (y - cy) ** 2 + (z - cz) ** 2 <= r * r:
                        b = pick(x, y, z) if callable(pick) else pick
                        if b:
                            self.put(x, y, z, b, **kw)

    def tube(self, pts, radius, pick, step=0.4, **kw):
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
                self.ball(p[0], p[1], p[2], radius(s), (lambda x, y, z, s=s: pick(x, y, z, s)) if callable(pick) else pick, **kw)
            done += ln

    def column(self, cx, cz, r, y0, y1, pick, taper=0.0, **kw):
        for y in range(int(y0), int(y1)):
            rr = r * (1 - taper * (y - y0) / max(1, y1 - y0))
            for x in range(int(cx - rr) - 1, int(cx + rr) + 2):
                for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    if math.hypot(x - cx, z - cz) <= rr:
                        b = pick(x, y, z) if callable(pick) else pick
                        if b:
                            self.put(x, y, z, b, **kw)

    def spike(self, cx, cz, y0, ht, r, pick, up=True, lean=(0.0, 0.0), **kw):
        for j in range(int(ht)):
            rr = r * (1 - j / ht) + 0.25
            yy = y0 + j if up else y0 - j
            ox, oz = lean[0] * j, lean[1] * j
            for x in range(int(cx + ox - rr) - 1, int(cx + ox + rr) + 2):
                for z in range(int(cz + oz - rr) - 1, int(cz + oz + rr) + 2):
                    if math.hypot(x - cx - ox, z - cz - oz) <= rr:
                        self.put(x, yy, z, pick(x, yy, z) if callable(pick) else pick, **kw)

    def local(self, X, Z, a, fn, ru, w0, w1):
        """Rasterise a figure defined in its own frame (u right, v toward the altar, w up) standing at (X, Z) facing the altar."""
        fx, fz = (C - X), (C - Z)
        n = math.hypot(fx, fz) or 1
        fx, fz = fx / n, fz / n
        rx, rz = -fz, fx
        for x in range(int(X - ru) - 1, int(X + ru) + 2):
            for z in range(int(Z - ru) - 1, int(Z + ru) + 2):
                u = (x - X) * rx + (z - Z) * rz
                v = (x - X) * fx + (z - Z) * fz
                for y in range(w0, w1):
                    b = fn(u, y - F, v, x, y, z)
                    if b:
                        self.put(x, y, z, b)


# ================================================================================================ the shared ground
PAL = {
    'grove': dict(floor=['minecraft:mossy_stone_bricks', 'minecraft:mossy_cobblestone', 'minecraft:moss_block', 'minecraft:cracked_stone_bricks'],
                  ring='minecraft:rooted_dirt', line='minecraft:mossy_stone_bricks', found='minecraft:stone', under='minecraft:dirt',
                  glow='minecraft:verdant_froglight', fire='minecraft:campfire'),
    'skyreach': dict(floor=['minecraft:calcite', 'minecraft:quartz_bricks', 'minecraft:diorite', 'minecraft:smooth_quartz'],
                     ring='minecraft:polished_diorite', line='minecraft:chiseled_quartz_block', found='minecraft:calcite', under='minecraft:diorite',
                     glow='minecraft:sea_lantern', fire='minecraft:soul_campfire'),
    'hollow': dict(floor=['minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks', 'minecraft:basalt', 'minecraft:blackstone'],
                   ring='minecraft:magma_block', line='minecraft:gilded_blackstone', found='minecraft:blackstone', under='minecraft:basalt',
                   glow='minecraft:shroomlight', fire='minecraft:soul_campfire'),
    'drowned': dict(floor=['minecraft:prismarine_bricks', 'minecraft:dark_prismarine', 'minecraft:prismarine', 'minecraft:mossy_stone_bricks'],
                    ring='minecraft:dark_prismarine', line='minecraft:sea_lantern', found='minecraft:dark_prismarine', under='minecraft:stone',
                    glow='minecraft:sea_lantern', fire='minecraft:soul_campfire'),
    'pale': dict(floor=['minecraft:snow_block', 'minecraft:packed_ice', 'minecraft:calcite', 'minecraft:snow_block'],
                 ring='minecraft:blue_ice', line='minecraft:blue_ice', found='minecraft:packed_ice', under='minecraft:stone',
                 glow='minecraft:soul_lantern', fire='minecraft:soul_campfire'),
    'scarlet': dict(floor=['minecraft:cut_red_sandstone', 'minecraft:red_sandstone', 'minecraft:smooth_red_sandstone', 'minecraft:red_sand'],
                    ring='minecraft:red_terracotta', line='minecraft:chiseled_red_sandstone', found='minecraft:red_sandstone', under='minecraft:terracotta',
                    glow='minecraft:ochre_froglight', fire='minecraft:campfire'),
    'clockwork': dict(floor=['minecraft:polished_deepslate', 'minecraft:deepslate_tiles', 'minecraft:deepslate_bricks', 'minecraft:polished_deepslate'],
                      ring='minecraft:polished_blackstone', line='minecraft:gold_block', found='minecraft:deepslate_tiles', under='minecraft:deepslate',
                      glow='minecraft:pearlescent_froglight', fire='minecraft:soul_campfire'),
    'mycelial': dict(floor=['minecraft:mycelium', 'minecraft:bone_block', 'minecraft:mushroom_stem', 'minecraft:pink_terracotta'],
                     ring='minecraft:crimson_nylium', line='minecraft:pearlescent_froglight', found='minecraft:calcite', under='minecraft:dirt',
                     glow='minecraft:pearlescent_froglight', fire='minecraft:soul_campfire'),
}
GAPS = [math.radians(a) for a in (45, 135, 225, 315)]               # ways out of the arena, toward the lairs


def in_gap(a, half=0.11):
    return any(abs(((a - g + math.pi) % (2 * math.pi)) - math.pi) < half for g in GAPS)


def ground(ar):
    p = PAL[ar.realm]
    realm = ar.realm
    # clear the battleground (a dome in the caves), then lay the floor and its foundation
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if realm in CAVE:
                for y in range(F, F + 36):
                    if (d / 46) ** 2 + ((y - F) / 35) ** 2 <= 1:
                        ar.put(x, y, z, AIR, open_ok=True)
            elif d <= OPEN_R + 2:
                for y in range(F, F + 31 + (8 if realm in SURFACE else 0)):
                    ar.put(x, y, z, AIR, open_ok=True)
            if d > 36:
                continue
            a = math.atan2(z - C, x - C)
            if PAD_R < d <= 31:
                ring = int(d) % 6 == 0
                spoke = abs(((math.degrees(a) % 30) + 15) % 30 - 15) < 18 / max(d, 1)
                b = p['ring'] if ring else (p['line'] if spoke else p['floor'][int(h(x, 0, z) * 4)])
                ar.put(x, F - 1, z, (b, AX) if b in ('minecraft:basalt', BONE) else b)
            elif 31 < d <= 36:
                ar.put(x, F - 1, z, p['floor'][int(h(x, 1, z) * 4)] if not (realm == 'hollow' and d <= 34.5) else 'minecraft:lava')
            for y in range(F - 9, F - 1):
                if d <= 36:
                    ar.put(x, y, z, p['found'] if y > F - 5 else p['under'])
            # under the floating arenas an inverted cone of rock with chains and drips; under the others a skirt down into the ground
            if realm in FLOAT:
                dep = int((36 - d) * 1.15 + h(x, 2, z) * 4)
                for y in range(F - 9 - dep, F - 9):
                    ar.put(x, y, z, p['under'] if h(x, y, z) < 0.75 else p['found'])
                if dep > 4 and h(x, 3, z) < 0.04:
                    ar.put(x, F - 10 - dep, z, drip('down'))
            else:
                for y in range(F - 20, F - 9):
                    ar.put(x, y, z, p['under'], over=False)
    if realm == 'hollow':                                                # the moat burns from below
        for x in range(W):
            for z in range(L):
                d = math.hypot(x - C, z - C)
                if 31 < d <= 34.5:
                    ar.put(x, F - 2, z, 'minecraft:magma_block')


def perimeter(ar, block, height=(3, 9), r0=33.5, r1=36.5, crown=None):
    """A wall of jagged teeth round the battleground, broken by four ways out."""
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if not (r0 <= d <= r1):
                continue
            a = math.atan2(z - C, x - C)
            if in_gap(a):
                continue
            t = abs(math.sin(a * 14 + 0.5)) ** 2.5
            ht = int(height[0] + (height[1] - height[0]) * t + h(x, 9, z) * 2)
            for y in range(F - 1, F + ht):
                b = block(x, y, z, y - F, ht) if callable(block) else block
                ar.put(x, y, z, b, open_ok=True)
            if crown and t > 0.92:
                ar.put(x, F + ht, z, crown, open_ok=True)


def braziers(ar, n=8, r=31.5, fire=None, base=PBB):
    for k in range(n):
        a = math.radians(22.5 + k * 360 / n)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        ar.put(x, F - 1, z, base)
        ar.put(x, F, z, base, open_ok=True)
        ar.put(x, F + 1, z, (fire or PAL[ar.realm]['fire'], {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}),
               open_ok=True)


def gap_markers(ar, block, top):
    """Each way out is flanked by two posts."""
    for g in GAPS:
        for s in (-1, 1):
            a = g + s * 0.15
            x, z = C + 35 * math.cos(a), C + 35 * math.sin(a)
            for y in range(F - 1, F + 10):
                for dx in (0, 1):
                    for dz in (0, 1):
                        ar.put(x + dx, y, z + dz, block, open_ok=True)
            ar.put(x, F + 10, z, top, open_ok=True)


# ================================================================================================ the realms
def grove(ar):
    def briar(x, y, z, w, ht):
        r = h(x, y, z)
        if w >= ht - 1:
            return 'minecraft:azalea_leaves' if r < 0.5 else 'minecraft:jungle_leaves'
        return 'minecraft:mangrove_roots' if r < 0.45 else ('minecraft:dark_oak_log' if r < 0.7 else ('minecraft:moss_block' if r < 0.85 else 'minecraft:rooted_dirt'))
    perimeter(ar, briar, height=(4, 11), crown=drip('up'))
    braziers(ar)
    gap_markers(ar, 'minecraft:dark_oak_log', 'minecraft:skeleton_skull')
    for k in range(8):                                                   # trophy totems
        a = math.radians(22.5 + k * 45)
        X, Z = C + 43 * math.cos(a), C + 43 * math.sin(a)
        twist = ar.rnd.uniform(0, 6)
        pts = [(X + 1.5 * math.cos(twist + t * 0.25), F - 14 + t, Z + 1.5 * math.sin(twist + t * 0.25)) for t in range(0, 40)]
        ar.tube(pts, lambda s: 2.6 - 1.2 * s, lambda x, y, z, s: ('minecraft:dark_oak_log', AX) if h(x, y, z) < 0.75 else 'minecraft:mangrove_roots')
        top = pts[-1]
        sx, sy, sz = top[0], top[1] + 2, top[2]
        fx, fz = (C - sx), (C - sz)
        n = math.hypot(fx, fz)
        fx, fz = fx / n, fz / n
        for x in range(int(sx) - 5, int(sx) + 6):                        # the deer skull, snout toward the altar
            for y in range(int(sy) - 3, int(sy) + 4):
                for z in range(int(sz) - 5, int(sz) + 6):
                    v = (x - sx) * fx + (z - sz) * fz
                    u = -(x - sx) * fz + (z - sz) * fx
                    w = y - sy
                    q = (u / 2.4) ** 2 + ((v + 0.5) / (3.6 if v > 0 else 2.6)) ** 2 + (w / (2.2 - max(0, v) * 0.25)) ** 2
                    if q <= 1:
                        eye = abs(abs(u) - 1.3) < 0.7 and 0.3 < v < 1.6 and 0 <= w <= 1
                        ar.put(x, y, z, PAL['grove']['glow'] if eye else (BONE, AX))
        for s in (-1, 1):                                                # antlers
            base = (sx - fz * s * 1.6, sy + 2, sz + fx * s * 1.6)
            ctrl = [base, (base[0] - fz * s * 3, base[1] + 4, base[2] + fx * s * 3), (base[0] - fz * s * 6 - fx * 2, base[1] + 8, base[2] + fx * s * 6 - fz * 2),
                    (base[0] - fz * s * 7 - fx * 3, base[1] + 13, base[2] + fx * s * 7 - fz * 3)]
            path = catmull(ctrl, 30)
            ar.tube(path, lambda s_: 0.9 - 0.4 * s_, (BONE, AX))
            for i in (8, 16, 24):
                px, py, pz = path[min(i, len(path) - 1)]
                for j in range(1, 4):
                    ar.put(px + fx * j * 0.6, py + j, pz + fz * j * 0.6, (BONE, AX))
        for j in range(4):                                               # skulls hung on chains under the trophy
            a2 = j * math.pi / 2 + 0.4
            hx, hz = X + 3.2 * math.cos(a2), Z + 3.2 * math.sin(a2)
            ln = 3 + j
            for y in range(int(sy) - 2 - ln, int(sy) - 2):
                ar.put(hx, y, hz, CHAIN)
            ar.put(hx, int(sy) - 3 - ln, hz, 'minecraft:skeleton_skull')
    for (a0, a1) in [(0.3, 0.3 + math.pi), (1.9, 1.9 + math.pi)]:        # two great roots arching over the clearing
        ctrl = [polar(52, a0, F - 12), polar(44, a0, F + 18), polar(30, a0, F + 38), polar(0, 0, F + 44), polar(30, a1, F + 38),
                polar(44, a1, F + 18), polar(52, a1, F - 12)]
        path = catmull(ctrl, 160)
        ar.tube(path, lambda s: 3.4 - 1.6 * math.sin(math.pi * s), lambda x, y, z, s: ('minecraft:mangrove_log', AX) if h(x, y, z) < 0.6 else
                ('minecraft:mangrove_roots' if h(x, y, z, 1) < 0.6 else 'minecraft:moss_block'))
        for i in range(10, len(path) - 10, 7):                           # vines and roots dripping off it
            px, py, pz = path[i]
            ln = 2 + int(h(i, 0, 1) * 7)
            for y in range(int(py) - 4 - ln, int(py) - 3):
                if y > F + 31:
                    ar.put(px, y, pz, ('minecraft:hanging_roots', {'waterlogged': 'false'}) if y == int(py) - 4 - ln else ('minecraft:mangrove_roots'))


def skyreach(ar):
    def nest(x, y, z, w, ht):
        r = h(x, y, z)
        return ((BONE, AX) if r < 0.35 else (('minecraft:stripped_birch_log', AX) if r < 0.65 else
                (('minecraft:stripped_dark_oak_log', AX) if r < 0.85 else 'minecraft:hay_block')))
    perimeter(ar, nest, height=(2, 7), r0=32.5, r1=38.5)
    braziers(ar, fire='minecraft:soul_campfire', base='minecraft:quartz_pillar')
    gap_markers(ar, 'minecraft:quartz_pillar', 'minecraft:lightning_rod')
    for k in range(6):                                                   # broken eggshells, big enough to hide in
        a = math.radians(10 + k * 60 + ar.rnd.uniform(-8, 8))
        X, Z = C + 42 * math.cos(a), C + 42 * math.sin(a)
        er = ar.rnd.uniform(4, 6)
        cut = ar.rnd.uniform(0.2, 1.0)
        ar.ball(X, F + er * 0.3, Z, er, lambda x, y, z, X=X, Z=Z, er=er, cut=cut:
                ('minecraft:calcite' if h(x, y, z) < 0.7 else ('minecraft:bone_block', AX))
                if (x - X) ** 2 + (y - F - er * 0.3) ** 2 + (z - Z) ** 2 >= (er - 1.1) ** 2 and y < F + er * cut else None)
    for k in range(8):                                                   # the storm pylons
        a = math.radians(22.5 + k * 45)
        X, Z = C + 46 * math.cos(a), C + 46 * math.sin(a)
        tilt = (ar.rnd.uniform(-0.06, 0.06), ar.rnd.uniform(-0.06, 0.06))
        for j in range(44):
            r = 2.6 * (1 - j / 52)
            cx, cz = X + tilt[0] * j, Z + tilt[1] * j
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if max(abs(x - cx), abs(z - cz)) <= r:
                        b = 'minecraft:oxidized_cut_copper' if j % 9 in (0, 1) else ('minecraft:light_blue_stained_glass' if j % 9 == 5 and
                                                                                      max(abs(x - cx), abs(z - cz)) > r - 1 else 'minecraft:quartz_block')
                        ar.put(x, F - 12 + j, z, b)
        ar.put(X + tilt[0] * 44, F + 32, Z + tilt[1] * 44, 'minecraft:gold_block')
        ar.put(X + tilt[0] * 44, F + 33, Z + tilt[1] * 44, ('minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'}))
        # scorch marks down the side
        for j in range(0, 40, 3):
            ar.put(X + 2.6 * math.cos(a) + tilt[0] * j, F - 10 + j, Z + 2.6 * math.sin(a) + tilt[1] * j, 'minecraft:black_concrete')
    for k in range(10):                                                  # giant feathers driven into the nest
        a = math.radians(k * 36 + 5)
        X, Z = C + 38 * math.cos(a), C + 38 * math.sin(a)
        lean = (math.cos(a) * 0.35, math.sin(a) * 0.35)
        for j in range(16):
            wdt = 2.2 * math.sin(math.pi * min(1, j / 14)) + 0.4
            cx, cz = X + lean[0] * j, Z + lean[1] * j
            for s in range(-int(wdt) - 1, int(wdt) + 2):
                if abs(s) <= wdt:
                    px, pz = cx - math.sin(a) * s, cz + math.cos(a) * s
                    ar.put(px, F + j, pz, ('minecraft:quartz_pillar', AX) if s == 0 else ('minecraft:white_wool' if j % 4 else 'minecraft:light_gray_wool'),
                           open_ok=math.hypot(px - C, pz - C) > OPEN_R)
    rnd = ar.rnd                                                         # floating shards with chains
    for k in range(14):
        a = rnd.uniform(0, 2 * math.pi)
        r = rnd.uniform(40, 60)
        X, Z, Y = C + r * math.cos(a), C + r * math.sin(a), F + rnd.randint(-20, 30)
        sr = rnd.uniform(1.5, 3.2)
        for x in range(int(X - sr) - 1, int(X + sr) + 2):
            for z in range(int(Z - sr) - 1, int(Z + sr) + 2):
                dd = math.hypot(x - X, z - Z)
                if dd <= sr:
                    for y in range(int(Y - (sr - dd) * 2), int(Y) + 1):
                        ar.put(x, y, z, 'minecraft:grass_block' if y == int(Y) else 'minecraft:calcite', over=False)
        for y in range(int(Y - sr * 2) - 5, int(Y - sr * 2)):
            ar.put(X, y, Z, CHAIN, over=False)


def hollow(ar):
    def wall(x, y, z, w, ht):
        return 'minecraft:obsidian' if w >= ht - 2 else (PBB if h(x, y, z) < 0.7 else 'minecraft:cracked_polished_blackstone_bricks')
    perimeter(ar, wall, height=(5, 13), r0=34.6, r1=38.0, crown=drip('up'))
    gap_markers(ar, PBB, ('minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'}))
    for g in GAPS:                                                       # bridges over the moat at each way out
        for t in range(30, 39):
            for s in (-1, 0, 1):
                ar.put(C + t * math.cos(g) - s * math.sin(g), F - 1, C + t * math.sin(g) + s * math.cos(g), PBB)
    for k in range(8):                                                   # gibbet towers to the roof, hung with cages
        a = math.radians(22.5 + k * 45)
        X, Z = C + 43 * math.cos(a), C + 43 * math.sin(a)
        ar.column(X, Z, 3.2, F - 12, F + 36, lambda x, y, z: PBB if h(x, y, z) < 0.6 else (BS if h(x, y, z, 1) < 0.8 else 'minecraft:gilded_blackstone'))
        for y in range(F, F + 36, 8):                                    # rings of spikes
            for j in range(8):
                b = j * math.pi / 4
                for q in range(1, 4):
                    ar.put(X + (3 + q) * math.cos(b), y + q * 0.4, Z + (3 + q) * math.sin(b), OBS if q < 3 else 'minecraft:iron_bars')
        fx, fz = (C - X) / 43, (C - Z) / 43
        for y in (F + 22, F + 12):                                       # the gibbet arm and its cage
            for j in range(4, 9):
                ar.put(X + fx * j, y, Z + fz * j, PBB)
            cx, cz = X + fx * 8, Z + fz * 8
            for j in range(1, 3):
                ar.put(cx, y - j, cz, CHAIN)
            for dy in range(-7, -3):
                for (dx, dz) in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
                    ar.put(cx + dx, y + dy, cz + dz, ('minecraft:iron_bars', None))
            ar.put(cx, y - 7, cz, PBB)
            ar.put(cx, y - 3, cz, PBB)
            ar.put(cx, y - 6, cz, 'minecraft:skeleton_skull')
        ar.put(X, F + 36, Z, ('minecraft:soul_campfire', {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}))
    # the Hollow King's empty throne, behind the Master's side (north)
    TX, TZ = C, C - 47
    for x in range(TX - 9, TX + 10):
        for z in range(TZ - 6, TZ + 7):
            for y in range(F - 1, F + 4):
                if abs(x - TX) <= 9 - (y - F + 1) and abs(z - TZ) <= 6:
                    ar.put(x, y, z, PBB)                                  # the dais
    for x in range(TX - 4, TX + 5):
        for y in range(F + 3, F + 32):
            for z in range(TZ - 4, TZ - 1):
                if abs(x - TX) <= 4 - max(0, (y - F - 24)) * 0.5:
                    ar.put(x, y, z, 'minecraft:gilded_blackstone' if (y - F) % 6 == 0 else BS)       # the back, narrowing to a point
        for z in range(TZ - 1, TZ + 4):
            ar.put(x, F + 8, z, PBB)                                      # the seat
            if abs(x - TX) >= 3:
                for y in range(F + 9, F + 13):
                    ar.put(x, y, z, BS)                                  # the arms
    for s in (-1, 1):
        ar.spike(TX + s * 5, TZ - 3, F + 26, 14, 1.6, OBS)               # horns
        ar.spike(TX + s * 3, TZ - 3, F + 30, 8, 1.0, 'minecraft:gilded_blackstone')
    ar.put(TX, F + 20, TZ - 1, 'minecraft:wither_skeleton_skull', {'rotation': '0'})
    # chains hanging from the roof all round the dome
    for k in range(40):
        a = ar.rnd.uniform(0, 2 * math.pi)
        r = ar.rnd.uniform(34, 44)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        top = F + int(35 * math.sqrt(max(0.0, 1 - (r / 46) ** 2)))
        ln = ar.rnd.randint(5, 14)
        for y in range(top - ln, top + 1):
            ar.put(x, y, z, CHAIN)
        ar.put(x, top - ln - 1, z, hanging_lantern())


def drowned(ar):
    braziers(ar, n=6, r=29.0, base='minecraft:prismarine_bricks')
    gap_markers(ar, 'minecraft:prismarine_bricks', 'minecraft:sea_lantern')
    # the leviathan's ribcage: a spine overhead running east to west, ribs curving down round the water ring
    for x in range(C - 44, C + 41):
        r = 2.8 if (x - C) % 6 == 0 else 2.0
        ar.ball(x, F + 37 + 2 * math.sin((x - C) / 30), C, r, lambda X, Y, Z: (BONE, AX) if h(X, Y, Z) < 0.8 else 'minecraft:calcite', open_ok=True)
        if (x - C) % 6 == 0:
            ar.spike(x, C, F + 39, 6, 1.4, (BONE, AX))
    for x in range(C - 36, C + 37, 6):
        top = F + 36 + 2 * math.sin((x - C) / 30)
        for s in (-1, 1):
            ctrl = [(x, top, C), (x, top - 3, C + s * 16), (x, F + 25, C + s * 30), (x, F + 6, C + s * 36), (x, F - 10, C + s * 34)]
            path = catmull(ctrl, 50)
            ar.tube(path, lambda t: 1.9 - 0.7 * t, lambda X, Y, Z, t: (BONE, AX) if h(X, Y, Z) < 0.85 else 'minecraft:dark_prismarine', open_ok=True)
            for i in range(6, len(path), 9):                             # kelp and seagrass hung off the ribs
                px, py, pz = path[i]
                if py > F + 31:
                    for y in range(int(py) - 3, int(py) - 1):
                        ar.put(px, y, pz, CHAIN)
                    ar.put(px, int(py) - 4, pz, hanging_lantern())
    # the skull at the east end, jaws open toward the arena
    SX, SY, SZ = C + 46, F + 30, C
    for x in range(SX - 9, SX + 12):
        for y in range(SY - 14, SY + 10):
            for z in range(SZ - 10, SZ + 11):
                u, w, v = x - SX, y - SY, z - SZ
                cran = (u / 9) ** 2 + (w / 8) ** 2 + (v / 9) ** 2 <= 1 and (u / 7.5) ** 2 + (w / 6.5) ** 2 + (v / 7.5) ** 2 > 1
                jaw = -14 <= w <= -9 and -8 <= u <= 10 and abs(v) <= 7 - max(0, u - 2) * 0.4 and not (abs(v) < 5 and w > -12)
                if cran or jaw:
                    eye = abs(abs(v) - 4) < 1.6 and -2 <= w <= 1 and u < -6
                    ar.put(x, y, z, 'minecraft:sea_lantern' if eye else ((BONE, AX) if h(x, y, z) < 0.85 else 'minecraft:calcite'), open_ok=True)
    for k in range(9):                                                   # fangs
        z = SZ - 7 + k * 1.75
        ar.spike(SX - 7, z, SY - 2, 6, 0.9, 'minecraft:calcite', up=False)
        ar.spike(SX - 6, z, SY - 9, 5, 0.9, 'minecraft:calcite')
    # drowned columns round the outside, some fallen
    for k in range(12):
        a = math.radians(k * 30 + 15)
        X, Z = C + 44 * math.cos(a), C + 44 * math.sin(a)
        ht = ar.rnd.randint(6, 20)
        ar.column(X, Z, 1.6, F - 14, F + ht, lambda x, y, z: 'minecraft:prismarine_bricks' if (y % 5) else 'minecraft:mossy_stone_bricks')
        ar.put(X, F + ht, Z, 'minecraft:sea_lantern')
    for k in range(20):                                                  # kelp beds on the walkway's outer rim
        a = ar.rnd.uniform(0, 2 * math.pi)
        x, z = C + 30 * math.cos(a), C + 30 * math.sin(a)
        ar.put(x, F, z, ('minecraft:sea_pickle', {'pickles': '3', 'waterlogged': 'false'}), open_ok=True)


def pale(ar):
    def ice(x, y, z, w, ht):
        return 'minecraft:blue_ice' if h(x, y, z) < 0.3 else ('minecraft:packed_ice' if w < ht - 2 else 'minecraft:ice')
    perimeter(ar, ice, height=(3, 15), r0=33.5, r1=37.5)
    braziers(ar, n=8, base='minecraft:packed_ice')
    gap_markers(ar, 'minecraft:packed_ice', ('minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'}))
    for k in range(18):                                                  # ice spikes jutting from the wall, leaning out
        a = math.radians(k * 20 + 7)
        if in_gap(a, 0.2):
            continue
        X, Z = C + 37 * math.cos(a), C + 37 * math.sin(a)
        ar.spike(X, Z, F - 2, ar.rnd.randint(14, 26), 2.2, lambda x, y, z: 'minecraft:packed_ice' if h(x, y, z) < 0.7 else 'minecraft:blue_ice',
                 lean=(math.cos(a) * 0.25, math.sin(a) * 0.25))

    def mourner(u, w, v, x, y, z):
        """A hooded figure of ice, hands over its face, weeping blue ice down its robe."""
        if w < 0:
            return None
        if w < 3 and abs(u) <= 4.5 and abs(v) <= 4.5:
            return 'minecraft:packed_ice' if w < 2 else 'minecraft:blue_ice'
        if 3 <= w < 22:
            t = (w - 3) / 19
            ru, rv = 4.8 - 1.8 * t, 3.6 - 1.2 * t
            if (u / ru) ** 2 + (v / rv) ** 2 <= 1:
                if abs(u) < 0.6 and v > rv - 1.2 and t > 0.3:
                    return 'minecraft:blue_ice'                           # the frozen tears
                return 'minecraft:snow_block' if h(x, y, z) < 0.35 else 'minecraft:packed_ice'
        if 22 <= w < 30:
            d = math.sqrt((u / 3.0) ** 2 + ((v + 0.3) / 3.2) ** 2 + ((w - 25.5) / 4.0) ** 2)
            if d <= 1:
                if v > 1.6 and abs(u) < 1.8 and 23 <= w <= 27:
                    return 'minecraft:light_gray_concrete' if w >= 25 else None     # the hands raised over the face
                return 'minecraft:packed_ice' if h(x, y, z) < 0.8 else 'minecraft:snow_block'
        if 18 <= w < 25:                                                  # the arms, bent up to the face
            for s in (-1, 1):
                if (u - s * 2.2) ** 2 + (v - 1.4 - (w - 18) * 0.15) ** 2 <= 1.4:
                    return 'minecraft:packed_ice'
        return None
    for k in range(8):
        a = math.radians(22.5 + k * 45)
        X, Z = C + 44 * math.cos(a), C + 44 * math.sin(a)
        ar.column(X, Z, 5, F - 14, F - 1, 'minecraft:packed_ice')
        ar.local(X, Z, a, mourner, 7, F - 1, F + 31)
        for j in range(2):                                               # frozen chains from the plinth to the wall
            b = a + (0.08 if j else -0.08)
            for t in range(37, 41):
                ar.put(C + t * math.cos(b), F + 2, C + t * math.sin(b), ('minecraft:chain', {'axis': 'x', 'waterlogged': 'false'}))
    # blue ice cracks across the battleground
    for k in range(9):
        a0 = math.radians(k * 40 + 12)
        for t in range(13, 33):
            a = a0 + 0.08 * math.sin(t * 0.9 + k)
            ar.put(C + t * math.cos(a), F - 1, C + t * math.sin(a), 'minecraft:blue_ice', open_ok=True)


def scarlet(ar):
    # the colosseum: tiers stepping up and out from the battleground
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if not (33.5 < d <= 50):
                continue
            a = math.atan2(z - C, x - C)
            if in_gap(a, 0.09):
                continue
            tier = int((d - 33.5) / 2)
            top = F - 1 + min(tier * 2, 15)
            for y in range(F - 10, top + 1):
                b = 'minecraft:smooth_red_sandstone' if y == top and tier % 2 == 0 else ('minecraft:cut_red_sandstone' if y == top else 'minecraft:red_sandstone')
                ar.put(x, y, z, b, open_ok=True)
            if d > 48.5:
                for y in range(top + 1, top + 4):
                    ar.put(x, y, z, 'minecraft:red_sandstone_wall' if y < top + 3 else 'minecraft:chiseled_red_sandstone', open_ok=True)
    braziers(ar, n=8, r=32.5, base='minecraft:chiseled_red_sandstone')
    gap_markers(ar, 'minecraft:chiseled_red_sandstone', 'minecraft:ochre_froglight')
    for k in range(8):                                                   # sun obelisks on the top tier
        a = math.radians(22.5 + k * 45)
        X, Z = C + 52 * math.cos(a), C + 52 * math.sin(a)
        for j in range(40):
            r = 2.4 * (1 - j / 46)
            for x in range(int(X - r) - 1, int(X + r) + 2):
                for z in range(int(Z - r) - 1, int(Z + r) + 2):
                    if max(abs(x - X), abs(z - Z)) <= r:
                        ar.put(x, F - 10 + j, z, 'minecraft:chiseled_red_sandstone' if j % 8 == 0 else 'minecraft:cut_red_sandstone')
        ar.ball(X, F + 32, Z, 2.4, lambda x, y, z: 'minecraft:gold_block' if h(x, y, z) < 0.5 else 'minecraft:red_stained_glass')
        ar.put(X, F + 32, Z, 'minecraft:ochre_froglight')
    rnd = ar.rnd
    for k in range(30):                                                  # spears driven into the tiers, skulls on some
        a = rnd.uniform(0, 2 * math.pi)
        if in_gap(a, 0.12):
            continue
        r = rnd.uniform(36, 47)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        tier = int((r - 33.5) / 2)
        top = F - 1 + min(tier * 2, 15)
        ht = rnd.randint(3, 6)
        for y in range(top + 1, top + 1 + ht):
            ar.put(x, y, z, ('minecraft:iron_bars', None) if y < top + ht else 'minecraft:end_rod', open_ok=True)
        if rnd.random() < 0.4:
            ar.put(x, top + 1 + ht, z, 'minecraft:skeleton_skull', open_ok=True)
    # Kharzul's scythe blade, driven point-first into the stone on the west side
    BX, BZ = C - 42, C
    for t in range(0, 60):
        ang = math.radians(-20 + t * 2.4)
        r = 22
        y = F - 6 + r * math.sin(ang) + 12
        zc = BZ + r * math.cos(ang) - 14
        wdt = 2.6 * math.sin(math.pi * t / 60) + 0.5
        for s in range(-int(wdt) - 1, int(wdt) + 2):
            if abs(s) <= wdt:
                ar.put(BX + s * 0.3, y + s, zc, 'minecraft:red_stained_glass' if abs(s) < wdt - 0.8 else 'minecraft:netherite_block', open_ok=True)
    for y in range(F + 22, F + 46):                                      # the haft, broken off
        ar.put(BX, y, BZ - 14 + 22 * math.cos(math.radians(124)) + (y - F - 22) * 0.05, 'minecraft:polished_blackstone')


def clockwork(ar):
    braziers(ar, n=4, r=31.5, base='minecraft:polished_blackstone_bricks')
    gap_markers(ar, 'minecraft:deepslate_tiles', 'minecraft:pearlescent_froglight')

    def wall(x, y, z, w, ht):
        return 'minecraft:gold_block' if w == ht - 1 else ('minecraft:polished_blackstone_bricks' if w % 4 else 'minecraft:deepslate_tiles')
    perimeter(ar, wall, height=(2, 4), r0=33.5, r1=35.5)
    for k in range(12):                                                  # the hour pillars
        a = math.radians(k * 30 - 90)
        if in_gap(a, 0.15):
            a += 0.18
        X, Z = C + 38 * math.cos(a), C + 38 * math.sin(a)
        ht = 22 if k % 3 == 0 else 16
        ar.column(X, Z, 2.2, F - 9, F + ht, lambda x, y, z: 'minecraft:deepslate_tiles' if (y - F) % 5 else 'minecraft:gold_block')
        for n in range(k % 4 + 1):                                       # tally of gold marks facing the centre
            ar.put(X - 2.6 * math.cos(a), F + ht - 3 - n * 2, Z - 2.6 * math.sin(a), 'minecraft:gold_block')
        ar.put(X, F + ht, Z, 'minecraft:pearlescent_froglight', AX)
        ar.spike(X, Z, F + ht + 1, 5, 1.2, 'minecraft:gold_block')

    def disc_gear(X, Y, Z, a, r, teeth, block, hub):
        """A gear standing on edge, facing the altar."""
        nx, nz = math.cos(a), math.sin(a)
        ux, uz = -nz, nx
        for i in range(-r - 3, r + 4):
            for j in range(-r - 3, r + 4):
                d = math.hypot(i, j)
                ang = math.atan2(j, i)
                tooth = math.cos(ang * teeth) > 0.2
                if d <= r - 1 or (d <= r + 1.6 and tooth):
                    if d < 1.6:
                        b = hub
                    elif r * 0.45 < d < r * 0.6 or (d <= r - 1 and abs(math.sin(ang * 3)) > 0.35 and d < r * 0.8):
                        continue                                         # spokes
                    else:
                        b = block
                    for dep in (0, 1):
                        ar.put(X + ux * i + nx * dep, Y + j, Z + uz * i + nz * dep, b)
    for k in range(8):
        a = math.radians(k * 45 + 22.5)
        big = k % 2 == 0
        r = 13 if big else 8
        X, Z = C + (46 if big else 42) * math.cos(a), C + (46 if big else 42) * math.sin(a)
        disc_gear(X, F + r - 4, Z, a, r, 14 if big else 9, 'minecraft:waxed_cut_copper' if big else 'minecraft:gold_block', 'minecraft:polished_blackstone')
    for k in range(4):                                                   # pendulum blades on gallows, swinging over the outer ring
        a = math.radians(k * 90)
        X, Z = C + 52 * math.cos(a), C + 52 * math.sin(a)
        ux, uz = -math.sin(a), math.cos(a)
        for s in (-1, 1):
            ar.column(X + ux * s * 6, Z + uz * s * 6, 1.0, F - 9, F + 34, 'minecraft:polished_blackstone_bricks')
        for t in range(-6, 7):
            ar.put(X + ux * t, F + 34, Z + uz * t, 'minecraft:gold_block')
        for y in range(F + 10, F + 34):
            ar.put(X, y, Z, CHAIN)
        for t in range(-5, 6):                                           # the crescent blade
            yy = F + 8 + int(abs(t) ** 1.6 / 4)
            for q in range(0, 3):
                ar.put(X + ux * t, yy - q, Z + uz * t, 'minecraft:iron_block' if q < 2 else 'minecraft:netherite_block')
    for k in range(10):                                                  # gears turning under the platform
        a = ar.rnd.uniform(0, 2 * math.pi)
        r = ar.rnd.uniform(10, 26)
        disc_gear(C + r * math.cos(a), F - 22 - ar.rnd.randint(0, 10), C + r * math.sin(a), a + 1.2, ar.rnd.randint(4, 7), 8,
                  'minecraft:gold_block' if k % 2 else 'minecraft:waxed_cut_copper', 'minecraft:polished_blackstone')


def mycelial(ar):
    braziers(ar, n=6, r=31.0, base='minecraft:bone_block')
    gap_markers(ar, ('minecraft:mushroom_stem', None), 'minecraft:pearlescent_froglight')
    for k in range(10):                                                  # the petals, leaning in like a closing flower
        a = math.radians(k * 36 + 18)
        if in_gap(a, 0.22):
            a += 0.3
        for t in range(0, 44):
            frac = t / 43
            r = 36 + 4 * math.sin(math.pi * frac) - frac * 6
            y = F - 4 + t * 0.85
            wdt = 9 * math.sin(math.pi * min(1, frac * 1.15)) + 1
            for s in range(-int(wdt) - 1, int(wdt) + 2):
                if abs(s) > wdt:
                    continue
                aa = a + s / r
                x, z = C + r * math.cos(aa), C + r * math.sin(aa)
                vein = abs(s) < 0.7 or abs(abs(s) - wdt * 0.5) < 0.5
                for dep in (0, 1):
                    xx, zz = x + math.cos(aa) * dep, z + math.sin(aa) * dep
                    ar.put(xx, y, zz, 'minecraft:pearlescent_froglight' if vein and dep == 0 and t % 3 == 0 else
                           ('minecraft:pink_terracotta' if vein else ('minecraft:magenta_terracotta' if h(int(xx), int(y), int(zz)) < 0.6 else 'minecraft:purple_wool')),
                           AX if vein and dep == 0 and t % 3 == 0 else None)
    for k in range(8):                                                   # flesh pillars, ribbed in bone, glowing between the ribs
        a = math.radians(k * 45)
        X, Z = C + 45 * math.cos(a), C + 45 * math.sin(a)
        ar.column(X, Z, 3.0, F - 12, F + 34, lambda x, y, z: ('minecraft:bone_block', AX) if (y - F) % 6 == 0 else
                  ('minecraft:shroomlight' if h(x, y, z) < 0.12 else ('minecraft:mushroom_stem' if h(x, y, z, 2) < 0.6 else 'minecraft:pink_terracotta')))
    for k in range(16):                                                  # spore pods hung from the roof
        a = ar.rnd.uniform(0, 2 * math.pi)
        r = ar.rnd.uniform(20, 42)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        top = F + int(35 * math.sqrt(max(0.0, 1 - (r / 46) ** 2)))
        ln = ar.rnd.randint(2, 5)
        py = top - ln - 3
        if r < OPEN_R and py <= F + 31:
            py = F + 33
        for y in range(py + 2, top + 1):
            ar.put(x, y, z, CHAIN, open_ok=True)
        ar.ball(x, py, z, 2.0, lambda X, Y, Z: 'minecraft:pearlescent_froglight' if (X + Y + Z) % 3 == 0 else 'minecraft:pink_wool', open_ok=True)
    for k in range(24):                                                  # bone spikes through the floor's edge
        a = ar.rnd.uniform(0, 2 * math.pi)
        x, z = C + 34 * math.cos(a), C + 34 * math.sin(a)
        if not in_gap(a, 0.15):
            ar.spike(x, z, F - 1, ar.rnd.randint(3, 8), 1.0, (BONE, AX), open_ok=True)


BUILD = {'grove': grove, 'skyreach': skyreach, 'hollow': hollow, 'drowned': drowned, 'pale': pale, 'scarlet': scarlet,
         'clockwork': clockwork, 'mycelial': mycelial}


def build(realm):
    ar = Arena(realm)
    ground(ar)
    BUILD[realm](ar)
    was = gen_citadels2.ENRICH
    gen_citadels2.ENRICH = False
    try:
        ar.g.save(f'arena_{realm}')
    finally:
        gen_citadels2.ENRICH = was
    return ar.g


def main(only=None):
    for r in only or BUILD:
        build(r)


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
