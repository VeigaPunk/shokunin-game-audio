#!/usr/bin/env python3
"""r89 RE-VERIFY census summary: committed-bytes receipts vs the mutant runs,
law-class census, and custody checks (unload index verification)."""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE
COMMITTED = ["r89v1", "r89v2", "r89v3", "cot-r1-t2", "cot-r1-t3",
             "cot-r2-t2", "cot-r2-t3", "held-foreign"]
MUTANTS = ["mut-sigreset-nohup", "mut-footglobal-held"]


def laws_for(rids):
    args = [sys.executable, str(RUNS / "laws2.py")]
    args += [str(RUNS / f"{r}.receipt.json") for r in rids]
    p = subprocess.run(args, capture_output=True, text=True)
    lines = [ln for ln in p.stdout.splitlines() if ln.startswith("LAW ")]
    return lines


def census(rids, label):
    lines = laws_for(rids)
    n = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    base = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    radd = {"PASS": 0, "FAIL": 0, "BLOCKED": 0}
    fails = []
    blocks = []
    for ln in lines:
        parts = ln.split()
        # LAW <rid> <law name...> <VERDICT> <detail>
        verdict = [p for p in parts if p in n]
        v = verdict[-1] if verdict else None
        name = ln.split(" ", 3)[2]
        if v:
            n[v] += 1
            (radd if name.startswith("R0") or name.startswith("R1") else
             base)[v] += 1
            if v == "FAIL":
                fails.append(ln)
            if v == "BLOCKED":
                blocks.append(ln)
    total = sum(n.values())
    print(f"== {label}: receipts={len(rids)} cells={total} "
          f"PASS={n['PASS']} FAIL={n['FAIL']} BLOCKED={n['BLOCKED']}")
    print(f"   base106: {sum(base.values())} cells PASS={base['PASS']} "
          f"FAIL={base['FAIL']} BLOCKED={base['BLOCKED']}")
    print(f"   R-add  : {sum(radd.values())} cells PASS={radd['PASS']} "
          f"FAIL={radd['FAIL']} BLOCKED={radd['BLOCKED']}")
    for ln in fails:
        print("   FAIL:", ln[:200])
    return n


def custody(rids):
    print("== custody (unload index verification, sinks_gone, own_nodes):")
    bad = 0
    for r in rids:
        d = json.loads((RUNS / f"{r}.receipt.json").read_text())
        for e, ent in d["measurements"].items():
            if not e.startswith("pwprof_"):
                continue
            un = ent.get("unloads") or {}
            for k, v in un.items():
                if not (v.get("verified_index") == v.get("captured") and
                        v.get("field") == "sink_name" and
                        v.get("value") == k and v.get("exit_code") == 0):
                    bad += 1
                    print(f"   BAD unload {r} {e} {k}: {v}")
            if not all((ent.get("sinks_gone") or {}).values()):
                bad += 1
                print(f"   BAD sinks_gone {r} {e}")
            if ent.get("own_nodes_after") != []:
                bad += 1
                print(f"   BAD own_nodes_after {r} {e}")
    print(f"   {len(rids)} receipts × 4 entries: violations={bad}")


def class_matrix(rids, label):
    print(f"== class arms ({label}):")
    for r in rids:
        d = json.loads((RUNS / f"{r}.receipt.json").read_text())
        m = d["measurements"]
        g = m["pwprof_gate_r89_probe"]["legs"]["g_hup"]
        x = m["pwprof_xw_r89_probe"]["legs"]
        cnt = [len(m[e]["legs"]) for e in
               ("pwprof_gate_r89_probe", "pwprof_oart_r89_probe",
                "pwprof_schema_r89_probe", "pwprof_xw_r89_probe")]
        f = {e: m[e]["failures"] for e in m
             if isinstance(m[e], dict) and m[e].get("failures")}
        print(f"   {r:20s} census={'/'.join(map(str, cnt))}"
              f"={sum(cnt)} g_hup rc={g.get('exit_code')}"
              f"@{g.get('wall_s')}s x_foot="
              f"{'GREEN own=' + str(x['x_foot'].get('own_clients')) if x['x_foot'].get('own_clients') else 'BLOCKED'}"
              f" x_top="
              f"{'GREEN med=' + str(x['x_top'].get('top_wait_med')) + '/' + str(x['x_top'].get('top_busy_med')) if x['x_top'].get('own_row') else 'BLOCKED'} "
              f"failures={f}")


if __name__ == "__main__":
    census(COMMITTED, "COMMITTED BYTES 5755be5b")
    census(MUTANTS, "REVERT-THE-FIX MUTANTS")
    class_matrix(COMMITTED, "committed")
    class_matrix(MUTANTS, "mutants")
    custody(COMMITTED + MUTANTS)
