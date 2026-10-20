# Round 101 — audio-shokunin — 2026-10-19

## Mistakes

| id | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M1 | Unlogged failing round (historical; reconciled in round 101) | `reports/round-87/r87-verifier.md:20-30`; `reports/round-88/r88-verifier.md:20-30`; at base `git show defbe128:LOG.md \| grep -cE 'r87\|r88'` → 0 (`reports/round-101/r101-scribe.md`); round 101 appended `LOG.md` `## Round 87` / `## Round 88`. | Q11 | A red verifier result without a contemporaneous ledger entry is unlogged, not admitted; reconcile it before later rounds and do not treat a fold as a verdict. |
| M2 | Adjudication skipped | rounds 87, 88, 93, 98, 99, 100 have report dirs and no adjudicator file — `for r in $(seq 87 100); do printf '%s ' $r; git ls-tree --name-only defbe128 reports/round-$r/ \| grep -c adjudicator; done` → 0 for exactly those six (`reports/round-101/r101-scribe.md`, `reports/round-101/r101-critic.md`); at base LOG records them only as bullets and `LOG.md:1534` says "Remaining adjudication is still open". | Q11 | A round without an adjudicator remains `unadjudicated`; a fold or green repair is not an ADMIT verdict. |
| M3 | Post-hoc disclosure | `LOG.md:1542-1546` (`ROUND 99 DISCLOSURE ERRATUM`): receipts showed two additional LAN-control runs beyond the disclosed pass. | Q9 | Disclose every executed arm in the round's own record at run time; a later erratum is a calibration failure. |
| M4 | Side effect on a live network | `LOG.md:1485-1490`: the six-second multicast RTP emission led to explicit opt-in and a default-off guard. | Q10 | Physical-network emission is default-off; require the invocation to name the interface before any such arm can run. |
| M5 | Commit identity drift | `LOG.md:1519-1524`; `git shortlog -sne defbe128` → `73 ci <ci@local>` of 262 commits (the remaining authors total 189). | Q14 | Attribute every lane commit to `audio-shokunin <audio@shokunin.local>`; do not use CI identity or change global Git configuration. |
| M6 | Citation lineage drift | Spot-check: `git merge-base --is-ancestor 5755be5b main` and `... 0cbbb3bb main` both exit 1; `git log -1` shows `e30bcc4c` and `7506c655` carry the same subjects on `main`. The STATE dossier's 41/122 tally was not re-counted. | Q12 | A cited commit must be reachable from the published branch, or the evidence must say `branch-scoped`. |
| M7 | Receipt-vs-harness falsification | `reports/round-76/r76-critic.md:61-99`; `SCORECARD.md:773-775`: the TERM gate passed on a zero-audio capture. The dossier's `.ufo/reports/round-76/audio.md` path is absent here; corrected to the lane critic report. | Q7 | A gate that zero-energy audio can satisfy is vacuous; every gate needs a positive control. |
| M8 | Co-tenancy false red/green | `SCORECARD.md:873,893`; `reports/round-88/r88-verifier.md:20-34` records red verdict arms under co-tenancy while the encoded laws held. | Q8 | Name co-tenancy as a confound wherever host resources are shared; one red run is not a verdict. |
| M9 | Ignore-pattern escape | `corpus/.gitignore:1-19` records the escaped `head-tree/`, `big.wav`, and nested-tree classes and the progressively widened rules. | Q15 | Ignore regenerable snapshot/scratch classes by pattern and prove the result with an ignored-file census. |
| M10 | Future-dated verdict headers | `SCORECARD.md:738,748` dates rounds 73/74 2026-11-01 although the records landed 2026-10-14/15; `ports/frontier/fb-pipewire.md:3-4` repeats the future observation date. | Q13 | A record header uses the observation date; a wave label or planned date is not a substitute. |
| M11 | Vacuous or uncited claim inside a round | `SCORECARD.md:873,883`: the scribe falsified the report's loadavg/leg-count claims and caught an uncited RED run. | Q2, Q5 | Make every number independently derivable by the verifier or mark it attestation-only; do not let an uncited or vacuous claim pass admission. |
| M12 | Stray byproducts promoted to repo root | `sha256sum` of `generate_timings.sh` and `corpus/live/r89-boundary/runs/adhoc/eager/wd/generate_timings.sh` matched at `ca84a047f3d50c084d16e66065809d75a923f48eb467d6fe7a591bd83b44345e`; `git ls-files` lists both. | Q15 | Test work-products belong under `corpus/live/<round>/`; the repo root holds contract files, not generated artifacts. |
| M13 | ART lead cited moving `master` source instead of the pinned FFmpeg tag | `reports/round-101/r101-reviewer.md:35` identifies `audio-art.md:137` as `master` and maps the cited lines to the n9.0.1 locations; the ART row at `audio-art.md:137` is the moving-branch citation. | Q3 | Pin tool and source versions, and cite source lines at the pinned revision actually checked. |
| M14 | Loudnorm regime described by input length instead of its actual −70 LUFS trigger | `reports/round-101/r101-reviewer.md:12-13,30`: at 2.5 s the −inf result follows the −70 LUFS gate; the 3 s boundary is a buffer-size check. | Q6 | Name the measured mechanism/threshold that triggers a regime; do not substitute a correlated input-length description. |
| M15 | L1 wrote a census from the brief instead of from its own table (K3 first draft: "nine floor / eight gated" while its own 17-row table showed 8 / 9) | `reports/round-101/r101-truepeak.md` §Controls "Measured specification discrepancy"; corrected in `corpus/knowledge/2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md` Observed bullets before admission | Q5 | Derive every count from the entry's own observed table (or re-count with a command); never carry a count from a prompt or brief. |
| M16 | Rewriting a 144-arm one-line selector to add one arm silently dropped two existing arms (`probe_ui_route_act_84_r63`, `probe_ui_route_act_00_r63` → mode `normal`) while the seat reported "all old selector outcomes are retained" | L1 per-flag evaluation of old vs new `mode =` / `suffix =` expressions (144 flags; 2 mismatches) recorded in `reports/round-101/r101-truepeak.md` correction section | Q16 | An edit to a dispatch/selector expression is verified by evaluating old and new for every input it routes, not by eye or by diff size; prepend/append instead of re-typing. |
| M17 | Filter-internal rate confused with final output rate | `reports/round-101/r101-reviewer-w2.md` finding 1; `corpus/knowledge/2026-10-19-loudnorm-short-sfx-regimes.md` `Filter-rate witness`: `ashowinfo` immediately after `loudnorm` reports `rate:192000` at 0.4 s and 3.0 s, while the final stream is 48000 Hz. | Q17 | Tap the named filter's output and label downstream resampling separately; record the selected filter rate as a distinct measurement. |
| M18 | A primary-source example was generalized without its qualifier | `corpus/SOURCES.md` S001 teach cell omitted the “unfortunately-phased” qualifier present at BS.1770-5 Annex 2 l.788-789; wave-2 review finding 7; corrected by S015. | Q18 | Preserve source qualifiers and scope; add a superseding row instead of widening an example into a universal limit. |
| M19 | Manual census drift in a claim gate | `reports/round-101/r101-reviewer-w2.md` findings 2/5: tier histogram is A=9 B=2 C=2, not A=10 B=2 C=1; the K1 table has 12 rows / 15 inputs, not 13 rows. | Q5 | Derive each histogram and grouped-row count from the actual table and rerun its count command before recording the gate. |
| M20 | Citation mismatch attributed to moving-source drift without evidence | `reports/round-101/r101-reviewer.md:24,35` reports the cited n9.0.1 and master loci as 450/463; the moving URL was a provenance defect, but the line mismatch itself was not shown to be caused by source drift. | Q3 | Record unpinned provenance and wrong anchors separately; do not claim version drift caused a mismatch without comparing the cited source revisions. |
| M21 | Gate names a stale criteria range | `corpus/lessons/round-101.md` original `## Gate` line 41 said Q1–Q15 while `corpus/QUALITY.md` already contained Q16. | Q19 | List the complete current criteria range in the gate, including same-round additions. |
| M22 | Registry `used-by` omitted a citing lesson | Wave-2 review finding 8: every original S001–S013 row was cited in the lesson's Gate but omitted `corpus/lessons/round-101.md` from `used-by`; the SOURCES path census only proved listed paths existed. | Q20 | Add every citing knowledge entry and lesson to `used-by`; validate completeness as well as existence. |
| M23 | Truepeak probe rebuilt canonical inputs and split generated outputs | `corpus/fixtures/measure_audio.py:main` dispatches `build_artifacts.py` before the truepeak probe; `corpus/fixtures/build_artifacts.py:12,15-22` sets `OUT` to `corpus/artifacts` and writes WAVs there. `reports/round-101/r101-truepeak.md:16-20` records receipts under `corpus/live/runs/` while controls and logs are under `corpus/live/round-101-truepeak/`. | Q21 | Final correction: truepeak measurement reads existing canonical WAVs without invoking the builder or rewriting `corpus/artifacts`; controls, logs, and its receipt all stay under `corpus/live/round-101-truepeak/`. With Q22 (M24), the complete current criteria bar is Q1–Q22; the earlier gate range remains historical. |
| M24 | Positive-control oracle self-validated against its generated PCM | `corpus/fixtures/measure_audio.py:_truepeak_r101_probe` derived expected overshoot by reading the same generated control WAV with `_truepeak_r101_quantized_expectation`, allowing a phase-0 positive-control mutation to agree with itself. | Q22 | Control acceptance uses a name-keyed analytic oracle independent of signal generation and observation: phase-π/4 12 kHz expects ≈+3.0103 dB and phase-0 expects ≈0.0 dB (±0.08 dB); quantized-PCM expectation is only a separate accuracy cross-check. |
| M25 | Non-adjudicator critic disposition omitted from reconciled record | `reports/round-87/r87-critic.md:9` and `reports/round-88/r88-critic.md:9` say “ADMIT-with-findings”; the Round 87/88 SCORECARD and LOG initially omitted this opinion while correctly preserving unadjudicated/no-ADMIT status. | Q11 | Record critic opinions as advisory evidence, explicitly not adjudication, and keep the authoritative status unadjudicated until an adjudicator exists. |
| M26 | Code-work revision conflated with receipt-carrying revision | The initial SCORECARD/LOG c3b attribution pointed at code-work revision `d00a8d22` although that tree lacked the 17-peak receipt; the receipt/count evidence was first carried by revision `343cd978` (review closure: `reports/round-101/r101-c1-review.md:18-20`). | Q12 | Name the code-work revision and receipt/count-carrying revision separately; cite a receipt only against the actual final head whose tree contains it. |

