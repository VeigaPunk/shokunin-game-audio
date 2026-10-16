# r100 simplifier — dead-symbol and propagation inventory of the sofa family

**Seat:** simplifier (leaf; no subagents, no live families, no source edits).
**Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c` (verified: commit
"r99 safety: require explicit opt-in before physical LAN control", parent
`193acbed` "r100 integrate"). **Scope:** the r100 sofa family only — the block
`corpus/fixtures/measure_audio.py` lines 52809–54250 plus its four wiring
splices (54389, 54400, 55259–55293, 55944, 55964), and
`corpus/fixtures/r100sofa.py` (1175 lines). All line numbers below resolve
against the pin; extracted copies live in
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-simplifier/pin/`.

**LSP disclosure:** no language server is available in this session (no `lsp`
device among this seat's tools). Every "unreferenced" claim below is a literal
inspection of the complete pinned files, NOT semantic proof. The sofa block is
a closed region: every `SOFA_R100_*`, `_sofa_r100_*` and `sofa_*_r100_entry`
reference in `measure_audio.py` lies inside 52809–55293 plus the wiring lines;
the only pre-block `sofa` hits are the r92 family's own load-only legs
(40938–40944, an unrelated family). `r100sofa.py` was read in full.

**Commands actually executed:** `git cat-file -t` / `git log` / `git show
--stat` / `git diff 193acbed bb177513` on the audio repo; `git show
PIN:<path>` extractions to scratch; `wc`, `sha256sum`, `grep`, and read-only
`python3 -c` JSON walks over the surviving r100 receipt. No fixture, family,
service or PipeWire object was run, signalled or mutated.

## 0. Provenance facts established first

1. The pin's own diff (`193acbed`→`bb177513`) touches only the r99 RTP section
   and adds `test_rtp_r99_lan_control.py`; **zero** diff lines contain `sofa`.
   The r100 sofa block is byte-identical across both commits.
2. `r100sofa.py` at the pin hashes `26e966601abf5d1d784842b192fa3e2d7e299538b832702f7124c90a3f227481`
   — exactly the sha the author report §5 claims.
3. Pinned `measure_audio.py` hashes `801e153b…`, which differs from the
   integration note's "r100 final" `5c8f7e9d…` solely because the r99 safety
   commit post-dates the green runs — the sofa bytes themselves are unchanged
   (point 1). The review pin therefore follows the LAN repair as required.
4. The author's own run receipts (`20261016T103052642013Z-sofa-r100`,
   `20261016T103758962243Z-sofa-r100`) and `corpus/live/r100-author/` are
   **absent from the tree now**. The surviving r100 evidence is the integration
   run `corpus/live/runs/20261016T121334985146Z-sofa-r100/measurements.json`
   (890,270 bytes; 9 sofa entries, 37 legs, `failures: {}`, no coverage
   blocks). This report cites only that surviving receipt and never implies
   the deleted author receipts are still available.

## 1. Findings, by severity

### F1 (highest — calibration + dead code): the no-config −22 law is not armed, but the author report's verdict table says it was measured

- **Where:** `measure_audio.py` 52920–52922 (constants), 53219 (plumbing flag),
  all nine entry bodies (53509–54249); author report §3 row 2 (line 120).
- **Failure path:** the three constants `SOFA_R100_NOCONFIG_ERR`
  ("no config was given"), `SOFA_R100_NOCONFIG_GRAPH_ERR` ("can't start
  graph") and `SOFA_R100_NOCONFIG_CODE` ("(-22)") are defined and referenced
  **nowhere else in the file**. The rig fully supports the class
  (`r100sofa.py` 719–720 `node_tok(no_config=True)`, 897, 1090, 1116–1118
  `--no-config`), and the family plumbing forwards it (`_sofa_r100_leg_args`
  53217–53221), but **no entry ever passes `no_config=True`** — the flag is
  reachable only by hand. The boundary's CONF row 2 (load OK → activation −22
  → silence) therefore has no armed leg in the pinned family.
