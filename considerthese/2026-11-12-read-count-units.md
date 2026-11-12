# Audio: requested capacity is not decoded duration

The official [libsndfile API](https://libsndfile.github.io/libsndfile/api.html), File Read Functions, inspected November 2026, distinguishes sample items from multichannel frames. This unversioned snapshot does not establish release history.

Frame-based reads require storage for frames multiplied by channels. Item-based counts must be divisible by channel count. Return values use the corresponding unit. At end-of-file, a read can return fewer objects without error, while unused buffer space is zero-filled. Those padding zeros are not additional decoded content.

**Proposed practice, unperformed:** Make a seven-frame stereo PCM fixture with distinct channels. Read it into capacity for ten frames through both count conventions, on independent handles. Predict equal populated samples but return counts expressed in different units. Compare a duration calculation based on returned frames with an intentionally wrong capacity-based calculation. Add a second read at end-of-file. Report fixture hash, library version, channel count, requested/returned counts, populated range and padding separately. Cap at four reads and thirty minutes. Use correctly sized buffers, not an overflow test.

This complements channel-mask and codec-tail notes: channels identify layout, while API counts delimit valid output. No calls were executed; no training or assimilation. Success would not establish format-wide decoder correctness.

Original commentary and invented fixture only. Software and documentation rights are distinct; no broader reuse clearance asserted.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-12-read-count-units.md.
