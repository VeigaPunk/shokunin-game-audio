#!/usr/bin/env python3
"""CRITIC replay stub for build_artifacts.py (r75 mode).

The r75 mode calls build_artifacts.py with NO probe flags (the fixture's
invocation list has no r75 build clause), i.e. the DEFAULT member build,
which rewrites tracked member artifacts under the repo corpus. The replay
must not write outside corpus/live/r75-critic/, so this stub exits 0
(= build step succeeded, skipped).

Equivalence argument, recorded in the report: the author's own runs DID
execute the real build, and the worktree members are byte-identical to
their tracked blobs afterwards (`git status --porcelain` clean for the
member dirs; `git hash-object` matches the index) — so the default build
is byte-idempotent on this host and skipping it cannot change any
measured byte. Member hashes are recorded in
corpus/live/r75-critic/replay/member-verify.txt.
"""
import sys

sys.exit(0)
