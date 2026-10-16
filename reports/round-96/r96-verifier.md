# r96 VERIFIER — frozen-tree gate on committed `7358f13b` (the pulsecli family)

Seat: **verifier** (non-author, audio-shokunin r96). Lane
`~/Projects/shokunin/audio-shokunin`, basis **`git archive HEAD`** taken at
**2026-10-16T10:00:5xZ** (local UTC−3 07:00) when `git rev-parse HEAD` read
**`7358f13bf0c1733f7f68339ebf787e66b851f011`** — the committed bytes, **not**
the worktree — extracted to **`/home/vgpnk/r96v/tree`** (the "archive to
/home" instruction; the archive is the only copy of this basis — see §1).
Window **10:01:00Z–10:14:35Z**; loadavg **2.98–5.5** at run starts, 32 cores.
Toolchain: Python **3.14.7**, gcc **16.2.1**, `libpulse` **17.0-98-gb096**,
numpy 2.5.3; `TMPDIR=~/Projects/shokunin/tmp`. **Zero tracked writes, zero
commits, zero pushes, no `set-default-*`**; every artifact under
`/home/vgpnk/r96v/` plus the small evidence copies in
`corpus/live/r96-verifier/` (untracked). The frozen `probeParent` slot
spawned **exactly one** read-only `labrat` (§3.3).

## 0. Verdict

**PASS on committed bytes.** The author's 178 legs re-derive green on a frozen
tree this seat built itself, twice, and every control is live and sensitive:
an unresponsive-server mutation turns the whole receipt into **308 named
BLOCKED cells — no leg cell reads green** (the only 3 PASS cells are receipt
identity: the mode and the two cross-checks), an instrument-build mutation
blocks the cork entry by name, a parse-law mutation reddens **exactly the two
`+`-prefixed cells** (fixture and this seat's independent law set name the
same two), an instrument-report mutation reddens exactly the two `−16` legs,
and all **11 receipt forgeries** are caught by field re-derivation (1 no-op
control).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive HEAD` @ 7358f13b | tar sha256 `5a6a10007560163db43881a9e98bfe3a49c123c247f38f42bcb5ffd1b754a6f4` (3 318 476 800 B); **44 579 files / 11 772 dirs / 0 symlinks**; file-set symdiff vs `git ls-tree -r 7358f13b` = **0** | PASS |
| fixture identity | committed blob | tree `measure_audio.py` sha256 `97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc` = `git show 7358f13b:…` = the r96-integrate merged sha; `pulse_r96_probe.c` `fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c` | PASS |
| instrument build from committed bytes | reproducible | `gcc -O1 … -lpulse -lm` rc 0; binary sha256 **`c3fc4cefed41157e7eac22e0a399ae232e7dfc4e695657ce0ed00b2ca2a46433`** — **identical to the author's recorded build**; `-fsyntax-only -Wall` clean; `py_compile` rc 0 | PASS |
| fresh runs on committed bytes | green | **2/2 green**: `20261016T100323631707Z-pulsecli-r96` (143 s), `20261016T100600813942Z-pulsecli-r96` (143 s); 178 legs, `failures {}`, stderr empty, 2 named blocks | PASS |
| declared leg census | 178 | **178** measured, per entry 41/27/68/20/22 — the author's table exactly | PASS |
| law re-derivation | own laws | **509 cells × 2 receipts**: 507 PASS / **0 FAIL** / 2 BLOCKED each; the attr set re-derived from **this seat's own transcription of the committed C law** | PASS |
| independent live re-derivation | own code/argv | **23/23 PASS** (`runs/r96v_live.py`): 8 attr cells vs own prediction, instrument `rc=−16`×10, cork flow gate **71 677 nonzero frames** (the fixture's own number), trigger negative 0, bogus-host wall 7.83 s | PASS |
| gate mutation — dead endpoint | named block, never green | 5/5 entries `coverage_blocked`, **0 legs**, `failures {}` **rc 0**; this seat's law set: **3 PASS (receipt identity only) / 308 BLOCKED / 0 FAIL** | PASS |
| build mutation — unbuildable instrument | named block | cork entry blocked by name (`#error` echoed), other 4 entries green (156 legs); law set 446 PASS / 63 BLOCKED / **0 FAIL** | PASS |
| parse mutation — `+` accepted | pinned red | fixture reddens **exactly** `t_parse_2b313030__r{1,2}` (`+100`) and `t_parse_2b30783634__r{1,2}` (`+0x64`), 12 failures; law set reddens the same **2 cells** (8 cells) | PASS |
| instrument mutation — fake `rc=0` | pinned red | fixture: `e_latency_query__r{1,2} did not return -16 … ([0])`; law set: the same 2 cells + the 2 build-sha cells (mutated bytes) | PASS |
| receipt forgery suite | caught | 11/11 fabrications caught by the exact cell; 1 no-op control clean (§5.2) | PASS |
| cross-run drift | armed constants stable | **16 385 leaf comparisons, 1 163 raw differences — 0 in the armed-constant set**; residuals are identity/timing/census classes (§6) | PASS |
| custody / hygiene | exit census clean | 0 `r96`/`r96a` modules, sinks, sources, sink-inputs, source-outputs, nodes, processes; defaults + clock props unchanged | PASS |
| zero tracked writes | none | `git status --porcelain --untracked-files=no` = **0 lines**; this lane is untracked-only | PASS |

## 1. Frozen tree

`git archive HEAD -o /home/vgpnk/r96v/head.tar` (1.9 s, 3 318 476 800 B,
sha256 `5a6a1000…`), extracted (`tar -xf --one-top-level=tree`, 2.4 s) to
`/home/vgpnk/r96v/tree`. Census 44 579 files / 11 772 dirs / 0 symlinks;
file-set symdiff against `git ls-tree -r 7358f13b --name-only` = **0**
(`runs/head.tar.sha256`; the tree is not a git repo, so no write can be
tracked by it). `python3 -m py_compile corpus/fixtures/measure_audio.py` rc 0.

**Basis drift after the archive (disclosed).** HEAD advanced twice inside this
window — `b8ff4efc` "r97 author: wppol … (+2156/−3)" at **07:01:30** and
`a2c6e3b7` "r90 adjudicate …" at **07:14:28** — so the worktree fixture is now
sha `7a070fa8…` (blob `125e4d6c…`, 47 424 lines) and **no longer carries the
r96-only bytes**. The frozen tree still does: its fixture sha equals
`git show 7358f13b:corpus/fixtures/measure_audio.py | sha256sum`
(`97ed1b1c…`), re-verified after HEAD moved. A gate run from the worktree at
any time after 07:01:30 would **not** have tested the r96 landing.

**Tracked witness material present in the tree** (this is what makes the gate
self-contained): `corpus/live/r96-scout/sources/pipewire-1.6.8-module-protocol-pulse-pulse-server.c`
(sha256 `0d3ce77dc4f775ca59880e887e6ad9579f651dd7407a8572e09f74267689eefa`,
= its `FETCHED-SOURCES.sha256` manifest) and the r96 boundary/scout receipts.
The author's untracked scratch was absent — every run below rebuilt its own
stimuli and its own instrument.

## 2. Fresh runs on committed bytes

| run | receipt | start→end (UTC) | wall | loadavg | legs | failures | blocks |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | `…/runs/20261016T100323631707Z-pulsecli-r96/measurements.json` | 10:01:00→10:03:23 | 143 s | 3.06/4.76/9.53 | 178 | `{}` | 2 |
| B | `…/runs/20261016T100600813942Z-pulsecli-r96/measurements.json` | 10:03:37→10:06:00 | 143 s | 5.52/5.30/9.00 | 178 | `{}` | 2 |

Per-entry: `pulsecli_avail_r96_probe` 41, `pulsecli_target_r96_probe` 27,
`pulsecli_attr_r96_probe` 68, `pulsecli_props_r96_probe` 20,
`pulsecli_cork_r96_probe` 22. Each entry carries a bounded `server_gate`
(`pactl info`, rc 0, 2–4 ms), `sinks_gone` all true, `unloads` verified
(`captured == verified_index`, `recycled: false`, rc 0), `own_nodes_after: []`.
A bounded `pactl info` was run by hand immediately before each run
(`preflight-pactl-info*.txt`, rc 0) — the daemon had been restarted at 06:24
local and answered throughout.

The two named blocks are the author's own: `e_native_corked rep 1/2` — the
pulse reply reports `Corked=True` while the live node state is
`running→running` (rep 1) and `suspended→running` (rep 2). Nothing else in
either receipt is non-green.

**Shared-host concurrency (disclosed, not hidden).** Run B ran concurrently
with a **foreign `--probe-pulsecli-r96` instance** from the repo worktree
(pid 758323, receipt `corpus/live/runs/20261016T100425297878Z-pulsecli-r96/`);
run B's entry heads censused `r96a_758323_*` nodes (3 in `avail`, 2 in
`target`/`attr`, 2 in `props`, 2 in `cork`). A foreign lane also **moved the
server's default source** mid-window (`alsa_input…Line__source` →
`r91a_src_783057` → later back), visible in run B's recorded `pactl info`
text; the **default sink** (the one the r96 legs depend on) never moved. The
armed set was unaffected: all 178 legs green in both runs and **zero
armed-constant drift** across A/B (§6). Sibling r92/r97/r100 lanes were live
throughout (`host_is_quiet: False` in every entry).

