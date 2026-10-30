"""The Drowned Expanse's five places, built onto the flat pads its generator keeps for them (DrownedTerrain's anchors),
and the frontier's Sunken Gate, the way in:

    the Sunken Gate     (frontier) a flooded stair down to a tide gate; the expedition's diving stores and journal
    Tidewatch Station   the research station: a glass dome on legs with a moon pool, the return gate, a beacon mast
    Deepwork Station    a salvage rig: a flooded pump hall (an ambush), a crane with a diving bell for a shelter
    the Choir Temple    a drowned basilica: the nave (waves), a rose window of light, a bell tower with an air loft
    the Wreck of the Long Patience  a broken hull on the slope: the Wreckmaw in the hold; a capsized stern holds air
    the Sunless Vault   the Deepcaller's flooded dome: pillars for cover, breath vents, the abyssal bell, an antechamber

Water is deliberate. Every cell a template leaves empty is filled with water, so nothing carves an accidental air pocket;
only the shelters (listed per build in `dry`) hold air, and check() refuses a build where air touches water from the
side or from above (water would pour in) or where a dry room's wall is a block water passes through. Waterloggable blocks
are written waterlogged unless they stand in a shelter. Each template's ground row is the pad's top (the sea floor).
"""
import math

from kit import AIR, B, Build, h

U = 'unstable_frontiers:'
WATER = 'minecraft:water'
SLATE = U + 'brine_slate'
BRICK = U + 'brine_bricks'
CHISELED = U + 'chiseled_brine'
CORAL = U + 'lumen_coral'
VENT = U + 'breath_vent'
GLYPH = U + 'tide_glyph'
GLASS = 'minecraft:glass'
TINT = 'minecraft:light_blue_stained_glass'
PRISM = 'minecraft:prismarine_bricks'
DARK_PRISM = 'minecraft:dark_prismarine'
SEA_LANTERN = 'minecraft:sea_lantern'
COPPER = 'minecraft:waxed_oxidized_copper'
CUT_COPPER = 'minecraft:waxed_oxidized_cut_copper'
COPPER_GRATE = 'minecraft:waxed_oxidized_copper_grate'
PLANK = 'minecraft:spruce_planks'
DARK_PLANK = 'minecraft:dark_oak_planks'
LOG_Y = B('stripped_spruce_log', axis='y')
LOG_X = B('stripped_spruce_log', axis='x')
LOG_Z = B('stripped_spruce_log', axis='z')
IRON = 'minecraft:iron_block'


def wl(name, **props):
    """A waterloggable block; flood() decides the waterlogged value."""
    return B(name, waterlogged='true', **props)


def bars():
    return wl('iron_bars', east='false', north='false', south='false', west='false')


def chain_y():
    return wl('chain', axis='y')


def lantern(hanging=True):
    return wl('sea_pickle', pickles='4') if not hanging else wl('lantern', hanging='true')


def bell_block(abyssal=False):
    return wl(U + ('abyssal_bell' if abyssal else 'tide_bell'))


GATE = wl(U + 'tide_gate')


def stone(x, y, z, salt=0):
    r = h(x, y, z, salt)
    if r < 0.07:
        return CHISELED
    if r < 0.22:
        return SLATE
    return BRICK


def disc(b, cx, cz, r, y, pick):
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for z in range(int(cz - r) - 1, int(cz + r) + 2):
            if math.hypot(x - cx, z - cz) <= r:
                b.set(x, y, z, pick(x, y, z) if callable(pick) else pick)


def water_box(b, x0, y0, z0, x1, y1, z1):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            for z in range(min(z0, z1), max(z0, z1) + 1):
                b.set(x, y, z, WATER)


def dry_cell(b, x, y, z):
    b.set(x, y, z, AIR)
    b.dry.add((x, y, z))


def glyph_post(b, x, y, z):
    b.set(x, y, z, BRICK)
    b.set(x, y + 1, z, GLYPH)


def kelp(b, x, y, z, height):
    for k in range(height):
        b.set(x, y + k, z, B('kelp_plant') if k < height - 1 else B('kelp', age='25'))


def reef(b, x, y, z, salt):
    """A little coral clump on the floor (y is the first water row)."""
    kinds = ('tube', 'brain', 'bubble', 'fire', 'horn')
    k = kinds[int(h(x, 0, z, salt) * len(kinds))]
    r = h(x, 1, z, salt)
    if r < 0.4:
        b.set(x, y, z, wl(f'{k}_coral'))
    elif r < 0.7:
        b.set(x, y, z, wl(f'{k}_coral_fan'))
    elif r < 0.85:
        b.set(x, y, z, wl('sea_pickle', pickles=str(1 + int(h(x, 2, z, salt) * 4))))
    else:
        b.set(x, y, z, B('seagrass'))


# ------------------------------------------------------------------------------------------------- finishing
PASS_THROUGH = ('stairs', 'slab', 'wall', 'fence', 'pane', 'bars', 'chain', 'lantern', 'chest', 'sign', 'ladder', 'trapdoor', 'pickle',
                'coral', 'seagrass', 'kelp', 'gate', 'bell', 'lectern', 'door', 'carpet', 'torch', 'rod', 'button', 'vent', 'glyph',
                'crafting', 'barrel', 'water')


