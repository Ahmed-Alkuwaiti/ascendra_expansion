"""The eight Warden relics, the Hand of Genesis and the Relic Pedestal, designed once as cuboid elements and written out as:
  - 3D item models (vanilla JSON elements: one rotation axis per element, angles of 0, +-22.5 or +-45 degrees),
  - one small texture per model (an 8 x 8 grid of painted swatches, one per material),
  - the pedestal's block models (an empty and a filled model per relic, the relic shrunk onto the top),
  - and box-model parts for the preview renderer (render_models), so the previews show exactly these shapes.
Units are 1/16 block, y up.
"""
import json
import math
import os
import random

from PIL import Image, ImageDraw

import mobspecs

ASSETS = __import__('paths').RES + '/assets/aurelia'


class Model:
    def __init__(self, key):
        self.key = key
        self.els = []

    def box(self, frm, to, style, axis=None, angle=0.0, origin=None):
        assert angle in (0, 22.5, -22.5, 45, -45, 0.0), angle
        if origin is None:
            origin = tuple((a + b) / 2 for a, b in zip(frm, to))
        self.els.append(dict(frm=tuple(frm), to=tuple(to), style=style, axis=axis, angle=angle, origin=tuple(origin)))

    def seg_chain(self, start, segs, axis, style_fn, depth):
        """Segments laid end to end, each turned about `axis` ('z' bends in x-y, 'x' bends in z-y). segs: (length, width, angle)."""
        x, y, z = start
        for i, (ln, w, ang) in enumerate(segs):
            th = math.radians(ang)
            if axis == 'z':
                self.box((x - w / 2, y, z - depth / 2), (x + w / 2, y + ln + min(1.0, w * 0.3), z + depth / 2), style_fn(i), 'z', ang, (x, y, z))
                x, y = x - ln * math.sin(th), y + ln * math.cos(th)
            else:
                self.box((x - depth / 2, y, z - w / 2), (x + depth / 2, y + ln + min(1.0, w * 0.3), z + w / 2), style_fn(i), 'x', ang, (x, y, z))
                y, z = y + ln * math.cos(th), z + ln * math.sin(th)
        return x, y, z

    def ring(self, c, r, n, size, style, plane='xz', y_off=0.0):
        """n small blocks round a circle (each turned to the nearest allowed angle)."""
        for i in range(n):
            a = 2 * math.pi * i / n
            if plane == 'xz':
                p = (c[0] + r * math.cos(a), c[1] + y_off, c[2] + r * math.sin(a))
            else:
                p = (c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2])
            s = size
            ang = [0, 45, 22.5, -22.5, -45][i % 5] if plane == 'xy' else 0
            self.box((p[0] - s[0] / 2, p[1] - s[1] / 2, p[2] - s[2] / 2), (p[0] + s[0] / 2, p[1] + s[1] / 2, p[2] + s[2] / 2), style,
                     'z' if plane == 'xy' else None, ang if plane == 'xy' else 0)


