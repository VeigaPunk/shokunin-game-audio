# R98 Scope Fold - Data Walk And Gates

Status: implemented; scoped software and native evidence below. Not a
full-family re-verification or round-admission claim.
Before: dadfa684, measure_audio.py sha
0a614a9c87c1cdcba3cf85f707aa2ea8aab369f50fa877391acc83b648743b1f.

## Data Walk

C line 755 creates r98a_<name-or-mode>; memset initializes name to NULL.
Python's run helper passes arguments unchanged, while six live-snapshot
callers and the direct xw profiler expect bare r98a_<tag> names.
The PID-scoped namespace constant is NOT connected to these arguments.
Therefore the selector-only fold cannot establish PID-scoped C streams.
The common live snapshot also ignores its probe env, querying the shared
graph even if the probe is connected to a private core.

The C fixture itself remains unchanged (9f840a6b...d323). The private
sandbox explicitly disables hardware.audio, hardware.bluetooth and
hardware.video-capture and redirects runtime/config/state/data. No new
physical-LAN control or full family run is required for this change.

## Milestones

- M1: actual production-run constructor with inert Popen captures argv
  and graph-call env. Named/default/peer-PID tags must be scoped, retry
  input must remain idempotent, and live witnesses must use probe env.
  Active callers must construct their node_name via the same authority.
- M2: minimal Python-only argument/name helpers, common-run binding,
  six snapshot caller updates, direct xw args/profiler binding and
  optional env forwarding on the graph reader. Gate: M1 tests green.
- M3: one short emit leg in a freshly owned, hardware-disabled private
  core. Observe the actual PID-scoped node and its link to the owned
  null sink, then owned process exits and socket removal. Preserve
  source/hash/command/receipt; no numerical-law or full-family claim.

Out of scope: new DSP laws, band tuning, physical LAN, broad reruns,
the separate graph-reader empty-output hardening and dispatch-exception
receipt-custody defects. Those findings are not closed by this plan.

## Results

M1 produced five failing subcases in three tests before the source edit:
three argv cases, the live environment, and active-caller name authority.
The same three tests pass afterward. The inert constructors execute the
production helpers, preserve caller inputs and prove retry idempotency;
they do not execute an actor or score audio. Compile and diff checks pass.
Before/after logs: audio-final-guard-proof/r98-scope-{before,after}.*.

M2 connects both common and direct-xw argv construction to PID-tagged
name arguments, six snapshot callers and the xw profiler to the same
name authority, and the common snapshot to the actual probe environment.
The C fixture and DSP parameters/thresholds are unchanged.

M3 first stopped BEFORE emitting: the proof directory made the private
manager socket path 111 bytes plus NUL, beyond the native 108-byte limit
(rc 220, ENAMETOOLONG). That failed setup and log remain in
audio-final-guard-proof/r98-scope-native-ntlflagm/.
Only the proof's runtime location was shortened to /tmp; no production
grader, DSP law or threshold was changed.

The corrected single private emit observation records:
- Source sha 72b23e043447557a9c3560e0633cac1fb7d94c964fe9b24f6b4439b7b5dc0007;
  C source 9f840a6b8b23196124270d96532b3b35b2b868d089aef4eb58ad2d6b0950d323.
- Actual argv name=1493099_scope_probe and node
  r98a_1493099_scope_probe, rc 0, state streaming, one active link to the
  owned r98a_ns_1493099 sink (serial 30), observed in the private graph.
- Before/after emit inventory contains only Dummy-Driver,
  Freewheel-Driver and the owned null sink; the emit node is gone afterward.
- WirePlumber 1493118 and core 1493112 both exit rc 0; socket disappearance
  is checked BEFORE removing the newly created short runtime directory.
- Hardware audio/Bluetooth/video-capture profiles are disabled in the
  captured private config. No operator service restart or physical LAN arm.

Byte-identical observation: reports/round-98/r98-scope-observation.json,
sha256 9f76df21a164f54d89d042bcaf832edde35d8c5decec5813e8e0bf76c4e6fd07.
Original commands, source copy, build and private logs:
audio-final-guard-proof/probe_r98_scope.py and
audio-final-guard-proof/r98-scope-native-1q7_ys28/.
This proves one producer/witness/cleanup path, not all 67 historical legs.
