"""The nine armor sets of the Arsenals of the Tenfold Seal, as worn 3D models: solid fitted plate, heavy pauldrons, a helm with
a silhouette you can tell from across a field, each painted with clean bevelled pixel shading (light top-left, shade
bottom-right, an inset panel line on every plate big enough to hold one).

Authored in the box-model space used everywhere else (units of 1/16 block, y up, front +z), relative to the player's own parts:
head and body pivot at the neck, arms at (+-5, -2, 0), legs at (+-1.9, -12, 0). Each piece is its own model, so a helmet only
ever carries the helmet's decorations. Writes ArmorModels.java (layer definitions) and one texture per piece. Inventory icons
are drawn separately (arsenal_art.ICONS).
"""
import math

import numpy as np
from PIL import Image

import mobspecs
import paths
from kit_data import KIT, PIECES, REALMS
from pixelart import M, Mat, GEMS

ROOTS = {'head': (0, 0, 0), 'hat': (0, 0, 0), 'body': (0, 0, 0), 'right_arm': (-5, -2, 0), 'left_arm': (5, -2, 0),
         'right_leg': (-1.9, -12, 0), 'left_leg': (1.9, -12, 0)}
SETS = REALMS + ['genesis']
ARMOR_ID = dict({r: KIT[r]['armor'] for r in REALMS}, genesis='genesis')
STYLE = {   # plate, trim, dark, glow, cloth
    'grove': dict(plate='bark', trim='moss', dark='wood_d', glow='verdant', cloth='leaf'),
    'skyreach': dict(plate='white', trim='sky_m', dark='steel', glow='sky', cloth='cloth_b'),
    'hollow': dict(plate='black', trim='gold', dark='soulsteel', glow='ember', cloth='cloth_r'),
    'drowned': dict(plate='teal', trim='pearl', dark='tidesteel', glow='teal_g', cloth='tidesteel'),
    'pale': dict(plate='ice', trim='gold', dark='night', glow='void_p', cloth='frost'),
    'scarlet': dict(plate='scarlet', trim='gold', dark='black', glow='amber', cloth='black'),
    'clockwork': dict(plate='black', trim='brass', dark='chronite', glow='chrono_g', cloth='chronite'),
    'mycelial': dict(plate='stalk', trim='myc', dark='night', glow='myc_g', cloth='myc'),
    'genesis': dict(plate='genesis', trim='gold', dark='black', glow='star', cloth='black'),
}


class Piece:
    def __init__(self):
        self.parts = []

    def add(self, name, size, origin, pivot=(0, 0, 0), rot=(0, 0, 0), style='white', parent='head'):
        assert name not in {p['name'] for p in self.parts}, name
        isize = tuple(max(1, int(round(v))) for v in size)
        origin = tuple(o + (v - iv) / 2 for o, v, iv in zip(origin, size, isize))     # rounding keeps the box centred
        self.parts.append(dict(name=name, size=isize, origin=origin, pivot=tuple(pivot),
                               rot=tuple(rot), style=style, anim='none', eyes=None, parent=parent))
        return name


def side(sx):
    return 'R' if sx < 0 else 'L'


ARMS = (('right_arm', -1), ('left_arm', 1))
LEGS = (('right_leg', -1), ('left_leg', 1))


# ------------------------------------------------------------------------------------------------ the shared plate
def face(p, m, z=4.7, eye_y=3.8, teeth=True, recess=True):
    """A menacing face: a dark recess, slanted eyes burning in it, a fanged jaw guard below."""
    if recess:
        p.add('faceShadow', (8, 4, 1), (-4, 1.6, z), style='abyss')
    for sx in (-1, 1):                                               # eyes slant down toward the nose: a scowl
        p.add('eye' + side(sx), (3, 1, 1), (-1.5, -0.5, -0.5), (sx * 2.1, eye_y, z + 1.0), rot=(0, 0, sx * 0.38), style=m['glow'])
    if teeth:
        p.add('jaw', (8, 2, 1), (-4, -0.6, z + 0.2), style='abyss')
        for k, x in enumerate((-2.6, 1.6)):                          # two canines, overlapping the jaw line
            p.add(f'fang{k}', (1, 3, 1), (x, -1.6, z + 0.7), style='bone')


