"""The Deepcaller: the leviathan of the Abyssal Vault, an angler of the trench as long as a house. A great lantern hangs
from a stalk over its head; that lantern is its lure, and the flash it gives is the attack you must look away from. Its
jaw is wide enough to swallow a diver; its tail drives its charges; its fin-arms stir the vortex.

Writes geo/entity/deepcaller.geo.json, animations/entity/deepcaller.animation.json, textures/entity/deepcaller.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'deepcaller'

HIDE = Material('chitin', (30, 40, 62), dark=(12, 16, 28), light=(70, 88, 120), seed=501, bands=6)
PLATE = Material('plate', (46, 60, 82), dark=(20, 26, 40), light=(96, 116, 146), seed=503, rust=(60, 120, 110))
BELLY = Material('flesh', (92, 104, 120), dark=(60, 68, 84), light=(140, 150, 166), seed=505)
FIN = Material('membrane', (40, 70, 100), dark=(18, 36, 56), light=(90, 140, 180), seed=507, alpha=220)
TOOTH = Material('bone', (220, 226, 210), dark=(150, 156, 140), seed=509)
MOUTH = Material('flesh', (70, 20, 40), dark=(36, 8, 20), light=(120, 50, 70), seed=511)
LURE = Material('glow', (140, 230, 255), dark=(40, 120, 180), light=(240, 252, 255), seed=513, glow=True)
SPOTS = Material('glow', (90, 200, 220), dark=(30, 90, 120), light=(180, 250, 255), seed=515, glow=True)
EYE = Material('eye', (200, 255, 255), light=(255, 255, 255), glow=True, rim=False)


def build():
    m = Model(NAME, 512, 256)
    root = m.bone('root', (0, 24, 0))
    body = m.bone('body', (0, 24, 0), root)
    body.cube((-20, 6, -20), (40, 34, 36), HIDE)
    body.cube((-18, 4, -18), (36, 3, 32), BELLY)
    body.cube((-14, 39, -16), (28, 4, 26), PLATE)                 # back plates
    for k, (x, z) in enumerate(((-16, -10), (14, -6), (-12, 6), (12, 8), (-6, -16), (4, 12))):
        body.cube((x, 26 + (k % 3) * 3, z), (2, 2, 2), SPOTS)
    head = m.bone('head', (0, 24, -20), body)
    head.cube((-22, 14, -46), (44, 26, 26), HIDE)
    head.cube((-20, 38, -44), (40, 4, 22), PLATE)
    head.cube((-21, 13, -45), (42, 2, 24), TOOTH)                 # upper teeth
    for side in (-1, 1):
        o = (16, 30, -44) if side > 0 else mirror_x((16, 30, -44), (3, 3, 3))
        head.cube(o, (3, 3, 3), EYE)
    jaw = m.bone('jaw', (0, 14, -22), head)
    jaw.cube((-21, 2, -48), (42, 10, 27), BELLY)
    jaw.cube((-20, 12, -47), (40, 2, 25), TOOTH)
    jaw.cube((-18, 10, -45), (36, 2, 22), MOUTH)
    stalk = m.bone('stalk', (0, 42, -30), head, rotation=(-30, 0, 0))
    stalk.cube((-1.5, 42, -32), (3, 18, 3), HIDE)
    stalk2 = m.bone('stalk2', (0, 60, -31), stalk, rotation=(60, 0, 0))
    stalk2.cube((-1.2, 60, -32), (2.4, 14, 2.4), HIDE)
    lure = m.bone('lure', (0, 74, -31), stalk2)
    lure.cube((-4, 72, -35), (8, 8, 8), LURE)
    lure.cube((-5, 79, -36), (10, 2, 10), FIN)
    for side, s in ((-1, 'l'), (1, 'r')):
        fin = m.bone(f'fin_{s}', (side * 20, 18, -8), body)
        o = (20, 16, -14) if side > 0 else mirror_x((20, 16, -14), (22, 2, 16))
        fin.cube(o, (22, 2, 16), FIN)
        o = (20, 14, -12) if side > 0 else mirror_x((20, 14, -12), (6, 6, 10))
        fin.cube(o, (6, 6, 10), HIDE)
    t1 = m.bone('tail1', (0, 24, 16), body)
    t1.cube((-14, 10, 16), (28, 24, 22), HIDE)
    t1.cube((-10, 33, 18), (20, 3, 18), PLATE)
    t2 = m.bone('tail2', (0, 22, 38), t1)
    t2.cube((-9, 14, 38), (18, 16, 20), HIDE)
    t2.cube((-1, 29, 40), (2, 8, 16), FIN)
    t3 = m.bone('tail3', (0, 22, 58), t2)
    t3.cube((-5, 17, 58), (10, 10, 16), HIDE)
    fluke = m.bone('fluke', (0, 22, 74), t3)
    fluke.cube((-2, 4, 72), (4, 36, 12), FIN)
    return m


def swim(a, amp=6, speed=1):
    a.wave('tail1', 'rotation', lambda p: [0, sin(p * speed, amp), 0], steps=16)
    a.wave('tail2', 'rotation', lambda p: [0, sin(p * speed, amp * 1.5, -0.12), 0], steps=16)
    a.wave('tail3', 'rotation', lambda p: [0, sin(p * speed, amp * 2, -0.24), 0], steps=16)
    a.wave('fluke', 'rotation', lambda p: [0, sin(p * speed, amp * 2.5, -0.36), 0], steps=16)
    for s, sd in (('l', -1), ('r', 1)):
        a.wave(f'fin_{s}', 'rotation', lambda p, sd=sd: [sin(p * speed, 8), 0, sd * sin(p * speed, 10, 0.25)], steps=16)


def animations():
    out = []
    a = Anim(f'animation.{NAME}.swim', 3.0)
    swim(a)
    a.wave('jaw', 'rotation', lambda p: [3 + sin(p, 2), 0, 0])
    a.wave('lure', 'scale', lambda p: [1 + sin(p * 2, 0.05)] * 3)
    a.wave('stalk', 'rotation', lambda p: [-30 + sin(p, 4), sin(p, 5, 0.3), 0])
    a.wave('body', 'position', lambda p: [0, sin(p, 1.5), 0])
    out.append(a)

    # lure tell: the stalk lifts the lantern high and it swells; then the flash
    a = Anim(f'animation.{NAME}.lure_tell', 1.5, loop='hold')
    swim(a, 3)
    a.keys('stalk', 'rotation', [(0, [-30, 0, 0]), (1.0, [-5, 0, 0]), (1.5, [0, 0, 0])])
    a.keys('lure', 'scale', [(0, [1, 1, 1]), (1.2, [1.6, 1.6, 1.6]), (1.5, [1.8, 1.8, 1.8])])
    out.append(a)
    a = Anim(f'animation.{NAME}.lure_flash', 0.6, loop=False)
    a.keys('lure', 'scale', [(0, [1.8, 1.8, 1.8]), (0.1, [2.6, 2.6, 2.6]), (0.6, [1, 1, 1])])
    a.keys('stalk', 'rotation', [(0, [0, 0, 0]), (0.6, [-30, 0, 0])])
    out.append(a)

    # charge tell: it coils, jaw opening, tail drawn to one side
    a = Anim(f'animation.{NAME}.charge_tell', 1.25, loop='hold')
    a.keys('tail1', 'rotation', [(0, [0, 0, 0]), (1.0, [0, 18, 0])])
    a.keys('tail2', 'rotation', [(0, [0, 0, 0]), (1.0, [0, 22, 0])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (1.0, [28, 0, 0])])
    a.keys('body', 'position', [(0, [0, 0, 0]), (1.0, [0, 0, 6])])
    out.append(a)
    a = Anim(f'animation.{NAME}.charge', 0.5)
    swim(a, 10, 2)
    a.keys('jaw', 'rotation', [(0, [30, 0, 0]), (0.5, [30, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.stunned', 2.0)
    a.wave('root', 'rotation', lambda p: [sin(p, 4), 0, 25 + sin(p, 6)])
    a.wave('jaw', 'rotation', lambda p: [18 + sin(p, 4), 0, 0])
    a.wave('stalk', 'rotation', lambda p: [10 + sin(p, 6), 0, 0])
    out.append(a)

    a = Anim(f'animation.{NAME}.vortex', 1.0)
    for s, sd in (('l', -1), ('r', 1)):
        a.wave(f'fin_{s}', 'rotation', lambda p, sd=sd: [sin(p, 30), sd * sin(p, 20, 0.25), sd * 25], steps=16)
    a.wave('root', 'rotation', lambda p: [0, p * 360, 0], steps=16)
    a.wave('jaw', 'rotation', lambda p: [20, 0, 0])
    out.append(a)

    a = Anim(f'animation.{NAME}.brood', 1.5, loop='hold')
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.6, [40, 0, 0]), (1.5, [35, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.6, [-12, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.roar', 2.0, loop=False)
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.4, [45, 0, 0]), (1.6, [45, 0, 0]), (2.0, [0, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.4, [-15, 0, 0]), (1.6, [-15, 0, 0]), (2.0, [0, 0, 0])])
    a.keys('lure', 'scale', [(0, [1, 1, 1]), (0.4, [1.5, 1.5, 1.5]), (2.0, [1, 1, 1])])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 3.0, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (3.0, [0, 0, 160])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (3.0, [0, -14, 0])])
    a.keys('lure', 'scale', [(0, [1, 1, 1]), (1.0, [2, 2, 2]), (3.0, [0.3, 0.3, 0.3])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (3.0, [30, 0, 0])])
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
