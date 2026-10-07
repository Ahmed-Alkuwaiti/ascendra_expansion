"""The eight realm greatswords as 3D item models (vanilla JSON elements, one rotation axis each, 0 / 22.5 / 45 degrees).

Every weapon is built along +y from a pommel at y = -16 to a tip near y = 32: three blocks of model, about two and a half in the hand.
The blade's flat side faces z; x is its width. Display transforms hold it by the grip in both hands' views and lay it on the
diagonal in the inventory. Uses the Model helper, swatch textures and element writer from relics.py.
"""
import math

from relics import Model, styles_of, texture, json_elements, write_json, ASSETS

C = 8.0          # the blade's centre line in x and z


def grip(m, wrap, pommel, gem, y0=-16, length=11):
    m.box((C - 2.2, y0, C - 2.2), (C + 2.2, y0 + 3, C + 2.2), pommel)
    m.box((C - 1.5, y0 + 0.5, C - 1.5), (C + 1.5, y0 + 2.5, C + 1.5), gem, 'y', 45)
    m.box((C - 1.2, y0 + 3, C - 1.2), (C + 1.2, y0 + 3 + length, C + 1.2), wrap)
    for k in range(0, length, 2):
        m.box((C - 1.45, y0 + 3.5 + k, C - 1.45), (C + 1.45, y0 + 4.3 + k, C + 1.45), pommel)


def blade(m, y0, y1, w, core, edge, glow, depth=1.6, taper=0.55):
    """A layered blade: a core, two bevelled edges, a glowing fuller, narrowing toward a pointed tip."""
    n = 6
    for i in range(n):
        a, b = y0 + (y1 - y0) * i / n, y0 + (y1 - y0) * (i + 1) / n
        ww = w * (1 - taper * i / n)
        m.box((C - ww / 2, a, C - depth / 2), (C + ww / 2, b + 0.2, C + depth / 2), core)
        m.box((C - ww / 2 - 0.6, a, C - depth / 4), (C - ww / 2, b + 0.2, C + depth / 4), edge)
        m.box((C + ww / 2, a, C - depth / 4), (C + ww / 2 + 0.6, b + 0.2, C + depth / 4), edge)
        if i < n - 1:
            m.box((C - 0.5, a, C - depth / 2 - 0.15), (C + 0.5, b + 0.2, C + depth / 2 + 0.15), glow)
    tw = w * (1 - taper)
    m.box((C - tw / 2, y1, C - depth / 2), (C + tw / 2, y1 + 2.5, C + depth / 2), edge, 'z', 45, (C, y1 + 1.2, C))


def thornroot_blade():
    """A greatsword of living wood: vines spiral the blade, thorns bristle from both edges, a moss-and-mushroom guard."""
    m = Model('thornroot_blade')
    grip(m, 'bark_d', 'bark', 'glowg')
    m.box((C - 7, -3, C - 2.5), (C + 7, 0, C + 2.5), 'bark')
    m.box((C - 8.5, -3.5, C - 1.5), (C - 6, 2, C + 1.5), 'bark_d', 'z', -22.5)
    m.box((C + 6, -3.5, C - 1.5), (C + 8.5, 2, C + 1.5), 'bark_d', 'z', 22.5)
    m.box((C - 6, 0, C - 2), (C + 6, 1.5, C + 2), 'moss')
    m.box((C + 3, 1.5, C - 1), (C + 4, 3.5, C), 'root_c')
    m.box((C + 2, 3.5, C - 2), (C + 5, 4.5, C + 1), 'cap')
    blade(m, 1, 29, 7, 'bark', 'wood', 'glowg', depth=2.2)
    for i in range(9):
        y = 3 + i * 2.9
        side = 1 if i % 2 else -1
        ww = 7 * (1 - 0.55 * (y - 1) / 28)
        m.box((C + side * (ww / 2 + 0.3) - 0.6, y, C - 0.6), (C + side * (ww / 2 + 0.3) + 0.6, y + 2.6, C + 0.6), 'thorn', 'z', -45 * side,
              (C + side * ww / 2, y, C))
    for i in range(7):
        y = 2 + i * 3.8
        m.box((C - 4, y, C + 1.0), (C + 4, y + 1.1, C + 1.7), 'moss_l', 'z', 22.5 if i % 2 else -22.5)
    return m


