"""Detail passes for the three citadels. Each takes the Grid and adds architecture; guards are placed afterwards."""
import math

AIR = 'minecraft:air'
VINE_FACE = {(1, 0): 'west', (-1, 0): 'east', (0, 1): 'north', (0, -1): 'south'}
FLOWER_NAMES = ['minecraft:cornflower', 'minecraft:blue_orchid', 'minecraft:allium', 'minecraft:azure_bluet', 'minecraft:oxeye_daisy',
                'minecraft:lily_of_the_valley', 'minecraft:poppy']
LEAF = {'persistent': 'true', 'distance': '7', 'waterlogged': 'false'}
LANTERN = {'hanging': 'false', 'waterlogged': 'false'}
OPPOSITE = {'east': 'west', 'west': 'east', 'south': 'north', 'north': 'south'}
CAMP = {'facing': 'north', 'lit': 'true', 'signal_fire': 'false', 'waterlogged': 'false'}


def vine_pass(g, rnd, names, chance, ymin=0, ymax=999):
    for (x, y, z), (name, _, _) in list(g.b.items()):
        if name not in names or not (ymin <= y <= ymax) or rnd.random() > chance:
            continue
        for (dx, dz), face in VINE_FACE.items():
            if g.get(x + dx, y, z + dz) is None:
                for k in range(rnd.randint(3, 10)):
                    if g.get(x + dx, y - k, z + dz) is None:
                        g.set(x + dx, y - k, z + dz, 'minecraft:vine', {face: 'true'})
                    else:
                        break
                break


def spiral_stair(g, cx, cz, y0, y1, r_fn, block, props, theta0, width=2, post_every=0):
    """A spiral stair climbing one block per step; r_fn(y) is the radius at height y."""
    th, y, n = theta0, y0, 0
    while y <= y1:
        r = r_fn(y)
        th += 1.0 / max(r, 5)
        tx, tz = -math.sin(th), math.cos(th)
        travel = ('east' if tx > 0 else 'west') if abs(tx) > abs(tz) else ('south' if tz > 0 else 'north')
        for w in range(width):
            wx, wz = cx + (r + w) * math.cos(th), cz + (r + w) * math.sin(th)
            g.set(wx, y, wz, block, dict(props, facing=travel))
            g.set(wx, y - 1, wz, 'minecraft:dark_oak_planks')
        if post_every and n % post_every == 0:
            ox, oz = cx + (r + width + 0.6) * math.cos(th), cz + (r + width + 0.6) * math.sin(th)
            g.set(ox, y, oz, 'minecraft:dark_oak_fence')
            g.set(ox, y + 1, oz, 'minecraft:lantern', LANTERN)
        y += 1
        n += 1


