# r96 critic — the pulsecli family at `7358f13b`

**Target.** `7358f13b` ("r96 author: pulsecli PulseAudio-native client API
(5 entries/178 legs, +2358/-3)"), the pulsecli family in
`corpus/fixtures/measure_audio.py` (committed span lines 41471–43787, file
sha256 `97ed1b1c586d2d5446f2ae85d1ab158e43b0f7d71edf430c2c5f045ed5299efc` —
equal to the integrate report's merged sha) plus the fixture
`corpus/fixtures/pulse_r96_probe.c` (sha256
`fe2c168352144cd66e6977debd84c3ebee80b9ace80c26c4f0bc37d00a8fc64c` = the
author's frozen sha). All bytes were read from `git show 7358f13b:` — the
working tree later carried the (now committed) r97 block, which is not part
of this review.

**Axes I attacked** (named, not inherited): *F* falsifiability of each armed
claim, *P* provenance (sha/splice/witness-vs-subject), *C* coverage honesty
(an unmeasured thing must be a named block, never a green), *T* teardown
hygiene, *N* census integrity (legs/cells actually distinct).

**Verdict posture.** No judgment is rendered here (the canonical Rust judge is
the only Pareto judge). Each item below is a counterexample with its smallest
safe correction.

---

## Findings

### C1 — `b_info_s_after_subcmd` is a non-discriminating green; its law is false (F, P)

**Counterexample.** A `-s` placed *after* the subcommand is silently dropped by
`pactl` 17.0; the arm's `rc 0` is the **default** server, not the named one:

| probe | rc | first line |
| --- | --- | --- |
| `pactl info -s /run/user/1000/pulse/native` | 0 | `Server String: /run/user/1000/pulse/native` |
| `pactl info -s tcp:127.0.0.1:4713` | **0** | `Server String: /run/user/1000/pulse/native` |
| `pactl -s tcp:127.0.0.1:4713 info` | **1** | `Connection failure: Connection refused` |
| `pactl info -s ''` / `pactl info -s unix:` | 0 | default server |

The dead-server variant proves the option is *ignored*, not honored: the
before-subcommand control refuses, the after-subcommand form connects to the
default. The arm (`rc 0`, no class) therefore cannot distinguish "the global
option works after the subcommand" from "the option was dropped", and the
receipt's `b_info_s_after_subcmd__r1/r2` (rc 0, `Server String: /run/user/…/
pulse/native`) is the same value either way.

**Evidence.** `corpus/live/r96-critic/lattice-probes.txt` (A1–A3, B5–B6);
receipt legs `b_info_s_after_subcmd__r1/r2`; boundary report line 153 ("`pactl
info -s …` … works `rc 0` 2/2") — the false claim is inherited, and the
landing arms it.

**Smallest safe correction.** Make the leg discriminating in one line:
`["pactl","info","-s","tcp:127.0.0.1:4713"]` with expected `rc 1` +
`pulse_refused`; or keep `rc 0` and re-word the claim to "a post-subcommand
`-s` is IGNORED" while arming the *resolved* server string (assert it is the
default socket). Either way the witness must move when the hypothesis is
negated.

### C2 — `e_trigger` and `e_prebuf_zero_slow` pass with a dead monitor witness (F, C)

**Counterexample.** Replace `_playback_r78_tap` with a stub that writes a
*valid 0-frame WAV* and sleeps (a structurally successful, content-empty
capture). Running the committed cork entry then yields failures **only** on
the positive legs (`e_cork` ×2, `e_prebuf_default_slow` ×2,
`e_prebuf_default_fast` ×2, `e_prebuf_zero_fast` ×2) while:

```
e_trigger__r1..r3            failures=[]   tap={'frames':0,'nonzero_frames':0,'peak':0}
e_prebuf_zero_slow__r1..r3   failures=[]   tap={'frames':0,'nonzero_frames':0,'peak':0}
```

and with a *missing* WAV (reader failure) `e_prebuf_zero_slow` still passes —
`_pulsecli_r96_capture_stats` returns `{frames:None,…}` and the committed
predicate `(st.get("nonzero_frames") or 0) > 12000` is `False`. So the trigger
negative and the prebuf-0 stall law are satisfied by "the tap measured
nothing", the exact shape the author's §2.1 rule ("never record an empty cold
result as absence") forbids. No arm anywhere reads `frames` or the recorded
`tap_exit_code` (set in `_pulsecli_r96_client_run`, never used).

**Evidence.** `corpus/live/r96-critic/dead-tap-mutation.log` (full per-leg
dump + entry failure list); committed `_check_trigger` /
`_check_prebuf_zero`; the missing-file predicate re-evaluated on the committed
`_pulsecli_r96_capture_stats` (`missing → e_trigger red, e_prebuf_zero_slow
green`; `empty → both green`).

**Smallest safe correction.** Require a same-leg liveness floor before a tap
verdict is allowed: in `_playback_leg` (or in each of the two checks) treat
`frames is None or frames < 0.5 * tap_frames` as a NAMED coverage block, and
arm the r78 tap's own `-n`-bound success shape. One helper plus two call
sites; no new authority.

### C3 — the r96 snapshot readers are not hermetic; witness and subject can split servers (P)

**Counterexample.** With `PULSE_SERVER=tcp:127.0.0.1:4713` in the harness env
(a foreign, dead server), the r96 witness readers follow it while the measured
legs do not:

```
_pulsecli_r96_pactl_json('sinks')  -> 0 rows
_pulsecli_r96_short_rows('sinks')  -> []
hermetic leg pactl list sinks short -> 3 rows, rc 0
```

`_pulsecli_r96_pactl_json` and `_pulsecli_r96_short_rows` never pass `env=`
(committed lines 41829 / 41839), so every row/link/sink-index witness can be
taken from a different server than the client under test. The author's §1
claim ("a foreign `PULSE_SERVER` … can never redirect a leg") holds for the
legs; it does not hold for their witnesses. Outcome under that env is a false
red / spurious block, not a false green — but the witness/subject split is
exactly the class the r83 fold closed for the legs.

**Evidence.** `corpus/live/r96-critic/hermeticity-probe.txt`.

**Smallest safe correction.** `env=_pulsecli_r96_env()` in both helpers
(two lines). The inherited readers used by the entry head
(`_capture_inventory`, `_playback_r78_node_names`, `_pactlmon_r85_graph`, …)
are outside this landing's diff and should be a named follow-up, not silently
folded here.

### C4 — the `p_malformed` "no stream was created" witness is dead (F)

**Counterexample.** `_pulsecli_r96_row("sink-inputs", 0)` matches a row whose
`application.process.id == "0"`, not an index-0 row; a stream created by the
leg carries the leg's pid, so the failure branch
(`if _pulsecli_r96_row("sink-inputs", 0) is not None`) can essentially never
fire. The same pid-0 lookup is *recorded* as `leaf["row"]` in
`t_f32le_invalid`, where it reads like a witness and is not one.
`_pulsecli_r96_run` records no child pid, so no pid-keyed witness is
available to that leg.

**Evidence.** committed occurrences of `_pulsecli_r96_row("sink-inputs", 0)`;
`_pulsecli_r96_run`'s receipt keys.

**Smallest safe correction.** Record `pid` in `_pulsecli_r96_run`'s receipt
and assert `_pulsecli_r96_row(what, pid) is None`; or census sink-input
indexes before/after the leg. The rc-1 + `pulse_invalid_property` half of the
arm is discriminating and unaffected.

### C5 — `t_proc_lat_b` is a byte-equivalent duplicate cell (N)

**Counterexample.** `_attr_leg("t_proc_lat_a", 2, latency_ms=100,
process_ms=5)` and `_attr_leg("t_proc_lat_b", 2, latency_ms=100,
process_ms=5, extra=())` are the same request; the two names carry four legs
for one cell. The "16 flag/env/frame cells" claim is 15 distinct cells (and 14
distinct numeric predictions: `t_f32_100` ≡ `t_stereo_100` =
13440/9604/3840/1440, since only the frame size enters the law).

**Evidence.** committed lines 42979–42980; my full-table dump
(`corpus/live/r96-critic/mutation-arithmetic.txt`).

**Smallest safe correction.** Drop `t_proc_lat_b` (census becomes 176 legs) or
re-purpose it to a genuinely distinct cell (e.g. `process_ms=5` with
`float32le`/stereo) and update the report's 178/16-cell prose. The receipts
stay authoritative either way.

### C6 — the tcp-4713 arms are host-state, not client laws (F) — tradeoff to name

`b_tcp_refused`, `b_tcp6_refused` and `b_env_loses_to_flag` all read
"nothing listens on pulseaudio's default TCP port 4713" (true now: `ss` shows
no listener, so all three legs are green in my run). A sibling lane that
starts a private pulse on 4713 turns them red — and would additionally
*mask* the flag/env precedence claim behind a connection success.

**Smallest safe correction.** Pre-check the port (connect → refused) and, if a
listener exists, block the leg by name and record the chosen port — the entry
already uses exactly this fail-closed pattern for the pacmd index-0 guard.

### C7 — report-internal count drift (non-semantic)

`r96-author.md` §4.4 says "12 legs" for props (receipt 20), §4.5 says "24
legs" for cork (receipt 22), §3 says "all 13 published boundary rows" while
its own table lists 12. The receipts are consistent (178 legs; my independent
run counts 178). Fix the three prose numbers so a verifier counting from the
prose does not false-alarm.

**Minor, instrument:** `pulse_r96_probe.c` accepts `--attr-mode`, `--amp` and
`--server`, none of which the harness ever passes (dead knobs; `--attr-mode
none` would bypass the buffer-attr path entirely if a future family used it).

---

## What survives (verified, not assumed)

**Splice and provenance (P).** The family span 41471–43787 hashes
`be60f1ba…` and the dispatch span 44554–44590 hashes `75bc7fdd…` — both
reproduce byte-exactly on the committed bytes (raw-slice convention, the
integrate report's numbers). The argparse row occurs exactly once, at line
43922, after the r92 row (round-ordered, as claimed); the mutex token once;
the `mode`/`suffix` ternaries once each with r96 first; the dispatch block is
top-level inside `main()` and takes the fixed-path family lock; the five
`measurements[...]` keys occur 1× each; a module-level symbol census finds
1182 names and **0 duplicates**; the three deletions are exactly the three
wiring lines (no prior row touched).

**Instrument (P).** Building the committed `pulse_r96_probe.c` with the
harness's own command (`gcc -O1 … -lpulse -lm`, source basename
`pulse_r96_probe.c`) reproduces the author's recorded binary sha
`c3fc4cefed…` twice. (The sha is basename-sensitive: a renamed source copy
builds to `448aea4e…` — the recorded value is meaningful only for the
harness's own command, which is what the receipt records.) The battery's own
`client_build` in my run reports source `fe2c1683…` and binary `c3fc4cef…`.

**Live re-measurement on the committed bytes (F, C, T).** One independent
battery run (`corpus/live/runs/20261016T100425297878Z-pulsecli-r96/`, 143 s
class, overlapping a sibling r96 verifier run in `/home/vgpnk/r96v/tree` and
four other lanes): **178 legs, 0 failures, 0 blocked entries**, two NAMED
coverage blocks (both `e_native_corked`, the disclosed cached-`dev_info`
disagreement). Every armed cork number reproduces the author's pair: `e_cork`
71677 nonzero frames ×2; `e_trigger` 0 / peak 0 ×3 with live taps (156672 /
156672 / 155648 frames); `e_prebuf_zero_slow` 2752 ×3 vs `e_prebuf_default_slow`
57341; `e_prebuf_zero_fast` 55550; `e_record_cork` peak 196608 / drained
262144; `e_latency_query` rc **−16** on all 10 calls per rep;
`e_subscribe` exactly 1 `change` at the uncork (2 before, 1 `new`, 31/61
foreign events filtered out); `capture_miss` 3/3 refused / 0 hung;
`late_attr_census` 1/66 first-snapshot-missing attrs (recovered — the
late-attr re-snapshot law is doing real work). Teardown: every entry
`sinks_gone={'ns': True}` (+`ns2`) and `own_nodes_after=[]`; no `r96a_`
module/sink/source/process of mine survived; defaults and clock metadata
untouched; the `r96a_*` rows in the WirePlumber store are the disclosed r90
class.

**Falsifier discrimination (F, mutation probes on the committed bytes).** The
mask-form `SPA_ROUND_DOWN/UP` reading changes the prediction of **exactly**
the two `s24le` cells — the author's "s24le falsifies a mask reading" claim
holds. The leading-space parse mutation changes exactly the `" 100"`/`"\t100"`
cells — the `pa_atou` lattice discriminates. All 12 published attribute rows
reproduce from the committed transcription (the prose's "13" is C7).

**Lattice edges measured beyond the armed set (coverage, not defects).**
`PULSE_SERVER=unix:` (no path), `PULSE_SERVER=unix`, and
`PULSE_SERVER=' '` all give `rc 1 Connection refused` — a *different* class
from the empty string's unique `rc 1 Invalid server` (so the empty-server arm
is genuinely unique, as claimed); `PULSE_SERVER=tcp:localhost:4713` refuses by
name; `-s ''` / `-s unix:` after the subcommand are ignored (C1).

---

## Archive (under /home, untracked; nothing committed)

`corpus/live/r96-critic/`:
`measure_audio.r96-committed.py` (= `git show 7358f13b:` bytes, 97ed1b1c…),
`measure_audio.r96critic.fixtures-copy.py` (the in-fixtures copy actually
run; identical bytes), `pulse_r96_probe.r96-committed.c` (fe2c1683…),
`build1/pulse_r96_probe` (+`pulse_r96_probe2`, source) — the archived
instrument, `c3fc4cef…`, twice-built; `lattice-probes.txt`,
`hermeticity-probe.txt`, `mutation-arithmetic.txt`, `dead-tap-mutation.log`,
`battery.log`; the battery receipt under
`corpus/live/runs/20261016T100425297878Z-pulsecli-r96/`.

No file under review was edited; the temporary in-fixtures copy and its
`__pycache__` entry were removed after the runs.