def galecutter():
    """A storm sabre two blocks long: a curved blade of stormglass split by lightning, a guard of swept feather-wings."""
    m = Model('galecutter')
    grip(m, 'navy_d', 'steel', 'rune_cyan')
    for s in (-1, 1):                                     # feathered wings swept up from the guard
        x0, x1 = (C + 1, C + 9) if s > 0 else (C - 9, C - 1)
        m.box((x0, -3, C - 1), (x1, -1, C + 1), 'feather_w', 'z', 22.5 * s, (C, -2, C))
        x0, x1 = (C + 1, C + 7) if s > 0 else (C - 7, C - 1)
        m.box((x0, -1.5, C - 0.8), (x1, 0.5, C + 0.8), 'storm_l', 'z', 45 * s, (C, -0.5, C))
        x0, x1 = (C + 2, C + 6) if s > 0 else (C - 6, C - 2)
        m.box((x0, -4.5, C - 0.6), (x1, -3.5, C + 0.6), 'glow_w', 'z', 22.5 * s, (C, -4, C))
    m.box((C - 2.5, -1, C - 2), (C + 2.5, 1.5, C + 2), 'steel')
    m.box((C - 1, -0.5, C - 2.2), (C + 1, 1, C + 2.2), 'rune_cyan')
    end = m.seg_chain((C, 1.5, C), [(7, 6.5, 0), (7, 6, -22.5), (6, 5, -22.5), (5, 4, -45), (4, 2.5, -45)], 'z',
                      lambda i: 'ice' if i % 2 else 'storm', 1.8)
    m.seg_chain((C + 1.6, 1.5, C + 1.0), [(7, 0.8, 0), (7, 0.8, -22.5), (6, 0.8, -22.5), (5, 0.7, -45)], 'z', lambda i: 'glow_w', 0.5)
    m.seg_chain((C - 1.6, 1.5, C - 1.0), [(7, 0.8, 0), (7, 0.8, -22.5), (6, 0.8, -22.5), (5, 0.7, -45)], 'z', lambda i: 'rune_cyan', 0.5)
    for (y, x) in [(6, 4), (12, 3), (17, 1)]:
        m.box((C + x, y, C - 0.4), (C + x + 3, y + 0.8, C + 0.4), 'glow_w', 'z', 45)
    return m


def soulbrand():
    """A black cleaver as broad as a door, cracked with molten light, a horned skull for a guard, soul fire in the pommel."""
    m = Model('soulbrand')
    grip(m, 'ash_fur', 'king_armor', 'soul_light')
    m.box((C - 4, -4, C - 3), (C + 4, 1, C + 3), 'bone')
    m.box((C - 2.5, -3, C + 2.8), (C - 0.8, -1.5, C + 3.3), 'flame')
    m.box((C + 0.8, -3, C + 2.8), (C + 2.5, -1.5, C + 3.3), 'flame')
    for s in (-1, 1):
        m.box((C + s * 3.5 - 1, -3, C - 1), (C + s * 3.5 + 1, 5, C + 1), 'horn', 'z', -22.5 * s, (C + s * 3.5, -3, C))
        m.box((C + s * 6 - 0.8, 3, C - 0.8), (C + s * 6 + 0.8, 8, C + 0.8), 'horn', 'z', -45 * s, (C + s * 6, 3, C))
    m.box((C - 7, 1, C - 1.4), (C + 7, 26, C + 1.4), 'king_armor')
    m.box((C - 7.6, 1, C - 0.7), (C - 7, 26, C + 0.7), 'steel')
    m.box((C + 7, 1, C - 0.7), (C + 7.6, 30, C + 0.7), 'steel')
    m.box((C - 7, 26, C - 1.4), (C + 7, 31, C + 1.4), 'king_armor', 'z', -22.5, (C - 7, 26, C))
    for (x0, y0, x1, y1) in [(-5, 4, -3, 14), (-3, 13, 1, 15), (1, 8, 2, 22), (3, 18, 5, 27), (-4, 18, -1, 19)]:
        m.box((C + x0, y0, C - 1.6), (C + x1, y1, C + 1.6), 'rune_orange')
    m.box((C - 1, 2, C - 1.7), (C + 1, 24, C + 1.7), 'flame')
    return m


