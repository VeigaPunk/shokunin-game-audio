# Round 47 Sol adjudication — UI absolute upper centroid

**Verdict: ADMIT the one declared calibration move, narrowly.** Calibration **improved**; depth **unchanged**; coverage **unchanged**. No demonstrated scoped harm. This verdict admits a reproducible, source-generated, project-decoded **gate-level** bracket of the unchanged ordinary UI absolute upper 4000 Hz spectrum predicate. It does not admit a new comparator, a causal single-variable spectral experiment, or a perceptual claim.

## Boundary and evidence

Clean-before `90c4aea8fe2c7ac4958d78b3d90c1206e6dc6004`. The source diff adds only mutually exclusive opt-in `--probe-ui-upper-centroid-below` and `--probe-ui-upper-centroid-above` generation, measurement, mode labeling, and receipt paths in `corpus/fixtures/build_artifacts.py` and `measure_audio.py`. `SPECS["ui"] == (.12, 250, 4000, False)` and `if not spec[1] <= centroid <= spec[2]` are unchanged. This absolute per-file upper check is distinct from R46's lower 250 Hz gate bracket and the pairwise `_alt` relative-centroid/duration distinctness rule. The new scratch files are not canonical artifacts.

| Fresh non-author receipt | Generated WAV SHA-256 | SoX-f32 whole-wave magnitude-FFT centroid | Peak FS / RMS dBFS | Result |
|---|---|---:|---|---|
| `corpus/live/runs/20261013T071531697506Z-ui-upper-centroid-below/measurements.json` | `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` | **3999.922795974407 Hz** | `.279754638671875` / `-18.327854015660773` | exit **0**, no failures |
| `corpus/live/runs/20261013T071532741662Z-ui-upper-centroid-above/measurements.json` | `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383` | **4000.427101452783 Hz** | `.2789306640625` / `-18.32785200392649` | exit **1**, sole `spectrum: centroid outside fixture band` |

Both are deterministic .12 s / **5760-frame**, 48 kHz mono PCM16 files, pass format/duration/peak <.95/RMS >=.001, and have distinct SHA-256. I inspected both raw receipt measurements and hashed both integrated WAVs; hashes match the receipts/report. Nominal generator oscillator values **3983/3984 Hz are not the measured centroids**. The independent alternate worker used different WAV SHAs (`20668f7a9bd167479e185ac3ad9ec13b36380719cfcf6506775f6bc63294e69d` / `61e69e3041ff76db1d5b67a892b3b4723d2296ea51235511fc2de8edf6f41cfb`) and measured **3998.2575908677754 / 4000.5907358489767 Hz**, same polarity; those files were not integrated.

Named non-author `reports/round-47/r47-verifier.md` lists **54 exact fresh serial commands, exits, receipts, and failure arrays**. I inspected 54 unique raw JSON receipt paths dated `20261013T071530637991Z`–`20261013T071626664428Z`: **23 exit 0 / 31 expected fixture-validation exit 1** per the command ledger; the historical prior52 subset (#1, #4–#54) remained **22/30**. Initial and final normal receipts `20261013T071530637991Z-normal` / `20261013T071626664428Z-normal` are equal JSON, with 17 canonical measurements and no failures, and equal the inspected preceding normal baseline. The verifier's SHA check reports old17 unchanged; normal receipt metrics, five generic `_alt` comparisons, four family groups/eight comparisons, and thresholds were preserved. Eight invalid outcomes (#49) are recorded as expected, including `native16_probe` pass and seven expected failures; section/seam historical replay outcomes remain in ledger. These controls support absence of observed regression, not a general proof of all behavior.

## Axis judgment

- **Calibration — improved.** Before R47 the unchanged inclusive UI gate had R46 lower-bound evidence but lacked a close source-generated **upper** boundary pass/fail replay. The measured 3999.922795974407 / 4000.427101452783 Hz pair and fresh opposite CLI exits now provide that missing numerical gate-level evidence.
- **Depth — unchanged.** No new perceptual, synthesis, engine, rights, or production capability; this is one pre-existing predicate measured more closely.
- **Coverage — unchanged.** The opt-in pair does not expand the ordinary artifact family or establish wider audio/perceptual coverage. Existing 17 canonical fixtures and prior probes are preserved.
- **Harm — none demonstrated in declared scope.** Source diff leaves comparator and canonical specifications unchanged; non-author replay and normal restoration show no observed regression. This is not a claim that all unseen contexts have been tested.

Executor's earlier nominal **3950/4050** and **3980/4020** candidate pairs were **valid but broader brackets**, *not failed numeric fits*. A helper's relative-path `ValueError`/reviewer's string-versus-Path invocation were setup errors, distinct from gate failures. The executor's repeated absolute-path correction is redundant report text, not a numeric result or a replay setup failure. Eight wave1 reports (`scout`, `executor`, `alt`, `critic`, `reviewer`, `simplifier`, `scribe`, `guard`) were read; their pre-integration predictions are not substituted for the later named verifier's actual runner receipts.

**Limit:** The two WAVs have different nominal carrier values, quantized samples, and complete FFT distributions. A sole recorded spectrum failure is gate-level isolation, **not causal single-variable spectral isolation**. No decoded-centroid **exact 4000 Hz equality** case was run; inclusive behavior at equality follows source comparison, not a measured equality receipt. No timbre, audio quality, perception, universal band, production suitability, rights, engine integration, publishing, rank, or promotion follows. **SHONEN four checked; no promotion.** No commit, push, or shared edit by this adjudicator.

## My command record

Read LOG, eight wave1 reports, verifier, source diff, and raw JSON with the Python REPL; no test runner or new receipt generation by me. Shell commands from `/home/vgpnk/Projects/prymeagnt/audio`:

- `git status --short --branch && git diff --stat 90c4aea --` — exit **0**; observed the two fixture-source modifications, LOG modification, and existing untracked receipts/reports.
- `git diff 90c4aea -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**; inspected unchanged comparator and opt-in additions.
- `git diff --check 90c4aea -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` — exit **0**.
