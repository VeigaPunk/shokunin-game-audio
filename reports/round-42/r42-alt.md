# R42 alternate independent peak bracket (31129/31130)

## Scope and result

Independent numerical fixture calibration only. I created two original UI-shaped scratch WAVs under `corpus/live/round-42/alt/`; no shared source, LOG, SCORECARD, canonical fixture, or other report was changed. The source-defined `measure()` helper reports an adjacent decoded PCM16 peak bracket: 31129 counts passes with no failures; 31130 counts fails only `level: clipping headroom or near silence`. Both satisfy the declared duration, 48 kHz mono PCM16, RMS, and UI centroid checks. No failed numerical fit occurred.

The existing comparator is strict `peak < .95` (implemented as failure when `peak >= .95`). `31129/32768 = 0.949981689453125`; `31130/32768 = 0.95001220703125`. Since `.95 * 32768 = 31129.6`, this brackets adjacent integer decoded magnitudes, not exact equality at .95.

## Recipe and hashes

For each file, `N=5760`, `rate=48000`, `t=np.arange(N)/rate`, and `base=sin(2*pi*(700*t + 800*t*t))*exp(-30*t)`. I selected the smallest bisection scale whose positive rounded PCM maximum reaches the requested count (70 iterations over [0,1.2]); quantization is `np.rint(np.clip(scale*base,-1,1)*32767).astype('<i2')`. Each waveform was written as mono, 2-byte PCM, 48 kHz WAV. Scales: 31129 `0.9602174671271009`; 31130 `0.9602483140187636`.

| Scratch file | SHA-256 | decoded min/max counts | peak FS | RMS dBFS | centroid Hz | duration / format | failures |
|---|---|---:|---:|---:|---:|---|---|
| `peak-31129.wav` | `d56bb13fbc1894a11e2807c18d52c25d7877fc9d194f29747b90e5659d509130` | -30459 / 31129 | 0.949981689453125 | -11.939951937178082 | 966.6827446669814 | .12 s, 48k mono PCM16 | none |
| `peak-31130.wav` | `eb2e49dd60fd83484958dcb3ee85ea611fe88fbaf70323cfc427b8a21f106119` | -30460 / 31130 | 0.95001220703125 | -11.939672328927625 | 966.6760815177989 | .12 s, 48k mono PCM16 | sole peak/headroom failure |

Metrics were produced by the project helper; the exact command and exit were:

```sh
python3 -c "import importlib.util,json,hashlib; from pathlib import Path; p=Path('/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-42/alt'); spec=importlib.util.spec_from_file_location('m','.shokunin/audio/corpus/fixtures/measure_audio.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); [print(x.name,hashlib.sha256(x.read_bytes()).hexdigest(),json.dumps(m.measure(x.stem,m.SPECS['ui'],x),sort_keys=True)) for x in sorted(p.glob('*.wav'))]"
```

Exit **0**. Helper output gave exact decoded float peaks as above, and WAV PCM extrema are recorded in the table. Both RMS values are far above `.001` FS; centroids are within 250–4000 Hz. I did not run either `measure_audio.py` opt-in CLI mode: no R42 peak mode exists in the shared runner yet, and changing shared source is outside this leaf scope. Thus this is an independent helper-metric result, not a runner receipt or integration/replay claim. No setup error or numeric failed fit was observed. (A harness-side attempt to await an already completed bash result raised a Python `TypeError`; the command was rerun correctly and exited 0, so that orchestration mistake did not affect fixture metrics.)

This pair does not establish exact equality at .95, audible clipping absence, headroom quality, production suitability, rights, engine behavior, or publishing suitability. No audition or sound-quality inference was made.
