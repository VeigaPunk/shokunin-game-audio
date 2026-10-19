source: S006 — host `ffmpeg -hide_banner -h filter=ebur128` (n9.0.1) — options `dualmono` (default false), `panlaw` (default −3.01029995663978), `peak`; S006 companion — https://raw.githubusercontent.com/FFmpeg/FFmpeg/n9.0.1/libavfilter/f_ebur128.c — l.172-173 (option defaults), l.783-784 (`integrated_loudness -= pan_law` for mono + dual_mono); S001 — ITU-R BS.1770-5 (11/2023) — Annex 1 l.322-323 (−3.01 LKFS for a 0 dBFS tone on one front channel), Annex 2 l.788-789 ("3 dB under-read for an unfortunately-phased tone at a quarter of the sampling frequency"); S015 — same standard and Annex 2 example, with the phase qualifier preserved; S002 — EBU R 128 (11/2023) — item (m) "True Peak Level of a programme shall not exceed −1 dBTP"; S003 — ASWG-R001 v1.10 (Aug 2013, third-party mirror) — rec. 7 (≤ −1 dBTP) and rec. 11 (stereo and surround); S012 — own-work `corpus/fixtures/measure_audio.py` — l.82-88 (single `ebur128=peak=true` call, only integrated loudness parsed) and l.95 (sample-peak level gate)
verified-at: 2026-10-19 (ffmpeg n9.0.1, SoX_ng 14.8.0.1, numpy 2.5.3 host; FFmpeg source at tag n9.0.1; the 17 canonical WAVs at base defbe128)
recheck: for f in $(ls corpus/artifacts/*.wav | xargs -n1 basename | sed 's/\.wav$//'); do s=$(ffmpeg -hide_banner -nostats -i corpus/artifacts/$f.wav -af "ebur128=peak=true+sample" -f null - 2>&1 | sed -n '/Summary:/,$p'); tp=$(echo "$s" | grep -A1 'True peak:' | grep -oE 'Peak: +[-0-9.inf]+' | tr -s ' ' | cut -d' ' -f2); sp=$(echo "$s" | grep -A1 'Sample peak:' | grep -oE 'Peak: +[-0-9.inf]+' | tr -s ' ' | cut -d' ' -f2); im=$(ffmpeg -hide_banner -nostats -i corpus/artifacts/$f.wav -af "ebur128=metadata=1,ametadata=mode=print:key=lavfi.r128.I" -f null - 2>&1 | grep -oE 'lavfi.r128.I=[-0-9.inf]+' | tail -1 | cut -d= -f2); id=$(ffmpeg -hide_banner -nostats -i corpus/artifacts/$f.wav -af "ebur128=metadata=1:dualmono=true,ametadata=mode=print:key=lavfi.r128.I" -f null - 2>&1 | grep -oE 'lavfi.r128.I=[-0-9.inf]+' | tail -1 | cut -d= -f2); echo "$f SP=$sp TP=$tp I=$im Idual=$id"; done

# ebur128 on the lane's mono fixtures: dual-mono reads +3.010/+3.011 LU, and the sample-peak gate does not bound true peak

**Claim.** Two measurement conventions change the numbers a reader gets from the lane's 17 mono 48 kHz PCM16 fixtures under ffmpeg n9.0.1 `ebur128`:

1. **Mono vs dual-mono.** By default a mono file is metered as one front channel. With `dualmono=true` the integrated loudness is raised by +3.010/+3.011 LU on every fixture that clears the gate (f_ebur128.c l.783-784 subtracts `pan_law`, default −3.01029995663978, l.173). BS.1770-5 gives the reason: a tone "applied to the left, centre, or right channel input" reads −3.01 LKFS (Annex 1, l.322-323), so the same mono asset reproduced centred on two speakers reads about 3.01 LU louder than when metered as one channel. Any LUFS figure quoted for a mono game asset must name which convention it used.
2. **Sample peak vs true peak.** The harness's level gate is a decoded **sample**-peak test (`if peak >= .95 or rms < .001`, `measure_audio.py:95`); its ebur128 call (`measure_audio.py:83`) requests `peak=true` but only the integrated-loudness line is parsed (l.84). On the canonical set, true peak exceeds sample peak by up to ≈ 1.1–1.2 dB (estimator-dependent, see Observed), and `impact.wav` crosses −1 dBTP (−0.7 dBTP) while its sample peak −1.8434 dBFS passes the `< .95` FS gate. The −1 dBTP ceilings of S002 (m) and S003 rec. 7 apply to the programme / title mix, so a per-asset true peak above −1 is **telemetry, not a violation** — the finding is that the sample-peak gate does not bound true peak.

## Observed (2026-10-19)

Sample/true peak from the ebur128 summary (0.1 dB display resolution), integrated loudness from `ebur128=metadata=1` (`lavfi.r128.I`, 0.001 resolution), 4× soxr reference peak from `aresample=192000:resampler=soxr:precision=28,astats` — all from the `recheck:` loop above plus `ffmpeg -hide_banner -nostats -i corpus/artifacts/<f>.wav -af "aresample=192000:resampler=soxr:precision=28,astats=measure_overall=Peak_level:measure_perchannel=none" -f null -` 2026-10-19.

| artifact | SP dBFS | TP dBTP | soxr 4× peak | I mono LUFS | I dual-mono | Δ LU |
|---|---|---|---|---|---|---|
| ui | −8.5 | −8.5 | −8.499 | −70.000 (floor → null) | −70.000 | — |
| ui_alt | −9.9 | −9.9 | −9.920 | −70.000 | −70.000 | — |
| ui_third | −8.5 | −8.5 | −8.499 | −70.000 | −70.000 | — |
| impact | −1.8 | **−0.7** | −0.737 | −70.000 | −70.000 | — |
| impact_alt | −2.4 | −2.4 | −2.427 | −70.000 | −70.000 | — |
| impact_third | −6.8 | −6.7 | −6.829 | −18.220 | −15.210 | +3.010 |
| movement | −5.4 | −5.1 | −5.171 | −70.000 | −70.000 | — |
| movement_alt | −3.9 | −3.1 | −3.149 | −70.000 | −70.000 | — |
| movement_third | −6.2 | −6.2 | −6.194 | −70.000 | −70.000 | — |
| ambience | −15.2 | −15.2 | −15.159 | −30.697 | −27.686 | +3.011 |
| ambience_alt | −14.0 | −14.0 | −13.991 | −24.688 | −21.677 | +3.011 |
| ambience_third | −13.0 | −13.0 | −12.956 | −18.992 | −15.982 | +3.010 |
| stem | −9.8 | −9.8 | −9.794 | −15.761 | −12.750 | +3.011 |
| stem_sections | −15.3 | −15.3 | −15.271 | −24.704 | −21.694 | +3.010 |
| stem_layer | −24.4 | −24.4 | −24.437 | −29.259 | −26.249 | +3.010 |
| stem_layer_alt | −26.0 | −26.0 | −26.022 | −32.698 | −29.688 | +3.010 |
| stem_layer_third | −26.0 | −26.0 | −26.022 | −32.628 | −29.618 | +3.010 |

- Exact decoded sample peaks (`python3 -c` over `sox <f> -t f32 -e floating-point -`, 20·log10 max|x|): impact −1.8434, movement −5.3603, movement_alt −3.8857, impact_third −6.8185 dBFS — 2026-10-19. Overshoot TP − SP on `impact`: 1.107 dB by the soxr 4× estimator (−0.737 − (−1.843)); ≈ 1.18 dB by the wave-1 reviewer's 4× aresample reading (`reports/round-101/r101-reviewer.md`); ebur128's own summary shows −1.8 → −0.7 at 0.1 dB resolution. movement_alt ≈ +0.74 dB, movement ≈ +0.19 dB (soxr). 13 of 17 artifacts show TP = SP at the 0.1 dB display step (all but impact, impact_third, movement, movement_alt).
- Files over −1 dBTP: 1 of 17 (`impact`).
- The eight artifacts of ≤ 0.36 s (ui ×3, impact, impact_alt, movement ×3) read the −70 floor in both conventions (no complete 400 ms block); `impact_third` (0.40 s, 19200 samples) is the only SFX with a measured integrated loudness.
- The dual-mono offset is +3.010/+3.011 LU on all nine gated files (impact_third, ambience ×3, stem ×5): 9 of 9. (Corrected before admission: the first draft of this entry said nine floor-read / eight gated; the round-101 probe seat's receipt flagged the reversed split, `reports/round-101/r101-truepeak.md`, and the table above shows 8 floor / 9 gated.)

## Inference

- [INFERENCE] The ≈ 1.1 dB inter-sample overshoot on `impact.wav` is the high-frequency transient class BS.1770-5 Annex 2 describes ("the higher the frequency of the peak-sample metered signal, the worse the potential error", pdftotext -layout l.787); the lane's synthetic impacts carry broadband attacks.
- [INFERENCE] A shipped mix that sums several such SFX can exceed the −1 dBTP programme ceiling even when every asset passes the sample-peak gate; whole-mix measurement is the relevant test (see `2026-10-19-game-loudness-whole-mix-protocol.md`).

## Unknown

- The true-peak meter's own error bound on these signals (ffmpeg's summary rounds to 0.1 dB; the soxr 4× column is a second estimator, not a reference meter).
- Whether a game engine's mono-to-stereo panning matches the −3.01 dB pan law assumed by `dualmono=true` (engine-side, Adjacent — game-dev lanes).

coverage: corpus/README.md coverage map — Core, gap entered round 101: loudness-measurement conventions (mono/dual-mono, true peak)
