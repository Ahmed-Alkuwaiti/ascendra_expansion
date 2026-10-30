"""Data for the Drowned Expanse: the dimension and its biomes, block states and models, loot, recipes, tags (including
the Curios slots the diving gear uses), rosters, advancements, text and sounds. datagen.py imports this and folds it
into its own run, so `python3 tools/datagen.py` still regenerates everything.
"""
import json
import os

from abyss_data import ROOT, DATA, NS, U, write, d, a, m, self_drop, pool, it, ing

# ------------------------------------------------------------------------------------------------------- rosters
ROSTERS = {
    # Deepwork Station: drowned salvagers and an eel in the flooded work bays (an ambush).
    'drowned_deepwork': {'mobs': [m('minecraft:drowned', 4), m(U + 'murkjaw', 2, 2)]},
    # The Choir Temple: waves of the drowned faithful, and a guardian that still keeps the nave.
    'drowned_choir': {'mobs': [m('minecraft:drowned', 5), m(U + 'murkjaw', 2, 2), m('minecraft:guardian', 1, 1)]},
    # The Wreck of the Long Patience: the Wreckmaw, an old murkjaw grown huge in the hull, with its young.
    'drowned_wreck': {'mobs': [m(U + 'murkjaw', 3)], 'escorts': 2,
                      'elite': {'id': U + 'murkjaw', 'title': 'The Wreckmaw', 'bar': 'green', 'abilities': ['rally'], 'health': 3.5}},
    # The Sunken Gate in the frontier: a few drowned in the flooded pool.
    'sunken_residents': {'mobs': [m('minecraft:drowned')]},
}

# The Sunken Gate generates in the frontier like the other landmarks (datagen.py's LANDMARKS and SETS take these).
LANDMARKS = {'sunken_gate': (['hushed_barrens', 'gnashwood_wilds', 'talon_spires'], 40, 6, True)}
SETS = {'sunken_gate': (['sunken_gate'], [1], 34, 14, 902261447, ('major_landmarks', 4))}
LENS = {'sunken': ['sunken_gate']}

# ------------------------------------------------------------------------------------------------------- dimension
# name: (water colour, water fog colour, fog colour, sky colour)
BIOMES = {'glassreef_shallows': (0x3fc8d8, 0x1a6f86, 0x9fd8e8, 0x7cc6ec),
          'kelpwood': (0x2f9a78, 0x124c46, 0x86c0b0, 0x7cc6ec),
          'sunken_reach': (0x2a5f9a, 0x0d2a4a, 0x6080a0, 0x7cc6ec),
          'blackwater_trench': (0x1a2c58, 0x050c1c, 0x30405a, 0x7cc6ec)}


