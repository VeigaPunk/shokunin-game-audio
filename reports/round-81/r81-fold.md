# r81 FOLD — gate-approved corrections applied to the `--probe-gst-r81` family

**Seat** FOLD (executor) · **host** devin/plazir27 · **repo**
`/home/vgpnk/Projects/shokunin/audio-shokunin` · HEAD `f91c7d0` · work
commit `6aa03e6`. **Scope**: `corpus/fixtures/measure_audio.py` only
(+ this report). No commit, no push — the orchestrator commits.

Fixture sha: `0dad37ee6500ca3d…` (pre-edit, == `6aa03e6` blob) →
`5eaba74b532eb9c62d529fe3d94534c36cb3b3954365cb61b8552ade9ed49d82`
(post-edit). `python3 -m py_compile` clean. File 15246 → **15219 lines**
(net −27; `git diff --stat`: +50/−75 in the fixture).

No `lsp` device answers this file (same gap recorded by the simplifier);
all edits are literal, review-verified text edits over the single file —
cross-references were re-grepped after editing (see each item's proof).

## Items applied

Line numbers: **before** = committed tree at `6aa03e6` (simplifier's
numbering); **after** = post-fold file.

| # | item | before | after | applied |
|---|------|--------|-------|---------|
| S1 | `ports` in `_gst_r81_graph` | :12641 docstring, :12651 tuple, :12666–12669 `elif Port`, :12681–12682 return | :12641 docstring, :12651 tuple, return :12677 (`{nodes, links, clients}`) | yes |
| S2 | dead `_props` helper | :13434–13436 | removed (`_node` kept at :13407–13409) | yes |
| S3 | `kill_proc`/`call` arms + docstring | :12927–12928 docstring, :12960–12967 arms | docstring :12912–12914; only `unload_module` + `else:{"unknown_event"}` remain (:12943–12946) | yes |
| S4 | `"ns"`/`"tag"` ctx keys ×6 | :13166, :13325, :13629, :13783, :14025, :14139 | all six now `ctx = {}` (:13143, :13302, :13606, :13760, :14002, :14116) | yes |
| S5 | `<tone>` redaction token | :13000–13001 | :12977–12978 (`<out>` + `<tmp>` kept — `<tmp>` retained as the one-token guard per simplifier's note) | yes |
| S6 | `expect_class` write + `cls` slots | :14067 write; `cls` in all 7 `L` tuples | write + slots gone; loop is `for name, argv, op, hit in L` (:14040–14042) | yes |
| S7 | `placeholder_7ffff000` arms + loss tolerance | :12780, :12797 arms; :13947–13949 predicate | arms removed (:12771–12775, :12788–12793); predicate now **pins** `riff=="wavenc_streaming"` AND `riff_size==0x7FFF0024` AND `data=="wavenc_streaming"` AND `data_declared==0x7FFF0000` (:13919–13930) — closes reviewer F1 inside the fixture | yes |
| S8 | `_gst_r81_ns_ensure` duplicate core | :12864–12871 inline load | `else: leaf = _loopback_r79_sinks_load([GST_R81_NS])[GST_R81_NS]` (:12851–12858); present-check + caller-owned `loads` write unchanged | yes |
| S9 | redundant `wall_cap=GST_R81_WALL_S` ×3 | :13202 (n4), :13358 (r8 kw-dict), :14066 (exit loop) | removed; signature default at :12907 unchanged (the loss legs' 4.5 s overrides kept) | yes |
| L1 | `p8_bogus_server` leg | tuple :14058–14062, expect row :14077 | removed; exit arm 7→6 legs, family 55→54 | yes |
| F1 | freeze predicate accepted falsified `0x7FFFF000` | (see S7) | corrected constants pinned; a hypothetical `0x7FFFF000` now surfaces as `other:2147479552` and **fails** the loss leg | yes (via S7) |
| F3 | `parse_rc1_no_artifact` vacuous for `out_path=None` legs | e3/e8/e9 ran `out_path=None`, shape `"none"` | **chose "real out_path" over dropping assertions**: e3/e8/e9 now carry a `filesink` + `out_path` (f4/f5/f6), shape `"absent"` — per-leg and class-level no-artifact checks are substantive for all 4 parse legs | yes |

F3 detail — e3/e8/e9 argv changes (each verified against `gst-launch-1.0`
on this host before the family run; parse refusals never create the
filesink file, matching e1's proven `exists:false`):

- **e3** `… audiotestsrc bogus-prop=42 num-buffers=4 ! wavenc ! filesink
  location=<e3.wav>` — hit `'no property "bogus-prop" in element
  "audiotestsrc"'`, rc=1, no file. (was `! fakesink`, no out_path)
- **e8** `… audiotestsrc num-buffers=4 ! tee name=t ! F64LE-caps !
  pulsesink  t. ! wavenc ! filesink location=<e8.wav>` — hit
  `"can't handle caps"`, rc=1, no file. **Note**: the naive fix
  (`! wavenc ! filesink` in place of `pulsesink`) was tested and
  *rejected on evidence* — wavenc accepts F64LE, so the pipeline
  constructed and WROTE the file (rc=0, exists=yes). The tee keeps the
  `F64LE→pulsesink` refusal while arming a real filesink branch.
  Also tested and rejected: `! pulsesink ! wavenc ! filesink` — it does
  still refuse with "can't handle caps", but the `pulsesink ! wavenc`
  tail is a never-runnable topology; the tee shape is runnable-intent.
- **e9** `… audiotestsrc ! wavenc ! filesink location=<e9.wav> !` —
  dangling `!` keeps the `"syntax error"` hit, rc=1, no file.
  (was bare `audiotestsrc !`, no out_path)

## Evidence

- **Compile**: `python3 -m py_compile corpus/fixtures/measure_audio.py`
  → OK. The tracked `__pycache__/measure_audio.cpython-314.pyc` that
  py_compile regenerated was restored to HEAD (`git checkout`) so the
  tracked blob stays clean for the orchestrator's commit.
- **Family re-run** `timeout 900 python3 corpus/fixtures/measure_audio.py
  --probe-gst-r81` → `failures: {}`, receipt
  `corpus/live/runs/20261015T181903683088Z-gst-r81/measurements.json`
  (pinned copy `corpus/live/r81-fold/gst-r81/run.measurements.json`,
  sha `26052a6b…`). 24 entries = 17 prior + 7 gst; **54 legs**
  (15/5/12/6/7/6/3 — exit arm 7→6 after p8 removal), `mode:
  probe-gst-r81`, every entry `failures: []`.
  - Frozen pins verified live: t3–t6 all
    `riff=wavenc_streaming / riff_size=0x7fff0024 / data=wavenc_streaming
    / data_declared=0x7fff0000` — exactly the corrected constants.
  - `class_summary = {parse_rc1_no_artifact: true,
    runtime_refusal_zero_byte: true}` — now substantive over 4 armed
    parse legs.
  - Receipt string census: `p8_bogus`, `expect_class`,
    `placeholder_7ffff000`, `unknown_event`, `killed_pgid`, `<tone>`,
    `<tmp>` all occur **0** times; `<out>` redaction still fires on all
    18 capture argv strings.
  - Hygiene: seat-owned names `gst_r81_auth_1701611` /
    `gst_r81_1701611_*` (names are `os.getpid()`-derived — **no
    env/name-prefix knob exists in the family**; the fold seat's pid
    makes them seat-owned by construction). `sinks_gone` true and
    `own_nodes_after []` in every loaded entry; fired unloads
    `verified_index==captured`, `recycled:false`, rc 0; the loss entry's
    teardown unload correctly `skipped:not_listed` (event already
    unloaded it — same shape as the pinned runs).
- **Battery pass** (documented invocation — there is no `--runs` flag;
  output lands in `corpus/live/runs/<stamp>-<suffix>`, pinned copies
  under `corpus/live/r81-fold/battery1/`):
  - `normal` → `…T181920520268Z-normal`, failures `{}`, rc 0. Receipt sha
    `8e8cdad6cc3c356d…` — **byte-identical** to the author/baseline
    normal receipts (6-way-identical sha from the verifier report).
  - `--probe-capture-r78` → `…T182248433946Z-capture-r78`, rc 1, **one
    contention failure** in `playback_default_follow_r78_probe`: the
    follow stream landed on the live default
    `alsa_output.usb-…HiFi__SPDIF__sink` instead of the probe's own
    `r78_def_sink_1772531`. This is the reviewer's documented
    residual-risk 1 (default-sink coupling under a foreign lane) — an
    honest red on an r78 codepath this fold did not touch; the sibling
    `r92s_*` scout lane was live during the window (`r92s_in` sink
    observed in `pactl list sinks short` before the run, gone after).
    Receipt `2ba3e6f3…`.
  - `--probe-capture-r79` → `…T182834250973Z-capture-r79`, failures `{}`,
    rc 0. Receipt `d6e2ae11…`.
  - `--probe-module-r80` → `…T182900462376Z-module-r80`, failures `{}`,
    rc 0. Receipt `31d20df1…`.
  - **Shape confirmed unchanged: 86 entries / 136 legs**
    (17/0 + 25/59 + 25/67 + 19/10) — identical to the author's battery
    shape.

## Declined / retained candidates

- **L2** (`c0≡e10`, `p6≡e11` cross-arm duplicates), `t1≡t2`,
  `t3≡t4≡t5≡t6`, the unconsumed `alsasrc` lattice row, and the
  `nosuchelement_r81_xyz` template control — **retained** per the
  simplifier's own reasoning (each is a named in-arm witness of a
  different claim; deletion would break arm self-containment).
- **T3** (6 never-fired error-class entries + 2 shadowed) — below the
  bar; kept as diagnostic vocabulary.
- **S5 optional follow-up** (`<tmp>` removal) — declined; kept as the
  one-token guard, per the simplifier's own recommendation.
- **F2** (`node.dont-reconnect` assertion on freeze legs) — reviewer
  recommendation, **not in the gate-approved correction set** handed to
  this seat; left for a future round.
- Everything in simplifier §3 ("checked and NOT dead") untouched.

## Remaining risks / blockers

1. **e8 tee variant**: verified on this host (class `gst_parse_refusal`,
   hit `"can't handle caps"`, rc 1, no artifact) and green in the family
   run. Its stderr wording changed (`could not link t to pulsesink0` vs
   `audiotestsrc0 to pulsesink0`) — the armed assertion is the substring
   `"can't handle caps"`, still satisfied.
2. The one r78 contention red is environmental (default moved mid-entry
   during the sibling r92s lane), not a fold regression — the r78 family
   is untouched by this diff and `normal` is byte-identical to the
   pinned sha.
3. `parse` in `class_summary` now lists only armed legs implicitly via
   `expect` class filtering; no leg remains that could pass the summary
   vacuously (all 4 parse legs measure a real `out`).

Stopping here — files changed: `corpus/fixtures/measure_audio.py`,
`reports/round-81/r81-fold.md`, receipts pinned under
`corpus/live/r81-fold/`. Not committed.
