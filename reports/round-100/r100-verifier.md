# r100 verifier — the sofa/spatializer family run once on the pinned export

**Seat:** verifier (leaf; no subagents; the only live-family runner for r100 in
this wave). **UFO_SEAT:** `r100-verifier-resume`. **Model pin:** `glmseat`
(`glm-5-3-flash-max`) invoked as first action; Godspeed loaded once.
**Source pin:** `bb177513a615a32d3bc150ecbdcf78302e110d8c` (commit
"r99 safety: require explicit opt-in before physical LAN control",
2026-10-16 12:29:41Z). **Flag:** `sofa-r100`. **Scope:** execute exactly the
fixed verifier recipe on a minimal frozen tracked-source export; write this
report and the scratch only; advisory, no gate-admission or shipping claim.

**LSP gap (recorded, per assignment):** no LSP server/device is available in
this session. All source statements below are literal text inspection of the
exported pinned bytes; no grep output is presented as semantic proof.

---

## 1. Commands actually executed

Scratch parent verified before mkdir: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/`
existed containing only `r99-verifier` — `r100-verifier` was unused. Export
(`git archive PIN corpus/fixtures corpus/artifacts | tar -x -C tree`): rc 0,
6.0 MB, no errors. `RTP_R99_ALLOW_LAN_CONTROL` was **unset in the ambient
environment before the run** (checked: `UNSET`) and was additionally removed by
`env -u` inside the mandated command; the opt-in was never set at any point.

Literal command (saved verbatim in scratch `COMMAND.txt`), executed with cwd
`…/r100-verifier/tree`:

```
env -u RTP_R99_ALLOW_LAN_CONTROL UFO_SEAT=r100-verifier-resume PYTHONDONTWRITEBYTECODE=1 timeout 1500 python3 corpus/fixtures/measure_audio.py --probe-sofa-r100
```

- Start ≈ 2026-10-16T12:38:04Z, completion 2026-10-16T12:44:42Z (wall ≈ 398 s;
  no wall-time claim armed — host was contended, §3 F2).
- **rc 0**; stderr **empty** (0 bytes); stdout 167 bytes:
  `{"receipt": "…/tree/corpus/live/runs/20261016T124442058903Z-sofa-r100/measurements.json", "failures": {}}`.
- Receipt sha256 `42f284789dc1ef0217b0ad4848454a72c563ff2f4c278273d105da02b33a2b25`
  (891 226 bytes). Cited for the lead to inspect; rc 0 is **not** claimed as
  complete coverage and no new numeric checker was composed.

Post-run census (observed): zero `r100a_*`/`r100sofa` processes, zero
`/tmp/r100a-sbx-*` sandbox dirs, zero own measure_audio processes; the shared
daemons (`/usr/bin/pipewire` pid 3549292, `pipewire-pulse` 3549294) were
running before, during and after, untouched — no service was restarted.

## 2. Receipt structure (raw facts, quoted not graded)

`measurements` carries 26 keys: the 17 standing canonical-corpus analysis
blocks (`ui`, `impact`, … `stem_layer_third`, each `legs=0` — the fixture's
normal battery analysis, not probe legs) plus the **9 sofa entries**:

| entry | legs | failures | coverage_blocked | own_nodes_after | own_procs_after | stream_rows |
| --- | --- | --- | --- | --- | --- | --- |
| sofa_shape_r100_probe | 2 | [] | none | [] | [] | [] |
| sofa_azimuth_r100_probe | 7 | [] | none | [] | [] | [] |
| sofa_curve_r100_probe | 4 | [] | none | [] | [] | [] |
| sofa_rate_r100_probe | 5 | [] | none | [] | [] | [] |
| sofa_control_r100_probe | 3 | [] | none | [] | [] | [] |
| sofa_transfer_r100_probe | 7 | [] | none | [] | [] | [] |
| sofa_inert_r100_probe | 4 | [] | none | [] | [] | [] |
| sofa_clock_r100_probe | 3 | [] | none | [] | [] | [] |
| sofa_shared_r100_probe | 2 | [] | none | [] | [] | **2 rows** (F3) |

Total **37 legs** — matches the declared 9 entries / 37 leg keys. All 37 legs
record `post_sweep clean=True`. Every entry carries the `law_provenance`
split (boundary-published / this-seat-measured / extrapolated) exactly as the
author report §3.1 declares, including the openly carried `XFER.az0_db`
2e-4 ambiguity and the `N_SAMPLES[88200]=1024` extrapolation.

Raw stored values quoted from the receipt (the lead checks quantitative
outputs; this seat claims no aggregate): FINE ILD az0 `0.0`, az90 `4.6084`,
az270 `-4.6084`, az180 `0.0`; `n_samples` `512/558/1024/1115` at
`44100/48000/88200/96000`; shared-graph az90 FINE `4.6084` (daemon answered:
`pw-dump` rc 0, 88 objects); clock ladder q512 `4.626`, q2048 `4.6084`,
r96000 `4.6176`; channel swap `-4.6084`; `s_unfed` frames 117 760 with ILD
`0.0` (the silence-until-fed cell is present and gated on frames > 0, not
rms == 0).

## 3. Findings (severity order)

**F1 — MEDIUM (provenance, observed, resolved): the verification pin is not
the author's green bytes, and the lead should record that.**
`corpus/fixtures/measure_audio.py` at the PIN hashes
`801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`, while the
author report §5 declares `e965f56c…` for both green runs and the integration
note declares `5c8f7e9d…` as the r100 final source. Byte comparison against
the frozen integration candidate
(`/home/vgpnk/Projects/shokunin/audio-resume-integrations/stage-r100.py`,
sha256 exactly `5c8f7e9d…`) shows the PIN differs in **exactly one hunk**
(`52608,52635c52608,52643`), inside `rtp_e2e_r99_entry()` — the r99
physical-LAN opt-in safety repair that commit `bb177513` itself carries
(12:29Z, after the author's 10:38Z greens). The entire r100 sofa family
region (`SOFA_R100_SRC` at `measure_audio.py:52851`, lock path `:52975`,
argparse `:54389`, entry wiring `:55260-55293`) is **byte-identical** through
author → integration → PIN, and `corpus/fixtures/r100sofa.py` is
byte-identical to the author's declared `26e96660…`. Smallest correction:
none to source; the lead should note in the round ledger that the r100
verification bytes = integration candidate + the r99 safety hunk, a disjoint
region. (Observed by byte diff, not inferred.)

**F2 — LOW (observed condition, no defect): the shared-graph cross-witness
ran under sibling contention.** `sofa_shared_r100_probe` records
`foreign_pw_clients` including a live sibling verifier's client
(pid 1441768, `pw-play --target r93a_1427852_in …/r93-verifier/tree/...`)
and every entry records `host_is_quiet: False`. The shared legs still
measured (both legs clean; shared az90 FINE ILD `4.6084`, identical to the
private-core value), consistent with the boundary's clock/load-invariance
extension — but this seat makes no new invariance claim from one contended
run. Smallest correction: none; a contention-free shared witness would need
a second run, which the one-run mandate forbids.

**F3 — LOW (observed, pre-disclosed class): the shared entry wrote exactly 2
rows into the operator's real WirePlumber store.**
`sofa_shared_r100_probe.stream_properties_own_rows` =
`['Audio/Sink:media.name:r100a_1427012_sofa\sinput',
'Output/Audio:media.name:r100a_1427012_sofa\soutput']` — the author's §7.1
disclosed r90/r95 class (recorded, not gated; the 8 private-core entries left
zero). These 2 rows now exist in the operator store from this verification
run. Smallest correction: none in verifier scope (source repairs are out of
scope); the lead may append them to the operator-store residue ledger.

**F4 — INFO (observed, pre-existing): stale bytecode caches are tracked in
the pin tree.** `corpus/fixtures/__pycache__/measure_audio.cpython-314.pyc`
and `build_artifacts.cpython-314.pyc` are committed blobs at the PIN
(`git ls-tree` confirms; mtime 12:29:41Z from the archive). No effect on this
run (`PYTHONDONTWRITEBYTECODE=1` held; source executed directly; no new pyc
written — the exported pycs are the archive's own bytes). Advisory hygiene
note only; out of repair scope.

**F5 — INFO (gap): IR/latency row remains unmeasured.** The scout's proposed
row 8 (single-sample delta through the spatializer, §4 row 8) is not among
the author's 9 entries and the boundary left it unarmed (§7). It is a named
gap in the family, not a defect in this run. The scout's row 9 (runtime
azimuth) IS armed and measured here (`c_runtime`, read-back `0.0 → 90.0`).

## 4. What the evidence supports

- The family ran **once**, on the pinned bytes, under the mandated
  environment: rc 0, empty stderr, receipt written, `failures: {}` on stdout.
- Structure matches the declared contract: 9 entries, 37 legs, no entry
  failures, **no coverage blocks** (the shared daemon answered, so the
  family's named-block branch never fired).
- Teardown discipline held: 37/37 legs `post_sweep clean=True`; all 9
  entries' `own_nodes_after`/`own_procs_after` empty; store rows `[]` on all
  private-core entries.
- The measured receipt values reproduce the author's two green runs and the
  boundary's corrected fine-recipe values at the printed precision (quoted
  in §2; grading belongs to the lead).
- **Blocked vs measured:** nothing was blocked in this run. Measured: all 37
  legs. Not measured by this family at all: the IR/latency row (F5), any
  perceptual/spatial-audio quality (never claimed by any seat), any
  cross-host behavior, and the r93/r99 families (their verifiers own those).

## 5. Residual risks and checks not run

- **Single run** (mandated): no repetition, no retry, no cross-run stability
  statement from this seat. The author's two greens plus this run are three
  runs on record; I assert no new bound over them.
- Contended host during the run (sibling r93-verifier family live; foreign
  load) — wall time and shared-graph conditions are not
  contention-controlled (F2).
- I did **not** re-derive the author-worktree → integration wiring-splice
  delta (`e965f56c…` → `5c8f7e9d…`); that link is attested by the
  integration note's byte-review, not independently recomputed here. The
  integration → PIN link **was** byte-verified (F1).
- I did not audit the r99 LAN-control behavior itself (r99's verifier owns
  it); I only attest the opt-in env was never set for this run.
- The receipt's 17 canonical-corpus blocks (`legs=0`) were not checked —
  outside r100 scope.
- The receipt lives in the **local scratch tree**
  (`…/audio-waveb-resume/r100-verifier/tree/corpus/live/runs/…`), which is
  untracked local evidence; nothing was committed or pushed by this seat and
  no claim is made that it is committed or remotely available.

## 6. Artifacts and attribution

- Report: `reports/round-100/r100-verifier.md` (this file; advisory only).
- Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r100-verifier/`
  — `COMMAND.txt` (literal command + start stamp), `probe.stdout` (167 B),
  `probe.stderr` (0 B), `probe.rc` (`0` + completion stamp), `tree/` (the
  6.0 MB frozen export incl. the receipt).
- Receipt:
  `…/r100-verifier/tree/corpus/live/runs/20261016T124442058903Z-sofa-r100/measurements.json`
  (sha256 `42f28478…a2b25`).
- Evidence provenance: pinned export via `git archive` of
  `bb177513a615a32d3bc150ecbdcf78302e110d8c`; integration candidate read
  read-only from `/home/vgpnk/Projects/shokunin/audio-resume-integrations/`;
  prior reports read from `reports/round-100/`. All local, nothing uploaded.
- Attribution: verifier seat, leaf, no descendants; family executed is the
  author's existing `--probe-sofa-r100` family unmodified; no grader, law
  set, threshold, or scoring policy was created; evidence and services left
  intact.
