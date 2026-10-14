# R76 reviewer — capture-side consumers (audio lane, POST-COMMIT verify)

Round 76 · wave `shokunin-train-20261101-w15` · repo `~/Projects/shokunin/audio-shokunin`
· HEAD `d566a31` (parent `2250be9`) · diff `+1147/−3` in
`corpus/fixtures/measure_audio.py` + `reports/round-76/r76-author.md`.

Seat: REVIEWER (leaf). No subagents, no git mutation, no tracked-file edit.
Verdict emitted here is a **recommendation**, not an admission.

Method: read the committed diff line-by-line; re-derived every r76 row from
the raw bytes myself (own probe harnesses, no fixture import from
`corpus/fixtures` — a scratch copy of the committed fixture was imported
instead so the tracked `.pyc` was never rewritten); replayed the full
battery on a sha-identical copy of the committed tree inside this seat's
write scope; diffed my receipt against the author's and against every other
r76 receipt on disk.

Evidence index (all paths relative to repo root):

| artifact | path |
| --- | --- |
| committed diff | `corpus/live/r76-reviewer/scratch/diff.patch` |
| my replay receipt (`failures: {}`) | `corpus/live/r76-reviewer/scratch/tree/corpus/live/runs/20261014T183354979511Z-capture-r76/measurements.json` (sha `a05621117225aaca…`) |
| my raw sever probe | `corpus/live/r76-reviewer/scratch/sev_probe.json` |
| class-derivation closure (fixture classifiers on my wound bytes) | `corpus/live/r76-reviewer/scratch/class_closure.json` + `sev_wounds/` |
| ffmpeg class probe (`-v verbose`) | `corpus/live/r76-reviewer/scratch/ffmpeg_class_probe.txt` |
| author canonical receipt | `corpus/live/runs/20261014T182450100472Z-capture-r76/measurements.json` (sha `ba36cd70f765826a…`) |

---

## 1. Verdict on the assigned checks

| check | result | evidence |
| --- | --- | --- |
| insertion-only, 3 touched lines guarded | **holds, one wording correction** | §2 |
| six-entry verdict logic, class vs raw evidence, no rc-trust | **holds** | §3 |
| sever partition TERM vs KILL consumer-specific | **holds, re-derived from raw bytes** | §3.2 |
| name axis | **holds** (14/14 rows reproduced) | §3.3 |
| device-inventory snapshotting | **holds, volatile leaf found** | §4.3 |
| byte-cap discipline on the unpaced oracle | **holds** | §3.5 |
| monitor roundtrip witness | **holds** | §3.6 |
| replay battery + re-derive rows | **done — `failures: {}`, differs from author in 2 explained leaves** | §4.1 |
| author's claimed shas | **confirmed, and stronger than claimed (4 receipts share `ba36cd70…`)** | §4.2 |

---

## 2. Insertion-only claim

`git show d566a31 --numstat` = `1147 3 corpus/fixtures/measure_audio.py` +
`241 0 reports/round-76/r76-author.md`. A `SequenceMatcher` over
old/new line lists yields exactly 4 pure inserts and 3 replaces; the 3
replaces are the 3 deleted lines. Rebuilt each new line from
`indent + prefix + old-line-verbatim`:

- `mode` (`measure_audio.py:4963`) and `suffix` (`:4983`): the prior ternary
  chain is preserved **verbatim as a suffix**; the prepended clause is
  `mode = "probe-capture-r76" if args.probe_capture_r76 else ` /
  `suffix = "-capture-r76" if args.probe_capture_r76 else `.
- mutex sum (`:4186`): **not a prepend** — the new flag is appended inside the
  list, i.e. `…args.probe_consumers2_r75, args.probe_capture_r76]) > 1:`. The
  prior *content* is preserved verbatim, but the prior *expression* is not a
  contiguous substring there. With `probe_capture_r76` false the sum is
  identical, so prior-flag behavior is unchanged, and the new flag is covered
  by the same `choose one probe mode` guard (`:4184` argparse, `:4477` block).

Correction (report wording, not code): `r76-author.md:16-17` says all three
touched lines are "guarded prepends" — true for `mode`/`suffix`, an in-list
append for the mutex sum. No behavioral consequence.

---

## 3. Verdict logic vs raw evidence

