"""Completes the realms' biomes.

Every realm was one fixed biome, and some were bare: Skyreach and the Clockwork Rift had no features at all, and the Grove and the
Hollow never placed their own ores. This makes each realm three biomes, chosen by the temperature noise:

  grove      The Gaudy Grove        Bloomwild (cherry and flower meadows)        Mossveil Thicket (dark, fern-choked jungle)
  skyreach   Skyreach               Cloud Meadows (flowered islands)             Stormfront (black sky, sparks, bare rock)
  hollow     The Hollow             Soulfire Wastes (soul sand, blue flame)      Ember Deeps (basalt deltas, magma, fire)
  drowned    The Drowned Expanse    Kelp Forest                                  Coral Graveyard (dead reefs, fossils)
  pale       The Pale Reach         Frozen Spires (ice spikes, icebergs)         Whisper Taiga (snowbound spruce)
  scarlet    The Scarlet Waste      Glass Dunes (rich in scarlet glass)          Bone Flats (fossils, dead brush)
  clockwork  The Clockwork Rift     Gearfields (copper and redstone)             The Stopped Hour (amethyst, dripstone)
  mycelial   The Mycelial Deep      Glowcap Hollows (lush, glowing)              Rootmaw (roots, dripstone, sculk veins)

and gives every biome a full set of features: the realm's own ore (new ones for Stormglass and Chronite), common ores, springs and
lakes, ground decoration and vegetation. Every biome in the mod lists its features in one shared order per step, so the game's feature
order check can never find a cycle. The realms' structure tags take in the new biomes, so every realm structure still generates in all
three. The Last Realm stays one biome.
"""
import copy
import json
import os

import paths

D = paths.RES + '/data/aurelia'
WG = D + '/worldgen'
LANG = paths.RES + '/assets/aurelia/lang/en_us.json'
REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']
RAW, LAKES, LOCAL, U_STRUCT, S_STRUCT, STRONG, ORES, U_DECOR, SPRINGS, VEG, TOP = range(11)


def mc(*names):
    return [f'minecraft:{n}' for n in names]


def au(*names):
    return [f'aurelia:{n}' for n in names]


# what every biome of a realm has, beyond its own extras: step -> features
BASE = {
    'grove': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_copper', 'ore_diamond') + au('ore_verdant'), SPRINGS: au('grove_springs') + mc('spring_water'),
              LAKES: mc('lake_lava_underground'), VEG: mc('glow_lichen'), TOP: []},
    'skyreach': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_copper', 'ore_gold') + au('ore_stormglass'), SPRINGS: mc('spring_water'),
                 LOCAL: mc('forest_rock')},
    'hollow': {ORES: mc('ore_magma', 'ore_gold_nether', 'ore_quartz_nether', 'ore_blackstone') + au('ore_emberheart'), SPRINGS: mc('spring_lava', 'spring_closed'),
               U_DECOR: mc('glowstone_extra', 'glowstone')},
    'drowned': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_iron_middle', 'ore_gold', 'ore_diamond', 'disk_sand', 'disk_clay', 'disk_gravel') + au('ore_tidestone'),
                SPRINGS: mc('spring_water'), VEG: mc('sea_pickle', 'glow_lichen')},
    'pale': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_iron_middle', 'ore_gold', 'ore_diamond') + au('ore_rime'), SPRINGS: mc('spring_water', 'spring_lava_frozen'),
             TOP: mc('freeze_top_layer')},
    'scarlet': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_iron_middle', 'ore_gold', 'ore_gold_extra', 'ore_diamond') + au('ore_sunglass'),
                SPRINGS: mc('spring_lava'), LAKES: mc('lake_lava_surface')},
    'clockwork': {ORES: mc('ore_coal_upper', 'ore_iron_upper', 'ore_copper', 'ore_redstone', 'ore_lapis') + au('ore_chronite'), SPRINGS: mc('spring_lava'),
                  VEG: mc('glow_lichen'), U_STRUCT: mc('amethyst_geode')},
    'mycelial': {ORES: mc('ore_iron_upper', 'ore_gold', 'ore_diamond', 'ore_tuff') + au('ore_bloomspore'), U_STRUCT: mc('amethyst_geode'),
                 SPRINGS: mc('spring_water'), VEG: mc('spore_blossom', 'glow_lichen', 'brown_mushroom_normal', 'red_mushroom_normal')},
}

