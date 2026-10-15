# R79 VERIFIER (audio) — independent replay of `--probe-capture-r79`, r78 regression, forge-kill

Seat: VERIFIER. Lane `~/Projects/shokunin/audio-shokunin`, HEAD
`a2616f732253ed90110ba16a223ec7d10224740c`. Host `plazir27`.
Toolchain: PipeWire 1.6.8, pactl 17.0-98-gb096, Python 3.14.7 (numpy 2.5.3),
Linux 7.2.3-arch1-3. Frozen artifact under test:
`corpus/fixtures/measure_audio.py` sha256
`4ee754b3fa7dab6c7be7c60930fc8c14854acf7f5439c9b150bb40aba0805095`
(matches the author's `frozen-artifact.txt`; `+2737/−3`; the three deletions
are exactly the exclusivity sum, the `mode` ternary, and the `suffix`
ternary — verified with `git diff -U0`, prior modes keep their values:
my r78 run's receipt `mode` is `probe-capture-r78`).

**No LSP device exists in this session** (`lsp` is not an available tool),
so caller/definition/diagnostics checks were done literally — reading the
file, exact diff hunks, and first-hand runtime experiments. Nothing below
is claimed as semantic (LSP) proof; grep/read output is used as text
evidence only.

**Write scope:** untracked `corpus/live/r79-verify/` (runs, comparison
tooling, forge receipts, host snapshots) and this report. No tracked edit
by this seat; the tracked `__pycache__/measure_audio.cpython-314.pyc` that
any run/import dirties was restored (`git checkout`), so the tracked tree
shows only the pre-existing ` M SHONEN.md` and the author's
` M corpus/fixtures/measure_audio.py`. No commit.

---

## 1. Verdict table

All cells below are read from my own receipt
`corpus/live/runs/20261015T080513286525Z-capture-r79/measurements.json`
(run V1, pid 4035425) unless noted; every cell was also compared against
author runs B/C and my V2 — see §3 for the replication result.

| # | author claim (§ in `r79-author.md`) | independent measurement (V1) | verdict |
| --- | --- | --- | --- |
| 1 | shape: one client, two nodes; `input.<n>` Stream/Input/Audio (`input_FL/FR` + `monitor_FL/FR`), `output.<n>` Stream/Output/Audio (`output_FL/FR`, **no** inputs); same client.id; one link-group; zero links join the pair | client_id 155 on both; `node.link-group` `loopback-4035880-20` on both; input ports `[input…:input_FL, input…:input_FR]`, output ports `[input…:monitor_FL, input…:monitor_FR]`; output node `input_ports []`, `[output…:output_FL, output…:output_FR]`; `target.object` verbatim (`ns_a`/`ns_b`); no self-edge in any sample | **CONFIRMED** |
| 2 | `-C` lattice: sink prop → that sink's monitor; prop with garbage/source target → default sink monitor; without prop → default source (unnegotiated on this host) | b01 producers `[ns_a]` ports `:monitor_*`; b08 (real source + `target.object=ns_a`) producers `[ns_a]` (**prop beats flag**); b09/b12 producers `[SPDIF]` ports `:monitor_*`; b02/b03/b05/b06/b07 producers `[]` + `capture_default_source_unnegotiated`; b10/b11 producers `[]`; `target_object_lies` True on b09 (request echoed, other node consumed) | **CONFIRMED** |
| 3 | `-P` lattice: resolvable honored; every unresolvable/inapplicable form lands the current default sink; `-o target.object` beats `-P` with a silent-sink control; `node.autoconnect=false` publishes unlinked | c01/c02 `[ns_b]/[ns_b2]`; c03/c04/c05/c06/c10 `[SPDIF]`; c07 consumers `[ns_b2]` with control tap on `ns_b` bound+ran+**0** `mine`; c08 `[]` | **CONFIRMED** |
| 4 | matrix: `[ MONO ]`/`MONO` → 0.5·(L+R) at 2269.3 (passthrough 4538.6, ratio 0.500); `-c 1` alone inert; port names stay `*_FL/*_FR` | cm1/cm3/cm4 channels `[{at_l 2269.3, at_r 2269.3}, …]`, `mix_half_gain_ratio 0.5`; cm2 `[{4538.6, 2.8}, {4.0, 4538.6}]`, ratio None; positions as claimed | **CONFIRMED** |
| 5 | `pw-record --target`: `output.<lb>` honored; `input.<lb>` + prop → monitor ports; `input.<lb>` without prop → default-source arm; prop on `output.<lb>` → default sink monitor; D17 manual pins rc=0 | d2b producers `[output…_rect_lb]` 14 `mine`; d2c `[input…_rect_lb]` 14 `mine`; d2d `[SPDIF]` 0 `mine`; d2a `[]` + `capture_default_source_unnegotiated`; d17 both `pw-link` pin commands exit 0, producers `[input…_rect_lb]` 14 `mine`, record stream rc 1 at its `-n` bound (its success shape) | **CONFIRMED** |
| 6 | hot-plug both ways, client alive, tone stops before every unload | e1 out-union `[SPDIF, hp]`; e2 `[SPDIF, hp2]`; e3 in-union `[SPDIF, ns_a]`, playback side untouched `[ns_b]`; all three `killed_at_bound` True; unload/load events fired rc 0 with ids | **CONFIRMED** |
| 7 | pw-cat latency prop vector verbatim; prop beats flag; `--latency 0` non-fatal argv error; param takes 3 distinct values (`latency_param_tracks_request`) | measured `node.latency`: d01 `4800/48000`, d02 `480/48000`, d03 `256/48000`, d04 `480`, d05 `1024/48000`, d06 `2048/48000`, d07 **absent**, d08 `0`, d09 `24000/48000`, d10 `480/48000`, d11/d12/d13 `4800/48000`; verdict `latency_param_tracks_request`; d13 stalls unlinked | **CONFIRMED** |
| 8 | filter-chain: good fragment publishes both nodes and they die with the loader; syntax error is a warning with later fragments still loading; bad label + `nofail` silent; without `nofail` loader rc 254; pw-cli client-scoped; DSP witness 0.5·(L+R) on FL, FR silence | f1 `expect_met` True, nodes `[mix_input…_f1, mix_output…_f1]`, loader rc −9 at kill; f2 parse-soft (loader alive, warning, no node); f3/f3b good node published despite the bad fragment; f4 silent tolerate; f5 **rc 254**; f6 control; f1 two-tone `[{at_l 4095.6, at_r 4095.6, peak 8191}, {0.0, 0.0, 0}]` | **CONFIRMED** |
| 9 | two formal runs, `failures: {}`, exit 0, empty stderr, 66 legs, no blocked entry, zero surviving nodes | my V1/V2: exit 0, `failures {}`, stderr 0 B, 25 measurements, 8/8 entries, **66 legs**, no `blocked`/`coverage_blocked`, `own_nodes_after: []` in all 8 entries, every probe sink `sinks_gone: True`; author B/C re-parsed: same 25/8/66, no blocked, `failures {}` | **CONFIRMED** |

Named-outcome class replication: V1 and V2 each carry exactly the same
seven `capture_default_source_unnegotiated` outcomes (shape a5; capture
b02/b03/b05/b06/b07; record d2a) with `source_meta=None` per-leg
correlates — the conditional fallback class is real and reproduced, not a
one-run artifact.

## 2. Independent runs

| run | window (UTC) | receipt | sha256 | exit | failures | stderr |
| --- | --- | --- | --- | --- | --- | --- |
| V1 `--probe-capture-r79` | 07:59:45 → 08:05:13 | `runs/20261015T080513286525Z-capture-r79/measurements.json` | `137b7472b969eb5e…` | 0 | `{}` | 0 B |
| V2 `--probe-capture-r79` | 08:05:18 → 08:10:45 | `runs/20261015T081045790824Z-capture-r79/measurements.json` | `594528b489a3a0a7…` | 0 | `{}` | 0 B |
| R78 `--probe-capture-r78` | 08:10:54 → 08:14:21 | `runs/20261015T081421351571Z-capture-r78/measurements.json` | `76d29dcb734aeecc…` | 0 | `{}` | 0 B |

Driver: `corpus/live/r79-verify/verify-run.sh` (my own; independent of
`r79-author/formal-runs.sh`), one probe per invocation, host snapshot
before/after each in `corpus/live/r79-verify/host-window-verify.log`.
Author B/C receipt sha256s re-derived and equal to the author's
`RECEIPTS.md` (`658773646ec8…`, `f4572530cb…`).

## 3. Field stability — replication modulo pids/timestamps

Two independent projections, both in `corpus/live/r79-verify/`:

* **Verdict keys** (`verdict_replication.py` → `verdict-replication-all.txt`):
  **681 verdict-bearing keys compared across B, C, V1, V2 — 0 differing**
  after normalizing pid-stamped names. Keys cover every entry's
  blocked/coverage/failures/teardown, every leg's topology unions and
  expectations, outcomes, tap verdicts (`bound_to_target`, `ran`,
  `carries_tone`, `mine_windows`), matrix signatures, latency values, and
  filter-chain verdicts. The author's "68/70 fields identical" is
  confirmed on a larger independent projection.
* **Full canonical diff** (`field_diff.py` → `field-diff-all.txt`): B vs V1
  differs on 94 leaf paths, of which 54 are measured/structural — and
  **every one of those 54 is an amplitude-estimate leaf whose value is a
  function of the pid-derived tag frequency** (`PLAYBACK_R78_TONE_L_HZ =
  997 + pid%4·211`, R = L+503, measure_audio.py:5970). Measured:
  B (L=997) `tap.peak_l/peak_r` 7725/8189; C (L=1419) 8137/7980;
  V1 (L=1208) 7980/8136; V2 (L=1630) 8189/7725 — all the same physical
  8192-amplitude tone, ±5.7 % estimator spread, while the verdict leaves
  (`mine_windows`, `mine_spans`, `carries_tone`) are byte-identical. The
  remaining diffs are timing/pacing (window counts, `zero_windows`),
  run-local ids (module ids, `client_id`, link-group), tmp paths, and the
  contention leaves. Matrix noise floor moves 2.7→3.0 across runs.

**Drift verdict: none at the verdict surface; the raw-leaf drift is the
designed per-run tone pair, not instability.** (The author's own B/C pair
also differs on 47 such leaves, so this is not a V1 artifact.)

## 4. r78 regression — and the two blocked capture arms

The r78 probe on the r79 tree: `failures {}`, exit 0, empty stderr,
17/17 fixture probes clean. Two r78 arms are `coverage_blocked` exactly as
the author stated:

* `capture_unlinked_zeros_r78_probe`: `monitor_source.enumerated False`,
  `waited_s 4.023`;
* `capture_parec_fix_r78_probe`: `enumerated False`, `waited_s 4.046`
  (the helper's 4 s timeout);
* plus one named `coverage_blocked` on `playback_default_follow_r78_probe`
  (`pactl: metadata was SPDIF at write time, not r78_def_sink_…`) — the
  r78 family's known flap class, not a new failure.

Key-set comparison against the baseline anchor receipt
(`corpus/live/r79-baseline/anchor-receipt-…json`): identical 25
measurements, identical failure-key sets (mine empty; the anchor's two
arms red), and every r78 arm has an identical leaf set **except**
`playback_aplay_axis_r78_probe.legs.params_cap.params`, where 8 leaves
(`channels*`, `rate*`, `formats`, `device_name`) exist in my run and in
the author's 05:57:01Z receipt but not in the anchor. Cause measured, not
code: the anchor's `arecord -D hw:0,0 --dump-hw-params` exited 1 with
`audio open error: Device or resource busy`, so the dump parsed to `{}`;
mine and 05:57 parsed the full envelope. Environment-conditional leaves,
not drift — the parsing code sits at measure_audio.py:7932-8000, far
outside every r79 diff hunk. **Note (pre-existing soft spot, r78 code):
the arm's envelope assertion is skipped when either side parses empty
(`if pp.get("channels_max") is not None and cp.get("channels_max") is not
None`), so the anchor's envelope check was vacuous.**

**Pre-existing defect or r79 regression? Pre-existing — four independent
witnesses:**

1. The helper `_playback_r78_wait_source` (measure_audio.py:6197) is
   **untouched** by the r79 diff: the diff hunks are
   `8824+2705`, `11651+1`, `11656(1)`, `11947+28`, `12505(1)`, `12525(1)`;
   the only occurrence of the helper's name anywhere in the diff is a
   comment in the new r79 gate. The three deletions are the wiring lines.
2. History across all r78 receipts
   (`corpus/live/r79-verify/r78-monitor-gate-history.txt`): the gate leaf
   first exists at 05:37:41Z (`True`, 0.002 s — pre-fold variant), and
   **every receipt from 05:50:13Z onward is `False` with ~4 s waits**
   (05:50:13Z, 05:57:01Z, 06:05:13Z, 08:14:21Z). The fold commit
   `a005e1e` is timestamped 06:00:10Z, and the baseline's anchor receipt
   at 06:05:13Z was taken on a **clean tree** — HEAD blob sha1
   `39286c725c25b034fcb0dcfc0f23bd5c3910a2ee`, re-verified here — so that
   receipt contains zero r79 code.
3. First-hand mechanism proof (`r78-gate-proof.py` /
   `r78-gate-proof.json`), using the **pristine HEAD module**
   (`git show HEAD:…`, sha256 `e66b38b1a2ccdd25…`) on a freshly loaded null
   sink: `pactl list sources` lists `r79verify_ns_218483.monitor` (True)
   but `pw-link -o` lists the monitor ports owned by the **sink**
   (`r79verify_ns_218483:monitor_FL/FR`) and
   `_playback_r78_output_ports("<sink>.monitor")` returns `[]` — so
   `_playback_r78_wait_source` returns `(False, 4.033 s)` and can never
   succeed here. The r79-local gate `_loopback_r79_wait_monitor` on the
   same sink returns `ready True, 0.006 s` (`pactl_listed True,
   monitor_ports True`). Sink unloaded by module id, `sink_gone True`.
4. My r78 run reproduces the identical block messages and 4 s waits.

**Consequence (finding A1):** the r78 fold armed a fail-closed guard that
is *permanently* closed on this host, so two r78 capture arms have been
vacuous since 05:50:13Z. The r78 baseline listed them among "6/8 clean"
arms — blocked entries carry zero failures, so a blocked arm reads green
in a failure-count summary. The r79 author named this and correctly did
not "fix" it (un-blocking would relax an inherited guard and change
prior-row behavior). The r79 arm's own gate is the corrected form.

## 5. Forge-kill receipt

Scratch mutants of the working-tree artifact, run as the real probe from a
path with `ROOT=corpus` so receipts land in `corpus/live/runs/`. Mutant
sources and diffs archived in `corpus/live/r79-verify/forge/`; the
scratch file under `corpus/fixtures/` was deleted after the runs.

| forge | mutation | mutant sha256 | run | result |
| --- | --- | --- | --- | --- |
| F-union | capture lattice b01 expected producer forged to `forge_missing_node_r79` | `398b026093cb166f…` | `runs/20261015T082148085394Z-capture-r79` | **exit 1**, sole failure `capture b01_sink_prop: expected producers [forge_missing_node_r79], got ['r79lb_ns_a_224789']`; all other entries green |
| F-tap | a1 leg's monitor tap aimed at a nonexistent node (its claimed target kept) | `f90592009cf1db2c…` | `runs/20261015T082734926185Z-capture-r79` | **exit 1**, sole failure `shape a1: the tap on r79lb_ns_b_257649 carried no tag-tone windows — consumption without content is not a playout verdict`; all other entries green |

F-tap's receipt shows *why* the kill is the right one: the forged tap
silently fell back to the **shared default sink monitor**
(`bound_producers ['alsa_output…SPDIF__sink']`, `bound_to_target False`,
55/55 zero windows), so the provenance confound and the hard content
failure both fired. The union gate and the tap-content gate are
load-bearing and kill a forged expectation / forged witness.

**Process note (self-caught):** my first mutant paired F-union with a tap
mutation keyed on the leg name `a1_shape`, but `_loopback_r79_leg`
receives `a1` — that half was **inert**. The run still killed F-union
(its receipt is `forge/forge-union-receipt.json`), and the a1 tap leaf
showed `bound_to_target True`, i.e. the tap mutation never applied. I
corrected the key and re-ran F-tap alone
(`forge/forge-tap-receipt.json`). Receipts over prose, including for the
verifier's own mutations.

## 6. Host quiet / contention ledger

`pgrep` was taken immediately before every run and in every snapshot
(`host-window-verify.log`).

* **V1 start (07:59:45Z): quiet** — no probe process, zero r79
  nodes/modules; the only sibling is the ~12 h stale
  `aplay -D null /tmp/nowriter-r75-…` (pid 2202613, another lane's leak,
  already named by the r78 baseline). V1 was then overlapped by foreign
  r79 probes: pid `4041488` (null sinks left SUSPENDED at 08:05:13Z) and
  pid `112759` (mid-capture-lattice at 08:05:13Z, b06/b07 legs live).
* **V2 (08:05:18 → 08:10:45Z): contended** — pid `112759` mid-run at
  start; by 08:10:45 a pid-pinned r79 probe (`../pidpin.py 0 python3 …
  --probe-capture-r79`, pid 139148) plus the simplifier's `r79bchk14`
  legs were live. Load average 4.24–4.38 at snapshots.
* **R78 (08:10:54 → 08:14:21Z): contended** — same pidpin probe and
  boundary/simplifier lanes; load ~4.
* **Forge runs (08:15 → 08:27Z): contended** — pidpin probes (196168,
  280716), the r79-boundary lane (`r79bo_*`), simplifier lanes.
* No `measure_audio` probe of *mine* was live during any other of my runs
  (serial execution), and each of my runs recorded `host_is_quiet: false`
  with `contention` leaves naming the foreign `aplay` and 1–2 foreign
  `pw_loopback` processes.
* **No contamination event in any of my runs**: zero
  `foreign_tone_witness` leaves, and the only leg confounds are the six
  systematic `tap bound to []` confounds on the never-fed legs (§7 A2) —
  identical in all four receipts.
* My runs left no residue: per-pid node count 0 for 4035425/127171/190539
  and both forge pids; `own_nodes_after: []`, `sinks_gone` all True.
  Foreign leftovers *did* accumulate during the window
  (`r79lb_ns_a/b_4041488`, `r79lb_fc_229236` modules still loaded at
  08:30Z) — not mine, not the author's.

## 7. Anomalies, by severity

**A1 — Medium (pre-existing, not an r79 regression): the r78
monitor-source gate can never confirm a null-sink monitor on this host.**
`capture_unlinked_zeros_r78_probe` and `capture_parec_fix_r78_probe` are
permanently `coverage_blocked` (zero failures, so they read "clean" in
failure-count summaries). Evidence: §4 (helper untouched by the diff;
`False` from 05:50:13Z onward incl. the clean-tree 06:05:13Z anchor;
pristine-HEAD experiment; `measure_audio.py:6197` vs `:9482`). Scope: this
host/version; the mechanism (fold's port-tag witness requires
`<sink>.monitor:` ports that the graph never publishes) is first-hand
verified. Not actionable inside r79 without changing prior-row behavior —
handed up as-is, as the author did.

**A2 — Low: the content pin is vacuous on the six never-fed legs.**
On a5/b02/b03/b05/b06/b07 the tap never binds (`bound_producers []`, 55/55
zero windows) — recorded as a named confound (`entry.confound_observed`
plus a leg `confound` string) but *not* a failure, and for these
`want_tone=False` legs the only content check is "no `mine` windows",
which an unbound tap trivially satisfies. The author's §10 phrasing ("a
tap that never bound is a named confound, never a pass") is honest about
the confound, but the leg does pass on topology alone. Recommend for a
future round: fail the leg when a tap spawned for a non-empty content
claim never bound (or require binding explicitly). Not a claim overreach
here, since those legs claim topology only.

**A3 — Info: receipt-leaf instability.** My runs' pw-cli `reply[]` lacks
the trailing `pipewire-0>> ` prompt line that B/C captured (3 vs 2
entries); the verdict line (`Error: "Could not load module"`) is identical
in both, so this is a scrape/pacing artifact, not a verdict difference.
Window counts/`zero_windows`/`audio_windows` and `loaded[0]` module ids
also move run-to-run by design.

**A4 — Info: two dead-code warts in the new arm.**
`tap_t = ns_b if kind != "none" else ns_b` (capture lattice,
measure_audio.py:9975 — both branches identical) and the unused
`extra_tw` list (playback lattice, :10172; the witness is registered via
`ctx_l`). Behaviour-neutral; the author cleaned a similar wart in §1 item 9.

**A5 — Info: foreign host-state leaks during the window.** Three
`r79lb_*` null-sink modules (`ns_a/b_4041488`, `fc_229236`) stayed loaded
after their owning processes exited — sibling lanes' leaks, not this arm's.
The ~12 h stale `aplay` (pid 2202613) persists.

**A6 — Info: tracked `__pycache__` side effect.** Running/importing the
fixture dirties the tracked `.pyc`; restored here (and by the author).

**A7 — Info (pre-existing r78 code, surfaced by the regression
comparison): conditional-vacuity in the aplay envelope arm.** When
`arecord --dump-hw-params` fails (device busy — the anchor's case), the
parsed params are `{}` and the playback/capture envelope assertion is
skipped without a named outcome; the receipt then carries no envelope
evidence for that run (the baseline anchor counted this arm "clean"). Not
r79's diff; noted for a future r78-side fold.

## 8. Residual risk and verification gaps

* No LSP device in this session: no semantic references/definition/
  diagnostics proof; caller/invariant checks are literal (diff hunks, code
  reading, runtime experiments).
* All findings are bounded to this host/toolchain (PipeWire 1.6.8, pactl
  17.0-98, this device set). The `capture_default_source_unnegotiated`
  class replicates with its per-leg correlate, but *why* WirePlumber hands
  out no default source is not established (same limit the author
  declares).
* The author's exploratory diagnostics (`exp_*.py`) were not re-run; my
  independent evidence for the same facts is the probe runs plus the
  gate-proof experiment.
* Forge tests mutate the harness, proving the gates bite; they do not
  prove the measured surface is complete (e.g. `-m` forms beyond the four
  legs, non-builtin filter-chain node types, other hosts).
* `latency_param_tracks_request` replicated in V1/V2 with the identical
  3-value set, but remains one host/version observation against r78's
  single-value reading.
* The r78 family flaps under multi-seat load (baseline: 11/13 receipts
  carry some red arm). My r78 run happened to be green (`failures {}`) on
  the two highest-flap arms; that is one sample, not a stability claim.

## 9. Artifact index (all under `corpus/live/r79-verify/`)

* `verify-run.sh`, `vrun1.*`, `vrun2.*`, `vrun-r78.*` — run driver, stdout,
  stderr (all stderr 0 B).
* `host-window-verify.log` — pre/post snapshots (sha256, pgrep, defaults,
  foreign nodes, leftovers, load).
* `field_diff.py`, `field-diff-BC-vrun1.txt`, `field-diff-all.txt` —
  canonical whole-receipt diffs with pid/volatile normalization.
* `verdict_replication.py`, `verdict-replication-all.txt` — 681 verdict
  keys × 4 receipts, 0 diffs.
* `headline_cells.py`, `headline-cells-all.txt` — headline cells across
  the four receipts.
* `r78-gate-proof.py`, `r78-gate-proof.json`,
  `r78-monitor-gate-history.txt` — the pre-existing-defect evidence.
* `head-mod/measure_audio_head.py` — pristine HEAD module used for the
  gate proof (sha256 `e66b38b1a2ccdd25…`).
* `forge/` — both mutant sources + diffs, run stdout/stderr, and the two
  failure receipts (`forge-union-receipt.json`, `forge-tap-receipt.json`).

Canonical receipts (written by the probe itself):
`runs/20261015T080513286525Z-capture-r79/`,
`runs/20261015T081045790824Z-capture-r79/`,
`runs/20261015T081421351571Z-capture-r78/`,
`runs/20261015T082148085394Z-capture-r79/` (F-union),
`runs/20261015T082734926185Z-capture-r79/` (F-tap).

**Verdict (recommendation, not an admission):** the r79 arm's declared
claims replicate under independent execution (2/2 green, 681/681 verdict
keys, 66/66 legs, clean teardown); the r78 regression shows no r79-induced
change, with the two blocked capture arms proven pre-existing by
first-hand experiment on pristine HEAD code; both load-bearing gates kill
their forgeries with exit 1. Recommend ADMIT-with-notes, the notes being
A1 (handed up, pre-existing) and A2 (softness on never-fed legs).
