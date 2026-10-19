source: S005 — https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/libavfilter/af_loudnorm.c — l.450-465 (first-frame short-input path), l.697-699 (3000 ms first chunk), l.740 + l.751-752 (192 kHz format negotiation); S014 — same source, l.740/l.751-752/l.808 (initial `FIRST_FRAME` and rate negotiation); S005 companion — https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/libavfilter/ebur128.c — l.550-553 and l.570-573 (`-HUGE_VAL` when no block clears the gates); S006 — host `ffmpeg -hide_banner -h filter=loudnorm` (n9.0.1) — option table; S001 — ITU-R BS.1770-5 (11/2023) — Annex 1 "Incomplete gating blocks … are not used" (pdftotext -layout l.258) and the −70 LKFS absolute gate (l.157)
verified-at: 2026-10-19 (ffmpeg n9.0.1 host; FFmpeg source at tag n9.0.1; BS.1770-5 PDF 11/2023)
recheck: run(){ ffmpeg -hide_banner -nostats -f lavfi -i "$1" -af "loudnorm=I=-24:TP=-1:LRA=11:print_format=json,astats=measure_overall=Peak_level:measure_perchannel=none" -f null - 2>&1 | grep -oE '"(input_i|output_i|normalization_type)" : "[^"]+"|Peak level dB: [-0-9.]+|Audio: pcm_f32le, [0-9]+ Hz' | tr '\n' ' '; echo; }; for d in 0.12 0.399 0.400 2.99 3.0 4; do printf 'dur=%s ' $d; run "sine=frequency=1000:sample_rate=48000:duration=$d,volume=-12dB"; done; for a in 0.001 0.0003; do printf 'amp=%s ' $a; run "aevalsrc=$a*sin(2*PI*1000*t):s=48000:d=2.5"; done

# ffmpeg loudnorm on short SFX: three regimes, selected by the gate and by a 3 s buffer check — not a loudness matcher below one gated block

**Claim.** With ffmpeg n9.0.1, `loudnorm=I=-24:TP=-1:LRA=11` (single pass) takes one of three paths on a mono 48 kHz input:

| Regime | Real trigger (source) | What it does | Rate at `loudnorm` / final output |
|---|---|---|---|
| **Peak-normalize** | whole input < 3000 ms **and** no 400 ms gating block clears the −70 LUFS absolute gate, so integrated loudness is `-inf` (ebur128.c l.550-553 / 570-573) | one linear gain `target_tp / peak` (af_loudnorm.c l.463, because `offset = +inf` makes `offset_tp` exceed TP) — the sound is peak-normalized to TP, not loudness-matched | 192000 Hz / 48000 Hz |
| **Linear loudness gain** | whole input < 3000 ms (af_loudnorm.c l.450: `in->nb_samples < frame_size(sample_rate, 3000)`) with ≥1 block above the gate | one linear gain to `I`, capped so the *sample* peak stays ≤ TP (l.453-463) | 192000 Hz / 48000 Hz |
| **Dynamic** | input ≥ 3000 ms (first chunk consumed is `frame_size(…, 3000)`, l.697), single pass | dynamic gain + limiter | 192000 Hz / 48000 Hz |

So for UI-length SFX (< 400 ms) loudnorm silently becomes a peak normalizer; for 0.4–3 s assets it is a linear gain capped by **sample** peak (the variable is named `true_peak`, but it is filled by `ff_ebur128_sample_peak`, l.456); at ≥ 3 s it takes the dynamic path. All three paths run inside `loudnorm` at 192 kHz; this recheck's final 48 kHz stream is downstream output resampling, not the filter's negotiated rate.


## Observed (2026-10-19, ffmpeg n9.0.1, 1 kHz sine at −12 dB unless stated)

