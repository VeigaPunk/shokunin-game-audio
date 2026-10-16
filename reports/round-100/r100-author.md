# r100 author — the sofa/spatializer HRTF node: the capstone family

Implementation of the round-100 move: an insertion-only `sofa` family in
`corpus/fixtures/measure_audio.py` (appended after the r95 block, before
`def main()`), wired as `--probe-sofa-r100`, plus one new fixture source,
`corpus/fixtures/r100sofa.py` — the seat's own rig (1175 lines, one leg per
process, `R100AJSON <json>` on stdout). **Nine entries, 37 legs.** Every armed
law is a boundary-surviving claim from `reports/round-100/r100-boundary.md`;
the scout's falsified and re-attributed rows are dropped or re-armed at the
boundary's corrected values.

Seat: **AUTHOR** (leaf; frozen `probeParent` — exactly one read-only `ufo-labrat`
child, advisory, folded §10). Host `plazir27`, window **2026-10-16 09:19Z →
10:38Z** (host local UTC−3). Branch `wt-r100` at `6fcff792`. **Zero commits.**

Host: PipeWire **1.6.8**, WirePlumber **0.5.17-1**, Python 3.14.7, 32 CPUs;
loadavg 5.6 at exit (the shared daemon was contended for the whole seat, §8).
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`.

---

## 0. Headline

1. **The surface is now a battery, not a scout's pins.** Nine entries / 37 legs
   cover the arming shape, the silence-until-fed law, the azimuth ILD law with
   its exact mirror, the 8-point curve, the rate-mismatch ladder, the control
   plane, the transfer law with rig falsifiers, the inert controls, the clock
   ladder, and a shared-graph cross-witness.
2. **The boundary's corrected values reproduce exactly.** The stride-1 recipe
   this family arms (`scout_fine`) returns the boundary's own fine numbers to
   all eight printed decimals: az0 `0.11650992/3`, az90 `0.16278101/0.0957599`,
   az180 `0.09857826`, ILD `4.6084` with az270 `-4.6084` (mirror sum
   `0.000000`). The scout's coarse recipe is recorded, never armed.
3. **The two green runs demonstrate the boundary's §3.1 window-landing verdict
   from the family's own receipts** (`stability.txt`, now a full sweep of all
   37 legs): stride-1 spread is **exactly 0 in 34 of 37 cells** and **≤1.72e-7**
   in the rest; the coarse recipe spreads up to **1.97e-5**. The scout's
   "≤2e-5 across reps" bound is the coarse stride's wobble, and it is encoded as
   a recorded witness instead of an armed claim.
4. **The seat-owned private core and the SHARED daemon agree exactly** — not
   merely to ~1e-7: the shared-graph az90 capture is **byte-identical**
   (`sha256 7a344c25…`) to the private-core az90 capture, with identical
   `0.16278101/0.0957599` and ILD `4.6084`. The boundary's §4.7 "reproduces to
   ~1e-5" is extended by orders of magnitude, and it is what legitimises this
   family's private-core arming.
5. **One author-level defect class was found and fixed before the green runs,
   and it is the most important line in this report**: the first battery
   version armed every law into a list the entry then *overwrote*, so three
   full-battery runs reported `failures: {}` while **no law was enforced at
   all**. §6 is the disclosure, the fix, and the receipted negative control
   that proves the arming is live.
6. **The shared graph is not free**: it leaves 2 `stream-properties` restore
   rows per filter-chain load in the operator's WirePlumber store (the
   disclosed r90/r95 class; 16 rows now, from 8 shared loads across this seat's
   runs). The private-core arming leaves **zero** — the only shape the law
   entries use, with the shared graph kept as a cross-witness.

---

## 1. Files changed

- `corpus/fixtures/measure_audio.py` — **+1484 / −3**. The only deletions are
  the three shared-line splices the wiring requires (mutex `sum([...])` list,
  `mode` select, receipt `suffix`; identical convention to r86–r89/r94/r95).
- `corpus/fixtures/r100sofa.py` — **new**, 1175 lines. The rig: bounded
  children (own session, `RLIMIT_CORE=0`, byte-capped), an interactive `pw-cli`
  session for the module, own WAV I/O, three analysis recipes, the seat-owned
  private-core mode, namespace-scoped sweep and name-verified unloads.
  Self-contained on purpose: it does **not** import the r92-scout `pwlib`
  scratch helper that both the r100 scout and boundary rigs imported, so a
  verifier can run it from tracked bytes alone.
- `corpus/live/measure_audio-sofa-r100.lock` — fixed-path family lock, created
  at runtime (untracked; the r84 F1 3-seat consensus, never `$TMPDIR`).
- `corpus/live/r100-author/` — this seat's receipts (`RECEIPTS.md`,
  `run-{1,2}.measurements.json`, `run-log.txt`, `stability.txt`,
  `negative-control.json`, `exit-census.json`, `manifest.sha256`).
- `corpus/live/runs/20261016T*-sofa-r100/` — eight full-battery receipts (six
  pre-fix/RED/superseded, two green on the frozen bytes).
- `reports/round-100/r100-author.md` — this file.

Nothing committed. `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
is the interpreter's build artifact and was already tracked-dirty at entry, as
the r100 scout and boundary both recorded.

