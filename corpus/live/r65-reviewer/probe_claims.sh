#!/usr/bin/env bash
# r65 reviewer: spot-check the r64 knowledge entry's three sharpest claims.
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
LOG=corpus/live/r65-reviewer/claims-probe.log
: > "$LOG"
probe() {
  f="$1"
  echo "===== $f =====" | tee -a "$LOG"
  ffprobe -v error -show_entries stream=codec_name,bits_per_sample -of default=noprint_wrappers=1 "$f" 2>&1 | tee -a "$LOG"
  sox -V6 "$f" -n stat 2>&1 | grep -E "detected file format|\(ffmpeg\)|Samples read|FAIL" | tee -a "$LOG"
  sox "$f" -n stat >/dev/null 2>&1; echo "decode_exit=$?" | tee -a "$LOG"
}
echo "### CLAIM A: non-monotone step map edges (author sweep variants, tracked)" | tee -a "$LOG"
for v in 0 1 33 40 64 65 65535; do probe "corpus/live/r64-author/sweep/sweep_valid_$v.wav"; done
echo "### CLAIM B: envelope gate (my byte-patched copies of pair_valid_24)" | tee -a "$LOG"
for g in control tag0001 cb21 guid0003; do probe "corpus/live/r65-reviewer/gate_${g}_vb24.wav"; done
echo "### CLAIM C: f24le promotion + lossless-3840 (scribe cross-container variants, tracked)" | tee -a "$LOG"
for f in vb024_c32 vb024_c24 vb017_c24; do probe "corpus/live/r64-scribe/variants/$f.wav"; done
