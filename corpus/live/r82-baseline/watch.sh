#!/usr/bin/env bash
# r82-baseline watcher: every 10 s, record HEAD / worktree fixture sha /
# tree fixture sha / sibling-lane census (processes + foreign nodes) /
# default sink-source / load. Appends to head-watch.log.
set -u
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
cd "$ROOT"
OUT="$ROOT/corpus/live/r82-baseline"
TREE="$OUT/tree"
FIX="$TREE/corpus/fixtures/measure_audio.py"
LOG="$OUT/head-watch.log"

while true; do
  ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  head=$(git rev-parse --short HEAD)
  wfix=$(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)
  tfix=$(sha256sum "$FIX" | cut -d' ' -f1)
  procs=$(for pid in $(pgrep -f "measure_audio|gst-launch|pw-cat|pw-play|pw-record|pw-loopback|parec|ffmpeg|ffplay" 2>/dev/null); do
            [ "$pid" = "$$" ] && continue
            cwd=$(readlink /proc/$pid/cwd 2>/dev/null || echo "?")
            printf '    pid=%s cwd=%s cmd=%s\n' "$pid" "$cwd" "$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | cut -c1-160)"
          done | head -12)
  nodes=$(pw-dump 2>/dev/null | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: sys.exit(0)
for n in d:
    if n["type"]!="PipeWire:Interface:Node": continue
    name=n["info"].get("props",{}).get("node.name","")
    if name.startswith(("r78","r79","r80","r81","r82","gst_","ffplay","Lavf","SDL")):
        print(f"    {n[\"id\"]} {name}")
' 2>/dev/null | head -12)
  defsrc=$(pactl info 2>/dev/null | grep -E "Default (Sink|Source)" | tr '\n' ' ')
  load=$(awk '{print $1}' /proc/loadavg)
  {
    printf '%s head=%s wfix=%s tfix=%s load=%s def=[%s]\n' "$ts" "$head" "${wfix:0:12}" "${tfix:0:12}" "$load" "$defsrc"
    if [ -n "$procs" ]; then echo "  sibling-procs:"; echo "$procs"; fi
    if [ -n "$nodes" ]; then echo "  foreign-nodes:"; echo "$nodes"; fi
  } >> "$LOG"
  sleep 10
done
