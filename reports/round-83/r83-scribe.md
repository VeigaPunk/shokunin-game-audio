# r83 scribe — evidence custody + claim audit

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r83). Scope: audit the r83 dossier —
`reports/round-83/r83-{author,boundary,scout}.md` plus the
`corpus/live/r83-{author,boundary,scout}/` evidence trees and the boundary
`manifest.json` — for claim→sha chains, arithmetic reconciliation (128 legs /
7 entries / 2 green runs), file existence, hash re-derivation and unreported
evidence. **Read-only on everything except this report and
`corpus/live/r83-scribe/`; no commits, no judgment passed** — every
discrepancy below is handed to the canonical judge as an adjudication item.

Entry state: HEAD `a151a226b84374482d5df14c87baef80511aa94e` (`r83 author:
128 legs / 7 entries`, 19:09:36 −0300). All r83 claims were re-derived from a
**commit-pin** (`git archive a151a226` → `/tmp/r83-scribe-work/tree`), not from
the worktree: HEAD moved to `bc3f55ca` (r100 boundary, 22:11Z) and the tracked
fixture was being rewritten by the r82-fold seat during the audit (worktree
sha `7cf9b00d…` → `1e67a024…` vs pinned `26431adf…`). Ambient load during the
audit: loadavg ≈ 69 / 32 cores, with a sibling wave-B seat executing
`--probe-pwcat-r83` live (its `/tmp/r83a-lat-*` taps appeared at 22:12–22:13Z).

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes, with one citation defect and two prose-only gaps.** Fixture chain re-derived byte-exact (`26431adf…` at the pin = blob; parent `eb865760…`; +2426/−3, 6 hunks, insertion-only family). Boundary chain is **fully clean**: all 22 receipt sha16 prefixes re-derived and equal to the manifest, all 444 manifest entries byte-verified, all 133 run dirs / 347 run files covered, raw wavs byte-identical across quiet+load reps. Author: both landed copies are byte-faithful to two distinct **green** canonical executions, but the cited stamp for `run1` (21:50:17Z) is not the copied bytes (22:01:05Z) and two executions are uncited (**ADJ-1**). Scout: receipts present and 5/5, but the headline `amp@1k=12882` is a degenerate one-sample read (**ADJ-4**) and its mean/zero-cadence figures are not in the receipt (**ADJ-5**). |
| 2 | Does the arithmetic reconcile? | **Yes for every headline cell.** 29+19+26+13+18+15+8 = **128 legs** × 2 green runs = **256 leg-executions**, 7 entries, `failures []` on all 14 entry-runs, `sinks_gone` all true, `own_nodes_after []` on every entry, 0 `coverage_blocked`, 4 sinks unloaded name-verified. On-disk executions are **4** (126+128+128+128 = 510 legs) — "2 runs" is a green-run count (**ADJ-1**). Author's "+ ~2,240 lines" vs actual **+2426/−3** (**ADJ-2**). Boundary leg/run-dir counts reconcile 1:1 per stage (39/7/16/18/38/12/1/8 receipts ↔ same dirs) modulo naming/coverage nits (**ADJ-10**). |
| 3 | Do the claimed files exist? | **Yes.** Every report-cited receipt, log, harness, raw wav and report is present at the claimed path; the boundary manifest's 444 entries all match disk (bytes+sha256); the scout tree holds 21 files (504 795 B apparent / 540 KiB du) including both retained `PK44_*.wav`; the author's two committed receipts match the canonical run dirs byte-for-byte. |
| 4 | Any unreported evidence? | **Yes — three.** (a) two uncited author executions: `20261015T212812356289Z` (126 legs, 13 failures, red) and `20261015T215017582814Z` (128 legs, 17 failures, red) (**ADJ-1**); (b) the author's canonical `corpus/live/runs/*-pwcat-r83/` receipts are **untracked** — only the two seat copies are in the commit (**ADJ-3**); (c) an accidental author dev tap `/tmp/r83a_dev/r_s4_peaks.wav` (20:30Z) that independently reproduces the peaks class. No unreported boundary or scout measurement was found; the boundary's load reps are **byte-identical** to the quiet rep, which is stronger than its own "byte-identical stats" wording. |
| 5 | Custody verdict | **INTACT (boundary) · INTACT-BUT-CITATION-DEFECTIVE (author) · HOST-ONLY (scout).** No verdict-surface contradiction was found between any report and its receipts: every flagged item is a citation/count/coverage defect or a degenerate-window artifact, not a falsified measurement. Items ADJ-1…ADJ-11 need adjudication; ADJ-12/13 are notes. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | claimed in | re-derivation |
| --- | --- | --- |
| `26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea` | not stated in r83-author.md (only "+ ~2,240 lines") | `sha256sum` of the pinned archive file = `git show a151a226:… \| sha256sum` = match; 19 811 lines; `compile()` clean (no `.pyc` written) |
| `eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4` | parent commit `b5d0f673` | match; 17 388 lines; delta = **+2426/−3 in 6 hunks** (one 2389-line family block inserted at 16314, five `main()` wiring sites); the 3 deleted lines are exactly the mutex-sum / mode / suffix lines (**ADJ-2**) |
| insertion-only / namespaced | r83-author.md §Invariants | confirmed: no deletions inside the family; tokens `_pwcat_r83` ×220, `PWCAT_R83_` ×179, `r83a_` ×17, `probe-pwcat-r83` ×3; boundary folds present in the committed bytes — `peaks_abs_octave_artifact` ×3, `props_syntax_error` ×6, `pwcat_props_syntax_error` ×4, `failopen_foreign_sink`, `4294967056` ×4, `full_wave`, `silent_or_thin` |