def helm(p, m, visor='slit'):
    p.add('helm', (10, 10, 10), (-5, -1, -5), style=m['plate'])
    p.add('brow', (11, 2, 2), (-5.5, 5.4, 4.4), rot=(0.12, 0, 0), style=m['trim'])
    p.add('rim', (11, 1, 11), (-5.5, -1.2, -5.5), style=m['trim'])
    face(p, m, z=4.6)
    if visor == 'tee':
        p.add('visorV', (1, 3, 1), (-0.5, 1.2, 5.6), style=m['glow'])
    for sx in (-1, 1):
        p.add('cheek' + side(sx), (1, 6, 4), (sx * 5.3 - 0.5, -2, 1), style=m['dark'])
        p.add('cheekSpike' + side(sx), (1, 3, 1), (-0.5, -3, -0.5), (sx * 5.3, -1.5, 4), rot=(0.4, 0, sx * 0.3), style=m['trim'])
        p.add('browHorn' + side(sx), (1.2, 4, 1.2), (-0.6, 0, -0.6), (sx * 4.2, 7, 4.5), rot=(0.5, 0, -sx * 0.5), style=m['dark'])


def torso(p, m, emblem=True):
    p.add('plate', (10, 13, 6), (-5, -12.6, -3), style=m['plate'], parent='body')
    p.add('chest', (8, 5, 1), (-4, -6.5, 3), style=m['plate'], parent='body')
    p.add('collar', (11, 1, 7), (-5.5, -1.2, -3.5), style=m['trim'], parent='body')
    p.add('back', (8, 9, 1), (-4, -11, -3.8), style=m['dark'], parent='body')
    if emblem:
        p.add('emblem', (3, 3, 1), (-1.5, -5.5, 3.6), style=m['glow'], parent='body')
        p.add('emblemRim', (5, 5, 1), (-2.5, -6.5, 3.3), style=m['trim'], parent='body')
    for arm, sx in ARMS:
        L = side(sx)
        x0 = -3.2 if sx < 0 else -1.8
        p.add('arm' + L, (5, 6, 5), (x0, -5.5, -2.5), style=m['plate'], parent=arm)
        p.add('vamb' + L, (6, 4, 6), (x0 - 0.5, -10.2, -3), style=m['dark'], parent=arm)
        p.add('vambBand' + L, (7, 1, 7), (x0 - 1, -7, -3.5), style=m['trim'], parent=arm)


def pauldron(p, m, arm, sx, w=8, h=4, d=7, tiers=2, style=None):
    """A layered shoulder: a broad plate, a trimmed rim, a smaller plate over it."""
    L = side(sx)
    cx = -1 if sx < 0 else 1
    st = style or m['plate']
    p.add('paul' + L, (w, h, d), (-w / 2, -1, -d / 2), (cx, 1.5, 0), rot=(0, 0, -sx * 0.22), style=st, parent=arm)
    p.add('paulRim' + L, (w + 1, 1, d + 1), (-(w + 1) / 2, -1.6, -(d + 1) / 2), (cx, 1.5, 0), rot=(0, 0, -sx * 0.22), style=m['trim'], parent=arm)
    if tiers > 1:
        p.add('paulTop' + L, (w - 2, 2, d - 2), (-(w - 2) / 2, h - 1, -(d - 2) / 2), (cx, 1.5, 0), rot=(0, 0, -sx * 0.22), style=st, parent=arm)
    return 'paul' + L


def legs(p, m, tabard=True):
    p.add('belt', (11, 3, 7), (-5.5, -13.5, -3.5), style=m['trim'], parent='body')
    p.add('buckle', (3, 2, 1), (-1.5, -12.8, 3.1), style=m['glow'], parent='body')
    if tabard:
        p.add('tabard', (5, 9, 1), (-2.5, -21.5, 3.0), style=m['cloth'], parent='body')
        p.add('tabardBack', (6, 8, 1), (-3, -20.5, -3.6), style=m['cloth'], parent='body')
    for leg, sx in LEGS:
        L = side(sx)
        p.add('thigh' + L, (5, 6, 5), (-2.5, -6.5, -2.5), style=m['plate'], parent=leg)
        p.add('knee' + L, (4, 3, 1.5), (-2, -9, 2.4), style=m['trim'], parent=leg)
        p.add('greave' + L, (5, 2, 5), (-2.5, -9, -2.5), style=m['dark'], parent=leg)
        p.add('hip' + L, (1, 5, 4), (sx * 2.6 - 0.5, -5, -2), style=m['trim'], parent=leg)


