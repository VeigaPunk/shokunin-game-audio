"""r83 critic probe B — the inherited name-verified unload predicate.

_r83 -> _pwcat_r83_unload_own -> _gst_r81_unload_own -> _gst_r81_sink_module_index.
r82's critic proved the predicate is a substring match (`sink_name=<name>` in
line). r83 re-uses the same helper with pid-suffixed names. This probe loads
two probe-owned null sinks whose names nest (r83c_a, r83c_a2) and asks the
COMMITTED helper which index it would unload for "r83c_a". A returned index of
the r83c_a2 module proves the predicate selects a foreign/sibling module.

Cleans up both modules by index afterwards (verified against pactl).
"""
import importlib.util
import json
import os
import subprocess
import sys

EXPORT = "/tmp/r83critic-src"
spec = importlib.util.spec_from_file_location(
    "ma_r83", os.path.join(EXPORT, "corpus", "fixtures", "measure_audio.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)


def sh(*a):
    p = subprocess.run(list(a), capture_output=True, timeout=15)
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def load(name):
    rc, out, err = sh("pactl", "load-module", "module-null-sink",
                      f"sink_name={name}")
    return {"rc": rc, "index": int(out) if out.isdigit() else None,
            "err": err[:120] or None}


def listed(name):
    rc, out, _ = sh("pactl", "list", "modules", "short")
    hits = [ln for ln in out.splitlines()
            if "module-null-sink" in ln and f"sink_name={name}" in ln]
    return hits


out = {}
a = load("r83c_a")
a2 = load("r83c_a2")
out["loads"] = {"r83c_a": a, "r83c_a2": a2}
out["listed_r83c_a"] = listed("r83c_a")
out["listed_r83c_a2"] = listed("r83c_a2")
idx = ma._gst_r81_sink_module_index("r83c_a")
out["helper_index_for_r83c_a"] = idx
out["helper_picked_r83c_a2"] = (idx is not None and idx == a2.get("index"))
# what the fixture would then do:
res = ma._pwcat_r83_unload_own(a.get("index"), "r83c_a")
out["unload_own_result"] = res
out["a2_still_listed_after"] = listed("r83c_a2")
# cleanup by index (whatever survived)
for nm in ("r83c_a", "r83c_a2"):
    for ln in listed(nm):
        i = ln.split("\t")[0].strip()
        if i.isdigit():
            sh("pactl", "unload-module", i)
out["residual"] = {nm: listed(nm) for nm in ("r83c_a", "r83c_a2")}
print(json.dumps(out, indent=1))
