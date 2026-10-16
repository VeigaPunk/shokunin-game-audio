# r93 reviewer — independent read-only audit of the pinned `ebur128` family

## 1. Identity, scope, commands

- **Seat:** reviewer (leaf; no subagents). Round **N=93**, role **reviewer**.
  `glmseat` skill invoked as first action: it is a model pin only
  (`glm-5-3-flash-max`, `.devin/skills/glmseat/SKILL.md`) with no executable
  content; this seat's runtime already satisfies it. No routing, profile or
  session state was touched.
- **Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c`
  ("r99 safety: require explicit opt-in before physical LAN control",
  2026-10-16 09:29:41 −0300). All line numbers below resolve against
  `git show PIN:corpus/fixtures/measure_audio.py` (55,974 lines); a verbatim
  copy is kept at `audio-waveb-resume/r93-reviewer/measure_audio.pin.py`
  (sha256 `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`).
- **Scope:** the r93 family region (lines 48679–50670) plus its wiring
  (54387, 54400–54401, 55173–55228, 55944, 55964–55970); the round's
  scout/boundary/author reports; the r93 section of
  `reports/round-100/r93-r99-r100-integration.md`; and the local integration
  receipt `corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`
  (read-only; not re-derived, not overwritten).
- **LSP gap (recorded):** no LSP server/device answers files in this seat, so
  every citation is literal source inspection of the pinned bytes. No grep
  output is presented as semantic proof; greps were used only to locate
  symbols, and each finding was then verified by reading the cited region.
- **Commands actually executed:** `git cat-file -t` / `log -1` / `ls-tree -r`
  / `show --stat` / `diff 74b75fce PIN` / `cat-file blob | sha256sum` on the
  pin; `git show PIN:corpus/fixtures/measure_audio.py` (exported to scratch);
  `git check-ignore -v` on the receipt and stimulus paths; read-only python
  inspection of the integration receipt (leg counts, coverage blocks,
  stimuli sha256 spot-check, hygiene fields); `ls` of the author worktree's
  run receipts; line-range reads of the pinned source. **No live family was
  run** (this seat is not the verifier), no receipt was re-derived, no
  service touched, nothing committed.

## 2. Findings, by severity

### M1 (Medium) — a whole claim class can drop out with rc 0 and empty `failures`; the green signal does not encode coverage loss

- **Where:** `_ebur_r93_run` 49734–49753; per-row checks that `continue` on
  `arm_failed` (entry 3: 50048–50050, entry 5: 50230–50231); the exit-code
  accumulator 55968–55970 (`failed = {k: v["failures"] …}; return
  bool(failed)`); the missing-tools block `_ebur_r93_block` 49706–49716,
  called at 49833–49835.
- **Failure path:** an arm failure is recorded only in `coverage_blocked`
  (49749–49752), never in `failures`. Entries 3 and 5 check laws per row and
  skip arm-failed rows, so a failure class that hits *only* their arms leaves
  those entries with `failures: []`. Concrete trigger: a regression of the
  author's own §5.4 bug 2 (stereo legs loading a 1-channel sink → feed link
  never binds, 49407–49411) arm-fails all 10 `ch_*` legs and the 2 stereo
  `p_st`/`tp_st` legs → 12 legs coverage-blocked, `failures: {}` across all
  nine entries → **rc 0**. Mono claim classes have backstops that make total
  loss non-green (entry 2's k-weighting base check 49989–49994 fires "no
  finite 1 kHz leg"; entry 4's post-capture check 50151–50156 fires on a
  missing tap; the daemon gate 49590–49623 + 55190–55209 exits non-zero) —
  the *stereo* class has none.
- **Evidence:** source read as above. Precedent observed: the author's 10:02
  run hit exactly the stereo-sink-width class (r93-author.md §5.4 bug 2) and
  was caught only by manual inspection, in a run that was already non-zero
  for unrelated reasons. The blocked-attempt receipts (§5.3) show the gate
  path is loud; no receipt in this tree shows the stereo-class green hole.
- **Smallest correction:** in `_ebur_r93_run`, after the rep loop, append a
  `failures` entry when every rep of a non-`expect_refusal` arm is
  `arm_failed` ("arm <tag>: no rep produced a measurement"); and have
  `_ebur_r93_block` append its message to `failures` as well (today the
  missing-tools block leaves `entry["failures"] = []` → rc 0 for that entry).
- **Observed/inferred:** the code path is source-observed; the end-to-end
  green receipt is inferred (not reproduced — no live families from this
  seat). Calibration note: the author's "a blocked run exits non-zero and can
  never read as green" (§3.3 law 1; dispatch comment 55200–55203) is true
  **only for the daemon-gate class**; arm-failure coverage loss is designed
  to be non-failing and visible only in `coverage_blocked`, so the lead's
  read of that field is the actual safeguard, not the exit code.

### L1 (Low) — entries 3–8 have no `try/finally`; an exception there skips the entry teardown and loses the whole receipt

- **Where:** entries 3–8 (50016–50571) run their loops and call
  `_ebur_r93_teardown` inline (50107, 50184, 50240, 50313, 50392, 50570) with
  no `try`; entries 1/2/9 wrap the body in `try/finally` (49836/49910,
  49934/49975, 50584/50665). The dispatch calls the entries bare
  (55211–55228).
- **Failure path:** an unexpected exception inside an entry-3..8 loop (e.g.
  the unbounded `communicate()` at 49244 hanging aside, any `KeyError`/
  `TypeError` from a helper) propagates past the entry: the entry-level
  teardown census (residual destroy, `sinks_gone`, `own_nodes_after`,
  `own_procs_after`, 49651–49703) never runs, and main() dies before the
  receipt write (55967) — no `measurements.json` at all. Per-leg cleanup
  still fires (`_ebur_r93_leg`'s own `finally`, 49448–49461), so objects are
  reclaimed; what is lost is the witness and the receipt.
- **Evidence:** source read; contrast with the r99 family in the same pin,
  whose `rtp_e2e_r99_entry` wraps its body in `except Exception` + `finally`
  (pin ~52647–52653) — the robustness convention exists in-repo but was not
  applied to r93's entries 3–8.
- **Smallest correction:** give entries 3–8 the same `try/finally` shape as
  entries 1/2/9 (teardown in `finally`), optionally recording the exception
  as a named failure.
- **Observed/inferred:** inferred (no exception observed in the local
  receipt; all nine entries completed there).

### L2 (Low) — rep loss degrades evidence without a failures-level trace; rep counts are declared, not enforced

- **Where:** `_ebur_r93_run` 49734–49753 records only rows that ran; every
  entry iterates existing rows; entry 7 pairs plateaus with
  `zip(got["h_sil_default"], got["h_sil_cap2"])` (50363–50374), which
  truncates to the shorter list. No code asserts `len(rows) == reps`.
- **Failure path:** one rep of a `reps=2` arm arm-fails → the surviving rep
  satisfies the law → entry green, rc 0, with the lost rep visible only as a
  `coverage_blocked` string. The author's stated evidence basis ("reps are 2
  for the armed arms", r93-author.md §6) is then 1 without a `failures`
  entry.
- **Smallest correction:** per arm, compare produced rows against `reps` and
  append a failure on shortfall (or record `reps_measured` per arm and let
  the lead's limits read it).
- **Observed/inferred:** inferred; the local receipt shows full reps
  (17/9/10/11/6/6/8/9/14 = 90).

### L3 (Low) — family-lock creation failure silently drops the exclusion safeguard

- **Where:** `_ebur_r93_family_lock` 49571–49587 returns `None` on
  `os.open` OSError; the call site 55188 (`_r93_family_lock =
  _ebur_r93_family_lock()`) ignores the result.
- **Failure path:** an unwritable `corpus/live/` (read-only bind, disk full,
  perms) → no lock is taken and the family runs **without** the same-family
  exclusion that the header (48715–48719) and author §2.3 claim as an
  inherited guard. Two concurrent `--probe-ebur-r93` runs would then interleave
  on the shared daemon. The lock discipline itself is sound where the file is
  creatable (flock held to exit; flock releases on process death, so no stale
  lock class; but the wait at 49580 is unbounded — bounded in practice by the
  driver's external timeout).
- **Smallest correction:** on open failure, return a typed record and route
  the family through `_ebur_r93_block` (or append to `failures`) instead of
  proceeding unguarded.
- **Observed/inferred:** inferred (lock file exists and works in this tree;
  the failure branch is unread code).

### L4 (Low) — a slow module load double-loads the filter-chain; only the last var is unloaded

- **Where:** `_ebur_r93_load_module` 49148–49184: 1.0 s post-send sleep
  (49157), then a retry that sends `load-module` **again** (49155–49156); the
  var scan takes the last `= @module:` line (49160–49164).
- **Failure path:** a load slower than 1 s misses the var on attempt 1; the
  attempt-1 module (whose var line can still arrive inside attempt 2's
  window) is never unloaded — two chains meter simultaneously and the series
  interleaves. Mitigation exists: teardown's residual sweep destroys any
  surviving `r93a_<pid>`-named **node** by id (49661–49671), but a node
  destroy is not a name-verified module unload.
- **Smallest correction:** before retrying, rescan the accumulated session
  text for a late var from the previous attempt and adopt it instead of
  re-sending.
- **Observed/inferred:** inferred; the integration receipt's attempts show
  first-try loads (the `notify_bogus` leg's three attempts are refusals, not
  slow loads).

### L5 (Low) — `own_procs_after` cannot see a leaked `pw-cli`

- **Where:** 49695–49703: the census greps `ps -eo pid,cmd` (argv only) for
  `EBUR_R93_PREFIX` among `pw-(play|record|cli)` lines. A `pw-play` carries
  the prefix via `--target` and a `pw-record` via its tap path, but a
  `pw-cli` session's argv is just `pw-cli` (49094) — the prefix lives in its
  environment, which `ps` does not print.
- **Failure path:** a `pw-cli` that ignores `quit` and survives
  `_ebur_r93_cli_close`'s killpg (D-state) is invisible to the witness; the
  node-level sweep still catches its `r93a_` nodes, but the process witness
  reports `[]` — the same class as the author's own disclosed leak
  (r93-author.md §5.1), which was found by cwd, not by this census.
- **Smallest correction:** match the session marker in `/proc/<pid>/environ`
  or record the spawned pw-cli PIDs at open time and check those exact PIDs
  at teardown.
- **Observed/inferred:** inferred from source; the leak precedent is the
  author's own disclosed observation.

### I1 (Info) — `pw-record` is absent from entry 1's tool census; its absence produces a misattributed (but fail-closed) failure

- **Where:** the tool check 49828–49829 lists `pw-cli, pw-play, pw-link,
  pw-dump, pactl`; `pw-record` is used by the capture taps (49262).
- **Path:** missing `pw-record` → `_ebur_r93_capture_start` records
  `capture_error` and the tap is skipped (49373–49377) → entry 4 fails with
  "the Window-only graph is not a live pass-through" (50151–50156) — a tool
  absence reported as a graph-semantics failure. Entry 8's `g_default`
  reports it correctly as "audio-domain ratio unmeasured" (50513–50526).
  Direction is fail-closed (rc 1), the class label is wrong.
- **Smallest correction:** add `pw-record` to the tool census.
- **Observed/inferred:** inferred.

### I2 (Info) — tap residue: the per-run `mkdtemp` tap directory is never removed

- **Where:** `_ebur_r93_ctx` 49565–49568 creates `r93a-tap-*` under TMPDIR;
  nothing deletes it. Tap WAVs (MB-scale per run) accumulate outside the
  repo. Not evidence corruption; disk residue only.
- **Smallest correction:** `shutil.rmtree(tapdir, ignore_errors=True)` in the
  family-level teardown.

### I3 (Info) — the `-3.003596` calibration constant is claimed byte-stable but is armed only at the looser reference tolerance

- **Where:** entry 2's table passes `None` as the constant for
  `tone_1k_100` (49927), so the 1e-4 constant check (49962–49967) is skipped;
  the row is pinned only by the 1e-3 own-reference check (49956–49961). The
  author's §6 cross-run identity list includes `-3.003596` as byte-stable.
- **Smallest correction:** pass `EBUR_R93_CAL_…` for the 1.0 row (or state
  in the report that this row's constant is evidence, not an armed law).
- **Observed/inferred:** source-observed; the byte-stability itself is the
  author's receipt evidence (not re-derived here).

## 3. What the evidence supports

Verified against the pinned bytes (line cites) and the local integration
receipt:

- **Wiring is exactly as claimed:** `--probe-ebur-r93` argparse row (54387),
  mutex membership with `parser.error` on >1 mode (54400–54401), dispatch
  under `args.probe_ebur_r93` (55173–55228), mode string (55944), receipt
  suffix `-ebur-r93` (55964), fixed lock path
  `corpus/live/measure_audio-ebur-r93.lock` (49575).
- **Nine entries, 90 leg keys:** static count from the pinned arms
  (topology 17 = 2+7+1+7; cal 9; channel 10; modes 11; peaks 6; window 6;
  history 8; gain 9; error 14) equals the integration receipt's per-entry
  leg counts and its 90 total; equals the author's "90 armed legs".
- **The two disclosed coverage blocks are the only ones, and the source
  produces exactly them:** receipt `coverage_blocked` = `notify_bogus`
  (×1, `cls=pwcli_module_load_fail`, `control_class=load_refused`, 3/3
  attempts refused — via the r88 errclass fallback 48817) and `g_default`
  (×2, `pre mid_rms 0.2098 / post 0.0` → "audio-domain ratio unmeasured",
  50513–50526). The integration note's "the message occurs twice; not two
  new measured arms" matches reps=2. `notify_bogus` correctly does **not**
  carry `expect_refusal` (both outcomes are claims); the six must-refuse
  arms (`g_unquoted` + five `e_labelfail_*`) do (50553, 50650).
- **The daemon gate matches its claim:** bounded 60 s (48739, 49590–49623),
  `pactl info` + `pw-dump` census with `stdout_bytes > 1000` (49601–49608;
  `stdout_bytes` is the true drained length per `_btwit_r88_run` 27793, so
  the gate's comment is accurate), and the gate block names itself in
  `failures` so the run exits non-zero (55190–55209). The green receipt has
  no gate key (gate passed silently).
- **JSON safety matches the claim:** writer `allow_nan=False` (55967);
  `_ebur_r93_json_safe` scrubs every entry on return (all nine return
  sites); non-finite floats become verbatim `"nan"/"inf"/"-inf"` literals
  (48774–48798); deltas over non-finite pairs become literal classes
  (48801–48809).
- **Inherited guards are real in source:** name-verified unloads re-read the
  module index immediately before firing (`_pactlmon_r85_unload_own`
  21880–21903; per-leg finally 49448–49461; entry teardown 49651–49703);
  bounded process groups with `start_new_session` + SIGTERM→SIGKILL
  escalation (49094–49097, 49219–49222, 49269–49272, 19202–19206,
  49449–49454); the pw-cli session lifecycle closes stdin and bounds the
  wait (49131–49145), matching the author's §7.7 fix; **no
  `pactl set-default-*` anywhere in the r93 region or its helpers** (the
  only `set-default` sites in the file are the r78 family at 7089/7108 and
  comments).
- **The own BS.1770 reference is computed over the bytes the arm fed:**
  refs derive from the same in-memory builders that are written to the WAVs
  (49488–49560), not from a capture tap — author §3.3 law 3 holds.
- **Self-containment holds:** every helper the r93 region calls is in-file
  (r77 11902, r78 6149, r79 8949, r83 16634, r84 19202, r85 21880,
  r88 27702–27833); the 14 stimuli are analytic and source-generated
  (49488–49538) with the output directory auto-created (48847);
  `corpus/live/round-93/` has **zero tracked files at the pin** (verified by
  `git ls-tree`) and is not gitignored (`check-ignore` rc 1) — the WAVs
  regenerate per run and their sha256s are recorded per entry
  (`_ebur_r93_entry_head` 49645–49648); the integration receipt's stimulus
  sha256 16-prefixes match the author's §3.1 table exactly (spot-checked
  `tone_1k_050` `b377abe8db044e44`, `tone_1k_100` `e91db1c3c3d26c34`,
  `st_mix` `7a11577c41f616bd`).
- **Pin provenance is clean for r93:** the whole file at the r93 integration
  commit `74b75fce` hashes to `59708fca45b5ee51…`, exactly the integration
  note's r93 stage sha; the r93 region (through the end of entry 9) is
  byte-identical between `74b75fce` and the pin; the pin's own diff touches
  measure_audio.py in a single hunk at `@@ -52605,34` (r99 region) and adds
  `test_rtp_r99_lan_control.py` — the r93 family is untouched by the pin's
  headline change.
- **Pin context (scope only; the deep audit is the r99 reviewer's):** the
  physical-LAN positive control now runs only when
  `RTP_R99_ALLOW_LAN_CONTROL == "1"` (pin ~52615–52645) and otherwise
  records a named coverage block with `measured: False` — default-off as
  required. The r93 family never reads that variable and arms no network
  traffic at all (every edge is a local `pw-link`; the only sockets are the
  daemon's own).
- **Receipt scope honesty:** in `--probe-ebur-r93` mode the base battery
  also runs (the integration receipt's `measurements` carries the 16 base
  entries plus the nine r93 entries), and base-battery failures would also
  fail the run (55968–55970) — the "nine entries / 90 leg keys" claims in
  the author report and integration note are correctly scoped to the r93
  subset. `UFO_SEAT` is inert for r93 (consumed only by the r90 family,
  35639), so the verifier recipe's env is harmless here.
- **Hygiene in the receipt:** `sinks_gone` all-true, `own_nodes_after: []`,
  `own_procs_after: []` for the sampled entries — matching author §2.3.

## 4. Residual risks and checks not run

- **No live family was run by this seat** (the verifier owns the single run
  per round). Every execution-shaped statement above is from the pinned
  source plus the pre-existing local receipt; nothing was re-measured.
- **Numeric reference values were not re-derived** (no new grader, law set
  or numerical pipeline — out of scope per the assignment). The boundary's
  1e-6 validation of the reference against installed libebur128 is taken as
  recorded evidence.
- **The author's two green batteries are not in this tree.** They exist in
  the author worktree (`/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r93/
  corpus/live/runs/20261016T101716935215Z-ebur-r93` and `…T103145603182Z-…`,
  plus the three earlier attempts) — verified by `ls`. In this worktree only
  the integration receipt exists, and it is **untracked and not gitignored**
  (`git ls-tree` at the pin: 0 files; `check-ignore` rc 1) — a local file,
  not committed at the pin and not claimed remote. The integration note's
  word "ignored" for `corpus/live/round-93/` is loose: the path is
  untracked, not ignore-matched.
- **The r88 foreign-scrub/errclass fallback semantics** (`_btwit_r88_scrub_foreign`,
  `_btwit_r88_errclass`) were trusted, not re-audited; the `notify_bogus`
  class label depends on them.
- **The pw-cli double-load race (L4) and the D-state hang edge in
  `_ebur_r93_reap`'s final unbounded `communicate()` (49244)** are inferred
  code paths; neither is observed in any local receipt.
- **Plugin-side mechanisms** (the block-phase quantisation of `Global`,
  the `max-window` source-vs-binary divergence, the `label=null` terse
  failure) remain the scout/boundary `[?]` items — not re-attacked here.
- **r98/r99/r100 regions were not audited** (other seats' rounds); the r99
  LAN opt-in was checked only for default-off scope, as noted.
- **The verifier's minimal-export path** (fixtures + artifacts only) was not
  exercised; stimuli regeneration is verified by source reading plus receipt
  sha agreement, not by an export run from this seat.

## 5. Artifacts and attribution

- **This report:** `reports/round-93/r93-reviewer.md` (the only repo file
  written by this seat).
- **Scratch:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-reviewer/`
  — `measure_audio.pin.py` (verbatim pinned source, sha256
  `801e153b…`), `receipt-inspect.txt` (read-only receipt inspection output).
- **Evidence read (all local, read-only, left intact):** pinned source via
  `git show bb177513…`; `reports/round-93/r93-scout.md`,
  `r93-boundary.md`, `r93-author.md`;
  `reports/round-100/r93-r99-r100-integration.md`;
  `corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`
  (untracked local receipt, not committed at the pin);
  author-worktree run listing under
  `/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r93/corpus/live/runs/`.
- **Attribution:** findings and line citations by the r93 reviewer seat
  (GLM-5.3-flash-max per the glmseat pin). Scout/boundary/author numbers are
  quoted from their reports and the local receipt; no measurement was
  re-run, no aggregate score invented, no round admitted, no canonical judge
  verdict claimed. This report is advisory; shipping and gate-admission
  authority remain with the lead.
