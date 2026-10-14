# R64 author — valid-bits→codec reclassification STEP MAP pinned (74-variant sweep + 3 boundary pairs)

host: devin (same lane as R61/R62/R63)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `37d4c57`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — declared claim CONFIRMED: the reclassification is an exact step map

R62 decomposed the mechanism (`wValidBitsPerSample` nonzero → `bits_per_coded_sample` →
`ff_get_pcm_codec_id` maps byte-width `w=(V+7)>>3` to a PCM codec; decode count =
Σ floor(pktᵢ/w) over bitrate-scaled packets). R63 pinned the route predicate
(RIFF@0 ∧ file[256]==0x84 → `act` → ffmpeg bridge). R64's declared coverage move:
sweep V over a controlled range under the SAME act-forced route and pin every step
boundary. The step map is **established and exhaustive**, not near/approximate.

## Sweep (scratch: `corpus/live/r64-author/`)

Generator/prober `gen_sweep.py`; **74 variants** — V ∈ {0..66} exhaustively plus
{72, 96, 128, 255, 1024, 32768, 65535} probing the u16 field's far tail. Every
variant is the r61-family header (WAVE_FORMAT_EXTENSIBLE mono 48k, fmt40, bits 16,
block_align 2, mask 0x4, PCM GUID) over ONE shared 11,520-byte payload, file[256]
pinned to 0x84 by assignment — variants differ ONLY at bytes 38–39
(wValidBitsPerSample). Full rows in `results.tsv` (header + 74 rows) and
`results.json`; **74/74 match the predicted law, zero mismatches**.

Per variant three probes: (a) `ffprobe -show_entries stream=codec_name,bits_per_sample
:format=duration` (negotiated codec), (b) default-route `sox -V6 <f> -n stat`
(detected format, `(ffmpeg)` tag, `Samples read`, exit) — the act-forced bridge leg —
plus `sox -t ffmpeg` forced for comparison, (c) `sox -t wav <f> -n stat` forced native.

### The measured step map

| V | w=(V+7)>>3 | ffprobe codec | bps | bridge samples | packets (ffprobe) | native `-t wav` |
|---|---|---|---|---:|---|---|
| 0 | — (no reclassify) | pcm_s16le | 16 | 5,760 | [8192,3328] | accept, 5,760 |
| 1–8 | 1 | pcm_u8 | 8 | 11,520 | [4096,4096,3328] | accept, 5,760 |
| 9–16 | 2 | pcm_s16le | 16 | 5,760 | [8192,3328] | accept, 5,760 |
| 17–24 | 3 | pcm_s24le | 24 | 3,839 | [8192,3328] | **reject** exit 2 |
| 25–32 | 4 | pcm_s32le | 32 | 2,880 | [11520] | reject exit 2 |
| 33–56 | 5,6,7 | **NONE** | 0 | — exit 2 `premature EOF` | demuxer still cuts [8192,3328] | reject exit 2 |
| 57–64 | 8 | pcm_s64le | 64 | 1,440 | [11520] | reject exit 2 |
| ≥65 (incl. 128..65535) | — | **NONE** | 0 | — exit 2 | [8192,3328] | reject exit 2 |

Sample counts obey r62's law exactly at every width: e.g. w=1 →
⌊4096/1⌋+⌊4096/1⌋+⌊3328/1⌋ = 11,520; w=3 → 2,730+1,109 = 3,839 (the 2B+1B
packet-tail residues); w=8 → ⌊11520/8⌋ = 1,440.

### All seven boundaries pinned

- **0|1** — reclassification on/off: V=0 leaves the declared 16-bit codec
  (pcm_s16le, 5,760); V=1 already reclassifies to pcm_u8 (11,520).
- **8|9** — w1→w2: pcm_u8→pcm_s16le; bridge count halves 11,520→5,760. The only
  boundary where BOTH members still decode natively (both 5,760) — the step is a
  pure bridge phenomenon here.
- **16|17** — w2→w3: s16le→s24le (5,760→3,839); coincides with the native
  accept→reject flip (`number of valid bits exceeds the number of bits per
  sample`). Already pinned by the r61 tracked pair.