# =================================================================================================== the eight relics
def rootbound_heart():
    """Mossback's relic: a heart of knotted bark, split by green-burning veins, roots trailing, moss on top."""
    m = Model('rootbound_heart')
    m.box((4, 3, 5), (12, 12, 11), 'bark')
    m.box((3, 7, 4), (8, 13, 10), 'bark_d', 'z', 22.5)
    m.box((8, 7, 6), (13, 13, 12), 'bark', 'z', -22.5)
    m.box((6, 1, 6), (10, 5, 10), 'bark_d', 'y', 45)
    for (frm, to) in [((5.5, 4, 10.6), (6.5, 11, 11.4)), ((9, 5, 10.6), (10, 11, 11.4)), ((5.5, 7, 10.6), (10, 8, 11.4)),
                      ((3.6, 5, 6), (4.4, 10, 7)), ((11.6, 4, 7), (12.4, 9, 8)), ((7, 2, 9.6), (8, 6, 10.4))]:
        m.box(frm, to, 'glowg')
    m.box((2.5, 6, 4), (13.5, 7, 5), 'bark_rot', 'z', 22.5)
    m.box((3, 9.5, 10.5), (13, 10.5, 11.5), 'bark_rot', 'z', -22.5)
    m.box((4, 4, 3.5), (5, 12, 12.5), 'bark_rot', 'x', 45)
    for (frm, to, ang) in [((5, -1, 7), (6, 4, 8), 22.5), ((10, -1, 5), (11, 4, 6), -22.5), ((8, -1, 9), (9, 3, 10), 45)]:
        m.box(frm, to, 'bark_d', 'x', ang)
    m.box((5, 12.5, 5), (10, 14, 9), 'moss')
    m.box((9, 13, 7), (12, 14.5, 10), 'moss_l')
    m.box((6, 12, 7), (7, 16, 8), 'bark_d', 'x', -22.5)
    m.box((9, 12, 8), (10, 15.5, 9), 'bark_d', 'z', 22.5)
    m.box((6.5, 15, 6.5), (7.5, 16, 7.5), 'glowg')
    return m


def storm_talon():
    """The Tempest Roc's relic: a great hooked talon of bone, crackling with cyan lightning, storm-black feathers at its root."""
    m = Model('storm_talon')
    for i, (frm, to, ang) in enumerate([((2, 1, 5), (9, 3, 11), -22.5), ((3, 2, 4), (10, 4, 10), 22.5), ((1, 3, 6), (8, 5, 12), 45),
                                        ((4, 1, 6), (12, 3, 11), -45), ((5, 3, 4), (12, 5, 9), 0)]):
        m.box(frm, to, 'navy' if i % 2 else 'navy_d', 'y', ang)
    m.box((4, 3.5, 6), (10, 6.5, 10), 'steel')
    m.box((3.6, 4.2, 5.6), (10.4, 5.2, 10.4), 'rune_cyan')
    end = m.seg_chain((7, 6, 8), [(4, 5, 0), (4, 4.5, -22.5), (3.5, 4, -45), (3, 3, -45), (3, 2, -45)], 'z',
                      lambda i: 'bone' if i % 2 == 0 else 'horn', 4)
    m.seg_chain((7, 6.5, 10.1), [(3.5, 1, 0), (3.5, 1, -22.5), (3, 1, -45), (2.5, 1, -45)], 'z', lambda i: 'glow_w', 0.6)
    m.seg_chain((7, 6.5, 5.9), [(3.5, 1, 0), (3.5, 1, -22.5), (3, 1, -45), (2.5, 1, -45)], 'z', lambda i: 'rune_cyan', 0.6)
    for (frm, to, ang) in [((11, 9, 7.5), (12, 13, 8.5), 22.5), ((3, 7, 7.5), (4, 11, 8.5), -22.5), ((12.5, 4, 7.5), (13.5, 7, 8.5), 45)]:
        m.box(frm, to, 'glow_w', 'z', ang)
    return m


