# r81 SIMPLIFIER — YAGNI/dead-code review of the `6aa03e6` diff (read-only)

**Seat** simplifier (r81) · **host** devin · **scope** the landed diff only:
`corpus/fixtures/measure_audio.py` +1686/−3 at `6aa03e6`, family block
`:12543`–`:14203` (7 entries / 55 legs). **Writes**: this report only.

**Custody / tree state at report time**

- Fixture sha256 `0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56`
  == author-pinned sha == the `6aa03e6` blob, unchanged across this seat's
  window; `git status --short` clean for the fixture. For the record: at
  analysis start the tracked
  `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc` showed as
  modified (mtime 14:45:53 — a sibling lane regenerated it before this seat
  started; this seat imported/executed nothing), and by report time it is
  clean again. No tracked file differs at report time.
- HEAD moved during the window `191d3f8` → `516b27e` (r81 scribe); no file
  this seat read changed.
- **No `lsp` device answers this file.** The only MCP server present is
  `rea` (210 tools: Ghidra/rizin/Frida/bundle REA; `procedure_references`,
  `find_xrefs_to_name`, `get_call_graph`, `xrefs` all operate on a loaded
  native binary/JS artifact — its subject `format` enum has no Python
  source). Recorded as unavailable: **all reference proofs below are
  literal `grep` over the single committed file, not semantic LSP proof.**
- No probe/battery re-run (read-only tasking ⇒ no new receipts). "Behavior
  preserved" below means: (i) static proof the removed code is read by no
  checker, and (ii) the pinned green runs show the removed path never fired.
  Receipts used: `corpus/live/r81-author/gst-r81-runs/run{1,2}.measurements.json`
  (sha-verified by the scribe; both `failures={}`, 55/55 legs), plus
  `reports/round-81/r81-{author,scout,boundary,boundary-readonly,scribe}.md`
  and `corpus/live/r81-scout/runs/s5-loss/*/receipt.json`.

## 0. Summary

| # | candidate | class | weight | bar |
|---|---|---|---|---|
| S1 | `ports` collection in `_gst_r81_graph` | dead data (never read) | ~6 lines | meets |
| S2 | `_props` nested helper (routing entry) | dead function | 3 lines | meets |
| S3 | `kill_proc`/`call` event arms + docstring | speculative generality | ~10 lines | meets |
| S4 | `"ns"`/`"tag"` ctx keys × 6 entries | dead config keys | 6 lines | meets |
| S5 | `<tone>` redaction token | copied-convention residue | 1 line | meets |
| S6 | `expect_class` write-only leaf | duplicate authority | 1 (+6 tuple slots) | meets |
| S7 | `placeholder_7ffff000` arms + loss tolerance | dead alternate path / falsified constant | 3 lines | meets |
| S8 | `_gst_r81_ns_ensure` core duplicates `_loopback_r79_sinks_load` | duplicated helper logic | ~10 lines | meets |
| S9 | redundant `wall_cap=` default passes × 3 | micro-noise | 3 args | meets |
| L1 | `p8_bogus_server` duplicates `p5_bogus_server` | dead leg (no distinct evidence) | 1 leg | meets |
| L2 | `c0≡e10`, `p6≡e11` cross-arm duplicate legs | duplicated evidence | 2 legs | flagged, **retained** |
| T3 | never-fired / shadowed error-class entries | diagnostic fallbacks | 6 lines | below bar |

No edits made (read-only seat). Line numbers are the committed tree at
`6aa03e6` (fixture sha above).

## 1. Deletion candidates that meet the bar

### S1 — `ports` is collected and returned, never read

**(a) Remove** `:12651` (`ports` in the tuple), `:12666`–`:12669` (the
`elif t.endswith("Port")` block), `:12681`–`:12682` (`"ports": ports` in the
return). Result: `nodes, links, clients = {}, [], {}` and a 3-key return.

**(b) Proof unexercised.** Literal grep for `"ports"`/`['ports']` over the
whole fixture matches only those three write sites. `_gst_r81_graph()` has
exactly one call site (`:12722`, inside `_gst_r81_sample`); its readers
(`_gst_r81_sample`, `_gst_r81_our_nodes`, `_gst_r81_consumers`,
`_gst_r81_producers`, `_gst_r81_last_node`) touch only `nodes`/`links`/
`clients`. The graph dict is never serialized — receipt leaves come from the
sample leaf, and the substring `ports` occurs **0** times in both r81
receipts. (Not semantic LSP proof — no LSP device; §Custody.)

