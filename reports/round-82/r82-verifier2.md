# r82 VERIFIER2 — verification of the FOLDED family on `d6167399` (frozen tree)

Seat: verifier2 (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`). Lane
`~/Projects/shokunin/audio-shokunin`. Window **2026-10-15 22:34–22:44Z**.
Verification target: commit **`d6167399`** ("r82 fold: 8-item queue applied
+198/-77 — simplifier -25, tone re-key pid-class, rc8 armed, a2
Speaker+gate, t2 zeros gate, exact-name unload; 77 legs x2 green"), frozen
via `git archive` — **not** the worktree. Toolchain receipt-identical to
the author/fold pin: ffmpeg/ffprobe/ffplay **n9.0.1** (`--enable-libpulse`),
PipeWire **1.6.8**, `PulseAudio (on PipeWire 1.6.8)` protocol 35, Python
3.14.7 (`corpus/live/r82-verify2/toolchain.txt`). **No tracked writes, no
commits, no pushes, no `pactl set-default-*`, no manual PipeWire objects**
(spot s3 exercised only the fixture's own load/unload helpers against
seat-owned `r82w_ctl_*` names, all removed at exit). Namespace `r82w_*` /
`r82-verify2` for all seat artifacts; scratch `/tmp/r82w-spot/` holds only
spot outputs.

## 0. Verdict

**VERIFIED.** Every assigned check passed on the frozen `d6167399` tree:

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive d6167399` | tar `4e7abefe…`, 43 494 files, symdiff vs `git ls-tree -r d6167399` = **0** | PASS |
| fixture identity | fold-recorded `7984409c…` | tree sha256 `7984409ceb9ca7c35b18b9b28f2add445701c044d71f8ee4ddc6f35d31217ef7` before/after **every** run | PASS |
| py_compile | clean | rc=0 | PASS |
| `--probe-ffmpeg-r82` ×3 (≥2 required) | failures `{}` | w1 `20261015T223652127290Z`, w2 `20261015T223926046605Z`, w3 `20261015T224303995684Z` — all rc=0 `{"failures": {}}` | PASS |
| 8 entries / 77 legs ×3 | all legs | **8 probe entries, legs 8/17/13/14/8/6/8/3 = 77** per run; 25 measurements; every leg carries an exec rc (77/77, 0 skipped) | PASS |
| `normal` receipt vs canonical | `8e8cdad6…` | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — **byte-identical** | PASS |
| run↔run verdict surface | stable | **0 diffs** over 77 legs (rc, error_class, error_hit, killed, out fmt pins) across w1/w2/w3 | PASS |
| teardown | zero seat objects | post-state: **0** `r82w_*`/`r82ff_*`/`r82v*` objects, **0** leftover probe processes of mine | PASS |
| fold-item spot checks | all items live | 5/5 folded-cell groups verified live + 3 independent re-derivations + labrat 6/6 clauses | PASS |

## 1. Frozen tree

- `git archive d6167399 -o /tmp/r82v2-tree.tar` → tar sha256
  `4e7abefe776b3c47083c61b2a7469bed2a163c92342e38a5ab57734add7e59b0`,
  55 125 members; extracted to `corpus/live/r82-verify2/tree/`
  (gitignored regenerable-snapshot path): 43 494 files / 0 symlinks.
- File-set symmetric difference vs `git ls-tree -r d6167399 --name-only`
  = **0 lines** (43 494 both sides).
- Fixture inside tree: sha256 `7984409ceb9ca7c35b18b9b28f2add445701c044d
  71f8ee4ddc6f35d31217ef7` — the fold's recorded post-edit sha exactly;
  git blob `d7951af66d03cdd034c7075316209069fd0c3ff3`.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 22:34:16→22:34:17 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`** |
| r82w1 | 22:34:17→22:36:52 | `… --probe-ffmpeg-r82` | 0 | `{}` | `5eafe45b75d39b8b3a7afb551b47dcda05d1340825debb4456d9aeb6c8586cde` |
| r82w2 | 22:36:52→22:39:26 | `… --probe-ffmpeg-r82` | 0 | `{}` | `024b29b88fbc92b8949c5de9d3209758ec79c021441e91e88d0443f752d63c83` |
| r82w3 | ~22:40:12→22:43:04 | `… --probe-ffmpeg-r82` | 0 | `{}` | `678ea35fb5ec2b8c5bcdd200247a09bcda399b5fb786b04f492cb1154dbbd8a5` |

- **`normal` byte-identity**: `8e8cdad6…` reproduced — canonical pin holds
  on the folded bytes too (author a/b + baseline a/b + r82-verifier +
  verifier2).
- Census per probe run: **25 entries / 77 legs** (17 base 0-leg entries +
  `ffpw_device_surfaces` 8, `ffpw_capture_lattice` 17,
  `ffpw_playback_lattice` 13, `ffpw_buffer_knobs` 14, `ffpw_target_loss` 8,
  `ffpw_error_classes` 6, `ffpw_alsa_split` **8** (the armed a7), `ffpw_ffplay_ffprobe` 3) — matches the fold's declared 77.
- stderr logs 0 B on all four runs. `host_is_quiet: true` on all 8 probe
  entries in all 3 runs.
- A **third** probe run was needed: w1 (pid 417268) and w2 (pid 454408)
  both landed on pid-class 0 (417268%4=0, 454408%4=0); w3 (pid 511699,
  class 3) supplied the second required class.
- Fixture sha256 `7984409c…` before **and** after all 4 runs.
- Ambient: loadavg ~52–77; `/tmp` tmpfs 70–80 % full (the fold's red-flake
  environment — did **not** recur); foreign sibling `r84a_probe_548706`
  null sink present at post-state (named, untouched; its module index
  536870923 is the same recycled id our `r82ff_ns_*` modules held — the
  exact LIFO-recycling case the name-verified unload exists for).

## 3. Verdict-surface stability

`runs/surface-diff.txt` — per-leg `{rc|exit_code, error_class, error_hit,
killed, out.{rate,ch,fmt,riff}}` over all 77 legs:

- w1 vs w2 vs w3: **0 diffs**, key symdiff 0.

## 4. Fold-item spot checks — live (`spot/`)

| fold item | live evidence | verdict |
| --- | --- | --- |
| **pid-class tone pairs — two different classes** | w1 pid 417268 → class 0 → 2900/3460; w2 pid 454408 → class 0 → same pair; w3 pid 511699 → class **3** → 4100/4660 (family lockfile `/tmp/measure_audio-ffmpeg-r82.lock` records `pid=511699 ns=r82ff_ns_511699 tone=4100.0/4660.0`). Spot **s1** re-implemented `_ffpw_r82_write_tone` byte-exactly for the three run pids: FFT peaks land exactly on the formula pairs (`2900.0/3460.0`, `4100.0/4660.0`), amps ≫ floor; full disjointness table — all 4 r82 classes ≥400 Hz clear of every r78 class (997+211j/+503) and every sibling r82 class, **0 collisions** both directions. Import-time band guard fired cleanly on every process incl. the s3 import (pid 554479). | PASS — 2 classes exercised, green |
| **rc=8 `-channels 0` leg** | Receipts 3/3: `a7_ch0_option_absent` `exit_code=8`, `error_class=ff_option_not_found`, stderr `Option channels not found.` + `Error opening input file hw:0,0.` Spot **s2** independent re-derivation of the argv (`ffmpeg -f alsa -channels 0 -i hw:0,0 …`): **rc=8**, identical stderr. Control: same spelling on the pulse indev → **rc=222 ERANGE** (`out of range [1 - 2.14748e+09]`) — the documented indev split. | PASS |
| **a2 Speaker target + `holder_consumers` gate** | Receipts 3/3: `a2_holder_sink = alsa_output.usb-…HiFi__Speaker__sink.29` (the Audio/Sink whose `aplay_device == hw:0,0` = capture dev); `a2_hw_free_pwheld.holder_consumers == […Speaker__sink.29]`; rc=0, `out.riff=finalized`, ~288 kB wav; holder watch argv shows `-f pulse -device …Speaker__sink.29`. `coverage_blocked` absent — the same-subdevice premise was exercised, not vacuous. | PASS |
| **t2 content gate** | 9/9 `t2_cap_r{0,1,2}` legs across the 3 runs: `fired unload_module at≈1.20` and `cap_tone.mine_spans` each contain a span ending **after** unl_at (`[0.1,2.1]`/`[0.1,2.0]` vs unl 1.201–1.208); rc=0, finalized wav, `pump_relinked_to=[SPDIF default]`. | PASS |
| **exact-name unload — negative control** | Spot **s3** live: imported the frozen fixture; loaded `r82w_ctl_a2` **first** (index 536870921, listed first — a substring scan for `sink_name=r82w_ctl_a` hits the foreign line first) then `r82w_ctl_a` (536870926). `_gst_r81_sink_module_index("r82w_ctl_a")` → **536870926** (own), rejecting 536870921; `_gst_r81_unload_own` rc=0, `verified_index==captured`, `recycled:false`; post-unload `pactl` shows `r82w_ctl_a` gone and **foreign `r82w_ctl_a2` SURVIVING** (sink id 220922 listed). Twin then unloaded by its own exact name — post-state zero `r82w_ctl_*`. | PASS — foreign prefix name NOT destroyed |

Receipt-level teardown corroboration (all 3 runs): 8 fired
`unload_module` events `verified_index==captured==536870923,
recycled:false, exit_code=0`; entry-level `unloads.r82ff_ns_<pid>` —
5× identical verified unload, 1× `skipped:not_listed` in target_loss
(the sanctioned already-gone-by-leg-unload case); `sinks_gone` all-true;
`own_nodes_after []` on every sink-owning entry.

## 5. Delegated probe (frozen probeParent — exactly one)

One read-only `ufo-labrat` (agent `a54a89eb`), hypothesis: "all three
receipts internally carry the folded-cell values consistently, clauses
(a) legs/entries/failures, (b) a7 rc8/class/token, (c) a2 holder gate,
(d) t2 post-unlink spans, (e) unload verified==captured, (f) pid→pair
mapping". Result: **PASS 6/6 clauses**, independently recomputed from
the receipts and frozen source (77 legs ×3, 25 `[]` failure lists, 42
clean unload results, pid arithmetic verified). Caveat it noted, agreed:
receipts don't store raw `f_l`/`f_r` — clause (f) verifies as
pid→pair consistency, with `mine` detections as the ±6 % attestation;
spot s1 supplies the independent freq measurement.

## 6. Teardown / tree state

- Post-state (`post-state.txt`, 22:44:26Z): **0 `r82w_*` objects, 0
  `r82ff_*` objects, 0 leftover probe processes of this seat**; default
  sink/source unchanged (`…SPDIF__sink.29` / `…Line__source.29`); the only
  foreign object is sibling `r84a_probe_548706` (named, untouched).
- Worktree `git status`: **zero tracked modifications**; seat footprint is
  untracked `corpus/live/r82-verify2/` (evidence + gitignored `tree/`) and
  this report. Scratch `/tmp/r82w-spot/` holds spot wavs/logs only;
  `/tmp/r82v2-tree.tar` remains as the archive receipt.
- No `pactl set-default-sink`/`set-default-source`; module ops only via
  the fixture's own name-verified helpers against seat-owned names.

## 7. Evidence map (`corpus/live/r82-verify2/`)

`battery.sh`, `analyze.py`, `runs/commands.log`,
`runs/{normal,r82w1,r82w2,r82w3}.stdout.json` (+`.stderr.log`),
`runs/{normal,r82w1,r82w2,r82w3}.receipt.json` (byte-copies of the tree
receipts), `receipt-shas.txt`, `runs/{r82w1,r82w3}.analysis.json`,
`runs/analysis.json`, `runs/surface-diff.txt`,
`spot/s1_tone_rederive.{py,out.json}`, `spot/s2_a7_rederive.sh`,
`spot/s2_a7.log`, `spot/s2_{a7,e2}.{out,err}`, `spot/s3_unload_exact.py`,
`spot/s3_unload_exact.out.json`, `pre-state.txt`, `post-state.txt`,
`toolchain.txt`, `tree/` (gitignored archive materialization; canonical
receipts also under `tree/corpus/live/runs/20261015T{223417918428Z-normal,
223652127290Z-ffmpeg-r82,223926046605Z-ffmpeg-r82,224303995684Z-ffmpeg-r82}/`).

## 8. Risks / blockers

- **None blocking.** `/tmp` ran 70–80 % full through the window (the same
  tmpfs pressure that produced the fold's red flake); no leg hit it —
  stderr logs empty, zero failures.
- w1/w2 both landing on pid-class 0 is coincidence, not a bias signal —
  the band guard covers all four classes at import and w3's class-3 run
  plus the s1 table cover the space.
- Foreign `r84a_probe_548706` shares the recycled module index 536870923
  our runs used — LIFO recycling is live on this host, and the
  name-verified unload behaved exactly as designed against it (s3 +
  receipt teardowns).
- No resume mutation attempted (no `resume_continuity_v1` preflight
  required or run); no commit, no push. The canonical Rust runtime
  remains the sole judge.
