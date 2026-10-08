"""Writes the preview gallery page (index.html) next to the images render_gallery.py made.

python3 build_gallery.py OUT_DIR
"""
import html
import sys

import finale_page
import mobspecs

ACTS = {1: ('Act I', 'The Shattered Crown', 'Three realms, three shards, the Crown of Aurelia.'),
        2: ('Act II', 'The Outer Realms', 'Three empty settings in the Crown, the Ascendant Crown.'),
        3: ('Act III', 'The Rifts Beneath', 'The hours and the roots under everything, the Eternal Crown.'),
        4: ('Finale', 'The Eightfold Seal', 'Eight relics, one gate, the Last Realm and the Unmaker. The Hand of Genesis.')}

R = [
    dict(id='grove', act=1, name='The Gaudy Grove', tag='Everything here grew too big, too bright, too loud.', accent='#8fd16a',
         realm='Amplified hills under moss and jungle, giant mushrooms, waterfalls off forested stone pillars, mossy ruins, drifting spores, permanent noon.',
         boss='mossback_titan', boss_name='Mossback', hp=2500,
         boss_desc='A hunched rot-wood horror with a deer-skull head, burning sockets, an antler rack hung with skull trophies and a beating heart in an open ribcage.',
         gimmick='Root Hearts', gimmick_desc='He plants three Root Hearts round the arena (four in phase 3). While any stands he heals 1.2% per heart per second and takes only 30% damage. Break them.',
         citadel='rootbound_citadel', citadel_name='Rootbound Citadel', where='Forest biomes', size='65 x 65 x 76',
         citadel_desc='A castle grown into a giant dark-oak tree: a mossy curtain wall, four mushroom-capped towers, a timber wall-walk, and the portal hall inside the trunk.',
         rite='Plant four Spore Hearts', rite_desc='Four Spore Planters round a froglight circuit. Sporecaps drop hearts and each tower holds two spares.',
         seal='Bramble Seal (4 Bramble Sentinels)', trap='Spore Vents: poison and slowness', opens='anyone (the first realm)',
         guards=[('bramble_sentinel', 'Bramble Sentinel', '90 HP. Thorns hurt melee attackers.'), ('sporecap', 'Sporecap', '34 HP. Poison spore clouds, heals the garrison.'),
                 ('rootstalker', 'Rootstalker', '40 HP. Pounces; its bite roots you.')]),
    dict(id='skyreach', act=1, name='Skyreach', tag='The sky tore itself into islands. It never stopped falling apart.', accent='#7fd8ff',
         realm='A true void. Floating islands in four sizes with blossom trees, ponds and waterfalls off their edges, ruined quartz towers and a spired castle island.',
         boss='tempest_roc', boss_name='Tempest Roc', hp=3000,
         boss_desc='A storm-black raptor in a horned bone mask, bone spikes along its wings, two-jointed talons and a bladed nine-feather tail.',
         gimmick='Crash and stun', gimmick_desc='Half damage in the air. A dive that misses leaves it stunned on the ground for about 3.5 seconds with the damage caps raised 2.5x. From phase 2 it throws gusts.',
         citadel='stormwatch_citadel', citadel_name='Stormwatch Citadel', where='Mountain biomes', size='65 x 65 x 92',
         citadel_desc='Quartz spires on a rock crag: a tall central spire, four satellite spires joined by arched bridges, waterfalls off the crag, angel wings over the gate.',
         rite='Lure Storm Wisps', rite_desc='A Storm Wisp\'s lightning charges every pylon within 4 blocks of the strike. Stand by a pylon when it fires. Three pylons.',
         seal='Storm Seal (4 Calcite Sentinels)', trap='Gale Plates: launch you 20 blocks up', opens='a Grove Shard',
         guards=[('calcite_sentinel', 'Calcite Sentinel', '100 HP. Shield cuts frontal damage 60%.'), ('storm_wisp', 'Storm Wisp', '30 HP. Telegraphed lightning from above.'),
                 ('gale_talon', 'Gale Talon', '30 HP. Circles, then dives with heavy knockback.')]),
    dict(id='hollow', act=1, name='The Hollow', tag='Something kept the dark here so it could not reach the others.', accent='#c48bff',
         realm='A closed cavern under a black ceiling: basalt floors, soul-soil drifts, lava lakes, falling ash, ziggurats on lava plugs, arched bridges and hanging stalactites.',
         boss='hollow_king', boss_name='The Hollow King', hp=4000,
         boss_desc='A towering dead king: a skull in an open helm, crown spikes with burning tips, a torn cape, a soul orb and a burning greatsword taller than he is.',
         gimmick='Annihilation', gimmick_desc='He channels for 5 seconds. Deal 6% of his health in that window to stagger him; fail and everyone within 28 blocks loses 60% of their max health.',
         citadel='ashen_citadel', citadel_name='Ashen Citadel', where='Underground, under badlands, desert, savanna, taiga, swamp', size='81 x 81 x 76',
         citadel_desc='A fortress in a lava cavern under the surface: a crater shaft with a spiral ramp, a causeway over the lava, a keep with four spired towers.',
         rite='Place twelve Soul Sigils', rite_desc='Twelve Soul Sockets round a recessed pit. Soul Jailers drop sigils and the four hall chests hold three each.',
         seal='Ash Seal (4 Ashbound Knights)', trap='Ember Vents: fire and damage', opens='a Storm Shard',
         guards=[('ashbound_knight', 'Ashbound Knight', '110 HP. Fire-immune; the greatsword ignites.'), ('soul_jailer', 'Soul Jailer', '60 HP. Chains you in place, calls Shades.'),
                 ('cinder_hound', 'Cinder Hound', '50 HP. Pounces, fiery bite.')]),
    dict(id='drowned', act=2, name='The Drowned Expanse', tag='The sea that swallowed the Sovereign\'s fleet. It is still hungry.', accent='#4fd6c8',
         realm='The overworld flooded to y 96: hills are islands, forests lie under dark green water. Sunken watchtowers, wrecks of the fleet, leviathan skeletons, reef shrines.',
         boss='vorath', boss_name='Vorath, the Tide Devourer', hp=4500,
         boss_desc='An abyssal leviathan: a barnacled skull-head, a maw of needle teeth, a glowing lure, six eyes and a long body that undulates down to a bladed fluke.',
         gimmick='The Tide Bells', gimmick_desc='He circles under the water, taking 30% damage. Ring one of the three bells at the ring\'s edge and he is dragged up against the stone, exposed for 7 seconds (full damage, caps 2.5x).',
         citadel='tidewrack_citadel', citadel_name='Tidewrack Citadel', where='Ocean, lukewarm, warm and cold ocean', size='65 x 72 x 65',
         citadel_desc='A drowned sea-fortress on a reef: a broken sea wall, four round towers, a keep on a rock island, a striped lighthouse and the wreck of the flagship.',
         rite='Ring five Tide Bells', rite_desc='In a dry vault under the reef, five bells on pedestals 0 to 4 blocks tall. Ring them in rising order; a wrong bell silences them and the sea surges.',
         seal='Coral Seal (4 Coralclad Juggernauts)', trap='Brine Grates: drag and drown', opens='the Crown of Aurelia',
         guards=[('coralclad_juggernaut', 'Coralclad Juggernaut', '120 HP. Hurls its anchor and hauls you in.'), ('tidecaller', 'Tidecaller', '50 HP. Whirlpools, heals the garrison.'),
                 ('razorclaw', 'Razorclaw', '44 HP. A reef crab that pins you.')]),
    dict(id='pale', act=2, name='The Pale Wastes', tag='Every sound that was ever made here was taken away.', accent='#dfe9ff',
         realm='Snow over packed ice, ice cliffs, powder-snow pockets, frozen lakes, ice spikes, kneeling colossi of ice and a frozen caravan in grey half-light.',
         boss='white_silence', boss_name='The White Silence', hp=5000,
         boss_desc='A gaunt faceless figure in a torn shroud: a porcelain mask with a glowing crack, a halo of icicles, a cold lantern on a chain and an icicle lance.',
         gimmick='The White', gimmick_desc='It turns invisible and blinds everyone for 8 seconds. Move upright and it hears you and strikes from behind. Creep up crouching and hit it to shatter its composure.',
         citadel='rimefast_citadel', citadel_name='Rimefast Citadel', where='Snowy plains, snowy taiga, ice spikes, slopes, grove', size='65 x 58 x 65',
         citadel_desc='A hushed abbey in the snow: a curtain wall with spruce-coned towers, a nave of packed-ice pillars, a belltower whose bell was taken, a graveyard of kneeling statues.',
         rite='Crouch on four Hush Stones', rite_desc='Crouch on a stone and stay perfectly still for five seconds. Moving, standing, or taking a hit restarts it. Hushwraiths shriek at anyone upright.',
         seal='Rime Seal (4 Rimeguards)', trap='Frost Runes: freeze you in place', opens='Leviathan\'s Pearl',
         guards=[('rimeguard', 'Rimeguard', '120 HP. Its glaive freezes you.'), ('hushwraith', 'Hushwraith', '40 HP. Shrieks at anyone moving upright.'),
                 ('rimefang', 'Rimefang', '46 HP. Gaunt white wolf, frost bite.')]),
    dict(id='scarlet', act=2, name='The Scarlet Sands', tag='The sun never moves here. Neither does anything else, for long.', accent='#ff7a5c',
         realm='Red sand on red sandstone, banded terracotta in every cliff, dry red canyons where the oceans were. Red glass monoliths and buried giants.',
         boss='kharzul', boss_name='Kharzul, the Glass Reaper', hp=6000,
         boss_desc='A hunched four-armed reaper of bone and red glass, an hourglass burning in his ribcage, a crown of glass blades and a scythe with a blade of red glass.',
         gimmick='The Last Grain', gimmick_desc='He turns his hourglass, then its light burns everyone it can see for 60% of their health. Keep a stone pillar between you; the light melts the block that stopped it.',
         citadel='sunscar_citadel', citadel_name='Sunscar Citadel', where='Desert and badlands', size='65 x 60 x 65',
         citadel_desc='A four-tier stepped temple round a deep court open to the sun: a colonnade avenue with two sphinxes, a gold-framed portal, glass-tipped obelisks.',
         rite='Turn the Sun Mirrors', rite_desc='The Sunwell fires north while the sun is up. Flip eight mirrors to lead the beam through three lenses, one at a time. A lit lens stays lit.',
         seal='Sun Seal (4 Sandglass Sentinels)', trap='Sunflare Plates: blinding light and a burn', opens='a Frozen Tear',
         guards=[('sandglass_sentinel', 'Sandglass Sentinel', '130 HP. Throws projectiles back.'), ('sunseer', 'Sunseer', '45 HP. Marks you, then burns the spot.'),
                 ('glasswing_scarab', 'Glasswing Scarab', '40 HP. Burrows and bursts out beside you.')]),
    dict(id='clockwork', act=3, name='The Clockwork Rift', tag='Every second that was ever stolen ended up here.', accent='#f2c14e', new=True,
         realm='A violet void with lightning that never lands. Torn-off fragments of gothic keeps drift on chains, needle spires carry clock faces on every side, broken bridges hang over nothing.',
         boss='vexor', boss_name='Vexor, the Hour Eater', hp=6000,
         boss_desc='A clockwork eye with a slit pupil in a cage of three turning golden rings, six clock-hand blades wheeling round it and pendulum clocks swinging on chains.',
         gimmick='The Hour Strikes', gimmick_desc='Every 26 seconds he channels for ten, sets the Master Clock to a new hour and scrambles the three dials round the face. Wind all three to his hour and his gears seize: he crashes onto the face for 7 seconds (full damage, caps 2.5x). Fail and he eats the hour: everyone is thrown back to where they stood five seconds ago and loses 30% of their health.',
         attacks='Twelve Strikes (numerals burst one after another round the face), the Pendulum (a marked line, then a sweep), Time Stop (everyone slowed, three lanced). Phase 2: Secondhands. Phase 3: the hour strikes more often. Takes 40% damage outside the seizure.',
         citadel='paradox_keep', citadel_name='Paradox Keep', where='Plains, sunflower plains, meadow', size='97 x 132 x 97',
         citadel_desc='A black gothic keep on a crag above a glowing purple rift. Two colossal Hourkeepers hold hourglasses over the stair; a three-arched viaduct crosses the rift to a gatehouse under a gold cog. Four round towers with ogive roofs, a curtain wall of lancets and buttresses, the Hall of Hours with flying buttresses, and a clock tower rising 120 blocks above the meadow with four great clock faces, a belfry and a gold-ringed needle spire. Rock fragments drift overhead on chains.',
         rite='Synchronise the three Clock Dials', rite_desc='Three dials on pedestals in the Hall of Hours; the Master Clock over the portal reads VII. The dials are linked: touching one winds it and the next one along the row forward an hour (the last drags the first). It starts at II, IX, IV and takes 15 touches. The generator checks that it can be solved.',
         seal='Paradox Seal (4 Hour Wardens)', trap='Time Snares: throw you back, slowness and mining fatigue', opens='the Ascendant Crown',
         guards=[('hour_warden', 'Hour Warden', '140 HP, armour 12. A clock-weight flail; its bell tolls time to a crawl.'),
                 ('secondhand', 'Secondhand', '32 HP. Circles overhead flinging clock-hand blades.'),
                 ('gearskitter', 'Gearskitter', '38 HP. A clockwork spider that steals your speed.')]),
    dict(id='mycelial', act=3, name='The Mycelial Deep', tag='Under everything, something has been growing for a very long time.', accent='#f07ad8', new=True,
         realm='A cavern the size of a sky, roofed with roots. Floors of mycelium and magenta and white clay, magenta-capped fungal towers taller than trees, root arches, glowing pools, spores falling like warm snow.',
         boss='bloom_mother', boss_name='The Bloom Mother', hp=6500,
         boss_desc='A rooted fungal flower: ten clawed petals round a maw with two rings of teeth and three tongues, stamens, glowing spore sacs on her stems and a mass of roots.',
         gimmick='The Inhale', gimmick_desc='Every 25 seconds she draws breath for six seconds and drags everyone toward her maw. Wrench the arena\'s spore valves open while she does: two or more open at the end and she chokes, her petals blown wide for 7 seconds (full damage, caps 2.5x). Fewer and she exhales: poison, nausea and 20% of everyone\'s health. Between inhales her roots seal the valves again.',
         attacks='Root Lash (roots churn under three players, then burst up and throw them), Spore Mortar (pods that burst into poison clouds), Devour (anyone close in front when the petals snap shut). Phase 2: Root Grubs. Phase 3: Spore Drifters and faster inhales. Takes 30% damage while her petals are closed.',
         citadel='spore_cathedral', citadel_name='Spore Cathedral', where='Dark forest, mushroom fields, old-growth spruce taiga', size='97 x 96 x 97',
         citadel_desc='A bone-white cruciform cathedral on a podium, gripped by roots. A grand quartz stair between two colossal hooded saints overgrown with moss, each cradling a spore light with a mushroom grown through its hood. Twin towers under magenta caps, a rose window, a mushroom dome 43 blocks across over the crossing and two lesser domes over the transepts. Root buttresses arch from the ground to the walls and giant mushrooms ring the clearing.',
         rite='Open the three Spore Valves', rite_desc='A glowing spore pool under the dome holds the portal on a dais. Three valves (two transepts and the apse) each shut twelve seconds after opening. Open all three before the first closes. The shortest route is 37 blocks, about 8.5 seconds at a walk.',
         seal='Root Seal (4 Husk Guards)', trap='Root Snares: slowness, poison and nausea', opens='the Hour Core',
         guards=[('husk_guard', 'Husk Guard', '140 HP. A fungus shield turns frontal blows; bursts into spores when it falls.'),
                 ('spore_drifter', 'Spore Drifter', '30 HP. Drifts overhead raining stinging spores.'),
                 ('root_grub', 'Root Grub', '42 HP. A bloated grub with a poisonous split-root mouth.')]),
]

