# R62 author — r61 SoX decode-length UNKNOWN resolved (packet-boundary remainder law)

host: devin (same lane as R61)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `1c52c7d`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` HEAD `8ec47838` (`.shokunin/audio` is a symlink
into the canonical repo; tracked changes live there).

## Scoped move

R61 left one UNKNOWN: the matched `pair_valid_17.wav` / `pair_valid_16.wav` differ only at byte
38 (`wValidBitsPerSample` 17 vs 16), yet SoX decoded **3,839** vs **5,760** f32 samples and
ffprobe reported `pcm_s24le 0.080 s` vs `pcm_s16le 0.120 s`. R62's declared depth move:
establish the exact mechanism with discriminating controls, then — iff a mechanism survives —
land minimal additive tracked controls that pin it. The mechanism is **established**; no
bounded UNKNOWN remains on the decode-length question.

## Mechanism (all four factors required; each isolated below)

1. **Loader selection is content-dependent.** SoX `formats.c` probes ACT before WAV:
   `CHECK(act, 0, 4, "RIFF", 256, 1, "\x84")` precedes `CHECK(wav, 0, 4, "RIFF", 8, 4, "WAVE")`.
   The R61 payload happens to carry `0x84` at file offset 256 (payload sample 94 = 1156 =
   0x0484). So `sox -V6` prints `detected file format type 'act'` and
   `Input File ... (ffmpeg)` — SoX's FFmpeg-backed pseudo-format handles the file, piping
   `ffmpeg -loglevel quiet -nostdin -strict -2 -i FILE -f au -` (16-bit PCM AU — which is why
   `sox --i` reports 16 bits despite the s24le source decode). With any other byte at 256,
   default SoX takes its **native** wav path and *rejects* the file:
   `number of valid bits exceeds the number of bits per sample` (exit 2).
2. **FFmpeg reclassifies the codec from `wValidBitsPerSample`.** `riffdec.c`
   `parse_waveformatex()` copies nonzero `wValidBitsPerSample` into `bits_per_coded_sample`;
   `lavf_utils.c` `ff_get_pcm_codec_id()` maps `(bps + 7) >> 3` bytes to the signed LE PCM
   codec (8-bit special-cases to `pcm_u8`). 17 → `pcm_s24le` (bytes-per-sample w = 3).
   Measured map: valid 8 → `pcm_u8` (11,520 samples); 16 → `pcm_s16le` (5,760);
   17/20/24 → `pcm_s24le`; 25/32 → `pcm_s32le` (2,880); 33/40/48/56 → codec `unknown`,
   SoX `premature EOF` exit 2; 57/64 → `pcm_s64le` (1,440).
3. **Packetization uses the reclassified bitrate and the DECLARED `nBlockAlign`.**
   `pcm.c`: max packet = `block_align · 2^⌊log2(bitrate / 80 / block_align)⌋`;
   `wavdec.c` then floors each packet to a `block_align` multiple. For valid17:
   bitrate = 24·48000 = 1,152,000 → 1,152,000/80/2 = 7,200 → 2^⌊log2 7200⌋ = 4,096 →
   max packet = 2·4096 = **8,192** → the 11,520-byte data chunk splits `[8192, 3328]`.
   `v17_c32` (32-bit container, valid 17) decides the bitrate basis: reclassified bitrate
   predicts `[8192,8192,6656]` → 7,678; declared byte-rate basis predicts `[16384,6656]` →
   7,679. Measured **7,678** → FFmpeg uses the reclassified bitrate.
4. **Per-packet remainder drop.** `pcmdec.c` emits `floor(pkt/w)` samples per packet and
   discards the tail bytes (a packet smaller than w is rejected whole).
   valid17: `floor(8192/3) + floor(3328/3)` = 2,730 + 1,109 = **3,839**; the 2-byte + 1-byte
   remainders sum to exactly one 3-byte sample — that is the entire 3,839-vs-3,840 gap.

Composed law, verified on every control below: **decoded samples = Σ floor(pktᵢ / w)**,
w = ceil8(`wValidBitsPerSample`)/8, packets = `min(mp, remaining declared data)` iterated.

## Discriminating controls (all measured this round; `sox -t ffmpeg` forced where noted)

| variant (one field changed vs ctrl) | codec | packets | samples | prediction |
|---|---|---|---|---:|
| `ctrl_valid17` (= r61 header shape) | pcm_s24le | [8192,3328] | **3,839** | 3,839 ✓ |
| block_align 1 | pcm_s24le | [8192,3328] | 3,839 | ✓ |
| block_align 3 | pcm_s24le | [11520] | **3,840** | ✓ (boundary gone → +1) |
| block_align 4 | pcm_s24le | [8192,3328] | 3,839 | ✓ |
| block_align 5 | pcm_s24le | [10240,1280] | 3,839 | ✓ |
| block_align 6 | pcm_s24le | [11520] | **3,840** | ✓ |
| block_align 8 | pcm_s24le | [8192,3328] | 3,839 | ✓ |
| valid 20 / 24 | pcm_s24le | [8192,3328] | 3,839 | ✓ |
| valid 25 / 32 | pcm_s32le | [11520] | **2,880** | ✓ (w=4, exact divide) |
| valid 64 | pcm_s64le | [11520] | 1,440 | ✓ |
| data 8,194 B | pcm_s24le | [8192,2] | **2,730** | ✓ (2-B tail packet rejected whole) |
| data 8,190 B | pcm_s24le | [8190] | 2,730 | ✓ |
| data 8,196 B | pcm_s24le | [8192,4] | 2,731 | ✓ |
| data 11,521 B | pcm_s24le | [8192,3329] | 3,839 | ✓ |
| data 11,522 B | pcm_s24le | [8192,3330] | 3,840 | ✓ |
| declared data size 17,280 (> real) | pcm_s24le | [8192,3328] | 3,839 | ✓ EOF clamp |
| declared data size 5,766 (< real) | pcm_s24le | [5766] | **1,922** | ✓ declared size bounds reads |
| `fact` chunk added | pcm_s24le | [8192,3328] | 3,839 (`-t ffmpeg`) | ✓ fact ignored |
| true PCM24 file (ba 3) | pcm_s24le | [11520] | **3,840** | ✓ width alone loses nothing |
| `v17_c32` (32-bit container, valid 17, ba 4) | pcm_s24le | [8192,8192,6656] | **7,678** | ✓ reclassified-bitrate basis |
| sweep d23040 ba5 / ba2 | pcm_s24le | [10240,10240,2560] / [8192,8192,6656] | 7,679 / 7,678 | ✓ |
| sweep d16384 ba3 / d8194 ba3 | pcm_s24le | [12288,4096] / [8194] | 5,461 / 2,731 | ✓ |
| r61 `pair_valid_17` / `pair_valid_16` | pcm_s24le / pcm_s16le | [8192,3328] | **3,839 / 5,760** | ✓ |

28 predictions, 28 confirmations. A single-row mismatch would have falsified the law; none did.
A depth-2 `ufo-labrat` probe independently derived the same table analytically from the
generators and confirmed the two measured anchors (3,839 / 5,760); its exec-free report is in
the dispatch transcript.

### Eliminated hypotheses
- **Header duration / fact fields**: `declared_long` still 3,839; `fact5760` still 3,839 via the
  ffmpeg path. Declared data size only *bounds* reads (`declared_short` → 1,922), it does not
  cause the 3,839-vs-5,760 gap.
- **Reclassified width alone**: `pcm24_true` (genuine s24le, ba 3) decodes all 3,840 — the −1
  needs the packet split, which needs stale `block_align=2` (or any cut not ≡0 mod 3).
- **Block boundary alone**: `ba3`/`ba6` variants decode 3,840 — the split only costs a sample
  when a boundary lands mid-sample, i.e. only under the 3-byte reclassified width.

### Loader-route subtlety (new this round)
`fact5760` inserts a chunk before `data`, shifting payload so file[256] = 0x06 → default SoX
takes native wav → rejects (`number of valid bits exceeds...`). `v17_c32` file[256] = 0x00 →
native wav **accepts** (17 ≤ 32 container) → 5,760 as declared 32-bit. The 0x84 collision is
required for the malformed files to reach the FFmpeg path at all; it is a property of the
payload bytes, not of any header field.

## Tracked changes (additive only; canonical fixtures/thresholds/`format_failures` untouched)

`corpus/fixtures/build_artifacts.py` **+28/−1**: new `build_ui_extensible_valid24_probe()` —
deterministic signed16 payload (`0.26·sin(2π·940·t) + 0.11·sin(2π·f2·t)`, f2 swept from 1830,
first hit f2=1903 → sample 94 = −2684 = 0xF584, pinning byte-256 = 0x84 so the pair exercises
the same default ffmpeg-bridge route as R61); emits `live/round-62/pair_valid_{24,32}.wav`;
two argparse flags + one dispatch branch.

`corpus/fixtures/measure_audio.py` **+13/−4**: two flags, mutual-exclusion sum, builder-flag
forwarding, one measurement block on `live/round-62/pair_valid_{24,32}.wav` under `SPECS["ui"]`,
and the `mode`/`suffix` chain heads prepended (newest-first convention).

Pair byte evidence: both 11,588 B; `cmp -l` → **only offset 38 differs** (0x18 vs 0x20);
SHA-256 `29e855324f9671a20367b602bb9c52055737d91553a3b08e34a088640f9199aa` (24) /
`796511768ad4b76140b699666f9d5601f8ef9477d37aca3eaea02fd55db847b5` (32); rebuild is
deterministic (identical SHA on re-run). ffprobe: `pcm_s24le 24-bit 0.080 s` vs
`pcm_s32le 32-bit 0.060 s`; default SoX decode 3,839 vs 2,880 — the pair replays the full
mechanism (reclassification + packet remainder) on a fresh payload.

## What ran — 84-command ledger (82 prior + 2 new modes at positions 2–3)

All commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>` from repo root;
receipts under `corpus/live/runs/<stamp>-<suffix>/measurements.json`. Full TSV:
`corpus/live/r62-author/scratch/ledger-r62.tsv`. Totals: **43 exit 0 / 41 exit 1**
(R61's 43/39 plus the two new exit-1 probes). Every prior-mode exit code AND failure string
matched the R61 ledger verbatim (spot-diffed rows 4–79); invalid battery identical
(`short_sections=section count; corrupt=decode; wrong_format=format; odd_sections=section count; native16_probe=pass(None); native24_probe=format; stereo48_probe=format; mono441_probe=format`).

New-mode receipts:
- `--probe-ui-extensible-valid-24-r62` → exit 1, receipt
  `corpus/live/runs/20261013T225311600340Z-ui-extensible-valid-24-r62/measurements.json`;
  sole failing entry `ui_extensible_valid_24_r62_probe`: `format: expected PCM16`,
  `duration: outside ±1 ms`, `level: clipping headroom or near silence`,
  `spectrum: centroid outside fixture band` — identical failure signature to R61 valid17,
  on a fresh payload (peak 0.99993896484375, centroid 11986.406764033485 Hz).
- `--probe-ui-extensible-valid-32-r62` → exit 1, receipt
  `corpus/live/runs/20261013T225312774439Z-ui-extensible-valid-32-r62/measurements.json`;
  `ui_extensible_valid_32_r62_probe`: `format: expected PCM16`, `duration: outside ±1 ms`
  (peak 0.092437744140625, centroid 3319.9866546749595 Hz — s32le decode stays inside the
  level/centroid bands; the pair discriminates even within failure classes).
- Normal run receipt `20261013T225310415061Z-normal/measurements.json` is **JSON-identical**
  to R61's normal `20261013T165521565727Z-normal` — zero corpus drift.

Setup errors encountered and corrected (no receipts affected): first ledger attempt ran from
the canonical repo with the worktree-relative path → 84× exit 2 file-not-found, discarded and
re-run from the worktree; ledger script's failure-column parser had a quoting bug (fixed
post-hoc by re-reading the written receipts; exit codes were captured correctly in-line).
`python3 -m py_compile` both fixture scripts → exit 0; `git diff --check` → clean.
Two tracked `__pycache__/*.pyc` binaries differ — mechanical `py_compile` regeneration churn,
same as prior rounds; disclosed, parent decides.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: the R61 UNKNOWN is fully decomposed — loader autodetect byte, valid-bits→codec
  map, bitrate-scaled block-aligned packetization, per-packet remainder floor. One frame's
  provenance is exact (2 B + 1 B remainders = one 3-byte sample).
