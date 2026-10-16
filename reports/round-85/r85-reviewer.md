# r85 REVIEWER — wave-B gate on committed `2a49d540`

**Seat: REVIEWER (executor-class, leaf, frozen `probeParent`).** Lane
`/home/vgpnk/Projects/shokunin/audio-shokunin`. Scope **only** the r85
landing — `git show 2a49d540 -- corpus/fixtures/measure_audio.py`
(**+2178/−3**, committed blob `0b49d5540dfce9a8dec3b9c41d8e756b22d95ba9`,
sha256 `714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2`,
24 900 lines) plus the two committed receipts. Everything below was
measured against a **pinned copy of the committed blob**
(`corpus/live/r85-reviewer/measure_audio_2a49d540.py` — `git hash-object`
== the committed blob; the working-tree `corpus/fixtures/measure_audio.py`
is byte-identical to it, `git status --porcelain` on that path is empty)
and a pinned minimal tree (`corpus/live/r85-reviewer/tree/`, blob + the
committed `build_artifacts.py` + a copy of `corpus/artifacts/`) so the
fixture's own receipt lands inside this seat's receipt dir. **Zero tracked
writes; nothing committed; no `set-default-*`; no `r85a_*` object of the
co-tenant seats was touched; all reviewer-created modules were unloaded
name-verified (final census: `residue-census.txt` — no `r85r_*`/numeric
probe module or sink, default sink still `…HiFi__SPDIF__sink.29`).**
`PYTHONDONTWRITEBYTECODE=1` was set on every run (the one pre-existing
tracked dirt, `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`,
was already ` M` at entry; its last rewrite (03:20:10 local) coincides with
the sibling seats' `importlib` replay scripts that import the repo fixture
— e.g. `corpus/live/r85-critic/unit-replay.py` — not with this seat, whose
runs used a pinned tree and left no `__pycache__` under
`corpus/live/r85-reviewer/`).

The frozen `probeParent` seat dispatched **one** `ufo-labrat`
(`agent f639051c`, bounded cdup either-way probe) — the child returned
**BLOCKED/INCONCLUSIVE: its seat had no shell/exec tool bound**, ran
nothing and wrote nothing (verbatim in
`corpus/live/r85-reviewer/labrat/labrat-report.md`). No second probe was
dispatched (the one-probe cap); the same bounded probe was then executed
**in-seat** (`labrat/r85r_cdup_probe.py`, §3.3) and a second in-seat
reproduction (`labrat/numeric_node_repro.py`, F1) was run.

---

## 0. Verdict

**PASS with findings.** The r85 family is insertion-only, correctly wired
(3 replaced wiring lines: mutex-sum, `mode`, `suffix`; plus
`add_argument` + 5 dispatch lines), and its 5 entries / **87 legs**
reproduce **0 failures** in both committed receipts; every armed verdict I
re-derived independently from the receipt data alone reproduces exactly
(**278/278 checks**, §2), the boundary corrections are encoded where the
report says they are (object.id/serial/source-name binds, never-monitor
sink-name, monotonic serials vs recycled module index, folded loss law,
self-destruct ladder, tap-validation + same-run solo reference), and **my
own run of the pinned blob on this host reproduces the committed landing:
87 legs, `failures: {}`, rc=0, teardown clean, in a single-tenant
window** (§3). The three host-bimodal realizations are admitted both ways
with sharp failing shapes — verified in code, in the receipts, and (for
cdup) by an in-seat probe that **realized both sides on this host** (§3.3)
— with one looseness in the cdup classifier noted below. The findings do
not change the verdict; the sharpest is a **measured run-abort**: a node
whose `node.name` is purely numeric (which this family itself creates in
the collision leg) makes the fixture's inherited node-name readers raise
`TypeError` — reproduced in isolation on the committed blob and observed
live in a co-tenant wave-B run (F1).

---

## 1. Findings, ranked

### F1 (medium) — a purely numeric `node.name` aborts the run: the inherited readers assume strings, and the r85 family itself plants numeric names

`pw-dump` emits a node whose `node.name` is purely numeric as a JSON
**int**, and three readers the r85 family relies on assume a string:

