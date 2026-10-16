# r85 critic — wave-B gate on committed `2a49d540`

Seat: `ufo-executor` (critic duties as assigned by
`.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r85-critic.md`).
**Committed tree only** (`2a49d540`), zero tracked writes, nothing committed.
Receipts: `corpus/live/r85-critic/` (+ `MANIFEST.txt` with shas + commands).

**Verdict: ADMIT-with-findings.** No false-green was found in the committed
receipts, the three host-bimodal realizations are genuinely pinned
either-way, and every law named in the task is armed. F1–F3 are latent
absorption channels (arms that pass on a shape the law does not intend);
F4–F10 are low/hygiene/inherited. Nothing here is a shipping decision.

---

## 0. Method (what was actually executed)

| check | evidence |
|---|---|
| commit custody + diff shape | `git show --numstat/-- 2a49d540`; sha256 of the committed blob |
| receipt census (legs, failures, realizations, teardown) | `legs-summary.txt`, `receipt-keyvalues.txt`, `receipt-mix.txt`, `receipt-aplayenv.txt`, `receipt-capture.txt` |
| pure-helper replay (classifier table, post-loss flush boundary, rail witness, leg counts) | `unit-replay.py` → `unit-replay.out` |
| **either-way proof** for the bimodal arms (verbatim committed arm text, committed + mutated receipts) | `arm-replay.py` → `arm-replay.json` — **27/27 cases as designed** |
| **absorption-gap proof** (the arms that are *not* either-way-safe) | `arm-replay-gaps.py` → `arm-replay-gaps.json` — 16/16 as designed |
| bounded **read-only** live corroboration of the addressing law | `live-readonly/probe.py` → `probe.json`, `raw-log.json`, `verdict.json`, `classifier-crosscheck.txt` |

