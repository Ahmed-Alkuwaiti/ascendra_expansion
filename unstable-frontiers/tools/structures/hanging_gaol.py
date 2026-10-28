"""The Hanging Gaol: a cage dungeon you cross rather than climb.

Two weathered pylons stand either side of a pit; a riveted girder spans them, and from it five cages hang on chains at
different depths, joined by sagging rope bridges. The route runs pylon, cell, cell, down to the warden's great cage over
the pit, then up again to the far pylon. Each cell holds a prisoner that wakes when you step aboard. Falling means a long
drop onto bone and dripstone.
"""
import math

from common import *
from kit import AIR, B, Build, h

W, H, L = 65, 82, 49
G = 26                      # local y of the ground around the pit
CX, CZ = 32, 24
PYLONS = [(6, CZ), (58, CZ)]
GIRDER_Y = G + 36
# (name, centre x, centre z, floor y, half width, height, roster)
CELLS = [
    ('cell_west', 17, 18, G + 20, 2, 5, 'gaol_cell_insect'),
    ('cell_north', 24, 31, G + 12, 2, 5, 'gaol_cell_wasp'),
    ('warden', CX, CZ, G - 9, 4, 8, 'gaol_warden'),
    ('cell_south', 40, 17, G + 12, 2, 5, 'gaol_cell_scorpion'),
    ('cell_east', 47, 30, G + 20, 2, 5, 'gaol_cell_flyer'),
]


def build():
    b = Build('hanging_gaol', W, H, L, seed=21)
    pit(b)
    for px, pz in PYLONS:
        pylon(b, px, pz)
    girder(b)
    for c in CELLS:
        cage(b, *c)
    bridges(b)
    scaffold(b)
    dressing(b)
    b.meta.update({'kind': 'cage_tower', 'title': 'Hanging Gaol', 'ground': G})
    return b


def pit(b):
    """An oval shaft with ragged walls, bone and dripstone at the bottom."""
    for x in range(W):
        for z in range(L):
            d = ((x - CX) / 21.0) ** 2 + ((z - CZ) / 15.0) ** 2
            wob = 0.08 * math.sin(math.atan2(z - CZ, x - CX) * 6) + h(x, 0, z, 3) * 0.06
            if d < 1.0 + wob:
                for y in range(2, G + 1):
                    b.set(x, y, z, AIR)
                b.set(x, 1, z, 'minecraft:gravel' if h(x, 1, z) < 0.3 else STONE)
                b.set(x, 0, z, STONE)
                q = h(x, 2, z, 9)
                if q < 0.07:
                    b.set(x, 2, z, BONE_Y if q < 0.03 else SKULL)
                elif q > 0.9:
                    b.set(x, 2, z, B('pointed_dripstone', thickness='tip', vertical_direction='up', waterlogged='false'))
                elif q > 0.82:
                    b.set(x, 2, z, COBWEB)
            elif d < 1.22 + wob:
                # the shaft wall: rough rock with old chain anchors
                for y in range(1, G + 1):
                    b.set(x, y, z, rock(x, y, z, 5) if y < G - 1 else (MOSS if h(x, y, z) < 0.3 else COARSE))
    # chains hanging into the dark from the rim
    for k in range(10):
        a = k * 0.63
        x, z = round(CX + 20 * math.cos(a)), round(CZ + 14 * math.sin(a))
        for y in range(G - 6 - (k * 7) % 12, G + 1):
            if b.get(x, y, z) in (None, AIR):
                b.set(x, y, z, CHAIN_Y)


