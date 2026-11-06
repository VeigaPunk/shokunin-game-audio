# Audio: channel count does not name speakers

[Microsoft WAVEFORMATEXTENSIBLE](https://learn.microsoft.com/en-us/windows/win32/api/mmreg/ns-mmreg-waveformatextensible), page updated June20,2023: extending WAVEFORMATEX adds multichannel and precision information while retaining backward representation compatibility. This is a documentation date, not the format's invention date.

The channel mask assigns speaker positions. Interleaved channels follow ascending set-bit order, and the number of set bits should match the declared channel count. Counting channels alone therefore cannot establish their speaker meanings.

For asset handoff, preserve layout alongside sample rate and count; this complements existing loudness metadata and codec-import notes. A structurally plausible header does not prove that the actual samples were authored in the declared order, nor that an engine preserves that layout. This is static format interpretation, not mixer routing or a playback test.

Selected member and remarks sections read. The page labels DirectShow legacy; no recommendation to adopt it follows. Documentation repository CC BY4.0 requires attribution and applicable change notices; asset rights remain separate. Original commentary only.
