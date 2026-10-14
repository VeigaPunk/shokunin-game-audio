# R74 simplifier — one byte-identity deletion (`LAVF_R74_EXTENT_TIMEOUT_S`), the acm fork gate measured wound-only (mitigated by the rev2 `fork_kind` fold), r73 replay preserved 0/1363 stable diffs, member-authority/duplicate-parser candidates ruled out with measured reasons

**Seat:** simplifier (delete-and-measure, not subjective trim). Lane: audio. Repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, host `plazir27`.
**State at measurement (2026-10-14 15:19–15:47 UTC):** HEAD at start `1ba8103` (r73
report-last). The r74 arm landed as a working-tree diff during the session in three
revisions — rev1 `154a35a0…` @15:29:24Z, rev2 `be6bd279…` @15:35:39Z, rev3 `9d179d80…`
@15:36:41Z — stable ≥2.5 min at 15:39:51Z, operator-committed as **`168b165`** (ci@local,
15:37:43Z, files: `measure_audio.py` +584/−10, the six `corpus/live/round-74/` members,
`reports/round-74/r74-author.md`). The committed blob sha256 of `measure_audio.py` is
**`9d179d80f379673b…` == my rev3 anchor**: every proof below runs against the exact
committed bytes. **Deletions made in the shared tree: none** — write scope is this report
+ `corpus/live/r74-simplifier/`; all treatments were applied to a scratch tree copy
(`tree/`), never to the shared file. Final shared-tree check: `measure_audio.py` worktree
== committed blob; `build_artifacts.py` untouched (`8ce629905e…`); the only tracked
modification is `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`, regenerated
by sibling seats' module imports during the landing window (the current pyc header
records the **rev1** working-tree source: mtime `12:29:24` / size `181574`, so it is
stale vs the committed rev3) — not written by this seat.
**LSP device — unavailable on this host/task (re-recorded empirically, per seat card).**
No `pyright`/`pylsp`/`jedi-language-server`/`lsp` binaries; `pygls`/`jedi` not importable;
`clangd` is C-family only. The sole MCP server (`rea`) is Ghidra-session-bound:
`binary_overview` → `target_unavailable: "No app is open. … call open_binary with its
local path"`; its `procedure_references` device serves loaded native binaries, not this
Python file. Every "no callers / unreferenced" statement below is therefore
**grep-literal fallback, explicitly not semantic proof**.
**Toolchain (this session):** pw-cat / libpipewire **1.6.8** (daemon live, pid 1905/2290),
mpv **v0.41.0** (libavformat **63.1.101**), ffmpeg/ffprobe **n9.0.1** (same libavformat),
SoX_ng **14.8.0.1**, Python **3.14.7**, numpy **2.5.3**, Linux x86_64 kernel
**7.2.3-arch1-3**.

## Deletion candidates (measured)

| # | Candidate | Byte-identity proof (scratch tree, full arm) | Ruling |
|---|---|---|---|
| **D1** | `LAVF_R74_EXTENT_TIMEOUT_S = 20` (`:1452` in the committed blob; uses `:1552`, `:1556`) — delete, re-point both uses to `CONSUMER_R73_TIMEOUT_S` (15) | rev3: treatment receipt `ebddda25…` **byte-identical** to (a) a second run of the unmodified code (`ebddda25…`) and (b) the author's own landed-revision receipt (`runs/20261014T153739783116Z-lavfsweep-r74`, `ebddda25…`). rev1: treatment `d272a13f…` byte-identical to the rev1 control and the author's rev1 receipt (`…153053003782Z`, `d272a13f…`). Identical-code control pair differs only in the declared ±1 ms jitter leaf `consumer_pwcat_ops2_r74_probe.target0_unlinked_stream.wall_s` (4.001 vs 4.002) | **Apply.** The entry's own `transport_protocol.arm_timeout_s` already declares `CONSUMER_R73_TIMEOUT_S` (15 s), so the deletion removes an *undeclared* second bound and makes the protocol block accurate for every leg in the entry |
| D2 | `LAVF_R74_ZERO_SINK_WAIT_S = 6.0` | receipt-visible: `zero_sink_daemon.pwcat_wait_s: 6.0` | Not deletable (evidence row) |
| D3 | `LAVF_R74_START_S = 2.0` | receipt-visible: cell text `"mpv --start=2.0 …"`, `predicted` string | Not deletable (evidence row) |
| D4 | `LAVF_R74_DIR = "round-74"` | receipt-visible: `directory: "live/round-74"` + all member `path`s | Not deletable (evidence row) |
| D5 | `LAVF_R74_MEMBERS` dict | receipt-visible: `predicted` per member, and it is the member authority for the dispatch loop | Not deletable; and it correctly **aliases** the canonical `dec_act` (`*TRANSPORT_R67_MEMBERS["dec_act"]`) instead of re-listing a path — no second member authority (the r73-C1 ruling held) |
| D6 | `made[...]` generation labels, `fork_kind`, `extent_legs`, `head_truncation`, `pcm_out_*`, lavf field copies in `mpv_extent_leg` | each is a receipt key | Not deletable (evidence rows / load-bearing pins, out of scope by tasking) |
| D7 | Extract a shared lavf-log parser for `mpv_leg` (r73, `:1129-1136`) and `mpv_extent_leg` (r74), or a shared group-by-signature helper (now a 5th copy), or a shared ops fifo/name-axis harness | extraction touches prior-round lines and changes their receipts' construction path | **Do not.** Insertion-only round contract (r73-R3 / r69-#12-#13 carry); the duplication is the contract's measured cost |

