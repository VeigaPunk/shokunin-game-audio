# R68 verifier — AGREE 5/5 (independent replay; committed state verified, not the author's claims)

seat: verifier (named, independent, non-author). Commit under test `6c91040`.
host: devin, same lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin` (ran
from the canonical repo root, not the worktree symlink — equivalent path).
Toolchain measured: SoX_ng v14.8.0.1 (`/usr/bin/sox`), ffprobe/ffmpeg n9.0.1,
python 3.14.7, numpy 2.5.3 — matches the author's declared toolchain exactly.
Replay window 20261014T1033–1037Z. Scratch: `corpus/live/r68-verifier/` only.

## What I ran myself (not the author's numbers)

- Full 114-command ledger replay: `corpus/live/r68-verifier/run_ledger.py`
  (independent copy of the author's MODES order — the order itself is under
  test — invoking the committed `corpus/fixtures/measure_audio.py` from the
  repo root). Output `ledger-r68-verifier.tsv`; 114 fresh receipt dirs under
  `corpus/live/runs/20261014T1033*–1035*`.
- My own compare `corpus/live/r68-verifier/compare.py` (positional exits +
  failure-summaries vs author's `ledger-r68.tsv`; my receipt bytes vs
  author's committed r68 receipts; my prior-112 receipt bytes vs committed
  r67 receipts).
- Raw `sox -V6 <input> -n stat` over all 4 transports on both members with my
  own hands (`raw-transports.txt`) — fork observed directly, not via receipt.
- Independent rebuild of `build_ui_posttable_r68_probe()`
  (`rebuild_members.py`, verbatim-ported generator into scratch) + `cmp`.
- sha256 re-hash of all 112 committed r67 receipt paths against the frozen
  baseline manifest `r68-baseline/committed-shas.tsv`.
- `git diff --name-status/--numstat a0958a9..6c91040` for the additive claim.
- Two standalone reruns of each new probe after the ledger (3 verifier
  receipts per probe total).

## Per-claim verdicts

### Claim 1 — posttable_nomatch fork is NAME-resolvability, not seekability — AGREE

My raw sox matrix (evidence `r68-verifier/raw-transports.txt`):

| transport | named | seekable | detected | observed verdict | exit |
|---|---|---|---|---|---|
| file | yes | yes | none (no `detected file format type` line) | `can't open input file ...: RIFF header not found` | 2 |
| fifo_path | yes | no | none | `RIFF header not found` | 2 |
| stdin_pipe | no | no | none | `can't determine type of  \`-'` (double space = empty io-type) | 2 |
| redirected_fd | no | **yes** | none | `can't determine type of  \`-'` | 2 |

