#!/usr/bin/env python3
"""r86-critic arm replay.

Slices the FIVE committed r86 verdict blocks out of
`git show fa5994a0:corpus/fixtures/measure_audio.py` (verbatim text, no
paraphrase) and execs each against:

  * the committed run1 and run2 legs  -> must reproduce failures == []
  * targeted mutations               -> absorption / coverage demos

Writes arm-replay.json next to itself.
"""
import copy
import textwrap
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SRC = subprocess.run(["git", "-C", str(REPO), "show",
                      "fa5994a0:corpus/fixtures/measure_audio.py"],
                     capture_output=True, check=True).stdout.decode()

RUNS = {
    "run1": REPO / "corpus/live/runs/20261016T063006268243Z-pwctl-r86/measurements.json",
    "run2": REPO / "corpus/live/runs/20261016T063043717745Z-pwctl-r86/measurements.json",
}
ENTRIES = {
    "pwctl_addr_r86_probe": "addr",
    "pwctl_params_r86_probe": "params",
    "pwctl_dsp_r86_probe": "dsp",
    "pwctl_meta_r86_probe": "meta",
    "pwctl_tools_r86_probe": "tools",
}

# ---- constants + helpers, sliced verbatim -------------------------------
consts = re.search(r"PWCTL_R86_PID = os\.getpid\(\).*?PWCTL_R86_CUBIC_PCT = \([^\n]+\)\n",
                   SRC, re.S).group(0)
update_rows = re.search(r"def _pwctl_r86_update_rows\(text\):.*?\n\n\n", SRC, re.S).group(0)
consts = consts.replace("PWCTL_R86_PID = os.getpid()", "PWCTL_R86_PID = 2675030")
NS = {"re": re, "os": None, "PLAYBACK_R78_TONE_AMP": 8192}

# ---- verdict blocks, sliced by marker -----------------------------------
blocks = {}
for m in re.finditer(r"\n    # ---------------- verdicts ----------------\n(.*?)\n    entry\[\"legs\"\] = legs\n",
                     SRC, re.S):
    body = m.group(1)
    # identify which entry by a distinctive marker
    if "ls_serial" in body:
        blocks["addr"] = body
    elif "n_enumformat" in body and "sp_port_lat" in body:
        blocks["params"] = body
    elif "PACTL" not in body and "regions" in body and "solo" in body:
        blocks["dsp"] = body
    elif "meta_census" in body:
        blocks["meta"] = body
    elif "lk_dup" in body:
        blocks["tools"] = body
assert set(blocks) == {"addr", "params", "dsp", "meta", "tools"}, sorted(blocks)


def exec_block(name, legs, entry, pid=None):
    ns = dict(NS)
    exec(consts, ns)
    exec(update_rows, ns)
    if pid is None:
        m = re.search(r"r86a_(\d+)_remote",
                      ((legs.get("jack_r") or {}).get("env") or {})
                      .get("R", ""))
        pid = int(m.group(1)) if m else 2675030
    ns.update({"PWCTL_R86_PID": pid, "PWCTL_R86_PREFIX": f"r86a_{pid}",
               "PWCTL_R86_NS": f"r86a_ns_{pid}",
               "PWCTL_R86_ROLE": f"r86arole{pid}",
               "PWCTL_R86_TAP": f"r86a_tap_{pid}"})
    ns.update({"legs": legs, "failures": [], "entry": entry,
               "PWCTL_R86_META_KEY": "r86a_k"})
    # function-locals the verdict blocks reference
    leaf = entry.get("ns_leaf") or {}
    ns["nid"] = leaf.get("node_id")
    ns["ser"] = str(leaf.get("object_serial"))
    subj = entry.get("subjects") or {}
    ns["port0"] = subj.get("port")
    ns["lid"] = subj.get("link")
    if ns["nid"] is None:
        m = re.search(r"pw-metadata -n default (\d+) ", 
                      (legs.get("m_write") or {}).get("argv") or "")
        if m:
            ns["nid"] = int(m.group(1))
    exec(textwrap.dedent(blocks[name]), ns)
    return ns["failures"], ns["entry"], ns["legs"]


results = {}


def load(run):
    return json.loads(RUNS[run].read_text())["measurements"]


# ---- 1. re-derivation on the committed receipts --------------------------
for run in ("run1", "run2"):
    m = load(run)
    per = {}
    for key, short in ENTRIES.items():
        e = copy.deepcopy(m[key])
        f, _entry, _legs = exec_block(short, e["legs"], e)
        per[key] = f
    results[f"rederive_{run}"] = per

# ---- 2. mutations --------------------------------------------------------
MUT = {}

# A1: dump_id vs dump_serial differ in TOTAL length, 700-char previews equal
MUT["A1_dump_id_serial_bytes_differ"] = {
    "entry": "pwctl_addr_r86_probe", "block": "addr",
    "f": lambda e: e["legs"]["dump_serial"].update(
        {"stdout_bytes": e["legs"]["dump_serial"]["stdout_bytes"] + 137}),
    "expect": "pass (absorption: the equality arm compares only the 700-char preview)"}

