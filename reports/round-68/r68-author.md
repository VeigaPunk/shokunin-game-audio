# R68 author — POST-TABLE FALLBACK measured: declared claim FALSIFIED-as-stated — the fork is NAME-resolvability, not seekability ({file,fifo_path}=wav-reader vs {stdin_pipe,redirected_fd}=can't-determine); txw pipe-refusal member pinned (true seekable fork at reader level)

host: devin (same lane as R61–R67)
Clean-before: canonical lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` HEAD `a0958a9`;
worktree `/home/vgpnk/Projects/prymeagnt/audio` (`.shokunin/audio` symlinks into the canonical repo).
Toolchain under test: SoX_ng v14.8.0.1 (`/usr/bin/sox` -> `sox_ng`), ffmpeg/ffprobe n9.0.1, python 3.14.7.

## Scoped move — declared falsifiable claim FALSIFIED-as-stated, actual axis measured exactly

The declared claim: *post-table fallback behavior forks on transport
seekability — a no-match member gets a different verdict/error signature on
`file`/`redirected_fd` vs `stdin_pipe`/`fifo_path`.*

**Measured outcome on `posttable_nomatch` (512 B, satisfies no CHECK row,
`detected file format type` absent on all four arms):**

| transport | named | seekable | detected | verdict |
|---|---|---|---|---|
| `file` | yes | yes | None | `RIFF header not found` (exit 2) |
| `fifo_path` | yes | no | None | `RIFF header not found` (exit 2) |
| `stdin_pipe` | no | no | None | `can't determine type of  \`-'` (exit 2) |
| `redirected_fd` | no | yes | None | `can't determine type of  \`-'` (exit 2) |

Verdict groups = **{file, fifo_path} vs {stdin_pipe, redirected_fd}** — the
fork partitions on NAMED, not seekable. `redirected_fd` is the falsification
arm: a seekable-but-anonymous input gets no fallback classification at all.
`fifo_path` is the other falsification arm: a non-seekable-but-named input
gets full fallback classification (extension → wav handler → reader verdict).
The declared seekable partition is not observed; the post-table fallback is
orthogonal to it.

## Mechanism (measured verdicts above; source corroborative)

`open_read` post-table path, verified local copy
`corpus/live/r64-reviewer/r64rev-formats.c:910-933` (== upstream tag
14.8.0.1): when `auto_detect_format` (formats.c:66-270) returns NULL,
`io_type == lsx_io_pipe` ⇒ `filetype = "sox"` — but that io_type is set only
by the `|cmd` popen opener (xfopen, formats.c:830-851); `-` keeps calloc
default `lsx_io_file` and fifo paths open as `lsx_io_file`. **On all four
ledger transports the only fallback classifier is
`lsx_find_file_extension(path)`** (util.c:130 — basename suffix after last
`.`): `file`/`fifo_path` carry `posttable_nomatch.wav` → ext `wav` →
`sox_find_format("wav", true)` → wav `startread` → `RIFF header not found`;
`-` has no extension → `can't determine type of %s \`%s'` with `type=""`
(the double space is the empty io-type string) on BOTH anonymous arms,
seekable or not. The `sndr` row (formats.c:247-248) is the only
extension-parameterized CHECK (`ext=="snd"` ∧ `\0\0`@0) — dead on a `.wav`
name; measured as corroboration in scratch (`probes/nomatch.bin` → named
arms `no handler for file extension \`bin'`, `probes/nomatch_noext` → named
arms `can't determine type of file \`...'` — namedness gates three distinct
fallback outcomes, seekability gates none).

