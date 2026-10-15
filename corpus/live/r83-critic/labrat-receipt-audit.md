# Labrat receipt audit (depth-2, read-only, advisory) — r83 committed receipts

Dispatched once by the frozen probeParent critic seat. Method: static JSON/prose
audit of `corpus/live/r83-author/measurements-run{1,2}.json` + the fixture block
`corpus/fixtures/measure_audio.py:16316-18700`. No fixture execution, no writes.

**Hypothesis:** the two committed receipts are internally consistent and
substantiate every headline pin in `reports/round-83/r83-author.md`.

## A. Structure / leg counts — CONFIRMED

Both receipts contain exactly the 7 keys; leg counts 29/19/26/13/18/15/8 =
**128 per receipt** (run1 == run2 == report).

## B. Failures — CONFIRMED

All `failures` arrays `[]`; zero `coverage_blocked`/`blocked`; `named_outcomes`
non-empty only in the matrix entry: run1 `["c1_mono_1: tap carried no audio …",
"m_alone arm realization: ['stable_mono','unmeasured','stable_mono'] …"]`,
run2 `["m_alone … ['stable_mono','stable_mono','stable_mono'] …"]` — both
disclosed in the report.

## C. Pin-by-pin — CONFIRMED

1. Entry 2: 18/18 `segv_*` legs `exit_code -11`, `signal SIGSEGV`,
   `nodes_after []`, `stderr ""`; `ctl_lb` `-9`/`SIGKILL`/`killed_at_bound true`.
2. Entry 1: 8 `err_*` rc=255 `props_syntax_error` with the two stderr fragments;
   5 `pc_err_*`/`pr_err_*` rc=1 `pwcat_props_syntax_error`; `drop_*` ran to
   bound with `stderr_tail null` and default `media.name`; `drop_partial`
   carries `"a": "b"`.
3. Entry 3: all 10 latency strings exact, incl. `4294967056/48000`; the 5 drop
   legs carry no `node.latency`; `onset_summary` — run1 ctl
   `[0.0934,0.1,0.1054]`, d10 deltas `[1.0429,0.9997,0.9934]`, d025
   `[0.3918,0.3516]`, l1000 `[0.1348,0.0973]`; run2 ctl median `0.1054`, d10
   deltas `[1.0429,0.9999,0.9992]`, d025 `[0.3981,0.3547]`, l1000
   `[0.1057,0.1053]`. All deltas in-envelope; no None transports.
4. Entry 4: `matrix_summary` matches report lines 59–60/91–92 exactly
   (run1 `c1_audio_legs 2`, arms `[stable_mono,unmeasured,stable_mono]`;
   run2 `c1_audio_legs 3`, arms `[stable_mono]×3`).
5. Entry 5: `remix_summary` 8181.6/8172.5; `m2_sdr_*` `out_port_names
   ["output_MONO"]`, FR `all_zero true`; `dm_move` `move_rc 0`, consumers
   unchanged.
6. Entry 6: `resample_summary {clean_amp_median 8172.5, artifact_class
   peaks_abs_octave_artifact}`; all three `s4_peaks_*` `full_wave_abs_octave`
   (run1 ch0: min 0, mean 4452.65, neg_frac 0.0, zero_frac 0.1462,
   amp@f 0.1, amp@2f 3177.9); `s1_disable_*` `all_zero`;
   `s4b_matched`/`s4c_downsample` `clean`; `s5_rate` `1/44100`; q0/q14 land.
7. Entry 7: all legs `failopen_target_is_default true`, `default_sink_now`
   SPDIF; `n_empty` `failopen_foreign_sink`; serials recorded and used verbatim.
8. Quoted numbers: `-l 5`, `-l -5`, d10 deltas `[1.043,1.000,0.999]`, d025
   `[0.398,0.355]`, ctl median `0.105`, `~14.6%` zero fraction, artifact class,
   "4 sinks unloaded / sinks_gone all true / own_nodes_after []" — all present.

## D. Adversarial scan

No nulls/recycled indices. Green-while-unmeasured paths are disclosed
(`c1_mono_1`, `m_alone_1`, fail-open `content_witness "declined"`). No
`deviates`/`nodes_not_seen`/`move_skipped` strings in either receipt.

## Findings (labrat, ranked)

1. **Label inaccuracy (minor):** report L52 presents `-d 0.25 [0.398,0.355]`
   next to the *delta* envelope `[0.08,0.60]`; the receipts store these as
   `onset_summary.d025_transports` (true deltas ~0.293/0.249). Envelope holds
   under either reading — no contradiction.
2. **Unverifiable statically:** the run timestamps `21:50:17Z`/`22:06:45Z` —
   neither JSON carries a timestamp field.
3. **Report self-inconsistency (not receipt):** L111 "No commits; everything
   working-tree-only" contradicts the committed status of the receipts it cites.
4. **Report mixes runs silently:** "ctl median 0.105" is run2's value (run1
   0.100).

**Verdict: CONFIRMED** — both receipts internally consistent; every reachable
numeric pin present and in-envelope; the only blemish is the d025
transports-vs-deltas labeling; unmeasured arms are recorded, not hidden.
