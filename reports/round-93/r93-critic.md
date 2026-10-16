# r93 critic — the `ebur128` family's acceptance logic, attacked

Seat: CRITIC (leaf, read-only). Round 93, role `critic`. Source pin
**`bb177513a615a32d3bc150ecbdcf78302e110d8c`** (the r99 safety commit; verified:
its only `measure_audio.py` hunk sits at line 52605 inside `rtp_e2e_r99_entry()`
and changes zero `ebur`/`ebur128` lines, so the r93 family bytes at this pin
equal the pre-pin bytes). Flag `ebur-r93`. No live family was run, no fixture
was executed or mutated, no routing/config/report-of-others was touched. LSP
was not available in this session: every finding below is literal source
inspection against the pinned blob (`git show PIN:corpus/fixtures/measure_audio.py`),
with line numbers from that blob.

Commands actually executed: `git cat-file/log/ls-tree/show/diff`, `sha256sum`,
read-only JSON audits of the frozen local receipts, a byte-region diff of the
author worktree's r93 family against the pin, `py_compile` of the pinned source
to `/tmp` (compile only — no fixture code executed), and `.pyc` header
inspection. Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-critic/audit-notes.md`.

---

## 1. Findings, by severity

### F1 (HIGH — fixable, observed live): arm failures land in the non-failing `coverage_blocked` bucket; `failures: {}` + rc 0 is reachable with zero measured legs

- **Where:** `_ebur_r93_run`, pin lines 49749–49752 —
  `if row.get("arm_failed") and not arm.get("expect_refusal"): entry.setdefault("coverage_blocked", []).append(...)`.
  Every entry predicate then skips arm-failed rows (`if row.get("arm_failed"): continue`
  at 49842, 49943, 50049, 50141, 50230, 50271, 50345, 50466), and the run exit
  code consults **only** `failures` (55968–55971:
  `failed = {k: v["failures"] ...}; return bool(failed)`).
- **Failure path:** any mid-run environment change (the author measured a
  ~3.4 h daemon wedge in this very window, r93-author.md §5.1) arm-fails every
  subsequent leg — "null sink never enumerated" / "filter-chain module
  refused" / "feed link never bound" — each into `coverage_blocked`. The
  battery then exits 0 with `failures: {}` and prints `{"failures": {}}`:
  green-on-blocked at run level. The only structural protection is the
  family-start daemon gate (55190–55209, correctly fail-closed), which by
  construction cannot see a wedge that starts after it passes.
- **Live instance (observed, frozen receipt):** the author's first full run
  `corpus/live/runs/20261016T100229270710Z-ebur-r93/measurements.json` (author
  worktree `audio-shokunin-wt-r93`): `ebur_channel_r93_probe` reads
  `failures: []` while **eight** legs carry `arm_failed="feed link never
  bound"` (`cls=ebur_r93_feed_refused`) in `coverage_blocked`;
  `ebur_peaks_r93_probe` reads `failures: []` with two more. That entry was
  green-by-receipt with all four stereo arms unmeasured; only the unrelated
  topology-expectation bug made the run loud at all.
- **Smallest correction:** in `_ebur_r93_run`, record unexpected arm failures
  in `failures` (or a distinct `arm_failures` list the exit code consults),
  leaving `coverage_blocked` for the two declared sub-arms only. One-line
  change; the disclosed blocks keep their classification.

### F2 (HIGH — fixable, source-proven): the fixed family lock silently no-ops on exactly the verifier's fresh-export path

- **Where:** `_ebur_r93_family_lock`, 49571–49587: `os.open(str(path),
  os.O_RDWR | os.O_CREAT)` on `ROOT/"live"/"measure_audio-ebur-r93.lock"`;
  `except OSError: return None`. The caller (55188) binds the return and never
  checks `None`; no receipt field records the lock at all.
