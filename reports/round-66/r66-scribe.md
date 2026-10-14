# R66 scribe — preemptor-map completion: wve predicate pinned, unreachable-on-RIFF falsification confirmed, decodable preemptors + length gates verified

Seat: **scribe** (leaf, report-only). Host: devin (`/usr/bin/sox` = SoX_ng
v14.8.0.1 USING_FFMPEG build; ffmpeg/ffprobe n9.0.1; python 3.14.7).
Worktree `~/Projects/prymeagnt/audio` with `.shokunin/audio` → canonical
`~/Projects/shokunin/audio-shokunin`. Scratch `corpus/live/r66-scribe/`;
this file is the only report path written.

Axis-move (verbatim, from the brief): *"complete the preemptor map on
RIFF+0x84@256 files: r65 boundary measured a wve CHECK row (formats.c row
~80) that precedes even gsrt(81) — identify wve's byte predicate empirically,
determine whether a wve-shaped RIFF file preempts gsrt/hcom/act (falsifiable
ordering claim), and land tracked DECODABLE-preemptor controls: at least one
pair where detection flips to a preemptor AND that preemptor's reader
successfully decodes (the critic's D1_hcomdecode+act 9-sample family, or the
scout's fmt-16 pcm_hcom_act/pcm_hcom68x sole-byte-68 pair), plus length-gate
boundary members pinning gsrt 24|25 and hcom 131|132 exactly. All prior
behavior — 96-command ledger, r63/r64/r65 tracked fixtures — byte-stable;
everything empirical (probes primary, disasm corroborative only)."*

## Prior-work disposition (verify/reuse, not restart)

`corpus/live/r66-scribe/` already contained a complete executed suite from an
earlier session of this seat: `gen_probes.py` (271 lines, own constructions —
LCG filler, own hcom field-chain values, 280–700 B carriers, NOT the author's
ramp carrier nor r65-scribe's JUNK family), `sweep.sh`, `results.tsv`
(71 data rows × 17 columns), `variants/` (71 fixtures + `manifest.tsv`),
`logs/` (1,562 per-variant receipt files: `stat`, `--i`, raw f32 decode,
forced `-t {wve,gsrt,hcom,act,wav}`, ffprobe, pipe-stdin and seekable-stdin
legs). Reuse verification performed this session:

- `awk`+`sha256sum -c` over `variants/manifest.tsv`: **all 71 fixtures
  byte-match their recorded SHAs** (silent pass).
- Bounded live re-execution (23 legs, capture `verify/spot-20261014.txt`):
  every result reproduced the recorded `results.tsv` value exactly —
  detection labels, sample counts, exit classes and error strings all
  identical. No drift between the recorded sweep and current binary
  behavior.

## Independent-derivation results (my own constructions)

### wve detector predicate — pinned exactly

`detect(wve) ⟺ len ≥ 15 ∧ file[0:15] == "ALawSoundFile**"`.

| probe | construction | detected |
|---|---|---|
| `P01_wve_magic15` | 15-B literal @0 + LCG filler, 280 B | **wve** (reader rejects) |
| `P02_x00`–`P02_x14` | XOR 0xFF at each position 0–14 | **15× no-detect** — every byte load-bearing |
| `P03_b15free` | byte 15 = 0x99 | **wve** — bytes ≥15 unconstrained |
| `P04_stars00` / `P05_stars1A` | `**`→`00` / `**`→`1A` | no-detect / no-detect — `*` is **literal 0x2A**, not wildcard or version digit |
| `P06_e12X` | byte 12 `e`→`X` | no-detect |
| `P07_len14` / `P08_len15` / `U09`/`U10` bare | 14 B / 15 B files | no-detect / **wve** — floor **exactly 15** |
| `P10_lowercase` | `alawsoundfile**` | no-detect — case-sensitive |

Corroborative-only source anchor: `formats.c:80`
`CHECK(wve,0,0,"",0,15,"ALawSoundFile**")` → `len>=15 && !memcmp(data,…,15)`
(local verified copy `/tmp/sox_ng_src/sox_ng/src/formats.c`; ==
`corpus/live/r64-reviewer/r64rev-formats.c` per r64's diff-verification).

### wve on RIFF — the falsifiable ordering claim is FALSIFIED (geometrically)

wve's predicate anchors at offset 0 and requires byte 0 = `0x41 'A'`; every
RIFF-family tag (`RIFF`/`RIFX`/`RF64`) requires `0x52 'R'` at byte 0. The
predicates are **mutually exclusive on any byte stream** — a "wve-shaped RIFF
file" cannot exist.

| probe | construction | detected | outcome |
|---|---|---|---|
| `Q1016/Q1044/Q1064/Q1100/Q1200` | RIFF+WAVE+0x84@256, `ALawSoundFile**` embedded @ {16,44,64,100,200} | **act** all five | @16 clobbers fmt-chunk → ffmpeg-fatal `premature EOF`; @44+ → ffmpeg bridge decodes 178 samples pcm_s16le |
| `Q120` | magic @4 (inside RIFF size field) | act | premature EOF |
| `Q121` | `RIFX`@0 + magic @16 | **wav** | RIFX wav-row fires; reader `file encoding 0x536f` |
| `Q02` | wve@0 + `FSSD`+`HCOM` + 0x84@256, no RIFF | **wve** | **decodes 64 samples, exit 0** |
| `Q03` | wve@0 + `ring.bin\0`@16 + `FSSD`+`HCOM` + 0x84 | **wve** | reader reject — wve beats gsrt+hcom simultaneously off-RIFF |
| `Q04` | wve@0 + `RIFF`@40 + 0x84 | **wve** | 64 samples — embedded RIFF inert (act anchors @0) |
| `Q05` | wve@0 + 0x84@256, no RIFF anywhere | **wve** | 64 samples |

So: **wve ≺ gsrt ≺ hcom ≺ act in table order where co-satisfiable (non-RIFF),
and wve is unreachable on the entire RIFF family.** The reachable pre-act
preemptor set on RIFF+0x84@256 is exactly **{gsrt, hcom}** — the map is
complete. Convergent with author W-series (16 RIFF embeds → act/wav, never
wve), reviewer p1–p8, simplifier s_* probes.

### wve reader fate — detector looser than reader (inverse of gsrt)

| probe | construction | detected | reader outcome |
|---|---|---|---|
| `R01_wve_dec64` | full 18-B ID1 `ALawSoundFile**\x00\x0f\x10` + BE32 num=64 + 10-B pad + 64 B data | wve | **64 samples, 8-bit A-law, exit 0** |
| `R02_wve_dec0` | num_samples=0 | wve | 0 samples, exit 0 |
| `R03` (declared 32 < 64 avail) / `R04` (declared 500 > 268 avail) | num_samples vs data-length mismatch, both directions | wve | reads **min(declared, available)**: 32 / 268 (+WARN `file header gives … but file length indicates …`) |
| `R05`/`P09`/`R06` | 15-B magic only / wrong ID1 tail (`\x00\x00\x00`, `\x01\x02\x03`) | wve | `can't find Psion identifier` / short files → `premature EOF` |

wve.c:22-37 (corroborative): reader re-verifies **18-byte** ID1
`ALawSoundFile**\0\017\020`, reads BE `num_samples`, skips 10 pad bytes.
Detector 15 B < reader 18 B — opposite asymmetry to gsrt, whose detector
literal includes the NUL@24 its reader never inspects (`memcmp(read_id, id,
strlen(id))` compares 8 bytes; gsrt.c:105 — my `T05` byte24=`0x2E` detects
`act`, not `gsrt`; on the forced `-t gsrt` file leg the same body dies
earlier anyway, in the RIFF `file_size` checksum loop).

### hcom decodable-preemptor inside RIFF+0x84@256 — independent re-derivation

| probe | construction (own field values) | detected | outcome |
|---|---|---|---|
| `S01_hcom_dec_riff` | 512-B fmt-16 RIFF/WAVE + `FSSD`@65 + `HCOM`@128 + reader chain (huffcount 5 @132 BE, cksum @136, compresstype 0 @140, divisor 2 @144 → 11025 Hz, dictsize 2 @148, dict @150-157, pad 0 @158, first byte @159, word @160) + 0x84@256 | **hcom** | **decodes 5 samples @11025 Hz, exit 0**; `--i` → `(hcom)` `8-bit HCOM`; ffprobe `codec_name=hcom` |
| `S02` / `S03` | sole byte `D`→`E` @68 / `M`→`N` @131 | **act** | ffmpeg bridge decodes 234 samples pcm_s16le — sole-byte detection-flip pair |
| `S04` | S01 minus act byte (256→0x00) | **hcom** | still 5 samples — preemptor needs no act conjunct |
| `S05`–`S08` | compresstype 7 / divisor 9 / dictsize 0 / dict-entry out of range | hcom | reader rejects at named gates: `bad compression type` / `bad sampling rate divisor` / `implausible dictionary size` / `invalid dictionary` |
| `S09` | declared checksum `0xDEADBEEF` ≠ consumed-word cksum | hcom | **5 samples, exit 0 — mismatch silent** |
| `S10`/`S11` | huffcount 9000 / 0 | hcom | 0 samples, exit 0 both |
| `S12` | compresstype 1 (delta) | hcom | decodes 5, exit 0 |

**New observation this round** (not in sibling reports): hcom's two
`stopread` close-time guards — `not all HCOM data read` and `checksum error
in HCOM data` (hcom.c:265-272) — produced **no observable failure**: neither
string appears in any of my 1,562 logs; S09 exits 0 with 5 samples despite a
provably wrong declared checksum, S10 exits 0 with the huffman count never
exhausted. The guards exist in source but are inert on the stat/decode path
on this build.

### gsrt decode fate + the seekability conjunct

| probe | construction | detected | outcome |
|---|---|---|---|
| `T01`/`T02` | non-RIFF 700-B carrier, `ring.bin\0`@16, file_size field 0 (checksum skipped), enc 0 (μ-law) / 8 (A-law) | gsrt | **188 samples each, exit 0** — gsrt decodes on a well-formed body |
| `T03` | enc 2 (G726) | gsrt | `invalid format for this file type` — reader's own encoding gate |
| `T04_gsrt_riff_collide` | RIFF+GSRT9@16+0x84@256, 600 B | gsrt | **file leg: `premature EOF` exit 2; pipe leg (`cat \| sox -`): 88 samples exit 0** — same bytes, opposite fates |
| `T05` | byte 24 `NUL`→`0x2E` | **act** | detector stricter than reader at byte 24; act route then fails `premature EOF` (ffmpeg finds no parseable stream) |

The T04 fork pins the conjunct in source (corroborative): gsrt.c:88
`if (file_size >= 2 && ft->seekable)` — the checksum-scan loop runs only on
seekable fds; `RIFF`@0 reads as BE `file_size` ≈ 1.38 G → loop reads to EOF
→ `premature EOF`. On a pipe the loop is skipped and the stream decodes
the bytes physically available after the 512-B HEADER_SIZE — exactly
88 = 600 − 512 — matching r65-critic's D2 pipe leg (88 samples) on a
different construction.

### Exact length gates — both RIFF shells and bare carriers

| gate | below | at/above | pinned |
|---|---|---|---|
| gsrt `len ≥ 25` (16+9) | `U02`/`U06` 24 B → `wav`/`NONE` | `U01`/`U05` 25 B → `gsrt` | **24‖25** |
| hcom `len ≥ 132` (128+4) | `U04`/`U08` 131 B → `wav` (decodes 43!) /`NONE` | `U03`/`U07` 132 B → `hcom` | **131‖132** |
| wve `len ≥ 15` | `U10`/`P07` 14 B → `NONE` | `U09`/`P08` 15 B → `wve` | **14‖15** |
| act `len ≥ 257` (256+1) | `U12` 256 B → `wav` (106 samples) | `U11` 257 B → `act` | **256‖257** |

Bare-carrier arms match the RIFF-shell arms — the gate is `len ≥ p + l` on
the read window, not a container property.

## Cross-seat verification (this session, executed by me)

- **Tracked members** (`corpus/live/round-66/`, uncommitted `??`):
  `pair_dec_hcom.wav` → `-V6 stat` prints `` detected file format type
  `hcom' `` + `Samples read: 9` (live, this session); `pair_dec_act.wav` →
  `act` + 278 samples; SHAs equal the author's report exactly
  (`325fb967…`, `777b6764…`, `e7db9976…`, `ede4161b…`, `6fd9f471…`,
  `a1abdac4…`).
- **Cross-seat byte-identity**: `cmp` —
  `round-66/pair_dec_hcom.wav` == `r65-critic/var/D1_hcomdecode+act.wav`
  (sha256 `325fb967f0c9c126…` both) **and** == author's scratch
  `D01_hcomdecode+act.wav`. Three independent constructions, one byte
  stream.
- **Ledger**: `corpus/live/r66-author/ledger-r66.tsv` = 102 rows, exit
  census **44×0 / 58×1** (matches author); normal-run receipt
  `runs/20261014T023251113379Z-normal/measurements.json` **byte-identical**
  (`cmp`) to r65's `20261014T014330610722Z`. Author/simplifier/baseline
  report prior-96 receipt byte-identity (96/0/0 by the simplifier's own
  run; baseline's frozen replay 86/96 raw-identical + 10 disclosed
  path-embedding class, 0 content diffs).
- **Toolchain**: identical to r65 record (SoX_ng 14.8.0.1, ffmpeg n9.0.1) —
  re-observed in `-V6` headers this session.
- **Working tree**: `git status` shows only `M build_artifacts.py` (+113/−1),
  `M measure_audio.py` (+93/−4), `M __pycache__` (mechanical regen,
  pre-disclosed class), `?? corpus/live/round-66/` + sibling scratch —
  the additive-only shape the author and simplifier describe.

## Conflicts / findings reported verbatim for the judge

1. **SCORECARD wording vs measured reachability** (r66-reviewer LOW-1,
   confirmed verbatim): `SCORECARD.md:662` r65 coverage cell reads *"a
   measured total order — `wve ≺ gsrt ≺ hcom ≺ act ≺ wav`"* scoped to the
   RIFF family. Table order does put wve(80) before gsrt(81), but on RIFF
   files wve is **unreachable** (offset-0 `A`/`R` exclusion — proven by my
   Q-family, the author's 16-embed battery, reviewer's p7). The r65
   knowledge entry is correctly scoped; the scorecard cell alone could
   mislead. Wording-level, no data error.
2. **The declared wve-preempts-on-RIFF claim resolved falsified** — the
   brief's explicit else-branch; author, reviewer, simplifier and this seat
   converge on the geometric exclusion. A falsified claim, cleanly
   recorded.
3. **Detection ≠ accept, three distinct asymmetries now measured**:
   wve detector 15 B < reader 18 B (detect-then-reject, R05/P09);
   gsrt detector 9 B > reader 8-B memcmp (NUL@24 demanded by the CHECK row
   only, T05; reader's `memcmp(read_id, id, strlen(id))` = 8 bytes,
   gsrt.c:105); hcom reader validates a whole field chain past the
   detector's two literals (S05–S08 ladder) yet its close-time integrity
   guards are inert in practice (S09/S10). "Detected" is a *claim made by the CHECK
   row*, not a promise the reader keeps — and for `act` the "reader" is an
   ffmpeg re-probe that can still decode the same bytes as `pcm_s16le`
   (S02/S03/U11/Q1044).
4. **hcom integrity fields are advisory on this path** — declared checksum
   wrong → still decodes (S09); declared huffcount impossible → still
   opens, emits what exists, exit 0 (S10). Guards present in source
   (hcom.c:265-272), unobserved in effect.
5. **Scout-pair alternative noted**: the brief offered the fmt-16
   `pcm_hcom_act`/`pcm_hcom68x` sole-byte-68 pair as an acceptable control;
   the author landed the critic's D1 family instead. Both flip on byte 68,
   but per r66-reviewer §3 the scout pair's hcom member fails its reader
   (`bad compression type`) — flip-only, not decodable — so the D1 choice
   was the load-bearing one. Recorded, no conflict.
6. **Seat-status at observation time**: sibling reports on disk —
   author, baseline, reviewer, simplifier. Boundary and scout have scratch
   matrices landed (`r66-boundary/runs/{matrix,sweep}.tsv` ≈1,796 rows;
   `r66-scout` probes+matrix) but no report files yet; r66-critic scratch
   is an empty dir. Their later prose may add corroboration; nothing in
   their scratch contradicts this table.
7. **Pre-disclosed caveats re-observed, not new**: `--i` exit-1 vs `stat`
   exit-2 asymmetry persists on open-failure legs; `premature EOF` remains
   non-attributing (≥3 emitters); receipt stderr paths embed absolute repo
   paths (same-host property).

## Touched surfaces / out-of-scope

- Wrote this session: `reports/round-66/r66-scribe.md`;
  `corpus/live/r66-scribe/verify/spot-20261014.txt` (bounded re-execution
  capture). Prior session of this seat wrote the `gen_probes.py`,
  `sweep.sh`, `results.tsv`, `variants/` (72 files), `logs/` (1,562 files)
  under the same scratch scope — verified and reused, not redone.
- Read-only: `corpus/live/round-66/` members, sibling r66 scratch
  (`r66-author`, `r66-reviewer`, `r66-simplifier`, `r66-baseline`,
  `r66-boundary`, `r66-scout`), `r65-critic/var/`, `ledger-r66.tsv`,
  `SCORECARD.md`, `LOG.md`, `corpus/knowledge/*`, `/tmp/sox_ng_src` sources
  (formats.c:80-97, wve.c, gsrt.c, hcom.c — corroboration only).
- Not done (out of scope / not mine): no commits/pushes/tags; no tracked
  edits (fixtures, measure/build scripts, LOG/SCORECARD/knowledge — the
  knowledge draft below is parent-decision content); no runner invocation;
  no second runtime; no subagent dispatch; no judgment of the axis (Pareto
  verdict belongs to the canonical Rust runtime/judge chain).

## Bounded UNKNOWNs retained

- All results single-host: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1.
  ffmpeg-less builds shrink `AUTO_DETECT_SIZE` to 132 and compile out the
  act row (source-level inference, untested) — wve/gsrt/hcom geometry
  unchanged, the act claim evaporates with its row.
- wve reader semantics beyond `start_read` (ID2 pad semantics, write path)
  unprobed; hcom Huffman decode correctness vs reference unmeasured — decode
  *count/exit* claims only.
- Whether `stopread` failures are ever propagated on any sox code path —
  observed inert on `stat`/decode/`--i`; other paths unexercised.
- gsrt pipe-decode's declared `num_samples` (~2.76 G from the `RIFF` dword)
  vs the 88 actually delivered — stream-length semantics on non-seekable
  inputs are clamped empirically, not mapped.
- `--magic`/`use_magic` path remains off-by-default untested; non-RIFF
  container families (AIFF etc.) out of scope.

## Draft knowledge entry — for `corpus/knowledge/2026-10-14-sox-preemptor-map-complete.md`

(Seat draft for parent decision; `[pending]` slots await the work/knowledge
commit SHAs the integration step assigns.)

```markdown
# SoX_ng preemptor map COMPLETE on RIFF+0x84@256 — wve unreachable on RIFF; decodable preemptors and exact length gates (round 66)

- Source: round-66 seat evidence (`reports/round-66/r66-{author,reviewer,
  simplifier,scribe,baseline}.md`; independent sweeps
  `corpus/live/r66-{author,scribe,simplifier,boundary,scout}/…`); upstream
  sox_ng-14.8.0.1 `src/formats.c` (local verified copy
  `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`), `wve.c`,
  `gsrt.c`, `hcom.c` — source citations corroborative; all load-bearing
  claims empirical. Commit: [pending].
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1. Work commit: [pending];
  this file's commit: [pending].
- Recheck when: SoX or ffmpeg version/build changes (the `act` row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  drop act), when the CHECK table gains or reorders any row, when a new row
  without an offset-0 anchor lands before `act`, or when fixture families
  change shape.

## Full measured ordering (first matching CHECK row wins)

`auto_detect_format` reads ≤ AUTO_DETECT_SIZE (257 on this build) once and
returns the FIRST matching row (formats.c:66-97). Measured table order,
with reachability on the RIFF family:

    voc(78) ≺ smp(79) ≺ wve(80) ≺ gsrt(81) ≺ amr-wb(82) ≺ prc(83) ≺
    sph(84) ≺ amr-nb(85) ≺ txw(86) ≺ sndt(87) ≺ vorbis(88) ≺ opus(89) ≺
    hcom(90) ≺ act(93) ≺ wav(95-97) ≺ aiff/aifc/8svx…

- Every row before `hcom` anchors a non-RIFF literal at offset 0
  (voc/smp/wve/amr-wb/prc/sph/amr-nb/txw/sndt) or `OggS`@0 (vorbis/opus) —
  all unreachable on `RIFF`/`RIFX`/`RF64`@0 files.
- On a `RIFF`@0 file the reachable pre-act preemptor set is exactly
  **{gsrt, hcom}**; measured order `gsrt ≺ hcom ≺ act ≺ wav` (r65 entry,
  re-verified r66).
- On non-RIFF carriers wve DOES preempt gsrt/hcom/act-shaped co-signatures
  (scribe `Q01–Q05`, author `W02–W04`, reviewer `p2/p3`,
  `m_wve_gsrt.bin` re-run) — table position 80 < 81 is live but only off
  the RIFF family.

### wve predicate (new this round)

    detect(wve) ⟺ len ≥ 15 ∧ file[0:15] == "ALawSoundFile**"

- All 15 bytes individually load-bearing (15 single-byte mutants →
  no-detect); `**` are literal `0x2A` bytes (`00`/`1A`/`?` substitutions all
  fail); case-sensitive; bytes ≥15 unconstrained; length floor exactly 15
  (14 → no-detect, 15 → wve). formats.c:80 corroborative.
- **Geometric exclusion**: byte 0 must be `0x41 'A'`; RIFF/RIFX/RF64 all
  require `0x52 'R'` at byte 0. No byte stream satisfies both — a
  "wve-shaped RIFF file" cannot exist. ~25 independent RIFF/RIFX
  constructions embedding the wve magic at offsets {4,8,12,15,16,36,44,64,
  100,128,200,252,300} detected `act`, `gsrt` or `wav` — never `wve`
  (scribe `Q1*/Q120/Q121`, author `W3*/W4*`, reviewer `p7`, simplifier
  `s_riff_wve300*`).

### Detection ≠ accept — the reader keeps its own contract

| format | detector | reader additionally requires | measured asymmetry |
|---|---|---|---|
| wve | 15-B literal @0 | 18-B ID1 `ALawSoundFile**\x00\x0f\x10` + BE32 num_samples + 10-B pad (wve.c:22-37) | detector **looser** — detects on 15 B, reader rejects `can't find Psion identifier` (15-B-only / wrong-tail files) |
| gsrt | `ring.bin\0` @16-24 (9 B incl. NUL) | `memcmp(read_id,"ring.bin",8)` @16 (gsrt.c:105) + file_size/encoding fields | detector **stricter** at byte 24 — `ring.bin`+`0x2E` does NOT detect gsrt (falls to act); byte 24 is never read by the reader's id check |
| hcom | `FSSD`@65 ∧ `HCOM`@128 | field chain @132+: compresstype ≤1, divisor 1-4, dictsize 1-511, valid dict entries | reader rejects at named gates (`bad compression type`/`bad sampling rate divisor`/`implausible dictionary size`/`invalid dictionary`) AFTER detection claims hcom |
| act | `RIFF`@0 ∧ `0x84`@256 | none — the "reader" is a `popen ffmpeg -f au` bridge; ffmpeg re-probes the bytestream | act-detected RIFF decodes as `pcm_s16le` via ffmpeg when the RIFF is parseable — detection routes, ffmpeg decides |

- A failed open is **terminal**: no re-detection, no second handler, no
  fallback to wav/act (r63+; re-verified on r66 fail-ladders).
- Error strings do not attribute the route (`premature EOF` has ≥3
  emitters); only the `-V4/-V6` `detected file format type` line does.
- hcom's close-time guards (`not all HCOM data read`, `checksum error in
  HCOM data`; hcom.c:265-272) produced **no observable failure** — wrong
  declared checksum still decoded 5 samples exit 0; impossible huffcount
  still opened and emitted what existed (scribe `S09`/`S10`). Declared
  integrity fields are advisory on the stat/decode path on this build.
- wve reader clamp: samples read = **min(declared num_samples, available
  data bytes)** both directions (32-declared→32; 500-declared→268, with
  WARN), not a failure.

### The seekability conjunct (invisible, load-bearing)

gsrt.c:88 `if (file_size >= 2 && ft->seekable)` gates a checksum-scan loop
over the whole stream. A RIFF collider reads `file_size` = `0x52494646`
(≈1.38 G): on a seekable fd the loop walks to real EOF → `premature EOF`
exit 2; on a non-seekable pipe the loop is skipped and the same bytes
decode 88 samples exit 0 (600-B carrier − 512-B HEADER_SIZE; r65 critic D2
and r66 scribe T04, independent constructions, identical fork). Transport,
not content, decides the outcome.

### Tracked decodable-preemptor controls and length gates (round-66)

`corpus/live/round-66/` (probe modes `--probe-ui-{dec-hcom,dec-act,
lengate-gsrt-24,lengate-gsrt-25,lengate-hcom-131,lengate-hcom-132}-r66`):

| member | construction | detected | decode fate |
|---|---|---|---|
| `pair_dec_hcom.wav` (600 B, sha [pending-pinned] `325fb967…`) | fmt-16 RIFF/WAVE + `FSSD`@65 + `HCOM`@128 + reader-valid hcom chain + `0x84`@256 | `hcom` | **native hcom reader decodes 9 samples @22050 Hz, exit 0**; `-t wav` 278; `-t act` 3,520 (ffmpeg's own hcom demuxer); byte-identical to r65-critic's `D1_hcomdecode+act.wav` |
| `pair_dec_act.wav` (`777b6764…`) | sole byte @68 `D`→`E` | `act` | ffmpeg bridge 278 samples pcm_s16le — detection flips on one conjunct byte |
| `pair_lengate_gsrt_{24,25}.wav` (`e7db9976…`/`ede4161b…`) | RIFF shells 24/25 B, `ring.bin[\0]`@16 | `wav`/`gsrt` | gate exactly 25 = 16+9; below-gate member is a wav-claimed honest shell |
| `pair_lengate_hcom_{131,132}.wav` (`6fd9f471…`/`a1abdac4…`) | RIFF shells 131/132 B, `FSSD`@65 + `HCO[M]`@128 | `wav`/`hcom` | gate exactly 132 = 128+4; 131-member decodes 43 samples as wav (the suppressed reader is genuinely readable) |

Exact gates independently re-pinned on bare carriers: wve **14‖15**,
gsrt **24‖25**, hcom **131‖132**, act **256‖257** — the `len ≥ p + l`
conjunct is a read-window property, not container-bound. Ledger 96→102
commands (44 exit 0 / 58 exit 1); all prior receipts byte-identical modulo
the pre-disclosed same-host path-embedding class.

## Falsifiable recheck conditions

1. `sox -V4 corpus/live/round-66/pair_dec_hcom.wav -n stat 2>&1` must print
   `detected file format type `hcom'` AND `Samples read: 9` exit 0 —
   `act`/`wav` detection, or 0 samples, falsifies the decodable-preemptor
   claim. Partner `pair_dec_act.wav` must detect `act` and read 278.
2. `sox -V4 pair_lengate_{gsrt_24,gsrt_25,hcom_131,hcom_132}.wav -n stat`
   must detect `wav`/`gsrt`/`wav`/`hcom` respectively; any flanking flip
   falsifies the exact-gate claim.
3. wve unreachability: any construction with `RIFF`/`RIFX`/`RF64` at byte 0
   that detects `wve` falsifies the geometric-exclusion claim regardless of
   embedded magic placement.
4. Rebuild determinism: `build_ui_dec_preempt_r66_probe()` +
   `build_ui_lengate_r66_probe()` must reproduce all six members
   byte-identically (`cmp` vs committed blobs); ledger re-run must hold
   44/58.
5. Any SoX/ffmpeg version or build-flag change → re-run the scratch sweeps
   (`corpus/live/r66-scribe/sweep.sh`, `r66-author` equivalents); a
   CHECK-table addition before row 93 without an offset-0 anchor, or an
   `AUTO_DETECT_SIZE` resize, invalidates the ordering at the first
   differing row.

## Bounded UNKNOWNs retained

- Single host/toolchain (SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1);
  ffmpeg-less builds drop the act row and shrink the read window to 132
  (untested compile-level inference) — gsrt/hcom ordering survives, act
  claims evaporate.
- wve reader/write semantics beyond `start_read` (ID2 pad, repeat info);
  hcom Huffman correctness vs reference; gsrt non-seekable length semantics
  — decode-count claims only, no fidelity/conformance claim.
- Whether stopread-class failures ever propagate on any code path
  (observed inert on stat/decode/`--i` legs only).
- `--magic`/`use_magic` path; plugin-registered CHECK rows (none
  installed); non-RIFF containers beyond spot checks.
```

## Stop

Report complete; seat halts here. No orchestration, no commits, no
sibling-scope writes.
