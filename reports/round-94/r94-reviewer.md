# r94 reviewer — the SoX_ng effect/DSP lattice, independently re-run

Seat: **reviewer** (leaf). Lane repo `/home/vgpnk/Projects/shokunin/audio-shokunin`
at **HEAD `aaf56d30`** (merge of `5755be5b` r89-foldfix + `f46dce00` r94-author).
Host `plazir27`, reviewer window **2026-10-16 08:55:05Z → 09:00Z**, loadavg
~55, `sox` = SoX_ng v14.8.0.1 (`/usr/bin/sox` sha256
`646d899b53c1c3fb94d8f48032a1e5eee549df75b22b4819a6be896af0d36947` — unchanged),
Python 3.14.7, numpy 2.5.3. **Zero commits. Zero tracked writes. No
`pactl set-default-*`.**

## Verdict

**PASS-wf (no actionable defect in the r94 diff).** The r94 sox family is
green on the *committed* bytes under an independent re-run, its receipts
resolve, its cross-seat witness layer is honest in both directions, and the
report's headline numbers re-derive. Two report-accuracy nits (LOW) and one
concurrent-lane hazard (MEDIUM, **not** the r94 author's) are recorded below.

## What was re-run, on which bytes

| step | command (all with `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`) | result |
| --- | --- | --- |
| pre-state | recorded before any run | HEAD `aaf56d30`, fixture sha **`4808c4cf`**, pyc sha `6e271a2d`, sox sha `646d899b` |
| full family | `python3 corpus/fixtures/measure_audio.py --probe-sox-r94` (`PYTHONDONTWRITEBYTECODE=1`) | rc 0, `corpus/live/runs/20261016T085514726246Z-sox-r94/measurements.json`, `failures: {}` |
| own spot harness | `python3 corpus/live/r94-reviewer/r94r_spotcheck.py` (own RIFF reader/writer, raw sox, own numpy laws) | **88 checks, 0 failed** |

The reviewer run is bound to the committed bytes: the pre-state sha `4808c4cf`
equals `git show HEAD:corpus/fixtures/measure_audio.py`, and the run could only
have parsed a clean file (see the MEDIUM finding for why that matters).

## Merge / provenance checks (the "green-run shas vs committed bytes" question)

- The author's green-run implementation sha `84298dcc…` is the **branch commit**
  blob `f46dce00:corpus/fixtures/measure_audio.py` and the archive copy
  `r94-author/measure_audio.py.final` — all three agree.
- The lane repo's **HEAD** blob is `4808c4cf…` (the merge brought in main's r89
  foldfix `+135/−26`). The two blobs differ **only outside** the r94 block: the
  2196-line family block (`r94-author/probes/r94_family.py`, sha `d2d233eb…`,
  **108 388 bytes**) is **byte-identical** in both — found verbatim at byte
  **1518983** of `git show HEAD:corpus/fixtures/measure_audio.py` and at byte
  1513299 of the author's green-sha copy (offsets verified byte-wise, not
  char-wise).
- The merge is clean: `grep -c '^<<<<<<<'` on `git show HEAD:…` = **0**, and the
  HEAD blob imports and executes (my run, plus a direct `importlib` load of a
  HEAD-blob copy in `r94-reviewer/r94r_probe/`).
- **A fresh run on the HEAD bytes is green**: 150 legs, `failures` empty and
  `coverage_blocked` empty in all 8 entries.
- Author receipts resolve: both parse, `mode = probe-sox-r94`, 8 entries,
  150 legs, 0 failures, 0 blocked; `host.sox_sha256` in both equals the live
  `/usr/bin/sox`; the archive copies in `r94-author/receipts/` are byte-identical
  to the `runs/` originals (2/2 MATCH); `sha256sum -c r94-author/manifest.sha256`
  = **217/217 OK**, manifest sha `a16d0a08…` as reported; scratch file count
  **211** as reported.

## Independently reproduced (not read from the author's receipts)

Structural walk of my receipt vs both author receipts, excluding
`host`/`host_exit`/`pw_census_*` and `wall_s`/`utc`/`loadavg`:

| pair | diffs | volatile legs | recorded guard row | worktree-path string | **unattributed** |
| --- | --- | --- | --- | --- | --- |
| reviewer vs author pass 1 | 110 | 108 | 1 | 1 | **0** |
| reviewer vs author pass 2 | 105 | 103 | 1 | 1 | **0** |
| author pass 1 vs pass 2 | 107 | 106 | 1 | 0 | **0** |

