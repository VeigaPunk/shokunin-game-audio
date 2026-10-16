# r99 reviewer — caller/error-path/propagation audit of the pinned r99 family

Seat: REVIEWER (leaf, read-only audit; no live family, no source change, no
subagent). Round N=99, role=reviewer, FLAG=rtp-r99.
Source pin: `bb177513a615a32d3bc150ecbdcf78302e110d8c`
("r99 safety: require explicit opt-in before physical LAN control", parent
`193acbed`). Scratch: `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-reviewer/`.

**LSP status: no LSP device/server is available in this seat's toolset.** Every
check below is literal inspection of pinned bytes read via
`git show PIN:path` (worktree verified byte-identical to the pin for all three
r99 files: `git diff --stat PIN -- corpus/fixtures/measure_audio.py
corpus/fixtures/r99rtp.py corpus/fixtures/test_rtp_r99_lan_control.py` is
empty). Grep/read output here is text evidence, not semantic proof; findings
are labeled source-proven (read from pinned bytes), observed (executed or read
from an existing receipt), or inferred (reasoned from source, not executed).

## Commands actually executed

- `git show PIN:corpus/fixtures/measure_audio.py` (full 55,974-line pinned
  bytes; r99 family = lines 50784–52804), `…r99rtp.py` (459 lines),
  `…test_rtp_r99_lan_control.py` (49 lines) — read in full.
- `git log/ls-tree/show` at the pin; `git check-ignore`; `git status`.
- Read-only receipt inspection (no derivation re-run):
  `corpus/live/runs/20261016T121018453359Z-rtp-r99/measurements.json` and
  `…/20261016T122858496567Z-rtp-r99/measurements.json` (mode
  `probe-rtp-r99`), plus `LOG.md` r99 entries and
  `reports/round-99/{r99-scout,r99-boundary,r99-author,r99-network-safety}.md`.
- sha256 of the pinned `measure_audio.py` bytes:
  `801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f` — equals
  the safety report's `source-after.sha256` and the proof dir's claim.
- **One execution**: the committed AST guard regression, run against the
  pinned bytes copied into my scratch (`PYTHONDONTWRITEBYTECODE=1 python3
  test_rtp_r99_lan_control.py -v`) → `Ran 2 tests … OK`, rc 0, no network, no
  fixture execution, no repo write. This is the only code I executed; I did
  not run the family and never set `RTP_R99_ALLOW_LAN_CONTROL`.

## R99-specific mandate: the physical-LAN control cannot run by default — VERIFIED

1. **Source-proven**: the only module load in the pinned r99 family that binds
   `local.ifname` to the operator's LAN interface is
   `measure_audio.py:52620-52621`
   (`_rtp_r99_sink_args(dest_ip=RTP_R99_MCAST, ifname=iface)`), and it sits
   inside `if os.environ.get("RTP_R99_ALLOW_LAN_CONTROL") == "1":` at
   `measure_audio.py:52608`. A repo-wide scan of the family (lines 50784–52804)
   finds `ifname=iface` nowhere else; every other sink load is
   `dest_ip="127.0.0.1"` (helper default, `measure_audio.py:51212`) or
   `dest_ip=RTP_R99_MCAST, ifname="lo"` (`:52336`, `:52516`); every source load
   is `ifname="lo"` (helper default `:51247`) or loopback-unicast with
   `ifname=None` **and** `expect_join=False` (`:52089`, `:52102`, `:52125` —
   all `src_ip="127.0.0.1"`, so no group join at all); every tap joins groups
   on lo only (`:51305` default, explicit `--ifname lo` at `:52072`).
2. **Fail-closed gate**: the test is an exact string compare `== "1"`. Unset,
   empty, `"0"`, `"true"`, `"yes"` all leave the control disabled. The else
   branch (`:52637-52643`) records
   `{"iface": …, "measured": False, "blocked": msg}` in `legs` **and** appends
   the same message to `entry["coverage_blocked"]` — a named block, not a
   silent green. The code never writes the variable (only `os.environ.get`
   reads it; the fixture and tap never read it).
3. **Observed (existing receipts, read-only)**:
   `20261016T122858496567Z-rtp-r99` (the default-safe pass, opt-in unset) has
   `e_lan_control = {"iface": "enp7s0", "measured": false, "blocked": "…
   requires explicit operator approval and RTP_R99_ALLOW_LAN_CONTROL=1"}`, no
   `arm_tx_packets` anywhere, and the loopback confinement leg green
   (`e_lan.resolution.verdict = "armed_below_band"`, emitted 20001, idle band
   2802, excess −1657). The pre-repair receipt `20261016T121018453359Z` shows
   the same leg **measured** (node running, disclosure text) — the disclosed
   egress the safety report records (6,034 TX packets on enp7s0).
4. **Observed (my execution)**: the committed AST regression
   (`corpus/fixtures/test_rtp_r99_lan_control.py`, tracked at the pin) passes
   on the pinned bytes: for (None, "", "0", "true") the guard body records
   `measured: False` + blocked + `coverage_blocked == [blocked]` and never
   reaches `_rtp_r99_cli_open` (a raising barrier proves it); for exactly "1"
   it reaches only the barrier — no audio, no network. The proof dir
   `/home/vgpnk/Projects/shokunin/r99-network-safety-proof/` corroborates:
   `lan-before.rc` 1 → `lan-after.rc` 0, `r99-safe.rc` 0 (env unset),
   `source-after.sha256` = the pinned hash.

