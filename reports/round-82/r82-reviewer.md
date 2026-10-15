# r82 REVIEWER — surgical correctness review of `aa03c347` (`corpus/fixtures/measure_audio.py`)

**Seat: REVIEWER (executor-class, leaf).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r82 diff
(`git show aa03c347 -- corpus/fixtures/measure_audio.py`, +2170/−3, final sha
`eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4`).
Baseline for the pin audit: the commit's own receipts
(`corpus/live/r82-author/ffmpeg-r82-runs/{run1,run2,final3,final4}.measurements.json`,
sha-verified against `corpus/live/runs/*-ffmpeg-r82/`) and
`reports/round-82/r82-boundary.md` + its receipts.
Probes under `corpus/live/r82-reviewer/` only. **No tracked writes, no
commits, no set-default-\*, no foreign object touched.** The frozen
`probeParent` seat dispatched **one** read-only `labrat` (agent
`13e6c55c`, advisory arithmetic on the tone bands; result folded in below).

---

## 0. Verdict

**PASS with findings.** The r82 family is insertion-only, structurally sound,
the eight entries / 76 legs are wired correctly, every pinned constant I
audited matches the committed receipts, refusals are gated with their classes,
and teardown is name-verified and clean in all four formal receipts. Three
findings are real and actionable: a **falsified "never read as `mine`"
distinctness claim** that can inject cross-lane tone verdicts, **two
boundary-mandated position/rc cells that are not armed**, and an **incomplete
contamination leg list**. The rest are loose-bound / hygiene items.

---

## 1. Findings, ranked

### F1 (medium) — the r82 tag pair collides with the r78/r79 pair inside both classifiers' ±6 % bands; the "never read as `mine`" claim is false

`measure_audio.py:14259-14261` defines the r82 pair `1210.0 / 1780.0` and
`:14563-14568` claims it is "*a pair DISTINCT from the r78 1k/1.5k tag so a
foreign probe's tone can never read as `mine` at the 6% window tolerance*".
But the r78/r79 family's pair is pid-dependent (`:5970-5971`):
`L = 997 + (pid % 4) * 211`, `R = L + 503` → `{997,1208,1419,1630}` /
`{1500,1711,1922,2133}`, written at amp 8192 both channels (`:6023-6039`),
which clears the r82 floor (`PLAYBACK_R78_TONE_AMP_MIN = 3000`).

For **pid % 4 == 1** the foreign pair is `1208 / 1711`:
- r82 classifier bands (`:14607-14618`): L `1210 ± 72.6` = `[1137.4, 1282.6]`,
  R `1780 ± 106.8` = `[1673.2, 1886.8]` — **both contain the r78-pid1 pair**.
- reverse: r78-pid1 bands L `1208 ± 72.48`, R `1711 ± 102.66` **both contain
  the r82 pair**.

