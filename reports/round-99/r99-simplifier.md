# r99 simplifier — weight inventory of the pinned r99 family

Seat: **SIMPLIFIER** (leaf, read-only). Round **99**. Source pin
`bb177513a615a32d3bc150ecbdcf78302e110d8c` ("r99 safety: require explicit
opt-in before physical LAN control", 2026-10-16 12:29:41Z). Family flag
`rtp-r99`. Report path: `reports/round-99/r99-simplifier.md`; scratch:
`/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-simplifier/`.

**Scope.** The pinned r99 surface only: `corpus/fixtures/measure_audio.py`
lines 50784–52809 (the `rtp_*_r99_*` family: six entries wired at 55251–55256
behind `--probe-rtp-r99`), `corpus/fixtures/r99rtp.py` (459 lines),
`corpus/fixtures/test_rtp_r99_lan_control.py` (49 lines), plus the round's
frozen reports (scout, boundary, author, integration) and the two frozen
r99 run receipts under `corpus/live/runs/`. No other round's family was
inventoried beyond the shared helpers r99 calls.

**Commands actually executed.** `git cat-file`/`log`/`ls-tree`/`show`/`grep`
against the pin; `sha256sum` verification of scratch copies against
`git show` output (all three files byte-identical:
`measure_audio.py 801e153b…`, `r99rtp.py 36b6b6f8…`,
`test_rtp_r99_lan_control.py f63d1399…`); literal `grep` over the scratch
copies; `python3` JSON reads of the two frozen receipts
(`20261016T121018453359Z-rtp-r99`, `20261016T122858496567Z-rtp-r99`).
**No live family was run, no source was edited, no experiment was executed,
`RTP_R99_ALLOW_LAN_CONTROL` was never set, no service was touched.**

**Method disclosure (required).** No LSP device is available in this seat's
toolset; every reference-absence claim below is a **literal census** (git
grep over the full pinned tree + direct reading of every call site in the
r99 section). That is not semantic proof; a call site reached only through
dynamic dispatch would be missed — none exists in this family (the six
entries are called directly at 55251–55256). Where I say "no caller in the
pin tree", read "no literal textual reference in any tracked file at the
pin".

**Deletions made: none.** This seat holds no edit scope; everything below is
a deletion candidate or an inventory item with evidence attached.

---

## Findings (severity order)

### F1 — HIGH — e_native's source-side law is unreachable as wired: the sink and the source are bound one port apart (observed)

- Where: `measure_audio.py:52334-52338` (the e_native fragment);
  defaults at `:51220` (`port = RTP_R99_PORT`) and `:51249`
  (`src_port = RTP_R99_PORT + 1`).
- Failure path: the leg loads the sink with default `destination.port =
  RTP_R99_PORT` and the source with default `source.port = RTP_R99_PORT +
  1`. The sink emits to `239.255.42.99:<P>`; the source binds
  `239.255.42.99:<P+1>`. A UDP datagram addressed to the group on `<P>` is
  never delivered to a socket bound on `<P+1>`, so the source can never
  receive a packet, whatever the kernel does with multicast delivery.
- Evidence (observed, frozen receipts — not re-derived):
  - Run `20261016T121018453359Z-rtp-r99`, `legs.e_native.fragment`:
    sink `destination.port = 46601`, source `source.port = 46602`;
    `legs.e_native.sink_sockets` row 2: `UNCONN … 239.255.42.99:46602`.
  - Run `20261016T122858496567Z-rtp-r99`: sink `destination.port = 46794`,
    source `source.port = 46795`; same one-port offset. In both runs the
    verdict is `source_recorded_peak: 0.0`, `source_rtp_ssrc: "0"`.
- Consequence: the leg's success branch (`:52391-52394`, the
  `_rtp_r99_dominates` assertion on the recording) is **unreachable as
  wired**; the only reachable outcome is the coverage-block `else`
  (`:52395-52405`). The block message attributes the silence to "host
  state … the sink's socket carries the host's LAN address on lo" and
  calls the difference "not a module law". That attribution is incomplete:
  the receipt's own `sink_sockets` row 2 records the source bound one port
  off the sink's destination, which alone guarantees the silence. The
  boundary's §5.3 clarification (a lo-bound multicast send is delivered by
  the kernel to sockets joined on any interface, with the host's LAN
  address as source) further undercuts the address-check hypothesis: the
  boundary's own e2e recorded the tone over this shape. The misnamed
  `sink_sockets` field (F8) carried the disproving row all along; it was
  recorded and never read.
