#!/usr/bin/env bash
# r91 VERIFIER — exit census. Read-only: prints host state after every run.
set -u
TREE=/home/vgpnk/r91-verify-tree
echo "== census at $(date -u +%Y-%m-%dT%H:%M:%SZ) =="
echo "-- loadavg: $(cat /proc/loadavg)"
echo "-- defaults:"
echo "   sink=$(pactl get-default-sink)  source=$(pactl get-default-source)"
echo "-- r91* modules: $(pactl list modules short 2>/dev/null | grep -c 'r91')"
echo "-- r91* sinks:   $(pactl list sinks short 2>/dev/null | grep -c 'r91')"
echo "-- r91* sources: $(pactl list sources short 2>/dev/null | grep -c 'r91')"
echo "-- r91* nodes (pw-dump): $(pw-dump 2>/dev/null | grep -c 'r91a_\|r91l_\|r91v_')"
echo "-- r91* processes:"
ps -eo pid,etime,cmd | grep -E 'r91a_|r91l_|r91v_|gstfreeze_r91|probe-gstfrz' | grep -v grep | grep -v census.sh || echo "   (none)"
echo "-- lock files:"
for f in "$TREE/corpus/live/measure_audio-gstfrz-r91.lock" \
         /home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/measure_audio-gstfrz-r91.lock; do
  if [ -e "$f" ]; then echo "   $(stat -c '%s bytes %y' "$f")  $f"; cat "$f" | sed 's/^/     /'; else echo "   absent: $f"; fi
done
echo "-- tree fixture shas (must equal the committed blobs):"
sha256sum "$TREE/corpus/fixtures/measure_audio.py" "$TREE/corpus/fixtures/gstfreeze_r91_resume.py"
echo "-- tree runs (this seat):"
ls -1d "$TREE"/corpus/live/runs/*gstfrz-r91* 2>/dev/null | tail -5