### 1.2 Author receipts — four canonical executions, two copies

| canonical dir (untracked) | pid | legs | failures | sha256 | landed as |
| --- | --- | --- | --- | --- | --- |
| `20261015T212812356289Z-pwcat-r83` | 1271909 | **126** (matrix 11) | **13** (props 5, matrix 3, resample 5) | `ec9c4b0450bd3147…` | — |
| `20261015T215017582814Z-pwcat-r83` | 1799801 | 128 | **17** (matrix 16, failopen 1) | `9a1114b0cdb3ffdc…` | — |
| `20261015T220105801638Z-pwcat-r83` | 2305712 | 128 | 0 | `4e56f4b023585ceb…` | `measurements-run1.json` |
| `20261015T220645473277Z-pwcat-r83` | 2535010 | 128 | 0 | `4ce6812fe563799c…` | `measurements-run2.json` |

`reports/round-83/r83-author.md` cites "`measurements-run1.json` (21:50:17Z),
`measurements-run2.json` (22:06:45Z)" and "two green runs, zero failures".
The **bytes** are faithful (`run1` = the 22:01:05Z green run; `run2` = the
22:06:45Z green run; both are the canonical files verbatim), but the **stamp**
for run1 points at the red 21:50:17Z execution, and neither red execution is
listed anywhere in the report or a receipts index (**ADJ-1**). The receipts
carry no embedded timestamp — run identity is the pid only (`2305712` /
`2535010`), so the mismatch is detectable only against the untracked canonical
dirs.

### 1.3 Boundary chains — clean end-to-end

- `manifest.json`: `file_count` 444 = `len(files)`; `total_bytes` 36 588 709 =
  Σ bytes; all 444 entries match disk on bytes **and** sha256; on-disk 446 =
  444 + `manifest.json` + one tracked `__pycache__` `.pyc`. Breakdown: 66 raw +
  22 receipts + 347 run-dir files + 5 scratch + 4 harness scripts.
- Report §10: **all 22** receipt sha16 prefixes re-derived exactly
  (`cf24f60d…`, `1615ff56…`, `93a4dc74…`, `4cd200a4…`, `1410c11d…`,
  `2fe6341a…`, `c8871a6c…`, `11ea7fd0…`, `213089a6…`, `ce8c08b6…`,
  `723fa87f…`, `5f790cea…`, `b4b4c32a…`, `9c4a47f5…`, `82940a48…`,
  `a3281685…`, `070671d5…`, `417dd9db…`, `74856f10…`, `52da1064…`,
  `1c8e6a93…`, `be4faa2b…`) and each equals the manifest's sha256.
- Raw byte identity (stronger than reported): `S4_peaks_mon.wav` =
  `S4_peaks_ld1_mon.wav` = `S4_peaks_ld2_mon.wav` = `2fe8505786479c51…`;
  `S1_disable_mon.wav` = `S1_disable_ld1/ld2_mon.wav` = `ec3650bd450cebe9…`.
- Timeline: `setup.start 16:36:02` → `teardown 16:52:43` local; manifest
  `generated 2026-10-15T16:52:53-0300`; report window "~16:34–16:53 UTC−3" ✓
  (2-min slack at the open); HEAD `2333fac` per `setup.json.git` ✓; commit
  `58e45e9c` 16:53:46. Zone labels are honest — no repeat of r82's ADJ-9.
