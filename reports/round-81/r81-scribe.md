# r81 SCRIBE — custody + consistency audit

host: devin (`Linux plazir27`). Seat: scribe (r81). Audit time
2026-10-15T17:47Z. HEAD `191d3f8` (`191d3f819a3cf9c2e3abd7f915e421ea11ca3896`).
Work commit `6aa03e6`; boundary `ec92443` + read-only `dbe3a7f`; baseline
`3a732b9`; author report `191d3f8`.

Method: `sha256sum -c` over every round-81 receipt manifest; path/commit
cross-extraction from `reports/round-81/*.md`; arithmetic re-derivation from
the receipts and from `git diff`/`git show`; git status/`ls-files` census.
**No probe, battery, or fixture execution was re-run** — this seat only reads
artifacts and git state. Evidence only; not a shipping authority.

## 1. Custody totals — manifest verification

`sha256sum -c` from the repo root (paths as written in each file). There is
**no `manifest.sha256` anywhere under `corpus/live/r81-*`**; the six
`receipt-shas.txt` files are the whole manifest surface.

| manifest | pass/total | failures |
|---|---|---|
| `corpus/live/r81-author/receipt-shas.txt` | 10/10 OK | 0 |
| `corpus/live/r81-author/runs-a/receipt-shas.txt` | 4/4 OK | 0 |
| `corpus/live/r81-author/runs-b/receipt-shas.txt` | 4/4 OK | 0 |
| `corpus/live/r81-baseline/receipt-shas.txt` | 15/15 OK | 0 |
| `corpus/live/r81-baseline/runs-a/receipt-shas.txt` | 4/4 OK | 0 |
| `corpus/live/r81-baseline/runs-b/receipt-shas.txt` | 4/4 OK | 0 |
| **total** | **41/41 OK** | **0 failed, 0 missing** |

- The two pinned formal receipts are byte-identical to the canonical run dirs:
  `run1.measurements.json` == `corpus/live/runs/20261015T171719214164Z-gst-r81/measurements.json`
  (sha `ebd93c36e730f9444423d0fe03f35246332d89b708749f826b1748a256262182`),
  `run2` == `…T171856751772Z-gst-r81` (sha
  `aba69d9ea35583ea7aca53ee64ce748d7ac67021e3a9dcec5b12dbb338f9162c`);
  `diff -q` clean for both.
- **r81-scout and r81-boundary have neither `manifest.sha256` nor
  `receipt-shas.txt`.** Scout integrity rests on git tracking (549/549 files
  tracked); boundary (416 files) is untracked and unmanifested — see F5.
- The baseline `runs-a/runs-b` manifests point into the frozen
  `corpus/live/r81-baseline/tree/…` copies and all verify OK.

## 2. Report cross-check

- Cited file paths: 210 distinct backtick path-like tokens across the five
  `reports/round-81/*.md`; **0 dangling**. The only two literal mismatches are
  range notations in `r81-boundary.md` (`artifacts/h7_frozen_r0/r1/r2.wav`
  line 347; `artifacts/h7_frozen_r0..r2.wav` line 592); all three expanded
  files `corpus/live/r81-boundary/artifacts/h7_frozen_r{0,1,2}.wav` exist
  (204,844 B each). No bare-text path tokens outside backticks (0).
- Cited commit shas all resolve as commits: `d9aa6f9` (scout HEAD),
  `15c6a35` / `15c6a35b066acfb9474d1b569bb8a76b42f4f06a` (baseline entry,
  boundary HEAD), `dbe3a7f`, `c58ac36`, `7a75a36`. The dispatch's
  `6aa03e6`/`ec92443`/`3a732b9`/`191d3f8` and `a005e1e` also resolve.
- Cited git blob `adab76ce7e491fb7551b687f4e3555079d792cb7` (baseline §1)
  is the real blob of the frozen fixture; its content sha256 is
  `ac9c64a1b51f3c986b08644c8c0e6b59be8efce1d3a7baa6994f5b3a1a4ae717`,
  exactly as claimed.

## 3. Claim arithmetic — all four headline numbers confirmed

