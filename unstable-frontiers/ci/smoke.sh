#!/usr/bin/env bash
# Standalone check (no Integrated Boogaloo mods): boots a dedicated server with only this addon and expects NeoForge to
# refuse, naming Antarchy as the missing dependency. That refusal is the actionable error a player sees if Antarchy is
# missing; the addon never falls back to other creatures. Run from this folder after `gradle build`.
set -u
mkdir -p run
rm -rf run/mods
echo "eula=true" > run/eula.txt
rm -f run/logs/latest.log
timeout 900 gradle runServer --no-daemon < /dev/null > server_console.log 2>&1
echo "server exited: $?"
echo "==== what NeoForge said ===="
grep -iE "antarchy|Missing or unsupported|mandatory dependenc" server_console.log run/logs/latest.log 2>/dev/null | cut -c1-300 | head -20
if grep -qiE "antarchy" server_console.log run/logs/latest.log 2>/dev/null && ! grep -q "Done (" run/logs/latest.log 2>/dev/null; then
  echo "PASS without Antarchy the server stops and names it"
else
  echo "FAIL expected a missing-dependency stop naming Antarchy"
  exit 1
fi