def boots(p, m):
    for leg, sx in LEGS:
        L = side(sx)
        p.add('boot' + L, (5, 5, 5), (-2.5, -12.4, -2.5), style=m['plate'], parent=leg)
        p.add('toe' + L, (4, 2, 2), (-2, -12.4, 2.4), style=m['dark'], parent=leg)
        p.add('cuff' + L, (6, 1, 6), (-3, -8, -3), style=m['trim'], parent=leg)
        p.add('ankleGem' + L, (1, 1, 1), (sx * 2.6 - 0.5, -10.5, 0), style=m['glow'], parent=leg)


def spikes(p, base, n, length, style, parent, spread=0.5, w=1.6):
    """A fan of n spikes rising from a part."""
    for k in range(n):
        a = (k - (n - 1) / 2) * spread
        p.add(f'{base}{k}', (w, length - abs(k - (n - 1) / 2) * 1.2, w), (-w / 2, 0, -w / 2), (math.sin(a) * 2.5, 2.5, 0),
              rot=(0, 0, -a), style=style, parent=parent)


# ------------------------------------------------------------------------------------------------ the nine sets
def mossbound(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'eyes')
        p.add('mossCap', (11, 2, 11), (-5.5, 8.6, -5.5), style='moss')
        p.add('mossDrape', (11, 4, 1), (-5.5, 5.5, -6), style='moss')
        for k, (x, z, st) in enumerate([(-3, 2, 'gem_m'), (2.5, -2, 'gem_y'), (3.5, 3, 'gem_m')]):
            p.add(f'flower{k}', (1, 1, 1), (x, 10.6, z), style=st)
        for sx in (-1, 1):
            L = side(sx)
            b = p.add('branch' + L, (1.6, 6, 1.6), (-0.8, 0, -0.8), (sx * 4, 9, -1), rot=(-0.2, 0, -sx * 0.6), style='bark')
            p.add('twig' + L, (1.2, 4, 1.2), (-0.6, 0, -0.6), (0, 5, 0), rot=(0, 0, sx * 0.7), parent=b, style='bark')
            p.add('leafA' + L, (3, 1, 2), (-1.5, 0, -1), (0, 4.5, 0), parent=b, style='leaf')
    elif piece == 'chestplate':
        torso(p, m)
        p.add('vineX', (1, 11, 1), (-0.5, -12, 3.2), rot=(0, 0, 0.5), style='vine', parent='body')
        for arm, sx in ARMS:
            pa = pauldron(p, m, arm, sx, 8, 4, 7)
            L = side(sx)
            p.add('paulMoss' + L, (7, 2, 6), (-3.5, 4.5, -3), (sx, 1.5, 0), style='moss', parent=arm)
            p.add('shroomS' + L, (1, 2, 1), (-0.5, 6, -0.5), (sx * 2, 1.5, 1), style='stalk', parent=arm)
            p.add('shroomC' + L, (3, 1, 3), (-1.5, 8, -1.5), (sx * 2, 1.5, 1), style='scarlet', parent=arm)
            p.add('bloom' + L, (1, 1, 1), (-0.5, 6.5, -0.5), (-sx * 1.5, 1.5, -2), style='gem_y', parent=arm)
    elif piece == 'leggings':
        legs(p, m)
        for leg, sx in LEGS:
            p.add('legVine' + side(sx), (1, 6, 1), (sx * 2.6 - 0.5, -8, 2.2), style='vine', parent=leg)
    else:
        boots(p, m)
        for leg, sx in LEGS:
            p.add('rootToe' + side(sx), (1, 1, 3), (-0.5, -12.4, 4), rot=(0.3, 0, 0), style='bark', parent=leg)
    return p


def tempest(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'slit')
        p.add('crest', (2, 4, 9), (-1, 9, -4.5), style=m['trim'])
        for sx in (-1, 1):
            L = side(sx)
            for k in range(3):
                p.add(f'wing{L}{k}', (1, 7 - k * 1.5, 2), (-0.5, 0, -1), (sx * 5, 5 - k, -1 - k * 1.5), rot=(-0.3 - k * 0.2, 0, -sx * (0.5 + k * 0.15)),
                      style='sky' if k == 0 else 'white')
    elif piece == 'chestplate':
        torso(p, m)
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 8, 4, 7)
            spikes(p, 'iceSpike' + side(sx), 3, 7, 'sky', 'paul' + side(sx), 0.45)
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
        for leg, sx in LEGS:
            p.add('heelFin' + side(sx), (1, 4, 2), (-0.5, 0, -1), (sx * 2.6, -11, -1.5), rot=(-0.6, 0, -sx * 0.4), style='sky', parent=leg)
    return p


