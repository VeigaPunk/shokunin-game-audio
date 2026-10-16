# r98 simplifier — weight inventory of the native `pw_stream` family

**Seat:** simplifier (leaf, read-only audit). Round N=98, family flag
`pwstream-r98`. **Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c`
("r99 safety: require explicit opt-in before physical LAN control",
2026-10-16 09:29:41 −03). Scope: the r98 family only —
`corpus/fixtures/r98stream.c` (1005 lines) and the r98 block of
`corpus/fixtures/measure_audio.py` (PIN-blob lines 46327–48676) plus its
dispatch (55142–55165), argparse row (54390), mutex token (54400) and
`mode`/`suffix` ternaries (55944, 55964). No source edit, no run, no
before/after experiment, no grader. Advisory only; not a gate decision.

**LSP gap (recorded).** No `lsp` device is available in this seat's
toolset, so no semantic reference check was possible. Every
reference-absence claim below is **literal inspection**: `grep` over the
full 55974-line pinned blob and `git grep` over the whole tracked tree
*at the pin* (`git grep … bb177513… --`). For the C fixture (one
translation unit, all functions `static`) and for a block-local Python
namespace with no `getattr` dispatch (the only three `getattr` hits in
the pinned file are r82/r96 helpers, lines 14487/42462/43714), literal
tree-wide absence is strong but it is **not** semantic proof; it is
labeled as such everywhere below.

**Commands actually executed:** `git cat-file -t`/`log -1` on the pin;
`git ls-tree -r --name-only` at the pin; `git show PIN:{corpus/fixtures/r98stream.c,corpus/fixtures/measure_audio.py}`
into scratch; `sha256sum` of both scratch copies; `grep`/`git grep`
queries as cited per finding; full reads of the four round-98 reports,
the wave `wwkd-plan.md`, and `review-common.md`/`review-roles.md`;
`mkdir -p` of the scratch path. Nothing else. No service, receipt, lock
or evidence file touched.

**Pin integrity.** Scratch `r98stream.c` sha256
`9f840a6b8b23196124270d96532b3b35b2b868d089aef4eb58ad2d6b0950d323` —
equals the author report's recorded fixture sha and the integrate note's
"verbatim both sides" value. Scratch `measure_audio.py` is the PIN blob
(git blob `50bf75fadb14324491cb632f99835b82d81482fa`, 55974 lines; the
file-level sha256 of my copy is `801e153b…`). All `measure_audio.py`
line numbers below are **PIN-blob lines**, not author-worktree lines.

---

## 1. Findings (ordered by severity)

Severity here = proven-ness × weight removed, for a simplifier. Every
item states: location, evidence, smallest correction, and whether the
absence is proven literally or the claim is behavioral/inferred.

### F1 (highest confidence, Python) — `_pwstream_r98_streaming_leg` is a dead alternate path: zero callers in the whole pinned tree

- **Where:** `corpus/fixtures/measure_audio.py` PIN-blob lines
  46961–46993 (33 lines + 2 blank).
- **Evidence:** `git grep -n "_pwstream_r98_streaming_leg"
  bb177513… --` over the entire tracked tree at the pin returns exactly
  one hit — the `def` itself. No call site exists in the r98 block, the
  dispatch, or any other family block; no dynamic dispatch exists (see
  the LSP-gap note). This is a **proven reference absence at the literal
  level, tree-wide**; not an LSP-semantic proof (no LSP device — §0).
- **Failure path (why it exists at all):** it is a second, parallel
  implementation of the §3.5 silent-link-transient handling
  (paused + no link + no error → one retry → named coverage block) that
  the family actually exercises through three other mechanisms:
  `_pwstream_r98_run`'s built-in retry (46631–46653),
  `_pwstream_r98_sweep_transient` (47178–47202), and the entries' inline
  handlers (e.g. 47551–47556, sb_run 48523–48535). The helper's own
  docstring (46963–46969) describes exactly the class the runner already
  handles — a dead duplicate authority for the same host class.
- **Smallest correction:** delete lines 46961–46993. Behavior-identical
  (uncalled). No armed row, receipt field, or report text depends on it
  (the author/integrate reports never mention the helper).
- **Classification:** observed (literal tree-wide grep at the pin).
  **Recommended deletion.** This is the one Python deletion that removes
  a whole second convention rather than a line.

### F2 (C, proven inert by source) — four write-only/dead observation fields and dead stores in `r98stream.c`

All in `corpus/fixtures/r98stream.c` at the pin; all proven by literal
occurrence census within the file (the only occurrences are the
declaration and, where listed, write sites; the line-961 hit for
`t_end_ms` is inside a printf **format string**, not a field reference):

| # | symbol | lines | status | smallest correction |
|---|---|---|---|---|
| a | `t_end_ms` | 128 (decl) | never assigned, never read; the `t_end_ms=` label at 961 prints `now_ms() − d.t0_ms` | delete the field from the declaration; the printed label is unaffected |
| b | `drained_flag` | 149 (decl), 378 (write) | write-only; `n_drained` (377) is the consumed signal | delete field + line 378 |
| c | `cap_sample_index` | 121 (decl), 316, 328 (incr) | write-only counter, never printed or compared | delete field + the two increments |
| d | `is_driving`/`is_lazy` dead stores | 358–359, 369–370 | both are unconditionally overwritten at `finish:` (933–934) before the only read (979). The `state`-mode stores at 856–857 are **live** (state mode jumps to `done:`, skipping `finish`) | delete 358–359 and 369–370 only |

- **Failure path:** none — these are pure weight; the printed summary
  (932–993) is byte-identical without them.
- **Classification:** observed (literal occurrence census in a single
  translation unit). **Recommended deletions.** Tradeoff for (c): the
  counter is harmless instrumentation; deleting it removes a future
  sample-index extension point (extension-point withdrawal = tradeoff,
  low value).

### F3 (C, proven inert by source) — dead no-op branch, dead computation, pure-alias helper, dead out-parameter

- **a. Empty stall branch** — lines 265–267:
  `if (d->mode && strcmp(d->mode, "stall") == 0 && !d->stall_at) { /* nothing */ }`.
  Empty compound statement; the condition has no side effects; the real
  stall arm is the next `if` (268–273). Delete 3 lines; behavior-identical.
- **b. `stride` computed then discarded** — line 293 assigns
  `uint32_t stride = …chunk->stride…`, line 332 is `(void)stride;`. The
  `(void)` cast is the code's own admission that the value is unused.
  Delete both lines; behavior-identical.
- **c. `arm_timer_rel` is a pure alias** — lines 560–563:
  `static void arm_timer_rel(struct data *d, int ms) { arm_timer(d, ms); }`
  with six call sites (496, 500, 511, 520, 532, 541). Single-line
  delegation; inlining `arm_timer` at the six sites is
  behavior-identical. **Tradeoff:** the name is the only surviving
  marker of the scout-lineage rel/abs distinction (the boundary's
  `r98bhold.c` lineage); deleting it removes an intent-marker name, not
  behavior. Duplicate authority; recommended deletion.
- **d. `make_params`'s `b_out` out-parameter is dead** — param at 615,
  `*b_out = b` at 631; both callers (798, 839) pass `&b` where `b`
  (declared 640) is never read afterward. Delete the param, line 631,
  and the caller-side declaration/argument; behavior-identical.
- **Classification:** observed (literal, single translation unit).
  **Recommended deletions.**

### F4 (C, candidate — behavioral proof NOT run) — three unused direct includes

- **Where:** lines 57 `<spa/param/props.h>`, 58 `<spa/debug/pod.h>`,
  59 `<spa/utils/result.h>`.
- **Evidence (literal):** zero occurrences of any symbol those headers
  provide — `SPA_PROP_`/`SPA_TYPE_Props`/`spa_props`: 0 hits;
  `spa_debug*`: 0 hits; `spa_strerror`/`spa_result*`: 0 hits (the C
  prints raw `-errno` at 726 instead of `spa_strerror`).
- **Smallest correction:** remove the three `#include` lines, then
  re-run the integration's own narrow check (`gcc -fsyntax-only
  $(pkg-config --cflags libpipewire-0.3) corpus/fixtures/r98stream.c`).
- **Classification:** reference absence proven at symbol level;
  **behavioral proof (compile after removal) not run** — transitive
  include risk means this is a candidate, not a proven deletion. This
  seat does not compile or edit.

### F5 (Python, duplicate observation) — the §3.5 coverage-block text is recorded twice for the same leg

- **Where:** inline handler 47551–47556 (entry 2, `r_gate_on_r{rep}`)
  vs `_pwstream_r98_sweep_transient` 47189–47192 (runs in every entry's
  `finally`).
- **Failure path:** for a `flags=autoconnect` leg that lands
  paused/no-error/no-callbacks, `_pwstream_r98_run` retries once
  (46631–46653); if the retry does not recover it returns
  `rec2["transient"]="autoconnect_link_transient"`. The sweep then
  appends `"{key}: autoconnect_link_transient (paused, no link, no
  error — the r98 boundary §3.5 host class)"` — **byte-identical** to
  what the inline handler already appended at 47553–47556. One blocked
  leg → two identical `coverage_blocked` rows.
