# r98 verifier — single live family run on the frozen minimal export

Advisory review seat. This report is not a shipping or gate-admission
decision; the canonical Rust runtime remains the sole judge.

## 1. Identity, scope, commands actually executed

- **Role**: verifier (leaf; no subagents, no routing edits, no source edits,
  no commits, no service restarts, no other live family).
- **Round / flag**: N=98, `--probe-pwstream-r98` (FLAG `pwstream-r98`).
- **Source pin**: `bb177513a615a32d3bc150ecbdcf78302e110d8c`
  ("r99 safety: require explicit opt-in before physical LAN control",
  2026-10-16 09:29:41 -0300). The r98 landing `d41cfa68` is in the pin's
  ancestry; the pinned blob's r98 family block is byte-identical to the
  integration-verified block (2351-line window sha256
  `ba7e3b58fbae83df040bef69d4568e9e0eb51526f7d5f8bdcbf71bda46471ada`,
  found at blob lines 46326–48676; dispatch block sha `965e7e3d…` at
  lines 55142–55172; argparse row line 54390; mutex token in the line at
  54400; mode/suffix ternaries at 55944/55964).
- **Model pin**: `glmseat` skill invoked as first action
  (`.devin/skills/glmseat/SKILL.md` — seat pinned to glm-5-3-flash-max);
  Godspeed loaded once. Axes for this audit: depth, coverage,
  calibration, operability (wwkd-plan M3).
- **LSP**: no LSP server/device was available to this seat for the Python
  fixture. All source statements below are literal text inspection of the
  pinned blob (`git archive` export), not semantic proof; receipt facts
  are JSON reads of frozen files.
- **Commands executed** (literal record in
  `audio-waveb-resume/r98-verifier/command.txt`):
  1. `git -C $REPO archive bb177513a615a32d3bc150ecbdcf78302e110d8c
     corpus/fixtures corpus/artifacts | tar -x -C $SCRATCH/tree`
     → rc 0, 6.0 MB export; author/live evidence intentionally omitted
     (generated stimuli regenerate; nothing borrowed).
  2. In the exported tree, exactly:
     `env -u RTP_R99_ALLOW_LAN_CONTROL UFO_SEAT=r98-verifier-resume
     PYTHONDONTWRITEBYTECODE=1 timeout 1500 python3
     corpus/fixtures/measure_audio.py --probe-pwstream-r98`
     → **rc 0**, wall ≈ 2 m 40 s, stderr empty, stdout exactly:
     `{"receipt": ".../tree/corpus/live/runs/20261016T124040716973Z-pwstream-r98/measurements.json", "failures": {}}`
  3. Read-only post-checks: receipt audit, residue census
     (`pactl list modules/sinks short | grep r98a_` → 0/0; no `r98a`
     processes; defaults unchanged SPDIF/Line; `RTP_R99_ALLOW_LAN_CONTROL`
     absent from the environment), sha256 of receipts.
- **Fixture identity in the export**: `corpus/fixtures/r98stream.c` sha256
  `9f840a6b8b23196124270d96532b3b35b2b868d089aef4eb58ad2d6b0950d323` —
  equals the author's recorded fixture sha. The family compiled and ran
  its own probe (`probe_build` records source/binary under `/tmp`).

## 2. Findings (by severity)

### F1 — xw entry: profiler cross-witness unmeasured in this window (coverage block, honestly labeled) — LOW, observed
- **Path**: pinned blob `corpus/fixtures/measure_audio.py` lines
  48385–48417 (xw entry `pwstream_xw_r98_probe`, def at 48333); receipt
  `measurements.pwstream_xw_r98_probe`.
- **Failure path**: `pw-profiler -J -n 900` is run with a 20.0 s bound and
  SIGKILLed at it (`timeout_s=20.0`, line 48386; killpg at 48391). In this
  window both stall legs' profiler stdout was truncated mid-record and
  unparseable (`parse_error`: "Expecting ',' delimiter…char 376831" /
  "Unterminated string…char 368640"; `exit_code -9`,
  `killed_at_bound: true`, `wall_s` 20.015/20.013) → lines 48408–48412
  appended `x_stall300` / `x_stall600` to `coverage_blocked`;
  `xrun_ratio_600_300 = None`.