def solid_wall(name):
    return name not in (AIR, WATER) and not any(s in name for s in PASS_THROUGH)


def flood(b):
    """AIR outside the shelters becomes water (under the sea); waterloggable blocks are waterlogged unless they stand in a
    shelter (on land, only those in the build's `wet` cells are)."""
    for pos, (name, props) in list(b.b.items()):
        if name == AIR and pos not in b.dry and not b.land:
            b.b[pos] = (WATER, ())
    for pos, (name, props) in list(b.b.items()):
        p = dict(props)
        if 'waterlogged' in p:
            wet = pos in b.wet if b.land else pos not in b.dry and pos not in b.dry_furniture
            p['waterlogged'] = 'true' if wet else 'false'
            b.b[pos] = (name, tuple(sorted(p.items())))


def check(b):
    """Refuses a build whose shelters would flood (or whose water would pour into them)."""
    problems = []
    for (x, y, z) in b.dry:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
            n = (x + dx, y + dy, z + dz)
            if n in b.dry:
                continue
            cell = b.b.get(n)
            name = cell[0] if cell else WATER            # outside the template, or left unset: the sea
            if dy == -1 and name == WATER:
                continue                                  # a moon pool: water below air stays put
            if n in b.dry_furniture:
                continue                                  # furniture standing inside the shelter (not waterlogged)
            if not solid_wall(name):
                problems.append(f'{b.name}: dry cell {x},{y},{z} meets {name} at {n}')
    stray = [p for p, c in b.b.items() if c[0] == AIR and p not in b.dry and not b.land]
    if stray:
        problems.append(f'{b.name}: {len(stray)} air cells outside the shelters, e.g. {stray[:3]}')
    for pos in b.dry_furniture:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0)):
            n = (pos[0] + dx, pos[1] + dy, pos[2] + dz)
            cell = b.b.get(n)
            if (cell is None or cell[0] == WATER) and n not in b.dry:
                problems.append(f'{b.name}: shelter furniture at {pos} touches water at {n}')
    if problems:
        raise SystemExit('\n'.join(problems[:20]))


def new(name, W, H, L, seed, land=False):
    b = Build(name, W, H, L, seed)
    b.dry = set()
    b.dry_furniture = set()
    b.land = land
    b.wet = set()
    return b


def furnish(b, x, y, z, block):
    """A block inside a shelter (a bell, a chest, a gate): written dry, and counted as part of the shelter."""
    b.set(x, y, z, block)
    b.dry_furniture.add((x, y, z))


def done(b):
    flood(b)
    check(b)
    return b


# ---------------------------------------------------------------------------------------- shelter (a dome on a deck)
def dome_shelter(b, cx, cz, floor_y, r, pool, shell=GLASS, rib=BRICK, ribs=8):
    """A hemispherical glass dome of radius r on a solid deck at floor_y, air inside, with a 2x2 moon pool in the deck
    at pool=(x, z) (open water below the deck lets a diver swim up into it)."""
    disc(b, cx, cz, r + 0.5, floor_y, lambda x, y, z: CHISELED if abs(math.hypot(x - cx, z - cz) - (r - 1.5)) < 0.5 else BRICK)
    for x in range(int(cx - r) - 2, int(cx + r) + 3):
        for z in range(int(cz - r) - 2, int(cz + r) + 3):
            for y in range(floor_y + 1, floor_y + r + 2):
                d = math.sqrt((x - cx) ** 2 + ((y - floor_y) * 1.0) ** 2 + (z - cz) ** 2)
                if d < r - 0.5:
                    dry_cell(b, x, y, z)
                elif d < r + 0.6:
                    a = math.atan2(z - cz, x - cx)
                    on_rib = abs(((a / (2 * math.pi) * ribs) % 1) - 0.5) > 0.42 or y == floor_y + 1
                    b.set(x, y, z, rib if on_rib else shell)
    px, pz = pool
    for x in (px, px + 1):
        for z in (pz, pz + 1):
            b.set(x, floor_y, z, WATER)
    # a rim round the pool, so nobody steps in by accident
    for x in range(px - 1, px + 3):
        for z in range(pz - 1, pz + 3):
            if (x, floor_y, z) not in ((px, floor_y, pz), (px + 1, floor_y, pz), (px, floor_y, pz + 1), (px + 1, floor_y, pz + 1)):
                if x in (px - 1, px + 2) or z in (pz - 1, pz + 2):
                    b.set(x, floor_y, z, CHISELED)


