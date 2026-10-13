# Round 63 — simplifier: minimal-design critique of the `act`-predicate pin

Seat: **simplifier** (leaf, report-only — no tracked edits). Host: devin. Worktree
`~/Projects/prymeagnt/audio`; `.shokunin/audio/` → `~/Projects/shokunin/audio-shokunin`
(canonical repo, HEAD `3c96a69` = r62 closeout). Brief: critique the author's landed r63
diff when it appears; judge smallest discriminating variant set, probe-mode wiring,
cheaper predicate-pinning controls; name anything deletable without losing the
falsification.

**Landing status at write time**: the author's diff landed during this review — first
as working-tree modifications (`M corpus/fixtures/build_artifacts.py` +32/−1,
`M corpus/fixtures/measure_audio.py` +25/−4), then committed as work commit
`1a97b0e` ("audio r63: act autodetect predicate pinned — RIFF@0 AND file[256]==0x84";
verified `git diff 3c96a69..1a97b0e` numstat identical to the reviewed diff). Also
landed: `corpus/live/round-63/pair_route_{84,00}.wav`, the author's 86-command ledger
receipts under `corpus/live/runs/20261013T234*`, and all seat scratch dirs (my own
scratch was swept into that commit — normal wave integration, not my action). I
critique the committed r63 diff directly. My independent verification ran in
`corpus/live/r63-simplifier/scratch/` (scripts + `value_sweep.tsv` + mutant WAVs).

## TL;DR verdict

- **The landed pair is the smallest receipt-bearing discriminating set**: one emitted
  file per route (`pair_route_84.wav` / `pair_route_00.wav`), sole diff = byte 256.
  I reconstructed the generator's blob in-memory byte-for-byte — emitted SHAs match
  (`cf5edecce1812f0a…` / `cb77db319a7a79…`), `diff offsets: [256]` only.
- **Only deletable token in the diff**: the `stat` effect in the route probe
  (`sox -V6 <path> -n stat`). `sox -V6 <path> -n` already emits both consumed markers
  (`detected file format type '…'`, `(ffmpeg)`); `stat` adds a full redundant decode.
  Cosmetic — zero risk either way.
- **One arguable tracked-coverage gap, not a defect**: the pair pins *value* at offset
  256 inside receipts; the *position* axis lives only in scratch (23,738-row matrix).
  A third emitted cell (`b256=0x00, b257=0x84` → native reject) would pin adjacency in
  a receipt for ~+12 lines. Optional; the pair alone already satisfies "land a tracked
  sweep-matrix control".
- **Two documentation/label nits**: the builder comment "all 256 values x all 11,588
  positions" reads as a cross product (~2.97 M cells); what ran is the *separable*
  1-D sweeps (256 values @ 256 + 11,588 positions @ 0x84) — which is exactly the
  minimal complete matrix for a conjunctive predicate. And `results.tsv`'s `route`
  column labels detected-`act`-but-ffmpeg-failed cells (e.g. `v17_c_wave8`) `native`.
- Nothing else in the +57/−5 is deletable: every added symbol is referenced by the
  new ledger rows 02–03.

## Independent pin of the predicate (needed to judge "smallest")

