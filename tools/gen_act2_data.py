"""Act two data and assets: the three outer-realm dimensions, their biomes and surface rules, ores, block/item assets,
loot tables, recipes, tags, structure definitions (citadels and realm structures) and names.
Structure templates themselves come from gen_act2_citadels.py and gen_act2_realms.py."""
import copy
import json
import os
import random

from PIL import Image, ImageDraw

import paths

ROOT = paths.RES
A = f'{ROOT}/assets/aurelia'
D = f'{ROOT}/data/aurelia'
V = paths.VANILLA
BLK, ITEM = f'{A}/textures/block', f'{A}/textures/item'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def vload(name):
    return json.load(open(f'{V}/{name}'))


# =========================================================================================== dimensions
DIMS = {
    # name: (fixed_time, ambient_light, sea_level, surface rule key)
    'drowned': (14000, 0.05, 96),
    'pale': (22800, 0.05, 63),
    'scarlet': (6000, 0.0, -63),
}
for name, (time, light, sea) in DIMS.items():
    write(f'{D}/dimension_type/{name}.json', {
        'ultrawarm': name == 'scarlet', 'natural': True, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False,
        'ambient_light': light, 'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False,
        'logical_height': 384, 'min_y': -64, 'height': 384, 'infiniburn': '#minecraft:infiniburn_overworld',
        'effects': 'minecraft:overworld', 'monster_spawn_light_level': {'type': 'minecraft:uniform', 'value': {'min_inclusive': 0, 'max_inclusive': 7}},
        'monster_spawn_block_light_limit': 0, 'fixed_time': time})
    write(f'{D}/dimension/{name}.json', {'type': f'aurelia:{name}', 'generator': {
        'type': 'minecraft:noise', 'settings': f'aurelia:{name}', 'biome_source': {'type': 'minecraft:fixed', 'biome': f'aurelia:{name}'}}})


# ---- surface rules
def block(name, props=None):
    s = {'Name': name}
    if props:
        s['Properties'] = props
    return {'type': 'minecraft:block', 'result_state': s}


def cond(c, then):
    return {'type': 'minecraft:condition', 'if_true': c, 'then_run': then}


def seq(*rules):
    return {'type': 'minecraft:sequence', 'sequence': list(rules)}


def depth(add=False, secondary=0, offset=0):
    return {'type': 'minecraft:stone_depth', 'offset': offset, 'surface_type': 'floor', 'add_surface_depth': add, 'secondary_depth_range': secondary}


def above_water():
    return {'type': 'minecraft:water', 'offset': -1, 'surface_depth_multiplier': 0, 'add_stone_depth': False}


def noise(lo, hi, name='minecraft:surface'):
    return {'type': 'minecraft:noise_threshold', 'noise': name, 'min_threshold': lo, 'max_threshold': hi}


NOT = lambda c: {'type': 'minecraft:not', 'invert': c}  # noqa: E731
STEEP = {'type': 'minecraft:steep'}
BANDS = {'type': 'minecraft:bandlands'}
BEDROCK = cond({'type': 'minecraft:vertical_gradient', 'random_name': 'minecraft:bedrock_floor',
                'true_at_and_below': {'above_bottom': 0}, 'false_at_and_above': {'above_bottom': 5}}, block('minecraft:bedrock'))
DEEPSLATE = cond({'type': 'minecraft:vertical_gradient', 'random_name': 'minecraft:deepslate',
                  'true_at_and_below': {'absolute': 0}, 'false_at_and_above': {'absolute': 8}}, block('minecraft:deepslate', {'axis': 'y'}))

SURFACE = {
    # sunken fields: grass and moss above the waterline, sand, gravel and mud below it
    'drowned': seq(BEDROCK,
                   cond(depth(), seq(cond(above_water(), seq(cond(noise(0.25, 9.0), block('minecraft:moss_block')),
                                                                block('minecraft:grass_block', {'snowy': 'false'}))),
                                     cond(noise(-9.0, -0.35), block('minecraft:gravel')),
                                     cond(noise(0.4, 9.0), block('minecraft:mud')),
                                     block('minecraft:sand'))),
                   cond(depth(add=True), seq(cond(above_water(), block('minecraft:dirt')), block('minecraft:sandstone'))),
                   DEEPSLATE),
    # snow over packed ice, ice cliffs, treacherous powder snow pockets, gravel under frozen water
    'pale': seq(BEDROCK,
                cond(depth(), seq(cond(NOT(above_water()), block('minecraft:gravel')),
                                  cond(STEEP, block('minecraft:packed_ice')),
                                  cond(noise(0.55, 9.0), block('minecraft:powder_snow')),
                                  block('minecraft:snow_block'))),
                cond(depth(add=True), seq(cond(STEEP, block('minecraft:packed_ice')), block('minecraft:snow_block'))),
                cond(depth(add=True, secondary=6), block('minecraft:packed_ice')),
                DEEPSLATE),
    # red sand on red sandstone, banded terracotta in every cliff and cutting
    'scarlet': seq(BEDROCK,
                   cond(depth(), seq(cond(STEEP, BANDS), block('minecraft:red_sand'))),
                   cond(depth(add=True), seq(cond(STEEP, BANDS), block('minecraft:red_sandstone'))),
                   cond(depth(add=True, secondary=30), BANDS),
                   DEEPSLATE),
}
ow = vload('ns_overworld.json')
for name, (time, light, sea) in DIMS.items():
    ns = copy.deepcopy(ow)
    ns['sea_level'] = sea
    ns['surface_rule'] = SURFACE[name]
    ns['ore_veins_enabled'] = name != 'scarlet'
    write(f'{D}/worldgen/noise_settings/{name}.json', ns)


# ---- biomes
def hexint(h):
    return int(h.lstrip('#'), 16)