## 3. Law re-derivation — `runs/r96v_laws.py` (509 cells × 2 receipts)

Two sources of truth, both **outside the fixture's Python**:

1. **This seat's own transcription of the server-side law**, written from the
   committed C: `fix_playback_buffer_attr` + `clamp_latency`
   (`pulse-server.c:418–525`, incl. `frac_to_bytes_round_up`, `load_defaults`
   `256/48000`, `960/48000`, `96000/48000`, `quantum_limit 8192`,
   `MAXLENGTH 4 MiB`, the **modulo** `SPA_ROUND_DOWN/UP`) plus
   `patch_buffer_attr` (`pulse/stream.c:997–1028`). It recomputes all six
   fields (`tlength`, `prebuf`, `minreq`, `maxlength`, `latency_num/denom`)
   from `(latency_ms, process_ms, PULSE_LATENCY_MSEC, frame)` and is compared
   **twice per leg**: against the fixture's `predicted` and against the
   **measured** `attrs_after_resnapshot`.
2. **This seat's own `pa_atou`** (leading space/`+`/`−` rejected, leading
   zeros stripped unless lowercase `0x`, full-string check, UINT32 bound,
   `ms ≤ 0` ignored) checked against the 17-cell `env_ms` lattice ×2 reps.

Coverage: the 13-family server lattice (rc + error class per rep), the
pacmd-equivalence refusals, the symlink/sha/bin claims, the targeting lattice
(landed index vs the receipt's own seat index; literal `target.object` on every
miss; the capture-miss asymmetry + its census), the 66 attr cells, the property
lattice (incl. last-wins in **both** argv orders and the restore-row
suppression), and the cork/trigger/prebuf/record/latency/subscribe/native
surface — plus structural laws (per-entry leg counts, unload verification,
`own_nodes_after`, foreign census) and two receipt-level cross-checks that
compare the **derived** red/blocked sets with the receipt's own lists (the
lists are never a law input).

