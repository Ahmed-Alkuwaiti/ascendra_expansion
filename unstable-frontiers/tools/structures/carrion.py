"""The Carrion Field and the small wayside landmarks that lead the eye across the frontier.

Carrion Field: the half-buried skeleton of something enormous, still being eaten. Insects work inside the ribcage,
predators stand on the spine and the skull; that is where the two kinds meet and fight. The gullet holds what the
beast swallowed.

Waysides (small, common): a fallen gibbet cage, an impaled carcass on a spike, an egg cluster, a claw-scored stone.
"""
import math

from common import *
from kit import AIR, B, Build, h


def carrion():
    W, H, L = 67, 34, 41
    G = 6
    b = Build('carrion_field', W, H, L, seed=51)
    # the churned ground: mud and coarse dirt, gore, flies (the mod adds the flies)
    for x in range(W):
        for z in range(L):
            d = ((x - 33) / 33) ** 2 + ((z - 20) / 20) ** 2
            if d < 1:
                q = h(x, G, z, 3)
                b.set(x, G, z, MUD if q < 0.3 else (COARSE if q < 0.6 else ('minecraft:podzol' if q < 0.8 else ROOTED)))
                if q > 0.97:
                    b.set(x, G + 1, z, BONE_Y)
    # the spine: a long arc of vertebrae half sunk in the ground
    spine = [(6, G - 1, 20), (18, G + 7, 21), (32, G + 10, 20), (46, G + 8, 19), (58, G + 3, 20), (64, G - 1, 21)]
    b.curve(spine, BONE_X, radius=lambda t: 1.4)
    for i in range(0, 60, 3):
        t = i / 60
        p = spine_point(spine, t)
        b.ellipsoid(p[0], p[1] + 1.6, p[2], 0.9, 1.6, 0.9, BONE_Y)         # dorsal spikes
    # ribs: arches from the spine into the ground on both sides, the biggest in the middle
    for k in range(9):
        t = 0.22 + k * 0.06
        top = spine_point(spine, t)
        span = 11 + 5 * math.sin(math.pi * (k + 0.5) / 9)
        for side in (-1, 1):
            if (k + (side > 0)) % 4 == 3:
                continue          # a broken rib
            p0 = (top[0], top[1], top[2])
            p1 = (top[0] + 1.5 * side, top[1] + 2, top[2] + side * span * 0.55)
            p2 = (top[0] + 2.5 * side, G - 1, top[2] + side * span)
            b.curve([p0, p1, p2], BONE_Z, radius=lambda t: 0.9 - 0.3 * t)
    # flesh still on the bones: wart and mushroom gore, sculk where it has rotted
    for k in range(70):
        t = 0.2 + (k % 23) / 40
        p = spine_point(spine, t)
        dz = ((k * 7) % 17) - 8
        x, y, z = round(p[0] + (k % 3) - 1), G + 1 + (k % 4), round(p[2] + dz)
        if h(x, y, z, 6) < 0.6:
            b.set(x, y, z, 'minecraft:nether_wart_block' if k % 3 else ('minecraft:sculk' if k % 2 else 'minecraft:red_mushroom_block'), over=False)
    # the skull: a great bone helm with eye pits and a jaw full of teeth, the gullet behind it
    sx, sy, sz = 8, G + 4, 20
    b.ellipsoid(sx, sy, sz, 7, 5.5, 6, lambda x, y, z: BONE_Y if h(x, y, z, 8) < 0.8 else 'minecraft:calcite', shell=0.55)
    b.ellipsoid(sx, sy, sz, 6, 4.5, 5, AIR)
    for ez in (sz - 3, sz + 3):
        b.ellipsoid(sx - 5, sy + 2, ez, 1.6, 1.4, 1.4, AIR)
        b.set(sx - 4, sy + 2, ez, 'minecraft:magma_block')
    for x in range(sx - 8, sx - 1):
        for z in range(sz - 4, sz + 5):
            if abs(z - sz) == 4 or x == sx - 8:
                b.set(x, sy - 3, z, BONE_Y)
                if (x + z) % 2 == 0:
                    b.set(x, sy - 2, z, B('pointed_dripstone', thickness='tip', vertical_direction='up', waterlogged='false'))
    b.box(sx - 7, sy - 2, sz - 2, sx - 5, sy, sz + 2, AIR)          # the open mouth
    b.chest(sx + 1, sy - 3, sz, 'chests/carrion_gullet', facing='west')
    b.point('vault', sx + 1, sy - 3, sz)
    b.set(sx + 2, sy - 3, sz + 1, SKULL)
    b.set(sx + 2, sy - 3, sz - 1, BONE_X)
    # residents: where insects feed (inside the ribs) and where predators stand (spine and skull)
    feed = [(round(spine_point(spine, t)[0]), G + 1, 20 + dz) for t in (0.3, 0.42, 0.55, 0.66) for dz in (-4, 4)]
    perch = [(round(spine_point(spine, t)[0]), round(spine_point(spine, t)[1]) + 3, 20) for t in (0.35, 0.5, 0.65)] + [(sx, sy + 6, sz)]
    b.meta['residents'] = [{'roster': 'carrion_swarm', 'spots': [list(p) for p in feed], 'count': 4},
                           {'roster': 'carrion_raptors', 'spots': [list(p) for p in perch], 'count': 2, 'flying': True}]
    b.meta['rivalry'] = {'hunters': 'carrion_raptors', 'prey': 'carrion_swarm'}
    b.zone('feeding', 'The Feeding', (4, G, 4, 62, G + 16, 36), feed, 'carrion_swarm', kind='territory')
    b.meta.update({'kind': 'carrion', 'title': 'Carrion Field', 'ground': G})
    return b


