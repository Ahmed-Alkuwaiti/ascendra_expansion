"""Generates the addon's data and assets JSON: rosters, worldgen (structures, sets, biomes, features, tags), loot tables,
recipes, advancements, the lang file and sounds.json. Run from tools/: `python3 datagen.py`. Landmark templates and their
sidecars come from tools/structures/*.py; this script reads the sidecars for each landmark's ground row.

Every Antarchy id used below was read from the Antarchy 2.2.9+1.21.1 jar that ships in Integrated Boogaloo 1.0.8
(entity tags, loot tables, recipes and lang via ci/pack/details.py); the pack server test re-checks them in game.
"""
import json
import os
import shutil

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
DATA = os.path.join(ROOT, 'data', 'unstable_frontiers')
ASSETS = os.path.join(ROOT, 'assets', 'unstable_frontiers')
NS = 'unstable_frontiers'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def d(*parts):
    return os.path.join(DATA, *parts)


# ------------------------------------------------------------------------------------------------------------ rosters
def m(id_, weight=1, mx=0):
    e = {'id': id_, 'weight': weight}
    if mx:
        e['max'] = mx
    return e


def elite(id_, title, bar, abilities):
    return {'id': id_, 'title': title, 'bar': bar, 'abilities': abilities}


A = 'antarchy:'
ROSTERS = {
    # Gibbet Spire: insects below, flyers above, the Alpha Mantis in the crown.
    # Health and attack as measured in Integrated Boogaloo 1.0.8 (Boogaloo Core scaling applied), see TESTING.md:
    # mantis 125/18, scorpion 75/10, wasp 40/8, springbug 250/24, stratoshark 100/10, manticore 150/22,
    # alpha mantis 950/36, nightmare 950/32, emperor scorpion 1050/56, brutalfly 1250/30, Hercules beetle 1625/60,
    # basilisk 800/72. Red ants and termites are passive creatures (12.5 health), used only as hive colour.
    'tower_swarm_pen': {'mobs': [m(A + 'mantis', 3, 2), m(A + 'scorpion', 4)]},
    'tower_hatchery': {'mobs': [m(A + 'wasp', 3), m(A + 'scorpion', 2), m(A + 'springbug', 1, 1)]},
    'tower_aerie': {'mobs': [m(A + 'wasp', 2)], 'flyers': [m(A + 'stratoshark', 3, 2), m(A + 'brutalfly', 1, 1)]},
    'tower_crown': {'mobs': [m(A + 'mantis')], 'escorts': 2,
                    'elite': elite(A + 'alpha_mantis', 'The Crowned Mantis', 'green', ['slam', 'pounce', 'rally'])},
    # Hanging Gaol: every cell holds one prisoner worth hunting for Antarchy's own recipes.
    # The cells hold mid-tier prisoners (springbug legs, manticore wings, scorpions); the Gaoler is the brutalfly, whose
    # wing is what Antarchy's Brutalfly Elytra needs. The emperor scorpion is the one heavy cell (Big Bertha's stinger).
    'gaol_cell_insect': {'mobs': [m(A + 'springbug', 1, 1), m(A + 'mantis', 1, 1)]},
    'gaol_cell_wasp': {'mobs': [m(A + 'wasp', 3, 3)]},
    'gaol_cell_scorpion': {'mobs': [m(A + 'emperor_scorpion', 1, 1)]},
    'gaol_cell_flyer': {'mobs': [m(A + 'manticore', 1, 1)]},
    'gaol_warden': {'mobs': [m(A + 'scorpion')], 'escorts': 2,
                    'elite': elite(A + 'brutalfly', 'The Gaoler', 'yellow', ['pounce', 'screech', 'rally'])},
    # Rookery: predators on their perches, scavengers in the tunnel, the Nightmare as its mother.
    'rookery_roost': {'mobs': [m(A + 'scorpion')], 'flyers': [m(A + 'stratoshark', 3), m(A + 'brutalfly', 1, 1)]},
    'rookery_mother': {'mobs': [m(A + 'stratoshark')], 'flyers': [m(A + 'stratoshark')], 'escorts': 1,
                       'elite': elite(A + 'nightmare', 'The Rookmother', 'purple', ['screech', 'pounce'])},
    'rookery_scavengers': {'mobs': [m(A + 'scorpion', 3), m(A + 'springbug', 1, 1)]},
    # Brood Hive.
    'hive_workers': {'mobs': [m(A + 'wasp', 3), m(A + 'termite', 1, 2), m(A + 'red_ant', 1, 2)]},
    'hive_brood': {'mobs': [m(A + 'wasp', 4), m(A + 'springbug', 1, 1), m(A + 'mantis', 1, 1)]},
    'hive_tyrant': {'mobs': [m(A + 'wasp'), m(A + 'termite')], 'escorts': 3,
                    'elite': elite(A + 'hercules_beetle', 'The Hive Tyrant', 'yellow', ['slam', 'rally'])},
    # Carrion Field residents: insects feed in the ribs, predators stand on the spine.
    'carrion_swarm': {'mobs': [m(A + 'mantis', 2), m(A + 'scorpion', 3)]},
    'carrion_raptors': {'mobs': [m(A + 'stratoshark')], 'flyers': [m(A + 'stratoshark', 3), m(A + 'brutalfly', 1, 1)]},
    # The Great Cage.
    'great_cage_finale': {'mobs': [m(A + 'mantis', 2), m(A + 'scorpion', 2), m(A + 'springbug', 1, 1)],
                          'flyers': [m(A + 'stratoshark', 3), m(A + 'nightmare', 1, 1)], 'escorts': 3,
                          'elite': elite(A + 'basilisk', 'The Cagewright\'s Beast', 'red', ['slam', 'screech', 'rally', 'pounce'])},
    # Between landmarks, after dark.
    'night_overflight': {'flyers': [m(A + 'nightmare', 1), m(A + 'stratoshark', 3)]},
}