**(c) Receipts.** `run1`/`run2`: no leaf added or removed; all 55 legs'
verdicts and leaf values are produced from `nodes`/`links`/`clients` only.
Byte-identical samples expected; the two pinned runs stand as the reference
because nothing they recorded came from `ports`.

### S2 — routing's `_props` helper is defined and never called

**(a) Remove** `:13434`–`:13436` (the nested `def _props(lname)`), keeping
the sibling `_node` which *is* called.

**(b) Proof unexercised.** `grep '_props('` matches only the definition.
Every routing check reads props inline: `nd.get("props")` at `:13443`,
`:13461`, `:13475`, `:13494`, `:13510`, `:13522`, `:13536`. No receipt
carries a `_props` artifact (it returns no leaf).

**(c) Receipts.** unchanged — no assertion or serialized field references it.

### S3 — `kill_proc` / `call` event arms are speculative

**(a) Remove** `:12960`–`:12967` (the `elif kind == "kill_proc"` and
`elif kind == "call"` arms) and the docstring sentence `:12927`–`:12928`
("`kill_proc` kills a feed's pgid, `call` runs a callable"). **Keep** the
`else` guard `:12968`–`:12969` (`{"unknown_event": kind}`): it is the
non-silent fallback and costs one line.

**(b) Proof unexercised.** `grep 'kill_proc'` matches only the dispatch +
docstring; `grep '"call"'` likewise. All three `events=[...]` construction
sites in the family (`:13800`, `:13840`, `:13857`) build exactly one kind:
`"unload_module"` (7 loss legs). Receipts: `fired[*].kind == "unload_module"`
for all 7 fired events in both runs; no `killed_pgid`, no `unknown_event`.
The existing runners this was patterned on (`_playback_r78_run` `:6491`,
`_loopback_r79_run` `:9104`) also never carry these two kinds.

**(c) Receipts.** all 55 legs × 2 runs: `fired` leaves identical (the arms
never execute). The c1 feed-kill is done inline in `finally` (`:13395`),
not via an event, so nothing moves.

### S4 — `"ns"` / `"tag"` ctx keys are dead config

**(a) Remove** the `"ns": GST_R81_NS, "tag": GST_R81_TAG` payload from the
six literals: `:13166`, `:13325`, `:13629`, `:13783`, `:14025`, `:14139`
(each becomes `{}` or, where used, straight to `dict(tmp=tmp)`).

**(b) Proof unexercised.** The only `ctx` reads in the whole family are
`ctx.get("tmp")` and `ctx.get("tone")` at `:13000`–`:13001` (grep over the
block). `ctx` is never serialized; the receipt only carries `env_extra` and
the redacted `argv`.

**(c) Receipts.** unchanged.

### S5 — the `<tone>` redaction token is impossible by construction

**(a) Remove** `(ctx.get("tone"), "<tone>")` at `:13001`. Optional
follow-up: `<tmp>` at `:13000` is currently shadowed by `<out>` (below) and
could go too if the runner contract pins "out_path always covers scratch
paths"; I would keep it as a one-token guard.

**(b) Proof unexercised.** No r81 entry ever sets `ctx["tone"]` (grep
`"tone"` in the block: only the redaction tuple and the c1 tone-window code,
which uses a *local* path); the c1 pw-play feed is spawned outside
`_gst_r81_leg`. Receipts: `<tone>` occurs **0** times in both runs. `<tmp>`
is also 0: every tmp-carrying leg passes `out_path`, and `str(out_path)`
(a superstring of the tmp dir) is replaced first — 15 argv strings carry
`<out>`, 0 carry `<tmp>`, 0 leak a raw `/tmp/` path.

**(c) Receipts.** all `argv` strings identical (`<out>` replacement still
fires on the 15 capture legs).

### S6 — `expect_class` is written and never read (duplicate authority)

**(a) Remove** `:14067` (`legs[name]["expect_class"] = cls`), and drop the
now-unused `cls` slot from the seven `L` tuples (`:14032`–`:14062`) so no
dead binding remains. Minimal alternative: delete `:14067` alone.

**(b) Proof unexercised / duplicated.** `grep 'expect_class'` matches only
the write. The checker's authority is the separate `expect` dict
(`:14070`–`:14078`) for classes and `expect_hit` (`:14089`) for hits. The
class of each exit leg is therefore declared **twice** (L tuple + expect
dict); only one is read, so the two can silently diverge on any edit.

