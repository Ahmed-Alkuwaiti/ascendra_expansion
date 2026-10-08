"""The extras: supplementary content round the main quest.

  advancements        a full tree: every realm entered, every realm's lieutenants and Warden, the crowns, the relics, the
                      Heralds, the Unmaker, the Hand of Genesis, each realm's armour and weapon, and a few long hunts
  paintings           twelve: the eight Wardens, the Unmaker, the Last Realm, the Shattered Crown and the Convergence Gate
  Aurelian Bestiary   a book of every Warden and lieutenant, opening at the realm you stand in (world/BestiaryPages.java)
  Wayfinder's Lodestar points to the nearest citadel, or in a realm to the nearest standing lair, then the altar
  realm masonry       for each of the eight realms: bricks, brick stairs, brick slab, a carved sigil stone and a sigil lamp

Writes registry/ExtraContent.java, world/BestiaryPages.java, and every texture, model, blockstate, loot table, recipe, tag,
advancement and lang line those need.
"""
import json
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw

import paths
from lieutenants import LIEUTENANTS, of_realm, stats

J = paths.JAVA
A = paths.RES + '/assets/aurelia'
D = paths.RES + '/data/aurelia'
MC = paths.RES + '/data/minecraft'
REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']
NAME = {'grove': 'The Gaudy Grove', 'skyreach': 'Skyreach', 'hollow': 'The Hollow', 'drowned': 'The Drowned Expanse', 'pale': 'The Pale Reach',
        'scarlet': 'The Scarlet Waste', 'clockwork': 'The Clockwork Rift', 'mycelial': 'The Mycelial Deep', 'last': 'The Last Realm'}
SHORT = {'grove': 'Grove', 'skyreach': 'Skyreach', 'hollow': 'Hollow', 'drowned': 'Drowned', 'pale': 'Pale', 'scarlet': 'Scarlet',
         'clockwork': 'Clockwork', 'mycelial': 'Mycelial'}
WARDEN = {'grove': 'mossback_titan', 'skyreach': 'tempest_roc', 'hollow': 'hollow_king', 'drowned': 'vorath', 'pale': 'white_silence',
          'scarlet': 'kharzul', 'clockwork': 'vexor', 'mycelial': 'bloom_mother'}
ARMOR = {'grove': 'verdant', 'skyreach': 'stormglass', 'hollow': 'emberheart', 'drowned': 'tidestone', 'pale': 'rime', 'scarlet': 'sunglass',
         'clockwork': 'chronite', 'mycelial': 'bloomspore'}
WEAPON = {'grove': 'rootbreaker', 'skyreach': 'stormpiercer', 'hollow': 'soulcleaver', 'drowned': 'tidebinder', 'pale': 'silent_requiem',
          'scarlet': 'venomfangs', 'clockwork': 'hourshatter', 'mycelial': 'sporethorn'}
RELICS = ['rootbound_heart', 'storm_talon', 'sovereign_hand', 'abyssal_fang', 'frozen_voice', 'glass_stinger', 'chronal_eye', 'living_spore']
STONE = {'grove': (92, 128, 78), 'skyreach': (214, 222, 232), 'hollow': (54, 48, 60), 'drowned': (58, 124, 116), 'pale': (196, 214, 236),
         'scarlet': (166, 62, 52), 'clockwork': (74, 68, 94), 'mycelial': (186, 150, 178)}
GLOW = {'grove': (120, 255, 80), 'skyreach': (120, 220, 255), 'hollow': (255, 140, 40), 'drowned': (80, 255, 220), 'pale': (210, 240, 255),
        'scarlet': (255, 80, 90), 'clockwork': (200, 120, 255), 'mycelial': (255, 90, 230)}
METAL = {'grove': 'verdantite_ingot', 'skyreach': 'aetherium_ingot', 'hollow': 'soulsteel_ingot', 'drowned': 'tidesteel_ingot', 'pale': 'rime_crystal',
         'scarlet': 'sunglass_shard', 'clockwork': 'chronite_ingot', 'mycelial': 'mycelial_ingot'}
MAPCOL = {'grove': 'COLOR_GREEN', 'skyreach': 'QUARTZ', 'hollow': 'COLOR_BLACK', 'drowned': 'WARPED_NYLIUM', 'pale': 'ICE', 'scarlet': 'COLOR_RED',
          'clockwork': 'COLOR_PURPLE', 'mycelial': 'COLOR_MAGENTA'}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=2)


