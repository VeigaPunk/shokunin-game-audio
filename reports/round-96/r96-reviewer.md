# r96 reviewer — pulsecli landing `7358f13b`

**Seat.** UFO-FSD reviewer (recommendation only; the canonical Rust judge is
the only Pareto judge). Nothing in this file was committed; no file under
review was edited.

**Target.** `7358f13b` ("r96 author: pulsecli PulseAudio-native client API
(5 entries/178 legs, +2358/-3)") — `corpus/fixtures/measure_audio.py`,
`corpus/fixtures/pulse_r96_probe.c`, `reports/round-96/r96-author.md`,
`reports/round-96/r96-integrate.md`.

**Method.** All review claims were re-derived from the committed blob
(`git show 7358f13b:<path>` hashed before use), the author seat's receipts, my
own cheap live probes, and deterministic evaluation of the committed
predicates. The author/boundary/scout/critic/verifier/integrate reports were
read **as data** (artifact-trust rule) — findings below rest on bytes,
receipts, and my own probes, never on another report's assertion.

**LSP device: unavailable in this dispatch.** No `lsp` tool is exposed to this
seat and no language server is configured for this repository (Python fixture
+ C fixture + reports; there is no server to answer `status`/`references`/
`definition`/`diagnostics`). Caller/definition checks were therefore done by
hashed byte extraction and exact-text inspection of the committed blob. No
semantic-server result is claimed anywhere in this report, and no empty cold
result is treated as absence.

**Receipts location (dispatch path note).** The dispatch names
`../audio-shokunin-wt-r96/corpus/live/r96-author/`; from the repo root that
resolves to a path that does not exist. The receipts are a **linked worktree
nested inside the repo** (`audio-shokunin-wt-r96/`, `.git` →
`.git/worktrees/audio-shokunin-wt-r96`, HEAD `5755be5b`), i.e.
`audio-shokunin/audio-shokunin-wt-r96/corpus/live/r96-author/`. All receipts
cited below were read there. The two required green runs are in that
worktree's `corpus/live/runs/20261016T093539457589Z-pulsecli-r96/` and
`...T093802929935Z-pulsecli-r96/`.

---

## 0. Re-derivation summary (author claims vs bytes + receipts)

| claim | re-derived | verdict |
| --- | --- | --- |
| 5 entries, 178 legs = 41/27/68/20/22 | receipt leg counts exact in both runs | **CONFIRMED** |
| 0 failures, both runs | `failures {}` in both receipts and both `run{1,2}.stdout.json`; no leg carries a non-empty failure list | **CONFIRMED** |
| only non-green lines = 2 named coverage blocks | `coverage_blocked` exists in exactly one entry (`pulsecli_cork_r96_probe`, 2 entries: `e_native_corked rep 1/2`) in both runs | **CONFIRMED** |
| measured bytes == landed bytes | r96 block (`# r96:`→`def main()`) 2316 lines, sha256 `e1422a13…` **identical** in the worktree (frozen `b545283e…` whole file) and the commit; span 41471–43787 = `be60f1ba…` (2317 lines) and dispatch 44554–44590 = `75bc7fdd…` reproduce the integrate report's numbers | **CONFIRMED** (whole-file frozen sha ≠ merged sha: see note N1) |
| insertion-only, no prior row modified | 6 hunks: +2317 block span, +37 dispatch, +1 argparse row, 3 replaced wiring lines = +2358/−3 exactly; no prior-round row touched | **CONFIRMED** |
| wiring: flag ×1, mutex token ×1, ternaries ×1 with r96 first, lock held to exit | lines 43922 / 43932 / 45241 / 45261 / 44580 | **CONFIRMED** |
| 12 published attribute rows exact | all 12 table rows reproduce `predicted == measured == table` in **both** runs (I re-evaluated all 12 pairs programmatically) | **CONFIRMED** |
| env beats flag in both orders | `t_env100_flag250` → 6720, `t_env250_flag100` → 13920 (both runs) | **CONFIRMED** |
| s24le falsifies a mask reading; `SPA_ROUND_DOWN/UP` modulo form | `_pulsecli_r96_round_down` = `num - (num % value)` (line 41888+) | **CONFIRMED** |
| `f32le` armed INVALID (rc 1 `Invalid sample specification`) | receipt: rc 1, class `pulse_bad_spec`, `error_hit` exact | **CONFIRMED** |
| cork/trigger/prebuf numbers | `e_cork` 71677 ×2; `e_trigger` 0/peak 0 ×3 with **live** taps (156672 frames); `e_prebuf_zero_slow` 2752 ×3; `e_prebuf_default_slow` 57341; `e_prebuf_zero_fast` 55550; `e_record_cork` peak 196608 / drained 262144; `e_latency_query` rc −16 on all 10 calls/rep; `e_subscribe` 1 change after uncork / 2 before / 1 new (foreign 40 and 24) | **CONFIRMED** |
| `late_attr_census` 0/66, `capture_miss_census` 3/3 refused 0 hung, `b_host_bogus` ≥ 2 s floor | receipts agree (7.81/8.00 s in run 1) | **CONFIRMED** |
| instrument source `fe2c1683…`, binary `c3fc4cef…` | `client_build` in both green receipts; worktree C fixture hashes `fe2c1683…` | **CONFIRMED** |
| teardown: `sinks_gone` true, `own_nodes_after []` | every entry, both runs; live `r96a` census now 0 modules / 0 sinks / 0 sink-inputs / no processes | **CONFIRMED** (weak-timed) |
| the landing survives later rounds | main worktree's r96 block (2316 lines) hashes `e1422a13…` = committed block | **CONFIRMED** |

---

## 1. Findings by severity

### R1 (HIGH) — `b_info_s_after_subcmd` is a non-discriminating green; the law it encodes is false — **critic C1 confirmed, re-derived independently**

**Counterexample (my probes, this host, pactl 17.0-98-gb096, no listener on
4713 — `ss -ltn` clean):**

```
$ pactl info -s tcp:127.0.0.1:4713     → rc 0, "Server String: /run/user/1000/pulse/native"
$ pactl -s tcp:127.0.0.1:4713 info     → "Connection failure: Connection refused"
$ pactl info -s ''                     → rc 0, default server string
```

A `-s` placed **after** the subcommand is silently dropped. The committed arm
is `_srv_leg("b_info_s_after_subcmd", 2, ["pactl","info","-s",socks],
_pulsecli_r96_env(), 0, None)` at lines 42519–42521, where `socks` is the
**entry's own resolved default socket** (`pulse_server.server_string`,
lines 42350–42356; receipt: `/run/user/1000/pulse/native`). The arm therefore
cannot distinguish "global option honored" from "option dropped": both yield
rc 0 and the same server string, and the receipt's recorded
`b_info_s_after_subcmd__r1/r2` (rc 0, default `Server String`) is the same
value under either hypothesis. The boundary report's inherited claim
("`pactl info -s <server>` … works `rc 0` 2/2", `r96-boundary.md` §3) is
false in the discriminating sense; the landing arms it as rc 0.