- Smallest correction (proposed, **not executed** — no live families for
  this seat): pass the source the sink's destination port, i.e. at
  `:52338` use `_rtp_r99_source_args(src_port=RTP_R99_PORT)` (or give the
  sink `port=RTP_R99_PORT + 1`). One argument. Note the co-located tap on
  the same group/port (`:52346`) then competes with the source for
  datagrams — the scout's disclosed tap-loss artifact; the boundary's e2e
  ran the same competition and still recorded the tone.
- Class: unreachable branch (inventory) + wrong recorded attribution
  (calibration). The block itself is honest (e_native stays unmeasured);
  the *reason* recorded in the receipt is not the mechanism the source
  shows.

### F2 — HIGH — the integration-cited r99 receipt was produced by pre-repair bytes: its LAN positive control transmitted on the operator's LAN (observed)

- Where: `reports/round-100/r93-r99-r100-integration.md:43-44` cites r99
  receipt `corpus/live/runs/20261016T121018453359Z-rtp-r99/measurements.json`.
- Evidence: that receipt's `legs.e_lan_control` carries
  `arm_tx_packets: 6034`, `fraction_of_emission: 1.006`, and **no**
  `measured`/`blocked` keys — the control ran and egressed on the
  operator's LAN interface. The pin's guard (`measure_audio.py:52608`,
  default-off, else-branch block at `:52637-52643`) postdates that run:
  the repair commit is 12:29:41Z, the cited run 12:10:18Z. The later run
  `20261016T122858496567Z-rtp-r99` (12:28:58Z, 43 s before the commit)
  shows the repaired behavior: `e_lan_control = {measured: False,
  blocked: "…requires explicit operator approval and
  RTP_R99_ALLOW_LAN_CONTROL=1"}` and that message in
  `coverage_blocked`.
- Consequence: the integration note's "all three families were run once,
  concurrently, on the final source" does not hold for the cited r99
  receipt with respect to the LAN-control guard — the cited evidence is
  pre-repair for this guard. The pinned source itself is correct (default
  off; verified by run 2 and by the guard's AST test), and this seat set
  no opt-in and ran nothing; the finding is about which receipt the
  integration note cites, not about the pinned code.
- Smallest correction (lead-side, not mine): re-cite the post-repair
  receipt (`…122858496567Z…`) for the r99 row, or re-run the family once
  on the pinned bytes so the cited receipt shows the default-off block.

### F3 — MEDIUM — dead code and documented-but-absent options in `r99rtp.py` (source-proven reference absence, literal census)

- `decode_s24be` (`r99rtp.py:178-186`): zero callers anywhere in the pin
  tree (git grep over all tracked files matches only the definition). The
  module docstring advertises `--format s16|s24` for send mode
  (`:30`) but the send parser (`:424-441`) defines no `--format`, so the
  s24 path is documented but never wired. **Deletion candidate, with
  tradeoff:** this is an extension-point withdrawal — it is the only
  in-repo S24BE decoder, and C14's *content* law is currently
  recorded-not-armed (the `r_s24be` leg asserts shape only:
  `measure_audio.py:52144-52150` — size 300, ptime, framecount,
  `rtp.mime=L24`; its tap payload is decoded by `decode_s16be` inside
  `recv` mode, so the recorded content fields for that leg are
  meaningless-but-unarmed). If a follow-up ever arms S24 content, this
  function becomes load-bearing. Withdrawal is a tradeoff, not a pure win.
- `analyse(packets, sizes_note=None)` (`:196`): the `sizes_note`
  parameter is never referenced in the body (grep matches only the def
  line). **Deletion candidate, no tradeoff** — pure dead parameter.
- `tone_slice_fraction(x, rate, freq, amp, step=16)` (`:131-152`): the
  `step` parameter is never used in the body, and the docstring
  (`:133-138`) describes lattice membership "congruent to its own index
  mod `step`" which the body does not implement (it compares each sample
  against the tone value at its own index, no mod). Both call sites
  (`:307`, `:398`) pass no `step`. **Deletion candidate for the
  parameter** plus a docstring correction; implementing the documented
  mod-step behavior would be a behavior change and is out of scope for
  this seat.
- `import os` (`:50`): zero `os.` references in the file. **Dead import,
  deletion candidate, no tradeoff.**
