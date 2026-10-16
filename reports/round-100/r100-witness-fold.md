# r100 Witness And Setup-Unwind Repair

Source before sha:
`5646861d7c2c914162fea5acd1f5d68a6ff76378acb196dfad73a84e0b9ff86c`.
Source after sha:
`a8760b120fbbb47d091f6d0a674e3630d4fd20b9ee6e366df0f6c57371a019f9`.

The lead reads the complete critic/reviewer reports and the actual frozen
clock variants. The valid witness is clock_mid.settings: its values are
strings, and all declared default.clock.* props map to those live keys by
removing default. The pw-cli-derived server_clock.quantum='4' is a parser
artifact; driver cycle-rate/quantum fields are null. Neither is substituted
for the settings witness or claimed as an observed cycle period.

## Source Changes

- Each requested clock property now requires its matching live settings
  value. This arms the existing witness; no requested values or ILD bands
  change.
- Missing module_unload_verified evidence now fails rather than silently
  skipping verification.
- Clock teardown/census runs from finally, with scratch removal protected
  even when that census raises.
- Missing/unreadable WirePlumber logs produce an unknown count plus named
  errors, not an initial -1 that one later ALSA line can cancel to zero.
- A late setup exception stops/reaps already registered sandbox children
  before re-raising. The Popen identities, not argv/root substrings,
  identify those children.

## Targeted Regression

corpus/fixtures/test_sofa_r100_witnesses.py runs actual AST-isolated
functions. Before: eight tests with sixteen failures including subtests.
After: all eight pass. Positive matching-clock and verified-unload
controls remain passing. Every declared requested property has both
missing and wrong-value negative controls. Source/test compile checks pass.

The startup test creates one inert, owned Python child in its own session,
forces the later WP-log open to fail, and verifies actual termination,
reaping and log closure. Its finally cleans that child on the old red
implementation too. It launches no PipeWire, audio, network or service.
Other capture/ILD witnesses in this unit are explicitly inert; this is
not a native HRTF measurement or complete law-set verification.

Raw commands, stdout/stderr/rc, source copies and complete source diff:
`/home/vgpnk/Projects/shokunin/audio-r100-witness-proof/`.

## Limits

No live clock measurement accompanies this source commit; a single
changed-entry observation follows separately. No full nine-entry replay
is needed to re-prove unchanged captures. Universal receipt-on-exception
containment, uncatchable/external termination, no-config/IR-latency gaps,
record-only shared-store writes, narrow clock-band margin and historical
author-receipt custody remain separately disclosed findings. No clean
unattended-family certification or native UFO verdict is asserted.

## Subsequent Changed-Entry Observation

One immutable export of 294e6c24 (source sha matches the after sha above)
runs only sofa_clock_r100_entry under the real host-global family lock.
The raw result is r100-clock-repair-receipt.json in this directory.
Execution: env -u RTP_R99_ALLOW_LAN_CONTROL python3 -B runner.py
under audio-r100-witness-proof/targeted-clock/; rc 0.

All three variants have the requested live settings: quantum 512 plus
max-quantum 2048, quantum 2048, rate 96000 plus allowed-rates [ 96000 ].
The entry has no failures or coverage blocks. All six retained core/WP
handles exit rc 0. The readable WP logs have zero ALSA lines, with no
log-reader errors. This is a scoped author observation, not a repeat of
the nine-entry family or independent verification of all repaired bytes.
