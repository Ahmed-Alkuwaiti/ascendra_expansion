"""Every realm's kit: armor (item sprites and worn textures), signature weapon, food, wildlife spawns and loot, the two new ores
(Chronite in the Clockwork Rift's floating rock, Bloomspore in the Mycelial Deep), recipes, tags and names. Definitions: kit_data.py."""
import json
import math
import os
import random

from PIL import Image, ImageDraw

import paths
from kit_data import KIT, PIECES, REALMS

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


def light(img, pal):
    """Shade a flat mask into the palette: lit from the top left, darker toward the bottom right and at the edges."""
    px = img.load()
    for x in range(16):
        for y in range(16):
            if not px[x, y][3] or px[x, y][:3] != (255, 0, 255):
                continue
            edge = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if not (0 <= x + dx < 16 and 0 <= y + dy < 16) or not px[x + dx, y + dy][3])
            t = (x - y) / 30.0 + 0.5 - 0.18 * edge
            idx = max(0, min(3, int(t * 4)))
            px[x, y] = pal[idx] + (255,)
    return img


def mask():
    return Image.new('RGBA', (16, 16), (0, 0, 0, 0))


MAG = (255, 0, 255, 255)


def armor_sprite(piece, pal, accent):
    img = mask()
    d = ImageDraw.Draw(img)
    if piece == 'helmet':
        d.rectangle([3, 4, 12, 11], fill=MAG)
        d.rectangle([4, 3, 11, 3], fill=MAG)
        d.rectangle([5, 8, 10, 11], fill=(0, 0, 0, 0))
        light(img, pal)
        d.line([(4, 6), (11, 6)], fill=accent + (255,))
    elif piece == 'chestplate':
        d.rectangle([2, 2, 13, 5], fill=MAG)
        d.rectangle([4, 2, 11, 14], fill=MAG)
        d.rectangle([6, 2, 9, 3], fill=(0, 0, 0, 0))
        d.rectangle([1, 3, 2, 8], fill=MAG)
        d.rectangle([13, 3, 14, 8], fill=MAG)
        light(img, pal)
        d.rectangle([7, 6, 8, 9], fill=accent + (255,))
    elif piece == 'leggings':
        d.rectangle([3, 2, 12, 5], fill=MAG)
        d.rectangle([3, 5, 6, 14], fill=MAG)
        d.rectangle([9, 5, 12, 14], fill=MAG)
        light(img, pal)
        d.line([(3, 3), (12, 3)], fill=accent + (255,))
    else:
        d.rectangle([2, 8, 6, 13], fill=MAG)
        d.rectangle([2, 12, 7, 14], fill=MAG)
        d.rectangle([9, 8, 13, 13], fill=MAG)
        d.rectangle([9, 12, 14, 14], fill=MAG)
        light(img, pal)
        d.point([(3, 9), (10, 9)], fill=accent + (255,))
    return outline(img)


