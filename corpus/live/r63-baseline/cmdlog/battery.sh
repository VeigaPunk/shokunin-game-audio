#!/bin/bash
# R63 baseline: frozen-tree serial replay of the r62 designated 84-command
# ledger (verbatim order from corpus/live/r62-author/scratch/run_ledger.sh /
# ledger-r62.tsv). Runs from the extracted HEAD tree root; measure_audio.py
# has no --runs flag, so receipts hard-write to tree/corpus/live/runs/ which
# is inside this scratch scope. Per-command stdout/stderr/exit -> cmdlog/NN.*.
TREE=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r63-baseline/tree
LOG=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r63-baseline/cmdlog
cd "$TREE" || exit 99
M=corpus/fixtures/measure_audio.py
OUT="$LOG/ledger-r63-baseline.tsv"
: > "$OUT"
i=0
run() {
  i=$((i+1))
  n=$(printf '%02d' "$i")
  python3 "$M" "$@" > "$LOG/$n.stdout" 2> "$LOG/$n.stderr"
  code=$?
  printf '%s' "$code" > "$LOG/$n.exit"
  receipt=$(python3 -c 'import json,sys
try:
  d=json.load(open(sys.argv[1])); print(d.get("receipt",""))
except Exception: print("")' "$LOG/$n.stdout" 2>/dev/null)
  fails=$(python3 -c 'import json,sys
try:
  d=json.load(open(sys.argv[1])); f=d.get("failures",{}); print("; ".join(f"{k}: "+"; ".join(map(str,v)) for k,v in f.items()) if f else "none")
except Exception: print("PARSE_FAIL")' "$LOG/$n.stdout" 2>/dev/null)
  printf '%02d\t%d\t%s\t%s\n' "$i" "$code" "$receipt" "$fails" >> "$OUT"
  echo "done $i exit=$code"
}
run
run --probe-ui-extensible-valid-24-r62
run --probe-ui-extensible-valid-32-r62
run --probe-ui-extensible-valid-17-r61
run --probe-ui-extensible-valid-16-r61
run --probe-ui-extensible-valid-0-r60
run --probe-ui-extensible-valid-16-r60
run --probe-ui-extensible-valid-13-r59
run --probe-ui-extensible-valid-16-r59
run --probe-ui-extensible-valid-14-r58
run --probe-ui-extensible-valid-16-r58
run --probe-ui-extensible-valid-15
run --probe-ui-extensible-valid-16
run --probe-ui-extensible-mask-zero
run --probe-ui-extensible-mask-center
run --probe-ui-extensible-pcm16
run --probe-ui-standard-pcm16-r55
run --probe-ui-pcm32
run --probe-ui-pcm16-r54
run --probe-ui-float32
run --probe-ui-pcm16-r53
run --probe-ui-pcm8
run --probe-ui-pcm16-r52
run --probe-ui-pcm24
run --probe-ui-pcm16
run --probe-ui-channel-stereo
run --probe-ui-channel-mono
run --probe-ui-rate-48001
run --probe-ui-rate-48000-r49
run --probe-ui-rate-47999
run --probe-ui-rate-48000
run --probe-ui-upper-centroid-below
run --probe-ui-upper-centroid-above
run --probe-ui-absolute-centroid-below
run --probe-ui-absolute-centroid-above
run --probe-ui-lower-tolerance-5713
run --probe-ui-lower-tolerance-5711
run --probe-ui-tolerance-5807
run --probe-ui-tolerance-5809
run --probe-ui-crest-46
run --probe-ui-crest-47
run --probe-ui-peak-31129
run --probe-ui-peak-31130
run --probe-outer-slope-32
run --probe-outer-slope-33
run --probe-outer-endpoint-983
run --probe-outer-endpoint-984
run --probe-ambience-orientation-forward
run --probe-ambience-orientation-reverse
run --probe-ambience-centroid-above
run --probe-ambience-centroid-below
run --probe-ui-mixed-pass
run --probe-ui-joint-below
run --probe-ui-orientation-forward
run --probe-ui-orientation-reverse
run --probe-ui-lower-centroid-below
run --probe-ui-lower-centroid-above
run --probe-ui-centroid-below
run --probe-ui-centroid-above
run --probe-ui-duration-below
run --probe-ui-duration-at
run --probe-ui-clone
run --probe-layer-third-join-edge-pass
run --probe-layer-third-join-edge-fail
run --probe-layer-third-join
run --probe-layer-third-slope-edge-pass
run --probe-layer-third-slope-edge-fail
run --probe-layer-third-slope
run --probe-layer-alt-reverse
run --probe-layer-alt-slope
run --probe-layer-alt-join
run --probe-layer-alt-flat
run --probe-layer-slope
run --probe-layer-join
run --probe-flat
run --probe-layer-flat
run --probe-slope
run --probe-failing
run --probe-invalid
run
run
run
run
run
echo "LEDGER_COMPLETE total=$i"
