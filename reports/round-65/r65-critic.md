# R65 critic — attack the pre-act preemptor ordering claim on RIFF files

Seat: critic. Target: the r65 declared move (pre-act CHECK ordering: `gsrt`
`ring.bin\0`@16-24, `hcom` `FSSD`@65∧`HCOM`@128 vs `act` `RIFF`@0∧`0x84`@256 vs
`wav`). Host: SoX_ng 14.8.0.1 (`/usr/bin/sox`), ffmpeg/ffprobe n9.0.1, strace.
Worktree `~/Projects/prymeagnt/audio`; all artifacts under
`corpus/live/r65-critic/` (`gen.py` 33-variant generator, `probe.sh`,
`results.tsv`, `var/` exhibits, `shas.txt`). No tracked files touched; no
commits.

**Author-landing status**: the tracked controls landed during this review
(uncommitted working-tree state — leaf seats don't commit):
`corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` +
`corpus/fixtures/{build_artifacts,measure_audio}.py` diffs (+41/+65 lines,
four `--probe-ui-preempt-*-r65` flags). Verified below; author's scratch
matrix `corpus/live/r65-author/results.tsv` (19 rows) and scout's
`r65-scout.md` (20 probes) cross-checked — three independent constructions
agree on every shared case.

## Verdict

**The ordering claim SURVIVES every attack: measured order is `gsrt` < `hcom`
< `act` < `wav`, first-match-wins.** No preemptor-shaped file routed `act` on
any of my 33 variants, the author's 19, or scout's 20 — the falsification fork
did not trigger.

**But two companion claims are FALSIFIED, and one mechanism attribution in the
round's evidence is wrong:**

1. *"A preemptor-detected file fails in its reader"* — **false.** My
   `D1_hcomdecode+act.wav` (RIFF+WAVE+`FSSD`@65+`HCOM`@128+`0x84`@256, valid
   hcom header chain) is detected `hcom` and **fully decodes 9 samples @22050
   Hz through the native hcom reader** (exit 0, `--i` prints `(hcom)` / `8-bit
   HCOM`). Scout's report left this open ("whether *any* RIFF file can survive
   hcom startread is open") — it can. Same file decodes 278 samples as PCM16
   wav under forced `-t wav`: one byte-stream, three working readers.
2. *"The terminal error attributes the reader"* — **false.** The bare string
   `premature EOF` is produced by **three different readers** on this file
   family (gsrt checksum loop, au reader on an empty ffmpeg pipe, and — as the
   longer `premature EOF on input file` — the wav reader's non-fatal WARN).
   On the *same file* `A5_gsrt+act.wav`, autodetect (`gsrt`) and forced
   `-t act` emit byte-identical `premature EOF`; only the `-V6` detection line
   or an execve count distinguishes them.
3. *Mechanism correction*: the gsrt `premature EOF` on RIFF files is **not**
   the "fixed ring.bin header read running out" (r65-scout's inference). It is
   the reader's **checksum loop**: bytes 0-3 are read as a big-endian
   `file_size`; `RIFF` = 1,380,533,830 → the loop tries to read
   `file_size−2` ≈ 1.38 G int16s and hits real EOF. Proven three ways below —
   a non-seekable fd skips the loop entirely and the same bytes decode.

## Attack 1 — double/triple collision: which single reader wins

| file (600 B unless noted) | signatures present | detected | outcome |
|---|---|---|---|
| `A1_gsrt+hcom+act.wav` | gsrt@16-24, FSSD@65, HCOM@128, 0x84@256, RIFF+WAVE | **gsrt** | `premature EOF`, exit 2, **0 child execve** (strace) |
| `A2_gsrtNoNUL+hcom+act.wav` | `ring.binX`@16-24 (NUL broken), hcom, act | **hcom** | `bad compression type`, exit 2 |
| `A3_gsrt+FSSDonly+act.wav` | gsrt, FSSD only, act | gsrt | `premature EOF`, exit 2 |
| `A4_hcom+act.wav` | hcom, act | hcom | `bad compression type`, exit 2 |
| `A5_gsrt+act.wav` | gsrt, act | gsrt | `premature EOF`, exit 2 |
| `A6_FSSDonly+act.wav` | FSSD@65 only, act | act | `(ffmpeg)`, 278 samples, exit 0 |
| `A7_HCOMonly+act.wav` | HCOM@128 only, act | act | `(ffmpeg)`, 278 samples, exit 0 |
| `A8_act_only.wav` | act only | act | `(ffmpeg)`, 278 samples, exit 0 |

`E7_triple_bothdecodable.wav` adds the sharpest fork — one file satisfying all
three predicates *and* decodable by two of the readers:

| route on the same 600 bytes | result |
|---|---|
| autodetect, regular file | `gsrt` → `premature EOF`, exit 2 |
| autodetect, stdin (`cat f \| sox - -n stat`) | `gsrt` → **88 samples**, 8 kHz u-law, exit 0 |
| `-t hcom` | **9 samples** @22050, exit 0 |
| `-t act` | `(ffmpeg)` bridge → ffmpeg's *hcom* demuxer → **3,520 samples**, exit 0 |
| `-t wav` | `file encoding 0x622e … not supported`, exit 2 |
| `-t gsrt` | `premature EOF`, exit 2 |
| ffprobe | `hcom` 22050 |

Naive attribution "the strongest signature's reader runs" survives ordering but
nothing else: detection picks gsrt; *which bytes get consumed* depends on the
fd and on forcing flags, and ffmpeg's own probe re-runs the contest (hcom
wins inside ffmpeg where sox picked gsrt).

## Attack 2 — preemptor fires, its reader rejects: fallthrough or fatal?

Fatal, terminal — confirmed on fresh constructions: `A4`→`bad compression
type`, `A5`→`premature EOF`, both exit 2, **no fallthrough** to act/wav (no
second detection line; strace shows zero execve on native routes vs the ffmpeg
child on act). Consistent with r63's single-dispatch model. New precision:

- hcom's reader walks fields in a fixed order — FSSD@65 → HCOM@128 →
  compresstype@140 ≤1 → divisor@144 ∈1..4 → dictsize@148 ∈1..511 → dictionary →
  data. Error strings mark the stop position: my `A4` dies at
  `bad compression type` (payload byte @140 made it >1); author's `m_hcom`
  (zeroed fields) gets one step further → `bad sampling rate divisor`; my `D1`
  passes all checks and decodes. `Mac header type is not FSSD` /
  `Mac data fork is not HCOM` are unreachable via autodetect (the CHECK
  guarantees both signatures) — observed only under forced `-t hcom`.
- A gsrt-detected RIFF file can **never** pass startread on a seekable fd:
  `RIFF`@0 = file_size 1.38 G → checksum loop needs ≈2.7 GB → EOF, always.
  The reader's id check (`ring.bin` @16, 8-byte memcmp — *weaker* than the
  detector's 9-byte row) is never reached on RIFF collisions.
- `-t gsrt` on a plain wav (`A8`) reproduces the same `premature EOF` —
  checksum again, not id: RIFF@0 drives it either way.

## Attack 3 — preemptor WITHOUT the act byte: is the preemptor self-consistent?

Yes — and it masks `wav` too, which is the part a naive reading misses:

| file | byte256 | detected | expected-by-naive-reading | outcome |
|---|---|---|---|---|
| `B_gsrt_00.wav` | 0x00 | **gsrt** (not wav!) | wav | `premature EOF`, exit 2 |
| `B_gsrt_41.wav` | 0x41 | gsrt | wav | `premature EOF` |
| `B_hcom_00.wav` | 0x00 | **hcom** | wav | `bad compression type` |
| `B_hcom_41/83/85.wav` | 0x41/0x83/0x85 | hcom | wav | `bad compression type` |
| `B_gsrt+hcom_00.wav` | 0x00 | gsrt | wav | `premature EOF` |

The preemptor rows are self-sufficient — `ring.bin\0`@16 or `FSSD`@65∧`HCOM`@128
alone reroute the file away from the wav reader even when act can never fire.
"no 0x84 ⇒ wav" is falsified for preemptor-shaped files.

## Attack 4 — non-0x84 byte256 + preemptor match

Covered by Attack 3 table (0x00/0x41/0x83/0x85): always the preemptor, never
wav, never act. Value-irrelevant — the byte-256 conjunct only gates the `act`
row, which is behind both preemptors anyway.

## Attack 5 — ambiguous detection output: deciding cases constructed

- **`premature EOF` is three-way ambiguous.** (a) gsrt checksum loop (native,
  fatal); (b) au reader on empty ffmpeg pipe (act route, fatal); (c) wav
  reader's *longer* `premature EOF on input file` (WARN, non-fatal — `E1b`
  decoded 43 samples, exit 0). Same string (a)≡(b): `A5` autodetect vs
  `sox -t act A5` — identical FAIL line, but strace shows 0 vs 12 execve lines
  (ffmpeg PATH search). **Only the `-V6` detection line, the `(handler)` --i
  marker on success, or an execve count attributes the reader.** Exit codes
  are useless: `act`-fail and preemptor-fail both exit 2.
- **`--i` receipt nuances**: `(hcom)`/`(gsrt)`/`(ffmpeg)` parentheticals print
  on `.wav` names when the handler's names[0] differs from the extension —
  confirmed on `D1` (`(hcom)`), `D3_puregsrt_sz0` (`(gsrt)`), `A8` (`(ffmpeg)`).
  hcom `--i` prints the info block but **omits Duration and exits 1** (gsrt/act
  `--i` exit 0 with Duration) — a per-handler receipt quirk, not a failure.
- **`m_gsrt25`-style divergence**: author's 25-B all-zeros-except-ring.bin file
  dies `invalid/missing file name in header` while my 25-B `E2b` (RIFF@0 kept)
  dies `premature EOF` — same length, same detection, different death point:
  zeros@0 → file_size=0 → checksum skipped → dies on the 16-byte id read.
  This *corroborates* the checksum-loop mechanism (and means error strings also
  report *where* in a reader the death occurred).
- **fd seekability is an invisible fourth conjunct on the gsrt route's
  outcome**: identical bytes — `sox D2.wav -n stat` → `premature EOF` exit 2;
  `cat D2.wav | sox - -n stat` and `sox /tmp/r65fifo.wav` (named FIFO, real
  filename, non-seekable) → opens `(gsrt)`, **decodes 88 samples** 8 kHz,
  exit 0, Duration field = 2,761,067,148 samples (= `RIFF`·2−512 — the file_size
  field's own arithmetic in the receipt). Prior rounds' "stdin unexercised" is
  now measured.

## Boundaries / exactness re-verified on fresh variants

- Position: `E3_gsrt@15`/`E3b_gsrt@17`+0x84 → `act`; `E4_FSSD@64`/`E4b_HCOM@127`
  +0x84 → `act`. Signature positions exact.
- Byte-24 NUL load-bearing: `A2` (`ring.binX`@16-24 + hcom + act) → **hcom** —
  breaking the NUL demotes gsrt and the *next* row claims the file, proving the
  9-byte compare live rather than by source reading.
- Conjunction: `A6`/`A7` (FSSD-only / HCOM-only) → `act` — both hcom conjuncts
  required.
- Length gates: `E1` 132 B → hcom (reader then EOFs at @132 field reads —
  `premature EOF`, still hcom-attributed); `E1b` 131 B → `wav` (the HCOM
  signature itself is truncated to `HCO` — trivially can't match; recorded as
  such, not as a "len-gate" datapoint per se); `E2b` 25 B → gsrt; `E2` 200 B
  (sub-257) → gsrt.
- No-RIFF containers: `E5_RIFX+gsrt` → gsrt, `E5b_RIFX+hcom` → hcom — preemptor
  rows don't need RIFF at all (author's `m_gsrt25` agrees); on RIFX they also
  shadow the RIFX wav row.
- Extension: `E6_triple.bin` (all three predicates, `.bin` name) → gsrt —
  content match precedes extension fallback.
- `-t act` is not a universal rescue: on `D1` (hcom-*valid*) the bridge decodes
  3,520 samples via ffmpeg's hcom demuxer; on gsrt-shaped `D2` ffmpeg fails
  (`Invalid data`) → empty pipe → `premature EOF`. Scout's "bridge is not a
  rescue" holds only for hcom-*invalid* shapes — the bridge outcome tracks
  ffmpeg's own probe, not sox's table.

## Tracked-controls verification (author's landed diff, re-measured)

`corpus/live/round-65/` members, all 11,588 B, `0x84`@256 held everywhere;
`cmp -l` diffs vs the `act` member are exactly the signature spans:

| member | sha256 (prefix) | sole byte diffs vs act | detected | outcome | ffmpeg execve |
|---|---|---|---|---|---|
| `pair_preempt_act.wav` | `cf5edecce1812f0a` | — (**byte-identical to `round-63/pair_route_84.wav`**, `cmp` clean) | `act` | 3,839 samples, exit 0 | spawned |
| `pair_preempt_gsrt.wav` | `477bd371` | @16-24 `ring.bin\0` (9 B) | `gsrt` | `premature EOF`, exit 2 | **none** |
| `pair_preempt_hcom.wav` | `bfc61413` | @65-68 `FSSD`, @128-131 `HCOM` | `hcom` | `bad compression type`, exit 2 | **none** |
| `pair_preempt_both.wav` | `a37adc7c` | union of both spans | `gsrt` | `premature EOF`, exit 2 | **none** |

The declared move is satisfied: ≥1 tracked pair where the preemptor wins —
three, including the double-collision where `gsrt` claims a file satisfying
all three predicates (ordering, not just preemption, is pinned). Fixture diffs
are additive and follow conventions: `build_ui_preempt_r65_probe()` (the same
r63-family builder, signature overlay loop), newest-first dispatch branch,
flags appended to the mutual-exclusion `sum`, `mode`/`suffix` chain heads
prepended. Both scripts parse (in-memory `compile()`, no pyc writes);
`git diff --check` clean; `corpus/live/round-{61,63}/` untouched.

**Receipt-shape check** (matches my correction #3): the measure block records
`sox_detected_format` + `sox_route` (derived from the detection line) and runs
three legs per member — autodetect stat, `-t act` bridge counterfactual,
`-t wav` native — each with exit/samples/stderr-tail. That is exactly the
attribution-correct receipt; the preemptor members' `CalledProcessError` wrap
mirrors the r63 `pair_route_00` convention. Two minor, non-blocking notes:
(a) `sox_route` falls back to a `(ffmpeg)`-substring check in stderr that can
never fire on failed opens (no `Input File` line is emitted) — harmless dead
logic, the detected-format field is authoritative anyway; (b) the two tracked
`__pycache__/*.pyc` binaries differ — the same mechanical `py_compile` churn
disclosed in r62/r63; flag for the adjudicator.

**Pair sharpness note** (for the record, not a defect): all three preemptor
members are fail-side — inherent on the 11,588-B family, where the signatures
must land on header fields and corrupt the wav structure (gsrt @16-24 always
destroys the first chunk header; `FSSD`@65-68 straddles `dataSize` on the
fmt-40 layout). If a future round wants a positive-decode preemptor member,
the `D1`-style construction (hcom fields inside a fmt-16 payload, valid
compresstype/divisor/dict — preemptor reader *succeeds*: `(hcom)` 22050 Hz,
9 samples) is the shape to copy; scout's `pcm_hcom_act` family recommended
the same idea independently.

## Agreement with sibling scratch (all shared cases)

| case | author r65 scratch | scout r65 | this seat |
|---|---|---|---|
| gsrt+hcom+act (both/m_both/A1/probe_gsrt_hcom_act) | gsrt | gsrt | **gsrt** ✓ |
| hcom+act | hcom `bad compression type` | hcom | hcom ✓ |
| gsrt+act | gsrt | gsrt | gsrt ✓ |
| preemptor + byte256≠0x84 | gsrt/hcom (no84) | gsrt/hcom (only) | gsrt/hcom (B_*) ✓ |
| sig-boundary breaks (m23/x24/x131/x65/partials) | act | act (badnul/halves) | act (E3/E4/A2 partial) ✓ |
| len gates | gsrt 25 / hcom — | 25/24, 132/131 | gsrt 25 ✓, hcom 132→hcom / 131→wav ✓ |
| no-RIFF preemptor | m_gsrt25 → gsrt | min_gsrt_25 → gsrt | E5 RIFX, E2b → gsrt ✓ |

Zero disagreements. My additions beyond the sibling matrices: successful
preemptor decodes (D1/D2/D3), fd-seekability fork, strace attribution,
hcom-decodable triple (`E7`), `--i` per-handler exit/Duration quirks, and the
three-way `premature EOF` attribution table.

## Impacted axes

- **claim-fidelity (ordering map)**: CONFIRMED — gsrt<hcom<act<wav;
  preemptor-shaped files never routed act. The tracked pair the author lands
  should record detection lines, not only exit/stderr (both are non-unique).
- **depth**: preemptor *outcome* space is larger than "reader fails" — hcom can
  fully accept (9-sample decode, valid dict+checksum), gsrt can decode on
  non-seekable fds (88 samples); the gsrt RIFF-death is the checksum loop
  (file_size@0-3 BE), not the id read. Two prior "unexplored/open" items
  (scout's hcom-accept, stdin path) closed empirically.
- **coverage**: 33 fresh discriminating variants + strace + fifo + stdin +
  forced-type legs; 5 new probe classes the round lacked.
- **calibration**: error-string→reader attribution now exact (`bad compression
  type`/`bad sampling rate divisor`/`invalid dictionary`/`Mac …` = hcom
  field-walk positions; bare `premature EOF` = gsrt-checksum **or** au-pipe —
  ambiguous; `premature EOF on input file` WARN = wav, non-fatal;
  `invalid/missing file name` = gsrt id-read, only when checksum was skipped).
- **byte-stability**: untouched — scratch-only writes; all inputs read.

## Smallest safe correction

1. Keep the ordering claim as measured: `gsrt` < `hcom` < `act` < `wav`,
   first-match, no fallthrough on reader failure.
2. Amend the outcome clause: "preemptor detection → native reader → fatal" →
   "…→ native reader; terminal fate is reader-field-walk-dependent and, for
   gsrt, fd-seekability-dependent — hcom accepts crafted RIFF files fully,
   gsrt always dies in the checksum loop on seekable RIFF collisions but can
   decode via pipes."
3. In the tracked pair's receipts, capture `detected file format type` (and
   `(handler)` marker or execve count where ambiguous) — exit code and the
   bare `premature EOF` string do not attribute the reader.
4. If the pair budget allows one more member, `D1`-style hcom-*valid* collision
   (preemptor reader *succeeds*: `(hcom)`, 22050 Hz, 9 samples, exit 0) is
   sharper than a fail-only pair — it proves route selection by positive
   decode, and its `-t wav` leg (278 samples) shows the suppressed member was
   genuinely readable.

## Receipts

- `corpus/live/r65-critic/gen.py`, `probe.sh`, `results.tsv` (33 rows),
  `var/` exhibits, `shas.txt`. Key shas: `A1` c8dd9fa2…, `A5` ba0156fa…,
  `D1` 325fb967…, `D2` bf60b294…, `E7` 2d682bbf….
- Commands verbatim above; detection line `sox -V6 <f> -n stat`; decode
  `sox <f> -t f32 -e floating-point - | wc -c`; strace `-f -e trace=execve`;
  stdin `cat <f> | sox -V6 - -n stat`; fifo `mkfifo /tmp/r65fifo.wav`.
- Source (corroborative only): `/tmp/sox_ng_src/sox_ng/src/formats.c` CHECK rows
  (gsrt :81, hcom :90, act :93, wav :95); `gsrt.c` start_read (readdw file_size,
  `file_size>=2 && ft->seekable` checksum loop, skip 12, 16-byte id read,
  `PADDING_SIZE` 478); `hcom.c` field-walk and error strings; both from the
  r64-verified sox_ng-14.8.0.1 tree.
