# R75 reviewer (audio) — correctness review of the landed diff

Seat: **reviewer** (leaf; report-only, no dispatch, no git mutation). Wave
`shokunin-train-20261101-w14`. Host `plazir27`, kernel `7.2.3-arch1-3`,
Python 3.14.7. Reviewed revision **`db46fba`** (`git show db46fba` =
`corpus/fixtures/measure_audio.py` +936/−3, `reports/round-75/r75-author.md`
+174). Committed fixture blob **`30eac683a94c3434274b56c4773b84ce577a3ac4`**
(`git hash-object` == `git rev-parse HEAD:corpus/fixtures/measure_audio.py`);
worktree clean against HEAD (`git status --porcelain corpus/fixtures` = 0
lines). Tools: pacat/paplay **17.0-98-gb096** (libpulse 17.0.0, libsndfile.so.1,
`sf_open_fd` present in the binary), aplay **1.2.16**, ffplay **n9.0.1**,
pactl 17.0, PipeWire daemon live (12 ALSA playback devices / 3 cards).

**Bottom line.** The landed arm is a correct, insertion-only extension: the
three prior-expression edits are exactly the mutex sum + `mode` + `suffix`
chains and each is a pure head-insert / tail-append with every prior clause
preserved verbatim in order (verified against r73/r74's own edit shape); the
new family reproduces byte-identically (3 independent sandbox replays, sha
`0829a598…`, `cmp`-equal to the on-disk receipts); no prior row moved
(prior-mode replay below); every headline claim in the commit message and the
author report that I could re-measure holds. Findings are **latent** issues
(a dead regex alternative, one unfiltered racy line, one convention deviation,
one wording drift) — no blocking defect, no active false claim.

## §1 What was verified (evidence first)

| # | check | command / artifact | result |
|---|---|---|---|
| E1 | replay on committed tree, 3× | sandbox ROOT `corpus/live/r75-reviewer/replay/corpus` (fixture = committed blob, `git hash-object` match), `bash corpus/live/r75-reviewer/replay3.sh` | **rc=0 ×3**, receipts `…T165540209609Z`, `…T165633987131Z`, `…T165727785190Z` (scratch `live/runs/`), all sha256 `0829a5986bb6ca70c5c9b06b50bf661e9c8dbbe7cddefac5b16e860e2c2a76d4`, 99159 B; `cmp` **byte-identical** to canonical `…T165017429491Z`; stdout `failures: {}`; stderr logs 0 B |
| E2 | 118/118 prior clauses preserved | `python3` clause-diff of `mode`/`suffix`/`sum` lines, HEAD~1 vs HEAD (scratch `clauses.py` logic in §5) | `mode`: 117→118 clauses, `SequenceMatcher` opcodes = **[(`insert`,10,10,10,67)]** (head insert only); `suffix`: same, `insert` at 12; prior 117 `("literal", args.flag)` pairs **verbatim in order**; `sum`: 118→119 entries, `new[1:]==old[1:]+['args.probe_consumers2_r75']`, 119 distinct, **no duplicates** |
| E3 | same edit shape as r73/r74 | same script on `febf34b` (r73) and `168b165` (r74) | r73/r74 both = single head-insert in `mode`/`suffix` + tail-append in `sum` → r75 shape is the family's precedent, not a new shape |
| E4 | insertion-only at the data level | sandbox replay of the **prior** mode `--probe-consumers-r73` (`replay_prior_r73.sh`, rc=1 = the mode's own documented forks) | 27 entries, keys == committed r73 receipt; **all 9 member entries byte-equal**; only 2 leaves differ: `consumer_pwcat_ops_r73_probe/daemon_live/default_sink` (`…SPDIF__sink` vs `…SPDIF__sink.2`, F11) and `/pacing_instant/wall_s` (4.044 vs 4.033); failure set **identical** to the committed r73 receipt's |
| E5 | prior *base* rows untouched in the r75 receipt | `json` leaf-compare vs committed r73 receipt | 17 shared measurement keys, **0 differing**, all 6 meta sections equal (author's "17 shared base rows" claim reproduces exactly) |
| E6 | 27/27 verdict groups transport-invariant | receipt `consumer2_*_r75_probe` | 9 members × 3 consumers = **27 groups, 0 forks**, `failures: []` per entry; distinct verdicts: paplay 2, aplay 2, ffplay 3 |
| E7 | `_consumer2_tail` vs raw surfaces | 14 distinct path-bearing line shapes extracted from `corpus/live/r75-scribe/raw/*` fed through the committed `_consumer2_tail` | **0 leaks** (`/home`, `/tmp`, `vgpnk` absent from every scrubbed tail); real member lines are 147–152 chars, i.e. inside the `[-160:]` window (fixture `:1021`) |
| E8 | tail stability probes | 20 + 45 direct `paplay_leg` file-arm calls (9 members × 5, +20 on `dec_hcom`); 5 direct ffplay writerless-fifo runs | paplay filtered tails: 20/20 and 45/45 identical per member (accept members = `Time: 0.000 sec; Latency: 34750 usec.`, reject members = `Failed to open audio file.`); raw last line 12/12 = `Draining connection to server.` (correctly filtered); ffplay last line 5/5 = the `nan … fd= 0 …` status line, rc 123 each |
| E9 | kill-class cells are comparable to r74's | `_nowriter_cell` (`:2335-2387`) vs `pwcat_ops2_entry`'s writerless cell (`:1771-1808`) | field-for-field identical (`blocked`,`wchan`,`sigterm_wait_s`,`sigterm_immune`,`exit_code`,`waited_s`; r75 adds `argv`); waits are the same declared bounds (3.0 s / 1.0 s) → the −15/−9/123 triplet is comparable by construction; receipt values: paplay −15 `wait_for_partner`, aplay −9 `wait_for_partner`, ffplay 123 `hrtimer_nanosleep` |
| E10 | aplay "daemon-coupled plugin route" attribution | process-local severing only (`PIPEWIRE_RUNTIME_DIR`+`XDG_RUNTIME_DIR` → empty tmp; live daemon untouched) | `aplay -D pipewire` **rc=1** `audio open error: Host is down`, bare `aplay` **rc=1** same, `aplay -D null` **rc=0**; `PULSE_SERVER=unix:/nonexistent` leaves all three rc=0 → the coupling is to PipeWire (comment `:2631-2634` accurate), not to the Pulse layer |
| E11 | paplay `sf_open_fd` mechanism claim | `ldd /usr/bin/paplay`, `strings /usr/bin/paplay` | links `libsndfile.so.1`; strings include `sf_open_fd`, `sf_close`, `sf_read_raw` → the name-blind fd-open attribution reproduces |
| E12 | argparse / mutex wiring | `--probe-consumers2-r75 --probe-lavfsweep-r74` and a 3-flag call | `measure_audio.py: error: choose one probe mode`, **rc=2** both; flag registered once (`:3023`), present in `--help`, in the sum (`:3025`), in `mode` (`:3782`) and `suffix` (`:3802`) chains |
| E13 | no hidden mutation by the mode | no-arg `build_artifacts.py` invocation forwarded by the r75 dispatch | `diff -rq corpus/artifacts <sandbox artifacts>` → **identical**; `git status --porcelain corpus/artifacts` = 0 → artifacts are regenerated byte-deterministically, prior rows cannot drift from that path |
| E14 | fresh-tree viability of the arm | `git ls-files` for all 9 members | all 9 r75 members (round-66/68/69) are **tracked** (unlike the r74 family, which must generate its members) → the r75 dispatch cannot crash on a missing member in a fresh clone; the r75 block also matches the r73 caller convention (no per-member existence guard in either) |
| E15 | receipt shape / error paths | receipt `consumer2_*` keys; `main()`'s `failed = {k: v["failures"] …}` (`:3806`) | group dicts are the r73 shape `{"transports":[…],"verdict":[…]}` (r73 receipt checked), leg keys `input, exit_code, …, error, stderr_tail, named, seekable` match r73; all 12 new entries carry `failures`, so the aggregation path raises no `KeyError`; `--raw`, empty-writer, blocked and reject legs all populate `error` per the r73 convention (with the §2 R3 exception) |

**Caller/definition checks (device disclosure).** No `lsp` device is present in
this seat's toolset, so the seat-card LSP path (`status`→`references`/
`definition`/`diagnostics`) was **not available**; caller and definition checks
were done by text search plus execution: every new helper is called from exactly
the sites listed in §4 (`grep -n` on the committed blob) and the module was
imported and its legs/entries executed (E1, E4, E8) — the strongest available
substitute for a semantic references query on a single-file Python fixture.
No `lsp` cold-start empty result is reported as absence.

## §2 Findings (severity order)

### R1 — LOW/MEDIUM (latent determinism hole + false in-code invariant): the `Time:…Latency:` alternative of `_PACAT_RACY_TAIL` can never match

`corpus/fixtures/measure_audio.py:2014-2017`

```python
_PACAT_RACY_TAIL = re.compile(
    r"^(Time:.*Latency:|Playback stream drained\.|"
    r"Draining connection to server\.|Connected to device.*|"
    r"Stream started\..*)$")
```

The `$` binds the whole alternation, so the first branch matches only a line
*ending* at `Latency:`. pacat's real progress line is
`Time: 0.000 sec; Latency: 34750 usec.` → **no match** (measured directly:
`re.match` MISS on the exact string; MATCH only on a truncated `…Latency:`).

Consequences, all evidenced:

- The comment at `:2086-2090` ("Filter them … so the tail is deterministic — a
  successful leg ends on the negotiated `Using sample spec ...` line") states an
  outcome the code does not produce: in the committed receipt the paplay tail is
  **the unfiltered progress line** (8 leaves, e.g.
  `consumer2_dec_hcom_r75_probe.consumers.paplay.transport_axis.file.stderr_tail
  = "Time: 0.000 sec; Latency: 34750 usec."`).
- The author report bound (`reports/round-75/r75-author.md:159-161`: "racy-line
  filters (`Time:`/drain/index lines for pacat …)") is inaccurate for the
  `Time:` line — only the drain/index lines are filtered.
- **Scope, stated precisely so the fix is neither over- nor under-read:** the
  flip the scribe measured pre-landing (drain line vs Time line, F21) *is*
  resolved — `Draining connection to server.` is filtered, and I measured the
  raw last line as the drain line 12/12. The residual is the *value* of the
  progress line: 65/65 measured tails carried `Latency: 34750 usec.` (20 + 45
  direct legs, §1 E8), so this is latent on this host/member set, **not** an
  active receipt drift. The 8 byte-identical receipts in this window (5
  canonical + 3 mine) are therefore explained by the sink's constant latency,
  not by the filter.
- One-token fix (`Latency:.*`) is the author's call; I do not edit the fixture.

### R2 — LOW (inconsistent filter application): the shared `_nowriter_cell` tail bypasses the ffplay racy-line filter

`_nowriter_cell` (`:2381`) calls `_consumer2_tail(err, str(fifo))` with no
consumer-specific filtering, while the other two ffplay ops cells drop the
status line and `ALSA lib` diagnostics (`:2783-2786`, `:2853-2855`). Result in
the committed receipt:
`consumer2_ffplay_ops_r75_probe.fifo_no_writer.stderr_tail =
"    nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B"` — i.e. the exact
shape `_FFPLAY_STATUS_TAIL` (`:2173`) was written to suppress. Measured 5/5
stable (stream never opens: all counters 0, rc 123 each, §1 E8), so latent; the
aplay/paplay cells of the same helper are unaffected (aplay's tail is the TERM
notice, paplay's is empty because the ordering check relies on absence).

### R3 — LOW (convention deviation, no consumer impact): `error: "invalid_data"` on rc=0

`ffplay_leg` (`:2256-2259`) sets `error` to `"invalid_data"` / `"could_not_seek"`
for legs that exited **0**. The r73/r74 consumer convention (same file, `mpv_leg`
`:1150-1151` and the r74 `mpv_extent_leg` `:1615-1616`) is
`error = blocked or (None if code == 0 else reason or f"exit {code}")` —
positive evidence lives in a dedicated field
(`mpv_verdict`), `error` only on non-zero/blocked. r75 already has the dedicated
field (`ffplay_invalid`, `could_not_seek`), so the duplicate string adds a
false-positive surface for any reader that treats `error != None` as failure.
Mitigation in the diff itself: `failures` is the receipt's real failure channel,
the deviation is documented in the docstring, and no in-repo consumer parses
`error` (`grep -rl transport_verdict_groups|stderr_tail` → only
`measure_audio.py`). Cosmetic/consistency finding.

### R4 — LOW (wording drift, recurrence of scribe F1): "committed receipt"

`reports/round-75/r75-author.md:55` — "Measured (committed receipt
`runs/20261014T165017429491Z-consumers2-r75` …)". The receipts are **untracked
on disk**: `git ls-files corpus/live/runs | grep -c consumers2` → **0** (5
receipt dirs exist). Same drift the scribe recorded as F1 for r74; the ledger
entry should say "on-disk receipt" unless the integrator commits them.

### R5 — LOW (bounded claim vs guarantee): `_consumer2_tail`'s "never leaks" docstring

The scrub is correct on every observed shape (14/14, §1 E7) and the pre-landing
F17 leak is genuinely fixed (0 path-bearing leaves in all 5 canonical receipts:
`/home`, `/tmp`, mkdtemp prefixes, `mkdtemp` → 0 occurrences). But the docstring
(`:2001-2007`) claims a guarantee the construction does not give: the `[-160:]`
window is applied **inside** `_consumer_tail` (`:1021`) *before* the r75 subs, so
a >160-char line whose `probe_arg` does not appear in the line leaks a fragment —
demonstrated synthetically (`Playing WAVE '<200-char path>/pair_dec_hcom.wav' :
…` with a non-matching probe → tail keeps `xxxx…/pair_dec_hcom.wav' : …`). In the
landed legs the probe_arg is always the relative label (file arm) or the basename
(fifo arm), both suffixes of the echoed path, so the marker always survives
inside the window and `\S+<input>` collapses it — the hole is unreachable today.
Two inherited corollaries worth recording, both pre-existing `_consumer_tail`
behaviour, not r75 regressions: (a) the retained tail *content* depends on the
absolute checkout-path length (real member lines are 147–152 chars against a 160
window); (b) the anonymous arms pass `probe_arg="-"`, so `.replace("-","<input>")`
is global — no observed corruption (the only `-`-initial shape is ffplay's own
`fd:` label), but any future hyphen-bearing stdin-arm tail would be rewritten.

### R6 — LOW (claim scope): "byte-identical ×3" is same-host-state, and the state is demonstrably volatile

All 8 r75 receipts in this window share sha `0829a598…` (5 canonical: 16:48:19Z,
16:49:13Z, 16:50:17Z, **16:57:17Z, 16:58:21Z** — the last two written by a
sibling seat during my window, not by me; 3 mine). But the family embeds
daemon-state leaves, and F11 is live: `daemon_live.default_sink` reads
`…SPDIF__sink` in every r75 receipt while the committed r73 receipt (15:43Z)
carries `…SPDIF__sink.2` — I measured that flip directly in E4. `wall_s`
(`daemon_gate_dead`, 0.001) is a wall-clock leaf the author already declares. So
the byte-identity claim is a *measured* property of one host-state window, not a
guarantee; a ledger entry citing it should name the receipts and the state.

## §3 Residual risk and verification gaps

- **Live-daemon dependency.** Every paplay leg, the aplay `default`/`pipewire`
  legs and the ffplay `pulse`/`alsa` legs need the live PipeWire daemon; my
  replay ran against it (daemon untouched, no `pactl` mutation; only
  process-local env severing in E10). On a host without a daemon the paplay
  matrix degrades to reject/reject-connect and the aplay `default` leg to the
  measured `Host is down` class — the receipt records that, it does not
  fabricate it (consistent with the author's declared bound).
- **Not re-run by this seat:** the `lavfsweep-r74` family and the r69/r70/r71/r72
  families. Insertion-only was established structurally (E2/E3) and at the data
  level for the nearest prior family (E4/E5) plus the shared base rows (E5);
  the remaining families' receipts were left untouched (`git ls-files
  corpus/live/runs | grep -c consumers2` = 0, no tracked receipt drift).
- **`avio_bytes_read`/`avio_seeks`** on the `-ss` cell (641580/2 vs 384044/0) are
  asserted deterministic by the author ×3; my 3 replays reproduce the identical
  receipt, but I did not vary the pacer length to test the claim's boundary.
- **ffplay driver legs `pulse`/`alsa`** are host-dependent by the author's own
  bound; the receipt's identical tails for `alsa` across my runs are not evidence
  of a general determinism property (F23-class timing lines are filtered there,
  which is why they matched).
- **LSP device unavailable** (§1 disclosure) — caller/definition/diagnostics
  evidence is textual + executional, not a semantic index.
- **Receipt tracking.** 5 canonical r75 receipts exist and none is tracked; if
  the ledger entry cites them, the sha group must be named (R4/R6).

## §4 Call sites of every new symbol (textual caller map, committed blob)

| symbol | def | callers |
|---|---|---|
| `CONSUMER_R75_*`, `FFPLAY_R75_ENV` | 1990-1995 | 2053/2057/2092 (paplay), 2128/2132 (aplay), 2223/2228/2230 (ffplay), 2317-2318, 2352/2355/2363/2376/2379 (nowriter), 2433/2481/2501/2514/2542/2570 (paplay ops), 2647/2689/2725 (aplay ops), 2771/2812/2815/2818/2847 (ffplay ops) |
| `_consumer2_tail` | 1998 | 2093, 2163, 2262, 2381, 2438, 2653, 2783, 2853 |
| `_PACAT_RACY_TAIL` | 2014 | 2092 only |
| `_paplay_fields` | 2020 | 2082, 2482, 2502, 2515, 2571 |
| `paplay_leg` | 2036 | 2282 (matrix loop), and no other |
| `_aplay_fields` | 2099 | 2158, 2649, 2691, 2727 |
| `aplay_leg` | 2111 | 2282 |
| `_FFPLAY_STATUS_TAIL` | 2173 | 2261, 2786, 2855 (absent from `_nowriter_cell`, R2) |
| `_ffplay_fields` | 2176 | 2255 |
| `ffplay_leg` | 2204 | 2282, 2811, 2813 |
| `consumer2_transport_entry` | 2268 | 3315 (dispatch) |
| `_nowriter_cell` | 2335 | 2454, 2462, 2665, 2797 |
| `consumers2_paplay_ops_entry` | 2390 | 3307 |
| `consumers2_aplay_ops_entry` | 2584 | 3309 |
| `consumers2_ffplay_ops_entry` | 2744 | 3311 |
| `--probe-consumers2-r75` | 3023 | sum 3025, dispatch 3295, `mode` 3782, `suffix` 3802 (build_artifacts arg list: **no** r75 flag — see E13, harmless) |

## §5 Exact commands / exits

```sh
cd ~/Projects/shokunin/audio-shokunin
git show db46fba -- corpus/fixtures/measure_audio.py > corpus/live/r75-reviewer/landed.diff   # 997 lines
git hash-object corpus/fixtures/measure_audio.py        # 30eac683a94c3434274b56c4773b84ce577a3ac4 == HEAD:…
python3 - <<'PY'   # clause preservation (mode/suffix/sum, HEAD~1 vs HEAD; and r73/r74 precedent)
PY                 # -> 117 pairs verbatim in order; insert@head only; sum tail-append, 119 distinct
bash corpus/live/r75-reviewer/replay3.sh                 # rc=0 ×3, sha 0829a5986bb6ca70…, cmp-equal to canonical
bash corpus/live/r75-reviewer/replay_prior_r73.sh        # rc=1 (mode's documented forks); 9/9 member entries byte-equal
python3 corpus/fixtures/measure_audio.py --probe-consumers2-r75 --probe-lavfsweep-r74   # rc=2 "choose one probe mode"
python3 - <<'PY'   # 14 raw path-bearing shapes through _consumer2_tail -> 0 leaks; 20+45 paplay tails; 5 ffplay nowriter runs
PY
ldd /usr/bin/paplay | grep sndfile ; strings /usr/bin/paplay | grep sf_open_fd
PIPEWIRE_RUNTIME_DIR=$E XDG_RUNTIME_DIR=$E timeout -s KILL 15 aplay -D pipewire <member>   # rc=1 "Host is down"
PIPEWIRE_RUNTIME_DIR=$E XDG_RUNTIME_DIR=$E timeout -s KILL 15 aplay -D null <member>       # rc=0
git ls-files corpus/live/runs | grep -c consumers2       # 0 (receipts untracked)
for d in corpus/live/runs/*consumers2*; do sha256sum "$d/measurements.json"; done   # 5 dirs, 1 sha
```

All inspection/audit commands exited 0 except the deliberate ones named above
(`rc=2` mutex error, `rc=1` prior-mode own failures, the reject arms' rc=1).
No git mutation, no product-code edit, no probe mode run in the canonical ROOT
(every replay ran under the sandbox `corpus/live/r75-reviewer/replay/`, which
carries a byte-copy of the committed fixture plus copies of the three member
dirs and `artifacts/`), no canonical receipt written by this seat.

## §6 Touched surfaces

- Wrote only `reports/round-75/r75-reviewer.md` and
  `corpus/live/r75-reviewer/**` (replay3.sh, replay_prior_r73.sh, landed.diff,
  replay/ sandbox ROOT incl. its `live/runs` receipts, replay-*.stdout/stderr,
  prior-r73.*).
- No tracked file modified; no git mutation; no dispatch; no sibling seat's
  artifact edited. The 4th/5th canonical receipts observed during my window are
  a sibling seat's (verifier scratch exists; my receipts are in the sandbox).

**Seat stop.** Report complete; findings R1–R6 are advisory, none blocking.
