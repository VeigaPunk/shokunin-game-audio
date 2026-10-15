# r82-critic evidence manifest

(large probe wavs — `cls_*.wav`, `forged.wav`, `tap.wav`, `sil.wav`,
`c13rep.wav`, `c3rep_*.wav` — trimmed post-analysis per lane practice;
stderr/cmd outputs retained)

Host `plazir27`, 2026-10-15 ~17:30–17:45Z (-03), loadavg ~90/32 (r83a
sibling lane live with own taps; audio graph quiet during the family
replay window). Seat objects `r82c_*`, all unloaded at exit.

## probes (all under the live loaded host)

1. `replay-load.stdout.json` + `replay-load.stderr.log` —
   `python3 corpus/fixtures/measure_audio.py --probe-ffmpeg-r82` on the
   committed fixture (aa03c347) at loadavg ~90 → exit 0,
   `{"failures": {}}`, 76 legs. Canonical receipt:
   `corpus/live/runs/20261015T203551336204Z-ffmpeg-r82/measurements.json`.
   Max timeline sample gap 0.209 s vs 0.2 s grid; pw-dump 25–46 ms under
   load; c3 realizations eio_251×3; a5 params_251; a6 rate 44100;
   p7 winner device_flag; star_vs_pactl agree.

2. `c3rep_{0..3}.err` — `ffmpeg -f pulse -i default -t 2.0` ×4 under
   load → rc=251 EIO, wall 0.087–0.114 s (envelope arm eio_251;
   nowhere near the 5 s hang bound).

3. `c13rep.err/wav` — `-i r82c_absent_name.monitor` → rc=0 (the
   `.monitor` permissive hole reproduces under load).

4. module-index substring proof (transcript in report §F4): with only
   `r82c_a2` loaded (idx 536870921), `_gst_r81_sink_module_index("r82c_a")`
   returned 536870921 and `_gst_r81_unload_own(None, "r82c_a")` fired —
   exit_code 0, `r82c_a2` destroyed. The "name-verified" guard matches
   `sink_name=<q>` as a substring.

5. ambient-env steering: `PULSE_SINK=r82c_tgt ffmpeg -f pulse` (no
   `-device`) → node `target.object=r82c_tgt`, `consumers=[r82c_tgt]`;
   control without the env → `target.object=None`, consumers=[SPDIF].

6. tone forgery: `forged.wav` (1210/1780) played into `r82c_tgt` from a
   foreign-named node (`foreign_ffplayish`), tapped → `carries_tone=True`,
   20/20 mine windows (`tap.wav`).

7. r78-collision classifier table: `cls_*.wav` — synthesized single-tone
   pairs classified by `_ffpw_r82_tone_windows`:
   (1208,1711) [r78 pid%4==1] → mine 10/10 **COLLISION**;
   (997,1500)/(1419,1922)/(1630,2133) → mine 0; (1210,1780) → mine 10/10.

8. `a5probe.err`/`arec.err` — `ffmpeg -f alsa -i default` rc=251
   `cannot set parameters`; `arecord -D default` rc=1 hw-params — the
   boundary's host-wide-broken pipewire-alsa capture state still live
   (a5 params_251 arm is the current realization).

9. Receipt mining (committed): all 4 runs —
   `a2_hw_free_pwheld.holder_consumers=[Headphones__sink]` (api.alsa.path
   hw:Audio,1 — a different subdevice than the hw:0,0 capture target;
   Speaker=hw:Audio,0 is the same-subdevice counterpart the report text
   names); `t2_cap_r2` in final3 shows `mine_spans [[0.2,1.1]]` — zero
   tag-tone windows after the 1.202 s unload, yet green (content ungated).

Exit state: 0 `r82c_*` modules, 0 r82c/r82ff nodes, no probe processes,
tracked tree clean (`git status` = only untracked additions).
