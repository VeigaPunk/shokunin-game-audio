# r92 VERIFIER — frozen-tree gate on the landing `ccbce758` (the filter-chain DSP lattice)

Seat: **verifier** (non-author, audio-shokunin r92). Lane
`~/Projects/shokunin/audio-shokunin`; basis **`git archive` of the r92
landing `ccbce758`** (the mint-time HEAD; r96 landed 42 s later, r97 during
this window) extracted to `/home/vgpnk/r92-verifier/tree-r92`, plus the
current HEAD at archive time **`b8ff4efc`** (r97) extracted to
`/home/vgpnk/r92-verifier/tree-head`. Window **2026-10-16 10:03Z–10:25Z**
(local UTC−3), host `plazir27`, loadavg 2–6 with four to six sibling
batteries live (r96/r97/r98/r99/r100/r93 lanes). `TMPDIR=~/Projects/shokunin/tmp`.

**Zero tracked writes by this seat, zero commits, zero pushes, no
`set-default-*`.** Every artifact this seat produced lives under
`/home/vgpnk/r92-verifier/` (the archive root the assignment named) or in this
report. The fixture was never edited in any tree this seat archived.

Duty: run the full `--probe-filterchain-r92` family fresh on committed bytes,
re-derive all 80 declared legs, apply mutation/negative controls, and take an
exit census (`own_nodes_after` empty, no `r92a` residue). The frozen
`probeParent` slot spawned **exactly one** read-only `labrat` (§8).

## 0. Verdict

**GATE PASS on committed bytes — with one substantive finding (the `d_qneg`
leg is measured on a saturated capture) and six lesser findings (F2–F7).**

| gate | result |
| --- | --- |
| r92 block byte-identity: landing ↔ current HEAD ↔ author worktree | **PASS** — 2295 lines / 103 580 B / sha256 `8b4b1608…` in all three |
| dispatch block + wiring re-derivation | **PASS** — 28 lines / sha256 `802f23d1…`; argparse, mutex, mode, suffix all present in the landing and in HEAD |
| run A, frozen landing bytes `ccbce758` | **PASS** — rc 0, `failures: {}`, no `coverage_blocked`, `own_nodes_after: []` ×4, 26+20+18+17 leg keys |
| run B, current HEAD bytes `b8ff4efc` | **PASS** — rc 0, `failures: {}`, no `coverage_blocked`, `own_nodes_after: []` ×4 |
| independent law re-derivation, both runs | **PASS** — 304 laws / 304 PASS / **0 FAIL / 0 BLOCKED**, all 81 leg keys (80 declared legs + `i_residual`), 64 nested label rows, 3 residual cells |
| raw-WAV re-derivation of the recorded cells | **PASS** — all 17 dsp legs reproduce to ≤0.0005 dB in both runs; residuals 0.5/0.5/0.0 LSB reproduce exactly |
| author's two green receipts, same law set | **PASS** — 304/304 and 303/303 |
| author's pre-fix red receipt, same law set | **never green** — 4 FAIL (incl. the `a_ladspa` class defect) + 6 BLOCKED (leg absent) |
| mutation controls (4) | **4/4 as designed** — 2 armed-input mutations caught on exactly the mutated leg, 1 no-op control green, 1 named coverage block |
| receipt forgeries (8 + 2 subtle + 3 fail-open probes) | **12/13 caught; 1 declared no-op control**; arm-tolerated fabrications caught by the raw re-derivation at 0.023 dB |
| exit census | **PASS** — `own_nodes_after: []` in all 8 entry-runs; **zero** `r92a` objects/processes for any of this seat's five pids; lock files inert with **FREE** flocks |

Findings: **F1** `d_qneg` POST capture saturates (5.73 % of samples at the s16
rail) — the recorded flat ≈+19 dB is a saturation-compressed reading;
**F2** three arms can raise instead of failing (labrat, §8); **F3** the
tool-missing block exits rc 0 (named block is the only witness); **F4**
`r92-integrate.md`'s worktree line range is off by one; **F5** the max-energy
window can tie within 0.03 % and pick a window adjacent to the signal tail;
**F6** the family lock file remains after exit (inert); **F7** disclosed
self-contamination: run B ran while this seat's own mutation controls were
live (the family recorded them as foreign `r92a` nodes; no armed cell moved);
**F8** two arms the sibling critic named as fail-open (`d_fhi`, the
`a_ports_none` feed witness) are closed by this seat's law set — verified by
forgery (§4).

