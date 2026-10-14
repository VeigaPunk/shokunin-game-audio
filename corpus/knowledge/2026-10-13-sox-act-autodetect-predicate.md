# SoX_ng `act` autodetect predicate — byte-exact routing rule (round 63)

- Source: round-63 seat evidence (`reports/round-63/r63-{author,scout,critic,
  boundary,scribe,reviewer,baseline}.md`); upstream sox_ng-14.8.0.1 source tag
  (`sox_ng-14.8.0.1` on codeberg — `src/formats.c` + `ffmpeg.c`, fetched at
  analysis time by r63-boundary and re-fetched independently by r64-reviewer;
  no copy is committed — citations re-verify against the upstream tag); binary
  disasm receipts `corpus/live/r63-boundary/disasm-act.txt` of
  `/usr/lib/libsox_ng.so.3.0.0` (r63-scout + r63-boundary).
- Verified at: 2026-10-13, host `/usr/bin/sox` SoX_ng v14.8.0.1
  (`pacman -Q sox` = 14.8.0.1-1, USING_FFMPEG build), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX or ffmpeg version/build changes (the act row is
  `#if USING_FFMPEG`; ffmpeg-less builds compile `AUTO_DETECT_SIZE 132` and
  have no act check at all), or when authoring new WAV fixtures whose header
  shape moves payload content across file offset 256.

## The predicate (complete)

SoX reads the first **257 bytes** once (`AUTO_DETECT_SIZE`, sized "for act")
and runs a first-match-wins CHECK table. The act row — the only act rule —
is `CHECK(act, 0,4,"RIFF", 256,1,"\x84")` (formats.c:93), ordered before the
wav rows (:95–97). On this build:

    detected == "act"  ⟺  readable ≥ 257 B
                          ∧ file[0:4] == "RIFF"      (literal, case-sensitive)
                          ∧ file[256] == 0x84        (exact offset, exact value)
                          ∧ no earlier row matched   (gsrt "ring.bin\0"@16;
                                                       hcom "FSSD"@65 ∧ "HCOM"@128)

Measured on the r61 pair family: 1 value of 256 fires; 1 position of 11,588
fires; `WAVE`@8 is **not** a conjunct (RIFF+0x84@256 without WAVE → `act`);
extension is not consulted on a match. File offset, not payload offset:
inserting a JUNK chunk relocates which payload byte is tested.

## What "act" routes to

`act` names the ffmpeg pseudo-handler (ffmpeg.c names[]; description "G729A
speech compression" — the rule exists so real ACT voice-recorder files, which
look like PCM WAV, reach ffmpeg). Its startread popens
`ffmpeg -loglevel quiet -nostdin -strict -2 -i FILE -f au -` and reads the
child's stdout with the **au** handler. One handler is chosen once; a
startread failure is terminal (`open_read` → `goto error`): there is no
re-detection and no fallback to `wav`. ffmpeg's stderr and exit status never
reach SoX — a missing codec, a demux failure, and a missing ffmpeg binary are
all indistinguishable `premature EOF` from the au reader.

## Observable routing signatures

- `sox -V4 <f> -n stat 2>&1 | grep 'detected file format type'` → `act` vs
  `wav` — the authoritative receipt (fires before any decode).
- `sox --i <f>` → `Input File … (ffmpeg)` suffix + **absent** Duration line
  = bridge; no suffix + Duration present = native. Caveat: the `(ffmpeg)`
  suffix is a handler/extension-name mismatch marker — it is suppressed when
  the extension already names the handler (e.g. a `.act` filename), so a
  missing suffix alone is not proof of native routing.
- Decode consequence on the valid17 family: `act` → ffmpeg path → 3,839
  samples (r62 packet-residue law); `wav` → native reader fatal
  `number of valid bits exceeds the number of bits per sample`, exit 2
  (a receiptless `CalledProcessError` inside the project measurer).
- Forced routes for controls: `sox -t wav …` (native, bypasses detection),
  `sox -t act` / `sox -t ffmpeg …` (bridge, byte-256-independent).

## Fixture-authoring rule (fragility, now pinned)

For the 68-byte-header extensible family, file 256 = payload byte 188 =
sample 94 LSB. Any payload/header edit that changes file byte 256 to
≠`0x84` silently reroutes SoX to the fatal native reader; any file shorter
than 257 B can't trigger act; any insertion before `data` moves the tested
payload byte. SHA-pin the byte, or use the r63 tracked pair
`corpus/live/round-63/pair_route_{84,00}.wav` (sole byte-256 diff,
`--probe-ui-route-act-{84,00}-r63`) as the pinned control.

## Bounded unknowns retained

- Other hosts/builds untested; non-ffmpeg SoX_ng builds lack the act row.
- Whether any *other* pre-act CHECK can match exotic RIFF payloads is
  source-enumerated (only gsrt/hcom lack an offset-0 anchor) but only those
  two were exercised.
- stdin/pipe path (257-B pending-buffer replay) unexercised; `--magic`
  off by default and unchanged in effect on these files.
- ffmpeg child exit-code/stdio plumbing (exit status never consulted;
  one fd stays open per act-routed open — boundary's disclosure).
