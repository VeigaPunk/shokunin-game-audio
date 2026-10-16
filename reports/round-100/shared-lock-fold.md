# Shared Audio Family-Lock Repair

Successor source sha:
`f753f9a9695d47c0d892833f5347c78fb536e3622d99ccd0f965b24735e8f254`.
This follows the r97 guard source at 8332b001.

Fresh pinned verifiers directly observed final families running unlocked:
their minimal exports lacked corpus/live when the old tree-relative
helpers silently returned None. The r98 C probe's non-pid-qualified
names additionally require cross-checkout, not merely same-tree, exclusion.

The eight family helpers for r91/r92/r93/r96/r97/r98/r99/r100 now share
one bounded per-user/per-family host lock, independent of checkout,
XDG_RUNTIME_DIR and TMPDIR. Ownership, regular-file type, link count and
private permissions are checked; symlinks are refused. Waiting never
truncates a holder's text. Real lock files remain persistent; no real
family lock is deleted. r90/r95's existing proven helpers are untouched.

The CLI summary additively displays its existing coverage_blocked map.
Partial-block exit semantics and receipt contents are unchanged. An rc 0
with named blocks remains partial evidence, not complete coverage.

The lead authors helper, wrapper mapping, summary and regression before
delegation, then reviews the complete source diff and raw checks.
Helper AST and copied test bytes are exact to the authored contract;
the current source equals the frozen proof-after copy. Compile checks
and nine tests pass. Tests use only uuid-named own locks, real flock
contention, two synthetic roots/envs, and inert summary data. No audio
family or real production-family lock probe is run for these tests.

Raw proof:
`/home/vgpnk/Projects/shokunin/audio-host-lock-proof/`.
Durable regression: corpus/fixtures/test_audio_host_lock.py.

A lock prerequisite failure is now a named hard refusal before any
family entry starts, not permission to run unlocked. It can exit on
stderr before main writes a receipt; universal exception containment
is a separately disclosed remaining fold. No new full-family execution
accompanies this commit, and other adjudicated findings remain open.
