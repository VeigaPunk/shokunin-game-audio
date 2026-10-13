# Round 62 — boundary (revenger): mechanism of SoX's 3,839-sample decode of `pair_valid_17.wav`

Seat: **revenger** — reconstruct host behavior from executable evidence. Scope: explain the
r61 UNKNOWN (SoX decodes `pair_valid_17.wav` to **3,839** f32 samples vs 5,760 for
`pair_valid_16.wav`; ffprobe `pcm_s24le`/`0.080 s` = 3,840 nominal). Host: Arch Linux,
`sox` = SoX_ng 14.8.0.1, `ffmpeg`/`ffprobe` = n9.0.1. All work in
`.shokunin/audio/corpus/live/r62-boundary/`; no repo content changed.

## Verdict: mechanism established, every number reproduced

The 3,839 is **not** a SoX wav-reader behavior at all. It is an emergent result of a
five-step chain, each step verified against n9.0.1 source and by discriminating controls:

```
.wav (byte 256 == 0x84) ──SoX autodetect──> "act" -> ffmpeg handler -> pipe
   `ffmpeg -i <file> -f au -`  ──libavformat──> riffdec.c parse_waveformatex:
        bits_per_coded_sample := wValidBitsPerSample (=17)
        codec_tag 1 (PCM GUID) -> ff_wav_codec_get_id(1,17)
             -> ff_get_pcm_codec_id(17,0,0,~1): (17+7)>>3=3 -> pcm_s24le
   ──wavdec.c──> packets of max_size 8192 B (aligned to nBlockAlign=2):
        8192 + 3328
   ──pcmdec.c──> per-packet floor to 3-byte frames:
        floor(8192/3)=2730  +  floor(3328/3)=1109   =   3839 frames
        trailing 2 B + 1 B re-fed -> "Invalid PCM packet" -> dropped
   ──au muxer──> .snd s16be stream, 7678 B = 3839 samples -> SoX au reader
```

The one-frame gap vs ffprobe's 3,840 is a metadata/decode divergence: stream duration is
`data_size<<3 / (ch x codec_bits) = 92160/24 = 3840` (exact division, nominal), while the
decoder emits per-packet floors that lose 3 payload bytes (one fake 24-bit frame).

## Evidence chain (commands -> observed output)

### 1. Handler selection — the `(ffmpeg)` path is a payload coincidence

- `sox --i corpus/live/round-61/pair_valid_17.wav` -> `Input File : 'pair_valid_17.wav' (ffmpeg)`;
  same for `pair_valid_16.wav`. For r57 `pair_valid_16.wav` (byte 256 = 0x1a) and r60
  `pair_valid_16.wav`/`pair_valid_0.wav` (0x78) the tag is **absent** -> native `wav` handler.
- `od -A d -t x1 -j 256 -N 1` on both r61 files -> `84`. SoX_ng `formats.c` autodetect table:
  `CHECK(act, "RIFF"@0, 0x84@256)` sits **before** `CHECK(wav, "RIFF"@0, "WAVE"@8)` with the
  comment "Must come before wav because it looks like a PCM WAV file" (`formats.c:93-95`).
  `act` is a name of the ffmpeg pseudo-handler (`ffmpeg.c` `names[]`).
- **Discriminating control**: `g_byte256_fixed.wav` = pair_valid_17 with only byte 256
  0x84->0x00 -> `sox` **fails**:
  `sox FAIL formats: can't open input file '...': number of valid bits exceeds the number of
  bits per sample` (exit 1) — the native wav reader's own guard. `g_byte256_fixed_v16.wav`
  -> `soxi` shows no `(ffmpeg)` and **does** print `Duration ... = 5760 samples` (the ffmpeg
  path prints no Duration).
- **Consequence for the lane**: had the r61 generator produced any other byte at payload
  offset 256, SoX would have *rejected* valid17 outright and the 3,839 phenomenon would not
  exist. Prior rounds' "SoX-f32 decode" results came through the native wav reader, not the
  ffmpeg path — a hidden cross-round confound.

### 2. SoX_ng ffmpeg handler is a CLI pipe, not libav linkage

`sox_ng-14.8.0.1/src/ffmpeg.c` `startread_ffmpeg` builds:
`ffmpeg -loglevel quiet -nostdin -strict -2 -i <file> -f au -`, then reads the child output
with the **au** handler. Direct reproduction:

- `ffmpeg -loglevel quiet -nostdin -strict -2 -i pair_valid_17.wav -f au - > v17.au` (7,710 B).
  Header: `.snd`, offset 0x20, **size 0xffffffff** (streamed/unknown), **encoding 3**
  (16-bit signed linear PCM, big-endian), rate 48000, ch 1. Payload 7,678 B = **3,839 x 2 B**.
