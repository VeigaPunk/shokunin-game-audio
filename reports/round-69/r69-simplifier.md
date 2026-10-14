# R69 simplifier — no deletions warranted: all five extsuffix members load-bearing (each is the sole rep of a distinct named-arm verdict class; .snd pins are individually required for the detection fork); claim CONFIRMED independently (named arm = 6 verdict signatures on identical bytes); prior-114 chain byte-intact

**Seat:** simplifier (delete-and-measure, not subjective trim).
**Diff measured:** author's working-tree landing at measurement time — `corpus/fixtures/measure_audio.py` +49/−3, `corpus/fixtures/build_artifacts.py` +46/−1, five members under `corpus/live/round-69/` (all sha256 `f073e70ad6e9d8c9f06697a9ca61d0a67bf4c351bcbe742c06c4a611d9d5e5d7`). Uncommitted at write time; parent integrates (r69-author.md "uncommitted working-tree, parent integrates"). Snapshot pinned at `corpus/live/r69-simplifier/author-snapshot/`; `cmp` re-verified unchanged at report time.
**Toolchain:** SoX_ng 14.8.0.1 (`/usr/bin/sox`), ffmpeg n9.0.1, Python 3.14.7, Linux x86_64.

## Verdict up front

The declared claim is **CONFIRMED**, reproduced here on TWO independent buffer
constructions (my own `\0\0`-prefixed scratch buffer, sha `54b3aa2a…`, and the
author's `(i*7+3)&0xFF`-ramp buffer, sha `f073e70a…`) — identical verdict
matrices on both, and my replica-tree runs of the landed code are
**byte-identical** to the author's committed ledger receipts for all five new
modes.

Named-arm verdict groups by extension alone on identical bytes — **6 distinct
signatures** (≥3 required): wav→`RIFF header not found`; bin→`no handler for
file extension 'bin'`; txw→{file:`invalid filetype ID … != LM8953`,
fifo:`input must be a file, not a pipe`} (the only member splitting the two
NAMED arms); f32→decode 128; snd→**detected `sndr`**, decode 504. `.snd` is
the first tracked member whose DETECTION field itself (`sox_detected_format`)
forks on transport name: `sndr` on {file, fifo_path} vs `None` on
{stdin_pipe, redirected_fd} — the ext-gated `sndr` CHECK row
(formats.c:247-248) fires only when the name resolves `snd`. Anonymous `-`
arms are can't-determine on all five members.

## What landed (census)

`measure_audio.py` (+49/−3 — measured `git diff --numstat`; author's report
says "+52/−3", a trivial miscount, critic agrees +49/−3):

- `TRANSPORT_R69_MEMBERS` dict (5 entries) + member-contract comment — same
  shape as `TRANSPORT_R67_MEMBERS`/`TRANSPORT_R68_MEMBERS`.
- 5 `add_argument` flags; +5 terms in the mutual-exclusion `sum()`; +5
  builder-forward splices (newest-first); r69 arm block prepended before the
  r68 arm (5-term member ternary → dict lookup → unchanged `transport_entry`);
  +5 terms each in `mode` and `suffix` chains. The 3 deleted lines are the
  routine chain rewrites (sum/mode/suffix) — extended, not altered.
- Wire census: each of `probe_transport_extsuffix_{wav,bin,txw,f32}_r69`
  referenced at 6 points (argparse 450, fwd 463-467, guard 643-645, member
  ternary 656-659, mode 1098, suffix 1118); `..._snd_r69` at 5 — member-select
  resolves snd by fallthrough, the established last-in-chain convention
  (r68's txw, r67's lengate_hcom_132 did the same).

`build_artifacts.py` (+46/−1): `build_ui_extsuffix_r69_probe()` writes ONE
512-B buffer to five names (loop), four byte pins (`b[0]=b[1]=b[7]=b[256]=0`)
over the r68 ramp; five flags; newest-first `if` arm (`main()`+builder), old
r68 `if`→`elif` (inert reorder — multi-flag invocation is already forbidden by
the mutual-exclusion sum).

Members: `extsuffix_nomatch.{wav,bin,txw,f32,snd}` — five real files, byte-
identical. **The differing extensions ARE the member contract.**

Untouched: `transport_leg`/`transport_matrix`/`transport_entry`/`transport_error`,
all ~110 prior arms, all prior member files. No census tooling tracked
(author's `check_table.py`/`census_check_rows.py`/`census-r69.json` live in
`corpus/live/r69-author/` scratch — correct scope).

## Delete-and-measure results

Replica `corpus/live/r69-simplifier/tree/` = `git archive HEAD` + author's
landed fixture/member overlay; replica receipts land inside the replica.

| # | Deletion candidate | Measured effect | Verdict |
|---|---|---|---|
| 1 | r69 arm block | `--probe-transport-extsuffix-snd-r69` exits 0 writing a receipt labeled `transport-extsuffix-snd-r69` containing the normal suite (replica `runs/20261014T110618562243Z-…`, hash `729a54d3…` vs real `80f6d64b…`) | **Load-bearing**; same silent-fallthrough hazard flagged in r68 — pre-existing convention for all ~113 flags, not introduced here. |
| 2 | `b[0]=0`/`b[1]=0` pins (with b[7]=0 kept) | `.snd` member: det `sndr`→`None` on all arms; verdict becomes `can't find Sun/NeXT/DEC identifier` on named arms (the registered `snd` ext-handler resolves — post-table fallback, not detection) | **Load-bearing** — claim part 2 dies. |
| 3 | `b[7]=0` pin alone (b[0]=b[1]=0 kept, b[7]→0x34 pattern) | Same collapse: `can't find Sun/NeXT/DEC identifier`, det None | **Load-bearing** — the sndr row needs ALL THREE conjuncts (`\0\0`@0 ∧ `\0`@7); each pin is individually required. |
| 4 | `b[256]=0` pin | Rebuilt member differs only @256 (0x03→0x00); `transport_entry` on the unpinned member yields **identical verdict groups** (det sndr, decode 504) | **Inert-but-justified** — act needs `RIFF`@0, already dead at byte 0; same ruling as r68's pin: one line documenting a real boundary. |
| 5 | `.wav` member | Sweep loses the identical-bytes control for the wav-reader class; r68's `posttable_nomatch.wav` pins the same verdict on DIFFERENT bytes — the declared move is "same bytes under different names" | **Load-bearing** (in-sweep anchor). |
| 6 | `.txw` member | Loses the only member where the two NAMED arms split ({file} reader-magic-fail vs {fifo} reader-seekable-gate) | **Load-bearing** — unique internal named-arm split. |
| 7 | `.bin` member | Loses the no-handler class (unregistered extension) | **Load-bearing** (declared move enumerates it). |
| 8 | `.f32` member | Loses the only decode-positive named arm routed purely by extension | **Load-bearing**. |
| 9 | `.snd` member | Claim part 2 dies outright | **Load-bearing**. |
| 10 | 512 B size (shrink e.g. .snd to ~10 B) | Rows are evaluated under `len >= p1+l1` — a sub-257 B member would let act(257)/hcom(132)/mpegts(189) rows pass by LENGTH-GATE, not byte-mismatch, weakening "no row matched" to "not evaluated" | **Load-bearing size** — 512 ≥ AUTO_DETECT_SIZE 257 keeps every live row genuinely evaluated. |
| 11 | Merge 5 flags → 1 sweep flag | Breaks row=mode=flag ledger convention (name derives from mode); saves ~5 argparse lines at the cost of a second convention | Not recommended. |
| 12 | Inline `TRANSPORT_R69_MEMBERS` / derive filename from member | Saves ~5 lines, discards the contract-comment location, diverges from R67/R68 map precedent | Not recommended (same as r68-#6). |
| 13 | 5 real member files → 1 file + 4 symlinks/hardlinks | Identical verdicts but weakens corpus (extraction/dedup hazards; builder writes real files); 2.5 KB is noise | Not warranted. |
| 14 | Reuse r68's `posttable_nomatch` bytes renamed | r68 buffer starts `u` — `first_match(bytes,"snd")` = None even under `.snd` (author's own `check_table.py` evaluator confirms) — the detection fork is unreachable on those bytes | **New buffer required** — not duplication. |

Strict-minimum note (for the record): the literal claim — ≥3 named groups +
a detection-fork member — is satisfied by any 3-member subset containing
`.snd` plus two of the others (e.g. {bin, f32, snd}). The declared axis-move
is verbatim a five-extension sweep; `.wav` and `.txw` each pin a named-arm
class (reader-verdict control; reader-internal split) no remaining member
covers. Keep all five.

## Byte-stability / preserved contract

- **Prior-114 replay**: independent `cmp`-semantic comparison of the r69
  ledger TSV (`corpus/live/r69-author/ledger-r69.tsv`, 119 rows, 49×0/70×1,
  0 UNPARSED) vs the r68 TSV — rows {1}∪{7-119}↔{1-114}: exit sequence
  position-identical and **all 114 receipt files byte-identical** (0/114
  mismatches). Author's own `compare_receipts.py` agrees ("114 prior-mode
  pairs checked, 0 mismatches").
- **New-mode determinism**: author's committed ledger receipts vs my replica
  runs — `e0d10839…`(wav), `68d21799…`(bin), `8bfbfe67…`(txw), `a89d6fcf…`(f32),
  `80f6d64b…`(snd) — all byte-identical; snd+txw each rerun-identical in
  replica. Author reports 5 runs each identical.
- **Member determinism**: replica rebuild of `build_ui_extsuffix_r69_probe()`
  regenerates all five members byte-identical (`f073e70a…` ×5 == committed
  members == author's scratch probes).
- **Spot replays (replica, post-diff code)**: `normal`, posttable-nomatch-r68,
  txw-piperefuse-r68, preempt-act-r67, dec-hcom-r66, route-act-84-r63,
  extensible-valid-8-r64 — all byte-identical to committed r68-ledger receipts.
- **Receipt-determinism surface**: all five members' `error`/`stderr_tail`
  fields are path-free (fifo tmpdir nonce never enters; `.bin`'s tail scrubs
  the ext to `<input>` by the `` `[^']*' `` regex — `error` keeps `bin`
  verbatim; `.f32` records `input clipped 65 samples`; `.snd` decodes 504).

## Census cross-check (dead-CHECK-row bookkeeping)

Author's census (`census_check_rows.py` + `check_table.py`): 131 parsed rows,
130 live (`adx` L165 compiled out by `#if 0`), 1 ext-gated (`sndr` L248);
evaluates every distinct input file in all 4,670 committed
`runs/*/measurements.json` receipts through the ordered table — **0
recorded-vs-evaluated mismatches**; **rows_hit = 5** (gsrt L81, txw L86,
hcom L90, act L93, wav L95), **rows_dead = 125**. My independent grep-scan of
the same receipts gives the same hit set (`act` 190, `gsrt` 86, `hcom` 88,
`txw` 8, `wav` 65 receipts; 8 null-detection receipt arms — the r68 member).
Post-commit the `.snd` receipts flip `sndr` L248 → hit (6/130).

Two scope caveats to carry (corroborating the critic): the census scope is
`runs/*/measurements.json` — committed non-receipt files with recorded
detections (e.g. `r63-critic/sweep_results.csv` RIFX/RF64 `wav` rows) are
outside it; and "dead" here means *never first-match in committed receipts*,
not unreachable — `wma` L238 is the only row dead-by-construction (identical
16-B GUID predicate to the earlier-ordered `asf` L174; verified:
`checkrows/wma.bin` → `detected 'asf'`). Twenty-eight other "dead" rows
detect fine on minimal-magic bytes — coverage debt, not dead code.

## Duplication / smaller-expression review

- No transport machinery duplication — the r69 arm calls the same
  `transport_entry` r67/r68 use; extracting a shared arm-runner would touch
  landed r68 lines (non-additive) for ~10 lines saved.
- Builder is already minimal (one buffer, one 5-iteration write loop, four
  documented pins).
- Tracked `__pycache__` `.pyc` churn — same disclosed mechanical regeneration
  as r62-r68; nondiscriminating tracked content the lane tolerates.

## Stop condition

The next deletion harms a claim: every member is the sole representative of a
distinct named-arm outcome class; the three sndr pins are individually
required for the detection fork; the 512 B size keeps the no-match predicate
evaluated rather than len-gated; and every structural element follows the
established per-round additive convention. No byte-identical extraction
demonstrated or warranted. **Deletions recommended: none.**

## Evidence index

- Scratch: `corpus/live/r69-simplifier/probes/extsweep.{wav,bin,txw,f32,snd}`
  (independent buffer sha `54b3aa2a…`), `matrix.json` (independent transport
  matrix, identical verdicts to author's `matrix-r69.json`).
- Replica: `corpus/live/r69-simplifier/tree/` (`git archive HEAD` + author
  overlay); variants `measure_audio_noarm.py`, `build_artifacts_nopin.py`,
  `build_artifacts_nosnd.py`; replica receipts incl. the mislabeled no-arm
  run `20261014T110618562243Z-transport-extsuffix-snd-r69` (hash `729a54d3…`).
- Snapshot: `corpus/live/r69-simplifier/author-snapshot/` (landed fixtures +
  member copies, `cmp`-reverified).
- Ledger: `corpus/live/r69-author/ledger-r69.tsv` (119 rows); prior-114
  byte-identity verified independently (0/114 mismatches, 0 exit diffs).
- Sibling corroboration: `r69-critic.md` (wma dead-by-construction + census
  scope caveats, both confirmed here), `r69-author.md` (mechanism + ledger).
