# r97 REVIEWER — the `wppol` landing at `b8ff4efc`

**Seat.** `r97-reviewer` (specialist dispatch, read-only). **Target.**
`b8ff4efc` "r97 author: wppol WirePlumber policy lattice (5 entries/69 legs,
+2156/-3)" in `/home/vgpnk/Projects/shokunin/audio-shokunin`; committed blob
`corpus/fixtures/measure_audio.py` sha256
`7a070fa817c4de6f4ae5eb5be38e7cfc2cdbb18cad605ee52427afcf0a6ca2bc` (47 424
lines). **Receipts reviewed.** `audio-shokunin/audio-shokunin-wt-r97/corpus/live/r97-author/`
(the dispatched `../audio-shokunin-wt-r97/…` path resolves to this worktree,
which lives *inside* the repo dir) — `RECEIPTS.txt`, `receipts/*.json`,
`dev/*.json`, `battery*.log`, `fixture-sha256.txt`, plus the four
`corpus/live/runs/*-wppol-r97/` receipts in that worktree. Host toolchain as
declared (PipeWire 1.6.8 / WirePlumber 0.5.17 / Lua 5.5 / Python 3.14.7).

**Tool availability (recorded, per the reviewer contract).** The `lsp` device is
**not present in this seat's tool surface** — no `lsp` tool exists to check
`status`/`references`/`definition`/`diagnostics`. All caller/definition/diagnostic
checks below are therefore text/structural inspection of the committed blob plus
**live execution of the committed bytes**; none is presented as semantic-index
proof. No empty cold-index result is recorded as absence.

**No edits, no commits, no staging.** The only file this seat adds to the
checkout is this report (untracked). Scratch lives outside the repo at
`/home/vgpnk/Projects/shokunin/reviewer-r97/` (committed-blob copy, micro-probes,
one single-entry live run whose private root is under that scratch `tmp/`).

---

## 0. What re-derives clean (recounted independently, not taken from the author or the critic)

| claim | re-derivation | result |
|---|---|---|
| splice identity | committed 43788–45905 sha256 `f58f0290fff2f76c…` **==** worktree lines 31091–33208; dispatch 46710–46743 `68de4d267dded2a4…` **==** worktree 33808–33841 | byte-exact, both sides |
| insertion-only merge | `git diff --numstat` = `2156 3`; the only 3 deletions are the mutex list, the `mode` ternary, the `suffix` ternary; wiring at 46041 (arg row, after r96), 46051 (mutex head), 47394 (mode, r97 first), 47414 (suffix, r97 first) | PASS |
| symbol census | 77 module-level names in the block; each defined exactly once at column 0 in the merged file; 0 duplicates, 0 collisions; the five entry names occur 2× (def + dispatch); 0 conflict markers | PASS |
| parse-only behavior | `py_compile` rc 0; `--help` rc 0 listing the flag; `--probe-wppol-r97` × {r96, failing} rc 2 `choose one probe mode`; no lock/receipt/run dir written | PASS |
| leg census | from all four author receipts (and both smoke receipts), with the header's disclosed context-key rule: **14/15/21/15/4 = 69** family legs, 22 entries total (17 base + 5 r97) | PASS |
| lattice | committed constant `WPPOL_R97_SETTINGS_SHA` = 25-key list; == tracked boundary `f_settings` receipt (4 cells) == scout receipt == **operator's live instance** in both author runs, in both verifier runs, and in this seat's own live run; a direct fixture-independent `wpctl settings` read right now hashes `56526540bdc17f52…` with 25 `Id:` rows | PASS |
| PRIVATE pair | `_wppol_r97_env` points `PIPEWIRE_RUNTIME_DIR`/`XDG_RUNTIME_DIR`/`XDG_CONFIG_HOME`/`XDG_STATE_HOME`/`XDG_DATA_HOME` at the per-entry `mkdtemp` root, pops `WIREPLUMBER_*_DIR` unless a leg arms replacement semantics, and the fragments disable `hardware.audio/bluetooth/video-capture`; every `wpctl set-default`/`clear-default` call passes the private `env` (45187 / 45220 / 45254 / 45290 / 45528); the shared session is only ever read | PASS |
| custody (observed) | all four receipts + both smoke receipts: `own_procs_after: []`, `shared_census.own_hits: []`, `a12` 0 own hits, `s3` operator value `Value: true` before and after the private write, `oracle_at_start` = the operator's real USB sink (proves the "shared" reads hit the operator's session, not the private one) | PASS |
| receipts integrity | every sha/byte count in `RECEIPTS.txt` verifies (17/17); the four `receipts/` copies are byte-identical to the `runs/` originals; the frozen fixture mtime (06:42:16) precedes both final batteries (06:47:37 / 06:52:58) and `fixture-sha256.txt` records `f0eb6c50…` before each final run | PASS |
| committed bytes execute | this seat ran `wppol_settings_r97_entry()` from a scratch copy of the **committed** blob: rc-0 green, `failures: []`, no blocked classes, `s1` 25 keys / sha match, `s2` 25/25/8 rows, `s3` private read-back false + operator value unchanged, `s4` same key set + same sha, `own_procs_after: []`, `shared_census.own_hits: []` | PASS |
| live block drift | the current (later-round) worktree file is `5e4150d9…` / 47 888 lines, but its r97 span still hashes `f58f0290…` and its dispatch span `68de4d26…` — later rounds did not disturb the landing | PASS |

