#!/usr/bin/env python3
"""r92 simplifier — fold proofs (no live probe needed).

Part A  replay differential: the four entry functions of base and folded
        trees, driven verbatim by the author's own recorded receipts (the
        measurement layer is stubbed from the receipt's legs).  Real bytes:
        the replayed entries must be byte-identical.
Part B  gate differential: synthetic entry heads (daemon bad / tools missing)
        exercise the base inline gates vs the folded helper.
Part C  F1 domain table: _fc92_shift_ok over the reachable input domain.
Part D  static: call-site census, AST locality, dead-local census.

Usage: python3 prove.py <base-tree> <folded-tree> [--receipts DIR] [--out JSON]
"""
import ast
import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

RECEIPTS = Path("/home/vgpnk/Projects/shokunin/audio-shokunin-wt-r92/"
                "corpus/live/r92-author/receipts")
RUNS = ("runA-20261016T094024556467Z", "runB-20261016T094602455160Z")
ENTRIES = ("filterchain_arm_r92_probe", "filterchain_dsp_r92_probe",
           "filterchain_ir_r92_probe", "filterchain_wpx_r92_probe")

SCRATCH_KEYS = ("tone", "tone200", "delta", "ir_2tap", "ir_d100",
                "ir_decay512", "ir_441", "ir_stereo", "ir_empty", "ir_text",
                "ir_dir", "bad_path")


