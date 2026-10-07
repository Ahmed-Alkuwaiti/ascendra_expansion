import copy, json, os

D = __import__('paths').RES + '/data/aurelia'
V = __import__('paths').VANILLA


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def vload(name):
    return json.load(open(f'{V}/{name}'))


# ---------------------------------------------------------------- Skyreach: a true void (every block is air; islands are structures)
ns = vload('ns_floating_islands.json')
ns['noise_router']['final_density'] = -1.0
ns['noise_router']['temperature'] = 0.0
ns['noise_router']['vegetation'] = 0.0
write(f'{D}/worldgen/noise_settings/skyreach.json', ns)

# ---------------------------------------------------------------- custom features, each a copy of a vanilla file with edits
springs = vload('v_placed_feature_spring_water.json')            # waterfalls everywhere on the Grove's cliffs
springs['placement'][0]['count'] = 110
springs['placement'][2]['height']['max_inclusive'] = {'absolute': 250}
write(f'{D}/worldgen/placed_feature/grove_springs.json', springs)

vines = vload('v_placed_feature_vines.json')                       # curtains of vines down the stone
vines['placement'][0]['count'] = 220
vines['placement'][2]['height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': 40}, 'max_inclusive': {'absolute': 230}}
write(f'{D}/worldgen/placed_feature/grove_vines.json', vines)

fungus = vload('v_configured_feature_crimson_fungus.json')         # giant red fungi that grow on basalt
fungus['config']['valid_base_block'] = {'Name': 'minecraft:basalt', 'Properties': {'axis': 'y'}}
write(f'{D}/worldgen/configured_feature/giant_red_fungus.json', fungus)
write(f'{D}/worldgen/placed_feature/giant_red_fungus_patch.json', {
    'feature': 'aurelia:giant_red_fungus',
    'placement': [{'type': 'minecraft:count_on_every_layer', 'count': 3}, {'type': 'minecraft:biome'}]})

falls = vload('v_configured_feature_spring_nether_open.json')      # lava falls that can start in blackstone and basalt
falls['config']['valid_blocks'] = ['minecraft:blackstone', 'minecraft:basalt', 'minecraft:smooth_basalt', 'minecraft:netherrack', 'minecraft:magma_block']
write(f'{D}/worldgen/configured_feature/hollow_lava_falls.json', falls)
lf = vload('v_placed_feature_spring_open.json')
lf['feature'] = 'aurelia:hollow_lava_falls'
lf['placement'][0]['count'] = 36
write(f'{D}/worldgen/placed_feature/hollow_lava_falls.json', lf)

# ---------------------------------------------------------------- biomes
def hexint(h):
    return int(h.lstrip('#'), 16)


def biome(name, precip, temp, down, colors, extra, monsters, carvers, features):
    steps = [[] for _ in range(11)]
    for step, items in features.items():
        steps[step] = items
    eff = {'sky_color': hexint(colors['sky']), 'fog_color': hexint(colors['fog']), 'water_color': hexint(colors['water']),
           'water_fog_color': hexint(colors['water_fog']), 'grass_color': hexint(colors['grass']), 'foliage_color': hexint(colors['foliage'])}
    eff.update(extra)
    write(f'{D}/worldgen/biome/{name}.json', {
        'has_precipitation': precip, 'temperature': temp, 'downfall': down, 'effects': eff,
        'spawners': {'monster': monsters, 'creature': [], 'ambient': [], 'axolotls': [], 'underground_water_creature': [],
                     'water_creature': [], 'water_ambient': [], 'misc': []},
        'spawn_costs': {}, 'carvers': {'air': carvers}, 'features': steps})


def particle(kind, prob):
    return {'particle': {'options': {'type': kind}, 'probability': prob}}


ORES = ['minecraft:ore_coal_upper', 'minecraft:ore_iron_upper', 'minecraft:ore_diamond']
biome('grove', True, 0.85, 0.9,
      {'sky': '#7FD6FF', 'fog': '#D5F7C0', 'water': '#3FC8E8', 'water_fog': '#1A8FA0', 'grass': '#8FDB5C', 'foliage': '#38C06C'},
      particle('minecraft:spore_blossom_air', 0.012),
      [{'type': 'aurelia:grove_ant', 'weight': 60, 'minCount': 2, 'maxCount': 4}],
      ['minecraft:cave', 'minecraft:cave_extra_underground', 'minecraft:canyon'],
      {6: ORES, 8: ['aurelia:grove_springs'],
       9: ['minecraft:trees_jungle', 'minecraft:mushroom_island_vegetation', 'minecraft:patch_large_fern', 'minecraft:flower_flower_forest',
           'minecraft:forest_flowers', 'minecraft:patch_grass_jungle', 'minecraft:jungle_bush', 'minecraft:patch_tall_grass',
           'aurelia:grove_vines', 'minecraft:brown_mushroom_normal', 'minecraft:red_mushroom_normal']})
biome('skyreach', False, 0.6, 0.3,
      {'sky': '#7CC0FF', 'fog': '#EAF6FF', 'water': '#4FC3FF', 'water_fog': '#3A9ED8', 'grass': '#A8F28A', 'foliage': '#7FE6A0'},
      particle('minecraft:end_rod', 0.004),
      [{'type': 'minecraft:phantom', 'weight': 20, 'minCount': 1, 'maxCount': 2},
       {'type': 'aurelia:sky_sentinel', 'weight': 40, 'minCount': 1, 'maxCount': 2}], [], {})