No mechanism law of the family was falsified by this review, and the critic's
"could not falsify a mechanism claim" verdict is reproduced. What follows is the
defect set, all of it bookkeeping/provenance/custody, in severity order.

---

## 1. Findings by severity

### R1 — MEDIUM-HIGH: the family's headline safety cross-witnesses are recorded, never armed (critic F1, extended)

- `s3_write_scope` (committed 45857–45884) reads the operator's
  `linking.follow-default-target` **before** and **after** the private write and
  stores both (45869–45873), but the only `s3` checks are the private read-back
  (45875) and `rc != 0` → named block (45877–45881). No code path can red on
  `shared_before != shared_after`; a divergent pair is a green. The critic's P3
  mutation is the live counterexample; the canonical bytes are clean
  (`Value: true` / `Value: true` in both author receipts and in this seat's own
  live run), so the report's sentence is true *on the observed bytes* and
  unguarded *as a property*.
- Same class, same entry: `s1_lattice.sha_matches_boundary` (45830–45833) is
  computed and never asserted (armed checks are rc / `n_keys` / key set,
  45834–45840), **and** `s4_shared_lattice.sha256` (45886–45897) is recorded but
  never compared to the constant — so "the lattice is install-scoped, not
  instance-scoped" rests on a field the fixture itself does not enforce. The
  verifier's `mut-sha` run is the proof: the fixture stays green with a poisoned
  constant; only the law set caught it.
- **Smallest safe correction.** one line after the two reads
  (`if sh_before.get("stdout") != sh_after.get("stdout"): failures.append(…)`),
  plus either assert the two shas or drop the fields.

### R2 — MEDIUM: the teardown/kill bookkeeping is zombie-blind, and the "restart latency" is an artifact (critic F3)

