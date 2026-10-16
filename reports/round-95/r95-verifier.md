# r95 VERIFIER — frozen-tree gate on committed `ffeb5155` (the JACK ↔ PipeWire interop lattice)

Seat: **verifier** (non-author, audio-shokunin r95). Lane
`~/Projects/shokunin/audio-shokunin`; basis **`git archive HEAD`**
(`021bde86`, whose parent chain carries the r95 author commit **`ffeb5155`**)
extracted to `corpus/live/r95-verifier/tree/` — the committed bytes, **not**
the worktree. Window **2026-10-16 09:01Z–09:28Z** (local UTC−3), loadavg
**51–57** at run start and **9.5** once the daemon recovered, 32 cores.
`TMPDIR=~/Projects/shokunin/tmp`.
**Zero tracked writes by this seat, zero commits, zero pushes, no
`set-default-*`**; every artifact under `corpus/live/r95-verifier/`.

Duty: re-run the full `--probe-jack-r95` family (5 entries / 24 legs) fresh on
the archived tree, re-derive cell-level claims, probe forgery/mutation
sensitivity on the signature gate, and confirm `coverage_blocked` cells are
named classes. The frozen `probeParent` slot spawned no labrat: the duty is a
re-run/mutation gate and the family's unknowns are host-toolchain ones, not
empirical mechanisms (disclosed, not silently skipped).

## 0. Verdict

**PASS on committed bytes, with two armed-cell findings and one host-state
episode recorded honestly.**

- The committed r95 block is **byte-identical** to the author's measured
  worktree bytes (85 685 B, sha-compared), and the merge is
  **insertion-only**: `git diff aaf56d30 HEAD` on the fixture is
  **+1809/−3** with exactly one 1773-line block hunk plus 5 `main()` sites
  and the 3 declared splice deletions.