### 3.1 No rc-trust
Every r76 verdict carries a non-rc carrier: exact bytes (`192044` at
`:3591`, `:3611`, `:3618`; `960044` at `:4013`), `cap_honored` (exact 262144
at `:3597-3601`), header classes (`data_finalized`, `data_64k_aligned`
`:3605-3606`), container kinds (`out_kind`, `:3843-3850`), placeholder
classes (`:3748`, `:3736-3737`, `:3757`) and parser classes (`:3752-3756`).
The gate's `(rc, class)` table (`:3433-3453`) is an expectation pin; the class
is the semantic carrier and each class traces to a named raw line
(`_CAPTURE_ERR_CLASSES`, `:2979-2996`, first-match most-specific-first).

I re-derived the ffmpeg classes from full `-v verbose` stderr
(`ffmpeg_class_probe.txt`): `-f pulse -i default` rc=251 with
`Error opening input: Input/output error` → `ffmpeg_io`; `-f alsa -i default`
rc=251 with `cannot set parameters (No such file or directory)` **and** a
generic EIO line → `ffmpeg_alsa` (correctly matched before the generic
pattern); dead `PULSE_SERVER` rc=253 with `Error opening input: No such
process` → `ffmpeg_esrch`. All three author table rows reproduce.

### 3.2 Sever partition — independently re-derived from raw bytes
`sev_probe.json` (my harness) + `class_closure.json` (the fixture's own
classifiers fed my wound files):

| cell | rc | raw bytes | riff field | data declared vs actual | stdlib `wave` | ffprobe |
| --- | --- | --- | --- | --- | --- | --- |
| pwrecord TERM | 1 | 278572 | finalized | 278528 == 278528 | opens, 1.00× honest | parses |
| parecord TERM | 0 | 131116 | finalized | 131072 == 131072 (2×65536) | opens, 1.00× | parses |
| ffmpeg TERM | 255 | 489678 | finalized | 489600 == 489600 | opens, 1.00× | parses |
| arecord TERM | 1 | 264184 | finalized | 264140 == 264140 | opens, 1.00× | parses |
| pwrecord KILL | −9 | 286764 | **placeholder_8** | 0 over 286720 real | **rejects** (`wave.Error`) | parses |
| parecord KILL | −9 | 131116 | **placeholder_8** | 0 over 131072 real | **rejects** | parses |
| ffmpeg KILL | −9 | 262144 | **placeholder_ff** | 0xFFFFFFFF over 262066 | opens, **16389×** inflated | parses |
| arecord KILL | −9 | 264044 | `other` (0x80000004) | **0x80000000** over 264000 | opens, **8134×** inflated | parses |

So: TERM finalizes in all four consumers; KILL wounds are genuinely
consumer-specific; arecord-KILL accept-and-lie is real at the byte level
(`wave.getnframes()` = 536 870 912 against 66 000 honest frames). The
report's "riff field measured `other`" note (`r76-author.md:131`,
`:3745-3747`) is exactly right and the claim is correctly pinned to the data
field instead. `ffprobe` tolerates all four wound shapes — also confirmed.

### 3.3 Name axis
All 14 rows reproduce in my replay (`capture_name_axis_r76_probe.legs`):
pw-record `.bin`→`riff_wav` / `--raw` on `.bin`→`raw_stream`; parecord
`.bin`→`riff_wav`, `.raw`→`raw_stream`, `--file-format=wav` on `.raw`→
`riff_wav`; arecord `-t wav` on `.bin`→`riff_wav`, `-t raw` on `.wav`→
`raw_stream`, no `-t` on `.bin`→`riff_wav` (flag-driven, name-blind); ffmpeg
`.bin` rc=234 `Error initializing the muxer … Invalid argument`, file
missing, `-f s16le` on `.bin`→`raw_stream`.

### 3.4 Device axis / r75 inversion
`default` and `pipewire` → rc=1 `alsa_hwparams` (`Unable to install hw
params`, my own run confirms the `set_params:1462` line); `sysdefault`,
`plughw:0,0`, `hw:0,0` → 192044 B paced; `-D null` → 192044 B in <0.5 s
unpaced; `hw:0,0 -c 1` → `alsa_channels` (my own run: `set_params:1404`).
The r75 side of the inversion is corroborated in
`corpus/live/runs/20261014T172034398145Z-consumers2-r75/measurements.json`
(`consumer2_aplay_ops_r75_probe.device_axis`: `default`/`pipewire` rc=0
playback, `hw_first` rc=1 `set_params:1404`).

### 3.5 Byte-cap discipline on the unpaced oracle
`-D null` occurs only with `-d 1` (`:3481`, `:3809`, `:3879`) plus the 15 s
outer `subprocess` timeout (`CAPTURE_R76_TIMEOUT_S = CONSUMER_R73_TIMEOUT_S`,
`:2952`, `:1003`); no unbounded null run exists in the added code. The parec
leg reads exactly `min(65536, cap-len(buf))` (`:3526-3528`) so it cannot
overread the 262144 cap, then SIGTERM + KILL-on-process-group
(`:3532-3538`) — receipt shows `bytes_read == cap_bytes == 262144`,
`cap_honored: true`, rc=0.