def jstr(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'


# ================================================================================================ the Bestiary
ABILITY = {
    'SLAM': 'Slam: a shockwave that hurls everyone close by up and away.',
    'CHARGE': 'Charge: a straight rush at you. Step aside.',
    'LEAP': 'Leap: it jumps onto you from afar.',
    'BOLT': 'Bolt: a bolt of its element. Break line of sight.',
    'VOLLEY': 'Volley: a bolt at everyone within 22 blocks.',
    'FIREBALLS': 'Fireballs: three at a time.',
    'SKULLS': 'Skulls: two wither skulls.',
    'SUMMON': 'Summon: it calls its realm\'s guards.',
    'PULL': 'Pull: drags everyone within 16 blocks to it, slowed.',
    'NOVA': 'Nova: a burst round it, 8 blocks wide.',
    'BLINK': 'Blink: vanishes and strikes from behind you.',
    'ZONE': 'Zone: a lingering cloud of its curse where you stand.',
    'STORM': 'Storm: lightning on everyone within 20 blocks.',
    'ROOT': 'Root: you cannot move or jump for three seconds.',
    'BULWARK': 'Bulwark: a shield for four seconds. Wait it out.',
}
ELEMENT = {'grove': 'poison and slowness', 'skyreach': 'levitation', 'hollow': 'fire and wither', 'drowned': 'slowness, and it drowns you',
           'pale': 'freezing and slowness', 'scarlet': 'fire and weakness', 'clockwork': 'slowness and mining fatigue',
           'mycelial': 'poison and nausea', 'last': 'darkness and wither'}


def strip_html(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s.replace('&middot;', '-'))).strip()


def paginate(text, limit=190):
    """Split text into book pages at word boundaries, keeping paragraph breaks."""
    pages, cur = [], ''
    for para in text.split('\n\n'):
        words = para.split(' ')
        chunk = ''
        for w in words:
            if len(cur) + len(chunk) + len(w) + 1 > limit:
                if cur.strip() or chunk.strip():
                    pages.append((cur + chunk).strip())
                cur, chunk = '', ''
            chunk += (' ' if chunk else '') + w
        cur += chunk + '\n\n'
    if cur.strip():
        pages.append(cur.strip())
    return pages


def bestiary():
    import build_gallery
    import finale_page
    R = {r['id']: r for r in build_gallery.R}
    pages = ['\u00a7lTHE AURELIAN BESTIARY\u00a7r\n\nEvery Warden, and every lieutenant who guards one.\n\nOpened inside a realm, this book turns to that '
             'realm.\n\n\u00a78- The Last Archivist']
    index = '\u00a7lContents\u00a7r\n'
    starts = {}
    body = []
    for realm in REALMS + ['last']:
        sec = []
        if realm == 'last':
            sec.append(f'\u00a7l{NAME[realm].upper()}\u00a7r\n\n\u00a78The Unmaker\u00a7r\n12,000 health\n\n'
                       f'Two Heralds stand before it. It will not wake while either lives.')
            sec += paginate(strip_html(finale_page.UNMAKER_TEXT))
        else:
            r = R[realm]
            sec.append(f'\u00a7l{NAME[realm].upper()}\u00a7r\n\n\u00a78Warden\u00a7r\n{r["boss_name"]}\n{r["hp"]:,} health\n\n'
                       f'Three lieutenants stand before it. It will not wake while any lives.')
            text = f'{r["boss_desc"]}\n\n\u00a7lGimmick: {r["gimmick"]}\u00a7r\n{r["gimmick_desc"]}'
            if r.get('attacks'):
                text += f'\n\n\u00a7lAttacks\u00a7r\n{r["attacks"]}'
            sec += paginate(text)
        for lt in of_realm(realm):
            hp, dmg = stats(lt)
            sec.append(f'\u00a7l{lt["name"]}\u00a7r\n\u00a78{lt["title"]}\u00a7r\n\n{hp:,} health, hits for {dmg}\n'
                       f'Its touch brings {ELEMENT[realm]}.\n\n{lt["lore"]}')
            sec += paginate('\n\n'.join(ABILITY[a] for a in lt['abilities']) + '\n\nAt half health it enrages: faster, and its abilities come quicker.'
                            ' No blow takes more than 6% of its health.')
        starts[realm] = len(body)
        body += sec
        index += f'\n{NAME[realm]}'
    off = len(pages) + 1
    pages.append(index)
    starts = {k: v + off for k, v in starts.items()}
    pages += body
    rows = ',\n'.join('            ' + jstr(p) for p in pages)
    srows = '\n'.join(f'            case "{k}" -> {v};' for k, v in starts.items())
    open(f'{J}/world/BestiaryPages.java', 'w').write(f'''package com.aurelia.world;

/** GENERATED by gen_extras.py from the gallery text and tools/lieutenants.py. The Aurelian Bestiary's pages. */
public final class BestiaryPages {{
    private BestiaryPages() {{}}

    public static final String[] PAGES = {{
{rows}
    }};

    /** The page each realm's section starts on (0-based), so the book opens where you stand. */
    public static int start(String realm) {{
        return switch (realm) {{
{srows}
            default -> 0;
        }};
    }}
}}
''')
    return len(pages)


