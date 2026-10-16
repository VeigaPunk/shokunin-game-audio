# r95 critic — the JACK↔PipeWire landing, attacked

Seat: **CRITIC (leaf)**. Host `plazir27`, window **2026-10-16 06:00–06:13 local
(09:00–09:13Z)**. Lane repo `~/Projects/shokunin/audio-shokunin` @ **HEAD `ffeb5155`**
(the lane has since advanced to `021bde86 r89 adjudicate` — an adjudication commit;
`ffeb5155` is the artifact under review and both commits carry the same
`corpus/fixtures/measure_audio.py` blob `cfd8e210…`). **Zero tracked writes, zero commits**
(`git status --porcelain` shows no modified tracked path). Object namespace **`r95c_*`**;
TMPDIR `~/Projects/shokunin/tmp`; bounded children with own session + SIGKILL at the bound;
**no `pactl set-default-*` was ever issued**; the only daemon objects this seat could have
created are disclosed in §5.

Artifact copy: `corpus/live/r95-critic/tree/` (`git archive ffeb5155`).
Own harness: `~/Projects/shokunin/tmp/r95c/` (`r95c_indep.py`, `r95c_version.c`,
`r95cjack`, `r95c_version`).

---

## 1. What I attacked, and what survived

| # | attack on the landing | result |
| --- | --- | --- |
| A1 | **Is the r95 block really byte-identical to the author's worktree bytes?** | **SURVIVED (verified).** Landed `measure_audio.py` `dca4dc9b…` vs author worktree `164a9158…`; the extracted block (from the `# r95:` header to the line before `def main()`) is **sha256 `5c61097200ee88787f037bcf93da4c3159bae474f95ed7e481d18f630e094627`, 85759 B, 1771 lines** in *both* files — byte-identical. Landed block span: lines **33289–35058**; `def main()` at 35059. |
| A2 | **Are the splices exactly the author's intent (nothing dropped/duplicated)?** | **SURVIVED.** The commit's **only** deletions are the 3 shared lines the author names: the mutex `sum([...])` list, the `mode` chain, the `suffix` chain. Exactly **1** `--probe-jack-r95` argparse line (35191), **1** `probe_jack_r95` term in the sum list, **1** `if args.probe_jack_r95:` dispatch (35663) holding `_r95_family_lock` to exit, **1** mode term, **1** suffix term; **5** entry defs; **4** occurrences of the dest name + the argparse line = the 5 wiring points. |
| A3 | **Is the "24 legs" headline real?** | **SURVIVED.** Receipt leg keys are exactly 3+4+2+10+5 = **24** (`a_avail, s_shape, s_liveness` / `x_rendered, x_native, x_fillalias, x_corner` / `b_jack2pw, b_pw2jack` / `q_default, q_live, q_cross, q_env, q_wrapper, q_env_rate, q_bufsize1, q_global, q_global_second, q_global_reset` / `d_xrun_stall, d_rtprio_poison, d_latency, d_transport, d_metadata`). No phantom legs, no unarmed legs. |
| A4 | **Is the fixture build record genuine (false-provenance check)?** | **SURVIVED.** I rebuilt the frozen `corpus/fixtures/r95jack.c` (`55d4d411…`, identical in worktree and landed) with an own gcc line (`gcc -O1 -w -o … -ljack -lm`): the binary sha256 prefix is **`016a685372e6d8fa`**, exactly the `build.binary_sha256` recorded in the author's green receipts. The build is reproducible from the frozen source. |
| A5 | **Do the a_avail symbol/version premises re-derive independently?** | **SURVIVED.** `nm -D --defined-only /usr/lib/libjack.so.0.3.1608` → **168 `T jack_*`**; all 7 absent-class symbols absent, all 8 present-class symbols present; libjack sha `34bbb09aceb7de3a`. Version, re-derived **offline with no daemon** by an own 12-line program: `"3.1.6.8 (using PipeWire 1.6.8)"`, `version_ints [3,1,6,8]`. |
| A6 | **Does the landed file's extra content (r89 foldfix + r94 block) contaminate the r95 family's path?** | **SURVIVED.** The worktree→landed delta touches only `pwtop_r88_entry`, the r89 foldfix helpers/entries, the r94 block and `main`; the intersection with the inherited helpers the r95 block actually calls (`_alsapw_r84_killpg/_loadavg`, `_capture_r77_sha256/_sink_names_strict`, `_pactlmon_r85_unload_own`, `_playback_r78_*`, `_pwcat_r83_ns_load`, `_pwprof_r89_errclass/_norm`) is **empty**. So the author's green evidence transfers to the landed bytes modulo the shared host. |
| A7 | **Does the landing modify any prior ledger row?** | **SURVIVED.** Commit touches 3 files only (`measure_audio.py`, `r95jack.c`, `r95-author.md`); all 3 deletions are the splice lines above. |

