# R64 scribe — wValidBitsPerSample→codec reclassification map (complete step map)

Seat: scribe (report-only documentation draft). Host: devin. Lane axis this
round: **coverage** — map the valid-bits→codec reclassification sweep under
the ffmpeg bridge that r62 disclosed and r63 made deterministic (act
predicate: `RIFF ∧ file[256]==0x84`).

Toolchain on record: `sox: SoX_ng v14.8.0.1`, `ffprobe`/`ffmpeg` n9.0.1,
Python 3.14 (all `/usr/bin`). Scratch under
`.shokunin/audio/corpus/live/r64-scribe/` (`variants/` 85 fixtures,
`gen_sweep.py`, `sweep.sh`, `results.tsv` 85 data rows, `manifest.sha256`,
`logs/` per-file ffprobe/ffmpeg/sox receipts). No tracked file, fixture,
receipt, predicate, or other lane's surface was written; nothing committed.
The project runner was deliberately not invoked — it has no `--runs` flag
(r63-reviewer established this) and would write the shared `live/runs/`;
all evidence is direct tool receipts against scratch variants.

Wave context: this scribe lane ran concurrently with the r64 wave —
sibling reports `r64-{author,critic,reviewer,scout,baseline}.md` and
scratch `corpus/live/r64-{author,baseline,boundary,critic,simplifier}/`
landed in the canonical repo while this sweep executed; the tracked writer
(r64-author) integrated six boundary fixtures + six probe modes mid-round.
Cross-seat consistency is reported verbatim in its own section below.

## Verdict on the declared claim

**ESTABLISHED — the reclassification is a step map, and it is NOT monotonic.**
Exhaustive vb sweep (0–64 plus 65/100/128/200/255) on the r61 fixture family
(16-bit container, payload cloned byte-identical so `file[256]==0x84` holds
on every variant; SoX `-V4` confirms detected=`act` on all 85 files) yields
exactly six step boundaries, all at adjacent vb pairs differing only at
header byte 38:

| vb band | ceil8 byte-width | ffmpeg codec | SoX f32 count (data=11,520 B) |
|---|---|---|---|
| 0 | (defer to container) | pcm_s16le | 5,760 |
| 1–8 | 1 | pcm_u8 | 11,520 |
| 9–16 | 2 | pcm_s16le | 5,760 |
| 17–24 | 3 | pcm_s24le | 3,839 |
| 25–32 | 4 | pcm_s32le | 2,880 |
| 33–56 | 5–7 | **none** (ffprobe `codec_name=unknown`) | 0 — `sox` exit 2 `premature EOF` |
| 57–64 | 8 | pcm_s64le | 1,440 |
| ≥65 (65,100,128,200,255) | — | **none** | 0 — exit 2 `premature EOF` |

Pinned boundaries: **8|9** (u8→s16le), **16|17** (s16le→s24le),
**24|25** (s24le→s32le), **32|33** (s32le→none), **56|57** (none→s64le),
**64|65** (s64le→none). The 33–56 "none" band and the re-entrant s64le band
resolve the r62 seat tension verbatim: r62-scribe's sampled map claimed
"≥33→unknown" (tested 33,40,255 — correct at those points but wrong as an
interval claim) while r62-boundary reported "63-64→s64le" (correct, and now
shown to extend down to 57). Both were locally right; the complete map is
above. ffmpeg exits **234** ("no decoder found") on every none-band file;
SoX exit **2** via the au reader's `premature EOF` — empirically confirming
the r63 knowledge entry's prediction that codec-miss is indistinguishable
from demux failure inside the bridge.

## Mechanism correlation (source-level, ffmpeg n9.0.1 extracted tree at
## `corpus/live/r62-boundary/src/` — lines re-verified by this seat)

- `riffdec.c:67` `parse_waveformatex`: `bps = rl16` (wValidBitsPerSample @
  file offset 38); `if (bps) par->bits_per_coded_sample = bps;` — nonzero
  vb *replaces* coded width; vb==0 keeps the container's. Then
  `codec_tag = AV_RL32(subformat GUID)` (=1 PCM here) →
  `ff_wav_codec_get_id` → `ff_get_pcm_codec_id(bps, flt=0, be=0, sflags=~1)`
  (riffdec.c:285).
