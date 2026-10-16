# r100 reviewer — independent final review (advisory, read-only)

**Seat:** reviewer (leaf; no subagents, no live families, no source changes).
**Round / flag:** N=100, FLAG=`sofa-r100`.
**Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c` ("r99 safety: require
explicit opt-in before physical LAN control"; parent `193acbed` r100 integrate).
Worktree HEAD == pin; no tracked modifications in the worktree.
**Scope:** the pinned r100 family (`--probe-sofa-r100` in
`corpus/fixtures/measure_audio.py` 52810–54390 + `corpus/fixtures/r100sofa.py`)
and the pinned r99 LAN-control guard this pin introduces. Advisory findings only;
no round is admitted and no canonical judge verdict is claimed.
**Axes this audit was judged on:** depth, coverage, calibration, operability.

**LSP disclosure:** no `lsp` device exists in this seat's toolset (MCP servers:
`rea` only). Every check below is literal pinned-source inspection
(`git show PIN:path`) plus read-only receipt/file reads. Grep hits are recorded
as literal-text facts, never as semantic proof.

## Commands actually executed

`git show`/`git diff`/`git status` on the pin; full reads of `r100sofa.py`
(1175 lines), the r100 family block, the r99 LAN section and arg builders,
`_rtp_r99_teardown`, main's dispatch and tail, and
`test_rtp_r99_lan_control.py`; JSON reads of the two cited receipts
(`…121334985146Z-sofa-r100`, `…121018453359Z-rtp-r99`); a static mutex-coverage
check over the pinned bytes; sha256 of the pinned vs pre-guard
`measure_audio.py`; and one observed execution of the new static test
`PYTHONDONTWRITEBYTECODE=1 python3 corpus/fixtures/test_rtp_r99_lan_control.py`
→ "Ran 2 tests … OK", rc 0 (AST-only: no audio, no network, no PipeWire, no
writes). Full log: `audio-waveb-resume/r100-reviewer/commands-and-evidence.md`.

---

## Findings, by severity

### F1 — Medium (error path, inferred): the nine r100 entries have no exception containment; one unexpected raise aborts the whole run before any receipt is written and can leak a started private core

- **Where:** every entry calls `tempfile.mkdtemp` and
  `_sofa_r100_sandbox_start` **outside** its `try`
  (`measure_audio.py` pin lines 53525–53534 shape, 53589–53598 azimuth,
  53686–53695 curve, 53741–53750 rate, 53799–53808 control, 53897–53906
  transfer, 54007–54016 inert, 54209–54211 shared; clock has it inside the
  try but see F6). The entries have `try/finally` only — no `except`.
- **Failure path:** e.g. `mkdtemp(dir=SOFA_R100_TMP)` raises `OSError`
  (TMPDIR full/unwritable) → propagates out of `sofa_shape_r100_entry` → out
  of the bare dispatch at 55276–55293 → out of `main` → traceback; the
  receipt write at 55963–55967 is never reached, so **all nine entries'
  measurements are lost**, and entries after the raising one never run.
  Additionally `_sofa_r100_sandbox_start` has unguarded raises after the core
  process is already started — `mkdir` at 53002 and `fh = open(logs/…, "wb")`
  at 53053 — so a raise there returns nothing, never calls
  `_sofa_r100_sandbox_stop(procs)`, and the already-started `pipewire` (and
  later `wireplumber`) child — `start_new_session=True` — **survives the
  crashed parent as a seat-owned daemon**.
- **Contrast (in-repo precedent):** every r99 entry wraps its body in
  `except Exception → coverage_blocked` (52155–52157, 52644–52646) and the
  r93 gate names itself in `failures` so a blocked family exits non-zero
  (55200–55209). The r100 family is the only new family without entry-level
  containment.
- **Smallest correction:** wrap each entry body (or the nine dispatch calls)
  in `except Exception → _sofa_r100_block(...)`; move the `mkdtemp`/
  `sandbox_start` calls inside the `try`; make `_sofa_r100_sandbox_start`
  stop already-started procs on its own late failure paths.
- **Observed or inferred:** inferred (source-proven path; not executed — this
  seat is read-only). No exception occurred in the cited green run.

### F2 — Medium-low (calibration, source-proven): a fully-blocked r100 run still exits rc 0

- **Where:** `main` 55968–55970: `failed = {k: v["failures"] … if
  v["failures"]}`; `return bool(failed)`. `_sofa_r100_block` (53243–53245)
  sets `entry["blocked"]` and `coverage_blocked` but never touches
  `failures`.
- **Failure path:** if the private core cannot come up (missing binary, dead
  core, socket never appears — 53037–53093), all sandbox entries block, the
  shared entry blocks on `pw-dump`, every entry publishes `failures: []` →
  the run prints `"failures": {}` and **returns False → rc 0**.
- **Conflict with the repo's own convention:** the r93 gate comment
  (55200–55203) states "a BLOCKED family must never read as a green battery:
  the gate names itself in failures so the run exits non-zero." The r100
  family's own author report §2 says a missing binary / dead core is "a named
  coverage block, never a silent green" — true in the receipt, false at the
  process-exit level that the verifier recipe and the lead's "raw verification
  return codes" read. (r99 shares the behavior; r93 is the stated precedent.)
- **Smallest correction:** have `_sofa_r100_block` also append a failure line
  (as the r93 gate does), or make `main` count `coverage_blocked` into
  `failed`.
- **Observed or inferred:** source-proven; the cited green run had no blocks,
  so its rc 0 was correct.

### F3 — Low-medium (coverage): the no-config −22 class is not armed, and its constants are dead code

- **Where:** `SOFA_R100_NOCONFIG_ERR/_GRAPH_ERR/_CODE` are defined at
  52920–52922 and referenced nowhere else in the pinned file (literal grep;
  not LSP-verified — no lsp device). The rig supports `--no-config`
  (`r100sofa.py` 1116–1118, 719–720) but no entry plan uses it.
- **Consequence:** the scout's row 2 / boundary's CONF-L row 2 — load OK →
  activation `no config was given` → `can't start graph (-22)` → pure silence
  with frames > 0, the class whose stated gate is "error + zero rms, never
  load rc" — is **unmeasured by the battery**. The author report §3/§4 does
  not claim it (honest omission), but the dead constants indicate a planned
  row that was dropped, and the integration note's "no entry failures or
  coverage blocks" does not distinguish "measured" from "not planned".