# ------------------------------------------------------------------------------------------------- the Sunken Gate
def sunken_gate():
    W = L = 25
    C, G = 12, 9
    b = new('sunken_gate', W, 24, L, seed=601, land=True)    # in the frontier: only the pool is water
    # the shaft: a 9x9 well of brine bricks, eight deep, flooded to the brim
    for x in range(C - 5, C + 6):
        for z in range(C - 5, C + 6):
            for y in range(G - 8, G + 1):
                edge = x in (C - 5, C + 5) or z in (C - 5, C + 5) or y == G - 8
                b.set(x, y, z, stone(x, y, z, 1) if edge else WATER)
                if not edge:
                    b.wet.add((x, y, z))
    # a stair spiralling down the inside of the wall
    steps = [(C - 4 + i, C - 4) for i in range(8)] + [(C + 4, C - 4 + i) for i in range(1, 9)]
    for i, (x, z) in enumerate(steps[:8]):
        b.set(x, G - 1 - i, z, BRICK)
    # the gate at the bottom: a frame on the floor of the well, the gate filling it
    for x in range(C - 1, C + 2):
        for z in range(C - 1, C + 2):
            b.set(x, G - 8, z, CHISELED)
            b.set(x, G - 7, z, GATE)
    b.point('gate', C, G - 7, C)
    for x in (C - 2, C + 2):
        for z in (C - 2, C + 2):
            b.set(x, G - 7, z, CORAL)
            b.set(x, G - 6, z, CORAL)
    # the coping round the pool, with standing stones
    for x in range(C - 7, C + 8):
        for z in range(C - 7, C + 8):
            d = max(abs(x - C), abs(z - C))
            if 6 <= d <= 7:
                b.set(x, G, z, stone(x, G, z, 2) if h(x, 0, z, 3) < 0.85 else 'minecraft:mossy_cobblestone')
                for y in range(G + 1, G + 6):
                    b.set(x, y, z, AIR)
    for (x, z) in ((C - 7, C - 7), (C + 7, C - 7), (C - 7, C + 7), (C + 7, C + 7)):
        for y in range(G + 1, G + 5):
            b.set(x, y, z, BRICK if y < G + 4 else CHISELED)
        b.set(x, G + 5, z, CORAL)
    # the expedition's diving camp beside it
    for x in range(C + 8, C + 12):
        for z in range(C - 3, C + 4):
            b.set(x, G, z, PLANK)
            for y in range(G + 1, G + 5):
                b.set(x, y, z, AIR)
    b.chest(C + 10, G + 1, C - 2, 'chests/sunken_gate_stores', facing='west')
    b.set(C + 10, G + 1, C, 'minecraft:crafting_table')
    b.set(C + 11, G + 1, C + 2, B('barrel', facing='up', open='false'))
    b.set(C + 9, G + 1, C + 3, B('lantern', hanging='false', waterlogged='false'))
    b.lectern_book(C + 10, G + 1, C + 2, 'west', 'Diving Notes', [
        'DIVING NOTES\n\nThe gate at the bottom of this well opens on a sea with no shore: the Drowned Expanse. It lets '
        'nobody through who could not breathe there. Wear goggles and a rig, do not just carry them.',
        'ABYSSAL GOGGLES\nleather, a Gnashback plate, leather\nglass pane, (empty), glass pane\n\nWithout them you see '
        'a few blocks. With them you also see the surveyors\' glowing route glyphs.',
        'DIVING RIG\ncopper, Gnashback plate, copper\ncopper, bucket, copper\nleather, (empty), leather\n\nThree minutes of '
        'air. It refills in open air, faster in the Expanse, fastest over a Breath Vent (the bubbling columns).',
        'With Curios, goggles go in the head slot and the rig on your back, so your armour stays on.\n\nBelow y 100 the '
        'rig drains three times as fast. Deepwork Station and the wreck hold the parts of a better one.',
        'Ring the bell in each station: if you black out, the tide carries you back to the last bell you rang. What you '
        'drop sinks and waits.\n\nTidewatch Station, where the gate lets out, has an echo sounder for you.'],
        author='Ilsa Vane')
    b.sign(C + 8, G + 1, C + 3, 4, ['Sunken Gate', 'goggles and rig', 'WORN, not carried', 'see the notes'])
    b.meta.update({'kind': 'sunken_gate', 'title': 'The Sunken Gate', 'ground': G})
    return done(b)


