# audio round 72 — verifier (seat: verifier)

Post-landing verification of the r72 third-decoder arm
(`--probe-sndfile-transport-r72` in `corpus/fixtures/measure_audio.py`).
Host: SoX_ng v14.8.0.1, ffmpeg/ffprobe n9.0.1, libsndfile 1.2.2-4
(`/usr/lib/libsndfile.so.1`, `sf_version_string()` = `libsndfile-1.2.2`),
CPython 3.14.7.

## Landing timeline (all times UTC)

- `14:20` — verification began; `HEAD = c079aba`, no `sndfile`/`r72`
  references in `corpus/fixtures/measure_audio.py`, working tree clean.
  Frontier report + scratch consumed; independent ctypes 4-arm matrix
  and `sndfile-info` logs produced in `corpus/live/r72-verifier/`.
- `14:26:18` — author arm visible in working tree + author receipt
  `corpus/live/runs/20261014T142618906524Z-sndfile-transport-r72/`.
- `14:27:07` — **commit `26baed1`** lands the arm (operator-substituted
  author, `ci <ci@local>`; no `r72-author.md` exists — the commit message
  + `LOG.md` carry the declared/corrected claim).
- `14:27:33` — my replay writes
  `corpus/live/runs/20261014T142733592435Z-sndfile-transport-r72/`.
  Fixture sha256 `515aabeb…` is identical in the working tree, `26baed1`,
  and `4fff488` — **the replay ran on the committed tree**.
- `14:27:51` — report-last `4fff488` (LOG/SCORECARD/adjudicator + seat
  reports; sweeps three r72 receipts and this seat's early scratch into
  the index).

## Item 1 — r72 arm replay on the committed tree: AGREE

```
python3 corpus/fixtures/measure_audio.py --probe-sndfile-transport-r72
```

- Exit **1**, ~10 s wall, stderr empty (0 B). Expected per the r67
  convention: `extsuffix_snd` forks across transports and the fork is
  recorded as a failure
  (`transport: libsndfile verdict forks across transports
  (file/fifo_path=RAW (header-less)/U-Law vs stdin_pipe/redirected_fd=
  Format not recognised.)`); `main()` returns `bool(failed)`.
- Receipt: `corpus/live/runs/20261014T142733592435Z-sndfile-transport-r72/measurements.json`;
  `mode="probe-sndfile-transport-r72"`, run dir suffix
  `-sndfile-transport-r72` — mode/suffix **wired** (r71 D1 not repeated:
  flag at `measure_audio.py:1102`, mutex sum `:1105`, measurement block
  `:1325-1335`, mode `:1791`, suffix `:1811`).
- All 9 `sndfile_<member>_r72_probe` entries present, each with a full
  4-transport axis (in-process ctypes `sf_open`/`sf_open_fd` +
  `sf_readf_short` drain), `transport_verdict_groups`, `transport_fork`,
  `decoder="libsndfile libsndfile-1.2.2"`, `sndfile_info_cli` (file arm
  only, exit 0 even on reject — verdicts keyed on the ctypes legs, not
  the CLI exit code, per frontier guidance).

Per-member verdicts, fresh receipt vs my independent ctypes matrix
(`corpus/live/r72-verifier/sndfile-matrix-verifier.json`, run with the
frontier harness before the arm existed) vs the frontier's own matrix:
**36/36 cells agree** on (format_name, read_frames, error-verdict):

| member | file | stdin_pipe | redirected_fd | fifo_path |
|---|---|---|---|---|
| dec_act | WAV/PCM16 rd 278 | same | same | same — no fork |
| dec_hcom | WAV/PCM16 rd 278 | same | same | same — no fork |
| posttable_nomatch | REJ `Format not recognised.` | same | same | same |
| txw_piperefuse | REJ `unimplemented format` | same | same | same (unique tier: magic recognized, no reader) |
| extsuffix_{wav,bin,txw,f32} | REJ `Format not recognised.` | same | same | same |
| extsuffix_snd | RAW/U-Law rd 500 | REJ | REJ | RAW/U-Law rd 500 — **fork, named-vs-anonymous** |

(The only textual delta vs my harness: the arm normalizes success to
`error: null` + `error_str: null`, where the frontier harness leaves
`"No Error."` in `error` — a convention difference, not a verdict one.)

