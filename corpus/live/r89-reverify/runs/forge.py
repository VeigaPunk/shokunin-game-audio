#!/usr/bin/env python3
"""r89 RE-VERIFY forgery / mutation spot-check on the signature gate.

The law re-derivation (laws2.py) reads the RECEIPT fields, never the
fixture's own `failures` list (except C02), so it must catch the forgeries
that are catchable from the recorded fields — and the re-verifier must NAME
the ones that are not (a fully self-consistent receipt rewrite is
undetectable at receipt level; the live batteries + the sha-pinned normal
receipt are the ground truth).

Bases are real receipts where the class was genuinely NOT green:
  * `r89-verifier/runs/r89v1.receipt.json` — pre-fix nohup: g_hup rc -9
    wall 9.03 (the launcher-inheritance red).
  * `r89-verifier/runs/cot1.receipt.json`   — pre-fix: x_top 0.0/0.0 row
    false-FAIL, fixture failures list non-empty.
  * `r89-reverify/runs/r89v3.receipt.json`  — post-fix: x_foot
    coverage_blocked (own client not enumerated).

Cases:
  P1 signature pin : forge the canonical `normal` receipt -> sha256 moves
                     off the canonical pin `8e8cdad6…` -> CAUGHT by pin.
  F1 g_hup rc      : rc -9 -> -1, wall 9.03 kept -> R03 (bounded at the
                     sig point) CAUGHT; G04 alone MISSED (rc+parse both
                     satisfy the arm) — disclosed.
  F2 x_foot        : own_clients [] -> [pid], coverage list KEPT -> C03
                     reports BLOCKED (never silent green) -> CAUGHT-partial;
                     coverage list POPPED -> MISSED at receipt level,
                     disclosed (compensated by mutation M2 + held-foreign
                     live run).
  F3 x_top         : 0.0/0.0 row -> fabricated real row, medians in band,
                     fixture failures KEPT -> C02 CAUGHT; failures POPPED ->
                     MISSED at receipt level, disclosed.
  F4 census        : drop one leg key -> C01b/R01 CAUGHT.
"""
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAWS = HERE / "laws2.py"
OUT = HERE / "forgery"
CANON_PIN = ("8e8cdad6cc3c356d07c463498f4759b8d73e73935cf591d117732"
             "f09ffaffb1b")


def run_laws(path):
    p = subprocess.run([sys.executable, str(LAWS), str(path)],
                       capture_output=True, text=True)
    fails = [ln for ln in p.stdout.splitlines() if " FAIL " in ln]
    blks = [ln for ln in p.stdout.splitlines() if " BLOCKED " in ln]
    return p.returncode, fails, blks


def save(name, d):
    fp = OUT / f"forged-{name}.measurements.json"
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n")
    return fp


