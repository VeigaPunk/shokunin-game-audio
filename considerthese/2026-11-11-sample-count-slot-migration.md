# Audio: compatible slots can lose their old meaning

[EBU Tech 3306](https://tech.ebu.ch/docs/tech/tech3306v1_1.pdf), July 2009, sections 3.4 and A.2, assigns sampleCountLow and sampleCountHigh in RF64's ds64 chunk to the extended fact sample count.

The [June 2018 final notice](https://tech.ebu.ch/docs/tech/tech3306.pdf) directs further standardization to ITU's BW64 recommendation.

[ITU BS.2088-2](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.2088-2-202511-I!!PDF-E.pdf), November 2025 with 2026 editorial amendments, Annex 1 section 4, retains those positions as dummyLow and dummyHigh. Readers ignore them; writers set them to zero for compatibility. This dates the inspected edition, not the field change.

For audio handoff, identify RF64 versus BW64 before interpreting corresponding fields. BW64 zeros in these slots do not establish zero samples or silence. Shared layout does not preserve every field's meaning.

EBU's site and ITU's publication reserve rights. Original commentary only; no parser, playback, training or assimilation.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-11-sample-count-slot-migration.md.