def weapon_sprite(realm, pal, accent):
    img = mask()
    d = ImageDraw.Draw(img)
    wood, wood_d = (110, 76, 40, 255), (70, 46, 22, 255)
    gold = (230, 190, 70, 255)
    P = [c + (255,) for c in pal]
    A_ = accent + (255,)
    if realm == 'grove':                                     # Thornroot Blade: a green blade studded with thorns, a root hilt
        d.line([(4, 11), (13, 2)], fill=P[2], width=2)
        d.line([(5, 11), (13, 3)], fill=P[1])
        for (x, y) in [(7, 7), (9, 5), (11, 3), (6, 10), (10, 6)]:
            d.point((x - 1, y - 1), fill=P[3])
        d.line([(3, 9), (6, 12)], fill=wood)
        d.line([(1, 14), (4, 11)], fill=wood_d, width=2)
        d.point((8, 7), fill=A_)
    elif realm == 'skyreach':                                # Galecutter: a curved sabre of stormglass
        pts = [(3, 12), (6, 9), (9, 6), (11, 3), (12, 1)]
        d.line(pts, fill=P[2], width=2)
        d.line([(4, 12), (7, 9), (10, 6), (12, 3)], fill=P[3])
        d.line([(2, 10), (5, 13)], fill=gold)
        d.line([(1, 14), (3, 12)], fill=P[0], width=2)
        d.point((9, 5), fill=A_)
    elif realm == 'hollow':                                  # Soulbrand: a black blade with a molten core
        d.line([(4, 11), (13, 2)], fill=P[0], width=3)
        d.line([(5, 10), (12, 3)], fill=P[2])
        d.point((12, 3), fill=P[3])
        d.line([(2, 9), (6, 13)], fill=(60, 60, 70, 255), width=2)
        d.line([(1, 14), (3, 12)], fill=wood_d, width=2)
    elif realm == 'drowned':                                 # Undertow Fang: a hooked fang on a coral grip
        d.line([(4, 11), (9, 6), (12, 4), (13, 2), (12, 1)], fill=P[3], width=2)
        d.line([(5, 11), (10, 6), (12, 5)], fill=P[2])
        d.point((11, 1), fill=P[3])
        d.line([(2, 9), (5, 12)], fill=P[1], width=2)
        d.line([(1, 14), (3, 12)], fill=(200, 90, 110, 255), width=2)
    elif realm == 'pale':                                    # Hushblade: a thin white blade, ice-blue edge
        d.line([(4, 11), (14, 1)], fill=P[3], width=1)
        d.line([(5, 11), (14, 2)], fill=P[2], width=1)
        d.line([(3, 10), (5, 12)], fill=P[1])
        d.line([(1, 14), (3, 12)], fill=P[0], width=2)
        d.point((13, 2), fill=A_)
    elif realm == 'scarlet':                                 # Glass Reaper: a scythe of red glass on a long haft
        d.line([(2, 14), (11, 3)], fill=wood, width=1)
        d.line([(3, 14), (12, 3)], fill=wood_d, width=1)
        d.line([(11, 2), (7, 1), (3, 2), (1, 4)], fill=P[2], width=2)
        d.line([(10, 3), (6, 2), (3, 3)], fill=P[3])
        d.point((11, 3), fill=gold)
    elif realm == 'clockwork':                               # Second Hand: a rapier shaped like a clock hand
        d.line([(4, 11), (13, 2)], fill=P[2], width=1)
        d.line([(5, 11), (14, 2)], fill=P[3], width=1)
        d.polygon([(12, 1), (14, 1), (14, 3)], fill=P[3])
        d.ellipse([2, 9, 6, 13], outline=gold)
        d.line([(1, 14), (3, 12)], fill=P[0], width=2)
        d.point((4, 11), fill=A_)
    else:                                                    # Spore Lash: a mace-headed puffball on a root stem
        d.line([(2, 13), (9, 6)], fill=(200, 186, 160, 255), width=2)
        d.ellipse([8, 1, 14, 7], fill=P[2])
        d.ellipse([9, 2, 12, 5], fill=P[3])
        for (x, y) in [(10, 6), (13, 4), (9, 3)]:
            d.point((x, y), fill=(255, 240, 250, 255))
        d.point((11, 4), fill=A_)
    return outline(img)


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


def ore_texture(base, crystal, glow, seed):
    r = random.Random(seed)
    img = Image.new('RGBA', (16, 16))
    px = img.load()
    for x in range(16):
        for y in range(16):
            v = r.randint(-9, 9)
            px[x, y] = tuple(max(0, min(255, c + v)) for c in base) + (255,)
    d = ImageDraw.Draw(img)
    for (x, y) in [(3, 3), (10, 2), (6, 9), (12, 11), (2, 12)]:
        d.polygon([(x, y + 2), (x + 1, y), (x + 3, y + 1), (x + 2, y + 3)], fill=crystal + (255,))
        d.point((x + 1, y + 1), fill=glow + (255,))
    return img


