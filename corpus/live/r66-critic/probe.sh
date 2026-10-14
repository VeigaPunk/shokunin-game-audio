#!/bin/bash
# r66-critic probe matrix: detection + outcome per variant, file vs pipe,
# plus forced -t legs where the attack calls for them.
cd "$(dirname "$0")"
VAR=var
OUT=results.tsv
printf 'name\tmode\tdetected\trc\tsamples\tf32bytes\ttail\n' > "$OUT"

det() {  # $1=file $2=mode
  local f="$1" m="$2" d rc smp f32 tl
  case "$m" in
    file) out=$(sox -V6 "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    pipe) out=$(cat "$f" | sox -V6 - -n stat 2>&1 >/dev/null); rc=$? ;;
    tgsrt) out=$(sox -t gsrt "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    tgsrtpipe) out=$(cat "$f" | sox -t gsrt - -n stat 2>&1 >/dev/null); rc=$? ;;
    thcom) out=$(sox -t hcom "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    twve) out=$(sox -t wve "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    tact) out=$(sox -t act "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    tactpipe) out=$(cat "$f" | sox -t act - -n stat 2>&1 >/dev/null); rc=$? ;;
    twav) out=$(sox -t wav "$f" -n stat 2>&1 >/dev/null); rc=$? ;;
    fifo) mkfifo /tmp/r66fifo 2>/dev/null; (cat "$f" > /tmp/r66fifo &) ; out=$(sox -V6 /tmp/r66fifo -n stat 2>&1 >/dev/null); rc=$?; rm -f /tmp/r66fifo ;;
  esac
  d=$(printf '%s' "$out" | grep -oP "detected file format type \`\K\S+?(?=')" | head -1)
  smp=$(printf '%s' "$out" | grep -oP 'Samples read:\s*\K\d+' | head -1)
  tl=$(printf '%s' "$out" | grep -v "detected file format" | tail -1 | cut -c1-90)
  f32=$(sox "$f" -t f32 -e floating-point - 2>/dev/null | wc -c)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$(basename "$f")" "$m" "${d:--}" "$rc" "${smp:--}" "$f32" "$tl" >> "$OUT"
}

for f in "$VAR"/Q* "$VAR"/N*; do det "$f" file; det "$f" pipe; done
for f in "$VAR"/H*; do det "$f" file; done
for f in "$VAR"/S_*; do det "$f" file; det "$f" pipe; det "$f" fifo; done
for f in "$VAR"/N1* "$VAR"/N2* "$VAR"/N3*; do det "$f" tgsrt; det "$f" tgsrtpipe; done
for f in "$VAR"/S_pair_lengate_gsrt_25.wav "$VAR"/S_pair_lengate_gsrt_24.wav "$VAR"/S_pair_dec_hcom.wav; do det "$f" tgsrt; done
for f in "$VAR"/G_sz0_len*.bin; do det "$f" file; det "$f" tgsrt; done
for f in "$VAR"/Q1*.bin "$VAR"/Q2*.wav "$VAR"/Q3*.bin; do det "$f" twve; det "$f" tgsrt; det "$f" thcom; det "$f" tact; done
column -t -s$'\t' "$OUT" | head -150
