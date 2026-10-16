# r84 scribe — evidence custody + claim audit

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r84). Scope: audit the committed r84 landing
`fbe65713` — `reports/round-84/r84-author.md`, the two committed receipts
`corpus/live/r84-author/runs/run{1,2}/measurements.json`, the fixture delta
`corpus/fixtures/measure_audio.py` (+2796/−3) — for claim→sha chains,
arithmetic reconciliation (147 legs / 6 entries / 2 green runs), file
existence, hash re-derivation and unreported evidence. **Read-only on
everything except this report and `corpus/live/r84-scribe/`; no commits, no
judgment passed** — every discrepancy below is handed to the canonical judge
as an adjudication item.

Entry state: HEAD `fbe65713b5adf1e76b3f6839968fc813a36d3fbf` (`r84 author:
147 legs / 6 entries`, 21:38:57 −0300). Every r84 claim was re-derived from a
**commit pin** (`git archive fbe65713` →
`~/Projects/shokunin/tmp/r84-scribe-work/tree`), not from the worktree.
Ambient at audit: loadavg ≈ 51–54 / 32 cores, and a **sibling wave-B seat was
executing the r84 fixture live** during the first minutes of the audit
(21:39–21:41Z: `TMPDIR/measure_audio-alsapw-r84.lock`, `TMPDIR/r84critic-*`,
`TMPDIR/r84a-props-i8ej74q8`, live `pw-dump` nodes `r84a_ns_1682245`,
`r84a_ns_1685102`, `r84c_env`); by 21:45Z those nodes were gone and only the
long-lived foreign `r84a_probe_548706` remained. No r84 claim below is
affected — all of it comes from the pin.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes, with one host-context contradiction and several count/citation defects.** Fixture chain re-derived byte-exact: pin `8ed09d19…` (22 725 lines) vs parent `7984409c…`, `+2796/−3` in 6 hunks, exactly 3 deleted lines (the r83 mutex-sum / mode / suffix wiring lines) — insertion-only otherwise. Both committed receipts are **byte-identical to their canonical run dirs** (`e8d463c2…`, `283f69e8…`) and there are **exactly two** canonical `*-alsapw-r84` dirs — both cited, both green (no r83-style uncited-execution defect). The report's `loadavg >100 throughout` is contradicted by its own receipts (51.27–59.16; **ADJ-1**). |
| 2 | Does the arithmetic reconcile? | **Yes for every headline cell.** 38+22+14+24+16+33 = **147 legs** × 2 runs, `failures []` in all 6 entries both runs, `coverage_blocked` 0 occurrences, `sinks_gone` all `true` and `own_nodes_after []` in the 4 sink-owning entries, 6 unloads `verified_index == captured`, `recycled false`, `exit_code 0`. Every gain law re-derives **exactly cubic** in both runs (0.125 = 0.5³, 3.375 = 1.5³, 0.015625 = 0.25³); sticky 30% → tap median **221** = ⌊8192·0.3³⌋ and leaf `db −31.37` = 20·log₁₀(0.3³). Two headline **counts** are wrong: capture-refusal class “×4” (actual 5 legs, **ADJ-2**) and negctl “22 named classes + 6 must-classify-nothing” (actual 23 expect-a-class / **18 distinct names** / 5 expect-null, **ADJ-3**). |
| 3 | Do the claimed files exist? | **Yes, except one path shorthand.** All receipt, canonical-dir, report and fixture paths exist; the toolchain strings (pipewire 1.6.8, wireplumber 0.5.17, pactl 17.0-98-gb096, alsa-utils 1.2.16, python 3.14.7, numpy 2.5.3) re-verify live. The cited `~/tmp/r84n.wav` does not exist — the artifact is `~/Projects/shokunin/tmp/r84n.wav` (**ADJ-8**). |
| 4 | Any unreported evidence? | **Yes — eight items.** (a) the `loadavg >100` contradiction (**ADJ-1**); (b) two falsified counts (**ADJ-2/3**); (c) the sticky note's “different-tag respawn 100% (measured)” has **no witness leg** in either receipt (**ADJ-4**); (d) `respawn_tap_med` and the `monA_*` amps are medians over **un-serialized** series — stats-only (**ADJ-5**); (e) receipts carry no fixture/git identity (**ADJ-6**); (f) a tracked `.pyc` is dirty in the worktree with the r84-compiled bytecode (**ADJ-7**); (g) five pre-session TMPDIR artifacts besides the disclosed `r84n.wav` (**ADJ-8**); (h) the ungated `mon_soidx` leaf snapshot that reads bogus 0% in run2 (**ADJ-11**). |
| 5 | Custody verdict | **INTACT-BUT-CITATION-DEFECTIVE (author landing) · INTACT (receipt/canonical chain) · HOST-ONLY (this seat's receipts, untracked).** No verdict-surface contradiction was found: every flagged item is a citation/count/host-context/provenance defect or an un-serialized statistic — **no falsified measurement, no red run, no residue**. Items ADJ-1…ADJ-12 need adjudication; ADJ-10/12 are nits/notes. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `fbe65713` (pin) | `8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e` | `git show fbe65713:… \| sha256sum` = `sha256sum` of the pinned archive file; 22 725 lines; equal to the worktree copy (fixture untouched after the commit) |
| `fbe65713^` (`c387749c`) | `7984409ceb9ca7c35b18b9b28f2add445701c044d71f8ee4ddc6f35d31217ef7` | equals `d6167399` = `cab9f08e` = `c387749c` — and equals the sha **r82-verifier2 itself cited** (“Fixture sha256 `7984409c…` before and after all 4 runs”), an independent cross-seat match |
| `a151a226` (r83) | `26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea` | equals the sha the **r83 scribe** re-derived — second cross-seat match |

Delta: `+2796/−3`, **6 hunks** — one 2758-line family block inserted at
`main():18818`, the 34-line dispatch block at `22032`, and 4 wiring hunks; the
diff contains **exactly 3 deleted lines** (`git diff | grep '^-'`): the r83
mutex-sum line, the `mode = …` ternary and the `suffix = …` ternary. Namespace
census on the pinned copy: `_alsapw_r84` ×330, `ALSAPW_R84_` ×89, `r84a_` ×25,
`probe-alsapw-r84` ×4, each of the six entry names ×1. `--probe-alsapw-r84`
is appended to `add_argument`, the mutex sum, `mode` and `suffix` — the r82/r83
convention, prior families untouched. Receipts (`commit-pin.txt`,
`fixture-chain.txt`).

### 1.2 Receipts — two copies, two canonical executions

| canonical dir (untracked) | wall (local) | sha256 | landed as |
| --- | --- | --- | --- |
| `20261016T003253840363Z-alsapw-r84` | 21:32:53 | `e8d463c26a97a6b590886fa5737b17a0b54cb0472380ff81a6bb19f33f860d4b` | `runs/run1/measurements.json` |
| `20261016T003756373122Z-alsapw-r84` | 21:37:56 | `283f69e8d82a29646957c5d89c37a10fa337b9263e8f2f21aeaec8e6c0cb0786` | `runs/run2/measurements.json` |

Both seat copies are the canonical files verbatim (`sha256` equal, no
normalization). Commit at 21:38:57 sits after both runs. **Exactly two**
`*-alsapw-r84` dirs exist under `corpus/live/runs/` — no uncited execution
(this is the r83 ADJ-1 defect class, absent here). The receipts carry **no**
embedded fixture sha / git HEAD, so the “two runs on identical bytes” link
rests on the unchanged worktree plus the run/commit timeline (**ADJ-6**).

### 1.3 Cross-seat corroboration found while auditing

- **Foreign sink attribution**: `r84a_probe_548706` (node 77, SUSPENDED) is
  documented as a *foreign sibling* already in `reports/round-82/r82-verifier2.md`
  (lines 69/116/146) at ~22:44Z Oct 15 — ~2 h **before** the r84 runs. The
  author's “NOT this family's / left running as found” disclosure is
  independently corroborated, and the live `pw-dump` at 21:45Z shows exactly
  that node and no other r84a-tagged survivor.
- **Boundary evidence**: `reports/round-84/r84-boundary.md` — its §0 verdict
  board rows 8 and 13, and its §5 “confirmed under load” board, already hold
  the same cubic laws **under hog** (loadavg 100–104, 3/3 each) and the sticky
  tap 221 — the author's ambient-load measurements and the boundary's loaded
  measurements agree.
- **Shared restore key**: the author's private `r84arole<pid>` key is a real
  avoidance of the boundary's contamination (`sink-input-by-media-role:music`,
  boundary §4 line 109 / §7 line 198) — the receipts' `role_reset` blocks show
  `reset_ok true`, `post_percent 100`, `post_mute false` at every entry head.

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells

- **6 entries / 147 legs**: `alsapw_dev_lattice_r84_probe` 38,
  `alsapw_pw_args_r84_probe` 22, `alsapw_pulseprop_r84_probe` 14,
  `alsapw_pactl_write_r84_probe` 24, `alsapw_monstream_r84_probe` 16,
  `alsapw_negctl_r84_probe` 33 — verified key-by-key in both receipts.
  Nit: the dev_lattice 38 includes one **non-leg scalar** (`hold_exit` = 1), so
  the family is 146 leg dicts + 1 int (**ADJ-10**).
- **2 green runs**: `failures []` on all 6 entries × 2 runs; `coverage_blocked`
  **0 occurrences** anywhere (the key is only written on a blocked/failed
  reader — same convention as r83); `sinks_gone` `{…: true}` on the 4
  sink-owning entries; `own_nodes_after []` on the same 4; `unloads`
  `verified_index == captured`, `recycled false`, `exit_code 0`, `stderr_tail
  null`. The two entries without those keys (dev_lattice, negctl) load no sink
  — the report's “every entry” is loose (**ADJ-9**).
- **Adaptive arms are receipted as such**: the `-D` lattice legs carry an
  explicit `arm` (`quiet_ok` / `direct_ok` / `free_ok`) plus a `pcm_state_before`
  witness (`closed`), and the eBUSY trio records its decision in
  `held_pcm`/`pcm_states_at_hold` (`card0/pcm1c: state: RUNNING` via the seat's
  own pin), `pcm_state_at_probe` and `free_pcm` — matching the report's
  “adaptive by design” wording.

