"""A detailing pass run on every structure template as it is saved (gen_citadels2.Grid.save).

1. Weathering: plain masonry and stone are mixed with their cracked, mossy, chiseled and neighbouring variants.
2. Quoins: convex wall corners get alternating courses of a contrasting dressed stone.
3. Dressing by realm: ivy and moss in the Grove, snow on every ledge in the Pale Wastes, glow lichen and hanging roots in the deep
   places, lanterns hung on chains from every high ceiling, cobwebs in upper corners, banners on tall walls, flowers in the grass.

It never touches the mod's own blocks or anything within two blocks of them, never decorates a guard's cell, never puts anything
in or beside water, and only ever adds blocks that nothing collides with (or hangs them well above head height), so every route the
reachability checks prove stays open.
"""
import random

AIR = 'minecraft:air'
M = 'minecraft:'

VARIANTS = {
    'stone_bricks': [('stone_bricks', 55), ('mossy_stone_bricks', 14), ('cracked_stone_bricks', 16), ('andesite', 5), ('cobblestone', 5),
                     ('mossy_cobblestone', 5)],
    'mossy_stone_bricks': [('mossy_stone_bricks', 60), ('stone_bricks', 20), ('mossy_cobblestone', 20)],
    'cobblestone': [('cobblestone', 70), ('mossy_cobblestone', 20), ('andesite', 10)],
    'mossy_cobblestone': [('mossy_cobblestone', 70), ('cobblestone', 20), ('moss_block', 10)],
    'deepslate_bricks': [('deepslate_bricks', 55), ('cracked_deepslate_bricks', 20), ('deepslate_tiles', 12), ('polished_deepslate', 8),
                         ('cobbled_deepslate', 5)],
    'deepslate_tiles': [('deepslate_tiles', 65), ('cracked_deepslate_tiles', 25), ('deepslate_bricks', 10)],
    'polished_deepslate': [('polished_deepslate', 72), ('deepslate_tiles', 18), ('cracked_deepslate_tiles', 10)],
    'cobbled_deepslate': [('cobbled_deepslate', 75), ('tuff', 12), ('cobblestone', 13)],
    'polished_blackstone_bricks': [('polished_blackstone_bricks', 66), ('cracked_polished_blackstone_bricks', 24), ('polished_blackstone', 6),
                                   ('gilded_blackstone', 4)],
    'blackstone': [('blackstone', 76), ('polished_blackstone', 12), ('gilded_blackstone', 3), ('cobbled_deepslate', 9)],
    'prismarine_bricks': [('prismarine_bricks', 60), ('prismarine', 25), ('dark_prismarine', 15)],
    'quartz_block': [('quartz_block', 60), ('smooth_quartz', 30), ('quartz_bricks', 10)],
    'quartz_bricks': [('quartz_bricks', 70), ('quartz_block', 20), ('chiseled_quartz_block', 10)],
    'red_sandstone': [('red_sandstone', 60), ('cut_red_sandstone', 20), ('smooth_red_sandstone', 15), ('chiseled_red_sandstone', 5)],
    'cut_red_sandstone': [('cut_red_sandstone', 70), ('red_sandstone', 20), ('smooth_red_sandstone', 10)],
    'sandstone': [('sandstone', 60), ('cut_sandstone', 20), ('smooth_sandstone', 15), ('chiseled_sandstone', 5)],
    'calcite': [('calcite', 82), ('diorite', 10), ('polished_diorite', 8)],
    'packed_ice': [('packed_ice', 76), ('blue_ice', 12), ('snow_block', 12)],
    'snow_block': [('snow_block', 86), ('packed_ice', 14)],
    'stone': [('stone', 60), ('andesite', 14), ('cobblestone', 10), ('tuff', 8), ('diorite', 4), ('granite', 4)],
    'andesite': [('andesite', 70), ('stone', 20), ('polished_andesite', 10)],
    'dirt': [('dirt', 70), ('coarse_dirt', 20), ('rooted_dirt', 10)],
    'tuff': [('tuff', 70), ('cobbled_deepslate', 15), ('andesite', 15)],
    'mud_bricks': [('mud_bricks', 80), ('packed_mud', 20)],
}
QUOIN = {'stone_bricks': 'polished_andesite', 'mossy_stone_bricks': 'polished_andesite', 'deepslate_bricks': 'polished_deepslate',
         'deepslate_tiles': 'polished_deepslate', 'polished_blackstone_bricks': 'polished_blackstone', 'calcite': 'smooth_quartz',
         'prismarine_bricks': 'dark_prismarine', 'red_sandstone': 'smooth_red_sandstone', 'cut_red_sandstone': 'chiseled_red_sandstone',
         'sandstone': 'cut_sandstone', 'quartz_bricks': 'smooth_quartz', 'quartz_block': 'quartz_bricks', 'packed_ice': 'blue_ice',
         'cobblestone': 'stone_bricks', 'bone_block': 'smooth_quartz'}
