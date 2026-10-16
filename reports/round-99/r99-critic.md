# r99 critic — attack record for the pinned native-RTP family

Seat: **CRITIC** (leaf, wave B, `shokunin-train-20261016-w24`). Round **N=99**,
role `critic`, FLAG `rtp-r99`. Source pin
**`bb177513a615a32d3bc150ecbdcf78302e110d8c`** ("r99 safety: require explicit
opt-in before physical LAN control", 2026-10-16 09:29:41 −0300). Advisory
only: this report admits nothing, gates nothing and is not a canonical judge
verdict. No source edits, no fixture or family execution, no network
operation, no subagents; the only files written are this report and
`audio-waveb-resume/r99-critic/`.

Pinned blobs verified by hash: `corpus/fixtures/measure_audio.py`
`801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`;
`corpus/fixtures/r99rtp.py`
`36b6b6f8ae332d768e6129fc1fbcf56e634c2e636ceaaa043f97ad11cccfa6a1` (identical
to the author's claimed implementation sha and to the integration's
companion-input hash — the instrument is byte-identical across author,
integration and pin); `corpus/fixtures/test_rtp_r99_lan_control.py` (49
lines, new in this commit).

**Worktree context (recorded, not reviewed):** main-worktree HEAD is
`90a7a9c6`, one commit past the pin; that successor adds the LOG entry and
`reports/round-99/r99-network-safety.md` plus the raw proof dir
`/home/vgpnk/Projects/shokunin/r99-network-safety-proof/`. The review target
below is the pin; the successor's record is cited as post-pin context where
it closes a question.

**Method:** LSP is unavailable to this seat; every source statement below is
literal inspection of the pinned bytes (`git show PIN:path`, sed/grep line
reads) — textual evidence, not semantic proof. Receipts were parsed
read-only with python3/json; no measurement was re-derived. All receipts
cited are local ignored-path evidence, not committed and not remotely
available.

Commands actually executed: glmseat skill read; assignment/plan reads;
`git cat-file/log/ls-tree/show` (pin identity, inventory, the safety diff,
pinned source regions, pinned-blob sha256sums); python3 JSON reads and
field-level figure checks over four r99 receipts (author ×2 in the nested
`audio-shokunin-wt-r99` worktree, integration `20261016T121018453359Z`,
default-safe `20261016T122858496567Z`); sha256 comparison of the author run
receipts against `r99-author/manifest.sha256`; ls/find/cat over
`corpus/live/`, `audio-resume-integrations/`, `r99-network-safety-proof/`,
and the verifier sibling's scratch; LOG.md and worktree-state reads. Full
log: `audio-waveb-resume/r99-critic/commands-evidence.md`.

---

## Findings, by severity

### C1 (high, fixable) — e_lan's branch order downgrades a decidable catastrophic LAN leak to a coverage block

- **Where:** `corpus/fixtures/measure_audio.py:52555-52597`. Emission witness
  `:52537-52539` (`emitted > 1000`); `if excess <= 0` → `armed_below_band`
  (`:52555-52562`); **`elif band > 0.25 * max(1, lan["emitted"])` →
  `coverage_block` (`:52568-52574`) precedes** the only failure branch
  (`else`: `allowance = 0.2 * emitted`, assert `excess <= allowance`,
  `:52589-52597`).
- **Failure path:** `excess = arm − max(idle1, idle2)`. Whenever the
  bracketing idle band exceeds 25 % of the emitted volume, *every* positive
  excess — including a leak of the entire emitted stream — falls into the
  coverage-block branch ("idle band … too wide to resolve the confinement …
  confinement unmeasured this pass") and the failure assertion is
  unreachable. A measured, decidable leak is filed as "unmeasured".
- **Counterexample (arithmetic on pinned code + receipt regimes; no live
  run):** in the verifier's pass (receipt
  `audio-waveb-resume/r99-verifier/tree/corpus/live/runs/
  20261016T124136092601Z-rtp-r99/measurements.json`) band = 8990 tx packets
  vs 0.25 × 19999 = 5000 → `band_over_emitted` 0.4495. A sink that leaked
  all 19999 emitted packets onto `enp7s0` (arm ≈ 27479, excess ≈ 18489 >
  allowance 4000) would be recorded `verdict: "coverage_block"` with a
  `coverage_blocked` line saying "confinement unmeasured this pass" — no
  failure anywhere in the entry. The author's own comment (`:52578-52588`)
  claims "A real leak of the 20 000 emitted packets would blow straight
  through that bound" — the branch order does not implement that claim.
- **Regime prevalence (observed in receipts):** author run 1
  (`audio-shokunin-wt-r99/corpus/live/runs/20261016T103556786349Z-rtp-r99/`)
  band 5675 > 5000 (`band_over_emitted` 0.2837) — red unreachable there too.
  Author run 2 (2208), integration (2137) and default-safe (2802) passes had
  narrow bands where the red branch is reachable. So the pin's only
  independent live run (the verifier's) executed in the regime where the
  failure path cannot fire.
- **Classification:** branch order source-read (observed); the
  leak-downgrade consequence is inferred by code-path arithmetic, corroborated
  by two receipt regimes. The leak itself was never executed.
- **Smallest correction:** evaluate leak magnitude *before* the band-width
  block: if `excess > allowance` (the code's own 0.2 × emitted bound — no new
  threshold concept), append a **failure** ("the arm window added ~N packets
  beyond the idle band — a leak of the emitted volume is decidable even under
  this band") while still recording the `resolution` dict; keep the
  coverage block only for `0 < excess <= allowance` under a wide band. One
  branch reorder; no new grader, law set or sampling policy. Honest cost: a
  foreign burst confined to the arm window could now false-red — that is the
  fail-loud direction, and the receipt's lo-tap count and socket shape let
  the lead distinguish a leak from a foreign burst.
- **Distinct from the declared loss:** the author/boundary honestly declared
  the counter cannot resolve *small* leaks under load; this defect is that
  *large* leaks are also not filed as failures when the band is wide.

### C2 (medium, fixable) — silent-unmeasured legs: precondition failures skip every verdict without a named block

- **Where:** e_lan `:52513` (`if cli is not None:`) and `:52518`
  (`if lan["node"].get("reached"):`) — every e_lan assertion
  (`:52537-52597`) lives inside both guards; e_lan_control `:52618` (same
  shape); and the shared sink-leg helper `:51685-51687`
  (`if leg["recv"] is None: leg["error"] = "tap produced no receipt";
  return leg`) used by all `s_*`, `r_s24be` and `a_*` legs.
- **Failure path:** a mid-entry `pw-cli` spawn failure, a sink that never
  reaches `running`, or a tap that produces no receipt leaves the leg dict
  partial with **no failure and no `coverage_blocked` entry**; the
  entry-level signals stay clean (`failures: []`,
  `coverage_blocked: [e_native, e_lan_control]`). This contradicts the
  family's own declared convention ("a missing tool / fixture / private core
  is a named coverage block … an entry that cannot measure names why",
  `r99-author.md` §Conventions) at leg granularity.
- **Evidence:** code path observed statically; **latent** — no preserved
  receipt triggers it (all four show `reached: true` and live clis), and
  `_rtp_r99_ready` exercises pw-cli earlier in the same entry, so
  likelihood is low. It is nonetheless exactly the class this seat exists to
  attack: a confinement leg with no verdict and no name.
- **Smallest correction:** in each guard's else, append a named coverage
  block and set the leg's `measured: false` / `blocked`, mirroring the
  control's blocked-branch shape at `:52637-52643` (e.g. "e_lan: pw-cli could
  not open — confinement unmeasured this pass"). Concordant with the
  verifier's F1 (the lock's silent `None`) — same "silent None" family at
  leg level.

### C3 (medium, calibration, fixable) — r99-author.md's quantitative e_lan / e_lan_control figures do not match the preserved green receipts it cites

- **Where:** `reports/round-99/r99-author.md` §5: e_lan "run 1: −232; run 2:
  −1322"; e_lan_control "adds 8626 (run 1) / 6975 (run 2) packets …
  144 % / 116 %".
- **Evidence (observed, field-level):** the cited receipts say run 1
  (`20261016T103556786349Z`) `excess_over_band` **−1339**,
  `arm_tx_packets` **7205** (`fraction_of_emission` 1.201); run 2
  (`20261016T104041659031Z`) **−338** and **6376** (1.063). Field-level
  checks (`"arm_tx_packets": 8626`, `"excess_over_band": -232`, …) are
  **False in both receipts**; the receipts are internally consistent (run 1
  counters re-derive exactly: 24885850 − 24881514 = 4336 = `deltas.arm`).
  The report's figures are self-consistent (8626/6000 = 144 %) but foreign
  to the preserved runs — most plausibly the deleted dev iterations,
  presented under the green passes' names.
- **No verdict flips:** both number sets satisfy the armed forms (arm ≤
  band; control ≥ 0.5 × 6000). But the verifier's residual #3 inherits the
  report's figures ("8626/6975") as the calibration record; the numbers of
  record are the receipts'.
- **Smallest correction:** re-cite the receipt values in r99-author.md (or
  relabel the figures as dev-iteration values); the lead's calibration
  should read 7205 / 6376 / 6034 from the receipts.

### C4 (medium-low, calibration, fixable) — the physical-LAN control's execution count is understated in the planning layer

- **Facts (receipt-backed):** the LAN positive control executed in **three
  preserved passes**: author run 1 (7205 tx), run 2 (6376), integration
  `20261016T121018453359Z` (6034) — plus an unknown number of deleted dev
  iterations. `wwkd-plan.md` ("This ran once and was disclosed") understates
  this, and the integration note's r99 paragraph records only `e_native` as
  blocked without mentioning that its own pass executed the control.
- **The disclosure chain itself is sound:** the author report §5, the code's
  disclosure string (`:52613-52616`), the LOG ROUND 99 SAFETY entry, and the
  post-pin `r99-network-safety.md` (which explicitly records the
  integration run's 6034-packet egress on `enp7s0`). The defect is the
  count, not the disclosure.
- **Smallest correction:** one sentence in the integration note ("this pass
  executed the disclosed LAN control: 6034 tx packets") and a plan errata
  ("ran on ≥ 3 recorded passes"). No code change.

### C5 (low, fixable) — e_native's block message asserts an unconditioned fact

- **Where:** `:52394-52411`. The block branch fires whenever the source's
  recorded peak ≤ 0.3 — including paths where the sink never reached
  `running` or the tap produced no receipt (`sink_emitted` false). The
  message still asserts "the sink emitted (see
  legs.e_native.verdict.sink_emitted and the wire peak)", contradicting the
  very field it cites in that case.
- **Latent:** all four preserved receipts have `sink_emitted: true`, so the
  message was true everywhere it actually fired.
- **Smallest correction:** interpolate the verdict values into the message
  (`sink_emitted=<…>, wire peak=<…>`) or condition the sentence on the
  verdict.

### C6 (low, fixable) — e_sap files an environment failure as two law failures

- **Where:** `:52444-52448`. Unlike e_native/e_relink (which
  `_rtp_r99_block` on bring-up failure, `:52302/:52464-52467`), e_sap's two
  assertions run unconditionally after `sok2 = _rtp_r99_core_up(inst,
  with_wp=False)`: a dead private core yields `sap.get("own_nodes") = None`
  → red "rtp-sap creates no node = None, want []" plus a red join-line
  assertion over an empty log. Visible, not silent — a calibration mislabel,
  not a false green.
- **Smallest correction:** guard both assertions on `sok2` and record a
  named coverage block otherwise, mirroring e_relink's bring-up guard.

### C7 (low, fixable) — the family lock returns None silently on os.open failure; the pinned family's independent live run executed unlocked

- **Where:** `:50903-50921` (`except OSError: return None` at
  `:50911-50912`); caller `:55250` discards the `None`.
- **Failure path:** if `corpus/live/` is absent or unwritable, the whole
  six-entry run proceeds with no same-family exclusion, defeating the fixed
  path-lock contract the helper's own docstring cites as load-bearing (the
  r84 F1 consensus).
- **Evidence:** the verifier **observed** exactly this in its frozen export
  (its F1: `corpus/live` absent until receipt time) — so the pin's only
  independent live run executed unlocked. Two seats converge independently
  on this defect. Harm tempered: port windows are pid-derived
  (`:50793`) and node names pid-unique; no second rtp-r99 lane was live.
- **Smallest correction (adopting the verifier's):** `mkdir(parents=True)`
  the lock's parent before `os.open`, or treat an untakeable lock as a named
  coverage block instead of returning `None`.

### C8 (info, fixable) — the control's executed branch never sets `measured: true`

The blocked branch sets `measured: False` (`:52640-52642`); the executed
branch (pre-pin receipts) leaves `measured` absent (None). A reader keying on
`measured` sees None for an executed control. One-line asymmetry fix in the
ran branch.

### C9 (info) — declared losses and honest blocks, verified rather than attacked

- **e_native** is coverage-blocked in all four receipts (author ×2,
  integration, verifier) carrying both sides' measurements (sink wire peak
  exactly 0.499969482; source peak 0.0, `rtp.ssrc "0"`); C6 is neither
  claimed nor falsified — matches the author's declaration and the
  boundary's data. Verified honest.
- **Default-off control:** with the gate closed, a default run's e_lan green
  rests on the counter's resolution calibration inherited from the pre-pin
  control runs (the verifier's residual #3 names this; concurrence). The
  blocked leg names the absence ("requires explicit operator approval …"),
  so the loss is declared, not hidden — the accepted trade, not a defect.
- **Pin live coverage (better than the raw receipts suggest):** the pin's
  default-safe behavior has two live receipts — the lead's
  `r99-safe` run (proof dir binds `source-after.sha256` = `801e153b…` = the
  pinned bytes; `lan-before.rc` 1 → `lan-after.rc` 0; run receipt
  `20261016T122858496567Z`) and the verifier's pinned-export run
  (`20261016T124136092601Z`, rc 0, `failures: {}`). What remains unexercised
  live on the pinned bytes is only the **opt-in branch itself** (by design;
  forbidden without operator approval) — its live behavior is inherited from
  the pre-pin control runs.

---

## What the evidence supports

- **The gate is fail-closed by construction:** exact `"1"` comparison
  (`:52608`); None/""/0/"true" all fall to the blocked branch (asserted by
  the pin's own AST-isolated test, executed before-red/after-green by the
  lead per the proof dir, and confirmed live in both post-repair receipts:
  `measured: false`, the approval message, exactly one entry-level
  `coverage_blocked` entry).
- **Exactly one LAN-egress door:** the only LAN-interface sink arm in the
  pinned family is `ifname=iface` at `:52620-52621`, inside the gate. Every
  other multicast arm pins lo (e_native `:52336-52337`, e_lan
  `:52515-52516`, the e_sap fragment, r_mcast's `"--ifname", "lo"`), and the
  instrument's own sender fail-closes when the interface address cannot
  resolve (`r99rtp.py:326-334`: SO_BINDTODEVICE `:322`, IP_MULTICAST_IF
  `:331`, TTL 1 `:333`, `{"sent": 0, "error": "no IPv4 address…"}` `:330`).
  The fixture cannot leak by default; the module can only through the gated
  control.
- **Count shape:** 37 leg-dictionary keys = 33 non-tone cells + 4 `tone`
  setup records, identical across all four receipts — matching the
  assignment's r99 description exactly (census 3; sink 7+tone; source 6+tone;
  refusal 8; e2e 5+tone; axis 4+tone).
- **Byte provenance:** pinned `r99rtp.py` = the author's implementation sha =
  the integration's companion hash; the pin's `measure_audio.py` delta vs the
  author's `1bb2f98b…` is exactly the guard + test (concur with the
  verifier's diff check; the proof dir's before/after sha files bind it
  further: before = `5c8f7e9d…`, after = `801e153b…`). The restored run-1
  receipt is byte-identical to the preserved copy (`fc120288…` verified
  against `r99-author/manifest.sha256`) — the author's disclosed restore is
  clean.
- **Process ownership and cleanup:** every entry tears down in a `finally`
  (e.g. `:52647-52651`) with socket/pid/shared-store/shared-graph witnesses;
  all four receipts' teardown witnesses are clean (`socket_gone: true`, no
  own daemon pids, no own store rows, no shared `r99a` nodes); the author's
  `exit-census.json` records shared daemons untouched (MainPIDs
  3549292/3549293/3549294) and `pactl_set_default_issued: false`.
