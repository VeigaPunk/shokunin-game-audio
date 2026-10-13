# R62 scribe — SoX/ffprobe decode-length mechanism for the valid17 header

Seat: scribe (report-only documentation draft). Host: devin. Lane axis this
round: **depth** — resolve the r61 UNKNOWN "why does SoX decode
`pair_valid_17.wav` to 3,839 f32 samples rather than the expected 3,840".

Toolchain on record: `ffprobe version n9.0.1`, `ffmpeg version n9.0.1`,
`sox: SoX_ng v14.8.0.1` (all `/usr/bin`). Scratch and fixtures under
`.shokunin/audio/corpus/live/r62-scribe/` (`variants/`, `dec/`,
`gen_variants.py`, `results.tsv`, `runs/`). No tracked file, fixture, receipt,
predicate, or another lane's surface was written; nothing committed.

## Verdict on the declared claim

The 3,839-vs-3,840 gap is **established, reproduced, and attributed**. It is a
libavformat/libavcodec *packet-boundary floor*, amplified by a SoX-specific
routing accident: the file only reaches a decoder that emits 3,839 samples
because SoX's content sniffer misclassifies the payload as `act` on the
strength of one byte (file offset 256 = `0x84`). Nothing in the header
"duration" is consumed, and the missing sample is not a fixed off-by-one.

## Established mechanism (all steps reproduced; commands quoted below)

1. **Reclassification.** For `WAVE_FORMAT_EXTENSIBLE` + PCM subtype GUID,
   ffmpeg n9.0.1's wav demuxer takes non-zero `wValidBitsPerSample`
   (fmt extension, file offset 38) as the coded-sample width, rounded up to
   whole bytes. Observed map (16-bit container held constant, only byte 38
   swept; this seat tested vb ∈ {0,1,7,8,9,11,15,16,17,18,20,23,24,25,31,32,
   33,40,255}): vb 1–8 → `pcm_u8` (tested 1,7,8); 9–16 → `pcm_s16le`
   (tested 9,11,15,16); 17–24 → `pcm_s24le` (tested 17,18,20,23,24 — sibling
   `r62-boundary` reports the full 17–24 interval); 25–32 → `pcm_s32le`
   (tested 25,31,32); 33, 40, 255 → `codec_name=unknown` (ffmpeg decode
   exit **234**, 0 samples). vb 0 → falls back to container `s16le`.
   `bits_per_raw_sample` reports the reclassified width (24). Stream duration
   is metadata division `data_bytes / width / rate` — 11520/3/48000 = 0.080 s
   = a *nominal* 3,840 frames — it does **not** drive the decoder.

2. **Decode count = Σ floor(packet_bytes / width).** `ffprobe -show_packets`
   on `pair_valid_17.wav` emits packets `8192 + 3328` bytes (durations 2730,
   1109). The `pcm_s24le` decoder consumes whole 3-byte samples per packet;
   each packet's remainder bytes are resubmitted and rejected —
   ffmpeg stderr literally prints `Invalid PCM packet, data has size 2` then
   `size 1` — so 2730 + 1109 = **3,839**, i.e. 3 bytes = exactly one nominal
   24-bit frame is lost across the two packet boundaries.

3. **Discriminating controls (all seven predictions exact).** Same header
   (byte-38 = 17), only data-chunk size varied:

   | data bytes | demux packets (ffprobe) | Σ floor(p/3) | observed ffmpeg f32 | remainder errors |
   |---:|---|---:|---:|---:|
   | 24 | 24 | 8 | **8** | 0 |
   | 3840 | 3840 | 1280 | **1280** | 0 |
   | 8190 | 8190 | 2730 | **2730** | 0 |
   | 8194 | 8192+2 | 2730 | **2730** (global floor 2731 — a whole sample dropped by a 2-packet boundary) | 2×"size 2" |
   | 11520 | 8192+3328 | 3839 | **3839** | "size 2","size 1" |
   | 16386 | 8192+8192+2 | 5460 | **5460** (global 5462 — loss scales with packet count) | 3×"size 2" |
   | 24576 | 8192×3 | 8190 | **8190** (global 8192) | 3×"size 2" |

   The single-packet `%3==0` cases (24, 3840, 8190) decode *exactly* —
   eliminating "header duration field", "fixed off-by-one", and "count-based
   trim". The multi-packet cases show the loss scales with the number of
   unaligned packet boundaries, i.e. **block-boundary × reclassified sample
   width** is the operative pair.