### 3.6 Roundtrip witness
My replay: `960044` B = `44 + 240000×4`, `data_finalized: true`,
`pw-cat -p` rc=0, sox `wav==wav` and aplay `WAVE==WAVE` same-class, both
content witnesses true. sox `samples_read` 192000 (mono member) vs 480000
(stereo 5 s capture) — the channel/path difference the report declares
(`r76-author.md:167-169`) is visible in the receipt and is not a verdict
difference.

---

## 4. Replay, shas, prior rows

### 4.1 My replay
Committed fixture copied byte-identically (`691d730d…` both) into a scratch
tree with symlinked read-only `artifacts/`+`live/round-*`, run as
`--probe-capture-r76` under `timeout -s KILL 480`. Result:
`{"failures": {}}` — all 6 capture entries and all 17 base rows pass.
Diff against the author's canonical receipt = **exactly 2 leaves**, both
explained and neither a claim defect:

1. `capture_gate_r76_probe.inventory.pw_capture_ports` 12 → 16: four
   transient client monitor ports (`pw-record:monitor_FL/FR`,
   `parecord:monitor_FL/FR`) present at my gate snapshot. The independent
   run `20261014T183404004733Z-capture-r76` (started 18:34:04, concurrent
   with mine) shows the same 12→16 drift.
2. `capture_roundtrip_r76_probe.detect_legs.aplay.captured.stderr_tail`
   74 → 69 chars: `_consumer_tail` truncates to `[-160:]` (`:1024`) **before**
   `_consumer2_tail` collapses the quoted path (`:2016-2017`), so at a deeper
   ROOT the line loses its head. I replicated both normalizers verbatim and
   reproduced both strings exactly (author ROOT len 51 → `"Playing WAVE
   <input>'…"`; scratch ROOT len 89 → `"ng WAVE <input>'…"`).

### 4.2 Claimed shas
- fixture `691d730d4b4b2aa1475aa03bd4d9d7b5c9bdd3baf6a62d24923097f6fb9e9734` ✓
- author harness `corpus/live/r76-author/scratch/sev_probe.py`
  `9c2c97eb79b1edf91a36f108e91c9834f9b035fbd0b8db649e8c321e1e3197b4` ✓
- canonical receipt `ba36cd70f765826a9937fc78c62143c984790f1bdc26a4ad8aaf813cfc00f92f` ✓
  — and **four** receipts carry that sha: the author's pair
  (`…T182450100472Z`, `…T182539237046Z`) plus `…T183215518470Z` and
  `…T183309733895Z` (further post-commit runs, not listed in the report).
- Author falsification narrative checks out: `…T181454Z` has exactly the 3
  reported failures (ffmpeg-KILL union, arecord-KILL riff field, roundtrip
  sox class); `…T182210Z` vs `…T182305Z` differ in **exactly one leaf** — the
  `/tmp/capture-r76-XXXXXXXX/` muxer-error leak — and the fix is visible as
  `<out>` in the canonical receipt.

### 4.3 Prior rows untouched — verified beyond the author's own runs
Deep-compared the 17 base rows plus every top-level section
(`distinctness`, `*_family_comparisons`, `sections`, `thresholds`) between the
**r75** canonical receipt (`…T172034398145Z-consumers2-r75`) and my **r76**
replay: **0 diffs** (only `mode` differs). The insertion-only claim therefore
holds independently of the author's receipts, and the r76 arm does not
perturb any pre-existing row.

### 4.4 Honest-contention guard fires as designed
`…T183404004733Z-capture-r76` (concurrent with my replay) recorded
`capture_bounded_r76_probe.legs.arecord_duration_hw` = rc 1, `error_class
alsa_busy`, `error "Device or resource busy"`, file absent — and still
`failures: []` via the busy carve-out (`:3615-3621`). Contention landed as
named data, not a fabricated capture and not a spurious failure.

---

## 5. Findings by severity

