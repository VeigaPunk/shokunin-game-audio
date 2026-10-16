# r99 Physical-LAN Control Safety Correction

Source commit: `bb177513a615a32d3bc150ecbdcf78302e110d8c`.
Source sha256:
`801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`.

The r99 author integration preserved a positive control that deliberately
sends one six-second synthetic tone onto the physical LAN interface:
multicast group 239.255.42.99, TTL 1. This is not loopback-only.
The integration run `20261016T121018453359Z-rtp-r99` executed that arm
on enp7s0 and recorded 6,034 interface TX packets. The orchestrator
disclosed the missed network effect to the operator.

The correction wraps only that control with the exact opt-in
`RTP_R99_ALLOW_LAN_CONTROL=1`. Without it, the leg has measured:false,
a named blocked reason, and a matching entry-level coverage_blocked
message. The old control's payload, threshold and body are unchanged
inside the guard. The preceding loopback confinement arm is unchanged.

Setting the variable is the technical opt-in mechanism, not permission
for an agent to transmit. Obtain explicit operator approval before
enabling the physical-LAN arm. Do not enable it merely to make a receipt
appear fully measured.

## Regression And Execution Evidence

- The lead-authored AST-isolated branch regression is committed at
  corpus/fixtures/test_rtp_r99_lan_control.py. It executes the actual
  guard body but replaces client opening with a raising barrier.
- Before repair: rc 1, guard absent. After: rc 0, two tests. Absent,
  empty, 0 and true values never reach the client; exact 1 reaches only
  the test barrier. No network operation occurs in these tests.
- Source and test compile checks pass. The retained r90 lock regression
  also passes. These checks do not claim a full historical-suite pass.
- One existing family run with the opt-in explicitly unset returns
  rc 0 and empty stderr on the repaired source. Receipt:
  corpus/live/runs/20261016T122858496567Z-rtp-r99/measurements.json.
  The lead directly checks e_lan_control has measured:false, the blocked
  message is propagated, and no arm_tx_packets record exists. The
  family's failure lists are empty; that does not imply full coverage.

Raw commands, source-only patch, before/after tests and outputs remain
under `/home/vgpnk/Projects/shokunin/r99-network-safety-proof/`.
Local ignored evidence is not silently claimed uploaded by Git.
The prior integration note and author receipts retain their historical
byte scope. Independent final review is separately pending.
