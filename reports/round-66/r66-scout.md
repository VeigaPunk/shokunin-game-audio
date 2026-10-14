# r66 — scout — audio lane — preemptor-map completion (wve predicate, RIFF geometry, len gates, decodable pair)

Seat: scout (recon only). Writes: this report + `corpus/live/r66-scout/`
(`gen_probes.py`, `run_matrix.sh`, `probes/` ×36, `runs/` logs+tables). No tracked
edits, no commits, no other lane touched.
Host: devin; worktree `~/Projects/prymeagnt/audio` (`.shokunin/audio` → canonical
`~/Projects/shokunin/audio-shokunin`). Toolchain: SoX_ng **v14.8.0.1**
(`/usr/bin/sox`, USING_FFMPEG build → `AUTO_DETECT_SIZE 257`), ffmpeg/ffprobe
n9.0.1, strace, python3. No `lsp` device in this seat's toolset — source citations
are grep/read against the local upstream copy `/tmp/sox_ng_src/sox_ng/src/`
(configure.ac `AC_INIT([sox_ng],[14.8.0.1])` — version matches the binary;
md5-identical to r64-reviewer's receipt copy). Corroborative only; every
load-bearing claim is a live measurement on this host's binary.

**Scratch provenance note**: `corpus/live/r66-scout/` contained a dead sibling
session's probes/logs on arrival. I audited the generator line-by-line, then
re-ran the entire harness fresh (`bash run_matrix.sh`); the regenerated
`runs/matrix.tsv` is byte-identical to the inherited copy (diff receipt kept as
`runs/matrix.prior.tsv`), all 36 probes re-measured and re-logged (364 files
under `runs/logs/`). Nothing below is inherited-on-trust.

## Verdict

All five brief items resolved. Headline: **the wve CHECK row is real, byte-exact,
and sits at formats.c:80 — but the declared "wve-shaped RIFF file preempts
gsrt/hcom/act" is geometrically unfalsifiable-as-stated: wve{0-14} and
RIFF{0-3} collide at byte 0 (`0x41 'A'` vs `0x52 'R'`), so a wve-shaped RIFF
file cannot exist on this build.** Where wve *can* co-match (non-RIFF surface)
it does preempt gsrt, hcom, and the bare 0x84 byte — every time. Len gates pin
exactly at gsrt 24|25 and hcom 131|132. The decodable-preemptor pair landed by
the author (`pair_dec_hcom.wav`/`pair_dec_act.wav`) re-derives sha-identical in
my independent build and is the sharpest option — see Deliverable 5.

Measured order where co-satisfiable (all live-detected, `runs/matrix.tsv`):

    voc(78) ⊥ smp(79) ⊥ wve(80) | wve < gsrt(81) < hcom(90) < act(93) < wav(95+)

(`⊥` = predicates byte-conflict at offset 0 — mutually exclusive on one file.)

## Deliverable 1 — wve CHECK predicate: identified empirically, source-corroborated

Source row (`formats.c:80`, corroborative): `CHECK(wve, 0,0,"", 0,15,
"ALawSoundFile**")` → predicate = `len >= 15 && memcmp(data,
"ALawSoundFile**", 15) == 0` under macro `formats.c:71-72` (single conjunct;
the `**` are literal `0x2A` bytes, not wildcards — the C string is 15 chars).

Empirical pinning (P-series, `sox -V6 <f> -n stat`, `detected file format type`
line; receipts `runs/logs/P*.v6.log`, table `runs/matrix.tsv`):

| probe | construction | detected | reader tail | proves |
|---|---|---|---|---|
| P01_wve_magic | magic@0-14, 300 B | **wve** | `can't find Psion identifier` | baseline hit |
| P02_wve_len15 | 15 B file | **wve** | `premature EOF` | len floor = 15 |
| P03_wve_len14 | 14 B file | NONE | ext fallback | 14 < gate |
| P04/P05 (b14X) | byte14 `*`→`X` | NONE | — | byte 14 literal `*` |
| P06 (b13X) | byte13 `*`→`X` | NONE | — | byte 13 literal `*` |
| P07 (b0low) | byte0 `A`→`a` | NONE | — | case-sensitive |
| P08 (b07X) | byte7 `n`→`X` | NONE | — | mid-magic required |
| P09 (b15free) | byte15 = 0xAA | **wve** | `can't find Psion identifier` | detector stops at 15 |
| P10 (len18 idok) | magic+`\x00\x0F\x10` | **wve** | `premature EOF` | ID1 accepted → dies later |

Detector-vs-reader asymmetry (new this round, both directions now mapped):
the CHECK row tests **15** bytes @0-14; `wve.c:22-36` `start_read` re-verifies
the **18-byte** ID1 `ALawSoundFile**\x00\x0F\x10`, then reads BE
`num_samples`@18-21, skips 10 pad bytes, then A-law payload @32 (mono, 8 kHz,
`SOX_FILE_BIG_END`). So detection is *weaker* than the reader here — P09
detects `wve` then fails `can't find Psion identifier`; P10 passes ID1 and
dies at `lsx_readdw` (`premature EOF`). The three distinct tails (`Psion
identifier` vs `premature EOF` vs clean decode) let a probe tell exactly how
far the reader got — used below.

## Deliverable 2 — wve probes + RIFF + 0x84@256: detection and preemption

**wve detects whenever its 15 bytes sit at offset 0** (Q/S/P series, `.bin` or
`.wav`). **On co-matchable files it preempts everything measured**:

| probe | signatures present | detected | note |
|---|---|---|---|
| Q01 | wve + `ring.bin\0`@16-24 + 0x84@256 | **wve** | beats gsrt + act-byte |
| Q02 | wve + gsrt + `FSSD`@65 + `HCOM`@128 + 0x84@256 | **wve** | quad collision → earliest row wins |
| Q03 | wve + hcom + 0x84@256 | **wve** | beats hcom |
| V01–V03 | wve *reader-valid* (±hcom conjuncts, ±0x84) | **wve** | **decode 64 samples, exit 0** — see D5 |

**On RIFF, wve is unreachable — geometric wall, not just unobserved.** Every
RIFF-family tag (`RIFF`/`RIFX`/`RF64`) needs `0x52`@0; wve needs `0x41`@0.
Head-swap battery (common 300-B tail, heads differ only @0-3; cmp receipt
`runs/diff-swap-pair.txt` = 4 bytes @1-4 `ALaw`→`RIFF`):

| probe | bytes 0-14 | detected | note |
|---|---|---|---|
| S01_head_wve | `ALawSoundFile**` | **wve** | positive control |
| S02_head_riff84 | `RIFF`+`SoundFile**`, 0x84@256 | **act** | 4-byte span flips wve→act (ffmpeg child spawned, demux fails → `premature EOF`) |
| S03_head_b0R | `RLawSoundFile**` | NONE | 1-byte flip @0 → neither row |
| S04_riff+wve@44 | RIFF/WAVE shell, full magic embedded @44 | **act** | magic not anchored @0 = invisible; 128 samples decodable via ffmpeg |
| S05/S06/S07 | RIFF+0x84 controls ±gsrt ±hcom | act / **gsrt** / **hcom** | ordering controls fire as expected |

So the brief's ordering claim resolves precisely: **wve < gsrt < hcom < act
holds on every surface where the predicates can coexist; the RIFF+0x84 surface
can never carry wve, so the reachable preemptor set on RIFF+0x84@256 is exactly
{gsrt, hcom}** — same conclusion as the author's r66-author W-series (16 RIFF
constructions, independent of mine).

