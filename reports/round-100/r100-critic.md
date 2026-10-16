# r100 critic — independent audit of the sofa/spatializer family

**Seat:** critic (leaf; no subagents, no live families, no source edits, no
shipping authority). **Round:** N=100. **Role:** critic. **Source pin:**
`bb177513a615a32d3bc150ecbdcf78302e110d8c` (tip = "r99 safety: require explicit
opt-in before physical LAN control"; parent `193acbed` = the r100 integration).
**Scope:** the pinned r100 family (`--probe-sofa-r100` in
`corpus/fixtures/measure_audio.py`, the rig `corpus/fixtures/r100sofa.py`), its
dispatch, its supporting instrument and its claimed laws, against the round's
scout/boundary/author/integration reports. **Advisory only:** nothing here
admits a round or claims a canonical judge verdict.

**Commands actually executed** (all read-only against the pin; no fixture was
mutated or executed): `git log/ls-tree/show/diff` at the pin; `sha256sum` over
`git show` blobs; literal reads and grep/sed over the dumped pin blobs; one
read of the integration receipt
`corpus/live/runs/20261016T121334985146Z-sofa-r100/measurements.json`; scratch
notes under `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-critic/`.
**LSP gap:** no LSP was used; every finding below is literal source inspection
plus grep over pinned bytes — grep hits are cited as line evidence, not as
semantic proof.

---

## 1. Findings (ordered by severity)

### F1 — The clock-invariance entry never arms that the variant was applied (missing-witness acceptance; fixable)

- **Where:** `measure_audio.py @bb177513:54084-54161` (`sofa_clock_r100_entry`).
- **Failure path:** the entry's only armed laws are the fine-ILD band
  (54130-54133, ±0.02 dB) and `n_samples` (54134-54136). The live witnesses
  that the variant is actually in force — `vrec["server_clock"]`,
  `vrec["settings"]` (the running graph's `pw-metadata -n settings` rows,
  54120-54123) and the drop-in text (54124-54129) — are **recorded, never
  gated**. If the sandbox drop-in `10-r100a.conf` fails to apply (malformed
  conf, a core that ignores `default.clock.quantum`), all three variants run at
  the same default clock, every ILD lands near 4.6084, both armed laws pass,
  and the entry greens while having measured **the same clock three times** —
  the "clock invariance" claim unmeasured. This is the entry whose own
  docstring says it is "what makes the whole family's private-core arming
  legitimate" (54085-54088), so the unguarded path sits exactly on the family's
  legitimacy load-bearing wall.
- **Evidence:** source lines above; the integration receipt shows the variants
  DID apply this round (`clock.quantum` 512 / 2048, `clock.rate` 96000 in
  `sofa_clock_r100_probe.variants[*].settings`) — so the observed greens are
  sound; the defect is that nothing would have caught non-application. The
  author report discloses the witness as recorded (§7.4) and the band thinness
  (§7.3/§9) but does not claim the application is armed — the gap is in the
  arming, not in the disclosure.
- **Smallest correction:** arm the existing witness, one line per variant, e.g.
  `_sofa_r100_eq(entry, leg, "server clock.quantum",
  vrec["settings"].get("clock.quantum"), "512")` (values are strings in the
  receipt) and `"clock.rate" == "96000"` for the r96000 variant. No new
  measurement, no new grader — the witness already exists in every row.
- **Observed or inferred:** inferred from source; the applied-state is observed
  in the receipt for this round only.

### F2 — Teardown law silently accepts an unverified module unload (missing-witness acceptance; fixable)

- **Where:** `measure_audio.py @bb177513:53347-53355`
  (`_sofa_r100_teardown_laws`) vs `r100sofa.py @bb177513:1020-1044`.
- **Failure path:** the fixture writes `row["module_unload_verified"]` only
  inside `if var is not None:` (r100sofa.py:1020-1042); when the `pw-cli`
  load output yields no `= @module:` var while the module **did** load and
  publish (output-format drift, log-window miss), the key is absent, no session
  unload is attempted, the FC nodes are destroyed by the sweep, the client's
  death removes the module, `post_sweep.clean` is True — and in the law helper
  `mod = row.get("module_unload_verified") or {}` makes the guard
  `if mod and not mod.get("matched")` **skip silently**. Every law passes; the
  "unload verified against its own nodes" claim (author §2, teardown row) is
  green while never verified. Mitigations that do not close it:
  `row["module_var"] = var` (r100sofa.py:926) is recorded but not gated;
  `_sofa_r100_shape_laws` only requires the nodes to publish (they did).
- **Evidence:** source lines above. Not observed in any receipt I could read —
  the integration receipt's azimuth legs all parsed `module_var=1` — so this is
  an unguarded path, not a live defect.
- **Smallest correction:** in `_sofa_r100_teardown_laws`, fail closed on the
  absent witness: `if not mod: _sofa_r100_fail(entry, f"{leg}: the module
  unload was never attempted (no module var parsed)")`. One line, r100-local.
- **Observed or inferred:** inferred from source.

### F3 — A fully-blocked battery reads green at the summary and rc level; the in-repo r93 gate precedent is not followed (fixable)

- **Where:** summary/rc `measure_audio.py @bb177513:55968-55970`; r100 block
  paths `53521-53524`, `53531-53534`, `54196-54204` (and every entry's
  `coverage_blocked`); the precedent `55200-55209` (r93 gate).
- **Failure path:** r100 environmental blocks go to `coverage_blocked` only;
  `failed = {k: v["failures"] ...}` and `return bool(failed)` make a run in
  which **all nine entries blocked with zero legs** exit **0** and print
  `{"failures": {}}` — a green-looking summary whose receipt says blocked. The
  same file's r93 gate states the convention explicitly: "a BLOCKED family must
  never read as a green battery: the gate names itself in failures so the run
  exits non-zero." The receipt is honest (each block is named in its entry), so
  this is summary-level green-on-blocked, not a hidden one — but it is exactly
  the class this seat is assigned to attack.
- **Evidence:** source lines above; this round's integration run had no blocks,
  so the path is unexercised in receipts.
- **Smallest correction (two options):** (a) smallest and additive across
  families: include `coverage_blocked` in the final summary JSON (one line at
  55969); (b) r100-only and stricter: an entry that arms zero legs also names
  itself in `failures`, per the r93 gate. The lead chooses; (a) changes no rc
  semantics, (b) makes the verifier's first blocked run exit non-zero.
- **Observed or inferred:** inferred from source.

### F4 — The family lock fails open and its absence is unrecorded (fixable)

- **Where:** `measure_audio.py @bb177513:52972-52986`
  (`_sofa_r100_family_lock` returns `None` on `OSError`) and `55275` (the
  return value is bound, never checked).
- **Failure path:** the lock path is `ROOT/live/measure_audio-sofa-r100.lock`
  with `ROOT = corpus` (line 27). The verifier's minimal tracked-source export
  contains only `corpus/fixtures` + `corpus/artifacts`, so on the **first** run
  in a fresh export `corpus/live` does not exist, `os.open` fails ENOENT, the
  lock is `None`, and the whole battery runs with **no same-family exclusion
  and no record** that the lock was not held (the receipt dir is only created
  later, at 55966). On the author's repo the lock works; the exported-tree
  first run is exactly the verifier's situation.
- **Evidence:** source lines + the verifier recipe's export list
  (review-roles.md). Inferred; not observed (no concurrent run exists here).
- **Smallest correction:** record the lock state in the receipt (e.g. a
  `family_lock_held` field in the summary/receipt), or fail closed per the r93
  gate convention. Record-only is the smallest safe change; the stricter
  option flips rc for an environmental prerequisite and is the lead's call.
- **Observed or inferred:** inferred from source.

### F5 — No entry-abort guard: one unexpected exception loses the whole battery's receipt (fixable; in-repo precedent exists)

- **Where:** dispatch `measure_audio.py @bb177513:55276-55293` (bare entry
  calls); receipt write `55963-55967` (once, at the end); the established
  guard pattern at `34513/34637/34898` and in the r99 e2e entry (~52648, the
  pin's own parent-adjacent block: `except Exception as exc:
  entry.setdefault("coverage_blocked", []).append(f"entry aborted: ...")`).
- **Failure path:** any uncaught exception inside an r100 entry propagates out
  of `main()` — traceback, exit ≠ 0, and **no `measurements.json` at all**, so
  the eight entries that completed are lost with the process. Secondary
  structural asymmetry: the clock entry's `_sofa_r100_teardown` sits inside the
  `try` (54154), not the `finally` (54155-54159), unlike the other eight
  entries — an exception in the variant loop skips the entry-level teardown
  census and the alsa-line law (the per-variant sandbox is still stopped by the
  inner finally at 54137-54138).
- **Evidence:** source lines above; the guard pattern exists in the same file
  for other families. Inferred; no exception occurred in the receipts I read.
- **Smallest correction:** wrap each r100 entry call in the dispatch with the
  same `except Exception` → named failure/block record used by r99 and r83-r85;
  move the clock entry's `_sofa_r100_teardown` into its `finally`.
- **Observed or inferred:** inferred from source.

### F6 — External termination leaks the private core and session manager (fixable hardening)

- **Where:** `measure_audio.py @bb177513:53047-53064` (sandbox `pipewire` /
  `wireplumber` spawned with `start_new_session=True`); cleanup only via
  `_sofa_r100_sandbox_stop` in entry flow; no `atexit`/signal handler exists in
  the file (grep: none).
- **Failure path:** the verifier's `timeout 1500` (or any external kill)
  terminates the family process; the sandbox sessions survive as orphans
  holding the sandbox socket; the exit census never runs. The leak is bounded
  (≤1 core+session-manager per interrupted entry), seat-owned, and — because
  the profile has no hardware monitors (52932-52949, alsa-line law 54150) —
  never touches an operator device. But the family's "0 private cores after"
  claim (author §5 exit census) holds only on clean exits.
- **Smallest correction:** a module-level registry of live sandbox process
  groups plus an `atexit` handler calling `_sofa_r100_sandbox_stop`.
- **Observed or inferred:** inferred from source; both receipted runs exited
  clean (exit census 0).

### F7 — Clock-law band margin is 12 % from the edge (declared tradeoff, not a defect)

The q512 leg's fine ILD 4.626 sits +0.0176 dB from the 4.6084 center inside a
±0.02 dB band — 88 % of the way to the edge (arithmetic on receipted values,
author §7.3/§9 and labrat H6 already say so). The band is borrowed from the
mismatch tolerance and the evidence base is three variants on one host. No code
change proposed; the lead should keep the band's provenance attached to any
adjudication citing the clock law, and F1's fix (arming the applied-variant
witness) is what makes this margin meaningful rather than vacuous.

### F8 — The "declared n_samples ladder" law is a tautology (calibration note)

`measure_audio.py @bb177513:53765-53766` compares `SOFA_R100_N_SAMPLES[rate]`
to `int(np.ceil(512 * rate / 44100))` — the table (52907) was constructed as
exactly those values, so this law cannot fail unless the table is hand-edited.
The real witness is the preceding law against the plugin-emitted
`row["n_samples"]` (53763-53764). Harmless; list it in the simplifier's
inventory of laws that add no evidence. No correction needed.

### F9 — Byte provenance: the pin's dispatch has never run the r100 family as a whole (disclosure, not a defect)

- sha256 chain for `corpus/fixtures/measure_audio.py`: author-worktree greens
  `e965f56c…bed7` (2 runs + negative control, author §5) → integration/final
  `5c8f7e9d…e9ab` (= blob at `193acbed`, receipted run
  `20261016T121334985146Z-sofa-r100`, rc 0) → **pin `bb177513` = `801e153b…e2f`**
  — never executed for r100. The pin's delta is exactly one hunk
  (`@@ -52605,34 +52605,42 @@`, the r99 `e_lan_control` opt-in) plus the new
  `corpus/fixtures/test_rtp_r99_lan_control.py`; the r100 block (52810-54300)
  and `r100sofa.py` (`26e96660…481`, matching the author's claimed sha) are
  byte-identical to the receipted bytes. So the r100 **law bytes** are
  unchanged, but any whole-file sha claim must cite `5c8f7e9d`, and the
  verifier's run will be the first r100 execution of the pin's whole-file
  bytes — which is precisely the verifier's job, provided the report cites the
  chain, not a single sha.
- The arming-live negative control (`negative-control.json`, "21 failures,
  ARMING LIVE") is **author-report-sourced only**: `corpus/live/r100-author/`
  does not exist in this worktree (it lives in the author's `wt-r100`
  worktree), and `git grep 'ARMING LIVE' bb177513 -- corpus/fixtures` finds no
  tracked harness — the proof that the arming is live is a frozen untracked
  receipt, not re-runnable from the pin.
- Citation precision: the integration note says "nine entries and 37 leg keys";
  the receipt's `measurements` holds **26 keys** — the 9 sofa entries plus 17
  canonical-battery entries that really ran (e.g. `ui.duration_s = 0.12`) plus
  `sections`/`distinctness`. The note is accurate about the family but a reader
  diffing "nine" against 26 keys needs the canonical-battery context stated.

### F10 — Ledger: no r100 row in LOG.md / SCORECARD.md at the pin (note, not a defect)

`grep r100 LOG.md SCORECARD.md` → empty; SCORECARD's last row is r86. This is
consistent with the integration note's "independent wave-B review and final
adjudication remain pending", but it means the claimed-laws surface for the
lead is the author report + code comments + receipts — not the SCORECARD — and
M4's closure must not imply a SCORECARD row exists. (Also observed, outside
r100: a stray `corpus/live/runs/measurements.json` of mode `probe-pwcat-r83`
sits directly under `runs/`; not this round's artifact, flagged for hygiene
only.)

---

## 2. What the evidence does support

- **The failure-accumulator fix is real and propagated end-to-end** — the
  r100-specific duty ("inspect propagation, not just helpers") traces clean:
  all nine entries bind `failures = entry.setdefault("failures", [])`
  (53515, 53588, 53685, 53740, 53798, 53896, 54006, 54091, 54173) and hand the
  **same object** to `_sofa_r100_teardown` (53574, 53671, 53725, 53782, 53880,
  53991, 54075, 54154, 54243); `_sofa_r100_fail` appends to that same list
  (53239-53240); `main()`'s rc reads `v["failures"]` from the same dicts
  (55968-55970). No entry replaces the list with a fresh object anywhere.
- **Leg-level fail-closed behavior:** `_sofa_r100_leg_ok` fails on no-JSON,
  `leg_error`, and timeout (53292-53305); `_sofa_r100_close` fails "unmeasured"
  on `None` rather than skipping (53263-53266); the fixture retries only
  `frames == 0`, never `rms == 0` (r100sofa.py:1149-1158), so the no-config
  cell's legitimate silence cannot be retried into a false pass, and `s_unfed`
  gates `rms == 0` **with frames > 0** (53561-53570).
- **Named-block discipline where it is implemented:** the shared entry names
  its block with the probe evidence (54196-54204), keeps silent attempts in the
  receipt next to the armed retry (54227-54235), and the teardown degrades to
  named blocks when `pw-dump` does not answer (53402-53407) or the store is
  unreadable (53457-53460).
- **The store-residue asymmetry is implemented as disclosed:** private-core
  rows → failure (53453-53456); shared rows → recorded r90/r95 class, never a
  failure (53444-53452); pid-scoped filter (53440).
- **Safety guards verified in the pinned bytes:** the r100 block contains no
  `pactl set-default-*` invocation (the only block hit is the comment at block
  line 6); the mutex splice carries `probe_sofa_r100` (54400); mode/suffix
  splices at 55944/55964; argparse row 54389; dispatch 55259-55293 — the only
  wiring, matching the author's "+1484/−3, three shared-line splices" claim in
  kind.
- **The r99 LAN-control default-off is present at the pin** and the r100 family
  neither reads nor sets `RTP_R99_ALLOW_LAN_CONTROL` (no interaction); the
  opt-in gate and its `measured: False, blocked: …` else-branch are in the pin
  diff.
- **Receipted greens are consistent with the armed laws** (integration
  receipt): azimuth fine ILDs 0.0 / 4.6084 ×2 / −4.6084 ×2 / 0.0; clock
  variants' settings witness 512 / 2048 / 96000; shared `pw-dump` 80 objects
  with 2 shared legs, both carrying `module_unload_verified`; 37 legs, 0
  failures, 0 blocks.

## 3. Blocked vs measured

- **Measured (receipted, on bytes other than the pin's whole file):** the
  integration run at `5c8f7e9d` (9 family entries / 37 legs, rc 0), the
  author's two green runs at `e965f56c`, the boundary's 146 legs, the scout's
  17 legs. The negative control's "21 failures / ARMING LIVE" is
  author-report-sourced; its JSON is not present in this worktree.
- **Blocked / not measurable by this seat:** any live execution (critic runs no
  families); the author-receipt copies (`corpus/live/r100-author/`) — absent
  from this worktree; the pin's whole-file bytes (`801e153b`) as an executed
  r100 family — that is the verifier's one run, not mine.

## 4. Residual risks and explicit checks not run

- No fixture, family, law, or grader was executed or mutated; no receipt was
  re-derived; no tar archive was copied.
- Not checked: the author/boundary raw receipts beyond the one integration
  measurements.json (they are absent from this worktree); the r99 block's
  full law set (the r99 reviewer's seat); the canonical battery's 17 entries'
  laws in the probe receipt (pre-existing battery, unchanged by r100); the
  tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` — a
  tracked build artifact whose header could in principle shadow stale bytecode
  if its recorded source mtime/size ever matched an export; the verifier
  recipe's `PYTHONDONTWRITEBYTECODE=1` prevents refresh, and I ran nothing, so
  I record the hazard without measuring it. Untracking that `.pyc` is a
  lead-authored hygiene fix.
- F1/F2's unguarded paths are inferred from source and unexercised in the
  receipts I could read; both fixes are one-liners that convert existing
  recorded witnesses into armed laws — they change no measurement and no band.

## 5. Artifact paths and attribution

- **This report:** `reports/round-100/r100-critic.md` (this file; the only
  repo file I write).
- **Scratch:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-critic/evidence.md`
  (sha chain, diff hunk map, receipt read-out, presence checks).
- **Evidence provenance:** pinned blobs read via `git show
  bb177513a615a32d3bc150ecbdcf78302e110d8c:<path>`; reports read from the
  worktree (`reports/round-100/r100-{author,boundary,scout}.md`,
  `r93-r99-r100-integration.md` — all tracked at the pin); integration receipt
  read from `corpus/live/runs/20261016T121334985146Z-sofa-r100/measurements.json`
  (local, untracked frozen input — not claimed committed or remote).
- **Attribution:** all findings are this seat's, derived from the pinned bytes
  and the named receipts; the author/boundary/scout reports are cited as
  claims and, where noted, as the source of numbers I could not re-read from
  receipts. No other seat's report was edited; no canonical judge verdict is
  claimed; the lead owns admission, fixes, and any re-run.