- Docstring documents `--min-arrivals` for recv mode (`:19`); the recv
  parser (`:415-422`) does not define it, and no `min_arrivals` symbol
  exists anywhere in the pin tree. Documented-but-absent option — stale
  doc (or an unwired feature); the doc line should be corrected, not the
  parser grown.

### F4 — MEDIUM — redundant core bring-up cycle plus a stale comment in `rtp_e2e_r99_entry` (source-proven)

- Where: `measure_audio.py:52413-52421`.
- The fragment clear at `:52413` **is load-bearing** (a stale fragment
  would make the next core load leftover daemon-side sink+source under
  the seat's names, and e_sap's `own_nodes == []` assertion would
  false-red) — keep it. But the `_rtp_r99_core_up(inst)` at `:52414`
  brings a core+WirePlumber up that **no leg uses**: e_sap's
  `_rtp_r99_core_up(inst, with_wp=False)` at `:52432` unconditionally
  tears the instance down first (`:50993`), and e_relink brings its own
  core up at `:52461`. The cycle is pure overhead (one core+WP start and
  stop per e2e run).
- The parenthetical comment at `:52415-52416` is stale on both counts: it
  calls the SAP leg "above" (it is below, `:52428`) and claims the core
  is brought back "for e_relink/e_lan" (it is torn down before either;
  e_relink re-ups). Evidence of a reordered block whose comment was not
  updated.
- **Deletion candidate:** the `:52414-52421` bring-up + block (keep the
  `:52413` clear). Tradeoff: loses the recorded
  `entry["bringup_client_route"]` health-check field (present in both
  frozen receipts) and the early block point; failure detection shifts to
  e_relink's bring-up (`:52461`) and to e_sap's `own_nodes` assertion,
  which is the actual verifier of the clear. Receipt shape changes.

### F5 — LOW-MEDIUM — teardown misclassifies a missing stream-properties store as "unreadable / unmeasured" (source-proven, latent)

- Where: `measure_audio.py:51481-51498`.
- `own_rows` starts `None` and is only assigned inside
  `if store.exists():`. A **missing** store file proves zero own rows (no
  rows can exist in a file that does not exist) — a clean witness — but it
  falls into `elif own_rows is None:` and appends the coverage block
  "teardown: stream-properties store unreadable — the shared-store
  witness is unmeasured". The message is also literally wrong for a
  missing file (nothing was unread).
- Latent on this host: both frozen receipts record
  `shared_stream_properties_own_rows: []` (the store exists and is
  clean), so the branch never fired here. It would mislabel a clean host
  that has never written the store.
- Smallest correction: `own_rows = []` when the store is absent; keep
  `None` (unmeasured) only for a read `OSError` on an existing file.

### F6 — LOW — e_lan's pw-cli spawn failure is a silent skip (fail-open), unlike every sibling leg (source-proven, latent)

- Where: `measure_audio.py:52512-52513` (`cli, _ = _rtp_r99_cli_open(inst)`
  — the message is discarded) with the assertions at `:52537+` nested
  inside `if cli is not None:` → `if lan["node"].get("reached"):`.
- If the spawn fails, `legs["e_lan"]` records `{"iface": …}` + note with
  **no failure and no coverage block** — the C7 law silently absent from
  an otherwise-green entry. Every sibling leg is fail-closed on the same
  event: s_two (`:51861-51883`, assertions fire on the empty dict),
  e_relink (`:52489-52495`, `packets > 0` fails), a_target_pos
  (`:52785-52792`). The opt-in-gated e_lan_control has the same shape
  (`:52618`). Latent: pw-cli spawned in both receipts; inferred from
  source, not observed. (The missing-witness acceptance shape is the
  critic's axis; recorded here because it is also an unreachable-witness
  path in the inventory sense.)

### F7 — LOW — never-overridden parameters (unused-in-practice knobs) in the r99 harness (literal call-site census)

All call sites read directly; counts are literal, not semantic:

- `_rtp_r99_ready(want_node=RTP_R99_SINK)` (`:51377`) — 3 call sites
  (`:51724`, `:52034`, `:52677`), all default.
- `_rtp_r99_tap(ifname="lo")` (`:51305`) — 6 call sites (`:51677`,
  `:51868`, `:52346`, `:52474`, `:52519`, `:52772`), all default.
- `_rtp_r99_play(wait=True, timeout=45)` (`:51267-51268`) — 8 call sites,
  none overrides `wait` or `timeout`.
- `_rtp_r99_core_up(timeout=45.0)` (`:50988`) — 11 call sites; only
  `with_wp` is ever overridden (`:52174`, `:52432`).
