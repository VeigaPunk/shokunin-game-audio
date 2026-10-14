# R66 critic — attack the completed preemptor map on RIFF+0x84@256

Seat: critic. Target: the r66 declared move (identify wve's byte predicate,
decide whether a wve-shaped RIFF file preempts gsrt/hcom/act, land tracked
DECODABLE-preemptor pair + gsrt 24|25 and hcom 131|132 lengate members).
Host: SoX_ng 14.8.0.1 (`/usr/bin/sox`), ffmpeg/ffprobe n9.0.1, strace.
Worktree `~/Projects/prymeagnt/audio` → canonical `~/Projects/shokunin/
audio-shokunin`; all artifacts under `corpus/live/r66-critic/` (`gen.py`
~50-variant generator, `probe.sh`, `results.tsv` 95 rows, `var/` exhibits,
`shas.txt`). No tracked files touched; no commits.

**Author-landing status**: the tracked diff is on disk uncommitted —
`corpus/fixtures/{build_artifacts,measure_audio}.py` (+113/+93 lines,
201 insertions/5 deletions per `git diff --stat`,
six `--probe-ui-{dec,lengate}-*-r66` flags) plus six fixture wavs under
`corpus/live/round-66/` (untracked, pending commit — same convention as
r63/r65 whose pair wavs are now tracked). The author's `compare_receipts.py`
run: **96 prior-mode pairs checked, 0 mismatches** (ledger-r66 rows 1,8-102
vs ledger-r65 rows 1-96, byte equality). All three run generations of each
new r66 receipt are byte-identical on this host.

## Verdict

**The completed map SURVIVES every attack — with one framing correction and
three new mechanism facts.** On RIFF+0x84@256 the detect order is
`gsrt` < `hcom` < `act` < `wav`, first-match-wins, no fallthrough. The wve
row (formats.c:80, before gsrt:81) is real but **cannot enter the contest on
RIFF files**: `ALawSoundFile**`@0-14 collides with `RIFF`@0 at byte 0. A
"wve-shaped RIFF file" is impossible-by-construction — the ordering question
is *vacuous on the declared domain*; wve precedence is only exercisable on
non-RIFF carriers, where it wins unconditionally.

**Three new facts the round's evidence should carry:**

1. **The act route on a stdin pipe is structurally broken in sox_ng** —
   `cat pair_dec_act.wav | sox - -n stat` → detected `act` → instant
   `can't find Sun/NeXT/DEC identifier`, exit 2, and strace proves the au
   reader fails *before ffmpeg's first write* (ffmpeg's `.snd` write gets
   EPIPE; it had all 600 bytes and produced valid au in isolation). The
   257-byte autodetect prefetch (`pending_bytes`) is replayed into the
   ffmpeg bridge's au reader — the pipe path never reaches ffmpeg's output.
   `sox -t act -` on the identical pipe decodes 278 samples fine.
   On a named fifo it is worse: the handler spawns
   `ffmpeg -i /tmp/fifo -f au -`, ffmpeg blocks in `open()` needing a
   second writer — an indefinite hang that outlives a killed sox.
2. **gsrt's reader floor (34 B) exceeds its detector floor (25 B).** Band
   [25,33] detects gsrt on every fd yet can never complete the reader's
   header walk (4+12+16+2). On `pair_lengate_gsrt_25` the stderr flips
   `premature EOF` (file) → `invalid/missing file name in header`
   (pipe/fifo) — the checksum-loop skip made visible on a tracked member.
3. **hcom's checksum and huffcount-residue checks are dead on the read
   path.** A wrong `checksum`@136 field still exits 0 with 9 samples;
   `huffcount`=1 → 1 sample exit 0; mid-data EOF emits a FAIL line
   (`unexpected EOF in HCOM data`) **yet exits 0**. The acceptance
   boundary is exactly the startread field walk:
   `compresstype≤1 ∧ 1≤divisor≤4 ∧ 1≤dictsize≤511 ∧ dictvalid ∧ bytes
   available`.

## Attack 1 — wve ordering: single winner? can wve ever lose?