def biome(name, precip, temp, down, colors, extra, spawners, carvers, features):
    steps = [[] for _ in range(11)]
    for step, items in features.items():
        steps[step] = items
    eff = {k: hexint(v) for k, v in colors.items()}
    eff.update(extra)
    sp = {'monster': [], 'creature': [], 'ambient': [], 'axolotls': [], 'underground_water_creature': [],
          'water_creature': [], 'water_ambient': [], 'misc': []}
    sp.update(spawners)
    write(f'{D}/worldgen/biome/{name}.json', {
        'has_precipitation': precip, 'temperature': temp, 'downfall': down, 'effects': eff,
        'spawners': sp, 'spawn_costs': {}, 'carvers': {'air': carvers}, 'features': steps})


def particle(kind, prob):
    return {'particle': {'options': {'type': kind}, 'probability': prob}}


def spawn(t, w, lo, hi):
    return {'type': t, 'weight': w, 'minCount': lo, 'maxCount': hi}


MOOD = {'mood_sound': {'sound': 'minecraft:ambient.cave', 'tick_delay': 6000, 'block_search_extent': 8, 'offset': 2.0}}
ORES = ['minecraft:ore_coal_upper', 'minecraft:ore_iron_upper', 'minecraft:ore_iron_middle', 'minecraft:ore_gold', 'minecraft:ore_diamond']
drowned_fx = dict(MOOD)
drowned_fx.update(particle('minecraft:underwater', 0.01))
drowned_fx['ambient_sound'] = 'minecraft:ambient.underwater.loop'
biome('drowned', True, 0.6, 0.9,
      {'sky_color': '#1C3D47', 'fog_color': '#1A4249', 'water_color': '#1E6F7A', 'water_fog_color': '#06232A',
       'grass_color': '#4F7A5A', 'foliage_color': '#3E6B4C'}, drowned_fx,
      {'monster': [spawn('minecraft:drowned', 100, 2, 4), spawn('aurelia:razorclaw', 35, 1, 2)],
       'water_creature': [spawn('minecraft:squid', 4, 1, 4)],
       'underground_water_creature': [spawn('minecraft:glow_squid', 10, 4, 6)],
       'water_ambient': [spawn('minecraft:tropical_fish', 25, 8, 8), spawn('minecraft:cod', 10, 3, 6)]},
      ['minecraft:cave', 'minecraft:cave_extra_underground'],
      {6: ORES + ['minecraft:disk_sand', 'minecraft:disk_clay', 'minecraft:disk_gravel', 'aurelia:ore_tidestone'],
       8: ['minecraft:spring_water'],
       9: ['minecraft:trees_mangrove', 'minecraft:warm_ocean_vegetation', 'minecraft:kelp_warm', 'minecraft:seagrass_warm',
           'minecraft:sea_pickle', 'minecraft:glow_lichen']})
pale_fx = dict(MOOD)
pale_fx.update(particle('minecraft:snowflake', 0.008))
biome('pale', True, -0.7, 0.5,
      {'sky_color': '#C9D3DA', 'fog_color': '#E4E9EE', 'water_color': '#5A7FAF', 'water_fog_color': '#22334A',
       'grass_color': '#C5D3C9', 'foliage_color': '#8FA29A'}, pale_fx,
      {'monster': [spawn('minecraft:stray', 60, 2, 3), spawn('aurelia:rimefang', 40, 1, 3)]},
      ['minecraft:cave', 'minecraft:cave_extra_underground', 'minecraft:canyon'],
      {6: ORES + ['aurelia:ore_rime'], 8: ['minecraft:spring_water'],
       9: ['minecraft:ice_spike', 'minecraft:ice_patch', 'minecraft:trees_snowy', 'minecraft:blue_ice'],
       10: ['minecraft:freeze_top_layer']})
scarlet_fx = dict(MOOD)
scarlet_fx.update(particle('minecraft:white_ash', 0.012))
biome('scarlet', False, 2.0, 0.0,
      {'sky_color': '#F2A06C', 'fog_color': '#E8B48A', 'water_color': '#B04A2A', 'water_fog_color': '#4A1A10',
       'grass_color': '#A0603A', 'foliage_color': '#8A5A30'}, scarlet_fx,
      {'monster': [spawn('minecraft:husk', 60, 2, 3), spawn('aurelia:glasswing_scarab', 40, 1, 2)]},
      ['minecraft:cave', 'minecraft:cave_extra_underground', 'minecraft:canyon'],
      {6: ORES + ['aurelia:ore_sunglass'], 8: ['minecraft:spring_lava'],
       9: ['minecraft:patch_dead_bush_badlands', 'minecraft:patch_cactus_desert']})

