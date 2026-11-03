# audio: from spatial interchange to coded delivery

Candidate reading only, checked 2026-11-03. Assimilation requires the user’s later manual instruction. No runtime trials, installation, corpus admission or assimilation occurred. This is a historical-to-still-published standards transition, not a claim about 2026 perceptual state of the art.

## Timeline and source roles

- **2011, interchange baseline:** Nachbar, Zotter, Deleflie and Sontacchi's [ambiX proposal](https://ambisonics.iem.at/proceedings-of-the-ambisonics-symposium-2011/ambix-a-suggested-ambisonics-format), Ambisonics Symposium, June 2–3, discusses incompatible ordering/normalization conventions and proposes a common representation plus an adaptor matrix for reduced or mixed-order signals. Read the introduction and format section. This is the hosted 2011 PDF; a search preview mentioned later comments, but those were not present in the opened PDF and are not attributed to this version.
- **2018, delivery extension:** Skoglund and Graczyk's [RFC 8486](https://www.rfc-editor.org/rfc/rfc8486.html), October 2018, extends Ogg Opus with Ambisonics mapping families 2 and 3. Read sections 3–5: ACN/SN3D conventions, optional non-diegetic stereo, and family 3's decoder demixing matrix distinguish channel meaning from channel count. The matrix's coded representation and header limits are part of the transport contract.
- **Current check:** the [RFC status page](https://www.rfc-editor.org/info/rfc8486/) still identifies Proposed Standard; the [errata record](https://www.rfc-editor.org/errata/rfc8486) lists editorial erratum 7342, verified 2023-02-13. This checks publication status, not deployed decoder coverage or a newest-codec ranking.

## What changes, what survives

Batch 1's RFC 7845 timing/container baseline already names RFC 8486 as an update; it does not develop spatial semantics. That baseline remains useful. The substantial addition is spatial interpretation: successful Opus decoding alone cannot establish correct orientation or normalization. The newer delivery mapping does not make the earlier interchange representation obsolete. My recommendation is to keep an explicitly described editable master and treat compressed distribution as a separately checked derivative. A project receiving legacy FuMa material should retain its declared convention until an explicit conversion is justified, rather than rename channels and assume equivalence.

For this lane, the useful boundary is signal and metadata verification. Head tracking, engine spatializer configuration and perceived immersion need separate evidence; no audio measurement here proves those outcomes. Neither paper nor RFC supplies rights to somebody else's recordings.

## Original post-hyaku comparison question

With one original four-channel directional fixture and separately identified stereo narration, can an interchange-to-delivery round trip preserve the intended channel identities and keep narration outside sound-field rotation? Compare declared conventions, matrix dimensions and decoded channel responses; include a deliberately mislabeled convention as a negative control. Report signal differences separately from spatial listening judgments. This experiment is proposed, not performed.

**Rights:** the RFC carries IETF Trust/BCP 78 terms and separate code-component provisions. No open redistribution license was established for the ambiX paper. This note links sources and contains original synthesis only; no paper, code, recording or diagram is copied.
