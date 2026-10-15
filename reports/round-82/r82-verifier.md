# r82 VERIFIER — non-author verification of `aa03c347` (frozen tree)

Seat: verifier (non-author). Host `plazir27` (`Linux 7.2.3-arch1-3`). Lane
`~/Projects/shokunin/audio-shokunin`. Window **2026-10-15 20:21–20:29Z**.
Verification target: commit **`aa03c347`** ("r82 author: ffmpeg/ffprobe/ffplay
<->PipeWire family — +2170, 8 entries 76 legs, 304 leg-execs green x4,
boundary corrections encoded"), frozen via `git archive` — **not** the
worktree. Toolchain receipt-identical to the author's pin: ffmpeg/ffprobe/
ffplay **n9.0.1** (`--enable-libpulse`), PipeWire **1.6.8**,
`PulseAudio (on PipeWire 1.6.8)` protocol 35, Python 3.14.7
(`corpus/live/r82-verify/toolchain.txt`). **No tracked writes, no commits,
no pushes, no `pactl set-default-*`, no manual PipeWire objects.** Namespace
`r82v_*` for all seat artifacts; scratch `/tmp/r82v-work/` removed at exit.

## 0. Verdict

**VERIFIED.** Every assigned check passed on a frozen `git archive
aa03c347` tree under ambient load (loadavg 96–114, sibling lanes live):

| check | required | measured | verdict |
| --- | --- | --- | --- |
| frozen tree integrity | `git archive aa03c347` | tar `f70c7aa5…`, 32 404 files, symdiff vs `git ls-tree -r aa03c347` = **0** | PASS |
| fixture identity | landed sha `eb865760…` | tree sha256 `eb86576063b359b8bd69d5147b03e443e73990052e76f9221a552cd0864d20b4` before/after **every** run | PASS |
| py_compile | clean | rc=0 | PASS |
| `--probe-ffmpeg-r82` ×2 under load | failures `{}` | run1 `20261015T202453785062Z` + run2 `20261015T202737547331Z`, both rc=0 `{"failures": {}}` | PASS |
| 76 legs ×2 executed green | all legs | 76/76 legs each run (8+17+13+14+8+6+7+3), 25 entries; 52 rc=0 + 24 pinned-refusal rc, **0 skipped** | PASS |
| `normal` receipt sha | `8e8cdad6…` | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` — byte-identical | PASS |
| run1↔run2 verdict surface | stable | **0 diffs** over 76 legs (rc, error_class, error_hit, outcome, verdict, out fmt pins) | PASS |
| verifier↔author `final3` | stable | **0 diffs** over the same 76-leg surface | PASS |
| teardown | zero `r82v_*` | post-state: **0** `r82v_*` objects, **0** `r82ff_*` objects, **0** leftover processes of mine | PASS |
| spot re-derivations | ≥5 | **8/8 reproduced** (incl. all 3 named: rc=187 empty device, `.monitor` fallback, ALSA nearest-supported) | PASS |

## 1. Frozen tree

- `git archive aa03c347 -o /tmp/r82v-work/r82v-tree.tar` → tar sha256
  `f70c7aa56d5cba655cb9af2acf2f26c6b56b7c2e7304f71d6e4c5ec224bc81c5`,
  41 961 members; extracted to `corpus/live/r82-verify/tree/` (gitignored
  regenerable-snapshot path per `corpus/.gitignore`): 32 404 files / 9 558
  dirs / 0 symlinks.
- File-set symmetric difference vs `git ls-tree -r aa03c347 --name-only`
  = **0 lines**.
- Fixture inside tree: sha256 `eb86576063b359b8bd69d5147b03e443e73990052e
  76f9221a552cd0864d20b4`, git blob `5d980a3b16f36fee668540afe038bfa9117e8c7c`
  — the author's recorded final sha exactly.
- **HEAD moved mid-window** `aa03c347 → 0556d5d` (sibling r90-boundary
  commit 20:21:41Z, does not touch `corpus/fixtures/`; blob
  `5d980a3b…` at both commits). Frozen tree unaffected — the archive pinned
  the sha, not HEAD.

## 2. Battery — CWD = frozen tree root (`runs/commands.log`)

| run | window (UTC) | cmd | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- | --- |
| normal | 20:22:01→20:22:06 | `python3 corpus/fixtures/measure_audio.py` | 0 | `{}` | **`8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`** |
| r82v1 | 20:22:06→20:24:53 | `… --probe-ffmpeg-r82` | 0 | `{}` | `5334fab2c4ba4c2e1a5ff91438f9248bf58ba457d329893c86dd16eb02361e51` |
| r82v2 | 20:24:53→20:27:37 | `… --probe-ffmpeg-r82` | 0 | `{}` | `a1786f94a124b48d49d818af693f4e7a338481ba7b13ccaf943a9073b62a27ec` |

- **`normal` byte-identity**: `8e8cdad6…` reproduced — now author a/b +
  baseline a/b + canonical + verifier = another independent pin.
- Census per probe run: **25 entries / 76 legs** (17 base 0-leg entries +
  `ffpw_device_surfaces` 8, `ffpw_capture_lattice` 17, `ffpw_playback_lattice`
  13, `ffpw_buffer_knobs` 14, `ffpw_target_loss` 8, `ffpw_error_classes` 6,
  `ffpw_alsa_split` 7, `ffpw_ffplay_ffprobe` 3) — exact match to the author.
- Every leg carries an exec rc: **76/76 executed, 0 skipped** per run; the 24
  nonzero-rc legs per run are the armed refusal cells (234/251/253/187/222/
  SIGABRT classes), each inside `failures {}`.
- Ambient load throughout: loadavg ~96–114; sibling `r96s_ns` sink at
  pre-state, sibling `r83a_dev_*` pw-loopback/pw-record legs live at
  post-state — foreign, named, untouched. `host_is_quiet: false` in 6/8 and
  5/8 loaded entries (run1/run2) — the family still went fully green.
- Fixture sha256 `eb865760…` before **and** after all 3 runs
  (`runs/commands.log`).

## 3. Verdict-surface stability

`runs/surface-diff.txt`, `runs/surface-diff-vs-author.txt` — per-leg
`{exit_code, rc, error_class, error_hit, outcome, verdict, star_vs_pactl,
out.{rate,ch,fmt,riff,exists}}` over all 76 legs:

- r82v1 vs r82v2: **0 diffs** (key symdiff 0).
- r82v1 vs author `final3.measurements.json`: **0 diffs** (key symdiff 0).

## 4. Spot re-derivations — 8/8 reproduced (`spot/`)

Independent re-executions of the pinned argv shapes (own `r82v_` names,
scratch `/tmp/r82v-work/`, logs `spot/s*.{out,err}`):

| spot | leg shape | pinned | measured |
| --- | --- | --- | --- |
| s1_d1 | `ffmpeg -f pipewire -i x` | rc=234 `ff_unknown_format` | **rc=234**, `Unknown input format: 'pipewire'` |
| s2_p12 | outdev `-device ""` | rc=187 `ff_pulse_sink_info` | **rc=187**, `pa_context_get_sink_info_by_name failed` + `Updating sink info failed` |
| s3_c13 | indev `-i r82v_nosuch_<pid>.monitor` | rc=0 permissive hole | **rc=0**; mid-run pw-dump (`s3_c13.pwdump.json`): `target.object=r82v_nosuch_741892` literal **`.monitor` stripped**, `stream.capture.sink=True`, `client.api=pipewire-pulse`, `fragsize=9600`, links ACTIVE from `…SPDIF__sink` monitor (default-sink fallback) |
| s4_a6 | `-f alsa -sample_rate 12345 -i hw:0,0` | nearest-supported clamp | **rc=0**, wav **rate=44100** (2ch/16-bit, 66 107 frames) — 12345 silently clamped |
| s5_e1 | indev `-sample_rate 0` | rc=222 `ff_option_range` | **rc=222**, `out of range [1 - 2.14748e+09]` |
| s6_c11 | indev `-server unix:/nonexistent-r82v` | rc=253 `ff_no_such_process` | **rc=253**, `No such process` |
| s7_p9 | outdev `-server unix:/nonexistent-r82v` | rc=187 `ff_access_denied` | **rc=187**, `Cannot connect context: Access denied` |
| s8_a3 | `-f alsa -i pipewire` | rc=251 `ff_alsa_params` | **rc=251**, `cannot set parameters (No such file or directory)` |

Cross-checked inside the verifier's own run1 receipt (not just fresh legs):
`p12` rc=187/`ff_pulse_sink_info`; `c13` rc=0 + `target.object=
no_such_thing_4076806` + producers=`[SPDIF]`; `a6` out rate=44100; `c14`
`node.rate=1/12345` + wav 12345 (no pulse clamp); `b1` tlength=16384/
prebuf=12548/minreq=3840/`node.latency=2176/48000`; `d4` `star_vs_pactl=
agree`; `t1` rc=0. **All match the author report §2 verbatim.**

## 5. Teardown / tree state

- In-receipt custody (both runs): every sink-owning entry reports
  `sinks_gone: {r82ff_ns_<pid>: true}` and `own_nodes_after: []`.
- Post-state (`post-state.txt`, 20:28:49Z): pactl + pw-dump census —
  **0 `r82v_*` objects, 0 `r82ff_*` objects, 0 leftover probe processes
  of this seat**; default sink/source unchanged (`…SPDIF__sink` /
  `…Line__source`); the only live foreign objects are a sibling
  `r83a_dev_*` lane (named, untouched).
- Worktree: `git status` shows **zero tracked modifications**; my only
  footprint is untracked `corpus/live/r82-verify/` (evidence +
  gitignored `tree/`) + this report. `/tmp/r82v-work/` deleted.
- No `pactl set-default-sink`/`set-default-source`, no `load-module`/
  `unload-module` issued by this seat (spot legs create transient stream
  nodes only, dead with each process).

## 6. Contention ledger

- Siblings live in-window: `r96s_ns` null sink (pre-state, gone by
  post-state), `r83a_dev_*` pw-loopback/pw-record lane (post-state),
  sibling commit `0556d5d` (r90-boundary) mid-window. None touched by me;
  none reached the verdict surface (0-drift both directions).
- `normal` stderr empty; both probe stderr logs 0 B.

## 7. Evidence map (`corpus/live/r82-verify/`)

`battery.sh`, `runs/commands.log`, `runs/{normal,r82v1,r82v2}.stdout.json`
(+`.stderr.log`), `runs/*.receipt.json` (byte-copies of the tree receipts),
`receipt-shas.txt`, `runs/surface-diff{,-vs-author}.txt`,
`spot/s*.{out,err}` + `s3_c13.pwdump.json`, `pre-state.txt`,
`post-state.txt`, `toolchain.txt`, `tree/` (gitignored archive
materialization; canonical receipts also under
`tree/corpus/live/runs/20261015T{202206899892Z-normal,202453785062Z-ffmpeg-r82,
202737547331Z-ffmpeg-r82}/`).

## 8. Risks / blockers

- None blocking. Honest carries: `c3`/`a5` envelopes armed but only the
  `eio_251`/`params_251` arms realized here too (consistent with author,
  boundary, and current host state); `-sinks pulse` `*` provenance remains
  mechanism-unverified (`agree` observed); ambient load was extreme
  (~100) yet zero timing-armed legs regressed.