Prefetch accounting (formats_i.c:178-219, upstream source at
`/tmp/sox_ng_src/sox_ng/src/`): on seekable inputs `lsx_readbuf_rewind` does
a true `rewind()`; on non-seekable it stashes the ≤257 prefetched bytes into
`ft->pending_buffer` (formats_i.c:207-216), which every subsequent
`lsx_readbuf` drains first — the fifo arm's identical `RIFF header not
found` verdict is the measured proof that the prefetched bytes are NOT lost
to the fallback reader. The "consumed on pipes" framing holds only for the
act/ffmpeg bridge child (r64 pending-buffer poison), which post-table never
reaches — no-match inputs have no route at all.

## Pipe-refusal member — txw chosen on byte cost, pinned as a true seekable fork

`txw_piperefuse.wav` (128 B): `LM8953`@0-5 detector magic (formats.c CHECK
txw row, 6 B) + 32-B reader header (tx16w.c WaveHeader_: filetype[6],
nulls[10], dummy_aeg[6], format 0xC9@22, sample_rate 3@23 → 1e5/6 Hz) + 96-B
deterministic payload. Measured matrix:

| transport | detected | verdict |
|---|---|---|
| `file` | txw | decode **64 samples**, exit 0 |
| `redirected_fd` | txw | decode **64 samples**, exit 0 |
| `stdin_pipe` | txw | `input must be a file, not a pipe` (exit 2) |
| `fifo_path` | txw | `input must be a file, not a pipe` (exit 2) |

A genuine {file,redirected_fd} vs {stdin_pipe,fifo_path} seekable fork —
but it lives at the READER's own `!ft->seekable` gate (tx16w.c:90-92, which
fires before any byte read), not in post-table fallback. The two r68 members
together separate the axes the declared claim conflated: post-table fallback
forks on name; reader-level pipe refusal forks on seekability.

**Byte cost (txw vs smp):** detector magic 6 B (`LM8953`) vs 17 B
(`SOUND SAMPLE DATA`); cheapest discriminating member 6 B vs 17 B (scratch:
`txw6.wav` → `file is truncated`, `smp17.wav` → `unexpected EOF in header` —
both pin refusal on pipes but fail seekable arms too); cheapest
**decode-positive** member 128 B vs ≥331 B for smp (112-B HEADERSIZE at
smp.c:32 + 4-B NoOfSamps + 2·N data + 215-B TRAILERSIZE at smp.c:74). txw
wins every byte-cost tier; the 128-B variant buys the positive-decode
control (`decode 64` vs `open refused`) rather than an error-vs-error pin.

## Tracked changes (additive only)

- `corpus/fixtures/build_artifacts.py` **+46/−1**: `build_ui_posttable_r68_probe()`
  writes both members to `corpus/live/round-68/`; two argparse flags; one
  newest-first dispatch arm (`main()` + builder). Builder output verified
  byte-identical to scratch probes and to a standalone rebuild
  (`sha256 6373923f…` / `fd7911a3…`, `cmp` clean).
- `corpus/fixtures/measure_audio.py` **+34/−3**: two flags; mutual-exclusion
  sum +2; two forwarding splats to `build_artifacts.py` (newest-first);
  `TRANSPORT_R68_MEMBERS` map; the r68 arm block prepended before the r67
  block (measure_audio.py:618-634) recording `transport_<member>_r68_probe`
  via the unchanged `transport_entry` machinery; `mode`/`suffix` chain heads
  prepended. No prior path, mode string, or helper touched.
- New member files (uncommitted working-tree, parent integrates):
  `corpus/live/round-68/posttable_nomatch.wav` (512 B, sha256
  `6373923ff849ed3868e76f827339827fe0a1b23f7bc413fd2573ef73681c92d7`),
  `corpus/live/round-68/txw_piperefuse.wav` (128 B, sha256
  `fd7911a3523d7bc9337ed58935b4a7e8b642f0f3bab864441fde4af51f01f504`).
  **The `.wav` extension on posttable_nomatch is part of the member
  contract** — the measured named-arm verdict is the extension fallback.
- No `lsp` device on this substrate — edits applied by hand against read
  file text per the fallback rule (same as r64-r67).
- Tracked `corpus/fixtures/__pycache__/*.cpython-314.pyc` differ —
  mechanical `py_compile` regeneration churn, same disclosure as r62-r67;
  parent decides.

## What ran — 114-command ledger (112 prior verbatim + 2 new modes at positions 2-3)

Commands `python3 .shokunin/audio/corpus/fixtures/measure_audio.py <flag>`
from the worktree root; receipts under `corpus/live/runs/<stamp>-<suffix>/`.
Runner `corpus/live/r68-author/run_ledger.py`; TSV `ledger-r68.tsv`;
comparison `compare_receipts.py`. Single contiguous clean run: **49 exit 0 /
65 exit 1**, zero UNPARSED (r67's 49/63 + the 2 new forking rows exit 1).

Prior-112 replay (r68 rows {1} ∪ {4-114} ↔ r67 rows {1-112}): exit sequence
position-identical and **all 112 receipts byte-identical** to the r67 receipt
files — `compare_receipts.py`: "112 prior-mode pairs checked, 0 mismatches",
exit 0.

New-mode receipts byte-deterministic across 3 runs each (sha256 `52bbb1a9…`
nomatch, `762aff12…` txw, ledger run + 2 standalone reruns):

- `--probe-transport-posttable-nomatch-r68` → exit 1,
  `runs/20261014T102301198816Z-transport-posttable-nomatch-r68/measurements.json`;
  fork `file/fifo_path=RIFF header not found vs stdin_pipe/redirected_fd=can't
  determine type of  \`-'`.
- `--probe-transport-txw-piperefuse-r68` → exit 1,
  `runs/20261014T102303207738Z-transport-txw-piperefuse-r68/measurements.json`;
  fork `file/redirected_fd=decode 64 samples vs stdin_pipe/fifo_path=input
  must be a file, not a pipe`.

Empirical sweep ahead of the tracked arm (scratch `run_matrix.py` →
`matrix-r68.json`): both members + `nomatch.bin`/`nomatch_noext`/`txw6`/
`smp17` variants — the tracked matrices reproduce the probes verbatim.
`gen_probes.py` regenerates the scratch fixtures deterministically.

Setup notes: `python3 -m py_compile` on both touched tracked scripts + the
scratch tools → exit 0; `git diff --check` → clean.

## Per-axis claim (author evidence only; verdict belongs to verifier + adjudicator)

- **depth**: post-table fallback is now a measured axis — the receipt proves
  the fallback classifier is the filename extension (name axis), isolates
  the reader-level `!seekable` gate as a separate true-seekable fork, and
  shows the ≤257-B prefetch is preserved (pending-buffer) for native
  fallback readers on non-seekable transports rather than consumed.
- **coverage**: +2 members over the post-table/pipe-refusal classes → the
  autodetect ledger now covers detection-match forks (r67), post-table
  no-match forks (this round), and reader pipe-refusal. Ledger 112→114
  commands.
- **calibration**: 112/112 prior receipts byte-identical; both new receipts
  byte-deterministic across 3 runs; builder reproduces members
  byte-identically.

## Conditional replay shape (for the non-author verifier)

114 commands = the r67 112 verbatim with
`--probe-transport-posttable-nomatch-r68` and
`--probe-transport-txw-piperefuse-r68` inserted newest-first at positions
2-3 (TSV order in `ledger-r68.tsv`). Expected 49 exit 0 / 65 exit 1; prior-112
receipts byte-identical to r67's; new receipts deterministic (fifo arm uses
the pinned 1.0 s writer linger; neither member engages the ffmpeg bridge so
no second-open dependency).

## UNKNOWNs / limits

- Verified on this host only: SoX_ng 14.8.0.1 + ffmpeg n9.0.1,
  `USING_FFMPEG` build (AUTO_DETECT_SIZE 257).
- The declared claim is falsified for THIS member shape (named `.wav`): the
  measured axis is name-resolvability, and within named arms the extension
  selects the fallback handler — other extensions give other reader
  verdicts (scratch: `.bin` → `no handler for file extension`), but the
  named-vs-anonymous partition is extension-agnostic (noext still forks
  `{file,fifo}` vs `{pipe,redir}`).
- `use_magic`/`--magic` path unexercised; `|cmd` popen inputs (the only
  `lsx_io_pipe` arm) unprobed — out of the 4-transport envelope.
- The `can't determine type of  \`-'` error records the whole FAIL line
  (no `':` post-quote pattern exists on that message) — verbatim, stable,
  but coarser than the normalized-message class of the other arms.
- No standards-conformance, fidelity, audibility, production, or promotion
  claim — local fixture measurements.

## Blockers

None. Zero subagents dispatched (LEAF per brief). No commit/push/merge
performed; parent integrates.
