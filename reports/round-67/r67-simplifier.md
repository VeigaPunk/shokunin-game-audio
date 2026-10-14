# Round 67 — simplifier: transport axis keep/drop — full 4-arm cross justified; parameterized runner clean; txw/smp refusal class has no tracked member

Seat: **simplifier**. Reviewed the landed transport arm on `measure_audio.py`
(working-tree diff `+183/−3`, HEAD `0df212f`). Method: post-landing keep/drop
per element, exercised in an isolated scratch replica
(`corpus/live/r67-simplifier/tree/` — real copies of `fixtures/`+`artifacts/`,
real copies of `live/round-*` so `build_artifacts.py` cannot write through into
tracked state; receipts land in `tree/live/runs/`). Replica validity proven
first: HEAD file in replica reproduces the committed r66 receipt
**byte-identical** (`tree` run `20261014T051605583740Z-ui-dec-hcom-r66` ==
shared `corpus/live/runs/20261014T050349299020Z-ui-dec-hcom-r66`).

No `lsp` device is exposed on this host — recorded unavailability per seat
card. For the no-dead-paths claim I used exact argparse-reference accounting
(every `add_argument` name vs every `args.*` use vs the sum/dispatch/mode/
suffix chains), not text grep; this file's dispatch is single-file argparse —
the structural check covers all call paths.

## Landed shape (what was added)

- `TRANSPORT_R67_ARMS` — 4 arms tagged `(named, seekable)`: the explicit 2×2.
- `TRANSPORT_R67_MEMBERS` — all 10 tracked autodetect members (r65 preempt ×4,
  r66 dec/lengate ×6); **zero new fixtures**, `build_artifacts.py` untouched.
- One parameterized runner `transport_leg(args, label, data=|stdin=)` serving
  all four arms; `transport_error` normalizes verdict text; `stderr_tail`
  strips backquoted input names to `` `<input>' `` (byte-stability across
  tmpdir fifo paths). `transport_entry` emits per-arm cells +
  `transport_verdict_groups` + `transport_fork` + `failures`.
- 10 new flags `--probe-transport-<member>-r67`: each is declared, summed,
  guarded, dispatched, and present in both mode and suffix chains (count
  verified: 106/106 flags wired; `lengate_hcom_132` is the ternary
  fallthrough at 4 uses vs 5 — correct).

## Keep/drop per element

| element | verdict | evidence |
|---|---|---|
| full 10-member × 4-arm cross | **KEEP** | the claim is "the set of transport-forking members is exactly *measurable*" — naming the set requires every member measured; ~44 cheap `sox stat` legs, cheaper than a member-selection convention |
| fifo arm | **KEEP — non-redundant** | only arm separating namedness from seekability: on every forking member `fifo_path ≡ stdin_pipe` (measured, below), proving *seekability* is the operative axis; and without mitigation it exposes the bridge's pathname re-open as an indefinite block (strace below) |
| redirected_fd arm | **KEEP — non-redundant** | on act members `redirected_fd` splits from `file` (`premature EOF` vs decode-278/3839): unnamed+seekable is a distinct verdict from named+seekable — the bridge needs *both* |
| `transport_leg` (one runner, all arms) | **KEEP** | satisfies "no duplicated transport-runner paths" — zero per-arm clones |
| `TRANSPORT_R67_FIFO_WRITER_HOLD_S` | **KEEP — load-bearing** | converts ffmpeg's fifo re-open from permanent block to deterministic empty-stream verdict; 3 consecutive `transport-preempt-act` runs → byte-identical receipts (`tree/live/runs/…051841/…051938/…051940` pairwise diff clean) |
| `stderr_tail` `` `<input>' `` normalization | **KEEP — load-bearing** | fifo tmpdir names are random per run; without normalization the receipt is not byte-deterministic |
| per-member probe flags (10 rows) | **KEEP** | row-per-member is the ledger convention (r63–r66 identical pattern); a single combined flag would create a second row granularity |
| `transport_fork` + `failures[]` pin | **KEEP** | routes the fork set through the existing failure aggregation — fork set = failed set, enumerable from receipts |
| `named`/`seekable` per arm | **KEEP** | axis definition itself, self-describing cells |
| `transport_verdict_groups` | **KEEP-acceptable; the one droppable layer** | derived restatement of `transport_axis` (zero new information, recomputable) — but it materializes the *signature-equality rule* (detected|route|exit|samples|error), which is semantic content. If a strict byte-count pass is ever wanted, this is the trim candidate, not the cells |
| `transport_protocol` per entry | **flag (micro-bloat), keep-acceptable** | 3 constants repeated identically in all 10 entries; could live once at receipt level, but per-entry self-containment is this file's convention |

**No duplicated transport-runner paths were introduced.** The pre-existing
r63→r66 autodetect blocks are four pasted generations of the same legs-runner
(r65/r66 share 72% of code lines, common runs of 8/9/18 lines verbatim) — each
generation is a round's pinned evidence shape, i.e. receipt-bound provenance:
**not a deletion target**. The r67 arm correctly broke the pattern instead of
adding a fifth paste.

## Measured fork set (independent replica, landed file)