- **Inherited environment is scoped:** the private instance overrides
  `PIPEWIRE_RUNTIME_DIR`/`XDG_*` and pins `PIPEWIRE_DEBUG=3` (`:50923-50944`);
  `a_quantum`'s settings manipulation runs under the instance env against
  the private core only (`:52684-52698`, reset included) — no shared-state
  mutation; the shared settings lattice is witnessed equal at entry start
  and end.

## Residual risks and explicit checks not run

1. I did **not** execute the fixture, the family, the LAN-control test, or
   any network operation (role boundary). The lead's proof dir records the
   guard test's before-red/after-green; neither the verifier nor I re-ran it
   — named, not hidden.
2. The opt-in branch (`"1"`) has never been exercised live on the pinned
   bytes (by design). Its live behavior is inherited from pre-pin control
   runs.
3. e_native's receiver-side blocker (the host's LAN address stamped on a
   lo-delivered packet) remains unexplained — the author's named follow-up
   stands; this wave adds fresh witnesses, not a mechanism.
4. The receipt is written once, at the end (`:55967`); an exception outside
   an entry's internal try (e.g. in `_rtp_r99_entry_head`) would lose the
   whole run's measurements. Harness-wide convention (r86–r95), not
   r99-specific — residual only.
5. e_lan's emission-witness floor is 1000 packets against a ~20000-packet
   window (`:52537-52539`) — a mostly-dead arm (~5 % of nominal) would still
   pass the witness; the exact count is recorded and the lead checks
   quantitative outputs. Hardening note, not a defect claim.
