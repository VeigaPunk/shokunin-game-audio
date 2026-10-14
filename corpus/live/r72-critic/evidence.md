# r72-critic — raw evidence log (host: devin, CPython 3.14, sox 14.8.0.1, ffmpeg n9.0.1, libsndfile 1.2.2-4)

All commands run from `~/Projects/shokunin/audio-shokunin`, HEAD `c079aba`
(working tree untracked scratch only). Scratch probe files:
`extsuffix_nomatch.{au,gsm,vox,bin2}` = byte-identical copy of
`corpus/live/round-69/extsuffix_nomatch.snd` (512 B), created in this dir.

## E1 — machine-checked 3-decoder lattice from committed receipts

```
python3 corpus/live/r72-critic/lattice_check.py     # exit 0; full output in lattice.txt
```
Sources: sox committed receipts (latest per mode: r67 dec_act/dec_hcom,
r68 posttable/txw, r69 extsuffix×5), ffmpeg
`corpus/live/runs/20261014T141033155858Z-ffprobe-transport-r71/measurements.json`,
libsndfile `corpus/live/frontier-sndfile/runs/sndfile-matrix.json`.
Acceptance = produced ≥1 decoded frame (sox `exit==0 and samples_read>0`;
ffmpeg `ffmpeg_exit==0`; sndfile `read_frames is not None`).

```
member              | sox          | ffmpeg       | sndfile
                    | f  p  r  q   | f  p  r  q   | f  p  r  q
dec_act             | Y . . .      | Y Y Y Y      | Y Y Y Y
dec_hcom            | Y Y Y Y      | Y Y Y Y      | Y Y Y Y
posttable_nomatch   | . . . .      | . . . .      | . . . .
txw_piperefuse      | Y . Y .      | . . . .      | . . . .
extsuffix_wav       | . . . .      | . . . .      | . . . .
extsuffix_bin       | . . . .      | . . . .      | . . . .
extsuffix_txw       | . . . .      | . . . .      | . . . .
extsuffix_f32       | Y . . Y      | . . . .      | . . . .
extsuffix_snd       | Y . . Y      | . . . .      | Y . . Y
```
Member-level accept classes (sox, ffmpeg, sndfile):
`(T,T,T)`: dec_act, dec_hcom · `(T,F,F)`: txw_piperefuse, extsuffix_f32 ·
`(T,F,T)`: extsuffix_snd · `(F,F,F)`: posttable, extsuffix_{wav,bin,txw}.
**No `(F,F,T)` (sndfile-only) and no `(F,T,F)` (ffmpeg-only) class exists on
the tracked 9.**

## E2 — sox accepts the `.snd` member on the same arms as libsndfile

```
sox corpus/live/round-69/extsuffix_nomatch.snd -n stat
→ Samples read: 504 ; exit 0
```
Committed receipt `corpus/live/runs/20261014T140641162793Z-transport-extsuffix-snd-r69`
(measurements key `transport_extsuffix_snd_r69_probe`):
`file`/`fifo_path` → det `sndr`, exit 0, samples_read 504;
`stdin_pipe`/`redirected_fd` → exit 2 `can't determine type`.
libsndfile matrix: `file`/`fifo_path` → RAW|U-LAW, read 500;
`stdin_pipe`/`redirected_fd` → `Format not recognised`.
→ identical named/anonymous partition, two mechanisms.

## E3 — the real sndfile-only exemplar: `.au`-named identical bytes

```
sox   extsuffix_nomatch.au -n stat   → exit 2, "can't find Sun/NeXT/DEC identifier"
sndfile (sf_open)                    → RAW|U-LAW, frames=512, drained=500
ffprobe -show_entries format=format_name → exit 1, Invalid data
ffmpeg -i ... -f null -              → exit 183
```
`.vox`-named: sox exit 0 / 1024 samples (WARN adpcms state errors);
sndfile RAW|VOX_ADPCM 1024; ffmpeg exit 183 → joint class, untracked.

## E4 — ffmpeg has a named-only accept outside the tracked set (`.gsm`)

```
ffprobe extsuffix_nomatch.gsm  → exit 0, format_name "gsm", duration 0.320000
ffmpeg  -i extsuffix_nomatch.gsm -f null - → exit 0
        "Input #0, gsm ... Stream #0:0: Audio: gsm, 8000 Hz, mono, s16, 13 kb/s"
ffprobe extsuffix_nomatch.bin2 (same bytes)  → exit 1 "Invalid data found"
cat extsuffix_nomatch.snd | ffprobe pipe:    → exit 1 "Invalid data found"
ffprobe /tmp/.../m.gsm (fifo, name kept)     → exit 0, format_name "gsm"
sox   extsuffix_nomatch.gsm -n stat          → exit 0, Samples read: 0
sndfile                                      → RAW|GSM610, frames=2560, drained=2560
```
Same bytes, name decides ffmpeg acceptance → ffmpeg name axis exists;
anonymous (pipe) rejects. This falsifies "ffmpeg ignores the name" as a
general statement (it holds only on the tracked names, which have no
accepting demuxer/extension score).

## E5 — `sndfile-info` 'frames' line is not a decode verdict

```
sndfile-info extsuffix_nomatch.snd   → "Frames      : 512"  (exit 0)
python3 corpus/live/r72-critic/drain_check.py corpus/live/round-69/extsuffix_nomatch.snd \
        corpus/live/round-66/pair_dec_act.wav
→ extsuffix_nomatch.snd: info.frames=512 single_call=500 drained_total=500
→ pair_dec_act.wav:      info.frames=278 single_call=278 drained_total=278
sndfile-info on fifo named m.snd     → "Frames      : unknown" (exit 0)
frontier matrix fifo arm             → frames=9223372036854775807, read_frames=500
```
Size sweep (same bytes truncated/padded, sf_open + full drain):
256→frames 256/drained 244 · 512→512/500 · 1024→1024/1012 · 2048→1024/1012
(frames is an estimate, not a read).

## E6 — exit-code / name / boundary traps

```
sndfile-info corpus/live/round-68/posttable_nomatch.wav  → exit 0 (reject text only)
cat extsuffix_nomatch.snd | sndfile-info /dev/stdin      → exit 0, "Format not recognised."
sox /tmp/.../m.fifo (fifo name without member ext)       → exit 2, "no handler for file extension `fifo'"
python3 -c 'ctypes sf_version_string'                    → libsndfile-1.2.2
```

## E7 — r71 receipt values used for the superset question

`corpus/live/runs/20261014T141033155858Z-ffprobe-transport-r71/measurements.json`
(byte-stable post-`77768fa`, mode wired):
dec_act → (`wav`,0,0) ×4 · dec_hcom → (`hcom`,0,0) ×4 ·
extsuffix_snd / extsuffix_f32 / txw_piperefuse → (`None`,1,183) ×4.

## E8 — frontier table number to fix

`reports/frontier/fa-sndfile.md:65` says `.f32` "decode 75, exit 0".
Committed receipt `…T140639114072Z-transport-extsuffix-f32-r69` says
samples_read **128** (file and fifo_path); live re-run `Samples read: 128`,
exit 0. "75" traces to the r69-scout zero-bytes pre-measurement
(`reports/round-69/r69-scout.md:99`), not the shipped member.

## E9 — state

`git rev-parse HEAD` → `c079abafdcabe5f6afc45d1a8cea6a0af8ee4847`;
untracked `corpus/live/r71-critic/` scratch exists (misnamed.bin/.f32,
*_asbin.bin, test_astxw.txw, timestamps 11:11–11:19) with **no**
`reports/round-71/r71-critic.md` — a dead ffmpeg name-axis probe.
