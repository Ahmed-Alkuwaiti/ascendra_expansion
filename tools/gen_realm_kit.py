"""Every realm's food, wildlife spawns and loot, and the two rift ores' blocks, worldgen and loot (Chronite in the Clockwork Rift's
floating rock, Bloomspore in the Mycelial Deep). Armor, weapons, tools, materials and every sprite: gen_arsenal.py. Definitions: kit_data.py."""
import json
import os

from PIL import Image, ImageDraw

import paths
from kit_data import KIT, REALMS

A = paths.RES + '/assets/aurelia'
D = paths.RES + '/data/aurelia'
MC = paths.RES + '/data/minecraft'
ITEM, BLK, ARM = f'{A}/textures/item', f'{A}/textures/block', f'{A}/textures/models/armor'


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def shade(c, k):
    return tuple(max(0, min(255, int(v * k))) for v in c[:3]) + (255,)


# =========================================================================================== sprite helpers
def outline(img, dark=0.45):
    """Give every opaque shape a one-pixel dark outline, like vanilla items."""
    px = img.load()
    out = img.copy()
    po = out.load()
    for x in range(16):
        for y in range(16):
            if px[x, y][3]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 16 and 0 <= ny < 16 and px[nx, ny][3]:
                    po[x, y] = shade(px[nx, ny], dark)
                    break
    return out


def mask():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


MAG = (255, 0, 255, 255)


def food_sprite(realm, pal, accent):
    img = mask()
    d = ImageDraw.Draw(img)
    P = [c + (255,) for c in pal]
    if realm == 'grove':
        d.ellipse([4, 5, 12, 14], fill=P[1]); d.ellipse([5, 6, 9, 10], fill=P[2]); d.line([(8, 5), (9, 2)], fill=(100, 70, 40, 255))
        d.ellipse([9, 1, 12, 3], fill=P[2])
    elif realm == 'skyreach':
        d.ellipse([3, 4, 13, 13], fill=P[2] [:3] + (230,)); d.ellipse([5, 5, 9, 9], fill=P[3])
    elif realm == 'hollow':
        d.polygon([(3, 10), (6, 5), (12, 4), (13, 9), (8, 13)], fill=(70, 40, 30, 255)); d.line([(5, 9), (11, 6)], fill=P[2])
        d.point([(7, 8), (10, 7)], fill=P[3])
    elif realm == 'drowned':
        d.ellipse([3, 4, 13, 12], fill=P[2]); d.ellipse([5, 5, 9, 8], fill=P[3]); d.point([(6, 12), (9, 13), (11, 12)], fill=P[1])
    elif realm == 'pale':
        d.ellipse([3, 6, 11, 13], fill=(200, 120, 110, 255)); d.ellipse([4, 7, 8, 10], fill=(230, 160, 150, 255))
        d.line([(10, 8), (14, 3)], fill=(240, 240, 240, 255), width=2)
    elif realm == 'scarlet':
        d.line([(2, 12), (6, 9), (10, 8), (13, 4)], fill=P[1], width=3); d.line([(3, 11), (7, 9), (11, 7)], fill=P[3])
    elif realm == 'clockwork':
        for (x, y) in [(4, 7), (8, 5), (9, 10)]:
            d.ellipse([x, y, x + 4, y + 4], fill=P[1]); d.point((x + 1, y + 1), fill=P[3])
        d.line([(6, 7), (8, 2), (10, 5)], fill=(60, 120, 60, 255))
    else:
        d.ellipse([3, 3, 13, 10], fill=P[2]); d.rectangle([7, 9, 9, 14], fill=(220, 210, 186, 255))
        d.point([(5, 5), (9, 4), (11, 7)], fill=(255, 230, 250, 255))
    img = light_keep(img)
    return outline(img)


def light_keep(img):
    return img


def item_model(name, parent='minecraft:item/generated'):
    write(f'{A}/models/item/{name}.json', {'parent': parent, 'textures': {'layer0': f'aurelia:item/{name}'}})