## 2. Conventions carried over

- Namespace `r100a_<pid>` for every node, sink, client and module description;
  the private-core sandbox adds no name outside it.
- Fixed-path lock `corpus/live/measure_audio-sofa-r100.lock` (flock); `TMPDIR`
  honoured for every sandbox and capture.
- Name-verified teardown: the driver sink is unloaded only through an index
  re-read from the module table immediately before firing and required to carry
  our own `sink_name=`; a recycled index is a failure, not a warning. A
  `pw-cli`-loaded filter chain is **client-local** — it never appears in the
  global registry — so its unload is verified against the session that loaded
  it *and* against the own-namespace nodes it created, re-censused after the
  unload (§7.2).
- Never `pactl set-default-sink` / `set-default-source` in this family; every
  child is its own session leader bounded by SIGTERM→SIGKILL process-group
  escalation. (For precision: the file contains exactly one
  `set-default-sink` invocation, in the **pre-existing r78 lattice** around
  line 7088, with its own restore path — this change neither touches nor adds
  one, and `grep '"set-default'` over the r100 family returns nothing.)
- Volatile text (ids, serials, uuids, wall times, loadavg, capture shas, window
  offsets, foreign node names) is recorded, never armed.
- r100-local error classes are checked before the inherited tables
  (`sofa_r100_no_fixture`, `sofa_r100_no_sofa`, `sofa_r100_leg_error`).
- A missing binary, a core that will not come up, a leg with no JSON, a silent
  shared take, or a graph reader that does not answer is a **named coverage
  block**, never a silent green.

## 3. The boundary-surviving claims, armed and measured

Measured values are green run 2. "FINE" = the stride-1 recipe, "COARSE" = the
boundary's own published recipe.