- **Not fully redundant:** the inline condition (paused + no error,
  *any* cb_count) is a superset of the runner's retry trigger (which
  also requires `cb_count` absent/0), so the inline handler alone covers
  a paused-with-callbacks leg that the sweep would miss.
- **Smallest correction:** guard the inline append with
  `not rec.get("transient")` (or drop the inline append and accept the
  sweep as the single recorder, narrowing the inline branch to the
  cb>0 case). Either removes the double record without losing a case.
- **Classification:** observed (source-path trace; the double record is
  not observed in a live run — no run was made). De-dup proposed, not a
  plain deletion.

### F6 (Python, redundant authority + calibration mismatch) — the sandbox leg retry is a second retry layer on top of the runner's, and the recorded class undercounts

- **Where:** `sb_run` 48517–48535 (entry 6) vs `_pwstream_r98_run`'s
  built-in retry 46631–46653.
- **Failure path:** sandbox legs call `_pwstream_r98_run` with the
  default `retry_transient=True`; for a paused/no-error/no-cb sandbox
  leg the runner already retries once. `sb_run` then sees
  paused/no-error and spawns a **third** time (`legs[name + "_retry"]`).
  A warmup-unlinked sandbox leg is therefore up to 3 spawns, while the
  recorded class says `sandbox_warmup_unlinked (paused, no error, after
  one retry)` and the author report §6 claims "absorb … with **ONE**
  named retry". The code does up to two retries; the report and the
  class text undercount.