def undertow_fang():
    """A whole leviathan fang made into a blade, teal light along its core, the hilt grown over with coral and barnacles."""
    m = Model('undertow_fang')
    grip(m, 'kelp', 'barnacle', 'water_glow')
    m.box((C - 5, -3, C - 3), (C + 5, 1, C + 3), 'coral')
    m.box((C - 6, -2, C - 1), (C - 3, 3, C + 2), 'coral_b', 'z', 22.5)
    m.box((C + 3, -2, C - 2), (C + 6.5, 2, C + 1), 'barnacle', 'z', -22.5)
    m.box((C + 5, -1, C - 0.5), (C + 9, 0, C + 0.5), 'fin', 'z', 45, (C + 5, -0.5, C))
    m.box((C - 9, -1, C - 0.5), (C - 5, 0, C + 0.5), 'fin', 'z', -45, (C - 5, -0.5, C))
    m.seg_chain((C, 1, C), [(7, 8, 0), (7, 7, 22.5), (6, 6, 22.5), (5, 4.5, 45), (4, 3, 45), (3, 1.5, 45)], 'z',
                lambda i: 'bone' if i % 2 == 0 else 'pearl', 3.2)
    m.seg_chain((C, 1.5, C + 1.65), [(7, 2.4, 0), (7, 2, 22.5), (6, 1.6, 22.5), (5, 1.2, 45)], 'z', lambda i: 'water_glow', 0.4)
    m.seg_chain((C, 1.5, C - 1.65), [(7, 2.4, 0), (7, 2, 22.5), (6, 1.6, 22.5), (5, 1.2, 45)], 'z', lambda i: 'water_glow', 0.4)
    return m


def hushblade():
    """A white blade nearly three blocks long and thin as a whisper, an ice-blue edge, a guard of icicles, frost on the grip."""
    m = Model('hushblade')
    grip(m, 'fur_w', 'ice_d', 'frost_glow', length=12)
    m.box((C - 3, -3, C - 3), (C + 3, -1, C + 3), 'ice_d', 'y', 45)
    for s in (-1, 1):
        for k, (dx, ln) in enumerate([(2.5, 7), (4.5, 5), (6, 3)]):
            m.box((C + s * dx - 0.6, -4 - ln, C - 0.6), (C + s * dx + 0.6, -3, C + 0.6), 'ice', 'z', 22.5 * s, (C + s * dx, -3, C))
            m.box((C + s * dx - 0.6, -1, C - 0.6), (C + s * dx + 0.6, -1 + ln * 0.6, C + 0.6), 'ice', 'z', -22.5 * s, (C + s * dx, -1, C))
    blade(m, -1, 30, 3.6, 'ice', 'glow_w', 'frost_glow', depth=1.0, taper=0.3)
    return m


def glass_reaper():
    """Kharzul's scythe remade: a long gilded haft and a crescent blade of red glass as wide as you are tall."""
    m = Model('glass_reaper')
    m.box((C - 1, -16, C - 1), (C + 1, 22, C + 1), 'haft')
    for y in (-14, -4, 6, 16):
        m.box((C - 1.4, y, C - 1.4), (C + 1.4, y + 1.2, C + 1.4), 'gold')
    m.box((C - 2.2, -16, C - 2.2), (C + 2.2, -13, C + 2.2), 'gold')
    m.box((C - 2, 21, C - 2), (C + 2, 25, C + 2), 'sandstone_r')
    m.box((C - 1.2, 22, C - 2.2), (C + 1.2, 24, C + 2.2), 'sun_glow')
    # the crescent: blocks laid along an arc, each turned to the nearest allowed angle
    for i in range(14):
        t = i / 13
        a = math.radians(100 - 120 * t)
        r = 13
        cx, cy = C - 1 + r * math.cos(a) * 1.1, 21 + r * math.sin(a) * 0.55
        w = 4.2 * (1 - 0.75 * t) + 0.8
        ang = [45, 45, 22.5, 22.5, 0, 0, 0, -22.5, -22.5, -45, -45, -45, -45, -45][i]
        m.box((cx - 1.4, cy - w / 2, C - 0.6), (cx + 1.4, cy + w / 2, C + 0.6), 'glass_red', 'z', ang, (cx, cy, C))
        m.box((cx - 1.0, cy - w / 2 - 0.5, C - 0.3), (cx + 1.0, cy - w / 2 + 0.3, C + 0.3), 'glass_glow', 'z', ang, (cx, cy, C))
    m.box((C - 3, 18, C - 0.8), (C + 3, 22, C + 0.8), 'gold')
    return m


