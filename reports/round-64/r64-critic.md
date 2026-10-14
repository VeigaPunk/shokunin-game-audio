# r64 — critic — audio lane — falsify the valid-bits step-map attribution

Seat: critic. Task: attack the claim that ffmpeg's negotiated codec under the
`act` bridge is a step map over `wValidBitsPerSample` — (a) test whether
container bit depth (byte 34) and other header fields actually drive the codec,
(b) break the per-packet floor count law at some width/alignment, (c) find a
case where ffprobe agrees but the SoX count contradicts the predicted law.

Worktree: `~/Projects/prymeagnt/audio`; scratch+receipts
`corpus/live/r64-critic/` (`probe.py`, `runs/probe-results.tsv` ~140 rows,
`var/` 153 built exhibits). Host: SoX_ng 14.8.0.1, ffmpeg/ffprobe n9.0.1
(`pacman -Q` ffmpeg 2:9.0.1-4), python3 3.14.7. Base fixture
`round-61/pair_valid_17.wav` sha `15cadf24…` (all variants either byte-patched
or structurally rebuilt from it; byte 256 re-pinned to `0x84` where noted —
the r63 act-pinning technique).

Probe primitives per variant: `ffprobe stream=codec_name,bits_per_coded_sample,
channels`; `ffprobe packet=size` (demuxer packet receipts); `sox -V4` detected
type; `sox <f> -t f32 -` count (natural route); `sox -t act <f> -t f32 -`
count (forced bridge); `ffmpeg … -f au -` wire header.

## Verdict — per-hypothesis

| hypothesis | verdict |
|---|---|
| (a) codec driven by container bps (byte 34), not valid-bits | **FALSIFIED in stated direction** — declared bps loses to any nonzero valid-bits in BOTH directions (decl24/v16→s16le; decl8/v24→s24le). But the stronger claim "step map is a *pure function* of valid-bits" is **FALSIFIED**: at fixed valid=17 the codec is s24le, s16le, alaw, mulaw, adpcm_ms, mp3, ac3, or *none* depending on six other inputs (see A-series). The map is a 1-D slice of a multi-input function. |
| (b) the Σfloor(pkt/width) count law breaks at some width/alignment | **Law mechanism CONFIRMED at 40+ alignments, sufficiency of inputs FALSIFIED.** Every observed count equals Σfloor(pktᵢ/frame) — including sub-frame packets dropping whole ([8192,1]→+0) — but the *count* at fixed valid-bits moves with declared `block_align` (3839↔3840), declared vs physical `data_size`, the LAST `data` chunk (rebase, not append), and `data_size∈{0,0xFFFFFFFF}` streaming. The stated packet formula is also missing its `× nb_channels` factor and uses canonical codec bits, not the valid value. |
| (c) ffprobe agrees but SoX count contradicts | **FOUND, three ways.** (i) `valid24 + block_align4` → ffprobe `pcm_f24le` (named codec) → SoX 2,880 ≠ width-3-law's 3,839 — a hidden codec flip via `block_align==4·ch` (wavdec.c:671). (ii) adpcm_ms/mp3/ac3 GUID tags → ffprobe *names* a codec → SoX yields **0 samples with exit 0** (silent empty-au — a different failure class from codec-NONE's exit-2 `premature EOF`). (iii) stereo `ch=2` → SoX 3,840 ≠ mono-law 3,839 (count is frames×ch on the wire; floor is per frame). |
| fallback within a sweep / stream | **No codec fallback exists — ever.** Codec is chosen once at header parse; valid 33–56 & ≥65 (incl. all of 256–65535 via byte 39) are codec-NONE *holes*, not fallbacks. `valid=0` → falls back to declared bps (decl24/v0→s24le/3,839; decl57/v0→s64le/1,440; decl0/v0→NONE/EOF). The real "continuation" surprise is in the *data extent*: a second `data` tag **replaces** the stream (last wins), and size 0/`0xFFFFFFFF` reads rest-of-file as audio. |

## What the codec actually is (n9.0.1 source-pinned, receipts below)