**Wave convergence (independent seats, same window).** The sibling `r92-critic`
(static re-derivation + 191-mutation battery, no live battery) independently
reached the same substantive finding: *"the recorded `Q=-1` 'broadband ~+19 dB'
is a clip ceiling"* (`r92-critic.md` §4.1), with a different method
(`clip(10·x)` re-simulation reproduces the recorded vector exactly; the
unclipped `3·x` reads exactly +9.542 dB) and the same conclusion that the
falsification itself stands. The sibling `r92-scribe` (custody audit) reports
the same leg-count reconciliation (commit message 80 vs 81 receipt keys) and
two documentation drifts (§F4). Where the three seats differ is method, not
verdict: critic = static/mutation, scribe = custody, this seat = the live
re-run on committed bytes.

---

## 1. Frozen tree and byte identity

| check | measured | verdict |
| --- | --- | --- |
| archive `ccbce758` (landing) | tar stream sha256 `4a9c702eb2275943f7abde9f6465ea24220b3a4ed43a55b8f063635d89ea4b74`, 3.2 GB tree | PASS |
| archive census, landing | **44 576 files** = `git ls-tree -r ccbce758` **exactly** (symdiff 0), 0 symlinks | PASS |
| archive `HEAD` at archive time | HEAD had moved `7358f13b`→**`b8ff4efc`** (r97, committed 07:01:30 local) while this lane prepared; archived sha256 `91c500ad66c482130f49f1bd898e171dd3bc6116bc99582ddc366d7b8f7aee88`, 44 581 files = `git ls-tree -r b8ff4efc` exactly | PASS |
| fixture identity | `corpus/fixtures/measure_audio.py` sha256 **`4e5fe3e6…ca90`** (landing) = the sha `r92-integrate.md` declares as the merged image; HEAD `7a070fa8…ca2bc`; author worktree **`5b17ad3d…d20c`** = the author's declared implementation sha | PASS |
| **r92 block identity** | the block (banner `# r92: THE FILTER-CHAIN DSP SURFACE` → last line before the next top-level construct) is **2295 lines / 103 580 B / sha256 `8b4b1608c6e5dbaf24e47b62a0a49aba68938233589b38865e134b419b7ffee8`** — byte-identical in the landing, in current HEAD (`b8ff4efc` at archive time; re-checked at `a2c6e3b7` after the window), in the author's worktree, and in the dirty worktree as edited by sibling lanes | PASS |
| dispatch block identity | 28 lines, sha256 **`802f23d1ef75cd2b8514704d0d70ded4f56b4ad3c89f5c1dc2202f9f0f67ae11`** = the integrate report's declared hash, and byte-identical to the worktree block (worktree lines 33877–**33904**) | PASS (range nit: F4) |
| wiring, landing | argparse row 41603; mutex line 41614 (138 tokens, `args.probe_filterchain_r92` ×1, appended last); `mode` 42886 (r92 first); `suffix` 42906 (r92 first); dispatch block 42208–42235 | PASS |
| wiring, current HEAD | argparse row 46038; mutex 140 tokens with the r92 token ×1; dispatch block 46645–46672 (same sha); `mode`/`suffix` carry the r92 branch after r97/r96 | PASS |
| `py_compile` in both frozen trees | rc 0 | PASS |
| symbol census | **78** module-level names defined by the block, 78 unique, **0 collisions**; the four dispatch keys defined 1× each; conflict markers 0 | PASS |

## 2. Fresh runs on committed bytes

