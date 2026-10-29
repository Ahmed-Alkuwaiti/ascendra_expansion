"""The Astral Abyss's five places, built onto the islands its generator keeps for them (AbyssTerrain's anchors):

    the Landing        where the rift sets you down: the return gate, a guide, signposts toward the other places
    the Starwell       a ring of standing stones around a well of light: waves; the Blinkstone and a Sigil Shard
    the Drifting Archive  a roofless library with reading platforms floating above it: the Archivist; a Sigil Shard
    the Tether Spire   a needle chained to platforms you climb by updraft: an ambush on the wing; a Sigil Shard
    the Hollow Crown   the boss arena: obelisks for cover, a low rim, the Eclipse Altar, a crown of broken spires

Each template's ground row is its floor, laid over the island's top (AbyssPlaces places it there). Rows below it fill the
island's uneven top, so a floor never floats; anything above is the place itself.
"""
import math

from common import *
from kit import AIR, B, Build, h

U = 'unstable_frontiers:'
ASTRAL = U + 'astral_bricks'
CHISELED = U + 'chiseled_astral'
SHALE = U + 'astral_shale'
STARMOSS = U + 'starmoss'
LUMEN = U + 'lumen_crystal'
RIFT_GLASS = U + 'rift_glass'
TENDRIL = U + 'void_tendril'
VENT = U + 'updraft_vent'
BLOOM = U + 'starbloom'
GATE_OPEN = B(U + 'abyss_gate', open='true')
ALTAR = U + 'eclipse_altar'
CHAIN_Y = B('chain', axis='y', waterlogged='false')

# the anchors as AbyssTerrain has them (x, z, radius, top), for the signposts
ANCHORS = {'landing': (0, 0, 20, 100), 'starwell': (232, -148, 24, 112), 'archive': (-236, -72, 30, 122),
           'tether_spire': (64, 268, 20, 92), 'hollow_crown': (24, 560, 46, 112)}
NAMES = {'starwell': 'The Starwell', 'archive': 'The Drifting Archive', 'tether_spire': 'The Tether Spire',
         'hollow_crown': 'The Hollow Crown'}


def stone(x, y, z, salt=0):
    r = h(x, y, z, salt)
    if r < 0.08:
        return CHISELED
    if r < 0.2:
        return SHALE
    return ASTRAL


def disc(b, cx, cz, r, y, pick, depth=0, under=SHALE):
    """A floor disc at row y, with `depth` rows of fill below it (tapering), so it sits on uneven island tops."""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            d = math.hypot(x - cx, z - cz)
            if d <= r:
                b.set(x, y, z, pick(x, y, z) if callable(pick) else pick)
                for k in range(1, depth + 1):
                    if d <= r - k * 0.6:
                        b.set(x, y - k, z, under)


def clear_above(b, cx, cz, r, y0, y1):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            if math.hypot(x - cx, z - cz) <= r:
                for y in range(y0, y1 + 1):
                    b.set(x, y, z, AIR)


def lamp_post(b, x, y, z, height=4):
    for k in range(height):
        b.set(x, y + k, z, 'minecraft:deepslate_brick_wall' if k else CHISELED)
    b.set(x, y + height, z, LUMEN)


def sign_rotation(dx, dz):
    """Standing-sign rotation whose text faces back along (dx, dz), toward a reader at the centre."""
    yaw = math.degrees(math.atan2(dx, -dz))
    return round(yaw / 22.5) % 16


def overgrow(b, rate=0.05):
    for (x, y, z), (name, _) in list(b.b.items()):
        if name == STARMOSS and b.get(x, y + 1, z) in (None, AIR) and h(x, y, z, 7) < rate:
            b.set(x, y + 1, z, BLOOM)
        if name in (ASTRAL, SHALE, CHISELED) and b.get(x, y - 1, z) == AIR and h(x, y, z, 8) < rate * 0.6:
            b.set(x, y - 1, z, TENDRIL)


