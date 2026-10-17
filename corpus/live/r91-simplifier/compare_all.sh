#!/bin/bash
# Run every before/after pair of the r91 gate and write one cmp file each.
# tag -> tree comes from the START lines, tag -> run dir from the END lines.
set -u
here=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-simplifier
declare -A TREE RUN
while read -r line; do
  tag=$(echo "$line" | sed -nE 's/^\[([^]]+)\].*/\1/p')
  case "$line" in
    \[*\]\ START*)
      tree=$(echo "$line" | sed -nE 's/.* tree=([^ ]+).*/\1/p')
      TREE[$tag]="$tree"
      ;;
    \[*\]\ END*)
      run=$(echo "$line" | sed -nE 's/.* run=([^ ]+).*/\1/p')
      RUN[$tag]="$run"
      ;;
  esac
done < "$here/run-log.txt"
for t in "${!RUN[@]}"; do
  echo "$t tree=${TREE[$t]:-?} run=${RUN[$t]}"
done | sort
pairs="
base.before2:f1.after1
base.before2:f1.after2
base.before2:f2.after1
base.before2:f2.after2
base.before2:f3.after1
base.before1:base.before2
base.before2:base.before3
f1.after1:f1.after2
f2.after1:f2.after2
"
for p in $pairs; do
  a=${p%%:*}; b=${p##*:}
  da="${TREE[$a]:-}/${RUN[$a]:-}"
  db="${TREE[$b]:-}/${RUN[$b]:-}"
  [ -d "$da" ] || { echo "skip $a (no run: $da)"; continue; }
  [ -d "$db" ] || { echo "skip $b (no run: $db)"; continue; }
  out="$here/cmp-$a-vs-$b.txt"
  python3 "$here/compare_runs_r91.py" "$da" "$db" > "$out" 2>&1
  rc=$?
  echo "$a vs $b rc=$rc $(grep -c 'DIFFERS' "$out") differs -> $(basename "$out")"
done