- `_rtp_r99_sink_leg(seconds=None, want_play=True)` (`:51651-51653`) — no
  call site passes either; the `if not want_play:` branch
  (`:51674-51676`) is never taken by any authored leg.
- `_rtp_r99_sink_args(sess=None)` (`:51214`) and
  `_rtp_r99_source_args(sess=None, latency=100)` (`:51248`) — no call
  site passes `sess` or `latency`.

Class: unused-in-practice arguments. **Deletion candidates only with the
extension-point tradeoff:** these are arg-builder knobs; removing them
narrows the surface for future legs (withdrawal of an extension point).
The zero-risk subset is `want_play` (whose branch is dead in every
authored leg) and the never-overridden `wait`/`timeout` on `_play`.

### F8 — LOW — duplicate observations and a misnamed field

- `_rtp_r99_udp_sockets` (`:51190-51208`) returns **all** private-core
  UDP sockets — on the fragment route that includes the *source's* socket
  — but every consumer names the result `sink_sockets` (`:51673`,
  `:52369`, `:51877`) and the e_native verdict quotes only row 0 as
  `sink_socket` (`:52386`). The source's row — the one that exposes F1 —
  was recorded in both receipts and never examined. Rename or filter;
  smallest correction is a field rename plus quoting both rows in the
  verdict.
- `entry["tools"]` (`:51542-51546`) vs `legs["c_absent"]["which"]`
  (`:51589-51590`): the absent-tool `which` paths are recorded twice in
  the census entry.
- `s_two` (`:51859-51904`) and `a_target_pos` (`:52762-52792`) duplicate
  the two-sink load/tap/play/read shape (~15 lines) while arming
  different laws (coexistence/socket shape vs flag order). Retained:
  folding them would couple two independently-armed laws.
- `_rtp_r99_eq/_true/_peak_exact/_dominates` (`:51409-51435`) parallel the
  r100 family's `_sofa_r100_eq/_true/…` one-for-one. Retained by the
  established insertion-only per-family convention; unifying them would
  create cross-family coupling — a second convention — which this seat
  will not propose.

### F9 — LOW — doc/behavior mismatches in the harness

- `_rtp_r99_run` docstring (`:50860-50862`): "the scrub rewrites
  `r99a_<pid>` to `r99a_<pid>`" — before and after are the same string.
  The regex at `:50850` rewrites `r99a_?[0-9]+` → `r99a_<pid>`; the
  docstring's "before" form should be the digits-bearing form.
- The same docstring's MUST rule ("scrub MUST be False for any call whose
  stdout this family parses") vs `_rtp_r99_udp_sockets` (`:51203`), which
  parses `ss -unap` output captured with the default `scrub=True`.
  Harmless today — the row filter is `pid=<digits>` and ss rows carry no
  `r99a<digits>` process names — but the parsed stdout is scrubbed
  contrary to the stated rule. Doc correction or a `scrub=False` for
  consistency.

### F10 — EVIDENCE GAP — the LAN-control regression test exists but has no recorded execution

`corpus/fixtures/test_rtp_r99_lan_control.py` (tracked at the pin)
AST-extracts the single `RTP_R99_ALLOW_LAN_CONTROL` guard from
`rtp_e2e_r99_entry` and proves default-off for `None`/`""`/`"0"`/`"true"`
and barrier-reach for `"1"` without sending. No tracked file references it
(git grep over the pin tree: zero content matches outside the file
itself), and the integration note records compile/help/mutex checks and
the r90 lock regression but not this test. Its pass status is unrecorded
in the evidence this seat read. Behavioral proof of the default-off
exists independently — run `…122858496567Z…` shows the blocked leg — so
the guard is evidenced; the *test's* execution is not. For the lead to
close.

### F11 — EVIDENCE GAP — LOG.md at the pin contains no r99 entry

`git show PIN:LOG.md | grep -ci r99` → 0. The lead's log does not record
the r99 family landing at the pinned revision. Provenance note only; the
scribe owns report→receipt linkage.

---

## What the evidence does support

- **The pinned default-off repair is real and single.** Exactly one
  `RTP_R99_ALLOW_LAN_CONTROL` guard exists in `rtp_e2e_r99_entry`
  (`:52608`), its else-branch records `measured: False` + the
  "requires explicit operator approval" block (`:52637-52643`), the AST
  test's expectations match that text exactly, and run
  `…122858496567Z…` shows the block firing with no egress. The opt-in
  branch is the disclosed positive control — **not** a deletion
  candidate; it is the extension point this round's repair exists to
  gate, and it is preserved.
