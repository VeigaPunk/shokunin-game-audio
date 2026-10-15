# r83 author — the pw-cat / pw-record / pw-loopback PROPS-PARSER surface (`--probe-pwcat-r83`)

New parallel ledger family in `corpus/fixtures/measure_audio.py` (+ ~2,240 lines, all namespaced
`r83a_*_<pid>` / `pwcat_*_r83_entry` / `_pwcat_r83_*` / `PWCAT_R83_*`; prior r76–r82 families untouched;
CLI wiring only: flag, mutex sum, dispatch, mode, output suffix). Host: plazir27, PipeWire 1.6.8,
WirePlumber 0.5.17, pactl 17.0, Python 3.14.7, NumPy 2.5.3, kernel 7.2.3-arch1-3.

**Two green runs, zero failures, 128 legs total.** Receipts:
`corpus/live/r83-author/measurements-run1.json` (21:50:17Z),
`corpus/live/r83-author/measurements-run2.json` (22:06:45Z).

## Entries / leg counts

| entry | measurement key | legs |
|---|---|---|
| (1) props parse lattice | `pwcat_props_parse_r83_probe` | 29 |
| (2) empty/whitespace SIGSEGV | `pwcat_empty_props_segv_r83_probe` | 19 |
| (3) latency units + real `-d` delay | `pwcat_latency_props_r83_probe` | 26 |
| (4) channel matrix + MONO caveat | `pwcat_channel_matrix_r83_probe` | 13 |
| (5) remix props | `pwcat_remix_props_r83_probe` | 18 |
| (6) resample props | `pwcat_resample_props_r83_probe` | 15 |
| (7) arg-edge fail-open lattice | `pwcat_failopen_args_r83_probe` | 8 |
| **total** | | **128** |

## Measured laws (all pinned with >=3 reps where a boundary was claimed)

1. **Syntax forms land verbatim.** space/comma `k=v`, `{ k = v }`, `{ "k" = "v" }`, `{ "k": "v" }` all
   land on the respective node (verified on pw-dump props); `-i` writes only `input.<n>`, `-o` only
   `output.<n>`; `node.name=` inside `-i` OVERRIDES `-n` (published as `<prefix>_capx`, the default
   `input.<n>` name absent — probe_absent-verified).

2. **Malformed properties are TWO classes (boundary correction — not universally silent).**
   - SILENT: `}{ garbage`, `[1,2`, `{ }`, `null`, `"str"` → both nodes spawn with full defaults
     (`media.name` stays `<tag> input`), stderr empty, alive at bound.
   - PARTIAL LAND (author-measured): `a=b,` → `a='b'` lands, the trailing empty segment drops silently.
   - HARD ERROR: `a=b }{ c=d`, `{ bad`, `media.name=` → **pw-loopback rc=255, `syntax error in
     --capture-props`/`--playback-props`, ZERO nodes published** (8 legs x2 classes). **pw-cat and
     pw-record exit rc=1 `syntax error in --properties`** — the per-binary rc split is pinned, not
     conflated (5 legs).

3. **Empty/whitespace props SIGSEGV family — all rc=-11, zero nodes published:** `-i ''`, `-o ''`,
   `-i ' '`, `-o ' '` on pw-loopback; `pw-cat -P ''`, `-P ' '`; `pw-record -P ''`, `-P ' '` — 18 crash
   legs against a live loopback control that ran to bound (rc=-9).

4. **Latency units lattice.** `-l` is atoi-ms ×48 (`-l 5`→240/48000, `-l 2.5`→96/48000,
   `-l 10000`→480000/48000); `-d` is float-s ×16000 (`-d 0.25`→4000/48000, `-d 1.0`→16000/48000);
   `-l` beats `-d` in either order; `-l 0`/abc/`-d 0`/-1/abc drop silently; **`-l -5` →
   4294967056/48000 uint32 wrap**; `-g` lands `node.group` on both nodes.

5. **The falsified "no delay" claim, re-armed as a transport envelope (boundary correction).**
   `-d` adds ~d SECONDS of REAL delay: ctl median transport 0.105 s; **`-d 1.0` deltas vs ctl =
   [1.043, 1.000, 0.999] s** (envelope [0.75,1.45]); `-d 0.25` [0.398, 0.355] s (env [0.08,0.60]);
   `-l 1000` [0.106, 0.105] s — `-l` is prop-only even at 1 s nominal. Method: link-gated loopback,
   monitor tap started before the feed, `first_nonsilent − (t_feed − t_tap)`; feed/record startup is
   common-mode and cancels in the delta.

