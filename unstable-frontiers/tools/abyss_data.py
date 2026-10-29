"""Data for the Rift Observatory and the Astral Abyss: the dimension and its biomes, block states and models, loot,
recipes, tags, rosters, advancements, text and sounds. datagen.py imports this and folds it into its own run, so
`python3 tools/datagen.py` still regenerates everything.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources')
DATA = os.path.join(ROOT, 'data', 'unstable_frontiers')
ASSETS = os.path.join(ROOT, 'assets', 'unstable_frontiers')
NS = 'unstable_frontiers'
U = NS + ':'
A = 'antarchy:'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def d(*p):
    return os.path.join(DATA, *p)


def a(*p):
    return os.path.join(ASSETS, *p)


def m(id_, weight=1, mx=0):
    e = {'id': id_, 'weight': weight}
    if mx:
        e['max'] = mx
    return e


# ------------------------------------------------------------------------------------------------------- rosters
ROSTERS = {
    # The Rift Observatory: the rift's own creatures, and the frontier insects drawn to it.
    'observatory_gallery': {'mobs': [m(U + 'lumen_mite', 4), m(U + 'orrery_warden', 1, 1), m(A + 'wasp', 1, 1)],
                            'flyers': [m(U + 'lumen_mite', 3), m(U + 'orrery_warden', 1, 1)]},
    'observatory_vaults': {'mobs': [m(U + 'lumen_mite', 5), m(A + 'scorpion', 1, 1)]},
    'observatory_spire': {'mobs': [m(U + 'lumen_mite', 3), m(U + 'orrery_warden', 1, 1)], 'escorts': 3,
                          'elite': {'id': U + 'orrery_warden', 'title': "The Astronomer's Warden", 'bar': 'blue', 'abilities': ['rally'],
                                    'health': 3.0}},
    'observatory_residents': {'mobs': [m(U + 'lumen_mite')], 'flyers': [m(U + 'lumen_mite')]},
    # The Astral Abyss's places.
    'abyss_starwell': {'mobs': [m(U + 'lumen_mite', 5), m(U + 'orrery_warden', 1, 1)]},
    'abyss_archive': {'mobs': [m(U + 'lumen_mite', 3), m(U + 'orrery_warden', 2, 1)], 'escorts': 3,
                      'elite': {'id': U + 'orrery_warden', 'title': 'The Archivist', 'bar': 'white', 'abilities': ['rally'], 'health': 3.5}},
    'abyss_tether': {'mobs': [m(U + 'lumen_mite', 4), m(U + 'orrery_warden', 1, 1)],
                     'flyers': [m(U + 'lumen_mite', 3)]},
}

# The observatory generates in the frontier like the other landmarks (datagen.py's LANDMARKS and SETS take these).
LANDMARKS = {'rift_observatory': (['hushed_barrens', 'talon_spires', 'gnashwood_wilds'], 40, 3, True)}
SETS = {'rift_observatory': (['rift_observatory'], [1], 40, 18, 551187213, ('major_landmarks', 5))}
LENS = {'observatory': ['rift_observatory']}

# ------------------------------------------------------------------------------------------------------- dimension
SKY = {'starlit_shoals': (0x0b0d24, 0x1a1f45, 'minecraft:glow', 0.0025),
       'shattered_reach': (0x100a22, 0x241a40, 'minecraft:white_ash', 0.004),
       'eclipse_hollow': (0x14060f, 0x2a0c1c, 'minecraft:crimson_spore', 0.003)}


def dimension():
    write(d('dimension_type', 'astral_abyss.json'), {
        'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False,
        'ambient_light': 0.24, 'fixed_time': 18000, 'monster_spawn_light_level': {'type': 'minecraft:uniform', 'min_inclusive': 0, 'max_inclusive': 7},
        'monster_spawn_block_light_limit': 0, 'piglin_safe': False, 'bed_works': True, 'respawn_anchor_works': False, 'has_raids': False,
        'logical_height': 256, 'min_y': 0, 'height': 256, 'infiniburn': '#minecraft:infiniburn_end', 'effects': f'{NS}:astral_abyss'})
    write(d('dimension', 'astral_abyss.json'), {'type': f'{NS}:astral_abyss', 'generator': {
        'type': f'{NS}:abyss', 'biome_source': {'type': f'{NS}:abyss', 'shoals': f'{NS}:starlit_shoals', 'reach': f'{NS}:shattered_reach',
                                                 'hollow': f'{NS}:eclipse_hollow'}}})
    empty = {k: [] for k in ('ambient', 'axolotls', 'creature', 'misc', 'monster', 'underground_water_creature', 'water_ambient', 'water_creature')}
    for name, (sky, fog, particle, prob) in SKY.items():
        spawners = json.loads(json.dumps(empty))
        spawners['monster'] = [{'type': U + 'lumen_mite', 'weight': 20, 'minCount': 2, 'maxCount': 3}]
        if name != 'starlit_shoals':
            spawners['monster'].append({'type': U + 'orrery_warden', 'weight': 4, 'minCount': 1, 'maxCount': 1})
        write(d('worldgen', 'biome', name + '.json'), {
            'has_precipitation': False, 'temperature': 0.5, 'downfall': 0.0,
            'effects': {'sky_color': sky, 'fog_color': fog, 'water_color': 0x3a5ad8, 'water_fog_color': 0x0b1030,
                        'grass_color': 0x2fa39a, 'foliage_color': 0x2c8f8a,
                        'particle': {'options': {'type': particle}, 'probability': prob},
                        'ambient_sound': f'{NS}:abyss.ambient',
                        'mood_sound': {'sound': f'{NS}:abyss.ambient', 'tick_delay': 4000, 'block_search_extent': 8, 'offset': 2.0},
                        'music': {'sound': 'minecraft:music.end', 'min_delay': 12000, 'max_delay': 24000, 'replace_current_music': False}},
            'spawners': spawners,
            # creature density stays low: a spawn has to fit a small energy budget (see also AbyssSpawnLimit)
            'spawn_costs': {U + 'lumen_mite': {'energy_budget': 0.6, 'charge': 0.5}, U + 'orrery_warden': {'energy_budget': 0.3, 'charge': 0.7}},
            'carvers': {}, 'features': [[] for _ in range(11)]})


# --------------------------------------------------------------------------------------------------- blocks and items
CUBE = ['astral_shale', 'astral_bricks', 'chiseled_astral', 'lumen_crystal', 'astral_ore']
ITEMS = ['focusing_lens', 'coolant_heart', 'star_chart', 'astrolabe', 'sigil_shard', 'eclipse_sigil', 'raw_starmetal', 'starmetal_ingot',
         'lumen_core', 'eclipse_scale', 'blinkstone', 'corona', 'star_bolt']


def blocks():
    def state(name, variants):
        write(a('blockstates', name + '.json'), {'variants': variants})

    def model(name, obj):
        write(a('models', 'block', name + '.json'), obj)

    def item(name, parent=None, layer=None):
        if layer:
            write(a('models', 'item', name + '.json'), {'parent': 'minecraft:item/generated', 'textures': {'layer0': layer}})
        else:
            write(a('models', 'item', name + '.json'), {'parent': parent or f'{NS}:block/{name}'})

    for n in CUBE:
        model(n, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/{n}'}})
        state(n, {'': {'model': f'{NS}:block/{n}'}})
        item(n)
    model('rift_glass', {'parent': 'minecraft:block/cube_all', 'render_type': 'minecraft:translucent', 'textures': {'all': f'{NS}:block/rift_glass'}})
    state('rift_glass', {'': {'model': f'{NS}:block/rift_glass'}})
    item('rift_glass')
    model('starmoss', {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
        'top': f'{NS}:block/starmoss_top', 'side': f'{NS}:block/starmoss_side', 'bottom': f'{NS}:block/astral_shale'}})
    state('starmoss', {'': [{'model': f'{NS}:block/starmoss'}, {'model': f'{NS}:block/starmoss', 'y': 90}, {'model': f'{NS}:block/starmoss', 'y': 180},
                            {'model': f'{NS}:block/starmoss', 'y': 270}]})
    item('starmoss')
    for n in ('starbloom', 'void_tendril'):
        model(n, {'parent': 'minecraft:block/cross', 'render_type': 'minecraft:cutout', 'textures': {'cross': f'{NS}:block/{n}'}})
        state(n, {'': {'model': f'{NS}:block/{n}'}})
        item(n, layer=f'{NS}:block/{n}')
    model('void_cyst', {'parent': 'minecraft:block/block', 'render_type': 'minecraft:cutout',
                        'textures': {'particle': f'{NS}:block/void_cyst', 'all': f'{NS}:block/void_cyst'},
                        'elements': [{'from': [2, 0, 2], 'to': [14, 13, 14], 'faces': {
                            f: {'texture': '#all', 'uv': [2, 3, 14, 16] if f not in ('up', 'down') else [2, 2, 14, 14]}
                            for f in ('north', 'south', 'east', 'west', 'up', 'down')}}]})
    state('void_cyst', {'': {'model': f'{NS}:block/void_cyst'}})
    item('void_cyst')
    model('abyss_gate', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/abyss_gate'}})
    model('abyss_gate_open', {'parent': 'minecraft:block/cube_all', 'render_type': 'minecraft:translucent',
                              'textures': {'all': f'{NS}:block/abyss_gate_open'}})
    state('abyss_gate', {'open=false': {'model': f'{NS}:block/abyss_gate'}, 'open=true': {'model': f'{NS}:block/abyss_gate_open'}})
    item('abyss_gate')
    for n in ('rift_engine', 'rift_engine_active'):
        model(n, {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
            'top': f'{NS}:block/{n}_top', 'side': f'{NS}:block/{n}_side', 'bottom': f'{NS}:block/astral_bricks'}})
    state('rift_engine', {'active=false': {'model': f'{NS}:block/rift_engine'}, 'active=true': {'model': f'{NS}:block/rift_engine_active'}})
    item('rift_engine')
    for n in ('updraft_vent', 'eclipse_altar'):
        model(n, {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
            'top': f'{NS}:block/{n}_top', 'side': f'{NS}:block/{n}_side', 'bottom': f'{NS}:block/astral_bricks'}})
        state(n, {'': {'model': f'{NS}:block/{n}'}})
        item(n)
    for i in ITEMS:
        parent = 'minecraft:item/handheld' if i == 'corona' else 'minecraft:item/generated'
        write(a('models', 'item', i + '.json'), {'parent': parent, 'textures': {'layer0': f'{NS}:item/{i}'}})


# ---------------------------------------------------------------------------------------------------------- loot
def self_drop(name):
    return {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'bonus_rolls': 0.0, 'entries': [{'type': 'minecraft:item', 'name': U + name}],
                                                  'conditions': [{'condition': 'minecraft:survives_explosion'}]}]}


def silk_or(name, other, lo=1, hi=1, fortune=False):
    alt = {'type': 'minecraft:item', 'name': other}
    fns = []
    if hi > 1 or lo > 1:
        fns.append({'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}})
    if fortune:
        fns.append({'function': 'minecraft:apply_bonus', 'enchantment': 'minecraft:fortune', 'formula': 'minecraft:ore_drops'})
    fns.append({'function': 'minecraft:explosion_decay'})
    alt['functions'] = fns
    silk = {'type': 'minecraft:item', 'name': U + name, 'conditions': [{'condition': 'minecraft:match_tool', 'predicate': {
        'predicates': {'minecraft:enchantments': [{'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}]}
    return {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'bonus_rolls': 0.0, 'entries': [{'type': 'minecraft:alternatives', 'children': [silk, alt]}]}]}


def pool(entries, rolls=1, chance=None):
    p = {'rolls': rolls, 'bonus_rolls': 0.0, 'entries': entries}
    if chance is not None:
        p['conditions'] = [{'condition': 'minecraft:killed_by_player'}, {'condition': 'minecraft:random_chance', 'chance': chance}]
    return p


def it(name, lo=1, hi=1, weight=1):
    e = {'type': 'minecraft:item', 'name': name, 'weight': weight}
    if hi > 1 or lo > 1:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}}]
    return e


CHESTS = {
    'observatory_archive': [pool([it('minecraft:book', 2, 4, 3), it('minecraft:paper', 3, 8, 3), it('minecraft:spyglass', 1, 1, 2),
                                  it('minecraft:compass', 1, 1, 2), it(U + 'raw_starmetal', 1, 3, 2), it('minecraft:amethyst_shard', 2, 6, 2)], rolls=4),
                            pool([it(U + 'astrolabe')])],
    'observatory_workshop': [pool([it('minecraft:copper_ingot', 4, 12, 3), it('minecraft:iron_ingot', 2, 6, 3), it('minecraft:redstone', 4, 12, 2),
                                   it(U + 'raw_starmetal', 2, 4, 3), it(U + 'lumen_core', 1, 1, 1), it(A + 'titanium_nugget', 2, 6, 2),
                                   it('minecraft:diamond', 1, 2, 1)], rolls=5)],
    'observatory_vault': [pool([it('minecraft:diamond', 2, 4, 3), it(U + 'starmetal_ingot', 2, 4, 3), it('minecraft:experience_bottle', 6, 12, 2),
                                it(A + 'uranium_ingot', 1, 2, 1), it(A + 'titanium_ingot', 1, 2, 1), it('minecraft:netherite_scrap', 1, 1, 1)], rolls=5)],
    'abyss_cache': [pool([it(U + 'raw_starmetal', 2, 5, 3), it(U + 'lumen_core', 1, 2, 1), it('minecraft:diamond', 1, 3, 2),
                          it('minecraft:ender_pearl', 2, 4, 2), it('minecraft:golden_apple', 1, 2, 1), it('minecraft:experience_bottle', 4, 10, 2)], rolls=4)],
}


def loot():
    for b in ('astral_bricks', 'chiseled_astral', 'lumen_crystal', 'starbloom', 'void_tendril', 'updraft_vent'):
        write(d('loot_table', 'blocks', b + '.json'), self_drop(b))
    write(d('loot_table', 'blocks', 'astral_shale.json'), self_drop('astral_shale'))
    write(d('loot_table', 'blocks', 'starmoss.json'), silk_or('starmoss', U + 'astral_shale'))
    write(d('loot_table', 'blocks', 'astral_ore.json'), silk_or('astral_ore', U + 'raw_starmetal', fortune=True))
    write(d('loot_table', 'blocks', 'rift_glass.json'), {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'bonus_rolls': 0.0, 'entries': [
        {'type': 'minecraft:item', 'name': U + 'rift_glass', 'conditions': [{'condition': 'minecraft:match_tool', 'predicate': {
            'predicates': {'minecraft:enchantments': [{'enchantments': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}}]}]}]})
    write(d('loot_table', 'blocks', 'void_cyst.json'), {'type': 'minecraft:block', 'pools': []})
    write(d('loot_table', 'entities', 'lumen_mite.json'), {'type': 'minecraft:entity', 'pools': [
        pool([it('minecraft:glowstone_dust', 1, 2)]), pool([it(U + 'lumen_core')], chance=0.06)]})
    write(d('loot_table', 'entities', 'orrery_warden.json'), {'type': 'minecraft:entity', 'pools': [
        pool([it(U + 'raw_starmetal', 1, 2)]), pool([it('minecraft:copper_ingot', 2, 5)]), pool([it(U + 'lumen_core')], chance=0.5)]})
    write(d('loot_table', 'entities', 'eclipse_leviathan.json'), {'type': 'minecraft:entity', 'pools': []})
    for name, pools in CHESTS.items():
        write(d('loot_table', 'chests', name + '.json'), {'type': 'minecraft:chest', 'pools': pools})


def ing(i):
    return {'tag': i[1:]} if i.startswith('#') else {'item': i}


def recipes():
    def shaped(name, pattern, key, result, count=1, cat='misc'):
        write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shaped', 'category': cat, 'pattern': pattern,
                                            'key': {k: ing(v) for k, v in key.items()}, 'result': {'id': result, 'count': count}})

    def shapeless(name, items, result, count=1):
        write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                            'ingredients': [ing(i) for i in items], 'result': {'id': result, 'count': count}})

    for kind, t in (('smelting', 200), ('blasting', 100)):
        write(d('recipe', f'starmetal_ingot_from_{kind}.json'), {'type': f'minecraft:{kind}', 'category': 'misc', 'cookingtime': t,
                                                                 'experience': 1.0, 'ingredient': ing(U + 'raw_starmetal'),
                                                                 'result': {'id': U + 'starmetal_ingot'}})
    shaped('astral_bricks', ['SS', 'SS'], {'S': U + 'astral_shale'}, U + 'astral_bricks', 4, 'building')
    shaped('chiseled_astral', ['B', 'L'], {'B': U + 'astral_bricks', 'L': 'minecraft:glowstone_dust'}, U + 'chiseled_astral', 1, 'building')
    shaped('rift_glass', [' L ', 'LGL', ' L '], {'L': 'minecraft:amethyst_shard', 'G': 'minecraft:glass'}, U + 'rift_glass', 4, 'building')
    shapeless('eclipse_sigil', [U + 'sigil_shard', U + 'sigil_shard', U + 'sigil_shard', 'minecraft:ender_eye'], U + 'eclipse_sigil')
    shaped('eclipse_sigil_forged', [' S ', 'SCS', ' S '], {'S': U + 'starmetal_ingot', 'C': U + 'lumen_core'}, U + 'eclipse_sigil')
    shaped('astrolabe', [' S ', 'SCS', ' L '], {'S': U + 'starmetal_ingot', 'C': 'minecraft:compass', 'L': U + 'lumen_core'}, U + 'astrolabe', 1, 'equipment')
    shaped('updraft_vent', ['BLB', 'BCB', 'BBB'], {'B': U + 'astral_bricks', 'L': U + 'lumen_core', 'C': 'minecraft:phantom_membrane'},
           U + 'updraft_vent', 2)


def tags():
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'mineable', 'pickaxe.json'), {
        'values': [U + 'cage_beacon', U + 'astral_shale', U + 'astral_bricks', U + 'chiseled_astral', U + 'astral_ore', U + 'lumen_crystal',
                   U + 'updraft_vent']})
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'needs_iron_tool.json'), {'replace': False, 'values': [U + 'astral_ore']})
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'mineable', 'hoe.json'), {'replace': False, 'values': [U + 'starmoss', U + 'void_cyst']})
    # starmoss counts as soil, so the starbloom (a flower) grows on it
    write(os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block', 'dirt.json'), {'replace': False, 'values': [U + 'starmoss']})
    write(d('tags', 'block', 'abyss_brood.json'), {'values': [U + 'void_cyst']})
    write(os.path.join(DATA, 'weapon_attributes', 'corona.json'), {'parent': 'bettercombat:glaive'})
    write(os.path.join(ROOT, 'data', 'c', 'tags', 'entity_type', 'bosses.json'), {'replace': False, 'values': [U + 'chained_matriarch', U + 'eclipse_leviathan']})


def advancements(adv, has, at):
    adv('observatory', 'enter', U + 'rift_engine', {'c': at(f'{NS}:rift_observatory')})
    adv('component', 'observatory', U + 'focusing_lens', {'lens': has(U + 'focusing_lens'), 'heart': has(U + 'coolant_heart'),
                                                          'chart': has(U + 'star_chart')}, requirements=[['lens', 'heart', 'chart']])
    adv('abyss', 'component', U + 'abyss_gate', {'c': {'trigger': 'minecraft:changed_dimension', 'conditions': {'to': f'{NS}:astral_abyss'}}},
        frame='goal')
    adv('blinkstone', 'abyss', U + 'blinkstone', {'c': has(U + 'blinkstone')})
    adv('sigil', 'abyss', U + 'eclipse_sigil', {'c': has(U + 'eclipse_sigil')})
    adv('leviathan', 'sigil', U + 'corona', {'c': has(U + 'eclipse_scale')}, frame='challenge')
    adv('starmetal', 'abyss', U + 'starmetal_ingot', {'c': has(U + 'starmetal_ingot')})


LANG = {
    'entity.unstable_frontiers.lumen_mite': 'Lumen Mite',
    'entity.unstable_frontiers.orrery_warden': 'Orrery Warden',
    'entity.unstable_frontiers.eclipse_leviathan': 'The Eclipse Leviathan',
    'entity.unstable_frontiers.star_bolt': 'Star Bolt',
    'item.unstable_frontiers.star_bolt': 'Star Bolt',
    'block.unstable_frontiers.astral_shale': 'Astral Shale',
    'block.unstable_frontiers.astral_bricks': 'Astral Bricks',
    'block.unstable_frontiers.chiseled_astral': 'Chiseled Astral Bricks',
    'block.unstable_frontiers.starmoss': 'Starmoss',
    'block.unstable_frontiers.lumen_crystal': 'Lumen Crystal',
    'block.unstable_frontiers.rift_glass': 'Rift Glass',
    'block.unstable_frontiers.astral_ore': 'Astral Ore',
    'block.unstable_frontiers.starbloom': 'Starbloom',
    'block.unstable_frontiers.void_tendril': 'Void Tendril',
    'block.unstable_frontiers.void_cyst': 'Void Cyst',
    'block.unstable_frontiers.abyss_gate': 'Rift Gate',
    'block.unstable_frontiers.rift_engine': 'Rift Engine',
    'block.unstable_frontiers.updraft_vent': 'Updraft Vent',
    'block.unstable_frontiers.eclipse_altar': 'Eclipse Altar',
    'item.unstable_frontiers.focusing_lens': 'Focusing Lens',
    'item.unstable_frontiers.focusing_lens.tip0': 'One of the rift engine\'s three components.',
    'item.unstable_frontiers.focusing_lens.tip1': 'Set it into the engine at the observatory\'s heart.',
    'item.unstable_frontiers.coolant_heart': 'Coolant Heart',
    'item.unstable_frontiers.coolant_heart.tip0': 'One of the rift engine\'s three components.',
    'item.unstable_frontiers.coolant_heart.tip1': 'Still cold. Set it into the engine.',
    'item.unstable_frontiers.star_chart': 'Star Chart',
    'item.unstable_frontiers.star_chart.tip0': 'One of the rift engine\'s three components.',
    'item.unstable_frontiers.star_chart.tip1': 'It shows a sky that is not this one.',
    'item.unstable_frontiers.astrolabe': 'Astrolabe',
    'item.unstable_frontiers.astrolabe.tip0': 'In the frontier: use to find the nearest Rift Observatory.',
    'item.unstable_frontiers.astrolabe.tip1': 'In the Astral Abyss: hold it to see the way to a place; use to pick the next.',
    'item.unstable_frontiers.astrolabe.tip2': 'Sneak and use to list every place and its state.',
    'item.unstable_frontiers.sigil_shard': 'Sigil Shard',
    'item.unstable_frontiers.sigil_shard.tip0': 'Three, with an eye of ender, make an Eclipse Sigil.',
    'item.unstable_frontiers.sigil_shard.tip1': 'One waits at each of the abyss\'s places: the Starwell, the Archive, the Tether Spire.',
    'item.unstable_frontiers.eclipse_sigil': 'Eclipse Sigil',
    'item.unstable_frontiers.eclipse_sigil.tip0': 'Set it into the altar of the Hollow Crown.',
    'item.unstable_frontiers.eclipse_sigil.tip1': 'Prepare first. What answers is very large.',
    'item.unstable_frontiers.raw_starmetal': 'Raw Starmetal',
    'item.unstable_frontiers.starmetal_ingot': 'Starmetal Ingot',
    'item.unstable_frontiers.starmetal_ingot.tip0': 'Forges Eclipse Sigils (with a Lumen Core) and repairs the Blinkstone.',
    'item.unstable_frontiers.lumen_core': 'Lumen Core',
    'item.unstable_frontiers.lumen_core.tip0': 'From Orrery Wardens (and rarely Lumen Mites).',
    'item.unstable_frontiers.eclipse_scale': 'Eclipse Scale',
    'item.unstable_frontiers.eclipse_scale.tip0': 'From the Eclipse Leviathan.',
    'item.unstable_frontiers.eclipse_scale.tip1': 'Sneak-use the Corona with a scale in your off hand to empower it; also repairs it.',
    'item.unstable_frontiers.blinkstone': 'Blinkstone',
    'item.unstable_frontiers.blinkstone.tip0': 'Use to step up to 10 blocks the way you look, through the air.',
    'item.unstable_frontiers.blinkstone.tip1': 'Never into a block. 3 s between steps. Repair with Starmetal.',
    'item.unstable_frontiers.corona': 'Corona',
    'item.unstable_frontiers.corona.tip0': 'Light stored: %s / %s. Each melee hit stores one.',
    'item.unstable_frontiers.corona.tip1': 'Use to release it all as a piercing beam (10 per charge).',
    'item.unstable_frontiers.corona.tip2': 'Tier %s of 3. Sneak-use with an Eclipse Scale in the off hand to raise it.',
    'item.unstable_frontiers.corona.tip3': 'Durability %s / %s',
    'place.unstable_frontiers.landing': 'the Landing',
    'place.unstable_frontiers.starwell': 'the Starwell',
    'place.unstable_frontiers.archive': 'the Drifting Archive',
    'place.unstable_frontiers.tether_spire': 'the Tether Spire',
    'place.unstable_frontiers.hollow_crown': 'the Hollow Crown',
    'place.unstable_frontiers.state.seen': 'visited',
    'place.unstable_frontiers.state.unseen': 'not yet visited',
    'place.unstable_frontiers.state.awake': 'the Leviathan is awake',
    'landmark.unstable_frontiers.rift_observatory.subtitle': 'Something was watched from here. Then something came through.',
    'landmark.unstable_frontiers.rift_observatory.conquered': 'The engine\'s three components are recovered. Set them into it.',
    'landmark.unstable_frontiers.abyss_landing.subtitle': 'The rift set you down here. The gate behind you leads back.',
    'landmark.unstable_frontiers.abyss_landing.conquered': '',
    'landmark.unstable_frontiers.abyss_place.subtitle': 'A fragment of the world the observatory watched.',
    'landmark.unstable_frontiers.abyss_place.conquered': 'A Sigil Shard is yours.',
    'landmark.unstable_frontiers.hollow_crown.subtitle': 'The Leviathan sleeps below. The altar wakes it.',
    'landmark.unstable_frontiers.hollow_crown.conquered': '',
    'message.unstable_frontiers.engine_has': 'That part is already in place.',
    'message.unstable_frontiers.engine_progress': 'The engine takes the part. %s of 3.',
    'message.unstable_frontiers.engine_needs': 'The rift engine is dark. It still needs: %s.',
    'message.unstable_frontiers.engine_active': 'The rift engine hums. The gate beside it stands open to the Astral Abyss.',
    'message.unstable_frontiers.rift_open_title': 'The Rift Opens',
    'message.unstable_frontiers.rift_open_sub': 'The gate stands open to the Astral Abyss, and stays open.',
    'message.unstable_frontiers.rift_no_gate': 'The engine woke, but no gate answered (was the gate frame broken?).',
    'message.unstable_frontiers.no_abyss': 'The Astral Abyss is missing (is the data pack disabled?).',
    'message.unstable_frontiers.abyss_welcome': 'The Astral Abyss. The gate behind you leads back. Fall too far and the rift will catch you, at a price. Follow the beams in the sky: the abyss\'s places hold Sigil Shards, and three make the Eclipse Sigil.',
    'message.unstable_frontiers.rift_catch': 'The rift catches you, and takes its due.',
    'message.unstable_frontiers.abyss_belongings': 'Your belongings wait in the Astral Abyss at %s %s %s. They keep for fifteen minutes.',
    'message.unstable_frontiers.eclipse_awake': 'The Leviathan is already awake.',
    'message.unstable_frontiers.eclipse_altar': 'An empty socket the shape of a sigil. The Leviathan has fallen %s times.',
    'message.unstable_frontiers.eclipse_rises': 'The Crown shakes. Something vast rises from the void below.',
    'message.unstable_frontiers.eclipse_sinks': 'The Leviathan sinks back into the void. The altar stays charged: the next call costs no sigil.',
    'message.unstable_frontiers.eclipse_falls': 'The Eclipse Leviathan falls. The sky over the Crown clears.',
    'message.unstable_frontiers.astrolabe_none': 'The astrolabe finds no observatory within reach.',
    'message.unstable_frontiers.astrolabe_observatory': 'A Rift Observatory: %s blocks %s.',
    'message.unstable_frontiers.astrolabe_elsewhere': 'The astrolabe\'s rings spin aimlessly here.',
    'message.unstable_frontiers.astrolabe_line': '%s: %s blocks %s %s',
    'message.unstable_frontiers.astrolabe_entry': ' %s: %s blocks %s (%s)',
    'message.unstable_frontiers.blink_blocked': 'No room to step there.',
    'message.unstable_frontiers.corona_empty': 'The Corona holds no light. Strike something first.',
    'message.unstable_frontiers.corona_max': 'The Corona can hold no more.',
    'message.unstable_frontiers.corona_tier': 'The Corona brightens: tier %s, %s charges.',
    'boss.unstable_frontiers.leviathan.beam': 'Its corona flares: get behind an obelisk, or off the line of light!',
    'boss.unstable_frontiers.leviathan.well': 'Rings close around you: step out of yours!',
    'boss.unstable_frontiers.leviathan.pass': 'A trail of soul fire: it will sweep along it. Then strike it low!',
    'boss.unstable_frontiers.leviathan.eclipse': 'The eclipse: it will crash down in the ring of fire. Then its core lies open!',
    'boss.unstable_frontiers.leviathan.phase2': 'The Leviathan roars. Its beam now sweeps back again, and it calls its mites.',
    'boss.unstable_frontiers.leviathan.phase3': 'The Leviathan roars. The eclipse is coming: more wells, and it will crash down and lie open.',
    'hint.unstable_frontiers.lumen_mite': 'Lumen Mites: when a mite\'s lantern swells, it spits a slow bolt. Step aside; they are fragile up close.',
    'hint.unstable_frontiers.orrery_warden': 'An Orrery Warden: when its rings stop and its lens flares, break line of sight. After the beam its rings stall: hit it then (double damage).',
    'advancement.unstable_frontiers.observatory': 'Stargazers',
    'advancement.unstable_frontiers.observatory.desc': 'Find a Rift Observatory in the frontier',
    'advancement.unstable_frontiers.component': 'Parts of the Engine',
    'advancement.unstable_frontiers.component.desc': 'Recover the Focusing Lens, the Coolant Heart and the Star Chart',
    'advancement.unstable_frontiers.abyss': 'Through the Rift',
    'advancement.unstable_frontiers.abyss.desc': 'Restore the rift engine and step into the Astral Abyss',
    'advancement.unstable_frontiers.blinkstone': 'Between the Stars',
    'advancement.unstable_frontiers.blinkstone.desc': 'Take the Blinkstone from the Starwell',
    'advancement.unstable_frontiers.sigil': 'The Eclipse Sigil',
    'advancement.unstable_frontiers.sigil.desc': 'Join three Sigil Shards with an eye of ender',
    'advancement.unstable_frontiers.leviathan': 'Totality',
    'advancement.unstable_frontiers.leviathan.desc': 'Defeat the Eclipse Leviathan at the Hollow Crown',
    'advancement.unstable_frontiers.starmetal': 'Fallen Metal',
    'advancement.unstable_frontiers.starmetal.desc': 'Smelt Starmetal mined from the abyss\'s islands',
}

SOUNDS = {
    'mite.ambient': (['abyss/mite_ambient'], 'Lumen Mite hums'),
    'mite.hurt': (['abyss/mite_hurt'], 'Lumen Mite hurts'),
    'mite.death': (['abyss/mite_death'], 'Lumen Mite dies'),
    'mite.tell': (['abyss/mite_tell'], 'Lumen Mite swells'),
    'mite.spit': (['abyss/mite_spit'], 'Lumen Mite spits'),
    'warden.ambient': (['abyss/warden_ambient'], 'Orrery Warden ticks'),
    'warden.hurt': (['abyss/warden_hurt'], 'Orrery Warden clangs'),
    'warden.death': (['abyss/warden_death'], 'Orrery Warden collapses'),
    'warden.tell': (['abyss/warden_tell'], 'Orrery Warden aligns its rings'),
    'warden.beam': (['abyss/warden_beam'], 'Orrery Warden fires'),
    'warden.stall': (['abyss/warden_stall'], 'Orrery Warden stalls'),
    'warden.recover': (['abyss/warden_recover'], 'Orrery Warden restarts'),
    'warden.pulse': (['abyss/warden_pulse'], 'Orrery Warden pulses'),
    'leviathan.ambient': (['abyss/leviathan_ambient'], 'The Leviathan sings'),
    'leviathan.hurt': (['abyss/leviathan_hurt'], 'The Leviathan hurts'),
    'leviathan.death': (['abyss/leviathan_death'], 'The Leviathan dies'),
    'leviathan.roar': (['abyss/leviathan_roar'], 'The Leviathan roars'),
    'leviathan.beam_tell': (['abyss/leviathan_beam_tell'], 'The corona flares'),
    'leviathan.beam': (['abyss/leviathan_beam'], 'The eclipse beam burns'),
    'leviathan.well': (['abyss/leviathan_well'], 'Gravity wells close'),
    'leviathan.pass': (['abyss/leviathan_pass'], 'The Leviathan swoops'),
    'leviathan.summon': (['abyss/leviathan_summon'], 'The Leviathan calls'),
    'leviathan.slam': (['abyss/leviathan_slam'], 'The Leviathan crashes down'),
    'rift.open': (['abyss/rift_open'], 'The rift opens'),
    'abyss.ambient': (['abyss/abyss_ambient'], 'The void hums'),
}


def write_all():
    dimension()
    blocks()
    loot()
    recipes()
    tags()
