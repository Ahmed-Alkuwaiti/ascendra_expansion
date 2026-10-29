"""Renders a model posed at a moment of one of its animations, from the same geometry and texture the game loads, so
models and animations can be inspected without a game client. These are preview renders, not in-game screenshots.

Bone maths follows GeckoLib's loader: x of pivots and cube origins is mirrored, x and y rotations are negated, and each
bone rotates about its pivot in Z, Y, X order (rotation X applied first), parents before children.
"""
import math

import numpy as np
from PIL import Image, ImageDraw


def rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def bone_mats(model, anim=None, t=0.0):
    mats = {}
    for b in model.bones:              # parents are declared before children
        r = list(b.rotation)
        pos = [0, 0, 0]
        if anim is not None:
            ar = anim.sample(b.name, 'rotation', t)
            if ar:
                r = [r[i] + ar[i] for i in range(3)]
            ap = anim.sample(b.name, 'position', t)
            if ap:
                pos = ap
        pivot = np.array([-b.pivot[0], b.pivot[1], b.pivot[2]])
        R = rot(math.radians(-r[0]), math.radians(-r[1]), math.radians(r[2]))
        M = np.eye(4)
        M[:3, :3] = R
        M[:3, 3] = pivot - R @ pivot + np.array([-pos[0], pos[1], pos[2]])
        if b.parent:
            M = mats[b.parent] @ M
        mats[b.name] = M
    return mats


def render(model, texture, out, anim=None, t=0.0, yaw=35.0, pitch=22.0, size=640, bg=(36, 38, 48), ground=True, label=None):
    tex = texture.convert('RGBA')
    mats = bone_mats(model, anim, t)
    quads = []
    light = np.array([0.4, 0.8, -0.45])
    light /= np.linalg.norm(light)
    from tex import faces as face_regions
    for b in model.bones:
        M = mats[b.name]
        for c in b.cubes:
            (ox, oy, oz), (sw, sh, sd) = c.origin, c.size
            inf = c.inflate
            x0, x1 = -(ox + sw) - inf, -ox + inf
            y0, y1, z0, z1 = oy - inf, oy + sh + inf, oz - inf, oz + sd + inf
            regions = face_regions(c)
            # face: (corner origin, u axis, v axis (downwards on the texture), normal)
            spec = {
                'north': ((x1, y1, z0), (x0 - x1, 0, 0), (0, y0 - y1, 0), (0, 0, -1)),
                'south': ((x0, y1, z1), (x1 - x0, 0, 0), (0, y0 - y1, 0), (0, 0, 1)),
                'east': ((x0, y1, z0), (0, 0, z1 - z0), (0, y0 - y1, 0), (-1, 0, 0)),
                'west': ((x1, y1, z1), (0, 0, z0 - z1), (0, y0 - y1, 0), (1, 0, 0)),
                'up': ((x1, y1, z1), (x0 - x1, 0, 0), (0, 0, z0 - z1), (0, 1, 0)),
                'down': ((x1, y0, z0), (x0 - x1, 0, 0), (0, 0, z1 - z0), (0, -1, 0)),
            }
            for face, (o, ua, va, nrm) in spec.items():
                fx, fy, fw, fh = regions[face]
                o, ua, va = np.array(o, float), np.array(ua, float), np.array(va, float)
                n = M[:3, :3] @ np.array(nrm, float)
                lum = 0.55 + 0.45 * max(0.0, float(n @ light))
                for j in range(fh):
                    for i in range(fw):
                        col = tex.getpixel((fx + i, fy + j))
                        if col[3] < 16:
                            continue
                        p = [o + ua * (i / fw) + va * (j / fh), o + ua * ((i + 1) / fw) + va * (j / fh),
                             o + ua * ((i + 1) / fw) + va * ((j + 1) / fh), o + ua * (i / fw) + va * ((j + 1) / fh)]
                        pts = [(M @ np.append(q, 1.0))[:3] for q in p]
                        quads.append((pts, tuple(int(v * lum) for v in col[:3]) + (col[3],)))
    # camera: turn the model by yaw, tilt by pitch, look along -z from +z
    ya, pa = math.radians(yaw), math.radians(pitch)
    cam = rot(pa, 0, 0) @ rot(0, ya, 0)
    proj = []
    for pts, col in quads:
        v = [cam @ p for p in pts]
        depth = sum(q[2] for q in v) / 4
        proj.append((depth, [(q[0], -q[1]) for q in v], col))
    xs = [x for _, ps, _ in proj for x, _ in ps]
    ys = [y for _, ps, _ in proj for _, y in ps]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1
    scale = size * 0.82 / span
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    img = Image.new('RGB', (size, size), bg)
    d = ImageDraw.Draw(img, 'RGBA')
    if ground:
        gy = size / 2 + (0 - cy) * scale
        # floor line at model y = 0, seen at the tilt
        for k in range(-6, 7):
            pass
    for depth, ps, col in sorted(proj, key=lambda q: q[0]):
        pts = [(size / 2 + (x - cx) * scale, size / 2 + (y - cy) * scale) for x, y in ps]
        d.polygon(pts, fill=col)
    if label:
        d.text((10, 10), label, fill=(220, 220, 230, 255))
    img.save(out)
    return img
