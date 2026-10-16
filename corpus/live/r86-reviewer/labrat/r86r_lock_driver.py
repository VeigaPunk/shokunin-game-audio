#!/usr/bin/env python3
"""r86 reviewer — driver for the r84-F1 fold probe (r86r_lock_probe.py).

Produces lock-probe.json: resolved lock paths per (module ROOT, TMPDIR,
lockfn) plus three executed flock serialization experiments:
  A. r86 lock, one ROOT, two different TMPDIRs   -> must serialize
  B. r85 lock, one ROOT, two different TMPDIRs   -> must NOT serialize
  C. r86 lock, two different ROOTs, same TMPDIR  -> must NOT serialize
     (the scope limit of a ROOT-relative fixed path)
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REVIEW = os.path.dirname(HERE)
PROBE = os.path.join(HERE, "r86r_lock_probe.py")
TREE1 = os.path.join(REVIEW, "tree", "corpus", "fixtures", "measure_audio.py")
TMP1 = "/home/vgpnk/Projects/shokunin/tmp"
TMP2 = os.path.join(TMP1, "r86r-alt-tmp")
TREE2 = os.path.join(REVIEW, "tree2", "corpus", "fixtures", "measure_audio.py")
PY = sys.executable


def run(cmd, env=None):
    e = dict(os.environ)
    e.update(env or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=e)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def resolve(module, tmpdir, lockfn):
    rc, out, err = run([PY, PROBE, "resolve", module, tmpdir, lockfn])
    if rc != 0:
        return {"error": err[-300:], "rc": rc}
    return json.loads(out)


def serialization(module_holder, module_waiter, lockfn, label,
                  tmp_holder, tmp_waiter, hold_s=5.0, gap_s=1.5):
    wit = os.path.join(HERE, f"witness-{label}.json")
    if os.path.exists(wit):
        os.remove(wit)
    ph = subprocess.Popen(
        [PY, PROBE, "hold", module_holder, lockfn, str(hold_s)],
        env={**os.environ, "TMPDIR": tmp_holder, "WITNESS": wit},
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(gap_s)
    t0 = time.time()
    rc, out, err = run([PY, PROBE, "wait", module_waiter, lockfn],
                       env={"TMPDIR": tmp_waiter})
    wall = time.time() - t0
    ho, he = ph.communicate()
    res = {"label": label, "lockfn": lockfn,
           "holder_module": module_holder, "waiter_module": module_waiter,
           "tmp_holder": tmp_holder, "tmp_waiter": tmp_waiter,
           "gap_s": gap_s, "hold_s": hold_s, "waiter_wall_s": round(wall, 3),
           "holder_rc": ph.returncode, "waiter_rc": rc}
    try:
        res["waiter"] = json.loads(out)
    except ValueError:
        res["waiter_raw"] = (out, err)
    if os.path.exists(wit):
        with open(wit) as fh:
            res["holder"] = json.load(fh)
    return res


def main():
    os.makedirs(TMP2, exist_ok=True)
    os.makedirs(os.path.dirname(TREE2), exist_ok=True)
    os.makedirs(os.path.join(REVIEW, "tree2", "corpus", "live"), exist_ok=True)
    if not os.path.exists(TREE2):
        shutil.copy2(TREE1, TREE2)
    out = {"module_tree1": TREE1, "module_tree2": TREE2,
           "tmp1": TMP1, "tmp2": TMP2, "resolved": [], "runs": []}
    for lockfn in ("r86", "r85"):
        for module, tag in ((TREE1, "tree1"), (TREE2, "tree2")):
            for tmpdir in (TMP1, TMP2):
                r = resolve(module, tmpdir, lockfn)
                r.update({"lockfn": lockfn, "module_tag": tag,
                          "tmpdir_tag": "tmp1" if tmpdir == TMP1
                          else "tmp2"})
                out["resolved"].append(r)
    out["runs"].append(serialization(TREE1, TREE1, "r86", "A_r86_same_root",
                                     TMP1, TMP2))
    out["runs"].append(serialization(TREE1, TREE1, "r85", "B_r85_same_root",
                                     TMP1, TMP2))
    out["runs"].append(serialization(TREE1, TREE2, "r86", "C_r86_cross_root",
                                     TMP1, TMP1))
    with open(os.path.join(HERE, "lock-probe.json"), "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
