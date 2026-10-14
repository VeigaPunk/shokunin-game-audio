# R69 reviewer — audit of r68 committed state (`6c91040` work + `7b8d423` report-last)

Seat: **reviewer** — audit-only; no tracked mutation performed or proposed. Host:
`sox` = SoX_ng **14.8.0.1** (`/usr/bin/sox`, `txw`/`sndr`/`smp` present in `sox --help`),
ffmpeg/ffprobe n9.0.1, python **3.14.7** — identical toolchain to the r68 record.
Audited tree: canonical repo `/home/vgpnk/Projects/shokunin/audio-shokunin` @ HEAD
`7b8d423`; on-disk `corpus/fixtures/measure_audio.py` sha256
`f7da1e46eee51a44486eabc0f3d2df8d9250d725ad0005744ff6f46307a27de3` and
`corpus/fixtures/build_artifacts.py` sha256
`96bfc1eab6974a8494f2b75af1d60edaaaee71fcb17cc21ff08cd29a5f9931fd` — both
byte-identical to `git show HEAD:` **before and after** my replay (no in-flight
r69 author diff contaminated the audit window). Ledger re-run from the lane
worktree `~/Projects/prymeagnt/audio` so `.shokunin/audio` resolves through the
symlink, matching `run_ledger.py`'s invocation contract. Scratch:
`corpus/live/r69-reviewer/` (`r69rev_ledger.py`, `ledger-r69rev.tsv`,
`r69rev_compare.py`, `ledger-r69rev-compare.txt`, `ledger-r69rev-stderr.log`,
`raw/` arm outputs, `probes/`).

## Verdict summary

| audit item (per brief) | result |
|---|---|
| 114-row r68 ledger re-run on HEAD | **SURVIVES — full replay, not a spot subset**: 114/114 rows; **49 exit-0 / 65 exit-1 / 0 other, 0 UNPARSED** — identical tally and position-identical exit sequence vs committed `ledger-r68.tsv` (compare [a]) |
| fresh receipts vs committed r68 receipts | **SURVIVES — all 114 byte-identical** (compare [b], 0 mismatches); receipt-dir suffixes identical row-for-row (compare [c] — the committed path suffix names the mode, so the mode ORDER is verified, not just the set) |
| failure summaries | **SURVIVES** — committed TSV column 4 reproduced verbatim on all 114 rows (compare [d], 0 mismatches) |
| prior-112 chain | **SURVIVES** — my rows {1}∪{4–114} fresh receipts byte-identical to committed **r67** ledger receipts (compare [e]: 112 pairs, 0 mismatches); author's committed `compare_receipts.py` re-run on committed data → `112 prior-mode pairs checked, 0 mismatches` (exit 0) |
| 2 r68 probe modes | **SURVIVES, extended** — fresh row-02 receipt sha256 `52bbb1a9c9c0fc73c3c269809c10081e8832b2b6fe0e2910d0216e0a83e08b2b` = all **8** committed copies (now 9 independent byte-identical receipts); row-03 sha256 `762aff12c5c512bfa3871afb519869a5ac2c473a7853e837b5afd2dd841f66dc` = all 8 committed copies (now 9) |
| named-axis partition (posttable_nomatch) | **SURVIVES** — independent raw `sox -V6` matrix + committed receipt content both encode `{file,fifo_path}`→`RIFF header not found` vs `{stdin_pipe,redirected_fd}`→`can't determine type of  \`-'`, detected=None on all 4 arms |
| txw reader `!seekable` gate | **SURVIVES** — raw + receipt: detected `txw` on all 4 arms; `{file,redirected_fd}` decode **64 samples** exit 0 vs `{stdin_pipe,fifo_path}` `input must be a file, not a pipe` exit 2 |
| `.snd` ext-gate counterexample (detection forks on namedness) | **SURVIVES** — reproduced live: same 300-zero bytes detect `sndr` on a `.snd` name, `can't determine` on anonymous seekable `-` |
| falsified-as-stated declared claim | **CONFIRMED** — `redirected_fd` is seekable yet anonymous and gets NO fallback classification (`can't determine`); `fifo_path` non-seekable yet named gets the full extension-fallback reader verdict. Post-table fallback partitions on NAME, not seekability — the corrected mechanism the committed ledger encodes |
| member fixtures | **SURVIVES** — tracked `corpus/live/round-68/posttable_nomatch.wav` sha256 `6373923ff849ed3868e76f827339827fe0a1b23f7bc413fd2573ef73681c92d7`, `txw_piperefuse.wav` sha256 `fd7911a3523d7bc9337ed58935b4a7e8b642f0f3bab864441fde4af51f01f504` — both match the r68 report verbatim |

**No drift found between committed claims and re-executed reality. Zero findings.**

## Evidence detail

### Full-ledger replay (strongest level)

- Runner `corpus/live/r69-reviewer/r69rev_ledger.py` (independent copy of the
  committed `r68-author/run_ledger.py` MODES order — the order itself under
  test), each row `python3 .shokunin/audio/corpus/fixtures/measure_audio.py
  <flag>` from the worktree root; fresh receipts under
  `corpus/live/runs/20261014T1049*–1052*` (114 untracked dirs, by-design
  `measure_audio.py` output).
