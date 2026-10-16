# r97 Narrow Signal-Ownership Repair

This successor repairs the required signal guard, not the whole r97 fold.
The historical author/reviewer/verifier receipts keep their original scope.

Before source sha:
`801e153b84368bba4a77e85c129376612c797694c435e9104cdad6e62169be2f`.
After source sha:
`6401edd7ff68aa934d82d42df18296f26e6e011db63cda830c2c146871b5c0fb`.

The source now retains the actual Popen objects created by the private
spawn helper, with exact owning-root identities. All three callers
explicitly pass that root. An argv/environment substring no longer
authorizes a signal. A missing root is rejected before spawn.
Teardown waits and reaps its registered direct children instead of
calling kill(pid, 0) repeatedly on unreaped zombies.

The lead authors the exact source bodies and regression before the
helper applies them. Lead review verifies all three function ASTs match
the contract, the durable test is byte-identical to its authored block,
and the current source equals the frozen after-copy.

## Regression Evidence

`corpus/fixtures/test_wppol_r97_guard.py` runs the actual helpers in an
AST-isolated namespace. It creates only its own short-lived test
children; it performs no audio, network or service operation.

Before: six tests, four failures (foreign argv mention, foreign
environment mention, missing root and the owned child's falsely
reported KILL). After: all six pass; owned child exits with SIGTERM
and is reaped; foreign/root-mismatched processes survive; invalid and
unregistered ids are refused. Source/test compile checks pass.

Raw commands, source-before/source-after, source-only diff and original
test stdout/stderr/rc are retained at:
`/home/vgpnk/Projects/shokunin/r97-guard-proof/`.

## Limits

The exit census is now explicitly scoped to registered live direct
children, recorded as own_process_census_scope. It does not certify
arbitrary descendant discovery or historical unregistered processes.
The regression does not claim an experimentally proven PID-reuse attack.

No new live r97 family run accompanies this commit. The shared-runtime,
unarmed hash, error-class, timing-label, duplicate-observation and lock
findings in r97-adjudicator.md remain open unless separately repaired
and evidenced. Do not infer clean isolation or full unattended-family
certification from this narrow guard test.
