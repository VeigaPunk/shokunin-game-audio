# r98 Failed Setup, Exception Cleanup And Named Census

Lead-authored repair on source sha
`ab31411341a94669bc1204f7d20f5de92471f9ee8538161df470f64b0382633b`.
Before source sha:
`a8760b120fbbb47d091f6d0a674e3630d4fd20b9ee6e366df0f6c57371a019f9`.
This is not a new verifier/native-judge run.

## Repairs

- A whole-entry prerequisite block now names a failure, retaining the
  partial legs and coverage block. Sub-arm coverage blocks are not
  indiscriminately promoted to failures.
- Teardown compares the loaded sink's actual value/name, not bookkeeping
  aliases such as ns/ns2, in both sink and node censuses.
- Each of the five shared-core entries runs teardown from finally on
  success or an unexpected exception. An existing whole-entry block
  already stops/unloads its resources and is not double-unloaded.
  Legs, transient sweep and failure bookkeeping remain in a protected
  inner finally even if teardown raises.
- Private startup retains its partial ctx before spawning. Socket timeout,
  create-node exceptions and later setup failures call the existing
  own-Popen stop/reap helper before re-raising.

## Proof

corpus/fixtures/test_audio_final_guards.py is the shared focused regression
for this fold and the adjacent r93 fold: identical test bytes have 31
failures including subtests against the old source, then all 13 tests pass
against the repaired source. Both files compile. Full source diff reviewed
by the lead; no fixture C, sample geometry or numerical law changes.

Two actual owned inert Python children cover private socket-never-appeared
and create-node-timeout paths. The tests verify terminated/reaped children
and closed logs, and clean them on the red baseline too. The suite also
injects an exception after core-entry load, verifies teardown runs, and
checks finally placement in all five shared-core entries.

Raw proof: /home/vgpnk/Projects/shokunin/audio-final-guard-proof/.
These are ordinary process/unit observations, not native PipeWire capture
measurements. The recorded 67-key verifier run remains attached to its
older frozen pin, never relabeled as verification of this repair.

## Residual Scope

Receipt-on-exception containment is not supplied by moving cleanup.
Sub-arm capture/profiler blocks, PID-scoped naming gaps, negative-control
reachability and other unarmed law findings remain review inputs.
Shared helpers and old published receipts are not rewritten.
