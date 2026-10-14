# R76 adjudicator (Sol) — capture-side consumers: pw-record/parecord/arecord/ffmpeg

Round: 76. Wave: `shokunin-train-20261101-w15` (author landed late;
wave-B partially re-seated after the SWE-2 rate-limit kill — verifier
`93a485fc` → `54ba2a8e` on a deepseek-flash profile). Work commit
`d566a31`, folds commit `18deef6`.

## Declared move

`--probe-capture-r76`: the RECORD direction the corpus lacked — six
entries (gate, bounded, sever, name-axis, device-axis, roundtrip) over
pw-record / parecord / arecord / ffmpeg-capture, with named failure
classes, structural wav inspection, and parser-usability witnesses.

## Claim adjudication

- **Capture lattice CONFIRMED with corrections** — verifier AGREE on
  all 8 byte-level spot claims: TERM-finalize vs KILL-wound per
  consumer (pw-record/parecord `riff=8`/`data=0` rejected by `wave`;
  arecord `0x80000000` accept-and-lie 8134×; ffmpeg `0xFFFFFFFF`
  16389× inflated / 0-byte class), rc never the verdict (rc=1
  complete / rc=0 empty / rc=255 valid), `-D null` unpaced oracle
  exactly 192044 B in ~0.02 s, parecord ~1.9 s dead start, roundtrip
  960044 B nonzero with both content witnesses.
- **Prior-row stability CONFIRMED** — 17 base rows byte-identical vs
  the r75 canonical across three independent replays; baseline
  zero-drift (`2250be9` freeze → `d566a31`: +1150/−3, insertion-only,
  5,290 committed receipts untouched).
- **Canonical-sha determinism SCOPED** — verifier DISAGREE on the
  whole-receipt sha (1/3 reproduced): mechanism measured — a pw-record
  monitor node survives ≥1 s post-teardown and contends for the card,
  shifting `pw_capture_ports` inventory leaves and flipping
  `arecord_duration_hw` between `alsa_busy` and success rows. The
  verdict surface (`failures: {}` + every pinned leaf) is stable; the
  whole-file sha is quiescent-host bounded (reviewer LOW-3 confirmed).
- **critic D1 / reviewer MEDIUM-1 CONFIRMED — the round's real bug**:
  a zero-audio capture satisfied the TERM gate (`data(0)` is trivially
  `finalized`+`64k_aligned`); the author's own clean receipts carried
  the vacuous row twice. Verifier proved reachability: a 0.4 s TERM
  yields rc=0 + finalized + zero audio. Folded: `data_actual_zero is
  False` required on both sever TERM checks and `parecord_term_bound`.
- **Verifier N1/N2 CONFIRMED — unchecked legs armed**: `ffmpeg_alsa_t`
  had no check (rc=251 missing-file passed silently); device-axis
  `sysdefault`/`plughw_first`/`hw_first` were emitted-never-checked
  (canonical: working routes, rc=0 paced 192044 B). Both now pinned
  with named-busy carve-outs.
- **Gate/sever vacuity closed**: absent expected legs fail loudly;
  early-exit is a named dead-start failure, not a silent skip; arecord
  absence requires a recorded `*_blockage` entry.
- **Simplifier D1–D9 applied** — all replay-proven byte-identical
  (8 passes, 0 divergences).

## Corrections folded (`18deef6`)

- `data_actual_zero is False` on all three TERM-site checks.
- Sever/leg-presence totality: absent → failure, blocked row → named
  skip, early-exit → dead-start failure.
- `wave_frames_class` → `fmt_absent` when the fmt leaf is missing
  (was silently `inflated` — demonstrated honest→inflated flip).
- Gate `pwrecord_monitor_alias` records an explicit blocked row.
- `ffmpeg_alsa_t` + three device-axis legs armed (rc=0/finalized/paced
  192044 B or named busy — `alsa_busy` carve-out consistent with the
  bounded entry, LOW-7).
- Roundtrip: seat-neutral `live/capture-r76-roundtrip` scratch + label
  (was writing into `r76-author`'s scope, MEDIUM-2); real masked argv
  recorded (LOW-9); docstring now names the actual guard (LOW-6).
- PipeWire counter scrub regex fixed to `seq[:=]` — observed form
  `seq:7`; the `=` pattern never fired (now visibly normalizing).
- D1–D9: `data_4k_aligned`, dead `hw0`/`mon`/`env`/`line` bindings,
  dead `kill_riff` key, unreachable `out_kind` elif, `cap_rel` alias.

## Noted, not folded

- **Verifier N3**: parecord's default header declares **44100 Hz on a
  48000 stream** (identical 393216 B at both rates ⇒ no resample) —
  ~0.19 s timing error on any header-derived dead-start fit. The `fmt`
  leaf already carries the mislabel; recorded as a known-bias witness,
  not a pinned expectation.
- **r77 scout falsified an r76 row's universality**: arecord TERM
  shape is device-dependent — `sysdefault` lands
  `placeholder_80000000` + `alsa_read_eintr`, not the hw class. The
  sever lattice iterates `hw:` devices only; scoped honestly, r77
  material.
- Critic housekeeping: ~29 GB author scratch rotation debt (sweep at
  closeout); pgrep-based "no process remains" checks are not
  attribution-safe on a shared host.
- Whole-receipt sha is quiescent-host bounded (mechanism above);
  `failures: {}` + pinned leaves remain the deterministic contract.

## Seat accounting

9/9: author `d566a31` (+1150/−3, 6 entries, byte-identical ×2); scout
(8-point frame falsification pre-landing — explicit source tokens, the
5.8 GB/s null oracle, per-consumer TERM/KILL wound classes, roundtrip
peak −15.27 dBFS); boundary (229 cells — rc pure noise ×20, bound
units per consumer, dead-start measurement, cross-decoder disagreement
matrix); critic (D1 vacuity + gate/sever coverage holes + scrub/label/
argv defects — all folded); reviewer ADMIT-corr (MEDIUM-1/2 + LOW-3–10);
simplifier (D1–D9 byte-identical ×8 passes; correctly stopped before
evidence-bearing code); baseline zero-drift; verifier AGREE on claims
with N1–N3 new findings + sha-determinism scoping; scribe (audit
caught the 25 GB scratch debt, the F4 missing receipts provenance hole,
and the dynamic device-enumeration flap).

## Verdict

**ADMIT-corr** — the capture direction is armed with named classes and
parser witnesses; the zero-audio vacuity (the round's real defect) and
all three unchecked-leg surfaces are closed; canonical sha re-scoped to
quiescent-host. Bounded: PipeWire 1.6.8 / pacat 17.0-98 / alsa-utils
1.2.16 / ffmpeg n9.0.1, this host. Work `d566a31` + folds `18deef6`;
report-last commit follows.

r77 frontier seeds: source-selection lattice + monitor-vs-source
asymmetry (scout pre-measured: `stream.capture.sink` fallback law,
`sustained_after_target_loss`, 5-witness reader matrix, device-dependent
TERM shapes incl. `alsa_read_eintr`), the 2 GiB split-sentinel rename
(`<name>-01.wav`), hot-plug, format axis, `pw-cat`/`parec --raw`
integrity-witness gap, concurrent capture+playback.