def sovereign_hand():
    """The Hollow King's relic: his severed gauntlet, black iron split with lava, soul fire burning in the palm."""
    m = Model('sovereign_hand')
    m.box((4, 0, 5), (12, 5, 11), 'king_armor')
    m.box((3.5, 4, 4.5), (12.5, 6, 11.5), 'plate_dk')
    m.box((4.5, 5.5, 5), (11.5, 10, 10.5), 'king_armor')
    m.box((5.5, 6.5, 10.3), (10.5, 9.5, 10.8), 'soul_light')
    m.box((6.5, 7, 10.7), (9.5, 9, 11.4), 'flame')
    for i, x in enumerate((4.6, 6.6, 8.6, 10.6)):
        h = [4.5, 5.5, 5, 4][i]
        m.seg_chain((x, 10, 8), [(h * 0.55, 1.8, 22.5), (h * 0.45, 1.6, 45)], 'x', lambda k: 'plate_dk' if k == 0 else 'king_armor', 1.8)
        m.box((x - 0.5, 10.5, 9.4), (x + 0.5, 12, 9.9), 'rune_orange')
    m.seg_chain((12, 6, 9), [(3, 2, -45), (2.5, 1.8, -45)], 'z', lambda k: 'plate_dk', 2)
    for (frm, to) in [((3.8, 1, 7), (4.2, 4.5, 8)), ((11.8, 2, 6), (12.2, 5, 7)), ((6, 0.2, 10.8), (10, 1, 11.2)), ((7, 5.6, 4.6), (8, 9.6, 5))]:
        m.box(frm, to, 'rune_orange')
    for (frm, to, ang) in [((3, 4, 7), (4, 8, 8), 22.5), ((12, 4, 7), (13, 8, 8), -22.5), ((7.5, 3, 4), (8.5, 7, 5), 45)]:
        m.box(frm, to, 'steel', 'z' if frm[0] != 7.5 else 'x', ang)
    return m


def abyssal_fang():
    """Vorath's relic: one curved fang as long as a sword, glowing teal along its core, coral and barnacles grown over its root."""
    m = Model('abyssal_fang')
    m.box((4, 0, 5), (12, 4, 11), 'coral')
    m.box((3, 1, 4), (7, 5, 8), 'coral_b', 'y', 22.5)
    m.box((9, 1, 8), (13, 4, 12), 'barnacle', 'y', -22.5)
    m.box((5, 3, 6), (11, 5, 10), 'pearl')
    m.seg_chain((8, 4.5, 8), [(4, 5, 0), (4, 4.4, 22.5), (3.5, 3.6, 22.5), (3, 2.8, 45), (2.5, 2, 45), (2, 1.2, 45)], 'z',
                lambda i: 'bone' if i % 2 == 0 else 'pearl', 4.5)
    m.seg_chain((8, 5, 10.35), [(4, 1.6, 0), (4, 1.4, 22.5), (3.5, 1.2, 22.5), (3, 1, 45)], 'z', lambda i: 'water_glow', 0.5)
    m.seg_chain((8, 5, 5.65), [(4, 1.6, 0), (4, 1.4, 22.5), (3.5, 1.2, 22.5), (3, 1, 45)], 'z', lambda i: 'water_glow', 0.5)
    for (frm, to, ang) in [((2, 3, 5), (3, 8, 6), -22.5), ((12, 2, 9), (13, 7, 10), 22.5), ((3, 4, 10), (4, 7, 11), 45)]:
        m.box(frm, to, 'coral', 'z', ang)
        m.box((frm[0] - 0.3, to[1] - 1, frm[2] - 0.3), (to[0] + 0.3, to[1], to[2] + 0.3), 'cyan_core', 'z', ang, (frm[0] + 0.5, frm[1], frm[2] + 0.5))
    return m


def frozen_voice():
    """The White Silence's relic: a bell of clear ice, cracked, bound in chains, a black flame trapped inside where its voice was."""
    m = Model('frozen_voice')
    m.box((3, 1, 3), (13, 3, 13), 'ice_d')
    m.box((4, 3, 4), (12, 10, 12), 'ice')
    m.box((5, 10, 5), (11, 12, 11), 'ice')
    m.box((6.5, 12, 6.5), (9.5, 14, 9.5), 'ice_d')
    m.box((7.3, 14, 7.3), (8.7, 15.5, 8.7), 'steel')
    m.box((6, 4, 11.9), (10, 9, 12.3), 'abyss')
    m.box((7, 4.5, 12.2), (9, 8, 12.6), 'abyss_glow')
    m.box((7.4, 7.5, 12.3), (8.6, 9.5, 12.7), 'abyss_glow')
    for (frm, to, ang) in [((2.5, 6, 2.5), (13.5, 7, 13.5), 0), ((7.5, 1, 2.5), (8.5, 12, 13.5), 45)]:
        m.box(frm, to, 'iron_dk', 'y', ang)
    for k in range(6):
        y = 1 + k * 1.6
        m.box((1.5 + (k % 2) * 0.4, y, 7.4), (2.7 + (k % 2) * 0.4, y + 1.4, 8.6), 'iron_dk', 'x', 45 if k % 2 else 0)
    for (frm, to, ang) in [((5, 9, 3.9), (6, 12, 4.2), 22.5), ((10, 5, 11.9), (11, 9, 12.2), -22.5), ((3.9, 5, 9), (4.2, 8, 10), 0)]:
        m.box(frm, to, 'frost_glow', 'z', ang)
    for (x, z) in [(3, 3), (12, 4), (4, 12), (12, 12)]:
        m.box((x, 1, z), (x + 1, 3.5, z + 1), 'glow_w', 'y', 45)
    return m


