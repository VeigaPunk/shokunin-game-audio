#!/usr/bin/env bash
# r66-scout measurement matrix. Per probe: -V6 stat (detection + samples),
# f32 decode byte count, sox --i receipt, forced -t {wve,act,wav} legs,
# strace execve count (ffmpeg bridge attribution), ffprobe codec.
# Logs land under runs/logs/<probe>.*; table -> runs/matrix.tsv.
set -u
cd "$(dirname "$0")"
mkdir -p runs/logs
TSV=runs/matrix.tsv
: > "$TSV"
printf 'probe\tsize\tdetected\trc\tsamples\tf32bytes\texecve_ffmpeg\ttail\n' >> "$TSV"

for f in probes/*; do
  n=$(basename "$f")
  sz=$(stat -c%s "$f")
  sox -V6 "$f" -n stat >"runs/logs/$n.v6.log" 2>&1
  rc=$?
  det=$(grep -o "detected file format type \`[^']*'" "runs/logs/$n.v6.log" | sed "s/.*\`//;s/'//")
  smp=$(grep -o 'Samples read:[[:space:]]*[0-9]*' "runs/logs/$n.v6.log" | grep -o '[0-9]*$')
  tailn=$(grep -E 'FAIL|WARN' "runs/logs/$n.v6.log" | tail -1 | sed 's/.*: //' | cut -c1-80)
  sox "$f" -t f32 -e floating-point - 2>/dev/null | wc -c > "runs/logs/$n.f32"
  f32=$(cat "runs/logs/$n.f32")
  sox --i "$f" >"runs/logs/$n.i.log" 2>&1; irc=$?
  for t in wve gsrt hcom act wav; do
    sox -t "$t" "$f" -n stat >"runs/logs/$n.t_$t.log" 2>&1
    echo "rc=$?" >> "runs/logs/$n.t_$t.log"
  done
  strace -f -e trace=execve sox "$f" -n stat > /dev/null 2> "runs/logs/$n.strace"
  xvc=$(grep -c 'execve("/usr/bin/ffmpeg"' "runs/logs/$n.strace" || true)
  ffprobe -v error -show_entries stream=codec_name -of csv=p=0 "$f" >"runs/logs/$n.ff.log" 2>&1
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$n" "$sz" "${det:-NONE}" "$rc" "${smp:--}" "$f32" "$xvc" "${tailn:--}" >> "$TSV"
done

# transport legs on the decodable probes + selected collisions
for n in V01_wve_valid.bin V02_wve_valid+hcom+84.bin D01_dec_hcom_rebuild.wav S06_riff+gsrt+84.wav; do
  cat "probes/$n" | sox -V6 - -n stat >"runs/logs/$n.pipe.v6.log" 2>&1
  echo "pipe_rc=$?" >> "runs/logs/$n.pipe.v6.log"
done

# sha + diffs for the pair candidates
sha256sum probes/* > runs/probe-shas.txt
sha256sum ../round-66/*.wav ../round-65/*.wav ../round-64/*.wav ../round-63/*.wav > runs/tracked-shas.txt
cmp -l probes/D01_dec_hcom_rebuild.wav probes/D02_dec_act_rebuild.wav > runs/diff-dec-pair.txt
cmp -l probes/D01_dec_hcom_rebuild.wav ../round-66/pair_dec_hcom.wav > runs/diff-rebuild-vs-tracked-hcom.txt
cmp -l probes/D02_dec_act_rebuild.wav  ../round-66/pair_dec_act.wav  > runs/diff-rebuild-vs-tracked-act.txt
cmp -l probes/S01_head_wve.bin probes/S02_head_riff84.bin > runs/diff-swap-pair.txt
echo "done"