- **Smallest correction:** either arm one `no_config` leg (the rig already
  implements it; the laws would be the three pinned log strings + rms 0.0
  with frames > 0) or delete the three dead constants and state the omission
  in the author report.
- **Observed or inferred:** observed (pinned bytes + receipts).

### F4 — Low (provenance): the cited r100 green receipt was produced on pre-guard bytes; the r99 receipt in the same note ran the LAN control for real

- **Facts (observed):** the integration run
  `20261016T121334985146Z-sofa-r100` executed on `measure_audio.py` sha
  `5c8f7e9d…` (= `193acbed`, per `r100-source.sha256` in the frozen
  integration evidence). The review pin's `measure_audio.py` is
  `801e153b…`. The diff `193acbed→bb177513` is confined to the
  `rtp_e2e_r99_entry` region (@@ −52605,34 +52605,42) plus the new test file,
  so the **r100 family bytes are identical** between receipt-source and pin —
  the receipt's family behavior matches the pin — but a byte-level
  source↔receipt chain for `measure_audio.py` does not close at the pin.
- The same note's r99 green (`…121018453359Z-rtp-r99`) records
  `e_lan_control` with `arm_tx_packets 6034`, `fraction_of_emission 1.006`,
  iface `enp7s0` — the positive control **did emit on the physical LAN** in
  that run (pre-repair bytes, opt-in set, as then disclosed). Under the pin
  that leg is blocked by default (verified below), so the r99 receipt is
  stale relative to the pin for exactly that leg. Expected timeline (the
  repair postdates the run), recorded here so the lead reads the two
  receipts against the right bytes.
- **Smallest correction:** none required in code; the lead should annotate
  that the r99 green predates the guard and that a post-repair r99 family run
  does not yet exist (`corpus/live/runs` holds exactly one `rtp-r99` run).
- **Observed or inferred:** observed.

### F5 — Low (verification gap / calibration): the author's key receipts are absent locally, and the surviving stability scratch conflicts with the report's run-1 leg count

- **Observed:** `corpus/live/r100-author/` (RECEIPTS.md, run-{1,2}
  measurements, `stability.txt`, `negative-control.json`, exit-census) does
  **not exist**; `corpus/live/runs/` holds only the integration run. No r100
  `negative-control.json` exists anywhere under `~/Projects/shokunin` (only
  r78/r79 files match). The "ARMING LIVE" demonstration (author §6.3: 21
  failures on perturbed laws) and the two green runs' receipts are therefore
  **not re-verifiable from local evidence** — the claims rest on report text
  and the labrat fold.
- The author's stability sweep survives only as untracked TMPDIR scratch
  `/home/vgpnk/Projects/shokunin/tmp/r100a_stability.txt` (mtime 07:18 local
  = 10:18Z, **before** both cited green stamps 10:30Z/10:37Z), and its
  "shared run A" row shows the armed shared az90 leg is `shared_az90_retry`
  — i.e. that run contained a silent first attempt **and** a retry leg. A
  retry leg is an extra leg key, so if run A is run 1, §5's "Run 1: … 37
  legs" is stale (38). If run A is a pre-fix run, §0.3's "stability.txt, now
  a full sweep of all 37 legs" demonstrates the two green runs is
  misattributed. Local evidence cannot settle which; flagged for the
  scribe/lead rather than adjudicated here.
