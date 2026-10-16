# R93 Entry Cleanup - Data Walk And Gates

Status: implemented; all nine entries repaired and the injected-case
gate is green. Not a full-family re-verification or round-admission
claim.
Before: 6cd98c64, source sha
9f242022408b7447cc9afeac44a34d353c37bd8b8cf60efa8e04c3bd780933ec.

## Data Walk

All nine entry failure lists share their entry accumulator, but only
topology/cal/error have finally teardown. Channel/modes/peaks/window/
history/gain call teardown only after the normal scientific body.
An unexpected backend exception skips those six cleanups; the other
three clean up but still let the exception escape the end-of-run writer.

test_ebur_r93_entry_cleanup.py loads the actual source without main,
replaces header/context/backend/teardown with inert callbacks, inserts
one metadata-only partial leg and raises from the first backend call.
All nine subcases fail before the repair, with no test errors.
There is no actor, audio backend, or process execution.
Logs: audio-final-guard-proof/r93-entry-cleanup-before.*.

## Milestones

1. Red one metadata case across the existing nine entries: DONE.
2. Add a small abort recorder for failure + named coverage reason;
   catch ordinary exceptions in all nine entries, always attach legs
   and run teardown in finally. Keep all six unprotected scientific
   bodies verbatim except indentation, and keep the three existing
   protected bodies unchanged. Gate: nine injected cases pass.
3. Compare scientific-body ASTs to the actual pre-edit snapshot at
   audio-final-guard-proof/r93-entry-6cd98c64-core-before.json, then
   compile and diff checks. No new numerical law, band, native battery
   or physical/network operation.

The one-off AST artifact records all nine original core bodies and
hashes. For the six linear entries it spans after ctx initialization
through the statement before entry["legs"]; for the three protected
entries it is the existing try body. It is differential repair evidence,
not a new permanent scientific grader.

Out of scope: late pw-cli/double-load and final-communicate findings,
entry-header exceptions before the cleanup scope, the generic main
writer boundary, and new audio-domain measurements. Those are not
silently closed by a callback-cleanup test.

One-case gate: the modes entry now records an unexpected abort, attaches
its partial legs and runs teardown in finally. The selected
EntryCleanupTest.test_modes_entry_smoke passes; its scientific-body AST
is identical to the actual pre-edit snapshot. Source at this intermediate
point is 8ad2091599d145f6b44858dd92633b8bd18ade482e7140b0e65b69cbd6481c07.
This is not a combined nine-entry green. Logs:
audio-final-guard-proof/r93-entry-cleanup-modes.*.

## Results

M2/M3 done. The same contract now covers all nine: each body runs
inside try, `except Exception` records one `_ebur_r93_abort` failure +
named coverage_blocked reason, and `finally` always attaches
legs/failures then runs teardown. For the five linear entries
(channel/peaks/window/history/gain) the scientific body was re-indented
verbatim under try; for the three already-protected entries
(topology/cal/error) only the except clause was added and the two
post-try assignments moved into the existing finally. Entry header
lines (head/failures/ctx/tools/table) stay outside the cleanup scope,
matching the modes shape.

Gates: test_ebur_r93_entry_cleanup.py — both tests green, all nine
injected subcases pass (previously eight failed after the modes fix).
All nine scientific-body ASTs re-verified identical against the real
pre-edit bytes at 6cd98c64 (extracted via `git show`, which supersedes
the discarded one-off snapshot json). `git diff --check` clean;
compile check clean; the other focused suites
(final_guards/host_lock/pwstream_r98_scope/rtp_r99_*/sofa_r100/
wppol_r97/wpstate_r90) all still pass. Source sha 4e0614f836....

No DSP law, band, threshold or entry-header change; no audio backend,
process or network execution in the gate. The out-of-scope findings
above remain open and are not silently closed here.
