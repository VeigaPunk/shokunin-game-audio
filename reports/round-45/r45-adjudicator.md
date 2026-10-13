# Round 45 adjudicator — Sol (non-author)

## Verdict: admit the one declared calibration move

| Axis | Verdict | Reason |
|---|---|---|
| Depth | **unchanged** | No new sound-design method or general proof of the duration comparator. |
| Coverage | **unchanged** | Two opt-in controls bracket an already covered ordinary UI gate; they do not expand production or asset-family coverage. |
| Calibration | **improved** | A source-generated, hash-pinned negative-side interior/exterior pair now isolates the existing `.12 s ± .001 s` ordinary duration check. R44 tested the positive side; R27's `.020 s` pairwise distinctness is a different gate. |

**Admit**: at least one axis improved, and the inspected source/receipts demonstrate no scoped harm. This is an admission of *these measured numerical fixtures*, not an equality or universal duration claim. Clean-before is `4de93bf829f539d77c0ebc4706dfe95903ab2f17`.

## Independent evidence review

I read the R45 LOG declaration, all eight wave-one reports (`r45-{scout,executor,alt,critic,reviewer,simplifier,scribe,guard}.md`), named non-author `r45-verifier.md`, the source diff, and the raw 50 receipt JSON files cited in the verifier's serial ledger. The ledger names **50 distinct existing fresh receipt paths**, `20261013T063747667567Z`–`20261013T063840271762Z`; its recorded exits are **21 exit 0 / 29 expected fixture-validation exit 1**. Excluding new #2/#3 leaves prior48 **20/28**. The initial and final normal receipts are exactly equal JSON and equal the R44 final normal receipt: 17 canonical measurements, no failures. Six normal receipts (#1, #46–#50) are equal. The #45 invalid receipt has eight expected statuses: short_sections/odd_sections section count, corrupt decode, wrong_format/native24/stereo48/mono441 format, native16 pass. The carried five generic `_alt` comparisons, four family groups, thresholds and sections remain represented in the fresh normal receipts; canonical artifacts have no diff versus clean-before. Fresh replay recorded no runner setup failures.

| Fresh mode | SHA-256 of generated WAV (independently recalculated) | ffprobe duration | Python signed / absolute `duration - .12` | Other measured gates | Exit and failures |
|---|---|---:|---|---|---|
| #2 `--probe-ui-lower-tolerance-5713` | `94f1ad9459fbfc06120668e3ebe5743a2d8690c66238d586f05006102811dd99` | `.119021 s` | `-.0009789999999999938` / `.0009789999999999938 s` | 5713 frames, 48k mono PCM16, peak `.27947998046875`, RMS `-16.399347369151716 dBFS`, centroid `1663.1001045998237 Hz` | **0**, no failures |
| #3 `--probe-ui-lower-tolerance-5711` | `2b4b0323f040a65b431a984e4fde5866f5c412754206c928e1fa21358adb9ab8` | `.118979 s` | `-.0010209999999999941` / `.0010209999999999941 s` | 5711 frames, 48k mono PCM16, peak `.27947998046875`, RMS `-16.3992750775437 dBFS`, centroid `1627.5978467387597 Hz` | **1**, sole `duration: outside ±1 ms` |

Raw receipts: `corpus/live/runs/20261013T063748725989Z-ui-lower-tolerance-5713/measurements.json` and `corpus/live/runs/20261013T063749795923Z-ui-lower-tolerance-5711/measurements.json`, paths relative to `.shokunin/audio/`. Both signals pass peak `< .95`, RMS `>= .001 FS`, and UI centroid 250–4000 Hz. The selected source-generated pair exactly matches executor hashes; the independent alternate pair has different hashes (`745bb3df...` / `e23080bc...`) and the same gate polarity. Ideal frame offsets are not substituted for actual ffprobe output or parsed subtraction.

The source diff from clean-before adds a fixed builder for 5713/5711 and two opt-in dispatch/receipt paths in `build_artifacts.py` and `measure_audio.py`. Existing `SPECS["ui"]`, ordinary `abs(duration-spec[0]) > .001`, thresholds, and normal mode are unchanged. `git diff --check` and canonical-artifact diff checks both passed. Old 17 canonical SHA/metrics are evidenced by equality of the fresh normal receipt to the R44 baseline; the prior-mode replay and invalid statuses provide bounded preservation evidence, not a proof of arbitrary future audio behavior.

## Error classification and limits

Executor's initial draft copied four R44 positive-side floating magnitudes into negative-side delta cells; parent corrected those four **report transcription** cells before integration from unchanged measured durations. This is neither numeric fit nor runner setup failure. Alt's first relative-path helper exception was a **setup error**, corrected before its successful independent fit. The 5711 sole duration failure is the **expected completed numeric failed fit**. Critic's disposable 5712 WAV had ffprobe `.119000`; parsed `abs(.119-.12) = .0010000000000000009` **fails** the current strict `>.001` float expression. It was not integrated and cannot be called an equality pass. No exact equality, perceptual duration or quality, production, rights, engine, publishing, rank, or promotion conclusion follows. SHONEN remains four checked boxes, **no promotion**. No push/merge is part of this verdict.

Commands I ran: `git diff 4de93bf829f539d77c0ebc4706dfe95903ab2f17 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py; git diff --check 4de93bf829f539d77c0ebc4706dfe95903ab2f17 -- .shokunin/audio/corpus/fixtures/build_artifacts.py .shokunin/audio/corpus/fixtures/measure_audio.py; git diff --quiet 4de93bf829f539d77c0ebc4706dfe95903ab2f17 -- .shokunin/audio/corpus/artifacts; echo canonical_diff_exit=$?` — overall exit **0**, final `canonical_diff_exit=0`; the `git diff --check` command itself exited **0** in this sequence. Receipt reads, SHA calculations, and comparisons above were direct Python reads, not runner reruns. The exact 50 replay commands/exits are individually listed in `r45-verifier.md`; I did not claim to rerun them.