# --------------------------------------------------------------------------------------------------------- landmarks
# name: (biomes, max_slope, max_water, clear_site)
LANDMARKS = {
    # Slopes are generous because the site is cleared (LandmarkPiece) and given a foundation; the first pack test with
    # tighter limits found the nearest landmark ~800 blocks away.
    'gibbet_spire': (['gnashwood_wilds', 'hushed_barrens'], 24, 3, True),
    'hanging_gaol': (['hushed_barrens'], 28, 3, True),
    'rookery': (['talon_spires'], 48, 4, False),
    'brood_hive': (['gnashwood_wilds'], 24, 3, True),
    'carrion_field': (['gnashwood_wilds', 'hushed_barrens', 'talon_spires'], 16, 3, True),
    'camp_intact': (['gnashwood_wilds', 'hushed_barrens', 'talon_spires'], 12, 2, True),
    'camp_ransacked': (['gnashwood_wilds', 'hushed_barrens'], 12, 2, True),
    'camp_torn': (['talon_spires', 'hushed_barrens'], 12, 2, True),
    'wayside_fallen_gibbet': (['gnashwood_wilds', 'hushed_barrens', 'talon_spires', 'rustbone_scar'], 8, 1, False),
    'wayside_impaled': (['gnashwood_wilds', 'hushed_barrens', 'rustbone_scar'], 8, 1, False),
    'wayside_egg_cluster': (['gnashwood_wilds', 'talon_spires'], 8, 1, False),
    'wayside_claw_stone': (['hushed_barrens', 'talon_spires', 'rustbone_scar'], 8, 1, False),
    'great_cage': (['rustbone_scar'], 32, 3, True),
}
SETS = {
    # One set for the major landmarks, so two of them never overlap; the game tries them in weighted order per site.
    'major_landmarks': (['gibbet_spire', 'hanging_gaol', 'rookery', 'brood_hive', 'carrion_field'], [4, 3, 4, 3, 3], 20, 9, 917264511,
                        ('great_cage', 6)),
    'camps': (['camp_intact', 'camp_ransacked', 'camp_torn'], [2, 1, 1], 14, 5, 228471, ('major_landmarks', 4)),
    'waysides': (['wayside_fallen_gibbet', 'wayside_impaled', 'wayside_egg_cluster', 'wayside_claw_stone'], [1, 1, 1, 1], 6, 2,
                 66128031, ('major_landmarks', 3)),
    'great_cage': (['great_cage'], [1], 48, 24, 403118277, None),
}
LENS = {'cages': ['gibbet_spire', 'hanging_gaol'], 'lairs': ['rookery', 'brood_hive', 'carrion_field'],
        'camps': ['camp_intact', 'camp_ransacked', 'camp_torn'], 'great_cage': ['great_cage']}


def worldgen():
    for old in ('worldgen/structure/cage_tower.json', 'worldgen/structure_set/cage_towers.json',
                'tags/worldgen/structure/cage_towers.json', 'tags/worldgen/biome/has_structure/cage_tower.json'):
        if os.path.exists(d(old)):
            os.remove(d(old))
    for name, (biomes, slope, water, clear) in LANDMARKS.items():
        side = json.load(open(d('landmark', name + '.json')))
        write(d('worldgen', 'structure', name + '.json'), {
            'type': f'{NS}:landmark', 'biomes': f'#{NS}:has_structure/{name}', 'step': 'surface_structures',
            'spawn_overrides': {}, 'terrain_adaptation': 'none', 'template': f'{NS}:{name}', 'ground': side['ground'],
            'max_slope': slope, 'max_water': water, 'foundation': name != 'carrion_field', 'clear_site': clear})
        write(d('tags', 'worldgen', 'biome', 'has_structure', name + '.json'), {'values': [f'{NS}:{b}' for b in biomes]})
    for name, (structs, weights, spacing, sep, salt, excl) in SETS.items():
        placement = {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}
        if excl:
            placement['exclusion_zone'] = {'other_set': f'{NS}:{excl[0]}', 'chunk_count': excl[1]}
        write(d('worldgen', 'structure_set', name + '.json'),
              {'structures': [{'structure': f'{NS}:{s}', 'weight': w} for s, w in zip(structs, weights)], 'placement': placement})
    write(d('tags', 'worldgen', 'structure', 'landmarks.json'), {'values': [f'{NS}:{s}' for s in LANDMARKS]})
    for group, structs in LENS.items():
        write(d('tags', 'worldgen', 'structure', 'lens', group + '.json'), {'values': [f'{NS}:{s}' for s in structs]})