# ---- ores: copies of the emerald ore with the outer-realm ores, many more veins
for ore, size, count, lo, hi in [('tidestone', 6, 16, -16, 110), ('rime', 6, 14, -16, 200), ('sunglass', 7, 16, -16, 220)]:
    cf = vload('cf_ore_emerald.json')
    cf['config']['size'] = size
    cf['config']['targets'][0]['state'] = {'Name': f'aurelia:{ore}_ore'}
    cf['config']['targets'][1]['state'] = {'Name': f'aurelia:{ore}_ore'}
    write(f'{D}/worldgen/configured_feature/ore_{ore}.json', cf)
    pf = vload('pf_ore_emerald.json')
    pf['feature'] = f'aurelia:ore_{ore}'
    pf['placement'][0]['count'] = count
    pf['placement'][2]['height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}
    write(f'{D}/worldgen/placed_feature/ore_{ore}.json', pf)


# =========================================================================================== textures
def noise_img(base, var, seed, size=16):
    r = random.Random(seed)
    img = Image.new('RGBA', (size, size))
    px = img.load()
    for x in range(size):
        for y in range(size):
            v = r.randint(-var, var)
            px[x, y] = tuple(max(0, min(255, c + v)) for c in base) + (255,)
    return img


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


MAT = {   # ore name: (gem colour, dark colour, host rock, material item)
    'tidestone': ((70, 240, 210), (20, 110, 110), (96, 112, 110), 'tidestone_shard'),
    'rime': ((190, 235, 255), (90, 140, 200), (210, 220, 228), 'rime_crystal'),
    'sunglass': ((255, 80, 60), (150, 20, 30), (178, 92, 44), 'sunglass_shard'),
}
for i, (name, (gem, dark, rock, item)) in enumerate(MAT.items()):
    img = noise_img(rock, 9, 700 + i)
    r = random.Random(800 + i)
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x, y = r.randint(1, 12), r.randint(1, 12)
        d.rectangle([x, y, x + 2, y + 1], fill=gem + (255,))
        d.point([(x, y + 2), (x + 3, y)], fill=dark + (255,))
        d.point([(x + 1, y)], fill=(255, 255, 255, 255))
    save(img, f'{BLK}/{name}_ore.png')
    img = noise_img(gem, 12, 900 + i)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 15], outline=dark + (255,))
    d.rectangle([3, 3, 12, 12], outline=tuple(min(255, c + 50) for c in gem) + (255,))
    d.line([(4, 11), (11, 4)], fill=(255, 255, 255, 255))
    save(img, f'{BLK}/{name}_block.png')
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if name == 'rime':
        d.polygon([(8, 0), (11, 5), (10, 15), (6, 15), (5, 5)], fill=gem + (255,), outline=dark + (255,))
        d.line([(8, 2), (8, 13)], fill=(255, 255, 255, 255))
    elif name == 'tidestone':
        d.polygon([(3, 9), (7, 2), (13, 4), (12, 11), (6, 14)], fill=gem + (255,), outline=dark + (255,))
        d.line([(6, 10), (10, 5)], fill=(230, 255, 250, 255))
    else:
        d.polygon([(8, 1), (13, 7), (8, 15), (3, 7)], fill=gem + (255,), outline=dark + (255,))
        d.line([(8, 3), (6, 8)], fill=(255, 220, 200, 255))
    save(img, f'{ITEM}/{item}.png')

# relics and the Ascendant Crown
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.ellipse([3, 3, 12, 12], fill=(220, 236, 236, 255), outline=(40, 120, 130, 255))
d.ellipse([5, 5, 9, 9], fill=(120, 255, 230, 255)); d.point([(6, 6)], fill=(255, 255, 255, 255))
save(img, f'{ITEM}/leviathan_pearl.png')
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.polygon([(8, 1), (12, 9), (10, 14), (6, 14), (4, 9)], fill=(200, 238, 255, 255), outline=(100, 150, 210, 255))
d.line([(7, 5), (6, 11)], fill=(255, 255, 255, 255))
save(img, f'{ITEM}/frozen_tear.png')
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.rectangle([3, 1, 12, 2], fill=(200, 150, 50, 255)); d.rectangle([3, 13, 12, 14], fill=(200, 150, 50, 255))
d.polygon([(4, 3), (11, 3), (8, 7), (8, 8), (11, 12), (4, 12), (7, 8), (7, 7)], fill=(170, 30, 40, 255), outline=(110, 10, 20, 255))
d.rectangle([5, 10, 10, 12], fill=(255, 190, 90, 255)); d.point([(7, 8), (8, 9)], fill=(255, 220, 140, 255))
save(img, f'{ITEM}/reapers_hourglass.png')
crown = Image.open(f'{ITEM}/crown_of_aurelia.png').convert('RGBA')
d = ImageDraw.Draw(crown)
for (x, y), c in zip([(4, 7), (8, 6), (11, 7)], [(120, 255, 230), (220, 245, 255), (255, 80, 60)]):
    d.point([(x, y), (x, y + 1)], fill=c + (255,))
save(crown, f'{ITEM}/ascendant_crown.png')
for layer in (1, 2):
    a = Image.open(f'{A}/textures/models/armor/aurelian_layer_{layer}.png').convert('RGBA')
    px = a.load()
    for x in range(a.width):
        for y in range(a.height):
            r_, g_, b_, al = px[x, y]
            if al:
                px[x, y] = (min(255, int(r_ * 0.9 + 30)), min(255, int(g_ * 0.85 + 40)), min(255, int(b_ * 0.8 + 70)), al)
    save(a, f'{A}/textures/models/armor/ascendant_layer_{layer}.png')

# ritual blocks
img = noise_img((40, 70, 72), 6, 11); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(20, 40, 44, 255))
save(img, f'{BLK}/tide_bell_frame.png')
for rung in (False, True):
    img = noise_img((210, 170, 70) if not rung else (120, 255, 220), 10, 12 + rung); d = ImageDraw.Draw(img)
    d.line([(0, 4), (15, 4)], fill=(120, 90, 40, 255) if not rung else (230, 255, 250, 255))
    d.line([(0, 11), (15, 11)], fill=(120, 90, 40, 255) if not rung else (230, 255, 250, 255))
    for x in (3, 8, 13):
        d.point([(x, 7)], fill=(90, 220, 200, 255))
    save(img, f'{BLK}/tide_bell{"_rung" if rung else ""}.png')
