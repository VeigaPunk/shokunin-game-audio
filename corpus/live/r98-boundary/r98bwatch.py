#!/usr/bin/env python3
"""Shared-graph clock watcher — is the shared graph's quantum/rate moving under
foreign load, and does a foreign rate excursion change my stream's geometry?

Runs a bounded loop (argv[1] = seconds, argv[2] = period s): every period it
records pw-top's driver rows (QUANT/RATE), the shared graph's default sink, the
loadavg, and one control leg (run target=r98b_ns flags=autoconnect) with its
geometry. Own objects only; the private null-sink is unloaded by verified index.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r98bd as m  # noqa: E402

OUT = Path(__file__).resolve().parent / "receipts" / "shared-clock-watch.json"


def top_rows():
    r = m.sh(["pw-top", "-b", "-n", "2"], timeout=20)
    txt = r["out"].decode(errors="replace")
    rows = []
    for l in txt.splitlines():
        if l.startswith(("R ", "I ", "C ")) and len(l.split()) >= 5:
            p = l.split()
            rows.append({"state": p[0], "name": p[-1], "quant": p[2], "rate": p[3],
                         "err": p[8] if len(p) > 8 else None})
    return rows


def main():
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 180
    period = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    mid = m.load_sink(m.SINK)
    time.sleep(1)
    samples = []
    t0 = time.time()
    while time.time() - t0 < total:
        rec = m.run_leg("watch", ["run", f"target={m.SINK}", "flags=autoconnect",
                                  "ms=900"], rep=len(samples))
        p = rec["parsed"]
        rows = top_rows()
        running = [r for r in rows if r["state"] == "R"]
        s = {"t": round(time.time() - t0, 1), "loadavg": m.loadavg(),
             "state": p.get("state"), "maxsize": p.get("last_maxsize"),
             "req": p.get("last_bufid"), "nbufs": p.get("last_nbufs"),
             "running_nodes": running[:8]}
        samples.append(s)
        print(json.dumps(s), flush=True)
        time.sleep(period)
    un = m.unload_sink(mid, m.SINK)
    OUT.write_text(json.dumps({"utc": m.utc(), "samples": samples, "unload": un,
                               "exit_census": m.census("watch-exit")}, indent=1))
    print("exit census r98b:", m.census("watch-exit2")["r98b_nodes"])


if __name__ == "__main__":
    main()