def spine_point(spine, t):
    segs = len(spine) - 1
    s = min(segs - 1, int(t * segs))
    u = t * segs - s
    a, c = spine[s], spine[s + 1]
    return tuple(a[i] + (c[i] - a[i]) * u for i in range(3))


# ---------------------------------------------------------------- waysides
def fallen_gibbet():
    b = Build('wayside_fallen_gibbet', 11, 8, 11, seed=61)
    G = 1
    for x in range(1, 10):
        for z in range(1, 10):
            if h(x, 0, z) < 0.5:
                b.set(x, G - 1, z, COARSE)
    # a cage on its side, door burst open, the chain still running back to a broken post
    for x in range(3, 8):
        for y in range(G, G + 4):
            for z in range(3, 7):
                edge = x in (3, 7) or y in (G, G + 3) or z in (3, 6)
                if edge:
                    b.set(x, y, z, B('iron_bars') if not (y in (G, G + 3) and x in (3, 7)) else BASALT)
    for y in range(G, G + 3):
        b.set(7, y, 4, AIR)
        b.set(7, y, 5, AIR)
    b.set(5, G, 4, SKULL)
    b.set(4, G, 5, BONE_X)
    b.line((5, G + 3, 6), (5, G, 9), CHAIN_Z)
    b.box(5, G, 9, 5, G + 2, 9, DARK_LOG_Y)
    b.set(5, G + 3, 9, slab('polished_blackstone', 'bottom'))
    b.meta.update({'kind': 'wayside', 'ground': G})
    return b


def impaled():
    b = Build('wayside_impaled', 9, 14, 9, seed=62)
    G = 1
    for y in range(G - 1, G + 10):
        r = 1.6 * (1 - (y - G) / 12) + 0.4
        b.cylinder(4, 4, r, y, y, lambda x, yy, z: DARK_BRICK if h(x, yy, z) < 0.7 else BASALT)
    b.set(4, G + 10, 4, wall('polished_blackstone_brick'))
    b.set(4, G + 11, 4, ROD_UP)
    # the carcass hung on it: ribs of bone, a skull, rot below
    b.ellipsoid(4, G + 6, 4, 2.5, 1.2, 1.5, lambda x, y, z: BONE_X if h(x, y, z) < 0.6 else 'minecraft:nether_wart_block', over=False)
    b.set(6, G + 7, 4, SKULL)
    for k in range(6):
        b.set(2 + k % 5, G - 1, 2 + (k * 3) % 5, 'minecraft:nether_wart_block' if k % 2 else MUD)
    b.meta.update({'kind': 'wayside', 'ground': G})
    return b


def egg_cluster():
    b = Build('wayside_egg_cluster', 11, 6, 11, seed=63)
    G = 1
    b.ellipsoid(5, G - 1, 5, 4.5, 1.6, 4, lambda x, y, z: MUD if h(x, y, z) < 0.6 else PACKED_MUD)
    for x in range(1, 10):
        for z in range(1, 10):
            if b.get(x, G, z) in (None, AIR) and b.get(x, G - 1, z) not in (None, AIR):
                q = h(x, G, z, 4)
                if q < 0.45:
                    b.set(x, G, z, B('turtle_egg', eggs=1 + int(q * 10) % 4, hatch=0))
                elif q > 0.85:
                    b.set(x, G, z, 'minecraft:white_wool')
                    b.set(x, G + 1, z, COBWEB)
    b.meta.update({'kind': 'wayside', 'ground': G})
    return b


def claw_stone():
    b = Build('wayside_claw_stone', 11, 12, 11, seed=64)
    G = 1
    b.ellipsoid(5, G + 3, 5, 3.5, 5.5, 3, lambda x, y, z: rock(x, y, z, 6))
    # three parallel gouges raked down one face, and a bone left at the foot
    for k in range(3):
        for y in range(G + 2, G + 8):
            x = 2 + k
            z = 2 + (y - G) // 3
            for zz in range(1, 6):
                if b.solid(x, y, zz):
                    b.set(x, y, zz, AIR)
                    b.set(x + 1, y, zz, 'minecraft:cobbled_deepslate' if b.solid(x + 1, y, zz) else None)
                    break
    b.set(1, G, 7, BONE_Z)
    b.set(2, G, 8, SKULL)
    b.meta.update({'kind': 'wayside', 'ground': G})
    return b


if __name__ == '__main__':
    carrion().save(foundation_level=None)
    for f in (fallen_gibbet, impaled, egg_cluster, claw_stone):
        f().save()