- Cleanup: `teardown.json` shows the r83b objects still present, `teardown2.json`
  shows `leftover_{modules,sinks,sources} []`, defaults unchanged, 5/5 unloads
  `rc=0 verified` ✓.

### 1.4 Scout chains — host-only custody

- `corpus/live/r83-scout/`: **0 tracked files** (21 files, 504 795 B apparent,
  `du` 540 KiB ✓ as reported), including `raw/PK44_1.wav` = `raw/PK44_2.wav`
  (sha256 `2ba24ad428a4bdca…`, byte-identical, 96 044 B / 24 000 frames each)
  and the 5 consolidated receipts + 6 scratch witnesses; `runs/` is empty.
- Report §10 cites exactly those files — all present. The report states
  "sha256 of any row available from the receipts JSON", but the receipts store
  **no** mean/min/zero statistics for the peaks legs (**ADJ-5**), and the
  "6/6" segv reps are not in the consolidated receipt (**ADJ-6**).

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells

- **7 entries / 128 legs**: `pwcat_props_parse 29`, `empty_props_segv 19`,
  `latency_props 26`, `channel_matrix 13`, `remix_props 18`,
  `resample_props 15`, `failopen_args 8` — verified leg-by-leg in both green
  receipts (dict lengths), 128/128.
- **2 green runs / 256 executions**: both `failures []` per entry, `mode =
  probe-pwcat-r83`, `sinks_gone` all true (4 distinct sinks
  `r83a_ns_a/ns_b/ns_m/ns44` per pid), `own_nodes_after []`, `unloads`
  `verified_index == captured`, `exit_code 0`, `recycled false`,
  `generic_capture_props_nodes_after []`, `coverage_blocked` 0 occurrences.
- On-disk total is 510 legs over 4 executions; the uncited pair is red
  (13 / 17 failures) (**ADJ-1**).

### 2.2 Author law→witness spot checks (both green receipts)

`rc=255` props_syntax_error ×8 (`err_0_0…err_3_1`, `Mismatched bracket` /
`Expected object value`) and `pw-cat`/`pw-record` `rc=1` ×5
(`pc_err_0/1/noval`, `pr_err_0/1`) ✓ law 2. `rc=-11` segv ×18 with live
`ctl_lb` `rc=-9` ✓ law 3. `-l 5` 240/48000, `-l 2.5` 96/48000, `-l 10000`
480000/48000, `-d 0.25` 4000/48000, `-d 1.0` 16000/48000, `-l 0/abc`/`-d
0/-1/abc` absent, `-l -5` **4294967056/48000**, `-l/-d` both orders 240/48000
✓ law 4. `m_alone` arms `['stable_mono','unmeasured','stable_mono']` (run1) /
`['stable_mono']×3` (run2) ✓ law 6. `n_empty` `failopen_foreign_sink` both
runs, serials 201022/201033 (run1) ✓ law 9.

Two citations are traceable to **run2 only** and are not labelled as such:
law 5's "ctl median 0.105 s, deltas [1.043, 1.000, 0.999], `-d 0.25`
[0.398, 0.355], `-l 1000` [0.106, 0.105]" is run2's `onset_summary`
(run1 gives 0.100 / [1.043, 1.000, 0.993] / [0.392, 0.352] / [0.135, 0.097]).
Law 8's numbers are run1's `s4_peaks_0.tap_stats` (`zero_frac 0.1462`,
`mean 4452.65`, `amp_at_997 0.1`, `amp_at_1994 3177.9`, `amp_at_3000 3178.6`,
`neg_frac 0.0`, `artifact_outcome full_wave_abs_octave`).

### 2.3 Boundary inventory

Receipt legs ↔ run dirs reconcile per stage (39/7/16/18/38/12/1/8). Nits:
the 8 `s5-scale` legs are stored as `ctrl/d0.25/…` but their dirs are
`scale_*`; 4 `s6x-pins` legs and 2 `s9x-move` legs have **no** per-leg run dir;
105 of 133 dirs carry all three of `cmd.txt/meta.json/stderr.txt` (**ADJ-10**).
§7 lists **7** numbered unstated modes while the §0 headline says "6" (**ADJ-8**).

### 2.4 Scout census

`p1-args` 36 legs + 5 content legs, `p3-midi` 8, `p4-remix` 19,
`p5-resample` 7 + 3 loopback legs, `p2-filter` 0 legs (tool-output evidence).
§1 says "38 legs" (receipt holds 41) and §0/§1 say `-i ''/-o ''` segv "6/6"
while the consolidated receipt holds **one** `S7_empty` leg (`rc=-11`) —
the boundary's receipted 8/8 quiet + 3/3 loaded is the substantiated version
(**ADJ-6**).

