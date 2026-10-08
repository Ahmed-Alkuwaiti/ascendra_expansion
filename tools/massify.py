"""Doubles every realm structure (the outposts, spires, colossi, islands, ruins, arches and wrecks): each block becomes a 2 x 2 x 2
block of the same, so a twenty-block outpost is now forty blocks across and its spire twice as tall.

Thin and single things are handled so the result still reads: slabs fill their own half (as double slabs), stairs keep their
step, fences, walls, bars and panes thicken into posts, doors stay one door tall-and-a-half, and anything that must stay single
(chests, lanterns, flowers, skulls, campfires, the mod's blocks) sits once in its corner. Guards stand where they stood, scaled.

The originals are kept in tools/_cores/realm/; this writes the doubled templates over data/aurelia/structures and adjusts how
deep each sits (surface structures sink twice as far, stalactites keep hanging from the ceiling, sky pieces keep their range).
"""
import json
import os

import nbtlib
from nbtlib import Compound, Double, Int, List

import gen_citadels2
import paths
from gen_act3_citadels import AIR, Grid

CORES = os.path.join(os.path.dirname(__file__), '_cores', 'realm')
STRUCT = paths.RES + '/data/aurelia/structures'
WG = paths.RES + '/data/aurelia/worldgen'
PREFIXES = ('grove_', 'root_arch', 'sky_', 'hollow_', 'drowned_', 'pale_', 'scarlet_', 'rift_', 'spore_shrine', 'fungal_')
MAX_Y = {'skyreach': 256, 'clockwork': 256, 'hollow': 128, 'mycelial': 128}

SINGLE = ('chest', 'barrel', 'lantern', 'torch', 'candle', 'skull', '_head', 'campfire', 'flower_pot', 'lectern', 'bell', 'banner', '_sign',
          'button', 'lever', 'pressure_plate', 'sapling', 'coral_fan', 'cobweb', 'spawner', 'brewing_stand', 'anvil', 'cake', 'beacon',
          'enchanting_table', 'end_portal_frame', 'conduit', 'amethyst_cluster', '_bed', 'aurelia:', 'trapdoor', 'respawn_anchor', 'lodestone',
          'hopper', 'grindstone', 'stonecutter', 'loom', 'smithing_table', 'cartography_table', 'fletching_table', 'composter', 'cauldron',
          'decorated_pot', 'turtle_egg', 'frogspawn', 'glow_lichen', 'hanging_roots', 'spore_blossom', 'tulip', 'cave_vines', 'twisting_vines',
          'weeping_vines', 'sea_pickle')
PLANTS = {'grass', 'tall_grass', 'fern', 'large_fern', 'dead_bush', 'poppy', 'dandelion', 'allium', 'blue_orchid', 'azure_bluet', 'oxeye_daisy',
          'cornflower', 'lily_of_the_valley', 'red_mushroom', 'brown_mushroom', 'crimson_roots', 'warped_roots', 'nether_sprouts', 'azalea',
          'flowering_azalea', 'vine', 'kelp', 'kelp_plant', 'seagrass', 'tall_seagrass', 'sunflower', 'lilac', 'rose_bush', 'peony', 'wither_rose',
          'torchflower', 'pink_petals', 'lily_pad', 'sweet_berry_bush', 'crimson_fungus', 'warped_fungus', 'small_dripleaf', 'big_dripleaf'}
POSTS = ('fence', '_wall', 'iron_bars', 'glass_pane', 'chain', 'end_rod', 'lightning_rod', 'pointed_dripstone', 'ladder', 'scaffolding')


def kind(name):
    n = name.split(':', 1)[1] if name.startswith('minecraft:') else name
    if name in (AIR, 'minecraft:cave_air', 'minecraft:void_air', 'minecraft:water', 'minecraft:lava'):
        return 'fill'
    if '_slab' in n:
        return 'slab'
    if '_stairs' in n:
        return 'stairs'
    if n.endswith('_door'):
        return 'door'
    if 'carpet' in n or n in ('snow', 'moss_carpet'):
        return 'carpet'
    if any(k in n for k in POSTS) and 'wall_banner' not in n and 'wall_sign' not in n and 'wall_torch' not in n:
        return 'post'
    if n in PLANTS or any(k in name for k in SINGLE):
        return 'single'
    return 'fill'


