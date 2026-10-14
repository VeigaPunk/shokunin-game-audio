# R69 verifier — AGREE 6/6 (one cosmetic prose nit, one numstat nit, neither material)

Independent non-author replay of commit `30bb86d` on host: devin lane repo
`/home/vgpnk/Projects/shokunin/audio-shokunin` (worktree HEAD `30bb86d`,
clean except pre-existing untracked `__pycache__`/seat scratch dirs).
Toolchain measured live: `sox: SoX_ng v14.8.0.1` (`/usr/bin/sox -> sox_ng`),
`ffprobe n9.0.1`, `python 3.14.7` — identical to the author's declared record.

Method note: to keep all replay output inside scratch
(`corpus/live/r69-verifier/`), the ledger was re-run through a frozen
measure-env (`measure-env/corpus/` = `git archive HEAD` of
`corpus/artifacts` + `corpus/fixtures` + all 63 `corpus/live/round-*` dirs —
the only input roots `measure_audio.py` references). `measure_audio.py`
resolves `ROOT` from `__file__`, so receipts land under
`measure-env/corpus/live/runs/` with corpus-relative `path` fields identical
to canonical. Raw `sox -V6` arms were also run directly against the
committed members (outside the harness) for the byte-level checks.

## Claim 1 — five byte-identical members partition the named arm ≥3 ways by extension alone: **AGREE**

- `corpus/live/round-69/extsuffix_nomatch.{wav,bin,txw,f32,snd}`: all 512 B,
  all sha256 `f073e70ad6e9d8c9f06697a9ca61d0a67bf4c351bcbe742c06c4a611d9d5e5d7`.
- Independent rebuild of the builder's formula
  (`bytearray((i*7+3)&0xFF,512)` + b[0]=b[1]=b[7]=b[256]=0) reproduces the
  sha exactly; the five committed `r69-author/probes/` copies are the same
  bytes. b[0]=b[1]=b[7]=0 verified on the committed members.
- Measured named-arm verdicts on identical bytes — raw `sox -V6` per arm
  AND the five committed receipts agree:

  | member | file | fifo_path | stdin_pipe / redirected_fd |
  |---|---|---|---|
  | .wav | `RIFF header not found` (2) | `RIFF header not found` (2) | `can't determine type of '-'` (2) |
  | .bin | `no handler for file extension 'bin'` (2) | same | `can't determine` (2) |
  | .txw | `invalid filetype ID in input file header, != LM8953` (2) | `input must be a file, not a pipe` (2) | `can't determine` (2) |
  | .f32 | decode **128 samples** (0) | decode 128 (0) | `can't determine` (2) |
  | .snd | detected `sndr` → decode **504** (0) | detected `sndr` → decode 504 (0) | `can't determine` (2) |

  Named-arm groups: **6 distinct** ({wav-reader, bin-no-handler,
  txw-header-fail, txw-pipe-refusal, f32-decode, sndr-decode}) ≥ claimed ≥3;
  `.txw` internally 3-groups. Detection NULL on all `.wav/.bin/.txw/.f32`
  arms and every anonymous arm. Matches `matrix-r69.json` and the receipts.

## Claim 2 — `.snd` = first detection-fork member: **AGREE**

- Receipt field fork: `sox_detected_format` = `"sndr"` on {file, fifo_path}
  vs `null` on {stdin_pipe, redirected_fd} — in both the committed receipts
  and my fresh receipt (byte-identical, sha `80f6d64b…`).
- Raw stderr byte-level: `sox INFO formats: detected file format type
  'sndr'` printed on the file arm and on a real fifo (mkfifo + one-shot
  write + 1.0 s linger); absent on `cat member | sox -V6 -` and
  `sox -V6 - < member` (both `can't determine type of '-'`, exit 2).
- Gate verified in the verified table copy
  `corpus/live/r64-reviewer/r64rev-formats.c`: L247
  `if (ext && !strcasecmp(ext, "snd"))` → L248
  `CHECK(sndr, 7, 1, "", 0, 2, "\0")` — the ONLY ext-gated row of 131
  parsed. Committed `check_table.py` evaluator (which DOES return sndr —
  see nits): `first_match(member_bytes,'snd')` → row 130; `wav/bin/txw/f32/
  au/None` → None.
- "First" verified empirically, not just asserted: scanning every committed
  receipt's `transport_axis` (4929 receipts), the ONLY member whose
  detection differs across arms is `live/round-69/extsuffix_nomatch.snd`
  ({None, sndr}) — it is the first AND the only one to date.

## Claim 3 — ledger 119 rows, 49/70, 0 UNPARSED, prior-114 byte-stable: **AGREE**

- My full replay (`run_ledger_v.py`, author's 119-mode order verbatim):
  **49 exit-0 / 70 exit-1 / 0 UNPARSED**; exit sequence and TSV column-4
  failure summaries position-identical to committed `ledger-r69.tsv`
  (0 mismatches on both).
- Committed-state check: the author's 114 prior-mode receipts (committed at
  their r69 stamp paths) are **byte-identical to the committed r68 receipts —
  114/114, 0 diffs**. Prior-114 TSV exits+failsums vs r68 TSV: 0 mismatches.