- **What is still measured**: the probe-side injection arms are
  deliberately profiler-independent (lines 48399–48406) and passed:
  `stall_gap_ms` 300/600 (bounds [250,400]/[550,700]), `stall_start_ms`
  517, `stall_end_ms` 817/1117, both legs `streaming` with stable
  geometry 49152 B / 12288 frames / stride 4. The crash-class negative
  control recorded `rc −11 SIGSEGV`, `gated: false`; the `Audio/Source`
  twin rc 0 + `paused` + param ids `20,15,17`.
- **Consequence**: the follower-xrun counts (≥10 / ≥40), driver-0 witness
  and the 600/300 ratio (author's frozen value 2.037) are **unmeasured in
  this window** — blocked, not green, not red. The fixture's own
  disclosure (§5.5 of the author report: profiler wall time varied 2×
  between batteries) predicted this fragility; my window pushed the parse
  over the truncation edge.
- **Smallest correction**: none required for honesty (the block is
  disclosed by the fixture itself). A later seat could parse the partial
  JSON stream or raise the bound; that is a source change, out of this
  seat's scope.
- **Observed**, with the mechanism confirmed in pinned source.

### F2 — minimal export silently downgrades the fixed-path family lock — LOW, observed
- **Path**: pinned blob line 46743 (`path = ROOT / "live" /
  "measure_audio-pwstream-r98.lock"`), lock helper 46739–46756, acquired
  at 55160 ("held to exit").
- **Failure path**: the recipe's export contains only `corpus/fixtures`
  and `corpus/artifacts`, so `corpus/live/` does not exist when the lock
  is taken; `os.open(..., O_CREAT)` raises ENOENT, the helper returns
  `None`, and the run proceeds **without** the same-family exclusion.
  Moot here (one verifier per family, run exactly once), but a second
  concurrent `--probe-pwstream-r98` in a fresh export-layout tree would
  not be excluded. (After the run, `corpus/live/runs/` exists — created
  by the receipt writer — so only the *first* run in a fresh export is
  unguarded.)
- **Smallest correction**: `mkdir(parents=True)` the lock's parent before
  open — a one-line source change, out of this seat's scope; recorded
  only.
- **Observed** (lock file absent at dispatch time in the export; run
  alive and past the lock call).

### F3 — author receipt paths resolve in the author worktree, not the main checkout — INFO, observed
- The author report cites
  `corpus/live/runs/20261016T101046237597Z-pwstream-r98/measurements.json`
  and `…101258039942Z…`; those relative paths do **not** resolve in the
  main checkout's `corpus/live/runs/` (no `*pwstream-r98` dirs there).
  They exist, intact, in the author worktree
  `audio-shokunin/audio-shokunin-wt-r98/corpus/live/runs/` (untracked,
  "not carried", as the integration note says). Both verify read-only:
  67 legs (15+18+12+4+4+14), per-entry `failures: []`, exactly one
  disclosed coverage block (`cap_noprop` policy row) — matching the
  author report's claims. sha256: `7cc43ba1…` (run 1), `3a4c209f…`
  (run 2); wedge-affected first attempt `bcb15eee…` also present.
- **Smallest correction**: a future addendum could cite the
  worktree-qualified path; report edits are out of this seat's scope.
- **Observed** (path resolution + JSON reads; nothing re-run, nothing
  overwritten).

### F4 — `cap_noprop` policy row blocked in every window so far — INFO, observed
- The WirePlumber "no target node available" refusal for a prop-less
  capture targeting a sink did not reproduce in the author's two windows
  or mine (state `streaming`, tone captured) — recorded, never armed, in
  all three receipts. Consistent with the author's §5.4 disclosure; the
  **target-less** refusal arm (which does reproduce) is the armed row.

## 3. What the single live run supports (measured, this window)

`--probe-pwstream-r98` on the pinned minimal export: **67/67 legs** across
the six entries (core 15 / run 18 / route 12 / cap 4 / xw 4 / sbx 14),
per-entry `failures: []`, stdout summary `failures: {}`. rc 0 is **not**
read as complete coverage: the three coverage blocks above are visible in
the receipt (1 disclosed policy row + 2 profiler-witness blocks).

65/67 legs' armed values reproduce the author's two frozen batteries
exactly, including:
- gate geometry ×2 reps: 49152 B / 12288 frames / stride 4 / requested
  1024 (both runs and mine);
- drain period 43.0 ms at own request 1024 (2·1024/48000 = 42.7 ms);
- `ticks` 87040 == 87040 across the two structurally equal time legs;
- trigger FALS: 30 `trigger_process()` calls, rc 1, **3** callbacks at
  421/901/1381 ms (author run 1 identical; run 2 422/902/1382);
- activation arm: 4 callbacks at 602/858/1114/1370 ms;
- RT_PROCESS: separate tid (1428464 vs main 1428462), sched 1073741824
  (SCHED_OTHER|RESET_ON_FORK), 5-event param lattice `20,15,17,17,4`;
  main-thread twin: same tid, sched 0, 7-event lattice
  `20,15,17,20,15,17,4`;
- `node.latency=512/48000` request lever: `size` 512 with `maxsize`
  unchanged;
- capture pins: 71680 frames, nz 69629, peak 0.499969, g997
  302974735.061 / g440 6.403 — identical to the last digit in all three
  receipts;
- sandbox: q512/q1024/q2048 → 49152/12288 with requested following the
  quantum; 44100-graph rate axis → upsampled 53500 B / **13375 frames**
  vs matched 49152/12288 (the boundary's rate-relative law); bare-core
  twins (no session manager) → `paused`, no link, no refusal, no
  fallback, no error; private WP hardware monitors disabled
  (`alsa_nodes: []`);
- routing: 3-rep exact-target stability census all `streaming` to
  `r98a_ns_<pid>`; core rc lattice reproduced (bad remote −112 EHOSTDOWN,
  second connect, direction-99, 0-params → paused, pre-connect −5/−95
  lattice, dequeue NULL).

Teardown verified two ways: per-entry `sinks_gone` all-true /
`own_nodes_after: []` / name-verified unloads rc 0, **and** an
independent post-run census (0 `r98a_*` modules, 0 sinks, 0 processes;
defaults SPDIF/Line unchanged). `inherited_env_levers: []` in every
entry (no `PIPEWIRE_*` lever leaked in). loadavg 0.28–0.69 — a quiet
window, unlike the author's 51–55; three sibling verifier lanes
(r93/r99/r100) were concurrently live on the shared graph and the
relative arming absorbed them (no red, no transient `paused` class
observed; route stability 3/3 clean).

## 4. Residual risks and explicit checks not run

- **xw cross-witness**: follower-xrun counts, driver-0 and the 600/300
  ratio are unmeasured in this window (F1). The author's frozen
  ratio 2.037 stands as their evidence, not re-measured here.
- **Not run**: any second family run (recipe = run once); any other
  probe mode; `--help`/mutex re-checks (the integration's narrow checks
  stand as recorded); any re-derivation or overwrite of author receipts;
  no full-repo archive; no tar copying; no source edits; no service
  restarts; shared daemons left running and untouched.
- **Not verifiable from this seat**: whether the 44100 shared-graph
  window class (boundary §3.2/§3.5) can recur — not armed, not observed
  here; the duplicate-Link count split (author §5.1) remains unresolved
  by design (recorded, never armed); the `media.class` SIGSEGV's exact
  dereference (scout `[?]` 4) — the crash reproduced (rc −11) but no
  debugger was attached.
- **Environment**: the family lock was inert in the fresh export (F2);
  TMPDIR was not set (recipe does not set it), so probe scratch went to
  `/tmp` — ephemeral, no evidence dependency.
- LSP unavailable (recorded in §1); no semantic-proof claims are made.

## 5. Artifacts and attribution

- **New receipt (this seat's single run)**:
  `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-verifier/tree/corpus/live/runs/20261016T124040716973Z-pwstream-r98/measurements.json`
  — sha256 `8520d7c8bf6c59a0f931df62e5333a0f74135b610c33f1cf974a2bd54435561e`.
  Local to this seat's scratch; not committed, not remotely available.
- **Scratch**: `audio-waveb-resume/r98-verifier/` — `command.txt`
  (literal recipe + run command), `run.stdout`, `run.stderr` (0 bytes),
  `run.rc` (0), `tree/` (the minimal export + the run's receipt).
- **Frozen inputs cited (read-only, untouched)**: author receipts in
  `audio-shokunin/audio-shokunin-wt-r98/corpus/live/runs/
  {20261016T101046237597Z,20261016T101258039942Z,20261016T092555426767Z}-pwstream-r98/`;
  round reports `reports/round-98/r98-{scout,boundary,author,integrate}.md`;
  wave assignment `.ufo/waves/shokunin-train-20261016-w24/
  {review-common,review-roles,wwkd-plan}.md`.
- **Attribution**: run executed by this seat only (UFO_SEAT
  `r98-verifier-resume`); all measured values above are from that run or
  quoted from the frozen receipts as labeled. Lead inspect the cited
  receipt for the quantitative check. No round is admitted here; no
  canonical judge verdict is claimed.
