"""Act three data and assets: the Clockwork Rift and the Mycelial Deep (dimensions, biomes, surface rules), clock and valve
block assets, items, loot, recipes, tags, structure definitions, names. Templates come from gen_act3_citadels.py and gen_act3_realms.py."""
import copy
import json
import math
import os
import random

from PIL import Image, ImageDraw

import paths

ROOT = paths.RES
A = f'{ROOT}/assets/aurelia'
D = f'{ROOT}/data/aurelia'
BLK, ITEM = f'{A}/textures/block', f'{A}/textures/item'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def noise_img(base, var, seed, size=16):
    r = random.Random(seed)
    img = Image.new('RGBA', (size, size))
    px = img.load()
    for x in range(size):
        for y in range(size):
            v = r.randint(-var, var)
            px[x, y] = tuple(max(0, min(255, c + v)) for c in base) + (255,)
    return img


# =========================================================================================== dimensions
write(f'{D}/dimension_type/clockwork.json', {
    'ultrawarm': False, 'natural': False, 'coordinate_scale': 1.0, 'has_skylight': True, 'has_ceiling': False, 'ambient_light': 0.15,
    'piglin_safe': False, 'bed_works': False, 'respawn_anchor_works': False, 'has_raids': False, 'logical_height': 256, 'min_y': 0, 'height': 256,
    'infiniburn': '#minecraft:infiniburn_end', 'effects': 'minecraft:the_end',
    'monster_spawn_light_level': {'type': 'minecraft:uniform', 'value': {'min_inclusive': 0, 'max_inclusive': 7}},
    'monster_spawn_block_light_limit': 0, 'fixed_time': 18000})
hollow_type = json.load(open(f'{D}/dimension_type/hollow.json'))
myc_type = dict(hollow_type)
myc_type.update({'ambient_light': 0.2, 'fixed_time': 18000, 'effects': 'minecraft:overworld', 'infiniburn': '#minecraft:infiniburn_overworld'})
write(f'{D}/dimension_type/mycelial.json', myc_type)
for name in ('clockwork', 'mycelial'):
    write(f'{D}/dimension/{name}.json', {'type': f'aurelia:{name}', 'generator': {
        'type': 'minecraft:noise', 'settings': f'aurelia:{name}', 'biome_source': {'type': 'minecraft:fixed', 'biome': f'aurelia:{name}'}}})

# the Rift is a void like Skyreach: every block is air, and the fragments are structures
rift = json.load(open(f'{D}/worldgen/noise_settings/skyreach.json'))
write(f'{D}/worldgen/noise_settings/clockwork.json', rift)


def block(name, props=None):
    s = {'Name': name}
    if props:
        s['Properties'] = props
    return {'type': 'minecraft:block', 'result_state': s}


def cond(c, then):
    return {'type': 'minecraft:condition', 'if_true': c, 'then_run': then}


def seq(*rules):
    return {'type': 'minecraft:sequence', 'sequence': list(rules)}


def depth(kind='floor', add=False, secondary=0):
    return {'type': 'minecraft:stone_depth', 'offset': 0, 'surface_type': kind, 'add_surface_depth': add, 'secondary_depth_range': secondary}


def noise(lo, hi, name='minecraft:surface'):
    return {'type': 'minecraft:noise_threshold', 'noise': name, 'min_threshold': lo, 'max_threshold': hi}


# the Deep: the Hollow's cavern shape, but deepslate and water instead of blackstone and lava, mycelium floors, bone ceilings
myc = json.load(open(f'{D}/worldgen/noise_settings/hollow.json'))
myc['default_block'] = {'Name': 'minecraft:deepslate', 'Properties': {'axis': 'y'}}
myc['default_fluid'] = {'Name': 'minecraft:water', 'Properties': {'level': '0'}}
rules = myc['surface_rule']['sequence'][:2]                       # bedrock floor and roof from the Hollow
rules += [
    cond(depth('floor'), seq(cond(noise(0.35, 9.0), block('minecraft:magenta_terracotta')),
                             cond(noise(-9.0, -0.45), block('minecraft:white_terracotta')),
                             block('minecraft:mycelium', {'snowy': 'false'}))),
    cond(depth('floor', add=True), block('minecraft:dirt')),
    cond(depth('ceiling'), seq(cond(noise(0.2, 9.0), block('minecraft:mushroom_stem', {'up': 'true', 'down': 'true', 'north': 'true', 'south': 'true',
                                                                                      'east': 'true', 'west': 'true'})),
                               block('minecraft:calcite'))),
]
myc['surface_rule'] = {'type': 'minecraft:sequence', 'sequence': rules}
write(f'{D}/worldgen/noise_settings/mycelial.json', myc)