## Honest stops (taste working)

- Universal hard-refusal and multi-sample flatness coverage rejected (Round 91): `LOG.md:1461-1466`.
- Post-subcommand `-s` interpretation false and rejected (Round 96): `LOG.md:1473-1478`.
- Negative-Q reading clipped (Round 92): `LOG.md:1467-1472`.
- Round 68's seekability claim falsified as stated; the no-match fallback follows the named extension, while the real seekability fork is inside the `txw` reader: `LOG.md:1019-1038`.
- Round 73's corpus-wide consumer-polarity claim falsified and retained only as two member-local forks: `LOG.md:1211-1217`.

## Near-misses caught at curation

- EBU R128 `−23 LUFS ±0.5 LU` is stale; the `0.5 LU` mention is historical, not the current normative tolerance: `audio-art.md:433`.
- ASWG-R001 console `−23 LUFS ±2` is superseded by v1.10's revision to `−24 LKFS`: `audio-art.md:434`.
- FMOD's indie threshold in the search result (`$200k revenue / $500k budget`) is stale against the current primary page: `audio-art.md:435`.
- The Godot 4.4 tutorial is contradicted by the same-version `ResourceImporterWAV` class reference on the import default: `audio-art.md:437`.

## Gate

Gate author: round-101 L1 (`W2RoundAudio-8`), 2026-10-19, against `corpus/QUALITY.md` Q1–Q15. Seat evidence: `reports/round-101/r101-reviewer.md` (wave-1 falsification of the ART leads), `reports/round-101/r101-critic.md`, `reports/round-101/r101-scout-godot.md`. Every seat is lane-dispatched, so this gate is still the lane; the non-author spot-check is the orchestrator's.