| boundary verdict (§2/§3/§4) | armed law | measured |
| --- | --- | --- |
| ports/shape CONF (136/136) | exact capture-side `{monitor_MONO, playback_MONO}` and playback-side `{output_FL, output_FR}` port sets; every link `rc 0` on `tries: 1` | exact in every leg of both runs |
| no-config CONF-L: load OK → activation `-22` → pure silence | `spatializer: no config was given` + `can't start graph` + `(-22)`, `n_samples` null, rms 0.0 **with frames > 0** | all present; frames 177152, rms `[0.0, 0.0]` |
| instantiate CONF: `using n_samples:512 …` | `n_samples` armed as the scaling law `ceil(512·fc_rate/44100)` | 512 / 558 / 1024 / 1115 at 44100 / 48000 / 88200 / 96000 |
| rate mismatch CONF+EXT: not refused, IR resampled, ILD survives | non-silent both channels + COARSE ILD band ±0.02 | 48000 `4.6163`, 88200 `4.6157`, 96000 `4.6176` (FINE `4.6119/4.6133/4.6153`) |
| the rate string is not reached | `Only the same sampling rate supported` absent from every leg's log | absent in all 37 legs |
| azimuth law CONF-L: 0 / +4.612 / −4.612 / 0 | FINE ILD `0.0 / 4.6084 / −4.6084 / 0.0` ±0.01; 2 reps per cardinal | `0.0`, `4.6084`, `−4.6084`, `0.0`; mirror sum `0.000000`; FINE rms `0.11650993 / 0.16278101 / 0.09857826` |
| front/back is spectral CONF+EXT: −1.4517 dB @440 | ratio az180/az0 ±0.05 dB, L == R | `−1.4516` dB, L == R |
| 997 Hz flips the SIGN EXT: +2.34 dB | ratio ±0.05 dB | `+2.3397` dB, L == R |
| not a pass-through CONF+EXT: −9.6421 dB | reference tap band + az0/ref, az90 L/ref, R/ref ±0.05 dB | ref `0.35369453` (tone `0.50043379`); `−9.6423`, `−6.7386`, `−11.3466` dB |
| channel swap EXT: −4.612 | swapped FINE ILD == the az270 value ±0.01 | `−4.6084` |
| gain is exactly linear EXT | FINE rms ratio to base within 1e-4 | `0.50000071` (gain 0.5), `2.00000141` (gain 2.0) |
| Radius ladder FALSIFIED (inert) | radius 0.5 / 3.0 identical to base within 1e-5 | identical (`0.16278101/0.0957599`, ILD `4.6084`) |
| Elevation IS effective EXT | az0/el90 FINE rms band, ILD 0 | `0.10322302`, ILD `0.0` |
| `default.sofa` is a symlink RE-ATTR | sha256 equality + realpath equality + identical output | `2768ac84…57e28` both, realpath `MIT_KEMAR_normal_pinna.sofa`, output identical |
| quoted token silently drops `control` NEW | read-back `s0:Azimuth == 0.0` with 90 requested + az0 signature | read-back `0.0`, ILD `0.0`, rms == az0 |
| runtime control change EXT | read-back `0.0 → 90.0`, rc 0, and the 100 ms ILD series steps | `0.0 → 90.0`; series `0.0 … 2.3823 → 4.6118 ×3 → 4.5375 … 0.0` |
| clock invariance EXT (§4.7) | FINE ILD preserved within ±0.02 dB across server quantum and rate | `q512 4.626`, `q2048 4.6084`, `r96000 4.6176`; live settings witness `clock.quantum 512/2048`, `clock.rate 96000` |
| teardown clean CONF (136/136) | per-leg `post_sweep.clean`, driver unload `rc 0` with no recycled index, no FC node surviving the module unload | clean in all 37 legs; 0 own processes / sandbox dirs / cores after |
| ≤2e-5 stability bound FALSIFIED as a cross-process claim | **not armed**; the coarse recipe is recorded, the fine one armed | fine spread ≤1.72e-7, coarse spread ≤1.97e-5 across the two runs |
| WAV bytes differ / 1 LSB CONF+RE-ATTR | not armed; per-leg capture sha256 + frames recorded | 28 of 37 captures byte-identical across runs; 9 differ, 3 of them in frame count |
| scout's n=1 rate-mismatch value | re-armed at n ≥ 3 (48000 ×3) | `4.6163/4.6138/4.6138` COARSE |

### 3.1 Law-table provenance (exact, after a labrat attack forced the split)

The armed centres are **not** uniformly "the boundary's own number", and the
family now says so in the code comment and in every receipt
(`law_provenance`). The split:

- **boundary-published, to the precision the boundary printed**: the FINE ILD
  `4.6084 / −4.6084 / 0.0`, the FINE rms `0.11650992 / 0.16278101 / 0.0957599 /
  0.09857826` (the boundary's `scratch/{window-landing,fine-ild}.json` carry
  them to 8 decimals), the 440 Hz front/back `−1.4517 dB`, and `n_samples`
  `512 / 558 / 1115`;
- **this seat's first-run centres, because the boundary's receipts store
  `ild_db` to only 3 decimals** (`axes-azcurve.json`: 3.465 / 4.195 / 4.612):
  `SOFA_R100_COARSE_ILD` and `SOFA_R100_MISMATCH_ILD` carry a 4th decimal this
  seat measured, each inside the boundary's 3-decimal value at the armed band;
