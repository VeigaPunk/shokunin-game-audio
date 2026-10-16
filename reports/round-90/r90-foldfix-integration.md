# r90 Fold Integration Review

The completed FF1-FF6 changes were reviewed against main `d41cfa68`,
which already contains the independent r98 integration. The r90 delta
is confined to its family and dispatch, plus its author-report corrections.
The historical fold report's `e2e5a002...` evidence remains unchanged.

## Additional Defect And Repair

Review found that a lock waiter timing out called the owner-release
helper, truncating the live holder's advisory text without owning the
flock. The timeout branch now only closes its own fd. Successful-owner
release still truncates before closing.

The lead-authored regression was executed before and after this repair:

- Before: rc 1, `AssertionError: refused waiter truncated holder text`.
- After: rc 0; holder text preserved, stale dead-pid text observed on
  subsequent successful acquisition, and owner release leaves zero bytes.
- Durable test: `python -B corpus/fixtures/test_wpstate_r90_lock.py`.

Raw captures and before/after patches are retained, not regenerated, at
`/home/vgpnk/Projects/shokunin/r90-resume-proof/`.

## Merged-Byte Measurement

One fresh full r90-family invocation, after bounded `pactl info` rc 0,
ran on source sha256
`91f42214780c573a9f86c7e12b4979dd06df1998c181179c9d834c2e4d98e297`.
Receipt:
`corpus/live/runs/20261016T120125610993Z-wpstate-r90/measurements.json`.

The orchestrator checked the receipt directly: all four entries have
`measured: true`, no failures, no entry coverage blocks, and exactly
16/15/24/6 legs (61 total). Every entry carries that exact source sha,
seat `r90-resume-proof`, a nonempty all-true sink census, and
`own_nodes_after: []`. The run census says 4/4 entries measured and the
family lock was acquired. The invocation returns rc 0; stderr is empty.
Compile/help return 0, and the r90+r98 probe mutex returns 2.

This is one new merged-byte family run, not two independent runs and
not a claim that the entire historical suite was re-executed. Later
integrations change the whole-file sha; this receipt binds these bytes
only. Its local evidence paths are gitignored and are not uploaded by
this commit.

## Remaining Scope

The original fold's race-class and store-residue tradeoffs remain as
documented in `r90-foldfix.md`. In particular, rc 0 alone still does
not certify measurement on a coverage-blocked invocation: inspect
`measured`, `legs_measured`, the census, and `coverage_blocked`.
This integration does not apply the queued simplifier deletions.
