#!/bin/bash
# r75-scout probe helper: probe.sh LABEL "command"  -> bounded, rc+wall recorded.
# All probes run under `timeout -s KILL 15` (fifo-open blocks are SIGTERM-immune
# per SHARED.md carried guards). Outputs land in corpus/live/r75-scout/legs/.
label="$1"; cmd="$2"
outdir="corpus/live/r75-scout/legs"
mkdir -p "$outdir"
t0=$(date +%s%N)
timeout -s KILL 15 bash -c "$cmd" >"$outdir/$label.stdout" 2>"$outdir/$label.stderr"
rc=$?
t1=$(date +%s%N)
echo "$label rc=$rc wall_ms=$(( (t1-t0)/1000000 ))"
