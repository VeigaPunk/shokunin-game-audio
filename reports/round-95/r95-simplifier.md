# r95 simplifier — proven folds on the JACK ↔ PipeWire family (queued, not landed)

**Verdict: PASS-with-named-blocker — 5 proven folds queued (`F2`–`F6`,
`+18/−24` lines in `corpus/fixtures/measure_audio.py`, net −6), 3 candidates
held with explicit tradeoffs (`F1`, `F7`, `B7`), 2 law-audit notes. Nothing
landed, zero tracked writes, zero commits. No unreferenced helper, no
tautological law and no law reading a key the fixture never emits was found —
those three audits came back clean and are reported as negative findings with
their method.**

The runtime proof is **partial and named**: the family's own narrow check
(`--probe-jack-r95`, 5 entries / 24 legs) could not be executed in this lane
because the host's PipeWire daemon is wedged (see §3). Every fold is proved
either by a daemon-free differential run against a folded scratch copy
(`F6`) or by a whole-input-domain equivalence table plus an AST-locality
proof (`F2`–`F5`). The integrator should have the round's verifier re-run
`--probe-jack-r95` on a quiet host **before** landing.

- Lane: `/home/vgpnk/Projects/shokunin/audio-shokunin`. HEAD moved under the
  lane: entry `021bde86` (r89 adjudicate) → exit `6fcff792` (r94 adjudicate).
  The two audited blobs are byte-identical at both ends (see §1).
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, bounded runs (`timeout -k`),
  never `pactl set-default-*`, no device touched, no module loaded by this
  seat, every child its own session leader and killed by pid.

## 1. Audited revision and scratch

| artifact | revision | size | sha256 |
| --- | --- | --- | --- |
| `corpus/fixtures/measure_audio.py` | r95 block lines **33289–35059** | 36 403 lines (block 1 771) | `dca4dc9bc87e006b534a50d80270bfb27492fadecfe75fbbd89f37342bd87ed7` |
| `corpus/fixtures/r95jack.c` | whole file | 778 lines | `55d4d4111bd8d46be743d0425a40dc8d938d15e071ce37f460db70de0df997be` |

Both hashes are identical at entry and at exit
(`corpus/live/r95-simplifier/shared-tree-entry.sha256`), and
`git status --porcelain --untracked-files=no` is empty at exit: **the shared
tree is byte-identical, zero tracked writes, zero commits**. All scratch
artifacts live under `corpus/live/r95-simplifier/` (untracked, the lane's
granted scratch path): a byte-identical copy of both audited files, the
extracted r95 block, the folded copies, five proof harnesses, their JSON
receipts and the two queued patches.

## 2. Reference proof — and the `lsp` unavailability record