def load_core(name):
    t = nbtlib.load(os.path.join(CORES, name + '.nbt'))
    W, H, L = [int(v) for v in t['size']]
    g = Grid(W, H, L)
    pal = [(str(p['Name']), tuple(sorted((str(k), str(v)) for k, v in p.get('Properties', {}).items()))) for p in t['palette']]
    for b in t['blocks']:
        x, y, z = (int(v) for v in b['pos'])
        nm, props = pal[int(b['state'])]
        g.b[(x, y, z)] = (nm, props, b['nbt'] if 'nbt' in b else None)
    g.entities = list(t['entities'])
    return g


def doubled(core):
    out = Grid(core.W * 2, core.H * 2, core.L * 2)
    b = out.b
    for (x, y, z), (nm, props, nbt) in core.b.items():
        k = kind(nm)
        X, Y, Z = 2 * x, 2 * y, 2 * z
        cells = [(X + i, Y + j, Z + m) for i in (0, 1) for j in (0, 1) for m in (0, 1)]
        pd = dict(props)
        if k == 'fill':
            for c in cells:
                b[c] = (nm, props, nbt)
        elif k == 'slab':
            t = pd.get('type', 'bottom')
            full = (nm, tuple(sorted(dict(pd, type='double').items())), None)
            for c in cells:
                lower = c[1] == Y
                b[c] = full if t == 'double' or (t == 'bottom') == lower else (AIR, (), None)
        elif k == 'stairs':
            f, half = pd.get('facing', 'north'), pd.get('half', 'bottom')
            back = {'north': lambda c: c[2] == Z, 'south': lambda c: c[2] == Z + 1, 'west': lambda c: c[0] == X, 'east': lambda c: c[0] == X + 1}[f]
            for c in cells:
                base_layer = (c[1] == Y) if half == 'bottom' else (c[1] == Y + 1)
                b[c] = (nm, props, None) if base_layer or back(c) else (AIR, (), None)
        elif k == 'door':
            if pd.get('half') == 'lower':
                b[(X, Y, Z)] = (nm, props, None)
                b[(X, Y + 1, Z)] = (nm, tuple(sorted(dict(pd, half='upper').items())), None)
                for c in cells:
                    b.setdefault(c, (AIR, (), None))
            else:
                for c in cells:
                    b.setdefault(c, (AIR, (), None))
        elif k == 'carpet':
            for c in cells:
                b[c] = (nm, props, None) if c[1] == Y else (AIR, (), None)
        elif k == 'post':
            for c in cells:
                b[c] = (nm, props, None)
        else:                                                            # single: once, in the corner, the rest left open
            for c in cells:
                b.setdefault(c, (AIR, (), None))
            b[(X, Y, Z)] = (nm, props, nbt)
    for e in core.entities:
        ent = Compound(e)
        pos = [float(v) for v in e['pos']]
        ent['pos'] = List[Double]([Double(pos[0] * 2), Double((pos[1]) * 2), Double(pos[2] * 2)])
        bp = [int(v) for v in e['blockPos']]
        X, Y, Z = bp[0] * 2, bp[1] * 2, bp[2] * 2
        for _ in range(2):                                               # the corner it stood on was left open: step down onto it
            if Y > 0 and b.get((X, Y - 1, Z), (AIR,))[0] in (AIR, 'minecraft:cave_air'):
                Y -= 1
        ent['pos'] = List[Double]([Double(pos[0] * 2), Double(pos[1] * 2 - (bp[1] * 2 - Y)), Double(pos[2] * 2)])
        ent['blockPos'] = List[Int]([Int(X), Int(Y), Int(Z)])
        out.entities.append(ent)
    return out


