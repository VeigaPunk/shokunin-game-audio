# r64 — scout — audio lane — coverage

Move: map the valid-bits→codec reclassification sweep surface under the
ffmpeg bridge (r62 disclosed, r63 made deterministic) — the r62/r63
routing map, the `wValidBitsPerSample` authoring path in
`build_artifacts.py`, live ffprobe verification of the existing pairs,
and the packetization law — with file:line pointers for the extended
sweep's builder entry point.

Seat: scout (recon only). Writes: this report +
`corpus/live/r64-scout/{variants,runs}/`. No tracked edits, no commits.
Host: devin; worktree `~/Projects/prymeagnt/audio` (`.shokunin/audio` →
canonical `~/Projects/shokunin/audio-shokunin`, HEAD `37d4c57` r63
adjudication). Toolchain: SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1,
python3 3.14.7.

## Verdict

**Sweep surface fully mapped and the step map itself re-verified live
this round.** The reclassification is a pure function of the 16-bit LE
field at file offset 38 (`wValidBitsPerSample`, inside the fmt chunk) on
an otherwise identical file; every band boundary below was re-measured
on byte-38-patched copies of `pair_valid_17.wav` (all kept `0x84`@256 →
all detected `act` → ffmpeg bridge). The declared claim — a step map
over valid-bits — is **confirmed with six measured steps**, two more
than the mission's sketched range {1..16, 17..24, 25..32, 33..48}
covers.

## Step map — measured r64 (payload = r61 pair, 11,520-B data, blockAlign 2)

Variants `corpus/live/r64-scout/variants/v<V>.wav` = base
`round-61/pair_valid_17.wav` with **only** file byte 38 patched
(`cmp -l` → sole diff at 1-based offset 39; byte 39 = field high byte,
0 in every variant). Route column is `sox -V4` detection; samples =
`sox <f> -t f32 - | wc -c` / 4.

| wValidBitsPerSample | ffprobe codec | width | ffprobe packets | SoX samples | exit |
|---|---|---|---|---|---|
| **0** | pcm_s16le | 2 | [8192, 3328] | 5,760 | 0 |
| **1–8** (1,7,8) | pcm_u8 | 1 | [4096, 4096, 3328] | 11,520 | 0 |
| **9–16** (9,15,16) | pcm_s16le | 2 | [8192, 3328] | 5,760 | 0 |
| **17–24** (17,24) | pcm_s24le | 3 | [8192, 3328] | **3,839** | 0 |
| **25–32** (25,31,32) | pcm_s32le | 4 | [11520] | 2,880 | 0 |
| **33–56** (33,48,56) | **unknown** | — | — | 0 — `premature EOF` | **2** |
| **57–64** (57,64) | pcm_s64le | 8 | [11520] | 1,440 | 0 |
| **65–255** (65,128,255) | **unknown** | — | — | 0 — `premature EOF` | **2** |

Measured step boundaries: **8|9** (u8→s16le), **16|17** (s16le→s24le),
**24|25** (s24le→s32le), **32|33** (s32le→*no codec*), **56|57**
(*no codec*→s64le), **64|65** (s64le→*no codec*). Consistent with the
r62-cited law `ff_get_pcm_codec_id` on `ceil8(valid)>>3` bytes
(1→u8, 2→s16, 3→s24, 4→s32, 8→s64, else none) and r62-author's own
12-point map ({8,16,17,20,24,25,32,33,40,48,56,57,64} — same bands).

Two edge semantics worth pinning in the sweep record:

- **valid=0 is "absent", not "0-bit"** — the nonzero check falls back
  to container `wBitsPerSample`=16 → pcm_s16le (5,760). A 0-vs-1 pair
  steps *down* (s16→u8).
- Codec-`unknown` values decode **nothing**: ffmpeg emits an empty pipe,
  the au reader dies `premature EOF`, SoX exits **2** (verified v33;
  ffprobe still prints `codec_name unknown` and a container-derived
  `format.duration` = 0.120 s). Inside `measure()` this is a
  `CalledProcessError` → receiptless *unless wrapped* (see measurer
  map). Failure is downstream of routing — `detected 'act'` still fires.

## Packetization law — verified r64 on all four widths

`max_packet = declared_block_align(2) · 2^⌊log2(reclassified_bitrate / 80 / block_align)⌋`
with `reclassified_bitrate = reclassified_bps · 48000`; SoX samples =
`Σ floor(pktᵢ / w)`. Re-measured packet splits (`ffprobe
-show_entries packet=size,duration`):

| codec | reclass. bitrate | /80/ba=2 | 2^floor(log2) | max pkt | split of 11,520 | Σ floor(pkt/w) |
|---|---|---|---|---|---|---|
| u8 | 384,000 | 2,400 | 2,048 | **4,096** | [4096,4096,3328] | 11,520 |
| s16le | 768,000 | 4,800 | 4,096 | **8,192** | [8192,3328] | 5,760 |
| s24le | 1,152,000 | 7,200 | 4,096 | 8,192 | [8192,3328] | 2,730+1,109 = **3,839** |
| s32le | 1,536,000 | 9,600 | 8,192 | **16,384** | [11520] single | 2,880 |
| s64le | 3,072,000 | 19,200 | 16,384 | **32,768** | [11520] single | 1,440 |

