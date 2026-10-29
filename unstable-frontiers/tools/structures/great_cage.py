"""The Great Cage: the Cagewright's prison at the heart of the Rustbone Scar, and the end of the adventure.

A ring wall with eight drum towers and four gatehouses encloses a courtyard of cell blocks (each cell still holds
something). In the middle, on a stepped plinth, stands a birdcage taller than anything else in the frontier: sixteen
basalt ribs curving to a crown ring, iron bars between, a brazier crown on top you can see across the Scar.

The inner gate has the Cagewright's Lock: using the Cagewright's Key on it wakes the finale. Inside, four pylons
shield the beast; break them while you fight. Below the cage floor, the Cagewright's vault opens when it falls.
"""
import math

from common import *
from kit import AIR, B, Build, h

W = L = 115
H = 100
G = 8
C = 57
R_WALL = 52
R_CAGE = 19
PLINTH = 4
CAGE_FLOOR = G + PLINTH
CAGE_H = 62


def build():
    b = Build('great_cage', W, H, L, seed=81)
    ground(b)
    ring_wall(b)
    cells(b)
    plinth(b)
    cage(b)
    vault(b)
    pylons(b)
    lock(b)
    dressing(b)
    zones(b)
    b.meta.update({'kind': 'great_cage', 'title': 'The Great Cage', 'ground': G})
    return b


def ground(b):
    """The courtyard: cracked flagstones and rust-red earth, bones where the prisoners were fed."""
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d <= R_WALL:
                q = h(x, G, z, 1)
                blk = DEEP_TILE if q < 0.35 else (DEEP_TILE_CRACK if q < 0.5 else ('minecraft:packed_mud' if q < 0.7 else 'minecraft:coarse_dirt'))
                if d < 8 + R_CAGE and d > R_CAGE + 1 and (int(math.degrees(math.atan2(z - C, x - C))) % 45) < 4:
                    blk = DARK_CHISEL          # radial paving lines toward the cage
                b.set(x, G - 1, z, blk)
                for y in range(G - 4, G - 1):
                    b.set(x, y, z, COBBLE_DEEP)
                if q > 0.985:
                    b.set(x, G, z, BONE_Y)


def ring_wall(b):
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if R_WALL - 1.5 <= d <= R_WALL + 1.5:
                ang = math.degrees(math.atan2(z - C, x - C)) % 360
                gate = any(abs(((ang - g + 180) % 360) - 180) < 4.5 for g in (0, 90, 180, 270))
                for y in range(G - 4, G + 18):
                    if gate and G <= y < G + 7:
                        b.set(x, y, z, AIR if d < R_WALL + 1 else B('iron_bars'))
                        continue
                    b.set(x, y, z, dark_stone(x, y, z) if y % 6 else DARK_CHISEL)
                # battlements and a wall-walk
                outer = d > R_WALL + 0.6
                if outer and int(ang * 2) % 3 == 0:
                    b.set(x, G + 18, z, wall('polished_blackstone_brick'))
                if not outer:
                    b.set(x, G + 17, z, slab('polished_blackstone_brick', 'top'))
    # drum towers between the gates, gatehouses over the gates
    for k in range(8):
        a = math.radians(45 * k + 22.5)
        tx, tz = C + R_WALL * math.cos(a), C + R_WALL * math.sin(a)
        b.cylinder(tx, tz, 4.5, G - 4, G + 26, lambda x, y, z: dark_stone(x, y, z) if y % 7 else DARK_CHISEL, hollow=1.2)
        b.cylinder(tx, tz, 3.2, G + 1, G + 1, OAK_DARK)
        for y in range(G + 27, G + 34):
            r = 5.2 * (1 - (y - G - 27) / 7)
            b.cylinder(tx, tz, max(0.5, r), y, y, DARK_BRICK, hollow=1.0)
        b.set(round(tx), G + 34, round(tz), ROD_UP)
        b.set(round(tx), G + 25, round(tz), SHROOM)
        for y in (G + 8, G + 16):
            for s in range(4):
                sx = round(tx + 4.5 * math.cos(math.radians(90 * s + 45)))
                sz = round(tz + 4.5 * math.sin(math.radians(90 * s + 45)))
                b.set(sx, y, sz, B('iron_bars'))
                b.set(sx, y + 1, sz, B('iron_bars'))
    for g in (0, 90, 180, 270):
        a = math.radians(g)
        gx, gz = C + R_WALL * math.cos(a), C + R_WALL * math.sin(a)
        ux, uz = -math.sin(a), math.cos(a)
        for side in (-1, 1):
            px, pz = gx + side * 6 * ux, gz + side * 6 * uz
            b.box(round(px) - 2, G - 4, round(pz) - 2, round(px) + 2, G + 24, round(pz) + 2, lambda x, y, z: dark_stone(x, y, z) if y % 5 else BASALT)
            b.set(round(px), G + 25, round(pz), B('soul_campfire', facing='north', lit='true', signal_fire='false', waterlogged='false'))
        # the arch over the gate and its hanging cage
        for t in range(-6, 7):
            x, z = round(gx + t * ux), round(gz + t * uz)
            y = G + 20 + round(3 * math.cos(t / 6 * math.pi / 2))
            b.set(x, y, z, DARK_CHISEL)
            b.set(x, y + 1, z, wall('polished_blackstone_brick'))
        for y in range(G + 12, G + 21):
            b.set(round(gx - 3 * math.cos(a)), y, round(gz - 3 * math.sin(a)), CHAIN_Y)
        b.hang_lantern(round(gx - 3 * math.cos(a)), G + 11, round(gz - 3 * math.sin(a)), soul=True)