# ================================================================================================ textures
def mat(rgb, glow=False, grain=None):
    import pixelart
    return pixelart.Mat(rgb, glow=glow, grain=grain)


def tex_bricks(realm):
    from pixelart import Sprite
    s = Sprite(16, 300 + REALMS.index(realm))
    base = STONE[realm]
    s.rect(-1, -1, 17, 17, mat(tuple(int(c * 0.45) for c in base)))
    for row in range(4):
        y0 = row * 4
        off = 4 if row % 2 else 0
        for k in range(-1, 3):
            x0 = k * 8 + off
            s.rect(x0 + 0.5, y0 + 0.5, x0 + 7.5, y0 + 3.5, mat(base, grain='speckle'))
    return s.render(outline=False, halo=False)


def tex_sigil(realm):
    from pixelart import Sprite
    s = Sprite(16, 320 + REALMS.index(realm))
    base = STONE[realm]
    s.rect(-1, -1, 17, 17, mat(tuple(int(c * 0.5) for c in base)))
    s.rect(1, 1, 15, 15, mat(base, grain='speckle'))
    s.rect(3, 3, 13, 13, mat(tuple(int(c * 0.7) for c in base)))
    s.gem(8, 8, 4.2, mat(GLOW[realm], glow=True))
    s.gem(8, 8, 1.8, mat(tuple(min(255, c + 60) for c in GLOW[realm]), glow=True))
    for (x, y) in [(2.5, 2.5), (13.5, 2.5), (2.5, 13.5), (13.5, 13.5)]:
        s.gem(x, y, 1.3, mat(GLOW[realm], glow=True))
    return s.render(outline=False, halo=False)


def tex_lamp(realm):
    from pixelart import Sprite
    s = Sprite(16, 340 + REALMS.index(realm))
    base = STONE[realm]
    s.rect(-1, -1, 17, 17, mat(tuple(int(c * 0.5) for c in base)))
    s.rect(2, 2, 14, 14, mat(GLOW[realm], glow=True))
    s.rect(7, 1, 9, 15, mat(tuple(int(c * 0.6) for c in base)))
    s.rect(1, 7, 15, 9, mat(tuple(int(c * 0.6) for c in base)))
    s.gem(8, 8, 2.2, mat(tuple(min(255, c + 70) for c in GLOW[realm]), glow=True))
    return s.render(outline=False, halo=False)


def tex_items():
    from pixelart import Sprite
    s = Sprite(16, 401)                                                  # the Lodestar: a gold rim, a dark face, a violet needle
    s.ellipse(8, 8, 7, 7, 'gold')
    s.ellipse(8, 8, 5.4, 5.4, 'abyss')
    s.line((4, 12), (12, 4), 1.6, 'void_p', 0.6)
    s.line((4, 12), (8, 8), 1.6, 'white')
    s.gem(8, 8, 1.4, 'star')
    for (x, y) in [(8, 1.5), (14.5, 8), (8, 14.5), (1.5, 8)]:
        s.gem(x, y, 1.0, 'gem_v')
    s.render().save(f'{A}/textures/item/wayfinders_lodestar.png')
    b = Sprite(16, 402)                                                  # the Bestiary: black leather, gold corners, a violet eye
    b.rect(2, 1, 14, 15, 'black')
    b.rect(2, 1, 4, 15, 'leather')
    b.rect(12, 2, 14, 14, 'bone')
    for (x, y) in [(5, 2), (12, 2), (5, 13), (12, 13)]:
        b.rect(x - 1, y - 1, x + 1.2, y + 1.2, 'gold')
    b.ellipse(8.5, 8, 2.6, 1.8, 'gold')
    b.ellipse(8.5, 8, 1.6, 1.4, 'void_p')
    b.render().save(f'{A}/textures/item/aurelian_bestiary.png')


# ================================================================================================ paintings
def painterly(im, w, h):
    """A render squeezed to painting size: box-downsampled, posterised to a small palette, framed."""
    im = im.convert('RGB')
    im = im.resize((w * 4, h * 4), Image.LANCZOS).resize((w, h), Image.BOX)
    im = im.quantize(colors=40, method=Image.MEDIANCUT, dither=Image.NONE).convert('RGB')
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w - 1, h - 1], outline=(46, 32, 22))
    d.rectangle([1, 1, w - 2, h - 2], outline=(150, 112, 52))
    return im