4. **s32le control (width 4).** vb 25–32 → `pcm_s32le`; `ffprobe
   -show_packets` emits one 11,520-byte packet (duration 2880) and ffmpeg
   decodes **2,880 samples with zero remainder errors** — when the
   reclassified width divides the packet sizes nothing is lost. A valid-bits
   sweep alone would never produce the 3,839 anomaly; the anomaly requires
   width 3 against the host's 8,192-byte chunking at 48 kHz mono.
   (Sibling seat `r62-boundary` traced the chunk size to
   `ff_pcm_default_packet_size` scaling with bitrate — their table:
   rate 24000 → 4096-byte chunks, rate 96000 → 16384, both reproduced as
   consistent with this law; see `corpus/live/r62-boundary/runs/measurement-log.txt`.)

5. **SoX never chose this decode — detection did.** `sox -t wav
   pair_valid_17.wav` → **exit 2**, `sox FAIL formats: can't open input file
   ... number of valid bits exceeds the number of bits per sample`. The
   native wav handler *fatally rejects* vb>container. The r61 file decoded at
   all because SoX's content sniffing reported
   `detected file format type 'act'` (`sox -V4`), which bypassed the wav
   handler and landed on the `(ffmpeg)` handler (`sox --i` prints
   `Input File: '...wav' (ffmpeg)`). The trigger is a single payload byte:
   **file offset 256 == 0x84** (payload byte 188 = low byte of PCM16
   sample #94 = `0x0484` = 1156). Prefix bisect of the r61 payload:
   ≤188 bytes → `wav` (fatal reject), ≥189 → `act` (ffmpeg decode);
   byte-value sweep at offset 256 on an all-zero payload: only `0x84` flips
   detection (0x00–0x83, 0x85–0xFF → `wav`). `sox -t ffmpeg` forces the
   ffmpeg handler and yields 3,839 regardless of the byte — confirming the
   decode is handler-level, not magic. Sibling seat `r62-boundary` located
   the source row: SoX_ng `formats.c` autodetect orders
   `CHECK(act, "RIFF"@0, 0x84@256)` *before* `CHECK(wav, "RIFF"@0,
   "WAVE"@8)`, and `act` is a name of the ffmpeg pseudo-handler
   (`ffmpeg.c names[]`) — i.e. the r61 payload satisfies both magics and
   `act` wins by table order (sibling-reported, consistent with every
   detection outcome observed here).
   **Consequence: the r61 "SoX decodes 3,839" observation was
   payload-contingent** — any byte other than 0x84 at offset 256 makes this
   host's SoX reject the same header outright.

6. **`sox --i` "16-bit" report vs s24le decode (r61 UNKNOWN #4).** Resolved
   as a display quirk: SoX prints the container `bits_per_coded_sample`
   (16) while its ffmpeg handler delivers s24le→f32. Verified on the
   independent `v17_d16386_trig.wav` (`act` trigger planted): `--i` still
   prints `Precision: 16-bit` while SoX emits 5,460 f32 samples.

7. **SoX vs ffmpeg decode equality.** Identical count (3,839) and same s24
   sequence; values differ slightly — SoX f32 max `.992279052734375` equals
   the r61 runner's recorded peak exactly (ffmpeg f32 max `.992306`),
   confirming the project runner's number came through SoX's ffmpeg path.
   Sibling `r62-boundary` attributes the small deltas (their max |Δ| =
   3.05e-05 vs my raw-f32 diff at byte 5) to SoX piping the ffmpeg decode
   through a 16-bit `au` mux/reader hop — plausible and consistent; the
   count law is unaffected.

## Eliminated hypotheses (brief's list, verbatim call)

- **header duration field** — ELIMINATED: stream duration stays `0.080000`
  (= 3,840 nominal frames) while decode yields 3,839; duration is computed
  metadata, not a decode bound (`ffprobe -show_packets` durs 2730+1109=3839
  vs stream 0.08 s; `ffprobe -count_frames` reports `nb_read_frames=2`
  packets). Single-packet controls decode their full count.
- **valid-bits (as the direct cause)** — ELIMINATED as *sufficient* cause:
  valid-bits selects the codec width (17→24 bits), which is necessary, but
  vb25–32 files (s32le) decode their full nominal count; the -1 belongs to
  the packet boundary.
- **block-boundary** — CONFIRMED as the loss mechanism: Σ floor(p_i/3) over
  8192-byte demux packets; remainder bytes rejected per packet.
- **reclassified sample width** — CONFIRMED as the interacting factor:
  width 3 makes 8192 ≡ 2 (mod 3); width 4 emits an aligned single packet and
  loses nothing.

## Commands / observed outputs (receipt excerpts; full scratch in `corpus/live/r62-scribe/`)

- `sha256sum corpus/live/round-61/pair_valid_{17,16}.wav` →
  `15cadf24…3fe4` / `2c5e244f…1d00` — match r61 recorded SHAs;
  `cmp -l` → sole differing byte offset 39 (1-based) = file offset 38,
  `0x11` vs `0x10` ✓ (octal 21/20 as printed).
- `ffprobe -v error -show_entries packet=size,duration -of csv=p=0
  pair_valid_17.wav` → `0,2730,8192` / `2730,1109,3328` (csv fields
  pts,duration,size).
- `ffmpeg -v error -i pair_valid_17.wav -f f32le -acodec pcm_f32le -` →
  15,356 bytes = **3,839** f32 samples, exit 0, stderr 2×`Invalid PCM
  packet` (sizes 2 and 1). `sox pair_valid_17.wav -t f32 -` → same 15,356
  bytes. SoX on `v17_d16386_trig.wav` → 21,840 bytes = 5,460 samples
  (`act`-detected → ffmpeg handler), matching Σ floor.
- `sox --i pair_valid_17.wav` → `Input File ... (ffmpeg)`, `Precision:
  16-bit`, `Sample Encoding: 16-bit Signed Integer PCM`.
- `sox -t wav pair_valid_17.wav -n stat` → FAIL, **exit 2**;
  `sox -V4` detection logs: `act` vs `wav` per the offset-256 byte.
- `ffmpeg -v error -i vb33_d11520.wav …` → exit **234**, 0 samples.

## Draft: `corpus/knowledge/2026-10-13-sox-validbits-decodelen.md` (content for parent decision — not landed)

```markdown
# WAVE_FORMAT_EXTENSIBLE wValidBitsPerSample: host decode-length behavior

source: local measurement on devin host — ffmpeg/ffprobe n9.0.1,
SoX_ng v14.8.0.1; fixtures `.shokunin/audio/corpus/live/round-61/
pair_valid_{17,16}.wav` (r61 SHAs `15cadf24…`/`2c5e244f…`) and
`.shokunin/audio/corpus/live/r62-scribe/variants/` + `results.tsv`;
command evidence in `reports/round-62/r62-scribe.md`; sibling source-level
corroboration in `corpus/live/r62-boundary/` (wavdec.c/pcmdec.c trace).
verified-at: 2026-10-13 (devin host, ffmpeg n9.0.1, SoX_ng v14.8.0.1).
recheck: on any ffmpeg/ffprobe/SoX version bump, on a different host, and
before any claim citing these numbers outside this host — packet sizes,
detection quirks, and the valid-bits→codec table are version-sensitive.

## What this host does to a PCM extensible header's valid-bits byte

Non-zero `wValidBitsPerSample` is taken by ffmpeg's wav demuxer as the
coded-sample width, rounded up to bytes: 1–8→pcm_u8, 9–16→pcm_s16le,
17–24→pcm_s24le, 25–32→pcm_s32le, ≥33→codec unknown (ffmpeg exit 234).
(Tested points within intervals listed in r62-scribe.md; the interval edges
are exactly 8/16/24/32 on this host.) The declared container width is
ignored for codec choice; stream duration metadata = data_bytes/width/rate
(can disagree with decoded frame count).

## Decode-length law (why 3,839 not 3,840)

decoded_samples = Σ floor(packet_bytes / reclassified_width), summed over
libavformat demux packets; per-packet remainder bytes are resubmitted and
rejected (`Invalid PCM packet, data has size {1,2}` on stderr, exit stays
0). At 48 kHz mono s24le the demux chunks at 8,192 bytes, so 11,520 bytes →
8192+3328 → 2730+1109 = 3,839 (one nominal frame lost). Single-packet
data divisible by the width decodes exactly; s32le (width 4) loses nothing.
Packet size is bitrate-derived, so the loss is host+header+rate specific —
never quote 3,839 as a property of "valid17 WAV" in general.

## SoX routing caveat (load-bearing)

SoX_ng's native wav handler fatally rejects validbits>container
(`number of valid bits exceeds the number of bits per sample`, exit 2).
The r61 pair decoded through SoX's `(ffmpeg)` handler only because content
sniffing returned `act` — triggered by byte 0x84 at file offset 256
(sibling r62-boundary, from SoX_ng source: `formats.c` orders
`CHECK(act, "RIFF"@0, 0x84@256)` before `CHECK(wav, "RIFF"@0, "WAVE"@8)`,
and `act` names the ffmpeg pseudo-handler). `sox -t ffmpeg` reproduces the
3,839 decode deterministically; `sox -t wav` reproduces the fatal
rejection. `sox --i` prints container bits (16) even while the ffmpeg path
decodes s24le — display quirk, not evidence. Do not cite a bare
`sox file.wav` decode count for malformed extensible headers without
recording which handler ran (`sox --i` shows `(ffmpeg)`).

## Bounded UNKNOWNs retained

- Whether the valid-bits→width table is spec-mandated or an ffmpeg
  heuristic; no WAV spec consulted; other hosts/decoders unmeasured.
- s64le coverage (sibling seat observed vb 63–64→s64le; not independently
  re-verified by scribe) and exact demux chunk-size rule across rates.
```

## Draft: `corpus/knowledge/2026-10-12-audio-checklist.md` — proposed appended rows

```markdown
| extensible WAV, wValidBitsPerSample > container bits | matched pair probe: `ffprobe -show_entries stream=codec_name,duration` + `ffmpeg -f f32le - | wc -c` + `sox --i` handler tag | probed 2026-10-13 r62: vb17→pcm_s24le, ffprobe duration 0.080s nominal 3840 vs decoded 3839 (per-packet floor over 8192B chunks); **payload-sensitive**: byte@256==0x84 routes SoX to `(ffmpeg)` handler else native wav rejects exit 2 |
| decode-length verification on malformed headers | count f32 bytes/4 AND record demux packets (`ffprobe -show_packets`) + which SoX handler ran; never infer samples from duration metadata alone | probed r62: metadata 3840 vs decode 3839 diverge on this host |
```

## Draft: LOG.md round-62 entry text (for parent integration)

```markdown
## Round 62 scribe — SoX decode-length UNKNOWN resolved (mechanism established)
- `reports/round-62/r62-scribe.md`: r61's "SoX 3,839 vs 3,840" gap is a
  libav packet-boundary floor, established with 7 exact-prediction size
  controls + a 19-value valid-bits sweep + SoX handler routing controls.
  Mechanism: ffmpeg n9 wav demuxer maps wValidBitsPerSample(≠0) to coded
  width ceil-to-bytes (17–24→pcm_s24le, ≥33→codec unknown); demux emits
  8192+3328-byte packets; pcm_s24le emits floor(pkt/3)=2730+1109=3839,
  remainder bytes resubmitted and rejected (stderr "size 2"/"size 1").
  Header duration (0.080s nominal 3840) is metadata division only —
  eliminated as cause, as are fixed off-by-one and count-trim models.
- Additional finding (payload-sensitive): SoX_ng's native wav handler
  fatally rejects validbits>container (exit 2); the r61 pair reached SoX's
  `(ffmpeg)` handler only via `act` misdetection triggered by byte 0x84 at
  file offset 256 (payload sample #94 low byte). `sox --i` "16-bit" is a
  display quirk vs the s24le decode. `sox -t ffmpeg` reproduces 3,839
  deterministically. Sibling seat r62-boundary's source trace
  (wavdec.c/pcmdec.c) independently reaches the same mechanism; no
  cross-seat conflicts observed by scribe.
- Drafts supplied for parent decision: knowledge entry
  `2026-10-13-sox-validbits-decodelen.md`, two checklist rows. Scribe wrote
  only `reports/round-62/r62-scribe.md` + `corpus/live/r62-scribe/`
  scratch; no commits, no other lanes.
```

## Cross-seat consistency (scribe duty: conflicts verbatim — none found)

- `corpus/live/r62-boundary/runs/measurement-log.txt` (sibling) derives the
  same Σ-floor mechanism from ffmpeg source (`wavdec.c` max_size=8192 at
  this bitrate; `pcmdec.c` remainder re-feed → reject) and matches all my
  packet/size observations, plus rate-scaling cases I did not run.
- `corpus/live/r62-critic/counts.csv` n-sweep (n=11514→3837 … n=11519→3839)
  — every count I spot-checked equals Σ floor(p_i/3) on 8192-byte chunks.
  Their files carry byte256=0x84 (cloned r61 payload) → SoX decode counts
  are via the ffmpeg handler, consistent with the routing finding here.
- No contradicting measurement observed; no claim upgraded beyond receipts.

## Remaining bounded UNKNOWNs

- ffmpeg spec-mandate vs heuristic for the valid-bits→width table; other
  hosts/decoders untested; s64le row and rate-dependent chunk sizing are
  sibling-reported, not scribe-verified.
- Whether the project measurer should treat the SoX decode count as stable:
  under current fixtures it is, but the same header with different payload
  bytes flips SoX to a fatal rejection — worth a verifier note.
- (Resolved via sibling source read) the act-vs-wav ordering: `r62-boundary`
  cites `CHECK(act, "RIFF"@0, 0x84@256)` preceding `CHECK(wav, ...)` in
  SoX_ng `formats.c` — consistent with all scribe-observed flips; scribe
  did not independently open the SoX_ng source.

## Out of scope (not performed)

No probe-flag runs against `corpus/live/round-61/` (would write another
round's dir); no runner/ledger replay (author/verifier duty); no fixture,
predicate, threshold, LOG, or knowledge file edits — drafts are enclosed
for the parent's landing decision; no git/network action.
