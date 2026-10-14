# R72 adjudicator (Sol) — third decoder: libsndfile transport matrix

Round: 72. Wave: `shokunin-train-20261101-w11`. Work commit `26baed1`.

## Declared move (coverage/runtime-breadth)

libsndfile 1.2.2 on the canonical 9-member × 4-transport corpus;
claim (as briefed): "3-decoder lattice partitions members into distinct
decoder-coverage classes: sox-only {txw-seekable/.f32-named},
sndfile-only {.snd-named}, ffmpeg superset on detect".

## Claim adjudication — critic/scout/boundary convergent corrections

| briefed clause | measured outcome |
|---|---|
| sox-only txw-seekable/.f32-named | CONFIRMED exactly (4 cells) |
| sndfile-only .snd-named | FALSIFIED-as-stated — sox also accepts {file,fifo} (sndr/504); class is sox∩sndfile vs ffmpeg-reject. The real sndfile-unique exemplar is `.au`-named identical bytes (frontier ext sweep, untracked) |
| ffmpeg superset on detect | FALSIFIED — ffmpeg detect set is the STRICTEST (8 < sndfile 10 < sox 11-14 cells); ffprobe does have a named axis elsewhere (.gsm accepts by extension) but not on this corpus |

## Measured lattice (committed receipt, byte-stable ×2)

- Exactly one transport fork: `extsuffix_snd` {file,fifo}=RAW/U-Law-500
  vs {stdin,redir}=Format not recognised — name axis, same partition as
  sox's sndr gate.
- txw = "unimplemented format" on all 4 (recognized-then-refused tier,
  unique to sndfile on this corpus).
- dec_act/dec_hcom = WAV/PCM16-278 on all 4 (no bridge fork).
- 5 members reject uniformly.

## Edge findings (boundary seat)

- fifo writer-hold: 50/50 identical at every hold — the r70 transition
  band was the SOX bridge's open-#2 artifact, does not transfer.
- tier onset exactly 12 B; `.snd` fallback opens even 0-byte; `.f32`
  never; ULAW fallback consumes the 12-byte sniff (frames=512 vs
  read=500); fallback case-insensitive.

## Seat accounting

scout, critic, boundary, scribe, simplifier all landed pre-commit with
byte-identical independent reproductions (36/36 cells equal across three
harnesses); author = operator-substituted (swe-2 seat produced no
scratch — promoted boundary's verified scratch arm per convention).

## Verdict

**ADMIT-with-correction** — the folded claim is the measured one;
briefed clause 2/3 falsified and recorded. Byte-identity of prior rows
by insertion-only construction; r72 rows byte-stable across 2 replays.
