# audio round 72 — critic (seat: critic, leaf)

Wave `shokunin-train-20261101-w11` · lane audio · repo `audio-shokunin`
HEAD `c079aba` (untracked seat scratch only) · host: devin; tools measured
this seat: sox 14.8.0.1, ffmpeg/ffprobe n9.0.1, libsndfile 1.2.2-4,
CPython 3.14.

Scope reviewed: the r72 MOVE (`--probe-sndfile-transport-r72`, receipt
family `sndfile_*_r72_probe`, the parenthetical 3-decoder claim) against
`reports/frontier/fa-sndfile.md`, `corpus/live/frontier-sndfile/`, the
committed sox receipts, and the committed r71 ffprobe receipt. Raw evidence:
`corpus/live/r72-critic/evidence.md`; lattice re-check:
`corpus/live/r72-critic/lattice.txt`.

## Headline

The probe addition is sound in shape (mirror `ffprobe_leg`/`ffprobe_transport_entry`,
`measure_audio.py:570/:687`; wire flag/mode/suffix at `:881/:1091/:1558/:1578`).
But the **claim to test is falsified in two of its three clauses by already-committed
evidence**, and one suggested implementation shortcut (`sndfile-info` 'frames' line
as decode verdict) fabricates a transport fork. All are fixable before the
author lands; none requires rejecting the move.

## Counterexample 1 — "sndfile-only: .snd-named" is false; sox accepts the same member on the same arms

Machine-checked acceptance lattice from committed receipts
(`python3 corpus/live/r72-critic/lattice_check.py`, exit 0 — full table in
`lattice.txt`; sources: r67/r68/r69 sox receipts, r71 ffprobe receipt
`corpus/live/runs/20261014T141033155858Z-ffprobe-transport-r71/measurements.json`,
`corpus/live/frontier-sndfile/runs/sndfile-matrix.json`):

```
extsuffix_snd   sox Y--Y   ffmpeg ----   sndfile Y--Y
```

- sox, committed receipt `corpus/live/runs/20261014T140641162793Z-transport-extsuffix-snd-r69`
  (`transport_extsuffix_snd_r69_probe`): `file`/`fifo_path` → det `sndr`, exit 0,
  **samples_read 504**; `stdin_pipe`/`redirected_fd` → exit 2 `can't determine type`.
  Live re-run: `sox corpus/live/round-69/extsuffix_nomatch.snd -n stat` →
  `Samples read: 504`, exit 0.
- libsndfile: RAW|U-LAW, `read_frames` 500 on `{file, fifo_path}`, reject on
  `{stdin_pipe, redirected_fd}` (frontier matrix).

Same member, same named-vs-anonymous partition, two different mechanisms
(sox's ext-gated CHECK row vs libsndfile's post-sniff fallback). Member-level
classes on the tracked 9 are `(sox,ffmpeg,sndfile)` =
`(T,T,T)`: dec_act, dec_hcom · `(T,F,F)`: txw_piperefuse, extsuffix_f32 ·
`(T,F,T)`: extsuffix_snd · `(F,F,F)`: posttable, extsuffix_{wav,bin,txw}.
**The `(F,F,T)` sndfile-only class is empty on the tracked set** (so is
`(F,T,F)`). The only confirmed clause is `sox-only: txw-seekable (Y-Y-) /
.f32-named (Y--Y)`.

The class is instantiable — just not by the member the claim names. On the
identical 512 no-magic bytes renamed `.au` (scratch
`corpus/live/r72-critic/extsuffix_nomatch.au`): sox exit 2
`can't find Sun/NeXT/DEC identifier`; sndfile RAW|U-LAW 500 frames; ffprobe
exit 1 / ffmpeg exit 183. That is the true sndfile-only exemplar, and it sits
in the frontier's own ext sweep (`probes/extsweep.au`), outside the tracked
corpus.

## Counterexample 2 — "ffmpeg superset on detect" survives no reading, and ffmpeg's name axis is real outside the tracked names

