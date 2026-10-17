#!/usr/bin/env python3
"""R77 scout — FRONTIER 1b: does `-P stream.capture.sink=true` silently
override `--target`?

Discriminators (three independent witnesses):
  W1 content identity — capture the same 0.1 s from four different named
     targets WITH the prop; if all four byte-identical, the target name
     was not honored.
  W2 link topology — hold a capture open with the prop and ask pw-link
     which ports it is actually attached to (the capture stream's own
     ports vs the node it consumes).
  W3 stream props — pw-dump the live capture stream and read its
     target.object / node.target / media.class props.
"""
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r77_probe import (LINE, MIC, M_SPDIF, M_SPK, S_SPDIF, emit,  # noqa: E402
                       mk, sh)

TMP = mk()
N = "4800"


def nonzero_frac(data):
    if not data:
        return None
    nz = sum(1 for b in data if b)
    return round(nz / len(data), 4)


def cap(target, prop=True, extra=None, n=N):
    slug = (target or "AUTO")[:24].replace("/", "_").replace(".", "_")
    p = os.path.join(TMP, f"d_{slug}_{prop}_{n}.wav")
    argv = ["pw-record"]
    if prop:
        argv += ["-P", "stream.capture.sink=true"]
    if target is not None:
        argv += ["--target", target]
    argv += ["-n", n] + (extra or []) + [p]
    r = subprocess.run(argv, capture_output=True, timeout=20)
    d = open(p, "rb").read() if os.path.exists(p) else b""
    return {"argv": [a if not a.startswith(TMP) else "<out>" for a in argv],
            "rc": r.returncode, "bytes": len(d),
            "payload_sha": hashlib.sha256(d[44:]).hexdigest()[:16],
            "nonzero_frac": nonzero_frac(d[44:]),
            "err": r.stderr.decode(errors="replace").strip()[:150]}


def main():
    out = {"probe": "target-override-r77", "tmp": TMP, "W1": {}, "W2": {},
           "W3": {}}

    # W1: content identity across named targets, with and without prop
    for prop in (True, False):
        for tgt in (LINE, MIC, M_SPDIF, M_SPK, S_SPDIF, "default", None):
            key = f"prop={prop}|target={tgt}"
            out["W1"][key] = cap(tgt, prop=prop)

    # W2: link topology during a held capture
    for label, argv in [
        ("monprop_target_MIC", ["pw-record", "-P",
                                "stream.capture.sink=true", "--target", MIC]),
        ("monprop_target_MONITOR_SPDIF", ["pw-record", "-P",
                                          "stream.capture.sink=true",
                                          "--target", M_SPDIF]),
        ("direct_target_MIC", ["pw-record", "--target", MIC]),
    ]:
        p = os.path.join(TMP, f"w2_{label}.wav")
        proc = subprocess.Popen(argv + [p], stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(1.2)
        rc, so, se, _w, _t = sh(["pw-link", "-l"], timeout=10)
        lines = so.decode(errors="replace").splitlines()
        # keep only the block containing a pw-record consumer port
        keep, hit = [], False
        for ln in lines:
            if "pw-record" in ln:
                hit = True
                keep.append(ln)
            elif ln.startswith("|") or ln.startswith("  "):
                if hit:
                    keep.append(ln)
            elif hit:
                keep.append(ln)
                if ln.strip() == "":
                    hit = False
        rc2, so2, _se2, _w2, _t2 = sh(["pw-dump"], timeout=20)
        props = []
        try:
            for o in json.loads(so2):
                pp = o.get("info", {}).get("props", {})
                if pp.get("application.name") == "pw-record" or \
                        "pw-record" in str(pp.get("node.name", "")):
                    props.append({k: v for k, v in pp.items()
                                  if k in ("node.name", "media.class",
                                           "target.object", "node.target",
                                           "stream.capture.sink",
                                           "application.name",
                                           "object.serial")})
        except Exception as exc:                               # noqa: BLE001
            props = [f"parse: {exc}"]
        out["W2"][label] = {"pwlink_lines": keep[:20], "stream_props": props}
        proc.send_signal(2)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)
        # W3: what did it leave on disk
        d = open(p, "rb").read() if os.path.exists(p) else b""
        out["W3"][label] = {"bytes": len(d),
                            "payload_sha": hashlib.sha256(d[44:]).hexdigest()[:16]
                            if len(d) > 44 else None,
                            "rc": proc.returncode}

    emit(out, "probe-target-override-r77.json")
    print(out["probe"])


if __name__ == "__main__":
    main()