| run | tree | receipt | sha256 | rc | failures | coverage_blocked | leg keys | own_nodes_after | contention |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **A** | `tree-r92` (landing `ccbce758`) | `…/runs/20261016T101236603490Z-filterchain-r92/measurements.json` | `42011c21d542121aaf4c1e061cae151bc01a744a658688c8b2f164d50054ff0b` | **0** | `{}` | none | 26/20/18/17 | `[]` ×4 | `host_is_quiet: false`, 5–12 foreign fixture runs, 2 foreign SPDIF links recorded (dsp entry) |
| **B** | `tree-head` (HEAD `b8ff4efc`) | `…/runs/20261016T101810912899Z-filterchain-r92/measurements.json` | `c3883ed2f6c623bced61b9879030877f90a3005e9af7889c76e029bb9433ea5c` | **0** | `{}` | none | 26/20/18/17 | `[]` ×4 | `host_is_quiet: false`, 2–4 foreign fixture runs |

Run A 10:03:08Z→10:12:36Z; run B 10:13:41Z→10:18:10Z. Both runs also carry the
fixture's 17 base entries (ui/stem/…), all green; only the four
`filterchain_*_r92_probe` entries are in scope here.

**Cross-run cell determinism.** 137 recorded cell keys per receipt, compared
across four runs (author A, author B, verifier A, verifier B):

- **verifier A ≡ author A** on every key except the volatile ones listed below
  — the two independent runs of the same committed bytes agree cell-for-cell
  (`d_qneg` 19.015/18.979/19.289/18.729/19.289; `d_gneg140` −46.566; residuals
  0.5/0.5/0.0; delay shifts; label table; eof classes; inventory counts).
