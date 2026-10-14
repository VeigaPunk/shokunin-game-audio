# R65 verifier (named NON-AUTHOR) — preemptor-collision ordering, committed-state replay

Seat: verifier (non-author). Target: commit `1b0d276` ("audio r65: preemptor-collision
autodetect ordering — tracked pair family + 4 seat reports"), HEAD of canonical repo
`~/Projects/shokunin/audio-shokunin`. Worktree `~/Projects/prymeagnt/audio` reaches the
same tree through the `.shokunin/audio` symlink.
Host: SoX_ng v14.8.0.1 (`/usr/bin/sox`), ffmpeg/ffprobe n9.0.1, python 3.14.7, numpy 2.5.3 —
same toolchain the author/critic report.

Method note: the committed `run_ledger.py` writes its TSV over the tracked
`corpus/live/r65-author/ledger-r65.tsv`. Per LEAF no-touch rules I ran the equivalent
committed-state re-run: `replay_ledger.py` under `corpus/live/r65-verifier/` — a verbatim
copy with exactly one line changed (the TSV output path). Command list, working directory,
and receipt handling are identical (`diff` confirms a single-line delta). Receipt files land
in untracked `corpus/live/runs/<stamp>-<suffix>/` as every prior replay has done.

## Verdict: AGREE on all five claims — every number reproduced on committed bytes

| # | claim | verdict |
|---|---|---|
| 1 | order gsrt < hcom < act < wav, first-match-wins, on tracked family | **AGREE** |
| 2 | ledger 96 cmds, 44 exit 0 / 52 exit 1, 92 prior receipts byte-identical | **AGREE** |
| 3 | sole-diff spans act↔gsrt 17–25, act↔hcom 66–69+129–132 | **AGREE** |
| 4 | critic counterexample: hcom-shaped RIFF decodes 9 samples @22050 | **AGREE** |
| 5 | no tracked mutation outside 2 fixture .py + pair files + __pycache__ | **AGREE** |

## Claim 1 — detection order on RIFF+0x84@256 (AGREE)

Direct replay on the committed members (`corpus/live/round-65/`), command
`sox -V6 pair_preempt_<m>.wav -n stat`, exits captured without pipe masking:

| member | detected | autodetect outcome | `-t act` leg | `-t wav` leg |
|---|---|---|---|---|
| `pair_preempt_act.wav` | `act` | `(ffmpeg)` bridge, Samples read 3839, exit 0 | 3839, exit 0 | exit 2 `number of valid bits exceeds the number of bits per sample` |
| `pair_preempt_gsrt.wav` | `gsrt` | FAIL `premature EOF`, exit 2 | FAIL `premature EOF`, exit 2 | exit 2 `file encoding 0x622e (Unknown) is not supported` |
| `pair_preempt_hcom.wav` | `hcom` | FAIL `bad compression type`, exit 2 | FAIL `premature EOF`, exit 2 | exit 2 `number of valid bits exceeds…` |
| `pair_preempt_both.wav` | `gsrt` | FAIL `premature EOF`, exit 2 | FAIL `premature EOF`, exit 2 | exit 2 `file encoding 0x622e …` |

The `both` member carries all three predicates yet detects `gsrt` — the ordering pin
(gsrt ≺ hcom, gsrt ≺ act). The `hcom` member detects `hcom` over `act` (hcom ≺ act).
The `act` control detects `act` over the RIFF-fallback `wav` row (act ≺ wav). Byte 256
is `0x84` on all four members (verified `xxd -s 256 -l 1 -p`). Total order
**gsrt < hcom < act < wav** confirmed on committed bytes — matches author report
§"Live routing" and critic's tracked-controls table verbatim.

Measurer-flag legs (the committed measurement block): the ledger rows 2–5 ran
`--probe-ui-preempt-{act,gsrt,hcom,both}-r65`; receipts record
`sox_detected_format` = act/gsrt/hcom/gsrt, `sox_route` = ffmpeg/native/native/native,
`decode_error_tool: "ffprobe"` on the three colliders — all fields as claimed.

Cross-check on author's committed scratch variants (`r65-author/variants/`),
`sox -V6` detection only: `b_gsrt`→gsrt, `b_hcom`→hcom, `b_both`→gsrt,
`b_gsrt_x24`→act, `b_hcom_x131`→act, `b_hcom_fssd_only`→act, `b_base00`→wav,
`m_hcom`→hcom, `m_gsrt25`→gsrt — consistent with `results.tsv` on every row probed
(9/9 spot-checked).

## Claim 2 — ledger replay (AGREE)

My re-run (`cd ~/Projects/prymeagnt/audio && python3
.shokunin/audio/corpus/live/r65-verifier/replay_ledger.py`): all 96 commands executed.

- Exit tally: **44 exit 0 / 52 exit 1** — matches the committed `ledger-r65.tsv`
  (its own tally is also 44/52; r64's committed TSV is 44/48).
- Full-row comparison vs committed r65 TSV: all 96 rows match on exit code AND
  failure-summary text — 0 mismatches.
- Prior-92 mapping (my rows {1}∪{6–96} vs r64 rows 1–92): exit sequence
  position-identical (0 mismatches), failure summaries verbatim (0 mismatches),
  **all 92 fresh receipts byte-identical to the committed r64 receipt files**
  (`corpus/live/runs/20261014T0039*-20261014T0040*/measurements.json`, tracked).
- Bonus: the author's own recorded prior-92 receipt files (paths in the committed
  r65 TSV, all present) are likewise byte-identical to the r64 receipts — 92/92, 0
  missing, 0 mismatches (replication of `compare_receipts.py` semantics against
  committed data).
- New-mode determinism: my four fresh `--probe-ui-preempt-*-r65` receipts
  (`20261014T0202{568,578,589,600}*`) are **byte-identical** to the author's
  recorded receipts (`20261014T01433{1736394,2805968,3872621,4931555}*`).
- Normal-run receipt also byte-matches r64's committed normal
  (`20261014T003914751250Z-normal`) — covered inside the 92-byte-compare.

## Claim 3 — sole-diff pairs (AGREE)

`cmp -l` (1-based byte offsets) on committed members vs `pair_preempt_act.wav`:

- act↔gsrt: offsets **17–25**, 9 bytes — exactly the `ring.bin\0` span. Nothing else.
- act↔hcom: offsets **66–69 + 129–132**, 8 bytes — exactly `FSSD`@65 + `HCOM`@128.
- act↔both: 17–25 ∪ 66–69 + 129–132, 17 bytes (union; consistent with gsrt↔both =
  hcom spans and hcom↔both = gsrt span by construction).
- Member sizes all 11,588 B; sha256: act `cf5edecce181…`, gsrt `477bd371…`,
  hcom `bfc61413…`, both `a37adc7c…` — match author's table.
- `cmp pair_preempt_act.wav corpus/live/round-63/pair_route_84.wav` → byte-identical
  (author's "uncollided control" claim confirmed).

## Claim 4 — critic's hcom-decode counterexample (AGREE)

Committed exhibit `corpus/live/r65-critic/var/D1_hcomdecode+act.wav`
(600 B, sha256 `325fb967f0c9c126b7aaac5f580c92f7f3946a728c2c7323a1c8d497c23896cd` —
prefix matches critic's `325fb967`):

- `sox -V6 D1_hcomdecode+act.wav -n stat` → `` detected file format type `hcom' ``,
  `Input File … (hcom)`, Sample Rate 22050, **Samples read: 9, exit 0**.
- `sox --i` → `Input File '…' (hcom)`, `8-bit HCOM`, 22050 Hz.
- `sox -t wav … -n stat` → **Samples read: 278** — the same byte-stream decodes as
  wav under force, per the critic's "one stream, three working readers" note.

A RIFF+0x84 file detected `hcom` CAN fully decode via the native hcom reader —
reproduced exactly. The round's corrected outcome clause stands.

## Claim 5 — no tracked mutation outside declared set (AGREE)

- `git show --diff-filter=M HEAD` → exactly 4 paths:
  `corpus/fixtures/build_artifacts.py`, `corpus/fixtures/measure_audio.py`,
  `corpus/fixtures/__pycache__/build_artifacts.cpython-314.pyc`,
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`.
  Deletions: 0. Everything else (pair files, reports, ledgers, scratch) is Adds (285).
- Fixture diffs are additive-only as claimed: +40/−1 builder
  (`build_ui_preempt_r65_probe` + 4 flags + newest-first dispatch head), +65/−4
  measurer (4 flags, mutual-exclusion sum, forwarding, one measurement block,
  `mode`/`suffix` chain heads). Both scripts parse (`compile()`), `git diff --check
  HEAD` clean.
- Working tree: 0 modified/deleted tracked files before AND after my full
  96-command replay — every tracked artifact/pair rewrite regenerated byte-identical
  content (deterministic build verified end-to-end; sha256 pre/post match on all 21
  hashed tracked wavs).

## Residual observations (non-blocking, for the record)

1. r65 ledger receipt paths are **untracked** working-tree files
   (`corpus/live/runs/20261014T0143*-20261014T0145*/`), whereas r64's ledger
   receipts were committed. Contents verified byte-identical both ways, so this is
   a tracking asymmetry, not an evidence gap — parent may want to commit them as
   r64 did.
2. `sox_route`'s `(ffmpeg)`-substring fallback can never fire on failed opens (no
   `Input File` line) — dead logic; `sox_detected_format` carries the verdict.
   Same note as critic's minor (a); cosmetic.
3. Receipt stderr tails embed the absolute repo path inside a 160-char window —
   byte-determinism holds only for same-root replays (simplifier replica receipts
   differ from author's solely in that path slice; verified — line 389 `act`,
   line 365 others). Environmental, not measurement nondeterminism.
4. Running the committed measurer necessarily rewrites tracked pair/artifact wavs
   in place (mtime changes, bytes identical — `git status` clean). A replay
   cannot avoid this; it is the fixture design, disclosed here for transparency.
5. Scope: ordering claim verified on this host's SoX_ng 14.8.0.1 + ffmpeg n9.0.1
   only; the `act` row is `#if USING_FFMPEG` (author's UNKNOWN — restated, not
   re-tested). No lsp device on this substrate — all checks were direct
   executions against committed bytes, stronger than symbol queries here.

## Receipts

- Scratch: `corpus/live/r65-verifier/` — `replay_ledger.py` (verbatim copy, TSV
  path redirected), `ledger-r65-verifier.tsv` (96 rows), `pre-run-hashes.txt`.
- Fresh run receipts under `corpus/live/runs/20261014T0202*`–`20261014T0204*`
  (untracked, per convention).
- No commits/push/merge/stash/checkout performed; tracked files untouched
  (0 M/D verified post-run; two incidental `__pycache__` outputs I generated in
  `r65-author/` were untracked and have been removed).
