# Round 65 — simplifier: minimality audit of the preemptor-ordering landing

Seat: **simplifier** (leaf, report-only — no tracked edits). Host: devin. Worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` → `~/Projects/shokunin/audio-shokunin`
(canonical repo). Brief: judge whether the author's landed r65 tracked surface is the
minimal expression of the measured preemptor-collision ordering; keep/drop per landed
element; flag (not add) missing adjacent-boundary bytes, missing double-collision
controls, unpinned claimed-ordering arms.

**Landing status at write time**: author's diff is landed as uncommitted working-tree
state on HEAD `b1e286c` (r64 adjudication): `build_artifacts.py` **+40/−1**,
`measure_audio.py` **+65/−4**, `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav`
(4 × 11,588 B), plus uncommitted run receipts under `corpus/live/runs/20261014T*`.
Author report `reports/round-65/r65-author.md` landed. I audit the working-tree diff.

## TL;DR verdict

- **The 4-member family is minimal for the claimed ordering.** The measured order is
  `gsrt ≺ hcom ≺ act ≺ wav`; the tracked members are exactly {control `act`, gsrt arm,
  hcom arm, gsrt-vs-hcom arm}. Removing any member unpins one arm of the claim. No
  redundant pair, no dead flag, no oversized comment.
- **The one literal byte-duplicate is load-bearing.** `pair_preempt_act.wav` is
  byte-identical to `round-63/pair_route_84.wav` (SHA `cf5edecce1812f0a…`, both
  verified here) — kept correctly: it is the co-located control that makes each
  collision pair's "sole differing span" locally checkable, it yields a fresh
  act-routed receipt under the r65 code path, and the alternative (cross-round file
  reference) would break the per-round self-contained builder convention endorsed
  at r64.
- **Every harness field is consumed.** The forced `-t act` (bridge) and `-t wav`
  (native) legs both discriminate: bridge records the no-rescue counterfactual
  (`premature EOF` on all colliders — ffmpeg's own probe re-runs the collision,
  hcom scores 100 > wav 99), native discriminates members by stderr
  (`file encoding 0x622e` on gsrt-shaped vs `number of valid bits exceeds…` on
  hcom-shaped). `decode_error_tool` is new and disambiguates which child died.
- **Drop verdicts: none.** Nothing in the +105/−5 is deletable without losing a
  receipted ordering arm.
- **Optional adds flagged** (sharpening, not completion): a single-byte
  adjacent-boundary member per signature; a decodable-family hcom pair; preemptor
  len-gate edges. Details below.

## Independent re-derivation (needed to judge "minimal")

Built my own probes in `corpus/live/r65-simplifier/probes/` (builder
`make_probes.py`, 22 variants on the same `round-63/pair_route_84.wav` base plus
257-B shells and adjacent-offset/lone-conjunct/act-byte mutants). Authoritative
receipt `sox -V4 … -n stat` `detected file format type` line; decode =
`sox <f> -t f32 -`. Results (`probe-table.txt`, logs `logs/`):

| probe | detected | decode exit / stderr tail |
|---|---|---|
| s_act_base (control) | act | 0 (bridge decodes; pcm_s24le) |
| s_gsrt_act (RIFF+`ring.bin\0`@16+0x84@256) | **gsrt** | 2 `premature EOF` |
| s_hcom_act (RIFF+`FSSD`@65+`HCOM`@128+0x84) | **hcom** | 2 `bad compression type` |
| s_gsrt_hcom_act (all three sigs) | **gsrt** | 2 `premature EOF` |
| s_gsrt_nonul / s_gsrt_short8 / s_gsrt_off15 / s_gsrt_off17 | act | 2 (fmt destroyed → bridge EOF) |
| s_hcom_{fssd64,fssd66,hcom127,hcom129,fssd_only,hcom_only} | act | 0 (bridge decodes) |
| s_gsrt_act83 / s_gsrt_act85 / s_hcom_act00 | gsrt / gsrt / hcom | 2 — preemptor ignores byte-256 value |
| m_gsrt_act.bin / m_hcom_act.bin (257-B shells) | gsrt / hcom | 2 (`bad sampling rate divisor` on hcom shell) |
| m_256_gsrt.bin (256 B < 257) | gsrt | 2 — act unreachable anyway |

Convergent with r65-scout (20 probes), r65-author (19 variants) and r65-critic
(~37 variants) — four derivations agree: preemptor wins on every file satisfying
its predicate; `gsrt` wins over `hcom`; no fallthrough (reader failure is
terminal, exit 2); post-act rows (avi/ftyp, scout) lose to act.

Then ran the landed flags **end-to-end in a scratch replica**
(`r65-simplifier/replica/corpus/` — the two working-tree scripts copied under a
replica ROOT so receipts/artifacts write inside my scope only): all four
`--probe-ui-preempt-{act,gsrt,hcom,both}-r65` modes exit 1 with complete receipts;
rebuilt fixtures SHA-identical to the tracked files (`act cf5edecc…`, `gsrt
477bd371…`, `hcom bfc61413…`, `both a37adc7c…`); receipt fields match the author's
own committed-path receipts field-for-field (act→`detected act`/ffmpeg/exit0/
3,839; gsrt→gsrt/native/exit2; hcom→hcom/native/exit2; both→gsrt). The `act`
member's receipt also reproduces r63's `pair_route_84` receipt on every
comparable field (pcm_s24le/24b/0.080 s/centroid 12,046.98293255464/same 4-gate
failure list) — byte-identical input, identical measurement.

## Landed diff audit — keep/drop per element

`build_artifacts.py` +40/−1: `build_ui_preempt_r65_probe()` (re-synthesizes the
shared r63/r64 payload, pins `blob[256]=0x84`, applies signature spans), four
argparse flags, newest-first `if` dispatch head (`main()` + builder, same shape
as r64's branch). `measure_audio.py` +65/−4: four flags, exclusion-sum extension,
four forwarding lines, one ~48-line measurement block at the newest-first head,
`mode`/`suffix` chain heads prepended. The −5 lines are chain/sum rewrites —
no symbol or behavior removed.

| element | verdict | reason |
|---|---|---|
| `pair_preempt_act.wav` | **keep** | in-family control; disclosed byte-duplicate of r63 `pair_route_84` — anchors sole-span pair diffs + fresh act receipt; cross-round reuse would couple builders |
| `pair_preempt_gsrt.wav` | **keep** | gsrt>act arm; sole 9-B span diff @17–25 vs control (cmp -l verified) |
| `pair_preempt_hcom.wav` | **keep** | hcom>act arm; sole 8-B diff @66–69+129–132 (cmp -l verified) |
| `pair_preempt_both.wav` | **keep** | the double-collision control: hcom↔both differ only in the gsrt span and detection flips hcom→gsrt — the gsrt≺hcom arm exists only because this member exists |
| builder comment (9 lines) | **keep** | carries the measured ordering, the sig literals, and the byte-identity disclosure; proportional to r64's comment convention |
| measure-block comment (6 lines) | **keep** | documents why the forced legs exist (counterfactuals) — reader-facing load-bearing |
| `-V6 … stat` route probe | **keep** | the discriminating receipt: detected format + samples + exit |
| `-t act` bridge leg | **keep** | records the no-rescue counterfactual (`premature EOF` on colliders even when forced — ffmpeg re-scores hcom>wav internally); new evidence vs r64's block |
| `-t wav` native leg | **keep** | uniform exit 2 but stderr discriminates per member (`0x622e` vs valid-bits reject) — proves the intact-vs-destroyed fmt underneath |
| `try/except CalledProcessError` wrap | **keep** | collider members fail inside `measure()`'s first child call; without the wrap the mode would be a receiptless crash (r62-established hazard) |
| `decode_error_tool` field | **keep** | colliders die at ffprobe (container unreadable), not sox — names which child raised; self-describing receipts |
| `sox_detected_format`/`sox_route`/`*_stderr` tails | **keep** | all consumed; `sox_route` derived as `(detected=="act") or (ffmpeg)∈stderr` — correct on all four members |
| 4 flags + sum-guard + forwarding + dispatch + mode/suffix heads | **keep** | 1:1 flag↔file↔receipt ledger symmetry; newest-first placement consistent; exclusion guard verified present |
| ASLR ` @ 0x…` strip in error entries (author-disclosed) | **keep** | makes the new receipts byte-deterministic across runs — a correctness fix inside the diff |

**Nothing deletable.** Rejected-as-worse alternatives checked: (a) 3-member set
{gsrt,hcom,both} — loses the act-routed control receipt and co-located pair base;
(b) {act,gsrt,hcom} — leaves gsrt≺hcom receiptless; (c) reusing
`round-63/pair_route_84` as the control — saves 11.6 KB but breaks the
self-contained per-round builder convention (r64 simplifier precedent) and the
flag→own-round-path ledger pattern; (d) span-mutant single-byte members *instead
of* signature members — would pin edge bytes but lose the clean
presence-vs-absence ordering pair.

## Flag-for-add candidates (sharpening, NOT defects; do not add myself)

1. **Single-byte adjacent-boundary member per signature.** Tracked pairs
   discriminate at span granularity (9 B / 8 B). Author's own scratch proves
   every edge byte load-bearing (`b_gsrt_m23`, `b_gsrt_x24` NUL-term,
   `b_hcom_x65`, `b_hcom_x131`, lone conjuncts → all detect `act`). One tracked
   member differing from `pair_preempt_gsrt` at byte 24 alone
   (`ring.bin\x80` → `act`) would make the gsrt pair single-byte-sharp and pin
   the NUL conjunct in tracked form; symmetric `FSSE`/`HCOX` members do the same
   for hcom. Cost: +1–2 files, +1–2 flags.
2. **A decodable-family hcom pair** (scout's `pcm_hcom_act` ↔
   `pcm_hcom68x_act`, 1,068-B fmt-16 PCM, sole byte-68 diff — I verified the
   cmp and the detection flip). On the landed valid17 family the preempted
   member is structurally un-decodable anyway (gsrt destroys the chunk walk;
   the family is native-rejected regardless), so the pair isolates ordering but
   not "would have decoded anyway." The fmt-16 pair shows a fully decodable
   (`-t wav` → 2,048 B) file suppressed purely by detection — the sharpest
   preemptor-wins demonstration available. Optional second family; the landed
   set already satisfies the mandate.
3. **Preemptor len-gate edges** (gsrt 24|25, hcom 131|132). Scout scratch:
   25 B fires gsrt / 24 B falls back; 132 B fires hcom / 131 B falls back.
   I re-confirmed hcom-131 → `wav` on a RIFF body (3× `sox -V4`). Note for the
   verifier: r65-critic's `results-final.tsv` carries a stale row marking its
   131-B `E1b` as `hcom` — its report text (line ~165) and my re-run both say
   `wav`; the TSV row predates a file regeneration. Not part of the ordering
   claim proper; optional.
4. **Post-act shadowing arm** (avi `AVI `@8 / ftyp `ftyp*`@4 co-match → `act`
   still wins; scout scratch). Beyond the declared pre-act scope; would complete
   the "one CHECK row among several" picture in the other direction. Optional.

## Nits (none discrimination-affecting)

1. `sox_exit_code` on collider members records **ffprobe's** returncode (1), not
   sox's — `measure()`'s first child call is ffprobe; `decode_error_tool`
   disambiguates so it is self-correcting in-receipt, but the field name
   mislabels the failing tool's code.
2. `sox_{stat,bridge,native}_stderr` tails embed absolute repo paths — the
   r62/r63-disclosed same-host byte-identity caveat, now at three more sites.
3. `__pycache__/*.pyc` diff — mechanical `py_compile` regeneration; standing
   disclosure since r62, parent decides.
4. Author ran the 96-command ledger plus visible re-runs
   (`runs/20261014T0140*`, `0142*`, `0143*`, `0145*` preemptor/normal sets) —
   superseded receipts remain untracked in `runs/`; dedup is the parent's
   integration concern, not tracked-surface weight.
5. No `lsp` device exists on this substrate — the diff removes no symbols
   (the −5 lines are chain/guard rewrites verified by `git diff`), so no
   deletion candidate required reference-proving this round.

## Preserved contract

- Prior tracked fixtures and ledger rows byte-stable: `git status` shows no
  modified tracked content outside the two scripts + `__pycache__`; r63/r64
  pair files untouched (SHAs re-verified: `pair_route_84` `cf5edecc…` present
  and identical as round-65's control).
- Author reports prior-92 receipts byte-identical to r64's and normal-run
  receipt byte-identical; consistent with my replica runs producing identical
  JSON deterministically.
- One convention, not two: naming (`pair_preempt_*`, `--probe-ui-preempt-*-r65`),
  flag shape, newest-first dispatch, receipt schema all follow the standing
  r57–r64 pattern.

## Scope / housekeeping

All findings host-specific (SoX_ng 14.8.0.1 + ffmpeg/ffprobe n9.0.1, devin).
Writes this round: this report +
`corpus/live/r65-simplifier/{make_probes.py, probes/*, logs/*, probe-table.txt,
replica/**}`. No commits, no pushes, no tracked edits, no subagents, no sibling
writes. Working tree otherwise as the author left it.