```
codec = f( tag==0xFFFE                       # riffdec.c:179  — else valid-bytes
                                              #   are just extradata
         ∧ fmt_size ≥ 40 ∧ cbSize ≥ 22       # :186-195      — parse gates
         ∧ GUID tail ∈ {AMBISONIC,BROKEN,    # :76-84        — else guid-table
                        MEDIASUBTYPE base}   #               #   lookup → NONE
         , guid_tag → codec-class            # ff_wav_codec_get_id :277-292
                                               #   1→int path, 3→flt path,
                                               #   6/7→alaw/mulaw, else tag table
         , bps_eff = valid ? valid : declared # parse_waveformatex :68-70
         , THEN post-parse kludges           # wavdec.c:664-674
             s24le + ba==4·ch + bps_coded==24 → pcm_f24le
             s32le + ba==4·ch + bps32 + extradata{01 00} → pcm_f16le )
```

### A-series receipts — codec flips at FIXED valid=17 (same bytes 38-39)

| variant | ffprobe codec | packets | SoX f32 | why |
|---|---|---|---|---|
| base | pcm_s24le | [8192,3328] | 3,839 | — |
| A1 decl=24 | pcm_s24le | [8192,3328] | 3,839 | declared inert vs valid≠0 |
| A1 decl=8 | pcm_s24le | [8192,3328] | 3,839 | valid wins upward… |
| A1 decl=24,valid=16 | pcm_s16le | [8192,3328] | 5,760 | …and downward |
| **A1 decl=24,valid=0** | **pcm_s24le** | [8192,3328] | **3,839** | **valid=0 → declared wins** |
| A1 decl=57,valid=0 | pcm_s64le | [11520] | 1,440 | fallback itself step-maps |
| A1 decl=0,valid=0 | **unknown** | — | exit 2 | both empty → NONE |
| **A2 tag=0x0001** | **pcm_s16le** | [8192,3328] | **5,760** | **non-extensible: valid17 → extradata** |
| A2 tag=0x0003 | unknown | — | exit 2 | float tag, bps16 → flt-path NONE |
| **A2 tag=0x0006** | **pcm_alaw** | [4096,4096,3328] | **11,520** | alaw: valid-bits never consulted |
| **A3 cbSize ∈ {0,1,20,21}** | **unknown** | — | **exit 2** | **parse gate — valid bytes unreachable** |
| A3 cbSize ≥ 22 | pcm_s24le | [8192,3328] | 3,839 | gate opens (incl. 0xFFFF) |
| A4 fmt_size ∈ {16,18,38} | unknown | — | exit 2 | cbSize clamps below 22 |
| A4 fmt_size=39 | — | `no 'data' tag` | exit 2 | parser desync: loses data chunk entirely |
| **A5 guid_tag=3** | **unknown** | — | **exit 2** | **flt path has no 17–24 band** |
| A5 guid_tag=6/7 | pcm_alaw/mulaw | [4096,…,3328] | 11,520 | companded 8-bit, 1 B/sample |
| A5 guid_tag=2 | adpcm_ms | [2048×5,1280] | **0, exit 0** | named codec, zero decodable frames |
| A5 guid_tag=0x55/0x2000 | mp3/ac3 | [11520] | **0, exit 0** | same silent-zero class |
| A5 guid_tag=0x11 | (ima_adpcm) | — | exit 2 | open-time fail (needs channel layout) |
| A6 guid tail byte↯ / zeroed | unknown | — | exit 2 | non-base GUID → guid-table miss → NONE |
| A7 valid ∈ {256,…,65535} | unknown | — | exit 2 | byte-39 values all holes |
| A8 ch=0 | (pcm_s24le named) | — | exit 2 | decode-open EINVAL |
| A8 rate=0 | — | `Invalid sample rate` | exit 2 | header reject |
| A8 mask ∈ {0,3} | pcm_s24le | [8192,3328] | 3,839 | mask inert (layout reset to declared ch) |

At fixed valid-bits, byte-38 tells you nothing without the gate inputs. The
boundary pair the lane tracks should carry the gate precondition or one of
these single-byte diffs as a falsifier pair.

## B-series — count law: mechanism confirmed, input sufficiency falsified

