"""Draws the addon's 16x16 item and block textures from the character grids below (one character per pixel, '.' is
transparent). Run from tools/: `python3 textures.py`. Original art; nothing is copied from another mod or Minecraft."""
import os

from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), '..', 'src', 'main', 'resources', 'assets', 'unstable_frontiers', 'textures')

PAL = {
    'k': (24, 20, 26), 'd': (58, 52, 60), 'g': (110, 104, 112), 'l': (170, 166, 172), 'w': (232, 228, 220),
    'b': (214, 204, 176), 'B': (160, 148, 118),                       # bone
    'r': (120, 24, 30), 'R': (186, 44, 44), 'p': (232, 96, 90),         # flesh, heart
    'y': (196, 150, 40), 'Y': (240, 204, 90), 'o': (140, 96, 30),       # gold, honey
    'a': (110, 60, 160), 'A': (168, 110, 226), 'v': (220, 180, 255),    # amethyst
    'c': (64, 120, 120), 'C': (110, 190, 180), 'n': (40, 70, 70),       # chitin teal
    'i': (90, 92, 100), 'I': (150, 154, 164), 'j': (200, 204, 212),     # iron
    'u': (60, 200, 90), 'U': (150, 250, 140),                           # uranium glow
    's': (70, 44, 26), 'S': (120, 80, 46),                              # leather, wood
}

ITEMS = {
    'rookery_talon': [
        '................',
        '..........kk....',
        '.........kbbk...',
        '........kbwbk...',
        '.......kbwbk....',
        '......kbwbBk....',
        '.....kbwbBk.....',
        '....kbwbBk......',
        '...kbbbBk.......',
        '..kBbbBk........',
        '..kBBBk.........',
        '..ksSk..........',
        '.ksSSk..........',
        '.kssk...........',
        '..kk............',
        '................'],
    'hive_heart': [
        '................',
        '....kk....kk....',
        '...kRRk..kRRk...',
        '..kRpRRkkRRRRk..',
        '..kRppRRRRRRRk..',
        '..kRpRRRRRYRrk..',
        '..kRRRRRRYYRrk..',
        '...kRRRRRYRrk...',
        '...kcRRRRRrck...',
        '....kcRRRrck....',
        '.....kcRrck.....',
        '......kcck......',
        '.......kk.......',
        '................',
        '................',
        '................'],
    'great_cage_heart': [
        '................',
        '.....iIIIIi.....',
        '....iIk..kIi....',
        '...iIkR..RkIi...',
        '...IkRpRRRRkI...',
        '...IkRpRRRRkI...',
        '...IkRRRURRkI...',
        '...IkRRUURRkI...',
        '...IkRRRURRkI...',
        '...iIkRRRRkIi...',
        '....iIkRRkIi....',
        '.....iIkkIi.....',
        '......iIIi......',
        '.......ii.......',
        '................',
        '................'],
    'cagewright_key': [
        '................',
        '...kkk..........',
        '..kyYyk.........',
        '.kyk.kyk........',
        '.kY.R.Yk........',
        '.kyk.kyk........',
        '..kyYyyk........',
        '...kkkyyk.......',
        '.......kyyk.....',
        '........kyyk....',
        '.......kyykyk...',
        '........kk.kyk..',
        '..........kyyk..',
        '...........kk...',
        '................',
        '................'],
    'rift_lens': [
        '................',
        '.....kkkkk......',
        '....kAvvvAk.....',
        '...kAv.k.vAk....',
        '...kv.kak.vk....',
        '...kvkaAak.k....',
        '...kv.kak.vk....',
        '...kAv.k.vAk....',
        '....kAvvvAk.....',
        '.....kccck......',
        '......knck......',
        '......kcnk......',
        '......knck......',
        '.......kk.......',
        '................',
        '................'],
    'cagewright_shackle': [
        '................',
        '....kkkk........',
        '...kIjjIk.......',
        '..kIk..kIk......',
        '..kj....jk......',
        '..kIk..kIk......',
        '...kIjjIk.......',
        '....kIIk........',
        '.....kik........',
        '......kik.......',
        '.......kik......',
        '......kkIkk.....',
        '.....kIjjjIk....',
        '.....kIbBbIk....',
        '......kkkkk.....',
        '................'],
}

BLOCK = {
    'cage_beacon_side': [
        'kkkkkkkkkkkkkkkk',
        'kdIdddIddddIdddk',
        'kdIdddIddddIdddk',
        'kIIIIIIIIIIIIIIk',
        'kdIaaaIaaaaIaadk',
        'kdIaAAIAvAaIAadk',
        'kdIaAvIvvAaIAadk',
        'kIIIIIIIIIIIIIIk',
        'kdIaAAIAvAaIAadk',
        'kdIaaAIAAaaIaadk',
        'kdIaaaIaaaaIaadk',
        'kIIIIIIIIIIIIIIk',
        'kdIdddIddddIdddk',
        'kdIdddIddddIdddk',
        'kgggggggggggggggk'[:16],
        'kkkkkkkkkkkkkkkk'],
    'cage_beacon_top': [
        'kkkkkkkkkkkkkkkk',
        'kdddIddddddIdddk',
        'kdaaIaaaaaaIaadk',
        'kIIIIIIIIIIIIIIk',
        'kdaaIaAAAAaIaadk',
        'kdaaIAvvvvAIaadk',
        'kdaaIAvwwvAIaadk',
        'kIIIIIvwwvIIIIIk',
        'kdaaIAvwwvAIaadk',
        'kdaaIAvvvvAIaadk',
        'kdaaIaAAAAaIaadk',
        'kIIIIIIIIIIIIIIk',
        'kdaaIaaaaaaIaadk',
        'kdddIddddddIdddk',
        'kdddIddddddIdddk',
        'kkkkkkkkkkkkkkkk'],
    'cage_beacon_bottom': ['k' * 16] + ['k' + 'dg' * 7 + 'k' if r % 2 else 'k' + 'gd' * 7 + 'k' for r in range(14)] + ['k' * 16],
}


def draw(grid, path):
    im = Image.new('RGBA', (16, 16), (0, 0, 0, 0))
    for y, row in enumerate(grid):
        assert len(row) == 16, (path, y, len(row))
        for x, ch in enumerate(row):
            if ch != '.':
                im.putpixel((x, y), PAL[ch] + (255,))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


if __name__ == '__main__':
    for name, g in ITEMS.items():
        draw(g, os.path.join(OUT, 'item', name + '.png'))
    for name, g in BLOCK.items():
        draw(g, os.path.join(OUT, 'block', name + '.png'))
    print('textures written')