def rootbound_detail(g, C, G, rnd):
    r_out = lambda y: 9 + 7 * math.exp(-(y - G) / 7.0)
    # branch bridges from each tower to the trunk, with fences and lanterns
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 20, C + sz * 20
        dx, dz = C - tx, C - tz
        dist = math.hypot(dx, dz)
        nx, nz = -dz / dist, dx / dist
        for i in range(3, int(dist - 9)):
            t = i / dist
            bx, bz = tx + dx * t, tz + dz * t
            for w in (-1, 0, 1):
                g.set(bx + nx * w, G + 17, bz + nz * w, 'minecraft:dark_oak_planks')
            if i % 3 == 0:
                for w in (-2, 2):
                    g.set(bx + nx * w, G + 18, bz + nz * w, 'minecraft:dark_oak_fence')
                    if i % 6 == 0:
                        g.set(bx + nx * w, G + 19, bz + nz * w, 'minecraft:lantern', LANTERN)
            if i in (3, 4, 5):
                for k in range(1, 4):
                    for w in (-1, 0, 1):
                        g.set(bx + nx * w, G + 17 + k, bz + nz * w, AIR)
            if i % 4 == 0:
                g.set(bx, G + 16, bz, 'minecraft:stripped_dark_oak_log', {'axis': 'y'})
    # spiral stair around the trunk to a railed terrace
    spiral_stair(g, C, C, G + 1, G + 34, lambda y: r_out(y) + 2.2, 'minecraft:dark_oak_stairs',
                 {'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'}, math.radians(200), 2, 7)
    for x in range(C - 16, C + 17):
        for z in range(C - 16, C + 17):
            d = math.hypot(x - C, z - C)
            if r_out(G + 35) + 1.0 <= d <= r_out(G + 35) + 5.5:
                g.set(x, G + 35, z, 'minecraft:dark_oak_planks')
            if abs(d - (r_out(G + 35) + 5.5)) < 0.6 and int(d * 3 + x) % 3 == 0:
                g.set(x, G + 36, z, 'minecraft:dark_oak_fence')
    # banners and a raised portcullis
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        tx, tz = C + sx * 20, C + sz * 20
        for y in (G + 12, G + 16):
            g.set(tx + 4 * sx, y, tz, 'minecraft:green_wall_banner', {'facing': 'east' if sx > 0 else 'west'})
            g.set(tx, y, tz + 4 * sz, 'minecraft:green_wall_banner', {'facing': 'south' if sz > 0 else 'north'})
    for x in range(C - 3, C + 4):
        g.set(x, G + 7, C + 28, 'minecraft:iron_bars', {'north': 'false', 'south': 'false', 'east': 'true', 'west': 'true', 'waterlogged': 'false'})
    # fountain, garden beds, ruined pillars
    fx, fz = C - 12, C + 17
    for x in range(fx - 3, fx + 4):
        for z in range(fz - 3, fz + 4):
            d = math.hypot(x - fx, z - fz)
            if d <= 3.2:
                g.set(x, G, z, 'minecraft:water' if d <= 2.2 else 'minecraft:mossy_stone_bricks', {'level': '0'} if d <= 2.2 else None)
                if d > 2.2:
                    g.set(x, G + 1, z, 'minecraft:mossy_stone_bricks')
    for k in range(3):
        g.set(fx, G + 1 + k, fz, 'minecraft:stripped_dark_oak_log', {'axis': 'y'})
    g.set(fx, G + 4, fz, 'minecraft:shroomlight')
    for x in range(C - 29, C + 30):
        for z in range(C - 29, C + 30):
            d = math.hypot(x - C, z - C)
            c = g.get(x, G, z)
            if 17 < d < 27 and c and c[0] in ('minecraft:moss_block', 'minecraft:grass_block', 'minecraft:podzol') and g.get(x, G + 1, z) is None:
                r = rnd.random()
                if r < 0.07:
                    g.set(x, G + 1, z, rnd.choice(FLOWER_NAMES))
                elif r < 0.12:
                    g.set(x, G + 1, z, rnd.choice(['minecraft:azalea', 'minecraft:flowering_azalea']))
                elif r < 0.17:
                    g.set(x, G + 1, z, 'minecraft:fern')
                elif r < 0.20 and g.get(x, G + 2, z) is None:
                    g.set(x, G + 1, z, 'minecraft:large_fern', {'half': 'lower'})
                    g.set(x, G + 2, z, 'minecraft:large_fern', {'half': 'upper'})
    for _ in range(6):
        a = rnd.uniform(0, 6.28)
        px, pz = C + 21 * math.cos(a), C + 21 * math.sin(a)
        if abs(pz - (C + 25)) > 4 or abs(px - C) > 6:
            for k in range(rnd.randint(2, 5)):
                g.set(px, G + 1 + k, pz, rnd.choice(['minecraft:mossy_stone_bricks', 'minecraft:stone_bricks', 'minecraft:mossy_cobblestone']))
    # the trunk hall: vaulted ribs, hanging roots, lanterns, a mossy floor
    for k in range(8):
        a = math.radians(45 * k + 22)
        for r in range(7, 0, -1):
            g.set(C + r * math.cos(a), G + 13 + (7 - r), C + r * math.sin(a), 'minecraft:stripped_dark_oak_log', {'axis': 'y'})
    for _ in range(40):
        x, z = C + rnd.randint(-6, 6), C + rnd.randint(-6, 6)
        for y in range(G + 19, G + 13, -1):
            above, here = g.get(x, y + 1, z), g.get(x, y, z)
            if math.hypot(x - C, z - C) <= 5 and above and above[0] != AIR and here and here[0] == AIR:
                g.set(x, y, z, 'minecraft:hanging_roots', {'waterlogged': 'false'})
                break
    for (lx, lz) in [(-5, -3), (5, -3), (-5, 3), (5, 3), (0, 4), (0, -4)]:
        for y in range(G + 12, G + 8, -1):
            above = g.get(C + lx, y + 1, C + lz)
            if above and above[0] != AIR:
                g.set(C + lx, y, C + lz, 'minecraft:lantern', {'hanging': 'true', 'waterlogged': 'false'})
                break
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            if math.hypot(x - C, z - C) < 5.5 and g.get(x, G + 1, z) is None and rnd.random() < 0.35:
                g.set(x, G + 1, z, 'minecraft:moss_carpet')
    vine_pass(g, rnd, {'minecraft:mossy_stone_bricks', 'minecraft:mossy_cobblestone', 'minecraft:dark_oak_log', 'minecraft:moss_block'}, 0.05, G + 4, G + 40)


