# wValidBitsPerSample→codec reclassification map under the act/ffmpeg bridge (round 64)

- Source: round-64 seat evidence — scribe's independent 85-variant sweep
  (`corpus/live/r64-scribe/results.tsv`, `variants/` + `manifest.sha256`,
  `gen_sweep.py`, `sweep.sh`, `logs/`); author `reports/round-64/
  r64-author.md` (74-variant sweep + landed pairs `corpus/live/round-64/
  pair_valid_{8,9,24,25,56,57}.wav` + 92-cmd ledger); critic
  `r64-critic.md` (attribution falsifications); scout `r64-scout.md`;
  boundary/verifier seats as integrated. Extends
  `2026-10-13-sox-ffmpeg-packet-residue.md` (count law) and
  `2026-10-13-sox-act-autodetect-predicate.md` (routing).
- **Precondition for the whole map** (critic's A-series): applies only to
  `wFormatTag==0xFFFE` ∧ `cbSize≥22` ∧ PCM subtype GUID. Non-extensible
  files never consult vb (it lands in extradata); non-PCM subtype GUIDs
  take the `flt=1` branch (f32le/f64le for vb 32/64 only — unexercised
  here).
- Verified at: 2026-10-13, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), `/usr/bin/ffprobe`+`ffmpeg` n9.0.1.
- Recheck when: ffmpeg/ffprobe or SoX version/build changes (the map is
  `ff_get_pcm_codec_id` + the wavdec promotion heuristics — both
  version-sensitive), or when fixture family header shape changes.

## The measured step map (16-bit container, mono 48 kHz, data 11,520 B,
## payload byte at file offset 256 = 0x84 so SoX detects `act`)

| wValidBitsPerSample | ffmpeg codec | demux packets | SoX f32 samples |
|---|---|---|---:|
| 0 | container's (here pcm_s16le) | 8192+3328 | 5,760 |
| 1–8 | pcm_u8 | 4096+4096+3328 | 11,520 |
| 9–16 | pcm_s16le | 8192+3328 | 5,760 |
| 17–24 | pcm_s24le | 8192+3328 | 3,839 |
| 25–32 | pcm_s32le | 11520 | 2,880 |
| 33–56 | none (`codec_name=unknown`) | — | 0, sox exit 2 `premature EOF` |
| 57–64 | pcm_s64le | 11520 | 1,440 |
| ≥65 | none | — | 0, sox exit 2 `premature EOF` |

Boundaries (each pinned by adjacent sole-byte-38 pairs): 8|9, 16|17, 24|25,
32|33, 56|57, 64|65. The map is **not** monotonic: 33–56 is a codec-none
band sitting between s32le and s64le. Source basis (ffmpeg n9.0.1):
`parse_waveformatex` copies nonzero vb over `bits_per_coded_sample`;
`ff_get_pcm_codec_id(vb, flt=0, be=0, sflags=~1)` ceils vb to byte width w
and tables {1→u8(unsigned branch), 2/3/4/8→s16/s24/s32/s64le, 5/6/7→NONE,
>64→NONE}.

## Decode counts are packet-residue law applications, per codec

`count = Σ floor(packet_bytes / sample_width)` over demux packets sized by
`block_align · 2^⌊log2(codec_bitrate/80/block_align)⌋` — codec bitrate is
the *reclassified* one, `block_align` is the *container's* declared value.
At 48 kHz mono with this 11,520-B payload: u8→4,096-B chunks (zero residue),
s16le/s24le→8,192-B chunks (s24le loses 2 B+1 B = one frame → 3,839),
s32le/s64le→single packet (exact 2,880 / 1,440). Codec-none rows decode 0.

## Two attribution rules that survive cross-container controls

1. vb≠0 ⇒ codec = map[vb] alone (container width never consulted for the
   codec — only for packetization via nBlockAlign). vb17 selects s24le on
   16-, 24-, AND 32-bit containers; vb8 selects u8 inside a 24-bit
   container; vb0 defers to the container.
2. Exception-by-shape, not by width: `s24le + block_align==4·ch + bpcs==24
   → pcm_f24le` promotion (wavdec.c). Same vb=24 gives s24le/3,839 on a
   16-bit container, s24le/3,840 on 24-bit, f24le/2,880 on 32-bit.
   vb017 on a 24-bit container decodes its nominal 3,840 — the r61/r62
   residue needs container alignment 2 ∧ codec width 3, i.e. it is a
   packet-boundary interaction, not a codec property.

## SoX-side consequences

- All rows were `act`-detected (payload `file[256]==0x84`). Codec-none vb
  ⇒ ffmpeg child fails ⇒ au reader `premature EOF`, exit 2 — same
  signature as a demux failure or missing ffmpeg (no fallback to `wav`).
- `sox --i` prints container `Precision: 16-bit` even while decoding
  s64le — display artifact, never codec evidence.
- Tracked boundary pair `corpus/live/round-64/pair_valid_{56,57}.wav`
  exercises the none→s64le step (sole byte-38 diff).

## Bounded unknowns retained

- Scribe sampled vb {65,100,128,200,255} as none; author reports the
  full 16-bit field (through 65,535) exhaustively — consult
  `r64-author.md` for the high-range rows.
- Stereo/multichannel packetization, other rates, float-subtype GUIDs
  (flt=1 branch), non-PCM subtypes — untouched by scribe.
- Other hosts/ffmpeg versions unmeasured; the map is an ffmpeg heuristic
  table, not a WAV-spec conformance claim.