## Findings (by severity)

No high or medium severity defect found. All findings are low/informational;
none opens a default LAN path or a silent green.

**F1 (Low, missing-key behavior — inferred).** `measure_audio.py:52503-52643`:
the whole `e_lan`/`e_lan_control` block lives in the `else:` of
`if not iface:` (`:52505-52508`). If `_rtp_r99_default_iface()` returns None
(no default route, `:51364-51373`), **both** `legs["e_lan"]` and
`legs["e_lan_control"]` keys vanish from the receipt (37 → 35 leg keys) and
`e_lan_control` gets no named block of its own — only `e_lan`'s message names
the gap. The safety posture still holds (the control cannot run), but the
family's own 37-key leg invariant and its "named coverage block" convention
are not honored for that leg in this environment. Smallest correction: record
an `e_lan_control` blocked leg (and an `e_lan` leg) in the `if not iface:`
branch too. Not observed on this host (a default iface exists in both
receipts); inferred from source.

**F2 (Low, unmeasured leg without a named block — inferred).** Inside the
opt-in branch, if `_rtp_r99_cli_open` returns None (`:52609`, pw-cli spawn
failure), `legs["e_lan_control"] = ctl` (`:52636`) still records the bare
disclosure dict — no `measured`, no `blocked`, no failure appended
(`:52618-52635` has no else). Same class in `e_lan`: cli None → `lan` carries
only `iface` (`:52512-52513`, `:52599`), no counters/resolution/verdict, no
failure. Both contradict the family's stated convention ("a missing tool … is
a named coverage block, never a silent green", r99-author.md). Mitigation:
`_rtp_r99_core_up` readiness requires `pw-cli info 0` to answer
(`:51015-51018`), so a wholly missing pw-cli blocks the entry at bring-up
before these legs; the sub-path needs a transient exec failure between
bring-up and the leg. Smallest correction: an explicit
`leg["blocked"] = "pw-cli unavailable"` + `coverage_blocked` append on the
cli-None path.

**F3 (Low, counter-None propagation — inferred).** `_rtp_r99_ifcounters`
returns None per key on OSError/ValueError (`:51353-51361`); `e_lan` then
computes `c1["tx_packets"] - c0["tx_packets"]` (`:52532-52534`) → TypeError if
any sysfs counter is unreadable (e.g. interface removed mid-window). The
entry-level `except` catches it (`:52644-52646`) as "entry aborted: …", so it
is **named**, but coarsely: `legs["e_lan"]`/`legs["e_lan_control"]` (assigned
later, `:52599`/`:52636`) are lost while e_native/e_sap/e_relink results
survive. Smallest correction: per-leg None guard producing an `e_lan` blocked
leg instead of an entry abort.

**F4 (Info, blocked-message wording — inferred for one path).** The e_native
coverage-block message (`:52396-52405`) statically asserts "the sink emitted
(see legs.e_native.verdict.sink_emitted …)". In the measured-silence case
(the only one observed in receipts) that is accurate; but in paths where the
sink never ran (core_up failure after the fragment write, or tap/record
failure) `verdict.sink_emitted` is False and the message contradicts the very
field it cites. Smallest correction: derive the clause from
`verdict.sink_emitted`.

**F5 (Info, witness recorded but not armed — inferred).** `settings_at_start`
(`:51454`) and `settings_at_end` (`:51512`) are recorded but never compared,
so a shared-settings drift across an entry would not append a failure.
Consistent with the private-core design (the family never touches shared
settings; no `pactl set-default-*` anywhere in the family — grep over
50784–52804 finds only the r100 header comment), but the witness is
decorative as written.

**F6 (Info, cosmetic).** `_rtp_r99_run`'s docstring (`:50859-50862`) says the
scrub "rewrites `r99a_<pid>` to `r99a_<pid>`" — the before/after example is
garbled (the code at `:50850` correctly rewrites `r99a_<digits>` →
`r99a_<pid>`, and parsing calls correctly use `scrub=False`).

**F7 (Info, evidence availability/attribution — observed).** At the pin:
`corpus/live/r99-boundary/` is tracked; `corpus/live/r99-scout/` exists in
the worktree but is **not tracked** at the pin; `corpus/live/r99-author/` and
the author's two green run dirs (`20261016T103556786349Z`,
`20261016T104041659031Z`) are **absent** — neither tracked nor in the
worktree — so the author report's cited receipt copies cannot be verified
from this tree. `reports/round-99/r99-network-safety.md` and `r99-scribe.md`
exist in the worktree but are not tracked at the pin (ls-tree shows only
author/boundary/scout under `reports/round-99/`). The two decisive
post-repair receipts (`121018453359Z`, `122858496567Z`) are present but
untracked worktree data. None of these local receipts is committed or
remotely available, and this report does not imply otherwise. Additionally,
the pre-repair receipt `121018453359Z` carries no source hash, so its
measured-LAN-control leg cannot be attributed to pre- vs post-repair bytes
from the receipt alone (the safety report and LOG entry supply the
attribution narratively).