def stormwatch_detail(g, C, G, rnd):
    r_c = lambda h: 9 - 6 * (h / 60.0) ** 1.15
    QB, QC, QS = 'minecraft:quartz_bricks', 'minecraft:chiseled_quartz_block', 'minecraft:smooth_quartz'
    for k in range(8):                                        # buttress fins
        a = math.radians(45 * k + 22.5)
        for h in range(0, 28):
            r = r_c(h) + 1.0
            g.set(C + r * math.cos(a), G + 1 + h, C + r * math.sin(a), 'minecraft:quartz_pillar', {'axis': 'y'})
        r = r_c(28) + 1.0
        g.set(C + r * math.cos(a), G + 29, C + r * math.sin(a), QC)
    h = 36                                                    # balcony ring
    for x in range(C - 12, C + 13):
        for z in range(C - 12, C + 13):
            d = math.hypot(x - C, z - C)
            if r_c(h) + 0.6 <= d <= r_c(h) + 3.2:
                g.set(x, G + 1 + h, z, QS)
            if abs(d - (r_c(h) + 3.2)) < 0.55:
                if (x + z) % 2 == 0:
                    g.set(x, G + 2 + h, z, QC)
                else:
                    g.set(x, G + 2 + h, z, 'minecraft:quartz_pillar', {'axis': 'y'})
    for k in range(8):
        a = math.radians(45 * k)
        g.set(C + (r_c(h) + 3.2) * math.cos(a), G + 3 + h, C + (r_c(h) + 3.2) * math.sin(a), 'minecraft:sea_lantern')
    for y_h in (12, 22):                                      # banners
        r = round(r_c(y_h))
        for (dx, dz, face) in ((0, 1, 'south'), (0, -1, 'north'), (1, 0, 'east'), (-1, 0, 'west')):
            if (dx, dz) != (0, 1) or y_h != 12:
                g.set(C + dx * (r + 1), G + 1 + y_h, C + dz * (r + 1), 'minecraft:light_blue_wall_banner', {'facing': face})
    fx, fz = C, C + 14                                        # plaza fountain
    for x in range(fx - 4, fx + 5):
        for z in range(fz - 4, fz + 5):
            d = math.hypot(x - fx, z - fz)
            if d <= 4:
                if d <= 3:
                    g.set(x, G, z, 'minecraft:water', {'level': '0'})
                else:
                    g.set(x, G, z, QB)
                    g.set(x, G + 1, z, QB)
    for k in range(4):
        g.set(fx, G + 1 + k, fz, 'minecraft:quartz_pillar', {'axis': 'y'})
    g.set(fx, G + 5, fz, 'minecraft:sea_lantern')
    for x in range(C - 26, C + 27):                           # hedges and flower beds
        for z in range(C - 26, C + 27):
            d = math.hypot(x - C, z - C)
            c = g.get(x, G, z)
            if 22 <= d <= 23.4 and c and not (z > C + 19 and abs(x - C) < 6):
                g.set(x, G + 1, z, 'minecraft:azalea_leaves', LEAF)
                if rnd.random() < 0.5:
                    g.set(x, G + 2, z, 'minecraft:azalea_leaves', LEAF)
            elif 18 <= d <= 21 and c and c[0] == 'minecraft:smooth_quartz' and g.get(x, G + 1, z) is None and rnd.random() < 0.10:
                g.set(x, G + 1, z, rnd.choice(FLOWER_NAMES))
    for (bx, bz, face) in [(C - 10, C + 4, 'east'), (C + 10, C + 4, 'west'), (C - 10, C - 6, 'east'), (C + 10, C - 6, 'west')]:
        g.set(bx, G + 1, bz, 'minecraft:quartz_stairs', {'facing': face, 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'})
    for y in range(G + 11, G + 16):                           # chandelier
        g.set(C, y, C, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
    for (dx, dz) in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
        g.set(C + dx, G + 10, C + dz, 'minecraft:sea_lantern')
    for k in range(8):                                        # copper conduits
        a = math.radians(45 * k + 22.5)
        if abs(math.degrees(a) - 90) < 30 or abs(math.degrees(a) - 270) < 30:
            continue
        x, z = C + 5.8 * math.cos(a), C + 5.8 * math.sin(a)
        for y in range(G + 1, G + 10):
            g.set(x, y, z, 'minecraft:copper_block')
        g.set(x, G + 10, z, 'minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'})
    for x in range(C - 7, C + 8):                             # mosaic floor spokes
        for z in range(C - 7, C + 8):
            d = math.hypot(x - C, z - C)
            ang = math.degrees(math.atan2(z - C, x - C))
            if 1.5 < d <= 6.2 and abs(round(ang / 45.0) * 45 - ang) < 5:
                g.set(x, G, z, 'minecraft:light_blue_concrete')
    for k in range(6):                                        # angel wings over the gate arch
        for sgn, face in ((-1, 'east'), (1, 'west')):
            g.set(C + sgn * (5 + k), G + 14 + k, C + 24, QB if k % 2 == 0 else QC)
            if k < 5:
                g.set(C + sgn * (5 + k), G + 15 + k, C + 24, 'minecraft:quartz_stairs', {'facing': face, 'half': 'bottom', 'shape': 'straight', 'waterlogged': 'false'})
    vine_pass(g, rnd, {'minecraft:calcite', 'minecraft:stone', 'minecraft:grass_block'}, 0.06, 2, G)


def ashen_detail(g, C, rnd, K1):
    PB, CPB = 'minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks'
    for t in range(3):                                        # stepped tiers around the keep
        half = 17 - 2 * t
        for x in range(C - half, C + half + 1):
            for z in range(C - half, C + half + 1):
                if max(abs(x - C), abs(z - C)) >= half - 1 and max(abs(x - C), abs(z - C)) > 12:
                    if abs(x - C) <= 2 and z > C:
                        continue
                    g.set(x, 10 + t, z, PB if rnd.random() > 0.15 else CPB)
    for (sx, sz) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        g.set(C + sx * 16, 13, C + sz * 16, 'minecraft:soul_campfire', CAMP)
    for off in (-5, 5):                                       # banners
        g.set(C + off, 20, K1 + 1, 'minecraft:red_wall_banner', {'facing': 'south'})
        g.set(C + off, 20, C - 13, 'minecraft:red_wall_banner', {'facing': 'north'})
        g.set(C + 13, 20, C + off, 'minecraft:red_wall_banner', {'facing': 'east'})
        g.set(C - 13, 20, C + off, 'minecraft:red_wall_banner', {'facing': 'west'})
    for a in (10, 55, 145, 190, 235, 325):                    # lava falls from the ceiling into the lake
        x, z = C + 24 * math.cos(math.radians(a)), C + 24 * math.sin(math.radians(a))
        top = int(26 + 24 * math.sqrt(max(0, 1 - (24 / 36.0) ** 2))) - 1
        for y in range(top, 8, -1):
            g.set(x, y, z, 'minecraft:lava', {'level': '0'})
    for _ in range(46):                                       # stalactites
        a, r = rnd.uniform(0, 6.28), rnd.uniform(20, 31)
        x, z = C + r * math.cos(a), C + r * math.sin(a)
        topy = int(26 + 24 * math.sqrt(max(0, 1 - (r / 36.0) ** 2))) - 1
        for k in range(rnd.randint(5, 16)):
            rad = max(0.0, 2.1 - 0.15 * k)
            for dx in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    if math.hypot(dx, dz) <= rad:
                        c = g.get(x + dx, topy - k, z + dz)
                        if c is None or c[0] == AIR:
                            g.set(x + dx, topy - k, z + dz, rnd.choice(['minecraft:blackstone', 'minecraft:basalt', 'minecraft:smooth_basalt']))
    for z in range(C + 10, C + 5, -1):                        # carpet to the pit
        for x in range(C - 1, C + 2):
            g.set(x, 10, z, 'minecraft:red_carpet')
    for zr in (C - 6, C, C + 6):                              # vaulted ribs
        for dx in range(-10, 11):
            y = 26 + int(round(9 * (1 - (dx / 10.0) ** 2)))
            g.set(C + dx, y, zr, PB)
            g.set(C + dx, y - 1, zr, CPB if rnd.random() < 0.3 else PB)
    for (lx, lz) in [(C - 5, C - 6), (C + 5, C - 6), (C - 5, C + 6), (C + 5, C + 6), (C, C)]:
        for y in (35, 34, 33, 32):
            g.set(lx, y, lz, 'minecraft:chain', {'axis': 'y', 'waterlogged': 'false'})
        g.set(lx, 31, lz, 'minecraft:soul_lantern', {'hanging': 'true', 'waterlogged': 'false'})


def _hut(g, cx, cz, y, cap):
    for dx in range(-3, 4):
        for dz in range(-3, 4):
            d = math.hypot(dx, dz)
            if 2.0 <= d <= 2.9:
                for k in range(3):
                    if not (dx == 0 and dz > 0 and k < 2):
                        g.set(cx + dx, y + k, cz + dz, 'minecraft:mushroom_stem')
            elif d < 2.0:
                for k in range(3):
                    g.set(cx + dx, y + k, cz + dz, AIR)
    for k, r in enumerate([4.2, 3.4, 2.2]):
        for dx in range(-5, 6):
            for dz in range(-5, 6):
                if math.hypot(dx, dz) <= r:
                    g.set(cx + dx, y + 3 + k, cz + dz, cap)
    g.set(cx, y + 2, cz, 'minecraft:lantern', {'hanging': 'true', 'waterlogged': 'false'})


def rootbound_gimmicks(g, C, G, rnd):
    """Bramble Seal across the trunk entrance (falls when the four Bramble Sentinels die), spore vents, mushroom huts."""
    for x in range(C - 2, C + 3):
        for y in range(G + 1, G + 8):
            g.set(x, y, C + 12, 'aurelia:bramble_seal')
    for (x, z) in [(C - 1, C + 18), (C + 1, C + 21), (C, C + 24), (C - 1, C + 27), (C + 1, C + 16)]:
        g.set(x, G, z, 'aurelia:spore_vent')
    _hut(g, C + 21, C - 11, G + 1, 'minecraft:red_mushroom_block')
    _hut(g, C - 21, C + 7, G + 1, 'minecraft:brown_mushroom_block')
    _hut(g, C + 7, C - 22, G + 1, 'minecraft:red_mushroom_block')
    for (x, z) in [(C + 14, C + 20), (C - 16, C - 14), (C + 22, C + 6)]:      # exposed verdant ore among the roots
        g.set(x, G + 1, z, 'aurelia:verdant_ore')


def stormwatch_gimmicks(g, C, G, rnd, chest_fn):
    """Storm Seal across the spire door (falls when the four Calcite Sentinels die), gale plates that launch you
    to the bridges, caches on two bridges, a ring of floating rune stones."""
    for x in range(C - 2, C + 3):
        for y in range(G + 1, G + 8):
            g.set(x, y, C + 8, 'aurelia:storm_seal')
    for (sx, sz) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        g.set(C + sx * 12, G, C + sz * 8, 'aurelia:gale_plate')
    for (sx, sz) in [(1, 1), (-1, -1)]:
        chest_fn(g, C + sx * 13, G + 20, C + sz * 13, 'aurelia:chests/stormwatch_cache', 'south')
    for k in range(8):
        a = math.radians(45 * k + 10)
        x, z, y = C + 15 * math.cos(a), C + 15 * math.sin(a), G + 46 + (k % 2) * 4
        for dx in (0, 1):
            for dy in (0, 1):
                for dz in (0, 1):
                    g.set(x + dx, y + dy, z + dz, 'minecraft:quartz_bricks' if (dx + dy + dz) % 2 else 'minecraft:chiseled_quartz_block')
        g.set(x, y + 2, z, 'minecraft:sea_lantern')
        g.set(x, y - 1, z, 'aurelia:stormglass_ore')


def ashen_gimmicks(g, C, rnd, K1):
    """Ash Seal across the keep door (falls when the four Ashbound Knights die), ember vents on the causeway, a colonnade."""
    for x in range(C - 2, C + 3):
        for y in range(10, 17):
            g.set(x, y, K1, 'aurelia:ash_seal')
    for (x, z) in [(C - 1, C + 15), (C + 1, C + 18), (C, C + 21), (C - 1, C + 24), (C + 1, C + 27)]:
        g.set(x, 9, z, 'aurelia:ember_vent')
    for k in range(12):
        a = math.radians(30 * k)
        if abs(math.degrees(a) - 90) < 25:
            continue
        x, z = C + 20.5 * math.cos(a), C + 20.5 * math.sin(a)
        for j in range(6):
            g.set(x, 10 + j, z, 'minecraft:polished_blackstone_bricks')
        g.set(x, 16, z, 'minecraft:chiseled_polished_blackstone')
        g.set(x, 17, z, 'minecraft:soul_lantern', {'hanging': 'false', 'waterlogged': 'false'})
    for (x, z) in [(C + 15, C - 15), (C - 15, C + 15), (C + 17, C + 10)]:
        g.set(x, 10, z, 'aurelia:emberheart_ore')
