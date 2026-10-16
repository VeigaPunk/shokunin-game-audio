#!/usr/bin/env python3
"""r85 simplifier BIMODAL-ARMS proof — the three host-bimodal realizations
(latebind / cdup_cap / sd_prop) plus the t_sinkname and mix-phase surfaces
are pinned as EITHER-WAY, not silently absorbing.

Method: extract the pinned realization-classifier + failure-predicate slice
verbatim from the committed blob and EXECUTE it over synthetic leg states
representing BOTH hosts' realizations (the boundary's side and the authoring
host's side), plus the "bad" states that must still fail. A leg that
accepts both sides but never fails on a broken state is "silently
absorbing"; a leg that accepts both sides AND fails on the broken states is
either-way.
"""
import textwrap
from pathlib import Path

BASE = Path("proofs/base-measure_audio.py").read_text()
OUT = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    tag = "PASS" if cond else "FAIL"
    if cond:
        PASS += 1
    else:
        FAIL += 1
    OUT.append(f"[{tag}] {name}: {detail}")


def slice_between(src, start_marker, end_marker):
    i0 = src.index(start_marker)
    i0 = src.rindex("\n", 0, i0) + 1
    i1 = src.index(end_marker)
    i1 = src.index("\n", i1) + 1
    return textwrap.dedent(src[i0:i1])


def run(slice_text, ns):
    exec(slice_text, ns)
    return ns


# ================================================================= latebind
LATE = slice_between(
    BASE,
    '            l = legs["latebind"]',
    '"bind, no refusal measured")')
LATE_NS = "r85a_late_1"


def late_state(links, alive, exit_code):
    return {"legs": {"latebind": {"samples": [{"links": links}],
                                  "alive_at_end": alive,
                                  "exit_code": exit_code}},
            "failures": [],
            "PACTLMON_R85_LATE": LATE_NS}


late_bound = [{"out_node": LATE_NS, "out_port_name": "capture_FL",
               "in_node": "r85a_1_latebind", "in_port_name": "input_FL"}]
foreign = [{"out_node": "alsa_output.x", "out_port_name": "monitor_FL",
            "in_node": "r85a_1_latebind", "in_port_name": "input_FL"}]
cases = {
    "authoring side late_bound": (late_state(late_bound, True, 1),
                                  "late_bound", 0),
    "boundary side stalled": (late_state([], True, 1), "stalled", 0),
    "refused": (late_state([], False, 1), "refused", 0),
    "BAD foreign bind": (late_state(foreign, True, 1), "foreign_bind", 1),
    "BAD other (dead rc0, no links)": (late_state([], False, 0), "other", 1),
}
ok, det = True, []
for label, (ns, want_real, want_fails) in cases.items():
    run(LATE, ns)
    real = ns["legs"]["latebind"].get("realization")
    nf = len(ns["failures"])
    good = real == want_real and nf == want_fails
    ok = ok and good
    det.append(f"{label}: realization={real} failures={nf} "
               f"(want {want_real}/{want_fails}) ok={good}")
check("B1 latebind is either-way: late_bound AND stalled/refused pass; "
      "foreign_bind and 'other' fail", ok, "; ".join(det))

# ================================================================= cdup_cap
CDUP = slice_between(
    BASE,
    '                cl = legs.get("cdup_cap") or {}',
    '"digits-resolution lattice fails")')
NS = "r85a_ns_1"


def cdup_state(links, alive, exit_code):
    return {"legs": {"cdup_cap": {"samples": [{"links": links}],
                                  "alive_at_end": alive,
                                  "exit_code": exit_code}},
            "failures": [], "PACTLMON_R85_NS": NS}


serial_mon = [{"out_node": NS, "out_port_name": "monitor_FL",
               "in_node": "r85a_1_cdup_cap", "in_port_name": "input_FL"}]
name_shadow = [{"out_node": "235221", "out_port_name": "capture_FL",
                "in_node": "r85a_1_cdup_cap", "in_port_name": "input_FL"}]
foreign_mon = [{"out_node": "other.sink", "out_port_name": "monitor_FL",
                "in_node": "r85a_1_cdup_cap", "in_port_name": "input_FL"}]
