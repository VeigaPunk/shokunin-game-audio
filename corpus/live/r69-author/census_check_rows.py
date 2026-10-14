#!/usr/bin/env python3
"""r69 dead-CHECK-row census: which rows of the SoX_ng auto_detect CHECK
table (corpus/live/r64-reviewer/r64rev-formats.c, == upstream 14.8.0.1) have
EVER been first-match across all committed receipts.

Method: every committed receipt under corpus/live/runs/*/measurements.json
(git ls-files) contributes measurement entries; each entry's `path` names
the input file. For each distinct input file we evaluate the full ordered
CHECK table in-source (check_table.parse_rows / first_match) with the file's
own filename extension (the ext lsx_find_file_extension would return), so
each file yields exactly one first-match row index (or none -> post-table).
rows_hit = row indices observed as first-match; rows_dead = live rows never
first-match. Receipts that explicitly record `sox_detected_format` are
cross-checked: recorded type must equal the evaluated row's type.

Output: census JSON + TSV printed to stdout.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_table import parse_rows, first_match

ROOT = Path(__file__).resolve().parents[3]          # .../audio-shokunin
CORPUS = ROOT / "corpus"
RUNS_LS = subprocess.run(["git", "-C", str(ROOT), "ls-files", "corpus/live/runs"],
                         capture_output=True, text=True, check=True).stdout.split()


def main():
    rows = parse_rows()
    live = [r for r in rows if not r["compiled_out"]]
    file_hit = {}          # relpath -> (row_index or None)
    recorded = {}          # relpath -> set of recorded detected types
    receipt_count = 0
    entry_count = 0
    for rel in RUNS_LS:
        if not rel.endswith("measurements.json"):
            continue
        receipt_count += 1
        try:
            doc = json.loads((ROOT / rel).read_text())
        except Exception:
            continue
        for name, entry in (doc.get("measurements") or {}).items():
            if not isinstance(entry, dict) or "path" not in entry:
                continue
            entry_count += 1
            path = entry["path"]
            if entry.get("sox_detected_format") is not None:
                recorded.setdefault(path, set()).add(entry["sox_detected_format"])
            # transport arms additionally record per-arm detections
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
    missing = [p for p, h in file_hit.items() if h == "missing"]
    for path, h in file_hit.items():
        if isinstance(h, int):
            rows_hit.setdefault(h, []).append(path)
    hit_idx = set(rows_hit)
    dead = [{"row": i, "line": r["line"], "type": r["type"],
             "d1": r["d1"].hex(), "at": r["p1"]}
            for i, r in enumerate(rows) if not r["compiled_out"] and i not in hit_idx]
    # cross-check: recorded detections vs evaluated first-match types
    mismatches = []
    for path, types in recorded.items():
        h = file_hit.get(path)
        evaltype = rows[h]["type"] if isinstance(h, int) else None
        for t in types:
            if t != evaltype:
                mismatches.append((path, t, evaltype))
    out = {
        "check_rows_total": len(rows),
        "check_rows_live": len(live),
        "check_rows_compiled_out": sum(r["compiled_out"] for r in rows),
        "compiled_out": [{"row": i, "line": r["line"], "type": r["type"]}
                         for i, r in enumerate(rows) if r["compiled_out"]],
        "ext_gated": [{"row": i, "line": r["line"], "type": r["type"]}
                      for i, r in enumerate(rows) if r["ext_gated"]],
        "receipts_scanned": receipt_count,
        "measurement_entries": entry_count,
        "distinct_input_files": len(file_hit),
        "missing_input_files": missing,
        "recorded_vs_evaluated_mismatches": mismatches,
        "rows_hit": [{"row": i, "line": rows[i]["line"], "type": rows[i]["type"],
                      "n_inputs": len(rows_hit[i]),
                      "example": sorted(rows_hit[i])[:4]}
                     for i in sorted(hit_idx)],
        "rows_dead": dead,
    }
    (Path(__file__).parent / "census-r69.json").write_text(
        json.dumps(out, indent=1) + "\n")
    print(f"rows total {out['check_rows_total']} (live {out['check_rows_live']}, "
          f"compiled-out {out['check_rows_compiled_out']})")
    print(f"receipts {receipt_count}, entries {entry_count}, inputs {len(file_hit)}, missing {len(missing)}")
    print(f"rows_hit {len(hit_idx)} / live {len(live)}; rows_dead {len(dead)}")
    print("mismatches:", mismatches)
    print("\nHIT rows:")
    for h in out["rows_hit"]:
        print(f"  row {h['row']:3d} L{h['line']:4d} {h['type']:10s} "
              f"n={h['n_inputs']} e.g. {h['example'][:2]}")
    print("\nDEAD rows (live, never first-match):")
    for d in dead:
        print(f"  row {d['row']:3d} L{d['line']:4d} {d['type']:10s} d1={d['d1']} @{d['at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