**(c) Receipts.** run1/run2 carry `expect_class` on 7 legs per run (confirmed
in the JSON); nothing asserts it. Removing it removes 7 write-only leaves
from a re-run receipt — a shape change, not a verdict change. All 7 exit
legs' rc/class/hit/artifact assertions are driven by `expect` + `expect_hit`
and are untouched.

### S7 — the falsified `0x7FFFF000` arms survive as an accepted class

**(a) Remove** `:12780` (`"placeholder_7ffff000" if riff == 0x7FFFF000 else`)
and `:12797` (`"placeholder_7ffff000" if csz == 0x7FFFF000 else`) from
`_gst_r81_wav_inspect`, and drop `"placeholder_7ffff000"` from the loss
tolerance at `:13947`–`:13948`, pinning the check to the measured class:

```python
if out.get("riff") != "wavenc_streaming" or \
        out.get("data") == "finalized":
```

**(b) Proof dead / falsified.** `0x7FFFF000` is the scout's misquote,
independently falsified three ways: `r81-boundary-readonly.md:25`–`28`
("Any arm asserting `0x7FFFF000` will fail; pin `0x7FFF0024`/`0x7FFF0000`"),
`r81-boundary.md:54`, `:355`–`:358`, and author §3.1. The scout's own raw
receipts record the true value as `"other:2147418112"` (12 files under
`corpus/live/r81-scout/runs/s5-loss/`); the string `placeholder_7ffff000`
occurs **0** times in run1/run2. The arms were copied from the scout probe
(`corpus/live/r81-scout/r81_probe.py:101`, `:113`) where they also never
matched; this commit added the corrected `wavenc_streaming` arms but kept the
stale ones. The four frozen legs report `riff=wavenc_streaming`,
`data=wavenc_streaming` (riff_size `2147418148` = 0x7FFF0024, data_declared
`2147418112` = 0x7FFF0000) in both runs — the deleted arms are behind them in
the chain and never reached.

**(c) Receipts.** t3–t6 classify `wavenc_streaming` before the deleted arms
in both runs; c1/c4/c7 (`finalized`) and t7 (`placeholder_8`/`zero`) are
upstream of them too. No leaf changes. Tradeoff: a hypothetical writer
emitting exactly 0x7FFFF000 now reads `other:2147479552` in the receipt
(still visible, not silent) and the loss leg fails — the desired strictness
for a pinned constant. This closes the same residue the scribe logged as F1
on the scout *text*, now inside the fixture itself.

### S8 — `_gst_r81_ns_ensure` re-implements `_loopback_r79_sinks_load`

**(a) Replace** the body `:12864`–`:12871` with a call to the existing
helper; the present-check `:12858`–`:12863` stays:

```python
def _gst_r81_ns_ensure(loads):
    if GST_R81_NS in (_capture_r77_sink_names() or []):
        leaf = {"present": True,
                "module_id": _gst_r81_sink_module_index(GST_R81_NS),
                "sink_seen": True}
    else:
        leaf = _loopback_r79_sinks_load([GST_R81_NS])[GST_R81_NS]
    loads[GST_R81_NS] = leaf
    return leaf
```

**(b) Proof duplicated.** `_loopback_r79_sinks_load` (`:9613`–`:9629`) is
line-for-line the same core: same `_playback_r78_null_sink_load`, same
`_loopback_r79_wait_monitor`, same leaf keys (`module_id`, `rc`, `error`,
`sink_seen`, `monitor_seen`, `monitor_waited_s`, `monitor_gate`). The r81
function adds only the present-check and the caller-owned `loads` write,
both preserved above. The family already reuses r77/r78/r79 gates by name
(`_capture_r77_sink_names`, `_playback_r78_null_sink_load`,
`_loopback_r79_wait_monitor`, `_playback_r78_write_tone`,
`_playback_r78_tone_windows`), so this is the same convention, not a new one.

**(c) Receipts.** `loads` is never serialized in the r81 entries, and the
only consumer of its leaves is teardown's `module_id` (`:12880`) — identical
value via either path. The r79 helper is already exercised green by the
committed r79 legs. Expected: all 55 legs' verdicts and every `unloads`
leaf unchanged.

### S9 — three call sites pass the default `wall_cap` (no-op)

