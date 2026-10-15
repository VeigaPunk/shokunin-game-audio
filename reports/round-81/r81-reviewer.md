# r81 REVIEWER — the `--probe-gst-r81` family, independently verified

Seat: **REVIEWER** (audio-shokunin round 81). Host `plazir27`, repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, work commit `6aa03e6`
(report commit `191d3f8`). **No commit, no tracked-file edit; this seat wrote
only this report.** Every command run was read-side (`git`, `sha256sum`, `jq`,
`python3 -c compile(...)`, `pw-dump`, `ps`, `strings`, `grep`); no host
PipeWire/Pulse state was mutated, no fixture leg was re-run, and the
concurrently live `r81-verifier` run (pid 2758068, observed via `ps` and as
node `gst_r81_auth_2758068` in `pw-dump`) was left untouched.

Artifacts under review: `corpus/fixtures/measure_audio.py` (+1686/−3),
`reports/round-81/r81-author.md`, receipts `corpus/live/r81-author/`
(`gst-r81-runs/run{1,2}.measurements.json`, `runs-{a,b}/`,
`stability-*.txt`, `receipt-shas.txt`) and the canonical receipts they pin
under `corpus/live/runs/`.

## Verdict

**ADMIT-recommend.** The diff is insertion-only modulo three wiring lines; the
seven arms measure what report §1–§7 claims (I re-derived every headline value
from the receipts, both runs); seat-ownership hygiene is real (single
name-verified unload path, seat-owned names, zero leftovers in the receipts);
no volatile cell is pinned; report arithmetic matches the receipts on disk
except for the attribution/typo items below. **No finding blocks admission** —
F1/F2 are assertion-strength and framing gaps that should be fixed in a future
round, F3–F8 are report-precision or hygiene items.

## Diff shape — insertion-only modulo the 3 wiring lines (verified)

```
git diff 6aa03e6^ 6aa03e6 -- corpus/fixtures/measure_audio.py   → 1686 insertions, 3 deletions
hunks: @@ -12540,6 +12540,1667 @@   (the family block, +1661)
       @@ -12662,13 +14323,14 @@   (flag +1; mutex line −1/+1)
       @@ -12959,6 +14621,27 @@    (dispatch block, +21)
       @@ -13530,7 +15213,7 @@    (mode ternary −1/+1)
       @@ -13550,7 +15233,7 @@    (suffix ternary −1/+1)
```

The deletion set is exactly the three wiring lines. Two are byte-verified
prepend-only: `mode` and `suffix` share their full original tail with the new
line (common suffix 8494/8494 and 7880/7880 chars), the only change being
`"probe-gst-r81" if args.probe_gst_r81 else ` / `"-gst-r81" if args.probe_gst_r81 else `
prepended. The mutex line is **not** a ternary: it is a one-token insertion
`, args.probe_gst_r81` appended inside the existing `sum([...])` list
(`difflib.SequenceMatcher` ratio 0.9975; single 22-char insertion) — semantics
equivalent, wording of report §1 wrong (F5).

Fixture identity: `sha256(measure_audio.py) = 0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56`
— equals the report §6 claim and the blob at `6aa03e6`
(`git show 6aa03e6:corpus/fixtures/measure_audio.py | sha256sum`); working tree
== HEAD. In-memory `compile()` clean (no `.pyc` written by this seat).

## Findings (by severity)

### F1 — medium (assertion strength / on-record boundary guidance): the freeze predicate accepts the constant the boundary seat falsified, and never asserts the corrected pair

`reports/round-81/r81-boundary-readonly.md:25-28` says: "Any arm asserting
`0x7FFFF000` will fail; pin `0x7FFF0024`/`0x7FFF0000`." The arm instead
**accepts either**: `corpus/fixtures/measure_audio.py:12780` and `:12797-12799`
classify `0x7FFFF000` as `placeholder_7ffff000`, and the freeze check
`:13947-13949` passes for `out["riff"] in ("wavenc_streaming",
"placeholder_7ffff000")` while asserting nothing about `riff_size` or
`data_declared`.

Receipts prove the *true* constants on all four freeze legs, both runs
(`corpus/live/r81-author/gst-r81-runs/run2.measurements.json`,
`gst_target_loss_r81_probe.legs.t{3,4,5,6}.out`):

```
bytes 204844 | riff_size 2147418148 (0x7FFF0024) | data_declared 2147418112 (0x7FFF0000)
data "wavenc_streaming" | data_actual 204800 | frames_declared 536854528
```

