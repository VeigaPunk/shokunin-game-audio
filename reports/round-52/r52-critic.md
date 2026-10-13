# R52 critic — unsigned PCM8 offset, scaling, and decode isolation

## Scope

I read the R52 declaration and the independent pair at `corpus/live/round-52/alt/`. I made no changes to shared source, LOG, SCORECARD, canonical artifacts, or other reports. This check targets possible false isolation from unsigned PCM8 centering/scaling, ffprobe metadata, SoX decode, and the other existing UI checks. Conclusions apply only to this constructed pair.

## Commands and evidence

From the repository root, I reran the independent generator:

```sh
python3 .shokunin/audio/corpus/live/round-52/alt/generate_pair.py
```

Exit **0**. It produced `candidate_pcm8.wav` (SHA-256 `0020bae326c373083f0e25be9b9362ef628b3ae0f2daf3942e5dee14d48c706c`, 5,804 bytes) and `control_pcm16.wav` (SHA-256 `40ba4ae4a7231b9072a29b734005a4f64e87331d91b49c4cd93582daecbb6db2`, 11,564 bytes).

For each file I ran the following command (exit **0** for both):

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,sample_fmt:format=duration -of json <file>
```

The PCM8 candidate reports `codec_name=pcm_u8`, `sample_fmt=u8`, `bits_per_sample=8`, 48,000 Hz, mono, duration `0.120000`; the control reports `pcm_s16le`, `s16`, 16 bits, 48,000 Hz, mono, duration `0.120000`. Thus the format distinction is present in actual stream metadata, not inferred from the WAV filename.

The pair's unchanged project-measurer command:

```sh
python3 .shokunin/audio/corpus/live/round-52/alt/measure_pair.py
```

exited **0**. It calls `measure(..., SPECS["ui"], path)` from the unmodified `measure_audio.py`. PCM8 measured duration `0.12 s`, peak `0.34375`, RMS `-14.981981404018596 dBFS`, centroid `2897.653252566734 Hz`; its only failure is `format: expected PCM16`. PCM16 has the same duration, peak, RMS, and centroid, with no failures. Both satisfy the existing UI non-format gates: duration within ±0.001 s, peak < .95 and RMS >= .001 linear amplitude (measured RMS is about 0.178), centroid within 250–4000 Hz. Centroid is relatively high within that band but not out of bounds. Bandwidth is reported as `5023.065492084627 Hz`; bandwidth is not a UI gate here. Integrated LUFS is null for both and is not the RMS gate.

I decoded both files directly with SoX (each command exited **0**):

```sh
sox .shokunin/audio/corpus/live/round-52/alt/candidate_pcm8.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/alt/pcm8.f32
sox .shokunin/audio/corpus/live/round-52/alt/control_pcm16.wav -t f32 -e floating-point .shokunin/audio/corpus/live/round-52/alt/pcm16.f32
```

Each output contains 5,760 little-endian float32 samples (23,040 bytes). Both decoded byte streams have SHA-256 `dc30251b3580c197f2937ce9c48b716ee87d56470b9fd6bb78cd1be4d34a01b6`. Elementwise comparison is exact: equal arrays, maximum absolute difference `0.0`, differing samples `0`; PCM8 decoded range is `[-0.34375, 0.2734375]`.

I inspected the pair generator's construction as an offset/scaling cross-check: it computes signed quantized values `d`, stores PCM8 as `u8 = d + 128`, and stores the signed PCM16 control as `d * 256`. For this encoding, subtracting the unsigned-8 midpoint and scaling by 256 yields the same normalized integer grid as the PCM16 control. The exact SoX decoded-vector match independently confirms there was no observed missing-128 offset or scale mismatch in this pair. It does not establish behavior for arbitrary PCM8 values or other decoders.

## Assessment and limits

No falsifying issue was found for the selected matched fixture: the correct unsigned codec/depth is reported, all non-format UI gates pass on both, PCM8 alone fails the PCM16 format predicate, and direct SoX f32 outputs are exact matches. No numeric UI fit failed and no transcription correction was needed. This is not evidence for general PCM8 conversion, codec handling, fidelity, audibility, quality, rights, production, engine behavior, or promotion.