- **verifier A vs verifier B (landing vs current HEAD): 125 of 137 keys
  identical.** The 12 differences are: `a_load_dbg5.lines` (6126 vs 8516 —
  recorded, floor 500, never armed), the `fixture_runs` contention counters,
  `foreign_r92a_nodes` (see F7), the floor-dominated `d_gneg140` 200 Hz cell
  (−46.566 vs −46.341, Δ0.225 dB inside the arm's ±1.5 dB), and three
  window-placement probe cells (§5/F5).
- Across all four runs the only armed cell that moves is that same
  floor-dominated `d_gneg140` 200 Hz cell (author A/B and verifier A:
  −46.566; verifier B: −46.341) — the deep-attenuation instrument spread the
  author's own §7 names; the decisive clamp witness is the 20 dB separation
  from the unclamped value, not this cell.

## 3. Independent law re-derivation

`runs/r92v_laws.py` — **304 laws** transcribed from the arms but computed from
the receipt's *recorded fields*; the entries' own `failures`/`coverage_blocked`
lists are never the detector (one cross-check law reads them explicitly). For
the 17 dsp legs the law set re-derives the transfer functions **from the raw
captured WAVs** with this seat's own RIFF reader, own max-energy window, own
single-bin DFT, own analytic RBJ implementation, and its own convolution +
alignment search for the residual cells. Absent legs are BLOCKED, never green.

| receipt | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| author green #1 (`…T094024556467Z`) | 304 | **304** | 0 | 0 |
| author green #2 (`…T094602455160Z`) | 303 | **303** | 0 | 0 |
| **verifier run A (landing bytes)** | 304 | **304** | 0 | 0 |
| **verifier run B (HEAD bytes)** | 304 | **304** | 0 | 0 |
| author pre-fix red (`…T093301592620Z`) | 306 | 296 | **4** | **6** |

Per-leg coverage in both verifier runs: **26/26 arm legs, 20/20 dsp legs,
18/18 ir legs (17 + `i_residual`), 17/17 wpx legs — all PASS**, plus the four
entry-hygiene groups (daemon, tools, `own_nodes_after`, `live_after`, no
coverage block). Inside the nested rows: `a_labels` 64/64 (26 load labels ×2,
6 non-labels ×2 with the `cannot create label` class) and `i_residual` 3/3
cells (`≤1 LSB`, `n_gt_1lsb = 0`).

Strongest re-derivations (both runs):

- **recorded gains reproduce from the raw WAVs**: max |recorded − recomputed|
  = **0.000 dB** (rounded) on all 17 dsp legs — the receipt's `gain_db` cells
  are the raw captures, not a transcription.
- **residuals reproduce exactly**: own convolution + own alignment → 0.5 /
  0.5 / 0.0 LSB at lag 24576 over 12 287 compared samples, `n_gt_1lsb = 0`.
- **window placement**: on every cell the stimulus actually excites with real
  level (ref magnitude ≥1e-4, response ≥ −20 dB), a second window 12 000
  samples later moves the reading by ≤0.05 dB; attenuated and floor-dominated
  cells are recorded, not armed.
- the author's pre-fix red receipt derives the `a_ladspa` class defect
  (`fc92_type_missing` where the specific LADSPA class is armed) and its
  missing `d_gneg140` leg is BLOCKED — a receipt that predates a leg never
  reads silently green.

## 4. Mutation and negative controls

M1–M3 ran on hardlink copies of the frozen landing tree (the fixture replaced
by rename, so no shared inode was written) and M5 ran from the frozen landing
tree itself with a farmed `PATH`; the entry-level runner calls one entry
function, which is where the arms live.

| # | control | mutation | result |
| --- | --- | --- | --- |
| M1 | armed constant | `d_gneg140` clamp centre −46.362 → −40.000 | **CAUGHT** — exactly one failure, `d_gneg140: Gain=-140 is not clamped…`, measured cell unchanged (−46.566) ⇒ the red is arm-driven, not measurement-driven |
| M2 | fixture/stimulus | 2-tap IR second tap `64 → 70` | **CAUGHT** — `i_2tap: the 2-tap IR is not reproduced (gap 64…)`, `out_n_gt = 2`; the residual arm stays green because it compares against the IR file's own kernel (by design — the peak-gap arm is the pin) |
| M3 | no-op control | comment-only insertion in the block | **GREEN** — `failures: []`, 20 legs, `own_nodes_after: []` |
| M5 | coverage naming | `PATH` = 3115-entry symlink farm with **`wpexec` removed** | **NAMED BLOCK** — `coverage_blocked: ["missing tools: ['wpexec']"]`, 0 legs; `failures: []` ⇒ a full run would exit **rc 0** with a blocked entry (F3) |

Receipt forgeries (tampered copies of verifier run A, `runs/forged/`):

| forgery | result |
| --- | --- |
| `blank-verdicts` (blank all four `failures` lists + drop `coverage_blocked`) | 270 PASS — **declared no-op control**: the lists are not the detector |
| `own_nodes_after → ["r92a_999999_fake"]` | **CAUGHT** (hygiene law) |
| `d_copy` 200 Hz gain → 0.5 | **CAUGHT** (`d_copy.unity`) |
| `d_gneg140` 200 Hz → −66.0 (the unclamped value) | **CAUGHT** (2 laws: is-the-−120-response, not-unclamped) |
| delete the `i_2tap` leg | **BLOCKED ×7** — never green |
| `v_spa` filter-graph count 6 → 5 | **CAUGHT** |
| `i_residual.i_2tap` 0.5 → 4.0 LSB | **CAUGHT** |
| `i_2tap` peak gap 64 → 70 | **CAUGHT** |
| arm-tolerated `d_lp` 200 Hz −0.007 → −0.03 / −0.05 (inside the arm's 0.06 dB) | **CAUGHT by the raw re-derivation** (0.023 / 0.043 dB > the 0.02 dB tolerance) — the raw check is ~3× tighter than the arm |
| critic-F3 probe: `d_fhi.gain_db` deleted (the fixture's own arm greens) | **CAUGHT** by this law set (`d_fhi.passthrough`, `len != 5`) |
| critic-F4b probe: `a_ports_none.feed_link` deleted (the fixture's own arm greens) | **CAUGHT** by this law set (`a_ports_none.feed_refused`) |
| control: `a_ports_sink.feed_link` deleted (fail-closed in the fixture too) | **CAUGHT** by both (`a_ports_sink.feed_ok`) |

## 5. Cross-seat cell re-derivation (tracked receipts)

The committed `corpus/live/r92-scout/` and `corpus/live/r92-boundary/` receipts
(658 files) were read on the frozen tree; the boundary's independent analytic
replay re-derives the family's armed cells:

- `copy` unity (0.000 dB ×5), `bq_lowpass` RBJ (−0.007/−3.012/−24.477/−47.37),
  `bq_peaking +6` (6.000), `bq_notch` (−93.812 at fc; skirts −0.184/−0.284),
  the Q clamp (`Q=10`, `Q=10.5`, `Q=1e9` all identical), the >Nyquist
  pass-through (`49000`/`97000` → 0.000), `Freq=0`/negative → exact zeros
  (`nz=0`), the delay map (`48 / 480 / 2400 / 2431 / 2431`), the silent
  convolver class (`E=0 W=0` at debug 3 **and** 5), `bq_raw` silence in all
  three arms, `Gain` inert on `bq_lowpass`, and the inventory (6 SPA
  filter-graph plugins, no ffmpeg; both LADSPA dirs absent; 25 LV2 bundles,
  0 `.so`; the shipped kemar conf referencing an unshipped IR).
- **The `Q=-1` nuance (author §3.1 vs boundary row 15).** The boundary's own
  `Q=-1` leg is a **`bq_lowpass`** (`b2_clamp.json` `graphs/Q--1/args`:
  `label=bq_lowpass`) and measures the 0.707 default
  (−0.007/−3.01/−24.475/−47.317) — so the boundary's *measurement* is right for
  the label it used. The family's falsifying leg is **`bq_peaking`** `Q=-1`,
  which measures a flat broadband response. The falsification is therefore of
  the row's *generalization* to every label, not of the lowpass cell; the
  author's "boundary row 15 falsified" is correct in substance and should be
  read as label-scoped.
- **The scout's "no ports" claim.** The scout's `shape.json` records its
  no-props filter-chain capture node as `Stream/Input/Audio` with
  `"ports": []` (`autoconnect: true`); the family's host-safe arming shape
  yields `Stream/Input/Audio` with `input_MONO`+`monitor_MONO` and **no
  `playback_MONO`** (feed link rc 255). The author's §4.3 is a shape
  difference, and the scout's exact shape was left un-armed by policy — a
  documented gap, not a contradiction.

## 6. Findings

**F1 — `d_qneg` is measured on a saturated POST capture (substantive).**
The `bq_peaking(Freq=1000, Q=-1, Gain=20)` leg's POST capture hits the s16
rail: `out_max_abs = 1.000000`, **7688 / 134144 samples (5.73 %) at ±full
scale** — identical in the author's run A and in both verifier runs (7244 in
author run B), while the PRE tap is clean (max 0.1596, 0 clip). The recorded
flat ≈+19 dB is therefore a **saturation-compressed reading**: clipping cannot
*create* a flat response (a peaking response would still show its skirt at
200 Hz), so the falsification of the 0.707-default claim survives — but the
level is a lower bound and the arm's "flat within 2 dB" shape witness is
partly a saturation artifact. Recommended fold fix: attenuate this leg's
stimulus (or re-arm it on a lower-level probe) and keep the falsification arm.
*Independently converged:* the sibling critic (`r92-critic.md` §4.1) reached
the same clip-ceiling conclusion from the same captures with a different
method (`clip(10·x)` reproduces the recorded vector exactly; the unclipped
`3·x` reads exactly +9.542 dB = 20·log10(3), so the analyzer is honest below
the clip) and adds the mechanism hypothesis RBJ-peaking `q → 0⁺` ⇒ constant
`A² = +20 dB`, testable in one leg (`Q=+1e-6`).

**F2 — three arms can raise instead of failing (labrat, §8).**
`abs(None)` in the `d_copy`/`d_fhi` unity arms and `max(qn.values())` on an
empty dict in `d_qneg` raise uncaught `TypeError`/`ValueError` when a cell is
`None`/absent — a crash voids the entry rather than producing a named leg
failure. Not vacuity (the arms do compare), but a robustness hole.

**F3 — the tool-missing block exits rc 0.** Measured (M5): the entry names
`missing tools: ['wpexec']` in `coverage_blocked` but appends **no failure**,
so a run whose entry never started still exits 0. The named block is the only
witness; a reader keying on rc alone reads a blocked run as green. (The
daemon-down path *does* append a failure and exits 1.)

**F4 — documentation drifts in the landing's prose (all three seats agree on
the cells).** (a) `r92-integrate.md`'s worktree dispatch-block range cites
33877–33903; the byte-identical 28-line block is 33877–**33904** (the declared
sha `802f23d1…` is right). (b) The commit message and report headline say
**80** legs; the receipts carry **81** top-level keys (26+20+18+17; `i_residual`
is itself a key) — this seat's count and the scribe's are identical.
(c) `r92-author.md` §4.1's log-line numbers (1792/1836/15468) are the
**pre-fix** run's, not the green runs' (A 1324/1059/12497, B 364/329/6070), and
RECEIPTS.md's "both green runs are on this sha256" is a mtime+unchanged-file
binding, not a receipt-recorded one (scribe items 2–3).

**F5 — max-energy window ties.** The window rule searches in 2400-sample steps
and can tie within 0.03 % (measured: 7898.8 vs 7896.4 energy). In author run B
the `d_qneg` out-tap's chosen window sat next to the signal tail; a second
window placed +12 000 samples later read 6.15 dB low (rms 0.41 vs 0.57). No
armed cell moved (the armed window matched run A to 0.03 dB), but any future
re-analysis of the stored captures must place windows per tap and inside the
steady region.

**F6 — the family lock file remains after exit.** `corpus/live/measure_audio-filterchain-r92.lock`
persists in each tree with `pid=<run> prefix=r92a_<pid>` (inert text); the
`flock` is released at process exit — this seat probed both files with
`LOCK_EX|LOCK_NB`: **FREE**. The author's worktree lock (pid 223834, 06:42) is
likewise stale-but-free. File artifact, not node residue.

**F7 — disclosed self-contamination in run B.** Run B overlapped this seat's
own entry-level mutation controls, and the family recorded three foreign
`r92a` node sets (`r92a_1071382_d_gneg_*`, `r92a_1090418_d_50ms_*`,
`r92a_1098326_d_gneg_*` — M1/M2/M3) in its `foreign_r92a_nodes` field. No
armed cell was affected (node names are pid-unique; `foreign_r92a_nodes` is a
record, never an arm). At census time the only live `r92a` population on the
host belonged to a **concurrent sibling verifier lane** (`r92s`, pid 1175531,
running the same family from its own tree) — named here so it is not mistaken
for residue.

**F8 — two critic-named fail-open arms are closed in this seat's law set.**
The fixture's own `d_fhi` arm (`any(abs(v) > 0.05 …)` over a possibly empty
`gain_db`) and `a_ports_none`'s feed witness (`rc == 0 → fail`; absent passes)
are fail-open (`r92-critic.md` §5, verified there by mutation). The independent
law set closes both: forged receipts with `d_fhi.gain_db` deleted,
`a_ports_none.feed_link` deleted, and `a_ports_sink.feed_link` deleted each
produce exactly one FAIL (`d_fhi.passthrough`, `a_ports_none.feed_refused`,
`a_ports_sink.feed_ok`). A gate run through this seat's laws therefore cannot
read those absences as green, even though a bare fixture run would.

## 7. Exit census

- **Per entry-run (8/8):** `own_nodes_after == []`; `sinks_gone` all true;
  `live_after = {spdif_links: <recorded>, procs: []}`; the three mutation
  controls and the tool-missing control also ended with
  `own_nodes_after: []` (the tool-missing one never started).
- **Host, scoped to this seat's five pids** (`786172` run A, `1044067` run B,
  `1071382`/`1090418`/`1098326` mutation controls): `pw-dump`, `pw-cli ls
  Node`, `pactl` modules/sinks/sources and `ps` all yield **0** `r92a_<pid>`
  objects or processes. The only `r92a` objects on the host belong to the
  concurrent sibling lane (`r92a_1175532…`), which is live, not residue.
