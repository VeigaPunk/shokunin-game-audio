# r94 VERIFIER — frozen-tree gate on committed `aaf56d30` (the SoX_ng effect lattice)

Seat: **verifier** (non-author, audio-shokunin r94). Lane
`~/Projects/shokunin/audio-shokunin`, basis **`git archive HEAD`**
(`aaf56d30`, "Merge branch 'wt-r94'") — the committed bytes, **not** the
worktree. Window **2026-10-16 08:54Z–08:59Z** (local UTC−3), loadavg
**53.9–54.6** at run start, 32 cores. Toolchain: `sox` = **SoX_ng v14.8.0.1**
(`/usr/bin/sox` sha256 `646d899b53c1…` — identical to the author's pin),
`ffmpeg` present, Python **3.14.7**, numpy **2.5.3**.
`TMPDIR=~/Projects/shokunin/tmp`. **Zero tracked writes by this seat, zero
commits, zero pushes, no `set-default-*`**; every artifact under
`corpus/live/r94-verifier/`. The frozen `probeParent` slot spawned no labrat
(the duty is a pure re-run/mutation gate and the family is file-only; no
empirical unknown required a second seat — disclosed, not silently skipped).

## 0. Verdict

**PASS on committed bytes.** Every cell the author landed re-derives green on
a frozen tree this seat built itself, twice, and the signature gate that pins
the lattice to the r94 scout's receipts is **live and sensitive**: witness
absence degrades to **146 named `coverage_blocked` cells** (never a green),
a forged witness sha turns the run **red with the two named legs**, a
fixture-side stimulus mutation turns it red at the root (**35 failures**), a
calibration-constant mutation turns it red on **8 metric arms**, and all
**11 receipt forgeries** this seat fabricated are caught by field
re-derivation (7 by `FAIL` laws, 2 by `BLOCKED`, 1 no-op control).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive HEAD` | tar sha256 `424ac63d73565814acce0cc655a803fed4613db71f589ae0f55da56607cdba2f` (3 317 524 480 B); **44 551 files / 11 772 dirs / 0 symlinks**; file-set symdiff vs `git ls-tree -r` = **0** | PASS |
| fixture identity | committed blob | sha256 `4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26` = the frozen-tree copy = the `HEAD:` blob = the worktree file at archive time | PASS |
| `py_compile` inside the frozen tree | clean | rc 0 | PASS |
| fresh runs on committed bytes | green | **2/2 green**: `20261016T085526073120Z-sox-r94` (08:55:23Z), `20261016T085534617516Z-sox-r94` (08:55:31Z); 8 entries, **150 legs**, `failures {}`, `coverage_blocked` empty in all 8 | PASS |
| declared leg count | 150 | **150** measured (45/15/22/12/20/11/12/13 — the author's table exactly) | PASS |
| law re-derivation (own laws) | armed law set | **253 laws × 6 receipts = 1518 cells**: green receipts **253/253 PASS each**; no law red on any committed-bytes run | PASS |
| independent live re-derivation | own code/argv/stimuli | **83 laws, 83 PASS** (own stimulus writer reproduces the scout's 9 prep shas; own RIFF reader; own band estimator) | PASS |
| signature gate — witness **absence** | named class, never green | scout receipts removed → `failures {}` **and 146 named `coverage_blocked` cells** (72 stimulus + 59 sha + 15 metric) | PASS |
| signature gate — witness **forgery** | red | one scout sha flipped → **2 named failures** (`det_gain_m6_D`, `gain_m6_rint`), rc 1 | PASS |
| gate sensitivity — fixture **stimulus** mutation | red | stim b 997.0→997.5 Hz → **35 failures** incl. 8 stimulus-root failures across all 8 entries | PASS |
| gate sensitivity — **calibration** mutation | red | `SOX_R94_BAND_OFFSET_DB` +1.0 dB → **8 metric-arm failures** (all five 0.05 dB tolerances) | PASS |
| receipt **forgery** suite | caught | 11/11 as designed: 7 `FAIL`, 2 `BLOCKED`, 1 no-op control (§6) | PASS |
| cross-run drift | none outside declared volatiles | **4 851 leaf comparisons, 1 difference** — the *recorded, not armed* `-G` default-path railed count (`14917` vs `14962`) | PASS (as declared) |
| custody / hygiene | file-only | 16/16 censuses `own_objects: []` / `own_modules: []`; live check 0 `r94*` sinks/sources/modules; default sink unchanged | PASS |
| zero tracked writes | none | `git status --untracked-files=no -- corpus/live/r94-verifier` = **0 lines**; the lane appears only as `??` | PASS |

**Doc-vs-measured:** every number the author's report declares was
re-measured and matches — **102** `_sox_r94_arm` call sites (103 grep hits
minus the `def`), **59** `_sox_r94_ref_arm` witnesses (60 − 1), **7**
`_sox_r94_ref_metric_arm` arms (8 − 1), **59** legs carrying a `scout_ref`,
**29/29** compared metric key-values, 150 legs, empty failures/blocked on
both green passes, and the cross-run residual it disclosed. Two counting
nuances are noted in §10; neither moves a verdict.

## 1. Frozen tree

`git archive HEAD` → `corpus/live/r94-verifier/r94v-head.tar` (3.3 GB, 2.5 s),
extracted to `corpus/live/r94-verifier/tree/` (`corpus/.gitignore` covers
`live/*/tree/`). Census **44 551 files / 11 772 dirs / 0 symlinks**;
file-set symdiff against `git ls-tree -r HEAD --name-only` = **0**
(`runs/r94v-symdiff.txt`). `python3 -m py_compile` on the tree fixture = rc 0.

The tree carries the **tracked** scout receipts
(`corpus/live/r94-scout/receipts/`, 18 JSON files incl. `prep.json` with the
9 stimulus shas) — so the cross-seat witness is exercised inside the frozen
tree rather than degrading. The author's own scratch (`corpus/live/r94-author/`)
is untracked and was **absent**, which is why the family rebuilt its stimuli
from source in every run below (the strongest form: self-sufficiency tested
on a fresh tree).

**Foreign state observed, not touched:** at 05:58 local a *concurrent r95
author seat* left this shared checkout mid-merge
(`.git/MERGE_HEAD` = `Merge branch 'wt-r95'`; `UU corpus/fixtures/measure_audio.py`;
worktree fixture now sha `5c7ee3d9ccb6…`, i.e. **no longer** the committed
blob). It postdates this seat's archive (05:54) and every run below ran inside
the frozen tree; this seat wrote nothing to the worktree, the index, or the
merge state.

## 2. Fresh runs on committed bytes

| run | receipt | host utc | loadavg | legs | failures | coverage_blocked |
| --- | --- | --- | --- | --- | --- | --- |
| A | `tree/corpus/live/runs/20261016T085526073120Z-sox-r94/measurements.json` | 08:55:23Z | 54.58 | 150 | `{}` | empty ×8 |
| B | `tree/corpus/live/runs/20261016T085534617516Z-sox-r94/measurements.json` | 08:55:31Z | 53.95 | 150 | `{}` | empty ×8 |

Per-entry: `sox_det` 45, `sox_gain` 15, `sox_rate` 22, `sox_remix` 12,
`sox_trim` 20, `sox_fade` 11, `sox_repeat_pad_silence` 12, `sox_dither_stat`
13. Each entry carries `pw_census_entry`/`pw_census_exit` with
`own_objects: []` / `own_modules: []` (negative control) and a host block
pinning `sox_sha256 646d899b53c1…`.

## 3. Law re-derivation — `runs/r94v_laws.py`

253 laws over the receipt's **recorded fields only**; the entry's own
`failures`/`coverage_blocked` lists are never an input to a law (two
receipt-level cross-checks at the end compare the derived red set with them).
Laws cover: the 9-stimulus signature gate; the determinism classes
(multi-sha vs single-sha, plus `out_sha256_all` ↔ `n_distinct_shas` ↔
`stable` internal consistency); the four byte-identity legs against the
**stimulus** sha; flag-order/buffer/client-env invariance; the concurrency
triples; gain/vol rounding (`mismatch_vs_rint_formula`, the ceil
discriminator, the 1-LSB `vol` spelling delta, the chain-order peaks); the
±1-frame length matrix and the `rules_fitting_all_half_rows == []` claim; the
whole alias lattice including the **disarm guard** (`rate_130db_home`);
remix/trim/fade/repeat/pad/silence sample laws; the dither envelope; the
`stat`/`stats -j`/`stat -freq`/`stat -e` field definitions; 59 cross-seat sha
witnesses and 15 cross-seat metric arms (29 key-values).

| receipt | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| A (green) | 253 | **253** | 0 | 0 |
| B (green) | 253 | **253** | 0 | 0 |
| forged witness (`tree-forgesha`) | 253 | 250 | **3** | 0 |
| calibration mutation (`tree-mutcal`) | 253 | 247 | **6** | 0 |
| stimulus mutation (`tree-mutstim`) | 253 | 224 | **29** | 0 |
| no scout receipts (`tree-norefs`) | 253 | 167 | 3 | **83** |

## 4. Independent live re-derivation — `runs/r94v_live.py` (83/83 PASS)

Own code only: own RIFF writer/reader, own sox argv, own band estimator, own
numpy cross-computations. Headline re-derivations (all against the author's
recorded fields and the scout's receipts):

- **Stimuli:** this seat's writer reproduces all **9/9** scout `prep.json`
  shas, and stimulus *a* equals the author's receipt sha.
- **Determinism:** default `gain -6` 5/5 distinct; `-D gain -6` 3/3 one sha
  **equal to both the receipt's and the scout's** `gain_D.json:gain_m6`
  (`d011774f2a3f0466…`); explicit `dither` 5/5 distinct, `-D dither` 5/5
  distinct, `-R dither` 3/3 one sha, `-R -D` ≡ `-R`; f32→s16 5/5 distinct,
  f32→s24 / f32→s32 stable; `gain 0`, the no-effect pass-through,
  `rate 48000`, `pad %50` byte-identical to this seat's own stimuli;
  `copy` → rc 2 `can't open input file`; flag order / `--buffer` / the
  PipeWire-pulse client env inert; a global option after the effect refuses
  rc 1.
- **Rounding:** own `gain -6` mismatch vs `rint(x·10^(−6/20))` = **0**,
  peaks `[−12.021, −18.041]`; `vol 0.5` ceil mismatch 0 with rint mismatch
  > 0; `vol 0.5 p` ≡ `rint(x·√0.5)` (0); the two `vol` spellings **23 000**
  samples apart, max **exactly 1 LSB**.
- **Rate:** all six lengths exact (`11025 / 11026 / 5512 / 6013 / 2756 /
  8000`); `rate 48000` identity; `rate -q -a` refusal with the exact message.
- **Alias lattice, convention-free** (every band level relative to the same
  leg's own peak, so the estimator constant cancels): `-q` fold sits
  **−6.14 dB** below its own peak (a hazard) vs the default's **−23.46 dB**
  rejection; `-a` is flat at 20 kHz (**−0.00 dB** rel. peak) with
  **−105.15 dB** rel. peak at 21.1 kHz; the 20 kHz-stimulus **default** row
  carries the deep floor (**−105.11 dB below its own 20 kHz tone**, vs
  −23.46 dB for the 23 kHz row) — i.e. the falsified "`-v` rejects at
  −130 dB" claim's real home re-derives without using the fixture's numbers.
- **Dither envelope:** own `-R dither -s` max **21**, RMS **5.740681** —
  identical to the receipt and to 1e-6 of the scout's.
- **stat:** own interleaved quadratic mean **0.279509** = sox's `RMS
  amplitude`; own interleaved max delta **0.728180** = sox's `Maximum delta`
  (not the per-channel 0.065277); `stat -freq` step **11.71875 Hz**, 6 144
  lines = 2048·3 windows on the 12 000-sample mono file; `stat -e` prints no
  `Integrated` on the 0.25 s mono file but does on the 1 s stereo file, while
  **ffmpeg's ebur128 gates the same short file to I = −70.0 LUFS**.
- **Hygiene:** 0 `r94v_`/`r94a_` PipeWire rows after the whole battery.

Estimator delta disclosed: on the `-q` row this seat's narrow-band estimator
reads 6.1 dB below the fixture's value relative to the same peak (the fixture's
`band_21100hz_db` ≈ its own peak level). This seat's estimator is exact on
synthetic tones (−6.173 dB for a 0.4913-amplitude tone, any of 1000 / 21 100 /
21 102.5 Hz), so the difference is a convention/bandwidth difference between
the two estimators on a *folded, non-stationary* product — the **law** (fold =
hazard within a few dB of peak vs ≥ 20 dB default rejection) is reproduced by
both.

## 5. Signature-gate sensitivity (four independent mutations)

Bases are `cp -al` hardlink copies of the frozen tree; every mutation **removes
and rewrites** its target file (never in-place), and the untouched tree's
fixture sha was re-checked afterwards (unchanged).

| mutation | what changed | measured outcome |
| --- | --- | --- |
| witness **absence** (`tree-norefs`) | `corpus/live/r94-scout/` removed | `failures {}`, **146 named `coverage_blocked` cells**: 72 × "stimulus X: no scout prep sha available", 59 × "<leg>: scout receipts absent at <path> -> cross-seat witness not armed", 15 × "<leg>: no scout metric recorded for <key> -> cross-seat metric law not armed". **No cell is a silent green.** |
| witness **forgery** (`tree-forgesha`) | `gain_D.json:gain_m6` recorded sha `d011774f…` → `0011774f…` | rc 1; **2 failures**: `det_gain_m6_D` and `gain_m6_rint` "cross-seat sha mismatch vs gain_D.json:gain_m6 (own d011774f… vs 0011774f…)" — the gate fires on the forged witness, and this seat's independent law set names the same two legs |
| **stimulus** mutation (`tree-mutstim`) | fixture stim *b* 997.0 → 997.5 Hz | rc 1; **35 failures** — the stimulus root is caught in all 8 entries ("rebuilt bytes differ from the scout's prep.json", own `fd691dcc…` vs `6a2a6b0c…`) plus 27 downstream sha mismatches; local (non-witnessed) laws still pass, i.e. the red is *pinned*, not noisy |
| **calibration** mutation (`tree-mutcal`) | `SOX_R94_BAND_OFFSET_DB` 2.5403 → 3.5403 | rc 1; **8 metric-arm failures** across the five 0.05 dB comparisons (e.g. `alias_23k_q` own −5.289 vs scout −6.289) — the estimator constant is *pinned by the witness*, not free |

The two halves matter together: absence must not read green (it does not — it
reads 146 named blocked cells), and a forged/incorrect witness must read red
(it does, on the exact legs).

## 6. Receipt forgery suite — `runs/r94v_laws.py --forge`

Base = the **green** run-A receipt (its `failures`/`coverage_blocked` are
already empty, so any law that fires is firing on *fields*, not on the
fixture's own verdict lists). 11 fabrications + 1 control:

| forgery | fabrication | caught by | result |
| --- | --- | --- | --- |
| `none` (control) | — | — | 253 PASS / 0 FAIL / 0 BLOCKED |
| `clear-failures` | blank every `failures`/`coverage_blocked` | — | 253 PASS (no-op on a green receipt; shows the lists are not the detector) |
| `flip-stable` | `det_gain_m6_D.n_distinct_shas=5`, `stable=false` | 2 laws (`nondeterministic`/`stable_field_consistent` vs `out_sha256_all`) | **CAUGHT (FAIL)** |
| `forge-sha` | identity leg's sha → `dede…` | 3 laws (identity vs stimulus + receipt cross-checks) | **CAUGHT** |
| `forge-band` | `alias_20k_default.band_21100hz_db = −60` | 3 laws (the `rate_130db_home` disarm guard) | **CAUGHT** |
| `forge-metric` | `gain_m6_rint.mismatch_vs_rint_formula = 17` | 2 laws (rounding + scout metric) | **CAUGHT** |
| `forge-text` | `stat_plain_a` RMS → 0.5 | 2 laws (field definition vs own numpy value) | **CAUGHT** |
| `pop-frames` | `trim_0_1s.frames = 4800` | 2 laws (the `s`-suffix law) | **CAUGHT** |
| `forge-stim` | stimulus *a* sha → `dede…` | 3 laws (stimulus signature gate + identity legs) | **CAUGHT** |
| `forge-scout-expect` | `scout_ref.expected_sha256` → `abab…` (own sha untouched) | 2 laws (match re-derived from own vs expected) | **CAUGHT** |
| `pop-scout-ref` | witness removed | 1 law | **BLOCKED** (never green) |
| `pop-coverage` | witness removed **and** both verdict lists blanked | 1 law | **BLOCKED** (never green) |

Residual, disclosed exactly as the r89 re-verifier did: a **fully
self-consistent receipt rewrite** (fabricated sha *and* a fabricated
expectation *and* blanked lists) is not detectable at receipt level. The
compensations are the ones this gate actually ran: the frozen-tree pin, two
fresh live runs, and §4's independent live re-derivation — which never reads
the receipt's verdict lists and rebuilt every witness from the scout's
committed receipts.

## 7. Cross-run drift (A vs B)

Structural walk of both green receipts: **4 851 leaf comparisons**, excluding
`wall_s`/`utc`/`loadavg`/`host*`/census counters and the **7 legs marked
`volatile_sha`** (`det_gain_m6_default`, `det_dither_explicit_default`,
`det_dither_explicit_D`, `det_f32_to_s16_plain`, `det_concurrency_default`,
`guard_gain_p12_default`, `guard_G_gain_p12_default`). **Exactly 1
difference**: `guard_default_path_row.railed_G_gain12_default` 14 917 vs
14 962 — the row the boundary's X1 correction says is dither-sensitive and
which the family **records, never arms** (only `> 0` is armed). This matches
the author's own disclosure, and the residual is invisible to judgment by
construction.

## 8. Custody, hygiene, provenance

- File-only family confirmed on the receipt side: 16/16 censuses (entry+exit ×
  8 entries) show `own_objects: []` and `own_modules: []`; a live `pactl`
  check after the whole battery found **0** `r94`-tagged sinks/sources/modules.
  The default sink is still
  `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink.29` (the same object
  the author's window read). **No `set-default-*` was issued by this seat** and
  the family contains no such call.
- Bounded children: 172 measured leg walls per run, **max 0.095 s** against the
  25 s cap; **0** `killed_at_bound`, **0** spawn errors, and exactly **8**
  non-zero-rc legs — all *armed* refusals: `det_copy_token_not_an_effect`
  (rc 2) plus rc 1 on `det_flag_after_effect`, `det_flag_after_dither`,
  `rate_q_a_refusal`, `trim_0_1e-9`, `trim_0_1sec`, `repeat_neg1`,
  `silence_zero_periods`. No unarmed red exists in either green run.
- Zero tracked writes: `git status --porcelain --untracked-files=no --
  corpus/live/r94-verifier` = 0 lines. The lane is untracked-only
  (`?? corpus/live/r94-verifier/`). The tracked pyc was not touched (all runs
  happened inside the frozen tree copies).
- Lane footprint: `r94v-head.tar` (3.3 GB) + `tree/` and four hardlink
  mutation copies + `scratch/` — **6.4 GB**, all under the gitignored
  `corpus/live/r94-verifier/`.

## 9. Remaining risks

1. **Console-line green bias (presentation, not artifact).** A blocked-only
   run prints `{"receipt": …, "failures": {}}` with **rc 0** (measured: the
   `tree-norefs` run). The receipt is honest — 146 named cells — but a reader
   of the runner's stdout alone would read that run as green. If a future
   gate greps stdout instead of the receipt, witness absence becomes
   invisible. Recommend the runner's summary line carry the blocked count.
2. **Self-consistent receipt rewrite** (see §6) is undetectable at receipt
   level; only live re-runs and the frozen-tree pin cover it. Unchanged from
   the r89 finding.
3. **Band-estimator convention delta** on the `-q` row (§4): 6.1 dB between
   this seat's estimator and the fixture's, on a folded non-stationary
   product. Both agree on the law; a future round that arms an *absolute*
   dB value on a folded row would be pinning convention, not physics.
4. **The fixed-path family lock is per-tree** (`ROOT/live/measure_audio-sox-r94.lock`),
   so two concurrent runs from *different* tree copies do not exclude each
   other — the inherited r89 F5 property. It cost nothing here (4 mutation
   runs ran concurrently in separate trees with separate scratch), but a
   same-family co-tenancy in one tree is the only case it excludes.
5. **Host load 54–57** during the window: every leg's wall time is ≪ cap and
   the cross-run walk is clean, so no evidence of load coupling — but the
   `-G` default-path count and the 7 volatile legs remain load/entropy
   sensitive by construction.
6. The shared checkout was left mid-merge by a **concurrent r95 seat** (§1).
   This seat neither caused nor touched it; the operator should resolve it
   before the next round's freeze, since the worktree fixture no longer
   equals `HEAD`.

## 10. Doc-vs-measured deltas (all minor, none gating)

- The author's "7 cross-seat metric witnesses" is the **arm call-site** count
  (7 sites, verified: 8 grep hits − 1 `def`); the **blocked-cell** count for
  that class is **15** (several sites arm more than one leg) and the compared
  key-value count is **29**, which is what the author's "29/29" cites. Both
  numbers are right on their own basis; the report does not say which basis
  "7" uses.
- The author's "~140 arm evaluations" for 102 call sites is not directly
  countable from the receipt (arms are internal); the 253 independent laws
  this seat wrote cover the same claim space and all pass.
- Author's `copy`-correction, `remix 0 1`-naming, `vol p`-factor and
  `stat -freq` line-law corrections all re-derived in §4 — each is a
  *correction* the scout did not have, and each is now pinned by an
  independent measurement, not just by the author's own.

## 11. Evidence index (all under `corpus/live/r94-verifier/`)

- `r94v-head.tar` (sha256 `424ac63d…`), `tree/` (symdiff 0),
  `runs/r94v-symdiff.txt`.
- Green receipts: `tree/corpus/live/runs/20261016T085526073120Z-sox-r94/`,
  `…085534617516Z-sox-r94/`; run logs `runs/r94v-runA.log`, `…runB.log`.
- Mutation runs: `tree-norefs/…085604070336Z…`, `tree-forgesha/…085558553138Z…`,
  `tree-mutcal/…085555657413Z…`, `tree-mutstim/…085601258604Z…` (+ logs).
- Law engine + results: `runs/r94v_laws.py`, `runs/laws-{A,B,forgesha,mutcal,mutstim,norefs}.json`,
  `runs/forge-*.json` (12).
- Live engine + results: `runs/r94v_live.py`, `runs/r94v-live.json` (83 laws),
  own stimuli/products in `scratch/`.
- Extracted family source for reading: `runs/r94v_family.py` (2 196 lines,
  byte-identical slice of the frozen fixture).