## Deliverable 3 — geometric intersection map (which rows can co-match one file)

Byte-range analysis vs live Q/S results — complete for the pre-act window:

| row(s) | fields | ∩ wve{0-14} | ∩ RIFF{0-3} | ∩ act{0-3,256} | measured |
|---|---|---|---|---|---|
| voc(78) {0-19}, smp(79) {0-16} | head magic | **conflict @0** | conflict @0 | conflict @0 | — (geometry) |
| **wve(80) {0-14}** | `ALawSoundFile**` | — | **conflict @0** | **conflict @0** | S01-S04 |
| **gsrt(81) {16-24}** | `ring.bin\0` | **disjoint** (byte15 free) | disjoint | disjoint | Q01→wve, S06→gsrt |
| **hcom(90) {65-68,128-131}** | FSSD+HCOM | disjoint | disjoint | disjoint | Q02/Q03→wve, S07→hcom |
| act(93) {0-3,256} | RIFF+0x84 | conflict @0 | — | — | — |
| wav(95-97) {0-3,8-11} | RIFF|RIFX|RF64+WAVE | conflict @0 | — | co-matches act, loses | S02 (act wins anyway via 0x84) |

Consequences:
- **wve ∧ gsrt ∧ hcom ∧ (0x84 byte) can all co-match one file** — Q02 does it;
  wve wins. Byte 15 is the only wve-constrained slot gsrt might want and it's
  free (gsrt starts @16).