On the tracked 9 ffmpeg accepts `{dec_act, dec_hcom}` only — strictly the
smallest accept set (⊂ sox's and ⊂ sndfile's; r71 receipt: those two members
`(wav|hcom, 0, 0)`, all others `(None, 1, 183)` on all 4 arms). So:
rejection-superset: true (ffmpeg is the strictest); detection-coverage
superset: false (ffmpeg detects nothing sox/sndfile miss; sndfile detects
`.snd`-named RAW|U-LAW and the LM8953 tier, sox detects act/txw/sndr which
ffmpeg lacks). "Superset" is backwards unless it means strictest.

Stronger: the r71/frontier line "ffmpeg tracks content, ignores the name" is
**corpus-limited**. Identical bytes renamed `.gsm`:
`ffprobe extsuffix_nomatch.gsm` → exit 0, `format_name "gsm"`, duration
0.320000; `ffmpeg -i … -f null -` → exit 0 (`Input #0, gsm … 8000 Hz mono
s16 13 kb/s`). The same bytes as `.bin2` or on `pipe:` → exit 1
`Invalid data found`; a fifo named `m.gsm` → accepted. Extension-driven
demuxer selection, i.e. a named-only ffmpeg acceptance — the same partition
shape as sox's sndr gate and libsndfile's fallback, on a name the tracked
corpus never probes. (sox on `.gsm`: exit 0 with **0 samples**; sndfile:
RAW|GSM610 2560 frames — so `.gsm` is a three-decoder *named-only* class,
not sndfile-only.) A dead `corpus/live/r71-critic/` scratch
(`misnamed.bin/.f32`, `*_asbin.bin`, no report) shows this axis was already
being probed and never landed.

Consequence for r72: do not let the receipt label `.snd` "sndfile-only", and
do not repeat "ffmpeg superset/content-only" as a confirmed clause. The
defensible statement is: *on the tracked 9, ffmpeg is the strictest decoder
(reject ⊇ both) and transport-invariant; off-corpus, all three decoders have
name-gated acceptances, so "name-insensitive" is not a decoder property.*

## Counterexample 3 — the MOVE's suggested `sndfile-info` 'frames' shortcut is not a decode verdict

Measured (`evidence.md` E5): `sndfile-info extsuffix_nomatch.snd` prints
`Frames : 512`, while `sf_readf_short` drains **500** frames (single call =
drain = 500; `drain_check.py`, exit 0). On the fifo, `sndfile-info` prints
`Frames : unknown` (ctypes: `9223372036854775807`), read still 500. A
frames-line decode leg would therefore report 512 vs unknown — a transport
fork manufactured from a length *estimate* where the decode is invariant
500/500. Size sweep: 256→frames 256/drained 244; 1024→1024/1012; 2048→1024/1012.
The decode leg must be the sf_read count (frontier ctypes pattern), recorded
*alongside* `frames`, never instead of it.

## Other measured traps for the author (all fixable, all cheap)

- `sndfile-info` **exits 0 on reject** (`posttable_nomatch.wav` → exit 0,
  verdict only in stdout) — receipt verdicts cannot key on exit code.
- FIFO basename must keep the member extension: my first fifo attempt
  (`…/m.fifo`) made sox answer `no handler for file extension \`fifo'`;
  the r71 arm's `feed=(tmp, path.name, …)` pattern is the correct one.
- Anonymous arms must be `sf_open_fd(dup(fd))` (frontier `leg_fd`), not a CLI
  path. `sndfile-info /dev/stdin` is a *named* path (basename `stdin`); it
  happens to reject here, but it falsifies the `named` flag and the
  "no name at all" boundary the frontier measured.
- Path-bearing text must be normalized: `sndfile-info` stdout contains
  `File : <path>` and `Error : Not able to open input file <path>.` — use
  the r71 `_tail()` pattern (`measure_audio.py:646-651`), or the family is
  not replay-stable (r71 D2, `reports/round-71/r71-verifier.md:91`).