def dimension():
    write(d('dimension_type', 'drowned_expanse.json'), {
        'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False,
        # beds work (a bed in a shelter sets your spawn there; with bed_works false a bed would explode)
        # light for the deep: water drinks skylight, so a little ambient light keeps the floor readable without shaders
        'ambient_light': 0.28, 'monster_spawn_light_level': {'type': 'minecraft:uniform', 'min_inclusive': 0, 'max_inclusive': 7},
        'monster_spawn_block_light_limit': 0, 'piglin_safe': False, 'bed_works': True, 'respawn_anchor_works': False, 'has_raids': False,
        'logical_height': 320, 'min_y': 0, 'height': 320, 'infiniburn': '#minecraft:infiniburn_overworld', 'effects': f'{NS}:drowned_expanse'})
    write(d('dimension', 'drowned_expanse.json'), {'type': f'{NS}:drowned_expanse', 'generator': {
        'type': f'{NS}:drowned', 'biome_source': {'type': f'{NS}:drowned', 'shallows': f'{NS}:glassreef_shallows', 'kelpwood': f'{NS}:kelpwood',
                                                   'reach': f'{NS}:sunken_reach', 'trench': f'{NS}:blackwater_trench'}}})
    empty = {k: [] for k in ('ambient', 'axolotls', 'creature', 'misc', 'monster', 'underground_water_creature', 'water_ambient', 'water_creature')}
    for name, (water, wfog, fog, sky) in BIOMES.items():
        sp = json.loads(json.dumps(empty))
        if name == 'glassreef_shallows':
            sp['water_ambient'] = [{'type': 'minecraft:tropical_fish', 'weight': 25, 'minCount': 3, 'maxCount': 6},
                                   {'type': 'minecraft:pufferfish', 'weight': 5, 'minCount': 1, 'maxCount': 2}]
            sp['water_creature'] = [{'type': U + 'lanternray', 'weight': 6, 'minCount': 1, 'maxCount': 2},
                                    {'type': 'minecraft:dolphin', 'weight': 2, 'minCount': 1, 'maxCount': 2}]
            sp['monster'] = [{'type': 'minecraft:drowned', 'weight': 4, 'minCount': 1, 'maxCount': 1}]
        elif name == 'kelpwood':
            sp['water_ambient'] = [{'type': 'minecraft:cod', 'weight': 15, 'minCount': 3, 'maxCount': 6},
                                   {'type': 'minecraft:salmon', 'weight': 10, 'minCount': 2, 'maxCount': 4}]
            sp['water_creature'] = [{'type': U + 'lanternray', 'weight': 6, 'minCount': 1, 'maxCount': 2},
                                    {'type': 'minecraft:squid', 'weight': 4, 'minCount': 1, 'maxCount': 3}]
            sp['monster'] = [{'type': U + 'murkjaw', 'weight': 6, 'minCount': 1, 'maxCount': 1},
                             {'type': 'minecraft:drowned', 'weight': 5, 'minCount': 1, 'maxCount': 2}]
        elif name == 'sunken_reach':
            sp['water_ambient'] = [{'type': 'minecraft:cod', 'weight': 6, 'minCount': 2, 'maxCount': 4}]
            sp['water_creature'] = [{'type': U + 'lanternray', 'weight': 4, 'minCount': 1, 'maxCount': 2}]
            sp['underground_water_creature'] = [{'type': 'minecraft:glow_squid', 'weight': 8, 'minCount': 1, 'maxCount': 3}]
            sp['monster'] = [{'type': U + 'murkjaw', 'weight': 8, 'minCount': 1, 'maxCount': 1},
                             {'type': 'minecraft:drowned', 'weight': 4, 'minCount': 1, 'maxCount': 2}]
        else:
            sp['underground_water_creature'] = [{'type': 'minecraft:glow_squid', 'weight': 10, 'minCount': 1, 'maxCount': 3}]
            sp['monster'] = [{'type': U + 'murkjaw', 'weight': 8, 'minCount': 1, 'maxCount': 1},
                             {'type': 'minecraft:guardian', 'weight': 2, 'minCount': 1, 'maxCount': 1}]
        write(d('worldgen', 'biome', name + '.json'), {
            'has_precipitation': True, 'temperature': 0.6, 'downfall': 0.5,
            'effects': {'sky_color': sky, 'fog_color': fog, 'water_color': water, 'water_fog_color': wfog,
                        'grass_color': 0x3f9f7f, 'foliage_color': 0x3a8f6f,
                        'particle': {'options': {'type': 'minecraft:underwater'}, 'probability': 0.004 if name != 'blackwater_trench' else 0.008},
                        'ambient_sound': f'{NS}:drowned.ambient',
                        'mood_sound': {'sound': f'{NS}:drowned.ambient', 'tick_delay': 4000, 'block_search_extent': 8, 'offset': 2.0},
                        'music': {'sound': 'minecraft:music.under_water', 'min_delay': 12000, 'max_delay': 24000, 'replace_current_music': False}},
            'spawners': sp,
            # low, bounded density (see also DrownedDimension.crowded)
            'spawn_costs': {U + 'murkjaw': {'energy_budget': 0.4, 'charge': 0.7}, U + 'lanternray': {'energy_budget': 0.5, 'charge': 0.5}},
            'carvers': {}, 'features': [[] for _ in range(11)]})


# --------------------------------------------------------------------------------------------------- blocks and items
CUBE = ['brine_slate', 'brine_bricks', 'chiseled_brine', 'lumen_coral', 'tide_glyph']
ITEMS = ['abyssal_goggles', 'deep_sight_goggles', 'diving_rig', 'deep_rig', 'swim_fins', 'breath_charm', 'echo_sounder',
         'pressure_valve', 'keel_plate', 'choir_pearl', 'abyssal_pearl']


def bell_model(tex):
    face = lambda uv: {'texture': '#bell', 'uv': uv}
    return {'parent': 'minecraft:block/block', 'render_type': 'minecraft:cutout', 'textures': {'particle': tex, 'bell': tex},
            'elements': [
                {'from': [4, 4, 4], 'to': [12, 13, 12], 'faces': {f: face([4, 3, 12, 12]) for f in ('north', 'south', 'east', 'west', 'up', 'down')}},
                {'from': [3, 2, 3], 'to': [13, 4, 13], 'faces': {f: face([3, 0, 13, 2]) for f in ('north', 'south', 'east', 'west', 'up', 'down')}},
                {'from': [7, 13, 7], 'to': [9, 16, 9], 'faces': {f: face([7, 0, 9, 3]) for f in ('north', 'south', 'east', 'west', 'up', 'down')}}]}