**No `lsp` device exists in this seat's toolset, and no language server
answers `corpus/fixtures/measure_audio.py`.** The only configured MCP server is
`rea`, a Ghidra-family native-binary analysis server whose operations are
keyed by procedure address / executable bytes (`annotate_native_function`); it
does not answer a Python source file. Deletion candidates were therefore
screened by **AST reference analysis over the module** (definition census,
`Name` load accounting, `Subscript`/`.get()` reader accounting with store/load
distinction, full call-site token census) plus a **repo-wide literal grep as
the declared fallback**. Neither is semantic proof and neither is presented as
such; where a name survives only in another seat's derived artifact
(`corpus/live/r95-critic/tree/…`, `corpus/live/r82-verify/tree/…`, the
boundary's `probes/r95bjack.c`) that artifact is *derived* or *historical*, not
a caller of the landed harness, and is called out in the tables below.

One class of candidate — the fixture's own mode dispatch — is decided
*semantically enough to be decisive*: every mode token the landed harness can
pass to `r95jack` is a literal in an enumerable call site, so the AST call-site
census (§4) is a complete caller set for the fixture's `strcmp` dispatch.

## 3. Runtime-proof status — the family's legs are unrunnable in this window

The r95 family needs a live PipeWire/JACK client path (`pw-dump`, `pw-cli`,
`pactl`, and a JACK client that activates). In this window the host daemon is
wedged:

- load average **53.8–57.1 on 32 cores**, driven by **48 `yes` processes**
  (parent pid 1537) that have been running **13 h** — `ps -eo pid,ppid,etime,args`;
- `pw-dump` never returns: `timeout 25` → rc 124 with 0 bytes; `timeout 90` →
  rc 124 with 0 bytes. `pw-cli ls Client` and `pactl list short sinks` hang
  past 10 s. **5 `pw-dump` processes from sibling lanes** are stuck
  (5–12.5 min elapsed each; a sixth sibling lane is itself running
  `timeout 200 pw-dump`) — the stall is daemon-wide, not lane-local
  (`blocker-census.txt`);
- the daemon *core* is alive (`pw-cli info 0` answers in ms, `pw-metadata -n
  settings` answers in 7 ms), so this is an enumeration/activation stall;
- a real fixture client run was killed at the bound with **zero output**:
  `R95A_NAME=r95s_<pid>_live timeout -k 3 20 ./bin/r95s_jack info 0.1` → rc 137,
  empty stdout/stderr (the client never got past open/activate in 20 s).

Consequences, stated plainly: **`F2`–`F5` could not be re-run through their
runtime legs** (`jack_surface_r95_entry`, `jack_addr_r95_entry`,
`jack_bytes_r95_entry`, `jack_defects_r95_entry`); their proof is the
equivalence tables of §6 plus the AST-locality proof, not a green receipt.
**`F6` is proved dynamically** because its affected leg is the no-daemon path,
which needs no live client (§6, `prove-f6-e2e.json`). The family lock
`corpus/live/measure_audio-jack-r95.lock` present in the tree is a **sibling
lane's** (pid 3228981, not this seat's); it was read, never written or removed.

## 4. Reference census — what is actually referenced

**Helper census (AST `Name` loads over the whole module; every r95 helper is
referenced at least once, so there is no unreferenced helper to delete):**

| helper | line | refs | helper | line | refs |
| --- | --- | --- | --- | --- | --- |
| `_jack_r95_errclass` | 33377 | 1 | `_jack_r95_wav_stats` | 33727 | 1 |
| `_jack_r95_norm` | 33385 | 2 | `_jack_r95_symbols` | 33761 | 1 |
| `_jack_r95_env` | 33393 | 21 | `_jack_r95_load_ns` | 33781 | 5 |
| `_jack_r95_run` | 33404 | 6 | `_jack_r95_family_lock` | 33799 | 1 |
| `_jack_r95_json` | 33491 | 1 | `_jack_r95_entry_head` | 33818 | 5 |
| `_jack_r95_probe` | 33503 | 21 | `_jack_r95_teardown` | 33836 | 5 |
| `_jack_r95_build` | 33518 | 5 | `_jack_r95_block` | 33914 | 15 |
| `_jack_r95_graph` | 33551 | 16 | `_jack_r95_eq` | 33939 | 115 |
| `_jack_r95_edges_touching` | 33639 | 7 | `_jack_r95_band` | 33945 | 14 |
| `_jack_r95_port` | 33644 | 1 | `_jack_r95_true` | 33951 | 12 |
| `_jack_r95_meta_rows` | 33652 | 3 | 5 × `*_r95_entry` | 33956+ | 1 each (from `main`) |
| `_jack_r95_settings` | 33671 | 9 | `_jack_r95_driver` | 33679 | 1 |
| `_jack_r95_shape_slice` | 33687 | 2 | `_jack_r95_tone` | 33706 | 1 |

All 15 r95 module-level constants have ≥1 use (14 × `JACK_R95_*` plus
`_JACK_R95_ERR_CLASSES`, whose single use is inside `_jack_r95_errclass`).

**Fixture-mode census (AST call-site token census over every
`_jack_r95_probe`/`_jack_r95_run` call in the landed harness):** the fixture
implements **11** modes and the harness invokes exactly
`info, shape, tone, stall, bufsize, rtprio_poison, latency, transport,
metadata, xconnect` — 10. `rtprio` is the one mode with **no landed caller**
(§6, `F1`).

**Law-key census:** for each entry, every key its laws read out of the probe
JSON is emitted by that entry's modes (the three apparent misses
`lat_out`, `out_active`, `in_active` are the *dynamic* labels
`"lat_%s"` / `"out_active"` / `"in_active"` of `print_latency` and the latency
mode, emitted by the fixture). **No law is vacuous by reading a never-emitted
key** — that audit is clean.

