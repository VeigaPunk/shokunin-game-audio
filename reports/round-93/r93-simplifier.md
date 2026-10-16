# r93 simplifier — dead-weight inventory of the `ebur-r93` family at the pin

**Seat:** SIMPLIFIER (leaf, wave-B final review). **Round:** 93. **Role flag:**
`ebur-r93`. **Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c`
("r99 safety: require explicit opt-in before physical LAN control",
2026-10-16 09:29:41 -0300). **Scope:** the r93 family inside
`corpus/fixtures/measure_audio.py` (lines 48677–50670, nine entries) plus its
`main()` wiring (55173–55228), read at the pin. Advisory only: no round is
admitted, no canonical verdict claimed, no live family run (that is the
verifier's alone), no source edit, no subagent.

**Method and its limit.** All analysis is static, on a scratch copy extracted
with `git show PIN:corpus/fixtures/measure_audio.py`
(sha256 `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`,
byte-identical to the pin by construction and re-verified). **No LSP device is
available in this environment** (the only MCP server here is `rea`, a Ghidra
native-binary provider — not a source LSP), so every "zero callers" below is a
**literal grep over the full 55,974-line pinned file** — reference absence at
the source level, never semantic proof. Each candidate symbol was also checked
to have exactly one definition site. Nothing was executed against the family;
no before/after experiment was run (role-forbidden).

**Commands actually executed:** `git rev-parse/log/ls-tree/show/cat-file/status`
on the audio repo; `sha256sum`; `grep`/`awk` over the scratch copy; `python3`
JSON reads of the frozen integration receipt
`corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`
(read-only; not re-derived). Scratch:
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-simplifier/`
(`measure_audio.py`, `evidence-greps.txt`). The shared tree's only tracked
modification is the pre-existing sibling `LOG.md`; I wrote nothing there.

---

## 1. Findings (severity-ordered)

Labels: `[O]` observed (receipt or pinned bytes read directly), `[I]` inferred
from pinned source/receipt. Line numbers resolve against the pin.

### F1 — `_ebur_r93_plateau_in` is never called (proven reference absence, grep) `[O]`

- `measure_audio.py:49028-49030`. Single definition, **zero call sites in the
  whole file**. Its twin `_ebur_r93_plateau_is` (49020) has 8 call sites; the
  band form was never adopted — every band check is inline
  (`ebur_window_r93_entry` 50294-50310, `ebur_history_r93_entry` 50358-50389).
- **Smallest correction:** delete the 3-line function. Behavior at the pin:
  never executed, so no measured claim can move.
- **Tradeoff (extension-point withdrawal):** it is the natural shape for a
  future band assertion; deleting it re-costs ~3 lines to re-add. Classified
  as a tradeoff, not a defect.

### F2 — `_ebur_r93_unlink` is never called (proven reference absence, grep) `[O]`

- `measure_audio.py:49082-49084`. Single definition, **zero call sites**. The
  family never tears a link down: teardown relies on module/sink unload
  (links die with their nodes — confirmed by the receipts' empty
  `own_nodes_after`/`own_procs_after`).
- **Smallest correction:** delete the 3-line function.
- **Tradeoff:** an explicit unlink is the tool for a future mid-leg re-link
  leg (the r99 family measures relinking; r93 has no such arm). Same
  classification as F1.

### F3 — dead local `same_leg_nodes` in `ebur_gain_r93_entry` `[O]`

- `measure_audio.py:50407-50411`. Assigned once, **never read** (single
  occurrence in the file). All four `g_*` arms build their node lists inline
  (50419-50424, 50428-50434, 50439-50444, 50449-50453); the sibling
  `same_leg_links` (50412) **is** consumed by all four arms — so the dead
  local is a half-finished refactor, not a shared-structure intent.
- **Smallest correction:** delete the 5-line assignment. The four arms are
  already self-contained; nothing else changes.

### F4 — write-only store `ctx["unloads"]` `[O]`

- Initialized `measure_audio.py:49567`, written `49459-49461` (leg finally),
  **never read** (`grep 'ctx["unloads"]'` over the whole file: one hit). The
  recorded evidence is the *entry-level* `entry["unloads"]`
  (teardown 49658, block 49712) — which the author's hygiene section cites
  (`unloads[*].exit_code == 0`).
- **Smallest correction:** drop the `"unloads": {}` init and turn 49459 into a
  bare `_pactlmon_r85_unload_own(...)` call. **The call itself must stay** —
  it is the working per-leg sink unload; only its return value is discarded
  today, so no evidence is lost.

### F5 — `_ebur_r93_args` parameter `ns` is dead in the body `[O]`