def pylon(b, px, pz):
    """A square stone pylon with a ladder shaft, doors onto the catwalks, a balcony and a tapered cap."""
    top = GIRDER_Y + 6
    for y in range(0, top + 1):
        r = 5 if y < G + 2 else (4 if y < GIRDER_Y - 4 else 3)
        for x in range(px - r, px + r + 1):
            for z in range(pz - r, pz + r + 1):
                if not (0 <= x < W):
                    continue
                edge = abs(x - px) == r or abs(z - pz) == r
                corner = abs(x - px) == r and abs(z - pz) == r
                if edge:
                    blk = TUFF_BRICK if corner else weathered(x, y, z, DEEP_BRICK, 'minecraft:cracked_deepslate_bricks', salt=7)
                    if y % 9 == 0:
                        blk = 'minecraft:chiseled_tuff_bricks' if corner else DEEP_TILE
                    b.set(x, y, z, blk)
                elif y > G:
                    b.set(x, y, z, AIR)
                else:
                    b.set(x, y, z, COBBLE_DEEP)
    # the ladder shaft and the floors where the catwalks leave
    lx = px + (2 if px < CX else -2)
    for y in range(G + 1, GIRDER_Y + 1):
        b.set(lx, y, pz - 2, B('ladder', facing='south', waterlogged='false'))
    for fy in (G + 20, GIRDER_Y):
        for x in range(px - 3, px + 4):
            for z in range(pz - 3, pz + 4):
                if (x, z) != (lx, pz - 2):
                    b.set(x, fy, z, slab('dark_oak', 'top') if fy != GIRDER_Y else DEEP_TILE)
        b.hang_lantern(px, fy + 4, pz)
    # ground door on the outward side, catwalk door facing the pit
    ox = px - 5 if px < CX else px + 5
    for y in range(G + 1, G + 4):
        for z in (pz - 1, pz, pz + 1):
            b.set(ox, y, z, AIR)
    ix = px + 4 if px < CX else px - 4
    for y in range(G + 21, G + 24):
        b.set(ix, y, pz, AIR)
    # corner piers that step in as they rise, arrow slits, and a corbelled balcony at the catwalk door
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in range(G - 2, GIRDER_Y + 2):
                r = 5 if y < G + 2 else (4 if y < GIRDER_Y - 4 else 3)
                ext = 1 if y < G + 14 else 0
                for e in range(0, ext + 1):
                    b.set(px + sx * (r + e), y, pz + sz * (r + e), TUFF_BRICK if y % 9 else 'minecraft:chiseled_tuff_bricks')
    for face in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        for y0 in (G + 8, G + 28):
            r = 4 if y0 > G + 2 else 5
            if y0 > GIRDER_Y - 4:
                r = 3
            x, z = px + face[0] * r, pz + face[1] * r
            if 0 <= x < W:
                for y in range(y0, y0 + 3):
                    b.set(x, y, z, B('iron_bars'))
    bx = px + 5 if px < CX else px - 5
    for z in range(pz - 2, pz + 3):
        b.set(bx, G + 19, z, B('polished_blackstone_brick_stairs', facing='west' if px < CX else 'east', half='top', shape='straight', waterlogged='false'))
        b.set(bx, G + 20, z, slab('dark_oak', 'top'))
        b.set(bx + (1 if px < CX else -1), G + 20, z, slab('dark_oak', 'top'))
        if z in (pz - 2, pz + 2):
            b.set(bx + (1 if px < CX else -1), G + 21, z, fence())
    for y in range(G + 6, G + 18):
        b.set(px + (5 if px > CX else -5) * 0, y, pz + 4 if y < G + 2 else pz + 5, B('black_wall_banner', facing='south') if y == G + 17 else None)
    # cap: a stepped pyramid with a brazier and a bell for the warden
    for k in range(4):
        r = 4 - k
        for x in range(px - r, px + r + 1):
            for z in range(pz - r, pz + r + 1):
                b.set(x, top + 1 + k, z, DARK_BRICK if k < 3 else DARK_CHISEL)
    b.set(px, top + 5, pz, B('soul_campfire', facing='north', lit='true', signal_fire='true', waterlogged='false'))
    b.set(px, GIRDER_Y + 3, pz, B('bell', attachment='ceiling', facing='north', powered='false'))


def girder(b):
    """A riveted truss between the pylons: two chords of blackstone, crossed bracing, a walkway on top."""
    x0, x1 = PYLONS[0][0] + 3, PYLONS[1][0] - 3
    for x in range(x0, x1 + 1):
        sag = int(1.5 * math.sin(math.pi * (x - x0) / (x1 - x0)))
        for z in (CZ - 2, CZ + 2):
            b.set(x, GIRDER_Y - sag, z, DARK_BRICK)
            b.set(x, GIRDER_Y - 4 - sag, z, DARK_BRICK)
            # X bracing between the chords
            ph = (x - x0) % 8
            yb = GIRDER_Y - 4 - sag + (ph if ph <= 4 else 8 - ph)
            b.set(x, yb, z, wall('polished_blackstone_brick'))
        for z in range(CZ - 2, CZ + 3):
            b.set(x, GIRDER_Y + 1 - sag, z, slab('polished_blackstone_brick', 'bottom'))
        if (x - x0) % 6 == 0:
            for z in range(CZ - 2, CZ + 3):
                b.set(x, GIRDER_Y - 4 - sag, z, DARK_CHISEL)
            b.set(x, GIRDER_Y + 2 - sag, CZ - 2, fence())
            b.set(x, GIRDER_Y + 2 - sag, CZ + 2, fence())
            b.set(x, GIRDER_Y + 3 - sag, CZ + 2, LANTERN_STAND)


