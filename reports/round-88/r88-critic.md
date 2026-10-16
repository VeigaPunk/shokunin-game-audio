# r88 critic — wave-B gate on committed `c19bec96`

Seat: `ufo-executor` (critic duties as assigned by
`.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r88-critic.md`).
**Committed tree only** (`c19bec96`), zero tracked writes, nothing
committed. Receipts: `corpus/live/r88-critic/` (+ `MANIFEST.txt` with
shas and commands).

**Verdict: ADMIT-with-findings.** Every claim the task names is
**verified as specified** on the committed receipts and independently
reproduced read-only on the live host: bluetooth is vacuous-by-absence
(HID-only DualSense, `audio_uuids=[]`, 4/4 create-node fabrications
refused `res:-2`/`res:-22`, module-bluez5 loads refused, no
`module-bluez5*.so` on disk, 14 SPA files, codecs property present), the
`{id ∪ serial}` dump set rule holds on all four armed legs and on live
`id≠serial` nodes, the `ls ⊋ dump` Metadata split is 9-vs-4 with
`info all` silently omitting every Metadata object, `pactl` index ==
`object.serial` with 0 violations, the `pw-top -n` traps reproduce
exactly, and the r88 lock is **not `$TMPDIR`-scoped** (5/5 either-way
cases with an in-tree negative control). The committed verdict blocks
re-derive **0 failures** on both green receipts, and **62 mutations ×
2 runs (124 evaluations)** all behave as designed — the headline arms
RED, the volatile-field controls PASS. F1–F6 are
silent-skip / vacuity / receipt-completeness gaps proven by execution;
F7 is a disclosure gap; F8 is the inherited tree-relative lock residual,
**live-witnessed again** — this time by the wave's own r88-verifier
running the same committed bytes from a copied tree. Nothing here is a
shipping decision.

---

## 0. Method (what was actually executed)

| check | evidence |
|---|---|
| commit custody + diff shape + wiring (static) | `git show c19bec96 --numstat/--`; blob sha; hunk census; programmatic wiring assertions |
| receipt census (legs, failures, teardown, coverage, dev run) | `census.py` → `census.json`, `census.out` |
| per-run claim table (both green runs) | inline claims script → `claims.json` |
| **arm replay** — the three committed verdict blocks sliced **verbatim** out of the commit object and `exec`'d against the committed receipts (author-run pid bound), then **62 mutations × 2 runs (124 evaluations)** | `arm-replay.py` → `arm-replay.json`, `.out`; slices `verdict-*.py` (sha'd) |
| **lock either-way proof** — the committed r88 lock function sliced verbatim and run cross-/same-`TMPDIR` and cross-tree, with the committed r85 `$TMPDIR`-scoped lock as **negative control**, on scratch trees only | `locktest.py` + `locktest_child.py` → `locktest.json`, `locktest.out`; slices `lockfn-r88.py`, `lockfn-r85.py` |
| bounded **read-only** live corroboration | `live-readonly.py` → `live-readonly.json`, `.out` (read verbs only; no object created, loaded, unloaded, linked or destroyed; no stream spawned) |
| co-tenancy witness (concurrent sibling seat, captured live) | `co-tenancy-witness.txt` |

No live battery was re-run (a battery would mutate the host and would
contend with the sibling r88-verifier seat running the same lane during
this gate). Every run used
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`; loadavg at the author's runs **74.4–84.9**
(both green runs) and **95.9** at the dev run — load preferred, as the
task directs.

Arm-replay provenance: the arm text is the **committed text**, sliced
verbatim by function boundaries and the `# ---- verdicts ----` marker —
no paraphrase, no dedent (the slice is exec'd inside `if True:` so its
4-space indent stays byte-exact). The only bound substitution is the
**author run's own pid** (recovered from each receipt) into
`BTWIT_R88_{PID,PREFIX,NS,NS2,ROLE}`, because the committed `wd_cli_id`
arm compares against `r88a_ns_<pid>` (F10 below). Every slice is
archived with its sha in `MANIFEST.txt`.

