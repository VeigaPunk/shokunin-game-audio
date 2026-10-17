#!/usr/bin/env python3
"""r74 scribe receipt-hygiene check — read-only over corpus/live/runs/.

1. Byte-stability grouping of the 13 consumers-r73 receipts + leaf-level diff
   vs the r73-era receipt cited by the author report.
2. Timestamp hygiene: dir stamp (UTC) vs file mtime (UTC).
3. ASLR/path scan of the consumer-family receipts.
Output: receipt-hygiene.json + stdout.
"""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RUNS = ROOT / "corpus" / "live" / "runs"
out = {}

fams = {"consumers-r73": sorted(RUNS.glob("*consumers-r73"))}
for fam, dirs in fams.items():
    rows = []
    for d in dirs:
        f = d / "measurements.json"
        if not f.exists():
            continue
        h = hashlib.sha256(f.read_bytes()).hexdigest()
        st = f.stat()
        import datetime
        mtime = datetime.datetime.fromtimestamp(st.st_mtime,
                                                datetime.timezone.utc)
        rows.append({"dir": d.name, "sha256": h,
                     "mtime_utc": mtime.strftime("%Y%m%dT%H%M%S.%fZ"),
                     "stamp": d.name.split("-")[0]})
    out[fam] = rows
    print(f"== {fam}: {len(rows)} receipts")
    for r in rows:
        print(f"  {r['dir']}  {r['sha256'][:16]}  mtime={r['mtime_utc'][:19]}")
    # stamp-vs-mtime delta
    deltas = []
    for r in rows:
        try:
            import datetime
            s = datetime.datetime.strptime(r["stamp"], "%Y%m%dT%H%M%S%fZ"
                                           ).replace(tzinfo=datetime.timezone.utc)
            mt = datetime.datetime.strptime(r["mtime_utc"],
                                            "%Y%m%dT%H%M%S.%fZ"
                                            ).replace(tzinfo=datetime.timezone.utc)
            deltas.append(abs((mt - s).total_seconds()))
        except ValueError:
            pass
    print(f"  stamp-vs-mtime max delta: {max(deltas) if deltas else None:.6f}s")

# leaf diff vs the r73-era receipt
base = RUNS / "20261014T145502288182Z-consumers-r73" / "measurements.json"
new = RUNS / "20261014T151240011154Z-consumers-r73" / "measurements.json"
b = json.loads(base.read_text())
n = json.loads(new.read_text())


def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from walk(v, path + "/" + str(i))
    else:
        yield path, o


bd = dict(walk(b))
nd = dict(walk(n))
diffs = [(k, bd[k], nd[k]) for k in sorted(set(bd) | set(nd))
         if bd.get(k, "<absent>") != nd.get(k, "<absent>")]
print(f"== leaf diff base(145502288182Z) vs new(151240011154Z): {len(diffs)} leaves")
for k, x, y in diffs[:20]:
    print(f"  {k}: {x!r} -> {y!r}")
out["leaf_diff_base_vs_new"] = [{"leaf": k, "base": x, "new": y}
                                for k, x, y in diffs]

# ASLR / path scan of the consumer-family receipts
for r in out["consumers-r73"]:
    p = RUNS / r["dir"] / "measurements.json"
    txt = p.read_text()
    r["has_0x_addr"] = bool(__import__("re").search(r"0x[0-9a-fA-F]{8,}", txt))
    r["has_abs_path"] = "/home/vgpnk" in txt
print("== consumer-family scan:")
for r in out["consumers-r73"]:
    if r["has_0x_addr"] or r["has_abs_path"]:
        print(f"  {r['dir']} 0x_addr={r['has_0x_addr']} abs_path={r['has_abs_path']}")

(ROOT / "corpus/live/r74-scribe/receipt-hygiene.json").write_text(
    json.dumps(out, indent=2) + "\n")