def fit(im, W, H, bg):
    """Centre an RGBA render on a gradient of the realm's colours, filling the canvas."""
    top, bot = bg
    canvas = Image.new('RGB', (W, H))
    for y in range(H):
        f = y / H
        canvas.paste(tuple(int(top[i] * (1 - f) + bot[i] * f) for i in range(3)), (0, y, W, y + 1))
    im = im.crop(im.getbbox())
    im.thumbnail((int(W * 0.9), int(H * 0.9)), Image.LANCZOS)
    canvas = canvas.convert('RGBA')
    canvas.alpha_composite(im, ((W - im.width) // 2, H - im.height - int(H * 0.04)))
    return canvas


PAINTINGS = []                                                           # (id, title, w, h) in pixels


def paintings(gallery=None):
    import render_gallery as rg
    import render_models as rm
    os.makedirs(f'{A}/textures/painting', exist_ok=True)
    for realm in REALMS:
        key = WARDEN[realm]
        parts, tex, glow = rm.build(key)
        im, _ = rm.render(parts, tex, glow, -32, 10, size=700, alpha=True)
        w, h = (64, 48) if key in ('tempest_roc', 'vorath') else (48, 64) if key in ('white_silence', 'kharzul') else (64, 64)
        art = painterly(fit(im, w * 8, h * 8, rg.BG[realm]), w, h)
        art.save(f'{A}/textures/painting/{key}.png')
        PAINTINGS.append((key, None, w, h))
    parts, tex, glow = rm.build('unmaker')
    im, _ = rm.render(parts, tex, glow, -32, 8, size=800, alpha=True)
    painterly(fit(im, 512, 512, rg.LAST_BG), 64, 64).save(f'{A}/textures/painting/unmaker.png')
    PAINTINGS.append(('unmaker', None, 64, 64))
    scenes = [('the_last_realm', 'finale/last_realm.webp', 64, 64), ('the_shattered_crown', 'finale/last_crown.webp', 64, 48),
              ('the_convergence_gate', 'finale/gate_ext.webp', 48, 48)]
    for pid, src, w, h in scenes:
        if gallery and os.path.exists(f'{gallery}/{src}'):
            im = Image.open(f'{gallery}/{src}').convert('RGB')
            arr = np.asarray(im).astype(int)
            bgcol = arr[:, :1, :]                                        # each row's background is its left-edge colour
            diff = np.abs(arr - bgcol).sum(axis=2) > 40
            ys, xs = np.nonzero(diff)
            if len(xs):                                                  # crop to the subject, with a little air round it
                pad = int(0.04 * max(im.size))
                im = im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad), min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))
            iw, ih = im.size                                             # crop to the painting's aspect, then paint it
            t = w / h
            corner = im.getpixel((0, 0))
            if iw / ih > t:                                              # too wide: pad top and bottom with the background
                nh = int(iw / t)
                canvas = Image.new('RGB', (iw, nh), corner)
                canvas.paste(im, (0, (nh - ih) // 2))
            else:
                nw = int(ih * t)
                canvas = Image.new('RGB', (nw, ih), corner)
                canvas.paste(im, ((nw - iw) // 2, 0))
            im = canvas
            painterly(im, w, h).save(f'{A}/textures/painting/{pid}.png')
        PAINTINGS.append((pid, None, w, h))
    tag = f'{MC}/tags/painting_variant/placeable.json'
    dump(tag, {'replace': False, 'values': [f'aurelia:{p[0]}' for p in PAINTINGS]})


PAINT_TITLE = {'mossback_titan': 'Mossback, the Rot Crown', 'tempest_roc': 'The Tempest Roc', 'hollow_king': 'The Hollow King',
               'vorath': 'Vorath, the Tide Devourer', 'white_silence': 'The White Silence', 'kharzul': 'Kharzul, the Reaper',
               'vexor': 'Vexor, the Hour Unwound', 'bloom_mother': 'The Bloom Mother', 'unmaker': 'The Unmaker',
               'the_last_realm': 'The Last Realm', 'the_shattered_crown': 'The Shattered Crown', 'the_convergence_gate': 'The Convergence Gate'}


# ================================================================================================ blocks
def stairs_blockstate(m):
    """The vanilla stairs blockstate, every facing, half and shape."""
    rot = {'east': 0, 'south': 90, 'west': 180, 'north': 270}
    out = {}
    for facing in ('east', 'west', 'south', 'north'):
        for half in ('bottom', 'top'):
            for shape in ('straight', 'inner_left', 'inner_right', 'outer_left', 'outer_right'):
                model = m + ('_inner' if shape.startswith('inner') else '_outer' if shape.startswith('outer') else '')
                y = rot[facing]
                if shape in ('inner_left', 'outer_left'):
                    y = (y - 90) % 360
                if half == 'top' and shape != 'straight':
                    y = (y + 90) % 360
                v = {'model': model}
                if half == 'top':
                    v['x'] = 180
                if y:
                    v['y'] = y
                if half == 'top' or y:
                    v['uvlock'] = True
                out[f'facing={facing},half={half},shape={shape}'] = v
    return {'variants': out}


BLOCKS = []                                                              # (id, kind, realm)


def blocks():
    for realm in REALMS:
        b = f'{realm}_bricks'
        for bid, kind in [(b, 'cube'), (f'{realm}_brick_stairs', 'stairs'), (f'{realm}_brick_slab', 'slab'), (f'{realm}_sigil_stone', 'cube'),
                          (f'{realm}_sigil_lamp', 'lamp')]:
            BLOCKS.append((bid, kind, realm))
        tex_bricks(realm).save(f'{A}/textures/block/{b}.png')
        tex_sigil(realm).save(f'{A}/textures/block/{realm}_sigil_stone.png')
        tex_lamp(realm).save(f'{A}/textures/block/{realm}_sigil_lamp.png')
        for cube in (b, f'{realm}_sigil_stone', f'{realm}_sigil_lamp'):
            dump(f'{A}/models/block/{cube}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': f'aurelia:block/{cube}'}})
            dump(f'{A}/blockstates/{cube}.json', {'variants': {'': {'model': f'aurelia:block/{cube}'}}})
            dump(f'{A}/models/item/{cube}.json', {'parent': f'aurelia:block/{cube}'})
        t = {'bottom': f'aurelia:block/{b}', 'top': f'aurelia:block/{b}', 'side': f'aurelia:block/{b}'}
        st = f'{realm}_brick_stairs'
        for suffix, parent in [('', 'stairs'), ('_inner', 'inner_stairs'), ('_outer', 'outer_stairs')]:
            dump(f'{A}/models/block/{st}{suffix}.json', {'parent': f'minecraft:block/{parent}', 'textures': t})
        dump(f'{A}/blockstates/{st}.json', stairs_blockstate(f'aurelia:block/{st}'))
        dump(f'{A}/models/item/{st}.json', {'parent': f'aurelia:block/{st}'})
        sl = f'{realm}_brick_slab'
        dump(f'{A}/models/block/{sl}.json', {'parent': 'minecraft:block/slab', 'textures': t})
        dump(f'{A}/models/block/{sl}_top.json', {'parent': 'minecraft:block/slab_top', 'textures': t})
        dump(f'{A}/blockstates/{sl}.json', {'variants': {'type=bottom': {'model': f'aurelia:block/{sl}'}, 'type=top': {'model': f'aurelia:block/{sl}_top'},
                                                         'type=double': {'model': f'aurelia:block/{b}'}}})
        dump(f'{A}/models/item/{sl}.json', {'parent': f'aurelia:block/{sl}'})
        # loot: each drops itself, a double slab two
        for bid, kind, _ in BLOCKS[-5:]:
            entry = {'type': 'minecraft:item', 'name': f'aurelia:{bid}'}
            if kind == 'slab':
                entry['functions'] = [{'function': 'minecraft:set_count', 'count': 2, 'add': False,
                                       'conditions': [{'condition': 'minecraft:block_state_property', 'block': f'aurelia:{bid}',
                                                       'properties': {'type': 'double'}}]}, {'function': 'minecraft:explosion_decay'}]
            dump(f'{D}/loot_tables/blocks/{bid}.json', {'type': 'minecraft:block', 'pools': [
                {'rolls': 1, 'bonus_rolls': 0, 'entries': [entry], 'conditions': [{'condition': 'minecraft:survives_explosion'}] if kind != 'slab' else []}]})
        # recipes: eight stone bricks round the realm's metal make eight bricks; the rest in the crafting grid and the stonecutter
        R = f'{D}/recipes'
        dump(f'{R}/{b}.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['SSS', 'SMS', 'SSS'],
                               'key': {'S': {'item': 'minecraft:stone_bricks'}, 'M': {'item': f'aurelia:{METAL[realm]}'}},
                               'result': {'item': f'aurelia:{b}', 'count': 8}})
        dump(f'{R}/{st}.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['B  ', 'BB ', 'BBB'],
                                'key': {'B': {'item': f'aurelia:{b}'}}, 'result': {'item': f'aurelia:{st}', 'count': 4}})
        dump(f'{R}/{sl}.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['BBB'],
                                'key': {'B': {'item': f'aurelia:{b}'}}, 'result': {'item': f'aurelia:{sl}', 'count': 6}})
        dump(f'{R}/{realm}_sigil_stone.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': ['S', 'S'],
                                               'key': {'S': {'item': f'aurelia:{sl}'}}, 'result': {'item': f'aurelia:{realm}_sigil_stone'}})
        dump(f'{R}/{realm}_sigil_lamp.json', {'type': 'minecraft:crafting_shaped', 'category': 'building', 'pattern': [' G ', 'GSG', ' G '],
                                              'key': {'G': {'item': 'minecraft:glowstone_dust'}, 'S': {'item': f'aurelia:{realm}_sigil_stone'}},
                                              'result': {'item': f'aurelia:{realm}_sigil_lamp'}})
        for out, n in [(st, 1), (sl, 2), (f'{realm}_sigil_stone', 1)]:
            dump(f'{R}/{out}_stonecutting.json', {'type': 'minecraft:stonecutting', 'ingredient': {'item': f'aurelia:{b}'},
                                                  'result': f'aurelia:{out}', 'count': n})
    # tags
    pick = f'{MC}/tags/blocks/mineable/pickaxe.json'
    t = json.load(open(pick))
    for bid, _, _ in BLOCKS:
        if f'aurelia:{bid}' not in t['values']:
            t['values'].append(f'aurelia:{bid}')
    dump(pick, t)
    for kind, tagname in [('stairs', 'stairs'), ('slab', 'slabs')]:
        vals = [f'aurelia:{bid}' for bid, k, _ in BLOCKS if k == kind]
        for folder in ('blocks', 'items'):
            p = f'{MC}/tags/{folder}/{tagname}.json'
            cur = json.load(open(p)) if os.path.exists(p) else {'replace': False, 'values': []}
            cur['values'] = sorted(set(cur['values']) | set(vals))
            dump(p, cur)


