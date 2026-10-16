# r86 REVIEWER — wave-B gate on committed `fa5994a0`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r86
pwctl landing — `git show fa5994a0 -- corpus/fixtures/measure_audio.py`
(committed blob `e030588c15390d2bea3cc2362f68fae9e170cd42`, sha256
`5ceba94019eaaa8f1db9ac18ea15023f7e4891e844defe86711f37873059b780`,
26 655 lines) plus the two committed receipts. Everything below was
measured against a **pinned copy of the committed blob**
(`corpus/live/r86-reviewer/measure_audio_fa5994a0.py` — `git hash-object`
== the committed blob; the working-tree file is byte-identical to it,
`git status --porcelain corpus/fixtures/measure_audio.py` is empty) and a
**pinned minimal tree** (`tree/corpus/fixtures/` = committed blob +
committed `build_artifacts.py` `0decb907…` + a copy of the committed
`corpus/artifacts/`) so the fixture's own receipt lands inside this
seat's receipt dir. **Zero tracked writes; nothing committed; no
`set-default-*`; no subject-0 write; no `r86a_*`/`r86b_*`/`r85v_*`
object of any co-tenant seat touched; every module this seat loaded was
unloaded name-verified.** The one tracked dirt at entry
(` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`, mtime
03:20:10) predates this seat and was not rewritten by it (its mtime is
unchanged; this seat's runs used the pinned tree and its own scripts).
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`
on every run.

The frozen `probeParent` seat dispatched **one** `ufo-labrat`
(agent `bd6e3069`, bounded r84-F1 fold probe). The child had **no
shell/exec tool** in its dispatch: it confirmed the fold **by source
reading** (quoted `ROOT / "live" / …` vs
`Path(tempfile.gettempdir()) / …`) and returned the *executed*
resolution as **UNTESTED**, with **zero side effects** (no file created,
no lock taken). No second probe was dispatched (the one-probe cap); the
empirical probe was then executed **in-seat** (§3) as the r85 seat did.

---

## 0. Verdict

**PASS with findings.** The r86 family is insertion-only, correctly
wired (6 hunks: `import resource`; the 1 722-line family block; the
`add_argument`; the mutex-sum, mode and suffix ternaries extended — the
three deletions are *pure term insertions*, verified by string surgery),
its 5 entries / **149 legs** reproduce `failures: {}` in both committed
receipts, **every armed verdict re-derives independently from the
receipt data alone (204/204 checks on each committed receipt)**, the
declared caveat rows are exactly as declared (`dump_color_eq` and
`d_route` `armed: False`; `n_format` `armed: "rc_only"` with the pod
presence recorded), the r84 F1 fold is **real and measured — the family
lock is a fixed path under `corpus/live/`, NOT `$TMPDIR`-scoped, and two
runs of the same ROOT with different TMPDIRs serialize** (§3), and **my
own run of the pinned blob on this host reproduces the landing: 149/149
legs, `failures: {}`, rc=0, teardown clean, under loadavg 91** (§4).
The findings do not change the verdict. The sharpest is that the
fixed-path lock is **ROOT-relative**: the r84-F1 TMPDIR hole is closed,
but two seats running the *frozen-tree* workflow (the wave-B convention)
do not exclude each other (measured, §3.3-C).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| committed-blob pin | `fa5994a0` fixture | blob `e030588c…`, sha256 `5ceba940…`, 26 655 lines; worktree byte-identical | PASS |
| diff shape | insertion-only | 6 hunks; **1758 added / 3 deleted** (`git show --numstat`); the 3 deletions are the wiring lines re-issued with the r86 term inserted (string-verified) | PASS |
| `py_compile` | clean | rc=0 on the pinned blob | PASS |
| committed receipts ×2 | `failures: {}` | run1 `1097d9f1…`, run2 `fe57c1cb…`: all 5 entries, `failures: []`, no `blocked`/`coverage_blocked` | PASS |
| independent law re-derivation | armed law set | **204 checks × 2 committed receipts = 408/408 PASS** (`r86r_audit.py`, receipts-only); pre-fix dev receipt fails 2 (positive control) | PASS |
| caveat rows | as declared | `dump_color_eq.armed == False`, `d_route.armed == False`, `n_format.armed == "rc_only"` in both committed receipts and in the live run | PASS |
| r84 F1 fold | NOT TMPDIR-scoped | resolved r86 path invariant across TMPDIRs, r85 path moves with TMPDIR; **A: same ROOT, two TMPDIRs → waiter blocked 3.52 s**; B (r85 contrast) 0.0002 s; C (cross-ROOT) 0.0001 s — scope limit (F1) | PASS-with-finding |
| live re-run (pinned blob) | green | `20261016T063726014052Z`, 06:36:46→06:37:26Z, loadavg 91.46, `failures: {}`, 149 legs, stderr 0 B, teardown clean | PASS |
| verdict-surface stability | deterministic | run1-vs-run2 = 24 volatile keys; live-vs-run1 = 36, **all 13 extra keys are 1-byte shifts from the 2-digit node id (85 vs 215)** + the calibration-volatile `reset` median (8191.5↔8192.0); **every armed verdict identical** | PASS |
| independent spots | ≥5 shapes | **9 spots / own `r86r_*` namespace** (addressing split, pw-dump surface, pw-cli trichotomy, pw-top split, pw-link lattice, pw-jack shim, metadata laws, set-param refusals, port echo-lie) — all reproduce the encoded law | PASS |
| custody/teardown | zero residue | in-receipt `sinks_gone` true, `own_nodes_after: []`, `meta_keys_gone: true`; post-state: 0 `r86a_`/`r86r_` modules/sinks/metadata keys/procs, defaults unchanged | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r86-reviewer/` (untracked) | PASS |

---

## 1. Findings, ranked

### F1 (medium-low) — the fixed-path lock is ROOT-relative: the TMPDIR hole is closed, but cross-ROOT (frozen-tree) same-family runs are not excluded

`_pwctl_r86_family_lock()` (`:24118-24136`) takes
`ROOT / "live" / "measure_audio-pwctl-r86.lock"` with
`ROOT = Path(__file__).resolve().parents[1]` (`:26`) — i.e. the *corpus
directory of the checkout that is running*. Measured (§3.3-C): a holder
in `tree/corpus/` and a waiter in `tree2/corpus/` with the **same
TMPDIR** take two different lock files — the waiter acquired in
0.0001 s, no exclusion. The wave-B verification seats run `git archive`
frozen trees (this seat, the r85 verifier, the r86 verifier), so this is
the normal case, not a corner. The contrast is explicit: the r85 lock
(`Path(tempfile.gettempdir())/…`) *did* exclude cross-ROOT runs whenever
TMPDIRs matched (the documented wave-B convention), while the r86 lock
does not; the r86 lock in turn survives the r84-F1 defect (different
TMPDIRs, same ROOT — measured A). The fold therefore trades one hole for
another rather than closing both.

Bounded impact (read, not measured): every object name is pid-scoped
(`r86a_ns_<pid>`, `r86arole<pid>`), the DSP tap and tone target the
run's own sink, `own_nodes_after` filters by `r86a_<pid>`, and the
`foreign_r86a_nodes` census is informational — so the sharpest concrete
hazard is a **false failure**, not a false green: `_pwctl_r86_teardown`
(`:24201-24221`) greps the *whole* default store for `r86a_` lines, so a
concurrent sibling's live `r86a_k` key at teardown time fails this run's
`meta_keys_gone`. No committed run and no run of mine took that path
(all three receipts: `meta_keys_gone: true`, `foreign_r86a_nodes: []`).
Fix: key the lock off a fixed *lane* root (the worktree
`corpus/live/` absolute path) instead of the running checkout's ROOT, or
hold both locks.

### F2 (low) — an unavailable lock is silently an unlocked run

`_pwctl_r86_family_lock` returns `None` on `OSError` and the caller
(`:25964`) ignores the return value; there is no witness, no
`coverage_blocked` marker. Measured while calibrating this probe: a
minimal tree whose `corpus/live/` did not exist produced
`fd_returned: false` and the run proceeded unlocked (`lock-probe-firstrun.json`).
A real `git archive fa5994a0` tree *does* contain `corpus/live/` (42 870
tracked files under it), so neither the author's runs nor this seat's run
were affected — the hole is latent (read-only lane, pruned tree,
permissions). Fix: record the lock outcome in the receipt (or fail the
entry) when the lock cannot be taken.

### F3 (low) — two "byte-identical" arms compare only the 700-char stdout preview

`_pwctl_r86_run` stores `stdout = outt[:700]` (`:23952`), and the arms
`dump_id ≡ dump_serial` (`:24437`) and `n_num3 ≡ n_enumformat`
(`:24658`) compare that preview, not the full bytes. A tail-only
difference would pass. The full lengths are recorded
(`stdout_bytes` 11564/11564 and 1128/1128 in the committed pair,
11563/11563 and 1128/1128 in my run), so no false green was taken — the
arm is just looser than the report's "byte-identical" wording. Fix:
compare `stdout_bytes` (and/or full text) as well.

### F4 (low) — conditional legs can vanish without a coverage marker

`l_props` (`:24600-24603`) is skipped when the self-loop census reader
returns nothing (`lid is None` → `continue`), and in the tools entry
`lk_d_port`/`lk_d_link` (`:25291`) and `lk_junkprops_unlink` (`:25307`)
are likewise conditional on the census — with no failure and no
`coverage_blocked` entry. Same class as r85-F4. All three receipts
contain the legs (`l_props` class `pwcli_not_impl`, `lk_d_port` rc=255,
`lk_d_link` rc=0, `lk_junkprops_unlink` rc=0), so no false green was
taken.

### F5 (nits) — reported size and line ranges

- The commit message, `r86-author.md` and the wave task all say
  **+1761** lines; `git show --numstat fa5994a0` is **1758 added / 3
  deleted**. The +3 is the three replaced wiring lines counted as
  additions (1758 + 3). The landing itself is exactly as described.
- The author report's wiring/mode/suffix line ranges
  (`~L25568/25576/25934–25964`, `~L26615/26635`) are ~10 lines low
  against the committed blob (actual: 25578/25586/25944–25974,
  26625/26645); the family-block range `~L23730–L25500` is exact at the
  head (the added block is 23730–25451, whose last code line — the tools
  entry's `return` — is 25449).

### F6 (nit) — `cli_pipe`'s SIGKILL half is harness-tautological

`cli_pipe` (`:25355-25359`) arms `killed_at_bound and signal ==
"SIGKILL"`; the SIGKILL is sent by the harness at the bound, so the
discriminating half is `killed_at_bound` (pw-cli did not exit within
4 s). Not a false-green risk.

### F7 (observation) — run1's subject-0 baseline carried a transient foreign default

run1's `subj0_keys` include `default.audio.source` and its
`oracle_at_start.source_meta` is `r85v_2658932_vsrc` (the r85 verifier
seat's virtual source); run2 and my run show the clean baseline
(`default.audio.sink`, `default.configured.audio.sink`,
`default.configured.audio.source`). The row is recorded, never armed,
and the family itself never writes subject 0 — the only subject-0 legs
are a read (`:25091`) and `-m 0` filters (`:25087`). Also checked: the
r86 block contains **no** `set-default-*` call; the only
`pactl set-default-sink` in the file belongs to the old r78 playback
family (`:7088`) and is not reachable via `--probe-pwctl-r86`.

---

## 2. Independent re-derivation of the armed verdicts (receipts only)

`corpus/live/r86-reviewer/r86r_audit.py` (sha256 `1367652631f9…`)
re-implements every r86 arm from the receipt data alone (no fixture
code, no host) and checks each receipt: **204 checks** covering, per
entry, the addressing split (`ls <serial>` resolves, `ls <id>` does not,
`info <id>` resolves, `info <serial>`/`enum-params <serial>` rc0
unknown-global), the class census (typed rows per class;
`Bogus`/`node`/`Session` byte-empty), the pw-dump surface
(`<id>≡<serial>` previews + zero-byte refusals + the `-C never`
positional trap + joined `-Cnever` + the self-Client law with disjoint
fresh serials), `info all`/`list-vars`/`list-remotes`, the real nonzero
remote refusal, the metadata silent-empty, the self-loop →
`info <link>` → `destroy <link>` census; the params matrix (pod dumps,
pod-absence rows, `n_format` rc-only, remote-ENOENT set, `d_route`
record-only, `3 ≡ EnumFormat`, unknown-param/unknown-global/not-impl
classes, `None`/empty-pod/stripped-key/wrong-type/`res:-95`/Port
echo-lie/usage refusals and the `minQuantum` unchanged check); the DSP
windows (solo envelope, cv25/cv50/mute/reset/dead/pa25/pa100 envelopes,
the cube-root read-back, dead-key `pactl == 100`, `Float 0.25` in the
store, 25/100 read-backs, all five write rc0); the metadata laws (store
census equality, strict-subset gap, echo-vs-persist, full replace,
typed value, absent-key silence, delete semantics, subject wipe,
`-m`/`-m 0` kill-bounded subject filters, read-only subject-0); the
process surfaces (top batch/`-n 0`/batch-TERM clean, TUI-TERM SIGABRT +
`remove_from_poll`, TUI-KILL SIGKILL, pw-cli /dev/null abort, quit,
pipe hang, the pw-jack env table, the pw-link rc=255 lattice and the
junk-props acceptance); and every teardown witness (unload
`verified_index == captured`, `recycled False`, `field/value`,
`sinks_gone`, `own_nodes_after`, `meta_keys_gone`).

| receipt | checks | result |
| --- | --- | --- |
| author run1 `20261016T063006268243Z` | 204 | **204 pass / 0 fail** |
| author run2 `20261016T063043717745Z` | 204 | **204 pass / 0 fail** |
| reviewer live run `20261016T063726014052Z` | 204 | **204 pass / 0 fail** |
| *positive control*: pre-fix dev run `20261016T062922907396Z` | 204 | **202 pass / 2 fail** — `n_format` armed rc_only (absent in the pre-fix bytes) and the entry failure `n_format: rc=0 pod=True — the pod-absence law fails`, exactly the correction the author report discloses |

Cross-run volatile surface (calibrated run1-vs-run2, 24 keys): the
foreign-graph byte counts (`ls_*`, `info_all`, `dump_color_join`),
metadata store byte lengths, `subj0_keys` (F7), the `reset` median
(8191.5↔8192.0), pid/ns/serial/id fields and timing. **Every armed
verdict is identical across the three runs.**

---

## 3. The r84 F1 fold — fixed-path lock, verified NOT TMPDIR-scoped

### 3.1 Code

- `_pwctl_r86_family_lock` (`:24118-24136`): `path = ROOT / "live" /
  "measure_audio-pwctl-r86.lock"`, `flock(LOCK_EX)`, witness
  `pid/ns/role`; docstring: "a $TMPDIR-scoped lock lets two same-family
  runs on different TMPDIRs race … so this lock lives under corpus/live/
  (outside $TMPDIR entirely)". **No `tempfile`/`TMPDIR` reference.**
- `_pactlmon_r85_family_lock` (`:22318-22319`) and
  `_alsapw_r84_family_lock` (`:19846`): `Path(tempfile.gettempdir()) / …`
  — the TMPDIR-scoped contrast.

### 3.2 Resolved paths (monkeypatched `os.open`, nothing created/locked)

`labrat/r86r_lock_probe.py` (`resolve` subcommand) under
`TMPDIR=~/Projects/shokunin/tmp` (tmp1) and
`TMPDIR=~/Projects/shokunin/tmp/r86r-alt-tmp` (tmp2):

| module ROOT | lockfn | tmp1 path | tmp2 path |
| --- | --- | --- | --- |
| `tree/corpus` | r86 | `…/tree/corpus/live/measure_audio-pwctl-r86.lock` | **same** |
| `tree2/corpus` | r86 | `…/tree2/corpus/live/measure_audio-pwctl-r86.lock` | **same** |
| `tree/corpus` | r85 | `~/Projects/shokunin/tmp/measure_audio-pactlmon-r85.lock` | `…/r86r-alt-tmp/measure_audio-pactlmon-r85.lock` |

### 3.3 Executed flock serialization (`labrat/lock-probe.json`)

| exp | lock | ROOT holder → waiter | TMPDIR holder → waiter | waiter waited | reading |
| --- | --- | --- | --- | --- | --- |
| A | r86 | tree1 → tree1 | tmp1 → tmp2 | **3.52 s** (holder held 5 s, waiter started +1.5 s) | **serialized — the fold works** |
| B | r85 | tree1 → tree1 | tmp1 → tmp2 | 0.0002 s | not serialized (the r84-F1 defect, as contrast) |
| C | r86 | tree1 → tree2 | tmp1 → tmp1 | 0.0001 s (real lock taken, fd 3) | not serialized — **ROOT scope limit (F1)** |

The first probe revision also realized the F2 case: with `tree2` pruned
of `corpus/live/`, `_pwctl_r86_family_lock` returned `None` (fd null) and
the run proceeded unlocked. That artifact (`lock-probe-firstrun.json`) is
kept for the record; the recorded `lock-probe.json` is the corrected
revision (two independent realizations of A/B/C agree).

---

## 4. Behavioral re-run of the pinned blob (this host)

`tree/corpus/fixtures/measure_audio.py --probe-pwctl-r86`,
`TMPDIR=~/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`, bounded
`timeout 2700`. Window **2026-10-16 06:36:46 → 06:37:26Z** (local
03:36:46→03:37:26), entry loadavg **91.46/78.03/64.27**. Receipt
`tree/corpus/live/runs/20261016T063726014052Z-pwctl-r86/measurements.json`
(copy `runs/r86r1/measurements.json`, sha256 `9a31073e6d…`); stdout
`{"failures": {}}`, stderr **0 B**.

**Result: 149 legs (34/43/16/22/34), `failures: {}` on all five entries,
no `blocked`/`coverage_blocked`, every teardown witness clean**
(`sinks_gone` true, `own_nodes_after: []`, `meta_keys_gone: true`,
unload `verified_index == captured == 536870922`, `recycled: false`).
Entry census: `host_is_quiet: true`, `fixture_runs: 0`,
`foreign_r86a_nodes: []`.

Realizations vs the committed pair: ns `r86a_ns_2912789`, node id **85**
(2 digits), serial 244225; DSP tap link validated pre-player
(4 edges), player attached (`sink` 244355), windows solo **8192.0**,
cv25 **2048.0** (exact linear), cv50 **4096.0**, mute **0.0**, reset
**8192.0**, dead **8192.0**, pa25 **128.0** (exact cubic), pa100
**8192.0**; pactl read-backs **63 % / 79 % / 100 % / 25 % / 100 %**;
`n_format` rc0 with pod present (863 B — the negotiation-tracked side);
`p_format` pod-absent with the racy `res:-5` text recorded;
`dump_color_eq` rc=255 `Unknown color: =never` (the author's boot side,
recorded only); metadata census 9 stores = `ls Metadata` 9, pw-dump
strict subset `{31,34,36,39}`; subject-0 baseline clean (F7).

Surface diff (`r86r_surface.py`, `surface-diff.json`): run1-vs-run2 = 24
volatile keys; live-vs-run1 = 36. The two sets differ by exactly 14
keys: **13 live-only keys, all of them exactly 1-byte `stdout_bytes`
shifts** caused by the 2-digit node id 85 vs 3-digit 215 (e.g. `dump_id`
11564→11563, `info_id` 1076→1075, each `m_*` 81→80) with identical line
counts — and 1 calibration-only key, `__regions` (run1 `reset` 8192.0 vs
run2 8191.5; my run matches run1). **No armed verdict differs.**

Co-tenancy (`cotenancy-at-entry.txt`, `residue-census.txt`): wave-B
siblings were live all window (`r86-critic`, `r86-scribe`,
`r86-simplifier`, `r86-verifier`); the r86-verifier's own frozen-tree
runs stamped 03:34:59 and 03:35:29 **before** this window; the worktree
lock witness (`pid=2808000`, mtime 03:34:30) was **not touched** by this
seat (read-only flock probe used the tree lock only), and this seat's
tree lock carries `pid=2912789` (03:36:59). Post-run: 0 `r86a_`/`r86r_`
modules, sinks, metadata keys or processes; default sink/source
unchanged; worktree fixture blob still `e030588c…`.

---

## 5. Independent spots (own `r86r_*` namespace)

`spot/r86r_spots.py` (sha256 `f74c9ca2f5…`, `spots.json`) and one
inline port spot (`spot/port-spot.json`); every own module unloaded
name-verified (`sink_gone: true`); crash-class spots ran with
`RLIMIT_CORE=0`. Window 03:38:03→03:38:11, loadavg 101.4.

| # | spot | measured |
| --- | --- | --- |
| S1 | addressing split (own sink, id 85 / serial 244497) | `ls <serial>` rc0 + the node; `ls <id>` 0 B rc0; `info <id>` rc0 + `id: 85`; `info <serial>` rc0 `unknown global` |
| S2 | pw-dump surface | `99999`/`bogus` 0 B rc0; `-C never` **0 B rc0** (positional trap); `-Cnever` 243 628 B rc0; `-C=never` rc255 `Unknown color: =never` (recorded side) |
| S3 | pw-cli stdin | `/dev/null` rc −6 (SIGABRT) + `remove_from_poll`; `quit` rc0; pipe stdin killed at the 4 s bound |
| S4 | pw-top split | batch + TERM rc0, no assertion; TUI + TERM SIGABRT + assertion |
| S5 | pw-link lattice | create rc0; duplicate **rc255 `File exists`**; bare/`-I`/`-v` rc255; `-d <link-id>` rc0 and the link is gone |
| S6 | pw-jack shim | `-p 512` → `Q=512/48000`; `-s 44100 -p 256` → `256/44100`; `-s` alone → unset; `-v`/`-vv`/preset-4+`-v` → D=3/4/5; bogus payload rc127 |
| S7 | metadata laws | dead subject 99997: `set property:` echo, **0** `update:` rows; `-n <bogus>` 0 B rc0; subject-0 read rc0 `Found "default"` (keys recorded) |
| S8 | set-param refusals | `garbage` → `None` echo rc0; `EnumFormat` rc0 + `res:-95` |
| S9 | port echo-lie (own port 196) | `set-param … Latency {minQuantum: 2.0}` rc0 + pod echo `Float 2.000000` **+ local `Error: "set-param not implemented on object 196 type:PipeWire:Interface:Port"`**; re-enum still `Float 0.000000`; `pw-link -d <port-id>` rc255 |

---

## 6. Caveat rows and encoded boundary corrections

The three declared caveats are encoded exactly as declared and were
re-verified in code, in both committed receipts and in the live run:
`dump_color_eq` `armed: False` (rc255/`Unknown color` on this boot, 0 B
on the boundary boot — data only), `d_route` `armed: False` (0 B
recorded), `n_format` `armed: "rc_only"` with `has_pod` recorded
(`True` post-negotiation in all three receipts — the boundary's
correction to the scout's pod-absence arm). The other boundary
corrections are likewise encoded and reproduce in my run: `pw-cli
</dev/null>` SIGABRT (not clean EOF), pw-link rc=255 (not rc0), `-I`/`-v`
as modifiers, `pw-dump -C never` positional trap, the port `set-param`
echo-lie (local not-implemented print, not "silently dropped"), the
`res:-95` EnumFormat refusal, the pw-top batch-vs-TUI signal split, the
dead-subject echo-lies law, the metadata census gap armed as a strict
subset, and no hash arm for the falsified "byte-stable modulo self".
Subject 0 is read-only (one read leg + `-m 0` filter); no
`set-default-*` anywhere in the r86 block.

---

## 7. Evidence index (all under `corpus/live/r86-reviewer/`, manifest.txt)

| artifact | content |
| --- | --- |
| `measure_audio_fa5994a0.py`, `pins.txt` | pinned committed blob (blob/sha256/numstat/worktree-identity pins) |
| `tree/` | pinned minimal tree (committed blob + `build_artifacts.py` + artifacts copy) — the live run's receipt lives under `tree/corpus/live/runs/20261016T063726014052Z-pwctl-r86/` |
| `r86r_audit.py`, `audit-checks.json`, `audit-live-run.json` | 204-check receipt-only re-derivation (committed pair + live run) |
| `r86r_surface.py`, `surface-diff.json` | normalized verdict-surface calibration + live diff |
| `labrat/r86r_lock_probe.py`, `r86r_lock_driver.py`, `lock-probe.json`, `witness-*.json`, `lock-probe-firstrun.json` | r84-F1 fold probe: resolved paths + A/B/C flock serialization (+ the pruned-ROOT F2 realization) |
| `runs/commands.log`, `runs/r86r1.stdout.json`, `runs/r86r1.stderr.log`, `runs/r86r1/measurements.json` | live run window, stdout/stderr, receipt copy |
| `spot/r86r_spots.py`, `spots.json`, `spots.out.txt`, `spot/port-spot.json` | 9 independent spots in the `r86r_*` namespace |
| `cotenancy-at-entry.txt`, `residue-census.txt` | lock witnesses / process + audio census at entry, post-run residue and default state |
| `manifest.txt` | sha256 of every receipt file above |

Commit-side pins: `fa5994a0` (author; fixture blob unchanged at current
HEAD), receipts sha256 `1097d9f1…` (run1) / `fe57c1cb…` (run2), author
report `a128b993…` (149 lines, +149/−0). The dispatched labrat returned
UNTESTED-empirical / CONFIRMED-by-source with zero side effects.

---

## 8. Remaining risks / blockers

- **Blockers: none.** The landing is green, reproduced, and its armed
  laws survive an independent re-derivation.
- F1 is the one finding with a measured gap behind it: wave-B seats on
  frozen trees are not excluded from each other; the sharpest concrete
  consequence is a possible `meta_keys_gone` false failure (and node
  census noise), not a false green. Fix is a lane-level lock root or a
  second lock.
- F2/F3/F4 are latent loosenesses: no committed or live run took the
  wrong path, but each admits one silently.
- Receipts still carry no source-revision hash (family-wide, unchanged
  since r84/r85); the evidence chain rests on the committed-blob pin,
  which this review verified.
- The crash-class rows (`pw-top` TUI TERM, `pw-cli </dev/null`) file no
  core from this seat (RLIMIT_CORE=0 on every such leg); the host
  coredump counter (5 373 entries) is not attributable to any seat and
  is not used as evidence.
