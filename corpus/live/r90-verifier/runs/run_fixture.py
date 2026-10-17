#!/usr/bin/env python3
"""Verifier-owned launcher for the frozen-tree fixture.

Resets SIGHUP/SIGINT/SIGQUIT to SIG_DFL before exec so a background/nohup
launch tree cannot hand the fixture an inherited SIG_IGN disposition (the
r89 `g_hup` class). Usage:

    python3 run_fixture.py python3 corpus/fixtures/measure_audio.py --probe-...
"""
import os
import signal
import sys

for _sig in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT):
    try:
        signal.signal(_sig, signal.SIG_DFL)
    except (OSError, ValueError):
        pass
os.execvp(sys.argv[1], sys.argv[1:])