- **this seat's fine-recipe centres where the boundary published a
  coarse-recipe number**: `ELEV90_RMS` (this seat's fine `0.10322302`; the
  boundary's coarse `0.10320148` is inside the band) and `XFER.az0_db` (this
  seat's `−9.6423`, recomputed from its own reference-tap pair; the boundary's
  published `−9.6421` is also inside the band, and **neither** recomputes from
  the boundary's printed rms pair, which gives ≈`−9.646` — an unresolved 2e-4
  ambiguity carried openly, not resolved by widening the band);
- **an admitted extrapolation**: `N_SAMPLES[88200] = 1024 = ceil(512·88200/
  44100)` — the boundary lost that leg; this seat measured 1024 in both runs.

## 4. Entries and legs

1. **`sofa_shape_r100_probe`** (2 legs) — `s_shape` (ports, links, load,
   `n_samples`, peak/nonzero bands, rate-string absence) and `s_unfed` (the
   chain loaded and linked but never fed: rms exactly 0.0 **with frames > 0**,
   which is why the no-config cell can never be gated on `rms == 0`).
2. **`sofa_azimuth_r100_probe`** (7 legs) — az0 ×2, az90 ×2, az270 ×2, az180 ×1;
   the FINE ILD law, the mirror (ILD and rms), the az0/az90/az180 FINE rms
   bands, and the 440 Hz front/back spectral offset.
3. **`sofa_curve_r100_probe`** (4 legs) — az45/135/225/315 armed on the COARSE
   recipe the boundary published them from, plus the mirror pairs 45↔315 and
   135↔225 (measured sums `−0.0002` and `0.000000`).
4. **`sofa_rate_r100_probe`** (5 legs) — 48000 ×3 (the boundary's n=1 cell needs
   reps), 88200 ×1, 96000 ×1; the `n_samples` scaling law, the COARSE ILD
   bands, non-silence, and the absent rate string.
5. **`sofa_control_r100_probe`** (3 legs) — `c_props` (the Props param exposes
   `s0:Azimuth/Elevation/Radius` on the capture-side node and **nothing** on the
   playback-side node), `c_runtime` (a live `set-param` on a RUNNING node, with
   a 100 ms ILD series), `c_quoted` (the silent control drop).
6. **`sofa_transfer_r100_probe`** (7 legs) — reference tap at az0 and az90, the
   channel swap, 997 Hz at az0/az180, gain 0.5 and 2.0.
7. **`sofa_inert_r100_probe`** (4 legs) — radius 0.5/3.0, elevation 90, and
   `default.sofa`; plus the host file identity (symlink, sha256, realpath).
8. **`sofa_clock_r100_probe`** (3 legs, 3 private cores) — q512, q2048, r96000;
   each variant's live `pw-metadata -n settings` rows are recorded, and the
   private session-manager log is asserted to contain **0** `alsa` lines (no
   hardware monitor was ever enumerated).
9. **`sofa_shared_r100_probe`** (2–3 legs) — the shared-graph cross-witness: it
   probes `pw-dump` once; when the daemon answers it measures the same laws on
   the shared graph, and when it does not it records a **named coverage block**
   with the evidence. This round it answered and the entry measured.

## 5. Evidence

- Implementation sha256 (both green runs identical bytes):
  `measure_audio.py e965f56ce12536b80895b62d1fdac096b2d1e32d00ea7e2c9d7089317313bed7`,
  `r100sofa.py 26e966601abf5d1d784842b192fa3e2d7e299538b832702f7124c90a3f227481`.
- Run 1: `corpus/live/runs/20261016T103052642013Z-sofa-r100/measurements.json`
  — 9 entries, **37** legs, fixture wall 397.9 s, `failures: {}`,
  `coverage_blocked: {}`.
- Run 2: `corpus/live/runs/20261016T103758962243Z-sofa-r100/measurements.json`
  — 9 entries, **37** legs, fixture wall 397.6 s, `failures: {}`,
  `coverage_blocked: {}`.
- The canonical battery is untouched: `python3 corpus/fixtures/measure_audio.py`
  (no probe flag) → `20261016T102052126803Z-normal`, exit 0, `failures: {}`.
- `corpus/live/r100-author/` carries the copies, the run log (all eight
  full-battery runs including the pre-fix and RED ones), the full stability
  sweep, the negative control and the exit census, with `manifest.sha256`.
