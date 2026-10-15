# r81 VERIFIER — independent re-execution of the author's claims

host: devin (`Linux plazir27 7.2.3-arch1-3`), seat: verifier (r81), window
2026-10-15T17:45–18:13Z. Work commit `6aa03e6`, author report
`reports/round-81/r81-author.md`. All invocations were `timeout`-bounded
(600 s for the gst family, 900 s for battery modes) and all resources were
the fixture's own pid-derived names (`gst_r81_auth_<pid>` /
`gst_r81_<pid>_*`); my runs used pids 2758068, 2769892, 2800787, 3325580 —
disjoint from the author's (1628328). The fixture exposes **no name-prefix
env/flag**; uniqueness is by `os.getpid()` per process, which is
seat-owned by construction. Receipts custody:
`corpus/live/r81-verifier/` (+ the fixture's own writes under
`corpus/live/runs/`).

Toolchain re-verified on the live host: `gst-launch-1.0`/`gst-inspect-1.0`
`/usr/bin/`, PipeWire 1.6.8 (`Server Name: PulseAudio (on PipeWire 1.6.8)`,
protocol 35), default sink
`alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink` — matches the
author's stated environment.

## Per-claim results

### Claim — tracked diff shape (+1 686/−3, one file, sha `0dad37ee…`): PASS

`git diff 6aa03e6^ 6aa03e6 --numstat` → `1686  3  corpus/fixtures/measure_audio.py`,
single file. `sha256sum` =
`0dad37ee6500ca3d547d6b9654ad526249ae3d80215fcca3614703429b95fe56` —
matches the author's pinned sha exactly. The three minus-lines are the
wiring ternaries (spot-checked in the diff).

### Claim — `python3 -m py_compile corpus/fixtures/measure_audio.py` passes: PASS

