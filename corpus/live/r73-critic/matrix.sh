#!/bin/bash
# r73-critic: consolidated consumer matrix (pw-cat + mpv; file + fifo) over the
# canonical 9 transport members + 4 lengate extras. Machine-written receipts:
# matrix.tsv (member,consumer,transport,rc,wall_ms,stderr1,log_mech) in r73-critic/.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin
L=$R/corpus/live
O=$R/corpus/live/r73-critic
MTSV=$O/matrix.tsv
: > "$MTSV"

declare -A MEM=(
  [posttable_nomatch]=$L/round-68/posttable_nomatch.wav
  [txw_piperefuse]=$L/round-68/txw_piperefuse.wav
  [dec_act]=$L/round-66/pair_dec_act.wav
  [dec_hcom]=$L/round-66/pair_dec_hcom.wav
  [extsuffix_wav]=$L/round-69/extsuffix_nomatch.wav
  [extsuffix_bin]=$L/round-69/extsuffix_nomatch.bin
  [extsuffix_txw]=$L/round-69/extsuffix_nomatch.txw
  [extsuffix_f32]=$L/round-69/extsuffix_nomatch.f32
  [extsuffix_snd]=$L/round-69/extsuffix_nomatch.snd
  [lengate_gsrt_24]=$L/round-66/pair_lengate_gsrt_24.wav
  [lengate_gsrt_25]=$L/round-66/pair_lengate_gsrt_25.wav
  [lengate_hcom_131]=$L/round-66/pair_lengate_hcom_131.wav
  [lengate_hcom_132]=$L/round-66/pair_lengate_hcom_132.wav
)

mech() { # member label prefix
  local f=$1
  if grep -q 'Seek failed (Operation not permitted)' "$f" 2>/dev/null; then echo "refresh-seek-EPERM";
  elif grep -q 'unrecognized file format' "$f" 2>/dev/null; then echo "unrecognized-format";
  elif grep -q 'Found .hcom. at score=100' "$f" 2>/dev/null; then
    if grep -q 'Stream is not seekable' "$f" 2>/dev/null; then echo "hcom-nonseekable-decode"; else echo "hcom-detect"; fi
  elif grep -q 'Detected file format: wav' "$f" 2>/dev/null; then echo "wav-detect";
  elif grep -q 'Stream is not seekable' "$f" 2>/dev/null; then echo "non-seekable";
  else echo "-"; fi
}

for m in posttable_nomatch txw_piperefuse dec_act dec_hcom extsuffix_wav extsuffix_bin extsuffix_txw extsuffix_f32 extsuffix_snd lengate_gsrt_24 lengate_gsrt_25 lengate_hcom_131 lengate_hcom_132; do
  p=${MEM[$m]}
  # pw-cat file
  s=$(date +%s%N)
  timeout -s KILL 20 pw-cat -p "$p" > "$O/mx-pwcat-file-$m.stdout" 2> "$O/mx-pwcat-file-$m.stderr"; rc=$?
  e=$(date +%s%N)
  printf '%s\tpw-cat\tfile\t%s\t%s\t%s\t-\n' "$m" "$rc" "$(( (e-s)/1000000 ))" "$(head -1 "$O/mx-pwcat-file-$m.stderr")" >> "$MTSV"
  # pw-cat fifo
  d=$(mktemp -d /tmp/r73c-mx-XXXXXX); mkfifo "$d/m.fifo"
  ( cat "$p" > "$d/m.fifo" ) & w=$!
  sleep 0.2
  s=$(date +%s%N)
  timeout -s KILL 20 pw-cat -p "$d/m.fifo" > "$O/mx-pwcat-fifo-$m.stdout" 2> "$O/mx-pwcat-fifo-$m.stderr"; rc=$?
  e=$(date +%s%N)
  printf '%s\tpw-cat\tfifo\t%s\t%s\t%s\t-\n' "$m" "$rc" "$(( (e-s)/1000000 ))" "$(head -1 "$O/mx-pwcat-fifo-$m.stderr")" >> "$MTSV"
  wait $w 2>/dev/null; rm -rf "$d"
  # mpv file
  timeout -s KILL 20 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/mx-mpv-file-$m.log" "$p" > /dev/null 2>&1; rc=$?
  printf '%s\tmpv\tfile\t%s\t-\t-\t%s\n' "$m" "$rc" "$(mech "$O/mx-mpv-file-$m.log")" >> "$MTSV"
  # mpv fifo
  d=$(mktemp -d /tmp/r73c-mx-XXXXXX); mkfifo "$d/m.fifo"
  ( cat "$p" > "$d/m.fifo" ) & w=$!
  sleep 0.2
  timeout -s KILL 20 mpv --no-config --vo=null --ao=null --audio-display=no --really-quiet --log-file="$O/mx-mpv-fifo-$m.log" "$d/m.fifo" > /dev/null 2>&1; rc=$?
  printf '%s\tmpv\tfifo\t%s\t-\t-\t%s\n' "$m" "$rc" "$(mech "$O/mx-mpv-fifo-$m.log")" >> "$MTSV"
  wait $w 2>/dev/null; rm -rf "$d"
done
echo "matrix written: $MTSV ($(wc -l < "$MTSV") rows)"