- `_wppol_r97_kill` (44226–44268) detects death with `os.kill(pid, 0)` (44247).
  The fixture never reaps its daemons, so a SIGKILLed child stays a zombie and
  the poll always runs the full grace before the SIGKILL escalation and the
  0.3 s tail. **Re-derived directly** (this seat's micro-probe): after
  SIGKILL without `wait()`, `/proc/<pid>/stat` state `Z`, `os.kill(pid,0)`
  satisfied for the whole 1.0 s window, `/proc/<pid>/environ` unreadable.
  Every `stops`/`wp_restarts` latency in every receipt is exactly
  `grace + 0.30x` — measured `1.301`, `8.305`, `8.306` (author ×4 receipts, and
  this seat's own live run: `wp`/`core` = `8.305`/`8.305`).
- Consequences: (a) the report's "observed restart latencies 1.3 s with the
  file still empty" (Remaining risks §2) mis-sizes the window by ~300× — the
  critic's instrumented run puts the decisive SIGKILL **0.004 s** after the
  mark; the 1.305 s is mark → *kill-call-complete* (`t_mark_to_restart_s` is
  recorded at 44817, before the new WP is even started); (b) SIGTERM-vs-SIGKILL
  is unobservable from the data, so "8 s graceful window" is code-true but
  receipt-unsupported; (c) `own_procs_after: []` can only mean "no **live** own
  process" — a zombie has no cmdline/environ, so the census is blind to exactly
  the residue class the kill path creates; (d) ~26 s of the defaults entry and
  ~half the battery wall is zombie polling.
- The mechanism claim itself survives: the d12 vacuity gate and red branch are
  live (critic P1/P5), and the file is genuinely unflushed at the restart in
  3/3 independent runs.

### R3 — MEDIUM: the teardown guard over-matches — a foreign process that merely *mentions* the root is killed (critic F4)

- `_wppol_r97_own` (44208–44224) is "the root path appears in
  `/proc/<pid>/cmdline` **or** `/proc/<pid>/environ`", not "a process this seat
  spawned". **Re-derived directly**: a foreign `tail -f <root>/logs/x.log`
  → `own() = True` (would be killed); a plain foreign `sleep` → `False`
  (refused). The refusal direction the boundary §2.5 asked for works; the
  over-match direction is unguarded, and the report's "the kill **refuses**
  anything else" is therefore too strong. Smallest safe correction: keep a
  module-level set of pids seen by `_wppol_r97_spawn` and require membership
  *in addition to* the path predicate.

### R4 — MEDIUM (new, not in the critic's list): `_wppol_r97_shared_env` does not strip `XDG_RUNTIME_DIR`

- 44607–44614 drops only `PIPEWIRE_*`/`WIREPLUMBER_*` overrides. The private
  pair is selected by `PIPEWIRE_RUNTIME_DIR` **and** `XDG_RUNTIME_DIR`
  (44138–44139), and the entries build private envs without mutating
  `os.environ`, so today the cross-witness reads the operator's session — proven
  by `oracle_at_start` carrying the operator's USB sink and by `s4` matching the
  operator's lattice. But if any future harness exports `XDG_RUNTIME_DIR`
  globally (a natural reading of the report's own "every … call runs with
  `PIPEWIRE_RUNTIME_DIR`/`XDG_RUNTIME_DIR` pointed at a private runtime dir"),
  `s3`/`s4`/`a12` would silently read the private instance: `a12`/census would
  likely red (`own_hits` non-empty), but `s3` and `s4`'s sha are unarmed (R1)
  and would stay green. Smallest safe correction: set `XDG_RUNTIME_DIR`
  explicitly to the operator's session dir in `_wppol_r97_shared_env` (and
  assert it differs from the private root).

### R5 — LOW: two `errclass` fields that are not observations (critic F2)

- `a3_conf_dir_missing.errclass` (44903–44907) is fed
  `(scan or {}).get("marks") and "<literal>" or ""` — any non-empty `marks`
  dict yields the literal regardless of which mark fired. Re-derived: the
  expression returns the same pair for connect-only marks, cfg-missing marks,
  and an all-`False` marks dict; a genuinely connect-shaped log classifies as
  `('wppol_connect', …)` while the field still reads `wppol_config_missing`.
- `a9_wp_on_modules_less_core.errclass` (45024–45026) reads
  `l2["stderr"]/["stdout"]`, but `_wppol_r97_variant` never returns those keys,
  so the field is structurally `[None, None]` (as in every receipt) even though
  its scan mark fired. Both fields look derived and are not. Fix or delete.

### R6 — LOW: the `pactl` claims (critic F5, with a scope correction to the critic)

- "No `pactl` call of any kind is made by this family" (r97-author.md,
  Custody) is false: every entry head calls `_capture_inventory()`
  (`pactl list sources short`, `pactl info`) and `_loopback_r79_oracle()`
  (`pactl info`) — committed 44670–44674; the receipts carry their output
  (`oracle_at_start.sink_pactl`, `pactl_exit: 0`). The intended claim (no
  `pactl` **write**; `pactl set-default-*` never called by this family) is
  true — the r97 block's only `pactl` mention is a comment (block line 65).
- **Correction to the critic's F5 parenthetical.** The critic wrote "no
  `pactl set-default-*` anywhere"; at file scope that is wrong — the committed
  blob **does invoke** `["pactl", "set-default-sink", d0]` at line 7088 (the
  r85 `pactlmon` family, a prior round's landing with its own guards), and
  records the verb at 7107. The author's "never called, anywhere" is likewise
  only true family-scoped. Neither is a defect of the r97 diff; both are
  phrasing that a later verifier could re-derive as a red.

### R7 — LOW: the census double-counts one observation (critic F6)

- `d9_lag_s` (45217) is the same expression against the same `lag_t0` as
  `d9_explicit_beats_priority.state_file_row_secs` (45202); the receipts show
  identical values (1.003/1.003, 1.002/1.002, and 1.003/1.004 in the verifier's
  runs). So 69 legs carry **68 distinct observations**. The census itself
  re-derives exactly (14/15/21/15/4), and the header's rule also lists
  `unloads`/`residual_destroy`, which no entry ever writes (`starts` is written
  in 4 entries, `pair`/`wp_restarts` sometimes as `null`) — harmless, but the
  rule as printed is a superset of the receipts.

### R8 — LOW: dead names/parameters (critic F7)

`WPPOL_R97_SINK_D` (43865) is defined once and never referenced;
`_wppol_r97_spawn(..., root=None)` (44199), `_wppol_r97_run(..., keep_raw=False)`
(44166) and `_wppol_r97_purge(env, cli, root)` (44515) carry unused
parameters (`purge` uses only `env`). Cosmetic; delete.

### R9 — LOW (new): the report's "rc 0" for the silent-fallback legs is not what the receipts record

- r97-author.md §3 says `l4`/`l6` "→ default B, **rc 0**, empty stderr". The
  receipts record `rc: null` for `l4`/`l6` (and for `l1/l3/l5/l9–l12/l17`):
  the stream is still alive at the cap and is killed by the harness, so it has
  no exit status. The fixture arms `rc ∈ {0, None}` (45394, 45401), i.e. the
  claim is "no error exit and empty stderr". The armed cells (default B, empty
  stderr) hold in all four receipts; the "rc 0" wording is not receipt-backed.

### R10 — LOW (provenance, new): the pre-freeze smoke bytes are not retained

- `fixture-sha256.txt` records two smoke runs on `4978e90c…` (06:33, 06:38)
  and two final runs on `f0eb6c50…` (06:47, 06:52); the fixture mtime is
  06:42:16, i.e. the smoke runs preceded the correction and the final batteries
  followed it on the frozen bytes (sha recorded before each run). The claim
  that the difference is *comment-only* cannot be byte-verified — the
  intermediate bytes are gone. Coherence evidence instead: both smoke receipts
  carry the same 69-leg census, `failures: {}`, the same lattice sha and the
  same `s3` values as the finals. Disclosed as non-record; recorded here as a
  gap, not a defect.

### R11 — INFORMATIONAL (method)

- The family lock (`_r97_family_lock = _wppol_r97_family_lock()` at 46733,
  inside the dispatch block) is taken in `main()` only, at a **tree-relative**
  path: single-entry drivers
  (the author's `dev_one.py`, the verifier's `r97v_entry.py`, this seat's
  driver) bypass it, and two checkouts do not exclude each other. My live run
  therefore ran unlocked (it ran alone). The family is safe under overlap
  (pid-namespaced everything — the verifier's F3 and the critic's §5 agree);
  the lock must not be read as a global exclusion.
- The author's "17 pre-existing base entries (14 legs each)" uses a different
  counting convention (14 top-level keys *including* `failures`, i.e. 13
  observations) than the r97 census rule. Descriptive only; the base entries
  are outside the 69.

---

## 2. Critic F1–F7 cross-check

| critic finding | this seat's verdict | evidence added / corrected |
|---|---|---|
| F1 `s3` fail-open (+ `s1` sha unarmed) | **CONFIRMED**, extended | code 45857–45884; also `s4.sha256` unarmed (45886–45897); clean on observed bytes in both author receipts and my live run |
| F2 `a3.errclass` constant, `a9.errclass` dead | **CONFIRMED** | micro-probe: literal returned for connect-only / all-`False` marks; true class of a connect log is `wppol_connect`; `a9` structurally `[None, None]` |
| F3 zombie-blind kill; `t_mark_to_restart_s` ≠ restart latency | **CONFIRMED** | micro-probe zombie proof (`Z`, `kill(pid,0)` ≥1.0 s, environ unreadable); `grace+0.30x` in every receipt incl. my run; `t_mark_to_restart_s` recorded at 44817 before the WP start |
| F4 guard over-match | **CONFIRMED** | micro-probe: foreign `tail` mentioning the root → `own()=True`; plain foreign `sleep` → `False` |
| F5 "no pactl call of any kind" false | **CONFIRMED**, scope-corrected | entry head 44670–44674; the file *does* invoke `pactl set-default-sink` at 7088 (r85 family), so "anywhere" is too broad on both sides |
| F6 `d9_lag_s` re-read | **CONFIRMED** | 45202 vs 45217, identical t0/expression; identical values in all receipts |
| F7 dead code | **CONFIRMED** | 43865, 44166, 44199, 44515 |

No critic finding was refuted; two were sharpened (F1 → `s4`; F5 → file-scope
`pactl set-default-sink` invocation). The critic's headline ("bookkeeping and
provenance only; no mechanism law falsified") matches this seat's independent
re-derivation.

---

## 3. Residual risk

1. **The unarmed witnesses (R1/R4) are the only place a real regression could
   hide green**: an operator-side change or an env-export mistake would not red
   the family, only a law set or a human. Cheap to close.
2. **Timing cells are load- and host-conditional.** The d12 window is a *state*
   (flushed vs unflushed), correctly gated; the reported magnitudes are not
   trustworthy (R2), but the vacuity path is live and named.
3. **Census honesty (R2c/R11)**: `own_procs_after: []` and the exit census are
   "no live process", not "no residue"; the daemons the family kills become
   zombies and are reaped only when the fixture exits.
4. **The receipts are worktree-lineage evidence** (`f0eb6c50…`, base
   `5755be5b` lacking r90–r96). The block is byte-identical and the verifier's
   two full runs plus my single-entry run are on the committed blob, so the
   transfer is covered — but the author's own receipts never executed the
   merged file.
5. **R9/R6/R10** are report-level; they cannot change a measured cell but they
   will cost a future verifier re-derivation time.

## 4. Verification gaps (what this review did not cover)

- The C-side `state:save_after_timeout` timeout is still unverifiable from the
  installed Lua (author's labrat partial; critic §7.1) — R2 explains the
  *recorded* latency, not the flush mechanism, and the d12-vs-d9 spread
  (≥1.6 s vs 1.003 s) is explained by the kill artifact, not by the C timeout.
- `wpctl status` against a *half-initialised* WirePlumber was not tested (only
  with WP killed) — author-disclosed, unchanged.
- `l18`'s movement path (which setting actually moves a live stream) remains
  unidentified; recorded, deliberately unarmed, as the boundary directed.
- No LSP-backed caller/definition sweep was possible (no `lsp` device); the
  symbol census (77 names, each defined once) and the live run are the
  substitute, not an index.
- I did not re-run the full battery: the verifier (2 runs on committed bytes,
  260-law set) and the critic (1 run) already did, and my single-entry run
  reproduces the settings entry green on the committed bytes. My run was
  lock-free (R11) and concurrent with whatever else was live on the host.

## 5. Evidence index (this seat)

- `/home/vgpnk/Projects/shokunin/reviewer-r97/committed-measure_audio.py` —
  `git show b8ff4efc:corpus/fixtures/measure_audio.py`, sha `7a070fa8…`;
  `block.py` = committed 43788–45905 (`f58f0290…`).
- `…/micro.py` + output — zombie proof, `own()` over-match, `errclass` constant
  (run against the scratch copy of the committed blob).
- `…/one_entry.py`, `…/tree/r97reviewer-settings.json`, `…/r97reviewer-settings.log`
  — live settings-entry run on the committed bytes (green; `s1/s2/s3/s4`,
  `stops` 8.305/8.305, `own_procs_after: []`, `shared_census.own_hits: []`).
- `…/live-wpctl-settings.txt` — direct fixture-independent `wpctl settings`
  read, sha `56526540bdc17f52…`, 25 keys.
- `…/tree/…/measure_audio.py --help` and the two mutex checks — parse-only
  re-derivations.
- Scratch private root `…/tmp/wppol-r97-1157000-qlqloc_e` (daemons stopped by
  the family's own guard; kept as residue evidence).

Seat stop. This is a recommendation set, not an admission; the canonical Rust
runtime remains the sole judge.