- `_playback_r78_node_names()` (`measure_audio.py:6147-6158`) —
  `sorted({…"node.name"…} - {None})` at `:6153` → `TypeError: '<' not
  supported between instances of 'int' and 'str'`;
- `_alsapw_r84_cands()` (`:19135-19140`) — `any(s in n["name"] …)` at
  `:19140` → `TypeError: argument of type 'int' is not a container or
  iterable`;
- `_pactlmon_r85_node()` (`:21816-21822`) — `n.get("name") == name` never
  matches a numeric name → returns `None` **silently** (my probe's own
  first helper hit exactly this, which is why its first attempt reported
  "digits-named sink never enumerated" — the node existed; the int/str
  compare failed).

Measured, in isolation, on the committed blob
(`corpus/live/r85-reviewer/labrat/numeric-node-repro.json`): load one
null sink `sink_name=123456789` → its `node.name` prop is the **int**
`123456789`; `_playback_r78_node_names()` → TypeError;
`_alsapw_r84_cands(graph, "alsa_playback.aplay")` → TypeError;
`_pactlmon_r85_node(graph, "123456789")` → `found: false` (no raise).

Why it is an r85 finding: the **collision leg creates such a node by
design** (`legs["cdup_load"] = _pwcat_r83_ns_load(str(ser_a))`,
`:22559`), and the family calls `_playback_r78_node_names()` from every
entry's teardown (`:22391`) and from every aplay leg (`:19482`).
Single-tenant runs are safe only because the digits sink is unloaded
before the next reader call; if that name-verified unload skips
(`_pactlmon_r85_module_index` returns `None` on a transient listing
failure → `unloads[…].skipped = not_listed`; the `sinks_gone` witness
would then fail, but the module stays loaded and the **next entry aborts
the whole run before any receipt is written**) — and any *concurrent*
numeric-named node (a sibling seat's collision leg with a different
`TMPDIR`, the boundary's own `r85b` collision sink, a user sink named
`12345`) does the same.

Observed live: the co-tenant `r85-verifier` seat's `r85v2` (window
06:22:22→06:23:07Z) crashed exactly this way —
`corpus/live/r85-verifier/runs/r85v2.stderr.log`: first
`TypeError: argument of type 'int' is not a container or iterable` in
`_alsapw_r84_cands` during `env_serial`, then
`TypeError: '<' not supported between instances of 'int' and 'str'` in
`_playback_r78_node_names` during the same entry's teardown; the run
produced **no receipt**. **Attribution (disclosed):** my own in-seat
probing left numeric-named sinks alive inside that window (a crashed
one-liner left `sink_name=777888999` loaded from ~06:23:0xZ, and the
digits-named `239758` was alive 06:22:47–06:22:52Z) — so this is not a
defect the landing inflicts on itself in a quiet single-tenant run, but it
is a measured, reproducible abort of this family's runs under the
co-tenancy the wave actually has (the family lock is TMPDIR-scoped, the
r84-F1 consensus finding). Fix direction: `str()`-coerce `node.name` in
those three readers (and treat a foreign numeric node as a hard
precondition/abort, never a crash).

### F2 (medium-low) — `sd_prop`'s "must land on the default monitor" arm is conditional: dead trap + no links passes and is labelled as a fallback

The prop-form self-destruct leg (`:23545-23575`) arms only the link shapes:

- non-`monitor_*` links → failure;
- links that never reach the default sink → failure;
- **no links + module alive → failure** (`"neither bound nor dead"`);
- **no links + module gone → PASS**, realization
  `"bind_killed_then_default"` (`l["realization"]` is assigned from
  `sd_gone` alone, `:23558-23560`).

A run in which the prop record's transient bind kills the trap and the
record then **never reaches the default monitor** therefore greens and is
labelled as if the default fallback happened. The author's report states
the arm as "links must land on the default monitor" — stronger than the
code enforces. Both committed receipts and my live run do realize the
default-monitor links (`…SPDIF__sink.29:monitor_FL/FR`, verified in all
three), so **no false-green was taken**; the hole is latent. Fix: when
`sd_gone` is true, require the default-monitor post-link (or a recorded
`stalled_after_bind_kill` realization that is explicitly non-green).