for filled in (False, True):
    side = noise_img((214, 220, 226), 6, 20 + filled)
    save(side, f'{BLK}/hush_stone_{"on" if filled else "off"}_side.png')
    top = noise_img((214, 220, 226), 6, 22 + filled); d = ImageDraw.Draw(top)
    col = (150, 230, 255) if filled else (120, 132, 146)
    d.ellipse([2, 2, 13, 13], outline=col + (255,)); d.line([(5, 8), (10, 8)], fill=col + (255,))
    d.line([(5, 6), (6, 6)], fill=col + (255,)); d.line([(9, 6), (10, 6)], fill=col + (255,))
    save(top, f'{BLK}/hush_stone_{"on" if filled else "off"}_top.png')
    lens = noise_img((150, 24, 34) if not filled else (255, 110, 70), 12, 24 + filled); d = ImageDraw.Draw(lens)
    d.rectangle([0, 0, 15, 15], outline=(200, 150, 50, 255)); d.rectangle([1, 1, 14, 14], outline=(140, 96, 30, 255))
    d.ellipse([4, 4, 11, 11], outline=(255, 200, 160, 255) if filled else (220, 80, 80, 255))
    save(lens, f'{BLK}/sun_lens_{"on" if filled else "off"}.png')
sw = noise_img((180, 92, 44), 8, 30)
save(sw, f'{BLK}/sunwell_side.png')
top = noise_img((200, 150, 50), 8, 31); d = ImageDraw.Draw(top); d.ellipse([3, 3, 12, 12], outline=(255, 230, 120, 255))
save(top, f'{BLK}/sunwell_top.png')
front = noise_img((180, 92, 44), 8, 32); d = ImageDraw.Draw(front)
d.ellipse([3, 3, 12, 12], fill=(255, 214, 90, 255), outline=(200, 150, 50, 255)); d.ellipse([6, 6, 9, 9], fill=(255, 250, 210, 255))
for (a_, b_) in [((7, 0), (8, 2)), ((7, 13), (8, 15)), ((0, 7), (2, 8)), ((13, 7), (15, 8))]:
    d.rectangle([a_, b_], fill=(255, 230, 120, 255))
save(front, f'{BLK}/sunwell_front.png')
mir = noise_img((235, 240, 245), 10, 33); d = ImageDraw.Draw(mir)
d.rectangle([0, 0, 15, 15], outline=(200, 150, 50, 255)); d.line([(2, 13), (13, 2)], fill=(255, 255, 255, 255))
save(mir, f'{BLK}/sun_mirror_glass.png')
save(noise_img((200, 150, 50), 8, 34), f'{BLK}/sun_mirror_base.png')

# seals and traps
img = noise_img((226, 86, 110), 12, 40); d = ImageDraw.Draw(img)
for pts in [[(0, 15), (5, 8), (4, 2)], [(5, 8), (10, 5), (12, 0)], [(10, 5), (15, 9)]]:
    d.line(pts, fill=(250, 150, 170, 255))
for (x, y) in [(3, 12), (11, 11), (8, 3)]:
    d.point((x, y), fill=(70, 255, 214, 255))
save(img, f'{BLK}/coral_seal.png')
img = noise_img((170, 214, 240), 10, 41); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(230, 245, 255, 255))
for k in (4, 8, 12):
    d.line([(k, 0), (k - 3, 15)], fill=(214, 240, 255, 255))
save(img, f'{BLK}/rime_seal.png')
img = noise_img((200, 110, 50), 8, 42); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(150, 70, 30, 255)); d.ellipse([4, 4, 11, 11], outline=(255, 214, 90, 255))
d.point([(7, 7), (8, 8), (7, 8), (8, 7)], fill=(255, 250, 200, 255))
save(img, f'{BLK}/sun_seal.png')


def trap(name, side_rgb, top_fn, seed):
    save(noise_img(side_rgb, 8, seed), f'{BLK}/{name}_side.png')
    img = noise_img(side_rgb, 8, seed + 1)
    top_fn(ImageDraw.Draw(img))
    save(img, f'{BLK}/{name}_top.png')


trap('brine_grate', (60, 70, 72), lambda d: ([d.line([(x, 1), (x, 14)], fill=(20, 26, 28, 255)) for x in (3, 6, 9, 12)],
                                            d.rectangle([0, 0, 15, 15], outline=(30, 110, 110, 255))), 50)
trap('frost_rune', (196, 214, 228), lambda d: (d.line([(8, 1), (8, 14)], fill=(120, 220, 255, 255)), d.line([(1, 8), (14, 8)], fill=(120, 220, 255, 255)),
                                              d.line([(3, 3), (12, 12)], fill=(170, 238, 255, 255)), d.line([(12, 3), (3, 12)], fill=(170, 238, 255, 255))), 60)
trap('sunflare_plate', (200, 150, 50), lambda d: (d.rectangle([2, 2, 13, 13], fill=(240, 240, 250, 255), outline=(150, 100, 30, 255)),
                                                 d.line([(4, 11), (11, 4)], fill=(255, 255, 255, 255))), 70)

