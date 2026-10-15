# r81-verifier2 — re-verification of the FOLDED tree

Seat: verifier (second pass, post-fold). Scope: the fold commit `07c0671`
("r81 fold: S1-S9+L1 dead code, freeze predicate pins corrected
0x7FFF0024/0x7FFF0000, e3/e8/e9 real out_paths"). HEAD moved during my
window (r92-scout commit `4256ea0` landed mid-battery) — per the task
rule, the fixture sha was verified directly:

- `git rev-parse 07c0671:corpus/fixtures/measure_audio.py` =
  `git rev-parse HEAD:corpus/fixtures/measure_audio.py` =
  `38c67960d1d0622184b1e8262c7b401ee4dcfc3e` — blob identical; the r92
  commit did not touch the fixture.
- `sha256sum corpus/fixtures/measure_audio.py` =
  `5eaba74b532eb9c62d529fe3d94534c36cb3b3954365cb61b8552ade9ed49d82` —
  matches the fold report's recorded sha; worktree file clean
  (`git status`/`git diff` empty for the path).
- Diff scope: `git show 07c0671 --stat` = 1 file, +50/−75 (15246 →
  15221 lines; the task's "15219" is a counting-variant, the commit
  arithmetic is exact).

All invocations `timeout`-bounded (900 s), CWD = repo root. Receipts and
custody under `corpus/live/r81-verifier2/` (`commands.log`,
`receipt-shas.txt`, per-mode stdout/stderr/receipt copies, `battery/` for
the four battery modes + `battery.sh` driver).

## Claim — `python3 -m py_compile corpus/fixtures/measure_audio.py`: PASS

rc=0, `PY_COMPILE_OK`, 18:31Z.

## Claim — `--probe-gst-r81` runs green, failures `{}`, 54 legs, freeze legs pinned: PASS (1/1 run)

`timeout 900 python3 corpus/fixtures/measure_audio.py --probe-gst-r81`
(18:33Z) → rc=0, stdout
`{"receipt": ".../runs/20261015T183327219943Z-gst-r81/measurements.json",
"failures": {}}`.

Receipt sha256 `09a0b6f8921fd63aaf848d5beb082b3b27c890f16aeb0c4928b1bcb668981730`
(copy: `corpus/live/r81-verifier2/gst-r81.receipt.json`).

- **24 entries** = 17 prior (all legs=0, untouched) + 7 gst family —
  matches the fold report's census.
- **54 legs**: gst_element_lattice 15, gst_naming 5, gst_routing 12,
  gst_pulse_axis 6, gst_target_loss 7, gst_exit_classes 6 (p8 removed),
  gst_autodetect 3.
- **Freeze legs carry the corrected constants empirically** — t3_pwsrc,
  t4_on_disconnect_error, t5_on_disconnect_eos, t6_prop_only each measured
  `riff=wavenc_streaming riff_size=2147418148 (0x7FFF0024)
  data=wavenc_streaming data_declared=2147418112 (0x7FFF0000)
  bytes=204844`, `exit=-9 killed=wallcap` (alive at cap). Predicate at
  `measure_audio.py:13920–13922` pins exactly those values; a falsified
  `0x7FFFF000` artifact would now fail the leg (reviewer F1 closed, via
  S7).
- **e3/e8/e9 real out_paths (F3 closed)** — all three argv carry
  `wavenc ! filesink location=<out>`; `class_summary` =
  `{parse_rc1_no_artifact: true, runtime_refusal_zero_byte: true}`; the
  exit arm is 6 legs (e1, e3, e8, e9, e10, e11) — **no `p8_bogus_server`
  leg anywhere in the receipt**.
- Teardown inside the entry: `unloads` shows the name-verified path
  (`captured` module id, `skipped:not_listed` on re-check),
  `sinks_gone.gst_r81_auth_<pid>=true`, `own_nodes_after=[]`.

## Claim — battery pass: 86 entries / 136 legs, failures empty, `normal` sha `8e8cdad6…`: PASS — all green on first pass

Documented invocation = the baseline's four modes verbatim (no `--runs`
flag), each `timeout 900`, sequential, receipts under `runs/` copied to
`corpus/live/r81-verifier2/battery/`:

| mode | window (Z) | rc | failures | receipt sha256 |
| --- | --- | --- | --- | --- |
| `normal` | 18:34:17 | 0 | {} | `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b` |
| `--probe-capture-r78` | 18:37:49 | 0 | {} | `7f7a9e63c4aaa2909d1184ac832450a9ad4d754bb0b60c0d4a3be75229d8c21f` |
| `--probe-capture-r79` | 18:43:27 | 0 | {} | `1a98d7facaa9ca6e9a93d9a942e7d8cf4a9df100c7d59d8e2dff43679b5226d6` |
| `--probe-module-r80` | 18:43:53 | 0 | {} | `53f2f56c20914131d49b495270a0a1e5c4843661684c67b92fec15fb9664689f` |

