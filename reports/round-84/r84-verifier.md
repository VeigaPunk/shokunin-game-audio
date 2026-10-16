# r84 VERIFIER — non-author verification of `fbe65713` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`,
loadavg 50–56 all window). Lane `~/Projects/shokunin/audio-shokunin`.
Window **2026-10-16 00:40:23–00:54:40Z**. Target: commit **`fbe65713`**
("r84 author: 147 legs / 6 entries — monitor-tap gain laws …; 2 green
runs"), frozen via `git archive` — **not** the worktree (sibling seats
were live; §6). Toolchain receipt-identical to the author's pin:
PipeWire **1.6.8**, WirePlumber **0.5.17**, pactl/libpulse
**17.0-98-gb096** (protocol 35), alsa-utils **1.2.16**, Python
**3.14.7**, NumPy **2.5.3** (`toolchain.txt`). **No tracked writes, no
commits, no pushes, no `pactl set-default-*`; all seat artifacts under
`r84v_*`/`r84-verifier`; spot scratch removed at exit.**

## 0. Verdict

**VERIFIED** — on the frozen `git archive fbe65713` tree, an isolated
replay (r84v2) reproduces the author's committed verdict surface
**exactly**: 0 exact / 0 named diffs against **both** author runs on all
147 legs, `failures: {}`, custody clean. The one red replay (r84v1) is
fully explained by concurrent foreign r84 activity (§5-F1/F2) and is
reproduced green in r84v2.

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive fbe65713` | tar sha256 `5cd2d0f7…`, 55 171 members; extracted 43 533 files / 11 639 dirs / 0 symlinks; file-set symdiff vs `git ls-tree -r fbe65713` = **0** | PASS |
| fixture identity | committed blob | sha256 `8ed09d19990480fd337cba99e45cb0588e0615fd90e34793ecc4841c21368e4e`, blob `bc3e0d33…` — identical before **and** after all runs + spots | PASS |
| py_compile | clean | rc=0 (inside frozen tree) | PASS |
| `normal` receipt sha | canonical pin | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical | PASS |
| `--probe-alsapw-r84` ×2 under load | failures `{}` | run1 `00:40:28–00:45:16Z` rc=1 (3 failures — contended, §5-F1/F2); run2 `00:45:41–00:50:21Z` rc=0 `{"failures": {}}`, stderr 0 B | PASS (run2) |
| 147 legs ×2 executed | all legs, no skips | 147/147 per run (38+22+14+24+16+33 across the 6 entries); `coverage_blocked` absent | PASS |
| verdict-surface stability | deterministic | **v2 vs author run1 = 0/0**, **v2 vs author run2 = 0/0**; author run1 vs run2 = 0/0; v2 vs v1 = 13 exact diffs, all in the foreign-contamination set | PASS |
| custody/teardown | zero residue | in-receipt `sinks_gone` all true + `own_nodes_after: []` on all sink-owning entries ×2; post-state: **0** `r84v_*` sinks/sources/streams/procs, 42 modules at seat baseline (44 at exit = the live foreign replay's 2 sinks) | PASS |
| spot re-derivations | ≥5 | **17 distinct spot shapes / 20 records**: 16 shapes reproduced exactly, 1 sub-claim falsified (F3), 2 disclosed protocol re-runs | PASS-with-finding |

## 1. Frozen tree

- `git archive fbe65713 -o …/tree.tar` → sha256
  `5cd2d0f72ca1e752c9915e9892f413b23dc6b8bf11046201bd0bb81cd4e2a965`,
  55 171 members; extracted to `corpus/live/r84-verifier/tree/`
  (gitignored regenerable path per `corpus/.gitignore live/**/*tree*/`):
  43 533 files / 11 639 dirs / 0 symlinks; symdiff vs
  `git ls-tree -r fbe65713 --name-only` = **0 lines**. The 1.6 GB tar
  was deleted after extraction; its sha is pinned here and in
  `runs/tree-tar-sha.txt`.
- Fixture inside the tree: sha256 `8ed09d19…` (blob `bc3e0d33…`) —
  unchanged after 2 probe runs, 1 normal run and 16 spots.
- Worktree tracked state untouched by this seat: `git status` shows only
  the **pre-existing** ` M corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
  (present at seat entry, 21:39). The worktree fixture itself stayed
  clean at `fbe65713` throughout; my only addition is the untracked
  `corpus/live/r84-verifier/`.