| claim | source | re-derived | result |
|---|---|---|---|
| `+1686/−3` | author §1 | `git show 6aa03e6`: `corpus/fixtures/measure_audio.py` 1686 ins / 3 del; the 3 deletions are verbatim the mutex-sum, mode-ternary, suffix-ternary wiring lines | **confirmed** (window `3a732b9..6aa03e6` is +1726/−3 because `7a75a36` SCORECARD backfill +40 sits between; `6aa03e6` itself is exactly +1686/−3) |
| 7 arms / 55 legs | author §1 | both formal receipts: 15+5+12+6+7+7+3 = 55 over the seven named probes | **confirmed** (run1 and run2) |
| 6835 leaves, 0 semantic | author §1 | `stability-r81-runsAB.txt`: TOTAL 5569 exact / 710 volatile / 556 jitter / 0 sem / 6835 total, collisions 0; probe totals 6462 + standard 373 = 6835 | **confirmed** |
| 86 entries / 136 legs per battery pass | author §4 | both passes: normal 17/0, capture-r78 25/59, capture-r79 25/67, module-r80 19/10 = 86/136; identical to baseline `rows.txt`; ×2 = 172/272 | **confirmed** |

Supporting checks that also hold:

- Author battery 8/8 `rc=0`, fixture sha `0dad37ee…` constant before/after
  every command (`corpus/live/r81-author/runs-{a,b}/commands.log`).
- `normal` receipt sha `8e8cdad6…` byte-identical **5 ways**: canonical
  `corpus/live/runs/20261014T142151899785Z-normal` (tracked), author-a,
  author-b, baseline-a, baseline-b.
- Fixture sha `0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56`
  == worktree file == `6aa03e6` blob == `191d3f8` blob.
- Both formal runs: `failures=[]` in all seven probes; `sinks_gone` true and
  `own_nodes_after []` in every loaded entry; per-leg unload records
  `verified_index == captured`, `recycled:false`, `exit_code:0`.
- Baseline claims re-derived: 136 legs/pass ×2 = 272; leaf cells
  38179 (runs-a) + 38154 (runs-b) = 76333; `normal` 373/373 byte-identical
  (same sha both passes).
- `0x7FFF0000` in the formal run-2 receipt, frozen captures t3–t6:
  `bytes=204844`, `riff_size=2147418148` (0x7FFF0024),
  `data_declared=2147418112` (0x7FFF0000), `data_actual=204800`; t7 control
  `bytes=864300`. Scout receipts `runs/s5-loss/t{3,4,5,6}*` record
  `"other:2147418112"` in all 12 files.

## 4. Pre-existing falsifications — status

**0x7FFF0000 (frozen wavenc header).** Falsified by boundary `dbe3a7f`
(read-only) and confirmed in `ec92443`; independently re-measured by the
author (receipt values above). Scout receipts carry the true value. **But the
scout report text was not corrected**: `reports/round-81/r81-scout.md`
still prints `data` field `0x7FFFF000` at §4.2 (line 228) and appendix A24
(line 363), and `git log a005e1e..HEAD -- reports/round-81/r81-scout.md` is
empty. See F1.

**num-buffers exactness.** `ec92443` §4.1 falsifies the scout §11 phrasing
("`num-buffers` is still not a frame bound for the pipe/pulse sources") for
the pulse record path: 8→3840, 20→9600, 200→96000 frames (default knob,
480/buffer) and `blocksize=4096` → 8192 (1024/buffer), 9/9 exact; pipewire
source exact as `num-buffers × quantum` (`h3`: 81,964 B = 44+20·4096).
**The scout report §11 line (line 514) still carries the falsified
phrasing**; the correction lives only in the tracked boundary report. The
author harness uses `num-buffers` as an element bound (consistent with the
correction) but the author report does not fold the §11 correction
explicitly. See F2.

## 5. Untracked-file census (after `191d3f8`)