### D1 — the only receipt-invisible weight in the new code

`LAVF_R74_EXTENT_TIMEOUT_S` has exactly three occurrences in the committed blob (def
`:1452` + `timeout=` `:1552` + the blocked-message f-string `:1556`). No extent leg timed
out in any measured run (7 members + the `--start=2` cell all completed in the landed
receipt; the author's scratch mpv run on `lavf_iss_multi` finished at 5.496 s wall,
`corpus/live/r74-author/log-file-lavf_iss_multi.iss.log:236`), so the constant leaves **no
trace in any receipt** — the deletion is byte-invisible. **Bounds of the proof:** the
constant's only observable surface is the string `"blocked: no verdict within 20 s"`,
emitted only when a leg exceeds the bound; the byte-identity proof is therefore bounded
to runs where no extent leg times out. **Tradeoff:** the extent legs' bound drops 20→15 s
(still SIGKILL-bounded via `subprocess.run(timeout=…)`, which kills with SIGKILL —
r73-C2 measured); on a slower host the extent legs lose 5 s of margin while the matrix
legs never had it. Receipts for the same member class (`transport_protocol.arm_timeout_s
= 15`) then describe all legs honestly.

## False-positive gates (measured)

### F1 — the acm "fork" cell is produced solely by the `seek_failed` leaf (rev1); rev2/rev3 annotate it as `wound`

- **rev1 receipt** (`…153053003782Z-lavfsweep-r74`): `lavfsweep_lavf_acm_r74_probe` —
  `exit_code=0`, `lavf_detected="acm"`, `mpv_verdict="success (reason 0)"` on **all four**
  transports; only `seek_failed` differs (`file`/`redirected_fd` = `"Operation not
  permitted"` vs `stdin_pipe`/`fifo_path` = `None`). The entry keyed groups on
  `(exit_code, lavf_detected, seek_failed)` → 2 groups → `transport_fork=true` →
  predicted `"fork"` → **gate passes, no failure recorded**.
- **Fixture-native extent measurement** (`corpus/live/r74-simplifier/acm_extent_check.py`,
  calling the landed `mpv_extent_leg` on the committed tree): **868 PCM bytes /
  0.00907 s on all four transports** (file/redirected_fd/stdin_pipe/fifo_path), rc=0 all.
  There is no output-level difference; under the r73-defined fork semantics (rc polarity)
  and any extent semantics, acm does not fork — the verdict is driven by the
  seek-refusal leaf alone. (Corroborates critic F1; the scribe's forgeability finding is
  the same surface.)
- **rev2/rev3 fold (committed):** `fork_kind` added — `None` (invariant), `"wound"`
  (partition on `seek_failed` alone), `"output_rc"` (rc partition), `"truncation"`
  (wound + measured head loss). Committed receipt `…153739783116Z`: acm `wound`,
  iss/apc `output_rc`, iss_multi `truncation`, adx/aifc/dec_act `None`. The receipt now
  carries the discriminator, and the author's report documents the shape split.
- **Residual (bounded):** the prediction gate still passes for acm (`transport_fork=true`
  == predicted `"fork"`); a wound-level partition satisfies the "fork" cell by
  construction. And no extent/no-data column exists for acm (extent legs only for
  iss_multi), so the wound label cannot be falsified **from the receipt alone** — my
  out-of-receipt measurement is the corroboration. **No deletion available:** removing
  `seek_failed` from the key changes the receipts; removing `fork_kind` removes the
  mitigation. Adjudication is critic/verifier territory.

### F2 — adjacent (r73, pre-existing, recorded-not-deletable): two claim-vs-gate gaps