def cells(b):
    """Eight cell blocks between the wall and the cage: barred fronts facing the cage, something inside every one."""
    b.meta['cell_doors'] = []
    for k in range(8):
        a = math.radians(45 * k)
        ux, uz = math.cos(a), math.sin(a)
        vx, vz = -uz, ux
        cx, cz = C + 36 * ux, C + 36 * uz
        for i in range(-5, 6):
            for j in range(-4, 5):
                x, z = round(cx + i * vx + j * ux), round(cz + i * vz + j * uz)
                for y in range(G, G + 8):
                    edge = abs(i) == 5 or abs(j) == 4 or y == G + 7
                    if not edge:
                        b.set(x, y, z, AIR)
                        continue
                    front = j == -4 and abs(i) < 5 and y < G + 6
                    if front:
                        b.set(x, y, z, B('iron_bars'))
                    else:
                        b.set(x, y, z, dark_stone(x, y, z) if y < G + 7 else slab('polished_blackstone_brick', 'bottom'))
                if abs(i) == 2 and j == 0:
                    for y in range(G, G + 7):
                        b.set(x, y, z, B('iron_bars'))   # a dividing wall: two cells per block
        door = [[round(cx + i * vx - 4 * ux), y, round(cz + i * vz - 4 * uz)] for i in (-1, 0, 1) for y in range(G, G + 3)]
        b.meta['cell_doors'].append(door)
        b.set(round(cx + 3 * vx + 2 * ux), G, round(cz + 3 * vz + 2 * uz), SKULL)
        b.set(round(cx - 3 * vx + 2 * ux), G, round(cz - 3 * vz + 2 * uz), BONE_Y)
        b.chain(round(cx + 2 * ux), G + 3, G + 6, round(cz + 2 * uz))
        if k % 2 == 0:
            b.chest(round(cx - 4 * vx + 3 * ux), G, round(cz - 4 * vz + 3 * uz), 'chests/great_cage_cell', facing='north')


def plinth(b):
    for y in range(G - 2, CAGE_FLOOR + 1):
        r = R_CAGE + 2 + (CAGE_FLOOR - y) * 1.0
        b.cylinder(C, C, r, y, y, lambda x, yy, z: dark_stone(x, yy, z) if yy < CAGE_FLOOR else weathered(x, yy, z, DEEP_TILE, DEEP_TILE_CRACK, salt=4))
    # stairs up the plinth at the four gates
    for g in (0, 90, 180, 270):
        a = math.radians(g)
        for s in range(PLINTH + 2):
            d = R_CAGE + 2 + PLINTH + 1 - s
            for w in range(-2, 3):
                x = round(C + d * math.cos(a) - w * math.sin(a))
                z = round(C + d * math.sin(a) + w * math.cos(a))
                face = {0: 'west', 90: 'north', 180: 'east', 270: 'south'}[g]
                b.set(x, G - 1 + s, z, B('polished_blackstone_brick_stairs', facing=face, half='bottom', shape='straight', waterlogged='false'))


