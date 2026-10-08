"""Walks every dungeon from its entrance to each of its chests (feet and head clear, solid underfoot, steps of one block, ladders)."""
import sys

import paths
from check_struct import load, walk


def standable(blocks, p):
    from check_struct import passable
    x, y, z = p
    return passable(blocks.get((x, y, z))) and passable(blocks.get((x, y + 1, z))) and not passable(blocks.get((x, y - 1, z)))


def main(only=None):
    import gen_dungeons as gd
    bad = 0
    for did, (biome, fn, kind) in gd.DUNGEONS.items():
        if only and did not in only:
            continue
        d = fn()
        blocks, size = load(f'{paths.RES}/data/aurelia/structures/dungeon_{did}.nbt')
        ex, ey, ez = d.entrance
        start = None
        for r in range(0, 6):                                           # nearest standing spot to the entrance
            for dy in range(-6, 8):
                for dx in range(-r, r + 1):
                    for dz in range(-r, r + 1):
                        p = (ex + dx, ey + dy, ez + dz)
                        if start is None and standable(blocks, p):
                            start = p
            if start:
                break
        if start is None:
            print(f'{did:20s} no place to stand at the entrance {d.entrance}')
            bad += 1
            continue
        miss = []
        for (cx, cy, cz, kind_) in d.chests:
            goal = lambda p, cx=cx, cy=cy, cz=cz: abs(p[0] - cx) + abs(p[2] - cz) <= 2 and cy - 2 <= p[1] <= cy + 1
            found, _ = walk(blocks, start, goal)
            if not found:
                miss.append(f'{kind_}@{cx},{cy},{cz}')
        print(f'{did:20s} {len(d.chests) - len(miss)}/{len(d.chests)} chests reachable' + (f'  MISSING {miss}' if miss else ''))
        bad += bool(miss)
    print('ALL OK' if not bad else f'{bad} dungeons with unreachable chests')


if __name__ == '__main__':
    main(sys.argv[1:] or None)
