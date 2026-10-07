"""The eight realm armor sets as 3D worn models: oversized plate with horns, antlers, wings, crowns, fins, gears and caps.

Authored in the box-model space used everywhere else (units of 1/16 block, y up, front +z), relative to the player's own parts:
head and body pivot at the neck, arms at (+-5, -2, 0), legs at (+-1.9, -12, 0). Each piece is its own model, so a helmet only
ever carries the helmet's decorations. Writes ArmorModels.java (layer definitions), one texture per piece, and preview parts.
"""
import math

import mobspecs
from kit_data import KIT, PIECES, REALMS

ROOTS = {'head': (0, 0, 0), 'hat': (0, 0, 0), 'body': (0, 0, 0), 'right_arm': (-5, -2, 0), 'left_arm': (5, -2, 0),
         'right_leg': (-1.9, -12, 0), 'left_leg': (1.9, -12, 0)}
STYLE = {   # base plate, trim, dark, glow, and the realm's special material
    'grove': ('bark', 'moss', 'bark_d', 'glowg', 'moss_l'),
    'skyreach': ('quartz', 'gold', 'storm_l', 'rune_cyan', 'feather_w'),
    'hollow': ('king_armor', 'steel', 'ash_armor', 'rune_orange', 'horn'),
    'drowned': ('plate_g', 'pearl', 'navy_d', 'water_glow', 'coral'),
    'pale': ('ice_armor', 'ice', 'ice_d', 'frost_glow', 'fur_w'),
    'scarlet': ('sandstone_r', 'gold', 'robe_red', 'sun_glow', 'glass_red'),
    'clockwork': ('iron_dk', 'brass', 'brass_d', 'rift_glow', 'clockface'),
    'mycelial': ('petal_c', 'cap_m', 'flesh_p', 'bloom_glow', 'root_c'),
    'unmade': ('regalia_w', 'gold', 'regalia_b', 'accretion2', 'abyss'),
}
SHARDS = ['shard_g', 'shard_c', 'shard_v', 'shard_t', 'shard_i', 'shard_r', 'shard_y', 'shard_m']   # one stone per realm, in realm order
SETS = REALMS + ['unmade']                                           # the eight realm sets, then the Unmaker's
ARMOR_ID = dict({r: KIT[r]['armor'] for r in REALMS}, unmade='unmade')


class Piece:
    def __init__(self):
        self.parts = []

    def add(self, name, size, origin, pivot=(0, 0, 0), rot=(0, 0, 0), style='bark', parent='head'):
        self.parts.append(dict(name=name, size=tuple(max(1, int(round(s))) for s in size), origin=tuple(origin), pivot=tuple(pivot),
                               rot=tuple(rot), style=style, anim='none', eyes=None, parent=parent))
        return name


def side(sx):
    return 'R' if sx < 0 else 'L'


# ------------------------------------------------------------------------------------------------ shared plate
def helm_base(p, st):
    base, trim, dark, glow, special = st
    p.add('helm', (10, 10, 10), (-5, -1, -5), style=base)
    p.add('helmBrow', (11, 2, 2), (-5.5, 5, 4.5), style=trim)
    p.add('helmVisor', (6, 1, 1), (-3, 3.5, 5.2), style=glow)
    p.add('helmCrest', (2, 3, 10), (-1, 9, -5), style=trim)


def chest_base(p, st):
    base, trim, dark, glow, special = st
    p.add('plate', (10, 14, 6), (-5, -13, -3), style=base, parent='body')
    p.add('plateBand', (11, 2, 7), (-5.5, -9, -3.5), style=trim, parent='body')
    p.add('plateCore', (3, 3, 1), (-1.5, -6, 3.1), style=glow, parent='body')
    p.add('armR', (6, 14, 6), (-4, -11, -3), style=base, parent='right_arm')
    p.add('armL', (6, 14, 6), (-2, -11, -3), style=base, parent='left_arm')


def legs_base(p, st):
    base, trim, dark, glow, special = st
    p.add('belt', (10, 4, 6), (-5, -13, -3), style=trim, parent='body')
    p.add('buckle', (2, 2, 1), (-1, -12, 3.1), style=glow, parent='body')
    for leg, x0 in (('right_leg', -2.5), ('left_leg', -2.5)):
        p.add('thigh' + leg[0].upper(), (5, 8, 5), (x0, -8, -2.5), style=base, parent=leg)
        p.add('knee' + leg[0].upper(), (5, 2, 2), (x0, -9, 2), style=trim, parent=leg)


def boots_base(p, st):
    base, trim, dark, glow, special = st
    for leg in ('right_leg', 'left_leg'):
        L = leg[0].upper()
        p.add('boot' + L, (6, 6, 6), (-3, -13, -3), style=dark, parent=leg)
        p.add('toe' + L, (6, 2, 3), (-3, -13, 2.5), style=base, parent=leg)
        p.add('cuff' + L, (7, 2, 7), (-3.5, -8, -3.5), style=trim, parent=leg)