- **Smallest correction (two options):** (i) pass
  `retry_transient=False` in sb_run's first `_pwstream_r98_run` call so
  sb_run's retry is the one named retry (report then matches code);
  (ii) drop sb_run's retry and let the runner's retry + sweep name the
  class (loses the distinct `sandbox_warmup_unlinked` class and one
  recovery chance). Either is a behavior change — **not a clean
  deletion**; the calibration fix (i) is the smaller one.
- **Classification:** inferred from source paths; no live run. Report
  the mismatch; the lead picks the option.

### F7 (Python, redundant authority / duplicate observation) — three sequential full pw-dump passes to read two nodes in entry 3's preamble

- **Where:** `_pwstream_r98_serial` 46726–46729 and
  `_pwstream_r98_object_id` 46732–46736 each run a **fresh full
  `_pwstream_r98_graph()`** (attempts=2, timeout=60 s) just to extract
  one field via `_pactlmon_r85_node`. Entry 3 calls them at 48027
  (serial ns), 48029 (serial ns2) and 48085 (object id ns) — three full
  graph reads for two stable, seat-owned nodes; entries 1/2/4/5 each add
  one more.
- **Failure path:** the reader's own docstring (46659–46663) says a
  loaded shared graph can make pw-dump take tens of seconds; the author
  window measured a 3 m 20 s enumeration wedge. Worst case the route
  entry spends minutes in preamble dumps, and each pass is an
  independent wedge/timeout exposure for the same fact.
- **Smallest correction:** in entry 3, take one
  `g = _pwstream_r98_graph()` and extract serial(ns), serial(ns2),
  object_id(ns) from that single snapshot (the lookups are adjacent and
  the nodes are this seat's own private sinks, loaded and verified
  before the reads). Generalizing to every entry is possible but each
  entry-preamble read is deliberate per-entry isolation — leave those.
- **Tradeoff:** freshness — a single snapshot assumes the graph does not
  change between the three reads (microseconds apart, own nodes). The
  shared-reader convention (`_pactlmon_r85_node(g, …)` taking a graph)
  already supports this; no second convention is created.
- **Classification:** inferred (source paths + the reader's own
  documented cost). Proposal, not a deletion.

### F8 (Python, dead observation channel — tradeoff, recommend retention) — `_pwstream_r98_graph` builds a `ports` map nothing consumes