Detected=None on all four arms (no CHECK row matches — confirmed
empirically, not just asserted). The partition **{file, fifo_path} vs
{stdin_pipe, redirected_fd}** is exactly what my receipt's
`transport_verdict_groups` encodes (receipt copy
`r68-verifier/receipt-nomatch-ledger.json`). Falsification-honest: the
declared seekability claim is falsified-as-stated — `redirected_fd` is
seekable yet anonymous and gets NO fallback classification (dies at
can't-determine), while `fifo_path` is non-seekable yet named and gets the
full extension-fallback reader verdict. What the committed ledger encodes
is the *corrected* mechanism: post-table fallback forks on
name-resolvability (`lsx_find_file_extension`), orthogonal to seekability.
That is what I verified — the corrected mechanism, not the falsified
declared claim.

### Claim 2 — txw_piperefuse true seekable fork at reader level — AGREE

My raw matrix: `detected file format type \`txw'` on all four arms;
{file, redirected_fd} → `Samples read: 64`, exit 0; {stdin_pipe, fifo_path}
→ `can't open input ...: input must be a file, not a pipe`, exit 2.
Partition **{file, redirected_fd} vs {stdin_pipe, fifo_path}** = a genuine
seekable fork, downstream of a real detection — matching the receipt
(`receipt-txw-ledger.json`) and the report exactly. The two members
together separate the conflated axes: name-resolvability (post-table) vs
the reader's own `!seekable` gate.

### Claim 3 — ledger 114 rows, 49/0-vs-65/1, prior-112 byte-identical — AGREE

My replay (`ledger-r68-verifier.tsv`, 114 rows): **49 exit 0 / 65 exit 1 /
0 other, 0 UNPARSED** — identical tally to the author's.
compare.py output verbatim:
```
[a] my exits: 49 exit-0 / 65 exit-1 / 0 other (author claims 49/65); exit mismatches vs author: NONE
[d] failure-summary mismatches vs author: NONE
[b] my receipts vs author's committed r68 receipts: 0 mismatches
[c] my prior-112 receipts vs committed r67 receipts: 0 mismatches
```
All 114 of my fresh receipts are **byte-identical** to the author's
committed r68-ledger receipts (stronger than exit-for-exit: full receipt
bytes), and my 112 prior rows are byte-identical to the committed r67
receipts (r68 rows {1}∪{4–114} ↔ r67 rows {1–112}).

### Claim 4 — new probes deterministic, exit 1, fork via `failures` — AGREE

Verifier receipts per probe (ledger run + 2 standalone + 1 exit-check):
- `--probe-transport-posttable-nomatch-r68` → exit 1 every run; every
  receipt sha256 `52bbb1a9c9c0fc73c3c269809c10081e8832b2b6fe0e2910d0216e0a83e08b2b`
  — identical to all **five** committed copies (author claimed 3 runs;
  the tree carries more, all identical).
- `--probe-transport-txw-piperefuse-r68` → exit 1 every run; every
  receipt sha256 `762aff12c5c512bfa3871afb519869a5ac2c473a7853e837b5afd2dd841f66dc`
  — identical to all five committed copies.
- The `failures` field on stdout carries the exact fork strings quoted in
  the report (`file/fifo_path=RIFF header not found vs stdin_pipe/redirected_fd=...`;
  `file/redirected_fd=decode 64 samples vs stdin_pipe/fifo_path=input must be a file, not a pipe`).

### Claim 5 — fixture diff additive-only — AGREE

`git diff --name-status a0958a9..6c91040`: **982 added, 4 modified, 0
deleted**. The only modified files: `build_artifacts.py` (+46/−1 — numstat
exact), `measure_audio.py` (+34/−3 — numstat exact), and the two tracked
`__pycache__` `.pyc` blobs (disclosed mechanical regeneration churn). Diff
read confirms: new `build_ui_posttable_r68_probe()`, two argparse flags,
one newest-first dispatch arm; `TRANSPORT_R68_MEMBERS` map, two flags,
mutual-exclusion sum +2, two forwarding splats, the r68 arm block
prepended before the r67 block, mode/suffix chain heads prepended. No
prior member, prior path, mode string, or receipt touched.

## Member + seed/manifest immutability

- `posttable_nomatch.wav` (512 B) sha256
  `6373923ff849ed3868e76f827339827fe0a1b23f7bc413fd2573ef73681c92d7` — matches
  the report; my verbatim-ported rebuild is **byte-identical** (`cmp`
  clean). Byte layout spot-checked: `'u'`@0 (kills every offset-0 magic),
  `0x00`@256 (act residual conjunct dead), not named `.snd`.
- `txw_piperefuse.wav` (128 B) sha256
  `fd7911a3523d7bc9337ed58935b4a7e8b642f0f3bab864441fde4af51f01f504` — matches
  the report; rebuild **byte-identical**. Layout: `LM8953`@0-5,
  `0xC9`@22, `3`@23 (→16666.7 Hz ≈ 1e5/6, confirmed in my raw stat output),
  deterministic `(i*5+1)&0xFF` payload 32–127.
- Prior members/receipts: 0 prior-path modifications in the commit
  (name-status above); all 112 committed r67 receipt paths **re-hash to the
  frozen r68-baseline manifest, 0 mismatches**; `corpus/knowledge/seed.md`
  last touched at the lane-mint commit `6e71ed4`, unchanged this round;
  prior round-*/ members last modified in their own commits.

## Mismatches

**0 mismatches** on every axis checked (exits, failure summaries, receipt
bytes ×2 comparisons, member bytes, manifest hashes).

## Host notes / honest limits

- `measure_audio.py` has **no `--runs` option**: receipts always write
  `ROOT/live/runs/<stamp>-<suffix>/`. My 114 replay receipts are untracked
  dirs under `corpus/live/runs/20261014T1033*–1037*` — left in place as
  untracked replay evidence (same convention the author's receipts used
  before being committed). My TSV/compare/report live under
  `corpus/live/r68-verifier/`.
- The claim's "(exit 2)" is the sox arm exit inside each receipt leg; the
  probe process itself exits 1 — consistent with the report's own ledger
  rows (1) and my replay.
- The r67 → r68 receipt byte-identity holds across my replay too — my
  prior-112 receipts equal the r67 committed bytes, not only the r68 ones.
- Untracked `corpus/live/r68-simplifier/` predates my run; not mine, untouched.
- No subagents, no commits, no edits outside my scratch + this report.