---

## 1. Custody and wiring — verified

- committed fixture sha256
  `ad9d59b1e0dc5e2be4274f4966e571dabefed94076c06093eed1bf4cd2aef4c4`
  == `git show c19bec96:corpus/fixtures/measure_audio.py` == worktree ==
  the sha the author report claims for **both** runs. `git diff --quiet
  c19bec96 -- corpus/fixtures/measure_audio.py` → IDENTICAL.
- diff shape: `+1772/−3` in the fixture (numstat) + 175 lines of report.
  Six hunks (per-hunk `+/-` census): one **1748-line insertion** (the
  r88 block, appended between `pwbind_midi_r87_entry()`'s `return` and
  `def main()`), plus five wiring hunks (`+1` arg, `+1/−1` mutex sum,
  `+20` dispatch, `+1/−1` mode, `+1/−1` suffix). **The only 3 deleted
  lines are exactly the three replaced wiring lines** (mutex sum, mode
  ternary, suffix ternary, verified by listing every `^-` line). No
  prior-family line (r76–r87) is touched; append/prepend only.
- wiring present and correct (programmatic assertions): the
  `--probe-btwit-r88` arg exists; `args.probe_btwit_r88` is in the mutex
  sum; the dispatch `if args.probe_btwit_r88:` runs with
  `_r88_family_lock = _btwit_r88_family_lock()` **before** the first
  entry and held to exit; `mode`/`suffix` carry `-btwit-r88` first in
  the ternary.
- guards checked statically in the committed block: private restore key
  `r88arole<pid>` (never the shared `music`); **no `set-default-*` call
  anywhere** (the only occurrence is the comment saying so); every
  unload goes through `_pactlmon_r85_unload_own`; residual
  `r88a_<pid>`-tagged nodes are destroyed by id before the final sweep;
  the `pw-play` stream is bounded and killed by process group
  (`_alsapw_r84_killpg`); `sinks_gone`/`own_nodes_after` armed.
- `compile()` of the committed source is clean (no `py_compile` run —
  bytecode is never written into the tree).
- receipt census: **3 entries / 79 legs** (btabs 28, witdiff 41,
  pwtop 10) in **both** green runs; leg names **byte-identical** across
  the two runs (`census.json:legname_identity` A==B for all three);
  `failures` empty and `coverage_blocked` absent on all three entries in
  both runs. Canonical receipt shas:
  run A `20261016T072313132218Z` → `a1c7746d…e83d4`;
  run B `20261016T072341162452Z` → `cce9164f…b640d`.

## 2. The three entries — receipt evidence (run A / run B, identical)

