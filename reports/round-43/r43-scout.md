# R43 scout — combined peak/RMS comparator and decode arithmetic

## Scope and declaration

Read the R43 declaration in `.shokunin/audio/LOG.md`, the current fixture builder and measurement runner, and prior control/threshold reports. This report is the only file written in this lane. I did not modify shared source, run shell commands, generate/decode WAVs, or audition. This is numerical fixture calibration only.

R43 declares source-generated 0.12 s / 5,760-frame / 48 kHz mono PCM16 UI-shaped controls with periodic 1 kHz cosine crests of 46 and 47 counts. The declared outcomes are 46 failing only the level check and 47 passing all checks, while both peaks stay below .95 and both centroids stay in 250–4000 Hz. It specifically describes an adjacent **crest count** bracket, not adjacent RMS values or an exact `.001` test.

## Implemented comparator and decoded signal path

In `corpus/fixtures/measure_audio.py`, `measure()` obtains stream metadata/duration with ffprobe, then decodes the WAV using this SoX invocation:

```python
command("sox", str(path), "-t", "f32", "-e", "floating-point", "-").stdout
```

It interprets output as little-endian float32 and widens to float64:

```python
samples = np.frombuffer(pcm, dtype="<f4").astype(np.float64)
```

Peak and RMS are computed over these decoded samples: `max(abs(samples))` and `sqrt(mean(samples**2))`. The one combined predicate is `if peak >= .95 or rms < .001:` and appends `level: clipping headroom or near silence`. Consequently peak equality/failure is inclusive at `.95`, while the RMS failure is strictly below `.001`; RMS exactly `.001` would not fail this branch. The receipt reports `peak_full_scale` and RMS in dBFS (`20*log10(rms)`), not linear RMS directly. It also records `peak_max_exclusive: .95` and a misleadingly named `rms_min_exclusive: .001`; the executable comparison is the authority.

The PCM16 decode scale is signed integer sample divided by 32768. For the proposed periodic cosine, 5,760 samples contain 120 cycles, so a crest is sampled. If quantization yields integer waveform `q[n] = rint(c*cos(2*pi*1000*n/48000))`, SoX-decoded values are `q[n]/32768` and thus:

- peak = `c/32768`;
- RMS = `sqrt(sum(q[n]**2)/5760)/32768`.

The numeric values in the executor report (read, not independently run here) are 46: RMS `0.0009918604133909925` FS = `-60.07098885448798 dBFS`; 47: RMS `0.0010130695326051166` FS = `-59.88721491134572 dBFS`. Thus the actual RMS gap straddles `.001` although the counts are adjacent crest magnitudes, and the expected comparator outcomes are consistent with those reported measurements. The associated peaks are `46/32768 = 0.00140380859375` and `47/32768 = 0.001434326171875`, nowhere near `.95`. Reported centroids 1333.1671762128612 Hz and 2221.180142174044 Hz are inside the UI band. This arithmetic does not itself establish runner receipts or independently validate executor measurements.

## Historical controls and remaining gap

The historical round-5 control report records this sequence (commands below are quoted from the report, not run in this lane):

```sh
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-flat
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-slope
python3 .shokunin/audio/corpus/fixtures/measure_audio.py --probe-failing
python3 .shokunin/audio/corpus/fixtures/measure_audio.py
```

Recorded exits were `0, 1, 1, 1, 0`. Normal fixture RMS values in the round-5 distribution were `-23.7799` to `-14.8814 dBFS`, well above the RMS floor of `-60 dBFS` (linear `.001`). The flat probe targets section contrast; slope targets loop slope; the broken ambience control fails centroid and endpoint, not the level predicate. These historical probes therefore do not isolate the RMS branch near its threshold.

R42 then covered the other arm of the combined predicate with 31,129/31,130 decoded PCM16 peak counts. Its corrected non-author 44-run replay recorded the 31,129 pass and 31,130 sole level failure; both had RMS around `-3.456 dBFS`, far above the RMS floor. That peak control does not test the RMS comparator. The old local threshold note likewise states that no dedicated RMS-boundary negative/positive control was exercised. Existing ordinary fixture positives and far-below-peak controls cannot substitute for a near-floor RMS bracket.

## Commands, failures, and limits

No shell commands were executed in this scout lane, so there are no scout shell exits or command failures to report. Historical command lines and exits above are documentary evidence from earlier reports. I did not independently decode either candidate, so I report no scout decoded measurement, SHA, numeric fit, or setup error. In later execution, a validly generated/decodeable waveform that misses the declared crest, RMS, peak, centroid, or ordinary-gate constraints is a numeric fixture-fit failure. Missing tool/path, invocation, or malformed-file failures are setup/decode errors instead; they must not be represented as measured comparator outcomes.

The narrow intended finding is only that the source arithmetic can place these two candidate RMS values on opposite sides of the existing linear `.001` comparator while peak remains low. It does not establish exact threshold equality, perceptual silence, audio quality, production, rights, engine behavior, publishing, or promotion.