# ---------------------------------------------------------------------------------------------- Tidewatch Station
def tidewatch():
    W = L = 41
    C, G = 20, 3
    b = new('drowned_tidewatch', W, 40, L, seed=611)
    D = G + 6                                       # the deck
    # a ring of reef round the station, and the legs
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if 13 < d < 19 and h(x, 0, z, 4) < 0.25:
                reef(b, x, G + 1, z, 4)
            if 15 < d < 19 and h(x, 1, z, 5) < 0.04:
                kelp(b, x, G + 1, z, 6 + int(h(x, 2, z, 6) * 10))
    for k in range(6):
        a = k * math.tau / 6
        lx, lz = round(C + math.cos(a) * 9), round(C + math.sin(a) * 9)
        for y in range(G + 1, D):
            b.set(lx, y, lz, COPPER if y % 3 else CUT_COPPER)
        b.set(lx, G, lz, CHISELED)
    dome_shelter(b, C, C, D, 9, (C + 4, C - 1))
    # inside: the return gate in a frame on the north wall, the bell, the stores, a guide
    gz = C - 6
    for x in range(C - 2, C + 3):
        for y in range(D + 1, D + 5):
            if x in (C - 2, C + 2) or y == D + 4:
                b.set(x, y, gz, CHISELED)
            else:
                furnish(b, x, y, gz, GATE)
    b.point('gate', C, D + 1, gz)
    b.sign(C + 3, D + 1, gz + 1, 8, ['Tide Gate', 'back to the', 'frontier', ''])
    b.dry_furniture.add((C + 3, D + 1, gz + 1))
    furnish(b, C - 4, D + 1, C + 2, bell_block())
    b.point('bell', C - 4, D + 1, C + 2)
    b.sign(C - 4, D + 1, C + 3, 0, ['Tide Bell', 'ring: your shelter', 'sneak-ring: travel', 'to the next bell'])
    b.dry_furniture.add((C - 4, D + 1, C + 3))
    b.chest(C - 1, D + 1, C + 5, 'chests/drowned_tidewatch', facing='north')
    b.dry_furniture.add((C - 1, D + 1, C + 5))
    b.set(C + 1, D + 1, C + 5, 'minecraft:crafting_table')
    b.dry_furniture.add((C + 1, D + 1, C + 5))
    b.lectern_book(C - 5, D + 1, C - 2, 'east', 'Tidewatch Log', [
        'TIDEWATCH STATION\n\nYou are in the air dome. The gate on the north wall goes back. The pool in the floor goes '
        'down into the sea. The chest holds an echo sounder: hold it to see the way to every charted place.',
        'ROUTES\nDeepwork Station: about 360 blocks west, in the kelp. Salvage, and the parts of a deep rig.\n\nThe Choir '
        'Temple: about 390 blocks south-east, deeper. Its pearl clears goggles.',
        'Both are charted for you. Beyond them the old wreck, then the Sunless Vault in the trench, where something '
        'answers a bell. Win a place\'s fight and the way onward is charted.',
        'The posts along the routes carry tide glyphs; through goggles they glow. The bubbling vents on the sea floor '
        'refill a rig. Lanternrays, fed glow berries, lead you to places you have not found.',
        'Below y 100 a plain rig drains three times as fast. Bring the valve from Deepwork and the keel plate from the '
        'wreck together with your rig: that is a deep rig.'], author='Survey Office')
    b.dry_furniture.add((C - 5, D + 1, C - 2))
    for (x, z) in ((C - 6, C - 4), (C + 6, C + 4), (C - 6, C + 4), (C + 6, C - 4)):
        furnish(b, x, D + 1, z, SEA_LANTERN)
    b.point('arrival', C, D + 1, C + 1)
    # the mast: a lattice tower from the crown of the dome nearly to the surface, a beacon at the top
    for y in range(D + 10, 37):
        b.set(C, y, C, COPPER_GRATE if y % 4 else CUT_COPPER)
        if y % 6 == 0:
            for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                b.set(C + dx, y, C + dz, bars())
    b.set(C, 37, C, SEA_LANTERN)
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        b.set(C + dx, 37, C + dz, CORAL)
    b.set(C, 38, C, SEA_LANTERN)
    # route posts out of the station toward Deepwork (west) and the Choir (south-east)
    for k in range(3):
        glyph_post(b, C - 12 - k * 2, G + 1, C)
        glyph_post(b, C + 10 + k * 2, G + 1, C + 8 + k * 2)
    b.meta.update({'kind': 'drowned_station', 'title': 'Tidewatch Station', 'ground': G})
    return done(b)


