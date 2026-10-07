import copy, json, os, random
from PIL import Image, ImageDraw

ROOT = __import__('paths').RES
A = f'{ROOT}/assets/aurelia'
D = f'{ROOT}/data/aurelia'
V = __import__('paths').VANILLA


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def noise(base, var, seed):
    r = random.Random(seed)
    img = Image.new('RGBA', (16, 16))
    px = img.load()
    for x in range(16):
        for y in range(16):
            v = r.randint(-var, var)
            px[x, y] = tuple(max(0, min(255, c + v)) for c in base) + (255,)
    return img


BLK, ITEM = f'{A}/textures/block', f'{A}/textures/item'
os.makedirs(BLK, exist_ok=True)
STONE, CALC, BLACK = (125, 125, 125), (224, 226, 222), (46, 40, 50)
REALM = {'verdant': ((110, 235, 100), (40, 130, 50), STONE), 'stormglass': ((120, 215, 255), (50, 110, 190), CALC), 'emberheart': ((255, 150, 50), (190, 60, 20), BLACK)}

# ---- ores, storage blocks, material items
for i, (name, (gem, dark, rock)) in enumerate(REALM.items()):
    img = noise(rock, 9, 100 + i)
    r = random.Random(200 + i)
    d = ImageDraw.Draw(img)
    for _ in range(6):
        x, y = r.randint(1, 12), r.randint(1, 12)
        d.rectangle([x, y, x + 2, y + 1], fill=gem + (255,))
        d.point([(x, y + 2), (x + 3, y)], fill=dark + (255,))
        d.point([(x + 1, y)], fill=(255, 255, 255, 255))
    img.save(f'{BLK}/{name}_ore.png')
    img = noise(gem, 12, 300 + i)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 15, 15], outline=dark + (255,))
    d.rectangle([3, 3, 12, 12], outline=tuple(min(255, c + 60) for c in gem) + (255,))
    d.line([(4, 11), (11, 4)], fill=(255, 255, 255, 255))
    img.save(f'{BLK}/{name}_block.png')
    item = name + '_shard' if name != 'emberheart' else 'emberheart'
    img = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if name == 'emberheart':
        d.ellipse([3, 3, 12, 13], fill=gem + (255,), outline=dark + (255,))
        d.ellipse([6, 6, 9, 9], fill=(255, 240, 150, 255))
    else:
        d.polygon([(8, 1), (12, 6), (9, 14), (5, 12), (4, 5)], fill=gem + (255,), outline=dark + (255,))
        d.line([(8, 3), (7, 11)], fill=(255, 255, 255, 255))
    img.save(f'{ITEM}/{item}.png')

# ---- seals (cube_all) and root heart
img = noise((70, 50, 30), 10, 1); d = ImageDraw.Draw(img)
for (a, b) in [((0, 3), (15, 12)), ((3, 0), (12, 15)), ((0, 12), (15, 3)), ((8, 0), (8, 15))]:
    d.line([a, b], fill=(60, 130, 50, 255))
for (x, y) in [(4, 4), (11, 5), (7, 10), (12, 12), (3, 12)]:
    d.point((x, y), fill=(150, 230, 90, 255))
img.save(f'{BLK}/bramble_seal.png')
img = noise((60, 150, 215), 10, 2); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(235, 245, 255, 255))
for k in range(0, 16, 5):
    d.line([(k, 0), (k, 15)], fill=(190, 235, 255, 255)); d.line([(0, k), (15, k)], fill=(190, 235, 255, 255))
d.line([(7, 2), (5, 7), (9, 8), (7, 13)], fill=(255, 255, 255, 255), width=1)
img.save(f'{BLK}/storm_seal.png')
img = noise((34, 30, 38), 6, 3); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 15, 15], outline=(20, 18, 24, 255))
for pts in [[(2, 3), (6, 6), (5, 11), (9, 14)], [(13, 2), (10, 6), (12, 10)], [(7, 1), (8, 4)]]:
    d.line(pts, fill=(255, 130, 40, 255))
img.save(f'{BLK}/ash_seal.png')
img = noise((60, 110, 50), 12, 4); d = ImageDraw.Draw(img)
d.ellipse([3, 3, 12, 12], fill=(130, 240, 90, 255), outline=(40, 80, 34, 255))
d.ellipse([6, 6, 9, 9], fill=(235, 255, 190, 255))
for pts in [[(0, 0), (4, 4)], [(15, 0), (11, 4)], [(0, 15), (4, 11)], [(15, 15), (11, 11)]]:
    d.line(pts, fill=(74, 52, 30, 255))
img.save(f'{BLK}/root_heart.png')

# ---- traps: a patterned top, plain sides
def trap(name, side_rgb, top_fn, seed):
    noise(side_rgb, 8, seed).save(f'{BLK}/{name}_side.png')
    img = noise(side_rgb, 8, seed + 1)
    top_fn(ImageDraw.Draw(img))
    img.save(f'{BLK}/{name}_top.png')


