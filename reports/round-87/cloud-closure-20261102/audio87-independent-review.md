# AUDIO87 independent terminal review — 2026-11-02

## Decision

**REJECT AS DECLARED — completed substantive reviewed attempt, not successful admission.** I independently adjudicate the original reproducible-green landing claim against its actual contemporary contract. The preserved original work, independent failure reviews and falsification-driven repairs are sufficient for this terminal negative decision. This is not an administrative closure, an invented new round, a retrospective pass, or a new execution certificate. The integrator may adopt this as the terminal disposition of existing round 87 toward a goal of completed substantively reviewed attempts; this file itself changes no count, lane, or fleet ledger.

The repaired full declaration is **NOT ADMITTED**: the documented second folded green is demonstrably a pre-fold receipt, and the required folded-repeatability → verifier-r2 acceptance chain is not established. This is an admission gap, not a reason to defer an already supportable rejection forever.

Reviewer: `/root/judge_audio_round87`, independent of packet author `/root/reconcile_audio_rounds`. I used `audio87-closure-packet.md` and `audio-resume-reconciliation.md` for navigation, then read actual task cards, source diffs, original reviews, raw JSON and Git objects. No audio fixture, retained probe, network/device control, provider, package install, credentials or host-setting operation was executed. Analysis used read-only Git/file inspection and a newly written inline JSON/hash reader, not project scripts. Only this audit document was written.

## Pins and operative contract

Audio HEAD observed: `f9da7ee97e0ba95da1803c2afe9c616c519bae18`, clean. Fleet HEAD observed during review: `742e0480819c0271c6a40aabb09882057e288100` (a kasegi61 commit); this differs from the navigation packet snapshot. Current fleet MANIFEST audio rows remain 62,63,64,65,101; r101 does not admit r87. Audio SCORECARD round87 and LOG rounds82–100 reconciliation still say unadjudicated, correctly describing the record before this new decision. Fleet `.ufo/waves/kaika-w1/audio-state.md:54–66` documents the original missing adjudicator.

Actual fleet task cards:
- `.ufo/waves/shokunin-train-20261015-w22/tasks/audio-r87-author.md`: boundary-surviving claims, insertion-only fixture, namespaced objects and name-verified teardown, fixed lane-path lock not TMPDIR-scoped, green twice on identical bytes.
- Same directory `audio-r87-verifier.md`: committed d1e687b9 tree only, load preferred, four named families.
- `audio-r87-fold.md`: **two green runs on folded bytes → verifier-r2 gate → adjudication**.
- `audio-r87-r88-fold.md`: two green runs of each family on folded bytes.
- w23 `audio-r87r88-foldverify.md` requests one fresh run on the explicitly stated premise that earlier folded runs existed, while calling the original contract authoritative. That premise is false for the cited r87 receipt. It does not establish a waiver of the original two-run requirement.

I read fleet PROTOCOL for context but do not retroactively import its modern seat-count, frontier or publication requirements into r87. No contemporary requirement for host-global cross-materialization locking is invented: fixed-path/not-TMPDIR was met narrowly; cross-tree concurrency remains an observed reproducibility limitation.

Verified available source identities (Git blobs read directly and SHA256 recomputed):

| Pin | Git fixture blob | SHA256 of `corpus/fixtures/measure_audio.py` |
|---|---|---|
| Original `d1e687b9b6beda083969e4a770d79a6b4407cde9` | `a712ccc6dbde3bf4de3626b1731557a67e8e04bc` | `be31da679be229074690dc5157edcc122612560594baa8ba62a9b5ce26dd9516` |
| Fold parent `1977cf42^` | `fab804d4be7118f1f3f9e6f4df7e9e0286534f73` | `623c25cc55521472dc54a1ab2b4ccb4a9836fda3ca1a71dcca06092a4317cd22` |
| Fold `1977cf4206f5bde37b94debb30139633ca5d85c0` | `846d1a591ebeef7d4cef9e51c2bf47dba6238cac` | `d278458501a966cf621ff3f858ae6b932c0621df1083bf30559cf5f0325a4dd9` |

