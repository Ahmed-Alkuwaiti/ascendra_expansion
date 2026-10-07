"""The Unmaker's gear: the Heart of the Unmade (its drop), the Regalia of the Unmade armor and the Worldbreaker.
The 3D models live with the others (gen_armor.unmade, weapons.worldbreaker); this writes the heart's model, names and recipes.
Every recipe asks for the Heart and one piece of each of the eight realms, the same way the Convergence Gate asks for eight relics."""
import json

import paths
from kit_data import KIT, PIECES, REALMS, UNMADE
from relics import Model, styles_of, texture, json_elements, write_json, DISPLAY, ASSETS

A = paths.RES + '/assets/aurelia'
D = paths.RES + '/data/aurelia'
MC = paths.RES + '/data/minecraft'
RING = 'ABCDEFGH'                                                    # the eight realm slots round the centre, realm order
PATTERN = ['ABC', 'HUD', 'GFE']


def heart():
    """A black hole the size of a fist: three crossed blocks of nothing, a burning disc round its middle, a white point at the core."""
    m = Model('unmade_heart')
    m.box((5, 5, 5), (11, 11, 11), 'abyss')
    m.box((4, 6, 6), (12, 10, 10), 'abyss')
    m.box((6, 4, 6), (10, 12, 10), 'abyss')
    m.box((6, 6, 4), (10, 10, 12), 'abyss')
    m.ring((8, 8, 8), 6.2, 14, (1.6, 0.8, 1.6), 'accretion', 'xz')
    m.ring((8, 8, 8), 7.6, 18, (1.1, 0.6, 1.1), 'accretion3', 'xz')
    m.box((7.3, 7.3, 11.9), (8.7, 8.7, 12.3), 'accretion2')
    m.box((7.3, 7.3, 3.7), (8.7, 8.7, 4.1), 'accretion2')
    return m


def ring_recipe(result, items, category='equipment'):
    key = {RING[i]: {'item': it} for i, it in enumerate(items)}
    key['U'] = {'item': 'aurelia:' + UNMADE['material']}
    return {'type': 'minecraft:crafting_shaped', 'category': category, 'pattern': PATTERN, 'key': key, 'result': {'item': result}}


def write_all():
    m = heart()
    img, where = texture(styles_of(m), 990)
    img.save(f'{ASSETS}/textures/item/unmade_heart.png')
    write_json(f'{A}/models/item/unmade_heart.json', {'textures': {'t': 'aurelia:item/unmade_heart', 'particle': 'aurelia:item/unmade_heart'},
                                                      'display': DISPLAY, 'elements': json_elements(m.els, where)})
    lang_p = f'{A}/lang/en_us.json'
    lang = json.load(open(lang_p, encoding='utf-8'))
    lang['item.aurelia.unmade_heart'] = UNMADE['material_name']
    lang['item.aurelia.unmade_heart.lore'] = UNMADE['material_lore']
    blocks = [f'aurelia:{KIT[r]["block"]}' for r in REALMS]
    for piece in PIECES:
        name = f'unmade_{piece}'
        write_json(f'{A}/models/item/{name}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'aurelia:item/{name}'}})
        lang[f'item.aurelia.{name}'] = UNMADE['pieces'][piece]
        write_json(f'{D}/recipes/{name}.json', ring_recipe(f'aurelia:{name}', blocks))
    lang['item.aurelia.armor_bonus.unmade'] = 'Full set, the ' + UNMADE['armor_name'] + ':'
    for i, line in enumerate(UNMADE['bonus']):
        lang[f'item.aurelia.armor_bonus.unmade.{i}'] = line
    w = UNMADE['weapon']
    lang[f'item.aurelia.{w}'] = UNMADE['weapon_name']
    lang[f'item.aurelia.{w}.power'] = UNMADE['weapon_power']
    lang[f'item.aurelia.{w}.ability'] = UNMADE['weapon_ability']
    lang[f'item.aurelia.{w}.lore'] = 'Eight swords, melted into one by the thing that broke them.'
    write_json(f'{D}/recipes/{w}.json', ring_recipe(f'aurelia:{w}', [f'aurelia:{KIT[r]["weapon"]}' for r in REALMS]))
    json.dump(lang, open(lang_p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    tag = f'{MC}/tags/items/freeze_immune_wearables.json'
    j = json.load(open(tag))
    j['values'] += [f'aurelia:unmade_{p}' for p in PIECES if f'aurelia:unmade_{p}' not in j['values']]
    write_json(tag, j)


if __name__ == '__main__':
    write_all()
    print('unmade gear written')
