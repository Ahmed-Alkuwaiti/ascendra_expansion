#!/usr/bin/env bash
# Boots a dedicated Forge server with the mod, generates land in every realm, places every structure and template once,
# then stops and reports every error the log shows. Run from the repository root after `gradle build`.
# The commands in ci/smoke_commands.txt are run by the mod itself (com.aurelia.event.SmokeTest) when AURELIA_SMOKE is set.
set -u
mkdir -p run
echo "eula=true" > run/eula.txt
printf "level-seed=aurelia\nmax-tick-time=-1\nspawn-protection=0\nonline-mode=false\n" > run/server.properties
rm -f run/logs/latest.log
export AURELIA_SMOKE="$PWD/ci/smoke_commands.txt"
timeout 2400 gradle runServer --no-daemon < /dev/null > server_console.log 2>&1
echo "server exited: $?"
L=run/logs/latest.log
echo "==== startup ===="
grep -E "Done \(|SMOKE start|SMOKE finished" $L | cut -c1-200
echo "==== errors and exceptions ===="
grep -nE "ERROR|Exception|Caused by|Failed to|Couldn't" $L | grep -v "Realms\|realms-telemetry\|Narrator" | cut -c1-400 | head -150
echo "==== command results ===="
echo "ok: $(grep -c 'SMOKE ok' $L)   failed: $(grep -c 'SMOKE FAILED' $L)   of $(grep -cv '^\s*$' ci/smoke_commands.txt)"
grep -E "SMOKE FAILED|SMOKE ok \(0\)" $L | cut -c1-300
grep -q "SMOKE finished" $L && ! grep -q "SMOKE FAILED" $L