| entry | claim | sharpest committed evidence |
|---|---|---|
| `btabs_bluez_r88_probe` (28) | bluetooth VACUOUS-by-absence | adapter `hci0` Powered `b true`, Media1 `110a`+`110b`; the one device `dev_BC_C7_46_34_C5_66` = DualSense, `uuid16=[1124,1200]`, `audio_uuids=[]`, Connected=false, Paired=true, Class 1288, `input-gaming`; 0 bluez cards, 0 bluez sinks; `pactl list` has exactly **1** bluez-family line = the `session.services` advertisement (`bluetooth.audio`); the only bluez5 graph object is `bluez_midi.server` `Midi/Bridge`; `module-bluez5-{discover,device}` rc 1 `pa_module_noent` in **4 argv shapes**; `send-message` rc 1 `pa_sendmsg_noent`; `set-card-profile` on the absent card rc 1 `pa_module_noent` **with the V3 confound armed as a first-class leg** (bogus profile on a real card → same text; same profile on the real card → rc 0); 14 SPA files; codecs strings 2 hits + 0 standalone; 0 `module-bluez5*.so`; **4/4 create-node refusals**: `.a2dp-sink`/`.sink` rc 0 `pwcli_remote_enoent` `res:-2`, `.a2dp.source`/`.midi.node` rc 0 `pwcli_remote_einval` `res:-22`, `can't create node`; `bz_own_residue=[]`; `mods_before==mods_after` |
| `witdiff_dump_r88_probe` (41) | the witness-diff lattice | set rule 4/4 `got==predicted`, no churn re-census; `pw-dump <id>` returns no ports; `-R`/`-i 0` same member set; `-s` carries `id =` + `object.serial =`; `pw-cli info` id-keyed (serial → `unknown global` rc 0); `ls Node` exposes `object.serial`; layouts flat (ls) vs star (info); prop keysets equal on Node+Device; params names equal, `dump_empty` ⊆ cli; silent classes (dead/abc/huge dumps, dead-serial dump, ls-only-metadata info) all rc 0 + both streams empty; `''` = full census; two-arg dump honors id1 only; `--color=always` ANSI breaks JSON; `-1` rc 255 `pwdump_invalid_opt`; **Metadata 9 (ls) vs 4 (dump)**, extra `[35,37,38,41,42]`; `info all` describes 85 of 91/92 (run A/B) and **zero** Metadata; `enum-params` 4≡Format byte-identical on the readable `Props`/`2` pair, `BogusXYZ` → `unknown param type`, Client → `not implemented`; **`pactl` index == `object.serial` 6/6, 0 violations, own index follows**; idle state pactl `SUSPENDED` ↔ dump `suspended` ↔ cli `suspended` |
| `pwtop_r88_probe` (10) | the frame lattice | `-n 1` exactly 1 frame, **all rows `C`** (12/12); `-n 0` 1 frame; `-n 3` 3 frames `[C] → [I,S] → [I,S]`, own row non-`C` in the last frame, attempt 1; `-n -1`/`-n abc` infinite, killed at the 4 s bound, rc −9, frames present; `-r` bogus rc 255 `pwtop_connect_down` `Can't connect: Host is down`; four-witness agreement idle (`SUSPENDED`/`suspended`/`suspended`/`S`) **and** driven (`RUNNING`/`running`/`running`/`R`, `linked: true`) |
| teardown (all) | | `sinks_gone` true, `own_nodes_after` `[]`, `unloads` name-verified, `foreign_r88a_nodes` `[]`, `contention.host_is_quiet` true on both runs |

## 3. Arm replay — re-derivation and either-way mutations

**Re-derivation on the committed receipts** (committed verdict blocks,
receipt legs, author-run pid bound):

- run A and run B: `btabs` **0** failures, `witdiff` **0** failures,
  `pwtop` **0** failures — matching each receipt's recorded `failures`.
- The as-recorded `pwtop` re-derivation additionally emits a **spurious
  `coverage_blocked`** (`pt_n3: 0 frames in 1 tries …`): the verdict
  consumes `legs["pt_n3"]["_frames_cache"]` and pops it, and the helper
  pops `stdout_raw`/`stderr_raw` — so neither survives into the receipt
  (F4). With the cache reconstructed to the recorded
  `frames`/`status_sets`/`last_frame_status_hist` (`P9c`), `pt_n3`
  re-derives clean (0 failures).
- dev run `btabs`: the committed verdict block **reproduces 6/6** of the
  dev receipt's recorded failures; its `witdiff`/`pwtop` legs are an
  earlier shape (`wd_enum_props`/`wd_enum_num2` absent, `pt_n2` not
  `pt_n3`) → `KeyError`, i.e. not re-derivable, as expected for a
  different code state.

**Mutation battery: 62 mutations × 2 runs = 124 evaluations, 0
not-as-designed.** The headline claims are armed **either-way and
sharply**:

