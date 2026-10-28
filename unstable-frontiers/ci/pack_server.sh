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
export UF_SMOKE="$PWD/ci/pack_smoke_commands.txt"
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
grep -E "SMOKE>|SMOKE FAILED|LANDMARK |LOCATE |STATS |Built " $L | sed 's/^\[[^]]*\] \[[^]]*\] \[[^]]*\]: //' | cut -c1-400
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
[ $ok = 1 ]
