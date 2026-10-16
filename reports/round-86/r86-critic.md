# r86 critic — wave-B gate on committed `fa5994a0`

Seat: `ufo-executor` (critic duties as assigned by
`.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r86-critic.md`).
**Committed tree only** (`fa5994a0`), zero tracked writes, nothing
committed. Receipts: `corpus/live/r86-critic/` (+ `MANIFEST.txt` with
shas + commands).

**Verdict: ADMIT-with-findings.** The r84 fold named in the task is
**verified as specified** (the r86 family lock is a fixed lane path and
is *not* `$TMPDIR`-scoped — proven either-way with a negative control),
the committed receipts re-derive green under the committed verdict
blocks on both runs, and the three named caveats are exactly what the
author says they are (record-only / rc-only). F1–F2 are latent
absorption/coverage channels, F3–F5 are arm-strength gaps (all latent,
none realized in the committed receipts), F6 is a residual co-tenancy
channel of the lock that this session **live-witnessed** (the wave's own
verifier ran the same committed bytes from a copied tree concurrently),
F7–F9 are hygiene/informational. Nothing here is a shipping decision.

---

## 0. Method (what was actually executed)

| check | evidence |
|---|---|
| commit custody + diff shape + guards (static) | `git show fa5994a0 --numstat/--`; blob sha; `grep` over the committed family block |
| receipt census (legs, failures, teardown, caveats) | `census.py` → `census.json`, `census.out` |
| **lock either-way proof** — verbatim committed lock functions run cross-/same-`TMPDIR`, with the r85 lock as a negative control | `locktest.py` + `locktest_child.py` → `locktest.json`, `locktest.out` |
| **arm replay** — the five committed verdict blocks sliced out of `git show fa5994a0:…` by marker and `exec`'d: re-derivation on both committed receipts + 13 targeted mutations | `arm-replay.py` → `arm-replay.json`, `arm-replay.out` |
| bounded **read-only** live corroboration (read verbs only) | `live-readonly/probe.py` → `live-readonly.json`, `probe.out` |
| co-tenancy witness (concurrent verifier run) | `co-tenancy-witness.txt` |