# ------------------------------------------------------------------------------------------------------------- biomes
def biomes():
    base = json.load(open(d('worldgen', 'biome', 'gnashwood_wilds.json')))
    barrens = json.load(open(d('worldgen', 'biome', 'hushed_barrens.json')))

    def spawners(monsters):
        s = {k: [] for k in base['spawners']}
        s['monster'] = [{'type': t, 'weight': w, 'minCount': lo, 'maxCount': hi} for t, w, lo, hi in monsters]
        return s

    # Natural spawns are deliberately thin (the mob cap still applies): the landmarks are where the fights are.
    base['spawners'] = spawners([(A + 'mantis', 20, 1, 2), (A + 'scorpion', 15, 1, 2), (A + 'termite', 10, 2, 3),
                                 ('minecraft:spider', 30, 1, 2)])
    barrens['spawners'] = spawners([(A + 'scorpion', 10, 1, 1), ('minecraft:husk', 20, 1, 2)])
    write(d('worldgen', 'biome', 'gnashwood_wilds.json'), base)
    write(d('worldgen', 'biome', 'hushed_barrens.json'), barrens)

    talon = json.loads(json.dumps(base))
    talon['temperature'] = 0.3
    talon['downfall'] = 0.4
    talon['effects'].update({'sky_color': 9016271, 'fog_color': 10530494, 'grass_color': 8429428, 'foliage_color': 7186292})
    talon['effects']['particle'] = {'options': {'type': 'minecraft:white_ash'}, 'probability': 0.002}
    talon['spawners'] = spawners([(A + 'scorpion', 10, 1, 1), ('minecraft:spider', 10, 1, 1)])
    talon['features'][1] = []
    talon['features'][9] = [f'{NS}:talon_spire', f'{NS}:islet', 'minecraft:patch_grass_taiga', 'minecraft:trees_windswept_hills']
    write(d('worldgen', 'biome', 'talon_spires.json'), talon)

    scar = json.loads(json.dumps(barrens))
    scar['temperature'] = 1.2
    scar['downfall'] = 0.0
    scar['has_precipitation'] = False
    scar['effects'].update({'sky_color': 12870492, 'fog_color': 10052676, 'grass_color': 10119514, 'foliage_color': 9467226,
                            'water_color': 9845049})
    scar['effects']['particle'] = {'options': {'type': 'minecraft:crimson_spore'}, 'probability': 0.004}
    scar['spawners'] = spawners([(A + 'scorpion', 15, 1, 2), (A + 'mantis', 5, 1, 1)])
    feats = scar['features']
    feats[9] = [f'{NS}:scar_ground', f'{NS}:rib_arch'] + [f for f in feats[9] if 'tree' not in f]
    write(d('worldgen', 'biome', 'rustbone_scar.json'), scar)

    for shape, placement in {
        'talon_spire': [{'type': 'minecraft:rarity_filter', 'chance': 3}],
        'islet': [{'type': 'minecraft:rarity_filter', 'chance': 5}],
        'rib_arch': [{'type': 'minecraft:rarity_filter', 'chance': 4}],
        'scar_ground': [{'type': 'minecraft:count', 'count': 3}],
    }.items():
        write(d('worldgen', 'configured_feature', shape + '.json'), {'type': f'{NS}:terrain', 'config': {'shape': shape}})
        write(d('worldgen', 'placed_feature', shape + '.json'), {'feature': f'{NS}:{shape}', 'placement': placement + [
            {'type': 'minecraft:in_square'}, {'type': 'minecraft:heightmap', 'heightmap': 'WORLD_SURFACE_WG'},
            {'type': 'minecraft:biome'}]})

    # The frontier's terrain: vanilla 1.21.1 overworld noise (tools/vanilla, printed from the game jar by
    # .github/workflows/vanilla_probe.yml) with the sea drained. The first pack test found two thirds of all landmark
    # sites under water; with no sea level, oceans and rivers become dry basins and canyons, and aquifers are off so
    # they stay dry. Underground lava lakes and springs remain.
    noise = json.load(open(os.path.join(os.path.dirname(__file__), 'vanilla', 'overworld_noise_settings_1.21.1.json')))
    noise['sea_level'] = -64
    noise['aquifers_enabled'] = False
    write(d('worldgen', 'noise_settings', 'frontier.json'), noise)
    dim = json.load(open(d('dimension', 'frontier.json')))
    dim['generator']['settings'] = f'{NS}:frontier'
    full = [-1.0, 1.0]

    def point(b, temp, hum, weird):
        return {'biome': f'{NS}:{b}', 'parameters': {'temperature': temp, 'humidity': hum, 'continentalness': full, 'erosion': full,
                                                     'weirdness': weird, 'depth': 0.0, 'offset': 0.0}}

    dim['generator']['biome_source']['biomes'] = [
        point('gnashwood_wilds', [-0.2, 1.0], [-0.35, 1.0], [-1.0, 0.55]),
        point('talon_spires', [-1.0, -0.2], [-0.35, 1.0], [-1.0, 0.55]),
        point('hushed_barrens', full, [-1.0, -0.35], [-1.0, 0.55]),
        point('rustbone_scar', full, full, [0.55, 1.0]),
    ]
    write(d('dimension', 'frontier.json'), dim)


# ------------------------------------------------------------------------------------------------------------ loot
def item(name, weight=1, lo=1, hi=1, chance=None):
    e = {'type': 'minecraft:item', 'name': name, 'weight': weight}
    if hi > 1 or lo > 1:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}}]
    return e


def book(levels=30, weight=1):
    return {'type': 'minecraft:item', 'name': 'minecraft:book', 'weight': weight,
            'functions': [{'function': 'minecraft:enchant_with_levels', 'levels': levels, 'options': '#minecraft:on_random_loot'}]}


def pool(entries, lo=1, hi=1, chance=None):
    p = {'rolls': lo if lo == hi else {'type': 'minecraft:uniform', 'min': lo, 'max': hi}, 'bonus_rolls': 0.0, 'entries': entries}
    if chance is not None:
        p['conditions'] = [{'condition': 'minecraft:random_chance', 'chance': chance}]
    return p


def table(*pools):
    return {'type': 'minecraft:chest', 'pools': list(pools)}


