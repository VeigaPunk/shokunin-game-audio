# Audio sampling rate is not always the packet clock

[Schulzrinne and Casner's RFC3551](https://www.rfc-editor.org/rfc/rfc3551.html), July2003, separates RTP timestamp interpretation from decoded audio accounting.

Channel count does not multiply timestamp frequency. The clock usually matches sampling frequency, with exceptions.

G.722 is the instructive compatibility exception. Its audio sampling rate is16000Hz while its RTP clock is8000Hz. The specification explicitly preserves the earlier erroneous assignment for interoperability and adds clarification rather than silently changing the wire convention.

For Audio's realtime-transport reading frontier, record payload format, timestamp clock, decoded sampling frequency and channel count separately before interpreting duration. A clock discrepancy alone does not prove resampling or corrupted audio. This is metadata interpretation, not engine integration.

Unlike Rubber Band's frame-count and onset compensation contract, the issue here is a protocol clock that deliberately differs from the represented signal. No execution or implementation claim.

Original commentary only. The RFC's copyright statement permits explanatory derivatives subject to notice requirements; source copies and implementation rights remain separate.