# A2: ls <id> returns the node's id row (partial resolution, no serial line)
MUT["A2_ls_id_partial_row"] = {
    "entry": "pwctl_addr_r86_probe", "block": "addr",
    "f": lambda e: e["legs"]["ls_id"].update(
        {"exit_code": 0, "stdout_bytes": 60,
         "stdout": f"id {e['legs']['ls_serial']['stdout'].split('id ')[1].split(',')[0]}, "
                   "type PipeWire:Interface:Node/3\n  object.path = \"x\"\n"}),
    "expect": "pass (gap: 'did not resolve' is armed as absence of the serial line only)"}

# A3: two pw-dump self clients (stale extra) -> report says 'exactly 1'
MUT["A3_self_clients_two"] = {
    "entry": "pwctl_addr_r86_probe", "block": "addr",
    "f": lambda e: e["legs"]["dump_full1"].update(
        {"self_clients": 2, "self_serials": ["242898", "242899"]}),
    "expect": "pass (absorption: arm is self_clients >= 1, not == 1)"}

# A4: dump_color_eq the OTHER boot's realization (0B rc0) — record-only
MUT["A4_dump_color_eq_other_realization"] = {
    "entry": "pwctl_addr_r86_probe", "block": "addr",
    "f": lambda e: e["legs"]["dump_color_eq"].update(
        {"exit_code": 0, "stdout_bytes": 0, "error_class": None}),
    "expect": "pass (by design: record-only arm, both realizations inert)"}

# P1: n_format pod-absent realization (the boundary's side)
MUT["P1_n_format_pod_absent"] = {
    "entry": "pwctl_params_r86_probe", "block": "params",
    "f": lambda e: e["legs"]["n_format"].update(
        {"has_pod": False, "stdout_bytes": 0}),
    "expect": "pass (documented rc-only arm: pod presence is negotiation-tracked)"}

# P2: n_format rc!=0 — control, the rc family IS armed
MUT["P2_n_format_rc1_control"] = {
    "entry": "pwctl_params_r86_probe", "block": "params",
    "f": lambda e: e["legs"]["n_format"].update({"exit_code": 1}),
    "expect": "FAIL (control: rc!=0 must trip the arm)"}

# P3: d_route the dump realization — record-only either way
MUT["P3_d_route_dump_realization"] = {
    "entry": "pwctl_params_r86_probe", "block": "params",
    "f": lambda e: e["legs"]["d_route"].update(
        {"has_pod": True, "stdout_bytes": 431}),
    "expect": "pass (by design: record-only arm)"}

# P4: not-implemented rows vanish (subject resolution failure) -> silent skip
MUT["P4_notimpl_rows_absent"] = {
    "entry": "pwctl_params_r86_probe", "block": "params",
    "f": lambda e: [e["legs"].pop(k) for k in
                    ("c_props", "f_props", "m_props", "l_props",
                     "core_setparam")],
    "expect": "pass (coverage hole: rows silently skipped, no failure/block)"}

# M1: census gap with an EMPTY pw-dump set (reader failure -> [])
MUT["M1_census_gap_empty_dump"] = {
    "entry": "pwctl_meta_r86_probe", "block": "meta",
    "f": lambda e: e["meta_census"].update({"dump_ids": []}),
    "expect": "pass (absorption: empty set is trivially a strict subset)"}

# M2: census gap violated (dump == ls) — control
MUT["M2_census_gap_equal_control"] = {
    "entry": "pwctl_meta_r86_probe", "block": "meta",
    "f": lambda e: e["meta_census"].update(
        {"dump_ids": list(e["meta_census"]["ls_ids"])}),
    "expect": "FAIL (control: no strict subset)"}

# M3: ls Metadata reader failure -> arm silently skipped
MUT["M3_census_ls_reader_failure"] = {
    "entry": "pwctl_meta_r86_probe", "block": "meta",
    "f": lambda e: e["meta_census"].update({"ls_ids": []}),
    "expect": "pass (coverage hole: arm skipped when ls_ids empty)"}

# T1: cli_devnull clean exit (scout's falsified row) — control
MUT["T1_cli_devnull_clean_control"] = {
    "entry": "pwctl_tools_r86_probe", "block": "tools",
    "f": lambda e: e["legs"]["cli_devnull"].update(
        {"exit_code": 0, "signal": None}),
    "expect": "FAIL (control: the abort class is armed)"}

# D1: cv25 not attenuated — control
MUT["D1_dsp_cv25_full_control"] = {
    "entry": "pwctl_dsp_r86_probe", "block": "dsp",
    "f": lambda e: e["legs"]["regions"]["cv25"].update({"median_peak": 8192.0}),
    "expect": "FAIL (control: the linear-DSP envelope is armed)"}

for name, spec in MUT.items():
    m = load("run1")
    e = copy.deepcopy(m[spec["entry"]])
    spec["f"](e)
    f, entry, legs = exec_block(spec["block"], e["legs"], e)
    results[name] = {"failures": f, "expected": spec["expect"],
                     "blocked": entry.get("coverage_blocked"),
                     "legs_mutated": True}

out = REPO / "corpus/live/r86-critic/arm-replay.json"
out.write_text(json.dumps(results, indent=2) + "\n")

# ---- summary -------------------------------------------------------------
for k, v in results.items():
    if k.startswith("rederive"):
        n = sum(len(x) for x in v.values())
        print(f"{k}: total failures across 5 entries = {n} "
              f"{'OK' if n == 0 else 'RED'}")
    else:
        print(f"{k}: failures={v['failures']} | expected: {v['expected']}")
