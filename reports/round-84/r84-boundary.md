# R84 boundary — attack on r84 scout claims under load

Seat **BOUNDARY** (leaf, r84). Host `plazir27`, measured **2026-10-15 ~19:35–20:2x UTC**.
Repo `~/Projects/shokunin/audio-shokunin`. Namespace **`r84b_*`**; every write under
`corpus/live/r84-boundary/` + this report. **Zero tracked writes, zero commits, all own
processes killed, all own modules unloaded by index-verified id** (exit witness §10).

**Provenance note:** the scout report's header says `@ HEAD a2616f73`; actual HEAD at my
entry was `2333fac` (a2616f73 is an *ancestor*, committed 03:00 local; 2333fac at 16:12
local — after the scout's 03:36 report write). Host-behavioral claims are not invalidated
by the repo move; the report's HEAD line is simply stale. **Host was under heavy sibling
load throughout** (loadavg 25.9 at entry, 48 mid-session, 100+ during my hog windows —
`r93s_fc_in`/`r82ff_ns_3036129` streams RUNNING; `r83b` and `r82ff`/ffmpeg (`Lavf63.1.101`)
nodes observed in my own capture snapshots). This is the "under load" condition, plus an
explicit 24-CPU-burner + audio-hog replay of the two sharpest laws.

## 0. Verdict board

| # | scout claim | verdict | one-line evidence |
| --- | --- | --- | --- |
| 1 | `-D` device lattice + 5-way refusal taxonomy (verbatim) | **HOLDS** (25 legs ×2) | all rc/err strings byte-identical; `Unknown PCM `, `Cannot get card index for`, `Unknown parameters CARD=Audio`, `Host is down`, ENOENT, `Channels count (1) not available` |
| 2 | plugin args `NODE/ROLE/RATE/CHANNELS/PERIOD_BYTES` + env vectors | **HOLDS** | `target.object`, `media.role`, `node.latency=1024/48000`, RATE warning, CHANNELS refusal, `PIPEWIRE_NODE`/`PIPEWIRE_PROPS` land |
| 3 | `EXCLUSIVE=1` → rc=0 | **FLAKY/BOUNDED** | one batch: rc=1 hw-params refusal ×2 (`pipewire:EXCLUSIVE=1`); follow-up matrix 6/6 rc=0 incl. same form. Precondition unattributed |
| 4 | plugin capture has **two state-dependent refusal shapes** (`hw params` vs `TICK_TIME`) | **FALSIFIED** | all bare-plugin refusals observed are **one stderr**: the hw-params dump whose **last line is `TICK_TIME: [0 0]`** — including the scout's own raw stderr. The "two shapes" are two line-slices of one stream |
| 5 | plugin capture revival by explicit `NODE=` | **HOLDS** | bare rc=1 in batch, `NODE=<Line>` rc=0 352844 B same batch; `NODE=`+`-f dat` rc=0 384044 B |
| 6 | `speaker-test` headless cells | **HOLDS** | `-D null -c2 -l1` rc=0 (0.01 s, unpaced), `-c 0` rc=0, `hw:0,0 -c1` refusal verbatim, `pipewire:NODE=` rc=0 wall 6.17 s node `alsa_playback.speaker-test` |
| 7 | `PULSE_PROP_*` verbatim vector, 2 exceptions | **HOLDS** (10 legs ×2) | raw `Communication` on node vs `phone`+restore-id in proplist; `application.name`/`media.name` dropped; `icon_name`→`icon-name`; `zzz.invented=42` int; bare `PULSE_PROP=` parsed |
| 8 | volume % is cubic, ≤250 ms | **HOLDS ambient AND under hog** | 3/3 ×0.125 (1024), ×3.375 (27648), ×0.015625 (128); `set-source-volume monitor` ×0.125; first change ≤0.1 s window; identical under 24-CPU+audio hog (loadavg 100–104) |
| 9 | suspend is an idle-hint, never a gate | **HOLDS ambient AND under hog** | linked sink stays RUNNING, node `running`, tone 8192→8192 (9011 with hog tone summed), player rc=0 full 7.1 s; idle→SUSPENDED; `suspend 0` stays SUSPENDED; play wakes; `2`→`Invalid suspend specification.` |
| 10 | `parec --monitor-stream` pin laws (`-d` ignored, move follows, source-output idx 44-B, bad idx rc=1) | **HOLDS** | A-only sig under bogus/foreign/absent `-d`; move → links to `r84b_ns2`; soidx rc=0 44 B; `0`/`999999` rc=1 44 B |
| 11 | monitor tap is **pre-gain** (`set-sink-input-volume` mid-run invisible, mute visible) | **FALSIFIED** (one unexplained outlier kept) | clean pre-state: write 100%→50% mid-run → tap **8192→1024** (monfix 2/2 + D1 + D3); scout's own p6 receipt shows tap **1024 from t=0** (their stream was already at restored 50%) — their "unchanged 8192" contradicts their own raw data |
| 12 | kill pinned stream → file stops growing, no EOS | **BOUNDED** | parec alive + no error/EOS 2/2; file-size behaviour rep-dependent (one rep plateau 768044→768044, one kept growing with silence to 1065644) |
| 13 | stream-restore stickiness (volume) | **HOLDS + extended** | respawn 30% → tap amp **221** = 0.3³×8192 exact; repair verified 100%; **mute is also sticky** (new, §6.3) |
| 14 | `-D null` capture ≠ zeros | **BOUNDED (structure claim wrong)** | 668 nz rows/s ✓ (664–688 across rates), peak 32508 ✓, but bursts are **period-locked at 125 ms** with 3 (44.1/48 k) or ~6 (8 k) clusters per period — not "spaced exactly 5512 frames" |
| 15 | `-D ''` diverges between aplay and arecord (§8.2) | **FALSIFIED** | with a genuine empty argv element **both** print `Unknown PCM `; the `Unknown PCM -d` shape needs the empty element to be absent (getopt eats `-d`) — reproducible both ways in both tools |
| 16 | ebusy: rc=1 + `/proc` RUNNING | **HOLDS + extension** | busy 3/3 while player live; **busy persists ≥0.8 s after the stream dies**; released once sink re-suspends (`closed`, aplay rc=0) |

## 1. Falsification 1 — the plugin-capture "two shapes" are one stderr (slice artifact)

My raw stderr for bare plugin capture (batch A, ×2) and for all 5 follow-up variants:

```
arecord: set_params:1462: Unable to install hw params:
ACCESS: RW_INTERLEAVED
FORMAT: S16_LE
...
PERIOD_SIZE: (5512 5513)        # 44.1k; 6000 @48k; 1000 @8k
BUFFER_SIZE: 22050
BUFFER_BYTES: 88200
TICK_TIME: [0 0]
```

The scout's **own** raw stderr `runs/p2-arecord/pipewire/rep{1,2}/stderr` is byte-for-byte
this same stream (ends `TICK_TIME: [0 0]`). Their second-batch receipt
`receipts/p2b-plugin-capture.json` recorded `err: ["BUFFER_SIZE: …","BUFFER_BYTES: …",
"TICK_TIME: [0 0]"]` — i.e. **the last three lines of that same dump**. The harness
printed different line-slices per batch; the report then classified the slices as two
"state-dependent shapes".

Follow-up shape hunt (5 format/rate variants × bare `pipewire`/`default`, plus
`NODE=`+`-f dat`): **5/5 refusals show the identical combined stderr; the only success is
the explicit-`NODE=` leg** (`hunt_node_dat` rc=0, 384044 B). No `TICK_TIME`-only stderr was
observable in any window today. Scope note: I cannot disprove that a *historical* window
(r78p's rc=0, or the scout's 06:2x batch) differed; what I falsify is the claim that two
distinct refusal texts are the observable states of this surface — every observed refusal
contains both markers, so `alsa_pw_hwparams` and `alsa_tick_time` are not disjoint classes
(a substring classifier for `TICK_TIME` matches both). Raw: `runs/pF2-followup/hunt_*/rep0/stderr`.

## 2. Falsification 2 — `-D ''` does not diverge between aplay and arecord

| form (exact argv) | arecord | aplay |
| --- | --- | --- |
| real empty element (`["-D","",...]`, bash `-D ''` and execve) | rc=1 `Unknown PCM ` | rc=1 `Unknown PCM ` |
| empty element dropped (`-D -d 1`, so getopt takes `-d`) | rc=1 `Unknown PCM -d` | rc=1 `Unknown PCM -d` |

Same invocation shape ⇒ same device string consumed. The scout's `Unknown PCM -d` is
reproducible only when the empty element is absent from argv (their recorded `cmd` shows
`-D ''`, so their harness must have dropped it before exec) — a harness artifact, not an
arecord-vs-aplay parsing difference. Raw: `runs/pF2-followup/empty_*/rep0/{cmd,stderr}`.

## 3. Falsification 3 — the monitor tap is not pre-gain (and the scout's own receipt says so)

Scout §7 tail: "`set-sink-input-volume A 50%` at 2.4 s → tap amp **unchanged 8192** — the
tap is pre-stream-gain". Their raw receipt `runs/p6-monstream/monA_sivol/rep{1,2}/result.json`
shows `sig: [[0.0, "A", 1024]]` — the tap read **1024 for the whole capture**, i.e. the
stream was already attenuated at spawn (their own earlier 30 %/50 % stream-restore writes,
§7 tail, had persisted on the role-keyed restore entry). Their 2.4 s write was a **no-op on
an already-50 % stream**; the report's "unchanged 8192" does not match their data.

My clean replays (stream-restore reset to 100 % live, verified `pre_si=100%`):

| leg | pre | mid-run write | tap before | tap after |
| --- | --- | --- | --- | --- |
| `pF3-monfix/sivol_clean` rep0 | 100% | `set-sink-input-volume A 50%` | 8192 ×5 | **1024** ×10 |
| `pF3-monfix/sivol_clean` rep1 | 100% | same | 8192 ×5 | **1024** ×10 |
| `pF4-sivolpin/D1_music_noentry` | 100% | same | 8192 | **1024** |
| `pF4-sivolpin/D3_music_prewrite100` | 100% | same | 8192 | **1024** |
| `pF4-sivolpin/D5_fresh_mute` | 100% | `set-sink-input-mute A 1` | 1024 | **0** (mute visible, as claimed) |

So the mid-run stream volume **is** visible on the per-stream tap (exact cubic ×0.125), and
mute is visible too — the "mute node-level / volume mix-level" split does not hold in the
clean state. **One outlier is kept on the record**: my first b_mon rep0 (`monA_sivol` in
`pF-monstream`) showed tap 8192 flat after the write. It did not reproduce (4 subsequent
clean runs all visible) and its precondition is unattributed; the scout's law may hold in
some state I did not isolate. Two other reps in that batch spawned at restored 50 % — which
is itself a live confirmation of claim 13, not a pre-gain datum.

Mechanism note (new): `pw-play` sets `media.role=Music` **by default**, so pw-play streams
key stream-restore as `sink-input-by-media-role:music` (lowercase) — a much broader restore
key than the scout's "by application name" phrasing. Raw:
`runs/pF3-monfix/{sivol_clean,kill_trace}`, `runs/pF4-sivolpin/*`.

## 4. Bounded / flaky claims

- **`EXCLUSIVE=1`**: scout's form `pipewire:NODE=ns,EXCLUSIVE=1` rc=0 (their receipt);
  my batch B `pipewire:EXCLUSIVE=1` (no NODE=) rc=1 hw-params dump ×2 at loadavg ~50;
  follow-up `excl_bare1`/`excl_node1`/`excl_node0`/`excl_bare1_ns` all rc=0 ×2 each.
  Net: acceptance is state-flaky; one refusal batch observed, not reproduced. Precondition
  unattributed. Raw `runs/pB-plugin/a_pw_excl`, `runs/pF2-followup/excl_*`.
- **kill-pinned-stream file growth**: parec stays alive with no error/EOS (2/2), but one
  rep's file plateaued (`768044` constant across 5 samples) while the other kept growing
  with silence (`547244→1065644`). "File stops growing" is rep/state-dependent. Raw
  `runs/pF3-monfix/kill_trace/*` (`size_trace`).
- **`arecord -D null` burst structure**: 668 nz rows/s (44.1 k) / 664 (48 k) / 688 (8 k),
  peak 32508/32508/32564. Bursts are **period-locked at 125 ms**: period 5512 @44.1 k,
  6000 @48 k, 1000 @8 k frames; burst starts per period at offsets ≈0/1026/4850 (44.1 k,
  48 k) and ≈0/258/260/500/758/760 (8 k); consecutive-burst spacing pattern 1026/3824/662
  (44.1 k). The "spaced exactly 5512 frames" phrasing describes the period, not burst
  spacing. Raw `runs/pA-replay/r_null`, `runs/pF2-followup/null_r48000|null_r8000`.
- **Analog floor**: `arecord -D hw:0,0` peak **700** (scout 620–663) — floor is
  host-state variable; `hw:0,1` exact 0 holds exactly (both reps, both batches).
- **ebusy extension**: refusal + `state: RUNNING` 3/3 while a live stream holds the PCM;
  after killing the player the PCM stayed `RUNNING` and busy ≥0.8 s; released when the sink
  re-suspended (`closed`; `aplay -D hw:0,0` rc=0). Raw `runs/pH-ebusy/*`.

## 5. Confirmed under load (verbatim board)

- **Cubic law, hog replay** (`pD-hogvol`, 24 CPU burners + `pw-play`+`pw-record` hog on
  `r84b_ns2`, loadavg 100.1→104.4): ×0.125, ×3.375, ×0.015625 — 3/3 each, transition
  within the first 0.1 s window after the write; `set-source-volume <ns>.monitor 50%` ×0.125
  mid-stream; mute 0→8192.
- **Suspend, hog replay** (`pE-susp` final run, audio hog summed into the sink): tone
  9011→9011 unbroken, sink RUNNING, node `running`, player rc=0 full wall; with the hog
  stream linked, `suspend-sink 1` left the sink RUNNING (hint-only confirmed under load).
- **PULSE_PROP vector** (10 legs ×2): `Communication` raw on node / `phone` in proplist +
  restore id; `Music`→`music` (canonicalization extends to known PA role names); `notarole`
  verbatim; `zzz.invented=42` int; `icon_name`→`icon-name` on node; `application.name` and
  `media.name` dropped (client wins); `module-stream-restore.id` prop lands on node but the
  server's key stays `sink-input-by-application-name:paplay`; bare `PULSE_PROP=` parsed.
- **Plugin arg surface**: `NODE=`→`target.object` (pin verified by link witness);
  `NODE=no_such` rc=0 + `target.object` set + links to the **measured current default**
  (SPDIF); `ROLE=Communication`→`media.role`; `PERIOD_BYTES=4096`→`node.latency=1024/48000`;
  `RATE=44100`→`Warning: rate is not accurate (requested = 48000Hz, got = 44100Hz)` +
  plug-plugin hint (the report's parenthetical is a paraphrase; raw has spaces/Hz);
  `CHANNELS=6`+stereo→`set_params:1404: Channels count non available`;
  `SERVER=nonexistent`→`Host is down`; `PIPEWIRE_NODE`→`target.object`;
  `PIPEWIRE_PROPS={node.name=X media.role=Communication}` → node `X` with role.
- **speaker-test**: `-D null -c2 -l1` rc=0 in **0.01 s** (unpaced; scout's 0.16 s is the
  same law), `-c 0` rc=0, `hw:0,0 -c1` refusal verbatim, `-t bogus` verbatim,
  `pipewire:NODE=<ns>` rc=0 wall 6.17 s node `alsa_playback.speaker-test`
  `target.object=r84b_ns` (my first batch's rc=-9 was my own 3 s finish cap — rerun natural
  exit rc=0).
- **Monitor-stream**: `sink_monitor` A+B peak 16104; pin A-only (peak 8192, B bins ≈0)
  under `-d ns`, no `-d`, bogus `-d`, foreign `-d`; `move-sink-input` → `r84b_ns2` links,
  capture follows; `mon_soidx` rc=0 44 B; `0`/`999999` rc=1 + 44 B; `monA_simute` tap 0 then
  back (with the restored 50 % base it returned to 1024).
- **Sticky restore**: 30 % write → respawn `value_percent: 30%`, tap amp **221**
  (= 0.3³ × 8192, exact); repair to 100 % verified by fresh respawn.

## 6. New modes / laws (not in the scout's lattice)

1. `NODE=<sink>.monitor` as a **playback** target: rc=0, `target.object` set, links to the
   **default sink** (silent fallback — extends the one-sided fallback law to monitor names).
2. Same name as a **capture** target: rc=1 hw-params refusal (no monitor-suffix bypass
   through the plugin).
3. `pactl set-sink-volume <ns> 50.5%` → rc=0, stored **33095 = 65536×0.505** (display rounds
   to `50%`); bare `1.5` → rc=0, stored **75020 = 65536×1.5^(1/3)** (a bare float is a
   *linear amplitude*, not a percent); `-10%` relative accepted.
4. **Mute is sticky through module-stream-restore** like volume: mute a live stream, let it
   die → the next same-key stream spawns muted (tap 0) with `value_percent` still 50 %;
   unmute+100 % on a live stream repairs it (fresh spawn 100 %, amp 8192).
5. `pw-play` default `media.role=Music` ⇒ role-keyed restore entries.

## 7. Contention ledger (mandatory)

**Foreign state present:** entry sinks `r93s_in` (IDLE), `r93s_fc_in` (RUNNING),
`r82ff_ns_3036129` (RUNNING); during my capture witness: source-output
`input.r83b_s2_C5` (r83b lane) and node `Lavf63.1.101` (r82ff/ffmpeg) — observed only.
Default sink/source were **never changed by me**; no foreign module/node/stream was killed,
moved, suspended, or re-volumed; `pactl suspend` (bare) and `pactl exit` never invoked.
The scout's r78 leftover sinks were already gone at my entry (checked).

**Events caused by this seat (all disclosed):**
1. ~12 plugin/default playback legs landed 1.2–6.2 s of tag tone on the **current default
   sink** (SPDIF) — bounded, link witnesses in receipts; the ebusy leg played ~1 s to
   Speaker, which woke it and re-suspended on its own (entry state SUSPENDED preserved).
2. SPDIF moved IDLE → SUSPENDED by idle timeout after my last landing (benign; wakes on use).
3. **Stream-restore writes** to the `sink-input-by-media-role:music` key (pw-play default):
   50 % (sivolpin/D-legs, b_mon), 30 % (sticky leg), and **mute=1** (sivolpin D5). This
   contaminated two of my own later measurements (pE-susp zeros; repro silence) before I
   diagnosed it — **repaired and verified**: fresh pw-play spawns 100 %, unmuted, monitor
   amp 8192 (`runs/…` + repair receipt in §6.3 evidence). No sibling pw-play was observed
   during the contaminated window; any sibling spawn in it would have been attenuated.
4. One crashed batch (`pD-vol` wiring bug) leaked `pw-play` + `pw-record` (my namespace);
   both killed within ~1 min, scratch file removed.
5. All my null sinks (`r84b_ns`, `r84b_ns2`) unloaded by index-verified module id; zero
   `r84b_*` objects/processes at exit (§10).

## 8. Method hazards found (for the fleet)

1. **`pw-record` + SIGKILL leaves a WAV with data-size 0** → naive readers see an empty
   capture and report "flat/absent". Use SIGTERM (or parse available bytes). My first
   suspend run read `-1` for this reason.
2. **Stream-restore contamination is not just volume — mute too**, and for `pw-play` the
   key is role-based (`media.role=Music` default), so a stray write hits every later
   pw-play. Reset with a live unmute+100 % write and verify with a fresh spawn.
3. **Any "tap unchanged" conclusion must verify the stream's pre-state** (`value_percent`
   *and* mute at spawn). A write on an already-attenuated stream is a no-op that looks like
   a pre-gain law (this is how the scout's C34 was produced).
4. A 3 s `finish()` cap silently SIGKILLs 6 s tools (speaker-test, 7 s players) → rc=-9
   "failures" that are harness artifacts; wait for natural exit before scoring.
5. Load is not neutral: the same leg can run at loadavg 10 or 104; record loadavg per leg.

## 9. Scout §12 falsification list — item-by-item outcome

| item | outcome |
| --- | --- |
| 1 `NODE=` writes `target.object` | not falsified (prop + pin witnessed) |
| 2 silent fallback on `NODE=` miss | not falsified (measured link → current default) |
| 3 capture needs explicit `NODE=` | not falsified (revival + `-f dat` success) |
| 4 two refusal texts are state-dependent | **FALSIFIED** — one stderr; classes overlap (§1) |
| 5 volume % cubic | not falsified (exact, ambient + hog) |
| 6 suspend hint-only | not falsified (ambient + hog) |
| 7 tap pre-gain / mute node-level | **FALSIFIED** (§3; scout's own receipt contradicts) |
| 8 `--monitor-stream` ignores `-d` | not falsified (3/3 shapes) |
| 9 env props lose to client proplist | not falsified (`appname`/`medianame` dropped) |
| 10 null capture ≠ zeros / 5512 spacing | 668-rows not falsified; **spacing claim falsified** (period-locked 125 ms, multi-cluster) |
| 11 source-output idx → 44-B accept | not falsified (rc=0 44 B) |

## 10. Exit witness (cleanup)

`pgrep -af r84b_` → none; `pactl list short {sinks,modules,sink-inputs,source-outputs}`
grepped for `r84b` → none; `/tmp/r84b_*` → none; `git status --short` → only the
**pre-existing** ` M corpus/fixtures/measure_audio.py` + `.pyc` (present at entry, never
touched by this seat); default sink `…SPDIF__sink`, default source `…Line__source`
(unchanged); Speaker/SPDIF both SUSPENDED (Speaker as at entry; SPDIF post-idle-timeout).

## 11. Receipts index (`corpus/live/r84-boundary/`)

- `r84b_probe.py` — main harness (replay/plugin/props/vol/hogvol/susp/hogsusp/mon/ebusy).
- `r84b_followup.py` — empty-arg two-form, capture-node witness, EXCLUSIVE matrix,
  speaker-test natural exit, shape hunt, null rates.
- `r84b_monfix.py` — restore-reset sivol reps, live kill growth trace.
- `r84b_sivolpin.py` — tap-visibility discriminator matrix (D1–D5).
- `receipts/`: `pA-replay.json` (25 legs ×2 + null nz), `pB-plugin.json` (15 legs),
  `pC-props.json` (10 ×2), `pD-vol.json`, `pD-hogvol.json` (cubic law ambient/hog),
  `pE-susp.json` (final clean run incl. hog), `pF-monstream.json`, `pF2-followup.json`,
  `pF3-monfix.json`, `pF4-sivolpin.json`, `pH-ebusy.json`.
- `runs/<probe>/<leg>/rep*/{cmd,stdout,stderr,result.json}` — 215 leg dirs; raw stderr is
  the primary artifact for every verbatim claim.

## 12. Remaining unknowns / risks

- One unexplained tap-invisibility observation (b_mon rep0) — not reproducible in 4 clean
  runs; precondition unattributed. (State candidate: no explicit restore entry at spawn.)
- `EXCLUSIVE=1` flakiness: one rc=1 batch vs 6/6 rc=0 later; no named precondition.
- kill-leg file-growth divergence (plateau vs silence-growth) — tap teardown behaviour on
  stream death is state-dependent.
- Historical windows (r78p success, scout 06:2x) not re-measurable; my shape finding is
  scoped to every window observed today (the combined stderr contains both markers).
- **Labrat seat**: dispatched exactly one read-only `ufo-labrat` (state-flip hypothesis);
  it returned **UNTESTABLE — no process-execution capability in this substrate
  instantiation** (zero legs run, zero mutation). Its bounded leg list was executed by this
  seat instead (covered by `pA-replay`, `pB-plugin`, `pF2-followup`); no independent second
  seat verified these numbers.
