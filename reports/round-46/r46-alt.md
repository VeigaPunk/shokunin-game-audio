# R46 alternate original UI centroid bracket — `r46-alt`

Scope: independently synthesized scratch candidates only. No canonical fixture, shared source, threshold, LOG, SCORECARD, or other report was changed. The pair is original deterministic mono PCM16/48 kHz, 5760 frames each, with a constant-amplitude sinusoid at 200 Hz or 300 Hz. The helper measurement uses the project’s actual `measure()` path: ffprobe metadata and SoX float32 decode followed by the whole-wave magnitude-FFT centroid. It is not a nominal-frequency proxy.

## Final candidates and measurements

| file | SHA-256 | decoded duration | decoded centroid | peak FS | RMS dBFS | format | ordinary UI failures |
|---|---|---:|---:|---:|---:|---|---|
| `below.wav` | `e2d85d3828bb139f8d7a6a459f34f88d3f2498b9135c105995717fe071184723` | 0.120 s | 202.48468234677034 Hz | 0.3499755859375 | -12.1292172285544 | 48k mono PCM16 | solely `spectrum: centroid outside fixture band` |
| `above.wav` | `2f9e9228b5cdcf7652ecfc8e1df54f4bc3647f8b303df63edd5e7f013b83af88` | 0.120 s | 302.47893043755806 Hz | 0.3499755859375 | -12.129225594162117 | 48k mono PCM16 | none |

Both pass duration, format, peak and RMS checks. These results bracket the lower bound numerically, but do not test equality at 250 Hz or establish a universal or perceptual threshold.

## Exact commands and outcomes

All commands ran from the repository working directory. The generator in this scratch directory is `build_pair.py`; it writes only `below.wav` and `above.wav` beside itself.

1. `python3 .shokunin/audio/corpus/live/round-46/alt/build_pair.py` — exit **0** (initial 180/300 Hz decaying-sine fit attempt).
2. Project helper import/measure invocation with relative candidate paths — exit **1**, setup/path error: `ValueError` because a relative WAV path was not relative to the helper’s absolute `ROOT`. This is not a numeric fit failure.
3. `python3 -c "import importlib.util; from pathlib import Path; p=Path('.shokunin/audio/corpus/fixtures/measure_audio.py').resolve(); s=importlib.util.spec_from_file_location('m',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(.12,250,4000,False); [print(n,m.measure(n,spec,(Path('.shokunin/audio/corpus/live/round-46/alt')/(n+'.wav')).resolve())) for n in ('below','above')]"` — exit **0**. Initial decoded centroids were 469.50228874958236 and 469.7553367212557 Hz; both were inside the UI band, so the intended below-band candidate fit failed numerically (both gates passed). This pair was superseded.
4. `python3 .shokunin/audio/corpus/live/round-46/alt/build_pair.py` — exit **0** after changing the below candidate to a 60 Hz decaying sine.
5. Same resolved-path helper invocation — exit **0**. Decoded centroid for the attempted below candidate was 720.4544798769202 Hz, still inside the band; this was another failed numeric fit, superseded.
6. `python3 .shokunin/audio/corpus/live/round-46/alt/build_pair.py` — exit **0** after switching both candidates to constant-amplitude sinusoids at 200/300 Hz.
7. Same resolved-path helper invocation — exit **0**. Final output gave the measurements and distinct failure lists shown above: below failed solely the spectrum gate; above passed all gates.
8. `sha256sum .shokunin/audio/corpus/live/round-46/alt/below.wav .shokunin/audio/corpus/live/round-46/alt/above.wav` — exit **0**, hashes as tabulated.

No project runner was edited or used to admit these candidates. This is alternate executor evidence only; independent integration/replay remains for the parent. No audition or quality, timbre, novelty, production, rights, engine, publishing, or promotion inference is made.