- **Defaults read unchanged** (`…HiFi__SPDIF__sink` / `…HiFi__Line__source`);
  no `set-default-*`, no `pw-metadata` write by this seat.
- Lock files: present, inert, flock FREE (§F6).

## 8. Labrat (the one permitted probe)

One read-only `labrat`, depth-2, bounded to the frozen landing block
(lines 39176–41470). Hypothesis: *at least one of the 81 leg keys has no
reachable failure path (a vacuous leg, the class the author already hit with
the str-vs-int `rbj: None` defect)*. **Verdict: CONTRADICTED** — 81/81 leg
keys enumerated in order, every leg carries at least one reachable
`_fc92_leg_fail` path, every arm reads only keys its leg records, `a_labels`
64/64 and `i_residual` 3/3 are armed, and the `v_*` legs' `{}` diagnostic
argument does not lose their arms. It also named the crash-class hole now
reported as **F2**. Zero side effects (read-only).

## 9. Remaining risks / what this gate does not prove

- The host was **not quiet** (4–12 foreign fixture runs; sibling lanes landing
  r96/r97/r98/r99/r100/r93 during the window). Determinism is established for
  the *recorded cells*, not for byte-identical captures — capture sizes and
  hashes vary run to run, exactly as the boundary established.
- F1: the `d_qneg` level is a saturated lower bound; the arm's flatness
  witness is clip-assisted. The falsification itself survives.
