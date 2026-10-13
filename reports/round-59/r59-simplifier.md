# R59 simplifier — keep the valid-bits pair local

## Recommendation

If the R59 original pair is confirmed measured, use the smallest R58-shaped integration: a deterministic builder for just the two R59 files, two uniquely named opt-in modes, and the existing UI measurement call on each selected WAV. Keep the pair under `corpus/live/round-59/`; use separate receipt paths/mode names. Do not add a generic extensible-WAV builder, header parser, decoder policy, valid-bit predicate, or abstraction shared across rounds. Preserve `format_failures()`, UI thresholds, canonical artifacts, normal mode, prior probes, and comparison families/sections. The existing predicate checks ffprobe's PCM16/16-bit, 48-kHz mono output, not `wValidBitsPerSample`; passing it cannot establish valid-bit enforcement.

Integration is conditional on measured R59 inputs: direct RIFF parsing confirms fmt40/tag `0xfffe`/cbSize22/mask `0x4`/PCM subtype, mono 48 kHz, 16-bit container, valid bits 13 versus 16, identical payload with all signed values divisible by eight, and only the valid-bits header field changed; ffprobe, SoX, and unchanged project UI measurements all run. Then preserve the actual decoded comparison and numeric outcomes. If either file is rejected, vectors differ, or a numeric gate fails, report that result rather than widening or altering the predicate/thresholds. Do not presume the declared 78-receipt replay count; it applies only if both selected modes generate receipts.

## Scope and command boundary

Read `/tmp/mission-audio-standing.md`, R59's LOG declaration, R58 reports, `build_artifacts.py`, and `measure_audio.py`. This lane performed source/report review only: no shell command, generator, RIFF parser, ffprobe, SoX, project measurement, runner invocation, or receipt. Accordingly this report has no R59 command exit codes, directly observed header, metadata, decoded vector comparison, metrics, or receipt. R59 executor scratch contains `generate.py`, `valid-13.wav`, `valid-16.wav`, and `.f32` files, but their presence is not evidence I independently verified. No setup command failed in this lane.

Source inspection: the current R58 path is explicit and round-local (`build_ui_extensible_valid14_probe`, two flags, one supplemental `measure("ui", SPECS["ui"], path)` branch); it does not require a generic abstraction. `format_failures()` compares sample rate/channels and codec/`bits_per_sample` only. Keep R59 source changes limited to its own pair builder and two opt-in selections, with no changes to that predicate or shared quality claims.

## R58 precedent (not R59 evidence)

The R58 executor's report records direct header parse: both files 11,588 bytes, RIFF size 11,580, fmt40/tag `0xfffe`, mono/48,000 Hz, byte rate 96,000, block align 2, container16, cbSize22, mask `0x4`, PCM subtype GUID `0100000000001000800000aa00389b71`, data 11,520 bytes. Only valid bits 14 versus 16 differed; the shared payload SHA-256 was `0b40e3c0f28aa6a50937f87c0fa260b2100f97572dbc8fdf517cea981e79b4fc`, all samples divisible by four. This demonstrates a simple fixture is enough; it does not supply R59 evidence.

Exact commands and exits as recorded by the R58 executor:

```sh
python3 ".shokunin/audio/corpus/live/round-58/executor/generate.py"  # 0
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav"  # 0; same with valid-16.wav: 0
sox ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav" -t f32 -e floating-point ".shokunin/audio/corpus/live/round-58/executor/valid-14.wav.f32"  # 0; same with valid-16.wav: 0
```

ffprobe reported both as `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `0.120000`; the report says SoX vectors each had 5,760 samples and were exactly equal (max absolute difference 0). Direct project measurement command for valid14 (exit 0), repeated with `valid-16.wav` (exit 0):

```sh
python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-58/executor/valid-14.wav")))'
```

Both reported 5,760 samples, `.12` s, peak `0.3153076171875`, RMS `-14.629479252569332 dBFS`, centroid `1129.9910331085607 Hz`, bandwidth `412.58546294347246 Hz`, LUFS null, and `failures: []`. These are direct function results, not runner receipts. R58 executor's first relative-path measurement commands exited 1 because the function needs a corpus-relative returned path; corrected absolute-path calls exited 0. R58 alternate noted one malformed inspection command before its corrected inspection (setup only). Keep such setup errors distinct from decode failures, gate failures, and receipts.

R58 establishes only behavior reported for its one payload/header and local tools, not valid-bit enforcement, resolution/fidelity, arbitrary valid-bit handling, audibility, quality, compatibility, or production suitability. The same limits apply to any R59 result; no fidelity or perceptual claim follows from this integration.

## Write boundary

This report is the only file changed by this lane. No source, LOG, SCORECARD, canonical artifact, other report, or executor/alternate scratch was changed; no commit or push was made.
