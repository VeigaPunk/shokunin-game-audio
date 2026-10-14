#!/usr/bin/env bash
# r65 reviewer: re-run the r64 boundary pairs against the committed r64 table.
# Expected (r64-author/r64-knowledge):
#   v8  pcm_u8    bps 8  bridge 11520  native 5760 exit0
#   v9  pcm_s16le bps16  bridge 5760   native 5760 exit0
#   v24 pcm_s24le bps24  bridge 3839   native FAIL exit2
#   v25 pcm_s32le bps32  bridge 2880   native FAIL exit2
#   v56 none      bps0   bridge FAIL exit2 'premature EOF'   native FAIL exit2
#   v57 pcm_s64le bps64  bridge 1440   native FAIL exit2
set -u
cd /home/vgpnk/Projects/shokunin/audio-shokunin
OUT=corpus/live/r65-reviewer
LOG=$OUT/boundary-rerun.log
: > "$LOG"
for v in 8 9 24 25 56 57; do
  f=corpus/live/round-64/pair_valid_$v.wav
  echo "===== pair_valid_$v.wav =====" | tee -a "$LOG"
  sha256sum "$f" | tee -a "$LOG"
  echo "-- ffprobe codec/bps/duration:" | tee -a "$LOG"
  ffprobe -v error -show_entries stream=codec_name,bits_per_sample:format=duration \
      -of default=noprint_wrappers=1 "$f" 2>&1 | tee -a "$LOG"
  echo "-- default-route sox -V6 -n stat (autodetect leg):" | tee -a "$LOG"
  sox -V6 "$f" -n stat 2>&1 | grep -E "detected file format|ffmpeg|Samples read|FAIL|can't" | tee -a "$LOG"
  echo "raw_exit=$?" | tee -a "$LOG"
  sox "$f" -n stat >/dev/null 2>&1; echo "decode_exit=$?" | tee -a "$LOG"
  echo "-- native forced sox -t wav -n stat:" | tee -a "$LOG"
  sox -t wav "$f" -n stat 2>&1 | grep -E "Samples read|FAIL|valid bits" | tee -a "$LOG"
  sox -t wav "$f" -n stat >/dev/null 2>&1; echo "native_exit=$?" | tee -a "$LOG"
done