def sovereign(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'tee')
        p.add('crownBand', (11, 2, 11), (-5.5, 9, -5.5), style='gold')
        for k in range(5):
            a = (k - 2) * 0.55
            p.add(f'crownSpike{k}', (1.6, 4 - abs(k - 2) * 0.6, 1.6), (-0.8, 0, -0.8), (math.sin(a) * 5, 10.5, math.cos(a) * 5 - 0.5),
                  rot=(0.2 * math.cos(a), 0, -0.2 * math.sin(a)), style='gold')
        p.add('crownGem', (2, 2, 1), (-1, 9, 5.2), style='gem_o')
        for sx in (-1, 1):
            L = side(sx)
            h = p.add('horn' + L, (2.4, 6, 2.4), (-1.2, 0, -1.2), (sx * 5, 6, 0), rot=(-0.1, 0, -sx * 1.1), style='black')
            p.add('hornTip' + L, (1.6, 4, 1.6), (-0.8, 0, -0.8), (0, 5.5, 0), rot=(0, 0, sx * 0.8), parent=h, style='gold')
    elif piece == 'chestplate':
        torso(p, m)
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 9, 4, 8)
            spikes(p, 'goldSpike' + side(sx), 3, 6, 'gold', 'paul' + side(sx), 0.5)
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
    return p


def abyssal(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'slit')
        p.add('finCrest', (1, 5, 9), (-0.5, 9, -5), style='pearl')
        for sx in (-1, 1):                                           # antlers of bone and coral
            L = side(sx)
            b = p.add('antler' + L, (1.6, 7, 1.6), (-0.8, 0, -0.8), (sx * 4, 8, -1), rot=(-0.15, 0, -sx * 0.55), style='bone')
            b2 = p.add('antler2' + L, (1.4, 6, 1.4), (-0.7, 0, -0.7), (0, 6.5, 0), rot=(-0.2, 0, sx * 0.4), parent=b, style='bone')
            p.add('tine' + L, (1.2, 4, 1.2), (-0.6, 0, -0.6), (0, 3, 0), rot=(0.5, 0, -sx * 0.8), parent=b, style='coral')
            p.add('tine2' + L, (1.2, 3, 1.2), (-0.6, 0, -0.6), (0, 4, 0), rot=(0.4, 0, -sx * 0.9), parent=b2, style='coral')
    elif piece == 'chestplate':
        torso(p, m)
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 8, 4, 7, style='pearl')
            spikes(p, 'boneSpike' + side(sx), 3, 5, 'bone', 'paul' + side(sx), 0.6, w=1.2)
            p.add('coral' + side(sx), (1, 4, 1), (-0.5, 0, -0.5), (sx * 2, 3, 3), rot=(0.4, 0, -sx * 0.3), style='coral', parent=arm)
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
        for leg, sx in LEGS:
            p.add('ankleFin' + side(sx), (1, 3, 3), (-0.5, 0, -1.5), (sx * 2.7, -10, 0), rot=(0, 0, -sx * 0.5), style='pearl', parent=leg)
    return p


def rimebound(piece, m):
    p = Piece()
    if piece == 'helmet':
        p.add('hood', (11, 11, 11), (-5.5, -1.5, -5.5), style='frost')
        p.add('hoodPeak', (8, 3, 8), (-4, 9, -5.5), rot=(-0.25, 0, 0), style='frost')
        p.add('hoodTrim', (12, 1, 2), (-6, 8.5, 4.5), style='gold')
        p.add('face', (8, 7, 1), (-4, 0, 4.7), style='abyss')
        face(p, m, z=5.0, eye_y=3.8, recess=False)
        p.add('circlet', (2, 2, 1), (-1, 6.5, 5.6), style='gem_w')
    elif piece == 'chestplate':
        torso(p, m)
        p.add('cape', (10, 14, 1), (-5, -14, -4.2), rot=(0.12, 0, 0), style='frost', parent='body')
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 9, 4, 8, style='frost')
            p.add('fur' + side(sx), (8, 2, 7), (-4, 4.5, -3.5), (sx, 1.5, 0), style='white', parent=arm)
    elif piece == 'leggings':
        legs(p, m)
        for k, x in enumerate((-4, 4)):
            p.add(f'bellStr{k}', (1, 2, 1), (x - 0.5, -15, 3), style='gold', parent='body')
            p.add(f'bell{k}', (2, 2, 2), (x - 1, -17, 2.5), style='gold', parent='body')
    else:
        boots(p, m)
    return p


