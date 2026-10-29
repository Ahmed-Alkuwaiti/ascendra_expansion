"""The Rift Observatory: an ancient observatory and containment fortress, split by the cosmic rift it was built to watch.

An octagonal containment wall encloses a courtyard torn diagonally by a fissure. In the middle stands the Containment
Well, a roofless rotunda over the rift engine: the rift itself hangs above it, a jagged tear of glass and light, ringed by
three broken containment rings that float with nothing holding them. The Lens Tower rises at the back with the shattered
observing dome and its great telescope still aimed at the tear; a broken bridge joins it to the Well's upper gallery.
West is the Orrery Hall (a ring fragment came down through its roof), east the Archive, south the Gatehouse. Under the
courtyard run the Coolant Vaults, overgrown with void cysts; the fissure breaks into them.

The engine needs three components, each won in a different fight:
    the Gatehouse      ambush in the gate passage (optional)
    the Orrery Hall    waves around the orrery, with flyers   -> Star Chart
    the Coolant Vaults brood: smash the cysts or they hatch    -> Coolant Heart
    the Lens Dome      the Astronomer's Warden; sealed until the Hall and the Vaults are cleared -> Focusing Lens
Restoring the engine opens the gate to the Astral Abyss for good and unseals the updraft lift up the Lens Tower.

Journals on lecterns tell what happened, in the order a visitor meets them.
"""
import math

from common import *
from kit import AIR, B, Build, h

U = 'unstable_frontiers:'
W = L = 81
H = 98
G = 13                 # courtyard floor row (the block you stand on)
C = 40
R_OUT = 36             # containment wall (octagon, flat sides on the axes)
R_WELL = 12            # the Containment Well's wall (outer radius ~12.9)
TX, TZ = C - 20, C - 22    # the Lens Tower
R_TOWER = 7
DOME_Y = G + 46        # dome floor row
R_DOME = 11
FRACTURE = math.radians(35)
DX, DZ = math.cos(FRACTURE), math.sin(FRACTURE)
VAULT_FLOOR = G - 12   # vault floor row

ASTRAL = U + 'astral_bricks'
CHISELED = U + 'chiseled_astral'
SHALE = U + 'astral_shale'
STARMOSS = U + 'starmoss'
LUMEN = U + 'lumen_crystal'
RIFT_GLASS = U + 'rift_glass'
TENDRIL = U + 'void_tendril'
CYST = U + 'void_cyst'
VENT = U + 'updraft_vent'
GATE = U + 'abyss_gate'
ENGINE = U + 'rift_engine'
COPPER = 'minecraft:oxidized_cut_copper'
COPPER_W = 'minecraft:weathered_cut_copper'
COPPER_B = 'minecraft:oxidized_copper'
END_ROD = B('end_rod', facing='up')
PURPLE_GLASS = 'minecraft:purple_stained_glass'
SHELF = 'minecraft:bookshelf'


# ---------------------------------------------------------------------------------------------------------- helpers
def st(x, z):
    """Position against the fracture: s = distance across the fracture plane, t = distance along it."""
    return -(x - C) * DZ + (z - C) * DX, (x - C) * DX + (z - C) * DZ


def fissure_width(t):
    return 2.0 + 1.2 * math.sin(t * 0.31) + 0.9 * h(int(t), 0, 0, 71)


def in_fissure(x, z, pad=0.0):
    s, t = st(x, z)
    return 13.5 < abs(t) < 40 and abs(s) < fissure_width(t) + pad


def rift_touch(x, y, z):
    """0..1: how strongly the rift has changed this spot (near the fracture plane and the tear)."""
    s, t = st(x, z)
    a = max(0.0, 1 - abs(s) / 9)
    b = max(0.0, 1 - math.hypot(x - C, z - C) / 16) if y > G + 6 else 0.0
    return max(a, b)


def masonry(x, y, z, salt=0):
    """The observatory's stone: deepslate bricks and tiles, cracked with age, turned to astral brick where the rift touched."""
    r = h(x, y, z, salt)
    if r < rift_touch(x, y, z) * 0.55:
        return CHISELED if r < 0.04 else ASTRAL
    if r > 0.86:
        return 'minecraft:cracked_deepslate_bricks'
    if r > 0.7:
        return 'minecraft:deepslate_tiles'
    return 'minecraft:deepslate_bricks'


def floor_tile(x, y, z):
    r = h(x, y, z, 5)
    if r < rift_touch(x, y, z) * 0.5:
        return STARMOSS if r < 0.2 else SHALE
    if r < 0.12:
        return 'minecraft:cracked_deepslate_tiles'
    if r < 0.5:
        return 'minecraft:polished_deepslate'
    return 'minecraft:deepslate_tiles'


def fill_stone(x, y, z):
    r = h(x, y, z, 9)
    return 'minecraft:tuff' if r < 0.18 else 'minecraft:deepslate'


def tangent_facing(x, z, cx, cz, clockwise=False):
    """The cardinal direction of travel around (cx, cz) at (x, z): a spiral stair's 'facing'."""
    a = math.atan2(z - cz, x - cx)
    tx, tz = -math.sin(a), math.cos(a)
    if clockwise:
        tx, tz = -tx, -tz
    if abs(tx) > abs(tz):
        return 'east' if tx > 0 else 'west'
    return 'south' if tz > 0 else 'north'


def spiral(b, cx, cz, r0, r1, y0, y1, a0, material, per_level):
    """A spiral stair from y0 to y1 between radii r0 and r1, starting at angle a0 (radians), climbing one block every
    per_level radians (counter-clockwise when seen from above, i.e. increasing angle). Headroom is cleared above it."""
    n = y1 - y0
    for x in range(int(cx - r1) - 1, int(cx + r1) + 2):
        for z in range(int(cz - r1) - 1, int(cz + r1) + 2):
            r = math.hypot(x - cx, z - cz)
            if not r0 <= r <= r1:
                continue
            a = math.atan2(z - cz, x - cx)
            k = int(((a - a0) % math.tau) / per_level)
            turn = int(math.tau / per_level)
            while k <= n:
                y = y0 + k
                b.set(x, y, z, stair(material, tangent_facing(x, z, cx, cz)))
                b.set(x, y - 1, z, 'minecraft:' + material + 's' if material.endswith('brick') else 'minecraft:' + material)
                for dy in range(1, 4):
                    if b.get(x, y + dy, z) is None or b.solid(x, y + dy, z):
                        b.set(x, y + dy, z, AIR)
                k += turn
    return a0 + n * per_level


# ---------------------------------------------------------------------------------------------------------- build
def build():
    b = Build('rift_observatory', W, H, L, seed=97)
    b.meta['gates'] = {}
    ground(b)
    vaults(b)
    fissure(b)
    outer_wall(b)
    gatehouse(b)
    well(b)
    hall(b)
    archive(b)
    lens_tower(b)
    bridge(b)
    rings(b)
    tear(b)
    growth(b)
    journals(b)
    zones(b)
    b.meta.update({'kind': 'rift_observatory', 'title': 'The Rift Observatory', 'ground': G})
    return b