def pauldrons(p, st, w=9, h=5, d=9, spikes=0, spike_style=None, extra=None):
    base, trim, dark, glow, special = st
    for arm, sx in (('right_arm', -1), ('left_arm', 1)):
        L = side(sx)
        cx = -1 if sx < 0 else 1
        p.add('paul' + L, (w, h, d), (-w / 2 + cx, 0, -d / 2), (0, 0, 0), rot=(0, 0, -sx * 0.18), style=base, parent=arm)
        p.add('paulRim' + L, (w + 1, 2, d + 1), (-(w + 1) / 2 + cx, -1, -(d + 1) / 2), rot=(0, 0, -sx * 0.18), style=trim, parent=arm)
        for k in range(spikes):
            z = -d / 2 + 1.5 + k * (d - 3) / max(1, spikes - 1)
            p.add(f'paulSpike{L}{k}', (2, 7 - abs(k - (spikes - 1) / 2) * 1.5, 2), (-1, 0, -1), (cx + sx * 1.5, h - 0.5, z),
                  rot=(0, 0, -sx * 0.45), style=spike_style or trim, parent=arm)
        if extra:
            extra(p, arm, sx, L)


# ------------------------------------------------------------------------------------------------ the eight sets
def verdant(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        p.add('mossCrown', (11, 2, 11), (-5.5, 9, -5.5), style='moss')
        for sx in (-1, 1):                                           # a great antler rack, three tines on each beam
            L = side(sx)
            b1 = p.add('antler' + L, (2, 9, 2), (-1, 0, -1), (sx * 4, 8, -1), rot=(-0.15, 0, -sx * 0.55), style='bark')
            b2 = p.add('antler2' + L, (2, 8, 2), (-1, 0, -1), (0, 9, 0), rot=(-0.25, 0, sx * 0.35), parent=b1, style='bark')
            p.add('antler3' + L, (1.5, 6, 1.5), (-0.75, 0, -0.75), (0, 8, 0), rot=(-0.3, 0, -sx * 0.4), parent=b2, style='bark_d')
            for k, (y, a) in enumerate([(3, 0.9), (6, 0.7)]):
                p.add(f'tine{L}{k}', (1.5, 6, 1.5), (-0.75, 0, -0.75), (0, y, 0), rot=(0.5, 0, -sx * a), parent=b2, style='bark_d')
            p.add('tine0' + L, (1.5, 5, 1.5), (-0.75, 0, -0.75), (0, 6, 0), rot=(0.6, 0, -sx * 0.9), parent=b1, style='bark_d')
            p.add('leaf' + L, (4, 1, 3), (-2, 0, -1.5), (sx * 5, 9, 2), rot=(0.3, 0, sx * 0.4), style='moss_l')
        p.add('shroomStem', (1, 2, 1), (2.5, 11, -1), style='root_c')
        p.add('shroomCap', (4, 1, 4), (1, 13, -2.5), style='cap')
        p.add('eyeGlow', (7, 1, 1), (-3.5, 3.5, 5.3), style=glow)
    elif piece == 'chestplate':
        chest_base(p, st)
        def shrooms(p, arm, sx, L):
            p.add('pShroomS' + L, (1, 3, 1), (-0.5, 0, -0.5), (sx * 1, 5, 1), parent=arm, style='root_c')
            p.add('pShroomC' + L, (4, 1, 4), (-2, 3, -2), (sx * 1, 5, 1), parent=arm, style='cap')
            p.add('pMoss' + L, (6, 2, 6), (-3, 4, -3), (sx * 1, 0, -1), parent=arm, style='moss')
        pauldrons(p, st, 10, 5, 9, spikes=3, spike_style='thorn', extra=shrooms)
        for k in range(5):                                           # a ridge of thorned roots up the back
            p.add(f'backRoot{k}', (2, 8 - k, 2), (-1, 0, -1), (-3 + k * 1.5, -11 + k * 2.2, -3), rot=(-0.6, 0, 0.3 - k * 0.15), parent='body', style='bark')
        p.add('vineFront', (8, 1, 1), (-4, -4, 3.1), rot=(0, 0, 0.25), parent='body', style='moss_l')
        p.add('vineFront2', (8, 1, 1), (-4, -10, 3.1), rot=(0, 0, -0.25), parent='body', style='moss_l')
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('tasset' + side(sx), (5, 6, 1), (-2.5, -6, 2.6), parent=leg, style='bark_d')
            p.add('leafTasset' + side(sx), (4, 4, 1), (-2, -9, 3), rot=(0.2, 0, 0), parent=leg, style='moss_l')
    else:
        boots_base(p, st)
        for leg in ('right_leg', 'left_leg'):
            L = leg[0].upper()
            for k, x in enumerate((-2, 0, 2)):
                p.add(f'rootClaw{L}{k}', (1, 1, 4), (-0.5, 0, 0), (x, -13, 4.5), rot=(0.4, 0, 0), parent=leg, style='bark_d')
    return p


def stormglass(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        for sx in (-1, 1):                                           # tall swept wings either side of the helm
            L = side(sx)
            w = p.add('hwing' + L, (1, 12, 5), (-0.5, 0, -2.5), (sx * 5.2, 3, -1), rot=(-0.35, 0, -sx * 0.35), style='feather_w')
            p.add('hwing2' + L, (1, 9, 4), (-0.5, 0, -2), (0, 11, -1), rot=(-0.4, 0, -sx * 0.2), parent=w, style='feather_w')
            p.add('hwingRib' + L, (1.5, 12, 1), (-0.75, 0, 2), (0, 0, 0), parent=w, style=trim)
        p.add('crestBlade', (1, 8, 12), (-0.5, 10, -7), style=glow)
        p.add('halo', (12, 1, 12), (-6, 13, -6), rot=(0.2, 0, 0), style=trim)
    elif piece == 'chestplate':
        chest_base(p, st)
        pauldrons(p, st, 9, 4, 9, spikes=2, spike_style='ice')
        for sx in (-1, 1):                                           # great angel wings from the shoulder blades
            L = side(sx)
            r = p.add('wingRoot' + L, (2, 2, 2), (-1, -1, -1), (sx * 3, -3, -3), rot=(0.3, sx * 0.5, -sx * 0.3), parent='body', style=trim)
            prev = r
            for k, (ln, h) in enumerate([(10, 14), (10, 12), (9, 9)]):
                prev = p.add(f'wing{L}{k}', (ln, h, 1), (-ln / 2 + sx * ln / 2, -h + 4, -0.5), (sx * (0 if k == 0 else ln - 1), 2 if k else 0, 0),
                             rot=(0, 0, -sx * 0.25), parent=prev, style='feather_w' if k % 2 == 0 else 'ray_top')
            p.add('wingGlow' + L, (14, 1, 1), (-7 + sx * 7, 3, 0.6), parent=r, style=glow)
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('feathTasset' + side(sx), (1, 7, 4), (-0.5, -7, -2), (sx * 2.8, 0, 0), rot=(0, 0, sx * 0.2), parent=leg, style='feather_w')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('ankleWing' + side(sx), (1, 6, 4), (-0.5, 0, -2), (sx * 3.2, -10, -1), rot=(-0.6, 0, -sx * 0.5), parent=leg, style='feather_w')
    return p


def emberheart(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        for sx in (-1, 1):                                           # great down-curving demon horns
            L = side(sx)
            h1 = p.add('horn' + L, (3, 3, 7), (-1.5, -1.5, -7), (sx * 4.5, 6, -1), rot=(0.3, sx * 1.1, 0), style='horn')
            h2 = p.add('horn2' + L, (2.5, 2.5, 6), (-1.25, -1.25, -6), (0, 0, -7), rot=(-0.7, 0, 0), parent=h1, style='horn')
            p.add('horn3' + L, (1.5, 1.5, 5), (-0.75, -0.75, -5), (0, 0, -6), rot=(-0.8, 0, 0), parent=h2, style='bone')
        for k in range(5):                                           # a crown of burning spikes
            a = math.pi * (0.15 + 0.7 * k / 4)
            p.add(f'flame{k}', (1.5, 5 + (k % 2) * 3, 1.5), (-0.75, 0, -0.75), (4.5 * math.cos(a), 9, -4.5 * math.sin(a) + 1),
                  rot=(-0.2, 0, (math.cos(a)) * -0.4), style='flame')
        p.add('maw', (6, 2, 1), (-3, 1, 5.1), style=glow)
    elif piece == 'chestplate':
        chest_base(p, st)
        pauldrons(p, st, 10, 6, 10, spikes=4, spike_style='horn')
        for k in range(3):                                           # chimney vents on the back, glowing
            p.add(f'vent{k}', (2.5, 7, 2.5), (-1.25, 0, -1.25), (-3 + k * 3, -6, -3.5), rot=(-0.4, 0, (k - 1) * 0.25), parent='body', style=dark)
            p.add(f'ventGlow{k}', (2, 1, 2), (-1, 7, -1), (-3 + k * 3, -6, -3.5), rot=(-0.4, 0, (k - 1) * 0.25), parent='body', style='flame')
        for (x0, y0, x1, y1) in [(-4, -12, -3, -4), (-3, -8, 2, -7), (2, -6, 3, 0), (-1, -3, 0, 0)]:
            p.add(f'crack{x0}{y0}', (x1 - x0, y1 - y0, 1), (x0, y0, 3.05), parent='body', style=glow)
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('kneeSpike' + side(sx), (1.5, 1.5, 4), (-0.75, -0.75, 0), (0, -8, 2.5), rot=(0.3, 0, 0), parent=leg, style='horn')
            p.add('lavaSeam' + side(sx), (1, 7, 1), (-0.5, -7, 2.55), parent=leg, style=glow)
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('heelSpike' + side(sx), (1.5, 1.5, 5), (-0.75, -0.75, -5), (0, -11, -3), rot=(-0.5, 0, 0), parent=leg, style='horn')
            p.add('emberToe' + side(sx), (5, 1, 1), (-2.5, -12, 5.6), parent=leg, style='flame')
    return p


def tidestone(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        p.add('dorsalFin', (1, 9, 12), (-0.5, 9, -7), rot=(-0.2, 0, 0), style='fin')
        p.add('finGlow', (1.2, 1, 11), (-0.6, 9.2, -6.5), rot=(-0.2, 0, 0), style=glow)
        for sx in (-1, 1):
            L = side(sx)
            p.add('gillFin' + L, (1, 6, 5), (-0.5, 0, -2.5), (sx * 5.3, 2, -1), rot=(0, 0, -sx * 0.6), style='fin')
            c1 = p.add('coral' + L, (2, 6, 2), (-1, 0, -1), (sx * 3.5, 9, 2), rot=(0, 0, -sx * 0.4), style='coral')
            p.add('coral2' + L, (1.5, 4, 1.5), (-0.75, 0, -0.75), (0, 5, 0), rot=(0.4, 0, sx * 0.6), parent=c1, style='coral_b')
        p.add('lure', (1, 6, 1), (-0.5, 0, -0.5), (0, 9, 4.5), rot=(0.9, 0, 0), style=trim)
        p.add('lureBulb', (2, 2, 2), (-1, 6, -1), (0, 9, 4.5), rot=(0.9, 0, 0), style=glow)
    elif piece == 'chestplate':
        chest_base(p, st)
        def shell(p, arm, sx, L):
            for k in range(3):
                p.add(f'barn{L}{k}', (2, 2, 2), (-1, 0, -1), (sx * (k - 1) * 2, 5, (k - 1) * 2.5), parent=arm, style='barnacle')
        pauldrons(p, st, 10, 5, 10, spikes=0, extra=shell)
        p.add('backFin', (1, 10, 9), (-0.5, -6, -9), (0, 0, -2.5), rot=(0.3, 0, 0), parent='body', style='fin')
        for sx in (-1, 1):
            p.add('sideFin' + side(sx), (1, 7, 6), (-0.5, -4, -6), (sx * 4, -6, -2.5), rot=(0.2, -sx * 0.6, 0), parent='body', style='fin')
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('scaleT' + side(sx), (5, 6, 1), (-2.5, -6, 2.6), parent=leg, style='fin')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('flipper' + side(sx), (1, 4, 6), (-0.5, 0, -1), (sx * 3.2, -12, 0), rot=(0, 0, -sx * 0.7), parent=leg, style='fin')
    return p


def rime(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        for k in range(9):                                           # a crown of long icicles fanned like a halo
            a = math.pi * (0.05 + 0.9 * k / 8)
            ln = 7 + 6 * math.sin(a)
            p.add(f'icicle{k}', (1.5, ln, 1.5), (-0.75, 0, -0.75), (5 * math.cos(a), 8, -3.5), rot=(-0.25, 0, -math.cos(a) * 0.8), style='ice')
        p.add('mask', (8, 6, 1), (-4, 1, 5.1), style='mask')
        p.add('maskCrack', (1, 5, 1), (-0.5, 1.5, 5.3), style=glow)
        p.add('furCollar', (12, 2, 12), (-6, -1.5, -6), style='fur_w')
    elif piece == 'chestplate':
        chest_base(p, st)
        pauldrons(p, st, 10, 5, 10, spikes=4, spike_style='ice')
        for k in range(7):                                           # a cape of hanging icicles
            x = -4 + k * 1.35
            p.add(f'capeIce{k}', (1.4, 10 + (k % 3) * 3, 1), (-0.7, -(10 + (k % 3) * 3), -0.5), (x, -1, -3.6), rot=(0.1, 0, 0), parent='body', style='ice')
        p.add('furMantle', (12, 3, 8), (-6, -2, -4), parent='body', style='fur_w')
        p.add('heartIce', (3, 3, 1), (-1.5, -7, 3.1), parent='body', style=glow)
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('kneeIce' + side(sx), (1.5, 4, 1.5), (-0.75, 0, -0.75), (0, -9, 2.5), rot=(0.6, 0, 0), parent=leg, style='ice')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            for k in range(3):
                p.add(f'bootIce{side(sx)}{k}', (1.2, 4, 1.2), (-0.6, 0, -0.6), (sx * 3, -10 + k * 1.5, -2 + k * 2), rot=(0, 0, -sx * 0.8), parent=leg, style='ice')
            p.add('fur' + side(sx), (7, 2, 7), (-3.5, -8, -3.5), parent=leg, style='fur_w')
    return p


def sunglass(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        p.add('sunDisc', (14, 14, 1), (-7, 2, -0.5), (0, 3, -6), style='gold')
        p.add('sunInner', (10, 10, 1), (-5, 4, -0.2), (0, 3, -6), style='sun_glow')
        for k in range(12):                                          # rays of red glass round the disc
            a = k * math.pi / 6
            p.add(f'ray{k}', (1.5, 6, 1), (-0.75, 0, -0.5), (6.5 * math.cos(a), 9 + 6.5 * math.sin(a), -6.2), rot=(0, 0, a - math.pi / 2), style='glass_red')
        for sx in (-1, 1):
            p.add('ear' + side(sx), (2, 7, 2), (-1, 0, -1), (sx * 3.5, 8, 1), rot=(0, 0, -sx * 0.25), style=base)
    elif piece == 'chestplate':
        chest_base(p, st)
        def blades(p, arm, sx, L):
            for k in range(3):
                p.add(f'glassBlade{L}{k}', (1, 9 - k * 2, 3), (-0.5, 0, -1.5), (sx * 2, 4, -3 + k * 3), rot=(0, 0, -sx * (0.5 + k * 0.15)), parent=arm, style='glass_red')
        pauldrons(p, st, 10, 5, 9, extra=blades)
        p.add('hourglassTop', (5, 2, 2), (-2.5, -4, -4), parent='body', style='gold')
        p.add('hourglass', (3, 6, 2), (-1.5, -10, -4.2), parent='body', style='glass_glow')
        p.add('hourglassBot', (5, 2, 2), (-2.5, -12, -4), parent='body', style='gold')
        p.add('sash', (11, 3, 7), (-5.5, -13, -3.5), rot=(0, 0, 0.15), parent='body', style='robe_red')
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('kilt' + side(sx), (5.5, 8, 1), (-2.75, -8, 2.6), parent=leg, style='robe_red')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('glassSpur' + side(sx), (1, 1, 5), (-0.5, -0.5, -5), (sx * 2, -11, -3), rot=(-0.3, sx * 0.3, 0), parent=leg, style='glass_red')
    return p


def chronite(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        p.add('clockCrest', (10, 10, 1), (-5, 0, -0.5), (0, 9, -2), style='clockface')
        p.add('clockRim', (12, 12, 1), (-6, -1, -0.8), (0, 9, -2), style='brass')
        p.add('hourHand', (1, 4, 1), (-0.5, 4, 0.2), (0, 9, -2), rot=(0, 0, 0.9), style='void')
        p.add('minHand', (1, 5, 1), (-0.5, 4, 0.3), (0, 9, -2), style='void')
        for sx in (-1, 1):                                           # cog-wheel horns
            L = side(sx)
            g = p.add('cogHorn' + L, (6, 6, 1.5), (-3, -3, -0.75), (sx * 6, 7, 0), rot=(0, sx * 1.57, 0.4), style='brass_d')
            p.add('cogHorn2' + L, (6, 6, 1.5), (-3, -3, -0.75), (0, 0, 0), rot=(0, 0, 0.78), parent=g, style='brass_d')
            p.add('cogHub' + L, (2, 2, 2), (-1, -1, -1), (0, 0, 0), parent=g, style=glow)
        p.add('eyeSlit', (6, 1, 1), (-3, 3.5, 5.3), style=glow)
    elif piece == 'chestplate':
        chest_base(p, st)
        def cogs(p, arm, sx, L):
            g = p.add('shoulderCog' + L, (8, 8, 1.5), (-4, -4, -0.75), (sx * 2.5, 5, 0), rot=(0, 1.57, 0), parent=arm, style='brass_d')
            p.add('shoulderCog2' + L, (8, 8, 1.5), (-4, -4, -0.75), (0, 0, 0), rot=(0, 0, 0.78), parent=g, style='brass_d')
        pauldrons(p, st, 9, 4, 9, extra=cogs)
        p.add('backClock', (10, 10, 1), (-5, -5, -0.5), (0, -6, -3.8), parent='body', style='clockface')
        p.add('backClockRim', (12, 12, 1), (-6, -6, -0.8), (0, -6, -4.0), parent='body', style='brass')
        p.add('pendulumRod', (1, 9, 1), (-0.5, -9, -0.5), (0, -11, -4), parent='body', style='brass')
        p.add('pendulumBob', (4, 4, 1), (-2, -13, -0.5), (0, -11, -4), parent='body', style=glow)
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('kneeCog' + side(sx), (4, 4, 1), (-2, -2, -0.5), (0, -8, 3), rot=(0, 0, 0.78), parent=leg, style='brass_d')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('spur' + side(sx), (4, 4, 1), (-2, -2, -0.5), (0, -11, -3.5), rot=(0, 1.57, 0.78), parent=leg, style='brass_d')
    return p


def bloomspore(piece, st):
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        helm_base(p, st)
        p.add('capBrim', (20, 2, 20), (-10, 9, -10), style='cap_m')
        p.add('capMid', (15, 3, 15), (-7.5, 11, -7.5), style='cap_m')
        p.add('capTop', (9, 3, 9), (-4.5, 14, -4.5), style='cap_m')
        p.add('gills', (18, 1, 18), (-9, 8.5, -9), style='bloom_glow')
        for k, (x, z) in enumerate([(-6, 4), (5, -5), (7, 3)]):
            p.add(f'miniStem{k}', (1, 2, 1), (-0.5, 0, -0.5), (x, 13, z), style='root_c')
            p.add(f'miniCap{k}', (3, 1, 3), (-1.5, 2, -1.5), (x, 13, z), style='puff')
        for k in range(6):
            a = k * math.pi / 3
            p.add(f'droop{k}', (1, 4, 1), (-0.5, -4, -0.5), (8 * math.cos(a), 9, 8 * math.sin(a)), style='root_c')
        p.add('faceGlow', (6, 1, 1), (-3, 3.5, 5.3), style=glow)
    elif piece == 'chestplate':
        chest_base(p, st)
        def caps(p, arm, sx, L):
            p.add('paulCap' + L, (10, 2, 10), (-5, 6, -5), (sx * 1, 0, 0), parent=arm, style='cap_m')
            p.add('paulCapTop' + L, (6, 2, 6), (-3, 8, -3), (sx * 1, 0, 0), parent=arm, style='cap_m')
        pauldrons(p, st, 8, 5, 8, extra=caps)
        for k, (x, y) in enumerate([(-3, -4), (2, -7), (-1, -11), (3, -2)]):
            p.add(f'sporeSac{k}', (3, 3, 3), (-1.5, -1.5, -1.5), (x, y, -3.8), parent='body', style='bloom_glow')
        for k in range(4):
            p.add(f'rootRib{k}', (10, 1, 1), (-5, 0, -0.5), (0, -2 - k * 3, 3.2), rot=(0, 0, 0.15 * (k % 2 * 2 - 1)), parent='body', style='root_c')
    elif piece == 'leggings':
        legs_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            p.add('gillSkirt' + side(sx), (5.5, 5, 1), (-2.75, -5, 2.6), parent=leg, style='bloom_glow')
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            for k, x in enumerate((-2, 0, 2)):
                p.add(f'rootToe{side(sx)}{k}', (1, 1, 4), (-0.5, 0, 0), (x, -13, 4.5), rot=(0.5, 0, 0), parent=leg, style='root_c')
            p.add('bootCap' + side(sx), (7, 1, 7), (-3.5, -7, -3.5), parent=leg, style='cap_m')
    return p


def unmade(piece, st):
    """The Regalia of the Unmade, cut from the Unmaker's shell: bone-white plate over black, a black hole for a heart, a halo of the
    eight realm stones behind the crown, eight realm blades fanned from the back like broken wings, horns that curl back past the
    shoulders. Every piece carries the eight stones somewhere."""
    p = Piece()
    base, trim, dark, glow, special = st
    if piece == 'helmet':
        p.add('helm', (10, 10, 10), (-5, -1, -5), style=dark)
        p.add('mask', (9, 10, 1), (-4.5, -1.5, 5), style=base)
        p.add('maskSlit', (1, 8, 1), (-0.5, -0.5, 5.6), style=glow)
        for sx in (-1, 1):
            p.add('eye' + side(sx), (2, 1, 1), (sx * 2.5 - 1, 4.5, 5.6), style='accretion')
        p.add('brow', (11, 2, 2), (-5.5, 7.5, 4.5), style=trim)
        p.add('browGem', (3, 3, 1), (-1.5, 7, 6.3), style=special)
        p.add('browGemLight', (1, 1, 1), (-0.5, 8, 6.9), style=glow)
        p.add('crownBand', (11, 2, 11), (-5.5, 9, -5.5), style=trim)
        for k in range(7):                                           # a crown of bone spikes, tallest at the brow
            a = math.pi * (k - 3) / 7
            h = 5 + (3 - abs(k - 3)) * 2.2
            sp = p.add(f'spike{k}', (2, h, 2), (-1, 0, -1), (4.6 * math.sin(a), 10.5, 4.6 * math.cos(a) - 0.5),
                       rot=(0.28 * math.cos(a), 0, -0.28 * math.sin(a)), style=base)
            p.add(f'spikeTip{k}', (1, 2, 1), (-0.5, 0, -0.5), (0, h, 0), parent=sp, style=trim)
        for sx in (-1, 1):                                           # great black horns, sweeping out and curling up past the crown
            L = side(sx)
            h1 = p.add('horn' + L, (4, 8, 4), (-2, 0, -2), (sx * 4.5, 5, -1), rot=(-0.2, 0, -sx * 1.15), style=dark)
            h2 = p.add('horn2' + L, (3, 8, 3), (-1.5, 0, -1.5), (0, 7.5, 0), rot=(-0.1, 0, sx * 0.75), parent=h1, style=dark)
            h3 = p.add('horn3' + L, (2, 7, 2), (-1, 0, -1), (0, 7.5, 0), rot=(0.15, 0, sx * 0.55), parent=h2, style=base)
            p.add('hornTip' + L, (1, 4, 1), (-0.5, 0, -0.5), (0, 6.5, 0), rot=(0.25, 0, sx * 0.3), parent=h3, style=trim)
            p.add('hornBand' + L, (4.5, 1, 4.5), (-2.25, 5, -2.25), parent=h1, style=trim)
            p.add('hornBand2' + L, (3.5, 1, 3.5), (-1.75, 5, -1.75), parent=h2, style=trim)
        halo = p.add('halo', (2, 2, 1), (-1, -1, -0.5), (0, 9, -7.5), style=special)   # the halo of the eight realms
        for k in range(20):
            p.add(f'haloRing{k}', (4, 1, 1), (-2, 11.5, -0.5), (0, 0, 0), rot=(0, 0, k * math.pi / 10), parent=halo, style=trim)
        for k, sh in enumerate(SHARDS):
            a = k * math.pi / 4 + math.pi / 8
            p.add(f'haloStone{k}', (2, 6, 2), (-1, 12.5, -1), (0, 0, 0), rot=(0, 0, a), parent=halo, style=sh)
    elif piece == 'chestplate':
        chest_base(p, st)
        p.add('heart', (6, 6, 2), (-3, -9, 3), style=special, parent='body')            # a black hole where the heart should be
        p.add('heartLight', (2, 2, 1), (-1, -7, 4.6), style=glow, parent='body')
        disc = p.add('disc', (1, 1, 1), (-0.5, -0.5, -0.5), (0, -6, 4.4), parent='body', style=special)
        for k in range(12):
            p.add(f'discSeg{k}', (2.4, 1, 1), (-1.2, 3.6, -0.5), (0, 0, 0), rot=(0, 0, k * math.pi / 6), parent=disc,
                  style='accretion' if k % 2 else 'accretion3')
        for sx in (-1, 1):
            for k, y in enumerate((-2.5, -5, -7.5, -10)):
                p.add(f'rib{side(sx)}{k}', (3, 1, 1), (-1.5, -0.5, -0.5), (sx * 4, y, 3.4), rot=(0, 0, sx * 0.3), parent='body', style=dark)

        def shell(p, arm, sx, L):                                   # Unmaker shell plates stacked on each shoulder
            cx = -1 if sx < 0 else 1
            p.add('shell' + L, (10, 3, 8), (-5, 6, -4), (cx, 0, 0), rot=(0, 0, -sx * 0.35), parent=arm, style='unmade_w2')
            p.add('shell2' + L, (8, 3, 6), (-4, 8.5, -3), (cx, 0, 0), rot=(0, 0, -sx * 0.55), parent=arm, style=base)
            p.add('shellGlow' + L, (1, 1, 8.5), (-0.5, 7.5, -4.25), (cx + sx * 3, 0, 0), parent=arm, style='accretion')
        pauldrons(p, st, 11, 6, 10, spikes=3, spike_style=dark, extra=shell)
        wings = p.add('wingRoot', (5, 5, 2), (-2.5, -2.5, -1), (0, -4, -3.5), parent='body', style=special)
        ring_ = p.add('backRing', (1, 1, 1), (-0.5, -0.5, -0.5), (0, 0, -1.2), parent=wings, style=special)
        for k in range(16):
            p.add(f'backRingSeg{k}', (3, 1, 1), (-1.5, 5.5, -0.5), (0, 0, 0), rot=(0, 0, k * math.pi / 8), parent=ring_,
                  style='accretion' if k % 2 else 'accretion3')
        for k, sh in enumerate(SHARDS):                              # eight realm blades spread like broken wings, four a side
            sx, i = (-1, k) if k < 4 else (1, k - 4)
            a = -sx * (0.75 + i * 0.36)
            b = p.add(f'wing{k}', (3, 5, 2), (-1.5, 1, -1), (0, 0, -1), rot=(-0.3, 0, a), parent=wings, style=base)
            p.add(f'wingBlade{k}', (2, 15 - i * 2, 1), (-1, 5.5, -0.5), (0, 0, 0), parent=b, style=sh)
    elif piece == 'leggings':
        legs_base(p, st)
        p.add('tabard', (6, 7, 1), (-3, -20, 3.2), parent='body', style=dark)
        p.add('tabardGlow', (1, 6, 1), (-0.5, -19.5, 3.6), parent='body', style=glow)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            L = side(sx)
            p.add('tasset' + L, (5, 6, 1), (-2.5, -7, 2.6), parent=leg, style=dark)
            p.add('kneeCap' + L, (5, 3, 3), (-2.5, -10, 1.5), parent=leg, style=trim)
            p.add('kneeSpike' + L, (1, 1, 4), (-0.5, -9, 4), parent=leg, style=dark)
            p.add('thighGlow' + L, (1, 6, 1), (sx * 2.5 - 0.5, -7, -0.5), parent=leg, style='accretion')
            p.add('hipFin' + L, (1, 5, 3), (-0.5, 0, -1.5), (sx * 2.8, -2, 0), rot=(0, 0, -sx * 0.45), parent=leg, style=base)
    else:
        boots_base(p, st)
        for sx, leg in ((-1, 'right_leg'), (1, 'left_leg')):
            L = side(sx)
            for k, x in enumerate((-2, 0, 2)):
                p.add(f'claw{L}{k}', (1, 1, 4), (-0.5, 0, 0), (x, -13, 4.5), rot=(0.45, 0, 0), parent=leg, style=base)
            p.add('heel' + L, (1, 1, 4), (-0.5, -0.5, -4), (0, -12, -3), rot=(-0.35, 0, 0), parent=leg, style=dark)
            for k in range(4):                                       # four realm stones on each cuff: eight across the pair
                a = k * math.pi / 2 + math.pi / 4
                sh = SHARDS[k + (0 if sx < 0 else 4)]
                p.add(f'cuffStone{L}{k}', (1, 2, 1), (-0.5, 0, -0.5), (3.8 * math.cos(a), -7, 3.8 * math.sin(a)), parent=leg, style=sh)
            p.add('ankleFin' + L, (1, 4, 4), (-0.5, 0, -2), (sx * 3.2, -11, 0), rot=(0, 0, -sx * 0.5), parent=leg, style='accretion')
    return p


BUILD = {'grove': verdant, 'skyreach': stormglass, 'hollow': emberheart, 'drowned': tidestone, 'pale': rime, 'scarlet': sunglass,
         'clockwork': chronite, 'mycelial': bloomspore, 'unmade': unmade}


def piece_parts(realm, piece):
    return BUILD[realm](piece, STYLE[realm]).parts


# ------------------------------------------------------------------------------------------------ outputs
def f(v):
    return f'{v:.3f}F'


def build_all():
    out = {}
    for i, realm in enumerate(SETS):
        for j, piece in enumerate(PIECES):
            parts = piece_parts(realm, piece)
            img, sheet = mobspecs.paint(parts, 400 + i * 10 + j)
            img.info.pop('glow', None)
            name = f'{ARMOR_ID[realm]}_{piece}'
            img.save(f'{mobspecs.ASSETS}/textures/models/armor/{name}.png')
            out[name] = (parts, sheet)
    return out


def write_java(built):
    L = ['package com.aurelia.client;', '',
         'import com.aurelia.AureliaMod;',
         'import net.minecraft.client.model.geom.ModelLayerLocation;',
         'import net.minecraft.client.model.geom.PartPose;',
         'import net.minecraft.client.model.geom.builders.CubeListBuilder;',
         'import net.minecraft.client.model.geom.builders.LayerDefinition;',
         'import net.minecraft.client.model.geom.builders.MeshDefinition;',
         'import net.minecraft.client.model.geom.builders.PartDefinition;',
         'import net.minecraft.resources.ResourceLocation;',
         'import net.minecraftforge.client.event.EntityRenderersEvent;', '',
         '/** GENERATED by gen_armor.py. The realm armor sets as worn 3D models, one per piece. Do not edit by hand. */',
         'public final class ArmorModels {',
         '    private ArmorModels() {}', '',
         '    public static ModelLayerLocation layer(String piece) {',
         '        return new ModelLayerLocation(new ResourceLocation(AureliaMod.MODID, "armor_" + piece), "main");',
         '    }', '']
    regs = []
    for name, (parts, sheet) in built.items():
        has_children = {p['parent'] for p in parts}
        L.append(f'    public static LayerDefinition {name}() {{')
        L.append('        MeshDefinition mesh = new MeshDefinition();')
        L.append('        PartDefinition root = mesh.getRoot();')
        for r, (px, py, pz) in ROOTS.items():
            L.append(f'        PartDefinition p_{r} = root.addOrReplaceChild("{r}", CubeListBuilder.create(), '
                     f'PartPose.offset({f(px)}, {f(-py)}, {f(-pz)}));')
        for p in parts:
            w, h, d = p['size']
            x0, y0, z0 = p['origin']
            px, py, pz = p['pivot']
            rx, ry, rz = p['rot']
            u, v = p['uv']
            decl = f'PartDefinition p_{p["name"]} = ' if p['name'] in has_children else ''
            L.append(f'        {decl}p_{p["parent"]}.addOrReplaceChild("{p["name"]}", CubeListBuilder.create().texOffs({u}, {v})'
                     f'.addBox({f(x0)}, {f(-(y0 + h))}, {f(-(z0 + d))}, {w}.0F, {h}.0F, {d}.0F), '
                     f'PartPose.offsetAndRotation({f(px)}, {f(-py)}, {f(-pz)}, {f(rx)}, {f(-ry)}, {f(-rz)}));')
        L.append(f'        return LayerDefinition.create(mesh, {sheet}, {sheet});')
        L.append('    }')
        L.append('')
        regs.append(f'        event.registerLayerDefinition(layer("{name}"), ArmorModels::{name});')
    L.append('    public static void register(EntityRenderersEvent.RegisterLayerDefinitions event) {')
    L += regs
    L.append('    }')
    L.append('}')
    open(__import__('paths').JAVA + '/client/ArmorModels.java', 'w').write('\n'.join(L) + '\n')


def preview_parts(realm, pieces=PIECES, mannequin=True):
    """The pieces as render_models parts, hung on the player's skeleton (the vanilla parts become invisible pivots)."""
    out = []
    for piece in pieces:
        for p in piece_parts(realm, piece):
            q = dict(p)
            q['name'] = piece + '_' + p['name']
            q['parent'] = (piece + '_' + p['parent']) if p['parent'] not in ROOTS else 'root_' + p['parent']
            out.append(q)
    roots = [dict(name='root_' + r, size=(1, 1, 1), origin=(0, 0, 0), pivot=(px, py + 24, pz), rot=(0, 0, 0), style='void', anim='none',
                  eyes=None, parent=None, hidden=True) for r, (px, py, pz) in ROOTS.items()]
    body = []
    if mannequin:                                                    # a dark stand inside, so the silhouette reads
        body = [dict(name='m_' + n, size=s, origin=o, pivot=(0, 0, 0), rot=(0, 0, 0), style='steel', anim='none', eyes=None, parent='root_' + r)
                for n, r, s, o in [('head', 'head', (8, 8, 8), (-4, 0, -4)), ('body', 'body', (8, 12, 4), (-4, -12, -2)),
                                   ('ra', 'right_arm', (4, 12, 4), (-3, -10, -2)), ('la', 'left_arm', (4, 12, 4), (-1, -10, -2)),
                                   ('rl', 'right_leg', (4, 12, 4), (-2, -12, -2)), ('ll', 'left_leg', (4, 12, 4), (-2, -12, -2))]]
    return roots + body + out


def icons():
    """32 x 32 inventory icons, rendered from each piece's own 3D model."""
    import render_models as rm
    from PIL import Image
    views = {'helmet': (-28, 12), 'chestplate': (-20, 8), 'leggings': (-20, 8), 'boots': (-28, 18)}
    for realm in SETS:
        for piece in PIECES:
            parts = preview_parts(realm, [piece], mannequin=False)
            tex, _ = mobspecs.paint(parts, 7)
            glow = tex.info.pop('glow')
            im, _ = rm.render(parts, tex, glow, *views[piece], size=256, alpha=True)
            im = im.crop(im.getbbox())
            side = max(im.width, im.height)
            sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
            sq.paste(im, ((side - im.width) // 2, (side - im.height) // 2))
            ic = sq.resize((30, 30), Image.LANCZOS)
            out = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
            out.paste(ic, (1, 1))
            px = out.load()
            for x in range(32):
                for y in range(32):
                    r, g, b, a = px[x, y]
                    px[x, y] = (r, g, b, 255 if a > 110 else 0)
            res = out.copy()
            rp = res.load()
            for x in range(32):
                for y in range(32):
                    if px[x, y][3]:
                        continue
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < 32 and 0 <= ny < 32 and px[nx, ny][3]:
                            c = px[nx, ny]
                            rp[x, y] = (c[0] // 3, c[1] // 3, c[2] // 3, 255)
                            break
            res.save(f'{mobspecs.ASSETS}/textures/item/{ARMOR_ID[realm]}_{piece}.png')


if __name__ == '__main__':
    b = build_all()
    write_java(b)
    icons()
    print('armor models:', len(b), 'pieces,', sum(len(v[0]) for v in b.values()), 'parts')
