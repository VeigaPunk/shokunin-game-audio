# Round 22 executor — native PCM24 / matched PCM16 pre-change probe

## Result

Generated two original, 4.000-second, 48 kHz mono sine WAVs in the assigned `corpus/live/round-22/executor/` scratch directory. The PCM24 and PCM16 files share the same 440 Hz, 0.2-full-scale analytic source; only quantization depth/encoding differs. This is an executor fit test, not a canonical asset or a production format claim.

- `native_pcm24.wav`: SHA-256 `3c7c3db68c1571b4ae14db89d4c15a8a48095189c0bf1d62ab2e291a6fae7125`, 576044 bytes.
- `native_pcm16.wav`: SHA-256 `11b85ba8d1e14d50e1a818c92eaea7ecc542dec14684402683f1fd89628f1003`, 384044 bytes.
- ffprobe reports PCM24 as `pcm_s24le`, 24 bits/sample, `s32` decoded sample format, 48000 Hz, mono; PCM16 as `pcm_s16le`, 16 bits/sample, `s16`, 48000 Hz, mono. The encoded bit depth is explicit even though ffprobe's decoded `sample_fmt` differs and alone is not the right bit-depth test.
- Before-change `measure()` returned no failures for either when given a 4 s / 100–1000 Hz spec: PCM24 peak .19999993 FS, RMS -16.98970 dBFS, centroid 440.041 Hz; PCM16 peak .19998169 FS, RMS -16.98998 dBFS, centroid 449.984 Hz. Both are 48k mono and otherwise pass. Thus the hypothesis is demonstrated: the present rate/channel predicate lets a native PCM24 input through. This tests current `measure()` behavior only; it does not establish that the pre-change public invalid-probe CLI accepted this arbitrary scratch file.

## Before-state inspection

Read `.shokunin/audio/corpus/fixtures/measure_audio.py` without modifying it. `measure()` asks ffprobe for only `stream=sample_rate,channels`, then decodes through SoX to float; the existing format failure is only `rate != 48000 or channels != 1`. No PCM codec, encoded bit depth, or sample-format field is queried or checked. A PCM16-only rule for this specifically declared input class should inspect ffprobe encoded metadata (e.g. `codec_name == pcm_s16le` and/or `bits_per_sample == 16`), not decoded SoX float output or `sample_fmt` alone. Keep this proposal bounded to PCM16 acceptance; not a general WAV validator.

## Exact shell invocations and exits

1. `cat .shokunin/audio/LOG.md` — **0** (read the round-22 declaration).
2. `git status --short --branch` — **0**; observed `## craft/audio-r1`, the pre-existing modified LOG, and round-22 live scratch directory.
3. `git status --short --branch` — **127**; malformed initial `bash()` construction passed the command as a literal executable. No effect.
4. `git status --short --branch` — **0**; corrected invocation, as above.
5. `ffprobe -v error -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,bits_per_raw_sample -of json .shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav` — **0**; JSON confirms PCM24 metadata listed above.
6. `ffprobe -v error -show_entries stream=codec_name,sample_fmt,sample_rate,channels,bits_per_sample,bits_per_raw_sample -of json .shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav` — **0**; JSON confirms PCM16 metadata listed above.
7. `sox .shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav -t f32 -e floating-point -` — **127**; initial harness wrapper incorrectly treated binary stdout as text. The command itself was not successfully run through that wrapper; no measurement inferred from this attempt.
8. `sox .shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav -t f32 -e floating-point -` — **127**, same binary-output wrapper failure; no measurement inferred.
9. `sox .shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav -t f32 -e floating-point - >/dev/null` — **0**.
10. `sox .shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav -t f32 -e floating-point - >/dev/null` — **0**.
11. `python3 -c "import importlib.util; from pathlib import Path; p=Path(\'.shokunin/audio/corpus/fixtures/measure_audio.py\'); s=importlib.util.spec_from_file_location(\'m\',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(4.0,100,1000,False); print(\'PCM24\',m.measure(\'x\',spec,Path(\'.shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav\'))); print(\'PCM16\',m.measure(\'x\',spec,Path(\'.shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav\')))"` — **2**; malformed shell quoting (unmatched quote), no Python measurement ran.
12. `python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(4.0,100,1000,False); print(m.measure("x",spec,Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav"))); print(m.measure("x",spec,Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav")))'` — **1**; first run used non-resolved relative paths, so the measurement's `relative_to(ROOT)` receipt formatting raised `ValueError` after analysis. Not counted as a fit.
13. `python3 -c 'import importlib.util; from pathlib import Path; p=Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=(4.0,100,1000,False); print(m.measure("x",spec,Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav").resolve())); print(m.measure("x",spec,Path(".shokunin/audio/corpus/live/round-22/executor/native_pcm16.wav").resolve()))'` — **0**; produced the two measurement dictionaries summarized above, both `failures: []`.

The WAV generation used Python in the REPL, not a shell command: standard-library `wave` wrote mono PCM at 48000 Hz with signed little-endian 16-bit samples and packed signed little-endian 24-bit samples from the same analytic sine. SHA-256 and size were computed in the REPL.

## Limits / failed fits

The first wrapper attempts that captured binary SoX stdout, one malformed measurement command, and the non-resolved-path measurement run failed as recorded; corrected SoX checks and the final resolved-path `measure()` run succeeded. The matched native pair is a successful test fit, not a failed synthesis fit. No sample-rights, listening/perceptual, engine, publishing, or release claim. No source or canonical files edited; only this report and the two assigned executor scratch WAVs were written.