def hexint(h):
    return int(h.lstrip('#'), 16)


def biome(name, precip, temp, down, colors, extra, spawners, carvers, features):
    steps = [[] for _ in range(11)]
    for step, items in features.items():
        steps[step] = items
    eff = {k: hexint(v) for k, v in colors.items()}
    eff.update(extra)
    sp = {'monster': [], 'creature': [], 'ambient': [], 'axolotls': [], 'underground_water_creature': [], 'water_creature': [], 'water_ambient': [], 'misc': []}
    sp.update(spawners)
    write(f'{D}/worldgen/biome/{name}.json', {'has_precipitation': precip, 'temperature': temp, 'downfall': down, 'effects': eff,
                                              'spawners': sp, 'spawn_costs': {}, 'carvers': {'air': carvers}, 'features': steps})


def spawn(t, w, lo, hi):
    return {'type': t, 'weight': w, 'minCount': lo, 'maxCount': hi}


biome('clockwork', False, 0.5, 0.0,
      {'sky_color': '#2A0E44', 'fog_color': '#3A1A5C', 'water_color': '#6A3AB0', 'water_fog_color': '#1A0A30', 'grass_color': '#7A5A9A', 'foliage_color': '#6A4A8A'},
      {'particle': {'options': {'type': 'minecraft:reverse_portal'}, 'probability': 0.012},
       'ambient_sound': 'minecraft:ambient.basalt_deltas.loop',
       'additions_sound': {'sound': 'minecraft:block.chain.place', 'tick_chance': 0.002}},
      {'monster': [spawn('aurelia:gearskitter', 40, 1, 3), spawn('minecraft:enderman', 10, 1, 1)]}, [], {})
biome('mycelial', False, 0.8, 0.9,
      {'sky_color': '#2A0A30', 'fog_color': '#4A1A50', 'water_color': '#B040C0', 'water_fog_color': '#3A0A40', 'grass_color': '#9A5AA0', 'foliage_color': '#A04AB0'},
      {'particle': {'options': {'type': 'minecraft:spore_blossom_air'}, 'probability': 0.03},
       'ambient_sound': 'minecraft:ambient.crimson_forest.loop',
       'mood_sound': {'sound': 'minecraft:ambient.cave', 'tick_delay': 6000, 'block_search_extent': 8, 'offset': 2.0}},
      {'monster': [spawn('aurelia:root_grub', 60, 1, 3), spawn('minecraft:spider', 10, 1, 2)], 'creature': [spawn('minecraft:mooshroom', 8, 2, 3)]},
      ['minecraft:nether_cave'],
      {2: ['minecraft:amethyst_geode'], 6: ['minecraft:ore_iron_upper', 'minecraft:ore_gold', 'minecraft:ore_diamond'],
       9: ['minecraft:mushroom_island_vegetation', 'minecraft:spore_blossom', 'minecraft:glow_lichen', 'minecraft:brown_mushroom_normal',
           'minecraft:red_mushroom_normal']})

# =========================================================================================== textures
def clock(hour, frame=(200, 150, 50), face=(236, 226, 200), glow=None, seed=0):
    img = noise_img(frame, 8, 900 + seed)
    d = ImageDraw.Draw(img)
    d.ellipse([1, 1, 14, 14], fill=face + (255,), outline=(120, 84, 30, 255))
    for k in range(12):
        a = k * math.pi / 6
        x, y = 7.5 + 5.6 * math.sin(a), 7.5 - 5.6 * math.cos(a)
        d.point((round(x), round(y)), fill=(60, 50, 40, 255))
    a = hour * math.pi / 6
    d.line([(7.5, 7.5), (7.5 + 3.6 * math.sin(a), 7.5 - 3.6 * math.cos(a))], fill=(30, 24, 30, 255), width=1)
    d.line([(7.5, 7.5), (7.5, 2.5)], fill=(90, 70, 110, 255), width=1)
    d.point((7, 7), fill=(170, 70, 255, 255) if glow else (40, 30, 30, 255))
    if glow:
        d.ellipse([0, 0, 15, 15], outline=glow + (255,))
    return img


