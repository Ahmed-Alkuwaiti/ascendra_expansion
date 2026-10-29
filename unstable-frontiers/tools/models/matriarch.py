"""The Chained Matriarch: the thing the Great Cage was built to hold. A colossal mantis-wasp queen with raptorial scythe
arms, a crown of bone spines and a swollen, glowing egg-sac abdomen under armoured plates. Iron shackles still bite into
her legs; the plates over the sac lift when she calls her brood, which is when she is most vulnerable.

Writes geo/entity/chained_matriarch.geo.json, animations/entity/chained_matriarch.animation.json and
textures/entity/chained_matriarch.png (+ _glowmask.png).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'chained_matriarch'

CHITIN = Material('chitin', (38, 52, 56), dark=(18, 26, 30), light=(76, 104, 104), seed=41, bands=5)
PLATE = Material('plate', (46, 62, 64), dark=(22, 30, 34), light=(96, 126, 118), seed=43, rust=(88, 150, 70))
SAC = Material('glow', (110, 200, 70), dark=(46, 96, 40), light=(196, 255, 120), seed=45, glow=True)
BONE = Material('bone', (222, 214, 190), dark=(150, 140, 116), seed=47)
BLADE = Material('bone', (196, 204, 196), dark=(110, 120, 116), seed=49)
EYE = Material('eye', (150, 255, 90), light=(240, 255, 210), glow=True, rim=False)
IRON = Material('iron', (90, 84, 82), dark=(50, 46, 46), light=(150, 96, 60), seed=51, rim=False)
MEMBRANE = Material('membrane', (70, 96, 84), dark=(34, 50, 44), light=(120, 150, 130), seed=53, alpha=190, rim=False)
LEG = Material('chitin', (32, 44, 48), dark=(16, 22, 26), light=(66, 90, 92), seed=55, bands=9)


def build():
    m = Model(NAME, 512, 256)
    root = m.bone('root', (0, 0, 0))
    body = m.bone('body', (0, 34, 0), root)
    body.cube((-12, 30, -16), (24, 18, 24), CHITIN)
    body.cube((-10, 48, -13), (20, 4, 18), PLATE)
    body.cube((-11, 27, -14), (22, 4, 20), PLATE)
    # the egg sac: a swollen glowing abdomen, its top armoured by plates that lift when she calls her brood
    abdomen = m.bone('abdomen', (0, 40, 8), body)
    abdomen.cube((-15, 26, 8), (30, 24, 26), SAC)
    abdomen.cube((-12, 28, 34), (24, 18, 10), SAC)
    abdomen.cube((-7, 31, 44), (14, 11, 7), CHITIN)
    abdomen.cube((-2, 33, 51), (4, 4, 8), BONE)                   # ovipositor
    for i, (z, w, y) in enumerate(((9, 32, 50), (19, 33, 50), (29, 30, 48), (37, 26, 46))):
        plate = m.bone(f'sac_plate{i}', (0, y, z + 4), abdomen)
        plate.cube((-w / 2, y - 2, z), (w, 4, 9), PLATE)
        plate.cube((-w / 2 - 1, y - 12, z), (2, 11, 9), PLATE)
        plate.cube((w / 2 - 1, y - 12, z), (2, 11, 9), PLATE)
    for side, s in ((-1, 'l'), (1, 'r')):
        wg = m.bone(f'wing_{s}', (6 * side, 50, 0), body, rotation=(0, 60 * side, -10 * side))
        o = (4, 49, -2) if side > 0 else mirror_x((4, 49, -2), (26, 2, 3))
        wg.cube(o, (26, 2, 3), BONE)
        o = (4, 49.5, 1) if side > 0 else mirror_x((4, 49.5, 1), (22, 0, 20))
        wg.cube(o, (22, 0, 20), MEMBRANE)
        o = (8, 49.4, 21) if side > 0 else mirror_x((8, 49.4, 21), (10, 0, 6))
        wg.cube(o, (10, 0, 6), MEMBRANE)
    neck = m.bone('neck', (0, 44, -16), body)
    neck.cube((-6, 40, -22), (12, 10, 8), CHITIN)
    head = m.bone('head', (0, 46, -22), neck)
    head.cube((-9, 40, -36), (18, 14, 14), CHITIN)
    head.cube((-10, 52, -35), (20, 3, 12), PLATE)
    for k, (ex, ey) in enumerate(((-8, 48), (5, 48), (-6, 44), (4, 44))):
        head.cube((ex, ey, -37), (3, 3, 1), EYE)
    crown = m.bone('crown', (0, 55, -28), head)
    for k, (x, hgt, tilt) in enumerate(((-8, 10, 0), (-4, 15, 0), (0, 19, 0), (4, 15, 0), (8, 10, 0))):
        crown.cube((x - 1.5, 55, -31 + abs(x) // 3), (3, hgt, 3), BONE)
        crown.cube((x - 1, 55 + hgt, -30 + abs(x) // 3), (2, 3, 2), BONE)
    for side, s in ((-1, 'l'), (1, 'r')):
        man = m.bone(f'mandible_{s}', (4 * side, 42, -35), head, rotation=(0, -15 * side, 0))
        o = (2, 39, -44) if side > 0 else mirror_x((2, 39, -44), (5, 4, 10))
        man.cube(o, (5, 4, 10), BONE)
        o = (-1, 39, -47) if side > 0 else mirror_x((-1, 39, -47), (5, 3, 4))
        man.cube(o, (5, 3, 4), BONE)
        # raptorial arms: shoulder, upper arm reaching forward, and the scythe folded up in front of the face
        arm = m.bone(f'arm_{s}', (12 * side, 44, -12), body, rotation=(-30, 0, 0))
        o = (10, 40, -32) if side > 0 else mirror_x((10, 40, -32), (6, 6, 22))
        arm.cube(o, (6, 6, 22), CHITIN)
        scy = m.bone(f'scythe_{s}', (13 * side, 43, -32), arm, rotation=(-90, 0, 0))
        o = (11, 41, -34) if side > 0 else mirror_x((11, 41, -34), (5, 5, 24))
        scy.cube(o, (5, 5, 24), CHITIN)
        o = (11.5, 37, -34) if side > 0 else mirror_x((11.5, 37, -34), (4, 4, 30))
        scy.cube(o, (4, 4, 30), BLADE)
        for k in range(4):
            o = (12, 34, -30 + k * 6) if side > 0 else mirror_x((12, 34, -30 + k * 6), (3, 3, 2))
            scy.cube(o, (3, 3, 2), BLADE)
        o = (11.5, 38, -40) if side > 0 else mirror_x((11.5, 38, -40), (4, 3, 7))
        scy.cube(o, (4, 3, 7), BLADE)                            # hooked tip
        # four walking legs with high knees, shackled at the ankle
        for k, z, splay in (('f', -6, -22), ('r', 14, 26)):
            leg = m.bone(f'leg_{k}{s}', (11 * side, 32, z), body, rotation=(0, -splay * side, -42 * side))
            o = (11, 30, z - 3) if side > 0 else mirror_x((11, 30, z - 3), (24, 6, 6))
            leg.cube(o, (24, 6, 6), LEG)
            shin = m.bone(f'shin_{k}{s}', (33 * side, 32, z), leg, rotation=(0, 0, 32 * side))
            o = (30, -9, z - 3) if side > 0 else mirror_x((30, -9, z - 3), (6, 42, 6))
            shin.cube(o, (6, 42, 6), LEG)
            o = (29, 2, z - 4) if side > 0 else mirror_x((29, 2, z - 4), (8, 5, 8))
            shin.cube(o, (8, 5, 8), IRON)                        # shackle
            o = (32, -4, z - 1) if side > 0 else mirror_x((32, -4, z - 1), (2, 6, 2))
            shin.cube(o, (2, 6, 2), IRON)                        # broken chain link
            o = (29, -10, z - 4) if side > 0 else mirror_x((29, -10, z - 4), (8, 2, 8))
            shin.cube(o, (8, 2, 8), BONE)
    return m


LEGS = ('leg_fl', 'leg_rl', 'leg_fr', 'leg_rr')


def animations():
    out = []
    a = Anim('animation.chained_matriarch.idle', 3.0)
    a.wave('abdomen', 'scale', lambda p: [1 + sin(p, 0.03), 1 + sin(p, 0.04), 1 + sin(p, 0.03)], steps=12)
    a.wave('body', 'position', lambda p: [0, sin(p, 0.6), 0])
    a.wave('head', 'rotation', lambda p: [sin(p, 3), sin(p, 8, 0.2), 0], steps=12)
    a.wave('mandible_l', 'rotation', lambda p: [0, sin(p * 3, 6), 0], steps=12)
    a.wave('mandible_r', 'rotation', lambda p: [0, -sin(p * 3, 6), 0], steps=12)
    a.wave('scythe_l', 'rotation', lambda p: [sin(p, 4), 0, 0])
    a.wave('scythe_r', 'rotation', lambda p: [sin(p, 4, 0.5), 0, 0])
    out.append(a)

    # while chained: she strains against the shackles, leaning away and hauling on each leg in turn
    a = Anim('animation.chained_matriarch.struggle', 2.4)
    a.wave('body', 'rotation', lambda p: [sin(p, 5), sin(p, 6, 0.25), sin(p, 7)], steps=12)
    for i, leg in enumerate(LEGS):
        sd = -1 if leg.endswith('l') else 1
        a.wave(leg, 'rotation', lambda p, i=i, sd=sd: [0, sin(p, 10, i * 0.25), sd * max(0.0, sin(p, 14, i * 0.25))], steps=12)
    a.wave('head', 'rotation', lambda p: [-8 + sin(p * 2, 6), sin(p, 14), 0], steps=12)
    a.wave('wing_l', 'rotation', lambda p: [0, 0, sin(p * 4, 8)], steps=16)
    a.wave('wing_r', 'rotation', lambda p: [0, 0, -sin(p * 4, 8)], steps=16)
    out.append(a)

    a = Anim('animation.chained_matriarch.walk', 1.4)
    for legs, ph in ((('leg_fl', 'leg_rr'), 0.0), (('leg_fr', 'leg_rl'), 0.5)):
        for leg in legs:
            sd = -1 if leg.endswith('l') else 1
            a.wave(leg, 'rotation', lambda p, ph=ph, sd=sd: [0, sin(p, 16, ph), sd * max(0.0, sin(p, 16, ph + 0.25))], steps=12)
    a.wave('body', 'position', lambda p: [0, sin(p * 2, 1.0), 0])
    a.wave('body', 'rotation', lambda p: [0, 0, sin(p, 3)])
    out.append(a)

    # scythe sweep: rears back with both scythes high (the tell), then slashes down and across in front of her
    a = Anim('animation.chained_matriarch.sweep_tell', 1.1, loop='hold')
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.5, [-14, 0, 0]), (1.1, [-16, 0, 0])])
    for s, sd in (('l', -1), ('r', 1)):
        a.keys(f'arm_{s}', 'rotation', [(0, [0, 0, 0]), (0.5, [-30, 0, sd * 22]), (1.1, [-36, 0, sd * 26])])
        a.keys(f'scythe_{s}', 'rotation', [(0, [0, 0, 0]), (0.5, [-25, 0, 0]), (1.1, [-30, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.5, [-15, 0, 0]), (1.1, [-15, 0, 0])])
    out.append(a)
    a = Anim('animation.chained_matriarch.sweep', 0.7, loop=False)
    a.keys('body', 'rotation', [(0, [-16, 0, 0]), (0.2, [14, 0, 0]), (0.7, [0, 0, 0])])
    for s, sd in (('l', -1), ('r', 1)):
        a.keys(f'arm_{s}', 'rotation', [(0, [-36, 0, sd * 26]), (0.18, [40, sd * 30, -sd * 10]), (0.7, [0, 0, 0])])
        a.keys(f'scythe_{s}', 'rotation', [(0, [-30, 0, 0]), (0.18, [85, 0, 0]), (0.7, [0, 0, 0])])
    out.append(a)

    # acid volley: the head snaps back and the abdomen clenches, then she spits three globs in an arc
    a = Anim('animation.chained_matriarch.spit_tell', 0.9, loop='hold')
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.5, [-30, 0, 0]), (0.9, [-34, 0, 0])])
    a.keys('neck', 'rotation', [(0, [0, 0, 0]), (0.5, [-12, 0, 0]), (0.9, [-14, 0, 0])])
    a.keys('abdomen', 'scale', [(0, [1, 1, 1]), (0.6, [0.9, 0.86, 0.94]), (0.9, [0.88, 0.84, 0.92])])
    a.keys('mandible_l', 'rotation', [(0, [0, 0, 0]), (0.5, [0, 30, 0]), (0.9, [0, 32, 0])])
    a.keys('mandible_r', 'rotation', [(0, [0, 0, 0]), (0.5, [0, -30, 0]), (0.9, [0, -32, 0])])
    out.append(a)
    a = Anim('animation.chained_matriarch.spit', 0.5, loop=False)
    a.keys('head', 'rotation', [(0, [-34, 0, 0]), (0.12, [18, 0, 0]), (0.5, [0, 0, 0])])
    a.keys('abdomen', 'scale', [(0, [0.88, 0.84, 0.92]), (0.12, [1.08, 1.1, 1.05]), (0.5, [1, 1, 1])])
    out.append(a)

    # brood call: the plates over the sac lift and the sac pulses: the weak point is open
    a = Anim('animation.chained_matriarch.brood', 3.0, loop=False)
    for i in range(4):
        a.keys(f'sac_plate{i}', 'position', [(0, [0, 0, 0]), (0.4 + i * 0.08, [0, 7 + i, 0]), (2.6, [0, 7 + i, 0]), (3.0, [0, 0, 0])])
        a.keys(f'sac_plate{i}', 'rotation', [(0, [0, 0, 0]), (0.5, [-12 + i * 6, 0, 0]), (2.6, [-12 + i * 6, 0, 0]), (3.0, [0, 0, 0])])
    for t in range(7):
        a.key('abdomen', 'scale', 0.4 + t * 0.35, [1.08 if t % 2 == 0 else 1.0, 1.12 if t % 2 == 0 else 1.0, 1.06 if t % 2 == 0 else 1.0])
    a.key('abdomen', 'scale', 0, [1, 1, 1])
    a.key('abdomen', 'scale', 3.0, [1, 1, 1])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.4, [-35, 0, 0]), (2.6, [-30, 0, 0]), (3.0, [0, 0, 0])])
    a.keys('wing_l', 'rotation', [(0, [0, 0, 0]), (0.4, [0, 0, 35]), (2.6, [0, 0, 30]), (3.0, [0, 0, 0])])
    a.keys('wing_r', 'rotation', [(0, [0, 0, 0]), (0.4, [0, 0, -35]), (2.6, [0, 0, -30]), (3.0, [0, 0, 0])])
    out.append(a)

    # unchained only: a crouch (the tell) and a leap that lands in a shockwave
    a = Anim('animation.chained_matriarch.leap_tell', 0.9, loop='hold')
    a.keys('body', 'position', [(0, [0, 0, 0]), (0.6, [0, -8, 0]), (0.9, [0, -9, 0])])
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.6, [10, 0, 0]), (0.9, [12, 0, 0])])
    for leg in LEGS:
        sd = -1 if leg.endswith('l') else 1
        a.keys(leg, 'rotation', [(0, [0, 0, 0]), (0.6, [0, 0, sd * 16]), (0.9, [0, 0, sd * 18])])
    a.keys('wing_l', 'rotation', [(0, [0, 0, 0]), (0.9, [0, 0, 40])])
    a.keys('wing_r', 'rotation', [(0, [0, 0, 0]), (0.9, [0, 0, -40])])
    out.append(a)
    a = Anim('animation.chained_matriarch.leap', 1.0, loop=False)
    a.keys('body', 'rotation', [(0, [12, 0, 0]), (0.3, [-20, 0, 0]), (0.8, [10, 0, 0]), (1.0, [0, 0, 0])])
    for leg in LEGS:
        sd = -1 if leg.endswith('l') else 1
        a.keys(leg, 'rotation', [(0, [0, 0, sd * 18]), (0.3, [0, 0, -sd * 22]), (0.85, [0, 0, sd * 10]), (1.0, [0, 0, 0])])
    for w, sd in (('wing_l', 1), ('wing_r', -1)):
        a.keys(w, 'rotation', [(0, [0, 0, sd * 40]), (0.15, [0, 0, sd * 70]), (0.3, [0, 0, -sd * 10]), (0.45, [0, 0, sd * 70]),
                               (0.7, [0, 0, 0])])
    out.append(a)

    a = Anim('animation.chained_matriarch.death', 2.5, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (1.2, [12, 0, 0]), (2.5, [0, 0, 70])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (2.5, [0, 10, 0])])
    for leg in LEGS:
        a.keys(leg, 'rotation', [(0, [0, 0, 0]), (2.0, [0, 0, -30]), (2.5, [0, 0, -35])])
    for s in ('l', 'r'):
        a.keys(f'scythe_{s}', 'rotation', [(0, [0, 0, 0]), (1.5, [50, 0, 0])])
    a.keys('abdomen', 'scale', [(0, [1, 1, 1]), (2.5, [0.85, 0.7, 0.85])])
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
