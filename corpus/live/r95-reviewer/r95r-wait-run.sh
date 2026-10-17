#!/usr/bin/env bash
# r95 reviewer: wait (bounded) for a responsive PipeWire daemon, then run
# the r95 battery once on the committed HEAD bytes. Scratch only.
cd /home/vgpnk/Projects/shokunin/audio-shokunin || exit 2
LOG=corpus/live/r95-reviewer/r95r-window.log
: > "$LOG"
ok=0
for i in $(seq 1 60); do
  t0=$(date +%s%N)
  timeout 12 pactl info >/dev/null 2>&1; rc=$?
  t1=$(date +%s%N); d=$(( (t1-t0)/1000000 ))
  n=$(pgrep -fc 'measure_audio.py' 2>/dev/null || true)
  la=$(cut -d' ' -f1 /proc/loadavg)
  echo "$(date -u +%H:%M:%SZ) try=$i pactl_rc=$rc d=${d}ms probes=$n load=$la" >> "$LOG"
  if [ "$rc" -eq 0 ] && [ "$d" -le 6000 ]; then
    echo "$(date -u +%H:%M:%SZ) WINDOW_OK after $i tries" >> "$LOG"
    ok=1
    break
  fi
  sleep 15
done
echo "window_ok=$ok" > corpus/live/r95-reviewer/r95r-run2-window.txt
export TMPDIR=/home/vgpnk/Projects/shokunin/tmp
export PYTHONDONTWRITEBYTECODE=1
timeout 1500 python3 corpus/fixtures/measure_audio.py --probe-jack-r95 \
  > corpus/live/r95-reviewer/r95r-run2-cli.log \
  2> corpus/live/r95-reviewer/r95r-run2-cli.err.log
echo "rc=$?" >> corpus/live/r95-reviewer/r95r-run2-rc.txt
echo "$(date -u +%H:%M:%SZ) done rc_file=corpus/live/r95-reviewer/r95r-run2-rc.txt" >> "$LOG"