def ground(b):
    """Solid ground under the whole courtyard (so the site never floats over a hillside), and the flagstone courtyard."""
    for x in range(W):
        for z in range(L):
            if not in_octagon(x, z, C, C, R_OUT):
                continue
            for y in range(0, G):
                b.set(x, y, z, fill_stone(x, y, z))
            b.set(x, G, z, floor_tile(x, G, z))
    # an inlaid star compass around the Well
    for i in range(8):
        a = i * math.pi / 4
        ln = 22 if i % 2 == 0 else 17
        for r in range(14, ln):
            x, z = C + math.cos(a) * r, C + math.sin(a) * r
            b.set(x, G, z, 'minecraft:chiseled_deepslate' if r % 4 else CHISELED)


def vaults(b):
    """The Coolant Vaults: a ring tunnel under the courtyard, four tank chambers on the diagonals, cysts everywhere."""
    f = VAULT_FLOOR
    air = []
    for x in range(W):
        for z in range(L):
            r = math.hypot(x - C, z - C)
            if 15.5 <= r <= 20.5:
                ceil = f + 6 + (1 if 17 < r < 19 else 0)
                for y in range(f + 1, ceil + 1):
                    air.append((x, y, z))
    b.meta['cysts'] = []
    for k in range(4):
        a = math.radians(45 + 90 * k)
        cx, cz = round(C + math.cos(a) * 26), round(C + math.sin(a) * 26)
        for x in range(cx - 4, cx + 5):
            for z in range(cz - 4, cz + 5):
                for y in range(f + 1, f + 8):
                    air.append((x, y, z))
        # the passage from the ring
        for r in range(19, 23):
            px, pz = C + math.cos(a) * r, C + math.sin(a) * r
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for y in range(f + 1, f + 5):
                        air.append((round(px) + dx, y, round(pz) + dz))
    for p in air:
        b.set(*p, AIR)
    # line every face of the carved space with vault masonry, the floor with tiles
    for (x, y, z) in air:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + dx, y + dy, z + dz)
            if b.get(*q) not in (None, AIR) and b.get(*q) in ('minecraft:deepslate', 'minecraft:tuff'):
                if dy == -1:
                    b.set(*q, 'minecraft:polished_deepslate' if h(*q, 3) < 0.6 else 'minecraft:deepslate_tiles')
                elif dy == 1:
                    b.set(*q, LUMEN if h(*q, 4) < 0.05 else 'minecraft:deepslate_tiles')
                else:
                    b.set(*q, 'minecraft:cracked_deepslate_bricks' if h(*q, 6) < 0.2 else 'minecraft:deepslate_bricks')
    # tanks, pipes and cysts in each chamber
    for k in range(4):
        a = math.radians(45 + 90 * k)
        cx, cz = round(C + math.cos(a) * 26), round(C + math.sin(a) * 26)
        for y in range(f + 1, f + 7):
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    edge = abs(dx) == 1 or abs(dz) == 1
                    b.set(cx + dx, y, cz + dz, ('minecraft:light_blue_stained_glass' if h(cx + dx, y, cz + dz, 8) > 0.25 else AIR) if edge
                          else ('minecraft:blue_ice' if y < f + 5 else 'minecraft:packed_ice'))
        b.box(cx - 1, f + 7, cz - 1, cx + 1, f + 7, cz + 1, COPPER)
        for dx, dz in ((-4, 0), (4, 0), (0, -4), (0, 4)):
            b.line((cx + dx * 0.25, f + 6, cz + dz * 0.25), (cx + dx, f + 6, cz + dz), COPPER_W)
        for i in range(7):
            ang = i * math.tau / 7 + k
            x, z = round(cx + math.cos(ang) * 3), round(cz + math.sin(ang) * 3)
            if b.get(x, f + 1, z) == AIR and b.get(x, f, z) not in (None, AIR):
                b.set(x, f + 1, z, CYST)
                b.meta['cysts'].append([x, f + 1, z])
        b.chest(cx + 3, f + 1, cz + 3, 'chests/observatory_workshop' if k % 2 else 'chests/abyss_cache', facing='north')
    # cysts along the ring
    for i in range(16):
        ang = i * math.tau / 16 + 0.2
        r = 16.5 if i % 2 else 19.5
        x, z = round(C + math.cos(ang) * r), round(C + math.sin(ang) * r)
        if b.get(x, f + 1, z) == AIR:
            b.set(x, f + 1, z, CYST)
            b.meta['cysts'].append([x, f + 1, z])
    # frost on the floor near the tanks, lumen on the walls
    for (x, y, z) in air:
        if y == f + 1 and b.get(x, y, z) == AIR and h(x, y, z, 12) < 0.04:
            b.set(x, y, z, B('snow', layers=1))
    # the stair down from the Well floor (south side), x C-1..C+1, descending toward +z
    for k in range(1, 12):
        z = C + 4 + k
        y = G - k
        for x in range(C - 1, C + 2):
            b.set(x, y, z, stair('deepslate_brick', 'north'))
            b.set(x, y - 1, z, 'minecraft:deepslate_bricks')
            for dy in range(1, 5):
                if y + dy <= G:
                    b.set(x, y + dy, z, AIR)
        for x in (C - 2, C + 2):
            for dy in range(0, 5):
                if y + dy <= G - 1:
                    b.set(x, y + dy, z, 'minecraft:deepslate_bricks')
        if k >= 4:
            for x in range(C - 1, C + 2):
                b.set(x, y + 5, z, 'minecraft:deepslate_tiles' if y + 5 < G else b.get(x, G, z) and floor_tile(x, G, z))
    for x in range(C - 1, C + 2):   # rail around the opening in the Well floor
        pass


def fissure(b):
    """The fracture across the courtyard: a chasm down to the vaults, lined with rift-changed stone and crystal."""
    for x in range(W):
        for z in range(L):
            s, t = st(x, z)
            if not 13.5 < abs(t) < 40 or not in_octagon(x, z, C, C, R_OUT + 1):
                continue
            w = fissure_width(t)
            if abs(s) < w:
                for y in range(VAULT_FLOOR + 1, G + 1):
                    b.set(x, y, z, AIR)
                b.set(x, VAULT_FLOOR, z, SHALE if h(x, 0, z, 2) < 0.7 else LUMEN)
                if h(x, 1, z, 3) < 0.12:
                    b.set(x, VAULT_FLOOR + 1, z, B('amethyst_cluster', facing='up', waterlogged='false'))
            elif abs(s) < w + 1.2:
                for y in range(VAULT_FLOOR, G + 1):
                    if b.get(x, y, z) not in (AIR,):
                        b.set(x, y, z, LUMEN if h(x, y, z, 4) < 0.05 else SHALE if h(x, y, z, 7) < 0.75 else 'minecraft:obsidian')
            elif abs(s) < w + 4 and h(x, G, z, 9) < 0.6:
                b.set(x, G, z, STARMOSS if h(x, G, z, 10) < 0.6 else SHALE)


