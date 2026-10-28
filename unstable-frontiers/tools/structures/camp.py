"""Expedition Camps: where Ilsa Vane's survey of the frontier stopped. Each camp holds a journal (lore and the clue
to what to hunt next), a map table, supplies, and the wreck of whatever went wrong: one is intact, one ransacked by
the swarm, one torn apart from above. The Great Cage is never named outright; the journals point at it.
"""
import math

from common import *
from kit import AIR, B, Build, h

JOURNALS = {
    'camp_intact': ('Survey Log, I', [
        'Ilsa Vane, surveyor.\n\nDay 2. The rift held. The land beyond is the old frontier the Cagewright fenced in: '
        'every tower here is a cage, and every cage was full.',
        'Day 4. Insects below, predators above. They meet where there is meat: the carrion fields. Stay downwind.',
        'Day 6. The towers wake when you step inside. Clear the crown and the vault opens. The trophies are the point: '
        'the Cagewright made keys from them.',
        'Day 9. A Rookery to the east. White rock below a nest of whole trees. The mother comes in from the sky.',
    ]),
    'camp_ransacked': ('Survey Log, II', [
        'Day 11. The hive took Bram. They do not eat you at once. They carry you down.',
        'Day 12. Their eggs hatch when the brood is threatened. Break the clutches first or you fight forever.',
        'Day 14. Under the throne there is a wall of resin. Something is sealed behind it. Only the Tyrant\'s death opens it.',
        'Day 15. Writing this in the dark. Something is digging up under the tents.',
    ]),
    'camp_torn': ('Survey Log, III', [
        'Day 20. Three keys: a cage trophy, a rookery talon, a hive heart. The Cagewright\'s own notes say so.',
        'Day 21. The scar where the bones turn red. The Great Cage stands in the middle of it, taller than anything here.',
        'Day 22. Four pylons hold the beast inside. While they stand, it cannot be hurt for long. Break them.',
        'Day 23. They came at night, from above. If you are reading this, take the lens and go on without us.',
    ]),
}


def camp(name):
    W, H, L = 29, 16, 29
    G = 2
    b = Build(name, W, H, L, seed=71 + len(name))
    torn = name == 'camp_torn'
    ransacked = name == 'camp_ransacked'
    # trodden ground
    for x in range(W):
        for z in range(L):
            if math.hypot(x - 14, z - 14) < 12.5 + 1.5 * h(x, 0, z):
                b.set(x, G - 1, z, 'minecraft:coarse_dirt' if h(x, 1, z) < 0.5 else 'minecraft:dirt_path')
    # two A-frame tents
    for tx, tz, col in ((8, 9, 'brown'), (19, 10, 'white')):
        for dz in range(-2, 3):
            for k in range(0, 4):
                for side in (-1, 1):
                    x = tx + side * (3 - k)
                    if torn and side == 1 and dz > -1 and tx == 19:
                        continue        # torn open from above
                    b.set(x, G + k, tz + dz, f'minecraft:{col}_wool')
            b.set(tx, G + 4, tz + dz, DARK_LOG_Z)
        b.set(tx, G, tz, B(f'{col}_carpet'))
        b.set(tx - 1, G, tz + 1, B('red_bed', facing='south', part='foot', occupied='false'))
        b.set(tx - 1, G, tz + 2, B('red_bed', facing='south', part='head', occupied='false'))
    # the map table, the journal, crates and the cold fire
    b.set(14, G, 18, 'minecraft:cartography_table')
    title, pages = JOURNALS[name]
    b.lectern_book(15, G, 18, 'north', title, pages)
    b.chest(12, G, 19, 'chests/camp_supply', barrel=True)
    b.chest(11, G, 19, 'chests/camp_survey', barrel=True)
    b.set(11, G + 1, 19, B('barrel', facing='up', open='false'))
    b.set(14, G, 14, B('campfire', facing='north', lit='false', signal_fire='false', waterlogged='false'))
    for k in range(8):
        a = k * math.tau / 8
        b.set(round(14 + 2 * math.cos(a)), G, round(14 + 2 * math.sin(a)), 'minecraft:cobblestone' if k % 2 else 'minecraft:mossy_cobblestone')
    # a lookout: a small timber tower with a ladder and a bell
    for y in range(G, G + 8):
        for dx, dz in ((0, 0), (2, 0), (0, 2), (2, 2)):
            b.set(22 + dx, y, 20 + dz, DARK_LOG_Y)
    b.box(22, G + 8, 20, 24, G + 8, 22, OAK_DARK)
    for dx, dz in ((0, 1), (2, 1), (1, 0), (1, 2)):
        b.set(22 + dx, G + 9, 20 + dz, fence())
    for y in range(G, G + 9):
        b.set(23, y, 23, B('ladder', facing='south', waterlogged='false'))
    b.set(23, G + 10, 21, B('bell', attachment='floor', facing='north', powered='false'))
    b.set(22, G + 9, 20, LANTERN_STAND)
    # a specimen cage, its prisoner long gone
    for y in range(G, G + 3):
        for x in range(5, 8):
            for z in range(18, 21):
                if x in (5, 7) or z in (18, 20):
                    b.set(x, y, z, B('iron_bars'))
    b.box(5, G + 3, 18, 7, G + 3, 20, slab('dark_oak', 'bottom'))
    b.set(6, G, 19, SKULL if torn else BONE_Y)
    if ransacked:
        for k in range(14):
            x, z = 4 + (k * 7) % 21, 4 + (k * 11) % 21
            b.set(x, G, z, COBWEB if k % 2 else B('turtle_egg', eggs=2, hatch=0))
        b.ellipsoid(10, G - 1, 4, 2.5, 1.2, 2, MUD)
        for y in range(G - 6, G):
            b.set(10, y, 4, AIR)                      # a hole dug up from below
    if torn:
        for k in range(5):
            b.set(17 + k, G, 6 + (k % 2), BONE_X if k % 2 else 'minecraft:white_wool')
        b.line((20, G, 12), (26, G + 4, 4), DARK_LOG_X)
    b.point('journal', 15, G, 18)
    b.meta.update({'kind': 'camp', 'title': 'Expedition Camp', 'ground': G})
    return b


if __name__ == '__main__':
    for n in JOURNALS:
        camp(n).save()