### MEDIUM-1 — sever assertions can pass vacuously (demonstrated on this host)
`capture_sever_r76_entry` accepts, for TERM cells, `rc == expected and
data_finalized is True` (`:3719-3724`; parecord's bounded cell adds
`data_64k_aligned`, `:3602-3608`) and, for the pw-record/parecord KILL cells,
`riff_size_field == "placeholder_8"` (`:3757`). A **header-only** wav
satisfies all of these: `data_declared == 0 == data_actual` ⇒
`data_finalized` True (`:3069`), `0 % 65536 == 0` ⇒ aligned True
(`:3076-3077`), and the open-time `riff_size_field == 8` is still
`placeholder_8`.
Not hypothetical: the author's own pre-fix receipt
`corpus/live/runs/20261014T181743427243Z-capture-r76/measurements.json`
carries `capture_sever_r76_probe.cells.parecord_term.file.data_actual_zero =
true`, `wave_frames_class = "honest_empty"` **and**
`cells.parecord_kill.file.data_actual_zero = true`, `data_declared_field =
"finalized"` — with `capture_sever_r76_probe.failures = []`. That is a
vacuous pass of both the "TERM finalizes the header" and the "KILL leaves the
open-time header" claims on an empty capture, i.e. exactly the wave's carried
vacuity guard (`SHARED.md:27-29`). (The pre-fix *bounded* parecord cell did
hold real bytes, `data_actual_zero: false`; the empty shape is the sever
cells.) The final code uses 2.5 s + `@DEFAULT_SOURCE@`, so the canonical run
carries real bytes (`data_actual_zero: false`, `data_actual = 131072` in my
replay) — but the assertion still has no non-emptiness floor.
`data_actual_zero` is already recorded; `and fin.get("data_actual_zero") is
False` closes it for the pw-record/parecord/arecord TERM cells and the
parecord KILL cell (arecord KILL and ffmpeg KILL already carry payload-shape
pins).

### MEDIUM-2 — roundtrip writes into another seat's live dir
`measure_audio.py:3935`: `scratch = ROOT / "live" / "r76-author"` (with
`mkdir(parents=True, exist_ok=True)`). Every replay — reviewer, verifier,
scout, a later round — creates and writes temp dirs inside the *author's*
seat directory, i.e. outside the replaying seat's declared write scope, and
the receipt's only path-shaped leaf is pinned to a seat name. I had to
relocate ROOT into this seat's scratch tree to replay without that
cross-seat write. Fix: a neutral round-scoped dir (e.g.
`ROOT/"live"/("r76-roundtrip")`) or a temp dir under ROOT that is not
seat-named.

### LOW-3 — receipt determinism is host-state and ROOT-depth bounded
(a) `inventory.pw_capture_ports` is polluted by *concurrent* capture
activity (12 → 16 in my replay and in `…T183404004733Z`); the author's
byte-identical pair is a quiescent-host property, and the report's
"byte-identical rerun" claim (`r76-author.md:191-192`) should carry that
bound explicitly. (b) the aplay captured `stderr_tail` leaf changes with the
checkout depth (§4.1.2). Neither leaf is keyed on by any verdict, so this is
evidence hygiene, not a claim error.

### LOW-4 — dead, misleading expectation
`:3710` `expected["arecord"]["kill_riff"] = "placeholder_80000000"` is never
read: the arecord branch keys on `data_declared_field` (`:3748`) because the
measured riff field is `other` (0x80000004 in my probe). A future reader
keying that dict would expect the wrong field.

### LOW-5 — degenerate `wave_frames_class` branch can confirm the headline claim for the wrong reason
`:3108-3119`: with no parsed `fmt` chunk, `frame_bytes == 0 ⇒ honest == 0`,
so any nonzero frame count classifies `"inflated"` — the very label the
arecord accept-and-lie assertion keys on (`:3753`). It does **not** fire in
the canonical cells (I verified `fmt` present, ch=2/bits=16, in every sever
cell and re-derived the 8134× ratio by hand), but the branch should refuse
(`"no_fmt"`/raise) rather than default into the asserted class.

### LOW-6 — docstring vs code in the roundtrip guard
`:3921` claims "A monitor-less host degrades to a named blocked", but the
guard is `if not sink or not member.exists()` (`:3927`); `inv["monitors"]` is
never consulted, so a host with a default sink and no monitor would attempt
the capture and land a failure instead of a named `blocked`.

### LOW-7 — contention policy is inconsistent across entries
The bounded entry tolerates `alsa_busy` (`:3615-3621`, demonstrated in
§4.4), but `capture_device_axis` asserts `error_class == "alsa_hwparams"`
for `default`/`pipewire` with no busy carve-out (`:3896-3899`) — under
contention that entry turns honest contention into a spurious `failures`
row.