def blocks():
    def state(name, variants):
        write(a('blockstates', name + '.json'), {'variants': variants})

    def model(name, obj):
        write(a('models', 'block', name + '.json'), obj)

    for n in CUBE:
        model(n, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'{NS}:block/{n}'}})
        state(n, {'': {'model': f'{NS}:block/{n}'}})
        write(a('models', 'item', n + '.json'), {'parent': f'{NS}:block/{n}'})
    model('breath_vent', {'parent': 'minecraft:block/cube_bottom_top', 'textures': {
        'top': f'{NS}:block/breath_vent_top', 'side': f'{NS}:block/breath_vent_side', 'bottom': f'{NS}:block/brine_slate'}})
    state('breath_vent', {'': {'model': f'{NS}:block/breath_vent'}})
    write(a('models', 'item', 'breath_vent.json'), {'parent': f'{NS}:block/breath_vent'})
    model('tide_gate', {'parent': 'minecraft:block/cube_all', 'render_type': 'minecraft:translucent', 'textures': {'all': f'{NS}:block/tide_gate'}})
    state('tide_gate', {'': {'model': f'{NS}:block/tide_gate'}})
    write(a('models', 'item', 'tide_gate.json'), {'parent': f'{NS}:block/tide_gate'})
    for n in ('tide_bell', 'abyssal_bell'):
        model(n, bell_model(f'{NS}:block/{n}'))
        state(n, {'': {'model': f'{NS}:block/{n}'}})
        write(a('models', 'item', n + '.json'), {'parent': f'{NS}:block/{n}'})
    for i in ITEMS:
        write(a('models', 'item', i + '.json'), {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{NS}:item/{i}'}})
    write(a('models', 'item', 'undertow.json'), {'parent': 'minecraft:item/handheld', 'textures': {'layer0': f'{NS}:item/undertow'}})


# ---------------------------------------------------------------------------------------------------------- loot
CHESTS = {
    # Tidewatch: the station's stores. The echo sounder is always there; nothing here replaces the rig.
    'drowned_tidewatch': [pool([it(U + 'echo_sounder')]),
                          pool([it('minecraft:glow_berries', 4, 8, 3), it('minecraft:cooked_cod', 3, 6, 3), it('minecraft:dried_kelp', 4, 10, 2),
                                it('minecraft:sea_lantern', 1, 3, 2), it('minecraft:copper_ingot', 2, 6, 2)], rolls=4)],
    'drowned_deepwork': [pool([it('minecraft:copper_ingot', 4, 10, 3), it('minecraft:iron_ingot', 2, 6, 3), it('minecraft:prismarine_shard', 3, 8, 3),
                               it('minecraft:prismarine_crystals', 2, 6, 2), it('minecraft:glow_ink_sac', 1, 3, 2), it('minecraft:diamond', 1, 1, 1)],
                              rolls=5)],
    'drowned_choir': [pool([it('minecraft:amethyst_shard', 3, 8, 3), it('minecraft:glow_ink_sac', 2, 4, 2), it('minecraft:nautilus_shell', 1, 2, 2),
                            it('minecraft:experience_bottle', 3, 8, 2), it('minecraft:emerald', 2, 6, 2), it('minecraft:gold_ingot', 2, 5, 2)], rolls=4)],
    'drowned_wreck': [pool([it('minecraft:gold_ingot', 3, 8, 3), it('minecraft:emerald', 3, 8, 3), it('minecraft:nautilus_shell', 1, 3, 3),
                            it('minecraft:diamond', 1, 3, 2), it('minecraft:experience_bottle', 4, 10, 2)], rolls=5),
                      pool([it('minecraft:heart_of_the_sea')])],
    'drowned_vault': [pool([it('minecraft:diamond', 2, 4, 3), it('minecraft:nautilus_shell', 2, 4, 2), it('minecraft:experience_bottle', 6, 12, 2),
                            it('minecraft:prismarine_crystals', 4, 10, 2), it('minecraft:netherite_scrap', 1, 1, 1)], rolls=4)],
    # the frontier's Sunken Gate: Ilsa Vane's expedition left its diving stores beside the pool
    'sunken_gate_stores': [pool([it('minecraft:leather', 3, 6, 3), it('minecraft:copper_ingot', 3, 8, 3), it('minecraft:glass_pane', 2, 4, 2),
                                 it('minecraft:glow_berries', 3, 6, 2), it('minecraft:bucket', 1, 1, 1), it('minecraft:kelp', 4, 10, 2)], rolls=4)],
}


def loot():
    for b in ('brine_slate', 'brine_bricks', 'chiseled_brine', 'lumen_coral', 'breath_vent', 'tide_glyph'):
        write(d('loot_table', 'blocks', b + '.json'), self_drop(b))
    for b in ('tide_gate', 'tide_bell', 'abyssal_bell'):
        write(d('loot_table', 'blocks', b + '.json'), {'type': 'minecraft:block', 'pools': []})
    write(d('loot_table', 'entities', 'lanternray.json'), {'type': 'minecraft:entity', 'pools': [
        pool([it('minecraft:glow_ink_sac')], chance=0.5), pool([it('minecraft:prismarine_crystals', 1, 2)], chance=0.4)]})
    write(d('loot_table', 'entities', 'murkjaw.json'), {'type': 'minecraft:entity', 'pools': [
        pool([it('minecraft:prismarine_shard', 1, 2)]), pool([it('minecraft:cod', 1, 2)]), pool([it('minecraft:nautilus_shell')], chance=0.08)]})
    write(d('loot_table', 'entities', 'deepcaller.json'), {'type': 'minecraft:entity', 'pools': []})
    for name, pools in CHESTS.items():
        write(d('loot_table', 'chests', name + '.json'), {'type': 'minecraft:chest', 'pools': pools})


def recipes():
    def shaped(name, pattern, key, result, count=1, cat='equipment'):
        write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shaped', 'category': cat, 'pattern': pattern,
                                            'key': {k: ing(v) for k, v in key.items()}, 'result': {'id': result, 'count': count}})

    def shapeless(name, items, result, count=1):
        write(d('recipe', name + '.json'), {'type': 'minecraft:crafting_shapeless', 'category': 'equipment',
                                            'ingredients': [ing(i) for i in items], 'result': {'id': result, 'count': count}})

    # first dive: vanilla materials and one frontier trophy (a Gnashback's plate), so the frontier introduces the sea
    shaped('abyssal_goggles', ['LPL', 'G G'], {'L': 'minecraft:leather', 'P': U + 'gnashback_plate', 'G': 'minecraft:glass_pane'},
           U + 'abyssal_goggles')
    shaped('diving_rig', ['CPC', 'CBC', 'L L'], {'C': 'minecraft:copper_ingot', 'P': U + 'gnashback_plate', 'B': 'minecraft:bucket',
                                                 'L': 'minecraft:leather'}, U + 'diving_rig')
    shaped('echo_sounder', [' A ', 'CRC', 'CCC'], {'A': 'minecraft:amethyst_shard', 'C': 'minecraft:copper_ingot', 'R': 'minecraft:redstone'},
           U + 'echo_sounder')
    # the upgrades: what the Expanse's places give
    shapeless('deep_rig', [U + 'diving_rig', U + 'pressure_valve', U + 'keel_plate'], U + 'deep_rig')
    shapeless('deep_sight_goggles', [U + 'abyssal_goggles', U + 'choir_pearl', 'minecraft:glow_ink_sac'], U + 'deep_sight_goggles')
    shaped('breath_charm', [' S ', 'PHP', ' P '], {'S': 'minecraft:string', 'P': U + 'abyssal_pearl', 'H': 'minecraft:heart_of_the_sea'},
           U + 'breath_charm')
    shaped('breath_charm_eclipse', [' S ', 'PHP', ' P '], {'S': 'minecraft:string', 'P': U + 'abyssal_pearl', 'H': U + 'eclipse_scale'},
           U + 'breath_charm')
    shaped('brine_bricks', ['SS', 'SS'], {'S': U + 'brine_slate'}, U + 'brine_bricks', 4, 'building')
    shaped('chiseled_brine', ['B', 'G'], {'B': U + 'brine_bricks', 'G': 'minecraft:glow_ink_sac'}, U + 'chiseled_brine', 1, 'building')


