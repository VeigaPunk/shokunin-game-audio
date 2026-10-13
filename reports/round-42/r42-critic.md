# R42 critic — peak isolation and decoded-sample check

## Scope and verdict

I independently checked the four existing round-42 scratch WAVs against the current `measure()` checks. The executor pair supports a narrow numeric calibration result: at 48 kHz mono PCM16 and 5760 decoded frames, 31129 counts passes while 31130 counts fails solely the combined level condition. RMS and centroid remain comfortably within their checks in both members. This is not an exact-equality test at .95, and it says nothing about sound quality or suitability.

## Encoded/decoded evidence

All four files probe as `pcm_s16le`, 48000 Hz, mono, 16-bit, duration 0.120000 s; SoX decoded 5760 samples from each. SHA-256 and decoded absolute peak counts:

| Pair | File | SHA-256 | Decoded abs peak (count / 32768) | RMS dBFS | Centroid Hz | failures |
|---|---|---|---:|---:|---:|---|
| executor | `corpus/live/round-42/executor/ui-peak-31129.wav` | `7e6c11325d27c1e0d2acaa11975fae1180a8186d2449816fa38f2eabbab93e14` | 31129 / 32768 = .949981689453125 | -3.4559832612 | 1002.2491 | none |
| executor | `corpus/live/round-42/executor/ui-peak-31130.wav` | `8e7cf36d2a78ee78446b12076361d69284928019ae2bc0072bd63a1fe3c57b3d` | 31130 / 32768 = .95001220703125 | -3.4557491412 | 1000.2482 | `level: clipping headroom or near silence` only |
| alt | `corpus/live/round-42/alt/peak-31129.wav` | `d56bb13fbc1894a11e2807c18d52c25d7877fc9d194f29747b90e5659d509130` | 31129 / 32768 = .949981689453125 | -11.9399519372 | 966.6827 | none |
| alt | `corpus/live/round-42/alt/peak-31130.wav` | `eb2e49dd60fd83484958dcb3ee85ea611fe88fbaf70323cfc427b8a21f106119` | 31130 / 32768 = .95001220703125 | -11.9396723289 | 966.6761 | `level: clipping headroom or near silence` only |

Both independent pairs preserve same rate, channel count, codec, bit depth, frame count and duration. Each pair's only observed measurement-failure change is the peak-count step and corresponding `level` result. RMS is far above .001 and centroid falls in 250–4000 Hz; no format/duration/spectrum failures. This falsifies a confound from those measured gates, not every possible confound or interpretation of the gate.

The checker computes peak after SoX decodes the encoded WAV to float32, then stores it as float64; it does not compare the original generator's in-memory float waveform. Here the decoded sample counts agree exactly with the PCM16 files' intended peaks (executor generator's selected positive and negative extrema are ±31129/±31130; independent alt files also decode to those absolute peaks). The one-count spacing is 1/32768 = 0.000030517578125 full scale. It does not establish bit-for-bit equality of all encoded and decoded representations, nor an exact `.95` input. Since `.95 * 32768 = 31129.6`, no PCM16 sample equals .95: 31129 is below and 31130 above. The test brackets the strict `peak >= .95` comparison on adjacent PCM16 peak magnitudes; it must not be described as testing exact equality at .95.

## Commands, exits, and setup distinction

Commands run from repo root:

- `cd .shokunin/audio && for f in corpus/live/round-42/{executor,alt}/*.wav; do echo "FILE=$f"; ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample,duration:format=duration -of default=noprint_wrappers=1 "$f"; sox "$f" -n stat 2>&1 | grep -E 'Samples read|Length \(seconds\)|Maximum amplitude|Minimum amplitude|RMS amplitude'; sha256sum "$f"; done` — **exit 0**. It showed four 5760-sample files, duration 0.120000, PCM S16LE / 48 kHz / mono.
- Initial helper attempt — **exit 1, setup error, not numeric failure**: from `.shokunin/audio`, I passed `corpus/live/...` to `measure()`, which resolves fixture paths relative to `corpus/`; `path.relative_to(ROOT)` raised `ValueError` because that path was not under `corpus/`. No gate result was produced by this failed attempt.
- Corrected numeric helper — **exit 0**. Exact command:

```sh
cd .shokunin/audio && python3 - <<'PY'
import importlib.util, pathlib, hashlib, struct, subprocess, sys
p=pathlib.Path('corpus/fixtures/measure_audio.py')
spec=importlib.util.spec_from_file_location('measure_audio',p); m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m)
for name, rel in [('executor31129','live/round-42/executor/ui-peak-31129.wav'),('executor31130','live/round-42/executor/ui-peak-31130.wav'),('alt31129','live/round-42/alt/peak-31129.wav'),('alt31130','live/round-42/alt/peak-31130.wav')]:
 path=m.ROOT/rel
 r=m.measure(name,(.12,250,4000,False),path); print(name, r)
 raw=subprocess.run(['sox',str(path),'-t','s16','-e','signed-integer','-'],check=True,capture_output=True).stdout
 x=struct.unpack('<%dh'%(len(raw)//2),raw)
 print('decoded_count',len(x),'peak_counts',max(abs(v) for v in x),'first_last',x[0],x[-1], 'sha256',hashlib.sha256(path.read_bytes()).hexdigest())
PY
```

It printed the table measurements above and decoded count `5760` for each WAV. Exit 0 is helper completion, not the peak-gate outcome: the 31130 measurement records contain expected level failures.

No setup error is counted as a failed numeric fit. The two 31130 cases are expected numeric gate failures, not setup errors. No audition or subjective, production, rights, engine, publishing, or promotion inference was made.
