# audio: curated source to consider, batch 4 — 2026-11-03

**Status: unassimilated post-hyaku reading.** No training, capability admission, installation or candidate execution. 

## EBU Tech 3285: distinguish stored loudness metadata from measurement

**Source and revision:** [Broadcast Wave Format specification](https://tech.ebu.ch/docs/tech/tech3285.pdf), version 2.0, May 2011; [publisher record](https://tech.ebu.ch/publications/tech3285) dated 20 May 2011. Opened 2026-11-03.

**Source summary:** BWF adds a broadcast extension chunk to WAVE. Its version field governs interpretation of UMID and loudness metadata. Loudness values use signed integers scaled by 100, rounded with ties away from zero. Unused parameters use 7FFFh; out-of-range values must also be ignored. TimeReference counts samples since midnight at the declared sample rate. These fields describe an asset; their presence does not measure its current waveform.

**Read first:** §1.1 version compatibility, §2.3 field descriptions on printed pages 10–12, then §2.4 rounding and invalid-value handling on pages 12–13.

**Domain gap and novelty:** The existing audio queue covers metering, codec timing, resampling and stretching. This adds the handoff failure where a valid waveform carries stale, missing or misinterpreted measurement metadata. EBU publisher overlap is intentional; Tech 3285/BWF is a distinct format source, absent under those aliases from the reviewed inventories.

**Rights:** The publisher marks its site copyright EBU, all rights reserved. No open document or software license was established. Link and summarize rather than reproduce the document. Asset rights, redistribution and AI-training permission remain separate.

**Original future question, not performed:** Can an asset review distinguish “not measured” from an actual zero without trusting a stored loudness field? After hyaku, propose three original metadata records for synthetic PCM: a valid negative value, the unused sentinel, and stale data after a gain change. Separately record decoded metadata and fresh measurements; reject any review that treats the sentinel as silence or metadata as measurement proof.

**Limits:** This is broadcast interchange, not a game loudness target or evidence that an engine preserves BWF chunks.

