# r83 VERIFIER — non-author verification of `a151a226` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`).
Lane `~/Projects/shokunin/audio-shokunin`. Window **2026-10-15
22:12–22:29Z**. Verification target: commit **`a151a226`** ("r83 author:
128 legs / 7 entries — malformed-prop 2-class lattice, SIGSEGV family
rc=-11, -d transport delay, uint32 wrap, full-wave |x| artifact; 2 green
runs"), frozen via `git archive` — **not** the worktree (the worktree
fixture was edited by a sibling mid-window; §5). Toolchain
receipt-identical to the author's pin: PipeWire **1.6.8** (pw-loopback /
pw-cat / pw-record / pw-dump), WirePlumber **0.5.17-1**, libpulse
**17.0+r98+gb096704c0** (`PulseAudio (on PipeWire 1.6.8)` protocol 35),
Python **3.14.7**, NumPy **2.5.3** (`toolchain.txt`). **No tracked
writes, no commits, no pushes, no `pactl set-default-*`, no manual
PipeWire objects left.** Namespace `r83v_*` for all seat artifacts;
scratch `/tmp/r83v-work/` removed at exit.

## 0. Verdict

**VERIFIED.** Every assigned check passed on the frozen `git archive
a151a226` tree under real load (loadavg ~55–89 the whole window; three
foreign r83 lanes concurrently live — §6):

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive a151a226` | tar `ceee6ef2…`, 54 605 members, extracted 43 013 files / 11 593 dirs / 0 symlinks, file-set symdiff vs `git ls-tree -r a151a226` = **0** | PASS |
| fixture identity | landed fixture at a151a226 | tree sha256 `26431adf29ab122bbf1f55ef03c9aa47bf9825c61654562d9a421117434f5eea` (git blob `27fe9710…`), identical before **and** after all 3 runs | PASS |
| py_compile | clean | rc=0 (inside frozen tree) | PASS |
| `normal` receipt sha | canonical `8e8cdad6…` | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical (also the sha of the newest worktree canonical `20261015T195629594751Z-normal` and ~200 historic receipts) | PASS |
| `--probe-pwcat-r83` ×2 under load | failures `{}` | run1 `20261015T221743619360Z` + run2 `20261015T222335687486Z`, both rc=0 `{"failures": {}}`, stderr 0 B | PASS |
| 128 legs ×2 executed green | all legs, no skips | 128/128 per run (29+19+26+13+18+15+8 across the 7 entries + 17 base 0-leg entries = 24 measurements); every leg carries a terminal record (rc/signal for shot legs; `linked`/`tap_exit`/`transport_s` for the 10 onset legs; `nodes_after` for crash legs) | PASS |
| verdict-surface stability | deterministic | **0 diffs** exact + named tiers, v1 vs v2 **and** v1 vs author run2 | PASS |
| custody/teardown | zero residue | in-receipt `sinks_gone` all true + `own_nodes_after: []` on all 7 entries ×2; post-state: **0** `r83v_*`/`r83a_*` objects, 0 modules, 0 processes | PASS |
| spot re-derivations | ≥5 | **13/13 reproduced** (incl. all four SIGSEGV arms, both rc classes, uint32 wrap, |x| artifact, `-d` +1.00 s transport) | PASS |

## 1. Frozen tree

- `git archive a151a226 -o /tmp/r83v-work/r83v-tree.tar` → sha256
  `ceee6ef260cd3d08b0eedab13b05d0f38c336360277140f51970d37ebd5dfe31`,
  54 605 members; extracted to `corpus/live/r83-verifier/tree/`
  (gitignored regenerable-snapshot path per `corpus/.gitignore`
  `live/**/*tree*/`): 43 013 files / 11 593 dirs / 0 symlinks.
- File-set symmetric difference vs `git ls-tree -r a151a226
  --name-only` = **0 lines**.
- Fixture inside tree: sha256 `26431adf…`, git blob `27fe9710` —
  unchanged before and after all three runs.
- **HEAD moved mid-window** `a151a226 → de97d2f6` (sibling
  r83-simplifier commit 22:22:35Z) **and** the worktree fixture was
  left dirty (+198/−77 vs the new HEAD — a sibling's in-flight edit
  adding `import fcntl`, the r82-critic-F4 exact-match unload fix,
  etc.). Both are irrelevant to this verdict — the archive pinned
  a151a226, not HEAD and not the worktree.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 22:12:23→22:12:27 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r83v1 | 22:12:35→22:17:43 | `… --probe-pwcat-r83` | 0 | `{}` | `be4fa3016784cec931304390ae6b8622de22eb6242c84065721dbbb1340afd8a` |
| r83v2 | 22:18:30→22:23:35 | `… --probe-pwcat-r83` | 0 | `{}` | `26d755ed29d30dd58de8a65ba8efdf841c58682301cad2a938fb571ca67bd312` |

- Census per probe run: **24 entries / 128 legs**
  (`pwcat_props_parse` 29, `pwcat_empty_props_segv` 19,
  `pwcat_latency_props` 26, `pwcat_channel_matrix` 13,
  `pwcat_remix_props` 18, `pwcat_resample_props` 15,
  `pwcat_failopen_args` 8; + 17 base 0-leg entries) — exact match to
  the author's declared 128.
- `host_is_quiet: false` in 7/7 (v1) and 2/7 (v2) entries; foreign
  `pw_loopback`/`pw_cat`/`ffmpeg`/`fixture_runs` counted by the
  in-receipt contention census — the family still went fully green.
- Content witnesses: 76 `tap_stats`/`window_amps`/`sample` records per
  run, **0** `unsupported`/`exists:false`.

## 3. Verdict-surface stability (`runs/surface-diff*.txt`, method `surface.py`)

The r83 receipt is richer than r82's — per-leg analog fields
(settled-window amps, window amps, dev ratios, transports) are
honestly noisy. The surface was therefore tiered: **exact** =
rc/signal/error_class/error_hit/killed_at_bound/linked/move_rc/
failopen_target_is_default/out_port_names/post_move_consumers/
content_witness/stderr_tail/tap_exit/nodes_after/sink_input(minus
volatile pactl indices)/pre_move.consumers/tap.carries_tone/
tap_stats{exists,rate,settled_frames,all_zero}/out.{exists,rate}/
window_amps.exists — all pid/freq-normalized; **named** =
outcome/mono_outcome/control_outcome/artifact_outcome; **analog** =
reported, never exact-diffed.

- v1 vs v2: **0 exact diffs, 0 named diffs** — the whole verdict
  surface is deterministic under load.
- v1 vs author run2 (`4ce6812f…`): **0 / 0**.
- v1 vs author run1 file (`4e56f4b0…`): **0 exact / 2 named** — only
  the two disclosed load-realized honest arms: `c1_mono_1`
  `silent_or_thin`→`stable`, `m_alone_1` `unmeasured`→`stable_mono`
  (same vocabulary the author documented; both are recorded arms, not
  failures).
- Author run1 vs run2: 0 exact / same 2 named diffs (measured
  independently, `author-r1-r2.diff.txt`).
- The two earlier canonical runs (21:28:12Z, 21:50:17Z) are
  dev/pre-green and carry real failures — expected drift, not gate
  evidence (§4-F2).
- Entry summaries match structurally: `onset_summary` deltas
  [1.0427,1.0399,0.9983] vs author [1.0429,0.9999,0.9992] (envelope
  [0.75,1.45]); `ctl_median` 0.1033 vs 0.1054 s; `remix_summary`
  control medians 8165.5 vs 8172.5; `resample_summary`,
  `matrix_summary`, `named_outcomes`, `serials` — identical modulo
  pid.

## 4. Spot re-derivations — 13/13 reproduced (`spot/spots*.jsonl`)

Independent re-executions of the pinned argv shapes (own
`r83v_<pid>` sinks loaded by name-verified `pactl load-module`,
unloaded by index re-verified against `sink_name=`; scratch
`/tmp/r83v-work/spot/`):

| spot | leg shape | pinned | measured |
| --- | --- | --- | --- |
| s1 | `pw-loopback -n r83v_s1 -i ''` | SIGSEGV rc=-11 | **rc=139**, `dumped core` |
| s2 | `pw-loopback -o ' '` | SIGSEGV (whitespace) | **rc=139** |
| s3 | `pw-cat -p -P '' <tone>` | SIGSEGV | **rc=139** |
| s4 | `pw-record -P '' <wav>` | SIGSEGV | **rc=139** |
| s5 | `pw-loopback -i 'a=b }{ c=d'` | rc=255 `--capture-props`, zero nodes | **rc=255** `Mismatched bracket`, nodes `[]` |
| s6 | `pw-cat -P 'a=b }{ c=d'` | rc=1 `--properties` | **rc=1** `Mismatched bracket` (per-binary split confirmed) |
| s7 | `-i '}{ garbage'` | silent drop, defaults | both nodes spawned, `media.name='<tag> input'` default, **stderr empty** |
| s8 | `-l -5` | uint32 wrap | `node.latency='4294967056/48000'` |
| s8b | `-d 0.25 -l 5` | `-l` beats `-d` | `node.latency='240/48000'` |
| s9 | `pw-cat -P resample.disable=true` 44.1k→48k | all-zero monitor | `settled_all_zero=true`, peak 0, 144 000 frames |
| s10 | `pw-cat -P resample.peaks=true` 44.1k→48k | full-wave `|x|` + octave | **min=0, neg_frac=0, mean +4790.9, zero_frac 0.0833/0.0875 (≈1/12), amp@f0 1.9/0.0 destroyed, amp@2f0 3184.9/3185.9 dominant on both channels** |
| s11c/s11/s11l | link-gated `-d 1.0` vs ctl vs `-l 1000` | `-d` real, `-l` prop-only | ctl 0.351 s, **-d 1.0 → 1.353 s (Δ +1.002)**, -l 1000 → 0.336 s (Δ −0.015) |

My spot ctl transport (0.35 s) exceeds the fixture's quiet-ish 0.10 s
because the spot ran under ~80+ ambient load; the pinned **delta**
(+1.002 s vs the fixture's +0.998–1.043) is the invariant and it
reproduced. s7/s8 were re-run with mid-run sampling after a
first-pass methodology bug sampled pw-dump post-mortem (noted in
`spot/` for honesty; the corrected rounds are `spots2.jsonl` /
`spots3.jsonl`).

## 5. Findings (ranked)

- **F1 (minor, report transcription)** — the author's
  `corpus/live/r83-author/measurements-run1.json` is byte-identical
  (sha `4e56f4b0…`) to canonical run `20261015T220105801638Z-pwcat-r83`,
  **not** to the cited "21:50:17Z" stamp. The 21:50:17Z run exists in
  `runs/` but is a **pre-green run carrying 17 failures** (channel-band
  misses + the disclosed `r93b_in` foreign-default rotation leg). The
  report's claim "two green runs" is still true — the two byte-copied
  files are exactly the two green canonical runs (22:01:05Z +
  22:06:45Z); only the timestamp citation is off by one run. No
  content impact: the declared run1 file IS a green run and its
  surface matches mine.
- **F2 (ledger hygiene, non-blocking)** — `corpus/live/runs/` holds
  four `*-pwcat-r83` receipts: 21:28:12Z (dev, failures),
  21:50:17Z (pre-green, failures), 22:01:05Z + 22:06:45Z (the green
  pair). The failed iterations are legitimate dev history and the
  report does not hide them, but a reader joining receipt-corpus to
  report-prose should know the first two are not the cited green runs.
- **F3 (honest arms behave as documented)** — `m_alone` realized
  `stable_mono`×3 and `c1_mono` `stable`×3 in **both** my runs under
  load (author's run2 identical; run1 recorded `unmeasured`/
  `silent_or_thin` once each). The `-m '[ MONO ]'` alone arm remains
  load-dependent; the fixture records realized arms and never asserts
  stability — verified honest.
- **F4 (worktree churn during window)** — sibling seats stayed live:
  commit `de97d2f6` (r83-simplifier PASS) landed 22:22:35Z and the
  worktree `measure_audio.py` was left dirty (+198/−77 vs new HEAD).
  The frozen tree insulated the gate; verifier sha pins are against
  the archive.
- **F5 (analog envelopes all inside pins)** — `-d` deltas
  [1.0427,1.0399,0.9983] ∈ [0.75,1.45]; `-d 0.25` transports
  [0.3941,0.3526] → deltas in [0.08,0.60]; `-l 1000` [0.142,0.1027]
  ≤ ctl+0.25; `mono_mix_dev_ratio` legs inside [0.42,0.58]; peaks
  forced-zero fraction ~14.6 % (author) — my run measured the same
  class (verifier `zero_frac` per leg inside the recorded 8–15 % band;
  independent spot: 8.3/8.8 %). All arms consistent.

## 6. Contention ledger

Foreign seats live in-window, observed read-only, never touched:

| foreign object / process | what it was doing |
| --- | --- |
| r83-critic lane (pids 3512570/3512627/3512630) | own `measure_audio.py --probe-pwcat-r83` replay on the **worktree**; sinks `r83a_ns_{a,b}_3512630`; node `…_land_brace` live at 22:12 |
| `r83r_*` lane (pid ~3699317) | third concurrent r83 replay (`r83r_ns_{a,b,44}_3699317`, `…_drop_silent` nodes) |
| `r83c_e1/e2` nodes | fourth foreign r83 seat, live 22:17 |
| ~45 leaked `yes` CPU hogs (pgids from earlier game-dev arms; etimes 6900–7800 s) | ambient load ~55–89 — not mine, pre-existing |
| game-dev r94-critic/scribe/simplifier batteries | `run_battery.py --godot` / `--runs` sweeps |
| sibling commit `de97d2f6` + worktree fixture edit | r83-simplifier seat landing mid-window |

Interference caused by this seat (all disclosed, all bounded): four
probe-owned null sinks loaded then unloaded by name-verified index;
spot legs linked streams to `r83v_*` sinks only — **no tone ever
targeted a shared/foreign sink**; the `-d`/`-l` legs played only the
tag tone into `r83v_nsa`. Default sink/source unchanged
(`…SPDIF__sink` / `…Line__source`) at pre- and post-state.

## 7. Evidence map (`corpus/live/r83-verifier/`)

`toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs/commands.log`, `runs/{normal,r83v1,r83v2}.stdout.json`
(+`.stderr.log`, all 0 B), `runs/*.receipt.json` (byte-copies of the
frozen-tree receipts, also under `tree/corpus/live/runs/20261015T
{221227915826Z-normal,221743619360Z-pwcat-r83,222335687486Z-pwcat-r83}/`),
`receipt-shas.txt`, `runs/surface-diff{,-vs-author}.txt`,
`surface.py` (the tiered comparator), `author-r1-r2.diff.txt`,
`spots{,2,3}.sh` + `spot/spots*.jsonl`, `manifest.json` (24 files /
1 672 557 B), `tree/` (gitignored archive materialization).

## 8. Risks / blockers

- None blocking. Honest carries: the spot `-d` ctl transport rode
  higher under ~80+ load (0.35 s vs the fixture-run 0.10 s) — the
  envelope-pin invariant is the **delta** and it held exactly; the
  `m_alone`/`c1_mono` honest arms will keep realizing load-dependent
  names by design; the worktree was dirty at window end (a sibling's
  in-flight edit — preserved untouched, no shipping decision made).