# waygates for the new realms
WAYGATE = {'drowned': ((40, 200, 190), (16, 60, 66)), 'pale': ((220, 240, 255), (120, 130, 146)), 'scarlet': ((255, 90, 60), (110, 40, 30))}
for realm, (glow, frame) in WAYGATE.items():
    for on in (False, True):
        sfx = 'on' if on else 'off'
        side = noise_img(frame, 8, sum(map(ord, realm)) + on)
        d = ImageDraw.Draw(side)
        d.rectangle([3, 1, 12, 14], fill=(glow if on else tuple(c // 3 for c in glow)) + (255,), outline=(200, 160, 70, 255))
        if on:
            d.line([(8, 2), (8, 13)], fill=(255, 255, 255, 255))
        save(side, f'{BLK}/waygate_{realm}_{sfx}_side.png')
        top = noise_img(frame, 8, sum(map(ord, realm)) + 50 + on)
        d = ImageDraw.Draw(top)
        d.ellipse([3, 3, 12, 12], outline=(glow if on else (90, 90, 90)) + (255,))
        save(top, f'{BLK}/waygate_{realm}_{sfx}_top.png')


# =========================================================================================== models and blockstates
def bs(name, variants):
    write(f'{A}/blockstates/{name}.json', {'variants': variants})


def model(name, obj):
    write(f'{A}/models/block/{name}.json', obj)


def item_model(name, obj):
    write(f'{A}/models/item/{name}.json', obj)


CUBE_ALL = ['coral_seal', 'rime_seal', 'sun_seal', 'tidestone_ore', 'rime_ore', 'sunglass_ore', 'tidestone_block', 'rime_block', 'sunglass_block']
for b in CUBE_ALL:
    bs(b, {'': {'model': f'aurelia:block/{b}'}})
    model(b, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{b}'}})
    item_model(b, {'parent': f'aurelia:block/{b}'})
for b in ['brine_grate', 'frost_rune', 'sunflare_plate']:
    bs(b, {'': {'model': f'aurelia:block/{b}'}})
    model(b, {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/{b}_top', 'side': f'aurelia:block/{b}_side'}})
    item_model(b, {'parent': f'aurelia:block/{b}'})
# hush stone and sun lens
bs('hush_stone', {'filled=false': {'model': 'aurelia:block/hush_stone_off'}, 'filled=true': {'model': 'aurelia:block/hush_stone_on'}})
for s in ('off', 'on'):
    model(f'hush_stone_{s}', {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/hush_stone_{s}_top', 'side': f'aurelia:block/hush_stone_{s}_side'}})
    model(f'sun_lens_{s}', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/sun_lens_{s}'}})
item_model('hush_stone', {'parent': 'aurelia:block/hush_stone_off'})
bs('sun_lens', {'filled=false': {'model': 'aurelia:block/sun_lens_off'}, 'filled=true': {'model': 'aurelia:block/sun_lens_on'}})
item_model('sun_lens', {'parent': 'aurelia:block/sun_lens_off'})
# sunwell: orientable
model('sunwell', {'parent': 'minecraft:block/orientable', 'textures': {'front': 'aurelia:block/sunwell_front', 'side': 'aurelia:block/sunwell_side', 'top': 'aurelia:block/sunwell_top'}})
bs('sunwell', {f'facing={f}': ({'model': 'aurelia:block/sunwell', 'y': y} if y else {'model': 'aurelia:block/sunwell'})
               for f, y in [('north', 0), ('east', 90), ('south', 180), ('west', 270)]})
item_model('sunwell', {'parent': 'aurelia:block/sunwell'})
# sun mirror: a gold base and a pane turned 45 degrees ("/" seen from above with north up)
model('sun_mirror', {'parent': 'minecraft:block/block', 'textures': {'particle': 'aurelia:block/sun_mirror_glass', 'glass': 'aurelia:block/sun_mirror_glass',
                                                                    'base': 'aurelia:block/sun_mirror_base'},
                     'elements': [
                         {'from': [1, 0, 1], 'to': [15, 2, 15], 'faces': {f: {'texture': '#base'} for f in ('down', 'up', 'north', 'south', 'east', 'west')}},
                         {'from': [-2.5, 2, 7.5], 'to': [18.5, 16, 8.5], 'rotation': {'origin': [8, 8, 8], 'axis': 'y', 'angle': 45, 'rescale': False},
                          'faces': {f: {'texture': '#glass'} for f in ('down', 'up', 'north', 'south', 'east', 'west')}}]})
bs('sun_mirror', {'slash=true': {'model': 'aurelia:block/sun_mirror'}, 'slash=false': {'model': 'aurelia:block/sun_mirror', 'y': 90}})
item_model('sun_mirror', {'parent': 'aurelia:block/sun_mirror'})
# tide bell: a frame with a hanging bell
for rung in (False, True):
    tex = 'aurelia:block/tide_bell_rung' if rung else 'aurelia:block/tide_bell'
    allf = lambda t: {f: {'texture': t} for f in ('down', 'up', 'north', 'south', 'east', 'west')}  # noqa: E731
    model('tide_bell' + ('_rung' if rung else ''), {'parent': 'minecraft:block/block', 'textures': {'particle': tex, 'bell': tex, 'frame': 'aurelia:block/tide_bell_frame'},
          'elements': [{'from': [2, 0, 6], 'to': [4, 16, 10], 'faces': allf('#frame')},
                       {'from': [12, 0, 6], 'to': [14, 16, 10], 'faces': allf('#frame')},
                       {'from': [2, 13, 7], 'to': [14, 15, 9], 'faces': allf('#frame')},
                       {'from': [5, 5, 5], 'to': [11, 12, 11], 'faces': allf('#bell')},
                       {'from': [4, 3, 4], 'to': [12, 5, 12], 'faces': allf('#bell')},
                       {'from': [7, 12, 7], 'to': [9, 13, 9], 'faces': allf('#frame')}]})
bs('tide_bell', {'rung=false': {'model': 'aurelia:block/tide_bell'}, 'rung=true': {'model': 'aurelia:block/tide_bell_rung'}})
item_model('tide_bell', {'parent': 'aurelia:block/tide_bell'})
# waygate: every realm, dormant and awake
wg = {}
for realm in ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet']:
    for on in (False, True):
        sfx = 'on' if on else 'off'
        wg[f'realm={realm},active={str(on).lower()}'] = {'model': f'aurelia:block/waygate_{realm}_{sfx}'}
        model(f'waygate_{realm}_{sfx}', {'parent': 'minecraft:block/cube_column', 'textures': {
            'end': f'aurelia:block/waygate_{realm}_{sfx}_top', 'side': f'aurelia:block/waygate_{realm}_{sfx}_side'}})
bs('waygate', wg)
for it in ['tidestone_shard', 'rime_crystal', 'sunglass_shard', 'leviathan_pearl', 'frozen_tear', 'reapers_hourglass', 'ascendant_crown']:
    item_model(it, {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'aurelia:item/{it}'}})
EGGS = ['vorath', 'white_silence', 'kharzul', 'pale_mirage', 'coralclad_juggernaut', 'tidecaller', 'razorclaw', 'rimeguard', 'hushwraith',
        'rimefang', 'sandglass_sentinel', 'sunseer', 'glasswing_scarab']
for e in EGGS:
    item_model(f'{e}_spawn_egg', {'parent': 'minecraft:item/template_spawn_egg'})

# =========================================================================================== loot, tags, recipes
for name, (gem, dark, rock, item) in MAT.items():
    lt = vload('lt_emerald_ore.json')
    lt.pop('random_sequence', None)
    ch = lt['pools'][0]['entries'][0]['children']
    ch[0]['name'] = f'aurelia:{name}_ore'
    ch[1]['name'] = f'aurelia:{item}'
    ch[1]['functions'].insert(0, {'function': 'minecraft:set_count', 'count': {'min': 1, 'max': 3}})
    write(f'{D}/loot_tables/blocks/{name}_ore.json', lt)
    write(f'{D}/recipes/{name}_block.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['###', '###', '###'],
                                            'key': {'#': {'item': f'aurelia:{item}'}}, 'result': {'item': f'aurelia:{name}_block', 'count': 1}})
    write(f'{D}/recipes/{item}_from_block.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                                 'ingredients': [{'item': f'aurelia:{name}_block'}], 'result': {'item': f'aurelia:{item}', 'count': 9}})
for b in ['tidestone_block', 'rime_block', 'sunglass_block', 'brine_grate', 'frost_rune', 'sunflare_plate', 'tide_bell', 'hush_stone',
          'sunwell', 'sun_mirror', 'sun_lens']:
    write(f'{D}/loot_tables/blocks/{b}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
          'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{b}'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})
write(f'{D}/recipes/ascendant_crown.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
      'ingredients': [{'item': f'aurelia:{i}'} for i in ['crown_of_aurelia', 'leviathan_pearl', 'frozen_tear', 'reapers_hourglass',
                                                         'tidestone_block', 'rime_block', 'sunglass_block']],
      'result': {'item': 'aurelia:ascendant_crown', 'count': 1}})
for tag, extra in [('mineable/pickaxe', ['aurelia:tidestone_ore', 'aurelia:rime_ore', 'aurelia:sunglass_ore', 'aurelia:tidestone_block',
                                         'aurelia:rime_block', 'aurelia:sunglass_block', 'aurelia:brine_grate', 'aurelia:frost_rune', 'aurelia:sunflare_plate']),
                   ('needs_diamond_tool', ['aurelia:tidestone_ore', 'aurelia:rime_ore', 'aurelia:sunglass_ore', 'aurelia:tidestone_block',
                                           'aurelia:rime_block', 'aurelia:sunglass_block'])]:
    p = f'{ROOT}/data/minecraft/tags/blocks/{tag}.json'
    j = json.load(open(p)) if os.path.exists(p) else {'replace': False, 'values': []}
    j['values'] += [v for v in extra if v not in j['values']]
    write(p, j)


def entry(item, weight, lo=None, hi=None):
    e = {'type': 'minecraft:item', 'name': item, 'weight': weight}
    if lo is not None:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]
    return e


def mob_loot(name, pools):
    write(f'{D}/loot_tables/entities/{name}.json', {'type': 'minecraft:entity', 'pools': pools})


def pool(entries, rolls=1, chance=None):
    p = {'rolls': rolls, 'entries': entries}
    if chance is not None:
        p['conditions'] = [{'condition': 'minecraft:killed_by_player'}, {'condition': 'minecraft:random_chance', 'chance': chance}]
    return p


GUARD_LOOT = {
    'coralclad_juggernaut': ('tidestone_shard', 2, 4, [entry('minecraft:prismarine_shard', 3, 2, 5), entry('minecraft:nautilus_shell', 1, 1, 1)]),
    'tidecaller': ('tidestone_shard', 1, 3, [entry('minecraft:prismarine_crystals', 3, 2, 4), entry('minecraft:heart_of_the_sea', 1, 1, 1)]),
    'razorclaw': ('tidestone_shard', 0, 2, [entry('minecraft:prismarine_shard', 3, 1, 3)]),
    'rimeguard': ('rime_crystal', 2, 4, [entry('minecraft:blue_ice', 3, 1, 3), entry('minecraft:diamond', 1, 1, 1)]),
    'hushwraith': ('rime_crystal', 1, 3, [entry('minecraft:echo_shard', 2, 1, 1), entry('minecraft:phantom_membrane', 3, 1, 2)]),
    'rimefang': ('rime_crystal', 0, 2, [entry('minecraft:bone', 3, 1, 3)]),
    'sandglass_sentinel': ('sunglass_shard', 2, 4, [entry('minecraft:gold_ingot', 3, 2, 5), entry('minecraft:diamond', 1, 1, 1)]),
    'sunseer': ('sunglass_shard', 1, 3, [entry('minecraft:blaze_powder', 3, 1, 3), entry('minecraft:glowstone_dust', 2, 2, 5)]),
    'glasswing_scarab': ('sunglass_shard', 0, 2, [entry('minecraft:gold_nugget', 3, 2, 6)]),
}
for mob, (mat, lo, hi, extra) in GUARD_LOOT.items():
    mob_loot(mob, [pool([entry(f'aurelia:{mat}', 1, lo, hi)]), pool(extra, chance=0.5),
                   pool([entry('minecraft:emerald', 1, 1, 3)], chance=0.35)])

common = [entry('minecraft:diamond', 6, 1, 3), entry('minecraft:emerald', 10, 2, 6), entry('minecraft:golden_apple', 4),
          entry('minecraft:experience_bottle', 8, 4, 10), entry('minecraft:ender_pearl', 5, 1, 3), entry('minecraft:enchanted_golden_apple', 1),
          entry('minecraft:netherite_scrap', 2, 1, 2)]
for table, mat, extra in [('tidewrack_cache', 'tidestone_shard', [entry('minecraft:heart_of_the_sea', 2, 1, 1), entry('minecraft:trident', 1)]),
                          ('rimefast_cache', 'rime_crystal', [entry('minecraft:blue_ice', 5, 4, 10), entry('minecraft:leather_chestplate', 3)]),
                          ('sunscar_cache', 'sunglass_shard', [entry('minecraft:gold_block', 2, 1, 2), entry('minecraft:totem_of_undying', 1)]),
                          ('drowned_outpost', 'tidestone_shard', [entry('minecraft:nautilus_shell', 4, 1, 2)]),
                          ('pale_outpost', 'rime_crystal', [entry('minecraft:leather_boots', 3), entry('minecraft:blue_ice', 4, 2, 6)]),
                          ('scarlet_outpost', 'sunglass_shard', [entry('minecraft:gold_ingot', 5, 2, 6)])]:
    write(f'{D}/loot_tables/chests/{table}.json', {'type': 'minecraft:chest', 'pools': [
        {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{mat}',
                                                    'functions': [{'function': 'minecraft:set_count', 'count': {'min': 4, 'max': 9}}]}]},
        {'rolls': {'min': 3, 'max': 5}, 'bonus_rolls': 0, 'entries': common + extra}]})

# =========================================================================================== structures
CITADELS = {
    'tidewrack_citadel': dict(biomes=['minecraft:ocean', 'minecraft:lukewarm_ocean', 'minecraft:warm_ocean', 'minecraft:cold_ocean'],
                              step='surface_structures', start={'absolute': 40}, project=None, adapt='none', mob='aurelia:razorclaw',
                              spacing=34, separation=12, salt=71920504, excl=None),
    'rimefast_citadel': dict(biomes=['minecraft:snowy_plains', 'minecraft:snowy_taiga', 'minecraft:ice_spikes', 'minecraft:snowy_slopes', 'minecraft:grove'],
                             step='surface_structures', start={'absolute': -12}, project='WORLD_SURFACE_WG', adapt='beard_thin', mob='aurelia:rimefang',
                             spacing=30, separation=10, salt=71920505, excl=None),
    'sunscar_citadel': dict(biomes=['minecraft:desert', '#minecraft:is_badlands'],
                            step='surface_structures', start={'absolute': -8}, project='WORLD_SURFACE_WG', adapt='beard_thin', mob='aurelia:glasswing_scarab',
                            spacing=32, separation=11, salt=71920506, excl=('ashen_citadel', 5)),
}


def structure(name, tag, start, project, adapt, step, spawns, variants, spacing, sep, salt, excl, biome_values=None):
    if biome_values is not None:
        write(f'{D}/tags/worldgen/biome/has_structure/{tag}.json', {'replace': False, 'values': biome_values})
    s = {'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/{tag}', 'step': step, 'spawn_overrides': spawns,
         'terrain_adaptation': adapt, 'start_pool': f'aurelia:{name}/start', 'size': 1, 'start_height': start,
         'max_distance_from_center': 80, 'use_expansion_hack': False}
    if project:
        s['project_start_to_heightmap'] = project
    write(f'{D}/worldgen/structure/{name}.json', s)
    write(f'{D}/worldgen/template_pool/{name}/start.json', {'fallback': 'minecraft:empty', 'elements': [
        {'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:{v}',
                                  'processors': {'processors': []}, 'projection': 'rigid'}} for v in variants]})
    placement = {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}
    if excl:
        placement['exclusion_zone'] = {'other_set': f'aurelia:{excl[0]}', 'chunk_count': excl[1]}
    write(f'{D}/worldgen/structure_set/{name}.json', {'structures': [{'structure': f'aurelia:{name}', 'weight': 1}], 'placement': placement})


for name, c in CITADELS.items():
    structure(name, name, c['start'], c['project'], c['adapt'], c['step'],
              {'monster': {'bounding_box': 'full', 'spawns': [spawn(c['mob'], 1, 1, 1)]}},
              [name], c['spacing'], c['separation'], c['salt'], c['excl'], c['biomes'])


def uniform(lo, hi):
    return {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}


REALM_GROUPS = [
    # name, variants, decor tag, start height, projection, spacing, separation, salt, exclusion
    ('drowned_spires', ['drowned_spire_0', 'drowned_spire_1', 'drowned_spire_2'], 'drowned_decor', {'absolute': -2}, 'OCEAN_FLOOR_WG', 6, 2, 91000201, None),
    ('drowned_wrecks', ['drowned_wreck_0', 'drowned_wreck_1'], 'drowned_decor', {'absolute': 89}, None, 9, 4, 91000202, ('drowned_spires', 1)),
    ('drowned_bones', ['drowned_bones_0', 'drowned_bones_1'], 'drowned_decor', {'absolute': -3}, 'OCEAN_FLOOR_WG', 8, 3, 91000203, ('drowned_wrecks', 1)),
    ('drowned_outposts', ['drowned_outpost_0', 'drowned_outpost_1'], 'drowned_decor', {'absolute': 92}, None, 10, 4, 91000204, ('drowned_wrecks', 2)),
    ('pale_colossi', ['pale_colossus_0', 'pale_colossus_1'], 'pale_decor', {'absolute': -5}, 'WORLD_SURFACE_WG', 9, 4, 91000205, None),
    ('pale_spires', ['pale_spire_0', 'pale_spire_1', 'pale_spire_2'], 'pale_decor', {'absolute': -3}, 'WORLD_SURFACE_WG', 6, 2, 91000206, ('pale_colossi', 1)),
    ('pale_outposts', ['pale_outpost_0', 'pale_outpost_1'], 'pale_decor', {'absolute': -2}, 'WORLD_SURFACE_WG', 10, 4, 91000207, ('pale_colossi', 2)),
    ('scarlet_monoliths', ['scarlet_monolith_0', 'scarlet_monolith_1', 'scarlet_monolith_2'], 'scarlet_decor', {'absolute': -3}, 'WORLD_SURFACE_WG', 6, 2, 91000208, None),
    ('scarlet_bones', ['scarlet_bones_0', 'scarlet_bones_1'], 'scarlet_decor', {'absolute': -6}, 'WORLD_SURFACE_WG', 9, 4, 91000209, ('scarlet_monoliths', 1)),
    ('scarlet_outposts', ['scarlet_outpost_0', 'scarlet_outpost_1'], 'scarlet_decor', {'absolute': -2}, 'WORLD_SURFACE_WG', 10, 4, 91000210, ('scarlet_bones', 2)),
]
for tag, biome_id in [('drowned_decor', 'aurelia:drowned'), ('pale_decor', 'aurelia:pale'), ('scarlet_decor', 'aurelia:scarlet')]:
    write(f'{D}/tags/worldgen/biome/has_structure/{tag}.json', {'replace': False, 'values': [biome_id]})
for name, variants, tag, start, project, spacing, sep, salt, excl in REALM_GROUPS:
    structure(name, tag, start, project, 'beard_thin' if 'outpost' in name and 'drowned' not in name else 'none',
              'surface_structures', {}, variants, spacing, sep, salt, excl)

# =========================================================================================== names
lp = f'{A}/lang/en_us.json'
lang = json.load(open(lp, encoding='utf-8'))
lang.update({
    'itemGroup.aurelia': 'Aurelia: The Shattered Crown',
    'entity.aurelia.vorath': 'Vorath, the Tide Devourer',
    'entity.aurelia.white_silence': 'The White Silence',
    'entity.aurelia.kharzul': 'Kharzul, the Glass Reaper',
    'entity.aurelia.pale_mirage': 'Pale Mirage',
    'entity.aurelia.coralclad_juggernaut': 'Coralclad Juggernaut',
    'entity.aurelia.tidecaller': 'Tidecaller',
    'entity.aurelia.razorclaw': 'Razorclaw',
    'entity.aurelia.rimeguard': 'Rimeguard',
    'entity.aurelia.hushwraith': 'Hushwraith',
    'entity.aurelia.rimefang': 'Rimefang',
    'entity.aurelia.sandglass_sentinel': 'Sandglass Sentinel',
    'entity.aurelia.sunseer': 'Sunseer',
    'entity.aurelia.glasswing_scarab': 'Glasswing Scarab',
    'block.aurelia.tide_bell': 'Tide Bell',
    'block.aurelia.hush_stone': 'Hush Stone',
    'block.aurelia.sunwell': 'Sunwell',
    'block.aurelia.sun_mirror': 'Sun Mirror',
    'block.aurelia.sun_lens': 'Sunglass Lens',
    'block.aurelia.coral_seal': 'Coral Seal',
    'block.aurelia.rime_seal': 'Rime Seal',
    'block.aurelia.sun_seal': 'Sun Seal',
    'block.aurelia.brine_grate': 'Brine Grate',
    'block.aurelia.frost_rune': 'Frost Rune',
    'block.aurelia.sunflare_plate': 'Sunflare Plate',
    'block.aurelia.tidestone_ore': 'Tidestone Ore',
    'block.aurelia.rime_ore': 'Rime Ore',
    'block.aurelia.sunglass_ore': 'Sunglass Ore',
    'block.aurelia.tidestone_block': 'Block of Tidestone',
    'block.aurelia.rime_block': 'Block of Rime',
    'block.aurelia.sunglass_block': 'Block of Sunglass',
    'item.aurelia.tidestone_shard': 'Tidestone Shard',
    'item.aurelia.rime_crystal': 'Rime Crystal',
    'item.aurelia.sunglass_shard': 'Sunglass Shard',
    'item.aurelia.tidestone_shard.lore': 'From the drowned rock of the Expanse. It is always damp.',
    'item.aurelia.rime_crystal.lore': 'Dug from the Pale Wastes. It never melts and never makes a sound.',
    'item.aurelia.sunglass_shard.lore': 'Glass the Scarlet Sun made out of the desert. Hot on one side.',
    'item.aurelia.leviathan_pearl': "Leviathan's Pearl",
    'item.aurelia.frozen_tear': 'Frozen Tear',
    'item.aurelia.reapers_hourglass': "Reaper's Hourglass",
    'item.aurelia.leviathan_pearl.lore': 'Taken from the deep. Hold it to your ear and you hear a heartbeat.',
    'item.aurelia.frozen_tear.lore': 'Someone cried, once, where nobody could hear.',
    'item.aurelia.reapers_hourglass.lore': 'The sand inside has stopped. It is waiting for permission.',
    'item.aurelia.ascendant_crown': 'Ascendant Crown',
    'structure.aurelia.tidewrack_citadel': 'Tidewrack Citadel',
    'structure.aurelia.rimefast_citadel': 'Rimefast Citadel',
    'structure.aurelia.sunscar_citadel': 'Sunscar Citadel',
})
for e in EGGS:
    lang[f'item.aurelia.{e}_spawn_egg'] = lang[f'entity.aurelia.{e}'].split(',')[0].replace('The ', '') + ' Spawn Egg'
json.dump(lang, open(lp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('act two data and assets written')
