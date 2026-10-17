#!/usr/bin/env python3
"""r75 scribe — landed-family audit (read-only).

Audits the material the r75 consumer arm will extend and that the r74 scribe
never saw (the r74 arm landed AFTER its snapshot):
  A. lavfsweep-r74 family (7 receipts): hashes, stamp/mtime, failures lists,
     leaf-diff between sha-group representatives, report-pin cross-check,
     member sha256 vs the r74-author table.
  B. consumers-r73 family (count drift since the r74-scribe snapshot: 14).
  C. Global hygiene scans: ASLR addresses, absolute host paths, tracked vs
     untracked, stamp==mtime max delta.

Output: family-audit.json + stdout. No subprocess, no receipt write.
"""
import datetime
import hashlib
import json
import re
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RUNS = ROOT / "corpus" / "live" / "runs"
out = {"generated_utc": datetime.datetime.now(datetime.timezone.utc)
       .strftime("%Y%m%dT%H%M%S.%fZ"), "sections": {}}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def stamp_delta(dirname, f):
    try:
        s = datetime.datetime.strptime(dirname.split("-")[0],
                                       "%Y%m%dT%H%M%S%fZ").replace(
            tzinfo=datetime.timezone.utc)
    except ValueError:
        return None
    mt = datetime.datetime.fromtimestamp(f.stat().st_mtime,
                                         datetime.timezone.utc)
    return abs((mt - s).total_seconds())


