# r93 author — the `ebur128` node's loudness lattice, authored and green

Seat: AUTHOR, worktree `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r93`
(branch `wt-r93` @ `5a632a4f`). Window **2026-10-16 05:44–10:45 UTC** on host
`plazir27`. Toolchain read live: PipeWire **1.6.8** (`1:1.6.8-1`),
libebur128 **1.2.6-2**, Python 3.14.7, 32 cores. `TMPDIR=~/Projects/shokunin/tmp`.
**Zero commits.**

**Status: nine entries, 90 armed legs, two green batteries on the final bytes**
(`failures: {}`), after a ~3.4 h host-daemon wedge that had to be worked
through (§5). Every armed law is a boundary-surviving claim; where the boundary
falsified a constant, the **law** is armed and the constant recorded.

---

## 1. Files changed

| path | change |
| --- | --- |
| `corpus/fixtures/measure_audio.py` | **+2056 / −3** — the r93 family, inserted before `def main()` (sha256 in §6). The only deletions are the three shared wiring lines (mutex list, mode select, receipt suffix); `import math` is added to the import block. |
| `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` | **tracked, modified as a byproduct** — this repo tracks the fixture caches, so running the edited module rewrote its `.pyc`. It is a generated cache of the new source (no semantic content of its own); it was left in place rather than reverted to a stale copy. A sibling's cache (`r93-scout/probes/__pycache__/pwlib93…pyc`, rewritten when the dev probes imported their library) was restored to HEAD. |
| `corpus/live/round-93/*.wav` | **14 fixture members** (analytic f32/48 kHz, §3.1), written by `_ebur_r93_stimuli()`, sha256 recorded in every receipt |
| `corpus/live/runs/20261016T101716935215Z-ebur-r93/measurements.json` | **green battery #1** |
| `corpus/live/runs/20261016T103145603182Z-ebur-r93/measurements.json` | **green battery #2** (same bytes; §6) |
| `corpus/live/runs/20261016T092003125628Z-ebur-r93/`, `…T092216336849Z-…`, `…T100229270710Z-…` | the three earlier battery attempts (gate-blocked ×2, then the first full run with four arm bugs — §5.4) |
| `corpus/live/r93-author/runs/` | the live receipts copied under the assigned receipts path |
| `corpus/live/r93-author/probes/{dev1..dev7,r93_block_a,r93_block_b}.py` | the dev probes (pre-wedge readings, offline arming self-test) and the two block sources |
| `reports/round-93/r93-author.md` | this file |

Nothing committed; no other tracked file was touched.

**Fixture-location note (deliberate, disclosed).** The assignment said "new
fixtures under `corpus/fixtures/`"; the repo's own convention for fixture
*members* is `corpus/live/round-N/` (tracked members live in
`corpus/live/round-3|4|6|7|8|10|11|65|66`; `corpus/fixtures/` holds only the two
Python builders). The r93 members land in `corpus/live/round-93/`, the same
place `--probe-slope` puts `corpus/live/round-3/slope_probe.wav`. Moving them
is a one-line change of `EBUR_R93_STIM_DIR`.

---

## 2. What was measured (battery #1, 90 legs, `failures: {}`)

### 2.1 The claim table, with the readouts