- btabs 40/40 RED: device gains an audio UUID; bluez card/sink appears;
  bridge becomes `Audio/Sink`; adapter unpowered; Media1 loses A2DP;
  each fabrication refusal class inverted; residue recorded; bluez
  module loaded; load-module/send-message succeed; SPA count 13; codecs
  property gone; module found on disk; MediaTransport appears; second
  pactl line; positive control fails; bogus-profile confound stops
  reproducing; adapter gone.
- witdiff 52/52 RED: set rule gains/loses an id; ports nested; mode
  variant; `-s` pair missing; cli serial resolves; ls serial hidden;
  layouts swapped; keysets/params diverge; silent classes speak; `''`
  partial; two-arg honors both; ANSI parses; `-1` rc 0; Metadata
  not-superset; `info all` describes Metadata; numeric≠name; bogus
  class; serial violation; vocab split; write-only param returns a pod.
- pwtop 26/26 RED: `-n 1` two frames / non-`C`; `-n 0` two frames;
  `-n -1` exits; `-n abc` no frames; `-r` quiet; idle/active vocab
  split; own row still CREATING.
- controls 6/6 PASS: volatile `wall_s`/`argv`/`stderr` noise is
  **not** armed (C1–C3), and the reconstructed `pt_n3` cache with a
  non-`C` own row is PASS (P9c) — so the REDs above are targeted, not
  blanket.

## 4. The fixed-path lock — either-way proof

The committed r88 lock function was sliced verbatim and run on scratch
trees (`corpus/live/r88-critic/locktest/`) so the live lane lock file
was never written. The r85 `Path(tempfile.gettempdir())` shape — also
sliced from the same committed file — is the **negative control**.
**5/5 as designed:**

| case | lock | trees | TMPDIRs | expected | result |
|---|---|---|---|---|---|
| A | r88 | same | same | SERIALIZED | **SERIALIZED** (child waited 1.500 s) |
| B | r88 | same | **different** | SERIALIZED | **SERIALIZED** (waited 1.523 s) |
| C | r85 | same | different | RACED (control) | **RACED** (0.000 s) |
| D | r88 | **different** | same | RACED | **RACED** (0.003 s) |
| E | r85 | same | same | SERIALIZED | **SERIALIZED** (waited 1.518 s) |

Case B is the task's claim: the r88 lock is a **fixed lane path**
(`ROOT/live/measure_audio-btwit-r88.lock`, never `$TMPDIR`), so
cross-`TMPDIR` same-family runs exclude. Case C proves the harness can
detect racing, so A/B/E are not false-greens. Case D is F8 below.

## 5. Findings

**F1 — medium — the HID-only device-record claim silently skips when
the device list is empty.** `btabs`'s device loop
`for rec in (legs["bz_device"].get("devices") or [])` has no arm on
non-emptiness. Proven (`B20`, both runs): `devices=[]` → **PASS, 0
failures, no `coverage_blocked`**. The tree leg records the device list
but is armed only on adapters, so on a host/moment with zero paired
devices the "measured, not assumed" HID-only claim is vacuous in
silence. Same class as the wave's r85 F2 / r86 F1 / r87 F1–F2. Fix:
`coverage_blocked` when the device list is empty (or arm it).

**F2 — low — the foreign set-rule legs silently skip.** The verdict
loop `for name in (…): l = legs.get(name); if not l: continue`, and
`wd_setrule_foreign_id`/`foreign_serial` are only built when a foreign
node exists. Proven (`W23`, both runs): both legs removed → **PASS, no
`coverage_blocked`**. Latent on this host (a foreign node always
exists). Fix: record the unmeasured halves as `coverage_blocked`.

**F3 — low — the two-arg dump arm silently skips when no foreign id
exists.** `wd_dump_two` is built only `if f_id`; the verdict guards with
`if l and …`. Proven (`W24`, both runs): leg removed → **PASS, no
`coverage_blocked`**. Latent. Fix: `coverage_blocked` on the missing
leg.

