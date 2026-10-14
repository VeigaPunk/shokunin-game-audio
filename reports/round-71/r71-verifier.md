# audio round 71 — verifier (seat: verifier)

Post-landing verification of the r71 ffprobe transport arm
(`--probe-ffprobe-transport-r71` in `corpus/fixtures/measure_audio.py`).
Host: ffmpeg/ffprobe n9.0.1, SoX_ng v14.8.0.1, CPython 3.14.

## Pinning note (brief inconsistency, not a code defect)

The brief pins the arm "committed at HEAD". Observed: `HEAD = e4e0444`
("r70 report-last"); `git status` shows ` M corpus/fixtures/measure_audio.py`
(+194/−1 vs HEAD) and `git log -3 -- corpus/fixtures/measure_audio.py` tops
out at r70 commit `59a7440`. **The r71 arm is uncommitted working-tree
state**, matching the author report's disclosed operator substitution.
I verified the landed working-tree state as-is.

## Item 1 — r71 arm: PASS (with bookkeeping defects D1/D2 below)

Command (fresh scratch `corpus/live/r71-verifier/`, ~4 min wall):

```
python3 corpus/fixtures/measure_audio.py --probe-ffprobe-transport-r71
```

- Exit: **0**; stdout receipt line:
  `corpus/live/runs/20261014T140436216589Z-normal/measurements.json`;
  `failures: {}`; stderr empty (0 bytes).
- All 9 `ffprobe_*_r71_probe` entries: `transport_fork: false`,
  `failures: []`, exactly one `transport_verdict_groups` entry spanning
  `[file, stdin_pipe, redirected_fd, fifo_path]` — **all members
  transport-invariant under ffmpeg/ffprobe**.
- `dec_act` → `ffprobe_format="wav"`, `probe_score=99`, `ffprobe_exit=0`,
  `ffmpeg_exit=0` on all 4 transports — detect+decode everywhere.
- `dec_hcom` → `ffprobe_format="hcom"`, `probe_score=100`, exits 0/0 on
  all 4 transports.
- All 7 no-match members (`posttable_nomatch`, `txw_piperefuse`,
  `extsuffix_{wav,bin,txw,f32,snd}`) → `ffprobe_format=null`,
  `ffprobe_exit=1`, `ffmpeg_exit=183` "Invalid data found when processing
  input" on all 4 transports — content-based rejection, name-insensitive.
- **redirected_fd shared-fd artifact: ABSENT.** `redirected_fd` is
  verdict-identical to `stdin_pipe` on every member (both run ffmpeg's
  `pipe:` protocol; same `pipe::` error text on rejects). The fresh-fd fix
  at `measure_audio.py:591` (`fh = open(stdin_path, "rb")` inside `run()`,
  per subprocess) holds.

## Item 2 — byte-stability of r67 arm: PASS

Command:

```
python3 corpus/fixtures/measure_audio.py --probe-transport-dec-act-r67
```

- Exit: **1** — expected: the known r67 transport fork is recorded as a
  failure by design (`main()` returns `bool(failed)`); the failure string
  matches the committed references verbatim.
- Receipt: `corpus/live/runs/20261014T140609902129Z-transport-dec-act-r67/measurements.json`
- `transport_axis` **byte-identical** to three committed (git-tracked)
  r67 references spanning 05:19–11:07 UTC:
  `runs/20261014T051948229455Z-transport-dec-act-r67`,
  `…T105010061339Z-…`, `…T110708558970Z-…`. The whole
  `transport_dec_act_r67_probe` entry (fork flag, failures, protocol) is
  also identical. The r71 insertion did not perturb prior rows.

## Item 3 — fifo hygiene: PASS

Post-run sweeps (`pgrep -a ffmpeg|ffprobe` + `/proc/*/cmdline` scan for
`transport-r71-*`, run mid-flight and again after both runs):

- **Zero** ffmpeg/ffprobe processes carrying a `transport-r71-*` fifo
  path; no `/tmp/transport-r71-*` dirs remain (TemporaryDirectory +
  `fifo.unlink` cleanup works).
- Observation only (not this arm): ~60 pre-existing ffmpeg orphans from
  earlier rounds/seats are alive (`r67-boundary/probes/.fifo_probe`,
  `/tmp/r67rev_fifo`, `/tmp/r69-starve-*`, `/tmp/r70simp-*`,
  `/tmp/holdladder-*`, `/tmp/open2-hold-*`, `/tmp/r71-scout-fifo-*`,
  `/tmp/fifo-hold-r70-*`), plus one stale `/tmp/transport-r67-eK2xTKfr/`
  dir (mtime 07:52 local, predates this session). None match the r71
  criterion; flagged for corpus hygiene, not counted against the arm.

## Defects found

- **D1 — mode/suffix wiring missing.** `args.probe_ffprobe_transport_r71`
  is in the mutex sum (`measure_audio.py:878`) and the measurement block
  (`:1086`) but absent from the `mode` (`:1553`) and run-dir `suffix`
  (`:1573`) selector chains. The receipt records `"mode": "normal"` and
  lands in a `*-normal/` dir — indistinguishable by mode/dir from an
  unprobed run (the author's own receipts show the same:
  `20261014T140155796326Z-normal`). Measurement keys still carry the r71
  family, so no data is lost; ledger tooling keyed on mode/suffix would
  mislabel it.
- **D2 — receipt not byte-stable / path leak.** `ffprobe_error` is
  normalized only for backtick-quoted input names (`:647`), but ffprobe
  emits `<abspath>: Invalid data found when processing input`. Result:
  (a) the fifo leg embeds the random mkdtemp suffix
  (`/tmp/transport-r71-XXXXXXXX/<name>`) — my receipt differs from the
  author's `20261014T140155796326Z` in exactly 14 fields (the 7 no-match
  members' `fifo_path.ffprobe_error` + `ffprobe_verdict_groups`), so the
  new ledger family is not replay-stable as landed; (b) the `file` leg
  embeds the absolute repo path (host-specific); (c)
  `ffprobe_verdict_groups` splits each no-match member into 3 groups
  (file / stdin_pipe+redirected_fd / fifo_path) purely on the differing
  path text — a grouping artifact, not a detection fork.
  `transport_verdict_groups` is unaffected (`ffmpeg_error` is already
  normalized) and `transport_fork` stays false, so the item-1 verdict is
  unaffected.
- **D3 — author report claim falsified-as-stated.** "probe_score returned
  null on n9.0.1 (field absent in this build's format dict)": both the
  author's receipt and mine carry `probe_score=99` (wav) / `100` (hcom)
  on successful detection; null appears only on the 7 rejecting members
  (ffprobe exit 1, no format JSON emitted).

## Files changed

- `reports/round-71/r71-verifier.md` (this report)
- `corpus/live/r71-verifier/r71-run.stdout.json`, `r71-run.stderr.log`,
  `r67-decact-run.stdout.json`, `r67-decact-run.stderr.log` (scratch)
- Probe-written receipts: `corpus/live/runs/20261014T140436216589Z-normal/measurements.json`,
  `corpus/live/runs/20261014T140609902129Z-transport-dec-act-r67/measurements.json`

## Remaining risks

- D2 means cross-run receipt diffs will always fire on the fifo leg until
  the error tail is path-normalized; any ledger byte-compare over the r71
  family needs the same `compare_receipts.py`-style masking the author
  used, or a fixture fix.
- Pre-existing orphan ffmpegs (item-3 observation) could mask a future
  real leak if a `transport-r71-*` survivor hides among them — the sweep
  keyed on the prefix, so this run is clean regardless.