STRUCT_NAMES = {
    'grove_pillar_0': 'Forested pillar', 'grove_pillar_2': 'Forested pillar', 'grove_ruin_0': 'Mossy ruin', 'grove_ruin_3': 'Tower stump',
    'grove_outpost_0': 'Watchtower camp', 'grove_outpost_1': 'Sporecap hamlet', 'sky_island_castle_0': 'Castle island', 'sky_island_large_0': 'Large island',
    'sky_island_medium_1': 'Medium island', 'sky_island_small_0': 'Small island', 'sky_outpost_0': 'Watch island', 'sky_outpost_1': 'Wind shrine',
    'hollow_ziggurat_0': 'Ziggurat', 'hollow_arch_0': 'Arched bridge', 'hollow_stalactite_0': 'Stalactite', 'hollow_stalactite_3': 'Stalactite',
    'hollow_outpost_0': 'Ashen fort', 'hollow_outpost_1': 'Soul shrine', 'drowned_spire_0': 'Sunken watchtower', 'drowned_wreck_0': 'Wreck of the fleet',
    'drowned_bones_0': 'Leviathan bones', 'drowned_outpost_0': 'Reef shrine', 'drowned_outpost_1': 'Drowned lighthouse', 'drowned_wreck_1': 'Wreck of the fleet',
    'pale_colossus_0': 'Kneeling colossus', 'pale_colossus_1': 'Fallen colossus', 'pale_spire_0': 'Ice spire', 'pale_spire_2': 'Ice spire',
    'pale_outpost_0': 'Frozen caravan', 'pale_outpost_1': 'Hushed shrine', 'scarlet_monolith_0': 'Red glass monolith', 'scarlet_monolith_2': 'Red glass monolith',
    'scarlet_bones_0': 'Buried giant', 'scarlet_bones_1': 'Buried giant', 'scarlet_outpost_0': 'Sunseer camp', 'scarlet_outpost_1': 'Glassworks',
    'rift_fragment_0': 'Keep fragment', 'rift_fragment_1': 'Keep fragment', 'rift_spire_0': 'Clock spire', 'rift_bridge_0': 'Broken bridge',
    'rift_outpost_0': 'Hour Warden watch-post', 'rift_outpost_1': 'Hour Warden watch-post', 'fungal_tower_0': 'Fungal tower', 'fungal_tower_1': 'Fungal tower',
    'fungal_tower_2': 'Fungal tower', 'root_arch_0': 'Root arch', 'spore_shrine_0': 'Spore Choir shrine', 'root_arch_1': 'Root arch'}