## 5. Queued folds (proven, not landed)

Applier: `corpus/live/r95-simplifier/apply_folds.py` (every anchor asserted to
occur exactly once/twice, `py_compile` on the result, AST locality diff).
Patch: `corpus/live/r95-simplifier/folds-r95s.patch` (`+18/−24`, net **−6**
lines). Hunk map, all inside the r95 block:
`33369, 33664, 33911, 34169, 34293, 34459, 34897` — **no other family's
identifier appears in the diff**; the only module-level touch is one tuple
member of `_JACK_R95_ERR_CLASSES` (`F6`), so the AST assignment-*count* delta
is 0 (`module_level_assign_delta`), not "no module-level change".

| # | fold | site | what it removes | proof | tradeoff |
| --- | --- | --- | --- | --- | --- |
| `F2` | one driver-sink unload authority | `jack_surface_r95_entry` 34172–34182 + `jack_bytes_r95_entry` 34462–34472 → new `_jack_r95_unload_ns(entry, failures, leaf, label)` | 2 × 11 identical lines, keeping one expression of the "probe sink must not survive the name-verified unload" law | `fold-equivalence.json:F2` — the two blocks are **identical modulo the failure label** (`s_shape:` vs `b_jack2pw:`), 11 shared lines each; the helper body is that block verbatim | the failure text is now built from a `label` argument; both labels are passed verbatim at the two call sites, so the emitted strings are unchanged |
| `F3` | redundant conditional | `jack_addr_r95_entry` 34296 | `if dst != conns_want[0] if conns_want else False:` → `if conns_want and dst != conns_want[0]:` | `fold-equivalence.json:F3` — `all_equal: true` over the whole reachable domain (empty/non-empty `conns_want` × equal/unequal `dst`) **and** over the four real arms: `alias_addressed` is `F,F,T,F` both ways | none observed |
| `F4` | one test of one condition | `jack_defects_r95_entry` 34888–34906 | the second `if not l.get("killed_at_bound"):` test and its duplicated branch | `fold-equivalence.json:F4` — `all_equal: true` for both `killed_at_bound` values: identical `failures` list **and order** (`rc, stall_cycles, cb, xrun_cbs`) and identical `coverage_blocked` | none observed |
| `F5` | dead computation | `_jack_r95_meta_rows` 33667 | `rec["row_count"] = len(rows)` | AST store/load scan: **0 readers** (`has_reader: false`; the only occurrence in the fixture is the writer); literal fallback agrees — the rec is discarded by both callers, which read `rows` only | none; `rows` itself is untouched |
| `F6` | dead error class | `_JACK_R95_ERR_CLASSES` 33372 | `("jack_r95_no_daemon", r"Could not connect to JACK server")` | **no emitter exists**: the string is absent from `r95jack` (built), `libjack.so.0.3.1608` (`34bbb09a…`), `pw-cli`, `pw-link`, `pw-metadata`, `pw-dump`, `pw-play`, `pw-record`, `pw-jack`, `pacman`, `nm`, `libpipewire-0.3`, and a broader `/usr/bin/pw-*` + `libpipewire*` scan (0 hits each; `strings -a`); the fixture prints `{"mode":"open","ok":false,"status":17}` with **empty stderr** on all three no-daemon shapes tested (`PIPEWIRE_RUNTIME_DIR=/nonexistent`, `PIPEWIRE_REMOTE=nonexistent`, `PIPEWIRE_RUNTIME_DIR=/tmp`). Dynamic: `_jack_r95_errclass(real no-daemon bytes)` = `[null, null]` **before and after** the fold (`prove-daemonfree.json` / `prove-folded.json`, `all_equal: true` on 10/10 observables), and `_jack_r95_run` on the real fixture returns an identical receipt (`error_class: null`, `exit_code: 3`, same stdout) in both copies (`prove-f6-e2e.json`) | the class was the family's only *name* for "no daemon"; the condition is still fully visible as `exit_code 3` + `{"mode":"open","ok":false,"status":17}` in every receipt. On a hypothetical host carrying **jack2's** libjack the phrase would exist again — the family's declared premise is the opposite (its `a_avail` entry fails if any JACK server binary is present), so the fold is safe on the declared host and is a *portability* loss only |