U = f'{NS}:'
LOOT = {
    'gibbet': table(pool([item('minecraft:bone', 4, 2, 5), item('minecraft:chain', 2, 1, 3), item('minecraft:rotten_flesh', 3, 2, 6),
                          item(A + 'raw_bug_meat', 3, 1, 3), item(A + 'chitin', 2, 1, 3), item('minecraft:iron_nugget', 2, 3, 9)], 3, 5),
                    pool([item(A + 'mantis_claw')], chance=0.3)),
    'swarm_pen': table(pool([item(A + 'chitin', 4, 2, 5), item(A + 'raw_bug_meat', 3, 2, 4), item('minecraft:arrow', 2, 6, 14),
                             item('minecraft:iron_ingot', 2, 1, 3), item('minecraft:bread', 2, 2, 4)], 3, 5),
                       pool([item(A + 'mantis_claw', 1, 1, 2)], chance=0.6)),
    'hatchery': table(pool([item(A + 'chitin', 3, 1, 4), item('minecraft:honeycomb', 2, 1, 3), item(A + 'raw_bug_meat', 3, 1, 3),
                            item('minecraft:slime_ball', 2, 1, 3), item('minecraft:experience_bottle', 1, 2, 5)], 3, 5),
                      pool([item(A + 'springbug_leg')], chance=0.5)),
    'aerie': table(pool([item('minecraft:feather', 3, 3, 8), item('minecraft:phantom_membrane', 2, 1, 2), item('minecraft:gold_ingot', 2, 1, 3),
                         item('minecraft:spectral_arrow', 2, 4, 10)], 3, 4),
                   pool([item(A + 'stratoshark_fin')], chance=0.7), pool([item(A + 'brutalfly_wing')], chance=0.25)),
    'crown_vault': table(pool([item('minecraft:diamond', 3, 1, 3), item('minecraft:experience_bottle', 3, 6, 12), book(30, 3),
                               item('minecraft:golden_apple', 2, 1, 2)], 3, 4),
                         pool([item(A + 'uranium_nugget', 1, 3, 6)]), pool([item(A + 'titanium_nugget', 1, 3, 6)]),
                         pool([item(A + 'mantis_claw', 1, 1, 2)]), pool([item('minecraft:netherite_scrap')], chance=0.15)),
    'gaol_cell': table(pool([item('minecraft:bone', 4, 1, 4), item('minecraft:chain', 3, 1, 2), item('minecraft:lead', 2),
                             item('minecraft:name_tag', 1), item(A + 'raw_bug_meat', 2, 1, 2), item(A + 'duct_tape', 1)], 2, 4)),
    'gaol_vault': table(pool([item('minecraft:diamond', 3, 1, 3), book(30, 3), item('minecraft:experience_bottle', 3, 6, 12)], 3, 4),
                        pool([item(A + 'uranium_nugget', 1, 4, 8)]), pool([item(A + 'titanium_nugget', 1, 4, 8)]),
                        pool([item(A + 'emperor_scorpion_stinger')], chance=0.35), pool([item(A + 'hercules_horn')], chance=0.35),
                        pool([item(A + 'critter_cage')], chance=0.3)),
    'camp_supply': table(pool([item('minecraft:bread', 4, 2, 5), item('minecraft:cooked_mutton', 3, 2, 4), item('minecraft:torch', 4, 4, 12),
                               item('minecraft:arrow', 3, 6, 16), item('minecraft:ladder', 2, 4, 8), item('minecraft:scaffolding', 2, 4, 8),
                               item('minecraft:golden_carrot', 1, 2, 4), item('minecraft:iron_ingot', 2, 1, 3)], 4, 6),
                         pool([item(A + 'bug_spray')], chance=0.25)),
    'camp_survey': table(pool([item('minecraft:map', 3), item('minecraft:compass', 2), item('minecraft:paper', 3, 2, 6),
                               item('minecraft:writable_book', 2), item('minecraft:amethyst_shard', 2, 1, 4)], 2, 4),
                         pool([item(U + 'rift_lens')], chance=0.6)),
    'rookery_clutch': table(pool([item('minecraft:feather', 3, 4, 10), item('minecraft:egg', 2, 2, 6), item('minecraft:bone', 3, 2, 5),
                                  item('minecraft:gold_nugget', 2, 4, 12), item('minecraft:diamond', 1)], 3, 5),
                            pool([item(A + 'stratoshark_fin', 1, 1, 2)]), pool([item(A + 'nightmare_scale')], chance=0.4)),
    'hive_larder': table(pool([item('minecraft:honey_bottle', 3, 1, 3), item('minecraft:honeycomb', 3, 2, 5), item(A + 'raw_bug_meat', 3, 2, 5),
                               item(A + 'flytrap_goo', 2, 1, 2), item(A + 'chitin', 3, 2, 4)], 3, 6)),
    'hive_royal': table(pool([item('minecraft:diamond', 3, 1, 3), book(30, 3), item(A + 'chitin_block', 2, 2, 4),
                              item('minecraft:experience_bottle', 2, 6, 12)], 3, 4),
                        pool([item(A + 'hercules_horn')], chance=0.5), pool([item(A + 'uranium_ingot')], chance=0.3),
                        pool([item(A + 'titanium_ingot')], chance=0.3)),
    'carrion_gullet': table(pool([item('minecraft:bone', 4, 3, 7), item('minecraft:rotten_flesh', 3, 3, 8), item('minecraft:gold_ingot', 2, 1, 3),
                                  item(A + 'chitin', 2, 1, 3), item('minecraft:iron_sword', 1)], 3, 5),
                            pool([item(A + 'mantis_claw'), item(A + 'stratoshark_fin')], chance=0.6),
                            pool([item(A + 'emperor_scorpion_stinger')], chance=0.15)),
    'great_cage_cell': table(pool([item('minecraft:chain', 3, 1, 3), item('minecraft:bone', 3, 2, 6), item(A + 'uranium_nugget', 2, 2, 5),
                                   item(A + 'titanium_nugget', 2, 2, 5), item('minecraft:diamond', 1)], 3, 5),
                             pool([item(A + 'basilisk_fang')], chance=0.15), pool([item(A + 'primordial_scute')], chance=0.1)),
    'great_cage_vault': table(pool([item('minecraft:diamond', 3, 2, 5), book(39, 3), item('minecraft:experience_bottle', 3, 12, 24),
                                    item('minecraft:enchanted_golden_apple', 1)], 4, 5),
                              pool([item(A + 'uranium_ingot', 1, 1, 2)]), pool([item(A + 'titanium_ingot', 1, 1, 2)]),
                              pool([item(A + 'basilisk_fang', 1, 1, 2)]), pool([item('minecraft:netherite_scrap', 1, 1, 2)]),
                              pool([{'type': 'minecraft:loot_table', 'value': f'{NS}:compat/marvel_vault', 'weight': 1}])),
}


def loot():
    for name, t in LOOT.items():
        write(d('loot_table', 'chests', name + '.json'), t)
    # Only loaded when Marvel Superheroes is present: an X-Gene for the serums (the Hulk serum also wants the vault's uranium).
    compat = table(pool([item('marvel:x_genes')], chance=0.35))
    compat['neoforge:conditions'] = [{'type': 'neoforge:mod_loaded', 'modid': 'marvel'}]
    write(d('loot_table', 'compat', 'marvel_vault.json'), compat)


# --------------------------------------------------------------------------------------------------------- recipes
def ing(i):
    return {'tag': i[1:]} if i.startswith('#') else {'item': i}


def shaped(name, pattern, key, result, count=1, category='misc'):
    write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shaped', 'category': category, 'pattern': pattern,
                                        'key': {k: ing(v) for k, v in key.items()}, 'result': {'id': result, 'count': count}})