**The landing is exactly the author's intent.** Nothing below is an integration defect.

---

## 2. Findings (counterexamples the round must not ignore)

### C1 — the blocked path is a vacuous green **and** it destroys the evidence that would classify it

**Counterexample (live, two independent seats).** In this window the r95-reviewer and
r95-verifier seats each executed the **frozen landed bytes** in independent trees. Both
receipts are identical in shape:

- `corpus/live/runs/20261016T090602831047Z-jack-r95/measurements.json` (reviewer, `rc=1`,
  `corpus/live/r95-reviewer/r95r-rc.txt`)
- `corpus/live/r95-verifier/tree/corpus/live/runs/20261016T090614906048Z-jack-r95/measurements.json`

| entry | failures | coverage_blocked |
| --- | --- | --- |
| `jack_surface_r95_probe` | 2 (`a_avail: version_ints = None`, `version = None`) | `probe null sink r95a_ns_<pid> never enumerated` |
| `jack_addr_r95_probe` | **`[]`** | same |
| `jack_bytes_r95_probe` | **`[]`** | same |
| `jack_quantum_r95_probe` | **`[]`** | same |
| `jack_defects_r95_probe` | **`[]`** | same |

Four of five entries report **`failures: {}` while measuring nothing at all**: each blocked
at its first act (`_jack_r95_load_ns` → `pactl load-module` never enumerated). The only
thing that keeps the run from reading as "green x2, re-verified" is the `a_avail` version
arm, and that arm reds for a host reason (C2), not a library reason. So the fixture's own
`failures` summary — the field a gate reads — cannot distinguish *"24 legs measured green"*
from *"0 legs measured"*. The author's own green criterion (`coverage_blocked` empty) is the
only discriminator, and the artifact does not enforce it.

**Worse — the block path drops the partial evidence.** `_jack_r95_block`
(`measure_audio.py:33914–33936`) sets `entry["failures"]` and `coverage_blocked` but **never
`entry["legs"]`**; the normal path sets it (34213–34214) and the `except` path sets it too
(34217–34219). Consequence, verified in both sibling receipts: the surface entry has keys
`['blocked','build','contention','coverage_blocked','failures','foreign_*','loadavg','probe',
'settings_at_start','tools','unloads']` — **no `legs`**. The `a_avail` records (including
`version_probe.killed_at_bound`) are gone, so the receipt asserts *"the version premise
failed"* where the truth is *"the probe never opened"*.

