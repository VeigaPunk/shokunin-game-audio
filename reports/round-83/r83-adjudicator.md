# r83 adjudication — pw-cat/pw-record arg lattice

**Verdict: ADMIT-with-findings** — committed `a151a226`, +2426/−3, 7 entries / 128 legs, three green family runs on record (author ×2 + critic replay + verifier ×2 on frozen bytes).

## Dossier

| seat | verdict | commit |
|---|---|---|
| author | 128 legs, 2 green runs | `a151a226` |
| boundary (pre-landed `9725e53` corrections) | folded pre-authoring | scout+boundary |
| critic | ADMIT-with-findings — third green replay; F1–F3 all latent | `15789964` |
| reviewer | PASS-with-findings — 5 folded corrections re-measured live | `52c5d807` |
| simplifier | PASS — T1–T7 net −8 patch (unapplied, queued) | `de97d2f6` |
| verifier | VERIFIED — normal sha byte-identical, 128/128 ×2, 13/13 re-derivations | `19945856` |
| scribe | boundary INTACT; author citation-defective (ADJ-1) | `2b221233` |

## Laws admitted

Two-class malformed-prop lattice (silent `}{ garbage` vs hard-error `a=b }{ c=d`/`{ bad`/`media.name=`; rc 255 pw-props vs rc 1 pw-cat/pw-record; `a=b,` partial land); empty/whitespace `-i/-o/-P` SIGSEGV family rc=−11; `-d` real transport delay (~1.0 s at `-d 1.0`); `-l 1000` prop-only; `-l -5`→4294967056 uint32 wrap; resample full-wave `|x|` artifact (fundamental destroyed, octave dominant); `[ MONO ]` = 0.5(L+R).

## Queued corrections (fold queue, measure_audio.py)

- Critic F1: entry-3 `-d 0.25`/`-l 1000` arms need min-count + `linked` gates (empty transports pass silently — live-proven).
- Critic F2: anchor the substring unload predicate (`_gst_r81_sink_module_index` family — kills foreign nested-name modules; shared helper, fixes r81/r82/r83).
- Critic F3: legs spawn `env=None`; `PIPEWIRE_NODE`/`PIPEWIRE_PROPS`/`PIPEWIRE_LATENCY` override explicit args — scrub or pin.
- Simplifier T1–T7 (−8 net lines, patch `b969518c` staged in `corpus/live/r83-simplifier/`).
- Reviewer F2: transport/peak envelopes 2–4× looser than boundary measurements — tighten.
- Scribe ADJ-1: author report cites a red-run stamp (22:01:05Z committed receipts are green+byte-faithful — provenance correct, stamp wrong).
- Critic F4–F7: med_clean gate transparency, `-n ''` nodes_not_seen fail-open, `dm_move`/`pc_drop` arm gates.

## Bounds

PipeWire 1.6.8 / libpulse 17.0 / WirePlumber 0.5.17, host under sustained load 55–130. `m_alone` recorded as named outcomes (never asserted stable); resample zero-fraction drift 8.3→14.6% reconciled as window content. No blocker.
