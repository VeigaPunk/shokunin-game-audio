# R72 baseline — independent `--probe-sndfile-transport-r72` implementation, env-anchored replay

host: devin (`Linux plazir27 7.2.3-arch1-3`, `toolchain.txt`). Seat: baseline.
HEAD at dispatch/env-copy: **`c079aba`**; moved mid-window to `26baed1`
(14:27:07 UTC — canonical r72 author implementation), `4fff488` (14:27:51 —
report-last; swept this lane's then-current scratch into the index), and
`50f55eb` (14:33:33 — r71 `_tail` ASLR-tag fix, `measure_audio.py` again).
All mid-window events are disclosed below and absorbed by the env anchoring.

## What was built (the MOVE, in-scope)

The brief asks for `--probe-sndfile-transport-r72` mirroring the r71 ffprobe
arm: sndfile-info detection + an sf_read decode leg, receipt family
`sndfile_*_r72_probe` keyed member × transport. The seat rules confine writes
to this report + `corpus/live/r72-baseline/`, so the flag was added to a
**verified env copy** of `measure_audio.py` (the r62–r70 baseline
`measure-env` pattern) — `corpus/live/r72-baseline/measure-env/corpus/`:

- 28 files copied from the clean worktree; **28/28 sha256-EQUAL to their
  `git show HEAD:` blobs** taken while HEAD was `c079aba`
  (`env-proofs.txt`): `corpus/fixtures/{measure_audio,build_artifacts}.py`,
  all 17 `corpus/artifacts/*.wav`, and the 9-member corpus
  (`live/round-66/pair_dec_{act,hcom}.wav`, `live/round-68/{posttable
  _nomatch,txw_piperefuse}.wav`, `live/round-69/extsuffix_nomatch.{wav,bin,
  txw,f32,snd}`). `live/runs/` created empty for env receipts.
- `fixtures/sndfile_leg_r72.py` — new bounded-subprocess ctypes helper
  (libsndfile-1.2.2 via `libsndfile.so.1`): `info|read × path|fd` plus a
  `formats` mode dumping the SFC_GET_FORMAT_{MAJOR,SUBTYPE} name tables.
  Anonymous arms use `sf_open_fd(dup(0))` — the frontier seat's genuine
  anonymous bound.
- `measure_audio.py` env patch (`env-patch.diff`): **insertion-only vs
  `c079aba`** — one code block (`TRANSPORT_R72_MEMBERS = TRANSPORT_R71_MEMBERS`,
  `sndfile_format_names`, `sndfile_leg`, `sndfile_transport_matrix`,
  `sndfile_transport_entry`), the argparse line, one appended term in the
  mutual-exclusion sum, the dispatch loop emitting `sndfile_{member}_
  r72_probe`, and prepends to the mode/suffix chains
  (`probe-sndfile-transport-r72` / `-sndfile-transport-r72`). 3 `<` lines =
  the 3 extended chain lines; 261 `>` lines added; zero deletions of
  existing logic.

Per-arm leg shape (mirrors `ffprobe_leg`'s two-subprocess shape, same
`run()`/fifo-writer/reap machinery, `TRANSPORT_R72_ARM_TIMEOUT_S = 15`):

- **detection**: `sndfile-info <path>` on named arms {file, fifo_path} —
  parses `Format : 0x…` + `Frames : N|unknown` + the reject reason
  (exit is always 0; verdicts live in stdout). Anonymous arms detect via
  `sf_open_fd` SF_INFO in the helper (`sndfile_detect_via` records which).
- **decode**: helper `read` mode = `sf_open`/`sf_open_fd` +
  `sf_readf_short` drain to EOF → `sf_decode_frames`. Verdict groups:
  `transport_verdict_groups` key (format, decode frames, decode error);
  `sndfile_verdict_groups` key the detection signature alone — the r71
  `ffprobe_verdict_groups` analog.

## Run — measured

```sh
cd corpus/live/r72-baseline/measure-env/corpus/fixtures
python3 measure_audio.py --probe-sndfile-transport-r72
```

Four runs: **14:29:19Z, 14:30:42Z, 14:31:18Z, 14:40:58Z — all exit 1** (the
`extsuffix_snd` named-fork failure, the expected recorded fork), each ~20 s
wall. Receipts:

- `measure-env/corpus/live/runs/20261014T142919881580Z-sndfile-transport-r72/measurements.json`
- `…/20261014T143042951596Z-sndfile-transport-r72/measurements.json`
- `…/20261014T143118305627Z-sndfile-transport-r72/measurements.json`
- `…/20261014T144058134967Z-sndfile-transport-r72/measurements.json`

Runs 2–4 are **byte-identical ×3** (sha256 `5501f57053bb…`,
`receipt-shas.txt`) — including run 4, made AFTER a sibling sweep reverted
the patched env harness at 14:37:44Z and I re-applied the identical patch;
the receipt regenerated unchanged. Run 1 differs only in the fifo
`sndfile_frames` field (`null` → `"unknown"`) from a mid-window fidelity
fix — `sndfile-info` prints `Frames : unknown` for the RAW fifo, a distinct
verdict from a missing line. Zero writes to canonical `corpus/live/runs/`
(ROOT is `__file__`-anchored; canonical census 5293 → 5298 during the
window, +5 all sibling-stamped — `runs-canonical-{before,after}.txt`).

## Verdict matrix — reproduced independently

| member | libsndfile verdict (all from fresh env receipt) |
|---|---|
| `dec_act` | WAV/PCM16, **278 frames decoded on all 4 arms** — no fork (sox: file-only decode) |
| `dec_hcom` | WAV/PCM16, 278 frames on all 4 — hcom-polyglot labeled WAV (no HCOM in build) |
| `posttable_nomatch` | `Format not recognised.` ×4 |
| `txw_piperefuse` | **`File contains data in an unimplemented format.` ×4** — magic-recognized-then-refused tier |
| `extsuffix_{wav,bin,txw,f32}` | `Format not recognised.` ×4 — no `.f32`/`.txw` fallback |
| `extsuffix_snd` | **RAW (header-less)/U-Law, 500 frames on {file, fifo_path}; `Format not recognised.` on {stdin_pipe, redirected_fd}** — named/anonymous fork, identical partition to sox's sndr gate |

Detail worth pinning: `.snd` fifo decode = 500 frames with `sf_seekable=false`
and declared frames `unknown`/INT64_MAX; the `.f32` member is rejected by
libsndfile where sox's extension dispatch decodes 128 samples on named arms.

## Cross-implementation agreement — 36/36 arms

`impl-compare.txt` compares my env receipt cell-by-cell (format_name /
read_frames / error / sf_seekable / format_hex-as-int / declared frames) against:

- **canonical committed receipt** `corpus/live/runs/20261014T142733592435Z-
  sndfile-transport-r72/measurements.json` (author implementation,
  in-process ctypes + SIGALRM timeout, `sndfile_info_cli` on the file arm
  only — a structurally different harness): **36/36 arm verdicts EQUAL,
  0 DIFFER**, all `transport_fork` flags EQUAL.
- **frontier matrix** `corpus/live/frontier-sndfile/runs/sndfile-matrix.json`
  (`No Error.` → null): **36/36 EQUAL, 0 DIFFER**.

The canonical receipts `20261014T142{618,634,733}Z` are themselves
byte-identical ×3 (sha256 `f7faaedb375e…`) — so four harnesses agree on the
full 9×4 lattice.

## Prior rows byte-stable (receipt level)

`prior-rows-stable.txt`: committed r71 vs r72 receipts — all **17 shared
base measurements + all 6 comparison sections + thresholds IDENTICAL**;
r72-only keys are exactly the 9 `sndfile_*_r72_probe` entries. Insertion-only
at the receipt level, matching the diff-level proof.

## Claim adjudication — measured

Declared: "the 3-decoder verdict lattice partitions members into distinct
decoder-coverage classes (sox-only: txw-seekable/.f32-named; sndfile-only:
.snd-named; ffmpeg superset on detect)." `lattice.tsv` joins committed sox
(r67–r69), ffprobe (r71), and libsndfile (r72) receipts per member × arm:

- **Partition CONFIRMED.** Detection-cell counts: ffmpeg 8 < libsndfile 10 <
  sox 14; acceptance classes: all-three {dec_act, dec_hcom}, sox-only
  {txw_piperefuse on seekable {file, redirected_fd}; extsuffix_f32 on named
  {file, fifo_path}}, sox∩sndfile-¬ffmpeg {extsuffix_snd named}, none
  {posttable, extsuffix_{wav,bin,txw}} — 4 distinct coverage classes + the
  txw "unimplemented format" verdict tier unique to libsndfile.
- "sndfile-only: .snd-named" — **falsified as stated** (sox also decodes 504
  named via sndr); measured class is sox∩sndfile vs ffmpeg-reject. Matches
  the adjudicator's correction (`r72-adjudicator.md`).
- "ffmpeg superset on detect" — **falsified**: ffmpeg is the strictest
  detector on this corpus (libsndfile's acceptance is a strict superset of
  ffmpeg's: same content accepts + the `.snd` name-fallback arm ffmpeg
  lacks).

## Live-tree events during the window (observed, not mine)

- `26baed1` (14:27:07Z) landed the canonical `--probe-sndfile-transport-r72`
  implementation + 3 committed receipts — mid-window, while my env was being
  assembled. It also swept my scratch-as-of-then into the index: the
  committed env `measure_audio.py` blob sha256-equals the `c079aba` base
  (`33f0a577…` both ways — the env copy provably predates the canonical
  implementation), and `sndfile_leg_r72.py` went in byte-identical
  (`47bdc6e5…`). The agreement above is therefore two independent
  implementations, not a copy check.
- `4fff488` (14:27:51Z) report-last commit — committed seat reports +
  remaining scratch. The patched env `measure_audio.py` consequently shows
  ` M` vs HEAD — the delta to committed is exactly my insertion-only patch.
- `50f55eb` (14:33:33Z) r71 `_tail` fix — canonical `measure_audio.py`
  changed again post-26baed1; unaffected receipts (env-anchored).
- `f5d7faf` (14:37:44Z) "r72 reviewer-fold" — during this commit's worktree
  operations my patched env `measure_audio.py` was restored to the
  committed (pre-patch) blob, erasing the harness I had measured with. I
  re-applied the identical insertion-only patch (diff-verbatim:
  `env-patch.diff`) and re-ran at 14:40:58Z — the fresh receipt is
  **byte-identical** to the pre-revert runs, so the revert+restore round-
  trip is fully absorbed. The file currently shows ` M` vs HEAD = my patch.
- 3 additional untracked canonical `*-sndfile-transport-r72` receipts
  (142824/142841/142954Z) — sibling replays; same verdict content on spot
  check.
- ` M corpus/live/r72-verifier/lattice.json` — sibling edit in flight.

## Write-scope accounting

Wrote only: this report; `corpus/live/r72-baseline/` (`measure-env/` —
28 verified HEAD-equal copies + patched `measure_audio.py` +
`sndfile_leg_r72.py` + 3 fresh `live/runs/` receipts; `env-proofs.txt`,
`env-patch.diff`, `impl-compare.txt`, `lattice.tsv`, `prior-rows-stable.txt`,
`receipt-shas.txt`, `pre-state.txt`, `post-state.txt`, `toolchain.txt`,
`runs-canonical-{before,after}.txt`). No canonical `corpus/live/runs/`
writes, no tracked-file edits outside the scratch dir, no commits, no
pushes. Leaf seat — no dispatch performed. (Caveat: the parent sweep
committed part of the scratch mid-window at `26baed1`/`4fff488`; the
worktree state stands as recorded.)

## Residual gaps

- Anonymous-arm detection uses `sf_open_fd` (SF_INFO) rather than a CLI —
  `sndfile-info` takes paths only; the mechanism is recorded per arm in
  `sndfile_detect_via`. Same bound the canonical implementation chose.
- `sndfile_frames` on the `.snd` fifo is `"unknown"` (sndfile-info's Frames
  line) where SF_INFO reports INT64_MAX — mapped as equal in the compare;
  both mean "declared frame count unknown on unseekable RAW".
- Within-host: libsndfile 1.2.2-4 Arch build; the format set is compile-time
  (no TXW/HCOM readers here).