for h in range(12):
    save(clock(h, seed=h), f'{BLK}/clock_dial_{h}.png')
    save(clock(h, glow=(180, 90, 255), seed=h + 20), f'{BLK}/clock_dial_{h}_set.png')
    save(clock(h, frame=(60, 50, 70), face=(250, 236, 200), glow=(255, 206, 90), seed=h + 40), f'{BLK}/master_clock_{h}.png')
for state, col in (('closed', (110, 42, 120)), ('open', (255, 70, 220))):
    side = noise_img((222, 210, 186), 8, 60)
    d = ImageDraw.Draw(side)
    d.rectangle([5, 0, 10, 15], fill=(196, 180, 152, 255))
    d.line([(7, 0), (7, 15)], fill=col + (255,))
    save(side, f'{BLK}/spore_valve_{state}_side.png')
    top = noise_img((196, 180, 152), 8, 61)
    d = ImageDraw.Draw(top)
    d.ellipse([3, 3, 12, 12], fill=(40, 16, 44, 255) if state == 'closed' else col + (255,), outline=(120, 90, 60, 255))
    d.line([(2, 7), (13, 7)], fill=(150, 110, 60, 255))
    save(top, f'{BLK}/spore_valve_{state}_top.png')
img = noise_img((40, 34, 48), 6, 70); d = ImageDraw.Draw(img)
d.ellipse([2, 2, 13, 13], outline=(200, 150, 50, 255)); d.line([(7, 7), (7, 3)], fill=(170, 70, 255, 255)); d.line([(7, 7), (11, 7)], fill=(170, 70, 255, 255))
save(img, f'{BLK}/paradox_seal.png')
img = noise_img((222, 210, 186), 10, 71); d = ImageDraw.Draw(img)
for pts in [[(0, 3), (6, 7), (15, 4)], [(2, 15), (8, 9), (13, 15)], [(6, 7), (8, 9)]]:
    d.line(pts, fill=(150, 64, 160, 255))
save(img, f'{BLK}/root_seal.png')
for name, base, fn, seed in [
        ('time_snare', (40, 34, 48), lambda d: (d.ellipse([2, 2, 13, 13], outline=(170, 70, 255, 255)), d.line([(7, 7), (4, 4)], fill=(255, 206, 90, 255))), 80),
        ('root_snare', (196, 180, 152), lambda d: [d.line([(0, y), (15, y + 3)], fill=(110, 42, 120, 255)) for y in (2, 7, 11)], 82)]:
    save(noise_img(base, 8, seed), f'{BLK}/{name}_side.png')
    t = noise_img(base, 8, seed + 1)
    fn(ImageDraw.Draw(t))
    save(t, f'{BLK}/{name}_top.png')
img = noise_img((150, 60, 230), 12, 90); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(200, 150, 50, 255)); d.ellipse([4, 4, 11, 11], outline=(240, 200, 255, 255))
save(img, f'{BLK}/chronite_block.png')
img = noise_img((200, 60, 190), 14, 91); d = ImageDraw.Draw(img)
for (x, y) in [(3, 3), (10, 5), (6, 11), (12, 12), (2, 9)]:
    d.ellipse([x, y, x + 2, y + 2], fill=(255, 190, 245, 255))