- Exit census: **0** `r100a` processes, **0** sandbox directories, **0** private
  cores or session managers, **0** `r100a` nodes and **0** `r100a` modules in
  the shared graph; the family lock is released. The shared clock settings this
  seat never wrote are unchanged (`clock.rate 48000`, `clock.quantum 1024`,
  `clock.force-quantum 0`, `clock.force-rate 0`).

## 6. The arming-live incident (found, fixed, receipted)

### 6.1 What happened

The first version of every entry ended with `entry["failures"] = failures`,
where `failures` was a **fresh local list**, while every law helper appended to
`entry.setdefault("failures", [])` — a *different* object. The final assignment
therefore discarded every law failure the entry had recorded. Only failures
raised through the teardown path (which appends to the caller's list) survived.

Three consecutive full-battery runs printed `failures: {}` on that code. They
were **not** evidence that the laws held; they were evidence that the laws were
never read. This is the silent-green class the seat card names, and it was found
by auditing the plumbing rather than by trusting the green.

### 6.2 The fix

Every entry now binds the local name to the entry's own list —
`failures = entry.setdefault("failures", [])` — so the helpers and the published
field are the same object (9/9 entries, independently re-checked by the labrat,
§10 H2). The RED run that followed immediately reported three **real** defects
the clobber had hidden:

1. the shape entry read `frames`/`peak`/`nonzero` from inside a *recipe*
   instead of from the analysis level (4 laws);
2. the `default.sofa` identity law compared a misspelled key
   (`default_sha256` instead of `default_sofa_sha256`), so it compared `None`
   against the real digest;
3. the shared-graph az90 leg produced a **silent take** (the r98 §3.5 /
   boundary rig-flake class on a graph this seat does not own).

Fixes: the analysis-level reads; the corrected key; a one-retry policy for a
silent shared take with a **named coverage block** if both attempts are silent;
and, in the fixture, the boundary's own retry rule — retry on `frames == 0`,
**never** on `rms == 0` (the no-config cell is legitimately silent with
frames > 0).

### 6.3 The receipted control

`corpus/live/r100-author/negative-control.json` — on the **frozen bytes**, the
predeclared law table is perturbed in memory (az0/az180/az270 ILD → 9.0, az90 →
0.0, all FINE rms → 0.5, `n_samples` → 999) and the same entry code path is
required to report failures: **21 failures, verdict `ARMING LIVE`**. The green
receipts are therefore read against a code path that demonstrably fails when it
should.

## 7. Author-level corrections found while encoding (new)

1. **The shared graph writes the operator's store; the private core does not.**
   Every shared-graph filter-chain load leaves exactly **2** rows
   (`…r100a_<pid>_sofa\sinput` / `\soutput`) in
   `~/.local/state/wireplumber/stream-properties`, written by the operator's
   WirePlumber; the family records them and does not gate on them (the disclosed
   r90/r95 class). The private-core arming leaves **zero** (verified twice: a
   whole-battery delta of 0, and every private entry's
   `stream_properties_own_rows: []`), because `XDG_STATE_HOME` is redirected
   into the sandbox. That asymmetry is now an explicit part of the teardown law:
   hard on the private core, recorded on the shared graph.
2. **A `pw-cli`-loaded module is client-local.** It never appears in `pw-dump`
   or `pw-cli ls Module` — only the daemon's own modules do — so "verify the
   module index before unload" cannot be satisfied against a global table for
   this family. The verification is re-specified: the unload must be issued in
   the session that loaded it, must be preceded by a re-read of the
   own-namespace nodes the module created, and must be followed by a re-census
   showing no `_sofa_in`/`_sofa_out` node surviving.
3. **The server quantum is visible in the stride-1 ILD.** At `q512` the fine ILD
   is `4.626` against `4.6084` at `q2048` and `4.6176` at a 96 kHz server rate —
   a `+0.0176 dB` excursion the boundary's coarse recipe could not resolve (its
   sandbox table shows `4.612` for every variant). The clock claim is armed and
   worded as **"preserved within ±0.02 dB"**, not "identical"; the band is the
   mismatch tolerance, and the largest deviation sits within 12 % of its edge.
4. **The clock ladder now has a live witness.** `pw-metadata -n settings` during
   the leg reports the *running* graph's `clock.quantum` (512 / 2048) and
   `clock.rate` (96000) per variant, so the variant is witnessed by the graph
   itself and not only by the config drop-in that declared it.