# ------------------------------------------------------------------------------------------------------- the Landing
def landing():
    W = L = 33
    C, G = 16, 6
    b = Build('abyss_landing', W, 26, L, seed=201)
    disc(b, C, C, 11, G, lambda x, y, z: CHISELED if abs(math.hypot(x - C, z - C) - 7) < 0.6 else stone(x, y, z, 1), depth=6)
    disc(b, C, C, 3, G, LUMEN)
    disc(b, C, C, 2, G, ASTRAL)
    clear_above(b, C, C, 12, G + 1, G + 18)
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 11 < d <= 13 and b.get(x, G, z) is None and h(x, 0, z, 3) < 0.7:
                b.set(x, G, z, STARMOSS)
    # the return gate, north of the centre (arrivals stand five blocks south of the centre, facing it)
    gz = C - 7
    b.box(C - 3, G + 1, gz, C + 3, G + 8, gz, CHISELED)
    for x in range(C - 2, C + 3):
        for y in range(G + 1, G + 7):
            b.set(x, y, gz, GATE_OPEN)
    b.box(C - 3, G + 1, gz - 1, C + 3, G + 8, gz - 1, lambda x, y, z: stone(x, y, z, 2))
    for x in (C - 4, C + 4):
        for y in range(G + 1, G + 10):
            b.set(x, y, gz, 'minecraft:polished_deepslate' if y < G + 9 else LUMEN)
    b.set(C, G + 9, gz, LUMEN)
    b.point('gate', C, G + 1, gz)
    # lamp posts and benches round the stage
    for k in range(8):
        a = k * math.tau / 8 + math.pi / 8
        lamp_post(b, round(C + math.cos(a) * 10), G + 1, round(C + math.sin(a) * 10))
    # signposts toward the other places
    for name in ('starwell', 'archive', 'tether_spire'):
        ax, az = ANCHORS[name][0], ANCHORS[name][1]
        dist = round(math.hypot(ax, az))
        a = math.atan2(az, ax)
        sx, sz = round(C + math.cos(a) * 8), round(C + math.sin(a) * 8)
        b.set(sx, G + 1, sz, 'minecraft:polished_deepslate')
        b.sign(sx, G + 2, sz, sign_rotation(math.cos(a), math.sin(a)), [NAMES[name], f'{dist} blocks', 'follow its beam', ''])
    b.sign(C + 2, G + 1, C + 11, sign_rotation(0, 1), ['The Hollow Crown', 'beyond the', 'Tether Spire', ''])
    b.lectern_book(C + 3, G + 1, C - 3, 'south', 'Landing Notice', [
        'LANDING NOTICE\n\nThe gate behind this stage returns you to the observatory you came through.\n\nThe beams of light '
        'in the sky mark our stations. An astrolabe points the way to each.',
        'Each station keeps a shard of the Eclipse Sigil. Three shards and an eye of ender make the Sigil, which wakes '
        'what waits at the Hollow Crown.\n\nThe stepping stones between islands are ours. Keep to them.',
        'If you fall, the rift catches you and sets you back where you last stood, at a price.\n\nWhat you drop drifts '
        'to the nearest station. What you leave behind when you die waits fifteen minutes.'], author='Survey Office')
    overgrow(b, 0.03)
    b.meta.update({'kind': 'abyss_landing', 'title': 'The Landing', 'ground': G})
    return b