- **24|25** — w3→w4: s24le→s32le (3,839→2,880); tight straddle (r62's tracked
  pair was the loose 24|32).
- **32|33** — w4→dead band: s32le→NONE; bridge exits 2 (`can't open input file
  ...: premature EOF`), the `(ffmpeg)` tag never prints since startread fails.
- **56|57** — dead→w8: NONE→pcm_s64le; the map is NON-monotone — the codec
  returns after a 24-value dead band.
- **64|65** — w8→dead for the entire rest of the u16 field (65..65535 all NONE).

### Secondary observations (recorded, mechanism attributed)

- Dead-band files still carry `n_streams=1` in ffprobe (`{bits_per_sample: 0}`,
  no `codec_name` key) and the demuxer still packetizes at the DECLARED-rate basis
  ([8192,3328] = the 768 kbps/mp-8192 shape, not the w-scaled shape) — the
  boundary there is codec absence at stream setup, not a packetization failure.
- Forced `-t ffmpeg` and act-autodetected routes agree on every row (br_n ==
  ff_n all 74) — autodetect and handler are cleanly separable, route uniform.
- Native `-t wav` leg has exactly one boundary: accept iff V ≤ declared 16
  (V=0 included), decode 5,760; reject V ≥ 17, exit 2. The bridge's 7-boundary
  map is invisible to the native reader — the reclassification IS a bridge
  phenomenon.
- Band-interior decode identity measured directly: `cmp` of `sox -t f32` streams
  — {1,5,8} identical, {9,12,16} identical, {17,20,24} identical, {25,32}
  identical, {57,64} identical; boundary pairs 8|9, 16|17, 24|25 DIFFER. The
  decoded output depends on w alone within a band.

### Eliminated hypotheses

- "Monotone degradation with V" — falsified twice: 1–8 yields MORE samples than
  9–16, and the dead band (33–56) is followed by a live s64le island (57–64).
- "Native reader shares the step boundaries" — falsified: native splits only at
  16|17 (the `valid > bits` check); within 0–16 it is constant.
- "The u8 class is a PCM16 fallback or s8" — falsified: codec is pcm_u8 (bps 8),
  a genuine unsigned-width-1 decode of all 11,520 bytes.
- "V>64 clamps to s64le or wraps" — falsified: 65, 128, 255, 1024, 32768, 65535
  all land in NONE with the same premature-EOF failure.
- "valid=0 reclassifies to w0/none" — falsified: V=0 is the off-switch
  (nonzero-only overwrite); codec stays pcm_s16le.

## Tracked changes (additive only; `format_failures`, `SPECS["ui"]`, thresholds, all prior modes untouched)

`corpus/fixtures/build_artifacts.py` **+36/−1**: `build_ui_validbits_steps_r64_probe()`
emits `corpus/live/round-64/pair_valid_{8,9,24,25,56,57}.wav` — the r61-family
header over one shared deterministic payload (`0.25·sin 920 + 0.10·sin 1380`
×8191, 5,760 frames), file[256] pinned 0x84 by assignment (r63 convention).
Six argparse flags + newest-first dispatch branch. The three pairs straddle three
different boundary families: {8,9} u8|s16le, {24,25} s24le|s32le, {56,57}
none|s64le — with r61's existing 16|17 pair the contiguous w1|w2|w3|w4 ladder is
fully pinned plus the dead-band→s64le edge.

`corpus/fixtures/measure_audio.py` **+56/−4**: six flags
(`--probe-ui-extensible-valid-{8,9,24,25,56,57}-r64`), mutual-exclusion sum,
builder-flag forwarding, one measurement block (r63 pattern extended: per member
it records `valid_bits`, `sox_detected_format`, `sox_route`, bridge
`sox_stat_exit_code`/`sox_stat_samples_read`, and the native `-t wav` leg
`sox_native_exit_code`/`sox_native_samples_read`/`sox_native_stderr`; decode
rejects get the CalledProcessError entry), and the `mode`/`suffix` chain heads
prepended newest-first.

