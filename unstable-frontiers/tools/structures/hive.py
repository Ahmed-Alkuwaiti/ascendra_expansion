"""The Brood Hive: a living mound over a nest of tunnels.

Above ground: a mound of packed mud and root, pocked with holes, with termite-style chimneys you can see over the trees.
Below: a winding descent through the entrance hall, the fungus garden and the larder to the brood chamber, where egg
clutches cover the floor (each clutch still standing hatches reinforcements, smash them to stop it), and at the bottom
the royal chamber, where the hive's tyrant sits on a throne of chitin in front of the sealed royal cache.
"""
import math

from common import *
from kit import AIR, B, Build, h

W, H, L = 61, 54, 61
G = 30
CX, CZ = 30, 30

ROOMS = {   # name: (centre, radii) in local coordinates
    'hall': ((30, G - 6, 30), (6, 4, 6)),
    'garden': ((44, G - 12, 24), (7, 4.5, 6)),
    'larder': ((17, G - 14, 38), (5, 3.5, 5)),
    'brood': ((32, G - 20, 40), (10, 5.5, 8)),
    'royal': ((30, G - 27, 20), (12, 7, 11)),
}
TUNNELS = [
    [(30, G + 6, 49), (30, G + 1, 42), (30, G - 4, 34)],                 # the main mouth down to the hall
    [(34, G - 7, 28), (39, G - 10, 25), (42, G - 12, 24)],                # hall to garden
    [(26, G - 7, 33), (21, G - 11, 36), (18, G - 13, 38)],                # hall to larder
    [(42, G - 13, 28), (40, G - 17, 34), (36, G - 19, 38)],               # garden to brood
    [(20, G - 15, 40), (24, G - 18, 42), (27, G - 19, 41)],               # larder to brood
    [(30, G - 21, 34), (29, G - 24, 28), (30, G - 26, 24)],               # brood down to the royal chamber
    [(46, G + 8, 30), (45, G + 2, 28), (44, G - 9, 25)],                  # a chimney shaft straight into the garden
]


def build():
    b = Build('brood_hive', W, H, L, seed=41)
    mound(b)
    linings(b)
    carve(b)
    dress(b)
    zones(b)
    b.meta.update({'kind': 'hive', 'title': 'Brood Hive', 'ground': G})
    return b


def mud(x, y, z, salt=0):
    q = h(x, y, z, salt)
    if q < 0.18:
        return MUD_BRICK if y < G - 10 else ROOTED
    if q < 0.45:
        return PACKED_MUD
    if q < 0.6:
        return MUD
    if q < 0.7:
        return COARSE
    return PACKED_MUD


def mound(b):
    """The dome over the hive, its chimneys, and the holes the brood comes and goes by."""
    b.ellipsoid(CX, G - 2, CZ, 17, 12, 15, lambda x, y, z: mud(x, y, z, 1), over=False)
    chim = [(23, 24, 11), (37, 22, 13), (31, 36, 16), (46, 30, 9), (19, 35, 8)]
    for cx, cz, ht in chim:
        for y in range(G + 4, G + 4 + ht + 6):
            t = (y - G - 4) / (ht + 6)
            r = 3.2 * (1 - t) + 0.8
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    if math.hypot(x - cx, z - cz) <= r + 0.4 * math.sin(y * 0.8 + x):
                        b.set(x, y, z, mud(x, y, z, 2) if h(x, y, z, 3) > 0.08 else 'minecraft:mud_bricks')
        b.set(cx, G + 4 + ht + 5, cz, AIR)
    # pockmarks and roots on the dome
    for k in range(40):
        a = k * 2.399
        e = 0.2 + (k % 7) / 9
        x = round(CX + 16 * math.cos(a) * math.cos(e))
        z = round(CZ + 14 * math.sin(a) * math.cos(e))
        y = round(G - 2 + 11.5 * math.sin(e))
        b.ellipsoid(x, y, z, 1.2, 1.2, 1.2, AIR)
        if k % 3 == 0:
            b.set(x, y - 2, z, B('hanging_roots', waterlogged='false'), over=False)
    # the trodden ground round the mound: coarse dirt, bone, a toppled tree
    for x in range(W):
        for z in range(L):
            d = ((x - CX) / 26) ** 2 + ((z - CZ) / 24) ** 2
            if 0.4 < d < 1 and h(x, G, z, 5) < 0.4:
                b.set(x, G, z, COARSE if h(x, G, z, 6) < 0.6 else ROOTED, over=False)
                if h(x, G, z, 7) < 0.05:
                    b.set(x, G + 1, z, BONE_Y)
    b.line((6, G + 1, 14), (16, G + 2, 6), DARK_LOG_X, radius=0.8)


