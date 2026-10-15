# r82 SIMPLIFIER — YAGNI/dead-code review of the `aa03c347` diff (read-only, patch NOT applied)

**Seat** simplifier (r82) · **host** devin · **scope** the landed diff only:
`corpus/fixtures/measure_audio.py` **+2170/−3** at `aa03c347`, family block
`:14179`–`:16311` (8 entries / 76 legs). **Writes**: this report +
`corpus/live/r82-simplifier/` only. **No tracked write, no commit, the patch
is NOT applied to the fixture.**

**Custody / tree state at report time**

- Fixture sha256 **`eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4`**
  = the author-pinned final sha = working tree = `git show HEAD:…` (all three
  re-derived at report time; `corpus/live/r82-simplifier/proofs/sha256.txt`).
- HEAD moved `aa03c347` → `fd0bc8b0` → `0556d5df` → `d8441a17` → `1e88e8e2` →
  `b307713e` during the window (sibling seats' commits). None touches
  `corpus/fixtures/` — the fixture sha is constant, and
  `git status --porcelain` shows **zero modified tracked files** at report
  time (the r82-simplifier paths are all new untracked paths, like every
  other `corpus/live/rXX-*` seat dir).
- **No `lsp` device answers this file on this substrate.** The only external
  device present is the `rea` Ghidra/native-REA MCP (binary/JS artifacts —
  its subject format has no Python source). Recorded unavailable: all
  reference proofs below are literal `grep`/AST over the single committed
  file plus an executed differential on scratch copies.
- **probeParent**: exactly one read-only `ufo-labrat` was dispatched (agent
  `1e41d4df`; report verbatim at `proofs/labrat-probe.txt`). That seat had
  read/grep tools only (no exec), so its dynamic checks could not run; its
  independent static census PASSed all eight predicates and surfaced two
  nuances (folded into T10 and §5). The executed differential was run by
  this seat (`proofs/differential.py`, all PASS).
- **No fresh full-family replay.** A sibling r82 run was live during the
  window (`pid 4076806`, `timeout 900 … --probe-ffmpeg-r82`), so a folded
  replay would have disturbed a sibling's canonical run and read contention
  noise. The four pinned runs (`run1`/`run2`, `final3`/`final4`) are the
  replay oracle; their verdict surfaces are independently re-verified
  identical here (`proofs/verdict-stability.txt`, both pairs 8/8 entries,
  only pid-stamped keys and the live-graph `-sources/-sinks` text excluded).

**Proof classes used below** — `[S]` static reachability (call-site census /
AST; no path to the deleted code), `[R]` receipt 0-hit across all four
pinned runs, `[D]` executed differential base-vs-folded on scratch copies,
`[O]` replay-oracle stability of the pinned pairs.

## 0. Summary

| # | item | class | base lines | Δ | proofs | tier |
|---|---|---|---|---|---|---|
| T1 | `FFPW_R82_FFPLAY` dead constant | dead constant | 14267 | −1 | S,D | A |
| T2 | `_ffpw_r82_last_node` `require_linked` param + branch | dead param/branch | 14376, 14382–14384 | −4/+1 | S,D | A |
| T3 | `_ffpw_r82_shot` `env_extra` param + env block | dead param/branch | 14509, 14512–14519, 14521–14522 | −10/+2 | S,D | A |
| T4 | `_landed_on` `taps` param + early return | dead param/branch | 15358, 15379–15380 | −3/+1 | S,D | A |
| T5 | entry-6 artifact check (never true) | dead conditional | 15969–15972 | −4 | S,R,D | A |
| T6 | device missing-row predicate | superseded predicate | 14826–14828 | −3 | S,R | B |
| T7 | `_star` write-only local | dead store | 14839 | ±0 | S,R,D | A |
| T8 | entry-2 `_cap` `post` param + argv slot | dead param/expression | 14947–14948, 14952–14953 | −2/+2 | S,D | C |
| T10 | `_ffpw_r82_kill_watch` `proc is None` branch + `label` | dead guard | 14389, 14391–14392, 14456 | −4/+2 | S,R,D | C |
| T11 | `_ffpw_r82_tone_windows` falsy-path guard | dead guard | 14593–14597 | −5/+3 | S,D | C |

Totals: **−37/+12, net −25 lines** (17 388 → 17 363); 11 hunks; every hunk
inside the r82 family block. **Tier A** = never-executed code; **Tier B** =
verdict-superseded predicate with a declared message-only delta; **Tier C** =
dead guards / dead payload params, provably unreachable from the current call
graph — separable hunks the operator may retain as input-contract guards.

## 1. Deliverable

- `corpus/live/r82-simplifier/r82-simplifier.patch` — sha256
  `3a48a7514f22583015b66a86e2865b2f1eafecfa3901d3ae3c9849a22305f200`,
  `git apply --check` clean against the committed fixture
  (`proofs/patch-check.txt`); **not applied**.
- `corpus/live/r82-simplifier/folded/measure_audio.py` — sha256
  `b8dfaf37cb82a9f9711f6084e1a6678ecd54a1499ee6358394c3784871d8d808`,
  17 363 lines; `python3 -m py_compile` clean (`proofs/pycompile.txt`); a
  fresh `patch -p1` of the patch over a scratch base copy is **byte-identical**
  to it (`proofs/differential.txt` D0). `folded/build_artifacts.py` is the
  unchanged sibling copy so the fold can be run live from its own ROOT.
- `corpus/live/r82-simplifier/proofs/` — base copy (== committed fixture),
  `fold-r82-simplifier.py` + `fold-apply.txt` (13 exact-match replacements,
  each asserted to match once), `static-proofs.py`/`.txt` (14/14 PASS),
  `receipt-census.py`/`.txt` (23/23 PASS), `verdict-stability.py`/`.txt`
  (both pinned pairs identical), `differential.py`/`.txt` (D0–D6 all PASS),
  `labrat-probe.txt`, `sha256.txt`, `patch-check.txt`, `pycompile.txt`.

## 2. Items — remove / proof / receipts

### T1 — `FFPW_R82_FFPLAY` is definition-only `[S][D]`

**(a) Remove** `:14267` (`FFPW_R82_FFPLAY = "ffplay"`).

**(b) Proof.** AST census over the whole file: 0 `Load` references
(`static-proofs.txt` T1); the single literal occurrence is the definition.
Entry 8 uses the literal `"ffplay"` in `fbase` (`:16217`) and
`shutil.which("ffplay")` (`:16199`). The region census shows it is the
**only** definition-only module-level name in the block.

**(c) Receipts.** No leaf can reference a constant that is never read; the
four pinned runs are unaffected. `[D]` folded-copy census re-run: name absent.

### T2 — `_ffpw_r82_last_node(..., require_linked=False)` never supplied `[S][D]`

**(a) Remove** the parameter at `:14376` and the branch at `:14382`–`:14384`:

```python
            if require_linked and not (nd.get("consumers") or
                                       nd.get("producers")):
                continue
```

**(b) Proof.** All **22** call sites (line list in `static-proofs.txt` and
`labrat-probe.txt`) pass at most `(leg)` / `(leg, src="holder")`; none passes
`require_linked`. The parameter is therefore always `False` and the
`continue` can never execute. `[D]` D2: base vs folded return identical
leaves on linked / unlinked / non-main / empty synthetic legs; the removed
surface is documented (base `require_linked=True` → `None`, folded →
`TypeError`) and is not used by any call site.

**(c) Receipts.** The branch has no leaf; the four pinned runs are
unaffected (no `require_linked` anywhere in the fixture).

### T3 — `_ffpw_r82_shot` `env_extra` never supplied `[S][D]`

**(a) Remove** the parameter at `:14509`, the `env = None` / `if env_extra:`
block at `:14512`–`:14519`, and the `env=env` argument at `:14522` (with no
`env_extra` the callee's `env=None` is exactly `subprocess.run`'s default).

**(b) Proof.** All **7** AST call sites (`d0`'s rep loop = 1 site / 2
executions, plus `d1`–`d6`; list in `static-proofs.txt`) pass a bare argv
list; none passes `env_extra`, so the block is unreachable. `[D]` D3:
`_ffpw_r82_shot(["true"])`, `(["false"])`, `(["/bin/echo","r82-probe"])`
return byte-identical dicts from base and folded.

**(c) Receipts.** The block writes no leaf; the device entry's 8 legs are
unchanged.

### T4 — `_landed_on(..., taps=True)` never supplied `[S][D]`

**(a) Remove** the parameter at `:15358` and the early return at
`:15379`–`:15380`.

**(b) Proof.** All **8** call sites (the `p0`/`p1`/`p2`/`p3`/`p4`/`p5`/`p6`/
`p8` routing checks) use the default; none passes `taps`, so
`if not taps: return` can never execute. (The `taps=False` at `:15332`
belongs to the sibling `_play` closure for `p9_bad_server`, which is checked
inline and never routed through `_landed_on`.) `[D]` folded-copy census: no
`taps` on `_landed_on`.

**(c) Receipts.** The guard produced no leaf; the playback entry's checks
are unchanged.

### T5 — entry-6 artifact check can never be true `[S][R][D]`

**(a) Remove** `:15969`–`:15972`:

```python
        out = leg.get("out") or {}
        if out.get("exists") and (out.get("bytes") or 0) > 44:
            failures.append(f"err {lname}: a refused leg must not "
                            f"produce audio — {out}")
```

**(b) Proof.** All six `_ffpw_r82_leg` calls in
`ffpw_error_classes_r82_entry` (`:15929`, `:15932`, `:15935`, `:15939`,
`:15942`, `:15946`) omit `out_path`; `_ffpw_r82_leg` stores
`"out": (_gst_r81_wav_inspect(out_path) if out_path else None)`
(`:14501`–`:14502`). So `leg.get("out") or {}` is always `{}`, and
`out.get("exists")` is always `None` → the condition is never true. The
check is dead as written (its intent — no audio from a refused leg — is
simply unmeasured; deleting it changes nothing that ever ran).

**(c) Receipts.** `[R]` all four pinned runs carry `"out": null` on e1–e6
(24/24 leg records, `receipt-census.txt` B) and `failures: []`; the arm has
**0 hits** and can have none. `[D]` folded copy still runs the identical
rc/class/token assertions for e1–e6.

### T6 — device missing-row predicate is superseded `[S][R]`

**(a) Remove** `:14826`–`:14828`:

```python
    if any(rows.get(d) is None for d in want_flags):
        failures.append("devices: a pinned audio device row is missing "
                        f"entirely — {rows_seen[0]}")
```

**(b) Proof.** The predicate implies the preceding per-device loop
(`:14818`–`:14821`) already appended at least one failure: for any missing
`d`, `rows.get(d) is None != flags` → the mismatch message fires. So the
predicate can only add a *duplicate diagnostic* to an already-red failures
list — it cannot change any verdict (pass→fail or fail→pass). 0 hits across
all four runs.

**(c) Receipts.** `[R]` all four runs: every pinned device row present with
the pinned flags (`alsa DE / pulse DE / jack D. / oss DE / sndio DE`), no
`pipewire` row, reps identical (`receipt-census.txt` E) — the arm never
fired. **Declared tradeoff**: on a future host where a pinned row is
*missing*, the failures list loses this one message (the device-named
per-row mismatch message remains and the run still fails). That is a
message-level change in an already-failing state, not a verdict change —
operator's call; drop this hunk to keep the duplicate diagnostic.

### T7 — `_star` is a write-only local `[S][R][D]`

**(a) Change** `:14839` to discard the second element:
`rows_pw, _ = _ffpw_r82_enum_rows(leg.get("out") or "")`.

**(b) Proof.** AST dead-store scan: `_star` has 1 `Store` and 0 `Load`
references in the whole file. Unlike `d3`/`d4`, the `d2` leg records only
`leg["rows"]` (no `leg["starred"]`), so the value is never serialized.

**(c) Receipts.** `[R]` the `d2_sources_pipewire` leg has no `starred` key in
any of the four runs, while `d3`/`d4` do (`receipt-census.txt` C). `[D]`
folded census: `_star` absent.

### T8 — entry-2 `_cap` `post` is never supplied `[S][D]`

**(a) Remove** the parameter at `:14947`–`:14948` and the `list(post or [])`
argv slot at `:14952`–`:14953` (the concatenation stays `base + list(pre) +
["-i", src] + ["-t", …]`).

**(b) Proof.** All **15** AST entry-2 call sites (`c0`–`c14`; 17 executions,
`c3`'s rep loop site runs 3×) pass at most `(name, pre, src)` positionally
with kwargs after; none passes `post`, so the slot is always `[]`. (The other
`_cap` closure, entry 4, has no `post`; 22 `_cap` AST sites total across both
closures, 0 with `post`.)

**(c) Receipts.** The argv is redacted as `<out>`/`<tmp>` in receipts; the
effective argv is unchanged because the slot was always empty.

### T10 — `_ffpw_r82_kill_watch`'s `missing` branch is unreachable `[S][R][D]`

**(a) Remove** the parameter at `:14389`, the guard at `:14391`–`:14392`, and
the second argument at the call site `:14456` (the sole call site):

```python
def _ffpw_r82_kill_watch(proc):
    """Timed-event kill for a watch proc (the pump) — SIGKILL its pgid."""
    if proc.poll() is not None:
```

**(b) Proof.** `_ffpw_r82_kill_watch` has exactly **one** call site (`:14456`),
fed by the sole `kill_watch` event — `(2.0, "kill_watch", "pump")` at `:15745`,
built in the same call that passes `watch={"pump": pump}` at `:15741`, where
`pump = _ffpw_r82_pump(...)` is a live `Popen`. `procs.get("pump")` is
therefore never `None`, and `label` is referenced nowhere else. The
`already_exited` branch is **retained** (a pump that dies early is a real
failure path). `[D]` D4: live child → `{"sigkilled": True}` + child dead for
both copies; exited child → identical `{"already_exited": 0}`.

**(c) Receipts.** `[R]` all four runs: the 12 `kill_watch` firings carry
`{"sigkilled": true}` and no `missing`/`already_exited` (`receipt-census.txt`
D). **Disclosed failure-path delta** (also flagged by the labrat): if
`procs.get(arg)` were ever `None`, base returns `{"missing": label}` while
the folded code would raise inside the `except Exception`-guarded event loop
and record `{"exc": …}`. No call site can produce that state today (static
proof); the hunk is separable if the operator prefers to keep the guard.

### T11 — `_ffpw_r82_tone_windows`'s falsy-path guard is unreachable `[S][D]`

**(a) Remove** the ternaries at `:14593`–`:14597`, pinning the helper's input
contract to a path:

```python
    path = Path(path)
    insp = _capture_wav_inspect(path)
    pcm = _playback_r78_pcm_array(path, insp)
```

**(b) Proof.** All **4** call sites pass a non-empty path expression:
`:14957` (`out` = a tmpdir wav path), `:15303` and `:15717` (paths already
gated by `Path(path).exists()`), `:15747` (`cap`). `if path` / `if path is
not None` are therefore always true. The **`pcm is None` "unsupported"
branch is preserved and reachable** (non-s16 input) — only the falsy-path
guard goes. `[D]` D5: tone-file and missing-file outputs identical base vs
folded.

**(c) Receipts.** No leaf changes; the tap/tone windows are produced exactly
as before.

## 3. Checked and NOT dead (explicitly cleared)

- **`_ffpw_r82_kill_watch`'s `already_exited` branch** — reachable: the pump
  (`ffmpeg -re -stream_loop -1`) can exit on its own error path. Retained.
- **`_ffpw_r82_block(loads=None)`** — two callers (entries 1 and 8) omit
  `loads`; both arms are live. Retained (contrast r80-F9, whose sole caller
  always passed the dict).
- **`_ffpw_r82_tone_windows`'s `pcm is None` branch** — reachable
  (non-s16/non-stereo input). Retained.
- **`_ffpw_r82_kill_watch`'s `try/except OSError`** — a pgid can be gone
  (ESRCH) between `poll()` and `killpg`; retained.
- **`res.get("skipped")` guards in t1/t2** — `skipped: "not_listed"` is a
  real teardown outcome (2 occurrences in the final3 receipt); retained.
- **`_ffpw_r82_sample`'s `live` / `live_map` leaves, `pump_relinked_to`,
  `holder_consumers`, `a5_realization`, `star_vs_pactl`, `p11_env_target`,
  `start_time_epoch_s`** — receipt-surface-only evidence fields, deliberately
  recorded-not-gated (the family's honest-leaf convention). No deletion.
- **Error-class tuple** — every entry except the `other_error` catch-all is
  realized in the four runs (`receipt-census.txt` G); `other_error` is the
  documented fallback. Retained (r81-T3 precedent).
- **`FFPW_R82_PROP_DROP`'s `window.x11.display`** — doubly filtered (the
  `FFPW_R82_PROP_KEEP` prefix set already excludes it), i.e. a redundant set
  element. Retained as documented drop vocabulary (r81 kept its drop set).
- **Wiring** — `--probe-ffmpeg-r82` is consumed by all four surfaces (arg at
  `:16436`, mutex sum `:16444`, dispatch `:16735`, mode `:17358`, suffix
  `:17378`); the receipt carries `mode: "probe-ffmpeg-r82"` / `-ffmpeg-r82`.
  No dead config key.

## 4. Below the bar (reported, retained)

- **Parameterization with no override callers**: `_ffpw_r82_leg`'s
  `byte_cap` (the triple-bound flood guard), `_ffpw_r82_shot`'s `timeout_s`
  and `_ffpw_r82_reap_watch`'s `timeout_s` (the helpers' primary bounds),
  `_play`'s `wall` (a pass-through of `FFPW_R82_WALL_S`, never overridden),
  `_refusal`'s `want_rc`/`want_class` (all three refusals are by design
  251/`ff_io_error`). Deletable by the same reachability argument as T8, but
  they are bound/assertion vocabulary, not dead flow — retained per the r81
  convention. T8 is in the patch because its dependent argv slot is a dead
  *expression*, not a knob.