- **The leg-key arithmetic matches the assignment.** Six entries wired at
  `:55251-55256`; leg-dictionary keys per receipt: census 3, sink 8,
  source 7, refusal 8, e2e 6, axis 5 = **37**, of which four are `tone`
  setup records (sink/source/e2e/axis) and 33 are non-tone cells —
  exactly the assignment's "37 leg-dictionary keys = four tone setup
  records plus 33 non-tone cells".
- **All 21 module-level `RTP_R99_*` constants and `_RTP_R99_*` structures
  are referenced** (census over the r99 section); no dead module-level
  symbol in the harness.
- **Inherited helpers are reused, not duplicated:** `_pwprof_r89_norm`,
  `_pwprof_r89_errclass`, `_jack_r95_graph`, `_jack_r95_settings`,
  `_playback_r78_foreign_clients`, `_playback_r78_node_names`,
  `_capture_r77_sink_names_strict`, `_alsapw_r84_loadavg`,
  `_alsapw_r84_killpg` are each defined exactly once in the file and
  called by the r99 family (`_jack_r95_settings_restore` is a distinct
  function, not a second definition).
- **The family lock is wired once and held to exit** (`:55250`, fixed
  path `corpus/live/measure_audio-rtp-r99.lock`, `:50903-50919`), same
  convention as r86–r95. One adjacent note for the critic: the
  `except OSError: return None` at `:50911-50912` proceeds **unlocked**
  if the lock file cannot be opened — a fail-open mutex, latent, not
  observed.
- **Teardown witnesses are clean in both frozen receipts** (socket-gone
  true, no own daemon pids, no shared r99a nodes, no own store rows, zero
  failures in all six entries).

## Residual risks and explicit checks not run

- **Not run (by design, this seat):** the live family, the LAN-control
  test, the verifier recipe, any before/after experiment, any `pactl` or
  service interaction. F1's one-argument correction is proposed, not
  executed; its confirmation belongs to the verifier/lead on the pinned
  bytes.
- **F1 residual:** even with matched ports, e_native's outcome on this
  host is not guaranteed by this seat's evidence — the boundary's e2e
  (matching shape, different probe code) recorded the tone, and the
  boundary's §5.3 explains the LAN-address peer as this host itself, but
  the author's "receiver-side address check" hypothesis is untested
  either way. The correction removes the *proven* blocker; the
  hypothesis remains unmeasured until a run says otherwise.
- **F2 residual:** I did not verify which source bytes run 1 was produced
  from beyond the receipt's own shape (no `measured`/`blocked` keys on
  `e_lan_control` ⇒ pre-guard code path). A lead-side check of the
  integration snapshots under `/home/vgpnk/Projects/shokunin/audio-resume-integrations/`
  can pin the exact source hash of that run; I did not read that tree.
- **Reference-absence method:** literal census only (no LSP device
  available; recorded as required). Grep output here is evidence of
  textual absence, never semantic proof.
- **F5/F6 are latent** — neither fired in the frozen receipts; both are
  source-read inferences.

## Artifact paths and attribution

- Pinned sources read (scratch copies, sha256-verified against
  `git show PIN:…`): `audio-waveb-resume/r99-simplifier/pin/{measure_audio.py, r99rtp.py, test_rtp_r99_lan_control.py}`.
- Frozen receipts read (not re-derived, not modified):
  `audio-shokunin/corpus/live/runs/20261016T121018453359Z-rtp-r99/measurements.json`,
  `audio-shokunin/corpus/live/runs/20261016T122858496567Z-rtp-r99/measurements.json`.
  These are local receipts; nothing here implies they are committed or
  remotely available.
- Receipt evidence extract saved:
  `audio-waveb-resume/r99-simplifier/e-native-port-evidence.txt`.
- Reports read: `reports/round-99/r99-scout.md`,
  `reports/round-99/r99-boundary.md`, `reports/round-99/r99-author.md`,
  `reports/round-100/r93-r99-r100-integration.md`.
- No source file, fixture, report, LOG, SCORECARD, MANIFEST or corpus
  file was modified by this seat. The shared tree is unchanged; my only
  writes are this report and my scratch directory.

*simplifier leaf — inventory and deletion candidates with evidence; nothing
deleted, nothing executed, nothing judged.*