lang_p = f'{A}/lang/en_us.json'
lang = json.load(open(lang_p, encoding='utf-8'))
spawns = {}
for realm in REALMS:
    k = KIT[realm]
    pal, accent = k['palette'], k['accent']
    # armor, weapons and tools now belong to gen_arsenal.py
    f = k['food']
    save(food_sprite(realm, pal, accent), f'{ITEM}/{f}.png')
    item_model(f)
    lang[f'item.aurelia.{f}'] = k['food_name']
    c = k['critter']
    lang[f'entity.aurelia.{c}'] = k['critter_name']
    lang[f'item.aurelia.{c}_spawn_egg'] = k['critter_name'] + ' Spawn Egg'
    write(f'{A}/models/item/{c}_spawn_egg.json', {'parent': 'minecraft:item/template_spawn_egg'})
    write(f'{D}/loot_tables/entities/{c}.json', {'type': 'minecraft:entity', 'pools': [
        {'rolls': 1, 'bonus_rolls': 0, 'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{f}', 'functions': [
            {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': 1, 'max': 2}},
            {'function': 'minecraft:looting_enchant', 'count': {'type': 'minecraft:uniform', 'min': 0, 'max': 1}}]}]},
        {'rolls': 1, 'bonus_rolls': 0, 'conditions': [{'condition': 'minecraft:random_chance_with_looting', 'chance': 0.2, 'looting_multiplier': 0.05}],
         'entries': [{'type': 'minecraft:item', 'name': f'aurelia:{k["material"]}'}]}]})
    spawns[realm] = c
    lang[f'item.aurelia.{f}.power'] = k['food_power']

# ---- the two new ores
ORES = {'chronite_ore': ((60, 58, 66), (170, 90, 255), (240, 210, 255), 'chronite_shard', 'Chronite Ore'),
        'bloomspore_ore': ((84, 84, 90), (210, 70, 200), (255, 200, 245), 'bloomspore', 'Bloomspore Ore')}
for ore, (base, crys, glow, drop, title) in ORES.items():
    # the ore's texture and name come from gen_arsenal.py
    write(f'{A}/blockstates/{ore}.json', {'variants': {'': {'model': f'aurelia:block/{ore}'}}})
    write(f'{A}/models/block/{ore}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{ore}'}})
    write(f'{A}/models/item/{ore}.json', {'parent': f'aurelia:block/{ore}'})
    lt = json.load(open(f'{D}/loot_tables/blocks/rime_ore.json'))
    txt = json.dumps(lt).replace('aurelia:rime_ore', f'aurelia:{ore}').replace('aurelia:rime_crystal', f'aurelia:{drop}')
    write(f'{D}/loot_tables/blocks/{ore}.json', json.loads(txt))
cf = json.load(open(f'{D}/worldgen/configured_feature/ore_rime.json'))
write(f'{D}/worldgen/configured_feature/ore_bloomspore.json', json.loads(json.dumps(cf).replace('aurelia:rime_ore', 'aurelia:bloomspore_ore')))
pf = json.load(open(f'{D}/worldgen/placed_feature/ore_rime.json'))
pf['feature'] = 'aurelia:ore_bloomspore'
pf['placement'][0]['count'] = 18
pf['placement'][2]['height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': 0}, 'max_inclusive': {'absolute': 120}}
write(f'{D}/worldgen/placed_feature/ore_bloomspore.json', pf)

# ---- spawns: each realm's biome gains its creature (the jelly in the water)
for realm, c in spawns.items():
    p = f'{D}/worldgen/biome/{realm}.json'
    b = json.load(open(p))
    cat = 'water_ambient' if c == 'lantern_jelly' else 'creature'
    lst = b['spawners'].setdefault(cat, [])
    if not any(s['type'] == f'aurelia:{c}' for s in lst):
        lst.append({'type': f'aurelia:{c}', 'weight': 12 if cat == 'creature' else 20, 'minCount': 2, 'maxCount': 4})
    if realm == 'mycelial':
        feats = b['features']
        if 'aurelia:ore_bloomspore' not in feats[6]:
            feats[6].append('aurelia:ore_bloomspore')
    write(p, b)

# ---- tags
for tag, extra in [(f'{MC}/tags/blocks/mineable/pickaxe.json', ['aurelia:chronite_ore', 'aurelia:bloomspore_ore']),
                   (f'{MC}/tags/blocks/needs_diamond_tool.json', ['aurelia:chronite_ore', 'aurelia:bloomspore_ore']),
                   ]:
    j = json.load(open(tag)) if os.path.exists(tag) else {'replace': False, 'values': []}
    j['values'] += [x for x in extra if x not in j['values']]
    write(tag, j)
json.dump(lang, open(lang_p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('realm kits written: foods, creatures, ores')