cases = {
    "authoring side serial_monitor_bypass":
        (cdup_state(serial_mon, True, 1), "serial_monitor_bypass", 0),
    "boundary side name_shadow_bound":
        (cdup_state(name_shadow, True, 1), "name_shadow_bound", 0),
    "stalled": (cdup_state([], True, 1), "stalled", 0),
    "refused": (cdup_state([], False, 1), "refused", 0),
    "BAD foreign_monitor": (cdup_state(foreign_mon, True, 1),
                            "foreign_monitor", 1),
    "BAD other": (cdup_state([], False, 0), "other", 1),
}
ok, det = True, []
for label, (ns, want_real, want_fails) in cases.items():
    run(CDUP, ns)
    real = ns["legs"]["cdup_cap"].get("realization")
    nf = len(ns["failures"])
    good = real == want_real and nf == want_fails
    ok = ok and good
    det.append(f"{label}: realization={real} failures={nf} "
               f"(want {want_real}/{want_fails}) ok={good}")
check("B2 cdup_cap is either-way: serial_monitor_bypass AND "
      "name_shadow_bound/stalled/refused pass; foreign_monitor and 'other' "
      "fail", ok, "; ".join(det))

# ================================================================= sd_prop
SD = slice_between(
    BASE,
    '            l = legs["sd_prop"]',
    '"measured nothing")')
SD_NAME = "r85a_sd_1"
DEF = "default.sink"


def sd_state(links, module_gone):
    return {"legs": {"sd_prop": {"samples": [{"links": links}]}},
            "failures": [], "def_sink": DEF,
            "_pactlmon_r85_module_index":
                lambda f, v: None if module_gone else 11,
            "PACTLMON_R85_SD": SD_NAME}


mon_default = [{"out_node": DEF, "out_port_name": "monitor_FL",
                "in_node": "r85a_1_sd_prop", "in_port_name": "input_FL"}]
mon_foreign = [{"out_node": "alsa_output.x", "out_port_name": "monitor_FL",
                "in_node": "r85a_1_sd_prop", "in_port_name": "input_FL"}]
non_mon = [{"out_node": DEF, "out_port_name": "playback_FL",
            "in_node": "r85a_1_sd_prop", "in_port_name": "input_FL"}]
cases = {
    "boundary side clean_default_fallback":
        (sd_state(mon_default, False), "clean_default_fallback", 0),
    "authoring side bind_killed_then_default":
        (sd_state(mon_default, True), "bind_killed_then_default", 0),
    "BAD non-monitor links": (sd_state(non_mon, True), None, 1),
    "BAD monitor on a foreign node": (sd_state(mon_foreign, True), None, 1),
    "BAD vacuous (no links, module alive)": (sd_state([], False), None, 1),
}
ok, det = True, []
for label, (ns, want_real, want_fails) in cases.items():
    run(SD, ns)
    real = ns["legs"]["sd_prop"].get("realization")
    nf = len(ns["failures"])
    good = (want_real is None or real == want_real) and nf == want_fails
    ok = ok and good
    det.append(f"{label}: realization={real} failures={nf} "
               f"(want {want_real}/{want_fails}) ok={good}")
check("B3 sd_prop is either-way: clean_default_fallback AND "
      "bind_killed_then_default pass; non-monitor / foreign-monitor / "
      "vacuous states fail", ok, "; ".join(det))

# ================================================================= t_sinkname
TS = slice_between(
    BASE,
    '            ts = legs["t_sinkname"]',
    '"monitor_*")')
NS2 = "r85a_ns2_1"


def ts_state(ports, alive, exit_code):
    links = [{"out_node": NS2, "out_port_name": p,
              "in_node": "r85a_1_t_sinkname", "in_port_name": "input_FL"}
             for p in ports]
    legs = {"t_sinkname": {"samples": [{"links": links}],
                           "alive_at_end": alive,
                           "exit_code": exit_code}}

    def link_ports(nm):
        return {e.get("out_port_name")
                for s in legs[nm].get("samples", [])
                for e in s.get("links", [])}

    return {"legs": legs, "failures": [], "link_ports": link_ports}


cases = {
    "boundary/authoring side bound_source (capture_*)":
        (ts_state(["capture_FL"], True, 1), "bound_source", 0),
    "stalled": (ts_state([], True, 1), "stalled", 0),
    "refused": (ts_state([], False, 1), "refused", 0),
    "BAD monitor link": (ts_state(["monitor_FL"], True, 1), "bound_source", 1),
    "BAD other": (ts_state([], False, 0), "other", 1),
}
ok, det = True, []
for label, (ns, want_real, want_fails) in cases.items():
    run(TS, ns)
    real = ns["legs"]["t_sinkname"].get("realization")
    nf = len(ns["failures"])
    good = real == want_real and nf == want_fails
    ok = ok and good
    det.append(f"{label}: realization={real} failures={nf} "
               f"(want {want_real}/{want_fails}) ok={good}")
