# Round 31 executor report — measured joint sub-threshold UI pair

## Result

I found and measured a source-generated 48 kHz mono PCM16 pair: a 5,760-frame base and a 6,719-frame variant. Using the project’s direct measurement implementation, both pass their ordinary waveform checks when the variant duration is declared as `6719/48000` rather than the canonical UI duration. The measured duration delta is nonzero and below `.020 s`; the measured relative centroid delta is also nonzero and below `.10`, near `.10`. Therefore both comparator branches are false and the existing OR distinctness result is reject (no comparator code or threshold changed).

The 6,719-frame variant is approximately `.139979 s`; it is **not** the canonical `.120 s` UI duration, and this result makes no claim that it conforms to that duration. This is a numeric comparator probe only, not a perceptual, quality, cutoff-equality, rights, engine, publication, or promotion conclusion.

## Measurements

Source: `.38 * sin(2*pi*k*(700*t + 800*t*t)) * exp(-30*t)`, with `t = arange(frame_count)/48000`, rounded/clipped into mono little-endian signed PCM16. Base `k=1.0`, 5,760 frames. Variant `k=1.0855000000000001`, 6,719 frames. Fit selected by direct measurement scan because analytic multiplier did not predict the FFT centroid robustly.

- Base: duration `0.120000 s`; centroid `966.8966593379727 Hz`; sample rate 48000; mono `pcm_s16le`, 16-bit; ordinary failures `[]`.
- Variant: duration `0.139979 s` (ffprobe); centroid `1062.944... Hz` (see complete exact receipt in `fit_results.json`); sample rate 48000; mono `pcm_s16le`, 16-bit; ordinary failures `[]`.
- Absolute duration delta: `0.019978999999999997 s` (nonzero, `< .020`).
- Relative centroid delta, using the project comparator’s base denominator: `0.09935249842494516` (nonzero, `< .10`).
- Duration branch `delta >= .020`: false. Centroid branch `relative_delta >= .10`: false. Combined existing OR result: false/reject.
- SHA-256: base `4bb56ddf502e0d0249f191e90a57ebe0adff7bee7649efa2c402c905c4c53af9`; variant `4513f29dc5638f53b18cdf200e9f5f0786b930e7c15d38013a1e12e254c4cb6f`.

Full direct project measurement and scan are in `corpus/live/round-31/executor/fit_results.json`; exact generated WAVs and the reproducible fitting script are alongside it. Project function used: `measure_audio.py::measure`, including its ffprobe metadata, SoX-decoded samples, and full-waveform positive-frequency weighted FFT centroid. Variant spec used only for ordinary checking: `(6719/48000, 250, 4000, False)`; base spec: existing canonical `SPECS["ui"]`. No claim is made that applying the canonical `.120 s` duration spec to the longer variant would pass.

## Commands, exits, and setup

1. First direct-measurement script attempt: `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-31/executor/measure_fit.py` — exit 1. Setup error: `measure()` requires the measurement path under the fixtures’ `ROOT`; the script supplied a relative path and got `ValueError: ... is not in the subpath of .../corpus`. Excluded as a failed setup attempt. Corrected script resolves scratch paths to absolute paths under corpus `ROOT`.
2. Corrected exploratory fit: `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-31/executor/measure_fit.py` — exit 0. Twelve initial coefficients, all with ordinary checks passing; measured ratios ranged from `0.0016955919389860163` through `0.13531931846217268`, demonstrating nonmonotonic ratio behavior in this finite sampled fit. Full values were printed; these exploratory files were superseded by the final script outputs.
3. Fine fit and final artifact generation: `cd /home/vgpnk/Projects/prymeagnt/audio && python3 .shokunin/audio/corpus/live/round-31/executor/fit_joint.py` — exit 0. Scan `k=1.08..1.12` in `.0005` increments, selecting eligible measured ratio closest to `.10` while strictly below and with no ordinary failures. It selected `1.0855000000000001`; exact final measurement and complete scan saved to `fit_results.json`.
4. Metadata/hash receipt: `cd /home/vgpnk/Projects/prymeagnt/audio && sha256sum .shokunin/audio/corpus/live/round-31/executor/base.wav .shokunin/audio/corpus/live/round-31/executor/variant.wav && ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-31/executor/variant.wav` — exit 0; hashes and metadata above.

No runner integration, canonical source edits, threshold edits, shared LOG/SCORECARD edits, or commits were made. Scope touched only this report and `.shokunin/audio/corpus/live/round-31/executor/` scratch.
