"""The finale: texture styles and registration of the Unmaker with mobspecs."""
import bosses_act4

STYLES = {
    'unmade_w': dict(base=(226, 218, 200), var=7, patches=[((196, 186, 166), 14, (1, 3)), ((40, 34, 44), 4, (1, 1))], cracks=(170, 80, 255)),
    'unmade_w2': dict(base=(206, 196, 176), var=8, patches=[((232, 224, 208), 12, (1, 3)), ((150, 140, 124), 10, (1, 2))]),
    'unmade_b': dict(base=(28, 26, 34), var=5, patches=[((46, 42, 56), 16, (1, 3)), ((14, 12, 18), 12, (1, 3))], cracks=(160, 70, 255)),
    'regalia_w': dict(base=(232, 226, 212), var=5, patches=[((246, 242, 232), 12, (1, 3)), ((200, 192, 176), 10, (1, 2))]),
    'regalia_b': dict(base=(30, 28, 38), var=4, patches=[((50, 46, 62), 14, (1, 3)), ((16, 14, 22), 10, (1, 2))]),
    'abyss': dict(base=(4, 2, 8), var=2, patches=[], dots=((40, 20, 70), 6, (1, 1))),
    'accretion': dict(base=(196, 120, 255), var=14, patches=[((250, 220, 255), 14, (1, 3)), ((130, 60, 230), 10, (1, 2))]),
    'accretion2': dict(base=(255, 242, 255), var=6, patches=[((230, 190, 255), 10, (1, 1))]),
    'accretion3': dict(base=(120, 50, 220), var=12, patches=[((190, 120, 255), 12, (1, 2))]),
    'shard_g': dict(base=(96, 240, 90), var=12, patches=[((200, 255, 170), 10, (1, 2)), ((40, 140, 40), 8, (1, 2))]),
    'shard_c': dict(base=(90, 214, 255), var=12, patches=[((220, 250, 255), 10, (1, 2)), ((30, 110, 200), 8, (1, 2))]),
    'shard_v': dict(base=(255, 140, 40), var=12, patches=[((255, 220, 120), 10, (1, 2)), ((90, 170, 255), 10, (1, 2))]),
    'shard_t': dict(base=(60, 230, 200), var=12, patches=[((200, 255, 240), 10, (1, 2)), ((20, 120, 120), 8, (1, 2))]),
    'shard_i': dict(base=(214, 236, 255), var=8, patches=[((255, 255, 255), 10, (1, 2)), ((140, 180, 240), 10, (1, 2))]),
    'shard_r': dict(base=(250, 50, 60), var=12, patches=[((255, 160, 150), 10, (1, 2)), ((150, 10, 30), 8, (1, 2))]),
    'shard_y': dict(base=(255, 204, 70), var=10, patches=[((255, 245, 190), 10, (1, 2)), ((200, 130, 30), 8, (1, 2))]),
    'shard_m': dict(base=(255, 80, 220), var=12, patches=[((255, 200, 245), 10, (1, 2)), ((160, 30, 150), 8, (1, 2))]),
}
GLOW = {'accretion', 'accretion2', 'accretion3', 'shard_g', 'shard_c', 'shard_v', 'shard_t', 'shard_i', 'shard_r', 'shard_y', 'shard_m'}

MOBS = {'unmaker': dict(parts='unmaker', seed=61, shadow=4.0)}


def register(mobs, styles, glow_styles, part):
    styles.update(STYLES)
    glow_styles.update(GLOW)
    for key, m in MOBS.items():
        fn = getattr(bosses_act4, m['parts'])
        mobs[key] = dict(parts=(lambda f=fn: f(part)), seed=m['seed'], shadow=m['shadow'])