# ------------------------------------------------------------------------------------------------------ the Starwell
def starwell():
    W = L = 47
    C, G = 23, 22
    b = Build('abyss_starwell', W, G + 30, L, seed=202)
    disc(b, C, C, 19, G, lambda x, y, z: STARMOSS if h(x, y, z, 4) < 0.55 else stone(x, y, z, 5), depth=5)
    disc(b, C, C, 10, G, lambda x, y, z: CHISELED if abs(math.hypot(x - C, z - C) - 9) < 0.7 else ASTRAL)
    clear_above(b, C, C, 20, G + 1, G + 28)
    # the well: a shaft of light down into the island, a stair round its wall, a vent at the bottom to ride back up
    for y in range(G - 18, G + 1):
        for x in range(C - 7, C + 8):
            for z in range(C - 7, C + 8):
                d = math.hypot(x - C, z - C)
                if d <= 5.2:
                    b.set(x, y, z, AIR)
                elif d <= 6.6:
                    b.set(x, y, z, LUMEN if h(x, y, z, 6) < 0.08 else stone(x, y, z, 7))
    disc(b, C, C, 5.2, G - 19, lambda x, y, z: 'minecraft:light_blue_stained_glass' if h(x, y, z, 8) < 0.5 else LUMEN)
    b.set(C, G - 19, C, VENT)
    per = math.radians(14)
    for k in range(19):
        a = k * per
        for rr in (3.9, 4.6):
            x, z = round(C + math.cos(a) * rr), round(C + math.sin(a) * rr)
            y = G - k
            b.set(x, y, z, stair('deepslate_brick', tangent(x, z, C, C, reverse=True)))
            b.set(x, y - 1, z, 'minecraft:deepslate_bricks')
    for y in range(G - 18, G + 1, 6):   # rings of lumen lamps down the shaft
        for k in range(6):
            a = k * math.tau / 6 + y
            b.set(round(C + math.cos(a) * 5.6), y, round(C + math.sin(a) * 5.6), LUMEN)
    b.chest(C + 2, G - 18, C - 2, 'chests/abyss_cache', facing='west')
    # the column of light above the well: floating crystals in a slow helix
    for k in range(26):
        a = k * 0.55
        r = 2.5 + (k % 3)
        b.set(C + math.cos(a) * r, G + 3 + k, C + math.sin(a) * r, LUMEN if k % 2 else RIFT_GLASS)
    # the stone ring: twelve standing stones, three fallen
    for k in range(12):
        a = k * math.tau / 12
        x, z = round(C + math.cos(a) * 14), round(C + math.sin(a) * 14)
        if k in (2, 7, 10):
            dx, dz = round(math.cos(a + 1.3) * 1), round(math.sin(a + 1.3) * 1)
            for i in range(5):
                b.set(x + dx * i, G + 1, z + dz * i, stone(x + i, G, z, 9))
            continue
        hgt = 6 + int(h(k, 0, 0, 10) * 4)
        for y in range(G + 1, G + hgt + 1):
            for dx in (0, 1):
                for dz in (0, 1):
                    b.set(x + dx - (1 if math.cos(a) < 0 else 0), y, z + dz - (1 if math.sin(a) < 0 else 0), stone(x, y, z, 11))
        b.set(x, G + hgt + 1, z, LUMEN)
    b.lectern_book(C - 11, G + 1, C, 'east', 'Starwell Log', [
        'STARWELL STATION\n\nThe well reaches into the light under the island. Whatever falls into it comes back up '
        'on the draught. So will you: stand on the vent at the bottom.',
        'The lantern-mites nest round the stones. They come in waves.\n\nThe Blinkstone we cut here lets a surveyor step '
        'across a gap through the air. Use it when the stones run out.'], author='Survey Office')
    sp = [(round(C + math.cos(a) * 11), G + 1, round(C + math.sin(a) * 11)) for a in [k * math.tau / 8 + 0.2 for k in range(8)]]
    b.zone('starwell', 'The Starwell', (C - 18, G - 19, C - 18, C + 18, G + 12, C + 18), sp, 'abyss_starwell', kind='waves',
           reward='blinkstone,sigil_shard', trigger=(C - 15, G + 1, C - 15, C + 15, G + 10, C + 15))
    overgrow(b, 0.06)
    b.meta.update({'kind': 'abyss_place', 'title': 'The Starwell', 'ground': G})
    return b


def tangent(x, z, cx, cz, reverse=False):
    a = math.atan2(z - cz, x - cx)
    tx, tz = -math.sin(a), math.cos(a)
    if reverse:
        tx, tz = -tx, -tz
    if abs(tx) > abs(tz):
        return 'east' if tx > 0 else 'west'
    return 'south' if tz > 0 else 'north'


