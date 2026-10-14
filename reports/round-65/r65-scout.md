# r65 — scout — audio lane — preemptor-collision autodetect ordering

Move (verbatim): "map the pre-act autodetect preemptor ordering on RIFF files:
the r63-pinned act predicate (len>=257 AND RIFF@0 AND file[256]==0x84) is one
CHECK row among several — the r62 seats recorded preemptor candidates gsrt
(signature 'ring.bin\0' @16) and hcom ('FSSD'@65 AND 'HCOM'@128). Construct
minimal RIFF+0x84@256 files that ALSO match each preemptor's predicate; measure
empirically which detection wins and what reader/route it selects (decode, sox
--i, ffprobe comparison, exit codes); if a preemptor-shaped file still routes
act, that ordering claim is falsified and must be recorded as such. Pin at
least one tracked RIFF-preemptor collision control pair where the preemptor
wins; keep all prior behavior including the r63 ledger rows and pair fixtures
byte-stable; derive everything empirically (probes) — disasm/source citation is
corroborative only."

Seat: scout (recon only). Writes: this report + `corpus/live/r65-scout/`
({make_probes.py, measure.sh, probes/, runs/}). No tracked edits, no commits.
Host: devin; worktree `~/Projects/prymeagnt/audio` (`.shokunin/audio` →
canonical `~/Projects/shokunin/audio-shokunin`, HEAD `b1e286c` r64
adjudication). Toolchain: SoX_ng v14.8.0.1 (`/usr/lib/libsox_ng.so.3.0.0`),
ffmpeg/ffprobe n9.0.1, strace, objdump, python3. No `lsp` device exists in this
seat's toolset — source citations are from the fetched local copy
`corpus/live/r64-reviewer/r64rev-formats.c` (upstream tag sox_ng-14.8.0.1,
r64-reviewer receipt) and are corroborative only; all load-bearing claims are
empirical on this host's binary.

## Verdict

**Ordering claim CONFIRMED, not falsified — measured on 20 probes.** Every
file satisfying a preemptor predicate was detected as the preemptor, never as
act. Empirical order on this host:

    gsrt  <  hcom  <  act  <  wav  <  (all remaining rows)
    :81       :90     :93    :95      formats.c source-line order

first-match-wins in both directions: preemptor rows claimed
RIFF+0x84@256+preemptor-magic files, while files matching act **and** a
post-act row (avi `RIFF+AVI@8`, mp4-family `ftyp*@4`) still detected `act`.
Detected-handler open failure is terminal in all cases — no fallthrough to act
or wav (exit 2 throughout).

## Deliverable 1 — ordered candidate list, byte-level predicates

`auto_detect_format` reads `len ≤ 257` bytes once (`AUTO_DETECT_SIZE 257 /* for
act */` in this USING_FFMPEG build) and returns the first row whose
`len >= p1+l1 && memcmp(data+p1,d1,l1)==0 && memcmp(data+p2,d2,l2)==0`. Len gate
covers only the deeper (p1) field. Row order = source order; pre-act rows
(formats.c:78-93, verified against local copy + binary disasm):

| # | row | predicate (fields, offsets) | len gate |
|---|---|---|---|
| 1 | voc | `"Creative Voice File\x1a"` @0-19 | 20 |
| 2 | smp | `"SOUND SAMPLE DATA"` @0-16 | 17 |
| 3 | wve | `"ALawSoundFile**"` @0-14 | 15 |
| 4 | **gsrt** | `"ring.bin\0"` @**16-24** (9 B incl. NUL) | **25** |
| 5 | amr-wb | `"#!AMR-WB\n"` @0-8 | 9 |
| 6 | prc | `\x37\x00\x00\x10\x6d\x00\x00\x10` @0-7 | 8 |
| 7 | sph | `"NIST_1A"` @0-6 | 7 |
| 8 | amr-nb | `"#!AMR\n"` @0-5 | 6 |
| 9 | txw | `"LM8953"` @0-5 | 6 |
| 10 | sndt | `"SOUND\x1a"` @0-5 | 6 |
| 11 | vorbis | `"OggS"` @0-3 ∧ `"vorbis"` @29-34 | 35 |
| 12 | opus | `"OggS"` @0-3 ∧ `"OpusHead"` @28-35 | 36 |
| 13 | **hcom** | `"FSSD"` @**65-68** ∧ `"HCOM"` @**128-131** | **132** |
| 14 | **act** (`#if USING_FFMPEG`) | `"RIFF"` @0-3 ∧ `\x84` @**256** | **257** |
| 15-17 | wav | `RIFF`/`RIFX`/`RF64` @0-3 ∧ `"WAVE"` @8-11 | 12 |
| … | aiff…sndr + the `#if USING_FFMPEG` block (:144+: 3g2,aa,aac,…,wsaud,wtv) | — | — |

