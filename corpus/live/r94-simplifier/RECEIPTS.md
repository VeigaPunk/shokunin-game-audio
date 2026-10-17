# r94s_ simplifier — live receipts index

Lane: `corpus/live/r94-simplifier/` (untracked, seat-owned; zero tracked writes).
Audited revision: `corpus/fixtures/measure_audio.py` at entry HEAD `aaf56d30`,
blob sha256 `4808c4cfb17c311204398c9858bea3582d512090cc4a075cf31c01f4a064ee26`.

The tree moved under the lane (the r95 author's JACK family landed as
`ffeb5155`, adjudicator `021bde86`); `r94s_head_021bde86.py` is that revision
(sha256 `dca4dc9bc87e006b534a50d80270bfb27492fadecfe75fbbd89f37342bd87ed7`).
The r94 block is content-identical across the move and both fold variants
re-apply to it with every anchor found exactly once.

## Scratch mirror

The fixture computes `ROOT = Path(__file__).resolve().parents[1]`, so the
scratch copy is laid out as a *mirror root* and never writes into the shared
tree:

    tree/fixtures/measure_audio.py      scratch copy of the fixture (folds applied here)
    tree/fixtures/build_artifacts.py    copied sibling (main() invokes it every run)
    tree/live/runs/                     the variant receipts
    tree/live/r94-author/scratch/       the family's own product dir (this mirror)
    tree/live/measure_audio-sox-r94.lock  the family lock (this mirror)
    tree/live/r94-scout -> ../../../r94-scout   read-only symlink: cross-seat witness

`build_artifacts.py` regenerates `tree/artifacts/` and `tree/live/round-6/`
inside the mirror (the shared `corpus/artifacts/` is untouched by this lane).

## Files

| file | what |
| --- | --- |
| `r94s_pristine.py` | the audited revision, byte-identical to HEAD's blob |
| `r94s_block_exact.py` | the extracted r94 block (lines 31091-33305 of the fixture) |
| `r94s_apply_folds.py` | the fold applier (variant A / B), anchors assert count==1 |
| `r94s_folds_variantA.diff` | variant-A diff (+43/-58, net -15 lines, 23 folds) |
| `r94s_folds_variantB.diff` | variant-B diff (+44/-63, net -19 lines, 26 folds) |
| `r94s_compare.py` | structural receipt walk (volatile-field exclusion) |
| `r94s_evidence_control.txt` | two pristine runs: the only diff is the documented dither-sensitive row |
| `r94s_evidence_variantA.txt` | baseline vs variant A |
| `r94s_evidence_variantB.txt` | baseline vs variant B |
| `r94s_evidence_arm_entailment.txt` | the A6 entailment proof (equivalent mutant) |
| `r94s_status_exit.txt` | `git status --porcelain` at exit (the r95 author's in-flight merge) |
| `r94s_baseline.*`, `r94s_foldA.*`, `r94s_foldB.*` | run stdout/stderr + wall stamps |

## Runs (all `TMPDIR=/home/vgpnk/Projects/shokunin/tmp`, `timeout 900`)

| receipt (mirror path) | fixture | legs | failures | coverage_blocked | bytes | wall |
| --- | --- | --- | --- | --- | --- | --- |
| `tree/live/runs/20261016T085541070919Z-sox-r94` | pristine | 150 | 0 | 0 | 351277 | 5 s |
| `tree/live/runs/20261016T085713383177Z-sox-r94` | pristine (control) | 150 | 0 | 0 | 351540 | 5 s |
| `tree/live/runs/20261016T085646268687Z-sox-r94` | variant A (19 folds) | 149 | 0 | 0 | 282955 | 5 s |
| `tree/live/runs/20261016T085841409268Z-sox-r94` | variant A (23 folds, final) | 149 | 0 | 0 | 282968 | 5 s |
| `tree/live/runs/20261016T085724185904Z-sox-r94` | variant B (22 folds) | 147 | 0 | 0 | 280162 | 5 s |

Wall times are the quiet-host window (05:55-05:58 local). The final variant-B
re-run started 05:58:50 into the host's stalled `pipewire-pulse` window and is
reported separately in `reports/round-94/r94-simplifier.md` (the census ladder
costs up to 12 s per `pactl` call while the daemon is unresponsive).

## Reproduce

    cd corpus/live/r94-simplifier
    cp -p r94s_pristine.py tree/fixtures/measure_audio.py
    python3 r94s_apply_folds.py A            # or B
    TMPDIR=/home/vgpnk/Projects/shokunin/tmp \
        timeout 900 python3 tree/fixtures/measure_audio.py --probe-sox-r94
    python3 r94s_compare.py <baseline.json> <variant.json>