def outer_wall(b):
    """The containment wall: an octagon of thick masonry with a wall walk, collapsed where the fissure crosses it."""
    for x in range(W):
        for z in range(L):
            if not (in_octagon(x, z, C, C, R_OUT) and not in_octagon(x, z, C, C, R_OUT - 2)):
                continue
            if in_fissure(x, z, 1.5):
                continue
            ang = math.atan2(z - C, x - C)
            top = G + 8
            slump = h(int(ang * 6), 0, 0, 31)
            if slump < 0.22:
                top = G + 2 + int(slump * 18)
            for y in range(G + 1, top + 1):
                b.set(x, y, z, masonry(x, y, z, 1))
            if top == G + 8:
                if (x + z) % 2 == 0 and not in_octagon(x, z, C, C, R_OUT - 1):
                    b.set(x, G + 9, z, masonry(x, G + 9, z, 2))
            else:
                for dx in range(-1, 2):   # rubble at the foot of a collapse
                    if h(x + dx, 0, z, 33) < 0.3:
                        b.set(x + dx, G + 1, z, 'minecraft:cobbled_deepslate', over=False)
    # four bastions on the diagonals
    for k in range(4):
        a = math.radians(45 + 90 * k)
        bx, bz = round(C + math.cos(a) * (R_OUT - 2) * 1.05), round(C + math.sin(a) * (R_OUT - 2) * 1.05)
        if math.hypot(bx - TX, bz - TZ) < 14:
            continue
        b.cylinder(bx, bz, 4, G + 1, G + 13, lambda x, y, z: masonry(x, y, z, 3), hollow=1.4)
        b.cylinder(bx, bz, 2.6, G + 1, G + 12, AIR)
        b.cylinder(bx, bz, 3.0, G + 9, G + 9, lambda x, y, z: masonry(x, y, z, 4))
        for i in range(8):
            q = i * math.pi / 4
            b.set(bx + round(math.cos(q) * 4), G + 14, bz + round(math.sin(q) * 4), masonry(bx, G + 14, bz, 5))
        b.set(bx, G + 10, bz, LUMEN)


def gatehouse(b):
    """The south gate: two drum towers and a vaulted passage with a broken portcullis."""
    z0, z1 = C + R_OUT - 3, C + R_OUT
    for sx in (-6, 6):
        b.cylinder(C + sx, C + R_OUT - 1, 3.4, G + 1, G + 15, lambda x, y, z: masonry(x, y, z, 7), hollow=1.2)
        b.cylinder(C + sx, C + R_OUT - 1, 2.2, G + 1, G + 14, AIR)
        b.cylinder(C + sx, C + R_OUT - 1, 2.4, G + 10, G + 10, 'minecraft:polished_deepslate')
        b.set(C + sx, G + 16, C + R_OUT - 1, 'minecraft:deepslate_brick_wall')
        b.set(C + sx, G + 9, C + R_OUT - 1, B('soul_lantern', hanging='true', waterlogged='false'))
    b.box(C - 3, G + 1, z0, C + 3, G + 9, z1, lambda x, y, z: masonry(x, y, z, 8))
    for z in range(z0, z1 + 1):
        for x in range(C - 2, C + 3):
            arch = G + 6 if abs(x - C) < 2 else G + 5
            for y in range(G + 1, arch + 1):
                b.set(x, y, z, AIR)
    for x in range(C - 2, C + 3):   # the portcullis, bent and half gone
        for y in range(G + 3, G + 7):
            if h(x, y, 0, 41) < 0.55:
                b.set(x, y, z0 + 1, 'minecraft:iron_bars')
    b.set(C, G + 7, z0 - 1, B('soul_lantern', hanging='true', waterlogged='false'))