| claim | armed law | measured (battery #1) |
| --- | --- | --- |
| **C1** topology + notify names | load log = 7/7/0/7; each notify name linkable; a bogus name yields nothing | `loaded n_input:7 n_output:7 n_control:0 n_notify:7` ×2; all 7 names → 54 readout lines each; `notify_bogus` → 0 lines (load refused, class `pwcli_module_load_fail` — the name is load-bearing either way); the chain exports `playback_MONO`+`monitor_MONO` |
| **C2** the readout is the `debug` link | — | every leg's readout arrives as `[I][…][plugin_builtin.c: … debug_run()] control: <v>` in the loading session |
| **C3** Momentary = exact BS.1770 K-weighted 400 ms | \|plateau − own reference\| ≤ 1e-3 dB; boundary constants ± 1e-4 | 1 kHz/1.0 `-3.003596` (ref `-3.003596`); 1 kHz/0.5 `-9.024196` ×2 (ref `-9.024195`); 0.25 `-15.044795` (ref exact); 40 Hz `-15.288830` (ref `-15.288824`); 100 Hz `-10.855398`; 4 kHz `-5.753903`; 10 kHz `-5.680018` ×2 (ref exact) |
| **C3′** K-weighting transfer | delta vs 1 kHz ± 0.01 dB | 40 Hz `-6.264634` (boundary `-6.2646`), 100 Hz `-1.831202` (`-1.8312`), 4 kHz `+3.270293` (`+3.2703`), 10 kHz `+3.344178` (`+3.3442`) |
| **C4** the per-port channel map is dead | all 7 input ports read the single-state value | `FL FR FC UNUSED SL SR DUAL MONO` = **`-9.024196` ×7** |
| **C5** dB mean, no summation | mix = dB mean ± 0.01 and ≥2 dB off the energy mean; a stereo pair = one channel | `FL 0.5 + FR 0.05` → **`-19.024195`** (the energy mean would be `-11.99`); `FL+FR` same tone → `-9.024196` |
| **C6** a silent channel poisons Momentary | `n_finite == 0`, `n_inf == n`; Global finite | **151/151 `-inf`, 0 finite**; Global `-9.091105` |
| **C8** Window-only ⇒ constant NaN pass-through | `n_finite == 0`, `n_nan ≥ n−2`, post tap alive | **150 NaN / 0 finite**, post tap **166911 nonzero** (audio flows) |
| **C8′** Range-only / Peak-only | the stale `0.0` class | `0.0` ×151, no NaN |
| **C9** Peak / True Peak index bug | FL `0.5`, DUAL MONO `0.0`, stereo `0.2` | Peak `0.5 / 0.0 / 0.2`; True Peak `0.5 / 0.0 / 0.2` |
| **C10** `max-window` honoured | absent ⇒ NaN; decay scales with the window | absent → all NaN; **0.4 → 0.427 s ×2**, **2.0 → 1.856 s ×2** (the boundary's own quiet/load values); Δ = 1.429 s |
| **C11** `max-history` is an above-gate block cap | silence never evicts; a second burst does; the own gated reference is the outside witness | burst+5 s silence: default `-9.505959/-9.537175` vs cap2 `-9.522255/-9.537175` (max Δ 0.031 ≤ 0.05); two bursts: default `-11.503388/-11.507975` vs cap2 `-15.539840/-15.532363` (Δ 4.03 LU); own reference `-11.283493` → default dev −0.22 LU (in envelope), cap dev −4.26 LU (outside) |
| **C12** `gain = 10^((target−LUFS)/20)` | same-leg residual ≤ 0.01 dB; clamp; silence ⇒ 1.0 | target 0: **residual `0.0 dB`** (gain `2.896856`); clamp: residual vs the −70 prediction **−0.0019 dB**, gain `0.000916` ≫ 10× the unclamped `2.9e-5`; silence: gain **exactly `1.0`**; default gain `0.205082` |
| **C13** a spaced control key must be quoted | the raw form refuses the load | refused with class `ebur_r93_ctl_grammar` (`error parsing more than 0 properties: Expected object key` + `missing filter.graph property`) |
| **C14** the label matrix | 5 load / 5 do not; `null` a distinct class | load: `debug busy sqrt ramp zeroramp`; fail: `null` → `ebur_r93_label_parse` (`error parsing label`), `avg sum gain nop` → `ebur_r93_plugin_refused` (`cannot create label`) |
| **C15** warning-only vs deferred | unknown key works with a `[W]` and no `[E]`; a non-numeric value loads and never meters | `config={bogus=1}` → `-9.024196`, `[W] … unknown key bogus`, no `[E]`; `config={max-history=abc}` → module loaded, **no readout at all**, with `[E] … requires a number` + `[E] … cannot create plugin instance … Invalid argument` |
| **C16** Global is not an independent BS.1770 measurement | ±1.0 LU envelope, never a constant | silent-channel Global dev **−0.067 LU**; two-burst default dev **−0.220 LU**; both inside the envelope, and the cap arm outside it |

### 2.2 Coverage recorded, not hidden

Two sub-arms are `coverage_blocked` (honest, non-failing):

1. `g_default` — **the audio-domain ratio is unmeasured**: the `post` tap (the
   chain's `output_MONO` after the `linear` gain node) carries a silent mid-tone
   window (`post=0.0`) while the `pre` tap is live (`pre≈0.207`). The tap binds
   and drains; the chain's output side produces no audio in this graph shape, so
   the ratio cannot be formed. The C12 *law* is carried by the same-leg residual
   (exactly `0.0 dB`), not by this witness. Recorded per leg with the tap RMS.
2. `notify_bogus` — the control's load was **refused** rather than loading with
   no readout (class `pwcli_module_load_fail`). Both outcomes prove the notify
   name is load-bearing; the leg records which one it saw
   (`control_class`).

### 2.3 Hygiene (every entry, both green runs)

`unloads[*].exit_code == 0` on the name-verified index; `sinks_gone` all-true;
`own_nodes_after: []`; `own_procs_after: []`; no `pactl set-default-*` ever
issued; the family lock is the fixed path
`corpus/live/measure_audio-ebur-r93.lock`.

---

## 3. The instrument

### 3.1 Fixture members (`corpus/live/round-93/`, sha256 in every receipt)

| member | frames | ch | sha256 (16) |
| --- | --- | --- | --- |
| `tone_1k_100` / `tone_1k_050` / `tone_1k_025` | 168000 | 1 | `e91db1c3c3d26c34` / `b377abe8db044e44` / `bdb6dcc1fb906d0c` |
| `tone_40_050` / `tone_100_050` / `tone_4k_050` / `tone_10k_050` | 168000 | 1 | `4fab39dc05b8744a` / `4f9caf364b900bc4` / `d2bf98f659b7825a` / `5627cd1ef5a82727` |
| `silence` | 168000 | 1 | `90165aa043f1d7ed` |
| `burst_1500ms` | 72000 | 1 | `37dfb759b0cd7356` |
| `bursts_two` (2.5 s @0.5 + 1.5 s silence + 2.5 s @0.25) | 312000 | 1 | `d6b62812a5aa3c4f` |
| `st_mix` (FL 0.5 / FR 0.05) | 168000 | 2 | `7a11577c41f616bd` |
| `st_both` (FL=FR 0.5) | 168000 | 2 | `3f5f779213d2fc9e` |
| `st_tone_silence` (FL 0.5 / FR 0) | 168000 | 2 | `effff5768456dc89` |
| `st_02_08` (FL 0.2 / FR 0.8) | 168000 | 2 | `4d12c7d58bcffe0a` |

Analytic sines, source-generated in-fixture (no seeded noise, no borrowed
audio, no rights question).

### 3.2 The arm (per leg, fresh)

`pactl load-module module-null-sink sink_name=r93a_<pid>_in channels=<ch>` → an
interactive `pw-cli` session opened with **`PIPEWIRE_DEBUG=3`** → `load-module
libpipewire-module-filter-chain <args>` **inside that session** (the module —
and therefore the plugin's INFO readout — lives in the client process, which is
why the debug level matters) → link the sink monitor to the chain
(`monitor_<ch> → playback_<ch>`, retried) → optional `pw-record` taps (`pre` =
sink monitor, `post` = the chain's `output_<ch>`) linked explicitly → `pw-play
--target <sink> <member>` → drain `dur + read_extra` → `unload-module <var>` in
the same session → `quit` → name-verified sink unload.

Readout parse: `[I][HH:MM:SS.µs][…] control: <v>` → `(t_rel, value)` with the
three observed literals `-nan` / `-inf` / finite dB. Plateau = median of the
longest run of consecutive near-equal finite values (0.05 dB grouping) — the
scout's convention, so every number is comparable with the scout/boundary
tables.

### 3.3 New harness laws this family adds

1. **The daemon is a gated prerequisite, not a variable.**
   `_ebur_r93_daemon_gate()` waits (bounded, 60 s) for `pactl info` *and* a
   `pw-dump` census; when they do not answer it blocks the family with the
   named class `ebur_r93_daemon_unavailable`, names itself in `failures` (a
   blocked run exits non-zero and can never read as green) and arms no leg.
   Product of the wedge measured in this window (§5).
2. **The module load is retried and its attempts recorded.** A refused
   descriptor load (`[E] … cannot create label`) is an **arm failure** with its
   class, never a semantic.
3. **The own BS.1770 reference is computed over the bytes the arm fed**, not
   over a capture tap, so the tap path is not in the law's critical path. The
   boundary validated the scout's Python reference against the installed
   libebur128 to 1e-6 dB; this fixture re-derives it (K-weighting, −70 LUFS
   absolute gate, −10 LU relative gate) and reproduces the scout's table to
   ≤6e-6 dB (§4).
4. **Every recorded float is JSON-safe** (`allow_nan=False` is the receipt
   law): a non-finite readout is stored as its verbatim literal, and every entry
   is scrubbed on return — one stray `-inf` cost a whole battery once (§5.4).
5. **Expected refusals are claims, not coverage gaps** — the six arms that must
   refuse carry `expect_refusal=True`.
6. **A link is not assumed**: the pre-flight caught two wrong link sides
   (`monitor_*` on a source, `input_*` on a record stream) and one wrong sink
   width (a 1-channel sink under a 2-channel chain) — the ports are named per
   side and per channel count, and the failure classes are recorded (§5.4).

Inherited unchanged: seat-owned `r93a_<pid>` names, the private
`r93arole<pid>` key, a FIXED family lock (the r84 F1 3-seat consensus),
name-verified unloads, bounded process groups, no `set-default-*`.

---

## 4. Offline checks that ran before the battery (not measurements)

1. `python3 -m py_compile corpus/fixtures/measure_audio.py` → OK.
2. **The reference table reproduces the scout's own-reference values**
   (1 kHz/1.0 `-3.003596` Δ0; 1 kHz/0.5 Δ1e-6; 0.25 Δ0; 40 Hz Δ6e-6;
   100 Hz Δ1e-6; 4 kHz Δ0; 10 kHz Δ0).
3. **The arming-logic self-test** (`probes/dev7.py`): the leg runner is stubbed
   and every entry is driven with satisfying rows and with one deliberately
   wrong row. The wrong row is **CAUGHT in all 9 entries**; the green direction
   is clean apart from stub artifacts that exist only because the stub's series
   does not decay/flow. Not a measurement, never recorded as one.

---

## 5. The window: a ~3.4 h host wedge, worked through

### 5.1 Timeline (UTC)

| time | observation |
| --- | --- |
| 05:46–05:52 | the arm works end-to-end; dev legs reproduce the boundary's numbers (plateau `-9.024196`, topology 7/7/0/7, Window-only 152/152 NaN, peaks `0.5/0.0/0.2`, mix `-19.024195`, silent 152/152 `-inf`, hist/hist2 eviction split, the label matrix) |
| ~05:56–05:59 | `pactl load-module module-null-sink` stops returning (a dev leg's sink id comes back empty at its 6 s bound) |
| 09:08 | `pactl info` never returns (killed at 25 s); `pw-dump` → 0 bytes; `pw-cli info 0`, `pw-metadata`, `pw-link -o` still answer |
| 09:14 | my own leaked `pw-cli` (pid 3332803, cwd this worktree, `PIPEWIRE_DEBUG=3`, spinning `R` since 06:08:20, reparented to systemd) found and killed by exact PID — **the wedge persisted** |
| 09:20 & 09:22 | battery attempts #1/#2: the gate blocks (3 attempts, 64.1 s, `pactl_exit -9`, `pw_dump_bytes 0`) |
| 09:18–09:23 | `pw-cli ls Node` intermittently answers; `create-node adapter {factory.name=support.null-audio-sink …}` returns a proxy but **no node appears** (the pactl-free path is closed) |
| **09:24:59** | **the daemon recovers** (`pactl info` OK, `pw-dump` 416 KB) — after ~3.4 h |
| 09:26–10:45 | batteries #3–#7 run against the healthy daemon (§5.4) |

Concurrent, read-only: other seats' lanes were stuck on the same calls (r98's
`pactl list sinks short`/`pw-dump`/`pw-cli ls Device`, an r95-verifier probe,
several `pw-dump` clients parked in `do_epoll_wait`). Load average fell from
~55 to ~7 while the wedge persisted, so it was not load-induced; the pulse
socket was listening with an empty backlog and its threads sat in
`do_epoll_wait`. `[?]` the mechanism is unresolved by this seat.

### 5.2 Hygiene during the wedge

The one residual object was mine: the null-sink node `r93a_in` (node id 249,
ports 211/229) left by a dev leg whose unload fired while `pactl` was already
wedged. It was destroyed natively (`pw-cli destroy 249`, verified: 0 r93a nodes
and 0 r93a ports). `[?]` the pulse *module* may still be listed; it could not be
unloaded while `pactl` was down. No foreign object was created, modified or
removed; no `set-default-*` was issued.

### 5.3 Gate receipts (the blocked attempts)

`corpus/live/runs/20261016T092003125628Z-ebur-r93/` and
`…T092216336849Z-ebur-r93/`: only `ebur_r93_daemon_gate` plus the 17 base
measurements, with `ready: false`, `waited_s 64.1`, `pactl_exit -9`,
`pw_dump_bytes 0`, and the named failure — a loud block, never a silent green.

### 5.4 Four arm bugs the first full run (10:02) exposed, and the fixes

The 10:02 run completed all legs and failed exactly four arms — every one a
*harness* bug, each fixed and re-verified before the green runs:

1. the topology expectation was typed `[7,7,7,7]` instead of `in/out/control/
   notify = 7/7/0/7` (the measurement was already correct);
2. the stereo legs loaded a **1-channel** sink under a 2-channel chain → the
   feed link could not bind (`No such file or directory`); the sink now takes
   the leg's channel count;
3. the `lufs2gain` node was declared as a second **meter** (`label=ebur128`) so
   the graph refused `l2g:LUFS` with `unknown input port` — the helper now takes
   a label and the five l2g sites declare `label=lufs2gain`;
4. the deferred-activation arm demanded the `[E]` pair in *every* rep; the
   activation messages land in the read window only when the window catches
   them, so the pair is now required **at least once per battery** while every
   rep must still load-without-metering.

Also fixed en route: the `post` tap link used `monitor_*` on a **source** (a
source's ports are `output_*`) and the audio-domain ratio used a whole-capture
RMS (dominated by the pre-convergence period where `lufs2gain` still passes the
signal at 1.0) instead of a mid-tone window.

---

## 6. Evidence

- Implementation sha256 (the bytes both green batteries ran):
  **`62e2606ebeb8f1d93aa27f0484b4b252f1787ac8ae86a0035140680257f0ba56`**
  (`corpus/fixtures/measure_audio.py`, +2035/−3).
- **Green battery #1**:
  `corpus/live/runs/20261016T101716935215Z-ebur-r93/measurements.json` —
  9 entries, **90 legs**, `failures: {}`; `coverage_blocked` carries only the
  two honest sub-arms of §2.2.
- **Green battery #2**:
  `corpus/live/runs/20261016T103145603182Z-ebur-r93/measurements.json` — same
  bytes, same nine entries, 90 legs, `failures: {}`, the same three
  `coverage_blocked` sub-arms.
- **Cross-run identity** (the byte-stability the claims lean on): every
  calibration constant is identical across both runs *and* across the reps
  (`-9.024196 ×2`, `-15.044795`, `-15.288830`, `-10.855398`, `-5.753903`,
  `-5.680018 ×2`, `-3.003596`); the K-weighting deltas are identical to 1e-6
  (`-6.264634 / -1.831202 / +3.270293 / +3.344178`); the window decays are
  identical (`0.427 s ×2` and `1.856 s ×2`); all seven port identities are
  `-9.024196`; the mix is `-19.024195`; the same-leg gain residual is `0.0 dB`;
  the peaks are `0.5/0.0/0.2` for both readouts. The history plateaus reproduce
  within the arm's 0.05 dB band (only the rep ordering differs — block phase,
  exactly the boundary's finding).
- Every entry's `stimuli` table carries the 14 member sha256s; every entry's
  teardown carries `sinks_gone`, `own_nodes_after`, `own_procs_after`.

**Read the receipts against these limits:** the C16 envelope is ±1.0 LU; the
window bands are `0.4 → ≤0.8 s`, `2.0 → ≥1.5 s`, `Δ ≥ 1.0 s`; the gain
audio-domain band is ±15 % (and unmeasured in these runs); reps are 2 for the
armed arms and 1 for the seven port identities.

---

## 7. Remaining risks and unmeasured surface

1. **The family cannot measure without the pulse module path + a `pw-dump`
   census** (the driver sink and the chain-port census). The gate makes a
   prerequisite failure loud and bounded; a native `create-node` driver was
   attempted twice as a pactl-free path and did not materialize a node.
2. **`C16`'s envelope is ±1.0 LU** — twice the boundary's observed span
   (−0.529…+0.205). An envelope, not a law.
3. **The window-decay bands are wide** (`0.4 → ≤0.8 s`, `2.0 → ≥1.5 s`,
   `Δ ≥ 1.0 s`) because the boundary's own values spread between conditions
   (0.418–0.426 s quiet vs 1.856–2.025 s load). The measured values happened to
   land exactly on the boundary's (`0.427`/`1.856`), but the arm does not pin
   them.
4. **The audio-domain gain ratio is unmeasured** (§2.2) — the `post` tap is
   silent in the `g_default` shape. C12's law stands on the same-leg residual.
5. **`notify_bogus` refused its load** in both green runs rather than loading
   silently; the control records the class, so the claim ("the notify name is
   load-bearing") holds either way, but the *silent* variant was not re-observed
   on the final bytes.
6. **`Shortterm LUFS` is telemetry**, not a claim: it reads a real value
   (`-9.724301`) — the boundary left that notify name unread.
7. **My own leak** (§5.1) is disclosed: one orphaned spinning `pw-cli` from this
   worktree lived 06:08–09:14 and did not by itself explain the wedge. The
   family's session lifecycle now closes stdin and bounds the wait on every leg,
   and the teardown censuses own processes.
8. **Reps are 2** for the armed arms; a single rep would not carry the
   byte-stability claim, and the byte-stability of the *stereo* dB-mean case is
   explicitly not claimed (the boundary falsified it: a 0.0028 dB rep spread) —
   the arm uses a 0.01 dB tolerance instead.

*author seat — authored, green twice on the final bytes, measured; judgment is
the orchestrator's.*