- The `d_gneg140` 200 Hz cell carries a ±0.23 dB spread across runs
  (floor-dominated); the arm's ±1.5 dB is generous by design and the decisive
  witness is the 20 dB separation from the unclamped value.
- The `Q=-1` *mechanism* remains unexplained beyond "not the default"; this
  gate adds the saturation finding to the record.
- The 20 kHz lowpass cell stays recorded-not-armed — the decision is right, but
  the author's stated reason ("float32 cancellation") is falsified by the
  sibling critic (`r92-critic.md` §4.2): the deviation is the **s16 capture
  floor** (the output's 20 kHz component is 0.35–0.40 LSB), and the ×32768
  capture scale reproduces the recorded −71.437 dB exactly. This seat's own
  evidence corroborates it: a float64 end-to-end re-derivation from the raw
  WAVs reproduces the recorded cell to 0.000 dB, so the 1.22 dB deviation from
  the analytic RBJ reference lives in the captured bytes, not in the
  analyzer's arithmetic. The family already carries an unused `fmt="f32"`
  capture path that would make this cell armable.
- This gate says nothing about other hosts, about the family's absent classes
  in the future, or about perceptual quality — it is a re-run/mutation gate on
  these committed bytes.

## 10. Evidence index

Root: `/home/vgpnk/r92-verifier/` (archive root named by the assignment).

| path | what |
| --- | --- |
| `tree-r92/`, `tree-head/` | the two frozen trees (landing `ccbce758`, HEAD `b8ff4efc`) |
| `r92-landing.tar.sha256`, `head.tar.sha256` | tar-stream shas |
| `runs/identity.txt`, `runs/census.txt` | block/fixture identity, file-set census |
| `tree-r92/corpus/live/runs/20261016T101236603490Z-filterchain-r92/measurements.json` | **run A receipt** (rc 0) |
| `tree-head/corpus/live/runs/20261016T101810912899Z-filterchain-r92/measurements.json` | **run B receipt** (rc 0) |
| `scratch/runA/`, `scratch/runB/` | every stimulus, IR fixture and captured WAV of both runs (96 files each) |
| `runs/r92v_laws.py`, `runs/verifierA.laws.json`, `runs/verifierB.laws.json`, `runs/authorA.laws.json`, `runs/authorB.laws.json`, `runs/authorPrefix.laws.json` | independent law set + per-receipt results |
| `runs/cross-run.txt`, `runs/boundary-cells.txt` | cross-run cell comparison; cross-seat cells |
| `runs/forged/`, `runs/forge.py`, `runs/forged-controls.txt` | forgery controls |
| `runs/mut-mutarm.json`, `runs/mut-mutir.json`, `runs/mut-mutnoop.json`, `runs/mut-mutnopwpx.json`, `runs/mutations.log` | mutation controls |
| `runs/pre-census.txt`, `runs/post-census.txt`, `runs/post-census-scoped.txt`, `runs/post-census-precise.txt` | host censuses |
| `runs/runA.stdout.json`, `runs/runB.stdout.json`, `runs/*.start` | run stdout + wall stamps |
| `corpus/live/r92-verifier/` (in-repo, untracked) | small-file mirror: both run receipts, the law set + results for five receipts, cross-run/cross-seat/census tables, mutation + forgery controls (900 KB; the trees and captures stay under `/home/vgpnk/r92-verifier/`) |

*verifier leaf — GATE PASS on committed bytes, 304/304 laws on two frozen
trees, 4/4 mutation controls, 12/13 forgeries caught (1 declared no-op), exit
census clean; the `d_qneg` saturation and the two critic-named fail-open arms
are named, not hidden.*
