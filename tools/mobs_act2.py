"""Act two: texture styles, the nine citadel guards, and registration of the three new Wardens with mobspecs."""
import math

import bosses_act2

STYLES = {
    # Drowned Expanse
    'abyss': dict(base=(16, 34, 44), var=6, patches=[((26, 58, 66), 18, (1, 4)), ((8, 18, 26), 14, (1, 3)), ((40, 84, 80), 4, (1, 1))]),
    'abyss_l': dict(base=(44, 74, 78), var=7, patches=[((62, 100, 98), 14, (1, 3)), ((30, 52, 58), 10, (1, 2))]),
    'belly_p': dict(base=(150, 172, 170), var=7, patches=[((120, 146, 146), 18, (1, 3))]),
    'shell': dict(base=(84, 78, 70), var=8, patches=[((112, 104, 92), 16, (1, 3)), ((58, 54, 48), 14, (1, 2))]),
    'barnacle': dict(base=(206, 198, 176), var=8, patches=[], dots=((70, 64, 58), 18, (1, 1))),
    'fin': dict(base=(22, 76, 84), var=8, patches=[((40, 110, 114), 14, (1, 3)), ((12, 46, 54), 10, (1, 2))]),
    'abyss_glow': dict(base=(70, 255, 214), var=12, patches=[((210, 255, 244), 10, (1, 1))]),
    'maw': dict(base=(96, 22, 34), var=8, patches=[((140, 40, 52), 14, (1, 2)), ((50, 10, 18), 12, (1, 2))]),
    'coral': dict(base=(226, 86, 110), var=12, patches=[((250, 140, 160), 14, (1, 2)), ((170, 50, 80), 12, (1, 2))]),
    'coral_b': dict(base=(70, 120, 214), var=10, patches=[((120, 170, 250), 12, (1, 2))]),
    'brass': dict(base=(168, 122, 52), var=10, patches=[((206, 162, 82), 12, (1, 2)), ((60, 120, 104), 14, (1, 3))]),
    'kelp': dict(base=(58, 98, 38), var=10, patches=[((84, 130, 52), 14, (1, 3)), ((36, 66, 26), 12, (1, 2))]),
    'drowned': dict(base=(86, 140, 128), var=8, patches=[((60, 106, 98), 16, (1, 3)), ((120, 170, 150), 8, (1, 2))]),
    'robe_sea': dict(base=(30, 70, 72), var=6, patches=[((48, 98, 96), 16, (1, 3)), ((20, 46, 50), 12, (1, 3))]),
    'water_glow': dict(base=(90, 210, 255), var=12, patches=[((220, 250, 255), 10, (1, 2))]),
    'pearl': dict(base=(238, 234, 246), var=6, patches=[((214, 200, 236), 12, (1, 2))]),
    'iron_rust': dict(base=(76, 72, 70), var=8, patches=[((120, 74, 46), 18, (1, 3)), ((52, 50, 50), 12, (1, 2))]),
    # Pale Wastes
    'shroud': dict(base=(226, 228, 230), var=6, patches=[((198, 202, 208), 16, (1, 4)), ((242, 244, 246), 8, (1, 2))]),
    'shroud_d': dict(base=(176, 182, 190), var=7, patches=[((150, 158, 168), 16, (1, 4)), ((206, 210, 216), 8, (1, 2))]),
    'ice': dict(base=(170, 214, 240), var=10, patches=[((214, 240, 255), 14, (1, 3)), ((128, 180, 220), 10, (1, 2))]),
    'ice_d': dict(base=(96, 146, 196), var=8, patches=[((140, 190, 230), 12, (1, 2))]),
    'mask': dict(base=(244, 242, 236), var=4, patches=[((226, 222, 214), 8, (1, 2))]),
    'frost_glow': dict(base=(170, 238, 255), var=10, patches=[((250, 255, 255), 12, (1, 2))]),
    'ice_armor': dict(base=(196, 214, 228), var=7, patches=[((150, 176, 200), 18, (2, 4)), ((236, 246, 255), 8, (1, 2))]),
    'fur_w': dict(base=(212, 214, 216), var=10, patches=[((180, 184, 190), 24, (1, 2))]),
    # Scarlet Sands
    'glass_red': dict(base=(160, 22, 34), var=12, patches=[((210, 60, 70), 14, (1, 3)), ((110, 12, 22), 12, (1, 2)), ((250, 170, 170), 4, (1, 1))]),
    'glass_glow': dict(base=(255, 74, 60), var=12, patches=[((255, 196, 150), 12, (1, 2))]),
    'robe_red': dict(base=(122, 26, 30), var=8, patches=[((150, 44, 40), 14, (1, 3)), ((80, 14, 20), 14, (1, 3))]),
    'robe_d': dict(base=(70, 14, 20), var=6, patches=[((96, 24, 28), 14, (1, 3)), ((44, 8, 12), 12, (1, 3))]),
    'sand': dict(base=(206, 160, 104), var=9, patches=[((228, 186, 130), 14, (1, 2)), ((170, 124, 80), 12, (1, 2))]),
    'gold_d': dict(base=(196, 146, 44), var=10, patches=[((236, 196, 90), 12, (1, 2)), ((140, 96, 30), 10, (1, 2))]),
    'sand_glow': dict(base=(255, 186, 80), var=12, patches=[((255, 236, 170), 12, (1, 2))]),
    'haft': dict(base=(40, 26, 24), var=6, patches=[((60, 40, 34), 14, (1, 3))]),
    'sandstone_r': dict(base=(178, 86, 40), var=9, patches=[((204, 112, 58), 16, (2, 4)), ((146, 66, 30), 14, (1, 3))]),
    'chitin': dict(base=(52, 30, 30), var=7, patches=[((80, 46, 40), 14, (1, 3)), ((196, 146, 44), 6, (1, 1))]),
    'sun_glow': dict(base=(255, 214, 90), var=10, patches=[((255, 250, 200), 12, (1, 2))]),
}
GLOW = {'abyss_glow', 'frost_glow', 'glass_glow', 'sand_glow', 'water_glow', 'sun_glow'}


