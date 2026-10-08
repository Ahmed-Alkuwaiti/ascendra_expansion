"""Dungeons: one great explorable structure for every biome of every realm, in the spirit of End Cities, Bastions and When Dungeons
Arise. Each is many rooms on many floors, joined by doors, stairs and ladders, held by a garrison of its realm's guards and by
spawners, with chests of six kinds whose loot rises with the realm:

  supply    food, torches, arrows, rope and the realm's food            armory    enchanted gear, now and then a realm tool or armour piece
  library   enchanted books, bottles of experience, lapis                alchemy   potions fit for the realm, golden apples, brewing goods
  treasure  gold, emeralds, diamonds, the realm's metal and material    vault     one per dungeon, at the end: the best of the lot

Tier runs from 1 (the Gaudy Grove) to 8 (the Mycelial Deep): enchantment levels, counts and rare drops climb with it, so a dungeon is
always worth the trip for someone at that point in the quest without handing out the next realm's gear.

  grove      Thornborn Spire (a vine-choked tower keep)      Blossom Sanctum (a terraced temple)       Rotwood Manor (a sprawling ruin)
  skyreach   Aviary Citadel (a floating tower-nest)          Sky Galleon (an airship)                  Thunder Temple (a lightning shrine)
  hollow     Ember Bastion (a walled black fortress)          Soul Prison (cellblocks round a pit)      Scorched Foundry (a forge-works)
  drowned    Drowned Keep (a half-sunk castle)               Kraken Galleon (a sunken warship)          Coral Cathedral
  pale       Frostbound Keep                                  Glacier Vault (halls cut into ice)         Hunter's Hall (a fortified longhouse)
  scarlet    Sunken Pyramid                                   Glassworks (furnace towers)                Ossuary Coliseum
  clockwork  The Great Clocktower                             Mechanical Nest (gear-works)               Hourglass Vault
  mycelial   Fungal Hive                                      Glowcap Village (mushroom houses)          Rootbound Asylum

Writes the templates, each one's structure, set, pool and biome tag, and the loot tables.
"""
import json
import math
import os
import random

from nbtlib import Compound, Short, String

import gen_citadels2
import paths
from gen_act3_citadels import AIR
from gen_landmarks import AX, BONE, CHAIN, B, fire, lantern

D = paths.RES + '/data/aurelia'
WG = D + '/worldgen'
REALMS = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']
TIER = {r: i + 1 for i, r in enumerate(REALMS)}
GUARDS = {'grove': ['bramble_sentinel', 'sporecap', 'rootstalker'], 'skyreach': ['calcite_sentinel', 'calcite_sentinel', 'storm_wisp'],
          'hollow': ['ashbound_knight', 'soul_jailer', 'cinder_hound'], 'drowned': ['coralclad_juggernaut', 'tidecaller', 'razorclaw'],
          'pale': ['rimeguard', 'hushwraith', 'rimefang'], 'scarlet': ['sandglass_sentinel', 'sunseer', 'glasswing_scarab'],
          'clockwork': ['hour_warden', 'secondhand', 'gearskitter'], 'mycelial': ['husk_guard', 'root_grub', 'spore_drifter']}
SPAWNS = {'grove': ['minecraft:spider', 'minecraft:zombie'], 'skyreach': ['minecraft:skeleton', 'minecraft:stray'],
          'hollow': ['minecraft:blaze', 'minecraft:wither_skeleton'], 'drowned': ['minecraft:drowned', 'minecraft:guardian'],
          'pale': ['minecraft:stray', 'minecraft:skeleton'], 'scarlet': ['minecraft:husk', 'minecraft:cave_spider'],
          'clockwork': ['minecraft:silverfish', 'minecraft:vindicator'], 'mycelial': ['minecraft:cave_spider', 'minecraft:zombie']}
FLYERS = {'storm_wisp', 'gale_talon', 'spore_drifter'}


