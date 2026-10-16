# R93 verifier — the `ebur-r93` family executed once on the frozen PIN

**Seat: VERIFIER (leaf), round 93.** Host `plazir27`. Window 2026-10-16
09:37–09:55 UTC−3 (12:37–12:55 UTC). Source pin
**`bb177513a615a32d3bc150ecbdcf78302e110d8c`** ("r99 safety: require explicit
opt-in before physical LAN control", 2026-10-16 09:29:41 −03). Flag
`ebur-r93`. Scratch `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-verifier/`.
This report is advisory; it is not a gate-admission or shipping decision.

LSP status: **no LSP server is available to this seat's toolset** (no `lsp`
device in this substrate). Recorded as a gap; all source statements below come
from literal pinned-source inspection (`git show PIN:path`, text only). Grep
output here is text evidence, never semantic proof.

## 1. Commands actually executed (verbatim, in order)

1. `timeout 15 pactl info` → **rc 0** (r93 prerequisite). Server
   `PulseAudio (on PipeWire 1.6.8)`, protocol 35, local, default sink
   `…HiFi__SPDIF__sink`, source `…HiFi__Line__source`.
2. Scratch parent verified before mkdir: `audio-waveb-resume/` existed and
   contained only `r99-verifier/` — `r93-verifier/` was unused (unique, never
   reused).
3. Export (recipe verbatim, rc 0, 6.0 MB):
   ```
   mkdir -p "$SCRATCH/tree"
   git -C /home/vgpnk/Projects/shokunin/audio-shokunin archive \
     bb177513a615a32d3bc150ecbdcf78302e110d8c corpus/fixtures corpus/artifacts | \
     tar -x -C "$SCRATCH/tree"
   ```
   Export byte-identity proven: sha256 of the exported
   `corpus/fixtures/measure_audio.py` = `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`
   = sha256 of `git show PIN:corpus/fixtures/measure_audio.py`. The minimal
   export intentionally omitted `corpus/live/` — nothing was borrowed.
4. The family, once, exactly as assigned (cwd = the export tree root):
   ```
   env -u RTP_R99_ALLOW_LAN_CONTROL UFO_SEAT=r93-verifier-resume \
     PYTHONDONTWRITEBYTECODE=1 timeout 1500 \
     python3 corpus/fixtures/measure_audio.py --probe-ebur-r93
   ```
   **rc 0**, stderr empty (0 bytes), stdout 165 bytes ending
   `{"receipt": ".../20261016T125015677298Z-ebur-r93/measurements.json", "failures": {}}`.
   Wall time ≈ 12 min (12:38:17 → 12:50:15 UTC). `RTP_R99_ALLOW_LAN_CONTROL`
   was only ever unset, never set.
5. Read-only receipt audits (python3 JSON reads; no new grader, no scoring,
   no numeric checker — structural counting and quoting only).

## 2. Findings, by severity

No high or medium finding. The run is green and reproduces the author's
pinned lattice. Three low/informational findings:

### F1 (low, operability — observed) the fixture leaks one tap dir per entry

`corpus/fixtures/measure_audio.py` (PIN) `_ebur_r93_ctx()` line 49568 creates
`tempfile.mkdtemp(prefix="r93a-tap-")` per entry; `_ebur_r93_teardown()`
(lines 49651–49703) never removes it — the only `unlink`s in the r93 section
are per-file (line 49259 tap-WAV reuse, line 51075 private-core socket locks).
Observed: exactly 9 `/tmp/r93a-tap-*` dirs left by this run (mtimes
09:38:17–09:48:41 local) and 9 preexisting ones from the operator's final-byte
run (09:07:03–09:17:26 local = the 12:07–12:17 UTC window). Failure path: none
today — unbounded accumulation only if runs repeat on one host. Smallest
correction: `shutil.rmtree(ctx["tapdir"], ignore_errors=True)` at teardown
end. Observed on both runs.

### F2 (info, environment — observed, not caused by this seat) a sibling wrote to the real repo's `measure_audio.py` during this run

