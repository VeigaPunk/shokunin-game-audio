# r101 CriticR101 — wave-1 adversarial review of C1 ledger truth and C3 probe design (read-only seat; transcribed verbatim by the L1)

Seat: `W2RoundAudio-8.CriticR101-2` (critic, lane-dispatched — still the lane). Scratch `/tmp/r101-critic/` (not evidence).

L1 note: the critic's table lists 'no fold commit' for 87/88; the scribe verified fold `1977cf42` (`r87+r88 fold: land pwbind/btwit defect fixes (+310/-112)`) is an ancestor of `defbe128` (`reports/round-101/r101-scribe.md`). The critic's C1 landed-text check ran before ExecLedger landed; wave 2 re-checks it.

**Axes reviewed:** C1 calibration (ledger truth); C3 depth/calibration (probe validity and regression safety). Read-only; inspected at HEAD `defbe128`. `A` = ancestor, `N` = not an ancestor, checked with `git merge-base --is-ancestor`.

| Round | Adjudicator path:line and verdict, or none | Verifier evidence | Cited landing/fold commit ancestry |
|---|---|---|---|
| 87 | None | `r87-verifier.md:20` — **GATE FAIL — NOT VERIFIED as a reproducible green landing.** | `d1e687b9` A; no fold commit |
| 88 | None | `r88-verifier.md:20` — **GATE FAIL as a reproducible green landing — PASS on every encoded law.** | `c19bec96` N; no fold commit |
| 89 | `r89-adjudicator.md:3-4` — **ADMIT-with-findings**, closed at `5755be5b` | `r89-verifier.md:22` GATE FAIL; `r89-reverify.md:20` GATE PASS | `f1ef7071`, `5755be5b` N |
| 90 | `r90-adjudicator.md:3` — **ADMIT-with-findings + foldfix contract** | `r90-verifier.md:17` — **PASS on committed bytes.** | `f50cf66a`, fold `753f13a6` N |
| 91 | `r91-adjudicator.md:3-4` — **ADMIT-with-findings + required fold** | `r91-verifier.md:29-39` — 128/128 checks on one green run; 2/6 family executions red | `d78f1cc9` N; required fold open |
| 92 | `r92-adjudicator.md:3-4` — **ADMIT-with-findings + required fold** | `r92-verifier.md:24` — **GATE PASS on committed bytes — with one substantive finding…** | `ccbce758` N; required fold open |
| 93 | None | `r93-verifier.md:49` — one green run; advisory, not an admission | `bb177513`, `d7a702d3` N; `4e0614f836…` is a source SHA, not a commit |
| 94 | `r94-adjudicator.md:3-4` — **ADMIT-with-findings** on `aaf56d30` | `r94-verifier.md:18` — **PASS on committed bytes.** | `aaf56d30` N |
| 95 | `r95-adjudicator.md:3` — **ADMIT-with-findings**, author `ffeb5155` → foldfix `6ba0201c` | `r95-verifier.md:22` — **PASS on committed bytes, with two armed-cell findings…** | `ffeb5155`, `6ba0201c` N |
| 96 | `r96-adjudicator.md:3-4` — **ADMIT-with-findings + required fold** | `r96-verifier.md:19` — **PASS on committed bytes.** | `7358f13b` N; required fold open |
| 97 | `r97-adjudicator.md:3-4` — **ADMIT-with-findings + required safety fold** | `r97-verifier.md:22` — **PASS on committed bytes, with six recorded findings…** | `b8ff4efc`, `8332b001`, `81b268f7` N |
| 98 | None | `r98-verifier.md:38-39` — one rc 0 run; advisory, not a gate decision | `d41cfa68`, `bb177513`, `d7a702d3` N; `72b23e04…` is a source SHA |
| 99 | None | `r99-verifier.md:29-30` — one rc 0 run; advisory, not an admission | `bb177513`, `e302dbce` N; `9f242022…` is a source SHA |
| 100 | None | `r100-verifier.md:36-40` — rc 0, explicitly not complete coverage | `fbd942cb`, `110638d4` N |

**C1 landed-text check:** no `## Round 87 verdict`–`## Round 100 verdict` sections are present in `SCORECARD.md`, so there are no landed sections to compare for over-claims, dates, or pointers. `LOG.md` also has no Round 87/88 entry, so the required verbatim GATE FAIL records are absent. No existing LOG `ADMIT` bullet without an adjudicator was found. Keep `LOG.md:1542-1546`’s R99 disclosure erratum (at least three recorded LAN controls, including TX deltas 7205/6376/6034) visible in any eventual R99 record. The R93 entry-cleanup note at `LOG.md:1570-1578` claims no full-family or clean-closure result. **Trap:** R89’s adjudicator closes at `5755be5b`, which is not an ancestor of this HEAD; don’t present that pin as current lineage.

**C3 counterexample:** for a stationary 12 kHz sine sampled at 48 kHz with phase π/4, sample peak is \(A/\sqrt2\), continuous peak is \(A\), so the ideal overshoot is \(20\log_{10}(\sqrt2)=3.01030\) dB. At amplitude 0.9, ideal sample/true peaks are −3.92545/−0.91515 dBFS. In a synthesized PCM16 WAV, FFmpeg n9.0.1 `ebur128=peak=true` measured:
- Abrupt onset: sample −3.92563 dBFS, TPK −0.3 dBFS (**+3.626 dB**, not +3.01).
- With a 5 ms fade-in: TPK −0.9 dBFS (**+3.026 dB**, consistent within FFmpeg’s 0.1 dB display rounding).
- Negative-control phase 0, abrupt onset: sample −0.91550, TPK −0.5 (**+0.416 dB**); with the same fade, TPK −0.9 (**+0.016 dB**).
- A full-scale first-sample transient masks the sine: sample −0.00027, TPK −0.0.

**Ranked risks and correction:** (1) **Fixable control defect:** onset/filter startup changes both positive and negative controls. Fade or pad before the measured steady-state region; derive expectations from the quantized control WAV. (2) **Vacuous pass risk:** current `measure()` maps a missing loudness match to `None` (`measure_audio.py:84-88`); the new probe must fail/block on missing or ambiguous TPK output, and require all 17 artifacts plus controls to have numeric measurements. (3) **Regression risk:** the normal-receipt pin is `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` (SCORECARD r81–r83). Opt-in wiring avoids changing it only if the normal `measure()` and receipt path remain untouched; verify against that pin. No `probe-truepeak-r101` code or test file is present at this inspection, so no additive diff was available to review. The control flaw is correctable; it is not by itself a reason for the canonical judge to reject the round.
