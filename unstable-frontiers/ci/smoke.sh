#!/usr/bin/env bash
# Boots a dedicated Forge server with the addon (no Antarchy, so the vanilla stand-ins are used), builds a tower in the
# frontier, runs fights on three of its stages, lets one reset itself, then stops and reports. Run from this folder after
# `gradle build`. The commands in ci/smoke_commands.txt are run by the mod itself (debug/SmokeTest) when UF_SMOKE is set.
set -u
mkdir -p run
echo "eula=true" > run/eula.txt
printf "level-seed=frontiers\nmax-tick-time=-1\nspawn-protection=0\nonline-mode=false\ndifficulty=normal\n" > run/server.properties
rm -f run/logs/latest.log
export UF_SMOKE="$PWD/ci/smoke_commands.txt"
timeout 1800 gradle runServer --no-daemon < /dev/null > server_console.log 2>&1
echo "server exited: $?"
L=run/logs/latest.log
echo "==== startup ===="
grep -E "Done \(|Unstable Frontiers loading|SMOKE start|SMOKE finished" $L | cut -c1-220
echo "==== errors and exceptions ===="
grep -nE "ERROR|Exception|Caused by|Failed to|Couldn't|Roster entry" $L | grep -v "Realms\|realms-telemetry\|Narrator" | cut -c1-400 | head -150
echo "==== command output ===="
grep -E "SMOKE>|SMOKE ok|SMOKE FAILED|tower [0-9-]+ centre|Built a cage tower|towers known|Nearest cage tower|reset:|started stage" $L | cut -c1-400
echo "==== checks ===="
ok=1
check() { if grep -qE "$2" $L; then echo "PASS $1"; else echo "FAIL $1"; ok=0; fi; }
check "server finished the script" "SMOKE finished"
check "tower built and registered" "Built a cage tower"
check "tower found by the encounter lookup" "tower [0-9-]+ centre"
check "a floor spawned creatures" "active=swarm_pen wave=[1-9][0-9]* alive=[1-9]"
check "idle floor reset itself" "active=none wave=0 alive=0 session=2"
check "crown guardian spawned" "active=crown wave=1 alive=[1-9]"
check "natural towers locatable" "Nearest cage tower"
if grep -qE "SMOKE FAILED|SMOKE ok \(0\)" $L; then echo "FAIL a command failed or returned 0:"; grep -E "SMOKE FAILED|SMOKE ok \(0\)" $L | cut -c1-300; ok=0; fi
if grep -qE "Exception|Caused by" $L; then echo "FAIL exceptions in the log"; ok=0; fi
[ $ok = 1 ]
