# r98 reviewer — caller/error-path/propagation audit of the pinned pwstream family

Identity: **reviewer** (leaf, read-only), round **N=98**, role **reviewer**.
Source pin: **`bb177513a615a32d3bc150ecbdcf78302e110d8c`** (`r99 safety: require
explicit opt-in before physical LAN control`, HEAD of main at dispatch).
Flag: **`pwstream-r98`**. Scope: the pinned `--probe-pwstream-r98` family in
`corpus/fixtures/measure_audio.py` (family block + dispatch) and
`corpus/fixtures/r98stream.c`, plus the round's frozen evidence. Advisory only;
no live family, no source edit, no commit, no shipping authority.

**LSP gap (recorded):** this seat has no LSP device/tool; every check below is
literal pinned-source inspection (`git show PIN:path`) plus read-only reads of
frozen receipts. Grep was used only as literal text search and is never
presented as semantic proof.

## Commands actually executed

`git log/ls-tree/show` at the pin; `git show PIN:corpus/fixtures/measure_audio.py`
and `:corpus/fixtures/r98stream.c` extracted to scratch; `sha256sum`/`wc -l`/
`sed -n` block extraction; `diff` of landing-block vs pin-block; `grep` on the
extracted pin bytes; read-only `python3` JSON summaries of the two frozen
receipts; `find`/`ls` for receipt provenance. No tracked file was written, no
process spawned beyond these, no service touched, `RTP_R99_ALLOW_LAN_CONTROL`
never set, no live family run (verifier-only per assignment).

## Provenance chain (verified before findings)

- Pin family block (lines 46326–48676 of the pinned blob, 2351 lines incl. the
  leading separator) sha256 **`ba7e3b58…71ada`** — byte-identical to the r98
  landing commit `d41cfa68`'s block (lines 45906–48256) **and** to the author
  worktree's `measure_audio.py` (`c9d7627b…`, block at 31091–33441) — the exact
  bytes both cited batteries ran. Independent re-derivation; not taken from the
  integrate note.
- Pin dispatch block (55142–55172, 31 lines) sha **`965e7e3d…956b`** — matches
  the integration's record.
- Pin `r98stream.c` sha **`9f840a6b…d323`** = author-worktree copy = the
  `probe_build.source_sha256` recorded **inside both green receipts** — the
  batteries compiled the committed source.
- Wiring at pin: argparse row 54390, mutex token in the sum at 54400 (4th of
  141), `mode` 55944 / `suffix` 55964 ternaries, dispatch 55142–55172 calling
  all six entries under a family lock held to exit (55160).
- All 12 cross-family helpers the block calls exist at pin:
  `_capture_inventory` 3151, `_playback_r78_node_names` 6149,
  `_playback_r78_foreign_clients` 6450, `_loopback_r79_oracle` 8949,
  `_capture_r77_sink_names_strict` 11902, `_pwcat_r83_ns_load` 16634,
  `_alsapw_r84_loadavg` 19038, `_alsapw_r84_killpg` 19202,
  `_pactlmon_r85_node` 21818, `_pactlmon_r85_unload_own` 21880,
  `_pwprof_r89_stream` 29550, `_pwprof_r89_jparse` 29662. The block is
  self-contained **against this pin** (it is not standalone-runnable; nothing
  claims it is).

## Findings (by severity)

### M1 — unguarded sandbox setup can abort the whole battery with zero receipt (inferred, static)

- Where: `measure_audio.py` (pin) **47142–47147** —
  `subprocess.run(["pw-cli", "create-node", …], timeout=25)` inside
  `_pwstream_r98_sb_start` raises `subprocess.TimeoutExpired` (or `OSError`)
  uncaught; the three sbx call sites (48577–48582, 48598–48603, 48624–48630)
  catch **only `RuntimeError`**. Also **47048–47049** —
  `shutil.copy("/usr/share/pipewire/pipewire.conf", …)` /
  `client.conf` raise `FileNotFoundError` uncaught (hardcoded distro paths).
- Failure path: a wedged/loaded graph (the author's own §4.1 class: every
  `pactl`/`pw-dump` subcommand timing out) hangs `pw-cli create-node` →
  `TimeoutExpired` at 25 s → propagates through `pwstream_sbx_r98_probe`'s
  `finally` → the dispatch (55161–55172, bare entry calls, no try/except) →
  `main()` dies **before** the receipt write (55963–55967) → **no
  `measurements.json` at all**: entries 1–5's completed evidence is lost with
  it, and the family lock releases at exit.