### 2.2 Headline gain laws — exact, both runs (`gain-laws.txt`)

| leg (×2 runs) | write | base → post | recomputed | stored `ratio` | cubic law |
| --- | --- | --- | --- | --- | --- |
| `vol_50_0`, `vol_50_1` | `set-sink-volume <ns> 50%` | 8192 → 1024 | 0.125 | 0.125 | 0.5³ = **0.125** ✓ |
| `vol_150` | `set-sink-volume <ns> 150%` | 8192 → 27648 | 3.375 | 3.375 | 1.5³ = **3.375** ✓ |
| `vol_25_idx` | `set-sink-volume <idx> 25%` | 8192 → 128 | 0.015625 | 0.0156 (4-dp rounding) | 0.25³ = **0.015625** ✓ |
| `src_vol50_0/1` | `set-source-volume <ns>.monitor 50%` | 8192 → 1024 | 0.125 | 0.125 | 0.5³ ✓ |
| `monA_sivol_0/1` | `set-sink-input-volume <idx> 50%` (mid-run) | 8192 → 1024 | 0.125 | 0.125 | 0.5³ ✓ |
| `vol_0_100`, `mute_cycle` | `0%`/mute then `100%`/unmute | 8192 → **0** → 8192 | — | — | 0³ / 1³ ✓ |
| `susp_live_0/1` | `suspend-sink` 0/1 | 8192 → 8192 | 1.0 | — | unchanged ✓ |
| `monA_nowrite` | (no write control) | 8192 → 8192 | 1.0 | — | unchanged ✓ |

The tap legs serialize their full 0.1 s `series` (71–72 windows), so each
ratio above is re-derivable **from the committed bytes alone**; the mute/vol0
histograms are 21 zero-windows + 8191/8192 elsewhere. Envelope constants in the
pinned fixture (`ALSAPW_R84_VOL_ENV`): `x0.125 (0.105,0.150)`,
`x3.375 (3.00,3.80)`, `x0.015625 (0.010,0.024)` — i.e. the gates are
−16/+20 %, −11/+13 % and −36/+54 % around exact cubic, while both runs measure
the exact value (observation for the critic/reviewer; not a custody defect).

### 2.3 Sticky restore (30% → 221) and index refusals