def glass_stinger():
    """Kharzul's relic: a jointed stinger of red glass in gold bands, the last grain of sand glowing in its tip."""
    m = Model('glass_stinger')
    m.box((4, 0, 4), (12, 2, 12), 'gold_d')
    m.box((5, 2, 5), (11, 4, 11), 'sandstone_r')
    end = m.seg_chain((8, 4, 8), [(3.5, 5, -22.5), (3.2, 4.6, -45), (3, 4.2, -45), (2.8, 3.8, 0), (2.6, 3.4, 22.5), (2.4, 3, 45)], 'z',
                      lambda i: 'glass_red', 4.4)
    m.seg_chain((8, 4, 10.4), [(3.5, 1, -22.5), (3.2, 1, -45), (3, 1, -45), (2.8, 1, 0), (2.6, 1, 22.5)], 'z', lambda i: 'gold', 0.6)
    m.seg_chain((8, 4, 5.6), [(3.5, 1, -22.5), (3.2, 1, -45), (3, 1, -45), (2.8, 1, 0), (2.6, 1, 22.5)], 'z', lambda i: 'gold', 0.6)
    x, y, z = end
    m.seg_chain((x, y, z), [(2.5, 2.4, 45), (2.2, 1.6, 45), (1.6, 0.8, 45)], 'z', lambda i: 'glass_glow' if i < 2 else 'sun_glow', 2.4)
    for (frm, to, ang) in [((3, 1.5, 7), (5, 3, 9), 45), ((11, 1.5, 7), (13, 3, 9), -45)]:
        m.box(frm, to, 'glass_red', 'z', ang)
    m.box((7.3, 1.8, 7.3), (8.7, 4.6, 8.7), 'sand_glow')
    return m


def chronal_eye():
    """Vexor's relic: his eye, torn out with its gold frame, the violet iris still turning, cogs and broken hands round it."""
    m = Model('chronal_eye')
    m.box((3, 0, 6), (13, 2, 10), 'iron_dk')
    m.box((6, 2, 7), (10, 4, 9), 'brass_d')
    m.box((2, 4, 6.5), (14, 15, 9.5), 'brass_d')
    m.box((3, 5, 6.2), (13, 14, 9.8), 'iron_dk')
    m.box((4, 6, 9.6), (12, 13, 10.1), 'rift_glow')
    m.box((5.5, 7.5, 10), (10.5, 11.5, 10.4), 'rift_glow2')
    m.box((7.4, 6.5, 10.3), (8.6, 12.5, 10.7), 'void')
    for (frm, to) in [((2, 14, 6), (14, 15.5, 10)), ((2, 3.5, 6), (14, 5, 10))]:
        m.box(frm, to, 'gold')
    for (cx, cy, r) in [(2.5, 13.5, 2.2), (13.5, 5, 2.2)]:
        m.box((cx - r, cy - r, 6.8), (cx + r, cy + r, 9.2), 'brass', 'z', 0)
        m.box((cx - r, cy - r, 6.9), (cx + r, cy + r, 9.1), 'brass', 'z', 45)
        m.box((cx - 0.7, cy - 0.7, 9.1), (cx + 0.7, cy + 0.7, 9.6), 'gold_glow')
    m.box((12.5, 10, 7.5), (16.5, 11, 8.5), 'iron_dk', 'z', 22.5)
    m.box((-0.5, 8, 7.5), (3.5, 9, 8.5), 'iron_dk', 'z', -45)
    for (frm, to) in [((4, 15.5, 7.5), (5, 16.5, 8.5)), ((11, 15.5, 7.5), (12, 16.5, 8.5)), ((7.5, 15.5, 7.5), (8.5, 17, 8.5))]:
        m.box(frm, to, 'gold_glow')
    return m


