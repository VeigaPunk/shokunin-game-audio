# Round 46 executor — UI centroid boundary pair

## Result

Generated two original 5760-frame (0.120 s), 48 kHz, mono PCM16 scratch controls under `corpus/live/round-46/executor/`. Measurement used the project `measure()` function, which invokes SoX to decode `f32` and computes the whole-wave magnitude-FFT weighted centroid. The below control is strictly below the ordinary UI lower bound and has **only** the expected spectrum failure; the above control is just above the lower bound and has no failures. These are numerical fixture controls, not sound-quality evidence.

| Control | SHA-256 | Frames / format | Project-decoded centroid | Peak FS | RMS dBFS | Project failures |
|---|---|---|---:|---:|---:|---|
| `ui-centroid-below.wav` | `fff9d981fe76c9163ba6a0db851e498b15fe193a1597427c8b73993b4666bfdf` | 5760, 48k mono PCM16 | 249.71389590882862 Hz | 0.279754638671875 | -18.327838866709165 | `spectrum: centroid outside fixture band` only |
| `ui-centroid-above.wav` | `6e453ff6cdf02e3fb72e0ebb0734f39a566a823841da8949187ad73d74a90a2a` | 5760, 48k mono PCM16 | 250.3250670185918 Hz | 0.27984619140625 | -18.32783946042307 | none |

Both measured durations are 0.12 s; both meet format, peak (<.95), and RMS (>=.001) gates. Integrated LUFS was null for both and is not used as a gate. They have distinct hashes. No claim of exact-250 Hz equality is made.

## Recipe and measured fitting

For each final WAV, `n=5760`, `t=np.arange(n)/48000`, `x=.28*np.sin(2*pi*f*t)*np.hanning(n)`, then quantize with `np.rint(np.clip(x,-1,1)*32767).astype('<i2')` and write one-channel, 2-byte samples at 48000 Hz using Python `wave`. Final nominal tone frequencies were 225 Hz (below) and 226 Hz (above). Windowing, PCM16 quantization, and decoded whole-wave FFT determine the actual project centroid; nominal frequency is not treated as the measured result.

An initial fitting pair at nominal 230 Hz and 270 Hz produced decoded centroids **253.80451803986455 Hz** and **293.3534382718592 Hz**. Both were above the threshold, so that candidate pair did not bracket the boundary and was discarded; it was a numeric fit iteration, not a runner/gate failure. Further 225/226 Hz measurements yielded the final strict polarity shown above. No shell setup or project measurement errors occurred.

## Exact shell command and exit

Command used to measure both final files via the project helper (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({k:m.measure(k,(.12,250,4000,False),Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-46/executor/ui-centroid-"+k+".wav")) for k in ("below","above")},indent=2))'
```

Direct SoX-decoded centroid work confirmed the same strict side (below 250; above 250); the exact project helper result above is the reported measurement. No audio audition or perceptual, production, rights, engine, publishing, promotion, or quality inference was performed.
