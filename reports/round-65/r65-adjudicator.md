# r65 Sol adjudicator — audio lane, wave `shokunin-train-20261013-w4`

Adjudicator: Sol (parent session), host devin, 2026-10-14. Scope: round 65 declared coverage move — map the pre-act autodetect preemptor ordering on RIFF files; pin a tracked preemptor-wins collision pair; prior ledger rows + fixtures byte-stable.

## Declared claim (verbatim)

"map the pre-act autodetect preemptor ordering on RIFF files … construct minimal RIFF+0x84@256 files that ALSO match each preemptor's predicate; measure empirically which detection wins and what reader/route it selects … if a preemptor-shaped file still routes act, that ordering claim is falsified and must be recorded as such. Pin at least one tracked RIFF-preemptor collision control pair where the preemptor wins; keep all prior behavior … byte-stable."

## Measured result

**CONFIRMED with critic corrections absorbed.** Total first-match-wins order measured on this host (SoX_ng 14.8.0.1, ffmpeg n9.0.1):

**`gsrt` ≺ `hcom` ≺ `act` ≺ `wav`** — every preemptor-shaped file detected the preemptor, never act (author 19 + scout 20 + critic 33 + scribe 36 constructions agree on every shared case). Only `gsrt` (`ring.bin\0`@16–24, len≥25) and `hcom` (`FSSD`@65–68 ∧ `HCOM`@128–131, len≥132) geometrically intersect the act trigger; post-act rows are shadowed.

**Critic corrections absorbed into the record:**
1. "Preemptor-detected ⇒ reader fails" is FALSE — an hcom-shaped file fully decodes 9 samples @22050 through the native hcom reader (exit 0); reader fate is field-walk + fd-seekability dependent.
2. `premature EOF` is not a reader signature — gsrt's checksum loop, au-on-empty-ffmpeg-pipe, and wav's non-fatal WARN variant all emit it; only `-V6` detection line or execve count disambiguates.
3. Seekability conjunct: gsrt's `premature EOF` on RIFF is a checksum loop driven by `RIFF`@0 read as BE `file_size` = 1.38 G words; on non-seekable fd the loop is skipped and the same bytes decode 88 samples @8 kHz.

Tracked surface: `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` (11,588 B each; `act` member byte-identical to r63 `pair_route_84.wav`, sole diffs exactly the signature spans: act↔gsrt bytes 17–25, act↔hcom 66–69+129–132); `build_artifacts.py` +40/−1, `measure_audio.py` +65/−4; ledger 86→96 rows (44 exit 0 / 52 exit 1).

## Adjudicator's own reproduction (committed tree, HEAD `1b0d276`)

`sox -V6` on all four tracked members: `act`→`` `act' ``+`(ffmpeg)` (exit 0); `gsrt`→`` `gsrt' ``+premature EOF (exit 2); `hcom`→`` `hcom' ``+bad compression type (exit 2); `both`→**`gsrt`** (the double-collision discriminator). `cmp -l` diffs byte-exact vs author report.

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r65-author.md` + tracked +40/−1 +65/−4 | 19-variant table, ledger 92→96, 92 prior receipts byte-identical |
| scout | `r65-scout.md` | ordering + geometric survey; len gates 25/132/257; `-t act` no-rescue (ffmpeg probes hcom=100>wav=99) |
| critic | `r65-critic.md` | 33 variants; ordering survives; TWO companion claims falsified (reader-fate, EOF-attribution) + seekability conjunct; absorbed |
| reviewer | `r65-reviewer.md` | r64 audit AGREE-all; zero latent preemptor collisions across 51 tracked fixtures + 7,999-file scan |
| baseline | `r65-baseline.md` | frozen `b1e286c` 92/92 rows, 44/48 exits, 86/92 byte-identical (6 path-coupled embeddings disclosed, anchor-compare equal) |
| simplifier | `r65-simplifier.md` | keep-all verdict; flagged optional adds (decodable-hcom pair, len-edge members) as sharpening candidates |
| scribe | `r65-scribe.md` | independent 36-fixture sweep convergent; knowledge draft → `corpus/knowledge/2026-10-14-sox-autodetect-preemptor-ordering.md` |
| boundary | pending at adjudication | report-only seat; scratch recon (stdin interplay, multi-preemptor, fallthrough targets) |
| verifier | `r65-verifier.md` | **AGREE all 5 claims** — committed-state replay, ledger 96 (44/52), sole diffs exact, hcom-decode counterexample reproduced |

## Disclosures recorded

- r65 run receipts left untracked while r64's were committed (tracking asymmetry — content verified byte-identical; noted for convention normalizing).
- `sox_route` dead `(ffmpeg)`-fallback logic on failed opens (non-blocking nit).
- Receipt stderr tails embed absolute paths — byte-determinism holds only same-root (pre-existing).
- `__pycache__` churn committed per lane convention (disclosed by author).
- Simplifier's optional adds deferred: single-byte adjacent-boundary members (24|25, 131|132), decodable-family hcom pair (`pcm_hcom_act`↔`pcm_hcom68x_act`), post-act shadowing arm — candidate next-round material.

## Per-axis verdicts

- **coverage: improved locally** — the autodetect surface grew from one pinned predicate to a measured total order with tracked collision controls + precedence semantics.
- **depth: improved locally** — reader-fate independence (detection ≠ accept), EOF non-attribution, and the seekability conjunct are now measured mechanics, not inference.
- **calibration: unchanged** — no thresholds/bounds touched.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

Single host; SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1; RIFF-family files only; ordering is detection-order empirical (disasm/source corroborative); no claims about preemptor readers' internal correctness, non-RIFF carriers beyond the measured 25-B gsrt shell, or other builds.