## Deliverable 2 — geometric intersection with RIFF@0 ∧ 0x84@256

act's fields occupy {0-3} and {256}. A colliding row must test neither a
non-`RIFF` byte in 0-3 nor a non-`0x84` byte at 256:

- **Pre-act**: every row except gsrt and hcom is anchored at offset 0 with
  magic ≠ `RIFF` (voc/smp/wve/amr-*/prc/sph/txw/sndt/vorbis/opus all require
  non-`RIFF` bytes at 0-3) → geometrically incompatible. **Only gsrt {16-24}
  and hcom {65-68,128-131} are disjoint from {0-3,256}** → both can coexist
  with the act trigger in one file. Matches the r62/knowledge enumeration.
- **Post-act** (shadowed — can co-match but never win): wav {0-3,8-11},
  avi {0-3,8-11}, nsp DS16@4-7, the ftyp family {4-11}, aa/mlp {4-7},
  wsaud {11,16-19}, sndr {0-1,7}. Two measured: `probe_avi_act.wav`
  (RIFF+`AVI `@8+0x84@256) and `probe_ftyp_act.wav` (`ftypisom`@4-11+0x84@256)
  both detected **`act`** — later matches are invisible in detection output.
- **RIFF-layout footnote**: in any RIFF, offsets 16-19 are the *first chunk's
  size field*. `ring.bin\0`@16-24 therefore always destroys the chunk walk
  (size ← 0x676e6972) — a gsrt-collision RIFF is structurally undecodable by
  ffmpeg's wav demuxer (`no 'data' tag found`). hcom fields can be placed
  fully inside a `data` payload in a fmt-16 layout (payload starts @44), so
  hcom collisions CAN preserve downstream decodability — the basis of the
  recommended pair.

## Deliverable 3 — probe matrix (empirical, this host)

Scratch: `corpus/live/r65-scout/probes/` (builder `make_probes.py`; full logs +
strace under `runs/logs/`, table `runs/probe-table.tsv|.txt`, shas
`runs/probe-shas.txt`). Route column = `sox -V4` `detected file format type`
line; reader outcome from same run's FAIL/INFO + `strace -f -e execve`.

**Pair-family collisions** (base `round-63/pair_route_84.wav`, 11,588 B,
RIFF@0+WAVE@8+0x84@256; sha cf5edecce1812f0a — base copy `probe_act_base.wav`
byte-identical):

| probe | vs base | detected | reader/route | sox exit | decoded | ffprobe |
|---|---|---|---|---|---|---|
| probe_act_base.wav | — | act | **ffmpeg child spawned** (strace: execve ffmpeg -f au -) | 0 | 15,356 B (3,839 f32) | pcm_s24le |
| probe_gsrt_act.wav | `ring.bin\0`@16-24 | **gsrt** | native gsrt reader → `premature EOF`; **no ffmpeg execve** | 2 | 0 | (wav demux: `no 'data' tag found`) |
| probe_hcom_act.wav | `FSSD`@65-68,`HCOM`@128-131 | **hcom** | native hcom reader → `bad compression type`; no ffmpeg | 2 | 0 | `Invalid data` (ff hcom probe) |
| probe_gsrt_hcom_act.wav | both magics | **gsrt** | gsrt reader → `premature EOF` | 2 | 0 | — |
| probe_gsrt_only.wav | gsrt magic, 256←0x00 | gsrt | gsrt → `premature EOF` | 2 | 0 | — |
| probe_hcom_only.wav | hcom magics, 256←0x00 | hcom | hcom → `bad compression type` | 2 | 0 | — |
| probe_gsrt_badnul.wav | `ring.bin\x80`@16-24 (9th byte ≠ NUL) | **act** | ffmpeg spawned, demux fails → `premature EOF` | 2 | 0 | — |
| probe_hcom_halffssd.wav | `FSSD`@65 only | act | ffmpeg decode ok | 0 | 15,356 B | pcm_s24le |
| probe_hcom_halfhcom.wav | `HCOM`@128 only | act | ffmpeg decode ok | 0 | 15,356 B | pcm_s24le |
| probe_avi_act.wav | `AVI `@8-11 (post-act row matches) | **act** | ffmpeg spawned → demux fails → `premature EOF` | 2 | 0 | — |
| probe_ftyp_act.wav | `ftypisom`@4-11 (post-act rows match) | **act** | ffmpeg spawned → fails | 2 | 0 | — |

**Minimal shells** (RIFF@0 + fields only, `make_probes.py minimal()`):

