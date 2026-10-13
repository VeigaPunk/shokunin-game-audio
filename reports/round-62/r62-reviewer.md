# R62 reviewer — non-author audit of round 61 (valid17/valid16 extensible pair)

Seat: reviewer (leaf, non-author). Host: devin. Executed from lane worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` resolves via symlink to
`~/Projects/shokunin/audio-shokunin` (confirmed: `readlink -f` →
`/home/vgpnk/Projects/shokunin/audio-shokunin`).

`measure_audio.py` accepts no `--runs` flag (verified: 76 `add_argument` calls,
none for runs; `ROOT = Path(__file__).resolve().parents[1]` hardcodes
`corpus/live/runs/`). All 82 receipts therefore append to the canonical runs
dir — same convention as every prior verifier. My scratch (extracted command
TSV, per-command stdout/stderr capture, exits table, before/after runs census)
lives under `corpus/live/r62-reviewer/`.

## A. Fresh serial replay of the r61 82-command ledger — AGREES

Extracted all 82 commands programmatically from `r61-verifier.md`'s ledger
(regexp on the table rows → `corpus/live/r62-reviewer/commands.tsv`; asserted
`#` sequence 1–82 and the ledger's own exit column summing to 43/39 *before*
running). Ran each serially once, captured stdout JSON + stderr + exit code per
command.

- **Exit shape: 43 exit 0 / 39 exit 1 — exact match** (`awk` over `exits.tsv`;
  every one of the 82 rows also matches its ledger exit code individually).
