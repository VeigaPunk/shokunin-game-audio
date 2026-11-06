# Audio: hash the samples, not the container

[RFC9639](https://www.rfc-editor.org/rfc/rfc9639.html), December2024 Standards Track, specifies FLAC's lossless PCM format. This publication date does not date the codec's invention or prove a superior shipping choice.

STREAMINFO's MD5 describes unencoded audio, not the complete file. Zero means unknown, not successful verification. Its input interleaves channels samplewise as signed little-endian values; nonbyte depths require sign extension. Hashing compressed bytes or a WAV header answers a different question.

For master-asset handoff, separate container identity from decoded-sample consistency. This adds a lossless verification distinction to the existing lossy-import warning. Matching this field does not establish provenance, listening quality, metadata preservation or an engine's behavior. Retain independent asset records; no decode, checksum test or runtime integration occurred.

Selected streaminfo, representation, security and copyright sections read. Malformed payloads still require bounded parsing. The RFC's2024 notice applies IETF Trust publication-date terms; extracted code requires Revised BSD notices. Original commentary only, no code or source reproduction. Known audio-format domain; proposed new FLAC mechanism coverage within the reviewed inventory.