- `sticky`: `spawn1_percent 100` → `write30 rc 0` → `respawn_percent 30` with
  the respawn leaf `value 19660 / "30%" / −31.37 dB` (`20·log₁₀(0.3³) =
  −31.373` ✓, i.e. **linear percent, cubic gain**) → `respawn_tap_med 221.0`
  (`8192·0.3³ = 221.184 → 221` ✓) → `repair rc 0` → `repaired_percent 100`,
  `repaired_mute false`. The stored `respawn_tap_series_tail` (last 6 windows:
  `[2.1,221]` then 8191/8192) is consistent with a ~2.2 s repair inside the
  `[0.8,3.2]` median window; the median itself is **stats-only** (**ADJ-5**).
- `mon_soidx`: `parec_exit_code 0`, `out.bytes 44`, `riff true`, `data_actual 0`
  (`unsupported: no s16 stereo data chunk`); `mon_bad0` / `mon_deadidx`:
  `parec_exit_code 1`, `parec_stderr "Stream error: No such entity\n"`,
  `out.bytes 44`, `parec_alive_at_dur false` — the three index-refusal cells
  reproduce verbatim in both runs.
- `monA_*` classifier census re-derived: `sink_monitor` **A+B ×21** (mix
  control); `monA_0/1/nod/bogusd/othersink` **A ×21**; `monA_move` **A ×23** —
  i.e. `-d` absent/bogus/foreign and `--monitor-stream`-only pins all carry the
  A-only signature in both runs.
- `pw_args`: `PERIOD_BYTES=4096` → node prop `alsa.period-bytes 4096` and
  `node.latency 1024/48000` (4096 B ÷ (2 ch × 2 B) = 1024 frames ✓);
  `RATE=44100` → `alsa.rate 44100`, `node.latency 5512/44100` and the verbatim
  `Warning: rate is not accurate (requested = 48000Hz, got = 44100Hz)`;
  `CHANNELS=6` → `alsa_params`; `SERVER=no_such` → `alsa_pw_conn` “Host is
  down”; `NODE=no_such`/`.monitor` playback → silent fallback to the default
  sink (consumer = the USB sink) — all identical in both runs.
- `pulseprop` node-view vs proplist-view (`pulseprop-node-vs-proplist.txt`):
  `Communication` on the node vs `phone` + `sink-input-by-media-role:phone` in
  the proplist (×2); `Music` → `music`; `notarole` raw; `zzz.invented` **int
  42 on the node vs string "42" in the proplist** (×3 incl. the parec leg);
  `application.process.binary pacat`; `module-stream-restore.id` landing on the
  node.

### 2.4 negctl unit table (the “22 / 6” claim)

Pinned fixture `cases` table (`measure_audio.py:21417-21507`): **23** positive
cases mapping onto **18 distinct** class names, and **5** expect-`null` cases
(`u_empty`, `u_noise`, `u_segv_words`, `u_ratewarn`, `u_recording`); all 23
`got == expect` in both runs. Live observation covers **17** distinct classes
(identical in both runs; only `alsa_open_enodev` never occurs live, which is
expected for a unit-table class). The r84-local class table
`_ALSAPW_R84_ERR_CLASSES` has **18** entries. The report's “22 named classes +
6 must-classify-nothing” matches none of these counts (**ADJ-3**; the frozen
labrat independently falsified the same two counts). The capture-refusal claim
is otherwise clean: the unit table proves both stderr slices
(`Unable to install hw params` / `TICK_TIME: [0 0]`) map to the **one** class,
and the live bare/default/`NODE=` capture legs all carry
`alsa_pw_capture_refusal` — **5** legs, not 4 (**ADJ-2**).

---

## 3. Independent re-derivations (this seat + one frozen-probeParent labrat)

**Gain laws (both runs).** Recomputed every `post_amp/base_amp` and compared
with the stored `ratio` and with `pct³`; all match to the stored 4-dp rounding
(`gain-laws.txt`). The cubic model is additionally confirmed at the leaf level
by `db −31.37` = `20·log₁₀(0.3³)` and by `value 19660` = `0.3·65536`.