Exact probe (fixture's own classifiers, imported, not re-implemented) —
`corpus/live/r82-reviewer/probe_tone_bands.json`:

| synthetic tone | classifier | mine_windows | carries_tone |
| --- | --- | --- | --- |
| 1208/1711 (r78 pid1) | `_ffpw_r82_tone_windows` | **20/20** | **true** |
| 997/1500 (r78 pid0, control) | `_ffpw_r82_tone_windows` | 0 | false |
| 1210/1780 (r82 self, control) | `_ffpw_r82_tone_windows` | 20 | true |
| 1210/1780 | `_playback_r78_tone_windows` pinned pid1 | **20/20** | **true** |
| 997/1500 | `_playback_r78_tone_windows` pinned pid1 | 0 | false |

Root cause is the 0.1 s window grid (4800 samples @ 48 kHz → 10 Hz bins):
1208 Hz and 1210 Hz land in the same bin, so the ±6 % tolerance is not even
exercised. Impact: any **concurrent r78/r79/r80/r81-family lane with
pid % 4 == 1** (they all use `_playback_r78_write_tone`, e.g. `:9705`, `:9986`,
`:10210`, …) that plays its tag tone onto the shared default sink while an r82
tap is listening can (a) trip the false red `play p0/p6/p10: the tag tone
LEAKED to the shared default sink` (`:15388`) and (b) satisfy the
witness-presence gates (`the shared-default tap never carried the tag tone`
`:15393`, `loss … never carried the tag tone post-unlink` `:15833`) for the
wrong reason. The
fleet ran exactly such siblings during this window (author §5). Fix: pick r82
frequencies outside every r78 band (e.g. L≈1310, R≈2450) or make the r82
classifier require an exclusive bin.

### F2 (medium) — the boundary's position-law **second exception** and the ALSA `-channels 0` rc=8 cell are not armed

`reports/round-82/r82-boundary.md` §V asks to "*Pin the position law with its
two exceptions (`-frame_size` aborts for any N≥1; outdev options in input
position error rc=8) and the debug evidence*" and to "*pin ALSA `-channels` →
rc=8 (option absent) as distinct from pulse `-channels 0` → 222*".

- Only the first exception is armed (`ci3` deprecation `:15558`, `ci5`
  SIGABRT `:15563`). No leg places an outdev option before `-i`; the entry
  docstring (`:14214-14217`) states the swallow as a universal "except the
  deprecated `-frame_size`".
- Reproduction (my probe, `corpus/live/r82-reviewer/probe_rc8.log`): the
  boundary's exact shape `ffmpeg -f pulse -buffer_size 16384 -i
  no_such_r82rev.monitor -t 1.5 -c:a pcm_s16le out.wav` → **rc=8
  `Option buffer_size not found.` 3/3**; the same option with a non-`.monitor`
  unresolvable name → rc=251 (open fails first). The fixture already uses
  `<ns>.monitor` inputs everywhere, so this cell was armable with seat-owned
  resources. Boundary receipts: `corpus/live/r82-boundary/runs/c3/pre_buffer_size/`
  (rc=8).
- ALSA `-channels 0` → rc=8 `Option channels not found.` is in
  `corpus/live/r82-boundary/runs/c6/alsa_ch_0/{cmd.txt,meta.json}`
  (`-f alsa -channels 0 -i hw:0,0`); the fixture pins only the pulse side
  (`e2_ch0` → 222, `:15932`). No ALSA `-channels` leg exists in the r82 block.
- Minor: the docstring's universal-swallow phrasing is only corrected in a
  nested ci6 comment (`:15630-15634`), where the boundary's "`-ac`/`-ar`
  encoder spellings DO land" carve-out lives.

### F3 (low-medium) — the playback entry's declared contamination list is incomplete

`entry["contamination"]["legs"]` (`:15256-15262`) lists
`p1,p2,p3,p4,p5,p8` only. Receipts (final3/final4) show **`p7_env_vs_flag`**
(`-device default` beats `PULSE_SINK=ns`) and **`p11_env_target`**
(`PIPEWIRE_PROPS target.object` ignored) both route the tag tone to the shared
default sink: `tap_def` `carries_tone=true`, `mine_windows` 16 and 17. Both
legs are thus undeclared audible contamination on the shared default sink —
the exact class the contamination ledger exists to disclose.

### F4 (low) — bounds are 13–50× looser than the boundary's pins, and one boundary pin is recorded-only

- `_refusal` (`:15030-15044`) fails only above **4.0 s** while its own message
  says "outside the ~1 s envelope"; the boundary measured **0.022–0.063 s**
  and said "do not pin 0.93 s". Receipts: c1/c2/c12 wall 0.067/0.067/0.075 s.
  A 3.9 s refusal would pass.
- `FFPW_R82_RELINK_BOUND_S = 0.8` (`:14258`) vs the boundary's pinned
  **≤60 ms** (35–57 ms measured); receipts re-link at the 0.2 s sample
  quantum, so the armed bound is ~13× the measured worst case.
- The boundary's "capture **no gap ≥0.1 s**" pin is not gated: `cap_tone`
  spans are recorded (`:15748-15752`) and never asserted. `final3` shows the
  captured-wav tone stopping at 1.1 s in `t2_cap_r2` (`mine_spans [[0.2,1.1]]`,
  9 windows) and a 0.3 s gap in `t2_cap_r1` (`[[0.2,1.1],[1.4,1.5]]`), i.e.
  the report's "mine_spans continuous (16 windows each)" sentence holds for
  run1 only. Not a verdict impact (not gated), but the claim is not armed and
  not stable.

### F5 (low, inherited) — teardown node-survival check is substring-keyed, not pid-keyed

`_ffpw_r82_teardown` (`:14662-14690`) matches `FFPW_R82_TAG in n or
FFPW_R82_XTAG in n or n == FFPW_R82_NS`, i.e. `"r82ff_2422178" in
"r82ff_24221781"` is **true**. A foreign lane whose pid has our pid as a
decimal prefix would be reported as ours ("r82-tagged nodes survived"), and
the docstring's "foreign r82ff names from other lanes are NOT counted —
ownership is pid-keyed" overstates the guarantee. Same convention as r81
(`:12885`), so inherited rather than new; sink teardown is unaffected
(name-verified index against the exact `sink_name=`).

### F6 (low) — degenerate-environment silent substitutions; one dead constant

- `c12_sink_name` uses `default or "<none>"` (`:15005-15007`): with no
  resolvable default sink the leg silently tests a bogus name and still passes
  `_refusal` — a false green for the "bare default-sink name is refused" cell.
- `c4` (`elif default:`, `:15096`) and `c13` (`:15209`) skip their
  target/producers assertions when `default` is falsy **without** a
  `coverage_blocked` leaf; `c5` and the playback p-legs do declare the same
  condition. (Also affects `t1/t2/f0/f1` `if default` guards.)
- `FFPW_R82_FFPLAY = "ffplay"` (`:14267`) is defined and never used (the only
  unused r82 constant).
- Redundant guard: `if any(rows.get(d) is None …)` in `d0` is already covered
  by the preceding `rows.get(dev) != flags` comparison.

---

## 2. What was verified green (exact)

**Wiring / shape.** Exactly **3 removed lines** in the whole file diff — the
mutex `sum([...])`, the `mode` ternary and the `suffix` ternary — each
prepended, insertion-only otherwise. `args.probe_ffmpeg_r82` appears once in
each of the four sites (`:16436` flag, `:16444` mutex, `:16735` dispatch,
`:17358` mode, `:17378` suffix). `py_compile` clean. Committed blob sha ==
report's `eb865760…`; the four receipts are 8 entries / 76 legs / **0
failures** each with `mode == "probe-ffmpeg-r82"`, and `final3/final4` copies
sha-match `corpus/live/runs/20261015T200955375107Z-ffmpeg-r82` and
`…201238976393Z-ffmpeg-r82`.

**Pinned constants vs receipts.** Re-extracted from `final3` and compared
against the code's `_ffpw_r82_prop_check` tables — every audited pin matches:
`c0` (`node.rate 1/48000`, `latency 2400/48000`, `fragsize 9600`,
`target.object` `.monitor`-stripped, `stream.capture.sink=true`,
`producers=[ns]`, tone 19 windows); `c8` (`1/44100`, `2205/44100`, `4410`,
wav 44100/1ch); `c10` (`fragsize 33600`, `maxlength 4194302`); `c14`
(`1/12345`, `617/12345`, `2468`, wav 12345); `p0` (`tlength 384000`,
`prebuf 380164`, `minreq 3840`, `maxlength 4194304`, `latency 8192/48000`,
`want-driver=True`); `b0–b6` and `ci0–ci6` tables verbatim (incl. `b6`
3072/2052/1024/`256/48000`, `ci2` 65536/`16384/48000`); `f0`/`f1` (ffplay
native `media.role=Game`, `node.async`, `2048/48000`, no `client.api`; SDL
pulse `pipewire-pulse`, `Audio Stream`, 6144/4100/2048, `512/48000`,
`target.object` = default → PULSE_SINK ignored); `f2` rc=0 wall 0.13 s,
`pcm_s16le/48000/2`, `start_time` epoch-class; `e1–e6` rc/class/hit; `a5`
realized `params_251` (the `plugin_rc0` arm armed but unrealized — disclosed);
`a6` 44100; `d0` `{alsa DE, pulse DE, jack D., oss DE, sndio DE}`, no
pipewire row; `d1` 234 `ff_unknown_format`; `d2` rc=0 zero rows;
`d4.star_vs_pactl = agree`; `d5/d6` option tables incl. `Lavf63.1.101` /
`record` / `48000` / `2` defaults; `c3` 3/3 `eio_251`; `p7` winner
`device_flag`; `p11` `{consumers:[default], target.object:null}`.

**Boundary corrections encoded.** `p12` rc=187 `ff_pulse_sink_info` with no
node and silent taps (the empty-string carve-out; boundary §1/§V);
`c13` rc=0, literal `.monitor`-stripped `target.object`, `producers=[default]`
(the permissive hole); capture EIO class pinned without the 0.93 s timing;
`c14` no pulse clamp vs `a6` ALSA clamp; `{eio_251, hang_killed}` and
`{plugin_rc0, params_251}` envelopes with realizations recorded; `-nostdin`
exclusion for ffplay documented in-code.

**Refusal handling.** Every refusal leg is gated on rc **and** class **and**
that no audio was produced (`_refusal`, `:15030-15044`; `e*` out-bytes check;
`p12` node + both taps silent): c1/c2/c12 251 EIO, c11/e6 253 ESRCH, c3
envelope, p9 187 access-denied, p12 187 sink-info, e1–e3 222 ERANGE, e4/e5 -6
libpulse asserts, a0/a1 251 busy, a3 251 params, a4 251 unknown-PCM, ci5 -6
sched assert, d1 234 EINVAL.

**Teardown ownership.** All unloads go through
`_ffpw_r82_unload_own` → `_gst_r81_unload_own(sink_name=FFPW_R82_NS)`
(re-read + `sink_name=` arg proof; `recycled:false`, rc=0, or
`skipped:not_listed` where the leg's own event already fired). Receipts:
`sinks_gone {r82ff_ns_<pid>: true}`, `own_nodes_after []`, `coverage_blocked`
absent in all four entries. No `set-default-*` anywhere in the block
(grep-clean); every kill is `killpg` on a seat-spawned pid; taps are bounded
`pw-record -n` runs on the shared default sink (declared contamination) or the
seat sink; `r82ff_*`/`r82ffx_*` naming holds throughout.

---

## 3. Probe artifacts (untracked, `corpus/live/r82-reviewer/`)

| file | content |
| --- | --- |
| `probe_tone_bands.py` / `probe_tone_bands.json` | fixture's own classifiers vs synthetic r78/r82 tones (F1) |
| `r78pid1_pair.wav`, `r78pid0_pair.wav`, `r82_pair.wav` | synthetic tones |
| `probe_rc8.log`, `rc8-{1,2,3}.stderr` | rc=8 `Option buffer_size not found.` 3/3 (F2) |
| `rc251.stderr` | control: same option, non-`.monitor` input → 251 |
| `alsa_ch0.stderr` | ALSA `-channels 0` with bogus device → 251 (open precedes the option check; boundary receipt is the rc=8 authority) |

The labrat's independent arithmetic (agent `13e6c55c`) agreed with the probe:
TRUE-for-some-pids, false exactly at pid % 4 == 1, in both directions.

## 4. Remaining risks / blockers

- **Risk (F1):** verdict instability under sibling contention — the r82 family
  and the r78/r79 family can cross-credit each other's tone on a shared sink
  whenever the sibling's pid % 4 == 1. No current receipt is contaminated
  (0 failures ×4), but the immunity comment is wrong.
- **Risk (F2/F4):** the fixture is looser than the boundary's corrections in
  three places (rc=8 cell absent, ALSA `-channels` rc=8 absent, re-link 0.8 s,
  no-gap pin unarmed); a genuine regression inside those envelopes would pass.
- **Not verified by me:** the intermediate `f9d88dcc…` fixture sha (run1/run2)
  is not recoverable from git; I audited only the committed blob against the
  committed receipts. I did not re-execute the 76-leg family (no re-run
  requested); the pin audit is receipt-based plus two narrow probes.
- HEAD advanced during the review window (sibling `1e88e8e2 r93 scout`); the
  reviewed blob is unchanged — `corpus/fixtures/measure_audio.py` is still
  `eb865760…`, and `aa03c347` is an ancestor of the current HEAD.
- **Blocker:** none. No resume mutation attempted (no `resume_continuity_v1`
  preflight was required or run).

Seat stop. No commits, no tracked writes, no scope widening.