def extend(path, values):
    """Adds values to a tag file another writer made (or makes it)."""
    old = json.load(open(path)) if os.path.exists(path) else {'replace': False, 'values': []}
    old['values'] = old['values'] + [v for v in values if v not in old['values']]
    write(path, old)


def tags():
    mc = os.path.join(ROOT, 'data', 'minecraft', 'tags', 'block')
    extend(os.path.join(mc, 'mineable', 'pickaxe.json'), [U + n for n in ('brine_slate', 'brine_bricks', 'chiseled_brine', 'breath_vent', 'tide_glyph',
                                                                       'lumen_coral')])
    extend(os.path.join(ROOT, 'data', 'c', 'tags', 'entity_type', 'bosses.json'), [U + 'deepcaller'])
    # Curios (in Integrated Boogaloo): each piece of diving gear has its own slot, so armour stays on. The slots are given
    # to players here; Curios ignores both files when it is absent, and the gear then works in the armour slots instead.
    cur = os.path.join(ROOT, 'data', 'curios', 'tags', 'item')
    write(os.path.join(cur, 'head.json'), {'replace': False, 'values': [U + 'abyssal_goggles', U + 'deep_sight_goggles']})
    write(os.path.join(cur, 'back.json'), {'replace': False, 'values': [U + 'diving_rig', U + 'deep_rig']})
    write(os.path.join(cur, 'feet.json'), {'replace': False, 'values': [U + 'swim_fins']})
    write(os.path.join(cur, 'necklace.json'), {'replace': False, 'values': [U + 'breath_charm']})
    write(d('curios', 'entities', 'diving_gear.json'), {'entities': ['player'], 'slots': ['head', 'back', 'feet', 'necklace']})


