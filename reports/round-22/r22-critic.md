# Round 22 critic — format isolation and metadata falsification

## Scope and verdict

I made no source, canonical WAV, shared-log, scorecard, or other-report edits; no commits. The tested question is whether a bit-depth negative is isolated by the intended format predicate rather than audio-quality gates, and whether metadata permits an unambiguous predicate. Results support that the current `measure()` accepts matched 48 kHz mono PCM16 and PCM24 inputs with no failures, and also accepts PCM float32. This is a useful falsification of the baseline, not evidence an integrated new predicate works. Keep any conclusion limited to these local WAV encodings and this SoX/ffprobe setup.

## Evidence

Using `stem_layer_third.wav` as the same source, SoX generated temporary 16-bit and 24-bit WAVs under `.shokunin/audio/corpus/live/`, then removed them in `finally`. Both `measure("stem_layer_third", SPECS[...], path)` results had `failures: []`, 48,000 Hz mono, duration 4 s, peak 0.04998779296875, RMS -31.66724765274306 dBFS, centroid 287.93805923844434 Hz, and identical reported seam values. ffprobe distinguished them:

- PCM16: `codec_name=pcm_s16le`, `sample_fmt=s16`, `bits_per_sample=16`.
- PCM24: `codec_name=pcm_s24le`, `sample_fmt=s32`, `bits_per_sample=24`.

The PCM24 `sample_fmt=s32` is the key metadata trap: `sample_fmt` describes decoder representation, not the WAV's stored precision here. A rule checking only `sample_fmt == s16` would reject the matched PCM16 positive too; a rule checking only `sample_fmt != s32` would accept this 24-bit negative. Prefer an explicit stream `codec_name`/`bits_per_sample` predicate (for this narrowly scoped PCM16 WAV requirement), and retain sample rate/channel checks. Do not infer bit depth from `sample_fmt` alone.

A separate SoX-generated 48 kHz mono float WAV reported `pcm_f32le`, `sample_fmt=flt`, `bits_per_sample=32`, yet also passed `measure()` with `failures: []` and the same displayed metrics. This reinforces that a codec/encoding check is necessary, not just a PCM24 special case. No test here supports arbitrary codec handling, extensible WAV variants, multi-stream selection, or other containers.

## Failure / limits

Two first attempts failed as test harness setup, not as audio results. The first wrote the temp PCM24 WAV to `/tmp`; `measure()` raised `ValueError` because its result path must be relative to corpus `ROOT` (exit 1). The second used a relative corpus path and hit the same `relative_to(ROOT)` error (exit 1). The corrected tests put scratch inside corpus `live/` and used resolved paths. No audio fit failed; the metadata distinction did not fail. These setup errors should not be represented as codec rejection or negative-control passes.

This is a single source waveform / local toolchain probe, not replay of runner modes, canonical-hash validation, or independent reproducibility. The source's level/spectrum gates are passed by both widths, which is precisely why it exposes the missing format distinction. No perceptual, sample-rights, engine, publishing, or general compatibility claim.

## Shell commands and exit codes

Every shell invocation in this task is listed below; command lines are reproduced exactly. The first two are failed setup attempts. The corrected matched PCM16/PCM24 and float32 probes both exited 0.

1. Exit **1** — `/tmp` scratch attempt:

```sh
python3 -c 'import subprocess,tempfile,pathlib,importlib.util,json
root=pathlib.Path(".shokunin/audio/corpus")
src=root/"artifacts/stem_layer_third.wav"
tmp=pathlib.Path(tempfile.gettempdir())/"r22-critic-stem24.wav"
subprocess.run(["sox",str(src),"-b","24",str(tmp)],check=True)
p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels","-of","json",str(tmp)],check=True,capture_output=True,text=True)
print(p.stdout.strip())
spec=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py")
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print(json.dumps(m.measure("stem_layer_third",m.SPECS["stem_layer_third"],tmp),sort_keys=True))
tmp.unlink()
'
```

2. Exit **1** — relative-path scratch attempt:

```sh
python3 -c 'import subprocess,tempfile,pathlib,importlib.util,json
root=pathlib.Path(".shokunin/audio/corpus")
src=root/"artifacts/stem_layer_third.wav"
paths=[root/"live/r22-critic-16.wav",root/"live/r22-critic-24.wav"]
try:
 for bits,path in zip((16,24),paths): subprocess.run(["sox",str(src),"-b",str(bits),str(path)],check=True)
 spec=importlib.util.spec_from_file_location("m",".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 for bits,path in zip((16,24),paths):
  p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels","-of","json",str(path)],check=True,capture_output=True,text=True)
  print("BITS",bits,"META",p.stdout.strip(),"MEASURE",json.dumps(m.measure("stem_layer_third",m.SPECS["stem_layer_third"],path),sort_keys=True))
finally:
 for path in paths: path.unlink(missing_ok=True)
'
```

3. Exit **0** — corrected matched 16/24-bit test (resolved paths; scratch removed):

```sh
python3 -c 'import subprocess,pathlib,importlib.util,json
root=pathlib.Path(".shokunin/audio/corpus").resolve()
src=root/"artifacts/stem_layer_third.wav"
paths=[root/"live/r22-critic-16.wav",root/"live/r22-critic-24.wav"]
try:
 for bits,path in zip((16,24),paths): subprocess.run(["sox",str(src),"-b",str(bits),str(path)],check=True)
 spec=importlib.util.spec_from_file_location("m",str(root/"fixtures/measure_audio.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 for bits,path in zip((16,24),paths):
  p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels","-of","json",str(path)],check=True,capture_output=True,text=True)
  print("BITS",bits,"META",p.stdout.strip(),"MEASURE",json.dumps(m.measure("stem_layer_third",m.SPECS["stem_layer_third"],path),sort_keys=True))
finally:
 for path in paths: path.unlink(missing_ok=True)
'
```

4. Exit **0** — float32 challenge (scratch removed):

```sh
python3 -c 'import subprocess,pathlib,importlib.util,json
root=pathlib.Path(".shokunin/audio/corpus").resolve(); src=root/"artifacts/stem_layer_third.wav"; path=root/"live/r22-critic-float32.wav"
try:
 subprocess.run(["sox",str(src),"-e","floating-point","-b","32",str(path)],check=True)
 spec=importlib.util.spec_from_file_location("m",str(root/"fixtures/measure_audio.py")); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_name,sample_fmt,bits_per_sample,sample_rate,channels","-of","json",str(path)],check=True,capture_output=True,text=True)
 print("META",p.stdout.strip(),"MEASURE",json.dumps(m.measure("stem_layer_third",m.SPECS["stem_layer_third"],path),sort_keys=True))
finally: path.unlink(missing_ok=True)
'
```
