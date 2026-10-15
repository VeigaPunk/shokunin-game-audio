#!/usr/bin/env bash
# r82-baseline post-state snapshot (host + tree + HEAD at exit).
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r82-baseline
{
  echo "at: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "HEAD: $(git rev-parse HEAD)"
  echo "HEAD_subject: $(git log --oneline -1)"
  echo "worktree_fixture_sha256: $(sha256sum corpus/fixtures/measure_audio.py | cut -d' ' -f1)"
  echo "tree_fixture_sha256: $(sha256sum "$OUT/tree/corpus/fixtures/measure_audio.py" | cut -d' ' -f1)"
  echo "worktree_tracked_dirty: '$(git status --porcelain --untracked-files=no | tr '\n' ';')'"
  echo "--- default"
  pactl info 2>/dev/null | grep -E "Default (Sink|Source)"
  echo "--- sinks"
  pactl list short sinks
  echo "--- sources"
  pactl list short sources
  echo "--- module count"
  pactl list short modules | wc -l
  echo "--- foreign r*/gst modules"
  pactl list short modules 2>/dev/null | grep -E 'r78|r79|r80|r81|r82|r83|r84|r91|r92|r93|gst' || echo "(none)"
  echo "--- foreign r*/gst nodes"
  pw-dump 2>/dev/null | python3 -c '
import json,sys
d=json.load(sys.stdin)
for n in d:
    if n["type"]!="PipeWire:Interface:Node": continue
    name=n["info"].get("props",{}).get("node.name","")
    if name.startswith(("r78","r79","r80","r81","r82","r83","r84","r91","r92","r93","gst_","ffplay","Lavf")):
        print(f"  id={n[\"id\"]} node.name={name!r}")
' 2>/dev/null || true
  echo "--- foreign processes"
  pgrep -af "measure_audio|pw-cat|pw-play|pw-record|pw-loopback|parec|gst-launch|ffmpeg|ffplay" | grep -v pgrep || echo "(none)"
  echo "--- canonical runs dir count (worktree)"
  find corpus/live/runs -maxdepth 1 -type d | wc -l
  echo "--- tree runs dir count (frozen scratch)"
  find "$OUT/tree/corpus/live/runs" -maxdepth 1 -type d | wc -l
} > "$OUT/post-state.txt" 2>&1
cat "$OUT/post-state.txt"