- This also resolves the r61 "`sox --i` reports 16-bit while decoding 24-bit" UNKNOWN: soxi
  reports the **AU intermediary** (16-bit, size unknown -> no Duration line), not the wav's
  effective codec.
- `ffmpeg -h muxer=au`: `Default audio codec: pcm_s16be` — the s24 decode is truncated to
  s16be in this hop.

### 3. Reclassification — valid bits *replaces* container bits

`libavformat/riffdec.c` (n9.0.1), `ff_get_wav_header` -> `parse_waveformatex` (lines 62-70):

```c
bps = avio_rl16(pb);                     /* wValidBitsPerSample */
if (bps)
    par->bits_per_coded_sample = bps;    /* 17 overwrites 16 */
```

PCM subtype GUID -> `codec_tag = 1` -> `ff_wav_codec_get_id(1, 17)` (line 83); tag 0x0001's
first table entry is `PCM_S16LE`, remapped by `ff_get_pcm_codec_id(17,0,0,~1)`
(`libavformat/utils.c:154`): `bps=(17+7)>>3 = 3` -> signed 3-byte -> **`AV_CODEC_ID_PCM_S24LE`**.
Observed: `ffprobe codec_name=pcm_s24le, bits_per_sample=24`. For 16 -> `(16+7)>>3=2` ->
`pcm_s16le` (unchanged).

### 4. Packetization — 8,192-byte chunks