def well(b):
    """The Containment Well: a roofless rotunda over the rift engine, two inner galleries, containment pylons."""
    top = {}
    for x in range(C - 14, C + 15):
        for z in range(C - 14, C + 15):
            r = math.hypot(x - C, z - C)
            ang = math.atan2(z - C, x - C)
            if 11 <= r <= 12.9:
                s, t = st(x, z)
                hgt = G + 19 + int(5 * h(int((ang + 4) * 5), 0, 0, 51))
                for y in range(G + 1, hgt + 1):
                    if abs(s) < 3.2 and t > 0:
                        continue                                        # the breach the fissure tore (exposed side)
                    if abs(s) < 2.6 and t < 0 and y < G + 7:
                        continue                                        # a lower breach on the far side
                    b.set(x, y, z, masonry(x, y, z, 11))
                top[(x, z)] = hgt
            elif r < 11:
                b.set(x, G, z, floor_tile(x, G, z) if r > 6 else ('minecraft:polished_deepslate' if (x + z) % 2 else 'minecraft:deepslate_tiles'))
                for y in range(G + 1, G + 26):
                    b.set(x, y, z, AIR)
    # windows: tall slits all round
    for i in range(16):
        a = i * math.tau / 16
        for r in (11, 12):
            x, z = round(C + math.cos(a) * r), round(C + math.sin(a) * r)
            for y in (G + 12, G + 13, G + 14):
                if b.get(x, y, z) not in (None, AIR):
                    b.set(x, y, z, AIR)
    # buttresses (one, standing in the fissure, has broken and hangs from the wall)
    for k in (1, 3, 7):
        a = math.radians(45 * k)
        pts = [(C + math.cos(a) * 21, G, C + math.sin(a) * 21), (C + math.cos(a) * 18, G + 10, C + math.sin(a) * 18),
               (C + math.cos(a) * 13.5, G + 18, C + math.sin(a) * 13.5)]
        for i in range(60):
            t = i / 59
            p = [pts[0][j] + (pts[2][j] - pts[0][j]) * t for j in range(3)]
            p[1] = G + 18 * math.sin(t * math.pi / 2)
            if in_fissure(p[0], p[2], 1.0) and p[1] < G + 10:
                continue
            b.ellipsoid(p[0], p[1], p[2], 1.3, 1.3, 1.3, lambda x, y, z: masonry(x, y, z, 12))
        if not in_fissure(pts[0][0], pts[0][2], 1.0):
            b.box(round(pts[0][0]) - 1, G + 1, round(pts[0][2]) - 1, round(pts[0][0]) + 1, G + 5, round(pts[0][2]) + 1,
                  lambda x, y, z: masonry(x, y, z, 13))
    # doors: west (to the hall), east (to the archive), south (main), north is the rift gate's wall
    for (dx, dz) in ((-1, 0), (1, 0), (0, 1)):
        for d in range(10, 14):
            for w in (-1, 0, 1):
                x, z = C + dx * d + (w if dz else 0), C + dz * d + (w if dx else 0)
                for y in range(G + 1, G + 5):
                    b.set(x, y, z, AIR)
    # the dais, the engine, the gate
    b.cylinder(C, C, 3.6, G + 1, G + 1, CHISELED)
    b.cylinder(C, C, 2.6, G + 1, G + 1, 'minecraft:polished_deepslate')
    b.set(C, G + 2, C, ENGINE)
    b.point('engine', C, G + 2, C)
    gz = C - 5
    b.box(C - 2, G + 1, gz, C + 2, G + 6, gz, CHISELED)
    for x in range(C - 1, C + 2):
        for y in range(G + 2, G + 6):
            b.set(x, y, gz, GATE)
    b.box(C - 3, G + 1, gz - 1, C + 3, G + 7, gz - 1, lambda x, y, z: masonry(x, y, z, 14))
    for x in (C - 3, C + 3):
        b.set(x, G + 7, gz, B('chain', axis='y', waterlogged='false'))
        b.set(x, G + 8, gz, LUMEN)
    b.point('gate', C, G + 2, gz + 1)
    # containment pylons with chains up toward the tear
    for k in range(4):
        a = math.radians(45 + 90 * k)
        px, pz = round(C + math.cos(a) * 7), round(C + math.sin(a) * 7)
        for y in range(G + 1, G + 9):
            b.set(px, y, pz, COPPER if y % 3 else 'minecraft:chiseled_copper' if h(px, y, pz) < 0.5 else COPPER_B)
        b.set(px, G + 9, pz, B('lightning_rod', facing='up', powered='false', waterlogged='false'))
        b.line((px, G + 10, pz), (C + (px - C) * 0.35, G + 15, C + (pz - C) * 0.35), B('chain', axis='y', waterlogged='false'))
    # the two inner galleries (G+10 all round, G+18 on the far side) and the stairs that reach them
    for x in range(C - 11, C + 12):
        for z in range(C - 11, C + 12):
            r = math.hypot(x - C, z - C)
            ang = math.degrees(math.atan2(z - C, x - C)) % 360
            if 8.6 <= r < 11:
                s, t = st(x, z)
                if abs(s) < 3.2 and t > 0:
                    continue
                b.set(x, G + 10, z, slab('deepslate_tile', 'top'))
                if r < 9.4:
                    b.set(x, G + 11, z, 'minecraft:iron_bars')
                if 150 <= ang <= 300 and h(x, 0, z, 61) > 0.12:
                    b.set(x, G + 18, z, slab('polished_deepslate', 'top'))
                    if r < 9.4:
                        b.set(x, G + 19, z, 'minecraft:iron_bars')
    spiral(b, C, C, 9.0, 10.9, G + 1, G + 10, math.radians(20), 'deepslate_brick', math.radians(5.6))
    spiral(b, C, C, 9.0, 10.9, G + 11, G + 18, math.radians(195), 'deepslate_brick', math.radians(5.6))
    # the gap the vault stair needs through the Well floor, with a rail
    for z in range(C + 5, C + 11):
        for x in (C - 2, C + 2):
            b.set(x, G + 1, z, 'minecraft:deepslate_brick_wall')
    # light
    for i in range(8):
        a = i * math.tau / 8 + 0.2
        b.set(round(C + math.cos(a) * 10.4), G + 9, round(C + math.sin(a) * 10.4), B('soul_lantern', hanging='true', waterlogged='false'))