- `pacing_trickle` (r73 ops entry): the comment claims wall ≥ delivery window; the gate
  checks `exit_code` only. Measured (committed receipts): `wall_s` 6.003–6.004 vs
  `delivery_window_s` 6.0; the field is recorded but ungated. The sibling
  `pacing_instant` cell *does* gate its wall (`playback_paced`), so the asymmetry is
  real, not stylistic. No deletion (evidence rows); flag for the verifier.
- `fifo_no_writer` (r73): gates `blocked` only; the discriminating `wchan`
  (`wait_for_partner`) is recorded but ungated.

### F3 — host-state observation affecting replay claims

The committed `-consumers-r73` set (15 receipts) contains one **daemon-down run**
(`…150305963053Z`: 6 failure keys — 2 member forks + 5 ops deviations, recorded
honestly) and a `daemon_live.default_sink` name drift to `…SPDIF__sink.2` first captured
post-landing at `…153153302722Z`. Causal attribution to the r74 ops-2 private-daemon cell
is **not established** (pre-existing churn visible: hdmi node suffix `.7`). Consequence
for all seats: replay byte-identity of `--probe-consumers-r73` is limited to code-induced
leaves + declared jitter + this host-state leaf.

## Ruled-out deletions (stop condition reached)

- **No dead symbols.** `scan_dead.py` on the committed blob: 0/36 top-level defs, 0/118
  argparse flags, 0/32 module constants, 0 local constants/locals unreferenced; all 11 new
  r74 symbols ≥2 references (grep-literal, LSP unavailable — see header).
- **Member-generation site (relocation, not deletion).** `build_lavf_r74_members()` lives
  in the fixture, where the r68/r69 convention puts member generation in
  `build_artifacts.py`. The author's report declares it a deliberate brief-scoped choice;
  moving it is not a weight change and would re-open the r69 convention. Recorded as a
  convention note for the next member-generating round to settle.
- **Insertion-only contract (D7).** Extracting the duplicated lavf parser / group loop /
  ops harness blocks would touch prior-round lines; r73-R3 carries.
- **Comment fold.** The critic §8.3 residue restatement landed **inside the author diff**
  (the committed diff's removed lines are exactly the 9 r73 comment lines at old
  `:988-994` plus the 3 chain lines) — comment-only, content matches the r73 adjudicated
  form, receipts unaffected (comments are not measured). Recorded as a process
  observation, not judged.
- **Author-report revision drift.** The committed `r74-author.md` describes rev1
  (`+544/−3`, receipt `…153027Z`); the committed diff is rev3 (`+584/−10`, incl. the
  critic/reviewer folds and receipt `…153739Z`). Noted because my revision timeline
  documents it; reconciliation is the reviewer/scribe lane.

## Preserved contract (retained behavior proven with the narrow existing checks)

- **Scratch control reproduces the landed arm byte-for-byte.** Control run 2 (committed
  code, scratch tree): `ebddda25…` == the author's own landed-revision receipt
  `…153739783116Z-lavfsweep-r74` (`ebddda25…`); control run 1 of the same code is
  `fa40a60c…`, differing only in the declared ±1 ms jitter leaf (below). rev1
  cross-check: my control `d272a13f…` == author's `…153053003782Z` receipt.
- **Prior row `--probe-consumers-r73` preserved on the committed tree.** Replay receipt
  `3db1d436…`: vs the post-drift committed receipt `…153153302722Z` — **0 stable diffs /
  1363 leaves, 1 jitter leaf** (`pacing_instant.wall_s` 4.033→4.036); vs the pre-drift
  committed receipt `…151240011154Z` — 1 stable diff = `daemon_live.default_sink`
  host-state leaf (F3) + 2 jitter leaves (`pacing_instant` 4.032→4.036,
  `pacing_trickle` 6.004→6.003). **Code-induced diffs: 0.**
- **r73 flag surface untouched.** The committed diff's removed lines are the 9 comment
  lines + the 3 chain lines (mutex/mode/suffix), each re-added verbatim plus the r74
  clause — the same edit r73 made to join the flag set. `consumer_ops_entry` is
  byte-identical, and ops-2 landed as a **parallel key**
  (`consumer_pwcat_ops2_r74_probe`), exactly the pre-landing ruling that keeps the r73
  replay intact. Measured counterfactual (rev1 simulation): extending
  `consumer_ops_entry` instead would have changed the r73 flag's receipt
  (`f6d5379a…`→`8ac6ed72…`, 1 one-sided leaf, 0 shared-leaf changes).
- **Member generation is byte-deterministic and self-sufficient.** The six
  `corpus/live/round-74/` member shas equal the author's scratch member shas (6/6) and
  the committed blobs; regeneration rewrites identical bytes.