rc 0 (17:45Z). Side note: the `__pycache__/*.pyc` is tracked, so py_compile
dirtied it exactly as the author described; restored with
`git checkout -- corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
after the runs — tracked tree is clean at report time (`git status
--porcelain` shows zero modified tracked files).

### Claim — `--probe-gst-r81` runs green, failures `{}`: PASS (2/2 runs)

- run 1: `timeout 600 python3 corpus/fixtures/measure_audio.py --probe-gst-r81`
  → exit 0, `{"receipt": "…/20261015T174710518675Z-gst-r81/measurements.json",
  "failures": {}}`, stderr 0 B. Custody:
  `corpus/live/r81-verifier/gst-r81.run1.measurements.json`
  (sha `363a38f52c9563c0dbf7781771d0024f3488a24421d05dc5db64e0770f5148ed`).
- run 2 (same cmd): exit 0, `failures: {}`, receipt
  `20261015T181232551735Z-gst-r81`, custody `gst-r81.run2.measurements.json`
  (sha `ad643a10515502f83f9730a66094cbf50b28a29ede4dc23319541a57a38ce4a9`).
- Census of run 1 (baseline `rows.py`): 24 measurement entries —
  the 17 normal-corpus rows + the 7 new probe entries; the probe entries
  carry **15/5/12/6/7/7/3 = 55 legs**, matching the declared table.
  6 835 leaf paths — identical leaf-space size to the author's pair.
- Run-to-run stability (baseline `percase.py`, pid-normalized;
  `corpus/live/r81-verifier/stability-gst-r81-run1-vs-run2.txt`):
  5 550 exact / 710 volatile / 574 jitter / **1 semantic** over 6 835 —
  the single semantic leaf is `a1_autoaudiosrc/stderr` (the repeated-ERROR
  list ordering), same class as the author's 0-semantic pair. Normalized-key
  collisions: 0.
- Wall clock: ~83 s per run on the quiet host (author wrote "~3 min";
  load-dependent, not a discrepancy).

### The seven pinned claims re-measured (my receipts, verbatim)

- **(1) lattice**: every leg `stable:true`, both reps match expect —
  `pipewiresink`/`pipewiresrc` klass `Sink|Source/Audio/Video` on
  `libgstpipewire.so` **1.6.8**; the 1.28.6 rows, `wavenc`
  `Codec/Muxer/Audio` (the author's fuller-klass correction holds);
  `openalsink` and the `nosuchelement_r81_xyz` control both **rc 255**;
  plugin `pipewire` version 1.6.8. PASS.
- **(2) naming crossover**: `client-name=` moved all three node strings
  (`node.name`, `node.description`, `media.name` =
  `gst_r81_2758068_client`) while the Client kept
  `application_name='gst-launch-1.0'`; `client-properties application.name=`
  moved only the Client (`gst_r81_2758068_app`); `client.name` is `null`
  on every leg (author's correction #3 confirmed). PASS.
- **(3) routing**: r1 two-key write (`node.target` + `target.object` =
  `<ns>`); r2/r3 single-key stream-properties both route; r4 bogus
  verbatim on both keys + silent re-link to the SPDIF default, exit 0;
  r5 element prop beats stream-properties; r6 `PIPEWIRE_PROPS` renamed
  node `gst_r81_2758068_env` + `node.target=<ns>`; r7 `PIPEWIRE_NODE`
  landed as `target.object`; r8 `node.autoconnect` = **STRING `"FALSE"`**,
  unlinked, killed at wallcap (−9); c0 refused 255
  `gst_target_not_found` + 0-byte artifact; c1 capture prop `"TRUE"`,
  `<ns>` monitor producer; c4 `<ns>.monitor` landed the **default** sink's
  monitor (r77 residual confirmed on a non-default target); c7 prop-only
  routed. PASS.
- **(4) pulse axis**: p1→`<ns>`; p2 bogus verbatim in `target.object` +
  **rc 0 silent fallback** to default; p3 `PULSE_SINK` honored; p4
  `device=` wins over env; p5 rc 255 `Connection refused`; p6 `pulsesrc`
  rc 1 `No such entity` + 0-byte artifact; all pulse nodes carry
  `client.api=pipewire-pulse`. PASS.
- **(5) target loss**: unload fired ~+1.2 s in every leg, all
  `verified_index == captured`, `recycled:false`, rc 0. t1/t2 playback
  re-linked → SPDIF default within one 0.2 s sample (empty-link sample at
  the boundary), alive at wallcap, stderr empty. t3/t4/t5/t6 capture:
  producers `[]` for every post-unload sample, artifact **frozen at
  204 844 B**, `riff_size=2147418148`=`0x7FFF0024`,
  `data_declared=2147418112`=`0x7FFF0000` — the corrected hex constants
  confirmed verbatim (the scout's `0x7FFFF000` misquote is again
  falsified). t7 `pw-record` control re-linked → default monitor at +0.2 s
  and kept growing (237 612→847 916 B). Direction-split law holds. PASS.
- **(6) exit classes**: e1/e3/e8/e9 rc 1 parse refusal, **no artifact**;
  e10 rc 255 + 0-byte artifact; p8 rc 255 `Connection refused`; e11
  `pulsesrc` the rc 1 + 0-byte outlier.
  `class_summary = {"parse_rc1_no_artifact": true,
  "runtime_refusal_zero_byte": true}`. PASS.
- **(7) autodetect**: a0 → a `client.api=pipewire-pulse` node
  (`media.name="audiotest wave"`) linked to the default sink ⇒
  autoaudiosink resolves to `pulsesink`; a1 rc 1 `No such entity`
  (r77's missing-default inherited); a2 `alsasink device=null` publishes
  **no** pw node. PASS.
- Teardown witnesses in my receipts: `sinks_gone` true on all loaded
  entries, `own_nodes_after` `[]` everywhere; the target-loss entry's
  post-leg unload correctly records `skipped:"not_listed"` (its modules
  were already unloaded by the in-leg verified-index fires).

### Claim — battery replay: row totals 86 entries / 136 legs: PASS; "failures empty in all runs": NOT-REPRODUCIBLE on first pass, environmental, green on bounded re-runs

Documented battery invocation = the baseline's four modes (there is no
`--runs` flag). Commands (each `timeout 900`, CWD repo root; logs
`corpus/live/r81-verifier/battery{,-rerun}/commands.log`):

| mode | pass 1 (17:47–17:58Z) | re-run | result |
| --- | --- | --- | --- |
| `normal` | rc 0, failures {} — receipt `20261015T174758787168Z-normal` | — | PASS |
| `--probe-capture-r78` | rc 1 | rc 1 (18:01Z) then **rc 0** (18:10Z, receipt `…181043Z`) | PASS on 3rd |
| `--probe-capture-r79` | rc 1 | **rc 0** (18:07Z, receipt `…180712Z`) | PASS on 2nd |
| `--probe-module-r80` | rc 0, failures {} — receipt `20261015T175737125582Z-module-r80` | — | PASS |

Green-set census (`rows.py`): normal 17/0, capture-r78 25/59,
capture-r79 25/67, module-r80 19/10 → **86 entries / 136 legs, exact
match** to the claim; failure dicts empty in the green set.

The two first-pass failures — one entry each, both in legs the r81
baseline already documented as environmental-variance cells:

- `playback_default_follow_r78_probe`: *"follow moved: last live
  consumers [SPDIF] — the stream never settled on the live default at ITS
  spawn (r78_def_sink_<pid>)"* — **byte-for-byte the same failure string
  the r81-baseline's own runs-b logged** under foreign contention. My leg
  detail shows the stream bound to `r78_def_sink` at +0.8 s then followed
  the +0.5 s `set-default` restore back to SPDIF by +1.8 s (author's
  green runs kept it pinned) — re-link timing inside the measurement
  window, not a code path difference.
- `loopback_playback_lattice_r79_probe` `c02_second_sink`: *"the tap on
  r79lb_ns_b2_<pid> carried no tag-tone windows — consumption without
  content is not a playout verdict"* — same "tap heard no tone" class as
  the baseline's runs-a `b05_garbage` confound; green on re-run.

Host-state cause identified: **a sibling r92-scout lane was actively
probing throughout my window** — `r92s_in` sink loaded (module-level),
plus cycling `pw-record` pairs (`r92s_ref`/`r92s_rec`, still alive at
18:12Z; its driver log shows stages launched under `timeout 1800` during
my battery). This mirrors the baseline's documented r91-scout confound.
Disclosure: my receipts' `contention` blocks still read
`pw_record:0, host_is_quiet:true` — the census keys on `comm=="pw-cat"`
(`measure_audio.py:6470`) while a directly-invoked `pw-record` (symlink
to `pw-cat`) reports `comm="pw-record"`; verified live: `/proc/<pid>/comm`
= `pw-record`. So `host_is_quiet` **under-reports pw-record/pw-play
activity** — a census blind spot, not a claim failure of r81. The failing
families are prior rows untouched by this commit (independently proven by
the `normal` byte-identity below).

### Claim — `normal` receipt byte-stable at sha `8e8cdad6…`: PASS

`sha256sum corpus/live/r81-verifier/battery/normal.receipt.json` =
`8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` —
byte-identical to the author's pinned sha (now identical 6 ways:
author a/b, baseline a/b, canonical, verifier).

### Claim — clean teardown / no leftovers: PASS

Post-run census at 18:12Z: `pw-dump | grep -E 'gst_r81|r78|r79|r80|verif'`
→ 0 nodes; `pactl list modules short` → 0 probe modules; `pactl list
sinks short` shows only host sinks + foreign `r92s_in`; `ps` shows no
stray `gst-launch`/`measure_audio`/capture processes of mine (the two
live `pw-record`s are the r92-scout lane's, seat-named, not touched). The
r81 family code contains zero `set-default-sink`/`set-default-source`
invocations (grep over the family block: comment mention only); I issued
none manually. The r78 family's own internal `set-default`+restore inside
its measured leg is committed prior behavior — `pactl get-default-sink`
read `…SPDIF__sink` before and after the battery, unchanged.

## Host-state notes

- Sibling lanes live during the window: r92-scout (`r92s_*` resources,
  active), plus a leftover non-audio `bash -c` analysis shell
  (pid 2756500) — neither mine, neither touched.
- All my capture legs were bounded by `timeout` at the shell level *and*
  by the fixture's own triple-bound (element bound + wall + byte cap).
- One resource could not be isolated from foreign traffic: the host
  **default sink** is shared and was observed read-only only.

## Files

- Changed (tracked): none. `git status` clean except the pre-existing
  untracked `corpus/live/` artifact tree.
- Added (untracked, seat-owned): `corpus/live/r81-verifier/` —
  `gst-r81.run{1,2}.{measurements.json,stdout.json,stderr.log,log,sha}`,
  `stability-gst-r81-run1-vs-run2.txt`, `receipt-shas.txt`,
  `battery/` (4 modes' stdout/stderr/receipt copies + commands.log +
  receipt-shas.txt), `battery-rerun/` (r78×2/r79×1 reruns, same custody);
  fixture-written receipts under `corpus/live/runs/` at stamps
  `…174710-gst-r81`, `…181232-gst-r81`, `…174758-normal`,
  `…175125/…180134/…181043-capture-r78`, `…175710/…180712-capture-r79`,
  `…175737-module-r80`. This report. No commits.

## Remaining risks / blockers

- `capture-r78`'s `playback_default_follow` leg is timing-sensitive to
  shared-host WirePlumber re-link latency: red 2/3 in my window under a
  live sibling lane, green when quiet. Not an r81 defect (prior row,
  byte-proven code path) but means battery "all green" is host-luck
  dependent — the author's 8/8 is achievable but not guaranteed per pass.
- `contention.host_is_quiet` misses directly-invoked `pw-record`/`pw-play`
  (comm blind spot) — a fixture limitation predating r81.

VERDICT: **VERIFIED-WITH-RESERVATIONS** — every r81-authored claim
reproduced on the committed tree (compile, +1686/−3 one-file diff, family
green ×2 with all seven claims verbatim, 86/136 battery census,
`8e8cdad6…` byte-stability, clean contention ledger); the sole
non-reproduction is the "failure dicts empty in all battery runs"
surface, attributable to live sibling-lane contention on a documented
prior-row leg, green on bounded re-run.
