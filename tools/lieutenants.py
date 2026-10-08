"""The Warden's lieutenants: three in every realm, two Heralds before the Unmaker. Each holds a lair somewhere out from the
landing pad; the Warden's altar will not wake until all of its realm's lieutenants are dead.

One table drives the models (mobs_lt.py), the Java (gen_lieutenants.py writes LieutenantKind.java), the lairs (gen_lairs.py),
the names and the gallery.

  body       biped | beast | spider | flyer | serpent: which base class and animations it uses
  size       hitbox (width, height) in blocks
  abilities  drawn from the shared library in Lieutenant.java:
             SLAM (ground shockwave), CHARGE (bull rush), LEAP (jump and crash down), BOLT (one aimed bolt),
             VOLLEY (a fan of bolts), FIREBALLS, SKULLS (wither skulls), SUMMON (minions), PULL (drag everyone in),
             NOVA (an elemental burst), BLINK (vanish and strike from behind), ZONE (a lingering cloud),
             STORM (lightning on everyone near), ROOT (snare everyone near), BULWARK (brief damage shell)
  element    the realm's flavour: particles, sounds and the effect its attacks carry
  minion     entity id summoned by SUMMON
  lair       arena | temple | spire | pit | maw: the lair's plan (gen_lairs.py)
"""

REALM_ORDER = ['grove', 'skyreach', 'hollow', 'drowned', 'pale', 'scarlet', 'clockwork', 'mycelial', 'last']
STATS = {   # health, attack damage per realm (the Wardens have 2,500 to 6,500; the Unmaker 12,000)
    'grove': (800, 14), 'skyreach': (950, 15), 'hollow': (1300, 18), 'drowned': (1400, 18), 'pale': (1500, 19),
    'scarlet': (1800, 21), 'clockwork': (1900, 22), 'mycelial': (2100, 23), 'last': (3600, 30)}