---

## 3. Independent empirical probes (scribe seat + one frozen-probeParent labrat)

**Peaks artifact (`resample.peaks` + 44.1k→48k).** Re-derived from retained
bytes: PK44_1/2 tone region (frames 2048–23999) exact-zero fraction **0.0833**
(1/12), gap histogram **12×1233 / 13×549**, run histogram 1×1737 / 2×46,
`min 0`, `neg_frac 0.0`, mean **+4383.29/+4382.43**, Hann-2|X|/N ch1 @3000 Hz
**1592.9**; boundary taps agree (0.0833, 12×5356 / 13×2380, DC-dominant,
ch1 @3000 = 1586) and the author's receipt agrees in its own 4|X|/N convention
(octave ≈3178 both channels). So the boundary's full-wave `|x|` + octave class
is **independently reproduced by two seats' bytes**; the scout's half-wave
class is falsified.

**The scout's `amp@1k=12882`.** Not reproducible from the retained bytes with
the retained code: the scout's own `fft_at` (`r83_probe.py:391-406`,
`setpos(min(n-1, int(0.5·rate)))` on a 24 000-frame file) reads **one** frame;
on the retained copy it returns **2788.0** (ch0@1k) / **4156.0** (ch1@1.5k).
The receipt's `amp_detail` 12882.0/3474.0 is exactly `2·|x|` for
`a[2143] = [6441, 1737]` — a one-sample Goertzel, and the "baseline 11450.0" is
the same artifact (`2·5725`). The same receipt's proper-window Goertzel gives
**2.0 / 14.1** and `dom` = DC (**ADJ-4**). The frozen-probeParent labrat
(one read-only dispatch; no exec tool in that seat, so static-only) reached the
same conclusion from the source and flagged that the scout receipt stores no
mean/min/zero fields.

**The 8.3% vs 14.6% zero-fraction divergence.** Reconciled: the author's
`_pwcat_r83_channel_stats` skips 0.3 s and then measures to EOF, so its settled
window still contains the pre-tone head — an accidentally retained author dev
tap (`/tmp/r83a_dev/r_s4_peaks.wav`) reproduces both numbers (tone-region
0.0833, settled 0.1628). The divergence is window content, not a different
artifact; the author's landed tap bytes are not retained, so its exact 0.1462
remains stats-only (**ADJ-3**).

**Boundary C3/C4 ("author cell wrong").** Re-derived: `C4` (`-c 1 -m`) is
stable 4095.6/4095.6 within the tone region; `C3` (`-m` alone) is time-varying
(Goertzel 4095.6/4095.6 in the first tone-second → 2190.1/4095.6 in the next),
confirming the correction. The report's exact windowed figures (1551.9/2046.9)
have no stored window spec — my tone-anchored 0.5–1.5 s window gives
1267.1/2046.6 (**ADJ-9**).

---

