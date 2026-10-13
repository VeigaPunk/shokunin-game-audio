# Round 32 scribe: decision table and evidence status

## Decision table

The declared experiment changes duration and centroid together and asks whether the existing `_alt` distinctness OR accepts through the centroid arm while duration remains below its cutoff. Expected comparisons below are the declared conditions, **not measured round-32 outcomes**.

| Case | Duration delta | Relative centroid delta | Duration arm (`>= .020`) | Centroid arm (`>= .10`) | Existing OR / expected status |
|---|---:|---:|---|---|---|
| Baseline duplicate (reference) | 0 | 0 | false | false | Reject alternate as not distinct |
| Round 31 joint-below control | 0.019978999999999997 | 0.09964036511023265 | false | false | Reject alternate; both below |
| Round 32 intended mixed case | nonzero, `< .020` | nonzero, `>= .10` | false | true | Accept alternate through centroid arm; runner expected exit 0 |
| Duration-arm comparison (prior declared control) | `>= .020` | `< .10` | true | false | Accept alternate through duration arm |
| Centroid-arm comparison (prior declared control) | 0 | `>= .10` | false | true | Accept alternate through centroid arm |

The round-32 target requires both per-file ordinary checks to pass: the 5760-frame base under canonical UI `.120 s` duration, and the 6719-frame variant under its separately declared scratch duration `6719/48000`. The 6719-frame variant does **not** conform to the canonical `.120 s` duration. The joint result would demonstrate one observed mixed-signals OR case only; it does not establish causal independence, exact cutoff behavior, universal OR behavior, or audible/perceptual distinctness.

## Evidence and failures

The declared round-32 LOG entry describes the target and preservation constraints, but no round-32 executor/alt/reviewer/critic reports or round-32 receipts were present in `.shokunin/audio/reports/round-32/` or `corpus/live/` when I inspected them. Therefore there is no measured fit or gate result to report here. No failed coefficient/fit or gate rejection should be inferred from the absence of evidence.

Failure classification for any later evidence:

- **Setup/command failure:** no valid measurement receipt (for example, command wrapper/path/dependency failure). Record command and exit; exclude it from gate outcomes and correct/retry separately.
- **Fit failure:** command runs and produces measurements, but no candidate reaches the declared nonzero `<.020` duration and nonzero `>= .10` centroid conditions, or per-file ordinary checks fail. Record the measured values and exclusions; this is not a comparator rejection.
- **Measured gate rejection:** valid receipt, ordinary checks pass, and existing comparator rejects the alternate. This is a gate outcome, distinct from setup or fit failure.
- **Measured gate acceptance:** valid receipt, ordinary checks pass, duration arm false and centroid arm true, and existing comparator accepts. This is the intended round-32 observation, pending actual receipt and independent replay.

## Commands run by this scribe

No shell commands were run, so there are no shell exit codes to report. I only inspected the declared LOG and report/receipt paths. No source, LOG, SCORECARD, canonical artifact, or other report was edited.

## Scope and limits

No equality, causal, perceptual, rights, engine, publishing, or promotion claim. This variant is not canonical `.120 s` duration-conforming. This report does not establish round-32 admission or independent replay; parent adjudication remains pending.