def load_module(tree, tag):
    path = Path(tree) / "corpus/fixtures/measure_audio.py"
    spec = importlib.util.spec_from_file_location(f"ma_{tag}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_receipt(run):
    d = json.loads((RECEIPTS / f"{run}-measurements.json").read_text())
    return d["measurements"]


def stub(mod, head, legs, scratch="/tmp/r92s-replay"):
    """Stub the measurement layer; the verdict code stays committed."""
    mod._fc92_entry_head = lambda probe: copy.deepcopy(head)
    stim = {k: f"{scratch}/{k}.wav" for k in SCRATCH_KEYS}
    mod._fc92_ctx = lambda: {"scratch": Path(scratch), "procs": [],
                             "loads": {}, "stim": stim}
    mod._fc92_teardown = lambda entry, failures, ctx: None
    mod._fc92_daemon_health = lambda timeout_s=15.0: {"ok": True,
                                                      "exit_code": 0,
                                                      "killed_at_bound":
                                                      False,
                                                      "wall_s": 0.01}
    # ---- arm-entry producers
    mod._fc92_lifetime_leg = (
        lambda ctx, tag="life": copy.deepcopy(legs["a_lifetime"]))
    mod._fc92_shape_leg = (
        lambda ctx, tag, media_class=True:
        copy.deepcopy(legs["a_ports_sink" if media_class
                           else "a_ports_none"]))
    LOAD_TAGS = {"lq": "a_links_quoted", "lb": "a_links_bare",
                 "hsh": "a_hash_uri", "gn": "a_graph_num",
                 "ge": "a_graph_empty", "bl": "a_bad_label",
                 "bt": "a_bad_type", "ff": "a_ffmpeg", "ld": "a_ladspa",
                 "bs": "a_bare_spaced", "qs": "a_quoted_spaced",
                 "tc": "a_typo_ctl", "eb": "a_ebur128",
                 "ebx": "a_ebur128_bad", "sf": "a_sofa", "sfc": "a_sofa_cfg",
                 "lnc": "a_load_noconfig", "lms": "a_load_missing",
                 "l5": "a_load_dbg5"}
    mod._fc92_load_leg = (
        lambda ctx, tag, graph_text, **kw:
        copy.deepcopy(legs[LOAD_TAGS[tag]]))
    mod._fc92_label_leg = (
        lambda ctx, tag, label, rep:
        copy.deepcopy(legs["a_labels"][f"{label}#{rep}"]))

    def run_stub(argv, timeout_s, **kw):
        """pw-cli stdin classes (arm) and wpexec script classes (wpx)."""
        if argv and argv[0] == "wpexec":
            if len(argv) == 1:
                return copy.deepcopy(legs["w_noargv"])
            return copy.deepcopy(legs["w_missing"])
        return _stdin_leg(legs, kw)
    mod._fc92_run = run_stub
    # ---- audio producers (dsp + ir)
    mod._fc92_audio_leg = (
        lambda ctx, entry, tag, node, kind, stim, **kw:
        copy.deepcopy(legs[tag]))
    mod._fc92_residual = (
        lambda out_path, ir_path, stim_path, **kw:
        copy.deepcopy(legs["i_residual"].get(
            Path(out_path).name.rsplit("_", 2)[0], {})))
    # ---- wpexec producers
    WPX_TAGS = {"w_print": "w_print", "w_globals": "w_globals",
                "w_rawget": "w_rawget", "w_req": "w_require_api",
                "w_settings": "w_settings", "w_lmb": "w_lm_bad_module",
                "w_lml": "w_lm_bad_label", "w_noquit": "w_noquit",
                "w_empty": "w_empty", "w_syntax": "w_syntax"}
    mod._fc92_wpx_leg = (
        lambda ctx, name, body, **kw: copy.deepcopy(legs[WPX_TAGS[name]]))
    mod._fc92_wpx_bg = (
        lambda ctx, name, body, **kw:
        copy.deepcopy(legs["w_localmodule"]))
    return mod


def _stdin_leg(legs, kw):
    sd = kw.get("stdin_data")
    if sd is None:
        return copy.deepcopy(legs["a_eof_null"])
    if sd == b"":
        return copy.deepcopy(legs["a_eof_pipe"])
    return copy.deepcopy(legs["a_quit"])


def run_entry(mod, name, entry_name, head=None, arms=None):
    """Drive one committed entry function with the stubs installed."""
    entry = getattr(mod, entry_name)()
    return entry


def jdump(o):
    return json.dumps(o, sort_keys=True, default=str)


def static_block(tree, tag):
    """Part D: call-site census + AST locality of the block."""
    src = (Path(tree) / "corpus/fixtures/measure_audio.py").read_text()
    tree_ast = ast.parse(src)
    calls = {}
    for node in ast.walk(tree_ast):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.setdefault(node.func.id, []).append(
                (len(node.args), tuple(k.arg for k in node.keywords)))
    return {"src_sha256": hashlib.sha256(src.encode()).hexdigest(),
            "lines": src.count("\n"),
            "fc92_block_calls": calls.get("_fc92_block", []),
            "shift_ok_calls": calls.get("_fc92_shift_ok", []),
            "daemon_gate_calls": calls.get("_fc92_daemon_gate", [])}


def top_def_hashes(tree):
    src = (Path(tree) / "corpus/fixtures/measure_audio.py").read_text()
    lines = src.splitlines()
    tree_ast = ast.parse(src)
    out = {}
    for node in tree_ast.body:
        if isinstance(node, ast.FunctionDef):
            seg = "\n".join(lines[node.lineno - 1:node.end_lineno])
            out[node.name] = hashlib.sha256(seg.encode()).hexdigest()[:16]
    return out


def main():
    base_tree, folded_tree = sys.argv[1], sys.argv[2]
    out_path = None
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])
    result = {}

    # ---------------- Part D (static, cheap) ----------------
    sb, sf = static_block(base_tree, "base"), static_block(folded_tree, "fold")
    db, df = top_def_hashes(base_tree), top_def_hashes(folded_tree)
    changed = sorted(k for k in set(db) | set(df)
                     if db.get(k) != df.get(k))
    result["static"] = {
        "base": sb, "folded": sf,
        "changed_top_level_defs": changed,
        "added_top_level_defs": sorted(set(df) - set(db)),
        "removed_top_level_defs": sorted(set(db) - set(df)),
    }

    # ---------------- modules ----------------
    mb = load_module(base_tree, "base")
    mf = load_module(folded_tree, "fold")

    # ---------------- Part C (F1 domain table) ----------------
    deltas = [None, 0, 48, 110, 480, 1024, 110 + 1024, 1024 - 2, 1024 + 2,
              2431, 2431 + 4096, 2431 - 4096, 10000, -1.5, 0.0, -0.0,
              True, False]
    wants = [0, 48, 110, 2431]
    c_rows = []
    c_ok = True
    for d in deltas:
        for w in wants:
            b = mb._fc92_shift_ok(d, w)
            f = mf._fc92_shift_ok(d, w)
            eq = (b[0] == f) and isinstance(f, bool)
            c_ok = c_ok and eq
            if not eq:
                c_rows.append({"delta": d, "want": w, "base": b, "fold": f})
    result["C_shift_ok"] = {"all_equal": c_ok, "rows": len(deltas) * len(wants),
                            "mismatches": c_rows}

    # ---------------- Part A (replay differential) ----------------
    a_out = {}
    for run in RUNS:
        meas = load_receipt(run)
        for entry_name in ENTRIES:
            rec = meas[entry_name]
            legs = copy.deepcopy(rec["legs"])
            head = {"probe": rec.get("probe"), "daemon": {"ok": True},
                    "contention": {}, "oracle_at_start": None,
                    "foreign_r92a_nodes": [], "inventory": {},
                    "loadavg": [0, 0, 0]}
            stub(mb, head, legs)
            eb = run_entry(mb, run, entry_name, head)
            stub(mf, head, legs)
            ef = run_entry(mf, run, entry_name, head)
            eq = jdump(eb) == jdump(ef)
            a_out.setdefault(run, {})[entry_name] = {
                "entries_identical": eq,
                "base_failures": eb.get("failures"),
                "fold_failures": ef.get("failures"),
            }
    result["A_replay_real"] = a_out

    # ---------------- Part A2 (mutations) ----------------
    run = RUNS[0]
    meas = load_receipt(run)
    head = {"probe": "mut", "daemon": {"ok": True}, "contention": {},
            "oracle_at_start": None, "foreign_r92a_nodes": [],
            "inventory": {}, "loadavg": [0, 0, 0]}
    muts = {}

    def replay(entry_name, legs, which):
        if which == "base":
            stub(mb, head, legs)
            return run_entry(mb, run, entry_name)
        stub(mf, head, legs)
        return run_entry(mf, run, entry_name)

    def fails(entry, needle):
        return [f for f in entry.get("failures") or [] if needle in f]

    # M1: d_fhi loses its gain_db (delete / empty)
    for label, mfn in (("delete", lambda a: a.pop("gain_db", None)),
                       ("empty", lambda a: a.update(gain_db={}))):
        legs = copy.deepcopy(meas["filterchain_dsp_r92_probe"]["legs"])
        mfn(legs["d_fhi"]["analysis"])
        b = replay("filterchain_dsp_r92_probe", legs, "base")
        f = replay("filterchain_dsp_r92_probe", legs, "fold")
        muts[f"M1_d_fhi_{label}"] = {
            "base_d_fhi_fail": fails(b, "d_fhi"),
            "fold_d_fhi_fail": fails(f, "d_fhi"),
            "base_other_fails": len(b.get("failures") or []),
            "fold_other_fails": len(f.get("failures") or []),
        }
    # M2: a_ports_none loses its feed_link witness / records rc=0
    for label, mfn in (("delete", lambda l: l.pop("feed_link", None)),
                       ("rc0", lambda l: l.update(
                           feed_link={"rc": 0, "tries": 3}))):
        legs = copy.deepcopy(meas["filterchain_arm_r92_probe"]["legs"])
        mfn(legs["a_ports_none"])
        b = replay("filterchain_arm_r92_probe", legs, "base")
        f = replay("filterchain_arm_r92_probe", legs, "fold")
        muts[f"M2_ports_none_{label}"] = {
            "base_ports_none_fail": fails(b, "a_ports_none"),
            "fold_ports_none_fail": fails(f, "a_ports_none"),
        }
    # M3: inject an [E] line into the silent legs' load reply (and a control
    # on a non-silent leg)
    legs = copy.deepcopy(meas["filterchain_ir_r92_probe"]["legs"])
    for t in ("i_noconfig", "i_missing", "i_empty", "i_text", "i_dir"):
        legs[t]["load"]["load_text"] = (
            "load reply\n[E] impl_activate()] cannot create plugin\n")
    b = replay("filterchain_ir_r92_probe", legs, "base")
    f = replay("filterchain_ir_r92_probe", legs, "fold")
    muts["M3_i_star_Eline"] = {
        "base_silent_fails": [x for x in (b.get("failures") or [])
                              if "silent class is not silent" in x],
        "fold_silent_fails": [x for x in (f.get("failures") or [])
                              if "silent class is not silent" in x],
        "base_total": len(b.get("failures") or []),
        "fold_total": len(f.get("failures") or []),
    }
    legs = copy.deepcopy(meas["filterchain_ir_r92_probe"]["legs"])
    legs["i_2tap"]["load"]["load_text"] = (
        "load reply\n[E] impl_activate()] cannot create plugin\n")
    b = replay("filterchain_ir_r92_probe", legs, "base")
    f = replay("filterchain_ir_r92_probe", legs, "fold")
    muts["M3_control_i_2tap_Eline"] = {
        "base_fails": len(b.get("failures") or []),
        "fold_fails": len(f.get("failures") or []),
    }
    result["A2_mutations"] = muts

    # ---------------- Part B (gate differential) ----------------
    import shutil as shutil_mod
    b_out = {}
    cases = {
        "daemon_bad": ({"ok": False, "exit_code": 1, "killed_at_bound": False,
                        "wall_s": 12.5}, True),
        "daemon_bad_killed": ({"ok": False, "exit_code": None,
                               "killed_at_bound": True, "wall_s": 15.0},
                              True),
        "daemon_ok": ({"ok": True, "exit_code": 0, "killed_at_bound": False,
                       "wall_s": 0.02}, True),
    }
    for case, (daemon, tools_ok) in cases.items():
        for which, mod in (("base", mb), ("fold", mf)):
            orig_which = shutil_mod.which
            if not tools_ok:
                shutil_mod.which = lambda t: None
            else:
                shutil_mod.which = lambda t: f"/usr/bin/{t}"
            try:
                head = {"probe": "gate", "daemon": daemon, "contention": {},
                        "oracle_at_start": None, "foreign_r92a_nodes": [],
                        "inventory": {}, "loadavg": [0, 0, 0]}
                legs = copy.deepcopy(
                    meas["filterchain_arm_r92_probe"]["legs"])
                stub(mod, head, legs)
                e = mod.filterchain_arm_r92_probe()
                b_out.setdefault(case, {})[which] = {
                    "blocked": e.get("blocked"),
                    "failures": e.get("failures"),
                    "tools": e.get("tools"),
                    "keys": sorted(e.keys()),
                }
            finally:
                shutil_mod.which = orig_which
        b_out[case]["identical"] = (jdump(b_out[case]["base"]) ==
                                    jdump(b_out[case]["fold"]))
    # tools-missing case
    for which, mod in (("base", mb), ("fold", mf)):
        orig_which = shutil_mod.which
        shutil_mod.which = (lambda t: None if t == "pw-cli"
                            else f"/usr/bin/{t}")
        try:
            head = {"probe": "gate", "daemon": {"ok": True}, "contention": {},
                    "oracle_at_start": None, "foreign_r92a_nodes": [],
                    "inventory": {}, "loadavg": [0, 0, 0]}
            legs = copy.deepcopy(meas["filterchain_arm_r92_probe"]["legs"])
            stub(mod, head, legs)
            e = mod.filterchain_arm_r92_probe()
            b_out.setdefault("tools_missing", {})[which] = {
                "blocked": e.get("blocked"), "failures": e.get("failures"),
                "keys": sorted(e.keys())}
        finally:
            shutil_mod.which = orig_which
    b_out["tools_missing"]["identical"] = (
        jdump(b_out["tools_missing"]["base"]) ==
        jdump(b_out["tools_missing"]["fold"]))
    result["B_gates"] = b_out

    # ---------------- reachability census (fallback rows) ----------------
    cls = {}
    for run in RUNS:
        meas = load_receipt(run)
        c = {}

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "error_class" and v:
                        c[v] = c.get(v, 0) + 1
                    walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        for e in ENTRIES:
            walk(meas[e])
        cls[run] = c
    result["class_census"] = cls

    text = json.dumps(result, indent=1, sort_keys=True, default=str)
    if out_path:
        out_path.write_text(text + "\n")
    print(text[:4000])
    print("...")
    print("A_replay all identical:",
          all(v["entries_identical"] for v in a_out.values()
              for v in v.values()))
    print("C shift_ok all_equal:", c_ok)
    print("B gates identical:", {k: v.get("identical")
                                 for k, v in b_out.items()})


if __name__ == "__main__":
    main()