- `lavf_utils.c:154` `ff_get_pcm_codec_id`: `bps≤0 || bps>64 → NONE`;
  else `w=(bps+7)>>3`; signed table when `sflags & (1<<(w-1))` — `~1` sets
  every bit except bit 0, so **w=1 lands in the *unsigned* branch → pcm_u8**;
  w∈{2,3,4,8} → s16le/s24le/s32le/s64le; **w∈{5,6,7} → NONE** (no codec).
  This is the entire observed map — the none-band is the missing 5/6/7-byte
  entries, not a rejection rule.
- `wavdec.c:670` post-parse promotion (new coverage finding): `codec_id ==
  PCM_S24LE ∧ block_align == channels·4 ∧ bits_per_coded_sample == 24 →
  PCM_F24LE`. My `vb024_c32` control (32-bit container, block_align=4)
  surfaces it: ffprobe reports **pcm_f24le**, decode 2,880 f32 (4-byte
  unpacking). `vb024_c24` (block_align=3) and `vb024_c16` (block_align=2)
  stay s24le — promotion keys on the *4-byte-aligned-24-bit* shape, not on
  vb alone.
- Packetization (`pcm.c:29` `ff_pcm_default_packet_size`): bitrate recomputed
  from the *codec* (`bits·rate·ch`), chunk =
  `block_align · 2^⌊log2(bitrate/80/block_align)⌋` keyed on the **container**
  nBlockAlign. Measured chunk sizes: u8→4,096; s16le/s24le→8,192;
  s32le/s64le→≥16,384 (single packet at this data size); c24 container
  (block_align 3)→12,288.

## Bit-depth-vs-valid-bits attribution (dispatch's conditional — now shown)

Within the `wFormatTag==0xFFFE ∧ cbSize≥22 ∧ PCM-subtype-GUID` family,
codec choice is a pure function of vb whenever vb≠0; the container width is
never consulted for the codec (the sflags/int-vs-float branch is tag-driven,
and the f24le promotion is a block_align shape test). Sibling critic shows
the claim fails outside that family — vb is ignored entirely on
non-extensible tags — see Cross-seat. Controls, all act-detected, same
payload:

| control | codec | packets | SoX f32 | attribution shown |
|---|---|---|---:|---|
| vb017_c16 | pcm_s24le | 8192+3328 | 3,839 | vb 17 > container 16 → widen up |
| vb017_c24 | pcm_s24le | 11520 | **3,840** | same vb on block_align 3 → lossless |
| vb017_c32 | pcm_s24le | 8192+3328 | 3,839 | vb 17 < container 32 → narrow down |
| vb008_c24 | pcm_u8 | 3072×3+2304 | 11,520 | vb 8 < container 24 → u8 |
| vb016_c32 | pcm_s16le | 8192+3328 | 5,760 | vb 16 < container 32 → s16le |
| vb024_c32 | **pcm_f24le** | 11520 | 2,880 | promotion (block_align 4 shape) |
| vb024_c24 | pcm_s24le | 11520 | 3,840 | promotion NOT triggered (align 3) |
| vb056_c24 | none | 11520 | 0 (exit 2) | none-band is vb-keyed, not container |
| vb057_c32 / vb064_c32 / vb064_c24 | pcm_s64le | 11520 | 1,440 | s64le band container-independent |
| vb000_c16/c24/c32 | s16le/s24le/s32le | per container | 5,760/3,840/2,880 | vb==0 → defer to container |
| vb255_c32 | none | 11520 | 0 (exit 2) | ≥65 none, container-independent |

Two consequences worth the corpus record: (1) `vb017_c24` is the first
member of the valid17 family to decode its **nominal** count (3,840) — the
3,839 residue is a container-block_align × codec-width interaction, not a
property of the codec or the header; (2) the same vb value (24) produces
three different negotiated codecs/counts across container alignments
(s24le/3,839; s24le/3,840; f24le/2,880).

