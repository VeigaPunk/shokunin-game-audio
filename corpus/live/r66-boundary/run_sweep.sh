#!/usr/bin/env bash
# r66-boundary sweep runner — detect-only (file mode) over probes/sweep/.
# Regenerates runs/sweep.tsv: <fixture>\t<detected|->
set -u
cd "$(dirname "$0")"
TSV=runs/sweep.tsv
: > "$TSV"
for f in probes/sweep/*.bin; do
  n=$(basename "$f")
  det=$(sox -V4 "$f" -n stat 2>&1 | grep -o "detected file format type \`[^']*'" | head -1 | sed "s/.*\`//;s/'//")
  printf '%s\t%s\n' "$n" "${det:--}" >> "$TSV"
done
echo "sweep: $(wc -l < "$TSV") rows"
