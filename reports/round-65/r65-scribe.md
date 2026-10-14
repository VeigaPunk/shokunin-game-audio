# R65 scribe — preemptor-collision autodetect ordering on RIFF files

Seat: scribe (report-only documentation draft). Host: devin. Round axis-move
(verbatim, from the brief): *"map the pre-act autodetect preemptor ordering on
RIFF files … construct minimal RIFF+0x84@256 files that ALSO match each
preemptor's predicate; measure empirically which detection wins and what
reader/route it selects (decode, `sox --i`, ffprobe comparison, exit codes);
if a preemptor-shaped file still routes act, that ordering claim is falsified
and must be recorded as such. Pin at least one tracked RIFF-preemptor
collision control pair where the preemptor wins; keep all prior behavior
including the r63 ledger rows and pair fixtures byte-stable; derive everything
empirically (probes)."*

Toolchain on record: `sox` SoX_ng v14.8.0.1 (`pacman -Q sox` = 14.8.0.1-1,
USING_FFMPEG build), `ffmpeg`/`ffprobe` n9.0.1 (`pacman -Q ffmpeg` =
2:9.0.1-4), Python 3.14.7, all `/usr/bin`. Scratch: this seat wrote only
`reports/round-65/r65-scribe.md` + `corpus/live/r65-scribe/` (generator
`gen_variants.py`, harness `sweep.sh`, `results.tsv` (27 rows + header),
`variants/` (27 manifest fixtures + 9 post-sweep `x_*` bisect exhibits),
`variants/manifest.tsv`, `logs/` per-file receipts: `*.stat.{out,err}`,
`*.i.{out,err}`, `*.dec.err/out`, `*.ffp.{out,err}`, forced-leg
`*.t{wav,act,gsrt,hcom}.{out,err}`). No tracked file, fixture, receipt, probe
mode, or other lane's surface was written; nothing committed; the project
runner was not invoked by this seat (no `--runs` flag; would write shared
`live/runs/` — same posture as r64-scribe).

Wave context: this scribe ran concurrently with the r65 wave. At observation
time the tracked writer had landed (uncommitted working-tree state)
`corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` +
`build_artifacts.py` (+40) + `measure_audio.py` (+65, four
`--probe-ui-preempt-*-r65` modes) and its 96-command ledger; sibling reports
`r65-{author,baseline,critic,reviewer,scout}.md` exist under
`reports/round-65/`. Sibling content is cited as *data* in the cross-seat
section only.

## Verdict on the declared claim

