#!/usr/bin/env python3
"""r78 SIMPLIFIER bounded mechanism probe for the `segv_audio` flake.

Hypothesis: the segv entry reuses PLAYBACK_R78_PROP_SINK_A — the very name
the props entry has just loaded and destroyed — and when the server's
duplicate-name rename wins the race, only the input-class leg (which must
resolve a *source* before it can crash) fails with "no target node
available"; the three output-class crash legs crash before resolution and
are unaffected.

Two arms, each in a FRESH process (so the pid-stamped name is fresh):
  arm F ("fresh")  : call playback_class_segv_r78_entry() directly
  arm N ("reused") : load+unload PLAYBACK_R78_PROP_SINK_A first (exactly
                     what the props entry does), then call the segv entry

usage: segv_mechanism.py <fixture.py> F|N
prints one JSON line: arm, segv_audio rc, stderr class, failures
"""
import importlib.util
import json
import sys


def load(path):
    spec = importlib.util.spec_from_file_location("fixture", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    mod = load(sys.argv[1])
    arm = sys.argv[2]
    if arm == "N":
        mid, rc, err = mod._playback_r78_null_sink_load(
            mod.PLAYBACK_R78_PROP_SINK_A)
        unload_rc = mod._playback_r78_unload(mid)
    else:
        mid, rc, err, unload_rc = None, None, None, None
    entry = mod.playback_class_segv_r78_entry()
    leg = entry["legs"]["segv_audio"]
    out = {"arm": arm, "fixture": sys.argv[1], "pid": __import__("os").getpid(),
           "preload": {"module_id": mid, "rc": rc, "error": err,
                       "unload_rc": unload_rc},
           "segv_audio_rc": leg.get("exit_code"),
           "segv_audio_error": leg.get("error"),
           "segv_audio_stderr": (leg.get("stderr_tail") or "")[:90],
           "sibling_rcs": {k: v.get("exit_code")
                           for k, v in entry["legs"].items()
                           if k.startswith("segv_")},
           "failures": entry.get("failures"),
           "sink_gone": entry.get("sink_gone")}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
