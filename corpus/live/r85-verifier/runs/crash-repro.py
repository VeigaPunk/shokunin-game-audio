#!/usr/bin/env python3
"""r85 verifier — offline reproduction of the r85v2 crash mechanism.

My r85v2 replay died mid-aplayenv with:

  TypeError: argument of type 'int' is not a container or iterable
    at _alsapw_r84_cands (measure_audio.py:19140)
  TypeError: '<' not supported between instances of 'int' and 'str'
    at _playback_r78_node_names (measure_audio.py:6153)

Both are triggered by one host condition: a live node whose `node.name`
property is not a string. This script proves the mechanism with a
crafted pw-dump (monkeypatched `subprocess.run`) — no live PipeWire
object, no host mutation — and shows the all-string control path is
clean. The same condition was live on the shared host during r85v2
(foreign node, gone at the next census); no such node existed during
r85v1 or the author's runs.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

PIN = sys.argv[1] if len(sys.argv) > 1 else \
    "corpus/live/r85-verifier/tree/corpus/fixtures/measure_audio.py"
SRC = Path(PIN)


def load_module(path):
    spec = importlib.util.spec_from_file_location("ma_pin", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fake_dump(node_names):
    dump = [{"id": 100 + i, "type": "PipeWire:Interface:Node",
             "info": {"props": {"node.name": nm}}} for i, nm in
            enumerate(node_names)]
    return json.dumps(dump).encode()


def main():
    ma = load_module(SRC)
    orig_run = subprocess.run
    results = {}

    def with_dump(node_names, fn):
        payload = fake_dump(node_names)

        class R:
            stdout = payload
            returncode = 0
            stderr = b""

        def fake_run(argv, *a, **k):
            if argv and argv[0] == "pw-dump":
                return R()
            return orig_run(argv, *a, **k)
        subprocess.run = fake_run
        try:
            return fn()
        finally:
            subprocess.run = orig_run

    # control — all names are strings
    names = with_dump(["aplay", "r85a_ns_1", "alsa_playback.aplay"],
                      ma._playback_r78_node_names)
    results["node_names_all_str"] = names
    cands = ma._alsapw_r84_cands(
        {"nodes": {1: {"name": "alsa_playback.aplay"}}}, "aplay")
    results["cands_all_str"] = len(cands)

    # the crash condition — one node carries an int node.name
    try:
        with_dump(["aplay", 12345, "r85a_ns_1"],
                  ma._playback_r78_node_names)
        results["node_names_int"] = "no error (UNEXPECTED)"
    except TypeError as exc:
        results["node_names_int"] = f"TypeError: {exc}"
    try:
        ma._alsapw_r84_cands({"nodes": {1: {"name": 12345}}}, "aplay")
        results["cands_int"] = "no error (UNEXPECTED)"
    except TypeError as exc:
        results["cands_int"] = f"TypeError: {exc}"

    print(json.dumps(results, indent=1))
    ok = (isinstance(results["node_names_all_str"], list)
          and results["cands_all_str"] == 1
          and results["node_names_int"].startswith("TypeError")
          and results["cands_int"].startswith("TypeError"))
    print("MECHANISM REPRODUCED" if ok else "REPRODUCTION FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