# ---------------------------------------------------------------------------------------------- Deepwork Station
def deepwork():
    W = L = 51
    C, G = 25, 3
    b = new('drowned_deepwork', W, 38, L, seed=621)
    # the pump hall: a long flooded shed of copper and brine brick, its roof half fallen in
    x0, x1, z0, z1 = C - 12, C + 6, C - 8, C + 8
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            b.set(x, G, z, CUT_COPPER if (x + z) % 2 else BRICK)
            for y in range(G + 1, G + 10):
                edge = x in (x0, x1) or z in (z0, z1)
                if edge:
                    door = (z == C and x == x1 and y < G + 5) or (x == x0 and abs(z - C) <= 1 and y < G + 4)
                    window = y in (G + 5, G + 6) and (x + z) % 4 == 0
                    b.set(x, y, z, WATER if door else bars() if window else (COPPER if y % 4 == 1 else BRICK))
                else:
                    b.set(x, y, z, WATER)
            roof = h(x, 9, z, 7) < 0.6 or x < C - 4
            b.set(x, G + 10, z, CUT_COPPER if roof else WATER)
    # pumps and pipes inside
    for k, px in enumerate(range(x0 + 3, x1 - 1, 5)):
        for y in range(G + 1, G + 5):
            b.set(px, y, C - 5, COPPER)
            b.set(px, y, C + 5, COPPER)
        b.set(px, G + 5, C - 5, COPPER_GRATE)
        b.set(px, G + 5, C + 5, COPPER_GRATE)
        for z in range(C - 4, C + 5):
            b.set(px, G + 7, z, wl('lightning_rod', facing='north', powered='false'))
    b.set(x0 + 2, G + 1, C, VENT)                    # the salvagers' vent still runs
    b.chest(x0 + 1, G + 1, C + 6, 'chests/drowned_deepwork', facing='east')
    b.set(C, G + 9, C, wl('lantern', hanging='true'))
    zone_box = (x0 + 1, G + 1, z0 + 1, x1 - 1, G + 9, z1 - 1)
    spawns = [(x0 + 3, G + 1, C - 3), (x0 + 8, G + 1, C + 3), (x0 + 13, G + 1, C - 2), (x1 - 2, G + 3, C + 4),
              (x0 + 6, G + 4, C), (x1 - 4, G + 2, C - 4)]
    b.zone('hall', 'The Pump Hall', zone_box, spawns, 'drowned_deepwork', kind='ambush', reward='pressure_valve,swim_fins',
           trigger=(x0 + 2, G + 1, z0 + 2, x1 - 2, G + 8, z1 - 2))
    # the crane: a lattice tower east of the hall, its arm out over the sea floor, a diving bell hung from it
    bx, bz = C + 14, C + 9                           # the diving bell hangs here
    tx, tz = C + 21, C + 9
    for y in range(G, G + 29):
        for dx, dz in ((0, 0), (1, 0), (0, 1), (1, 1)):
            b.set(tx + dx, y, tz + dz, COPPER if (y + dx + dz) % 3 else COPPER_GRATE)
    for x in range(bx - 1, tx + 2):
        b.set(x, G + 28, tz, CUT_COPPER)
        b.set(x, G + 28, tz + 1, CUT_COPPER)
    for y in range(G + 19, G + 28):
        b.set(bx, y, bz, chain_y())
    # the bell: an iron shell, open at the bottom; the air inside stays (water does not rise into it)
    by = G + 10                                      # its rim
    for x in range(bx - 4, bx + 5):
        for z in range(bz - 4, bz + 5):
            for y in range(by, by + 9):
                d = math.hypot(x - bx, z - bz)
                top = by + 8
                inner = 3.0 if y < top - 2 else 3.0 - (y - (top - 2)) * 1.0
                if y == top and d <= 2.5:
                    b.set(x, y, z, IRON)
                elif inner - 0.5 <= d <= inner + 0.8 and y < top:
                    b.set(x, y, z, IRON if (y - by) % 3 else 'minecraft:copper_block')
                elif d < inner - 0.5 and y > by and y < top:
                    dry_cell(b, x, y, z)
    # a grating floor ring inside the bell to stand on, leaving the middle open as the way in
    for x in range(bx - 2, bx + 3):
        for z in range(bz - 2, bz + 3):
            if max(abs(x - bx), abs(z - bz)) == 2:
                b.dry.discard((x, by + 1, z))
                b.set(x, by + 1, z, CUT_COPPER)
            elif (x, by + 1, z) in b.dry:
                b.dry.discard((x, by + 1, z))
                b.set(x, by + 1, z, WATER)
    furnish(b, bx + 2, by + 2, bz, bell_block())
    b.point('bell', bx + 2, by + 2, bz)
    furnish(b, bx - 2, by + 2, bz, SEA_LANTERN)
    # salvage yard: crates, an anchor, kelp through the wreckage
    for k in range(10):
        x = C - 18 + int(h(k, 0, 0, 8) * 12)
        z = C + 10 + int(h(k, 1, 0, 8) * 10)
        b.set(x, G + 1, z, B('barrel', facing='up', open='false') if k % 3 else DARK_PLANK)
    for x in range(W):
        for z in range(L):
            if math.hypot(x - C, z - C) > 18 and math.hypot(x - bx, z - bz) > 7 and abs(x - tx) > 2 and h(x, 3, z, 9) < 0.05:
                kelp(b, x, G + 1, z, 8 + int(h(x, 4, z, 9) * 14))
    for k in range(3):
        glyph_post(b, x1 + 5 + k * 3, G + 1, C + 2)
    b.meta.update({'kind': 'drowned_place', 'title': 'Deepwork Station', 'ground': G})
    return done(b)


