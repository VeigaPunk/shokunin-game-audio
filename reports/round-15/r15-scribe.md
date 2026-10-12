# Round 15 scribe — decision table draft

## Scope and status

This is the requested before/after decision-table draft, not a verdict. The round-15 log declares a proposed **depth** move: add an opt-in 180 Hz internal-layer slope-only negative. At the time of writing, the log contains the proposal but no round-15 candidate, runner integration, independent replay, or adjudication evidence. I have not run shell commands or measured audio. Do not treat the proposed after-state as achieved or as a pass.

## Decision table

| Question | Before `0928e9e` (as declared in the round log) | Proposed after-state | Evidence/status |
|---|---|---|---|
| 180 Hz clean layer internal gap | Passes existing comparison | Must remain passing | Before: round log reports decoded gap `0.0003662109375` FS. After: not yet evidenced here. |
| 180 Hz clean layer side-slope | Passes existing comparison | Must remain passing | Before: round log reports mismatch `0.0008544921875` FS/sample. After: not yet evidenced here. |
| Matched 180 Hz slope-only negative | Absent | Add opt-in `--probe-layer-alt-slope`, failing only the existing `>.001` FS/sample side-slope gate | Proposed only. No candidate or runner receipt cited in the round log excerpt. |
| Negative's gap, component validity/contrast, generic and outer gates | No matched negative to assess | Gap `<=.03` FS; valid 180 Hz component with contrast `>=6dB`; generic/outer checks pass | Acceptance conditions only; no measurements supplied. |
| Existing controls and canonical artifacts | Existing behavior is the baseline | Preserve prior modes and all twelve canonical hashes | To be checked by integration/replay; not established in this report. |
| Axis judgment | No matched 180 Hz slope-only negative | Could improve **depth** if the negative is independently shown to fail solely on slope and controls/hashes remain intact | Unadjudicated; no axis improvement or no-harm claim. |

## Evidence, limits, and required follow-up

The round-15 log states clean decoded frames 95998–96001 as `[-0.000701904296875, -0.0003662109375, 0, 0.001190185546875]` FS, yielding the stated clean internal gap and slope mismatch. It proposes adding about `0.0004` FS to frame 96001 as a **hypothesis**, not a result. It also specifies reusing the existing local bounds (`.03` FS gap, `.001` FS/sample slope, `6dB` contrast), with no new threshold. These are declarations in the source log, not independent measurements by this scribe.

For any later claim, distinguish (1) a generated scratch WAV recipe/hash, (2) its decoded runner receipt and complete failure list, (3) independent replay and canonical-hash comparison, and (4) adjudication. A failed fit must not be presented as a slope-only rejection. The proposed numeric gate is a fixture/toolchain proxy only; it does not establish audible smoothness, musical quality, engine behavior, security, external compatibility, or production readiness.

No shell command was run for this report; there are no command exits or receipts to claim. This draft should be updated only from the assigned candidate, integration, independent-verifier, and adjudicator reports. No pass is invented here.
