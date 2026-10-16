#!/usr/bin/env python3
"""Reset launcher-inherited signal dispositions, then exec argv.

Why: bash's asynchronous (background) command handling and nohup(1) set
SIGHUP/SIGINT/SIGQUIT to SIG_IGN, and exec() PRESERVES SIG_IGN. The fixture
spawns pw-profiler via subprocess.Popen, so under such a launcher the
unhandled-signal legs (g_hup) inherit SIG_IGN and a delivered SIGHUP is
discarded — the leg then measures rc -9 at the harness bound instead of the
host's default-terminate rc -1. This wrapper restores SIG_DFL so the replay
measures the landing, not the launcher. Verifier-owned; never tracked.
"""
import os
import signal
import sys

for _s in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT):
    try:
        signal.signal(_s, signal.SIG_DFL)
    except (OSError, ValueError):
        pass
os.execvp(sys.argv[1], sys.argv[1:])
