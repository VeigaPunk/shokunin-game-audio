# R77 adjudicator (Sol) — capture-source lattice, fallback law, reader matrix, sever axis, split sentinel, format axis

Round: 77. Wave: `shokunin-train-20261101-w17` wave-A + wave-B; seats on
mixed swe-2 / deepseek-v4.1-flash lanes. Work commit `65790f1`, fold
commit `1a84ca7` (+336/−127 in `corpus/fixtures/measure_audio.py`).

## Declared move

`--probe-capture-r77`: six entries over the record-side frontier —
`capture_target_loss_r77` (sustained capture across target unload),
`capture_source_lattice_r77` (target/prop resolution incl. the
`stream.capture.sink` fallback law), `capture_readers_r77` (five-reader
matrix on severed WAVs), `capture_arecord_sever_r77` (bound-derived
headers, device/sever axes), `capture_split_sentinel_r77` (2 GiB
auto-split `<name>-01.wav`), `capture_format_axis_r77` (format
conversion vs `usage_refusal`).

## Claim adjudication

- **Fallback law CONFIRMED** — verifier AGREE on all 8 headline claims
  in its own harness: the sink is never captured without the prop;
  unresolvable/`default`/source-name targets all land the current
  default sink's monitor (identity, not silence — the pin is
  sink-nonconsumption). `sustained_after_target_loss` reproduced
  byte-exact. Fold added `prop_probe_sink` (per-process sink name) so
  the selection distinction is measurable on single-sink hosts.
- **Reader matrix CONFIRMED + armed** — all five readers honestly
  report 96,000 frames on the calibration file (fold asserted this
  fail-closed; it was recorded-but-never-checked at author time).
- **Split sentinel CONFIRMED** — 2 GiB rotation writes
  `<name>-01.wav`; fold replaced the full-file `read_bytes()` with
  bounded header reads / chunked zero scan / `np.memmap` PCM stats
  (was +2048 MB RSS — reviewer F5).
- **Prior-row stability CONFIRMED** — baseline 125/125 prior rows
  stable in BOTH phases; verifier 1172 leaves 0 diffs on r76 rows.
- **N2 wall-leg vacuity FIXED in fold** — verifier found the wall leg
  ran `pactl unload-module ""` (rc-0 no-op) after the bounded leg
  already killed the sink. Fold: fresh per-run sink +
  `r77_loss_sink_<pid>` + exact module id + fail-closed
  unload-fired/pre-loss-consume checks. Folded run shows the real
  transition (98→104→102 % rate buckets, probe sink → SPDIF fallback,
  `probe_sink_gone: true`).
- **Contention classes NAMED, not asserted away** — cross-seat
  `pw-record` clients pollute link inventories (baseline differencing +
  owner-pid filtering + `foreign`/`stale_link` confounds); roundtrip
  content witness has a measured 18.6 % false-alarm rate under
  multi-seat load; `host_is_quiet` now counts `/proc` comm+cmdline not
  `pgrep -f` wrappers.
- **Seed-mutation surface DISCLOSED** — probe runs regenerate tracked
  `corpus/artifacts/*.wav` in place; an undeclared `ambience.wav`
  rewrite was caught at commit time and restored to HEAD bytes.
  Read-only-seeds is an r78 candidate (reviewer).
- **Falsified claims not retained** — author's "±1 frame" wall-clock
  drift (simplifier measured ≤8192 frames) and two pre-measured scout
  rows corrected by measurement; all recorded in the author report.

## Fold inventory (1a84ca7)

Simplifier zero-diff batch (+56/−58); exclusivity guard covers
`--probe-capture-r77` (found independently by critic, reviewer,
verifier, baseline — 4 seats); per-process sink names; discriminating
`prop_probe_sink` row; streaming fixes; `sink_gone` vacuity armed;
confound honoring; fail-closed asserts (calibration, device-axis
existence/header-class, format refusal triple, `data_actual` byte
bounds, sink-gone teardown); raw-fraction `carries_tone`; sha-pair
fail-closed; `noprop` fallback class generalized to named classes when
the default source is live.

Folded probe: all 6 probes `failures: {}` under a contended host
(receipt `20261014T210316456683Z`). r76 regression on the folded tree:
3 failures all classified host-state — `parec_no_device` + arecord
legs reproduce **identically on pre-fold HEAD** (device topology
changed: DualSense source now default; PCM paths freed), and the
roundtrip-witness failure matches the named 18.6 % contention
false-alarm class (`nonzero_fraction_gt_half=true`, level-far only).

## Seat records

scout (pre-measured lattice); author `b92a17d4`; boundary `79539680`;
baseline `660f1e30` (zero-drift both phases); scribe `4f70d450`
(5-delta fold scope correct); critic `b47b…` + reviewer `8c9f…` +
verifier `47e18c85` + simplifier `11f727f2` — all landed; every
consensus defect folded.

## Verdict

**ADMIT-corr** — the source/fallback lattice is armed with named
classes and a discriminating probe-owned row; every vacuity found by
four independent seats is closed; host-state drift is named rather
than asserted. Bounded: PipeWire 1.6.8 / pacat 17.0-98 / alsa-utils
1.2.16 / ffmpeg n9.0.1, this host, DualSense-default-source topology.
Work `65790f1` + fold `1a84ca7`; report-last follows.

r78 frontier seeds: playback-side fallback lattice (ungated but
topologically visible — scout `3e81acc7` measured default-follow,
`pactl set-default-sink` silent rc-0 no-op, mid-play re-link,
`pw-play` SIGSEGV on bogus `media.class`, aplay EBUSY lock-retention
~1–7 s, `alsa_tick_time` falsified), `unlinked_sustained_zeros`, JACK
unshimmed path, parec `--fix-*` header mismatch, MIDI row, GStreamer
`pipewiresrc` fallback equivalence (gst scout landed).

## Fold-2 corrections (scribe r78 audit — findings 5.1–5.6)

- **5.1 A/B provenance** — the pre-fold r76 run existed but lived only
  in `/tmp/audio-prefold` (a detached worktree), so it was absent from
  the audited record. Now preserved in-repo at
  `corpus/live/r77-fold-prefold-ab/` with a NOTE. Its failure set
  (`parec_no_device`, `arecord -D default`/`-D pipewire`) matches the
  post-fold runs — the host-topology classification stands on artifact.
- **5.2 fold regression FIXED** — the pid-owner pw-dump filter emptied
  `target_object_prop` on all 12 cells: `application.process.id` lives
  on the CLIENT object (pw-record's client announces as `pw-cat`), not
  the node, and resolves via `node.client.id`; the value is a JSON int,
  so an int-vs-str compare also filtered silently. Fixed to resolve
  through `client.id` with str-cast, and the leaf is now fail-closed:
  a live leg with an empty provenance witness FAILS.
- **5.3 leaf semantics** — `confound_observed` broadened in the fold to
  also mean "a named fallback class fired" (fallback_default_source);
  semantics disclosed here rather than silently re-scoped.
- **5.4 module ids** — pactl reuses ids across load/unload; "exact
  module id" is exact-per-load, not instance-unique. The vacuity stays
  closed via the unload-fired + pre-loss-consume asserts.
- **5.5 seat ids** — the seat table above cites agent ids not present
  in repo artifacts; authoritative citations are the report files
  `reports/round-77/r77-{author,boundary,baseline,scribe,critic,
  reviewer,verifier,simplifier}.md`.
- **5.6 timestamps** — two r78 scout reports label local (-0300)
  windows as "UTC"; off by 3 h, cosmetic.