trap('spore_vent', (92, 122, 50), lambda d: (d.ellipse([3, 3, 12, 12], fill=(30, 44, 22, 255), outline=(50, 80, 36, 255)),
                                              d.ellipse([6, 6, 9, 9], fill=(150, 255, 90, 255))), 10)
trap('gale_plate', (232, 228, 222), lambda d: (d.rectangle([1, 1, 14, 14], outline=(110, 200, 245, 255)),
                                                d.polygon([(8, 3), (12, 8), (9, 8), (9, 12), (7, 12), (7, 8), (4, 8)], fill=(90, 205, 255, 255))), 20)
trap('ember_vent', (50, 44, 54), lambda d: [d.line([(2, y), (13, y)], fill=(255, 130, 40, 255)) for y in (3, 6, 9, 12)], 30)

# ---- models, blockstates, items
CUBE_ALL = ['bramble_seal', 'storm_seal', 'ash_seal', 'root_heart', 'verdant_ore', 'stormglass_ore', 'emberheart_ore',
            'verdant_block', 'stormglass_block', 'emberheart_block']
for b in CUBE_ALL:
    write(f'{A}/blockstates/{b}.json', {'variants': {'': {'model': f'aurelia:block/{b}'}}})
    write(f'{A}/models/block/{b}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{b}'}})
    write(f'{A}/models/item/{b}.json', {'parent': f'aurelia:block/{b}'})
for b in ['spore_vent', 'gale_plate', 'ember_vent']:
    write(f'{A}/blockstates/{b}.json', {'variants': {'': {'model': f'aurelia:block/{b}'}}})
    write(f'{A}/models/block/{b}.json', {'parent': 'minecraft:block/cube_column', 'textures': {'end': f'aurelia:block/{b}_top', 'side': f'aurelia:block/{b}_side'}})
    write(f'{A}/models/item/{b}.json', {'parent': f'aurelia:block/{b}'})
for it in ['verdant_shard', 'stormglass_shard', 'emberheart']:
    write(f'{A}/models/item/{it}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'aurelia:item/{it}'}})

# ---- loot tables: ores copy vanilla emerald ore, everything else drops itself
MAT = {'verdant': 'verdant_shard', 'stormglass': 'stormglass_shard', 'emberheart': 'emberheart'}
for name, item in MAT.items():
    lt = json.load(open(f'{V}/lt_emerald_ore.json'))
    lt.pop('random_sequence', None)
    ch = lt['pools'][0]['entries'][0]['children']
    ch[0]['name'] = f'aurelia:{name}_ore'
    ch[1]['name'] = f'aurelia:{item}'
    ch[1]['functions'].insert(0, {'function': 'minecraft:set_count', 'count': {'min': 1, 'max': 3}})
    write(f'{D}/loot_tables/blocks/{name}_ore.json', lt)
for b in ['verdant_block', 'stormglass_block', 'emberheart_block', 'spore_vent', 'gale_plate', 'ember_vent']:
    write(f'{D}/loot_tables/blocks/{b}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
        'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{b}'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}]})

# ---- tags: mine with a pickaxe, need iron
mine = ['aurelia:verdant_ore', 'aurelia:stormglass_ore', 'aurelia:emberheart_ore', 'aurelia:verdant_block', 'aurelia:stormglass_block',
        'aurelia:emberheart_block', 'aurelia:spore_vent', 'aurelia:gale_plate', 'aurelia:ember_vent', 'aurelia:root_heart']
write(f'{ROOT}/data/minecraft/tags/blocks/mineable/pickaxe.json', {'replace': False, 'values': mine})
write(f'{ROOT}/data/minecraft/tags/blocks/needs_iron_tool.json', {'replace': False, 'values': mine[:6]})

# ---- recipes: storage blocks both ways, and the Crown now needs one block of each realm material
for name, item in MAT.items():
    write(f'{D}/recipes/{name}_block.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['###', '###', '###'],
                                            'key': {'#': {'item': f'aurelia:{item}'}}, 'result': {'item': f'aurelia:{name}_block', 'count': 1}})
    write(f'{D}/recipes/{item}_from_block.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                                 'ingredients': [{'item': f'aurelia:{name}_block'}], 'result': {'item': f'aurelia:{item}', 'count': 9}})
write(f'{D}/recipes/crown_of_aurelia.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
      'ingredients': [{'item': f'aurelia:{i}'} for i in ['grove_shard', 'storm_shard', 'void_shard', 'verdant_block', 'stormglass_block', 'emberheart_block']],
      'result': {'item': 'aurelia:crown_of_aurelia', 'count': 1}})

# ---- ore generation: Grove (in stone) and Hollow (in blackstone and basalt); Skyreach ore is built into the islands
cf = json.load(open(f'{V}/cf_ore_emerald.json'))
cf['config']['size'] = 7
for t in cf['config']['targets']:
    t['state'] = {'Name': 'aurelia:verdant_ore'}
