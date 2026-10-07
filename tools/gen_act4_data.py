"""The finale's data and assets: the Last Realm (dimension, biome), the Convergence Gate's placement, Realm Node, Unmaking Anchor and
Last-realm Waygate block assets, loot, names. Relic and pedestal models come from relics.py; templates from gen_act4_structures.py."""
import json

from PIL import ImageDraw

from gen_act3_data import A, BLK, D, bs, entry, item_model, model, noise_img, pool, save, spawn, structure, write, biome
from gen_act4_structures import GLASS, REALMS
import relics

# =========================================================================================== the Last Realm
write(f'{D}/dimension_type/last.json', {
    'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False, 'ambient_light': 0.1,
    'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False, 'logical_height': 256, 'min_y': 0, 'height': 256,
    'infiniburn': '#minecraft:infiniburn_end', 'effects': 'minecraft:the_end',
    'monster_spawn_light_level': {'type': 'minecraft:uniform', 'value': {'min_inclusive': 0, 'max_inclusive': 7}},
    'monster_spawn_block_light_limit': 0, 'fixed_time': 18000})
write(f'{D}/dimension/last.json', {'type': 'aurelia:last', 'generator': {
    'type': 'minecraft:noise', 'settings': 'aurelia:last', 'biome_source': {'type': 'minecraft:fixed', 'biome': 'aurelia:last'}}})
write(f'{D}/worldgen/noise_settings/last.json', json.load(open(f'{D}/worldgen/noise_settings/clockwork.json')))
biome('last', False, 0.5, 0.0,
      {'sky_color': '#000000', 'fog_color': '#1A0A2E', 'water_color': '#5A2AA0', 'water_fog_color': '#0A0418', 'grass_color': '#6A6A6A',
       'foliage_color': '#5A5A5A'},
      {'particle': {'options': {'type': 'minecraft:white_ash'}, 'probability': 0.02},
       'ambient_sound': 'minecraft:ambient.soul_sand_valley.loop',
       'mood_sound': {'sound': 'minecraft:ambient.soul_sand_valley.mood', 'tick_delay': 6000, 'block_search_extent': 8, 'offset': 2.0},
       'music': {'sound': 'minecraft:music.end', 'min_delay': 6000, 'max_delay': 12000, 'replace_current_music': True}},
      {}, [], {})

# =========================================================================================== the Convergence Gate in the overworld
structure('convergence_gate', 'convergence_gate', {'absolute': -6}, 'WORLD_SURFACE_WG', 'beard_box', {}, ['convergence_gate'], 44, 16, 71920509,
          None, ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow', 'minecraft:savanna', 'minecraft:forest',
                 'minecraft:birch_forest', 'minecraft:taiga', 'minecraft:snowy_plains', 'minecraft:desert'])

# =========================================================================================== loot
write(f'{D}/loot_tables/chests/convergence_cache.json', {'type': 'minecraft:chest', 'pools': [
    pool([entry('minecraft:diamond', 1, 3, 6)]), pool([entry('minecraft:netherite_scrap', 1, 1, 3)]),
    pool([entry('minecraft:enchanted_golden_apple', 1, 1, 1)], chance=0.4),
    pool([entry('minecraft:golden_apple', 4, 2, 4), entry('minecraft:ender_pearl', 4, 4, 8), entry('minecraft:experience_bottle', 4, 6, 12)], rolls=3)]})
MATERIAL = {'grove': 'verdant_shard', 'skyreach': 'stormglass_shard', 'hollow': 'emberheart', 'drowned': 'tidestone_shard', 'pale': 'rime_crystal',
            'scarlet': 'sunglass_shard', 'clockwork': 'chronite_shard', 'mycelial': 'bloomspore'}
for realm in REALMS:
    write(f'{D}/loot_tables/chests/last_{realm}.json', {'type': 'minecraft:chest', 'pools': [
        pool([entry('aurelia:' + MATERIAL[realm], 1, 6, 12)]),
        pool([entry('minecraft:diamond', 3, 1, 3), entry('minecraft:golden_carrot', 4, 4, 8), entry('minecraft:totem_of_undying', 1, 1, 1),
              entry('minecraft:netherite_scrap', 2, 1, 1)], rolls=2)]})
for b in ('relic_pedestal', 'realm_node', 'unmaking_anchor'):                # unbreakable or self-consuming: they drop nothing
    write(f'{D}/loot_tables/blocks/{b}.json', {'type': 'minecraft:block', 'pools': []})