- **Wiring verified:** `--probe-lavfsweep-r74` → mutex sum → `mode`
  (`probe-lavfsweep-r74`) → `suffix` (`-lavfsweep-r74`) → dispatch branch, one clause
  each.

## Stop condition

The next deletion that would remove weight — dropping the extent legs' duration probe
(used by the `--start` gate), the `fork_kind` annotation (the F1 mitigation), or
extracting the duplicated parsers/loops (touches prior-round lines) — harms an axis
(falsifiability / replay / insertion-only). Deletions recommended for the tracked tree:
**D1 only (one constant, one line, byte-identical receipts)**. Stop.

## Evidence index

Scratch `corpus/live/r74-simplifier/` (sha256 of each, full list in `final-state.txt`):

- state: `head-at-start.txt` `c23152dc…`, `landed-sha-snapshot{1,2,3}.txt`,
  `stability-watch.txt` `b0949e56…` (STABLE 15:39:51Z, sha `9d179d80…`),
  `final-state.txt` `711bb8b0…` (re-verified 15:48:09Z: worktree == committed blob), `landing-poll{,2,3}.txt`
- revisions: `landing-snapshot{1,2,3}.diff` (`84bdc39a…`/`9c414284…`/`7836de54…`)
- **D1**: `measure_audio.D-E1-final.py` `b62bc348…` (−1 line vs committed
  `9d179d80…`), `run_final_proofs.sh` `528e8d10…`, `final-proofs.log`,
  `final-control-receipt.json` `fa40a60c…`, `final-control2-receipt.json` `ebddda25…`,
  `final-DE1-receipt.json` `ebddda25…` (== author receipt `…153739783116Z`),
  `DE1-diff.txt` `a7d2eb80…`, `final-diffs.txt` `14bb9457…` (all five comparison
  outputs); rev1 pair: `control-receipt.json` / `DE1-receipt.json` both `d272a13f…`
  (== author `…153053003782Z`)
- **F1**: `acm_extent_check.py` `132c4c1d…`, `acm-extent-check-final.json` `6116fdb3…`
  (868 B / 0.00907 s × 4 transports; only `seek_failed` differs)
- prior row: `final-r73-receipt.json` `3db1d436…`; diffs vs `…151240011154Z` and
  `…153153302722Z` (above)
- dead scan: `scan_dead.py` `3fe9fe96…`, `dead-symbol-scan-landed.txt` `e27ddaa4…`,
  `new-symbol-refs.txt` `e62e49f1…`
- members: `author-members-sha.txt` `e3c303dc…` (author scratch == round-74, 6/6)
- harness: `build_scratch_tree.sh` `61179807…`, `diff_receipts.py` `e8a280ba…`,
  `stability-watch.sh` `85963bcb…`, `watch-landing{,2,3}.sh`
- counterfactual: `ops2sim-receipt.json` `8ac6ed72…` (r73 entry extended simulation)

## Exact commands / exits (key legs)

```sh
cd ~/Projects/shokunin/audio-shokunin
# state
git rev-parse HEAD                     # 1ba8103 -> 168b165 (operator commit 15:37:43Z)
git show HEAD:corpus/fixtures/measure_audio.py | sha256sum   # 9d179d80… == worktree
git show HEAD -- corpus/fixtures/measure_audio.py | grep -E '^-' | grep -v '^---'
                                       # only the 9 comment lines + 3 chain lines
# scratch tree + full-arm proofs (never the shared tree)
bash corpus/live/r74-simplifier/run_final_proofs.sh        # rc=0; log final-proofs.log
#   control  rc=0 receipt …154205783550Z  sha fa40a60c…
#   control2 rc=0 receipt …154556389360Z  sha ebddda25…   (same code; jitter leaf flips)
#   D-E1     rc=0 receipt …154301536887Z  sha ebddda25…   (== control2 == author 153739Z)
#   r73      rc=1 receipt …154339319443Z  (rc=1 expected: the 2 adjudicated forks)
python3 corpus/live/r74-simplifier/diff_receipts.py <committed> <rerun>
# F1 extent (fixture's own instrument)
python3 corpus/live/r74-simplifier/acm_extent_check.py     # 868 B x4, rc 0 x4
# dead scan
python3 corpus/live/r74-simplifier/scan_dead.py corpus/fixtures/measure_audio.py
                                       # no dead symbols (36 defs / 118 flags / 32 consts)
```

**Rulings digest:** apply D1; do not add a second member authority, timeout authority,
parser, group loop, or member-generation site (D2–D7); the acm wound annotation is the
F1 mitigation — keep it; the r73 comment fold and ops-2 parallel key are the two choices
that kept the replay intact.