Retained contract of the folded copy: all 5 entries, all 24 legs, every law
and every armed value, every receipt key except the one dead computation and
the one dead class tuple member; `py_compile` clean; AST diff touches exactly
the intended functions
(`fold-apply.json:changed_top_level_defs` = `_jack_r95_meta_rows`,
`_jack_r95_unload_ns` (new), `jack_addr_r95_entry`, `jack_bytes_r95_entry`,
`jack_defects_r95_entry`, `jack_surface_r95_entry`).

## 6. Candidates held (with the tradeoff that holds them)

| # | candidate | site | why held |
| --- | --- | --- | --- |
| `F1` | delete the fixture's dead `rtprio` mode | `r95jack.c` 411–428 (18 lines) + the mode list in the header comment (line 18) | **No landed caller** (mode census, §4) and its only unique emitted key `samples` is read by no law (its `is_realtime_live`/`cpu_load_live` duplicate `rtprio_poison`'s, and `rtprio_poison` is the mode the landed `d_rtprio_poison` leg runs). Proven mechanically: scratch copy `r95jack-nortprio.c` **compiles with the same flags** and its dispatch census loses only `rtprio` (`rtprio` → `mode:"unknown"` rc 2; `rtprio_poison` still dispatched; `bogusmode` unchanged). **Held because it is a re-measurability tradeoff, not pure weight**: the *scout* ran this exact mode (`corpus/live/r95-scout/probes/r95driver.py:stage_rtprio`, receipt `e_rtprio.json`) and the *boundary* row 9 re-measured the same claim with its own binary (`probes/r95bjack.c`; its receipts `h_rtprio.json`/`q_rtprio.json` carry `"mode":"rtprio_poison"`). Deleting the landed copy removes the family's re-runnable *plain* (unpoisoned) sample arm while the historical provenance (a different 710-line file) stays. Queued only as the **optional** patch `folds-r95s-optional-fixture.patch`; if the round's axes weight re-measurability over line weight, keep the mode. |
| `F7` | delete the `poison_aa_hex` emission | `r95jack.c` 461–467 (7 lines + 2 extra `poison_stack` calls) | It is a **duplicate encoding of the same run's `poison_aa` ints**, and no law reads it — but the **boundary's own analyzer reads it** (`corpus/live/r95-boundary/probes/r95banalyze.py`; the key is in `h_rtprio.json` / `q_rtprio.json`). Deleting it would diverge the landed instrument from the round's historical measurement vocabulary — exactly the "second convention" the seat must not create. **Do not fold.** |
| `B7` | drop `wd=` from `_jack_r95_run`/`_jack_r95_probe`, and the `sig_at`/`sig` branch (`33404`, `33503`, `33442–33446`, plus the always-`False` `fired_sig` / always-`None` `alive_at_sig` receipt fields) | Python, ~10 lines + 2 parameters | No r95 call site passes `wd=` or `sig_at=` (call-site keyword census), so the branch and the two receipt fields are unreachable **inside this family**. Held because it is the **shared r84–r89 helper shape**: r89's `_pwprof_r89_nleg` passes `sig_at=bound_s` and `wd=` through (`29715`, `30303`). Folding it in r95 alone would make this family the odd one out — a second convention for a ~10-line gain. |

## 7. Law-audit notes (no fold; recorded for the verifier)

- **Latent vacuous loop, not a tautology.**
  `for r in (j.get("resolve") or []):` (34092) arms its `found` laws only when
  the fixture emits rows; if `jack_get_ports(c, "r95a", …)` returned nothing the
  loop would silently arm **zero** laws. The sibling `pattern_r95a` band
  (`5..100`, 34084–34085) guards the same pattern and makes this low-risk today,
  but the loop has no non-empty guard of its own. Hardening (adding a count law)
  is an author/verifier move, not a weight removal — reported, not folded.
- **Self-referential premise, not a tautology.**
  `_jack_r95_eq(… "tone peak_i16" …, tone.get("peak_i16"), JACK_R95_AMP_I16)`
  (34532) checks the harness's own generator against the constant it was
  given. It *is* falsifiable in principle (`peak_i16 ≤ amp`, equality only when
  a sample lands within ~0.008 rad of the sine peak); measured here for
  997/48000, 1000/48000, 997/44100 and 500/48000, it holds (16383) in all four.
  Keep.
