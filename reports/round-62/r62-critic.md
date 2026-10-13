# R62 critic — SoX decode-length UNKNOWN (r61 valid17 pair)

Seat: critic. Task: falsify the round's claim-in-progress on why SoX emitted
**3,839** f32 samples for `pair_valid_17.wav` vs **5,760** for `pair_valid_16.wav`
(header duration vs valid-bits vs block-boundary vs reclassified width).
Worktree: `~/Projects/prymeagnt/audio`; scratch: `corpus/live/r62-critic/`
(`gen.py`, `measure.sh`, `counts.csv`, `var/*.wav` — 174 generated variants,
all byte-verified: `rebuild_v17.wav`/`rebuild_v16.wav` SHA-256 match the r61
recorded values `15cadf24…`/`2c5e244f…` exactly).

## Verdict: the mechanism is resolved, and the naive attribution is wrong twice

The 3,839 is produced entirely inside **ffmpeg's** WAV path — SoX is a
passthrough — and it is **not** attributable to `wValidBitsPerSample=17` as a
value, nor to any declared duration, nor to a fixed "drops one frame" bug. It is
a **demuxer packet-boundary residue loss** whose size depends on data-chunk
size, declared `nBlockAlign`, and the reclassified codec's bytes-per-frame.

End-to-end chain (all on this host: ffmpeg n9.0.1, SoX_ng v14.8.0.1):

1. `libavformat/riffdec.c::parse_waveformatex`: `bps = avio_rl16` reads the
   field; `if (bps) par->bits_per_coded_sample = bps` — **wValidBitsPerSample
   unconditionally overwrites the coded-sample width** (0 is skipped → why r60's
   valid0 was inert). PCM subtype GUID → tag 1 → `ff_wav_codec_get_id(1, 17)` →
   `ff_get_pcm_codec_id` ceilings to the PCM width ladder.
2. Measured ladder: valid 1–8 → `pcm_u8`, 9–16 → `pcm_s16le`, 17–24 →
   `pcm_s24le`, 25–32 → `pcm_s32le`, ≥33 → `unknown` (0 frames out).
   So v17, v18, v20, v23, v24 all reclassify identically and all yield **3839**
   on the same payload (`counts.csv`, sweep A). The *number* 17 is irrelevant;
   the *band* 17–24 is what matters.
3. `wavdec.c::set_max_size` → `ff_pcm_default_packet_size` (pcm.c):
   `max_size = block_align · 2^⌊log2(bitrate/8/10/block_align)⌋`, with bitrate
   **recomputed from the codec** (24·48000·1 = 1,152,000 → 14,400 B per 0.1 s),
   not the header's nAvgBytesPerSec. Declared ba=2 → `2·4096 = 8192`.
4. `wav_read_packet`: `size = (max_size/ba)·ba` then `min(size,left)` → packets
   **[8192, 3328]** — verified: `ffprobe -show_entries packet=size` on the real
   `pair_valid_17.wav` prints exactly `8192 3328`.
5. The pcm_s24le decoder emits `floor(pkt_bytes/3)` frames per packet and
   **rejects each packet's <3-byte tail**: `ffmpeg -v warning` shows exactly two
   `Invalid PCM packet, data has size 2` and `size 1` errors on the r61 file —
   residues 8192 mod 3 = 2 and 3328 mod 3 = 1. Count: 2730 + 1109 = **3839**.
   Lost payload = 3 bytes = exactly one 24-bit frame.
6. `st->duration` (`0.080 s`) is itself *computed* — `sample_count =
   (data_size·8)/(ch·codec_bits)` = 11520·8/24 = 3840 — and a `fact` chunk
   declaring 1/3839/3840/5760 samples changes neither it nor the count
   (`ext_v17_n11520_fact*` all → 3839). No "declared duration" field exists.

## Per-hypothesis verdicts

