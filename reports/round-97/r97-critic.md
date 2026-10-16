# r97 CRITIC — the `wppol` WirePlumber-policy family at `b8ff4efc`

**Seat.** `r97-critic` (specialist dispatch). **Target.** `b8ff4efc` "r97 author:
wppol WirePlumber policy lattice (5 entries/69 legs, +2156/-3)" in
`/home/vgpnk/Projects/shokunin/audio-shokunin`. **Host** `plazir27`, 32 cores,
PipeWire 1.6.8 / WirePlumber 0.5.17 / Lua 5.5 / Python 3.14.7 — the author's
toolchain, re-verified. **Window** 2026-10-16 07:01Z–07:15Z (≈14 min wall; the
host was *not* quiet: loadavg 4–9, and a **second full `--probe-wppol-r97`
battery from the r97 verifier lane was live the whole time**, see §7).

**Archive checkout (under /home, never /tmp).**
`/home/vgpnk/Projects/shokunin/critic-r97/wt` — a registered `git worktree`
of `audio-shokunin` detached at `b8ff4efc` (prunable; the fixture there is the
**committed** file, sha `7a070fa8…`, 47 424 lines). Mutation copies live in
`critic-r97/mut/p1…p5`, probe outputs in `critic-r97/out/`, logs in
`critic-r97/logs/`. Nothing was written to the main checkout except this
report; main's fixture sha is unchanged and `git status` carries no new
modification.

**Verdict shape (no judgment — the canonical Rust runtime is the sole judge).**
I could not falsify a single headline mechanism claim of the family: the splice
is byte-exact, the private-pair isolation and custody claims hold under live
re-measurement, the flush-gated restart race is armed 3/3 on independent runs
and its vacuity gate and red branch are both live, and a full battery on the
**committed** bytes is green (69 legs, `failures: {}`, no blocked classes).
What I did falsify is **bookkeeping and provenance**: seven in-place fixable
defects (§4), the largest being an unarmed safety cross-witness (F1) and a
stop/restart latency number that is a zombie-poll artifact, wrong by ~300×
(F3). None of them changes a mechanism law; all of them inflate or fail-open a
receipt field that a later verifier will re-derive.

---

## 1. What I ran