Byte predicate (three independent constructions agree — author W01-W26,
scout P01-P10/V01-V03, boundary a_*/my Q*): `ALawSoundFile**`@0-14, all 15
bytes compared (every single-byte flip at 0-14 kills detection), byte 15
free, gate `len ≥ 15` (14 → no match). formats.c:71-96 corroborates:
`CHECK(wve, 0,0,"", 0,15,"ALawSoundFile**")` at row 80; detection buffer is
257 B when `USING_FFMPEG` (132 otherwise — act row is compiled out there).

| variant | signatures present | detected | outcome |
|---|---|---|---|
| `Q1_wve+gsrt+hcom+84.bin` | wve@0, ring.bin\0@16, FSSD@65, HCOM@128, 0x84@256 | **wve** | `can't find Psion identifier`, exit 2 |
| `Q2` same bytes, `.wav` name | identical | **wve** | same (content precedes extension) |
| `Q3_wveDEC+hcom+84.bin` | valid Psion id + FSSD/HCOM/0x84 in payload | **wve** | **decodes 268 samples**, exit 0; `-t hcom` also decodes 9 on the same bytes |
| `Q4_riff_named_wve.wve` | RIFF file named `.wve` | **wav** | 128 samples, exit 0 |
| `Q5_wveVALID15+gsrt+hcom+84.bin` | = Q1 bytes (gsrt@16 kills Psion id anyway) | **wve** | `can't find Psion identifier` |

- **Quad-collision**: `wve ∧ gsrt ∧ hcom ∧ act` is unconstructable — act
  needs RIFF@0, wve needs `ALaw...`@0. The maximal collision
  (wve∧gsrt∧hcom∧0x84, no RIFF) → wve, every time (mine Q1; author W03;
  scout Q02; boundary b_wve_gsrt_hcom). No witness exists where wve's
  predicate holds and a later row wins: the only earlier rows are voc:78
  (`Creative Voice File\x1a`@0) and smp:79 (`SOUND SAMPLE DATA`@0), both
  byte-0-incompatible with 'A'.
- **wve never loses** — and it also has its own detect-only band: detector
  needs 15 B but the reader checks an 18-byte Psion id
  (`...\x00\x0f\x10`@15-17) → `a_wve_magic15`/`P02` die `premature EOF`,
  `a_wve_badid`/`P01` die `can't find Psion identifier`.
- **Corollary for the declared domain**: of all rows before act
  (voc/smp/wve/gsrt/amr-wb/prc/sph/amr-nb/txw/sndt/vorbis/opus/hcom), every
  @0-magic conflicts with 'R'; only gsrt@16-24 and hcom@65+128 can collide
  with RIFF+0x84. The map's completeness claim is provable: the preemptor
  set on this domain is exactly {gsrt, hcom}; wve is *excluded*, not merely
  *ordered-earlier*.

## Attack 2 — is the 9-sample hcom decode stable? same-signature different-fate?

All 19 H-variants share the identical detection signature (RIFF@0,
FSSD@65-68, HCOM@128-131, 0x84@256) → **every one detected `hcom`**.
Fates diverge entirely inside the reader's field walk:

| variant | field changed | result |
|---|---|---|
| `H00_base_decode9` | (=tracked pair_dec_hcom, sha-identical) | **9 samples @22050, exit 0** |
| `H01_compresstype1` | 0→1 | 9 samples, exit 0 (delta-coding → different values) |
| `H02/H03` divisor | 1→2/4 | 9 samples @11025/5512, exit 0 |
| `H04/H05` divisor | 5 / 0 | **`bad sampling rate divisor`**, exit 2 |
| `H06_compresstype2` | 0→2 | **`bad compression type`**, exit 2 |
| `H07/H08` dictsize | 0 / 512 | **`implausible dictionary size`**, exit 2 |
| `H09_invaliddict` | dict[0]=(5,5) out-of-range | **`invalid dictionary`**, exit 2 |
| `H18_dictsize1` | 2→1, entry(-1,0) | **`invalid dictionary`**, exit 2 |
| `H10_badchecksum` | @136 = 0xDEADBEEF | **9 samples, exit 0** — checksum never checked on read |
| `H11` huffcount=10 | | 10 samples, exit 0 (1 bit/leaf dict ⇒ bit-per-sample) |
| `H12` huffcount=1 | | 1 sample, exit 0 — residue ignored |
| `H13` huffcount=0 | | 0 samples, exit 0 |
| `H14/H15` first byte / datum | | 9 samples, exit 0 (values change) |
| `H16` datasize/rsrcsize@83-90 | ramp→junk | 9 samples, exit 0 — **read but never validated** |
| `H17` pad@158 | 0→0x99 | 9 samples, exit 0 — skipped, unchecked |
| `H19` huffcount=40 truncated@200 | | 40 samples, exit 0 (enough ramp words) |
| `H21` huffcount=4000 | | 0 samples, **FAIL `unexpected EOF in HCOM data`, exit 0** |

