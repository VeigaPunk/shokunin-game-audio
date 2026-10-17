#!/usr/bin/env python3
"""Compact reader for r81-boundary receipts (seat-owned scratch analyzer)."""
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
REC = OUT / "receipts"


def freeze_time(sizes):
    """Return (t_last_change, size_at_change, t_end, size_end)."""
    vals = [(t, s) for t, s in sizes if s is not None]
    if not vals:
        return None
    t_end, s_end = vals[-1]
    last_t, last_s = vals[0]
    for t, s in vals:
        if s != last_s:
            last_t, last_s = t, s
    return last_t, last_s, t_end, s_end


def series(sizes, step=0.2):
    vals = [(t, s) for t, s in sizes if s is not None]
    if not vals:
        return "no-file"
    out, nxt = [], 0.0
    for t, s in vals:
        if t >= nxt:
            out.append("%.1f:%s" % (t, s))
            nxt = t + step
    if out and not out[-1].startswith("%.1f" % vals[-1][0]):
        out.append("%.1f:%s" % vals[-1])
    return " ".join(out)


def mine(g):
    return {k: v for k, v in (g.get("mine") or {}).items()
            if k.startswith("gst_r81_bnd") or k == "gst-launch-1.0"}


def links(g, pat="gst_r81_bnd"):
    return [ln for ln in (g.get("links") or []) if pat in ln]


def show_leg(leg, verbose=True):
    print("### %s r%s  rc=%s killed=%s elapsed=%ss %s" % (
        leg["name"], leg.get("rep"), leg["rc"], leg.get("killed"),
        leg["elapsed_s"], leg.get("note") or ""))
    if leg.get("env_extra"):
        print("    env: %s" % json.dumps(leg["env_extra"]))
    print("    argv: %s" % " ".join(leg["argv"]))
    for pr in leg.get("producers") or []:
        print("    prod %s: at=%s started=%s ended=%s killed=%s rc=%s err=%s" % (
            pr["name"], pr["at"], pr.get("started"), pr.get("ended"),
            pr.get("killed"), pr.get("rc"), (pr.get("stderr_head") or [])[:1]))
    if leg.get("actions"):
        for a in leg["actions"]:
            r = a["result"]
            keep = {k: r[k] for k in ("rc", "index", "reason", "name", "verified_line")
                    if k in r} or r
            if "reload" in r:
                keep = {"reload": r["reload"]}
            print("    action@%s: %s" % (a["t"], json.dumps(keep)[:200]))
    if leg.get("sizes"):
        ft = freeze_time(leg["sizes"])
        print("    sizes: %s" % series(leg["sizes"]))
        if ft:
            print("    last-change t=%s size=%s | end t=%s size=%s" % ft)
    if leg.get("out"):
        o = leg["out"]
        print("    out: bytes=%s riff=%s data=%s frames=%s ch=%s rate=%s peak=%s" % (
            o["bytes"], o["riff"], o["data"], o["frames"], o["ch"], o["rate"],
            leg.get("out_peak")))
    print("    stderr: %s | cls=%s hit=%s" % ((leg.get("stderr_head") or [])[:2],
                                             leg.get("err_class"), leg.get("err_hit")))
    if verbose and leg.get("samples"):
        prev = None
        for s in leg["samples"]:
            ln = links(s["g"])
            mn = sorted(mine(s["g"]))
            cur = (tuple(ln), tuple(mn))
            if cur != prev:
                print("    g@%s nodes=%s" % (s["t"], mn))
                for l in ln:
                    print("        link %s" % l)
                prev = cur
    print()


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else None
    only = sys.argv[2] if len(sys.argv) > 2 else None
    for p in sorted(REC.glob("s*.json")):
        if stage and not p.stem.startswith(stage):
            continue
        doc = json.loads(p.read_text())
        print("=" * 78)
        print("RECEIPT %s  when=%s" % (p.name, doc.get("when")))
        body = doc.get("body") or {}
        if isinstance(body, dict) and "legs" in body:
            for k in ("load", "load2", "load3", "load4"):
                if body.get(k):
                    print("  %s: %s" % (k, body[k]))
            for leg in body["legs"]:
                if only and only not in leg["name"]:
                    continue
                show_leg(leg)
        else:
            print(json.dumps(body, indent=1)[:3000])


if __name__ == "__main__":
    main()