## What the evidence supports

- **Default-off LAN control: verified** at three independent levels (pinned
  source; committed AST regression executed by me on pinned bytes; the
  default-safe family receipt showing measured:false + blocked + no
  arm_tx_packets). The confinement leg (`e_lan`) is green in both receipts
  and unchanged by the repair.
- **Structure**: 37 leg-dictionary keys = 4 tone setup records
  (sink/source/e2e/axis, `:51719/:52029/:52305/:52672`) + 33 non-tone cells
  (census 3, sink 7, source 6, refusal 8, e2e 5, axis 4) — matches the
  assignment count, confirmed both from the pinned source's `legs[...]`
  assignments and from both receipts (3/8/7/8/6/5 per entry).
- **e_native is explicitly unmeasured, not green**: both receipts carry the
  e_native coverage block with both sides' measurements (sink wire peak
  exactly 0.499969482 at 204 B; source recorded peak 0.0, `rtp.ssrc` "0",
  one sync line) — matching the author report's honest block.
- **Refusal lattice measured as claimed**: receipts show core_exit_code
  234 (x_destip/x_f32/x_media/x_srcport0) and −8 (x_ptime_pair, the SIGFPE
  class); the lattice legs are fail-visible (a surviving core or a missing
  node appends a failure).
- **Propagation is fail-visible in the measured paths**: missing tap
  receipts, absent nodes, missing props, and cli-None in s_two/e_relink/e_sap
  all append failures rather than passing; `_rtp_r99_run` never raises
  (spawn_error records); `_jack_r95_graph` is bounded (timeout 20, error
  dict). Self-containment: the r99 family's cross-family helpers
  (`_jack_r95_graph`, `_playback_r78_foreign_clients`, `_jack_r95_settings`,
  `_alsapw_r84_loadavg`, `_alsapw_r84_killpg`, `_playback_r78_node_names`,
  `_capture_r77_sink_names_strict`, `_pwprof_r89_*`) all exist in the same
  pinned file; the fixture `r99rtp.py` is fully self-contained (own codec,
  tone, WAV reader, Goertzel; no third-party RTP tool).
- **Configuration precedence**: the only config input to the safety posture
  is the environment variable, exact-matched; no config file or CLI flag can
  enable the LAN arm; children inherit the env but nothing but the gate reads
  it.

## Residual risks and checks not run

- I did **not** run the family (verifier-only per the assignment); the
  default-safe receipt is the lead's run, inspected read-only. My one
  execution was the AST guard regression on pinned bytes in scratch.
- The pre-repair receipt's byte provenance (121018453359Z) is unverifiable
  from the receipt alone (no source hash recorded) — F7.
- The `armed_below_band` confinement form bounds only leaks large enough to
  exceed the idle band (the author discloses the 6599–8505 pkt/20 s band and
  the counter's resolution limit; the inline comment "needs no band guard" is
  correct for noise direction but the small-leak limit lives only in the
  note/author report).
- `c_docs`' man-page regexes (`min-ptime[^.]*default 2`) are format-fragile —
  fail-visible (a format change turns the leg red), not fail-open.
- The family is host-specific (`pacman`, `/usr/lib/pipewire-0.3`, `ss`,
  `pw-*`); every missing dependency names a block (census required-tools
  check `:51551-51556`), so portability gaps are honest, but I did not
  execute any entry to observe those blocks.
- Untested hypotheses (inferred, not executed): F1's no-default-iface
  receipt shape; F2's transient pw-cli failure; F3's mid-window counter
  read failure.
- I did not audit `r99-scribe.md` or the r100 integration note (other seats'
  scope); existence noted for attribution only.

## Artifact paths and attribution

- This report: `reports/round-99/r99-reviewer.md` (my only repo write).
- Scratch (pinned-byte copies + my test run):
  `/home/vgpnk/Projects/shokunin/audio-waveb-resume/r99-reviewer/`
  (`measure_audio.py`, `test_rtp_r99_lan_control.py` — both `git show PIN:`
  outputs; no `__pycache__`, no other writes).
- Evidence inspected read-only: the two run receipts under
  `corpus/live/runs/*-rtp-r99/` (worktree-only, untracked),
  `corpus/live/r99-boundary/` (tracked at the pin),
  `reports/round-99/{scout,boundary,author,network-safety}.md`, `LOG.md`
  (ROUND 99 SAFETY entry), `/home/vgpnk/Projects/shokunin/r99-network-safety-proof/`
  (before-red/after-green chain; `source-after.sha256` = pinned hash
  `801e153b…`).
- Prior-receipt attribution: `121018453359Z` = pre-repair disclosed LAN
  egress (measured control); `122858496567Z` = default-safe pass (blocked
  control). The author's own green receipts are absent from this checkout
  (F7) and are not implied committed or remote anywhere above.

Advisory only: this is a reviewer seat's recommendation, not a round
admission or a canonical judge verdict.