Exact packet law now (pcm.c:29-55 + wavdec.c:792-799), predicted vs measured:

```
max_pkt = ba_decl · 2^⌊log2 clip64( codec_bits·rate·ch /80/ba_decl , 1, INT_MAX/ba_decl )⌋
          codec_bits = av_get_bits_per_sample(codec_id)   # canonical: 24 for ALL of 17–24
          ba_decl    = declared nBlockAlign (byte 32)     # NOT reclassified frame
          ba ≤ 0 → EINVAL → max_pkt = 4096
packets = chunks of ≤max_pkt, last = min(max_pkt, left); pcmdec drops buf%n per
          packet (whole packet if buf < frame n = ch·width)
```

| variant | packets | count | law check |
|---|---|---|---|
| v17 ba∈{1,2,4,8,16,8192} | [8192,3328] | 3,839 | nb formula → 8192 each, telescopes |
| **v17 ba∈{3,6,7,12,16384,40000,65535}** | **[11520]** | **3,840** | max 12288/14336/16384/ba → single → **same valid-bits, +1 sample** |
| v17 ba=5 | [10240,1280] | 3,839 | different split, same count — packet shape ≠ count |
| v17 ba=0 | [4096,4096,3328] | 3,839 | EINVAL→4096 fallback, no ba-rounding |
| v17 byte_rate ∈ {0,1,48000,…,0xFFFFFFFF} | [8192,3328] all | 3,839 | **declared byte_rate inert** — packetizer self-recomputes (pcm.c:41-44 "don't trust codecpar bitrate") |
| **v17 ch=2 ba=4** | **[11520]** | **3,840** | **bitrate = bits·rate·CH confirmed: 2.304e6 → max 16384 → single → 1,920 frames ×2** |
| v17 ch=3 ba=6 | [11520] | 3,840 | 3,456e6… → single → 1,280 fr ×3 |
| **v24 ba=4 mono** | [11520] | **2,880** | **pcm_f24le flip — codec changed, not just count** |
| v24 ba=8 stereo | [11520] | 2,880 | same flip at ba==2·4 |
| **v32 ba=4 + extradata{01 00}** | [11520] | **2,880** | **pcm_f16le flip** (f16/f24 are 32-bit-container floats → w=4) |
| v32 ba4+ext{00}, v32 ba2+ext{01} | [11520] | 2,880 | controls stay s32le |
| v17 n∈{1,2,…,8,189,8190..8196,11517..21,16383..7,32768..71,40000} | as law | Σfloor ✓ | incl. **[8192,1]→+0** sub-frame drop; n=3→1 |
| **data_size decl < phys** (8192/11520) | [8192] | **2,730** | **declared size truncates — physical tail ignored** |
| decl 11520 > phys 8192 | [8192] | 2,730 | EOF truncation, short-read absorbed |
| decl 6 | [6] | 2 | — |
| **two 'data' chunks** (8192+3000, 3000+8192, ×3) | **[c2 only]** | **1,000 / 2,730** | **LAST data chunk wins — stream REBASES, not appends** (wavdec.c:473 `data_ofs = tell` per hit) |
| 'data'+0xFFFFFFFF tail | — | **0, exit 0** | last tag wins with INT64_MAX extent → EOF position |
| **data_size=0** | [8192,3328] | 3,839 | `data_end=INT64_MAX` → rest-of-file = audio |
| data_size=0 + 'data'+3000 tail | [8192,6336] | **4,842** | **trailing chunk headers+payload consumed as audio** |
| data_size=0xFFFFFFFF + JUNK tail | [8192,3344] | 3,844 | same: chunk headers became samples |
| LIST/INFO tail | [8192,3328] | 3,839 | ignored (as expected) |

## C-series — ffprobe-agrees / SoX-contradicts exhibits

1. **`B7_v24_ba4` / `D2p_tag1_s24_ba4_pin`**: ffprobe `pcm_f24le`, SoX 2,880.
   The width-3 prediction (3,839) fails because `block_align==4·ch`+`bps==24`
   silently rewrites the codec to a 4-byte float *after* the valid-bits map.
   Same failure via the extensible tag (B7) and the plain-PCM tag (D2p) —
   the kludge is tag-path-independent.