def shapeless(name, items, result, count=1, category='misc'):
    write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shapeless', 'category': category,
                                        'ingredients': [ing(i) for i in items], 'result': {'id': result, 'count': count}})


def recipes():
    shaped('swarmbreaker', [' C ', 'CHC', ' S '], {'C': A + 'mantis_claw', 'H': U + 'hive_heart', 'S': 'minecraft:netherite_sword'},
           U + 'swarmbreaker', category='equipment')
    shapeless('cagewright_key', [U + 'cage_trophy', U + 'rookery_talon', U + 'hive_heart', A + 'uranium_ingot', 'minecraft:tripwire_hook'],
              U + 'cagewright_key')
    shaped('rift_lens', [' A ', 'ASA', ' C '], {'A': 'minecraft:amethyst_shard', 'S': 'minecraft:spyglass', 'C': A + 'chitin'},
           U + 'rift_lens', category='equipment')
    shaped('cagewright_shackle', ['C C', 'CTC', ' L '], {'C': 'minecraft:chain', 'T': U + 'rookery_talon', 'L': 'minecraft:lead'},
           U + 'cagewright_shackle', category='equipment')
    shaped('cage_beacon', ['BOB', 'OHO', 'BOB'], {'B': 'minecraft:iron_bars', 'O': 'minecraft:crying_obsidian', 'H': U + 'great_cage_heart'},
           U + 'cage_beacon')


# ----------------------------------------------------------------------------------------------------- advancements
def adv(name, parent, icon, criteria, frame='task', hidden=False, requirements=None):
    a = {'display': {'icon': {'id': icon}, 'title': {'translate': f'advancement.{NS}.{name}'},
                     'description': {'translate': f'advancement.{NS}.{name}.desc'}, 'frame': frame, 'show_toast': True,
                     'announce_to_chat': frame != 'task', 'hidden': hidden}, 'criteria': criteria}
    if parent:
        a['parent'] = f'{NS}:{parent}'
    else:
        a['display']['background'] = 'minecraft:textures/block/polished_blackstone_bricks.png'
    if requirements:
        a['requirements'] = requirements
    write(d('advancement', name + '.json'), a)