- `measure_audio.py:49050-49062`. The body references `fc_in` and `fc_out`
  but never `ns`; the sole caller (49340) passes only
  nodes/links/inputs/outputs/ch/position. `ns` is a vestige of an earlier
  descriptor shape.
- **Smallest correction:** remove the parameter. Pure signature cleanup; the
  emitted descriptor string is unchanged.

### F6 — `_ebur_r93_play` parameter `wall` is dead in the body (misleading signature) `[O]`

- `measure_audio.py:49210-49225`. `target` is used (49220); `wall` is never
  referenced — the bound actually applied is the caller's
  `_ebur_r93_reap(play, 3.0)` (49425). The signature advertises a wall bound
  the function does not implement.
- **Smallest correction:** remove `wall` (keep `target`, which is used and
  default-only). Optional: rename nothing else.

### F7 — duplicate descriptor grammar: `raw_args` re-spells `_ebur_r93_args` `[O]`

- `measure_audio.py:50537-50550` (`ebur_gain_r93_entry`, the C13 unquoted-key
  leg) hand-builds the full filter-chain descriptor — node.description,
  `filter.graph={nodes=…,links=…,inputs=…,outputs=…}`, `audio.channels`,
  `audio.position`, `capture.props`, `playback.props` — the exact template
  `_ebur_r93_args` owns (49050-49062). The embedded node/link literals are
  byte-reconstructable from the existing helpers: `_ebur_r93_ebu()` ≡
  `{type=ebur128,name=e,label=ebur128}`;
  `_ebur_r93_ebu(name="l2g", label="lufs2gain", ctl="Target LUFS=-100")`
  emits the **raw unquoted** `control={Target LUFS=-100}` verbatim (the ctl
  is inserted unmodified, 49784-49785), which is precisely what C13 tests;
  `_ebur_r93_link_spec` emits the two link literals.
- **Failure path this enables:** two spellings of the same grammar can drift —
  a future change to `_ebur_r93_args` (e.g. the descriptor prefix or props)
  leaves `raw_args` behind, and the C13 leg would then test a descriptor no
  other leg produces.
- **Smallest correction:** rebuild `raw_args` via
  `_ebur_r93_args(nodes=[…helpers…], links=[…], inputs=["e:In DUAL MONO"],
  outputs=["e:Out DUAL MONO"])`. Byte-identical at the pin `[I]` (compared
  token by token against 49053-49062); no behavior change.

### F8 — `two["nodes"]` re-declares `_ebur_r93_meter`'s default byte-for-byte `[O]`

- `measure_audio.py:50024-50025` (`ebur_channel_r93_entry`) vs the meter
  default at 49767-49769 — identical strings. The `two` dict needs only
  inputs/outputs/ch; omitting `"nodes"` selects the identical default.
- **Smallest correction:** drop the `"nodes"` key from `two`. Cosmetic; listed
  because it is a second authority for the same bytes.

### F9 — label legs arm a full stimulus rig and collect an unchecked series (dead observation) `[O]` (mechanism `[I]`)

- `_ebur_r93_meter` defaults `stim_key="tone_1k_050"` (49757); the five
  load-label call sites (50634-50644) do not override it, so each
  `e_label_*` leg loads the null sink, binds the feed link, **plays the full
  3.5 s tone**, and reaps it at a 3.0 s wall (49425) — then the C14 check
  consumes only `arm_failed`/`error_class`. Observed in the frozen
  integration receipt: `e_label_debug_r0` carries `play {exit_code: 0}` and a
  36-value series of `control: 0.000000` (plateau 0.0, `n_finite` 36) that no
  assertion reads; `e_label_busy_r0` has an empty series; the fail-label legs
  return before play. `[I]` the 0.0 series is the debug label logging its
  **unlinked** Control input per quantum (`links=[]`), consistent with
  r93-scout §2.
- Cost: ~2 s surplus per load-label leg (the reap waits out the tone),
  ~10 s per battery — small, but it is work and receipt volume no claim uses.
- Hazard worth naming: the `e_label_debug` leg feeds audio into the debug
  node's **audio In** — the exact shape r93-scout §2 warns against ("Do not
  connect the debug node's audio In"). No corruption is observed (the readout
  parse is regex-scoped; the receipt is green and clean), but the shape is
  the warned one.
- **Smallest correction:** `stim_key=None` at the two label call sites
  (50635-50640, 50646-50651). **Tradeoff:** the receipt loses `row["play"]`
  and the (unchecked) series for label legs — a schema change, disclosed
  here, not a silent deletion. The played tone is not part of any claim.