- Evidence: source-only trace; both frozen receipts are green (never
  triggered). The lone `except Exception` in `main` (55599) belongs to the old
  sox/decode pipeline, not a dispatch wrapper — no family wraps its entries,
  so this is the file-wide pattern, but the reachable raisers are r98-specific
  code.
- Smallest correction: catch `TimeoutExpired`/`OSError` at the two call sites
  and convert to the same named `coverage_blocked` shape the `RuntimeError`
  path already produces (or wrap each dispatch entry call).
- Status: **inferred** (static), not observed in any receipt.

### M2 — route entry's `sinks_gone` teardown census is vacuous (observed)

- Where: route entry keys its loads by **tag** — `loads[tag] =
  _pwstream_r98_load_ns(name)` for `tag in ("ns","ns2")` (48020–48022) — while
  `_pwstream_r98_teardown` computes
  `gone = {nm: nm not in sinks_now for nm in (loads or {})}` (46871) over the
  dict **keys**. It therefore tests the literal strings `"ns"`/`"ns2"`
  against real node names → always `True`.
- Evidence: receipt `20261016T101046237597Z` route entry records
  `sinks_gone: {'ns': True, 'ns2': True}` (tag keys) vs the core entry's
  correct `{'r98a_ns_903127': True}` (real sink names). Same in run 2.
- Impact: the claimed "final sink census armed" safeguard silently degenerates
  in **1 of 6 entries**; a surviving route sink would not be flagged by
  `sinks_gone`. Backstops that still hold: `residual_destroy` scans the graph
  for `r98a_<pid>` names (46855–46864) and `own_nodes_after` uses the same
  substring (46883–46889) — in both receipts `own_nodes_after: []`,
  `residual_destroy: None`, and the unloads themselves are name-verified
  (`verified_index == captured`, exit 0), so no real residue was hidden in
  these runs. The defect is the check, not the teardown.
- Smallest correction: one line in `_pwstream_r98_teardown` — key the census
  by `leaf.get("value", tag)` instead of the raw key.
- Status: **observed** (receipt + source).

### M3 — xw stall legs bypass the §3.5 transient guard → false red under the documented host class (inferred)

- Where: the stall legs are spawned by direct `Popen` (48365–48373), not via
  `_pwstream_r98_run`, so they get neither the transient retry (46631–46653)
  nor a `transient` marker; the gap arm at 48399–48406 then reads
  `stall_gap_ms`, which the C fixture prints as **0** when the stall never
  fired (both timestamps 0 — `r98stream.c` 966–969).
- Failure path: the boundary's §3.5 class (autoconnect leg lands `paused`,
  no link, no error — 9/44 attack legs in one documented window) hits a stall
  leg → `stall_gap_ms=0 outside [250,400]` **and** `follower xrun_count=None
  < 10` are appended as failures; the sweep (47186–47202) drops failures only
  for legs carrying a `transient` marker or an errored `link_snapshot` —
  stall legs have neither → the false reds stand, contradicting the sweep's
  own docstring "never a false red" (47183–47185).
- Smallest correction: route the stall spawn through `_pwstream_r98_run`
  (inherits retry + marker + sweep), or add a paused-no-error →
  `coverage_blocked` branch before the gap arm.
- Status: **inferred** (static); 0/236 boundary census legs hit it, but the
  class is documented in-repo.

### M4 — `t_id` fallback witness silently downgrades when `object.id` fails to resolve (inferred)

