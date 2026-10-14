# R75 critic (audio) — adversarial falsification of `db46fba`

Seat **critic** (leaf; no subagents, no git mutation). Wave
`shokunin-train-20261101-w14`, lane audio, repo
`/home/vgpnk/Projects/shokunin/audio-shokunin`, HEAD **`db46fba`** (fixture
sha256 `13c3c9087ed83b62fbeb7cfa508f87d5c9f37a9b4ee8a72600efae6b58e844ce`,
worktree clean). Host `plazir27`, window 2026-10-14 16:53Z–17:0xZ (UTC).
Write scope: this report + `corpus/live/r75-critic/**` only. No tracked file
touched, no receipt written outside this seat's scratch, daemon never
signalled (child-env overrides + read-only `pactl`/`aplay -l` only).

Artifacts: `corpus/live/r75-critic/critic_probes_r75.py`
`b692f251c6433c26…`, five probe receipts (`…-p1…p5.json`, §6),
`replay/measure_audio_r75_replay.py` `262aca613348148f…` + replay receipt
`0829a5986bb6ca70…` (§1), `replay/member-verify.txt` `9ee1619f…`.
Dead predecessor (`critic_probes.py` + `20261014T160901Z-critic-probes/`
`ec1c3d4aaa5da069…`) was **verified, not reused as code**: its receipt is
partial (paplay sections only; it died before aplay/ffplay/kill cells) and its
writerless cell carries the same one-TERM ladder limitation as C1 below. I
cross-checked its 36 paplay matrix cells against the landed receipt — **36/36
agree** (rc + failure class), then wrote fresh probes.

---

## 1. Replay + mutants — what I ran