LIEUTENANTS = [
    # ---------------------------------------------------------------------------------------------- the Gaudy Grove
    dict(id='thornmaw', realm='grove', name='Thornmaw', title='the Briar Hound', body='beast', size=(2.6, 2.4), speed=0.34,
         abilities=['CHARGE', 'LEAP', 'ROOT'], element='grove', minion=None, lair='maw',
         lore='A wolf the size of a cart, grown through with briars. Its howl roots the ground under you.',
         awaken='Something vast shakes the thorns from its back.', death='The briars go still, and the hound with them.'),
    dict(id='hollowbark', realm='grove', name='Old Hollowbark', title='the Rotting Ent', body='biped', size=(2.2, 6.2), speed=0.22,
         abilities=['SLAM', 'SUMMON', 'ZONE'], element='grove', minion='aurelia:grove_ant', lair='temple',
         lore='The oldest tree in the Grove, dead on its feet and still walking. Ants nest in the hollow of its chest.',
         awaken='The dead tree opens its eyes.', death='Old Hollowbark falls, and does not get up.'),
    dict(id='rot_matron', realm='grove', name='The Rot Matron', title='Mother of the Undergrowth', body='spider', size=(3.4, 1.9), speed=0.3,
         abilities=['VOLLEY', 'PULL', 'SUMMON'], element='grove', minion='aurelia:rootstalker', lair='pit',
         lore='A spider like a fallen log, her back a garden of rot. Her webs drag you to her.',
         awaken='Eight eyes open in the dark under the roots.', death='The Rot Matron curls up and dies.'),
    # ---------------------------------------------------------------------------------------------- Skyreach
    dict(id='galeclaw', realm='skyreach', name='Galeclaw', title='the Storm Harrier', body='flyer', size=(3.2, 1.7), speed=0.3,
         abilities=['CHARGE', 'BOLT', 'STORM'], element='skyreach', minion=None, lair='spire',
         lore='A hawk of storm-grey feathers that dives out of thunderheads. Lightning follows it down.',
         awaken='A shriek splits the clouds.', death='Galeclaw tumbles out of the sky.'),
    dict(id='thunder_colossus', realm='skyreach', name='The Thunder Colossus', title='Keeper of the Spire', body='biped', size=(2.6, 6.6), speed=0.2,
         abilities=['SLAM', 'STORM', 'BULWARK'], element='skyreach', minion=None, lair='arena',
         lore='Calcite and stormcloud stacked into a giant. Every blow it lands calls the lightning.',
         awaken='The stone giant draws a breath of thunder.', death='The Colossus cracks, and the storm in it leaks away.'),
    dict(id='squall_seraph', realm='skyreach', name='The Squall Seraph', title='the Wind that Judges', body='flyer', size=(1.6, 3.6), speed=0.32,
         abilities=['BLINK', 'VOLLEY', 'PULL'], element='skyreach', minion=None, lair='temple',
         lore='A winged knight with a spear of wind and a halo of hail. It is never where you swung.',
         awaken='Wings unfold above you, white and cold.', death='The Seraph scatters into sleet.'),
    # ---------------------------------------------------------------------------------------------- the Hollow
    dict(id='cinderjaw', realm='hollow', name='Cinderjaw', title='Hound of the Pit', body='beast', size=(2.8, 2.6), speed=0.36,
         abilities=['CHARGE', 'NOVA', 'LEAP'], element='hollow', minion=None, lair='pit',
         lore='A hound of cooling magma with a forge for a throat. It bursts into flame when it is hurt.',
         awaken='The lava stirs, and stands up.', death='Cinderjaw cools to black stone.'),
    dict(id='chainwarden', realm='hollow', name='The Chainwarden', title='Jailer of the Damned', body='biped', size=(2.2, 5.4), speed=0.22,
         abilities=['PULL', 'SLAM', 'SUMMON'], element='hollow', minion='aurelia:hollow_shade', lair='arena',
         lore='The Hollow King\'s gaoler, wrapped in the chains of everyone it ever kept. It hooks you and hauls you in.',
         awaken='Chains rattle in the dark, and go taut.', death='The Chainwarden falls, and its chains let go.'),
    dict(id='ashen_choir', realm='hollow', name='The Ashen Choir', title='Three Who Sing Ash', body='flyer', size=(2.6, 2.6), speed=0.26,
         abilities=['SKULLS', 'ZONE', 'BLINK'], element='hollow', minion=None, lair='temple',
         lore='Three burning skulls bound by a single shroud. Their song is a cloud of wither.',
         awaken='Three voices begin to sing.', death='The Choir falls silent, one voice at a time.'),
    # ---------------------------------------------------------------------------------------------- the Drowned Expanse
    dict(id='reef_crusher', realm='drowned', name='The Reef Crusher', title='Shell of the Deep', body='beast', size=(3.8, 2.4), speed=0.24,
         abilities=['SLAM', 'CHARGE', 'BULWARK'], element='drowned', minion=None, lair='arena',
         lore='A crab as wide as a house, its shell crusted with coral and wrecks. It shuts up tight when it is hurt.',
         awaken='The reef rises on eight legs.', death='The Reef Crusher\'s shell splits open.'),
    dict(id='drowned_admiral', realm='drowned', name='The Drowned Admiral', title='Captain of the Sunken Fleet', body='biped', size=(1.6, 4.4), speed=0.26,
         abilities=['LEAP', 'PULL', 'SUMMON'], element='drowned', minion='minecraft:drowned', lair='maw',
         lore='Vorath\'s admiral, still giving orders to a crew three centuries dead. His anchor drags you to the deck.',
         awaken='A ship\'s bell rings under the water.', death='The Admiral goes down with his ship.'),
    dict(id='abyssal_siren', realm='drowned', name='The Abyssal Siren', title='Voice of the Trench', body='flyer', size=(1.6, 4.0), speed=0.3,
         abilities=['VOLLEY', 'NOVA', 'ROOT'], element='drowned', minion=None, lair='temple',
         lore='Half eel, half drowned queen, floating in a column of her own water. Her song pins you where you stand.',
         awaken='Somewhere, a woman begins to sing.', death='The Siren\'s song breaks off.'),
    # ---------------------------------------------------------------------------------------------- the Pale Wastes
    dict(id='frostmaw', realm='pale', name='Frostmaw', title='the Starving Yeti', body='biped', size=(2.6, 4.8), speed=0.28,
         abilities=['SLAM', 'LEAP', 'ROOT'], element='pale', minion=None, lair='pit',
         lore='A hunched white giant, all ribs and claws. The snow freezes solid where it lands.',
         awaken='Something hungry climbs out of the snow.', death='Frostmaw collapses into the drifts.'),
    dict(id='rime_knight', realm='pale', name='The Knight of Last Winter', title='Sworn to the Silence', body='biped', size=(1.4, 4.0), speed=0.3,
         abilities=['BLINK', 'CHARGE', 'NOVA'], element='pale', minion=None, lair='arena',
         lore='A knight in armor of black ice who took a vow of silence and kept it past death. You will not hear him coming.',
         awaken='A knight in black ice draws its sword without a sound.', death='The Knight shatters.'),
    dict(id='the_mourner', realm='pale', name='The Mourner', title='She Who Weeps Snow', body='flyer', size=(1.6, 4.2), speed=0.28,
         abilities=['VOLLEY', 'NOVA', 'PULL'], element='pale', minion=None, lair='temple',
         lore='A veiled figure floating over the snow, weeping ice. Where she looks, the light goes out.',
         awaken='Someone is weeping in the wind.', death='The Mourner\'s veil falls empty to the snow.'),
    # ---------------------------------------------------------------------------------------------- the Scarlet Sands
    dict(id='dune_tyrant', realm='scarlet', name='The Dune Tyrant', title='King of Stings', body='spider', size=(3.8, 2.3), speed=0.32,
         abilities=['CHARGE', 'VOLLEY', 'LEAP'], element='scarlet', minion=None, lair='maw',
         lore='A scorpion of red glass and old bone. Its sting fires barbs from twenty paces.',
         awaken='The dunes split, and a tail rises.', death='The Tyrant\'s tail falls limp.'),
    dict(id='sand_pharaoh', realm='scarlet', name='The Sandglass Pharaoh', title='Who Was Buried Waiting', body='biped', size=(1.6, 4.6), speed=0.24,
         abilities=['SUMMON', 'ZONE', 'BLINK'], element='scarlet', minion='minecraft:husk', lair='temple',
         lore='A pharaoh wrapped in gold and grave-cloth, holding an hourglass full of red sand. The dead rise when he turns it.',
         awaken='An hourglass turns over in the dark.', death='The Pharaoh\'s sand runs out.'),
    dict(id='glass_djinn', realm='scarlet', name='The Glass Djinn', title='Furnace of the Sands', body='flyer', size=(2.0, 4.2), speed=0.3,
         abilities=['FIREBALLS', 'NOVA', 'BLINK'], element='scarlet', minion=None, lair='spire',
         lore='A spirit of molten glass, all fire inside. It hurls the sun at you a piece at a time.',
         awaken='The air above the sand begins to burn.', death='The Djinn cools, cracks and falls in shards.'),
    # ---------------------------------------------------------------------------------------------- the Clockwork Rift
    dict(id='pendulum_butcher', realm='clockwork', name='The Pendulum Butcher', title='It Keeps Perfect Time', body='biped', size=(2.4, 5.6), speed=0.22,
         abilities=['SLAM', 'CHARGE', 'BULWARK'], element='clockwork', minion=None, lair='arena',
         lore='An iron executioner with pendulum blades for arms, swinging on the beat. It never misses a stroke.',
         awaken='A great pendulum begins to swing.', death='The Butcher winds down and stops.'),
    dict(id='gearwyrm', realm='clockwork', name='The Gearwyrm', title='Engine Without End', body='serpent', size=(3.0, 1.9), speed=0.34,
         abilities=['CHARGE', 'BOLT', 'LEAP'], element='clockwork', minion=None, lair='pit',
         lore='A centipede of gears and pistons, a hundred segments long. It strikes like a piston and spits sparks.',
         awaken='Gears grind together somewhere below you.', death='The Gearwyrm seizes up, segment by segment.'),
    dict(id='hourless_oracle', realm='clockwork', name='The Hourless Oracle', title='Who Saw Your Death', body='flyer', size=(2.2, 3.2), speed=0.28,
         abilities=['BLINK', 'ROOT', 'VOLLEY'], element='clockwork', minion=None, lair='spire',
         lore='A floating clock-faced seer with too many hands. It has seen how this ends, and freezes you in that moment.',
         awaken='Every clock around you stops.', death='The Oracle\'s hands spin free.'),
    # ---------------------------------------------------------------------------------------------- the Mycelial Deep
    dict(id='rot_behemoth', realm='mycelial', name='The Rot Behemoth', title='Mountain of Spores', body='beast', size=(4.0, 3.6), speed=0.22,
         abilities=['SLAM', 'ZONE', 'CHARGE'], element='mycelial', minion=None, lair='pit',
         lore='A beast buried under its own fungal forest. Every step shakes loose a cloud of spores.',
         awaken='A hill of mushrooms gets up.', death='The Behemoth sinks back into the rot.'),
    dict(id='pale_gardener', realm='mycelial', name='The Pale Gardener', title='Who Tends the Dead', body='biped', size=(1.6, 5.8), speed=0.3,
         abilities=['CHARGE', 'SUMMON', 'ROOT'], element='mycelial', minion='aurelia:sporecap', lair='temple',
         lore='A tall, thin thing of white stalk with scythes for hands. It plants the dead and harvests the living.',
         awaken='Something tall stoops out of the fungus.', death='The Gardener withers where it stands.'),
    dict(id='lumen_horror', realm='mycelial', name='The Lumen Horror', title='Light in the Deep', body='flyer', size=(2.8, 3.8), speed=0.24,
         abilities=['ZONE', 'VOLLEY', 'PULL'], element='mycelial', minion=None, lair='spire',
         lore='A drifting jellyfish-cap of glowing flesh, trailing poisoned threads. Its light draws you in.',
         awaken='A soft light rises out of the dark.', death='The Lumen Horror\'s light goes out.'),
    # ---------------------------------------------------------------------------------------------- the Last Realm
    dict(id='herald_of_ruin', realm='last', name='The Herald of Ruin', title='First of the Unmade', body='biped', size=(2.6, 6.8), speed=0.24,
         abilities=['SLAM', 'CHARGE', 'NOVA', 'SUMMON'], element='last', minion='aurelia:husk_guard', lair='arena',
         lore='A giant of bone-white plate and black void, the Unmaker\'s sword arm made flesh.',
         awaken='The Herald of Ruin raises its blade.', death='The Herald of Ruin comes apart.'),
    dict(id='herald_of_silence', realm='last', name='The Herald of Silence', title='Last of the Unmade', body='flyer', size=(3.0, 3.0), speed=0.28,
         abilities=['BLINK', 'VOLLEY', 'PULL', 'ROOT'], element='last', minion=None, lair='spire',
         lore='A great eye wrapped in rings of broken worlds. It does not speak; it unmakes sound.',
         awaken='Everything goes quiet.', death='The Herald of Silence closes its eye.'),
]

BY_ID = {lt['id']: lt for lt in LIEUTENANTS}


def of_realm(realm):
    return [lt for lt in LIEUTENANTS if lt['realm'] == realm]


def stats(lt):
    hp, dmg = STATS[lt['realm']]
    k = {'beast': 0.9, 'spider': 0.85, 'flyer': 0.8, 'serpent': 0.9, 'biped': 1.1}[lt['body']]
    return int(round(hp * k / 50) * 50), dmg


assert all(len(of_realm(r)) >= 2 for r in REALM_ORDER)