### F3 (low) — the capture-lattice arms police port *direction*, not the target node's identity

- `t_prop_sinkname` (`:23504-23509`) accepts **any** `monitor_*` — the
  boundary law is the named sink's *own* monitor. The fixture's own
  `cap_loss_prop` leg proves the prop form can land on a **foreign**
  monitor (the default sink, `:23442-23454`), so the shape the arm would
  accept is real, not hypothetical.
- `t_srcname` / `t_srcserial` / `t_srcid` (`:23491-23503`) accept **any**
  `capture_*` — not specifically the named source's ports.
- `cdup_cap` (`:22706-22737`): foreign **monitor** binds fail
  (`foreign_monitor`), but a foreign **non-monitor** bind is absorbed as
  `"name_shadow_bound"` (`:22722-22725`) — the label asserts name-first
  resolution without measuring it. Note the wave-B sibling commit messages
  diverge on exactly this point (`8ae131e6` critic: "either-way arms
  proven 27/27"; `972202bf` scribe: "ADJ-3: cdup_cap NOT armed both ways
  (foreign bind absorbed)"); my independent reading of the committed blob
  is: **foreign monitor binds fail; foreign non-monitor binds pass as
  `name_shadow_bound`** — the scribe's concern is realized for the
  non-monitor case only.

All three runs realize the strong form (source binds on `r85a_vsrc_*`,
prop-sinkname on `r85a_ns2_*`), so no false-green was taken. Fix: add the
`out_node` identity to the same assertions that check the port prefix.

### F4 (low) — the whole move/collision sub-lattice can vanish silently

`if ia is not None:` (`:22537`) guards every `mv_*`/`cdup_*` leg, and
`if dup.get("module_id") is not None:` (`:22564`) guards
`cdup_move`/`cdup_cap`; when the stream never attaches or the numeric-name
sink fails its enumeration gate, the legs are simply absent — **no
failure, no `coverage_blocked` entry** (all three green receipts have
`coverage_blocked: None`). A green receipt can therefore be missing the
collision law entirely (the very claim the boundary §3.5 closed). Fix:
record a `coverage_blocked` marker (or fail) on either skip, as the
`_pactlmon_r85_block` path already does for missing tools/loads.

### F5 (low) — the `0 = live default` arm is only conditionally discriminating

`g_zero` compares the first `N%` of `pactl get-sink-volume 0` with
`@DEFAULT_SINK@`'s (`:22632-22639`). On this host it discriminates because
the live default is at 40 % while the probe sink is at 100 %
(`g_zero`/`g_defsink` 26214/40 %, `g_name` 65536/100 %) — but if the
default sink happened to share the probe sink's volume, a `0` resolving to
the probe sink (or any same-volume sink) would green. Fix: compare the
full row (raw counts / base volume) and/or assert the two rows differ
before treating equality as evidence.

### F6 (nits)

- `sers` (`:22738`) is computed and never used; the serial arm then runs
  `serials != sorted(serials)` on the raw list, so a `None` serial raises
  `TypeError` (entry abort) instead of a named failure — robustness only
  (loud, not a false-green).
- The family header comment claims "leading/trailing spaces … all parse"
  (`:21606-21608`), but only the leading-space leg exists (`g_leadspace`);
  the boundary's trailing-space row has no leg.
- Receipts do not self-certify the source revision (no blob/sha field) —
  family-wide (r84 receipts are the same); the identical-bytes claim rests
  on the committed blob hash + leg-shape match, which I verified.

---

## 2. Independent re-derivation of the armed verdicts (receipts only)

`corpus/live/r85-reviewer/r85r_audit.py` (sha256
`0d81e7de296b92b99840fcbf51c94412cd5628adfb50cbad7cac9bd4a21dfabc`)
re-implements every r85 arm from the receipt data alone (no fixture code)
and checks both committed receipts: **278 checks, 278 pass, 0 fail**
(`audit-checks.json`). It covers, per entry: the address lattice
(rc/class/volume-row equality/parse edges/`g_lead0` `armed=false`),
pw-cli inversion, move name/serial/bogus, the collision move, the cdup
realization **re-derived from raw link shapes**, serial monotonicity +
module-index recycle, tap-link validation for all 6 mix legs, solo
reference window + zero bleed, mix2 full-amplitude/bleed/4-links-2-ports,
the mixdup/mixdelay/mixinv ratio→label mappings and the ≤2.05 linear
bound, mixclip rail/spur, aplay env publish+consumer evidence (including
the props-win discriminator and both silent-default fallbacks), the
capture baseline/lattice/loss/self-destruct/latebind arms, the negctl unit
table (`got == expect` for all 13 rows; I also re-read the classifier
chain by hand: each canned string maps to the intended class in
r85-local → r84 → shared order), the live no-error controls, and every
teardown witness (`own_nodes_after == []`, `sinks_gone`/`sources_gone`
all true, `failures == []`).

Cross-run volatile surface (both committed receipts, documented): only
the phase/coherence realizations move — `mixdup` `coherent_2x` (2.0) ↔
`partial` (0.259), `mixdelay` `partial` (0.226) ↔ `cancelled` (0.025),
`mixinv` `slipped` 1.87 ↔ 1.85, `mixclip` rail 0.2321 ↔ 0.2325 / spur
1921.5 ↔ 1921.3, `cap_loss` `grew_content` 2048 ↔ `froze`, plus
pid/tmp/serial/id/timing fields and the pid-offset tag-tone pair
(`997/1500` ↔ `1208/1711`). Every *armed* verdict is identical across the
two runs.

## 3. Behavioral re-run of the pinned blob (this host)

### 3.1 Run

`corpus/live/r85-reviewer/tree/corpus/fixtures/measure_audio.py
--probe-pactlmon-r85`, `TMPDIR=~/Projects/shokunin/tmp`, bounded
`timeout 2700`, `PYTHONDONTWRITEBYTECODE=1`; canon receipt
`…/r85-reviewer/tree/corpus/live/runs/20261016T062221991868Z-pactlmon-r85/measurements.json`,
copy `corpus/live/r85-reviewer/runs/r85r1/measurements.json` (sha256
`20eda837241a8e1a2ff04f654d629737f5b43e718d461027fe0c9f79a85c01f0`).
Window 06:19:07→06:22:22Z, loadavg ≈50. **Result: `failures: {}` for all
five entries, 87 legs (40/7/6/17/17), rc=0, every teardown witness clean,
no `r85a_*` residue.** The entry censuses show **no foreign audio client**
(`pw_play`/`pw_record`/`parec`/… all 0; only `fixture_runs: 1` — the
lock-blocked sibling process, which was running nothing). My audit passes
**278/278** on this receipt too.

Co-tenancy (recorded, `cotenancy-at-entry.txt`, `runs/commands.log`): the
`r85-verifier` seat's `r85v1` held the family lock when I entered; my run
waited **~88 s** in `locks_lock_inode_wait`, then held the lock while the
verifier's `r85v2` queued behind me (lock file carried
`pid=2599248`). The **TMPDIR-scoped lock worked** because every seat used
the lane TMPDIR — the positive control for the r84-F1 finding. The
verifier's `r85v1` (single-tenant, pre-my-probes) was green
(`failures: {}`); its `r85v2` is the F1 crash above.