check("B4 t_sinkname is either-way: bound_source AND stalled/refused pass; "
      "a monitor_* link or 'other' fails", ok, "; ".join(det))

# ================================================================= mix phase
MIXDUP = slice_between(
    BASE,
    '            legs["mixdup"]["realization"] = (',
    '"(<=2.05x) fails")')


def mixdup_state(med, ref):
    return {"legs": {"mixdup": {}}, "failures": [], "dv": med, "ref": ref,
            "PACTLMON_R85_DUP_ENV": (1.80, 2.20)}


cases = {
    "coherent_2x (2.0)": (mixdup_state(2.0, 1.0), "coherent_2x", 0),
    "partial (0.26)": (mixdup_state(0.26, 1.0), "partial", 0),
    "cancelled (0.03)": (mixdup_state(0.03, 1.0), "cancelled", 0),
    "unmeasured": (mixdup_state(None, 1.0), "unmeasured", 1),
    "BAD over the linear bound (2.2)": (mixdup_state(2.2, 1.0),
                                        "coherent_2x", 1),
}
ok, det = True, []
for label, (ns, want_real, want_fails) in cases.items():
    ns["drat"] = (ns["dv"] / ns["ref"]) if ns["ref"] and ns["dv"] is not None \
        else None
    run(MIXDUP, ns)
    real = ns["legs"]["mixdup"].get("realization")
    nf = len(ns["failures"])
    good = real == want_real and nf == want_fails
    ok = ok and good
    det.append(f"{label}: ratio={ns['drat']} realization={real} "
               f"failures={nf} (want {want_real}/{want_fails}) ok={good}")
check("B5 the mix coherent-sum surface is classified (not armed) and only "
      "the linear bound fires", ok, "; ".join(det))

# ============================================================ B6 absorption
# The either-way property (B1-B4) is about the TWO NAMED host sides. This
# check enumerates the THIRD-state channels that are absorbed by the same
# arms (reported as findings, corroborating r85-critic F1/F2/F3 and the
# r85-scribe ADJ-3).
absorbed = {}

# B6a cdup_cap: a FOREIGN node's capture_* links -> name_shadow_bound, passes
foreign_cap = [{"out_node": "some.foreign.source", "out_port_name": "capture_FL",
                "in_node": "r85a_1_cdup_cap", "in_port_name": "input_FL"}]
ns = cdup_state(foreign_cap, True, 1)
run(CDUP, ns)
absorbed["cdup_cap foreign capture_* bind"] = (
    ns["legs"]["cdup_cap"].get("realization"), len(ns["failures"]))

# B6b the t_src* loop: a foreign node's capture_* links pass the shape check
CAP_SLICE = slice_between(
    BASE,
    "            for nm, want_node in (",
    '"did not resolve on the default monitor")')


def run_cap_slice(legs, def_sink):
    def link_ports(nm):
        return {e.get("out_port_name")
                for s in legs[nm].get("samples", [])
                for e in s.get("links", [])}

    ns = {"legs": legs, "failures": [], "def_sink": def_sink,
          "link_ports": link_ports, "PACTLMON_R85_VSRC": "r85a_vsrc_1"}
    exec(CAP_SLICE, ns)
    return ns["failures"]


def mk_legs():
    def sample(links):
        return {"samples": [{"links": links}]}

    cap = [{"out_node": "r85a_vsrc_1", "out_port_name": "capture_FL",
            "in_node": "x", "in_port_name": "input_FL"}]
    mon = [{"out_node": "r85a_ns2_1", "out_port_name": "monitor_FL",
            "in_node": "x", "in_port_name": "input_FL"}]
    dm = [{"out_node": DEF, "out_port_name": "monitor_FL",
           "in_node": "x", "in_port_name": "input_FL"}]
    return {"t_srcname": sample(cap), "t_srcserial": sample(cap),
            "t_srcid": sample(cap), "t_prop_sinkname": sample(mon),
            "t_prop_srcname": sample(dm)}