The preserved `corpus/live/r87-fold/fold.diff` equals the actual fold commit diff after excluding path-prefix headers. This establishes source correspondence, not new behavior verification. Original report labels mentioning `a7d2367b` are not available Git objects here; actual reviewer report introduction is `2d060492a2f5dfe7b42adc275fb6a23b7e5a1911`, and I rely on its available bytes, not identity equivalence with that old label.

## Criterion-specific adjudication

| Criterion | Verdict and evidence |
|---|---|
| Substantive original domain work | **Established.** Four implemented families/105 leg keys; original author report, source and receipts. Boundary report (`fd0bc8b02ecc60f28f821e8659e8aa844a9f064b`) falsifies scout's routing order and supplies the correction flag > node.target. This is actual learning, not a failed launch or marker. |
| Original two author greens | **Supported as observations**, with report-attested source provenance rather than authenticated execution lineage. They do not establish independent repeatability. |
| Independent committed-byte reproducible-green gate | **FAIL.** Three verifier replays are red in preserved raw JSON; separate reviewer reports one red and one green frozen replay. Original refusal-window harness defect is independently diagnosed. A fail-closed harness defect can reject reproducibility without falsifying the underlying refusal law. |
| Depth | **Substantive bounded learning retained; full declared admission rejected.** Routing correction, serial/object.id distinctions, mode direction, live Props response and MIDI event witnesses have independent support. Vacuous sysex/termination and weak negative arms prevent treating all original coverage as proven. No exact universal DSP or perceptual quality conclusion follows. |
| Coverage | **Incomplete for full admission.** Critic demonstrates missing MIDI legs/empty attempts, unresolved-peer edges and absent snapshots can evade original arms. Later repair is real but its happy receipt does not exercise every negative path.105 keys are not105 independently proved laws. |
| Calibration | **Original/fold whole-green representation rejected.** Preserve original red development runs, red independent replays, source attribution limits, duplicated folded-green attribution, and absent committed verifier-r2 acceptance. Current narrower rejection repairs our interpretation; it does not retroactively improve the author's calibration verdict. |
| Fold correspondence and bounded repair | **Established statically plus one historical green observation**, not completed gate. Full-log fields,5-second sysex sample, self-exit skeleton, named blocks and raw-edge checks exist in landed source. |
| Terminal completion as rejected learning | **Established by this independent review**, subject to integrator adoption. Original claim has decisive contrary evidence, extensive actual work and multiple independent assessments. No fresh native execution is necessary to reject it honestly. |

## Independent original failures and custody

Paths below are under `lanes/audio/`. I read and SHA256-hashed all three verifier JSONs and verified their local bytes equal `git show HEAD:<path>`.

| `corpus/live/r87-verifier/runs/` | SHA256 | Actual failure |
|---|---|---|
| `r87v1.receipt.json` | `3fd7d46e0836608d363fe5687dfcce3b024ff09db060c466c3a919e999a9f942` | create_usage |
| `r87v2.receipt.json` | `1e8683f0b452364e7ce2ec47f72845334e269b22a57f4db0ac83c1860a0dd088` | create_badfac, create_usage, pin zero bytes/no events |
| `r87v3.receipt.json` | `2d8ddd6dace8dfdb058509401ee6dfcffec656abfc162cbf84869ba4c85fa6fb` | create_badfac, create_usage |

Their Git blob IDs are respectively `5273626c5edd45b9a9eda09c00390b71daf84044`, `77ee115fc297cdf9f4a8fbd3af8369715c6ddd4e`, `6d1fbc7e464426a226cb5880d0e7338d2a6adc15`. Available report introductions: verifier `b13787f9cc83bd372631fc9d22c56207860f9b90`; reviewer `2d060492a2f5dfe7b42adc275fb6a23b7e5a1911`; critic `a924878f9fc3692269a9c715d5bc6c5ba94d7a4c`; simplifier `c49fcfad92082a73de6aba0b9e5a1e4f1bece0a5`; scribe `6af83254ed2bf9f10b5f42210310a4677183f18a`. Reviewer PASS-with-findings and critic ADMIT-with-findings are scoped seat opinions, not a terminal acceptance overriding the verifier gate.