def leaves(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{path}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{path}[{i}]")
    else:
        yield path, o


def leaf_diff(a, b):
    la, lb = dict(leaves(a)), dict(leaves(b))
    keys = sorted(set(la) | set(lb))
    diffs = []
    for k in keys:
        if la.get(k, "<absent>") != lb.get(k, "<absent>"):
            diffs.append({"leaf": k, "a": la.get(k, "<absent>"),
                          "b": lb.get(k, "<absent>")})
    return diffs


# ---- A. lavfsweep-r74 -------------------------------------------------------
famA = sorted(RUNS.glob("*lavfsweep-r74"))
rowsA = []
for d in famA:
    f = d / "measurements.json"
    doc = json.loads(f.read_text())
    m = doc["measurements"]
    entries = {k: v for k, v in m.items() if isinstance(v, dict)}
    fail_counts = {k: len(v.get("failures", [])) for k, v in entries.items()
                   if "failures" in v}
    rowsA.append({
        "dir": d.name, "sha256": sha(f), "bytes": f.stat().st_size,
        "mode": doc.get("mode"), "entries": len(entries),
        "failures_total": sum(fail_counts.values()),
        "stamp_vs_mtime_s": stamp_delta(d.name, f),
        "keys": sorted(entries),
    })
out["sections"]["A_lavfsweep_r74"] = {
    "count": len(rowsA), "rows": rowsA,
    "distinct_sha": sorted({r["sha256"][:16] for r in rowsA}),
}
print(f"== A. lavfsweep-r74: {len(rowsA)} receipts, "
      f"{len({r['sha256'][:16] for r in rowsA})} distinct sha")
for r in rowsA:
    print(f"  {r['dir']} {r['sha256'][:16]} {r['bytes']}B mode={r['mode']} "
          f"failures={r['failures_total']} "
          f"stamp-mtime={r['stamp_vs_mtime_s']:.6f}s")

# leaf diff between sha-group representatives (earliest of each group)
reps = {}
for r in rowsA:
    reps.setdefault(r["sha256"][:16], r["dir"])
reps = sorted(reps.items(), key=lambda kv: kv[1])
diffs = {}
if len(reps) > 1:
    base_dir = reps[0][1]
    base = json.loads((RUNS / base_dir / "measurements.json").read_text())
    for sh, dirn in reps[1:]:
        other = json.loads((RUNS / dirn / "measurements.json").read_text())
        dl = leaf_diff(base, other)
        diffs[f"{base_dir} vs {dirn}"] = dl
        # classify
        semantic = [d for d in dl
                    if not any(t in d["leaf"] for t in
                               ("wall_s", "pacing", "waited_s", "duration_s",
                                "sigterm_wait_s"))]
        print(f"  diff {base_dir[:24]} vs {dirn[:24]}: {len(dl)} leaves, "
              f"{len(semantic)} non-wall candidates")
        for d in semantic[:8]:
            print(f"     SEM? {d['leaf']}: {d['a']!r} -> {d['b']!r}")
out["sections"]["A_lavfsweep_r74"]["leaf_diffs"] = {
    k: v for k, v in diffs.items()}

# report-pin cross-check against the cited receipt
cited = RUNS / "20261014T153027827786Z-lavfsweep-r74" / "measurements.json"
cm = json.loads(cited.read_text())["measurements"]
pins = {}
try:
    iss = cm["lavfsweep_lavf_iss_r74_probe"]["transport_axis"]
    pins["iss.file.rc"] = iss["file"]["exit_code"]
    pins["iss.file.seek_failed"] = iss["file"]["seek_failed"]
    pins["iss.stdin.rc"] = iss["stdin_pipe"]["exit_code"]
    pins["iss.fifo.rc"] = iss["fifo_path"]["exit_code"]
    acm = cm["lavfsweep_lavf_acm_r74_probe"]["transport_axis"]
    pins["acm.file.rc"] = acm["file"]["exit_code"]
    pins["acm.file.seek_failed"] = acm["file"]["seek_failed"]
    im = cm["lavfsweep_lavf_iss_multi_r74_probe"]["transport_axis"]
    pins["iss_multi.file.pcm_out_bytes"] = im["file"].get("pcm_out_bytes")
    pins["iss_multi.fifo.pcm_out_bytes"] = im["fifo_path"].get("pcm_out_bytes")
    pins["iss_multi.file.pcm_out_duration_s"] = im["file"].get(
        "pcm_out_duration_s")
    sp = cm["lavf_startpos_wav_r74_probe"]["extent_legs"]
    pins["startpos.file.pcm_out_bytes"] = sp["file"].get("pcm_out_bytes")
    pins["startpos.file.pcm_out_duration_s"] = sp["file"].get(
        "pcm_out_duration_s")
    pins["startpos.stdin.pcm_out_bytes"] = sp["stdin_pipe"].get("pcm_out_bytes")
    pins["startpos.stdin.pcm_out_duration_s"] = sp["stdin_pipe"].get(
        "pcm_out_duration_s")
    o2 = cm["consumer_pwcat_ops2_r74_probe"]
    pins["ops2.escalation.exit_code"] = o2["fifo_no_writer_escalation"]["exit_code"]
    pins["ops2.escalation.sigterm_immune"] = o2["fifo_no_writer_escalation"]["sigterm_immune"]
    pins["ops2.target0.exit_code"] = o2["target0_unlinked_stream"]["exit_code"]
    pins["ops2.target0.term_terminable"] = o2["target0_unlinked_stream"]["term_terminable"]
    pins["ops2.raw_axis.rcs"] = {k: v["exit_code"]
                                 for k, v in o2["pwcat_raw_name_axis"]["legs"].items()}
    pins["ops2.zero_sink.audio_sink_count"] = o2["zero_sink_daemon"]["audio_sink_count"]
    pins["ops2.zero_sink.exit_code"] = o2["zero_sink_daemon"]["pwcat"]["exit_code"]
except KeyError as e:
    pins["ERROR"] = f"missing key {e}"
out["sections"]["A_report_pins_cited_receipt"] = pins
print("== A. report pins (cited receipt 20261014T153027827786Z):")
for k, v in pins.items():
    print(f"  {k} = {v}")

# member sha256 vs r74-author table
author_table = {"lavf_iss.iss": "4fbc2ca5", "lavf_iss_multi.iss": "85a518c8",
                "lavf_apc.apc": "684d2794", "lavf_acm.acm": "5afaa65a",
                "lavf_adx.adx": "3831ef47", "lavf_aifc.aifc": "23aa8a65"}
mem = {}
for name, pref in author_table.items():
    p = ROOT / "corpus" / "live" / "round-74" / name
    got = sha(p)[:8] if p.exists() else "ABSENT"
    mem[name] = {"report_prefix": pref, "measured_prefix": got,
                 "match": got == pref}
out["sections"]["A_member_shas"] = mem
print("== A. members vs report table:",
      "all match" if all(v["match"] for v in mem.values()) else mem)

# ---- B. consumers-r73 -------------------------------------------------------
famB = sorted(RUNS.glob("*consumers-r73"))
rowsB = []
for d in famB:
    f = d / "measurements.json"
    rowsB.append({"dir": d.name, "sha256": sha(f), "bytes": f.stat().st_size,
                  "stamp_vs_mtime_s": stamp_delta(d.name, f)})
out["sections"]["B_consumers_r73"] = {
    "count": len(rowsB), "rows": rowsB,
    "distinct_sha": sorted({r["sha256"][:16] for r in rowsB})}
print(f"== B. consumers-r73: {len(rowsB)} receipts "
      f"({len({r['sha256'][:16] for r in rowsB})} distinct sha)")
for r in rowsB:
    print(f"  {r['dir']} {r['sha256'][:16]} {r['bytes']}B")

# ---- C. global hygiene ------------------------------------------------------
allm = sorted(RUNS.glob("*/measurements.json"))
aslr = []
paths = []
for f in allm:
    txt = f.read_text()
    if re.search(r"0x[0-9a-fA-F]{8,}", txt):
        aslr.append(f.parent.name)
    if "/home/vgpnk" in txt:
        paths.append(f.parent.name)
out["sections"]["C_global"] = {
    "receipts_total": len(allm),
    "aslr_files": len(aslr), "aslr_dirs": aslr,
    "path_files": len(paths),
    "path_by_family": {},
}
fam = {}
for n in paths:
    key = re.sub(r"^\d{8}T\d{6,}Z-", "", n)
    fam[key] = fam.get(key, 0) + 1
out["sections"]["C_global"]["path_by_family"] = fam
print(f"== C. global: {len(allm)} receipts; ASLR-addr files {len(aslr)}; "
      f"path-embedding files {len(paths)}")
print("   path by family:", json.dumps(fam))

(ROOT / "corpus/live/r75-scribe/family-audit.json").write_text(
    json.dumps(out, indent=1))
print("wrote corpus/live/r75-scribe/family-audit.json")