# ================================================================================================ loot
def item(name, w, lo=1, hi=1, fns=()):
    e = {'type': 'minecraft:item', 'name': name, 'weight': w}
    f = list(fns)
    if hi > 1:
        f.insert(0, {'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}})
    if f:
        e['functions'] = f
    return e


def ench(lo, hi, treasure=False):
    return {'function': 'minecraft:enchant_with_levels', 'levels': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}, 'treasure': treasure}


def potion(pid, kind='minecraft:potion', w=4):
    return item(kind, w, fns=[{'function': 'minecraft:set_potion', 'id': f'minecraft:{pid}'}])


def table(rolls, entries, extra_pools=()):
    return {'type': 'minecraft:chest', 'pools': [{'rolls': {'type': 'minecraft:uniform', 'min': rolls[0], 'max': rolls[1]}, 'bonus_rolls': 0,
                                                  'entries': entries}] + list(extra_pools)}


ELEMENT_POTION = {'grove': 'regeneration', 'skyreach': 'slow_falling', 'hollow': 'fire_resistance', 'drowned': 'water_breathing', 'pale': 'night_vision',
                  'scarlet': 'fire_resistance', 'clockwork': 'swiftness', 'mycelial': 'regeneration'}


def loot_tables():
    from kit_data import ARSENAL, KIT
    ARMOR = {'grove': 'verdant', 'skyreach': 'stormglass', 'hollow': 'emberheart', 'drowned': 'tidestone', 'pale': 'rime', 'scarlet': 'sunglass',
             'clockwork': 'chronite', 'mycelial': 'bloomspore'}
    out = {}
    for realm in REALMS:
        t = TIER[realm]
        a, k = ARSENAL[realm], KIT[realm]
        metal, special, tool, food = f'aurelia:{a["metal"]}', f'aurelia:{a["special"]}', a['tool'], f'aurelia:{k["food"]}'
        gear = 'diamond' if t >= 4 else 'iron'
        lv = (8 + 3 * t, 16 + 3 * t)                                    # enchantment levels climb with the realm, topping out at 40
        out['supply'] = table((4, 8), [
            item('minecraft:bread', 10, 2, 5), item('minecraft:cooked_beef' if t % 2 else 'minecraft:cooked_mutton', 10, 2, 6), item(food, 8, 2, 6),
            item('minecraft:golden_carrot', 3 + t, 1, 4), item('minecraft:torch', 8, 6, 16), item('minecraft:arrow', 8, 6, 20),
            item('minecraft:string', 6, 2, 8), item('minecraft:leather', 5, 1, 4), item('minecraft:coal', 6, 3, 10),
            item('minecraft:iron_ingot', 6, 2, 6), item('minecraft:lead', 2), item('minecraft:saddle', 1), item('minecraft:name_tag', 1)])
        out['armory'] = table((2, 5), [
            item(f'minecraft:{gear}_sword', 6, fns=[ench(*lv)]), item(f'minecraft:{gear}_pickaxe', 5, fns=[ench(*lv)]),
            item(f'minecraft:{gear}_chestplate', 4, fns=[ench(*lv)]), item(f'minecraft:{gear}_helmet', 4, fns=[ench(*lv)]),
            item(f'minecraft:{gear}_leggings', 4, fns=[ench(*lv)]), item(f'minecraft:{gear}_boots', 4, fns=[ench(*lv)]),
            item('minecraft:bow', 5, fns=[ench(*lv)]), item('minecraft:crossbow', 4, fns=[ench(*lv)]), item('minecraft:shield', 4),
            item('minecraft:arrow', 6, 8, 24), item(f'aurelia:{tool}_pickaxe', 2), item(f'aurelia:{tool}_axe', 2),
            item(f'aurelia:{ARMOR[realm]}_helmet', 1), item(f'aurelia:{ARMOR[realm]}_boots', 1), item(metal, 5, 1, 3)])
        out['library'] = table((3, 6), [
            item('minecraft:book', 10, fns=[ench(*lv)]), item('minecraft:book', 3, fns=[ench(lv[0] + 4, lv[1] + 4, True)]),
            item('minecraft:experience_bottle', 8, 2, 4 + t), item('minecraft:lapis_lazuli', 8, 3, 10), item('minecraft:paper', 6, 3, 9),
            item('minecraft:bookshelf', 3, 1, 3), item('minecraft:ink_sac', 4, 1, 4), item('minecraft:map', 2), item('aurelia:aurelian_bestiary', 1)])
        out['alchemy'] = table((3, 6), [
            potion('healing', w=6), potion('strong_healing' if t >= 4 else 'healing', 'minecraft:splash_potion', 4), potion(ELEMENT_POTION[realm], w=6),
            potion('strength' if t < 5 else 'long_strength', w=3), potion('regeneration', w=3), potion('night_vision', w=2),
            item('minecraft:nether_wart', 5, 2, 6), item('minecraft:glistering_melon_slice', 4, 1, 3), item('minecraft:blaze_powder', 3, 1, 3),
            item('minecraft:glowstone_dust', 4, 2, 6), item('minecraft:golden_apple', 2 + t // 2), item('minecraft:ghast_tear', max(0, t - 4) or 1),
            item('minecraft:brewing_stand', 1)])
        out['treasure'] = table((4, 7), [
            item('minecraft:gold_ingot', 10, 3, 8 + t), item('minecraft:emerald', 8, 2, 4 + t), item('minecraft:diamond', 3 + t // 2, 1, 1 + t // 2),
            item(metal, 8, 2, 4 + t // 2), item(special, 3, 1, 2), item('minecraft:amethyst_shard', 5, 2, 8), item('minecraft:iron_block', 3, 1, 2),
            item('minecraft:gold_block', 1 + t // 3, 1, 2), item('minecraft:netherite_scrap', max(1, t - 4) if t >= 5 else 0 or 1),
            item('minecraft:golden_horse_armor' if t < 4 else 'minecraft:diamond_horse_armor', 2)])
        vault = [item(metal, 10, 4, 8 + t), item(special, 6, 1, 3), item('minecraft:diamond', 8, 2, 3 + t // 2),
                 item('minecraft:golden_apple', 6, 1, 3), item('minecraft:book', 6, fns=[ench(lv[1], lv[1] + 8, True)]),
                 item(f'aurelia:{k["weapon"]}', 2), item(f'aurelia:{ARMOR[realm]}_chestplate', 2), item(f'aurelia:{ARMOR[realm]}_leggings', 2),
                 item('minecraft:totem_of_undying', 1 + t // 3), item('minecraft:music_disc_pigstep' if realm == 'hollow' else 'minecraft:music_disc_otherside', 1)]
        if t >= 5:
            vault += [item('minecraft:netherite_scrap', t - 3, 1, 2), item('minecraft:enchanted_golden_apple', 1)]
        if t >= 7:
            vault += [item('minecraft:netherite_upgrade_smithing_template', 2), item('minecraft:diamond_block', 2)]
        out['vault'] = table((5, 8), vault, [{'rolls': 1, 'bonus_rolls': 0, 'entries': [item(metal, 1, 2, 4)]}])
        for kind, tbl in out.items():
            for pool in tbl['pools']:
                pool['entries'] = [e for e in pool['entries'] if e['weight'] > 0]
            p = f'{D}/loot_tables/chests/dungeon/{realm}_{kind}.json'
            os.makedirs(os.path.dirname(p), exist_ok=True)
            json.dump(tbl, open(p, 'w'), indent=2)


# ================================================================================================ the builder
def spawner_nbt(eid):
    return Compound({'id': String('minecraft:mob_spawner'), 'SpawnData': Compound({'entity': Compound({'id': String(eid)})}), 'Delay': Short(20),
                     'MinSpawnDelay': Short(240), 'MaxSpawnDelay': Short(800), 'SpawnCount': Short(2), 'MaxNearbyEntities': Short(5),
                     'RequiredPlayerRange': Short(14), 'SpawnRange': Short(3)})


FACE = {(0, -1): 'north', (0, 1): 'south', (1, 0): 'east', (-1, 0): 'west'}


class Dun(B):
    def __init__(self, realm, W, H, L, pal, seed):
        super().__init__(W, H, L, seed)
        self.realm = realm
        self.p = pal
        self.chests = []
        self.entrance = None
        self.pending = []

    def blk(self, key):
        v = self.p[key]
        if isinstance(v, list):                                         # a list is a mix, chosen per block
            return lambda x, y, z: v[int(((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) % 1000 / 1000.0 * len(v))]
        return v

    def pick(self, key, x, y, z):
        v = self.blk(key)
        return v(x, y, z) if callable(v) else v

    # ---------------------------------------------------------------- the pieces
    def shell(self, x0, y0, z0, x1, y1, z1, wall='wall', floor='floor', ceil='floor'):
        """A room: walls, a floor at y0 and a ceiling at y1, the inside cleared."""
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    edge = x in (x0, x1) or z in (z0, z1)
                    if y == y0:
                        self.put(x, y, z, self.pick(floor, x, y, z))
                    elif y == y1:
                        self.put(x, y, z, self.pick(ceil, x, y, z))
                    elif edge:
                        corner = x in (x0, x1) and z in (z0, z1)
                        self.put(x, y, z, self.pick('pillar' if corner else wall, x, y, z))
                    else:
                        self.put(x, y, z, AIR)

    def door(self, x, y, z, along_x, w=1, h=3):
        for d in range(-w // 2 + (1 if w % 2 == 0 else 0), w // 2 + 1):
            for k in range(h):
                self.put(x + (d if along_x else 0), y + k, z + (0 if along_x else d), AIR)

    def windows(self, x0, z0, x1, z1, y, every=4):
        for x in range(x0 + 2, x1 - 1, every):
            for z in (z0, z1):
                self.put(x, y, z, self.p['glass'])
                self.put(x, y + 1, z, self.p['glass'])
        for z in range(z0 + 2, z1 - 1, every):
            for x in (x0, x1):
                self.put(x, y, z, self.p['glass'])
                self.put(x, y + 1, z, self.p['glass'])

    def ladder(self, x, z, y0, y1, n):
        """A ladder from y0 to y1 at (x, z), against the wall on the side opposite n (n points into the room)."""
        for y in range(y0, y1 + 1):
            self.put(x, y, z, 'minecraft:ladder', {'facing': FACE[n], 'waterlogged': 'false'})
            self.put(x - n[0], y, z - n[1], self.pick('wall', x, y, z), over=True)
        self.put(x + n[0], y1 + 1, z + n[1], AIR)                       # room to step off at the top

    def flight(self, x, y, z, dx, dz, steps, block='floor', width=2):
        """A straight stair of solid steps climbing one block per step, headroom cleared above."""
        sx, sz = (-dz, dx)
        for i in range(steps):
            for w in range(width):
                px, pz = x + dx * i + sx * w, z + dz * i + sz * w
                self.put(px, y + i, pz, self.pick(block, px, y + i, pz))
                for k in range(1, 4):
                    self.put(px, y + i + k, pz, AIR)

    def battlements(self, x0, z0, x1, z1, y, key='wall'):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or z in (z0, z1):
                    self.put(x, y, z, self.pick(key, x, y, z))
                    if (x + z) % 2 == 0:
                        self.put(x, y + 1, z, self.pick(key, x, y, z))

    def roof(self, x0, z0, x1, z1, y, key='roof', along_x=True):
        span = (z1 - z0) if along_x else (x1 - x0)
        for k in range(span // 2 + 2):
            for i in range((x0 if along_x else z0) - 1, (x1 if along_x else z1) + 2):
                for s in (k, span - k):
                    x, z = (i, z0 + s) if along_x else (x0 + s, i)
                    self.put(x, y + k, z, self.pick(key, x, y + k, z))

    def cone(self, cx, cz, r, y, h, key='roof'):
        for k in range(h):
            rr = r * (1 - k / h) + 0.3
            for x in range(int(cx - rr) - 1, int(cx + rr) + 2):
                for z in range(int(cz - rr) - 1, int(cz + rr) + 2):
                    if math.hypot(x - cx, z - cz) <= rr:
                        self.put(x, y + k, z, self.pick(key, x, y + k, z))

    def hang(self, x, y, z, length=2):
        for k in range(length):
            self.put(x, y - k, z, CHAIN)
        self.put(x, y - length, z, lantern(self.p.get('soul', False), True))

    def spawner(self, x, y, z, eid=None):
        eid = eid or self.rnd.choice(SPAWNS[self.realm])
        self.g.set(int(x), int(y), int(z), 'minecraft:spawner', None, spawner_nbt(eid))

    def loot(self, x, y, z, kind, facing='north'):
        from gen_act3_citadels import chest
        chest(self.g, int(x), int(y), int(z), f'aurelia:chests/dungeon/{self.realm}_{kind}', facing)
        self.chests.append((int(x), int(y), int(z), kind))

    def guards(self, x0, z0, x1, z1, y, n):
        """Queue guards for a room; they are stood in place once the whole dungeon is built, so nothing is laid over them."""
        for _ in range(n):
            eid = self.rnd.choice(GUARDS[self.realm])
            x, z = self.rnd.randint(x0 + 1, max(x0 + 1, x1 - 1)), self.rnd.randint(z0 + 1, max(z0 + 1, z1 - 1))
            self.pending.append((eid, x, y, z))

    def place_guards(self):
        for eid, x, y, z in self.pending:
            if eid in FLYERS:
                self.g.air_guard(f'aurelia:{eid}', x, y + 1, z)
            else:
                self.stand(f'aurelia:{eid}', x, z, y)
        self.pending = []

    def stand(self, eid, x, z, y):
        """Stand a guard on its own room's floor near (x, z): never on bars or a fence, never on the floor above."""
        for r in range(4):
            for dx in range(-r, r + 1):
                for dz in range(-r, r + 1):
                    if max(abs(dx), abs(dz)) != r:
                        continue
                    for yy in (y, y + 1, y - 1, y + 2):
                        under = self.g.get(x + dx, yy - 1, z + dz)
                        if under is None or not self.g.solid(x + dx, yy - 1, z + dz) or 'bars' in under[0] or 'fence' in under[0] or 'pane' in under[0]:
                            continue
                        if self.g.free(x + dx, yy, z + dz) and self.g.free(x + dx, yy + 1, z + dz):
                            self.g.add_entity(eid, x + dx, yy, z + dz)
                            return

    def furnish(self, x0, y, z0, x1, z1, kind, guards=1, spawner=False, facing='north'):
        """Dress a room for its purpose and set its chest against the back wall."""
        cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
        if kind == 'library':
            for x in range(x0 + 1, x1):
                for k in (1, 2):
                    self.put(x, y + k, z0 + 1, 'minecraft:bookshelf')
            self.put(cx, y + 1, cz, ('minecraft:lectern', {'facing': 'south', 'has_book': 'false', 'powered': 'false'}))
        elif kind == 'alchemy':
            self.put(x0 + 1, y + 1, z0 + 1, ('minecraft:brewing_stand', {'has_bottle_0': 'false', 'has_bottle_1': 'false', 'has_bottle_2': 'false'}))
            self.put(x1 - 1, y + 1, z0 + 1, ('minecraft:cauldron', None))
        elif kind == 'armory':
            self.put(x0 + 1, y + 1, z0 + 1, ('minecraft:anvil', {'facing': 'east'}))
            self.put(x1 - 1, y + 1, z0 + 1, ('minecraft:smithing_table', None))
            self.put(cx, y + 1, z0 + 1, ('minecraft:grindstone', {'face': 'floor', 'facing': 'north'}))
        elif kind == 'supply':
            for x in range(x0 + 1, min(x1, x0 + 4)):
                self.put(x, y + 1, z0 + 1, ('minecraft:barrel', {'facing': 'up', 'open': 'false'}))
        elif kind in ('treasure', 'vault'):
            for x in (x0 + 1, x1 - 1):
                self.put(x, y + 1, z0 + 1, self.p.get('accent', 'minecraft:gold_block'))
        self.loot(cx, y + 1, z0 + 1 if kind != 'library' else z0 + 2, kind, 'south')
        if spawner:
            self.spawner(cx, y + 1, z1 - 2 if z1 - z0 > 4 else cz)
        self.guards(x0, z0, x1, z1, y + 1, guards)
        self.hang(cx, self.top_of(cx, y, cz) - 1, cz)

    def top_of(self, x, y, z):
        for k in range(1, 12):
            c = self.g.get(x, y + k, z)
            if c is not None and c[0] != AIR:
                return y + k
        return y + 5

    def keep(self, x0, z0, x1, z1, y0, floors, fh=5, kinds=(), door_side='s', ladder_corner=(1, 1)):
        """A building of several floors, a ladder shaft in one corner, rooms furnished in order, battlements on top."""
        for f in range(floors):
            y = y0 + f * fh
            self.shell(x0, y, z0, x1, y + fh, z1)
            self.windows(x0, z0, x1, z1, y + 2)
            if f < len(kinds) and kinds[f]:
                self.furnish(x0 + 1, y, z0 + 1, x1 - 1, z1 - 1, kinds[f], guards=1 + f // 2, spawner=(f % 2 == 1))
        lx = x0 + 1 if ladder_corner[0] == 0 else x1 - 1
        lz = z0 + 1 if ladder_corner[1] == 0 else z1 - 1
        n = (0, 1) if ladder_corner[1] == 0 else (0, -1)
        self.ladder(lx, lz, y0 + 1, y0 + floors * fh, n)
        self.battlements(x0, z0, x1, z1, y0 + floors * fh + 1)
        cx, cz = (x0 + x1) // 2, (z0 + z1) // 2
        if door_side == 's':
            self.door(cx, y0 + 1, z1, True, 2)
            return (cx, y0 + 1, z1 + 1)
        if door_side == 'n':
            self.door(cx, y0 + 1, z0, True, 2)
            return (cx, y0 + 1, z0 - 1)
        if door_side == 'e':
            self.door(x1, y0 + 1, cz, False, 2)
            return (x1 + 1, y0 + 1, cz)
        self.door(x0, y0 + 1, cz, False, 2)
        return (x0 - 1, y0 + 1, cz)

    def tower(self, cx, cz, r, y0, floors, fh=5, kinds=(), cap='cone'):
        """A round tower of several floors, a ladder up the inside, a door to the south."""
        for f in range(floors):
            y = y0 + f * fh
            for x in range(int(cx - r) - 1, int(cx + r) + 2):
                for z in range(int(cz - r) - 1, int(cz + r) + 2):
                    d = math.hypot(x - cx, z - cz)
                    if d > r:
                        continue
                    for k in range(fh + 1):
                        if k == 0 or k == fh:
                            self.put(x, y + k, z, self.pick('floor', x, y + k, z))
                        elif d > r - 1.1:
                            self.put(x, y + k, z, self.pick('glass' if (k in (2, 3) and abs(x - cx) < 1) else 'wall', x, y + k, z))
                        else:
                            self.put(x, y + k, z, AIR)
            if f < len(kinds) and kinds[f]:
                rr = int(r) - 1
                self.furnish(int(cx - rr) + 1, y, int(cz - rr) + 1, int(cx + rr) - 1, int(cz + rr) - 1, kinds[f], guards=1, spawner=False)
        top = y0 + floors * fh
        self.ladder(int(cx), int(cz - r) + 1, y0 + 1, top if cap != 'cone' else y0 + (floors - 1) * fh, (0, 1))
        if cap == 'cone':
            self.cone(cx, cz, r + 1.5, top + 1, int(r * 2.2))
        else:
            self.battlements(int(cx - r), int(cz - r), int(cx + r), int(cz + r), top + 1)
        for zz in range(int(cz + r - 2), int(cz + r) + 1):            # through the whole thickness of the wall
            self.door(int(cx), y0 + 1, zz, True, 1)
        return (int(cx), y0 + 1, int(cz + r) + 1)

    def bridge(self, a, b, y, width=3, key='floor', rail='fence'):
        (x0, z0), (x1, z1) = a, b
        n = int(max(abs(x1 - x0), abs(z1 - z0)))
        for i in range(n + 1):
            x, z = x0 + (x1 - x0) * i / max(n, 1), z0 + (z1 - z0) * i / max(n, 1)
            for w in range(-(width // 2), width // 2 + 1):
                px, pz = (x, z + w) if abs(x1 - x0) >= abs(z1 - z0) else (x + w, z)
                self.put(px, y, pz, self.pick(key, int(px), y, int(pz)))
                for k in (1, 2, 3):
                    self.put(px, y + k, pz, AIR)
            for w in (-(width // 2) - 1, width // 2 + 1):
                px, pz = (x, z + w) if abs(x1 - x0) >= abs(z1 - z0) else (x + w, z)
                self.put(px, y + 1, pz, self.p.get('fence', 'minecraft:iron_bars'))

    def tunnel(self, a, b, y, width=3, key='floor'):
        """A passage from a to b (x, z) at standing level y: floor under it, three blocks of air over it."""
        (x0, z0), (x1, z1) = a, b
        n = int(max(abs(x1 - x0), abs(z1 - z0))) + 1
        for i in range(n + 1):
            x, z = x0 + (x1 - x0) * i / n, z0 + (z1 - z0) * i / n
            for dx in range(-(width // 2), width // 2 + 1):
                for dz in range(-(width // 2), width // 2 + 1):
                    self.put(x + dx, y - 1, z + dz, self.pick(key, int(x + dx), y - 1, int(z + dz)))
                    for k in range(3):
                        self.put(x + dx, y + k, z + dz, AIR)

    def plaza(self, x0, z0, x1, z1, y, key='floor', depth=8):
        for x in range(x0, x1 + 1):
            for z in range(z0, z1 + 1):
                for yy in range(y - depth, y + 1):
                    self.put(x, yy, z, self.pick(key if yy == y else 'found', x, yy, z))
                for k in range(1, 5):
                    self.put(x, y + k, z, AIR, over=False)


# ================================================================================================ palettes
def pal(**kw):
    base = dict(fence='minecraft:iron_bars', accent='minecraft:gold_block', soul=False)
    base.update(kw)
    return base


PAL = {
    'grove': pal(wall=['minecraft:mossy_stone_bricks', 'minecraft:stone_bricks', 'minecraft:mossy_cobblestone', 'minecraft:cracked_stone_bricks'],
                 floor=['minecraft:spruce_planks', 'minecraft:dark_oak_planks'], pillar=('minecraft:dark_oak_log', AX), roof='minecraft:dark_oak_planks',
                 glass='minecraft:lime_stained_glass_pane', found='minecraft:cobblestone', fence='minecraft:dark_oak_fence', accent='minecraft:moss_block'),
    'skyreach': pal(wall=['minecraft:quartz_bricks', 'minecraft:calcite', 'minecraft:smooth_quartz'], floor=['minecraft:birch_planks', 'minecraft:polished_diorite'],
                    pillar='minecraft:quartz_pillar', roof='minecraft:light_blue_terracotta', glass='minecraft:light_blue_stained_glass_pane',
                    found='minecraft:calcite', fence='minecraft:birch_fence', accent='minecraft:oxidized_copper'),
    'hollow': pal(wall=['minecraft:polished_blackstone_bricks', 'minecraft:cracked_polished_blackstone_bricks', 'minecraft:blackstone'],
                  floor=['minecraft:polished_basalt', 'minecraft:polished_blackstone'], pillar='minecraft:gilded_blackstone', roof='minecraft:nether_bricks',
                  glass='minecraft:iron_bars', found='minecraft:blackstone', fence='minecraft:nether_brick_fence', accent='minecraft:gilded_blackstone', soul=True),
    'drowned': pal(wall=['minecraft:prismarine_bricks', 'minecraft:dark_prismarine', 'minecraft:mossy_stone_bricks'], floor=['minecraft:dark_prismarine', 'minecraft:prismarine'],
                   pillar='minecraft:prismarine_bricks', roof='minecraft:dark_prismarine', glass='minecraft:cyan_stained_glass_pane', found='minecraft:stone',
                   fence='minecraft:iron_bars', accent='minecraft:sea_lantern'),
    'pale': pal(wall=['minecraft:packed_ice', 'minecraft:snow_block', 'minecraft:polished_diorite'], floor=['minecraft:spruce_planks', 'minecraft:packed_ice'],
                pillar=('minecraft:stripped_spruce_log', AX), roof='minecraft:spruce_planks', glass='minecraft:light_blue_stained_glass_pane', found='minecraft:stone',
                fence='minecraft:spruce_fence', accent='minecraft:blue_ice', soul=True),
    'scarlet': pal(wall=['minecraft:cut_red_sandstone', 'minecraft:red_sandstone', 'minecraft:smooth_red_sandstone'], floor=['minecraft:cut_red_sandstone', 'minecraft:red_terracotta'],
                   pillar='minecraft:chiseled_red_sandstone', roof='minecraft:orange_terracotta', glass='minecraft:red_stained_glass_pane',
                   found='minecraft:red_sandstone', fence='minecraft:iron_bars', accent='minecraft:gold_block'),
    'clockwork': pal(wall=['minecraft:deepslate_tiles', 'minecraft:polished_deepslate', 'minecraft:deepslate_bricks'], floor=['minecraft:polished_deepslate', 'minecraft:copper_block'],
                     pillar='minecraft:waxed_cut_copper', roof='minecraft:waxed_oxidized_cut_copper', glass='minecraft:purple_stained_glass_pane',
                     found='minecraft:deepslate', fence='minecraft:iron_bars', accent='minecraft:gold_block', soul=True),
    'mycelial': pal(wall=['minecraft:mushroom_stem', 'minecraft:bone_block', 'minecraft:pink_terracotta'], floor=['minecraft:mycelium', 'minecraft:brown_mushroom_block'],
                    pillar=('minecraft:bone_block', AX), roof='minecraft:red_mushroom_block', glass='minecraft:magenta_stained_glass_pane',
                    found='minecraft:dirt', fence='minecraft:iron_bars', accent='minecraft:shroomlight'),
}


def variant(realm, **kw):
    p = dict(PAL[realm])
    p.update(kw)
    return p


# ================================================================================================ the dungeons (G is the ground level)
G = 12


def thornborn_spire():
    d = Dun('grove', 56, 80, 56, PAL['grove'], 101)
    d.plaza(4, 4, 51, 51, G - 1, depth=10)
    d.entrance = d.keep(14, 14, 41, 41, G, 3, 6, kinds=('supply', 'armory', 'library'), door_side='s')
    d.tower(28, 28, 6, G + 18, 5, 5, kinds=('alchemy', None, 'treasure', None, 'vault'))
    for (x, z) in [(8, 8), (47, 8), (8, 47), (47, 47)]:
        d.tower(x, z, 3.5, G, 3, 5, kinds=(None, 'supply'), cap='cone')
    for k in range(40):                                                 # vines all over it
        x, y, z = d.rnd.randint(13, 42), d.rnd.randint(G + 2, G + 40), d.rnd.choice([13, 42])
        d.put(x, y, z, ('minecraft:vine', {'north': 'false', 'south': 'false', 'east': 'false', 'west': 'false', 'up': 'false',
                                            'south' if z == 42 else 'north': 'true'}), over=False)
    return d


def blossom_sanctum():
    p = variant('grove', wall=['minecraft:cherry_planks', 'minecraft:stripped_cherry_wood'], floor=['minecraft:cherry_planks', 'minecraft:moss_block'],
                pillar=('minecraft:cherry_log', AX), roof='minecraft:pink_terracotta', glass='minecraft:pink_stained_glass_pane', fence='minecraft:cherry_fence')
    d = Dun('grove', 60, 50, 60, p, 102)
    for k, (r, h) in enumerate([(27, 0), (21, 4), (15, 8)]):            # three terraces, a stair up the front of each
        d.plaza(30 - r, 30 - r, 30 + r, 30 + r, G - 1 + h, key='wall', depth=10 if k == 0 else h)
    for (r_next, h) in [(21, 0), (15, 4)]:
        d.flight(29, G + h, 30 + r_next + 4, 0, -1, 4, block='wall')
    d.entrance = (30, G, 58)
    d.keep(20, 20, 40, 40, G + 8, 2, 6, kinds=('library', 'vault'), door_side='s')
    d.roof(19, 19, 41, 41, G + 21)
    for (x, z) in [(8, 8), (52, 8), (8, 52), (52, 52)]:
        d.keep(x - 4, z - 4, x + 4, z + 4, G, 1, 5, kinds=(d.rnd.choice(['supply', 'alchemy', 'armory']),), door_side='s')
        d.roof(x - 5, z - 5, x + 5, z + 5, G + 6)
    return d


def rotwood_manor():
    p = variant('grove', wall=['minecraft:dark_oak_planks', 'minecraft:mossy_cobblestone', 'minecraft:stripped_dark_oak_log'], roof='minecraft:mossy_cobblestone',
                glass='minecraft:brown_stained_glass_pane')
    d = Dun('grove', 64, 40, 50, p, 103)
    d.plaza(2, 2, 61, 47, G - 1, depth=10)
    d.entrance = d.keep(4, 14, 30, 36, G, 2, 6, kinds=('supply', 'library'), door_side='s')
    d.keep(30, 8, 58, 42, G, 2, 6, kinds=('armory', 'alchemy'), door_side='w')
    d.door(30, G + 1, 24, False, 2)
    d.roof(3, 13, 31, 37, G + 13)
    d.keep(38, 18, 50, 30, G + 12, 1, 6, kinds=('vault',), door_side='s')
    for _ in range(60):                                                 # rot: holes in the walls and floors, moss creeping in
        x, y, z = d.rnd.randint(4, 58), d.rnd.randint(G + 2, G + 12), d.rnd.randint(8, 42)
        c = d.g.get(x, y, z)
        if c and c[0] not in ('minecraft:chest', 'minecraft:ladder', 'minecraft:spawner'):
            d.put(x, y, z, 'minecraft:moss_block' if d.rnd.random() < 0.5 else 'minecraft:cobweb')
    return d


def aviary_citadel():
    d = Dun('skyreach', 60, 90, 60, PAL['skyreach'], 201)
    T = 30
    d.island(30, 30, T - 1, 26, 'minecraft:grass_block', 'minecraft:calcite', depth=1.3)
    d.entrance = d.keep(18, 18, 42, 42, T, 2, 6, kinds=('supply', 'armory'), door_side='s')
    d.tower(30, 30, 7, T + 12, 4, 6, kinds=('library', 'alchemy', 'treasure', 'vault'), cap='flat')
    for k in range(16):                                                 # the nest on the crown: a ring of bone and dead wood
        a = k * math.pi / 8
        for j in range(3):
            x, z = 30 + 9.5 * math.cos(a + j * 0.1), 30 + 9.5 * math.sin(a + j * 0.1)
            d.put(x, T + 37 + j, z, BONE if (k + j) % 2 else ('minecraft:stripped_birch_log', AX))
    for (x, z) in [(11, 28), (49, 28)]:                                 # watchtowers either side of the keep, on the island
        d.tower(x, z, 3.5, T, 2, 6, kinds=('supply',), cap='cone')
    return d


def sky_galleon():
    p = variant('skyreach', wall=['minecraft:spruce_planks', 'minecraft:dark_oak_planks'], floor=['minecraft:spruce_planks'], pillar=('minecraft:spruce_log', AX),
                glass='minecraft:glass_pane', fence='minecraft:spruce_fence')
    d = Dun('skyreach', 70, 60, 30, p, 202)
    Z, Y = 15, 20
    for x in range(6, 64):                                              # the hull, tapering to bow and stern
        t = (x - 6) / 57
        half = 9 * math.sin(math.pi * min(1, t * 1.1)) ** 0.6 + 1
        for z in range(int(Z - half), int(Z + half) + 1):
            depth = int(7 * max(0.0, 1 - abs(z - Z) / max(half, 1)) ** 0.5)
            for y in range(Y - depth, Y + 1):
                d.put(x, y, z, 'minecraft:spruce_planks' if y < Y else 'minecraft:spruce_planks')
            if abs(z - Z) >= half - 1:
                for y in range(Y + 1, Y + 3):
                    d.put(x, y, z, 'minecraft:spruce_fence')
    d.keep(10, 9, 24, 21, Y, 2, 5, kinds=('supply', 'vault'), door_side='e')           # the stern castle
    d.keep(30, 10, 44, 20, Y - 6, 1, 6, kinds=('armory',), door_side='n')             # the hold, below deck
    d.ladder(31, 11, Y - 5, Y, (0, 1))
    for x0 in (26, 40, 52):                                             # masts and sails
        for y in range(Y + 1, Y + 26):
            d.put(x0, y, Z, ('minecraft:spruce_log', AX))
        for y in range(Y + 8, Y + 24):
            for z in range(Z - 7, Z + 8):
                d.put(x0 + 1, y, z, 'minecraft:white_wool' if (y + z) % 7 else 'minecraft:light_blue_wool')
    for k in range(4):                                                  # the gasbags that keep it up
        d.ball(20 + k * 12, Y + 32, Z, 6, 'minecraft:white_wool', ry=4, rz=6)
        for y in range(Y + 26, Y + 29):
            d.put(20 + k * 12, y, Z, CHAIN)
    d.loot(50, Y + 1, Z, 'treasure')
    d.loot(56, Y + 1, Z + 2, 'alchemy')
    d.guards(28, Z - 5, 60, Z + 5, Y + 1, 4)
    d.entrance = (60, Y + 1, Z)
    return d


def thunder_temple():
    p = variant('skyreach', wall=['minecraft:polished_deepslate', 'minecraft:deepslate_tiles'], floor=['minecraft:polished_deepslate', 'minecraft:oxidized_cut_copper'],
                pillar='minecraft:oxidized_copper', roof='minecraft:waxed_oxidized_cut_copper', glass='minecraft:light_blue_stained_glass_pane')
    d = Dun('skyreach', 60, 80, 60, p, 203)
    T = 28
    d.island(30, 30, T - 1, 27, 'minecraft:tuff', 'minecraft:deepslate', depth=1.4)
    d.entrance = d.keep(16, 16, 44, 44, T, 2, 7, kinds=('armory', 'library'), door_side='s')
    d.cone(30, 30, 18, T + 15, 14)
    for (x, z) in [(16, 16), (44, 16), (16, 44), (44, 44)]:
        for y in range(T + 1, T + 40):
            d.put(x, y, z, 'minecraft:oxidized_cut_copper' if y % 5 else 'minecraft:copper_block')
        d.put(x, T + 40, z, ('minecraft:lightning_rod', {'facing': 'up', 'powered': 'false', 'waterlogged': 'false'}))
    d.keep(24, 24, 36, 36, T + 15, 1, 6, kinds=('vault',), door_side='s')
    d.ladder(25, 35, T + 1, T + 15, (0, -1))
    d.keep(4, 26, 12, 34, T, 1, 5, kinds=('alchemy',), door_side='e')
    d.keep(48, 26, 56, 34, T, 1, 5, kinds=('treasure',), door_side='w')
    return d


def ember_bastion():
    d = Dun('hollow', 70, 50, 70, PAL['hollow'], 301)
    d.plaza(2, 2, 67, 67, G - 1, depth=12)
    for x in range(4, 66):                                              # the outer wall, 8 high, with a gate
        for z in range(4, 66):
            if x in (4, 5, 64, 65) or z in (4, 5, 64, 65):
                for y in range(G, G + 9):
                    d.put(x, y, z, d.pick('wall', x, y, z))
    d.door(35, G, 65, True, 4, 6)
    d.door(35, G, 64, True, 4, 6)
    d.entrance = (35, G, 67)
    d.keep(20, 20, 50, 46, G, 3, 6, kinds=('supply', 'armory', 'treasure'), door_side='s')
    d.keep(28, 26, 42, 40, G + 18, 1, 7, kinds=('vault',), door_side='s')
    for (x, z) in [(10, 10), (59, 10), (10, 59), (59, 59)]:
        d.tower(x, z, 4, G, 3, 5, kinds=('alchemy', None, 'library'), cap='flat')
    for _ in range(12):                                                 # lava pools in the bailey
        x, z = d.rnd.randint(8, 62), d.rnd.choice([d.rnd.randint(8, 16), d.rnd.randint(50, 60)])
        d.put(x, G - 1, z, 'minecraft:lava')
    return d


def soul_prison():
    d = Dun('hollow', 56, 50, 56, variant('hollow', floor=['minecraft:soul_soil', 'minecraft:polished_blackstone']), 302)
    d.plaza(2, 2, 53, 53, G - 1, depth=12)
    for f in range(3):                                                  # three rings of cells round an open pit
        y = G + f * 6
        d.shell(8, y, 8, 47, y + 6, 47)
        for x in range(16, 40):
            for z in range(16, 40):
                for k in range(0, 7):
                    d.put(x, y + k, z, AIR)
        for k in range(10):
            cx = 10 + k * 4
            for (z0, z1) in [(9, 14), (41, 46)]:
                for zz in (z0, z1):
                    pass
                d.box(cx, y + 1, z0, cx, y + 4, z1, 'minecraft:polished_blackstone_bricks')
                for zz in range(z0 + 1, z1):
                    pass
                d.box(cx + 1, y + 1, z1 if z0 == 9 else z0, cx + 3, y + 4, z1 if z0 == 9 else z0, ('minecraft:iron_bars', None))
        d.furnish(9, y, 17, 15, 38, ['supply', 'alchemy', 'library'][f], guards=2, spawner=True)
        d.furnish(40, y, 17, 46, 38, ['armory', 'treasure', 'vault'][f], guards=2, spawner=f > 0)
    for f in range(2):                                                  # ladders last, so no floor is laid over them
        d.ladder(10, 39, G + f * 6 + 1, G + (f + 1) * 6, (0, -1))
        d.ladder(45, 39, G + f * 6 + 1, G + (f + 1) * 6, (0, -1))
    d.door(8, G + 1, 27, False, 3)
    d.entrance = (6, G + 1, 27)
    for y in range(G - 6, G):                                           # the pit, full of soul fire
        for x in range(18, 38):
            for z in range(18, 38):
                d.put(x, y, z, AIR if y > G - 6 else 'minecraft:soul_sand')
    for x in range(19, 37, 3):
        d.put(x, G - 5, 19, ('minecraft:soul_fire', None))
    return d


def scorched_foundry():
    d = Dun('hollow', 64, 50, 50, variant('hollow', wall=['minecraft:bricks', 'minecraft:polished_basalt', 'minecraft:blackstone']), 303)
    d.plaza(2, 2, 61, 47, G - 1, depth=12)
    d.entrance = d.keep(6, 10, 40, 40, G, 2, 8, kinds=('supply', 'armory'), door_side='s')
    for x in range(8, 39, 6):                                           # furnaces and lava troughs along the floor
        d.put(x, G + 1, 12, ('minecraft:blast_furnace', {'facing': 'south', 'lit': 'true'}))
        d.put(x + 1, G, 20, 'minecraft:lava')
    for (x, z) in [(12, 6), (24, 6), (36, 6)]:
        d.column(x, z, 2, G, G + 32, 'minecraft:bricks')
        d.put(x, G + 32, z, fire(False))
    d.keep(42, 16, 58, 34, G, 3, 6, kinds=('alchemy', 'treasure', 'vault'), door_side='w')
    d.door(40, G + 1, 25, False, 2)
    return d


def drowned_keep():
    d = Dun('drowned', 60, 50, 60, PAL['drowned'], 401)
    d.plaza(4, 4, 55, 55, G - 1, depth=10)
    d.entrance = d.keep(14, 14, 46, 46, G, 3, 6, kinds=('supply', 'library', 'treasure'), door_side='s')
    d.keep(24, 24, 36, 36, G + 18, 2, 6, kinds=('alchemy', 'vault'), door_side='s')
    d.ladder(25, 35, G + 1, G + 18, (0, -1))
    for (x, z) in [(14, 14), (46, 14), (14, 46), (46, 46)]:
        d.tower(x, z, 4, G, 4, 5, kinds=(None, 'armory'), cap='flat')
    for _ in range(40):                                                 # kelp and pickles
        x, z = d.rnd.randint(4, 55), d.rnd.randint(4, 55)
        if d.g.get(x, G, z) is None:
            d.put(x, G, z, ('minecraft:sea_pickle', {'pickles': '2', 'waterlogged': 'true'}))
    return d


def kraken_galleon():
    p = variant('drowned', wall=['minecraft:dark_oak_planks', 'minecraft:stripped_dark_oak_log'], floor=['minecraft:dark_oak_planks'], pillar=('minecraft:dark_oak_log', AX),
                glass='minecraft:glass_pane', fence='minecraft:dark_oak_fence')
    d = Dun('drowned', 72, 40, 32, p, 402)
    Z, Y = 16, G + 6
    for x in range(4, 68):
        t = (x - 4) / 63
        half = 10 * math.sin(math.pi * min(1, t * 1.08)) ** 0.6 + 1
        tilt = int((x - 36) * 0.08)                                     # listing on the sea floor
        for z in range(int(Z - half), int(Z + half) + 1):
            depth = int(8 * max(0.0, 1 - abs(z - Z) / max(half, 1)) ** 0.5)
            for y in range(Y - depth + tilt, Y + 1 + tilt):
                d.put(x, y, z, 'minecraft:dark_oak_planks')
    d.keep(8, 9, 24, 23, Y, 2, 5, kinds=('treasure', 'vault'), door_side='e')
    d.keep(30, 9, 50, 23, Y - 7, 1, 6, kinds=('armory',), door_side='n')
    d.ladder(31, 10, Y - 6, Y, (0, 1))
    d.loot(56, Y + 1, Z, 'supply')
    d.loot(44, Y + 1, Z - 3, 'alchemy')
    for x0 in (30, 46):
        for y in range(Y + 1, Y + 14):
            d.put(x0 + (y - Y) * 0.4, y, Z, ('minecraft:dark_oak_log', AX))                 # broken masts
    for k in range(8):                                                  # the kraken's arms over the hull
        a = k * math.pi / 4
        path = [(36 + 18 * math.cos(a), G - 2, Z + 14 * math.sin(a)), (36 + 14 * math.cos(a), Y + 6, Z + 10 * math.sin(a)),
                (36 + 8 * math.cos(a + 0.5), Y + 10, Z + 6 * math.sin(a + 0.5))]
        d.tube(path, lambda s: 1.6 - 1.0 * s, lambda x, y, z, s: 'minecraft:purple_concrete' if (x + y + z) % 4 else 'minecraft:magenta_concrete')
    d.guards(30, Z - 5, 64, Z + 5, Y + 1, 4)
    d.entrance = (66, Y + 1, Z)
    return d


def coral_cathedral():
    p = variant('drowned', wall=['minecraft:brain_coral_block', 'minecraft:tube_coral_block', 'minecraft:prismarine_bricks', 'minecraft:dead_brain_coral_block'],
                pillar='minecraft:prismarine_bricks', glass='minecraft:light_blue_stained_glass_pane')
    d = Dun('drowned', 60, 60, 50, p, 403)
    d.plaza(2, 2, 57, 47, G - 1, depth=10)
    d.entrance = d.keep(8, 12, 52, 38, G, 2, 9, kinds=('library', 'supply'), door_side='s')
    d.roof(7, 11, 53, 39, G + 19, along_x=True)
    for x in (8, 52):
        d.tower(x, 25, 5, G, 5, 6, kinds=('alchemy', None, 'armory', None, 'treasure'), cap='cone')
    d.keep(24, 18, 36, 30, G + 19, 1, 6, kinds=('vault',), door_side='s')
    d.ladder(25, 29, G + 1, G + 19, (0, -1))
    return d


def frostbound_keep():
    d = Dun('pale', 60, 60, 60, PAL['pale'], 501)
    d.plaza(4, 4, 55, 55, G - 1, depth=10)
    d.entrance = d.keep(16, 16, 44, 44, G, 3, 6, kinds=('supply', 'armory', 'library'), door_side='s')
    d.roof(15, 15, 45, 45, G + 19)
    for (x, z) in [(9, 9), (51, 9), (9, 51), (51, 51)]:
        d.tower(x, z, 4, G, 5, 5, kinds=(None, 'alchemy' if x < 30 else 'treasure', None, None, 'vault' if (x, z) == (51, 51) else None), cap='cone')
    for _ in range(30):
        x, z = d.rnd.randint(4, 55), d.rnd.randint(4, 55)
        for j in range(d.rnd.randint(2, 6)):
            d.put(x, G + j, z, 'minecraft:packed_ice', over=False)
    return d


def glacier_vault():
    p = variant('pale', wall=['minecraft:packed_ice', 'minecraft:blue_ice', 'minecraft:packed_ice'], floor=['minecraft:packed_ice', 'minecraft:snow_block'],
                pillar='minecraft:blue_ice', glass='minecraft:blue_ice')
    d = Dun('pale', 60, 44, 60, p, 502)
    d.ball(30, G + 6, 30, 28, lambda x, y, z: 'minecraft:packed_ice' if (x + y * 3 + z) % 5 else 'minecraft:blue_ice', ry=14)   # the glacier
    d.entrance = d.keep(18, 10, 42, 26, G, 2, 6, kinds=('supply', 'alchemy'), door_side='s')
    d.keep(18, 26, 42, 50, G, 2, 6, kinds=('armory', 'library'), door_side='n')
    d.keep(24, 32, 36, 44, G - 7, 1, 6, kinds=('vault',), door_side='n')
    d.ladder(25, 33, G - 6, G, (0, 1))
    for z in range(48, 60):                                             # a tunnel out through the ice to the south
        for x in range(28, 32):
            for y in range(G + 1, G + 4):
                d.put(x, y, z, AIR)
            d.put(x, G, z, 'minecraft:packed_ice')
    for z in range(0, 11):
        for x in range(28, 32):
            for y in range(G + 1, G + 4):
                d.put(x, y, z, AIR)
            d.put(x, G, z, 'minecraft:packed_ice')
    d.loot(40, G + 1, 30, 'treasure')
    d.entrance = (30, G + 1, 0)
    return d


def hunters_hall():
    p = variant('pale', wall=['minecraft:spruce_planks', 'minecraft:stripped_spruce_log'], floor=['minecraft:spruce_planks'], roof='minecraft:dark_oak_planks')
    d = Dun('pale', 70, 40, 44, p, 503)
    d.plaza(2, 2, 67, 41, G - 1, depth=10)
    for x in range(3, 67, 2):                                           # a palisade
        for z in (3, 40):
            for y in range(G, G + 6):
                d.put(x, y, z, ('minecraft:spruce_log', AX))
    d.door(35, G, 40, True, 4, 6)
    d.entrance = (35, G, 42)
    d.keep(10, 12, 58, 30, G, 1, 8, kinds=('supply',), door_side='s')
    d.roof(9, 11, 59, 31, G + 8, along_x=True)
    d.keep(12, 14, 22, 28, G + 9, 1, 5, kinds=('armory',), door_side='e')
    d.keep(46, 14, 56, 28, G + 9, 1, 5, kinds=('vault',), door_side='w')
    d.ladder(13, 15, G + 1, G + 9, (0, 1))
    d.ladder(55, 15, G + 1, G + 9, (0, 1))
    d.loot(30, G + 1, 28, 'treasure', 'north')
    d.loot(40, G + 1, 28, 'alchemy', 'north')
    for x in range(14, 56, 6):                                          # antler trophies along the hall
        d.put(x, G + 6, 13, BONE)
        d.put(x - 1, G + 7, 13, BONE)
        d.put(x + 1, G + 7, 13, BONE)
    return d


def sunken_pyramid():
    d = Dun('scarlet', 70, 50, 70, PAL['scarlet'], 601)
    for k in range(12):                                                 # the stepped pyramid
        r = 33 - k * 2.6
        for x in range(int(35 - r), int(35 + r) + 1):
            for z in range(int(35 - r), int(35 + r) + 1):
                for y in range(G - 2 + k * 3, G + 1 + k * 3):
                    d.put(x, y, z, d.pick('wall', x, y, z))
    d.keep(20, 20, 50, 50, G, 2, 6, kinds=('supply', 'treasure'), door_side='s')
    for z in range(50, 70):                                             # the entrance passage
        for x in range(33, 37):
            for y in range(G + 1, G + 5):
                d.put(x, y, z, AIR)
            d.put(x, G, z, 'minecraft:cut_red_sandstone')
    d.entrance = (35, G + 1, 69)
    d.keep(28, 28, 42, 42, G - 8, 1, 7, kinds=('vault',), door_side='n')    # the burial vault beneath
    d.ladder(29, 29, G - 7, G, (0, 1))
    d.keep(4, 30, 14, 40, G, 1, 5, kinds=('armory',), door_side='e')
    d.keep(56, 30, 66, 40, G, 1, 5, kinds=('alchemy',), door_side='w')
    d.keep(30, 4, 40, 14, G, 1, 5, kinds=('library',), door_side='s')
    d.tunnel((15, 35), (22, 35), G + 1)
    d.tunnel((55, 35), (48, 35), G + 1)
    d.tunnel((35, 15), (35, 22), G + 1)
    return d


def glassworks():
    p = variant('scarlet', glass='minecraft:orange_stained_glass_pane', pillar='minecraft:gold_block')
    d = Dun('scarlet', 64, 70, 56, p, 602)
    d.plaza(2, 2, 61, 53, G - 1, depth=10)
    d.entrance = d.keep(8, 14, 40, 42, G, 2, 7, kinds=('supply', 'alchemy'), door_side='s')
    for (x, z, n) in [(48, 14, 4), (48, 40, 5), (24, 6, 3)]:
        d.tower(x, z, 5, G, n, 6, kinds=('armory', 'library', 'treasure', 'vault' if n == 5 else None, None), cap='cone')
    for k in range(12):                                                 # glass crystals bursting from the roof
        x, z = d.rnd.randint(10, 38), d.rnd.randint(16, 40)
        d.column(x, z, 1.2, G + 15, G + 15 + d.rnd.randint(4, 12), 'minecraft:red_stained_glass', taper=0.8)
    for x in range(10, 39, 7):
        d.put(x, G + 1, 16, ('minecraft:furnace', {'facing': 'south', 'lit': 'true'}))
    return d


def ossuary_coliseum():
    p = variant('scarlet', wall=['minecraft:bone_block', 'minecraft:smooth_sandstone', 'minecraft:cut_red_sandstone'], pillar=('minecraft:bone_block', AX))
    d = Dun('scarlet', 72, 40, 72, p, 603)
    d.plaza(2, 2, 69, 69, G - 1, depth=10)
    for x in range(72):                                                 # the ring of seating
        for z in range(72):
            dd = math.hypot(x - 36, z - 36)
            if 20 <= dd <= 33:
                top = G - 1 + int((dd - 20) * 0.9)
                for y in range(G - 1, top + 1):
                    d.put(x, y, z, d.pick('wall', x, y, z))
            if 33 < dd <= 34.5:
                for y in range(G, G + 15):
                    d.put(x, y, z, d.pick('wall', x, y, z) if (y - G) % 5 else ('minecraft:bone_block', AX))
    for z in range(30, 72):
        for x in range(33, 40):
            if math.hypot(x - 36, z - 36) > 19:
                for y in range(G, G + 5):
                    d.put(x, y, z, AIR)
                d.put(x, G - 1, z, 'minecraft:cut_red_sandstone')
    d.entrance = (36, G, 71)
    for k in range(6):                                                  # cells under the seating, each a room
        a = k * math.pi / 3                                              # turned so the entrance passage (due south) runs between two cells
        cx, cz = int(36 + 26 * math.cos(a)), int(36 + 26 * math.sin(a))
        d.keep(cx - 4, cz - 4, cx + 4, cz + 4, G, 1, 5, kinds=(['supply', 'armory', 'library', 'alchemy', 'treasure', 'vault'][k],),
               door_side='n' if cz > 36 else 's')
        dz = -5 if cz > 36 else 5
        d.tunnel((cx, cz + dz), (36 + 16 * math.cos(a), 36 + 16 * math.sin(a)), G + 1)
    d.spawner(36, G, 36)
    d.guards(26, 26, 46, 46, G, 5)
    return d


def great_clocktower():
    d = Dun('clockwork', 50, 100, 50, PAL['clockwork'], 701)
    T = 26
    d.island(25, 25, T - 1, 22, 'minecraft:deepslate_tiles', 'minecraft:deepslate', depth=1.2)
    d.entrance = d.keep(13, 13, 37, 37, T, 2, 6, kinds=('supply', 'armory'), door_side='s')
    d.keep(17, 17, 33, 33, T + 12, 6, 6, kinds=('library', None, 'alchemy', None, 'treasure', 'vault'), door_side='s')
    for (fx, fz, axis) in [(25, 16, 'n'), (25, 34, 's')]:               # clock faces on the tower
        cy = T + 40
        for i in range(-6, 7):
            for j in range(-6, 7):
                dd = math.hypot(i, j)
                if dd <= 6.5:
                    d.put(25 + i, cy + j, fz, 'minecraft:gold_block' if dd > 5.5 else 'minecraft:calcite')
        for t in range(5):
            d.put(25, cy + t, fz, 'minecraft:polished_blackstone')
            d.put(25 + t, cy, fz, 'minecraft:polished_blackstone')
    d.cone(25, 25, 10, T + 49, 16)
    return d


def mechanical_nest():
    d = Dun('clockwork', 64, 70, 64, variant('clockwork', wall=['minecraft:waxed_cut_copper', 'minecraft:deepslate_tiles', 'minecraft:waxed_exposed_cut_copper']), 702)
    T = 24
    d.island(32, 32, T - 1, 29, 'minecraft:polished_deepslate', 'minecraft:deepslate', depth=1.1)
    d.entrance = d.keep(20, 20, 44, 44, T, 2, 6, kinds=('armory', 'supply'), door_side='s')
    for (x, z) in [(10, 32), (54, 32), (32, 10), (32, 54)]:
        d.tower(x, z, 5, T, 3, 6, kinds=('alchemy', 'library', 'treasure') if x != 54 else ('treasure', None, 'vault'), cap='flat')
        d.bridge((x, z), (32, 32), T + 12, 3)
    for k in range(6):                                                  # gears turning on the walls
        a = k * math.pi / 3
        cx, cz = 32 + 13 * math.cos(a), 32 + 13 * math.sin(a)
        for i in range(-4, 5):
            for j in range(-4, 5):
                dd = math.hypot(i, j)
                ang = math.atan2(j, i)
                if dd <= 3 or (dd <= 4.4 and math.cos(ang * 8) > 0.3):
                    d.put(cx + i * -math.sin(a), T + 7 + j, cz + i * math.cos(a), 'minecraft:gold_block' if dd < 1.4 else 'minecraft:waxed_cut_copper')
    return d


def hourglass_vault():
    p = variant('clockwork', wall=['minecraft:amethyst_block', 'minecraft:calcite', 'minecraft:polished_deepslate'], glass='minecraft:purple_stained_glass_pane')
    d = Dun('clockwork', 56, 90, 56, p, 703)
    T = 30
    for y in range(T - 24, T + 46):                                     # an hourglass: two cones point to point, with a waist room
        k = abs(y - (T + 11)) / 35
        r = 4 + 20 * k
        for x in range(int(28 - r) - 1, int(28 + r) + 2):
            for z in range(int(28 - r) - 1, int(28 + r) + 2):
                dd = math.hypot(x - 28, z - 28)
                if r - 1.5 < dd <= r and (y < T or y > T + 22):
                    d.put(x, y, z, d.pick('wall', x, y, z))
    for x in range(4, 53):
        for z in range(4, 53):
            if math.hypot(x - 28, z - 28) <= 23:
                for y in range(T - 6, T):
                    d.put(x, y, z, 'minecraft:sand' if y == T - 1 else 'minecraft:calcite')
    d.entrance = d.keep(18, 18, 38, 38, T, 2, 6, kinds=('supply', 'library'), door_side='s')
    d.keep(20, 20, 36, 36, T + 12, 2, 6, kinds=('treasure', 'vault'), door_side='s')
    d.ladder(19, 37, T + 1, T + 12, (0, -1))
    d.keep(6, 24, 14, 32, T, 1, 5, kinds=('armory',), door_side='e')
    d.keep(42, 24, 50, 32, T, 1, 5, kinds=('alchemy',), door_side='w')
    return d


def fungal_hive():
    d = Dun('mycelial', 64, 56, 64, PAL['mycelial'], 801)
    d.plaza(2, 2, 61, 61, G - 1, depth=10)
    for (x, z, r, h, kinds) in [(32, 32, 9, 4, ('supply', 'library', 'treasure', 'vault')), (14, 16, 6, 2, ('alchemy', None)), (50, 16, 6, 2, ('armory', None)),
                                (16, 48, 6, 3, (None, 'supply', None)), (48, 48, 6, 3, ('treasure', None, None))]:
        e = d.tower(x, z, r, G, h, 6, kinds=kinds, cap='none')
        for xx in range(int(x - r - 4), int(x + r + 5)):                # a mushroom cap on every tower
            for zz in range(int(z - r - 4), int(z + r + 5)):
                dd = math.hypot(xx - x, zz - z)
                if dd <= r + 4:
                    d.put(xx, G + h * 6 + 1 + (1 if dd < r else 0), zz, 'minecraft:shroomlight' if (xx * zz) % 9 == 0 else 'minecraft:red_mushroom_block')
        if (x, z) == (32, 32):
            d.entrance = e
        else:
            d.bridge((x, z), (32, 32), G, 3)
    return d


def glowcap_village():
    d = Dun('mycelial', 64, 40, 64, variant('mycelial', roof='minecraft:brown_mushroom_block'), 802)
    d.plaza(2, 2, 61, 61, G - 1, key='floor', depth=10)
    kinds = ['supply', 'library', 'alchemy', 'armory', 'treasure', 'supply', 'alchemy', 'vault']
    for k in range(8):                                                  # mushroom houses round a glowing well
        a = k * math.pi / 4
        x, z = 32 + 20 * math.cos(a), 32 + 20 * math.sin(a)
        d.tower(x, z, 4.5, G, 1 if k < 7 else 2, 6, kinds=(kinds[k], None), cap='none')
        for xx in range(int(x - 8), int(x + 9)):
            for zz in range(int(z - 8), int(z + 9)):
                dd = math.hypot(xx - x, zz - z)
                hh = 7 if k < 7 else 13
                if dd <= 7:
                    d.put(xx, G + hh + (1 if dd < 4 else 0), zz, 'minecraft:shroomlight' if (xx + zz) % 7 == 0 else 'minecraft:brown_mushroom_block')
    for x in range(29, 36):
        for z in range(29, 36):
            d.put(x, G - 1, z, 'minecraft:water' if 30 <= x <= 34 and 30 <= z <= 34 else 'minecraft:bone_block')
    d.put(32, G - 2, 32, ('minecraft:pearlescent_froglight', AX))
    d.guards(14, 14, 50, 50, G, 5)
    d.spawner(32, G, 20)
    d.entrance = (32, G, 60)
    return d


def rootbound_asylum():
    p = variant('mycelial', wall=['minecraft:mud_bricks', 'minecraft:packed_mud', 'minecraft:mangrove_roots'], floor=['minecraft:rooted_dirt', 'minecraft:mud_bricks'],
                pillar=('minecraft:mangrove_log', AX), roof='minecraft:mud_bricks')
    d = Dun('mycelial', 64, 50, 50, p, 803)
    d.plaza(2, 2, 61, 47, G - 1, depth=10)
    d.entrance = d.keep(6, 8, 58, 26, G, 2, 6, kinds=('supply', 'alchemy'), door_side='s')
    d.keep(6, 26, 30, 44, G, 2, 6, kinds=('library', 'armory'), door_side='n')
    d.keep(34, 26, 58, 44, G, 2, 6, kinds=('treasure', 'vault'), door_side='n')
    for k in range(10):                                                 # roots strangling it
        a = d.rnd.uniform(0, 2 * math.pi)
        x0, z0 = 32 + 30 * math.cos(a), 25 + 22 * math.sin(a)
        d.tube([(x0, G - 3, z0), (32 + 18 * math.cos(a), G + 14, 25 + 12 * math.sin(a)), (32 + 6 * math.cos(a + 1), G + 16, 25 + 4 * math.sin(a + 1))],
               lambda s: 1.8 - s, ('minecraft:mangrove_log', AX))
    return d


# id: (biome, builder, realm, placement)
DUNGEONS = {
    'thornborn_spire': ('grove', thornborn_spire, 'surface'), 'blossom_sanctum': ('bloomwild', blossom_sanctum, 'surface'),
    'rotwood_manor': ('mossveil_thicket', rotwood_manor, 'surface'),
    'aviary_citadel': ('skyreach', aviary_citadel, 'sky'), 'sky_galleon': ('cloud_meadows', sky_galleon, 'sky'), 'thunder_temple': ('stormfront', thunder_temple, 'sky'),
    'ember_bastion': ('hollow', ember_bastion, 'cave'), 'soul_prison': ('soulfire_wastes', soul_prison, 'cave'), 'scorched_foundry': ('ember_deeps', scorched_foundry, 'cave'),
    'drowned_keep': ('drowned', drowned_keep, 'seafloor'), 'kraken_galleon': ('kelp_forest', kraken_galleon, 'seafloor'),
    'coral_cathedral': ('coral_graveyard', coral_cathedral, 'seafloor'),
    'frostbound_keep': ('pale', frostbound_keep, 'surface'), 'glacier_vault': ('frozen_spires', glacier_vault, 'surface'), 'hunters_hall': ('whisper_taiga', hunters_hall, 'surface'),
    'sunken_pyramid': ('scarlet', sunken_pyramid, 'surface'), 'glassworks': ('glass_dunes', glassworks, 'surface'), 'ossuary_coliseum': ('bone_flats', ossuary_coliseum, 'surface'),
    'great_clocktower': ('clockwork', great_clocktower, 'sky'), 'mechanical_nest': ('gearfields', mechanical_nest, 'sky'), 'hourglass_vault': ('stopped_hour', hourglass_vault, 'sky'),
    'fungal_hive': ('mycelial', fungal_hive, 'cave'), 'glowcap_village': ('glowcap_hollows', glowcap_village, 'cave'), 'rootbound_asylum': ('rootmaw', rootbound_asylum, 'cave'),
}
CAVE_Y = {'hollow': (33, 36), 'mycelial': (34, 50)}
SKY_Y = {'skyreach': (50, 110), 'clockwork': (70, 110)}


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(obj, open(path, 'w'), indent=2)


BUILT = {}


def main(only=None):
    loot_tables()
    for k, (did, (biome, fn, kind)) in enumerate(DUNGEONS.items()):
        if only and did not in only:
            continue
        d = fn()
        d.place_guards()
        BUILT[did] = d
        realm = d.realm
        was = gen_citadels2.ENRICH
        gen_citadels2.ENRICH = False
        try:
            import enrich
            enrich.enrich(d.g, f'dungeon:{realm}', light=True)
            d.g.save(f'dungeon_{did}')
        finally:
            gen_citadels2.ENRICH = was
        s = {'type': 'minecraft:jigsaw', 'biomes': f'#aurelia:has_structure/dungeon_{did}', 'step': 'surface_structures', 'terrain_adaptation': 'none',
             'start_pool': f'aurelia:dungeon_{did}/start', 'size': 1, 'max_distance_from_center': 80, 'use_expansion_hack': False, 'spawn_overrides': {}}
        if kind == 'surface':
            s['start_height'] = {'absolute': -G}
            s['project_start_to_heightmap'] = 'WORLD_SURFACE_WG'
            s['terrain_adaptation'] = 'beard_box'
        elif kind == 'seafloor':
            s['start_height'] = {'absolute': -G}
            s['project_start_to_heightmap'] = 'OCEAN_FLOOR_WG'
            s['terrain_adaptation'] = 'beard_thin'
        elif kind == 'cave':
            lo, hi = CAVE_Y[realm]
            s['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo - G}, 'max_inclusive': {'absolute': hi - G}}
            s['terrain_adaptation'] = 'beard_box'
        else:
            lo, hi = SKY_Y[realm]
            s['start_height'] = {'type': 'minecraft:uniform', 'min_inclusive': {'absolute': lo}, 'max_inclusive': {'absolute': hi}}
        dump(f'{WG}/structure/dungeon_{did}.json', s)
        dump(f'{WG}/structure_set/dungeon_{did}.json', {'structures': [{'structure': f'aurelia:dungeon_{did}', 'weight': 1}],
                                                        'placement': {'type': 'minecraft:random_spread', 'spacing': 26, 'separation': 10, 'salt': 91200000 + k}})
        dump(f'{WG}/template_pool/dungeon_{did}/start.json', {'fallback': 'minecraft:empty', 'elements': [
            {'weight': 1, 'element': {'element_type': 'minecraft:single_pool_element', 'location': f'aurelia:dungeon_{did}',
                                      'processors': {'processors': []}, 'projection': 'rigid'}}]})
        dump(f'{D}/tags/worldgen/biome/has_structure/dungeon_{did}.json', {'replace': False, 'values': [f'aurelia:{biome}']})
        print(f'   {did}: {len(d.chests)} chests ({", ".join(sorted(set(c[3] for c in d.chests)))}), {len(d.g.entities)} guards')


if __name__ == '__main__':
    import sys
    main(sys.argv[1:] or None)