No battery was re-run (a battery would mutate the host). Every run with
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`;
live loadavg **85.31–88** (load preferred). The lock harness holds/writes
only the two lock files (`corpus/live/measure_audio-pwctl-r86.lock`,
untracked; and two scratch `$TMPDIR`s), nothing tracked.

Arm-replay provenance: the arm text is the **committed text**, sliced
verbatim; only `PWCTL_R86_PID` is parameterised per run (2661839 /
2675030, parsed from the receipts' own `r86a_<pid>_remote` witness) so
that pid-bearing arms compare against the right namespace.

---

## 1. Custody and wiring — verified

- committed fixture sha256
  `5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780`
  == worktree == the sha the author report claims for both runs.
- diff shape: `+1758/−3` in the fixture (numstat). One 1722-line
  insertion hunk (`@@ -23726,6 +23727,1728 @@`) between
  `pactlmon_negctl_r85_entry()`'s `return` and `main()`, plus six wiring
  hunks. **The only 3 deleted lines are exactly the three replaced
  wiring lines** (mutex sum, `mode` ternary, `suffix` ternary); the only
  other non-block change is `import resource` (`@@ -9,6 +9,7 @@`).
  No prior-family line (r76–r85) is touched.
- wiring present and correct: `--probe-pwctl-r86` (25578), mutex sum
  includes it (25586), dispatch `if args.probe_pwctl_r86:` (25944) with
  `_r86_family_lock = _pwctl_r86_family_lock()` **before** the first
  entry and held to exit (25964), `mode` (26625), `suffix` (26645).
- receipt census: 5 entries / **149 legs** (addr 34, params 43, dsp 16,
  meta 22, tools 34) in **both** green runs; leg names byte-identical
  across runs (`census.json:_legname_diff_run1_run2` = IDENTICAL);
  `failures` empty for all 22 entries in both runs; `coverage_blocked`
  absent everywhere.
- teardown witnesses, both runs, all five entries: every unload
  `verified_index == captured` (536870922), `recycled: False`,
  `exit_code 0`; `sinks_gone` true; `own_nodes_after: []`;
  `meta_keys_gone: true` (meta entry). Matches the author's claim
  sentence-for-sentence.
- guards checked statically in the committed block: private restore key
  `r86arole<pid>` (never `music`); **no `set-default-*` call anywhere**
  (comments only); the only `set-sink-volume` calls target
  `PWCTL_R86_NS` (the probe's own sink); subject-0 metadata is read-only
  (`subj0_read`, `-m 0`); `setp("0", …)` is a refused Core set-param
  witness, not a write; every unload goes through
  `_pactlmon_r85_unload_own` (21879–21902, index re-read + own
  `sink_name=` byte-match immediately before firing, stale ids never
  fired); crash-class legs run with `RLIMIT_CORE=0`
  (`_pwctl_r86_no_core`, `nocore=True` on `cli_devnull`, always in
  `_pwctl_r86_sigleg`).
- provenance note: the green receipts carry post-verdict markers that
  only the committed text writes — `ls_Node.typed_rows=4`,
  `info_link.format_pod=True`, `dump_color_eq.armed=False`,
  `d_route.armed=False`, `n_format.armed="rc_only"` — while the pre-fix
  dev receipt lacks `n_format.armed` and fails exactly on the old
  pod-presence assertion (see §4). So the green pair was produced by the
  corrected (committed) code, not the dev bytes. As in r85, the receipt
  does **not** embed a fixture hash: the run→file binding is the
  author's claim + these structural markers.
- the disclosed dev run (`20261016T062922907396Z`, sha `090a50ab…`) has
  exactly one failure in the whole receipt:
  `n_format: rc=0 pod=True — the pod-absence law fails`, and no
  `armed` key on that leg. The correction between dev and green touched
  only that arm.

## 2. The five entries — receipt evidence (run1 / run2)

| entry | law surface | sharpest committed evidence |
|---|---|---|
| `addr` (34 legs) | addressing split, class census, pw-dump surface, self-Client, destroy | `ls <serial>` 228 B with `object.serial` + `id <nid>,`; `ls <id>` **0 B**; `info <serial>` rc0 `pwcli_unknown_global`; `dump_id`≡`dump_serial` (11564 B, 700-char preview equal); `dump_badid`/`dump_bogus`/`dump_color_sep` 0 B rc0; `dump_color_join` 420 KB; self-clients 1/1 with fresh serials (242898→242899 / 243277→243278); `info 31` (live metadata) 0 B rc0; `remote_down` rc≠0 `failed to connect` |
| `params` (43 legs) | enum-params matrix + set-param refusals | pods present for Node{Props,PropInfo,EnumFormat}/Port{EnumFormat,Latency,IO,Meta}/Device{Profile,EnumProfile,EnumRoute}; pod-absent `p_format`/`n_latency`/`n_proclat`; remote ENOENT rows; `not implemented` for Client/Factory/Module/Link/Core; `None` echo, empty pod, stripped `zzz`, wrong-type None-slot, remote `-95`, port echo-lie + `minQuantum` unchanged, bad id, usage |
| `dsp` (16 legs) | set-param as live DSP | windowed medians: solo 8192 → cv25 **2048.0** → cv50 **4096.0** → mute **0.0** → reset 8192.0/8191.5 → dead-scalar **8192.0** (store reads Float 0.25 back; pactl 100 %) → pactl 25 % **128.0** → 100 % **8192.0**; pactl read-back after cv25 ∈ (50,80) (≈63 %); tap link-validated before the player spawned (player attach sink 243000/243370, 94/93 windows) |
| `meta` (22 legs) | store laws + census gap | `-l` = `ls Metadata` = 9 stores `[31,34,35,36,37,38,39,41,42]`, pw-dump strict subset `[31,34,36,39]`; bare ≡ `-n default`; bogus store 0 B rc0; echo→persist on the live subject, full-replace overwrite, `Spa:String` verbatim, absent-key Found-only, `-d` key/subject semantics, dead-99997 echo-lies, `-m <subj>` filter (kill-bounded), subject-0 read-only baseline |
| `tools` (34 legs) | process surfaces | `pw-top -b -n 2/0` rc0; batch+TERM rc0 **vs TUI+TERM SIGABRT + `loop.c:189`** (both runs); `pw-cli </dev/null` SIGABRT, pipe-stdin SIGKILL-bound, `quit` rc0; pw-jack env lattice `512/48000`, `256/44100`, `-s` alone unset, `-v/-vv/preset` → 3/4/5, `-r` REMOTE, rc0 usage family, bogus payload rc127; pw-link create rc0, duplicate **255 File exists**, bogus 255, modifiers/usage 255, `-d <port>` 255, `-d <link>` rc0, junk props silently accepted + link formed |

`foreign_r86a_nodes: []` in all ten entry runs — the author's pair ran
without same-family co-tenancy. Receipt loadavg 52.60–68.87.

## 3. The r84 fold — the family lock is NOT `$TMPDIR`-scoped (headline)

**Static.** `_pwctl_r86_family_lock()` (24118–24136) opens
`ROOT / "live" / "measure_audio-pwctl-r86.lock"` (24124) where
`ROOT = Path(__file__).resolve().parents[1]` = `<tree>/corpus`; no
`tempfile`, no `gettempdir()`, no env interpolation anywhere in the
function. Contrast the inherited r85 lock (22314–22330), which is
`Path(tempfile.gettempdir()) / "measure_audio-pactlmon-r85.lock"`.
The lock is taken in the dispatch block (25964) before the first entry
and held to process exit.

**Empirical either-way proof** (`locktest.py`; the committed function
text is `exec`'d verbatim, only `ROOT`/pid constants bound):

| case | TMPDIR | lock path observed | contender wait |
|---|---|---|---|
| A: r86 lock, **cross-`TMPDIR`** | A vs B | both `…/corpus/live/measure_audio-pwctl-r86.lock` | **2.2064 s** (holder held 3.0 s) |
| B: r86 lock, same `TMPDIR` | A vs A | same fixed path | **2.2105 s** |
| C: **r85** lock, cross-`TMPDIR` (negative control) | A vs B | `…/r86crit-lock-a/…-r85.lock` vs `…/r86crit-lock-b/…-r85.lock` | **0.0001 s** — *no exclusion* |

**Verdict: the r84 F1 defect is fixed for the dimension it names.** Two
same-tree runs with different `TMPDIR`s serialize (A); the same-tree
control behaves identically (B); the r85 lock demonstrably does not (C),
which proves the harness can detect non-exclusion.

**Residual (F6, live-witnessed):** the path is fixed *relative to the
tree*, so a same-family run from a **different tree** is not excluded.
During this session the wave's own `r86-verifier` ran the committed
bytes (`sha256 5ceba940…`) from `corpus/live/r86-verifier/tree` with its
own lock file (`…/r86-verifier/tree/corpus/live/measure_audio-pwctl-r86.lock`,
pid 2831406) while this lane's lock file was held by this seat's test
(pid 2808000); neither waited on the other, and the verifier's
`normal`/`r86v1`/`r86v2` runs all completed rc=0. In-flight, this lane's
read-only census saw the verifier's `r86a_ns_2810553` (10 dump rows), 1
`r86a` module and the `r86a_k_f` metadata key. Transcript:
`co-tenancy-witness.txt`.

## 4. The three named caveats — confirmed as documented

| caveat | committed text | replay result |
|---|---|---|
| `d_route` **record-only** | leg 24596–24597; `legs["d_route"]["armed"] = False` (24657); no assertion | committed (0 B, no pod) passes; the dump realization (pod present) **also passes** → inert either way, as designed |
| `dump_color_eq` **record-only** | leg 24310–24311; `armed = False` (24454); no assertion | this boot: rc255 + `pwcli_dump_color`; the boundary's other boot (0 B rc0) **also passes** → inert either way, as designed |
| `n_format` **rc-only** | 24643–24648: fails only on `exit_code != 0`; `armed = "rc_only"` | pod-present (both green runs: rc0, 863 B, `has_pod: True`) passes; pod-absent (the boundary realization) **also passes**; rc≠0 **fails** (control). The "Format exposure tracks negotiation" law is therefore *recorded*, not armed — only the rc0-acceptance family is armed |

## 5. Arm replay — re-derivation and absorption gaps

**Re-derivation:** the five committed verdict blocks, exec'd against the
committed run1 and run2 legs, produce **0 failures on both runs**
(`arm-replay.json:rederive_*`). The committed receipts are internally
consistent with the committed arms.

**Absorption / coverage demos** (run1 legs, one mutation each) and
**controls**:

| case | mutation | result | reading |
|---|---|---|---|
| A1 | `dump_serial.stdout_bytes` +137 (previews equal) | **passes** | F4: the `<id>`≡`<serial>` arm compares only the 700-char preview; byte-length equality is not armed |
| A2 | `ls <id>` returns the node's `id N, type …` row without the serial line | **passes** | F5: "did not resolve" is armed as absence of `object.serial` only |
| A3 | `dump_full1.self_clients = 2` + a stale serial | **passes** | F3: the report's "exactly 1 fresh client" is armed as `self_clients >= 1`; serial freshness recorded, not armed |
| A4 | `dump_color_eq` = 0 B rc0 (other boot) | **passes** | record-only, by design |
| P1 | `n_format.has_pod = False` | **passes** | rc-only, by design |
| P3 | `d_route` = pod present | **passes** | record-only, by design |
| P4 | delete `c_props/f_props/m_props/l_props/core_setparam` | **passes**, no block | F2: rows silently skipped when their subject/`dump_ids` lookup fails (24680 `if l is None: continue`) |
| M1 | `meta_census.dump_ids = []` | **passes** | F1: `set([]) < set(ls_ids)` is trivially true — the census-gap law is not armed against an empty dump set |
| M3 | `meta_census.ls_ids = []` | **passes**, no block | F1: the whole arm is skipped by the 25115 guard; no `coverage_blocked` |
| P2 | `n_format.exit_code = 1` | **FAILS** (control) | the rc family is armed |
| M2 | `dump_ids = ls_ids` | **FAILS** (control) | the strict-subset check is armed |
| T1 | `cli_devnull` clean exit | **FAILS** (control) | the abort class is armed |
| D1 | `cv25 = 8192` | **FAILS** (control) | the linear-DSP envelope is armed |

None of the five absorption/gap channels is realized in the committed
receipts (dump set non-empty and strict subset; all not-implemented rows
present; `self_clients == 1`; previews equal *and* full bytes equal, see
§6). They are latent.

## 6. Live read-only corroboration (independent of the author's receipts)

`live-readonly/probe.json`, loadavg 85.31, read verbs only — subject =
the host's default sink node (`object.id` **232**, `object.serial`
**172871**):

- `pw-cli ls 172871` → 414 B node row; `pw-cli ls 232` → **0 B**;
  `pw-cli info 232` rc0; `pw-cli info 172871` rc0 +
  `unknown global '172871'`; `enum-params 172871` rc0 + same class →
  **the serial/id split holds now**.
- `pw-dump 232` vs `pw-dump 172871`: **full-byte equal**, 19433 B, equal
  sha256 → the F4 law itself holds in full on this host (the arm's
  preview-only comparison is the weak part, not the law).
- census: `pw-metadata -l` = `pw-cli ls Metadata` =
  `[31,34,35,36,37,38,39,41,42]`; `pw-dump` = `[31,34,36,39]` strict
  subset → **identical to the committed receipts**; `pw-cli info 31`
  (live store) → rc0, **0 B**.
- `pw-jack -p 512` → `Q=512/48000`; `-s 44100` alone → `Q=unset`;
  `pw-cli info bogus` rc0; `pw-cli -r <bogus> ls Node` → **rc 255**;
  `pw-top -b -n 2` rc0.
- residue at probe time: 0 `r86a` modules / nodes / default-store keys
  (the verifier's runs had exited and cleaned up).

## 7. Probe tooling note

The frozen `probeParent` dispatched exactly **one** read-only `labrat`
(H: "the r86 census-gap arm is vacuous on an empty pw-dump set and is
skipped entirely when the `ls Metadata` id list is empty"). The child
returned **CONFIRMED** with the verbatim committed lines (25115 guard,
25120 subset check) and both boolean evaluations; its substrate exposed
**file-read only (no exec, no git)**, so it did not execute anything — it
verified the claim by reading, which is sufficient for a code-logic
claim. It made no edits and left nothing behind. This is an independent
second opinion on F1, not the sole basis for it (my own mutation replay
M1/M3 is the primary evidence).

## 8. Findings

**F1 — medium — the census-gap law is not armed against an empty
`pw-dump` set, and vanishes silently on a `ls Metadata` reader failure.**
25114–25124: `if cen["store_ids"] and cen["ls_ids"]:` (25115) skips the
whole arm when either list is empty, and `set(dump_ids) < set(ls_ids)`
(25120) is trivially true for `dump_ids == []`. `_pwctl_r86_dump_ids`
returns `None` on reader failure, which the census dict stores as `[]`
(25059) — so a pw-dump parse failure would *pass* the census-gap law, and
a `ls Metadata` failure would remove the arm without a
`coverage_blocked`. Demonstrated (M1, M3); labrat-confirmed. Fix: require
`dump_ids and set(dump_ids) < set(ls_ids)`, and route an empty/None
`ls_ids` to `coverage_blocked`.

**F2 — medium — matrix rows are silently skipped when their subject
lookup fails.** 24677–24687 (`if l is None: continue`) covers
`c_props/f_props/m_props/l_props/core_setparam`; `l_props` also depends
on the entry's self-loop forming, and `meta_info_empty` (24321) is only
collected `if mids:`. A `pw-dump` client/factory/module lookup failure
would silently shrink the "not implemented" matrix with no failure and
no `coverage_blocked`. Demonstrated (P4). Not realized in the receipts
(all rows present, all subjects resolved).

**F3 — low — "exactly 1 fresh pw-dump client" is armed as `>= 1`.**
24455–24460: `l.get("self_clients", 0) < 1`; the report's stronger claim
("each invocation = exactly 1 fresh `pw-dump` client") is not what the
arm enforces, and the serial-freshness (`self_serials`) is recorded but
never compared. Demonstrated (A3: 2 clients + a stale serial passes).

**F4 — low — the `<id>`≡`<serial>` dump equality is armed over the
700-char preview.** `_pwctl_r86_run` stores `stdout = outt[:700]`
(23952) and 24437 compares those previews; `stdout_bytes` are not
compared either. Demonstrated (A1). The underlying law is nevertheless
true in full on this host (§6: 19433 B byte-equal), so this is arm
strength, not a false-green in the receipts.

**F5 — low — `ls <id>` "did not resolve" is armed as "the serial line is
absent".** 24379–24384. A partial resolution that prints the `id N,`
row without `object.serial` would pass. Demonstrated (A2). The stronger
arm is `stdout_bytes == 0`.

**F6 — low/medium (residual, live-witnessed) — the fixed lock is
tree-relative, so cross-tree same-family runs still co-tenant.** §3:
the r84/TMPDIR property is verified, but the lock file lives under
`ROOT/corpus/live/`, and a verifier/reviewer copy tree gets its own lock.
This session's concurrent `r86-verifier` run is the realized witness
(`co-tenancy-witness.txt`). Consequence for this family is bounded
(seat-owned `r86a_<pid>` names; census arms are shape-based), but the
lock no longer serializes the very seats that replay the family, and the
`meta_keys_gone` witness can false-red under co-tenancy (F7).

**F7 — low — two teardown-witness gaps.** (a) `own_nodes_after`
(24194–24197) matches `f"r86a_{PWCTL_R86_PID}" in n` or the loaded sink
names, but this pid's tap node is named `r86a_tap_<pid>` (23845), which
does *not* contain `r86a_<pid>` — a lingering tap node of this run is
invisible to the witness (the entry kills the tap first, so this is a
hole, not a realized leak; the pattern is inherited from r85).
(b) `meta_keys_gone` (24205–24208) greps the default store for **any**
`r86a_` line, not this pid's keys — under cross-tree co-tenancy (F6) a
foreign run's live keys would false-red this run's teardown.

**F8 — low (hygiene/doc).** The report and commit message say
`+1761/−3`; the committed diff is **`+1758/−3`** (numstat; the three
replaced wiring lines are already counted in the 1758). Also "loadavg
~50 during runs" vs the receipts' 52.60–68.87.

**F9 — informational.** The subject-0 baseline is deliberately
read-only-recorded: run1's key set is 4 keys (including
`default.audio.source`), run2's is 3 — the host realization differs
between the two runs and the receipts capture it without arming it
(disclosed in the author report; consistent with the boundary's
asymmetry note).

## 9. Blockers / remaining risks

- **Blockers: none.**
- Remaining risks: F1–F5 are latent absorption/coverage channels that a
  future low-load or reader-failure host can hit (F1 and F2 remove
  coverage without a `coverage_blocked`, so they are the two worth
  fixing first); F6/F7 mean same-family serialization holds within a
  tree but not across trees, and cross-tree co-tenancy can false-red the
  metadata-key witness; the record-only rows (`d_route`,
  `dump_color_eq`, `n_format` pod) and the subject-0 key set stay
  unarmed by design.
- Custody note: `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  was already `M` before this session (mtime 03:20:10, session start
  03:33:59) and was not touched here (all runs with
  `PYTHONDONTWRITEBYTECODE=1`; no import of the fixture). The fixture
  source is byte-identical to the commit. `corpus/live/measure_audio-pwctl-r86.lock`
  (untracked) now carries this seat's locktest witness line
  (`pid=2808000`), i.e. it was already an untracked artifact in the
  receipts area and stays untracked.

## 10. Receipts index

| artifact | what it is |
|---|---|
| `census.py` → `census.json`, `census.out` | 3-receipt leg census, teardown witnesses, caveat-arm states, run1↔run2 leg-name diff |
| `locktest.py` + `locktest_child.py` → `locktest.json`, `locktest.out` | A/B/C lock either-way proof with negative control |
| `arm-replay.py` → `arm-replay.json`, `arm-replay.out` | 2 re-derivations + 13 mutations against the verbatim committed verdict blocks |
| `live-readonly/probe.py` → `live-readonly.json`, `probe.out` | read-only live corroboration (addressing split, full-byte dump equality, census gap, pw-jack, rc family) |
| `co-tenancy-witness.txt` | the concurrent verifier run / tree-relative lock witness |
| `MANIFEST.txt` | shas of the above + the exact commands + custody inputs |
