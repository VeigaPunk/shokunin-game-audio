#!/usr/bin/env bash
# r66-scribe sweep: per-variant detection + reader fate receipts.
# For each variants/* file:
#   logs/<f>.stat.{out,err}   sox -V6 <f> -n stat       (detection line + samples + exit)
#   logs/<f>.i.{out,err}      sox --i <f>               (handler parenthetical + exit)
#   logs/<f>.dec.{out,err}    sox <f> -t f32 -e floating-point -   (bytes + exit)
#   logs/<f>.t<T>.{out,err}   sox -t T <f> -n stat      (forced legs: wve gsrt hcom act wav)
#   logs/<f>.ffp.{out,err}    ffprobe -v error -show_entries ...
#   logs/<f>.pipe.{out,err}   cat <f> | sox -V6 - -n stat  (non-seekable fd leg)
#   logs/<f>.redir.{out,err}  sox -V6 - -n stat < <f>      (seekable-stdin leg)
# results.tsv columns: name detected rc samples i_hdl i_rc dec_B dec_rc
#   t_wve t_gsrt t_hcom t_act t_wav ffp pipe redir stat_tail
set -u
cd "$(dirname "$0")"
SOX=/usr/bin/sox
FFP=/usr/bin/ffprobe
OUT=results.tsv

detect_line() { grep -o "detected file format type \`[^']*'" "$1" 2>/dev/null | sed "s/.*\`//;s/'//" || true; }
samples_line() { grep -o "Samples read:[[:space:]]*[0-9]*" "$1" 2>/dev/null | grep -o "[0-9]*" || true; }
handler_p() { grep -o "([^)]*)" "$1" 2>/dev/null | head -1 | tr -d '()' || true; }
lastline() { tail -1 "$1" 2>/dev/null | tr '\011' ' ' | tr -d "\140\047"; }

printf 'name\tdetected\trc\tsamples\ti_hdl\ti_rc\tdec_B\tdec_rc\tt_wve\tt_gsrt\tt_hcom\tt_act\tt_wav\tffp\tpipe\tredir\tstat_tail\n' > "$OUT"

declare -A T
for f in variants/*; do
  [ -f "$f" ] || continue
  base=$(basename "$f")
  case "$base" in manifest.tsv) continue;; esac
  l="logs/$base"

  $SOX -V6 "$f" -n stat >"$l.stat.out" 2>"$l.stat.err"; rc_stat=$?
  det=$(detect_line "$l.stat.err"); det=${det:-NONE}
  smp=$(samples_line "$l.stat.err"); smp=${smp:--}
  st=$(lastline "$l.stat.err")

  $SOX --i "$f" >"$l.i.out" 2>"$l.i.err"; rc_i=$?
  ih=$(handler_p "$l.i.out"); ih=${ih:-none}

  $SOX "$f" -t f32 -e floating-point - >"$l.dec.out" 2>"$l.dec.err"; rc_dec=$?
  decb=$(wc -c <"$l.dec.out")

  for t in wve gsrt hcom act wav; do
    $SOX -t "$t" "$f" -n stat >"$l.t$t.out" 2>"$l.t$t.err"; rc=$?
    s=$(samples_line "$l.t$t.err"); s=${s:--}
    tl=$(lastline "$l.t$t.err" | cut -c1-60)
    T[$t]="rc=$rc s=$s $tl"
  done

  $FFP -v error -show_entries stream=codec_name:format=format_name,duration \
       -of default=nw=1 "$f" >"$l.ffp.out" 2>"$l.ffp.err"; rc_ffp=$?
  ffp=$(tr '\n' ';' <"$l.ffp.out" | tr '\011' ' ' | tr -d "\140\047" | cut -c1-90)
  [ $rc_ffp -ne 0 ] && ffp="rc=$rc_ffp $(lastline "$l.ffp.err" | cut -c1-60)"

  cat "$f" | $SOX -V6 - -n stat >"$l.pipe.out" 2>"$l.pipe.err"; rc_pipe=$?
  pdet=$(detect_line "$l.pipe.err"); pdet=${pdet:-NONE}
  psmp=$(samples_line "$l.pipe.err"); psmp=${psmp:--}
  pipe="$pdet s=$psmp rc=$rc_pipe $(lastline "$l.pipe.err" | cut -c1-50)"

  $SOX -V6 - -n stat <"$f" >"$l.redir.out" 2>"$l.redir.err"; rc_redir=$?
  rdet=$(detect_line "$l.redir.err"); rdet=${rdet:-NONE}
  rsmp=$(samples_line "$l.redir.err"); rsmp=${rsmp:--}
  redir="$rdet s=$rsmp rc=$rc_redir $(lastline "$l.redir.err" | cut -c1-50)"

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$base" "$det" "$rc_stat" "$smp" "$ih" "$rc_i" "$decb" "$rc_dec" \
    "${T[wve]}" "${T[gsrt]}" "${T[hcom]}" "${T[act]}" "${T[wav]}" \
    "${ffp:-none}" "$pipe" "$redir" "${st:0:100}" >> "$OUT"
done
echo "rows: $(($(wc -l <"$OUT") - 1))"