def side_box(sx, length):
    return 0 if sx > 0 else -length


# ====================================================================================== Tidewrack guards
def coralclad(P):
    """Heavy: a diver's hulk in brass and coral, with a porthole helm and a rusted anchor."""
    parts = []
    add = parts.append
    for side, sx in (('R', -1), ('L', 1)):
        n = 'leg' + side
        add(P(n, (7, 13, 7), (-3.5, -13, -3.5), (sx * 5, 13, 0), style='brass', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Boot', (9, 5, 11), (-4.5, -13, -4), parent=n, style='iron_rust'))
        add(P(n + 'Coral', (3, 5, 3), (sx * 2 - 1.5, -4, 3), rot=(0.3, 0, sx * 0.4), parent=n, style='coral'))
    add(P('body', (20, 16, 14), (-10, 0, -7), (0, 13, 0), style='brass'))
    add(P('belly', (16, 8, 2), (-8, 1, 7), parent='body', style='iron_rust'))
    add(P('tank', (10, 12, 5), (-5, 2, -11), parent='body', style='iron_rust'))
    for k, (x, y, z, s, st) in enumerate([(-9, 13, -4, 4, 'coral'), (7, 12, 2, 3, 'coral_b'), (-4, 15, 5, 3, 'coral'), (8, 3, -6, 3, 'barnacle'), (-8, 5, 6, 2, 'barnacle')]):
        add(P(f'growth{k}', (s, s + 2, s), (x - s / 2, y, z - s / 2), parent='body', style=st))
    add(P('helm', (14, 13, 14), (-7, 0, -7), (0, 29, 0), style='brass', anim='head'))
    add(P('helmRim', (16, 3, 16), (-8, -1, -8), parent='helm', style='iron_rust'))
    add(P('porthole', (8, 8, 1), (-4, 3, 7), parent='helm', style='iron_rust'))
    add(P('visor', (6, 6, 1), (-3, 4, 7.4), parent='helm', style='abyss_glow'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('sidePort' + nm, (1, 5, 5), (sx * 7.2 - 0.5, 4, -2.5), parent='helm', style='abyss_glow'))
        c = 'helmCoral' + nm
        add(P(c, (2, 8, 2), (-1, 0, -1), (sx * 5, 12, -1), rot=(-0.2, 0, -sx * 0.5), parent='helm', style='coral'))
        add(P(c + 'Branch', (2, 5, 2), (-1, 0, -1), (0, 5, 0), rot=(0, 0, sx * 0.9), parent=c, style='coral'))
        add(P('pauldron' + nm, (10, 7, 11), (-5, -2, -5.5), (sx * 13, 27, 0), style='iron_rust'))
        add(P('pauldronBarn' + nm, (4, 2, 4), (sx * 2 - 2, 5, -1), parent='pauldron' + nm, style='barnacle'))
        a = 'arm' + side_name(sx)
        add(P(a, (6, 15, 6), (-3, -15, -3), (sx * 13, 26, 0), rot=(-1.3 if sx < 0 else 0.0, 0, 0), style='brass', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Gauntlet', (8, 6, 8), (-4, -18, -4), parent=a, style='iron_rust'))
    # the anchor, raised in the right hand like a mace
    add(P('anchorShaft', (2, 30, 2), (-1, -4, -1), (0, -17, 0), rot=(1.5, 0, 0), parent='armR', style='iron_rust'))
    add(P('anchorRing', (5, 4, 2), (-2.5, -8, -1), parent='anchorShaft', style='iron_rust'))
    add(P('anchorStock', (14, 2, 2), (-7, 0, -1), parent='anchorShaft', style='iron_rust'))
    add(P('anchorCrown', (16, 3, 2), (-8, 24, -1), parent='anchorShaft', style='iron_rust'))
    for sx, nm in ((-1, 'R'), (1, 'L')):
        add(P('anchorFluke' + nm, (3, 8, 2), (sx * 8 - 1.5, 19, -1), rot=(0, 0, sx * 0.4), parent='anchorShaft', style='iron_rust'))
        add(P('anchorBarb' + nm, (2, 3, 2), (sx * 8 - 1, 17, -1), parent='anchorShaft', style='coral'))
    add(P('anchorChain', (1, 14, 1), (-0.5, -14, -0.5), (0, -16, 2), parent='armL', style='steel', anim='sway'))
    return parts


def side_name(sx):
    return 'L' if sx > 0 else 'R'


def tidecaller(P):
    """Special: a drowned priestess in kelp robes, a crown of shells, a conch staff, and three orbiting water orbs."""
    parts = []
    add = parts.append
    add(P('robe', (12, 10, 10), (-6, 0, -5), (0, 2, 0), style='robe_sea'))
    add(P('robe2', (10, 10, 8), (-5, 0, -4), (0, 12, 0), style='robe_sea'))
    for i in range(10):
        a = i * 2 * math.pi / 10
        ln = 12 + (i % 3) * 3
        add(P(f'kelp{i}', (2, ln, 1), (-1, -ln, -0.5), (6 * math.sin(a), 12, 5 * math.cos(a)), rot=(0, a, 0), style='kelp', anim='sway'))
    add(P('chest', (10, 8, 6), (-5, 0, -3), (0, 22, 0), style='drowned'))
    add(P('stole', (12, 3, 7), (-6, 6, -3.5), parent='chest', style='kelp'))
    add(P('pearlChest', (2, 2, 1), (-1, 3, 3), parent='chest', style='pearl'))
    add(P('head', (8, 8, 8), (-4, 0, -4), (0, 30, 0), style='drowned', eyes=(90, 255, 220), anim='head'))
    add(P('hair', (10, 12, 4), (-5, -6, -6), parent='head', style='kelp'))
    for k in range(5):
        a = (k - 2) * 0.35
        add(P(f'shell{k}', (2, 4 + (k % 2) * 2, 1), (-1, 0, -0.5), (math.sin(a) * 4, 7, math.cos(a) * 1 - 1), rot=(0, 0, -a), parent='head', style='pearl' if k % 2 else 'coral'))
    for sx in (-1, 1):
        n = 'arm' + side_name(sx)
        add(P(n, (3, 12, 3), (-1.5, -12, -1.5), (sx * 6.5, 29, 0), rot=(-0.6 if sx < 0 else -0.25, 0, -sx * 0.1), style='drowned', anim='armA' if sx < 0 else 'armB'))
        add(P(n + 'Sleeve', (5, 6, 5), (-2.5, -6, -2.5), parent=n, style='robe_sea'))
    add(P('staff', (2, 36, 2), (-1, -14, -1), (0, -11, 0), rot=(0.6, 0, 0), parent='armR', style='wood'))
    add(P('conch', (5, 7, 5), (-2.5, 22, -2.5), parent='staff', style='coral'))
    add(P('conchTip', (3, 4, 3), (-1.5, 29, -1.5), parent='staff', style='pearl'))
    add(P('staffOrb', (3, 3, 3), (-1.5, 18, -1.5), parent='staff', style='water_glow', anim='pulse'))
    add(P('orbitRoot', (2, 2, 2), (-1, -1, -1), (0, 22, 0), style='void', anim='spin'))
    for k in range(3):
        a = k * 2 * math.pi / 3
        add(P(f'orb{k}', (4, 4, 4), (-2, -2, -2), (11 * math.cos(a), 4 * math.sin(a * 2), 11 * math.sin(a)), parent='orbitRoot', style='water_glow'))
    return parts


def razorclaw(P):
    """Fast: a reef crab the size of a horse, with a barnacled shell, eye-stalks and two hooked pincers."""
    parts = []
    add = parts.append
    add(P('body', (18, 7, 14), (-9, 0, -7), (0, 8, 0), style='coral'))
    add(P('shell', (20, 3, 16), (-10, 6, -8), parent='body', style='shell'))
    add(P('shellRidge', (12, 2, 10), (-6, 9, -5), parent='body', style='coral'))
    for k, (x, z, s) in enumerate([(-6, -3, 3), (4, 2, 4), (0, -5, 2), (7, -4, 2)]):
        add(P(f'barn{k}', (s, 2, s), (x - s / 2, 10.5, z - s / 2), parent='body', style='barnacle'))
    for k, x in enumerate((-7, -3.5, 3.5, 7)):
        add(P(f'spike{k}', (2, 2, 4), (-1, -1, 0), (x, 4, 7), rot=(-0.3, 0, 0), parent='body', style='bone_d'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('stalk' + nm, (1, 6, 1), (-0.5, 0, -0.5), (sx * 3, 6, 6), rot=(0.3, 0, -sx * 0.2), parent='body', style='coral', anim='head'))
        add(P('eye' + nm, (2, 2, 2), (-1, 6, -1), parent='stalk' + nm, style='abyss_glow'))
        for k in range(4):
            leg = f'leg{nm}{k}'
            ang = (k - 1.5) * 0.35
            add(P(leg, (10, 2, 2), (side_box(sx, 10), -1, -1), (sx * 8, 3, 4 - 3.5 * k), rot=(0, sx * ang, -sx * 0.35),
                  parent='body', style='coral', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
            add(P(leg + 'Tip', (2, 9, 2), (-1, -9, -1), (sx * 10, 0, 0), rot=(0, 0, sx * 0.25), parent=leg, style='shell' if k % 2 else 'coral'))
        c = 'claw' + nm
        add(P(c, (4, 4, 9), (-2, -2, 0), (sx * 7, 4, 6), rot=(0.1, sx * 0.4, 0), parent='body', style='coral', anim='armA' if sx < 0 else 'armB'))
        add(P(c + 'Palm', (7, 6, 9), (-3.5, -3, 0), (0, 0, 8), rot=(0, -sx * 0.5, 0), parent=c, style='coral'))
        add(P(c + 'Upper', (4, 3, 9), (-2, 0, 0), (0, 1, 8), rot=(-0.25, 0, 0), parent=c + 'Palm', style='coral'))
        add(P(c + 'Lower', (3, 2, 8), (-1.5, -2, 0), (0, -2, 8), rot=(0.25, 0, 0), parent=c + 'Palm', style='bone_d'))
        add(P(c + 'Barn', (3, 2, 3), (-1.5, 2.5, 2), parent=c + 'Palm', style='barnacle'))
    return parts


# ====================================================================================== Rimefast guards
def rimeguard(P):
    """Heavy: an ice knight with a crest of icicles, a tower shield of blue ice and a frost glaive."""
    parts = []
    add = parts.append
    for sx in (-1, 1):
        n = 'leg' + side_name(sx)
        add(P(n, (5, 13, 5), (-2.5, -13, -2.5), (sx * 3.2, 13, 0), style='ice_armor', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Greave', (6, 6, 2), (-3, -10, 2.5), parent=n, style='ice'))
    add(P('body', (13, 14, 8), (-6.5, 0, -4), (0, 13, 0), style='ice_armor'))
    add(P('tabard', (7, 12, 1), (-3.5, -9, 4), parent='body', style='shroud'))
    add(P('cape', (12, 24, 1), (-6, -22, -5), (0, 13, 0), rot=(0.1, 0, 0), parent='body', style='fur_w'))
    add(P('collar', (14, 4, 9), (-7, 12, -4.5), parent='body', style='fur_w'))
    add(P('head', (8, 9, 8), (-4, 0, -4), (0, 27, 0), style='ice_armor', anim='head'))
    add(P('visor', (6, 1, 1), (-3, 4, 4.1), parent='head', style='frost_glow'))
    for k in range(5):
        add(P(f'crest{k}', (1, 5 + (2 - abs(k - 2)) * 3, 1), (-0.5, 0, -0.5), (0, 8, -3 + 1.5 * k), rot=(-0.5 + 0.25 * k, 0, 0), parent='head', style='ice'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('pauldron' + nm, (7, 4, 8), (-3.5, 0, -4), (sx * 9, 25, 0), style='ice_armor'))
        for k in range(3):
            add(P(f'frost{nm}{k}', (1, 4 + k, 1), (-0.5, 0, -0.5), (sx * (1 + k), 4, -2 + 2 * k), rot=(0, 0, -sx * (0.3 + 0.2 * k)), parent='pauldron' + nm, style='ice'))
        a = 'arm' + nm
        add(P(a, (4, 13, 4), (-2, -13, -2), (sx * 8.5, 25, 0), rot=(-0.45 if sx < 0 else -0.25, 0, 0), style='ice_armor', anim='armA' if sx < 0 else 'armB'))
    add(P('shield', (2, 22, 14), (-1, -12, -7), (2.5, -10, 0), rot=(0.25, 0, 0), parent='armL', style='ice'))
    add(P('shieldBoss', (1, 6, 6), (1, -3, -3), parent='shield', style='frost_glow'))
    add(P('shieldRim', (3, 2, 16), (-1.5, 9, -8), parent='shield', style='ice_armor'))
    add(P('glaive', (2, 34, 2), (-1, -10, -1), (0, -12, 0), rot=(0.25, 0, 0), parent='armR', style='steel'))
    add(P('glaiveBlade', (1, 12, 5), (-0.5, 24, -1), parent='glaive', style='ice'))
    add(P('glaiveEdge', (1, 10, 1), (-0.5, 25, 3.5), parent='glaive', style='frost_glow'))
    return parts


def hushwraith(P):
    """Special: a floating hooded wraith with a stitched-shut mouth, a raised finger, and a cracked silent bell."""
    parts = []
    add = parts.append
    add(P('body', (10, 14, 7), (-5, 0, -3.5), (0, 12, 0), style='shroud_d'))
    for i in range(12):
        a = i * 2 * math.pi / 12
        ln = 14 + (i % 3) * 3
        add(P(f'tatter{i}', (3, ln, 1), (-1.5, -ln, -0.5), (5 * math.sin(a), 12, 4 * math.cos(a)), rot=(0, a, 0), style='shroud' if i % 2 else 'shroud_d', anim='sway'))
    add(P('hood', (10, 11, 10), (-5, 0, -5), (0, 26, 0), style='shroud_d', anim='head'))
    add(P('hoodPeak', (6, 5, 6), (-3, 10, -5), parent='hood', style='shroud_d'))
    add(P('face', (8, 8, 1), (-4, 1, 4.6), parent='hood', style='void'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (1, 1, 1), (sx * 2 - 0.5, 5, 5.2), parent='hood', style='frost_glow'))
    add(P('stitch', (6, 1, 1), (-3, 2, 5.3), parent='hood', style='bone'))
    for k in range(4):
        add(P(f'stitchX{k}', (1, 3, 1), (-2.5 + 1.6 * k, 1, 5.4), parent='hood', style='bone'))
    for sx in (-1, 1):
        n = 'arm' + side_name(sx)
        raised = sx < 0
        add(P(n, (3, 14, 3), (-1.5, -14, -1.5), (sx * 6.5, 25, 0), rot=((-2.5 if raised else -0.2), 0, -sx * 0.25), style='shroud', anim='none' if raised else 'armB'))
        add(P(n + 'Hand', (3, 4, 2), (-1.5, -18, -1), parent=n, style='bone_d'))
        for k in range(3):
            ln = 8 if (raised and k == 1) else 5
            add(P(f'{n}Finger{k}', (1, ln, 1), (-0.5, -ln, -0.5), (-1 + k, -18, 0), rot=(0 if raised else 0.3, 0, 0), parent=n, style='bone'))
    add(P('bell', (5, 6, 5), (-2.5, -6, -2.5), (3, 14, 4), parent='body', style='gold_d', anim='sway'))
    add(P('bellCrack', (1, 5, 1), (-0.5, -5.5, 2.6), parent='bell', style='void'))
    return parts


def rimefang(P):
    """Fast: a gaunt white wolf with a visible ribcage, icicle spines and frost in its throat."""
    parts = []
    add = parts.append
    add(P('body', (8, 8, 18), (-4, 0, -9), (0, 11, 0), style='fur_w'))
    add(P('ribs', (9, 6, 8), (-4.5, 0.5, 0), parent='body', style='bone'))
    add(P('chest', (10, 10, 7), (-5, -1, 2), parent='body', style='fur_w'))
    for k in range(6):
        add(P(f'spine{k}', (1, 4 + (k % 2) * 2, 1), (-0.5, 0, -0.5), (0, 8, 6 - 3 * k), rot=(-0.5, 0, 0), parent='body', style='ice'))
    add(P('head', (8, 7, 8), (-4, -3.5, 0), (0, 19, 10), style='fur_w', anim='head'))
    add(P('snout', (5, 4, 7), (-2.5, -3.5, 8), parent='head', style='bone'))
    add(P('jaw', (4, 2, 6), (-2, -5, 8), parent='head', style='bone_d', anim='jaw'))
    add(P('breath', (3, 2, 2), (-1.5, -3, 14.6), parent='head', style='frost_glow'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('eye' + nm, (1, 1, 1), (sx * 2.5 - 0.5, 0.5, 7.6), parent='head', style='frost_glow'))
        add(P('ear' + nm, (2, 4, 1), (sx * 2.5 - 1, 3.5, 2), rot=(-0.3, 0, 0), parent='head', style='fur_w'))
        add(P('fang' + nm, (1, 3, 1), (sx * 1.5 - 0.5, -6, 13), parent='head', style='ice'))
    for k, (x, z, an) in enumerate([(-3, 6, 'legA'), (3, 6, 'legB'), (-3, -6, 'legB'), (3, -6, 'legA')]):
        n = f'leg{k}'
        add(P(n, (3, 11, 3), (-1.5, -11, -1.5), (x, 11, z), style='fur_w', anim=an))
        add(P(n + 'Paw', (3, 2, 4), (-1.5, -11, -1), parent=n, style='bone_d'))
    add(P('tail', (2, 2, 12), (-1, -1, -12), (0, 17, -9), rot=(-0.6, 0, 0), style='fur_w', anim='sway'))
    add(P('tailIce', (1, 1, 4), (-0.5, -0.5, -16), parent='tail', style='ice'))
    return parts


# ====================================================================================== Sunscar guards
def sandglass(P):
    """Heavy: a red-sandstone colossus with an hourglass heart, a slit visor, and fists studded with glass."""
    parts = []
    add = parts.append
    for sx in (-1, 1):
        n = 'leg' + side_name(sx)
        add(P(n, (7, 13, 7), (-3.5, -13, -3.5), (sx * 5, 13, 0), style='sandstone_r', anim='legA' if sx < 0 else 'legB'))
        add(P(n + 'Band', (8, 2, 8), (-4, -7, -4), parent=n, style='gold_d'))
    add(P('body', (22, 18, 13), (-11, 0, -6.5), (0, 13, 0), style='sandstone_r'))
    add(P('coreFrame', (8, 12, 2), (-4, 3, 6), parent='body', style='gold_d'))
    add(P('coreUp', (4, 4, 1), (-2, 9, 7.5), parent='body', style='sand_glow', anim='pulse'))
    add(P('coreLow', (6, 3, 1), (-3, 4, 7.5), parent='body', style='sand_glow', anim='pulse'))
    add(P('head', (9, 8, 9), (-4.5, 0, -4.5), (0, 31, 0), style='sandstone_r', anim='head'))
    add(P('visor', (7, 1, 1), (-3.5, 4, 4.6), parent='head', style='glass_glow'))
    add(P('crest', (2, 5, 9), (-1, 8, -4.5), parent='head', style='glass_red'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('obelisk' + nm, (5, 12, 5), (-2.5, 0, -2.5), (sx * 13, 29, -1), rot=(0, 0, -sx * 0.15), style='sandstone_r'))
        add(P('obeliskTip' + nm, (3, 5, 3), (-1.5, 12, -1.5), parent='obelisk' + nm, style='glass_red'))
        a = 'arm' + nm
        add(P(a, (8, 18, 8), (-4, -18, -4), (sx * 15, 28, 0), rot=(-0.2, 0, -sx * 0.08), style='sandstone_r', anim='armA' if sx < 0 else 'armB'))
        add(P(a + 'Fist', (10, 8, 10), (-5, -26, -5), parent=a, style='sandstone_r'))
        for k in range(3):
            add(P(f'{a}Shard{k}', (2, 5, 2), (-3 + 3 * k - 1, -24, 4.5), rot=(0.5, 0, 0), parent=a, style='glass_red'))
    return parts


def sunseer(P):
    """Special: a veiled priest in crimson and sand, a gold mask, a halo of sun-rays, and a mirror-topped staff."""
    parts = []
    add = parts.append
    add(P('robe', (12, 12, 9), (-6, 0, -4.5), (0, 0, 0), style='robe_red'))
    add(P('robe2', (10, 10, 7), (-5, 0, -3.5), (0, 12, 0), style='sand'))
    add(P('sash', (11, 3, 8), (-5.5, 0, -4), (0, 14, 0), style='gold_d'))
    add(P('chest', (10, 8, 6), (-5, 0, -3), (0, 22, 0), style='robe_red'))
    add(P('head', (8, 8, 8), (-4, 0, -4), (0, 30, 0), style='robe_d', anim='head'))
    add(P('mask', (6, 6, 1), (-3, 1, 4), parent='head', style='gold_d'))
    for sx in (-1, 1):
        add(P('eye' + side_name(sx), (1, 1, 1), (sx * 1.5 - 0.5, 4, 4.4), parent='head', style='sun_glow'))
    add(P('veil', (8, 4, 1), (-4, -3, 4.2), parent='head', style='robe_red'))
    add(P('haloRoot', (2, 2, 2), (-1, -1, -1), (0, 34, -5), style='void', anim='spin'))
    for k in range(10):
        a = k * 2 * math.pi / 10
        add(P(f'ray{k}', (2, 6 + (k % 2) * 3, 1), (-1, 0, -0.5), (6 * math.cos(a), 0, 6 * math.sin(a)), rot=(0, -a, 0), parent='haloRoot', style='sun_glow' if k % 2 else 'gold_d'))
    for sx in (-1, 1):
        n = 'arm' + side_name(sx)
        add(P(n, (3, 12, 3), (-1.5, -12, -1.5), (sx * 6.5, 29, 0), rot=(-0.5 if sx < 0 else -0.15, 0, -sx * 0.1), style='robe_red', anim='armA' if sx < 0 else 'armB'))
        add(P(n + 'Cuff', (4, 3, 4), (-2, -12, -2), parent=n, style='gold_d'))
    add(P('staff', (2, 38, 2), (-1, -14, -1), (0, -12, 0), rot=(0.5, 0, 0), parent='armR', style='haft'))
    add(P('mirrorFrame', (9, 9, 2), (-4.5, 24, -1), parent='staff', style='gold_d'))
    add(P('mirror', (7, 7, 1), (-3.5, 25, 0.6), parent='staff', style='sun_glow'))
    return parts


def scarab(P):
    """Fast: a beetle the size of a pony, with a horn, mandibles, and wing-cases of red glass."""
    parts = []
    add = parts.append
    add(P('body', (12, 7, 16), (-6, 0, -8), (0, 6, 0), style='chitin'))
    add(P('thorax', (10, 6, 6), (-5, 0.5, 0), (0, 6, 8), style='chitin'))
    add(P('head', (7, 5, 5), (-3.5, 0, 0), (0, 7, 13), style='chitin', anim='head'))
    add(P('horn', (2, 9, 2), (-1, 0, -1), (0, 4, 4), rot=(0.6, 0, 0), parent='head', style='gold_d'))
    add(P('hornTip', (2, 4, 2), (-1, 0, -1), (0, 9, 0), rot=(-0.6, 0, 0), parent='horn', style='glass_red'))
    for sx in (-1, 1):
        nm = side_name(sx)
        add(P('eye' + nm, (1, 2, 2), (sx * 3.6 - 0.5, 2, 2), parent='head', style='glass_glow'))
        add(P('mandible' + nm, (2, 2, 5), (-1, -1, 0), (sx * 2, 1, 5), rot=(0, -sx * 0.4, 0), parent='head', style='bone_d', anim='jaw'))
        add(P('elytra' + nm, (7, 3, 17), (side_box(sx, 7), 0, -15), (sx * 0.5, 7, 7), rot=(0.05, sx * 0.08, -sx * 0.18), parent='body', style='glass_red'))
        add(P('elytraEdge' + nm, (1, 3, 15), (sx * 6.5 - 0.5 if sx > 0 else -7, 0.3, -14), parent='elytra' + nm, style='glass_glow'))
        for k in range(3):
            leg = f'leg{nm}{k}'
            add(P(leg, (7, 2, 2), (side_box(sx, 7), -1, -1), (sx * 5, 1, 4 - 5 * k), rot=(0, sx * (0.4 - 0.4 * k), -sx * 0.3), parent='body',
                  style='chitin', anim='legA' if (k + (sx > 0)) % 2 else 'legB'))
            add(P(leg + 'Tip', (2, 7, 2), (-1, -7, -1), (sx * 7, 0, 0), rot=(0, 0, sx * 0.2), parent=leg, style='gold_d'))
    return parts


MOBS = {
    # Wardens
    'vorath': dict(parts='vorath', seed=21, shadow=3.0),
    'white_silence': dict(parts='white_silence', seed=22, shadow=1.2),
    'kharzul': dict(parts='kharzul', seed=23, shadow=1.6),
    # guards
    'coralclad_juggernaut': dict(parts=coralclad, seed=31, shadow=0.9),
    'tidecaller': dict(parts=tidecaller, seed=32, shadow=0.5),
    'razorclaw': dict(parts=razorclaw, seed=33, shadow=0.8),
    'rimeguard': dict(parts=rimeguard, seed=34, shadow=0.6),
    'hushwraith': dict(parts=hushwraith, seed=35, shadow=0.4),
    'rimefang': dict(parts=rimefang, seed=36, shadow=0.6),
    'sandglass_sentinel': dict(parts=sandglass, seed=37, shadow=1.0),
    'sunseer': dict(parts=sunseer, seed=38, shadow=0.5),
    'glasswing_scarab': dict(parts=scarab, seed=39, shadow=0.7),
}


def register(mobs, styles, glow_styles, part):
    styles.update(STYLES)
    glow_styles.update(GLOW)
    for key, m in MOBS.items():
        fn = m['parts']
        if isinstance(fn, str):
            fn = getattr(bosses_act2, fn)
        mobs[key] = dict(parts=(lambda f=fn: f(part)), seed=m['seed'], shadow=m['shadow'])