The single "path string" diff is `det_copy_token_not_an_effect.reps[0].error_hit`,
whose message embeds the absolute worktree path (`…-wt-r94` vs the lane repo) —
a path artifact, not a content difference. The 7 `volatile_sha` legs are exactly
the 5 default-path determinism legs + the 2 single-rep `-G` guard legs, and
**no volatile leg carries a fixed cross-seat sha witness** (checked: 0 overlap),
so the witness layer cannot flake.

Leg-level re-derivation with raw `/usr/bin/sox` + own RIFF reader + own numpy
(**50 of 150 legs, all 8 entries**: det 9, gain 6, rate 13, remix 5, trim 5,
fade 4, repeat/pad/silence 4, dither/stat 4):

- **Stimuli**: all 9 rebuilt from the documented definitions with my own writer;
  every rebuilt sha equals both the receipt's recorded sha and the **r94
  scout's `prep.json`** sha, and every rebuilt sample matrix is content-equal to
  the scout's own scratch file (independent seat, independent process).
- **det**: default `gain -6` 5/5 distinct vs `-D` 1/3 stable and byte-equal to
  the scout's `gain_D.json:gain_m6`; `gain 0`, the no-effect pass-through and
  `pad %50` byte-identical to the *stimulus* sha; `copy` refuses rc 2
  ``can't open input file``; f32→s24 stable 1/5 while f32→s16 is 5/5; `-D`
  after the infile gives the same bytes.
- **gain**: `gain -6` mismatch 0 vs `rint(x·10^(−6/20))`; `vol 0.5` mismatch 0
  vs **ceil** and 23000 vs rint; `vol -6.0206 d` mismatch 0 vs rint;
  `vol 0.5 p` mismatch 0 vs `rint(x·√0.5)` (peak −9.031078); the two `vol`
  spellings differ on 23000 samples with max abs diff **exactly 1 LSB**;
  chain order `[−2.999988]` vs `[−8.999645]`.
- **rate**: frames 11025 / 11026 / 5512 / 6013 / 2756 all exact; all 7 alias
  legs byte-equal to the receipt. **Falsification re-checked estimator-free**
  (band-minus-peak, same estimator both sides): default **−22.638 dB**,
  `-v` **−22.638 dB** (identical, distinct bytes), 20 kHz-default row
  **−126.107 dB** — i.e. the ≈−130 dB figure lives on the 20 kHz stimulus, not
  on `-v`. `-q` folds with peak −6.172481 and the 21.1 kHz band 2.7 dB below
  it; `-l` sits 23.020 dB below `-a` at 20 kHz; `rate -q -a` refuses rc 1 with
  the exact message.
- **remix**: `remix 1` = L (mismatch 0; 47000 differ from the mean); downmix
  = `floor((L+R+1)/2)` (mismatch 0; 17000 differ from nearest-even);
  `channels 1` byte-equal to `remix 1,2`; `-m` exact sum; `remix 0 1` = [0, L]
  (ch0 all-zero, ch1 = L) — the report's naming correction is right.
- **trim**: `1s` → 1 frame, `4800s` → 4800; `1sec` refuses with the
  `cannot parse position \`(null)'` class; `trim 0 0.1` is sample-exact
  (mismatch 0 vs the input head); `trim 0 0` is a valid 0-frame WAV rc 0.
- **fade**: stop positional truncates (7200 / 9600 frames); log envelope
  0.003169 / 0.056235 / 0.316210 vs `10^(−5(1−x))` 0.003162 / 0.056234 /
  0.316228; `fade 0.1` ≡ `fade l 0.1` bytes.
- **repeat/pad/silence**: `repeat 2` = 3N frames with tiling mismatch 0;
  `pad 0.1 0.2` 26400 frames, first_nonzero 4801, last_nonzero 16799;
  `silence 1 0.1 1%` 16796 frames with 7200 trailing zeros; both-sides keeps
  **959 = rate/50 − 1**; `-l` keeps 5759.
- **dither/stat**: `-R dither -s` stable, max 21 LSB / RMS **5.740681** and
  byte-equal to the scout; `-p 12` max 23 / RMS 7.969959; `stat` "RMS
  amplitude" 0.279509 = my own interleaved quadratic mean; "Maximum delta"
  0.728180 = interleaved max|Δ| (per-channel would be 0.065277); "Volume
  adjustment" 2.000; `stat -freq` 49152 lines = 2048·ceil(96000/4096) at an
  11.71875 Hz step; `stats -j` channel-0 rms −9.03088 / crest 1.41421 /
  peak_count 2000 / window 0.05.

