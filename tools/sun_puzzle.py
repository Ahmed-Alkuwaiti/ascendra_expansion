"""Designs and checks the Sunscar Citadel's mirror puzzle with the same rules as SunBeam.java.

Court cells are (i, j) with i east and j south, 0..16. Walls surround the court; lenses sit in wall cells.
"""
import itertools
import random

N = 17
DIRS = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
SLASH = {'E': 'N', 'N': 'E', 'W': 'S', 'S': 'W'}
BACK = {'E': 'S', 'S': 'E', 'W': 'N', 'N': 'W'}


def trace(mirrors, state, lenses, obstacles, source, facing, openings=()):
    """Returns the set of lenses lit and the path."""
    (x, y), d = source, facing
    lit, path = set(), []
    for _ in range(96):
        dx, dy = DIRS[d]
        x, y = x + dx, y + dy
        p = (x, y)
        path.append(p)
        if p in mirrors:
            d = SLASH[d] if state[mirrors.index(p)] else BACK[d]
            continue
        if p in lenses:
            lit.add(p)
            continue
        inside = 0 <= x < N and 0 <= y < N
        if p in obstacles or p == source or (not inside and p not in openings):
            break
    return lit, path


def analyse(mirrors, init, lenses, obstacles, source, facing, openings=()):
    n = len(mirrors)
    best = {l: 99 for l in lenses}
    all3 = []
    for state in itertools.product((True, False), repeat=n):
        lit, _ = trace(mirrors, state, lenses, obstacles, source, facing, openings)
        flips = sum(a != b for a, b in zip(state, init))
        for l in lit:
            best[l] = min(best[l], flips)
        if len(lit) == len(lenses):
            all3.append(flips)
    return best, all3


def design(seed=7, tries=12000):
    rnd = random.Random(seed)
    lenses = [(-1, 4), (12, -1), (17, 11)]          # west wall, north wall, east wall
    source, facing = (13, 16), 'N'
    obstacles = {(4, 9), (10, 9), (4, 1), (10, 15)}   # four sun pillars, off every line the beam can use
    openings = {(7, 17), (8, 17), (9, 17)}             # the corridor out of the south wall
    best_layout = None
    for _ in range(tries):
        rows, cols = (2, 4, 7, 11, 13), (2, 6, 9, 12, 13, 15)
        cells = [(i, j) for i in cols for j in rows if (i, j) not in obstacles]
        mirrors = rnd.sample(cells, 8)
        init = tuple(rnd.random() < 0.5 for _ in mirrors)
        lit0, _ = trace(mirrors, init, lenses, obstacles, source, facing, openings)
        if lit0:
            continue
        best, all3 = analyse(mirrors, init, lenses, obstacles, source, facing, openings)
        if max(best.values()) >= 99 or min(best.values()) < 2:
            continue
        score = sum(best.values()) + min(best.values())
        if best_layout is None or score > best_layout[0]:
            best_layout = (score, mirrors, init, best, all3)
    return lenses, source, facing, obstacles, openings, best_layout


if __name__ == '__main__':
    lenses, source, facing, obstacles, openings, (score, mirrors, init, best, all3) = design()
    print('mirrors', mirrors)
    print('init', init)
    print('fewest flips to light each lens', best)
    print('(each lens is lit by its own beam: the lenses sit in the walls, so a beam stops after one; lit lenses stay lit)')
