#!/usr/bin/env python3
"""r85-critic arm replay: proves the three host-bimodal arms are pinned
EITHER-WAY (both recorded realizations pass) and NOT silently absorbing
(their failure modes still fail).

The arm text is sliced verbatim out of the COMMITTED blob
(`git show 2a49d540:corpus/fixtures/measure_audio.py`, line ranges
located by marker) and exec'd against (a) the committed run1/run2 legs
and (b) in-memory mutations that stand for the OTHER realization and for
the law-breaking shape. No host calls: the only external symbol used by
the sliced text (`_pactlmon_r85_module_index` in the sd_prop arm) is
stubbed.

Read-only: writes only under corpus/live/r85-critic/.
"""
import copy
import json
import subprocess
import textwrap
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = ROOT / "corpus/live/r85-critic"
COMMIT = "2a49d540"

blob = subprocess.run(["git", "show", f"{COMMIT}:corpus/fixtures/measure_audio.py"],
                      cwd=ROOT, capture_output=True, check=True).stdout.decode()
lines = blob.splitlines()


def slice_by_markers(start_marker, end_marker, occurrence=1):
    """Return the source text from the line containing start_marker
    through the line containing end_marker (inclusive)."""
    hits = [i for i, ln in enumerate(lines) if start_marker in ln]
    assert hits, f"start marker missing: {start_marker}"
    i0 = hits[occurrence - 1]
    j = next(j for j in range(i0, len(lines)) if end_marker in lines[j])
    return textwrap.dedent("\n".join(lines[i0:j + 1]))


ARMS = {
    "helpers": slice_by_markers('def links_of(nm):',
                                'return {e.get("out_port_name") for e in links_of(nm)}'),
    "t_sinkname": slice_by_markers('ts = legs["t_sinkname"]',
                                   '"monitor_*")'),
    "cdup_cap": slice_by_markers('cl = legs.get("cdup_cap") or {}',
                                 '"digits-resolution lattice fails")'),
    "sd_prop": slice_by_markers('l = legs["sd_prop"]',
                                '"measured nothing")'),
    "latebind": slice_by_markers('l = legs["latebind"]',
                                 '"bind, no refusal measured")'),
}

NS = "r85a_ns_1"
NS2 = "r85a_ns2_1"
LATE = "r85a_late_1"
SD = "r85a_sd_1"
DEF = "alsa_output.default.1"


def edge(out_node, port, in_node="rec"):
    return {"out": f"{out_node}:{port}", "in": f"{in_node}:input_FL",
            "out_node": out_node, "in_node": in_node,
            "out_port_name": port, "in_port_name": "input_FL",
            "state": "active"}


def run_arm(arm, legs, names, *, sd_index=5):
    ns = {
        "legs": copy.deepcopy(legs), "failures": [],
        "PACTLMON_R85_NS": names["ns"], "PACTLMON_R85_NS2": names["ns2"],
        "PACTLMON_R85_LATE": names["late"], "PACTLMON_R85_SD": names["sd"],
        "def_sink": names["def"],
        "_pactlmon_r85_module_index": lambda *a, **k: sd_index,
    }
    exec(ARMS["helpers"], ns)  # noqa: S102 - verbatim committed helper text
    exec(ARMS[arm], ns)  # noqa: S102 - verbatim committed arm text
    return ns["failures"], ns["legs"]


def load(run):
    d = json.load(open(ROOT / f"corpus/live/r85-author/runs/{run}/measurements.json"))
    m = d["measurements"]
    cap = m["pactlmon_capture_r85_probe"]
    addr = m["pactlmon_addr_r85_probe"]
    late_links = [e for s in cap["legs"]["latebind"].get("samples", [])
                  for e in (s.get("links") or [])]
    ser_links = [e for s in cap["legs"]["t_sinkserial"].get("samples", [])
                 for e in (s.get("links") or [])]
    cdup_links = [e for s in addr["legs"]["cdup_cap"].get("samples", [])
                  for e in (s.get("links") or [])]
    sd_out = None
    for nm in ("sd_record", "sd_parec", "sd_prop", "sd_pwlink"):
        l = cap["legs"].get(nm) or {}
        if l.get("tag", "").startswith("r85a_"):
            sd_out = l["tag"].replace("r85a_", "r85a_sd_") if "_sd_" not in l["tag"] else l["tag"]
        if (l.get("sd_ports") or l.get("links")):
            pass
    sd_name = next((ln for ln in [cap["legs"]["sd_pwlink"].get("argv", "")] if ln), "")
    names = {
        "ns": cdup_links[0]["out_node"] if cdup_links else "r85a_ns_x",
        "ns2": ser_links[0]["out_node"] if ser_links else "r85a_ns2_x",
        "late": late_links[0]["out_node"] if late_links else "r85a_late_x",
        "sd": "r85a_sd_" + str(addr["contention"]["own_pid"]),
        "def": cap["inventory"]["default_sink"],
        "pid": addr["contention"]["own_pid"],
    }
    return m, names


