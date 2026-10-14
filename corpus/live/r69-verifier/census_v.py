#!/usr/bin/env python3
"""r69-verifier census: same method as r69-author/census_check_rows.py but
parameterized over a receipt set: (a) the committed set at 7b8d423 (pre-r69),
(b) HEAD (post-integration). Receipts read from the working tree — commit
30bb86d is add-only under corpus/live/runs so pre-commit paths are unchanged.
Never writes into r69-author; outputs to this dir."""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "/home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r69-author")
from check_table import parse_rows, first_match

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
CORPUS = ROOT / "corpus"


def census(receipt_rels):
    rows = parse_rows()
    live = [r for r in rows if not r["compiled_out"]]
    file_hit, recorded = {}, {}
    n_rec = n_ent = 0
    for rel in receipt_rels:
        if not rel.endswith("measurements.json"):
            continue
        n_rec += 1
        try:
            doc = json.loads((ROOT / rel).read_text())
        except Exception:
            continue
        for name, entry in (doc.get("measurements") or {}).items():
            if not isinstance(entry, dict) or "path" not in entry:
                continue
            n_ent += 1
            path = entry["path"]
            if entry.get("sox_detected_format") is not None:
                recorded.setdefault(path, set()).add(entry["sox_detected_format"])
            for arm in (entry.get("transport_axis") or {}).values():
                if isinstance(arm, dict) and arm.get("sox_detected_format") is not None:
                    recorded.setdefault(path, set()).add(arm["sox_detected_format"])
            if path not in file_hit:
                f = CORPUS / path
                data = f.read_bytes() if f.exists() else None
                if data is None:
                    file_hit[path] = "missing"
                    continue
                ext = f.suffix[1:] if "." in f.name else None
                hit = first_match(data, ext, rows)
                file_hit[path] = hit[0] if hit else None
    rows_hit = {}
    for path, h in file_hit.items():
        if isinstance(h, int):
            rows_hit.setdefault(h, []).append(path)
    mismatches = []
    for path, types in recorded.items():
        h = file_hit.get(path)
        evaltype = rows[h]["type"] if isinstance(h, int) else None
        for t in types:
            if t != evaltype:
                mismatches.append((path, t, evaltype))
    missing = [p for p, h in file_hit.items() if h == "missing"]
    return {"receipts": n_rec, "entries": n_ent, "inputs": len(file_hit),
            "missing": missing,
            "hit": {i: {"line": rows[i]["line"], "type": rows[i]["type"],
                        "n": len(v), "ex": sorted(v)[:3]}
                    for i, v in sorted(rows_hit.items())},
            "mismatches": mismatches,
            "live": len(live), "total": len(rows)}


def ls_tree(commit):
    return subprocess.run(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only",
                           commit, "corpus/live/runs"],
                          capture_output=True, text=True, check=True).stdout.split()


def ls_head():
    return subprocess.run(["git", "-C", str(ROOT), "ls-files", "corpus/live/runs"],
                          capture_output=True, text=True, check=True).stdout.split()


def main():
    rows = parse_rows()
    print("rows parsed:", len(rows),
          "| ext_gated:", [(i, r["line"], r["type"], r.get("ext_needed"))
                          for i, r in enumerate(rows) if r.get("ext_gated")],
          "| compiled_out:", [(i, r["line"], r["type"])
                              for i, r in enumerate(rows) if r["compiled_out"]])
    data = (ROOT / "corpus/live/round-69/extsuffix_nomatch.snd").read_bytes()
    for ext in ("wav", "bin", "txw", "f32", "snd", "au", None):
        h = first_match(data, ext, rows)
        i = h[0] if h else None
        print(f"first_match(member,{ext!r}) ->", None if i is None else (i, rows[i]["line"], rows[i]["type"], h))
    pre = census(ls_tree("7b8d423"))
    head = census(ls_head())
    out = {"pre_7b8d423": pre, "head": head}
    (Path(__file__).parent / "census-v.json").write_text(json.dumps(out, indent=1) + "\n")
    for tag, r in (("pre(7b8d423)", pre), ("HEAD", head)):
        print(f"\n== {tag}: receipts={r['receipts']} entries={r['entries']} "
              f"inputs={r['inputs']} missing={len(r['missing'])} live={r['live']}")
        print("   hit rows:", {i: (v['line'], v['type'], v['n']) for i, v in r['hit'].items()})
        print("   rows_hit count:", len(r['hit']), " dead:", r['live'] - len(r['hit']),
              " recorded-vs-eval mismatches:", len(r['mismatches']), r['mismatches'][:3])
        if r['missing']:
            print("   missing inputs:", r['missing'][:5])
    return 0


if __name__ == "__main__":
    sys.exit(main())