def cage(b, name, cx, cz, fy, r, ht, roster):
    """A hanging cell: a slab floor ringed by bars under a domed cap, hung by four chains from the girder."""
    top = fy + ht
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            edge = abs(x - cx) == r or abs(z - cz) == r
            corner = abs(x - cx) == r and abs(z - cz) == r
            b.set(x, fy, z, DARK_BRICK if edge else DEEP_TILE)
            b.set(x, fy - 1, z, slab('polished_blackstone', 'top') if not edge else DARK_CHISEL)
            for y in range(fy + 1, top):
                if corner:
                    b.set(x, y, z, BASALT)
                elif edge:
                    b.set(x, y, z, B('iron_bars'))
                else:
                    b.set(x, y, z, AIR)
            b.set(x, top, z, DARK_CHISEL if corner else slab('polished_blackstone_brick', 'bottom'))
    # domed cap and the hanging point
    for k in range(1, r + 1):
        rr = r - k
        for x in range(cx - rr, cx + rr + 1):
            for z in range(cz - rr, cz + rr + 1):
                if abs(x - cx) == rr or abs(z - cz) == rr:
                    b.set(x, top + k, z, DARK_BRICK)
    # chains up to the girder from the cap corners (they converge on a hook over the cell)
    hook = (cx, GIRDER_Y - 5, CZ)
    for dx, dz in ((-r, -r), (r, -r), (-r, r), (r, r)):
        b.line((cx + dx, top + 1, cz + dz), hook, CHAIN_Y)
    b.line((cx, top + r + 1, cz), hook, CHAIN_Y)
    # a hatch in the cap of the warden's cage, and a vault cell inside it
    if name == 'warden':
        for x in range(cx - 1, cx + 2):
            for y in range(top, top + r + 1):
                b.set(x, y, cz, AIR)
        b.set(cx - 2, fy + 1, cz - 2, GILDED)
        b.chest(cx - 2, fy + 2, cz - 2, 'chests/gaol_vault', facing='south')
        b.point('vault', cx - 2, fy + 2, cz - 2)
        for y in range(fy + 1, fy + 4):
            b.set(cx - 3, y, cz - 1, B('iron_bars'))
            b.set(cx - 2, y, cz - 1, B('iron_bars'))
            b.set(cx - 1, y, cz - 1, B('iron_bars'))
            b.set(cx - 1, y, cz - 2, B('iron_bars'))
            b.set(cx - 1, y, cz - 3, B('iron_bars'))
        b.meta.setdefault('gates', {})['warden'] = [[cx - 2, y, cz - 1] for y in range(fy + 1, fy + 4)]
        for x in range(cx - r + 1, cx + r):
            for z in range(cz - r + 1, cz + r):
                if h(x, fy, z, 61) < 0.12:
                    b.set(x, fy + 1, z, BONE_Y if h(x, fy, z, 2) < 0.5 else SKULL)
    else:
        b.set(cx + 1, fy + 1, cz + 1, CHAIN_Y)
        b.set(cx - 1, fy + 1, cz, BONE_X)
        if name in ('cell_west', 'cell_south'):
            b.chest(cx, fy + 1, cz - 1, 'chests/gaol_cell', facing='south')
    b.hang_lantern(cx, top - 1, cz, soul=True)
    box = (cx - r + 1, fy + 1, cz - r + 1, cx + r - 1, top - 1, cz + r - 1)
    trig = (cx - r - 2, fy - 1, cz - r - 2, cx + r + 2, top + 1, cz + r + 2)
    sp = [(cx + dx, fy + 1, cz + dz) for dx, dz in ((0, 0), (1, 1), (-1, -1), (1, -1), (-1, 1))]
    if name == 'warden':
        b.zone('warden', 'The Warden\'s Cage', box, sp, roster, kind='guardian', gate='warden', reward='cage_trophy', final=True,
               trigger=trig, requires=['cell_west', 'cell_north', 'cell_south', 'cell_east'])
    else:
        b.zone(name, 'A hanging cell', box, sp, roster, kind='cell', trigger=trig, waves=1)