def cage(b):
    """Sixteen ribs from the plinth to the crown ring; bars between; a brazier crown on a hook at the top."""
    top = CAGE_FLOOR + CAGE_H
    for y in range(CAGE_FLOOR + 1, top + 1):
        t = (y - CAGE_FLOOR) / CAGE_H
        # birdcage profile: straight-sided, swelling slightly, then curving in hard to the crown
        r = R_CAGE * (1.0 + 0.06 * math.sin(t * math.pi * 1.2)) * (1 if t < 0.62 else math.sqrt(max(0.0, 1 - ((t - 0.62) / 0.38) ** 2)))
        r = max(r, 3.0)
        for k in range(360):
            a = math.radians(k)
            x, z = round(C + r * math.cos(a)), round(C + r * math.sin(a))
            rib = (k % 22.5) < 2.6
            band = (y - CAGE_FLOOR) % 14 == 0
            blk = BASALT if rib else (DARK_CHISEL if band else B('iron_bars'))
            if y < CAGE_FLOOR + 6 and not rib and any(abs(((k - g + 180) % 360) - 180) < 6 for g in (0, 90, 180, 270)):
                blk = AIR       # the four doorways
            b.set(x, y, z, blk)
    # crown ring, hook and brazier
    b.cylinder(C, C, 4.5, top - 1, top + 1, lambda x, y, z: GILDED if h(x, y, z) < 0.5 else DARK_CHISEL, hollow=1.5)
    for y in range(top + 2, top + 12):
        b.set(C, y, C, CHAIN_Y)
    b.cylinder(C, C, 2.2, top + 12, top + 12, DARK_CHISEL)
    b.set(C, top + 13, C, B('soul_campfire', facing='north', lit='true', signal_fire='true', waterlogged='false'))
    for dx, dz in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        b.set(C + dx, top + 13, C + dz, SHROOM)
        b.set(C + dx, top + 14, C + dz, ROD_UP)
    # chains hanging down inside, each with a small gibbet, and a ring of hanging lanterns
    for k in range(8):
        a = math.radians(45 * k + 10)
        x, z = round(C + 9 * math.cos(a)), round(C + 9 * math.sin(a))
        yb = CAGE_FLOOR + 22 + (k % 3) * 4
        for y in range(yb, top - 6):
            b.set(x, y, z, CHAIN_Y)
        b.hang_lantern(x, yb - 1, z, soul=k % 2 == 0)


def vault(b):
    """Under the cage floor: the Cagewright's vault, reached by a stair that opens when the beast falls."""
    vy = G - 8
    b.box(C - 5, vy, C - 5, C + 5, vy + 5, C + 5, lambda x, y, z: DARK_BRICK if y in (vy, vy + 5) or abs(x - C) == 5 or abs(z - C) == 5 else AIR)
    for dx, dz in ((-3, -3), (3, -3), (-3, 3), (3, 3)):
        b.set(C + dx, vy + 1, C + dz, GILDED)
        b.chest(C + dx, vy + 2, C + dz, 'chests/great_cage_vault', facing='south')
    b.set(C, vy + 1, C, 'minecraft:crying_obsidian')
    b.set(C, vy + 4, C, SOUL_LANTERN)
    b.point('vault', C - 3, vy + 2, C - 3)
    # the trapdoor stair: the floor tiles over it are the gate
    gate = []
    for s in range(1, 9):
        x = C - 4 + s
        y = vy + 1 + (s - 1) * (CAGE_FLOOR - vy - 1) // 8
        b.set(x, y, C, B('polished_blackstone_brick_stairs', facing='east', half='bottom', shape='straight', waterlogged='false'))
        for yy in range(y + 1, min(y + 4, CAGE_FLOOR)):
            b.set(x, yy, C, AIR)
    for x in range(C + 2, C + 6):
        gate.append([x, CAGE_FLOOR, C])
    b.meta.setdefault('gates', {})['finale'] = gate