- **Evidence (surviving receipt):** across all 37 legs of
  `20261016T121334985146Z-sofa-r100`: `"no_config"` occurrences **0**;
  `no config was given` **0**; `can't start graph` **0**; `"n_samples": null`
  **0**. The author report §3 row 2's "measured" values also match no leg:
  `frames 177152` occurs in the receipt only on `x_az0`,
  `x_az90/ref_analysis` and `shared_az0` (all non-silent, fully configured
  legs), and the `rms [0.0, 0.0] with frames > 0` signature matches `s_unfed`
  at **117760** frames — a different mechanism (configured-but-unfed, graph
  starts fine) from the no-config −22 activation refusal.
- **Smallest correction (lead's move, not mine):** either arm one
  `no_config=True` leg in `sofa_shape_r100_entry` (the plumbing already
  exists), or delete the three dead constants plus the `no_config` plumbing
  pair and correct author-report §3 row 2 to say the class is recorded, not
  armed. I made neither change: reports other than mine and source edits are
  out of my scope.
- **Observed or inferred:** the dead constants and absent leg are observed
  (literal reads); that the report row is wrong is inferred from the surviving
  receipt — the author's own deleted receipts could not be checked.

### F2 — dead family-side symbols (proven reference absence by literal inspection)

| item | location | proof |
| --- | --- | --- |
| `SOFA_R100_RECIPES` | measure_audio.py 52865 | defined; zero other references |
| `SOFA_R100_TONE_HZ` | 52856 | defined; zero other references (the 440 Hz default lives in the rig at 883/957/1006/1010/1127) |
| `SOFA_R100_RATE_STRING` | 52919 | defined; zero other references (the rig checks the string itself, `r100sofa.py` 866) |
| `SOFA_R100_COARSE_ILD` keys `0, 90, 180, 270` | 52903–52904 | the only read site is 53711, indexed by `az ∈ {45,135,225,315}` from the curve plan (53700) |
| `_sofa_r100_teardown(..., loads=None, ...)` | 53383 | `loads` is never referenced in the body (53396–53460); 8 of 9 callers pass a literal `{}` (53671, 53725, 53782, 53880, 53991, 54075, 54154, 54243), one passes nothing (53574) |
| `_sofa_r100_env(..., wp)` | 52997 | single caller 53041 passes `wp=True` always; the `if wp:` branch (53014–53017) is unconditional in practice |
| identity dict comprehension | 53085 | `rec["procs"] = {k: v for k, v in rec["procs"].items()}` maps every key to itself — a no-op copy |
| dead leg kwargs `tone_secs`, `argv_order`, `ctl_order`, `debug`, `no_config` | 53208–53210, 53219 | no entry passes any of them (checked every `_sofa_r100_leg(...)` call site, 53538–54218) |
| `Bounded.as_dict` | r100sofa.py 144–148 | defined; zero call sites in the file |
| `Bg.pid` property | r100sofa.py 171–173 | never read — `Bg.stop` uses `proc.pid` directly (182, 189) |

Each deletion is behavior-preserving by inspection (removing an unreferenced
binding or an always-constant parameter). Per my role I ran **no** before/after
experiment, so none of these is behaviorally proven — the reference absence is
proven, the behavioral equivalence is argued from the source alone.

### F3 — rig-side extension points the family never drives (tradeoff class, not proven dead)

`r100sofa.py` is a hand-runnable CLI (its own docstring, lines 4–12), so an
unused flag is an extension point, not a provable dead branch:

- `--no-config` (719–720, 1116–1118) — the F1 class; currently family-orphaned.
- `--argv-order` with `args_token`'s `reversed`/`graph_last` branches
  (742–761, 899–900, 1132) — the boundary measured token order inert; the
  author dropped the order entry and kept the machinery.
- `--ctl-order` with `node_tok`'s `control_first` reversal (717, 737–738,
  896, 1133) — same decision residue.
