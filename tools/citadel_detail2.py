"""Grand detail pass for the three citadels: real architecture on top of the base builds.

Everything here is placed with put(), which only writes into empty space (or over small plants) unless forced,
and never overwrites a mod block, a chest or a lectern. So puzzles, seals and loot stay intact.
"""
import math

AIR = 'minecraft:air'
PLANTS = {'minecraft:fern', 'minecraft:grass', 'minecraft:tall_grass', 'minecraft:large_fern', 'minecraft:vine', 'minecraft:azalea',
          'minecraft:flowering_azalea', 'minecraft:cornflower', 'minecraft:blue_orchid', 'minecraft:allium', 'minecraft:azure_bluet',
          'minecraft:oxeye_daisy', 'minecraft:lily_of_the_valley', 'minecraft:poppy', 'minecraft:moss_carpet'}
LOG_Y = {'axis': 'y'}
LANTERN = {'hanging': 'false', 'waterlogged': 'false'}
HANG = {'hanging': 'true', 'waterlogged': 'false'}
CHAIN = {'axis': 'y', 'waterlogged': 'false'}
CAMP = {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}
SLAB = {'type': 'bottom', 'waterlogged': 'false'}
ROD = {'facing': 'up'}


def is_free(g, x, y, z):
    c = g.get(x, y, z)
    return c is None or c[0] == AIR or c[0] in PLANTS


def is_solid(g, x, y, z):
    c = g.get(x, y, z)
    return c is not None and c[0] != AIR and c[0] not in PLANTS


def put(g, x, y, z, name, props=None, force=False):
    c = g.get(x, y, z)
    if c is not None and c[0] != AIR and c[0] not in PLANTS:
        if not force or c[0].startswith('aurelia:') or c[0] in ('minecraft:chest', 'minecraft:lectern'):
            return False
    g.set(x, y, z, name, props)
    return True


def weather(g, rnd, table):
    """Swap a share of plain blocks for worn variants. table: {block: [(variant, chance), ...]}"""
    for key, (name, props, nbt) in list(g.b.items()):
        if name in table and not props:
            roll = rnd.random()
            for variant, chance in table[name]:
                if roll < chance:
                    g.b[key] = (variant, (), nbt)
                    break
                roll -= chance


def stair(facing, half='bottom'):
    return {'facing': facing, 'half': half, 'shape': 'straight', 'waterlogged': 'false'}


