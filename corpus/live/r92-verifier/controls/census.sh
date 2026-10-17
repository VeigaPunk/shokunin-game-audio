#!/usr/bin/env bash
# r92 verifier host census — r92a residue + daemon health + family locks.
# Read-only: only bounded queries, no set-default-*, no writes.
set -u
echo "=== census at $(date -u +%Y-%m-%dT%H:%M:%SZ)  loadavg=$(cat /proc/loadavg)"
echo "--- pactl info (bounded 12s):"
timeout 12 pactl info 2>&1 | sed -n '1,4p'; echo "pactl_info_rc=$?"
echo "--- r92a residue (host graph):"
timeout 25 pw-dump 2>/dev/null | grep -c 'r92a' || echo "pw-dump rc=$? (no r92a match)"
timeout 12 pw-cli ls Node 2>/dev/null | grep -c 'r92a' || echo "pw-cli ls Node rc=$?"
echo "--- r92a residue (pactl rows):"
timeout 12 pactl list short modules 2>/dev/null | grep -c 'r92a' || true
timeout 12 pactl list short sinks 2>/dev/null | grep -c 'r92a' || true
timeout 12 pactl list short sources 2>/dev/null | grep -c 'r92a' || true
echo "--- r92a residue (processes):"
ps -ef | grep -c '[r]92a' || true
echo "--- own lock files (fixed corpus/live paths, per tree):"
for d in /home/vgpnk/r92-verifier/tree-r92 /home/vgpnk/r92-verifier/tree-head \
         /home/vgpnk/Projects/shokunin/audio-shokunin \
         /home/vgpnk/Projects/shokunin/audio-shokunin-wt-r92; do
  f="$d/corpus/live/measure_audio-filterchain-r92.lock"
  if [ -e "$f" ]; then echo "$f -> $(cat "$f" 2>/dev/null | tr '\n' ' ') [mtime $(stat -c %y "$f")]"; else echo "$f -> absent"; fi
done
echo "--- default sink/source (recorded, never written):"
timeout 12 pactl get-default-sink 2>&1; timeout 12 pactl get-default-source 2>&1
echo "--- foreign family runs live (measure_audio.py):"
ps -ef | grep '[m]easure_audio.py' | awk '{print $2, $NF, $(NF-1)}' | sort | uniq -c | head -20
echo "=== end census"