# (id, name, temperature band, extra features by step, effect overrides, spawn weight changes)
COLD, MID, WARM = [-1.0, -0.3], [-0.3, 0.3], [0.3, 1.0]
VARIANTS = {
    'grove': [
        ('grove', 'The Gaudy Grove', MID, {VEG: mc('trees_jungle', 'mushroom_island_vegetation', 'patch_large_fern', 'flower_flower_forest', 'forest_flowers',
                                                   'patch_grass_jungle', 'jungle_bush', 'patch_tall_grass') + au('grove_vines') +
                                                mc('brown_mushroom_normal', 'red_mushroom_normal')}, {}, {}),
        ('bloomwild', 'Bloomwild', WARM, {VEG: mc('trees_cherry', 'flower_cherry', 'flower_meadow', 'flower_flower_forest', 'patch_grass_plain', 'patch_tall_grass',
                                                  'patch_sunflower', 'patch_berry_common')},
         {'grass_color': 0xB4E06A, 'foliage_color': 0xF2A6D2, 'fog_color': 0xF6D6E8, 'particle': {'options': {'type': 'minecraft:cherry_leaves'}, 'probability': 0.01}},
         {'mossling': 14}),
        ('mossveil_thicket', 'Mossveil Thicket', COLD, {VEG: mc('trees_jungle', 'dark_forest_vegetation', 'patch_large_fern', 'patch_grass_jungle', 'vines',
                                                                 'brown_mushroom_old_growth', 'red_mushroom_old_growth') + au('grove_vines')},
         {'grass_color': 0x3E7A2C, 'foliage_color': 0x2C5E22, 'fog_color': 0x6A8E5A, 'sky_color': 0x5E8A6E,
          'particle': {'options': {'type': 'minecraft:spore_blossom_air'}, 'probability': 0.03}}, {'grove_ant': 16}),
    ],
    'skyreach': [
        ('skyreach', 'Skyreach', MID, {VEG: mc('trees_meadow', 'patch_grass_plain', 'flower_meadow', 'patch_tall_grass')}, {}, {}),
        ('cloud_meadows', 'Cloud Meadows', WARM, {VEG: mc('trees_birch_and_oak', 'flower_plains', 'flower_meadow', 'patch_sunflower', 'patch_tall_grass',
                                                          'patch_grass_plain')},
         {'grass_color': 0x9EE07A, 'sky_color': 0xA8DCFF, 'fog_color': 0xE8F4FF}, {'cloud_ray': 14}),
        ('stormfront', 'Stormfront', COLD, {VEG: mc('trees_windswept_hills', 'patch_grass_normal')},
         {'sky_color': 0x3A4458, 'fog_color': 0x56607A, 'grass_color': 0x6A8A6E,
          'particle': {'options': {'type': 'minecraft:electric_spark'}, 'probability': 0.006}}, {'sky_sentinel': 12}),
    ],
    'hollow': [
        ('hollow', 'The Hollow', MID, {U_DECOR: mc('basalt_blobs', 'blackstone_blobs', 'basalt_pillar', 'patch_soul_fire') + au('hollow_lava_falls'),
                                       VEG: au('giant_red_fungus_patch') + mc('brown_mushroom_nether', 'red_mushroom_nether')}, {}, {}),
        ('soulfire_wastes', 'Soulfire Wastes', COLD, {ORES: mc('ore_soul_sand'), U_DECOR: mc('blackstone_blobs', 'patch_soul_fire', 'basalt_pillar'),
                                                       VEG: mc('brown_mushroom_nether')},
         {'fog_color': 0x1B3A4A, 'particle': {'options': {'type': 'minecraft:soul_fire_flame'}, 'probability': 0.004}}, {'hollow_shade': 16}),
        ('ember_deeps', 'Ember Deeps', WARM, {RAW: mc('large_basalt_columns', 'small_basalt_columns'),
                                               U_DECOR: mc('delta', 'basalt_blobs', 'patch_fire') + au('hollow_lava_falls'), SPRINGS: mc('spring_delta'),
                                               VEG: au('giant_red_fungus_patch')},
         {'fog_color': 0x5A1E0E, 'particle': {'options': {'type': 'minecraft:ash'}, 'probability': 0.05}}, {'ember_beetle': 14}),
    ],
    'drowned': [
        ('drowned', 'The Drowned Expanse', MID, {VEG: mc('trees_mangrove', 'warm_ocean_vegetation', 'kelp_warm', 'seagrass_warm')}, {}, {}),
        ('kelp_forest', 'Kelp Forest', COLD, {VEG: mc('kelp_cold', 'kelp_warm', 'seagrass_deep', 'seagrass_normal')},
         {'water_color': 0x2E8A6E, 'water_fog_color': 0x0E3A2E}, {'lantern_jelly': 14}),
        ('coral_graveyard', 'Coral Graveyard', WARM, {U_STRUCT: mc('fossil_upper', 'fossil_lower'), ORES: mc('disk_gravel'),
                                                      VEG: mc('warm_ocean_vegetation', 'seagrass_simple', 'underwater_magma')},
         {'water_color': 0x3A5A6A, 'water_fog_color': 0x101A22, 'fog_color': 0x6A7A86}, {'razorclaw': 14}),
    ],
    'pale': [
        ('pale', 'The Pale Reach', MID, {LOCAL: mc('ice_spike', 'ice_patch'), VEG: mc('trees_snowy'), U_DECOR: mc('blue_ice')}, {}, {}),
        ('frozen_spires', 'Frozen Spires', COLD, {LOCAL: mc('iceberg_packed', 'iceberg_blue', 'ice_spike', 'ice_patch'), U_DECOR: mc('blue_ice')},
         {'fog_color': 0xC8E0FF, 'sky_color': 0xB8D4F0, 'particle': {'options': {'type': 'minecraft:snowflake'}, 'probability': 0.03}}, {'rimefang': 14}),
        ('whisper_taiga', 'Whisper Taiga', WARM, {VEG: mc('trees_taiga', 'trees_grove', 'patch_taiga_grass', 'patch_berry_common', 'brown_mushroom_taiga')},
         {'grass_color': 0x86A08A, 'foliage_color': 0x5E7A66, 'fog_color': 0xA8B8C8}, {'frost_hare': 14}),
    ],
    'scarlet': [
        ('scarlet', 'The Scarlet Waste', MID, {VEG: mc('patch_dead_bush_badlands', 'patch_cactus_desert')}, {}, {}),
        ('glass_dunes', 'Glass Dunes', WARM, {ORES: au('ore_sunglass_rich'), S_STRUCT: mc('desert_well'), VEG: mc('patch_cactus_decorated', 'patch_dead_bush_2')},
         {'fog_color': 0xFFB880, 'sky_color': 0xFFA070, 'particle': {'options': {'type': 'minecraft:white_ash'}, 'probability': 0.02}}, {'glasswing_scarab': 14}),
        ('bone_flats', 'Bone Flats', COLD, {U_STRUCT: mc('fossil_upper', 'fossil_lower'), VEG: mc('trees_badlands', 'patch_dead_bush_2', 'patch_grass_badlands')},
         {'fog_color': 0xD8C0A8, 'grass_color': 0xA89A60, 'foliage_color': 0x9A8A52}, {'sand_skink': 14}),
    ],
    'clockwork': [
        ('clockwork', 'The Clockwork Rift', MID, {U_DECOR: mc('pointed_dripstone')}, {}, {}),
        ('gearfields', 'Gearfields', WARM, {ORES: mc('ore_copper_large', 'ore_redstone_lower'), U_DECOR: mc('pointed_dripstone')},
         {'fog_color': 0x6A4A2A, 'sky_color': 0x8A6A4A}, {'gearskitter': 14}),
        ('stopped_hour', 'The Stopped Hour', COLD, {U_DECOR: mc('large_dripstone', 'dripstone_cluster', 'sculk_vein')},
         {'fog_color': 0x3A2A5A, 'sky_color': 0x2A1A4A, 'particle': {'options': {'type': 'minecraft:reverse_portal'}, 'probability': 0.01}}, {'cogling': 14}),
    ],
    'mycelial': [
        ('mycelial', 'The Mycelial Deep', MID, {VEG: mc('mushroom_island_vegetation')}, {}, {}),
        ('glowcap_hollows', 'Glowcap Hollows', WARM, {VEG: mc('lush_caves_vegetation', 'lush_caves_ceiling_vegetation', 'cave_vines', 'mushroom_island_vegetation')},
         {'fog_color': 0x6AA07A, 'particle': {'options': {'type': 'minecraft:spore_blossom_air'}, 'probability': 0.04}}, {'spore_puff': 14}),
        ('rootmaw', 'Rootmaw', COLD, {U_DECOR: mc('dripstone_cluster', 'large_dripstone', 'sculk_vein'), U_STRUCT: mc('monster_room'),
                                      VEG: mc('rooted_azalea_tree')},
         {'fog_color': 0x2A1A22, 'particle': {'options': {'type': 'minecraft:mycelium'}, 'probability': 0.03}}, {'root_grub': 16}),
    ],
}
MUSIC = {'grove': 'music.overworld.jungle', 'bloomwild': 'music.overworld.cherry_grove', 'mossveil_thicket': 'music.overworld.lush_caves',
         'skyreach': 'music.overworld.meadow', 'cloud_meadows': 'music.overworld.flower_forest', 'stormfront': 'music.overworld.stony_peaks',
         'hollow': 'music.nether.crimson_forest', 'soulfire_wastes': 'music.nether.soul_sand_valley', 'ember_deeps': 'music.nether.basalt_deltas',
         'drowned': 'music.under_water', 'kelp_forest': 'music.under_water', 'coral_graveyard': 'music.under_water',
         'pale': 'music.overworld.snowy_slopes', 'frozen_spires': 'music.overworld.frozen_peaks', 'whisper_taiga': 'music.overworld.grove',
         'scarlet': 'music.overworld.desert', 'glass_dunes': 'music.overworld.desert', 'bone_flats': 'music.overworld.badlands',
         'clockwork': 'music.overworld.dripstone_caves', 'gearfields': 'music.overworld.old_growth_taiga', 'stopped_hour': 'music.overworld.deep_dark',
         'mycelial': 'music.overworld.lush_caves', 'glowcap_hollows': 'music.overworld.lush_caves', 'rootmaw': 'music.overworld.deep_dark'}
