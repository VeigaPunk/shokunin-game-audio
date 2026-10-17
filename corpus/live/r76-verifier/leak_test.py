#!/usr/bin/env python3
"""r76 verifier — leak probe: does the arm's pw-record primitive leave a
live PipeWire node behind?  Read-only w.r.t. tracked files; scratch only."""
import subprocess
import sys
import time
from pathlib import Path

TMP = Path("/tmp/r76-verifier-leak")
TMP.mkdir(exist_ok=True)


def pwrecord_nodes():
    p = subprocess.run(["pw-link", "-o"], capture_output=True, timeout=10)
    return [ln.strip() for ln in p.stdout.decode().splitlines()
            if "pw-record" in ln]


def all_ports():
    p = subprocess.run(["pw-link", "-o"], capture_output=True, timeout=10)
    return p.stdout.decode().splitlines()


def ps_pwrecord():
    p = subprocess.run(["pgrep", "-a", "pw-record"], capture_output=True)
    return p.stdout.decode().strip()


def probe(label, argv, timeout_s=15):
    print(f"--- {label}")
    print("  before: nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout_s)
        rc, err = proc.returncode, None
    except subprocess.TimeoutExpired:
        rc, err = None, "TIMEOUT"
    # the primitive's own settle
    time.sleep(0.5)
    print("  after : rc=%s err=%s nodes=%s procs=%r"
          % (rc, err, pwrecord_nodes(), ps_pwrecord()))
    time.sleep(2.0)
    print("  +2s   : nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))


if __name__ == "__main__":
    print("baseline ports=%d nodes=%s"
          % (len(all_ports()), pwrecord_nodes()))
    print("baseline procs=%r" % ps_pwrecord())

    # (a) the bounded-entry primitive: -n exact, subprocess.run timeout
    probe("bounded -n 4800 (0.1 s)",
          ["pw-record", "--target", "@DEFAULT_SOURCE@", "-n", "4800",
           "--rate", "48000", "--channels", "2", "--format", "s16",
           str(TMP / "a.wav")])

    # (b) the sever primitive: SIGTERM mid-record
    print("--- sever TERM (2.5 s then SIGTERM)")
    print("  before: nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))
    pr = subprocess.Popen(
        ["pw-record", "--target", "@DEFAULT_SOURCE@", "--rate", "48000",
         "--channels", "2", "--format", "s16", str(TMP / "b.wav")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    time.sleep(2.5)
    pr.send_signal(15)
    try:
        pr.wait(timeout=5.0)
    except subprocess.TimeoutExpired:
        print("  TERM did not land within 5 s")
    time.sleep(0.5)
    print("  after TERM rc=%s nodes=%s procs=%r"
          % (pr.returncode, pwrecord_nodes(), ps_pwrecord()))

    # (c) the roundtrip primitive: -n 240000 (5 s), wait for natural exit
    print("--- roundtrip -n 240000 (5 s)")
    print("  before: nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))
    pr2 = subprocess.Popen(
        ["pw-record", "-P", "stream.capture.sink=true", "--target",
         "alsa_output.usb-Generic_USB_Audio-00.HiFi__SPDIF__sink",
         "-n", "240000", "--rate", "48000", "--channels", "2",
         "--format", "s16", str(TMP / "c.wav")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        start_new_session=True)
    t0 = time.monotonic()
    try:
        pr2.wait(timeout=30)
        print("  exited rc=%s after %.2f s" % (pr2.returncode,
                                               time.monotonic() - t0))
    except subprocess.TimeoutExpired:
        print("  did NOT exit in 30 s")
    time.sleep(0.5)
    print("  after : nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))

    # (d) the sysdefault-style block: arecord that may hang
    print("--- arecord -D sysdefault -d 1")
    print("  before: nodes=%s procs=%r" % (pwrecord_nodes(),
                                           ps_pwrecord()))
    probe("arecord -D sysdefault -d 1",
          ["arecord", "-D", "sysdefault", "-d", "1", "-f", "S16_LE",
           "-r", "48000", "-c", "2", "-t", "wav", str(TMP / "d.wav")])

    print("FINAL ports=%d nodes=%s procs=%r"
          % (len(all_ports()), pwrecord_nodes(), ps_pwrecord()))
    sys.exit(0)
