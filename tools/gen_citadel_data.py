import json, os, urllib.request

D = '/home/claude/aurelia/src/main/resources/data/aurelia'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


CITADELS = {
    'rootbound_citadel': dict(biomes=['#minecraft:is_forest'], step='surface_structures', start=-11, adapt='beard_thin',
                              mob='aurelia:rootstalker', spacing=28, separation=10, salt=71920501),
    'stormwatch_citadel': dict(biomes=['#minecraft:is_mountain'], step='surface_structures', start=-8, adapt='beard_thin',
                               mob='aurelia:gale_talon', spacing=24, separation=8, salt=71920502),
    'ashen_citadel': dict(biomes=['#minecraft:is_badlands', 'minecraft:desert', '#minecraft:is_savanna', '#minecraft:is_taiga',
                                  'minecraft:swamp'],
                          step='underground_structures', start=-66, adapt='none', mob='aurelia:cinder_hound',
                          spacing=30, separation=12, salt=71920503),
}
for name, c in CITADELS.items():
    write(f'{D}/tags/worldgen/biome/has_structure/{name}.json', {'replace': False, 'values': c['biomes']})
    write(f'{D}/worldgen/structure/{name}.json', {
        'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/{name}', 'step': c['step'],
        'spawn_overrides': {'monster': {'bounding_box': 'full', 'spawns': [{'type': c['mob'], 'weight': 1, 'minCount': 1, 'maxCount': 1}]}},
        'terrain_adaptation': c['adapt'], 'start_pool': f'aurelia:{name}/start', 'size': 1,
        'start_height': {'absolute': c['start']}, 'project_start_to_heightmap': 'WORLD_SURFACE_WG',
        'max_distance_from_center': 80, 'use_expansion_hack': False})
    write(f'{D}/worldgen/template_pool/{name}/start.json', {
        'fallback': 'minecraft:empty',
        'elements': [{'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:{name}',
                                               'processors': {'processors': []}, 'projection': 'rigid'}}]})
    write(f'{D}/worldgen/structure_set/{name}.json', {
        'structures': [{'structure': f'aurelia:{name}', 'weight': 1}],
        'placement': {'type': 'minecraft:random_spread', 'spacing': c['spacing'], 'separation': c['separation'], 'salt': c['salt']}})


def entry(item, weight, lo=None, hi=None):
    e = {'type': 'minecraft:item', 'name': item, 'weight': weight}
    if lo is not None:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]
    return e


common = [entry('minecraft:diamond', 6, 1, 3), entry('minecraft:emerald', 10, 2, 6), entry('minecraft:golden_apple', 4),
          entry('minecraft:experience_bottle', 8, 4, 10), entry('minecraft:ender_pearl', 5, 1, 3),
          entry('minecraft:enchanted_golden_apple', 1)]
write(f'{D}/loot_tables/chests/rootbound_hearts.json', {'type': 'minecraft:chest', 'pools': [
    {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': 'aurelia:spore_heart',
                                                'functions': [{'function': 'minecraft:set_count', 'count': 2}]}]},
    {'rolls': {'min': 2, 'max': 4}, 'bonus_rolls': 0, 'entries': common + [entry('minecraft:glow_berries', 6, 4, 10), entry('minecraft:moss_block', 5, 6, 16)]}]})
write(f'{D}/loot_tables/chests/ashen_sigils.json', {'type': 'minecraft:chest', 'pools': [
    {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': 'aurelia:soul_sigil',
                                                'functions': [{'function': 'minecraft:set_count', 'count': 3}]}]},
    {'rolls': {'min': 2, 'max': 4}, 'bonus_rolls': 0, 'entries': common + [entry('minecraft:echo_shard', 3, 1, 2), entry('minecraft:soul_sand', 5, 6, 16)]}]})
print('citadel data written')
