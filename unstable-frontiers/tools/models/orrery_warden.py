"""The Orrery Warden: one of the observatory's machines, a brass orrery that kept the rift engine's instruments aligned.
The rift got into it. Now it drifts on its own, three rings turning around a lens that burns with starlight, and it
guards whatever it was built near. When its rings stop and line up and its lens flares, it is about to fire; after the
beam its rings stall and it sags, open.

Writes geo/entity/orrery_warden.geo.json, animations/entity/orrery_warden.animation.json, textures/entity/orrery_warden.png.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from anim import Anim, save, sin
from geo import Model
from tex import Material, paint

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers')
NAME = 'orrery_warden'

BRASS = Material('plate', (176, 138, 70), dark=(104, 76, 36), light=(226, 194, 120), seed=201, rust=(76, 150, 128))
DARK = Material('plate', (52, 58, 84), dark=(26, 28, 44), light=(92, 100, 140), seed=203, rust=None)
LENS = Material('glow', (120, 240, 255), dark=(40, 150, 200), light=(240, 255, 255), seed=205, glow=True)
GROWTH = Material('glow', (150, 90, 220), dark=(70, 30, 120), light=(220, 170, 255), seed=207, glow=True)
CHAIN = Material('iron', (90, 92, 104), dark=(50, 52, 60), light=(140, 120, 100), seed=209, rim=False)


def ring(m, name, parent, r, y, thick, mat, segs=12, tilt=None):
    """A ring of segments in the XZ plane of its bone (pivot at the core's centre). A tilted ring nests in a tilt bone."""
    if tilt is not None:
        holder = m.bone(name + '_tilt', (0, y, 0), parent, rotation=tilt)
        parent = holder
    b = m.bone(name, (0, y, 0), parent)
    seg_len = 2 * math.pi * r / segs + 0.8
    for i in range(segs):
        a = 2 * math.pi * i / segs
        cx, cz = r * math.cos(a), r * math.sin(a)
        # each segment lies along the ring's tangent (a cube rotation about the vertical through its centre)
        yaw = -math.degrees(a) + 90
        b.cube((cx - seg_len / 2, y - thick / 2, cz - thick / 2), (seg_len, thick, thick), mat if i % 2 else DARK,
               rotation=(0, yaw, 0), pivot=(cx, y, cz))
        if i % 3 == 0:
            b.cube((cx - 1, y - thick / 2 - 0.75, cz - 1), (2, thick + 1.5, 2), LENS, rotation=(0, yaw, 0), pivot=(cx, y, cz))
    return b


def build():
    m = Model(NAME, 128, 128)
    root = m.bone('root', (0, 0, 0))
    core = m.bone('core', (0, 20, 0), root)
    core.cube((-5, 15, -5), (10, 10, 10), DARK)
    core.cube((-6, 16, -4), (12, 8, 8), BRASS)
    core.cube((-4, 16, -6), (8, 8, 12), BRASS)
    core.cube((-4, 14, -4), (8, 12, 8), DARK)
    lens = m.bone('lens', (0, 20, -6), core)
    lens.cube((-3, 17, -7.5), (6, 6, 2), BRASS)
    lens.cube((-2, 18, -8.2), (4, 4, 1), LENS)
    crown = m.bone('crown', (0, 26, 0), core)
    for i in range(5):
        a = 2 * math.pi * i / 5
        crown.cube((3 * math.cos(a) - 0.5, 26, 3 * math.sin(a) - 0.5), (1, 4 + (i % 2) * 2, 1), BRASS)
    crown.cube((-1, 26, -1), (2, 7, 2), LENS)
    # rift growth bursting through the casing
    core.cube((3, 22, 2), (3, 3, 3), GROWTH)
    core.cube((-6.5, 15, 1), (2, 3, 4), GROWTH)
    ring(m, 'ring_a', core, 11, 20, 2, BRASS, segs=14)
    ring(m, 'ring_b', core, 14, 20, 1.5, BRASS, segs=16, tilt=(62, 0, 0))
    ring(m, 'ring_c', core, 17, 20, 1.5, BRASS, segs=18, tilt=(-58, 30, 0))
    pend = m.bone('pendulum', (0, 14, 0), core)
    pend.cube((-0.5, 6, -0.5), (1, 8, 1), CHAIN)
    pend.cube((-2, 2, -2), (4, 4, 4), BRASS)
    pend.cube((-1, 1, -1), (2, 1, 2), LENS)
    return m


def animations():
    out = []
    a = Anim(f'animation.{NAME}.idle', 4.0)
    a.wave('ring_a', 'rotation', lambda p: [0, 360 * p, 0], steps=16)
    a.wave('ring_b', 'rotation', lambda p: [0, -360 * p, 0], steps=16)
    a.wave('ring_c', 'rotation', lambda p: [0, 720 * p, 0], steps=16)
    a.wave('core', 'position', lambda p: [0, sin(p, 1.2), 0])
    a.wave('pendulum', 'rotation', lambda p: [sin(p, 10), 0, sin(p, 6, 0.25)])
    a.wave('lens', 'rotation', lambda p: [sin(p, 4), sin(p, 10, 0.2), 0])
    out.append(a)

    # the tell: rings stop, swing into line behind the lens, the lens draws back and flares
    a = Anim(f'animation.{NAME}.beam_tell', 1.0, loop='hold')
    a.keys('ring_a', 'rotation', [(0, [0, 0, 0]), (0.6, [0, 90, 0]), (1.0, [0, 90, 0])])
    a.keys('ring_b_tilt', 'rotation', [(0, [0, 0, 0]), (0.6, [28, 0, 0]), (1.0, [28, 0, 0])])
    a.keys('ring_c_tilt', 'rotation', [(0, [0, 0, 0]), (0.6, [-32, -30, 0]), (1.0, [-32, -30, 0])])
    a.keys('lens', 'position', [(0, [0, 0, 0]), (0.5, [0, 0, 1.5]), (1.0, [0, 0, 1.5])])
    a.keys('lens', 'scale', [(0, [1, 1, 1]), (0.8, [1.4, 1.4, 1]), (1.0, [1.5, 1.5, 1])])
    a.keys('pendulum', 'rotation', [(0, [0, 0, 0]), (0.5, [25, 0, 0])])
    out.append(a)

    a = Anim(f'animation.{NAME}.beam', 1.5)
    a.wave('lens', 'scale', lambda p: [1.5 + sin(p * 3, 0.15), 1.5 + sin(p * 3, 0.15), 1])
    a.wave('ring_a', 'rotation', lambda p: [0, 90, sin(p * 6, 2)])
    a.wave('ring_b_tilt', 'rotation', lambda p: [28, 0, 0])
    a.wave('ring_c_tilt', 'rotation', lambda p: [-32, -30, 0])
    a.wave('core', 'position', lambda p: [sin(p * 6, 0.3), 0, 0.8])
    out.append(a)

    # after firing: rings stall and droop, the core sags. The opening.
    a = Anim(f'animation.{NAME}.stalled', 2.0)
    a.wave('ring_a', 'rotation', lambda p: [14, 90, 8], steps=4)
    a.wave('ring_b_tilt', 'rotation', lambda p: [40, 0, 10], steps=4)
    a.wave('ring_c_tilt', 'rotation', lambda p: [-10, -30, -12], steps=4)
    a.wave('core', 'position', lambda p: [0, -3 + sin(p, 0.4), 0])
    a.wave('core', 'rotation', lambda p: [12, 0, sin(p, 5)])
    a.wave('lens', 'scale', lambda p: [0.7, 0.7, 1], steps=4)
    out.append(a)

    a = Anim(f'animation.{NAME}.pulse_tell', 0.6, loop='hold')
    for r in ('ring_a', 'ring_b', 'ring_c'):
        a.keys(r, 'scale', [(0, [1, 1, 1]), (0.5, [0.7, 1, 0.7]), (0.6, [0.65, 1, 0.65])])
    a.keys('core', 'scale', [(0, [1, 1, 1]), (0.6, [0.9, 0.9, 0.9])])
    out.append(a)

    a = Anim(f'animation.{NAME}.pulse', 0.5, loop=False)
    for r in ('ring_a', 'ring_b', 'ring_c'):
        a.keys(r, 'scale', [(0, [0.65, 1, 0.65]), (0.12, [1.5, 1, 1.5]), (0.5, [1, 1, 1])])
    out.append(a)

    a = Anim(f'animation.{NAME}.death', 1.5, loop='hold')
    a.keys('ring_a', 'position', [(0, [0, 0, 0]), (1.5, [0, -14, 0])])
    a.keys('ring_b_tilt', 'rotation', [(0, [0, 0, 0]), (1.5, [70, 0, 40])])
    a.keys('ring_c_tilt', 'rotation', [(0, [0, 0, 0]), (1.5, [-60, 0, -50])])
    a.keys('core', 'position', [(0, [0, 0, 0]), (1.5, [0, -12, 0])])
    a.keys('core', 'rotation', [(0, [0, 0, 0]), (1.5, [50, 30, 20])])
    a.keys('lens', 'scale', [(0, [1, 1, 1]), (1.5, [0.2, 0.2, 1])])
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
