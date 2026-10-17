# r92-verifier evidence (mirror)

Small-file mirror of the r92 verifier gate. The report is
`reports/round-92/r92-verifier.md`.

Full evidence (the two frozen trees, both 3.2 GB, and the raw capture WAVs)
lives at **`/home/vgpnk/r92-verifier/`** — the archive root the assignment
named ("git archive HEAD to /home"):

| path | what |
| --- | --- |
| `/home/vgpnk/r92-verifier/tree-r92/` | `git archive ccbce758` (the r92 landing; mint-time HEAD) |
| `/home/vgpnk/r92-verifier/tree-head/` | `git archive b8ff4efc` (current HEAD at archive time, r97) |
| `/home/vgpnk/r92-verifier/scratch/runA/`, `runB/` | every stimulus, IR fixture and captured WAV (96 files each) |
| `/home/vgpnk/r92-verifier/runs/` | law set, censuses, forged receipts, mutation outputs, run stdout |

This mirror carries: both run receipts (`receipts/`), the independent law set
and its results for five receipts (`laws/`), the cross-run/cross-seat/census
tables (`census/`), and the mutation + forgery controls (`controls/`).

Nothing here is committed; `corpus/live/**` is untracked evidence by project
convention.
