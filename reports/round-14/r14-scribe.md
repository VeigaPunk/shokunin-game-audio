# Round 14 scribe — draft decision table

**Status:** draft from the round-14 declaration and source inspection only. No round-14 implementation, fixture measurement, replay, or adjudication evidence was present when this draft was prepared. Do not treat the proposed outcome as a pass or an admitted move.

## Before / after decision table

| Question | Before (`ce3233a`) | Proposed after (requires implementation and independent replay) | Evidence status |
|---|---|---|---|
| 180 Hz `stem_layer_alt` internal join | Positive fixture passes the existing internal adjacent-gap (`<= .03` FS) and side-slope mismatch (`<= .001` FS/sample) checks. There is no matched 180 Hz gap-only negative. | Add opt-in `--probe-layer-alt-join`, based on the generated `stem_layer_alt`; introduce a frame-96000 adjacent gap `> .03` FS while tuning frame 96001 so the existing side-slope mismatch remains `<= .001` FS/sample. Intended outcome: the scratch fails only the existing internal adjacent-gap check. | Before claim is in the round-14 LOG. Proposed after is a specification, not measured evidence. |
| Other checks on proposed scratch | N/A | Generic/outer checks, section validity and `>=6 dB` 180 Hz component-amplitude contrast, existing `_alt` distinctness, and side-slope check should pass. | Not verified. No values or receipt available. |
| Existing modes / canonical corpus | Round-13 records are summarized in LOG; round-14 baseline inventory not independently reproduced here. | Existing modes retain expected outcomes, normal mode restores, and all 12 canonical WAV hashes remain unchanged vs `ce3233a`. | Not replayed / not hash-checked here. |
| Axis verdict | Existing claim: missing a matched 180 Hz gap-only negative. | If the proposed isolated failure and regressions checks are independently evidenced, this is a bounded **depth** move using existing limits; otherwise no admission. | Verdict pending verifier and adjudicator. |

## Decision criteria and caveats

The discriminating check is the existing internal adjacent-sample gap at indices 95999/96000. A qualifying isolated probe must have `abs(x[96000]-x[95999]) > .03` full scale, while the side-slope expression `abs((x[96001]-x[96000])-(x[95999]-x[95998])) <= .001` full scale/sample. It must also retain valid section measurements and `>=6 dB` contrast, pass the other applicable gates and positive-variant distinctness, and show no unintended failures. These are existing local thresholds, not new calibration evidence.

The stated goal is a controlled synthetic numeric fixture, not a claim that a one-sample gap is audible, musically objectionable, representative of a transition, or evidence about an adaptive engine, security, or production quality. A successful fixture would exercise this branch only; it would not establish behavior over diverse signals. No threshold calibration or listening test is evidenced.

## Commands and evidence

No audio generation, measurement, or verifier shell command was run for this report; therefore there are no such commands/exits or credited receipts to report. The working-tree status and latest commit were inspected read-only (`git status --short && git log -1 --oneline`); output showed only `.shokunin/audio/LOG.md` modified and `ce3233a Audio round 13: final depth report`. Source and LOG were read for task context. No source, LOG, scorecard, canonical asset, or commit was changed by this report.