from render_gallery import STRUCTS  # noqa: E402


def e(s):
    return html.escape(str(s))


def parts(key):
    return len(mobspecs.MOBS[key]['parts']())


CSS = r"""
:root {
  /* Layout: a long codex, one chapter per realm; each chapter reads warden > arena > citadel > portal > realm > guards. */
  --ink: #0e0c14; --vellum: #17141f; --panel: #1f1b29; --line: #362f45; --text: #ebe6f2; --muted: #a79fb8; --gold: #e9c46a;
  --display: 'Cinzel', 'Trajan Pro', Georgia, serif; --body: 'Alegreya Sans', 'Segoe UI', system-ui, sans-serif;
  --mono: 'JetBrains Mono', ui-monospace, Menlo, monospace;
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--ink); color: var(--text); font: 17px/1.55 var(--body); margin: 0; }
a { color: inherit; }
.wrap { max-width: 1240px; margin: 0 auto; padding-inline: 20px; }
header.top { padding-block: 56px 28px; border-bottom: 1px solid var(--line); background: radial-gradient(1200px 400px at 50% -80px, #2b2140 0%, transparent 70%); }
.eyebrow { font: 600 12px/1 var(--mono); letter-spacing: .18em; text-transform: uppercase; color: var(--gold); }
h1 { font: 700 clamp(34px, 6vw, 64px)/1.05 var(--display); margin: 14px 0 10px; letter-spacing: .02em; text-wrap: balance; }
.lede { color: var(--muted); max-width: 66ch; margin: 0; }
.acts { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 14px; margin-top: 30px; }
.act { border: 1px solid var(--line); background: var(--vellum); padding: 16px 18px; border-radius: 4px; }
.act h3 { font: 700 15px/1.2 var(--display); margin: 6px 0 4px; letter-spacing: .04em; }
.act p { margin: 0; color: var(--muted); font-size: 15px; }
.act .realms { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.chip { font: 500 12px/1 var(--mono); padding: 6px 8px; border: 1px solid var(--line); border-radius: 3px; text-decoration: none; color: var(--text); }
.chip:hover, .chip:focus-visible { border-color: var(--c, var(--gold)); color: var(--c, var(--gold)); outline: none; }
.chain { margin-top: 26px; font: 13px/1.6 var(--mono); color: var(--muted); overflow-x: auto; white-space: nowrap; padding-bottom: 6px; }
.chain b { color: var(--text); font-weight: 600; }
nav.jump { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 5; background: color-mix(in srgb, var(--ink) 92%, transparent); backdrop-filter: blur(6px); border-bottom: 1px solid var(--line); }
nav.jump .wrap { display: flex; gap: 6px; overflow-x: auto; padding-block: 10px; }
nav.jump .chip { white-space: nowrap; }
section.realm { padding-block: 64px 24px; border-bottom: 1px solid var(--line); }
.rhead { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 8px 24px; align-items: end; }
.rhead h2 { font: 700 clamp(28px, 4.4vw, 46px)/1.05 var(--display); margin: 8px 0 4px; color: var(--c); text-wrap: balance; }
.rhead .tag { font-style: italic; color: var(--muted); margin: 0; }
.new { font: 700 11px/1 var(--mono); letter-spacing: .14em; color: var(--ink); background: var(--c); padding: 5px 7px; border-radius: 2px; vertical-align: middle; margin-left: 10px; }
.stats { font: 13px/1.5 var(--mono); color: var(--muted); text-align: right; }
.stats b { color: var(--text); font-weight: 600; }
h3.sub { font: 700 13px/1 var(--mono); letter-spacing: .16em; text-transform: uppercase; color: var(--c); margin: 44px 0 14px; display: flex; gap: 12px; align-items: center; }
h3.sub::after { content: ""; flex: 1; height: 1px; background: var(--line); }
figure { margin: 0; }
figure img { display: block; width: 100%; height: auto; border-radius: 3px; border: 1px solid var(--line); background: var(--panel); cursor: zoom-in; }
figcaption { font: 13px/1.45 var(--mono); color: var(--muted); margin-top: 8px; }
.two { display: grid; grid-template-columns: minmax(0, 3fr) minmax(0, 2fr); gap: 22px; align-items: start; }
.pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.three { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.grid4 { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }
.guard .from { display: block; font: 600 11px/1.6 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--c); }
code { font: 13px var(--mono); background: var(--panel); padding: 1px 5px; border-radius: 3px; }
.grid6 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.text h4 { font: 700 20px/1.2 var(--display); margin: 0 0 6px; color: var(--text); letter-spacing: .02em; }
.text p { margin: 0 0 12px; }
.text .k { font: 600 12px/1 var(--mono); letter-spacing: .12em; text-transform: uppercase; color: var(--c); display: block; margin: 16px 0 6px; }
dl.facts { display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 6px 14px; margin: 14px 0 0; font-size: 15px; }
dl.facts dt { font: 600 12px/1.9 var(--mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
dl.facts dd { margin: 0; }
.guard figcaption b { color: var(--text); font-weight: 600; display: block; font-family: var(--body); font-size: 15px; }
.strip { overflow-x: auto; border: 1px solid var(--line); border-radius: 3px; background: var(--panel); padding: 14px; }
.strip img { display: block; max-width: none; height: 96px; image-rendering: pixelated; }
.wg { display: flex; gap: 20px; font: 12px/1 var(--mono); color: var(--muted); margin-top: 8px; min-width: 2176px; }
.wg span { width: 252px; }
footer { padding-block: 40px 60px; color: var(--muted); font-size: 14px; }
dialog { border: 0; padding: 0; background: transparent; max-width: 96vw; max-height: 94vh; }
dialog::backdrop { background: rgba(6, 5, 10, .92); }
dialog img { max-width: 96vw; max-height: 90vh; display: block; }
dialog p { color: var(--text); font: 13px var(--mono); margin: 8px 0 0; }
@media (max-width: 860px) {
  .two, .pair { grid-template-columns: minmax(0, 1fr); }
  .three, .grid6, .grid4 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .rhead { grid-template-columns: minmax(0, 1fr); }
  .stats { text-align: left; }
}
@media (max-width: 520px) { .three, .grid6 { grid-template-columns: minmax(0, 1fr); } body { font-size: 16px; } }
@media (prefers-reduced-motion: no-preference) { figure img { transition: transform .2s ease; } figure img:hover { transform: translateY(-2px); } }
"""