- Wire `mode` + run-dir `suffix` in the same change (r71 D1,
  `r71-verifier.md:82`); the r71 family is now byte-stable — the r72 family
  must be too (two consecutive runs, byte-identical).
- Pin `sf_version_string()` (`libsndfile-1.2.2`) in the entry: the `.snd`
  fallback set and the `unimplemented format` tier are compile-time build
  properties (frontier "Unresolved/limits"), so an unversioned receipt cannot
  support a cross-build claim. Also: `ports/frontier/fb-pipewire.md` measured
  that pw-cat's decode layer **is** libsndfile — do not later count pw-cat as
  a fourth independent decoder.
- Implement the ctypes legs inside `corpus/fixtures/` (single authority); do
  not import `corpus/live/frontier-sndfile/probe_sndfile.py` (seat scratch).
- Number to fix: `reports/frontier/fa-sndfile.md:65` says `.f32` "decode 75";
  the committed receipt (`…T140639114072Z-transport-extsuffix-f32-r69`) and a
  live re-run both say **128** (75 is the r69-scout zero-bytes
  pre-measurement, `r69-scout.md:99`). The r72 report must cite 128.

## Impacted axes

- **coverage** — the decoder-coverage lattice is the round's headline; as
  claimed it asserts a non-empty class the receipts show empty, and omits the
  one axis (ffmpeg extension-driven accept) that breaks the r71
  "content-only" story.
- **calibration** — class labels are claims: they must be computed from the
  measured per-member accept vectors (`lattice_check.py` is the pattern), not
  copied from the brief's parenthetical; "0 samples, exit 0" (sox `.gsm`)
  needs an explicit acceptance criterion (≥1 decoded frame), stated in the
  receipt.
- **provenance** — version-pinned decoder identity, API-boundary anonymous
  arms, and single implementation authority; the untracked dead r71-critic
  scratch shows what happens when a name-axis probe lands nowhere.

## Smallest safe correction

1. Keep the move: `--probe-sndfile-transport-r72`, insertion-only, ctypes
   `sf_open`/`sf_open_fd` + full-drain `sf_readf_*`; per entry record
   `path`, `pair_member`, `decoder: "libsndfile"`, `sf_version_string`,
   per-arm `format`/`format_name`/`frames`/`read_frames`/`error`/
   `sf_seekable`, transport groups + fork pin; fifo arm with `path.name`;
   path-normalized tails; mode/suffix wired.
2. Restate the claim to the measured partition (4 non-empty classes; `.snd`
   = sox+sndfile name-gated, different mechanisms; sndfile's r72-unique
   contributions = the `unimplemented format` tier and the post-sniff
   fallback mechanism, not an exclusive acceptance class), and record the
   falsification of "sndfile-only: .snd-named" and "ffmpeg superset on
   detect" in the round report — a falsified clause with receipts is the
   round's deliverable, not a defect to hide.
3. If a tracked sndfile-only class is wanted, add one member in a later,
   all-three-arms round (`.au`-named copy of the same 512 bytes: sox reject /
   sndfile accept / ffmpeg reject, measured above) — do not relabel `.snd`
   and do not add it to only the sndfile arm.
4. Verify: two consecutive r72 runs byte-identical; prior rows (r67–r71)
   byte-stable (r71 arm's own replay is the control); no new absolute/tmp
   paths in the receipt.

Tradeoff the canonical judge must reject if shipped as-is: the parenthetical
claim as written (two clauses false), a decode verdict derived from the
`sndfile-info` frames line, and any silent member-set change that makes the
sndfile-only class non-empty without re-measuring sox and ffmpeg on the new
member.

Files written (this seat): `reports/round-72/r72-critic.md`;
`corpus/live/r72-critic/{evidence.md,lattice.txt,lattice_check.py,drain_check.py,extsuffix_nomatch.{au,gsm,vox,bin2}}`.
No git mutations; no writes outside scope. Stop.