**Worse still — the block path skips the exit census.** `sinks_gone`, `own_nodes_after`,
`stream_properties_own_rows` are absent from every blocked entry (they are present in the
author's green receipts). A family whose stated convention is *"name-verified teardown …
final `sinks_gone` / `own_nodes_after` census armed"* runs **no census at all** on the one
path where residue is most likely (`module_id is None` ⇒ the load may have succeeded with
its response lost ⇒ nothing to unload).

*Smallest safe correction:* in `_jack_r95_block`, carry `entry["legs"] = legs` (and the
already-computed head records), run the same residue census as `_jack_r95_teardown`, and
record `entry["measured"] = False`; the round's gate must require `coverage_blocked == []`
before reading `failures`. (Precedent in-flight: the r96 seat is wiring exactly this class of
entry-level gate in this same window — `_pulsecli_r96_server_gate`, bounded `pactl info`,
"an unresponsive daemon is a NAMED entry-level coverage block, never a red and never a
green".)

### C2 — witness/daemon unavailability is armed as *claim falsification* (false red)

**Counterexample.** Both sibling runs red on `a_avail`:
`version_ints = None, want [3, 1, 6, 8]` and `version = None`. The mechanism is host
condition, not library behaviour:

- `_jack_r95_probe(probe, ["info","0.2"], 10.0)` (33996–33998) hangs inside
  `jack_client_open` while the daemon is stalled → the harness SIGKILLs at the bound →
  stdout empty → `_jack_r95_json` returns `None` → `vj = {}` → `version_ints` is `None`.
- The version premise itself is **true**: I re-derived it offline with no daemon
  (`r95c_version`: `"3.1.6.8 (using PipeWire 1.6.8)"`, `[3,1,6,8]`).
- The fixture's `open_client` (`r95jack.c:139–153`) has **no timeout of its own**, and
  `main` installs `signal(SIGTERM, on_sig)` handlers that only set `g_stop`
  (`r95jack.c:258`): a client blocked in the open is **uninterruptible by SIGTERM**. I
  reproduced this with my own build — two `r95cjack shape` processes stayed in
  `futex_do_wait` for 5:29 and 3:04 under `timeout 12` (SIGTERM) and only died on SIGKILL.
- The err-class table has `jack_r95_no_daemon` (`Could not connect to JACK server`,
  33372), but it **never fires in this state** — the client hangs instead of printing.

So the family converts a stalled daemon into a red for a claim that is not false. The
asymmetry is explicit in the author's own convention: *"a missing compiler / header / libjack
/ tool is a named coverage block, never a silent green"* — a missing **daemon** is not.

**The same hole fired in the author's own dev run and is still in the landed bytes.**
Author run `20261016T085246666582Z-jack-r95` (worktree tree) has **29 failures**, all of the
form `s_shape: client.api = None, want 'jack'` … `s_shape: links while running = None, want
[]`, i.e. every arm fed by the concurrent witness (`_jack_r95_shape_slice`,
33687–33703) firing because the `pw-dump` snapshot was unreadable. `_jack_r95_shape_slice`
has **no error field**, and `_jack_r95_entry_head` (33818–33833) **discards `g["error"]`**
from `_jack_r95_graph` (33551; the bounded `pw-dump` at 33558, `timeout=20`). The witness's own failure is therefore invisible: the
receipt claims 29 falsified laws where the witness was unavailable. (The author's later
greens are the same bytes with a readable graph.)

*Smallest safe correction:* treat a probe killed at the open bound and an unreadable graph
snapshot as **named coverage blocks** (a `jack_r95_open_timeout` class in
`_JACK_R95_ERR_CLASSES`, plus an `error` field on the slice/entry-head), never as arm
failures. Bounded `pactl info` / graph-readability gate at entry (as above) removes the
whole class.

### C3 — the family lock is **tree-local**, not family-global: two seats ran the family concurrently

**Counterexample (live, this window).** `_jack_r95_family_lock` (33799–33815) derives the
lock path from `ROOT` = `Path(__file__).resolve().parents[1]`, i.e. *the tree the file is
executed from*:

- reviewer (lane tree): fd 3 → `…/audio-shokunin/corpus/live/measure_audio-jack-r95.lock`,
  holder `pid=3228981 ns=r95a_ns_3228981`
- verifier (archived tree): fd 3 → `…/r95-verifier/tree/corpus/live/measure_audio-jack-r95.lock`,
  holder `pid=3231401 ns=r95a_ns_3231401`

Two *different* lock files, **held simultaneously**, both running `--probe-jack-r95`
(06:02–06:06Z). The r84 F1 3-seat consensus the author invokes is *"a FIXED lane path under
corpus/live/ — never `$TMPDIR`; cross-TMPDIR same-family runs must still exclude"*; the
implementation excludes only runs from the **same tree**. The `git archive`/tree-copy
convention that every seat in this round uses (I used it myself, §4) defeats it by
construction. This matters because the r95 family is the first to write **host-global**
state: `q_global*` writes `settings clock.force-quantum` and asserts the exact value during
(34800), after the writer exits (34803), and after the reset (34824), with `settings_moved`
diffing the whole store (34829). Two concurrent same-family runs can
therefore produce both a false red and a masked green on the same key — the author's
disclosure ("a sibling seat writing the same key inside the arm window would surface as a
real red with the value in the receipt") is honest but the lock was supposed to make it
impossible, and it cannot.

*Smallest safe correction:* anchor the family lock to a host-global, tree-independent path
(e.g. `${XDG_RUNTIME_DIR:-/run/user/$UID}/ufo-measure_audio-jack-r95.lock`, or
`~/.local/state/…`), and key it by family only. This is a repo-convention fix (r86–r89 share
the defect) — flag it for the fold rather than patching r95 alone.

### C4 — the lock wait is unbounded (contradicts the lane's "every child is bounded" guard)

`fcntl.flock(fd, fcntl.LOCK_EX)` (33808) is a **blocking** acquire with no timeout, no
`LOCK_NB` retry cap, no coverage block and no error class; the docstring says a second run
"waits HERE". A second same-tree run therefore hangs indefinitely. I could not exhibit a live
blocked waiter (the two seats used different lock files, C3), but the path is unconditional.
*Smallest safe correction:* `LOCK_NB` + bounded retry (e.g. 600 s) → named coverage block
`jack_r95_family_lock_busy`.

### C5 — the lock file is not self-cleaning and reads as a live holder

`corpus/live/measure_audio-jack-r95.lock` still contains `pid=3228981 …` long after that
process exited (verified: `ps` shows no such pid; `flock -n` then succeeds). Any seat that
reads the file instead of probing the lock sees a stale "holder". Minor, but it is exactly
the kind of stale-state artifact this lane treats as a defect class. *Correction:* truncate
on release (or have readers `flock -n`-probe rather than `cat`).

### C6 — report arithmetic drifts off the landed artifact (twice)

- The report's **`measure_audio.py` — +1805 / −3** is the *worktree* delta
  (`git -C wt-r95 diff --numstat 5a632a4f` → `1805 3`). The **landed commit's** delta is
  **+1809 / −3** (`git diff --numstat ffeb5155^ ffeb5155`). The 4 extra lines are pure
  whitespace: 2 blank lines inserted before the `# r95:` header and 2 after the r95 dispatch
  block (worktree has 2 / 0, landed has 4 / 2). Block bytes unaffected (A1).
- The report's **"`corpus/fixtures/r95jack.c` — new, 764 lines"** vs the artifact's **778**
  lines (`wc -l`, identical in worktree and landed; the commit's numstat is `778 0`).

Neither is an artifact defect, but the lane has already paid for this class once: the r89
fold fix carries the comment *"the '47 legs' headline in the author commit/report was
arithmetic drift — the receipt leg keys are the record"*. The r95 headline numbers that *are*
right (5 entries, 24 legs, the two implementation shas) I verified independently; the two
that are wrong are the two that were not re-derived.

---

## 3. What I could **not** test (named blockers, not silent)

The host's PipeWire/pulse layer was **unresponsive for the whole window** (load 52–55; ~8
sibling batteries running: r90, r91, r92, r94-simplifier, r96, r98, r99):

- `pactl info` → `rc=124` (killed at bound, no answer); `pactl load-module` never returns;
  `pw-dump` → `rc=124`, **0 bytes**; `pw-cli info 0` prints the core info then hangs.
- My own end-to-end re-run of the frozen bytes (`r95c_indep.py`) aborted at the first act
  (`own sink never enumerated`) and printed nothing else — the same block both sibling seats
  hit. **My live re-derivation of the armed laws therefore does not exist**: not the
  `outm → 2` CanMonitor correction, not the addressing matrix, not the byte witnesses, not
  the quantum lattice.
- The `outm → 2` correction I can only support **statically**: the fixture registers
  `JackPortIsOutput|JackPortCanMonitor` (`r95jack.c:303`) and prints the real
  `jack_port_flags` (`print_latency`, `r95jack.c:206`, flags at `:216`), so the armed 2 is a measurement
  rather than a transcription; the boundary's own receipts carry `lat_outm.flags == 2`
  (3/3 + 3/3) and the labrat's source read finds `JackPortCanMonitor` absent from the whole
  file. **Verdict on that row: boundary-consistent, not critic-reproduced.**
- Whether the two blocked sibling runs left orphaned `r95a_ns_3228981` /
  `r95a_ns_3231401` modules: **unmeasurable** (no readable graph), and their receipts carry
  no census because of C1. Recipe for the fold when the daemon recovers:
  `pactl list short modules | grep -E 'r95a_ns_3228981|r95a_ns_3231401'`.

## 4. Seat's own footprint / disclosures

- Artifact archive written to `corpus/live/r95-critic/tree/` (untracked); report here;
  scratch under `~/Projects/shokunin/tmp/r95c/` (untracked). No tracked file modified, no
  commit, no `pactl set-default-*`, no `wpctl set-default`.
- I compiled the **frozen** `r95jack.c` twice (own gcc lines) into TMPDIR; binaries
  `r95cjack` (sha prefix `016a685372e6d8fa`) and `r95c_version`.
- One aborted own run (06:03Z) called `pactl load-module module-null-sink
  sink_name=r95c_ns_<pid>` / `r95c_t4_<pid>` with the space-separated `sink_properties` form
  and unloaded whatever it had ids for; because the daemon stalled, the response may have
  been lost and the module may exist without an id. **Disclosed exposure**: if a later
  census finds an `r95c_`-named null sink, it is this seat's — `pactl list short modules |
  grep r95c_`. I could not verify it (no readable graph all window), and my own
  `own_nodes_after` is *not* a valid census under that condition — the same C1 weakness, in
  my own scratch, stated rather than hidden.
- I read the two sibling receipts but touched neither their processes nor their trees; I
  killed only my own `r95cjack` PIDs (verified gone).

---

## 5. Verdict

**Landing: PASS-with-findings — the block extraction is clean and provably the author's
intent (A1–A7, byte-identical block `5c610972…`, 3 splice deletions, 24 legs, reproducible
fixture build, no prior-row change).**

**The family's green claim does not survive an independent re-run in this window.** Both
independent seats that executed the frozen bytes came back `rc=1` with **4/5 entries vacuous
greens and 1/5 entries red for a host reason** (C1, C2). C1 and C2 are *fixable defects*, not
tradeoffs the judge must reject: they are both instances of the same hole — *unavailable
witness/daemon armed as falsified claim, and the blocked path losing the evidence that would
say so* — and the smallest safe correction is one bounded gate plus two lines in
`_jack_r95_block` (carry `legs`, run the census, mark `measured: false`). C3/C4 are a
repo-convention defect in the family-lock authority (tree-local path; unbounded wait) that
the fold should own, not r95 alone. C6 is report arithmetic, twice, in the exact class the
lane has already folded once.

**Gate condition for the round:** do not read `failures: {}` as green for any r95 entry.
Read `coverage_blocked`; require it empty for all five entries before the family carries a
green, and re-run when the host daemon answers.

**Impacted axes:** reproducibility of the green (independent re-run fails in-window);
evidence integrity of blocked entries (legs + exit census dropped); host-state safety
(family lock not family-global; residue census skipped on the block path; unbounded lock
wait); provenance accuracy (report arithmetic).

*Leaf seat — attacked the approach and the bytes; did not judge, admit, edit, integrate, or
ship.*
