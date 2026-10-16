# r85 VERIFIER — wave-B gate on committed `2a49d540` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`),
lane `~/Projects/shokunin/audio-shokunin`, window
**2026-10-16 06:18:20–06:30:02Z**, loadavg **50–61** throughout (load
preferred; every run below ran under it). Target: commit **`2a49d540`**
("r85 author: 87 legs / 5 entries — pactl serial/monotonicity, mix taps
+ solo ref, aplay env, capture lattice, negctl; 3 host-bimodal
realizations armed both ways; 2 green runs"), frozen via `git archive`
— **not** the worktree (a sibling r86 author is live-writing the
worktree fixture, §6). Toolchain receipt-identical to the author's pin:
PipeWire **1.6.8**, WirePlumber **0.5.17**, pactl/libpulse
**17.0-98-gb096**, alsa-utils **1.2.16**, Python **3.14.7**, NumPy
**2.5.3** (`runs/toolchain.txt`). **No tracked writes by this seat, no
commits, no pushes, no `set-default-*`; every seat artifact under
`corpus/live/r85-verifier/`; all scratch under
`TMPDIR=~/Projects/shokunin/tmp` (`/tmp` at 76 % quota).**

## 0. Verdict

**VERIFIED — wave-B gate PASS.** On the frozen `2a49d540` tree, two
green replays (r85v1, r85v2b) reproduce the author's committed verdict
surface **exactly** — **0 exact / 0 named / 0 entry-level diffs** against
**both** author runs on all 87 legs — and an independent 101-law checker
passes on all four receipts (author ×2, verifier ×2). The three
host-bimodal realizations are **armed both ways**: an executed probe of
the committed verdict slices shows each non-observed realization passing
and each hostile shape failing (latebind and cdup cleanly; sd_prop with
one vacuous corner, F2). One replay (r85v2) died on a **foreign**
non-string `node.name` — inherited r78/r84 fragility, mechanism
reproduced offline, custody preserved, re-run green (F1).

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive 2a49d540` | tar sha256 `85767cc3…`, 1 592 238 080 B; 43 640 files / 11 657 dirs / 0 symlinks; file-set symdiff vs `git ls-tree -r 2a49d540` = **0** | PASS |
| fixture identity | committed blob | sha256 `714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2` — identical to the author's declared source pin, before and after all runs | PASS |
| py_compile | clean | rc=0 (inside frozen tree) | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical | PASS |
| `--probe-pactlmon-r85` ×2 under load | failures `{}` | r85v1 `06:18:47–06:20:35Z` rc=0 `{}`; r85v2 `06:22:22–06:23:07Z` **rc=1 crash** (F1, foreign node); r85v2b `06:26:46–06:28:34Z` rc=0 `{}` | PASS (v1, v2b) |
| 87 legs × 5 entries ×2 | all legs, no skips | 87/87 per green run (40/7/6/17/17); no `blocked`/`coverage_blocked` | PASS |
| verdict-surface stability | deterministic | v1 vs author run1 = **0/0/0**, v1 vs run2 = **0/0/0**, v2b vs run1 = **0/0/0**, v2b vs run2 = **0/0/0**, v1 vs v2b = **0/0/0**; calibration author1 vs author2 = **0/0/0** | PASS |
| independent law re-derivation | armed law set | **101 laws, 101 PASS** on author run1, author run2, r85v1, r85v2b | PASS |
| three host-bimodal realizations | either-way, not absorbing | executed committed-slice probe: 17 cases, 16 exact; latebind PASS, cdup_cap PASS, sd_prop PASS-with-hole (F2) | PASS-with-finding |
| custody/teardown | zero residue | `sinks_gone`/`sources_gone` all true + `own_nodes_after: []` in every entry of every green run; post-state: **0** `r85a_*`/`r85v_*` modules/sinks/sources/nodes; default sink/source unchanged | PASS |
| independent spots | ≥5 shapes | **12 shapes, 12/12 green** (final battery) — own code, own `r85v_*` namespace | PASS |
| zero tracked writes | none | this seat wrote only under `corpus/live/r85-verifier/`; the worktree fixture's ` M` is the **r86 author's** uncommitted block (disclosed, §6) | PASS (for this seat) |

## 1. Frozen tree

- `git archive 2a49d540 -o …/r85v-tree.tar` → sha256
  `85767cc386f73ae9f7a46bb13d5c3ddfdae6145da27bbe2f025d8842e349e709`
  (1 592 238 080 B); extracted to `corpus/live/r85-verifier/tree/`
  (gitignored regenerable path per `corpus/.gitignore`
  `live/**/*tree*/`): 43 640 files / 11 657 dirs / 0 symlinks; symdiff
  vs `git ls-tree -r 2a49d540 --name-only` = **0 lines**. The tar was
  deleted after extraction; its sha is pinned in
  `runs/tree-tar-sha.txt`.
- Fixture inside the tree: sha256 `714564a3…` (blob `0b49d554…`) —
  unchanged after 3 normal/probe runs + 5 spot batteries.
- Commit shape: `+2178 / −3` in `corpus/fixtures/measure_audio.py`; the
  3 deletions are exactly the declared wiring lines (mutex-sum `if
  sum([…])`, `mode` ternary, `suffix` ternary). Author receipts are
  byte-identical to canon: run1 == `20261016T061227150495Z` (`69a96ad6…`),
  run2 == `20261016T061417931113Z` (`98267a0f…`) — no citation drift.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 06:18:45→06:18:47 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r85v1 | 06:18:47→06:20:35 | `… --probe-pactlmon-r85` | 0 | `{}` | `7909147afb8051e9690d2244081fa728c2c7be2a525357fcb13b9d723b134daa` |
| r85v2 | 06:22:22→06:23:07 | `… --probe-pactlmon-r85` | 1 | **crash** (F1; no receipt; started when the reviewer's queued run released the lock) | — |
| r85v2b | 06:26:46→06:28:34 | `… --probe-pactlmon-r85` | 0 | `{}` | `5e8ed9c712cd02f44bb3266816d6f8c7668d419b6b7d75acf3ef64551d731ece` |

- Leg census per green run: **87 legs / 5 entries** — exact match to the
  committed count (entry split 40/7/6/17/17).
- r85v1 headline values: solo ref `l_a=r_b=8190.7` (bleed 0.0);
  mixdup 0.292 `partial`; mixclip peak 32768 / rail 0.2335 / spur 1921.8;
  serials `237432→237446→237460` (module idx 536870916 recycled ×3);
  `g_lead0` rc1 `pa_get_info_noent`, `armed: false`; cap_loss posts
  `froze`×2; `latebind=late_bound`, `cdup_cap=serial_monitor_bypass`,
  `sd_prop=bind_killed_then_default` (sd gone), `t_sinkname=bound_source`.
- r85v2b: same armed surface; all five entry heads record
  `fixture_runs: 0`, no foreign clients (`host_is_quiet: true`);
  cap_loss posts `grew_content`×2 (2048 frames each).
- TMPDIR `~/Projects/shokunin/tmp` for every run and spot.

## 3. Verdict-surface stability

Tiered comparator (`runs/surface.py`, r83/r84 convention): **exact** =
rc/signal/error_class/error_hit/killed_at_bound/expect/got/armed/
alive_at_end/module_alive/source_alive/skipped/recycled + normalized
link shapes (node names, port names) + unload records + structural
booleans; **named** = volume-percent rows; **analog** = timings, sizes,
amps, indices, serials, pids, paths, module ids, link `state`.
Normalization collapses pid runs, `r85a_/r85v_` namespaces, object
ids/serials/module indices, hex ids, tmp paths. `realization` fields are
excluded from the exact tier and reported separately (the three bimodal
sites + mix phase realizations are volatile by design; `runs/laws.py`
re-derives their armed bounds).

Calibration: **author run1 vs run2 = 0 exact / 0 named / 0 entry-level**
— the comparator pins exactly the surface the author's own two green runs
agree on. Then:

- r85v1 vs author run1 **0/0/0**; vs author run2 **0/0/0**.
- r85v2b vs author run1 **0/0/0**; vs author run2 **0/0/0**.
- r85v1 vs r85v2b **0/0/0**.
- Realization-only diffs across the four receipts (all in the documented
  volatile classes, none in an armed verdict):

| run | latebind | cdup_cap | sd_prop | sd gone | t_sinkname | cap_loss_0 / _1 post | mixdup / mixdelay / mixinv |
| --- | --- | --- | --- | --- | --- | --- | --- |
| author1 | late_bound | serial_monitor_bypass | bind_killed_then_default | true | bound_source | grew_content / froze | coherent_2x / partial / slipped |
| author2 | late_bound | serial_monitor_bypass | bind_killed_then_default | true | bound_source | grew_content / grew_content | partial / cancelled / slipped |
| r85v1 | late_bound | serial_monitor_bypass | bind_killed_then_default | true | bound_source | froze / froze | partial / partial / slipped |
| r85v2b | late_bound | serial_monitor_bypass | bind_killed_then_default | true | bound_source | grew_content / grew_content | partial / partial / slipped |

Serials strictly increasing in all four runs (`235347…`, `236361…`,
`237432…`, `241163…`); module index recycled identically ×3 in every run.

**Independent law checker** (`runs/laws.py`, verifier-owned logic, no
fixture import) re-derives 101 armed laws from the receipt data: addr
lattice (serial/object.id/`0`=live-default/`""`/parse edges/move
name+serial+bogus/collision/serial monotonicity), mix (tap-link
validated ×6, solo window, zero bleed, mix2 amplitude/bleed/topology,
dup/delay/inv linear bounds, clip rail/fraction/spur), aplay env
(node/props/conflict props-win/serial/bogus/none), capture (baseline
bind+content, `t_src*` source binds, `t_sinkserial` monitor bypass,
`t_sinkname` never-monitor, prop forms, loss ×2: linked, no re-link,
alive, unload rc0, flush ≤16384, growth ceased; prop-loss default-monitor
re-link; sd idle/record/parec/prop/pwlink; latebind), negctl (13 unit
rows + live controls + SIGKILL discriminator). **101/101 PASS on all
four receipts** (`runs/laws-author1.txt`, `laws-author2.txt`,
`laws-r85v1.txt`, `laws-r85v2b.txt`).

## 4. The three host-bimodal realizations — either-way pinning

`runs/armprobe.py` extracts the **committed** verdict slices verbatim by
anchor from the frozen tree and `exec`s them against synthetic `legs`
dicts (mutation-style unit probe of the verdict logic; no live audio):
latebind slice 20 lines (sha `b3f3f2c6c031bb29`), cdup_cap 32 lines
(`b50ba501d5b8d668`), sd_prop 31 lines (`3aa3ae1b36931681`). 17 cases:

- **latebind — SUSTAINED.** `late_bound` (observed), `stalled`
  (boundary-side), `refused` all append **no** failure; hostile
  `foreign_bind` and dead-rc0 `other` each append their failure.
- **cdup_cap — SUSTAINED.** `serial_monitor_bypass` (observed),
  `name_shadow_bound` (boundary-side), `stalled`, `refused` all pass;
  hostile `foreign_monitor` and `other` fail. The extra invariant
  (`monitor_*` links may only come from the serial holder) holds.
- **sd_prop — SUSTAINED with one hole (F2).** Both measured realizations
  (`bind_killed_then_default`, `clean_default_fallback`) pass; hostile
  non-monitor links, non-default monitor, and no-links-with-live-trap
  all fail. **But** a synthetic “no links + trap dead” leg appends no
  failure and is labeled `bind_killed_then_default` — see F2.

Live corroboration: the boundary report measured the other side of all
three (no-link stall 6/6, name-first digits resolution, clean fallback);
this host realized the author side in all four receipts.

## 5. Independent spots (`spot/spots.py`; own code, no fixture import)

Final battery **12/12 green** (`spot/spots5.out.txt`); own `r85v_<pid>`
namespace, own tone/spectral code, family flock taken for the whole
window:

| spot | shape | measured (final battery) |
| --- | --- | --- |
| s1 | pactl serial-vs-object.id, name equivalence, `0`, `""` | name rc0 = serial rc0 (100 % = 100 %); object.id rc1; `0` → 40 % = `@DEFAULT_SINK@` 40 %; `""` → `Operation failed: Invalid argument`; `235_xxx` rc1 |
| s2 | pw-cli namespace inversion | `info <id>` rc0; `info <serial>` rc0 + `unknown global` |
| s3 | serial monotonicity + index recycle | `242657→242667→242677` strictly increasing; module idx 536870924 ×3 |
| s4 | move-sink-input name/serial/collision | stream `242686`: sink `242632→242640→242632`; a sink **named** `242632` alive (idx 242700); `move-sink-input <stream> 242632` rc0 lands on the **serial holder** 242632, not the name 242700 |
| s5 | mix tap + solo reference | tap links validated (monitor_*); solo `l_a=8191.3 r_b=8191.4`; 2-stream both tones `8191.4`; bleed 0.0; 4 edges → 2 `playback_*` ports |
| s6 | aplay env targeting | NODE → publishes + links the named sink; conflict props-win (no link to the NODE sink); serial-in-props resolves; bogus NODE publishes bogus `target.object` + silent default fallback (SILENCE file only) |
| s7 | capture `--target` lattice | source name/serial → `capture_*`; sink serial → `monitor_*`; sink name noprop → **never** `monitor_*` (`bound_source` realization, capture_* of the live remap); prop → default monitor |
| s8 | loss law | links die (post 0), never re-form, process alive, unload rc0, growth ceased, `post_frames 0` |
| s9 | Audio/Source self-destruct | idle ≥3.6 s survives; pw-record bind kills module at **0.07 s** (0.08 s in an earlier battery) |
| s10 | live negative controls | `""` → Invalid argument; rc-0 `unknown global`; `pactl info`/`pw-dump` clean; SIGKILL'd pw-play → SIGKILL, no error class |
| teardown | residue | `leftover=[]` |

Disclosed iterations: the early batteries had **harness bugs** (s4
looked up the stream by a tag the short listing never carries; s6 sampled
the graph after `aplay` had exited; s4's tone was shorter than the two
moves; one s4 gate was over-strict on a redundant node lookup). All
iterations are retained (`spots.out.txt` … `spots5.out.txt`); the last
two batteries are 12/12, and the final one carries the complete collision
evidence (named sink alive, digits move → serial holder).

## 6. Custody, contention, host state

- **Custody**: every green receipt carries `sinks_gone`/`sources_gone`
  all-true and `own_nodes_after: []` in all five entries; module unloads
  are name-verified by the module's own `sink_name=`/`source_name=`
  arg. Post-state (06:30:02Z): **0** `r85a_*`/`r85v_*` sinks, sources,
  modules or nodes; default sink `…SPDIF__sink.29` / default source
  `…Line__source.29` unchanged from pre-state. The r85v2 crash left **no
  residue** (the entry's `finally` unloaded every module before the
  witness reader itself raised — verified by the post-crash census).
- **Contention ledger** (all foreign work observed read-only, never
  touched):
  - **r85-reviewer replay** (pid 2599248, own frozen tree of the same
    commit) `06:19:07→06:22:22Z`, 87 legs, `failures {}` green; it held
    the same-TMPDIR family lock between my r85v1 and r85v2 (my r85v1
    receipt records it as `fixture_runs: 1` in 3 entry heads; my r85v2b
    saw `fixture_runs: 0`).
  - **r86 authoring seat** (`--probe-pwctl-r86`, `r86a_ns_2661839`,
    `r86a_tmp_2606500` pw-cli set-param mix probe) live from ~06:21Z;
    it is also writing the **worktree** fixture (uncommitted
    `+1758/−3` vs `2a49d540` — an appended r86 family; the r85 family
    region is byte-identical to the frozen copy, checked). This is the
    only reason `git status` shows the fixture as modified; **this seat
    wrote nothing outside `corpus/live/r85-verifier/`**.
  - r85-critic / r85-scribe / r85-simplifier seats: read-only audits /
    offline proofs in-window; ambient loadavg ~50–61.
  - Disclosed r84 leftover `r84a_probe_548706` sink still present,
    SUSPENDED, untouched.
- **Interference by this seat**: 3 probe runs + 1 normal run from the
  frozen tree; 5 spot batteries on probe-owned `r85v_*` null sinks (all
  unloaded name-verified, `leftover: []`); the only default-sink audio
  was `aplay` SILENCE legs (s6) and the prop-form default-monitor
  captures — no tag tone ever landed on the shared sink.

## 7. Findings (ranked)

- **F1 (non-blocking; robustness carry to the fold) — the r85 family
  inherits the r78/r84 non-string-`node.name` crash.** My r85v2 replay
  died mid-`aplayenv` with `TypeError: argument of type 'int' is not a
  container or iterable` (`_alsapw_r84_cands`, fixture line 19140) and
  the `finally` teardown then died with `TypeError: '<' not supported
  between instances of 'int' and 'str'` (`_playback_r78_node_names`,
  line 6153) — both caused by one **foreign** live node whose
  `node.name` property was not a string (gone by the next census;
  producer not captured). `runs/crash-repro.py` reproduces both errors
  offline with a crafted pw-dump (no host mutation) and shows the
  all-string control path is clean. Neither helper is modified by
  `2a49d540`, but the commit adds new call sites (r85 teardown calls
  `_playback_r78_node_names`; the new aplayenv entry calls
  `_alsapw_r84_aplay_leg` → `_alsapw_r84_cands`). Effect: a co-tenanted
  host can kill the entry (and the witness reader) mid-run — no receipt
  is written, though the teardown's unload loop runs first so custody is
  preserved. Suggest a type guard (`isinstance(name, str)`) in both
  helpers, or an explicit `coverage_blocked` path. Not an encoded-law
  defect; all four green receipts are unaffected.
- **F2 (minor; arm hole) — `sd_prop`'s dead branch accepts a leg that
  measured nothing.** The verdict slice labels any no-link leg with a
  dead trap `bind_killed_then_default` and appends no failure
  (`not plinks and not sd_gone` only fires on the live-trap side). My
  executed probe confirms a synthetic “no links + trap dead” leg passes
  (and would be indistinguishable from “bound, killed at bind latency,
  no sample ever captured”). Both *measured* realizations pass and all
  hostile shapes fail, so the either-way pinning claim holds; the corner
  is vacuous, not absorbing a hostile shape. Suggest an explicit
  `dead_unbound` realization (or requiring a ≥1-link witness on the dead
  branch). Recorded by the labrat's advisory trace and re-run as an
  executed case by this seat.
- **F3 (hygiene, no behavioral effect) — two dead locals in the r85
  block.** `sers = [s for s in entry["serial_cycles"]["serials"] …]`
  (line 22738) is never used (the arm uses `serials`); `want_node` in the
  `t_srcname/t_srcserial/t_srcid` loop (line 23491) is never read — the
  arm checks the `capture_*` port class only (which is sufficient at
  lattice time, when the only live remap source is `vsrc`).
- **F4 (corpus hygiene, observation) — the canonical runs dir also holds
  two earlier `pactlmon-r85` runs** (`20261016T060244900131Z`, 70 legs,
  red; `20261016T061003728457Z`, 70 legs, green) from a pre-correction
  source revision (their failures name the old `u_move_parse` expectation
  and the old strict arms). The committed report cites only the two
  87-leg runs, which are byte-identical to canon — no citation defect;
  noted so a later reader does not mistake the older receipts for the
  committed source.

## 8. Evidence map (`corpus/live/r85-verifier/`, 53 files / 5 854 641 B
excluding the gitignored tree; `manifest.json` + `manifest.sha256`)

`runs/toolchain.txt`, `pre-state.txt`, `post-state.txt`, `commands.log`,
`window-start.txt`, `tree-tar-sha.txt`, `ls-tree-2a49d540.txt`,
`tree-files.txt`, `fixture-sha.txt`, `receipt-shas.txt`,
`normal.stdout.json`/`normal.stderr.log`,
`r85v1.stdout.json`/`.stderr.log`/`.receipt.json`,
`r85v2.stdout.json`/`.stderr.log` (crash), `r85v2b.*` (+ receipt),
`surface.py` + `surface-*.txt` (calibration, v1/v2b vs both authors,
v1-vs-v2b), `laws.py` + `laws-*.txt`, `armprobe.py` + `armprobe.txt`,
`crash-repro.py` + `crash-repro.txt`;
`spot/spots.py`, `spot/spots{,2,3,4,5}.out.txt` + `.err.txt`;
`labrat/` (empty — see §10); `tree/` (gitignored `git archive`
materialization holding the receipts as written by the fixture).

## 9. Risks / blockers

- **None blocking.** The landing verifies on the frozen tree; both green
  replays are surface-identical to both author runs; the 101-law set
  passes on all four receipts.
- Carries for the wave-B fold: **F1** (foreign non-string `node.name`
  kills an entry and its witness reader; type-guard the two r78/r84
  helpers), **F2** (`sd_prop` dead-branch vacuous corner), **F3**
  (dead locals).
- Residual uncertainty: the producer of the transient non-string
  `node.name` was not captured (gone at the next census) — F1 is proven
  as a mechanism, not attributed to a named foreign client.
- Disclosed leftovers by this seat: none on the live host; the 1.6 GB
  frozen tree is left as regenerable receipt material (gitignored) for
  the orchestrator to keep or prune.

## 10. Labrat disclosure

The single permitted `probeParent` labrat was dispatched once, read-only,
for a bounded “either-way pinning” hypothesis (extract the three verdict
slices verbatim, `exec` them against synthetic legs). Its substrate
exposed **no shell/exec/write tooling**, so it returned an
**analytical** line-level trace with zero artifacts (`labrat/` is
empty) and explicitly labelled itself untested. This seat then re-ran
the same case matrix as an **executed** probe (`runs/armprobe.py`,
§4) — the executed result confirms the labrat's trace, including the
F2 corner. No other descendant was spawned.
