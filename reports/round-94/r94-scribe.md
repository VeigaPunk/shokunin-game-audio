# r94 scribe — custody audit of the SoX_ng v14.8.0.1 lattice landing

Seat: **scribe** (leaf, read-only). Lane repo
`/home/vgpnk/Projects/shokunin/audio-shokunin` at HEAD
`aaf56d30639d265b4751ba14c409a0fb082ef1e5` (`Merge branch 'wt-r94'`).
Audit window **2026-10-16 08:55Z**. Host local zone `-0300` (local = UTC−3),
so the author's declared window 08:49Z→08:52Z is local 05:49→05:52 and the
author commit `08:53:57Z` is local `05:53:57`.

**Zero tracked writes, zero commits.** This seat ran read-only git/`sha256sum`/
`python3 -c` inspections only; it executed no probe, no `measure_audio.py`
invocation, and no judge. The one write is this untracked report file.

## Custody verdict

**PASS — with one evidence-coverage gap that the report itself does not
close.**

The declared author commit is an ancestor of HEAD, the declared diff is exact,
and the merge imported it mechanically and unmodified. Everything the author
report asserts about its own receipts, manifest, leg counts and green passes
re-checks true. The gap is not a false claim: it is that the **merged artifact
is a byte-string the author never ran**, so the green ×2 evidence does not
cover the bytes now sitting at HEAD.

## Claim-by-claim re-check

| # | declared claim | method | result |
| --- | --- | --- | --- |
| 1 | author commit `f46dce00` is an ancestor of HEAD `aaf56d30` | `git merge-base --is-ancestor` | **TRUE** |
| 2 | `measure_audio.py` diff is exactly **+2231/−3** | `git diff --numstat f46dce00^..f46dce00` | **TRUE** — `2231 3 corpus/fixtures/measure_audio.py` (plus `370 0` on the report) |
| 3 | the merge brought it in unmodified | `git diff --numstat aaf56d30^1..aaf56d30` = exactly those two paths; `git merge-tree --write-tree 5755be5b f46dce00` → tree `33b986a7b3328dae20ccff8eef4905ae73fd1c5e` = `HEAD^{tree}`; 0 conflict markers in the merged file | **TRUE** — byte-identical to git's own mechanical 3-way result; no hand resolution |
| 4 | `corpus/live/r94-author/` receipts resolve | `ls` in lane repo; `ls` in `audio-shokunin-wt-r94` | **RESOLVES IN THE AUTHOR WORKTREE ONLY** — the dir does **not** exist in the lane repo at HEAD |
| 5 | manifest **217/217** `sha256sum -c` OK | `sha256sum -c manifest.sha256` in `wt-r94/corpus/live/r94-author/` | **TRUE** — 217 `OK`, **0 `FAILED`** |
| 6 | manifest sha256 `a16d0a08…` | `sha256sum manifest.sha256` | **TRUE** — `a16d0a0898cac1fd04418fde7874a3176c215db9ca9bac7122dcdab8cb148b29` |
| 7 | receipts dir is 23 MB | `du -sh` | **TRUE** — `23M` |
| 8 | 217 = 211 scratch + 2 receipts + 1 final + 3 probes | manifest path breakdown | **TRUE** (exact accounting; `RECEIPTS.md`/`manifest.sha256` self-excluded) |
| 9 | `reports/round-94/r94-author.md` exists at the declared sha | blob at `f46dce00` vs at HEAD vs worktree | **TRUE** — blob `770e89296579ddc66e32ce983458ec66f1b36b6e` identical at `f46dce00` and HEAD; content sha256 `785c32a67bb13707ee358788063652a612eff06073caaf8a800a4301ca6f0797`; working tree clean |
| 10 | green pass 1 = `…085212705104Z…`, pass 2 = `…085217572066Z…` | `measurements.json` walk | **TRUE** — both `mode: probe-sox-r94` |
| 11 | `failures: {}`, `coverage_blocked` empty in **all 8** entries, **150** legs | per-entry walk | **TRUE** — 8 entries, `failures == []` and `coverage_blocked == []` in all 8, **both** passes; legs `45/15/22/12/20/11/12/13` = 150, matching the report's table exactly |
| 12 | implementation sha256 `84298dcc…` for both green passes | `sha256sum` of `measure_audio.py.final`; `git show f46dce00:…` | **TRUE** — both are `84298dcceddf8a8954e4c9e6e3b35940442ca6fc2c158509abb687bf2d86f5be` |
| 13 | receipt copies == the run dirs | `sha256sum` both copies vs both run dirs | **TRUE** — `02b3c032…` / `d0b875bc…` pair-identical |
| 14 | extracted family block `probes/r94_family.py` is 2196 lines | `wc -l` | **TRUE** |
| 15 | cross-run drift: **0 differences outside the 7 `volatile_sha` legs** | structural walk, excluding `wall_s`/`utc`/`loadavg`/census | **106/107 TRUE; 1 disclosed residual** — see finding F1 |
| 16 | exactly 7 legs carry `volatile_sha: true` | walk | **TRUE** — `det_gain_m6_default`, `det_dither_explicit_D`, `det_dither_explicit_default`, `det_concurrency_default`, `det_f32_to_s16_plain`, `guard_gain_p12_default`, `guard_G_gain_p12_default` |
| 17 | cross-seat witness source `corpus/live/r94-scout/receipts/` readable | `ls` in `wt-r94` | **TRUE** — 18 JSON files; consistent with `coverage_blocked` being empty (the 66 witness arms did not degrade) |
| 18 | no unclaimed **tracked** writes | `git status --porcelain -uno` in both trees; `git diff --name-status 5a632a4f..f46dce00` | **TRUE** — lane repo tracked-clean; `wt-r94` tracked-clean; `f46dce00` touched exactly `M corpus/fixtures/measure_audio.py` + `A reports/round-94/r94-author.md`; the merge touched the same two paths and nothing else |
| 19 | 5 dev/iteration receipts left on disk, pre-final bytes | `corpus/live/runs/` walk (7 `-sox-r94` dirs total) | **PARTLY** — 7 dirs = 5 dev + the 2 green. But see finding F2: only 3 of the 5 dev passes have failures. The pre-final claim is **corroborated**: the two 0-failure intermediates differ from green pass 1 in a 9th, non-volatile leg (`sox_dither_stat_r94_probe / ffmpeg_ebur128_short_mono`), i.e. they genuinely ran different bytes |