# =========================================================================================== block assets
for realm in REALMS:
    col = relics.REALM_COLOR[realm]
    for lit in (False, True):
        sfx = 'lit' if lit else 'dark'
        side = noise_img((34, 30, 40), 6, 300 + REALMS.index(realm) * 2 + lit)
        d = ImageDraw.Draw(side)
        c = col if lit else tuple(v // 3 for v in col)
        d.rectangle([4, 2, 11, 13], outline=(200, 160, 70, 255))
        d.polygon([(8, 3), (11, 8), (8, 12), (5, 8)], fill=c + (255,))
        if lit:
            d.point([(8, 6), (8, 7), (7, 8), (9, 8)], fill=(255, 255, 255, 255))
        save(side, f'{BLK}/realm_node_{realm}_{sfx}_side.png')
        top = noise_img((34, 30, 40), 6, 400 + REALMS.index(realm) * 2 + lit)
        ImageDraw.Draw(top).ellipse([3, 3, 12, 12], fill=c + (255,), outline=(200, 160, 70, 255))
        save(top, f'{BLK}/realm_node_{realm}_{sfx}_top.png')
v = {}
for realm in REALMS:
    for lit in (False, True):
        m = f'realm_node_{realm}_{"lit" if lit else "dark"}'
        model(m, {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/{m}_top', 'side': f'aurelia:block/{m}_side'}})
        v[f'realm={realm},lit={str(lit).lower()}'] = {'model': f'aurelia:block/{m}'}
bs('realm_node', v)
item_model('realm_node', {'parent': 'aurelia:block/realm_node_grove_lit'})

img = noise_img((20, 14, 30), 6, 500)
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(226, 218, 200, 255))
for (a, b) in [((3, 2), (7, 9)), ((7, 9), (5, 14)), ((12, 1), (9, 7)), ((9, 7), (13, 13))]:
    d.line([a, b], fill=(190, 110, 255, 255))
save(img, f'{BLK}/unmaking_anchor.png')
bs('unmaking_anchor', {'': {'model': 'aurelia:block/unmaking_anchor'}})
model('unmaking_anchor', {'parent': 'minecraft:block/cube_all', 'textures': {'all': 'aurelia:block/unmaking_anchor'}})
item_model('unmaking_anchor', {'parent': 'aurelia:block/unmaking_anchor'})

for on in (False, True):                                             # the Waygate to the Last Realm: a starfield in a black and white frame
    sfx = 'on' if on else 'off'
    side = noise_img((30, 28, 34), 5, 600 + on)
    d = ImageDraw.Draw(side)
    for i in range(16):
        d.point([(i, 0), (i, 15), (0, i), (15, i)], fill=(226, 218, 200, 255) if (i // 2) % 2 else (20, 18, 24, 255))
    d.rectangle([3, 2, 12, 13], fill=(4, 2, 10, 255), outline=(220, 180, 80, 255))
    if on:
        for k, realm in enumerate(REALMS):
            d.point([(4 + k, 3 + (k * 5) % 9)], fill=relics.REALM_COLOR[realm] + (255,))
        d.point([(8, 7), (7, 8), (9, 8), (8, 9), (8, 8)], fill=(255, 255, 255, 255))
    save(side, f'{BLK}/waygate_last_{sfx}_side.png')
    top = noise_img((30, 28, 34), 5, 610 + on)
    ImageDraw.Draw(top).ellipse([3, 3, 12, 12], outline=((255, 255, 255) if on else (90, 90, 90)) + (255,))
    save(top, f'{BLK}/waygate_last_{sfx}_top.png')
wg = json.load(open(f'{A}/blockstates/waygate.json'))['variants']
for on in (False, True):
    sfx = 'on' if on else 'off'
    wg[f'realm=last,active={str(on).lower()}'] = {'model': f'aurelia:block/waygate_last_{sfx}'}
    model(f'waygate_last_{sfx}', {'parent': 'minecraft:block/cube_column', 'textures': {
        'end': f'aurelia:block/waygate_last_{sfx}_top', 'side': f'aurelia:block/waygate_last_{sfx}_side'}})
bs('waygate', wg)
item_model('unmaker_spawn_egg', {'parent': 'minecraft:item/template_spawn_egg'})

# =========================================================================================== tags
mp = f'{D}/../minecraft/tags/blocks/mineable/pickaxe.json'
j = json.load(open(mp))
j['values'] += [x for x in ['aurelia:unmaking_anchor'] if x not in j['values']]
write(mp, j)

# =========================================================================================== names
lp = f'{A}/lang/en_us.json'
lang = json.load(open(lp, encoding='utf-8'))
LORE = {'rootbound_heart': 'It still beats, slow as a tree grows. Mossback grew around it for a thousand years.',
        'storm_talon': 'Lightning crawls along it whenever someone lies nearby.',
        'sovereign_hand': 'The King held the crown in this hand when it broke. The soul fire in the palm is hers.',
        'abyssal_fang': 'Wet, always. Hold it to your ear and you hear the deep breathing.',
        'frozen_voice': 'Everything the White Silence took is in here. If it ever thaws, the Wastes will scream.',
        'glass_stinger': 'The last grain of the Sovereign\'s hourglass, kept where no one could turn it.',
        'chronal_eye': 'It watches the moment just behind this one.',
        'living_spore': 'Plant it and it would grow a world. That is the problem.',
        'hand_of_genesis': 'The hand that cut the worlds apart. Now it is yours.'}
lang.update({
    'entity.aurelia.unmaker': 'The Unmaker', 'item.aurelia.unmaker_spawn_egg': 'Unmaker Spawn Egg',
    'block.aurelia.relic_pedestal': 'Relic Pedestal', 'block.aurelia.realm_node': 'Realm Node', 'block.aurelia.unmaking_anchor': 'Unmaking Anchor',
    'item.aurelia.hand_of_genesis': 'Hand of Genesis', 'structure.aurelia.convergence_gate': 'Convergence Gate',
    'item.aurelia.relic.hint': 'One of eight. Lay it on its pedestal at the Convergence Gate.',
    'item.aurelia.hand_of_genesis.mode': 'Power: %s', 'item.aurelia.hand_of_genesis.use': 'Use to cast. Sneak and use to change power.',
})
for key, name, _, _, _ in relics.RELICS:
    lang[f'item.aurelia.{key}'] = name
for key, text in LORE.items():
    lang[f'item.aurelia.{key}.lore'] = text
json.dump(lang, open(lp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('finale data and assets written')
