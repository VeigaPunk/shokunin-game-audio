# r93 Arm Failure Propagation And Owned Scratch Cleanup

Lead-authored repair; not another review-seat launch or a native UFO verdict.
Before source sha:
`a8760b120fbbb47d091f6d0a674e3630d4fd20b9ee6e366df0f6c57371a019f9`.
After source sha:
`ab31411341a94669bc1204f7d20f5de92471f9ee8538161df470f64b0382633b`.
The same source commit also contains the separately described r98 repairs.

## Changes And Evidence

- Unexpected arm setup failures now reach failures as well as the named
  coverage-block list. Explicit expected refusals retain their classification.
- ch_silent_mom, m_range_only and m_peak_only require a successful recorded
  playback exit before accepting their silent/plateau readout. A dead feeder
  cannot certify these semantics. Other long-running arms are not given
  this additional exit-code constraint.
- All nine entry callers share the actual failures list with the helper.
  The first proposed helper-only change was insufficient: the callers could
  overwrite its failures with their independent empty lists. A full
  modes-entry regression through the real JSON normalizer exposes that
  loss; the initialization fix closes it.
- Temporary capture directories have registered TemporaryDirectory owners,
  retained outside the serialized context. Normal teardown and whole-entry
  blocks clean only those owners. An unregistered path is never deleted or
  reported successfully cleaned. No old /tmp/r93a-tap-* glob is swept.
- Whole-entry prerequisite blocks fail rather than summarize empty success.

The frozen verifier receipt has playback exit 0 on both repetitions of
all three affected arm tags. Those are existing measured inputs, not a
new replay or new capture claim. The setup/silence guard does not change
any dB constants, timing bands, stimulus or capture implementation.

## Reproducible Regression

`python3 -B corpus/fixtures/test_audio_final_guards.py`

The exact current test bytes (sha
`7fe44d567ea3e538062ca60344a0070a301e8b3b5de5fc98214e5ef2c59b1d68`)
run against an isolated copy of the old source: 13 tests, 31 failures
including subtests, rc 1. The same bytes against repaired source: all
13 pass, rc 0. Source/test compile checks pass. The unit combines r93/r98
failure-path cases; it runs no audio, PipeWire or network. Owned-child
cases use inert Python children and clean them even on baseline failure.

Raw source/test copies, full diff, staged and final command outputs:
`/home/vgpnk/Projects/shokunin/audio-final-guard-proof/`.

## Still Not Claimed

This is not a new complete 90-key family measurement. The g_default tap
defect and unattempted audio-domain gain arms, one-sided decay band,
exception/receipt containment, and historical bytecode/provenance findings
remain distinct items for adjudication. A completed temporary cleanup is
not a claim of universal process containment or external-kill safety.
