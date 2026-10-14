# R68 simplifier — no deletions warranted: every r68 element load-bearing; declared seekability claim FALSIFIED-as-stated (measured fork = NAME-resolvability); txw member carries the true seekable pipe-refusal pin; prior-receipt chain byte-intact

**Seat:** simplifier (delete-and-measure, not subjective trim).
**Diff measured:** landed as commit `6c91040` ("r68: post-table fallback fork = NAME-resolvability ... ledger 112->114, prior rows byte-identical"). No tracked modifications at write time; untracked state = this seat's scratch (`corpus/live/r68-simplifier/`) plus the r68 verifier seat's in-flight post-commit full-ledger replay (`corpus/live/r68-verifier/` + `corpus/live/runs/20261014T1032*-20261014T1034*Z-*` run dirs, not mine — the earliest spot receipt `20261014T103208572318Z-transport-txw-piperefuse-r68` is byte-identical to my replica run of the same mode, see below).
**Toolchain:** SoX_ng 14.8.0.1 (`/usr/bin/sox`), ffmpeg n9.0.1, Python 3.14.7, Linux x86_64.

## Verdict up front

The r68 diff is **already at the minimal expression under the established round-additive convention**: +37/−3 lines in `corpus/fixtures/measure_audio.py`, +47/−1 in `corpus/fixtures/build_artifacts.py`, and the four deleted lines are the routine per-round rewrites of the three long chain expressions (sum-block, mode chain, suffix chain) plus the r66 builder-guard line — each replaced by itself plus the new terms. No new runner, no duplicated transport machinery, no dead member. I found **no deletion candidate** that does not kill a measured claim; each element was delete-and-measure tested in scratch (`corpus/live/r68-simplifier/`), details below.

The declared claim was **falsified as stated** (author and critic already say this; independently reproduced here): post-table no-match forks `{file, fifo_path}` vs `{stdin_pipe, redirected_fd}` — the *named* axis, not the seekable one. `redirected_fd` (seekable-but-anonymous) is the falsification arm; `fifo_path` (non-seekable-but-named) is the other. The txw member supplies the round's genuine seekable fork. Both findings are in the committed receipts:

| mode | verdict groups (verbatim from committed receipt) |
|---|---|
| `transport_posttable_nomatch_r68_probe` | `{file, fifo_path}` → detected null, exit 2, `RIFF header not found` \| `{stdin_pipe, redirected_fd}` → detected null, exit 2, `sox FAIL formats: can't determine type of  '-'` |
| `transport_txw_piperefuse_r68_probe` | `{file, redirected_fd}` → detected `txw`, exit 0, 64 samples \| `{stdin_pipe, fifo_path}` → detected `txw`, exit 2, `input must be a file, not a pipe` |

## What landed (census)

`measure_audio.py` (commit `6c91040`, relative to r67 HEAD `bd5e1fe`):

- `TRANSPORT_R68_MEMBERS` dict + 6-line member-contract comment (L198–207) — documents that the `.wav` extension on `posttable_nomatch` is part of the member contract (post-table fallback = `lsx_find_file_extension(path)`).
- Two `add_argument` flags (L427–428), two terms in the mode-count sum (L430), two builder-forward splices (L443–444), two terms each in the mode chain (L1052) and suffix chain (L1072).
- r68 arm block (L617–634): guard → member ternary → dict lookup → `transport_entry(...)` call. **Structurally identical to the r67 arm** (L635–663: guard → 10-term ternary → `TRANSPORT_R67_MEMBERS[member]` → same call). The 15-line comment inside the arm carries the falsification note and the ≤257-B pending-buffer mechanism attribution.

`build_artifacts.py`: one new function `build_ui_posttable_r68_probe()` (writes both members + byte-cost provenance comments citing `formats.c:66-267`, `formats.c:920-933`, `tx16w.c:90`, `smp.c` sizes), two argparse flags, one new `if` branch before the r66 branch (calls `main()` + the builder). One deleted line = the old r66 `if` head, replaced by the r68 branch + `elif`.