def advancements(adv, has, at):
    adv('sunken_gate', 'enter', U + 'tide_gate', {'c': at(f'{NS}:sunken_gate')})
    adv('diving_gear', 'sunken_gate', U + 'diving_rig', {'goggles': has(U + 'abyssal_goggles'), 'rig': has(U + 'diving_rig')},
        requirements=[['goggles'], ['rig']])
    adv('drowned', 'diving_gear', U + 'lumen_coral', {'c': {'trigger': 'minecraft:changed_dimension', 'conditions': {'to': f'{NS}:drowned_expanse'}}},
        frame='goal')
    adv('deep_rig', 'drowned', U + 'deep_rig', {'c': has(U + 'deep_rig')}, frame='goal')
    adv('deep_sight', 'drowned', U + 'deep_sight_goggles', {'c': has(U + 'deep_sight_goggles')})
    adv('deepcaller', 'deep_rig', U + 'undertow', {'c': has(U + 'abyssal_pearl')}, frame='challenge')
    adv('breath_charm', 'deepcaller', U + 'breath_charm', {'c': has(U + 'breath_charm')})


PLACES = {'tidewatch': 'Tidewatch Station', 'deepwork': 'Deepwork Station', 'choir': 'the Choir Temple', 'wreck': 'the Wreck of the Long Patience',
          'vault': 'the Sunless Vault'}

