# r95 reviewer — the JACK ↔ PipeWire interop family, independently re-run

Seat: **reviewer** (leaf). Lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin`
at **HEAD `021bde86`** (`r89 adjudicate`, parent `ffeb5155` = the r95 author commit;
the r95 work was authored on `wt-r95` tip `2f46b1ed`, whose base `5a632a4f`
predates the r94 merge). Host `plazir27`, reviewer window
**2026-10-16 09:02:04Z → 09:24Z**, loadavg 51–60 falling to 1.8, 1–16 concurrent
`measure_audio.py` batteries from sibling rounds. Python 3.14.7, gcc 16.2.1,
`jackd`/`jack_lsp`/`valgrind` absent, `pw-jack` present, libjack =
`/usr/lib/libjack.so.0.3.1608` sha256 `34bbb09a…`. **Zero commits. Zero tracked
writes. No `pactl set-default-*`.** Scratch: `corpus/live/r95-reviewer/`.

## Verdict

**BLOCKED-ON-HOST for the fresh-green proof; FAIL-wf on the r95 family's own
evidence paths (four actionable defects, two of which fired live in my run).**

Three separate claims have to be kept apart, because this round they do not
agree:

| claim | status |
| --- | --- |
| the merged HEAD **carries the author's exact r95 bytes** | **PROVED** — the 1771-line r95 block is byte-identical (`e143bb05…`) in `wt-r95` and at HEAD; `r95jack.c` identical (`55d4d411…`); my independent rebuild of the committed source reproduces the greens' binary sha (`016a6853…`) |
| the author's **receipts resolve** and their headline numbers re-derive | **PROVED** — 2 greens × 5 entries × 24 legs, `failures {}`, `coverage_blocked` absent, manifest 4/4 OK, archive copies byte-identical to the `runs/` originals, ~40 armed values re-derived exactly |
| the family is **green on the committed HEAD bytes** | **NOT PROVED** — the shared PipeWire instance wedged host-wide at ≈09:02:15Z; my run and an *independent concurrent verifier run* both blocked all five entries. No green run on HEAD bytes exists |
| the family's **block/red discipline is honest** | **PARTLY FALSIFIED** — it blocked honestly on the null-sink load, but recorded a *false red* on the version law for a client that never opened (F4) |

The r95 diff is also **not defect-free on its own evidence paths**: F2 (the
coverage-block path silently drops the per-leg diagnostics) and F4 (a client
that cannot open is judged as a version mismatch) both fired in my receipt and
in the verifier's.

## What was re-run, on which bytes

| step | command (all `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`) | result |
| --- | --- | --- |
| pre-state | recorded before any run | HEAD `021bde86`; fixture `dca4dc9b…`; pyc `6e271a2d…`; gcc `/usr/bin/gcc`; libjack `34bbb09a…`; `measure_audio.py` processes **15** |
| battery #1 | `python3 corpus/fixtures/measure_audio.py --probe-jack-r95` | **rc 1**; `corpus/live/runs/20261016T090602831047Z-jack-r95/measurements.json`; all 5 entries **blocked** + `a_avail` red (see F4) |
| battery #2 | `corpus/live/r95-reviewer/r95r-wait-run.sh` — waits (bounded, 12 s probe / 15 s backoff) for a responsive daemon, then runs the same command | **never fired**: 36 tries 09:07:30Z→09:23:16Z, every one `pactl_rc=124` (`r95r-window.log`); killed at 09:23Z to keep the run bounded — a third battery against a wedged daemon would only add a third identical block |
| rebuild | `gcc -O1 -w -o r95rjack r95jack.c -ljack -lm` from `git show HEAD:corpus/fixtures/r95jack.c` | binary sha `016a685372e6d8fab9dbd54bdb28b97e948688c2d990bf896feaf26bf9fd7ecf` = the greens' recorded `binary_sha256` prefix `016a685372e6d8fa` |
| native client | `./r95rjack info 0.2` (own build, direct, bypasses `pactl`) | **hangs past the 20 s bound** — the wedge is not a `pactl`-only artifact |

Battery #1's receipt is archived at
`corpus/live/r95-reviewer/run1-saturated/measurements.json`; the CLI log, the
rc, the pre-state and the provenance file are alongside it.

## The host incident (why there is no green run on HEAD)

At 09:02:04Z the host already had 15 concurrent `measure_audio.py` batteries
(r90 `wpstate`, r91 `gstfrz`, r92, r94 `sox` ×2, r96 dev, …). Within ~10 s of my
battery starting — i.e. **before the r95 family had loaded a single object or
opened a single client** — the first leg failed to open a JACK client. Measured
afterwards, on the same host:

- `pactl info` → `Connection failure: Timeout` (rc 1 at its own 30 s bound);
  `pactl list sinks short` never returned; `timeout 60 pactl info` rc 1.
- `pw-cli info 0` and `pw-cli ls Node` hang past 30 s; six `pw-dump` processes
  from *other* seats sat 3–11 minutes in `S` state; the shared
  `/usr/bin/pipewire` (pid 2060) is idle in `do_epoll_wait` (3:09 CPU over
  16.5 h) — it accepts connections and never completes the registry.
- A direct `./r95rjack info 0.2` (my build of the committed fixture, native
  libjack → PipeWire, no `pactl`) hangs past 20 s.
- `org.pulseaudio.Server` is still owned by the shared `pipewire-pulse`
  (pid 2694, `:1.66`) — **no sibling hijack**, contrary to the first suspicion;
  the journal shows r96/r97 private instances *losing* that name race
  (`D-Bus name org.pulseaudio.Server already taken`, 06:09:31).
- An **orphaned `pw-cli` (pid 3332803)** — parent already `systemd --user`, i.e.
  some seat launched it unbounded and its launcher exited — has been in `R`
  state at **92 % CPU for 3+ minutes**, stdin on a dead pipe. Not mine (my
  `pw-cli`/`pw-dump` calls are all `timeout`-bounded); reported, not killed.
- **The wedge is independent of load.** When the sibling batteries drained
  (09:17–09:19Z) the host fell to loadavg **1.78–2.96** with 1–6 probe
  processes — and `pactl info` still returned `Connection failure: Timeout` at
  its own 30 s bound, and a direct native client open still hung. Re-checked at
  09:24Z (load 6.33): `pactl info` rc 1 at **30032 ms**, exactly the client's
  internal timeout. Nothing about this is contention-shaped; the shared
  PipeWire/`pipewire-pulse` instance is stuck and does not self-heal.
- **The JACK client survives SIGTERM** while wedged (`timeout 12 ./r95rjack info`
  had to be SIGKILLed by hand). The harness is unaffected — `_jack_r95_run`
  escalates to SIGKILL at the bound (`measure_audio.py:33449`) — but it means any
  *manual* bound that relies on SIGTERM will not hold on this host.

**Corroboration (this is the part that makes it the host, not my invocation):**
a *verifier* seat ran the same family concurrently from its own tree
(`corpus/live/r95-verifier/tree`, pid 3231401, started 09:02:28Z) and produced
an **identical signature** — all five entries blocked on
`probe null sink r95a_ns_3231401 never enumerated`, plus the same two
`a_avail` version failures. Two independent pids, two independent trees, same
window, same block. The receipts are at
`corpus/live/r95-verifier/tree/corpus/live/runs/20261016T090614906048Z-jack-r95/`.

Attribution therefore: **environment, not r95**. What the r95 family *did*
under that environment is the honest thing — it refused a silent green and
named the block — with the one exception in F4.

## Merge / provenance checks (the "green-run shas vs committed bytes" question)

- The author's green-run implementation sha `164a9158…` is the **branch blob**
  `wt-r95:corpus/fixtures/measure_audio.py`; the lane **HEAD** blob is
  `dca4dc9b…`. `git diff wt-r95:… HEAD:…` = `+2370 / −29`, and every hunk is
  *outside* the family: the r89 foldfix (`_pwprof_r89_sigreset`, x_foot/x_top)
  and the r94 sox block. The 29 deletions are the r89/r94 splices of the
  shared `mode` / `suffix` / mutex lines.
- **The r95 block is byte-identical in both**: lines 30982→32752 of the branch
  blob and 33289→35059 of the HEAD blob are the same 1771 lines, sha
  `e143bb05627c05afb8459ac1cff570efe6b93d468c02cceef0f13609a97ea07d`
  (verified by extraction + `sha256sum`, not by grep). `r95jack.c` is
  identical (`55d4d411…`) at both refs.
- **The merge is clean and the artifact is reproducible from HEAD**: no conflict
  markers; my independent gcc build of HEAD's `r95jack.c` reproduces the exact
  binary the greens ran (`016a685372e6d8fa…`), and the HEAD blob parses,
  dispatches (`mode = probe-jack-r95`) and executes all five entries — my run
  reached every entry and only failed on the daemon.
- Author receipts resolve: both parse; `mode = probe-jack-r95`; 22 entries (5
  r95) × 24 legs; `failures {}`; `coverage_blocked` **absent** in all ten r95
  entries (in this harness the key is only created when a block occurs, so
  "empty" is the correct reading); `sha256sum -c manifest.sha256` **4/4 OK**;
  the archive copies in `r95-author/receipts/` are **byte-identical** to the two
  `runs/` originals (2/2 MATCH); the two CLI logs carry `failures: {}` and
  receipt paths under the **wt-r95 worktree**, exactly as the report states.
  The two dev runs behave as `RECEIPTS.md` claims: `…085246…` red
  (`jack_surface_r95_probe` only), `…085334…` green.
- Teardown witnesses hold in all five entries of both greens: `own_nodes_after
  []`, `stream_properties_own_rows []`, `residual_destroy` absent, unloads
  name-verified (`verified_index == captured`, `recycled false`, `exit_code 0`,
  `field sink_name`), `sinks_gone` true where a sink was still loaded at
  teardown. `libjack_sha256` in the receipt (`34bbb09a…`) equals the live
  library on this host.

### Headline numbers re-derived from the author's greens (not read from the prose)

Recomputed from `receipts/green{1,2}-measurements.json` only, and matching the
report: 168 exported `jack_*` symbols with the declared absent/present classes;
`version "3.1.6.8 (using PipeWire 1.6.8)"`, `version_ints [3,1,6,8]`; port flags
`2 / 1 / 6 / 18` and `outm = 2`; `group.dsp.0` / `Duplex` / `DSP` /
`always-process`, no `media.class`; `port.alias`/`object.path` on all five ports
with `port.physical` only on `outp` and `port.terminal` only on `outt`; monitor
`0 / 1 / 0` and `links []`; driver `Dummy-Driver` `priority.driver 200000`;
`ns` alias `<description>:playback_MONO` vs `object.path <name>:playback_0`;
`cb = 85` in both; `x_native dst_found false / connect_rc 22` vs
`x_rendered`/`x_fillalias`/`x_corner` `rc 0` (fill-aliases resolves the alias
but the connection list reports the canonical rendered name);
`b_jack2pw` peak `0.5`, rms `0.34732 / 0.32404`, frames `88064 / 102400`,
sha `5dc9f062… / be178a25…`, mag² ratio `0.9534 / 0.9541`;
`b_pw2jack` `in_peak 0.499969482` both, `in_nonzero 53245` both, mag² ratio
`0.9999812142687` both (recomputed from `goertzel_mag2 / (0.25·in_nonzero)²`);
`q_default` read-back unchanged + `activated 2048` + prop `"2048"` + settings
`"0"`; `q_live` `bufsize_cbs 1 → bufsize_cbs_after 2`, `last_bufsize_cb_after
512`; `q_cross` second client `bufsize_active 2048`; `q_env`/`q_wrapper`
`512/48000`; `q_env_rate` `srate 44100` with `clock.rate` restored to `48000`;
`q_bufsize1` prop `"1"` + effective `4` + settings `"0"`; `q_global` metadata
`512` during **and after** exit, second client `512`, reset `"0"`,
`settings_moved []`; `d_xrun_stall` `stall_cycles 8 / cb 36 / xrun_cbs 1 /
delayed 0.0`; poison `0xaaaaaaa0` / `0xbbbbbbb0` × 3 (masked) against a
baseline that is garbage in both runs (`77/82` then `-1359737185`, `-1`);
latency `[0,0]/[0,0]` → `[100,200]/[10,20] total 150`, input stays `[0,0]`;
transport `0 → 0 → 1 → 0` with the frame advancing `0 → 23552 / 0 → 22528`,
frozen across `locate`/`reposition`, `out_connected 1`; metadata `own_desc_count
2`, missing `-1`, live row `r95a/key1` subject `204` == the node's registry id
in **both** runs, rows gone after exit.

## Findings

### F1 — MEDIUM (code): the metadata witness namespace is not seat-scoped, so a concurrent r95 run can force a false red in `d_metadata`

`corpus/fixtures/r95jack.c:672-716` writes and reads the **literal** keys
`r95a/key1` and `r95a/portkey` — no pid — while every node, client and sink in
the family is `r95a_<pid>`. `_jack_r95_meta_rows`
(`measure_audio.py:33652`) then collapses the store into `rows[key] = {subject,
value}`, **keyed by key alone**, discarding the subject dimension; the `default`
store can hold both seats' rows simultaneously. The arms at
`measure_audio.py:35034` (`rows["r95a/key1"].value == "value1"`), `:35041`
(`subj == mid["node_id"]`) and `:35048` (`rows_after_exit`, which filters on the
`r95a/` prefix only) therefore read a sibling's row when a sibling is live.

Evidence that this is reachable, not theoretical: an independent seat ran the
same family **concurrently with my battery** in this window (verifier pid
3231401, same host, different tree — see F6). The author's greens cannot falsify
this, because they were run alone. Fix: put the pid in the key
(`r95a_<pid>/key1`) or filter the parsed rows by the subject id.

### F2 — MEDIUM (code, fired live): the coverage-block path drops `entry["legs"]`, destroying the evidence that justifies the block

`_jack_r95_block` (`measure_audio.py:33914`) sets `blocked`, appends
`coverage_blocked`, unloads what it is handed and sets `entry["failures"]` — but
never `entry["legs"] = legs`, and no caller passes the local `legs`
(`:33975`, `:33983`, `:34040`, `:34243`, …). The exception path does keep them
(`:34219`, `:34331`, `:34575`, `:34840`, `:35056`), so the omission is specific
to the block path.

Fired in both runs: my receipt and the verifier's have **no `legs` key at all**
in any of the five entries, while `jack_surface_r95_probe` had already executed
`a_avail` end-to-end — its two failures are in the receipt, but the leg record
that explains them (the version probe's `exit_code`, `stdout`, `stderr`,
`error_class`) is gone. The comment at `:34216` ("never lose the receipt") is
honoured for `failures` and not for `legs`, on exactly the path that most needs
diagnosis.

### F3 — MEDIUM (code, latent): the `except Exception` paths skip `_jack_r95_teardown`

All five entries append a coverage block and return without unloading `loads`
or running the residue sweep / `sinks_gone` / `own_nodes_after` /
`stream-properties` witnesses (`:34216`, `:34328`, `:34572`, `:34837`,
`:35053`). `_jack_r95_block` at least unloads the sinks it is handed
(`:33928-33934`, returning at `:33936`). Consequence: an unexpected exception
raised after
`_jack_r95_load_ns` succeeds leaves a `r95a_<pid>` null sink (and any live
child) on a **shared** host with no census recording it — the very residue the
teardown was built to refuse.

### F4 — MEDIUM (code + honesty, fired live): a JACK client that never opened is judged as a version-law failure instead of a coverage block

`a_avail` arms `version_ints == [3,1,6,8]` and the `"PipeWire 1.6.8"` substring
directly from the parsed JSON (`measure_audio.py:34016`, `:34018`) without first
requiring `version_probe.exit_code == 0` / a non-null JSON. When the daemon
refuses or stalls the client open, `vj` is `{}` and the receipt says:

```
a_avail: version_ints = None, want [3, 1, 6, 8]
a_avail: version = None — the PW-backed version string fails
```

which reads as *the version-pinned premise failed*. It did not: the host was
unavailable. Both my run and the verifier's produced exactly these two lines
and exited **1 (red)**, not "blocked". Every other availability fact in this
family is blocked rather than judged (null sink, driver confound, tools,
compiler); this one leg breaks the family's own discipline. Fix: block on a
failed/absent open, judge the version only on a successful one.

### F5 — MEDIUM (host hygiene): the only restore of the host-global `clock.force-quantum` is the fixture client itself

`q_global` (`measure_audio.py:34780`) writes `settings clock.force-quantum=512`
via `jack.global-buffer-size=true`, and the restore is a second *client*
(`q_global_reset`, `:34813`) that calls `jack_set_buffer_size(1)`. There is no
harness-side restore in the teardown and none in the `except` path
(`:34837`). If that reset client is killed at the bound, or an exception lands
between the two legs, the shared host is left at a forced 512-sample quantum for
every other seat; the receipt reds (`"metadata restored"` at `:34823`) but
nothing repairs it. The greens show the arm works when it completes
(`settings_moved []`, final `"0"`, `clock.rate 48000`) — the risk is the failure
path, which the family otherwise treats with care. Mitigation: an unconditional
`pw-metadata -n settings 0 clock.force-quantum 0` in teardown, fired only if the
arm moved the key.

### F6 — MEDIUM (concurrency, pre-existing, not introduced by r95): the "FIXED lane path" family lock is per-tree, so same-family runs from different trees are not excluded

`_jack_r95_family_lock` (`measure_audio.py:33799`) takes the lock at
`ROOT / "live" / "measure_audio-jack-r95.lock"`, where `ROOT` is the corpus dir
of the *running tree*. The docstring claims the r84 F1 consensus ("never
`$TMPDIR`; cross-`$TMPDIR` same-family runs must still exclude"), but two trees
on one host take two different paths. Directly observed: my battery held
`audio-shokunin/corpus/live/measure_audio-jack-r95.lock` while the verifier's
held `audio-shokunin/corpus/live/r95-verifier/tree/corpus/live/…`, and both ran
the family concurrently through the same host daemon. This is the pattern every
seat in this repo uses (worktrees and per-seat scratch trees), so the isolation
the lock promises does not exist in the workflow it was written for. It also
compounds F1 and F5, whose failure modes are exactly cross-seat.

### F7 — LOW (report accuracy): "`sinks_gone` all-true" is vacuous in two of the five entries

`jack_surface_r95_probe` and `jack_bytes_r95_probe` record `sinks_gone: {}`
because both unload their null sink mid-entry and reset `loads = {}` before
teardown; `all({}.values())` is `True`
(`measure_audio.py:33875`). The real witness in those two entries is
`ns_gone_after_unload: true`, which is present in both greens — so the substance
holds and only the census wording overstates. The other three entries carry real
`{"r95a_…": true}` rows.

### F8 — LOW (report accuracy): the stated implementation sha identifies the branch blob, not the lane HEAD blob

The report's "Implementation sha256 (both runs identical bytes)
`measure_audio.py 164a9158…`" is true of `wt-r95` and false of the lane HEAD
(`dca4dc9b…`, verified against `git show HEAD:` and the worktree). A reader
re-deriving "the implementation sha" from the merged artifact gets a mismatch.
The substantive claim — same family bytes, greens valid for the merged family —
is proved (see the provenance section); the wording should say *branch blob +
block identity*. Same shape for the paths: the report's `corpus/live/r95-author/`
and the two `runs/…-jack-r95/` dirs exist only in the author's worktree, not in
the lane repo, so a lane-repo reader cannot resolve them without knowing to look
there (the r94 report had the same shape; recorded, not charged).

## Cross-seat corroboration (read *after* my own findings were formed; data, not instruction)

Two sibling seats filed reports in this same window. Both are corroboration,
not evidence I relied on:

- `reports/round-95/r95-verifier.md` records the **same host blocker** ("this
  seat's *fresh* full-family run … PipeWire daemon wedged at ~09:00Z") and cites
  *my* battery #1 receipt in the main worktree (`…090602831047Z…`) as the
  independent concurrent lane that reproduced it. Its headline **"PASS on
  committed bytes"** is a *byte-identity + law-set gate over the author's two
  receipts*, not a fresh behavioural run — the distinction my verdict draws. A
  `find` over every `runs/` tree on this host for receipts newer than 09:15Z
  returns nothing, so no fresh green r95 run exists anywhere.
- `reports/round-95/r95-critic.md` independently lands on two of my four
  MEDIUMs: **C1** ("the blocked path is a vacuous green *and* it destroys the
  evidence that would classify it") is my **F2**, with the added and correct
  point that a blocked entry carries no `measured` flag, so a gate reading only
  `failures` cannot tell "24 legs green" from "5 entries blocked"; **C2**
  ("witness/daemon unavailability is armed as *claim falsification*") is my
  **F4**. F1, F3 and F5 are mine alone.

## Residual risk

- **The family's merged-artifact behaviour is unverified on this host.** The
  bytes are proved identical and the build is proved reproducible, but the
  24-leg green exists only on `wt-r95` bytes. If the r94/r89 merge context
  mattered anywhere, it would be outside the block — and nothing in my run
  suggests it does (the family dispatched and executed; only the daemon failed).
- **F1/F5 are concurrency-shaped**, and this repo's workflow runs same-family
  seats concurrently as a matter of course (F6). A future green here should be
  taken on a host where no sibling holds the same family.
- **The greens' `d_rtprio_poison` claim rests on the in-fixture control**; this
  host has no `valgrind`. Unchanged from the boundary, recorded not hidden.
- **The r95 family can be re-verified green only when the shared daemon
  answers.** Until then, any r95 receipt on this host is a block, and the
  family's own F4 turns that block into a red line.

## Verification gaps

- **No green run on HEAD bytes** — blocked by the host incident described above.
  Battery #1 ran and blocked; battery #2 waited 36 bounded probes over 16 minutes
  and never found a responsive daemon, so the family's 24 legs were **never
  executed on HEAD bytes** in this window. The only HEAD-byte evidence is
  structural (block identity, reproducible build, clean dispatch and honest
  block), not behavioural.
- **"never `pactl set-default-*`" is not independently provable from
  artifacts** — I did not issue it, and the author's `exit-census.json` shows the
  default sink/source unchanged and no `r95a` residue, but a seat's *non*-actions
  leave no trace. Recorded as an absence-of-evidence gap, not a defect.
- **No live evidence for the host-global quantum claims** (`q_env_rate`,
  `q_global*`) in my own window; they are verified only against the author's
  receipts (values re-derived, not re-measured).
- **The verifier's concurrent receipt is cited as corroboration of the block,
  not as independent evidence of green** — it carries the same F4 red and no
  legs, and it is another seat's artifact, not mine.
- **F6's cross-tree lock gap was observed, not measured to a conclusion**: I did
  not attempt to provoke a cross-seat quantum collision (that would have
  required a second battery against a wedged daemon).

*Leaf seat — reviewed, re-ran, and re-derived; not judged. No verdict here is an
admission, and no file outside `reports/round-95/r95-reviewer.md` was written.*