- **Smallest correction:** restore or re-derive the author receipts into the
  evidence tree (lead-owned), or have the scribe record the absence and the
  stability-file timeline explicitly.
- **Observed or inferred:** observed (filesystem); the 37-vs-38 question is
  unresolved.

### F6 — Low (error path, inferred): the clock entry's residue teardown sits in the try body, not the finally

- **Where:** 54154 `_sofa_r100_teardown(entry, failures, {})` is inside the
  `try` (54101–54154); the `finally` (54155–54158) only `rmtree`s. An
  exception in the variant loop skips the teardown census entirely (and then
  crashes the run per F1). All eight other entries call teardown in their
  `finally`.
- **Smallest correction:** move the teardown call into the `finally`.
- **Observed or inferred:** inferred (source-proven; not executed).

### F7 — Low (fail-open in an already-blocked path, inferred): the wp-alsa law passes vacuously when no wp log exists

- **Where:** 54141–54153: `alsa_lines` sums over `(root/"logs").glob("*-wp.log")`;
  zero logs → `alsa_lines == 0` → no failure. Reachable only when every
  variant failed before the session manager spawned (those variants are
  already coverage-blocked), so it cannot mask a measured run — but the
  "no-hardware premise" would then be unproven while the entry shows no
  failure.
- **Smallest correction:** fail or block when the glob is empty.
- **Observed or inferred:** inferred. In the cited run `wp_alsa_lines` is 0
  with three real variants (measured, not vacuous).

### F8 — Informational (disclosure): the rig's zero-frame retry discards the first attempt's row

- `r100sofa.py` 1149–1158: on a `frames == 0` capture the rig re-runs the leg
  and **overwrites** `row`; only `attempts` records that a retry happened.
  The measure_audio-level shared-entry retry keeps both rows
  (54216–54227), so the two retry policies disclose differently. The
  boundary's "the retry is recorded in the row" is only partially inherited.
- **Smallest correction:** keep the first row under e.g. `attempt_1` when
  retrying.

### F9 — Informational (hygiene / inherited)

- `_sofa_r100_teardown`'s `loads` parameter (53383) is unused; callers pass
  `{}`.
