# Round 25 alternate format controls (r25-alt)

## Scope and result

Built two independent, analytic 440 Hz, four-second, PCM16 WAV controls under `.shokunin/audio/corpus/live/round-25/alt/`. They isolate the two format fields that were co-failed by the old 44.1 kHz stereo probe: `stereo48.wav` is 48 kHz stereo (channels only wrong), and `mono441.wav` is 44.1 kHz mono (rate only wrong). Both are mono-equivalent sine content duplicated across channels where stereo; neither changes codec/bit depth. Both meet numerical acoustic checks when decoded as mono: duration 4.0 s, peak about 0.100 FS, RMS about 0.0707 FS, centroid about 459/476 Hz within the stem 100–2000 Hz band, and endpoint delta <.03 FS. Therefore the designed rejection reason is isolated to channel count or sample rate, not those acoustic checks. This does not constitute integrated-runner verification, and no threshold or shared source was changed.

SHA-256: `stereo48.wav` `c85c0734b87f810836a4e4605a61665ffd3144317eff362fe39a422c603f1e2d`; `mono441.wav` `2432cafc1e43dc210055ccc857da04113565663ad6e092ae7f7a220dc29c8055`.

## Exact commands and exits

Files were generated with this Python REPL code (exit status not applicable; no shell command): using `wave` to write signed little-endian 16-bit samples, `round(0.1*32767*sin(2*pi*440*i/rate))`, 4*rate frames, duplicate each sample for each channel; parameters `(stereo48,48000,2)` and `(mono441,44100,1)`.

`ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/alt/stereo48.wav` — exit **0**; reports PCM16, 48000 Hz, 2 channels, 4.000000 s.

`ffprobe -v error -show_entries stream=sample_rate,channels,codec_name,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-25/alt/mono441.wav` — exit **0**; reports PCM16, 44100 Hz, 1 channel, 4.000000 s.

`sox .shokunin/audio/corpus/live/round-25/alt/stereo48.wav -t f32 -e floating-point - | wc -c` — exit **0**, 1536000 bytes (48000*4*2 decoded float32 samples).

`sox .shokunin/audio/corpus/live/round-25/alt/mono441.wav -t f32 -e floating-point - | wc -c` — exit **0**, 705600 bytes (44100*4 decoded float32 samples).

A single shell inspection ran `python3 -c` with ffprobe JSON parsing and these assertions: append `sample_rate` iff rate != 48000; append `channels` iff channels != 1; print metadata and failure fields for each file. Exact command:

```sh
python3 -c "import json,subprocess; from pathlib import Path;\nfor p in sorted(Path('.shokunin/audio/corpus/live/round-25/alt').glob('*.wav')):\n q=json.loads(subprocess.run(['ffprobe','-v','error','-show_entries','stream=sample_rate,channels,codec_name,bits_per_sample:format=duration','-of','json',str(p)],check=True,capture_output=True,text=True).stdout); s=q['streams'][0]; failures=[];\n if int(s['sample_rate']) != 48000: failures.append('sample_rate')\n if int(s['channels']) != 1: failures.append('channels')\n print(p.name, s['sample_rate'],s['channels'],s['codec_name'],s['bits_per_sample'],q['format']['duration'],'isolated_failures='+','.join(failures)"
```

Exit **0**, output: `mono441.wav 44100 1 pcm_s16le 16 4.000000 isolated_failures=sample_rate`; `stereo48.wav 48000 2 pcm_s16le 16 4.000000 isolated_failures=channels`.

Decoded mono numeric summaries were computed with Python `wave`/NumPy (not a shell command): `mono441.wav`: 176400 frames, centroid 475.8086 Hz, RMS 0.0707087, peak 0.1000061, endpoint delta 0.0062561; `stereo48.wav`: 192000 frames, centroid 458.8031 Hz, RMS 0.0707096, peak 0.1000061, endpoint delta 0.0057678. They satisfy the referenced stem numeric bounds; rate/channel rejection is intended. These are scratch-control observations, not execution through the integrated checker.

## Limits

No shared builder, runner, canonical fixture, log, scorecard, or other report was edited; no commit/push. These controls show matched metadata-level predicate isolation for this analytic PCM16 content only. They do not establish broad codec/container handling, sound quality, engine behavior, rights, or publishing.
