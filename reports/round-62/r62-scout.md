# r62 — scout — audio lane — depth

Move: resolve the SoX decode-length UNKNOWN recorded at r61
(`pair_valid_17.wav` decodes to 3,839 f32 samples while `pair_valid_16.wav`
yields 5,760 despite byte-identical PCM payloads).

Seat: scout (recon only). Writes this report plus scratch under
`corpus/live/r62-scout/`. No source edits, no commits.

## Verdict

**UNKNOWN resolved.** The 3,839 = `floor(8192/3) + floor(3328/3) = 2730 + 1109`.

- SoX never decodes the file with its native `wav` handler. Both R61 pair
  files are misdetected as `act` (SoX_ng `auto_detect_format`,
  `src/formats.c`: `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` — checked **before**
  `wav`, comment: "Must come before wav because it looks like a PCM WAV
  file"). Both pair payloads carry byte `0x84` at file offset 256 (data-chunk
  byte 188). `act` open fails; the handler fallback chain reaches `ffmpeg`,
  which claims the file (`sox --i` reports `(ffmpeg)`).
- ffmpeg's wav demuxer sees `wValidBitsPerSample=17 > wBitsPerSample=16` and
  reclassifies the stream as `pcm_s24le` (3-byte samples). It packetizes the
  11,520-byte data chunk in 8192-byte granules: packets `8192 + 3328`. The
  `pcm_s24le` decoder emits only complete 3-byte samples **per packet** and
  drops each tail (`Invalid PCM packet, data has size 2 but at least a size
  of 3 was expected`; same for size 1). 2730 + 1109 = **3,839**.
- `pair_valid_16.wav` takes the identical `act`→`ffmpeg` route (same payload
  bytes, `0x84` at 256) but stays `pcm_s16le` (2-byte): `8192/2 + 3328/2 =
  4096 + 1664 = 5,760` — no loss because the packet sizes divide evenly.

Deeper finding (depth axis): the 17-valid-bits file is **decodable only by
accident**. With any other byte at offset 256 the file detects as `wav` and
the native handler hard-fails
(`number of valid bits exceeds the number of bits per sample`), which inside
`measure()` would raise `CalledProcessError` — no measurement, no receipt.
The R61 receipt exists because payload byte 188 happens to be `0x84`.

## Source map

Measurer: `corpus/fixtures/measure_audio.py` (643 lines)

- `SPECS` dict `:15`; `"ui": (.12, 250, 4000, False)` at `:16`.
- `command()` `:36-38` — `subprocess.run(args, check=True, capture_output=True)`.
- `format_failures()` `:40-46` — requires 48 kHz mono and `pcm_s16le`/16 bits.
- `measure()` `:49-97`:
  - ffprobe `:51-52`: `ffprobe -v error -show_entries
    stream=sample_rate,channels,codec_name,bits_per_sample:format=duration
    -of json <path>`
  - SoX `:55`: `sox <path> -t f32 -e floating-point -` → `np.frombuffer(...,
    "<f4")` `:56`; **no input `-t`, so input format is auto-detected** — this
    is the load-bearing detail for the anomaly.
  - duration comes from ffprobe `format.duration` `:57`, not the f32 count.
  - ffmpeg loudness `:67-68`: `ffmpeg -hide_banner -nostats -i <path>
    -filter_complex ebur128=peak=true -f null -`
  - failure rules `:76-87` (±1 ms duration, headroom/silence, centroid band,
    loop-seam deltas).
- R61 CLI flags `--probe-ui-extensible-valid-{17,16}-r61` declared `:244-245`;
  one-probe mutex at `:247`.
- Builder dispatch `command(sys.executable, .../build_artifacts.py, ...)`
  `:259`; R61 flag forwarded at `:333-334`.
- R61 path selection `:413-417`: `ROOT/"live"/"round-61"/
  f"pair_valid_{valid}.wav"` then `measure(name, SPECS["ui"], path)` `:417`.
- Receipt `:632-638`: `live/runs/<stamp><-ui-extensible-valid-*-r61>/
  measurements.json`; `return bool(failed)` `:639` → `sys.exit(main())`.
- `measure()` catches nothing; only `invalid_probes()` catches
  `CalledProcessError` (`:138-143`). A SoX hard-fail inside `measure()`
  propagates → traceback exit, **receiptless**.

Builder: `corpus/fixtures/build_artifacts.py` (846 lines)