- `--debug` (1135–1136, 1143) — default 3 is what every family leg uses.
- `--tone-secs` / `--tone-amp` (884–885, 1092, 1128–1129) — defaults always
  used; `tone_amp` has no family plumbing at all.
- `unlink()` + `_post_action`'s `relink_out` branch (841–843, 1076–1080) —
  the boundary's relink-timing axis; the only `post` action any entry issues
  is `set_azimuth` (53832–53833).
- `write_wav`'s `ch > 1` branch (567–571) — every caller passes `ch=1` (963).
- `env` parameters of `ports_of`/`link`/`run` (764, 827, 151) — never passed
  non-None; the private-core env flows through the `PW_ENV` global instead.

Withdrawing any of these is an **extension-point withdrawal and must be
classified as a tradeoff**: each encodes a boundary-measured axis (order
inertness, relink timing, no-config refusal) that a later round may re-arm at
zero rig cost. My recommendation is to keep F3 and delete only F2.

### F4 — duplicate observations (kept deliberately; recorded, not armed)

- `entry["failures"] = failures` re-assignments in every entry
  (e.g. 53523, 53533, 53579, 53597, 53676, …): after the §6.2 fix the local
  name IS the entry's list (same object via `setdefault` at entry top), so
  every rebind is a same-object no-op. This is the author's post-incident
  belt-and-braces (author report §6.2) — deleting it removes a regression
  guard against a future helper rebinding the list. **Tradeoff; keep.**
- `entry["blocked"]` (set by `_sofa_r100_block`, 53244) duplicates the first
  `coverage_blocked` element — the house convention of every prior family
  (same pattern at 6675, 7021, 7381, …). Inherited, not r100-specific. Keep.
- `peak` is recipe-independent (max over the whole channel) yet computed once
  per recipe per channel (`r100sofa.py` 654) and re-selected at 693 — a
  threefold duplicate of one number. Cheap; cosmetic only.
- `tone_ratio_db` (690–692) is computed for every stereo recipe and read by
  **no law** in `measure_audio.py` (grep: zero consumers) — recorded-only,
  like `play_link_origin` (975), `links_after` (1013), `ports_rec/ref/play`
  (936/943/971) and the `calls` ledger (1062–1064). This is the family's
  stated recorded/armed split working as designed; not deletions.
- The `SOFA_R100_LAW_PROVENANCE` dict is embedded in all nine entry heads
  (53488–53495) — nine receipt copies of one block. Per-entry
  self-containment convention. Keep.
- Fixture-path authority is duplicated across the two files
  (`SOFA_R100_SOFA`/`SOFA_R100_DEFAULT_SOFA` at 52853–52854 vs `SOFA`/
  `DEFAULT_SOFA` at `r100sofa.py` 53–54), as are the 440 Hz default and the
  rate string. The rig's self-containment is documented as deliberate
  (`r100sofa.py` 14–20); a path change must edit both files. Tradeoff noted,
  not a deletion candidate.