**F4 — low-medium — the `pt_n3` verdict input is not recorded
(receipt completeness).** The verdict reads
`legs["pt_n3"]["_frames_cache"]` and **pops** it; the helper pops
`stdout_raw`/`stderr_raw` before returning. The receipt therefore
contains the arm's *output* (`last_frame_status_hist`) and the helper's
own summaries (`frames`, `status_sets`), but **not the per-row frames
the arm judged**. Re-deriving the committed verdict on the receipt
as-recorded yields a spurious `coverage_blocked: pt_n3: 0 frames …`.
This is not a false-green (the arm did run in-run, and the recorded
`frames`/`status_sets`/`hist` are consistent with the claim), but the
green `pt_n3` verdict is not reproducible from the receipt alone. Fix:
record the parsed rows (or a compact `(status,id)` list) under a key the
verdict does not pop.

**F5 — low — the four-witness vocab guards are structurally vacuous
when `vocab` is absent.** Proven (`P11`: `{linked:true, top_frames:3}`
→ PASS; `P12`: `{top_frames:3}` → PASS; both runs, no failure, no new
`coverage_blocked`): `len({None,…}) != 1` is False and `None in {}` is
False, so a missing vocab passes the agreement check silently. Latent —
the recorder writes `vocab` in the same update — same class as r87 F6.
Fix: `if not l.get("vocab"): coverage_blocked`.

**F6 — low — the write-only no-pod signature admits a classless rc≠0
silence.** The `wd_enum_fmt`/`wd_enum_num4` arms only reject
`has_pod`; the "silent" outcome is `error_class is None` regardless of
rc. Proven (`W26`, both runs): `exit_code=1, stdout="", stderr="",
class=None` → **PASS** and recorded as outcome `silent`. Latent (both
green runs measured rc 0: run A `res:-5` for `Format`, run B silent;
dev `res:-5`). Fix: require rc 0 for the silent signature, as every
other silence arm does.

**F7 — informational (disclosure) — one RED dev run is present and
never cited.** `corpus/live/runs/20261016T071710822152Z-btwit-r88/`
is a **red** run (75 legs, 13 failures: btabs 6, witdiff 5, pwtop 3 —
e.g. `cli_cant_create` refusal classes, empty codecs strings, empty ls
Metadata, `pt_n2`). The report references dev discovery narratively
("Newly discovered in dev…", "a dev capture emitted 1 frame") but gives
no run id, sha or failure census. The r87 scribe's ADJ-1 precedent
("2 undisclosed RED dev runs") applies. Note the dev btabs failures are
**reproduced 6/6** by the committed verdict block on the dev receipt,
so the dev run is genuine evidence of the pre-fix state, not noise.
**Independently corroborated during this gate**: the r88-scribe commit
`2226b92e` ("r88 scribe: INTACT — …; ADJ-1: uncited RED dev run (3rd
round of the class)") flags the same run as its ADJ-1.

**F8 — medium (inherited, and LIVE-WITNESSED again) — the fixed-path
lock is *tree-relative*.** `ROOT = Path(__file__).resolve().parents[1]`,
so the lock lives at `<tree>/corpus/live/measure_audio-btwit-r88.lock`:
a same-family run from a **copied tree** takes a different lock file and
is not serialized. Proven by locktest case **D** (cross-tree → RACED,
0.003 s) and **realized live during this gate** — see §7. Within this
wave `TMPDIR` is pinned and the author's two runs shared a tree, so the
two green runs did serialize. This is the r86 F1/F6 → r87 F10 residual,
now fourth round running. Fix remains a design decision (an OS-level
named lock or an in-daemon sentinel), not this gate's.

**F9 — informational — report-vs-receipt nuance on the enum refusal
path.** The report attributes the `Format` `res:-5` variant to "the dev
run"; the **green run A** receipt also shows `pwcli_remote_eio` on
`wd_enum_fmt` (run B is silent/silent). The claim "the refusal path
varies, the no-pod signature does not" is *more* true than the report
says — no action needed beyond the text.