- **Receipt freshness**: runs census before = **2,453 dirs** (consistent with
  the adjudicator's 2,369 pre + 82 verifier + 2 adjudicator). After = 2,535;
  `comm -13` yields **exactly 82 new dirs**, timestamps
  `20261013T220247762216Z`–`20261013T220413514733Z`, monotone, suffix sequence
  identical to the ledger order (`new-dirs.txt`). Zero duplicates, zero extras.
- **Receipt equality vs the r61 verifier's 82 receipts: 81/82 byte-identical**
  (`read_bytes()` comparison, my dir #n vs the verifier's cited dir #n).
- **All 82 stdout payloads parse as JSON**; all 39 exit-1 outcomes carry
  in-receipt failure records (validation outcomes, not crashes).
- Spot-compare required by brief: **normal** (`220247762216Z-normal`),
  **valid17** (`220248834432Z-…`), **valid16** (`220249901871Z-…`) — all three
  byte-identical to the verifier's `165521565727Z`, `165522836463Z`,
  `165524127908Z` respectively.

### The single byte-level divergence (explained, not a defect in r61 evidence)

Receipt #77 (`--probe-invalid`) differs in exactly one line: the captured
ffprobe `stderr` for `corrupt.wav` embeds the **resolved absolute path** —
r61's receipt shows `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/…`,
mine shows `/home/vgpnk/Projects/shokunin/audio-shokunin/…`. Cause: between r61
and now the lane content was extracted from the prymeagnt repo into the
standalone repo and `.shokunin/audio` became a symlink (prymeagnt commits
`c4adfd2a`, `8ec47838`); `Path(__file__).resolve()` now yields the canonical
path. R59/R60/R61 invalid receipts all embed the prymeagnt path (verified on
`131358546073Z`, `133323717760Z`, `165701077902Z`); mine is the first with the
new base. Every gate-relevant field is identical — this is an
environment-path string, not a measurement. **New disclosure**: the
invalid-battery receipt is not byte-stable across repo relocations.

## B. Prior-80 preservation vs the R60 designated ledger — AGREES (1 explained diff)

Mapped my #1 ↔ R60 #1 and my #4–82 ↔ R60 #2–80 (R60 dirs parsed from
`r60-verifier.md`, 80 unique). **79/80 byte-identical**; the sole diff is the
same `--probe-invalid` stderr path line above. The r61 verifier's "80/80 exact
complete-JSON match" held in its own window; at r62 the same mapping shows one
environment-path string delta.

## C. Fixture bytes and independent tool reproduction — AGREES

- `pair_valid_17.wav` SHA `15cadf24…b63fe4`, `pair_valid_16.wav` SHA
  `2c5e244f…591d00`, each 11,588 bytes; `cmp -l` reports exactly one byte —
  file offset 38 (cmp's 1-based byte 39): `0x11` vs `0x10`.
- Fresh ffprobe (n9.0.1): valid17 → `pcm_s24le`, `s32`, `bits_per_sample=24`,
  `bits_per_raw_sample=24`, duration `0.080000`; valid16 → `pcm_s16le`, `s16`,
  16 bits, `0.120000`. Reclassification reproduces.
- Fresh SoX (SoX_ng v14.8.0.1) f32 decode: valid17 → **15,356 bytes = 3,839
  samples**, SHA `3cda5978…1e707c`; valid16 → **23,040 bytes = 5,760**, SHA
  `407e8c22…b6f9a97` — byte-identical to the committed
  `corpus/live/round-61/valid{17,16}.f32` artifacts (fourth independent
  reproduction of the same bytes). The **3,839-vs-3,840 one-frame gap**
  (11,520/3 = 3,840 expected) and the **`sox --i` "16-bit Signed Integer PCM"
  vs 24-bit ffmpeg-backend decode inconsistency** both reproduce — the r61
  UNKNOWNs stand, unsoftened.
- valid17 receipt: 18 measurement entries; sole failing entry
  `ui_extensible_valid_17_r61_probe` with exactly
  `['format: expected PCM16', 'duration: outside ±1 ms', 'level: clipping
  headroom or near silence', 'spectrum: centroid outside fixture band']`;
  measured `pcm_s24le`/24/48000/mono/`0.08` s, peak `0.992279052734375`, RMS
  `-7.797933085328953` dBFS, centroid `12180.625368025178` Hz, bandwidth
  `7171.544640451181` Hz — all as recorded. valid16 receipt: zero failures,
  `pcm_s16le`/16/`0.12` s. My normal receipt is **byte-identical to both** the
  R60-author (`132816640667Z`) and R60-verifier (`133202557584Z`) normals.

## D. Source-diff claim — AGREES (with adjudicator's corrected split)

`git diff 0a300b4..04b4bd4` (the post-rewrite equivalents of `cd62e6d1..1b35faaa`):
hunks touch only the two argparse flags, the mutual-exclusion sum (+2 args),
the forwarded-builder/measurement block (`measure(name, SPECS["ui"], path)` on
`live/round-61/pair_valid_{17,16}.wav`), and the `mode`/`suffix` chain heads.
`format_failures`, `SPECS`, thresholds, canonical 17 untouched. Numstat
**`build_artifacts.py` +18/−1, `measure_audio.py` +13/−4 = +31/−5** — confirms
the adjudicator's correction and the author/verifier off-by-one per-file split
(total correct), already disclosed by the adjudicator as transcription-level.
Commit `04b4bd4` also swept ~220 historical scratch files + 2 `__pycache__`
binaries (231 files, +82,634/−5) — hygiene noise as disclosed.

## E. Commit-hash citations — DISAGREE (explained: history rewrite on extraction)

Every commit hash the r61 reports cite **fails to resolve** in
`~/Projects/shokunin/audio-shokunin` (`git rev-parse --verify` / `cat-file -t`
fatal; only branch `main` + `origin/main`; reflog shows rename
`craft/audio-r1` → `main` at `e1ac349`):

| cited hash | role in reports | status in audio-shokunin | resolution |
|---|---|---|---|
| `cd62e6d`/`cd62e6d1` | author/verifier/adjudicator clean-before (R60 final) | **unresolvable** | exists in origin repo `~/Projects/prymeagnt` (worktree r12) as `cd62e6d1 "Audio round 60: final malformed valid0 report"`; post-rewrite equivalent `0a300b4` (parent of `04b4bd4`) |
| `1b35faaa` | adjudicator pinned work commit | **unresolvable** | origin: `1b35faaa "…observe extensible valid17 pair (author+verifier)"`; post-rewrite equivalent `04b4bd4` |
| `4894d07` | LOG r61 retro-declaration "clean-before" | **unresolvable — and wrong even in origin** | origin: `4894d074` is the **R59-final** commit ("Audio round 59: final valid13 pair report"), an ancestor of `cd62e6d`. The LOG's retro-record pins the wrong round's hash; the correct clean-before was `cd62e6d` (author's figure) |

**Cross-repo content equivalence verified**: blob SHAs are identical across the
rewrite — `measure_audio.py` `2efd10ea`, `build_artifacts.py` `39526567`,
`pair_valid_17.wav` `8f723fad`, `r61-verifier.md` `25197c5b` — so the
extraction preserved content exactly; only commit identifiers changed.
Ancestry in origin repo is consistent (`4894d07` ⊂ `cd62e6d` ⊂ `1b35faaa` ⊂
`36f2b057` = r61 final; lane equivalents `0a300b4` ⊂ `04b4bd4` ⊂ `e1ac349` ⊂
HEAD `1c52c7d`).

## Per-checked-claim verdict

| Claim | Verdict |
|---|---|
| 82-command shape 43 exit0 / 39 exit1, all-fresh receipts | **AGREE** — reproduced exactly, 82 new dirs, per-row exits match |
| valid17 exit1 w/ receipt, 4 named failures on sole entry, measured values | **AGREE** — byte-identical receipt, fresh values quoted above |
| valid16 exit0 clean | **AGREE** — byte-identical |
| normal == R60 normal | **AGREE** — byte-identical to both cited R60 normals |
| prior-80 exact subset of R60 ledger | **AGREE** — 79/80 byte-identical + 1 explained env-path string (r61's own claim held fully in its window) |
| pair SHAs, offset-38-only diff, payload identity | **AGREE** — SHA + `cmp -l` reproduced |
| ffprobe `pcm_s24le`/0.08 reclassification; SoX 3,839 vs 5,760; f32 SHAs | **AGREE** — fresh reproduction byte-identical |
| additive-only diff, +31/−5; thresholds/predicates/canonical17 untouched | **AGREE** — hunks audited; per-file split off-by-one already disclosed by adjudicator |
| cited commits resolve & are ancestors of HEAD | **DISAGREE in cited repo** — `cd62e6d(1)`, `1b35faaa`, `4894d07` unresolvable in `audio-shokunin`; all resolve in origin repo `~/Projects/prymeagnt`; blob-identical post-rewrite equivalents exist (`0a300b4`, `04b4bd4`) |
| LOG r61 clean-before `4894d07` | **DISAGREE** — that hash is R59-final, not R60-final, even in the origin repo |
| SoX 3,839≠3,840 gap & `--i`/decode inconsistency retained UNKNOWN | **AGREE** — both reproduce; still unexplained |

## New findings for the record

1. **Receipt byte-determinism exception** (minor): `--probe-invalid` receipts
   embed the resolved absolute fixture path inside captured ffprobe stderr —
   not byte-stable across repo relocation/symlink changes. All other 81
   receipts are relocation-stable.
2. **Cited-commit staleness after lane extraction** (moderate process finding):
   r61-era commit pins are dead in the canonical lane repo; anyone auditing
   r61 against `audio-shokunin` alone cannot resolve them. Equivalents verified
   above. Future reports should cite the post-extraction hash where the lane
   now lives.
3. **LOG retro-declaration mis-pins clean-before by one round** (minor):
   `4894d07` = R59-final; correct was `cd62e6d`/`0a300b4`. The adjudicator had
   already disclosed the declaration's absence/retro-record.

## Residual risk / gaps

- I did not re-run `py_compile`/`git diff --check` as gate steps (same
  disclosure the r61 verifier made); the diff was audited at hunk level and
  all 82 invocations succeeded.
- Depth-axis open items carry forward intact: the 3,839-vs-3,840 mechanism,
  `sox --i` inconsistency, whether ffmpeg's 17→24 rounding is spec-mandated,
  and other >16 values — all still UNKNOWN, all still honestly recorded.
- Other wave members' r62 scratch dirs (`r62-baseline`, `r62-boundary`,
  `r62-critic`, `r62-scout`, `r62-scribe`, `r62-simplifier`) appeared under
  `corpus/live/` during my run — concurrent wave activity, not mine; I wrote
  only `corpus/live/r62-reviewer/`, my 82 append-only runner receipts, and
  this report. `git status` shows zero modified tracked files.

No commits, pushes, merges, or subagent dispatch. One report file written.