def pylons(b):
    """Four pylons at the quarter points inside the cage: the core block of each must be broken."""
    b.meta['pylons'] = []
    for g in (45, 135, 225, 315):
        a = math.radians(g)
        px, pz = round(C + 12 * math.cos(a)), round(C + 12 * math.sin(a))
        for y in range(CAGE_FLOOR + 1, CAGE_FLOOR + 4):
            b.set(px, y, pz, BASALT)
        b.set(px, CAGE_FLOOR + 4, pz, 'minecraft:crying_obsidian')
        b.set(px, CAGE_FLOOR + 5, pz, B('end_rod', facing='up'))
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            b.set(px + dx, CAGE_FLOOR + 1, pz + dz, B('polished_blackstone_brick_stairs', facing={(1, 0): 'west', (-1, 0): 'east', (0, 1): 'north', (0, -1): 'south'}[(dx, dz)],
                                                      half='bottom', shape='straight', waterlogged='false'))
        b.line((px, CAGE_FLOOR + 6, pz), (C, CAGE_FLOOR + 30, C), CHAIN_Y)
        b.meta['pylons'].append([px, CAGE_FLOOR + 4, pz])


def lock(b):
    """The Cagewright's Lock beside the south doorway of the cage."""
    lx, lz = C + 2, C + R_CAGE + 2
    b.set(lx, CAGE_FLOOR + 1, lz, 'minecraft:lodestone')
    b.set(lx, CAGE_FLOOR + 2, lz, B('chain', axis='y', waterlogged='false'))
    b.sign(lx - 1, CAGE_FLOOR + 1, lz, 0, ['The Cagewright\'s', 'Lock', '', 'Three keys made one'])
    b.point('lock', lx, CAGE_FLOOR + 1, lz)
    # the south doorway is barred until the lock turns
    gate = []
    for k in range(-5, 6):
        a = math.radians(90 + k)
        x, z = round(C + R_CAGE * math.cos(a)), round(C + R_CAGE * math.sin(a))
        for y in range(CAGE_FLOOR + 1, CAGE_FLOOR + 6):
            if b.get(x, y, z) in (None, AIR):
                b.set(x, y, z, B('iron_bars'))
                gate.append([x, y, z])
    b.meta.setdefault('gates', {})['lock'] = gate


def dressing(b):
    # braziers along the radial paths and the bones of whatever got loose
    for k in range(8):
        a = math.radians(45 * k + 22.5)
        for d in (26, 45):
            x, z = round(C + d * math.cos(a)), round(C + d * math.sin(a))
            b.set(x, G, z, DARK_CHISEL)
            b.set(x, G + 1, z, B('campfire', facing='north', lit='true', signal_fire='false', waterlogged='false'))
    for k in range(30):
        a = k * 2.399
        d = 22 + (k * 5) % 24
        x, z = round(C + d * math.cos(a)), round(C + d * math.sin(a))
        b.set(x, G, z, BONE_X if k % 3 else SKULL, over=False)
    # the Cagewright's last writing, on a lectern by the south gate
    b.lectern_book(C - 3, G, C + R_WALL - 6, 'north', 'The Cagewright', [
        'I built cages for everything the frontier made. Towers, gaols, nests turned to prisons.',
        'The last one I could not kill. So I built the largest cage of all around it, and four pylons to hold it.',
        'I took the keys apart and left them with my wardens: the cage, the roost, the hive.',
        'Whoever makes them one again will find the lock at the south door. Break the pylons. Do not let it out.',
    ], author='The Cagewright')


def zones(b):
    floor = CAGE_FLOOR + 1
    box = (C - R_CAGE + 1, floor, C - R_CAGE + 1, C + R_CAGE - 1, floor + 30, C + R_CAGE - 1)
    sp = [(round(C + 8 * math.cos(math.radians(a))), floor, round(C + 8 * math.sin(math.radians(a)))) for a in range(0, 360, 45)]
    sky = [(round(C + 14 * math.cos(math.radians(a))), floor + 18, round(C + 14 * math.sin(math.radians(a)))) for a in (0, 120, 240)]
    b.zone('finale', 'The Great Cage', box, sp, 'great_cage_finale', kind='finale', flyer_spawns=sky, gate='finale',
           reward='great_cage_heart,matriarch_mantle', final=True, pylons=b.meta['pylons'], lock=b.points['lock'], lock_gate='lock')


if __name__ == '__main__':
    build().save(foundation_level=G - 4)
