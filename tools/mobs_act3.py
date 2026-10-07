"""Act three: texture styles, the six citadel guards, and registration of Vexor and the Bloom Mother with mobspecs."""
import math

import bosses_act3
from mobs_act2 import side_box, side_name

STYLES = {
    # Clockwork Rift
    'iron_dk': dict(base=(34, 32, 40), var=6, patches=[((52, 48, 60), 18, (1, 3)), ((20, 18, 26), 14, (1, 3))], cracks=(170, 70, 255)),
    'brass_d': dict(base=(178, 132, 54), var=10, patches=[((216, 172, 84), 14, (1, 2)), ((120, 84, 30), 14, (1, 2)), ((90, 120, 80), 4, (1, 2))]),
    'rift_glow': dict(base=(168, 70, 255), var=14, patches=[((236, 190, 255), 12, (1, 2)), ((110, 30, 200), 8, (1, 2))]),
    'rift_glow2': dict(base=(230, 160, 255), var=10, patches=[((255, 240, 255), 10, (1, 1))]),
    'gold_glow': dict(base=(255, 206, 90), var=10, patches=[((255, 244, 190), 10, (1, 1))]),
    'clockface': dict(base=(232, 222, 196), var=5, patches=[((40, 34, 30), 10, (1, 1))]),
    # Mycelial Deep
    'root_c': dict(base=(222, 210, 186), var=8, patches=[((196, 180, 152), 16, (1, 3)), ((150, 80, 160), 6, (1, 2))]),
    'flesh_p': dict(base=(110, 42, 120), var=9, patches=[((150, 64, 160), 14, (1, 3)), ((70, 22, 80), 14, (1, 3))]),
    'flesh_d': dict(base=(70, 30, 78), var=7, patches=[((96, 44, 104), 14, (1, 3)), ((44, 16, 50), 12, (1, 2))]),
    'petal_p': dict(base=(132, 40, 150), var=10, patches=[((180, 70, 196), 14, (1, 3)), ((90, 24, 104), 12, (1, 2)), ((240, 200, 240), 4, (1, 1))]),
    'petal_c': dict(base=(226, 214, 192), var=8, patches=[((200, 186, 160), 14, (1, 3)), ((170, 90, 180), 8, (1, 2))]),
    'bloom_glow': dict(base=(255, 70, 220), var=14, patches=[((255, 190, 245), 12, (1, 2))]),
    'cap_m': dict(base=(150, 40, 160), var=10, patches=[], dots=((255, 120, 230), 18, (1, 2))),
}
GLOW = {'rift_glow', 'rift_glow2', 'gold_glow', 'bloom_glow'}