def glasscarapace(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'eyes')
        h = p.add('scarabHorn', (2, 7, 2), (-1, 0, -1), (0, 8, 3), rot=(0.6, 0, 0), style='scarlet')
        p.add('scarabHorn2', (1.5, 4, 1.5), (-0.75, 0, -0.75), (0, 6.5, 0), rot=(-0.9, 0, 0), parent=h, style='gold')
        for sx in (-1, 1):
            L = side(sx)
            hs = p.add('sideHorn' + L, (1.6, 5, 1.6), (-0.8, 0, -0.8), (sx * 4.5, 7, 0), rot=(0, 0, -sx * 0.8), style='black')
            p.add('sideHornTip' + L, (1.2, 3, 1.2), (-0.6, 0, -0.6), (0, 4.5, 0), rot=(0, 0, sx * 0.6), parent=hs, style='gold')
    elif piece == 'chestplate':
        torso(p, m)
        for sx in (-1, 1):                                          # glass elytra-wings on the back
            L = side(sx)
            w = p.add('wing' + L, (1, 14, 6), (-0.5, -12, -3), (sx * 2.5, 0, -3.6), rot=(0.25, sx * 0.5, sx * 0.25), style='glass_r', parent='body')
            p.add('wingVein' + L, (1, 12, 1), (-0.4, -11, -0.5), (0, 0, 0), parent=w, style='gold')
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 8, 4, 7)
            spikes(p, 'redSpike' + side(sx), 2, 5, 'black', 'paul' + side(sx), 0.6)
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
    return p


def paradox(piece, m):
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'slit')
        p.add('gearCrest', (7, 7, 1), (-3.5, -3.5, -0.5), (0, 11, -1), style='brass')
        p.add('gearCrest2', (7, 7, 1), (-3.5, -3.5, -0.5), (0, 11, -1), rot=(0, 0, 0.785), style='brass')
        p.add('gearHub', (3, 3, 1.4), (-1.5, -1.5, -0.7), (0, 11, -1), style='chrono_g')
        for sx in (-1, 1):
            p.add('earGear' + side(sx), (1.4, 4, 4), (-0.7, -2, -2), (sx * 5.4, 4, 0), rot=(0.785, 0, 0), style='brass')
    elif piece == 'chestplate':
        torso(p, m, emblem=False)
        p.add('clock', (6, 6, 1), (-3, -8.5, 3.3), style='clock', parent='body')
        p.add('clockRim', (7, 7, 1), (-3.5, -3.5, -0.5), (0, -5.5, 3.6), rot=(0, 0, 0.785), style='brass', parent='body')
        p.add('clockCore', (2, 2, 1), (-1, -6.5, 4.1), style='chrono_g', parent='body')
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 8, 4, 7)
            p.add('cog' + side(sx), (1.4, 5, 5), (-0.7, -2.5, -2.5), (sx * 4.2, 4.5, 0), rot=(0.785, 0, 0), style='brass', parent=arm)
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
    return p


def bloomguard(piece, m):
    p = Piece()
    if piece == 'helmet':
        p.add('hood', (11, 10, 11), (-5.5, -1.5, -5.5), style='stalk')
        p.add('face', (8, 7, 1), (-4, -0.5, 4.7), style='abyss')
        face(p, m, z=5.0, eye_y=3.4, recess=False)
        p.add('cap', (15, 2, 15), (-7.5, 8, -7.5), style='myc')
        p.add('capTop', (10, 2, 10), (-5, 10, -5), style='myc')
        for k, (x, z) in enumerate([(-5, 3), (4, -4), (5, 4), (-3, -5)]):
            p.add(f'spot{k}', (2, 1, 2), (x - 1, 10, z - 1), style='myc_g')
    elif piece == 'chestplate':
        torso(p, m)
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 8, 3, 7, style='myc')
            p.add('orb' + side(sx), (3, 3, 3), (-1.5, 4.5, -1.5), (sx, 1.5, 0), style='myc_g', parent=arm)
        p.add('robeBack', (9, 6, 1), (-4.5, -12, -4), style='myc', parent='body')
    elif piece == 'leggings':
        legs(p, m)
    else:
        boots(p, m)
    return p