**(a) Remove** the redundant `wall_cap=GST_R81_WALL_S` arguments at
`:13202` (n4), `:13358` (r8's kw dict becomes `{}`), `:14066` (exit legs).
The default at `:12920` is the same constant.

**(b) Proof.** `GST_R81_WALL_S` is the declared default; passing it cannot
change behavior. Only the loss legs intentionally override (4.5 s).

**(c) Receipts.** unchanged.

## 2. Leg-level: 7 arms / 55 legs

Method: coarse duplicate-signature scan over every leg in both pinned runs
(`(exit_code, error_class, error_hit, out.riff, out.data, out.bytes,
last-sample consumers/producers, killed)`), then a read of every check block.
Every one of the 55 legs is referenced by at least one assertion (no orphan
leg): lattice via `want` (15), naming n0–n4, routing r1–r8 + c0/c1/c4/c7,
pulse p1–p6, loss t1–t7, exit via `expect` (7), autodetect a0–a2.

### L1 — `p8_bogus_server` produces no evidence `p5_bogus_server` doesn't (meets the bar)

**(a) Remove** the `p8_bogus_server` entry at `:14058`–`:14062` and its
`expect` row at `:14077` (exit-classes arm drops 7 → 6 legs; family 55 → 54).

**(b) Proof duplicated.** In **both** runs, p5 and p8 have byte-identical
`stderr` (only `num-buffers` differs in argv: 96 vs 4) and identical
`(rc=255, gst_connection_refused, "Failed to connect: Connection refused")`.
p5's check (`:13736`–`:13746`) asserts strictly more: same rc + class, plus
`Failed to set pipeline to PAUSED` in stderr. p8's `expect_hit`
("Connection refused") is a substring of p5's own `error_hit`. Inside the
exit arm, p8 contributes nothing to `class_summary` (`:14102`–`:14111`
selects the `zero_byte` legs e10/e11 only), and it does not assert the
state-change line its entry docstring names, nor measure an artifact
(shape `none`). The only references to p8 in the fixture are its L row and
its expect row.

**(c) Receipts.** run1/run2: p5 carries every p8 assertion (verified above);
the exit arm's two stated pairs remain fully witnessed in-arm by
e1/e3/e8/e9 (rc=1, no artifact) and e10/e11 (runtime, 0-byte), and the
connection-refused class stays pinned by p5 in claim 4. Tradeoff: the
claim-6 table loses a row and the exit arm stops being self-contained for
that class; that is exactly the redundancy the round asked to surface.

### L2 — cross-arm duplicate fault injections (flagged, retained)

Exact duplicates in both runs: `c0_no_prop ≡ e10_pwsrc_no_prop` (stderr
byte-identical; both rc=255 `target_not_found`, 0-byte artifact) and
`p6_pulsesrc_bogus ≡ e11_pulsesrc_bogus` (same fault, num-buffers=4; both
rc=1 `gst_no_such_entity`, 0-byte). **Retained** because each is the named
in-arm witness of a *different* claim: c0 is routing's prop-gate contrast
against c1, e10 is the exit arm's rc=255 runtime witness; p6 is the pulse
arm's direction split, e11 is the exit arm's rc=1 outlier. Deleting either
would break arm self-containment and make claim evidence depend on another
entry's success. Recorded so the duplication is visible, not fixed.

Also retained, same reasoning: `t1≡t2` (the split law names both elements
explicitly) and `t3≡t4≡t5≡t6` (the inertness law *is* the comparison). The
lattice's `alsasrc` row has no consuming leg and `nosuchelement_r81_xyz` is
a template control — both produce distinct availability/template evidence
and are asserted in `want`; retained.

## 3. Checked and NOT dead (explicitly cleared)

- **`_gst_r81_wav_inspect` vs `_capture_wav_inspect` (`:3025`)** — parallel
  helpers are deliberate: the r81 vocabulary names the wavenc streaming
  placeholders (0x7FFF0024/0x7FFF0000) that the shared r76 helper would
  report as `other`; extending the shared helper could reclassify committed
  r76/r77 rows (the family's own "never prepend into shared tables" rule,
  stated at `:12612`–`:12614`). No merge proposed.
- **`_gst_r81_graph` vs `_loopback_r79_nodes`/`_module_r80_nodes`** — the
  r81 reader is object-id keyed with the `node.client.id → Client.pid` join;
  the others are name-keyed. Different keying is the naming-crossover
  claim's whole point. Retained.
- **`_gst_r81_unload_own` vs `_playback_r78_unload` / `_module_r80_unload_own`**
  — three ownership proofs exist; r81's name-in-args match is the strongest
  and follows the sink-module family. Replacing it with r80's live-citation
  gate would change the proof and the `verified_index`/`recycled` receipt
  leaves. Retained (and out of diff scope to touch the older two).
- **`_gst_r81_teardown`/`_gst_r81_block` vs r79's** — r81 *tightens* the
  convention (strict sink reader + `coverage_blocked` on reader error;
  `setdefault` instead of clobbering `coverage_blocked`). Divergence is an
  improvement; retained.
- **Constants** — `GST_R81_{PID,NS,TAG,RAW,WALL_S,BYTE_CAP,LOSS_EVENT_S,
  LOSS_WALL_S,RELINK_BOUND_S,BOGUS,ANSI,PROP_KEEP,PROP_DROP}` all referenced
  ≥2× (grep census). No dead constant.
- **`GST_R81_PROP_KEEP`** — every alternative is matched by ≥1 observed key
  in the receipts (`node.*`, `stream.capture.sink`, `target.object`,
  `media.*`, `application.name`, `client.api`, `object.register`,
  `pulse.server.type`). **`GST_R81_PROP_DROP`** — the 7 keys are
  receipt-stability drops; their presence cannot be shown from receipts
  (dropped by construction) and dropping a key that never occurs is
  harmless. No deletion.
- **Receipt-surface-only fields** (never asserted, kept as evidence):
  node `state` (3 observed classes: running/idle/suspended), sample `live`,
  `signal`, `wall_s`, `env_extra`, `fmt/ch/rate/bits`, `data_actual`,
  `frames_declared`, and the lattice leg's `expect` copy at `:13102`
  (write-only, aliases `want[el]` at write time — no divergence risk today).
- **Copy-paste observations with no weight win** (retained): the `base`
  pipeline list 4× (num-buffers 96/96/96/48), `default = inventory or
  oracle.sink_pactl` 3×, the `_node`/`_nd`/inline accessors, 19 copies of
  `if leg.get("exit_code") != 0 or nd is None`, and routing's `default_seen`
  (`:13425`–`:13428`, message-only, includes `sink_meta` unlike the other
  three sites). Hoisting each would add a helper for near-zero net weight.
- **Wiring (`:14326` flag, `:14333` mutex, `:15216` mode, `:15236` suffix,
  `:14624` dispatch)** — the 3 diff deletions are exactly the rewritten
  mutex/mode/suffix lines; all four surfaces consume the flag and the
  receipt carries `mode: "probe-gst-r81"` / `-gst-r81` suffix. No dead
  config key.

## 4. Below the bar (reported, not proposed)

**T3 — six of ten error-class entries never fire; two are shadowed.**
Receipts show exactly four classes in use: `gst_parse_refusal`,
`gst_target_not_found`, `gst_no_such_entity`, `gst_connection_refused`.
Never returned by any of the 55 legs: `gst_state_change_refusal`,
`gst_not_negotiated`, `gst_not_linked`, `gst_no_element`,
`gst_internal_stream`, `other_error`. `gst_state_change_refusal` is
*shadowed* by `gst_connection_refused` on p5/p8 (the only legs whose stderr
carries its marker) and by `gst_target_not_found` on e10; `gst_no_element`
cannot fire because e1's stderr matches `gst_parse_refusal` first;
`not_negotiated`/`internal_stream`/`not_linked` name the scout's e14 class,
whose legs were not armed. Pruning saves ~6 table lines but removes
diagnostic resolution for unarmed failure modes — a coverage/diagnostic
tradeoff, not a clean weight win. Recommendation: either keep as the scout's
class vocabulary, or arm e14 (a coverage change, out of this seat's scope).
`other_error` is the catch-all and should stay regardless.

**Parameterization with no override callers** — `sample_at` (default path
exercised by 48 legs) and `byte_cap` (the cap check runs on every loop tick
but never trips: 0 `bytecap` kills in both runs; the only `killed` value is
`wallcap`, 8 legs). Retained: `byte_cap` is the flood guard named in the
triple-bound claim; deleting the override only would be churn.

**Limits of this review**: no fresh run (read-only), so "preserved" rests on
static unread proofs plus the pinned runs; `loads` is not serialized, so the
`present` branch of `_gst_r81_ns_ensure` cannot be evidenced from receipts
(the S8 proposal preserves it either way); r76–r80 code was not reviewed
(diff scope).

## 5. Stop point

S1–S8 are behavior-identical by construction and receipt-neutral (S6/S7
change only write-only/redundant leaves; S8 is shape-identical). The next
deletions — the error-class fallbacks (T3), the unarmed scout classes, or
the cross-arm witness legs (L2) — would each remove a diagnostic, coverage,
or self-containment axis rather than weight. Stop here.