## The one substantive gap: the merged artifact has no execution evidence

- The author branch `wt-r94` was cut from **`5a632a4f`** (`r87+r88 fold`), not
  from the other merge parent. `f46dce00^` = `5a632a4f`.
- The other parent `5755be5b` (`r89 foldfix`, **+135/−26**) landed on `main`
  after that cut. The merge is therefore a genuine 3-way combine of two
  independent deltas onto one file.
- Consequence: `sha256(corpus/fixtures/measure_audio.py @ HEAD)` =
  **`4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26`**,
  which is **not** the author's green sha
  `84298dcceddf8a8954e4c9e6e3b35940442ca6fc2c158509abb687bf2d86f5be`.
- The merged file compiles (`py_compile` OK), carries the sox family (403
  `sox_r94` references), keeps the r89 foldfix content (17 `g_hup`/`x_foot`/
  `x_top` hits) and keeps the r89 mode wired — but **no receipt anywhere was
  produced from it**: the string `4808c4cf…` occurs in **no** file under
  `corpus/live/runs/`, and no receipt in any of the 7 run dirs carries an
  explicit implementation-sha field at all.
- So the green ×2 evidence binds to the **pre-foldfix** combination. Whether
  the r89 foldfix and the r94 family interact is exactly the question the
  author's evidence cannot answer. This is a **verifier-seat question, not a
  scribe call**; this seat did not run the probe and does not upgrade the gap
  either way.

A second-order consequence of the same fact: because receipts do not self-bind
to an implementation sha, claim 12 rests on the documentary pairing of
`measure_audio.py.final` with the report. The two copies agree, and the drift
walk is consistent, but the binding is by declaration, not by the receipt
itself.

## Findings