So the decodable member's acceptance is **field-contingent, not
signature-implied**: `FSSD∧HCOM∧RIFF∧0x84` buys detection only; the reader
then independently gates on ~20 more bytes the CHECK row never reads.
Same-signature different-fate pairs are trivial (H00 vs H04/H06/H07/H09 —
identical detection, four distinct die positions). The tracked pair proves
detect→decode once; my H-family shows the complement "detected hcom ∧
reader rejects" on the same signature — complementary, not contradicting.

Also verified: `-t hcom` on `pair_dec_act` dies `Mac header type is not
FSSD` — the sole @68 demotion byte is exactly the reader's first check;
`-t wav` on `pair_dec_hcom` decodes 278 samples (the suppressed PCM16
skeleton is genuinely valid underneath — same dual-decode shape as r65
D1, byte-identical: `325fb967f0c9` both).

## Attack 3 — seekability on the tracked members (file / stdin-pipe / fifo)

| tracked member | regular file | stdin pipe (`cat f \| sox -`) | fifo |
|---|---|---|---|
| `pair_dec_hcom` | hcom, **9 samples**, exit 0 | **identical** | identical |
| `pair_dec_act` | act→bridge, **278**, exit 0 | act→**instant FAIL** `can't find Sun/NeXT/DEC identifier`, exit 2 | act→ffmpeg `open()` **deadlock** (then au FAIL if killed) |
| `pair_lengate_gsrt_25` | gsrt→`premature EOF`, exit 2 | gsrt→`invalid/missing file name in header`, exit 2 | same as pipe |
| `pair_lengate_gsrt_24` | wav→`fmt chunk not found`, exit 2 | identical | identical |
| `pair_lengate_hcom_132` | hcom→`premature EOF`, exit 2 | identical | identical |
| `pair_lengate_hcom_131` | wav→43 samples, exit 0 | identical | identical |

- **gsrt checksum-loop skip is tracked-visible**: same bytes, same `gsrt`
  detection and exit 2, but the die position flips — file dies in the
  checksum loop (`RIFF`@0 = file_size 1.38 G); pipe skips it and dies at
  the 16-byte id read (needs bytes 16-31, file has 25). The G-sweep pins
  the reader floor at **34 B**: `G_sz0_len{25..31}` → `invalid/missing
  file name` (id read short); `{32,33}` → `premature EOF` (encoding read
  @32-33 short); `{34,...}` → **0 samples, exit 0** — the 478-byte padding
  skip's EOF is unchecked and degrades to an empty decode.
- **dec_act's bridge is regular-file-only for a sox-side reason**: the
  autodetect prefetch stashes 257 B in `ft->pending_bytes`; the fork-child
  regurgitates them into ffmpeg's stdin (correct), but the parent's
  `pending_bytes` are *also* drained by the bridge's own au reader — it
  reads "RIFF…" where `.snd` must be and fails before ffmpeg's first
  output byte (strace: parent FAILs before execve'd ffmpeg writes;
  `.snd` → EPIPE). Forced `-t act` skips autodetect → works (278).
  `-t wav` on the same pipe also works (278). The bug reproduces on the
  r65 `pair_preempt_act` member — it is input-independent.
- Receipt impact: detection/exit/sample fields are fd-stable for every
  member; only stderr-tail fields would differ on a pipe. The harness
  always measures regular files → the tracked receipts are stable; the
  fd-dependence is latent, not receipt-breaking.

## Attack 4 — NUL@24: detector demands it, reader ignores it

