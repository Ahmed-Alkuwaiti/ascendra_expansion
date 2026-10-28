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
grep -nE "ERROR|Exception|Caused by" $L | cut -c1-300 | head -120
echo "==== DUMP ===="
grep -E "DUMP " $L | sed 's/.*DUMP //'
echo "==== commands ===="
grep -E "SMOKE>|SMOKE ok|SMOKE FAILED|tower [0-9-]+ centre|towers known|Built a cage" $L | cut -c1-300
grep -q "SMOKE finished" $L