**Run-to-run stability (`run-diff.txt`).** 6740 of 7951 leaf paths are
identical between the two receipts; after normalizing TMPDIR random suffixes,
pids and object indices only **373** differ, and the residue is
identity/timing/snapshot noise. The semantic residue is small and
verdict-neutral: capture-amplitude jitter (`out/peak` 660–662, 32552–32648),
burst phase/count (`out/first_starts[]`, `bursts` 13↔14), one classifier
window (`monA_move/sig/windows[8]/a` 5547 vs 8189 — same class `A`),
`pulseprop` node `state` `running`↔`suspended` on 3 legs, and the two items in
ADJ-11/ADJ-12.

**Classifier tables.** Re-derived the sig-class census and the negctl
`expect/got` table from the committed bytes (no live run needed).

**Path existence (`path-existence.txt`).** Every backticked repo/absolute path
in the report resolves; the only miss is `~/tmp/r84n.wav` (**ADJ-8**).

**Live, read-only (no PipeWire object created).** `pipewire --version` 1.6.8,
`wireplumber` 0.5.17, `pactl` 17.0-98-gb096, `aplay/arecord` 1.2.16, python
3.14.7, numpy 2.5.3 — all match the report's host block; `pw-dump` at 21:45Z
shows only the foreign `r84a_probe_548706` from the r84a namespace. Live
replays of the laws were deliberately left to the verifier/critic seats (a
sibling wave-B seat was already running the fixture while this audit ran).

**Frozen-probeParent labrat (one read-only dispatch, advisory).** Independent
census of the same two receipts (`labrat-r84-headline-advisory.txt`): all
headline numerics verified; **falsified** the “×4” capture-refusal count and
the “22 + 6” negctl decomposition; noted that dev_lattice's 38 keys include the
`hold_exit` scalar and that “post-gain” is a semantic reading of the x0.125
ratio rather than something the receipts can prove on their own.

---