### F10 — tracked `.pyc` caches are stale duplicate authority (repo-level) `[O]`

- `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` at the pin: its
  16-byte header records source size **533,005 B** (mtime field
  `0x6AD06A54` ≈ 2026-10-15, last commit `a005e1e4`, r78 era) while the
  pinned `measure_audio.py` is **2,766,373 B** — stale by ~2.23 MB of source.
  Same class: `build_artifacts.cpython-314.pyc` records 60,272 B vs the
  pinned `.py`'s 60,240 B. The `.gitignore` at the pin has no `__pycache__`
  rule, so tracking is deliberate (r93-author §1 discloses the cache as a
  committed byproduct).
- Impact: inert at runtime (CPython validates size/mtime and recompiles), but
  it is tracked dead weight and the source of the perpetual "tracked-dirty"
  churn the scout documented.
- **Smallest correction:** untrack the `__pycache__/*.pyc` files and add the
  ignore rule. **Tradeoff:** this reverses a disclosed repo convention and is
  outside this lane's write scope — proposed, not performed.

### F11 — defensive dead branches (inventory; deletion optional) `[O]`

- `_ebur_r93_stats` (48985-48993): the `isinstance(v, str)` conjuncts in
  `n_nan`/`n_inf` can never fire — the sole caller (49428) feeds
  `_ebur_r93_series` output, which appends floats only (48954-48976).
  Tradeoff: the family's JSON-safe series (`row["series"]`, strings for
  non-finite) is the representation a future stats caller would pass, so the
  branches are future-proofing.
- `_ebur_r93_num` (48790-48793): the `None`/`str` passthrough and the
  `str(value)[:80]` branch have no caller at the pin (every call site passes
  a float). Same defensive class.
- `_ebur_r93_leg`'s fallback defaults (49329-49336: `dur`, `read_extra`,
  `ch`, `kind`, `readout`, `note`) are an unreachable second default layer:
  its only caller is `_ebur_r93_run` (49746) whose spec is always a
  `_ebur_r93_meter(...)` dict, and the meter always sets every one of those
  keys (49762-49773). Harmless (both layers reference the same constants, so
  no drift), but the second layer is provably dead.
- Default-only parameters never overridden at any call site (extension
  knobs, not dead code — inventory only): `_ebur_r93_sine(phase)`,
  `_ebur_r93_ref_global(rate/block_s/overlap/weight)`,
  `_ebur_r93_decay(drop_db)`, `_ebur_r93_tail(n)`, `_ebur_r93_delta(nd)`,
  `_ebur_r93_cli_open(debug)`, `_ebur_r93_cli_close(bound_s)`,
  `_ebur_r93_load_module(tries)`, `_ebur_r93_play(target)`.

### F12 — latent gap: `n_inf` never counts a positive `inf` `[O]` (gap), reachability `[I]`

- `_ebur_r93_stats` (48988-48990) counts only `-inf`; a positive `inf`
  readout — which `EBUR_R93_CTRL_RE` accepts (48752) — would be counted
  nowhere (not nan, not `-inf`, not finite). Never observed on this surface
  (the three literals are `-nan`/`-inf`/finite), so latent. One-line fix if
  ever armed; not a deletion.

### F13 — teardown asymmetry across entries (observation, not a deletion) `[O]`

- Entries 1, 2 and 9 wrap their bodies in `try/finally` with
  `_ebur_r93_teardown` (49910-49911, 49975-49976, 50665-50666); entries 3-8
  call teardown after their loops (50107, 50184, 50240, 50313, 50392, 50570).
  An exception between legs in entries 3-8 skips the entry-level teardown
  censuses. Exposure is bounded: `_ebur_r93_leg`'s own `finally`
  (49448-49461) still kills the process groups, closes the session and
  unloads the sink, so no node leaks — what is lost is the census evidence,
  and only on an in-process exception (a SIGTERM kill skips `finally`
  everywhere regardless).

### F14 — minor residue and recorded-only evidence (observations) `[O]`

- `_ebur_r93_ctx` creates `tempfile.mkdtemp(prefix="r93a-tap-")` (49568);
  nothing removes it — tap WAVs and the directory survive in TMPDIR
  (untracked, outside the repo). A one-line cleanup in teardown would close
  it; out of this lane's write scope.
- `row["play"]` (49416, 49425) is recorded but no entry assertion reads it;
  the boundary's silent-arm hazard is covered indirectly (a silent arm fails
  the plateau checks). This matches the boundary's own recommendation
  ("record `play.rc`, never read it as a semantic") — kept as-is.