def linings(b):
    """A consistent wall round every room and tunnel, so the hive looks the same whatever rock it was dug into."""
    for name, ((x, y, z), (rx, ry, rz)) in ROOMS.items():
        mat = (lambda X, Y, Z: 'antarchy:chitin_block' if h(X, Y, Z, 9) < 0.35 else mud(X, Y, Z, 3)) if name == 'royal' else (lambda X, Y, Z: mud(X, Y, Z, 4))
        b.ellipsoid(x, y, z, rx + 2, ry + 2, rz + 2, mat, over=False)
    for path in TUNNELS:
        b.curve(path, lambda X, Y, Z: mud(X, Y, Z, 5), radius=lambda t: 3.3, over=False)


def carve(b):
    for name, ((x, y, z), (rx, ry, rz)) in ROOMS.items():
        b.ellipsoid(x, y, z, rx, ry, rz, AIR)
        # flatten the floor so it can be walked and fought on
        for X in range(int(x - rx), int(x + rx) + 1):
            for Z in range(int(z - rz), int(z + rz) + 1):
                if ((X - x) / rx) ** 2 + ((Z - z) / rz) ** 2 <= 0.85:
                    fy = int(y - ry * 0.55)
                    for Y in range(int(y - ry) - 1, fy):
                        b.set(X, Y, Z, mud(X, Y, Z, 8))
    for path in TUNNELS:
        b.curve(path, AIR, radius=lambda t: 1.8)


def floor_y(name):
    (x, y, z), (rx, ry, rz) = ROOMS[name]
    return int(y - ry * 0.55)