Source ground truth (boundary seat's fetched tree, read-only):
`corpus/live/r63-boundary/src/sox_ng/src/formats.c:71-97` —
`CHECK(act, 0, 4, "RIFF", 256, 1, "\x84")` expands to
`len >= 257 && data[256]==0x84 && data[0..3]=="RIFF"`, evaluated strictly before the
three `wav` checks; `AUTO_DETECT_SIZE` is 257 *because of* act (`:61`).

My own probes (`scratch/sweep_values.py`, `sweep_positions.py`; probe =
`sox -V3 <mutant> -n`, `base.wav` = committed `corpus/live/round-61/pair_valid_17.wav`,
SHA `15cadf24…`, native byte 256 = `0x84`):

| axis | experiment | observed |
|---|---|---|
| value @ 256 | all 256 values, in-place mutation | `act` exit 0 for **exactly 0x84**; `wav` exit 2 for all 255 others — no format escapes (`value_sweep.tsv`, 256 rows) |
| position | 0x84 relocated to {68,128,200,255,257,260,324,384,512,1024,8191,11587}, byte 256 → 0x00 | all `wav` exit 2 — position is file-absolute 256 only |
| neighbors | 0x84 at 255 **and** 257, byte 256 → 0x00 | `wav` exit 2 — not "0x84 anywhere adjacent" |
| RIFF gate | `R`→`X` @0, keep b256=0x84 | detected `NONE` exit 2 ("RIFF header not found" via extension fallback) — RIFF is a required conjunct |
| WAVE gate | `W`→`X` @8, keep RIFF + b256=0x84 | detected **`act`** exit 2 (ffmpeg then EOFs on the broken header) — WAVE is *not* required by the predicate |
| RIFF variants | `RIFX` / `RF64` @0-3, keep b256=0x84 | detected `wav` both — predicate wants literal `RIFF`, not the wav-check family |
| length floor | truncate to 257 B (b256=0x84) → `act` exit 0; truncate to 256 B (0x84 @255) → `wav` exit 2 | `len >= 257` is a real conjunct; position isn't "last byte" |
| preemption | `FSSD`@65-68 + `HCOM`@128-131 (hcom check, formats.c:90) or `ring.bin\0`@16-24 (gsrt check, :81), keep b256=0x84 | detected `hcom` / `gsrt` — **earlier checks still outrank act**; single-byte sweeps can't see this |
| `--i` marker | `sox --i base.wav` | `Input File : 'base.wav' (ffmpeg)` — the observable bridge marker |

Convergent with the author's `results.tsv` (23,738 rows: `v17/v16_fullpos` 11,588 each,
`v17/v16_fullval` 256 each, ~40 controls; exactly **21** `act` cells — one per sweep
family plus structural cells) and with critic's `E_{gsrt,hcom}_*`, `D_rifx_*`,
`G_trunc*` exhibits — three independent derivations agree.

Refined claim the evidence supports: **`file[0..3]=="RIFF" ∧ file[256]==0x84 ∧
len≥257` selects `act`/`(ffmpeg)`, provided no earlier CHECK fires** — on RIFF files the
only reachable preemptors are `gsrt` (16–24, NUL-terminated) and `hcom` (65–68 + 128–131).

## Landed diff audit — deletability

`build_artifacts.py` +32/−1: `build_ui_route_act_r63_probe()` synthesizes a fresh
valid17-extensible blob (920 Hz + 1380 Hz, amp 8191) and emits the byte-256 pair; two
argparse flags; one dispatch branch (newest-first, convention). `measure_audio.py`
+25/−4: two flags, sum-list entries, forwarding, one ~13-line measurement block that
runs `sox -V6 <path> -n stat`, calls `measure()`, converts `CalledProcessError` into a
receipt entry (`sox_exit_code`, `sox_stderr`, failure `decode: default SoX route
rejected input`), and annotates `sox_detected_format` / `sox_route` on both legs.

- **Smallest discriminating variant set?** Yes for a receipt-bearing control. The
  claim is a *flip* — it needs one positive leg (0x84 → act → decode → 4-failure
  measurement) and one negative leg (0x00 → wav → fatal reject → rejection receipt).
  Verified against the author's real receipts: `runs/20261013T234233555211Z-ui-route-act-84-r63`
  carries `sox_detected_format:"act"`, `sox_route:"ffmpeg"`, the r61-shape 4 failures;
  `…234234583776Z-ui-route-act-00-r63` carries `"wav"`/`"native"`/`sox_exit_code:2`.
  The try/except is load-bearing (r62-simplifier showed `check=True` turns a native
  reject into a runner crash, no receipt); `exc.stderr.decode()` is safe —
  `command()` uses `capture_output=True` (line 37). Imports `re`/`subprocess`
  pre-exist (lines 7–8). No dead code anywhere in the diff.