def living_spore():
    """The Bloom Mother's relic: her seed, a cage of bone round a heart of magenta light, sprouting tiny caps."""
    m = Model('living_spore')
    m.box((4, 0, 4), (12, 2, 12), 'root_c')
    m.box((5, 3, 5), (11, 11, 11), 'flesh_p')
    m.box((6, 4, 6), (10, 10, 10), 'bloom_glow')
    for ang in (0, 45):
        for (frm, to) in [((7.4, 1, 3.5), (8.6, 13, 4.5)), ((7.4, 1, 11.5), (8.6, 13, 12.5)), ((3.5, 1, 7.4), (4.5, 13, 8.6)),
                          ((11.5, 1, 7.4), (12.5, 13, 8.6))]:
            m.box(frm, to, 'petal_c', 'y', ang, (8, 7, 8))
    m.box((4, 12, 4), (12, 13.5, 12), 'petal_c', 'y', 45, (8, 12, 8))
    m.box((5, 6.5, 3), (11, 7.5, 13), 'petal_c')
    for (x, z, h, w, st) in [(9, 9, 2.5, 3, 'cap_m'), (5, 10, 1.5, 2, 'cap_m'), (6.5, 6, 3.5, 3.5, 'cap_m'), (11, 5, 1.2, 2, 'cap_m')]:
        m.box((x - 0.4, 13.5, z - 0.4), (x + 0.4, 13.5 + h, z + 0.4), 'root_c')
        m.box((x - w / 2, 13.5 + h, z - w / 2), (x + w / 2, 14.3 + h, z + w / 2), st)
    for (frm, to, ang) in [((2, 0, 6), (6, 1, 7), 22.5), ((10, 0, 9), (14, 1, 10), -22.5), ((7, 0, 12), (8, 1, 15), 45)]:
        m.box(frm, to, 'root_c', 'y', ang)
    for k in range(5):
        a = k * 2 * math.pi / 5
        x, z = 8 + 4.6 * math.cos(a), 8 + 4.6 * math.sin(a)
        m.box((x - 0.4, 4 + k, z - 0.4), (x + 0.4, 5 + k, z + 0.4), 'bloom_glow')
    return m


