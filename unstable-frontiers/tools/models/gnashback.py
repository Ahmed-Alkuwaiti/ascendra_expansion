"""The Gnashback: a giant beetle of the Gnashwood whose shell grew around the bars of an old cage. Rusted iron ribs arch
over its back; it charges head-down behind a bone horn and crushing mandibles.

Writes geo/entity/gnashback.geo.json, animations/entity/gnashback.animation.json and textures/entity/gnashback.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, ease, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')

CHITIN = Material('chitin', (74, 52, 46), dark=(40, 27, 26), light=(122, 86, 66), seed=3, bands=4)
SHELL = Material('plate', (98, 58, 38), dark=(54, 32, 24), light=(170, 120, 82), seed=5)
HEAD = Material('chitin', (58, 40, 38), dark=(30, 20, 20), light=(104, 72, 60), seed=7)
BELLY = Material('chitin', (150, 124, 96), dark=(110, 88, 66), light=(186, 160, 126), seed=9, bands=3)
BONE = Material('bone', (214, 200, 168), dark=(150, 136, 108), seed=11)
IRON = Material('iron', (112, 92, 84), dark=(70, 56, 52), light=(176, 110, 70), seed=13, rim=False)
EYE = Material('eye', (255, 170, 40), light=(255, 240, 180), glow=True, rim=False)
LEG = Material('chitin', (64, 44, 40), dark=(34, 24, 22), light=(110, 76, 62), seed=17, bands=8)


def build():
    m = Model('gnashback', 256, 256)
    root = m.bone('root', (0, 0, 0))
    body = m.bone('body', (0, 17, 0), root)
    body.cube((-10, 12, -12), (20, 13, 16), CHITIN)
    body.cube((-8, 25, -10), (16, 2, 12), CHITIN)
    body.cube((-9, 10, -11), (18, 3, 14), BELLY)
    abdomen = m.bone('abdomen', (0, 18, 4), body)
    abdomen.cube((-13, 10, 4), (26, 14, 25), CHITIN)
    abdomen.cube((-12, 8, 6), (24, 3, 21), BELLY)
    abdomen.cube((-9, 12, 29), (18, 10, 5), CHITIN)
    # split elytra over a stepped dome; they lift apart when it is about to charge
    for side, name in ((-1, 'elytra_l'), (1, 'elytra_r')):
        el = m.bone(name, (2 * side, 27, 4), abdomen)
        o = (1, 23, 3) if side > 0 else mirror_x((1, 23, 3), (14, 5, 29))
        el.cube(o, (14, 5, 29), SHELL)
        o = (1, 28, 5) if side > 0 else mirror_x((1, 28, 5), (11, 3, 25))
        el.cube(o, (11, 3, 25), SHELL)
        o = (1, 31, 8) if side > 0 else mirror_x((1, 31, 8), (7, 2, 19))
        el.cube(o, (7, 2, 19), SHELL)
    spine = m.bone('spine', (0, 32, 4), abdomen)
    spine.cube((-1.5, 31, 4), (3, 3, 27), IRON)
    # three rusted cage ribs arching over the back, shorter toward the tail
    for i, (z, top) in enumerate(((8, 46), (17, 43), (26, 39))):
        rib = m.bone(f'rib{i}', (0, 33, z), spine)
        rib.cube((-11, 31, z), (2, top - 31, 2), IRON)
        rib.cube((9, 31, z), (2, top - 31, 2), IRON)
        rib.cube((-11, top, z), (22, 2, 2), IRON)
        rib.cube((-1, top + 2, z), (2, 4, 2), IRON)
    head = m.bone('head', (0, 18, -12), body)
    head.cube((-8, 10, -24), (16, 11, 12), HEAD)
    head.cube((-9, 18, -25), (18, 5, 10), SHELL)               # brow plate
    head.cube((-8, 18, -26), (3, 3, 1), EYE)
    head.cube((5, 18, -26), (3, 3, 1), EYE)
    head.cube((-5, 10, -26), (10, 4, 2), BELLY)                # mouthparts
    horn = m.bone('horn', (0, 22, -25), head, rotation=(-20, 0, 0))
    horn.cube((-2, 20, -33), (4, 4, 9), BONE)
    horn.cube((-1.5, 21, -39), (3, 3, 6), BONE)
    horn.cube((-1, 22, -43), (2, 2, 4), BONE)
    for side, name in ((-1, 'mandible_l'), (1, 'mandible_r')):
        man = m.bone(name, (5 * side, 13, -24), head, rotation=(0, -12 * side, 0))
        o = (3, 11, -33) if side > 0 else mirror_x((3, 11, -33), (4, 4, 9))
        man.cube(o, (4, 4, 9), BONE)
        o = (0, 11, -37) if side > 0 else mirror_x((0, 11, -37), (5, 3, 4))
        man.cube(o, (5, 3, 4), BONE)
        o = (-1, 11.5, -39) if side > 0 else mirror_x((-1, 11.5, -39), (3, 2, 3))
        man.cube(o, (3, 2, 3), BONE)
    # six legs: the femur rises outward from the hip to a high knee, the tibia drops to the ground
    for side in (-1, 1):
        s = 'l' if side < 0 else 'r'
        for k, z, splay in (('f', -9, -18), ('m', 0, 0), ('r', 11, 18)):
            leg = m.bone(f'leg_{k}{s}', (9 * side, 18, z), body, rotation=(0, -splay * side, -40 * side))
            o = (9, 16, z - 2) if side > 0 else mirror_x((9, 16, z - 2), (14, 4, 4))
            leg.cube(o, (14, 4, 4), LEG)
            shin = m.bone(f'shin_{k}{s}', (22 * side, 18, z), leg, rotation=(0, 0, 30 * side))
            o = (20, -7, z - 2) if side > 0 else mirror_x((20, -7, z - 2), (4, 25, 4))
            shin.cube(o, (4, 25, 4), LEG)
            o = (19, -8, z - 3) if side > 0 else mirror_x((19, -8, z - 3), (6, 2, 6))
            shin.cube(o, (6, 2, 6), BONE)
    return m


A_TRIPOD = ('leg_fl', 'leg_mr', 'leg_rl')
B_TRIPOD = ('leg_fr', 'leg_ml', 'leg_rr')


def gait(a, amp_swing, amp_lift):
    for legs, phase in ((A_TRIPOD, 0.0), (B_TRIPOD, 0.5)):
        for leg in legs:
            side = -1 if leg.endswith('l') else 1
            a.wave(leg, 'rotation', lambda p, ph=phase, sd=side: [0, sin(p, amp_swing, ph), sd * max(0.0, sin(p, amp_lift, ph + 0.25))])


def animations():
    out = []
    a = Anim('animation.gnashback.idle', 2.0)
    a.wave('body', 'position', lambda p: [0, sin(p, 0.4), 0])
    a.wave('mandible_l', 'rotation', lambda p: [0, sin(p * 2, 6), 0])
    a.wave('mandible_r', 'rotation', lambda p: [0, -sin(p * 2, 6), 0])
    a.wave('head', 'rotation', lambda p: [sin(p, 2), sin(p, 4, 0.2), 0])
    out.append(a)

    a = Anim('animation.gnashback.walk', 1.0)
    gait(a, 18, 14)
    a.wave('body', 'position', lambda p: [0, sin(p * 2, 0.5), 0])
    a.wave('head', 'rotation', lambda p: [0, sin(p, 4), 0])
    out.append(a)

    a = Anim('animation.gnashback.charge', 0.5)
    gait(a, 28, 22)
    a.wave('body', 'rotation', lambda p: [8, 0, sin(p, 3)])
    a.wave('head', 'rotation', lambda p: [14, 0, 0])
    a.wave('mandible_l', 'rotation', lambda p: [0, 14, 0])
    a.wave('mandible_r', 'rotation', lambda p: [0, -14, 0])
    a.wave('elytra_l', 'rotation', lambda p: [0, 0, 14])
    a.wave('elytra_r', 'rotation', lambda p: [0, 0, -14])
    out.append(a)

    # the tell before a charge: lowers its head, scrapes the ground twice, rocks back on its hind legs
    a = Anim('animation.gnashback.charge_tell', 1.25, loop='hold')
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.3, [-8, 0, 0]), (1.0, [-6, 0, 0]), (1.25, [10, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.3, [16, 0, 0]), (1.25, [18, 0, 0])])
    for t0 in (0.3, 0.75):
        a.keys('leg_fl', 'rotation', [(t0, [0, -25, -10]), (t0 + 0.2, [0, 20, 12]), (t0 + 0.45, [0, -25, -10])])
    a.keys('mandible_l', 'rotation', [(0, [0, 0, 0]), (0.5, [0, 22, 0]), (1.25, [0, 22, 0])])
    a.keys('mandible_r', 'rotation', [(0, [0, 0, 0]), (0.5, [0, -22, 0]), (1.25, [0, -22, 0])])
    # the elytra crack open: the readable warning from above and behind
    a.keys('elytra_l', 'rotation', [(0, [0, 0, 0]), (0.4, [0, 0, 16]), (1.25, [0, 0, 20])])
    a.keys('elytra_r', 'rotation', [(0, [0, 0, 0]), (0.4, [0, 0, -16]), (1.25, [0, 0, -20])])
    out.append(a)

    a = Anim('animation.gnashback.bite', 0.6, loop=False)
    a.keys('head', 'position', [(0, [0, 0, 0]), (0.2, [0, -1, -3]), (0.6, [0, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.2, [10, 0, 0]), (0.6, [0, 0, 0])])
    a.keys('mandible_l', 'rotation', [(0, [0, 0, 0]), (0.15, [0, 30, 0]), (0.25, [0, -6, 0]), (0.6, [0, 0, 0])])
    a.keys('mandible_r', 'rotation', [(0, [0, 0, 0]), (0.15, [0, -30, 0]), (0.25, [0, 6, 0]), (0.6, [0, 0, 0])])
    out.append(a)

    # stunned after ramming a wall: legs splay, the body sags and sways, the head lolls
    a = Anim('animation.gnashback.stunned', 1.5)
    a.wave('body', 'position', lambda p: [0, -2.5, 0])
    a.wave('body', 'rotation', lambda p: [-4, 0, sin(p, 8)])
    a.wave('head', 'rotation', lambda p: [22, sin(p, 12, 0.25), sin(p, 10)])
    for leg in A_TRIPOD + B_TRIPOD:
        side = -1 if leg.endswith('l') else 1
        a.wave(leg, 'rotation', lambda p, sd=side: [0, 0, sd * 22])
    out.append(a)

    a = Anim('animation.gnashback.death', 1.6, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (1.0, [0, 0, 92]), (1.6, [0, 0, 90])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (1.0, [0, 6, 0]), (1.6, [0, 4, 0])])
    for leg in A_TRIPOD + B_TRIPOD:
        a.keys(leg, 'rotation', [(0, [0, 0, 0]), (0.8, [0, 0, -30]), (1.6, [0, 0, -40])])
    out.append(a)
    return out


def write():
    m = build()
    for d in ('geo/entity', 'animations/entity', 'textures/entity'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    m.save(os.path.join(OUT, 'geo/entity/gnashback.geo.json'))
    paint(m, os.path.join(OUT, 'textures/entity/gnashback.png'))
    anims = animations()
    save(anims, os.path.join(OUT, 'animations/entity/gnashback.animation.json'))
    return m, anims


if __name__ == '__main__':
    write()
    print('gnashback written')