2. **`A5_g0002_adpcm_ms`, `A5_g0055_mp3`, `A5_g2000_ac3`**: ffprobe names the
   codec; SoX emits a valid zero-sample au stream → **exit 0 with 0 f32
   bytes**. A sweep that records only "samples" sees `0` indistinguishable
   from a crash unless it also records exit/stderr — and a gate keyed on
   "exit==0" would call these *successes*. Distinct from codec-NONE
   (`premature EOF`, exit 2).
3. **`B3_ch2_v17`**: ffprobe pcm_s24le ch2; SoX count 3,840 = 1,920 frames × 2
   ch — the "sample count" is interleaved-samples-on-wire; floor is per
   *frame* (n = ch·width in pcmdec.c:431-443). Mono-law phrasing silently
   assumes ch=1.

Also: **the AU wire is always s16be** (`ffmpeg -f au -` → encoding 3 for every
codec — the muxer's `.audio_codec` default; u8, s24, s32, s64, f32, alaw all
convert). SoX never sees the reclassified width; the 3,839 signature is purely
ffmpeg's upstream packet-residue loss. "Negotiated sample-width" in the sweep
table is a demuxer-side property only.

## Impacted axes

- **expansion**: positive — the sweep surface is larger than declared. Beyond
  the six valid-band steps the r64 map already found, this adds: the
  preconditions (tag/cbSize/fmt_size/GUID-class), a second codec-flip family
  (f16/f24 kludges via ba/extradata), the last-data-chunk rebase and
  size-0/0xFFFFFFFF streaming extents, the two failure classes (exit-2
  premature-EOF vs exit-0 silent-empty), and declared-bps fallback at valid=0.
- **quality**: positive — mechanism moved from "consistent with
  ff_get_pcm_codec_id" to exact n9.0.1 lines with live packet receipts at
  every boundary (all B1 predictions matched, including ba=0→4096 and
  clip(…,1) at ba≥16384).
- **discernment**: the claim under test — "the reclassification is a step map
  over valid-bits values" — is **true as a slice, false as a function**. Any
  recorded boundary pair implicitly carries `tag=0xFFFE ∧ fmt≥40 ∧ cbSize≥22
  ∧ base-GUID-tail ∧ PCM-subclass ∧ declared-ba/geometry fixed`; one-byte diffs
  exist that hold valid-bits constant and change codec+count. The sweep
  record should name the gate so a future seat doesn't read the table as a
  pure map.

## Smallest safe correction

1. Keep the valid-bits sweep, but state the preconditions in the record and
   per-value record the *gate inputs* (or note them fixed). Boundary-pair
   candidates that pin a real step with clean receipts: **{24,25}** (s24|s32,
   both exit-1) — prefer over {32,33} whose second leg needs the r63
   try/except wrap; alternatively **{56,57}** if the hole-edge is the
   interesting boundary. A falsifier pair for the report's own gate: reuse
   `A3_cb21` vs `A3_cb22` (same valid17, codec NONE vs s24le).
2. Record count as `frames × channels` and declare `block_align`,
   `data_size`/EOF, and last-`data`-tag position as count inputs — the
   packet-residue signature is otherwise misattributed to valid-bits alone.
3. For codec-NONE values keep the r63 try/except wrap AND record exit+sample
   count — exit-0-with-0-samples (named codec, zero frames) is a real third
   outcome the sweep's decode/die dichotomy misses.

Stop after this review. Receipts: `corpus/live/r64-critic/probe.py`,
`runs/probe-results.tsv`, `var/*.wav` (153 exhibits, byte-patched or
structurally built from `round-61/pair_valid_17.wav` sha `15cadf24…`; byte-256
act-pin noted per row where applied). Source citations: ffmpeg n9.0.1
`libavformat/riffdec.c` :62-92,99-138,179-195,240-272,277-292; `wavdec.c`
:452-480,630-681,687,792-799; `libavformat/pcm.c` :29-55; `libavcodec/pcm.c`
:407-446; `libavformat/au.c` :46-62.
