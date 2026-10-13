# R42 executor — decoded PCM16 peak fixtures

## Result

Generated two original UI-shaped 0.12 s probes under `corpus/live/round-42/executor/`. Both are 5760-frame, 48 kHz, mono PCM16 WAVs. The target is decoded absolute peak sample count, measured from the WAV bytes; the direct project measurement helper confirms one passes and one fails only the existing peak/level check.

| Target | SHA-256 | Decoded peak counts | Project helper peak | RMS dBFS | Centroid Hz | Failures |
|---:|---|---:|---:|---:|---:|---|
| 31129 | `7e6c11325d27c1e0d2acaa11975fae1180a8186d2449816fa38f2eabbab93e14` | ±31129 | 0.949981689453125 | -3.4559832611867107 | 1002.249073839976 | none |
| 31130 | `8e7cf36d2a78ee78446b12076361d69284928019ae2bc0072bd63a1fe3c57b3d` | ±31130 | 0.95001220703125 | -3.455749141202171 | 1000.2482261395106 | `level: clipping headroom or near silence` only |

Both helper results report duration 0.12 s, sample rate 48000 Hz, one channel, `pcm_s16le`, 16 bits/sample. The RMS values exceed the 0.001 minimum and centroids lie within the UI 250–4000 Hz fixture band. The boundary is adjacent decoded PCM magnitudes around `.95*32768 = 31129.6`; it is not an exact-equality test at .95.

## Reproducible fixture recipe

`scratch` script `corpus/live/round-42/executor/generate.py`: for each target count `c` in `(31129, 31130)`, form 5760 samples `round(c*cos(2*pi*1000*n/48000))` for `n=0..5759`, cast little-endian signed 16-bit, and write mono/48kHz WAV. Since 1000 Hz has an integer 1200-sample period at 48 kHz, the sampled crest reaches exactly `+c` (and `-c`). This deliberately quantized periodic tone is a numeric fixture, not an audio-quality claim.

## Commands and exits

Commands ran from repository root. `python3 .shokunin/audio/corpus/live/round-42/executor/generate.py` exited **0**, printing frame counts, signed extrema, and hashes shown above.

The project helper was invoked directly (without modifying it), importing `corpus/fixtures/measure_audio.py` and calling `measure("ui", SPECS["ui"], path)` on each scratch WAV:

```sh
python3 -c 'import importlib.util,json,pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; paths=[pathlib.Path(".shokunin/audio/corpus/live/round-42/executor/ui-peak-31129.wav"),pathlib.Path(".shokunin/audio/corpus/live/round-42/executor/ui-peak-31130.wav")]; print(json.dumps([m.measure("ui",spec,x.resolve()) for x in paths],indent=2))'
```

The direct function call exited **0** and returned the metrics table above. It reports measurements but does not exercise the project CLI's mode/receipt/exit behavior.

Raw decoded-count/hash inspection command exited **0**:

```sh
python3 -c 'import wave, pathlib, numpy as np; from hashlib import sha256; d=pathlib.Path(".shokunin/audio/corpus/live/round-42/executor"); [(lambda p: (lambda x: print(p.name, "sha256="+sha256(p.read_bytes()).hexdigest(), "frames="+str(len(x)), "decoded_peak_counts="+str(int(np.max(np.abs(x)))), "rms_pcm_count="+str(float(np.sqrt(np.mean(x.astype(float)**2))))))(np.frombuffer(wave.open(str(p),"rb").readframes(5760), dtype="<i2")))(p) for p in sorted(d.glob("*.wav"))]'
```

No numeric fit failures and no setup errors occurred. No CLI exits are claimed for these probes: the shared helper has no R42 probe mode yet and I did not edit it. No audition or claims about sound quality, clipping perception, production, rights, engine use, publishing, or promotion are made.
