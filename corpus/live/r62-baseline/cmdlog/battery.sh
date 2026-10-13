#!/usr/bin/env bash
# r62 baseline frozen replay — commands 2..82 of the r61-verifier 82-command
# ledger, run serially inside the git-archive HEAD snapshot at ./tree.
# Command 01 (normal) was already run manually as the standalone smoke test.
set -u
SCRATCH="$(cd "$(dirname "$0")" && pwd)"
TREE="$SCRATCH/../tree"
cd "$TREE" || exit 99

run() {  # NN flag...
  local nn="$1"; shift
  python3 corpus/fixtures/measure_audio.py "$@" \
      > "$SCRATCH/../cmdlog/$nn.stdout" 2> "$SCRATCH/../cmdlog/$nn.stderr"
  echo "$?" > "$SCRATCH/../cmdlog/$nn.exit"
  printf '%s exit=%s\n' "$nn" "$(cat "$SCRATCH/../cmdlog/$nn.exit")"
}

run 02 --probe-ui-extensible-valid-17-r61
run 03 --probe-ui-extensible-valid-16-r61
run 04 --probe-ui-extensible-valid-0-r60
run 05 --probe-ui-extensible-valid-16-r60
run 06 --probe-ui-extensible-valid-13-r59
run 07 --probe-ui-extensible-valid-16-r59
run 08 --probe-ui-extensible-valid-14-r58
run 09 --probe-ui-extensible-valid-16-r58
run 10 --probe-ui-extensible-valid-15
run 11 --probe-ui-extensible-valid-16
run 12 --probe-ui-extensible-mask-zero
run 13 --probe-ui-extensible-mask-center
run 14 --probe-ui-extensible-pcm16
run 15 --probe-ui-standard-pcm16-r55
run 16 --probe-ui-pcm32
run 17 --probe-ui-pcm16-r54
run 18 --probe-ui-float32
run 19 --probe-ui-pcm16-r53
run 20 --probe-ui-pcm8
run 21 --probe-ui-pcm16-r52
run 22 --probe-ui-pcm24
run 23 --probe-ui-pcm16
run 24 --probe-ui-channel-stereo
run 25 --probe-ui-channel-mono
run 26 --probe-ui-rate-48001
run 27 --probe-ui-rate-48000-r49
run 28 --probe-ui-rate-47999
run 29 --probe-ui-rate-48000
run 30 --probe-ui-upper-centroid-below
run 31 --probe-ui-upper-centroid-above
run 32 --probe-ui-absolute-centroid-below
run 33 --probe-ui-absolute-centroid-above
run 34 --probe-ui-lower-tolerance-5713
run 35 --probe-ui-lower-tolerance-5711
run 36 --probe-ui-tolerance-5807
run 37 --probe-ui-tolerance-5809
run 38 --probe-ui-crest-46
run 39 --probe-ui-crest-47
run 40 --probe-ui-peak-31129
run 41 --probe-ui-peak-31130
run 42 --probe-outer-slope-32
run 43 --probe-outer-slope-33
run 44 --probe-outer-endpoint-983
run 45 --probe-outer-endpoint-984
run 46 --probe-ambience-orientation-forward
run 47 --probe-ambience-orientation-reverse
run 48 --probe-ambience-centroid-above
run 49 --probe-ambience-centroid-below
run 50 --probe-ui-mixed-pass
run 51 --probe-ui-joint-below
run 52 --probe-ui-orientation-forward
run 53 --probe-ui-orientation-reverse
run 54 --probe-ui-lower-centroid-below
run 55 --probe-ui-lower-centroid-above
run 56 --probe-ui-centroid-below
run 57 --probe-ui-centroid-above
run 58 --probe-ui-duration-below
run 59 --probe-ui-duration-at
run 60 --probe-ui-clone
run 61 --probe-layer-third-join-edge-pass
run 62 --probe-layer-third-join-edge-fail
run 63 --probe-layer-third-join
run 64 --probe-layer-third-slope-edge-pass
run 65 --probe-layer-third-slope-edge-fail
run 66 --probe-layer-third-slope
run 67 --probe-layer-alt-reverse
run 68 --probe-layer-alt-slope
run 69 --probe-layer-alt-join
run 70 --probe-layer-alt-flat
run 71 --probe-layer-slope
run 72 --probe-layer-join
run 73 --probe-flat
run 74 --probe-layer-flat
run 75 --probe-slope
run 76 --probe-failing
run 77 --probe-invalid
run 78
run 79
run 80
run 81
run 82
echo '=== battery done ==='