# ====================================================================================== Paradox Keep guards
def gearskitter(P):
    """Fast: a clockwork spider, its body a ticking clock face, eight brass legs and a gear turning on its back."""
    parts = []
    add = parts.append
    add(P('body', (14, 8, 14), (-7, 0, -7), (0, 8, 0), style='iron_dk'))
    add(P('face', (12, 12, 1), (-6, -2, 7), parent='body', style='clockface'))
    add(P('rim', (14, 2, 2), (-7, 10, 6.5), parent='body', style='brass_d'))
    add(P('handH', (1, 5, 1), (-0.5, 4, 8.2), parent='body', style='iron_dk'))
    add(P('handM', (4, 1, 1), (0, 4, 8.3), parent='body', style='iron_dk'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (2, 2, 1), (sx * 4 - 1, 8, 8.4), parent='body', style='rift_glow'))
    add(P('gear', (12, 2, 12), (-6, -1, -6), (0, 9, -1), parent='body', style='brass_d', anim='spin'))
    for k in range(6):
        a = k * math.pi / 3
        add(P(f'gearTooth{k}', (3, 2, 3), (-1.5, -1, -1.5), (7 * math.cos(a), 0, 7 * math.sin(a)), parent='gear', style='brass_d'))
    add(P('gearHub', (4, 2, 4), (-2, 1, -2), parent='gear', style='rift_glow'))
    for sx in (-1, 1):
        nm = side_name(sx)
        for k in range(4):
            leg = f'leg{nm}{k}'
            add(P(leg, (11, 2, 2), (side_box(sx, 11), -1, -1), (sx * 6, 4, 5 - 3.5 * k), rot=(0, sx * (0.6 - 0.4 * k), -sx * 0.45),
                  parent='body', style='brass_d', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
            add(P(leg + 'Joint', (3, 3, 3), (-1.5, -1.5, -1.5), (sx * 11, 0, 0), parent=leg, style='iron_dk'))
            add(P(leg + 'Tip', (2, 11, 2), (-1, -11, -1), (sx * 11, 0, 0), rot=(0, 0, sx * 0.3), parent=leg, style='iron_dk'))
    return parts


def secondhand(P):
    """Special: a floating violet core in a cage of rings, orbited by six clock-hand blades."""
    parts = []
    add = parts.append
    add(P('core', (8, 8, 8), (-4, -4, -4), (0, 20, 0), style='rift_glow', anim='pulse'))
    add(P('cage', (12, 2, 12), (-6, -1, -6), parent='core', style='brass_d', anim='spinR'))
    add(P('cageV', (2, 12, 12), (-1, -6, -6), parent='core', style='brass_d', anim='spin'))
    add(P('eye', (4, 4, 1), (-2, -2, 4.2), parent='core', style='glow_w'))
    add(P('pupil', (1, 3, 1), (-0.5, -1.5, 4.6), parent='core', style='void'))
    add(P('orbit', (2, 2, 2), (-1, -1, -1), (0, 20, 0), style='void', anim='spin'))
    for i in range(6):
        a = i * math.pi / 3
        h = f'blade{i}'
        add(P(h, (2, 1, 14), (-1, -0.5, 0), (9 * math.cos(a), (i % 2) * 4 - 2, 9 * math.sin(a)), rot=(0.2 * (-1) ** i, -a + math.pi / 2, 0),
              parent='orbit', style='iron_dk'))
        add(P(h + 'Tip', (4, 1, 4), (-2, -0.5, -2), (0, 0, 15), rot=(0, math.pi / 4, 0), parent=h, style='brass_d'))
        add(P(h + 'Edge', (1, 1, 12), (-0.5, 0.6, 1), parent=h, style='gold_glow'))
    for k in range(3):
        add(P(f'spark{k}', (1, 5, 1), (-0.5, -2.5, -0.5), (6 * math.cos(k * 2.1), -7 + k, 6 * math.sin(k * 2.1)), parent='core', style='rift_glow2', anim='sway'))
    return parts


def hour_warden(P):
    """Heavy: an iron giant with a clock for a head, a pendulum swinging in its open chest, and a chained clock-weight flail."""
    parts = []
    add = parts.append
    for sx in (-1, 1):
        n = 'leg' + side_name(sx)
        add(P(n, (6, 14, 6), (-3, -14, -3), (sx * 4.5, 14, 0), style='iron_dk', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Plate', (7, 5, 2), (-3.5, -9, 3), parent=n, style='brass_d'))
        add(P(n + 'Foot', (7, 3, 9), (-3.5, -14, -3), parent=n, style='brass_d'))
    add(P('body', (16, 16, 10), (-8, 0, -5), (0, 14, 0), style='iron_dk'))
    add(P('cavity', (8, 10, 1), (-4, 3, 5), parent='body', style='void'))
    add(P('pendulum', (1, 7, 1), (-0.5, -7, -0.5), (0, 12, 5.4), parent='body', style='brass_d', anim='sway'))
    add(P('pendulumBob', (4, 4, 1), (-2, -11, -0.5), (0, 12, 5.4), parent='body', style='gold_glow', anim='sway'))
    add(P('collar', (18, 3, 12), (-9, 15, -6), parent='body', style='brass_d'))
    for sx in (-1, 1):
        add(P('pauldron' + side_name(sx), (8, 6, 10), (-4, 0, -5), (sx * 12, 27, 0), rot=(0, 0, -sx * 0.2), style='brass_d'))
        add(P('pauldronSpike' + side_name(sx), (2, 7, 2), (-1, 6, -1), (sx * 12, 27, 0), rot=(0, 0, -sx * 0.4), style='iron_dk'))
    add(P('head', (12, 12, 5), (-6, 0, -2.5), (0, 31, 0), style='brass_d', anim='head'))
    add(P('dial', (10, 10, 1), (-5, 1, 2.6), parent='head', style='clockface'))
    add(P('hourHand', (1, 4, 1), (-0.5, 6, 3.4), parent='head', style='iron_dk'))
    add(P('minHand', (4, 1, 1), (-0.5, 5.5, 3.5), rot=(0, 0, 0.6), parent='head', style='iron_dk'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (2, 1, 1), (sx * 2.5 - 1, 7, 3.5), parent='head', style='rift_glow'))
    add(P('bell', (6, 4, 6), (-3, 12, -3), parent='head', style='brass_d'))
    for sx in (-1, 1):
        a = 'arm' + side_name(sx)
        add(P(a, (5, 16, 5), (-2.5, -16, -2.5), (sx * 12, 26, 0), rot=(-0.5 if sx < 0 else -0.15, 0, -sx * 0.1), style='iron_dk', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Fist', (7, 6, 7), (-3.5, -21, -3.5), parent=a, style='brass_d'))
    add(P('chainA', (1, 8, 1), (-0.5, -8, -0.5), (0, -21, 0), parent='armR', style='steel', anim='sway'))
    add(P('chainB', (1, 8, 1), (-0.5, -8, -0.5), (0, -8, 0), rot=(0.4, 0, 0), parent='chainA', style='steel'))
    add(P('flail', (9, 9, 4), (-4.5, -9, -2), (0, -8, 0), parent='chainB', style='brass_d'))
    add(P('flailFace', (7, 7, 1), (-3.5, -8, 2.1), (0, -8, 0), parent='chainB', style='clockface'))
    for k, (x, y) in enumerate([(-6, -5), (5, -5), (-1, -12), (-1, 1)]):
        add(P(f'flailSpike{k}', (2, 2, 2), (x, y, -1), (0, -8, 0), parent='chainB', style='iron_dk'))
    return parts


# ====================================================================================== Spore Cathedral guards
def root_grub(P):
    """Fast: a bloated grub of cream flesh with violet caps sprouting from its back and a mouth like a split root."""
    parts = []
    add = parts.append
    prev = None
    for k, (w, h, ln) in enumerate([(12, 10, 8), (13, 11, 8), (12, 10, 7), (10, 8, 6), (7, 6, 5)]):
        n = f'seg{k}'
        if prev is None:
            add(P(n, (w, h, ln), (-w / 2, 0, -ln / 2), (0, 1, 6), style='root_c', anim='undulate'))
        else:
            add(P(n, (w, h, ln), (-w / 2, -h / 2, -ln), (0, 4.5 if k == 1 else 0, -ln / 2 - 1 if k == 1 else -6.5 + k * 0.4), parent=prev, style='root_c', anim='undulate'))
        if k < 4:
            add(P(n + 'Cap', (6 + (k % 2) * 2, 2, 6), (-3 - (k % 2), h / 2 if prev else h, -3 - (0 if prev else -1)), parent=n, style='cap_m'))
            add(P(n + 'Stalk', (2, 3, 2), (-1, h / 2 - 2 if prev else h - 2, -1), parent=n, style='root_c'))
        prev = n
    add(P('head', (9, 8, 6), (-4.5, 0, 0), (0, 1, 10), style='flesh_p', anim='head'))
    add(P('mouth', (6, 5, 1), (-3, 1.5, 6), parent='head', style='void'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('mandible' + nm, (2, 2, 6), (-1, -1, 0), (sx * 3.5, 2, 5), rot=(0, -sx * 0.5, 0), parent='head', style='bone', anim='jaw'))
        add(P('eye' + nm, (1, 1, 1), (sx * 3 - 0.5, 6, 6), parent='head', style='bloom_glow'))
        for k in range(3):
            add(P(f'leg{nm}{k}', (2, 4, 2), (-1, -4, -1), (sx * 6, 4, 8 - 7 * k), style='flesh_d', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
    return parts


def spore_drifter(P):
    """Special: a floating mushroom-jelly with a glowing cap and a curtain of stinging tendrils."""
    parts = []
    add = parts.append
    add(P('cap', (16, 6, 16), (-8, 0, -8), (0, 22, 0), style='cap_m', anim='pulse'))
    add(P('capTop', (12, 4, 12), (-6, 6, -6), parent='cap', style='cap_m'))
    add(P('capCrown', (6, 3, 6), (-3, 10, -3), parent='cap', style='bloom_glow'))
    add(P('under', (14, 2, 14), (-7, -2, -7), parent='cap', style='root_c'))
    add(P('core', (6, 6, 6), (-3, -7, -3), parent='cap', style='bloom_glow', anim='pulse'))
    for i in range(12):
        a = i * 2 * math.pi / 12
        ln = 14 + (i % 3) * 5
        t = f'tendril{i}'
        add(P(t, (1, ln, 1), (-0.5, -ln, -0.5), (6.5 * math.cos(a), 20, 6.5 * math.sin(a)), style='root_c' if i % 2 else 'flesh_p', anim='sway'))
        add(P(t + 'Tip', (2, 3, 2), (-1, -ln - 3, -1), parent=t, style='bloom_glow'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (2, 2, 1), (sx * 3 - 1, 1, 8.1), parent='cap', style='glow_w'))
    return parts


def husk_guard(P):
    """Heavy: a skeleton knight swallowed by fungus, a cap shield on one arm, a bone spear, mushrooms bursting from its skull."""
    parts = []
    add = parts.append
    for sx in (-1, 1):
        n = 'leg' + side_name(sx)
        add(P(n, (4, 14, 4), (-2, -14, -2), (sx * 3.5, 14, 0), style='bone', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Growth', (5, 5, 5), (-2.5, -8, -2.5), parent=n, style='flesh_p'))
    add(P('pelvis', (10, 4, 6), (-5, 12, -3), style='bone_d'))
    add(P('spine', (3, 13, 3), (-1.5, 15, -2.5), style='bone'))
    for k in range(4):
        add(P(f'rib{k}', (12, 1, 6), (-6, 18 + 2.5 * k, -3), style='bone'))
    add(P('overgrowth', (12, 8, 7), (-6, 20, -5), style='flesh_p'))
    add(P('heartSac', (4, 4, 3), (-2, 21, 0), style='bloom_glow', anim='pulse'))
    add(P('head', (8, 8, 8), (-4, 0, -4), (0, 29, 0), style='bone', anim='head'))
    add(P('jaw', (6, 2, 5), (-3, -2, -1), parent='head', style='bone_d', anim='jaw'))
    for sx in (-1, 1):
        add(P('socket' + side_name(sx), (2, 2, 1), (sx * 2 - 1, 3, 4.1), parent='head', style='void'))
        add(P('glow' + side_name(sx), (1, 1, 1), (sx * 2 - 0.5, 3.5, 4.4), parent='head', style='bloom_glow'))
    for k, (x, z, h, w) in enumerate([(-2, -1, 5, 7), (3, 1, 3, 5), (0, -3, 8, 5)]):
        add(P(f'shroom{k}Stem', (2, h, 2), (x - 1, 8, z - 1), parent='head', style='root_c'))
        add(P(f'shroom{k}Cap', (w, 2, w), (x - w / 2, 8 + h, z - w / 2), parent='head', style='cap_m'))
    for sx in (-1, 1):
        a = 'arm' + side_name(sx)
        add(P(a, (3, 14, 3), (-1.5, -14, -1.5), (sx * 7, 27, 0), rot=(-0.45 if sx < 0 else -0.2, 0, 0), style='bone', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Moss', (5, 5, 5), (-2.5, -4, -2.5), parent=a, style='flesh_p'))
    add(P('shield', (2, 22, 16), (-1, -14, -8), (2, -8, 0), rot=(0.2, 0, 0), parent='armL', style='cap_m'))
    add(P('shieldRim', (3, 2, 18), (-1.5, 7, -9), parent='shield', style='root_c'))
    add(P('shieldEye', (1, 6, 6), (1, -6, -3), parent='shield', style='bloom_glow'))
    add(P('spear', (2, 38, 2), (-1, -12, -1), (0, -12, 0), rot=(0.3, 0, 0), parent='armR', style='bone_d'))
    add(P('spearHead', (3, 9, 2), (-1.5, 26, -1), parent='spear', style='bone'))
    return parts


MOBS = {
    'vexor': dict(parts='vexor', seed=41, shadow=2.6),
    'bloom_mother': dict(parts='bloom_mother', seed=42, shadow=3.2),
    'gearskitter': dict(parts=gearskitter, seed=51, shadow=0.8),
    'secondhand': dict(parts=secondhand, seed=52, shadow=0.4),
    'hour_warden': dict(parts=hour_warden, seed=53, shadow=0.9),
    'root_grub': dict(parts=root_grub, seed=54, shadow=0.7),
    'spore_drifter': dict(parts=spore_drifter, seed=55, shadow=0.5),
    'husk_guard': dict(parts=husk_guard, seed=56, shadow=0.7),
}


def register(mobs, styles, glow_styles, part):
    styles.update(STYLES)
    glow_styles.update(GLOW)
    for key, m in MOBS.items():
        fn = m['parts']
        if isinstance(fn, str):
            fn = getattr(bosses_act3, fn)
        mobs[key] = dict(parts=(lambda f=fn: f(part)), seed=m['seed'], shadow=m['shadow'])