def genesis(piece, m):
    """The Unmaker's regalia: bone-white and gold plate over black, the eight realm stones round a star on the breast,
    a horned crown with a red stone, layered gold-edged pauldrons, shards of the unmade worlds hanging at the back."""
    p = Piece()
    if piece == 'helmet':
        helm(p, m, 'slit')
        p.add('crownBand', (11, 2, 11), (-5.5, 9, -5.5), style='gold')
        for k in range(5):
            a = (k - 2) * 0.5
            p.add(f'spike{k}', (1.6, 5 - abs(k - 2) * 0.9, 1.6), (-0.8, 0, -0.8), (math.sin(a) * 5, 10.5, math.cos(a) * 5 - 0.6),
                  rot=(0.2 * math.cos(a), 0, -0.2 * math.sin(a)), style='gold' if k % 2 == 0 else 'genesis')
        p.add('crownGem', (2, 2, 1), (-1, 9, 5.3), style='gem_r')
        for sx in (-1, 1):
            L = side(sx)
            h = p.add('horn' + L, (2.4, 6, 2.4), (-1.2, 0, -1.2), (sx * 5, 6.5, -1), rot=(-0.3, 0, -sx * 1.0), style='black')
            h2 = p.add('horn2' + L, (2, 5, 2), (-1, 0, -1), (0, 5.5, 0), rot=(-0.2, 0, sx * 0.7), parent=h, style='genesis')
            p.add('hornTip' + L, (1.2, 3, 1.2), (-0.6, 0, -0.6), (0, 4.5, 0), rot=(0, 0, sx * 0.4), parent=h2, style='gold')
    elif piece == 'chestplate':
        torso(p, m, emblem=False)
        p.add('heartRim', (9, 9, 1), (-4.5, -10, 3.2), style='gold', parent='body')
        p.add('heart', (7, 7, 1), (-3.5, -9, 3.5), style='black', parent='body')
        p.add('star', (2, 2, 1), (-1, -6.5, 4.0), style='star', parent='body')
        for k, gm in enumerate(GEMS):
            a = k * math.pi / 4
            p.add(f'stone{k}', (2, 2, 1), (-1, -1, -0.5), (math.cos(a) * 2.6, -5.5 + math.sin(a) * 2.6, 4.3), style=gm, parent='body')
        p.add('band', (11, 1, 7), (-5.5, -10.5, -3.5), style='gold', parent='body')
        for arm, sx in ARMS:
            pauldron(p, m, arm, sx, 9, 4, 8, tiers=2)
            L = side(sx)
            p.add('paulGold' + L, (8, 1, 7), (-4, 5, -3.5), (sx, 1.5, 0), rot=(0, 0, -sx * 0.22), style='gold', parent=arm)
            spikes(p, 'spike' + L, 3, 6, 'genesis', 'paul' + L, 0.5)
        for k, (x, y, st) in enumerate([(-6, -2, 'genesis'), (6, -3, 'black'), (-4, 3, 'black'), (5, 2, 'genesis'), (0, 5, 'star')]):
            p.add(f'shard{k}', (2, 3, 1), (-1, -1.5, -0.5), (x, y, -6), rot=(0, 0, 0.785), style=st, parent='body')
    elif piece == 'leggings':
        legs(p, m)
        p.add('tabardGold', (1, 8, 1), (-0.5, -21, 3.6), style='gold', parent='body')
    else:
        boots(p, m)
        for leg, sx in LEGS:
            p.add('goldToe' + side(sx), (6, 1, 2), (-3, -10.6, 2.2), style='gold', parent=leg)
    return p


BUILD = {'grove': mossbound, 'skyreach': tempest, 'hollow': sovereign, 'drowned': abyssal, 'pale': rimebound, 'scarlet': glasscarapace,
         'clockwork': paradox, 'mycelial': bloomguard, 'genesis': genesis}