def hand_of_genesis():
    """The Unmaker's drop: a gauntlet of bone-white and black plate set with all eight relic stones round a white star in the palm."""
    m = Model('hand_of_genesis')
    m.box((4, 0, 5), (12, 4, 11), 'unmade_b')
    m.box((3.5, 3.5, 4.5), (12.5, 5, 11.5), 'gold')
    m.box((4, 5, 5.5), (12, 11, 10.5), 'unmade_w')
    m.box((5.5, 6.5, 10.3), (10.5, 10, 10.8), 'gold')
    m.box((7, 7.3, 10.7), (9, 9.3, 11.2), 'accretion2')
    stones = ['shard_g', 'shard_c', 'shard_v', 'shard_t', 'shard_i', 'shard_r', 'shard_y', 'shard_m']
    pts = [(5, 6.5), (5, 9.5), (6.5, 11), (8, 11.2), (9.5, 11), (11, 9.5), (11, 6.5), (8, 5.6)]
    for st, (x, y) in zip(stones, pts):
        m.box((x - 0.7, y - 0.7, 10.4), (x + 0.7, y + 0.7, 11.1), st)
    for i, x in enumerate((4.8, 6.9, 9.0, 11.1)):
        h = [4.2, 5.2, 5.0, 4.0][i]
        m.seg_chain((x, 11, 8), [(h * 0.5, 1.9, 0), (h * 0.5, 1.7, -22.5)], 'x', lambda k: 'unmade_b' if k == 0 else 'unmade_w', 2)
        m.box((x - 0.95, 11 + h * 0.5 - 0.6, 6.9), (x + 0.95, 11 + h * 0.5 + 0.2, 9.1), 'gold')
    m.seg_chain((12, 6, 8.5), [(3, 2, -45), (2.6, 1.8, -22.5)], 'z', lambda k: 'unmade_b' if k == 0 else 'unmade_w', 2)
    for (frm, to) in [((3.8, 1, 6), (4.2, 4, 7)), ((11.8, 1, 9), (12.2, 4, 10)), ((7.6, 0.3, 10.9), (8.4, 3.5, 11.3))]:
        m.box(frm, to, 'rift_glow')
    for (frm, to, ang) in [((3, 4.5, 7.5), (4, 9, 8.5), 22.5), ((12, 4.5, 7.5), (13, 9, 8.5), -22.5)]:
        m.box(frm, to, 'gold', 'z', ang)
    return m


RELICS = [('rootbound_heart', 'Rootbound Heart', 'mossback_titan', 'grove', rootbound_heart),
          ('storm_talon', 'Storm Talon', 'tempest_roc', 'skyreach', storm_talon),
          ('sovereign_hand', 'Sovereign Hand', 'hollow_king', 'hollow', sovereign_hand),
          ('abyssal_fang', 'Abyssal Fang', 'vorath', 'drowned', abyssal_fang),
          ('frozen_voice', 'Frozen Voice', 'white_silence', 'pale', frozen_voice),
          ('glass_stinger', 'Glass Stinger', 'kharzul', 'scarlet', glass_stinger),
          ('chronal_eye', 'Chronal Eye', 'vexor', 'clockwork', chronal_eye),
          ('living_spore', 'Living Spore', 'bloom_mother', 'mycelial', living_spore)]
REALM_COLOR = {'grove': (110, 230, 90), 'skyreach': (110, 215, 255), 'hollow': (255, 140, 40), 'drowned': (60, 230, 200),
               'pale': (220, 238, 255), 'scarlet': (250, 60, 60), 'clockwork': (255, 205, 80), 'mycelial': (255, 90, 225)}


def pedestal_elements(realm):
    """The Relic Pedestal: a stepped plinth of polished blackstone with gold trim and a realm-coloured rune on every side."""
    m = Model('pedestal')
    m.box((0, 0, 0), (16, 3, 16), 'plate_dk')
    m.box((1, 3, 1), (15, 4, 15), 'gold_d')
    m.box((3, 4, 3), (13, 10, 13), 'plate_dk')
    m.box((2, 10, 2), (14, 12, 14), 'plate_dk')
    m.box((2.5, 12, 2.5), (13.5, 12.5, 13.5), 'gold_d')
    for (frm, to) in [((6, 5, 12.8), (10, 9, 13.3)), ((6, 5, 2.7), (10, 9, 3.2)), ((12.8, 5, 6), (13.3, 9, 10)), ((2.7, 5, 6), (3.2, 9, 10))]:
        m.box(frm, to, 'rune_' + realm)
    return m


# =================================================================================================== outputs
def swatch_styles():
    st = dict(mobspecs.STYLES)
    for realm, col in REALM_COLOR.items():
        st['rune_' + realm] = dict(base=col, var=8, patches=[(tuple(min(255, c + 60) for c in col), 10, (1, 1))])
    return st


