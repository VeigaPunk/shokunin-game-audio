#!/usr/bin/env python3
"""Derive r76 boundary verdicts from the raw cell receipts.

Reads every runs/*/measurements.json under corpus/live/r76-boundary and emits
runs/<stamp>-boundary-r76-verdicts/verdicts.json + a markdown summary on stdout.

Classes are computed, never asserted:
- header_idiom: how a consumer's *unfinalised* file declares its length.
- sever_class:  what TERM1 did to a mid-capture stream (alive_after_term1,
  rc, header finality), TERM2/KILL escalation.
- capture_ratio: captured seconds / wall seconds (bounded + 8 s cells).
- bound_honour: requested bound vs captured seconds vs wall.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"


def load_all():
    recs = {}
    for p in sorted(RUNS.glob("*/measurements.json")):
        try:
            for r in json.loads(p.read_text()):
                key = f"{p.parent.name}/{r['cell']}"
                recs[key] = r
        except (OSError, ValueError):
            continue
    return recs


def body_seconds(r):
    """Payload seconds from the RIFF header rate/channels (PCM16 only)."""
    pr = r.get("probe") or {}
    ri = r.get("riff") or {}
    size = r.get("size")
    if not size or not ri.get("wave"):
        return None
    rate = pr.get("rate")
    ch = pr.get("ch")
    codec = pr.get("codec")
    if not rate or not ch or codec != "pcm_s16le":
        return None
    return (size - 44) / (int(rate) * int(ch) * 2)


def header_idiom(r):
    ri = r.get("riff") or {}
    if not ri.get("wave"):
        return "no-header" if r.get("size") else "no-file"
    d, a = ri.get("declared"), ri.get("actual")
    dd = ri.get("data_declared")
    if d is None:
        return "unknown"
    if d + 8 == a:
        return "finalised"
    if d == 8 and dd == 0:
        return "libsndfile-placeholder(8/0)"
    if d in (0xFFFFFFFF, 0xFFFFFFF0):
        return "lavf-placeholder(0xFFFFFFFF)"
    return f"stale({d}/{a})"


def sever_class(r):
    if r.get("alive_after_term1"):
        base = "term1-immune"
    elif r.get("alive_after_term2"):
        base = "term2-immune"
    else:
        base = "term1-fatal"
    rc = r.get("rc")
    if base == "term1-fatal":
        base += f"(rc={rc})"
    if r.get("killed_by") == "harness":
        base += "+harness-kill"
    return base


def fmt_secs(x):
    return f"{x:.3f}" if isinstance(x, float) else "-"


def main():
    recs = load_all()
    out = {"cells": len(recs), "verdicts": {}}

    def pick(pred):
        return {k: v for k, v in recs.items() if pred(v)}

    # ---- header idiom of killed/partial files
    killed = pick(lambda r: r.get("killed_by") in ("harness", "term1", "term2", "kill")
                  and r.get("size"))
    idioms = {}
    for k, r in killed.items():
        fam = re.sub(r"^(sev-(mid|early)|pin|bound|name|gate|load\d*|loadcpu\d*)-", "", r["cell"])
        fam = re.sub(r"[-\d]+$", "", fam)
        idioms.setdefault(fam, set()).add(header_idiom(r))
    out["verdicts"]["header_idiom_by_family"] = {k: sorted(v) for k, v in sorted(idioms.items())}

    # ---- sever ladder
    sev = {}
    for k, r in recs.items():
        if not k.split("/")[1].startswith("sev-"):
            continue
        phase = "mid" if "-mid-" in k else "early"
        tag = k.split(f"sev-{phase}-")[1]
        sev.setdefault(tag, {})[phase] = {
            "rc": r.get("rc"),
            "wall_s": r.get("wall_s"),
            "wall_at_term1": r.get("wall_at_term1"),
            "alive_after_term1": r.get("alive_after_term1"),
            "alive_after_term2": r.get("alive_after_term2"),
            "killed_by": r.get("killed_by"),
            "size": r.get("size"),
            "bytes_at_term1": r.get("bytes_at_term1"),
            "header": header_idiom(r),
            "captured_s": (round(body_seconds(r), 3) if body_seconds(r) else None),
            "probe_dur": (r.get("probe") or {}).get("duration"),
            "stderr_tail": (r.get("stdout_tail") or "")[-160:],
            "class": sever_class(r),
        }
    out["verdicts"]["sever_ladder"] = sev

    # ---- capture ratio (bounded 8 s wall cells + gates)
    ratio = {}
    for k, r in recs.items():
        cell = k.split("/")[1]
        if not cell.startswith(("pin-", "bound-", "gate-")):
            continue
        b = body_seconds(r)
        if b is None or not r.get("wall_s"):
            continue
        ratio[cell] = {"wall_s": r["wall_s"], "captured_s": round(b, 3),
                       "ratio": round(b / r["wall_s"], 3), "rc": r.get("rc"),
                       "header": header_idiom(r),
                       "probe_dur": (r.get("probe") or {}).get("duration")}
    out["verdicts"]["capture_ratio"] = ratio

    # ---- bound honour: requested vs captured (stream time) vs wall
    bounds = {}
    req = {"bound-pw-src-n48000": ("samples", 48000, 48000.0),
           "bound-pw-src-n24000": ("samples", 24000, 48000.0),
           "bound-ar-null-d1": ("seconds", 1, 1.0),
           "bound-ar-null-s48000": ("samples", 48000, 48000.0),
           "bound-ar-hw00-d1": ("seconds", 1, 1.0),
           "bound-ff-pulse-src-t1": ("seconds", 1, 1.0),
           "bound-ff-alsa-null-t1": ("seconds", 1, 1.0),
           "bound-ff-alsa-null-t2": ("seconds", 2, 1.0),
           "bound-ff-alsa-hw00-t1": ("seconds", 1, 1.0),
           "bound-ff-pulse-src-fs100k": ("bytes", 100000, 1.0),
           "bound-pa-term1": ("wrapper-TERM", 2.0, 1.0)}
    for k, r in recs.items():
        cell = k.split("/")[1]
        if cell not in req:
            continue
        kind, value, rate = req[cell]
        b = body_seconds(r)
        bounds[cell] = {"requested": f"{kind}={value}", "wall_s": r.get("wall_s"),
                        "captured_s": round(b, 3) if b else None,
                        "rc": r.get("rc"), "size": r.get("size"),
                        "header": header_idiom(r),
                        "probe_dur": (r.get("probe") or {}).get("duration"),
                        "killed_by": r.get("killed_by"),
                        "class": sever_class(r) if r.get("ladder") else None}
    out["verdicts"]["bound_honour"] = bounds

    # ---- name axis
    names = {}
    for k, r in recs.items():
        cell = k.split("/")[1]
        if not cell.startswith("name-"):
            continue
        names[cell] = {"rc": r.get("rc"), "size": r.get("size"),
                       "header": header_idiom(r),
                       "codec": (r.get("probe") or {}).get("codec"),
                       "dur": (r.get("probe") or {}).get("duration"),
                       "stderr_tail": (r.get("stdout_tail") or "")[-120:]}
    out["verdicts"]["name_axis"] = names

    # ---- fifo / sink edges
    edges = {}
    for k, r in recs.items():
        cell = k.split("/")[1]
        if not cell.startswith(("fifo-", "sink-")):
            continue
        edges[cell] = {"rc": r.get("rc"), "wall_s": r.get("wall_s"),
                       "killed_by": r.get("killed_by"),
                       "non_regular": r.get("non_regular"),
                       "size": r.get("size"),
                       "stderr_tail": (r.get("stdout_tail") or "")[-140:]}
    out["verdicts"]["fifo_sink_edges"] = edges

    # ---- load replay comparison
    load = {}
    for k, r in recs.items():
        cell = k.split("/")[1]
        if not cell.startswith(("load", "loadcpu")):
            continue
        load[cell] = {"rc": r.get("rc"), "wall_s": r.get("wall_s"),
                      "alive_after_term1": r.get("alive_after_term1"),
                      "alive_after_term2": r.get("alive_after_term2"),
                      "killed_by": r.get("killed_by"), "size": r.get("size"),
                      "header": header_idiom(r), "class": sever_class(r)}
    out["verdicts"]["load"] = load

    outdir = RUNS / "verdicts-r76"
    outdir.mkdir(exist_ok=True)
    (outdir / "verdicts.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")

    # ---- markdown
    md = []
    md.append(f"cells read: {out['cells']} -> {outdir/'verdicts.json'}")
    md.append("\n## sever ladder")
    md.append("| target | phase | class | rc | wall@term1 | wall | bytes@term1 | size | captured_s | header |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    for tag in sorted(sev):
        for phase in ("mid", "early"):
            v = sev[tag].get(phase)
            if not v:
                continue
            md.append(f"| {tag} | {phase} | {v['class']} | {v['rc']} | {v['wall_at_term1']} | "
                      f"{v['wall_s']} | {v['bytes_at_term1']} | {v['size']} | {v['captured_s']} | {v['header']} |")
    md.append("\n## capture ratio (captured_s / wall_s)")
    md.append("| cell | wall | captured_s | ratio | rc | header | probe_dur |")
    md.append("|---|---|---|---|---|---|---|")
    for cell in sorted(ratio):
        v = ratio[cell]
        md.append(f"| {cell} | {v['wall_s']} | {v['captured_s']} | {v['ratio']} | {v['rc']} | {v['header']} | {v['probe_dur']} |")
    md.append("\n## bound honour")
    md.append("| cell | requested | wall | captured_s | rc | size | header | probe_dur | killed_by |")
    md.append("|---|---|---|---|---|---|---|---|---|")
    for cell in sorted(bounds):
        v = bounds[cell]
        md.append(f"| {cell} | {v['requested']} | {v['wall_s']} | {v['captured_s']} | {v['rc']} | "
                  f"{v['size']} | {v['header']} | {v['probe_dur']} | {v['killed_by']} |")
    md.append("\n## name axis")
    md.append("| cell | rc | size | header | codec | dur | tail |")
    md.append("|---|---|---|---|---|---|---|")
    for cell in sorted(names):
        v = names[cell]
        md.append(f"| {cell} | {v['rc']} | {v['size']} | {v['header']} | {v['codec']} | {v['dur']} | {v['stderr_tail'][-60:]} |")
    md.append("\n## fifo / sink edges")
    md.append("| cell | rc | wall | killed_by | non_regular | size | tail |")
    md.append("|---|---|---|---|---|---|---|")
    for cell in sorted(edges):
        v = edges[cell]
        md.append(f"| {cell} | {v['rc']} | {v['wall_s']} | {v['killed_by']} | {v['non_regular']} | {v['size']} | {v['stderr_tail'][-70:]} |")
    md.append("\n## load replay")
    md.append("| cell | class | rc | wall | size | header |")
    md.append("|---|---|---|---|---|---|")
    for cell in sorted(load):
        v = load[cell]
        md.append(f"| {cell} | {v['class']} | {v['rc']} | {v['wall_s']} | {v['size']} | {v['header']} |")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