- `RATE = 48000` (top); `build_ui_extensible_valid17_probe()` `:192-201`:
  - writes `corpus/live/round-61/`; payload `round(8191*(.28*sin(2π·1050·i/
    RATE) + .10*sin(2π·1750·i/RATE)))`, 5,760 int16 samples = 11,520 bytes;
  - fmt40 `0xfffe`, ch 1, byteRate 96000, blockAlign 2, bits 16, cbSize 22,
    `wValidBitsPerSample` = `{17,16}` (the pair's only byte difference,
    file offset 38), channel mask `0x4`, PCM subtype GUID
    `0100000000001000800000aa00389b71`; then `data` chunk.
- Same builder shape serves r57-r60 pairs (`:204-255`), which live under
  `corpus/live/round-{57..60}/`.

Fixtures: `corpus/live/round-61/pair_valid_{17,16}.wav`
(sha256 `15cadf24…2eb63fe4` / `2c5e244f…59591d00`); `valid17.f32` /
`valid16.f32` are the recorded decodes. Scratch controls:
`corpus/live/r62-scout/` (`make_controls.py`, `ctrl_v17_data*.wav`,
`orig_renamed.wav`, `orig_byte256_00.wav`, `ctrl_byte256_84.wav`).

R61 verifier ledger (`reports/round-61/r61-verifier.md`): 82 serial commands,
43 exit-0 + 39 expected exit-1; commands #2/#3 are the two new R61 probes
(`-valid-17-r61` exit 1, `-valid-16-r61` exit 0), each with a fresh
`live/runs/<stamp><suffix>` receipt; the other 80 replayed the r60 ledger.

## Decode-routing evidence

Toolchain: `sox 14.8.0.1-1` (SoX_ng v14.8.0.1), `ffprobe`/`ffmpeg` n9.0.1,
GCC 16. Upstream reference read-only: sox_ng `src/formats.c` on codeberg
(main; the `act` CHECK and `AUTO_DETECT_SIZE 257 /* for act */` under
`USING_FFMPEG`).

| file | byte[256] | `sox -V6` detects | opens as | decoded bytes / samples |
|---|---|---|---|---|
| `round-61/pair_valid_17.wav` | `0x84` | `act` | `(ffmpeg)` | 15,356 B = 3,839 |
| `round-61/pair_valid_16.wav` | `0x84` | `act` | `(ffmpeg)` | 23,040 B = 5,760 |
| `round-60/pair_valid_16.wav` | `0x78` | `wav` (`EXTENSIBLE`) | native `wav` | 5,760 |
| `round-60/pair_valid_0.wav`  | `0x78` | `wav` | native `wav` | 5,760 |
| `artifacts/ui.wav` | `0x01` | `wav` | native `wav` | 5,760 |
| `r62-scout/ctrl_v17_data11520.wav` (identical header, ramp payload) | `0xbc` | `wav` | native `wav` | **hard fail** |
| `r62-scout/orig_byte256_00.wav` (v17, byte 256 → `0x00`) | `0x00` | `wav` | native `wav` | **hard fail** |
| `r62-scout/ctrl_byte256_84.wav` (ramp v17, byte 256 → `0x84`) | `0x84` | `act` | `(ffmpeg)` | 15,356 B = 3,839 |

Both directions flip routing with one payload byte — confirmed causal, not
correlation. Verbose lines for the pair path:

```
sox INFO formats: detected file format type `act'
sox INFO au: found big-endian `.snd' identifier
Input File     : 'round-61/pair_valid_17.wav' (ffmpeg)
```

`act` fails open, the fallback chain logs an `au` sniff line (no `.snd`/
`dns.`/`\0ds.`/`.sd\0` magic exists in the file — internal au heuristic,
non-load-bearing), and `ffmpeg` wins.

## Packet-level mechanism (forced `-t ffmpeg`, discriminating controls)

`ffprobe -show_packets` on the original: packets `8192` + `3328` bytes,
durations 2730 + 1109 samples. On `ctrl_v17_data24576.wav`: three `8192`
packets, duration 2730 each.

| data bytes | packet split | per-packet floor(bytes/3) | predicted | observed |
|---|---|---|---|---|
| 8,190  | 8190 | 2730 | 2730 | **2,730** (10,920 B) |
| 8,193  | 8192+1 | 2730+0 | 2730 | **2,730** — whole-file floor would be 2731 |
| 11,520 | 8192+3328 | 2730+1109 | 3839 | **3,839** (15,356 B) |
| 12,289 | 8192+4097 | 2730+1365 | 4095 | **4,095** — whole-file floor would be 4096 |
| 16,383 | 8192+8191 | 2730+2730 | 5460 | **5,460** — whole-file floor would be 5461 |
| 24,576 | 8192×3 | 2730×3 | 8190 | **8,190** — whole-file floor would be 8192 |