# ----------------------------------------------------------------------------------------------- the Choir Temple
def choir():
    W = L = 57
    C, G = 28, 3
    b = new('drowned_choir', W, 46, L, seed=631)
    # the nave: 15 wide, 33 long, running north-south; columns, a broken vault
    x0, x1, z0, z1 = C - 8, C + 8, C - 16, C + 16
    for x in range(x0, x1 + 1):
        for z in range(z0, z1 + 1):
            b.set(x, G, z, PRISM if (x + z) % 3 else DARK_PRISM)
            for y in range(G + 1, G + 15):
                if x in (x0, x1) or z in (z0, z1):
                    door = z == z1 and abs(x - C) <= 2 and y < G + 7
                    window = y in range(G + 6, G + 11) and z % 4 == 0 and z not in (z0, z1)
                    b.set(x, y, z, WATER if door else bars() if window else stone(x, y, z, 2))
                else:
                    b.set(x, y, z, WATER)
            arch = G + 15 + int(3 * math.sin(math.pi * (x - x0) / (x1 - x0)))
            broken = h(x // 2, 0, z // 3, 11) < 0.3
            for y in range(G + 15, arch + 1):
                b.set(x, y, z, WATER if broken else (BRICK if y == arch else stone(x, y, z, 3)))
    for z in range(z0 + 4, z1 - 2, 6):
        for x in (C - 5, C + 5):
            for y in range(G + 1, G + 14):
                b.set(x, y, z, PRISM if y % 5 else CHISELED)
            b.set(x, G + 14, z, CORAL)
    # the rose window in the north wall, the altar before it with the chest
    for x in range(x0 + 1, x1):
        for y in range(G + 4, G + 15):
            d = math.hypot(x - C, y - (G + 9))
            if d < 5:
                b.set(x, y, z0, CORAL if d < 1.5 or abs(((math.atan2(y - G - 9, x - C) / math.tau * 8) % 1) - 0.5) < 0.12 else TINT)
    for x in range(C - 2, C + 3):
        b.set(x, G + 1, z0 + 3, CHISELED)
    b.chest(C, G + 2, z0 + 3, 'chests/drowned_choir', facing='south')
    for x in (C - 3, C + 3):
        b.set(x, G + 1, z0 + 3, VENT)
    spawns = [(C - 3, G + 1, z0 + 8), (C + 3, G + 1, z0 + 12), (C, G + 1, z0 + 18), (C - 4, G + 3, z0 + 24), (C + 4, G + 2, z0 + 6),
              (C, G + 5, z0 + 14)]
    b.zone('nave', 'The Drowned Choir', (x0 + 1, G + 1, z0 + 1, x1 - 1, G + 14, z1 - 1), spawns, 'drowned_choir', kind='waves', waves=3,
           reward='choir_pearl', trigger=(x0 + 2, G + 1, z0 + 2, x1 - 2, G + 12, z1 - 4))
    # the bell tower, east of the door: flooded below, an air loft at the top reached from a pool in its floor
    tx0, tz0 = x1 + 2, z1 - 8
    for x in range(tx0, tx0 + 9):
        for z in range(tz0, tz0 + 9):
            b.set(x, G, z, BRICK)
            for y in range(G + 1, G + 34):
                if x in (tx0, tx0 + 8) or z in (tz0, tz0 + 8):
                    door = z == tz0 + 8 and x == tx0 + 4 and y < G + 4
                    b.set(x, y, z, WATER if door else stone(x, y, z, 4))
                else:
                    b.set(x, y, z, WATER)
    loft = G + 26
    for x in range(tx0 + 1, tx0 + 8):
        for z in range(tz0 + 1, tz0 + 8):
            b.set(x, loft, z, CHISELED)
            for y in range(loft + 1, G + 33):
                dry_cell(b, x, y, z)
    for x in range(tx0, tx0 + 9):
        for z in range(tz0, tz0 + 9):
            b.set(x, G + 33, z, BRICK)
    for (x, z) in ((tx0 + 3, tz0 + 3), (tx0 + 4, tz0 + 3), (tx0 + 3, tz0 + 4), (tx0 + 4, tz0 + 4)):
        b.set(x, loft, z, WATER)
    furnish(b, tx0 + 6, loft + 1, tz0 + 6, bell_block())
    b.point('bell', tx0 + 6, loft + 1, tz0 + 6)
    furnish(b, tx0 + 1, loft + 1, tz0 + 1, SEA_LANTERN)
    for y in range(G + 33, G + 38):
        b.set(tx0 + 4, y, tz0 + 4, CHISELED if y < G + 37 else CORAL)
    for x in range(W):
        for z in range(L):
            if (x < x0 - 3 or x > x1 + 11 or z < z0 - 3 or z > z1 + 3) and h(x, 0, z, 12) < 0.2:
                reef(b, x, G + 1, z, 12)
    for k in range(3):
        glyph_post(b, C - 4 - k * 3, G + 1, z0 - 4 - k * 2)
    b.meta.update({'kind': 'drowned_place', 'title': 'The Choir Temple', 'ground': G})
    return done(b)


# ---------------------------------------------------------------------------------------------------- the Wreck
def wreck():
    W = L = 57
    C, G = 28, 4
    b = new('drowned_wreck', W, 30, L, seed=641)
    # the bow half: a hull lying along x, listing to one side, half sunk into the slope; open where it broke
    xa, xb, base = C - 22, C + 2, G - 2
    for x in range(xa, xb + 1):
        t = (x - xa) / (xb - xa)
        half = 2 + 4.5 * min(1.0, t * 3)               # a pointed bow, then the full beam
        for z in range(int(C - half) - 1, int(C + half) + 2):
            dz = (z - C) / half
            if abs(dz) > 1.05:
                continue
            keel = base + int(round(3 * dz * dz))      # a rounded bottom
            lean = int(round(0.25 * (z - C)))
            for y in range(keel, base + 11):
                yy = y + lean
                if abs(dz) > 0.82 or y == keel:
                    gap = y > keel + 1 and h(x, y, z, 13) < 0.1
                    b.set(x, yy, z, WATER if gap else (PLANK if y % 3 else LOG_X))
                elif y == base + 6 and h(x // 2, 0, z, 15) < 0.55:
                    b.set(x, yy, z, PLANK)            # what is left of the deck
                else:
                    b.set(x, yy, z, WATER)
        if x % 4 == 0 and x < xb - 2:                  # ribs where the planking has gone
            for z in range(int(C - half), int(C + half) + 1):
                if abs((z - C) / half) > 0.82:
                    b.set(x, base + 9 + int(round(0.25 * (z - C))), z, LOG_Z)
    # the hold: the Wreckmaw's lair, a deck above it partly gone
    spawns = [(C - 10, G + 1, C), (C - 4, G + 2, C - 2), (C - 15, G + 2, C + 2), (C - 7, G + 4, C + 3)]
    b.zone('hold', 'The Hold of the Long Patience', (C - 20, G - 1, C - 6, C + 1, G + 9, C + 6), spawns, 'drowned_wreck', kind='guardian',
           reward='keel_plate', trigger=(C - 18, G, C - 4, C - 1, G + 7, C + 4))
    # the captain's cabin at the broken end, the chest and a heart of the sea
    for x in range(C - 3, C + 3):
        for z in range(C - 3, C + 4):
            b.set(x, G + 1, z, DARK_PLANK)
    b.chest(C - 1, G + 2, C, 'chests/drowned_wreck', facing='west')
    b.set(C - 2, G + 2, C + 2, wl('lantern', hanging='false'))
    # the fallen masts across the sea floor
    for k, (mx, mz, ang) in enumerate(((C - 14, C, 0.6), (C - 4, C, -0.9))):
        for i in range(22):
            x = round(mx + math.cos(ang) * i)
            z = round(mz + math.sin(ang) * i)
            b.set(x, G + 1 + (1 if i < 4 else 0), z, LOG_X if abs(math.cos(ang)) > 0.7 else LOG_Z)
            if i in (8, 15):
                for j in range(-3, 4):
                    b.set(round(x - math.sin(ang) * j), G + 2, round(z + math.cos(ang) * j), 'minecraft:white_wool' if h(i, j, k, 16) < 0.5
                          else WATER)
    # the stern: capsized a little apart, keel up, trapping air under it (a shelter you enter from below)
    sx0, sx1, sz0, sz1 = C + 8, C + 18, C - 5, C + 5
    top = G + 9
    for x in range(sx0, sx1 + 1):
        for z in range(sz0, sz1 + 1):
            edge = x in (sx0, sx1) or z in (sz0, sz1)
            for y in range(G + 3, top + 1):
                if y == top or edge:
                    b.set(x, y, z, PLANK if (x + y + z) % 4 else LOG_Z)
                elif y >= G + 5:
                    dry_cell(b, x, y, z)
                else:
                    b.set(x, y, z, WATER)
            b.set(x, G + 2, z, LOG_X if edge else WATER)
    # a deck to stand on inside, round the open middle
    for x in range(sx0 + 1, sx1):
        for z in range(sz0 + 1, sz1):
            if x in (sx0 + 1, sx1 - 1) or z in (sz0 + 1, sz1 - 1):
                b.dry.discard((x, G + 5, z))
                b.set(x, G + 5, z, PLANK)
            elif (x, G + 5, z) in b.dry:
                b.dry.discard((x, G + 5, z))
                b.set(x, G + 5, z, WATER)
    for y in range(G + 3, G + 5):
        for x in range(sx0 + 1, sx1):
            for z in range(sz0 + 1, sz1):
                b.set(x, y, z, WATER)
    furnish(b, sx0 + 1, G + 6, sz0 + 1, bell_block())
    b.point('bell', sx0 + 1, G + 6, sz0 + 1)
    furnish(b, sx1 - 1, G + 6, sz1 - 1, SEA_LANTERN)
    for x in range(W):
        for z in range(L):
            if h(x, 5, z, 17) < 0.06 and not (sx0 - 1 <= x <= sx1 + 1 and sz0 - 1 <= z <= sz1 + 1):
                if (x, G + 1, z) not in b.b:
                    b.set(x, G + 1, z, B('seagrass') if h(x, 6, z, 17) < 0.7 else wl('sea_pickle', pickles='3'))
    for k in range(3):
        glyph_post(b, C + 2 + k * 4, G + 1, C - 12 - k * 3)
    b.meta.update({'kind': 'drowned_place', 'title': 'The Wreck of the Long Patience', 'ground': G})
    return done(b)


# ------------------------------------------------------------------------------------------------ the Sunless Vault
def vault():
    W = L = 75
    C, G = 37, 3
    R = 26
    b = new('drowned_vault', W, 44, L, seed=651)
    # the floor of the dome: rings of brine brick and slate, lumen coral inlays
    disc(b, C, C, R + 1, G, lambda x, y, z: CORAL if abs(math.hypot(x - C, z - C) - 12) < 0.5 else stone(x, y, z, 5))
    # the dome: a flooded hemisphere, ribs of chiseled brine, three arched entrances
    for x in range(C - R - 2, C + R + 3):
        for z in range(C - R - 2, C + R + 3):
            for y in range(G + 1, G + R + 10):
                dx, dz = x - C, z - C
                dy = (y - G) * 0.75
                d = math.sqrt(dx * dx + dz * dz + dy * dy)
                if d < R:
                    b.set(x, y, z, WATER)
                elif d < R + 1.5:
                    a = math.atan2(dz, dx)
                    door = any(abs(((a - da + math.pi) % math.tau) - math.pi) < 0.12 for da in (math.pi / 2, math.pi * 7 / 6, -math.pi / 6)) \
                        and y < G + 8
                    oculus = dx * dx + dz * dz < 9
                    rib = abs(((a / math.tau * 12) % 1) - 0.5) > 0.44
                    b.set(x, y, z, WATER if door or oculus else (CHISELED if rib else stone(x, y, z, 6)))
    b.point('centre', C, G + 16, C)
    # six pillars for cover from the lure's flash
    for k in range(6):
        a = k * math.tau / 6
        px, pz = round(C + math.cos(a) * 15), round(C + math.sin(a) * 15)
        for y in range(G + 1, G + 15):
            for ox in (0, 1):
                for oz in (0, 1):
                    b.set(px + ox, y, pz + oz, PRISM if y % 5 else CHISELED)
        b.set(px, G + 15, pz, CORAL)
    # breath vents, so a diver can refill mid-fight (none under the middle)
    for k in range(4):
        a = k * math.tau / 4 + math.pi / 4
        b.set(round(C + math.cos(a) * 20), G, round(C + math.sin(a) * 20), VENT)
    # the abyssal bell on a dais at the south door
    for x in range(C - 2, C + 3):
        for z in range(C + R - 6, C + R - 2):
            b.set(x, G + 1, z, CHISELED)
    b.set(C, G + 2, C + R - 4, bell_block(abyssal=True))
    b.point('bell', C, G + 2, C + R - 4)
    b.sign(C + 1, G + 2, C + R - 4, 8, ['The Abyssal Bell', 'ring it to wake', 'the Deepcaller', 'prepare first'])
    # the antechamber outside the south door: an air room with a pool in its floor, a tide bell, a chest
    ax0, ax1, az0, az1 = C - 5, C + 5, C + R + 3, C + R + 10
    for x in range(ax0, ax1 + 1):
        for z in range(az0, az1 + 1):
            b.set(x, G, z, BRICK)
            b.set(x, G + 3, z, CHISELED if x in (ax0, ax1) or z in (az0, az1) else BRICK)
            for y in range(G + 4, G + 10):
                if x in (ax0, ax1) or z in (az0, az1) or y == G + 9:
                    b.set(x, y, z, stone(x, y, z, 7) if y != G + 6 or (x + z) % 3 else GLASS)
                else:
                    dry_cell(b, x, y, z)
            if not (x in (ax0, ax1) or z in (az0, az1)):
                for y in (G + 1, G + 2):
                    b.set(x, y, z, WATER)
            else:
                for y in (G + 1, G + 2):
                    b.set(x, y, z, BRICK if (x, z) != (C, az0) else WATER)
    for (x, z) in ((C, az0 + 4), (C + 1, az0 + 4), (C, az0 + 5), (C + 1, az0 + 5)):
        b.set(x, G + 3, z, WATER)
    furnish(b, ax0 + 1, G + 4, az0 + 1, bell_block())
    b.point('shelter_bell', ax0 + 1, G + 4, az0 + 1)
    b.chest(ax1 - 1, G + 4, az1 - 1, 'chests/drowned_vault', facing='west')
    b.dry_furniture.add((ax1 - 1, G + 4, az1 - 1))
    furnish(b, ax1 - 1, G + 4, az0 + 1, SEA_LANTERN)
    furnish(b, ax0 + 1, G + 4, az1 - 1, SEA_LANTERN)
    b.lectern_book(C - 2, G + 4, az1 - 1, 'north', 'Last Entry', [
        'THE SUNLESS VAULT\n\nWe rang the bell once. What came up from under the dome was larger than the stern of the '
        'Long Patience, with a lamp on its head.',
        'Do not look into the lamp when it brightens: turn away, or put a pillar between you. When it coils, get off its '
        'line: it cannot stop, and the dome wall stuns it. Strike then.',
        'When the water turns, swim outward. The vents in the floor still breathe; your rig can refill there between '
        'its attacks. Hurt badly, it calls the young eels.'], author='Survey Office')
    b.dry_furniture.add((C - 2, G + 4, az1 - 1))
    # trench detail around the vault: black basalt spires, glow-lichen-like coral
    for x in range(W):
        for z in range(L):
            d = math.hypot(x - C, z - C)
            if d > R + 4 and h(x, 7, z, 18) < 0.02 and not (ax0 - 2 <= x <= ax1 + 2 and az0 - 2 <= z <= az1 + 2):
                for y in range(G + 1, G + 3 + int(h(x, 8, z, 18) * 8)):
                    b.set(x, y, z, 'minecraft:basalt' if y % 4 else CORAL)
    b.meta.update({'kind': 'drowned_vault', 'title': 'The Sunless Vault', 'ground': G})
    return done(b)


if __name__ == '__main__':
    for f in (sunken_gate, tidewatch, deepwork, choir, wreck, vault):
        f().save()