- `r69rev_compare.py` output verbatim (`ledger-r69rev-compare.txt`):
  ```
  [a] my exits: 49 exit-0 / 65 exit-1 / 0 other (committed r68: 49/65)
      exit mismatches vs committed r68: 0
  [b] fresh receipts vs committed r68 receipts: 0 mismatches
  [c] receipt-suffix (mode-order) mismatches: 0
  [d] failure-summary mismatches vs committed r68: 0
  [e] prior-112 pairs vs committed r67 receipts: 112 checked, 0 mismatches
  RESULT: ALL-CLEAN
  ```

### Raw transport matrices (own hands, `corpus/live/r69-reviewer/raw/`)

`posttable_nomatch.wav` (512 B): no `detected file format type` line on ANY
arm — file exit 2 `RIFF header not found`; fifo (mkfifo + one-shot write +
1.2 s linger) exit 2 `RIFF header not found`; stdin_pipe and redirected_fd
exit 2 `can't determine type of  \`-'` (double space = empty io-type).
Partition **{file, fifo_path} vs {stdin_pipe, redirected_fd}** = the named
axis; `redirected_fd` (seekable+anonymous) is the falsification arm —
rewind succeeds and buys nothing.

`txw_piperefuse.wav` (128 B): `detected file format type 'txw'` on ALL four
arms; file + redirected_fd → `Samples read: 64` exit 0; stdin_pipe + fifo →
`input must be a file, not a pipe` exit 2. A genuine **{file,redirected_fd}
vs {stdin_pipe,fifo_path}** seekable fork at the reader's own `!ft->seekable`
gate — orthogonal to the post-table axis. Both match the committed receipt
`transport_verdict_groups` verbatim (content-checked, not just bytes).

### `.snd` ext-gate counterexample — detection forks on name (probes/, raw/)

- `nd_zeros.snd` (300 zeros): named `file` arm → `detected file format type
  'sndr'` → sndr reader → `invalid rate value` exit 2; **identical bytes** on
  anonymous `redirected_fd` (seekable `-`) → NO detection → `can't determine
  type of  \`-'`. Detection itself forks on the transport name — the first
  counterexample to r67's detection-invariance, exactly as
  `corpus/knowledge/2026-10-14-sox-posttable-fallback.md:32` records.
- `zeros_d7zero.snd` (8 zeros + `\x11` pad, `data[7]=0`): named → `detected
  'sndr'` → `invalid rate value` (in-table CHECK row armed);
  `zeros_pad.snd` (`\0\0`+`\x11` pad, `data[7]=0x11≠0`): named → NO `detected`
  line → ext-fallback → same sndr reader → `can't find Sun/NeXT/DEC
  identifier` — both branches of boundary's E5 reproduced (CHECK-pass arm and
  CHECK-fail→extension-fallback arm); anonymous arms can't-determine on all.

### Namedness gates three distinct fallback outcomes (corroboration)

Identical 512-B `posttable_nomatch` bytes under three names: `.wav` → `RIFF
header not found` (wav-reader verdict); `.bin` → `no handler for file
extension \`bin'`; no-extension → `can't determine type of file \`...'` —
the extension-fallback ladder the author reported, verified live.

## Concurrent-execution note (observation, not a finding)

Sibling r69 seat scratch dirs (`r69-critic`, `r69-scout`, `r69-boundary`,
`r69-scribe`, plus a stray `corpus/live/corpus/` path — none mine) existed
untracked during my replay; my run still produced **0 UNPARSED and 114/114
byte-identical receipts** — consistent with the r67/r68 bound that the
build-artifacts mid-write flake is momentary and did not trigger in this
window. Serial-execution byte-stability claim holds.

Post-audit `git status`: **0 tracked modifications**; untracked = my
`corpus/live/r69-reviewer/` + the 114 `runs/20261014T1049*–1052*` receipts +
pre-existing sibling dirs (untouched).

## Findings by severity

- **HIGH/MED/LOW defects against r68 committed state: none.** Every audited
  item — the full 114-row ledger, both r68 probe modes, the named-axis
  partition, the txw reader gate, the `.snd` ext-gate detection fork,
  prior-receipt byte-identity (fresh-vs-r68 AND fresh-vs-r67), member
  digests, and the falsified-as-stated record — survives verbatim
  re-execution.

## Residual risk / verification gaps

- Byte-identity is a *re-execution* result (every row re-invokes live
  `sox`/`ffprobe` over the transports); it proves harness determinism and
  verdict reproducibility on this host, not source-level attributions
  (pending-buffer replay, `lsx_io_pipe` popen arm) — those rest on r68
  scout/critic strace evidence, not re-run by me this round (not required
  by the brief; verdict-level claims are what the committed record asserts).
- `zeros_d7zero.snd` named arm detected `sndr` but read `invalid rate value`
  rather than boundary's `decode 294` — different payload content (mine lacks
  a parseable rate header), same detection fork; the audited claim is the
  DETECTION fork on namedness, which reproduces exactly.
- Single host/toolchain: SoX_ng 14.8.0.1 USING_FFMPEG + ffmpeg n9.0.1;
  ext-gated CHECK behavior is build-local (standing bound).
- The r69 declared move (extension-suffix sub-axis + dead-CHECK census) is
  the author's in-flight diff — out of audit scope; `measure_audio.py` sha
  stable across my entire window confirms no contamination.

Leaf seat: no commits, no pushes, no tracked edits, no dispatches.