**Honest-saturation checks** (own probe against a HEAD-blob copy, no writes):

- Witness absent (`SOX_R94_SCOUT` → nonexistent dir): `_sox_r94_ref_arm` and
  `_sox_r94_ref_metric_arm` each append **`coverage_blocked`** and **zero**
  failures — a missing witness is never a pass.
- Witness present with a wrong sha / wrong metric: each appends a real
  **`failures`** entry. The layer fails loudly in the other direction too.
- Arm audit: 102 `_sox_r94_arm` call sites (103 grep hits − the `def`), 59
  `_sox_r94_ref_arm` sites, 7 `_sox_r94_ref_metric_arm` sites (which fan out to
  **15 legs / 29 compared keys** in the receipt — the report's "7 metric
  witnesses" and "29 metric comparisons" are the same thing counted two ways).
  No arm condition is a constant or a self-comparison; every one I read
  (all 8 entries) evaluates measured data.
- PipeWire hygiene: `own_objects`/`own_modules` empty at entry **and** exit in
  all 8 entries of my run; inside the block (HEAD-blob block, 108 388 bytes)
  there are **0** `load-module`, **0** `unload-module`, **0** `pw-cli`,
  **0** `wpctl`, **0** `pw-dump`, and **0** `set-default-*` call sites (the
  token occurs once, in the header comment: "names, never set-default-*"); the
  only `pactl` uses are the read-only helper (`list short sinks|sources|modules`,
  `get-default-sink`, `get-default-source`); and no sox argv takes a device —
  every argv head is `{in}` / `-D` / `-R` / `-G` / `--no-dither` / `--version`
  (0 `-d`, 0 `-p`, 0 `play`, 0 `rec`). Live host check after my runs found
  0 `r94`-tagged sinks/sources/modules; the host defaults are unchanged from
  both the author's window and my own (`…HiFi__SPDIF__sink.29`,
  `…HiFi__Line__source.29`).

## Findings by severity

**HIGH / CRITICAL — none in the r94 diff.**

**MEDIUM — lane repo left unmerged by a concurrent r95 landing (not r94's).**
The lane repo's working tree no longer holds HEAD's fixture:
`git status` shows `UU corpus/fixtures/measure_audio.py` plus staged
`corpus/fixtures/r95jack.c` and `reports/round-95/r95-author.md`, file mtime
`2026-10-16 05:57:03 −0300` (= **08:57:03Z**, i.e. ~2 minutes *after* my
battery run and *after* my pre-state snapshot). The working file now carries
**8 conflict blocks** (`<<<<<<< ours` = the r94 sox block, `>>>>>>> theirs` = an
r95 JACK block) and `ast.parse` fails (`unmatched '}' at 33479`). Evidence that
this is not the r94 author's diff: HEAD's blob has **0** markers, the merge
`aaf56d30` is clean, and the author's commits (`f46dce00`) contain no markers.
Impact: **any fresh `--probe-sox-r94` run in this worktree now aborts** until the
r95 landing is resolved — my evidence predates it and is bound to `4808c4cf`.
I did not touch the unmerged path (zero tracked writes); the resolution belongs
to the r95/integration seat.

**LOW — the report's guard-row citation points at dev-pass numbers.**
`r94-author.md` (§ "Boundary corrections actually encoded" X1 row and § risk
list) cites the default-path railed counts as *"15092 / 14873 at the ≥ 32 767
threshold in pass 1"*. The green pass 1 receipt records
`(railed_gain12_default, railed_G_gain12_default) = (30000, 14987)`; pass 2
records `(30000, 15097)`; my run `(30000, 14981)`. The quoted pair comes from
the two **dev/iteration** receipts `…085137302309Z` (15092) and
`…085151245387Z` (14873) — which the report itself classifies as "provenance of
the iteration, not evidence". No green-ness depends on it (the legs are
`volatile_sha: true` and the only armed predicate is `c1 > 0 and c2 > 0`), but
an evidence pointer that resolves to a non-evidence pass is exactly what a
reviewer should not let stand. Related half-imprecision: the plain `gain 12`
count is **30000 in all 8 observed receipts** (5 dev + 2 green + mine) — only
the `-G` leg's count is dither-sensitive, so "the default-path railed counts are
dither-sensitive" is true of one of the two legs.