**CONFIRMED, not falsified — measured order: `gsrt` ≺ `hcom` ≺ `act` ≺ `wav`
(first matching CHECK row wins).** No preemptor-shaped file routed `act` on
any of my 27 sweep files + 9 bisect exhibits, nor on the author's tracked
4-member family. A file carrying all three signatures (RIFF@0, `ring.bin\0`
@16-24, `FSSD`@65-68, `HCOM`@128-131, `0x84`@256) detects `gsrt` on every
construction (mine `b_both84`, `n_gsrt_hcom`; author's `pair_preempt_both`).
The ordering survives; it is now a *measured total order*, not a candidate
list.

## Independent construction (not the r61 fixture family)

All fixtures are hand-built 312-B (or length-gate) files written by
`gen_variants.py`; none derives from the r61/r63 WAV corpus:

- **Family V — valid minimal WAV**: `RIFF`+`WAVE`+`JUNK`(196-B payload at
  file 20-215)+`fmt`(PCM16/mono/8 kHz @216)+`data`(64 B @240). The hcom
  windows 65-68 and 128-131 sit *inside the JUNK payload*, so the file stays
  a fully well-formed WAV that decodes under `-t wav`. Byte 256 is data
  payload byte 8; `0x84` assigned per member.
- **Family B — bare RIFF shell**: `RIFF`+size+`WAVE`/variant-form then zeros;
  detection bait only. Carries the gsrt signature (which *cannot* coexist
  with a valid RIFF chunk table — see Finding 2).
- **Family N — non-RIFF controls**: zeroed carriers + signatures; isolates
  each preemptor's (lack of) offset-0 anchor.
- **Family L — length gates**: exact `len >= p1+l1` boundaries.

## Measured detection results (my sweep — `results.tsv`, 27 rows)

| variant | signatures present (RIFF@0 and `0x84`@256 unless noted) | detected | outcome | receipt |
|---|---|---|---|---|
| `v_base84` | — (valid WAV) | `act` | `--i` `(ffmpeg)`, no Duration; decode 128 B f32 exit 0 | `logs/v_base84.wav.*` |
| `v_base00` | byte256→0x00 | `wav` | native; `--i` no suffix + Duration; 128 B f32 exit 0 | `logs/v_base00.wav.*` |
| `v_hcom84` | `FSSD`@65+`HCOM`@128 (inside JUNK payload) | **`hcom`** | exit 2 `bad sampling rate divisor` | `logs/v_hcom84.wav.stat.err` |
| `v_hcom00` | hcom sigs, byte256→0x00 | **`hcom`** | exit 2 `bad sampling rate divisor` — preempts `wav` too | `logs/v_hcom00.wav.stat.err` |
| `v_fssd_only` | `FSSD`@65 only | `act` | `(ffmpeg)`, 128 B exit 0 | |
| `v_hcom_only` | `HCOM`@128 only | `act` | `(ffmpeg)`, 128 B exit 0 | |
| `v_gsrt84` | `ring.bin\0`@16-24 over JUNK size | **`gsrt`** | exit 2 `premature EOF` | `logs/v_gsrt84.wav.stat.err` |
| `b_riff84` | bare shell + `WAVE`@8 | `act` | bridge fails `premature EOF` exit 2 | |
| `b_riff00` | byte256→0x00 | `wav` | wav reader `fmt chunk not found` exit 2 | |
| `b_noform84` | `XXXX`@8 (no WAVE) | `act` | exit 2 — `WAVE`@8 not a conjunct (r63 re-check) | |
| `b_avi84` | `AVI `@8 | `act` | exit 2 — act precedes the post-act `avi` rows | |
| `b_gsrt84` | `ring.bin\0`@16-24 | **`gsrt`** | exit 2 `premature EOF` | |
| `b_gsrt_00` | gsrt sig, byte256→0x00 | **`gsrt`** | exit 2 — preemptor ignores byte 256 | |
| `b_hcom84` | `FSSD`@65+`HCOM`@128 | **`hcom`** | exit 2 `bad sampling rate divisor` | |
| `b_hcom_00` | hcom sigs, byte256→0x00 | **`hcom`** | exit 2 | |
| `b_both84` | gsrt + hcom + act signatures | **`gsrt`** | exit 2 — gsrt beats hcom beats act | |
| `b_gsrt_badnul` | `ring.bin`@16-23 + byte24=`0x2e` | `act` | exit 2 — the literal's 9th byte (terminating NUL) is compared | |
| `n_gsrt` | `ring.bin\0`@16, no RIFF | **`gsrt`** | **exit 0** — reader accepts; 0 samples | `logs/n_gsrt.bin.*` |
| `n_hcom` | hcom sigs, no RIFF | **`hcom`** | exit 2 `bad sampling rate divisor` | |
| `n_gsrt_hcom` | both sigs, no RIFF | **`gsrt`** | exit 0 — ordering holds without RIFF | |
| `n_zero` | none, no RIFF | *no match* | `no handler for file extension 'bin'` exit 2 | |
| `l_gsrt_25` | `ring.bin\0`@16-24, 25 B | **`gsrt`** | exit 2 `invalid/missing file name in header` | |
| `l_gsrt_24` | `ring.bin`@16-23 only, 24 B | *no match* | `no handler for file extension 'bin'` | |
| `l_hcom_132` | hcom sigs, 132 B | **`hcom`** | exit 2 `premature EOF` | |
| `l_hcom_131` | `FSSD`@65 + `HCO`@128, 131 B | *no match* | `no handler for file extension 'bin'` | |
| `l_act_257` | RIFF+`0x84`@256, 257 B | `act` | exit 2 | |
| `l_act_256` | RIFF, 256 B (byte 256 absent) | `wav` | wav reader `fmt chunk not found` exit 2 | |

Detected tally over the 27-row sweep: **act 8, gsrt 7, hcom 6, wav 3,
no-match 3**. `sox --i` exit codes on open failure are **1** (vs `sox -n stat`
exit **2**) — a signature asymmetry worth keeping in the record.

## Route/reader selected by each detection (all measured)

- **`gsrt`** → the native gsrt reader. On RIFF-shaped bodies it dies
  `premature EOF` (exit 2); on a 25-B carrier `invalid/missing file name in
  header`; on a zeroed 312-B carrier it *accepts* — `sox --i` prints
  `(gsrt)` + Channels 1 / 8 kHz / 14-bit / 8-bit u-law and stat reads 0
  samples, exit 0. **Reader outcome is body-dependent; detection is the
  only load-bearing claim.**
- **`hcom`** → the native hcom reader. On my near-zero families it dies at
  `bad sampling rate divisor`; on the author's r61-family member it dies at
  `bad compression type` — both strings are hcom-startread failures
  (adjacent in `libsox_ng.so.3` at `0xb65f1`/`0xb6606`, corroborative
  `strings` only); which guard trips is content-dependent. `--i` exits 1
  with that same error; no `(ffmpeg)` suffix ever appears.
- **`act`** → the ffmpeg pseudo-handler (r63): `popen ffmpeg … -f au -` →
  au reader on the pipe; `--i` shows the `(ffmpeg)` suffix + absent
  Duration on success.
- **`wav`** → native wav reader (r63 route baseline).

## Fall-through — detection is single-dispatch; a reader reject is terminal

Empirical, on bytes that *are* decodable by another route:

- `v_hcom84.wav` is a **fully valid WAV** (the signatures sit inside a JUNK
  payload): forced `sox -t wav v_hcom84.wav -n stat` → **exit 0** (stat
  completes), forced `sox -t act` → `premature EOF` exit 2 (ffmpeg child
  dies — see Finding 1), but the default route detects `hcom` → `bad
  sampling rate divisor` exit 2. Detection won, reader rejected, no
  re-detection, no fallback to `wav` — the decodable outcome is unreachable
  without a forced `-t`.
- `v_gsrt84.wav` default route detects `gsrt` → `premature EOF`; forced
  `-t wav` on the same bytes → `fmt chunk not found` (the `ring.bin` write
  overwrote the first subchunk's size field — the gsrt window is
  *structurally* incompatible with a valid RIFF table, Finding 2).
- Sibling corroboration (data, not rerun): r65-critic `strace` shows **0
  child execve** on gsrt-detected files (no ffmpeg spawned — the preemptor
  route is native-only), and its `D1_hcomdecode+act.wav` — a
  RIFF+WAVE+hcom-sigs+`0x84`@256 file whose body is a *valid* hcom — detects
  `hcom` and **decodes 9 samples @22050 Hz, exit 0** through the native hcom
  reader. My `n_gsrt` benign-accept (detected gsrt, opens, 0 samples, exit
  0) is the same direction weaker: *preemptor-detected ⇒ reader failure* is
  **false as a universal** — true only when the body isn't really that
  format.

## Findings beyond the ordering itself

1. **The hcom signature poisons ffmpeg's own prober.** `ffprobe -v debug`
   on `v_hcom84.wav` → `Format hcom probed with size=2048 and score=100`
   then `Invalid data found when processing input` (score 100 > wav's 99,
   matching the author's identical observation on `pair_preempt_hcom.wav`).
   Consequence: an hcom-collision file fails under *both* ecosystems — SoX
   native hcom and, counterfactually, the act/ffmpeg bridge (my `-t act`
   leg on `v_hcom84`/`v_hcom00` → `premature EOF`, 0 B). The only measured
   route that decodes it is forced `-t wav` (or `-f wav` under ffprobe →
   `pcm_s16le`). A lone conjunct (`v_fssd_only`, `v_hcom_only`) does not
   poison ffprobe — `wav`/`pcm_s16le`, exit 0.
2. **A gsrt-collision file can never be a valid RIFF.** Offsets 16-19 are
   structurally the *first subchunk's size field* in every RIFF container
   (RIFF+formtype = 12 B, chunk header @12-19). `ring.bin\0`@16-24 sets that
   size to `0x676e6972` (~1.73 GB) and overwrites payload start — SoX's wav
   reader then reports `fmt chunk not found` (mine) or
   `file encoding 0x622e (Unknown)` (author's family, where the write hits
   `wFormatTag`@20-21 = `"g."`), ffprobe `no 'fmt ' or 'XMA2' tag found` /
   `no 'data' tag found`. The hcom windows (65-68, 128-131) have no such
   structural constraint — they can hide inside any chunk payload, which is
   why `v_hcom84` is simultaneously a valid WAV and hcom-detected.
3. **gsrt reader-failure bisect (reader semantics, corroborative).** On a
   zeroed carrier + `ring.bin\0`@16: any nonzero byte at file offsets 0, 1,
   or 2 → `premature EOF`; offset 3 alone (`0x46`) → opens, 0 samples; size
   field @4-7 and `WAVE`@8-11 irrelevant (`x_gsrt_*` exhibits). This is
   consistent with r65-critic's source-level correction — bytes 0-3 are
   read as a big-endian `file_size` feeding the reader's checksum loop
   (`RIFF` = 1,380,533,830 → ~1.38 G int16 reads → real EOF); my byte bisect
   bounds the field to 0-2 sensitivity at this file size (offset 3 alone
   yields size ≤255 → 510 B of reads fits 312 B). Scout's "fixed header
   read running out" phrasing is superseded by the critic's mechanism.
4. **Error strings do not attribute the reader** (recorded verbatim from
   r65-critic, directionally consistent with my receipts): `premature EOF`
   is emitted by ≥3 different readers on this family (gsrt size loop, the
   au reader on an empty ffmpeg pipe, wav's longer `premature EOF on input
   file` warn) — on critic's `A5`, the gsrt-detected route and forced
   `-t act` emit *byte-identical* `premature EOF`; only the `-V4/-V6`
   `detected file format type` line (or an execve count) separates them.

## r63/r64 prior-behavior byte-stability (verified by this seat)

- `corpus/live/round-63/pair_route_84.wav` sha256
  `cf5edecce1812f0a0a5c1a16f0b2a920118be3f281b3f43638c1bc2f9f6b93e4` and
  `pair_route_00.wav` `cb77db319a7a791fa95ed14d83ab08f0c75b5c80635ec1897a9dea7c591c621a`
  — both equal `git show HEAD:` bytes exactly (worktree clean for those
  paths). Detection re-run verbatim: `pair_route_84` → `detected 'act'`,
  3,839 samples; `pair_route_00` → `detected 'wav'` → native
  `number of valid bits exceeds the number of bits per sample` exit 2.
- The r63 ledger rows (author claim, independently corroborated by
  r65-baseline): the r65 author's 96-command ledger replays the prior 92
  rows position-identical and **all 92 receipts byte-identical** to r64's;
  baseline's frozen-archive replay of the same 92 modes produced
  44 exit-0/48 exit-1 matching `ledger-r64.tsv`. My seat verified only the
  pair fixtures + detection line directly — ledger-replay claims are
  reported as sibling evidence.
- `corpus/live/round-64/pair_valid_*.wav` unchanged in git status (only
  `??`/`M` entries this round are r65 additions + pycache churn +
  `measure_audio.py`/`build_artifacts.py`).

## Tracked collision pair status (author's landing — verified as data)

Landed in the working tree, **uncommitted** at observation (`??` on
`corpus/live/round-65/`, `M` on the two fixture scripts; HEAD `b1e286c`):

- `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav` — the
  r61-family valid17 extensible WAV, all members `0x84`@256. `act` member is
  **byte-identical to r63 `pair_route_84.wav`** (sha `cf5edecc…` match, my
  `sha256sum`). Pair diffs (my `cmp -l`, 1-based): `act↔gsrt` = offsets
  17-25 only (the `ring.bin\0` span); `act↔hcom` = 66-69 + 129-132; `gsrt↔both`
  = 66-69+129-132. Every preemptor-wins pair's sole difference is its
  signature span — the "pair where the preemptor wins" deliverable is
  satisfied as the `{gsrt,hcom}↔{act}` and ordering pairs `{gsrt,hcom}↔{both}`.
- Probe modes `--probe-ui-preempt-{act,gsrt,hcom,both}-r65` wired in
  `measure_audio.py`; run receipts e.g.
  `corpus/live/runs/20261014T014333872621Z-ui-preempt-hcom-r65/measurements.json`
  record `sox_detected_format: "hcom"`, `sox_route: "native"`, stat
  `bad compression type`, bridge `premature EOF`, native `number of valid
  bits exceeds…` — matching my independent measurement of the same bytes.
- Commit slot: **[pending]** (parent integrates; this seat does not commit).

## Cross-seat consistency (converge/diverge verbatim)

- **Ordering: fully convergent across four independent constructions.**
  Author (19 variants, r61-family + 257-B shells): `gsrt ≺ hcom ≺ act ≺
  wav`, "No preemptor-shaped file routed act". Scout (20 probes): same
  order, same no-act outcome, plus post-act `avi`/`ftyp` collisions → `act`.
  Critic (33 variants): same order; no falsification of the ordering.
  Mine (36 files): identical order — including `both`-signature files
  detecting `gsrt` on every construction.
- **Critic's two falsifications are companion claims, not the ordering** —
  recorded verbatim: (a) "preemptor-detected ⇒ reader failure" is false
  (valid-hcom body decodes 9 samples); (b) `premature EOF` is not a reader
  attribution. My results.tsv's uniform exit-2 column on colliders is a
  property of *my fixture bodies*, not of detection — consistent with both.
- **Mechanism correction adopted:** critic's BE32 `file_size`@0-3 →
  checksum-loop reading of the gsrt `premature EOF` is corroborated by my
  `x_gsrt_b{0,1,2,3}` bisect (nonzero at 0-2 → EOF; at 3 → accept).
- **Error-string difference vs r63/author:** my hcom rows fail at
  `bad sampling rate divisor` where the r61-family fails at `bad
  compression type` — same reader, different first-tripped guard; reported,
  not a conflict.
- Reviewer: AGREE on all re-executed r64 claims + "zero latent preemptor
  collisions" in committed corpus (its `collision-scan.tsv` — none of the
  tracked fixtures accidentally carry the signatures).

## Draft: `corpus/knowledge/2026-10-14-sox-autodetect-preemptor-ordering.md` (content for parent decision — not landed)

```markdown
# SoX_ng preemptor ordering on RIFF files — gsrt ≺ hcom ≺ act ≺ wav (round 65)

- Source: round-65 seat evidence (`reports/round-65/r65-{author,scout,critic,
  scribe,reviewer,baseline}.md`; scribe's independent sweep
  `corpus/live/r65-scribe/results.tsv` + `variants/` + `logs/`); upstream
  sox_ng-14.8.0.1 `src/formats.c` (codeberg tag; local verified copy
  `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`) —
  source citations corroborative; all load-bearing claims empirical.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (USING_FFMPEG build), ffmpeg/ffprobe n9.0.1. Commit: [pending].
- Recheck when: SoX or ffmpeg version/build changes (the `act` row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  drop the act row entirely — ordering gsrt≺hcom≺wav survives but act
  disappears), when the CHECK table gains a pre-act row without an
  offset-0 anchor, or when fixture families change shape.

## Measured ordering result

`auto_detect_format` reads ≤257 B once (`AUTO_DETECT_SIZE 257 /* for act */
`, formats.c:61) and returns the FIRST matching CHECK row. On a RIFF file
(`RIFF`@0) the reachable pre-act rows are exactly two — every other row in
front of `act` anchors a non-RIFF literal at offset 0. Measured total order
(four independent fixture families, ~100 collision variants total):

    gsrt  ≺  hcom  ≺  act  ≺  wav
    :81      :90      :93     :95    (formats.c line order = match order)

- gsrt row: `CHECK(gsrt, 0,0,"", 16,9,"ring.bin")` — predicate
  `len ≥ 25 ∧ file[16:25] == "ring.bin\0"` (the C literal's terminating NUL
  at offset 24 is compared; a non-NUL 9th byte falls through to `act`).
- hcom row: `CHECK(hcom, 65,4,"FSSD", 128,4,"HCOM")` — predicate
  `len ≥ 132 ∧ file[65:69]=="FSSD" ∧ file[128:132]=="HCOM"` (both conjuncts
  required; either alone → `act`).
- act row: `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` — the r63 predicate
  `len ≥ 257 ∧ RIFF@0 ∧ file[256]==0x84`, unchanged.
- A file satisfying all three signatures detects **gsrt** (earliest row).
  Preemptors ignore byte 256 entirely (`*_00` members still detect
  gsrt/hcom — the preemptor even beats `wav` when `0x84` is absent).
- Length gates are exact: gsrt fires at len=25 not 24; hcom at 132 not 131;
  act at 257 not 256.

## Downstream route per detection (single dispatch, no fallback)

| detected | handler | observed on collision bodies |
|---|---|---|
| `gsrt` | native gsrt reader | RIFF body → `premature EOF` exit 2 (reader treats bytes 0-3 as a BE `file_size` feeding a read/checksum loop — `RIFF`≈1.38 G > file); 25-B carrier → `invalid/missing file name in header`; zeroed 312-B carrier → **accepts**: `--i` `(gsrt)` 1ch/8kHz/14-bit/μ-law, 0 samples, exit 0 |
| `hcom` | native hcom reader | near-zero body → `bad sampling rate divisor`; r61-family body → `bad compression type` — both are hcom-startread guards (which trips is content-dependent); a genuinely valid-hcom body decodes (critic: 9 samples @22050 Hz) |
| `act` | ffmpeg pseudo-handler | `popen ffmpeg -f au` → au reader; `--i` `(ffmpeg)` + no Duration line |
| `wav` | native wav reader | normal r63 baseline |

`sox <f> -n stat` exits **2** on open failure; `sox --i <f>` exits **1** on
the same failure — the `--i` asymmetry is measured, not a typo.

## Fall-through behavior (preemptor detects but reader rejects)

Terminal — no re-detection, no second handler, no fallback to `act`/`wav`
(r63 single-dispatch chain confirmed on the collision family):
`v_hcom84.wav` (a fully valid WAV whose hcom signatures sit inside a JUNK
payload) detects `hcom` → `bad sampling rate divisor` exit 2, while the
same bytes decode cleanly under forced `-t wav` (exit 0). The preempted
verdict is *the detected reader's verdict on a malformed body*, not an
ordering property — error strings are content-dependent (`premature EOF`
alone is emitted by ≥3 readers on this family and does NOT attribute the
route; only the `-V4/-V6` `detected file format type` line does).

Two structural corollaries, both measured:

- **hcom collision is ffmpeg-fatal too.** ffmpeg's prober independently
  scores `hcom` 100 > `wav` 99 on the same FSSD@65+HCOM@128 bytes, so a
  hcom-shaped file fails even under the counterfactual `-t act` bridge
  (`premature EOF` — ffmpeg child emits nothing). The only measured
  decode route is forced `-t wav` / `-f wav`.
- **gsrt collision is never WAV-valid.** Offsets 16-19 are structurally the
  first subchunk's size field in every RIFF file; `ring.bin\0` there sets
  it to `0x676e6972` (~1.73 GB), so `-t wav` fails `fmt chunk not found` /
  `file encoding 0x622e`, ffprobe `no 'fmt '…`/`no 'data' tag found`. The
  hcom windows (65-68, 128-131) are unconstrained — they can hide inside
  any chunk payload.

## Relation to the r63 act predicate and the r64 step map

- The r63 predicate stands verbatim; r65 completes its quantifier: the
  "no earlier row matched" conjunct is now a measured total order, not an
  enumerated-candidate claim. The full detect rule on this build:
  `detected == first matching row of (voc,smp,wve,gsrt,amr-wb,prc,sph,
  amr-nb,txw,sndt,vorbis,opus,hcom,act,wav…)` where on a `RIFF`@0 file only
  {gsrt, hcom, act, wav, avi-family} can match, and the measured winner
  order is gsrt < hcom < act < wav < (post-act rows — act still beats
  `avi`/`ftyp` collisions).
- The r64 valid-bits→codec step map is unchanged and *unreached* under a
  preemptor collision: it applies only after `act` wins the table. A
  collided vb-family file never reaches ffmpeg — e.g. tracked
  `pair_preempt_hcom.wav` (a vb17 file) is claimed by hcom before the
  vb17-vs-16 question can arise.
- Fixture-authoring rule extends: a payload signature at 16-24 or
  (65-68,128-131) reroutes detection regardless of byte 256. The tracked
  collision family `corpus/live/round-65/pair_preempt_{act,gsrt,hcom,both}.wav`
  (probe modes `--probe-ui-preempt-*-r65`) pins it; `pair_preempt_act.wav`
  is byte-identical to `round-63/pair_route_84.wav` (sha256 `cf5edecc…`).

## Bounded UNKNOWNs retained

- Reader acceptance semantics of gsrt/hcom beyond the exercised bodies
  (valid-hcom decode is one critic sample; gsrt accepted only a degenerate
  zero carrier). Real-world well-formed gsrt/hcom corpus untested.
- stdin/pipe detection on colliders (one critic probe only); `--magic`
  path (off by default) untested this round.
- Non-ffmpeg SoX_ng builds: ordering derived on a USING_FFMPEG build; on a
  132-byte-window build the act row vanishes (hcom becomes the deepest
  RIFF-reachable preemptor).
- Other hosts/versions; plugin-registered formats could add CHECK rows
  (none installed here).
- Exact hcom reader guard order between `bad sampling rate divisor` and
  `bad compression type` is content-keyed; not exhaustively mapped.

## Falsifiable recheck conditions

1. `sox -V4 corpus/live/round-65/pair_preempt_both.wav -n stat 2>&1 | grep
   detected` must print `gsrt` — any `hcom`/`act`/`wav` reading falsifies
   the ordering (member sha256 `a37adc7c…`; commit slot [pending]).
2. `sox -V4 pair_preempt_{gsrt,hcom}.wav -n stat` must detect `gsrt`/`hcom`
   and exit 2 on this fixture body; `pair_preempt_act.wav` must detect
   `act` and read 3,839 samples.
3. Rebuild determinism: `build_ui_preempt_r65_probe()` must reproduce the
   four members byte-identically (`cmp` vs committed blobs).
4. Any SoX/ffmpeg version change → rerun this file's probes
   (`corpus/live/r65-scribe/sweep.sh` regenerates the detection matrix);
   CHECK-table additions or a resized `AUTO_DETECT_SIZE` invalidate the
   ordering claim at the first differing row.
```

## Draft: LOG.md round-65 entry text (for parent integration)

```markdown
## Round 65 scribe — preemptor ordering independently re-derived; convergent
- `reports/round-65/r65-scribe.md`: independent 36-file probe sweep under
  `corpus/live/r65-scribe/` (own constructions: 312-B valid-WAV JUNK-pad
  family, bare-RIFF shells, non-RIFF carriers, exact length gates) —
  measured total order `gsrt ≺ hcom ≺ act ≺ wav`, zero act-routed
  colliders; hcom sigs inside a *valid* WAV preempt it (`bad sampling rate
  divisor`, `-t wav` decodes clean — single-dispatch, no fallback); ffmpeg's
  own prober also claims hcom-signature files (score 100 > wav 99) so even
  the bridge can't decode them; gsrt sig necessarily corrupts the RIFF
  chunk table (16-19 = first-chunk size). r63 pair fixtures sha-verified
  byte-identical to HEAD + detection re-run clean; author's tracked
  `pair_preempt_*` family re-verified (act member == r63 pair_route_84;
  both → gsrt). Cross-seat: convergent with author/scout/critic on
  ordering; critic's two companion-claim falsifications (reader accept is
  body-dependent; `premature EOF` isn't a reader attribution) recorded
  verbatim, consistent with scribe's n_gsrt accept + byte-0-3 bisect.
```

## Commands / observed outputs (receipt excerpts; full receipts in `corpus/live/r65-scribe/`)

- `python3 gen_variants.py` → 27 fixtures + `variants/manifest.tsv` (all
  sha256 listed); Family V asserts `out[256]==b256` per member; JUNK
  payload bounds file offsets 65-68/128-131.
- `bash sweep.sh` → `results.tsv` 27 data rows; per file: `sox -V4 <f> -n
  stat` (detected line + exit), `sox --i`, `sox <f> -t f32 -` (bytes+exit),
  `ffprobe -v error -show_entries format=format_name:stream=codec_name`,
  forced `sox -t {wav,act,gsrt,hcom} <f> -n stat` / `-t f32 -`.
- Spot verbatim: `logs/v_hcom84.wav.stat.err` → ``detected file format type
  `hcom'`` then `FAIL … bad sampling rate divisor`; `logs/v_hcom84.wav.twav.err`
  → stat completes (exit 0, no FAIL); `logs/v_gsrt84.wav.twav.err` →
  `fmt chunk not found`; `logs/n_gsrt.bin.i.out` → `(gsrt)` + `Precision:
  14-bit` / `8-bit u-law`; `logs/l_gsrt_25.bin.stat.err` → `invalid/missing
  file name in header`.
- ffprobe: `ffprobe -v debug v_hcom84.wav` → `Format hcom probed with
  size=2048 and score=100` → `Invalid data found when processing input`;
  `ffprobe -f wav v_hcom84.wav` → `codec_name=pcm_s16le format_name=wav`;
  `ffprobe b_gsrt84.wav` → `[wav] no 'fmt ' or 'XMA2' tag found`.
- Bisect (`x_gsrt_*`): nonzero at file offsets 0/1/2 → `premature EOF`;
  offset 3 alone or bytes 4-11 alone → gsrt opens, `Samples read: 0`.
- r63 re-verify: `sha256sum corpus/live/round-63/pair_route_*.wav` ==
  `git show HEAD:` bytes; `sox -V4 pair_route_84.wav -n stat` → `act`,
  `Samples read: 3839`; `pair_route_00.wav` → `wav`, valid-bits FAIL.
- Author-family re-verify: `cmp -l` pair diffs (17-25 / 66-69+129-132);
  `sox -V4 pair_preempt_both.wav` → `detected 'gsrt'` → `premature EOF`.

## Eliminated hypotheses

- "A preemptor-shaped RIFF file still routes act" — **eliminated** on 36
  files + author's 4 tracked members + siblings' ~70 rows: every matching
  preemptor claims the file; the declared ordering claim survives.
- "0x84@256 participates in the preemptor decision" — eliminated by the
  `*_00` members: gsrt/hcom rows fire regardless of byte 256 and even beat
  `wav` (`v_hcom00` detected hcom on a byte256=0x00 valid WAV).
- "hcom needs only one conjunct" — eliminated: `v_fssd_only`,
  `v_hcom_only` → `act`; author's `x131`/`x65` one-byte-off rows → `act`.
- "The 9-byte gsrt literal ignores its NUL" — eliminated: `b_gsrt_badnul`
  (byte24=`0x2e`) → `act`.
- "Detection failure implies extension fallback can rescue" — `.bin`
  carriers with no matching CHECK → `no handler for file extension 'bin'`
  exit 2 (l_gsrt_24, l_hcom_131, n_zero).

## Retained bounded UNKNOWNs

- gsrt/hcom reader acceptance beyond exercised bodies (one valid-hcom
  decode from critic; my gsrt accept was a degenerate 0-sample carrier).
- Which byte offsets hcom's `bad sampling rate divisor` guard reads —
  content-keyed, unmapped by this seat (source cites corroborative only).
- stdin/pipe detection path on colliders (critic probed one stdin case;
  my sweep is regular files only).
- Whether SoX's wav reader ever tolerates the `ring`-sized first chunk via
  EOF clamping on other content shapes — observed failures only.
- ffmpeg probe-score details beyond the observed hcom=100/wav=99 outcome;
  gsrt does not exist as an ffmpeg demuxer so no ffmpeg-side gsrt contest.

## Touched surfaces / out-of-scope

- Wrote: `reports/round-65/r65-scribe.md`; `corpus/live/r65-scribe/`
  (`gen_variants.py`, `sweep.sh`, `results.tsv`, `variants/` 36 files incl.
  `manifest.tsv`), `logs/` 432 receipt files). All inside the brief's write
  scope via the `.shokunin/audio` symlink.
- Read-only: `corpus/live/round-{62,63,64,65}/`, sibling `r65-*` scratch,
  `reports/round-*/`, `corpus/fixtures/measure_audio.py`,
  `corpus/live/r64-reviewer/r64rev-formats.c`, `/usr/lib/libsox_ng.so.3`
  (`strings` corroboration only).
- Not done (out of scope / not mine): no commits/pushes; no edits to
  tracked fixtures, probe modes, LOG/SCORECARD/knowledge files (drafts
  above are parent-decision content); no runner invocation (no `--runs`;
  avoids shared `live/runs/` writes); no disasm-as-evidence (binary strings
  cited corroboratively); no claims beyond this host's toolchain.
```

Stop: report complete; no further action.