m1, N1 = load("run1")
m2, N2 = load("run2")
report = {"commit": COMMIT, "arm_ranges": {k: ARMS[k].splitlines()[0] + " ... "
                                           + ARMS[k].splitlines()[-1].strip()
                                           for k in ARMS}, "cases": []}


def case(name, arm, legs, names, want_fail, *, sd_index=5):
    fails, _ = run_arm(arm, legs, names, sd_index=sd_index)
    got = bool(fails)
    report["cases"].append({"case": name, "arm": arm, "expected_failure": want_fail,
                            "got_failure": got, "failures": fails,
                            "match": got == want_fail})


def leg(entry, nm):
    return copy.deepcopy(entry["legs"][nm])


CAP = "pactlmon_capture_r85_probe"
ADDR = "pactlmon_addr_r85_probe"

# ---------- t_sinkname (capture lattice, noprop sink name) ----------
for run, m, N in (("run1", m1, N1), ("run2", m2, N2)):
    case(f"{run}:t_sinkname committed (bound_source)", "t_sinkname",
         {"t_sinkname": leg(m[CAP], "t_sinkname")}, N, False)
ts = {"t_sinkname": leg(m1[CAP], "t_sinkname")}
ts["t_sinkname"]["samples"] = [{"at_s": 1.0, "links": [
    edge(N1["ns2"], "monitor_FL")], "size": 100, "node_alive": True}]
case("t_sinkname mutated: monitor link (law break)", "t_sinkname", ts, N1, True)
ts = {"t_sinkname": leg(m1[CAP], "t_sinkname")}
ts["t_sinkname"]["samples"] = [{"at_s": 1.0, "links": [], "size": 44,
                                "node_alive": True}]
ts["t_sinkname"]["alive_at_end"] = False
ts["t_sinkname"]["exit_code"] = 3
case("t_sinkname mutated: 'other' shape", "t_sinkname", ts, N1, True)
ts = {"t_sinkname": leg(m1[CAP], "t_sinkname")}
ts["t_sinkname"]["samples"] = [{"at_s": 1.0, "links": [], "size": 44,
                                "node_alive": True}]
ts["t_sinkname"]["alive_at_end"] = False
ts["t_sinkname"]["exit_code"] = 1
case("t_sinkname mutated: refusal (boundary realization)", "t_sinkname", ts, N1, False)
ts = {"t_sinkname": leg(m1[CAP], "t_sinkname")}
ts["t_sinkname"]["samples"] = [{"at_s": 1.0, "links": [], "size": 44,
                                "node_alive": True}]
ts["t_sinkname"]["alive_at_end"] = True
case("t_sinkname mutated: stalled (boundary realization)", "t_sinkname", ts, N1, False)
ts = {"t_sinkname": leg(m1[CAP], "t_sinkname")}
ts["t_sinkname"]["samples"] = [{"at_s": 1.0, "links": [
    edge(N1["ns2"], "capture_FL")], "size": 100, "node_alive": True}]
case("t_sinkname mutated: arbitrary source bind, no monitor (other side)",
     "t_sinkname", ts, N1, False)

# ---------- cdup_cap (serial-first collision) ----------
for run, m, N in (("run1", m1, N1), ("run2", m2, N2)):
    case(f"{run}:cdup_cap committed (serial_monitor_bypass)", "cdup_cap",
         {"cdup_cap": leg(m[ADDR], "cdup_cap")}, N, False)
cc = {"cdup_cap": leg(m1[ADDR], "cdup_cap")}
cc["cdup_cap"]["samples"] = [{"at_s": 1.0, "links": [edge("foreign_sink", "monitor_FL")]}]
case("cdup_cap mutated: foreign monitor (law break)", "cdup_cap", cc, N1, True)
cc = {"cdup_cap": leg(m1[ADDR], "cdup_cap")}
cc["cdup_cap"]["samples"] = [{"at_s": 1.0, "links": [edge("some_source", "capture_FL")]}]
case("cdup_cap mutated: name_shadow_bound / bound_source (other side)",
     "cdup_cap", cc, N1, False)
cc = {"cdup_cap": leg(m1[ADDR], "cdup_cap")}
cc["cdup_cap"]["samples"] = [{"at_s": 1.0, "links": []}]
cc["cdup_cap"]["alive_at_end"] = False
cc["cdup_cap"]["exit_code"] = 1
case("cdup_cap mutated: refused (other side)", "cdup_cap", cc, N1, False)
cc = {"cdup_cap": leg(m1[ADDR], "cdup_cap")}
cc["cdup_cap"]["samples"] = [{"at_s": 1.0, "links": []}]
cc["cdup_cap"]["alive_at_end"] = True
case("cdup_cap mutated: stalled (other side)", "cdup_cap", cc, N1, False)