- **wve ∧ RIFF is impossible** — so "wve preempts act" is vacuous on the RIFF
  axis: when wve matches, act's RIFF conjunct fails by construction; when act
  matches, wve's magic is absent. The 0x84@256 byte alone (Q01-Q03) is inert
  without RIFF@0.
- **gsrt ∧ hcom ∧ act is the maximal RIFF-surface collision** (r65's terrain);
  wve joins only off-RIFF. The preemptor map on RIFF+0x84@256 is complete:
  {gsrt:81, hcom:90}, both < act:93 < wav:95.

## Deliverable 4 — length gates pinned as sole-byte variants

Gate semantics (macro `:71`): `len >= p1+l1` where len = bytes actually
buffered (≤257). gsrt needs **25** (16+9, the 9th byte is the literal's NUL
terminator — `memcmp` compares 9 bytes of `"ring.bin"`); hcom needs **132**
(128+4). Measured (RIFF/WAVE shells + bare `.bin` cross-checks):

| probe | size | sig bytes | detected | outcome |
|---|---|---|---|---|
| L01/`pair_lengate_gsrt_25` | 25 | `ring.bin\0`@16-24 | **gsrt** | `premature EOF`, exit 2 |
| L02/`pair_lengate_gsrt_24` | 24 | `ring.bin`@16-23 (NUL cut) | wav | `fmt chunk not found`, exit 2 |
| L03/`pair_lengate_hcom_132` | 132 | FSSD+HCOM complete | **hcom** | `premature EOF`, exit 2 |
| L04/`pair_lengate_hcom_131` | 131 | `HCO`@128-130 (M cut) | wav | **decodes 43 samples, exit 0** |
| L05/L06 (.bin) | 25/24 | gsrt sigs | **gsrt** / NONE | gate is on file length, not RIFF |
| L07/L08 (.bin) | 132/131 | hcom sigs | **hcom** / NONE | same; NONE → ext fallback |

Byte-diff receipts (`cmp -l`, 1-based): L01↔L02 = byte5 (RIFF size 17↔16) +
1 trailing byte; L03↔L04 = bytes 5,41 (RIFF+dataSize bookkeeping) + 1 trailing
byte — the *semantic* delta is exactly the length-crossing signature byte
(NUL@24 / `M`@131). **The bare `.bin` members are the pure sole-byte variants**:
L05↔L06 and L07↔L08 are strict prefixes (`cmp` reports EOF only) — cleanest
gate evidence, though they pay for it with ext-fallback on the below side.
My L01–L04 rebuilds are sha-identical to the tracked `pair_lengate_*` members
(`runs/tracked-shas.txt` vs `runs/probe-shas.txt`).

## Deliverable 5 — decodable-preemptor pair: recommendation

**Recommend the tracked hcom-9-sample pair: `pair_dec_hcom.wav` ↔
`pair_dec_act.wav` — confirmed sharpest.** My independent rebuilds
(`D01`/`D02`, fresh generator, no shared code with the author's builder) are
**byte-identical to the tracked members** (empty `cmp` receipts
`runs/diff-rebuild-vs-tracked-{hcom,act}.txt`), and the hcom member matches
r65-critic's `D1_hcomdecode+act.wav` sha `325fb967…` — three-way convergence.

| member | diff | detected | exit | decode | route evidence |
|---|---|---|---|---|---|
| `pair_dec_hcom.wav` (600 B) | — | **hcom** | 0 | **9 samples @22050, 36 f32 B** | native reader, `execve_ffmpeg=0`; `sox --i` prints `(hcom)`/`8-bit HCOM`/`22050`; stdin transport also detects+decodes (9, rc0) |
| `pair_dec_act.wav` (600 B) | **1 byte @68** `D`→`E` (`FSSD`→`FSSE`) | **act** | 0 | 278 samples, 1112 f32 B | ffmpeg bridge, `execve_ffmpeg=1`, ffprobe `pcm_s16le` |

Why sharpest: (a) **sole-byte** divergence (`runs/diff-dec-pair.txt` = one line,
offset 69 `104→105`); (b) detection flips *to* the preemptor **and the
preemptor's own reader decodes** — the round's exact requirement, satisfied
natively (no ffmpeg ambiguity); (c) the preempted member is itself fully
decodable (278 via bridge; D01 also decodes 278 under forced `-t wav`), so the
pair isolates ordering, not file validity; (d) three working readers on one
byte-stream measured (hcom 9 / act-bridge 3520 / wav 278 — forced-leg receipts
`D01.t_*.log`), reproducing r65-critic's E7 table.

The scout's r65 fmt-16 alternative (`pcm_hcom_act` ↔ `pcm_hcom68x`) **does not
satisfy this round's bar**: its preemptor member detects hcom but the reader
fails (`bad compression type`, 0 B) — it's an ordering pair, not a
decodable-preemptor pair. Keep it as prior art.

**Bonus finding (beyond the pair)**: `V02_wve_valid+hcom+84.bin` shows wve
itself is a *decodable preemptor* — carries the full hcom conjunct set +
0x84 byte, detects `wve`, **decodes 64 samples rc0** (stdin too), while every
forced alternate reader fails (`-t hcom`→`bad compression type`, `-t wav`→`RIFF
header not found`, `-t act`→`premature EOF`: exclusive decodability). Cannot be
a RIFF pair (byte-0 wall, D3) — but on the non-RIFF surface it's the earliest
decodable preemptor this map admits.

## Facts / inference / unknowns

**Facts (measured this round, this host):** every matrix row in
`runs/matrix.tsv` (36 probes × detection/exit/samples/f32-bytes/execve count);
wve len floor 15 & byte-exactness (P02-P09); preemption direction on all
co-matchable collisions (Q01-Q03, S01-S02); gate edges 24|25, 131|132 on both
RIFF and bare surfaces (L01-L08); pair_dec rebuild sha-identity; lengate
rebuild sha-identity; ffmpeg child spawned iff detected `act` (5/36: D02, D03,
S02, S04, S05 — strace `execve("/usr/bin/ffmpeg"` receipts); transport legs
(stdin detects wve/hcom and decodes; gsrt stdin fails `invalid format for this
file type` — non-seekable path differs from regular-file `premature EOF`,
consistent with r65-critic's checksum-loop mechanism note).

**Inference (corroborative, not load-bearing):** CHECK macro semantics from
`formats.c:71-72`; row numbering 80/81/90/93/95 from source order; wve reader
layout from `wve.c:22-37`; the `ring.bin` 9th compared byte is the literal's
NUL terminator (l1=9 > string length 8 — memcmp consumes `\0`).

**Remaining unknowns (bounded):** pre-wve rows voc/smp never exercised live
(geometry suffices — byte-0 conflict is provable without a probe); voc/smp's
own preemption power on non-RIFF triple-collisions unmeasured (out of scope —
they can't touch the RIFF axis anyway); non-ffmpeg builds drop act
(`AUTO_DETECT_SIZE 132`) — different map, untested here; real-world wve files
vs our synthetic ID1s not sampled.

## Receipts

- `corpus/live/r66-scout/gen_probes.py` — 36-probe generator (P/V/Q/S/L/D
  families; documented per family).
- `corpus/live/r66-scout/run_matrix.sh` — harness: `-V6` stat, f32 decode count,
  `--i`, forced `-t {wve,gsrt,hcom,act,wav}`, strace execve census, ffprobe,
  stdin transport legs, sha/cmp receipts.
- `corpus/live/r66-scout/probes/` ×36; `runs/logs/` ×364; `runs/matrix.tsv`
  (regenerated identical this session — `runs/matrix.prior.tsv` = inherited
  copy, diff-empty); `runs/probe-shas.txt`; `runs/tracked-shas.txt`;
  `runs/diff-{dec-pair,swap-pair,rebuild-vs-tracked-hcom,rebuild-vs-tracked-act}.txt`.
- Source refs (corroborative): `/tmp/sox_ng_src/sox_ng/src/formats.c:61-97`
  (AUTO_DETECT_SIZE, CHECK macro, rows 78-97), `/tmp/sox_ng_src/sox_ng/src/
  wve.c:22-37` (18-byte ID1, BE num_samples, `can't find Psion identifier`).
- Verbatim key commands: `sox -V6 <f> -n stat`; `sox <f> -t f32
  -e floating-point - | wc -c`; `sox -t <type> <f> -n stat`; `cat <f> | sox -V6
  - -n stat`; `strace -f -e trace=execve sox <f> -n stat`; `cmp -l a b`.
