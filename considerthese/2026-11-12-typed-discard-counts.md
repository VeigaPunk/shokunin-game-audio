# Audio: typed discard counts

[RFC3611](https://www.rfc-editor.org/rfc/rfc3611.html), November 2003, section 4.7.1, defines a VoIP discard rate accumulated since reception began. It covers early/late jitter-buffer discards and excludes duplicate-packet discards.

[RFC7002](https://www.rfc-editor.org/rfc/rfc7002.html), September 2013, sections 1–3, augments extended reports with discard counts typed as duplication, early arrival or late arrival. Counts may be interval or cumulative. This does not redefine the older rate.

The newer metric excludes higher-layer decoding drops. Its block depends on measurement information in the same compound RTCP packet; without the measurement interval, the block must be discarded. Missing context is not a zero count.

For audio diagnostics, preserve the report type, discard category and measurement span before comparing values. A duplicate discard alone does not establish missing audible content, and a packet count is not a rate. These are report-interpretation boundaries, not listening results, network measurements or engine changes.

RFC3611 permits conditional explanatory derivatives; RFC7002 invokes IETF Trust terms. Original commentary only; broader reuse clearance is not asserted.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-12-typed-discard-counts.md. No training or assimilation.