**Untouched:** `transport_matrix`, `transport_entry`, `transport_leg`, `transport_error`, `stderr_tail`, all r67 machinery, all ~100 prior probe arms. `git diff` confirms only those 4 `-` lines total.

## Delete-and-measure results

Each experiment ran in the scratch replica `corpus/live/r68-simplifier/tree/` (replica provenance: `git archive` of pre-r68 HEAD + author's landed fixture/member files; both replica fixtures now `cmp`-equal to committed `HEAD:` — verified `git show HEAD:corpus/fixtures/{measure_audio,build_artifacts}.py` vs replica files, byte-identical, so every measurement below is on the committed code):

| # | Deletion candidate | Measured effect | Verdict |
|---|---|---|---|
| 1 | r68 arm block (`if (args.probe_transport_posttable_nomatch_r68 or ...)` through `transport_entry` call) | `--probe-transport-posttable-nomatch-r68` still parses and still writes a receipt labelled `probe-transport-posttable-nomatch-r68`, but the receipt contains the **whole normal-suite measurement set** (ui/impact/movement/ambience/stem members) — silently wrong ledger row, not an error. Receipt: replica `live/runs/20261014T103009333001Z-transport-posttable-nomatch-r68/measurements.json` (removed after inspection). | **Load-bearing.** The arm is the only thing routing the flag to the member. (Flags this seat's one structural note: the `if`-arm shape means a missing arm degrades to a mislabeled normal receipt rather than failing — pre-existing convention for all ~106 arms, not introduced by r68.) |
| 2 | `posttable_nomatch.wav` member (or its `TRANSPORT_R68_MEMBERS` entry) | No source member → `transport_matrix` raises at `path.read_bytes()`/`mkfifo` on a missing file; the post-table axis claim has no rows. | **Load-bearing** — it is the measured phenomenon. |
| 3 | `txw_piperefuse.wav` member + flag | Same as #2 for the pipe-refusal claim — the tasking's "ONE tracked pipe-refusal member" dies outright. | **Load-bearing.** |
| 4 | `b[256] = 0x00` belt pin in the builder | Rebuilt member without the pin: differs only at offset 256 (`0x03` vs `0x00`); `transport_matrix` on the unpinned member gives **identical verdict groups** (`{file,fifo_path}` → RIFF-not-found / `{stdin_pipe,redirected_fd}` → can't-determine). Measured: `corpus/live/r68-simplifier` nopin probe run. | **Inert-but-justified.** Zero verdict effect today; it pins the member against future payload-formula edits drifting byte 256 into act's `0x84` conjunct. One line + comment; the cheapest possible documentation of a real CHECK-row boundary. Keep — removing it would not shrink anything meaningful and would remove the guard. |
| 5 | `.wav` extension on `posttable_nomatch.wav` (member naming) | Counterfactual member `noext_probe` (same 512 B, no extension): `file` arm `error` embeds the absolute member path, **`fifo_path` arm `error` embeds the `mkdtemp` nonce** (`can't determine type of file '/tmp/transport-r67-nhye5p6m/noext_probe'`) → nondeterministic receipt bytes *and* phantom per-transport verdict groups, since `error` (unlike `stderr_tail`) is not path-scrubbed. Critic flagged this prospectively (r68-critic.md "Harness-artifact risk"); this seat demonstrated it concretely in scratch. With `.wav`, `error` = `RIFF header not found` — path-free on both named arms. | **Load-bearing member design.** The extension is what makes the post-table route resolvable AND the receipt deterministic. |
| 6 | `TRANSPORT_R68_MEMBERS` dict (inline the two tuples into the arm) | Possible micro-shrink (~4 lines) but discards the member-contract comment location and diverges from the `TRANSPORT_R67_MEMBERS` precedent at L179. | Not recommended — current form matches convention, documents intent, and the saving is noise. |
| 7 | Builder `if`-branch in `build_artifacts.py` | Members never generated → mode fails at transport matrix (missing file). | **Load-bearing.** |
| 8 | Second flag consolidation (one `--probe-transport-r68 <member>` selector instead of two flags) | Smaller arg surface but breaks the ledger's one-flag-per-row convention (row name = mode name = flag name; `measurements` key derives from mode). Every prior round including r67's 10-member arm uses per-row flags. | Not recommended — would create a second convention to save two `add_argument` lines. |
| 9 | txw member on a different transport subset, or smaller member | 128 B is already the byte-cost-justified minimum the author derived (txw needs `LM8953` 6-B magic + 32-B reader header + payload for a positive decode; smp's equivalent is ≥331 B — author's probe log: `txw6.wav`→`file is truncated`, `smp17.wav`→`unexpected EOF in header`). | **Load-bearing at current size.** |

### Prefix/truncation safety of the fifo arm (critic's "starved writer" flag)

Direct measurement (`corpus/live/r68-simplifier` truncated-fifo probe): delivering N bytes of `posttable_nomatch.wav` to a fifo and running `sox <fifo> -n stat` —

- N = 8, 64, 257, 512 → identical signature `RIFF header not found`, exit 2.
- N = 0 (writer dies before first write) → `file is truncated` — a *different* signature, i.e. a phantom third group, but only under total writer failure — the already-documented orphan/kill class from r67. Normal `cat`+linger delivery is atomic from the reader's view.

The member is prefix-safe for every partial delivery a live writer can produce.

## Byte-stability / preserved contract

Replica-vs-shared receipt comparisons (all `cmp` on `measurements.json`):

- **New modes (2/2):** `transport-posttable-nomatch-r68`, `transport-txw-piperefuse-r68` — byte-identical replica↔committed-run receipts.
- **r67 transport family (10/10):** preempt-act/gsrt/hcom/both, dec-hcom/act, lengate-gsrt-24/25, lengate-hcom-131/132 — all byte-identical (replica `live/runs/20261014T1028{30..44}Z-*` vs committed `20261014T1023{05..23}Z-*` receipts). The `mkdtemp` nonce dir never enters these receipts (errors are path-free).
- **Older families:** `normal`, `ui-route-act-84-r63`, `ui-extensible-valid-8-r64`, `ui-dec-hcom-r66` — byte-identical.
- **Disclosed path-embedding class only:** `ui-preempt-act-r65`, `ui-lengate-hcom-132-r66` differ from committed receipts solely inside stderr leaves that embed the absolute input path (`sox_native_stderr`, `sox_stderr`, `sox_stat_stderr`) — my replica's longer prefix produces the diff, including the `[-160:]` tail-truncation mid-token cuts (`pen input file`, `ats: can't open`). Pre-disclosed across r62–r67 baselines; not a behavioral divergence — same file on the same path emits identical bytes.
- **Chain evidence:** reviewer's committed run (`corpus/live/r68-reviewer/ledger-r68rev-compare.txt` / r68-reviewer.md) replayed **112/112 prior rows on HEAD byte-identical**; my post-diff replica replays are byte-identical on the committed script. Both directions of the chain hold.
- **Member determinism:** fresh `build_ui_posttable_r68_probe()` output is byte-identical to the tracked members — `posttable_nomatch.wav` sha256 `6373923ff849ed38…` (512 B), `txw_piperefuse.wav` sha256 `fd7911a3523d7bc9…` (128 B).
- **Ledger:** `corpus/live/r68-author/ledger-r68.tsv` = 114 rows; row 1 `normal`, rows 2–3 the two r68 modes, rows 4–13 the r67 transport modes, remaining 102 rows in prior order.
- **Wiring census** (`corpus/live/r68-simplifier/wirecheck.py`): 108 flags; `probe_transport_posttable_nomatch_r68` referenced at 6 points (argparse, sum, fwd, guard, member-select, mode, suffix), `probe_transport_txw_piperefuse_r68` at 5 — the member-select ternary resolves txw by fallthrough, same convention as `lengate_hcom_132`'s last-in-chain position in r67. The 11 flagged anomalies are all pre-existing known-good (`probe-invalid` special-cased; r67 flags absent from the builder-fwd block by design since r67 used existing members).
- A post-commit verifier spot-run (`corpus/live/runs/20261014T103208572318Z-transport-txw-piperefuse-r68/`, not mine) is byte-identical to my replica receipt of the same mode — third independent confirmation.

## Duplication / smaller-expression review

- **No transport-matrix duplication.** The r68 arm calls the same `transport_entry`/`transport_matrix` the r67 arm calls; the only difference is member-selection arity (2-term vs 10-term ternary). The smallest-correct-expression shape for two rows under this convention is exactly what landed.
- **`TRANSPORT_R68_MEMBERS` as a separate dict** (rather than extending `TRANSPORT_R67_MEMBERS`) is the right call: the r67 map's comment binds its members to the r65/r66 rounds they were generated under; merging would blur round provenance for a ~5-line saving.
- **Fifo writer linger** (`TRANSPORT_R67_FIFO_WRITER_HOLD_S = 1.0`) applies uniformly to both new members although neither invokes the ffmpeg bridge (posttable→wav native, txw→txw native): parameterizing linger per-member would create a second code path — worse than the one inert second of writer-hold. Keep uniform.
- `tempfile.TemporaryDirectory(prefix="transport-r67-")` retains the r67 name inside r68 runs — cosmetic only; the tmpdir name provably never enters receipts for extension-bearing members (receipts byte-identical across independent `mkdtemp` nonces). Renaming would churn a shared constant for zero effect.

## Tradeoffs / flags for the record

- **Tracked `__pycache__` churn:** `corpus/fixtures/__pycache__/{build_artifacts,measure_audio}.cpython-314.pyc` are tracked files whose bytes changed as a build side effect and were committed in `6c91040`. Regen-deterministic given same source+interpreter, disclosed in earlier rounds; flagging only because it is nondiscriminating tracked content the lane convention already tolerates.
- **Silent-fallthrough structure (pre-existing):** the flag/arm split means deleting an arm yields a *mislabeled normal receipt*, not an error (delete-and-measure #1). A `transport`-flag-without-arm assertion would harden this, but it is a cross-round structural property — flagging for the parent, not widening scope to fix it.
- **`error` field shape:** for `-` arms the stored error is the full `sox FAIL formats: can't determine type of  '-'` line (no `':` for `transport_error`'s tail-split to consume) — deterministic and consistent across rows; noted by critic, unchanged by r68.

## Stop condition

The next deletion harms an axis: removing either member/mode/arm deletes a measured claim outright (post-table named-axis fork; tracked pipe-refusal seekable fork), and removing the `.wav` member contract or the `b[256]` pin degrades determinism or guard documentation. No byte-identical extraction demonstrated or warranted — the diff already reuses the single transport runner. **Deletions recommended: none.**

## Evidence index

- Scratch: `corpus/live/r68-simplifier/tree/` (replica, fixtures `cmp`-equal to `HEAD:`), `corpus/live/r68-simplifier/wirecheck.py` (108-flag census).
- Delete-and-measure: arm-deletion variant `fixtures/measure_audio_noarm.py` + its mislabeled receipt run; nopin member rebuild at `/tmp/r68s-nopin/` with identical verdict groups; ext-less counterfactual `noext_probe` showing mkdtemp-nonce `error` nondeterminism; truncated-fifo probe N∈{0,8,64,257,512}.
- Receipt comparisons: replica `live/runs/20261014T1028*-transport-*-r67/` (10/10 identical), `20261014T1025*-transport-*-r68/` (2/2 identical), `1026*-{normal,ui-route-act-84-r63,ui-extensible-valid-8-r64,...}` (identical or disclosed-path-only).
- Ledger: `corpus/live/r68-author/ledger-r68.tsv` (114 rows).
- Sibling corroboration: `reports/round-68/r68-critic.md` (independent falsification + ext-less hazard prediction this seat confirmed), `reports/round-68/r68-reviewer.md` (112/112 HEAD-replay byte-identical), `reports/round-68/r68-author.md` (mechanism + byte-cost derivation).