# ====================================================================================== ROOTBOUND
def rootbound_grand(g, C, G, rnd):
    r_out = lambda y: 9 + 7 * math.exp(-(y - G) / 7.0)
    MSB, SB, MC = 'minecraft:mossy_stone_bricks', 'minecraft:stone_bricks', 'minecraft:mossy_cobblestone'

    # --- a timber wall-walk inside the curtain wall, on log brackets, with a rail and hanging lanterns
    for x in range(g.W):
        for z in range(g.L):
            d = math.hypot(x - C, z - C)
            if 25.6 <= d < 28.0:
                put(g, x, G + 7, z, 'minecraft:spruce_planks')
                if d < 26.5 and (x + z) % 2 == 0:
                    put(g, x, G + 8, z, 'minecraft:dark_oak_fence')
    for k in range(24):
        a = math.radians(15 * k + 7)
        if abs(math.degrees(a) - 90) < 14:
            continue
        px, pz = C + 25.9 * math.cos(a), C + 25.9 * math.sin(a)
        for y in range(G + 1, G + 7):
            put(g, px, y, pz, 'minecraft:dark_oak_log', LOG_Y)
        if k % 2 == 0:
            lx, lz = C + 27.0 * math.cos(a), C + 27.0 * math.sin(a)
            if is_solid(g, lx, G + 7, lz):
                put(g, lx, G + 6, lz, 'minecraft:lantern', HANG)
    for (lx, face, sup) in ((C + 25, 'west', C + 26), (C - 25, 'east', C - 26)):    # ladders up to the wall-walk
        for y in range(G + 1, G + 8):
            g.set(sup, y, C + 2, 'minecraft:dark_oak_log', LOG_Y)
            g.set(lx, y, C + 2, 'minecraft:ladder', {'facing': face, 'waterlogged': 'false'})

    # --- buttresses outside, arrow slits through the wall
    for k in range(12):
        a = math.radians(30 * k + 15)
        if abs(math.degrees(a) - 90) < 20:
            continue
        for rr, top in ((30.7, G + 6), (31.5, G + 4)):
            x, z = C + rr * math.cos(a), C + rr * math.sin(a)
            for y in range(G + 1, top + 1):
                put(g, x, y, z, MSB if rnd.random() < 0.6 else SB)
            put(g, x, top + 1, z, 'minecraft:mossy_stone_brick_slab', SLAB)
    for k in range(30):
        deg = 12 * k + 6
        if abs(deg - 90) < 16 or abs((deg % 90) - 45) < 11:
            continue
        a = math.radians(deg)
        for rr in (28.2, 29.1, 30.0):
            x, z = C + rr * math.cos(a), C + rr * math.sin(a)
            for y in (G + 4, G + 5):
                c = g.get(x, y, z)
                if c and c[0] in (MSB, MC):
                    g.set(x, y, z, AIR)

    # --- gatehouse: two round turrets with conical roofs and banners
    for sx in (-1, 1):
        tx, tz = C + sx * 7, C + 29
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                d = math.hypot(dx, dz)
                if 1.5 <= d <= 2.6:
                    for y in range(G + 1, G + 14):
                        put(g, tx + dx, y, tz + dz, SB if (y % 4 == 0) else MSB, force=True)
                for k, r in enumerate([3.3, 2.5, 1.6, 0.7]):
                    if d <= r:
                        put(g, tx + dx, G + 14 + k, tz + dz, 'minecraft:dark_oak_planks', force=True)
        put(g, tx, G + 18, tz, 'minecraft:lantern', LANTERN)
        put(g, tx, G + 10, tz + 3, 'minecraft:green_wall_banner', {'facing': 'south'})

    # --- tower interiors: three floors, a ladder, doors onto the wall-walk, furniture
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 20, C + sz * 20
        for fy in (G + 7, G + 14):
            for x in range(tx - 2, tx + 3):
                for z in range(tz - 2, tz + 3):
                    put(g, x, fy, z, 'minecraft:spruce_planks')
        face = 'north' if sz > 0 else 'south'
        for y in range(G + 1, G + 22):
            g.set(tx, y, tz + 2 * sz, 'minecraft:ladder', {'facing': face, 'waterlogged': 'false'})
        for y in (G + 8, G + 9):                                   # doors from the first floor onto the wall-walk
            for k in (0, 1):
                g.set(tx - 3 * sx, y, tz + k * sz, AIR)
                g.set(tx + k * sx, y, tz - 3 * sz, AIR)
        put(g, tx + 2 * sx, G + 1, tz + 2 * sz, 'minecraft:barrel', {'facing': 'up', 'open': 'false'})
        put(g, tx + 2 * sx, G + 1, tz - 2 * sz, 'minecraft:crafting_table')
        put(g, tx + 2 * sx, G + 8, tz + 2 * sz, 'minecraft:bookshelf')
        put(g, tx + 2 * sx, G + 9, tz + 2 * sz, 'minecraft:bookshelf')
        put(g, tx - 2 * sx, G + 8, tz + 2 * sz, 'minecraft:lantern', LANTERN)
        put(g, tx + 2 * sx, G + 15, tz - 2 * sz, 'minecraft:hay_block', LOG_Y)
        put(g, tx + 2 * sx, G + 15, tz - 1 * sz, 'minecraft:hay_block', LOG_Y)
        put(g, tx - 2 * sx, G + 15, tz - 2 * sz, 'minecraft:lantern', LANTERN)

    # --- courtyard: lamp posts, a ring path, a lily pond, a berry garden, an idol of the Warden, root arches
    for z in (C + 18, C + 22):
        for x in (C - 4, C + 4):
            put(g, x, G + 1, z, 'minecraft:mossy_cobblestone_wall')
            put(g, x, G + 2, z, 'minecraft:mossy_cobblestone_wall')
            put(g, x, G + 3, z, 'minecraft:lantern', LANTERN)
    for x in range(g.W):
        for z in range(g.L):
            d = math.hypot(x - C, z - C)
            c = g.get(x, G, z)
            if 21.6 <= d <= 23.2 and c and c[0] in ('minecraft:moss_block', 'minecraft:grass_block', 'minecraft:podzol') and g.get(x, G + 1, z) is None:
                g.set(x, G, z, 'minecraft:dirt_path' if rnd.random() < 0.8 else 'minecraft:coarse_dirt')
    px, pz = C + 13, C + 17
    for x in range(px - 5, px + 6):
        for z in range(pz - 5, pz + 6):
            d = math.hypot(x - px, z - pz)
            c = g.get(x, G, z)
            if d <= 3.3 and c and not c[0].startswith('aurelia:'):
                g.set(x, G, z, 'minecraft:water', {'level': '0'})
                if is_free(g, x, G + 1, z):
                    g.set(x, G + 1, z, 'minecraft:lily_pad' if rnd.random() < 0.3 else AIR)
            elif d <= 4.3 and c and rnd.random() < 0.6 and is_free(g, x, G + 1, z):
                g.set(x, G, z, MC)
    gx0, gz0 = C - 16, C - 17
    for x in range(gx0, gx0 + 6):
        for z in range(gz0, gz0 + 6):
            edge = x in (gx0, gx0 + 5) or z in (gz0, gz0 + 5)
            if not is_free(g, x, G + 1, z) or not g.get(x, G, z):
                continue
            if edge:
                if not (x == gx0 + 2 and z == gz0 + 5):
                    put(g, x, G + 1, z, 'minecraft:dark_oak_fence')
            else:
                g.set(x, G, z, 'minecraft:rooted_dirt')
                put(g, x, G + 1, z, 'minecraft:sweet_berry_bush', {'age': str(rnd.choice([1, 2, 3, 3]))})
    ix, iz = C + 12, C - 16
    for dx in (-1, 0, 1):
        for dz in (-1, 0, 1):
            put(g, ix + dx, G + 1, iz + dz, MSB)
    for y in range(G + 2, G + 5):
        put(g, ix, y, iz, 'minecraft:stripped_dark_oak_log', LOG_Y)
    put(g, ix, G + 5, iz, 'minecraft:bone_block', LOG_Y)
    put(g, ix, G + 4, iz + 1, 'minecraft:verdant_froglight', LOG_Y)
    for sx in (-1, 1):
        put(g, ix + sx, G + 6, iz, 'minecraft:dark_oak_fence')
        put(g, ix + sx, G + 7, iz, 'minecraft:dark_oak_fence')
        put(g, ix + 2 * sx, G + 7, iz, 'minecraft:dark_oak_fence')
        put(g, ix + sx, G + 3, iz, 'minecraft:dark_oak_fence')
    for az in (C + 20, C + 24):
        for i in range(0, 181, 5):
            a = math.radians(i)
            put(g, C + 5.6 * math.cos(a), G + 1 + 5.6 * math.sin(a), az, 'minecraft:dark_oak_wood', LOG_Y)

    # --- the trunk's face: a carved door frame with lanterns, and two glowing eyes above it
    for sx in (-1, 1):
        for y in range(G + 1, G + 8):
            put(g, C + sx * 3, y, C + 15, 'minecraft:stripped_dark_oak_log', LOG_Y, force=True)
        put(g, C + sx * 3, G + 8, C + 16, 'minecraft:stripped_dark_oak_log', {'axis': 'z'}, force=True)
        put(g, C + sx * 3, G + 7, C + 16, 'minecraft:lantern', HANG, force=True)
        for z in range(C + 6, C + 14):
            if is_solid(g, C + sx * 2, G + 11, z) and is_free(g, C + sx * 2, G + 11, z + 1):
                g.set(C + sx * 2, G + 11, z, 'minecraft:shroomlight')
                g.set(C + sx * 2, G + 12, z, 'minecraft:stripped_dark_oak_log', {'axis': 'x'})
                break
    for x in range(C - 3, C + 4):
        put(g, x, G + 8, C + 15, 'minecraft:stripped_dark_oak_log', {'axis': 'x'}, force=True)

    # --- the canopy: glow-berry vines under the boughs, bee nests, three lookout platforms off the terrace
    for (x, y, z), (name, _, _) in list(g.b.items()):
        open_cell = lambda c: c is None or c[0] == AIR or 'leaves' in c[0]
        if name in ('minecraft:dark_oak_wood', 'minecraft:dark_oak_log') and y >= G + 28 and rnd.random() < 0.05 and open_cell(g.get(x, y - 1, z)):
            ln = rnd.randint(2, 6)
            for k in range(1, ln + 1):
                if not open_cell(g.get(x, y - k, z)):
                    break
                tip = (k == ln) or not open_cell(g.get(x, y - k - 1, z))
                berries = 'true' if rnd.random() < 0.45 else 'false'
                if tip:
                    g.set(x, y - k, z, 'minecraft:cave_vines', {'age': '25', 'berries': berries})
                else:
                    g.set(x, y - k, z, 'minecraft:cave_vines_plant', {'berries': berries})
    for (deg, yy) in ((40, G + 22), (170, G + 26), (290, G + 20)):
        a = math.radians(deg)
        rr = r_out(yy) + 0.8
        face = ('east' if math.cos(a) > 0 else 'west') if abs(math.cos(a)) > abs(math.sin(a)) else ('south' if math.sin(a) > 0 else 'north')
        put(g, C + rr * math.cos(a), yy, C + rr * math.sin(a), 'minecraft:bee_nest', {'facing': face, 'honey_level': '3'})
    for deg in (30, 150, 270):
        a = math.radians(deg)
        cx, cz = C + 20 * math.cos(a), C + 20 * math.sin(a)
        for i in range(13, 20):                                      # plank bridge from the terrace
            for w in (-1, 0, 1):
                put(g, C + i * math.cos(a) - w * math.sin(a), G + 35, C + i * math.sin(a) + w * math.cos(a), 'minecraft:spruce_planks')
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                d = math.hypot(dx, dz)
                if d <= 4.2:
                    put(g, cx + dx, G + 35, cz + dz, 'minecraft:spruce_planks', force=True)
                    for k in (1, 2, 3):
                        c = g.get(cx + dx, G + 35 + k, cz + dz)
                        if c and 'leaves' in c[0]:
                            g.set(cx + dx, G + 35 + k, cz + dz, AIR)
                    if d > 3.3 and (dx + dz) % 2 == 0:
                        put(g, cx + dx, G + 36, cz + dz, 'minecraft:dark_oak_fence')
                if d <= 3.2:
                    put(g, cx + dx, G + 39, cz + dz, 'minecraft:dark_oak_slab', SLAB, force=True)
        for (ox, oz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            for k in (1, 2, 3):
                put(g, cx + ox, G + 35 + k, cz + oz, 'minecraft:dark_oak_fence', force=True)
        put(g, cx, G + 38, cz, 'minecraft:lantern', HANG, force=True)
        put(g, cx + 1, G + 36, cz + 1, 'minecraft:barrel', {'facing': 'up', 'open': 'false'}, force=True)

    weather(g, rnd, {SB: [('minecraft:cracked_stone_bricks', 0.12), (MSB, 0.15)],
                     MSB: [('minecraft:cracked_stone_bricks', 0.06), (SB, 0.08), (MC, 0.05)],
                     'minecraft:dark_oak_planks': [('minecraft:spruce_planks', 0.15)]})


# ====================================================================================== STORMWATCH
def stormwatch_grand(g, C, G, rnd):
    r_c = lambda h: 9 - 6 * (h / 60.0) ** 1.15
    QB, QC, QS = 'minecraft:quartz_bricks', 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz'
    QP = 'minecraft:quartz_pillar'
    sats = [(C + sx * 21, C + sz * 21, sx, sz) for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]]

    # --- weathered copper roofs on every spire, with a bright band
    for (x, y, z), (name, props, nbt) in list(g.b.items()):
        if name in (QB, QC):
            if y >= G + 49 and math.hypot(x - C, z - C) <= 7:
                g.b[(x, y, z)] = ('minecraft:cut_copper' if y % 6 == 0 else 'minecraft:oxidized_cut_copper' if rnd.random() < 0.8 else 'minecraft:weathered_cut_copper', (), nbt)
            else:
                for (cx, cz, _, _) in sats:
                    if y >= G + 29 and math.hypot(x - cx, z - cz) <= 5.5:
                        g.b[(x, y, z)] = ('minecraft:cut_copper' if y % 6 == 0 else 'minecraft:oxidized_cut_copper' if rnd.random() < 0.8 else 'minecraft:weathered_cut_copper', (), nbt)

    # --- arches under the four bridges, end-rod lamps along them
    for (cx, cz, sx, sz) in sats:
        steps = int(math.hypot(cx - C, cz - C))
        nx, nz = -sz / math.sqrt(2), sx / math.sqrt(2)
        for i in range(10, steps - 4):
            t = i / steps
            bx, bz = C + (cx - C) * t, C + (cz - C) * t
            u = (i - 10) / float(steps - 15)
            depth = 2 + int(round(6 * (2 * u - 1) ** 2))
            for w in (-1, 0, 1):
                for k in range(1, depth + 1):
                    put(g, bx + nx * w, G + 19 - k, bz + nz * w, QB if k < depth else QC)
            if i % 4 == 0:
                for w in (-2, 2):
                    if is_solid(g, bx + nx * w, G + 20, bz + nz * w):
                        put(g, bx + nx * w, G + 21, bz + nz * w, 'minecraft:end_rod', ROD)
        face = 'north' if sz > 0 else 'south'
        put(g, cx, G + 11, cz - sz * 5, 'minecraft:light_blue_wall_banner', {'facing': face})
        put(g, cx, G + 17, cz - sz * 5, 'minecraft:light_blue_wall_banner', {'facing': face})

    # --- stained glass rings up the central spire
    for h in (16, 26, 38, 46):
        r = r_c(h)
        for k in range(8):
            a = math.radians(45 * k + (0 if h < 30 else 22.5))
            x, z = C + round(r * math.cos(a)), C + round(r * math.sin(a))
            for dy in (0, 1):
                c = g.get(x, G + 1 + h + dy, z)
                if c and c[0] in (QB, QC):
                    g.set(x, G + 1 + h + dy, z, 'minecraft:cyan_stained_glass' if k % 2 else 'minecraft:white_stained_glass')

    # --- plaza: lamp posts, two reflecting pools, two winged statues
    for k in range(12):
        deg = 30 * k + 15
        if abs(deg - 90) < 20:
            continue
        a = math.radians(deg)
        x, z = C + 20.4 * math.cos(a), C + 20.4 * math.sin(a)
        if g.get(x, G, z):
            for y in (G + 1, G + 2, G + 3):
                put(g, x, y, z, QP, LOG_Y)
            put(g, x, G + 4, z, 'minecraft:sea_lantern')
            put(g, x, G + 5, z, 'minecraft:end_rod', ROD)
    for sx in (-1, 1):
        for x in range(C + sx * 6, C + sx * 10, sx):
            for z in range(C + 16, C + 21):
                edge = x in (C + sx * 6, C + sx * 9) or z in (C + 16, C + 20)
                c = g.get(x, G, z)
                if not c or c[0].startswith('aurelia:'):
                    continue
                if edge:
                    g.set(x, G, z, QC)
                else:
                    g.set(x, G, z, 'minecraft:water', {'level': '0'})
                    g.set(x, G - 1, z, 'minecraft:sea_lantern')
        px, pz = C + sx * 16, C + 5
        for dx in (-1, 0, 1):
            for dz in (-1, 0, 1):
                put(g, px + dx, G + 1, pz + dz, QB)
        put(g, px, G + 2, pz, QC)
        for y in range(G + 3, G + 7):
            put(g, px, y, pz, QP, LOG_Y)
        put(g, px, G + 7, pz, QC)
        put(g, px, G + 8, pz, 'minecraft:end_rod', ROD)
        for k, dz in enumerate((1, 2, 3)):
            for s2 in (-1, 1):
                put(g, px, G + 5 + k, pz + s2 * dz, QS)
                put(g, px, G + 6 + k, pz + s2 * dz, 'minecraft:quartz_slab', SLAB)

    # --- amethyst veins in the crag, three tethered islets with pavilions
    for (x, y, z), (name, props, nbt) in list(g.b.items()):
        if name == 'minecraft:calcite' and y < G - 1 and rnd.random() < 0.05:
            if any(g.get(x + dx, y, z + dz) is None for (dx, dz) in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                g.b[(x, y, z)] = ('minecraft:amethyst_block', (), nbt)
    for (deg, yy) in ((0, G + 11), (180, G + 14), (270, G + 12)):
        a = math.radians(deg)
        cx, cz = C + 26.5 * math.cos(a), C + 26.5 * math.sin(a)
        for dy in range(0, 5):
            rr = 3.3 - dy * 0.7
            for dx in range(-4, 5):
                for dz in range(-4, 5):
                    if math.hypot(dx, dz) <= rr:
                        if dy == 0:
                            put(g, cx + dx, yy, cz + dz, 'minecraft:grass_block', {'snowy': 'false'}, force=True)
                        else:
                            put(g, cx + dx, yy - dy, cz + dz, 'minecraft:calcite' if rnd.random() < 0.8 else 'minecraft:amethyst_block', force=True)
        for (ox, oz) in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            for k in (1, 2, 3):
                put(g, cx + ox, yy + k, cz + oz, QP, LOG_Y, force=True)
        for dx in range(-3, 4):
            for dz in range(-3, 4):
                if math.hypot(dx, dz) <= 3.3:
                    put(g, cx + dx, yy + 4, cz + dz, 'minecraft:quartz_slab', SLAB, force=True)
        put(g, cx, yy + 3, cz, 'minecraft:sea_lantern', force=True)
        put(g, cx, yy + 1, cz, 'minecraft:amethyst_block', force=True)
        for y in range(yy - 5, G, -1):
            if not put(g, cx, y, cz, 'minecraft:chain', CHAIN):
                break

    weather(g, rnd, {QB: [('minecraft:quartz_block', 0.12), ('minecraft:polished_diorite', 0.04)],
                     QS: [('minecraft:quartz_block', 0.10), ('minecraft:polished_diorite', 0.04)],
                     'minecraft:calcite': [('minecraft:diorite', 0.08)]})


# ====================================================================================== ASHEN
def ashen_grand(g, C, rnd, K1):
    K0 = C - 12
    PB, CPB = 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks'
    WALL = 'minecraft:polished_blackstone_brick_wall'
    CHI = 'minecraft:chiseled_polished_blackstone'

    # --- every keep wall: stepped buttress piers and furnace windows that glow from inside
    faces = [('z', K1, 1), ('z', K0, -1), ('x', K1, 1), ('x', K0, -1)]

    def at(axis, coord, out, off, depth):
        return (C + off, coord + out * depth) if axis == 'z' else (coord + out * depth, C + off)
    for (axis, coord, out) in faces:
        for off in (-9, -4, 4, 9):
            for depth, top in ((1, 31), (2, 22)):
                x, z = at(axis, coord, out, off, depth)
                for y in range(10, top + 1):
                    put(g, x, y, z, PB if y % 7 else CHI)
                put(g, x, top + 1, z, WALL)
        for off, ys in ((-7, (22, 23, 24)), (7, (22, 23, 24)), (-7, (29, 30, 31)), (0, (29, 30, 31)), (7, (29, 30, 31))):
            for y in ys:
                x, z = at(axis, coord, out, off, 0)
                xi, zi = at(axis, coord, out, off, -1)
                g.set(x, y, z, 'minecraft:orange_stained_glass')
                g.set(xi, y, zi, 'minecraft:shroomlight')

    # --- the gate: a chiseled frame, fang spikes above, lanterns under the lintel
    for sx in (-3, 3):
        for y in range(10, 18):
            put(g, C + sx, y, K1 + 1, CHI, force=True)
        put(g, C + sx, 18, K1 + 1, WALL)
        put(g, C + sx, 19, K1 + 1, WALL)
    for x in range(C - 2, C + 3):
        put(g, x, 17, K1 + 1, CHI, force=True)
        put(g, x, 18, K1 + 1, WALL if x != C else CHI)
    put(g, C, 19, K1 + 1, 'minecraft:soul_lantern', LANTERN)
    for sx in (-2, 2):
        put(g, C + sx, 16, K1 + 1, 'minecraft:soul_lantern', HANG)

    # --- battlement spikes on the keep roof, pyramid roofs and hanging lanterns on the towers
    for x in range(K0, K1 + 1):
        for z in range(K0, K1 + 1):
            if (x in (K0, K1) or z in (K0, K1)) and is_solid(g, x, 39, z):
                put(g, x, 40, z, WALL)
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 12, C + sz * 12
        for k, half in enumerate([3, 3, 2, 2, 1, 1]):
            for x in range(tx - half, tx + half + 1):
                for z in range(tz - half, tz + half + 1):
                    put(g, x, 50 + k, z, 'minecraft:deepslate_tiles')
        for (bx, bz) in ((tx + 4 * sx, tz), (tx, tz + 4 * sz)):
            put(g, bx, 47, bz, WALL)
            for y in (46, 45, 44):
                put(g, bx, y, bz, 'minecraft:chain', CHAIN)
            put(g, bx, 43, bz, 'minecraft:soul_lantern', HANG)

    # --- the plateau: skulls on pikes, bone piles, basalt columns
    def ground_y(x, z):
        for y in range(13, 9, -1):
            if is_free(g, x, y, z) and is_free(g, x, y + 1, z) and is_free(g, x, y + 2, z) and is_solid(g, x, y - 1, z):
                return y
        return None
    for _ in range(40):
        a, r = rnd.uniform(0, 6.28), rnd.uniform(14.5, 20)
        x, z = int(round(C + r * math.cos(a))), int(round(C + r * math.sin(a)))
        if abs(x - C) < 5 and z > C:
            continue
        y = ground_y(x, z)
        if y is None:
            continue
        roll = rnd.random()
        if roll < 0.4:
            put(g, x, y, z, WALL)
            put(g, x, y + 1, z, WALL)
            put(g, x, y + 2, z, 'minecraft:skeleton_skull', {'rotation': str(rnd.randint(0, 15))})
        elif roll < 0.65:
            put(g, x, y, z, 'minecraft:bone_block', {'axis': rnd.choice(['x', 'y', 'z'])})
            if rnd.random() < 0.5:
                put(g, x + 1, y, z, 'minecraft:bone_block', {'axis': rnd.choice(['x', 'z'])})
        else:
            for (dx, dz) in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0)):
                yy = ground_y(x + dx, z + dz)
                if yy is not None and rnd.random() < 0.8:
                    for k in range(rnd.randint(1, 5)):
                        put(g, x + dx, yy + k, z + dz, 'minecraft:basalt', LOG_Y)

    # --- inside the hall: colonnades, lava under glass along the walls, banners, a throne
    for sx in (-8, 8):
        for dz in (-8, -4, 4, 8):
            for y in range(10, 26):
                put(g, C + sx, y, C + dz, CHI if y in (10, 17, 25) else 'minecraft:polished_blackstone')
    for sx in (-9, 9):
        for z in range(C - 9, C + 10):
            c = g.get(C + sx, 9, z)
            if c and c[0] in ('minecraft:deepslate_tiles', 'minecraft:polished_blackstone') and is_free(g, C + sx, 10, z):
                g.set(C + sx, 9, z, 'minecraft:orange_stained_glass')
                g.set(C + sx, 8, z, 'minecraft:lava', {'level': '0'})
    for dz in (-6, 6):
        put(g, C + 10, 19, C + dz, 'minecraft:red_wall_banner', {'facing': 'west'})
        put(g, C - 10, 19, C + dz, 'minecraft:red_wall_banner', {'facing': 'east'})
    for x in range(C + 8, C + 11):                                  # the throne, against the east wall
        for z in range(C - 2, C + 3):
            put(g, x, 10, z, PB)
    put(g, C + 10, 11, C, 'minecraft:polished_blackstone_stairs', stair('east'))
    for y in range(11, 18):
        g.set(C + 11, y, C, 'minecraft:crying_obsidian')
    for dz in (-1, 1):
        put(g, C + 10, 11, C + dz, WALL)
        put(g, C + 10, 12, C + dz, WALL)
        put(g, C + 9, 11, C + 2 * dz, 'minecraft:soul_campfire', CAMP)
        g.set(C + 11, 16, C + dz, 'minecraft:gilded_blackstone')

    weather(g, rnd, {PB: [(CPB, 0.07), ('minecraft:polished_blackstone', 0.06), ('minecraft:gilded_blackstone', 0.015)],
                     'minecraft:blackstone': [('minecraft:gilded_blackstone', 0.01), ('minecraft:deepslate', 0.05)]})