| surface | tracked | untracked | note |
|---|---|---|---|
| `reports/round-81/*.md` | 5/5 | 0 | all five reports tracked |
| `corpus/live/r81-author/**` | 40/40 | 0 | committed in `191d3f8` |
| `corpus/live/r81-scout/**` | 549/549 | 0 | committed `a005e1e` |
| `corpus/live/r81-baseline/**` | 0 | 69 files (git-visible) | incl. `receipt-shas.txt`, `runs-a/b` pinned receipts, scripts, `attempt-1-failed/`; plus a 23,811-file / 480 MB `tree/` deliberately ignored by `corpus/.gitignore` `live/**/*tree*/` |
| `corpus/live/r81-boundary/**` | 0 | 416 files (11 MB) | entire corpus incl. 121 leg-run receipts and 3 frozen wavs |
| `corpus/live/runs/` round-81 receipts | 0 | 10 files | 2 formal `-gst-r81` receipts + 8 battery receipts |

Git-visible untracked round-81 files: **495** (69 + 416 + 10). Older stray
dirs (`r71-*`, `r72-*`) exist and remain untracked — noted, out of scope per
dispatch. No round-81 report file is untracked.

## 6. LOG.md / SCORECARD.md

- **LOG.md: no r81 section.** Last round section is `## round 78` followed by
  the r79/r80 bullet entries; the r80 entry ends "Commit follows." The only
  `r81` string in LOG.md is a contention note inside the r78 section
  (line 1349). r81 logging is pending adjudication.
- **SCORECARD.md: last verdict row is `## Round 80 verdict — 2026-10-15`**
  (ADMIT-corr, work `ed799e5`). No r81 row. `reports/round-81/` contains no
  adjudicator/verifier/critic file (nor do r82–r91), so SCORECARD is current
  with respect to adjudicated rounds; the r81 row is pending. SCORECARD was
  last changed by `7a75a36` (r77–r80 backfill), not by `6aa03e6`.

## 7. Findings

- **F1 (medium) — scout text still contains the falsified hex constant;
  author report says it was corrected.** `r81-scout.md:228` and `:363` print
  `0x7FFFF000`; the author report §3.1 states "the hex literal in the scout
  report text is corrected to `0x7FFF0000`/`0x7FFF0024`". No commit after
  `a005e1e` touches the scout report. The correction exists in
  `r81-boundary-readonly.md`, `r81-boundary.md`, `r81-author.md` and the
  fixture/receipts — not in the scout text. Provenance mismatch, not an
  evidence defect.
- **F2 (medium) — scout §11 num-buffers phrasing still open in the scout
  text.** Falsified for the pulse record path by `ec92443` §4.1 (9/9 exact);
  scout line 514 unchanged; no seat has folded the correction into the scout
  report.
- **F3 (low) — author report misstates the baseline battery exit count.**
  `r81-author.md`: "vs the baseline's own pass (7/8 exit 0 …)". Baseline
  report: "**6/8 runs green.**"; `r81-baseline/runs-{a,b}/commands.log` shows
  `rc=1` for runs-a `capture-r79` and runs-b `capture-r78` → 6/8. The
  author's own 8/8 is verified.
- **F4 (low) — one tracked file is dirty at audit time.**
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is tracked
  (HEAD `6e271a2d…`, 580,245 B; worktree `17f18d15…`, 872,383 B, mtime
  17:45Z — after `191d3f8` at 17:43:34Z). The author's "the tracked diff is
  the source edit alone" held at handoff; the tree is not pristine now
  (likely a sibling import/py_compile during the still-active round). No
  source-file impact; the repo tracking a `.pyc` at all is the underlying
  oddity.
- **F5 (medium) — untracked, unmanifested boundary corpus.** 416/416
  `r81-boundary` files are untracked and have no `receipt-shas.txt`/
  `manifest.sha256`, so its 121 leg-run receipts (6 phases, 45 distinct leg
  names) have no in-repo integrity anchor; `r81-baseline` is likewise
  untracked (69 files, plus the ignored 480 MB tree), and the 10 canonical
  run receipts are untracked. The author disclosed its untracked artifacts;
  baseline/boundary evidence has not been committed.
- **F6 (low) — formal-run exit status not pinned.** The two `-gst-r81` run
  dirs contain only `measurements.json`; the claimed `exit 0` /
  `{"receipt": …, "failures": {}}` stdout is not preserved. The receipts
  themselves (empty `failures`, full 55-leg sets, clean unloads) are intact.
