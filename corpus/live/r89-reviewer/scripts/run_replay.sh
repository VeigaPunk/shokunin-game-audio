#!/bin/bash
# r89 reviewer replay runner — frozen tree 0d732989, fixed TMPDIR, timestamps.
# usage: run_replay.sh <label> <tmpdir>
set -u
ROOTDIR=/home/vgpnk/Projects/shokunin/audio-shokunin
TREE=$ROOTDIR/corpus/live/r89-reviewer/tree
LABEL=$1
TMPD=$2
LOGD=$ROOTDIR/corpus/live/r89-reviewer/runs
export TMPDIR="$TMPD"
export PYTHONDONTWRITEBYTECODE=1
cd "$TREE" || exit 97
start=$(date +%s.%N)
load0=$(cat /proc/loadavg)
timeout 900 python3 corpus/fixtures/measure_audio.py --probe-pwprof-r89 \
    > "$LOGD/$LABEL.stdout" 2> "$LOGD/$LABEL.stderr"
rc=$?
end=$(date +%s.%N)
load1=$(cat /proc/loadavg)
printf '%s start=%s end=%s rc=%s load_start=[%s] load_end=[%s]\n' \
    "$LABEL" "$start" "$end" "$rc" "$load0" "$load1" >> "$LOGD/timeline.log"
exit $rc
