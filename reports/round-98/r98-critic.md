# r98 critic — the native `pw_stream` family attacked at the pin

Seat: **critic** (leaf, read-only). Round **98**, family flag **`pwstream-r98`**.
Source pin: **`bb177513a615a32d3bc150ecbdcf78302e110d8c`** (head commit "r99
safety: require explicit opt-in before physical LAN control"; the r98 bytes
ride inside it). Scope: the pinned family block in
`corpus/fixtures/measure_audio.py` (blob lines 46326–48676), its dispatch
(55142–55172), the committed C fixture `corpus/fixtures/r98stream.c`, the four
r98 reports, and the three frozen receipts in the author worktree. Advisory
only: no round admitted, no canonical verdict claimed, no live family run, no
fixture executed or mutated, no source edits.

Commands executed are listed verbatim in
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-critic/commands-and-hashes.txt`.
LSP was unavailable; everything below is literal source inspection plus
receipt reads, and each finding says whether it was **observed** (receipt on
disk) or **inferred** (source path only).

---

## 0. Provenance first (what I verified before attacking)

- The pinned family block (blob lines 46326–48676, incl. leading blank) hashes
  `ba7e3b58fbae83df040bef69d4568e9e0eb51526f7d5f8bdcbf71bda46471ada` —
  byte-identical to the author's block source
  `audio-shokunin-wt-r98/corpus/live/r98-author/r98block.py` (116 914 B) and to
  the sha the integration note records. **The block bytes at the pin are the
  bytes both green batteries ran.**
- Dispatch block (55142–55172) hashes `965e7e3d…`, the argparse row (54390)
  hashes `5b2c034f…` — both equal the integrate note's records; the mutex token
  `args.probe_pwstream_r98` is present (54400) and `mode`/`suffix` carry the
  r98 arms (55944/55964).
- `corpus/fixtures/r98stream.c` at the pin hashes `9f840a6b…` — equals the
  author's recorded fixture sha.
- All **12 out-of-block helpers** the block calls (`_capture_inventory`,
  `_playback_r78_node_names`, `_playback_r78_foreign_clients`,
  `_loopback_r79_oracle`, `_alsapw_r84_loadavg`, `_alsapw_r84_killpg`,
  `_pactlmon_r85_node`, `_pactlmon_r85_unload_own`, `_pwcat_r83_ns_load`,
  `_pwprof_r89_stream`, `_pwprof_r89_jparse`,
  `_capture_r77_sink_names_strict`) are **byte-identical between the author's
  worktree base `5755be5b` and the pin** (AST-level def comparison). The
  "copied-but-unmeasured bytes" attack on the helper layer comes up empty.
- Both cited green receipts exist as **untracked local files** in the author
  worktree (`audio-shokunin-wt-r98/corpus/live/runs/20261016T1010…` and
  `…1012…`), each with 67 legs (15/18/12/4/4/14), `failures: []` on every
  entry, and exactly one coverage cell (`cap_noprop`). They are **not
  committed and not remotely available**; the integrate note says so
  ("untracked, not carried") and main's `corpus/live/runs/` indeed has no
  pwstream-r98 run dirs.
- Spot-checks of run 2 against the author's table all match: `ticks` 87040 ==
  87040; drain period 43.0 ms at own request 1024; trigger 30 calls / rc 1 /
  **3** callbacks at 422/902/1382 ms; activation 4 callbacks at
  602/858/1114/1370 ms; geometry 49152 B / 12288 frames / stride 4 / requested
  1024 (both reps); xruns 27 / 55, ratio 2.037; crash class rc −11 SIGSEGV
  recorded not gated, Audio/Source twin rc 0 state `paused`; sandbox
  `alsa_nodes: []` for all four WirePlumber variants; teardown unloads rc 0,
  `sinks_gone` true, `own_nodes_after: []`; `c_state` transitions
  unconnected→connecting→paused(→unconnected on disconnect), `node.loop.class=main`.

So the family's *content* is what the reports claim. The findings below are
about the instrument's failure semantics, not its laws.

---

## 1. Findings (severity order)

### F1 — HIGH, fixable: blocked entries never name themselves in `failures`; a fully-blocked r98 battery summarizes green

- **Where:** `_pwstream_r98_block` (pin 46892–46913) sets `entry["blocked"]`
  and appends to `coverage_blocked` but leaves `failures` untouched;
  `main()`'s summary `failed = {k: v["failures"] …}` (55968–55970) drives both
  the printed summary and the process exit code.
- **Concrete failure path:** a run where every entry takes a named block —
  missing toolchain (`pwstream_probe_unbuildable`), the wedge-class
  `pwstream_null_sink_unavailable`, or all-sandbox `sandbox_warmup_unlinked` —
  produces six entries with `failures: []`, so the run prints
  `"failures": {}` and **exits 0**.
- **Evidence (observed):** the wedge-era receipt
  `audio-shokunin-wt-r98/corpus/live/runs/20261016T092555426767Z-pwstream-r98/measurements.json`
  shows the mechanism live: `pwstream_core_r98_probe` and
  `pwstream_run_r98_probe` with `blocked="pwstream_null_sink_unavailable"` and
  `failures=[]`. That run escapes a green summary **only because** unrelated
  route/cap legs redded in the same window. Nothing in the instrument enforces
  the difference.
- **The repo's own convention says otherwise:** the r93 gate in the same file
  (55200–55209) states verbatim: *"a BLOCKED family must never read as a green
  battery: the gate names itself in failures so the run exits non-zero"* — and
  does it. The r98 family violates that convention. It also contradicts the
  author's own §6 claim ("a run that lands there is honestly unmeasured, not
  green"): at the summary level the code does not deliver that.
- **Impacted axes:** calibration (honest scope) primarily; coverage (a
  blocked battery is silently indistinguishable from a measured one to any
  reader filtering `failures: {}`).
- **Smallest correction:** in `_pwstream_r98_block`, also
  `failures.append(f"blocked: {msg}")` (or make `main()`'s `failed` include
  entries with non-empty `blocked`/`coverage_blocked`). One line, no arm
  changes, aligns r98 with the r93 convention. The lead owns the edit.

### F2 — MEDIUM, fixable: teardown is success-path-only; an exception between load and teardown leaks the private sink and loses the receipt

- **Where:** every entry's `finally` (e.g. 47483–47486) records
  legs/failures but does **not** run `_pwstream_r98_teardown`; teardown sits at
  the end of the `try` body (47482, 47990, 48142, 48318, 48478). The dispatch
  (55142–55172) calls the six entries bare — no per-entry exception guard —
  and `main()` writes the receipt only at the very end (55965–55967).
- **Concrete failure path:** any unexpected exception after
  `_pwstream_r98_load_ns` (a census helper raising, an arm crashing on an
  unexpected field shape) propagates out of `main()`: **no receipt is written
  at all**, the family lock is released at exit, and the loaded
  `r98a_ns_<pid>` sink(s) and any live tone player are never unloaded —
  residue on the shared graph with zero record.
- **Evidence (observed correlate):** both green receipts record
  `foreign_r98a_nodes: ["r98a_ns_692649", "r98a_ns_700362"]` in **every** entry
  head — two orphaned same-family sinks from earlier pre-green attempts
  persisted through the green batteries. The family only ever cleans its own
  pid's objects, so residue from a crashed earlier run is visible-but-never
  cleaned by the instrument; the author removed two such sinks manually at
  seat end (author §4.2). The leak path itself is inferred from source; the
  residue class is observed on the host in this very window.
- **Impacted axes:** operability (process ownership/cleanup), depth (the
  receipt-loss side also destroys evidence).
- **Smallest correction:** move the teardown into the `finally` (it is already
  idempotent over empty `loads`/`players`), or wrap each dispatch call in a
  try/except that converts an unexpected exception into a named blocked entry
  **with teardown**. No arm changes.

### F3 — MEDIUM, fixable: `_pwstream_r98_sb_start` leaks a live private core when the socket never appears

- **Where:** 47128–47141. The 80×0.25 s socket wait has two raise paths: the
  core *died* (no leak) and the `else` branch — socket never appeared, core
  **still running** — which closes the logs and raises `RuntimeError` without
  touching `procs["core"]`.
- **Concrete failure path:** the sbx entry catches `RuntimeError` →
  `coverage_blocked` → `continue` (48577–48582, 48598–48603, 48624–48630) with
  no `_pwstream_r98_sb_stop` (the ctx was never returned). Each failed sandbox
  start orphans one `pipewire` daemon (own session, redirected runtime dir).
  Repeated failures stack orphans.
- **Evidence:** inferred from source; the class is corroborated by the
  author's §4.2 ("a private-core orphan from a crashed scratch driver was
  killed") in the same window — that instance is attributed to the scratch
  driver, not this path.
- **Impacted axes:** operability (process ownership and cleanup).
- **Smallest correction:** kill `procs["core"]` (SIGTERM→SIGKILL group
  escalation, the family's own convention) on both raise paths, or return a
  partial ctx and let the caller `sb_stop` it.

### F4 — MEDIUM, fixable: the family lock is per-checkout and fails open; probe node names have no pid, so overlapping runs cross-contaminate routing witnesses

- **Where:** `_pwstream_r98_family_lock` (46739–46755) locks
  `ROOT/live/measure_audio-pwstream-r98.lock` — a path **inside the
  checkout**. On `os.open` OSError it returns `None` and the run proceeds with
  no lock and no named record (fail-open). The fleet runs six sibling
  checkouts (`audio-shokunin-wt-r96…r100` + main), each with its own
  `corpus/live` — two same-family runs in different checkouts never exclude
  each other.
- **Amplifier:** the C fixture builds stream node names **without the pid**
  (`r98stream.c:755`, `snprintf(namebuf,…, "r98a_%s", d.name)`), and the
  route/cap witnesses match those bare names (`r98a_t_serial`, `r98a_envnode`,
  `r98a_t_prefix`, …; 48047, 48073, 48093, 48123, 48378, 48390). The pid-tagged
  sinks (`r98a_ns_<pid>`) cannot collide; the probe stream nodes can. Two
  overlapping runs would read each other's links in `link_snapshot` and both
  could summarize green.
- **Evidence:** inferred from source (all 11 runs were serialized inside
  wt-r98 by a working lock; no collision occurred). The lock fail-open branch
  is source fact.
- **Impacted axes:** operability (lock scope), depth (witness integrity).
- **Smallest correction:** (a) on lock-open failure, name it — record
  `family_lock: "unavailable"` in the entry and put it in `failures` per F1,
  or fall back to a host-wide path; (b) make the Python pass pid-suffixed
  `name=` values (it already computes `PWSTREAM_R98_PREFIX`) so probe node
  names are seat-owned like the sinks.

### F5 — LOW, fixable hardening: the pw-dump readers never check the exit code; a clean exit with empty output fabricates the empty graph the docstring warns against

- **Where:** `_pwstream_r98_graph` 46668–46702 and `_pwstream_r98_sb_nodes`
  47163–47168: `json.loads(proc.stdout or b"[]")` with no `proc.returncode`
  check. The graph reader's docstring (46662–46664) explicitly promises to
  *"return {"error": …} rather than fabricating an empty graph (an empty graph
  would silently pass every absence arm)"* — but only the
  timeout/OSError/JSON paths produce an error; `pw-dump` exiting 0 with empty
  stdout yields a truthy empty graph.
- **Mitigation in the shipped arms:** every absence arm is paired with a
  positive control that redd on a dead core (the sandbox geometry arms need
  `streaming`; the bare twins need `paused`, which a dead core cannot report;
  teardown's final witnesses are pactl-side). So no shipped arm goes green on
  this path today — it is a hardening gap against future arms, not an
  observed false green.
- **Smallest correction:** `if proc.returncode != 0: → error leaf` in both
  readers.

### F6 — LOW, calibration: `_pwstream_r98_streaming_leg` is dead code whose contract contradicts the shipped behavior

- **Where:** defined at 46961–46993, **never called** (grep over the pin blob:
  only the definition). All entries implement the §3.5 transient pattern
  inline: one retry, then a named `coverage_blocked` — which is what the
  reports document.
- **Hazard:** if a later seat adopts the helper, it double-retries (its second
  `_pwstream_r98_run` keeps the default `retry_transient=True`, so a stuck leg
  spawns up to 4 processes) and drops the first attempt's record from `legs`
  entirely (the internal retry in `_pwstream_r98_run` likewise replaces the
  first record with the retry's — recovered legs keep only
  `transient_recovered`, and the first attempt's raw output is not in the
  receipt).
- **Smallest correction:** delete the helper (simplifier-class), or pass
  `retry_transient=False` in its second call and keep the first record under
  `key + "_first"`. Either way, do not let its docstring's "retried once"
  describe a two-layer retry.

### F7 — LOW, calibration (declared-tradeoff candidate): load-sensitive timing arms fail in the safe direction but can red under fleet load

- `stall_gap_ms` bands [250,400]/[550,700] (48402–48406) arm a `usleep()`
  wall clock; the boundary measured ambient loadavg 56–67 on this host, the
  author's window 51–55 early and 4–7 during the greens. An overshooting
  usleep under load reds the injection arm that actually ran.
- `trigger_count ∈ [29,30]` (47749–47751) arms a 40 ms re-arm cadence against
  the fixture's hard cap of 30 (`r98stream.c:523`); late timer fires under
  load drop the count below 29.
- The `time` legs' deactivation at cb 8 inside `ms=2600` (47789–47794) assumes
  the ~256 ms callback cadence holds; a stretched cadence leaves
  `get_time_after_deactivate_rc` at its init value → red.
- All three fail **false-red**, never false-green — safe direction, but a
  verifier run under the boundary's load regime could red rows that are load
  artifacts, not law violations. This is a tradeoff the lead may accept (tight
  pins = sharpness); naming it so the verifier's red is interpreted against
  the receipt's `loadavg`/`contention` fields.

### F8 — INFO, disclosed tradeoff confirmed in the pinned bytes: the teardown witness remains pactl-primary

- `_pwstream_r98_teardown`'s final census uses
  `_capture_r77_sink_names_strict()` / `_playback_r78_node_names()` (46865,
  46877) — the pulse-socket table that the author's §4.2 showed can be
  interposed by a foreign `pipewire-pulse` (green `sinks_gone` while sinks
  reappeared owned by a sibling's server). The pw-dump graph sweep
  (46854–46864) runs mid-teardown, but the final witnesses are pactl. The
  author's own §6 recommends pw-dump-primary for a later seat. **Declared
  loss of coverage, not a hidden regression** — recorded here so the pin's
  bytes are not credited with the stronger witness.

### F9 — INFO, positive: the claims the banner makes about hygiene are true in source

- No `pactl set-default-*` anywhere in the block (the only `set-default` hit
  is the banner comment; the block's own `pactl` use is the read-only
  `get-default-sink` plus the helper-mediated own-sink load/unload).
- Env-lever clearing is real (46410–46419) and censused (46770–46771; empty in
  both green runs); `RLIMIT_CORE=0` is armed **only** on the crash-class legs
  (`core_limit=True`, 48453/48465) and the sandbox daemons; every spawned
  process is its own session leader with SIGTERM→SIGKILL group escalation
  (6 `_alsapw_r84_killpg` sites); the C fixture checks
  `pw_main_loop_new`/`pw_context_new`/`pw_context_connect` NULLs (708–726)
  after the boundary's rc −11 lesson; `param_ids[16]` and `cb_log` writes are
  bounded (221, 239).

---

## 2. What the evidence does support

- **Measured (receipt-backed, two independent batteries on the final bytes):**
  the 67-leg census per entry; the trigger FALS (30 calls → 3 buffer-cadence
  callbacks); the rate-relative geometry (12288 rate-matched, 13375 upsampled,
  both armed as a set); the latency lever; the prop-level AUTOCONNECT gate
  with env precedence; the 7-event non-RT / 5-event RT param lattices; the
  drain period relative to the leg's own request; the xrun linearity (27/55,
  ratio 2.037, driver 0); the crash class recorded-not-gated with the
  Audio/Source twin's state honestly unpinned; the bare-core re-attribution of
  the refusal/fallback to WirePlumber policy; the no-ALSA sandbox profile.
- **Disclosed-blocked (honestly named in the receipts):** the `cap_noprop`
  policy cell (one per green run) — recorded, never armed. The wedge-era run's
  blocks are retained as harness history.
- **Not measured anywhere:** the landed blob's shared wiring was never
  exercised by a full battery **on the landed bytes** (integration ran
  compile/help/mutex checks only). I verified the block, the dispatch block,
  the argparse row, the C fixture, and all 12 called helpers are
  byte-identical to measured configurations, so the residual risk reduces to
  runtime interaction with main's later landings — which do not execute in
  pwstream mode. I judge that residual negligible, but it is the honest
  boundary of what the greens cover.

## 3. Residual risks and explicit checks not run

- No live family run (critic role); the verifier seat owns the single live run
  on the minimal frozen export. My F1/F2/F3 findings are exactly the paths a
  verifier run could exercise (a wedge or a sandbox-start failure mid-run).
- No receipt re-derivation, no raw `raw/*.out` re-reads beyond the receipt
  JSONs, no scout/boundary receipt re-audit (reports read as evidence).
- The duplicate-Link question stays unresolved by design (recorded, never
  armed) — the author's port-level-witness recommendation stands.
- The foreign-interposition teardown blind spot (F8) is unfixable inside this
  family's pactl witness; it needs the pw-dump-primary rework the author
  already proposed.
- I did not verify the `_pwcat_r83_ns_load`/`_pactlmon_r85_unload_own`
  internals beyond their pin-vs-base byte identity; their behavior is
  inherited r83/r85 evidence.

## 4. Artifact paths and attribution

- Report (this file):
  `/home/vgpnk/Projects/shokunin/audio-shokunin/reports/round-98/r98-critic.md`
  — the only tracked-path file this seat writes.
- Scratch (untracked):
  `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-critic/` —
  `commands-and-hashes.txt` (verbatim command log + all hashes),
  `measure_audio.py` / `r98stream.c` / `block.py` (pin extractions used for
  line-referenced reading; not executions).
- Evidence read (frozen, untracked, **local only — not committed, not remote**):
  `audio-shokunin-wt-r98/corpus/live/runs/{20261016T101046237597Z,
  20261016T101258039942Z,20261016T092555426767Z}-pwstream-r98/measurements.json`
  and `audio-shokunin-wt-r98/corpus/live/r98-author/r98block.py`.
- Reports read: `reports/round-98/{r98-scout,r98-boundary,r98-author,
  r98-integrate}.md` (committed tracked files).
- Attribution: all line numbers refer to the pin blob
  `bb177513a615a32d3bc150ecbdcf78302e110d8c` of
  `corpus/fixtures/measure_audio.py` unless the file is named. Findings F1–F6
  are fixable defects with one-line-scale corrections; F7/F8 are declared
  tradeoffs for the lead to accept or reject. No round is admitted here; the
  canonical Rust runtime remains the sole judge.
