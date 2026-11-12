# Audio: a coded number needs its blocking strategy

[RFC9639](https://www.rfc-editor.org/rfc/rfc9639.html), December 2024, sections 8.2, 9.1 and 9.1.5, formalizes FLAC's frame accounting. Publication does not date the codec's invention.

With fixed blocking, the coded number counts preceding frames; with variable blocking, it counts preceding samples. The strategy cannot change within a stream. A shorter final frame is compatible with fixed blocking. The number encoding resembles UTF-8 but extends beyond ordinary Unicode encoders' range. These are numeric fields, not text.

**Proposed practice, unperformed:** Build a tiny header-accounting model, not a decoder. Give it three invented block lengths: 1024, 1024, 320. Compare fixed-strategy frame ordinals against variable-strategy sample offsets, retaining the final partial block. Add controls that switch strategy midstream and mislabel a sample offset as a frame ordinal. Set expected acceptance and offsets before execution. Report input tables, oracle calculations, actual outcomes, version and hashes. Limit this to six synthetic cases and thirty minutes, without codec execution or production files.

This adds seek-accounting interpretation to the existing decoded-sample-checksum reading. A successful model would not certify FLAC conformance, valid CRCs, decoder safety or audio quality. Nothing was executed; no training or assimilation.

RFC rights invoke IETF Trust terms. Original commentary and invented cases only; broader reuse clearance is not asserted.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-12-flac-coded-number-units.md.
