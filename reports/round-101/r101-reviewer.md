# r101 ReviewerR101 — wave-1 falsification of K1/K3/K4/K5 candidate facts (read-only seat; transcribed verbatim by the L1)

Seat: `W2RoundAudio-8.ReviewerR101-2` (reviewer, lane-dispatched — still the lane). Scratch `/tmp/r101-reviewer/` (not evidence). ART = `/home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/fleet-ledger/.ufo/waves/kaika-w1/audio-art.md`. Host ffmpeg n9.0.1; PDFs/HTML fetched 2026-10-19.

| Fact | Command | Result |
|---|---|---|
| K1 0.12 s / 2.5 s / 4 s tone | loudnorm sweep, `-f null` | −inf→peak −1.00 linear; out_i −24.05 linear; dynamic. **Reproduced** |
| ui.wav TP −8.50→−1.00 | loudnorm on corpus/artifacts/ui.wav | **Reproduced** |
| 400 ms boundary | sine 0.399 / 0.400 / 0.401 s | −inf / −24.05 / −24.05. **Exact at 0.400 s** |
| 3 s cut-over | sine 2.99 / 3.0 / 3.01 s | linear −24.05 / dynamic −23.95 / dynamic. **Reproduced** |
| Sub-400 ms mechanism | ebur128.c:571-573 (`-HUGE_VAL` when no block); af_loudnorm.c:461-463 | **Source-explained** (offset=+inf → `target_tp/true_peak`); mechanism is the reviewer's derivation, outputs match |
| Trigger is the −70 LUFS gate, not length | 2.5 s aevalsrc at peak −60 / −70.5 / −80 dBFS | −60: in −63.05, linear normal (out −23.95). −70.5 and −80: in −inf, out −4.05, TP −1.00. **ART's length-based wording is incomplete** |
| 3 s rule source | af_loudnorm.c:450, 697-702 | first chunk is `frame_size(3000)`; a shorter total input is a buffer-size check, not a loudness rule. **Source-explained** |
| K2 LRA 0.00 → dynamic 192 kHz | steady 440 Hz, linear=true | **Reproduced**; af_loudnorm.c:820-821 |
| K2 LRA 6.00 → linear 48 kHz | stepped 440 Hz | **Reproduced** (output_tp −18.51) |
| K2 LRA 12.10 > target 11 → dynamic | measured_LRA=12.10 control | **Reproduced** (dynamic, 192000 Hz); l.821 |
| K2 12 kHz: output_tp −25.56, sample −25.6, true −22.2 | recheck | **Reproduced** |
| K3 dual-mono delta, 1 kHz −20 dB | ebur128 metadata, 10 s | −41.070 → −38.060 = **+3.010 LU**. f_ebur128.c:782-784 applies `-= pan_law`, default −3.01029995663978 (l.173) |
| K3 ambience / stem_sections | same | −30.697→−27.686 (+3.011); −24.704→−21.694 (+3.010). **Reproduced** |
| K3 impact TP | ebur128 TP vs aresample 4x sample peak | SP −1.84; TP −0.7 (ebur128) / −0.66 (4x). **Reproduced**; overshoot ≈1.18 dB, not 1.1 |
| K3 movement_alt | ebur128 | SP −3.9, TP −3.1 (not in ART) |
| K4 compress/mode default | Godot class ref property lines | 4.3 `= 0` Disabled; 4.4 and stable `= 2` QOA. **Reproduced** |
| K4 tutorial 4.4 | HTML text | "…compression modes can be chosen from for WAV files: Disabled (default)…". **Reproduced** |
| S005 line numbers | fetched n9.0.1 and master af_loudnorm.c | ART cites l.456, 462, 746, 757, 826-828, 852, 862; n9.0.1 (and master) have 450, 463, 740/752, 757, 820-821, 846/856. **DIFFERS** |
| K5 ASWG recs 4/5/7/9/10/11 | pdftotext ASWG-R001 mirror | **Reproduced** (−24 (±2), −18 (±2), ≤−1 dBTP, "minimum of 30 minutes") |
| K5 BS.1770-5 pure tones | pdftotext PDF l.340-341 | quote **reproduced**; ART's "excludes pure tones" is **overstated** |
| S002 R128 V5 | pdftotext | −23.0 LUFS; ±1.0 LU impractical (h); ±0.2 LU QC (i); ≤−1 dBTP (m). **Reproduced** |

Per-entry recommendation (none cites tier-C S007 as sole support):
- K1: REJECT as written in the ART lead; re-admit after fix — the −inf trigger is "no 400 ms block above −70 LUFS", not "shorter than 400 ms"; the 3 s boundary is a buffer-size check; cite n9.0.1 lines.
- K3: ADMIT after fix — "+3.010 LU", cite f_ebur128.c:782-784; overshoot ≈1.18 dB.
- K4: ADMIT — every quote and default reproduced.
- K5: ADMIT after fix — drop "excludes pure tones"; mark "would contradict both specs" as [INF].

Defects in the ART lead (audio-art.md line numbers): 1 `:232-237` K1 length-based regime; 2 `:239-240, 258` S005 l.456/462 not at n9.0.1 (450/463); 3 `:270-271` K2 cites 826-828/121/852/862 → 820-821/115-116/846/856; 4 `:137` S005 row cites `master`; 5 `:304` overshoot 1.1 → ≈1.18 dB; 6 `:364-365` pure-tone overstatement; 7 `:295-302` "exactly 3.0 LU" → +3.010, mechanism uncited; 8 the round-101 files were absent at wave-1 review time (step-3 file checks deferred to wave 2).

Hygiene (seat's own statement): several commands hit the `__fnmcd` cd failure; all writes went to /tmp/r101-reviewer; no git commands; nothing written to the worktree.

L1 routing: findings 1–7 were forwarded to ExecLoudness-2 and ExecSources-2 before their entries landed.
