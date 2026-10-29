"""The Eclipse Leviathan: what the observatory was built to watch, and what came through when the rift engine failed.
A vast ray of the void with wings full of stars, an eclipse burning on its back (a black disc in a ring of fire), a whip
of a tail and, under its belly, a core it guards with armoured plates. Original design for Unstable Frontiers.

Writes geo/entity/eclipse_leviathan.geo.json, animations/entity/eclipse_leviathan.animation.json and its texture.
The renderer scales it x2: about 14 blocks from wingtip to wingtip in game.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'eclipse_leviathan'

HIDE = Material('void', (22, 22, 46), dark=(8, 8, 20), light=(52, 56, 100), seed=301)
HIDE.stars = 0.018
WING = Material('void', (40, 26, 84), dark=(14, 8, 36), light=(86, 70, 150), seed=303, rim=False)
WING.stars = 0.03
EDGE = Material('chitin', (70, 70, 110), dark=(30, 30, 56), light=(130, 130, 180), seed=305)
BELLY = Material('plate', (140, 136, 170), dark=(80, 76, 110), light=(196, 192, 220), seed=307, rust=None)
CORONA = Material('glow', (255, 200, 90), dark=(230, 120, 40), light=(255, 250, 210), seed=309, glow=True)
DISC = Material('chitin', (6, 6, 10), dark=(2, 2, 4), light=(20, 18, 30), seed=311, rim=False)
EYE = Material('eye', (120, 240, 255), light=(240, 255, 255), glow=True, rim=False)
CORE = Material('glow', (160, 230, 255), dark=(60, 120, 220), light=(250, 255, 255), seed=313, glow=True)
TENDRIL = Material('glow', (110, 70, 200), dark=(40, 20, 90), light=(180, 140, 255), seed=315, glow=True)


def build():
    m = Model(NAME, 512, 256)
    root = m.bone('root', (0, 0, 0))
    body = m.bone('body', (0, 16, 0), root)
    body.cube((-14, 11, -20), (28, 9, 40), HIDE)
    body.cube((-10, 20, -16), (20, 2, 32), HIDE)
    body.cube((-3, 22, -14), (6, 3, 30), EDGE)                    # dorsal ridge
    for z in (-10, -2, 6):
        body.cube((-1.5, 25, z), (3, 3, 4), EDGE)
    # belly: the core and the plates over it
    body.cube((-12, 9, -16), (24, 2, 32), BELLY)
    core = m.bone('core', (0, 9, 0), body)
    core.cube((-5, 7.5, -9), (10, 2, 18), CORE)
    for side, s in ((-1, 'l'), (1, 'r')):
        plate = m.bone(f'plate_{s}', (side * 5, 8, 0), body)
        o = (0, 6.5, -10) if side > 0 else mirror_x((0, 6.5, -10), (6.5, 2, 20))
        plate.cube(o, (6.5, 2, 20), BELLY)
    # head and mouth
    head = m.bone('head', (0, 15, -20), body)
    head.cube((-15, 11, -31), (30, 8, 11), HIDE)
    head.cube((-11, 18, -29), (22, 3, 9), HIDE)
    for x in (-9, -5, 4, 8):
        head.cube((x, 17.5, -31.5), (2, 2, 1), EYE)
    jaw = m.bone('jaw', (0, 11, -22), head)
    jaw.cube((-13, 8, -32), (26, 3, 11), BELLY)
    jaw.cube((-11, 10.5, -31.5), (22, 1, 1), EDGE)                # teeth line
    for side, s in ((-1, 'l'), (1, 'r')):
        horn = m.bone(f'horn_{s}', (side * 13, 14, -30), head, rotation=(10, side * 8, 0))
        o = (11, 11, -44) if side > 0 else mirror_x((11, 11, -44), (5, 6, 14))
        horn.cube(o, (5, 6, 14), EDGE)
        o = (12, 12, -50) if side > 0 else mirror_x((12, 12, -50), (3, 4, 6))
        horn.cube(o, (3, 4, 6), EDGE)
    # wings: inner, middle and tip segments, a ridged leading edge, starry membranes
    for side, s in ((-1, 'l'), (1, 'r')):
        def ox(x0, w):
            return x0 if side > 0 else -x0 - w
        w1 = m.bone(f'wing_{s}', (side * 14, 16, -8), body)
        w1.cube((ox(14, 26), 15, -14), (26, 2, 30), WING)
        w1.cube((ox(14, 26), 15.5, -17), (26, 3, 3), EDGE)
        w1.cube((ox(14, 26), 15, 16), (26, 1, 4), WING)
        w1.cube((ox(14, 18), 15, 20), (18, 1, 4), WING)               # trailing edge taper
        w1.cube((ox(14, 10), 15, 24), (10, 1, 3), WING)
        w2 = m.bone(f'wing_{s}_mid', (side * 40, 16, -8), w1, rotation=(0, -side * 14, 0))
        w2.cube((ox(40, 24), 15.5, -13), (24, 1.5, 24), WING)
        w2.cube((ox(40, 24), 15.5, -16), (24, 2.5, 3), EDGE)
        w2.cube((ox(40, 14), 15.75, 11), (14, 1, 4), WING)
        w3 = m.bone(f'wing_{s}_tip', (side * 64, 16, -8), w2, rotation=(0, -side * 16, 0))
        w3.cube((ox(64, 20), 15.75, -12), (20, 1, 14), WING)
        w3.cube((ox(64, 10), 15.75, 2), (10, 1, 4), WING)
        w3.cube((ox(64, 22), 15.75, -14.5), (22, 2, 2.5), EDGE)
        w3.cube((ox(82, 6), 15.25, -16), (6, 2, 4), CORONA)        # glowing wingtip
        # tendrils from under the wing's trailing edge
        for k, (x, z) in enumerate(((22, 12), (34, 8))):
            t1 = m.bone(f'tendril_{s}{k}', (side * x, 15, z), w1)
            t1.cube((ox(x - 1, 2), 3, z - 1), (2, 12, 2), TENDRIL)
            t2 = m.bone(f'tendril_{s}{k}_end', (side * x, 3, z), t1)
            t2.cube((ox(x - 0.75, 1.5), -9, z - 0.75), (1.5, 12, 1.5), TENDRIL)
    # tail
    prev = body
    z, wdt = 20, 8.0
    for i in range(4):
        t = m.bone(f'tail{i + 1}', (0, 15.5, z), prev)
        t.cube((-wdt / 2, 15.5 - wdt / 4, z), (wdt, wdt / 2, 14), HIDE)
        t.cube((-0.75, 15.5 + wdt / 4, z + 2), (1.5, 1.5, 9), EDGE)
        prev, z, wdt = t, z + 14, wdt * 0.75
    sting = m.bone('stinger', (0, 15.5, z), prev)
    sting.cube((-5, 15, z), (10, 1, 6), EDGE)
    sting.cube((-1.25, 14.75, z + 3), (2.5, 1.5, 10), CORONA)
    # the eclipse on its back: a black disc in a burning ring, standing upright behind the head
    halo = m.bone('halo', (0, 40, 2), body)
    for r, wdt in ((5, 12), (8, 10), (10, 6)):
        halo.cube((-r, 40 - wdt / 2 * 0 - r * 0 - wdt / 2, 1.5), (2 * r, wdt, 1), DISC)
    halo.cube((-9, 33, 1.5), (18, 14, 1), DISC)
    halo.cube((-6, 30, 1.5), (12, 20, 1), DISC)
    corona = m.bone('corona', (0, 40, 2), halo)
    segs, R = 20, 13.5
    for i in range(segs):
        a = 2 * math.pi * i / segs
        cx, cy = R * math.cos(a), 40 + R * math.sin(a)
        ln = 2 * math.pi * R / segs + 0.6
        roll = math.degrees(a) + 90
        corona.cube((cx - ln / 2, cy - 1, 1), (ln, 2, 2), CORONA, rotation=(0, 0, roll), pivot=(cx, cy, 2))
        if i % 2 == 0:
            fl = 3 + (i % 4)
            fx, fy = (R + fl / 2) * math.cos(a), 40 + (R + fl / 2) * math.sin(a)
            corona.cube((fx - 0.75, fy - fl / 2, 1.5), (1.5, fl, 1), CORONA, rotation=(0, 0, math.degrees(a) - 90), pivot=(fx, fy, 2))
    strut = m.bone('strut', (0, 24, 2), body)
    strut.cube((-1.5, 24, 1), (3, 6, 3), EDGE)
    return m


WINGS = ('wing_l', 'wing_r')
TENDRILS = [f'tendril_{s}{k}' for s in 'lr' for k in (0, 1)]


def swim(a, amp=22, lag=0.12, tail_amp=10):
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.wave(w, 'rotation', lambda p, sd=sd: [0, 0, sd * sin(p, amp)], steps=16)
        a.wave(w + '_mid', 'rotation', lambda p, sd=sd: [0, 0, sd * sin(p, amp * 0.8, -lag)], steps=16)
        a.wave(w + '_tip', 'rotation', lambda p, sd=sd: [0, 0, sd * sin(p, amp * 0.7, -2 * lag)], steps=16)
    for i in range(4):
        a.wave(f'tail{i + 1}', 'rotation', lambda p, i=i: [sin(p, tail_amp * (0.6 + 0.2 * i), 0.15 * i), sin(p, 6, 0.1 * i), 0], steps=16)
    for t in TENDRILS:
        a.wave(t, 'rotation', lambda p, t=t: [sin(p, 14, 0.2 + 0.1 * len(t)), 0, sin(p, 8, 0.3)], steps=12)
        a.wave(t + '_end', 'rotation', lambda p, t=t: [sin(p, 18, 0.35), 0, 0], steps=12)
    a.wave('body', 'position', lambda p: [0, sin(p, 2.0, 0.25), 0], steps=16)


def animations():
    out = []
    a = Anim(f'animation.{NAME}.swim', 3.0)
    swim(a)
    a.wave('corona', 'rotation', lambda p: [0, 0, 120 * p], steps=12)
    out.append(a)

    # Eclipse Beam: it rears, the corona flares and spins, the mouth opens (1.5 s), then the beam sweeps
    a = Anim(f'animation.{NAME}.beam_tell', 1.5, loop='hold')
    swim(a, 6, tail_amp=4)
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.8, [-16, 0, 0]), (1.5, [-18, 0, 0])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (1.0, [32, 0, 0]), (1.5, [35, 0, 0])])
    a.keys('halo', 'scale', [(0, [1, 1, 1]), (1.2, [1.35, 1.35, 1]), (1.5, [1.4, 1.4, 1])])
    a.keys('corona', 'rotation', [(0, [0, 0, 0]), (1.5, [0, 0, 540])])
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (0.8, [0, 0, -sd * 18]), (1.5, [0, 0, -sd * 20])])
    out.append(a)

    a = Anim(f'animation.{NAME}.beam', 1.0)
    swim(a, 5, tail_amp=3)
    a.wave('body', 'rotation', lambda p: [-18, sin(p, 2), 0])
    a.wave('jaw', 'rotation', lambda p: [35, 0, 0], steps=4)
    a.wave('halo', 'scale', lambda p: [1.4 + sin(p * 2, 0.06), 1.4 + sin(p * 2, 0.06), 1])
    a.wave('corona', 'rotation', lambda p: [0, 0, 720 * p], steps=12)
    out.append(a)

    # Gravity Well: the wings sweep forward and curl, the tendrils lift
    a = Anim(f'animation.{NAME}.well_tell', 1.25, loop='hold')
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (0.8, [0, sd * 28, sd * 22]), (1.25, [0, sd * 30, sd * 24])])
        a.keys(w + '_tip', 'rotation', [(0, [0, 0, 0]), (0.8, [0, 0, sd * 40])])
    for t in TENDRILS:
        a.keys(t, 'rotation', [(0, [0, 0, 0]), (1.0, [-70, 0, 0])])
    a.keys('core', 'scale', [(0, [1, 1, 1]), (1.25, [1.3, 1.6, 1.3])])
    out.append(a)

    # the low pass: wings swept back, nose down, tail straight
    a = Anim(f'animation.{NAME}.pass', 1.0)
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.wave(w, 'rotation', lambda p, sd=sd: [0, -sd * 24, sd * sin(p, 6)], steps=8)
        a.wave(w + '_tip', 'rotation', lambda p, sd=sd: [0, -sd * 18, sd * sin(p, 10, -0.1)], steps=8)
    a.wave('body', 'rotation', lambda p: [10, 0, sin(p, 3)])
    for i in range(4):
        a.wave(f'tail{i + 1}', 'rotation', lambda p, i=i: [0, sin(p, 4, 0.1 * i), 0])
    out.append(a)

    a = Anim(f'animation.{NAME}.summon', 1.5, loop='hold')
    swim(a, 10)
    a.keys('halo', 'scale', [(0, [1, 1, 1]), (0.5, [1.25, 1.25, 1]), (1.0, [0.95, 0.95, 1]), (1.5, [1.2, 1.2, 1])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.5, [20, 0, 0]), (1.5, [10, 0, 0])])
    out.append(a)

    # the roar at each turn of the fight
    a = Anim(f'animation.{NAME}.roar', 2.0, loop=False)
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.4, [42, 0, 0]), (1.6, [42, 0, 0]), (2.0, [0, 0, 0])])
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.4, [-24, 0, 0]), (1.6, [-24, 0, 0]), (2.0, [0, 0, 0])])
    a.keys('halo', 'scale', [(0, [1, 1, 1]), (0.5, [1.6, 1.6, 1]), (1.5, [1.5, 1.5, 1]), (2.0, [1, 1, 1])])
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (0.5, [0, 0, -sd * 40]), (1.6, [0, 0, -sd * 38]), (2.0, [0, 0, 0])])
    out.append(a)

    # exposed: down on the arena, wings slumped, belly plates open over the core
    a = Anim(f'animation.{NAME}.exposed', 2.0)
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.wave(w, 'rotation', lambda p, sd=sd: [0, 0, sd * (-14 + sin(p, 3))], steps=8)
        a.wave(w + '_mid', 'rotation', lambda p, sd=sd: [0, 0, sd * -10], steps=4)
        a.wave(w + '_tip', 'rotation', lambda p, sd=sd: [0, 0, sd * -12], steps=4)
    a.wave('plate_l', 'position', lambda p: [-7, 0, 0], steps=4)
    a.wave('plate_r', 'position', lambda p: [7, 0, 0], steps=4)
    a.wave('core', 'scale', lambda p: [1.15 + sin(p * 2, 0.12), 1.4 + sin(p * 2, 0.25), 1.1], steps=12)
    a.wave('body', 'rotation', lambda p: [6, 0, sin(p, 3)])
    a.wave('halo', 'rotation', lambda p: [30, 0, sin(p, 4)])
    a.wave('jaw', 'rotation', lambda p: [12 + sin(p, 6), 0, 0])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 3.0, loop='hold')
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (3.0, [0, sd * 50, sd * 70])])
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (3.0, [30, 0, 60])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (3.0, [0, -20, 0])])
    a.keys('halo', 'scale', [(0, [1, 1, 1]), (1.0, [1.8, 1.8, 1]), (3.0, [0.1, 0.1, 1])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.5, [40, 0, 0]), (3.0, [25, 0, 0])])
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
