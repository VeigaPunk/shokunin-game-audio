# Specify which endpoint belongs to the loop

[Web Audio1.1](https://www.w3.org/TR/2026/WD-webaudio-1.1-20260922/), September2026 Working Draft, retains the exclusive loopEnd convention already present in the June2021 Recommendation. This is continuity, not a newly invented looping method or browser certification.

Sections1.9.2 and1.9.5 distinguish the endpoint from the last included content. Loop positions use buffer time, independent of playbackRate; positions can fall between sample frames. Fractional positions and rate changes involve interpolation. Section1.9.5 is explanatory; normative playback requirements are separate.

For Audio asset handoff, record the intended interval and units alongside seam measurements. A last included sample index is not automatically an exclusive endpoint. A clean join measured on the master does not establish identical output after interpolation or import. Comparing rendered output is a separate, authorized measurement, not a source guarantee.

This adds endpoint interpretation beside existing import-default coverage, without changing engine settings. Original commentary only; W3C licensing requires notices for copied or modified material. No code, source capture, playback or integration is supplied.