- **Generator**: pinning byte 256 by *assignment* (`variant[256] = byte`) is a genuine
  simplification vs r62's f2-sweep-until-0x84 — same guarantee, less machinery. The
  payload's natural byte 256 is `0x5c`, so both assignments are real edits.
- **Probe-mode wiring minimal?** Yes within convention, with one deletable token:
  `stat` in the route probe. Verified `sox -V6 route_84.wav -n` prints
  `detected file format type 'act'` and `Input File … (ffmpeg)` with no effect —
  `stat` only makes the probe re-decode 11,520 B whose decode `measure()` already
  proves on the -84 leg (and never runs on the -00 leg, which fails at open).
- **Cheaper controls considered, all rejected as net-worse**:
  (a) *zero new fixtures* — mutate the committed `pair_valid_17.wav` in-runner; saves
  the ~24-line builder but adds mutation logic to `measure_audio.py` and loses emitted
  SHA-citable fixtures — worse transparency per line saved.
  (b) *one flag, both files* — `--probe-ui-route-act-r63` measuring the pair into a
  single receipt saves ~6 wiring atoms AND captures the contrast atomically; it breaks
  the per-variant ledger symmetry the verifier replays (84 prior rows are all
  one-flag-one-file). Viable, not required.
  (c) *probe mode necessity itself* — satisfied: the receipt is now the only place
  `sox_route` is durably recorded; a pure knowledge note would leave the ledger without
  the claimed evidence.

## Nits (reported, none falsification-affecting)

1. Builder comment "all 256 values x all 11,588 positions" — the measured matrix is
   separable (256 values **at** 256; 0x84 relocated across all 11,588 positions).
   For a conjunction of independent byte conjuncts that *is* the minimal complete
   cover; a 256×11,588 product adds zero discriminating power. Phrasing only.
2. `results.tsv` `route` column: `"ffmpeg" if "(ffmpeg)" in err else "native"` — but
   `(ffmpeg)` is emitted only on successful input-open, so detected-`act` cells whose
   ffmpeg pipe then fails (`v17_c_wave8`, `v16_c_wave8`) are labeled `native`.
   `detected` is the authoritative column; scratch-level label nit.
3. The `-00` receipt's `sox_stderr` embeds the absolute repo path
   (`/home/vgpnk/Projects/shokunin/…`) — the same byte-determinism wrinkle r62-baseline
   flagged in `--probe-invalid`'s ffprobe stderr: receipts are byte-identical only
   under the same checkout path. Optional fix: `.replace(str(ROOT), "$ROOT")` on the
   captured stderr — one line, makes the receipt location-independent.
4. Optional strengthening: a third emitted cell `pair_route_pos257.wav`
   (b256=0x00, b257=0x84) would make the *position* axis receipt-covered, not just
   scratch-covered — ~+12 lines (1 flag set + 1 emission + ternary heads). The 2-cell
   landing is already sufficient for the declared "tracked sweep-matrix control".

## r62 additions retro-check

What actually landed from r62's 23-variant exploration was only the `pair_valid_{24,32}`
bracket + 2 modes (+28/−1, +13/−4) — the minimal discriminating pair for the
s24→s32 boundary, matching last round's recommended trim. Nothing retroactively
deletable; the r63 diff touches none of it.

## Housekeeping / scope

All findings host-specific (SoX_ng 14.8.0.1 + ffmpeg/ffprobe n9.0.1); no
standards/other-version inference. No commits, no pushes, no subagents, no sibling
writes. Writes this round: this report + `corpus/live/r63-simplifier/scratch/`
(`sweep_values.py`, `sweep_positions.py`, `value_sweep.tsv`, mutant WAVs, reconstructed
`route_{84,00}.wav`). `git status` still shows only the author's two modified `.py`
files + mechanical `.pyc` churn; I restored nothing and touched nothing tracked.