So the law as *reported* is true and the falsification is honoured in the
report text (§3.1). What is missing is the pin: the arm cannot distinguish the
corrected constant from the scout's misquote, i.e. it would still pass if
`wavenc` emitted `0x7FFFF000`. Recommend `riff == "wavenc_streaming"` plus
`riff_size == 0x7FFF0024 and data_declared == 0x7FFF0000` (the values are
already in the receipt).

### F2 — medium (mechanism framing): the split law's own receipt carries the discriminator `node.dont-reconnect=true`, which the report neither names nor asserts

Every gst **capture** node in both runs carries `node.dont-reconnect: true`
(96 node samples: `t3_pwsrc`, `t4`, `t5`, `t6_prop_only`, `c1`, `c4`, `c7`,
`n4`); the re-linking control does not (`t7_pw_record_control` props: no such
key), and gst **playback** nodes do not (`r1`…`r8`, `n0`…`n3`, `p1`…`p4`).
Verified by a receipt-wide group-by: `Stream/Input/Audio` + gst ⇒
`dont-reconnect=true` (n=96), `Stream/Input/Audio` + pw-record ⇒ null (n=22),
`Stream/Output/Audio` ⇒ null (n=78).

WirePlumber implements that key as exactly "do not move/re-link":
`/usr/share/wireplumber/scripts/linking/prepare-link.lua:27`
(`local reconnect = not cutils.parseBool (si_props ["node.dont-reconnect"])`),
`:65` (`"... dont-reconnect, not moving"`), `:73-76` ("if the stream has
dont-reconnect and was already linked before, don't link it to a new target").
The literal is **absent from every gst plugin** (`grep -rl dont-reconnect
/usr/lib/gstreamer-1.0/` → empty) and present in the PipeWire core and pulse
module, so the flag is not gst's own write.

The measurement itself is solid and honest (0 producers in all 17 post-unload
samples of t3–t6, 204844 B flat, stderr empty, alive at wall cap, and t7
re-links at +0.202 s). The defect is that report §2 claim 5 / §5 states "the
gst capture does not re-link" as an unqualified client-specific law, rules out
only `node.target` ("the stale node.target prop is ruled out as the cause"),
and never mentions the prop that its own receipt records and that the session
manager consumes. Recommend asserting `node.dont-reconnect == "true"` on the
freeze legs (and its absence on t7) and wording the law as
"target-bound gst capture streams are flagged `node.dont-reconnect` and are not
re-linked by policy", or explicitly stating that the cause is not
distinguished.

### F3 — low-medium (vacuous witness): `class_summary.parse_rc1_no_artifact` is substantive for 1 of its 4 legs

`:14081` does `out = leg.get("out") or {"exists": False}`; e3/e8/e9 were run
with `out_path=None` (`:14038`, `:14043`, `:14046`), so their `out` is `null`
in the receipt and the `all(...)` at `:14105-14107` passes **vacuously** for
them. Only e1 has a filesink and is a real no-artifact witness
(`e1_missing_element.out = {"exists": false}`). Report §2 claim 6 presents the
class-level statement as measured ("parse refusals are rc=1 + no artifact
(`class_summary.parse_rc1_no_artifact: true`)"). The per-leg (rc, class) pairs
are all genuine (verified); only the *class-level* summary is weaker than
advertised. Recommend giving e3/e8/e9 a filesink path, or counting only legs
with a defined `out_path`.

### F4 — low (report attribution): the semantic-leaf attribution in §4 is wrong for the r79 leaf and for 6 of the 133 r78 leaves

Verified totals (TOTAL rows of the `stability-*.txt` files):
`stability-r81-runsAB.txt` 5569/710/556/**0** sem over 6835;
`normal` 373/373 exact; `module-r80` 0 sem over 1785; `capture-r79` **1** sem
over 23619; `capture-r78` **133** sem over 12405; cross-pair r80 **1**, r79
**276**, r78 **424** — all match report §4. But the claim that these are "all
inside `playback_default_follow_r78_probe`'s live-routing cells" is wrong:
the r79 leaf is
`filterchain_module_r79_probe/legs/f1_good/tap/windows[0]/audio`, and the 133
r78 leaves span three cases (`playback_default_follow_r78_probe` 127,
`playback_target_lattice_r78_probe` 5, `playback_target_loss_r78_probe` 1).
Also undisclosed: the r78 A/B pair has 7 added / 34 removed leaf paths and r79
has 0 added / 2 removed (same tone-window list-length drift).

### F5 — low (report wording): "prepend-only ternary" describes 2 of 3 wiring lines; two anchors are off by one

See the diff-shape block: the mutex line is a list append, not a ternary.
Anchor check: `:14326` flag ✓, `:14624` dispatch ✓, `:15216` mode ✓; report's
`":14334 (mutex)"` is the `parser.error` body (`if sum([...]) > 1:` is at
14333) and `":15237 (suffix)"` is the `out = …` line (`suffix = …` is at
15236). Cosmetic.

### F6 — low (report table): `alsasink` klass printed as `Sink`

Report §2 claim-1 table row `alsasink`/`alsasrc` prints `Sink`/`Source/Audio`;
the fixture asserts `Sink/Audio` (`:13056-13059`) and the receipt says
`klass=Sink/Audio` for alsasink (and `Source/Audio` for alsasrc), `stable=true`
on both reps, both runs. The compression is inherited from the scout's
`Sink|Source/Audio` cell; the armed value is the correct one.

### F7 — low (blanket claim): "all unloads … rc 0" is true for every *fired* unload, not for every unload record

Per run there are 4 teardown unload records + 7 timed unload events. The
timed events and three teardown records are
`{"verified_index":536870919,"captured":536870919,"recycled":false,"exit_code":0}`
(verified_index == captured, `recycled:false`, rc 0 — both runs). The
`gst_target_loss_r81_probe` teardown record is
`{"verified_index":null,"captured":536870919,"skipped":"not_listed"}` because
the +1.2 s event already unloaded the sink — the correct behaviour (no bare
index is fired) and the reason `sinks_gone` passes trivially there. §5's
"all runs: recycled:false, rc 0" should say "all fired unloads".

### F8 — low (observation, hygiene; not an author defect): the tracked `.pyc` is a shared hazard, transiently dirty in my review window

`corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` is **tracked**.
At 17:45:53Z it was modified in the tree (580245 → 872383 B; embedded header
src_size 808688 = the r81 source, src_mtime 17:15:56Z); at 17:48:23Z it was
back to the HEAD blob (580245 B, embedded src_size 533517). The write
**postdates** the author's handoff commit `191d3f8` (17:43:34Z) and coincides
with the `r81-verifier` lane start (its dir 17:45:40Z), so attribution is most
likely that sibling lane — the author's §6 claim is corroborated, not
contradicted. Evidence that the author's own compile happened at 17:15:56Z and
was cleaned up: `reports/round-81/r81-baseline.md:270` (independent witness:
"the r81-author seat's `python3 -m py_compile` + `--probe-gst-r81` legs
(17:15:56Z onward)") and the fixture mtime 17:15:56Z, unchanged through both
formal runs and the battery. Recommend untracking the `.pyc` (or ignoring it)
in a later round so no lane's syntax check dirties a tracked binary.

## Independently confirmed (receipts re-derived, both runs unless noted)

- **Scale/shape**: 7 new entries, 55 legs (15/5/12/6/7/7/3); 24 entries in the
  receipt = 17 prior + 7 new; `failures: []` per entry, `mode=probe-gst-r81`.
- **Shas**: run1 `ebd93c36e730f944…`, run2 `aba69d9ea35583ea…` — report text
  matches; the pinned copies under `gst-r81-runs/` are byte-identical to
  `corpus/live/runs/20261015T1717…-gst-r81/` and `…T171856…-gst-r81/`.
- **§1 lattice**: 14 element legs × 2 reps, `stable=true` all, both runs;
  versions 1.6.8 (pipewire pair) / 1.28.6 (rest); `wavenc=Codec/Muxer/Audio`;
  `openalsink` and the control both rc=255 with the exact first line; plugin
  `pipewire` rc 0 version 1.6.8; and the rc asymmetry is armed (inspect 255 vs
  `e1` gst-launch rc=1).
- **§2 naming**: n0 default `gst-launch-1.0`/`gst-launch-1.0`/`gst-launch-1.0`
  with `application.name=null`; n1 renames only `node.name`; n2 renames all
  three node strings while the Client keeps `gst-launch-1.0`; n3 moves the
  Client to `…_app` while the node keeps `gst-launch-1.0`; n4 capture node
  renamed, producers `[<ns>]`. Client-side: `client.name` is `null` on
  **196/196** node samples of the family (report §3.3 "on every leg" ✓).
- **§3 routing**: r1 two-key write (`node.target` **and** `target.object`);
  r2/r3 single-key each route; r4 bogus verbatim + silent fallback to the
  leg-time default with empty stderr; r5 element prop beats `stream-properties`;
  r6 `PIPEWIRE_PROPS` honoured (rename + `node.target`); r7 `PIPEWIRE_NODE`
  lands as `target.object`; r8 `node.autoconnect` is the STRING `"FALSE"`,
  node unlinked, `killed=wallcap`, rc −9; c0 rc=255 `target not found` +
  0-byte artifact; c1 finalized 819244-B wav, `stream.capture.sink` STRING
  `"TRUE"`, producers `[<ns>]`, tag tone 42/42 windows; c4 lands the *default*
  monitor (producers = default SPDIF node, not `<ns>`); c7 prop-only routes.
- **§4 pulse axis**: p1 `target.object=<ns>` + `client.api=pipewire-pulse`;
  p2 bogus verbatim + silent default fallback; p3 `PULSE_SINK` honoured;
  p4 `device=` beats `PULSE_SINK`; p5 rc=255 `Connection refused` + "Failed to
  set pipeline to PAUSED" present; p6 rc=1 `No such entity` + 0-byte artifact.
- **§5 target loss**: 22 samples/leg at 0.2 s, unload fired at 1.2 s by the
  name-verified index; t1/t2 first post-unload link at **+0.203 s**, t7 at
  **+0.202 s**, all with an empty-link sample at the unload instant (report's
  "one empty-link sample at the boundary" ✓); t3–t6 no link in any post-unload
  sample, flat 204844 B, unfinalized header, empty stderr, alive to the 4.5 s
  wall cap, identical across on-disconnect none/error/eos and prop-only; t7
  233516 → 864300 B (run-2 verbatim) and `finalized`-never (SIGKILLed).
- **§6 exit classes**: e1 rc=1 no artifact; e3/e8/e9 rc=1 `gst_parse_refusal`
  with the exact expected stderr substrings; e10 rc=255 + 0-byte; e11 rc=1
  `No such entity` + 0-byte (the outlier); p8 rc=255 `Connection refused`;
  `class_summary = {parse_rc1_no_artifact: true, runtime_refusal_zero_byte: true}`
  (see F3 for the strength caveat).
- **§7 autodetect**: a0 rc=0, `client.api=pipewire-pulse`,
  `media.name="audiotest wave"`, consumers = default sink; a1 rc=1 with
  `GstPulseSrc…actual-src-puls` + `No such entity` + `not-negotiated (-4)` +
  0-byte artifact; a2 rc=0 with **0** pw node samples.
- **Hygiene**: single `pactl unload-module` call site in the whole new family
  (`:12842`, inside `_gst_r81_unload_own`); 0 `set-default-*` in the family;
  all names `gst_r81_auth_<pid>` / `gst_r81_<pid>_*` (pids 1291125 run 1,
  1297251 run 2); `sinks_gone` true and `own_nodes_after []` in every loaded
  entry of both runs; no threads anywhere in the family; every spawned pgid is
  killed by its owner; `unlink` only on the leg's own scratch output.
- **Battery (§4)**: 8 commands, all `EXIT=0` and `failures {}`; per pass
  86 entries / 136 legs (17/0, 25/59, 25/67, 19/10) → 172/272 across both
  passes; fixture sha constant `0dad37ee…` before/after every command in both
  `commands.log`s; `normal` receipt `8e8cdad6cc3c356d…` byte-identical across
  author-a/b and baseline-a/b, and shared by 352 of the 500 tracked `-normal`
  receipts I hashed. Baseline's own 7/8-exit-0 pass corroborated
  (`rc=0,0,1,0` twice; its runs-b capture-r78 stdout carries the 3 failure
  rows).
- **Contention disclosure (§5)**: corroborated by independent evidence — the
  baseline's runs-b battery ran 17:11:27–17:20:57Z (`corpus/live/r81-baseline/runs-b/commands.log`)
  and the author's formal runs were 17:17:19Z / 17:18:56Z, so the claimed
  overlap is real; the author's own `contention` census shows
  `fixture_runs: 1`, `pw_loopback: 1`, `host_is_quiet: false` in the gst
  entries, and `reports/round-81/r81-baseline.md:265-275` names the author's
  legs from the other side.
- **Nondeterminism**: no volatile cell is pinned anywhere in the family — no
  byte counts (grep for `204844|819244|65580|864300|2147418112` in
  `:12543-14203` → only the `0x7FFF` classifier branches), no object ids, no
  wall times, no sample counts; `wall_s`, `id`, `t`, `size` appear only in
  comparisons that are relative (growth, `<= 44`, `!= 0`) or in the
  pid-normalized compare. The `stability-r81-runsAB.txt` classification
  (5569 exact / 710 volatile / 556 jitter / 0 semantic / 0 added / 0 removed)
  is consistent with the two runs differing only in pids/ids/times.

## Residual risk

1. **Default-sink coupling.** r4/p2/c4/a0/t1/t2/t7 assert against the leg-time
   default read at entry start; a foreign lane that moves the default mid-entry
   makes these arms *fail* (honest red, not a false pass) — as happened to the
   baseline seat's own battery. Not a defect; a known contention coupling that
   the round-81 window exercised.
2. **Ambient env inheritance.** `_gst_r81_leg` (`:12930-12933`) copies
   `os.environ` and only *adds* `env_extra`; it never scrubs `PIPEWIRE_PROPS` /
   `PIPEWIRE_NODE` / `PULSE_SINK`. The env-vector legs set their own values,
   but the control legs (r1–r8, p1/p2, a0) would be confounded by a foreign
   ambient value. My shell env has none and the receipts show the expected
   values, so this is latent only; scrubbing those three keys for the non-env
   legs would close it.
3. **`sink_name=` substring match.** `_gst_r81_sink_module_index` (`:12823`)
   matches `f"sink_name={sink_name}" in ln`, so a module named
   `gst_r81_auth_<ourpid>_suffix` would satisfy the ownership proof for our
   index. Pid-scoped names make this remote (a sibling lane cannot use our pid),
   but a token-boundary match would be strictly safer.
4. **`num-buffers` bound semantics.** The family uses `num-buffers` as a
   *bound* only and never asserts a frame count, so it is consistent with the
   boundary falsification ("`num-buffers` **is** an exact frame bound on the
   pulse record path", `reports/round-81/r81-boundary.md:275-291`); the
   observed artifacts are 204800 frames (c1, 100 buffers) and 102400 frames
   (c4/c7), i.e. per-buffer size differs by path, which the arms do not depend
   on. No conflict.

## Verification gaps

1. **No LSP device in this seat's toolset.** No `lsp` server/status tool was
   exposed to me, so `references`/`definition`/`diagnostics` could not be run
   and no cold-empty result was recorded. Caller/definition checks were done
   textually over the single file (every new helper has a definition and ≥1
   call site — `_gst_r81_errclass/graph/our_nodes/consumers/producers/sample/
   wav_inspect` 1 caller each; `unload_own` 3; `teardown` 4 entry `finally`
   blocks; `block` 6; `leg` 23; `entry_head` 7) and by reading every caller.
   **This is textual enumeration, not semantic proof**; the grep output above
   is offered as the literal fallback only.
2. **No per-run fixture hash inside the gst-r81 receipts.** The "byte-identical
   frozen code" claim for the two formal runs is supported indirectly: the
   fixture's mtime is 17:15:56Z and is unchanged at review time (both runs
   17:17:19Z/17:18:56Z postdate it), the blob sha equals the report's, and the
   baseline seat independently logged the author's `py_compile` at 17:15:56Z.
   The battery driver does record before/after shas per command; the formal-run
   receipts do not.
3. **Post-run "zero leftovers" census cannot be re-verified now.** An
   `r81-verifier` run was live during my review (`ps` pid 2758068; pw-dump node
   `gst_r81_auth_2758068`), so the host census I could take is not a statement
   about the author's window. The in-receipt witnesses (`sinks_gone` true,
   `own_nodes_after []` in all loaded entries of both runs) are the evidence I
   verified.
4. **Relink latency is an interval, not a point.** The empty-link sample at the
   unload instant plus the first linked sample at +0.203 s means the true
   latency ∈ (0, 0.203] s; the report's "+0.203 s" is the first observation and
   is labelled as such ("one empty-link sample at the boundary"), and the
   `GST_R81_RELINK_BOUND_S = 0.45` gate is a bound, not a measurement — all
   honest, but the law is "≤ one sample", not "0.203 s".
5. **F1/F2/F3 are assertion-strength gaps, not measured errors.** I did not
   re-run any leg (per the seat's no-heavy-run constraint), so I cannot say
   whether an arm pinned to `0x7FFF0024/0x7FFF0000` or to
   `node.dont-reconnect` would stay green on a re-run; the receipts show the
   values needed to make those pins, both runs.