### 3.2 Realizations (live run vs the committed pair)

Identical to the committed pair on every armed verdict: serials
238462→238476→238490 with module index 536870916 recycled ×3; solo
`l_a=r_b=8190.7/8190.8`, bleed 0; mix2 all four tones 8190.7, bleed 0,
4 links → 2 `playback_*` ports; `mixdup` 2.0 `coherent_2x`; `mixdelay`
0.226 `partial`; `mixinv` 1.869 `slipped`; `mixclip` peak 32768, rail
0.2321, spur 1921.5; `t_sinkname` `bound_source` (`capture_FL/FR`,
never a monitor); `cap_loss` **froze 0/0** (the third side of the folded
falsification, recorded not armed); `cap_loss_prop` → default monitor;
`sd_record`/`sd_parec` 0.08/0.09 s; `sd_prop`
`bind_killed_then_default` with default-monitor links; `latebind`
`late_bound` on the late source's own `capture_*`.
**`g_lead0` realized the OTHER side of the boundary-bimodal
`0<digits>` row on this host (`rc=0`, no error class, vs `rc=1
pa_get_info_noent` in both committed runs) and the run did not fail —
`armed=False` is exactly right.**

### 3.3 Either-way pinning of the three host-bimodal realizations

| realization | author side (committed + my run) | boundary side | armed admission | sharp failing shape |
|---|---|---|---|---|
| `latebind` | `late_bound` (links on `r85a_late_*:capture_*`) | `stalled` (no link, alive) | both + `refused` | any link not on the late source's own `capture_*` → `foreign_bind` fail (`:23592-23608`) |
| `cdup_cap` | `serial_monitor_bypass` (links `r85a_ns_*:monitor_*`) | `refused`/`stalled` (no link) | both + `name_shadow_bound` | monitor links not on the serial holder → `foreign_monitor` fail; `other` fail (`:22719-22737`); foreign **non-monitor** links pass (F3) |
| `sd_prop` | `bind_killed_then_default` + default-monitor links | `clean_default_fallback` | both | non-monitor links fail; links off the default fail; **no links + dead trap passes (F2)** |

