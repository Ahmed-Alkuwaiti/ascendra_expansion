"""Building kit for the frontier's structures.

A Build is a sparse voxel grid. Generators draw into it with shape helpers, mark encounter zones and points of interest,
then save(): that writes the structure template (.nbt, the exact file the game places), a sidecar JSON the mod reads
for encounters and features, and nothing else. Previews are rendered from the saved .nbt, so a preview always shows the
real structure.
"""
import json
import math
import os
import random

import nbtlib
from nbtlib import Compound, Int, List, String, Byte

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'src', 'main', 'resources')
NS = 'unstable_frontiers'
TEMPLATES = os.path.join(RES, 'data', NS, 'structure')
LANDMARKS = os.path.join(RES, 'data', NS, 'landmark')
DATA_VERSION = 3955  # Minecraft 1.21.1

AIR = 'minecraft:air'
VOID = 'minecraft:structure_void'


def h(x, y, z, salt=0):
    """Stable pseudo-random 0..1 for a position, so details never shift between runs."""
    x, y, z = int(round(x)), int(round(y)), int(round(z))
    n = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (salt * 2654435761)
    n = (n ^ (n >> 13)) * 0x5bd1e995 & 0xffffffff
    return ((n ^ (n >> 15)) & 0xffffff) / 0xffffff


def B(name, **props):
    """A block with properties, e.g. B('chain', axis='x')."""
    if ':' not in name:
        name = 'minecraft:' + name
    return (name, tuple(sorted((k, str(v).lower()) for k, v in props.items())))


