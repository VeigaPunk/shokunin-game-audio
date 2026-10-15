#!/usr/bin/env python3
"""r82-verify2 spot s3 — the exact-name unload negative control, live.

Imports the FROZEN d6167399 fixture, loads two seat-owned null sinks
whose names sit in the prefix trap: `r82w_ctl_a2` FIRST (lower module
index, listed first) and `r82w_ctl_a` SECOND. A substring predicate
scanning `pactl list modules short` for `sink_name=r82w_ctl_a` would
match the FOREIGN a2 line first and fire its index — the r82 critic-F4
incident shape. Under the fold's exact-equality fix the query must
return only `r82w_ctl_a`'s own index, the unload must destroy only
`r82w_ctl_a`, and `r82w_ctl_a2` must SURVIVE (negative control). The
foreign twin is then unloaded by its own exact name (cleanup) and the
post-state must show zero r82w_ctl_* objects."""
import importlib.util, json, subprocess, sys
from pathlib import Path

FIX = ("/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/"
       "r82-verify2/tree/corpus/fixtures/measure_audio.py")
spec = importlib.util.spec_from_file_location("ma_frozen", FIX)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)          # import-time band guard runs here
print("import_ok True (band guard passed for import pid", m.FFPW_R82_PID,
      "pair", m.FFPW_R82_TONE_L_HZ, m.FFPW_R82_TONE_R_HZ, ")")

def pactl_sinks():
    p = subprocess.run(["pactl", "list", "sinks", "short"],
                       capture_output=True, timeout=10)
    return p.stdout.decode(errors="replace")

def mod_lines():
    p = subprocess.run(["pactl", "list", "modules", "short"],
                       capture_output=True, timeout=10)
    return [ln for ln in p.stdout.decode(errors="replace").splitlines()
            if "r82w_ctl" in ln]

res = {"steps": []}
try:
    # load FOREIGN-prefix twin first so it holds the LOWER module index
    # and is listed before the query target — the sharpest trap order.
    loads = m._loopback_r79_sinks_load(["r82w_ctl_a2", "r82w_ctl_a"])
    res["loads"] = loads
    res["module_lines_after_load"] = mod_lines()

    id_a = (loads.get("r82w_ctl_a") or {}).get("module_id")
    id_a2 = (loads.get("r82w_ctl_a2") or {}).get("module_id")

    q_a = m._gst_r81_sink_module_index("r82w_ctl_a")
    q_a2 = m._gst_r81_sink_module_index("r82w_ctl_a2")
    res["query_r82w_ctl_a"] = q_a
    res["query_r82w_ctl_a2"] = q_a2
    res["query_a_is_own"] = (q_a == id_a)
    res["query_a_rejects_foreign"] = (q_a != id_a2)
    res["query_a2_is_own"] = (q_a2 == id_a2)

    # fire the name-verified unload at OUR name only
    unl = m._gst_r81_unload_own(id_a, sink_name="r82w_ctl_a")
    res["unload_r82w_ctl_a"] = unl

    sinks = pactl_sinks()
    res["a_gone"] = "r82w_ctl_a " not in sinks and \
        "r82w_ctl_a\n" not in sinks and "r82w_ctl_a\t" not in sinks
    res["a_gone_strict"] = not any(
        ln.split()[1] == "r82w_ctl_a"
        for ln in sinks.splitlines() if len(ln.split()) >= 2)
    res["foreign_a2_survives"] = any(
        ln.split()[1] == "r82w_ctl_a2"
        for ln in sinks.splitlines() if len(ln.split()) >= 2)
    res["sinks_mid"] = [ln for ln in sinks.splitlines() if "r82w_ctl" in ln]
finally:
    # cleanup: unload the foreign twin by its own exact name
    try:
        id_a2 = m._gst_r81_sink_module_index("r82w_ctl_a2")
        res["cleanup_query_a2"] = id_a2
        res["cleanup_unload_a2"] = m._gst_r81_unload_own(
            id_a2, sink_name="r82w_ctl_a2") if id_a2 is not None else \
            "not_listed"
    except Exception as exc:
        res["cleanup_exc"] = repr(exc)
    try:
        id_a = m._gst_r81_sink_module_index("r82w_ctl_a")
        if id_a is not None:
            res["cleanup_unload_a"] = m._gst_r81_unload_own(
                id_a, sink_name="r82w_ctl_a")
    except Exception as exc:
        res["cleanup_exc_a"] = repr(exc)
    res["module_lines_end"] = mod_lines()
    sinks = pactl_sinks()
    res["post_sinks_r82w"] = [ln for ln in sinks.splitlines()
                            if "r82w_ctl" in ln]

res["verdict"] = bool(
    res.get("query_a_is_own") and res.get("query_a_rejects_foreign") and
    res.get("query_a2_is_own") and
    (res.get("unload_r82w_ctl_a") or {}).get("exit_code") == 0 and
    res.get("a_gone_strict") and res.get("foreign_a2_survives") and
    not res.get("post_sinks_r82w"))
print(json.dumps(res, indent=2, default=str))
sys.exit(0 if res["verdict"] else 1)