# ---------------------------------------------------------------------------------------------- the Drifting Archive
def archive():
    W = L = 57
    C, G = 28, 8
    TOP = G + 28
    b = Build('abyss_archive', W, G + 44, L, seed=203)
    disc(b, C, C, 24, G, lambda x, y, z: STARMOSS if h(x, y, z, 12) < 0.35 else stone(x, y, z, 13), depth=6)
    clear_above(b, C, C, 26, G + 1, G + 42)
    # the rotunda: a roofless library, its wall broken at the top
    for x in range(C - 11, C + 12):
        for z in range(C - 11, C + 12):
            d = math.hypot(x - C, z - C)
            a = math.atan2(z - C, x - C)
            if 9 <= d <= 10.6:
                top = G + 12 + int(7 * h(int((a + 4) * 4), 0, 0, 14))
                for y in range(G + 1, top + 1):
                    b.set(x, y, z, stone(x, y, z, 15))
            elif d < 9:
                b.set(x, G, z, 'minecraft:dark_oak_planks' if d > 3 else CHISELED)
    for k in range(4):   # doors
        a = k * math.pi / 2
        for d in range(8, 12):
            for w in (-1, 0, 1):
                x = round(C + math.cos(a) * d - math.sin(a) * w)
                z = round(C + math.sin(a) * d + math.cos(a) * w)
                for y in range(G + 1, G + 5):
                    b.set(x, y, z, AIR)
    for k in range(16):   # shelves round the wall
        a = k * math.tau / 16 + 0.2
        if k % 4 == 0:
            continue
        x, z = round(C + math.cos(a) * 8.2), round(C + math.sin(a) * 8.2)
        for y in range(G + 1, G + 4):
            b.set(x, y, z, 'minecraft:bookshelf' if h(x, y, z, 16) > 0.2 else 'minecraft:chiseled_bookshelf')
    # the stair round the inside of the wall to the walkway at G+12
    per = math.radians(9)
    for k in range(12):
        a = math.radians(30) + k * per
        for rr in (7.0, 7.8):
            x, z = round(C + math.cos(a) * rr), round(C + math.sin(a) * rr)
            b.set(x, G + 1 + k, z, stair('dark_oak', tangent(x, z, C, C)))
            if k:
                b.set(x, G + k, z, 'minecraft:dark_oak_planks')
    end = math.radians(30) + 11 * per
    # walkway from the stair's top out through the wall to the first floating platform
    ex, ez = C + math.cos(end) * 7.5, C + math.sin(end) * 7.5
    px, pz = C + math.cos(end) * 15, C + math.sin(end) * 15
    for i in range(30):
        t = i / 29
        x, z = ex + (px - ex) * t, ez + (pz - ez) * t
        for w in (-0.7, 0, 0.7):
            qx, qz = x - math.sin(end) * w, z + math.cos(end) * w
            b.set(qx, G + 12, qz, 'minecraft:dark_oak_planks')
            for y in range(G + 13, G + 16):
                b.set(qx, y, qz, AIR)
    # the first platform, with a vent whose draught passes the edge of the reading platform above
    disc(b, px, pz, 3.6, G + 12, lambda x, y, z: stone(x, y, z, 17), depth=3)
    for k in range(3):
        a = k * math.tau / 3
        b.set(px + math.cos(a) * 3, G + 13, pz + math.sin(a) * 3, 'minecraft:bookshelf')
    vx, vz = round(C + math.cos(end) * 11.5), round(C + math.sin(end) * 11.5)
    b.set(vx, G + 12, vz, VENT)
    for y in range(G + 13, TOP + 4):
        b.set(vx, y, vz, AIR)
    # the reading platform (the Archivist's), floating over the rotunda
    disc(b, C, C, 10.5, TOP, lambda x, y, z: CHISELED if abs(math.hypot(x - C, z - C) - 6) < 0.6 else stone(x, y, z, 18), depth=2)
    for x in range(C - 11, C + 12):
        for z in range(C - 11, C + 12):
            d = math.hypot(x - C, z - C)
            if 9.8 <= d <= 10.5 and h(x, 0, z, 19) < 0.7:
                b.set(x, TOP + 1, z, 'minecraft:deepslate_brick_wall')
    # an opening in the rail where the vent's draught comes up
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            b.set(vx + dx, TOP + 1, vz + dz, AIR) if b.get(vx + dx, TOP + 1, vz + dz) == 'minecraft:deepslate_brick_wall' else None
    b.set(vx, TOP, vz, AIR)
    for dy in range(1, 3):
        b.set(vx, TOP - dy, vz, AIR)
    for k in range(4):   # lecterns and shelves on the platform: cover from the Archivist's beam
        a = k * math.pi / 2 + math.pi / 4
        x, z = round(C + math.cos(a) * 5), round(C + math.sin(a) * 5)
        b.box(x - 1, TOP + 1, z, x + 1, TOP + 3, z, 'minecraft:bookshelf')
    b.chest(C, TOP + 1, C + 2, 'chests/abyss_cache', facing='south')
    for k in range(6):   # crystals hanging under the platform
        a = k * math.tau / 6
        for dy in range(1, 4):
            b.set(C + math.cos(a) * 7, TOP - 2 - dy, C + math.sin(a) * 7, LUMEN if dy == 3 else TENDRIL)
    # loose pages: book platforms drifting round about
    for k in range(7):
        a = k * math.tau / 7 + 0.5
        r = 17 + (k % 3) * 2
        y = G + 6 + (k * 5) % 22
        x, z = C + math.cos(a) * r, C + math.sin(a) * r
        disc(b, x, z, 1.6, y, lambda x_, y_, z_: stone(x_, y_, z_, 20), depth=1)
        b.set(x, y + 1, z, 'minecraft:bookshelf' if k % 2 else LUMEN)
    b.lectern_book(C - 3, G + 1, C, 'east', 'Archive Catalogue', [
        'ARCHIVE CATALOGUE\n\nThe reading room floats above the stacks. Climb the stair to the walkway; the draught on '
        'the outer platform carries you up.',
        'The orrery we left here to guard the shard has turned, like the others. When its rings stop, put a shelf '
        'between you and its lens.\n\nAfter it fires, it stalls. Strike then.'], author='Survey Office')
    sp = [(round(C + math.cos(a) * 7), TOP + 1, round(C + math.sin(a) * 7)) for a in (0.2, 1.8, 3.4, 5.0)]
    b.zone('archive', 'The Archivist', (C - 10, TOP + 1, C - 10, C + 10, TOP + 12, C + 10), sp, 'abyss_archive', kind='guardian',
           reward='sigil_shard', final=True, trigger=(C - 11, TOP - 2, C - 11, C + 11, TOP + 12, C + 11))
    overgrow(b, 0.05)
    b.meta.update({'kind': 'abyss_place', 'title': 'The Drifting Archive', 'ground': G})
    return b