- **Where:** built at 46688–46694, returned at 46701; the only r98
  consumers (`_pwstream_r98_node_links`, `_pactlmon_r85_node`) read
  `nodes`/`links` only; `_pactlmon_r85_edges` — the one ports consumer
  in the shared reader — is never called with an r98 graph.
- **Evidence:** literal — no `["ports"]` or `.get("ports")` read of an
  r98 graph anywhere in the pinned blob.
- **Why retain anyway:** the docstring pins "the r85 graph shape
  {nodes, ports, links}" — shape parity with the shared reader is a
  deliberate single convention; trimming `ports` would create a
  divergent local shape (a second convention). **Classified as an
  extension-point withdrawal = tradeoff; recommended retention** (or a
  one-line comment noting the channel is currently unconsumed).

### F9 (C, stale names / stale doc — naming findings, no deletion)

- **a. `last_bufid` holds the requested frame count, not a buffer id**
  (line 350: `d->last_bufid = (uint32_t)(b->requested & 0xffffffff)`).
  The Python arms it *as* the request (47622–47626, 47660, 47815–47819,
  geo `requested` 47639–47640), so the armed semantics are self-consistent;
  the C field name misleads. Renaming would break the armed field-name
  contract with the receipts — **do not rename**; document only.
- **b. `last_nbufs` holds frames-per-buffer, not a buffer count** —
  line 349 overwrites `b->size` with the frame count and line 352 then
  stores it. The Python arms `maxsize == nbufs*stride` and
  `nbufs ∈ {12288, 13375}` (47591–47607) — consistent as a *frames*
  law; the name says otherwise. Same prescription: document, don't rename.
- **c. `time_rc_before` is reused for the post-deactivate rc** (line 868,
  printed as `get_time_after_deactivate_rc` at 869). Stale name inside
  the `time` branch; no deletion.
- **d. The header's drain line is a stale mechanism claim** — line 40:
  "drain — queue N buffers then pw_stream_flush(drain=true)". No
  N-buffer pre-queue exists anywhere in the file; the flush fires from
  `on_process` at cb ≥ 3 (275–279) or from the timer's `drain_at`
  (487–498). The doc describes a mechanism the code does not implement.
  Smallest correction: reword the comment (comment-only change).
- **Classification:** observed (literal). No deletions; (d) is a
  comment-only correction candidate.

### F10 (extension points with no harness caller — tradeoff class, recommend retention)

The role requires classifying any withdrawal of an extension point as a
tradeoff. All of the following are **unused by the committed harness**
(literal grep over the pinned blob) but are live CLI surface of the
committed fixture:

| extension point | C lines | harness usage |
|---|---|---|
| `props` mode | 921–926 | no `["props", …]` mode call anywhere in the r98 block |
| `no_params=` option | 672, 835–837 | never passed (the error case `case=no_params` at 811–819 is a separate mechanism) |
| 2-channel branch | 626–627, 894–895 | `channels=` never passed (default 1; capture accounting silently no-ops for stereo — frames stay 0) |
| flag tokens `map_buffers`, `no_convert`, `async`, `early_process`, `rt_trigger_done` | 573–583 | never armed by the family (the scout/boundary measured some via their own probes) |
| `nbuf=` option | 48 (doc), 96, 275, 648, 667 | passed only as `nbuf=5` (47845, 47885); only `d->nbuf > 0` is ever consulted — but `nbuf=0` would disable the callback-driven drain flush, so the option is a live switch with a single used value, **not** dead |
| `wd=` param of `_pwstream_r98_run` (46582/46601/46647) and `wd`/`env` of `_pwstream_r98_prof` (46996–46997); `attempts=` of `_pwstream_r98_load_ns` (46810) | — | no call site supplies them (all 47 `_pwstream_r98_run(` occurrences inspected; 5 `_pwstream_r98_load_ns` sites use the default) |

Deleting any of these withdraws surface that the scout/boundary lineage
documented and that a later round may arm; **recommended retention**,
except the `wd` parameter of `_pwstream_r98_run`, which is a plain dead
parameter (deleting it is behavior-identical — `cwd=None` is `Popen`'s
default — and no extension intent is recorded anywhere). That one is a
**recommended deletion** (small).

---

## 2. What the evidence supports

- **Supported (measured/literal):** every zero-caller and write-only
  claim above, at the literal level, tree-wide at the pin; the pin
  integrity of both audited files; the block boundaries (46327–48676;
  dispatch 55142–55165; argparse 54390; mutex 54400; ternaries
  55944/55964).
