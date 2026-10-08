#!/usr/bin/env bash
# Boots a dedicated Forge server with the mod, generates land in every realm, places every structure and template once,
# then stops and reports every error the log shows. Run from the repository root after `gradle build`.
set -u
mkdir -p run
echo "eula=true" > run/eula.txt
printf "level-seed=aurelia\nmax-tick-time=-1\nspawn-protection=0\nonline-mode=false\n" > run/server.properties
rm -f run/logs/latest.log
mkfifo /tmp/server_in
( tail -f /tmp/server_in | timeout 1500 gradle runServer --no-daemon > server_console.log 2>&1; echo "server exited: $?" >> server_console.log ) &
exec 3>/tmp/server_in
for i in $(seq 1 240); do
  if grep -q "Done (" run/logs/latest.log 2>/dev/null; then break; fi
  if grep -q "server exited" server_console.log 2>/dev/null; then break; fi
  sleep 5
done
if grep -q "Done (" run/logs/latest.log 2>/dev/null; then
  echo "==== server is up; generating realms and placing structures ===="
  while IFS= read -r cmd; do
    echo "$cmd" >&3
    sleep 2
  done < ci/smoke_commands.txt
  sleep 20
  echo "stop" >&3
  for i in $(seq 1 60); do grep -q "server exited" server_console.log && break; sleep 5; done
fi
exec 3>&-
echo "==== startup ===="
grep -E "Done \(|server exited" run/logs/latest.log server_console.log | head
echo "==== errors and exceptions ===="
grep -nE "ERROR|Exception|Caused by|Failed to|Unknown|Couldn't" run/logs/latest.log | grep -v "Realms\|realms-telemetry\|Narrator" | head -150
echo "==== command failures ===="
grep -nE "Unknown or incomplete command|Invalid|not found|Failed to place|No such" run/logs/latest.log | head -60
grep -q "Done (" run/logs/latest.log