- Three `/proc` own-process censuses exist (`_sofa_r100_own_procs`
  53358–53380; the shared entry's inline foreign census 54177–54192; the
  rig's `_own_procs` 311–332). The first two could share a helper; the rig's
  is required by its self-containment. Minor.

### F5 — propagation audit (the r100-specific duty: helper → entry → main)

Verified live, by reading the pinned bytes:

1. `_sofa_r100_fail` (53239) appends to `entry.setdefault("failures", [])` —
   the same object each entry binds as `failures` at its top (the §6.2 fix).
   `_sofa_r100_teardown` (53383) appends into the caller's list. No
   accumulator clobber survives anywhere in the nine entries.
2. Dispatch (55276–55293) stores all nine entries in `measurements`; `main`'s
   summary (55968) builds `failed` from `v["failures"]` for **every** entry —
   each r100 entry always carries the key (set at entry top), so the summary
   cannot KeyError on this family. Exit code is `bool(failed)` (55970).
3. `coverage_blocked` rides in the receipt data only and does **not** affect
   the exit code — a named block is not a failure, consistent with the
   family contract ("named coverage block, never a silent green").

Two propagation defects found (both observed by reading; neither executed):

- **F5a (low):** `sofa_clock_r100_entry` is the only entry whose final
  `_sofa_r100_teardown` sits in the `try` (54154) rather than the `finally`
  (54155–54159, which only `rmtree`s). An exception escaping the variant loop
  skips the residue census entirely. Per-variant sandbox stops do run (inner
  `finally` 54137–54139), so the exposure is the census, not the processes.
  Smallest correction: move 54154 into the `finally`.
- **F5b (low):** the no-hardware witness's `alsa_lines` counter (54142–54148)
  sets `-1` **by assignment** when one WP log is unreadable, then a later
  readable log **adds** to it — a mixed state yields a wrong count and
  swallows the unreadable condition; all-unreadable yields the misleading
  failure text "mentions alsa -1 times". The witness can report a wrong
  number instead of a named block. Smallest correction: count unreadable logs
  separately and block on them.
- Note (not a defect): entries are invoked without try/except in `main`
  (55276–55293), and each entry's `tempfile.mkdtemp` sits outside its `try`
  (53525, 53589, 53686, 53741, 53799, 53897, 54007, 54098) — an `OSError`
  there aborts the whole family run before any receipt is written. That is a
  loud failure, not a silent green; the family lock is released by process
  exit. Recorded as a residual risk, not a deletion candidate.

## 2. What the evidence supports

- The r100 family's failure propagation is sound on the pinned bytes: the
  §6-incident class (helper appends to a list the entry then overwrites) is
  gone; every law failure reaches `entry["failures"]` and the run summary.
- The family is self-contained: no sofa symbol is referenced outside the
  block + wiring; the only cross-family couplings are the documented
  inherited helpers (`_playback_r78_node_names`, `_jack_r95_graph`,
  `_jack_r95_errclass`, `_jack_r95_norm`, `_playback_r78_foreign_clients`,
  `_alsapw_r84_loadavg`).
- The surviving integration receipt shows 9 entries / 37 legs, zero failures,
  zero coverage blocks — matching the integration note's claim for r100.
- **Blocked, not measured:** the no-config −22 class (F1) is unmeasured in
  every piece of surviving evidence. I claim nothing about the author's
  deleted receipts beyond their absence.

## 3. Residual risks and checks not run

- No LSP: all absence proofs are literal text inspection, not semantic
  references. A dynamically-constructed reference (e.g. `getattr` by string
  name) would be invisible to it; I checked the block for such patterns and
  found none, but that check is grep-grade, not proof.
- No before/after execution: every F2 deletion is argued from the source,
  never demonstrated by a run (my role forbids the experiment).
- The rig's CLI flags (F3) could be driven by hand at any time; "unused by
  the family" is the strongest claim I make about them.
- The author's own receipts and `corpus/live/r100-author/` are gone; the
  author report's §5/§6 receipts (two green runs, negative control,
  stability sweep) cannot be re-audited from the tree — only the integration
  run survives.
- I did not audit the r99 RTP section or the safety commit's test file beyond
  confirming the diff does not touch the sofa block.

## 4. Artifacts and attribution

- This report: `reports/round-100/r100-simplifier.md` (the only repo file I
  wrote).
- Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-simplifier/`
  — `pin/measure_audio.py`, `pin/r100sofa.py` (extracted pinned bytes).
- Evidence read (frozen, unmodified): the round's scout/boundary/author and
  integration reports; `corpus/live/runs/20261016T121334985146Z-sofa-r100/measurements.json`.
- Attribution: pin and role supplied by the lead's wave item; prior evidence
  by the r100 scout, boundary, author and integration seats; this seat made
  no measurement, no edit, and no admission.

*Leaf seat — advisory inventory only; not a judge verdict, not an admission,
not a shipping decision.*