def hall(b):
    """The Orrery Hall (west): a long vaulted hall around a hanging model of the heavens. A ring fragment broke the roof."""
    x0, x1, z0, z1 = C - 37, C - 15, C - 9, C + 9
    top = G + 15
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            wall = x in (x0, x1) or z in (z0, z1)
            gable = top + max(0, 5 - abs(z - C) // 2)
            for y in range(G + 1, gable + 1):
                if wall and y <= top:
                    b.set(x, y, z, masonry(x, y, z, 21))
                elif y > top:
                    b.set(x, y, z, masonry(x, y, z, 22) if y == gable or wall else AIR)
                else:
                    b.set(x, y, z, AIR)
            b.set(x, G, z, floor_tile(x, G, z) if not wall else masonry(x, G, z, 23))
    # pillars and windows
    for x in range(x0 + 3, x1, 4):
        for z in (z0, z1):
            for y in range(G + 1, top + 1):
                b.set(x, y, z + (1 if z == z0 else -1), 'minecraft:polished_deepslate' if y % 5 else CHISELED)
        for z in (z0, z1):
            for y in range(G + 9, G + 13):
                b.set(x + 2, y, z, AIR if y < G + 12 else 'minecraft:deepslate_tile_slab')
    # the mezzanine
    for x in range(x0 + 1, x1):
        for z in range(z0 + 1, z1):
            if x - x0 <= 2 or x1 - x <= 2 or z - z0 <= 2 or z1 - z <= 2:
                b.set(x, G + 7, z, slab('deepslate_tile', 'top'))
                inner = (x - x0 == 3 or x1 - x == 3 or z - z0 == 3 or z1 - z == 3) and x0 + 3 <= x <= x1 - 3 and z0 + 3 <= z <= z1 - 3
                if inner:
                    b.set(x, G + 8, z, 'minecraft:iron_bars')
    for i, (sx, sz, f) in enumerate(((x0 + 1, z0 + 3, 'south'), (x1 - 1, z1 - 3, 'north'))):
        for k in range(7):
            z = sz + (k if f == 'south' else -k)
            for dx in (0, 1 if sx == x0 + 1 else -1):
                b.set(sx + dx, G + 1 + k, z, stair('deepslate_brick', f))
                for y in range(G + 2 + k, G + 5 + k):
                    if y != G + 7 or k == 6:
                        b.set(sx + dx, y, z, AIR)
            if k < 6:
                for dx in (0, 1 if sx == x0 + 1 else -1):
                    b.set(sx + dx, G + 7, z, AIR)
    # doors: east into the Well's corridor, north and south to the courtyard
    for z in range(C - 1, C + 2):
        for x in range(x1 - 1, C - 10):
            for y in range(G + 1, G + 5):
                b.set(x, y, z, AIR)
            b.set(x, G, z, 'minecraft:polished_deepslate')
            if x > x1:
                b.set(x, G + 5, z, masonry(x, G + 5, z, 24))
                for zz in (C - 2, C + 2):
                    for y in range(G + 1, G + 5):
                        b.set(x, y, zz, masonry(x, y, zz, 25))
    for z in (z0, z1):
        for x in range(C - 27, C - 24):
            for y in range(G + 1, G + 5):
                b.set(x, y, z, AIR)
    # the orrery: a sun, rings on chains, planets on rods
    ox, oz, oy = C - 26, C, G + 10
    b.ellipsoid(ox, oy, oz, 1.6, 1.6, 1.6, 'minecraft:shroomlight')
    b.chain(ox, oy + 2, top, oz)
    planets = ['minecraft:amethyst_block', 'minecraft:copper_block', 'minecraft:prismarine', 'minecraft:obsidian', LUMEN]
    for i, (rr, tilt) in enumerate(((3.5, 0.15), (5.5, -0.25), (7.5, 0.35))):
        n = int(rr * 7)
        for j in range(n):
            a = j * math.tau / n
            x, z = ox + math.cos(a) * rr, oz + math.sin(a) * rr
            y = oy + math.sin(a) * rr * tilt
            if h(j, i, 0, 81) > 0.12:
                b.set(x, y, z, COPPER_W if j % 3 else 'minecraft:chain')
        pa = i * 2.1 + 0.6
        px, pz, py = ox + math.cos(pa) * rr, oz + math.sin(pa) * rr, oy + math.sin(pa) * rr * tilt
        b.ellipsoid(px, py, pz, 0.9, 0.9, 0.9, planets[i])
        b.chain(round(px), round(py) + 1, top, round(pz))
    # the ring fragment that came through the roof, and the hole it left
    for x in range(C - 33, C - 26):
        for z in range(C - 9, C - 2):
            for y in range(top - 1, top + 6):
                if h(x, y, z, 82) < 0.85:
                    b.set(x, y, z, AIR)
    b.curve([(C - 30, top + 9, C - 7), (C - 31, top + 2, C - 5), (C - 33, G + 4, C - 3), (C - 34, G + 1, C + 1)], CHISELED,
            radius=lambda t: 1.1)
    for y in range(G + 1, G + 3):
        for x in range(C - 36, C - 31):
            for z in range(C - 5, C + 3):
                if h(x, y, z, 83) < 0.35:
                    b.set(x, y, z, 'minecraft:cobbled_deepslate', over=False)
    # the workshop alcove and the chart table
    b.chest(x0 + 2, G + 8, z1 - 2, 'chests/observatory_workshop', facing='west')
    b.set(x0 + 2, G + 8, z1 - 3, 'minecraft:smithing_table')
    b.set(C - 26, G + 1, C + 6, 'minecraft:cartography_table')
    b.set(C - 25, G + 1, C + 6, 'minecraft:cartography_table')
    for x, z in ((x0 + 4, z0 + 4), (x1 - 4, z0 + 4), (x0 + 4, z1 - 4), (x1 - 4, z1 - 4)):
        b.set(x, top - 1, z, B('soul_lantern', hanging='true', waterlogged='false'))


def archive(b):
    """The Archive (east): two floors of shelves, the lectern with the survey of the far side, and the astrolabe's chest."""
    x0, x1, z0, z1 = C + 15, C + 30, C - 7, C + 7
    top = G + 13
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            wall = x in (x0, x1) or z in (z0, z1)
            for y in range(G + 1, top + 1):
                b.set(x, y, z, masonry(x, y, z, 31) if wall or y == top else AIR)
            b.set(x, G, z, 'minecraft:dark_oak_planks' if not wall else masonry(x, G, z, 32))
            if not wall and not (x1 - 5 <= x <= x1 - 1 and z0 + 1 <= z <= z0 + 3):
                b.set(x, G + 7, z, 'minecraft:dark_oak_planks')
    # a corner collapse lets the sky in
    for x in range(x1 - 5, x1 + 1):
        for z in range(z1 - 5, z1 + 1):
            for y in range(G + 9, top + 1):
                if h(x, y, z, 33) < 0.8 or x + z > x1 + z1 - 4:
                    b.set(x, y, z, AIR)
    for x in range(x0 + 1, x1):
        for z in (z0 + 1, z1 - 1):
            for y in (G + 1, G + 2, G + 3, G + 8, G + 9):
                if (x - x0) % 5 and h(x, y, z, 34) > 0.15:
                    b.set(x, y, z, SHELF)
    for k in range(5):   # stair up in the north-east corner
        b.set(x1 - 1 - k, G + 1 + k, z0 + 2, stair('dark_oak', 'west'))
        b.set(x1 - 1 - k, G + 1 + k, z0 + 3, stair('dark_oak', 'west'))
    for k in range(5, 7):
        b.set(x1 - 1 - k, G + 1 + k, z0 + 2, stair('dark_oak', 'west'))
        b.set(x1 - 1 - k, G + 1 + k, z0 + 3, stair('dark_oak', 'west'))
        for x in range(x1 - 1 - k, x1):
            for z in (z0 + 2, z0 + 3):
                if b.get(x, G + 7, z) == 'minecraft:dark_oak_planks':
                    b.set(x, G + 7, z, AIR)
    for z in range(C - 1, C + 2):   # door west, toward the Well
        for x in range(C + 12, x0 + 1):
            for y in range(G + 1, G + 5):
                b.set(x, y, z, AIR)
            b.set(x, G, z, 'minecraft:polished_deepslate')
    b.chest(x1 - 2, G + 8, C, 'chests/observatory_archive', facing='west')
    b.set(x1 - 2, G + 8, C + 1, 'minecraft:cartography_table')
    b.set(x0 + 4, G + 1, C, B('lectern', facing='west', has_book='false', powered='false'))
    for x, z in ((x0 + 4, z0 + 3), (x1 - 4, z1 - 3), (x0 + 4, z1 - 3)):
        b.set(x, G + 6, z, B('lantern', hanging='true', waterlogged='false'))
        b.set(x, G + 12, z, B('lantern', hanging='true', waterlogged='false'))


def lens_tower(b):
    """The Lens Tower and its broken dome; the great telescope; the lift shaft (sealed until the engine wakes)."""
    for x in range(TX - R_DOME - 2, TX + R_DOME + 3):
        for z in range(TZ - R_DOME - 2, TZ + R_DOME + 3):
            r = math.hypot(x - TX, z - TZ)
            if r <= R_TOWER + 0.9:
                for y in range(0, G + 1):
                    b.set(x, y, z, fill_stone(x, y, z))
                b.set(x, G, z, 'minecraft:polished_deepslate' if r < R_TOWER - 1 else masonry(x, G, z, 41))
                for y in range(G + 1, DOME_Y):
                    if r >= R_TOWER - 1:
                        b.set(x, y, z, masonry(x, y, z, 42))
                    else:
                        b.set(x, y, z, AIR)
    # the spiral stair: along the wall, arriving at the bridge door (G+18) and the dome floor
    toward = math.atan2(C - TZ, C - TX)
    per = math.radians(10.5)
    a0 = toward - 17 * per
    spiral(b, TX, TZ, 3.6, 5.95, G + 1, DOME_Y, a0, 'deepslate_brick', per)
    # ground door (facing the Well), bridge door (G+18), and a doorway where the ring passes (G+32)
    for (y0, y1) in ((G + 1, G + 4), (G + 18, G + 21), (G + 32, G + 35)):
        for d in range(5, 9):
            for w in (-1, 0, 1):
                x = round(TX + math.cos(toward) * d - math.sin(toward) * w * 0.8)
                z = round(TZ + math.sin(toward) * d + math.cos(toward) * w * 0.8)
                for y in range(y0, y1 + 1):
                    b.set(x, y, z, AIR)
    # arrow slits
    for i in range(12):
        a = i * math.tau / 12
        for y in range(G + 6, DOME_Y - 2, 9):
            x, z = round(TX + math.cos(a) * (R_TOWER - 0.5)), round(TZ + math.sin(a) * (R_TOWER - 0.5))
            b.set(x, y, z, AIR)
            b.set(x, y + 1, z, AIR)
    # the dome: floor on corbels, a half-shattered shell open toward the rift
    for x in range(TX - R_DOME - 1, TX + R_DOME + 2):
        for z in range(TZ - R_DOME - 1, TZ + R_DOME + 2):
            r = math.hypot(x - TX, z - TZ)
            if r <= R_DOME:
                b.set(x, DOME_Y, z, 'minecraft:polished_deepslate' if r < R_DOME - 1 else CHISELED)
                if R_TOWER - 1 < r:
                    depth = int((r - R_TOWER + 1) * 0.9)
                    for y in range(DOME_Y - depth, DOME_Y):
                        b.set(x, y, z, masonry(x, y, z, 43))
    facing = (math.cos(toward), math.sin(toward))
    for x in range(TX - R_DOME - 1, TX + R_DOME + 2):
        for z in range(TZ - R_DOME - 1, TZ + R_DOME + 2):
            for y in range(DOME_Y + 1, DOME_Y + R_DOME + 2):
                d = math.sqrt((x - TX) ** 2 + (z - TZ) ** 2 + ((y - DOME_Y) * 1.0) ** 2)
                if R_DOME - 1.0 <= d <= R_DOME:
                    nx, nz = (x - TX) / max(1, d), (z - TZ) / max(1, d)
                    broken = nx * facing[0] + nz * facing[1] > 0.35 - 0.3 * h(x, y, z, 44) and y > DOME_Y + 3
                    if broken or h(x, y, z, 45) < 0.06:
                        continue
                    rib = abs(math.atan2(z - TZ, x - TX) % (math.pi / 4)) < 0.12
                    b.set(x, y, z, COPPER_B if rib else (ASTRAL if y > DOME_Y + 7 else masonry(x, y, z, 46)))
                elif d < R_DOME - 1.0 and y > DOME_Y:
                    b.set(x, y, z, AIR)
    # the last turns of the stair come up through the dome floor
    spiral(b, TX, TZ, 3.6, 5.95, DOME_Y - 3, DOME_Y, a0 + (DOME_Y - 3 - (G + 1)) * per, 'deepslate_brick', per)
    # the telescope, aimed at the tear
    base = (TX, DOME_Y + 3, TZ)
    aim = (C - TX, (G + 50) - base[1], C - TZ)
    n = math.sqrt(sum(a * a for a in aim))
    aim = [a / n for a in aim]
    for i in range(0, 17):
        p = [base[j] + aim[j] * i for j in range(3)]
        rad = 1.2 + i * 0.07
        b.ellipsoid(p[0], p[1], p[2], rad, rad, rad, COPPER_W if i % 4 else 'minecraft:copper_block')
    for i in range(1, 16):
        p = [base[j] + aim[j] * i for j in range(3)]
        b.set(p[0], p[1], p[2], AIR)
    b.box(TX - 1, DOME_Y + 1, TZ - 1, TX + 1, DOME_Y + 2, TZ + 1, 'minecraft:polished_deepslate')
    b.set(TX, DOME_Y + 2, TZ, 'minecraft:lodestone')
    # instrument consoles: cover in the fight
    for k in range(4):
        a = toward + math.pi / 4 + k * math.pi / 2
        x, z = round(TX + math.cos(a) * 6.5), round(TZ + math.sin(a) * 6.5)
        b.box(x - 1, DOME_Y + 1, z, x + 1, DOME_Y + 2, z, COPPER if k % 2 else 'minecraft:polished_deepslate')
        b.set(x, DOME_Y + 3, z, B('lightning_rod', facing='up', powered='false', waterlogged='false'))
    b.chest(round(TX - math.cos(toward) * 8), DOME_Y + 1, round(TZ - math.sin(toward) * 8), 'chests/observatory_vault', facing='south')
    for k in range(6):
        a = k * math.tau / 6
        b.set(round(TX + math.cos(a) * 9), DOME_Y + 1, round(TZ + math.sin(a) * 9), B('lantern', hanging='false', waterlogged='false'))
    # the lift: a vent in the tower floor and one on a ledge half way, each sealed until the engine wakes
    # (the second vent sits on the side away from the telescope, so the shaft comes up clear of its stand)
    lx, lz = TX, TZ
    b.set(lx, G, lz, VENT)
    for y in range(G + 1, G + 24):
        b.set(lx, y, lz, AIR)
    b.box(lx - 2, G + 23, lz - 1, lx - 1, G + 23, lz + 1, 'minecraft:polished_deepslate')
    b.set(lx - 2, G + 23, lz, VENT)
    for y in range(G + 24, DOME_Y + 3):
        b.set(lx - 2, y, lz, AIR)
    b.set(lx - 2, G + 24, lz + 1, 'minecraft:iron_bars')
    b.set(lx - 2, G + 24, lz - 1, 'minecraft:iron_bars')
    seal = [[lx, G + 1, lz], [lx - 2, G + 24, lz], [lx - 2, DOME_Y, lz]]
    for p in seal:
        b.set(*p, CHISELED)
    b.meta['gates']['lift'] = seal
    b.point('lens_tower', TX, DOME_Y + 1, TZ)


def bridge(b):
    """The broken bridge from the Well's upper gallery to the Lens Tower's door (deck at G+17, a 2-block gap)."""
    toward = math.atan2(C - TZ, C - TX)
    a_start = (C + math.cos(toward + math.pi) * 11.5, C + math.sin(toward + math.pi) * 11.5)
    a_end = (TX + math.cos(toward) * 6.5, TZ + math.sin(toward) * 6.5)
    n = int(math.dist(a_start, a_end) * 3)
    for i in range(n + 1):
        t = i / n
        x = a_start[0] + (a_end[0] - a_start[0]) * t
        z = a_start[1] + (a_end[1] - a_start[1]) * t
        if 0.45 < t < 0.62:
            continue
        for w in (-1.2, -0.6, 0, 0.6, 1.2):
            px, pz = x - math.sin(toward) * w, z + math.cos(toward) * w
            b.set(px, G + 17, pz, masonry(px, G + 17, pz, 51))
            for y in range(G + 18, G + 21):
                if b.solid(round(px), y, round(pz)):
                    b.set(px, y, pz, AIR)
        for w in (-1.7, 1.7):
            px, pz = x - math.sin(toward) * w, z + math.cos(toward) * w
            b.set(px, G + 18, pz, 'minecraft:deepslate_brick_wall')
        b.set(x, G + 16, z, masonry(x, G + 16, z, 52))
    # the Well's door onto the bridge
    for d in range(10, 14):
        for w in (-1, 0, 1):
            x = round(C + math.cos(toward + math.pi) * d - math.sin(toward) * w * 0.8)
            z = round(C + math.sin(toward + math.pi) * d + math.cos(toward) * w * 0.8)
            for y in range(G + 18, G + 22):
                b.set(x, y, z, AIR)
    # rubble from the missing span, down on the courtyard
    mid = ((a_start[0] + a_end[0]) / 2, (a_start[1] + a_end[1]) / 2)
    for i in range(14):
        x, z = mid[0] + (h(i, 0, 0, 53) - 0.5) * 6, mid[1] + (h(i, 1, 0, 53) - 0.5) * 6
        b.set(x, G + 1, z, 'minecraft:cobbled_deepslate' if i % 3 else ASTRAL, over=False)


def ring_points(cx, cy, cz, r, tilt, axis_angle, step=0.35):
    ax, az = math.cos(axis_angle), math.sin(axis_angle)
    ct, stt = math.cos(tilt), math.sin(tilt)
    n = int(math.tau * r / step)
    for i in range(n):
        a = i * math.tau / n
        px, py, pz = math.cos(a) * r, 0.0, math.sin(a) * r
        # Rodrigues rotation about the horizontal axis (ax, 0, az)
        dot = px * ax + pz * az
        cxp = (0 * pz - az * py, az * px - ax * pz, ax * py - 0 * px)
        rx = px * ct + cxp[0] * stt + ax * dot * (1 - ct)
        ry = py * ct + cxp[1] * stt
        rz = pz * ct + cxp[2] * stt + az * dot * (1 - ct)
        yield a, cx + rx, cy + ry, cz + rz


def rings(b):
    """Three containment rings around the tear, floating, each broken in two places. The widest is a walkable band."""
    specs = [(21, G + 32, math.radians(6), 0.4, 3, 1), (15, G + 44, math.radians(28), 1.9, 1, 2), (10, G + 54, math.radians(52), 3.1, 1, 3)]
    for r, cy, tilt, axis, width, salt in specs:
        gaps = [h(salt, 0, 0, 91) * math.tau, h(salt, 1, 0, 91) * math.tau]
        for a, x, y, z in ring_points(C, cy, C, r, tilt, axis):
            if any(min(abs(a - g), math.tau - abs(a - g)) < 0.22 + 0.1 * salt for g in gaps):
                continue
            node = int(a / (math.tau / 12) + 0.5) % 2 == 0 and abs((a / (math.tau / 12)) % 1 - 0.5) > 0.46
            if width > 1:
                for dr in (-1, 0, 1):
                    q = (r + dr) / r
                    px, pz = C + (x - C) * q, C + (z - C) * q
                    b.set(px, y, pz, LUMEN if node and dr == 0 else (CHISELED if dr == 0 else ASTRAL))
                q = (r + 1.6) / r
                if int(a * 20) % 3 == 0:
                    b.set(C + (x - C) * q, y + 1, C + (z - C) * q, 'minecraft:deepslate_brick_wall')
            else:
                b.ellipsoid(x, y, z, 0.75, 0.75, 0.75, LUMEN if node else (COPPER if int(a * 6) % 2 else CHISELED))
        # fragments drifting off each break
        for g in gaps:
            for k in range(4):
                ga = g + (k - 1.5) * 0.08
                d = 1.5 + k * 1.3
                x, z = C + math.cos(ga) * (r + d), C + math.sin(ga) * (r + d)
                b.set(x, cy + (k - 1) * 1.5 + math.sin(ga) * r * math.sin(tilt) * 0.5, z, ASTRAL if k % 2 else CHISELED)
    # resident mites drift around the rings
    b.meta['residents'] = [{'roster': 'observatory_residents', 'flying': True, 'count': 3,
                            'spots': [[round(C + math.cos(a) * 18), G + 36, round(C + math.sin(a) * 18)] for a in (0.5, 2.6, 4.4)]}]


def tear(b):
    """The rift: a jagged vertical tear in the fracture plane above the engine, its glass edged with crying obsidian."""
    y0, y1 = G + 12, G + 82
    for y in range(y0, y1 + 1):
        f = (y - y0) / (y1 - y0)
        w = 6.0 * math.sin(math.pi * f) ** 0.6 * (0.8 + 0.4 * h(y, 0, 0, 101))
        lean = math.sin(f * 3.0) * 1.5
        for x in range(C - 10, C + 11):
            for z in range(C - 10, C + 11):
                s, t = st(x, z)
                t -= lean
                if abs(t) > w + 1 or abs(s) > 1.3:
                    continue
                core = abs(t) < w - 1.2 and abs(s) < 0.7
                edge = abs(t) <= w + 0.5
                if core:
                    r = h(x, y, z, 102)
                    b.set(x, y, z, RIFT_GLASS if r < 0.55 else PURPLE_GLASS if r < 0.85 else LUMEN)
                elif edge and abs(s) < 1.0:
                    b.set(x, y, z, 'minecraft:crying_obsidian' if h(x, y, z, 103) < 0.7 else 'minecraft:obsidian')
    # debris pulled into orbit around the tear
    for i in range(70):
        a = h(i, 0, 0, 104) * math.tau
        r = 6 + h(i, 1, 0, 104) * 14
        y = G + 22 + h(i, 2, 0, 104) * 50
        x, z = C + math.cos(a) * r, C + math.sin(a) * r
        if b.get(round(x), round(y), round(z)) in (None, AIR):
            b.set(x, y, z, [ASTRAL, SHALE, 'minecraft:cobbled_deepslate', 'minecraft:amethyst_block', PURPLE_GLASS][i % 5])
    for i in range(10):   # lights hanging under the tear
        a = i * math.tau / 10
        b.set(C + math.cos(a) * 3, G + 11, C + math.sin(a) * 3, END_ROD if i % 2 else LUMEN)


def growth(b):
    """Rift growth: tendrils under overhangs near the fracture, crystal on stone, starbloom in the moss."""
    cells = list(b.b.items())
    for (x, y, z), (name, _) in cells:
        if name in (AIR, 'minecraft:structure_void'):
            continue
        below = b.b.get((x, y - 1, z))
        above = b.b.get((x, y + 1, z))
        touch = rift_touch(x, y, z)
        if y > G and below is not None and below[0] == AIR and h(x, y, z, 111) < 0.015 + 0.3 * touch and b.solid(x, y, z):
            for k in range(1, 2 + int(h(x, y, z, 112) * 3)):
                if b.b.get((x, y - k, z), (None,))[0] != AIR:
                    break
                b.set(x, y - k, z, TENDRIL)
        if name == STARMOSS and (above is None or above[0] == AIR) and h(x, y, z, 113) < 0.15:
            b.set(x, y + 1, z, U + 'starbloom')
        if name in (SHALE, ASTRAL) and (above is None or above[0] == AIR) and h(x, y, z, 114) < 0.03 and y >= G:
            b.set(x, y + 1, z, B('amethyst_cluster', facing='up', waterlogged='false'))


def journals(b):
    """The story, told in the order a visitor finds it. Original text."""
    b.lectern_book(C + 3, G + 1, C + 28, 'south', 'Standing Orders', [
        'STANDING ORDERS OF THE LONG WATCH\n\nThis observatory keeps watch on the Hollow Star: the dark body that does not turn '
        'with the others.\n\nThe engine opens a window to it. It is opened only with all three parts in place and the '
        'Prefect\'s word.',
        'The gate is never left open.\n\nAnything that comes through the window is held in the Well until the wardens '
        'take it.\n\n- Prefect Aurel Danth'], author='Aurel Danth')
    b.lectern_book(C + 4, G + 1, C - 3, 'west', 'Engine Log', [
        'ENGINE LOG, LAST ENTRY\n\nThe window would not close. Something on the far side was holding it open from '
        'beneath.\n\nSo I took the engine apart.',
        'The FOCUSING LENS went back to the dome. The COOLANT HEART is in the vaults below, where the cold keeps it '
        'safe. The STAR CHART is in the Orrery Hall.\n\nWithout all three the engine is only stone. Put them back and '
        'it will open again.',
        'Whoever does: the gate does not close once it is open. I am sorry.\n\n- Sorrel Ike, engineer'], author='Sorrel Ike')
    b.lectern_book(C - 20, G + 1, C + 6, 'north', 'The Hollow Star', [
        'NOTES ON THE HOLLOW STAR\n\nThrough the window: islands, floating in starlight, with no ground below them. Our '
        'surveyors built on four of them before the fracture.',
        'The Starwell. The Drifting Archive. The Tether Spire. And the Hollow Crown, where the Star itself sits low.\n\n'
        'The orreries we built to keep the lantern-mites down have turned. Their rings still align before they fire.',
        'Something vast circles the Hollow Star and covers it, as the moon covers the sun.\n\nIt has an eye.\n\n- A.D.'],
                   author='Aurel Danth')
    b.lectern_book(C + 19, G + 1, C, 'west', 'Survey of the Far Side', [
        'SURVEY OF THE FAR SIDE\n\nArrival: a landing stage by the far gate. The gate leads straight back here.\n\n'
        'Each of our stations there holds a shard of the eclipse sigil, kept apart on purpose.',
        'Three shards and an eye of ender make the Sigil. The altar in the Hollow Crown takes it.\n\n'
        'Do not go to the altar unprepared.',
        'On falling: the rift remembers where you last stood. Fall far enough and it throws you back there, but it '
        'takes its due.\n\nThings dropped into the dark drift to the nearest station.\n\nOur astrolabes find the way: '
        'there is one in this archive.'], author='Survey Office')
    b.lectern_book(C + 22, VAULT_FLOOR + 1, C + 22, 'north', 'Coolant Maintenance', [
        'COOLANT MAINTENANCE\n\nThe cysts grow on anything cold. The mites hatch from them.\n\nBreak every cyst you see. '
        'If you leave them, they keep hatching.',
        'The Heart is in the main tank. We left it there.\n\n- maintenance crew'], author='Maintenance')
    toward = math.atan2(C - TZ, C - TX)
    b.lectern_book(round(TX - math.cos(toward) * 7), DOME_Y + 1, round(TZ - math.sin(toward) * 7) + 2, 'east', 'The Last Watch', [
        'THE LAST WATCH\n\nI aimed the great lens at the Star tonight. It looked back.\n\nThe Leviathan wears the eclipse '
        'like a crown.',
        'Our altar in the Hollow Crown can call it up. A Sigil, made from the three shards, wakes it. Kill it there, '
        'where the obelisks give some cover.\n\nIts beam burns along a line. Stand where the line is not.',
        'Its gravity wells pull you inward, never out. Its passes are marked in fire before it comes.\n\nIf it crashes '
        'down, it lies open. Strike then.\n\nI am taking the lens down. - A.D.'], author='Aurel Danth')


def zones(b):
    # the Gatehouse: an ambush in the gate passage
    gz = C + R_OUT
    b.zone('gatehouse', 'The Gatehouse', (C - 10, G + 1, gz - 12, C + 10, G + 12, gz), [
        (C - 6, G + 11, gz - 1), (C + 6, G + 11, gz - 1), (C - 4, G + 1, gz - 6), (C + 4, G + 1, gz - 6), (C, G + 1, gz - 9)],
        'observatory_residents', kind='ambush', waves=1, trigger=(C - 3, G + 1, gz - 4, C + 3, G + 7, gz),
        flyers_at=[(C - 5, G + 14, gz - 6), (C + 5, G + 14, gz - 6), (C, G + 16, gz - 10)])
    # the Orrery Hall: waves around the orrery, mites on the wing
    sp = [(C - 34, G + 1, C - 6), (C - 18, G + 1, C - 6), (C - 34, G + 1, C + 6), (C - 18, G + 1, C + 6), (C - 26, G + 1, C - 7),
          (C - 26, G + 8, C + 8), (C - 35, G + 8, C), (C - 17, G + 8, C)]
    b.zone('hall', 'The Orrery Hall', (C - 36, G + 1, C - 8, C - 16, G + 18, C + 8), sp, 'observatory_gallery', kind='waves',
           flyers_at=[(C - 30, G + 12, C - 4), (C - 22, G + 12, C + 4), (C - 26, G + 13, C)], reward='star_chart')
    # the Coolant Vaults: brood, hatching from the cysts
    vsp = []
    for k in range(8):
        a = k * math.tau / 8 + 0.4
        vsp.append((round(C + math.cos(a) * 18), VAULT_FLOOR + 1, round(C + math.sin(a) * 18)))
    b.zone('vaults', 'The Coolant Vaults', (C - 31, VAULT_FLOOR + 1, C - 31, C + 31, VAULT_FLOOR + 8, C + 31), vsp, 'observatory_vaults',
           kind='brood', brood='unstable_frontiers:void_cyst', brood_eggs=b.meta.pop('cysts'), reward='coolant_heart')
    # the Lens Dome: the Astronomer's Warden, sealed until the Hall and the Vaults are cleared
    dsp = [(TX + round(math.cos(a) * 4), DOME_Y + 1, TZ + round(math.sin(a) * 4)) for a in (0.3, 1.9, 3.5, 5.1)]
    b.zone('dome', 'The Lens Dome', (TX - R_DOME + 1, DOME_Y + 1, TZ - R_DOME + 1, TX + R_DOME - 1, DOME_Y + 11, TZ + R_DOME - 1), dsp,
           'observatory_spire', kind='guardian', requires=['hall', 'vaults'], reward='focusing_lens', final=True,
           trigger=(TX - R_DOME, DOME_Y - 2, TZ - R_DOME, TX + R_DOME, DOME_Y + 12, TZ + R_DOME))


if __name__ == '__main__':
    build().save(foundation_level=0)
