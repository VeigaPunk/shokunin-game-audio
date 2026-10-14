#!/usr/bin/env python3
"""r69 SCRIBE dead-CHECK-row census (independent, row-level).

Coverage census over the auto_detect_format CHECK table in the lane-verified
formats.c copy (corpus/live/r64-reviewer/r64rev-formats.c, sha256
82c3058e... == upstream tag 14.8.0.1). Build flags verified live this
session: USING_FFMPEG=1, HAVE_SNDFILE=1, HAVE_SF_FORMAT_MPC2K=1 (sds+mpc2k
detection probed); HAVE_MAGIC post-table (not a row); #if 0 adx excluded
-> 130 active rows / 77 distinct types.

Tiers:
  SIMULATED  -- evaluate the parsed table in order over every git-tracked
                file under corpus/ (member fixtures incl. seat probes) and
                record which ROW is first-match (the .snd ext gate handled).
  RECORDED   -- scan every tracked file for `sox_detected_format` values and
                `detected file format type` strings; split by file kind
                (receipt json vs raw log/tsv/stderr vs report md).
  LEDGER     -- subset of tracked receipts under corpus/live/runs/ (the
                measure_audio.py ledger receipts).

Row status = first-match simulated on >=1 committed member, or its type
recorded as a detection in a committed file. Everything else is dead.
"""
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FORMATS = REPO / "corpus" / "live" / "r64-reviewer" / "r64rev-formats.c"
AUTO_DETECT_SIZE = 257
CONDS = {"USING_FFMPEG": True, "HAVE_SNDFILE": True,
         "HAVE_SF_FORMAT_MPC2K": True, "HAVE_MAGIC": True}
SKIP_EXT = {".json", ".md", ".py", ".tsv", ".txt", ".log", ".stderr",
            ".stdout", ".c", ".h", ".sh", ".diff", ".patch", ".out"}