The real repo worktree shows ` M corpus/fixtures/measure_audio.py` with mtime
**09:47:30 local — inside this run's window**. The diff content is r97-family
code (`WPPOL_R97_CHILDREN`, `_wppol_r97_spawn/_wppol_r97_own` rework), not
r93. This seat cannot have written it: the run's `ROOT` is
`Path(__file__).resolve().parents[1]` (line 27) = the export tree; every
fixture write (stimuli `ROOT/live/round-93`, lock `ROOT/live/measure_audio-ebur-r93.lock`,
receipt `ROOT/live/runs/<stamp>`) lands under the scratch. Recorded as
concurrent sibling contact; not repaired, not judged.

### F3 (info, calibration lineage — verified by text diff) the PIN's r99-safety commit does not touch the r93 family

The author's green batteries ran impl sha256 `62e2606e…` (worktree) and the
integration's final-byte run ran source `5c8f7e9d…`; this PIN is one commit
later. `git diff 193acbed..bb177513 -- corpus/fixtures/measure_audio.py` has a
single hunk at `@@ -52605,34 +52605,42 @@ def rtp_e2e_r99_entry():` and **zero**
`ebur` mentions; the commit also adds `test_rtp_r99_lan_control.py`. So the
r93 family bytes are identical across `5c8f7e9d…` → `bb177513…`, and this
run's greens measure the same r93 code the integration ran. Text-level
verification (no LSP).

## 3. What the run measured (receipt `20261016T125015677298Z-ebur-r93`)

Structural result — matches the integration note exactly:

- **Nine family entries** (`ebur_topology/cal/channel/modes/peaks/window/history/gain/error_r93_probe`),
  **90 leg keys** total (17+9+10+11+6+6+8+9+14). The 17 base corpus entries
  (ui/impact/movement/ambience/stem, measured against the export's
  `corpus/artifacts/`) ran with zero failures, as the fixed entrypoint always
  does.
- **`failures: {}` in every entry; run rc 0.**
- **Coverage blocks reproduce the disclosed two, no more:**
  `notify_bogus: filter-chain module refused (cls=pwcli_module_load_fail)` —
  the load was refused again (the *silent* variant was again not observed,
  author risk §7.5 stands); and `g_default: audio-domain ratio unmeasured
  (pre=0.20658457 post=0.0)` **twice** — one per rep, the duplicated-message
  shape the integration note explicitly describes ("not two new measured
  arms"). Source: the block is emitted at lines 50520–50526 when the post tap
  carries no mid-tone window.
- **Teardown censuses clean in all nine entries**: `sinks_gone` all true,
  `own_nodes_after: []`, `own_procs_after: []`, every unload rc 0. Independent
  post-run sweep: 0 `r93a` modules, 0 `r93a` nodes in `pw-dump`, no `pw-*`
  processes.
- **All 90 legs**: `play.exit_code == 0`, feed link `ok: true` on first try,
  zero unexpected arm failures. The only 7 `arm_failed` legs are the seven
  expected-refusal arms (`notify_bogus`, `g_unquoted`, `e_labelfail_{null,avg,sum,gain,nop}`),
  each retried 3× per the load-retry law and recorded with the exact expected
  classes (`pwcli_module_load_fail`, `ebur_r93_ctl_grammar`,
  `ebur_r93_label_parse`, `ebur_r93_plugin_refused` ×4). The boundary's
  silent-arm hazard (§0.2: `pw-play` rc 1, empty stderr) did not occur.
- **Generated stimuli regenerated, not borrowed**: the export had no
  `corpus/live/`; the run wrote 14 WAVs into `tree/corpus/live/round-93/`,
  and all 14 sha256s equal the author's recorded prefixes (§3.1 of
  r93-author.md) — e.g. `tone_1k_050 b377abe8db044e44`,
  `st_mix 7a11577c41f616bd`. The analytic builders are deterministic.
