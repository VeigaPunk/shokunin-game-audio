#!/usr/bin/env python3
"""r68-scribe independent measurement: post-table fallback + txw/smp pipe refusal.

Reuses the landed r67 arm machinery (transport_matrix/transport_leg) imported
verbatim from corpus/fixtures/measure_audio.py — same 4 transports, same
verdict signature, same fifo writer-linger protocol. Members live under
corpus/live/r68-scribe/probes/ (scratch).
"""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # corpus/
SPEC = importlib.util.spec_from_file_location(
    "measure_audio", ROOT / "fixtures" / "measure_audio.py")
ma = importlib.util.module_from_spec(SPEC)
sys.modules["measure_audio"] = ma
SPEC.loader.exec_module(ma)

PROBES = ROOT / "live" / "r68-scribe" / "probes"
MEMBERS = [
    "nomatch_zeros.wav",
    "nomatch_noise.wav",
    "nomatch_zeros.bin",
    "nomatch_zeros",
    "cand_txw.wav",
    "cand_smp.wav",
]

out = {}
for name in MEMBERS:
    path = PROBES / name
    arms = ma.transport_matrix(path)
    groups = []
    for transport in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
        arm = arms[transport]
        sig = (arm["sox_detected_format"], arm["sox_route"], arm["exit_code"],
               arm["samples_read"], arm["error"])
        for g in groups:
            if g[0] == sig:
                g[1].append(transport)
                break
        else:
            groups.append((sig, [transport]))
    out[name] = {
        "member": name,
        "sha256": __import__("hashlib").sha256(path.read_bytes()).hexdigest(),
        "transport_axis": arms,
        "transport_verdict_groups": [
            {"transports": ts, "sox_detected_format": s[0], "sox_route": s[1],
             "exit_code": s[2], "samples_read": s[3], "error": s[4]}
            for s, ts in groups],
        "transport_fork": len(groups) > 1,
    }

dest = Path(__file__).resolve().parent / "runs" / "posttable-matrix.json"
dest.write_text(json.dumps(out, indent=2) + "\n")
print("wrote", dest)
for name, entry in out.items():
    print(f"== {name}  fork={entry['transport_fork']}")
    for g in entry["transport_verdict_groups"]:
        print("   ", "/".join(g["transports"]),
              "| det=", g["sox_detected_format"], "route=", g["sox_route"],
              "exit=", g["exit_code"], "smp=", g["samples_read"],
              "err=", g["error"])
