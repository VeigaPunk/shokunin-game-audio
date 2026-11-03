# audio: curated sources to consider — 2026-11-03

**Status: unassimilated future reading after hyaku.** This is a reading queue, not an admitted lesson, training round, or capability claim. Original summaries and source links only; no source code or third-party prose copied. No candidate code was run, installed or integrated. Existing daily-reflection files and source registries remain unchanged.

Selected after reviewing this lane’s PROVINCE, supplied source registry and historical considerthese context. Two complementary sources are enough for this first batch: one method/specification and one maintained implementation.

## 1. RFC 7845: Ogg Opus framing and sample timing

- **Source / type:** [RFC 7845: Ogg Opus framing and sample timing](https://www.rfc-editor.org/rfc/rfc7845) — specification. Opened 2026-11-03.
- **Why this lane:** Targets the declared ship-codec round-trip frontier: avoid mistaking encoder delay or padding for a broken loop seam.
- **Verified anchor:** Sections 4.2–4.6 distinguish pre-skip, PCM position, end trimming and seek pre-roll; the RFC page identifies RFC 8486 as an update.
- **Read first:** Read sections 4.2–4.6 before designing encoded-loop measurements.
- **Proposed later exercise (not performed):** After hyaku, propose an original impulse-plus-loop fixture with non-frame-aligned length. Record decoded sample count, onset alignment and seam discontinuity separately, including intentionally incorrect trimming as a negative control.
- **Rights:** IETF Trust / BCP 78 document terms; not public domain. Code-component terms are separate. [License evidence](https://www.rfc-editor.org/rfc/rfc7845).
- **Limits:** A container timing rule does not prove perceptual transparency or engine support. Consult RFC 8486 and errata for affected channel mappings. No engine wiring or rights clearance.
- **Duplicate review:** New specification beyond the existing BS.1770/R128 loudness and QOA/import sources. Exact/normalized primary URL absent from supplied lane inventory.

## 2. Xiph Opus reference implementation

- **Source / type:** [Xiph Opus reference implementation](https://github.com/xiph/opus) — repository. Opened 2026-11-03.
- **Why this lane:** Provides implementation and test-design reading for the unmeasured Opus codec frontier without repeating the QOA lead.
- **Verified anchor:** README identifies stored-file/game-soundtrack use and separates codec from container; COPYING specifies three-clause redistribution conditions and linked patent licenses.
- **Read first:** Start with README, COPYING, encoder/decoder API boundaries and the repository test layout; pin an exact revision before any later experiment.
- **Proposed later exercise (not performed):** After hyaku, compare a pinned reference decoder against the already-approved local decoder on original signals, separating codec error, container trimming and resampling.
- **Rights:** BSD-3-Clause-style COPYING, plus separately linked royalty-free patent terms; audit selected files and optional model/dependency terms before reuse. [License evidence](https://github.com/xiph/opus/blob/main/COPYING).
- **Maintenance evidence:** Opened commit history shows 2026-09-08 activity (328079c) and 2026-08 codec fixes. This is observed maintenance, not an assertion of the newest upstream commit. [History/release evidence](https://github.com/xiph/opus/commits/main/).
- **Limits:** libopus is not an Ogg file reader. Do not treat raw opus_demo framing as an Ogg asset, run upstream scripts now, or infer subjective sound quality from numerical error.
- **Duplicate review:** No Xiph Opus repository or RFC 7845 occurs in this lane’s supplied URL inventory. Exact/normalized primary URL absent from supplied lane inventory.

## Family-overlap and revision check

Method/specification: new source family in supplied lane inventory. Repository: new source family in supplied lane inventory. These checks include repository identity and publisher-domain overlap, not just exact URLs.

Repository revision evidence: [328079cfdade069a2fce6db5501b8de75c97d060; commit independently retrieved through the GitHub connector](https://github.com/xiph/opus/commit/328079cfdade069a2fce6db5501b8de75c97d060). This is a reading anchor, not proof of host compatibility; mutable README/license links above were inspected separately on 2026-11-03.

## Admission gate, later

Re-open and pin versions when hyaku work is authorized. State the narrow claim, build original positive and negative cases within this lane’s province, and retain measured limitations. Reading or successful third-party tests alone does not admit a capability. Attribution, redistribution rights and AI-training permission remain distinct; this queue makes no training-permission or asset-rights determination.
