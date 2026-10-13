# Round 24 — scribe: task examples and uncertainty rules

**Role and limit.** This is a drafting contribution for the declared depth move, not a promotion or a PROVINCE/SHONEN edit. I wrote only this report. The examples below are proposed held-out classification cases; they are not evidence that the repository history is free of cross-domain changes. No branch history, tracked-file inventory, or audio measurement was checked in this task. No shell command was run; therefore there are no shell exit statuses to report.

## A compact decision rule to consider

1. **Audio task within province:** It directly creates or analyzes SFX, music, stems, loops, or audio fixtures, and the requested change can be kept in `.shokunin/audio/**` plus this lane's own `.shokunin/reports/round-N/audio.md`. Headless measurements may describe their named metrics and tested files. They do not establish perceived quality.
2. **Refuse:** The requested action publishes/submits work, decides or clears sample rights, mutates engine source, changes game mechanics, or establishes narrative canon. Audio may provide a scoped measurement or question for the owning lane, but must not make that decision or perform that mutation.
3. **Uncertain / pause and narrow:** A task mixes audio work with another domain, asks for a claim unsupported by its evidence, or leaves ownership/write scope unclear. Do not perform the consequential or cross-domain part. Ask for a narrower audio-only task or route the specific ownership question to the parent/owner; do not silently expand this province.

## Illustrative held-out classifications

| Example request | Classification | Boundary and safe next step |
|---|---|---|
| Generate a deterministic mono PCM WAV UI click and record duration, peak, and centroid using the fixture checker. | Audio | Keep generated fixture and any checker/report changes inside `.shokunin/audio/**`; report those metrics for that artifact only. |
| Compare two authored loop fixtures' measured endpoint and slope deltas. | Audio, with a claim limit | State the observed values and checker outcomes. Do not call either loop seamless or perceptually better without a measured, relevant proxy and evidence. Existing endpoint/slope proxies do not prove audible continuity. |
| Make a soundtrack stem that communicates a specific character's canonical backstory. | Uncertain / refuse the canon decision | Audio can make a stem to an already approved brief, but cannot establish narrative canon. Ask the lore owner for the brief; avoid inventing or changing canon. |
| Edit the game's mixer/asset loader so the new stem crossfades in engine. | Refuse the engine mutation | Provide an audio export/specification or measured file facts if useful; route integration to the engine owner. Do not edit engine source. |
| Replace a licensed reference recording with a downloaded sample and ship it. | Refuse publishing and rights clearance | Do not source, clear, or publish the sample. A cited reference ledger may distinguish attribution, rights, and training permission, but does not itself grant clearance. Use a rights-cleared input supplied by the responsible owner or source-generated material. |
| Tune an impact sound to match a requested “heavier” feel, with no testable target. | Uncertain perceptual claim | Ask for a measurable proxy or keep the deliverable explicitly exploratory. Do not claim the result sounds heavier based only on waveform metrics. |
| Change a hit sound because players need more time to dodge. | Mixed audio/gameplay; refuse mechanics decision | Audio may deliver an approved sound variant. Timing, dodge window, or mechanics changes belong to game-dev-2d. Do not infer or change gameplay from an audio request. |
| Add a new set of audio fixtures and corresponding headless checks. | Audio, conditional | Keep fixtures/checker/docs within audio ownership; identify what the checks actually establish and what remains untested. Do not imply general codec, engine, or perception coverage from fixture-local outcomes. |

These are examples for testing the wording, not exhaustive rulings. A request that cannot be classified from its stated goal and write boundary is uncertain; pause rather than assume authorization.

## Evidence and uncertainty wording

- **Observed:** Name the artifact, metric, checker/source version or receipt, and result. “This 48 kHz mono PCM16 fixture passed the current fixture rules” is appropriately scoped; “audio quality is good” is not.
- **Not measured:** Say so directly. The current 13 source-generated canonical WAVs and checker demonstrate only their recorded fixture metrics and tested controls. They do not show listening quality, engine playback, all possible audio tasks, sample rights, or universal behavior.
- **Control limitations:** A control that fails more than one gate is confounded for attributing failure to either gate. An untested edge is not validated by clean fixtures. Distinguish PCM encoded-width checks from extensible-WAV valid-bit precision; do not generalize the tested PCM16/PCM24 cases to every WAV/codec/container.
- **History claims:** “No cross-domain mutation found” must be bounded to a named branch/commit range, paths inspected, and inspection method. This task checked no history, so it makes no such claim. A checked branch is not proof about all branches, future work, or universal lane behavior.
- **Unclear ownership or evidence:** Mark uncertain, identify the exact unresolved question, and stop the dependent action. Do not turn absence of evidence into a pass, a rights clearance, a perceptual conclusion, or permission to modify another domain.

## Scope note

The checklist can improve task classification; it cannot by itself verify historical scope discipline or justify checking SHONEN box 4. That requires the named non-author verifier and the separate, scoped repo-history evidence specified in the round plan. Promotion/rank is outside this move.