No live battery was re-run (critic duty: zero tracked writes; a battery would
mutate the host). Live host touched with **read verbs only**
(`pw-dump`, `pactl get-*`, `pactl list`, `pw-cli info`). All runs with
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`.

Arm-replay provenance: the arm text is sliced out of
`git show 2a49d540:corpus/fixtures/measure_audio.py` by marker and `exec`'d —
it is the committed text, not a paraphrase. Only the mix arms' live
measurement function (`_pactlmon_r85_amps`) is stubbed with canned windows;
the arm's decision logic is what those cases test.

---

## 1. Custody and wiring — verified

- committed fixture sha256 `714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2`
  == working tree == the sha the author report claims for both runs.
- `+2178/−3` exactly: one 2150-line insertion (2156-line hunk incl. context)
  between `alsapw_negctl_r84_entry()` and `main()` (the family block, lines
  21579–23726) plus 5 wiring hunks; the only 3 deleted lines are the mutex
  sum, the `mode` ternary and the `suffix` ternary. Prior families untouched;
  no r76–r84 line edited.
- wiring present and correct: `--probe-pactlmon-r85` (23854), mutex sum
  (23862), dispatch `if args.probe_pactlmon_r85:` (24220) with
  `_pactlmon_r85_family_lock()` before the first entry (24233), `mode`
  (24870), `suffix` (24890).
- receipts: 5 entries / **87 legs** (40 addr + 7 mix + 6 aplayenv + 17 capture
  + 17 negctl) in **both** runs, leg names byte-identical across runs,
  `failures: {}` for all 22 entries in both runs, `own_nodes_after: []`,
  all `sinks_gone`/`sources_gone` true, `blocked`/`coverage_blocked` absent,
  loadavg 49.13–53.28 (`host_is_quiet: True`) — matches the claimed "~50,
  87 legs / 5 entries, 2 green runs".
- canon receipts byte-identical to the committed copies:
  run1 `69a96ad6…76c4` == `20261016T061227150495Z-pactlmon-r85/measurements.json`;
  run2 `98267a0f…35c5` == `20261016T061417931113Z-pactlmon-r85/measurements.json`.
- guards checked statically in the committed text: private restore key
  `r85arole<pid>` (no shared `music`); no `set-default-*` call anywhere in the
  family; every unload goes through `_pactlmon_r85_unload_own` with the
  module's **own** `sink_name=`/`source_name=` field (index re-read
  immediately before firing; `captured` ids are never fired); family-local
  classes are checked *before* the r84 chain and are **not** in
  `_CAPTURE_ERR_CLASSES`; taps bounded by `-n` and link-validated; tag tones
  fail-closed to probe-owned sinks (only SILENCE lands on the shared default
  in the aplay legs); every spawn is `start_new_session` + `killpg`.

## 2. The five law groups named in the task

| group | armed where | receipt evidence (run1/run2) |
|---|---|---|
| serial monotonicity | `addr` 22738–22744: 3 cycles, `len==3 ∧ distinct ∧ sorted` | serials 235347→235361→235375 / 236361→236375→236389; module index 536870916 ×3 (**recorded, never armed** — as documented) |
| mix taps + solo reference | `mix` `tap_ok()` 22830–22847 (non-empty, all `monitor_*`) + solo window 22858–22863 + mix2 amplitude/bleed/topology + clip rail/spur | tap links 2/2 `monitor_*` at 0.15 s; solo `l_a=r_b=8190.7/8190.8`, bleed 0.0; mix2 4 edges → 2 `playback_*` ports, 4 distinct producers, meds 8190.7 ×4, bleed 0; clip peak 32768, rail 0.2321/0.2325 ∈ [0.08,0.60], spur 1921.5/1921.3 |
| aplay env targeting | `aplayenv` 23087–23141 | `PIPEWIRE_NODE`/`PROPS` land on ns; conflict → ns only, nothing on ns2; serial-in-props publishes int 235558/236572, consumers = ns name; bogus publishes `no_such_r85a` and falls back to the default sink; no-env → default sink (silence files) |
| boundary-corrected capture lattice | `capture` 23460–23520, 23393–23458 | `t_sinkname` `bound_source` (never `monitor_*`); `t_sinkserial` → ns2 `monitor_*`; `t_prop_sinkname` → ns2 `monitor_*`; `t_prop_srcname` → default `monitor_*`; `t_srcname`/`t_srcserial`/`t_srcid` → vsrc `capture_*`; loss law: links die, never re-form, alive, sizes frozen after the flush, unload rc 0; prop loss re-links to the default monitor; self-destruct ladder 0.08–0.09 s (recorded; **see F2**); latebind either-way (**see §3**) |
| negctl table | 13 canned cases 23634–23667 + 4 live controls 23676–23723 | replay 13/13 (`unit-replay.out`); live controls rc 0/no class; `ctl_sigkill` signal `SIGKILL`, class `None` |

## 3. The three host-bimodal realizations — either-way proof

`arm-replay.py` executes the **verbatim committed arm text** against (a) the
committed run1/run2 legs and (b) mutated legs standing for the *other* side and
for the law-breaking shape. 27/27 cases behave as designed:

| arm | committed (this host) | other side (boundary) | law break |
|---|---|---|---|
| `latebind` | `late_bound` passes | `stalled` passes, `refused` passes | foreign monitor / foreign source capture / dead-rc0-“other” **fail** |
| `cdup_cap` | `serial_monitor_bypass` passes | `name_shadow_bound` passes, `refused` passes, `stalled` passes | foreign monitor **fails** |
| `sd_prop` | `bind_killed_then_default` passes | `clean_default_fallback` passes, no-links+module-gone passes | no-links+module-alive **fails**, visible trap bind **fails**, foreign monitor **fails** |
| `t_sinkname` (the least-stable row) | `bound_source` passes | refusal passes, stall passes, arbitrary-source bind passes | any `monitor_*` link **fails**, `other` **fails** |

So: the three named realizations are pinned as **either-way with an
invariant**, not silently absorbing — each side passes only through its own
recorded realization, and every shape that breaks the invariant still fails.
The two remaining author-recorded volatilities (`mixdup`/`mixdelay`) are
realizations of a bound-only arm — see **F3**, which is where the absorption
risk actually lives.

## 4. Findings

**F1 — medium — `t_srcname`/`t_srcserial`/`t_srcid` arm the port *shape*, not
the node identity; the intended check is dead code.**
`capture` 23491–23503 binds `want_node` in the loop header and never uses it;
the arm only asserts every link port starts with `capture_`. Demonstrated
(`arm-replay-gaps.json`): a record bound to `some_other_source:capture_FL/FR`
passes with no failure, while a non-`capture_` port shape still fails. Any
live source (default source, the remap source, a foreign remap) satisfies the
arm, so "source name/serial/object.id binds **this** source" is not actually
armed. Fix: `all(e["out_node"] == PACTLMON_R85_VSRC …)` (the `want_node`
value should also be `VSRC`, not `VSRC+"b"`).

**F2 — medium — the connect-kill arms accept "the module never existed".**
`sd_record`/`sd_parec` (23530–23544) accept any `module_dead_at_s` ≤ 1.5 s,
and `_pactlmon_r85_sd_leg`'s first grid sample is taken immediately, so a
*failed fresh load* reads as a kill at ≈0.0 s and passes; if the legs are
absent the loop silently `continue`s with no `coverage_blocked`. Demonstrated
(`arm-replay-gaps.json`): `module_dead_at_s=0.0` + no links passes; absent
legs pass; 2.5 s fails (control). The 0.08/0.09 s receipts show the loads did
work in both runs — latent only. Fix: record/gate the fresh load leaf and arm
`0.02 < module_dead_at_s ≤ 1.5`.

**F3 — medium — `mixdup`/`mixdelay`/`mixinv` arm only the upper bound.**
22915–22967: the arm fails only on `ratio is None or ratio > 2.05`. A ratio
of exactly 1.0 (one of the two players never started / one stream only) and
≈0.125 (the boundary's §2.1 1/8 tap-gain hazard landing on that leg) both pass
as `partial`/`cancelled`. Demonstrated (`arm-replay-gaps.json`, stubbed
`amps`): ratio 1.0 passes for all three arms, ratio 3.0 fails (controls).
Consequence of the honest downgrade of the boundary's "exactly 2×, 6/6" —
the author's own run2 measured 0.259/0.025, i.e. the boundary claim is not
reproducible here. Fix: on the duplicate legs also arm player liveness
(`player_exits` all 0/SIGKILL) and `len(mix_edges) >= 2`, and give the
duplicate legs a lower envelope (e.g. `ratio >= 0.8`) distinct from the
cancellation leg.

**F4 — low — percent-equality arms are vacuous if the `%` parse misses.**
`g_zero` (22632–22639), `g_serial` vs `g_name` (22616), `s_sink_serial` vs
`s_monitor_name` (22649) compare `_pactlmon_r85_vol_pct()` results; two `None`s
are equal. The `"Volume:"` presence check in the rc0 loop makes this need a
format change, but it is a real vacuity. Demonstrated
(`arm-replay-gaps.json`): both rows `"Volume: no percent here"` → passes;
`g_zero` rc=1 → fails (control). Fix: require `pct is not None`.

**F5 — low — `cdup_move`'s expected post-state equals its pre-state.**
22697–22705: the stream is already on the serial holder when the collision
move is issued (`after3.sink == ns_idx`), so a silent no-op (`rc=0`, unmoved)
is indistinguishable from the law. Demonstrated: `rc=0` + unchanged sink
passes; landing on the name-shadow sink fails; `rc!=0` fails. Discriminating
form: move to `ns2` first, then `move-sink-input <stream> <digits>` and require
`ns`.

**F6 — low (hygiene) — dead code.** `sers` (22738) computed and never used
(the monotonicity arm uses the raw `serials` list, which raises `TypeError` if
a cycle load returned `None` instead of failing cleanly); `want_node` (23491);
the `label` parameter of `gsv` (22487); `_r85_family_lock`'s handle (24233) is
never read (intentional fd-hold, but linter-visible). No `pyflakes`/`ruff` in
this environment; `py_compile` clean.

**F7 — low (doc drift).** The family header still states the boundary's
CLOSED law — "No late-bind: an absent-name `--target` stall is NOT re-armed"
(21645–21647) — and "the same file twice sums coherently to 2x (pinned as an
envelope)" (21652–21654), while the committed arms record the opposite
realization on this host (latebind `late_bound` 2/2) and arm only the linear
bound. The author report §4 and the arm comments are correct; the header
comment is stale and reads as if the closed law were encoded.

**F8 — medium (inherited) — the family lock is TMPDIR-scoped.**
`_pactlmon_r85_family_lock()` uses `tempfile.gettempdir()`
(`measure_audio-pactlmon-r85.lock`), so two same-family runs with different
`TMPDIR`s do not serialize — exactly the r84 critic F1 finding, inherited
verbatim by r85, and r85's tap cross-credit/collision-sink surface is the
thing the lock exists to protect. Within this wave `TMPDIR` is pinned to
`~/Projects/shokunin/tmp`, so the two author runs did serialize.

**F9 — low — post-loss arms go vacuous if the file did not exist at loss.**
`_pactlmon_r85_post_stats` with `loss_size is None` returns
`post_frames 0 / froze`, and the "growth ceased" arm compares `None == None`.
Only `pre_ok` (links at the first sample) guards it; not exercised in either
receipt (sizes present at loss in all 3 legs).

**F10 — informational — the flush bound is a documented widening.**
`post_frames ≤ 16384` (8 quanta) is looser than the boundary's safe
assertion "no new content" (they measured froze 6/6); the author measured a
2048-frame flush. Bounded, recorded, 8× margin — but a host with a larger
in-flight flush would false-red this arm.

## 5. Live read-only corroboration (independent of the author's receipts)

`live-readonly/probe.json` — current host state, read verbs only:

- default sink `…HiFi__SPDIF__sink.29`: `object.serial` **172871**,
  `object.id`/global id **232**;
- `pactl get-sink-volume 172871` → rc0, `Volume: front-left: 26214 / 40% …`;
  same row by name; **`get-sink-volume 232` → rc1 `Failed to get sink
  information: No such entity`**;
- `pactl list sinks short` first field = **172871** == `object.serial`
  (the index the move/collision arms compare against);
- `pw-cli info 232` → rc0 node dump; `pw-cli info 172871` → **rc0 +
  `unknown global '172871'`** (the rc-0 lie shape);
- default source name and serial both rc0; `get-source-volume <sink name>` →
  rc1 `Failed to get source information: No such entity`;
- classifier cross-check: the live stderr shapes classify as
  `pa_get_info_noent` / `pwcli_unknown_global` exactly as the negctl table
  expects (`live-readonly/classifier-crosscheck.txt`).

Verdict: the encoded serial-not-id / pw-cli-inversion / index==serial laws
hold on this host now.

## 6. Probe tooling note

The frozen probeParent dispatched exactly one read-only `labrat` probe
(hypothesis = the addressing law above). The child returned **inconclusive —
no measured evidence**: its substrate exposed only file-inspection tools
(no exec), so it could run no `pw-dump`/`pactl`/`pw-cli` command and wrote no
receipts. That unavailability is recorded here rather than as absence; the
dispatcher then ran the same bounded read-only battery directly (§5). The
child made no edits and left nothing behind.

## 7. Blockers / remaining risks

- **Blockers: none.**
- Remaining risks: F1–F3 are latent absorption channels that a future
  low-load host can hit (F3 also re-opens the §2.1 tap hazard on the three
  bound-only legs); F8 means same-family exclusion depends on a shared
  `TMPDIR`; the three bimodal realizations may realize the other side on a
  verifier host — all sides are armed, so that is a pass, not a failure.
- Custody note: `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  was **already dirty** (`M`) in the first `git status` of this session; my
  imports/compile refreshed it byte-identically (a fresh compile of the
  unchanged source hashes to the same bytes, `e5a32d87…`), so no tracked
  content changed. The source file itself is byte-identical to the commit.
