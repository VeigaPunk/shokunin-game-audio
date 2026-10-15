#!/usr/bin/env python3
"""B9 — one-shot debug-level A/B on the silent convolver, with the FULL pw-cli
log written to disk so the [E]/[W] count and the graph-load evidence are both
auditable (B6 only stored the counts; its debug-5 legs failed to capture audio,
so the "did the graph load?" question has to be answered from the log text).

Writes runs/b9_dbg{3,5}.log. No audio, no sink, no links.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig as R

CASES = {
    "missing": "config={filename=/nonexistent/r92b_ir.wav}",
    "noconfig": "",
}


def main():
    t0 = time.time()
    R.preflight()
    res = {}
    for lvl in ("3", "5"):
        for nm, cfg in CASES.items():
            tok = R.fc_args(["{type=builtin,name=cv,label=convolver%s}" %
                             (("," + cfg) if cfg else "")])
            cli = R.PwCli(env={"PIPEWIRE_DEBUG": lvl}, idle=1.0, hard=25.0)
            out, var = cli.load("libpipewire-module-filter-chain", tok)
            time.sleep(3.0)
            unload = cli.cmd("unload-module %d" % var) if var is not None else None
            cli.close()
            txt = cli.text()
            lines = txt.splitlines()
            graph_lines = [l.strip()[:170] for l in lines if "spa.filter-graph" in l]
            path = os.path.join(R.RUNS, "b9_dbg%s_%s.log" % (lvl, nm))
            with open(path, "w") as f:
                f.write(txt)
            res["%s-dbg%s" % (nm, lvl)] = {
                "var": var, "loaded_graph": any("loaded n_input" in l for l in lines),
                "n_lines": len(lines), "n_E": txt.count("[E]"), "n_W": txt.count("[W]"),
                "n_I": txt.count("[I]"), "n_D": txt.count("[D]"),
                "graph_lines": graph_lines, "log": path,
                "convolver_lines": [l.strip()[:200] for l in lines
                                    if "convolver" in l.lower() or "sndfile" in l.lower()
                                    or "ir.wav" in l.lower()][:12],
            }
            print("%-14s debug=%s var=%s graph=%s lines=%d E=%d W=%d D=%d -> %s" %
                  (nm, lvl, var, res["%s-dbg%s" % (nm, lvl)]["loaded_graph"], len(lines),
                   txt.count("[E]"), txt.count("[W]"), txt.count("[D]"), path))
            for l in graph_lines[:6]:
                print("      |", l)
    res["elapsed_s"] = round(time.time() - t0, 1)
    res["sweep"] = R.sweep()
    R.jdump(os.path.join(R.REC, "b9_dbg.json"), res)
    print("WROTE b9_dbg.json (%.1fs)" % (time.time() - t0))


if __name__ == "__main__":
    main()