def has(i):
    return {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': i}]}}


def at(structure):
    return {'trigger': 'minecraft:location', 'conditions': {'player': [{'condition': 'minecraft:entity_properties', 'entity': 'this',
                                                                         'predicate': {'location': {'structures': structure}}}]}}


def advancements():
    for old in ('caged', 'trophy'):
        if os.path.exists(d('advancement', old + '.json')):
            os.remove(d('advancement', old + '.json'))
    adv('root', None, U + 'rift_shard', {'c': has(U + 'rift_shard')})
    adv('enter', 'root', 'minecraft:crying_obsidian', {'c': {'trigger': 'minecraft:changed_dimension',
                                                             'conditions': {'to': f'{NS}:frontier'}}})
    adv('survey', 'enter', U + 'rift_lens', {'camp': at(f'#{NS}:lens/camps'), 'lens': has(U + 'rift_lens')}, requirements=[['camp', 'lens']])
    adv('caged', 'enter', 'minecraft:iron_bars', {'c': at(f'#{NS}:lens/cages')})
    adv('carrion', 'enter', 'minecraft:bone_block', {'c': at(f'{NS}:carrion_field')})
    adv('trophy', 'caged', U + 'cage_trophy', {'c': has(U + 'cage_trophy')}, frame='goal')
    adv('talon', 'enter', U + 'rookery_talon', {'c': has(U + 'rookery_talon')}, frame='goal')
    adv('hive_heart', 'enter', U + 'hive_heart', {'c': has(U + 'hive_heart')}, frame='goal')
    adv('swarmbreaker', 'hive_heart', U + 'swarmbreaker', {'c': has(U + 'swarmbreaker')})
    adv('shackle', 'talon', U + 'cagewright_shackle', {'c': has(U + 'cagewright_shackle')})
    adv('key', 'trophy', U + 'cagewright_key', {'c': has(U + 'cagewright_key')}, frame='goal')
    adv('great_cage', 'key', 'minecraft:lodestone', {'c': at(f'{NS}:great_cage')})
    adv('cage_heart', 'great_cage', U + 'great_cage_heart', {'c': has(U + 'great_cage_heart')}, frame='challenge')
    adv('beacon', 'cage_heart', U + 'cage_beacon', {'c': has(U + 'cage_beacon')})


# ------------------------------------------------------------------------------------------------------------ tags
def tags():
    write(d('tags', 'block', 'brood.json'), {'values': ['minecraft:turtle_egg', 'minecraft:frogspawn']})
    # Better Combat (in Integrated Boogaloo) gives the Swarmbreaker glaive move sets; ignored when Better Combat is absent.
    write(os.path.join(DATA, 'weapon_attributes', 'swarmbreaker.json'), {'parent': 'bettercombat:glaive'})


# ------------------------------------------------------------------------------------------------------------ sounds
SOUNDS = {
    'landmark.discover': ('block.bell.resonate', 0.6, 'A landmark looms'),
    'landmark.wake': ('entity.warden.listening_angry', 0.8, 'The cage wakes'),
    'landmark.wave': ('block.beehive.work', 0.6, 'Something stirs'),
    'landmark.gate': ('block.chain.break', 0.5, 'A gate gives way'),
    'landmark.conquer': ('ui.toast.challenge_complete', 1.0, 'Landmark conquered'),
    'elite.tell': ('entity.ravager.roar', 0.8, 'An elite readies itself'),
    'elite.slam': ('entity.warden.attack_impact', 0.7, 'A crushing slam'),
    'finale.pylon': ('block.respawn_anchor.deplete', 0.6, 'A pylon shatters'),
    'finale.shield': ('block.amethyst_block.resonate', 0.7, 'The pylons shield it'),
    'brood.crack': ('entity.turtle.egg_crack', 0.7, 'Eggs crack'),
    'item.shackle': ('block.chain.place', 0.7, 'The shackle binds'),
    'item.lens': ('item.spyglass.use', 0.8, 'The lens focuses'),
}
# The creatures' own sounds: files synthesised by tools/sounds/synth.py (event: (files, subtitle)).
CREATURE_SOUNDS = {
    'gnashback.ambient': (['gnashback/ambient'], 'Gnashback chitters'),
    'gnashback.hurt': (['gnashback/hurt'], 'Gnashback hurts'),
    'gnashback.death': (['gnashback/death'], 'Gnashback dies'),
    'gnashback.bite': (['gnashback/bite'], 'Gnashback bites'),
    'gnashback.scrape': (['gnashback/scrape'], 'Gnashback scrapes the ground'),
    'gnashback.charge': (['gnashback/charge'], 'Gnashback charges'),
    'gnashback.impact': (['gnashback/impact'], 'Gnashback crashes'),
    'shrikewing.ambient': (['shrikewing/ambient1', 'shrikewing/ambient2'], 'Shrikewing cries'),
    'shrikewing.hurt': (['shrikewing/hurt'], 'Shrikewing hurts'),
    'shrikewing.death': (['shrikewing/death'], 'Shrikewing dies'),
    'shrikewing.screech': (['shrikewing/screech'], 'Shrikewing screeches: it is about to dive'),
    'shrikewing.flap': (['shrikewing/flap'], 'Wings beat'),
    'matriarch.ambient': (['matriarch/ambient1', 'matriarch/ambient2'], 'The Matriarch rumbles'),
    'matriarch.hurt': (['matriarch/hurt1', 'matriarch/hurt2'], 'The Matriarch hurts'),
    'matriarch.death': (['matriarch/death'], 'The Matriarch falls'),
    'matriarch.roar': (['matriarch/roar'], 'The Matriarch roars'),
    'matriarch.brood': (['matriarch/brood'], 'The brood sac opens'),
    'matriarch.sweep_tell': (['matriarch/sweep_tell'], 'Scythes drawn back'),
    'matriarch.sweep': (['matriarch/sweep'], 'Scythes sweep'),
    'matriarch.spit': (['matriarch/spit'], 'The Matriarch spits acid'),
    'matriarch.slam': (['matriarch/slam'], 'The Matriarch lands'),
    'matriarch.acid': (['matriarch/acid'], 'Acid sizzles'),
}


def sounds():
    out = {}
    for name, (event, pitch, sub) in SOUNDS.items():
        out[name] = {'subtitle': f'subtitles.{NS}.{name}', 'sounds': [{'name': f'minecraft:{event}', 'type': 'event', 'pitch': pitch}]}
    for name, (files, sub) in CREATURE_SOUNDS.items():
        missing = [f for f in files if not os.path.exists(os.path.join(ASSETS, 'sounds', f + '.ogg'))]
        assert not missing, f'run tools/sounds/synth.py first: missing {missing}'
        out[name] = {'subtitle': f'subtitles.{NS}.{name}', 'sounds': [f'{NS}:{f}' for f in files]}
    write(os.path.join(ASSETS, 'sounds.json'), out)
    subs = {f'subtitles.{NS}.{k}': v[2] for k, v in SOUNDS.items()}
    subs.update({f'subtitles.{NS}.{k}': v[1] for k, v in CREATURE_SOUNDS.items()})
    return subs


# -------------------------------------------------------------------------------------------------------- models
ITEMS = ['rift_shard', 'cage_trophy', 'swarmbreaker', 'rookery_talon', 'hive_heart', 'great_cage_heart', 'cagewright_key', 'rift_lens',
         'cagewright_shackle']


def models():
    for i in ITEMS:
        parent = 'minecraft:item/handheld' if i == 'swarmbreaker' else 'minecraft:item/generated'
        write(os.path.join(ASSETS, 'models', 'item', i + '.json'), {'parent': parent, 'textures': {'layer0': f'{NS}:item/{i}'}})
    write(os.path.join(ASSETS, 'models', 'block', 'cage_beacon.json'), {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
        'top': f'{NS}:block/cage_beacon_top', 'bottom': f'{NS}:block/cage_beacon_bottom', 'side': f'{NS}:block/cage_beacon_side'}})
    write(os.path.join(ASSETS, 'models', 'item', 'cage_beacon.json'), {'parent': f'{NS}:block/cage_beacon'})
    write(os.path.join(ASSETS, 'blockstates', 'cage_beacon.json'), {'variants': {'': {'model': f'{NS}:block/cage_beacon'}}})
    write(d('loot_table', 'blocks', 'cage_beacon.json'), {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'bonus_rolls': 0.0, 'entries': [
        {'type': 'minecraft:item', 'name': U + 'cage_beacon'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'mineable', 'pickaxe.json'), {'values': [U + 'cage_beacon']})
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'needs_diamond_tool.json'), {'values': [U + 'cage_beacon']})


