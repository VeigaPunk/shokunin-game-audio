# R63 baseline — frozen before-state replay of the 84-command battery

Seat: baseline (scout role), audio lane round 63, host devin. Leaf: no
subagents, no git mutation, no writes outside
`corpus/live/r63-baseline/` and this report.

## Frozen snapshot method

- `git -C ~/Projects/shokunin/audio-shokunin archive HEAD | tar -x -C
  corpus/live/r63-baseline/tree` at HEAD
  `3c96a69fcf298f60d53023225d9b268e8f625410` ("audio r62 adjudication:
  ADMIT — LOG/SCORECARD/verifier+adjudicator reports, r61 pin
  correction"). Corpus/fixture state is the r62 work commit `cbe763e`
  plus the adjudication commit's reports/receipts only. Extracted tree
  ≈ 103 MB incl. 2,707 tracked historical `live/runs/` receipts (up from
  2,453 at r62 baseline — r62's 84 author + 84 verifier + adjudicator
  re-run receipts are now committed history).
- **The frozen copy runs standalone.** `measure_audio.py`/
  `build_artifacts.py` resolve `ROOT`/`OUT` via
  `Path(__file__).resolve().parents[1]`; fixture reads, probe rebuilds,
  and receipt writes stay under `…/r63-baseline/tree/corpus/`. Host tools:
  ffprobe n9.0.1, ffmpeg n9.0.1, SoX_ng v14.8.0.1, python3 3.14.7 +
  numpy 2.5.3 — identical toolchain to r62. Extracted
  `corpus/fixtures/measure_audio.py` / `build_artifacts.py` hash to the
  HEAD blob IDs `1858baf6` / `750d29b4` (`git hash-object` ==
  `git rev-parse HEAD:`) — byte-faithful snapshot.
- `--runs` note: `measure_audio.py` at HEAD still has **no `--runs`
  flag** — it hard-writes `ROOT/live/runs/<stamp>-<suffix>/
  measurements.json`. Under the frozen tree that root is inside my
  scratch dir, so all receipts stayed in scope. Command mapping: the r62
  ledger ran `python3 .shokunin/audio/corpus/fixtures/measure_audio.py`
  from the prymeagnt worktree; the frozen replay ran
  `python3 corpus/fixtures/measure_audio.py` from the tree root —
  identical flag sequence, byte-identical script content.

## Battery reconstruction

The 84 commands were taken verbatim from
`corpus/live/r62-author/scratch/run_ledger.sh` / `ledger-r62.tsv` — the
r62 designated ledger (bare normal at position 1, the two r62 modes at
positions 2–3, `--probe-invalid` at 79, five trailing normals at 80–84,
76 other `--probe-*` flags). All 84 flags exist in HEAD argparse
(verified against `measure_audio.py` `add_argument` list). Run serially
once each from the tree root by `cmdlog/battery.sh`; per-command
stdout/stderr/exit captured under `cmdlog/NN.{stdout,stderr,exit}`;
row ledger `cmdlog/ledger-r63-baseline.tsv`. A bare-normal standalone
smoke run preceded the battery (exit 0, receipt
`20261013T233637010688Z-normal`) — same convention as r62 baseline.

## Observed before-state receipt summary

- Runs-dir census: 2,707 pre-existing dirs → **2,792** = exactly 85 new
  (84 battery + 1 smoke), monotonically stamped
  `20261013T233646294882Z`–`20261013T233816766176Z` for the battery
  (~90 s wall), zero duplicate receipt paths, zero extras, zero
  pre-existing paths reused; all 84 receipt paths exist under the frozen
  tree (84/84 ledger `receipt` fields resolve), all 84 stdout payloads
  parsed as JSON, all 84 stderr files empty.
- **Exit codes: 43 exit 0 / 41 exit 1** — identical shape to the r62
  designated ledger. **84/84 exit codes match the r62 author ledger
  row-for-row** (`ledger-r62.tsv` positional compare). All exit-1 rows
  are expected validation outcomes recorded in receipts, not
  decoder/setup failures.
- **Receipt byte-compare vs the r62 committed receipts** (tracked inside
  the frozen tree, positional match on dir-name suffix — 84/84 suffixes
  match): **83/84 `measurements.json` byte-identical**. Sole exception
  is command 79 `--probe-invalid`
  (`…233811611451Z-invalid`), differing only in the ffprobe stderr
  string embedded for the `corrupt` probe: it carries the frozen-tree
  absolute path `…/r63-baseline/tree/corpus/live/round-6/corrupt.wav`
  where the committed receipt has `…/audio-shokunin/corpus/live/
  round-6/corrupt.wav`. Same file, same `decode`/`expected_failure`
  classification, same exit code; location-dependent string, not a
  numeric or gate difference — the same divergence class the r62
  baseline and r62 reviewer both recorded (pre-existing since the repo
  extraction).
- Key receipt SHA-256 (frozen replay):
  - `233647488812Z-ui-extensible-valid-24-r62`
    `0d1b61367cd5e3330354c3e2aa5fadf4da2c28c607bb39cbb3645cd613410754`
  - `233648688198Z-ui-extensible-valid-32-r62`
    `fe6cc56120d89fbbd76e931e6b73defb6ea983421fcea8cb8451f6979db42578`
  - `233649817872Z-ui-extensible-valid-17-r61`
    `d6eca5a298b2e88d9179868fa2f5f5968ecba85d0dd422b1bd51353e4eabf9f2`
    — identical digest to the r62 baseline's frozen replay of the same
    mode (byte-identical receipts hash identically).
  - `233650929378Z-ui-extensible-valid-16-r61`
    `4d5c909e0557d31113bef6d566c6fa9eafdb994a7cfa0e61f398d8c9015aeff3`
    — likewise identical to r62 baseline.
  - all six battery normals share
    `8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732f09ffaffb1b`
    — byte-identical to the r62 verifier normal
    `230948252481Z-normal` and the r62/r61 normal lineage.
  - `233811611451Z-invalid`
    `4f0fe973f4511833dffeb77917cf42a10e9c3c4e73c0960293c32eebdb6b9adb`
    (differs only as noted).
- R62 probe behavior reproduced in the frozen tree: command 02
  `--probe-ui-extensible-valid-24-r62` → exit 1, sole failing entry
  `ui_extensible_valid_24_r62_probe` = `format: expected PCM16`,
  `duration: outside ±1 ms`, `level: clipping headroom or near silence`,
  `spectrum: centroid outside fixture band`; command 03 valid32 → exit 1
  with `format: expected PCM16`, `duration: outside ±1 ms`; command 04
  valid17 → exit 1 with the same four-failure set as valid24. Command 05
  valid16 → exit 0 clean.
- **Before-state mechanism anchors for the r63 depth claim** (the
  byte-256 `act` autodetect collision): in the frozen tree, payload byte
  256 = `0x84` on both `corpus/live/round-61/pair_valid_17.wav` and
  `corpus/live/round-62/pair_valid_24.wav` (`xxd -s 256 -l 1 -p` →
  `84`). `sox -V6 pair_valid_17.wav -n` → `detected file format type
  'act'`, `Input File … (ffmpeg)`; `sox pair_valid_17.wav -t f32 -` →
  15356 B (3,839 f32, the packet-residue signature); `sox
  pair_valid_32.wav -t f32 -` → 11520 B (2,880, exact w=4 divide).
  Fixture SHAs: `pair_valid_17.wav`
  `15cadf242eff13ede3ff25b992f4410ec89a76a9814e2afad346b4052eb63fe4`,
  `pair_valid_24.wav`
  `29e855324f9671a20367b602bb9c52055737d91553a3b08e34a088640f9199aa`,
  `pair_valid_32.wav`
  `796511768ad4b76140b699666f9d5601f8ef9477d37aca3eaea02fd55db847b5`
  — all match the committed r61/r62 values.

## Scope notes and unknowns

- Baseline only: this replay establishes the committed before-state
  (HEAD `3c96a69`) against which the r63 author move — mapping the
  `act` autodetect byte predicate — will be judged. It does not attempt
  the byte-position/value sweep itself; it confirms the frozen tree
  reproduces the collision state the sweep starts from (byte 256 `0x84`,
  `act` route, ffmpeg bridge, packet-residue decode counts).
- Receipt JSON equality is computed against the r62 author's *tracked*
  receipts inside the frozen tree — an offline comparison; no live-repo
  receipts were read into the result set beyond that snapshot.
- Live-repo writes performed: only `corpus/live/r63-baseline/**` (tree,
  cmdlog, ledger) and this report.
- Concurrency disclosure: `git status` during my run shows sibling seats
  active — untracked `corpus/live/r63-{author,boundary,critic,reviewer,
  scout,simplifier}/` scratch dirs, plus an in-place 84-command replay
  writing untracked `corpus/live/runs/20261013T233617…`–`…233644…` dirs
  in the live repo (stamps precede/overlap my battery window
  `233646…`–`233816…`; those live-tree dirs are not mine). By report
  time the live working tree also carries the r63 **author's**
  in-progress tracked-writer edits (` M corpus/fixtures/
  build_artifacts.py` +33/−1-ish, ` M measure_audio.py` +29/−4, ` M
  __pycache__/build_artifacts.cpython-314.pyc` — the expected
  author-diff shape, uncommitted). My frozen tree under
  `r63-baseline/tree/` is a tar extraction of HEAD `3c96a69` and cannot
  be contaminated by in-place or working-tree writes — the before-state
  it replayed is the committed state, not the author's pending edit.
  None of the live-tree modifications are mine; my only live-repo
  writes are `corpus/live/r63-baseline/**` and this report.
- Unknowns carried into r63 unchanged: which byte positions and values
  at/near offset 256 flip `act` autodetect on this file family (the
  declared sweep), and the pre-existing `--probe-invalid` path-string
  divergence — recorded, not a gate difference.