def c_string_bytes(lit):
    s = lit.strip()
    assert s.startswith('"') and s.endswith('"'), lit
    body = s[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        c = body[i]
        if c != "\\":
            out.append(ord(c)); i += 1; continue
        i += 1
        c = body[i]
        if c == "x":
            j = i + 1
            while j < len(body) and body[j] in "0123456789abcdefABCDEF":
                j += 1
            out.append(int(body[i + 1:j], 16)); i = j
        elif c in "01234567":
            j = i
            while j < len(body) and j < i + 3 and body[j] in "01234567":
                j += 1
            out.append(int(body[i:j], 8)); i = j
        else:
            out.append({"n": 10, "t": 9, "r": 13, "0": 0}.get(c, ord(c)))
            i += 1
    out.append(0)
    return bytes(out)


def parse_rows():
    lines = FORMATS.read_text().splitlines()
    rows, stack = [], []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if s.startswith("#if 0"):
            stack.append(False)
        elif s.startswith("#if"):
            sym = s.split()[1] if len(s.split()) > 1 else ""
            stack.append(CONDS.get(sym, True))
        elif s.startswith("#endif"):
            stack.pop()
        elif s.startswith("#else"):
            if stack:
                stack[-1] = not stack[-1]
        if "CHECK(" in s and "define CHECK" not in s:
            text = s
            while text.count("(") > text.count(")"):
                i += 1
                text += " " + lines[i].strip()
            inner = text[text.index("(") + 1:text.rindex(")")]
            inner = re.sub(r"/\*.*?\*/", "", inner, flags=re.S)
            parts = [p.strip() for p in inner.split(",")]
            assert len(parts) == 7, (i, parts)
            typ, p2, l2, d2, p1, l1, d1 = parts
            rows.append({"line": i + 1, "type": typ.strip(),
                         "p2": int(p2), "l2": int(l2),
                         "d2": c_string_bytes(d2), "p1": int(p1),
                         "l1": int(l1), "d1": c_string_bytes(d1),
                         "active": all(stack)})
        i += 1
    return rows


def first_match(rows, data, ext=None):
    ln = min(len(data), AUTO_DETECT_SIZE)
    buf = data[:AUTO_DETECT_SIZE]
    for idx, row in enumerate(rows):
        if not row["active"]:
            continue
        if row["type"] == "sndr" and not (ext and ext.lower() == "snd"):
            continue
        if ln >= row["p1"] + row["l1"]:
            if (buf[row["p1"]:row["p1"] + row["l1"]] == row["d1"][:row["l1"]]
                    and buf[row["p2"]:row["p2"] + row["l2"]] == row["d2"][:row["l2"]]):
                return idx
    return None


def main():
    rows = parse_rows()
    active_idx = [i for i, r in enumerate(rows) if r["active"]]
    files = subprocess.run(["git", "ls-files"], cwd=REPO,
                           capture_output=True, text=True).stdout.splitlines()

    # --- SIMULATED first-match over every tracked member-like file ----------
    row_members = defaultdict(set)          # active idx -> member paths
    member_row = {}
    n_members = 0
    for f in files:
        if not f.startswith("corpus/"):
            continue
        p = REPO / f
        if p.suffix in SKIP_EXT or not p.is_file():
            continue
        data = p.read_bytes()
        n_members += 1
        ext = p.suffix[1:] if p.suffix else None
        idx = first_match(rows, data, ext)
        member_row[f] = idx
        if idx is not None:
            row_members[idx].add(f)

    # --- RECORDED detections over every tracked file ------------------------
    det_re = re.compile(r"detected file format type [`']([\w.\-]+)'")
    recorded = defaultdict(lambda: defaultdict(set))   # type -> kind -> files
    for f in files:
        if not f.startswith("corpus/") and not f.startswith("reports/"):
            continue
        p = REPO / f
        if not p.is_file() or p.stat().st_size > 3_000_000:
            continue
        if p.suffix == ".json":
            kind = "receipt_json"
        elif f.startswith("reports/"):
            kind = "report_md"
        elif p.suffix in (".tsv", ".stderr", ".stdout", ".log", ".txt"):
            kind = "raw_log"
        else:
            continue
        text = p.read_text(errors="replace")
        seen = set(det_re.findall(text))
        if kind == "receipt_json":
            try:
                payload = json.loads(text)
            except Exception:
                payload = None
            stack = [payload]
            while stack:
                node = stack.pop()
                if isinstance(node, dict):
                    for k, v in node.items():
                        if k == "sox_detected_format" and isinstance(v, str):
                            seen.add(v)
                        else:
                            stack.append(v)
                elif isinstance(node, list):
                    stack.extend(node)
        for t in seen:
            recorded[t][kind].add(f)

    live_types = set(row_members[i] and rows[i]["type"] for i in row_members)
    live_types = {rows[i]["type"] for i in row_members}
    rec_types = set(recorded)
    all_types = {rows[i]["type"] for i in active_idx}
    dead_rows = [i for i in active_idx if i not in row_members
                 and rows[i]["type"] not in rec_types]
    dead_types = sorted(all_types - live_types - rec_types)

    result = {
        "build_flags_verified": dict(CONDS, note="sds+mpc2k detection probed"),
        "rows_total_parsed": len(rows),
        "rows_active": len(active_idx),
        "rows_inactive_source": [r["line"] for r in rows if not r["active"]],
        "distinct_types_active": len(all_types),
        "tracked_member_files_simulated": n_members,
        "types_simulated_firstmatch": sorted(live_types),
        "types_recorded_detection": sorted(rec_types),
        "row_firstmatch": {
            f"{i}:{rows[i]['type']}": sorted(row_members[i])[:8]
            for i in sorted(row_members)},
        "recorded_by_kind": {
            t: {k: sorted(v)[:6] for k, v in kinds.items()}
            for t, kinds in sorted(recorded.items())},
        "dead_row_count": len(dead_rows),
        "dead_rows": [{"line": rows[i]["line"], "type": rows[i]["type"],
                       "src": rows[i]} for i in dead_rows],
        "dead_type_count": len(dead_types),
        "dead_types": dead_types,
    }
    # strip bytes for json
    for d in result["dead_rows"]:
        d["src"] = {"p1": d["src"]["p1"], "l1": d["src"]["l1"],
                    "p2": d["src"]["p2"], "l2": d["src"]["l2"]}
    out = REPO / "corpus/live/r69-scribe/runs/census.json"
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(f"active rows={len(active_idx)} types={len(all_types)} "
          f"members_simulated={n_members}")
    print(f"simulated-firstmatch types={len(live_types)}: {sorted(live_types)}")
    print(f"recorded types={len(rec_types)}: {sorted(rec_types)}")
    print(f"DEAD rows={len(dead_rows)}/{len(active_idx)} "
          f"DEAD types={len(dead_types)}")
    rows_by_type = defaultdict(list)
    for i in active_idx:
        rows_by_type[rows[i]["type"]].append(i)
    # of live types, which ROWS still dead (multi-row types partially dead)
    partial = {t: {"live_rows": [rows[i]["line"] for i in idxs if i in row_members],
                   "dead_rows": [rows[i]["line"] for i in idxs if i not in row_members]}
               for t, idxs in rows_by_type.items()
               if t in live_types or t in rec_types}
    partial = {t: v for t, v in partial.items() if v["dead_rows"]}
    print("partially-dead multi-row types:")
    print(json.dumps(partial, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