Census over the four receipts: normal 17/0, capture-r78 25/59,
capture-r79 25/67, module-r80 19/10 → **86 entries / 136 legs, exact
match** to the fold report's "shape confirmed unchanged".

**`normal` receipt sha = `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`
— byte-identical** to the pinned sha (now 7-way identical: author a/b,
baseline a/b, canonical, verifier1, verifier2). Byte-equality through the
fold on the deterministic path is direct evidence the prior rows are
untouched.

Unlike verifier1's window (2 transient reds under sibling r92-scout
contention), mine had **zero transient reds — all four modes green on the
first pass**. Every contention block in the battery receipts reports
`host_is_quiet: true` with all counters 0. The r92-scout *commit* landed
mid-battery but no live `r92s_*` modules/sinks/processes were observed at
any census point. (Inherited caveat, not a claim failure: the contention
census keys on `comm=="pw-cat"` and can under-report directly-invoked
`pw-record`/`pw-play` — documented by r81-verifier1; all legs were green
so nothing is being excused by it.)

Fixture sha256 before == after every run (`5eaba74b…`, see
`battery/commands.log`).

## Claim — dead-code removals landed, reuse wired: PASS (grep-verified)

On the committed file (`measure_audio.py`):

| removal (simplifier id) | probe | result |
| --- | --- | --- |
| `ports` collection in `_gst_r81_graph` (S1) | function body | returns `{nodes, links, clients}` only — `ports` gone |
| `_props` nested helper (S2) | `def _props` | 0 hits |
| `kill_proc`/`call` event arms (S3) | `kill_proc`, `"call"` | 0 / 0 hits |
| `"ns"`/`"tag"` ctx keys (S4) | `ctx = {"ns"`, `ctx.get("ns")` | 0 / 0 hits |
| `<tone>` redaction token (S5) | `ctx.get("tone")` | 0 hits; the two remaining `<tone>` strings (:6548/:6555) are r7x-era code, outside the gst_r81 family |
| `expect_class` write-only leaf (S6) | `expect_class` | 0 hits |
| `placeholder_7ffff000` / `0x7FFFF000` (S7) | both tokens | 0 / 0 hits; corrected `0x7FFF0024`/`0x7FFF0000` present at :12775/:12791/:13920–13926 |
| `_gst_r81_ns_ensure` duplication (S8) | :12846–12856 | helper now delegates to `_loopback_r79_sinks_load([GST_R81_NS])` — the r79 helper is reused (9 r79 call sites + all gst_r81 ensure sites) |
| redundant `wall_cap=` passes (S9) | `wall_cap=GST_R81_WALL_S` | 1 hit = the signature default itself (:12906); the 3 redundant call-site passes removed; the 3 `GST_R81_LOSS_WALL_S` overrides correctly kept |
| `p8_bogus_server` leg (L1) | `p8_bogus_server`, `"p8` | 0 / 0 hits; exit arm = 6 legs in code and receipt |

## Claim — clean teardown / zero seat-owned leftovers: PASS

Post-run census 18:44:19Z (battery done 18:43:53Z + gst run 18:33Z):

- `pw-dump | grep '"node.name"'` for `r81|r78|r79|r80|r92|verif|gst|def_|lb_`
  → **0 nodes**.
- `pactl list modules short` → **0** null-sink/loopback/virtual modules
  (all probe unloads went through the index-verified path; none needed
  manual cleanup).
- `pactl list sinks short` → only host sinks: `HiFi__SPDIF__sink`,
  `HiFi__Speaker__sink`, `HiFi__Headphones__sink` (all SUSPENDED) +
  `hdmi-stereo` (host PCI hardware; appeared vs the pre-run list — a host
  device event, not seat-owned).
- `ps` → no `gst-launch`, `pw-record`, `pw-play`, `pw-cat`,
  `pw-loopback`, `paplay`, `parec`, or `measure_audio` processes.
- Seat naming respected: fixture spawned only `gst_r81_auth_<pid>` /
  `gst_r81_<pid>`-prefixed objects; my seat issued no `set-default-*`
  calls; all captures bounded by shell `timeout` and the fixture's own
  wall/byte caps.

## Verdict

**VERIFIED** — every folded claim reproduced verbatim on the committed
tree: py_compile clean; `--probe-gst-r81` rc=0 / failures `{}` / 54 legs
with the freeze legs empirically carrying the corrected pinned constants
(0x7FFF0024/0x7FFF0000); battery 86 entries / 136 legs with all four
modes' failures empty **on the first pass** and `normal` byte-identical
at `8e8cdad6…` (7-way); all S1–S9+L1 removals grep-confirmed absent and
`_loopback_r79_sinks_load` reuse live; zero seat-owned leftovers.

Residual risks (inherited, not new): the contention census's
`comm=="pw-cat"` blind spot (documented by verifier1) means a `pw-record`-
only foreign lane could go unrecorded — moot here, all green; reviewer
F2 (`node.dont-reconnect` witness unreferenced) remains a fold-deferred
item noted by the fold seat.

Blockers: none. Custody: `corpus/live/r81-verifier2/` (untracked
evidence), this report. No commits made.
