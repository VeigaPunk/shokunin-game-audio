# R72 boundary — third-decoder (libsndfile 1.2.2) arm executed in boundary scratch (author landing ABSENT at report time): fresh 9×4 matrix is 36/36 field-identical to the frontier harness; lattice claim audited — sox-only CONFIRMED, **sndfile-only class EMPTY (.snd-named is sox∩sndfile)**, ffmpeg-superset holds only as a detect-label refinement on co-accepted members; edge probes: NO fifo writer-hold band (50/50), 12-byte sniff probe is consumed by the raw fallback (ULAW reads 500 of 512 frames), tier onset exactly 12 B, fallback is case-insensitive

Seat: **boundary** (leaf). Lane: audio. Repo: `/home/vgpnk/Projects/shokunin/audio-shokunin`.
Host: python 3.14.7, libsndfile **1.2.2-4** (`sf_version_string()` = `libsndfile-1.2.2`),
SoX_ng **v14.8.0.1**, ffprobe/ffmpeg **n9.0.1**, kernel 7.2.3-arch1-3.
Observation snapshot: 2026-10-14 ~14:25 UTC; HEAD **`c079aba`** (wave-10 report-last).
Author landing for r72 is **absent** at snapshot (`grep -c sndfile corpus/fixtures/measure_audio.py` → 0;
newest probe flag is still `--probe-ffprobe-transport-r71`, `measure_audio.py:881`);
`reports/round-72/r72-scribe.md` exists (its verified lattice is cited below as corroboration).
No `lsp` device exposed in this seat window; all checks by direct measurement + read/grep.
Write scope respected: this file + `corpus/live/r72-boundary/` only; no tracked file modified
(`git hash-object corpus/fixtures/measure_audio.py` = `bae5de49…` = `HEAD:…`), no git mutation.

## What this seat executed (and why in scratch)

