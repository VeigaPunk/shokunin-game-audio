#!/usr/bin/env bash
# fifo-path leg: mkfifo, start a writer, run `sox fifo -n stat` under timeout.
# For act members the ffmpeg bridge re-opens the fifo path -> needs a 2nd writer.
set -u
R=/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live
L=logs
TSV=fifo.tsv
printf 'member\tleg\tdetected\texit\tsamples\tlastline\n' > "$TSV"
emit() { local m=$1 t=$2 ex=$3 log=$4 det samp tail
  det=$(grep -o "detected file format type \`[^']*'" "$log" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$log" | head -1 | grep -o '[0-9]*$')
  tail=$(grep -E 'FAIL|WARN' "$log" | tail -1 | sed 's/.*sox //' | cut -c1-110)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$m" "$t" "${det:--}" "$ex" "${samp:--}" "${tail:-ok}" >> "$TSV"
}
FIFO=/tmp/r67critic_fifo
for d in round-65 round-66; do
  for f in "$R/$d"/*.wav; do
    [ -e "$f" ] || continue; n=$(basename "$f")
    rm -f "$FIFO"; mkfifo "$FIFO"
    # leg 1: single writer, sox opens fifo by path
    ( cat "$f" > "$FIFO" & echo $! > /tmp/r67critic_w1.pid )
    timeout 10 sox -V4 "$FIFO" -n stat >"$L/$n.fifo1w.log" 2>&1; ex=$?
    wait "$(cat /tmp/r67critic_w1.pid)" 2>/dev/null; emit "$n" fifo-path-1w "$ex" "$L/$n.fifo1w.log"
    # leg 2: fifo passed as stdin fd (sox - < fifo), single writer
    rm -f "$FIFO"; mkfifo "$FIFO"
    ( cat "$f" > "$FIFO" & echo $! > /tmp/r67critic_w2.pid )
    timeout 10 sox -V4 - -n stat < "$FIFO" >"$L/$n.fifofd.log" 2>&1; ex=$?
    wait "$(cat /tmp/r67critic_w2.pid)" 2>/dev/null; emit "$n" fifo-as-fd "$ex" "$L/$n.fifofd.log"
    # leg 3: fifo-path with a *persistent* second writer that re-feeds (dd loop once)
    rm -f "$FIFO"; mkfifo "$FIFO"
    ( cat "$f" > "$FIFO"; cat "$f" > "$FIFO" ) &
    WP=$!
    timeout 10 sox -V4 "$FIFO" -n stat >"$L/$n.fifo2w.log" 2>&1; ex=$?
    wait "$WP" 2>/dev/null; emit "$n" fifo-path-2w "$ex" "$L/$n.fifo2w.log"
  done
done
rm -f "$FIFO" /tmp/r67critic_w1.pid /tmp/r67critic_w2.pid
echo done