- My fresh receipts vs the author's committed 119: **106 byte-identical**;
  13 differ — all resolved as receipt-embedded absolute input paths: the
  `sox_{stat,bridge,native}_stderr` fields are `tail[-1][-160:]` windows of
  stderr lines containing the input's absolute path, and my env path is
  +25 chars (`/r69-verifier/measure-env`), shifting the slice start.
  Reconstructive proof on row 21: the same `sox` leg on canonical vs env
  paths produces stderr lines identical after path normalization, and each
  receipt field is exactly the `[-160:]` window of its own run's line
  (verified both directions). Post-path error text identical on all 13
  rows; rows 36 + 114 become fully byte-identical after infix→canon
  substitution. Exits, verdicts, detected formats, sample counts: all
  identical — no semantic drift. (The r69-baseline seat's `compare.py`
  anticipates exactly this as `normalized` status.)

## Claim 4 — five new probes deterministic, fork via `failures`, exit 1: **AGREE**

- Each `--probe-transport-extsuffix-<ext>-r69` exited 1 in my replay with
  the fork reported in `failures` — committed receipts carry the same
  `transport: detection+decode verdict forks across transports (...)` entry.
- Determinism: the 5 committed copies per mode are single-sha each; my 6th
  independent run is byte-identical for all five —
  wav `e0d10839…`, bin `68d21799…`, txw `8bfbfe67…`, f32 `a89d6fcf…`,
  snd `80f6d64b…` — matching the report's claimed shas exactly.

## Claim 5 — dead-CHECK census numbers: **AGREE** (numbers only, per brief)

Independent rerun of the author's method (own driver `census_v.py`,
reusing the committed `check_table.py` evaluator):

- Pre-integration set (`git ls-tree -r 7b8d423 corpus/live/runs`):
  **4670 receipts, 79398 measurement entries, 126 distinct inputs,
  0 missing, 0 recorded-vs-evaluated mismatches** — rows_hit =
  `gsrt` L81 (×3 inputs), `txw` L86 (×1), `hcom` L90 (×3), `act` L93 (×13),
  `wav` L95 (×105) = **5/130 live** (125 never-first-match). All numbers
  identical to committed `census-r69.json`.
- HEAD set (4929 receipts): **6/130** — `sndr` row 130 (L248) flips
  dead→hit, n=1 input = `live/round-69/extsuffix_nomatch.snd`.
- Table structure: 131 CHECK rows, 130 live, 1 compiled-out (`adx` inside
  `#if 0`), 1 ext-gated (`sndr`). Deadness interpretation per the critic's
  caveat (coverage bookkeeping, `wma` the only dead-by-construction row) —
  not re-adjudicated; the receipt numbers stand as stated.

## Claim 6 — diff additive-only, prior members/receipts byte-stable: **AGREE**

- `git diff 7b8d423..30bb86d`: **2255 additions / 4 modifications / 0
  deletions**. The 4 M: the two fixture scripts + the two disclosed
  `__pycache__` regenerations. No prior member, receipt, seed
  (`corpus/knowledge/seed.md`), manifest, or knowledge file touched.
- `build_artifacts.py` +46/−1: the −1 is the dispatch `elif` line re-emitted
  with the r69 arm prepended — additive semantics, verified.
- `measure_audio.py` +49/−3 (see nit): the 3 replaced lines are the
  mutual-exclusion sum, `mode` chain head, and `suffix` chain head — same
  expressions with the five flags prepended newest-first; no prior path,
  mode string, or helper altered. `TRANSPORT_R69_MEMBERS`, the five
  argparse flags, the five forwarding splats, and the r69 arm block are all
  pure additions.
- Members committed at `corpus/live/round-69/` (tracked at HEAD) and
  byte-identical to builder output (independent rebuild verified).

## Nits (non-blocking)

1. Report says `measure_audio.py` "+52/−3" — `git diff --numstat` reads
   **+49/−3** (52 total changed lines counting the 3 rewritten chain lines
   on both sides; `git show --stat` displays "52 +-"). Cosmetic.
2. Report prose says the compiled-out `adx` row sits at "L136" — actual is
   **L165** (`#if 0` at L164); the author's own `census-r69.json` records
   `line: 165`, so this is a prose typo, not a data error.
3. The r69-critic report asserts the author's `check_table.py`
   `first_match()` "cannot return sndr" (literal-decoding bug). That is
   **not true of the committed copy**: it pads literals with the implicit
   NUL (`check_table.py:152-160`) and my direct run returns row 130
   (`sndr`) on the member bytes under ext `snd` — the critic likely
   evaluated a pre-fix revision.

## Replay artifacts (this seat's scratch)

`corpus/live/r69-verifier/`: `run_ledger_v.py`, `ledger-r69v.tsv`,
`ledger-stderr.log`, `census_v.py`, `census-v.json`, `measure-env/`
(44 MB frozen copy + 119 fresh receipts under `measure-env/corpus/live/runs/`),
`fifos/` (mkfifo scratch, cleaned).

Verdict: **AGREE on all 6 claims.** Zero subagents, zero commits,
zero edits outside scratch + this report.