Refutes whole-file `floor(total/3)` and single-EOF-frame loss: loss accrues
**per 8192-byte packet** (2 B per full packet, 1 B on the 3328 tail for
valid17). ffmpeg stderr confirms:
`Invalid PCM packet, data has size 2 but at least a size of 3 was expected`
and `... size 1 ...` followed by `Decoding error: Invalid data found when
processing input`. Direct `ffmpeg -i` decode also emits 15,356 B — SoX adds
nothing; the loss is inside ffmpeg's `pcm_s24le` packet decode.

ffprobe stream on valid17: `codec_name pcm_s24le`, `sample_fmt s32`,
`bits_per_sample 24`, `bits_per_raw_sample "24"`, `format.duration
"0.080000"` (= 3839/48000+0.000 0208…, matching the R61 receipt). valid16:
`pcm_s16le`, 16, `0.120000`.

## SoX knob inventory (input side, relevant to decode length)

- Default: auto-detect (`auto_detect_format`) — **content-dependent**, the
  anomaly's entry point; no filetype flag is passed by `measure()` (`:55`).
- `-t wav` (or `wavpcm`): forces native WAV → hard FAIL on `wValidBits >
  wBitsPerSample` (`sox -t wav round-61/pair_valid_17.wav …` →
  `can't open input file … number of valid bits exceeds the number of bits
  per sample`), 0 output bytes.
- `-t ffmpeg`: forces libavformat → reproduces 15,356 B exactly; deterministic.
- `sox --i`: reports handler suffix `(ffmpeg)`, 1 ch, 48,000 Hz, "Precision:
  16-bit" for both pair members (cosmetic — the codec is s24le for v17).
- `-V4`/`-V6`: reveals `detected file format type` and handler DBUG lines.
- Input `-r`/`-c` (rate/channels) are accepted by `sox` for headerless
  formats only; irrelevant here (RIFF header supplies them). Not used by the
  runner.
- Buffer knobs (`--buffer`, `--input-buffer` global opts): output-pipeline
  effect only; do not change the ffmpeg demuxer's 8192-byte packet granule.
- `sox formats` list includes `wav`, `wavpcm`, `ffmpeg`, `act`, `au`, etc.

## Facts vs inference vs remaining unknowns

Facts (all reproduced above with commands): misdetection via byte `0x84` at
256; `(ffmpeg)` handler; `pcm_s24le` reclassification; 8192-byte
packetization; per-packet tail discard; 3,839 arithmetic; native-handler
hard fail; receiptless-crash asymmetry (`command(check=True)` + uncaught in
`measure()`).

Inference (strong, control-backed): same routing explains r61-valid16's
*lossless* 5,760 (even 2-byte division) and predicts r60/r55-era
valid-pairs decoded via **native** wav (their payloads have `0x78`/`0x01`
at 256) — consistent with r60 verifier counts.

Remaining unknowns (bounded, non-blocking): the exact startread-failure/
fallback ordering inside sox_ng between `act`→`au`→`ffmpeg` (winner is
proven; path sequence inferred from INFO lines); the au "`.snd` identifier"
trigger byte (none of au's four documented magics occur in the file); why a
detected-`act` failure falls through to other handlers while a detected-`wav`
parse failure aborts (asymmetric retry semantics — observed, not sourced);
sox_ng `act.c` source on codeberg main returned 404 (handler may live in
another file).

## Implications (recon notes, not change proposals)

- `sox <path> -t f32 -e floating-point -` in `measure()` is
  handler-ambiguous: identical flags yield native rejection **or**
  ffmpeg-backed partial decode depending on one payload byte (offset 256).
  The R61 "decodes but short" observation is a coincidence of the chosen
  sine pair; it is not a property of the malformed header.
- If fixture semantics should be deterministic, the only stable levers are
  explicit input types (`-t wav` / `-t ffmpeg`) — both behave
  deterministically; default detection does not. Whether/how to pin that is
  the author seat's call.
- The 17-bit fixture cannot serve as a "malformed but decodable" positive
  control under the native handler at all — its only decode path rides a
  content-sniffed `act` false positive.