5. **The shared graph reproduces the private core *exactly*.** Not ~1e-5 and not
   merely ~1e-7: the shared az90 capture is byte-identical to the private-core
   az90 capture (`sha256 7a344c25…`), with the same `0.16278101/0.0957599` and
   ILD `4.6084`. The boundary's §4.7 sandbox comparison is extended to the
   strongest form this rig can express.
6. **The window-landing verdict is demonstrated by this family's own runs.**
   Across the two green runs, over all 37 legs: stride-1 spread exactly `0` in
   **34** cells, worst `1.717e-07` (`az0_r0`); coarse spread worst `1.966e-05`
   (`c_props`), with `az0_r0` at `1.97e-05`. Capture bytes: **28 of 37**
   byte-identical, 9 differing, 3 of those in frame count only (pw-record's
   1024-frame quantization) — the boundary's §3.2 finding, reproduced.
7. **The `default.sofa` symlink is re-confirmed** on this host:
   `sha256 2768ac841213a7ae11d1ea7fd0f25a69b39216102dc5dd913ea6ba0f0dc57e28`
   for both paths, `realpath` = `MIT_KEMAR_normal_pinna.sofa`, identical
   binaural output. There is still exactly one HRIR corpus here.
8. **The rig-flake class is real on the shared graph**: one of the shared-graph
   az90 attempts came back silent with frames > 0, while no private-core leg
   ever did. The retry recovered it, and the silent row is kept in the receipt
   next to the armed one.

## 8. Environment deviation (disclosed, not hidden)

The family arms its laws on a **seat-owned private PipeWire core plus a private
WirePlumber profile with no hardware monitors** (the boundary's §4.7 sandbox
shape), and keeps the shared graph as a cross-witness entry. Reasons, in the
order they were established:

1. At seat entry the **shared daemon could not serve a fresh `pw-dump`**: 0
   bytes in 30 s, three times, while `pw-cli ls` and `pw-link` answered
   normally. The proven r100 rig shape (the scout's and the boundary's) depends
   on `pw-dump`.
2. **Two foreign clients were wedged alive in the shared graph** — a `pw-dump`
   (pid 3224758) and an `r95rjack` (pid 3357353). They are foreign: this seat
   counted them, never signalled them. Against a fresh private core the same
   `pw-dump` returned 22 835 bytes immediately, so the wedge was the shared
   daemon's state, not the client binary.
3. The wedge cleared later in the seat (the shared entry then measured 94
   objects), which is exactly why the cross-witness entry exists: it is
   adaptive, and it records a named block instead of a green when the daemon
   does not answer.

Consequences, all recorded: no `r100a` object is ever created on the shared
graph by the law entries; the private session manager is asserted to log **0**
`alsa` lines (no operator device is enumerated or opened); the operator's
WirePlumber store is never written by the private-core entries; and the
clock-invariance entry is the in-round proof that the private core reproduces
the shared graph.

## 9. Remaining risks / blockers

- **None blocking.** Honest exposures, recorded rather than hidden:
  - **The shared daemon is not this seat's to control.** Its policy, its
    contention and its wedged clients changed twice during the seat. The
    cross-witness entry adapts; the laws do not depend on it.
  - **The clock law is a ±0.02 dB band, not an identity** (§7.3), and the band
    is borrowed from the mismatch tolerance: the `q512` leg sits at `+0.0176`
    dB in both green runs, i.e. 12 % inside the edge.
  - **The `n_samples` scaling law is armed as `ceil(512·fc_rate/44100)`**, which
    fits 512/558/1024/1115 exactly. It is a fit to four points of one plugin
    build on one host; another build's rounding could differ.
  - **The transfer law carries a 2e-4 ambiguity** (§3.1): the boundary's
    published `−9.6421 dB` does not recompute from its own printed rms pair
    (≈`−9.646`). The family arms this seat's own measured `−9.6423` with a
    ±0.05 dB band and records the discrepancy rather than resolving it.
  - **Capture bytes are not kept.** Per-leg WAVs live in a temporary sandbox and
    are removed at entry end; the durable record is the receipt's
    `analysis.sha256`, `frames`, and per-recipe `rms`/`tone`/`win_offset`
    (disclosed in `RECEIPTS.md`).
  - **The operator's store carries 16 `r100a` rows** (8 shared-graph
    filter-chain loads × 2) from this seat's runs. No CLI deletes them — the
    r90/r95 class stands, and this seat's *law* entries added none.
  - **No perceptual or spatial-audio-quality claim is made anywhere in the
    family.** ILD and single-bin magnitudes are energy proxies. The SOFA file's
    own metadata says "No license provided, ask the author for permission": it
    is used as a test fixture only, and clearance stays with the operator.
  - **Bounded to this host**: PipeWire 1.6.8 +
    `libspa-filter-graph-plugin-sofa` + one HRIR file + one machine.