def fig(src, cap, alt=None):
    return f'<figure><img src="{e(src)}" alt="{e(alt or cap)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'


def realm_section(r):
    c = r['accent']
    out = [f'<section class="realm" id="{r["id"]}" style="--c:{c}"><div class="wrap">']
    out.append('<div class="rhead"><div>')
    out.append(f'<span class="eyebrow">{ACTS[r["act"]][0]} &middot; {e(r["citadel_name"])} &rarr; {e(r["name"])}</span>')
    out.append(f'<h2>{e(r["name"])}{"<span class=new>NEW</span>" if r.get("new") else ""}</h2><p class="tag">{e(r["tag"])}</p></div>')
    out.append(f'<div class="stats">Warden <b>{e(r["boss_name"])}</b><br><b>{r["hp"]:,}</b> HP &middot; <b>{parts(r["boss"])}</b> model parts<br>Portal opens for <b>{e(r["opens"])}</b></div></div>')
    # warden
    out.append('<h3 class="sub">The Warden</h3>')
    out.append(fig(f'bosses/{r["boss"]}.webp', f'{e(r["boss_name"])}, front and back. Glowing parts render at full brightness in game.'))
    out.append('<div class="two" style="margin-top:22px">')
    out.append(fig(f'arenas/{r["id"]}_arena.webp', 'The arena the Waygate builds round the pad: its wall, its monuments, the gimmick blocks on the pad, and the Warden (not to scale).'))
    out.append(f'<div class="text"><h4>{e(r["boss_name"])}</h4><p>{e(r["boss_desc"])}</p>'
               f'<span class="k">Gimmick: {e(r["gimmick"])}</span><p>{e(r["gimmick_desc"])}</p>'
               + (f'<span class="k">Attacks</span><p>{e(r["attacks"])}</p>' if r.get('attacks') else '') + '</div></div>')
    out.append(finale_page.lieutenants_block(r['id'], r['boss_name'].split(',')[0]))
    # citadel
    out.append('<h3 class="sub">The Citadel</h3>')
    out.append('<div class="pair">' + fig(f'citadels/{r["citadel"]}_ext.webp', f'{e(r["citadel_name"])} inside its fortress: curtain walls, towers, a gatehouse and a causeway to the keep. Dots mark guards.')
               + fig(f'citadels/{r["citadel"]}_cut.webp', 'Cut away to show the inside.') + '</div>')
    out.append(f'<div class="text" style="margin-top:18px"><p>{e(r["citadel_desc"])}</p><dl class="facts">'
               f'<dt>Generates in</dt><dd>{e(r["where"])}</dd><dt>Size</dt><dd>{e(r["size"])} blocks</dd>'
               f'<dt>Seal</dt><dd>{e(r["seal"])}</dd><dt>Floor trap</dt><dd>{e(r["trap"])}</dd></dl></div>')
    # portal and rite
    out.append('<h3 class="sub">Portal and rite</h3><div class="two">')
    out.append(fig(f'portals/{r["citadel"]}_rite.webp', 'The portal room, roof and near walls removed.'))
    out.append(f'<div class="text"><h4>{e(r["rite"])}</h4><p>{e(r["rite_desc"])}</p><p>When the rite is done the Waygate wakes. It opens for '
               f'<b>{e(r["opens"])}</b>.</p></div></div>')
    # realm
    out.append('<h3 class="sub">The realm</h3><div class="two">')
    out.append(fig(f'realms/{r["id"]}_diorama.webp', 'An illustrative patch of the realm with its real structure templates. In game the terrain comes from the dimension\'s own noise settings.'))
    out.append(f'<div class="text"><h4>{e(r["name"])}</h4><p>{e(r["realm"])}</p></div></div>')
    out.append('<div class="grid6" style="margin-top:18px">')
    for n in STRUCTS[r['id']]:
        out.append(fig(f'structures/{n}.webp', f'{e(STRUCT_NAMES.get(n, n))} <span style="opacity:.6">({n})</span>'))
    out.append('</div>')
    # guards
    out.append('<h3 class="sub">Guards</h3><div class="three">')
    for key, name, note in r['guards']:
        out.append(f'<figure class="guard"><img src="guards/{key}.webp" alt="{e(name)}" loading="lazy"><figcaption><b>{e(name)}</b>{e(note)}</figcaption></figure>')
    out.append('</div>')
    # the realm's arsenal and wildlife
    from kit_data import ARSENAL, KIT
    k, a = KIT[r['id']], ARSENAL[r['id']]
    out.append('<h3 class="sub">Arsenal and wildlife</h3>')
    out.append(fig(f'gear/{r["id"]}_armor.webp', f'{e(k["armor_name"])} armor, worn: every piece is its own 3D model.'))
    out.append(f'<div class="two" style="margin-top:22px">' + fig(f'gear/{r["id"]}_items.webp', 'The four armor pieces, three tools, the ore, '
               'the materials and the food.') + f'<div class="text"><h4>{e(k["armor_name"])} armor</h4><span class="k">Full set</span>'
               f'<p>{e(k["bonus"])}</p><span class="k">Tools</span><p>{e(a["tool_name"])} pickaxe, axe and shovel.</p>'
               f'<span class="k">Ore and materials</span><p>{e(a["ore_name"])} drops {e(a["raw_name"])}; '
               f'armor and tools are made from {e(a["metal_name"])}, the weapon also takes {e(a["special_name"])}.</p></div></div>')
    out.append(f'<div class="two" style="margin-top:22px;grid-template-columns:minmax(0,1fr) minmax(0,2fr)">' + fig(f'gear/{r["id"]}_weapon.webp',
               f'{e(k["weapon_name"])}, a {e(a["weapon_kind"])}.') + f'<div class="text"><h4>{e(k["weapon_name"])}</h4>'
               f'<span class="k">On hit</span><p>{e(k["weapon_power"])}</p><span class="k">Use</span><p>{e(k["weapon_ability"])}</p></div></div>')
    out.append(f'<div class="two" style="margin-top:22px">' + fig(f'gear/{r["id"]}_critter.webp', f'The {e(k["critter_name"])}.')
               + f'<div class="text"><h4>{e(k["critter_name"])}</h4><p>{e(k["critter_desc"])} Passive; it follows anyone holding '
               f'{e(k["food_name"])} and breeds on it, and drops it.</p><span class="k">{e(k["food_name"])}</span><p>{e(k["food_power"])}</p></div></div>')
    out.append('</div></section>')
    return '\n'.join(out)