- **Supported (source-path trace, not live-observed):** the F5 double
  record and the F6 triple-spawn path — both are reachable paths read
  from the source; no battery was run, so their *frequency* is unknown.
- **Calibration cross-check that PASSED:** the six entries' leg
  assignments in the pinned source sum to exactly the declared census —
  core 15 / run 18 / route 12 / cap 4 / xw 4 / sbx 14 = **67** (entry 1:
  47246–47470; entry 2: 47526–47982; entry 3: 48039–48123; entry 4:
  48205–48302; entry 5: 48363–48465; entry 6: 48575–48653). The declared
  "six entries, 67 legs" matches the source, leg for leg.
- **Blocked / not resolvable in this checkout:** the author's two green
  receipts (`corpus/live/runs/20261016T101046237597Z-pwstream-r98/`,
  `…101258039942Z-pwstream-r98/`) and the wedge receipt
  (`…092555426767Z-…`) are cited by the author/integrate reports but
  **do not exist in this tree** — `corpus/live/runs/` here contains no
  `*pwstream-r98*` dir and `corpus/live/` has `r98-boundary`/`r98-scout`
  but no `r98-author` dir. They are untracked author-environment
  evidence, not carried (the integrate note discloses exactly this). I
  did not need them for any finding above and did not fabricate their
  contents; nothing in this report depends on them.

## 3. Residual risks and explicit checks NOT run

- **No LSP reference check** (no `lsp` device in this seat's toolset) —
  all absence claims are literal greps; a semantic check could in
  principle find references literal grep cannot (none is plausible for
  these names, but the distinction is recorded, per contract).
- **No compile** — the F4 include removals are unproven behaviorally;
  `gcc -fsyntax-only` after removal is the gate before landing them.
- **No run of any family** (this seat is not the verifier; the prior
  operator family jobs are finished and shared daemons were left
  untouched).
- **No before/after experiment** — every "behavior-identical" claim is
  a source-level argument (empty body / write-only / pure delegation /
  uncalled), not a measured A/B.
- **Not audited:** the other families' blocks (r90/r93/r99/r100), the
  shared helpers the r98 block borrows (`_pactlmon_r85_*`,
  `_pwcat_r83_*`, `_pwprof_r89_*`, `_capture_*`, `_playback_r78_*`,
  `_alsapw_r84_*`, `_loopback_r79_oracle`) beyond the one shape check
  the object-id finding required, and the receipts' contents.
- **Deliberately not proposed:** renaming `last_bufid`/`last_nbufs`/
  `time_rc_before` (would break the armed field-name contract with
  frozen receipts); trimming `_pwstream_r98_graph`'s `ports` (shape
  parity with the r85 reader — F8); any of F10's extension points.

## 4. Net effect if the recommended deletions landed

~45 lines of dead weight (33 Python + ~12 C) plus two redundant-authority
fixes (F5 de-dup, F6 calibration), with **no armed row, receipt field,
coverage class, or report claim lost** — the family's measured surface
(67 legs, the §3.5 named-block path, the recorded-not-armed rows) is
untouched. The next deletion past this set (F8's `ports`, F10's
extension points) would trade convention parity or fixture surface for
trivial weight — that is where this inventory stops.

## 5. Artifacts and attribution

- **This report:** `reports/round-98/r98-simplifier.md` (the only
  tracked-path write by this seat).
- **Scratch:** `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r98-simplifier/`
  — `r98stream.c` (pinned copy, sha256 `9f840a6b…`, equals the author's
  recorded fixture sha) and `measure_audio.py` (pinned blob copy, git
  blob `50bf75fa…`). Both extracted with `git show PIN:path`; no
  worktree file was read for source claims.
- **Inputs read (lead-authored / round evidence):**
  `.ufo/waves/shokunin-train-20261016-w24/{review-common.md,review-roles.md,wwkd-plan.md}`;
  `reports/round-98/{r98-scout.md,r98-boundary.md,r98-author.md,r98-integrate.md}`.
- **Attribution:** scout/boundary/author/integrate reports are their
  seats' work, quoted only as provenance; the C fixture's header
  comments (lines 1–51) are the author's own record of the
  boundary-derived deltas and are preserved verbatim here — nothing in
  this report proposes touching them. All findings above are this
  seat's, from the pinned bytes. Advisory only: no round admitted, no
  canonical verdict claimed, nothing shipped.
