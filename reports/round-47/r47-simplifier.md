# R47 simplifier — two opt-in modes, no framework

## Scope
R47 LOG declares one calibration move: a deterministic 0.12 s / 5760-frame, 48 kHz mono PCM16 UI-shaped pair. The actual decoded whole-wave magnitude-FFT centroid must be in-band immediately below the existing 4000 Hz upper bound for one fixture and strictly above for the other. Expected outcomes are below: exit 0/no failures; above: exit 1/sole `spectrum: centroid outside fixture band` failure. Existing comparator remains `250 <= centroid <= 4000`. Do not change thresholds or ordinary behavior. This is calibration evidence only, not a causal single-variable spectral test.

## Smallest explicit implementation shape
Two booleans/modes are sufficient; use distinct per-mode scratch WAV paths and route both through the existing `measure(name, SPECS["ui"], path)` path, so the ordinary comparator supplies the result. Build each waveform deterministically at exactly 5760 frames and save as mono PCM16/48 kHz. Do not add a generalized threshold, calibration framework, or shared tuning helper. In report terms the minimal CLI shape is:

```text
--probe-ui-absolute-centroid-below-4000
--probe-ui-absolute-centroid-above-4000
```

Each is mutually exclusive, creates only its corresponding fixture, and stores the usual measurements receipt. Expected exit status is derived from the normal measurement failures (0 below, 1 above). These are proposed names/shape, not implemented or run commands; the current checker has only the earlier R46 `--probe-ui-absolute-centroid-below/above` modes, whose 225/226 Hz fixtures tested the lower bound and are not this upper-bound pair.

## Local numeric fixture experiment (no checker mode run)
I created two scratch WAVs under `.shokunin/audio/corpus/live/round-47/r47-simplifier/` using NumPy sine × Hann-window samples and PCM16 rounding. I decoded them with SoX to f32 and computed the project’s whole-wave magnitude-rFFT weighted centroid, bandwidth, peak and RMS. Both are exactly 5760 decoded samples. The distinct scratch files have these SHA-256 values:

| mode | nominal sine (Hz; not a decoded centroid) | decoded centroid (Hz) | bandwidth (Hz) | peak FS | RMS dBFS | SHA-256 |
|---|---:|---:|---:|---:|---:|---|
| below | 3900 | 3917.096806437624 | 490.488148034138 | 0.279876708984375 | -18.327852133076135 | `c650da9b946bb5fa30a818a6b7f8c5c2b0bbcf643b0f47689709900591640ac7` |
| above | 4100 | 4116.535402468537 | 480.754508841482 | 0.27978515625 | -18.327844106215714 | `a40e1ce2c3c919e8e93342ed19a7dfa59f1ff17e76bcee22435ea7138da489e1` |

Both meet the declared format/duration/peak/RMS constraints; centroid is the only intended differing gate result. The table gives actual decoded project metric, not nominal tone frequency. These were successful numerical candidates, not failed fits. No checker run means their expected exit codes/failure arrays are predictions from the unchanged comparator, not observed runner receipts. No transcription correction was needed.

## Exact shell commands and exits
Ran the following shell command (the WAV paths above) to inspect both files and SoX-decode them; overall shell exit 0, each ffprobe exit 0 and each SoX exit 0:

```sh
for x in below above; do echo ===$x; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-47/r47-simplifier/$x.wav; echo ffprobe_exit=$?; sox .shokunin/audio/corpus/live/round-47/r47-simplifier/$x.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-47/r47-simplifier/$x.f32; echo sox_exit=$?; done
```

There were no setup errors in these commands. I did not run the checker, tests, or audition. Distinguish this from checker setup/mode availability: this task’s scratch fixtures do not connect to a new checker mode, and no code was changed. The 3900/4100 nominal tone frequencies are inputs only; the measured decoded centroids above are the relevant values.

## Limits
This demonstrates a numeric fixture pair around the stated gate boundary, not exact 4000 Hz equality, causal isolation, timbre, quality, perception, production suitability, rights, engine integration, publishing, or promotion. No framework or threshold tuning is proposed.
