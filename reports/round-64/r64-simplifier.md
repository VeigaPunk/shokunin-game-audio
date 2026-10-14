# Round 64 — simplifier: minimal-design critique of the valid-bits step-map pin

Seat: **simplifier** (leaf, report-only — no tracked edits). Host: devin. Worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` → `~/Projects/shokunin/audio-shokunin`
(canonical repo). Brief: critique the author's landed r64 diff — smallest boundary-pair
set for the step map, whether an existing pair family could carry the arm, anything
deletable without losing step-boundary discrimination.

**Landing status at write time**: the author's diff is landed as uncommitted working-tree
state on HEAD `5cc0eb0` (r64 interim): `build_artifacts.py` **+36/−1**, `measure_audio.py`
**+56/−4**, plus `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav` (6 × 11,588 B =
69,528 B) and 92-row ledger receipts under `corpus/live/runs/20261014T*`. Author report
`reports/round-64/r64-author.md` landed concurrently. I critique the working-tree diff
directly.

## TL;DR verdict

- **The set is minimal-and-correct under the mandate's literal reading.** The decoded
  *width* steps of the act-route map are exactly three: 8|9 (1B→2B), 16|17 (2B→3B),
  24|25 (3B→4B). Round-61's tracked `pair_valid_{16,17}` already pins 16|17 under the
  same route (both members carry 0x84@256). The r64 landing adds exact-adjacency pairs
  for the other two — {8,9} and {24,25} — plus {56,57} pinning the map's non-monotone
  re-entry (dead band → pcm_s64le island). Every decodable-width step in the sweep is
  now receipt-pinned at single-value adjacency; nothing landed is redundant.
- **Fixture minimality is maximal**: every r64 member differs from the tracked r63
  `pair_route_84.wav` at exactly one byte (1-based offset 39 = the valid-bits field);
  intra-pair diffs are that same single byte. I regenerated all six emitted blobs
  in-memory — SHA-256 identical to the working-tree files (`v8 bc9878f7…`, `v9 02887d11…`,
  `v24 714998b8…`, `v25 614845eb…`, `v56 d4ee4431…`, `v57 aa520464…`).
- **Existing families honestly reused, not duplicated**: r61's pair carries 16|17;
  r62's loose {24,32} straddle cannot pin 24|25 (any step in 25..32 fits) so a new pair
  was required; r63's pair is orthogonal (route predicate). No second convention was
  created — naming, flag shape, dispatch order all follow the standing pattern.
- **One optional completion, not a defect**: {32,33} — the staircase's cliff INTO the
  dead band — is the only boundary in the declared {1..48} sweep range left scratch-only.
  Its members would re-combine already-receipted behaviors (s32le at r62's valid32;
  premature-EOF at the new valid56), so its marginal evidence is adjacency-only. If the
  adjudicator wants every declared-segment edge receipt-pinned, it costs +2 files + ~15
  wiring atoms. The {64,65} island exit is the same shape, out-of-range, same argument.
- **Nothing in the +92/−5 is deletable without losing discrimination.** Per-field audit
  below; the notable micro-detail is that r63's sole deletable token — `stat` in the
  `-V6` route probe — is now *load-bearing* (it produces the `Samples read` count that
  carries the count-law evidence).

## Independent pin of the map (needed to judge "smallest")

Base = tracked `corpus/live/round-61/pair_valid_17.wav` (SHA `15cadf24…`, natural
0x84@256); I mutated only bytes 38–39 (wValidBitsPerSample, u16 LE) — the same field
the author sweeps — and probed each mutant with `sox -V4 -n` (detected format),
`sox -t f32 -` (decoded count), `ffprobe` (negotiated codec). Scratch:
`corpus/live/r64-simplifier/scratch/{sweep.py,variants/}`, rows in
`corpus/live/r64-simplifier/runs/sweep.tsv`.

| valid | detected | codec | samples | boundary |
|---|---|---|---|---|
| 0 | act | pcm_s16le | 5,760 | (0 = off-switch → container 16) |
| 1, 8 | act | pcm_u8 | 11,520 | — |
| 9, 16 | act | pcm_s16le | 5,760 | **8|9** u8→s16le |
| 17, 24 | act | pcm_s24le | 3,839 | **16|17** s16le→s24le |
| 25, 32 | act | pcm_s32le | 2,880 | **24|25** s24le→s32le |
| 33, 56 | act | — (ffprobe no codec_name) | exit 2 `premature EOF` | **32|33** s32le→NONE |
| 57, 64 | act | pcm_s64le | 1,440 | **56|57** NONE→s64le |
| 65, 128, 255, 65535 | act | — | exit 2 `premature EOF` | **64|65** s64le→NONE |

Convergent with the author's `results.tsv` (74 variants: all of 0..66 plus
{72,96,128,255,1024,32768,65535}, every row `OK` vs the predicted law) and the r64-scout
pre-sweep — three derivations agree. All my mutants routed `act` (0x84@256 inherited);
the dead-band members show the distinctive signature `detected act → ffmpeg child fails →
premature EOF` (codec absence at stream setup, not a route miss).

Map established: `pcm_u8` [1,8], `pcm_s16le` [9,16], `pcm_s24le` [17,24],
`pcm_s32le` [25,32], dead band [33,56], `pcm_s64le` island [57,64], dead [65,65535];
V=0 passes through to the declared 16-bit codec. The u8 class is a genuine count
*inversion* (11,520 > the native 5,760) — falsifying "reclassification only truncates".

## Landed diff audit — deletability

`build_artifacts.py` +36/−1: `build_ui_validbits_steps_r64_probe()` re-synthesizes the
r63 payload (`0.25·sin920 + 0.10·sin1380` ×8191, 5,760 frames — natural byte 256 = 0x5c,
verified) and pins `blob[256]=0x84` by assignment per member; six argparse flags;
one newest-first dispatch branch. `measure_audio.py` +56/−4: six flags, exclusion sum,
forwarding, one ~40-line measurement block, `mode`/`suffix` chain heads prepended.

- **Smallest discriminating pair set?** See verdict — exact-adjacency pairs at every
  decoded-width step, plus the one boundary where *both* members were receipt-novel
  ({56,57}: first premature-EOF entry + first s64le decode in tracked form). Six flags,
  one-file-per-receipt ledger symmetry preserved (86→92 rows, positions 2–7; totals
  44×exit0/48×exit1 verified — v9 is the sole clean-exit new member, which makes {8,9}
  additionally a pass|fail gate contrast on identical payload).
- **Is each pair's flank load-bearing?** Yes. Verified live on the emitted files:
  v8 act→pcm_u8/11,520 (native leg 5,760 — the only pair where both members decode
  natively, so the step is provably bridge-attributed, not header-inherent);
  v9 act→pcm_s16le/5,760 (native 5,760); v24 act→pcm_s24le/3,839 (native exit 2);
  v25 act→pcm_s32le/2,880 (native exit 2); v56 act→premature EOF exit 2 (native exit 2);
  v57 act→pcm_s64le/1,440 (native exit 2). Removing any member unpins its boundary.
- **Measure block per-field**: `route` probe (V6 + stat) yields detected/route-tag/
  samples/exit — all consumed (`sox_stat_samples_read` is the count-law receipt datum;
  `stat` is required for it — last round's redundant token is this round's evidence
  carrier). `native` forced-`-t wav` probe yields exit/samples/stderr-tail — all
  consumed, and it is what makes {8,9} discriminate *route* causation rather than
  payload/header causation. The try/except `CalledProcessError` wrap is load-bearing:
  member 56 fails inside `measure()`'s `check=True` sox call and would otherwise be a
  receiptless runner crash (r62-established hazard). `valid_bits` is name-derivable —
  one line, self-describing receipts, marginal keep.
- **`sox_route` expression is a quiet fix**: `(detected=="act") or b"(ffmpeg)" in stderr`
  — the detected-arm correctly labels member 56's *detected-but-failed* bridge as
  `"ffmpeg"`, where r63's stderr-only test would have mislabeled it `native` (the label
  wrinkle I flagged at r63 for `v17_c_wave8`). The `(ffmpeg)`-in-stderr disjunct is
  probably unreachable in this family (act is the only ffmpeg-bridge detector and the
  tag only prints on successful open) — ~20 chars of defensive depth, not worth removing.
- **Rejected-as-worse alternatives checked**: (a) *zero new fixtures* — mutate a tracked
  pair in-runner; loses emitted SHA-citable files, adds mutation code to the runner
  (r63's (a), unchanged verdict). (b) *Patch-from-tracked*: read `pair_route_84.wav` and
  rewrite bytes 38–39 — saves ~5 payload-synthesis lines but couples this round's builder
  to round-63's file surviving and breaks the per-round self-contained-builder
  convention; the inline re-synthesis is the right call. (c) *Three pair-flags* instead
  of six member-flags — saves ~15 atoms, breaks one-flag-one-file ledger symmetry
  (r63 precedent: viable, not required). (d) *Smaller payload/fewer members* — each
  member is a boundary flank; the pairs are already unit-minimal.

## Nits (none discrimination-affecting)

1. **Absolute repo path in receipt stderr** — `sox_stderr` and the new
   `sox_native_stderr` both embed `/home/vgpnk/Projects/shokunin/…`; r64 doubles the
   sites of the byte-determinism wrinkle flagged at r62/r63 (receipts are byte-identical
   only under the same checkout path). Optional `.replace(str(ROOT), "$ROOT")`.
2. **`results.tsv` `route` column** marks dead-band rows `?` while the receipt logic
   now calls them `"ffmpeg"` — the receipt label is more accurate (act IS the ffmpeg
   route even when the child fails); scratch-vs-receipt divergence is cosmetic.
3. **Transient sibling clobber observed and healed**: `corpus/live/r63-author/
   ledger-r63.tsv` was briefly rewritten mid-session by a wrong-cwd `run_ledger.py`
   re-run (86 rows → `UNPARSED … Errno 2`, `.shokunin/audio` path doubled); author
   preserved evidence at `corpus/live/r64-author/r63-ledger-clobbered-observed.tsv`
   and restored the file — it is clean at HEAD now. Process footgun worth noting:
   the ledger writer targets an absolute path while measure paths are worktree-relative.
4. **`__pycache__` churn** on both tracked `.pyc` — mechanical `py_compile`
   regeneration, same disclosure as r62/r63; parent decides.

## Housekeeping / scope

All findings host-specific (SoX_ng 14.8.0.1 + ffmpeg/ffprobe n9.0.1); the map is
per-file-family (11,588-B fmt40 extensible, block_align 2). No commits, no pushes, no
subagents, no sibling writes. Writes this round: this report +
`corpus/live/r64-simplifier/{scratch/sweep.py,scratch/variants/*.wav,runs/sweep.tsv,
runs/pair-probes.txt}`. Working tree otherwise untouched by me; the author's diff
remains uncommitted as landed.