| hypothesis (from the brief) | verdict | evidence |
|---|---|---|
| header-declared duration drives the count | **falsified** | no duration field exists; `fact` chunk ignored (sweep F); duration is downstream of the same reclassification (3840 ≠ observed 3839 anyway) |
| valid-bits field (value 17) causes 3839 | **falsified as stated** | v18/20/23/24 → same 3839; v25–32 → 2880 exact; field matters only through the codec-ceiling step |
| reclassified 24-bit width | **confirmed, refined** | necessary: every s24le reclassification divides data by 3; but `floor(n/3)` alone predicts 3840 — wrong by 1 |
| block-boundary / buffering | **confirmed, precisely** | packets = `min(left, ba-aligned max_size)`; decoder drops `pkt mod 3` tail per packet |

## The two requested falsifications — both achieved

**3,839 without valid-bits 17** (three independent constructions):
- `pcm16_n7678.wav` — plain tag-1 PCM16, 7678-byte data → SoX and ffmpeg emit
  **3839** (just the frame count; shows the number carries no valid-bits signal).
- `pcm24_n11517.wav`, `pcm24_n11518.wav` — plain tag-1 PCM24 → **3839** =
  `floor(11517/3)` — the exact count arises on unremarkable files.
- `ext24_v24_n11517.wav` — extensible, valid24, 24-bit container → **3839**.

**non-3,839 with valid-bits 17** (count is size/align-dependent, not
field-fated): `ext_v17_n11522` → 3840; `n11526` → 3841; `n7680` → 2560;
`ba3`/`ba6`/`ba7`/`ba48` → 3840; `ext24_v17_n11520` (valid17 *below* container)
→ 3840.

## Predictive model — verified on held-out cases

`frames = Σᵢ floor(pktᵢ/3)`, `pktᵢ = min(left, (max_size/ba)·ba)`,
`max_size = ba·2^⌊log2(14400/ba)⌋` (mono s24 48k). Spot predictions, all exact:

- n-sweep under v17 (35 sizes): P=8192 fits every point; boundary discriminator
  n=8194 → 2730 (8192+2) rules out P=4096 (would give 2731) and P≥8194 (2731).
- `ffmpeg -max_size` on the real pair: 5000→3838, 6000→3840, 7000→3839,
  8190→3840, 8191→3840, 8193→3839, 9000/12288/20000→3840.
- Block-align sweep ba∈{1..10}: observed 3839/3839/3840/3839/3839/3840/3840/
  3839/3839 — matches per-ba max_size (ba5→10240, ba10→10240 packets seen via
  `show_packets` = `10240 1280`).
- Small max_size: ms1–3 → 0 frames + 5760 invalid-packet warnings (ba-clamp
  `size<ba → size=ba` gives 2-byte packets, all rejected); ms4/5 → 2880+2880
  warnings; ms7 → **3840, zero warnings** (6-byte packets divide by 3).
- Held-out: v17 ba4 n20000 → 6665; v17 n24579 → 8191 (loses 2 frames);
  v32 n100000 → 25000 exact; v17 ba48 n11520 → 3840.

## Critic finding beyond the arithmetic: SoX never natively read the file

- `sox -V6` shows SoX **content-sniffs every fmt40-extensible WAV as `act`**
  (`ext_v16` included — all prior extensible probes went through this), then
  iterates handlers (`au` logged) and lands on the **`(ffmpeg)` input handler**.
- SoX's **native** `wav` handler **refuses** the r61 file outright:
  `sox -t wav pair_valid_17.wav` → `FAIL formats: can't open input file:
  number of valid bits exceeds the number of bits per sample` (exit-level
  failure, 0 samples). `-t wav` decodes valid16 (23040 B) and r57 valid15
  (23040 B) fine — the refusal is exactly the `valid > container` boundary.
