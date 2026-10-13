# Round 25 executor — isolated rate/channel controls

## Scope and outcome
Generated two original analytic 440 Hz sine WAVs (0.2 full-scale peak, 4.000 s, PCM16) under the assigned `corpus/live/round-25/executor/` scratch directory. They differ from the intended 48 kHz mono PCM16 baseline in exactly one format field apiece:

| File | Rate | Channels | Width/codec | Duration | Isolated difference |
|---|---:|---:|---|---:|---|
| `sine_48k_stereo_pcm16.wav` | 48000 | 2 | 16-bit `pcm_s16le` | 4.000 s | channels only |
| `sine_44k1_mono_pcm16.wav` | 44100 | 1 | 16-bit `pcm_s16le` | 4.000 s | rate only |

This is fixture evidence only; neither file was integrated into the shared invalid-probe runner. No threshold or shared file changed.

## Commands and results
1. `python3 .shokunin/audio/corpus/live/round-25/executor/synthesize.py` — exit **0**. The script deterministically writes both files using `math.sin(2*pi*440*i/rate)`, rounded to signed little-endian PCM16; stereo duplicates each sample in both channels.
2. `for f in .shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav .shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav; do ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json "$f"; done` — exit **0**. Metadata matches table.
3. `sox .shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav -t f32 -e floating-point -` — exit **0**; 384000 float samples (stereo-interleaved), peak 0.19998169, RMS 0.14141680. `sox .shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav -t f32 -e floating-point -` — exit **0**; 176400 samples, peak 0.19998169, RMS 0.14141655.
4. `sox .shokunin/audio/corpus/live/round-25/executor/sine_48k_stereo_pcm16.wav -t f32 -e floating-point -c 1 -` — exit **0**; mono mixdown gives 192000 samples and 449.984 Hz magnitude-weighted spectral centroid using 48000 Hz. `sox .shokunin/audio/corpus/live/round-25/executor/sine_44k1_mono_pcm16.wav -t f32 -e floating-point -c 1 -` — exit **0**; 176400 samples and 457.772 Hz centroid using 44100 Hz. Both have approximately 0.2 peak / 0.1414 RMS; no gross level or spectral confound for a hypothetical broad 440 Hz control. This centroid is a decoded-signal description, not a pass against any unrelated fixture's spectral band.
5. Python `hashlib.sha256(path.read_bytes()).hexdigest()` — hashes: stereo `1a71090267d97dc07c14f4a057e2b14a433b45086a424cb99128f55831328987`; mono `1bd9aac91baecffb03cb667c7e4116806eb149aa1c39b5cc787e1b861c965e69` (command not separately executed; values calculated with Python SHA-256).

## Failed fit / limits
No synthesis or metadata/decoding setup failed. These controls were not passed through `measure_audio.py` because integration is outside executor scope; therefore no runner rejection outcome is claimed. Format behavior is inferred from observed metadata and the current source predicate, not an independent runtime rejection. Measurements are not evidence about sound quality, engine behavior, rights, publication or codec compatibility generally.