| Input | input_i | output_i | type | out peak dB | `loudnorm` rate / final output rate |
|---|---|---|---|---|---|
| 0.12 s | −inf | −inf | linear | −1.000000 | 192000 / 48000 |
| 0.399 s | −inf | −inf | linear | −1.000000 | 192000 / 48000 |
| 0.400 s | −33.05 | −24.05 | linear | −21.013921 | 192000 / 48000 |
| 0.41 / 1.0 / 2.5 / 2.99 s | −33.05 | −24.05 | linear | −21.013921 | 192000 / 48000 |
| 3.0 s | −33.05 | −23.95 | dynamic | −20.969510 | 192000 / 48000 |
| 3.01 s | −33.05 | −23.95 | dynamic | −20.969512 | 192000 / 48000 |
| 4 s | −33.05 | −24.03 | dynamic | −20.969512 | 192000 / 48000 |
| 2.5 s, amp 0.001 (−60 dBFS) | −63.05 | −23.95 | linear | −20.950000 | 192000 / 48000 |
| 2.5 s, amp 0.0003 (−70.5 dBFS) | −inf | −4.05 | linear | −1.000000 | 192000 / 48000 |
| 2.5 s, amp 0.0001 (−80 dBFS) | −inf | −4.05 | linear | −1.000000 | 192000 / 48000 |
| `corpus/artifacts/ui.wav` (0.12 s) | −inf | −inf | linear | −1.000000 (input_tp −8.50) | 192000 / 48000 |
| `corpus/artifacts/stem_sections.wav` (4 s) | −24.68 | −23.95 | dynamic | −14.490638 (input_tp −15.27) | 192000 / 48000 |

Filter-rate witness (2026-10-19): `for d in 0.4 3.0; do ffmpeg -hide_banner -nostats -f lavfi -i "sine=frequency=1000:sample_rate=48000:duration=$d" -af 'loudnorm=I=-24:TP=-1:LRA=11:print_format=json,ashowinfo' -f null - 2>&1 | grep -m1 -E 'ashowinfo.*rate:[0-9]+'; done` → `rate:192000` at both durations. In n9.0.1, `frame_type` starts as `FIRST_FRAME` (l.808), so `query_formats()` negotiates 192000 Hz (l.740, l.751-752) before the first frame can switch the processing mode; the `Audio: pcm_f32le, 48000 Hz` line is the final output stream after downstream resampling.

Each row — the `recheck:` command (the two artifact rows: `ffmpeg -hide_banner -nostats -i corpus/artifacts/<f>.wav -af "loudnorm=I=-24:TP=-1:LRA=11:print_format=json,astats=measure_overall=Peak_level:measure_perchannel=none" -f null - 2>&1 | grep -oE '"(input_i|input_tp|output_i|normalization_type)" : "[^"]+"|Peak level dB: [-0-9.]+'`) 2026-10-19.

- The 400 ms edge is exact: 0.399 s → `-inf`, 0.400 s → −33.05 (one complete block; BS.1770-5 Annex 1: "Incomplete gating blocks at the end of the measurement interval are not used", l.258).
- The length edge is exact: 2.99 s → `linear`, 3.0 s → `dynamic`.
- Length alone does not select peak-normalize: a 2.5 s tone below the −70 LUFS gate (−70.5 dBFS) is also peak-normalized to −1 dB — gaining ~69.5 dB of noise floor along with it.

## Inference

- [INFERENCE] Any lane SFX that `measure()` already reports as `integrated_lufs: null` (all eight ≤ 0.36 s artifacts read −70.0 in ebur128; see `2026-10-19-ebur128-dualmono-and-true-peak-on-fixtures.md`) would be peak-normalized, not loudness-matched, by a default single-pass loudnorm — so loudnorm cannot equalize perceived level across the UI/impact/movement set.
- [INFERENCE] Because the linear-path cap uses sample peak, a short linear-mode output can exceed TP in true-peak terms (see the K3 entry: `impact.wav` true peak sits ≈ 1.1–1.2 dB above its sample peak).

## Unknown

- Behaviour on ffmpeg versions other than n9.0.1 (the cited lines are pinned to that tag; master was not compared line-by-line by the L1).
- Two-pass `linear=true` behaviour (measured_* inputs) is not covered here; a reviewer re-run of that path is recorded in `reports/round-101/r101-reviewer.md` (K2 rows) and is not admitted by this entry.

coverage: corpus/README.md coverage map — Core, gap entered round 101: per-asset normalization tooling
