#!/usr/bin/env bash
# Boots a dedicated server with the addon and the Integrated Boogaloo mods it depends on or touches (picked, with every
# dependency, from the real pack in ./pack), using the pack's own configs and server scripts. Run after fetch_pack.py
# and `gradle build`, from the addon folder.
set -u
rm -rf run/mods run/config run/kubejs run/world
mkdir -p run/mods
python3 ci/pack/select_mods.py pack/mods run/mods antarchy integrated_superheroes morph boogaloo_core electric_boogaloo kubejs \
  marvel marvellegacy viltrumitecore lootr curios bettercombat | tee pack_selection.txt
cp -r pack/overrides/config run/config 2>/dev/null || true
mkdir -p run/kubejs && cp -r pack/overrides/kubejs/server_scripts run/kubejs/ 2>/dev/null || true
echo "eula=true" > run/eula.txt
printf "level-seed=frontiers\nmax-tick-time=-1\nspawn-protection=0\nonline-mode=false\ndifficulty=normal\n" > run/server.properties
rm -f run/logs/latest.log
export UF_SMOKE="$PWD/ci/pack_smoke_commands.txt"
timeout 2400 gradle runServer --no-daemon < /dev/null > server_console.log 2>&1
echo "server exited: $?"
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