def menace(p, m, piece):
    """What every set shares: horned pauldrons, a spined back, a V-ridged chest, clawed gauntlets, spiked knees, tattered
    cloth, clawed and spurred boots. Added after each set's own build, so it only ever adds."""
    names = {q['name'] for q in p.parts}
    if piece == 'chestplate':
        for arm, sx in ARMS:
            L = side(sx)
            cx = -1 if sx < 0 else 1
            if 'paul' + L in names:
                h = p.add('mnHorn' + L, (2.4, 5, 2.4), (-1.2, 0, -1.2), (sx * 3, 3, -1), rot=(-0.25, 0, -sx * 0.6), style=m['dark'], parent='paul' + L)
                h2 = p.add('mnHorn2' + L, (1.8, 4, 1.8), (-0.9, 0, -0.9), (0, 4.5, 0), rot=(-0.2, 0, sx * 0.45), style=m['dark'], parent=h)
                p.add('mnHornTip' + L, (1.2, 3, 1.2), (-0.6, 0, -0.6), (0, 3.5, 0), rot=(-0.2, 0, sx * 0.35), style=m['trim'], parent=h2)
            for k, z in enumerate((-1.4, 0, 1.4)):
                p.add(f'mnClaw{L}{k}', (1, 3, 1), (-0.5, -3, -0.5), (cx, -10.2, z + 0.6), rot=(0.35, 0, -sx * 0.15), style=m['trim'], parent=arm)
            p.add('mnFin' + L, (1, 4, 3), (-0.5, -2, -1.5), (cx + sx * 3.1, -8, 0), rot=(0, 0, -sx * 0.45), style=m['trim'], parent=arm)
        for k, y in enumerate((-2, -5, -8)):
            p.add(f'mnSpine{k}', (1.6, 5 - k, 1.6), (-0.8, 0, -0.8), (0, y, -3.6), rot=(-0.9, 0, 0), style=m['dark'], parent='body')
        for sx in (-1, 1):
            p.add('mnRidge' + side(sx), (6, 1, 1), (-3, -0.5, -0.5), (sx * 2.2, -9.5, 3.4), rot=(0, 0, sx * 0.55), style=m['trim'], parent='body')
    elif piece == 'leggings':
        for leg, sx in LEGS:
            L = side(sx)
            p.add('mnKnee' + L, (1.4, 1.4, 4), (-0.7, -0.7, 0), (0, -7.6, 3), rot=(-0.35, 0, 0), style=m['trim'], parent=leg)
            p.add('mnThighSpike' + L, (1, 3, 1), (-0.5, 0, -0.5), (sx * 2.6, -4, 0), rot=(0, 0, -sx * 0.9), style=m['dark'], parent=leg)
        if 'tabard' in names:
            for k, (x, h) in enumerate([(-2, 4), (-0.5, 2), (1, 5), (2, 3)]):
                p.add(f'mnTatter{k}', (1, h, 1), (x, -21.5 - h, 3.0), style=m['cloth'], parent='body')
    elif piece == 'boots':
        for leg, sx in LEGS:
            L = side(sx)
            for k, x in enumerate((-1.6, 0, 1.6)):
                p.add(f'mnToe{L}{k}', (1, 1, 3), (-0.5, -0.5, 0), (x, -11.9, 4), rot=(0.25, 0, 0), style=m['trim'], parent=leg)
            p.add('mnSpur' + L, (1, 1, 4), (-0.5, -0.5, -4), (0, -10, -2.4), rot=(-0.5, 0, 0), style=m['dark'], parent=leg)
            p.add('mnShin' + L, (1, 4, 2), (-0.5, 0, 0), (0, -11, 2.4), rot=(0.25, 0, 0), style=m['trim'], parent=leg)
    return p


def piece_parts(realm, piece):
    return menace(BUILD[realm](piece, STYLE[realm]), STYLE[realm], piece).parts


# ------------------------------------------------------------------------------------------------ the clean painter
def _mat(style):
    if style in M:
        return M[style]
    st = mobspecs.STYLES.get(style, {'base': (90, 90, 100)})
    return Mat(st['base'])