### Candidates

| candidate | decision | criteria / reason |
|---|---|---|
| K1 as drafted in the ART lead (`audio-art.md` §4 K1: "shorter than one 400 ms gating block" selects peak-normalize; master-era line cites) | **rejected** | Q6 (regime stated by length; the reviewer showed a 2.5 s tone below the −70 LUFS gate is also peak-normalized — L1 re-ran: amp 0.0003 → `input_i -inf`, peak −1.000000) and Q3 (cites l.456/462 on `master`; at tag n9.0.1 the lines are 450/463) — lessons M14, M13 |
| K1 rewritten — `corpus/knowledge/2026-10-19-loudnorm-short-sfx-regimes.md` | **admitted** | Q1 three header lines; Q2/Q5 every row re-measured by the L1 on host (sweep in the entry, 13 rows reproduced); Q3 n9.0.1 lines re-located from the fetched tag; Q4 sole tier-A support (S005/S006/S001); Q6 triggers named (−70 LUFS gate, 3000 ms buffer check) |
| K2 loudnorm two-pass linear gate + JSON `output_tp` under-read (`audio-art.md` §4 K2) | **rejected this round** | Q5: reproduced only by the reviewer seat; the authoring seat did not re-run it, and the ART lead's line cites fail Q3 (l.826-828/121/852/862 → n9.0.1 l.820-821/115/846/856). Flip: an author re-run of the three-signal recheck with pinned lines |
| K3 — `corpus/knowledge/2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md` | **admitted** | Q1; Q2/Q5 17-artifact table re-measured (L1 loop in `recheck:`); Q3 f_ebur128.c n9.0.1 l.172-173/783-784; Q6 the dual-mono offset named as the pan law, not "3 dB"; per-asset TP labelled telemetry; ART lead corrections folded (+3.010 not "exactly 3.0"; overshoot ≈ 1.1 dB with method stated) |
| K4 — `corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md` | **admitted** | Q1; Q2/Q5 docs grep + host headless import re-run by the L1 (`compress/mode=2`, `.sample` sizes reproduced against the scout's); Q3 version-pinned pages (4.3 / 4.4 / stable-4.7); contradicting tutorial rowed `rejected` (S011) |
| K5 — `corpus/knowledge/2026-10-19-game-loudness-whole-mix-protocol.md` | **admitted** | Q1; Q5 pdftotext string counts re-run; Q4 tier-C S007 used only as a labelled lead, ASWG mirror tiered B and corroborated by S004; ART overstatement "BS.1770 excludes pure tones" not carried (the text says "not, in general, suitable … to estimate the subjective loudness of pure tones"); "would contradict both specs" carried only as [INFERENCE] |
| K6 AI-audio terms ledger fields (`audio-art.md` §4 K6) | **rejected this round** | rule 1 of the SOURCES contract: its seven sources (ART S023–S029) were not re-opened this round, so no row and no admission; Frontier, record-only. Flip: re-open the terms pages in a round that rows them, with 30–180 d recheck cadence |

Admitted 4 · rejected 3 (one as-drafted variant, two deferred with flips). Expansion: 4 admitted entries on 4 coverage-map rows that held 0 entries at base (`corpus/README.md` §Core gap, sweep there).

### SOURCES rows written this round (contract rule 1)

All rows new; no status/recheck/used-by changed in place (no prior registry existed: `git -C . cat-file -e defbe128:corpus/SOURCES.md` → fatal). Access date 2026-10-19 for every row.

| id | URL / command | ≤25-word quote | location |
|---|---|---|---|
| S001 | https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf | "Incomplete gating blocks at the end of the measurement interval are not used." | Annex 1, pdftotext -layout l.258 |
| S002 | https://tech.ebu.ch/docs/r/r128.pdf | "the True Peak Level of a programme shall not exceed −1 dBTP (dB True Peak)" | item (m), l.135 |
| S003 | http://gameaudiopodcast.com/ASWG-R001.pdf | "audio content should be measured for as long as is practical and for a minimum of 30 minutes" | rec. 10, l.111-112 |
| S004 | https://www.audiokinetic.com/en/community/blog/mastering-a-game-with-wwise-part1/ | "It is strongly recommended to measure the actual output of your device." | §Measuring Loudness |
| S005 | https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/libavfilter/af_loudnorm.c | "if (s->frame_type == FIRST_FRAME && in->nb_samples < frame_size(inlink->sample_rate, 3000)) {" | l.450 |
| S006 | `ffmpeg -hide_banner -h filter=ebur128` (n9.0.1) | "dualmono <boolean> ..F.A...... treat mono input files as dual-mono (default false)" | option table |
| S007 | https://www.soundarmoury.co.uk/blog/loudness-study | "Considering all of the recorded games, the mean average loudness is -20.6 LUFS." | results paragraph |
| S008 | https://docs.godotengine.org/en/stable/classes/class_resourceimporterwav.html | "By default, Godot imports WAV files using the lossy Quite OK Audio compression." | Description; Properties `int compress/mode = 2` |
| S009 | https://docs.godotengine.org/en/4.3/classes/class_resourceimporterwav.html | "int compress/mode = 0" | Properties table |
| S010 | https://docs.godotengine.org/en/4.4/classes/class_resourceimporterwav.html | "By default, Godot imports WAV files using the lossy Quite OK Audio compression." | Description; Properties `int compress/mode = 2` |
| S011 | https://docs.godotengine.org/en/4.4/tutorials/assets_pipeline/importing_audio_samples.html | "Three compression modes can be chosen from for WAV files: Disabled (default), RAM (Ima-ADPCM), or QOA (Quite OK Audio)." | Compress > Mode |
| S012 | `corpus/fixtures/measure_audio.py` at defbe128 | "if peak >= .95 or rms < .001:" | l.95 |
| S013 | `godot --headless --path <scratch> --import` (Godot 4.7.2) | "compress/mode=2" | generated `ui.wav.import`, `stem.wav.import` |

Census (contract, run from the lane root 2026-10-19): rows 13; malformed 0; tiers `A=10 B=2 C=1`; status `mined=12 rejected=1`; duplicate ids, enum/tier-inflation and missing used-by paths print nothing.

### Spot-check

Pending: the non-author spot-check (≥ 1 admit, ≥ 1 reject, ≥ 3 SOURCES rows re-opened) is the orchestrator's after the round lands. Recommended sample: admit K1 (re-run its `recheck:`), reject K2 (re-run the reviewer's three-signal recheck), rows S003 / S005 / S011.