- **Fresh runs on committed bytes** (this seat's own, §2.2): **two full runs,
  24/24 legs each**, with the family's armed cells re-deriving green except
  **one cell** — `d_metadata: stale after remove` — which is red in both my
  runs and green in all 13 prior observations (author + tracked
  scout/boundary receipts). The cell is **host-timing conditional** (§8.1),
  so the family's green is load-conditional; the lattice's other 23 legs and
  every cross-seat cell re-derive.
- This seat's **own independent law set (256 laws)** re-derives the author's
  two declared green receipts at **256/256 PASS, 0 FAIL, 0 BLOCKED**; on my
  runs it derives exactly the one red cell the receipts name (and exactly the
  two driver-confound blocks run B names); on the author's *non-green* dev run
  it derives the 5 absent-witness BLOCKED cells (that receipt predates the
  store witness — the `stream_properties_own_rows` key is simply absent, so
  nothing reads silently green).
- **20 fabricated receipts** (19 fabrications + 1 no-op control) are caught:
  17 by `FAIL`, 2 by `BLOCKED`, 1 recorded-not-armed control correctly a
  no-op. The signature gate is live under both mutations: a **stimulus**
  change (tone 997.0→997.5 Hz) reds the two energy laws, and an **armed
  constant** change reds the fixture's own flag arm while this seat's laws
  stay green (independence).
- The `coverage_blocked` surface is a **named-class** surface: with `gcc`
  removed from `PATH` all five entries emit `missing tools: ['gcc']`; the
  driver confound, the store-unreadable teardown and the stall-kill path all
  emit named classes, never a green.
- **Host episode (§2.1), not a bytes defect:** the shared user daemon wedged
  at ~09:00Z under concurrent sibling-seat batteries, reddening this seat's
  first run and (independently) a concurrent main-worktree run; it recovered
  at 09:24:41Z and the four runs above were taken on the committed bytes. The
  episode also exposed a real receipt-shape gap (§8.4).

## 1. Frozen tree and byte identity

| check | required | measured | verdict |
| --- | --- | --- | --- |
| archive | `git archive HEAD` | tar sha256 `fbe9cb9bad0c899c1908057321caab84c04ea64e1faeb0db53d81f1d59f3ba27` (3 317 678 080 B) | PASS |
| census | — | **44 555 files / 11 772 dirs / 0 symlinks**; file-set symdiff vs `git ls-tree -r HEAD --name-only` = **0** (`runs/r95v-symdiff.txt`) | PASS |
| fixture identity | committed blob | `corpus/fixtures/measure_audio.py` sha256 `dca4dc9bc87e006b534a50d80270bfb27492fadecfe75fbbd89f37342bd87ed7` = `HEAD:` blob = tree copy = the worktree file **at archive time (09:01Z)** | PASS |
| fixture source | committed blob | `corpus/fixtures/r95jack.c` sha256 `55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be` = `HEAD:` blob = tree copy = the author's declared implementation sha | PASS |
| `py_compile` in the frozen tree | clean | rc 0 | PASS |
| **block byte-identity** | author's worktree bytes | the r95 block (banner → `def main()`) is **85 685 B and byte-identical** between the author's worktree (`wt-r95`, file sha `164a915825dd054b…`, i.e. the author's declared implementation sha) and the committed file — so the author's greens transfer to committed bytes | PASS |
| merge shape | insertion-only + 3 splices | `git diff aaf56d30 HEAD -- corpus/fixtures/measure_audio.py` = **+1809 / −3**; hunks: one 1773-line block insertion, `--probe-jack-r95` arg, `args.probe_jack_r95` in the mutex `sum([...])`, the 32-line dispatch block, the `mode` select, the `suffix` select; the **only 3 deletions are the 3 declared spliced lines** | PASS |

The tree carries the **tracked** r95 scout and boundary receipts
(`corpus/live/r95-scout/`, `corpus/live/r95-boundary/` — 43 + 60 files), so the
cross-seat cell re-derivation in §4 runs against committed bytes.

**Foreign state, observed and not touched:** from ~09:28Z a concurrent sibling
lane began editing the **shared worktree** fixture
(`corpus/fixtures/measure_audio.py`, mtime 09:28:13Z, now +493/−169 against
`HEAD`: new `_jack_r95_daemon_gate` / `_jack_r95_witness_gate` /
lock-path helpers — i.e. a lane repairing exactly the contention and
witness gaps §2/§8 name). Every number in this report was produced from the
**frozen tree copies** under `corpus/live/r95-verifier/`; the worktree file was
equal to `HEAD` when this seat archived it (09:01Z) and this seat never wrote
to it. The operator should decide whether that worktree edit is folded into a
later commit before the next freeze.

## 2. Fresh runs on committed bytes

### 2.1 Run A — red by daemon contention (not a bytes defect)

`tree/` → `python3 corpus/fixtures/measure_audio.py --probe-jack-r95`
(09:02:16Z start, receipt stamp `20261016T090614906048Z`):

| entry | legs | failures | coverage_blocked |
| --- | --- | --- | --- |
| `jack_surface_r95_probe` | 0 | **2** (`a_avail: version_ints = None`; `a_avail: version = None`) | 1 (`probe null sink r95a_ns_3231401 never enumerated`) |
| `jack_addr_r95_probe` | 0 | 0 | same named block |
| `jack_bytes_r95_probe` | 0 | 0 | same named block |
| `jack_quantum_r95_probe` | 0 | 0 | same named block |
| `jack_defects_r95_probe` | 0 | 0 | same named block |

Attribution evidence (all measured, not inferred):

1. **Same signature, different tree.** A concurrent lane ran the identical
   family from the *main worktree* at 09:06:02Z
   (`corpus/live/runs/20261016T090602831047Z-jack-r95/`) and produced the
   **same two failures and the same five named blocks** (pid 3228981).
2. **Every daemon-dependent surface hangs simultaneously**: `pw-dump`
   rc 124 at a 20 s bound with 0 bytes; `pactl list sinks short` rc 124;
   `pw-jack` client open (`./r95vjack info 0.2`, compiled from the committed
   source) produced **no output at all** inside 12 s; while
   `pw-metadata -n settings` answers in **4–7 ms** throughout.
3. **The failures are absences, not wrong values** (`None`), i.e. a witness
   that never arrived — the code path that arms them is unchanged and passes
   on the author's identical bytes.
4. **The author saw the same class**: their dev run 1
   (`20261016T085246666582Z`, loadavg 56.56) recorded `s_shape`/`s_liveness`
   mid-witness `None` (29 failures + 2 named blocks) while `a_avail` passed in
   0.222 s; their greens follow at 08:54:42Z / 08:55:27Z.
5. **Host forensics**: one shared daemon (pid 2060, up 16 h); ~09:00Z four
   sibling-seat batteries started (r90/r91/r94/r98 lanes) and the r97 lane
   began spawning private `pipewire -c …/wppol-r97-*/conf/pw/*.conf` daemons
   in TMPDIR; **five sibling `pw-dump` clients sat stuck for 3–15 minutes**
   (pids 3208675, 3224758, 3236057, 3261714, 3297578 — r98/r93/r92 lanes'
   diagnostic commands whose parent shells stopped draining them) and two
   `pw-jack` clients (this seat's and a concurrent r95c lane's) sat inside a
   blocking `jack_client_open` past their `timeout` bounds (the fixture's
   SIGTERM handler is a flag setter, so only SIGKILL ends them — the family
   itself escalates correctly, `timeout(1)` does not). This seat killed
   **only its own** stuck client. The wedge is fleet-wide, not local to this
   lane: a sibling r95c lane was blocked at the same time on the same daemon.
6. **The daemon-free surfaces still work**: `pw-metadata -n settings` answers
   in 4–7 ms throughout, and the fixture's `unknown` mode returns
   `R95AJSON {"mode":"unknown",…}` in **1 ms** — so the two r95-local error
   classes (`jack_r95_unknown_mode`, reachable here; `jack_r95_no_daemon`,
   the message class the wedged path would need) are wired and the client
   binary itself is healthy. The wedge is in the daemon's registry/connect
   path, not in the fixture.
7. **The daemon is up but saturated**: `pw-cli info 0` prints the core info
   (version 1.6.8) and then fails to complete inside 8 s;
   `pw-cli ls Client` enumerates **210 clients** and also fails to complete —
   a client population dominated by stuck sibling-lane probes, which is the
   most economical explanation for a registry/connect path that never syncs
   while the metadata path stays instant.

A receipt-shape note found while reading the red receipt (real, minor): the
early-block path (`_jack_r95_block`) does **not** carry `entry["legs"]`, so a
run that blocks *after* a leg has run reports `failures` with **no leg
detail** (`legs: []`). It never reads green, but the receipt loses the
evidence of the legs that did run.

### 2.2 Run B / run C — fresh on committed bytes after the daemon recovered

The retry loop caught the recovery at **09:24:41Z** (`pw-dump` 9 ms,
`pactl` 3 ms) and fired four runs back to back on the frozen tree and the two
hardlink mutation copies (each 39 s wall):

| run | receipt | tree | legs | failures | coverage_blocked |
| --- | --- | --- | --- | --- | --- |
| **B** | `…T092520745855Z` | `tree/` (committed bytes) | **24** | **1** | 2 named |
| **C** | `…T092559604608Z` | `tree/` (committed bytes) | **24** | **1** | 0 |
| **mutstim** | `…T092638509558Z` | `tree-mutstim/` (fixture tone 997.0→997.5 Hz) | 24 | **3** | 0 |
| **mutlaw** | `…T092717417797Z` | `tree-mutlaw/` (armed `jack_port_flags out` 2→3) | 24 | **3** | 0 |

Per-entry on **run B**: surface 3, addr 4, bytes 2, quantum 10, defects 5 —
the declared 24. **Run C is identical to run B in every armed cell** (same
`j2p` ratio 0.954104, same frames 100352, same `p2j` ratio 0.999930, same
`in_nonzero` 52221, same `cb_in_nonzero` 51), so the family is deterministic
on committed bytes under a quiet daemon.

**The one red cell, both runs**: `d_metadata: stale after remove = '', want
'value1'`. The leg's own record shows why — `get_after_remove_rc = -1` and
`get_after_remove_value = ''`, i.e. the client's own getter reports *not
found* immediately after removing its own property. All **13 prior
observations** of this cell (4 in the author's runs, 9 in the tracked
scout+boundary receipts) recorded `rc 0` / `'value1'` (a stale local cache
hit). The cell is therefore **host-timing conditional**, not a law: under
loadavg ≈ 55 the metadata update has not reached the client's cache when the
getter runs (stale hit); under loadavg ≈ 9.5 (my window) it has
(`-1`/`''`). The family arms the stale branch as a hard equality — a
**false-red generator** on an unloaded host (finding, §8).

The two named blocks in run B are the family's own F1 design working: the
resolved driver was the real `alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink`
(a foreign driver, `priority.driver = 796`) instead of `Dummy-Driver`, and the
entry recorded it as a **named confound** rather than pretending the
fallback-driver props held. Run C resolved `Dummy-Driver` again and has no
blocks — the driver flips with host state, and the family handles both.

## 3. Law re-derivation — `runs/r95v_laws.py`

**256 laws** over the receipts' **recorded fields only**; the entries' own
`failures` / `coverage_blocked` lists are never an input (they are used at the
end as a cross-check). Coverage: the no-server premise and tool census; the
version quadruple and the 168-export class; the citizen shape (alias triple,
`object.path` indices, `format.dsp`, the five `jack_port_flags` round-trips
`2/1/6/18/2`, Physical/Terminal props, CanMonitor absent, monitor API
bookkeeping, zero links, driver resolution); the addressing lattice (rendered
0 / native 22 / fill-aliases 0 / corner 0 with their pw-dump edges); both byte
witnesses (capture peak / rms ratio / nonzero fraction / Goertzel ratio, the
sample-exact `in_peak == peak_i16/32768` law and its energy ratio); the
quantum lattice (inactive invisibility, live callback, second client,
`PIPEWIRE_QUANTUM` ≡ `pw-jack -p`, the 44100 rate axis, `nframes==1` metadata
path, the global store write + restore + `settings_moved`); the defect
families (xrun envelope, RT stack-poison pattern, latency triples, transport
projection, metadata registry-id row); and per-entry hygiene (name-verified
unloads, `sinks_gone`, `stream_properties_own_rows`, `own_nodes_after`,
foreign censuses).

| receipt | laws | PASS | FAIL | BLOCKED |
| --- | --- | --- | --- | --- |
| author green #1 (`…T085442157241Z`) | 256 | **256** | 0 | 0 |
| author green #2 (`…T085527000328Z`) | 256 | **256** | 0 | 0 |
| author dev run 3 (`…T085334177280Z`) | 256 | 251 | 0 | **5** (all `stream_properties_own_rows` **absent** from that receipt) |
| **this seat run B** (committed bytes) | 257 | 253 | **1** | 3 (named driver confound) |
| **this seat run C** (committed bytes) | 256 | 255 | **1** | 0 |
| this seat run A (contended) | 72* | 13 | 0 | **59** |
| this seat `nogcc` run | 72* | 10 | 0 | **62** |
| `mutstim` (tone 997.5 Hz) | 256 | 251 | **5** | 0 |
| `mutlaw` (armed flags 2→3) | 256 | 254 | **2** | 0 |

\* only the laws whose entry data exists are emitted when an entry blocks
early (the surface entry ran partially, the rest never started) — 72 of 256.

Receipt-level cross-checks: on the author's greens the derived red set is
empty and the receipts' own lists are empty; on dev run 3 the derived BLOCKED
set is the 5 entries' absent store witness (that run predates the witness: the
`stream_properties_own_rows` key and the named unreadable-store block are both
absent, while the committed bytes and the author's final worktree bytes carry
both — so a `None` on the final bytes would imply a named block; a contract
law encodes exactly that); on run A the receipt's own 2 `a_avail` failures
(`version_ints = None`, `version = None`) appear in this law set as
**BLOCKED**, not FAIL — the fixture calls an absent witness a failure, the law
set calls it an absence; both read never-green, and the derived BLOCKED set
contains exactly the cells the receipt's named block names. On runs B/C the
derived FAIL set is exactly the one cell the receipt names, and the derived
BLOCKED set is exactly the two driver-confound cells run B names.

## 4. Cross-seat cell re-derivation (committed scout/boundary receipts)

`runs/r95v_crosscheck.py` pulls, for 24 headline keys, every value the
author's green receipt recorded and every value the **tracked** r95-scout and
r95-boundary receipts recorded under the same key. Cells that re-derive
identically (shared sets): `version_ints [3,1,6,8]`, the port-flag set
`{1,2,6,18}`, `request_monitor_rc 0`, `monitoring_input 1`,
`ensure_monitor_rc 0`, `always_process true`, `connect_rc {0,22}`,
`bufsize_activated {2048,4,512}`, `bufsize_after_set_active 512`,
`bufsize_active {2048,512}`, `lat_cap {0,100,200}`, `lat_play {0,10,20}`,
`total {0,150}`, `state_after_start 1`, `xrun_cbs 1`, `stall_cycles 8`,
`get_client_value "value1"`, `get_missing_rc -1`. Contextual (different leg
states, not disagreements): `out_connected 1` and non-empty
`out_connections` in the transport/corner/xconnect legs.

Cell-level claims re-derived by hand:

- **Author correction #1 is right and the scout's own receipt proves it.**
  `r95-scout/receipts/b_shape.json` records `lat_outm.flags = 2`, while the
  scout *report* table (line 147) declares the CanMonitor round-trip `0xA`;
  `r95-boundary/receipts/{h,q}_shape.json` carry **3/3 reps each** with
  `lat_outm.flags = [2,2,2]` — exactly the author's "3/3 each" claim. The
  committed family arms **2**.
- **The port-flag round-trip re-derives from the committed toolchain**:
  `/usr/include/jack/types.h` gives `IsOutput=0x2`, `IsPhysical=0x4`,
  `CanMonitor=0x8`, `IsTerminal=0x10`, and the committed fixture *requests*
  `out=0x2`, `in=0x1`, `outp=0x6`, `outt=0x12`, `outm=0xA`
  (`r95jack.c:299–303`). The recorded round-trip is `2/1/6/18/2`: four of the
  five match the request, and the one that does not is exactly the CanMonitor
  bit — which the PW graph corroborates (no prop, no `port.extra` on `outm`).
  So the scout's `0xA` is the *request*, the receipt's `2` is the *report*;
  the family armed the report.
- **F7 effective size re-derives**: `{h,q}_bufsize1` each record
  `bufsize_activated = 4` (2 reps), matching the family's 1..8 band + exact 4.
- **168 exports re-derive independently**: this seat's own
  `nm -D --defined-only /usr/lib/libjack.so.0.3.1608` filtered to `[Tt]`
  `jack_*` text symbols yields **168**, with the 7 absent and 8 present
  members of the declared classes exactly as armed.
- **Toolchain identity re-derives**: `libjack` sha256
  `34bbb09aceb7de3a…` (= the receipt's recorded 16-hex prefix) and the
  fixture rebuild sha256 `016a685372e6d8fa…` (= the receipt's
  `build.binary_sha256` prefix) — the recorded build is reproducible from the
  committed source with `gcc -O1 -w -ljack -lm`.

## 5. Signature-gate sensitivity

The family's "signature" is the **fixture-source identity + the stimulus the
probe generates** (it has no cross-seat witness by design; the boundary and
scout are referenced in comments only).

### 5.1 Receipt forgery suite (`--forge`, base = author green #2)

| forgery | fabrication | result |
| --- | --- | --- |
| `none` (control) | — | 256 PASS / 0 FAIL / 0 BLOCKED |
| `blank-verdicts` | blank both verdict lists | 256 PASS — **no-op control**: the lists are not the detector |
| `forge-version-ints` | `[3,1,6,9]` | **CAUGHT (FAIL)** |
| `forge-export-count` | 168 → 167 | **CAUGHT** |
| `forge-flags-outm` | `lat_outm.flags` → 10 | **CAUGHT** |
| `forge-port-alias` | `outm` alias | **CAUGHT** |
| `forge-native-rc` | native `connect_rc` 22 → 0 | **CAUGHT** |
| `forge-in-peak` | `in_peak` → 0.4999 | **CAUGHT** |
| `forge-mag2` | capture Goertzel → 1e9 | **CAUGHT** |
| `forge-ideal` | `ideal_mag2` → 1.0 | **CAUGHT (2 laws)** |
| `forge-conns` | rendered `conns` → [] | **CAUGHT** |
| `forge-driver` | driver → "Other" | **CAUGHT** |
| `forge-quantum-prop` | live `force_quantum` → "1024" | **CAUGHT** |
| `forge-settings-moved` | `settings_moved` → `["clock.rate"]` | **CAUGHT** |
| `forge-xrun` | `xrun_cbs` 1 → 8 | **CAUGHT** |
| `forge-latency` | `total` 150 → 100 | **CAUGHT** |
| `forge-metadata-row` | live row `value1` → `value9` | **CAUGHT** |
| `forge-build-sha` | `build.src_sha256` → `deadbeef…` | **CAUGHT** |
| `pop-leg` | remove `b_jack2pw` | **BLOCKED (11 laws)** — never green |
| `pop-hygiene` | remove `stream_properties_own_rows` | **BLOCKED** |
| `forge-capture-sha` | capture sha256 → `deadbeef` | 256 PASS — **recorded-not-armed control**, correctly a no-op (the boundary's F2 window artifact) |

### 5.2 Coverage-block naming (measured, this seat)

`PATH` = a 3123-entry symlink farm with **`gcc`/`cc`/`clang` removed**:
all five entries emit `blocked`/`coverage_blocked = ["missing tools:
['gcc']"]`, `failures: []`, `legs: []`. **Named class, never a green.**
Runner stdout for that run is `{"receipt": …, "failures": {}}` with **rc 0** —
the r94 verifier's risk #1 (console-line green bias) reproduces here: the
receipt is honest, the summary line is not.

### 5.3 Mutation runs (live, on hardlink copies of the frozen tree)

| mutation | what changed | fixture's own arms | this seat's laws |
| --- | --- | --- | --- |
| `tree-mutstim` | **stimulus**: `r95jack.c` tone 997.0 → **997.5 Hz** (fixture-source sha becomes `abcfd3b1b2ae3dcc`) | **RED**: `b_jack2pw mag2 ratio = 0.0124` (want [0.9,1.03]), `b_pw2jack mag2 ratio = 0.3196` (want [0.985,1.005]) | **5 FAIL**: the two energy ratios, `build.src_sha256` (`abcfd3b1…` vs the committed `55d4d411…`), the rebuilt binary sha, and the metadata cell |
| `tree-mutlaw` | **armed constant**: `("out", 2)` → `("out", 3)` in the port-flag tuple (C code untouched) | **RED**: `s_shape: jack_port_flags out = 2, want 3` | **2 FAIL** — and *neither is the flags law*: my laws expect 2 (which is what the receipt records) and PASS, while the fixture's own arm reds on its mutated expectation. The 2 FAILs are the `b_pw2jack` energy ratio (see §8.2) and the metadata cell |

The pair is the point: `mutstim` proves the family's physics arms are pinned to
the stimulus that produced them (a fixture-side frequency change cannot pass),
and `mutlaw` proves the *gate* is live while this seat's law set stays
independent of the fixture's armed expectations.

## 6. Cross-run drift

Structural walk of the author's two declared greens (`--diff`):
**2 453 leaf comparisons**, 418 raw differences, **29 non-volatile** — and
every one of the 29 is a *recorded-never-armed* foreign-graph census row
(`s_shape.json.census.all` 59 vs 51, `census.dsp_type` 55 vs 47,
`census.first40[]` naming sibling seats' `pw-play` nodes and the USB Audio
device that replaced the S/PDIF one). The classed volatiles that differ
elsewhere are exactly the declared ones: the `b_jack2pw` capture
`sha256` (`5dc9f062…` vs `be178a25…` — the boundary's F2 window artifact),
the RT-priority `baseline` garbage (`82` vs `-1359737185`), pid-keyed unload
censuses, wall clocks, and `all_desc_count` 2 vs 3 (foreign writers; the
family arms only `own_desc_count`).

This seat's own two runs on committed bytes (`--diff`, 2 456 leaf
comparisons, **50 non-volatile**) differ only in: the foreign graph census
(`census.all` 57 vs 55, `census.dsp_type` 53 vs 51, `census.first40[]` —
r91a/r96a/r98a sibling nodes and the USB Audio devices), the run-B-only
driver confound (the USB S/PDIF sink driving with `priority.driver 796` vs
run C's `Dummy-Driver`), and the pid-bearing `pattern_r95a_list`/`resolve`
rows. **Every armed cell is identical between B and C.**

## 7. Hygiene, custody, provenance

- File-level: the frozen tree's own run receipts carry `unloads` (all
  `exit_code 0`, name-verified `sink_name=`), `sinks_gone` all-true (or `{}`
  where the sink was unloaded mid-entry and `ns_gone_after_unload` is armed
  instead), `stream_properties_own_rows: []` and `own_nodes_after: []` in all
  five entries, both green runs.
- **This seat's four runs are hygienically identical to the author's**:
  `stream_properties_own_rows []`, `own_nodes_after []`, `sinks_gone`
  all-true (or `{}` with `ns_gone_after_unload` true), every unload
  `exit_code 0`, `settings_moved: []`, and `settings_final.clock.force-quantum
  = "0"` in all four.
- This seat never issued `pactl set-default-*`; the only host-state write the
  family performs (`clock.force-quantum`) is restored to `"0"` in-entry and
  re-verified (`settings_moved: []`).
- **Zero tracked writes by this seat**: every path this seat created or
  modified is untracked (`corpus/live/r95-verifier/**`,
  `reports/round-95/r95-verifier.md`); the lane appears only as `??`. The one
  tracked modification visible now (`corpus/fixtures/measure_audio.py`) is the
  **concurrent sibling lane's** worktree edit recorded in §1 — not this
  seat's, and it postdates every run here (all of which ran inside the frozen
  tree copies). All artifacts (3.3 GB tar, tree + 3 hardlink copies, receipts,
  laws) live under `corpus/live/r95-verifier/`.
- **Foreign state observed, not touched**: a concurrent r95c lane was probing
  the same wedged daemon; r97/r99 lanes were spawning private daemons; the
  r90/r91/r94/r98 batteries were live. This seat killed **only its own**
  stuck `r95vjack` client (pid 3311121/3311120).

## 8. Risks

1. **The `d_metadata` "stale after remove" cell is host-timing conditional
   and is armed as a hard equality.** Census: **13/13** prior observations
   (author's 4 runs + 9 tracked scout/boundary receipts) recorded
   `get_after_remove_rc = 0` / `'value1'`; **this seat's 4 runs (B, C,
   mutstim, mutlaw)** all recorded `-1` / `''`. The leg's own record carries
   both halves, so the law is not a law — it is a race between the metadata
   removal and the client's cache refresh. Fix: arm the *pair*
   (`rc 0`+`value1` **or** `rc -1`+`''`) or record the cell as volatile.
2. **The `b_pw2jack` energy band `[0.985, 1.005]` has a flake mode.** With
   identical fixture bytes, the `mutlaw` run recorded `mag2 ratio = 0.9103`
   while `in_nonzero`/`cb_in_nonzero` were `49149`/`25` (vs `52221`/`51` in
   runs B/C and `53245`/`52` in the author's) — i.e. the `pw-play` link
   landed late, the captured tone window is half-length, and the ±1 % band
   false-reds. The `in_nonzero`/`cb_in_nonzero` bands themselves held. Fix:
   make the energy law conditional on the captured window being complete
   (e.g. `cb_in_nonzero ≥ 40`) or widen the band to the observed spread.
3. **Console-line green bias (presentation, not artifact).** A blocked-only
   run prints `{"receipt": …, "failures": {}}` with **rc 0** (measured on the
   `nogcc` run). The receipt is honest — five named cells — but a reader of
   the runner's stdout alone would read that run as green. Recommend the
   runner's summary line carry the blocked count, and the family's readiness
   precondition (`pw-dump` round-trip) be recorded so a contended run is
   self-labelling.
4. **`_jack_r95_block` drops `legs`** on the early-block path: a receipt can
   carry `failures` with no leg detail (§2.1, run A). Cheap fix: set
   `entry["legs"] = legs` inside `_jack_r95_block`.
5. **The fixed-path family lock is per-tree**
   (`ROOT/live/measure_audio-jack-r95.lock`), so two runs from different tree
   copies do not exclude each other — the inherited r89 F5 property. It cost
   nothing here (my tree's lock is separate from the worktree's).
6. **Self-consistent receipt rewrite** is undetectable at receipt level; the
   compensations are the frozen-tree pin, the byte-identity proof, and the
   independent law set.
7. `d_xrun_stall` arms an *envelope* (`xrun_cbs ≤ 1`) rather than the
   boundary's exact 0, and its kill path is a named block — deliberate, but
   it means the leg cannot distinguish "0 callbacks" from "1 callback".
8. The `q_*` legs write host-global metadata (`clock.force-quantum`); a
   sibling seat writing the same key inside the arm window would surface as a
   real red. The family restores and verifies, and diffs the store.

## 9. Doc-vs-measured deltas (minor, none gating)

- The author says the block was "appended after the r89 block"; measured, the
  block lands after the **r94** family code and its dispatch sits between the
  r94 and r89 dispatches. Immaterial to the insertion-only claim (the diff
  proves prior rows untouched).
- The author's "3/3 each" for the boundary's `lat_outm` is exact (3 reps in
  each of `h_shape`/`q_shape`).
- The author's "997 Hz / amp 0.5" tone and "int16 peak 16383" re-derive from
  the committed fixture constants and the receipt's `tone_source`.
- The author's declared implementation sha (`164a9158…`) is the **worktree**
  file sha; the committed file sha is `dca4dc9b…`. The r95 block is
  byte-identical between them (§1), so this is a merge-shape artifact, not a
  discrepancy.
- The author's four runs are not all on the final bytes: dev run 3
  (`…T085334177280Z`) carries **no** `stream_properties_own_rows` key (and no
  named unreadable-store block), while the two greens and the committed bytes
  carry both — i.e. the witness was added during the dev pass. The report
  does not say so; the receipts do.

## 10. Artifacts and exact commands

Everything below lives under `corpus/live/r95-verifier/` (untracked) —
lane footprint **6.3 GB** (3.1 GB tar + 3.2 GB tree; the three mutation
copies are hardlink copies, 196 K / 2.0 M of broken links):

- `r95v-head.tar` (sha256 `fbe9cb9bad0c899c…`) + `tree/` (+ `tree-mutstim/`,
  `tree-mutlaw/`, `tree-nogcc` PATH farm), `runs/r95v-symdiff.txt`,
  `runs/r95v-lstree.txt`, `runs/r95v-treefiles.txt`.
- `runs/r95v_laws.py` (256 laws, `--forge`, `--diff`),
  `runs/r95v_crosscheck.py`, `scratch/r95v_wait_then_run.sh`.
- Receipts: `tree/corpus/live/runs/20261016T090614906048Z-jack-r95` (run A,
  contended), `…T091203850330Z-jack-r95` (`nogcc`),
  `…T092520745855Z-jack-r95` (**run B**), `…T092559604608Z-jack-r95`
  (**run C**), `tree-mutstim/…T092638509558Z-jack-r95`,
  `tree-mutlaw/…T092717417797Z-jack-r95`; law JSONs
  `runs/r95v-laws-{author-greenA,author-greenB,runA,runB,runC,mutstim,mutlaw,nogcc}.json`;
  wait log `runs/r95v-wait.log`.

```
git archive HEAD -o …/r95v-head.tar && tar -xf … -C tree
python3 corpus/fixtures/measure_audio.py --probe-jack-r95          # run A
PATH=<farm without gcc> python3 … --probe-jack-r95                 # nogcc
python3 runs/r95v_laws.py <receipt> --libjack-sha 34bbb09a… --binary-sha 016a685372e6d8fa
python3 runs/r95v_laws.py <receipt> --forge <name>                 # 20 fabrications
python3 runs/r95v_laws.py --diff <receiptA> <receiptB>             # drift
python3 runs/r95v_crosscheck.py                                    # cross-seat cells
```

*Leaf seat — verified on committed bytes; not judged.*