- **Failure path:** `ROOT = Path(__file__).resolve().parents[1]` (line 27) is
  the corpus dir. The verifier recipe exports only `corpus/fixtures` +
  `corpus/artifacts` into a fresh tree, and the lock is acquired (55188)
  **before** anything creates `corpus/live/` (the stimuli writer's
  `mkdir(parents=True)` fires later, inside the first entry). So on every
  verifier run the open raises ENOENT, the family runs **unlocked**, silently,
  and the green receipt cannot show whether same-family exclusion held.
  Secondary: the lock is a blocking `flock(LOCK_EX)` with no timeout and no
  wait record — a hung holder (this window's 3.4 h wedge) blocks a second
  same-family run indefinitely with no output.
- **Smallest correction:** `path.parent.mkdir(parents=True, exist_ok=True)`
  before the open, record acquired/None in the receipt, and bound (or record)
  the wait.

### F3 (MEDIUM — fixable, latent; trigger class measured by the boundary): three predicates accept the silent-arm readout as the claimed semantic

- **Where:** `ch_silent_mom` (50075–50079) passes on any all-`-inf` series;
  `m_range_only`/`m_peak_only` (50157–50163) pass on the stale `0.0` plateau.
  A leg whose feed never delivered audio (the boundary's measured `pw-play`
  rc-1 empty-stderr class — 4/25 legs of quiet core r2, r93-boundary.md
  §0.2/§2.5) produces exactly those readouts. None of the three arms carries a
  tap, and none consults `row["play"]["exit_code"]` — which the harness
  **does record** (49424–49425) — nor any "audio flowed" witness.
- **Contrast:** the same entry enforces the post-tap witness on
  `m_window_only` (50151–50156) and `m_momentary_only` (50171–50175), so the
  pattern exists in the family; the three arms above simply do not use it.
- **Status:** latent — in both author greens and the final-byte integration
  run, every leg's `play.exit_code` is 0 or None, so the hole never fired.
- **Smallest correction:** require `row["play"]["exit_code"] == 0` (or a
  nonzero tap witness) in those three predicates before accepting the
  all-`-inf`/`0.0` series.

### F4 (MEDIUM — fixable): the C10 window-scaling law is one-sided; the small-window arm has no lower bound

- **Where:** 50294–50310 — the checks are `max(d040) > 0.8` (upper bound
  only), `min(d200) < 1.5`, and `min(d200) - max(d040) < 1.0`.
- **Failure path:** a host where the 0.4 s window decays in ~0.05 s passes
  all three checks (a ≥1.5 s two-second arm still satisfies Δ ≥ 1.0). The
  boundary's measured d040 is 0.418–0.426 s, so a lower bound (e.g. ≥ 0.2 s)
  is safe and makes the scaling law two-sided. §7.3 discloses the bands as
  wide but not the one-sidedness.

### F5 (MEDIUM — fixable mislabel): the `g_default` silent post tap is an unresolved arm defect recorded with a causal claim the scout's own evidence contradicts

- **Where:** all three final runs record `g_default: audio-domain ratio
  unmeasured (pre=0.20976177 post=0.0)` — pre tap live, post tap silent.
  r93-author.md §2.2 frames this as "the chain's output side produces no
  audio in this graph shape".
- **Counterexample (source-linked, from local evidence):** the scout measured
  the same node on the same host producing the gained signal at the output —
  r93-scout.md §2 (last bullet) and §3.9: `audio_ratio` 0.199–0.206 against a
  logged gain of 0.2086–0.2112. "Produces no audio" is therefore a property
  of this arm's graph/tap, not of the node; the block is an unresolved arm
  defect, not an inherent coverage loss.
- **Breadth:** the other three gain arms (`g_target0`, `g_clamp`,
  `g_silence`) use the same `outputs=["lin:Out"]` shape with **no taps**, so
  the audio-domain half of C12 is unattempted there too — the unmeasured
  surface is broader than the single disclosed block.
- **What still stands:** C12's *law* is carried by the same-leg residual
  (exactly 0.0 dB in the greens) and does not depend on this witness.
- **Smallest correction:** either replay the scout's verbatim gain cell (the
  proven arm) or relabel the block "arm defect, cause unresolved"; and either
  tap or explicitly mark the audio-domain half unattempted on the other three
  gain arms.

### F6 (LOW — fixable, provenance): the pinned tree carries a stale tracked `.pyc` — copied-but-unmeasured bytes

