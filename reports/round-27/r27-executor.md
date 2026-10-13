# Round 27 executor — matched UI duration candidates

## Result

Synthesized three original 48 kHz mono PCM16 WAVs in `.shokunin/audio/corpus/live/round-27/executor/`: baseline `base.wav` (5,760 frames), near-boundary `var6719.wav` (6,719 frames), and `var6720.wav` (6,720 frames). All use the same analytic UI waveform as the existing fixture, `0.38*sin(2π*(700*t+800*t²))*exp(-30*t)`, with `t=frame/48000`, rounded/clipped to PCM16 as in the fixture builder. The baseline is byte-identical to canonical `ui.wav` (SHA-256 `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; `cmp` exit 0).

Each candidate was measured directly through repository `measure_audio.measure()` with its **own declared expected duration** and the unchanged UI band/loop spec `(duration,250,4000,False)`. This avoids classifying the longer WAVs as failures of the canonical `.120 s` duration spec. All three report `failures: []`; each reports 48,000 Hz, mono, `pcm_s16le`/16-bit, non-clipping peak, non-silent RMS, and centroid within 250–4,000 Hz.

| candidate | frames | ffprobe duration (s) | duration delta from baseline (s) | centroid (Hz) | relative centroid delta | `delta >= .020 OR centroid >= .10` |
|---|---:|---:|---:|---:|---:|---|
| baseline | 5760 | 0.120000 | — | 966.896659338 | — | — |
| var6719 | 6719 | 0.139979 | 0.019978999999999997 | 941.657058714 | 0.02610372099 | false |
| var6720 | 6720 | 0.140000 | 0.020000000000000018 | 939.410108956 | 0.02842759887 | true |

The 6-decimal ffprobe duration string for 6719 frames represents `.139979`, so subtracting the baseline's `.120000` yields `.019979` (Python float result `.019978999999999997`), not the ideal frame-count arithmetic `959/48000 = .0199791666667`. This measured value remains below `.020`; centroid also remains below `.10`, so the candidate is a numeric negative. At 6720 frames, ffprobe reports `.140000`; float subtraction yields `.020000000000000018`, so the existing `>= .020` comparator passes equality in this measurement path. **No threshold was changed.** The duration comparison uses ffprobe's rounded format duration converted to float, not exact WAV frame-count rational arithmetic.

These are direct measurements only, not integrated runner modes; I did not alter shared source or establish runner-level isolation. This is evidence about the existing numeric comparator on these synthetic WAVs, not perceptual distinctness or a general duration/codec claim. No listening, rights, engine, publishing, or promotion claim.

## Commands and exits

From repository root. The first command synthesizes scratch WAVs and hashes them; exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-27/executor/synthesize.py && sha256sum .shokunin/audio/corpus/live/round-27/executor/*.wav
```

Output hashes: baseline `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`, var6719 `bb90dd8b9eeb657037fdff68792b47f81cc47623771acbe9f7cc2d82418b2bb0`, var6720 `e490102ed1d5b60c5182aba754b08f393511faa7f874f1e64bd9de3fcc350b57`.

Direct measurements and comparator arithmetic; exit **0**:

```sh
python3 .shokunin/audio/corpus/live/round-27/executor/measure.py
```

Metadata/frame-count check; exit **0**:

```sh
for f in .shokunin/audio/corpus/live/round-27/executor/{base,var6719,var6720}.wav; do ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"; done
python3 - <<'PY'
import wave
from pathlib import Path
for p in sorted(Path('.shokunin/audio/corpus/live/round-27/executor').glob('*.wav')):
    with wave.open(str(p), 'rb') as w:
        print(p.name, w.getnframes(), w.getframerate(), w.getnchannels(), w.getsampwidth())
PY
```

Baseline identity check; exit **0** (equal hashes, `cmp_exit=0`):

```sh
sha256sum .shokunin/audio/corpus/artifacts/ui.wav .shokunin/audio/corpus/live/round-27/executor/base.wav
cmp -s .shokunin/audio/corpus/artifacts/ui.wav .shokunin/audio/corpus/live/round-27/executor/base.wav; printf 'cmp_exit=%s\n' $?
```

No failed fits or failed shell commands occurred. No perceptual, rights, engine, publish, or promotion inference is made.