| probe | size | detected | exit | note |
|---|---|---|---|---|
| min_act.wav | 257 | act | 2 | ffmpeg can't demux shell → premature EOF (act reachable on bare RIFF+0x84) |
| min_gsrt_act.bin | 257 | **gsrt** | 2 | preemptor wins on a 257-B shell |
| min_hcom_act.bin | 257 | **hcom** | 2 | hcom reader → `bad sampling rate divisor` |
| min_gsrt_hcom_act.bin | 257 | **gsrt** | 2 | both magics → earliest row wins |
| min_hcom_200.bin | 200 | **hcom** | 2 | len 200 < 257: act unreachable anyway; hcom gate ≈132 confirmed live |
| min_gsrt_25.bin | 25 | **gsrt** | 2 | len-gate edge = 25 = 16+9 |
| min_gsrt_24.bin | 24 | *(none)* | 2 | → extension fallback: `no handler for file extension 'bin'` |
| min_hcom_132.bin | 132 | **hcom** | 2 | len-gate edge = 132 = 128+4 |
| min_hcom_131.bin | 131 | *(none)* | 2 | → extension fallback |

**Decodable-collision family** (fmt-16 PCM WAV, 1,068 B, 512-sample sine;
'FSSD'@65-68 and 'HCOM'@128-131 land inside `data` payload @44+; 0x84@256):

| probe | detected | exit | decoded | `sox -t wav` | `sox -t act` | ffprobe auto |
|---|---|---|---|---|---|---|
| pcm_act_base.wav | act | 0 | 2,048 B | 2,048 B | 2,048 B | pcm_s16le |
| **pcm_hcom_act.wav** | **hcom** | 2 | 0 (`bad compression type`) | **2,048 B** | **0 B** | `Invalid data` — `Format hcom probed with size=2048 and score=100` |
| pcm_hcom68x_act.wav | act | 0 | 2,048 B | 2,048 B | 2,048 B | pcm_s16le |
| pcm_hcom131x_act.wav | act | 0 | 2,048 B | 2,048 B | 2,048 B | pcm_s16le |

Two-layer preemption detail: `pcm_hcom_act.wav` is a *valid, fully decodable*
WAV (`sox -t wav` → 2048 B; `ffmpeg -f wav` → 1024 B s16le) yet (a) SoX
detects hcom → hcom reader rejects → terminal; (b) even the **forced** `-t
act`/`-t ffmpeg` bridge cannot rescue it — the ffmpeg child's own probe scores
`hcom 100` over wav and fails, so the au pipe is empty → `premature EOF`. The
native-wav route is the only reader that decodes this file.

Binary corroboration (not load-bearing): `objdump` of `auto_detect_format`
shows the compiled len-gate sequence `cmp rcx,0x18`@0x1a338 (25 → gsrt) …
`cmp rcx,0x83`@0x1aa5d (132 → hcom) then `cmp rcx,0x100`@0x1aa76 (257 → act) —
machine order matches source order; r63-scout mapped the act branch onward.

## Deliverable 4 — pair recommendation for the author

**Primary (sharpest): `pcm_hcom_act.wav` ↔ `pcm_hcom68x_act.wav`** — a
*one-byte* collision pair (sole diff @file offset 68, `'D'→'E'`, `cmp -l`
receipt `runs/diff-hcom-pair.txt`). Both are structurally valid fmt-16 RIFF
WAVs (`sox -t wav` decodes 2,048 B on both; shas `b52aedcd…` / see
`runs/probe-shas.txt`).

| member | detection | outcome | receipt shape |
|---|---|---|---|
| pcm_hcom_act.wav | `hcom` | open-fail `bad compression type`, **exit 2**, 0 B | needs the r63-style `try/except CalledProcessError` wrap inside `measure()` — `command(check=True)` propagates |
| pcm_hcom68x_act.wav | `act` | ffmpeg bridge, **exit 0**, 2,048 B = 512 f32 samples | normal receipt; `format:` failure vs the measurer's pcm_s16le gate is fine (both members can also be run as forced-route probes outside the measurer) |