def paint(parts):
    """Each face: a solid base tone, light catching its top rows, a dark rim round its sides and bottom, a dither into shadow
    near the bottom of tall faces. Tops are a step lighter, undersides a step darker. Glowing materials burn white at the core
    and go to the glow layer too."""
    sheet, pos = mobspecs.pack(parts)
    img = np.zeros((sheet, sheet, 4), np.uint8)
    glow = np.zeros((sheet, sheet, 4), np.uint8)
    for i, p in enumerate(parts):
        u, v = pos[i]
        p['uv'] = (u, v)
        w, h, d = p['size']
        mat = _mat(p['style'])
        t = mat.tones
        faces = [((d, 0, w, d), 1), ((d + w, 0, w, d), -1), ((0, d, d, h), 0), ((d, d, w, h), 0), ((d + w, d, d, h), 0), ((2 * d + w, d, w, h), 0)]
        for (fx, fy, fw, fh), lift in faces:
            for ex in range(fw):
                for ey in range(fh):
                    k = 2 + (1 if lift > 0 else 0) - (1 if lift < 0 else 0)
                    if mat.glow:
                        k = 4 if (0 < ex < fw - 1 and 0 < ey < fh - 1) else 2
                    elif fw > 2 and fh > 2:
                        if ex in (0, fw - 1) or ey == fh - 1:
                            k = 1                                       # a dark rim marks the plate's edge
                        elif ey == 0 or (ey == 1 and fh > 5):
                            k = 3                                       # light catching the top
                        elif fh > 6 and ey >= fh - 3 and (ex + ey) % 2 == 0:
                            k = 1 if ey == fh - 2 else 2                # a soft dither into shadow at the bottom
                    c = t[max(0, min(4, k))]
                    img[v + fy + ey, u + fx + ex] = (*c, 255)
                    if mat.glow:
                        glow[v + fy + ey, u + fx + ex] = (*c, 255)
    out = Image.fromarray(img, 'RGBA')
    out.info['glow'] = Image.fromarray(glow, 'RGBA')
    return out, sheet


# ------------------------------------------------------------------------------------------------ outputs
def f(v):
    return f'{v:.3f}F'


def build_all():
    out = {}
    for realm in SETS:
        for piece in PIECES:
            parts = piece_parts(realm, piece)
            img, sheet = paint(parts)
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
         '/** GENERATED by gen_armor.py. The nine armor sets as worn 3D models, one per piece. Do not edit by hand. */',
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
    open(paths.JAVA + '/client/ArmorModels.java', 'w').write('\n'.join(L) + '\n')


def preview_parts(realm, pieces=PIECES, mannequin=True):
    """The pieces as render_models parts, hung on the player's skeleton (the vanilla parts become invisible pivots)."""
    out = []
    for piece in pieces:
        for p in piece_parts(realm, piece):
            q = dict(p)
            q['name'] = piece + '_' + p['name']
            q['parent'] = (piece + '_' + p['parent']) if p['parent'] not in ROOTS else 'root_' + p['parent']
            out.append(q)
    roots = [dict(name='root_' + r, size=(1, 1, 1), origin=(0, 0, 0), pivot=(px, py + 24, pz), rot=(0, 0, 0), style='black', anim='none',
                  eyes=None, parent=None, hidden=True) for r, (px, py, pz) in ROOTS.items()]
    body = []
    if mannequin:                                                    # the wearer underneath, so gaps read as body, not holes
        body = [dict(name='m_' + n, size=s, origin=o, pivot=(0, 0, 0), rot=(0, 0, 0), style='steel', anim='none', eyes=None, parent='root_' + r)
                for n, r, s, o in [('head', 'head', (8, 8, 8), (-4, 0, -4)), ('body', 'body', (8, 12, 4), (-4, -12, -2)),
                                   ('ra', 'right_arm', (4, 12, 4), (-3, -10, -2)), ('la', 'left_arm', (4, 12, 4), (-1, -10, -2)),
                                   ('rl', 'right_leg', (4, 12, 4), (-2, -12, -2)), ('ll', 'left_leg', (4, 12, 4), (-2, -12, -2))]]
    return roots + body + out


def render_preview(realm, size=620, bg=((24, 20, 34), (8, 6, 12)), views=((-28, 8), (150, 10))):
    import render_models as rm
    parts = preview_parts(realm)
    tex, _ = paint(parts)
    glow = tex.info.pop('glow')
    ims, sc = [], None
    for yaw, pitch in views:
        im, sc = rm.render(parts, tex, glow, yaw, pitch, size=size, bg=bg, scale=sc)
        ims.append(im)
    return ims


if __name__ == '__main__':
    b = build_all()
    write_java(b)
    print('armor models:', len(b), 'pieces,', sum(len(v[0]) for v in b.values()), 'parts')