- **Calibration constants reproduce exactly** (measured plateau vs the
  fixture's own BS.1770 reference over the fed bytes, law |Δ| ≤ 1e-3 dB):
  1k/1.0 `-3.003596` (Δ0), 1k/0.5 `-9.024196` ×2 (Δ1e-6), 0.25 `-15.044795`
  (Δ0), 40 Hz `-15.288830` (Δ6e-6), 100 Hz `-10.855398` (Δ1e-6),
  4 kHz `-5.753903` (Δ0), 10 kHz `-5.680018` ×2 (Δ0).
- **The falsified-constant laws hold on fresh bytes**: all 7 input ports read
  `-9.024196` (dead channel map, C4); mix `-19.024195` (dB mean, C5); silent
  channel → 150/150 `-inf` with Global `-9.091105` finite (C6); Window-only
  151/152 NaN with audio flowing (C8); Peak/True Peak `0.5/0.0/0.2` (C9);
  window absent → NaN, 0.4 → decay 0.427 s ×2, 2.0 → 1.856 s ×2 (C10, the
  author's own values); history: silence never evicts (`-9.522255` both
  configs), two-burst default `-11.503388` vs cap2 `-15.539840` (C11);
  gain: same-leg residual **0.0 dB** (target 0, gains 2.896856/2.897281 —
  leg-dependent constants, exact law), clamp residual −0.000629 dB at gain
  0.000916, silence gain exactly 1.0, default gain 0.205082 (C12); unquoted
  spaced key refused with the expected class (C13); label matrix
  debug/busy/sqrt/ramp/zeroramp load, null/avg/sum/gain/nop refuse (C14);
  unknown key warning-only `-9.024196`, non-numeric `max-history` loads and
  never meters (C15); Shortterm telemetry `-9.724301` in the modes entry
  (matches author §7.6).
- Host was quiet during the run (entry loadavg 0.21–0.69); `foreign_r93a_nodes`
  empty at every entry head.

## 4. Blocked vs measured, residual risks, checks not run

- **Measured here**: the single green battery on PIN `bb177513…` — 90 legs,
  constants, refusal classes, teardown censuses, stimuli determinism.
- **Blocked (disclosed, unchanged)**: the `g_default` audio-domain ratio is
  unmeasured (post tap silent in this graph shape; C12 stands on the same-leg
  residual only) and `notify_bogus`'s silent-load variant was not re-observed.
- **Not run (out of this seat's recipe)**: no repetition, no load/quantum/rate
  arms — the boundary's load-regime and axis claims are not re-measured; no
  independent re-derivation of Global references (the fixture's own reference
  is quoted from the receipt, not recomputed — no new numerical pipeline);
  no r99/r98/r100 family was touched; `RTP_R99_ALLOW_LAN_CONTROL` never set.
- **Residual risks**: (a) one run only — the byte-stability claims lean on the
  author's two batteries plus this one, three runs total; (b) a ready daemon
  gate leaves no receipt trace (the gate object is stored only when it
  blocks, lines 55190–55210) — a green run cannot show the gate ran; (c) the
  tap-dir leak (F1) accumulates per run; (d) the sibling's concurrent write to
  the real repo worktree (F2) means the real repo's worktree bytes are in
  flux — this report's source statements are pinned via `git show PIN`, not
  the worktree.
- **LSP**: unavailable in this seat's toolset; recorded as a gap. All
  source citations are literal pinned-text reads.

## 5. Artifacts and attribution

- Receipt (this run):
  `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r93-verifier/tree/corpus/live/runs/20261016T125015677298Z-ebur-r93/measurements.json`
  (local scratch; **not committed, not remotely available**).
- Scratch: `command.txt` (literal command), `stdout.txt` (165 bytes, the
  receipt line), `stderr.txt` (0 bytes), `rc.txt` (`rc=0`), `tree/` (the
  6.0 MB export + regenerated stimuli + receipt).
- Read as frozen input evidence (not re-derived):
  `reports/round-93/r93-scout.md`, `r93-boundary.md`, `r93-author.md`,
  `reports/round-100/r93-r99-r100-integration.md`; the author's green
  receipts `corpus/live/runs/20261016T101716935215Z-ebur-r93/` and
  `…T103145603182Z-…` and the integration receipt
  `…T121901064467Z-ebur-r93/` remain in the real repo, untouched.
- Attribution: verifier leaf seat (glmseat model pin), round 93 of the
  shokunin-train-20261016-w24 wave. Advisory only; the lead owns judgment.