save(img, f'{BLK}/bloomspore_block.png')
WG = {'clockwork': ((180, 90, 255), (40, 34, 48)), 'mycelial': ((255, 70, 220), (110, 42, 120))}
for realm, (glow, frame) in WG.items():
    for on in (False, True):
        sfx = 'on' if on else 'off'
        side = noise_img(frame, 8, sum(map(ord, realm)) + on)
        d = ImageDraw.Draw(side)
        d.rectangle([3, 1, 12, 14], fill=(glow if on else tuple(c // 3 for c in glow)) + (255,), outline=(200, 160, 70, 255))
        if on:
            d.line([(8, 2), (8, 13)], fill=(255, 255, 255, 255))
        save(side, f'{BLK}/waygate_{realm}_{sfx}_side.png')
        top = noise_img(frame, 8, sum(map(ord, realm)) + 50 + on)
        ImageDraw.Draw(top).ellipse([3, 3, 12, 12], outline=(glow if on else (90, 90, 90)) + (255,))
        save(top, f'{BLK}/waygate_{realm}_{sfx}_top.png')

# items
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.polygon([(8, 1), (12, 6), (9, 14), (5, 12), (4, 5)], fill=(170, 80, 255, 255), outline=(200, 150, 50, 255)); d.line([(8, 3), (7, 11)], fill=(240, 220, 255, 255))
save(img, f'{ITEM}/chronite_shard.png')
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.ellipse([4, 3, 12, 11], fill=(200, 60, 190, 255), outline=(110, 42, 120, 255)); d.rectangle([7, 11, 9, 14], fill=(222, 210, 186, 255))
d.point([(6, 5), (9, 7)], fill=(255, 220, 250, 255))
save(img, f'{ITEM}/bloomspore.png')
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.ellipse([2, 2, 13, 13], fill=(40, 34, 48, 255), outline=(200, 150, 50, 255)); d.ellipse([5, 5, 10, 10], fill=(170, 70, 255, 255))
d.line([(7, 3), (7, 6)], fill=(10, 8, 12, 255)); d.line([(7, 6), (7, 9)], fill=(10, 8, 12, 255))
save(img, f'{ITEM}/hour_core.png')
img = Image.new('RGBA', (16, 16), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
d.polygon([(8, 14), (2, 7), (4, 2), (8, 5), (12, 2), (14, 7)], fill=(200, 50, 190, 255), outline=(110, 30, 120, 255))
d.point([(5, 5), (6, 4)], fill=(255, 210, 250, 255))
save(img, f'{ITEM}/bloom_heart.png')
crown = Image.open(f'{ITEM}/ascendant_crown.png').convert('RGBA'); d = ImageDraw.Draw(crown)
d.point([(6, 9), (9, 9)], fill=(170, 70, 255, 255)); d.point([(7, 10), (8, 10)], fill=(255, 70, 220, 255))
save(crown, f'{ITEM}/eternal_crown.png')
for layer in (1, 2):
    a = Image.open(f'{A}/textures/models/armor/aurelian_layer_{layer}.png').convert('RGBA')
    px = a.load()
    for x in range(a.width):
        for y in range(a.height):
            r_, g_, b_, al = px[x, y]
            if al:
                px[x, y] = (min(255, int(r_ * 0.8 + 40)), min(255, int(g_ * 0.6 + 10)), min(255, int(b_ * 0.8 + 80)), al)
    save(a, f'{A}/textures/models/armor/eternal_layer_{layer}.png')


# =========================================================================================== models, blockstates
def bs(name, variants):
    write(f'{A}/blockstates/{name}.json', {'variants': variants})


def model(name, obj):
    write(f'{A}/models/block/{name}.json', obj)


def item_model(name, obj):
    write(f'{A}/models/item/{name}.json', obj)


v = {}
for h in range(12):
    for filled in (False, True):
        m = f'clock_dial_{h}' + ('_set' if filled else '')
        model(m, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{m}'}})
        v[f'hour={h},filled={str(filled).lower()}'] = {'model': f'aurelia:block/{m}'}
bs('clock_dial', v)
item_model('clock_dial', {'parent': 'aurelia:block/clock_dial_0'})
v = {}
for h in range(12):
    model(f'master_clock_{h}', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/master_clock_{h}'}})
    v[f'hour={h}'] = {'model': f'aurelia:block/master_clock_{h}'}
bs('master_clock', v)
item_model('master_clock', {'parent': 'aurelia:block/master_clock_0'})
for st in ('closed', 'open'):
    model(f'spore_valve_{st}', {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/spore_valve_{st}_top', 'side': f'aurelia:block/spore_valve_{st}_side'}})
bs('spore_valve', {f'open={o},locked={l}': {'model': f'aurelia:block/spore_valve_{"open" if o == "true" else "closed"}'}
                   for o in ('true', 'false') for l in ('true', 'false')})
item_model('spore_valve', {'parent': 'aurelia:block/spore_valve_closed'})
for b in ('paradox_seal', 'root_seal', 'chronite_block', 'bloomspore_block'):
    bs(b, {'': {'model': f'aurelia:block/{b}'}})
    model(b, {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{b}'}})
    item_model(b, {'parent': f'aurelia:block/{b}'})
for b in ('time_snare', 'root_snare'):
    bs(b, {'': {'model': f'aurelia:block/{b}'}})
    model(b, {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/{b}_top', 'side': f'aurelia:block/{b}_side'}})
    item_model(b, {'parent': f'aurelia:block/{b}'})
wg = json.load(open(f'{A}/blockstates/waygate.json'))['variants']
for realm in WG:
    for on in (False, True):
        sfx = 'on' if on else 'off'
        wg[f'realm={realm},active={str(on).lower()}'] = {'model': f'aurelia:block/waygate_{realm}_{sfx}'}
        model(f'waygate_{realm}_{sfx}', {'parent': 'minecraft:block/cube_column', 'textures': {
            'end': f'aurelia:block/waygate_{realm}_{sfx}_top', 'side': f'aurelia:block/waygate_{realm}_{sfx}_side'}})
bs('waygate', wg)
for it in ('chronite_shard', 'bloomspore', 'hour_core', 'bloom_heart', 'eternal_crown'):
    item_model(it, {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'aurelia:item/{it}'}})
EGGS = ['vexor', 'bloom_mother', 'gearskitter', 'secondhand', 'hour_warden', 'root_grub', 'spore_drifter', 'husk_guard']
for e in EGGS:
    item_model(f'{e}_spawn_egg', {'parent': 'minecraft:item/template_spawn_egg'})


# =========================================================================================== loot, recipes, tags
def entry(item, weight, lo=None, hi=None):
    e = {'type': 'minecraft:item', 'name': item, 'weight': weight}
    if lo is not None:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]
    return e


def pool(entries, rolls=1, chance=None):
    p = {'rolls': rolls, 'entries': entries}
    if chance is not None:
        p['conditions'] = [{'condition': 'minecraft:killed_by_player'}, {'condition': 'minecraft:random_chance', 'chance': chance}]
    return p


for b in ('chronite_block', 'bloomspore_block', 'time_snare', 'root_snare', 'clock_dial', 'master_clock', 'spore_valve'):
    write(f'{D}/loot_tables/blocks/{b}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
          'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{b}'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})
GUARD_LOOT = {
    'gearskitter': ('chronite_shard', 0, 2, [entry('minecraft:gold_nugget', 3, 2, 6), entry('minecraft:iron_ingot', 2, 1, 2)]),
    'secondhand': ('chronite_shard', 1, 3, [entry('minecraft:amethyst_shard', 3, 1, 3), entry('minecraft:clock', 1, 1, 1)]),
    'hour_warden': ('chronite_shard', 2, 4, [entry('minecraft:gold_ingot', 3, 2, 5), entry('minecraft:diamond', 1, 1, 1)]),
    'root_grub': ('bloomspore', 0, 2, [entry('minecraft:brown_mushroom', 3, 1, 3)]),
    'spore_drifter': ('bloomspore', 1, 3, [entry('minecraft:glow_berries', 3, 2, 5), entry('minecraft:spore_blossom', 1, 1, 1)]),
    'husk_guard': ('bloomspore', 2, 4, [entry('minecraft:bone', 3, 2, 5), entry('minecraft:diamond', 1, 1, 1)]),
}
for mob, (mat, lo, hi, extra) in GUARD_LOOT.items():
    write(f'{D}/loot_tables/entities/{mob}.json', {'type': 'minecraft:entity', 'pools': [
        pool([entry(f'aurelia:{mat}', 1, lo, hi)]), pool(extra, chance=0.5), pool([entry('minecraft:emerald', 1, 1, 3)], chance=0.35)]})
common = [entry('minecraft:diamond', 6, 1, 3), entry('minecraft:emerald', 10, 2, 6), entry('minecraft:golden_apple', 4), entry('minecraft:experience_bottle', 8, 4, 10),
          entry('minecraft:ender_pearl', 5, 1, 3), entry('minecraft:enchanted_golden_apple', 1), entry('minecraft:netherite_scrap', 3, 1, 2)]
for table, mat, extra in [('paradox_cache', 'chronite_shard', [entry('minecraft:clock', 3, 1, 1), entry('minecraft:totem_of_undying', 1)]),
                          ('cathedral_cache', 'bloomspore', [entry('minecraft:spore_blossom', 3, 1, 2), entry('minecraft:totem_of_undying', 1)]),
                          ('rift_outpost', 'chronite_shard', [entry('minecraft:amethyst_shard', 4, 2, 6)]),
                          ('mycelial_outpost', 'bloomspore', [entry('minecraft:glow_berries', 4, 3, 8)])]:
    write(f'{D}/loot_tables/chests/{table}.json', {'type': 'minecraft:chest', 'pools': [
        {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{mat}',
                                                    'functions': [{'function': 'minecraft:set_count', 'count': {'min': 4, 'max': 9}}]}]},
        {'rolls': {'min': 3, 'max': 5}, 'bonus_rolls': 0, 'entries': common + extra}]})
for name, item in (('chronite_block', 'chronite_shard'), ('bloomspore_block', 'bloomspore')):
    write(f'{D}/recipes/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['###', '###', '###'],
                                       'key': {'#': {'item': f'aurelia:{item}'}}, 'result': {'item': f'aurelia:{name}', 'count': 1}})
    write(f'{D}/recipes/{item}_from_block.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                                 'ingredients': [{'item': f'aurelia:{name}'}], 'result': {'item': f'aurelia:{item}', 'count': 9}})
write(f'{D}/recipes/eternal_crown.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
      'ingredients': [{'item': f'aurelia:{i}'} for i in ['ascendant_crown', 'hour_core', 'bloom_heart', 'chronite_block', 'bloomspore_block']],
      'result': {'item': 'aurelia:eternal_crown', 'count': 1}})
p = f'{ROOT}/data/minecraft/tags/blocks/mineable/pickaxe.json'
j = json.load(open(p))
j['values'] += [x for x in ['aurelia:chronite_block', 'aurelia:time_snare'] if x not in j['values']]
write(p, j)
p = f'{ROOT}/data/minecraft/tags/blocks/mineable/axe.json'
j = json.load(open(p)) if os.path.exists(p) else {'replace': False, 'values': []}
j['values'] += [x for x in ['aurelia:bloomspore_block', 'aurelia:root_snare'] if x not in j['values']]
write(p, j)


# =========================================================================================== structures
def structure(name, tag, start, project, adapt, spawns, variants, spacing, sep, salt, excl, biome_values=None):
    if biome_values is not None:
        write(f'{D}/tags/worldgen/biome/has_structure/{tag}.json', {'replace': False, 'values': biome_values})
    s = {'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/{tag}', 'step': 'surface_structures', 'spawn_overrides': spawns,
         'terrain_adaptation': adapt, 'start_pool': f'aurelia:{name}/start', 'size': 1, 'start_height': start,
         'max_distance_from_center': 80, 'use_expansion_hack': False}
    if project:
        s['project_start_to_heightmap'] = project
    write(f'{D}/worldgen/structure/{name}.json', s)
    write(f'{D}/worldgen/template_pool/{name}/start.json', {'fallback': 'minecraft:empty', 'elements': [
        {'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:{v}', 'processors': {'processors': []},
                                  'projection': 'rigid'}} for v in variants]})
    placement = {'type': 'minecraft:random_spread', 'spacing': spacing, 'separation': sep, 'salt': salt}
    if excl:
        placement['exclusion_zone'] = {'other_set': f'aurelia:{excl[0]}', 'chunk_count': excl[1]}
    write(f'{D}/worldgen/structure_set/{name}.json', {'structures': [{'structure': f'aurelia:{name}', 'weight': 1}], 'placement': placement})


structure('paradox_keep', 'paradox_keep', {'absolute': -9}, 'WORLD_SURFACE_WG', 'beard_box',
          {'monster': {'bounding_box': 'full', 'spawns': [spawn('aurelia:gearskitter', 1, 1, 1)]}}, ['paradox_keep'], 36, 12, 71920507, None,
          ['minecraft:plains', 'minecraft:sunflower_plains', 'minecraft:meadow'])
structure('spore_cathedral', 'spore_cathedral', {'absolute': -6}, 'WORLD_SURFACE_WG', 'beard_box',
          {'monster': {'bounding_box': 'full', 'spawns': [spawn('aurelia:root_grub', 1, 1, 1)]}}, ['spore_cathedral'], 36, 12, 71920508, None,
          ['minecraft:dark_forest', 'minecraft:mushroom_fields', 'minecraft:old_growth_spruce_taiga'])


def uniform(lo, hi):
    return {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}


for tag, biome_id in (('clockwork_decor', 'aurelia:clockwork'), ('mycelial_decor', 'aurelia:mycelial')):
    write(f'{D}/tags/worldgen/biome/has_structure/{tag}.json', {'replace': False, 'values': [biome_id]})
for name, variants, tag, start, project, spacing, sep, salt, excl in [
        ('rift_fragments', ['rift_fragment_0', 'rift_fragment_1', 'rift_fragment_2'], 'clockwork_decor', uniform(50, 170), None, 4, 1, 91000301, None),
        ('rift_spires', ['rift_spire_0', 'rift_spire_1'], 'clockwork_decor', uniform(60, 140), None, 8, 3, 91000302, ('rift_fragments', 1)),
        ('rift_bridges', ['rift_bridge_0', 'rift_bridge_1'], 'clockwork_decor', uniform(70, 150), None, 6, 2, 91000303, ('rift_spires', 1)),
        ('rift_outposts', ['rift_outpost_0', 'rift_outpost_1'], 'clockwork_decor', uniform(80, 140), None, 9, 4, 91000304, ('rift_spires', 2)),
        ('mycelial_towers', ['fungal_tower_0', 'fungal_tower_1', 'fungal_tower_2'], 'mycelial_decor', uniform(33, 60), None, 4, 1, 91000305, None),
        ('mycelial_arches', ['root_arch_0', 'root_arch_1'], 'mycelial_decor', uniform(33, 60), None, 7, 3, 91000306, ('mycelial_towers', 1)),
        ('mycelial_outposts', ['spore_shrine_0', 'spore_shrine_1'], 'mycelial_decor', uniform(33, 55), None, 9, 4, 91000307, ('mycelial_arches', 2))]:
    structure(name, tag, start, project, 'beard_thin' if tag == 'mycelial_decor' else 'none', {}, variants, spacing, sep, salt, excl)

# =========================================================================================== names
lp = f'{A}/lang/en_us.json'
lang = json.load(open(lp, encoding='utf-8'))
lang.update({
    'entity.aurelia.vexor': 'Vexor, the Hour Eater', 'entity.aurelia.bloom_mother': 'The Bloom Mother',
    'entity.aurelia.gearskitter': 'Gearskitter', 'entity.aurelia.secondhand': 'Secondhand', 'entity.aurelia.hour_warden': 'Hour Warden',
    'entity.aurelia.root_grub': 'Root Grub', 'entity.aurelia.spore_drifter': 'Spore Drifter', 'entity.aurelia.husk_guard': 'Husk Guard',
    'block.aurelia.clock_dial': 'Clock Dial', 'block.aurelia.master_clock': 'Master Clock', 'block.aurelia.spore_valve': 'Spore Valve',
    'block.aurelia.paradox_seal': 'Paradox Seal', 'block.aurelia.root_seal': 'Root Seal', 'block.aurelia.time_snare': 'Time Snare',
    'block.aurelia.root_snare': 'Root Snare', 'block.aurelia.chronite_block': 'Block of Chronite', 'block.aurelia.bloomspore_block': 'Bloomspore Block',
    'item.aurelia.chronite_shard': 'Chronite Shard', 'item.aurelia.bloomspore': 'Bloomspore',
    'item.aurelia.chronite_shard.lore': 'Crystallised time, chipped from the Rift. It is always slightly warmer than a second ago.',
    'item.aurelia.bloomspore.lore': 'It pulses in your palm, very slowly, like something asleep.',
    'item.aurelia.hour_core': 'Hour Core', 'item.aurelia.hour_core.lore': 'The heart of the Hour Eater. It ticks backwards.',
    'item.aurelia.bloom_heart': 'Bloom Heart', 'item.aurelia.bloom_heart.lore': 'It is still singing, too low to hear.',
    'item.aurelia.eternal_crown': 'Eternal Crown',
    'structure.aurelia.paradox_keep': 'Paradox Keep', 'structure.aurelia.spore_cathedral': 'Spore Cathedral',
})
for e in EGGS:
    lang[f'item.aurelia.{e}_spawn_egg'] = lang[f'entity.aurelia.{e}'].split(',')[0].replace('The ', '') + ' Spawn Egg'
json.dump(lang, open(lp, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('act three data and assets written')