`wavdec.c` `wav_read_packet`: `size = wav->max_size`, aligned down to `block_align`(=2),
capped by remaining `left`. `set_max_size` -> `ff_pcm_default_packet_size`
(`libavformat/pcm.c:29`): bitrate recomputed from the **codec** (`24*48000*1 = 1,152,000`;
the header's 96,000 B/s is superseded): `nb_samples = 1152000/8/10fps/2 = 7200 ->
1<<av_log2(7200) = 4096 -> max_size = 2*4096 = 8,192 B`.
`ffprobe -show_packets` -> `size=8192 (duration=2730)`, `size=3328 (duration=1109)` — and
ffprobe's own per-packet durations are already floored.

### 5. Decode — per-packet floor to the 3-byte frame

`libavcodec/pcm.c` `pcm_decode_frame`: `n = channels*sample_size = 3`;
`if (buf_size % n) { if (buf_size < n) -> "Invalid PCM packet ..."; else buf_size -= buf_size%n; }`.
`libavcodec/decode.c:508-512`: consumed < pkt->size -> the remainder is retained and
re-presented to the decoder, where `size < 3` errors and is dropped.

Observed verbatim on `ffmpeg -i pair_valid_17.wav -f f32le out` (exit 0, out = 15,356 B):

```
[pcm_s24le] Invalid PCM packet, data has size 2 but at least a size of 3 was expected
[dec:pcm_s24le] Decoding error: Invalid data found when processing input
[pcm_s24le] Invalid PCM packet, data has size 1 but at least a size of 3 was expected
[dec:pcm_s24le] Decoding error: Invalid data found when processing input
```

i.e. 8,192 -> 8,190 B decoded (2,730 fr) + 2 B rejected; 3,328 -> 3,327 B (1,109 fr) + 1 B
rejected. **2,730 + 1,109 = 3,839**; exactly 3 payload bytes lost — the one-frame gap.

### 6. Duration metadata

`wavdec.c:657-662`: `sample_count = (data_size << 3) / (ch * av_get_bits_per_sample(codec))
= 92160/24 = 3840 -> st->duration`. ffprobe `duration_ts=3840`, `duration=0.080000` — a
byte-count division, independent of what the decoder can actually emit.

## Discriminating controls (each changes exactly one field vs pair_valid_17)

Generator `gen_variants.py` reproduces pair_valid_17 **byte-identically**
(`a_valid_017.wav` SHA = `15cadf24...`) and pair_valid_16 (sole diff at offset 38).

| Control | Prediction from mechanism | Observed |
|---|---|---|
| `wValidBitsPerSample` sweep 0..255 | codec = `ff_get_pcm_codec_id` map | **exact**: 0->s16le/5,760; 1-8->**u8**/11,520; 9-16->s16le/5,760; 17-24->s24le/3,839; 25-32->s32le/2,880 (one 11,520 B packet); 33-40->codec NONE (sox can't open); 63-64->s64le/1,440; 65,255->NONE |
| rate 96,000 (valid=17) | max_size 16,384 -> single 11,520 B packet, 11,520%3=0 -> **no loss** | packets `[11520]`, **3,840** samples |
| rate 24,000 | max_size 4,096 -> `1365*2 + 1109` | packets `[4096,4096,3328]`, **3,839** |
| rate 8,000/12,000 | max_size 2,048 -> `682*5 + 426` | packets `[2048x5,1280]`, **3,836** |
| data 8,190 B | one aligned packet -> zero loss | packets `[8190]`, **2,730** |
| data 8,193 B | 8,192->2,730 + size-1 packet rejected | **2,730** |
| data 11,523 B | `2730 + floor(3331/3)=1110` | **3,840** |
| data 16,380 B | `2730 + floor(8188/3)=2729` | **5,459** |
| data 24,576 B | `2730 x 3` | **8,190** |
| declared data 11,517 (actual 11,520) | `2730 + floor(3325/3)=1108` | packets `[8192,3325]`, **3,838** — declared size honored |
| tag 0x0001 (non-extensible) + valid17 | `parse_waveformatex` skipped -> no override | `pcm_s16le`, **5,760** |
| cbSize 0 / 20 (fmt 40) | codec_id NONE | sox fails (`premature EOF` after ffmpeg fallback fails) |
| float subtype GUID + valid17 | `ff_get_pcm_codec_id(17,flt=1)` -> NONE | rejected |
| true 24-bit container + valid17 | s24le, block_align 3 -> max_size 12,288, all %3=0 | packets `[12288,4992]`, **5,760** |
| byte 256 0x84->0x00 | handler flips ffmpeg->native wav | native **rejects** valid17; v16 decodes 5,760 |

## Sample-content note

The "decoded" audio is garbage by construction: ffmpeg interprets the 16-bit payload's
bytes as 24-bit little-endian samples, then truncates `s24 >> 8` into s16be for AU. My
simulation `src[0:8190] + src[8192:11519]` regrouped by 3 and `>>8` reproduces `v17.au`'s
payload **byte-for-byte** (7,678 B). SoX's f32 output vs direct `ffmpeg -f f32le`: same
3,839 count, max |Δ| 3.05e-05 (the extra 16-bit truncation inside the AU hop).

## r61 UNKNOWNs — status

| r61 open question | Resolution |
|---|---|
| Why 3,839 not 3,840 | Established: per-packet floor of 8,192/3,328-byte packets to 3-byte frames; 3 payload bytes rejected at packet boundaries (2 B + 1 B). |
| 17->24-bit rounding: spec or heuristic | ffmpeg n9.0.1 heuristic: `bits_per_coded_sample := wValidBitsPerSample` (nonzero) then byte-ceil codec map. Not a spec rule; the field is malformed (>container). |
| Do other valid bits >16 behave alike | Mapped: 17-24 identical (3,839); 25-32 -> s32le; 33-40/65+ -> no codec -> rejection; packet-boundary loss varies with rate/data size (rate 96,000 -> zero loss). |
| `sox --i` 16-bit vs 24-bit decode | Not an inconsistency: soxi reports the `.snd` intermediary (encoding 3, size `0xffffffff`) produced by the ffmpeg pipe, which is also why no Duration prints. |

## Residual scope limits (reported, not claimed)

- Exact for **this host**: SoX_ng 14.8.0.1 handler order + ffmpeg n9.0.1 demuxer/decoder.
  No second host/version tested. The `act` autodetect match is payload-dependent; only the
  r61 pair's byte 256 was verified (r57/r60 bytes checked for contrast).
- The `ff_pcm_default_packet_size` bitrate path uses the recomputed codec bitrate;
  `block_align` stays the header's 2. Packet sizes are ffmpeg-internal; SoX only sees the
  AU sample stream.
- No claim about other containers, channel counts, masks, GUID subtypes, or about spec
  conformance of any party. `wValidBitsPerSample=17` remains a malformed header.

## Confidence

**High.** Every stage is source-cited (n9.0.1 / sox_ng-14.8.0.1) and independently
reproduced by single-field controls that changed the predicted quantity (codec map,
packet size via rate, boundary loss via data size, handler via byte 256). The AU
intermediary was simulated bit-exact. The only inference flagged: SoX's fallback to the
native wav handler after the ffmpeg handler fails (observed error strings are the native
reader's; fallback order itself not traced through `open_read` code).

## Receipts / artifacts

- `corpus/live/r62-boundary/runs/measurement-log.txt` — condensed log above.
- `corpus/live/r62-boundary/variants/` — 30 single-field fixtures (generator byte-exact
  vs the r61 pair).
- `corpus/live/r62-boundary/src/` — n9.0.1 `riffdec.c`, `riff.c`, `wavdec.c`, `pcm.c`
  (lavf), `pcmdec.c`, `decode.c`, `utils.c`; sox_ng-14.8.0.1 `ffmpeg.c`, `formats.c`.
- `corpus/live/r62-boundary/{v16,v17,v17ff,v16ff}.f32`, `{v16,v17}.au`,
  `gen_variants.py`, copied `pair_valid_1{6,7}.wav` (SHAs verified `15cadf24..` / `2c5e244f..`).
