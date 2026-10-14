# r63 Sol adjudicator — audio lane, wave `shokunin-train-20261013-w2`

Adjudicator: Sol (parent session), host devin, 2026-10-13. Scope: round 63 declared depth move — pin or falsify the `act` autodetect predicate disclosed at r62.

## Declared claim (verbatim)

"the `act` trigger is a specific byte predicate at/near offset 256 — falsify or pin it with a controlled sweep: which byte positions and which values at each position flip `sox --i`/decode routing between `(ffmpeg)` and native `wav` on this file family. Land a tracked sweep-matrix control iff a predicate is established; else bounded UNKNOWN with eliminated hypotheses."

## Measured result

**Predicate established exactly**, five independent derivations convergent (author 23,738-row sweep, critic 1,408 probes, scribe 293, simplifier ~30 mutants, boundary source+disasm):

```
detected == "act"  ⟺  len ≥ 257 ∧ file[0:4]=="RIFF" ∧ file[256]==0x84 ∧ ¬(earlier CHECK)
```

Earlier CHECKs that preempt: gsrt `ring.bin\0`@16, hcom `FSSD`@65 ∧ `HCOM`@128 (boundary + critic + simplifier all demonstrated). No fallback chain: `open_read` detects once, dispatches once, `goto error` on failure — closes r62's `act→au→ffmpeg` ordering UNKNOWN. `act` resolves to the ffmpeg pseudo-handler (G729A, ffmpeg.c:116); the terminal `premature EOF` is the au reader on an empty ffmpeg pipe.

## Adjudicator's own reproduction (committed tree, HEAD `1a97b0e`)

- `cmp -l pair_route_84.wav pair_route_00.wav` → sole diff at 1-based byte 257 (offset 256): `204 0` octal = `0x84`/`0x00`.
- `sha256sum` → `cf5edecce1812f0a…` / `cb77db319a7a791f…` — byte-identical to author's cited SHAs.
- `sox -V6 pair_route_84.wav -n stat` → `detected file format type 'act'`, `(ffmpeg)` tag, `Samples read: 3839`, exit 0 — **the r62 packet-residue path reproduced on the tracked pair**.
- `sox -V6 pair_route_00.wav -n stat` → `detected file format type 'wav'`, FAIL `number of valid bits exceeds the number of bits per sample`, real exit **2** (checked `$?` directly, not via pipe).
- `measure_audio.py --probe-ui-route-act-84-r63` → exit 1 (receipt written); `--probe-ui-route-act-00-r63` → exit 1 (receipt written). Both expected-validation shape.

## Seat-evidence audit

| seat | landed | key evidence |
|---|---|---|
| author | `r63-author.md` + tracked +57/−5 | exhaustive sweeps; ledger 84→86 (43/43); prior-84 receipts byte-identical |
| critic | `r63-critic.md` | falsified range/multi-byte/content hypotheses; produced native-wav WITH 0x84@256 (RIFX/RF64); preemptor set |
| reviewer | `r63-reviewer.md` | r62 audit AGREE-all: 84/84 exits, 84/84 receipts byte-identical, both discernment directions re-executed |
| baseline | `r63-baseline.md` | frozen `3c96a69` 84-cmd replay: 43/39 exits match, 83/84 byte-identical (one absolute-path string) |
| boundary | `r63-boundary.md` | no-fallback proof; two more collision offsets; fd-leak + exit-status disclosures |
| scout | `r63-scout.md` | binary disasm pin: `cmp BYTE …,0x84` at data+0x100; routing signatures |
| scribe | `r63-scribe.md` | knowledge-entry draft (landed `corpus/knowledge/2026-10-13-sox-act-autodetect-predicate.md`); own 293-row sweep |
| simplifier | `r63-simplifier.md` | minimal-diff verdict: pair is the smallest receipt-bearing discriminating set; two nits (none blocking) |
| verifier | `r63-verifier.md` | **AGREE all claims**: 86/86 exits + 86/86 receipts byte-identical; pair SHA/cmp verified; both discernment directions on committed tree |

## Disclosures recorded (none gate-affecting)

- Verifier caveat: the `00` receipt embeds the absolute canonical path in `sox_stderr` — byte-identity is a same-host property (same class r62-baseline flagged on `--probe-invalid`).
- Simplifier nits: TSV `route=native` mislabels act-detected/ffmpeg-failed cells; builder comment "256 values x 11,588 positions" reads as cross-product (actual: separable 1-D sweeps — sufficient for a conjunctive predicate). Non-blocking.
- Boundary: ffmpeg child exit status never reaped; one fd leaked per act-routed open — evidence-quality disclosures, claimed nowhere as gate behavior.
- Integration: regenerable frozen baseline `tree/` and the extracted upstream `src/` pruned; no source tarball is committed — source citations re-verify against the upstream `sox_ng-14.8.0.1` tag (r64-reviewer re-fetched it independently and confirmed the cited lines).

## Per-axis verdicts

- **depth: improved locally** — r62's declared fragility is now an exact, source-cited, exhaustively-measured predicate; the no-fallback ordering UNKNOWN closed.
- **coverage: improved locally** — the routing dimension gets a tracked pair + two opt-in modes; ledger 84→86, all prior preserved verbatim.
- **calibration: improved locally** — the gate's behavior on native-rejected valid-bits headers (route-00 → exit 2 receiptless vs bridge-decoded exit 1 receipt) is now pinned discriminating.

Verdict: **ADMIT** — no demonstrated scoped harm; four SHONEN boxes remain checked without promotion.

## Bounds retained

Same-host SoX_ng 14.8.0.1 + ffmpeg n9.0.1 only; non-USING_FFMPEG builds lack the act row entirely; stdin/pipe detection unexercised; exotic pre-act CHECK collisions beyond gsrt/hcom unexercised. No standards-conformance, decoder-correctness, fidelity, audibility, production, rights, or promotion inference.