- **coverage**: 28 discriminating controls measured + a new byte-38 matched pair (24 vs 32)
  pinning reclassification *and* the remainder signature (3,839 vs exact 2,880).
- **calibration**: 84-command ledger preserves R61 shape exactly; normal receipt
  JSON-identical; new probes land inside expected failure classes.

## Conditional replay shape (for the non-author verifier)

84 commands = the R61 82 verbatim with `--probe-ui-extensible-valid-24-r62` and
`--probe-ui-extensible-valid-32-r62` inserted at positions 2–3. Expected 43 exit 0 / 41 exit 1.

## UNKNOWNs / limits

- Verified on this host only: ffprobe/FFmpeg n9.0.1, SoX_ng v14.8.0.1. The ACT-collision route
  is a SoX-version behavior; other builds may order probes differently.
- ffprobe packetization constants (`/80`, pow2 sizing) are source-read + fit-verified on the
  swept grid; interior parameter space not exhaustively enumerated.
- Native wav path behavior for valid>container was only exercised via reject/accept at the
  boundary (17>16 reject, 17≤32 accept); native decode content for accepted malformed files
  not characterized.
- No standards-conformance, fidelity, audibility, production, rights, engine, or promotion
  claim. These are local fixture measurements on deliberately malformed headers.

## Blockers

None. One labrat dispatched (packet-law verification); it confirmed analytically — no writes.
No commit/push/merge performed; parent integrates.
