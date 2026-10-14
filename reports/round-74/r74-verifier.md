# R74 verifier — replay of the committed lavf no-seek sweep + pw-cat ops-2

Round: 74. Wave: `shokunin-train-20261101-w13`. Seat: verifier (LEAF).
Author commit `168b165` (incl. critic/reviewer folds — fork_kind lattice,
falsified-claim comment). Replayed on committed tree at HEAD **`168b165`**
== author commit — zero delta to audit (`git diff 168b165..HEAD` empty;
`origin/main` still at `1ba8103`, commit is local-only as of writing).
Fixture sha `a5ad3651…` == `HEAD:corpus/fixtures/measure_audio.py`.

## Method / receipts

Fixture hardcodes receipt output to `corpus/live/runs/<stamp>-<suffix>/`
(no `--runs` flag); fresh receipts copied post-hoc into this seat's scope.

| run | mode | exit | receipt |
|---|---|---|---|
| 1 | `--probe-lavfsweep-r74` | 0 | `runs/20261014T154034384723Z-lavfsweep-r74/measurements.json` → `corpus/live/r74-verifier/runs/…/` |
| 2 | `--probe-lavfsweep-r74` | 0 | `runs/20261014T154138420733Z-lavfsweep-r74/measurements.json` → `corpus/live/r74-verifier/runs/…/` |
| 3 | `--probe-consumers-r73` | 1 | `runs/20261014T154324595001Z-consumers-r73/` |
| 4 | `--probe-sndfile-transport-r72` | 1 | `runs/20261014T154334689125Z-sndfile-transport-r72/` |
| 5 | `--probe-ffprobe-transport-r71` | 0 | `runs/20261014T154355215779Z-ffprobe-transport-r71/` |
| 6 | `--probe-transport-extsuffix-snd-r69` | 1 | `runs/20261014T154357226006Z-transport-extsuffix-snd-r69/` |
| 7 | `--probe-transport-txw-piperefuse-r68` | 1 | `runs/20261014T154359263500Z-transport-txw-piperefuse-r68/` |
| 8 | `--probe-transport-dec-act-r67` | 1 | `runs/20261014T154401381149Z-transport-dec-act-r67/` |

Exit=0 on the r74 arm is correct-by-construction — failures fire only on
prediction *deviation* (both directions), so `failures: {}` means every
declared cell held. Exit=1 on prior modes is the r67 convention (measured
forks recorded as failures). Stdout/stderr captures:
`corpus/live/r74-verifier/run{1,2}.stdout.json`, `prior-*.stdout.json`;
all stderr logs 0 bytes.

## Result: byte-level

- **run1 ≡ run2 ≡ author's newest run**: sha256
  `ebddda2506212f2e004ae019e0c1325435d0d90bb238a38722f442ac355cdb6a` on all
  three of `…T154034384723Z` (mine), `…T154138420733Z` (mine),
  `…T153739783116Z` (author's final pre-commit run, 15:37:39 UTC — 4 s
  before commit timestamp). **Byte-identical, including the wall_s leaf**
  (`target0_unlinked_stream.wall_s` = 4.002 in all three).