**F10 — informational (replay note, not a defect) — the `wd_cli_id`
arm embeds the run's own pid** (`BTWIT_R88_NS = r88a_ns_<pid>`, the
recorded `node.name`). A replay that does not bind the author run's pid
falsely REDs this arm; with the pid bound it re-derives clean. Recorded
so a later reader does not mistake the artifact for a defect.

**F11 — informational — no in-receipt implementation sha.** The
receipts carry `mode`/`thresholds`/`measurements` but no source hash;
"two green on identical bytes" rests on the worktree == commit ==
claimed sha and the author's statement, not on receipt content. The
wave convention may not include one; noted for the verifier/reviewer
audit trail.

## 6. Live corroboration (read-only, independent of the author's receipts)

`live-readonly.json` / `.out`; every command a read verb, all bounded.

- **BlueZ absent class reproduced on the live host**: adapter
  `/org/bluez/hci0` Powered `b true`; Media1 `as 2 "0000110a-…"
  "0000110b-…"`; the one device `dev_BC_C7_46_34_C5_66` with
  `as 2 "00001124-…" "00001200-…"` (HID + PnP only), Class `u 1288`,
  Icon `s "input-gaming"`, Connected `b false`, Paired `b true`; zero
  bluez cards, zero bluez sinks; the single `pactl list` match is the
  `session.services` line; 14 SPA files; `strings` finds
  `spa.bluez5.codecs` + `property bluez5.codecs '%s' is not an array`
  (2 substring hits, 0 standalone, 126 `bluez5.` names); zero
  `module-bluez5*.so`; the only bluez5 graph object is
  `bluez_midi.server` id 49 `Midi/Bridge` — **zero Audio/\* bluez
  objects**.
- **Set rule on live `id≠serial` nodes**: node `232`/serial `172871`,
  `97`/`172872`, `175`/`172873` — `pw-dump <id>`, `pw-dump <serial>`,
  `-R`, `-i 0` all return exactly the predicted set (1 object, 0
  ports); `pw-dump <id> <other>` honors the first only; `-s` carries
  `id =` + `object.serial =`. (The author's receipts additionally arm
  the own node 153 vs serial 251940 on both runs.)
- **Metadata split**: dump `[31,34,36,39]` vs ls
  `[31,34,35,36,37,38,39,41,42]` → 9-vs-4, extra `[35,37,38,41,42]`;
  `pw-cli info 35` (ls-only) = rc 0 with **both streams empty**;
  `info all` describes 79 of 85 objects with **zero** Metadata — the
  silent-omission class is real.
- **`pactl` index == `object.serial`**: 5/5 matched, 0 violations,
  0 unmatched (the author's own `r88a_ns_1262851` is gone, correctly
  unloaded; the two foreign residue sinks `r84a_probe_548706`,
  `r87t_ns` match too).
- **pw-top traps**: `-n 1` → 1 frame, statuses `[C]`; `-n 3` → 3
  frames `[C]`, `[I,S]`, `[I,S]`; `-n 0` → 1 frame; `-n -1` and
  `-n abc` → killed at the 4 s bound, rc −9, frames emitted; `-r bogus`
  → rc 255 `Can't connect: Host is down`.
- **Silent classes**: `pw-dump 98765432` / `abc` / `99999999999999999999`
  → rc 0, both streams empty; `pw-dump ''` → the full census (85 ==
  census); `pw-dump -1` → rc 255 `invalid option`; `pw-cli info
  <dead>` → rc 0 + `unknown global`; `pw-cli ls Node` exposes
  `object.serial`; `enum-params <dead> Format` → rc 0 + `unknown
  global`.
- **Idle four-witness agreement** (no stream spawned): pactl
  `SUSPENDED` / dump `suspended` / cli `suspended` / top `S`.

## 7. Co-tenancy witness — captured live (`co-tenancy-witness.txt`)