## 10. Labrat fold (frozen `probeParent` — exactly one read-only child, advisory)

One read-only `ufo-labrat` was dispatched against this seat's own artifacts with
six predeclared attacks. **Toolset limit disclosed: read/grep/glob only — no
exec**, so it could not re-run a leg; it attacked the receipts, the law table
and the rig source. It created no artifacts and touched no PipeWire object.

| attack | verdict | what it found, and what this seat did |
| --- | --- | --- |
| **H1** law-table fidelity | **SUPPORTS with exceptions** | Traced 8 constants exactly to boundary artifacts (FINE ILD/rms to 8 decimals from `scratch/fine-ild.json` and `window-landing.json`; `n_samples` 512/558/1115 from `fc_log`; front/back −1.4517). **But** it showed the 4-decimal `COARSE_ILD`/`MISMATCH_ILD` centres exist nowhere in the boundary's receipts (which store 3 decimals) — they are *this seat's* measurements — and that `ELEV90_RMS` (0.10322302 vs boundary 0.10320148) and `XFER.az0_db` (−9.6423 vs published −9.6421) are this seat's fine-recipe values, with the boundary's inside the band. It also flagged `N_SAMPLES[88200]` as an extrapolation. **Acted on:** the code comment now states the provenance split exactly, and every receipt carries a `law_provenance` block (§3.1); the two superseded green runs were replaced by two fresh green runs on the corrected bytes. |
| **H2** arming live | **SUPPORTS** | Verified all 9 entries bind the same list object the helpers append to, that the armed checks read fields that exist at the analysis level, and that `negative-control.json` fires 21 failures with verbatim law strings. |
| **H3** two runs, one byte-set | **SUPPORTS (b), UNRESOLVED (a)** | (a) it could not re-hash without exec — the frozen shas are the author's own claim, and the receipts record no fixture sha; disclosed in §5 rather than papered over. (b) it recomputed the spreads and found the **az45 coarse scatter (1.25e-5) missing from the first `stability.txt`**, and that the fine worst case is 1.72e-7, not "≤1.7e-7". **Acted on:** `stability.txt` is now a full 37-leg sweep, the wording is corrected, and the file records why it changed. |
| **H4** shared cross-witness | **SUPPORTS** | Confirmed the silent first attempt is recorded next to the armed retry, and that the shared az90 capture is **bit-identical** to the private-core one. **Acted on:** §0/§7.5 upgraded from "~1e-7" to "byte-identical". |
| **H5** operator store | **SUPPORTS** | Counted the `r100a` rows in the operator's store and matched them to `exit-census.json` and to the 2-rows-per-shared-load rule. |
| **H6** clock disclosure | **SUPPORTS** | Confirmed the armed ±0.02 dB is equal to what the receipts support, with the `q512` deviation at 12 % of the edge, and noted the band is borrowed from the mismatch tolerance. **Acted on:** §7.3 and §9 say exactly that. |
| **extra** | — | It also flagged that the boundary's own `−9.6421 dB` does not recompute from the boundary's printed inputs, and that `shared_graph_pwdump.bytes` differ across runs from ambient foreign churn. Both are recorded (§3.1, §9); neither is a defect of this family. |

Net: **six attacks, one SUPPORTS-with-exceptions and five SUPPORTS**, and three
artifacts were changed because of it (the law-table comment + `law_provenance`,
the stability sweep, and the wording in this report). The child was advisory and
edited nothing.

*Leaf seat — implemented, measured, and green on frozen bytes; not judged.*
