# R72 scribe — THIRD DECODER (libsndfile 1.2.2): r72 harness arm NOT LANDED at scribe time (absent, not failed); frontier × reviewer libsndfile matrices agree 36/36; verified 3-decoder lattice: sox-only {txw-seekable, .f32-named} CONFIRMED, **no sndfile-only acceptance cell** (.snd-named is sox+sndfile-shared), ffmpeg ⊃ libsndfile on detected-type classes only; conflicts F1–F5 reported verbatim

Seat: **scribe** (leaf, report-only). Host: devin — SoX_ng v14.8.0.1,
ffprobe/ffmpeg n9.0.1, libsndfile **1.2.2** (`sf_version_string()` via ctypes,
this session), python 3.14.7. Repo `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Observation snapshot: **2026-10-14 14:20 UTC**; HEAD `c079aba` (wave-10
report-last, committed 14:16:08Z). Scratch `corpus/live/r72-scribe/`; this file
is the only report path written. No tracked file modified, no git mutation, no
decoder re-run (all numbers below re-read from existing artifacts/receipts).

Axis-move (verbatim, from the brief): *"add `--probe-sndfile-transport-r72`
mirroring the r71 ffprobe arm: sndfile-info detection + a decode leg …
Receipt family `sndfile_*_r72_probe` keyed per member x transport. Claim to
test: the 3-decoder verdict lattice partitions members into distinct
decoder-coverage classes (sox-only: txw-seekable/.f32-named; sndfile-only:
.snd-named; ffmpeg superset on detect). Every claim needs measured evidence;
insertion-only; prior rows byte-stable."*

## Author-landing state at observation — the r72 MOVE is unlanded

Checked this session, repeatedly (final check 14:20Z):

- `grep -c sndfile corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py`
  → **0 / 0**. Last probe flag in the tracked fixture is
  `--probe-ffprobe-transport-r71` (`measure_audio.py:881`); no
  `--probe-sndfile-transport-r72` exists, and no `sndfile` token anywhere in
  the fixture. `TRANSPORT_R71_MEMBERS` (`:556`) is still the newest member set.
- `git hash-object corpus/fixtures/measure_audio.py` =
  `bae5de494f2fcc159fd88bbaf5ff0b4bfa04538a` = `git rev-parse
  HEAD:corpus/fixtures/measure_audio.py` (working tree == HEAD; sha256
  `33f0a57764f38d5ec372ff2c19729593fe5e2acfb4cfa2ff191294c2da8e4c6c`).
  `git status --porcelain` shows **no modification to any tracked file**.
- No receipt family exists: `grep -rl sndfile corpus/live/runs/*/measurements.json`
  → no output. There is no `sndfile_*_r72_probe` key anywhere in `runs/`.
- No `corpus/live/r72-author/` scratch; no new commit after `c079aba`; no
  `reports/round-72/` directory existed before this file.

**Consequence:** the r72 harness insertion (probe flag + `sndfile_*_r72_probe`
receipts) is *absent, not failed*. Everything below is assembled from
pre-existing measured artifacts — the frontier seat's libsndfile matrix, the
committed sox/ffmpeg receipts, and (as corroboration only) sibling-seat
scratch — not from a landed r72 arm. The "insertion-only / prior rows
byte-stable" gate is therefore **not exercisable** at scribe time (nothing was
inserted; trivially no prior row changed).

Sibling scratch present at snapshot (untracked, in flight):
`r72-boundary/` (prior-verdict extract), `r72-critic/`, `r72-reviewer/`
(independent libsndfile harness + lattice), `r72-scout/` (baseline extract),
`r72-simplifier/`, `r72-verifier/` (created empty 14:20Z). None of these is
committed evidence; the reviewer matrix is used below only as a cross-check.

## Measured evidence used (sources + provenance audit)

1. **libsndfile matrix (frontier, tracked/committed)** —
   `corpus/live/frontier-sndfile/runs/sndfile-matrix.json`
   (sha256 `466516f95486fe7c6bc3c6dc7f5aa620b9c0d638717b91b62ecc8ee0658d8cc0`):
   13 members × 4 arms, ctypes `sf_open`/`sf_open_fd`, full SF_INFO + read
   count. Harness `corpus/live/frontier-sndfile/probe_sndfile.py`
   (`8081097c…`); CLI logs `logs/info-*.txt` for all 9 canonical members.
2. **libsndfile matrix (reviewer, untracked scratch, independent path)** —
   `corpus/live/r72-reviewer/sndfile-matrix.json` (`c06d3215…`), 9 canonical
   members × 4 arms. Its harness `probe_sndfile_r72.py` (`b7ec38ab…`) is an
   independent re-implementation (its docstring: *"written from the API surface
   directly rather than reusing the frontier harness"*; diff vs frontier
   harness = 271 lines of divergence). **My cross-check: 36/36 cells identical
   to the frontier matrix** (verdict string + format_name).
3. **sox + ffmpeg columns** — frontier extract
   `corpus/live/frontier-sndfile/runs/prior-verdicts.tsv` (`89caf693…`),
   72 rows. **My audit: every row re-checked against the committed receipt
   named in its own `receipt` column — 72/72 exact** (sox:
   detected/exit/samples/error; ffmpeg: ffprobe_format/ffmpeg_exit/ffmpeg_error).
4. **ffmpeg receipt-invariance** — three receipts carry the same r71 ffprobe
   entries: `20261014T140155796326Z-normal` (`c584b0d0…`),
   `20261014T141008229687Z-ffprobe-transport-r71`,
   `20261014T141033155858Z-ffprobe-transport-r71` (`578cad95…`). **Lattice
   fields (ffprobe_format, probe_score, ffprobe_exit, ffmpeg_exit,
   ffmpeg_error) are 36/36 identical across all three.** The only differences
   are `ffprobe_error` path-normalization and verdict-group shape — the r71
   verifier's D2 (`reports/round-71/r71-verifier.md:91`), corrected in
   `77768fa` ("r71 corrections: path-normalized error tails"). Verdict impact:
   none.
5. **sndfile-info CLI leg** — `logs/info-*.txt` (all 9 members): dec_act and
   dec_hcom open as WAV/PCM16 (0x00010002); `extsuffix_snd` opens as
   `0x00040010`, 8000 Hz, Frames 512; `posttable`, `extsuffix_{wav,bin,txw,f32}`
   → `Error : Not able to open input file … / Format not recognised.`;
   `txw_piperefuse` → `File contains data in an unimplemented format.`
   (This leg is read from the frontier's committed logs, not re-run.)
6. **Extension-fallback sweep (frontier)** —
   `corpus/live/frontier-sndfile/runs/extsweep.json` (`de58146f…`):
   56 extensions on identical no-magic bytes; exactly four decode:
   `.au` (0x40010, read 500/512), `.gsm` (0x40020, read 2560/2560),
   `.snd` (0x40010, read 500/512), `.vox` (0x40021, read 1024/1024) — all
   8 kHz mono.

## Verified 3-decoder lattice (9 members × 4 arms = 36 cells)

`A` = accepts (sox: exit 0 + samples; ffmpeg: decode exit 0; sndfile:
read_frames > 0); `R` = rejects. Compact form — arms are listed only where a
member forks. Full 36-row machine-readable lattice with receipt provenance:
`corpus/live/r72-scribe/lattice-verified.tsv`.

| member | arm(s) | sox (receipt) | ffmpeg (r71 receipt) | libsndfile 1.2.2 |
|---|---|---|---|---|
| dec_act | file | **A** act 278 (r67) | **A** wav | **A** WAV/PCM16 278 |
| dec_act | stdin_pipe, redirected_fd, fifo_path | R (`can't find Sun/NeXT/DEC identifier` / `premature EOF`) | **A** wav | **A** WAV/PCM16 278 |
| dec_hcom | all 4 | **A** hcom 9 (r67) | **A** hcom | **A** WAV/PCM16 278 (labels hcom-polyglot WAV) |
| posttable | all 4 | R (RIFF/anon) | R (Invalid data) | R `Format not recognised.` |
| txw_piperefuse | file, redirected_fd | **A** txw 64 (r68) | R | R `unimplemented format` |
| txw_piperefuse | stdin_pipe, fifo_path | R `input must be a file, not a pipe` | R | R `unimplemented format` |
| extsuffix_wav | all 4 | R | R | R |
| extsuffix_bin | all 4 | R | R | R |
| extsuffix_txw | all 4 | R | R | R |
| extsuffix_f32 | file, fifo_path | **A** 128 samples (r69) | R | R (no `.f32` fallback) |
| extsuffix_f32 | stdin_pipe, redirected_fd | R | R | R |
| extsuffix_snd | file, fifo_path | **A** sndr 504 (r69) | R | **A** RAW|U-Law 500 |
| extsuffix_snd | stdin_pipe, redirected_fd | R | R | R |

Acceptance cell counts (of 36): **sox 11, ffmpeg 8, libsndfile 10.** Cell
classes: sox-only **4** (txw {file, redirected_fd}; f32 {file, fifo_path});
ffmpeg-only **3** (dec_act pipes); **sndfile-only 0**; sox+sndfile-only 2
(extsuffix_snd {file, fifo_path}); ffmpeg+sndfile-only 3 (dec_act pipes);
all-three 5 (dec_act/file, dec_hcom ×4); all-reject 22. Member-level classes:
dec_hcom = all-three/all-arms; dec_act = mixed (sox file-only; the other two
all-arms); txw_piperefuse and extsuffix_f32 = sox-only (arm-qualified);
extsuffix_snd = sox+sndfile; posttable / extsuffix_{wav,bin,txw} = none.

## Claim audit (each clause, against the sources above)

- **"sox-only: txw-seekable/.f32-named" — CONFIRMED.** 4 cells: txw on the two
  seekable arms, .f32 on the two named arms; both rejected by ffmpeg and
  libsndfile.
- **"sndfile-only: .snd-named" — NOT CONFIRMED as an acceptance class.**
  Measured: extsuffix_snd {file, fifo_path} is accepted by **both** sox
  (`sndr`, 504 samples, r69 receipt) and libsndfile (`RAW (header-less)/U-Law`,
  500 read frames); ffmpeg rejects all 4 arms. The frontier report itself
  frames it as vs-ffmpeg (`fa-sndfile.md:101-102`: *"libsndfile accepts, ffmpeg
  rejects: extsuffix_snd on named arms (the name fallback — the single
  libsndfile-only acceptance here)"*). What IS sndfile-unique on this corpus:
  (a) the **mechanism** (post-sniff filename fallback; sox reaches the same
  member through its ext-gated `sndr` CHECK row), and (b) a **verdict tier no
  other decoder has**: txw = magic-recognized-then-refused
  (`unimplemented format`) vs `Format not recognised` for true no-magic bytes.
- **"ffmpeg superset on detect" — TRUE only against libsndfile's detected-type
  set, and only on detect (not acceptance).** Measured detected labels on the
  9 members: ffprobe {wav, hcom} ⊋ libsndfile {WAV} (both polyglots labeled
  WAV; no HCOM reader in this build). sox's detected set {act, hcom, txw,
  sndr} is incomparable to ffprobe's (sox detects txw/sndr, ffprobe doesn't;
  ffprobe detects dec_act as wav, sox as act). On **acceptance**, no decoder's
  set contains another's: sox 11 ⊅ sndfile 10 ⊅ ffmpeg 8; ffmpeg-only cells
  exist (dec_act pipes), sndfile-only-vs-ffmpeg cells exist (.snd named).
- **Overall lattice claim ("distinct decoder-coverage classes") — CONFIRMED
  as a 6-way arm-qualified member partition**: {dec_hcom all-three-all-arms},
  {dec_act mixed}, {txw_piperefuse sox-only-seekable}, {extsuffix_f32
  sox-only-named}, {extsuffix_snd sox+sndfile-named}, {posttable,
  extsuffix_wav, extsuffix_bin, extsuffix_txw none}. No sndfile-only and no
  ffmpeg-only *member* class exists on this corpus.

## Conflicts / findings reported verbatim for the canonical judge

- **F1 — `fa-sndfile.md:65` numeric slip.** Frontier table says extsuffix_f32
  *"**decode 75, exit 0** on named arms"*. The committed receipt it is
  summarizing — `corpus/live/runs/20261014T140639114072Z-transport-extsuffix-f32-r69/measurements.json`
  (`a89d6fcf…`) — records `samples_read: 128` on **both** `file` and
  `fifo_path` (and its own fork message: *"file/fifo_path=decode 128 samples"*);
  `reports/round-69/r69-author.md:27` says *"decode **128 samples**"*; the
  reviewer's `lattice.tsv` row also reads `-/0/128`. "75" matches the r69
  scribe's **300-byte synthetic body A** (300/4 = 75), not the canonical
  512-byte member. Receipts say 128.
- **F2 — brief phrase "sndfile-only: .snd-named" vs measured shared
  acceptance** (see claim audit; sox also accepts those cells). Reported, not
  adjudicated.
- **F3 — "ffmpeg superset on detect" needs a scope qualifier**: measured true
  only as ffprobe {wav,hcom} ⊋ libsndfile {WAV}; not true of sox's detect set
  and not true of any acceptance set (numbers above).
- **F4 — provenance note (r71 residue, no verdict impact).** The frontier
  extract and the reviewer lattice cite **different receipts** for the same
  ffmpeg measurements (`…140155796326Z-normal` vs `…141033155858Z-ffprobe-transport-r71`).
  Both exist; lattice fields agree 36/36 across all three r71 receipts; only
  `ffprobe_error` text (absolute path / `pipe:` vs normalized `<input>`) and
  verdict-group shape differ — the known r71 D2 defect, fixed at `77768fa`.
  Anyone byte-comparing r71-era receipts must expect that diff.
- **F5 — host-state note.** ~20 long-lived leaked `ffmpeg` reader processes on
  dead fifos are still resident (`ps`: 16 on `r67-boundary/probes/.fifo_probe`,
  3 on `r67-author/fifo/*.wav`, 1 on `r67test.wav`; etime ≈ 9h15m, 0.0% CPU,
  e.g. PIDs 1930577…, 1999783…). Pre-round residue; no r72 measurement impact
  observed. In-flight sibling seats add transient ffmpeg processes (78 total
  `ffmpeg` PIDs at 14:21Z) — not leaks from this seat (this seat started none).
  r71's own runs reaped cleanly (per its author report).

## Gates

| gate | state at snapshot |
|---|---|
| author landing (`--probe-sndfile-transport-r72` + receipts) | **OPEN — absent, not failed** |
| insertion-only / prior rows byte-stable | **not exercisable** (no insertion; fixture == HEAD, no tracked diff) |
| verifier replay on committed tree | not run (r72-verifier scratch empty at 14:20Z) |
| adjudicator / report-last | not run (no r72 report-last commit) |
| provenance (my audit) | prior-verdicts 72/72 vs cited receipts; sndfile frontier×reviewer 36/36; ffprobe fields across 3 receipts 36/36 |

## Touched surfaces

- Wrote **only**: `reports/round-72/r72-scribe.md` (this file) and
  `corpus/live/r72-scribe/{lattice_extract.py, lattice-verified.tsv, checks.txt}`.
- `git status --porcelain` after writing: only untracked `corpus/live/r72-*/`
  scratch dirs (plus pre-existing untracked r71 files) — **no tracked file
  modified, no git mutation, no product-code edit**.

## Out-of-scope (explicitly not done)

- Implementing the r72 probe arm or any fixture/harness change (author's move;
  scribe seat forbids product-code edits).
- Re-running libsndfile/sox/ffmpeg measurements (frontier + reviewer already
  measured; no re-run to decorate the report).
- Verification/adjudication (verifier/critic/boundary/reviewer/judge seats).
- Commit/push/publish (operator-owned).

## Artifact paths + hashes (snapshot)

- This report: `reports/round-72/r72-scribe.md`
- Scratch: `corpus/live/r72-scribe/lattice_extract.py`;
  `lattice-verified.tsv` (`f58c51ccac4e7a3917e9e5a060ad50af026b2a4d3362a68773fec92e62ee00e1`);
  `checks.txt` (`d4358c027e5755c03050f59bc5cf4ae318ba44941ba71a87e13299c136b79160`)
- Frontier: `reports/frontier/fa-sndfile.md` (`33c3be10…`);
  `corpus/live/frontier-sndfile/runs/sndfile-matrix.json` (`466516f9…`),
  `prior-verdicts.tsv` (`89caf693…`), `extsweep.json` (`de58146f…`),
  `probe_sndfile.py` (`8081097c…`), `logs/info-*.txt`
- Receipts: `corpus/live/runs/20261014T140155796326Z-normal/measurements.json`
  (`c584b0d0…`); `…141033155858Z-ffprobe-transport-r71/measurements.json`
  (`578cad95…`); `…140639114072Z-transport-extsuffix-f32-r69/measurements.json`
  (`a89d6fcf…`); r67/r68/r69 member receipts as cited in `prior-verdicts.tsv`
- Sibling scratch (not evidence, cross-check only):
  `corpus/live/r72-reviewer/sndfile-matrix.json` (`c06d3215…`),
  `lattice-classes.txt` (`ffb4d19c…`), `probe_sndfile_r72.py` (`b7ec38ab…`);
  `corpus/live/r72-boundary/prior-verdicts.json` (`43b6350f…`)

## Exact commands / exits (appendix)

```sh
cd ~/Projects/shokunin/audio-shokunin
grep -c sndfile corpus/fixtures/measure_audio.py corpus/fixtures/build_artifacts.py   # 0, 0
grep -n 'probe-ffprobe-transport-r71' corpus/fixtures/measure_audio.py                # :881 (newest flag)
git hash-object corpus/fixtures/measure_audio.py                                      # bae5de49… == HEAD blob
git rev-parse HEAD:corpus/fixtures/measure_audio.py                                   # bae5de49…
git status --porcelain                                                                # no tracked mods (only ?? r72-*)
grep -rl sndfile corpus/live/runs/*/measurements.json                                 # (none)
python3 corpus/live/r72-scribe/lattice_extract.py                                     # exit 0
#   -> prior-verdicts rows verified against cited receipts: 72/72 (mismatches=0)
#   -> libsndfile frontier-vs-reviewer cells: 36/36 identical (diffs=0)
#   -> sox-only cells: txw_piperefuse/{file,redirected_fd}, extsuffix_f32/{file,fifo_path}
#   -> sndfile-only cells: none ; ffmpeg-only cells: none
python3 -c "import ctypes; lib=ctypes.CDLL('libsndfile.so.1'); lib.sf_version_string.restype=ctypes.c_char_p; print(lib.sf_version_string())"   # libsndfile-1.2.2
sha256sum reports/frontier/fa-sndfile.md corpus/live/frontier-sndfile/runs/*.json …   # hashes above
```

Exit codes: all inspection commands above exited 0. The only non-zero exits
seen this session were two `ls` misses — the initial wave-dir path probe
(exit 2, the wave tree lives outside the lane repo) and `ls reports/round-72`
(exit 2 before this directory was created).

**Seat stop.** Report complete; no further action taken (leaf, no dispatch, no
commit).
