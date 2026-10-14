#!/usr/bin/env bash
# r67-scout — transport fork matrix.
# Members: the 18 tracked autodetect-ledger members (r63-r66) + 1 normal wav
# + 1 no-detect scratch probe (extension-fallback discrimination).
# Transports: file | pipe(-) | redir(-) | devstdin_pipe | devstdin_redir |
#             fifo (writer exits) | fifo_hold (writer lingers 8s) | popen(|cmd)
# Leg per member x transport: `sox -V4 <input> -n stat` -> detected, exit,
# samples-read, stderr tail. Fifo legs run cwd'ed into the fifo dir and are
# invoked by basename so stderr names are deterministic.
set -u
cd "$(dirname "$0")"
ROOT=/home/vgpnk/Projects/shokunin/audio-shokunin
R=$ROOT/corpus/live
L=runs/logs; mkdir -p "$L" fifo
TSV=runs/transport.tsv
: > "$TSV"

emit() { # member transport exit log
  local m=$1 t=$2 ex=$3 log=$4 det samp tail
  det=$(grep -o "detected file format type \`[^']*'" "$log" | head -1 | sed "s/.*\`//;s/'//")
  samp=$(grep -o 'Samples read: *[0-9]*' "$log" | head -1 | grep -o '[0-9]*$')
  tail=$(grep -E 'FAIL|WARN' "$log" | tail -1 | sed 's/^.*sox //' | cut -c1-110)
  printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$m" "$t" "${det:--}" "$ex" "${samp:--}" "${tail:-ok}" >> "$TSV"
}

probe() { # member relpath
  local m=$1 f=$2 ff
  ff="$ROOT/$f"
  sox -V4 "$ff" -n stat >"$L/$m.file.log" 2>&1;        emit "$m" file  $? "$L/$m.file.log"
  cat "$ff" | sox -V4 - -n stat >"$L/$m.pipe.log" 2>&1; emit "$m" pipe  $? "$L/$m.pipe.log"
  sox -V4 - -n stat <"$ff" >"$L/$m.redir.log" 2>&1;    emit "$m" redir $? "$L/$m.redir.log"
  cat "$ff" | sox -V4 /dev/stdin -n stat >"$L/$m.dspipe.log" 2>&1; emit "$m" dspipe $? "$L/$m.dspipe.log"
  sox -V4 /dev/stdin -n stat <"$ff" >"$L/$m.dsredir.log" 2>&1;    emit "$m" dsredir $? "$L/$m.dsredir.log"
  # fifo: basename invocation, writer closes promptly
  rm -f "fifo/$m.wav"; mkfifo "fifo/$m.wav"
  cat "$ff" > "fifo/$m.wav" &
  (cd fifo && timeout 15 sox -V4 "$m.wav" -n stat) >"$L/$m.fifo.log" 2>&1
  emit "$m" fifo $? "$L/$m.fifo.log"; wait 2>/dev/null; rm -f "fifo/$m.wav"
  # fifo_hold: writer holds the write end 8s after EOF (ffmpeg's own open then connects)
  mkfifo "fifo/$m.wav"
  { cat "$ff"; sleep 8; } > "fifo/$m.wav" &
  (cd fifo && timeout 20 sox -V4 "$m.wav" -n stat) >"$L/$m.fifoh.log" 2>&1
  emit "$m" fifoh $? "$L/$m.fifoh.log"; wait 2>/dev/null; rm -f "fifo/$m.wav"
  # popen command-pipe transport
  sox -V4 "|cat $ff" -n stat >"$L/$m.popen.log" 2>&1;  emit "$m" popen $? "$L/$m.popen.log"
}

# tracked autodetect-ledger members
probe pair_route_84        corpus/live/round-63/pair_route_84.wav
probe pair_route_00        corpus/live/round-63/pair_route_00.wav
probe pair_valid_8         corpus/live/round-64/pair_valid_8.wav
probe pair_valid_9         corpus/live/round-64/pair_valid_9.wav
probe pair_valid_24        corpus/live/round-64/pair_valid_24.wav
probe pair_valid_25        corpus/live/round-64/pair_valid_25.wav
probe pair_valid_56        corpus/live/round-64/pair_valid_56.wav
probe pair_valid_57        corpus/live/round-64/pair_valid_57.wav
probe pair_preempt_act     corpus/live/round-65/pair_preempt_act.wav
probe pair_preempt_gsrt    corpus/live/round-65/pair_preempt_gsrt.wav
probe pair_preempt_hcom    corpus/live/round-65/pair_preempt_hcom.wav
probe pair_preempt_both    corpus/live/round-65/pair_preempt_both.wav
probe pair_dec_hcom        corpus/live/round-66/pair_dec_hcom.wav
probe pair_dec_act         corpus/live/round-66/pair_dec_act.wav
probe pair_lengate_gsrt_24 corpus/live/round-66/pair_lengate_gsrt_24.wav
probe pair_lengate_gsrt_25 corpus/live/round-66/pair_lengate_gsrt_25.wav
probe pair_lengate_hcom_131 corpus/live/round-66/pair_lengate_hcom_131.wav
probe pair_lengate_hcom_132 corpus/live/round-66/pair_lengate_hcom_132.wav
# normal wav control
probe ui                   corpus/artifacts/ui.wav

# no-detect scratch probe: 300 zeros -> no CHECK row; fifo named .wav vs .bin vs '-'
python3 - <<'EOF'
open('/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r67-scout/probes/nodetect.bin','wb').write(b'\0'*300)
EOF
ND=probes/nodetect.bin
sox -V4 "$ND" -n stat >"$L/nodetect.filebin.log" 2>&1; emit nodetect_bin file $? "$L/nodetect.filebin.log"
cp "$ND" probes/nodetect.wav
sox -V4 probes/nodetect.wav -n stat >"$L/nodetect.filewav.log" 2>&1; emit nodetect_wav file $? "$L/nodetect.filewav.log"
cat "$ND" | sox -V4 - -n stat >"$L/nodetect.pipe.log" 2>&1;   emit nodetect pipe $? "$L/nodetect.pipe.log"
rm -f fifo/nodetect.wav fifo/nodetect.bin; mkfifo fifo/nodetect.wav fifo/nodetect.bin
cat "$ND" > fifo/nodetect.wav & (cd fifo && timeout 15 sox -V4 nodetect.wav -n stat) >"$L/nodetect.fifowav.log" 2>&1; emit nodetect fifowav $? "$L/nodetect.fifowav.log"; wait 2>/dev/null
cat "$ND" > fifo/nodetect.bin & (cd fifo && timeout 15 sox -V4 nodetect.bin -n stat) >"$L/nodetect.fifobin.log" 2>&1; emit nodetect fifobin $? "$L/nodetect.fifobin.log"; wait 2>/dev/null
sox -V4 "|cat $PWD/$ND" -n stat >"$L/nodetect.popen.log" 2>&1; emit nodetect popen $? "$L/nodetect.popen.log"
rm -f fifo/nodetect.wav fifo/nodetect.bin
echo "== done =="; column -t -s$'\t' "$TSV" | sed -n '1,200p'