**Correction to report/packet arithmetic:** `corpus/live/r87-verifier/runs/laws-all.txt` SHA256 `f6e4d5f7523ceda372a1d87fceb874a3da371ebc99651b7d9955a82aaf0d4894` lists 43+43+42+40+41+41+43 = **293/301**, not295/301. Its matrix has8 failures (badfac3, usage4, pin1), not6. This strengthens the rejection but does not change its basis. The reviewer's frozen-tree raw receipts are not present in the searched reviewer directory; their failure details are preserved in the independent report and verifier matrix/hash list, not newly raw-verified by me.

## The duplicated folded-green attribution

Directly hashed canonical `corpus/live/runs/<directory>/measurements.json`:
- Original A, `20261016T070036115509Z-pwbind-r87`: `01f04d354f2186dbcf4bc984e2d62a49f378ea8ca2f810d79c7586797d1f1667`.
- Original B, `20261016T070305393338Z-pwbind-r87`: `2970c944375f2e3b8b6f3ab16bdd5a343521222844d9a3a044a0a7d9a974a655`.
- Fold verification, `20261016T083046454782Z-pwbind-r87`: `895deece0eedb48e5cf9c86077cb15831d1371006fbd74922be69c279601d61c`.

Author §Runs explicitly pins A/B to original be31da67 source. Fold §Leg results nevertheless labels exact B as fold r1. Raw B has only `log_tail/errors` for both create legs, sysex snapshots0.922/1.723s, and no skeleton `self_exited`. Fresh083046 has full `log`, snapshots0.919/5.021s and `self_exited:true`. Thus B is not evidence of executing the folded shape. B/fresh bytes match their Git objects; fresh canonical and `r87-fold/measurements-20261016T083046454782Z-pwbind-r87.json` are identical, not two runs. Each contains four families with18/33/30/24 keys, failures `[]`, and blocks absent (not the report's `{}`/explicit empty blocks notation).

Available all-ref path census contains six canonical r87 receipts:064958,065456,065750,070036,070305,083046. Only last has folded shape. Receipts' durable custody is evidence commit `57e5577fa7ab713f87d908ce5169d3596e795ce1`, later than author/fold commits. This bounded history does not prove no untracked run ever existed; it does prove the two cited receipts do not substantiate two folded runs. The fold-verify seat observed uncommitted source later matched to committed source; do not call it the missing committed-only verifier-r2 gate.

## Learning retained; remaining gaps and exact next-action status

1. Retain the corrected routing order and host-bounded observations, original mutation discrimination and falsified fail-open arms. Do not discard valid subclaims merely because the whole reproducibility gate fails.
2. Retain the full-log vs tail-window lesson, post-EOF observation rather than kill-status inference, self-termination witness, explicit missing-data blocks and raw-edge rather than resolved-name absence.
3. **Additional correction to packet:** simplifier's specific `legs[name]["snaps"]` spawn-error KeyError is statically addressed in fold by `legs[name].get("snaps") or []`, then a false last-presence verdict on empty data. No fresh execution certifies this branch, but it is not accurate to leave that exact direct-subscript defect wholly undisposed. Broader exception containment is not established.
4. Preserve tree-relative locking, co-tenancy pin flake, failure-path replay limitations and envelope-not-exact measurement scope. Later rounds' locks do not automatically supply r87 gate evidence.

| Action | Target | Reason / done | Status |
|---|---|---|---|
| Terminal original-claim review | Existing r87 | Actual original failures, independent review and substantive work checked; this negative decision completed | **Done** |
| Integrator adoption | Existing r87 audit/ledger | Reviewer does not edit lane/fleet or count | **Pending integrator**, not evidence-blocked |
| Establish repaired full admission, only if requested | Fold pin and repeatability/verifier-r2 evidence | Need distinct genuine folded green plus required independent acceptance evidence, or newly authorized immutable-pin verification; none fabricated | **Uncertain / not established** |
| New native runs or hardware/network/settings work | Audio host | Not needed for rejection and outside this read-only assignment; none attempted | **Not performed**, not an approval denial |

No denial occurred and no uncertain side-effect execution needs checking. Stop this review at existing87; this document neither starts88 nor advances any counter. Preserve all original reports and this correction append-only on adoption.