Pair byte evidence: all six 11,588 B; `cmp -l` between any two members → **only
1-based offset 39 differs** (file byte 38, the valid-bits low byte; all V ≤ 57
so the high byte is 0 throughout). SHA-256: v8 `bc9878f789fd26e2685dbf5a4ed2255b94c1bdf07c4e4bd317da4fc3d00a1927`,
v9 `02887d11d7eb3779a55e5bc3e75e0e1800dc94233785e8d84afb760303827378`,
v24 `714998b8be1aa48c36eace1039d6dc6e13afdd374e6b1c1a1f2c925079d0bb64`,
v25 `614845eb5e77b0acd8dcc9ef34b3bc0bb57f0ca6bc8b8d7d213d2cb3987eb91c`,
v56 `d4ee4431ac2ede1e7ee544f03dc2dd1da1803fa968cfb46a44bc91ae5c2af681`,
v57 `aa520464e608859c81ad4dd5f9f0771330a3a98434d4b8a7bd2749993b39fd94`.
Builder re-run is deterministic (each of 7+ mode runs rewrote identical bytes;
receipts byte-identical across independent runs — shown for v56 and v9).

## What ran — 92-command ledger (86 prior verbatim + 6 new modes at positions 2–7)

All commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/measurements.json`.
Runner `corpus/live/r64-author/run_ledger.py`; full TSV
`corpus/live/r64-author/ledger-r64.tsv`. Totals: **44 exit 0 / 48 exit 1**
(r63's 43/43 plus the new pair: one exit-0 member v9, five exit-1).

Prior-86 replay (my rows {1}∪{8..92} vs r63 rows 1..86): exit sequence
**position-identical**, failure summaries **verbatim identical**, and all 86
receipts **byte-identical** to the original r63 receipt files (compared
file-by-file against the paths in `corpus/live/r64-reviewer/r63-receipt-paths.txt`
— sibling-recorded originals, all present).

New-mode receipts (ledger run):
- `--probe-ui-extensible-valid-8-r64` → exit 1,
  `runs/20261014T003915864930Z-ui-extensible-valid-8-r64/measurements.json`;
  `ui_extensible_valid_8_r64_probe`: format/duration/level/spectrum 4-gate;
  entry records codec `pcm_u8`/8, bridge `sox_stat_samples_read` 11,520,
  native 5,760 exit 0, `sox_detected_format: "act"`, `sox_route: "ffmpeg"`.
- `--probe-ui-extensible-valid-9-r64` → **exit 0**,
  `runs/20261014T003916973423Z-ui-extensible-valid-9-r64/measurements.json`;
  zero failures — pcm_s16le/16, bridge 5,760, native 5,760. The pair's
  discriminating wrinkle: both members native-decode identically; only the
  bridge reveals the step (and only v8 fails the gates).
- `--probe-ui-extensible-valid-24-r64` → exit 1,
  `runs/20261014T003918093987Z-ui-extensible-valid-24-r64/measurements.json`;
  pcm_s24le/24, bridge 3,839, native reject; 4-gate.
- `--probe-ui-extensible-valid-25-r64` → exit 1,
  `runs/20261014T003919213741Z-ui-extensible-valid-25-r64/measurements.json`;
  pcm_s32le/32, bridge 2,880, native reject; format+duration only (decodes
  inside level/centroid bands — discriminates within failure classes).
- `--probe-ui-extensible-valid-56-r64` → exit 1,
  `runs/20261014T003920303644Z-ui-extensible-valid-56-r64/measurements.json`;
  decode-failure entry: `decode: default SoX route rejected input`,
  `sox_exit_code: 2`, stderr `can't open input file ...: premature EOF`;
  detected `act`, route `ffmpeg`, native exit 2 with the verbatim
  valid-bits-exceeds line.
- `--probe-ui-extensible-valid-57-r64` → exit 1,
  `runs/20261014T003921431256Z-ui-extensible-valid-57-r64/measurements.json`;
  pcm_s64le/64, bridge 1,440, native reject; format+duration+spectrum.