AMBIENT = {'hollow': ('ambient.crimson_forest.loop', 'ambient.crimson_forest.additions'),
           'soulfire_wastes': ('ambient.soul_sand_valley.loop', 'ambient.soul_sand_valley.additions'),
           'ember_deeps': ('ambient.basalt_deltas.loop', 'ambient.basalt_deltas.additions'),
           'rootmaw': (None, 'ambient.warped_forest.additions'), 'kelp_forest': (None, 'ambient.underwater.loop.additions'),
           'coral_graveyard': (None, 'ambient.underwater.loop.additions')}
DECOR_TAG = {'grove': ['grove_decor'], 'skyreach': ['skyreach_islands'], 'hollow': ['hollow_decor'], 'drowned': ['drowned_decor'], 'pale': ['pale_decor'],
             'scarlet': ['scarlet_decor'], 'clockwork': ['clockwork_decor'], 'mycelial': ['mycelial_decor']}
NEW_ORES = {'stormglass': ('aurelia:stormglass_ore', 'stone', 9, 12, 0, 250), 'chronite': ('aurelia:chronite_ore', 'stone', 8, 12, 0, 250),
            'sunglass_rich': (None, None, 0, 10, 0, 220)}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=2)


def ores():
    """Stormglass for Skyreach's rock, Chronite for the Rift's, and a richer seam of scarlet glass for the Glass Dunes."""
    for name, (block, _, size, count, lo, hi) in NEW_ORES.items():
        if block:
            dump(f'{WG}/configured_feature/ore_{name}.json', {'type': 'minecraft:ore', 'config': {'discard_chance_on_air_exposure': 0.0, 'size': size, 'targets': [
                {'state': {'Name': block}, 'target': {'predicate_type': 'minecraft:tag_match', 'tag': 'minecraft:stone_ore_replaceables'}},
                {'state': {'Name': block}, 'target': {'predicate_type': 'minecraft:tag_match', 'tag': 'minecraft:deepslate_ore_replaceables'}}]}})
        feature = 'aurelia:ore_sunglass' if name == 'sunglass_rich' else f'aurelia:ore_{name}'
        dump(f'{WG}/placed_feature/ore_{name}.json', {'feature': feature, 'placement': [
            {'type': 'minecraft:count', 'count': count}, {'type': 'minecraft:in_square'},
            {'type': 'minecraft:height_range', 'height': {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}},
            {'type': 'minecraft:biome'}]})