hollow_fx = {'ambient_sound': 'minecraft:ambient.basalt_deltas.loop',
             'mood_sound': {'sound': 'minecraft:ambient.basalt_deltas.mood', 'tick_delay': 6000, 'block_search_extent': 8, 'offset': 2.0},
             'additions_sound': {'sound': 'minecraft:ambient.basalt_deltas.additions', 'tick_chance': 0.0111}}
hollow_fx.update(particle('minecraft:white_ash', 0.06))
biome('hollow', False, 0.5, 0.0,
      {'sky': '#0A0A12', 'fog': '#2A1210', 'water': '#2A2438', 'water_fog': '#0F0C16', 'grass': '#4A4650', 'foliage': '#3A3540'},
      hollow_fx,
      [{'type': 'aurelia:hollow_shade', 'weight': 60, 'minCount': 2, 'maxCount': 4},
       {'type': 'minecraft:enderman', 'weight': 10, 'minCount': 1, 'maxCount': 2}],
      ['minecraft:nether_cave'],
      {7: ['minecraft:basalt_blobs', 'minecraft:blackstone_blobs', 'minecraft:basalt_pillar', 'minecraft:glowstone_extra',
           'minecraft:glowstone', 'minecraft:patch_soul_fire'],
       8: ['aurelia:hollow_lava_falls'],
       9: ['aurelia:giant_red_fungus_patch', 'minecraft:brown_mushroom_nether', 'minecraft:red_mushroom_nether']})

# ---------------------------------------------------------------- structure groups
def uniform(lo, hi):
    return {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}


GROUPS = [
    # name, variants, biome tag, start_height, project_to_heightmap, spacing, separation, salt, exclusion
    ('skyreach_castle_islands', ['sky_island_castle_0'], 'skyreach_islands', uniform(70, 110), False, 20, 9, 91000101, None),
    ('skyreach_large_islands', ['sky_island_large_0', 'sky_island_large_1'], 'skyreach_islands', uniform(50, 120), False, 9, 4, 91000102, ('skyreach_castle_islands', 3)),
    ('skyreach_medium_islands', ['sky_island_medium_0', 'sky_island_medium_1', 'sky_island_medium_2'], 'skyreach_islands', uniform(40, 150), False, 5, 2, 91000103, ('skyreach_large_islands', 3)),
    ('skyreach_small_islands', ['sky_island_small_0', 'sky_island_small_1', 'sky_island_small_2'], 'skyreach_islands', uniform(30, 170), False, 3, 1, 91000104, ('skyreach_medium_islands', 1)),
    ('grove_pillars', ['grove_pillar_0', 'grove_pillar_1', 'grove_pillar_2', 'grove_pillar_3'], 'grove_decor', {'absolute': -6}, True, 7, 3, 91000105, None),
    ('grove_ruins', ['grove_ruin_0', 'grove_ruin_1', 'grove_ruin_2', 'grove_ruin_3', 'grove_ruin_4'], 'grove_decor', {'absolute': -3}, True, 5, 2, 91000106, ('grove_pillars', 1)),
    ('hollow_ziggurats', ['hollow_ziggurat_0', 'hollow_ziggurat_1'], 'hollow_decor', uniform(30, 48), False, 9, 4, 91000107, None),
    ('hollow_arches', ['hollow_arch_0', 'hollow_arch_1'], 'hollow_decor', uniform(46, 76), False, 7, 3, 91000108, ('hollow_ziggurats', 1)),
    ('grove_outposts', ['grove_outpost_0', 'grove_outpost_1'], 'grove_decor', {'absolute': -3}, True, 10, 4, 91000110, ('grove_pillars', 1)),
    ('skyreach_outposts', ['sky_outpost_0', 'sky_outpost_1'], 'skyreach_islands', uniform(60, 150), False, 7, 3, 91000111, ('skyreach_large_islands', 2)),
    ('hollow_outposts', ['hollow_outpost_0', 'hollow_outpost_1'], 'hollow_decor', uniform(32, 50), False, 8, 3, 91000112, ('hollow_ziggurats', 2)),
    ('hollow_stalactites', [f'hollow_stalactite_{i}' for i in range(5)], 'hollow_decor', {'absolute': 74}, False, 3, 1, 91000109, None),
]
for tag, biome_id in [('skyreach_islands', 'aurelia:skyreach'), ('grove_decor', 'aurelia:grove'), ('hollow_decor', 'aurelia:hollow')]:
    write(f'{D}/tags/worldgen/biome/has_structure/{tag}.json', {'replace': False, 'values': [biome_id]})
for name, variants, tag, start, project, spacing, sep, salt, excl in GROUPS:
    s = {'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/{tag}', 'step': 'surface_structures', 'spawn_overrides': {},
         'terrain_adaptation': 'none', 'start_pool': f'aurelia:{name}/start', 'size': 1, 'start_height': start,
         'max_distance_from_center': 80, 'use_expansion_hack': False}
    if project:
        s['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
    write(f'{D}/worldgen/structure/{name}.json', s)
    write(f'{D}/worldgen/template_pool/{name}/start.json', {
        'fallback': 'minecraft:empty',
        'elements': [{'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:{v}',
                                               'processors': {'processors': []}, 'projection': 'rigid'}} for v in variants]})
    placement = {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}
    if excl:
        placement['exclusion_zone'] = {'other_set': f'aurelia:{excl[0]}', 'chunk_count': excl[1]}
    write(f'{D}/worldgen/structure_set/{name}.json', {'structures': [{'structure': f'aurelia:{name}', 'weight': 1}], 'placement': placement})
print('realm data written')
