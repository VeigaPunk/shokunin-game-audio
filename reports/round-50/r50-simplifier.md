# R50 simplifier: stereo format gate control

## Minimal wiring

Use the existing builder's single-probe opt-in pattern: one flag builds only a stereo/mono pair under `corpus/live/round-50/executor/`; do not add a framework or new comparator/threshold. Keep fixture generation separate from the ordinary measurement call. Feed each WAV path to `measure("ui", SPECS["ui"], path)` unchanged. This uses the existing UI duration, level, centroid, and format checks; expected pair result is stereo with only `format: expected 48kHz mono`, mono with no failures.

One practical constraint: `build_artifacts.py`'s current `main()` unconditionally builds the standard artifact set before flag branches call `main()` (as the rate probes do). A round-50 builder flag should branch directly to a tiny pair builder before that common `main()` path, writing only the designated round-50 executor scratch directory. No need to alter the existing rate modes. Avoid adding a special runner: invoke the current `measure_audio.py` interface on the two explicit paths, or call its `measure` function from a short command. Do not add durable run receipts unless the parent wants them; the existing script's normal CLI measures its artifact set, not arbitrary paths.

## Existing pair / observed project measurement

The supplied executor scratch pair is already present. Both files contain 5760 frames at 48000 Hz, PCM16. The mono WAV SHA-256 is `93223ee4df8c027d6efaa12d9eca47af3de4fba1eba90c27f29c49ab0086a54a`; stereo is `59e508f1b30d17eef5f00951434915bc7974e02d6988faf07a557270611e950e`. The stereo interleaved payload repeats each mono PCM16 sample in both channels (11,520 mono payload bytes; 23,040 stereo payload bytes).

Exact metadata commands, both exit 0:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-50/executor/stereo.wav
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-50/executor/mono.wav
```

Both commands exited 0.
Actual ffprobe fields for stereo: `pcm_s16le`, 48000 Hz, 2 channels, 16 bits, duration `0.120000`; mono: `pcm_s16le`, 48000 Hz, 1 channel, 16 bits, duration `0.120000`.

I invoked the unchanged project measurement function (command exited 0):

```sh
python -c "import sys; from pathlib import Path; sys.path.insert(0, '.shokunin/audio/corpus/fixtures'); import measure_audio as m; [print(m.measure('ui', m.SPECS['ui'], Path(p).resolve())) for p in ['.shokunin/audio/corpus/live/round-50/executor/stereo.wav','.shokunin/audio/corpus/live/round-50/executor/mono.wav']]"
```

Exit code: 0.

- Stereo: duration 0.12 s, 48000 Hz, 2 channels, PCM16; SoX `f32` stream 46080 bytes = 11520 float32 samples, i.e. 5760 frames × 2 decoded samples. Peak `0.3160400390625`; RMS `-19.902100515581505 dBFS`; whole-decoded-wave centroid `2019.8445020922231 Hz`; failures: solely `format: expected 48kHz mono`.
- Mono: duration 0.12 s, 48000 Hz, 1 channel, PCM16; SoX `f32` stream 23040 bytes = 5760 float32 samples; peak `0.3160400390625`; RMS `-19.902100515581505 dBFS`; centroid `1928.2134621890698 Hz`; failures: none.

Both observed decoded streams fit the unchanged duration ±1 ms, peak <.95, RMS >=.001, centroid 250–4000 Hz criteria. The project measurement treats the SoX-decoded whole stream as authority; stereo's reported centroid differs from mono despite identical per-channel payload sequence. This does not establish per-channel analysis or general stereo/downmix handling. These are numeric measurements, not transcription or listening evidence. No failed fit or transcription was run. The first two direct-call attempts failed during setup (path passed as string, then non-absolute relative path); corrected command above succeeded; these are setup errors, not numeric gate failures.


Setup-only attempts before the successful measurement call (both exited 1; neither produced a measurement):

```sh
python -c "import sys; sys.path.insert(0, '.shokunin/audio/corpus/fixtures'); import measure_audio as m; print(m.measure('ui', m.SPECS['ui'], '.shokunin/audio/corpus/live/round-50/executor/stereo.wav')); print(m.measure('ui', m.SPECS['ui'], '.shokunin/audio/corpus/live/round-50/executor/mono.wav'))"
```

This first passed a string where the helper requires `Path` (`AttributeError`). The second attempt wrapped paths in `Path(...)` but left them relative; it exited 1 with `ValueError` from `relative_to(ROOT)`. The succeeding command above resolves paths first. These were setup errors, not failed numeric fits.

## Scope

This proposes the smallest opt-in builder path and reuse of current measurement logic. No thresholds, formats, runner framework, or analysis semantics change. No claim about channel-agnostic stereo handling, audition, sound quality, perception, production, rights, engine integration, publishing, or promotion.