def dress(b):
    # the hall: webs and the first eggs, a dead explorer
    (x, y, z), r = ROOMS['hall']
    fy = floor_y('hall')
    for k in range(10):
        a = k * 0.7
        b.set(round(x + 4.5 * math.cos(a)), fy + 3 + k % 3, round(z + 4.5 * math.sin(a)), COBWEB, over=False)
    b.set(x - 3, fy, z + 2, SKULL)
    b.set(x - 2, fy, z + 2, B('lantern', hanging='false', waterlogged='false'))
    b.chest(x - 4, fy, z + 1, 'chests/camp_supply', barrel=True)
    # the garden: mushroom pillars, glowing caps, a mycelium floor
    (x, y, z), r = ROOMS['garden']
    fy = floor_y('garden')
    for X in range(x - 7, x + 8):
        for Z in range(z - 6, z + 7):
            if b.get(X, fy - 1, Z) not in (None, AIR) and b.get(X, fy, Z) in (None, AIR):
                b.set(X, fy - 1, Z, 'minecraft:mycelium' if h(X, fy, Z) < 0.7 else 'minecraft:podzol')
    for k, (dx, dz, ht) in enumerate(((-4, -2, 5), (3, 3, 6), (4, -3, 4), (-2, 4, 5))):
        for Y in range(fy, fy + ht):
            b.set(x + dx, Y, z + dz, B('mushroom_stem', down='false', east='true', north='true', south='true', up='false', west='true'))
        cap = 'minecraft:red_mushroom_block' if k % 2 else 'minecraft:brown_mushroom_block'
        b.ellipsoid(x + dx, fy + ht, z + dz, 2.2, 0.8, 2.2, cap, over=False)
        b.set(x + dx, fy + ht - 1, z + dz, SHROOM)
    # the larder: bones, a carcass, the hive's hoard
    (x, y, z), r = ROOMS['larder']
    fy = floor_y('larder')
    for k in range(18):
        X, Z = x + int(4 * math.cos(k)), z + int(4 * math.sin(k * 1.3))
        b.set(X, fy, Z, BONE_X if k % 3 else SKULL, over=False)
    b.ellipsoid(x + 1, fy + 1, z - 1, 2.0, 1.2, 1.3, lambda X, Y, Z: 'minecraft:red_mushroom_block' if h(X, Y, Z) < 0.5 else BONE_Z, over=False)
    b.chest(x - 2, fy, z - 2, 'chests/hive_larder', facing='east')
    # the brood chamber: egg clutches on mud, wool sacs on the walls, roots from the ceiling
    (x, y, z), (rx, ry, rz) = ROOMS['brood']
    fy = floor_y('brood')
    b.meta['brood_eggs'] = []
    for X in range(int(x - rx), int(x + rx) + 1):
        for Z in range(int(z - rz), int(z + rz) + 1):
            if ((X - x) / rx) ** 2 + ((Z - z) / rz) ** 2 > 0.75 or b.get(X, fy, Z) not in (None, AIR):
                continue
            q = h(X, fy, Z, 51)
            if q < 0.16:
                b.set(X, fy - 1, Z, MUD)
                b.set(X, fy, Z, B('turtle_egg', eggs=2 + int(q * 40) % 3, hatch=1))
                b.meta['brood_eggs'].append([X, fy, Z])
            elif q > 0.94:
                b.set(X, fy, Z, 'minecraft:white_wool')
                b.set(X, fy + 1, Z, COBWEB)
    for k in range(16):
        a = k * 0.4
        X, Z = round(x + (rx - 1) * math.cos(a)), round(z + (rz - 1) * math.sin(a))
        b.set(X, fy + 4, Z, B('hanging_roots', waterlogged='false'), over=False)
    for dx in (-5, 0, 5):
        b.set(x + dx, int(y + ry) - 1, z, 'minecraft:ochre_froglight', over=False)
    # the royal chamber: a throne of chitin and bone, the sealed cache behind a resin wall
    (x, y, z), (rx, ry, rz) = ROOMS['royal']
    fy = floor_y('royal')
    tz = z - rz + 3
    b.box(x - 4, fy, tz, x + 4, fy, tz + 3, 'antarchy:chitin_block')
    b.box(x - 3, fy + 1, tz, x + 3, fy + 1, tz + 2, 'antarchy:chitin_block')
    b.box(x - 2, fy + 2, tz, x + 2, fy + 5, tz, 'antarchy:chitin_block')
    for dx in (-3, 3):
        b.line((x + dx, fy + 2, tz), (x + dx * 1.7, fy + 8, tz - 1), BONE_Y, radius=0.6)
    b.set(x, fy + 6, tz, SKULL)
    # the cache: a hollow behind the throne, closed by a wall of honey "resin" that dissolves when the tyrant dies
    b.box(x - 2, fy, tz - 4, x + 2, fy + 3, tz - 1, AIR)
    b.box(x - 3, fy - 1, tz - 5, x + 3, fy + 4, tz - 5, 'antarchy:chitin_block', over=False)
    b.chest(x, fy, tz - 3, 'chests/hive_royal', facing='south')
    b.point('vault', x, fy, tz - 3)
    gate = []
    for dx in (-1, 0, 1):
        for dy in range(0, 3):
            b.set(x + dx + 3, fy + dy, tz - 1, 'minecraft:honey_block')
            gate.append([x + dx + 3, fy + dy, tz - 1])
    b.box(x + 2, fy, tz - 2, x + 5, fy + 2, tz - 2, AIR)
    b.meta.setdefault('gates', {})['royal'] = gate
    for k in range(8):
        a = k * math.tau / 8
        b.set(round(x + (rx - 2) * math.cos(a)), fy, round(z + (rz - 2) * math.sin(a)), 'minecraft:ochre_froglight' if k % 2 else SHROOM)


def zones(b):
    def box(name, grow=0):
        (x, y, z), (rx, ry, rz) = ROOMS[name]
        return (int(x - rx - grow), int(y - ry - grow), int(z - rz - grow), int(x + rx + grow), int(y + ry + grow), int(z + rz + grow))

    def spots(name, n=8, ring=0.55):
        (x, y, z), (rx, ry, rz) = ROOMS[name]
        fy = floor_y(name)
        return [(round(x + rx * ring * math.cos(k * math.tau / n)), fy, round(z + rz * ring * math.sin(k * math.tau / n))) for k in range(n)]

    b.zone('hall', 'The Entrance Hall', box('hall'), spots('hall', 5), 'hive_workers', kind='ambush', waves=1)
    b.zone('brood', 'The Brood Chamber', box('brood'), spots('brood'), 'hive_brood', kind='brood', brood_eggs=b.meta['brood_eggs'])
    b.zone('royal', 'The Hive Tyrant', box('royal'), spots('royal', 6, 0.45), 'hive_tyrant', kind='guardian', gate='royal',
           reward='hive_heart', final=True)


if __name__ == '__main__':
    build().save()
