"""The Lanternray: a broad, gentle ray of the Drowned Expanse's reefs, with rows of lights along its wings. It glides in
slow wingbeats and flashes all its lights at once when struck (or when it agrees to lead you somewhere).

Writes geo/entity/lanternray.geo.json, animations/entity/lanternray.animation.json, textures/entity/lanternray.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'lanternray'

SKIN = Material('chitin', (52, 92, 128), dark=(24, 46, 72), light=(110, 160, 190), seed=301)
BELLY = Material('flesh', (196, 214, 222), dark=(150, 172, 186), light=(232, 240, 244), seed=303)
FIN = Material('membrane', (64, 110, 150), dark=(34, 64, 96), light=(130, 180, 210), seed=305, alpha=230)
LIGHT = Material('glow', (120, 240, 220), dark=(40, 160, 160), light=(230, 255, 245), seed=307, glow=True)
EYE = Material('eye', (20, 30, 40), light=(200, 255, 250), rim=False)


def build():
    m = Model(NAME, 128, 64)
    root = m.bone('root', (0, 4, 0))
    body = m.bone('body', (0, 4, 0), root)
    body.cube((-5, 1, -9), (10, 5, 16), SKIN)
    body.cube((-4, 0.5, -8), (8, 1, 14), BELLY)
    body.cube((-3, 2, -12), (6, 3, 3), SKIN)                      # snout
    body.cube((-3.6, 4, -10.5), (1, 1, 1), EYE)
    body.cube((2.6, 4, -10.5), (1, 1, 1), EYE)
    for k, z in enumerate((-6, -2, 2)):
        body.cube((-0.5, 6, z), (1, 1, 2), LIGHT)                  # dorsal lights
    for side, s in ((-1, 'l'), (1, 'r')):
        inner = m.bone(f'wing_{s}', (side * 5, 3.5, -1), body)
        o = (5, 3, -8) if side > 0 else mirror_x((5, 3, -8), (9, 1, 13))
        inner.cube(o, (9, 1, 13), FIN)
        for i, z in enumerate((-6, -2, 2)):
            o = (7 + i % 2, 4, z) if side > 0 else mirror_x((7 + i % 2, 4, z), (1, 0.5, 1))
            inner.cube(o, (1, 0.5, 1), LIGHT)
        outer = m.bone(f'wingtip_{s}', (side * 14, 3.5, -1), inner)
        o = (14, 3.2, -6) if side > 0 else mirror_x((14, 3.2, -6), (8, 0.6, 9))
        outer.cube(o, (8, 0.6, 9), FIN)
        for i, z in enumerate((-4, 0)):
            o = (16 + 2 * i, 3.8, z) if side > 0 else mirror_x((16 + 2 * i, 3.8, z), (1, 0.5, 1))
            outer.cube(o, (1, 0.5, 1), LIGHT)
    tail = m.bone('tail', (0, 3.5, 7), body)
    tail.cube((-1, 3, 7), (2, 1.5, 8), SKIN)
    tail2 = m.bone('tail2', (0, 3.6, 15), tail)
    tail2.cube((-0.5, 3.3, 15), (1, 1, 9), SKIN)
    tail2.cube((-0.5, 3.3, 23), (1, 1, 1), LIGHT)
    return m


def flap(a, amp=16):
    for s, sd in (('l', -1), ('r', 1)):
        a.wave(f'wing_{s}', 'rotation', lambda p, sd=sd: [0, 0, sd * sin(p, amp)], steps=16)
        a.wave(f'wingtip_{s}', 'rotation', lambda p, sd=sd: [0, 0, sd * sin(p, amp * 1.3, -0.12)], steps=16)


def animations():
    out = []
    a = Anim(f'animation.{NAME}.swim', 2.4)
    flap(a)
    a.wave('body', 'position', lambda p: [0, sin(p, 0.8, 0.25), 0], steps=16)
    a.wave('tail', 'rotation', lambda p: [sin(p, 6, 0.3), sin(p, 8), 0], steps=16)
    a.wave('tail2', 'rotation', lambda p: [0, sin(p, 14, -0.15), 0], steps=16)
    out.append(a)

    # the flash: wings snap up and every light swells
    a = Anim(f'animation.{NAME}.flash', 0.6, loop=False)
    for s, sd in (('l', -1), ('r', 1)):
        a.keys(f'wing_{s}', 'rotation', [(0, [0, 0, 0]), (0.15, [0, 0, sd * 30]), (0.6, [0, 0, 0])])
    a.keys('body', 'scale', [(0, [1, 1, 1]), (0.15, [1.08, 1.15, 1.05]), (0.6, [1, 1, 1])])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 1.0, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (1.0, [0, 0, 170])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (1.0, [0, -6, 0])])
    for s in 'lr':
        a.keys(f'wing_{s}', 'rotation', [(0, [0, 0, 0]), (1.0, [0, 0, 0])])
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
