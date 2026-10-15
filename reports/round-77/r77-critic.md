# R77 CRITIC (audio) — attacking commit `65790f1` (`--probe-capture-r77`)

Seat: **critic**. Repo `~/Projects/shokunin/audio-shokunin` @ HEAD `65790f1`
(`r77 work: capture-source lattice + fallback law + reader matrix`, authored
2026-10-14 17:10:17 −0300 = **20:10:17Z**). Host `plazir27`, measured
2026-10-14 17:12–17:20 local (20:12–20:20Z). Toolchain identical to the
author's session (PipeWire 1.6.8, pacat 17.0-98-gb096, alsa-utils 1.2.16,
ffmpeg n9.0.1, SoX_ng 14.8.0.1, Python 3.14.7).

**Write scope: exactly `corpus/live/r77-critic/` (untracked, new) plus this
report. Zero tracked-file edits. No device is held by this seat's batteries —
every leg factory is monkeypatched (see §7).** Evidence read first:
`reports/round-77/{r77-author,r77-scout,r77-boundary,gst-scout}.md`.

**Verdict: the round's *findings* are sound and its prior rows are stable, but
its *gates* are thinner than its headline table.** Four executable
counterexamples show r77 rows that pass with an absent/empty field, and a
post-commit run of the committed fixture **failed three of its own assertions
on this host** under contention it had already recorded.

---

## 0. Headline

| # | counterexample | class | verdict |
| --- | --- | --- | --- |
| 1 | **the committed gate failed 3 assertions** in the 20:13:36Z post-commit run: `target loss … got ['r77_loss_sink'] -> []`, `re-link is not total`, `lattice prop_auto … got []` — while the same receipt records `host_is_quiet: False`, `fixture_runs: 6` | **witness integrity / run isolation** | **FALSIFIED AS WRITTEN** (law survives; the *witness* inverts) |
| 2 | 12 arecord device-axis TERM legs, **every one with no file at all**, `failures: []` | gate vacuity | **FALSIFIED** (battery A) |
| 3 | format-axis rate legs fed **20244 / 24756 / 31244 / 43244 B**, `failures: []` — the "byte count is rate-invariant" law is ungated | gate vacuity | **FALSIFIED** (battery B) |
| 4 | reader matrix driven by a **2× wrong unit calibration** (`soxi_s = 192000` vs `expected_frames = 96000`), `failures: []` | gate vacuity | **FALSIFIED** (battery C) |
| 5 | **7 of 11** lattice rows are satisfied by the single hypothesis *"ignore the target, always consume the current default sink's monitor"*; no row targets a non-default sink's `.monitor` | premature saturation | **FALSIFIED** (battery E) |
| 6 | tone witness: `carries_tone` is True only at `nonzero_frac ≥ 0.075`, not the stated `> 0.05` (bucket == threshold dead zone) | witness discrimination | **FALSIFIED** (measured) |
| 7 | `sha_match_control := (None == None) → True`; live receipt has `target_object_is_request: true` with `target_object_prop: [null]` (a foreign pw-dump node) | false provenance | **FALSIFIED** (battery D + live) |
| 8 | split sentinel rename row, `.monitor` resolution, `usage_refusal` no-file | — | **NOT falsified** (positively checked) |
| 9 | `--probe-capture-r76` replay vs two prior receipts | prior rows | **STABLE** (798/799 leaves byte-identical) |

---

## 1. F1 — the gate fails on its own recorded contention (highest severity)

**Counterexample (live, not synthetic).** `corpus/live/runs/20261014T201336507976Z-capture-r77/measurements.json`
— a post-commit run of the committed fixture (launched ~20:11Z, after the
20:10:17Z commit; the working tree is still clean at that path), ~3 min after
the author's last clean run (`…200645323501Z`, a pre-commit iteration of the
same file):

```
capture_target_loss_r77_probe.failures:
  target loss: expected the capture to consume the probe sink before the
  unload and …SPDIF__sink after, got ['r77_loss_sink'] -> []
  target loss: the post-loss artifact is NOT byte-identical to the FALLBACK
  node's own same-bound control — the re-link is not total
capture_source_lattice_r77_probe.failures:
  lattice prop_auto: expected consumption of default_sink (…SPDIF__sink),
  got [] (target_arg=None)
```

