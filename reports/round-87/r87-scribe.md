# r87 scribe — wave-B gate on the committed pwbind landing (d1e687b9)

host: `plazir27` (local = UTC−3). Lane `~/Projects/shokunin/audio-shokunin`.
Seat: SCRIBE (wave-B gate, r87). Scope: audit the committed r87 landing
`d1e687b9` — `corpus/fixtures/measure_audio.py` (+2083/−3, sha
`be31da67…`), `reports/round-87/r87-author.md`, and the two cited green
receipts — for claim→sha chains, arithmetic reconciliation (4 entries /
105 legs / 2 green runs), file existence, hash re-derivation, unreported
evidence, the caveat rows, and (the round's assigned focus) **whether the
r87 family lock is at a fixed lane path rather than TMPDIR-scoped**.

**Read-only on everything except this report and `corpus/live/r87-scribe/`;
no commits, no judgment passed** — every discrepancy below is handed to the
canonical judge as an adjudication item.

Entry state: HEAD `d1e687b9b6beda083969e4a770d79a6b4407cde9` (`r87 author:
4 entries pwbind lattice`, 04:04:24 −0300; parent `fe4fe472`). Every fixture
claim was re-derived from a **commit pin** (`git archive d1e687b9` →
`~/Projects/shokunin/tmp/r87-scribe-work`), not from the worktree; worktree
fixture sha == pin sha (`be31da67…`). Ambient at audit: loadavg ≈ 91 / 32
cores, and **sibling wave-B seats were executing r87 work live** (verifier
`python3 … --probe-pwbind-r87` pid 763463 from its own tree copy at 04:05:25;
further live runs `r87a_2476582` and `r87a_2643100` at 04:09 — see ADJ-7).
No r87 claim below depends on live state; the cited receipts are the two
canonical green run dirs, whose shas were unchanged for the whole audit.

---

## 0. Verdict

| # | question | answer |
| --- | --- | --- |
| 1 | Do the claim→sha chains hold? | **Yes.** Pin fixture sha `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516` (28 735 lines) = worktree copy; diff is **+2083/−3** (stat 2086 changed, 6 hunks) with exactly 3 deleted lines (mutex sum, `mode`, `suffix` — each replaced in place); both cited receipt shas re-derive (`01f04d35…f1667`, `2970c944…a655`). **Nits: the two red dev runs are undisclosed (ADJ-1); the receipts are host-only and unpinned (ADJ-2); prose “failures: {}” / “coverage_blocked: []” (ADJ-3); two line-ref ranges (ADJ-4).** |
| 2 | Does the arithmetic reconcile? | **Yes.** 18+33+30+24 = **105 legs × 2 green runs**; `failures: []` on all 4 entries in both runs; the `coverage_blocked` key is **absent** on all 4 entries both runs. **328/328 re-derivation checks pass** (`laws-recheck.txt`) covering every headline law (routing precedence, serial vs object.id, the Props live-DSP witness, the midi dead-target census, the 45 B SMF, the remote/RAOP census). Cross-run: 287/3 779 pid-normalized differing leaves, **zero** `exit_code`/`signal`/`killed_at_bound` differences — all churn is identity text, wall/observe times, and one record-only tap-edge state (`negotiating`↔`active`). |
| 3 | Do the claimed files exist? | **Yes.** Every repo path in the report resolves (`path-existence.txt`; the “MISS” tokens are media-class strings and name templates, no path defect). The commit contains exactly 2 files (fixture + report); the cited receipts and the lock are untracked/host-only. |
| 4 | **Is the family lock fixed-path, not TMPDIR-scoped?** | **YES — verified statically, dynamically, by a sibling seat, and by the frozen labrat.** Statically: `ROOT` L26, lock path L25849 `ROOT/"live"/"measure_audio-pwbind-r87.lock"`, blocking `LOCK_EX` L25854 (no `LOCK_NB`), dispatch L28046 “held to exit”; **no `tempfile.gettempdir()` anywhere in the r87 family** (the three hits L14764/L19846/L22318 are the r82/r84/r85 locks, untouched; r86 stays fixed at L24124). Dynamically: two concurrent acquirers with **different TMPDIRs** resolved the identical path and serialized (A waited 0.0001/1.9754 s, overlap −0.0003 s); same-TMPDIR serialized; dead holder re-acquired in 0.0001 s; the r84 TMPDIR-scoped control **raced** (overlap 1.9861 s) — the harness can see non-exclusion. Independent: the sibling r87-critic seat's lock test (A/B/D serialized, r85 control raced) and the frozen labrat's static trace agree on every line number. Caveats: the lock is fixed **per checkout** (cross-tree copies race — E case, the known r86 residual), and `os.open` failure silently skips exclusion (L25850-25853). |
| 5 | Are the encoded claims as reported? | **Yes.** Routing law: `target.object` > `--target` > `node.target` on the raw argvs (`p_three`→NS2, `p_nt_vs_flag`→NS, `p_nt_garbage`→default — the boundary-corrected reversal, armed both halves); serial resolves (`--target 246757` and `target.object=246757`→NS) and object.id never resolves even when it is the sink's own id (`118`→default); Props live-DSP witness solo **8192** → `{volume:0.25}` **2048.0** (exact 0.25) → 8192 → `{mute:true}` **0.0** → 8192, spawn-time volumes 4096/0/12288; midi dead-target census — all six target forms rc≠0 `no target node available` `res:-2`; pw-link carries **real events** — `aplaymidi` over a pinned Midi-Bridge writes a **45 B** SMF carrying both `0x90` note-ons and both `0x80` note-offs (26 B skeleton on the refused record); `remote_cli` **rc255**, zero remote/raop/zeroconf surface (0 modules, 34 in the dir, avahi running). |
| 6 | Custody verdict | **INTACT (pin, receipt chain, teardown witnesses) · GREEN ×2 (both cited receipts re-derive; 328/328 checks) · LOCK FOCUS VERIFIED · NO VERDICT-BEARING DEFECT FOUND.** Defects are disclosure/preservation/prose-level: two undisclosed red dev runs (ADJ-1), host-only unpinned receipts (ADJ-2), prose nits (ADJ-3/4), unrecorded env vectors (ADJ-5), an unmentioned cli teardown skip (ADJ-6), and ambient/observation nits (ADJ-7…10). No falsified measurement, no residue, no write-scope violation. |

---

## 1. Claim→sha chain, re-derived

### 1.1 Fixture chain (commit pin)

| revision | sha256 | re-derivation |
| --- | --- | --- |
| `d1e687b9` (pin) | `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516` | pinned archive file = worktree copy; 28 735 lines; matches the sha the report cites |
| diff | `+2083 / −3` (stat: 2 086 changed), 6 hunks | `@@ -25449,6 +25449,2061 @@` (family block, header L25452 … helpers/entries L25452–27506), `@@ -25576,6 +27631,7 @@` (add_argument **L27634**), `@@ -25583,7 +27639,7 @@` (mutex sum **L27642**), `@@ -25972,6 +28028,30 @@` (dispatch **L28031–28056**), `@@ -26622,7 +28702,7 @@` (`mode` **L28705**), `@@ -26642,7 +28722,7 @@` (`suffix` **L28725**) |
| deleted lines | exactly 3 | the pre-r87 mutex sum, `mode`, `suffix` — each replaced in place with the `probe_pwbind_r87` head; insertion-only otherwise |
| commit totals | 2 files, 2 321 insertions, 3 deletions | fixture + report; **the receipts are not in the commit** |

Namespace/wiring census on the pinned copy: `PWBIND_R87` ×154, `r87a_`
×18, `r87arole` ×3, `probe-pwbind-r87` ×4, `probe_pwbind_r87` ×4
(add_argument L27634, mutex sum L27642, dispatch guard L28031,
mode/suffix heads L28705/L28725); prior families untouched.

### 1.2 Receipts — five canonical executions, two cited

| canonical dir (untracked) | wall (local) | sha256 | status | landed as |
| --- | --- | --- | --- | --- |
| `20261016T064958137082Z-pwbind-r87` | 03:49:58 | `b3d839b0172c0d66…` | **red — 15 failures** (modes 8, cli 7) + midi `coverage_blocked` (pin leg) | only as “3 dev” in the file list |
| `20261016T065456126915Z-pwbind-r87` | 03:54:56 | `694fb8d6d770337e…` | **red — 2 failures** (cli `fmt_stream` seal) | only as “3 dev” in the file list |
| `20261016T065750423328Z-pwbind-r87` | 03:57:50 | `6f137cf804301a5f…` | green | only as “3 dev” in the file list |
| `20261016T070036115509Z-pwbind-r87` | 04:00:36 | `01f04d354f2186dbcf4bc984e2d62a49f378ea8ca2f810d79c7586797d1f1667` | green, 105 legs | cited (run A) |
| `20261016T070305393338Z-pwbind-r87` | 04:03:05 | `2970c944375f2e3b8b6f3ab16bdd5a343521222844d9a3a044a0a7d9a974a655` | green, 105 legs | cited (run B) |

Timeline: dev1 03:49:58 → dev2 03:54:56 → **fixture mtime 03:55:12** → dev3
03:57:50 → runA 04:00:36 → runB 04:03:05 → commit 04:04:24. The mtime sits
between dev2 and dev3, and the dev receipts themselves show the pre-fix
tokens: dev1's `ports` dirs are `"input"/"output"` where the committed
`_pwbind_r87_ports` normalizes to `"in"/"out"` (L25756-25769), and dev1/dev2's
`fmt_stream` seal failed because the pre-fix reader returned `rate: None`
(committed `_pwbind_r87_parse_format` is Choice-aware, L26009-26020). So
**dev1/dev2 measured pre-fix bytes; their source is not recoverable** (no
snapshot, receipts unpinned). The two cited green runs and dev3 measured the
committed bytes; “green twice on identical file bytes” is true as stated.

**ADJ-1 (disclosure).** The report never discloses that two of the three dev
runs were RED (dev1: 8 modes + 7 cli failures + the midi pin leg
`coverage_blocked`; dev2: 2 `fmt_stream` failures). The r85 “uncited red run”
class recurs in weakened form: the runs exist on disk and are referenced only
as a count in the file list, with no red disclosure and no explanation.
Preservation-level, not a measurement defect (the green A/B evidence stands).

**ADJ-2 (custody).** No `pwbind-r87` receipt is tracked (`git ls-files` = 0):
the landed commit contains the fixture and the report only, so the two green
receipts and the lock witness are host-only (r86-ADJ-3 class), and the
receipts embed **no fixture sha / git HEAD** (r84-ADJ-6/r85 class), so
“identical bytes” is re-derivable only from the host timeline. The report’s
“Files changed (nothing committed)” heading is stale in the landed artifact
(the fixture and report are the commit).

---

## 2. Arithmetic reconciliation

### 2.1 Assigned cells (both cited runs)

| entry | legs | content verified |
| --- | --- | --- |
| `pwbind_modes_r87_probe` | 18 | one binary + symlink sha census (4 aliases = `pw-cat`, `pw-mididump`/`pw-cli` distinct); usage refusals (`m_bare`/`m_mflag_only`/`m_noflag_target` mode-required; `--capture`/`--duplex` unknown-longopt; clip/dsd read-fails); last-wins direction (argv0 override, extended triples); midi publish shapes; never-duplex port law; `-s` stays up; recorded-file witnesses |
| `pwbind_target_r87_probe` | 33 | the full precedence lattice on 2 null sinks (10×NS, 4×NS2, 14×default, 3×no-link); serial-resolves / object.id-never (against the sink's own `118`/`246757`); env braces/bare/garbage; `.monitor`/wrong-class/stale-serial; name collision; default-sink stability; name-verified unloads |
| `pwbind_cli_r87_probe` | 30 | cold-registry artifact vs warm control; unknown-global family ×5; Props live-DSP witness + exact-ratio regions; spawn-volume lattice (1.5 unclamped); Format seal on stream+sink and the unlinked `res:-2`; send-command state machine; latency `res:-95`; unknown-key silent drop; foreign no-gate (read/same-value/unknown-key/bogus-type); destroy stream/sink-module; create-node session/linger/badfac/usage |
| `pwbind_midi_r87_probe` | 24 | six dead target forms; the two publishes; the pin (real 45 B SMF); the 26 B skeleton; offline+live `pw-mididump`; pactl/pw-cli module-miss classes; remote host-down family (pw-cli rc255); the unlinked stall; the zero remote/raop census |
| **total** | **105** | `failures: []` ×4 ×2; `coverage_blocked` absent ×4 ×2; teardown witnesses clean in every entry (`own_nodes_after []`, `foreign_r87a_nodes []`, `sinks_gone` all true) |

### 2.2 Re-derivation (`laws-recheck.txt`)

**328/328** checks pass on the two cited receipts: every `consumers` verdict,
the raw-argv precedence halves, serial/id resolution, the region medians and
ratios, the SMF byte witness (`head_hex` `4d546864…90…80`), the dead-target
census, rc255/zero-census, all 20 teardown/meta witnesses. The env-routing
legs are behaviour-verified but their **env vectors are not recorded in the
receipts** (the leg has no `env` key) — code-verifiable only (ADJ-5).

### 2.3 Cross-run stability (run A vs run B, pid/num-normalized)

287 of 3 779 leaves differ; **zero** verdict-class differences
(`exit_code`/`signal`/`killed_at_bound`). The differences are all volatile by
design: `argv` node ids (88), observation offsets `at_s` (86), `wall_s` (38),
`id_in_session`/`node_id` (10), timing `done_at_s`/`spawn_at_s`/`wait_s`,
log text with ids, and two record-only tap-edge `state` fields
(`negotiating`→`active`). “The arms are identical” holds.

---

## 3. The assigned focus — the fixed-path family lock

Method: the committed `ROOT` expression, the `PWBIND_R87_PID/NS/ROLE`
constants and the `_pwbind_r87_family_lock` body were extracted **verbatim**
from the pin (L26, L25559-25565, L25844-25861) and exec'd with `__file__`
pointed at the pin copy; two children were spawned **back-to-back** (Popen)
with **different TMPDIRs** and raced for the lock. A second copy of the pin
supplied the cross-tree case, and the r84 TMPDIR-scoped lock the negative
control. Independently, the frozen-probeParent `ufo-labrat` (one dispatch,
read-only, advisory; static trace only) hand-traced the same committed lines
and reached the same conclusion with matching line numbers.

| probe | result |
| --- | --- |
| resolved path, child A (`TMPDIR=…/tmpA1`) | `…/r87-scribe-work/corpus/live/measure_audio-pwbind-r87.lock` |
| resolved path, child B (`TMPDIR=…/tmpB1`) | **identical** — outside both TMPDIRs |
| acquire windows (A) | 0.0001→1.9754 s; B waited 1.9754 s → strict serialization (overlap −0.0003 s) |
| same-TMPDIR pair (C) | serialized (one waited 1.9826 s) |
| dead holder (D) | re-acquired in **0.0001 s** (flock released on process death; the file is never unlinked) |
| r84 TMPDIR-scoped control (B) | two paths, overlap **1.9861 s** — RACED as expected |
| cross-tree copy of the same commit (E) | two paths, overlap **1.9996 s** — RACED: the lock is fixed **per checkout** (known r86 residual) |
| sibling r87-critic seat (read-only peek at its receipt) | A/B/D serialized; r85 control raced; E cross-tree raced — same verdicts |
| lane file, `O_RDONLY|LOCK_NB` probe | acquired in 6e-06 s, content unchanged (no live lane-tree holder at probe time) |

Static properties: blocking `fcntl.flock(fd, LOCK_EX)` (no `LOCK_NB`
fallback); fd stored in a `main()`-local at L28046 (“held to exit”), so
release is process-scoped; witness write `pid=… ns=… role=…` guarded by
`except OSError: pass`; the function returns `None` if `os.open` fails
(exclusion silently skipped — open-failure path, not TMPDIR-dependent); no
`unlink()` of the lock path anywhere; the four r87 entry calls (L28048/
28050/28052/28054) all follow the lock line inside the same `if` block.

Lane witness timeline (last-writer-wins, never unlinked): at 04:07 it held
`pid=799468 ns=r87a_ns_799468` (49 B, dead pid — a sibling lock test), at
04:09:51 `pid=3585207 ns=r87a_ns_3585207 role=r87arole3585207` (52 B, run B's
pid; sha `432b7978…`) — it is not a lock record, only a witness (ADJ-7). The
r84 fold (r84 critic F1, 3-seat consensus) is **applied for r87**; r82/r84/r85
locks remain `$TMPDIR`-scoped and untouched.

---

## 4. Caveat rows and the encoded claims

| encoded claim | committed arm | run A | run B |
| --- | --- | --- | --- |
| routing law `target.object`>`flag`>`node.target` | `_pwbind_r87_expect` L26086; argvs L26355-26390 | p_three→NS2, p_nt_vs_flag→NS, p_nt_garbage→DEF, p_pb1→DEF, p_pb2→NS | same |
| serial resolves / object.id never | `refs.ns_id=118`, `ns_serial=246757` | p_serial/p_prop_serial→NS; p_objid/p_prop_objid→DEF | same |
| Props live-DSP witness | regions L26095ff, verdicts L27008ff | 8192→2048→8192→0→8192 | same |
| midi dead-target census | verdicts L27400-27412 | 6 forms rc1 `res:-2`; publishes zero links | same |
| pw-link real events | pin leg + SMF witness L25972-26001 | 45 B, `90`/`80` both true | same |
| rc255 / zero remote census | L27470ff, `remote_census` | remote_cli 255; 0 named/0 net modules | same |
| `dump_color_eq`-class record-only rows | — | none this round | — |

The dev-run degradation paths are real and correctly fail-closed: dev1's
bridge-absent boot set the midi **pin** leg `coverage_blocked` (never a
vacuous pass) and left `mdump_live.attempts=[]`; the committed mdump verdict
degrades a never-published node to `coverage_blocked` too (L27454-27461).
The report's caveat names only the mdump flake — the pin-leg degradation is
the one dev1 actually realized (ADJ-10).

---

## 5. Adjudication items (no judgment passed — for the canonical judge)

| # | seat | severity | item | evidence |
| --- | --- | --- | --- | --- |
| ADJ-1 | author | disclosure | Two of the three dev runs are RED and undisclosed (dev1: modes 8 + cli 7 failures + midi pin coverage_blocked; dev2: 2 fmt_stream failures); the report says only “{3 dev, 2 green}” in the file list. | `receipt-chain.txt`; dev receipts |
| ADJ-2 | author | custody | Receipts are host-only (commit = fixture + report) and embed no fixture sha / HEAD; dev1/dev2 source bytes are unrecoverable (fixture mtime 03:55:12 between dev2 and dev3). | `receipt-chain.txt`; `git show --stat d1e687b9` |
| ADJ-3 | author | nit | “`failures: {}`” — actual `[]`; “`coverage_blocked: []` on all 4 entries” — the key is **absent** in all 4 entries both runs. | receipts |
| ADJ-4 | author | nit | Line refs: “26095–27595 the four entry functions” — actual 26095–27506 (`main()` L27507); “28005–28028 dispatch” — actual 28031–28056; helpers “25619–26082” — actual to 26093. Refs are not marked “~”. | `fixture-refs.txt` |
| ADJ-5 | author | minor (report completeness) | The env-routing arms’ env vectors are not recorded in the receipts (no `env` key in `p_env*` legs); re-derivation needs the committed code (L26341-26350). | `legs-runA.txt`; L26341-26350 |
| ADJ-6 | author | nit | The cli entry’s teardown unload is `skipped: not_listed` (the `destroy_sink_module` leg already removed the module); the report’s “name-verified teardown” prose describes the target entry’s verified unloads. `sinks_gone` holds. | cli `unloads` |
| ADJ-7 | lane/host | ambient | Sibling wave-B seats ran r87 live during the audit (verifier pid 763463 04:05:25 from its own tree; runs 2476582/2643100 at 04:09); the lane lock witness was rewritten during the audit (799468 dead test pid → run B’s 3585207). The author’s post-run-B zero-census cannot be re-observed now; the receipts’ own teardown witnesses verify it. | `host-live.txt`; `lock-verify.txt` |
| ADJ-8 | lane/host | observation | Receipt bytes differ in 287/3 779 normalized leaves (all volatile; zero verdict-class) — “the arms are identical” holds; the one non-timing record-only drift is `tap_link.edges[].state` negotiating↔active. | `run-diff.txt` |
| ADJ-9 | lane | custody (inherited) | Tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is dirty: sha `b8826019…`, 1 570 039 B, mtime **03:55:12** — i.e. re-written inside the r87 author window (between dev2 and dev3, alongside the fixture edit), before this seat. Unchanged by this scribe (audit started 04:05; fixture never imported, `PYTHONDONTWRITEBYTECODE=1`). Operator item. | `host-live.txt` |
| ADJ-10 | author | nit | Caveat attribution: the report’s mdump-live flake caveat is real, but the degradation actually realized in dev1 was the **pin** leg (`bridge capture port absent`) with `mdump_live.attempts=[]`; the committed mdump verdict does degrade to `coverage_blocked` when a node never publishes. | dev1 receipt; L27299, L27454-27461 |

---

## 6. Write-scope / custody notes

- Committed in `d1e687b9`: fixture (+2083/−3) and the author report — 2
  files, 2 321 insertions, 3 deletions. Nothing else.
- This seat wrote only `reports/round-87/r87-scribe.md` and
  `corpus/live/r87-scribe/` (18 artifacts + `manifest.json`; the manifest
  lists each artifact’s bytes+sha256 and this report’s sha). **No tracked
  file was modified**, no commit, no push, no
  PipeWire object created or destroyed (only read-only `pw-dump`/`pactl
  list`/`pgrep` queries and one `O_RDONLY` non-blocking flock). All scratch
  lived in `~/Projects/shokunin/tmp/r87-scribe-work`; every python
  invocation ran with `PYTHONDONTWRITEBYTECODE=1` and never imported the
  fixture. No LSP device was exposed to this seat; the work is read-only
  audit, so static reads + the pinned-copy dynamic exec were used and no
  text-rename risk exists.
- The pin-copy dynamic lock test wrote its witness only into the pin copy
  under scratch; the single lane-file touch was an `O_RDONLY` non-blocking
  flock whose content was unchanged (verified by before/after read + sha).
- Exactly one descendant was spawned: the frozen-probeParent `ufo-labrat`
  (read-only, advisory, no exec substrate, no edits).

---

## 7. Remaining risks / blockers

1. No verdict-bearing defect was found. Both cited green receipts re-derive
   end-to-end (328/328), the assigned focus is verified statically,
   dynamically (cross-TMPDIR serialization; dead-holder non-blocking;
   negative control raced), independently by a sibling seat and by the
   labrat, and all encoded claims hold on the raw receipt evidence.
2. Residual risks are preservation-level: the receipts are host-only (ADJ-2)
   and do not pin their source bytes; two red dev runs are undisclosed and
   their source bytes are lost (ADJ-1); the lock is fixed per checkout, so a
   fixture copied elsewhere locks its own `corpus/live` — TMPDIR-independence
   holds, global exclusion does not (E case).
3. ADJ-7 means the live lock witness no longer shows the author’s run-A pid
   and the live graph currently carries sibling `r87a_*` objects; the
   author’s five-run inventory and both cited receipt shas were stable
   throughout, and later sibling runs may add their own (non-author) dirs.
4. ADJ-9 is the only tracked-file item and is an operator decision
   (unchanged from r84/r85); no shipping decision is made or implied here.
5. No blockers for the round.

*Seat stop. Read-only; no commits; no judgment — the canonical Rust runtime
remains the sole judge.*
