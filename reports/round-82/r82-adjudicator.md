# r82 adjudication — ffmpeg transport lattice

**Verdict: ADMIT-corr** — authored `aa03c347`-era work, folded `d6167399` (+198/−77), verified on folded bytes.

## Dossier

| seat | verdict | commit |
|---|---|---|
| author | 8 entries / 76 legs, 304 leg-executions green ×4 | earlier |
| baseline | green, `normal` sha byte-identical | `2333fac` |
| boundary | 6 claims falsified/corrected, folded pre-authoring | `9725e53` |
| critic | ADMIT-with-findings — F1–F13, latent classes proven live | `51a98e54` |
| reviewer | PASS-with-findings — F1 tone-band collision, F2 rc-8 class | `88f08fc9` |
| simplifier | PASS — 10 items net −25 (folded) | `b24a9457` |
| verifier | VERIFIED — 76/76 ×2 @load114, 8/8 re-derivations | `97bd351a` |
| scribe | custody INTACT — hash chains re-derive | `b307713e` |
| fold | 8-item queue applied: tones re-keyed pid-class, rc-8 armed, a2 retarget+gate, t2 zeros gate, exact-name unload, flock | `d6167399` |
| verifier-r2 | VERIFIED — 77 legs ×3, all fold items live, foreign-name unload negative control | `cab9f08e` |

## Folds applied and verified

- Simplifier −25 net lines (10 proven items).
- Reviewer F1: r82 tone pairs re-keyed `2900+400k` pid-class + band-clear guard (r78 collision removed — two pid classes exercised live).
- Reviewer F2: `-channels 0` rc=8 `ff_option_not_found` class armed.
- Critic F1: `a2_hw_free` retargeted to Speaker subdevice + `holder_consumers` gate.
- Critic F2: `t2_cap` post-unlink `mine_spans` content gate (sustained-zeros hole closed).
- Critic F3: pid-keyed tag + same-family flock to exit.
- Critic F4: `_gst_r81_sink_module_index` → exact-name equality (foreign `r82w_ctl_a2` survived live negative control).

## Bounds

PipeWire 1.6.8 / ffmpeg n9.0.1 / ALSA 1.2.16 / WirePlumber 0.5.17, host under load 55–153. One environmental red flake observed (`/tmp` tmpfs quota, rc=134 — correctly rejected by the new content gate). Blocking-flock stall is an intentional honest signal.