- **Byte-stability: ×6, stronger than the claimed ×2.** All six
  `-sndfile-transport-r72` receipts (`…T142618906524Z`, `…T142634507936Z`,
  `…T142733592435Z` [mine, committed], `…T142824524743Z`,
  `…T142841935923Z`, `…T142954167521Z`) hold byte-identical
  `sndfile_*_r72_probe` entries. No path/tmp leak: `path` is
  repo-relative (`live/round-66/pair_dec_act.wav`), error strings are
  libsndfile's own, and `sndfile_info_cli.reason` captures only the last
  output line (`Format not recognised.`) — the path-bearing
  `Error : Not able to open input file <abs>` line is not the last line
  (r71 D2 not repeated; verified in
  `corpus/live/r72-verifier/logs/info-*.txt`).
- `sndfile_info_cli.frames_field` for `extsuffix_snd` records `512`
  while `read_frames` is `500` — the CLI Frames line is a container
  estimate kept alongside, not keyed on (boundary's 12-byte sniff
  consumption accounts for the delta; critic counterexample-3 honored).

## Item 2 — prior battery replay on the committed tree: AGREE (byte-stable)

Four arms re-run; each probe entry byte-compared to the latest committed
(git-tracked) reference for its mode:

| flag | exit | fresh receipt | committed ref | probe-entry diff |
|---|---|---|---|---|
| `--probe-ffprobe-transport-r71` | 0 | `…T143132478314Z-ffprobe-transport-r71` | `…T141033155858Z` | **0/9 differ** |
| `--probe-transport-dec-act-r67` | 1 | `…T143134547969Z-transport-dec-act-r67` | `…T140657558238Z` | 0/1 differ |
| `--probe-transport-extsuffix-snd-r69` | 1 | `…T143136560660Z-transport-extsuffix-snd-r69` | `…T140641162793Z` | 0/1 differ |
| `--probe-transport-txw-piperefuse-r68` | 1 | `…T143138574159Z-transport-txw-piperefuse-r68` | `…T140645235307Z` | 0/1 differ |

Exit-1 legs are the known committed transport forks (failure-by-design),
and their failure strings match the committed receipts verbatim. Prior
rows byte-stable under the r72 insertion — verified by execution, not
just by construction.

## Item 3 — insertion-only diff: AGREE

`git show 26baed1 -- corpus/fixtures/measure_audio.py`: **+236/−3**.
Every removed line re-appears in the added set with exactly one term
inserted (checked mechanically): the mutex `sum([...])` gains
`args.probe_sndfile_transport_r72`; the `mode` chain prepends
`"probe-sndfile-transport-r72" if … else`; the `suffix` chain prepends
`"-sndfile-transport-r72" if … else`. The remaining 233 additions are
the new block `measure_audio.py:734-950` (`TRANSPORT_R72_MEMBERS =
TRANSPORT_R71_MEMBERS`, `_SF_INFO`/`_SF_FORMAT_INFO` ctypes decls,
`_sndfile_verdict`, `_sndfile_leg`, `sndfile_transport_entry`), the
flag, the mutex term, the measurement block, and the two chain terms.
No prior measurement code altered.

## Item 4 — 3-decoder lattice claim: PARTIAL (as briefed) / AGREE (as landed)

Briefed claim: "sox-only: txw-seekable/.f32-named; sndfile-only:
.snd-named; ffmpeg superset on detect". Critic/scout/boundary corrected
2 of 3 clauses **before** the arm landed; the committed code comment
(`measure_audio.py:1327-1331`), `LOG.md`, and `r72-adjudicator.md` carry
the corrected claim. My independent per-member accept lattice
(`corpus/live/r72-verifier/extract_lattice.py` → `lattice.json`, sources:
committed r67/r68/r69 sox receipts + committed r71 ffprobe receipt + the
fresh r72 receipt) reproduces the corrected partition exactly:

