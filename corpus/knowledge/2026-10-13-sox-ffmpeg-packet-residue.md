# SoX decode-length gap on malformed extensible WAV = ffmpeg per-packet residue (round 62)

- Source: round-62 seat evidence (`reports/round-62/r62-{author,boundary,scout,critic,scribe,simplifier}.md`), non-author replay `r62-verifier.md`, Sol `r62-adjudicator.md`.
- Verified at: 2026-10-13, host `/usr/bin/sox` SoX_ng v14.8.0.1, `/usr/bin/ffprobe` n9.0.1, Python 3.14.
- Recheck when: SoX/ffmpeg versions change, or `pair_valid_17.wav` payload bytes change (see fragility note).

## The measured law

For `WAVE_FORMAT_EXTENSIBLE` files routed through SoX's `(ffmpeg)` handler:

```
decoded_f32_samples = Σ over ffmpeg demuxer packets floor(packet_bytes / pcm_sample_width)
```

where sample width = `ceil8(wValidBitsPerSample)` *overriding* the container's
`bits_per_coded_sample` (17–24 → s24le/3B, 25–32 → s32le/4B, …), and packet
boundaries = `block_align · 2^⌊log2(bitrate/80/block_align)⌋` computed on the
**reclassified** bitrate (r61 pair: 8,192 B max → packets `8192 + 3328` →
`2730 + 1109 = 3,839`; the 2 B+1 B tails are rejected per packet as
`Invalid PCM packet`, total loss = one 3-byte frame).

## Required factors — removing any one changes the count

1. **Routing**: SoX sniffs `act` before `wav` on `file[256]==0x84` (payload
   byte 188). The r61 pair reaches ffmpeg *only* through that byte
   coincidence; with byte 256 `≠0x84` (or file ≤256 B, or a chunk between
   fmt/data) SoX detects `wav` and the native reader **fatally rejects**
   `valid>container` (exit 2 — a receiptless crash inside `measure()`'s
   `check=True`). Verified bidirectionally on byte flips.
2. **Reclassification**: nonzero `wValidBitsPerSample` replaces coded width;
   declared container bits are ignored. `sox --i` "16-bit" is a display
   artifact of the AU intermediary tag, not the decoded format.
3. **Packetization on reclassified bitrate**: `v17_c32` (control swapping the
   declared byte-rate to the s32le basis) yields 7,678 — the packetizer keys
   on the *reclassified* stream bitrate.
4. **Per-packet floor**: `-max_size` overrides move the count predictably
   (5000→3838, 6000→3840, 7000→3839); whole-file floor and EOF-loss are
   falsified by `pcm16_n7678`/`pcm24_n11517` controls producing 3,839 with no
   valid-bits anomaly at all.

## Gate interaction (unchanged gate, malformed headers)

| valid bits | ffmpeg codec | SoX decode | project gate |
|---|---|---|---|
| 16 (control) | pcm_s16le | 5,760 | exit 0 clean |
| 17 | pcm_s24le | 3,839 | exit 1: format+duration+level+spectrum |
| 24 | pcm_s24le | 3,839 | exit 1: format+duration+level+spectrum |
| 32 | pcm_s32le | 2,880 | exit 1: format+duration |

The gate never parses valid-bits; rejection rides ffprobe's reclassification
of the measured stream.

## Fragility note for future fixture authors

Receipts for the r61/r62 valid-bits family exist *because* the shared payload
has byte 256 = `0x84`. Any edit changing that byte silently reroutes SoX to
the native `wav` reader and converts "exit 1 with receipt" into a
`CalledProcessError` crash. SHA-pin or deliberately set the byte when
authoring probes in this family.

## Bounded unknowns retained

`act`→`au`→`ffmpeg` fallback ordering details and au's internal sniff trigger;
packetizer constants swept on a grid, not exhaustively; behavior on other
SoX/ffmpeg versions; anything about audibility, fidelity, or standards
conformance (never claimed).