## 4. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | moderate | `r84-author.md` §Host says “loadavg >100 throughout”; the receipts' own per-entry `loadavg` are **51.27–59.16** (36 samples, both runs, none >100), and the audit-time host loadavg was 51–54. The receipt field is the raw `/proc/loadavg` first-three read (`_alsapw_r84_loadavg`, `measure_audio.py:19036-19040`) — no scaling is applied, so the contradiction is direct. No verdict cell depends on it (the laws are exact at ambient ~51–59, and the boundary re-measured them under 100–104). | both receipts' `loadavg`; `/proc/loadavg` at audit; pinned helper |
| ADJ-2 | author | minor | Entries table: “single capture-refusal class ×4”; **5** legs carry `alsa_pw_capture_refusal` (`r_pw_bare_0/1`, `r_pw_default`, `r_pw_node_miss`, `r_pw_node_mon`). Independently falsified by the labrat. | `cleanup-and-unreported.txt`; labrat advisory |
| ADJ-3 | author | minor | negctl “22 named classes + 6 must-classify-nothing”: actual **23** expect-a-class / **18** distinct names / **5** expect-null; the live family shows **17** distinct classes. | pinned fixture `cases` table; labrat advisory |
| ADJ-4 | author | custody | Sticky note asserts “measured: … different-tag respawn 100%”, but **no leg in either committed receipt witnesses a different-tag respawn** (the string's only occurrence is inside the note). The encoded same-tag arm is fully receipted. | `grep different-tag` on both receipts |
| ADJ-5 | author | custody | Stats-only values: `respawn_tap_med 221.0` is a median over `[0.8,3.2]` of an **un-serialized** tap series (only the last 6 windows stored), and `monA_*` `base_amp`/`post_amp` are medians over parec wavs under TMPDIR (removed). Contrast: the `pactl_write` tap legs **do** serialize `series`, so those ratios are fully re-derivable. | receipt fields + `measure_audio.py:21258-21263, 21387` |
| ADJ-6 | author | custody | The receipts carry no fixture sha / git HEAD, so “two green runs on identical bytes” is not receipted provenance; it rests on the unchanged worktree (pin sha = worktree sha) and the run/commit timeline. | `commit-pin.txt` |
| ADJ-7 | lane | custody | Tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is **dirty in the worktree** (1 256 889 B, sha `21b39e3c…`, header `source_mtime/size` = the committed fixture, i.e. r84-compiled bytecode; HEAD blob `6e271a2d…` unchanged since `d6167399`). Not disclosed in the report; attribution is ambiguous (mtime 21:26:35 precedes run1, and a script run does not rewrite a `.pyc` — only an import does). This seat wrote no tracked file. | `commit-pin.txt`; pyc header parse |
| ADJ-8 | author | nit | Cited `~/tmp/r84n.wav` does not exist — the file is `~/Projects/shokunin/tmp/r84n.wav`; and the lane TMPDIR also holds pre-session `cap1.err`, `cap2.err`, `cap3.err`, `cap3.wav`, `t` (20:28) that the report does not mention. | `path-existence.txt`; TMPDIR listing |
| ADJ-9 | author | nit | Prose shape nits: “`failures: {}`” (actual `failures: []`), “`coverage_blocked: null`” (key absent, 0 occurrences), “`sinks_gone` … every entry” (4 of 6 entries carry the key; the other two load no sink). | receipts |
| ADJ-10 | author | nit | dev_lattice “38 legs” includes one non-leg scalar (`hold_exit` = 1) → the family is 146 leg dicts + 1 int over 147 counted cells. | receipts; labrat advisory |
| ADJ-11 | author | note | `mon_soidx`'s stored `source_output` snapshot is **ungated**: run1 `source 225164` (attached, 100%), run2 `source 4294967295` + volume 0% — exactly the pre-routing bogus-0% artifact the author's refinement #2 warns about. Not verdict-bearing (the cell is the parec rc0 + 44-byte output), but it is an ungated read inside the evidence. | `run-diff.txt`; receipts |
| ADJ-12 | lane | note | Host pre-state differed between the runs: run1's `pcm_states_pre.card0.pcm3p` = `state: RUNNING` (foreign holder) vs `closed` in run2 — the ebusy arms are adaptive by design, but the differing pre-state is undisclosed. | `run-diff.txt` |

---

## 5. Write-scope / custody notes

- Committed in `fbe65713`: fixture (+2796/−3), the two receipts (11 612 +
  11 602 lines), the author report (107 lines) — 4 files, 26 117 insertions,
  3 deletions.
- Author evidence: 2 tracked receipt files; the two canonical run dirs are
  **untracked** (host-only), exactly as in r83 — but here the seat copies are
  byte-identical to them, so no re-run is needed for any landed number.
- Canonical run dirs are the only executions of the r84 family on disk (2);
  both cited, both green.
- This seat wrote only `reports/round-84/r84-scribe.md` and
  `corpus/live/r84-scribe/` (9 receipts + `manifest.json`, 121 366 B; the
  manifest lists each receipt's bytes+sha256). **No tracked file was modified**
  (the tracked `.pyc` dirt in ADJ-7 pre-existed and its sha is unchanged since
  the audit opened), no commit, no push, no PipeWire object created, no
  `set-default-*`, no unload. All scratch work lived in
  `~/Projects/shokunin/tmp/r84-scribe-work` and every python invocation ran
  with `PYTHONDONTWRITEBYTECODE=1`.

---

## 6. Remaining risks / blockers

1. ADJ-1 is a host-context claim contradicted by the landing's own receipts;
   the adjudicator should decide whether the report text is corrected (the
   measurements themselves stand, and the boundary already carries the
   loaded-host version).
2. ADJ-2/3 are count defects in the report prose; no verdict cell changes
   (the underlying legs and classes are all receipted and green).
3. ADJ-4/5/6 are preservation gaps: a claimed different-tag arm and two median
   statistics cannot be re-derived from the current corpus; any future
   re-derivation needs a fresh execution, not the committed bytes.
4. ADJ-7 is the only tracked-file custody item and is ambiguous in
   attribution; it is an operator item (the tracked `.pyc`'s committed blob
   has been stale relative to the fixture at every revision since `d6167399`,
   and the worktree copy now carries r84 bytecode). No shipping decision is
   made or implied here.
5. ADJ-8…ADJ-12 are wording/path/inventory notes that do not affect any
   verdict cell.
6. No blockers for the round. The landing is a clean, green, two-run,
   insertion-only landing with byte-faithful receipts, exact cubic gain laws,
   and a corroborated foreign-state disclosure; the defects are citation-level.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