def features_for(realm, extra):
    steps = [[] for _ in range(11)]
    for src in (BASE[realm], extra):
        for st, feats in src.items():
            for f in feats:
                if f not in steps[st]:
                    steps[st].append(f)
    return steps


def main():
    ores()
    base_src = {r: json.load(open(f'{WG}/biome/{r}.json')) for r in REALMS}
    router_noise = json.load(open(f'{WG}/noise_settings/grove.json'))['noise_router']
    biomes = {}
    for realm in REALMS:
        for vid, name, band, extra, eff, spawn in VARIANTS[realm]:
            b = copy.deepcopy(base_src[realm])
            b['effects'].update(eff)
            for cat, entries in b['spawners'].items():
                for e in entries:
                    key = e['type'].split(':')[1]
                    if key in spawn:
                        e['weight'] = spawn[key]
            b['_steps'] = features_for(realm, extra)
            b['effects']['music'] = {'sound': f'minecraft:{MUSIC[vid]}', 'min_delay': 6000, 'max_delay': 18000, 'replace_current_music': False}
            if vid in AMBIENT:                                            # each biome sounds like itself
                loop, add = AMBIENT[vid]
                if loop:
                    b['effects']['ambient_sound'] = f'minecraft:{loop}'
                b['effects']['additions_sound'] = {'sound': f'minecraft:{add}', 'tick_chance': 0.0111}
            biomes[vid] = (realm, name, band, b)
    # one shared order per step across every biome, so no two biomes can disagree about which feature comes first
    order = [[] for _ in range(11)]
    for vid, (_, _, _, b) in biomes.items():
        for st in range(11):
            for f in b['_steps'][st]:
                if f not in order[st]:
                    order[st].append(f)
    lang = json.load(open(LANG, encoding='utf-8'))
    for vid, (realm, name, band, b) in biomes.items():
        b['features'] = [sorted(b['_steps'][st], key=order[st].index) for st in range(11)]
        del b['_steps']
        dump(f'{WG}/biome/{vid}.json', b)
        lang[f'biome.aurelia.{vid}'] = name
    lang['biome.aurelia.last'] = 'The Last Realm'
    json.dump(lang, open(LANG, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    # each realm picks among its three by temperature; every other parameter spans everything
    span = [-2.0, 2.0]
    for realm in REALMS:
        dp = f'{D}/dimension/{realm}.json'
        dim = json.load(open(dp))
        dim['generator']['biome_source'] = {'type': 'minecraft:multi_noise', 'biomes': [
            {'biome': f'aurelia:{vid}', 'parameters': {'temperature': band, 'humidity': span, 'continentalness': span, 'erosion': span, 'weirdness': span,
                                                       'depth': span, 'offset': 0.0}}
            for vid, _, band, _, _, _ in VARIANTS[realm]]}
        dump(dp, dim)
        np_ = f'{WG}/noise_settings/{realm}.json'
        ns = json.load(open(np_))
        for k in ('temperature', 'vegetation'):
            if not isinstance(ns['noise_router'][k], dict):
                ns['noise_router'][k] = router_noise[k]                  # the sky realms had a flat temperature: give them the noise
        dump(np_, ns)
        for tag in DECOR_TAG[realm]:
            tp = f'{D}/tags/worldgen/biome/has_structure/{tag}.json'
            t = json.load(open(tp))
            t['values'] = sorted(set(t['values']) | {f'aurelia:{v[0]}' for v in VARIANTS[realm]})
            dump(tp, t)
    print('biomes:', len(biomes), 'in', len(REALMS), 'realms')


if __name__ == '__main__':
    main()