## Interaction with act routing (all 85 rows)

Every variant carries the r61 payload verbatim ⇒ `file[256]==0x84` ⇒ SoX
`-V4` reports ``detected file format type `act' `` on **all 85** (asserted in
`gen_sweep.py`; `sox_detect` column uniform). Codec-bearing rows show
`sox --i` `Input File … (ffmpeg)`; none-band rows show `sox` exit 2
`can't open input file …: premature EOF` — the bridge's ffmpeg child dies
silently and the au reader sees empty stdout, exactly the failure
indistinguishability the r63 entry predicted. `sox --i` on codec rows still
prints `Precision: 16-bit` (container display quirk, r62-known) — e.g.
vb057 prints 16-bit while decoding s64le→1,440 f32.

## Boundary-family pair (dispatch: land iff a step boundary is established)

Six boundaries established ⇒ pair condition met. **Already landed by the
tracked writer**: `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav`
(three straddling pairs: u8|s16le, s24le|s32le, none|s64le) plus six probe
modes `--probe-ui-extensible-valid-{8,9,24,25,56,57}-r64` in the author's
92-command ledger (44 exit0 / 48 exit1). My independently built candidates
(`variants/vb056_c16.wav` `17739018…`, `variants/vb057_c16.wav`
`7c4ef14b…`) differ in bytes from the landed pair (`d4ee4431…`,
`aa520464…` — author generated its own payload family), but the landed
pair re-verifies identically under my probes: byte 256 = `0x84` on both,
sole diff at offset 39 (`cmp -l`: `39  70  71`), valid56 → `unknown` /
SoX exit 2 / 0 bytes, valid57 → `pcm_s64le` / 5,760 f32 bytes = 1,440
samples. No conflict between the two constructions.

## Draft: `corpus/knowledge/2026-10-13-sox-validbits-codec-map.md` (content for parent decision — not landed)

```markdown
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
```

## Draft: LOG.md round-64 entry text (for parent integration)

```markdown
## Round 64 scribe — valid-bits→codec step map established (coverage)
- `reports/round-64/r64-scribe.md`: independent 85-variant sweep (vb 0–64
  exhaustive + 65/100/128/200/255; c24/c32 attribution controls) on the
  r61 fixture family under the r63-pinned act route (all variants
  act-detected, `file[256]==0x84` asserted per file). Step map is exact
  and **non-monotonic**: 1–8→u8, 9–16→s16le, 17–24→s24le, 25–32→s32le,
  **33–56→none**, **57–64→s64le**, ≥65→none; boundaries pinned at
  adjacent sole-byte-38 pairs 8|9, 16|17, 24|25, 32|33, 56|57, 64|65.
  SoX counts follow the r62 packet law per codec width (u8 11,520; s16le
  5,760; s24le 3,839; s32le 2,880; s64le 1,440; none → SoX exit 2
  `premature EOF` — empirically confirming the bridge's
  no-fallback/codec-miss-indistinguishable claim).
- Attribution controls: codec keyed on vb alone when vb≠0 inside the
  extensible-PCM family (17→s24le on c16/c24/c32; 8→u8 inside c24;
  16→s16le inside c32; vb0→container). New coverage finding: wavdec's
  `s24le ∧ block_align==4·ch ∧ bpcs==24 → pcm_f24le` promotion
  (vb024_c32), plus vb017_c24 = first lossless (3,840) valid17-family
  decode — the 3,839 residue is a container-alignment × codec-width
  interaction, not a codec property. Resolves r62's scribe("≥33→unknown")
  vs boundary("63–64→s64le") tension: both locally correct; the s64le
  band starts at 57.
- Author landed `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav`
  + six `--probe-ui-extensible-valid-*-r64` modes (92-cmd ledger);
  scribe re-verified the 56|57 pair independently (sole byte-38 diff,
  byte256=0x84, unknown→s64le, 0 vs 1,440 samples). Gate outcomes per
  author's receipts: valid-9 exit0 clean; valid-8/24 exit1 4-gate;
  valid-25 exit1 format+duration; valid-56 exit1 receipted `decode:
  default SoX route rejected input`; valid-57 exit1
  format+duration+spectrum.
- Drafts supplied for parent decision: knowledge entry
  `2026-10-13-sox-validbits-codec-map.md`. Scribe wrote only
  `reports/round-64/r64-scribe.md` + `corpus/live/r64-scribe/` scratch;
  no commits, no runner, no other lanes' surfaces.
```