# ------------------------------------------------------------------------------------------------------------- lang
LANG = {
    'itemGroup.unstable_frontiers': 'Unstable Frontiers',
    'item.unstable_frontiers.rift_shard': 'Unstable Rift Shard',
    'item.unstable_frontiers.rift_shard.tip0': 'Use to cross into the Unstable Frontier; use there to return.',
    'item.unstable_frontiers.rift_shard.tip1': 'Expedition camps lie near where you arrive. Read the journals.',
    'item.unstable_frontiers.rift_shard.tip2': 'Lost your way? /frontier return takes you home.',
    'item.unstable_frontiers.cage_trophy': 'Cage Trophy',
    'item.unstable_frontiers.cage_trophy.tip0': 'Taken from the guardian of a cage tower or the Hanging Gaol.',
    'item.unstable_frontiers.cage_trophy.tip1': 'One of the three parts of the Cagewright\'s Key.',
    'item.unstable_frontiers.cage_trophy.tip2': 'Also repairs the Swarmbreaker.',
    'item.unstable_frontiers.rookery_talon': 'Rookery Talon',
    'item.unstable_frontiers.rookery_talon.tip0': 'Torn from the Rookmother.',
    'item.unstable_frontiers.rookery_talon.tip1': 'One of the three parts of the Cagewright\'s Key.',
    'item.unstable_frontiers.rookery_talon.tip2': 'Forges and repairs the Cagewright\'s Shackle.',
    'item.unstable_frontiers.hive_heart': 'Hive Heart',
    'item.unstable_frontiers.hive_heart.tip0': 'Still beating. Cut from the Hive Tyrant.',
    'item.unstable_frontiers.hive_heart.tip1': 'One of the three parts of the Cagewright\'s Key.',
    'item.unstable_frontiers.hive_heart.tip2': 'Forges the Swarmbreaker.',
    'item.unstable_frontiers.great_cage_heart': 'Heart of the Great Cage',
    'item.unstable_frontiers.great_cage_heart.tip0': 'What kept the Cagewright\'s Beast alive.',
    'item.unstable_frontiers.great_cage_heart.tip1': 'Builds a Cage Beacon: safe ground in the frontier,',
    'item.unstable_frontiers.great_cage_heart.tip2': 'and an anchor your Rift Shard returns you to.',
    'item.unstable_frontiers.cagewright_key': 'Cagewright\'s Key',
    'item.unstable_frontiers.cagewright_key.tip0': 'Opens the lock of the Great Cage, in the Rustbone Scar.',
    'item.unstable_frontiers.cagewright_key.tip1': 'Use it on the lodestone lock beside the south door.',
    'item.unstable_frontiers.cagewright_key.tip2': 'What is inside wakes when the lock turns.',
    'item.unstable_frontiers.rift_lens': 'Rift Lens',
    'item.unstable_frontiers.rift_lens.tip0': 'Use in the frontier to survey the nearest cage, lair and camp.',
    'item.unstable_frontiers.rift_lens.tip1': 'The Great Cage shows once you carry the Cagewright\'s Key.',
    'item.unstable_frontiers.cagewright_shackle': 'Cagewright\'s Shackle',
    'item.unstable_frontiers.cagewright_shackle.tip0': 'Use on a hostile creature below a third of its health.',
    'item.unstable_frontiers.cagewright_shackle.tip1': 'It fights for you for 60 seconds, then crumbles. No bosses.',
    'item.unstable_frontiers.cagewright_shackle.tip2': 'Repair with Rookery Talons.',
    'item.unstable_frontiers.swarmbreaker': 'Swarmbreaker',
    'item.unstable_frontiers.swarmbreaker.tip0': 'Deals 50% more damage to insects.',
    'item.unstable_frontiers.swarmbreaker.tip1': 'Use to Pounce: leap, and land in a shockwave that smashes egg clutches',
    'item.unstable_frontiers.swarmbreaker.tip2': 'and staggers the insects it hits. Repair with Cage Trophies.',
    'block.unstable_frontiers.cage_beacon': 'Cage Beacon',
    'biome.unstable_frontiers.gnashwood_wilds': 'Gnashwood Wilds',
    'biome.unstable_frontiers.hushed_barrens': 'Hushed Barrens',
    'biome.unstable_frontiers.talon_spires': 'Talon Spires',
    'biome.unstable_frontiers.rustbone_scar': 'Rustbone Scar',
    'landmark.unstable_frontiers.cage_tower.subtitle': 'Every cage here was full once.',
    'landmark.unstable_frontiers.cage_tower.conquered': 'The cages are empty. The vault is open.',
    'landmark.unstable_frontiers.rookery.subtitle': 'Look up.',
    'landmark.unstable_frontiers.rookery.conquered': 'The nest is quiet.',
    'landmark.unstable_frontiers.hive.subtitle': 'The walls are breathing.',
    'landmark.unstable_frontiers.hive.conquered': 'The resin wall behind the throne gives way.',
    'landmark.unstable_frontiers.carrion.subtitle': 'Something is still feeding.',
    'landmark.unstable_frontiers.carrion.conquered': 'The feeding is over, for now.',
    'landmark.unstable_frontiers.camp.subtitle': 'Ilsa Vane\'s expedition stopped here.',
    'landmark.unstable_frontiers.camp.conquered': '',
    'landmark.unstable_frontiers.great_cage.subtitle': 'The Cagewright built this to hold one thing.',
    'landmark.unstable_frontiers.great_cage.conquered': 'The Great Cage is broken. The vault below is open.',
    'zone.unstable_frontiers.waves.start': 'They come in waves.',
    'zone.unstable_frontiers.ambush.start': 'An ambush!',
    'zone.unstable_frontiers.brood.start': 'Break the clutches, or they never stop hatching.',
    'zone.unstable_frontiers.cell.start': 'The prisoner wakes.',
    'zone.unstable_frontiers.roost.start': 'The roost takes wing.',
    'zone.unstable_frontiers.guardian.start': 'The guardian rises.',
    'zone.unstable_frontiers.finale.start': 'Break the four pylons. While they stand, it cannot be hurt for long.',
    'elite.unstable_frontiers.slam.tell': '%s rears up. Get out of the ring!',
    'elite.unstable_frontiers.rally.tell': '%s calls its kin.',
    'elite.unstable_frontiers.pounce.tell': '%s crouches to spring.',
    'elite.unstable_frontiers.screech.tell': '%s draws breath to shriek.',
    'bar.unstable_frontiers.pylons': ' (pylons: %s)',
    'message.unstable_frontiers.sealed': '%s is sealed. Clear the rest first (%s).',
    'message.unstable_frontiers.finale_locked': 'The Great Cage is locked. The Cagewright\'s Key turns it, at the lodestone by the south door.',
    'message.unstable_frontiers.roster_missing': 'This fight cannot start: roster \'%s\' is missing from the mod\'s data. See latest.log for the fix.',
    'message.unstable_frontiers.roster_unusable': 'This fight cannot start: roster \'%s\' needs creatures that are not installed: %s. Install Antarchy 2.2.9 (Integrated Boogaloo 1.0.8) or fix the roster.',
    'message.unstable_frontiers.busy': 'It waits: too many fights are running on this server.',
    'message.unstable_frontiers.brood_left': '%s clutches still whole.',
    'message.unstable_frontiers.brood_broken': 'The brood is broken. Nothing more will hatch.',
    'message.unstable_frontiers.brood_smashed': 'Smashed %s clutches.',
    'message.unstable_frontiers.zone_cleared': '%s falls silent.',
    'message.unstable_frontiers.conquered': '%s conquered',
    'message.unstable_frontiers.reward': 'You take: %s',
    'message.unstable_frontiers.lock_open': 'The lock has already turned.',
    'message.unstable_frontiers.key_no_lock': 'The key fits only the lock of the Great Cage.',
    'message.unstable_frontiers.shield_down': 'The last pylon falls. It can be hurt now.',
    'message.unstable_frontiers.pylon_down': 'A pylon shatters. %s still stand.',
    'message.unstable_frontiers.shielded': 'The pylons shield it. Break them!',
    'message.unstable_frontiers.problems': 'Unstable Frontiers found %s data problems (fights that cannot start):',
    'message.unstable_frontiers.overflight': 'Wings, somewhere overhead.',
    'message.unstable_frontiers.shackle_boss': 'Nothing can shackle that.',
    'message.unstable_frontiers.shackle_strong': 'It is too strong yet. Wear it down to a third first.',
    'message.unstable_frontiers.shackle_bound': '%s is bound to you for 60 seconds.',
    'message.unstable_frontiers.beacon_anchored': 'The Cage Beacon holds. Your Rift Shard will bring you here.',
    'message.unstable_frontiers.lens_elsewhere': 'The lens shows only the frontier.',
    'message.unstable_frontiers.lens_title': 'Through the Rift Lens:',
    'message.unstable_frontiers.lens_none': ' %s: nothing within sight.',
    'message.unstable_frontiers.lens_line': ' %s: %s blocks %s (%s)',
    'message.unstable_frontiers.lens_clouded': ' Far off, something vast. The lens clouds over. (Carry the Cagewright\'s Key.)',
    'lens.unstable_frontiers.cages': 'Cage',
    'lens.unstable_frontiers.lairs': 'Lair',
    'lens.unstable_frontiers.camps': 'Camp',
    'lens.unstable_frontiers.great_cage': 'The Great Cage',
    'lens.unstable_frontiers.state.conquered': 'conquered',
    'lens.unstable_frontiers.state.standing': 'standing',
    'lens.unstable_frontiers.state.unknown': 'unvisited',
    'message.unstable_frontiers.arrive': 'The Unstable Frontier. Smoke from an expedition camp, %s blocks to the %s.',
    'message.unstable_frontiers.arrive_none': 'The Unstable Frontier. No camp in sight; travel and watch the skyline.',
    'message.unstable_frontiers.no_frontier': 'The frontier dimension is missing (is the data pack disabled?).',
    'message.unstable_frontiers.return_not_here': 'You are not in the frontier.',
    'message.unstable_frontiers.return_cooldown': 'The rift is still closing. Try again in %s s.',
    'advancement.unstable_frontiers.root': 'Unstable Frontiers',
    'advancement.unstable_frontiers.root.desc': 'Craft an Unstable Rift Shard (amethyst, crying obsidian, an eye of ender)',
    'advancement.unstable_frontiers.enter': 'Beyond the Rift',
    'advancement.unstable_frontiers.enter.desc': 'Enter the Unstable Frontier',
    'advancement.unstable_frontiers.survey': 'Survey Party',
    'advancement.unstable_frontiers.survey.desc': 'Find one of Ilsa Vane\'s expedition camps, or a Rift Lens',
    'advancement.unstable_frontiers.caged': 'Caged',
    'advancement.unstable_frontiers.caged.desc': 'Enter a Gibbet Spire or the Hanging Gaol',
    'advancement.unstable_frontiers.carrion': 'Downwind',
    'advancement.unstable_frontiers.carrion.desc': 'Find a Carrion Field, where the insects and the predators meet',
    'advancement.unstable_frontiers.trophy': 'Cage Breaker',
    'advancement.unstable_frontiers.trophy.desc': 'Defeat a cage\'s guardian and take its Cage Trophy',
    'advancement.unstable_frontiers.talon': 'Nest Robber',
    'advancement.unstable_frontiers.talon.desc': 'Defeat the Rookmother and take a Rookery Talon',
    'advancement.unstable_frontiers.hive_heart': 'Regicide',
    'advancement.unstable_frontiers.hive_heart.desc': 'Defeat the Hive Tyrant and take its heart',
    'advancement.unstable_frontiers.swarmbreaker': 'Brood-breaker',
    'advancement.unstable_frontiers.swarmbreaker.desc': 'Forge the Swarmbreaker from a Hive Heart',
    'advancement.unstable_frontiers.shackle': 'Bound',
    'advancement.unstable_frontiers.shackle.desc': 'Forge the Cagewright\'s Shackle from a Rookery Talon',
    'advancement.unstable_frontiers.key': 'The Cagewright\'s Key',
    'advancement.unstable_frontiers.key.desc': 'Join a Cage Trophy, a Rookery Talon and a Hive Heart',
    'advancement.unstable_frontiers.great_cage': 'The Great Cage',
    'advancement.unstable_frontiers.great_cage.desc': 'Stand in the Rustbone Scar, inside the Great Cage',
    'advancement.unstable_frontiers.cage_heart': 'Heart of the Cage',
    'advancement.unstable_frontiers.cage_heart.desc': 'Break the pylons and kill the Cagewright\'s Beast',
    'advancement.unstable_frontiers.beacon': 'Safe Ground',
    'advancement.unstable_frontiers.beacon.desc': 'Build a Cage Beacon',
}
for k in ('east', 'southeast', 'south', 'southwest', 'west', 'northwest', 'north', 'northeast'):
    LANG[f'direction.unstable_frontiers.{k}'] = k


def lang(extra):
    write(os.path.join(ASSETS, 'lang', 'en_us.json'), {**LANG, **extra})


def rosters():
    shutil.rmtree(d('roster'), ignore_errors=True)
    for name, r in ROSTERS.items():
        write(d('roster', name + '.json'), r)


if __name__ == '__main__':
    rosters()
    worldgen()
    biomes()
    loot()
    recipes()
    advancements()
    tags()
    models()
    lang(sounds())
    print('data written')