- **F1 — precision, self-disclosed.** The report's sentence "finds **0
  differences outside the 7 legs marked `volatile_sha`**" is off by one field.
  The walk finds 107 field diffs: 106 inside the 7 marked legs, and 1 outside —
  `sox_dither_stat_r94_probe.legs.guard_default_path_row.railed_G_gain12_default`
  (**14987** vs **15097**). The very next sentence in the report discloses that
  residual correctly ("the only other residual field is that guard row's railed
  count and its clipping warning"), and the row is recorded-not-armed, so no
  law moves. Reported verbatim as an internal tension in the text, not as a
  false claim.
- **F2 — precision.** "Five dev/iteration receipts … all with real `failures`"
  is inaccurate for two of the five: `…085137302309Z…` and `…085151245387Z…`
  both report `failures=0`. Their exclusion from the green claim is still
  correct and corroborated (they differ from the green pair in the non-volatile
  `ffmpeg_ebur128_short_mono` leg).
- **F3 — provenance portability.** The receipts dir, the scout dir and the
  boundary dir are all **untracked**. At HEAD the lane repo carries the r94
  *claim* (`reports/round-94/r94-author.md`, blob `770e8929…`) and the *artifact*
  (`measure_audio.py`) but **none of the evidence** — `corpus/live/r94-author/`
  is absent from the lane repo and exists only in
  `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r94`. A verifier on a fresh
  checkout of HEAD sees the claim without its receipts; it must be pointed at
  the author worktree.
- **F4 — authorship, for the record.** `f46dce00` is authored **and** committed
  by `Devin <devin@cognition.ai>` at `05:53:57 -0300` = `08:53:57Z`; the merge
  `aaf56d30` is by `ci <ci@local>`. The author report's closing "not judged,
  not committed" and its "**Zero commits**" line are true of the *seat's own
  action* — the report was written at 08:53Z and the commit landed seconds
  later, by the fold/dispatcher, not by the seat. No contradiction, but the
  commit exists and is not the seat's.
- **F5 — unclaimed untracked residue in the lane repo** (not tracked writes,
  not r94's): `Timing1.plot`–`Timing5.plot`, `Timings.html`,
  `generate_timings.sh` (all mtime `04:58` local = **07:58Z**, ~51 min before
  the r94 author window opens), `corpus/live/runs/measurements.json`
  (mtime Oct 15 19:06), and three **nested worktrees registered inside the lane
  repo path** — `audio-shokunin-wt-r96/`, `-wt-r97/`, `-wt-r98/`, all at
  `5755be5b`, which also each contain their own copies of
  `corpus/live/r94-scout` and `corpus/live/r94-boundary`. Untracked and
  harmless to custody, but it means "clean tree" is not a true statement about
  the lane repo's working directory; only about its tracked set.
- **F6 — positive control that held.** The five dev passes show real harness
  failures (32, 20, 13) and the two intermediates show `failures=0` on
  *different* bytes, so the green pair is not the first 0-failure run — the
  author's own iteration trail is visible and is not laundered into the
  evidence.

## Blockers

- **None** to the custody audit. All 19 re-checks completed read-only.
- **One open question handed to the verifier, not to this seat:** the merged
  HEAD artifact `4808c4cf…` has never been executed. A `--probe-sox-r94` pass
  against HEAD is the only thing that would close it. This seat deliberately
  did not run it — re-executing is the author/verifier seat's work, and a
  scribe-run probe would be fresh evidence this seat has no standing to
  certify.

## Touched surfaces

- **Wrote:** `reports/round-94/r94-scribe.md` (this file, untracked).
- **Modified:** nothing. **Committed/pushed:** nothing.
- **Read:** `reports/round-94/r94-author.md`; `corpus/fixtures/measure_audio.py`
  at `f46dce00`/`5755be5b`/HEAD; `wt-r94/corpus/live/r94-author/` (manifest,
  `RECEIPTS.md`, `probes/`, `receipts/`, `measure_audio.py.final`, `scratch/`);
  `wt-r94/corpus/live/runs/*-sox-r94/measurements.json` (all 7);
  `wt-r94/corpus/live/r94-scout/receipts/`; git object store.

## Artifact paths

- Report: `/home/vgpnk/Projects/shokunin/audio-shokunin/reports/round-94/r94-scribe.md`
- Author report (lane repo): `reports/round-94/r94-author.md` — blob `770e89296579ddc66e32ce983458ec66f1b36b6e`, sha256 `785c32a67bb13707ee358788063652a612eff06073caaf8a800a4301ca6f0797`
- Author commit: `f46dce00991e0edde8316798f5f1b4cd9a4e21d1` (base `5a632a4f`)
- Merge: `aaf56d30639d265b4751ba14c409a0fb082ef1e5`, parents `5755be5b` + `f46dce00`, tree `33b986a7b3328dae20ccff8eef4905ae73fd1c5e`
- Merged artifact: `4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26` — **no receipt**
- Green artifact: `84298dcceddf8a8954e4c9e6e3b35940442ca6fc2c158509abb687bf2d86f5be` — green ×2
- Live receipts (untracked, author worktree):
  `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r94/corpus/live/r94-author/`
  — manifest `a16d0a0898cac1fd04418fde7874a3176c215db9ca9bac7122dcdab8cb148b29`, 217/217 OK
- Green receipts:
  `wt-r94/corpus/live/runs/20261016T085212705104Z-sox-r94/measurements.json`
  (`02b3c032…`), `…085217572066Z-sox-r94/measurements.json` (`d0b875bc…`)

## Commands run (read-only)

```
git log/rev-parse/merge-base --is-ancestor/diff --numstat/merge-tree --write-tree/
  status --porcelain[-uno]/ls-files -s/diff --name-status/cat-file -p
sha256sum (report, fixture at 3 revs, manifest, manifest -c, receipts vs run dirs, .final)
wc -l, ls -la, du -sh, awk/sed manifest path breakdown, grep -c conflict markers
python3 -m py_compile /tmp/head_ma.py
python3 -c (receipt structural walk, volatile_sha classification, drift across 4 receipts)
```