## Continuation corrections — 2026-10-19

The first L1 (`W2RoundAudio-8`) stopped after a provider rate limit. This continuation keeps the original three claims and appends corrections; it does not silently replace the first gate record. The lane-dispatched wave-2 reviewer is still the lane, not an independent adjudicator.

### Review findings and disposition

- K1's earlier table misidentified the 48 kHz final output as the linear-path filter rate and implied only dynamic mode used 192 kHz. The corrected table labels both: `loudnorm` negotiates 192000 Hz for every path; the final stream is 48000 Hz after downstream resampling. The immediate post-filter `ashowinfo` command and output are in the knowledge entry's `Filter-rate witness`; n9.0.1 starts at `FIRST_FRAME` (l.808) and `query_formats()` offers 192000 Hz (l.740, l.751-752).
- The K1 table contains 12 grouped rows covering 15 signal inputs. Its `recheck:` loop covers eight; the wave-2 reviewer ran the seven omitted inputs and reported they matched. The first gate's “13 rows reproduced” was wrong and is superseded.
- K3's dual-mono result is +3.010/+3.011 LU across nine gated fixtures, not exactly +3.010 on every fixture. The K3 prose now matches its table.
- The original gate's Q1–Q15 range omitted existing Q16. This correction applies the complete current bar, Q1–Q20; Q17–Q20 are linked to M17, M18, M21 and M22 below.
- The ART's moving `master` URL and incorrect line anchors are distinct defects. The cited n9.0.1 and master loci were both reported at 450/463, so source-version drift is not established as the cause.

