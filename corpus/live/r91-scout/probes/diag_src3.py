#!/usr/bin/env python3
"""r91 scout diagnostic 3: freeze-vs-zeros discriminator on remap-source loss.

Variants:
  A: no node.name, default format, -n 1000000   (this seat's F1s shape minus name)
  B: no node.name, explicit --rate/--channels/--format, -n 288000 (r85 s3 recleg shape)
  C: node.name set, explicit rate flags          (this seat's F1s shape)
Each: NS1 + pw-play tone + remap-source; unload src at t=1.5 s; sample 3 s.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from driver import (sh, pw_dump, nodes_by_prefix, links_raw, relevant_links,
                    load_null_sink, load_remap_source, unload_verified, node_state,
                    ensure_tone_wav, TONE_NS1_ARGV, TONE_WAV, TMP)

NS = "r91s_diag_ns"
SRC = "r91s_diag_src"


def variant(name, argv_extra, use_name):
    ns = load_null_sink(NS)
    tone = subprocess.Popen(TONE_NS1_ARGV, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(1.2)
    src = load_remap_source(SRC, NS)
    time.sleep(1.2)
    out = os.path.join(TMP, f"diag3_{name}.wav")
    recname = f"r91s_diag3_{name}"
    argv = ["pw-record"]
    if use_name:
        argv += ["-P", "node.name=" + recname]
    argv += argv_extra + ["--target", SRC, out]
    rec = subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                           start_new_session=True)
    t0 = time.time()
    acted = False
    rows = []
    while time.time() - t0 < 4.5:
        el = time.time() - t0
        if not acted and el >= 1.5:
            unload_verified(src["idx"], SRC)
            acted = True
        st = node_state(recname if use_name else "pw-record")
        sz = os.path.getsize(out) if os.path.exists(out) else None
        rows.append({"t": round(el, 2), "sz": sz, "state": (st or {}).get("state")})
        time.sleep(0.15)
    try:
        os.killpg(os.getpgid(rec.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    rec.wait(timeout=5)
    try:
        os.killpg(os.getpgid(tone.pid), signal.SIGKILL)
    except ProcessLookupError:
        pass
    tone.wait(timeout=5)
    unload_verified(src["idx"], SRC)
    unload_verified(ns["idx"], NS)
    if os.path.exists(out):
        os.unlink(out)
    return rows


def main():
    ensure_tone_wav(TONE_WAV)
    print("=== A: no node.name, default format, -n 1000000")
    for r in variant("A", ["-n", "1000000"], False):
        print("  ", r)
    print("=== B: no node.name, explicit rate flags, -n 288000")
    for r in variant("B", ["--rate", "48000", "--channels", "2", "--format", "s16", "-n", "288000"], False):
        print("  ", r)
    print("=== C: node.name, explicit rate flags, -n 288000")
    for r in variant("C", ["--rate", "48000", "--channels", "2", "--format", "s16", "-n", "288000"], True):
        print("  ", r)


if __name__ == "__main__":
    main()