## Commands / observed outputs (receipt excerpts; full receipts in `corpus/live/r64-scribe/`)

- `python3 gen_sweep.py` → 85 variants cloned from
  `corpus/live/round-61/pair_valid_17.wav` (sha256
  `15cadf24…3fe4`, matches r61 record); sole header edits byte 38:40 (vb)
  and, for c24/c32 controls, bytes 28–35 (byte-rate/block-align/bits);
  `assert payload[188]==0x84` on every file.
- `bash sweep.sh` → `results.tsv` 85 rows. Per row: ffprobe
  codec_name/bits_per_raw_sample/duration, ffprobe packet sizes,
  `ffmpeg -v warning -i F -f f32le -acodec pcm_f32le -` byte count + exit +
  `Invalid PCM packet` stderr count, `sox -V4 F -n stat` detected type,
  `sox F -t f32 -` byte count + exit, `sox --i` `(ffmpeg)` tag.
- Spot verbatim: `cmp -l variants/vb056_c16.wav variants/vb057_c16.wav` →
  `39  70  71` (sole diff, offset 38 zero-based, 0x38 vs 0x39).
  `logs/soxdec_vb033_c16.err` = `sox FAIL formats: can't open input file
  '...': premature EOF`. `logs/ff_vb017_c16.err` = two `Invalid PCM
  packet` lines (sizes 2,1). `logs/sox_vb057_c16.log` = `detected file
  format type \`act'`; `sox --i` → `(ffmpeg)` + `Precision: 16-bit` while
  ffprobe says `codec_name=pcm_s64le`.
- Sanity greps: `awk` pivots on the final results.tsv (85 data rows) —
  detect=act 85/85; codec histogram u8:10, s16le:10, s24le:12, s32le:10,
  s64le:11, f24le:1, unknown:31; every `unknown` row has sox_f32=0 ∧
  sox_exit=2 ∧ ffmpeg_exit=234.

## Eliminated hypotheses

- "≥33 → unknown" (r62-scribe's sampled phrasing) — FALSIFIED as an
  interval claim: 57–64 → pcm_s64le re-enters the table.
- "container bits participates in codec choice" — ELIMINATED for vb≠0 by
  the c24/c32 controls (pure vb keying; only the f24le shape-promotion and
  packetization touch container fields).
- "count law needs re-derivation per codec" — REDUCED to the general law:
  observed counts = Σ floor(pkt/w) for every codec width, chunk size from
  container block_align × codec bitrate; vb017_c24's lossless 3,840
  confirms the residue is alignment-keyed.
- "vb sweep might hit the wav reader instead of ffmpeg" — impossible under
  this payload: 85/85 act-detected; no wav-route observations this round.
  (Author's `-t wav` forced-native column shows the native reader's own
  verdict: accept vb≤16, fatal reject vb≥17.)

## Retained bounded UNKNOWNs

- vb 66–99 / 101–127 / 129–199 interior on *scribe's* fixtures (source
  rule says none; sampled points only). r64-author reports full u16 range
  coverage — left to verifier cross-check.
- The `flt=1` (IEEE-float subtype GUID) branch: ff_get_pcm_codec_id
  returns f32le/f64le only for bps 32/64 — unexercised here (PCM subtype
  throughout); critic's tag sweeps partially cover non-PCM territory.