The `cdup` either-way claim is not just read from the code: the in-seat
probe (`labrat/r85r_cdup_probe.py`, `labrat/cdup-probe.json`) loaded two
`r85r_*` sinks plus a sink literally **named with the holder's serial**
(`240353`), and measured both sides on this host in one window —
**(a)** holder alive: `--target 240353` linked
`r85r_a_2623545:monitor_FL/FR` (serial-first, the author's realization);
**(b)** holder unloaded, digits-named sink alive: the same target linked
**nothing** (44 B, rc=1, stderr `no target node available` — the
"refused" side, never the digits sink's own monitor). The dispatched
labrat could not run this (no exec tool); the probe was executed in-seat
instead, and every `r85r_*` module was unloaded name-verified (residue
`[]`).

## 4. Evidence index (all under `corpus/live/r85-reviewer/`)

| artifact | content |
|---|---|
| `measure_audio_2a49d540.py` | pinned committed blob (hash-object == committed) |
| `tree/` | pinned minimal tree (blob + build_artifacts + artifacts copy) |
| `r85r_audit.py`, `audit-checks.json`, `audit-live-run.json` | 278-check re-derivation (committed receipts + live run) |
| `runs/commands.log`, `runs/r85r1.stdout.json`, `runs/r85r1/measurements.json` | live run window + receipt copy |
| `cotenancy-at-entry.txt`, `residue-census.txt` | lock/co-tenancy census, final residue/default-sink census |
| `labrat/labrat-report.md` | dispatched labrat: BLOCKED (no exec tool), nothing run/written |
| `labrat/r85r_cdup_probe.py`, `labrat/cdup-probe.json` | in-seat cdup either-way probe (both sides realized) |
| `labrat/numeric_node_repro.py`, `labrat/numeric-node-repro.json` | F1 isolation repro on the committed blob |
| `labrat/numeric_name_check.py`, `labrat/window.txt` | numeric-name enumeration check + probe windows |

Commit-side pins: `2a49d540` (author, fixture blob unchanged at current
HEAD `972202bf`), receipts sha256 `69a96ad6…` (run1) / `98267a0f…`
(run2), report `5c4b8d62…`.

## 5. Remaining risks / blockers

- **Blockers: none.** The review is complete; the landing is green and
  reproduced.
- F1 is the one finding with a live run-abort behind it; it needs a
  co-tenant numeric-named node (or a leaked digits sink). Its fix is a
  three-line `str()` coercion in readers the r85 change inherits, plus a
  precondition on foreign numeric nodes.
- F2/F3/F4/F5 are latent arm loosenesses: no committed or live run took
  the false-green path, but each admits a wrong shape silently.
- The `0<digits>` pactl row and the freeze-vs-zeros post-loss shape stay
  record-only (both sides realized across the three runs — correct
  handling); the `mixdup`/`mixdelay` "partial" label conflates a dead
  second stream (ratio ≈1) with quantum misalignment, and `mixinv`
  slipped on all three runs (the boundary's cancellation law did not
  reproduce here) — all recorded, none armed.
- Receipts carry no source-revision hash (family-wide); evidence chain
  rests on the committed blob pin, which this review verified.
