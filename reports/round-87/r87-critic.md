# r87 critic — wave-B gate on committed `d1e687b9`

Seat: `ufo-executor` (critic duties as assigned by
`.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r87-critic.md`).
**Committed tree only** (`d1e687b9`), zero tracked writes, nothing
committed. Receipts: `corpus/live/r87-critic/` (+ `MANIFEST.txt` with
shas and commands).

**Verdict: ADMIT-with-findings.** Every claim the task names is
**verified as specified** on the committed receipts: the boundary-
corrected routing law `target.object > --target > node.target` is armed
**either-way and sharply** (46/46 targeted mutations RED across both
green runs, including the scout's *reversed* law), serial-resolves /
object.id-never is armed on both the flag and the prop paths, the Props
live-DSP witness reproduces exactly (`8192 → 2048 → 8192 → 0 → 8192`),
the midi dead-target census and the 45 B SMF pin are real, and the
rc255/rc0 remote-surface census is what the author says it is. The
fixed-path lock is **proven not `$TMPDIR`-scoped** (5/5 either-way cases
with an in-tree negative control). F1–F3 are **silent-skip / vacuity
channels proven by execution**; F4–F8 are arm-strength and latent-
vacuity gaps; F10 is the inherited tree-relative lock residual, which
this session **live-witnessed** (the wave's own r87-verifier is running
the same committed bytes from a copied tree, unserialized). Nothing here
is a shipping decision.

---

## 0. Method (what was actually executed)

| check | evidence |
|---|---|
| commit custody + diff shape + wiring (static) | `git show d1e687b9 --numstat/--`; blob sha; fixture sha256; hunk-header census |
| receipt census (legs, failures, teardown, coverage, dev runs) | `census.py` → `census.json`, `census.out` |
| **lock either-way proof** — the committed lock functions sliced verbatim, run cross-/same-`TMPDIR` and cross-tree, with the in-tree r85 `$TMPDIR`-scoped lock as **negative control** | `locktest.py` + `locktest_child.py` → `locktest.json`, `locktest.out` |
| **routing-law arm replay** — the committed `pwbind_target_r87_entry` verdict block sliced by marker out of `git show d1e687b9:…` and `exec`'d: re-derivation on both committed receipts + 23 targeted mutations ×2 runs + 8 absorption cases | `arm-replay.py` → `arm-replay.json`, `arm-replay.out` |
| **midi + cli absorption-gap proof** — same technique on the midi and cli verdict blocks: 10 absorption cases + 9 controls | `arm-replay-gaps.py` → `arm-replay-gaps.json`, `.out` |
| bounded **read-only** live corroboration | `live-readonly.py` → `live-readonly.json`, `live-readonly.out` |
| cold-registry hypothesis (dispatcher fallback for the labrat probe) | `cold-registry.py` → `cold-registry.json`, `cold-registry.out` |
| co-tenancy witness (concurrent sibling seat, captured live) | `co-tenancy-witness.txt` |

No live battery was re-run (a battery would mutate the host and would
contend with the sibling seats already running this lane). The live host
was touched with **read verbs only** (`pw-dump`, `pactl get-*`/`list`,
`pw-cli info`/`--version`, `sha256sum`, `realpath`). Every run used
`TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `PYTHONDONTWRITEBYTECODE=1`;
loadavg **84.6–96.2** (load preferred, as the task directs).

Arm-replay provenance: the arm text is the **committed text**, sliced
verbatim out of the commit object, not a paraphrase. The only
substitution is `_pwbind_r87_default_sink` → the **recorded**
`default_sink_at_end`, so the drift arm is exercised deterministically;
the ns/ns2 names are parameterised per run from the receipt's own
`sinks_gone` keys. Every sliced fragment is archived with its sha in
`MANIFEST.txt` (`armfrag-*`, `lockfn-*`, `_committed_measure_audio.py`).

---

## 1. Custody and wiring — verified

- committed fixture sha256
  `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516`
  == worktree == the sha the author report claims for **both** runs.
- diff shape: `+2083/−3` in the fixture (numstat) + 238 lines of report.
  Six hunks: one 2055-line insertion
  (`@@ -25449,6 +25449,2061 @@` between `pwctl_tools_r86_entry()`'s
  `return` and `main()`) plus five wiring hunks
  (`+1`, `±1`, `+24`, `±1`, `±1`). **The only 3 deleted lines are exactly
  the three replaced wiring lines** — the flag mutex sum, the `mode`
  ternary and the `suffix` ternary. No prior-family line (r76–r86) is
  touched; append/prepend only.
- wiring present and correct: `--probe-pwbind-r87`, the mutex sum
  including it, the dispatch `if args.probe_pwbind_r87:` with
  `_r87_family_lock = _pwbind_r87_family_lock()` **before** the first
  entry and held to exit, `mode`, `suffix`.
- receipt census: **4 entries / 105 legs** (modes 18, target 33, cli 30,
  midi 24) in **both** green runs; leg names **byte-identical** across
  the two runs (`census.json:legname_diff` = IDENTICAL for all four);
  `failures` empty and `coverage_blocked` absent on all four entries in
  both runs.
- canonical receipt shas match the author's claims exactly:
  run A `20261016T070036115509Z` → `01f04d354f2186db…d79c7586797d1f1667`;
  run B `20261016T070305393338Z` → `2970c944375f2e3b…a0a7d9a974a655`.
- the three dev runs are also present; the **first** dev run
  (`20261016T064958137082Z`) carries a real
  `coverage_blocked=['midi pin leg unmeasured — bridge capture port or
  seq 14:0 absent']` on the midi entry — i.e. the boundary's startup
  flake is a **real observed event** and the committed degradation path
  was exercised for real, not merely written.
- guards checked statically in the committed block: private restore key
  `r87arole<pid>` (never the shared `music`); **no `set-default-*` call
  anywhere**; every unload goes through `_pactlmon_r85_unload_own`
  (module index re-read + own `sink_name=` byte-match immediately before
  firing, captured ids never fired); a residual census destroys any
  surviving `r87a_<pid>` node by id before the final sweep;
  `sinks_gone`/`own_nodes_after` armed; reader failures append to
  `coverage_blocked`. The lattice **reads** the default sink and never
  writes it (receipt: `default_sink_at_start == default_sink_at_end` on
  both runs).

## 2. The four entries — receipt evidence (run A / run B)

| entry | law surface | sharpest committed evidence |
|---|---|---|
| `modes` (18 legs) | one binary + direction flags, no duplex | `pw-play`/`pw-record`/`pw-midiplay`/`pw-midirecord` realpath == `pw-cat`; `pw-mididump`/`pw-cli` distinct; 7 refusals by error class; last-wins armed in **both** directions (`m_p_r`/`m_r_p_r`/`m_play_r` → `Stream/Input/Audio` with `input_*`; `m_r_p`/`m_p_r_p`/`m_record_p` → `Stream/Output/Audio` with `output_*`); never-duplex asserted per leg |
| `target` (33 legs) | the routing precedence lattice | see §3 — 30 routing verdicts + 3 hard no-link switches + the name-collision arm |
| `cli` (30 legs) | pw-cli on live objects | cold-registry artifact + warm contrast; 5 unknown-global verbs; **Props live-DSP witness** solo 8192.0 → `{volume:0.25}` 2048.0 → `{volume:1.0}` 8192.0 → `{mute:true}` 0.0 → `{mute:false}` 8192.0; `--volume` spawn ladder v100 8192 / v050 4096 / v000 0 / v150 12288; Format seal on stream **and** sink; sendcmd table; create-node session-bound vs `object.linger=true`; last leg unloads the whole module |
| `midi` (24 legs) | dead-target + pin + remote census | all six `m_t_*` forms rc=1 + `no target node available` + `res:-2`; `pin` **45 B** SMF with both `0x90` note-ons and both `0x80` note-offs; `skeleton` 26 B `MThd+MTrk+EOT`; `remote_cli` **rc 255** `Host is down`; `pwcli_*` module loads **rc 0** with `Could not load module`; `remote_census` zero remote-named nodes and zero raop/zeroconf/airplay `.so` in a 34-entry module dir |

## 3. The routing law — either-way proof (the headline claim)

`arm-replay.py` executes the **verbatim committed verdict block** against
the committed legs and against mutated legs. **Re-derivation: 0 failures
on both runs.** **Mutations: 46/46 RED, 0 not-as-designed.**

| mutation | run A / run B |
|---|---|
| `p_nt_vs_flag` lands NS2 (**the scout's reversed law**: flag loses to node.target) | RED |
| `p_nt_rev` lands NS (reverse leg) | RED |
| `p_three` lands NS (prop loses to flag) | RED |
| `p_prop_twice` lands NS (first `-P` wins, not last) | RED |
| `p_pb1` lands NS (garbage prop falls through to a valid flag) | RED |
| `p_pb2` lands DEF | RED |
| `p_pb3` lands NS | RED |
| `p_nt_garbage` lands NS2 (**garbage flag falls through to node.target**) | RED |
| `p_objid` / `p_prop_objid` land NS (**object.id resolves**) | RED |
| `p_serial_stale` lands NS | RED |
| `p_env_vs_prop` lands NS2 (env loses to `-P`) | RED |
| `p_env_garbage` lands NS | RED |
| `p_env_nobrace` lands DEF (brace form only) | RED |
| `p_own` gains a second consumer (cross-link) | RED |
| default sink drifts mid-entry | RED |
| `p_zero` / `p_noauto` gain a consumer | RED |
| `p_zero` node never present | RED |
| `p_mon` lands NS (the `.monitor` suffix resolves as a name) | RED |
| `p_src_name` lands NS (wrong-class source resolves) | RED |
| `p_mediarole` / `p_capsink` land NS | RED |
| `p_empty` lands NS | RED |
| `p_coll` lands NS2 (collision resolves to the stream) | RED |
| `p_cat` lands DEF (pw-cat does not share the lattice) | RED |

Measured precedence on both runs (run A shown), which is exactly the
boundary's correction of the scout:

```
p_three        -P target.object=NS2  -P node.target=NS   --target NS  -> [NS2]   prop > flag
p_nt_vs_flag   -P node.target=NS2                        --target NS  -> [NS]    flag > node.target
p_nt_rev       -P node.target=NS                         --target NS2 -> [NS2]   (both directions)
p_nt           -P node.target=NS                         (no flag)    -> [NS]    node.target alone works
p_pb1          --target NS  -P target.object=BOGUS                    -> [DEF]   garbage prop BEATS valid flag
p_nt_garbage   -P node.target=NS2                        --target BOGUS -> [DEF] garbage flag does NOT fall through
p_objid        --target <object.id>                                   -> [DEF]   object.id NEVER resolves
p_serial       --target <object.serial>                               -> [NS]    serial resolves
p_coll         a stream NAMED like the sink                           -> [NS]    sink wins name resolution
```

So the encoded law is not "a precedence chain with fallback" but
**first-present-wins with no fallback**, ordered
`target.object > --target > node.target`, and every unresolvable string
lands the current default sink. The committed entry docstring says
exactly that. `p_coll`'s `collision_objects` records both the `Audio/Sink`
and the same-named `Stream/Output/Audio` present simultaneously, so the
collision leg really is a collision, not a coincidence.

## 4. The fixed-path lock — either-way proof

The three committed lock functions were sliced verbatim and run in a
controlled harness. `r85` (`Path(tempfile.gettempdir())`) is the
**negative control** — the in-tree pre-fix shape, so the control is drawn
from the same committed file. **5/5 as designed:**

| case | lock | TMPDIRs | expected | result |
|---|---|---|---|---|
| A | r87 | different | SERIALIZED | **SERIALIZED** (child waited 2.003 s) |
| B | r86 | different | SERIALIZED | **SERIALIZED** (child waited 1.981 s) |
| C | r85 | different | RACED (control) | **RACED** (waited 0.000/0.005 s) |
| D | r87 | same | SERIALIZED | **SERIALIZED** (waited 1.989 s) |
| E | r87 | cross-**tree** | RACED | **RACED** (waited 0.000/0.000 s) |

Case C proves the harness can detect racing, so A/B/D are not
false-greens. The r87 lock path is
`ROOT / "live" / "measure_audio-pwbind-r87.lock"` where
`ROOT = Path(__file__).resolve().parents[1]` → a **fixed lane path,
never `$TMPDIR`** — the claim in the task is **confirmed**. Case E is
F10 below.

## 5. Findings

**F1 — medium — the midi dead-target census silently skips absent legs,
with no `coverage_blocked`.** `pwbind_midi_r87_entry`'s verdict loop
(27402–27413) does `l = legs.get(name); if l is None: continue`, and
`m_t_serial`/`m_t_objid` are only *built* `if bridge:` (27201–27207).
Proven by execution (`arm-replay-gaps.json`):
- **MID-G1** — all six `m_t_*` legs removed → **PASS, 0 failures, no
  `coverage_blocked`**. The entire dead-target census can be unmeasured
  and the entry is still green.
- **MID-G2** — only `m_t_serial` + `m_t_objid` removed (the `if bridge:`
  branch) → **PASS, no `coverage_blocked`**. This is precisely the
  "serial resolves / object.id never" half of the claim the task names:
  on a host with no `Midi-Bridge`, it is unmeasured and silent.
- Controls: `m_t_bridge` rc=0 → RED; `pin.file` absent → **PASS but
  `coverage_blocked` recorded** (correct behaviour, and the contrast that
  shows G1/G2 are the anomaly). Fix: replace `continue` with an
  `entry.setdefault("coverage_blocked", []).append(...)` and make the
  bridge-less branch record the two unmeasured legs.

**F2 — medium — `mdump_live` with an empty `attempts` list passes
silently.** `live = {"attempts": []}` (27299) and the attempt loop only
runs `if bridge and bridge.get("capture_port") and seq`. The verdict arm
is `if live and not noted: coverage_blocked` / `elif noted and …: fail`
(27456–27464) — with `attempts == []` **both branches are falsy**.
Proven: **MID-G3** → PASS, no failure, no `coverage_blocked`. Fix: make
the empty-attempts case take the same `coverage_blocked` branch as
"never published".

**F3 — medium — the three hard no-link switches accept a *real* link
whose peer name did not resolve.** `_pwbind_r87_consumers` collects only
truthy `in_node`, and `_pactlmon_r85_edges` derives `in_node` from a
`nodes.get(l["in_node"])` lookup that returns `None` when the peer's
global id is missing from that graph snapshot (a real race on a loaded
daemon). Proven (`arm-replay.json`): **A6** `p_zero`, **A7** `p_noauto`,
**A8** `p_zero_prop` — each given a `playback_FL` edge with
`in_node=None` → **all three PASS**. The arm cannot distinguish "no link"
from "a link whose peer name missed the snapshot". Note the positive
arms are fail-closed here (A1: a leg with no snaps at all → RED; A4: a
transient mis-route caught by the union-across-snaps → RED), so the
exposure is confined to the three no-link switches. Fix: arm on
`len(edges_out) == 0` rather than on the *resolved* consumer set. The
midi `m_t_zero`/`m_noauto` arm shares the same `consumers` primitive but
additionally requires last-snap presence and an exact `media_class`, so
it is narrower — same fix applies.

**F4 — low — the `p_zero` family checks presence at *any* snap, not the
last.** `if got or not any(s.get("present") for s in legs[name]["snaps"])`
(26458) accepts a node present at 0.9 s and gone at 1.7 s. Proven: **A3**
→ PASS. Every sibling arm in the same commit uses
`_pwbind_r87_last_snap` (the midi no-link arm at 27416, the modes
direction arm at 26237); this one arm is the outlier. Fix: use
`_pwbind_r87_last_snap`.

**F5 — low — the foreign identical-value-write arm is vacuous when the
volume did not parse.** `if fo.get("volume_read") is not None and
fo.get("volume_after") != fo.get("volume_read")` (27086). Proven:
**CLI-G1** (`volume_read = None`) → PASS, no `coverage_blocked`; control
**CLI-C1** (`1.0 → 0.5`) → RED. Latent on this host (`volume_read=1.0`).

**F6 — low — the `props_unk` unknown-key-drop arm is structurally
vacuous.** `if legs.get("props_unk") is not None:` (27009). Proven:
**CLI-G2** (leg removed) → PASS, no `coverage_blocked`. Latent in the
committed flow because the same `attached` flag gates `props_unk` *and*
`solo`, and a missing `solo` fails first — but the guard is silent by
construction and would stop being latent if the solo reference ever came
from a different source.

**F7 — low — the live-DSP multiplier envelopes are wide.** `V25_ENV =
(0.15, 0.35)` around a claimed **exact** 0.25; proven **CLI-G3** (ratio
0.16) and **CLI-G4** (ratio 0.34) → both PASS; control **CLI-C2** (ratio
1.0, a no-op write) → RED. So the arm does exclude "the write did
nothing" and "the write muted", which is the point — but a 6×-wrong
multiplier is admitted. The `--volume` ladder is tighter
(`V50 (0.40,0.60)`, `V150 (1.35,1.65)`, ±20 %) and the tap is clean
enough to have measured 2048/8192 exactly, so a tighter `V25_ENV` is
available. Envelope-not-pin is the wave's declared convention, so this is
a strength note, not a defect.

**F8 — low — `MUTE_MAX = 128` admits non-zero residue.** Proven
**CLI-G5** (`median_peak = 64`, i.e. 0.8 % of solo) → PASS. Measured
0.0 in both runs, so latent; the arm's real job (rejecting an unmuted
8192) is done.

**F9 — informational (verified, not a gap) — `p_coll`'s port-shape arm
is armed.** `if coll_ports and not all(str(p).startswith("playback_") …)`
looks short-circuitable, but `coll_ports` collects `None` entries when
ports are absent and `str(None)` = `"None"`, so **A2** (edges stripped of
`in_port_name`) → RED as designed. Recorded so a later reader does not
mistake it for a gap.

**F10 — medium (inherited, and LIVE-WITNESSED) — the fixed-path lock is
*tree-relative*.** `ROOT = Path(__file__).resolve().parents[1]`, so the
lock lives at `<tree>/corpus/live/measure_audio-pwbind-r87.lock`: a
same-family run from a **copied tree** takes a *different* lock file and
is **not** serialized. This is the r86 F1/F6 residual, inherited
unchanged by r87. Proven by locktest case **E** (cross-tree → RACED) and
**realized live during this session** — see §6. Within this wave
`TMPDIR` is pinned and the author's two runs shared a tree, so the two
green runs did serialize.

**F11 — informational — hygiene.** `_pwbind_r87_family_lock`'s returned
fd is never read (intentional fd-hold, but linter-visible, as in r86);
`p_cat` records no `last.media_class` (the arm correctly uses `consumers`
only, but the class is unrecorded and so unverifiable from the receipt).
`py_compile` of the committed source is clean.

**F12 — informational — no doc drift found.** Unlike r85 (F7), the r87
family header, the four entry docstrings and the arm comments all agree
with what the committed arms actually measure — including the explicit
statement that the correction is the boundary's and that the scout's
reversed claim is *not* encoded.

## 6. Live corroboration (independent of the author's receipts)

### 6a. Read-only host state — `live-readonly.json`

- **binary-identity lattice reproduced independently**: `pw-play`,
  `pw-record`, `pw-midiplay`, `pw-midirecord` all realpath to
  `/usr/bin/pw-cat` with the same sha256; `pw-mididump` and `pw-cli` are
  distinct. The modes entry's first arm is a fact about this host, not a
  receipt artifact.
- **midi pin precondition present**: `Midi-Bridge` node id 46
  (`Midi/Bridge`); ALSA seq `14:0 Midi Through Port-0`; `/dev/snd/seq`
  exists.
- **remote-surface census reproduced**: zero remote/raop/zeroconf/
  airplay-named nodes; `ls /usr/lib/pipewire-0.3 | wc -l` = **34** with
  zero raop/zeroconf/airplay matches — matching `remote_census`'s
  `module_dir_count: 34`.
- default sink `…HiFi__SPDIF__sink.29` and default source
  `…HiFi__Line__source.29` — the values the lattice reads and never
  writes.

### 6b. Cold-registry hypothesis — CONFIRMED (`cold-registry.json`)

The frozen probeParent dispatched exactly one read-only `labrat`; its
substrate exposed no command-execution tool, so it returned **STILL NO
EXEC** (see §7). The dispatcher then ran the same bounded read-only
battery directly. Result on the live host, read verbs only:

```
pw-cli info 232            -> rc 0, full dump: "id: 232 / type: PipeWire:Interface:Node/3 / properties: …"
printf 'info 232\nquit\n' | pw-cli
                           -> rc 0, stdout "Welcome to PipeWire version 1.6.8…", stderr
                              Error: "info: unknown global '232'"
   (reproduced a second time — identical)
pw-cli info 99999999       -> rc 0, Error: "unknown global '99999999'"
printf 'info 99999999\nquit\n' | pw-cli
                           -> rc 0, Error: "unknown global '99999999'"
pw-cli info 172871         -> rc 0, Error: "unknown global '172871'"   <- the pactl index / object.serial
```

So **H1 holds**: the same read verb on the same *live* global id gives a
full dump in argv mode and `unknown global` in stdin-at-t=0 mode, stably
across repeats — the `cold_nowarm` / `warm_control` contrast the fixture
arms is real and independently reproducible. Two side observations:
the *serial* `172871` is still not a global id (the r86 §5 law holds on
this host now), and the cold form is a **rc-0 lie** (exit code 0 with an
error on stderr), which is why the committed arm asserts on the text
blob rather than on `rc`.

### 6c. Co-tenancy witness — captured live (`co-tenancy-witness.txt`)

At `2026-10-16T07:07:31Z`, while this gate was running, the wave's own
**r87-verifier** seat was executing the committed bytes from a **copied
tree**:

```
pid 763463  python3 corpus/fixtures/measure_audio.py --probe-pwbind-r87
launched from  corpus/live/r87-verifier/tree   (its ROOT resolves to
               .../r87-verifier/tree/corpus)
```

- the **lane** lock `corpus/live/measure_audio-pwbind-r87.lock` was
  **FREE** at that moment (a non-blocking `flock` acquired it
  immediately) while the verifier was mid-run — so the two runs were
  **not** serialized;
- the verifier's **own** tree lock held
  `pid=763463 ns=r87a_ns_763463 role=r87arole763463`;
- the verifier's namespace was visible in the **shared** daemon
  (`r87a_763463_mr`, `Stream/Input/Midi`, node id 223) and was correctly
  recorded by the committed design as a **foreign** `r87a_` witness —
  teardown targets only its own pid.

This is F10 realized, not hypothetical: it is exactly the r86 F1/F6
cross-tree co-tenancy residual, and it is also the r86 reviewer's F1
("cross-tree co-tenancy can false-FAIL `meta_keys_gone`, fail-closed").
The committed design's response (foreign names recorded, never judged;
own-pid-only teardown) is the right one, and it is what makes this
tolerable rather than fatal. **Disclosed by name as required.**

## 7. Probe tooling note

The frozen probeParent dispatched **exactly one** read-only `labrat`
(hypothesis = the cold-registry artifact). It returned
**INCONCLUSIVE — no measured evidence**: its substrate exposed only
file-inspection tools (no exec), so it could run no `pw-cli`/`pw-dump`
command. Per the seat card the dispatch was **retried once after warmup
to the same child seat** (not a second spawn); it again returned
**`STILL NO EXEC`**. That unavailability is recorded here as
**unavailability, not absence**. The child made no edits and left nothing
behind. The dispatcher then ran the same bounded read-only battery
directly (§6b), which **confirmed** the hypothesis.

## 8. Blockers / remaining risks

- **Blockers: none.**
- F1–F2 are the same silent-skip class the wave has now flagged in three
  consecutive rounds (r85 F2, r86 F1, r87 F1/F2); both are proven by
  execution and both are one-line fixes.
- F3 is fail-closed on every positive routing arm; the exposure is
  confined to the three hard no-link switches, and it needs a graph
  snapshot race to realize — likely under the load this lane runs at.
- F10 is inherited and **live**; the tree-relative lock means the
  fixed-path fix only serializes *within* a tree. A cross-tree
  co-tenancy guard (an OS-level named lock, or an in-daemon sentinel)
  would be the durable fix, but it is a design decision, not this gate's.
- The three bimodal realizations (the boundary's corrections) are all
  armed on both sides; a verifier host realizing the *other* side is a
  pass, not a failure.

## 9. Custody notes

- **Zero tracked writes.** The fixture in the worktree is byte-identical
  to the commit object; `HEAD` is still `d1e687b9`; nothing was staged or
  committed. The only dirty tracked path is
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`, which was
  **already `M`** in this session's first `git status`; a fresh
  `py_compile` of the committed source reproduces the current worktree
  `.pyc` byte-for-byte (`b8826019…`), so it is bytecode churn over
  unchanged source, not source drift. The committed `.pyc` is the older
  `6e271a2d…`.
- **Lock-file disclosure.** The lock either-way proof necessarily
  writes the lane lock (`corpus/live/measure_audio-pwbind-r87.lock`,
  untracked, by design a scratch artifact holding the last holder's
  witness line). It overwrote the author's run-B witness
  (`pid=3585207 …`) with the harness pid; **the original bytes were
  restored at the end of the session** and the file is now byte-identical
  to its pre-session content. All other receipts live under
  `corpus/live/r87-critic/` (untracked) and `reports/round-87/`.
