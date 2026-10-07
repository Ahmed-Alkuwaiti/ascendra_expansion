"""Preview renderer for the box models in mobspecs (software z-buffer, orthographic, textured).

Uses the same hierarchy rules as gen_models.py: a child's pivot is relative to its parent's pivot in the parent's
rotated frame, and rotation is Rz * Ry * Rx in spec space (y up, front +z).
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import mobspecs


def rot(rx, ry, rz):
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def world_frames(parts):
    byname = {p['name']: p for p in parts}
    frames = {}

    def frame(p):
        if p['name'] in frames:
            return frames[p['name']]
        R = rot(*p['rot'])
        t = np.array(p['pivot'], dtype=float)
        if p.get('parent'):
            PR, Pt = frame(byname[p['parent']])
            R, t = PR @ R, Pt + PR @ t
        frames[p['name']] = (R, t)
        return R, t
    for p in parts:
        frame(p)
    return frames


def faces_of(p):
    w, h, d = p['size']
    x0, y0, z0 = p['origin']
    x1, y1, z1 = x0 + w, y0 + h, z0 + d
    u, v = p['uv']
    # (top-left corner, s-edge end, t-edge end, texture rect)
    return [
        ((x0, y1, z1), (x1, y1, z1), (x0, y0, z1), (u + d, v + d, w, h)),            # front +z
        ((x1, y1, z0), (x0, y1, z0), (x1, y0, z0), (u + 2 * d + w, v + d, w, h)),    # back -z
        ((x1, y1, z1), (x1, y1, z0), (x1, y0, z1), (u + d + w, v + d, d, h)),        # +x
        ((x0, y1, z0), (x0, y1, z1), (x0, y0, z0), (u, v + d, d, h)),                # -x
        ((x0, y1, z0), (x1, y1, z0), (x0, y1, z1), (u + d, v, w, d)),                # top
        ((x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (u + d + w, v, w, d)),            # bottom
    ]


def render(parts, tex, glow, yaw=-35, pitch=22, size=900, margin=40, bg=None, scale=None, center=None, light=(-0.4, 0.75, 0.55), alpha=False):
    frames = world_frames(parts)
    V = rot(math.radians(pitch), 0, 0) @ rot(0, math.radians(yaw), 0)
    T = np.asarray(tex.convert('RGBA'), dtype=np.float32)
    G = np.asarray(glow.convert('RGBA'), dtype=np.float32)
    L = np.array(light) / np.linalg.norm(light)
    quads = []
    for p in parts:
        if p.get('hidden'):
            continue
        R, t = frames[p['name']]
        for (a, b, c, rect) in faces_of(p):
            pts = [V @ (t + R @ np.array(q, dtype=float)) for q in (a, b, c)]
            n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
            if np.linalg.norm(n) == 0:
                continue
            n = -n / np.linalg.norm(n)    # faces_of winds each face inward; flip to the outward normal
            if n[2] < -1e-6:              # facing away from the viewer (+z toward viewer after the view rotation)
                continue
            wn = V.T @ n
            quads.append((pts, rect, max(0.0, float(wn @ L))))
    allp = np.array([q for qq in quads for q in qq[0]])
    lo, hi = allp.min(axis=0), allp.max(axis=0)
    if scale is None:
        scale = (size - 2 * margin) / max(hi[0] - lo[0], hi[1] - lo[1])
    if center is None:
        center = ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
    W = H = size
    img = np.zeros((H, W, 3), dtype=np.float32)
    if bg is not None:
        top, bot = np.array(bg[0], dtype=np.float32), np.array(bg[1], dtype=np.float32)
        img[:] = (top[None, :] * (1 - np.linspace(0, 1, H)[:, None]) + bot[None, :] * np.linspace(0, 1, H)[:, None])[:, None, :]
    zbuf = np.full((H, W), -1e9, dtype=np.float32)

    def sx(p):
        return (p[0] - center[0]) * scale + W / 2, -(p[1] - center[1]) * scale + H / 2

    for pts, (tu, tv, tw, th), shade in quads:
        p0, p1, p2 = [np.array(sx(p)) for p in pts]
        e1, e2 = p1 - p0, p2 - p0
        det = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(det) < 1e-6:
            continue
        corners = [p0, p1, p2, p1 + e2]
        xs = [c[0] for c in corners]
        ys = [c[1] for c in corners]
        xa, xb = max(0, int(math.floor(min(xs)))), min(W - 1, int(math.ceil(max(xs))))
        ya, yb = max(0, int(math.floor(min(ys)))), min(H - 1, int(math.ceil(max(ys))))
        if xa > xb or ya > yb:
            continue
        X, Y = np.meshgrid(np.arange(xa, xb + 1) + 0.5, np.arange(ya, yb + 1) + 0.5)
        dx, dy = X - p0[0], Y - p0[1]
        s = (dx * e2[1] - dy * e2[0]) / det
        t = (e1[0] * dy - e1[1] * dx) / det
        m = (s >= -0.001) & (s <= 1.001) & (t >= -0.001) & (t <= 1.001)
        if not m.any():
            continue
        z = pts[0][2] + s * (pts[1][2] - pts[0][2]) + t * (pts[2][2] - pts[0][2])
        sub = zbuf[ya:yb + 1, xa:xb + 1]
        m &= z > sub
        if not m.any():
            continue
        iu = np.clip((tu + np.clip(s, 0, 0.9999) * tw).astype(int), 0, T.shape[1] - 1)
        iv = np.clip((tv + np.clip(t, 0, 0.9999) * th).astype(int), 0, T.shape[0] - 1)
        col = T[iv, iu, :3]
        gl = G[iv, iu]
        lit = col * (0.42 + 0.68 * shade)
        glow_on = gl[..., 3:4] > 0
        lit = np.where(glow_on, np.maximum(lit, gl[..., :3] * 1.05), lit)
        region = img[ya:yb + 1, xa:xb + 1]
        region[m] = lit[m]
        sub[m] = z[m]
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), 'RGB')
    if alpha:
        out.putalpha(Image.fromarray(((zbuf > -1e9) * 255).astype(np.uint8), 'L'))
    return out, scale


def build(key):
    m = mobspecs.MOBS[key]
    parts = m['parts']()
    img, sheet = mobspecs.paint(parts, m['seed'])
    glow = img.info.pop('glow')
    return parts, img, glow


def sheet(keys, out, views=((-35, 18), (145, 18)), size=640, title=None, bg=((24, 26, 34), (52, 56, 70)), labels=None):
    tiles = []
    for key in keys:
        parts, tex, glow = build(key)
        row = []
        sc = None
        for (yaw, pitch) in views:
            im, s = render(parts, tex, glow, yaw, pitch, size=size, bg=bg, scale=sc)
            sc = s if sc is None else sc
            row.append(im)
        tiles.append((key, row, len(parts)))
    cols = len(views)
    W = cols * size
    H = len(tiles) * (size + 36) + (60 if title else 0)
    canvas = Image.new('RGB', (W, H), (14, 14, 20))
    d = ImageDraw.Draw(canvas)
    try:
        f1 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 30)
        f2 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    y = 0
    if title:
        d.text((16, 12), title, fill=(255, 210, 140), font=f1)
        y = 60
    for key, row, n in tiles:
        name = (labels or {}).get(key, key.replace('_', ' ').title())
        d.text((14, y + 6), f'{name}  ({n} parts)', fill=(230, 230, 240), font=f2)
        for i, im in enumerate(row):
            canvas.paste(im, (i * size, y + 36))
        y += size + 36
    canvas.save(out)
    print('wrote', out)


if __name__ == '__main__':
    keys = sys.argv[2:]
    sheet(keys, sys.argv[1])