- **Never-fired diagnostic arms**: the `hang_killed` arm of the c3 envelope
  (0/12 realizations), the `plugin_rc0` arm of a5 (0/4), the `wallcap` /
  `bytecap` kills (0 across all 76 legs × 4). All are legitimate
  falsification arms (the scout/boundary observed the other side), so they
  stay — pruning them would delete the envelope the round deliberately armed.

## 5. Limits / residual risk

- **No fresh folded full-family replay** (sibling r82 run live at analysis
  time — recorded above). Per item the proof is static reachability `[S]`
  plus 0-hit receipts `[R]` plus the executed differential `[D]`; the replay
  oracle `[O]` is the author's two pinned pairs, independently re-verified
  verdict-identical here. A live folded replay remains the operator's
  strongest end-to-end confirmation and can be run from `folded/` (ROOT
  resolves to `corpus/live/r82-simplifier/`, receipts land under
  `corpus/live/r82-simplifier/live/runs/`).
- **T6's message delta** (missing-row state) and **T10's None-input delta**
  are disclosed above; both are unreachable/verdict-invariant today. The
  labrat seat independently flagged exactly these two plus the fact that its
  own dynamic checks could not run (no exec tool) — all three are addressed.
- The r82 family is live-host data: raw receipts are **not** byte-identical
  across replays (bytes written, module indices, pid-stamped names, the
  foreign-node enumerations), so "byte-identical replay" is only meaningful
  on the verdict surface — which is what `verdict-stability.txt` proves for
  both pinned pairs. The deleted code produces no verdict-surface leaf in
  any of them.
- No semantic LSP proof (device unavailable, recorded); the reference proofs
  are grep/AST + executed differential.

## 6. Reproduction

```
cd ~/Projects/shokunin/audio-shokunin
python3 corpus/live/r82-simplifier/proofs/static-proofs.py corpus/fixtures/measure_audio.py
python3 corpus/live/r82-simplifier/proofs/receipt-census.py
python3 corpus/live/r82-simplifier/proofs/verdict-stability.py
PYTHONDONTWRITEBYTECODE=1 python3 -B corpus/live/r82-simplifier/proofs/differential.py
git apply --check corpus/live/r82-simplifier/r82-simplifier.patch   # clean, not applied
```

All four scripts exit 0; `patch-check` is a check only — the tracked fixture
is untouched (`git status` clean, fixture sha `eb865760…`).