| probe | patch on the pristine bytes | what it must show | observed |
|---|---|---|---|
| **P0** baseline | none — `wppol_defaults_r97_entry()` from the committed file | reproduce the author's d9/d12/d13 | `failures: []`; d12 unflushed (state file `""`), `default_after = Q`, `configured_after = null`; d13 row at **1.003 s**; wall **54.1 s** (`out/base-defaults.json`) |
| **P1** red-branch liveness | `time.sleep(3.0)` inserted after the gate read, before `_wppol_r97_restart_wp` (the sleep lands *after* the gate's sample, so this probes the red branch — P5 probes the gate) | a surviving choice must red | **2 reds**: `d12_restart_race_lost: the configured choice survived an unflushed restart — the race did not arm ('r97a_sp_814646')` and `a configured row survived the unflushed restart` (`out/p1-defaults.json`) |
| **P4** signal-instant instrumentation | record the first-signal monotonic in `_wppol_r97_kill`, expose `t_set_to_SIGNAL_s` in d12 | the decisive kill is ~ms after the gate, not 1.3 s | `t_set_to_SIGNAL_s = 0.004` vs `t_set_to_restart_s = 1.305`; gate false; `default_after = Q` (`out/p4-defaults.json`) |
| **P5** vacuity-gate liveness | `time.sleep(3.0)` inserted *before* the gate read (`state_at_set`) | a flushed window must be a named vacuous class, never a red | `coverage_blocked: ["d12_restart_race_lost: the state file had already flushed before the restart — the race window was missed, cell unarmed"]`, `failures: []` (`out/p5-defaults.json`) |
| **P3** s3 fail-open | the *shared* after-read taken from the **private** instance (`env=env`) | a divergent before/after must red if the witness is armed | `shared_before='Value: true\n'` vs `shared_after='Value: false\n'` (divergent) and **`failures: []`** (`out/p3-settings.json`) → F1 |
| **Surgical A** | pristine module; two *different* arming failures | the a3 `errclass` field must track the log | canonical empty dir: rc **78**, marks `[config-missing]`; broken-fragment dir: rc **69**, marks `[Failed to connect…, opening config file:, opening fragment file:, using configuration file:]` — **identical `errclass` field** in both (`out/surgical.json`) → F2 |
| **Surgical B** | pristine module; guard attacks | refuse foreign pids | plain foreign `sleep` → `{"killed": false, "reason": "REFUSED foreign pid"}`, alive ✓; a foreign `tail -f <root>/logs/reader-target.log` → **`{"killed": true, "sig": "KILL"}`** → F4 |
| **Zombie proof** | 5-line direct experiment | — | a SIGKILLed, unreaped child: state **`Z`**, `os.kill(pid,0)` OK for the whole window, `/proc/<pid>/environ` unreadable → explains `grace + 0.305 s` in every stop record → F3 |
| **Full battery on committed bytes** | none — `python3 wt/corpus/fixtures/measure_audio.py --probe-wppol-r97` | the splice runs end-to-end | rc 0, **`failures: {}`**, **69 legs (14/15/21/15/4)**, no `coverage_blocked`, `own_procs_after: []` and `own_hits: []` in all five entries, d12/d13 reproduce; wall **5.3 min**; receipt `wt/corpus/live/runs/20261016T101312036321Z-wppol-r97/measurements.json` sha256 `51d95b79dd89f708132742b1a5094bad19644cb8dc0969fdce145e6f78f709e9` |

All probes ran with `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`,
`PYTHONDONTWRITEBYTECODE=1`; every daemon is a private core+WirePlumber pair
under its own `mkdtemp` root; the operator's instance was only ever *read*.

---

## 2. Splice review — re-derived: byte-exact, and end-to-end

Re-derived independently, not taken from `r97-integrate.md`:

| check | result |
|---|---|
| family block | main lines **43788–45905** sha256 `f58f0290fff2f76c5c343db643585d3b9bb32912dee99aa7e129f262cc8243f5` **==** WT lines 31091–33208 — byte-identical (2118 lines) |
| dispatch block | main lines **46710–46743** sha256 `68de4d267dded2a4ad2c5ae5f5a7a59e823d63d594bdcd8a8a48317644dea3b9` **==** WT 33808–33841 |
| placement | block ends `return entry` + 2 blank lines + `def main():`; dispatch preceded by `_pulsecli_r96_cork_entry()`, followed by `if args.probe_pactlmon_r85:` — both anchors as disclosed |
| argparse row | `--probe-wppol-r97` at 46041, immediately after the r96 row (main's newest r9x row) |
| mutex | `args.probe_wppol_r97` at the **head** of the sum list, 46051: **140 tokens, 0 missing, 0 extra, 0 duplicate** against 140 `parser.add_argument("--probe-*")` rows — the whole probe mutex is complete for this flag *and* for every other one |
| mode / suffix | r97 first in both ternaries (47394 / 47414) |
| namespace | the block defines **77** module-level names, each **exactly once** in the merged file; only **4** lines outside block+dispatch mention `r97a`/`wppol` — the four wiring lines. No stale r97 copy from any earlier round |
| behavioural | `--help` rc 0 listing the flag; `--probe-wppol-r97` × {`--probe-failing`, `--probe-pulsecli-r96`, `--probe-pwprof-r89`} all rc 2 `choose one probe mode`; **no** lock, receipt or run dir written by any parse-only exit (main's `corpus/live/measure_audio-wppol-r97.lock` absent) |
| end-to-end | the full battery in §1 row 9 ran the **committed** file: green, 69 legs, receipt written under the `-wppol-r97` suffix |

The only splice nit: the author's `--probe-wppol-r97` row sits after `--probe-pulsecli-r96`
here, while in the author worktree it sat at the end of the *r9x* group they had
(r88 last). Both are non-semantic; the integrate note discloses it.

---

## 3. Flush-gated restart race (d12/d13) — re-checked; **claim holds**, the *latency* does not

Independent observations (author run 1, run 2, my P0, my P4, my battery):

| run | d13 row appears at | d12 `state_file_before_restart` | d12 `t_set_to_restart_s` | d12 outcome |
|---|---|---|---|---|
| author run 1 (`…094737705611Z`) | 1.003 s | `""` | 1.306 | lost → Q, no configured row |
| author run 2 (`…095258906395Z`) | 1.003 s | `""` | 1.305 | lost → Q, no configured row |
| critic P0 | 1.003 s | `""` | 1.304 | lost → Q, no configured row |
| critic P4 (instrumented) | — | `""` | 1.305 | lost → Q; **signal at 0.004 s** |
| critic battery (committed bytes) | 1.003 s | `""` | 1.304 | lost → Q, no configured row |

- **Armed 3/3** independent full-run d12 cells (the file was genuinely empty at
  the restart in every run), and the P5 mutation proves the vacuity gate is
  live: flush first ⇒ `coverage_blocked` named block, **no red**.
- The P1 mutation proves the red branch is live: a *surviving* choice produces
  two reds.
- **F3 below**: the "1.3 s restart latency" the report reasons from is the
  zombie poll, not the restart. The decisive SIGKILL lands **4 ms** after the
  `set-default` mark. Measured flush lag is **1.003 s** in the d9/d13 shapes and
  **> 1.6 s** in the d12 shape (file still `""` after the restart) — the window
  is *not* a ~1 s constant, and the header's "the boundary's ~1 s race" should
  read "≥1 s, shape-dependent". The mechanism claim survives; the number used to
  size it is wrong by ~300×.

---

## 4. Findings (all in-place fixable; none falsifies a mechanism law)

### F1 — `s3_write_scope` cross-witness is recorded, never asserted (fail-open). **Live counterexample.**
- **Counterexample.** P3: `shared_before='Value: true\n'` vs `shared_after='Value: false\n'`
  — i.e. the operator's value *appears changed* — and the entry still returns
  `failures: []` with no `coverage_blocked`. Nothing in the code can red on it:
  the only s3 checks are the private read-back (45875) and `rc != 0` → named
  block (45878). Same class, same file: `s1_lattice.sha_matches_boundary` (45830)
  is computed and never asserted (the armed checks are rc / `n_keys` / key set,
  45834–45838).
- **Evidence.** Canonical runs *are* clean (`shared_before == shared_after ==
  'Value: true\n'` in both author receipts and in mine), so the report's sentence
  is true on the observed bytes — it is simply **not armed**, so the family's
  headline safety property ("the operator's value is unchanged") fails open.
- **Impacted axes.** custody/isolation-safety; receipt provenance.
- **Smallest safe correction.** one line after the two reads:
  `if sh_before.get("stdout") != sh_after.get("stdout"): failures.append("s3_write_scope: the operator's value moved under a private write")`
  — and either assert `sha_matches_boundary` or drop the field.

### F2 — `a3_conf_dir_missing.errclass` is a constant literal, not an observation. **Live counterexample.**
- **Counterexample.** 44903: `_wppol_r97_errclass((scan or {}).get("marks") and
  "Could not locate configuration file 'wireplumber.conf'" or "")`. `marks` is a
  9-key dict whenever the scan succeeded, so the literal is *always* fed and the
  field is `('wppol_config_missing', "Could not locate configuration file
  'wireplumber.conf'")` **whatever the log said**. Surgical A: a broken-fragment
  config dir fails completely differently (rc 69, marks `Failed to connect to
  PipeWire` / `opening config file:` / `opening fragment file:` /
  `using configuration file:`) and the field is **byte-identical**; with all
  marks `false` the expression still returns the same pair.
- **Mirror image.** `a9_wp_on_modules_less_core.errclass` is `[None, None]` in
  both author receipts although its `Failed to connect to PipeWire` mark *did*
  fire (45024 → the r88/r87 table has no class for it). The field is not a
  function of the observed log in either direction.
- **Impacted axes.** receipt provenance (a field that *looks* derived).
- **Smallest safe correction.** derive it from the log the leg already writes:
  `_wppol_r97_errclass(_wppol_r97_log_tail(v1.get("log"), 1 << 20) or "")`, or
  delete the key from both a3 and a9.

### F3 — the stop/restart bookkeeping is zombie-blind: every latency is `grace + 0.305 s`, and `t_mark_to_restart_s` is not a restart latency. **Live counterexample.**
- **Counterexample.** P4 (instrumented): `t_set_to_SIGNAL_s = 0.004` while
  `t_set_to_restart_s = 1.305`. The 1.3 s is the poll loop in
  `_wppol_r97_kill` (44226), whose death detector is `os.kill(pid, 0)` (44247) —
  satisfied by a **zombie** (the fixture never reaps its daemons). Direct proof:
  after SIGKILL, state `Z`, `kill(pid,0)` OK for the whole 1 s window,
  `/proc/<pid>/environ` unreadable. Every stop record in every receipt is
  therefore exactly `grace + 0.305`: `1.301` (fast), `4.303` (default grace),
  `8.305` (graceful) — **4/4 of the author's receipts** (2 battery + 2 disclosed
  pre-freeze smoke: `stops {wp: 8.305, core: 8.305}`, `restarts {immediate:
  1.301, durable: 8.305}` in all four) and **4/4 of mine**.
- **Consequences.** (a) the report's "observed restart latencies 1.3 s with the
  file still empty" and the header's "~1 s race" mis-size the window by ~300×;
  (b) the SIGTERM-vs-SIGKILL distinction is **unobservable** from the data, so
  "an 8 s graceful window before SIGKILL escalation" is not supported by the
  family's own receipt; (c) `own_procs_after` (44709; predicate `_wppol_r97_own`
  44208 via `_wppol_r97_own_procs` 44646) can never see an unreaped own child —
  a zombie has no cmdline and no environ — so the honest reading of
  `own_procs_after: []` is "no **live** own process";
  (d) cost: in the defaults entry ~26 s of the 54 s wall is zombie polling
  (1.3 + 8.3 + 8.3 + 8.3), and ~half of the 5.3 min battery.
- **Impacted axes.** timing-accuracy of the record; census honesty; cost.
- **Smallest safe correction.** in `_wppol_r97_kill`, treat `/proc/<pid>/stat`
  state `Z` (or `os.waitpid(pid, os.WNOHANG)`) as dead, and record the instant of
  the first signal (`t_signal`) next to `secs`; keep `t_mark_to_restart_s` only
  if it is redefined as mark→signal.

### F4 — the teardown kill guard over-matches: a foreign process that merely *mentions* the private root is killed.
- **Counterexample.** Surgical B: a foreign `tail -f <root>/logs/reader-target.log`
  (clean env, started by the critic) → `_wppol_r97_kill` returns
  `{"killed": true, "sig": "KILL"}`. The predicate (44208) is
  "cmdline **or** environ contains the root path", not "is a process this seat
  started". The refusal direction is correct: a plain foreign `sleep` →
  `{"killed": false, "reason": "REFUSED foreign pid"}`, still alive. The
  boundary §2.5 premise itself is confirmed: a live private WirePlumber's
  cmdline is `wireplumber -c wireplumber.conf -p main` (no root) while its
  12 401-byte environ carries the root, and the census sees and kills it.
- **Impacted axes.** custody/isolation (a *foreign* reader can be signalled),
  and the report's absolute claim "the kill **refuses** anything else".
- **Smallest safe correction.** keep a module-level set of pids this seat
  spawned (`_wppol_r97_spawn` sees every one) and require membership *in
  addition to* the path predicate. No adopted-process case is lost.

### F5 — report claim falsified: "No `pactl` call of any kind is made by this family" (r97-author.md, Custody).
- **Counterexample.** every entry head calls `_capture_inventory()`
  (`pactl list sources short`, `pactl info`) and `_loopback_r79_oracle()` →
  `_loopback_r79_pactl_defaults()` (`pactl info`) — 3 read-only `pactl` calls ×
  5 entries × every battery run. The receipts carry their output:
  `oracle_at_start.sink_pactl = 'alsa_output.usb-Generic_USB_Audio-00…'`,
  `pactl_exit: 0`. The *intended* claim ("no `pactl` write; `pactl set-default-*`
  never called") is true — grep of the block: zero `pactl` invocations, and no
  `pactl set-default-*` anywhere.
- **Impacted axes.** provenance precision of the report (not the fixture).
- **Smallest safe correction.** reword to "no `pactl` *write*; the only `pactl`
  calls are the inherited read-only inventory/oracle probes".

### F6 — leg census: `d9_lag_s` re-measures a field the d9 record already carries.
- **Evidence.** 45217 `entry["d9_lag_s"] = round(time.monotonic() - lag_t0, 3)`
  is the same expression, same `t0`, as 45202
  `state_file_row_secs` — 1.003/1.003 and 1.002/1.002 in the author runs,
  1.003/1.004 in mine. It adds no observation, so of the disclosed
  **15 defaults legs / 69 total**, one is a re-read (distinct observations: 68).
  The rest of the census is exactly recountable — I reproduced
  **14/15/21/15/4 = 69** from the receipts using the disclosed context-key rule
  in all three runs. Nit: the rule also lists `unloads` and `residual_destroy`,
  which this family never writes.
- **Impacted axes.** leg-census honesty.
- **Smallest safe correction.** drop `d9_lag_s` (keep the field inside d9) or
  redefine it against a different `t0` (e.g. the metadata-row instant); trim the
  two unused names from the rule.

### F7 — dead entries (cosmetic).
`WPPOL_R97_SINK_D` (43865) is defined and never referenced (every other sink
constant is). Unused parameters: `_wppol_r97_spawn(..., root=None)` (44199,
never read), `_wppol_r97_run(..., keep_raw=False)` (never passed),
`_wppol_r97_purge(env, cli, root)` (44515, `cli`/`root` unused).
**Correction.** delete the constant; drop the parameters.

---

## 5. Attacks that did **not** land (verified-clean, so the gate can rely on them)

- **Forgery check against raw artifacts.** For the author's run-1 arming root
  (`tmp/wppol-r97-218888-ffn20zgt`), every scan claim in the receipt is present
  verbatim in the logs still on disk: a3 `Failed to load configuration: Could not
  locate configuration file 'wireplumber.conf'` with **0** fragment lines;
  a4 the copy's conf + copy fragments (`10-r97a-copy.conf`, `alsa-vm.conf`) and
  **no** `/usr/share/wireplumber/wireplumber.conf.d` fragment + `using
  configuration file: wireplumber.conf`; a5 shipped `alsa-vm.conf` + the private
  XDG fragment; a6 shipped + the shim-`$HOME` fragment and **no** operator path;
  a7 both fragments then `Could not locate script 'sm-objects.lua'`;
  a9 `Failed to connect to PipeWire`; `core_stub.log` `no modules loaded from
  context.modules`. No log under any root contains
  `vgpnk/.config/wireplumber` or `vgpnk/.local/state/wireplumber`.
- **State-file claims.** `tmp/wppol-r97-218888-wsxk_mrg/conf/xdg-state/wireplumber/default-nodes`
  is byte-equal to the receipt's d13 row (`default.configured.audio.sink=r97a_sp_218888`);
  run 2's is `r97a_sp_443725`; the linking root holds `r97a_sa_443725` (l18's
  write). The d9 metadata/state duality, d10 clear, d11 fallback and the
  tie/driver ranking legs all re-derive.
- **Residue census (author roots).** exactly **36** roots, **11.1 MB** of files,
  **0** processes — live *or* zombie — naming any author root, **0** author pid
  files pointing at a live non-zombie pid, **0** bound unix sockets. The 20
  battery roots map 1:1 onto 2 runs × 5 entries by mtime, and the 16 dev roots
  match the disclosed dev receipts. Among r97 roots the only live daemons are the
  two batteries running *now* (mine and the verifier's); the other live private
  daemons on the host belong to foreign lanes (§6).
- **Operator-instance state.** `~/.local/state/wireplumber/default-nodes` mtime
  is 06:24 — the **disclosed foreign** shared-daemon restart (06:24:34), not any
  r97 window; the private instance writes only its own `XDG_STATE_HOME`.
- **Shared-graph safety, live.** 0 `r97a` objects in the operator's graph in
  every receipt and in my live re-check (`objects: 139, own_hits: []`) — *while
  two wppol batteries ran concurrently*.
- **Lock.** fixed lane path, `flock(LOCK_EX)` held to exit (`_r97_family_lock`
  bound at 46733), identical in shape to r89/r96 (r95's bounded-wait variant is
  the stricter, newer convention — no r97 regression). Two *different checkouts*
  do not exclude each other (the verifier's tree vs my worktree) — that is the
  inherited r84 design, not an r97 defect.
- **Census predicate, positive case.** a live private WirePlumber (no root in
  cmdline, root in environ) is seen by `_wppol_r97_own_procs` and killed —
  the boundary's §2.5 fix works in the direction it was written for.

---

## 6. Disclosures

- **Contention ledger.** 07:03:15–07:08:37 the **r97 verifier's own**
  `--probe-wppol-r97` battery ran concurrently (pid 788475, launched from
  `audio-shokunin/corpus/live/r97-verifier/tree/`, receipt
  `…T100837483839Z-wppol-r97`) — i.e. two private-instance batteries at once
  through my P0/P3 and surgical probes; from ≈07:15 its run 2 and four
  single-entry mutation probes (settings/wpexec) were live again, after my
  measurement runs had finished. Foreign lanes were also live (r100
  `r100sofa.py` legs, an r91 gstfrz client, and **two orphaned r99 private pairs
  from 06:16** — `pipewire -c …/r99asmoke/conf2/…` + `wireplumber -p main`, still
  alive 52 min later; *not* r97's residue). My runs were made under loadavg 4–9
  on 32 cores; every leg of the full battery still landed green.
- **Provenance.** All my numbers come from (a) the author's two frozen-byte
  receipts + the raw logs/roots they cite, (b) my own runs of the *committed*
  bytes and of five patched copies. The `wppol_r97_block.py` in the author's dev
  dir is not evidence of record and was not used as such.
- **Untracked.** This report is the only file I add to the main checkout; I did
  not commit, stage, or touch any tracked file (`corpus/fixtures/measure_audio.py`
  sha unchanged at `7a070fa8…`).
- **Head moved under the review (not by me).** At 07:14 a sibling lane committed
  `a2c6e3b7` ("r90 adjudicate … + wave-B reports + foldfix contract", 7 files,
  +1633) on top of `b8ff4efc`; it touches **no** fixture byte — HEAD's
  `corpus/fixtures/measure_audio.py` and the working tree are both still exactly
  `b8ff4efc`'s bytes (`7a070fa8…`). The landing under review is unchanged.
- **Cleanup.** My `/tmp` scratch from one over-match probe was removed; all other
  scratch is under `/home` (`critic-r97/`, and my runs' private roots under
  `tmp/wppol-r97-{790688,795233,814646,842689,867816,892396,894886}-*`).
  `critic-r97/wt` remains registered as a git worktree — prune it when the
  archive is no longer wanted.

## 7. Residual uncertainty (what this review does not cover)

1. The C-side flush timeout (`state:save_after_timeout`) is still unverifiable
   from the installed Lua; F3 explains the *recorded* latency, not the flush
   mechanism, and the d12-vs-d9 lag spread (≥1.6 s vs 1.003 s) remains
   unexplained by any receipt I hold.
2. `wpctl status` against a *half-initialised* WirePlumber was not tested (the
   family arms it only with WirePlumber killed) — the author discloses this.
3. `l18`'s movement path (which setting actually moves a live stream on a default
   change) is still unidentified; the family records it unarmed, as directed.
4. My F1/F2/F3/F4 fixes are *proposed*, not applied — this seat does not edit.
   P5/P1/P3/P4 are the probe shapes a fold can reuse to prove the fixes land.
5. Nothing here speaks to the operator's subjective audio goal; the receipt's
   proxies are what they are.

Seat stop. The canonical Rust runtime remains the sole judge.