gsrt.c: `id[16]="ring.bin"`; reader reads 16 bytes @16-31 then
`memcmp(read_id, id, strlen(id))` — **8 bytes**. The detector's 9th byte
(the C literal's terminator NUL@24) is never consulted by the reader.

- `N5_badnul_riff84_enc0.wav` (RIFF+0x84, `ring.binX`@16-24 X=0x41,
  ULAW code 0 @32-33): autodetect → **act** (NUL conjunct fails) → bridge
  `premature EOF`; `cat | sox -t gsrt -` → **88 samples, exit 0**.
  Detector rejects, reader accepts — same bytes.
- `N6` (same, byte24=NUL): detected `gsrt`; pipe decodes identically —
  the sole divergence byte changes *routing*, not *reader-acceptance*.
- `N2_badnul_sz0.bin` (file_size=0 → no checksum wall even on file):
  `-t gsrt` decodes 88 samples while detection finds *no* row.
- Tracked relevance: the divergence needs ≥34 B (reader floor); the
  tracked `pair_lengate_gsrt_24` (24 B) is below it, so the member cannot
  exhibit the asymmetry — detection-demotion and reader-rejection coincide
  there. The asymmetry is real but lives in a size band the pair
  deliberately avoids.

## Attack 5 — ledger's new rows: receipt nondeterminism

- **Absolute paths embedded** in `sox_stderr`/`sox_stat_stderr`/
  `sox_bridge_stderr`/`sox_native_stderr` of the three failing members —
  e.g. `…pair_lengate_gsrt_24.wav: Invalid data found when processing
  input`. **Pre-existing convention**: r65 receipts embed the same and were
  admitted; the r66 baseline's `semantic_compare.py` already normalizes on
  the `corpus/` anchor. On this host all three run generations are
  byte-identical; cross-host they are location-dependent. Note, not new.
- `measure_error: "KeyError: 'duration'"` (dec_hcom) — deterministic on
  this toolchain (3×identical). The `decode_error_tool:
  "measure_pipeline"` branch is new code; it records a *schema crash*
  (`probe["format"]["duration"]` missing on hcom) **after both decodes
  succeeded** — ffprobe parsed the stream and sox emitted 36 f32 bytes.
  The failure tag `decode: standard measurement pipeline rejected input`
  flattens two different events (gsrt/hcom lengate members = real decode
  rejection; dec_hcom = schema gap post-decode). The positive evidence is
  correctly captured in `sox_stat_samples_read:9`, `sox_f32_bytes:36`,
  `sox_detected_format:"hcom"` — the label is cosmetic but a naive reader
  could mistake the decodable member for a fail-side one. Fixable wart.
- `sox_route` retains the r65 `(ffmpeg)`-substring fallback that cannot
  fire on failed opens — harmless dead logic, detected-format is
  authoritative.
- `dec_hcom --i` exits 1 (hcom omits Duration) — per-handler quirk already
  recorded in r65.
- The ledger TSV itself embeds absolute receipt paths — scratch file,
  untracked, fine.
- Tracked `__pycache__/{build_artifacts,measure_audio}.cpython-314.pyc`
  differ — the same mechanical py_compile churn flagged in r62/r63/r65;
  flag for adjudicator.

## Fixture verification (re-measured, not trusted)

- `pair_dec_hcom` sha256 `325fb967…` — **byte-identical to r65-critic's
  D1**; my `H00` rebuild reproduces it exactly. Decode: 9 samples
  (-0.5, -1.0×8) @22050 Hz, `(hcom)`/`8-bit HCOM` on `--i`, exit 0, on
  file+pipe+fifo identically.
- `pair_dec_{hcom,act}`: `cmp -l` = sole byte @68 `'D'→'E'` — exact
  declared demotion. `-t hcom` on act member dies at the FSSD check.
- lengate members: gsrt 24|25 → `wav`/`gsrt`; hcom 131|132 → `wav`(43
  samples)/`hcom` — gate exact. RIFF size fields self-consistent per
  member (size@4=n−8; dataSize@40=n−44 where n≥44).
- Same-class third gate, unmeasured-in-pair (scratch): act's own len gate
  `256|257` — `A_gate256.wav`→wav 106 samples; `A_gate257_84`→act;
  `A_gate257_00`→wav.
- Scripts: `ast.parse` clean on both; `git diff --check` clean; six flags
  in add_argument, sum() mutual-exclusion, command passthrough, member
  chain, mode chain, suffix chain — all six sites present (`hcom_132`
  is the member chain's else-tail — pattern, not a defect).
- Prior-ledger byte-stability: author's `compare_receipts.py` re-run by
  me → 96 pairs, 0 mismatches.

## Impacted axes

- **claim-fidelity**: ordering map CONFIRMED on RIFF+0x84@256 —
  {gsrt<hcom<act<wav}; wve's precedence is real but *vacuous on this
  domain* (byte-0 exclusion) and unconditional on non-RIFF. The "wve
  preempts" clause should be phrased as exclusion, not ordering, on RIFF.
- **depth**: decodable-preemptor outcome is fd-conditional for the act
  route (pending_bytes→au-reader leak on `-`; ffmpeg `open()` deadlock on
  fifo) and fd-invariant for hcom. hcom checksum/huffcount residue =
  dead checks on read path; read-phase `unexpected EOF` FAILs exit 0.
- **coverage**: ~50 discriminating variants (51 files in `var/`,
  shas pinned), +forced-type legs, +pipe/
  fifo legs on all six tracked members, +strace-attributed act-pipe
  failure, +gsrt reader-floor sweep 25-512, +act len gate 256|257.
- **calibration**: die-position map extended — `invalid/missing file name`
  on a gsrt RIFF file now means "checksum skipped, id read short"
  (non-seekable, or file_size<2); `can't find Sun/NeXT/DEC identifier` on
  `sox -` means prefetch-poisoned au reader, *not* an au verdict on the
  input; hcom FAIL-with-exit-0 exists (read-phase EOF).
- **byte-stability**: clean — 96/96 prior receipts identical; 3× identical
  new receipts; scratch-only writes by this seat.

## Smallest safe correction

1. Keep the map as measured: on RIFF+0x84@256 the contestable preemptors
   are exactly {gsrt<hcom} before act; record wve as *excluded by byte-0
   exclusivity* on this domain (it preempts unconditionally on non-RIFF).
2. Amend the outcome clause: "that preemptor's reader successfully
   decodes" → "…on a regular file; the act bridge additionally requires
   a seekable path (stdin-pipe autodetect→act is broken upstream; fifo
   hangs in ffmpeg open())". dec_hcom needs no qualifier.
3. No tracked-diff change required — all found defects are environmental
   (sox quirks), not fixture defects. The two cosmetic notes for the
   receipt schema: (a) the `decode: … rejected input` tag also covers a
   post-decode schema crash — consider `"measure pipeline could not
   complete"` wording for the `measure_pipeline` branch; (b) absolute
   paths in stderr fields remain an accepted convention (baseline
   already normalizes).
4. Optional pair-budget note: the act len gate 256|257 is the same class
   the lengate family pins (measured in scratch); a 25-33 B gsrt member
   would be detect-only by construction — the reader floor is 34 B, not
   the detector's 25.

## Receipts

- `corpus/live/r66-critic/{gen.py,probe.sh,results.tsv,shas.txt,var/}` —
  38 variants, 95 probe rows. Key shas: `H00`/`S_pair_dec_hcom`
  `325fb967f0c9` (=tracked), `N5_badnul_riff84_enc0` (act-detected,
  `-t gsrt` pipe decodes 88), `Q1` `1ea0071e82d2` (max collision→wve),
  `G_sz0_len34` `2ab6f1cfae22` (reader floor, 0-sample decode).
- Commands verbatim: detection `sox -V6 <f> -n stat`; pipe `cat <f> |
  sox -V6 - -n stat`; forced `sox -t <fmt> <f> -n stat`; fifo
  `mkfifo /tmp/r66fifo`; strace `-f -e trace=read,write,dup2,clone,execve,pipe`;
  ffmpeg isolation `cat <f> | ffmpeg -loglevel quiet -nostdin -strict -2
  -i - -f au - | xxd`.
- Source (corroborative only): `/tmp/sox_ng_src/sox_ng/src/formats.c`
  CHECK rows (wve:80, gsrt:81, hcom:90, act:93, wav:95-97),
  `AUTO_DETECT_SIZE`=257/132 by USING_FFMPEG; `formats_i.c`
  `lsx_readbuf_rewind` pending_bytes :178-216; `ffmpeg.c`
  `startread_ffmpeg` fork/regurgitate :32-107; `gsrt.c` start_read
  (file_size dw, `file_size>=2 && seekable` checksum loop, skip 12,
  16-byte id read, 8-byte memcmp, unchecked PADDING_SIZE 478);
  `hcom.c` field walk + `stopread` checksum/`huffcount` checks;
  `wve.c` 18-byte Psion id.