def page():
    chips = {a: ''.join(f'<a class="chip" style="--c:{r["accent"]}" href="#{r["id"]}">{e(r["name"])}</a>' for r in R if r['act'] == a) for a in ACTS}
    chips[4] = '<a class="chip" style="--c:#c9a6ff" href="#finale">The Eightfold Seal</a>'
    acts = ''.join(f'<div class="act"><span class="eyebrow">{e(t[0])}</span><h3>{e(t[1])}</h3><p>{e(t[2])}</p><div class="realms">{chips[a]}</div></div>'
                   for a, t in ACTS.items())
    chain = ' &rarr; '.join(f'<b>{e(r["boss_name"].split(",")[0])}</b>' for r in R)
    names = ''.join(f'<span>{e(r["name"])}: off / on</span>' for r in R)
    body = f"""<title>Aurelia Codex</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Cinzel:wght@600;700&family=JetBrains+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
<header class="top"><div class="wrap">
<span class="eyebrow">Forge 1.20.1 &middot; for the Ascendra modpack</span>
<h1>Aurelia: The Shattered Crown</h1>
<p class="lede">Every Warden, arena, citadel, portal, realm, structure and guard in the mod, rendered from the mod's own model specs and structure templates.
Eight realms in three acts, then the finale. Every realm has its own arsenal (a 3D armor set, a weapon, three tools, an ore and two materials) and its own creature and food. Each one is reached through a citadel in the overworld: kill the seal's guardians, finish the rite, step through, break the Warden's two or three lieutenants in their lairs, then wake the Warden.</p>
<div class="acts">{acts}</div>
<div class="chain">Warden order: {chain} &rarr; <b>Eternal Crown</b> &rarr; eight relics &rarr; <b>The Unmaker</b></div>
</div></header>
<nav class="jump" aria-label="Realms"><div class="wrap">{''.join(chips.values())}<a class="chip" href="#waygates">Waygates</a><a class="chip" href="#scale">Twice the size</a><a class="chip" href="#extras">Extras</a></div></nav>
<main>
{''.join(realm_section(r) for r in R)}
{finale_page.section()}
<section class="realm" id="waygates" style="--c:var(--gold)"><div class="wrap">
<h3 class="sub" style="margin-top:0">The eight Waygates</h3>
<div class="strip"><img src="portals/waygates.png" alt="Waygate block faces for all eight realms, dormant and awake"><div class="wg">{names}</div></div>
<p class="lede" style="margin-top:14px">Each realm's portal block, dormant and awake. A Waygate opens only for the relic of the realm before it; the crowns count as every relic that went into them.</p>
</div></section>
<section class="realm" id="extras" style="--c:var(--gold)"><div class="wrap">
<h3 class="sub" style="margin-top:0">Extras</h3>
<p class="lede" style="margin-bottom:18px">Supplementary content round the quest. <b>Twelve paintings</b> (the eight Wardens, the Unmaker, the Last Realm, the Shattered Crown and the Convergence Gate) that turn up when you hang a painting. <b>Realm masonry</b> for builders: bricks, brick stairs, brick slabs, a carved sigil stone and a glowing sigil lamp for each realm, made from stone bricks and the realm's metal. The <b>Wayfinder's Lodestar</b> (compass, amethyst, an eye of ender): in the overworld it points to the nearest citadel, in a realm to the nearest lair still standing, then to the altar. The <b>Aurelian Bestiary</b> (book, ink, feather, amethyst): every Warden and lieutenant, their health, attacks and how to beat them, opening at the realm you stand in. And an <b>advancement tree</b> of 56: every realm, every realm's lieutenants and Warden, the crowns, the relics, the Heralds, the Unmaker, each realm's armour and weapon, and long hunts like slaying all twenty-six lieutenants.</p>
{fig('extras/paintings.webp', 'The twelve paintings, as they hang.')}
<div class="two" style="margin-top:22px;grid-template-columns:minmax(0,1fr) minmax(0,2fr)">{fig('extras/masonry.webp', 'Realm masonry: bricks, sigil stone and sigil lamp for each realm (stairs and slabs use the bricks).')}{fig('extras/items.webp', "The Wayfinder's Lodestar and the Aurelian Bestiary.")}</div>
</div></section>
<section class="realm" id="scale" style="--c:var(--gold)"><div class="wrap">
<h3 class="sub" style="margin-top:0">Everything, twice the size</h3>
<p class="lede" style="margin-bottom:18px">Every realm structure up to 52 blocks across has been doubled: each block became a 2&times;2&times;2 block, so outposts, spires, colossi, towers, shrines and wrecks now stand twice as tall and four times as broad, and their guards stand where they stood. Slabs, stairs, doors, fences and plants keep their shapes at the new scale. The pieces that were already vast (the sky castle, the great islands, the grove pillars, the ziggurat, the hollow arches, the rift spires) stay as they were. Before on the left, now on the right, at the same scale:</p>
{fig('structures/before_after.webp', 'Six realm structures, before and after.')}
</div></section>
</main>
<footer><div class="wrap">Every structure in the mod goes through a detailing pass (tools/enrich.py) when it is generated: weathered and mixed masonry, quoins on corners, lintels and sills round windows, inlaid floor borders, furniture in room corners, and realm dressing (ivy, moss, snow, hanging roots, cobwebs, lanterns on chains, banners, flowers). Glow lichen is left out of these pictures because in game it is a thin film. Renders are flat-shaded previews made outside the game: block colours are approximate, and models show their glow textures at full brightness as they do in game. Click any picture to enlarge it.</div></footer>
<dialog id="zoom"><img id="zoomimg" alt=""><p id="zoomcap"></p></dialog>
<script>
(function () {{
  var d = document.getElementById('zoom'), im = document.getElementById('zoomimg'), cap = document.getElementById('zoomcap');
  document.addEventListener('click', function (ev) {{
    var t = ev.target;
    if (t.tagName === 'IMG' && t.closest('figure')) {{
      im.src = t.src; im.alt = t.alt;
      var fc = t.closest('figure').querySelector('figcaption');
      cap.textContent = fc ? fc.textContent : '';
      if (d.showModal) d.showModal();
    }} else if (d.open && (t === d || t === im)) {{ d.close(); }}
  }});
}})();
</script>"""
    return body


if __name__ == '__main__':
    out = sys.argv[1]
    open(f'{out}/index.html', 'w', encoding='utf-8').write(page())
    print('wrote', f'{out}/index.html')
