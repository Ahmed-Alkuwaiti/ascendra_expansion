"""The Shrikewing: the frontier's sky hunter. An ash-boned raptor-insect with two pairs of bruised membrane wings, a hooked
beak and a barbed tail; like a shrike it impales what it kills on spikes, which is where the impaled carcasses come from.

Writes geo/entity/shrikewing.geo.json, animations/entity/shrikewing.animation.json and textures/entity/shrikewing.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model, mirror_x
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')

ASH = Material('chitin', (186, 178, 164), dark=(108, 100, 96), light=(226, 220, 206), seed=21, bands=4)
BAND = Material('chitin', (58, 54, 66), dark=(30, 28, 36), light=(96, 90, 108), seed=23)
BEAK = Material('bone', (72, 62, 60), dark=(40, 34, 34), seed=25)
BONE = Material('bone', (220, 212, 192), dark=(150, 140, 124), seed=27)
MEMBRANE = Material('membrane', (118, 74, 128), dark=(62, 36, 74), light=(160, 110, 168), seed=29, alpha=215, rim=False)
MEMBRANE2 = Material('membrane', (96, 62, 112), dark=(54, 30, 66), light=(140, 96, 150), seed=31, alpha=205, rim=False)
EYE = Material('eye', (255, 64, 48), light=(255, 210, 190), glow=True, rim=False)


def wing(m, side, name, pivot, length, chord, z0, outer_len, outer_chord, parent):
    """A wing: a bony leading edge with a membrane behind it, and an outer segment that folds and lags in the beat."""
    px, py, pz = pivot
    wb = m.bone(name, pivot, parent)
    if side > 0:
        x0 = px
    else:
        x0 = -px - length
        x0 = -(px + length) if False else px - length
    o = (px, py - 1, z0) if side > 0 else (px - length, py - 1, z0)
    wb.cube(o, (length, 2, 2), BONE)
    o = (px, py - 0.5, z0 + 2) if side > 0 else (px - length, py - 0.5, z0 + 2)
    wb.cube(o, (length, 0, chord), MEMBRANE)
    for k in range(0, int(length) - 4, 6):
        o = (px + k + 1, py - 0.6, z0 + 2 + chord) if side > 0 else (px - k - 5, py - 0.6, z0 + 2 + chord)
        wb.cube(o, (4, 0, 3), MEMBRANE2)
    tip_x = px + length * side
    ob = m.bone(name + '_outer', (tip_x, py, pz), wb)
    o = (tip_x, py - 1, z0) if side > 0 else (tip_x - outer_len, py - 1, z0)
    ob.cube(o, (outer_len, 1.5, 1.5), BONE)
    o = (tip_x, py - 0.5, z0 + 1.5) if side > 0 else (tip_x - outer_len, py - 0.5, z0 + 1.5)
    ob.cube(o, (outer_len, 0, outer_chord), MEMBRANE)
    for k in range(0, int(outer_len) - 6, 7):
        o = (tip_x + k + 1, py - 0.6, z0 + 1.5 + outer_chord) if side > 0 else (tip_x - k - 5, py - 0.6, z0 + 1.5 + outer_chord)
        ob.cube(o, (4, 0, 3), MEMBRANE2)
    o = (tip_x + outer_len - 4, py - 1, z0 - 1) if side > 0 else (tip_x - outer_len, py - 1, z0 - 1)
    ob.cube(o, (4, 2, 2), BEAK)                                   # the hooked claw at the wing tip
    return wb, ob


def build():
    m = Model('shrikewing', 256, 128)
    root = m.bone('root', (0, 0, 0))
    body = m.bone('body', (0, 16, 0), root)
    body.cube((-5, 12, -9), (10, 9, 20), ASH)
    body.cube((-4, 9, -8), (8, 4, 12), BAND)                      # keel
    body.cube((-5.5, 20, -7), (11, 2, 4), BAND)
    body.cube((-5.5, 20, 1), (11, 2, 4), BAND)
    body.cube((-2, 21, -6), (4, 3, 12), BONE)                     # dorsal ridge
    neck = m.bone('neck', (0, 18, -9), body)
    neck.cube((-3.5, 14, -16), (7, 7, 8), ASH)
    head = m.bone('head', (0, 18, -16), neck)
    head.cube((-4.5, 13, -25), (9, 8, 10), BONE)
    head.cube((-2.5, 14, -33), (5, 5, 9), BEAK)
    head.cube((-2, 10, -35), (4, 6, 3), BEAK)                     # the hook
    head.cube((-5, 17, -22), (1, 2, 3), EYE)
    head.cube((4, 17, -22), (1, 2, 3), EYE)
    crest = m.bone('crest', (0, 21, -16), head, rotation=(-35, 0, 0))
    crest.cube((-1, 20, -18), (2, 6, 3), BAND)
    crest.cube((-0.5, 25, -18), (1, 3, 2), BONE)
    jaw = m.bone('jaw', (0, 14, -23), head)
    jaw.cube((-2.5, 12, -31), (5, 2, 8), BEAK)
    for side, s in ((-1, 'l'), (1, 'r')):
        wing(m, side, f'wing_{s}', (5 * side, 20, -5), 22, 15, -7, 22, 12, body)
        wing(m, side, f'hindwing_{s}', (5 * side, 19, 5), 16, 11, 4, 12, 8, body)
        leg = m.bone(f'leg_{s}', (3 * side, 12, 0), body, rotation=(30, 0, 0))
        o = (2, 5, -1) if side > 0 else mirror_x((2, 5, -1), (2, 8, 2))
        leg.cube(o, (2, 8, 2), BAND)
        o = (1, 4, -3) if side > 0 else mirror_x((1, 4, -3), (4, 2, 4))
        leg.cube(o, (4, 2, 4), BEAK)
    tail = m.bone('tail', (0, 17, 11), body)
    tail.cube((-2.5, 14.5, 10), (5, 5, 10), ASH)
    tail2 = m.bone('tail2', (0, 17, 20), tail)
    tail2.cube((-1.5, 15.5, 20), (3, 3, 10), BAND)
    barb = m.bone('barb', (0, 17, 30), tail2)
    barb.cube((-3, 15.5, 30), (6, 3, 4), BONE)
    barb.cube((-1, 16, 34), (2, 2, 7), BONE)
    barb.cube((-0.5, 18, 32), (1, 4, 1), BONE)
    return m


WINGS = ('wing_l', 'wing_r', 'hindwing_l', 'hindwing_r')


def flap(a, amp, outer, hind_phase=0.22, amp_hind=None):
    amp_hind = amp_hind or amp * 0.8
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        ph = hind_phase if w.startswith('hind') else 0.0
        am = amp_hind if w.startswith('hind') else amp
        a.wave(w, 'rotation', lambda p, sd=sd, ph=ph, am=am: [0, 0, sd * sin(p, am, ph)], steps=12)
        a.wave(w + '_outer', 'rotation', lambda p, sd=sd, ph=ph: [0, 0, sd * sin(p, outer, ph - 0.12)], steps=12)


def animations():
    out = []
    a = Anim('animation.shrikewing.fly', 0.8)
    flap(a, 34, 22)
    a.wave('body', 'position', lambda p: [0, sin(p, 1.4, 0.25), 0])
    a.wave('tail', 'rotation', lambda p: [sin(p, 4), sin(p, 6, 0.3), 0])
    a.wave('tail2', 'rotation', lambda p: [sin(p, 5, 0.2), sin(p, 8, 0.4), 0])
    out.append(a)

    a = Anim('animation.shrikewing.glide', 2.0)
    flap(a, 4, 3)
    a.wave('tail', 'rotation', lambda p: [0, sin(p, 5), 0])
    a.wave('head', 'rotation', lambda p: [sin(p, 3), sin(p, 6, 0.3), 0])
    out.append(a)

    # the tell before a dive: hangs in the air, wings flared high, beak open, barb raised
    a = Anim('animation.shrikewing.dive_tell', 1.0, loop='hold')
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (0.3, [0, 0, -sd * 55]), (1.0, [0, 0, -sd * 60])])
        a.keys(w + '_outer', 'rotation', [(0, [0, 0, 0]), (0.3, [0, 0, sd * 25]), (1.0, [0, 0, sd * 30])])
    a.keys('body', 'rotation', [(0, [0, 0, 0]), (0.4, [-22, 0, 0]), (1.0, [-25, 0, 0])])
    a.keys('head', 'rotation', [(0, [0, 0, 0]), (0.4, [-18, 0, 0]), (1.0, [-20, 0, 0])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.3, [35, 0, 0]), (1.0, [35, 0, 0])])
    a.keys('tail', 'rotation', [(0, [0, 0, 0]), (0.5, [-30, 0, 0]), (1.0, [-35, 0, 0])])
    a.keys('tail2', 'rotation', [(0, [0, 0, 0]), (0.5, [-30, 0, 0]), (1.0, [-35, 0, 0])])
    out.append(a)

    a = Anim('animation.shrikewing.dive', 0.5)
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.wave(w, 'rotation', lambda p, sd=sd: [0, sd * 55, -sd * 8])
        a.wave(w + '_outer', 'rotation', lambda p, sd=sd: [0, sd * 30, 0])
    a.wave('body', 'rotation', lambda p: [32, 0, sin(p, 3)])
    a.wave('head', 'rotation', lambda p: [-10, 0, 0])
    a.wave('leg_l', 'rotation', lambda p: [-60, 0, 0])
    a.wave('leg_r', 'rotation', lambda p: [-60, 0, 0])
    out.append(a)

    # after a missed dive it labours to climb: the window to hit it
    a = Anim('animation.shrikewing.recover', 1.2)
    flap(a, 48, 30)
    a.wave('body', 'rotation', lambda p: [-12, 0, sin(p, 9)])
    a.wave('head', 'rotation', lambda p: [10, sin(p, 12), 0])
    a.wave('jaw', 'rotation', lambda p: [max(0, sin(p * 2, 20)), 0, 0])
    out.append(a)

    a = Anim('animation.shrikewing.perch', 3.0)
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.wave(w, 'rotation', lambda p, sd=sd: [0, sd * 78, sd * 10])
        a.wave(w + '_outer', 'rotation', lambda p, sd=sd: [0, sd * 150, 0])
    a.wave('body', 'rotation', lambda p: [-14, 0, 0])
    a.wave('body', 'position', lambda p: [0, sin(p, 0.4), 0])
    a.wave('head', 'rotation', lambda p: [12, sin(p, 30, 0.1), 0], steps=12)
    a.wave('leg_l', 'rotation', lambda p: [-30, 0, 0])
    a.wave('leg_r', 'rotation', lambda p: [-30, 0, 0])
    out.append(a)

    a = Anim('animation.shrikewing.rake', 0.5, loop=False)
    for leg in ('leg_l', 'leg_r'):
        a.keys(leg, 'rotation', [(0, [0, 0, 0]), (0.15, [-80, 0, 0]), (0.3, [20, 0, 0]), (0.5, [0, 0, 0])])
    a.keys('jaw', 'rotation', [(0, [0, 0, 0]), (0.12, [40, 0, 0]), (0.25, [0, 0, 0])])
    a.keys('barb', 'rotation', [(0, [0, 0, 0]), (0.2, [-60, 0, 0]), (0.5, [0, 0, 0])])
    out.append(a)

    a = Anim('animation.shrikewing.death', 1.2, loop='hold')
    a.keys('root', 'rotation', [(0, [0, 0, 0]), (1.2, [0, 0, 160])])
    a.keys('root', 'position', [(0, [0, 0, 0]), (1.2, [0, -6, 0])])
    for w in WINGS:
        sd = 1 if w.endswith('r') else -1
        a.keys(w, 'rotation', [(0, [0, 0, 0]), (1.2, [0, sd * 40, sd * 50])])
    out.append(a)
    return out


def write():
    m = build()
    for d in ('geo/entity', 'animations/entity', 'textures/entity'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    m.save(os.path.join(OUT, 'geo/entity/shrikewing.geo.json'))
    paint(m, os.path.join(OUT, 'textures/entity/shrikewing.png'))
    anims = animations()
    save(anims, os.path.join(OUT, 'animations/entity/shrikewing.animation.json'))
    return m, anims


if __name__ == '__main__':
    write()
    print('shrikewing written')
