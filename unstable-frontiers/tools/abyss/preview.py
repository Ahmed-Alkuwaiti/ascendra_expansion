"""Top-down map and a side section of the Astral Abyss terrain (terrain.py), for tuning. python3 preview.py out_dir"""
import math
import os
import sys

from PIL import Image, ImageDraw

import terrain as t

out = sys.argv[1] if len(sys.argv) > 1 else '.'
os.makedirs(out, exist_ok=True)
X0, X1, Z0, Z1, S = -420, 420, -320, 680, 2
W, H = (X1 - X0) // S, (Z1 - Z0) // S
img = Image.new('RGB', (W, H), (6, 6, 16))
px = img.load()
for i in range(W):
    for j in range(H):
        x, z = X0 + i * S, Z0 + j * S
        sp = t.column(x, z)
        if not sp:
            continue
        top, bot = sp[0]
        k = max(0, min(1, (top - 50) / 130))
        thick = max(0, min(1, (top - bot) / 40))
        r = int(40 + 120 * k)
        g = int(60 + 110 * k * (1 - 0.4 * thick))
        b = int(110 + 120 * k)
        if len(sp) > 1:
            r, g = int(r * 0.85), int(g * 0.85)
        px[i, j] = (r, g, b)
d = ImageDraw.Draw(img)
for name, (cx, cz, r, top) in t.ANCHORS.items():
    i, j = (cx - X0) // S, (cz - Z0) // S
    d.ellipse([i - r // S, j - r // S, i + r // S, j + r // S], outline=(255, 210, 90))
    d.text((i + r // S + 3, j - 6), name, fill=(255, 230, 160))
for sx, sz, sy in t.STONES:
    i, j = (sx - X0) / S, (sz - Z0) / S
    d.point((i, j), fill=(255, 120, 200))
img.save(os.path.join(out, 'abyss_map.png'))

# side section along the landing -> tether spire -> hollow crown line (x = 0..64 band projected), y 0..256
sec = Image.new('RGB', (H, 256), (6, 6, 16))
p2 = sec.load()
for j in range(H):
    z = Z0 + j * S
    x = int(0 + (64 - 0) * max(0, min(1, z / 268))) if z < 268 else int(64 + (24 - 64) * min(1, (z - 268) / 292))
    for top, bot in t.column(x, z):
        for y in range(max(0, bot), min(255, top) + 1):
            p2[j, 255 - y] = (150, 140, 200) if y == top else (70, 60, 110)
sec.save(os.path.join(out, 'abyss_section.png'))
print('ok')