**LOW — "Implementation sha256" is the branch blob, not the lane HEAD blob.**
`r94-author.md` states `84298dcc…`; at the lane repo HEAD the fixture is
`4808c4cf…`. The r94 block is byte-identical in both and the HEAD bytes re-run
green (above), so the diff is unaffected — but the receipt carries **no
fixture-sha field** (`host` records only sox/python/numpy/loadavg), so a reader
cannot bind a receipt to implementation bytes from the receipt alone; the
binding rests on the author's archive copy plus the block-identity check. That
is a family-wide receipt-convention gap rather than an r94 regression; recording
the fixture sha in the receipt (or in `host`) would close it for every family.

**INFO — naming/prefix deviation, declared.** The family hardcodes
`SOX_R94_TAG = f"r94a_{pid}"` and `_sox_r94_scratch()` →
`live/r94-author/scratch`; changing either is a tracked edit, which this seat
may not make. The reviewer therefore ran the **committed bytes unmodified** and
honoured `r94r_` for every artifact it minted itself (`r94r_*` products,
`corpus/live/r94-reviewer/`, `corpus/live/r94r-author/`). The `r94a_` tag is a
census negative-control prefix only — the family creates **no** PipeWire object,
so no host-visible name is ever taken. (A temporary symlink
`corpus/live/r94-author → r94r-author` kept the run's products under an
`r94r`-named path; it was removed at exit.)

## Residual risk and verification gaps

- **Nondeterministic legs cannot be pinned by construction.** The 5 default-path
  determinism legs and the 2 `-G` guard legs are sha-volatile *by law*; the
  family marks them and arms only the nondeterminism predicate. Confirmed
  independently (5/5 distinct shas, 16/16 under concurrency).
- **The band estimator's calibration constant** (`SOX_R94_BAND_OFFSET_DB =
  2.5403`) is an empirical convention. It is re-armed per run by the 7 metric
  call sites (15 legs / 29 keys) against the scout's table, and my own
  independent estimator reproduced every *relative* claim (the falsification,
  the `-q` fold, the 20 kHz hole) without the constant. Absolute band values
  remain estimator-convention-dependent.
- **The scout's `-h`/`-r` headroom pair is not encoded** (declared as an
  explicit gap in the report, correctly). That row of the scout's table is
  therefore unverified by this family.
- **Cross-seat witness is conditional**: absent `corpus/live/r94-scout/receipts/`,
  66 witness arms degrade to `coverage_blocked` (honest, but the run's coverage
  shrinks). In this lane the directory is present and all 59 sha + 29 metric
  comparisons armed.
- **Host state is noisy**: loadavg ~55 with foreign seat batteries live, and the
  census `sink_total` moved 13 → 14 during the author's window (a foreign seat).
  The family's own-object negative control covers its own prefix only; content
  laws are load-independent (the r94 boundary established that, and my run
  reproduces every content byte).
- **Not verified here**: the r95/r96-r98 worktrees, and the five dev receipts
  (read only to establish the guard-row provenance above).

## Hygiene / state at exit

- Reviewer archive: `corpus/live/r94-reviewer/` — `r94r_spotcheck.py`,
  `r94r_spotcheck.json` (88 checks), `receipts/20261016T085514726246Z-sox-r94.json`,
  `r94r_probe/measure_audio.py` (HEAD-blob copy used for the import-level
  witness probe), `logs/` (pre-state, run stdout/stderr, spot-check log,
  pyc pre-state copy), `scratch/` (own stimuli + products), `manifest.sha256`
  (81 entries, manifest sha `fa923dce…`). My run's products also sit at
  `corpus/live/r94r-author/scratch/` (the family's hardcoded scratch path,
  reached through the temporary symlink).
- Tracked-write footprint of this seat: **none**. `corpus/fixtures/measure_audio.py`
  was untouched by me (the `UU` state above is the r95 landing), and the tracked
  byte-code cache is still HEAD-identical (`6e271a2d…`) because every run used
  `PYTHONDONTWRITEBYTECODE=1` — no restore was needed. The only tracked-dirty
  entries in the lane repo at exit are the r95 seat's (`UU
  corpus/fixtures/measure_audio.py`, `A corpus/fixtures/r95jack.c`,
  `A reports/round-95/r95-author.md`).
- `reports/round-94/r94-reviewer.md` (this file) is the only path this seat
  added outside `corpus/live/`; it is a new untracked file, not a modification.

*reviewer leaf — re-ran the lattice on the committed bytes; not judged, not
committed, no verdict admitted.*