- Where: 48085–48087 — `target=str(_pwstream_r98_object_id(PWSTREAM_R98_NS))`;
  on a graph-read error or absent node this returns `None` → `target="None"`
  → the leg becomes a **garbage**-fallback leg, whose armed expectation
  (link to the default sink) still passes. The F5 witness ("an id resolves
  like garbage, not like a serial") silently loses its discriminating power.
- Evidence: receipt `t_id_r0` argv shows `target=157` — a real id in the
  author's windows; latent only.
- Smallest correction: `oid is None → coverage_blocked; continue`.

### M5 — family lock fails open on `OSError` (inferred)

- Where: 46744–46747 — if the fixed-path lock file cannot be created/opened,
  `_pwstream_r98_family_lock` returns `None` and the run proceeds **without
  same-family exclusion**, unrecorded. (A second *runnable* run still blocks
  on `flock`; the gap is the uncreatable-file case, e.g. a read-only corpus.)
- Smallest correction: record a `coverage_blocked` (or refuse) on lock
  failure instead of proceeding unlocked.

### I1 — the r98 execution evidence is untracked; the canonical tree carries none (info)

- The two green batteries cited as "evidence of record"
  (`corpus/live/runs/20261016T101046237597Z-pwstream-r98/measurements.json`,
  `…T101258039942Z…`) exist **only** in the untracked author worktree
  `audio-shokunin-wt-r98/corpus/live/runs/`; the canonical tree has no
  `*-pwstream-r98` run dir anywhere. The pin tracks 5745 `corpus/live/runs`
  files — all 20261012 — and **zero 20261016 receipts**, so committing run
  receipts is the repo's own established practice; the final-wave rounds
  deviate. The integrate note discloses "untracked, not carried", but the
  author report's §2 paths do not resolve in the canonical tree and the
  worktree is prunable. Committing the two `measurements.json` (324 KB each)
  would close it.

### I2–I4 (info, no action required for admission)

- **I2:** `PWSTREAM_R98_ENV_LEVERS` (46389–46391) covers the five
  `stream.c:2142-2163` levers but not `PIPEWIRE_REMOTE`; an inherited value
  is neither cleared (46415–46416) nor censused (46770–46771). Failure mode
  is loud (every leg fails connect), not silent. Low.
- **I3:** `sb_run`'s "ONE named retry" (48511–48536) undercounts: the runner's
  internal retry (46631–46653) fires first, so a paused sandbox leg can spawn
  up to 4 probes; bounded, and a leg can collect two `coverage_blocked`
  entries (entry-level 48531–48534 + sweep 47190–47192). Cosmetic.
- **I4:** the C fixture's `props` mode (921–926) and the
  `no_convert`/`early_process`/`async`/`map_buffers`/`rt_trigger_done` flags
  (573–583) are parsed but unused by the family's legs — dead options
  (simplifier's territory, noted not actioned).

## Safeguards traced and confirmed (source matches claim)

Family lock at the fixed `corpus/live/` path, held to exit (46739–46755,
55160); per-leg clearing of the five `PIPEWIRE_*` levers plus the
`inherited_env_levers` census (46410–46419, 46770–46771; receipts: `[]`);
name-verified unloads via `_pactlmon_r85_unload_own` with `field`/`value`
carried on each load leaf (46847–46853; receipts: `verified_index == captured`,
exit 0); **zero `set-default-*` occurrences** outside the banner comment;
`start_new_session=True` on every spawn with `killpg` escalation
(SIGTERM→SIGKILL on players/daemons 46839–46846, 47082–47103; SIGKILL on leg
timeout 46615–46621); `RLIMIT_CORE=0` on the crash class only (46434–46441,
46603, 48448/48460); NULL-context hardening in C (`pw_main_loop_new`/
`pw_context_new` checked → `R98 ctx_error=…` + rc 3, C 709–723); the `hold`
guard placed **after** the activate/trigger branches and before the
fall-through quit (C 479–546 — the author's §5.2 correction is real in the
committed bytes); `name=` prefixed `r98a_` in C (755) matching the Python
side's `node_name="r98a_"+tag`; full-text `stream_error` preserved end-to-end
(C 937; Python free-text pass 46509–46515); the §3.5 transient guard on all
runner-driven legs + the single-point sweep (46631–46653, 46961–46993,
47178–47203) — except the xw stall legs (M3); default-sink resolution via
`pactl get-default-sink` with unresolved-alias → named coverage block
(46781–46807, used at 47395–47399 and 48102–48107); volatile text recorded
never armed (duplicate-Link count 48060–48066, crash-source state 48467–48476,
Goertzel pair recorded 48220–48222, `ticks` armed only across structurally
equal legs 47826–47839, mismatch-case `requested` unpinned — the sbx
upsampled leg passes no `want_req`); rate-relative geometry armed as
`nbufs ∈ {12288,13375}` / `maxsize ∈ {49152,53500}` with the sandbox 44100
axis and matched twin (47600–47607, 48611–48618); drain period armed relative
to the leg's own request, ratio [0.6, 1.6] (47875–47881); trigger FALS armed
(30 calls, cb ≤ 4, min gap ≥ 350 ms, cb < tc, 47744–47765); RT/non-RT param
lattice classes (47682–47703); xrun injection armed probe-side
(`stall_gap_ms`) with the profiler scoped to own node names and driver-0 +
ratio bands (48399–48445); crash class recorded, never gated (48447–48476);
sandbox with hardware monitors disabled and the no-ALSA absence armed
(47060–47067, 48558–48571; receipts: `[]` for all four WP variants); bare-core
twins with `retry_transient=False` (48651–48653).

## What the evidence supports (measured vs blocked vs not-run)

- **Measured (by the author, read by me):** both frozen receipts show exactly
  67 legs (core 15 / run 18 / route 12 / cap 4 / xw 4 / sbx 14 — matching my
  independent source census), `failures: []` in every entry, and exactly one
  coverage block (`cap_noprop` policy row, disclosed). Spot-checked values
  match the author's §2 table: geometry 49152 B/12288 frames/stride
  4/requested 1024 (both reps), `ticks` 87040 == 87040 at cb 8, drain 43.0 ms
  at request 1024, trigger 30 calls → 3 callbacks (421/901/1381 ms), param
  lattice 7-event non-RT / 5-event RT, xruns 27/55 ratio 2.037, crash class
  rc −11 SIGSEGV (gated false) with the Audio/Source twin at rc 0, capture
  pins 71680 frames / nz 69629 / peak 0.499969, teardown `sinks_gone`
  all-true / `own_nodes_after: []`, `link_stability` 3/3 streaming,
  `inherited_env_levers: []`. The batteries compiled the committed fixture
  (`source_sha256` inside the receipts).
- **Blocked/unmeasured by design and honestly labeled:** the `cap_noprop`
  policy row (recorded, never armed), the duplicate-Link count (recorded),
  the crash-source post-connect state (recorded), mismatch-case `requested`
  (unpinned), bare-core enumeration (not censused).
- **Not run by this seat:** no live family (verifier-only); no measurement
  re-derived; the green claim rests on the two frozen receipts, which are
  untracked (I1).

## Residual risks and explicit checks not run

1. Timing-sensitive arms (`cadence [200,330] ms`, `trigger_count [29,30]`,
   `queued == nbufs`, `dequeue_null == 0`, xrun bands) could false-red under
   extreme load; they held in the author's loadavg 51–67 windows. Not
   re-tested.
2. M1 is exactly the failure mode a verifier run would exercise under a
   graph wedge — the verifier's single run is the live test of it; a wedge
   during sandbox setup would lose the entire run's receipt.
3. M3's false-red path needs the §3.5 transient to land on one of the two
   stall legs specifically (0/236 in the boundary census; 9/44 in one attack
   window across autoconnect legs generally).
4. No LSP in this seat: caller/definition checks are literal-source traces
   against the pin, not semantic-index proofs (gap recorded above).
5. Out of scope, not audited: the r93/r99/r100 blocks in the same pinned
   file; the scout/boundary raw receipts; `LOG.md`/`SCORECARD.md`
   dispositions; the r90 foldfix hunks (the pin post-dates the r98 landing;
   the r98 block itself is byte-identical landing↔pin, so the foldfix did
   not touch it).

## Artifacts and attribution

- Report: `reports/round-98/r98-reviewer.md` (this file; only my assigned
  report was written in the repo tree).
- Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-reviewer/`
  (`measure_audio_pin.py`, `r98stream_pin.c`, `ma_landing.py`,
  `block_landing.py`, `block_pin.py` — pin extractions and diff inputs).
- Frozen inputs read, not modified: the two author receipts in
  `audio-shokunin-wt-r98/corpus/live/runs/20261016T{101046237597,101258039942}Z-pwstream-r98/`
  (untracked worktree evidence; **not** committed, **not** remotely
  available), and the four committed round-98 reports (scout/boundary/
  author/integrate).
- Attribution: all findings above are this seat's static trace of the pinned
  bytes plus read-only receipt reads; the measured values quoted are the
  author's receipts, verified against their internal `source_sha256`, not
  re-derived. Advisory only — the canonical Rust runtime remains the sole
  judge.