- Normal-run receipt `20261014T003914751250Z-normal/measurements.json` is
  byte-identical to r63's normal receipt `20261013T234232472196Z-normal`.

Setup notes: `python3 -m py_compile` on gen_sweep.py + both fixture scripts →
exit 0; `git diff --check` → clean. Two tracked `__pycache__/*.pyc` binaries
differ — mechanical `py_compile` regeneration churn, same disclosure as
r62/r63; parent decides. No `lsp` device is exposed on this substrate, so the
symbol-adjacent edits (newest-first chain heads, exclusion sum) were applied by
hand against read file text — recorded per the fallback rule.

**Found-and-restored (sibling damage, not mine):** the tracked scratch file
`corpus/live/r63-author/ledger-r63.tsv` was clobbered in the working tree by a
wrong-cwd re-run of `r63-author/run_ledger.py` (absolute TSV path always writes
there; relative MEASURE path fails outside the worktree → 86 rows of
exit-2 `UNPARSED … Errno 2`). I preserved the observed clobber at
`corpus/live/r64-author/r63-ledger-clobbered-observed.tsv` and restored the file
to HEAD via `git checkout` — the committed bytes are r63's landed evidence and
are what my byte-identical receipt comparison is checked against. Flagging for
the parent in case a sibling wants the audit trail instead.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **expansion**: the bridge's valid-bits behavior went from 4 known points to a
  74-variant exhaustive map over the full effective range — every width class
  (1,2,3,4,8), the dead band, and the >64 tail — plus seven pinned boundaries,
  three legs per variant (negotiated codec, bridge count, native outcome), and
  packet-level intermediates (`-show_packets`) per width.
- **quality**: zero mismatches against the composed law on all 74 rows; matched
  pairs differ only at the valid-bits field; receipts deterministic across
  reruns; band-interior byte-identity and dead-band packetization verified
  directly rather than assumed.
- **discernment**: boundary pairs chosen where the signal is sharpest — {8,9}
  isolates the unsigned special case AND shows a boundary invisible to the
  native reader (its one passing member proves the step is route-dependent, not
  payload-dependent); {24,25} tightens r62's loose 24|32 straddle; {56,57} pins
  the non-monotone dead-band→s64le return. Eliminated-hypothesis list kept
  explicit rather than implied.

## Conditional replay shape (for the non-author verifier)

92 commands = the r63 86 verbatim with the six `--probe-ui-extensible-valid-*-r64`
flags inserted newest-first at positions 2–7 (TSV order in `ledger-r64.tsv`).
Expected 44 exit 0 / 48 exit 1; prior-86 receipts byte-identical to r63's;
new receipts deterministic (v56 and v9 independently re-produced identical JSON).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 + ffmpeg n9.0.1; the `act` row is
  `#if USING_FFMPEG` — ffmpeg-less builds never take the bridge.
- Exhaustiveness is over THIS file family (11,588-B WAVE_FORMAT_EXTENSIBLE,
  mono 48k, block_align 2, 11,520-B data). Other rates/alignments share the row
  semantics by construction, but only this shape was swept; packet boundaries
  are data-size-dependent (r62's packet law), so other shapes would land
  different counts inside the same codec map.
- The dead band's demuxer packetization basis (declared bits vs byte_rate) is
  unresolved between two numerically identical candidates on this fixture —
  recorded, not decided.
- Interior non-boundary sub-bands are inferred uniform from w-only dependence +
  byte-identity spot checks ({1,5,8}, {9,12,16}, {17,20,24}, {25,32}, {57,64});
  the TSV covers every V in 0..66 anyway.
- No standards-conformance, fidelity, audibility, production, rights, engine, or
  promotion claim — local fixture measurements on deliberately varied headers.

## Blockers

None. One `ufo-labrat` probe dispatched (band-invariance hypothesis); it ran
exec-less and confirmed structurally from the fixture construction + recorded
run data; the byte-identity leg it proposed was then executed by this seat
directly (results above). No commit/push/merge performed; parent integrates.