### LOW-8 — gate leg can vanish silently
`pwrecord_monitor_alias` exists only `if mon` (`:3377-3380`) and the
expectation loop `continue`s on a missing leg (`:3447-3449`), so on a host
with no enumerated monitor the receipt shows no trace of the skipped gate —
inconsistent with the explicit `{"blocked": …}` rows the other entries emit.

### LOW-9 — paraphrased argv
`:3957-3961` records `capture_leg.argv` as a hand-written summary that omits
the real `--rate/--channels/--format` (the actual argv is only pinned
indirectly by `file.fmt`); every other leg in the family records the real
argv. `player_argv` is likewise a paraphrase.

### LOW-10 — snapshot traceability
Only the gate entry stores its inventory (`entry["inventory"]`, `:3352`); the
other five entries re-enumerate and discard, so a device/name-axis row cannot
be traced to the snapshot it used (legs do record their resolved device and
argv, so this is traceability, not evidence). Related:
`_capture_leg_targets` (`:3217-3222`) silently falls back
`default_source → sources[0]` and `default_sink.monitor → monitors[0]` with
no marker in the receipt.

### Observation (outside the diff)
At 18:32:34 the tracked `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
was 325363 B (the r76 source's cache, i.e. dirty vs HEAD's 157038 B) and was
restored to HEAD bytes at 18:32:59 — a concurrent lane importing the module,
not the author (mtime is post-commit; other lanes ran this same battery at
18:32:15, 18:33:09, 18:34:04). `git status --porcelain` is clean of tracked
modifications now, and the commit itself contains only the 2 intended files.
Report list of untracked receipt dirs (`r76-author.md:206-209`) undercounts:
there are 9 `*-capture-r76` dirs, one of them (`…T181356Z`) empty (no
`measurements.json`), plus 2 post-commit byte-identical runs and 1 contention
run not listed.

---

## 6. Residual risk and verification gaps

- **Quiescence**: my replay could not be taken on a quiet host (concurrent
  lanes ran the same battery during my session), so my sha differs from
  `ba36cd70…` by the inventory leaf alone. The author's byte-identity is
  confirmed (4 receipts) but only for a quiet host at the canonical ROOT.
- **Relocated ROOT**: my replay ran with a deeper ROOT to stay inside this
  seat's write scope — which is precisely what exposed LOW-3b. An in-place
  replay would be byte-identical on the aplay leaf but would write into
  `corpus/live/runs/` and `corpus/live/r76-author/` (outside scope).
- **Not re-measured**: audible/decode equivalence of the roundtrip beyond the
  two content witnesses; "same verdict class" stays bounded to sox's detected
  format, aplay's ALSA accept and those witnesses, exactly as the report
  states. parecord's 44100 Hz (vs 48000 for pw-record/arecord) is recorded
  honestly in `fmt` and no rate claim is made.
- **ffmpeg KILL class is a union by design** (`:3729-3741`); the flushed-prefix
  alignment was observed unaligned in both my probe (262066) and the
  canonical receipt — the report's deliberate non-pinning
  (`r76-author.md:234-236`) is honest.
- **Contention window**: `arecord_busy` cells are only reachable when a
  foreign holder exists; my run saw none, the concurrent run did (§4.4).
- **No LSP device in this seat's tool surface** (no server to `status`, so no
  `references`/`definition`/`diagnostics` query was possible). Caller and
  definition checks were therefore done by reading the committed source and,
  where it matters, by *executing* it: the only callers of the r76 helpers are
  the six entry functions and `main()` (`:4477-4495`), and the receipts prove
  every helper was reached with the pinned arguments. Nothing in this report
  rests on text grep as semantic proof.
- Seat-card runtime checks (one canonical runtime, same-identity reroute,
  `resume_continuity_v1`) are out of scope for this lane: this repo is the
  shokunin audio corpus, no runtime/judge was invoked and no other judge
  exists here. No subagents, no git mutation, no tracked-file edit was made
  by this seat; all writes stayed in `reports/round-76/r76-reviewer.md` and
  `corpus/live/r76-reviewer/`.

## 7. Recommendation

**ADMIT-corr**: the committed r76 arm is behaviorally sound — every headline
claim reproduced from raw evidence by an independent replay (6/6 entries
`failures: {}`, 17/17 prior rows byte-identical to r75), the KILL partition
and accept-and-lie are real at the byte level, and the contention path
degrades honestly. Fold MEDIUM-1 (non-emptiness floor on the TERM/parecord-KILL
carriers) and MEDIUM-2 (seat-named scratch dir) before the family is treated as
a durable ledger carrier; LOW-3 belongs in the report's honest-bounds section as
a one-line caveat.
