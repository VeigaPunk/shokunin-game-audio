#!/usr/bin/env bash
# r90-simplifier: run every comparison pair and write one receipt per pair
# plus a one-line summary. Pairs are named <tree><tag> -> <tree><tag>.
set -u
EVID=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r90-simplifier
R=/home/vgpnk/Projects/shokunin/r90s
declare -A RUN=(
 [base.before1]=$R/base/corpus/live/runs/20261016T100056345811Z-wpstate-r90
 [f1.after1]=$R/f1/corpus/live/runs/20261016T100215992353Z-wpstate-r90
 [base.before2]=$R/base/corpus/live/runs/20261016T100335959656Z-wpstate-r90
 [f2.after2]=$R/f2/corpus/live/runs/20261016T100500273289Z-wpstate-r90
 [f1.after1b]=$R/f1/corpus/live/runs/20261016T100622524052Z-wpstate-r90
 [base.before3]=$R/base/corpus/live/runs/20261016T100744523490Z-wpstate-r90
 [f1.after1c]=$R/f1/corpus/live/runs/20261016T100947949495Z-wpstate-r90
 [f1.after1d]=$R/f1/corpus/live/runs/20261016T101111965940Z-wpstate-r90
 [base.before4]=$(ls -d $R/base/corpus/live/runs/*wpstate-r90 | tail -1)
)
PAIRS=(
 "base.before2 f2.after2        FOLD-2 primary pair (pristine -> folded, both green)"
 "base.before2 f1.after1c       FOLD-1 primary pair (pristine -> folded, both green)"
 "base.before1 f1.after1d       FOLD-1 second pair (pristine -> folded, both green)"
 "base.before2 f1.after1        FOLD-1 pair with the host race firing (folded run red)"
 "base.before1 base.before2     CONTROL identical bytes (pristine vs pristine)"
 "base.before2 base.before3     CONTROL identical bytes (pristine vs pristine; 2nd red)"
 "base.before3 base.before4     CONTROL identical bytes (pristine vs pristine; 3rd)"
 "f1.after1c   f1.after1d       CONTROL folded vs folded (same folded bytes)"
)
: > "$EVID/summary.txt"
for p in "${PAIRS[@]}"; do
  a=${p%% *}; rest=${p#* }; b=${rest%% *}; note=${rest#* }
  out="$EVID/cmp-$a-vs-$b.txt"
  python3 "$EVID/compare_runs.py" "${RUN[$a]}" "${RUN[$b]}" > "$out" 2>&1
  rc=$?
  verdict=$(grep '^VERDICT' "$out" | head -1)
  printf '%-42s %-34s %s\n' "$a -> $b" "${verdict#VERDICT: }" "rc=$rc  # $note" \
      >> "$EVID/summary.txt"
done
cat "$EVID/summary.txt"