def items_data():
    tex_items()
    for iid in ('wayfinders_lodestar', 'aurelian_bestiary'):
        dump(f'{A}/models/item/{iid}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'aurelia:item/{iid}'}})
    R = f'{D}/recipes'
    dump(f'{R}/wayfinders_lodestar.json', {'type': 'minecraft:crafting_shaped', 'category': 'misc', 'pattern': [' A ', 'ACA', ' E '],
                                           'key': {'A': {'item': 'minecraft:amethyst_shard'}, 'C': {'item': 'minecraft:compass'},
                                                   'E': {'item': 'minecraft:ender_eye'}}, 'result': {'item': 'aurelia:wayfinders_lodestar'}})
    dump(f'{R}/aurelian_bestiary.json', {'type': 'minecraft:crafting_shapeless', 'category': 'misc',
                                         'ingredients': [{'item': 'minecraft:book'}, {'item': 'minecraft:ink_sac'}, {'item': 'minecraft:feather'},
                                                         {'item': 'minecraft:amethyst_shard'}], 'result': {'item': 'aurelia:aurelian_bestiary'}})
    # a Lodestar waits in every citadel's loot tables too? No: kept to the crafting grid, so the citadels' loot stays as balanced.
    dump(f'{D}/tags/worldgen/structure/citadels.json', {'replace': False, 'values': [
        'aurelia:rootbound_citadel', 'aurelia:stormwatch_citadel', 'aurelia:ashen_citadel', 'aurelia:tidewrack_citadel', 'aurelia:rimefast_citadel',
        'aurelia:sunscar_citadel', 'aurelia:paradox_keep', 'aurelia:spore_cathedral', 'aurelia:convergence_gate']})


# ================================================================================================ advancements
ADV = []


def adv(aid, parent, icon, title, desc, criteria, frame='task', xp=0, hidden=False, requirements=None):
    a = {'display': {'icon': {'item': icon}, 'title': {'text': title}, 'description': {'text': desc}, 'frame': frame,
                     'show_toast': True, 'announce_to_chat': True, 'hidden': hidden},
         'criteria': criteria}
    if parent:
        a['parent'] = f'aurelia:{parent}'
    else:
        a['display']['background'] = 'minecraft:textures/block/polished_blackstone_bricks.png'
    if requirements:
        a['requirements'] = requirements
    if xp:
        a['rewards'] = {'experience': xp}
    dump(f'{D}/advancements/{aid}.json', a)
    ADV.append(aid)


def kill(eid):
    return {'trigger': 'minecraft:player_killed_entity', 'conditions': {'entity': [
        {'condition': 'minecraft:entity_properties', 'entity': 'this', 'predicate': {'type': f'aurelia:{eid}'}}]}}


def has(*iids):
    return {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': [f'aurelia:{i}']} for i in iids]}}


def enter(dim):
    return {'trigger': 'minecraft:changed_dimension', 'conditions': {'to': f'aurelia:{dim}'}}


def advancements():
    import shutil
    if os.path.isdir(f'{D}/advancements'):
        shutil.rmtree(f'{D}/advancements')
    adv('root', None, 'aurelia:crown_of_aurelia', 'Aurelia: The Shattered Crown', 'Find a citadel. Wake its Waygate. Take back the crown.',
        {'start': {'trigger': 'minecraft:tick'}})
    adv('wayfinder', 'root', 'aurelia:wayfinders_lodestar', 'Which Way Is Doom?', 'Make a Wayfinder\'s Lodestar.', {'has': has('wayfinders_lodestar')})
    adv('bestiary', 'root', 'aurelia:aurelian_bestiary', 'Know Thine Enemy', 'Make the Aurelian Bestiary.', {'has': has('aurelian_bestiary')})
    prev = 'root'
    crowns = {'hollow': ('crown_of_aurelia', 'The Crown of Aurelia', 'Make the Crown from the first three shards.'),
              'scarlet': ('ascendant_crown', 'Ascendant', 'Set three more shards in the Ascendant Crown.'),
              'mycelial': ('eternal_crown', 'Eternal', 'Finish the Eternal Crown.')}
    for realm in REALMS:
        adv(f'enter_{realm}', prev, f'aurelia:{realm}_sigil_stone', f'Through the Waygate: {SHORT[realm]}', f'Step into {NAME[realm]}.', {'enter': enter(realm)})
        lts = of_realm(realm)
        adv(f'lieutenants_{realm}', f'enter_{realm}', 'aurelia:lair_seal', f'Lieutenants of {SHORT[realm]}',
            'Slay ' + ', '.join(l['name'] for l in lts[:-1]) + f' and {lts[-1]["name"]}.', {l['id']: kill(l['id']) for l in lts}, frame='goal', xp=100)
        adv(f'warden_{realm}', f'lieutenants_{realm}', f'aurelia:{WARDEN[realm]}_spawn_egg', f'{NAME[realm]} Falls',
            f'Defeat the Warden of {NAME[realm]}.', {'kill': kill(WARDEN[realm])}, frame='goal', xp=250)
        adv(f'armor_{realm}', f'enter_{realm}', f'aurelia:{ARMOR[realm]}_chestplate', f'Dressed for {SHORT[realm]}',
            f'Hold every piece of the {SHORT[realm]} armour.', {'set': has(*[f'{ARMOR[realm]}_{p}' for p in ('helmet', 'chestplate', 'leggings', 'boots')])})
        adv(f'weapon_{realm}', f'enter_{realm}', f'aurelia:{WEAPON[realm]}', WEAPON[realm].replace('_', ' ').title(),
            f'Forge the weapon of {NAME[realm]}.', {'has': has(WEAPON[realm])})
        prev = f'warden_{realm}'
        if realm in crowns:
            cid, title, desc = crowns[realm]
            adv(cid, prev, f'aurelia:{cid}', title, desc, {'has': has(cid)}, frame='challenge' if realm == 'mycelial' else 'goal', xp=500)
            prev = cid
    adv('eightfold_seal', 'eternal_crown', 'aurelia:chronal_eye', 'The Eightfold Seal', 'Hold all eight relics at once.',
        {r: has(r) for r in RELICS}, frame='challenge', xp=500)
    adv('enter_last', 'eightfold_seal', 'aurelia:realm_node', 'The End of Every World', 'Pass the Convergence Gate into the Last Realm.', {'enter': enter('last')},
        frame='goal')
    heralds = of_realm('last')
    adv('heralds', 'enter_last', 'aurelia:unmaking_anchor', 'The Heralds Silenced', 'Slay both Heralds of the Unmade.',
        {l['id']: kill(l['id']) for l in heralds}, frame='goal', xp=300)
    adv('unmaker', 'heralds', 'aurelia:unmaker_spawn_egg', 'Unmade', 'Defeat the Unmaker.', {'kill': kill('unmaker')}, frame='challenge', xp=1500)
    adv('hand_of_genesis', 'unmaker', 'aurelia:hand_of_genesis', 'The Worlds Are Yours', 'Take up the Hand of Genesis.', {'has': has('hand_of_genesis')},
        frame='challenge', xp=1000)
    adv('genesis_armor', 'hand_of_genesis', 'aurelia:genesis_chestplate', 'Genesis', 'Hold every piece of the Genesis armour.',
        {'set': has('genesis_helmet', 'genesis_chestplate', 'genesis_leggings', 'genesis_boots')}, frame='challenge', xp=500)
    # the long hunts
    adv('lieutenant_hunter', 'lieutenants_grove', 'aurelia:lair_seal', 'Lieutenant Hunter', 'Slay all twenty-six lieutenants.',
        {l['id']: kill(l['id']) for l in LIEUTENANTS}, frame='challenge', xp=1000)
    adv('tenfold_arsenal', 'weapon_grove', 'aurelia:worldsunder', 'Arsenals of the Tenfold Seal', 'Hold all eight realm weapons and Worldsunder.',
        {w: has(w) for w in list(WEAPON.values()) + ['worldsunder']}, frame='challenge', xp=750)
    adv('realm_mason', 'enter_grove', 'aurelia:grove_sigil_lamp', 'Mason of the Realms', 'Hold a sigil lamp from every realm.',
        {r: has(f'{r}_sigil_lamp') for r in REALMS}, frame='goal', xp=200)
    adv('all_realms', 'enter_mycelial', 'aurelia:waygate', 'Walker Between Worlds', 'Set foot in every realm, the Last included.',
        {r: enter(r) for r in REALMS + ['last']}, frame='challenge', xp=300)


# ================================================================================================ Java and lang
def java():
    bl = []
    for bid, kind, realm in BLOCKS:
        const = bid.upper()
        props = (f'BlockBehaviour.Properties.of().mapColor(MapColor.{MAPCOL[realm]}).strength(2.0f, 6.0f).requiresCorrectToolForDrops()'
                 f'.sound(SoundType.{"GLASS" if kind == "lamp" else "STONE"})' + ('.lightLevel(s -> 15)' if kind == 'lamp' else ''))
        if kind == 'stairs':
            ctor = f'new StairBlock(() -> {realm.upper()}_BRICKS.get().defaultBlockState(), {props})'
        elif kind == 'slab':
            ctor = f'new SlabBlock({props})'
        else:
            ctor = f'new Block({props})'
        bl.append(f'    public static final RegistryObject<Block> {const} = ModBlocks.BLOCKS.register("{bid}", () -> {ctor});')
        bl.append(f'    public static final RegistryObject<Item> {const}_ITEM = ModItems.ITEMS.register("{bid}", () -> new BlockItem({const}.get(), new Item.Properties()));')
    pt = [f'    public static final RegistryObject<PaintingVariant> PAINTING_{p[0].upper()} = PAINTINGS.register("{p[0]}", () -> new PaintingVariant({p[2]}, {p[3]}));'
          for p in PAINTINGS]
    tab = ', '.join([f'{b[0].upper()}_ITEM' for b in BLOCKS])
    open(f'{J}/registry/ExtraContent.java', 'w').write(f'''package com.aurelia.registry;

import com.aurelia.AureliaMod;
import com.aurelia.item.BestiaryItem;
import com.aurelia.item.WayfinderItem;
import java.util.List;
import net.minecraft.world.entity.decoration.PaintingVariant;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.Rarity;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;

/** GENERATED by gen_extras.py. The extras: realm masonry, the Wayfinder's Lodestar, the Aurelian Bestiary and the paintings. */
public final class ExtraContent {{
    private ExtraContent() {{}}

    public static final DeferredRegister<PaintingVariant> PAINTINGS = DeferredRegister.create(ForgeRegistries.PAINTING_VARIANTS, AureliaMod.MODID);

    public static final RegistryObject<Item> WAYFINDERS_LODESTAR = ModItems.ITEMS.register("wayfinders_lodestar",
            () -> new WayfinderItem(new Item.Properties().stacksTo(1).rarity(Rarity.RARE)));
    public static final RegistryObject<Item> AURELIAN_BESTIARY = ModItems.ITEMS.register("aurelian_bestiary",
            () -> new BestiaryItem(new Item.Properties().stacksTo(1).rarity(Rarity.UNCOMMON)));

{chr(10).join(bl)}

{chr(10).join(pt)}

    /** Touches the class so the registrations above happen before the registers fire. */
    public static void init() {{}}

    /** Everything here for the creative tab, in order. */
    public static List<RegistryObject<Item>> tabItems() {{
        return List.of(WAYFINDERS_LODESTAR, AURELIAN_BESTIARY, {tab});
    }}
}}
''')
    lang_p = f'{A}/lang/en_us.json'
    lang = json.load(open(lang_p, encoding='utf-8'))
    lang['item.aurelia.wayfinders_lodestar'] = "Wayfinder's Lodestar"
    lang['item.aurelia.wayfinders_lodestar.lore'] = 'Use it: in the overworld it finds a citadel; in a realm, the nearest standing lair.'
    lang['item.aurelia.aurelian_bestiary'] = 'The Aurelian Bestiary'
    lang['item.aurelia.aurelian_bestiary.lore'] = 'Every Warden and lieutenant. Opens at the realm you stand in.'
    for bid, kind, realm in BLOCKS:
        nice = {'cube': None, 'stairs': 'Brick Stairs', 'slab': 'Brick Slab', 'lamp': 'Sigil Lamp'}[kind]
        if kind == 'cube':
            nice = 'Bricks' if bid.endswith('_bricks') else 'Sigil Stone'
        lang[f'block.aurelia.{bid}'] = f'{SHORT[realm]} {nice}'
    for pid, _, _, _ in PAINTINGS:
        lang[f'painting.aurelia.{pid}.title'] = PAINT_TITLE[pid]
        lang[f'painting.aurelia.{pid}.author'] = 'The Last Archivist'
    json.dump(lang, open(lang_p, 'w', encoding='utf-8'), indent=2, ensure_ascii=False)


def main(gallery=None):
    n = bestiary()
    blocks()
    items_data()
    paintings(gallery)
    advancements()
    java()
    print(f'extras: bestiary {n} pages, {len(BLOCKS)} blocks, {len(PAINTINGS)} paintings, {len(ADV)} advancements')


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else None)