6. Operability is host-bound by design: the census leg's `pacman -Q` and
   man-page arms red (not block) on a non-Arch host. The family is a native
   battery; portability beyond this host class is not claimed.
7. Sibling scribe/simplifier reports were not cross-read (outside my
   assigned reading list); I read the verifier's report and the post-pin
   safety record as evidence. My findings stand on primary sources.

## Artifacts and attribution

- This report: `reports/round-99/r99-critic.md`. Scratch:
  `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-critic/
  commands-evidence.md` (full command log + extracted facts). Both are new;
  no tracked repo file was touched by this seat.
- Receipts (local ignored-path evidence, not committed, not remote):
  author greens `audio-shokunin/audio-shokunin-wt-r99/corpus/live/runs/
  20261016T103556786349Z-rtp-r99/` and `…/20261016T104041659031Z-rtp-r99/`
  (+ `corpus/live/r99-author/` manifest and exit census); integration
  `corpus/live/runs/20261016T121018453359Z-rtp-r99/`; default-safe
  `corpus/live/runs/20261016T122858496567Z-rtp-r99/`; verifier
  `audio-waveb-resume/r99-verifier/tree/corpus/live/runs/
  20261016T124136092601Z-rtp-r99/`.
- Post-pin record (context, one commit past the review pin): `90a7a9c6`
  (LOG entry + `reports/round-99/r99-network-safety.md`) and
  `/home/vgpnk/Projects/shokunin/r99-network-safety-proof/`.
- Attribution: critic seat, wave B, round 99 — advisory findings only. The
  lead inspects the receipts and raw outputs; admission, gating and any
  repair land upstream of this seat. Not judged, not admitted, not shipped.

*critic leaf — attacked the pinned bytes and the receipts; executed nothing
that measures; stopped after the assigned review.*
