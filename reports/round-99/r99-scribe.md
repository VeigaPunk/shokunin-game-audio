# r99 scribe — provenance audit: report → receipt → author bytes → integrated bytes → pin

Seat: SCRIBE (leaf, wave `shokunin-train-20261016-w24`). Round **N=99**, role
**scribe**, FLAG **rtp-r99**, source pin
**`bb177513a615a32d3bc150ecbdcf78302e110d8c`** — verified as HEAD of
`/home/vgpnk/Projects/shokunin/audio-shokunin`, commit *"r99 safety: require
explicit opt-in before physical LAN control"*, 2026-10-16 09:29:41 −0300.
First action: loaded the `glmseat` skill (`.devin/skills/glmseat/SKILL.md`,
model pin `glm-5-3-flash-max` — matches this seat's runtime; no routing,
profile, config or session-state edits). Godspeed loaded once. This seat is an
audit leaf: **no live family run, no subagent, no source edit, no commit; the
only repo write is this report**; scratch is
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-scribe/`.
`RTP_R99_ALLOW_LAN_CONTROL` was **never set** by this seat.

## 1. Commands actually executed (read-only unless noted)

- `git rev-parse / log -1` on the pin; `git status --porcelain` (no
  modified tracked files; untracked evidence trees only); `git check-ignore`
  on `corpus/live` paths (ignored, as the integration report states).
- `git show <rev>:corpus/fixtures/{measure_audio.py,r99rtp.py}` at
  `bb177513`, `193acbed`, `81a5b55d` + `sha256sum`; worktree snapshot hashes
  (`audio-shokunin-wt-r99/corpus/fixtures/*`).
- Receipt parsing (python3/json) of four r99 receipts: author run 1/2
  (`audio-shokunin-wt-r99/corpus/live/r99-author/measurements-run{1,2}.json`
  and their `runs/20261016T103556786349Z` / `…104041659031Z` twins) and the
  two integration-era receipts `corpus/live/runs/20261016T121018453359Z-rtp-r99/`
  and `…122858496567Z-rtp-r99/`.
- Family-slice extraction and byte-diff: r99 block
  (`# r99a — the NATIVE RTP NETWORK-TRANSPORT surface`, pin line 50673) to
  block end, across author / integrated / pinned bytes.
- **One execution, static and local**: exported the pin's
  `test_rtp_r99_lan_control.py` + `measure_audio.py` into my scratch
  (`r99-scribe/gate-test/`) and ran
  `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest test_rtp_r99_lan_control -v`
  → **Ran 2 tests … OK, rc 0** on the exact pinned bytes (`801e153b…`). This
  is the gate's own AST test (no audio, no network, no family); not a
  measurement and not a family run.
- Read: r99-scout.md, r99-boundary.md, r99-author.md,
  `reports/round-100/r93-r99-r100-integration.md`,
  `audio-resume-integrations/byte-cmp.commands` + `cmp-r99-*.rc/stdout`,
  LOG.md, SCORECARD.md, the r99-verifier scratch (read-only).

## 2. The chain, link by link (all observed)

| link | bytes / hashes | verdict |
| --- | --- | --- |
| author report → author bytes | r99-author.md records `measure_audio.py 1bb2f98b…`, `r99rtp.py 36b6b6f8…`; the author worktree snapshot `audio-shokunin-wt-r99/corpus/fixtures/` hashes **match exactly** | OK |
| author bytes → author receipts | `r99-author/measurements-run1.json` ≡ `runs/20261016T103556786349Z-rtp-r99/measurements.json` (`fc120288…`), run2 ≡ `…104041659031Z` (`efddd5c8…`); `manifest.sha256` lists exactly those four hashes; CLI logs present; `exit-census.json` clean (0 own graph objects / processes / store rows / sockets; defaults SPDIF/Line unchanged; `pactl_set_default_issued: false`) | OK |
| author bytes → integrated bytes | `81a5b55d` `measure_audio.py = 7b372a6b…` = the integration report's r99 stage sha; `r99rtp.py = 36b6b6f8…` = author's; `r99-author.md` committed byte-identical to the author worktree (orchestrator `cmp -s` rc 0, frozen in `audio-resume-integrations/`); **r99 family slice byte-identical author vs integrated** (2127 lines, slice sha `a1669ca9…`) — the "verbatim author slices" claim holds for the family body | OK |
| integrated → final-byte run | `193acbed` `measure_audio.py = 5c8f7e9d…` = the integration report's "r100 final" stage sha; receipt `…121018453359Z-rtp-r99` (the one the integration report cites): six entries, **37 leg keys**, `e_native` coverage-blocked, `e_lan_control` **measured** (pre-safety bytes) | OK |
| integrated → pin | `bb177513` `measure_audio.py = 801e153b…`; r99-slice diff vs integrated is **only** the `e_lan_control` opt-in gate (slice lines 1936–1971 = pin lines ~52608–52648) plus the new `test_rtp_r99_lan_control.py`; `r99rtp.py` unchanged (`36b6b6f8…`) | OK |
| pin → post-safety receipt | `…122858496567Z-rtp-r99` (12:28:58Z, 43 s before the commit stamp): `e_lan_control = {measured: false, blocked: "…requires explicit operator approval and RTP_R99_ALLOW_LAN_CONTROL=1"}` + `coverage_blocked` entry; `e_lan` armed in the strongest form (`resolution.verdict: "armed_below_band"`, idle_band 2802, emitted 20001, excess −1657); `e_native` blocked with the **identical** message text as run 1; all other legs structurally unchanged; five private-core entries `socket_gone: true`, `own_daemon_pids_alive: []`; `failures` empty in all six entries | OK |

**Counts (no stale numbers found).** Every receipt and the pinned source
agree: six entries; leg-dictionary keys 3+8+7+8+6(+1 dup site)+5 = 37 runtime
keys = **4 `tone` setup records** (sink/source/e2e/axis, amp_i16 16383,
freq 997) **+ 33 non-tone cells** (`c_*`×3, `s_*`×7, `r_*`×6, `x_*`×8,
`e_*`×5, `a_*`×4) — exactly the review-common r99 description and the author
report's "six entries, 33 legs". (The pinned source assigns
`legs["e_lan_control"]` at two static sites — if/else branches — one runtime
key.)

**Gate (default-off), verified three ways.** (a) Source: the pinned
`e_lan_control` arm is wrapped in
`if os.environ.get("RTP_R99_ALLOW_LAN_CONTROL") == "1"` (exact-string compare;
pin line 52608) with an else branch recording `measured: False` + a
`coverage_blocked` message (pin ~52638–52648); `e_lan` (loopback confinement)
is **outside** the gate. (b) Executed: the pin's own AST test on the pinned
bytes — no opt-in (`None`/`""`/`"0"`/`"true"`) leaves the leg unmeasured and
never opens the client; exact `"1"` reaches the control via a barrier mock
(2/2 OK, rc 0). (c) Observed behavior: the 12:28Z receipt shows the leg
blocked by default. This seat never set the variable.

## 3. Findings (severity order)

1. **Citation locations dangle from the repo root (moderate; observed).**
   `r99-author.md` cites `corpus/live/r99-author/` and
   `corpus/live/runs/20261016T103556…Z-rtp-r99/` / `…104041…Z` — none exist in
   the main worktree (the author's teardown note + later cleanup removed
   them). They resolve only inside the **untracked** author-worktree snapshot
   `audio-shokunin/audio-shokunin-wt-r99/`, where every cited byte survives
   and hash-matches. Concrete failure path: a reader following the author
   report from the repo root hits ENOENT and could wrongly conclude the
   receipts are lost. Smallest correction: a lead-authored provenance note
   naming the snapshot as the receipt home (or relocating the four files);
   not mine to apply. The integration report's own citation
   (`…121018453359Z-rtp-r99`) resolves fine.
2. **No receipt binds itself to the source bytes that produced it
   (moderate; observed gap, inferred binding).** r99 receipts record
   `payload_sha256` (×16) and `rtp_sha256` (×1) of stimuli but **no sha of
   `measure_audio.py`/`r99rtp.py`**. Receipt→source binding therefore rests
   on run-stamp timestamps + the integration report's stage-sha table + my
   slice diffs. In particular the 12:28Z receipt's identity with the pinned
   bytes is **inferred** (43 s before the commit stamp; gate-blocked behavior
   present) — not hash-proven. The r99 verifier's minimal export **is**
   pin-exact (`801e153b…` / `36b6b6f8…` hashed in their scratch tree), but
   their run's stdout/stderr were **empty at my report time** — the
   pinned-bytes full-family execution is not witnessed by this report.
   Smallest correction: future receipts could embed the source sha; nothing
   retroactive is repairable, and I do not recompute any measurement.
3. **Lead ledgers are stale through no seat's fault (low; observed).**
   LOG.md's last entry is ROUND 97 — no r98/r99/r100 rows; SCORECARD.md ends
   at the r86 verdict. Consistent with the integration report's "Outstanding
   Gates" (wave-B review and adjudication pending). Lead-owned files;
   untouched by me; recorded so the gap is visible.
4. **Original vs corrected artifacts kept distinct (info; no defect).** The
   author's whole-file sha (`1bb2f98b…`) ≠ integrated (`7b372a6b…`) ≠ pin
   (`801e153b…`) **by construction** (different wiring base, then the safety
   gate) — disclosed by the integration report, and the invariant that
   matters holds: family slice byte-identical author→integrated, gate-only
   integrated→pin. The author's cleanup note (run #1's dir deleted, receipt
   preserved byte-identically, sha `fc120288…`) is corroborated by the
   surviving copies. The pre-safety receipts' measured `e_lan_control`
   (8626/6975-packet class disclosures) remain **original** evidence of
   pre-safety bytes; the 12:28Z blocked leg is the **corrected** default. No
   receipt is presented as something it is not.

## 4. What the evidence supports (blocked vs measured)

- **Measured/observed:** the declared r99 shape (6 entries, 37 = 4+33) in all
  four receipts and the pinned source; byte-identical author→integrated
  family slice; pin-vs-integrated diff confined to the LAN gate; default-off
  gate executed green on pinned bytes (static AST test); post-safety
  receipt's `e_lan` armed `below_band` and `e_native` still explicitly
  unmeasured with unchanged message text; clean exit censuses.
- **Explicitly blocked/unmeasured (correctly labeled, everywhere):**
  `e_native` — sink emits (wire peak `0.499969482`, socket
  `192.168.0.253%lo → 239.255.42.99`) but the co-located source records
  silence (`peak 0.0`, `rtp.ssrc 0`); the receipts say "C6 is not falsified
  here, it is unmeasured". `e_lan_control` post-safety: unmeasured by design
  without opt-in.
- **Not witnessed by this report:** the pinned-bytes live family run
  (verifier's lane incomplete at report time); any quantitative verdict —
  the lead checks those; I claim none.

## 5. Residual risks and checks not run

- No live family, no re-derivation of any measurement, no network or audio
  operation by this seat; shared daemons untouched; no `pactl set-default-*`.
- The 12:28Z receipt's byte-identity to the pin is inferred (§3.2), not
  hash-proven; the verifier's outcome is unknown to me.
- C6 (native pair end-to-end) remains unmeasured on this host in every
  receipt; the author's named residuals stand untested here: receive-path
  peak overshoot (recorded, never armed), `a_quantum` set-equality
  non-reproduction (mechanism armed, set recorded), opus/MIDI/VBAN/netjack2/
  avb unmeasured, LAN-counter idle-band width (6599–8505/20 s in the author's
  passes).
- I did not audit r93/r98/r100 (other seats' rounds) beyond the shared
  integration report; I did not verify the orchestrator's `cmp` snapshots
  beyond their frozen rc/stdout files.

## 6. Artifacts and attribution

- This report: `reports/round-99/r99-scribe.md` (the only repo file I wrote).
- Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-scribe/`
  (`gate-test/` holds the pin-exact `measure_audio.py` +
  `test_rtp_r99_lan_control.py` and the passing unittest run; an
  `evidence-notes.md` summarizes receipt parses).
- Evidence audited (all local, none claimed committed/remote beyond git):
  author/boundary/scout reports (`reports/round-99/`), integration report
  (`reports/round-100/r93-r99-r100-integration.md`), four r99 receipts (two
  author-era inside `audio-shokunin-wt-r99/`, two integration-era under
  `corpus/live/runs/`), orchestrator byte-comparison evidence
  (`/home/vgpnk/Projects/shokunin/audio-resume-integrations/`), r99-verifier
  scratch tree (read-only peek).
- Attribution: scout/boundary/author/integration content is those seats' and
  the orchestrator's work; I audited links only. Advisory — no round
  admission, no judge verdict, no shipping authority.

*Leaf scribe — chain audited on frozen bytes; stopped after this report.*