def second_hand():
    """A rapier shaped like the hand of a clock: an arrow-head tip, a cog for a guard, a clock face for a pommel."""
    m = Model('second_hand')
    m.box((C - 3, -16, C - 1), (C + 3, -10, C + 1), 'clockface')
    m.box((C - 3.4, -16.4, C - 0.8), (C + 3.4, -9.6, C + 0.8), 'brass')
    m.box((C - 0.3, -14.5, C - 1.3), (C + 0.3, -12, C + 1.3), 'void')
    grip(m, 'iron_dk', 'brass_d', 'rift_glow', y0=-10, length=7)
    for k in range(8):
        a = k * math.pi / 4
        x, y = C + 4.5 * math.cos(a), 0 + 4.5 * math.sin(a)
        m.box((x - 1, y - 1, C - 0.8), (x + 1, y + 1, C + 0.8), 'brass_d', 'z', 45 if k % 2 else 0)
    m.box((C - 3.5, -3.5, C - 0.6), (C + 3.5, 3.5, C + 0.6), 'brass', 'z', 45)
    m.box((C - 1.2, -1.2, C - 0.9), (C + 1.2, 1.2, C + 0.9), 'rift_glow')
    m.box((C - 0.8, 3, C - 0.5), (C + 0.8, 28, C + 0.5), 'iron_dk')
    m.box((C - 0.25, 4, C - 0.6), (C + 0.25, 27, C + 0.6), 'rift_glow')
    m.box((C - 3.2, 26, C - 0.5), (C + 3.2, 28.5, C + 0.5), 'brass')
    m.box((C - 2.6, 27.5, C - 0.5), (C + 2.6, 31, C + 0.5), 'brass', 'z', 45, (C, 29, C))
    m.box((C - 1, 22, C - 0.7), (C + 1, 24, C + 0.7), 'gold_glow')
    return m


def spore_lash():
    """A great mushroom maul: a twisted root haft, a cap the size of a shield with glowing gills, spore sacs and small caps."""
    m = Model('spore_lash')
    m.seg_chain((C, -16, C), [(10, 2.6, 0), (10, 2.4, 22.5), (8, 2.2, 0), (8, 2.2, -22.5)], 'z', lambda i: 'root_c', 2.6)
    for y in (-12, -4, 4):
        m.box((C - 1.8, y, C - 1.8), (C + 1.8, y + 1.5, C + 1.8), 'flesh_p')
    m.box((C - 8, 19, C - 8), (C + 8, 23, C + 8), 'cap_m')
    m.box((C - 6.5, 23, C - 6.5), (C + 6.5, 26, C + 6.5), 'cap_m')
    m.box((C - 4, 26, C - 4), (C + 4, 28, C + 4), 'cap_m')
    m.box((C - 7.5, 18.4, C - 7.5), (C + 7.5, 19, C + 7.5), 'bloom_glow')
    for (x, z) in [(-6, -3), (5, 4), (-2, 6), (3, -6)]:
        m.box((C + x - 1, 20, C + z - 1), (C + x + 1, 22, C + z + 1), 'puff_glow')
    for (x, z, h) in [(-3, 2, 2), (2, -1, 3), (0, 3, 1.5)]:
        m.box((C + x - 0.4, 28, C + z - 0.4), (C + x + 0.4, 28 + h, C + z + 0.4), 'root_c')
        m.box((C + x - 1.2, 28 + h, C + z - 1.2), (C + x + 1.2, 28.8 + h, C + z + 1.2), 'puff')
    return m


WEAPONS = [('thornroot_blade', thornroot_blade), ('galecutter', galecutter), ('soulbrand', soulbrand), ('undertow_fang', undertow_fang),
           ('hushblade', hushblade), ('glass_reaper', glass_reaper), ('second_hand', second_hand), ('spore_lash', spore_lash)]

DISPLAY = {
    'thirdperson_righthand': {'rotation': [0, -90, 0], 'translation': [0, 12, 0.5], 'scale': [0.85, 0.85, 0.85]},
    'thirdperson_lefthand': {'rotation': [0, 90, 0], 'translation': [0, 12, 0.5], 'scale': [0.85, 0.85, 0.85]},
    'firstperson_righthand': {'rotation': [0, -90, 25], 'translation': [1.13, 12, 1.13], 'scale': [0.68, 0.68, 0.68]},
    'firstperson_lefthand': {'rotation': [0, 90, -25], 'translation': [1.13, 12, 1.13], 'scale': [0.68, 0.68, 0.68]},
    'gui': {'rotation': [0, 0, -45], 'translation': [0, 0, 0], 'scale': [0.32, 0.32, 0.32]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.3, 0.3, 0.3]},
    'fixed': {'rotation': [0, 0, -45], 'translation': [0, 0, 0], 'scale': [0.45, 0.45, 0.45]},
    'head': {'rotation': [0, 0, 0], 'translation': [0, 8, 0], 'scale': [0.6, 0.6, 0.6]},
}


def write_all():
    for i, (key, fn) in enumerate(WEAPONS):
        m = fn()
        img, where = texture(styles_of(m), 900 + i)
        img.save(f'{ASSETS}/textures/item/{key}.png')
        write_json(f'{ASSETS}/models/item/{key}.json', {'textures': {'t': f'aurelia:item/{key}', 'particle': f'aurelia:item/{key}'},
                                                       'display': DISPLAY, 'elements': json_elements(m.els, where)})


if __name__ == '__main__':
    write_all()
    print('weapon models written')