def names():
    """The templates small enough to double (already-vast ones, the sky castle, the great islands, the grove pillars and the
    ziggurats, stay as they are)."""
    out = []
    for n in sorted(os.listdir(CORES)):
        if not n.endswith('.nbt'):
            continue
        w, h, l = [int(v) for v in nbtlib.load(os.path.join(CORES, n))['size']]
        if max(w, l) <= 52 and h <= 70:
            out.append(n[:-4])
    return out


def save_cores():
    """The first time: keep the current templates as the originals."""
    os.makedirs(CORES, exist_ok=True)
    for n in os.listdir(STRUCT):
        if n.endswith('.nbt') and n.startswith(PREFIXES) and not os.path.exists(os.path.join(CORES, n)):
            os.system(f'cp "{STRUCT}/{n}" "{CORES}/{n}"')


def placement():
    """Each structure that places these templates: sink surface pieces twice as deep, hang stalactites from the same ceiling,
    keep sky pieces inside the world, give the bigger pieces room, and space their sets a little wider."""
    side_p = os.path.join(CORES, 'placement.json')
    side = json.load(open(side_p)) if os.path.exists(side_p) else {}
    sizes = {}
    for n in names():
        t = nbtlib.load(os.path.join(CORES, n + '.nbt'))
        sizes[n] = [int(v) for v in t['size']]
    for f in sorted(os.listdir(WG + '/structure')):
        sname = f[:-5]
        j = json.load(open(f'{WG}/structure/{f}'))
        pool = j['start_pool'].split(':')[1].split('/')[0]
        pj = json.load(open(f'{WG}/template_pool/{pool}/start.json')) if os.path.exists(f'{WG}/template_pool/{pool}/start.json') else None
        if pj is None:
            continue
        templates = [e['element']['location'].split(':')[1] for e in pj['elements'] if 'location' in e['element']]
        if not templates or not all(t in sizes for t in templates):
            continue
        H = max(sizes[t][1] for t in templates)
        Wd = max(max(sizes[t][0], sizes[t][2]) for t in templates)
        rec = side.setdefault(sname, {'start_height': j['start_height']})
        sh = rec['start_height']
        if 'absolute' in sh and j.get('project_start_to_heightmap'):
            j['start_height'] = {'absolute': sh['absolute'] * 2}
        elif sname == 'hollow_stalactites':
            j['start_height'] = {'absolute': sh['absolute'] - H}
        elif sh.get('type') == 'minecraft:uniform':
            realm = 'skyreach' if sname.startswith('skyreach') else 'clockwork' if sname.startswith('rift') else \
                'hollow' if sname.startswith('hollow') else 'mycelial' if sname.startswith('mycelial') else None
            top = MAX_Y.get(realm, 300) - 2 * H - 2
            lo, hi = sh['min_inclusive']['absolute'], sh['max_inclusive']['absolute']
            hi2 = max(lo, min(hi, top))
            j['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': min(lo, hi2)}, 'max_inclusive': {'absolute': hi2}}
        if Wd > 80:
            j['max_distance_from_center'] = 116  # +12 terrain adaptation must stay <= 128
        json.dump(j, open(f'{WG}/structure/{f}', 'w'), indent=2)
        sp = f'{WG}/structure_set/{sname}.json'
        if os.path.exists(sp):
            s = json.load(open(sp))
            pl = s['placement']
            orig_pl = rec.setdefault('spacing', [pl['spacing'], pl['separation']])
            pl['spacing'] = max(orig_pl[0], int(orig_pl[0] * 1.4))
            pl['separation'] = min(pl['spacing'] - 1, max(orig_pl[1], int(orig_pl[1] * 1.5)))
            json.dump(s, open(sp, 'w'), indent=2)
    json.dump(side, open(side_p, 'w'), indent=1)


def main(only=None):
    save_cores()
    for n in only or names():
        g = doubled(load_core(n))
        import enrich
        enrich.enrich(g, n, light=True)                                  # a fresh, light dressing at the new scale
        was = gen_citadels2.ENRICH
        gen_citadels2.ENRICH = False
        try:
            g.save(n)
        finally:
            gen_citadels2.ENRICH = was
    if not only:
        placement()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