| member | detected | verdict groups | fork |
|---|---|---|---|
| preempt_act | act | file=decode 3839 \| pipe+fifo=`can't find Sun/NeXT/DEC identifier` \| redir=`premature EOF` | **T** (3 groups) |
| preempt_gsrt | gsrt | file+redir=`premature EOF` \| pipe+fifo=`invalid format for this file type` | **T** (seekability axis) |
| preempt_hcom | hcom | 1 group | F |
| preempt_both | gsrt | file+redir=`premature EOF` \| pipe+fifo=`invalid format` | **T** |
| dec_hcom | hcom | 1 group (9 samples, all arms) | F — invariant control |
| dec_act | act | file=278 \| pipe+fifo=Sun/NeXT \| redir=`premature EOF` | **T** (3 groups) |
| lengate_gsrt_24 | wav | 1 group | F |
| lengate_gsrt_25 | gsrt | file+redir=`premature EOF` \| pipe+fifo=`invalid/missing file name` | **T** |
| lengate_hcom_131 | wav | 1 group (43 samples) | F |
| lengate_hcom_132 | hcom | 1 group | F |

Fork set = **{preempt_act, preempt_gsrt, preempt_both, dec_act,
lengate_gsrt_25}** — the act + gsrt reader classes, exactly. Declared claim
holds ("at least one tracked member's verdict forks"). One honest scoping:
on *tracked* members gsrt forks at the normalized-error level (exit 2,
samples None on all arms; the error class forks). The decode-count fork
(88 samples on pipe) lives on untracked constructions (r65 critic D2); act
carries the decode-level fork on tracked members.

## Prior-contract preservation

- `normal`, `route-act-84-r63`, `extensible-valid-8-r64` receipts: **byte-
  identical** HEAD-file vs landed-file in the replica (exit codes also match:
  0/1/1/1).
- `preempt-act-r65`, `lengate-hcom-132-r66`: **identical modulo the
  pre-disclosed absolute-path-embedding class** — diffs are confined to the
  embedded checkout path inside stderr tails (`[-160:]` window cuts at
  different offsets because replica paths differ in length). On the shared
  tree both versions emit identical bytes; the landed diff touches only
  additive code (new functions/flags/chains — verified by diff inspection:
  no old measurement key changed shape).

## Missing minimal adds (flagged, not blocking)

1. **txw/smp pipe-refusal class has no tracked member.** r66-boundary measured
   `input must be a file, not a pipe` on untracked `g_txw_*`/`p_smp_*`
   fixtures — a third fork class (detection fires, open refuses) that the
   landed matrix cannot pin because no tracked member detects txw/smp.
   Sharpest missing add: one `LM8953`@0 carrier. Author chose zero new
   members — defensible (declared claim satisfied on the existing set); flag
   for a future round rather than this landing.
2. **amr-nb decode-count fork** (800 file vs 1120 pipe, r66-boundary) is a
   samples-level fork, weaker than verdict-level — second-priority add.
3. wve WARN-only fork is below signature scope — correctly out.

## Hazard flag

If the 10 s arm timeout ever fires on the fifo arm, `subprocess.run` kills
sox but the popen'd **ffmpeg grandchild survives as a permanently-blocked
orphan** (observed live: two leaked ffmpeg PIDs on
`r67-author/fifo/pair_dec_act.wav` after scratch runs, six more from
r67-boundary's `.fifo_probe`). With the writer-hold design the arm resolves
deterministically and the timeout is only a backstop — residual, rare;
candidate follow-up is process-group kill on timeout. Orphans from my run
were reaped (PIDs 2004282/2010122 killed; `ps` shows none under
r67-simplifier paths).

## Mechanism receipt

`strace -f` on the fifo arm (`corpus/live/r67-simplifier/strace-fifo-act.txt`):
sox `openat(fifo)=3`, `lseek(3)=ESPIPE`, detects `act`, then `execve("ffmpeg",
"-i", <fifo path>, "-f", "au", "-")` — the act bridge transports input by
**pathname re-open**, which is why the 2×2 cannot collapse: `file` succeeds,
`redirected_fd` fails (no name to reopen), `fifo_path` deadlocks without the
writer-hold (name exists, second open blocks), `stdin_pipe` fails on the
consumed stream. Each arm isolates a distinct verdict on the act class.

## Preserved contract & tradeoffs

- Preserved: all 102 prior ledger rows reproduce byte-identically (sampled 5
  representative modes spanning normal/r63/r64/r65/r66; diffs only in the
  disclosed path-embedding class); `build_artifacts.py` and all tracked
  fixtures untouched; dispatch consistency 106/106.
- Tradeoff accepted: `transport_verdict_groups` + `transport_fork` are derived
  data committed to the receipt (restates `transport_axis`); kept because they
  encode the fork-signature definition. No deletions were warranted in the
  landed code; no dead paths exist in the file.
- Shared tree: only the author's `measure_audio.py` landing plus untracked
  r67 scratch dirs; the tracked `__pycache__/*.pyc` regen is from lane runs
  (not my writes — my executions ran scratch copies only).

Receipts: `corpus/live/r67-simplifier/{tree,head-tree}/live/runs/` (20+
receipts incl. all 10 transport modes + HEAD-vs-landed pairs),
`transport-matrix.json` (author-spike replication), `strace-fifo-act.txt`,
`fifo_act_trace.sh`, `measure_audio_HEAD.py` (HEAD reference copy).
