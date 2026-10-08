"""The finale chapter of the preview gallery (build_gallery.py): the eight relics, the Convergence Gate, the Last Realm,
the Unmaker and the Hand of Genesis. Images come from render_gallery.py's `finale` section."""
import html

import mobspecs

RELIC_TEXT = [
    ('rootbound_heart', 'Rootbound Heart', 'Mossback', 'A heart of knotted bark split by green-burning veins, roots trailing, moss on top.'),
    ('storm_talon', 'Storm Talon', 'Tempest Roc', 'A hooked talon of bone crackling with cyan lightning, storm-black feathers at its root.'),
    ('sovereign_hand', 'Sovereign Hand', 'Hollow King', 'His severed gauntlet: black iron split with lava, soul fire burning in the palm.'),
    ('abyssal_fang', 'Abyssal Fang', 'Vorath', 'One curved fang as long as a sword, teal light along its core, coral grown over its root.'),
    ('frozen_voice', 'Frozen Voice', 'White Silence', 'A bell of clear ice bound in chains, a black flame trapped inside where its voice was.'),
    ('glass_stinger', 'Glass Stinger', 'Kharzul', 'A jointed stinger of red glass in gold bands, the last grain of sand glowing in its tip.'),
    ('chronal_eye', 'Chronal Eye', 'Vexor', 'His eye, torn out with its gold frame, the violet iris still turning, cogs round it.'),
    ('living_spore', 'Living Spore', 'Bloom Mother', 'Her seed: a cage of bone round a heart of magenta light, sprouting tiny caps.')]
POWERS = [('Verdant Bloom', 'Grove', 'Heals you and everyone within 8 blocks, with Regeneration II.'),
          ('Tempest Leap', 'Skyreach', 'Throws you forward on the wind, with Slow Falling.'),
          ("Sovereign's Wrath", 'Hollow', 'A cone of soul fire: 12 damage and burning to every enemy in front of you.'),
          ('Undertow', 'Drowned', "Drags every enemy within 12 blocks to you; Water Breathing and Dolphin's Grace."),
          ('Silence', 'Pale', 'Freezes every enemy within 10 blocks; you turn invisible.'),
          ('Last Grain', 'Scarlet', 'A beam of burning light: 16 damage to the first thing it touches.'),
          ('Haste of Hours', 'Clockwork', 'Speed III and Haste III for you; everything nearby slows.'),
          ('Spore Bloom', 'Mycelial', 'Poison II and Weakness II on every enemy within 8 blocks.')]

UNMAKER_TEXT = """<div class="text"><h4>The thing behind the worlds</h4><p>A broken colossus round a black hole. A shell of bone-white and black
plates bursts outward from the Last Heart, cracked with violet light. A blazing accretion ring turns round the heart. Above it, a tall
cracked mask with one burning slit and swept-back horns. Behind the mask, a halo of eight stolen shards, one in each Warden's colour.
Two vast detached hands reach forward, and a storm of debris circles the whole thing. It is about 18 blocks tall and 20 across.</p>
<span class="k">I &middot; Borrowed Gods</span><p>Every 30 seconds it borrows one Warden's power. That realm's node on the arena rim lights
up, the realm's weather fills the arena (poison vines, lightning, wither, undertow, frost, fire, slowed time, choking spores), and a
10-second channel starts. Touch the lit node to return the power and it staggers for 8 seconds (full damage, caps 2.5x). Fail and the
realm's catastrophe falls on everyone: 35% of max health plus that realm's curse. The Clockwork curse even throws you back to where you
stood five seconds earlier. Then it heals. This runs in every phase.</p>
<span class="k">II &middot; World Breaker (66%)</span><p>It tears pieces off the islands and drops them on the arena. Smoke marks each spot
first, and the rubble stays as cover. It calls the dead Wardens' heavy guards back as echoes. Unmaking Anchors rise from the floor and
mend it while they stand: break them with a pickaxe.</p>
<span class="k">III &middot; The Last Heart (33%)</span><p>The heart is bare: it takes 60% damage, up from 25%. It drags everyone toward
it and begins <b>the Unmaking</b>. Deal 4% of its health in six seconds to break the channel and stagger it. Fail and a wedge of the arena
falls into the void. The pad and the node plinths always hold.</p>
<span class="k">Attacks</span><p>The Grasp (a ring marks the ground under every player, then a hand slams down), the Void Lance (a beam
that withers), and the Collapse (a shockwave in phase one, a pull from phase two).</p></div>"""

