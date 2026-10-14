#!/usr/bin/env python3
"""r68 scratch: 4-transport verdict matrix per probe (mirrors transport_leg)."""
import os, re, subprocess, sys, tempfile, threading, time, json
from pathlib import Path

HOLD = 1.0

def error(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]

def leg(args, data=None, stdin=None):
    kw = {"input": data} if data is not None else ({"stdin": stdin} if stdin else {})
    try:
        p = subprocess.run(args, capture_output=True, timeout=10, **kw)
        text, code = p.stderr.decode(errors="replace"), p.returncode
        err = error(text)
    except subprocess.TimeoutExpired as e:
        text = (e.stderr or b"").decode(errors="replace"); code = None
        err = "blocked"
    det = re.search(r"detected file format type `(\S+?)'", text)
    rd = re.search(r"Samples read:\s*(\d+)", text)
    return {"detected": det.group(1) if det else None, "exit": code,
            "samples": int(rd.group(1)) if rd else None, "error": err,
            "last": (text.strip().splitlines() or [""])[-1]}

def matrix(path):
    arms = {}
    arms["file"] = leg(["sox", "-V6", str(path), "-n", "stat"])
    arms["stdin_pipe"] = leg(["sox", "-V6", "-", "-n", "stat"], data=path.read_bytes())
    with path.open("rb") as fh:
        arms["redirected_fd"] = leg(["sox", "-V6", "-", "-n", "stat"], stdin=fh)
    with tempfile.TemporaryDirectory() as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        def feed():
            try:
                with fifo.open("wb") as fh:
                    fh.write(path.read_bytes()); fh.flush(); time.sleep(HOLD)
            except OSError: pass
        w = threading.Thread(target=feed, daemon=True); w.start()
        try:
            arms["fifo_path"] = leg(["sox", "-V6", str(fifo), "-n", "stat"])
        finally:
            w.join(timeout=HOLD + 5)
    return arms

out = {}
for name in sys.argv[1:]:
    p = Path("probes") / name
    out[name] = matrix(p)
    print(f"== {name} ({p.stat().st_size} B)")
    for arm, r in out[name].items():
        print(f"   {arm:14} det={r['detected']} exit={r['exit']} samples={r['samples']} err={r['error']}")
Path("matrix-r68.json").write_text(json.dumps(out, indent=2))