# ----------------------------------------------------------------------------------------------- the Tether Spire
def tether_spire():
    W = L = 41
    C, G = 20, 8
    b = Build('abyss_tether_spire', W, G + 66, L, seed=204)
    disc(b, C, C, 16, G, lambda x, y, z: STARMOSS if h(x, y, z, 21) < 0.5 else stone(x, y, z, 22), depth=5)
    clear_above(b, C, C, 18, G + 1, G + 64)
    # a ring pool under the platforms: it breaks a fall from them
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 6.5 <= d <= 13.5:
                for y in (G - 2, G - 1, G):
                    b.set(x, y, z, 'minecraft:water')
                b.set(x, G - 3, z, SHALE)
            elif 13.5 < d <= 14.5 or 5.5 <= d < 6.5:
                for y in (G - 3, G - 2, G - 1, G):
                    b.set(x, y, z, CHISELED if y == G else SHALE)
    # the spire: a tapering needle of astral brick with lumen veins
    for y in range(G + 1, G + 62):
        r = 4.2 - (y - G) * 0.045
        for x in range(C - 5, C + 6):
            for z in range(C - 5, C + 6):
                d = math.hypot(x - C, z - C)
                if d <= r:
                    vein = abs(math.atan2(z - C, x - C) * 3 + y * 0.15) % math.tau < 0.25
                    b.set(x, y, z, LUMEN if vein and d > r - 1 else stone(x, y, z, 23))
    # three platforms climbing round it, each reached by a vent on the one below; chains tether them to the spire
    plats = [(0.4, G + 15), (2.5, G + 29), (4.6, G + 43)]
    prev_vent = None
    for i, (a, y) in enumerate(plats):
        px, pz = C + math.cos(a) * 10, C + math.sin(a) * 10
        disc(b, px, pz, 4.2, y, lambda x, y_, z: stone(x, y_, z, 24 + i), depth=2)
        for x in range(round(px) - 5, round(px) + 6):
            for z in range(round(pz) - 5, round(pz) + 6):
                d = math.hypot(x - px, z - pz)
                if 3.6 <= d <= 4.2 and h(x, i, z, 25) < 0.6:
                    b.set(x, y + 1, z, 'minecraft:deepslate_brick_wall')
        for k in range(30):
            t = k / 29
            sx, sz = C + math.cos(a) * 3, C + math.sin(a) * 3
            b.set(sx + (px - sx) * t, y + 6 - 6 * t, sz + (pz - sz) * t, B('chain', axis='x' if abs(math.cos(a)) > 0.7 else 'z', waterlogged='false'))
        # the vent on this platform, at its edge toward the next
        if i < len(plats) - 1:
            na = plats[i + 1][0]
            mid = (a + na) / 2
            vx, vz = round(C + math.cos(mid) * 10.5), round(C + math.sin(mid) * 10.5)
            disc(b, vx, vz, 1.6, y, lambda x, y_, z: stone(x, y_, z, 26), depth=1)
            b.set(vx, y, vz, VENT)
            for yy in range(y + 1, plats[i + 1][1] + 3):
                b.set(vx, yy, vz, AIR)
            # the next platform reaches out to the draught
            nx, nz = C + math.cos(na) * 10, C + math.sin(na) * 10
            for k in range(12):
                t = k / 11
                b.set(nx + (vx - nx) * t * 0.8, plats[i + 1][1], nz + (vz - nz) * t * 0.8, stone(vx, y, vz, 27))
            b.set(vx, plats[i + 1][1], vz, AIR)
    # the ground vent up to the first platform
    a, y = plats[0]
    gx, gz = round(C + math.cos(a - 0.5) * 9), round(C + math.sin(a - 0.5) * 9)
    disc(b, gx, gz, 1.5, G + 1, lambda x, y_, z: stone(x, y_, z, 28))
    b.set(gx, G + 1, gz, VENT)
    for yy in range(G + 2, y + 3):
        b.set(gx, yy, gz, AIR)
    px, pz = C + math.cos(a) * 10, C + math.sin(a) * 10
    for k in range(10):
        t = k / 9
        b.set(px + (gx - px) * t * 0.8, y, pz + (gz - pz) * t * 0.8, stone(gx, y, gz, 29))
    b.set(gx, y, gz, AIR)
    # the top platform: the fight, a cache, and a beacon of crystal
    ta, ty = plats[-1]
    tx, tz = C + math.cos(ta) * 10, C + math.sin(ta) * 10
    b.chest(round(tx), ty + 1, round(tz), 'chests/abyss_cache', facing='north')
    for k in range(5):
        b.set(C, G + 62 + k, C, LUMEN if k % 2 == 0 else RIFT_GLASS)
    b.lectern_book(C - 9, G + 1, C + 6, 'east', 'Tether Log', [
        'TETHER SPIRE\n\nWe chained the platforms to the needle and set draughts between them. Stand on a vent and it '
        'carries you up; crouch to sink.',
        'The pool round the foot of the spire will catch a fall from the lower platforms. Not from the top.\n\nThe mites '
        'here hunt on the wing. Keep your back to the needle.'], author='Survey Office')
    sp = [(round(tx + math.cos(k * 2.1) * 2), ty + 1, round(tz + math.sin(k * 2.1) * 2)) for k in range(3)]
    fl = [(round(tx + math.cos(k * 1.6) * 7), ty + 5, round(tz + math.sin(k * 1.6) * 7)) for k in range(4)]
    b.zone('tether', 'The Tether Spire', (round(tx) - 9, ty - 2, round(tz) - 9, round(tx) + 9, ty + 12, round(tz) + 9), sp, 'abyss_tether',
           kind='ambush', waves=2, flyers_at=fl, reward='sigil_shard',
           trigger=(round(tx) - 4, ty, round(tz) - 4, round(tx) + 4, ty + 4, round(tz) + 4))
    overgrow(b, 0.05)
    b.meta.update({'kind': 'abyss_place', 'title': 'The Tether Spire', 'ground': G})
    return b