- Commit shape confirmed: `+2796 / −3` in `corpus/fixtures/measure_audio.py`,
  the 3 deletions being exactly the declared wiring lines (mutex-sum,
  mode ternary, suffix ternary).

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 00:40:23→00:40:25 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6…`** (canonical pin) |
| r84v1 | 00:40:28→00:45:16 | `… --probe-alsapw-r84` | 1 | 3 (§5-F1/F2) | `5549dff6d127e0cc01ad5d999cc681910819c99e37f3c4c31a49b878db11f6d3` |
| r84v2 | 00:45:41→00:50:21 | `… --probe-alsapw-r84` | 0 | `{}` | `fe03f4ef9e5b08247e196c6ddbf3d5b66e3433bd73775463bfe942f233db6029` |

- Leg census per probe run: **147 legs / 6 entries** — exact match to the
  author's declared count (entry split 38/22/14/24/16/33).
- `TMPDIR=/home/vgpnk/Projects/shokunin/tmp` for every run and spot
  (`/tmp` at 76 % quota).
- r84v1's three failures were `a_plughw00` (rc=0 + a **foreign** node in
  `new_node_names`), `st_hw00_c1` (EBUSY instead of the channel-count
  refusal) and `pw_server` (SIGKILL at the 8 s bound). All three are
  contention artifacts — §5-F1/F2.
- Contention census (in-receipt): r84v1 saw `fixture_runs: 1` and a
  foreign `aplay`/`parec` in 3 entries; r84v2 saw `fixture_runs: 1–2`
  (queued sibling run) but no foreign stream in any leg window.

## 3. Verdict-surface stability (`runs/surface-diff*.txt`, `runs/surface.py`)

Tiered comparator (r83 convention): **exact** = rc/signal/error_class/
error_hit/killed_at_bound/unknown_pcm_name/stderr/stdout/arm/out.exists+
rate/riff/unsupported/stream-leaf mute + semantic props/suspend rows/
tap_exit/player_exit/sig.exists — all pid/index/path/seat-normalized;
**named** = `ratio` bucket, `respawn_tap_med`, `volume_value`,
`volume_percent`, sig window-set; **analog** = timing/amps/series/pids/
indices/leaf volume/cork/node state (never exact-diffed).

Calibration: **author run1 vs run2 = 0 exact / 0 named** — the
comparator pins exactly the surface the author's own two green runs
agree on (no over- or under-pinning).

- **r84v2 vs author run1: 0 exact / 0 named.**
- **r84v2 vs author run2: 0 exact / 0 named.**
- r84v2 vs r84v1: 13 exact / 0 named — the contaminated legs
  (`a_hw03`, `a_plughw00`, `ebusy_hold`, `st_hw00_c1`, `env_node`,
  `env_props`, `pw_ch2`, `pw_period`, `pw_rate44`, `pw_role`,
  `pw_server`, `r_pw_node_src_1`, `st_pw_c6`).
- Author receipt identity: `corpus/live/r84-author/runs/run1` == canon
  `20261016T003253840363Z` (`e8d463c2…`) and `run2` ==
  `20261016T003756373122Z` (`283f69e8…`) — byte-identical, so the
  report's two-run claim and its citations are exact (no r83-F1-class
  citation drift).

## 4. Spot re-derivations — 17 shapes / 20 records (`spot/spots.jsonl`, `spot/spots.py`)

Independent protocol (own `r84v_*` sinks, own tone/tap/analysis code —
no fixture import), own `r84vrole<pid>` restore key, own TMPDIR.

| spot | pinned shape | measured (reps) |
| --- | --- | --- |
| s1 | `set-sink-volume <ns> 50%` → tap ×0.125 | 8192→**1024**, ratio **0.125** |
| s2 | `set-sink-volume <ns> 150%` → ×3.375 | 8192→**27648**, ratio **3.375** |
| s3 | `set-sink-volume <sink idx> 25%` → ×0.015625 | 8192→**128**, ratio **0.015625** |
| s4 | `set-source-volume <ns>.monitor 50%` → ×0.125 | 8192→**1024**, ratio **0.125** |
| s5 | sticky: 30 % write → same-tag respawn 30 %, tap 221 | spawn1 100 → after30 30 → respawn **30 %**, tap med **221.0** (exactly 8192·0.3³), repair→**100 %** |
| s5 | name-scoped refinement | different-tag respawn **100 %** |
| s6 | `--monitor-stream 0` / `999999` | rc=1 `Stream error: No such entity`, **44 B** file, 0 data bytes (×2 reps) |
| s6 | source-output index accepted | no error class, **44 B** header-only, still alive at 4 s (and 6 s past donor end) |
| s7 | pre-route leaf | `sink=4294967295`, volume block all-zero, read **0 %** |
| s7b | pre-route write → restore key | **not** swallowed: routed leaf 25 %, same-tag respawn **25 %**; post-route control respawn 25 % → **sub-claim falsified, F3** |
| s8 | donor must be parec | `pw-record --target <sink>` and `--target <ns>.monitor` both rc=1 `no target node available`; `parec -d <ns>.monitor` registers a source-output with `application.process.id` == pid |
| s9 | per-leg pre-reset (persistent object state) | leftover 25 % sink **+** 50 % monitor source → cascade base **16** = 8192·0.25³·0.5³; after pre-reset **8192** |
| s10 | `-D ''` argv-eating | `aplay -D ''` → `Unknown PCM ` (empty); `aplay -D -d 1` → `Unknown PCM -d`; `arecord -D ''` → `Unknown PCM ` — both rc=1 |
| s11 | single capture-refusal class | `arecord -D pipewire` and `-D default` → rc=1, no file, **both** `Unable to install hw params:` **and** `TICK_TIME: [0 0]` |
| s11b | one-sided NODE= law | `NODE=<hw Line source>` revives rc=0 (352 844 B real wav); `NODE=<ns>.monitor` refuses in the same single class |
| s12 | `PERIOD_BYTES=4096` → `node.latency` | **`1024/48000`**; `NODE=no_such` → landed on the **default sink** (silent fallback) |
| s12b | `RATE=44100` playback | rc=0 + `Warning: rate is not accurate (requested = 48000Hz, got = 44100Hz)` |
| s13 | `SERVER=bogus` isolation | rc=1 `audio open error: Host is down` in **0.005/0.006 s** (×2) — run1's 8 s hang was contention, not the isolated law |
| s14 | `arecord -D null` content | rc=0, 44 100 frames, **nz_rows 668**, 25 bursts, peak 32 655 — nonzero content confirmed; 5512 spacing not an invariant (matches the boundary correction) |

Honest disclosures: the first `s3` rep used the *stream* index (rc=1
`No such entity`, ratio 1.0) — retained in the JSONL and re-run with the
sink index; the first `s12b` rep used the 14 s spot tone and was killed
at its 15 s bound while still playing — protocol artifact, re-run with a
1.4 s tone. Both are visible in `spots.jsonl`/`spots*.out.txt`.

## 5. Findings (ranked)

- **F1 (non-blocking, wave-B hygiene) — the same-family lock is
  TMPDIR-scoped, so concurrent r84 runs do not serialize.**
  `_alsapw_r84_family_lock` locks
  `Path(tempfile.gettempdir())/"measure_audio-alsapw-r84.lock"`, so two
  r84 runs with different `TMPDIR`s run concurrently (the r84-critic
  replay #1 used `TMPDIR=…/r84critic-tmp` while this seat used
  `…/tmp`). Bidirectional cross-credit is
  recorded: **my** r84v1 receipt captured the critic's seat objects
  (`pw_role` → `['r84a_1685102_hold']`, `pw_period` →
  `['alsa_playback.aplay','r84a_ns_1685102']`, `env_props` →
  `['r84a_1685102_envp']`, `a_plughw00` → `['alsa_playback.aplay']`),
  and the **critic's** receipt captured mine (`a_front` →
  `['r84a_1682245_hold']`, `a_iec958_d0` →
  `['alsa_playback.aplay','r84a_ns_1682245']`, `env_node` →
  `['r84a_1682245_envp']`). The `new_node_names`/`nodes_mid` witness is
  not seat-scoped (generic `alsa_playback.aplay` names), so the
  "adaptive" aplay arms can redden a green landing purely from a
  neighbour's node creation. Not a defect in the encoded laws — the
  laws themselves reproduced 0/0 — but the "same-family exclusion"
  claim holds only when seats share `TMPDIR`.
- **F2 (non-blocking, latent) — two arms are contention-fragile.**
  `st_hw00_c1` requires hw:0,0 to be free (a concurrent holder yields
  EBUSY, rc=1 with **no** error class → red); `pw_server` was killed at
  its 8 s bound once under load while the isolated shape returns in
  5 ms (s13 ×2). Both reproduced green in r84v2 and match the author's
  surface. Suggest an adaptive guard (EBUSY-tolerant `st_hw00_c1`;
  a longer/soft bound or a retry on `pw_server`).
- **F3 (minor, docstring claim not reproduced) — the pre-route write is
  not swallowed.** `_alsapw_r84_wait_attached`'s docstring claims the
  pre-route leaf "swallows a `set-sink-input-volume` write without
  registering it into the stream-restore key". Two independent reps
  contradict the second half: s7 fired 25 % inside the pre-route window
  and the routed leaf read 25 %; s7b repeated it and the same-tag
  respawn came back **25 %** (post-route control also 25 %). The
  **read** half is exactly reproduced (s7: `sink=0xFFFFFFFF`, all-zero
  volume, bogus 0 %). Recommend narrowing the docstring to the read
  side; the encoded laws and receipts are unaffected (no r84 leg
  asserts the swallow).
- **F4 (minor, honest nuance) — the SO-pinned parec's exit is
  protocol-dependent.** The author's `mon_soidx` recorded rc=0 at 4.5 s;
  my spot's SO-pinned parec was still alive at 4 s and stayed alive 6 s
  after the donor source-output ended (44 B header-only, no error
  class). The fixture's assertion accepts rc ∈ {0,−15} + no class +
  ≤200 B, so both are green — but "exits rc=0" should not be read as a
  law.
- **F5 (positive, report hygiene) — no citation drift this round.**
  The report's two cited receipts are byte-identical to the canon
  (`e8d463c2…` / `283f69e8…`), `+2796/−3` matches, the 3 deletions are
  the declared wiring lines, `sinks_gone` all true and `own_nodes_after`
  empty in both author runs, and the disclosed foreign
  `r84a_probe_548706` sink is still present, SUSPENDED, untouched.

## 6. Contention ledger

Foreign seats live in-window, observed read-only, never touched:

| foreign object / process | what it was doing |
| --- | --- |
| r84-critic replay #1 (pid 1685102, cwd `~/tmp/r84critic-src`, TMPDIR `~/tmp/r84critic-tmp`) 00:41:40–00:45:17Z | its own `--probe-alsapw-r84` replay, fully overlapping my r84v1; its receipt records my nodes, mine records its |
| r84-critic replay #2 (pid 1740760, same cwd, TMPDIR `~/tmp`) 00:46:41–~00:51:2xZ | second replay; held the shared family lock during my spot battery; its `r84a_ns_1740760` sink + `pw-play` stream are live in my post-state |
| queued r84 replay (pids 1743075/1743076) | waiting on the lock during my window (counted as `fixture_runs` in r84v2 entry heads) |
| r84-reviewer replay (00:45:39Z) | died immediately (`build_artifacts.py` exit 2 in their frozen tree) — did not contend |
| g3d r96-author `run_battery.py` | ambient CPU load (loadavg ~50–56) |
| foreign sink `r84a_probe_548706` (SUSPENDED) + `~/tmp/r84n.wav` | disclosed by the author; observed untouched at pre- and post-state |
| `r84a_1682245_hold` / `r84a_1685102_hold` etc. | transient probe nodes from the two concurrent r84 runs (the cross-credit evidence itself) |

Interference caused by this seat (all disclosed, bounded): 2 probe runs
+ 1 normal run from the frozen tree; 16 spots using 2 probe-owned null
sinks per spot process (all unloaded name-verified, `gone: true`);
s12's `NODE=` miss landed ~1 s on the shared default sink (the same
measured silent-fallback shape the fixture records); no tone ever
targeted a foreign sink; default sink/source unchanged at pre- and
post-state.

## 7. Evidence map (`corpus/live/r84-verifier/`)

`toolchain.txt`, `pre-state.txt`, `post-state.txt`,
`runs/commands.log`, `runs/{normal,r84v1,r84v2}.stdout.json`
(+`.stderr.log`, all 0 B), `runs/{normal,r84v1,r84v2}.receipt.json`
(byte-copies of the frozen-tree receipts), `runs/receipt-shas.txt`,
`runs/tree-tar-sha.txt`, `runs/ls-tree-fbe65713.txt`,
`runs/tree-files.txt`, `runs/surface.py` (tiered comparator),
`runs/surface-diff-v2-vs-author.txt`, `runs/surface-diff-v2-v1.txt`,
`runs/surface-diff-v1-vs-author.txt`, `runs/author-r1-r2.diff.txt`,
`spot/spots.py`, `spot/spots.jsonl` (28 records: 4 setups, 20 spots,
4 teardowns), `spot/spots{,2,3}.out.txt`, `spot/spots.window.txt`,
`manifest.json` (34 files / 6 129 918 B), `tree/` (gitignored archive
materialization holding the receipts as written by the fixture).

## 8. Risks / blockers

- **None blocking.** The landing verifies on the frozen tree; the red
  replay is explained and reproduced green.
- Carries for the wave-B fold: F1 (lock scope / non-seat-scoped node
  witness), F2 (two non-adaptive arms), F3 (docstring sub-claim), F4
  (SO-pin exit wording). None changes any encoded law or receipt value.
- Disclosed leftovers by this seat: private, pid-scoped restore keys
  `r84vrole<pid>` (one of them at 25 % from s7b) are inert — no other
  seat can carry that role; spot scratch dirs were removed; the frozen
  tree (`tree/`, 1.6 GB, gitignored) is left as regenerable receipt
  material for the orchestrator to keep or prune.