- `_sofa_r100_leg_ok` (53292–53305) does not check `_fixture.rc`. Benign on
  these bytes (the rig exits 2 iff `leg_error`, and rc 1 with a parsed row is
  unreachable because the JSON print is main's last act), but an explicit rc
  check would be cheaper than the argument.
- The clock variants' `server_clock` witness records
  `default.clock.quantum: '4'` (receipt) — a `pw-cli info 0` line-parsing
  quirk at 537–542. Recorded, never armed; the armed clock law is witnessed
  by the `pw-metadata` `settings` rows, which are correct (512/2048/96000).
- The family-lock helper returns `None` on `os.open` failure (52976–52979)
  and the dispatch proceeds unlocked — the identical inherited pattern in
  r99/r82/r95, not an r100 regression; noting it once for the lead.

---

## What the evidence does support (positive verifications)

1. **Failure propagation helper → entry → main is sound on the pinned bytes**
   (the r100-specific duty). `_sofa_r100_fail` appends to
   `entry.setdefault("failures", [])` (53239–53240); all nine entries bind
   `failures = entry.setdefault("failures", [])` (53515, 53588, 53685, 53740,
   53798, 53896, 54006, 54091, 54173 — exactly 9, matching the 9 entry
   functions) so helpers, teardown and the published field share one object;
   `entry["failures"] = failures` at every exit path re-binds the same
   object; `main`'s `failed` map (55968) drives both the printed summary and
   the return code. The §6 clobber class (`entry["failures"] = <fresh local
   list>`) is gone. Source-proven; the negative-control receipt that
   demonstrated it live is absent (F5).
2. **The three RED-run defects the author claims to have fixed are fixed in
   the pin:** analysis-level `frames`/`peak`/`nonzero` reads (53542–53549);
   the `default_sofa_sha256` key (54057–54072 vs rig outputs at
   `r100sofa.py` 1164–1165); the shared-take one-retry + named block
   (54216–54234); the rig retries only `frames == 0`, never `rms == 0`
   (1149–1158).
3. **r99 physical-LAN control cannot run by default (explicit duty) —
   verified, partly by observed execution.** The only non-loopback egress
   path in the r99 family is `e_lan_control` (52608–52636), gated by
   `os.environ.get("RTP_R99_ALLOW_LAN_CONTROL") == "1"` (exact-match; the
   else branch records `measured: False` + a named coverage block). Every
   other multicast site binds `lo` explicitly (52336, 52515–52516; sources
   and taps default `ifname="lo"`; `r99rtp.py` send defaults `--ifname lo`
   with `SO_BINDTODEVICE` + `IP_MULTICAST_IF`); every ungated sink arg
   defaults `dest_ip="127.0.0.1"` unicast (51212). The new static test
   passes on the pinned bytes (2 tests OK, rc 0): values None/""/"0"/"true"
   are refused, exactly one guard exists in `rtp_e2e_r99_entry`, and "1"
   reaches the client-open barrier before any send. Test-scope note: it
   guards only `rtp_e2e_r99_entry`; a future LAN-binding leg in another
   entry would not be caught.
4. **Mutex is complete:** 144 argparse probe flags ↔ 144 mutex members at
   54400, zero missing in either direction (static check on pinned bytes);
   `probe_sofa_r100` and `probe_rtp_r99` both present; >1 → `parser.error`
   rc 2 (54400–54401).
5. **Self-containment:** `r100sofa.py` imports stdlib only — no `pwlib`
   import — and runs from tracked bytes (`SOFA_R100_SRC` =
   `corpus/fixtures/r100sofa.py`, tracked at the pin). Host inputs
   (`/usr/share/libmysofa/…sofa`, `/usr/share/pipewire/*.conf`) are external
   and disclosed.
6. **The cited integration receipt matches the declared shape and the armed
   laws:** 9 sofa entries, 37 legs (2+7+4+5+3+7+4+3+2), `failures {}`,
   `coverage_blocked {}`; az90 fine ILD 4.6084 (rms 0.16278101/0.0957599),
   az270 −4.6084, az0/az180 0.0; `s_unfed` frames 117760 with rms [0.0, 0.0]
   (silence-with-frames, the class that must never be gated on rms==0);
   n_samples 512/558/1024/1115; shared az90 capture sha `7a344c25…` ==
   private az90 sha — the byte-identical cross-witness claim is receipted;
   `law_provenance` present; shared entry records 2 disclosed store rows,
   private entries none.
7. **Claimed safeguards match source:** `r100a_<pid>` namespace everywhere;
   fixed-path lock; name-verified sink unload (fresh table re-read + own
   `sink_name=`, recycled index is a failure) and client-local module unload
   verified against own nodes with a post-unload re-census; never
   `set-default-*` (exactly one pre-existing r78 invocation at 7089, none in
   the family); `RLIMIT_CORE=0` + SIGTERM→SIGKILL process-group escalation;
   env precedence correct (sandbox `PW_ENV` wins over inherited
   `os.environ`; `XDG_STATE_HOME` redirected so law entries never write the
   operator's store).

## Residual risks and explicit checks not run

- **No live family run** (this role is read-only): the pinned family has
  never been executed as a unit at the pin's `measure_audio.py` sha
  (`801e153b…`); the round's verifier single run is the check for that.
- **The author's negative control and two green receipts are absent
  locally** (F5) — the "arming live" demonstration is not re-verifiable
  here; the lead should treat it as author-asserted until restored.
- **No LSP**: all "never referenced"/"only call site" statements are literal
  text facts over the pinned bytes, not semantic proof (dynamic references
  would be missed; none is plausible for the plain module globals involved).
- The stability-file timeline and the run-1 37-vs-38 leg count (F5) are
  unresolved from local evidence.
- r93/r98 families were not reviewed (other seats' rounds); the r99 family
  was reviewed only as far as the LAN-control duty requires.
- The `PwCli.load` var parse (`= @module:`) was not re-verified against
  pw-cli 1.6.8 output beyond the receipted end-to-end unload witnesses.
- Scratch note: pinned bytes were read via `git show PIN:path` into temporary
  `/tmp/pin_*.py` extracts (since removed); no repo file outside my report
  and scratch dir was created or modified, and no service or daemon was
  started, stopped or restarted.

## Artifacts and attribution

- **Report:** `reports/round-100/r100-reviewer.md` (this file; the only
  repo file written by this seat).
- **Scratch:** `audio-waveb-resume/r100-reviewer/commands-and-evidence.md`
  (command log + receipt outputs).
- **Evidence read (not modified):** pinned sources via `git show
  bb177513…`; receipts `corpus/live/runs/20261016T121334985146Z-sofa-r100/`
  and `…121018453359Z-rtp-r99/`; round reports `r100-scout.md`,
  `r100-boundary.md`, `r100-author.md`, `r93-r99-r100-integration.md`;
  frozen integration evidence `/home/vgpnk/Projects/shokunin/audio-resume-integrations/`;
  author scratch `/home/vgpnk/Projects/shokunin/tmp/r100a_stability.txt`.
- All local receipts and the integration evidence are **local-only**; nothing
  here implies they are committed or remotely available.
- Advisory only: these findings are recommendations for the lead; no round is
  admitted, no canonical judge verdict is claimed, and no shipping decision
  is made by this seat.