- **Where:** `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is
  tracked at the pin. Its header (flags=0, timestamp-based) declares a
  **533,517-byte** source; the pinned source is **2,766,373 bytes**; a fresh
  compile of the pinned source (3,065,559-byte .pyc) differs in the entire
  code body. The .pyc was last committed at **r78** (`a005e1e4`) and never
  regenerated through r79–r100.
- **Report mismatch:** r93-author.md §1 describes this path as "modified as a
  byproduct … left in place rather than reverted to a stale copy". That
  describes the author **worktree's** .pyc (verified: embedded size 1,716,584
  == the author source size; source sha256 `62e2606e…` matches §6) — the
  pinned copy *is* a stale copy.
- **Impact:** hygiene only — direct script runs ignore it, the verifier
  recipe's `PYTHONDONTWRITEBYTECODE=1` prevents refresh, and Python's
  mtime+size cache validation invalidates it for the one in-repo importer
  (`test_wpstate_r90_lock.py`). Smallest correction: drop it from the index or
  regenerate it, as a deliberate diff.

### F7 (LOW — calibration): the armed label matrix is 10 of 32 labels; the scout's `min`/`passthrough` fail classes are dropped without disclosure

- **Where:** 48770–48771 — `LOAD_LABELS=(debug,busy,sqrt,ramp,zeroramp)`,
  `FAIL_LABELS=(null,avg,sum,gain,nop)`. The scout's fail set (r93-scout.md
  §3.10) was `avg gain min nop passthrough sum`; the fixture drops `min` and
  `passthrough` and adds `null` (with its own distinct class). The author's
  C14 text ("5 load / 5 do not") is honest about the count, but read against
  the scout's 32-entry claim (scout claim 14) the matrix looks covered when
  two scout-failing labels are no longer armed. A one-line disclosure fixes
  the calibration; re-arming them is optional.

### F8 (LOW — robustness): six of nine entries have no `try/finally` around their arms loop, and the receipt is written once at the end

- **Where:** channel (50016–50108), modes (50113–50185), peaks (50190–50241),
  window (50246–50314), history (50319–50393), gain (50398–50571) have none;
  topology (49836–49911), cal (49934–49976), error (50584–50666) do. The
  receipt write is a single end-of-main step (55966–55967) with no
  try/except around the nine entry calls (55173–55228).
- **Failure path:** an exception inside those loops skips that entry's
  teardown census and propagates to main — the whole run's measurements,
  including entries already measured, are lost with no receipt. Per-leg
  cleanup (the leg's own `finally`, 49448–49461) still runs, so no host leak;
  the loss is evidentiary. Smallest correction: wrap each entry call (or add
  `try/finally` per entry) and write a partial receipt on exception.

### F9 (LOW — completeness): a fourth, undisclosed blocked attempt exists in the author worktree

- `corpus/live/runs/20261016T092620653912Z-ebur-r93/` (author worktree) is a
  gate-blocked run (0 legs, `failures=1`, class `ebur_r93_daemon_unavailable`)
  that r93-author.md §5.3 does not list (it lists 092003 and 092216 only).
  Loud and harmless — but the evidence list is incomplete. Also minor: the
  report states the `measure_audio.py` delta as +2056/−3 (§1) and +2035/−3
  (§6); one of the two is wrong.

### F10 (LOW — flakiness, fail-closed direction): the same-leg gain residual compares last-of-each-split values from different quanta

- 50479: `residual = 20·log10(gain[-1]) + lufs[-1]` — the last Global line
  and the last Gain line need not be the same sample. The boundary showed
  Global still decreasing through the tail, so drift between the two last
  lines can spuriously exceed the 0.01 dB band — a false red, never a false
  green. Pairing by nearest timestamp would fix it.

### F11 (LOW): teardown census and temp hygiene gaps

- `own_procs_after` greps only `pw-(play|record|cli)` (49695–49698); a leaked
  `pw-link`/`pactl`/`pw-dump` would not be censused (all are bounded and
  reaped, so exposure is small). The per-run tap directory
  (`tempfile.mkdtemp(prefix="r93a-tap-")`, 49568) and its tap WAVs are never
  deleted — tmp litter only.

---

## 2. What the evidence does support (verified, not attacked)

- **Counts:** nine entries / 90 leg keys verified statically (17+9+10+11+6+6+
  8+9+14) and in the final-byte receipt `corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`.
- **The disclosed coverage blocks are exactly the declared ones:** in both
  author greens and the integration run, `coverage_blocked` = `g_default`
  ratio ×2 (one per rep — the integration note's "occurs twice" is correct)
  + `notify_bogus` load-refusal ×1; `failures: []` in all nine entries. No
  green-on-blocked instance exists in the three final runs.
- **Provenance carries:** the r93 family region is byte-identical between the
  author worktree (`62e2606e…`, the bytes both greens ran) and the pin
  (91,178 vs 91,255 bytes; the only difference is the next family's banner
  line). The greens' evidence transfers to the pinned bytes.
- **Fail-closed structures that hold:** the family-start daemon gate (exercised
  live three times — 092003, 092216, 092620 — all loud, 0 legs, named in
  `failures`); teardown enforcement (surviving sinks/nodes/procs append to
  `failures`, 49680–49703); name-verified unloads that re-read the module
  index immediately before firing and never fire a captured id (21880–21903);
  no `set-default-*` anywhere in the r93 region; `expect_refusal` arms fail
  closed on a wrong class (50556–50567, 50652–50664); the deferred-activation
  witness is battery-level (50616–50633 — the author's fix #4 is in the
  pinned bytes); play rc is recorded per leg (the F3 witness exists, unused).
- **Determinism:** the 14 stimuli are analytic sines with no randomness
  (48829–48832, 49494–49517) — regeneration in the verifier's export is sound.
- **Cross-run identity:** the greens' calibration tables are byte-identical
  across both runs; window decays 0.427/1.856 s identical; peaks identical;
  history plateaus reproduce within the 0.05 dB band (rep ordering differs —
  the boundary's block-phase finding).

## 3. Blocked vs measured

- **Measured (frozen receipts):** everything in §2 above, plus the F1 live
  instance in the 10:02 run.
- **Blocked (disclosed by the authors, confirmed here):** the `g_default`
  audio-domain ratio (F5 — mislabeled cause, real block) and the `notify_bogus`
  silent variant (load-refused on the final bytes; the silent variant remains
  unobserved — author §7.5).
- **Not measurable by this seat:** the g_default arm-defect mechanism (why
  `lin:Out` is silent) — unresolved; I did not run the arm.

## 4. Residual risks and checks not run

- No live family, no fixture execution, no mutation of any receipt, source,
  or service; `RTP_R99_ALLOW_LAN_CONTROL` was never set. All execution claims
  are quoted from frozen local receipts.
- The `.pyc`-importer safety is reasoned from Python's cache-validation
  rules, not measured.
- The C16 ±1.0 LU envelope and the window bands are declared tolerances, not
  laws — the lead should read them as envelopes (author §6 says so; F4 adds
  the one-sidedness).
- Out of scope, not audited: the r99/r100 families, the SCORECARD/LOG (no r93
  row exists yet — verdict pending, consistent with M4), and the historical
  suite.

## 5. Artifacts and attribution

- This report: `reports/round-93/r93-critic.md` (this file).
- Scratch/evidence notes: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-critic/audit-notes.md`.
- Sources: pinned blob `bb177513…:corpus/fixtures/measure_audio.py`;
  frozen receipts under `corpus/live/runs/20261016T121901064467Z-ebur-r93/`
  (main repo) and `audio-shokunin-wt-r93/corpus/live/runs/20261016T{092003125628Z,092216336849Z,092620653912Z,100229270710Z,101716935215Z,103145603182Z}-ebur-r93/`
  (author worktree — local, uncommitted, not claimed committed or remote);
  r93-scout.md / r93-boundary.md / r93-author.md / round-100 integration note.
- Attribution: critic seat, GLM-5.3-flash-max (glmseat pin loaded from
  `/home/vgpnk/Projects/shokunin/.devin/skills/glmseat/SKILL.md`; no MCP
  server of that name exists in this session — the local skill file is the
  invocation path). Advisory only; no admission, verdict, or shipping claim.