- Already-disclosed duplicate observations, no action: the `g_default`
  coverage-blocked message appears twice (reps=2, one arm — the integration
  note says exactly this); the load text is recorded at three granularities
  (`attempts[].lines`, `warn_lines`, `load_text`) — per-attempt provenance,
  deliberate.

---

## 2. What the evidence supports

- **The family is otherwise tight.** It duplicates nothing it could reuse:
  all fifteen shared helpers it calls (`_capture_inventory`,
  `_playback_r78_*`, `_loopback_r79_oracle`, `_capture_r77_sink_names_strict`,
  `_pwcat_r83_ns_load`, `_alsapw_r84_*`, `_pactlmon_r85_*`, `_btwit_r88_*`)
  are defined earlier in the same file and delegated to, not re-implemented.
  The BS.1770 reference exists **exactly once** in the 55,974-line file
  (`1681.974450955533` and the `-0.691` constant appear only at
  48870/48924/48939/48947) — no cross-family duplicate authority.
- **The wiring is live and single-path:** argparse row (54387), mutex token
  in the multi-probe guard (54400), dispatch (55173), fixed family lock
  (55188), daemon gate with a named block path that names itself in
  `failures` (55190-55209), nine entries (55211-55228). No dead mode select,
  no orphaned mutex row.
- **The measured claims are untouched by every proposed deletion:** F1-F6
  remove code that is never executed; F7-F8 rebuild byte-identical strings;
  F9-F10 change receipt shape/convention and are flagged as such. The
  nine-entry / 90-leg shape, the C1-C16 law set, the lock/gate guards and the
  receipt schema (modulo F9's flagged option) are preserved.
- **Blocked vs measured, at the receipt:** the frozen integration receipt
  confirms nine entries and 17+9+10+11+6+6+8+9+14 = **90 legs**, no entry
  failures, with exactly the two disclosed coverage blocks (`notify_bogus`
  load refusal; `g_default` audio-domain ratio unmeasured, twice — one arm,
  two reps). My findings add no new quantitative claim and none of them
  touches a measured value.

## 3. Residual risks and explicit checks not run

- **No live execution.** I did not run the family or any probe (verifier
  only); every deletion is behavior-preserving by source construction
  (never executed / byte-identical), but the preserved-contract claim rests
  on reading, not on a re-run. The verifier's single run is the behavioral
  check.
- **Grep is not semantic proof.** With no LSP device available, "zero
  callers" is literal-text absence over one file. A dynamic reference
  (getattr, exec, a name built by concatenation) would evade it; I checked
  the r93 region for such patterns and found none, but that check is itself
  literal.
- **Line numbers are pin-relative.** They resolve against
  `bb177513a615a32d3bc150ecbdcf78302e110d8c` (verified byte-identical scratch
  copy); they will drift on any later edit.
- **The author's r93-stage sha256 (`62e2606e…`) is not the pin's** — later
  rounds appended the r99/r100 families to the same file, so the pin's
  `measure_audio.py` is `801e153b…`. Anyone diffing against the author report
  must diff family slices, not whole files.
- **F9's correction changes the receipt schema** (label legs lose
  `row["play"]`/series). If the lead values byte-stable receipt shapes across
  rounds, keep the stimulus and accept the ~10 s/battery cost instead.
- **F10's correction reverses a disclosed repo convention** (tracked fixture
  caches); it needs a lead-authored convention change, not a drive-by
  untrack.

## 4. Artifact paths and attribution

- **Report (this file):** `reports/round-93/r93-simplifier.md` — the only
  repo file I wrote.
- **Scratch:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-simplifier/`
  — `measure_audio.py` (pin-extracted, sha256
  `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`) and
  `evidence-greps.txt` (the literal grep proofs quoted above).
- **Evidence read, not produced:** pinned source via `git show`;
  `corpus/live/runs/20261016T121901064467Z-ebur-r93/measurements.json`
  (orchestrator's integration run, frozen input);
  `reports/round-93/r93-{scout,boundary,author}.md`;
  `reports/round-100/r93-r99-r100-integration.md`; wave assignment files
  (lead-authored). All local receipts remain local; nothing here implies
  they are committed or remotely available.
- **Attribution:** scout/boundary/author claims are quoted from their
  reports; the receipt numbers are the orchestrator's integration run; the
  dead-weight inventory and every deletion proposal are this seat's, static
  at the pin, advisory, and unexecuted.

**Stop condition:** the next deletion candidates are the default-only
extension parameters (F11's inventory) and the defensive branches — removing
them trades real future-proofing and extension surface for a few tokens each.
That harm outweighs the weight saved; I stop here.