- Project-runner gate outcomes per vb value beyond the six landed probe
  modes: not re-run by scribe (runner has no --runs; would write shared
  `live/runs/`). Author's ledger receipts show: valid-8 → exit1 4-gate;
  valid-9 → **exit0 clean** (native and bridge agree at 5,760 — only the
  codec name stepped); valid-24 → exit1 4-gate; valid-25 → exit1
  format+duration only; valid-56 (codec-none) → exit1 with failure entry
  `decode: default SoX route rejected input` — a receipted failure, not a
  receiptless crash; valid-57 → exit1 format+duration+spectrum.
- Whether SoX's au intermediary transcodes any of these widths (counts
  match ffmpeg's exactly for all classes; sample VALUES not diffed except
  spot class — the r62 known deltas via 16-bit au tagging apply here too).

## Cross-seat consistency (conflicts verbatim — one resolved, one scoped)

- vs `reports/round-64/r64-author.md` (74-variant sweep, tracked writer):
  **fully convergent** on the step map — identical bands and counts
  (their table adds a native `-t wav` column: accept for vb≤16, reject
  exit 2 for vb≥17 — consistent: vb>container is what SoX's native reader
  fatally rejects). Author pins a seventh boundary **0|1**
  (reclassification on/off) that my band table folds into the vb=0 row.
  Their ≥65 claim spans the full u16 field to 65,535; scribe's sweep tops
  at 255 — no conflict, wider coverage is theirs.
- vs `reports/round-64/r64-critic.md`: critic **falsified the universal
  phrasing** "the codec is a pure function of valid-bits" — at fixed
  valid=17 the outcome varies with codec tag (0x0001 non-extensible →
  s16le, vb becomes extradata; 0x0006 → alaw …). Scribe's claim is scoped
  to the `0xFFFE ∧ cbSize≥22 ∧ PCM-GUID` family and stands inside it;
  the knowledge draft carries the precondition verbatim. Critic also shows
  vb==0 defers to *any* declared width (decl57/v0→s64le), generalizing my
  c24/c32 fallback controls.
- vs `reports/round-64/r64-scout.md`: independent sampled re-measurement
  of the same six boundaries — convergent.
- `reports/round-64/r64-baseline.md`: r63 committed-ledger replay 84/86
  byte-identical (two divergences = the known absolute-path receipts);
  pre-state `37d4c57` intact.
- `reports/round-64/r64-reviewer.md`: r63 artifact checks pass; notes
  `corpus/live/r63-boundary/` lacks `src/` on disk (pruned, never
  tracked). Scribe's mechanism citations point at `corpus/live/
  r62-boundary/src/` which **is** on disk — verified by direct reads of
  `riffdec.c` (:67, :285), `lavf_utils.c` (:154), `wavdec.c` (:670),
  `pcm.c` (:29) this round.
- vs `reports/round-62/r62-scribe.md` line ~31: "33, 40, 255 → codec_name=
  unknown …" — observed-correct; its draft phrasing "…, ≥33→codec
  unknown" is falsified by vb 57–64 → s64le.
- vs `reports/round-62/r62-boundary.md` line 127: "33-40->codec NONE …
  63-64->s64le/1,440; 65,255->NONE" — confirmed and completed: NONE band
  is exactly 33–56, s64le band exactly 57–64.
- `corpus/knowledge/2026-10-13-sox-ffmpeg-packet-residue.md` "17–24 →
  s24le/3B, 25–32 → s32le/4B, …" — consistent; this round replaces the
  ellipsis with the exact table.
- No contradicting measurement observed anywhere in the sweep.

## Out of scope (not performed)

No landing of the knowledge entry or LOG text (drafts above, parent's
call); no tracked fixture writes by this seat (the landed `round-64/`
pairs + ledger receipts are the author's; scribe's candidate variants stay
in `corpus/live/r64-scribe/` scratch); no probe-flag/runner invocation
(no `--runs` flag; shared `live/runs/` untouched by scribe); no edits to
fixtures, predicates, thresholds, SCORECARD, SHONEN, or other lanes'
surfaces; no git/network action.
