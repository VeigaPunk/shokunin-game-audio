#!/usr/bin/env bash
# r76-scout roundtrip cell (scratch): play a canonical member to the default
# sink while three capture consumers record the same sink's monitor.
set -u
cd "$(dirname "$0")"
LEGS=legs
mkdir -p "$LEGS"
MON=alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.monitor
SINK=alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink
MEMBER=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/artifacts/stem_sections.wav
LOG=runs/roundtrip.log
: > "$LOG"

run_one() {
  local tag="$1"; shift
  echo "=== $tag : $* ===" >> "$LOG"
  ( "$@" ) >>"$LOG" 2>&1 &
  local cpid=$!
  sleep 0.4
  # start the player, then wait for the capture window to close
  timeout -s KILL 8 paplay "$MEMBER" >>"$LOG" 2>&1
  echo "player_rc=$?" >> "$LOG"
  wait "$cpid"
  echo "capture_rc=$?" >> "$LOG"
}

rm -f "$LEGS"/rt-*.wav "$LEGS"/rt-*.raw
run_one ffmpeg-pulse-mon timeout -s KILL 6 ffmpeg -hide_banner -loglevel error -nostdin -y -f pulse -i "$MON" -t 5 "$LEGS/rt-ffmpeg-mon.wav"
run_one ffmpeg-pulse-sink-rt2 timeout -s KILL 6 ffmpeg -hide_banner -loglevel error -nostdin -y -f pulse -i "$MON" -t 5 "$LEGS/rt-ffmpeg-mon2.wav"
run_one parec-monitor timeout -s KILL 6 parec -d @DEFAULT_MONITOR@ --rate=48000 --channels=2 --format=s16le --file-format=wav "$LEGS/rt-parec-mon.wav"
run_one pwrec-sink timeout -s KILL 6 pw-record --target "$SINK" -P stream.capture.sink=true --rate 48000 --channels 2 --format s16 "$LEGS/rt-pwrec-mon.wav"
ls -l "$LEGS"/rt-* >> "$LOG" 2>&1
cat "$LOG"