The round MOVE (`add --probe-sndfile-transport-r72 … sndfile_*_r72_probe`) has two halves:
the tracked-fixture insertion (author's scope, not landed) and the measurement itself.
Boundary executed the measurement half as a scratch arm mirroring the r71 ffprobe arm shape
(`measure_audio.py:570-730`: detection leg + decode leg + 4 transports + verdict groups +
fork pin + `_r72_probe` receipt family) — this is exactly the boundary convention of r71
(`reports/round-71/r71-boundary.md`): probe the move's mechanics independently, keep receipts
in the seat scratch. The scratch receipts below are **not** committed evidence; the verifier
must replay the author's landed arm when it exists.

Harness: `corpus/live/r72-boundary/probe_sndfile_r72.py` (`c8813bbc…`) — ctypes
`sf_open`/`sf_open_fd` + `sf_readf_short`, 15 s arm timeout (SIGALRM), per-arm fresh fds,
per-arm fifo+writer, plus the `sndfile-info` CLI detection leg on the file arm
(path-normalized to `<input>`; exit recorded — it is 0 on all 9 members incl. the 4 rejects).

Receipts (mode `probe-sndfile-transport-r72`, keys `sndfile_<member>_r72_probe`):
- `corpus/live/r72-boundary/runs/20261014T141950676005Z-sndfile-transport-r72/measurements.json`
- `corpus/live/r72-boundary/runs/20261014T142002371100Z-sndfile-transport-r72/measurements.json`
- both sha256 **`1cef6941de3bcbb413a545803fd785848c0d432696f3a50d233bb9f9b1a4b60b`** (byte-stable, json-normalized diff = empty)
- earlier buggy run (`…141931…`, `239fab18…`) kept only as provenance (CLI leg had a
  cwd-relative path bug; matrix arms unaffected).

## Fresh 9×4 matrix (independent re-run, all measured this seat)

`f`=file, `s`=stdin_pipe, `r`=redirected_fd, `F`=fifo_path; verdict = `format_name:read_frames`
(or `REJ` + error). Full field-level axis in the receipt.

| member | file | stdin_pipe | redirected_fd | fifo_path | fork |
|---|---|---|---|---|---|
| dec_act | WAV/PCM16:278 | WAV/PCM16:278 | WAV/PCM16:278 | WAV/PCM16:278 | no |
| dec_hcom | WAV/PCM16:278 | WAV/PCM16:278 | WAV/PCM16:278 | WAV/PCM16:278 | no |
| posttable_nomatch | REJ `Format not recognised.` | REJ | REJ | REJ | no |
| txw_piperefuse | REJ `…unimplemented format.` | REJ | REJ | REJ | no |
| extsuffix_wav | REJ | REJ | REJ | REJ | no |
| extsuffix_bin | REJ | REJ | REJ | REJ | no |
| extsuffix_txw | REJ | REJ | REJ | REJ | no |
| extsuffix_f32 | REJ | REJ | REJ | REJ | no |
| extsuffix_snd | RAW/U-Law:500 | REJ | REJ | RAW/U-Law:500 | **yes** |

- Cross-check vs `corpus/live/frontier-sndfile/runs/sndfile-matrix.json`: **0 field diffs over
  9 members × 4 arms × {format_name, format_check, read_frames, samplerate, channels,
  sf_seekable, frames}** (script diff, exit 0). The one fork is the same {file, fifo_path}
  vs {stdin_pipe, redirected_fd} partition the frontier measured (and the scribe verified).
- `frames` on the fifo arm for extsuffix_snd = `INT64_MAX` (unknown length), read still 500 —
  length field, not verdict. dec_act/dec_hcom decode 278 on **all four** transports
  (transport-invariant), including the unseekable pipe.

## 3-decoder lattice (fresh sndfile arm + latest committed sox/ffmpeg receipts)

Baselines: latest committed receipts per mode (`corpus/live/r72-boundary/prior-verdicts.json`,
`43b6350f…`; run ids: r67 `…140657558238Z`/`…140655461558Z`, r68 `…140643200613Z`/`…140645235307Z`,
r69 `…140632996659Z`/`…140635039506Z`/`…140637075953Z`/`…140639114072Z`/`…140641162793Z`,
r71 `…141033155858Z-ffprobe-transport-r71`). Lattice artifact: `lattice.json` (`31c12204…`).

Acceptance per arm: sox `exit_code==0`; ffmpeg `ffmpeg_exit==0`; sndfile `read_frames is not None`.
Cell counts over 36: **sox 11, ffmpeg 8, sndfile 10** — identical to the scribe's
`reports/round-72/r72-scribe.md:118` (independent path: scribe re-read frontier+reviewer
matrices; this seat re-ran the decoder).

Member-level classes (any-transport acceptance), measured:
- **all three**: `dec_hcom` (all 4 transports each).
- **sox-only**: `txw_piperefuse` {file, redirected_fd} = the two **seekable** arms;
  `extsuffix_f32` {file, fifo_path} = the two **named** arms. → the brief's
  "sox-only: txw-seekable/.f32-named" is **CONFIRMED** (4 cells).
- **sndfile-only: ∅.** `extsuffix_snd` is accepted by **both** sox (det `sndr`, 504 samples,
  exit 0) and sndfile (RAW|U-Law, 500 read frames) on exactly {file, fifo_path}; ffmpeg
  rejects all 4. → "sndfile-only: .snd-named" is **FALSIFIED-AS-STATED**: there is no
  sndfile-only acceptance cell on this corpus. What is sndfile-unique is (a) the mechanism
  (post-sniff filename fallback vs sox's ext-gated `sndr` CHECK row) and (b) the verdict
  tier below — not the acceptance class. (Same conclusion as scribe F2.)
- **sox(file-only) + ffmpeg + sndfile**: `dec_act` (sox decodes only on `file`; the other two
  on all 4) — a mixed class, no sole owner.
- **reject-all**: `posttable_nomatch`, `extsuffix_{wav,bin,txw}` (each decoder rejects all 4,
  with three different error taxonomies).
- No ffmpeg-only member class exists.

Detect-label universes (measured): sox {`act`,`hcom`,`txw`,`sndr`}; ffmpeg {`wav`,`hcom`};
sndfile {`WAV/PCM16`,`RAW (header-less)/U-Law`} + the unique **recognition tier**:
`txw_piperefuse` → `File contains data in an unimplemented format.` on all 4 arms
(magic recognized, no reader) vs `Format not recognised.` for true no-match. → the brief's
"ffmpeg superset on detect" is **not true corpus-wide**: ffmpeg detects nothing where
sndfile detects RAW|U-Law (`.snd` named) or the txw recognition tier, and sox's set is
incomparable to ffmpeg's. The only reading that holds: on the members **both** ffmpeg and
sndfile accept (dec_act, dec_hcom), ffmpeg's label partition {wav,hcom} is a strict
refinement/superset of sndfile's single {WAV/PCM16} label. Acceptance is not superset in any
direction (sox 11 ⊅ sndfile 10 ⊅ ffmpeg 8; each pair has sole cells). (Same as scribe F3.)

Net: the "distinct decoder-coverage classes" claim is **CONFIRMED as an arm-qualified
6-way member partition** — {dec_hcom all-three-all-arms}, {dec_act mixed}, {txw_piperefuse
sox-only-seekable}, {extsuffix_f32 sox-only-named}, {extsuffix_snd sox+sndfile-named},
{posttable, extsuffix_wav, extsuffix_bin, extsuffix_txw none} — with **no sndfile-only and
no ffmpeg-only member class**.

## Boundary edge probes (scratch, `edge_results_probe-{a..e}.json`)

**a — fifo writer-hold sweep** (`dec_act`, `extsuffix_snd`; holds {0, .05, .2, .5, 1.0} × 5 reps):
**50/50 identical verdicts at every hold including 0** for both members — no transition band.
Contrast: the sox ffmpeg bridge needs a 1.0 s writer linger (r70 ladder; transition band) and
direct ffmpeg needs none (r71 probe A). Mechanism (consistent with frontier): libsndfile opens
the fifo once and reads to EOF; the writer's linger can only cost wall-clock. Elapsed per leg
≈ hold by construction (the arm's writer-join waits out the linger), so verdict distribution —
not elapsed — is the measure.

**b/e1 — truncation tiers (named file arm, basename preserved).** The content sniff needs
**exactly 12 bytes** before it will claim a format:
- `dec_act` (RIFF/WAVE): <12 B → `Format not recognised.`; 12–43 B → `Error in WAV file.
  No 'data' chunk marker.` (recognized, incomplete); ≥44 B opens WAV, `frames = data_bytes/2`
  exactly (44 B → opens with 0 frames; 64 B → 10; 600 B → 278).
- `txw_piperefuse` (LM8953@0): <12 B → `Format not recognised.`; ≥12 B → `File contains data
  in an unimplemented format.` So the "recognized-then-refused" tier onset is 12 B, not 6.
- `extsuffix_snd` (no-magic .snd): **even a 0-byte file opens** as RAW/U-Law, 8 kHz mono
  (fallback fires with no content at all); `frames` = file length; `read_frames = N−12` for
  N ≥ 16 (16 B → 4, 512 B → 500).
- `extsuffix_f32` (control): `Format not recognised.` at every prefix length — no `.f32`
  fallback.

**d/e2 — the 500-vs-512 gap is a decoder quirk, not harness noise.** Read-exhaust on the .snd
file arm: `read_counts=[500, 0]`, total 500, while `SF_INFO.frames=512`. 16-byte variants whose
first 12 bytes differ (0x00×12 vs 0xFF×12, same last 4) yield **identical samples**
(μ-law 0xAA = 5372; last4=0x00 → −32124): the raw-fallback reader starts at byte offset 12 —
the 12-byte sniff probe is consumed and never rewound. `dec_act` exhausts fully ([278, 0]).
This is measured behaviour of libsndfile-1.2.2 on this path; mechanism stated as inference.

**c — extension-case sweep** (identical 512-B no-magic bytes): the fallback is
**case-insensitive** — `.snd/.SND/.Snd/.sND`, `.au/.AU/.Au` → RAW/U-Law; `.gsm/.GSM` →
GSM 6.10 (read 2560); `.vox/.VOX/.Vox` → VOX ADPCM (read 1024); `.ulaw/.ULAW`, `.wav`, `.f32`
do not fire. Content precedence holds: RIFF bytes named `.snd`/`.SND` open as WAV/PCM16 278.
(Resolves the frontier's "case sensitivity unmeasured" gap.)

## Commands / exits (exactly as run)

```sh
cd ~/Projects/shokunin/audio-shokunin
python3 corpus/live/r72-boundary/probe_sndfile_r72.py        # exit 1 (by design: the one
#   measured fork is recorded as a failure entry; receipt printed; 9.0 s)
python3 corpus/live/r72-boundary/edge_probes.py a            # exit 0 (17.5 s)
python3 corpus/live/r72-boundary/edge_probes.py b            # exit 0
python3 corpus/live/r72-boundary/edge_probes.py c            # exit 0
python3 corpus/live/r72-boundary/edge_probes.py d            # exit 0
python3 corpus/live/r72-boundary/edge_probes.py e            # exit 0
python3 corpus/live/r72-boundary/build_lattice.py            # exit 0
sndfile-info <abs path>                                      # exit 0 on all 9 incl. rejects
```

Artifacts: `probe_sndfile_r72.py` `c8813bbc…`; `edge_probes.py` `5f236b0a…`;
`extract_prior.py` `53daf03b…`; `build_lattice.py` `c3973d14…`; `prior-verdicts.json`
`43b6350f…`; `lattice.json` `31c12204…`; `edge_results_probe-a..e.json`
`edbc0e94…/0e22820b…/9749fe56…/485ef4db…/13ed8ce3…`; logs `logs/info-*.txt` (9),
`logs/matrix-stderr.txt` `4e3fa323…`. Member bytes bound by sha256: dec_act `777b6764…`,
dec_hcom `325fb967…`, posttable `6373923f…`, txw_piperefuse `fd7911a3…`, all five
`extsuffix_*` identical `f073e70a…` (512 B each).

## Remaining unknowns / risks

- The author's landed arm (if it lands) will differ in receipt field shape from this scratch
  arm; verdicts should agree — the verifier should diff on verdicts, not bytes. The
  "insertion-only / prior rows byte-stable" gate is not exercisable from this seat (nothing
  inserted; `git status --porcelain` shows no tracked modification).
- The 12-byte sniff-probe consumption (first 12 bytes unreachable on the raw ULAW fallback
  path) is measured on this build only; other libsndfile builds may rewind. The `.au` arm
  showed the same 500 read; the mechanism is inferred.
- Frontier's remaining gaps stand: pure-FSSD HCOM unmeasured; `|cmd`/`/dev/stdin` spellings
  unprobed; `sndfile-info` on fifo paths not exercised via CLI (ctypes only).
- Host residue noted by the scribe (leaked ffmpeg readers on dead fifos from earlier rounds)
  is pre-existing; this seat left zero orphans (`pgrep -fa sndfile-r72` empty after runs,
  no `/tmp/sndfile-r72-*` left).

**Seat stop.** Measured output above; no edits outside the stated scope; no git mutation.