### SOURCES corrections

The initial gate stated 13 rows and `A=10 B=2 C=1`; the actual original-table tier count is `A=9 B=2 C=2`. Two append-only correction rows were added: S014 supersedes S005's incomplete rate description, and S015 supersedes S001's unqualified phase example. Current census: 15 rows; malformed 0; tiers `A=11 B=2 C=2`; statuses `mined=14 rejected=1`; duplicate IDs, enum/tier-inflation and missing listed-path commands print nothing. The contract census commands are in `fleet-ledger/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:64-81`.

S014 and S015 were opened during this continuation. Rule-1 evidence:

| id | URL | ≤25-word quote | location |
|---|---|---|---|
| S014 | https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/libavfilter/af_loudnorm.c | “static const int input_srate[] = {192000, -1};” | n9.0.1 `af_loudnorm.c` l.740 |
| S015 | https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I!!PDF-E.pdf | “an unfortunately-phased tone at a quarter of the sampling frequency.” | BS.1770-5 Annex 2, `pdftotext -layout` l.788-789 |

Per SOURCES contract rule 2, the following records the old→new `used-by` values for original rows whose Gate now cites the lesson. Path shorthand: K1 = `corpus/knowledge/2026-10-19-loudnorm-short-sfx-regimes.md`; K3 = `corpus/knowledge/2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md`; K4 = `corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md`; K5 = `corpus/knowledge/2026-10-19-game-loudness-whole-mix-protocol.md`; L = `corpus/lessons/round-101.md`.

