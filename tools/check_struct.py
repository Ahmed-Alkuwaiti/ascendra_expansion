"""Structural checks on a generated template: flooding risks and a walkable route between two points."""
import collections
import sys

import nbtlib

NOCOLLIDE = ('water', 'ladder', 'seagrass', 'kelp', 'sea_pickle', 'carpet', 'torch', 'candle', 'vein', 'rail', 'dead_bush', 'fern', 'vine')
EXACT = {'air', 'cave_air', 'snow', 'grass', 'tall_grass', 'tube_coral', 'brain_coral', 'bubble_coral', 'fire_coral', 'horn_coral', 'chain', 'lever',
         'red_mushroom', 'brown_mushroom', 'poppy', 'dandelion', 'allium', 'blue_orchid', 'azure_bluet', 'oxeye_daisy', 'cornflower',
         'lily_of_the_valley', 'crimson_roots', 'nether_sprouts', 'hanging_roots', 'glow_lichen', 'cobweb', 'spore_blossom'}


def load(path):
    t = nbtlib.load(path)
    pal = [str(p['Name']).split(':')[1] for p in t['palette']]
    return {tuple(int(v) for v in b['pos']): pal[int(b['state'])] for b in t['blocks']}, [int(v) for v in t['size']]


def leaks(blocks, water_top):
    """Air below the water line that touches water, or touches a cell the template leaves to the world (which may be sea)."""
    bad = []
    for (x, y, z), n in blocks.items():
        if n != 'air' or y > water_top:
            continue
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            q = (x + d[0], y + d[1], z + d[2])
            m = blocks.get(q)
            if m == 'water' or (m is None and q[1] <= water_top):
                bad.append(((x, y, z), q, m))
    return bad


def passable(n):
    return n is None or n in EXACT or n.endswith('_wall_banner') or (any(k in n for k in NOCOLLIDE) and 'wall' not in n and 'block' not in n)


def walk(blocks, start, goal_fn, limit=400000):
    """BFS over standing positions: feet and head free, solid below (or a ladder/water), steps of up to one block."""
    def can_stand(p):
        x, y, z = p
        a, b, c = blocks.get((x, y, z)), blocks.get((x, y + 1, z)), blocks.get((x, y - 1, z))
        if not (passable(a) and passable(b)):
            return False
        if a and ('ladder' in a or 'water' in a):
            return True
        return c is not None and not passable(c) or (c is not None and ('ladder' in c))
    seen = {start}
    q = collections.deque([start])
    while q and len(seen) < limit:
        p = q.popleft()
        if goal_fn(p):
            return p, len(seen)
        x, y, z = p
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
            for dy in (1, 0, -1, -2, -3):
                n = (x + dx, y + dy, z + dz)
                if n in seen or (dx == dz == 0 and dy == 0):
                    continue
                if dy > 0 and not (passable(blocks.get((x, y + 2, z)))):
                    continue
                if dx == dz == 0 and dy > 0 and not (blocks.get(p) and ('ladder' in blocks[p] or 'water' in blocks[p])):
                    continue
                if can_stand(n):
                    seen.add(n)
                    q.append(n)
    return None, len(seen)


if __name__ == '__main__':
    b, size = load(sys.argv[1])
    wl = int(sys.argv[2])
    lk = leaks(b, wl)
    print('flood risks:', len(lk), lk[:12])
