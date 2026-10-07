"""The Arsenals of the Tenfold Seal: every realm's armor, weapon, three tools, ore and two materials, plus the Unmaker's Genesis
arsenal. Writes the sprites (arsenal_art.py), item models, names, recipes and tags, and clears out what the arsenals replaced.
Definitions: kit_data.ARSENAL and kit_data.GENESIS. Worn armor models: gen_armor.py."""
import json
import os

import numpy as np

import arsenal_art as art
import paths
from kit_data import ARSENAL, GENESIS, KIT, PIECES, REALMS, SPECIAL_LORE, SPECIAL_RECIPE, TOOLS

A = paths.RES + '/assets/aurelia'
D = paths.RES + '/data/aurelia'
MC = paths.RES + '/data/minecraft'
GONE_WEAPONS = ['thornroot_blade', 'galecutter', 'soulbrand', 'undertow_fang', 'hushblade', 'glass_reaper', 'second_hand', 'spore_lash',
                'worldbreaker']
GONE = GONE_WEAPONS + ['unmade_heart'] + [f'unmade_{p}' for p in PIECES]
ARMOR_SHAPES = {'helmet': ['MMM', 'M M'], 'chestplate': ['M M', 'MMM', 'MMM'], 'leggings': ['MMM', 'M M', 'M M'], 'boots': ['M M', 'M M']}
TOOL_SHAPES = {'pickaxe': ['MMM', ' S ', ' S '], 'axe': ['MM', 'MS', ' S'], 'shovel': ['M', 'S', 'S']}
RING, RING_PATTERN = 'ABCDEFGH', ['ABC', 'HUD', 'GFE']


def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w', encoding='utf-8'), indent=2)


def save(img, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)


def remove(path):
    if os.path.exists(path):
        os.remove(path)


# ------------------------------------------------------------------------------------------------ holding a 64-pixel weapon
def _rot(x, y, z):
    x, y, z = np.radians([x, y, z])
    Rx = np.array([[1, 0, 0], [0, np.cos(x), -np.sin(x)], [0, np.sin(x), np.cos(x)]])
    Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    Rz = np.array([[np.cos(z), -np.sin(z), 0], [np.sin(z), np.cos(z), 0], [0, 0, 1]])
    return Rx @ Ry @ Rz                                             # JOML rotationXYZ, as ItemTransform uses


def held_big(k3=1.55, k1=1.3, grip=(6, 58)):
    """Vanilla's handheld transforms, scaled up by k, with the translation moved so the grip stays in the hand.
    A vertex v (0..1) lands at T + R S (v - 0.5); keeping the grip fixed gives T = T0 + (s0 - s) R (g - 0.5)."""
    g = np.array([grip[0] / 64, 1 - grip[1] / 64, 0.5]) - 0.5
    out = {}
    for key, rot, t0, s0, k in [('thirdperson_righthand', (0, -90, 55), (0, 4.0, 0.5), 0.85, k3),
                                ('firstperson_righthand', (0, -90, 25), (1.13, 3.2, 1.13), 0.68, k1)]:
        s = s0 * k
        T = np.array(t0) / 16 + (s0 - s) * (_rot(*rot) @ g)
        t = [round(float(v) * 16, 2) for v in T]
        out[key] = {'rotation': list(rot), 'translation': t, 'scale': [round(s, 3)] * 3}
        out[key.replace('right', 'left')] = {'rotation': [rot[0], -rot[1], -rot[2]], 'translation': t, 'scale': [round(s, 3)] * 3}
    return out


def item_model(name, parent='minecraft:item/generated', display=None):
    m = {'parent': parent, 'textures': {'layer0': f'aurelia:item/{name}'}}
    if display:
        m['display'] = display
    write(f'{A}/models/item/{name}.json', m)


def shaped(result, pattern, key, count=1):
    return {'type': 'minecraft:crafting_shaped', 'category': 'equipment', 'pattern': pattern,
            'key': {k: {'item': v} for k, v in key.items()}, 'result': {'item': result, 'count': count}}


def ring(result, items, centre, count=1):
    key = {RING[i]: it for i, it in enumerate(items)}
    key['U'] = centre
    return shaped(result, RING_PATTERN, key, count)