def bridges(b):
    """Rope bridges along the route, sagging between doorways."""
    route = [(PYLONS[0][0] + 5, G + 20, CZ)] + [(c[1], c[3], c[2]) for c in CELLS] + [(PYLONS[1][0] - 5, G + 20, CZ)]
    for (x0, y0, z0), (x1, y1, z1) in zip(route, route[1:]):
        n = max(2, int(math.dist((x0, z0), (x1, z1)) * 2))
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            z = z0 + (z1 - z0) * t
            y = y0 + (y1 - y0) * t - 2.2 * math.sin(math.pi * t)
            xi, yi, zi = round(x), int(round(y)), round(z)
            if b.get(xi, yi, zi) in (None, AIR):
                b.set(xi, yi, zi, slab('spruce', 'top' if (y - int(y)) > 0.5 else 'bottom'))
            for k in (1, 2):
                if b.get(xi, yi + k, zi) == 'minecraft:iron_bars':
                    b.set(xi, yi + k, zi, AIR)          # cut a door where the bridge meets a cell
            if i % 3 == 0:
                dx, dz = z1 - z0, -(x1 - x0)
                ln = math.hypot(dx, dz) or 1
                for s in (-1, 1):
                    px, pz = round(x + s * dx / ln), round(z + s * dz / ln)
                    if b.get(px, yi + 1, pz) in (None, AIR):
                        b.set(px, yi + 1, pz, fence('spruce'))


def scaffold(b):
    """A scaffolding tower from the pit floor to the rim beside the warden's cage: the way down, and the way out."""
    sx, sz = CX + 6, CZ + 6
    for y in range(2, G + 2):
        b.set(sx, y, sz, B('scaffolding', bottom='false', distance=0, waterlogged='false'))
    # a plank step from the scaffold onto the warden cage roof
    for x in range(CX + 3, sx):
        b.set(x, G - 9 + 8 + 1, sz - 2, slab('spruce', 'bottom'))


def dressing(b):
    """The pit rim: a ring of iron spikes, impaled skulls, a toppled cage, the camp the jailers left."""
    for k in range(40):
        a = k * math.tau / 40
        x, z = round(CX + 23.5 * math.cos(a)), round(CZ + 17 * math.sin(a))
        if 0 <= x < W and 0 <= z < L and h(x, 0, z, 4) < 0.7:
            b.set(x, G + 1, z, B('iron_bars'))
            if k % 5 == 0:
                b.set(x, G + 2, z, fence())
                b.set(x, G + 3, z, SKULL)
    # a fallen cage beside the west pylon
    fx, fz = 9, 40
    for x in range(fx, fx + 4):
        for y in range(G + 1, G + 4):
            b.set(x, y, fz, B('iron_bars'))
            b.set(x, y, fz + 3, B('iron_bars') if h(x, y, fz, 2) < 0.7 else AIR)
    for z in range(fz, fz + 4):
        b.set(fx, G + 1, z, BASALT)
    b.chain(fx + 1, G + 1, G + 1, fz + 1)
    b.set(fx + 2, G + 1, fz + 1, SKULL)
    # the jailers' camp: a lectern with their last notes, a barrel, a cold fire
    b.lectern_book(52, G + 1, 41, 'north', 'Gaol Ledger',
                   ['Ledger of the Hanging Gaol.\n\nFive cells. Feed the west cell twice daily, the warden never.',
                    'The warden is no beast of ours. The Cagewright brought it in chains and told us never to open the great cage.',
                    'Night three. The chains are singing. Something below the pit is answering them.',
                    'If you read this: the great cage opens only once the four cells are quiet. Do not be in it when it does.'])
    b.chest(54, G + 1, 41, 'chests/camp_supply', barrel=True)
    b.set(50, G + 1, 42, B('campfire', facing='north', lit='false', signal_fire='false', waterlogged='false'))


if __name__ == '__main__':
    build().save(foundation_level=0)
