# r28-critic — comparator isolation and close-fit challenge

## Finding

I independently falsified neither the comparator arithmetic nor the basic fixed-duration centroid-arm isolation: a scratch baseline and two variants measured through the project `measure_audio.measure()` have equal reported duration, pass its ordinary UI checks, and straddle the existing numeric cutoff. However, “close parameter fit” is not evidence of a smooth or perceptually close transition. The project's whole-waveform, unwindowed FFT magnitude centroid is highly non-monotonic with small analytic parameter changes; nearby nominal values can jump across and back across the cutoff. Treat the result strictly as numeric proxy polarity for these saved/read-back files.

## Independent scratch check

I generated 5,760-frame UI-shaped chirps at 48 kHz, PCM16, changing only initial frequency `f0` from baseline 700 Hz to 730 and 740 Hz. Envelope and chirp slope stayed fixed (`.38*sin(2*pi*(f0*t + 800*t*t))*exp(-30*t)`). Direct project `measure()` results:

| File | f0 | duration | format | peak FS | RMS dBFS | centroid Hz | relative delta vs base | distinctness centroid arm |
|---|---:|---:|---|---:|---:|---:|---:|---|
| base | 700 | .120000 s | 48k mono PCM16 | .3759460 | -19.991688 | 966.896659 | — | reference |
| f730 | 730 | .120000 s | 48k mono PCM16 | .3758850 | -19.991666 | 1043.089087 | .0788010 | below .10; fail if duration delta=0 |
| f740 | 740 | .120000 s | 48k mono PCM16 | .3761292 | -19.991626 | 1077.651352 | .1145466 | >= .10; pass if duration delta=0 |

All three returned empty ordinary `failures`; same frame count and ffprobe duration give duration delta 0. I reproduced the OR branch arithmetic separately (duration delta 0, `.078801...` false; `.114546...` true). These parameters are less close than the executor's fitted pair and are included as independent isolation evidence, not as the best-fit claim.

### Exact commands and exits

Run from project root:

- `python3 /tmp/r28critic/make.py` — exit **0**; wrote only scratch WAVs under `/tmp/r28critic/`.
- `python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); m.ROOT=Path("/tmp"); [print(n,m.measure(n,m.SPECS["ui"],Path("/tmp/r28critic")/(n+".wav"))) for n in ["base","f730","f740"]]'` — exit **0**; direct project measure outputs summarized above. `m.ROOT=Path("/tmp")` only permits the helper to render scratch paths relative to root; it does not alter repository files or measurements.
- `python3 -c 'import numpy as np; r=48000; n=5760; t=np.arange(n)/r;
def c(f):
 x=np.round(np.clip(.38*np.sin(2*np.pi*(f*t+800*t*t))*np.exp(-30*t),-1,1)*32767).astype(np.int16).astype(float)/32768; s=np.abs(np.fft.rfft(x)); q=np.fft.rfftfreq(n,1/r); return float(np.dot(q,s)/s.sum());
b=c(700); print("baseline",b);
[(print(f,round(c(f),3),round(abs(c(f)-b)/b,6))) for f in range(730,741)]'` — exit **0**; local f0 sweep shows 730 relative `.078801`, 731 `.107543`, 732 `.096948`, 733 `.056211`, 734 `.012087`, 735 `.012738`, 736 `.010434`, 737 `.021857`, 738 `.073001`, 739 `.112103`, 740 `.114547`. This is non-monotonic, so interpolation or “parameter closeness” is not a reliable fit argument. This sweep used the same PCM16 generation/FFT arithmetic; the selected direct measurement used actual WAV readback via SoX.
- First attempt `python3 -c '...m.measure(...,Path("/tmp/r28critic")/...)...'` — exit **1**: `ValueError` because `measure()` reports `path.relative_to(ROOT)` and `/tmp/r28critic` is outside its ROOT. Setup/reporting path issue, not a failed numeric fit; fixed by setting helper `m.ROOT=Path("/tmp")` as shown in the successful command.

## Challenge to the submitted close-fit claims

The executor's `f0=630` / `626` pair and the alternate's multiplier `1.10` / `1.11` do bracket the checker numerically, but neither establishes a smoothly close parameter boundary. The alternate changes the entire chirp trajectory (`700*k*t + 800*k*t*t`), and its own recorded fine sweep is non-monotonic (1.104 relative .11253, 1.105 relative .07657). The executor likewise reports non-monotonic trials near 625/626 Hz. A one-parameter analytic family does not make the FFT proxy continuous in the measured, quantized finite-sample result in a practically useful sense. Do not characterize candidate parameter separation as perceptual closeness or exact threshold equality.

A second conceptual limit: centroid is a weighted mean of FFT-bin frequencies and can change from phase/interference, envelope, leakage, or PCM quantization, not just an isolated “frequency shift.” Same frame count and duration remove the obvious differing FFT-bin-grid confound for this pair; they do not make centroid a perceptual metric. This does not demonstrate audibility or perception.

## Scope

Only this report was written in the repository. Candidate WAVs and generator are under `/tmp/r28critic`; no runner, canonical fixture, LOG, SCORECARD, source, prior receipts, or other report was changed. No threshold, rights, engine, publishing, or promotion claim is made.