- The sniff is fragile and content-based: inserting *any* chunk between `fmt `
  and `data` (JUNK, LIST, fact-before-data) or shrinking the file to ≤256 bytes
  flips detection to `wav` → refusal with **no ffmpeg fallback** (`-V6` shows
  wav tried, error, abort). `fact` *after* data stays `act`; data-size floor
  sits between file bytes 256→wav and 258→act (n187/n189). `-t ffmpeg` on the
  refused files decodes 3839/32 normally — so the refusal is routing, not
  undecodability.
- `sox --i` prints `Precision: 16-bit / 16-bit Signed Integer PCM` on **every**
  fmt40-extensible variant tested (codec u8/s24/s32, container 16 or 24) —
  answering r61's residual UNKNOWN: the `--i` line is a constant display
  artifact of the ffmpeg handler's header summary, not a decode-width
  inconsistency. The decoded stream follows ffprobe's reclassified codec.
- SoX vs ffmpeg f32 payloads for valid17 differ only in last-digit conversion
  rounding (ratio 1.0, ~1e-5); **counts identical (3839)**, so SoX contributed
  nothing to the count.

## Impacted axes

- **depth**: the r61 UNKNOWN is fully resolved — the round's axis move is
  achievable, *provided* the claim is worded as the ffmpeg-side chain above.
  A claim phrased as "SoX reads valid-bits" or "valid17 drops a frame" would be
  a misattribution the record cannot support: the value 17 is incidental
  (17–24 identical), the loss is packet-residue (not a frame drop), and SoX
  only reaches this path through `act` mis-sniffing — its own wav handler
  refuses the file.
- **quality**: all numbers reproducible; generator + `counts.csv` + variant
  files in scratch; rebuild SHAs match r61 exactly.
- **discernment / defect-vs-tradeoff**: this is a fixable **wording defect**
  risk, not a gate problem — and a scope note: the effect is ffmpeg-local
  packetization, scales with packet count (can lose ≥1 frames: n24579 loses 2),
  and also silently truncates on *non-extensible* PCM24 files when data bytes
  aren't 3-aligned (pcm24_n11517 → 3839). Whether that truncation is "a
  decoder bug" is out of lane scope; for the lane's claim it suffices that the
  behavior is deterministic, parameter-predictable, and unrelated to valid-bits
  semantics per se.

## Smallest safe correction

Report the mechanism as: *valid-bits > 16 (nonzero overwrite of
bits_per_coded_sample) → ffmpeg ceilings codec to s24le → demuxer emits
ba-aligned ~8192-byte packets → pcm decoder rejects each packet's mod-3 tail;
11520 B → 8192+3328 → 2730+1109 = 3839 (one frame's worth of residue bytes
lost).* Note explicitly: SoX native wav refuses `valid > container`; the 3,839
measurement exists only via SoX's `act`→`(ffmpeg)` handler routing.

## Receipts

- `corpus/live/r62-critic/counts.csv` — 160-row ffprobe/ffmpeg/sox matrix.
  (Disclosure: `sox_exit` column captures `wc`'s status, not sox's — the 0-byte
  rows are real sox refusals, re-verified individually with `-t` flags.)
- `corpus/live/r62-critic/var/` — 174 variant WAVs + `gen.py`/`measure.sh`
  (deterministic rebuild; `rebuild_v{16,17}.wav` SHA-match r61).
- `corpus/live/r62-critic/base{16,17}.f32`, `ff{16,17}.f32` — decode artifacts;
  base17 SHA `3cda5978…` matches r61's recorded `valid17.f32` exactly.
- Key commands: `sox -t wav/-t ffmpeg/-V6/-show_packets`,
  `ffmpeg -v error -max_size <n> -i … -f f32le -acodec pcm_f32le - | wc -c`,
  `ffprobe -show_entries stream=codec_name,…,packet=size`.
- ffmpeg source corroboration: n9.0.1 `riffdec.c::parse_waveformatex`,
  `wavdec.c::wav_read_packet`/`set_max_size`, `pcm.c::ff_pcm_default_packet_size`
  (fetched source, quoted logic above — read-only reference, not in-repo).