GATE_TEXT = """<div class="text"><h4>Place all eight relics</h4><p>An overworld ruin (81 x 74 x 81) on a stepped terrace of black and white
stone. An octagonal ring as tall as a tower, a gold inner edge, a starfield behind it, and eight rune sockets in the colours of the
realms. Before it, eight pedestals stand in an arc, each one waiting for one Warden's relic. Touch a pedestal with the wrong relic and it
tells you which one it wants. When all eight are home, the Waygate in the gate's foot wakes.</p><dl class="facts">
<dt>Generates in</dt><dd>Plains, sunflower plains, meadow, savanna, forest, birch forest, taiga, snowy plains, desert</dd>
<dt>Find it</dt><dd><code>/locate structure aurelia:convergence_gate</code></dd>
<dt>Guards</dt><dd>Eight echoes, one heavy guard from each realm: Bramble Sentinel, Calcite Sentinel, Ashbound Knight, Coralclad
Juggernaut, Rimeguard, Sandglass Sentinel, Hour Warden, Husk Guard</dd>
<dt>Opens for</dt><dd>The eight relics, laid on their pedestals</dd></dl></div>"""

REALM_TEXT = """<div class="text"><h4>Every realm becomes part of the fight</h4><p>A void under a black sky. In the middle is a ring of
checkered stone 57 blocks across, with an inverted cone of black rock hanging under it. Eight bridges run out to eight floating islands,
one for each realm you walked: a jungle tree, a quartz spire, a ziggurat over lava, a drowned watchtower, a kneeling ice statue, a red
glass monolith, a clock tower, a giant mushroom. Each has a shrine and a chest of its realm's material.</p><p>The game builds the arena
and the islands from structure templates the first time you arrive. It rebuilds the arena every time the Unmaker wakes, so the fight
always starts on whole ground.</p></div>"""


def e(s):
    return html.escape(str(s))


def fig(src, cap):
    return f'<figure><img src="{e(src)}" alt="{e(cap)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'


LAIR_KIND = {'arena': 'a walled arena', 'temple': 'a stepped temple', 'spire': 'a spiralling spire', 'pit': 'a sunken pit', 'maw': 'a skull-mouthed maw'}


def lieutenants_block(realm, warden):
    """A realm's lieutenants: each one's model, its lair, and what it does. Shared by every realm section and the finale."""
    from lieutenants import of_realm, stats
    lts = of_realm(realm)
    o = [f'<h3 class="sub">The lieutenants</h3><p class="lede" style="margin-bottom:18px">{len(lts)} lairs ring the landing pad, 150 blocks out. '
         f'Crouch and use each lair\'s seal to wake its lieutenant; when it dies the lair\'s beacon goes dark. {e(warden)} will not wake until every '
         'lair is dark. Entering the realm lists the lairs still standing, with their direction and distance.</p>']
    for lt in lts:
        hp, dmg = stats(lt)
        ab = ', '.join(a.title() for a in lt['abilities'])
        o.append('<div class="two" style="margin-top:22px">' + fig(f'lieutenants/{lt["id"]}.webp', f'{e(lt["name"])}, {e(lt["title"])}: front and back.')
                 + fig(f'lairs/lair_{lt["id"]}.webp', f'Its lair, {LAIR_KIND[lt["lair"]]}, with the seal at its heart.') + '</div>')
        o.append(f'<div class="text" style="margin-top:12px"><h4>{e(lt["name"])}, {e(lt["title"])}</h4><p>{e(lt["lore"])}</p>'
                 f'<dl class="facts"><dt>Health</dt><dd>{hp:,}</dd><dt>Hit</dt><dd>{dmg}</dd><dt>Abilities</dt><dd>{e(ab)}</dd>'
                 + (f'<dt>Calls</dt><dd>{e(lt["minion"].replace("_", " "))}</dd>' if lt['minion'] else '')
                 + '<dt>Enrages</dt><dd>at half health: faster, and its abilities come quicker</dd></dl></div>')
    return ''.join(o)


