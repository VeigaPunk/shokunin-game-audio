# r99 Native Pair And Confinement-Branch Repair

Successor source sha:
`5646861d7c2c914162fea5acd1f5d68a6ff76378acb196dfad73a84e0b9ff86c`.
Previous source sha:
`f753f9a9695d47c0d892833f5347c78fb536e3622d99ccd0f965b24735e8f254`.

The native fragment now explicitly gives the source RTP_R99_PORT, the
same destination port used by its sink. The helper's +1 default is
unchanged because standalone packet-injection legs need it. The frozen
verifier receipt directly records the earlier mismatch (46814/46815).
The former host-state explanation for its silence is withdrawn; a
miswired fixture cannot establish that explanation. Runtime reception
after the repair is not inferred from the arg-string test.

The e_lan noisy-window abstention now applies only to positive excess
within the already-existing 20%-of-emitted allowance. Greater excess
must reach the existing failure assertion even with a wide idle band.
No numerical threshold changes. The <=0 and exactly-at-allowance
controls retain their prior outcomes. NIC counters remain a sampled
coarse proxy under background variance, not universal isolation proof.

## Targeted Regression

The lead authors the exact test and source decisions before editing.
corpus/fixtures/test_rtp_r99_loopback.py extracts actual arg builders,
the actual native fragment calls, actual allowance assignment and
actual leak branch. It performs no network or audio operation.

Before: three tests, two failures: native ports differ; a 4001-packet
excess in a 9000-packet idle band wrongly abstains. After: all three
pass. The standalone +1 source-port control and all five synthetic
leak cases hold. The existing two default-off LAN-control tests also
pass. Source and new test compile checks pass; authored/durable test
bytes match.

Raw before/after commands and captures, source copies and exact diff:
`/home/vgpnk/Projects/shokunin/audio-rtp-loopback-proof/`.

The physical-LAN control remains default-off; it is not enabled for
these tests or to force a runtime result. Historical controls remain
historical evidence, not proof of the successor's default behavior.
No full-family or new native receive measurement accompanies this
commit; a later scoped e2e observation will be reported separately.