| receipt | legs | cells | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- | --- |
| A (green) | 178 | 509 | **507** | 0 | 2 |
| B (green) | 178 | 509 | **507** | 0 | 2 |

Headline re-derivations (both runs identical unless stated): `t_default`
192000/190082/1920/4194304/8192; `t_env_10` 1536/1026/512/…/256; `t_maxlength`
4177920/4176002/1920/…/8192; `t_s24_default` 288000/**285123**/2880/**4194303**
(the modulo falsifier — a mask reading would give 285120/4194304);
`t_env250_flag100` 13920/12002/1920/…/5040 (env beats flag); the 17 parse cells
including `0X64`→invalid and `0100`→100. `late_attr_census` 1/66 (A) and 2/66
(B) — recorded, never armed. `capture_miss_census` 3/3 refused, 0 hung (both).

### 3.3 The two BLOCKED cells — the labrat probe

The frozen `probeParent` slot dispatched **one** read-only `ufo-labrat` probe
on the single falsifiable claim behind the only named block:

> H: the `Corked:` field `pactl list sink-inputs` reports for a **native**
> (pw-play) stream is the pulse server's **cached** manager-object state
> (`dev_info.state != STATE_RUNNING`), not the live node state, so it can read
> `true` while the node is stably `running`, and such a stream carries no
> `pulse.corked` property.

**Verdict: SUPPORTED**, and this seat re-verified the citations directly:
`fill_sink_input_info` reads the cached manager object
(`get_device_info(o, &dev_info, …)` at **:4116**), then
`if (pulse.corked prop) corked = spa_atob(str); else corked = dev_info.state != STATE_RUNNING;`
at **:4129–4132** (mirror for source-outputs :4213–4216); `pulse.corked` is
only ever set by the pulse-protocol create paths (:1796, :2076). The committed
source sha256 `0d3ce77d…` matches its fetched-source manifest. The r96
boundary/scout receipts show the non-drifted case (`pulse.corked: null`,
`state: "running"`, `Corked: false`) — i.e. the field is a projection that can
lag, exactly as the fixture's named block says. Residual uncertainty
(unchanged): `dev_info.state`'s cache-proxying lives in unfetched manager code,
and the lag window is measured only by the two reps.

## 4. Independent live re-derivation — `runs/r96v_live.py` (23/23 PASS)

Own code only: own tone writer, own `pactl -f json` parsing, own WAV analysis,
own capture recipe, own transcription. Evidence:
`/home/vgpnk/r96v/live3/r96v_live.json`.

- **8 attr cells** (default, `--latency-msec=100`, `--process-time-msec=5`,
  env 250 + flag 100, env `+100` invalid, env `0x64`, s24 default, stereo 100):
  every measured row equals **this seat's own prediction** — including
  `maxlength 4194303` on s24 and the invalid-`+100` default row.
- **Instrument latency**: 10 `pa_stream_get_latency` calls, **all `rc=−16`**
  (own parse of the instrument's `EV … latency phase=… rc=…` lines).
- **Cork flow gate**: own `pw-record -P stream.capture.sink=true --target <own
  null sink>` capture around the committed instrument's `cork` leg → the
  corked window is **silent (0 nonzero frames < 1 s)** and the post-uncork
  window carries **71 677 nonzero frames** — bit-for-bit the fixture's armed
  number; uncork event at client t=1.328 s.
- **Trigger negative**: same capture around `--mode trigger` → **0 nonzero
  frames** in the whole leg.
- **Bogus-host DNS wall**: own bounded `pactl info` with a dead
  `PULSE_SERVER` → rc 1, **7.83 s** (the ≥ 2 s floor armed by the family).
- **Exit census**: own module/sink/process census before and after; the
  module was name-verified before unload and absent after; defaults (sink) and
  all four `clock.*` settings unchanged.

(A first draft of this script failed 5 of its own checks — two of them because
`pw-record --target <sink>.monitor` does not resolve in this PipeWire version
and one because of a line-filter bug; the failures were **this seat's script
bugs**, disclosed here, and the corrected run is the 23/23 record above. The
correction is itself evidence for the fixture's choice of the
`stream.capture.sink=true` capture recipe.)

## 5. Mutation / negative controls

Each mutation is a hardlink copy of the frozen tree with the target file
**removed and rewritten** (the untouched tree's fixture shas were re-checked
afterwards); each ran the real CLI on the mutated tree.

### 5.1 Tree mutations

| mutation | what changed | measured outcome |
| --- | --- | --- |
| **gate / dead endpoint** (`mut-gate`) | the entry gate's `pactl info` armed with `PULSE_SERVER=tcp:127.0.0.1:4713` | 5/5 entries `coverage_blocked` (“pulse server unresponsive at entry…”), **0 legs**, `failures {}`, **rc 0** — the console reads green. This seat's law set: **3 PASS / 308 BLOCKED / 0 FAIL** — the 3 PASS are receipt identity only (`mode`, both cross-checks); **no cell is a silent green**. The entry *heads* still recorded the live server (`PulseAudio (on PipeWire 1.6.8)`) while the gate leaf refused in 1 ms — the block is the mutation's, not a dead daemon |
| **build / unbuildable instrument** (`mut-build`) | `#error` inserted into `pulse_r96_probe.c` | cork entry blocked by name (“the own-libpulse instrument did not build …:33:2: error: #error r96v-mutation”); the other four entries green (156 legs, `failures {}`); law set 446 PASS / 63 BLOCKED / **0 FAIL** |
| **parse law** (`mut-parse`) | `_pulsecli_r96_parse_atou` accepts a leading `+` | rc 1; fixture reddens **exactly** the 4 legs of the two `+` cells (`t_parse_2b313030__r{1,2}` = `+100`, `t_parse_2b30783634__r{1,2}` = `+0x64`), 12 failures, all other 174 legs green; **this seat's law set names the same two cells** (8 cells: 4 `own_transcription_matches_fixture_prediction` + 4 `env_ms`) — pinned, not noisy |
| **instrument report** (`mut-instrument`) | `pa_stream_get_latency`'s rc forced to 0 in the C fixture | rc 1; fixture: `e_latency_query__r{1,2}: … did not return -16 in every call ([0])`; law set: the same 2 cells + the 2 build-sha cells (the committed bytes were mutated, so those two shas must move) |

### 5.2 Receipt forgery suite — `--forge` (11 fabrications + 1 control)

| forgery | caught by | result |
| --- | --- | --- |
| `none` (control) | — | 507 PASS / 0 FAIL / 2 BLOCKED |
| `blank-lists` (blank both verdict lists) | `receipt.blocked_agree` | **CAUGHT** (the 2 named blocks vanish while the derived cells remain — the lists are not the detector) |
| `forge-attr-measured` (a measured `tlength` +1) | `t_lat_100__r1.measured_matches_own_transcription` | **CAUGHT** |
| `forge-attr-predicted` (a `prebuf` prediction +1) | `t_env_10__r1.own_transcription_matches_fixture_prediction` | **CAUGHT** |
| `forge-parse` (`env_ms` 100→101) | `t_parse_30783634__r1.env_ms` | **CAUGHT** |
| `pop-leg` (delete `p_dup__r2`) | structural leg-count + the leg law | **CAUGHT** |
| `forge-build` (binary sha → zeros) | `client_build.binary_sha` | **CAUGHT** |
| `forge-census` (`sinks_gone.ns` false) | `pulsecli_target_r96_probe.sinks_gone` | **CAUGHT** |
| `forge-native-class` (`has_pulse_corked` true) | `e_native_corked__r1.no_pulse_corked_prop` | **CAUGHT** |
| `forge-corked-flip` (`corked_true_samples` 0) | `e_cork__r1.corked_witness` | **CAUGHT** |
| `forge-latency` (`latency_rcs` → 0) | `e_latency_query__r1.nodata` | **CAUGHT** |
| `forge-restore` (suppression row +1) | `p_restore_off_playback__r1.suppressed` | **CAUGHT** |

Each fabrication additionally trips `receipt.failures_agree` (a field says red
while the receipt's own list is empty) — the intended “green receipt, red
fields” detector.

## 6. Cross-run drift (A vs B)

Structural walk of both green receipts: **16 385 leaf comparisons, 1 163 raw
differences**, every one classified:

- 24 × `first_snapshot_attrs.*` — the late-attr **race census** (recorded,
  never armed; the armed field is `attrs_after_resnapshot`);
- 26 × recorded stdout/stderr text of the server-lattice legs — the foreign
  **default-source move** (above) shows up here, plus per-run `Client Index`;
- 5 × `foreign_r96a_nodes` — the concurrent foreign instance census;
- 11 × witness **counts** (`cork_flip.*_samples`, `tap.frames`) — armed only
  as `≥1`/`>0`/bounds, not as equalities;
- the rest are identity/timing/ids/paths (`row.*`, module ids, landed names,
  `*_t`, `wall_s`).

**Armed-constant set: 0 differences.** Every field a law compares to a
literal (all 66 attr predictions/measurements, `env_ms`, `frame_size`,
`latency_rcs == −16`, `changes_at_uncork == 1`, `has_pulse_corked false`,
restore rows 0, `sinks_gone` true, `own_nodes_after []`, build shas, refusal
`exit_code`/`error_class`, `stderr_bytes == 0`, `row_seen`/`linked`) is
identical in A and B. Relational arms (landed index == the same receipt's seat
index, literal `target.object`) are verified per receipt, not across runs.

## 7. Custody, hygiene, provenance

- **Exit census after the whole battery** (own live check): **0** `r96`/`r96a`
  modules, sinks, sources, sink-inputs, source-outputs, PipeWire nodes and
  processes; default sink `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`
  and default source `alsa_input…Line__source` unchanged; `clock.force-quantum=0`,
  `clock.force-rate=0`, `clock.quantum=1024`, `clock.rate=48000` unchanged
  (this seat never touched them). Every receipt's own `sinks_gone` /
  `own_nodes_after` / verified-unload block agrees.
- **Residue (disclosed).** The r90-class WirePlumber store residue: 43 rows in
  `~/.local/state/wireplumber/stream-properties` carry `r96a_` after the whole
  battery, of which **15 are attributable to this seat's six runs** (3 rows
  each for the five runs that loaded a null sink; the `mut-gate` run — whose
  entries never got past the gate — left **0**), the rest predate this window
  (the author's runs and the concurrent foreign lane). The family's own
  suppression legs and the own-libpulse instrument leave none (verified
  in-receipt: `restore_before == restore_after == 0` for all 4 suppression
  tags per run). My independent live suite added **8** `r96v_` rows (its
  `pacat` cells do not set `state.restore-props=false`). The store has no CLI
  delete.
- **Bounded children**: no `killed_at_bound` in any of the six runs' cork or
  target legs; the only armed non-zero exits are the refusals the family
  declares. All six run stderr logs are empty (0 bytes).
- **Lane footprint**: `/home/vgpnk/r96v` = 6.3 GB (head.tar 3.1 GB + the
  frozen tree 3.2 GB, hardlink-shared with the four mutation copies);
  `corpus/live/r96-verifier/` = 3.5 MB of evidence copies (untracked).
- **Zero tracked writes**: `git status --porcelain --untracked-files=no` = 0
  lines. No commit, no push, no `set-default-*`, no sibling-lane artifact
  touched.

## 8. Remaining risks

1. **Console-line green bias (confirmed by construction).** Both the
   `mut-gate` and `mut-build` runs print `{"receipt": …, "failures": {}}` with
   **rc 0** while the receipt carries 5 (resp. 1) named entry-level blocks and
   zero legs. A reader of the runner's stdout alone reads those as green. The
   receipt is honest; recommend the summary line carry the blocked count (the
   r94 finding, now demonstrated with a real mutation).
2. **Self-consistent receipt rewrite** is undetectable at receipt level; the
   compensations are the frozen-tree pin, the two live runs, and §3–§4's own
   code. Unchanged from r89/r94.
3. **The named block is a host property, not a law**: `e_native_corked`'s
   value arm is unarmed because the pulse server's cached `dev_info` state
   demonstrably lags the live node. A future host whose cache is in sync turns
   it green — and if a future round *arms* the value, it will be arming the
   cache's timing. The class claim (no `pulse.corked` on a native stream) is
   armed and passed in every run.
4. **Shared-host concurrency is real and was observed**: a foreign
   `--probe-pulsecli-r96` instance ran inside run B's window, a foreign lane
   moved the server's default source, and sibling r92/r97/r100 lanes were live.
   Nothing in the armed set moved — but the family's fixed-path lock is
   **per-tree**, so two concurrent same-family runs from different trees do
   not exclude each other (the r89 F5 property, now observed live).
5. **Armed floors that could red on a different host**: the bogus-host DNS
   wall (≥ 2 s; measured 7.7–8.0 s) would red on a negative resolver cache;
   `e_prebuf_zero_slow` is an **upper** bound (≤ 12 000; measured 2 752) and
   `e_prebuf_default_slow`/`_fast` lower bounds (measured 57 341 / 55 550);
   the target entry's fallback legs record the landed name (a session-manager
   default change is evidence, not a failure).
6. **Host load**: 2.98–5.5 at run starts with `host_is_quiet: False` in every
   entry; all walls are far inside their bounds and the armed-constant drift
   is zero, so no load coupling is visible — but the recorded witness counts
   (§6) remain timing-sensitive by construction.

## 9. Doc-vs-measured deltas (all minor, none gating)

- The author's §4 header for the props entry says “12 legs”; the §5 census
  table (and this gate) measure **20** (14 property legs + 2 malformed + 4
  restore). The census table is the right one.
- `e_subscribe`'s “24–40 FOREIGN sink-input events” were **20/26** (run A)
  and **35/34** (run B) — recorded, never armed; the armed law (exactly 1 own
  `change` after the uncork, ≥1 `new`) held in every rep of every run.
- `late_attr_census` “0/66 in both runs” measured **1/66** and **2/66** — the
  host was not quiet; the race is a census, not a law, and every leg recovered
  within the re-snapshot bound (all 66 armed in both runs).
- The author's “178 legs / 5 entries / both runs 143 s / 0 failures /
  `failures {}`” and the frozen shas (`b545283e…` worktree, `97ed1b1c…`
  committed, `fe2c1683…` C fixture, `c3fc4cef…` built binary) all re-measured
  as stated; the committed-blob sha is the one that matters and it is the one
  the frozen tree carries.
- The author's declared per-entry census (41/27/68/20/22) is exact, and every
  armed number the author publishes (`e_cork` 71 677, `e_trigger` 0/0,
  `e_prebuf_zero_slow` 2 752, `e_record_cork` 196 608/262 144, every
  `latency` call −16) re-derived identically in both runs.

## Evidence index

- Frozen tree: `/home/vgpnk/r96v/tree` (tar `head.tar`, sha in
  `runs/head.tar.sha256`); receipts under `…/tree/corpus/live/runs/`.
- Mutation trees: `/home/vgpnk/r96v/mut-{gate,build,parse,instrument}/`.
- Law set + live suite + outputs: `/home/vgpnk/r96v/runs/` (`r96v_laws.py`,
  `r96v_live.py`, `r96v_laws_all.{json,txt}`, `r96v_forgeries.json`), live
  records `/home/vgpnk/r96v/live{,2,3}/r96v_live.json`.
- Repo copies (untracked): `corpus/live/r96-verifier/{receipts,runs}/`.
