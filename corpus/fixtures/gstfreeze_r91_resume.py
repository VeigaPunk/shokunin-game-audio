#!/usr/bin/env python3
"""r91a fixture — the application that does NOT take the CLOCK_LOST pause.

The r91 boundary measured that `gst-launch-1.0`'s own bus handler re-clocks
on GST_MESSAGE_CLOCK_LOST by forcing PLAYING->PAUSED->PLAYING
(`gst-launch.c:642-646`), that the capture element FAILS the
PAUSED->PLAYING half while no link exists (`error during negotiation`,
`gstpipewiresrc.c:1094`), and that the pipeline then aborts the transition
and the source stays flushing.  This fixture is the positive control for
that mechanism: the SAME element, the SAME target loss, the SAME manual
`pw-link` afterwards — but the app observes the message and never touches
the pipeline state.  If the artifact resumes, the freeze was the launcher,
not the client.

Every mutating host action stays with the caller (the battery owns the
name-verified module unload and the manual link); this process only runs a
pipeline and witnesses it.

Bounded by construction: its own wall clock, an artifact byte cap, a
status file rewritten on every tick (a hard kill still leaves a valid
witness), SIGTERM/SIGINT flush the status and exit, and the pipeline is set
to NULL before exit.  Seat-owned names only (`r91a_*` / `gst_r91a_*`).
"""
import argparse
import json
import os
import signal
import sys
import time


def _nick(value):
    """PyGObject enum nick: MessageType exposes value_nicks (list), State
    exposes value_nick (str).  Handle both."""
    nicks = getattr(value, "value_nicks", None)
    if nicks:
        return nicks[-1]
    return getattr(value, "value_nick", None) or str(value)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--status", required=True)
    ap.add_argument("--client-name", required=True)
    ap.add_argument("--wall", type=float, default=5.5)
    ap.add_argument("--byte-cap", type=int, default=4 * 1024 * 1024)
    ap.add_argument("--interval", type=float, default=0.15)
    a = ap.parse_args()

    import gi
    gi.require_version("Gst", "1.0")
    from gi.repository import Gst

    Gst.init(None)
    desc = ("pipewiresrc client-name=%s target-object=%s "
            "stream-properties=props,stream.capture.sink=true "
            "num-buffers=1000000 ! "
            "audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! "
            "filesink location=%s" % (a.client_name, a.target, a.out))
    pipe = Gst.parse_launch(desc)
    bus = pipe.get_bus()
    bus.add_signal_watch()

    st = {"app": "gstfreeze_r91_resume", "client_name": a.client_name,
          "target": a.target, "out": a.out, "wall_s": a.wall,
          "desc": desc, "clock_lost": False, "clock_lost_t": None,
          "forced": None, "errors": [], "bus_types": [],
          "state_changes": [], "samples": [], "killed": None,
          "exit": None, "rc": None, "first_bytes": None,
          "last_bytes": None}
    t0 = time.monotonic()
    stop = {"flag": False}

    def flush():
        try:
            tmp = a.status + ".tmp"
            with open(tmp, "w") as fh:
                json.dump(st, fh, indent=1, sort_keys=True)
            os.replace(tmp, a.status)
        except OSError:
            pass

    def drain():
        while True:
            m = bus.pop()
            if m is None:
                return
            t = round(time.monotonic() - t0, 3)
            src = m.src
            src_name = src.get_name() if src is not None else None
            st["bus_types"].append({"t": t, "type": _nick(m.type),
                                    "src": src_name})
            if m.type == Gst.MessageType.CLOCK_LOST:
                # Observed, never acted on: no set_state(PAUSED/PLAYING)
                # anywhere in this process after the initial PLAYING.
                st["clock_lost"] = True
                st["clock_lost_t"] = t
            elif m.type == Gst.MessageType.STATE_CHANGED and \
                    src_name == "pipeline0":
                old, new, _ = m.parse_state_changed()
                st["state_changes"].append({"t": t, "old": _nick(old),
                                            "new": _nick(new)})
            elif m.type == Gst.MessageType.ERROR:
                err, _dbg = m.parse_error()
                st["errors"].append({"t": t,
                                     "err": err.message[:240]})

    def on_sig(_signum, _frame):
        stop["flag"] = True

    signal.signal(signal.SIGTERM, on_sig)
    signal.signal(signal.SIGINT, on_sig)

    def size():
        try:
            return os.path.getsize(a.out)
        except OSError:
            return None

    pipe.set_state(Gst.State.PLAYING)
    try:
        while True:
            t = time.monotonic() - t0
            drain()
            b = size()
            st["samples"].append({"t": round(t, 3), "bytes": b})
            if st["first_bytes"] is None and b is not None:
                st["first_bytes"] = b
            if b is not None:
                st["last_bytes"] = b
            flush()
            if stop["flag"]:
                st["exit"] = "signal"
                break
            if t >= a.wall:
                st["exit"] = "wall"
                break
            if b is not None and b > a.byte_cap:
                st["exit"] = "bytecap"
                break
            time.sleep(a.interval)
    finally:
        pipe.set_state(Gst.State.NULL)
        time.sleep(0.15)
        drain()
        st["rc"] = 0
        st["elapsed_s"] = round(time.monotonic() - t0, 3)
        flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