| id | old `used-by` | new `used-by` |
|---|---|---|
| S001 | K1, K3, K5 | K1, K3, K5, L |
| S002 | K3, K5 | K3, K5, L |
| S003 | K3, K5 | K3, K5, L |
| S004 | K5 | K5, L |
| S005 | K1 | K1, L |
| S006 | K1, K3 | K1, K3, L |
| S007 | K5 | K5, L |
| S008 | K4 | K4, L |
| S009 | K4 | K4, L |
| S010 | K4 | K4, L |
| S011 | — | K4, L |
| S012 | K3 | K3, L |
| S013 | K4 | K4, L |

S014 is used by K1 and L; S015 is used by K3 and L. No other registry fields changed in place.

### Frontier

No `corpus/README.md` Frontier item moved into Core this round. Four uncovered Core-gap rows were admitted and indexed (`README.md` §Core gap, §Frontier); remaining frontier rows are unchanged.

### Used-by follow-up

The reviewer rechecked every source ID against the round-101 knowledge entries and found that the Godot QOA entry cites S011 in its provenance and its rejected-tutorial row. The `used-by` change chain is `— → corpus/lessons/round-101.md → corpus/knowledge/2026-10-19-godot-wav-import-default-qoa.md, corpus/lessons/round-101.md`; the final S011 value now lists both citers. No other `used-by` values changed in this pass.

## Final continuation gate — 2026-10-19

The current criteria bar applied here is **Q1–Q22**; the earlier Q1–Q15 and Q1–Q20 statements above are historical intermediate ranges. C1/C2/C3 remain the same three claims; C1 critic opinions are not adjudications, C1 axis score is unmeasured, and no round-101 ADMIT is asserted.

- `python3 corpus/fixtures/test_truepeak_r101.py` → 10 tests, OK (parser/fail-closed, analytic positive/negative controls, truepeak builder exclusion, default-mode builder preservation).
- `timeout 900 python3 corpus/fixtures/measure_audio.py --probe-truepeak-r101` → exit 0, `failures: {}`, `coverage_blocked: {}`; final receipt `corpus/live/round-101-truepeak/20261019T233319127994Z/measurements.json`, 17 finite artifact true peaks, positive +2.999 dB vs +3.0103 analytic, phase-0 0.000 dB, dual-mono +3.010 LU.
- Canonical fixture check before/after the real probe: `sha256sum corpus/artifacts/*.wav | sha256sum` → `f4e1eb8db062802426fb68ce528212d9d4219e8fd698857658529933020410a9` both times; `git status --porcelain -- corpus/artifacts` empty; `git diff --quiet defbe128 -- corpus/artifacts` exit 0.
- A default-mode CLI run in a temporary copy of the two fixture scripts and 17 WAVs returned rc 0, no failures or coverage blocks, and receipt SHA-256 `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`, matching the pinned normal receipt; all writes stayed in the temporary directory.

## SOURCES recheck correction — 2026-10-19

Reviewer E09 found the rejected, versioned Godot tutorial row S011 lacked a recheck cadence. Only the permitted `recheck` field changed: `— → on-release` (`corpus/SOURCES.md:19`). The final registry retains S011's rejected status, flip condition, and K4/lesson `used-by` paths.

## Final continuation clarifications — 2026-10-19

- In the final-probe report, `coverage_blocked` is CLI stdout, not a stored `measurements.json` field; this clarification adds no telemetry.
- ART dossier IDs S014–S018 are a separate sequence from the local `corpus/SOURCES.md` registry IDs S014/S015 (FFmpeg loudnorm and ITU-R BS.1770-5).
- The four preexisting Core-gap rows were filled; no Frontier row was promoted into Core.