Why sharpest: the preemptor suppresses a *genuinely decodable* act-route file
(proven by `-t wav` 2048 B and the 68x member's live decode), so the pair
isolates ordering — not "the file was broken anyway." Alternate 1-byte member:
`pcm_hcom131x_act.wav` (diff @offset 131 `'M'→'N'`). Builder recipe: fmt-16
PCM WAV, ≥512-B payload; place `FSSD`@65-68 + `HCOM`@128-131 + `0x84`@256
inside payload — *not* on the fmt-40 family (there `FSSD`@65-68 straddles
dataSize@64-67 and destroys ffmpeg demuxing — verified `Invalid data`).

**Secondary (9-byte field collision): `probe_gsrt_act.wav` ↔
`probe_act_base.wav`** — sole 9-byte span diff @16-24 (receipt
`runs/diff-gsrt-pair.txt`), detection gsrt↔act, exit 2↔0, decode 0↔15,356 B.
Weaker only in that the preempted member is structurally undecodable by ffmpeg
(RIFF layout forces offsets 16-19 to be the first chunk size) — detection
contrast is still maximal. `runs/diff-hcom-pairfamily.txt` holds the
pair-family hcom diff if the author prefers staying on the 11,588-B family.

## Deliverable 5 — falsification candidates & detection-ambiguity notes

- **No preemptor-shaped file routed act** — the falsification fork did not
  trigger on any of the 20 probes; the r62/r63 ordering claim stands
  (confidence high, this build/host).
- **Terminal, no fallthrough**: preemptor-detected files whose readers reject
  do NOT re-enter detection — `gsrt→premature EOF`, `hcom→bad compression
  type`/`bad sampling rate divisor`, all exit 2, no ffmpeg execve. A file
  "hcom-detected but unreadable" never reaches act.
- **Exit code is NOT a route signature**: act-detected-but-undemuxable files
  (probe_avi_act, probe_ftyp_act, probe_gsrt_badnul) and preemptor-detected
  files both exit 2. Only `-V4` `detected file format type` (or strace execve
  count: 1 = native path, ffmpeg child = act bridge) disambiguates; `sox --i`
  prints nothing usable on reader-fail (no `Input File` line at all).
- **Shadowed co-matches are invisible**: detection reports only the FIRST
  matching row — probe_avi_act simultaneously satisfies act and avi's
  `RIFF+AVI @8`; only `act` appears. Any "row X doesn't match" claim on a
  RIFF file is unprovable from detection output when an earlier row fires.
- **Bridge is not a rescue**: `-t act`/`-t ffmpeg` on `pcm_hcom_act.wav`
  yields 0 B because ffmpeg's own probe prefers its hcom demuxer
  (`score=100`, measured `-v debug`); the preemptor shape poisons the ffmpeg
  child too. Only `-t wav` decodes (2,048 B). Same-shape note for
  pair-family: `sox -t wav` on `probe_{gsrt,hcom}_act.wav` → 0 B (corrupted
  fmt/dataSize), so those members can't claim native-decodability.
- **Conjunct integrity**: gsrt's 9th byte must be `0x00` (`ring.bin\x80` →
  detected act); hcom needs BOTH `FSSD`@65 and `HCOM`@128 (either alone →
  act). Len gates: gsrt 25 B, hcom 132 B, act 257 B (131-B and 24-B probes
  fall through to extension fallback).
- **Prior art byte-stable**: all inputs were read-only; `round-63/
  pair_route_{84,00}.wav` untouched (base re-copied sha-identical
  `cf5edecce1812f0a`); existing tracked receipts/ledgers unmodified.

## Facts vs inference vs remaining unknowns

**Facts (measured this round, this host):** every detection/route/exit/decoded
column above; strace execve counts (act-route spawns `/usr/bin/ffmpeg
-loglevel quiet -nostdin -strict -2 -i <f> -f au -`; preemptor routes spawn
none); ffmpeg `hcom … score=100` probe line; len-gate edges 24/25, 131/132;
`bad compression type` / `bad sampling rate divisor` / `premature EOF` reader
errors; cmp-diff receipts; `no handler for file extension 'bin'` on
detection-miss.

**Inference (corroborated, not re-derived):** mapping of compiled len-gates to
source rows (0x18→gsrt, 0x83→hcom, 0x100→act — order and values match, and
r63-scout mapped the act branch independently); ffmpeg's hcom probe checking
the same 65/128 offsets (observed score=100 + `Invalid data`, source unread);
gsrt reader's `premature EOF` = fixed ring.bin header read running out;
upstream comment "Must come before wav because it looks like a PCM WAV file".

**Remaining bounded unknowns:** real gsrt/hcom files can't collide (real FSSD
files start `FSSD`@0 ≠ `RIFF`) — the collision is synthetic-only;
hcom-reader's exact accept path unprobed (our fakes all die at
divisor/compression-type checks — whether *any* RIFF file can survive hcom
startread is open but irrelevant to detection ordering); non-ffmpeg SoX builds
drop the act row entirely (AUTO_DETECT_SIZE 132 — different landscape);
stdin/pipe pending-buffer path unexercised; other hosts untested.

## Receipts / artifacts

- `corpus/live/r65-scout/make_probes.py`, `measure.sh` — builders/harness.
- `corpus/live/r65-scout/probes/` — 20 fixtures (11,588-B pair family ×11,
  1,068-B fmt-16 family ×4, minimal shells ×5).
- `corpus/live/r65-scout/runs/probe-table.{tsv,txt}` — full matrix;
  `runs/probe-shas.txt`; `runs/diff-{gsrt,hcom,hcom-pairfamily}-pair.txt`;
  `runs/logs/*.v4|.i.err|.log|strace-*` — per-probe -V4, soxi and execve
  receipts.
- Commands verbatim in body; base fixture `corpus/live/round-63/
  pair_route_84.wav` (sha `cf5edec…`, read-only).