LANG = {
    'entity.unstable_frontiers.lanternray': 'Lanternray',
    'entity.unstable_frontiers.murkjaw': 'Murkjaw',
    'entity.unstable_frontiers.deepcaller': 'The Deepcaller',
    'block.unstable_frontiers.brine_slate': 'Brine Slate',
    'block.unstable_frontiers.brine_bricks': 'Brine Bricks',
    'block.unstable_frontiers.chiseled_brine': 'Chiseled Brine Bricks',
    'block.unstable_frontiers.lumen_coral': 'Lumen Coral',
    'block.unstable_frontiers.breath_vent': 'Breath Vent',
    'block.unstable_frontiers.tide_glyph': 'Tide Glyph',
    'block.unstable_frontiers.tide_gate': 'Tide Gate',
    'block.unstable_frontiers.tide_bell': 'Tide Bell',
    'block.unstable_frontiers.abyssal_bell': 'Abyssal Bell',
    'item.unstable_frontiers.abyssal_goggles': 'Abyssal Goggles',
    'item.unstable_frontiers.abyssal_goggles.tip0': 'Wear (head curio slot, or helmet slot) to see much further under water.',
    'item.unstable_frontiers.abyssal_goggles.tip1': 'Through them, the surveyors\' tide glyphs glow along the routes.',
    'item.unstable_frontiers.deep_sight_goggles': 'Deep-Sight Goggles',
    'item.unstable_frontiers.deep_sight_goggles.tip0': 'Further sight still, even in the trench.',
    'item.unstable_frontiers.deep_sight_goggles.tip1': 'Hostile creatures within 16 blocks glow while you are under water.',
    'item.unstable_frontiers.diving_rig': 'Diving Rig',
    'item.unstable_frontiers.diving_rig.tip0': 'Wear (back curio slot, or chest slot). Breathes for you under water.',
    'item.unstable_frontiers.diving_rig.tip1': 'Refills in open air, faster in the Drowned Expanse, fastest over a Breath Vent.',
    'item.unstable_frontiers.diving_rig.tip2': 'Below y 100 in the Expanse it drains three times as fast.',
    'item.unstable_frontiers.deep_rig': 'Deep Rig',
    'item.unstable_frontiers.deep_rig.tip0': 'Seven minutes of air, and no extra drain in the deep.',
    'item.unstable_frontiers.deep_rig.tip1': 'Refills like a diving rig.',
    'item.unstable_frontiers.rig.air': 'Air: %s:%s of %s min',
    'item.unstable_frontiers.swim_fins': 'Swim Fins',
    'item.unstable_frontiers.swim_fins.tip0': 'Wear (feet curio slot, or boots slot): much faster swimming.',
    'item.unstable_frontiers.breath_charm': 'Breath Charm',
    'item.unstable_frontiers.breath_charm.tip0': 'Wear (necklace curio slot): you breathe water, anywhere.',
    'item.unstable_frontiers.breath_charm.tip1': 'The tide gate accepts it in place of a rig.',
    'item.unstable_frontiers.echo_sounder': 'Echo Sounder',
    'item.unstable_frontiers.echo_sounder.tip0': 'In the Drowned Expanse: hold it to see the way and depth to a charted place.',
    'item.unstable_frontiers.echo_sounder.tip1': 'Use to pick the next charted place; sneak and use to list them all.',
    'item.unstable_frontiers.echo_sounder.tip2': 'Places are charted when you reach them, or when a fight ahead of them is won.',
    'item.unstable_frontiers.pressure_valve': 'Pressure Valve',
    'item.unstable_frontiers.pressure_valve.tip0': 'From Deepwork Station. Half of a Deep Rig.',
    'item.unstable_frontiers.pressure_valve.tip1': 'Craft with a Diving Rig and a Keel Plate.',
    'item.unstable_frontiers.keel_plate': 'Keel Plate',
    'item.unstable_frontiers.keel_plate.tip0': 'From the Wreckmaw. The other half of a Deep Rig.',
    'item.unstable_frontiers.keel_plate.tip1': 'Craft with a Diving Rig and a Pressure Valve.',
    'item.unstable_frontiers.choir_pearl': 'Choir Pearl',
    'item.unstable_frontiers.choir_pearl.tip0': 'From the Choir Temple.',
    'item.unstable_frontiers.choir_pearl.tip1': 'Craft into Abyssal Goggles (with a glow ink sac) for Deep-Sight Goggles.',
    'item.unstable_frontiers.abyssal_pearl': 'Abyssal Pearl',
    'item.unstable_frontiers.abyssal_pearl.tip0': 'From the Deepcaller. Repairs the Undertow.',
    'item.unstable_frontiers.abyssal_pearl.tip1': 'Three, with a heart of the sea or an eclipse scale, make a Breath Charm.',
    'item.unstable_frontiers.undertow': 'Undertow',
    'item.unstable_frontiers.undertow.tip0': 'Use: cast a 24-block line. A creature is dragged to you; a wall drags you to it.',
    'item.unstable_frontiers.undertow.tip1': 'Strikes harder against creatures in water or of the sea.',
    'item.unstable_frontiers.undertow.tip2': 'Works anywhere: the frontier\'s cliffs, the Abyss\'s islands. Bosses cannot be dragged.',
    'lens.unstable_frontiers.sunken': 'Sunken Gate',
    'item.unstable_frontiers.rift_lens.tip3': 'It also finds the Sunken Gates, the way into the Drowned Expanse.',
    'hud.unstable_frontiers.rig': 'Rig %s:%s',
    'landmark.unstable_frontiers.sunken_gate.subtitle': 'A flooded stair. The gate at the bottom wants divers, not swimmers.',
    'landmark.unstable_frontiers.sunken_gate.conquered': '',
    'landmark.unstable_frontiers.drowned_station.subtitle': 'Ring the bell to make this shelter yours.',
    'landmark.unstable_frontiers.drowned_station.conquered': '',
    'landmark.unstable_frontiers.drowned_place.subtitle': 'The surveyors\' charts end here.',
    'landmark.unstable_frontiers.drowned_place.conquered': 'Cleared. The way onward is charted.',
    'landmark.unstable_frontiers.drowned_vault.subtitle': 'The Deepcaller sleeps under the dome. The abyssal bell wakes it.',
    'landmark.unstable_frontiers.drowned_vault.conquered': '',
    'place.unstable_frontiers.state.charted': 'charted',
    'message.unstable_frontiers.tide_gate_refuses': 'The tide gate will not open: %s',
    'message.unstable_frontiers.need_both': 'you need Abyssal Goggles and a Diving Rig (or a Breath Charm) worn, not carried.',
    'message.unstable_frontiers.need_rig': 'you need a Diving Rig (or a Breath Charm) worn, not carried.',
    'message.unstable_frontiers.need_goggles': 'you need Abyssal Goggles worn, not carried.',
    'message.unstable_frontiers.no_drowned': 'The Drowned Expanse is missing (is the data pack disabled?).',
    'message.unstable_frontiers.drowned_welcome': 'The Drowned Expanse. You stand in Tidewatch Station\'s air dome; the gate here leads back. Your rig breathes for you: watch the gauge, and refill over Breath Vents or in a dome. Ring the tide bell to make a shelter yours: if you black out, the tide returns you to it. Hold the echo sounder to find the charted stations.',
    'message.unstable_frontiers.charted': 'Charted: %s.',
    'message.unstable_frontiers.bell_new': 'You ring the bell of %s. This shelter is yours now: black out, and the tide brings you back here.',
    'message.unstable_frontiers.bell_rung': 'You ring the bell of %s again. Shelter set.',
    'message.unstable_frontiers.bell_list': 'Other bells you have rung: %s. Sneak and ring to travel to the next.',
    'message.unstable_frontiers.bell_none': 'No other bells rung yet.',
    'message.unstable_frontiers.bell_travel': 'The tide carries you to %s.',
    'message.unstable_frontiers.drowned_rescue': 'Everything goes dark... The tide carries you back to your shelter.',
    'message.unstable_frontiers.drowned_belongings': 'Your belongings sank in the Drowned Expanse at %s %s %s. They keep for fifteen minutes and do not drift.',
    'message.unstable_frontiers.rig_30': 'Rig: 30 seconds of air left.',
    'message.unstable_frontiers.rig_10': 'Rig: 10 seconds of air left! Surface or find a vent.',
    'message.unstable_frontiers.rig_empty': 'Your rig is empty. You are holding your breath now: get to air, a vent or a dome.',
    'message.unstable_frontiers.deep_line': 'Below the deep line (y 100) your diving rig drains three times as fast. A Deep Rig would not.',
    'message.unstable_frontiers.sounder_elsewhere': 'The echo sounder only answers in the Drowned Expanse.',
    'message.unstable_frontiers.sounder_line': '%s: %s blocks %s %s',
    'message.unstable_frontiers.ray_content': 'The lanternray eats, content. There is nowhere left it can lead you.',
    'message.unstable_frontiers.ray_leads': 'The lanternray flashes and turns: follow it.',
    'message.unstable_frontiers.undertow_boss': 'Too heavy to drag.',
    'message.unstable_frontiers.deepcaller_awake': 'The Deepcaller is already awake.',
    'message.unstable_frontiers.deepcaller_rises': 'The bell\'s note goes down and down. Something answers from below the dome.',
    'message.unstable_frontiers.deepcaller_sinks': 'The Deepcaller sinks back into the dark. Ring the bell again when you are ready.',
    'message.unstable_frontiers.deepcaller_falls': 'The Deepcaller\'s light goes out.',
    'boss.unstable_frontiers.deepcaller.lure': 'Its lure brightens: look away or put stone between you!',
    'boss.unstable_frontiers.deepcaller.charge': 'It coils: get off its line, and let it hit the dome wall!',
    'boss.unstable_frontiers.deepcaller.vortex': 'The water turns: swim outward, away from it!',
    'boss.unstable_frontiers.deepcaller.phase2': 'The Deepcaller roars. It charges twice now, and calls its brood.',
    'hint.unstable_frontiers.murkjaw': 'A Murkjaw: when its jaw unhinges and bubbles mark a line, swim off the line. A miss into a wall stuns it (double damage).',
    'hint.unstable_frontiers.lanternray': 'Lanternrays are harmless. Feed one glow berries and it leads you to a place you have not charted.',
    'advancement.unstable_frontiers.sunken_gate': 'Sunken Stair',
    'advancement.unstable_frontiers.sunken_gate.desc': 'Find a Sunken Gate in the frontier (a Rift Lens points to one)',
    'advancement.unstable_frontiers.diving_gear': 'Suited Up',
    'advancement.unstable_frontiers.diving_gear.desc': 'Craft Abyssal Goggles and a Diving Rig (both need a Gnashback plate)',
    'advancement.unstable_frontiers.drowned': 'Into the Drowned Expanse',
    'advancement.unstable_frontiers.drowned.desc': 'Pass the tide gate wearing goggles and a rig',
    'advancement.unstable_frontiers.deep_rig': 'Below the Line',
    'advancement.unstable_frontiers.deep_rig.desc': 'Build a Deep Rig from Deepwork\'s valve and the Wreckmaw\'s keel plate',
    'advancement.unstable_frontiers.deep_sight': 'Clear Water',
    'advancement.unstable_frontiers.deep_sight.desc': 'Make Deep-Sight Goggles from a Choir Pearl',
    'advancement.unstable_frontiers.deepcaller': 'Lights Out',
    'advancement.unstable_frontiers.deepcaller.desc': 'Ring the abyssal bell and defeat the Deepcaller',
    'advancement.unstable_frontiers.breath_charm': 'Gills',
    'advancement.unstable_frontiers.breath_charm.desc': 'Make a Breath Charm and never need the rig again',
}
for k, v in PLACES.items():
    LANG[f'place.unstable_frontiers.{k}'] = v