- **`_jack_r95_errclass` on the unknown-mode path matches the fixture's
  *stdout*** (`R95AJSON {"mode":"unknown",…}`), not a stderr message; that is
  the live half of the table and it is exercised in `prove-folded.json`
  (`["jack_r95_unknown_mode", "unknown"]`).

## 8. Preserved contract (what a landing must not lose)

1. All 5 entries and all 24 legs stay wired in `main()` (`--probe-jack-r95`),
   with the fixed-path family lock and the `r95a_<pid>` namespace.
2. Every armed law and every armed value is unchanged; the folds change no
   expected value, no band, no law name and no law order (`F4`'s failure order
   is proved identical).
3. Every recorded (not armed) receipt field survives except the one dead
   computation (`F5`) and the one dead class tuple member (`F6`) — the
   recorded-not-armed convention itself is untouched.
4. The fixture's **armed** source hash premise is unaffected: `src_sha256` is
   *recorded*, never armed, so `F1`'s optional landing changes a recorded value
   only (and would also make the author report's mode list historical — the
   report stays untouched).
5. Nothing in this report edits another seat's artifacts; the two queued
   patches are the only landable diff.

## 9. Evidence index (scratch, untracked)

| file | what it is |
| --- | --- |
| `shared-tree-entry.sha256` | entry hashes of the two audited blobs (re-verified at exit) |
| `r95-block.py` | the extracted r95 block (lines 33289–35059) |
| `prove_daemonfree.py` / `prove-daemonfree.json` | daemon-free narrow checks on the shared copy (error classes vs real fixture bytes, `nm` export census 168 + absent/present classes, tone peak law, host `settings` clean, JSON reader, scrub) |
| `apply_folds.py` / `fold-apply.json` | the four Python folds applied to a scratch copy, anchors asserted, `py_compile`, AST-locality diff, line delta |
| `fold_equivalence.py` / `fold-equivalence.json` | `F2` textual identity, `F3` truth table + real arms, `F4` control-flow table, `F5` reader scan |
| `prove_folded.py` / `prove-folded.json` | differential: 10/10 daemon-free observables identical shared vs folded |
| `prove_f6_e2e.py` / `prove-f6-e2e.json` | `F6` end-to-end: real fixture through `_jack_r95_run` in both copies, receipts identical |
| `r95jack-nortprio.c`, `bin/r95s_jack_nortprio` | `F1` scratch instrument (build + dispatch census) |
| `bin/r95s_jack` | the unmodified fixture, built with the family's own flags |
| `folds-r95s.patch`, `folds-r95s-optional-fixture.patch` | the queued folds (`F2`–`F6`) and the optional `F1` |
| `blocker-census.txt` | timestamped host census backing §3 (loadavg, `yes` fleet, stuck `pw-dump`s, own-residue check, family lock) |

## 10. Blockers and stop condition

- **Blocker (runtime proof):** the host daemon stall of §3. Not lane-local,
  not repairable from a seat. The queued folds must be re-proved with
  `--probe-jack-r95` on a quiet host before landing; `F6` alone is already
  proved end-to-end here.
- **Blocker (reference proof):** no `lsp` device, so no semantic caller proof
  was available for Python names; AST + literal fallback used and labelled as
  such. The fixture-mode question is the exception, and is decided by a
  complete AST call-site census.
- **Stop condition reached:** the next deletion would harm an axis. The
  remaining weight is (a) recorded-not-armed receipt evidence (`F7`, and the
  recorded fields generally), whose removal costs the receipt axis, and
  (b) helper parameters/branches shared with the r84–r89 families (`B7`),
  whose removal costs the convention axis by creating a second helper shape.
  Beyond `F2`–`F6` the family has no dead path, no unreferenced helper, no
  tautological law and no duplicate authority left that can be removed
  without paying one of those two axes.

**Queued for the integrator: `F2`, `F3`, `F4`, `F5`, `F6`** (patch
`folds-r95s.patch`). **Optional, tradeoff-flagged: `F1`**
(`folds-r95s-optional-fixture.patch`). **Do not land: `F7`, `B7`.**
