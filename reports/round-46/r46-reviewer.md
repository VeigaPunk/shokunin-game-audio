# R46 reviewer — minimal opt-in modes

**Recommendation:** keep the ordinary UI spectrum predicate and `SPECS`/canonical fixtures unchanged. Two explicit opt-in modes are enough: `--probe-ui-centroid-below` and `--probe-ui-centroid-above`, each selecting one original 5760-frame scratch WAV, then measure it against the existing UI spec. Avoid a new generic framework or any threshold/predicate modification. The R29 lower-centroid pair addressed pairwise distinctness, not this ordinary absolute lower-band predicate.

I used the project's `measure_audio.measure()` path, which decodes with SoX to f32 and calculates whole-wave magnitude-FFT centroid. The selected executor candidates are 48 kHz mono PCM16, duration 0.12 s, and have distinct SHA-256:

| mode / file | SHA-256 | decoded centroid | peak | RMS dBFS | bandwidth | result against ordinary 250–4000 Hz UI spec |
|---|---|---:|---:|---:|---:|---|
| below `executor/ui-centroid-below.wav` | `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf` | 249.71389590882862 Hz | 0.279754638671875 | -18.327838866709165 | 625.8273248256264 Hz | sole `spectrum: centroid outside fixture band` |
| above `executor/ui-centroid-above.wav` | `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a` | 250.3250670185918 Hz | 0.27984619140625 | -18.32783946042307 | 625.8448652317335 Hz | no failures |

The first reviewer draft transcribed the below peak as 0.279754150390625; parent corrected it against executor and critic project measurements to 0.279754638671875 before integration. This was a report transcription error, not a failed fit, setup error, or gate outcome. Both decoded fixtures satisfy format, duration, peak (<.95), and RMS (>=.001) checks. `integrated_lufs` was `null` for both; it is not used for this acceptance. No exact-250-Hz equality or general band-calibration claim follows.

Numeric fitting is distinct from setup and transcription errors. The executor's measured 225 Hz nominal trial produced 249.71389590882862 Hz and still failed spectrum; 226 Hz produced 250.3250670185918 Hz and passed. Earlier executor nominal trials 180/190/200/210/215/218/220 Hz decoded centroids 203.49356156298964/214.04197054391747/224.82545582968012/233.60780677342987/238.72811691578477/241.74486157112997/243.28423052433737 Hz and failed solely spectrum. The alt-generated named `below.wav` and `above.wav` decoded to 720.4544798769202 and 469.7553367212557 Hz respectively, both passing; nominal sine frequency is therefore not a substitute for measured whole-wave centroid. Do not treat the alt pair as the calibration bracket.

Commands I ran (from repo root):

- `python -c 'import sys, pathlib, hashlib; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; root=pathlib.Path(".shokunin/audio/corpus/live/round-46");
for p in sorted(root.rglob("*.wav")):
 r=m.measure(p.stem, m.SPECS["ui"], p); print(p, hashlib.sha256(p.read_bytes()).hexdigest(), r)'` — exit 1. Setup/path error: relative paths were not under the helper's corpus root (`ValueError` from `relative_to`); no numeric result from that invocation.
- `python -c 'import sys, pathlib, hashlib; sys.path.insert(0, ".shokunin/audio/corpus/fixtures"); import measure_audio as m; root=pathlib.Path(".shokunin/audio/corpus/live/round-46").resolve();
for p in sorted(root.rglob("*.wav")):
 r=m.measure(p.stem, m.SPECS["ui"], p); print(p, hashlib.sha256(p.read_bytes()).hexdigest(), r)'` — exit 0; results above.

This is numerical fixture calibration only. No audition or inference about quality, perception, timbre, novelty, production, rights, engine behavior, publishing, or promotion.
