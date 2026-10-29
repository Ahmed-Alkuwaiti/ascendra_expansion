#!/usr/bin/env bash
# In-game screenshots with the whole Integrated Boogaloo pack: a server run builds the landmarks into a world, then the
# full client (all pack mods, software OpenGL under Xvfb) opens that world and plays ci/client_shots.txt. Screenshots land
# in run_client/screenshots. Run after fetch_pack.py and `gradle build`, from the addon folder.
set -u
UF_WORLD_ONLY=1 UF_SMOKE_FILE="$PWD/ci/client_world_commands.txt" bash ci/pack_server.sh || { echo "FAIL world preparation"; exit 1; }

rm -rf run_client
mkdir -p run_client/mods run_client/saves
cp pack/mods/*.jar run_client/mods/
cp -r pack/overrides/config run_client/config 2>/dev/null || true
cp -r pack/overrides/kubejs run_client/kubejs 2>/dev/null || true
cp -r pack/overrides/defaultconfigs run_client/defaultconfigs 2>/dev/null || true
cp pack/overrides/options.txt run_client/options.txt 2>/dev/null || true
cp -r run/world run_client/saves/world
rm -f run_client/saves/world/session.lock
# Light settings for software rendering; no tutorial, no narrator prompt, no pause when the window lacks focus.
python3 - <<'PY'
import os
p = 'run_client/options.txt'
opts = {}
if os.path.exists(p):
    for l in open(p, encoding='utf-8', errors='replace'):
        if ':' in l:
            k, v = l.rstrip('\n').split(':', 1)
            opts[k] = v
opts.update({'renderDistance': '8', 'simulationDistance': '6', 'guiScale': '2', 'pauseOnLostFocus': 'false',
             'onboardAccessibility': 'false', 'tutorialStep': 'none', 'skipMultiplayerWarning': 'true', 'narrator': '0',
             'fullscreen': 'false', 'joinedFirstServer': 'true', 'fov': '0.25', 'gamma': '0.6'})
open(p, 'w').write(''.join(f'{k}:{v}\n' for k, v in opts.items()))
PY
export UF_SHOTS="$PWD/ci/client_shots.txt"
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_GL_VERSION_OVERRIDE=4.6
export MESA_GLSL_VERSION_OVERRIDE=460
timeout 3600 xvfb-run -a -s "-screen 0 1280x720x24" gradle runClient --no-daemon < /dev/null > client_console.log 2>&1
echo "client exited: $?"
L=run_client/logs/latest.log
echo "==== shots ===="
grep -E "SHOTS" $L | sed 's/^\[[^]]*\] \[[^]]*\] \[[^]]*\]: //' | cut -c1-300
echo "==== errors (first 80) ===="
grep -nE "ERROR|Exception|Caused by" $L | grep -vE "mixin/|DISTXFORM" | cut -c1-300 | head -80
echo "==== geckolib / unstable_frontiers lines ===="
grep -niE "geckolib.*(error|warn|missing)|unstable_frontiers.*(error|warn|missing)" $L | cut -c1-300 | head -40
echo "==== console tail ===="
tail -60 client_console.log | cut -c1-300
for c in run_client/crash-reports/*.txt; do [ -f "$c" ] && { echo "==== $c ===="; head -80 "$c" | cut -c1-300; }; done
ls -la run_client/screenshots 2>/dev/null
grep -q "SHOTS finished" $L
