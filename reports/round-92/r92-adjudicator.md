# r92 Adjudication - Filter-Chain DSP

DECISION: **ADMIT-with-findings + required fold** on `ccbce758`, scoped to
the independently re-derived measurements. Reject the two mechanism
sentences and the coverage claims contradicted below.

## Five-Gate Record

- Verifier: fresh archived runs on `ccbce758` and `b8ff4efc` both pass;
  304/304 independent checks pass on each, covering 81 top-level leg
  keys. Raw-WAV analysis independently reproduces the recorded DSP
  measurements. Controls distinguish mutations, no-op and named blocks.
- Critic: encoding reproduces, but the negative-Q reading is a clipping
  ceiling and the 20 kHz discrepancy is reproduced by s16 quantization,
  not float32 arithmetic. Several missing-witness paths pass open.
- Reviewer: independent analysis corroborates both mechanism corrections.
  Every receipted sink unload was skipped as `not_listed`; successful
  final censuses do not demonstrate that name-verified unload fired.
  The reason for those skips remains unresolved.
- Scribe: family/dispatch and retained receipt links hold; the headline
  count is 80 while receipts have 81 keys, including `i_residual`.
  Whole-file implementation binding was asserted, not recorded in receipts.
- Simplifier: paired runs prove candidate fail-closed fixes and local
  deduplications. No candidate patch is landed by this adjudication.

## Admitted And Rejected Scope

Admit the receipted response/residual/activation observations and the
boundary falsifications at their measured scope. Do not treat a clipped
capture as a response-magnitude measurement. Reject the float32
explanation for the quantization-floor cell and the interpretation of
`d_fhi`, `a_ports_none` or silent-load rows as fully guarding missing
witnesses. The reviewer's approximate gain model is explanatory evidence,
not a newly pinned unclipped measurement.

## Required Fold

1. Make `d_fhi` reject missing or incomplete gain vectors.
2. Make the no-port `feed_link` guard reject absent/indeterminate status,
   and arm each silent IR row's load reply before its activation half.
3. Preserve a named block/abort envelope when numeric predicates cannot
   evaluate; do not convert exceptions or missing tools into measured green.
4. Distinguish an absent module from a failed module-table read in unload
   bookkeeping. Retain the unresolved skip mechanism and final-census
   evidence separately; neither is proof of the other.
5. Correct 80 -> 81, stale log sizes, timestamps and the two mechanism
   sentences. Mark missing in-receipt source binding explicitly.
6. Keep simplifier deduplication candidates separate from these required
   coverage repairs. The optional signature-shape deletion is not
   automatically accepted with the primary folds.

No law, threshold, fixture, pin or normalization changes accompany this
disposition. Evidence: the five `r92-*` wave-B reports in this directory.
This is not a clean all-arms verdict or a claim that the queued repairs
have shipped.