# =========================================================================================== worn armor textures
def armor_layers(realm, kit):
    pal, accent = kit['palette'], kit['accent']
    for layer in (1, 2):
        src = Image.open(f'{ARM}/aurelian_layer_{layer}.png').convert('RGBA')
        out = src.copy()
        sp, po = src.load(), out.load()
        lum = [(sp[x, y][0] * 0.3 + sp[x, y][1] * 0.59 + sp[x, y][2] * 0.11) for x in range(src.width) for y in range(src.height) if sp[x, y][3]]
        hi = sorted(lum)[int(len(lum) * 0.93)] if lum else 255
        rnd = random.Random(sum(map(ord, realm)) + layer)
        for x in range(src.width):
            for y in range(src.height):
                r_, g_, b_, a = sp[x, y]
                if not a:
                    continue
                L = (r_ * 0.3 + g_ * 0.59 + b_ * 0.11) / 255.0
                idx = min(3, int(L * 4.2))
                c = pal[idx]
                if L * 255 >= hi:
                    c = accent
                n = rnd.randint(-8, 8)
                po[x, y] = tuple(max(0, min(255, v + n)) for v in c) + (a,)
        save(out, f'{ARM}/{kit["armor"]}_layer_{layer}.png')


# =========================================================================================== write everything
def item_model(name, parent='minecraft:item/generated'):
    write(f'{A}/models/item/{name}.json', {'parent': parent, 'textures': {'layer0': f'aurelia:item/{name}'}})


lang_p = f'{A}/lang/en_us.json'
lang = json.load(open(lang_p, encoding='utf-8'))
ARMOR_SHAPES = {'helmet': ['MMM', 'M M'], 'chestplate': ['M M', 'MMM', 'MMM'], 'leggings': ['MMM', 'M M', 'M M'], 'boots': ['M M', 'M M']}
spawns = {}
for realm in REALMS:
    k = KIT[realm]
    pal, accent = k['palette'], k['accent']
    for i, piece in enumerate(PIECES):
        name = f'{k["armor"]}_{piece}'
        save(armor_sprite(piece, pal, accent), f'{ITEM}/{name}.png')
        item_model(name)
        lang[f'item.aurelia.{name}'] = f'{k["armor_name"]} {piece.title()}'
        write(f'{D}/recipes/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': 'equipment', 'pattern': ARMOR_SHAPES[piece],
                                           'key': {'M': {'item': f'aurelia:{k["material"]}'}}, 'result': {'item': f'aurelia:{name}'}})
    armor_layers(realm, k)
    w = k['weapon']
    save(weapon_sprite(realm, pal, accent), f'{ITEM}/{w}.png')
    item_model(w, 'minecraft:item/handheld')
    lang[f'item.aurelia.{w}'] = k['weapon_name']
    lang[f'item.aurelia.{w}.power'] = k['weapon_power']
    write(f'{D}/recipes/{w}.json', {'type': 'minecraft:crafting_shaped', 'category': 'equipment', 'pattern': ['M', 'B', 'S'],
                                    'key': {'M': {'item': f'aurelia:{k["material"]}'}, 'B': {'item': f'aurelia:{k["block"]}'},
                                            'S': {'item': 'minecraft:stick'}}, 'result': {'item': f'aurelia:{w}'}})
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
    lang[f'item.aurelia.armor_bonus.{k["armor"]}'] = 'Full set: ' + k['bonus']
    lang[f'item.aurelia.{f}.power'] = k['food_power']

# ---- the two new ores
ORES = {'chronite_ore': ((60, 58, 66), (170, 90, 255), (240, 210, 255), 'chronite_shard', 'Chronite Ore'),
        'bloomspore_ore': ((84, 84, 90), (210, 70, 200), (255, 200, 245), 'bloomspore', 'Bloomspore Ore')}
for ore, (base, crys, glow, drop, title) in ORES.items():
    save(ore_texture(base, crys, glow, sum(map(ord, ore))), f'{BLK}/{ore}.png')
    write(f'{A}/blockstates/{ore}.json', {'variants': {'': {'model': f'aurelia:block/{ore}'}}})
    write(f'{A}/models/block/{ore}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{ore}'}})
    write(f'{A}/models/item/{ore}.json', {'parent': f'aurelia:block/{ore}'})
    lang[f'block.aurelia.{ore}'] = title
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
                   (f'{MC}/tags/items/freeze_immune_wearables.json', [f'aurelia:rime_{p}' for p in PIECES])]:
    j = json.load(open(tag)) if os.path.exists(tag) else {'replace': False, 'values': []}
    j['values'] += [x for x in extra if x not in j['values']]
    write(tag, j)
json.dump(lang, open(lang_p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('realm kits written:', len(REALMS) * (len(PIECES) + 2), 'items, 2 ores, 8 creatures')
