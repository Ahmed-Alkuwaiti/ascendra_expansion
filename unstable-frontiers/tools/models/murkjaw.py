"""The Murkjaw: a long ambush eel of the Drowned Expanse's caves, wrecks and kelp. Six body segments undulate as it swims.
Its tell: the jaw unhinges wide and the lure over its snout flares. Stunned, it goes slack and rolls.

Writes geo/entity/murkjaw.geo.json, animations/entity/murkjaw.animation.json, textures/entity/murkjaw.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'murkjaw'

HIDE = Material('chitin', (42, 58, 50), dark=(18, 26, 22), light=(86, 108, 88), seed=401, bands=4)
BELLY = Material('flesh', (128, 132, 104), dark=(88, 92, 70), light=(170, 172, 140), seed=403)
FIN = Material('membrane', (60, 82, 70), dark=(30, 44, 36), light=(110, 140, 120), seed=405, alpha=220)
TOOTH = Material('bone', (226, 220, 196), dark=(170, 160, 130), seed=407)
MOUTH = Material('flesh', (120, 30, 40), dark=(70, 14, 20), light=(170, 60, 70), seed=409)
LURE = Material('glow', (180, 255, 140), dark=(60, 170, 60), light=(240, 255, 220), seed=411, glow=True)
EYE = Material('eye', (255, 200, 60), light=(255, 250, 200), glow=True, rim=False)

SEGS = 6


def build():
    m = Model(NAME, 128, 128)
    root = m.bone('root', (0, 6, 0))
    head = m.bone('head', (0, 6, -8), root)
    head.cube((-3.5, 6, -16), (7, 5, 9), HIDE)
    head.cube((-3, 5.5, -15), (6, 0.5, 8), TOOTH)                 # upper teeth
    head.cube((-3.8, 9, -13), (1, 1, 1), EYE)
    head.cube((2.8, 9, -13), (1, 1, 1), EYE)
    stalk = m.bone('lure', (0, 11, -12), head, rotation=(-20, 0, 0))
    stalk.cube((-0.5, 11, -12), (1, 4, 1), HIDE)
    stalk.cube((-1, 14.5, -13), (2, 2, 2), LURE)
    jaw = m.bone('jaw', (0, 5.5, -8), head)
    jaw.cube((-3.2, 3, -16), (6.4, 2.5, 8.5), BELLY)
    jaw.cube((-2.8, 5.5, -15.5), (5.6, 0.5, 7.5), TOOTH)
    jaw.cube((-2.6, 4.4, -15), (5.2, 1, 6.5), MOUTH)
    parent = root
    z = -8
    for i in range(SEGS):
        w = 6.5 - i * 0.8
        hgt = 5 - i * 0.55
        seg = m.bone(f'seg{i}', (0, 6, z), parent)
        seg.cube((-w / 2, 8.5 - hgt / 2 - 0.5, z), (w, hgt, 7), HIDE)
        seg.cube((-w / 2 + 0.5, 8.5 - hgt / 2 - 0.8, z + 0.5), (w - 1, 0.5, 6), BELLY)
        seg.cube((-0.5, 8.5 + hgt / 2 - 0.5, z + 1), (1, 1.5, 5), FIN)   # dorsal fin
        if i == 0:
            for side in (-1, 1):
                o = (w / 2, 6.5, z + 1) if side > 0 else mirror_x((w / 2, 6.5, z + 1), (3, 0.5, 3))
                seg.cube(o, (3, 0.5, 3), FIN)
        parent = seg
        z += 7
    tail = m.bone('tailfin', (0, 8, z), parent)
    tail.cube((-0.5, 5.5, z), (1, 6, 5), FIN)
    return m


def undulate(a, amp=10, speed=1):
    for i in range(SEGS):
        a.wave(f'seg{i}', 'rotation', lambda p, i=i: [0, sin(p * speed, amp * (0.5 + i * 0.15), -i * 0.13), 0], steps=16)
    a.wave('tailfin', 'rotation', lambda p: [0, sin(p * speed, amp * 1.8, -0.9), 0], steps=16)
    a.wave('head', 'rotation', lambda p: [0, sin(p * speed, amp * 0.3, 0.1), 0], steps=16)


def animations():
    out = []
    a = Anim(f'animation.{NAME}.swim', 1.6)
    undulate(a)
    a.wave('jaw', 'rotation', lambda p: [sin(p, 3) + 4, 0, 0])
    out.append(a)

    # the tell: the jaw unhinges, the lure flares, the body coils back
    a = Anim(f'animation.{NAME}.tell', 1.0, loop='hold')
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.5, [38, 0, 0]), (1.0, [42, 0, 0])])
    a.keys('lure', 'scale', [(0, [1, 1, 1]), (0.5, [1.6, 1.6, 1.6]), (1.0, [1.8, 1.8, 1.8])])
    a.keys('lure', 'rotation', [(0, [0, 0, 0]), (1.0, [25, 0, 0])])
    for i in range(SEGS):
        sd = 1 if i % 2 == 0 else -1
        a.keys(f'seg{i}', 'rotation', [(0, [0, 0, 0]), (0.6, [0, sd * 14, 0]), (1.0, [0, sd * 16, 0])])
    a.keys('head', 'position', [(0, [0, 0, 0]), (1.0, [0, 0, 2])])
    out.append(a)

    a = Anim(f'animation.{NAME}.lunge', 0.4)
    undulate(a, 6, 2)
    a.keys('jaw', 'rotation', [(0, [42, 0, 0]), (0.4, [42, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.stunned', 1.2)
    a.wave('root', 'rotation', lambda p: [0, 0, 60 + sin(p, 10)])
    a.wave('jaw', 'rotation', lambda p: [20 + sin(p, 5), 0, 0])
    for i in range(SEGS):
        a.wave(f'seg{i}', 'rotation', lambda p, i=i: [0, sin(p, 3, -i * 0.1), 0])
    out.append(a)

    a = Anim(f'animation.{NAME}.bite', 0.35, loop=False)
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.1, [40, 0, 0]), (0.2, [-2, 0, 0]), (0.35, [0, 0, 0])])
    a.keys('head', 'position', [(0, [0, 0, 0]), (0.15, [0, 0, -3]), (0.35, [0, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 1.2, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (1.2, [0, 0, 180])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (1.2, [0, -4, 0])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (1.2, [30, 0, 0])])
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