def report(name, expect, rc, fails, blks, law=""):
    if expect == "CAUGHT":
        hit = [f for f in fails if law in f]
        ok = rc == 1 and bool(hit)
    elif expect == "CAUGHT-PARTIAL":
        hit = [b for b in blks if law in b]
        ok = bool(hit)
    elif expect == "MISSED":
        ok = rc == 0 and not fails
    else:  # MISSED-G04
        ok = all(law not in f for f in fails)
    print(f"FORGE {name}: expect={expect} rc={rc} n_fail={len(fails)} "
          f"n_blocked={len(blks)} -> {'as-predicted' if ok else 'SURPRISE'}")
    for ln in (fails + blks)[:3]:
        print(f"    {ln[:220]}")
    return ok


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    vpre, cotpre, v3post = (Path(p) for p in sys.argv[1:4])
    all_ok = True

    # ---------- P1: the canonical signature pin ----------
    nd = json.loads(Path(sys.argv[4]).read_text()) if len(sys.argv) > 4 \
        else None
    if nd is not None:
        nd["thresholds"]["rate_hz"] = 48001          # single-byte-class forge
        fp = save("normal-pin", nd)
        sha = hashlib.sha256(fp.read_bytes()).hexdigest()
        caught = sha != CANON_PIN
        print(f"FORGE normal-pin: sha={sha[:16]}… canonical={CANON_PIN[:16]}… "
              f"-> {'CAUGHT' if caught else 'MISSED'} (signature gate)")
        all_ok &= caught

    # ---------- F1: g_hup rc -9 -> -1 (pre-fix nohup receipt) ----------
    d = json.loads(vpre.read_text())
    g = d["measurements"]["pwprof_gate_r89_probe"]["legs"]["g_hup"]
    print(f"F1 base: g_hup rc={g.get('exit_code')} wall={g.get('wall_s')} "
          f"bytes={g.get('stdout_bytes')}")
    d1 = copy.deepcopy(d)
    d1["measurements"]["pwprof_gate_r89_probe"]["legs"]["g_hup"][
        "exit_code"] = -1
    rc, fails, blks = run_laws(save("g_hup", d1))
    all_ok &= report("g_hup", "CAUGHT", rc, fails, blks,
                    "R03 g_hup")
    all_ok &= report("g_hup-G04-alone", "MISSED-G04", rc, fails, blks,
                    "G04 g_hup")

    # ---------- F2: x_foot coverage_blocked -> forged own client ----------
    d = json.loads(v3post.read_text())
    xf = d["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_foot"]
    print(f"F2 base: own_clients={xf.get('own_clients')} "
          f"pwprof_during={xf.get('pwprof_during')}")
    d2 = copy.deepcopy(d)                      # partial: leg only
    xf2 = d2["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_foot"]
    xf2["own_clients"] = [xf2.get("own_pid")]
    xf2["own_objects"] = []
    rc, fails, blks = run_laws(save("x_foot-partial", d2))
    all_ok &= report("x_foot-partial", "CAUGHT-PARTIAL", rc, fails, blks,
                    "x_foot")
    d3 = copy.deepcopy(d2)                     # full: coverage list popped
    for e in d3["measurements"].values():
        if isinstance(e, dict):
            e.pop("coverage_blocked", None)
    rc, fails, blks = run_laws(save("x_foot-full", d3))
    all_ok &= report("x_foot-full", "MISSED", rc, fails, blks)

    # ---------- F3: x_top 0.0/0.0 -> forged real row ----------
    d = json.loads(cotpre.read_text())
    xt = d["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_top"]
    print(f"F3 base: own_row={json.dumps(xt.get('own_row'))} "
          f"failures={d['measurements']['pwprof_xw_r89_probe'].get('failures')}")
    row = {"status": "R", "id": 44, "quant": 2048, "rate": 48000,
           "wait": "3.0us", "busy": "3.0us", "wait_us": 3.0, "busy_us": 3.0}

    def forge_top(dd):
        l = dd["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_top"]
        l["own_row"] = row
        l["real_own_rows"] = [row]
        l["transient_own_rows"] = 0
        l["top_wait_med"] = 3.0
        l["top_busy_med"] = 3.0
        l["prof_wait_us_med"] = 3.0
        l["prof_busy_us_med"] = 3.0
    d4 = copy.deepcopy(d)                      # partial: leg only
    forge_top(d4)
    rc, fails, blks = run_laws(save("x_top-partial", d4))
    all_ok &= report("x_top-partial", "CAUGHT", rc, fails, blks,
                    "C02 pwprof_xw_r89_probe failures")
    d5 = copy.deepcopy(d4)                     # full: failures list cleared
    for e in d5["measurements"].values():
        if isinstance(e, dict):
            e.pop("failures", None)
            e["failures"] = []
    rc, fails, blks = run_laws(save("x_top-full", d5))
    all_ok &= report("x_top-full", "MISSED", rc, fails, blks)

    # ---------- F4: leg census ----------
    d6 = copy.deepcopy(json.loads(v3post.read_text()))
    del d6["measurements"]["pwprof_xw_r89_probe"]["legs"]["x_link"]
    rc, fails, blks = run_laws(save("census", d6))
    all_ok &= report("census", "CAUGHT", rc, fails, blks,
                    "C01b leg census")

    print(f"FORGERY SPOT-CHECK: {'all predictions held' if all_ok else 'SURPRISE(S) — inspect'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