write(f'{D}/worldgen/configured_feature/ore_verdant.json', cf)
pf = json.load(open(f'{V}/pf_ore_emerald.json'))
pf['feature'] = 'aurelia:ore_verdant'
pf['placement'][0]['count'] = 14
pf['placement'][2]['height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': 0}, 'max_inclusive': {'absolute': 220}}
write(f'{D}/worldgen/placed_feature/ore_verdant.json', pf)
cf = json.load(open(f'{V}/cf_ore_quartz.json'))
cf['config']['size'] = 8
base = cf['config']['targets'][0]
cf['config']['targets'] = []
for blk in ['minecraft:blackstone', 'minecraft:basalt', 'minecraft:smooth_basalt']:
    t = copy.deepcopy(base)
    t['state'] = {'Name': 'aurelia:emberheart_ore'}
    t['target']['block'] = blk
    cf['config']['targets'].append(t)
write(f'{D}/worldgen/configured_feature/ore_emberheart.json', cf)
pf = json.load(open(f'{V}/pf_ore_quartz_nether.json'))
pf['feature'] = 'aurelia:ore_emberheart'
pf['placement'][0]['count'] = 12
write(f'{D}/worldgen/placed_feature/ore_emberheart.json', pf)
for biome, step, fid in [('grove', 6, 'aurelia:ore_verdant'), ('hollow', 7, 'aurelia:ore_emberheart')]:
    p = f'{D}/worldgen/biome/{biome}.json'
    j = json.load(open(p))
    if fid not in j['features'][step]:
        j['features'][step].append(fid)
    write(p, j)

# ---- chest loot for outposts and the Stormwatch caches
def entry(item, weight, lo=None, hi=None):
    e = {'type': 'minecraft:item', 'name': item, 'weight': weight}
    if lo is not None:
        e['functions'] = [{'function': 'minecraft:set_count', 'count': {'min': lo, 'max': hi}}]
    return e


common = [entry('minecraft:diamond', 5, 1, 2), entry('minecraft:emerald', 10, 2, 5), entry('minecraft:golden_apple', 4),
          entry('minecraft:experience_bottle', 8, 3, 8), entry('minecraft:ender_pearl', 5, 1, 3), entry('minecraft:iron_ingot', 8, 2, 6)]
for table, mat, extra in [('grove_outpost', 'verdant_shard', entry('aurelia:spore_heart', 4, 1, 1)),
                          ('skyreach_outpost', 'stormglass_shard', entry('minecraft:feather', 6, 4, 10)),
                          ('hollow_outpost', 'emberheart', entry('aurelia:soul_sigil', 5, 1, 2)),
                          ('stormwatch_cache', 'stormglass_shard', entry('minecraft:enchanted_golden_apple', 2))]:
    write(f'{D}/loot_tables/chests/{table}.json', {'type': 'minecraft:chest', 'pools': [
        {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{mat}',
                                                    'functions': [{'function': 'minecraft:set_count', 'count': {'min': 3, 'max': 7}}]}]},
        {'rolls': {'min': 3, 'max': 5}, 'bonus_rolls': 0, 'entries': common + [extra]}]})

# ---- names
lp = f'{A}/lang/en_us.json'
lang = json.load(open(lp, encoding='utf-8'))
lang.update({
    'block.aurelia.bramble_seal': 'Bramble Seal', 'block.aurelia.storm_seal': 'Storm Seal', 'block.aurelia.ash_seal': 'Ash Seal',
    'block.aurelia.spore_vent': 'Spore Vent', 'block.aurelia.gale_plate': 'Gale Plate', 'block.aurelia.ember_vent': 'Ember Vent',
    'block.aurelia.root_heart': 'Root Heart', 'block.aurelia.verdant_ore': 'Verdant Ore', 'block.aurelia.stormglass_ore': 'Stormglass Ore',
    'block.aurelia.emberheart_ore': 'Emberheart Ore', 'block.aurelia.verdant_block': 'Block of Verdant Shards',
    'block.aurelia.stormglass_block': 'Block of Stormglass', 'block.aurelia.emberheart_block': 'Block of Emberheart',
    'item.aurelia.verdant_shard': 'Verdant Shard', 'item.aurelia.stormglass_shard': 'Stormglass Shard', 'item.aurelia.emberheart': 'Emberheart',
    'item.aurelia.verdant_shard.lore': 'Mined in the Gaudy Grove. It is still growing.',
    'item.aurelia.stormglass_shard.lore': 'Found in the rock of the Skyreach islands. It holds a spark.',
    'item.aurelia.emberheart.lore': 'Dug from the walls of the Hollow. Warm to the touch.',
})
json.dump(lang, open(lp, 'w', encoding='utf-8'), indent=2)
print('assets, loot, tags, recipes and ore generation written')
