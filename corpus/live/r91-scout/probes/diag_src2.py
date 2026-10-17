#!/usr/bin/env python3
"""r91 scout diagnostic 2: does a pw-play tone into a seat null-sink run, and
does the remap-source chain carry it?  (Bounded; explicit teardown.)"""
import json, os, signal, subprocess, sys, time, wave, struct, math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import (sh, pw_dump, nodes_by_prefix, links_raw, relevant_links,
                    load_null_sink, load_remap_source, unload_verified, node_info)

NS = "r91s_diag_ns"
SRC = "r91s_diag_src"
REC = "r91s_diag_rec"
TONE = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-scout/tmp/r91s_tone.wav"


def make_tone(path, secs=20, rate=48000, freq=997, amp=8000):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(rate)
        n = int(secs * rate)
        frames = bytearray()
        for i in range(n):
            v = int(amp * math.sin(2 * math.pi * freq * i / rate))
            frames += struct.pack("<hh", v, v)
        w.writeframes(bytes(frames))


def state_of(prefix):
    dump, _ = pw_dump()
    nodes = nodes_by_prefix(dump, prefix)
    if not nodes:
        return None
    props = nodes[0]["props"]
    return {"id": nodes[0]["id"], "state": nodes[0]["state"],
            "driver": props.get("node.driver"), "name": props.get("node.name")}


def main():
    if not os.path.exists(TONE):
        make_tone(TONE)
    ns = load_null_sink(NS)
    print("ns load:", ns["ok"], ns["idx"])
    tone = subprocess.Popen(["pw-play", "-P", "node.name=r91s_diag_tone",
                             "--target", NS, TONE],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(1.5)
    print("tone(pw-play):", json.dumps(state_of("r91s_diag_tone")))
    print("ns:", json.dumps(state_of(NS)))
    # direct tap of NS monitor
    out1 = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-scout/tmp/diag_tap.wav"
    rec1 = subprocess.Popen(["pw-record", "-P", "node.name=r91s_diag_tap", "--target", NS,
                             "-n", "1000000", out1],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(2.0)
    sz = os.path.getsize(out1) if os.path.exists(out1) else None
    print("tap on NS monitor:", json.dumps(state_of("r91s_diag_tap")), "bytes:", sz)
    try:
        os.killpg(os.getpgid(rec1.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    rec1.wait(timeout=5)
    # remap chain
    src = load_remap_source(SRC, NS)
    print("src load:", src["ok"], src["idx"])
    time.sleep(1.5)
    print("src:", json.dumps(state_of(SRC)))
    out2 = "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r91-scout/tmp/diag_rec2.wav"
    rec2 = subprocess.Popen(["pw-record", "-P", "node.name=" + REC, "--target", SRC,
                             "-n", "1000000", out2],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    time.sleep(2.0)
    sz2 = os.path.getsize(out2) if os.path.exists(out2) else None
    print("rec on remap src:", json.dumps(state_of(REC)), "bytes:", sz2)
    try:
        os.killpg(os.getpgid(rec2.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    rec2.wait(timeout=5)
    try:
        os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    tone.wait(timeout=5)
    print("unload src:", unload_verified(src["idx"], SRC))
    print("unload ns:", unload_verified(ns["idx"], NS))
    for f in (out1, out2):
        if os.path.exists(f):
            os.unlink(f)


if __name__ == "__main__":
    main()
