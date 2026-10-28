"""Shared palettes and building blocks for the frontier's structures."""
import math

from kit import AIR, B, h

# ---------------------------------------------------------------- palettes (vanilla first; Antarchy blocks only where noted)
DARK = 'minecraft:polished_blackstone'
DARK_BRICK = 'minecraft:polished_blackstone_bricks'
DARK_CRACK = 'minecraft:cracked_polished_blackstone_bricks'
DARK_CHISEL = 'minecraft:chiseled_polished_blackstone'
GILDED = 'minecraft:gilded_blackstone'
BASALT = B('polished_basalt', axis='y')
DEEP_TILE = 'minecraft:deepslate_tiles'
DEEP_TILE_CRACK = 'minecraft:cracked_deepslate_tiles'
DEEP_BRICK = 'minecraft:deepslate_bricks'
COBBLE_DEEP = 'minecraft:cobbled_deepslate'
TUFF = 'minecraft:tuff'
TUFF_BRICK = 'minecraft:tuff_bricks'
STONE = 'minecraft:stone'
ANDESITE = 'minecraft:andesite'
BARS = 'minecraft:iron_bars'
RUST_BARS = 'minecraft:iron_bars'
CHAIN_Y = B('chain', axis='y', waterlogged='false')
CHAIN_X = B('chain', axis='x', waterlogged='false')
CHAIN_Z = B('chain', axis='z', waterlogged='false')
BONE_Y = B('bone_block', axis='y')
BONE_X = B('bone_block', axis='x')
BONE_Z = B('bone_block', axis='z')
COBWEB = 'minecraft:cobweb'
SHROOM = 'minecraft:shroomlight'
SOUL_LANTERN = B('soul_lantern', hanging='true', waterlogged='false')
LANTERN = B('lantern', hanging='true', waterlogged='false')
LANTERN_STAND = B('lantern', hanging='false', waterlogged='false')
ROD_UP = B('end_rod', facing='up')
OAK_DARK = 'minecraft:dark_oak_planks'
DARK_LOG_Y = B('dark_oak_log', axis='y')
DARK_LOG_X = B('dark_oak_log', axis='x')
DARK_LOG_Z = B('dark_oak_log', axis='z')
STRIPPED_X = B('stripped_dark_oak_log', axis='x')
STRIPPED_Z = B('stripped_dark_oak_log', axis='z')
STRIPPED_Y = B('stripped_dark_oak_log', axis='y')
HAY = B('hay_block', axis='y')
MUD = 'minecraft:mud'
PACKED_MUD = 'minecraft:packed_mud'
MUD_BRICK = 'minecraft:mud_bricks'
COARSE = 'minecraft:coarse_dirt'
ROOTED = 'minecraft:rooted_dirt'
MOSS = 'minecraft:moss_block'
MOSS_CARPET = 'minecraft:moss_carpet'
SKULL = B('skeleton_skull', rotation=0)


def stair(material, facing, half='bottom', shape='straight'):
    return B(f'{material}_stairs', facing=facing, half=half, shape=shape, waterlogged='false')


def slab(material, kind='bottom'):
    return B(f'{material}_slab', type=kind, waterlogged='false')


def wall(material):
    return B(f'{material}_wall', east='none', north='none', south='none', west='none', up='true', waterlogged='false')


def fence(material='dark_oak'):
    return B(f'{material}_fence', east='false', north='false', south='false', west='false', waterlogged='false')


def weathered(x, y, z, base, cracked, mossy=None, salt=0, crack=0.18, moss=0.0):
    r = h(x, y, z, salt)
    if mossy and r < moss:
        return mossy
    if r < moss + crack:
        return cracked
    return base


def dark_stone(x, y, z):
    return weathered(x, y, z, DARK_BRICK, DARK_CRACK, salt=3, crack=0.22)


def rock(x, y, z, salt=0):
    """Natural rock for spires and plinths: banded stone, tuff and andesite with deepslate below."""
    r = h(x, y, z, salt)
    band = math.sin(y * 0.35 + h(x // 3, 0, z // 3, salt) * 2)
    if y < 6 and r < 0.5:
        return COBBLE_DEEP
    if band > 0.55:
        return TUFF
    if r < 0.18:
        return ANDESITE
    if r < 0.24:
        return 'minecraft:gravel' if y > 4 else STONE
    return STONE


def octagon(cx, cz, r):
    """Points of a regular octagon (flat sides on the axes)."""
    return [(cx + r * math.cos(math.radians(22.5 + 45 * i)), cz + r * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]


def in_octagon(x, z, cx, cz, r):
    """Inside a regular octagon whose flat sides sit r from the centre."""
    dx, dz = abs(x - cx), abs(z - cz)
    return dx <= r and dz <= r and dx + dz <= r * 1.4142


def on_octagon_rim(x, z, cx, cz, r):
    return in_octagon(x, z, cx, cz, r) and not in_octagon(x, z, cx, cz, r - 1)