# ---------- sd_prop (self-destruct prop form) ----------
for run, m, N in (("run1", m1, N1), ("run2", m2, N2)):
    case(f"{run}:sd_prop committed (bind_killed_then_default)", "sd_prop",
         {"sd_prop": leg(m[CAP], "sd_prop")}, N, False, sd_index=None)
sp = {"sd_prop": leg(m1[CAP], "sd_prop")}
sp["sd_prop"]["samples"] = [{"at_s": 1.0, "links": [edge(N1["def"], "monitor_FL")]},
                            {"at_s": 2.0, "links": [edge(N1["def"], "monitor_FR")]}]
case("sd_prop mutated: clean_default_fallback (other side)", "sd_prop", sp, N1,
     False, sd_index=5)
sp = {"sd_prop": leg(m1[CAP], "sd_prop")}
sp["sd_prop"]["samples"] = [{"at_s": 1.0, "links": []}]
case("sd_prop mutated: no links + module alive (measured nothing)", "sd_prop", sp,
     N1, True, sd_index=5)
sp = {"sd_prop": leg(m1[CAP], "sd_prop")}
sp["sd_prop"]["samples"] = [{"at_s": 1.0, "links": [edge(N1["sd"], "capture_FL")]},
                            {"at_s": 2.0, "links": [edge(N1["def"], "monitor_FL")]}]
case("sd_prop mutated: transient trap bind visible (non-monitor)", "sd_prop", sp,
     N1, True, sd_index=5)
sp = {"sd_prop": leg(m1[CAP], "sd_prop")}
sp["sd_prop"]["samples"] = [{"at_s": 1.0, "links": [edge("other_sink", "monitor_FL")]}]
case("sd_prop mutated: monitor link on a FOREIGN sink", "sd_prop", sp, N1, True,
     sd_index=5)
sp = {"sd_prop": leg(m1[CAP], "sd_prop")}
sp["sd_prop"]["samples"] = [{"at_s": 1.0, "links": []}]
case("sd_prop mutated: no links, module gone (died at bind)", "sd_prop", sp, N1,
     False, sd_index=None)

# ---------- latebind (no-late-bind, bimodal) ----------
for run, m, N in (("run1", m1, N1), ("run2", m2, N2)):
    case(f"{run}:latebind committed (late_bound)", "latebind",
         {"latebind": leg(m[CAP], "latebind")}, N, False)
lb = {"latebind": leg(m1[CAP], "latebind")}
lb["latebind"]["samples"] = [{"at_s": 1.0, "links": []}, {"at_s": 2.6, "links": []}]
lb["latebind"]["alive_at_end"] = True
case("latebind mutated: stalled (boundary realization)", "latebind", lb, N1, False)
lb = {"latebind": leg(m1[CAP], "latebind")}
lb["latebind"]["samples"] = [{"at_s": 1.0, "links": []}, {"at_s": 2.6, "links": []}]
lb["latebind"]["alive_at_end"] = False
lb["latebind"]["exit_code"] = 1
case("latebind mutated: refused (boundary realization)", "latebind", lb, N1, False)
lb = {"latebind": leg(m1[CAP], "latebind")}
lb["latebind"]["samples"] = [{"at_s": 1.0, "links": [edge(N1["ns2"], "monitor_FL")]},
                             {"at_s": 2.6, "links": [edge(N1["late"], "capture_FL")]}]
case("latebind mutated: foreign monitor bind (law break)", "latebind", lb, N1, True)
lb = {"latebind": leg(m1[CAP], "latebind")}
lb["latebind"]["samples"] = [{"at_s": 1.0, "links": [edge("other_src", "capture_FL")]}]
case("latebind mutated: foreign source capture bind (law break)", "latebind", lb, N1, True)
lb = {"latebind": leg(m1[CAP], "latebind")}
lb["latebind"]["samples"] = [{"at_s": 1.0, "links": []}]
lb["latebind"]["alive_at_end"] = False
lb["latebind"]["exit_code"] = 0
case("latebind mutated: 'other' (dead, rc0, no links)", "latebind", lb, N1, True)

report["names"] = {"run1": N1, "run2": N2}
report["all_match"] = all(c["match"] for c in report["cases"])
(OUT / "arm-replay.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"all_match": report["all_match"],
                  "cases": [{k: c[k] for k in ("case", "expected_failure",
                                               "got_failure", "match")}
                            for c in report["cases"]]}, indent=1))
