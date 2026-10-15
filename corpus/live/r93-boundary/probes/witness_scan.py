#!/usr/bin/env python3
"""r93-boundary: independent libebur128 witness scan over a receipt's captures.

For every leg with a ref_path/post_path in the given receipt JSON, run the
installed-libebur128 witness (probes/ebur_witness2) in `full` and `trim` mode
and store the values next to the plugin/own-reference numbers.

Usage: witness_scan.py <receipt.json> [out.json]
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ebur_witness2")


def witness(path, mode):
    r = subprocess.run([WIT, path, mode], capture_output=True, text=True, timeout=60)
    m = re.search(r"I=(-?[\d.]+)", r.stdout)
    return {"I": float(m.group(1)) if m else None, "rc": r.returncode}


def main():
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        HERE, "receipts", "witness_%s.json" % os.path.basename(src).replace(".json", ""))
    with open(src) as f:
        d = json.load(f)
    rows = []
    for r in d.get("legs", []):
        row = {"tag": r.get("tag"), "arm": r.get("arm") or r.get("cfg"),
               "readout": r.get("readout"), "plugin_plateau": (r.get("stats") or {}).get("plateau")}
        for key in ("ref_path", "post_path"):
            p = r.get(key)
            if not p or not os.path.exists(p):
                continue
            sz = os.path.getsize(p)
            row[key] = {"size": sz}
            if sz < 100000:
                row[key]["skipped"] = "file smaller than a leg's capture (mid-write)"
                continue
            row[key]["libebur128"] = {m: witness(p, m) for m in ("full", "trim")}
            if r.get("ref_global") and key == "ref_path":
                row[key]["scout_ref_global"] = r["ref_global"].get("lufs")
        if row.get("plugin_plateau") is not None and row.get("ref_path", {}).get("libebur128"):
            for m in ("full", "trim"):
                v = row["ref_path"]["libebur128"][m]["I"]
                if v is not None:
                    row["offset_plugin_minus_lib_%s" % m] = round(row["plugin_plateau"] - v, 6)
        rows.append(row)
    res = {"stage": "witness_scan", "source": src, "n": len(rows), "rows": rows}
    with open(out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True)
    for r in rows:
        print("%-26s plugin=%-11s lib_full=%-11s lib_trim=%-11s off_full=%-9s off_trim=%s" % (
            r.get("tag"), r.get("plugin_plateau"),
            (r.get("ref_path", {}).get("libebur128", {}).get("full", {}) or {}).get("I"),
            (r.get("ref_path", {}).get("libebur128", {}).get("trim", {}) or {}).get("I"),
            r.get("offset_plugin_minus_lib_full"), r.get("offset_plugin_minus_lib_trim")))
    print("-> %s" % out)


if __name__ == "__main__":
    main()