**Smallest safe correction (host-state-independent).** Re-word the law to
"a post-subcommand `-s` is IGNORED" and make the arm discriminating on the
**resolved** server: argv `["pactl","info","-s","tcp:127.0.0.1:4713"]`, armed
as rc 0 **and** stdout `Server String:` == `socks`. That moves when the option
is honored (a different version/listener prints the TCP string or refuses)
without depending on port 4713 being dead. The critic's alternative
(dead-server argv with expected rc 1) works but imports the C6/R6 host-state
dependence.

### R2 (HIGH) — the two negative capture arms admit a dead tap; the report's "a tap that never links is a leg failure" is false for `e_prebuf_zero_slow` — **critic C2 confirmed by deterministic evaluation of the committed predicates**

**Counterexample.** Committed predicates:

- `_check_trigger` (43419–43424): fails iff `st.get("nonzero_frames") != 0 or
  st.get("peak") != 0`.
- `_check_prebuf_zero` (43445–43450): fails iff
  `(st.get("nonzero_frames") or 0) > 12000`.

Evaluated on the three witness shapes (`_pulsecli_r96_capture_stats`, 42069,
returns `{None,None,None}` on an unreadable WAV; `{0,0,0}` on a valid empty
WAV):

| witness shape | `e_trigger` | `e_prebuf_zero_slow` |
| --- | --- | --- |
| live-silent (real measurement) | PASS | PASS |
| empty valid WAV (dead tap) | **PASS** | **PASS** |
| missing WAV (reader failure) | RED | **PASS** |

