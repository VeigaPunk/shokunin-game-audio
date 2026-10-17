# r91 verifier — receipts

Seat: verifier (non-author). Basis: `git archive HEAD` at 2026-10-16T10:01:0xZ
(HEAD then `7358f13b`, r96 author; the r91 landing is `d78f1cc9`) extracted to
`/home/vgpnk/r91-verify-tree`. Report: `reports/round-91/r91-verifier.md`.
Zero tracked writes, zero commits, no `set-default-*`.

| file | what it is |
| --- | --- |
| `identity.txt` | archive/HEAD, tar sha, file census, fixture + block + dispatch byte-identity, wiring, foreign state |
| `preflight-run1.txt`, `preflight-run2.txt` | host state (loadavg, defaults, r91 residue) before each battery run |
| `run1.stdout.json`, `run1.stderr.log` | battery run 1 — **RED** (`c_alive`), receipt `20261016T100257559587Z-gstfrz-r91` |
| `run2.stdout.json`, `run2.stderr.log` | battery run 2 — green, receipt `20261016T100551473978Z-gstfrz-r91` |
| `runs/20261016T100257559587Z-gstfrz-r91/measurements.json` | the full red receipt (copied from the frozen tree) |
| `runs/20261016T100551473978Z-gstfrz-r91/measurements.json` | the full green receipt (copied from the frozen tree) |
| `derive.py`, `derive-run1.txt`, `derive-run2.txt` | independent 128-check re-derivation of the 15 legs + fixture process (run 2: 128/128; run 1: 125/128 = the family's own red cells) |
| `diag_clock.py`, `diag1..3.json/.out` | clock entry instrumented (target sink liveness per sample + per leg) — 3/3 green |
| `repeat_clock.py`, `repeat_clock.json/.out` | 6 committed clock-entry repeats — 6/6 green (flake rate probe) |
| `diag_family.py`, `fam1..4.json/.out` | full-family replays in battery order, clock legs instrumented — fam3 **RED** (`s_norelink` third shape); fam1/fam2/fam4 green (fam4 under a `pw-dump`/`pactl` stress loop) |
| `controls.py`, `controls-neg.json`, `controls-mutstim.json` | negative control (5/5 named `missing tools` blocks), armed-constant mutation (exactly 3 header failures), stimulus mutation (sticky app reds the resume leg) |
| `census.sh`, `census-after-runs.txt` | exit census: 0 r91* objects/processes, defaults unchanged, fixture shas intact |
| `identity.txt` §foreign | sibling-lane observations (worktree churn at 10:01:02Z, r97 landing at 10:01:30Z, the `r91c-tree` same-family run at 10:00:58–10:01:42Z) |