The r62 packet-residue signature (8192+3328 → 3,839) reproduces
verbatim; the packet granule itself **steps with the reclassified
bitrate** — a second step function the sweep can record per value
(s24le is the only width that loses samples on this payload: 2 B+1 B
tails = one 3-byte frame; all other widths divide cleanly, matching
r63-boundary's residue-free table).

## Builder map — `corpus/fixtures/build_artifacts.py` (904 lines)

All valid-bits fixtures share one fmt recipe; `wValidBitsPerSample` is
the 8th pack field and lands at **file offset 38** (LE u16; byte 38 =
low byte, byte 39 = high byte — 0 in every existing fixture):

```
fmt = struct.pack("<HHIIHHHHI", 0xfffe, 1, RATE, RATE*2, 2, 16, 22, valid, 0x4) + guid
```

File layout this produces (all valid-bits fixtures, 11,588 B total):
`RIFF`@0-3 · size@4-7 · `WAVE`@8-11 · `fmt `@12-15 · fmtSize=40@16-19 ·
fmt@20-59 (tag 0xfffe@20-21, ch=1@22-23, rate@24-27, byteRate@28-31,
blockAlign=2@32-33, bits=16@34-35, cbSize=22@36-37,
**validBits@38-39**, mask=0x4@40-43, GUID@44-59) · `data`@60-63 ·
dataSize@64-67 · payload@68+. So file byte 256 = payload byte 188 =
**sample 94 low byte** — the act-trigger byte is payload content.

Per-family builders (same fmt line; differ only in payload + `valid`
tuple + output round dir):

| builder | lines | emits | byte-256 handling |
|---|---|---|---|
| `build_ui_route_act_r63_probe` | **:192-215** | `live/round-63/pair_route_{84,00}.wav` | **direct `variant[256] = byte` pin (:212-215)** — payload-independent, simplest for a sweep |
| `build_ui_extensible_valid24_probe` | :218-237 | `live/round-62/pair_valid_{24,32}.wav` | deterministic f2 sweep until `values[94]&0xff==0x84` (:226-231; first hit f2=1903) — natural payload keeps 0x84 |
| `build_ui_extensible_valid17_probe` | :240-249 | `live/round-61/pair_valid_{17,16}.wav` | accidental 0x84 (r61 payload, sample 94 = 0x0484) |
| `build_ui_extensible_valid0_probe` | :252-261 | round-60 {0,16} | — |
| `build_ui_extensible_valid13_probe` | :264-274 | round-59 {13,16} | scaled payload `(values*8)` |
| `build_ui_extensible_valid14_probe` | :277-287 | round-58 {14,16} | `(values*4)` |
| `build_ui_extensible_valid_bits_probe` | :290-303 | round-57 {15,16} | clamp/scale payload |
| `RATE` / `OUT` | :11 / :12 | 48,000; `parents[1]/"artifacts"` → builders write `OUT.parent/"live"/round-N/` | — |

Dispatch plumbing: argparse flags tail at **:791-792** (r63 pair);
newest-first `elif` head at **:794-796**
(`if args.probe_ui_route_act_84_r63 or ...: main(); build_…()`). Each
probe branch calls `main()` first (canonical regenerate) then the
builder — a new sweep flag slots in as a new top `elif` + flag line.
`guid` constant: `bytes.fromhex("0100000000001000800000aa00389b71")`
(KSDATAFORMAT_SUBTYPE_PCM), e.g. :208.

**Sweep builder shape (recon observation, not a patch):** one shared
deterministic payload + a `for valid in (...)` loop emitting
`pair_valid_{v}.wav`, plus post-assembly `variant[256] = 0x84` per
variant (r63 technique — keeps every variant byte-identical except
offset 38, unlike the f2 sweep which mutates the payload; either pins
the act route). For values >255 the field's high byte (offset 39) must
also be set; the claimed range ≤48 needs byte 38 only.

## Measurer map — `corpus/fixtures/measure_audio.py` (673 lines)

- `measure()` **:49-95**: ffprobe stream+duration query :51-52;
  `sox <path> -t f32 -e floating-point -` at **:55 — no `-t`, so input
  format is auto-detected** (the load-bearing detail: bridge route is
  exercised only when byte 256 = 0x84, or nothing else pre-empts);
  failure rules :76-87 (`format_failures` :40-46 requires
  pcm_s16le/16-bit → every reclassified codec is a `format:` failure).
- `command()` = `subprocess.run(check=True, capture_output=True)` —
  a SoX exit-2 inside `measure()` propagates → receiptless crash.
  **The r63 block's try/except is the required template for
  codec-unknown sweep values:** :421-437 wraps `measure()` in
  `try/except CalledProcessError` → `{"sox_exit_code", "sox_stderr",
  failures:["decode: default SoX route rejected input"]}` and records
  `sox_detected_format`/`sox_route` (:425-436) — exactly the fields a
  sweep entry wants per value.
- Other measurement blocks for shape: r62 pair :438-442 (plain
  `measure()`), r61 :443-447, r60 :448-452 … all read
  `ROOT/"live"/round-N/pair_valid_{v}.wav` under `SPECS["ui"]`.
- Plumbing for a new mode: flag lines :240-249 (append);
  one-probe mutex `sum(...)` :251-252 (add each flag);
  builder-flag forwarding tail **:341-342** (append);
  `mode=` chain head :643 and `suffix=` chain head :663 (prepend
  newest); receipt path :664 `live/runs/<stamp><suffix>/`.
- **`measure_audio.py` has no `--runs` flag** (r63-baseline +
  r63-verifier both recorded this): receipts always go to tracked
  `corpus/live/runs/`. My `--runs` instruction cannot be honored by the
  runner as-is; sweep runs through it will write there (sibling seats
  share it — timestamp-census attribution, as r63 seats did).

## Routing surface (r62/r63-established, re-spot-checked)

- `act` ⟺ `len≥257 ∧ file[0:4]=="RIFF" ∧ file[256]==0x84` (formats.c:93,
  before the wav rows; knowledge entry
  `corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md`). All 20
  of my r64 variants detected `act`.
- `act` IS the ffmpeg pseudo-handler: popens
  `ffmpeg -loglevel quiet -nostdin -strict -2 -i <f> -f au -`; single
  dispatch, **no fallback**; child stderr/exit-status invisible; empty
  pipe → au `premature EOF` exit 2.
- Forced levers (deterministic, byte-256-independent): `sox -t wav`
  (native; valid>16 → fatal `number of valid bits exceeds the number of
  bits per sample`), `sox -t act` / `sox -t ffmpeg` (bridge).
- **Same-route caveat for the sweep**: `measure()`'s `sox` call has no
  `-t` — through the project runner the bridge is reached ONLY via
  byte-256=0x84; forced `-t` is available for out-of-runner probes.
- Existing pairs re-verified live this round: valid16→pcm_s16le/5,760,
  valid17→pcm_s24le/3,839, valid24→pcm_s24le/3,839,
  valid32→pcm_s32le/2,880; `pair_route_{84,00}.wav` codec pcm_s24le
  (ffprobe route-agnostic; SoX routing is the byte-256 difference).

## Boundary-family pair candidates (for the claim's tracked-pair clause)

Prior-art coverage: {16,17} pair already tracked (round-61),
{24,32} tracked (round-62 — spans but does not pin the 24|25 step).
Measured-adjacent pairs that pin a step exactly:

| pair | class change | SoX outcome | receipt shape |
|---|---|---|---|
| {24,25} | s24le→s32le | 3,839 vs 2,880 | two exit-1 receipts |
| {32,33} | s32le→*none* | 2,880 vs exit-2 | needs the r63 try/except wrap |
| {8,9} | u8→s16le | 11,520 vs 5,760 | two exit-1 receipts |
| {56,57} | *none*→s64le | exit-2 vs 1,440 | one wrap-required side |
| {64,65} | s64le→*none* | 1,440 vs exit-2 | one wrap-required side |
| {0,1} | absent→u8 | 5,760 vs 11,520 | semantics edge pair |

## Facts vs inference vs remaining unknowns

**Facts (measured this round, this host):** the 20-value step table +
packet splits above; sole-diff byte-38 variants; `premature EOF` exit-2
on codec-unknown values; existing-pair codec/decode re-verification;
all cited line numbers read directly from the files at HEAD `37d4c57`.

**Inference (prior-art, not re-derived):** `ceil8(valid)>>3` →
`ff_get_pcm_codec_id` byte-width table (r62-author's
riffdec.c/lavf_utils.c citation — my map is consistent at every
measured point); packet formula interior constants (source-read +
fit-verified at r62, re-fit here on five widths); `measure()` crash is
receiptless *unless* the block wraps (r62-scout established; r63 block
demonstrates the wrap).

**Remaining bounded unknowns:** values 256+ (byte-39 high-byte) untested
— expected `unknown` via the same byte-width law but unmeasured;
whether ffmpeg packetizer behavior differs on *other* payload
sizes/blockAligns was verified only for this 11,520-B/ba-2 family
(r62-author swept both, fit held); interior values inside each band
(2-7, 10-15, 18-23, 26-30, 34-47, 49-55, 58-63) are band-boundary
interpolations — each measured value landed in its predicted band, the
sweep itself is the author's exhaustive pass; SoX/ffmpeg version
dependence (USING_FFMPEG builds only) unchanged from r62/r63 bounds.

## Receipts / artifacts

- `corpus/live/r64-scout/variants/v{0,1,7,8,9,15,16,17,24,25,31,32,33,48,56,57,64,65,128,255}.wav`
  — 20 byte-38 variants of `pair_valid_17.wav` (sole-diff verified).
- `corpus/live/r64-scout/runs/sweep-valid-bits.tsv` — full
  codec/bps/bytes/samples/detection table.
- `corpus/live/r64-scout/runs/variant-shas.txt` — sha256 of
  representative variants.
- Commands verbatim in body; base fixture
  `corpus/live/round-61/pair_valid_17.wav` (sha `15cadf24…` per r62).
