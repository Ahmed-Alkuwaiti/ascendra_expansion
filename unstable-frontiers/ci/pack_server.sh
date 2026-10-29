#!/usr/bin/env bash
# Boots a dedicated server with the addon and the Integrated Boogaloo mods it depends on or touches (picked, with every
# dependency, from the real pack in ./pack), using the pack's own configs and server scripts. Run after fetch_pack.py
# and `gradle build`, from the addon folder.
set -u
rm -rf run/mods run/config run/kubejs run/defaultconfigs run/world
mkdir -p run/mods
# Every jar of the pack except client-only ones (rendering, menus, tooltips, input). Several pack mods carry mixins that
# hard-require other pack mods, so a hand-picked subset does not boot; the whole pack is also what players run.
CLIENT_ONLY='sodium|iris|fancymenu|konkrete|melody|drippy|dark_loading_screen|mousetweaks|stellar|bhmenu|better-advanced-tooltips|justenoughthreads|overflowingbars|entityculling|immediatelyfast|modernfix-client|reeses|controlling|searchables|appleskin-client|betterf3|chat_heads|continuity|enhancedvisuals|notenoughanimations|skinlayers|3dskinlayers|presencefootsteps|ambientsounds|soundphysics|dynamiclights|lambdynamiclights|shulkerboxtooltip|legendarytooltips|iconic|crash.?assistant|mezz_config|enhancedblockentities|better-clouds|retrodamageindicators|ebe'
for j in pack/mods/*.jar; do
  b=$(basename "$j" | tr 'A-Z' 'a-z')
  if echo "$b" | grep -qE "$CLIENT_ONLY"; then echo "SKIP (client-only) $(basename "$j")"; else cp "$j" run/mods/; fi
done | tee pack_selection.txt
echo "LOADED $(ls run/mods | wc -l) of $(ls pack/mods/*.jar | wc -l) pack jars" | tee -a pack_selection.txt
cp -r pack/overrides/config run/config 2>/dev/null || true
cp -r pack/overrides/kubejs run/kubejs 2>/dev/null || true
cp -r pack/overrides/defaultconfigs run/defaultconfigs 2>/dev/null || true
echo "eula=true" > run/eula.txt
printf "level-seed=frontiers\nmax-tick-time=-1\nspawn-protection=0\nonline-mode=false\ndifficulty=normal\n" > run/server.properties
rm -f run/logs/latest.log
export UF_SMOKE="${UF_SMOKE_FILE:-$PWD/ci/pack_smoke_commands.txt}"
# Client-only mods that the name list missed refuse to construct on a dedicated server ("invalid dist"); drop each one
# named in the crash report or seen in the stack trace and boot again, at most 8 times. Each dropped mod is listed in pack_selection.txt.
for attempt in 1 2 3 4 5 6 7 8; do
  rm -rf run/crash-reports run/world
  timeout 2400 gradle runServer --no-daemon < /dev/null > server_console.log 2>&1
  code=$?
  grep -q "SMOKE finished" run/logs/latest.log 2>/dev/null && break
  grep -q "invalid dist DEDICATED_SERVER" server_console.log run/crash-reports/*.txt 2>/dev/null || break
  bad=$(python3 ci/pack/client_only_culprits.py run/mods server_console.log run/crash-reports/*.txt 2>/dev/null)
  [ -n "$bad" ] || break
  for j in $bad; do echo "SKIP (client-only, refused on a server) $(basename $j)" | tee -a pack_selection.txt; rm -f "$j"; done
done
echo "server exited: $code"
if [ -n "${UF_WORLD_ONLY:-}" ]; then
  grep -E "SMOKE>|SMOKE FAILED|LANDMARK |Built " run/logs/latest.log | cut -c1-300
  grep -q "SMOKE finished" run/logs/latest.log
  exit $?
fi
L=run/logs/latest.log
echo "==== mods loaded ===="
grep -E "Unstable Frontiers loading|Loading [0-9]+ mods|Done \(" $L | cut -c1-200
echo "==== dependency problems ===="
grep -A25 "Missing or unsupported mandatory dependencies" $L | head -40 | cut -c1-300
echo "==== errors (first 120) ===="
grep -nE "ERROR|Exception|Caused by" $L | grep -vE "mixin/|DISTXFORM" | cut -c1-300 | head -120
echo "==== console tail ===="
grep -vE "mixin/|DISTXFORM" server_console.log | tail -80 | cut -c1-300
for c in run/crash-reports/*.txt; do [ -f "$c" ] && { echo "==== $c ===="; head -60 "$c" | cut -c1-300; }; done
echo "==== DUMP ===="
grep -E "DUMP " $L | sed 's/.*DUMP //'
echo "==== rosters ===="
grep -E "ROSTER " $L | sed 's/.*ROSTER /ROSTER /' | cut -c1-300
echo "==== landmarks ===="
grep -E "SMOKE>|SMOKE FAILED|LANDMARK |LOCATE |STATS |SITES |Built " $L | sed 's/^\[[^]]*\] \[[^]]*\] \[[^]]*\]: //' | cut -c1-400
echo "==== creature trials ===="
grep -E "TRIAL " $L | sed 's/.*TRIAL /TRIAL /' | cut -c1-300 | head -300
echo "==== data load problems ===="
grep -nE "Couldn't parse|Failed to (load|parse)|Unknown (registry|loot)|unstable_frontiers.*(ERROR|error)|Unstable Frontiers: " $L | cut -c1-400 | head -60
echo "==== checks ===="
ok=1
check() { if grep -qE "$2" $L; then echo "PASS $1"; else echo "FAIL $1"; ok=0; fi; }
nocheck() { if grep -qE "$2" $L; then echo "FAIL $1"; ok=0; else echo "PASS $1"; fi; }
check "server finished the script" "SMOKE finished"
check "Antarchy loaded with the addon" "Unstable Frontiers loading with Antarchy 2\.2\.9"
check "every roster resolves against the installed Antarchy" "rosters, 0 unusable"
nocheck "no data-load problems reported by the addon" "Unstable Frontiers: (landmark|roster)"
check "Gibbet Spire built" "Built Gibbet Spire"
check "spire wave floor spawned creatures" "swarm_pen \[WAVES\] ACTIVE session [0-9]+ mobs [1-9]"
check "spire crown guardian spawned" "crown \[GUARDIAN\] ACTIVE session [0-9]+ mobs [1-9]"
check "spire crown cleared and its gate opened" "gates open \[crown\]"
check "gaol cell prisoner spawned" "cell_south \[CELL\] ACTIVE session [0-9]+ mobs [1-9]"
check "gaol warden spawned" "warden \[GUARDIAN\] ACTIVE session [0-9]+ mobs [1-9]"
check "rookery roost spawned" "roost \[ROOST\] ACTIVE session [0-9]+ mobs [1-9]"
check "rookmother spawned" "rookmother \[GUARDIAN\] ACTIVE session [0-9]+ mobs [1-9]"
check "hive brood spawned" "brood \[BROOD\] ACTIVE"
check "hive tyrant spawned" "royal \[GUARDIAN\] ACTIVE session [0-9]+ mobs [1-9]"
check "great cage finale spawned" "finale \[FINALE\] ACTIVE session [0-9]+ mobs [1-9]"
check "great cage lock gate opened" "gates open \[.*lock"
check "natural camps generate" "LOCATE camp"
check "natural landmarks generate" "LOCATE any"
check "the Great Cage generates" "LOCATE great_cage"
nocheck "no creature trial step failed" "TRIAL FAIL"
check "gnashback: tell before the charge" "TRIAL PASS gnashback tells its charge"
check "gnashback: a dodged charge stuns it" "TRIAL PASS a dodged charge into a wall stuns"
check "gnashback: stunned back takes double" "TRIAL PASS stunned gnashback takes"
check "gnashback: an undodged charge hits" "TRIAL PASS an undodged gnashback charge hits"
check "shrikewing: flies" "TRIAL PASS shrikewing stays aloft"
check "shrikewing: tell before the dive" "TRIAL PASS shrikewing screeches"
check "shrikewing: a dodged dive leaves it open" "TRIAL PASS a dodged dive"
check "shrikewing: an undodged dive hits" "TRIAL PASS an undodged dive hits"
check "matriarch: waits dormant in the cage" "TRIAL PASS the Matriarch waits in the cage"
check "matriarch: dormant cannot be hurt" "TRIAL PASS the dormant Matriarch cannot be hurt"
check "matriarch: the key wakes her, chained" "TRIAL PASS the key wakes the same Matriarch"
check "matriarch: chained damage reduction" "TRIAL PASS chained, she takes"
check "matriarch: scythe sweep" "TRIAL PASS scythe sweep"
check "matriarch: acid volley" "TRIAL PASS acid volley"
check "matriarch: brood call opening" "TRIAL PASS brood call: the open sac"
check "matriarch: brood call escorts" "TRIAL PASS brood call brought escorts"
check "matriarch: pylons snap the chains" "TRIAL PASS breaking the pylons frees her"
check "matriarch: full damage when free" "TRIAL PASS free, she takes"
check "matriarch: leap" "TRIAL PASS leap"
check "matriarch: death clears the Great Cage" "TRIAL PASS killing her clears the Great Cage"
check "observatory built" "Built The Rift Observatory"
check "observatory hall waves" "hall \[WAVES\] ACTIVE session [0-9]+ mobs [1-9]"
check "observatory vaults brood" "vaults \[BROOD\] ACTIVE"
check "observatory gatehouse ambush" "gatehouse \[AMBUSH\] ACTIVE"
check "observatory dome guardian after the seal lifts" "dome \[GUARDIAN\] ACTIVE session [0-9]+ mobs [1-9]"
check "observatory: the dome is sealed at first" "TRIAL PASS the Lens Dome is sealed"
check "observatory: the seal lifts" "TRIAL PASS clearing the Hall and the Vaults unseals"
check "observatory: the engine takes its parts" "TRIAL PASS the engine takes its three parts"
check "observatory: the engine opens the gate" "TRIAL PASS the waking engine opens the rift gate"
check "observatory: the lift unseals" "TRIAL PASS the waking engine unseals the lift"
check "warden: tell before the beam" "TRIAL PASS orrery warden aligns its rings"
check "warden: beam hits in the open" "TRIAL PASS the beam hits a target in the open"
check "warden: stalled takes double" "TRIAL PASS after the beam it stalls"
check "warden: cover stops the beam" "TRIAL PASS cover taken during the tell stops the beam"
check "mite: flies" "TRIAL PASS lumen mite stays aloft"
check "mite: tell before the spit" "TRIAL PASS lumen mite swells"
check "mite: bolts expire" "TRIAL PASS star bolts are gone"
check "abyss: places build" "TRIAL PASS hollow_crown built on its island"
check "abyss: safe arrival" "TRIAL PASS arrivals stand on the landing"
check "abyss: return gate open" "TRIAL PASS the landing's return gate stands open"
check "abyss: void catch" "TRIAL PASS a fall into the void is caught"
check "abyss: the catch never kills" "TRIAL PASS the catch never takes the last"
check "abyss: item rescue" "TRIAL PASS an item dropped into the void drifts"
check "abyss: starwell waves" "starwell \[WAVES\] ACTIVE session [0-9]+ mobs [1-9]"
check "leviathan: summoned at the altar" "TRIAL PASS the altar takes the sigil"
check "leviathan: shielded while rising" "TRIAL PASS the rising Leviathan cannot be hurt"
check "leviathan: one at a time" "TRIAL PASS only one Leviathan at a time"
check "leviathan: phase one attacks told" "TRIAL PASS phase one: beam, low pass and gravity well"
check "leviathan: keeps to its arena" "TRIAL PASS the Leviathan keeps to its arena"
check "leviathan: phase two" "TRIAL PASS phase two at two thirds"
check "leviathan: mites capped" "TRIAL PASS phase two calls Lumen Mites"
check "leviathan: eclipse and exposed" "TRIAL PASS phase three: the eclipse dive"
check "leviathan: save and load" "TRIAL PASS its phase, arena and mites survive"
check "leviathan: orphan refused" "TRIAL PASS a Leviathan with no fight to belong to"
check "leviathan: abandoned fight resets" "TRIAL PASS with nobody in the arena"
check "leviathan: charged altar recalls" "TRIAL PASS the charged altar calls it again"
check "leviathan: victory rewards" "TRIAL PASS victory: rewards owed"
[ $ok = 1 ]