`tap_exit_code` is written once (`rec["tap_exit_code"] =
_pulsecli_r96_kill(tap)`, 43304) and **never read** (`grep -c` = 1); no arm
consults `frames`. So a tap that links but captures nothing satisfies both
negative laws, and a tap that never links still satisfies the stall law —
the exact "empty cold result as absence" shape the author's own §2.1 rule
forbids, and directly contrary to the author's §7 claim ("a tap that never
links is a leg failure (not a silent pass)").

**No recorded green is false today:** both green receipts carry live taps for
these legs (`e_trigger` frames 156672/nonzero 0 ×3; `e_prebuf_zero_slow`
frames 192000/nonzero 2752 ×3). The defect is falsifiability, not measurement.

**Smallest safe correction.** One liveness floor in `_playback_leg` (or in the
two checks): treat `frames is None or frames < 0.5 * tap_frames` as a NAMED
coverage block (not a red), and arm the tap's own `-n`-bound success shape
(`tap_exit_code == 1`).

### R3 (MEDIUM) — witness readers are not hermetic; witness and subject can split servers — **critic C3 confirmed by reading**

`_pulsecli_r96_pactl_json` (41829) and `_pulsecli_r96_short_rows` (41839) call
`subprocess.run([...], capture_output=True, timeout=12)` with **no `env=`**,
while every measured leg goes through `_pulsecli_r96_env()` (which drops all
inherited `PULSE_*`). With a foreign `PULSE_SERVER` in the harness env, every
row/link/sink-index witness can be taken from a different server than the
client under test → false reds / spurious blocks (not false greens). The
author's §1 hermeticity claim holds for the legs, not for their witnesses.

**Smallest safe correction.** `env=_pulsecli_r96_env()` in both helpers (two
lines). The inherited readers used by the entry heads
(`_capture_inventory`, `_playback_r78_node_names`, `_pactlmon_r85_graph`, …)
are outside this diff — a named follow-up, not folded here.

### R4 (MEDIUM) — the `p_malformed` "no stream was created" witness is dead; the `t_f32le_invalid` recorded `row` looks like a witness and is not — **critic C4 confirmed**