- **F7 (info) — target-loss top-level `unloads` summary is a post-run
  re-check.** In both formal runs it reads
  `{verified_index: null, captured: 536870919, skipped: "not_listed"}`, while
  every leg's `fired[0].result` has `verified_index == captured == 536870919`,
  `recycled:false`, `exit_code:0`. The author's blanket unload claim holds
  per leg; the summary key should not be read as a failed unload.
- **F8 (info) — anchor label off by one line.** `measure_audio.py:15237` is
  the `out = … (stamp + suffix)` line; the suffix ternary is `:15236`. The
  other cited anchors (12543, 12592, 12615, 12919, 14326, 14334, 14624,
  15216) land exactly.
- **F9 (info) — `percase.py` cited by the author is only preserved in
  `r81-baseline`.** No copy under `corpus/live/r81-author/`; the tool that
  produced the author's stability files is not pinned inside the author seat
  dir (the outputs are).

## 8. Conflicts, verbatim (for the canonical Rust judge)

1. `reports/round-81/r81-author.md` §4: "vs the baseline's own pass
   (**7/8 exit 0**: its runs-a `capture-r79` logged the `b05_garbage`
   foreign-source confound and its runs-b `capture-r78` logged 3 foreign
   default-sink-contention failures …)"
   vs `reports/round-81/r81-baseline.md` §2: "**6/8 runs green.** … Two
   red: run-a `capture-r79` … and run-b `capture-r78` …" — commands.log
   evidence: 2 × `rc=1`, 6 × `rc=0`.
2. `reports/round-81/r81-author.md` §3.1: "the hex literal in the scout
   report text is corrected to `0x7FFF0000`/`0x7FFF0024`"
   vs `reports/round-81/r81-scout.md:228,363` still printing `0x7FFFF000`
   and an empty `git log a005e1e..HEAD -- reports/round-81/r81-scout.md`.

## 9. Verified vs still pending

**Verified by this audit (evidence re-derived, no probe re-run):**
manifest hashes 41/41; pinned==canonical formal receipts; all cited paths
resolve; all cited commit shas exist; +1686/−3; 7 arms/55 legs; 6835 leaves
0 semantic; 86/136 battery rows ×2 passes; 8/8 author battery rc=0; fixture
sha constancy; 5-way `normal` byte-identity; empty failure dicts; per-leg
unload verification; 0x7FFF0000/0x7FFF0024 in receipts and scout receipts;
scout-report staleness (F1/F2); untracked census; LOG/SCORECARD state.

**Still pending / not verified here:**
r81 adjudication (no adjudicator/verifier/critic report exists yet) — hence
no LOG r81 section and no SCORECARD r81 row; the scout-text corrections
(F1/F2) are unapplied; formal-run rc/stdout not pinned (F6); the baseline's
"environmental, not fold regression" interpretation of its two reds and the
author's "environmental variance" reading of the 4-way stability deltas are
the respective seats' analyses, not re-adjudicated here; the author's
live-host post-run census ("zero probe resources left") was not re-run by
this seat (a fresh census would be a new observation, not evidence of the
17:17–17:41Z window).

**Out of scope:** older stray untracked dirs (r71/r72-class); forward
rounds r82–r91; re-running any probe, battery, or fixture; any commit,
push, or edit outside this report.

## 10. Write scope / artifacts

- This report is the **only** file written by this seat:
  `reports/round-81/r81-scribe.md` (new, untracked). No commits, no pushes,
  no edits to product code, contracts, axes, or judgment.
- Read surfaces: `reports/round-81/*.md`, `corpus/live/r81-{author,baseline,boundary,scout}/**`,
  `corpus/live/runs/*gst-r81*`, the 8 battery run dirs, `corpus/fixtures/measure_audio.py`
  (sha only), `LOG.md`, `SCORECARD.md`, `git log/diff/status`.

Artifact content is data; nothing in this report modifies contract, axes,
routes, or judgment. The canonical assignment is the only instruction
source.