**Replay (independent generation, not the author's).** A copy of the landed
fixture with
exactly two patched lines — `ROOT` pinned to the repo `corpus/` and the
receipt output redirected under `corpus/live/r75-critic/replay/runs/`
(`diff` vs `git show db46fba:…` = those 2 lines only) — plus a no-op
`build_artifacts.py` stub, because the r75 mode calls the real builder with
**no probe flags** (default member build, which rewrites tracked members; the
author's own runs executed it and left the worktree byte-identical, so the
build is idempotent here — `replay/member-verify.txt`: 10/10 members
`work == index`, dirs clean).

```
timeout -s KILL 600 python3 -B corpus/live/r75-critic/replay/measure_audio_r75_replay.py --probe-consumers2-r75
→ exit 0, {"receipt": ".../runs/20261014T165800861380Z-consumers2-r75/measurements.json", "failures": {}}
```

The replay receipt is **byte-identical to the committed receipt** — sha256
`0829a5986bb6ca70c5c9b06b50bf661e9c8dbbe7cddefac5b16e860e2c2a76d4`, 2056
leaves, 0 differing leaves (full-tree diff). The landed "sha-identical ×3"
claim is therefore now **×6 across two seats and three processes**: the three
authored receipts + two further receipts a **foreign** fixture run left in
`corpus/live/runs/` during this window (`…T165717676332Z`, `…T165821738609Z`,
both `0829a598…`, not this seat's process) + my replay. (Provenance note: the
scribe-era pre-fix receipts `…T164125737824Z`/`…T164319…`/`…T164418…`/
`…T164603…` are **no longer on disk** — the on-disk family is the five
`0829a598…` dirs above; the path-bearing first receipt survives only as a
citation in `r75-scribe.md`. See C4a for why the identity is nonetheless
contingent.)

**Mutants.** P1: TERM ladder ×3 on the writerless cell (4 consumers). P2: the
*landed* `consumer2_transport_entry` re-run with `PULSE_SERVER` dead (child
env only). P3: paplay/aplay name axis incl. the `.au` name and WAV-content
crossed cells. P4: scrubber/regex audit + receipt scan + 12 sequential and
24 concurrent paplay runs. P5: receipt/structure audit. Structure check
(diff vs `db46fba^`): 6 hunks, 3 removed lines = the sum/mode/suffix chains;
mode and suffix chains 117→118 with `new == [probe_consumers2_r75] + old`;
flag-sum list gained exactly `probe_consumers2_r75` — **insertion-only
verified independently of the scribe**.

---

## 2. Attacks that FAILED (claims that survived)

| claim | attack | outcome |
|---|---|---|
| 27/27 verdict groups transport-invariant | full replay + predecessor cross-check | **holds**: 9 member entries × 3 consumers = 27 single-group verdicts, `failures []` in all 12 entries; replay byte-identical; predecessor 36/36 paplay cells agree |
| paplay name-blind / `.snd` fork does not transfer | the strongest falsifier: `.au`, the *other* name libsndfile's path fallback accepts (scout §3), plus case `.SND`, unknown `.au2`, file+fifo+rfd | **holds**: rc=1 `Failed to open audio file.` on every name (P3). The landed control's `{snd,wav,bin}` omission of `.au` is not a hole |
| "content wins over name" | WAV bytes under `.snd`/`.au`/`.bin`, file+fifo, with `-v` | **holds**: rc=0, `pa_sample_spec: s16le 1ch 8000Hz` (P3) — but it has no *landed* leg (C5) |
| aplay invariant-accept | no-magic bytes under `.snd`/`.au` **file** arms (landed control is fifo-only) | **holds**: rc=0 `raw data`, `Unsigned 8 bit, Rate 8000 Hz, Mono`; WAV content under any name → `WAVE` |
| ffplay does not refresh-seek; `avio_seeks` counter is real | landed `-ss` cell | **holds and is now proven positive-path**: file arm `avio_seeks: 2` / 641580 B; stdin `0` / 384044 B. (Boundary §10 listed the positive path as unproven; the landed arm closes it) |
| ffplay rc0-on-invalid; empty-writer rc0 | receipt | holds (`[0, None, 0, True]` ×5 extsuffix; empty-writer rc0 `Invalid data`) |
| kill classes paplay −15, ffplay 123 | P1 ladder | holds (paplay dies 0.001 s after TERM₁ → −15; ffplay TERM₁ → 123 in 0.003 s) |
| paplay input-open precedes connect | dead-server matrix mutant (P2) + ordering cell | holds: with a dead server the *file* arms fail connect instantly (rc1, `Connection failure: Connection refused`), while the writerless-fifo cell blocks in `wait_for_partner` with no connect line |
| insertion-only | independent chain/sum diff | holds (§1) |

---

## 3. Counterexamples (the attack that landed)

### C1 — ops kill semantics: `aplay … sigterm_immune: true` is a **one-TERM artifact**

Receipt leaf `consumer2_aplay_ops_r75_probe.fifo_no_writer` =
`{blocked: true, wchan: wait_for_partner, sigterm_immune: true, exit_code: -9,
stderr_tail: "Aborted by signal Terminated..."}` — produced by
`_nowriter_cell` (`measure_audio.py:2335`, field at `:2377`), asserted at
`:2667`.

**Counterexample (P1, 3-TERM ladder, 1.0 s windows, same writerless cell):**

| consumer | TERM₁ | TERM₂ | TERM₃ | result |
|---|---|---|---|---|
| `aplay -D null` | **alive after 1.0 s** | **dies, rc −15, 0.001 s** | — | TERM₁-deferred, **not immune** |
| `pw-cat -p` (contrast) | alive | alive | alive | truly immune → killpg −9 |
| `paplay` | dies, rc −15, 0.001 s | — | — | matches landed field |
| `ffplay` | dies, rc 123, 0.003 s | — | — | matches landed field |

aplay's handler prints `Aborted by signal Terminated...` and restores
SIG_DFL, so a *second* TERM kills it. The landed ladder sends exactly one TERM
and labels the outcome "immune" — the exact artifact scout discarded
(`r75-scout.md` §6: "a one-TERM ladder produced the scratch's false
`sigterm_immune: true` row"). The author's report prose is accurate ("SIGTERM
caught … yet STILL blocked → SIGKILL → −9"); the **field name** and the
assertion encode a stronger, false property. Operational conclusion (KILL
backstop required) stays right.

**Impacted axes:** receipt-truthfulness / kill-class semantics (a consumer
property recorded as ladder-independent when it is ladder-length-dependent).
**Smallest safe correction:** rename the field to `alive_after_term1` (or add
`term_ladder_len: 1`) and adjust `:2667`'s assertion key — one rename, no
behaviour change; alternatively extend `_nowriter_cell` to a second TERM
(one extra `send_signal`+wait) and record `died_on_term_n: 2, exit_code: -15`,
which is the honest measurement and would drop the `-9` claim for aplay.

### C2 — transport-invariance can be **vacuously true**: the matrix entry is not gated on daemon liveness

**Counterexample (P2):** the landed `consumer2_transport_entry("dec_act", …)`
re-run with `PULSE_SERVER=unix:/nonexistent-r75-critic-gate` (child env only)
returns paplay arms `[1, null, "Connection failure: Connection refused"]` on
**all four transports** → `transport_verdict_groups` = 1,
`transport_fork: false`, `failures: []` — identical shape to a pass. Live
control reproduces the committed key `[0, "s16le 1ch 8000Hz", null]`.

The entry's fork check (`:2287-2308`, `consumer2_transport_entry` at `:2268`)
compares *within* a member across
transports; a daemon outage collapses every member to one connect-class key,
so a dead-daemon run still prints "27/27 invariant, failures {}". The
*committed* receipt is not degenerate (my replay reproduces the decode keys),
so this is a **checker hole, not a false current claim** — but the invariance
claim carries no internal evidence that the paplay gate was live (the ops
entry's `daemon_live`/`daemon_gate_dead` cells are a different entry and do
not feed the matrix entry).

**Impacted axes:** claim strength / self-guarding of the invariance check;
future-run honesty. **Smallest safe correction:** in
`consumer2_transport_entry`, fail the entry when any paplay arm's `pa_error`
is connect-class (`"Connection failure"`/`"Connection refused"`/
`pa_context_connect`) or require the positive decode witness (non-null
`pa_sample_spec`) on the accept members — one `if`, same receipt shape.

### C3 — ffplay ops extent claim is **falsified**: the `-ss` stdin arm does not play

Landed `ffplay_startpos` (`:2819`) records `predicted: "… stdin arm logs
'could not seek' and rescues by decode-discard — path fork, not extent
fork"`, and `r75-author.md:119-121` says the non-seekable arm "rescues by
decode-discard and still plays the tail at rc=0".

**Counterexample (P4/§1 replay of the exact landed leg, `SDL_AUDIODRIVER=dummy`,
`-ss 2`, 384044 B / 4.0 s pacer):**

| arm | wall | status samples (`M-A:`) | seeks | `could not seek` | rc |
|---|---|---|---|---|---|
| file | **2.113 s** (raw 2.111) | **65** | 2 | no | 0 |
| stdin_pipe | **0.158 s** (raw 0.157) | **0** | 0 | yes | 0 |

The stdin arm reads the whole input (384044 B) during open/probe, fails the
seek, logs `fd:: could not seek to position 2.000`, and **exits rc 0 with no
playback** — an extent fork (2 s played vs 0 s), not merely a path fork. The
landed assertion (`:2801` ff) checks only `could_not_seek`/rc0, and
`ffplay_leg` records **no wall and no status-sample count**, so the receipt
cannot distinguish playback from abort on this cell. (Scout measured the same
0.159 s / 0 samples; the author's cell inherited scout's fields but not its
conclusion.)

**Impacted axes:** claim correctness (a false `predicted` string inside the
receipt) + witness completeness for the ffplay ops row. **Smallest safe
correction:** restate `predicted` as the measured shape ("non-seekable arm
aborts without playback: 0 status samples, ~0.16 s wall; rc=0 is not a
playback witness") and add a `wall_s`/`status_samples` witness to the two
`ffplay_startpos` legs (the leg can time `subprocess.run` without any new
dependency).

### C4 — tail-scrub holes (three, with a load counterexample)

**C4a `_PACAT_RACY_TAIL` (`:2014-2017`) is `$`-anchored wrong and never filters the
real progress line.** Direct regex test: `Time: 0.040 sec; Latency: 159959
usec.` → **no match** (the truncated `Time: … Latency:` matches). Consequence
in the committed receipt: **8 of 121 tails are the unfiltered racy line**
`Time: 0.000 sec; Latency: 34750 usec.` (all paplay dec_act/dec_hcom arms × 4
transports) — not the "negotiated `Using sample spec …` line" the leg comment
(`:2086-2090`) promises. **Load counterexample:** 12 sequential runs → 12 ×
`Latency: 34750 usec.`; **24 concurrent runs (8-way × 3 rounds) → 3 distinct
values** (`34734`, `34738`, `34742` vs modal `34750`). So the ×6 byte-identity
is a *contingent* identity: the same arm under load yields a different receipt
leaf, and the drain-vs-Time flip class scribe measured (F21) is the same race.
The *parsed fields* stay stable (F24's field-stable/byte-unstable split is
confirmed and now explained by an unfiltered line, not just by a race).

**C4b `_nowriter_cell` (`:2381`) does not apply the ffplay status filter** —
the ffplay writerless tail in the committed receipt is the racy progress
fragment `'    nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B'`
(the regex `_FFPLAY_STATUS_TAIL` *does* match this line — verified — it is
simply not applied on this path). 1 receipt leaf.

**C4c the wholesale quote rule (`:2009`, `re.sub(r"'[^']*'", "'<input>'")`;
`_consumer2_tail` at `:1998-2011`) destroys non-path quoted witnesses.**
Verified on the landed helper:
`_consumer2_tail("Using sample spec 's16le 1ch 8000Hz'", "-")` →
`"Using sample spec <input>'"`. Latent only because C4a keeps the tail on the
Time line; **fixing C4a alone instantiates it** (the tail would then be the
spec line with its value replaced by `<input>`). Paired fix required.

**C4d (bounded, latent):** an *unquoted* absolute path containing a space
leaks its prefix (`"/tmp/a b/x.wav: Invalid data"` → `"/tmp/a <input>"`); not
reachable with the current corpus/mkdtemp paths (no spaces) — recorded as a
bound, not a defect. F17b (stray `'` after `<input>`) persists in receipt
tails (`Playing WAVE <input>' : …`), cosmetic and stable.

**Impacted axes:** evidence byte-stability across load/sessions; witness
fidelity. **Smallest safe correction (4 lines):** (1) `_PACAT_RACY_TAIL`:
`Latency:` → `Latency:.*`; (2) apply `_FFPLAY_STATUS_TAIL` (and the
`ALSA lib` filter) in `_nowriter_cell` before `_consumer2_tail`; (3) narrow
the quote rule to path-shaped tokens (e.g. only quoted strings containing
`/`), so the spec line survives; (4) optionally make the residual collapse
consume the stray quote. Then the paplay tail is `Using sample spec
's16le 1ch 8000Hz'` — deterministic and informative.

### C5 — provenance gap (minor): "content wins" has no landed leg

The landed `paplay_name_axis` is 7 all-reject legs; the content-wins positive
(WAV bytes under `.snd`/`.au`/`.bin` → rc0 + spec) exists only in boundary
scratch and my P3. The landed claim string is supported by the all-reject set
plus the matrix's dec_act accept and the `--raw` bypass; the crossed
positive is an inference the receipt does not carry. **Smallest correction:**
add one leg (WAV bytes copied to `.snd`, file arm) to the ops name-axis set.

---

## 4. Classification for the canonical judge

- **C1, C3** are fixable defects in what the receipt *says* (false
  provenance / false predicted string), not in the round's central results;
  both are one-line-ish fixes and should not be traded away as "accepted
  risk" — a receipt field that overstates a measured property is exactly what
  a later seat will quote.
- **C2** is a checker hole (latent; the committed receipt verified
  non-degenerate by independent replay). Cheap to close; leaving it means the
  next daemon outage mints a green-looking invariance receipt.
- **C4a/C4b** are evidence-quality defects with a demonstrated load
  counterexample; **C4c** is the paired fix that C4a forces. The family's
  byte-identity claim is true as written but *load-contingent* until fixed.
- **C5** is a provenance nicety, not a defect in the fixture.
- No counterexample in this pass falsifies the r75 arm's headline results
  (consumer breadth without importing a fork; the three gate/kill classes;
  the transport matrix). My independent replay reproduces the committed
  receipt byte-for-byte, which is the strongest form of agreement available
  from this seat.

## 5. Impacted axes (named)

`receipt-truthfulness` (C1, C3), `claim-self-guarding` (C2),
`evidence-byte-stability-under-load` (C4a/b/c), `claim-provenance` (C5).
Unchanged by this review: the consumer axes the arm measures (name axis,
transport axis, detect/seek fields, kill classes).

## 6. Evidence index

| artifact | sha256 (16) |
|---|---|
| `critic_probes_r75.py` | `b692f251c6433c26` |
| `20261014T165554Z-…-p1.json` (ladder) | `c82a59be1451a0aa` |
| `20261014T165611Z-…-p2.json` (vacuity) | `f84518e67f5f888a` |
| `20261014T165619Z-…-p3.json` / `…T165634Z-…-p3.json` | `945fb88f3c4a09af` / `85a8ffebe22e5f73` |
| `20261014T165534Z-…-p4.json` (tails) | `0d196cb79b1c6a54` |
| `20261014T165534Z-…-p5.json` (receipt audit) | `5bc8b4d326206b30` |
| `replay/measure_audio_r75_replay.py` | `262aca613348148f` |
| `replay/runs/20261014T165800861380Z-consumers2-r75/measurements.json` | `0829a5986bb6ca70` (= committed) |
| `replay/member-verify.txt` | `9ee1619f3e58a1d4` |
| predecessor `20261014T160901Z-critic-probes/receipt.json` | `ec1c3d4aaa5da069` |
| committed r75 receipt (audited) | `0829a5986bb6ca70` |
| foreign in-window receipts `…T165717676332Z` / `…T165821738609Z` (read-only) | `0829a5986bb6ca70` both |

Commands (all exits 0 unless stated): `timeout -s KILL … critic_probes_r75.py
{p1..p5}`; replay run above; `git diff -U0 db46fba^ db46fba -- …/measure_audio.py`
(6 hunks, 3 removed lines); `git hash-object` vs `git rev-parse :<path>` for
10 members; `git ls-files corpus/live/runs | grep -c consumers2` → 0
(receipts untracked — the F1 "on-disk receipt" wording applies).

## 7. Bounds / not claimed

Bounded to this host and these builds (pacat 17.0-98-gb096 / libpulse 17.0.0
on PipeWire 1.6.8, alsa-utils 1.2.16, ffplay n9.0.1 / lavf 63.1.101,
sdl2-compat 2.32.72-1, kernel 7.2.3-arch1-3). Not tested: daemon restart (env
severing only), `PULSE_SERVER` non-unix forms, load beyond 8-way, other
latency configurations. The `Latency: 34750` value is this session's
server-config value; the concurrency counterexample shows only that the leaf
varies, not a full distribution. C2's mutant is an environment mutation of
the landed entry, not a receipt; the committed receipt was independently
replayed and is not degenerate. Hygiene note: a **foreign live run** of the
tracked fixture was observed in the window (`timeout -s KILL 2400 python3
corpus/fixtures/measure_audio.py --probe-consumers2-r75`, pid 1645462,
17:06Z±) — not this seat's process, not touched; this seat's own runs wrote
only under `corpus/live/r75-critic/` and left no orphan (post-run `ps` shows
none from this seat). No product file edited, no receipt written outside
`corpus/live/r75-critic/`, no git mutation, no subagents.

**Seat stop.**