# ------------------------------------------------------------------------------------------------- the Hollow Crown
def hollow_crown():
    W = L = 97
    C, G = 48, 6
    R = 40
    b = Build('abyss_hollow_crown', W, G + 34, L, seed=205)

    def floor(x, y, z):
        d = math.hypot(x - C, z - C)
        a = math.atan2(z - C, x - C)
        if abs(d - 17) < 0.7 or abs(d - 29) < 0.7:
            return CHISELED
        if d < 6:
            return 'minecraft:obsidian' if d > 5 else ('minecraft:crying_obsidian' if h(x, 0, z, 30) < 0.3 else 'minecraft:obsidian')
        if abs((a * 6 / math.pi) % 2 - 1) < 0.06 and d < R - 2:
            return CHISELED
        r = h(x, y, z, 31)
        return STARMOSS if r < 0.12 else SHALE if r < 0.3 else ASTRAL
    disc(b, C, C, R + 1, G, floor, depth=6)
    clear_above(b, C, C, R + 6, G + 1, G + 33)
    # the low rim: knee-high, broken in places so the arena is never a closed box
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            a = math.atan2(z - C, x - C)
            if R - 0.5 <= d <= R + 1 and h(int(a * 14), 0, 0, 32) > 0.15:
                b.set(x, G + 1, z, stone(x, G + 1, z, 33))
                if h(x, 1, z, 34) < 0.4:
                    b.set(x, G + 2, z, 'minecraft:deepslate_brick_wall')
    # six obelisks at 30 degrees off every 60 (the Leviathan's passes run between them): cover from the beam
    for k in range(6):
        a = math.radians(30 + 60 * k)
        ox, oz = round(C + math.cos(a) * 17), round(C + math.sin(a) * 17)
        for y in range(G + 1, G + 12):
            r = 1.6 if y < G + 8 else 1.0
            for x in range(ox - 2, ox + 3):
                for z in range(oz - 2, oz + 3):
                    if max(abs(x - ox), abs(z - oz)) <= r:
                        b.set(x, y, z, CHISELED if y in (G + 1, G + 8) else stone(x, y, z, 35))
        b.set(ox, G + 12, oz, LUMEN)
        b.set(ox, G + 13, oz, B('end_rod', facing='up'))
    # the crown: broken spires outside the rim, leaning out
    for k in range(18):
        a = k * math.tau / 18 + 0.1
        if k in (4, 13):
            continue
        hgt = 10 + int(h(k, 0, 0, 36) * 16)
        base_r = R + 3.5
        for y in range(0, hgt):
            lean = y * 0.12
            r = 1.8 * (1 - y / hgt) + 0.5
            sx, sz = C + math.cos(a) * (base_r + lean), C + math.sin(a) * (base_r + lean)
            for x in range(int(sx - r) - 1, int(sx + r) + 2):
                for z in range(int(sz - r) - 1, int(sz + r) + 2):
                    if math.hypot(x - sx, z - sz) <= r and 0 <= x < W and 0 <= z < L:
                        b.set(x, G + y - 2, z, stone(x, y, z, 37) if y < hgt - 1 else LUMEN)
    # the Eclipse Altar, at the north edge on a stepped dais
    az = C - 34
    for k, r in enumerate((4.5, 3.5, 2.5)):
        disc(b, C, az, r, G + k, CHISELED if k == 2 else ASTRAL)
    b.set(C, G + 3, az, ALTAR)
    b.point('altar', C, G + 3, az)
    for x in (C - 3, C + 3):
        for y in range(G + 1, G + 6):
            b.set(x, y, az - 2, 'minecraft:polished_deepslate' if y < G + 5 else LUMEN)
    b.lectern_book(C + 5, G + 1, az + 2, 'south', 'The Hollow Crown', [
        'THE HOLLOW CROWN\n\nSet the Eclipse Sigil in the altar and the Leviathan rises from the dark below.\n\n'
        'The obelisks stop its beam. Its passes run between them.',
        'Its wells pull you in, never out: walk out of the ring before it closes.\n\nWhen it crashes down in fire, '
        'its core lies open. Strike it then.',
        'If everyone leaves the Crown, it sinks again, and the altar keeps the sigil: the next call costs nothing.'],
        author='Aurel Danth')
    b.point('centre', C, G + 1, C)
    overgrow(b, 0.03)
    b.meta.update({'kind': 'hollow_crown', 'title': 'The Hollow Crown', 'ground': G})
    return b


if __name__ == '__main__':
    for f in (landing, starwell, archive, tether_spire, hollow_crown):
        f().save()