At `2026-10-16T04:27–04:28Z`, while this gate was running, the wave's
own **r88-verifier** seat was executing the committed bytes from a
**copied tree**:

```
pid 1450101  python3 corpus/fixtures/measure_audio.py --probe-btwit-r88
             launched from  corpus/live/r88-verifier/tree
fd 3 ->      corpus/live/r88-verifier/tree/corpus/live/measure_audio-btwit-r88.lock
stdout ->    corpus/live/r88-verifier/runs/r88v5.stdout.json
```

- the **lane** lock `corpus/live/measure_audio-btwit-r88.lock` was
  **FREE** (still carrying the author's run-B witness
  `pid=1298372 …`, mtime 04:23) while the verifier was mid-run — the two
  runs were **not** serialized;
- the verifier's own **tree** lock carries `pid=1450101 ns=r88a_ns_1450101
  role=r88arole1450101`;
- the verifier has since completed (its runs dir shows 5 verifier runs
  plus author-receipt replays and laws/surface diff tooling).

This is **F8 realized**, not hypothetical — and for the fourth
consecutive round it is the wave's own sibling seat. The committed
design's response (foreign names recorded, never judged; own-pid-only
teardown) is the right one, and it is what makes this tolerable rather
than fatal. **Disclosed by name as required.**

## 8. Probe tooling note

The frozen probeParent dispatched **exactly one** read-only `labrat`
(hypotheses: the bluez absent class and the `{id ∪ serial}` set rule).
Its substrate exposed only file-inspection tools (no exec), so it
returned **STILL NO EXEC**. Per the seat card the dispatch was
**retried once after warmup to the same child seat** (not a second
spawn); it again returned **`STILL NO EXEC`**. That unavailability is
recorded here as **unavailability, not absence**. The child made no
edits and left nothing behind. The dispatcher then ran the bounded
read-only battery directly (§6), which confirmed both hypotheses.

## 9. Blockers / remaining risks

- **Blockers: none.**
- F1–F3, F5 are the same silent-skip/vacuity class the wave has now
  flagged in four consecutive rounds (r85 F2, r86 F1, r87 F1/F2, r88
  F1–F3/F5); all are proven by execution and all are small guards.
- F4 is a receipt-completeness gap: the `pt_n3` verdict is green and
  its recorded summaries are consistent, but it cannot be re-derived
  from the receipt alone.
- F8 is inherited, live again, and only a cross-tree design change
  closes it; within a single tree the fixed path does exclude.
- No battery re-run: the sibling r88-verifier was mid-run on the same
  lane; the host was left as found by this gate (read verbs only).

## 10. Custody notes

- **Zero tracked writes.** The fixture in the worktree is byte-identical
  to the commit object; nothing was staged or committed. The only dirty
  tracked path is `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`,
  which was **already `M`** in this session's first `git status`
  (mtime 04:22, before this seat started); all gate runs used
  `PYTHONDONTWRITEBYTECODE=1`, and no `__pycache__` exists under
  `corpus/live/r88-critic/`.
- **HEAD moved during the gate** (not by this seat): `c8a958e2` (the
  **r87 verifier** lane, "GATE FAIL — create_badfac/create_usage …")
  landed on top of `c19bec96`, then `2226b92e` (the **r88 scribe**
  lane). The r88 fixture is unaffected throughout
  (`git diff --quiet c19bec96 -- corpus/fixtures/measure_audio.py` →
  identical at every check), and this gate's custody is the r88 author
  commit named in the task. Disclosed so a later reader is not
  surprised by the sha.
- **Lock-file disclosure.** The live lane lock
  `corpus/live/measure_audio-btwit-r88.lock` was **never written** by
  this gate (sha `930d6404…`, still the author's run-B witness): the
  either-way proof ran on scratch trees under
  `corpus/live/r88-critic/locktest/`. All gate receipts live under
  `corpus/live/r88-critic/` (untracked); the report is
  `reports/round-88/r88-critic.md` (untracked, uncommitted).
