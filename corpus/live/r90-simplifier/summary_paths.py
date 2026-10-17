#!/usr/bin/env python3
"""Changed-leaf summary for every pair in compare_all's PAIRS table."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import compare_all as CA  # noqa: E402

for a, b, note in CA.PAIRS:
    print(f"\n##### {a} -> {b}   # {note}")
    r = subprocess.run([sys.executable, str(HERE / "diff_paths.py"),
                        CA.RUN[a], CA.RUN[b]], capture_output=True, text=True)
    for ln in r.stdout.splitlines():
        if ln.startswith("==") or ln.startswith("TOTAL") or \
                ln.startswith("   "):
            print(ln)