SOUNDS = {
    'ray.ambient': (['drowned/ray_ambient'], 'Lanternray sings'),
    'ray.hurt': (['drowned/ray_hurt'], 'Lanternray hurts'),
    'ray.death': (['drowned/ray_death'], 'Lanternray dies'),
    'ray.chime': (['drowned/ray_chime'], 'Lanternray chimes'),
    'murkjaw.ambient': (['drowned/murkjaw_ambient'], 'Murkjaw growls'),
    'murkjaw.hurt': (['drowned/murkjaw_hurt'], 'Murkjaw hurts'),
    'murkjaw.death': (['drowned/murkjaw_death'], 'Murkjaw dies'),
    'murkjaw.tell': (['drowned/murkjaw_tell'], 'Murkjaw rattles its jaw'),
    'murkjaw.lunge': (['drowned/murkjaw_lunge'], 'Murkjaw lunges'),
    'murkjaw.bite': (['drowned/murkjaw_bite'], 'Murkjaw bites'),
    'murkjaw.stun': (['drowned/murkjaw_stun'], 'Murkjaw hits the wall'),
    'deepcaller.ambient': (['drowned/deepcaller_ambient'], 'The Deepcaller calls'),
    'deepcaller.hurt': (['drowned/deepcaller_hurt'], 'The Deepcaller hurts'),
    'deepcaller.death': (['drowned/deepcaller_death'], 'The Deepcaller dies'),
    'deepcaller.roar': (['drowned/deepcaller_roar'], 'The Deepcaller roars'),
    'deepcaller.lure': (['drowned/deepcaller_lure'], 'The lure brightens'),
    'deepcaller.charge_tell': (['drowned/deepcaller_charge_tell'], 'The Deepcaller coils'),
    'deepcaller.charge': (['drowned/deepcaller_charge'], 'The Deepcaller charges'),
    'deepcaller.slam': (['drowned/deepcaller_slam'], 'The Deepcaller hits the wall'),
    'deepcaller.vortex': (['drowned/deepcaller_vortex'], 'The water turns'),
    'deepcaller.brood': (['drowned/deepcaller_brood'], 'The Deepcaller calls its brood'),
    'tide.gate': (['drowned/tide_gate'], 'The tide gate opens'),
    'tide.gate_refuse': (['drowned/tide_gate_refuse'], 'The tide gate stays shut'),
    'tide.bell': (['drowned/tide_bell'], 'A tide bell rings'),
    'tide.abyssal_bell': (['drowned/tide_abyssal_bell'], 'The abyssal bell tolls'),
    'rig.warn': (['drowned/rig_warn'], 'Rig air low'),
    'undertow.cast': (['drowned/undertow_cast'], 'Undertow cast'),
    'drowned.ambient': (['drowned/drowned_ambient'], 'The deep water hums'),
}


def write_all():
    dimension()
    blocks()
    loot()
    recipes()
    tags()
