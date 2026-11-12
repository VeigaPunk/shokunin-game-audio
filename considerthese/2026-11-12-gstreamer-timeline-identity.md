# Audio: stream position is not the playback clock

GStreamer's [Clocks and synchronization](https://gstreamer.freedesktop.org/documentation/application-development/advanced/clocks.html), inspected November 2026, distinguishes absolute clock time, pipeline running-time and stream-time. This unversioned snapshot does not establish release history.

Running-time accounts for time spent playing, excluding pauses. Buffer running-time requires its timestamp and preceding SEGMENT information. Stream-time describes media position and can repeat during looping; it is not the synchronization clock. Sinks additionally account for latency. Non-live sources restart buffer running-time after a flushing seek, so a monotonic sequence must be scoped to its timing epoch.

**Proposed practice, unperformed:** Prepare a log of an original cue, pause/resume, a repeated two-second region and a flushing seek. Keep clock/base-time, segment, timestamp and reported position in separate columns. With a pinned GStreamer build, later compare segment conversion results against prior predictions. Include a control that incorrectly schedules from stream position. Report epoch boundaries, expected/actual running-times and unresolved metadata; never treat missing segment context as zero. Cap at twelve records and forty-five minutes, without live capture, network streams or engine integration.

This extends the audio transport frontier beyond RTP clock units. No pipeline was executed; no training or assimilation. Timing interpretation does not establish audible synchronization.

Original commentary and invented log only; documentation reuse clearance is not asserted.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-12-gstreamer-timeline-identity.md.
