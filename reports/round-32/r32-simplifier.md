# Round 32 simplifier

## Recommendation
Keep this to one opt-in probe, not a reusable framework or a new canonical asset. The declared claim is narrow: for this generated pair, the existing alternate comparison passes when duration delta is nonzero and below `.020` while relative centroid delta is nonzero and at least `.10`.

Generate the 5760-frame baseline and 6719-frame variant from source. Reuse the existing per-file measurement and `_alt` comparison path. Keep the baseline on the canonical UI spec; declare the variant's `6719/48000` duration only as its scratch ordinary-check spec. Do not change the `.020 OR .10` logic, thresholds, or canonical WAVs. A runner receipt must show both measured deltas and the ordinary-check results; do not infer them from the generation coefficient.

## Scope and limits
The 6719-frame variant is about `.139979 s`, so it does **not** conform to the canonical `.120 s` UI duration. Passing its separately declared scratch spec is not canonical-duration conformance. The observation would demonstrate this mixed-signals case only—not causal independence, an exact cutoff, broad codec behavior, or audible/perceptual distinctness. It makes no equality, rights, engine, publishing, or promotion claim.

## Commands and failures
No shell commands were run; there are no command exit codes, fit attempts, or setup failures to report. Any later unsuccessful coefficient fit or setup error should be recorded separately from a runner gate result.