def texture(model_styles, seed):
    """A 64 x 64 texture: 8 x 8 swatches of 8 px, painted in each material's colours. Returns the image and style -> (u, v) in 1/16."""
    styles = swatch_styles()
    img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    px = img.load()
    rnd = random.Random(seed)
    where = {}
    for i, name in enumerate(model_styles):
        cx, cy = (i % 8) * 8, (i // 8) * 8
        st = styles[name]
        for x in range(8):
            for y in range(8):
                n = rnd.randint(-st['var'], st['var'])
                px[cx + x, cy + y] = tuple(max(0, min(255, c + n)) for c in st['base']) + (255,)
        for (col, count, (lo, hi)) in st.get('patches', []) + ([st['dots']] if 'dots' in st else []):
            for _ in range(max(1, count // 6)):
                x, y = rnd.randint(0, 7), rnd.randint(0, 7)
                d.rectangle([cx + x, cy + y, cx + min(7, x + rnd.randint(lo, hi) - 1), cy + min(7, y + rnd.randint(lo, hi) - 1)], fill=col + (255,))
        if 'cracks' in st:
            x, y = rnd.randint(0, 7), rnd.randint(0, 7)
            for _ in range(4):
                nx, ny = min(7, max(0, x + rnd.randint(-2, 2))), min(7, max(0, y + rnd.randint(-2, 2)))
                d.line([cx + x, cy + y, cx + nx, cy + ny], fill=st['cracks'] + (255,))
                x, y = nx, ny
        where[name] = (cx / 4.0, cy / 4.0)
    return img, where


def json_elements(els, where, shift=(0, 0, 0), k=1.0, about=(8, 0, 8)):
    out = []
    for e in els:
        def tr(p):
            return [round(about[i] + (p[i] - about[i]) * k + shift[i], 3) for i in range(3)]
        u, v = where[e['style']]
        faces = {f: {'uv': [u + 0.25, v + 0.25, u + 1.75, v + 1.75], 'texture': '#t'} for f in ('north', 'south', 'east', 'west', 'up', 'down')}
        el = {'from': tr(e['frm']), 'to': tr(e['to']), 'faces': faces}
        if e['axis'] and e['angle']:
            el['rotation'] = {'angle': e['angle'], 'axis': e['axis'], 'origin': tr(e['origin'])}
        for i in range(3):                                          # vanilla rejects coordinates outside -16..32
            el['from'][i] = max(-16, min(32, el['from'][i]))
            el['to'][i] = max(-16, min(32, el['to'][i]))
        out.append(el)
    return out


DISPLAY = {'gui': {'rotation': [25, -35, 0], 'translation': [0, 0, 0], 'scale': [0.85, 0.85, 0.85]},
           'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.4, 0.4, 0.4]},
           'fixed': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.75, 0.75, 0.75]},
           'head': {'rotation': [0, 0, 0], 'translation': [0, 10, 0], 'scale': [0.8, 0.8, 0.8]},
           'thirdperson_righthand': {'rotation': [0, 45, 0], 'translation': [0, 2, 1], 'scale': [0.5, 0.5, 0.5]},
           'thirdperson_lefthand': {'rotation': [0, -45, 0], 'translation': [0, 2, 1], 'scale': [0.5, 0.5, 0.5]},
           'firstperson_righthand': {'rotation': [0, 30, 0], 'translation': [1, 2, 0], 'scale': [0.55, 0.55, 0.55]},
           'firstperson_lefthand': {'rotation': [0, -30, 0], 'translation': [1, 2, 0], 'scale': [0.55, 0.55, 0.55]}}


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(obj, f, indent=1)


def styles_of(*models):
    seen = []
    for m in models:
        for e in m.els:
            if e['style'] not in seen:
                seen.append(e['style'])
    assert len(seen) <= 64
    return seen


def write_all():
    allm = [(key, fn()) for key, _, _, _, fn in RELICS] + [('hand_of_genesis', hand_of_genesis())]
    for i, (key, m) in enumerate(allm):
        img, where = texture(styles_of(m), 700 + i)
        os.makedirs(f'{ASSETS}/textures/item', exist_ok=True)
        img.save(f'{ASSETS}/textures/item/{key}.png')
        write_json(f'{ASSETS}/models/item/{key}.json', {'textures': {'t': f'aurelia:item/{key}', 'particle': f'aurelia:item/{key}'},
                                                       'display': DISPLAY, 'elements': json_elements(m.els, where)})
    # the pedestal: one texture holding the plinth's materials and every relic's, so a filled pedestal is one model
    variants = {}
    for key, _, _, realm, fn in RELICS:
        ped = pedestal_elements(realm)
        rel = fn()
        img, where = texture(styles_of(ped, rel), 800)
        img.save(f'{ASSETS}/textures/block/relic_pedestal_{realm}.png')
        tex = {'t': f'aurelia:block/relic_pedestal_{realm}', 'particle': f'aurelia:block/relic_pedestal_{realm}'}
        empty = json_elements(ped.els, where)
        filled = empty + json_elements(rel.els, where, shift=(0, 12.5, 0), k=0.75)
        write_json(f'{ASSETS}/models/block/relic_pedestal_{realm}.json', {'textures': tex, 'elements': empty})
        write_json(f'{ASSETS}/models/block/relic_pedestal_{realm}_filled.json', {'textures': tex, 'elements': filled})
        variants[f'realm={realm},filled=false'] = {'model': f'aurelia:block/relic_pedestal_{realm}'}
        variants[f'realm={realm},filled=true'] = {'model': f'aurelia:block/relic_pedestal_{realm}_filled'}
    write_json(f'{ASSETS}/blockstates/relic_pedestal.json', {'variants': variants})
    write_json(f'{ASSETS}/models/item/relic_pedestal.json', {'parent': 'aurelia:block/relic_pedestal_grove_filled'})


# =================================================================================================== preview
def parts_of(m, k=1.0, shift=(0, 0, 0)):
    """Box-model parts (render_models) for a design: y up, centred on x and z."""
    parts = []
    for i, e in enumerate(m.els):
        o = e['origin']
        pv = tuple((o[j] - (8 if j != 1 else 0)) * k + shift[j] for j in range(3))
        frm = tuple((e['frm'][j] - o[j]) * k for j in range(3))
        size = tuple((e['to'][j] - e['frm'][j]) * k for j in range(3))
        a = math.radians(e['angle']) if e['axis'] else 0.0
        rot = (a if e['axis'] == 'x' else 0.0, a if e['axis'] == 'y' else 0.0, a if e['axis'] == 'z' else 0.0)
        parts.append(dict(name=f'e{i}', size=tuple(max(1, int(round(s))) for s in size), origin=frm, pivot=pv, rot=rot, style=e['style'],
                          anim='none', eyes=None, parent=None))
    return parts


def render_relic(m, size=420, bg=None, yaw=-30, pitch=18, on_pedestal=None, k=8.0):
    """A relic at k times life size (so the box painter has room for detail), optionally standing on its pedestal."""
    import render_models as rm
    mobspecs.STYLES.update({key: v for key, v in swatch_styles().items() if key.startswith('rune_')})
    parts = parts_of(m, k)
    if on_pedestal:
        parts = parts_of(pedestal_elements(on_pedestal), k) + parts_of(m, k * 0.75, shift=(0, 12.5 * k, 0))
        for i, p in enumerate(parts):
            p['name'] = f'p{i}'
    tex, _ = mobspecs.paint(parts, 5)
    glow = tex.info.pop('glow')
    im, _ = rm.render(parts, tex, glow, yaw, pitch, size=size, bg=bg, alpha=bg is None)
    return im


if __name__ == '__main__':
    write_all()
    print('relic models written')