| class (sox, ffmpeg, sndfile) | members | arms where accepted |
|---|---|---|
| (T,T,T) all-decode | dec_act, dec_hcom | all 4 under ffmpeg/sndfile; sox: dec_hcom all 4, dec_act file-only (bridge fork) |
| (T,F,F) sox-only | txw_piperefuse | sox {file, redirected_fd} — the seekable pair |
| (T,F,F) sox-only | extsuffix_f32 | sox {file, fifo_path} — the named pair |
| (T,F,T) sox+sndfile joint | extsuffix_snd | {file, fifo_path} for both, different mechanisms (sndr CHECK row vs post-sniff name fallback) |
| (F,F,F) all-reject | posttable_nomatch, extsuffix_{wav,bin,txw} | — |

- Clause "sox-only txw-seekable/.f32-named": **AGREE** — 4 cells, no
  other decoder accepts those members on any arm (libsndfile's txw
  verdict is the recognized-then-refused `unimplemented format` tier —
  still a reject).
- Clause "sndfile-only .snd-named": **DISAGREE-as-stated** — sox decodes
  the same member on the same named arms (sndr, 504 samples; committed
  r69 receipt + my extract). The class is (T,F,T). The (F,F,T)
  sndfile-only class is **empty** on the tracked 9. Landed materials
  record this falsification — the correct outcome handling.
- Clause "ffmpeg superset on detect": **DISAGREE-as-stated** — ffmpeg's
  accept set {dec_act, dec_hcom} is the strictest, not a superset
  (⊂ sox's and ⊂ sndfile's per-member accepts on this corpus).
- Net "distinct decoder-coverage classes": **AGREE** — 4 non-empty
  classes on 9 members, all confirmed on committed receipts.

## Item 5 — hygiene: AGREE

Post-run sweep: zero `/tmp/sndfile-r72-*` or `/tmp/transport-r72-*`
leftovers (legs are in-process ctypes; the fifo arm uses
`TemporaryDirectory` + `reap_fifo_orphans` at `measure_audio.py:879`),
zero `measure_audio`/sndfile process orphans (only other seats' live
scratch jobs were visible during the sweep). Zero pre-existing
ffmpeg/ffprobe orphans on the host today (the r71-era population is
gone).

## Nits (observations, not verdict-affecting)

- N1 — `"decoder": "libsndfile libsndfile-1.2.2"` doubles the name
  (`"libsndfile " + sf_version_string()`, `measure_audio.py:932-933`).
  Cosmetic; the version pin itself satisfies the critic's
  cross-build provenance requirement.
- N2 — Commit `26baed1` also swept `corpus/live/r72-baseline/` scratch
  (incl. a copied `measure-env/` fixture tree, one copy of which now
  shows `M` in `git status` — another seat's live state) and `4fff488`
  committed a `__pycache__/*.pyc` plus this seat's early scratch +
  probe receipts mid-verification. Not arm defects; corpus-hygiene
  notes for the operator.
- N3 — `frames` field vs `read_frames` (512 vs 500 on `.snd`): recorded
  correctly as container-field vs decode-drain; boundary's 12-byte sniff
  finding explains the delta. No verdict keys on `frames`.

## Files / receipts

- Report: `reports/round-72/r72-verifier.md`.
- Scratch (`corpus/live/r72-verifier/`): `extract_lattice.py`,
  `lattice.json`, `sndfile-matrix-verifier.json` + `.stderr.log`,
  `logs/info-*.txt`, `r72-run.stdout.json` + `.stderr.log`,
  `batt-probe-*.stdout.json` + `.stderr.log`.
- Probe-written receipts (tool's own output): all six
  `corpus/live/runs/*-sndfile-transport-r72/measurements.json` (mine:
  `…T142733592435Z`), `…T143132478314Z-ffprobe-transport-r71`,
  `…T143134547969Z-transport-dec-act-r67`,
  `…T143136560660Z-transport-extsuffix-snd-r69`,
  `…T143138574159Z-transport-txw-piperefuse-r68`.

## Remaining risks

- Within-host only: libsndfile 1.2.2-4 (Arch). The fallback extension
  set and the `unimplemented format` tier are compile-time; receipts pin
  `sf_version_string()` but a different build could legitimately differ.
- The empty (F,F,T) class is a corpus property, not a decoder property
  — the critic's `.au`-named bytes instantiate it off-corpus. Any future
  round adding such a member must re-run all three arms.
- `sf_open` honors the name only via the path argument; `|cmd` and
  `/dev/stdin` spellings unprobed (frontier's caveat stands).
