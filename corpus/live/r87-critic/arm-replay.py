#!/usr/bin/env python3
"""r87-critic arm replay.

Slices the COMMITTED verdict block + its helpers VERBATIM out of
`git show d1e687b9:corpus/fixtures/measure_audio.py` and execs them
against (a) the two committed green receipts and (b) targeted mutations.

Re-derivation cases prove the arms are live; mutation cases hunt for
absorption (a mutation that PASSES is a finding).
"""
import json
import os
import re
import subprocess
import sys

ROOT = "/home/vgpnk/Projects/shokunin/audio-shokunin"
HERE = os.path.join(ROOT, "corpus/live/r87-critic")
COMMIT = "d1e687b9"
FIXTURE = "corpus/fixtures/measure_audio.py"

GREEN = [
    "20261016T070036115509Z-pwbind-r87",
    "20261016T070305393338Z-pwbind-r87",
]


def committed_text():
    return subprocess.run(["git", "show", f"{COMMIT}:{FIXTURE}"],
                          cwd=ROOT, capture_output=True, check=True).stdout.decode()


def extract_fn(src, name):
    lines = src.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"def {name}("))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("def "):
            end = j
            break
    return "\n".join(lines[start:end]).rstrip() + "\n"


def fn_bounds(src, name):
    lines = src.split("\n")
    start = next(i for i, ln in enumerate(lines) if ln.startswith(f"def {name}("))
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("def "):
            end = j
            break
    return lines, start, end


def extract_block(src, owner_fn, start_marker, end_marker):
    """Slice a marker-delimited block from INSIDE a named function."""
    lines, fs, fe = fn_bounds(src, owner_fn)
    s = next(i for i in range(fs, fe) if start_marker in lines[i])
    e = next(i for i in range(s, fe) if end_marker in lines[i])
    return "\n".join(lines[s:e + 1])


def build_ns():
    src = committed_text()
    ns = {"json": json, "os": os, "re": re}
    parts = {}
    for fn in ("_pwbind_r87_consumers", "_pwbind_r87_last_snap",
               "_pwbind_r87_expect"):
        parts[fn] = extract_fn(src, fn)
        exec(compile(parts[fn], f"<{fn}>", "exec"), ns)
    blk = extract_block(src, "pwbind_target_r87_entry",
                        "# ---------------- verdicts ----------------",
                        'entry["failures"] = failures')
    parts["_verdict_block"] = blk
    return ns, parts, blk


def run_block(ns, blk, legs, entry, src_foreign):
    """Exec the committed verdict block over a (possibly mutated) leg dict."""
    env = dict(ns)
    # the block re-reads the live default sink; in replay we feed it the
    # RECORDED value so the drift arm is exercised deterministically.
    env["_pwbind_r87_default_sink"] = lambda: entry.get(
        "default_sink_at_end", entry.get("default_sink_at_start"))
    env.update({
        "legs": legs,
        "entry": entry,
        "failures": [],
        "src": src_foreign,
        "NS": os.environ["PWBIND_R87_NS"],
        "NS2": os.environ["PWBIND_R87_NS2"],
        "DEF": entry.get("default_sink_at_start") or "<unreadable-default>",
        "PWBIND_R87_NS": os.environ["PWBIND_R87_NS"],
        "PWBIND_R87_NS2": os.environ["PWBIND_R87_NS2"],
        "PWBIND_R87_STALE_SERIAL": "98765432",
        "PWBIND_R87_BOGUS": "no_such_r87a",
    })
    body = "def _arm():\n" + "\n".join(
        ("    " + l if l.strip() else l) for l in blk.split("\n")) + "\n"
    exec(compile(body, "<verdict-block>", "exec"), env)
    env["_arm"]()
    return env["failures"]


def load_legs(run):
    p = os.path.join(ROOT, "corpus/live/runs", run, "measurements.json")
    d = json.load(open(p))
    ent = d["measurements"]["pwbind_target_r87_probe"]
    return ent["legs"], ent, ent.get("refs", {}).get("src")


def clone(legs):
    return json.loads(json.dumps(legs))


def set_consumers(legs, name, names):
    """Rewrite a leg so its edges_out produce exactly `names`."""
    leg = legs[name]
    snaps = leg.get("snaps") or []
    if not snaps:
        return
    keep = snaps[-1]
    leg["snaps"] = [keep]
    keep["edges_out"] = [{"in_node": n, "in_port_name": "playback_FL"}
                         for n in names]


