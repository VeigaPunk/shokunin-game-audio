#!/usr/bin/env bash
# r92 verifier — mutation / negative controls (entry-level; the point is the
# ARM's detection).  Each runs ONE entry function from a mutated hardlink
# copy of the frozen landing tree.
set -u
R=/home/vgpnk/r92-verifier
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
run() { # tree entry tag scratch
  echo "=== $3 ($2 from $1) at $(date -u +%H:%M:%SZ)"
  ( cd "$1" && UFO_FC92_SCRATCH="$4" timeout -s KILL 1200 \
      python3 "$R/runs/run_entry.py" "$1" "$2" "$3" ) \
      > "$R/runs/mut-$3.json" 2> "$R/runs/mut-$3.stderr.log"
  echo "rc=$? -> runs/mut-$3.json"
  python3 - "$R/runs/mut-$3.json" <<'EOF'
import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print('  failures:', json.dumps(d.get('failures'))[:400])
    print('  coverage_blocked:', json.dumps(d.get('coverage_blocked'))[:200])
    print('  own_nodes_after:', d.get('own_nodes_after'))
    print('  legs:', len(d.get('legs') or []))
except Exception as e:
    print('  unreadable:', e)
EOF
}
# M1 armed-constant mutation (d_gneg140 clamp centre -46.362 -> -40.000)
run "$R/tree-mutarm" filterchain_dsp_r92_probe mutarm "$R/scratch/mutarm"
# M2 fixture/stimulus mutation (2-tap IR second tap 64 -> 70)
run "$R/tree-mutir" filterchain_ir_r92_probe mutir "$R/scratch/mutir"
# M3 no-op control (comment-only insertion in the r92 block)
run "$R/tree-mutnoop" filterchain_dsp_r92_probe mutnoop "$R/scratch/mutnoop"
echo "=== M5 coverage-block naming control (wpexec removed from PATH) at $(date -u +%H:%M:%SZ)"
( cd "$R/tree-r92" && PATH="$R/pathfarm-nopwpx" UFO_FC92_SCRATCH="$R/scratch/mutnopwpx" \
    timeout -s KILL 300 python3 "$R/runs/run_entry.py" "$R/tree-r92" filterchain_wpx_r92_probe mutnopwpx ) \
    > "$R/runs/mut-mutnopwpx.json" 2> "$R/runs/mut-mutnopwpx.stderr.log"
echo "rc=$?"
python3 - "$R/runs/mut-mutnopwpx.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1]))
print('  failures:', json.dumps(d.get('failures')))
print('  coverage_blocked:', json.dumps(d.get('coverage_blocked')))
print('  blocked:', d.get('blocked'))
print('  legs:', len(d.get('legs') or []))
EOF
echo "=== mutation controls done at $(date -u +%H:%M:%SZ)"
