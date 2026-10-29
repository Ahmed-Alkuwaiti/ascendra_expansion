"""The Lumen Mite: a palm-sized star-eater of the Astral Abyss, all spines and a lantern of a belly. Swarms drift around
rift growth and spit sparks of stolen starlight. Its glowing abdomen swells before it spits: that is the tell.

Writes geo/entity/lumen_mite.geo.json, animations/entity/lumen_mite.animation.json, textures/entity/lumen_mite.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'lumen_mite'

SHELL = Material('void', (34, 36, 70), dark=(14, 14, 32), light=(70, 76, 128), seed=101)
SHELL.stars = 0.04
SPINE = Material('bone', (176, 190, 220), dark=(96, 104, 140), seed=103)
LANTERN = Material('glow', (90, 230, 230), dark=(30, 140, 160), light=(220, 255, 250), seed=105, glow=True)
WING = Material('membrane', (150, 200, 240), dark=(90, 130, 190), light=(220, 240, 255), seed=107, alpha=120, rim=False)
EYE = Material('eye', (255, 220, 120), light=(255, 255, 220), glow=True, rim=False)
LEG = Material('chitin', (40, 42, 80), dark=(20, 20, 40), light=(80, 86, 140), seed=109)


def build():
    m = Model(NAME, 64, 64)
    root = m.bone('root', (0, 0, 0))
    body = m.bone('body', (0, 8, 0), root)
    body.cube((-2.5, 6, -3), (5, 4, 6), SHELL)
    body.cube((-1, 10, -2), (2, 1, 4), SPINE)                    # dorsal ridge
    for k, z in enumerate((-2, 0, 2)):
        body.cube((-0.5, 10, z), (1, 2 + (k % 2), 1), SPINE)      # spines
    head = m.bone('head', (0, 8, -3), body)
    head.cube((-2, 6.5, -6), (4, 3, 3), SHELL)
    head.cube((-1.6, 8.2, -6.2), (1, 1, 1), EYE)
    head.cube((0.6, 8.2, -6.2), (1, 1, 1), EYE)
    for side in (-1, 1):
        mand = m.bone(f'mandible_{"l" if side < 0 else "r"}', (side * 1.2, 7, -6), head)
        o = (0.6, 6, -8) if side > 0 else mirror_x((0.6, 6, -8), (1, 1, 2.5))
        mand.cube(o, (1, 1, 2.5), SPINE)
        ant = m.bone(f'antenna_{"l" if side < 0 else "r"}', (side * 1, 9.5, -5.5), head, rotation=(-35, -side * 20, 0))
        o = (0.5, 9.5, -10) if side > 0 else mirror_x((0.5, 9.5, -10), (0.5, 0.5, 4.5))
        ant.cube(o, (0.5, 0.5, 4.5), SPINE)
        o = (0.25, 9.25, -11) if side > 0 else mirror_x((0.25, 9.25, -11), (1, 1, 1))
        ant.cube(o, (1, 1, 1), LANTERN)
    lantern = m.bone('lantern', (0, 8, 3), body)
    lantern.cube((-2, 5.5, 3), (4, 4, 5), LANTERN)
    lantern.cube((-1.5, 6, 7.5), (3, 3, 1.5), LANTERN)
    lantern.cube((-2.3, 8.8, 3.5), (4.6, 1, 4), SHELL)            # a cap of shell over the glow
    for side, s in ((-1, 'l'), (1, 'r')):
        for i, (z, ln, ch) in enumerate(((-2, 7, 4), (1, 5.5, 3))):
            w = m.bone(f'wing{i}_{s}', (side * 2, 10, z), body, rotation=(0, 0, side * 12))
            o = (2, 10, z) if side > 0 else mirror_x((2, 10, z), (ln, 0, ch))
            w.cube(o, (ln, 0, ch), WING)
        for i, z in enumerate((-2, 0, 2)):
            leg = m.bone(f'leg{i}_{s}', (side * 2.2, 6.5, z), body, rotation=(0, 0, side * 35))
            o = (2.2, 3.5, z - 0.25) if side > 0 else mirror_x((2.2, 3.5, z - 0.25), (0.5, 3, 0.5))
            leg.cube(o, (0.5, 3, 0.5), LEG)
    return m


WINGS = [f'wing{i}_{s}' for i in (0, 1) for s in 'lr']


def buzz(a, amp=30):
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        ph = 0.25 if w.startswith('wing1') else 0.0
        a.wave(w, 'rotation', lambda p, sd=sd, ph=ph: [0, 0, sd * (12 + sin(p * 4, amp, ph))], steps=16)


def animations():
    out = []
    a = Anim(f'animation.{NAME}.fly', 0.5)
    buzz(a)
    a.wave('body', 'position', lambda p: [0, sin(p, 0.6), 0])
    a.wave('lantern', 'rotation', lambda p: [sin(p, 6, 0.2), 0, 0])
    for s in 'lr':
        for i in range(3):
            a.wave(f'leg{i}_{s}', 'rotation', lambda p, i=i: [sin(p, 12, i * 0.2), 0, 0])
    out.append(a)

    # the tell: the lantern swells and brightens, wings flare, head rears
    a = Anim(f'animation.{NAME}.spit_tell', 0.75, loop='hold')
    buzz(a, 40)
    a.keys('lantern', 'scale', [(0, [1, 1, 1]), (0.6, [1.45, 1.45, 1.3]), (0.75, [1.5, 1.5, 1.35])])
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.5, [-18, 0, 0]), (0.75, [-20, 0, 0])])
    a.keys('mandible_l', 'rotation', [(0, [0, 0, 0]), (0.5, [0, 30, 0])])
    a.keys('mandible_r', 'rotation', [(0, [0, 0, 0]), (0.5, [0, -30, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.spit', 0.4, loop=False)
    a.keys('lantern', 'scale', [(0, [1.5, 1.5, 1.35]), (0.1, [0.8, 0.8, 0.8]), (0.4, [1, 1, 1])])
    a.keys('body', 'rotation', [(0, [-20, 0, 0]), (0.1, [12, 0, 0]), (0.4, [0, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 0.8, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (0.8, [0, 0, 180])])
    a.keys('lantern', 'scale', [(0, [1, 1, 1]), (0.5, [1.6, 1.6, 1.6]), (0.8, [0.2, 0.2, 0.2])])
    out.append(a)
    return out


def write():
    m = build()
    for d in ('geo/entity', 'animations/entity', 'textures/entity'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    m.save(os.path.join(OUT, f'geo/entity/{NAME}.geo.json'))
    paint(m, os.path.join(OUT, f'textures/entity/{NAME}.png'))
    anims = animations()
    save(anims, os.path.join(OUT, f'animations/entity/{NAME}.animation.json'))
    return m, anims


if __name__ == '__main__':
    write()
    print(NAME, 'written')
