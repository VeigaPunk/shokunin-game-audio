#!/usr/bin/env python3
"""r70-critic counterexample probes against the landed (uncommitted) diff.

Imports fifo_hold_leg/transport_entry straight from the modified
corpus/fixtures/measure_audio.py. Writes nothing to the repo: fifos live in
tempfile dirs; transport_entry is read-only w.r.t. the tree.

Usage:
  python3 probe.py conj      # one oneshot leg at hold=12s > arm_timeout=10s
                             # (writer provably attached at open #2, yet the
                             # recorded signature is the 'blocked' cell)
  python3 probe.py cell H F N  # N reps of fifo_hold_leg(H, F)
"""
import json
import sys
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
sys.path.insert(0, str(ROOT / "corpus" / "fixtures"))
import measure_audio as m  # noqa: E402

MEMBER = ROOT / "corpus" / "live" / "round-66" / "pair_dec_act.wav"


def main():
    mode = sys.argv[1]
    if mode == "conj":
        leg = m.fifo_hold_leg(MEMBER, 12.0, "oneshot")
        # writer attached until ~12s after reader-1 attach; open #2 lands at
        # ~30-130ms -> attached-at-open-#2 is guaranteed by construction.
        print(json.dumps(leg, indent=1))
        print("PREDICT: error='blocked: no verdict within 10 s', exit_code=None")
        print("YET verdict_emitted holds the au-magic FAIL text and the writer")
        print("was attached at open #2 -> outcome is NOT binary on attachment.")
        return
    if mode == "cell":
        hold, feed, n = float(sys.argv[2]), sys.argv[3], int(sys.argv[4])
        for i in range(n):
            leg = m.fifo_hold_leg(MEMBER, hold, feed)
            print(f"h={hold} {feed} rep{i}: exit={leg['exit_code']} "
                  f"err={leg['error']!r} wall={leg['wall_s']} "
                  f"emitted={leg['verdict_emitted']!r}", flush=True)
        return
    raise SystemExit(f"bad mode {mode}")


if __name__ == "__main__":
    main()
