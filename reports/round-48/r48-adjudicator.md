# Round 48 Sol adjudication — adjacent sample-rate format calibration

## Verdict

**Admit the one declared calibration move, locally.** Against clean-before `2c05aa0ca49bcaa4c53b06c52f6d0c51fe66388f`, the axes are **depth unchanged; coverage unchanged; calibration improved**. There is **zero demonstrated scoped harm**. The gain is a fresh, narrow 47,999-versus-48,000 Hz *metadata-rate boundary* check of the existing exact ffprobe integer-rate/mono predicate, with identical discrete PCM payloads and all other UI gates passing. Round 25's `mono441_probe` was a broad 44.1-kHz mismatch, not this adjacent boundary. No change to the predicate is needed or claimed. This satisfies the declared admission rule (at least one improved axis, none harmed), not a claim about arbitrary rates or production audio.

## Evidence and independent replay

I read the Round 48 LOG, all eight wave1 reports (`scout`, `executor`, `alt`, `critic`, `reviewer`, `simplifier`, `scribe`, `guard`), named non-author `r48-verifier.md`, the diff against clean-before, the raw newly generated WAVs, and the 56 fresh receipt JSON files. The verifier's complete ledger gives each exact `python3 .shokunin/audio/corpus/fixtures/measure_audio.py [--probe-…]` command, expected exit, and receipt path; this adjudication did **not** rerun those commands or create receipts. I independently checked 56 distinct existing ledger paths from `20261013T073437351218Z` through `20261013T073543068672Z`: **24 exit 0 / 32 expected fixture-validation exit 1**, no replay setup failure. Excluding the new #2–#3, its full prior54 subset (#1, #4–#56) is **23/31**. The raw first/final normal JSON objects match exactly (17 canonical measurements without failures), as do intervening restored normals. The first normal matches the R47 fresh normal JSON. All 17 canonical WAV SHA-256 values match the historical guard table; five generic `_alt` comparisons and eight third-variant comparisons across four families pass. Thresholds, section results, eight invalid-fixture outcomes (seven expected failures, native16 expected pass), and normal restoration hold. The invalid runner's exit 1 is an **expected fixture-validation result**, not a setup error.

The new commands and outcomes (from the non-author verifier's exact ledger, repository root):

| Exact command | Exit | Fresh raw receipt | Probe result |
|---|---:|---|---|
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-47999` | 1 | `.shokunin/audio/corpus/live/runs/20261013T073438393360Z-ui-rate-47999/measurements.json` | Sole `format: expected 48kHz mono` |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-ui-rate-48000` | 0 | `.shokunin/audio/corpus/live/runs/20261013T073439440343Z-ui-rate-48000/measurements.json` | No failures |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T073437351218Z-normal/measurements.json` | Initial normal, 17 clean |
| `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` | 0 | `.shokunin/audio/corpus/live/runs/20261013T073543068672Z-normal/measurements.json` | Final normal, identical JSON |

| Fresh probe | WAV SHA-256 | Frames / ffprobe rate / channels / codec / bits | ffprobe duration | Peak FS | RMS dBFS | Project SoX-f32 whole-wave centroid |
|---|---|---|---:|---:|---:|---:|
| 47999 | `71551e200633e62b1b9db4ee5a582f8d4d996cd693f2e4a040a96023b130a210` | 5760 / 47999 / 1 / pcm_s16le / 16 | .120003 s | .27996826171875 | -18.327858226717105 | 1022.5148421151724 Hz |
| 48000 | `387500a620fbfdfb38e044ebb1ec8e0a82be14be9dc71e2bd18e45ec9625ed8c` | 5760 / 48000 / 1 / pcm_s16le / 16 | .120000 s | .27996826171875 | -18.327858226717105 | 1022.536144951523 Hz |

The two generated WAVs have byte-identical 11,520-byte PCM payloads (SHA-256 `058cacc8a6cdf19afa215c4d386bb903ede8641b9aed0468ff4678ef327c9eea`) and identical SoX-decoded f32 byte sequences (SHA-256 `4497c82d9bd1fb000455081a5f477af7756e7c035bbe1e81ad295f0b32805c7f`); their WAV hashes differ because their header rates differ. Each measured duration lies inside `.12 ± .001 s`, peak is below `.95`, RMS exceeds `.001` FS, and centroid lies within the existing UI 250–4000 Hz band. The format error is the only failure in the 47999 receipt. Independent original alt samples at `.30`/700 nominal Hz give the same polarity, but the integrated/replayed fixtures are the executor pair above.

## Scope, caveats, and source control

`git diff 2c05aa0 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py` exited **0** and shows only paired scratch-WAV generation plus two opt-in runner flags, fixture measurement dispatch, and receipt labels. The ordinary `SPECS["ui"]`, exact `format_failures` requirement (`int(stream["sample_rate"]) == 48000` and `int(stream["channels"]) == 1`, plus PCM16 check), numeric thresholds, and other gates remain unchanged. The full tracked `.shokunin/audio` diff additionally includes the declared LOG; no tracked canonical artifact changes were shown. This is source and receipt evidence, not my rerun of the runner.

Wave1 reports distinguish setup errors from outcomes: alt's two helper path errors, scout's malformed direct-SoX command, reviewer's relative-path helper error, and guard's shell quoting error were setup, not failed numeric fits. The selected pair had **no numeric failed fit and no final report-transcription correction**. Scribe correctly labeled its decision table as pre-integration expectation, not a runner receipt; its inline sample-count-based rate selection cannot by itself distinguish the two 5760-frame files, so the *actual project measure and fresh runner JSON*, not that inline command, govern the 48000-Hz centroid. Critic's pre-integration inability to confirm runner exits was resolved by later fresh receipts. No undocumented runner failure is promoted to a gate result.

Equal discrete sample values do **not** imply the same physical-time waveform: declaring a different rate changes interpreted duration and the FFT frequency grid, hence the different centroids. The other gates *pass* for these two inputs, rather than being invariant by definition. No resampling/converter path, exact physical-signal isolation, universal sample-rate behavior, audible quality/perception, production readiness, rights, engine use, publishing, rank, or promotion follows. The four SHONEN were checked without promotion. This report makes no shared edit, commit, or push.
