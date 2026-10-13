# R57 simplifier — valid-bits pair, no framework

## Recommendation

Keep the R57 probe to one narrow paired builder and two opt-in modes, matching the existing R55/R56 pattern. Generate the same UI-shaped 5,760-frame mono/48 kHz PCM16 payload in WAVE_FORMAT_EXTENSIBLE fmt40 headers, PCM subtype GUID, cbSize22, mask `0x4`, 16-bit container; set only `wValidBitsPerSample` to 15 or 16. Expose separate valid-15 and valid-16 runner options, measure the selected artifact with unchanged `measure("ui", SPECS["ui"], path)`, and leave format predicates, UI thresholds, canonical fixtures, and normal behavior untouched. Do not build a generic WAVE/header framework.

The executor’s measured pair is already a minimal candidate: its 15/16 files differ only at valid-bits metadata and both ffprobe/project measurements pass. SoX also decoded identical vectors for this particular pair. This does not establish that 15 valid bits are independently meaningful or that all valid-15 headers/decoders behave this way. In particular ffprobe reports the container codec as `pcm_s16le`, `sample_fmt=s16`, and 16 bits for both, not the valid-bits field. Report the actual header and decoder observations, not a general acceptance claim.

## Evidence collected

Read `/tmp/mission-audio-standing.md`, the R57 declaration in `.shokunin/audio/LOG.md`, the R56 executor/reviewer/alternate/verifier/simplifier reports, and the existing builder and measurer. The current integrated source has R56 mask-zero/center modes but no R57 valid-bits modes. I made no source edits and ran no integrated runner or receipt/replay command.

Inspected executor scratch RIFF headers directly (Python inspection; no shell command): both files are 11,588 bytes, tag `0xfffe`, mono/48,000 Hz, 16-bit container, mask `0x4`, same PCM subtype GUID `0100000000001000800000aa00389b71`; `valid-15.wav` says 15 valid bits and `valid-16.wav` says 16. SHA-256: valid15 `d3835a35014b3536c1710aafed8a104ef32eaa84acb37c87213127785f18175c`; valid16 `bd7d95901935c0effe21fd64e44a47487372be9d0c80f86cc725380df0352f47`.

Commands and outcomes:

- `for f in .shokunin/audio/corpus/live/round-57/executor/valid-{15,16}.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json "$f"; echo "ffprobe_exit=$?"; done` — exit **0**. Each ffprobe invocation exited 0 and reported `pcm_s16le`, `s16`, 48,000 Hz, mono, 16 bits/sample, duration `.120000` s.
- First project-measurer attempt used relative `Path(...)` arguments; both calls raised `ValueError` at `relative_to(ROOT)` and exited **1**, producing no receipts. This is a receiptless path/setup error, not a format rejection or failed numeric fit.
- Corrected command: `for f in "$PWD"/.shokunin/audio/corpus/live/round-57/executor/valid-{15,16}.wav; do echo "FILE=$f"; python3 -c 'import importlib.util; from pathlib import Path; s=importlib.util.spec_from_file_location("m", ".shokunin/audio/corpus/fixtures/measure_audio.py"); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(m.measure("ui",m.SPECS["ui"],Path("'"$f"'")))'; echo "measure_exit=$?"; done` — shell exit **0**, each measurement call exit **0**. Both returned duration `.12`, 48 kHz mono `pcm_s16le`/16-bit, peak `.31536865234375`, RMS `-14.628519169868087 dBFS`, centroid `1123.322704293326 Hz`, bandwidth `276.15444981222976 Hz`, LUFS null, `failures: []`.
- `for f in "$PWD"/.shokunin/audio/corpus/live/round-57/executor/valid-{15,16}.wav; do out="$f.f32"; sox "$f" -t f32 -e floating-point "$out"; echo "sox_exit=$? bytes=$(wc -c < "$out") sha256=$(sha256sum "$out" | cut -d' ' -f1)"; done` — shell exit **0**, both SoX calls exit **0**, outputs 23,040 bytes with SHA-256 `d80f13858e4fdcf641f2164b440a99a42711fd4213239ad809c8136ee4620ce7` each.
- `python3 -c 'import numpy as np; from pathlib import Path; p=Path(".shokunin/audio/corpus/live/round-57/executor"); a=np.fromfile(p/"valid-15.wav.f32",dtype="<f4"); b=np.fromfile(p/"valid-16.wav.f32",dtype="<f4"); print("n",len(a),len(b),"equal",np.array_equal(a,b),"max_abs",float(np.max(np.abs(a-b))),"different",int(np.count_nonzero(a!=b)),"peak15",float(np.max(np.abs(a))),"peak16",float(np.max(np.abs(b)))'` — exit **0**; 5,760 samples each, exactly equal, max absolute difference 0, differing samples 0; both decoded peaks `.31536865234375`.

The setup failure is disclosed and is not evidence of a valid-15 rejection. There is no integrated runner receipt from this lane. Parent/verifier should record both integrated mode outcomes and preserve the declaration’s prior-72/canonical17/invalid/threshold replay contract; if a valid-15 decode/setup fails before a receipt, classify it separately from runner format validation.

## Limits and scope

Evidence is limited to these executor-generated mono PCM16 payload/header examples and this local ffprobe, SoX, and project measurer. Identical SoX vectors here are an observation, not a universal valid-bits conversion/fidelity claim. This report makes no general WAVE_FORMAT_EXTENSIBLE, standards-conformance, decoder-compatibility, audibility, quality, production, rights, engine, publishing, or promotion claim. Only `.shokunin/audio/reports/round-57/r57-simplifier.md` was written; no shared source, LOG, SCORECARD, canonical artifact, or other report was changed. No commit or push was made.
