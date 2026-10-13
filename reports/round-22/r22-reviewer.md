# r22-reviewer — source review

## Finding

The current checker has no PCM encoding/bit-depth predicate. In `measure()`, ffprobe requests only `stream=sample_rate,channels:format=duration`; the resulting gate rejects only non-48 kHz or non-mono. It then sends the file through SoX as float32 before numeric checks. Consequently the current measurement path cannot distinguish native PCM16 from PCM24 after decode, and its format-failure message refers only to rate/channel. `invalid_probes()` routes short/odd inputs through `section_contrast()`, corrupt input through ffprobe decode failure, and `wrong_format` through rate/channel metadata. There is no PCM24 case or bit-depth report in that route.

Source locations: `.shokunin/audio/corpus/fixtures/measure_audio.py`, `measure()` metadata query and format gate; `invalid_probes()` probe tuple and `wrong_format` branch; `main()` `--probe-invalid` route. `build_artifacts.py` currently builds the round-6/7 invalid fixtures, but has no round-22/native-PCM24 case in the source inspected.

## Direct metadata check

The round-22 executor scratch is suitable to distinguish container width without relying on secondary audio metrics. ffprobe reports the 24-bit candidate as `codec_name=pcm_s24le`, `bits_per_sample=24`, `sample_fmt=s32`, `sample_rate=48000`, `channels=1`; the positive scratch reports `pcm_s16le`, 16 bits, `s16`, 48 kHz mono. This also shows why `sample_fmt` alone is insufficient here: ffprobe labels the PCM24 decode format `s32`; use codec/bit-depth metadata together.

## Minimal source-change fit (recommendation only)

1. Extend the existing ffprobe stream query with `codec_name,bits_per_sample,sample_fmt` and make the measured format gate explicitly require native `pcm_s16le` / 16-bit PCM in addition to 48 kHz mono. Record the observed encoding metadata in each measurement so the predicate is auditable. This is an explicit PCM16 scope, not generalized WAV/codec support.
2. Add the generated PCM24 scratch to the existing opt-in invalid builder and `invalid_probes()` list. Its branch should query the same metadata and set `observed_failure: format` specifically on the PCM encoding/bit-depth mismatch, retaining observed rate/channels and codec/bits/sample format in the receipt. Do not feed the PCM24 case through only the existing rate/channel condition or infer rejection from downstream level/spectrum failures.
3. Keep an explicitly measured known-good native PCM16 positive (canonical asset or generated matched positive) and show it passes the same new predicate; retain all old invalid outcomes. Keep this narrowly targeted rather than duplicating independent metadata checks with differing field names.

Potential implementation detail for integration: SoX float decode remains useful for signal metrics, but it is not proof of source PCM width. The predicate must use ffprobe metadata before/alongside decode. A 24-bit PCM WAVE may use `sample_fmt=s32`; rejecting it because `sample_fmt != s16` would work for this example but is less directly specific than checking `codec_name` and `bits_per_sample`.

## Limits and failed fits

This is source review plus metadata inspection, not an integration or before/after test. I did not modify shared code, run the invalid-mode end-to-end receipt, test the round-22 candidate against `measure()`, or verify canonical hashes/previous modes. Two direct attempt commands to invoke `measure()` failed during harness setup, not audio validation: one supplied a string instead of `Path` (AttributeError); one used a relative path outside `ROOT` (ValueError). A subsequent retry command also had a misspelled `.shokhun` path (FileNotFoundError). These failed attempts are not passes and do not change the source conclusion. I make no sample-rights, perceptual, engine, or publishing claim.

## Shell command/exit ledger

- `cat .shokunin/audio/LOG.md` — exit 0. Read the round-22 declaration and constraints.
- `git status --short && git rev-parse HEAD` — exit 0; HEAD `14cf9861ca19041ddb25c322facc5ace9271a146`. Preexisting LOG modification and untracked pycache/round-22 scratch were visible; I did not alter them.
- `find .shokunin/audio/corpus/live/round-22 -maxdepth 3 -type f -print` — exit 0; found executor/alternate PCM16 and PCM24 scratch files.
- `ffprobe -v error -show_entries stream=codec_name,codec_tag_string,bits_per_sample,sample_fmt,sample_rate,channels -of json .shokunin/audio/corpus/live/round-22/executor/native_pcm24.wav` — exit 0; PCM24 metadata above.
- `python3 -c 'import importlib.util; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print("pcm24",m.measure("candidate",(.12,0,24000,False),".shokhun/audio/corpus/live/round-22/executor/native_pcm24.wav")["failures"]); print("pcm16",m.measure("candidate",(.12,0,24000,False),".shokhun/audio/corpus/live/round-22/executor/native_pcm16.wav")["failures"])'` — exit 1; failed setup, string `path` has no `relative_to`.
- `ffprobe -v error -show_entries stream=codec_name,codec_tag_string,bits_per_sample,sample_fmt,sample_rate,channels -of json .shokhun/audio/corpus/live/round-22/executor/native_pcm16.wav` — exit 0; PCM16 metadata above.
- `python3 -c 'import importlib.util; from pathlib import Path; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print("pcm24",m.measure("candidate",(.12,0,24000,False),Path(".shokhun/audio/corpus/live/round-22/executor/native_pcm24.wav"))["failures"]); print("pcm16",m.measure("candidate",(.12,0,24000,False),Path(".shokhun/audio/corpus/live/round-22/executor/native_pcm16.wav"))["failures"])'` — exit 1; failed setup, relative scratch path is outside `ROOT`.
- `python3 -c 'import importlib.util; from pathlib import Path; p=".shokhun/audio/corpus/fixtures/measure_audio.py"; s=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); base=Path(".shokhun/audio/corpus/live/round-22/executor").resolve(); print("pcm24",m.measure("candidate",(.12,0,24000,False),base/"native_pcm24.wav")["failures"]); print("pcm16",m.measure("candidate",(.12,0,24000,False),base/"native_pcm16.wav")["failures"])'` — exit 1; failed setup because that shell command contained misspelled `.shokhun` paths. No failed command above is evidence of input acceptance or rejection.
