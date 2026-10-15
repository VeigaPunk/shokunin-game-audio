#!/usr/bin/env python3
"""r91b: is the gst freeze a CLOCK_LOST -> pipeline-pause, not a client stall?

Evidence chain so far:
  * gstpipewiresrc.c:906-910 posts GST_MESSAGE_CLOCK_LOST on the
    STREAMING -> PAUSED transition for audio streams.
  * the element's own GST_DEBUG log shows exactly `got stream state paused`
    at the moment the target node is unloaded, and the pipeline then clears
    its state (`gst_bin_change_state_func: clearing EOS elements`).
  * the scout's §4 "client is sticky: link present, node idle, no data" is
    measured with gst-launch, whose bus handler pauses the pipeline on
    CLOCK_LOST and never resumes it.

This probe uses the GStreamer python bindings to observe the bus messages
directly and to answer two questions the scout left `[?]`:

  Q1 (cause): is CLOCK_LOST actually posted on target loss?
  Q2 (consequence): if the app does NOT pause (or re-sets PLAYING after a
      short pause), does the element resume producing once a link exists?

Arms (one process each, bounded):
  OBSERVE   - log every bus message; do nothing else.  Expect CLOCK_LOST,
              then the default handler pauses the pipeline.
  RESUME    - on CLOCK_LOST, ignore it for `hold` seconds, then force
              set_state(PLAYING) and keep running; a manual pw-link to a live
              seat monitor is made while held.  Does the file grow again?
  IGNORE    - drop CLOCK_LOST entirely (handled=True, no default handler).
              Does the element keep producing (keepalive) or stall?

Bounded: wall cap in the loop, byte cap, killpg on the owning process group.
Seat-owned names r91b_*/gst_r91b_* only.
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r91b_probe import (TMP, RUNS, load_null_sink, unload_verified,
                        ensure_tone_wav, TONE_WAV, find_ports, sh, sha)

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst  # noqa: E402

SCRATCH = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-boundary"
BYTE_CAP = 4 * 1024 * 1024

PIPE = ("pipewiresrc client-name={name} target-object={ns} "
        "stream-properties=props,stream.capture.sink=true {extra} ! "
        "audio/x-raw,format=S16LE,rate=48000,channels=2 ! wavenc ! "
        "filesink location={out}")


def nick(v):
    """PyGObject enum nick: MessageType exposes value_nicks (list), State
    exposes value_nick (str).  Handle both."""
    n = getattr(v, "value_nicks", None)
    if n:
        return n[-1]
    return getattr(v, "value_nick", None) or str(v)


def relink(ns2, prefix):
    outs, _ = find_ports("o", ns2)
    ins, _ = find_ports("i", prefix)
    done = []
    for o in outs:
        sfx = o.split(":")[-1]
        if not sfx.startswith("monitor_"):
            continue
        want = "input_" + sfx.split("_", 1)[1]
        for i in ins:
            if i.endswith(":" + want):
                done.append({"out": o, "in": i, "res": sh(["pw-link", o, i])})
                break
    return done


def one(arm, name, ns, extra="", hold=1.5, wall=5.0, relink_to=None):
    Gst.init(None)
    leg_dir = os.path.join(RUNS, arm + "_" + name)
    os.makedirs(leg_dir, exist_ok=True)
    out = os.path.join(TMP, f"{arm}_{name}.wav")
    if os.path.exists(out):
        os.unlink(out)
    ns1 = load_null_sink(ns)
    tone = tone_log = None
    ns2 = None
    if relink_to:
        ns2 = load_null_sink(relink_to)
        ensure_tone_wav(TONE_WAV)
        tone_log = open(os.path.join(leg_dir, "tone.log"), "wb")
        tone = subprocess.Popen(["pw-play", "-P", "node.name=r91b_tone_rl",
                                 "--target", relink_to, TONE_WAV],
                                stdout=tone_log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        time.sleep(1.0)
    prefix = f"gst_r91b_{arm.lower()}"
    desc = PIPE.format(name=prefix, ns=ns, extra=extra, out=out)
    pipe = Gst.parse_launch(desc)
    bus = pipe.get_bus()
    bus.add_signal_watch()
    msgs = []
    st = {"clock_lost": False, "clock_lost_t": None, "forced": None,
          "manual": None, "manual_t": None, "paused_by_default": None}
    t0 = time.monotonic()

    def drain():
        """pop() drains without needing a GLib main loop (signal watch alone
        never fires in this script)."""
        while True:
            m = bus.pop()
            if m is None:
                return
            t = round(time.monotonic() - t0, 3)
            src = m.src
            rec = {"t": t, "type": nick(m.type),
                   "src": src.get_name() if src is not None else None}
            if m.type == Gst.MessageType.CLOCK_LOST:
                st["clock_lost"] = True
                st["clock_lost_t"] = t
                if arm == "IGNORE":
                    rec["handled"] = True
                    msgs.append(rec)
                    continue
                if arm == "RESUME":
                    st["paused_by_default"] = False
                    msgs.append(rec)
                    continue
            if m.type == Gst.MessageType.STATE_CHANGED and src is not None \
                    and src.get_name() == "pipeline0":
                old, new, _ = m.parse_state_changed()
                rec["old"] = nick(old)
                rec["new"] = nick(new)
            if m.type == Gst.MessageType.ERROR:
                rec["err"] = m.parse_error()[0].message
            msgs.append(rec)

    def on_msg(bus_, m):
        pass  # real work happens in drain()

    bus.connect("message", on_msg)
    pipe.set_state(Gst.State.PLAYING)
    timeline = []
    unload = None
    try:
        while True:
            t = time.monotonic() - t0
            drain()
            if t >= 1.2 and unload is None:
                unload = unload_verified(ns1["idx"], ns)
            if relink_to and st["manual"] is None and t >= (st["clock_lost_t"] or 1.2) + 0.3:
                st["manual"] = relink(relink_to, prefix)
                st["manual_t"] = t
            if arm == "RESUME" and st["clock_lost"] and st["forced"] is None \
                    and t >= (st["clock_lost_t"] or 0) + hold:
                ret = pipe.set_state(Gst.State.PLAYING)
                st["forced"] = {"t": round(t, 3), "ret": str(ret)}
            if t >= wall:
                break
            if os.path.exists(out) and os.path.getsize(out) > BYTE_CAP:
                break
            timeline.append({"t": round(t, 2),
                             "bytes": os.path.getsize(out) if os.path.exists(out) else None})
            time.sleep(0.1)
    finally:
        pipe.set_state(Gst.State.NULL)
        time.sleep(0.2)
        drain()
        if tone is not None:
            try:
                os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
            tone.wait(timeout=5)
            tone_log.close()
        if st["manual"]:
            for l in st["manual"]:
                sh(["pw-link", "-d", l["out"], l["in"]])
        if ns2:
            unload_verified(ns2["idx"], relink_to)
        unload_verified(ns1["idx"], ns)
        if os.path.exists(out):
            os.unlink(out)
    sizes = [x["bytes"] for x in timeline if x["bytes"] is not None]
    rec = {"arm": arm, "name": name, "pipe": desc, "unload": unload,
           "clock_lost": st["clock_lost"], "clock_lost_t": st["clock_lost_t"],
           "forced": st["forced"], "manual": st["manual"], "manual_t": st["manual_t"],
           "messages": msgs, "timeline": timeline,
           "first_bytes": sizes[0] if sizes else None,
           "last_bytes": sizes[-1] if sizes else None,
           "grew_after_loss": (sizes[-1] > sizes[0]) if sizes else None}
    with open(os.path.join(leg_dir, "receipt.json"), "w") as f:
        json.dump(rec, f, indent=1, sort_keys=True)
    print(json.dumps({k: rec[k] for k in
                      ("arm", "name", "clock_lost", "clock_lost_t", "forced",
                       "manual_t", "first_bytes", "last_bytes", "grew_after_loss",
                       "unload")}, sort_keys=True))
    print("  msg types:", [m["type"] for m in msgs])
    return rec


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "OBSERVE"
    hold = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    if which == "OBSERVE":
        one("OBSERVE", "baseline", "r91b_ns_obs")
    elif which == "RESUME":
        # hold=999 => never force PLAYING within the wall: relink-only arm
        one("RESUME", "relink", "r91b_ns_res", relink_to="r91b_ns_res2", hold=hold)
    elif which == "IGNORE":
        one("IGNORE", "baseline", "r91b_ns_ign")
    elif which == "CTRL_ALIVE":
        # control: target alive, manual relink to a second live monitor
        one("CTRL_ALIVE", "alive", "r91b_ns_ctl", relink_to="r91b_ns_ctl2", hold=999)