legs_foreign = mk_legs()
for nm in ("t_srcname", "t_srcserial", "t_srcid"):
    legs_foreign[nm] = {"samples": [{"links": [
        {"out_node": "some.foreign.source", "out_port_name": "capture_FL",
         "in_node": "r85a_1_" + nm, "in_port_name": "input_FL"}]}]}
fb = run_cap_slice(legs_foreign, "default.sink")
absorbed["t_src* foreign capture_* bind"] = ("shape-only", len(fb))

# B6c the sd connect-kill arm: "the module never existed" passes
SD_ARM = slice_between(
    BASE,
    '            for nm in ("sd_record", "sd_parec"):',
    '"death — the no-link arm fails")')


def sd_arm_state(module_dead_at, out_data):
    return {"legs": {"sd_record": {"module_dead_at_s": module_dead_at,
                                   "out": {"data_actual": out_data},
                                   "links": []}},
            "failures": []}


ns = sd_arm_state(0.0, 0)           # module never existed: "dead" at t=0
run(SD_ARM, ns)
absorbed["sd connect-kill never-loaded module"] = (
    "no failure", len(ns["failures"]))
ns = sd_arm_state(None, 0)          # never died -> must fail
run(SD_ARM, ns)
absorbed["sd connect-kill survived (None)"] = ("failure", len(ns["failures"]))
ns = sd_arm_state(2.5, 0)           # died too late -> must fail
run(SD_ARM, ns)
absorbed["sd connect-kill survived (2.5s)"] = ("failure", len(ns["failures"]))
ns = sd_arm_state(0.08, 500)        # content formed before death -> must fail
run(SD_ARM, ns)
absorbed["sd connect-kill content-before-death"] = (
    "failure", len(ns["failures"]))

# B6d mixdup: a single stream (ratio 1.0) is classified `partial` and passes
ns = mixdup_state(1.0, 1.0)
ns["drat"] = 1.0
run(MIXDUP, ns)
absorbed["mixdup single-stream (ratio 1.0)"] = (
    ns["legs"]["mixdup"].get("realization"), len(ns["failures"]))

gaps = {k: v for k, v in absorbed.items()
        if v[1] == 0 and k.split()[0] in ("cdup_cap", "t_src*", "sd", "mixdup")}
check("B6 absorption channels (third states that pass) enumerated — the "
      "either-way property holds for the two named sides, but these "
      "broken/degenerate states are NOT caught",
      absorbed["cdup_cap foreign capture_* bind"][1] == 0 and
      absorbed["t_src* foreign capture_* bind"][1] == 0 and
      absorbed["sd connect-kill never-loaded module"][1] == 0 and
      absorbed["mixdup single-stream (ratio 1.0)"][1] == 0 and
      absorbed["sd connect-kill survived (None)"][1] == 1 and
      absorbed["sd connect-kill survived (2.5s)"][1] == 1 and
      absorbed["sd connect-kill content-before-death"][1] == 1,
      "; ".join(f"{k}: realization={v[0]} failures={v[1]}"
                for k, v in absorbed.items()))

# ============================================================ B7 want_node
# The dead `want_node` (T8) encoded an out_node==VSRC+"b" expectation that
# the receipts CONTRADICT: the measured lattice legs bind the ORIGINAL
# `vsrc` (rep-0 source), not `vsrcb`.
import json
rec = json.loads(Path("../r85-author/runs/run1/measurements.json").read_text())
legs = rec["measurements"]["pactlmon_capture_r85_probe"]["legs"]
bound_nodes = {e.get("out_node") for nm in ("t_srcname", "t_srcserial",
                                            "t_srcid")
               for s in legs[nm]["samples"] for e in s["links"]}
vsrc = rec["measurements"]["pactlmon_capture_r85_probe"]["vsrc"]["node_id"] and \
    [n for n in bound_nodes if n and n.startswith("r85a_vsrc_")]
check("B7 the deleted `want_node` intent (VSRC+'b') contradicts the pinned "
      "receipts (the lattice legs bind the original vsrc)",
      all(not n.endswith("b") for n in bound_nodes) and bound_nodes,
      f"measured out_nodes={sorted(bound_nodes)} — a revived "
      f"`out_node == want_node` check would FAIL both pinned runs, which "
      f"is why T8 is reported (not silently folded away)")

Path("proofs/bimodal-arms.txt").write_text(
    "\n".join(OUT) + f"\n\nTOTAL: {PASS} PASS / {FAIL} FAIL\n",
    encoding="utf-8")
print("\n".join(OUT))
print(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