- vs the receipt the author report *cites* (`…T153027827786Z`): raw diff
  is exactly 7 lines — all seven are `fork_kind` field additions
  (`"output_rc"`×2, `"wound"`, `"truncation"`, `null`×3). That cited run
  predates the fork_kind fold; the fold is inside the same commit and the
  newest in-tree run matches HEAD-code output byte-for-byte. The citation
  is one fold behind the code — a naming quirk, not a measurement
  discrepancy (disclosed in the commit message's "+ critic/reviewer
  folds").
- **Member determinism**: `build_lavf_r74_members()` rewrote all six
  `corpus/live/round-74/` members on each of my two runs; `git status` on
  the directory stayed clean and sha256 prefixes match the author table
  exactly (`iss 4fbc2ca5`, `iss_multi 85a518c8`, `apc 684d2794`,
  `acm 5afaa65a`, `adx 3831ef47`, `aifc 23aa8a65`).
- **Insertion-only**: `git show 168b165` deletes only 6 comment lines
  (the r73 falsified-claim comment, restated to the adjudicated form —
  the disclosed fold) + the 3 mutex/mode/suffix chain lines (each
  re-emitted verbatim + the r74 clause). Zero prior-row code touched;
  zero `runs/` receipts committed (untracked by convention).

## Per-claim adjudication (all on my run-1 receipt unless noted)

### (a) `lavf_iss` output_rc fork — AGREE

`transport_verdict_groups`: `{file, redirected_fd}` → `[2,"iss",
"Operation not permitted"]` vs `{stdin_pipe, fifo_path}` → `[0,"iss",
null]`. `lavf_score`=100 on all four arms; `stream_not_seekable` and
`refresh_seek` track the seekable bit exactly. Same signature shape as
r73's dec_hcom. `fork_kind="output_rc"`, `predicted="fork"` held.

### (b) `lavf_apc` output_rc fork — AGREE

Identical partition: `[2,"apc","Operation not permitted"]` vs
`[0,"apc",null]`, score 100 throughout, `fork_kind="output_rc"`.

### (c) `lavf_acm` wound-level fork — AGREE

`{file, redirected_fd}` → `[0,"acm","Operation not permitted"]` vs
`{stdin_pipe, fifo_path}` → `[0,"acm",null]`, score 66. The fork lands on
`seek_failed` alone with rc=0 both sides — the ENOSYS/NOGENSEARCH-class
wound (demuxer survives the failed refresh seek), distinct from iss/apc's
output_rc wound. `fork_kind="wound"` correctly labels it.

### (d) `lavf_iss_multi` truncation fork — AGREE

Verdict groups `[0,"iss","Operation not permitted"]` vs `[0,"iss",null]`
and `extent_legs` (ao=pcm): file **516196 B / 5.851791 s** vs fifo
**520260 B / 5.897868 s**, `delta_bytes` **4064**, `truncated: true`,
`fork_kind="truncation"` (reviewer-F1 relabel present). Reproduced
byte-for-byte — rc0-with-lost-head, not the rc2 wound: corollary
CONFIRMED exactly as reported.

### (e) invariant controls — AGREE (all three)

`lavf_adx` → `[0,"adx",null]` ×4 arms (score 75, GENERIC_INDEX index-seek
rescue — refresh_seek fires on seekable arms yet no seek_failed);
`lavf_aifc` → `[0,"aiff",null]` ×4 (score 100, aiff read_seek);
`dec_act` → `[0,"wav",null]` ×4 (score 99). `transport_fork=false`,
`fork_kind=null`, zero failures on all three.

### (f) `mpv --start=2` position fork — AGREE

`lavf_startpos_wav_r74_probe` on `artifacts/stem_sections.wav`:
`pcm_out_duration_s` = {file 2.0, redirected_fd 2.0} vs {stdin_pipe 4.0,
fifo_path 4.0}; bytes 192068 vs 384068; all rc=0 `success (reason 0)`;
`position_fork=true`. Exact 2.0/4.0 s split — not approximate.

### (g) ops2 `fifo_no_writer_escalation` — AGREE

`blocked: true`, `wchan: "wait_for_partner"`, `sigterm_immune: true`
(survived the 1.0 s TERM window), `exit_code: -9` after `killpg` SIGKILL,
`waited_s: 3.0`. The kill-escalation rc cell is pinned as briefed.

### (h) ops2 `target0_unlinked_stream` — AGREE

`timeout -s TERM 4 pw-cat -p --target 0 <dec_hcom>` → `exit_code: 124`,
`wall_s: 4.002`, `term_terminable: true`, `stderr_tail: null`. The hang
is real (bounded at the wrapper) yet TERM-TERMINABLE — cleanly the
negative twin of (g)'s SIGTERM-immune open-block. Matches r73-boundary's
measured class.

### (i) ops2 `pwcat_raw_name_axis` — AGREE

Identical `extsuffix_nomatch.snd` bytes through `pw-cat -p --raw` on
fifos named `axis.{snd,wav,bin}` → `exit_code: 0` on ALL THREE, no
sndfile_error/pw_error. The ops-1 decode-layer fork {0,1,1} collapses —
the name axis dies without libsndfile. CONFIRMED.

### (j) ops2 `zero_sink_daemon` — AGREE

Private `pipewire` spawned under a scratch runtime dir: `socket_up:
true`, `audio_sink_count: 0` (pw-dump census), `pw-cat -p` blocked the
full 6.0 s → killpg SIGKILL → `exit_code: -9`, `blocked: true`; daemon
terminated in `finally`. Live session daemon (pid 1905) untouched — the
hang class reproduces.

### (k) member generation — AGREE

`lavfsweep_generation_r74_probe`: all 7 members `generated`, `blocked:
{}` — no fabrication path taken; regeneration byte-identical (above).

### (l) prior-row byte stability — AGREE

Six prior modes replayed; every fresh receipt **byte-identical**
(`cmp -s`) to the newest same-mode receipt in the tree:

| mode | ref (newest) | fresh | result |
|---|---|---|---|
| consumers-r73 | `…T153153302722Z` | `…T154324595001Z` | byte-identical (incl. wall_s leaves) |
| sndfile-transport-r72 | `…T153203364007Z` | `…T154334689125Z` | byte-identical |
| ffprobe-transport-r71 | `…T153224091499Z` | `…T154355215779Z` | byte-identical |
| transport-extsuffix-snd-r69 | `…T153226137588Z` | `…T154357226006Z` | byte-identical |
| transport-txw-piperefuse-r68 | `…T151124708058Z` | `…T154359263500Z` | byte-identical |
| transport-dec-act-r67 | `…T153104888889Z` | `…T154401381149Z` | byte-identical |

Fork failure strings reproduce verbatim (e.g. r73:
`file/redirected_fd=2/hcom/Operation not permitted vs
stdin_pipe/fifo_path=0/hcom/None`). The r74 arm perturbed no prior row.

## Determinism (run 2 vs run 1)

`--probe-lavfsweep-r74` second run: exit 0, `failures: {}`, receipt
**byte-identical** to run 1 — including the sole wall-clock leaf
(`target0.wall_s` 4.002 both times; the 4 s `timeout` bound makes the
leaf a near-constant, and this replay landed in the same ms bucket —
author's own runs show the leaf can drift: `…T153053…` recorded 4.001).
The arm is deterministic on this host to the byte.

## Notes / bounds

- Host gates held: PipeWire 1.6.8 live (`PulseAudio (on PipeWire 1.6.8)`
  via pactl, daemon pid 1905), mpv v0.41.0, ffmpeg n9.0.1 (lavfi synth +
  adx/aifc muxers present; iss/apc/acm muxers absent — hand-built
  members, as the brief allowed), `timeout` GNU semantics in use.
- Mechanism corroboration inside the receipt: every seekable arm
  attempts `refresh_seek` (adx/aifc/wav included) — only the no-seek
  demuxers return `seek_failed`, which is exactly the 4-clause rule.
- The author's cited receipt (`…T153027…`) is pre-fork_kind-fold; the
  newest committed-run receipt (`…T153739…`) is the correct byte-compare
  target and matches my replay exactly. Recorded as a citation quirk,
  not a defect — the report's measured VALUES are identical either way.
- `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` shows as
  modified — pre-existing bytecode-cache noise (dirty before my runs);
  no tracked content file touched by this seat. Sibling r74 reports
  (baseline/boundary/critic/reviewer/scout/scribe) sit untracked in
  `reports/round-74/` — left alone.
- acm member is a synthetic silence-recipe (subformat 0x7700, disclosed
  by the author): the fork evidence is the demuxer-level `seek_failed`
  signature, which is what the receipt keys on — the bound holds.

## Verdict

**AGREE on all twelve claim items (a–l).** The committed arm replays
byte-for-byte — my two runs and the author's final run share one sha256;
every predicted fork fired with its declared wound kind, every invariant
control held, both wound shapes and all four ops-2 cells reproduce
exactly, member generation is byte-deterministic, and six prior-mode
replays are byte-identical to their newest references.