The same receipt's own contention block: `{'pw_record': 1, 'fixture_runs': 6,
'host_is_quiet': False}`. The next post-commit run (`…201650898147Z`,
`fixture_runs: 8`) passed cleanly — so this is **host-state-dependent
instability**, not a systematic break.

**Two mechanisms, both inside the commit.**

*(a) The probe-owned sink has a fixed global name.*
`CAPTURE_R77_NULL_SINK = "r77_loss_sink"` (line 4216) and
`_capture_r77_null_sink_id()` returns the id of the **first** `pactl list
modules` line *containing* that name (line 5095) — with two concurrent runs of
the same fixture, each run can unload the other's module. Receipt evidence:
the wall-clock leg records `unloaded: {'exit_code': 0, 'error': 'Failed to
unload module: Module  not loaded\n'}` (the id it read was already gone), the
lattice cell `prop_garbage` consumed **`r77_loss_sink`** (the *other* run's
sink) and was swallowed by the `foreign` carve-out (`confound: "foreign
node(s) ['r77_loss_sink'] consumed"`), and `link_after_exit` shows the ghost
`r77_loss_sink` link in the `prop_pulse_token` cell. A probe-owned resource
with a non-unique name is a duplicate authority over a shared node.

*(b) The link-differencing mitigation cancels this cell's own link.*
`_capture_r77_link_delta` differences `pw-link -l` against a baseline taken
before the spawn, and `pw-link -l` keys by **port name** — so a stale link
from the previous cell (the author's own §7.3 ghost, 1–2 s) sits on the same
`pw-record:input_FL/FR` entries and the cell's own link cancels. The 20:13
receipt is unambiguous:

```
prop_auto: live_at_link_sample True, bytes 384044, data_finalized True,
           content {peak 4457, nonzero_frac 0.8, carries_tone True},
           link_producers [], consumed_nodes [], foreign_links_ignored True,
           stale_link_before_cell True
```

The **content** witness proves the law exactly (the capture consumed the
default sink's monitor and carried its tone); the **topology** witness says
`[]` and the gate fails the cell. `_capture_r77_wait_clear` noticed the stale
table (`stale_link_before_cell: True`) but only *records* it — it does not
retry, and `ambiguous` is defined as `len(nodes) > 1`, so the **empty** case
is not classified as a confound.

**Impacted axes:** `run_isolation`, `witness_integrity` (the round's headline
law is asserted through a witness that can invert on a shared host).

**Smallest safe correction.** (i) `CAPTURE_R77_NULL_SINK = f"r77_loss_sink_{os.getpid()}"`
and match that exact name in `_capture_r77_null_sink_id()`; (ii) in
`_capture_r77_link_delta`, when the differenced node set is empty and the
baseline was stale (`stale_link_before_cell`), return the same named confound
as `ambiguous` instead of an empty consumption set — or re-sample after the
2 s ghost window before judging. Either alone would have turned the 20:13
failures into named confounds instead of assertions.

---

## 2. F2 — the arecord device axis has **no value assertions at all**

**Counterexample (executable).** `corpus/live/r77-critic/vacuity_batteries.py`
battery A drives the real `capture_arecord_sever_r77_entry()` with synthetic
cells that satisfy every *other* assertion and sets all 12 `term_*` device
legs to `file = {"exists": False}` (no file was written):

```
device-axis TERM legs: 12; of those, file absent: 12
entry failures: []
eintr_cells: []  scout_alsa_read_eintr_reproduced: False
```

The gate iterates `device_legs` and only checks **key presence**
(lines 5415–5420). The 12 TERM cells — the round's "15/15 cells did not
reproduce the scout's `alsa_read_eintr`" claim — are emitted and never
asserted. `eintr_cells`/`scout_alsa_read_eintr_reproduced` are a *recorded
negative*: a host where the scout's shape **does** reproduce would pass the
gate silently.

**Impacted axis:** `gate_vacuity` (the r76 `data_actual_zero` class of bug,
reproduced one entry over).

**Smallest safe correction.** In the `device_legs` loop, after the key check:

```python
fin = leg.get("file", {})
if fin.get("exists") is not True or fin.get("data_finalized") is not True \
        or leg.get("error_class") != "aborted_by_signal":
    failures.append(f"arecord device axis {key}: expected a finalized "
                    f"aborted_by_signal capture, got {fin} / "
                    f"{leg.get('error_class')}")
```

That converts 12 unasserted legs into gated ones without touching the
"record, don't assert" treatment of `eintr_cells`.

---

## 3. F3 — the format axis' rate-invariance law is ungated

**Counterexample (executable).** Battery B feeds the four `--rate` legs byte
counts that are *not* rate-invariant:

```
byte counts fed, by rate leg: {"rate_8000": 20244, "rate_44100": 24756,
                               "rate_96000": 31244, "rate_192000": 43244}
entry failures: []
```

Only `baseline` is byte-pinned (line 5657). `CAPTURE_R77_FORMAT_LEGAL`
carries `{"rate": N}` alone for the rate legs, and the loop checks only the
keys present in the expectation dict — so `-n` being a frame bound (the
author's §6 headline) is asserted **nowhere**. The live receipt does show
19244 B for all four rates, so the law holds; the gate cannot detect its loss.

**Impacted axis:** `gate_vacuity`.

**Smallest safe correction.** `("rate_8000", ("--rate", "8000"), {"rate": 8000, "bytes": 19244})`
for each rate leg (the expectation loop already reads `got` from `fin["fmt"]`,
so add a `bytes` branch, or append the four `bytes == 19244` checks next to
the baseline line).

---

## 4. F4 — the reader matrix' unit calibration is decorative

**Counterexample (executable).** Battery C runs the real
`capture_readers_r77_entry()` with a `_capture_r77_readers` that answers
`soxi -s`/`-D` in **interleaved samples** (the exact unit confusion the
calibration exists to catch):

```
calibration expected_frames=96000
answers={"wave": 96000, "ffprobe": 96000, "soxi_s": 192000,
         "soxi_D": 192000, "sndfile": 96000}
entry failures: []
reader_honesty: {"soxi_s": {"inflated": 12, "_wrong": 12, ...}}
```

A 2× unit error is reported as *"soxi is wrong on 12/12 wounds"* and **nothing
fails**. `entry["unit_calibration"]` (line 5164) and `entry["reader_honesty"]`
(line 5221) are both emitted and never asserted, so the round's whole frontier
3 (the 12×5 matrix, the pinned ordering `sndfile ≳ ffprobe > wave > soxi`)
carries zero gate weight.

**Impacted axis:** `gate_vacuity` + `witness_discrimination`.

**Smallest safe correction.** Two lines in the failures list:

```python
cal = entry["unit_calibration"]
for r in ("wave", "ffprobe", "soxi_s", "soxi_D", "sndfile"):
    if (cal["readers"].get(r) or {}).get("value") != cal["expected_frames"]:
        failures.append(f"unit calibration: {r} must answer "
                        f"{cal['expected_frames']} frames")
```

and (optionally) pin `reader_honesty["soxi_s"]["_wrong"] >= 5` so the matrix's
declared finding is a gate, not prose.

---

## 5. F5 — the fallback witness: which rows can actually separate the law?

**Counterexample (executable).** `corpus/live/r77-critic/lattice_power.py`
reads the fixture's own `CAPTURE_R77_LATTICE` and asks of each row: *is this
row satisfied by the single hypothesis H_fallback = "the target name is
ignored and the capture always consumes the current default sink's monitor"?*

```
rows satisfied by H_fallback ALONE: 7/11
    prop_default_sink, prop_default_sink_monitor, prop_source,
    prop_default_token, prop_pulse_token, prop_garbage, prop_auto
rows that can separate the law from H_fallback: 4
    prop_other_sink, noprop_default_sink, noprop_default_sink_monitor,
    noprop_source
rows whose TARGET is a `.monitor` name:
    ['prop_default_sink_monitor', 'noprop_default_sink_monitor']
of those, rows whose target is a NON-default sink's monitor: []
```

So the row that carries the scout's falsified claim
(`prop_default_sink_monitor`) is **still non-discriminating**: honoured and
fallback both land on the default sink, and the tone is played *into the
default* by design, so the content witness is fallback-consistent too. The
falsifying experiment lives only in the boundary seat's separate harness —
`corpus/live/r77-boundary/probe-p1c-mechanism.json`:

```
default moved to Speaker; target <SPDIF>.monitor -> signature [False, True]
consumed "SPEAKER monitor" (the fallback); pw-dump monitor_named_nodes: []
```

Re-run that state through the r77 gate and the row still passes (want = the
default = the consumed node), whether or not `.monitor` names resolve. The
author's §1 prose does label the cell a fallback — but the **table is the
coverage contract**, and the contract cannot express the distinction.

**Impacted axis:** `witness_discrimination` / premature saturation.

**Smallest safe correction.** One row, separable without moving the default
sink:

```python
("prop_other_sink_monitor", "other_sink_monitor", True, "default_sink", True),
```

with `_capture_r77_lattice_targets` returning `tg["other_sink"] + ".monitor"`.
Honoured ⇒ hdmi monitor (silent); fallback ⇒ the default monitor (tone). The
boundary seat already measured this exact cell.

---

## 6. F6/F7 — the two `None` classes

**F6, the tone threshold.** `_capture_r77_pcm_stats` buckets
`nonzero_frac = round(frac/0.05)*0.05` and then pins
`carries_tone = nonzero_frac > 0.05` — the bucket value **equals** the
threshold, so the class is dead in `[0.025, 0.075)`:

```
frac 0.03-0.07 -> bucket 0.05 -> carries_tone False
frac >= 0.075  -> bucket >= 0.10 -> carries_tone True
```

A capture that carried 2.5–7.5 % nonzero samples (a low-duty or partially
captured tone, an attenuated route) reads **"no tone"** and satisfies the two
`exp_tone=False` rows. The live tone rows are 0.80–0.85 and the silent rows
0.0, so the *True* direction is robust (a full tone is 13× over the
threshold); the loose direction is the False one. The **discriminating
minimum** the witness can honestly claim is `frac ≥ 0.075`.

**F7, `None == None`.** Battery D:

```
_capture_r77_sha256(<absent a>) = None; _capture_r77_sha256(<absent b>) = None
sha_match_control := (a == b) = True
```

`sha_match_control`/`sha_match_dead_sink` (lines 4931–4934) read as
"byte-identical" from two absent files (the leaf checks elsewhere in the entry
do fail, so the entry cannot pass vacuously — but the leaf is a false witness
in isolation). The same class is **live** in the 20:13 receipt's `prop_auto`:

```
target_object_prop: [null]      <-- a foreign pw-record node (pid mismatch)
target_object_is_request: true  <-- None == None
```

`_capture_r77_node_props` takes `dump["nodes"][0]` with no pid/serial match
(line 4372–4379), and `target_object_is_request` compares
`nodes[0]["target_object"] == target` where `target is None` for the no-target
cell.

**Impacted axis:** `evidence_provenance`.

**Smallest safe correction.** (i) `carries_tone = round(frac/0.05)*0.05 >= 0.10`
(or compare the raw fraction); (ii) `hc is not None and hc == hl` for both sha
leaves; (iii) match the pw-dump node on `application.process.id` == the
spawned pid and require `target is not None` before asserting the trap.

---

## 7. Answers to the assigned hunts

1. **Vacuity — which gate passes with an absent/empty field?** F2 (12
   device-axis TERM legs), F3 (rate legs' bytes), F4 (unit calibration +
   reader tallies), plus `entry["rename_is_silent"]` (line 5570, computed,
   never asserted) and the refusal legs' `exit_code` (never asserted — a
   refusal at rc=2 passes). The live rows that *look* most exposed
   (`prop_*` byte counts, `data_finalized`) are in fact covered, because the
   tone check is a strict identity (`tone is not exp_tone`), so `None` fails
   loudly. **Legs emitted-but-never-asserted: the whole device axis, the
   whole reader matrix, the rate legs' bytes, `rename_is_silent`, the refusal
   rc.**
2. **The fallback witness — could a silent-monitor capture pass the lattice
   rows?** In the *expected-silent* direction, yes for the two rows that
   expect `tone=False` if the capture carried < 7.5 % nonzero samples (F6);
   in the *expected-tone* direction, no — 0.80 vs 0.0 is unambiguous. The
   sharper problem is F5: for **7 of 11 rows** both witnesses are
   fallback-consistent, so those rows cannot separate the law from
   H_fallback at all. The discriminating minimum for the content witness is
   `nonzero_frac ≥ 0.075`, and for a row's *power* the tone must be played
   into a node other than the predicted fallback.
3. **`declared_echo` — keyed on reader output alone?** No, and that is the
   right design: `_capture_r77_frame_class` compares the reader's answer
   against **two artifact-derived quantities** (`data_actual // frame_bytes`
   = honest, `data_declared // frame_bytes` = declared), so the class is not
   circular in the "reader grades itself" sense. The residual circularity is
   different and worth naming: `honest` is a *header-vs-file-length*
   consistency verdict, so on any finalized file (`declared == actual`) the
   `declared_echo` branch is **unreachable by construction** and a reader that
   echoes a patched field scores "honest" — i.e. the matrix ranks *which
   reader trusts the file length*, not which reader measured the audio. A
   read that **accidentally** equals the truth therefore passes as honest, and
   the case that would expose it is a header-**rate** error (soxi -D is
   converted back with the fixture's own header rate at line 4492, so a wrong
   header rate is invisible in the frame domain). The scout's own `-f cd` row
   (12173.94 s vs 11184.81 s — same declared frames, different header rate) is
   the local evidence that the rate field can differ across legs.
   *Smallest safe correction:* record `soxi -D`'s raw seconds and assert
   `frames == round(seconds * header_rate)`, or add one wound with a
   deliberately wrong header rate.
4. **Split sentinel — can a mere >2 GiB growth satisfy the rename row?** No:
   `cross.requested_path_exists is not False` fails (line 5549) and
   `rot-01.wav` is required **positively** from the fresh scratch listing
   (line 5553) — a failed or non-renaming leg leaves either the requested path
   or no siblings, and both fail. Verified against the live receipt
   (`rot-01.wav 2147483692 B, riff "other", data_declared 0x7FFFFFFF`,
   `requested_path_exists False`, `rename_is_silent True`). Ungated residue:
   `cross.exit_code == 0` and `rename_is_silent` itself, and the split
   member's `data_actual == 0x80000000` (only `bytes` and `data_declared` are
   pinned). *Correction:* assert all three.
5. **`usage_refusal` — is "no file at all" asserted?** Yes, positively:
   `file.exists` is `path.exists()` on a fresh tempdir path
   (`_capture_wav_inspect`, line 3034), asserted `is not False` (line 5669).
   Not inferred from an absent artifact. Ungated: `exit_code == 1` (line 5642
   covers legal legs only) and the "never touches the device" claim, which is
   prose — no link/device sample is taken for the refusal legs.
6. **Prior rows — replay `--probe-capture-r76`.** **Stable.** A fresh replay
   (`corpus/live/runs/20261014T201458231716Z-capture-r76`, `EXIT=0`,
   `failures: {}`) compared leaf-by-leaf against the post-edit receipt
   (`…200218106707Z`) and the pre-edit receipt (`…193039362478Z`):
   **798 of 799 leaves identical to both** (0 structural drifts in all six
   entries; the single drift is `capture_roundtrip_r76_probe.detect_legs.sox.captured.stderr_tail`
   — a content-derived `Volume adjustment` number, not a gated field). The
   commit's two deleted lines are `main()`'s `mode`/`suffix` ternaries,
   rewritten prepend-only; I verified programmatically that the tails are
   byte-identical to `503689c`, so **no prior flag's value changed**.
   (`corpus/live/r77-critic/r76-prior-row-stability.txt`.)

---

## 8. Cross-reference, not my assignment

`--probe-capture-r77` was **not added to the exclusivity guard**: the
`sum([...]) > 1` list at `main()` still ends at `args.probe_capture_r76`
(line ~5800, `parser.error("choose one probe mode")` at 5802). So
`--probe-capture-r77 --probe-capture-r76` runs *both* families while `mode`
and the run-dir suffix say `probe-capture-r77` — a receipt-identity mismatch
(and mutual device contention). The r77-baseline seat is already on this; I
record it only because it is the same class (identity/duplicate authority)
and lands in the same commit. *Correction:* add `args.probe_capture_r77` to
the sum list.

---

## 9. What I could **not** falsify (recorded, not skipped)

- **The arecord open-header law** (bound-derived `-d N` / `-s S` /
  unbounded → `0x80000000`) is asserted and matched in every receipt
  (`576000 / 960000 / 2304000 / 1200000 / 2147483648`, `finalized False`),
  and the r76 `0x80000000` row is re-measured inside the same entry — the
  re-scoping cannot silently drop it.
- **The split sentinel** is the strongest-checked leg in the round (§7.4).
- **The target-loss artifact-level law** (rc=1, exact `-n` bytes, finalized)
  survived every receipt including the contended one; only the *witness*
  broke.
- **The lattice's live cells** are guarded by strict identity on the tone
  (`None` fails), so an unsupported/absent content witness cannot pass.
- **Byte discipline in the r77 entries themselves:** every added leg is
  `-n`/`-d`/`-s` bounded except the loss wall-clock leg (SIGTERM at 3.0 s)
  and the two split legs (20 ms dir-summing watchdog, 2.4 GB SIGKILL,
  60 s wall cap, scratch removed in `finally`). No new unbounded `-D null`
  leg was introduced.

---

## 10. Provenance and footprint

- **Byte discipline (this seat):** `corpus/live/r77-critic/` = **48 KB**
  (scripts + JSON/text receipts), the replay's run dir = **56 KB**, all temp
  legs written to a seat-local `TMPDIR` and removed. **Total 104 KB.** The
  largest single leg artifact was the replay's roundtrip monitor capture
  (240 000 frames = 960 044 B ≈ 0.94 MB); every other leg was ≤ 480 KB —
  nothing written to `/tmp`'s tmpfs and no unbounded leg run.
- **No device was held by the batteries:** A–E monkeypatch the fixture's own
  leg factories (`_capture_r77_sever_cell`, `_capture_r77_file_leg`,
  `_capture_r77_readers`) and call the *real* gate functions, so no
  `pw-record`/`arecord`/`ffmpeg` capture is spawned; the only subprocesses are
  the entries' own cheap enumerations (`pactl list`, `arecord -l`,
  `pw-dump`). I loaded no null sink of my own ("own null sink" was not needed
  — no target-loss leg was run by this seat).
- **No foreign node was captured.** The single real capture this seat ran is
  the fixture's own `--probe-capture-r76` replay, whose legs target the
  default source/monitor exactly as the committed fixture specifies. At
  launch the r77-baseline seat's `--probe-consumers2-r75` run was live; that
  contention is why the r76 replay is reported as a *structural* comparison
  rather than a byte-exact one (and it still matched 798/799 leaves).
- **Commands.**
  `TMPDIR=corpus/live/r77-critic/tmp timeout -k 5 600 python3 corpus/fixtures/measure_audio.py --probe-capture-r76`
  → `r76-replay.stdout.json` (EXIT=0);
  `python3 corpus/live/r77-critic/compare_r76.py <fresh> <prior-post> <prior-pre>`;
  `python3 corpus/live/r77-critic/vacuity_batteries.py` → `gate-vacuity-batteries.json`;
  `python3 corpus/live/r77-critic/lattice_power.py` → `lattice-power.txt`;
  the receipt census → `r77-gate-census.txt`.
- **Provenance.** Receipts cited: the author's clean r77 run
  (`…200645323501Z`), the post-commit contended run
  (`…201336507976Z`), the post-commit clean run (`…201650898147Z`), the
  boundary seat's `probe-p1c-mechanism.json`, and my r76 replay
  (`…201458231716Z`). The r77 receipts stamped 19:46–20:06Z are pre-commit
  working-tree iterations (the commit is 20:10:17Z) and are labelled as such
  in `r77-gate-census.txt` — they are *not* evidence about the committed
  fixture.

**Bottom line for the judge:** keep the measurements, arm the gates. The four
vacuous legs (F2–F4 + `rename_is_silent`/refusal rc) are one-line additions to
existing failure lists; F5 is one table row; F1 is a per-run resource name plus
one confound branch; F6/F7 are two predicate tightenings. None of them changes
a measured value, and none of them is a tradeoff the canonical judge must
reject — they are strictly more discriminating at the same cost.
