#!/usr/bin/env python3
"""Run a probe with os.getpid() % 4 pinned to a chosen residue.

Why: `PLAYBACK_R78_TONE_L_HZ = 997.0 + (os.getpid() % 4) * 211.0` makes the
tag tone's frequency (and every tone-derived receipt leaf: window f_l/f_r,
a_l/a_r, at_l/at_r, the mix/stereo bands) a function of the probe process's
pid residue. A control-vs-candidate pair with different residues cannot be
compared leaf-for-leaf on those leaves. This driver forks until a child
lands on the requested residue, then execs the probe from that child; the
probe's own `os.getpid()` is the child's pid, so both sides of a pair can be
run at the SAME residue. Only the residue is pinned; everything else (pid
value, names, timing) is untouched and normalized by the comparator.

Usage: pidpin.py <residue> <python-exe> <probe.py> [args...]
Exit: the probe's own exit status, or 3 if no residue landed in 512 forks.
"""
import os
import sys

WRONG = 97


def main():
    residue = int(sys.argv[1])
    argv = sys.argv[2:]
    for _ in range(512):
        pid = os.fork()
        if pid == 0:
            if os.getpid() % 4 == residue:
                os.execvp(argv[0], argv)
            os._exit(WRONG)
        _, status = os.waitpid(pid, 0)
        if os.WIFEXITED(status) and os.WEXITSTATUS(status) == WRONG:
            continue
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        return 1
    sys.stderr.write("pidpin: no residue %d in 512 forks\n" % residue)
    return 3


if __name__ == "__main__":
    sys.exit(main())
