# r83 REVIEWER — surgical correctness review of `a151a226` (`corpus/fixtures/measure_audio.py`, pw-cat/pw-record/pw-loopback props surface)

**Seat: REVIEWER (executor-class, leaf).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r83
landing — `git show a151a226 -- corpus/fixtures/measure_audio.py`
(+2426/−3; committed blob `27fe971077f64de3a6339fba10294fa2d61d666b`,
sha256 `26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea`,
19811 lines). Everything below was measured against a **pinned copy of the
committed tree** (`corpus/live/r83-reviewer/measure_audio_a151a226.py`,
extracted with `git show`, sha-verified equal to the blob) — never against
the moving working tree. **Zero tracked writes, no commits, no
`set-default-*`, no foreign object touched.** The frozen `probeParent`
seat dispatched **no** labrat: the review's arithmetic is re-derived
independently in `audit_pins.py` (see §3) rather than delegated.

---

## 0. Verdict

**PASS with findings.** The r83 family is insertion-only, structurally
sound, and wired correctly; the 7 entries / **128 legs** reproduce
exactly in both committed receipts with **0 failures**; every pinned
constant I re-derived from the receipt data (679 independent checks) and
every one of the five folded boundary corrections I re-measured **live,
under load** reproduces on this host. Teardown is name-verified and clean
in all receipts and in all three of my probes. The findings are real but
none changes a verdict: the **receipt citation for run1 is wrong** (it
names a *red*, uncommitted run's stamp), several gates are 2–4× looser
than the boundary's measured values, the `-n ''` leg's verdict is
pid-unattributed, and one error class is never asserted.

---

## 1. Findings, ranked

### F1 (medium) — the report's run1 receipt stamp names a *different, red* run; two earlier red runs are undisclosed

`reports/round-83/r83-author.md:9-10` cites
`corpus/live/r83-author/measurements-run1.json` as **(21:50:17Z)**.
The committed file is byte-identical to the run dir
`corpus/live/runs/20261015T220105801638Z-pwcat-r83/measurements.json`
(sha256 `4e56f4b0…` both) — i.e. **22:01:05Z**, not 21:50:17Z. The stamp
the report cites is the *third* run dir, `…T215017582814Z-pwcat-r83`
(sha256 `9a1114b0…`), which is **not** the committed receipt and is
**not green**:

| run dir (UTC stamp) | legs | failing entries | fixture revision fingerprint |
| --- | --- | --- | --- |
| `212812356289Z` | 126 | **3** (`props_parse`: 3 landing-form input nodes never published; `channel_matrix`: stereo control absent; `resample`: `s4_peaks_*` "ch1 octave absent (0.0)" — the fixture's *own* artifact classifier was wrong) | no `mono_*_dev_ratio` keys |
| `215017582814Z` | 128 | **2** (`channel_matrix`: `c1_mono_0 @0.35s … amp 0.0 outside the band`; `failopen`: `n_empty: output consumers [SPDIF] != [r93b_in] — the -n '' fail-open arm fails`) | `mono_max_dev_ratio` |
| `220105801638Z` = **committed run1** | 128 | 0 | `mono_mix_dev_ratio` + `stereo_pass_dev_ratio` |
| `220645473277Z` = **committed run2** | 128 | 0 | same as run1 |

The committed receipts are provably from the **final** revision (their
leg leaves carry the final three-way naming keys and
`artifact_outcome: full_wave_abs_octave`), so the verdict is unaffected —
but the citation is not traceable: a reader following the report's
21:50:17Z stamp lands on a red receipt, and neither red run is mentioned
anywhere in the report. The 21:50 failure is also *interesting* rather
than embarrassing: it is the run that proved the stale-default-name pin
(`!= [r93b_in]`) wrong and produced the final **route-shape-not-name**
verdict — the fix the report describes in §9 but attributes to no run.
Impact: traceability/attribution only. Fix: cite `220105801638Z`, and
state that the 21:28/21:50 runs were red at earlier revisions.

### F2 (low-medium) — the armed envelopes are 2–4× looser than the boundary's measured values (inherited r82-F4 pattern)

`reports/round-83/r83-boundary.md` measured control transport
**0.103–0.127 s** and `-d 1.0` at **1.103–1.148 s**; the fixture arms

- `PWCAT_R83_TRANSPORT_MAX_S = 0.50` (`:16399`) as the *control* gate —
  ≈4× the measured worst case. A control regression to 0.45 s passes.
- `PWCAT_R83_D10_DELTA_S = (0.75, 1.45)` (`:16400`): measured deltas are
  run1 `[1.0429, 0.9997, 0.9934]` / run2 `[1.0429, 0.9999, 0.9992]`. A
  "`-d 1.0` adds only ~0.8 s" regression passes the lower bound.
- `PWCAT_R83_D025_DELTA_S = (0.08, 0.60)` (`:16401`) vs measured deltas
  0.29/0.25 — ~2× wide.
- The `s4_peaks` mean gate is `mean < 1500 → fail` (`:18445`) against a
  measured ≈+4450 (a 60 % DC collapse still passes); the octave gate is
  `a2 < 0.20 * clean` (`:18456`) vs measured ≈3176 of ≈8172.

The `-l 1000` gate (`> 0.75 s → fail`, `:17736`) *is* discriminating
(a realized 1 s prop-only failure would fail it). No current receipt is
inside the slack, so this is a *future-regression* exposure, not a false
green.

### F3 (low) — the `-n ''` leg's verdict is pid-unattributed and its nodes are outside the teardown witness

`pwcat_failopen_args_r83_entry` watches the literal names
`input.capture.props` / `output.capture.props` (`:18578-18579`) — `-n ''`
publishes the *default* names, which carry no `r83a_<pid>` tag. Two
consequences:

- The `failopen_foreign_sink` verdict (`:18667-18678`) can be satisfied
  by a **concurrent sibling seat's** `-n ''` nodes; conversely a sibling
  could perturb it. The fixture discloses the attribution gap in
  `_pwcat_r83_teardown` (`:16558-16560`) and records the literal names in
  `generic_capture_props_nodes_after`, but the verdict itself is not
  qualified by ownership.
- Those same names are the only own nodes the teardown witness
  (`PWCAT_R83_PREFIX in n`, `:16583`) cannot see, so a leaked
  `capture.props` node is **recorded but never gated**. Receipts:
  `generic_capture_props_nodes_after == []` in both runs (no leak in
  practice).

### F4 (low) — the `pw_usage` error class is defined and never asserted

`_PWCAT_R83_ERR_CLASSES` (`:16423-16424`) defines
`("pw_usage", r"pw-(?:cat|record|play|loopback|midiplay|mididump) \[options\]")`,
but no leg pins a usage-refusal cell (grep: 1 occurrence, the definition).
Same class as r82's unused `FFPW_R82_FFPLAY` constant. Not a claim the
report makes; dead weight in the family classifier.

### F5 (low) — §5 quotes one run's transport numbers without naming it, and mixes deltas with raw transports

`r83-author.md:51-54` cites `ctl median 0.105 s`, `d10 deltas [1.043,
1.000, 0.999]`, `d025 [0.398, 0.355]`, `-l 1000 [0.106, 0.105]` — those
are **run2**'s numbers verbatim (`ctl_median_s 0.1054`,
`d10_deltas_vs_ctl [1.0429, 0.9999, 0.9992]`, `d025_transports
[0.3981, 0.3547]`, `l1000_transports [0.1057, 0.1053]`). Run1 differs
(median 0.1; third d10 delta **0.9934**, not 0.999; `l1000 [0.1348,
0.0973]`). The paragraph also switches units mid-list: d10 as *deltas vs
ctl*, d025/l1000 as *raw transports*, while the envelopes it names are
delta envelopes. Both runs pass; the citation is ambiguous, not wrong.

### F6 (informational, inherited) — teardown ownership is substring-keyed

`_pwcat_r83_teardown` matches `PWCAT_R83_PREFIX in n` (`:16583`), so a
foreign lane whose pid has our pid as a decimal prefix (`r83a_2305712` ⊂
`r83a_23057120`) would be reported as ours. Same convention as r81/r82
(the r82 reviewer's F5); sink unloads are unaffected (name-verified index
against the exact `sink_name=`).

### F7 (informational) — `pc_drop`'s "no syntax error" gate reads only the last stderr line

`:17430` tests `"syntax error" in leg["stderr_tail"]`, and `stderr_tail`
is `_capture_tail` = the **last** normalized stderr line. A multi-line
stderr whose final line lacks the phrase would pass. In the receipts
`pc_drop.stderr_tail` is empty (the drop really is silent), so the gate is
moot today; `_pwcat_r83_check_rc`'s class+fragment gates read the full
stderr and are unaffected.

---

## 2. What was verified green (exact)

**Wiring / shape.** Exactly **3 removed lines** in the whole file diff —
the mutex `sum([...])`, the `mode` ternary and the `suffix` ternary — each
prepended, insertion-only otherwise (the 2395-line first hunk lands the
whole family). `--probe-pwcat-r83` appears at all five sites:
`:18826` (flag), `:18834` (mutex sum), `:19125` (dispatch), `:19781`
(mode), `:19801` (suffix). `py_compile` clean on the pinned copy. Live
CLI check: `--probe-pwcat-r83 --probe-gst-r81` → **rc=2** argparse usage
error (the mutex rejects two probe flags;
`corpus/live/r83-reviewer/probe_live.json:cli_mutex`).

**Receipts / counts.** Both committed receipts are
`mode == "probe-pwcat-r83"`, **7 entries / 128 legs / 0 failures**,
`coverage_blocked` absent, `sinks_gone` all-true, `own_nodes_after []`,
every unload `rc=0 recycled=false` with a name-verified index
(`audit_pins.json`, 679 checks × 2 runs). Leg counts per entry match the
report's table exactly: 29/19/26/13/18/15/8. Receipt shas:
run1 `4e56f4b0…` == `runs/20261015T220105801638Z-pwcat-r83`;
run2 `4ce6812f…` == `runs/20261015T220645473277Z-pwcat-r83`.

**Pinned constants vs receipts (re-derived, not imported).**
`audit_pins.py` re-implements the fixture's verdict logic from the
recorded data (tag pair derived per run from `contention.own_pid`:
run1 997/1500, run2 1419/1922) and reports **679 checks / 0 failures**:
props-parse lattice (4 landing forms verbatim on `input.<n>`, `-o`
one-sided, `node.name=` override with `input.<n>` absent in every
sample), 7 drop legs (bound-to-bound, empty stderr, full defaults,
`a='b'` partial), 8 hard-error legs (rc=255 + class + fragment + zero
nodes, `--capture-props` ×6 and `--playback-props` ×2), 5 pw-cat/pw-record
arms (rc=1 `--properties`), 18 SIGSEGV legs (rc=-11, `nodes_after []`)
against a live control, the 10 `node.latency` pins + 5 absent-drop pins +
`node.group` on both nodes, the onset summary (ctl medians, d10/d025
deltas recomputed and equal to the recorded ones, `-l 1000` ≤0.75 s), the
matrix summary (control median 8191, `c1_mono` windows inside
`[0.42,0.58]·med`, `m_alone` dev ratios and 3-way arm labels recomputed),
the remix summary (control 8181.6, `output_MONO` collapse, FR ≤0.08·med,
`d0_ctl` downmix band, `d3_sdr` FL-only, `dm_move` rc=0 with post-move
consumers unchanged), the resample summary (`node.rate 1/44100`,
`resample.disable` all-zero with live links, the |x| artifact marks, the
two clean controls, `--rate` inert, `quality` verbatim), and the arg-edge
shapes (`c_empty`/`p_empty`/`n_empty`/`serial`).

**Boundary corrections encoded — and reproduced LIVE under load**
(loadavg 101–124 on 32 cores during the probes; sibling seats' `r83a_*`
legs were visible in `pw-dump` mid-probe):

| folded correction | boundary report | fixture encoding | my live re-measure |
| --- | --- | --- | --- |
| malformed props are 2 classes | `r83-boundary.md:34,75-76,308` | `:16330-16338`, `err_*`/`pc_*`/`pr_*` checks | `}{ garbage` silent (node alive, `media.name "<tag> input"`, stderr empty); `a=b }{ c=d` → **255** `--capture-props: Mismatched bracket`; `media.name=` on `-o` → **255** `--playback-props: Expected object value`; pw-cat & pw-record → **1** `--properties: Mismatched bracket`; all zero nodes |
| empty-prop SIGSEGV family | `:33,65-69,221-222` | `:16339-16342`, 18 legs | 5/5 fresh: `-i ''`, `-i ' '`, `-o ''`, `pw-cat -P ''`, `pw-record -P ''` → **rc=-11 SIGSEGV**, zero nodes |
| `-d` really delays | `:41,186` | `:16396-16401`, `_pwcat_r83_onset_leg` | ctl 0.1052 s vs `-d 1.0` 1.1477 s → **delta 1.0425 s** (fixture receipts' first delta: 1.0429 in both runs) |
| `-l -5` uint32 wrap | `:40,171,234` | `:16345-16346`, `lneg5` pin | in-flight `node.latency = **4294967056/48000**` on both nodes |
| peaks = full-wave \|x\| octave | `:39,146,312` | `:16370-16377`, `s4_peaks` marks | upsample: min 0, `neg_frac` 0, mean 4490, zero_frac 0.139, fundamental 0.0–0.1, octave 3175.8/3162.5; **matched-rate control clean** (min −8192, neg 0.465, fundamental 8172.5, octave 0.0) → upsample-only |

Also re-measured live: `-l 5`→240/48000, `-l 2.5`→96/48000,
`-l 10000`→480000/48000, `-d 0.25`→4000/48000, `-d 1.0`→16000/48000,
`-l`+`-d` both orders→240/48000, `-l 0`/`-d abc`→absent, `-g`→`node.group`
on **both** nodes (probe #2).

**Refusal handling.** Every refusal leg is gated on rc **and** class
**and** (for the parse family) the stderr fragment, plus a zero-node
witness; the SIGSEGV family is gated on rc **and** signal name **and**
zero nodes (`_pwcat_r83_check_rc` `:17198-17211`, `_pwcat_r83_check_segv`
`:17186-17195`). No leg treats "still running" as a crash or vice versa
(`killed_at_bound` is a separate field).

**Teardown ownership.** Unloads go through
`_pwcat_r83_unload_own` → `_gst_r81_unload_own(sink_name=…)`: the module
table is re-read immediately before firing and only the index whose args
carry our `sink_name=` is unloaded (`:12821-12843`). Receipts:
`recycled:false`, `rc:0`, `skipped:not_listed` never needed; witnesses
`sinks_gone` (all true) + `own_nodes_after` ([]) + the pid-unattributed
`generic_capture_props_nodes_after` recorded separately. **No
`set-default-*` anywhere in the block** (grep-clean: the only occurrences
are the "never set-default-*" comments). The only pactl verbs are
`load-module`, `unload-module` (name-verified), `get-default-sink` (read)
and `move-sink-input` (own stream, resolved by **exact** `node.name`
match in `_module_r80_sink_input` `:11818`). Every spawn is
`start_new_session=True`; every kill is `killpg` on a seat-spawned pid
(9 `killpg` / 7 `start_new_session` in the block); taps are `-n`-bounded
`pw-record` runs.

**Contamination honesty.** Tones only ever reach probe-owned sinks:
`_pwcat_r83_feed` is called with `PWCAT_R83_NS_A` or the
fail-closed-guarded `feed_sink` (`:16851-16852` raises for a non-own
sink), and every play/record leg targets `ns_a`/`ns_b`/`ns_m`/`ns44`.
The `-C ''`/`-P ''`/`-n ''` fail-open legs are topology-only with an
explicit `content_witness` string ("declined — fail-open legs carry no
tone feed" / "declined — silence-only path to the shared sink") — and the
receipts agree (no feed process on those legs). The r93b_in default-sink
rotation the report describes in §9 **is** receipted (run1's
`oracle_at_start.sink_pactl == "r93b_in"` **and**
`inventory.default_sink == "r93b_in"` in 2 entries — `props_parse` and
`remix` — while `default_sink_now` at sample time is the SPDIF sink) — and
the 21:50 red run is the one that proved the name-pin wrong (F1).

**Receipt-vs-report numbers.** Every number I spot-checked in
`r83-author.md` matches one of the two committed receipts (m_alone arms
run1 `['stable_mono','unmeasured','stable_mono']` / run2 ×3; the
`c1_mono_1` silent leg; `n_empty` → `failopen_foreign_sink` both runs;
zero `coverage_blocked`; "all 4 sinks unloaded name-verified"), with the
F1 stamp exception and the F5 run-attribution ambiguity. Host header
(PipeWire 1.6.8, pactl 17.0-98-gb096, WirePlumber 0.5.17, Python 3.14.7,
NumPy 2.5.3, kernel 7.2.3-arch1-3) verified on this host.

---

## 3. Probe artifacts (untracked, `corpus/live/r83-reviewer/`)

| file | content |
| --- | --- |
| `audit_pins.py` / `audit_pins.json` | independent re-derivation of every r83 pin from both committed receipts: **679 checks, 0 failed** |
| `measure_audio_a151a226.py` | the pinned committed fixture (sha256 `26431adf…` = blob `27fe9710…`) |
| `probe_live.py` / `probe_live.json` | malformed-prop classes, SIGSEGV family, `-d` onset, peaks artifact, CLI mutex; teardown witnesses |
| `probe_live2.py` / `probe_live2.json` | in-flight props: latency lattice incl. the uint32 wrap, `-g`, silent-drop defaults |
| `probe_live3.py` / `probe_live3.json` | crash legs with **default** naming leak zero nodes (witness adequacy) + live sibling `r83a_*` contention evidence |
| `tmp/*.wav` | tone files and the four monitor taps analyzed above |
| `manifest.json` | 15-file sha256/bytes manifest |

All three probes ended with `sinks_gone` all-true, `own_nodes_after []`,
zero leftover spawns; the module count returned to the pre-probe 44 and
`pactl get-default-sink` is unchanged (`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29`).

---

## 4. Remaining risks / blockers

- **Risk (F1):** receipt traceability — the report's run1 stamp resolves
  to a red, uncommitted run; the two earlier red runs are undisclosed.
  The committed receipts are nonetheless from the final revision
  (fingerprint-verified) and green.
- **Risk (F2):** the transport/artifact envelopes absorb a 25–45 %
  regression; a future regression inside them would pass.
- **Risk (F3):** the `-n ''` verdict is pid-unattributed — under a
  concurrent sibling `-n ''` leg it can be satisfied for the wrong
  reason (no current receipt affected).
- **Environment note:** the working tree drifted **during** this review —
  a sibling seat edited `corpus/fixtures/measure_audio.py` at 19:16:13
  (−37/+13, `_ffpw_r82_*` / `_landed_on`, **zero r83 mentions**), and the
  fleet's load was 101–124/32 while I probed (the author's own runs
  recorded `host_is_quiet: true`). My review is against the pinned blob
  `27fe9710…`; any r83-relevant change after `a151a226` invalidates it.
  The pre-existing tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  modification predates this seat (mtime 19:08:53; already dirty in my
  first status read) and is not mine.
- **Not verified by me:** the full 128-leg family re-run (verifier
  seat's scope — I ran single-leg reproductions of every folded
  correction, not the family); the 21:28/21:50 runs' fixture revisions
  are not recoverable from git (only their receipts survive, untracked).
- **Blocker:** none. No resume mutation attempted (no
  `resume_continuity_v1` preflight was required or run).

Seat stop. No commits, no tracked writes, no scope widening.