def section():
    n = len(mobspecs.MOBS['unmaker']['parts']())
    o = ['<section class="realm" id="finale" style="--c:#c9a6ff"><div class="wrap">',
         '<div class="rhead"><div><span class="eyebrow">Finale &middot; Convergence Gate &rarr; The Last Realm</span>'
         '<h2>The Eightfold Seal<span class=new>NEW</span></h2><p class="tag">Eight Wardens. Eight relics. One final gate.</p></div>'
         f'<div class="stats">Final boss <b>The Unmaker</b><br><b>12,000</b> HP &middot; <b>{n}</b> model parts<br>Drops <b>the Hand of Genesis</b></div></div>',
         '<h3 class="sub">The eight relics</h3>',
         '<p class="lede" style="margin-bottom:18px">Every Warden now drops a relic as well as its usual shard, every time it dies, so a world that '
         'already beat the early bosses can fight them again. Each relic is a real 3D item model built from cuboids, so it looks like this in '
         'your hand, in an item frame, and on its pedestal.</p><div class="grid4">']
    for key, name, warden, desc in RELIC_TEXT:
        o.append(f'<figure class="guard"><img src="finale/relic_{key}.webp" alt="{e(name)} on its pedestal" loading="lazy">'
                 f'<figcaption><b>{e(name)}</b><span class="from">{e(warden)}</span>{e(desc)}</figcaption></figure>')
    o.append('</div><h3 class="sub">The Convergence Gate</h3>')
    o.append('<div class="pair">' + fig('finale/gate_ext.webp', 'The gate on its terrace. Dots mark the eight echo guards.')
             + fig('finale/gate_side.webp', 'From the side: the octagonal ring, the starfield behind it, the buttress towers.') + '</div>')
    o.append('<div class="two" style="margin-top:22px">' + fig('finale/gate_rite.webp', 'The pedestals, each with a crystal lamp and a glass conduit to the gate.')
             + GATE_TEXT + '</div>')
    o.append('<h3 class="sub">The Last Realm</h3>')
    o.append(fig('finale/last_realm.webp', 'The whole hub as the game builds it round the landing pad. Clockwise from the right: Grove, Skyreach, '
                 'Hollow, Drowned, Pale, Scarlet, Clockwork, Mycelial.'))
    o.append('<div class="two" style="margin-top:22px">' + fig('finale/last_arena.webp', 'The arena: rings of sandstone and black stone round the pad, '
             'a gold circle, and the eight Realm Nodes on the rim, one at the foot of each bridge.') + REALM_TEXT + '</div>')
    o.append('<div class="grid4" style="margin-top:18px">')
    for r in ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial']:
        o.append(fig(f'finale/island_{r}.webp', f'{r.title()} island'))
    o.append('</div>')
    o.append(lieutenants_block('last', 'The Unmaker').replace('The lieutenants', 'The two Heralds'))
    o.append('<h3 class="sub">The Unmaker</h3>')
    o.append(fig('finale/unmaker.webp', 'The Unmaker, front and back. Glowing parts render at full brightness in game.'))
    o.append('<div class="two" style="margin-top:22px">' + fig('finale/unmaker_over_the_last_realm.webp', 'The Unmaker over the Last Realm (not to scale).')
             + UNMAKER_TEXT + '</div>')
    o.append('<h3 class="sub">Final drop: the Hand of Genesis</h3><div class="two">')
    o.append(fig('finale/hand_of_genesis.webp', 'The Hand of Genesis: bone-white and black plate set with all eight relic stones round a white star.'))
    o.append('<div class="text"><h4>Wield the powers of all eight realms</h4><p>Use it to cast its current power, with a 2.5-second cooldown. '
             'Sneak and use it to switch to the next power.</p><dl class="facts">')
    for name, realm, desc in POWERS:
        o.append(f'<dt>{e(realm)}</dt><dd><b>{e(name)}</b>: {e(desc)}</dd>')
    o.append('</dl></div></div>')
    o.append('<h3 class="sub">The Arsenals of the Tenfold Seal</h3>')
    o.append(fig('finale/arsenals.webp', 'Every realm\'s arsenal, and the Unmaker\'s. Three Fractured Genesis fall with every Unmaker kill; '
                 'one, with an ingot of each realm\'s metal, makes four Genesis Ingots. Worldsunder takes a Fractured Genesis and all eight realm weapons.'))
    o.append('</div></section>')
    return '\n'.join(o)
