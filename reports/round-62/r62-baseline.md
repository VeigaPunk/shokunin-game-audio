# R62 baseline — frozen before-state replay of the 82-command battery

Seat: baseline (scout role), audio lane round 62, host devin. Leaf: no
subagents, no git mutation, no writes outside
`corpus/live/r62-baseline/` and this report.

## Frozen snapshot method

- `git -C ~/Projects/shokunin/audio-shokunin archive HEAD | tar -x -C
  corpus/live/r62-baseline/tree` at HEAD
  `1c52c7d074ed693f9d4ea98e5f9fea4cc204c8cd` ("Revert HOURS.md…";
  corpus state identical to r61 work commit `04b4bd4` — `git diff
  04b4bd4..HEAD -- corpus/fixtures corpus/artifacts` is empty; the only
  later corpus-touching commit `e1ac349` added two adjudicator receipts).
  Extracted tree ≈ 89 MB incl. 2,453 tracked historical `live/runs/` receipts.
- **The frozen copy runs standalone.** `measure_audio.py`/`build_artifacts.py`
  resolve `ROOT`/`OUT` via `Path(__file__).resolve().parents[1]`, so all
  fixture reads, probe rebuilds, and receipt writes stay under
  `…/r62-baseline/tree/corpus/`. Host tools: ffprobe n9.0.1, SoX_ng v14.8.0.1,
  ffmpeg, python3 + numpy 2.5.3. No in-place replay needed; concurrent
  author edits cannot contaminate the snapshot (extraction, not worktree).
- `--runs` note: `measure_audio.py` at HEAD has **no `--runs` flag** — it
  hard-writes `ROOT/live/runs/<stamp>-<suffix>/measurements.json`. Under the
  frozen tree that root is inside my scratch dir, so all 82 receipts stayed in
  scope. Command mapping: the r61 ledger ran
  `python3 .shokunin/audio/corpus/fixtures/measure_audio.py` from the prymeagnt
  worktree; the frozen replay ran `python3 corpus/fixtures/measure_audio.py`
  from the tree root — identical flag sequence, byte-identical script content.

## Battery reconstruction

The 82 commands were taken verbatim from `reports/round-61/r61-verifier.md`'s
designated ledger (6 bare normal runs at positions 1, 78–82, `--probe-invalid`
at 77, and 75 `--probe-*` flags). All flags exist in HEAD argparse. Run
serially once each from the tree root; per-command stdout/stderr/exit captured
under `corpus/live/r62-baseline/cmdlog/NN.{stdout,stderr,exit}`; the driver is
`cmdlog/battery.sh` (command 01 run manually first as the standalone smoke
test — exit 0).

## Observed before-state receipt summary

- Runs-dir census: 2,453 pre-existing dirs → exactly **82 new dirs**,
  one per command, monotonically stamped `20261013T220326169413Z`–
  `20261013T220553914971Z` (~2.5 min wall). Zero duplicates, zero extras,
  zero pre-existing paths reused; all 82 receipt paths exist under the frozen
  tree; all 82 stdout payloads parsed; all stderr files empty.
- **Exit codes: 43 exit 0 / 39 exit 1** — identical shape to the r61
  designated ledger. Exit-1 commands: 02, 16, 18, 20, 22, 24, 26, 28, 31, 32,
  35, 37, 38, 41, 43, 45, 47, 49, 51, 52, 54, 56, 58, 60, 62, 63, 65–77 —
  the same positions as the verifier table; all are expected validation
  outcomes recorded in receipts, not decoder/setup failures.
- **Receipt content equality vs the r61 designated ledger** (which is itself
  tracked inside the frozen tree): all 82 new dirs match their positional
  verifier counterpart on dir-name suffix; **81/82 `measurements.json` are
  byte-identical**. The single exception is command 77 `--probe-invalid`
  (`…220548878291Z-invalid`), which differs only in the ffprobe stderr string
  embedded for the `corrupt` probe: it carries the frozen-tree absolute path
  `…/r62-baseline/tree/corpus/live/round-6/corrupt.wav` where the verifier
  receipt has `…/prymeagnt/audio/.shokunin/audio/corpus/live/round-6/
  corrupt.wav`. Same file, same `decode` classification, same exit code;
  location-dependent string, not a numeric or gate difference.
- Key receipt SHA-256 (frozen replay):
  - `220428883541Z-ui-extensible-valid-17-r61` `d6eca5a298b2e88d9179868fa2f5f5968ecba85d0dd422b1bd51353e4eabf9f2`
  - `220429961572Z-ui-extensible-valid-16-r61` `4d5c909e0557d31113bef6d566c6fa9eafdb994a7cfa0e61f398d8c9015aeff3`
  - normal receipts (all six, first `220326169413Z-normal` through last
    `220553914971Z-normal`) share `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`
    — byte-identical to verifier normal `165521565727Z-normal`.
  - `220548878291Z-invalid` `f3e6bb6ba1b60b369cfb45ff5db173a99dc54a00b38c6b4a7b55c8de60081670` (differs only as noted).
- R61 probe behavior reproduced in the frozen tree: command 02
  `--probe-ui-extensible-valid-17-r61` → exit 1, sole failing entry
  `ui_extensible_valid_17_r61_probe` = `format: expected PCM16`,
  `duration: outside ±1 ms`, `level: clipping headroom or near silence`,
  `spectrum: centroid outside fixture band`; probe stream `pcm_s24le`, 24
  bits, duration `0.08` s, peak `0.992279052734375`. Command 03 valid16 →
  exit 0 clean. The builder's deterministic regeneration in the frozen tree
  produced `pair_valid_17.wav` `15cadf242eff13ede3ff25b992f4410ec89a76a9814e2afad346b4052eb63fe4`
  / `pair_valid_16.wav` `2c5e244fb19bed5f6abdaa605ae503dd6685f88cb440de93a4cd313959591d00`
  — the published r61 SHAs. Command 77's stdout reproduces the eight-entry
  invalid battery (`section count`/`decode`/`format`/`section count`/
  `null`/`format`/`format`/`format`).

## Scope notes and unknowns

- Baseline only: this replay establishes the committed before-state against
  which the r62 author move will be judged. It does not attempt the
  discriminating controls for the r61 SoX 3,839-vs-3,840 decode-length
  UNKNOWN; it only confirms the frozen tree reproduces the state in which
  that UNKNOWN was recorded (valid17 reclassifies to `pcm_s24le`/0.080 s
  everywhere measured).
- Receipt JSON equality is computed against the verifier's *tracked* receipts
  inside the frozen tree — an offline comparison; no live-repo receipts were
  read into the result set beyond that snapshot.
- Live-repo writes performed: only `corpus/live/r62-baseline/**` (tree,
  cmdlog, this battery's inputs) and this report. Sibling scratch
  `corpus/live/r62-boundary/` (untracked, pre-existing) was not touched.
- Concurrency disclosure: `git status` shows a sibling seat ran the same
  82-command battery **in-place** in the live repo during my replay window
  (82 new untracked `corpus/live/runs/20261013T220247…`–`…220413…` dirs,
  overlapping but disjoint from my frozen run `220326…`–`220553…`), plus
  other lanes' `corpus/live/r62-*/` scratch dirs. None of that is mine; my
  frozen tree under `r62-baseline/tree/` is a tar extraction and cannot be
  contaminated by in-place writes. No tracked file shows modified.
- Remaining unknowns for the depth question are unchanged from r61: the
  ffmpeg 17→24-bit rounding rule provenance, the SoX one-frame shortfall,
  other >16 valid-bits values, and the `--i` vs decode inconsistency —
  all still open; nothing in the frozen battery bears on them.