def main():
    ns, parts, blk = build_ns()
    for k, v in parts.items():
        open(os.path.join(HERE, f"armfrag-{k.lstrip('_')}.py"), "w").write(v)

    results = {"rederive": [], "mutations": [], "absorption": []}
    NS = "r87a_ns_<PID>"
    NS2 = "r87a_ns2_<PID>"

    for run in GREEN:
        legs0, ent0, src0 = load_legs(run)
        pid = re.search(r"r87a_ns_(\d+)", ent0["sinks_gone"] and
                        next(iter(ent0["sinks_gone"])) or "").group(1)
        os.environ["PWBIND_R87_NS"] = f"r87a_ns_{pid}"
        os.environ["PWBIND_R87_NS2"] = f"r87a_ns2_{pid}"
        n, n2 = os.environ["PWBIND_R87_NS"], os.environ["PWBIND_R87_NS2"]
        DEF = ent0["default_sink_at_start"]

        legs = clone(legs0)
        entry = {"default_sink_at_start": DEF,
                 "default_sink_at_end": ent0.get("default_sink_at_end", DEF)}
        f = run_block(ns, blk, legs, entry, src0)
        results["rederive"].append({
            "run": run, "pid": pid, "def": DEF,
            "n_failures": len(f), "failures": f,
            "verdict": "PASS" if not f else "FAIL",
            "n_legs": len(legs),
        })

        # ---------- mutation battery ----------
        def mut(label, fn, expect_red=True):
            lg = clone(legs0)
            en = {"default_sink_at_start": DEF,
                  "default_sink_at_end": ent0.get("default_sink_at_end", DEF)}
            fn(lg, en)
            fl = run_block(ns, blk, lg, en, src0)
            results["mutations"].append({
                "run": run, "label": label, "n_failures": len(fl),
                "failures": fl[:3],
                "verdict": "PASS" if not fl else "FAIL",
                "as_designed": (not fl) != expect_red,
            })

        mut("M1 p_nt_vs_flag lands NS2 (flag loses to node.target — the "
            "scout's reversed law)",
            lambda lg, en: set_consumers(lg, "p_nt_vs_flag", [n2]))
        mut("M2 p_three lands NS (prop loses to flag)",
            lambda lg, en: set_consumers(lg, "p_three", [n]))
        mut("M3 p_pb1 lands NS (garbage prop falls through to valid flag)",
            lambda lg, en: set_consumers(lg, "p_pb1", [n]))
        mut("M4 p_nt_garbage lands NS2 (garbage flag falls through to "
            "node.target)",
            lambda lg, en: set_consumers(lg, "p_nt_garbage", [n2]))
        mut("M5 p_objid lands NS (object.id resolves)",
            lambda lg, en: set_consumers(lg, "p_objid", [n]))
        mut("M6 p_prop_objid lands NS (object.id resolves on the prop path)",
            lambda lg, en: set_consumers(lg, "p_prop_objid", [n]))
        mut("M7 p_serial_stale lands NS (stale serial resolves)",
            lambda lg, en: set_consumers(lg, "p_serial_stale", [n]))
        mut("M8 p_env_vs_prop lands NS2 (env loses to -P)",
            lambda lg, en: set_consumers(lg, "p_env_vs_prop", [n2]))
        mut("M9 p_env_garbage lands NS (garbage env falls through)",
            lambda lg, en: set_consumers(lg, "p_env_garbage", [n]))
        mut("M10 p_coll lands NS2 (name collision resolves to the stream)",
            lambda lg, en: set_consumers(lg, "p_coll", [n2]))
        mut("M11 p_own gains a second consumer (cross-link)",
            lambda lg, en: set_consumers(lg, "p_own", [n, n2]))
        mut("M12 default sink drifts mid-entry",
            lambda lg, en: en.update(default_sink_at_end="some_other_sink.99"))
        mut("M13 p_zero gains a consumer",
            lambda lg, en: set_consumers(lg, "p_zero", [n]))
        mut("M14 p_zero node never present",
            lambda lg, en: lg["p_zero"].update(snaps=[]))
        mut("M15 p_mon lands NS (the .monitor suffix resolves as a name)",
            lambda lg, en: set_consumers(lg, "p_mon", [n]))
        mut("M16 p_src_name lands NS (wrong-class source resolves)",
            lambda lg, en: set_consumers(lg, "p_src_name", [n]))
        mut("M17 p_mediarole lands NS (role prop routes)",
            lambda lg, en: set_consumers(lg, "p_mediarole", [n]))
        mut("M18 p_empty lands NS (empty --target resolves)",
            lambda lg, en: set_consumers(lg, "p_empty", [n]))
        mut("M19 p_nt_rev lands NS (flag loses to node.target, reverse leg)",
            lambda lg, en: set_consumers(lg, "p_nt_rev", [n]))
        mut("M20 p_noauto gains a consumer (autoconnect=false ignored)",
            lambda lg, en: set_consumers(lg, "p_noauto", [n]))
        mut("M21 p_cat lands DEF (pw-cat does not share the lattice)",
            lambda lg, en: set_consumers(lg, "p_cat", [DEF]))
        mut("M22 p_prop_twice lands NS (first -P wins, not last)",
            lambda lg, en: set_consumers(lg, "p_prop_twice", [n]))
        mut("M23 p_env_nobrace lands DEF (brace form only)",
            lambda lg, en: set_consumers(lg, "p_env_nobrace", [DEF]))

        # ---------- absorption hunt (a PASS here is a finding) ----------
        def absorb(label, fn, note):
            lg = clone(legs0)
            en = {"default_sink_at_start": DEF,
                  "default_sink_at_end": ent0.get("default_sink_at_end", DEF)}
            fn(lg, en)
            fl = run_block(ns, blk, lg, en, src0)
            results["absorption"].append({
                "run": run, "label": label, "n_failures": len(fl),
                "failures": fl[:3],
                "verdict": "PASS" if not fl else "FAIL",
                "absorbing": not fl,
                "note": note,
            })

        absorb("A1 p_own leg has NO snaps at all (spawn failure)",
               lambda lg, en: lg["p_own"].update(snaps=[], consumers=[]),
               "does an unspawned leg read as 'no consumers' and get "
               "absorbed by a want=[] arm? want=[NS] here")
        def _a2(lg, en):
            for s in lg["p_coll"]["snaps"]:
                if s.get("edges_out"):
                    s["edges_out"] = [{"in_node": e.get("in_node")}
                                      for e in s["edges_out"]]
        absorb("A2 p_coll edges carry no in_port_name", _a2,
               "is the non-playback-port arm vacuous when ports are absent?")
        absorb("A3 p_zero present at first snap, gone at last, no consumers",
               lambda lg, en: lg["p_zero"].update(
                   snaps=[{"present": True, "edges_out": []},
                          {"present": False, "edges_out": []}]),
               "does the presence arm accept a node that vanished?")
        absorb("A4 p_own consumers transiently wrong at first snap only",
               lambda lg, en: lg["p_own"].update(snaps=[
                   {"present": True, "edges_out": [{"in_node": n2}]},
                   {"present": True, "edges_out": [{"in_node": n}]}]),
               "union-across-snaps should catch a transient mis-route")
        absorb("A5 p_own edges_out entries with falsy in_node",
               lambda lg, en: lg["p_own"].update(snaps=[
                   {"present": True,
                    "edges_out": [{"in_node": ""}, {"in_node": n}]}]),
               "falsy in_node silently dropped — does a dead edge count?")
        absorb("A6 p_zero HAS a real link but its peer name did not "
               "resolve (in_node=None)",
               lambda lg, en: lg["p_zero"].update(snaps=[
                   {"present": True,
                    "edges_out": [{"out_node": n,
                                   "in_node": None,
                                   "in_port_name": "playback_FL"}]}]),
               "the no-link arm cannot distinguish 'no link' from 'a link "
               "whose peer node id missed the graph snapshot'")
        absorb("A7 p_noauto HAS a real link, peer unresolved",
               lambda lg, en: lg["p_noauto"].update(snaps=[
                   {"present": True,
                    "edges_out": [{"out_node": n,
                                   "in_node": None,
                                   "in_port_name": "playback_FL"}]}]),
               "same channel on the autoconnect=false switch")
        absorb("A8 p_zero_prop HAS a real link, peer unresolved",
               lambda lg, en: lg["p_zero_prop"].update(snaps=[
                   {"present": True,
                    "edges_out": [{"out_node": n,
                                   "in_node": None,
                                   "in_port_name": "playback_FL"}]}]),
               "same channel on the 0-beats-target.object switch")

    json.dump(results, open(os.path.join(HERE, "arm-replay.json"), "w"),
              indent=1, sort_keys=True)

    lines = []
    lines.append("== RE-DERIVATION on committed receipts ==")
    for r in results["rederive"]:
        lines.append(f"  {r['run']} pid={r['pid']} legs={r['n_legs']} "
                     f"failures={r['n_failures']} {r['verdict']}")
        for x in r["failures"]:
            lines.append(f"      ! {x}")
    lines.append("")
    lines.append("== MUTATION BATTERY (expect RED) ==")
    nbad = 0
    for r in results["mutations"]:
        flag = "" if r["as_designed"] else "   <<< NOT AS DESIGNED"
        if not r["as_designed"]:
            nbad += 1
        lines.append(f"  {r['verdict']:4s} nf={r['n_failures']:<2} {r['label']}{flag}")
        for x in r["failures"]:
            lines.append(f"        - {x}")
    lines.append(f"  ({nbad} not-as-designed)")
    lines.append("")
    lines.append("== ABSORPTION HUNT (a PASS = a finding) ==")
    for r in results["absorption"]:
        lines.append(f"  {r['verdict']:4s} nf={r['n_failures']:<2} "
                     f"absorbing={r['absorbing']!s:5s} {r['label']}")
        lines.append(f"        note: {r['note']}")
        for x in r["failures"][:2]:
            lines.append(f"        - {x}")
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "arm-replay.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