def main():
    lang_p = f'{A}/lang/en_us.json'
    lang = json.load(open(lang_p, encoding='utf-8'))
    for x in GONE:                                                 # what the arsenals replaced
        for p in (f'{A}/models/item/{x}.json', f'{A}/textures/item/{x}.png', f'{D}/recipes/{x}.json', f'{A}/textures/models/armor/{x}.png'):
            remove(p)
        for suffix in ('', '.power', '.ability', '.lore'):
            lang.pop(f'item.aurelia.{x}{suffix}', None)
    for k in [k for k in lang if k.startswith('item.aurelia.armor_bonus.unmade')]:
        lang.pop(k)
    big = held_big()
    rows = [(r, ARSENAL[r], KIT[r]['armor']) for r in REALMS] + [('genesis', GENESIS, 'genesis')]
    for realm, a, armor in rows:
        metal = f'aurelia:{a["metal"]}'
        # ---- weapon
        w = a['weapon']
        save(art.WEAPONS[realm][1]().render(), f'{A}/textures/item/{w}.png')
        item_model(w, 'minecraft:item/handheld', big)
        lang[f'item.aurelia.{w}'] = a['weapon_name']
        if realm != 'genesis':
            k = KIT[realm]
            lang[f'item.aurelia.{w}.power'] = k['weapon_power']
            lang[f'item.aurelia.{w}.ability'] = k['weapon_ability']
            write(f'{D}/recipes/{w}.json', shaped(f'aurelia:{w}', [' MM', ' XM', 'S  '],
                                                   {'M': metal, 'X': f'aurelia:{a["special"]}', 'S': 'minecraft:stick'}))
        # ---- armor
        for piece in PIECES:
            name = f'{armor}_{piece}'
            save(art.ICONS[piece](realm).render(), f'{A}/textures/item/{name}.png')
            item_model(name)
            lang[f'item.aurelia.{name}'] = f'{a["armor_name"]} {piece.title()}'
            write(f'{D}/recipes/{name}.json', shaped(f'aurelia:{name}', ARMOR_SHAPES[piece], {'M': metal}))
        # ---- tools
        for kind, fn in zip(TOOLS, (art.pickaxe, art.axe, art.shovel)):
            name = f'{a["tool"]}_{kind}'
            save(fn(realm).render(), f'{A}/textures/item/{name}.png')
            item_model(name, 'minecraft:item/handheld')
            lang[f'item.aurelia.{name}'] = f'{a["tool_name"]} {kind.title()}'
            key = {'M': metal, 'S': 'minecraft:stick'}
            write(f'{D}/recipes/{name}.json', shaped(f'aurelia:{name}', TOOL_SHAPES[kind], key))
        lang[f'item.aurelia.{a["metal"]}'] = a['metal_name']
        lang[f'item.aurelia.{a["special"]}'] = a['special_name']
        if realm == 'genesis':
            continue
        # ---- ore, raw drop, storage block: same ids as before, new names and art
        lang[f'block.aurelia.{a["ore"]}'] = a['ore_name']
        lang[f'item.aurelia.{a["raw"]}'] = a['raw_name']
        lang[f'block.aurelia.{k["block"]}'] = a['block_name']
        save(art.ore(a['ore']).render(outline=False, halo=False), f'{A}/textures/block/{a["ore"]}.png')
        # ---- the metal: smelted from the raw drop, or the raw drop alloyed with gold or iron
        raw = f'aurelia:{a["raw"]}'
        if a['metal_from'] == 'smelt':
            for kind, t in (('smelting', 200), ('blasting', 100)):
                write(f'{D}/recipes/{a["metal"]}_from_{kind}.json', {'type': f'minecraft:{kind}', 'category': 'misc', 'ingredient': {'item': raw},
                                                                     'result': f'aurelia:{a["metal"]}', 'experience': 1.0, 'cookingtime': t})
        elif a['metal_from'] in ('gold', 'iron'):
            write(f'{D}/recipes/{a["metal"]}.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                                     'ingredients': [{'item': raw}, {'item': raw}, {'item': f'minecraft:{a["metal_from"]}_ingot'}],
                                                     'result': {'item': f'aurelia:{a["metal"]}'}})
        # ---- the special
        sp = a['special']
        if sp in SPECIAL_RECIPE:
            write(f'{D}/recipes/{sp}.json', shaped(f'aurelia:{sp}', [' M ', 'MXM', ' M '], {'M': metal, 'X': SPECIAL_RECIPE[sp]}))
        elif sp == 'living_root_fiber':
            write(f'{D}/recipes/{sp}.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                             'ingredients': [{'item': 'minecraft:vine'}, {'item': 'minecraft:vine'}, {'item': raw}],
                                             'result': {'item': f'aurelia:{sp}', 'count': 2}})
    # ---- every material sprite (realm metals and specials, renamed raw drops, Genesis)
    for mid, fn in art.MATERIALS.items():
        save(fn().render(), f'{A}/textures/item/{mid}.png')
        item_model(mid)
    for mid, text in SPECIAL_LORE.items():
        lang[f'item.aurelia.{mid}.lore'] = text
    # ---- Genesis: ingots from a Fractured Genesis and every realm's metal; Worldsunder from every realm's weapon
    G = GENESIS
    write(f'{D}/recipes/genesis_ingot.json', ring('aurelia:genesis_ingot', [f'aurelia:{ARSENAL[r]["metal"]}' for r in REALMS],
                                                  'aurelia:fractured_genesis', 4))
    write(f'{D}/recipes/{G["weapon"]}.json', ring(f'aurelia:{G["weapon"]}', [f'aurelia:{ARSENAL[r]["weapon"]}' for r in REALMS],
                                                  'aurelia:fractured_genesis'))
    lang[f'item.aurelia.{G["weapon"]}.power'] = G['weapon_power']
    lang[f'item.aurelia.{G["weapon"]}.ability'] = G['weapon_ability']
    lang[f'item.aurelia.{G["weapon"]}.lore'] = 'Eight weapons, melted into one by the thing that broke them.'
    lang['item.aurelia.armor_bonus.genesis'] = 'Full set, Genesis:'
    for i, line in enumerate(G['bonus']):
        lang[f'item.aurelia.armor_bonus.genesis.{i}'] = line
    for realm in REALMS:
        lang[f'item.aurelia.armor_bonus.{KIT[realm]["armor"]}'] = 'Full set: ' + KIT[realm]['bonus']
    json.dump(lang, open(lang_p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    # ---- tags
    tag = f'{MC}/tags/items/freeze_immune_wearables.json'
    j = json.load(open(tag)) if os.path.exists(tag) else {'replace': False, 'values': []}
    want = [f'aurelia:rime_{p}' for p in PIECES] + [f'aurelia:genesis_{p}' for p in PIECES]
    j['values'] = [v for v in j['values'] if not v.startswith('aurelia:unmade_')] + [v for v in want if v not in j['values']]
    write(tag, j)
    print('arsenals written:', len(rows), 'rows,', len(rows) * (1 + len(PIECES) + len(TOOLS)), 'gear items,', len(art.MATERIALS), 'materials')


if __name__ == '__main__':
    main()