## 4. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | moderate | Receipt-stamp ↔ bytes mismatch plus two uncited executions. Report cites `run1 (21:50:17Z)`; the copied bytes are the 22:01:05Z run (`4e56f4b0…`, pid 2305712), while the 21:50:17Z dir (`9a1114b0…`, pid 1799801) is a **red** 128-leg run (17 failures) and the 21:28:12Z dir is a red 126-leg run (13 failures). No count in the report changes; the two landed receipts are green and byte-faithful. | canonical dirs + sha/pid mapping; `author-run-census.txt` |
| ADJ-2 | author | minor | "+ ~2,240 lines" vs numstat **+2426/−3** (−186, 7.7% understated). | `git show --numstat a151a226` |
| ADJ-3 | author | custody | Canonical `corpus/live/runs/*-pwcat-r83/` receipts are untracked (4 dirs, host-only); the seat copies are the only committed bytes. The resample tap wavs are not retained, so `zero_frac 0.1462` and the onset transports are stats-only. | `git ls-files`, tap paths under `/tmp` (gone) |
| ADJ-4 | scout | moderate | "fundamental still verifies (amp@1k=12882 > baseline 11450)" is a degenerate one-sample Goertzel (`2·|x|`, frame 2143); retained bytes + retained code give 2788.0/4156.0, and the same receipt's proper-window Goertzel gives 2.0/14.1 with DC-dominant `dom`. The falsification stands; the number's provenance should be corrected. | `scout-and-peaks.txt`; `r83_probe.py:391-406` |
| ADJ-5 | scout | minor | Prose-only statistics: mean +4383.3/+4382.4 **re-derives exactly** from retained bytes; the gap histogram 12×1187/13×549 re-derives as **12×1233/13×549** (13 bucket exact; 12 bucket −46 = the number of 2-sample zero runs). Neither figure is stored in `p5-resample.json`. | retained `PK44_*.wav` |
| ADJ-6 | scout | minor | "6/6" segv reps and "§1 38 legs" do not match the consolidated receipt (1 `S7_empty` leg; 36 legs + 5 content legs = 41). The boundary's 8/8 + 3/3 receipted run is the substantiated form. | `p1-args.json` |
| ADJ-7 | scout | note | "deterministic 2/2 reps" is substantiated by the retained byte-identical `PK44_1/2.wav`, but the receipt serializes one leg only (no rep dimension). | sha equality |
| ADJ-8 | boundary | nit | §7 numbers **7** unstated modes; §0 headline says "plus 6". | report text |
| ADJ-9 | boundary | minor | C3's windowed figures (1551.9 / 2046.9) have no stored window spec; the phenomenon reproduces (tone-anchored 0.5–1.5 s: 1267.1/2046.6; Goertzel 2190.1/4095.6) and C4's stability reproduces. | `s2-channel.json` + raw `C3/C4` wavs |
| ADJ-10 | boundary | nit | §10's "per-leg `runs/<stage>/<leg>/{cmd.txt,stderr.txt,meta.json}`" holds for 105/133 dirs; 6 receipt legs (`s6x-pins` ×4, `s9x-move` ×2) have no dir and the 8 `s5-scale` legs' dir names carry a `scale_` prefix absent from the receipt. | dir/receipt diff |
| ADJ-11 | boundary | nit | "no run >2" holds in the tone region; whole-file run histograms also contain the two silence runs (43 648 / 5 122). | zero-run histograms |
| ADJ-12 | scout | custody | Scout evidence tree is **untracked** (0/21 files); all its shas were re-derived today from host bytes only — same pattern as r82/r91/r96/r97 scouts. | `git ls-files corpus/live/r83-scout` = 0 |
| ADJ-13 | lane | note | During the audit HEAD moved to `bc3f55ca` and the tracked fixture was rewritten by the r82-fold seat (worktree `7cf9b00d…` → `1e67a024…`); every r83 number here comes from the `a151a226` archive, so no r83 claim is affected. | `commit-pin.txt` |

---

## 5. Write-scope / custody notes

- Author evidence: 2 tracked files (`measurements-run{1,2}.json`) + the report
  in `a151a226`; the 4 canonical run dirs untracked (ADJ-3). Fixture diff is
  insertion-only with the 3 deleted lines being the r83 wiring lines.
- Boundary evidence: 446 tracked (444 manifest files + `manifest.json` +
  a tracked `__pycache__/r83b_probe.cpython-314.pyc`); the manifest covers every
  file except itself and that `.pyc`; `scratch/` tones and the MIDI note are
  included.
- Scout evidence: 0 tracked (ADJ-12); report tracked in `15c6a35b`.
- This seat wrote only `reports/round-83/r83-scribe.md` and
  `corpus/live/r83-scribe/` (6 receipts + `manifest.json`, 49 263 B; the
  manifest lists each receipt's bytes+sha256). No tracked file was modified,
  no commit, no push, no PipeWire object created, no `set-default-*`.

---

## 6. Remaining risks / blockers

1. ADJ-1 is a provenance defect in an otherwise byte-faithful, green author
   landing: the adjudicator should decide whether the report's stamp is
   corrected to 22:01:05Z and the two red executions disclosed, or the receipts
   index is re-issued. The underlying measurements do not need re-running.
2. ADJ-4/5/6 are scout-report defects; the *substance* of every affected claim
   is now carried by the boundary's and author's receipted evidence plus this
   seat's byte re-derivation, so no scout re-run is required for the round.
3. ADJ-3/12 are preservation gaps (untracked run dirs; unretained taps): any
   future re-derivation of the author's `zero_frac` or onset transports needs a
   fresh execution, not the current corpus.
4. ADJ-9/10/11 are wording/inventory nits that do not affect any verdict cell.
5. No blockers for the round; the boundary dossier is the cleanest of the three
   and its headline score (10 confirmed / 2 falsified / 1 over-generalized /
   1 corrected cell) matches its own 13-row verdict table.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
