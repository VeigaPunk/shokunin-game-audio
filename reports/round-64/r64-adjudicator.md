# r64 Sol adjudicator — audio lane, wave `shokunin-train-20261013-w3`

Adjudicator: Sol (parent session), host devin, 2026-10-14. Scope: round 64 declared coverage move — map the wValidBitsPerSample→codec reclassification sweep under the act-forced ffmpeg bridge, pinning step boundaries as tracked controls.

## Declared claim (verbatim)

"the reclassification is a step map over valid-bits values — sweep wValidBitsPerSample through a controlled range under the SAME act-forced route, record per-value the ffmpeg-negotiated codec/sample-width and SoX decode sample count, and pin the boundary values where width steps. Land a tracked boundary-family pair iff a step boundary is established; else bounded UNKNOWN with eliminated hypotheses."

## Measured result

**ESTABLISHED with a falsification absorbed.** Three independent sweeps converge on an exact non-monotonic step map (author 74 variants, scribe 85, simplifier 17 mutants + boundary 39):

| valid-bits | codec | bridge samples |
|---|---|---:|
| 0 | container's (s16le) | 5,760 |
| 1–8 | pcm_u8 | 11,520 |
| 9–16 | pcm_s16le | 5,760 |
| 17–24 | pcm_s24le | 3,839 |
| 25–32 | pcm_s32le | 2,880 |
| 33–56 | NONE | exit 2 premature EOF |
| 57–64 | pcm_s64le | 1,440 |
| ≥65 | NONE | exit 2 |

Boundaries: 0|1, 8|9, 16|17, 24|25, 32|33, 56|57, 64|65 — all adjacent-pair pinned.

**Falsified clause absorbed**: the map is NOT a pure function of valid-bits — it is gated on the WAVE_FORMAT_EXTENSIBLE envelope (tag==0xFFFE ∧ cbSize≥22 ∧ PCM-GUID); at fixed vb=17 different envelopes yield s16le/alaw/mulaw/adpcm_ms/mp3/ac3/none. The claim survives scoped to the envelope; the knowledge entry and this report carry the precondition verbatim. Bonus corrections: `s24le ∧ block_align==4·ch ∧ bpcs==24 → f24le` promotion; count law needs `×nb_channels` at canonical bits; residue is alignment×width (vb17 on a 24-bit container decodes lossless 3,840).

## Adjudicator's own reproduction (committed tree, HEAD `4c12342`)

- `ffprobe` on all four spot pairs: v8→`pcm_u8`, v9→`pcm_s16le`, v25→`pcm_s32le`, v56→`unknown`, v57→`pcm_s64le`.
- `sox pair_valid_8.wav -n stat` → `Samples read: 11520`; v57 → `1440`; v56 → `FAIL formats: can't open input file ... premature EOF`, exit 2.
- `measure_audio.py --probe-ui-extensible-valid-25-r64` → exit 1, receipt shows `codec_name=pcm_s32le, bits_per_sample=32`, designed failure summary.

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r64-author.md` + tracked +92/−5 | 74-variant sweep 0 mismatches vs composed law; ledger 92 (44/48); prior-86 byte-identical |
| critic | `r64-critic.md` | envelope-gate falsification (A-series); hidden codec flips f24le/f16le; named-undecodable codecs exit-0/0-samples third class; nb_channels factor |
| reviewer | `r64-reviewer.md` | r63 audit AGREE-all (86/86 receipts byte-identical, 3 generations convergent); independent re-fetch of upstream tag confirms formats.c citations |
| baseline | `r64-baseline.md` | frozen `37d4c57` 43/43 exits, 86/86 rows, 84/86 byte-identical (2 known path couplings) |
| scout | `r64-scout.md` | full step map live pre-author; packet-granule stepping with bitrate; builder/measurer insertion pointers |
| scribe | `r64-scribe.md` | knowledge-entry draft (landed verbatim `corpus/knowledge/2026-10-13-sox-validbits-codec-map.md`); f24le promotion; lossless-3,840 container proof |
| simplifier | `r64-simplifier.md` | minimal-diff verdict: {8,9}+{24,25} complete the width-step cover (16|17 already tracked), {56,57} pins s64le re-entry; optional {32,33} adjacency-only |
| boundary | `r64-boundary.md` | stdin act predicate same buffer but ffmpeg bridge on stdin broken two ways (undrained pending_buffer→EPIPE; stdio-prefetch offset loss); no second autodetect on pipe (au tail-call unconditional, .snd-magic only); non-USING_FFMPEG retained UNKNOWN |
| verifier | `r64-verifier.md` | **AGREE all four claims** — 92-cmd replay 44/48, 86/86 receipts byte-identical + 6/6 new receipts; pair discriminators live; envelope-gate spot-checks (cb21→NONE vs cb22→s24le); commits resolve |

## Disclosures recorded (none gate-affecting)

- Reviewer nit N2 (fixed `5cc0eb0`): r63-adjudicator overstated retained source material; corrected to upstream-tag citation posture.
- Verifier methodology note: an early relative-path compare showed false diffs — harness artifact, corrected compare gave 86/86 identity.
- Sibling misfire: a wrong-cwd ledger rerun clobbered tracked `corpus/live/r63-author/ledger-r63.tsv` mid-wave; author caught + `git checkout`-restored byte-exact; boundary flagged independently. Watch item: `run_ledger.py` output path is hardcoded.
- Boundary disclosure from r63 retained: ffmpeg child exit status never reaped; one fd leak per act-routed open — evidence-quality note, not gate behavior.

## Per-axis verdicts

- **coverage: improved locally** — 86→92 ledger commands; three boundary-straddling pair families tracked; dead band + s64le re-entry pinned.
- **depth: improved locally** — the map is now source-attributed (ff_get_pcm_codec_id table + wavdec promotion) with gate preconditions and three convergent sweeps.
- **calibration: unchanged** — thresholds untouched; designed exit-1 shape preserved.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

This host only (SoX_ng 14.8.0.1 USING_FFMPEG build + ffmpeg n9.0.1); map gated on 0xFFFE∧cbSize≥22∧PCM-GUID; non-extensible and float-subtype GUIDs unexercised; stdin+ffmpeg-bridge dead combination disclosed; no standards/fidelity/production inference.
