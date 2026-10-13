# R43 independent critic — RMS-only calibration claim

Scope: numerical fixture calibration only. I did not audition or infer sound quality, production suitability, rights, engine behavior, or publishing/promotion readiness. I read the R43 declaration in `.shokunin/audio/LOG.md` and inspected the executor scratch candidates only; no shared source, canonical artifact, log, scorecard, other report, or git state was changed.

## Independent candidate check

Candidates: `corpus/live/round-43/executor/crest-46.wav` and `crest-47.wav` (paths relative to `.shokunin/audio`). SHA-256: `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc` and `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3`.

I used the project's `measure()` directly with the declared UI spec, rather than invoking an R43 CLI mode: the checked-in `measure_audio.py` has no R43 RMS-probe flags yet. Exact command (exit 0):

```sh
python3 -c "import importlib.util,json; from pathlib import Path; s=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps([m.measure('probe',(0.12,250,4000,False),m.ROOT/'live/round-43/executor/'/n) for n in ['crest-46.wav','crest-47.wav']],indent=2))"
```

| Candidate | WAV format / duration | decoded peak (crest) | decoded RMS | RMS dBFS | centroid | measurement failures |
|---|---|---:|---:|---:|---:|---|
| 46 | PCM16, mono, 48,000 Hz, 0.120000 s / 5,760 frames | 46/32768 = 0.00140380859375 | 0.0009918604133909925 | -60.07098885448798 | 1333.1671762128612 Hz | sole `level: clipping headroom or near silence` |
| 47 | PCM16, mono, 48,000 Hz, 0.120000 s / 5,760 frames | 47/32768 = 0.001434326171875 | 0.0010130695326051164 | -59.88721491134572 | 2221.180142174044 Hz | none |

The direct PCM inspection independently agreed on 5,760 frames and decoded RMS values. `ffprobe` confirmed both codec `pcm_s16le`, 48,000 Hz, mono, 16-bit, duration `0.120000`; exact command `ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json <candidate>` exited 0 for each. SoX f32 decoding exited 0 for both; RMS above is from that decoded PCM path used by `measure()`.

## Falsification / limits

- **RMS branch isolated in this pair:** observed peaks are about 0.0014 FS, far below .95, so the 46 failure cannot be attributed to the clipping side of `peak >= .95 or rms < .001`. The 46/47 decoded RMS values straddle .001 and match the declared expected fail/pass. This supports a local RMS comparator calibration control, not a conclusion that loudness alone governs acceptance generally.
- **Peak:** this pair does not probe near the peak bound; it only holds peak far below it. It neither overturns nor extends R42's peak-specific evidence.
- **Centroid:** both observed values fall within the UI fixture band 250–4000 Hz. However, these values are not close to the declared 1000 Hz tone: especially the 47 centroid is 2221 Hz. For these extremely low-amplitude, quantized PCM candidates, passing the broad band is not evidence of a clean 1 kHz sinusoid or spectrum/timbre. Thus “centroid passed” is true only as the stated band predicate, not as a claim that the intended tone was faithfully measured.
- **Duration/format:** both meet the declared fixture checks; no detected failure here. This is not evidence about other encodings or durations.
- **Decoded RMS and equality:** measurements are from SoX-decoded float samples, and are strictly below/above .001 as listed. The comparator is `rms < .001`, so a mathematically exact equality would not fail that clause; this pair does not attain or test equality. The values demonstrate a straddle, not adjacent attainable RMS values: only crest counts 46 and 47 are adjacent, and the decoded RMS gap is about 2.12e-5 FS. No exact threshold-equality, general monotonicity, or perceptual silence inference is justified.

No numeric fit attempt was made that failed. One helper invocation was a setup/API error, not a fixture fit or gate result: I first passed string paths to `measure()`, which raised `AttributeError: 'str' object has no attribute 'relative_to'` (exit 1); converting to relative `Path` objects still produced a setup `ValueError` because they were relative to the repository root instead of the fixture `ROOT` (exit 1). The corrected command above passed. I did not run the checker CLI because the current source has no R43 modes; no CLI exit is claimed.

Overall: candidate evidence supports the narrow adjacent-crest RMS straddle under the existing decoded-RMS comparator, with peak, format, duration, and stated centroid band checks held. It does not falsify the narrow R43 claim; it does falsify any broader reading that the RMS pair validates a 1 kHz spectrum, exact `.001` equality, sound quality, or the peak branch.
