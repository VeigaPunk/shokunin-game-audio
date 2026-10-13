# Round 43 alternate independent RMS-bracket report

## Result and scope

Independent fixture pair produced under `.shokunin/audio/corpus/live/round-43/alt/`. The 46-count probe fails the existing level predicate with the sole reported `level: clipping headroom or near silence` failure; decoded peak is far below `.95`, so the measured RMS below `.001` identifies the near-silence branch. The 47-count probe passes with no failures; its decoded peak is also far below `.95`, while RMS is above `.001`. This is a fixture-local adjacent *crest count* control, not adjacent attainable RMS values, exact equality at `.001`, perceptual silence, or a claim about audio quality. No threshold or source was changed. No audition or production, rights, engine, publication, or promotion inference is made.

## Exact deterministic recipe and hashes

For each `k` in `{46,47}`, create 5,760 signed little-endian PCM16 mono samples at 48,000 Hz:

`pcm[n] = round(k * cos(2*pi*1000*n/48000))`, `n=0..5759`.

Write as WAV (one channel, 2-byte samples, 48,000 Hz). The 1000 Hz cosine is periodic over 0.12 seconds. Source files are original and distinct. SHA-256 and measured decoded metrics:

| Crest k | SHA-256 | Frames / duration | Format | Decoded peak FS | Decoded RMS FS | RMS dBFS | Decoded centroid Hz | Result |
|---:|---|---|---|---:|---:|---:|---:|---|
| 46 | `869d1e5ada618a3c9daaa7be3100c9a01dc1342df63d732355a23a306130adfc` | 5760 / 0.12 s | 48 kHz mono PCM16 | 0.00140380859375 | 0.0009918604133909925 | -60.07098885448798 | 1333.1671762128612 | sole level failure |
| 47 | `4c8c67a08558f14ad0642cac99563056407eeeecdc6b05e974f7b24cf74804b3` | 5760 / 0.12 s | 48 kHz mono PCM16 | 0.001434326171875 | 0.0010130695326051164 | -59.88721491134572 | 2221.1801421740442 | no failures |

The centroid values are within the UI 250–4000 Hz band. Both decoded peaks are `< .95`; RMS is respectively below and above `.001`. These metrics separate the RMS branch from the peak branch in the unchanged `peak >= .95 or rms < .001` test.

## Commands and errors

The project SoX f32 decoder was first checked for both WAVs; command was `sox .shokunin/audio/corpus/live/round-43/alt/ui-crest-46.wav -t f32 -e floating-point -` and the corresponding command with `ui-crest-47.wav`. Both exited 0 and emitted 23,040 bytes of decoded samples.

I invoked the project's `measure_audio.measure` with the UI spec against each file (using the exact command below); exit 0. It reported for 46: `peak_full_scale=0.00140380859375`, `rms_dbfs=-60.07098885448798`, `spectral_centroid_hz=1333.1671762128612`, `failures=['level: clipping headroom or near silence']`; and for 47: `peak_full_scale=0.001434326171875`, `rms_dbfs=-59.88721491134572`, `spectral_centroid_hz=2221.1801421740442`, `failures=[]`.

```sh
python3 -c 'import importlib.util, pathlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py").resolve(); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); spec=m.SPECS["ui"]; print(m.measure("46",spec,pathlib.Path(".shokunin/audio/corpus/live/round-43/alt/ui-crest-46.wav").resolve())); print(m.measure("47",spec,pathlib.Path(".shokunin/audio/corpus/live/round-43/alt/ui-crest-47.wav").resolve())'
```

There was one setup/path error before the successful invocation: the same measurement import passed relative WAV paths, and `measure()` raised `ValueError` because the relative paths did not lie under its resolved project root. That command exited **1**. This was a harness invocation/path setup error, not a numeric fit or fixture failure. Re-running with resolved absolute paths succeeded as shown above. The 46 result is the intended numeric threshold failure; the 47 result is a numeric pass. No other runner modes were invoked.

## Boundaries

This report covers only the two independently generated probes and their project decoder/measurement. It does not re-verify canonical fixtures, prior mode replay, old-17 hashes, or any broader round preservation claims. No shared source, LOG, SCORECARD, canonical artifact, or other report was edited; no commit or push was made.