`_pulsecli_r96_row(what, pid)` (41869) matches only a row whose
`application.process.id == str(pid)`. The guard at 43135 asks for pid `0`, so
it can essentially never fire for a stream created by the leg; and
`_bad_spec`'s `leaf["row"] = _pulsecli_r96_row_view(_pulsecli_r96_row(
"sink-inputs", 0))` (43000) records `null` in both green receipts. The rc-1 +
`pulse_invalid_property` half of the arm is discriminating and unaffected.

**Smallest safe correction.** Record the child pid in `_pulsecli_r96_run`
receipts and assert `_pulsecli_r96_row(what, pid) is None`; or census
sink-input indexes before/after the leg.

### R5 (MEDIUM-LOW) — `t_proc_lat_b` is a byte-equivalent duplicate cell; "16 flag/env/frame cells" is 15 cells / 14 distinct predictions — **critic C5 confirmed**

`_attr_leg("t_proc_lat_a", 2, latency_ms=100, process_ms=5)` and
`_attr_leg("t_proc_lat_b", 2, latency_ms=100, process_ms=5, extra=())`
(42979–42981) are the same request — `extra=()` is the default; the receipts
show identical argv and identical predictions. `t_f32_100` ≡ `t_stereo_100`
(13440/9604/3840/1440, both frame 4). So the 178-leg census contains 2
duplicate legs and the prose cell count is overstated by one.

**Smallest safe correction.** Drop `t_proc_lat_b` (census 176) or re-purpose it
to a genuinely distinct cell, and update the "16 cells" prose.

### R6 (LOW) — the tcp-4713 arms are host-state, not client laws, and this is undisclosed

`b_tcp_refused`, `b_tcp6_refused` and `b_env_loses_to_flag` (42495–42518) all
assert "nothing listens on pulseaudio's default TCP port 4713" (true now, and
in the receipts). A sibling lane that starts a private pulse on 4713 reds them
loudly — and would mask the flag/env precedence claim behind a connection
success. The author's §7 risk list does not name it.

**Smallest safe correction.** Pre-check the port and block the leg by name if a
listener exists (the entry already uses this fail-closed pattern for the
`a_pacmd_*` index-0 guard), or move the precedence arms to a socket path that
is dead by construction.

### R7 (LOW) — report prose drift (verifier C7 class, extended)

All report-only, none semantic; a verifier counting from prose will
false-alarm:

| report text | measured |
| --- | --- |
| §4.4 "props … (12 legs)" | 20 |
| §4.5 "cork … (24 legs)" | 22 |
| §3 "all 13 published boundary rows" | 12 rows listed, 12 reproduce |
| §1 "the r96 block (+1 607 lines)" | block 2316 lines; commit +2358/−3 |
| §4.5 "`Corked: false` while the node is `running`" | receipt `corked_field: true`, `projection_agrees: false` → named block; the committed code arms only the no-`pulse.corked` class (43683+) |
| §2.2 "Live census: 25/66 … (a receipt re-scan puts 27/66 …)" | §5 and the receipts say `late_attr_census 0/66` in both green runs |
| §2.1 "the row→link gap measured 0.004–0.086 s" | green receipts: within-leg gap 0.000–0.001 s (`row_t`/`link_t` 0.086–0.103 s run 1, 0.086–0.089 s run 2); 0.0–0.086 s is the **dev** run's gap (`dev-target.json`) |

### R8 (LOW) — instrument dead knobs

`pulse_r96_probe.c` accepts `--server`, `--amp`, `--attr-mode`
(committed C lines 138/139/148) but the harness never passes them
(`--attr-mode` does not occur in `measure_audio.py`). Dead surface; `--attr-mode
none` would bypass the buffer-attr path if a future family reused the
instrument.

### N1 (NOTE) — frozen-sha labeling (no action beyond one sentence)

The author report's §5 "Frozen bytes" sha for `measure_audio.py` is
`b545283e…`, which is the **worktree** file, not the landed blob
(`97ed1b1c…`). This is fully disclosed and mapped in `r96-integrate.md`
("merged sha … ≠ the WT file's … (expected)"), and I verified the family bytes
are identical across the two (`e1422a13…` block, `be60f1ba…` span). A reader
who hashes the commit against the author report's sha gets a mismatch; the
landing identity for the family is the span hash. Recommend the author report
carry the span hash next to the frozen sha.

### N2 (NOTE) — unverifiable dev narrative

The §2.1 story ("the first dev run … 8 rows carried `sink = 4294967295`") is
not verifiable from the surviving receipts — `dev-target.json` contains 0
occurrences of `4294967295` (it is a later dev run, post-link-law). The law it
forced is present and effective in the committed bytes (`_pulsecli_r96_link_ok`
41879, used at 42014; 24/24 target legs `polls=2`, `linked: true` in both green
runs). No action; the narrative is superseded history.

---

## 2. Cross-check of the critic's C1/C2 (asked explicitly)

- **C1 — CONFIRMED**, and re-derived with my own probes rather than taken on
  the critic's word (see R1). Two refinements to the critic's write-up:
  (a) the arm's *prose* in the landing report is vague ("the global option
  after the subcommand") — the **false law is inherited from the boundary
  report** and encoded as the arm's rc-0 expectation; (b) the critic's
  "smallest safe correction" (dead-server argv, expected rc 1) imports the
  R6 host-state dependence; the resolved-server-string form above avoids it.
- **C2 — CONFIRMED** on the committed predicates (see R2), including the
  asymmetry the critic noted: a *missing* WAV reds `e_trigger` but leaves
  `e_prebuf_zero_slow` green, and an *empty valid* WAV passes both. I did not
  re-run the critic's stub mutation (that would require re-running the live
  battery); the predicate evaluation above is deterministic on the committed
  bytes and reproduces the critic's mutation table without host interaction.
- C3–C7 also checked: C3/C4/C5 confirmed by reading (R3/R4/R5), C6 confirmed
  as a tradeoff to name (R6), C7 confirmed and extended (R7). The critic's
  "instrument dead knobs" minor is confirmed (R8).

## 3. What survives (verified, not assumed)

The landing's core is sound: the measured family bytes **are** the landed
family bytes; the splice accounting is exact; the 12-row attribute
transcription reproduces on live rows in both runs; the env-precedence,
parse-lattice, late-attr re-snapshot and link-witness laws do real work (the
`late_attr_census`/`link` machinery is code-verified and receipt-verified);
every armed cork/prebuf/record/latency/subscribe number the author publishes
reproduces; teardown is clean in every entry and the only non-green lines are
the two disclosed `e_native_corked` blocks; the landing is intact in the
working tree under later rounds. Critic and verifier independently re-ran the
battery on the committed bytes (178 legs / 0 failures / 2 blocks), which closes
the "author ran on a pre-r90 base" gap.

## 4. Residual risk and verification gaps

1. **I did not execute a full battery myself** (host under multi-seat load; my
   seat ran static re-derivation, receipt re-derivation, and two read-only
   `pactl` probes). "The landed file runs green end-to-end" therefore rests on
   the critic's and verifier's runs, which I inspected but did not reproduce.
2. **The author's two green runs exercised a base that predates main's
   r90–r95 blocks.** The r96 block and its wiring are byte-identical and
   self-contained (my WT-vs-merged diff shows only other rounds' blocks and
   their wiring lines differ), so the family result transfers — but the exact
   landed `main()` body was not the one the author ran.
3. **`e_native_corked`'s value arm is a host property**, not a law (cached
   `dev_info`); a host with a synced cache greens it. The class claim is armed
   and passed. Do not arm the value in a future round.
4. **Console-line green bias** (inherited): the runner prints
   `{"receipt": …, "failures": {}}` with rc 0 even when entries carry named
   blocks and zero legs. The author's report is honest about its 2 blocks; a
   reader of stdout alone is not.
5. **Fixed-path family lock is per-tree** — two concurrent same-family runs
   from different trees do not exclude each other (observed live by the
   verifier's run B window). Not introduced by this landing; worth a named
   follow-up if cross-tree concurrency becomes routine.
6. **No LSP**: no semantic caller/definition evidence is claimed; caller
   checks were byte/hash-based. The fixture's only in-repo callers are
   `main()` (argparse/mutex/ternaries/dispatch — verified) and the battery
   runner scripts (which invoke the flag explicitly; no registry/allowlist
   enumerating probe flags exists outside receipts and reports — checked).

## 5. Evidence index (this seat)

- Committed blob hashes: `git show 7358f13b:corpus/fixtures/measure_audio.py`
  → `97ed1b1c…` (45271 lines); `…:pulse_r96_probe.c` → `fe2c1683…`.
- Block/span hashes: block 41472–43787 `e1422a13…` (2316 lines) = worktree
  block 31092–33407 `e1422a13…`; span 41471–43787 `be60f1ba…`;
  dispatch 44554–44590 `75bc7fdd…`; worktree file `b545283e…` = frozen-shas.txt.
- Hunk accounting: `diff` parent→commit = 6 hunks, +2358/−3.
- Receipts: `audio-shokunin-wt-r96/corpus/live/runs/20261016T093539457589Z-pulsecli-r96/`
  and `…T093802929935Z-pulsecli-r96/` (leg counts, armed values, coverage
  blocks, `client_build`), `corpus/live/r96-author/{frozen-shas.txt,battery.log,
  run1.stdout.json,run2.stdout.json,dev-target.json}`.
- My probes: `pactl info -s tcp:127.0.0.1:4713` / `pactl -s tcp:127.0.0.1:4713
  info` / `pactl info -s ''` / `pactl info -s /run/user/1000/pulse/native`;
  `ss -ltn` (no 4713 listener); live `r96a` census (0/0/0, no processes);
  predicate table evaluation (R2); programmatic comparison of the 12 published
  attribute rows against both receipts (12/12 exact).