class Build:
    def __init__(self, name, W, H, L, seed=1):
        self.name, self.W, self.H, self.L = name, W, H, L
        self.b = {}
        self.nbt = {}
        self.rnd = random.Random(seed)
        self.zones = []
        self.points = {}
        self.meta = {}

    # ---------------------------------------------------------------- cells
    def inside(self, x, y, z):
        return 0 <= x < self.W and 0 <= y < self.H and 0 <= z < self.L

    def set(self, x, y, z, block, over=True):
        x, y, z = int(round(x)), int(round(y)), int(round(z))
        if not self.inside(x, y, z):
            return
        if not over and (x, y, z) in self.b and self.b[(x, y, z)][0] != AIR:
            return
        if block is None:
            return
        if isinstance(block, str):
            block = B(block) if ':' not in block or not block.startswith('minecraft:') else (block, ())
        self.b[(x, y, z)] = block
        self.nbt.pop((x, y, z), None)

    def get(self, x, y, z):
        v = self.b.get((x, y, z))
        return v[0] if v else None

    def solid(self, x, y, z):
        n = self.get(x, y, z)
        return n is not None and n not in (AIR, VOID) and not any(s in n for s in ('bars', 'chain', 'ladder', 'cobweb', 'lantern', 'carpet', 'torch', 'rod'))

    def clear(self, x, y, z):
        self.set(x, y, z, AIR)

    # ---------------------------------------------------------------- shapes
    def box(self, x0, y0, z0, x1, y1, z1, pick, hollow=False, over=True):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    edge = x in (x0, x1) or y in (y0, y1) or z in (z0, z1)
                    if hollow and not edge:
                        self.set(x, y, z, AIR, over)
                    else:
                        self.set(x, y, z, pick(x, y, z) if callable(pick) else pick, over)

    def walls(self, x0, y0, z0, x1, y1, z1, pick):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    for y in range(y0, y1 + 1):
                        self.set(x, y, z, pick(x, y, z) if callable(pick) else pick)

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, pick, over=True, shell=None):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                    if d <= 1 and (shell is None or d >= shell):
                        self.set(x, y, z, pick(x, y, z) if callable(pick) else pick, over)

    def cylinder(self, cx, cz, r, y0, y1, pick, hollow=None, over=True):
        for y in range(y0, y1 + 1):
            rr = r(y) if callable(r) else r
            for x in range(int(cx - rr) - 1, int(cx + rr) + 2):
                for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    d = math.hypot(x - cx, z - cz)
                    if d <= rr and (hollow is None or d > rr - hollow):
                        self.set(x, y, z, pick(x, y, z) if callable(pick) else pick, over)

    def line(self, a, b, pick, radius=0.0, over=True):
        n = max(1, int(math.dist(a, b) * 2.5))
        for i in range(n + 1):
            t = i / n
            p = [a[k] + (b[k] - a[k]) * t for k in range(3)]
            if radius <= 0:
                self.set(p[0], p[1], p[2], pick(*p) if callable(pick) else pick, over)
            else:
                self.ellipsoid(p[0], p[1], p[2], radius, radius, radius, pick, over)

    def curve(self, pts, pick, radius=lambda t: 0.0, over=True):
        """A Catmull-Rom spline through pts, with a radius that can change along it."""
        P = [pts[0]] + list(pts) + [pts[-1]]
        segs = len(pts) - 1
        for s in range(segs):
            p0, p1, p2, p3 = P[s], P[s + 1], P[s + 2], P[s + 3]
            n = max(2, int(math.dist(p1, p2) * 3))
            for i in range(n):
                t = i / n
                q = [0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                            + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t ** 3) for k in range(3)]
                r = radius((s + t) / segs)
                if r <= 0.5:
                    self.set(q[0], q[1], q[2], pick(*q) if callable(pick) else pick, over)
                else:
                    self.ellipsoid(q[0], q[1], q[2], r, r, r, pick, over)

    # ---------------------------------------------------------------- furnishings
    def chest(self, x, y, z, loot, facing='north', barrel=False):
        if barrel:
            self.set(x, y, z, B('barrel', facing='up', open='false'))
        else:
            self.set(x, y, z, B('chest', facing=facing, type='single', waterlogged='false'))
        self.nbt[(x, y, z)] = Compound({'LootTable': String(f'{NS}:{loot}' if ':' not in loot else loot)})

    def lectern_book(self, x, y, z, facing, title, pages, author='Ilsa Vane'):
        self.set(x, y, z, B('lectern', facing=facing, has_book='true', powered='false'))
        page_list = List[Compound]([Compound({'raw': String(json.dumps({'text': p}))}) for p in pages])
        book = Compound({'id': String('minecraft:written_book'), 'count': Int(1), 'components': Compound({
            'minecraft:written_book_content': Compound({'title': Compound({'raw': String(title)}), 'author': String(author),
                                                        'pages': page_list, 'resolved': Byte(1)})})})
        self.nbt[(x, y, z)] = Compound({'Book': book, 'Page': Int(0)})

    def sign(self, x, y, z, facing_rot, lines, wall=None):
        if wall:
            self.set(x, y, z, B('dark_oak_wall_sign', facing=wall, waterlogged='false'))
        else:
            self.set(x, y, z, B('dark_oak_sign', rotation=facing_rot, waterlogged='false'))
        msgs = List[String]([String(json.dumps({'text': l})) for l in (lines + ['', '', '', ''])[:4]])
        side = Compound({'messages': msgs, 'color': String('white'), 'has_glowing_text': Byte(1)})
        self.nbt[(x, y, z)] = Compound({'front_text': side, 'back_text': side, 'is_waxed': Byte(1)})

    def chain(self, x, y0, y1, z):
        for y in range(min(y0, y1), max(y0, y1) + 1):
            self.set(x, y, z, B('chain', axis='y', waterlogged='false'))

    def hang_lantern(self, x, y, z, soul=False):
        self.set(x, y, z, B('soul_lantern' if soul else 'lantern', hanging='true', waterlogged='false'))

    # ---------------------------------------------------------------- encounter and feature markers
    def zone(self, zid, name, box, spawns, roster, kind='waves', waves=None, flyers_at=None, reward=None, trigger=None, **extra):
        """An encounter. box = (x0,y0,z0,x1,y1,z1) is the fighting space; trigger (defaults to box) wakes it.
        spawns are local feet positions. roster names a roster in the mod's rosters file."""
        z = {'id': zid, 'name': name, 'box': list(box), 'trigger': list(trigger or box), 'spawns': [list(s) for s in spawns],
             'roster': roster, 'kind': kind}
        if waves is not None:
            z['waves'] = waves
        if flyers_at is not None:
            z['flyer_spawns'] = [list(s) for s in flyers_at]
        if reward:
            z['reward'] = reward
        z.update(extra)
        self.zones.append(z)

    def point(self, key, x, y, z):
        self.points[key] = [x, y, z]

    # ---------------------------------------------------------------- output
    def footprint(self):
        """Columns the template occupies at its lowest level, for the foundation fill."""
        low = {}
        for (x, y, z), (n, _) in self.b.items():
            if n in (AIR, VOID):
                continue
            if (x, z) not in low or y < low[(x, z)]:
                low[(x, z)] = y
        return low

    def save(self, foundation_level=None):
        palette, index, blocks = [], {}, []
        for (x, y, z), (name, props) in sorted(self.b.items()):
            key = (name, props)
            if key not in index:
                index[key] = len(palette)
                e = Compound({'Name': String(name)})
                if props:
                    e['Properties'] = Compound({k: String(v) for k, v in props})
                palette.append(e)
            blk = Compound({'pos': List[Int]([Int(x), Int(y), Int(z)]), 'state': Int(index[key])})
            if (x, y, z) in self.nbt:
                blk['nbt'] = self.nbt[(x, y, z)]
            blocks.append(blk)
        root = Compound({'DataVersion': Int(DATA_VERSION), 'size': List[Int]([Int(self.W), Int(self.H), Int(self.L)]),
                         'palette': List[Compound](palette), 'blocks': List[Compound](blocks), 'entities': List[Compound]([])})
        os.makedirs(TEMPLATES, exist_ok=True)
        path = os.path.join(TEMPLATES, f'{self.name}.nbt')
        nbtlib.File(root, gzipped=True).save(path)
        side = {'template': f'{NS}:{self.name}', 'size': [self.W, self.H, self.L], 'zones': self.zones,
                'points': self.points, **self.meta}
        if foundation_level is not None:
            side['foundation_level'] = foundation_level
        os.makedirs(LANDMARKS, exist_ok=True)
        with open(os.path.join(LANDMARKS, f'{self.name}.json'), 'w') as f:
            json.dump(side, f, indent=1)
        solid = sum(1 for v in self.b.values() if v[0] not in (AIR, VOID))
        print(f'{self.name}: {self.W}x{self.H}x{self.L}, {solid} blocks, {len(palette)} block states, {len(self.zones)} encounters')
        return path