6. **Channel matrix.** `-c 1 -m '[ MONO ]'` is the pinned stable arm — `0.5*(L+R)` both channels in
   every settled window (ratio envelope [0.42,0.58] vs control median 8191). **`m_alone` caveat
   (boundary correction):** `-m '[ MONO ]'` alone at `-c 2` was realized `stable_mono`/`stable_mono`/
   `unmeasured` in run1 and `stable_mono`×3 in run2 — recorded as named outcomes with per-window
   amplitude dev ratios; the boundary's `time_varying` arm was measured under load, and only the
   `-c 1` arm is pinned. Channel-shape props (`audio.position`, `audio.channels`, `channelmap.map`)
   land verbatim but are content-inert (stereo passthrough carried the tag).

7. **Remix props (pw-cat -P).** `stream.dont-remix=true` is the only effective switch both ways:
   mono→stereo publishes `output_MONO` with FL-only full-amp content; stereo→mono keeps FL only
   (FR dropped, not mixed). `node.dont-remix`, `channelmix.upmix/disabled/stereo-widen/upmix-method`,
   `node.passive` land verbatim and are content-inert. `node.dont-move=true` makes
   `pactl move-sink-input` a silent rc=0 no-op (post-move consumers still `[ns_b]`). Upmix duplicates
   at full amp; mono-sink downmix = `0.5*(L+R)` both freqs.

8. **Resample props (pw-cat -P, 44.1k→48k).** Default is pitch-preserving (`node.rate=1/44100`).
   `resample.disable=true` + mismatch → **all-zero monitor with links live** and no error (3 legs);
   matched-rate + disable and `disable=false` + mismatch carry the tone. **`resample.peaks=true` +
   mismatch → the FULL-WAVE `|x|` artifact**: never negative (min=0), DC mean ≈ +4450, forced zeros
   (~14.6% this run — boundary recorded ~8.3%, both are recorded honestly), the fundamental destroyed
   (amp_at_f ≈ 0.1) and the **octave dominant** (amp_at_2f ≈ 3170 vs control ~8192) on BOTH channels
   at each channel's own frequency — `peaks_abs_octave_artifact`, UPSAMPLE-only (48k→44.1k clean,
   matched-rate clean). `--rate` does NOT override the file rate; `resample.quality` lands verbatim.

9. **Arg edges.** `-C ''` fail-opens capture to the default-side monitor; `-P ''` fail-opens playback
   to a session sink; `-n ''` publishes `input./output.capture.props` and playback still routes away
   from `-P`. All three are topology-only legs (no tone ever fed on a path that could reach a shared
   sink). **Pinned as ROUTE SHAPE, not name**: single non-probe-owned Audio-class node wins — measured
   honestly because a foreign `r93b_in` seat sink had rotated the stored default mid-run (pactl said
   `r93b_in`, WirePlumber routed `-n ''`/`-C ''` to the SPDIF device's monitor; run recorded both
   readings). `-C`/`-P` accept object.serial numbers verbatim (landed on the probe sinks).

## Realized / unrealized arms (recorded, not claimed)

- `m_alone` realized arms: run1 `['stable_mono','unmeasured','stable_mono']`, run2
  `['stable_mono']×3` — the boundary's `time_varying` was load-dependent; the fixture records the arm
  per leg (`mono_mix_dev_ratio` / `stereo_pass_dev_ratio`) and never asserts `-m` alone is stable.
- One `c1_mono` leg in run1 was silent (`silent_or_thin`, unmeasured — cold WirePlumber attach on the
  entry's first feed legs; a recorded warmup leg absorbs it and controls need ≥2/3 tone arms).
- `n_empty` outcome: `failopen_foreign_sink` both runs (fail-open confirmed; the winning sink name
  is recorded, not pinned to a stale default string).
- Zero `coverage_blocked` items; all 4 sinks unloaded name-verified, `sinks_gone` all true,
  `own_nodes_after` empty on every entry.

## Invariants kept

- Insertion-only family; r82-shaped (entry → bounded legs → verdict checks → teardown).
- `r83a_*_<pid>` seat-owned names; `PWCAT_R83_*` constants; family-local error-class tuple consulted
  before the shared pw table (never prepended into `_CAPTURE_ERR_CLASSES`).
- Bounded process groups (`start_new_session`, `os.killpg`), taps bounded by `-n`, tones fed only to
  probe-owned sinks (`own_sinks` fail-closed guard raises on a foreign `feed_sink`).
- Name-verified module unloads only (re-read module table, fire only the index whose args carry our
  `sink_name=`); never `set-default-*`; teardown witnesses `sinks_gone` + `own_nodes_after` on every
  entry; `generic_capture_props_nodes_after` records the `-n ''` literal names separately.
- No commits; everything working-tree-only.

## Blockers

None.