DRESSED = {'stone_bricks': 'chiseled_stone_bricks', 'cobblestone': 'stone_bricks', 'deepslate_bricks': 'chiseled_deepslate',
           'deepslate_tiles': 'polished_deepslate', 'polished_deepslate': 'chiseled_deepslate', 'polished_blackstone_bricks': 'chiseled_polished_blackstone',
           'blackstone': 'polished_blackstone', 'prismarine_bricks': 'dark_prismarine', 'quartz_block': 'chiseled_quartz_block',
           'quartz_bricks': 'chiseled_quartz_block', 'red_sandstone': 'chiseled_red_sandstone', 'cut_red_sandstone': 'smooth_red_sandstone',
           'sandstone': 'chiseled_sandstone', 'calcite': 'smooth_quartz', 'packed_ice': 'blue_ice', 'mud_bricks': 'packed_mud'}
B = {'waterlogged': 'false'}
FURNITURE = {
    'grove': [('barrel', {'facing': 'up', 'open': 'false'}, ('potted_fern', {})), ('composter', {'level': '0'}, None),
              ('bookshelf', {}, ('potted_red_mushroom', {})), ('crafting_table', {}, None)],
    'skyreach': [('bookshelf', {}, ('potted_cornflower', {})), ('barrel', {'facing': 'up', 'open': 'false'}, ('lantern', dict(B, hanging='false'))),
                 ('cartography_table', {}, None)],
    'hollow': [('barrel', {'facing': 'up', 'open': 'false'}, ('skeleton_skull', {'rotation': '4'})), ('blast_furnace', {'facing': 'north', 'lit': 'false'}, None),
               ('smithing_table', {}, None), ('lodestone', {}, ('soul_lantern', dict(B, hanging='false')))],
    'drowned': [('barrel', {'facing': 'up', 'open': 'false'}, ('sea_pickle', {'pickles': '3', 'waterlogged': 'false'})),
                ('bookshelf', {}, None), ('dark_prismarine', {}, ('lantern', dict(B, hanging='false')))],
    'pale': [('bookshelf', {}, ('white_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})), ('barrel', {'facing': 'up', 'open': 'false'}, None),
             ('cauldron', {}, None)],
    'scarlet': [('barrel', {'facing': 'up', 'open': 'false'}, ('decorated_pot', {'facing': 'north', 'waterlogged': 'false'})),
                ('loom', {'facing': 'north'}, None), ('chiseled_red_sandstone', {}, ('red_candle', {'candles': '2', 'lit': 'true', 'waterlogged': 'false'}))],
    'clockwork': [('barrel', {'facing': 'up', 'open': 'false'}, ('purple_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})),
                  ('bookshelf', {}, ('potted_wither_rose', {})), ('lodestone', {}, None), ('smithing_table', {}, None)],
    'mycelial': [('mushroom_stem', {}, ('potted_crimson_fungus', {})), ('barrel', {'facing': 'up', 'open': 'false'}, ('magenta_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'})),
                 ('bookshelf', {}, ('potted_red_mushroom', {}))],
    'last': [('chiseled_polished_blackstone', {}, ('soul_lantern', dict(B, hanging='false'))), ('bookshelf', {}, ('purple_candle', {'candles': '3', 'lit': 'true', 'waterlogged': 'false'}))],
}
WALLISH = set(VARIANTS) | set(QUOIN) | {'bone_block', 'mushroom_stem', 'oak_log', 'spruce_log', 'dark_oak_log', 'jungle_log', 'oak_planks',
                                        'spruce_planks', 'dark_oak_planks', 'moss_block', 'chiseled_stone_bricks', 'smooth_quartz',
                                        'cracked_stone_bricks', 'polished_deepslate', 'deepslate', 'magenta_terracotta', 'white_terracotta',
                                        'terracotta', 'smooth_sandstone', 'mud', 'basalt', 'polished_basalt'}
NONSOLID = {'air', 'cave_air', 'water', 'lava', 'vine', 'glow_lichen', 'moss_carpet', 'snow', 'grass', 'tall_grass', 'fern', 'large_fern',
            'dead_bush', 'cobweb', 'chain', 'lantern', 'soul_lantern', 'hanging_roots', 'ladder', 'torch', 'wall_torch', 'end_rod',
            'spore_blossom', 'red_mushroom', 'brown_mushroom', 'poppy', 'dandelion', 'cornflower', 'azure_bluet', 'oxeye_daisy', 'allium',
            'blue_orchid', 'lily_of_the_valley', 'pointed_dripstone', 'amethyst_cluster', 'candle', 'lily_pad', 'seagrass', 'kelp',
            'kelp_plant', 'sea_pickle', 'crimson_roots', 'nether_sprouts', 'soul_fire', 'fire', 'campfire', 'soul_campfire', 'iron_bars',
            'lightning_rod', 'bell'}

ROCK = {'deepslate', 'tuff', 'cobbled_deepslate', 'stone', 'andesite', 'blackstone', 'calcite', 'diorite', 'packed_ice', 'prismarine',
        'dark_prismarine', 'bone_block', 'mossy_cobblestone', 'terracotta', 'orange_terracotta', 'red_terracotta', 'yellow_terracotta',
        'white_terracotta', 'basalt', 'magma_block'}
REALM_ORE = {'grove': 'verdant_ore', 'skyreach': 'stormglass_ore', 'hollow': 'emberheart_ore', 'drowned': 'tidestone_ore', 'pale': 'rime_ore',
             'scarlet': 'sunglass_ore', 'clockwork': 'chronite_ore', 'mycelial': 'bloomspore_ore'}
THEMES = {
    'grove': dict(vine=0.12, moss=0.18, lichen=0.0, snow=False, roots=0.03, cobweb=0.02, lantern='lantern', banner='green',
                  flowers=['grass', 'fern', 'poppy', 'dandelion', 'allium', 'blue_orchid', 'oxeye_daisy', 'grass']),
    'skyreach': dict(vine=0.03, moss=0.0, lichen=0.0, snow=False, roots=0.0, cobweb=0.0, lantern='lantern', banner='light_blue',
                     flowers=['grass', 'cornflower', 'azure_bluet', 'oxeye_daisy', 'lily_of_the_valley', 'grass']),
    'hollow': dict(vine=0.0, moss=0.0, lichen=0.03, snow=False, roots=0.0, cobweb=0.05, lantern='soul_lantern', banner='red',
                   flowers=['crimson_roots', 'nether_sprouts']),
    'drowned': dict(vine=0.0, moss=0.0, lichen=0.04, snow=False, roots=0.0, cobweb=0.0, lantern='lantern', banner='cyan', flowers=[],
                    no_unset=True),
    'pale': dict(vine=0.0, moss=0.0, lichen=0.0, snow=True, roots=0.0, cobweb=0.03, lantern='soul_lantern', banner='white', flowers=[]),
    'scarlet': dict(vine=0.0, moss=0.0, lichen=0.0, snow=False, roots=0.0, cobweb=0.03, lantern='lantern', banner='orange',
                    flowers=['dead_bush']),
    'clockwork': dict(vine=0.0, moss=0.0, lichen=0.025, snow=False, roots=0.0, cobweb=0.04, lantern='soul_lantern', banner='purple',
                      flowers=['grass', 'fern']),
    'mycelial': dict(vine=0.0, moss=0.07, lichen=0.07, snow=False, roots=0.06, cobweb=0.02, lantern='lantern', banner='magenta',
                     flowers=['red_mushroom', 'brown_mushroom', 'crimson_roots']),
    'last': dict(vine=0.0, moss=0.0, lichen=0.02, snow=False, roots=0.0, cobweb=0.0, lantern='soul_lantern', banner='purple',
                 flowers=['grass', 'fern', 'allium']),
}
PREFIX = [('rootbound', 'grove'), ('grove', 'grove'), ('stormwatch', 'skyreach'), ('sky_', 'skyreach'), ('ashen', 'hollow'), ('hollow', 'hollow'),
          ('tidewrack', 'drowned'), ('drowned', 'drowned'), ('rimefast', 'pale'), ('pale', 'pale'), ('sunscar', 'scarlet'), ('scarlet', 'scarlet'),
          ('paradox', 'clockwork'), ('rift_', 'clockwork'), ('spore_', 'mycelial'), ('fungal', 'mycelial'), ('root_arch', 'mycelial'),
          ('convergence', 'last'), ('last_core', 'last')]
HORIZ = [((1, 0, 0), 'east', 'west'), ((-1, 0, 0), 'west', 'east'), ((0, 0, 1), 'south', 'north'), ((0, 0, -1), 'north', 'south')]


def theme_of(name):
    if name.startswith('last_island_'):
        return name[len('last_island_'):]
    if name.startswith('dungeon:'):                                  # a dungeon takes its realm's dressing
        return name.split(':')[1]
    if name.startswith('lair_'):                                     # a lieutenant's lair takes its realm's dressing
        from lieutenants import BY_ID
        return BY_ID[name[len('lair_'):]]['realm']
    for pre, t in PREFIX:
        if name.startswith(pre):
            return t
    return 'grove'


def pick(rnd, options):
    total = sum(w for _, w in options)
    r = rnd.uniform(0, total)
    for b, w in options:
        r -= w
        if r <= 0:
            return b
    return options[-1][0]


def enrich(g, name, light=False):
    theme_key = theme_of(name)
    th = THEMES[theme_key]
    if light or name.startswith('lair_'):                           # vast work (lairs, fortresses): a lighter hand, or the overgrowth buries it
        th = dict(th, vine=th['vine'] * 0.3, moss=th['moss'] * 0.4, lichen=th['lichen'] * 0.5, flower_rate=0.03)
    rnd = random.Random(sum(ord(c) * (i + 1) for i, c in enumerate(name)))
    b = g.b
    W, H, L = g.W, g.H, g.L
    allow_unset = not th.get('no_unset') and name != 'last_core'

    def short(p):
        c = b.get(p)
        return None if c is None else c[0].split(':')[1]

    def plain(p):
        c = b.get(p)
        return c is not None and c[0].startswith(M) and not c[1] and c[2] is None

    def solid(p):
        s = short(p)
        return s is not None and s not in NONSOLID and 'carpet' not in s and 'slab' not in s and 'stairs' not in s and 'wall' not in s \
            and 'fence' not in s and 'pane' not in s and 'glass' not in s and 'door' not in s and 'trapdoor' not in s

    def inside(p):
        return 0 <= p[0] < W and 0 <= p[1] < H and 0 <= p[2] < L

    def free(p):
        c = b.get(p)
        if c is None:
            return allow_unset and inside(p)
        return c[0] in (AIR, 'minecraft:cave_air')

    # ---- what must not be touched
    protect = set()
    sun = [p for p, c in b.items() if c[0].startswith('aurelia:sun')]
    for p, c in list(b.items()):
        if c[0].startswith('aurelia:') or c[0] in ('minecraft:chest', 'minecraft:lectern', 'minecraft:bell'):
            for dx in range(-2, 3):
                for dy in range(-2, 4):
                    for dz in range(-2, 3):
                        protect.add((p[0] + dx, p[1] + dy, p[2] + dz))
    if sun:                                                         # the Sunscar court: the beam needs every air cell in it
        x0, x1 = min(p[0] for p in sun) - 3, max(p[0] for p in sun) + 3
        z0, z1 = min(p[2] for p in sun) - 3, max(p[2] for p in sun) + 3
        y0 = min(p[1] for p in sun)
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                for y in range(y0 - 1, y0 + 6):
                    protect.add((x, y, z))
    for e in g.entities:
        x, y, z = (int(v) for v in e['blockPos'])
        for dy in range(-1, 4):
            protect.add((x, y + dy, z))
    wet = set()
    for p, c in b.items():
        if c[0] in ('minecraft:water', 'minecraft:lava') or ('waterlogged', 'true') in c[1]:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        wet.add((p[0] + dx, p[1] + dy, p[2] + dz))

    def can_place(p):
        return p not in protect and p not in wet and free(p)

    added = 0

    def put(p, block, props=None):
        nonlocal added
        g.b[p] = ('minecraft:' + block, tuple(sorted((props or {}).items())), None)
        added += 1

    # ---- 1 & 2: quoins on convex corners, then weathering
    cells = list(b.items())
    for p, c in cells:
        if not plain(p):
            continue
        s = c[0][len(M):]
        if s in QUOIN and p[1] % 2 == 0:
            open_sides = [d for d, _, _ in HORIZ if free((p[0] + d[0], p[1], p[2] + d[2]))]
            if len(open_sides) == 2 and open_sides[0][0] != -open_sides[1][0] and open_sides[0][2] != -open_sides[1][2]:
                if short((p[0], p[1] + 1, p[2])) == s and short((p[0], p[1] - 1, p[2])) == s:
                    b[p] = (M + QUOIN[s], (), None)
                    continue
        if s in VARIANTS:
            v = pick(rnd, VARIANTS[s])
            if v != s:
                b[p] = (M + v, (), None)

    # ---- 2a: ore in the rock. The Clockwork Rift's floating stone holds Chronite; each Last Realm island its realm's ore.
    ore = None
    if name.startswith('rift_'):
        ore = 'aurelia:chronite_ore'
    elif name.startswith('last_island_'):
        ore = 'aurelia:' + REALM_ORE[name[len('last_island_'):]]
    if ore:
        for p, c in list(b.items()):
            if plain(p) and c[0][len(M):] in ROCK and p not in protect and rnd.random() < 0.045:
                b[p] = (ore, (), None)

    # ---- 2b: architecture. Lintels and sills round windows, inlaid borders round room floors, capitals and bases on pillars.
    def glassy(q):
        t = short(q)
        return t is not None and ('glass' in t)
    for p, c in list(b.items()):
        if not plain(p):
            continue
        s = c[0][len(M):]
        base = s
        for k, opts in VARIANTS.items():
            if any(s == o for o, _ in opts):
                base = k
                break
        dressed = DRESSED.get(base)
        if dressed is None:
            continue
        x, y, z = p
        if glassy((x, y - 1, z)) or glassy((x, y + 1, z)):          # lintel over a window, sill under it
            b[p] = (M + dressed, (), None)
            continue
        if free((x, y + 1, z)) and free((x, y + 2, z)) and any(solid((x + d[0], y + 1, z + d[2])) for d, _, _ in HORIZ) \
                and any(solid((x, y + k, z)) for k in range(3, 9)):   # a floor cell against a wall, under a roof
            b[p] = (M + dressed, (), None)
            continue
        if all(free((x + d[0], y, z + d[2])) for d, _, _ in HORIZ) and solid((x, y + 1, z)) != solid((x, y - 1, z)):
            b[p] = (M + dressed, (), None)                            # the top or foot of a free-standing pillar

    # ---- 2c: furniture in the corners of rooms
    furn = FURNITURE.get(theme_key, FURNITURE['grove'])
    for p, c in list(b.items()):
        x, y, z = p
        if not solid(p) or not can_place((x, y + 1, z)) or not free((x, y + 2, z)) or (x, y + 1, z) in protect:
            continue
        walls = [d for d, _, _ in HORIZ if solid((x + d[0], y + 1, z + d[2])) and solid((x + d[0], y + 2, z + d[2]))]
        if len(walls) != 2 or walls[0][0] == -walls[1][0] and walls[0][2] == -walls[1][2]:
            continue
        if not any(solid((x, y + k, z)) for k in range(3, 8)):          # only under a roof
            continue
        ax, az = -(walls[0][0] + walls[1][0]), -(walls[0][2] + walls[1][2])   # the room must open out past the corner (never a bend in a passage)
        if not all(free((x + dx, y + h, z + dz)) for (dx, dz) in [(ax, 0), (0, az), (ax, az), (2 * ax, az), (ax, 2 * az)] for h in (1, 2)):
            continue
        if rnd.random() < 0.45:
            block, props, top = rnd.choice(furn)
            put((x, y + 1, z), block, props)
            if top and can_place((x, y + 2, z)) and rnd.random() < 0.6:
                put((x, y + 2, z), top[0], top[1])

    # ---- 3: dressing
    cells = list(b.items())
    for p, c in cells:
        if not solid(p) or p in protect:
            continue
        s = short(p)
        x, y, z = p
        above = (x, y + 1, z)
        below = (x, y - 1, z)
        # sides: ivy, lichen, banners
        for d, dname, opp in HORIZ:
            n = (x + d[0], y, z + d[2])
            if not can_place(n):
                continue
            r = rnd.random()
            if th['vine'] and s in WALLISH and r < th['vine']:
                length = rnd.randint(1, 5)
                for k in range(length):
                    q = (n[0], n[1] - k, n[2])
                    if not can_place(q) or not solid((x, y - k, z)):
                        break
                    put(q, 'vine', {'east': 'false', 'west': 'false', 'north': 'false', 'south': 'false', 'up': 'false', opp: 'true'})
                continue
            if th['lichen'] and r < th['lichen'] and any(solid((n[0], n[1] + k, n[2])) for k in range(1, 9)):   # only in roofed, dark places
                props = {k: 'false' for k in ('down', 'up', 'north', 'south', 'east', 'west')}
                props[opp] = 'true'
                props['waterlogged'] = 'false'
                put(n, 'glow_lichen', props)
                continue
            if s in WALLISH and r > 0.9965:                          # a banner on a tall wall, well above the ground
                clear = 0
                while clear < 6 and free((n[0], n[1] - clear - 1, n[2])):
                    clear += 1
                if clear >= 4 and all(not (q in protect) for q in [(n[0], n[1] - k, n[2]) for k in range(5)]):
                    put(n, f'{th["banner"]}_wall_banner', {'facing': dname})
        # top surfaces: snow, moss, flowers
        if can_place(above) and plain(p):
            open_sky = all(not solid((x, y + k, z)) for k in range(1, 14))
            r = rnd.random()
            if th['snow'] and open_sky and r < 0.65:
                put(above, 'snow', {'layers': '1'})
            elif s in ('grass_block', 'moss_block', 'podzol', 'mycelium') and th['flowers'] and r < th.get('flower_rate', 0.16):
                put(above, rnd.choice(th['flowers']))
            elif s in ('red_sand', 'sand') and 'dead_bush' in th['flowers'] and r < 0.03:
                put(above, 'dead_bush')
            elif th['moss'] and s in WALLISH and open_sky and r < th['moss']:
                put(above, 'moss_carpet')
        # ceilings: lanterns on chains, hanging roots, cobwebs
        if can_place(below) and s in WALLISH | {'oak_planks', 'spruce_planks', 'dark_oak_planks'}:
            gap = 0
            while gap < 12 and free((x, y - gap - 1, z)) and (x, y - gap - 1, z) not in protect:
                gap += 1
            floor = (x, y - gap - 1, z)
            if gap < 12 and solid(floor):
                r = rnd.random()
                if gap >= 5 and (x * 7 + z * 13) % 11 == 0 and r < 0.5:
                    put(below, 'chain', {'axis': 'y', 'waterlogged': 'false'})
                    put((x, y - 2, z), th['lantern'], {'hanging': 'true', 'waterlogged': 'false'})
                elif gap >= 4 and th['roots'] and r < th['roots']:
                    put(below, 'hanging_roots', {'waterlogged': 'false'})
                elif gap >= 4 and th['cobweb'] and r < th['cobweb']:
                    walls = sum(1 for d, _, _ in HORIZ if solid((x + d[0], y - 1, z + d[2])))
                    if walls >= 2:
                        put(below, 'cobweb')
    return added
