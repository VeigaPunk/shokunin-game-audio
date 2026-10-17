#!/usr/bin/env python3
"""r74 reviewer — secondary cell (ii): mpv --start=N position fork.
file arm seeks (plays from N); fifo arm cannot seek (plays from 0).
Measured via --ao=pcm byte counts. Independent of the fixture."""
import json, os, subprocess, sys, tempfile, threading, time
from pathlib import Path
TIMEOUT = 15
def feed(fifo, data, hold):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data); fh.flush(); time.sleep(hold)
    except OSError: pass
def leg(path, transport, data, start, hold=1.0):
    with tempfile.TemporaryDirectory(prefix="rv-start-") as tmp:
        out = Path(tmp) / "played.wav"
        argv = ["mpv", "--no-config", "--vo=null", "--audio-display=no",
                "--really-quiet", "--ao=pcm", f"--ao-pcm-file={out}",
                f"--start={start}"]
        if transport == "file":
            argv.append(str(path)); kw = {}
        else:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            w = threading.Thread(target=feed, args=(fifo, data, hold), daemon=True)
            w.start(); argv.append(str(fifo)); kw = {}
        try:
            p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT, **kw)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = None
        finally:
            if transport == "fifo_path": w.join(timeout=hold+5)
        played = out.stat().st_size if out.exists() else 0
        return {"transport": transport, "start_s": start, "exit_code": rc,
                "played_bytes": played}
if __name__ == "__main__":
    path = Path(sys.argv[1]).resolve(); data = path.read_bytes()
    res = {"member": sys.argv[1], "legs": []}
    for start in (0, 0.5):
        for t in ("file", "fifo_path"):
            res["legs"].append(leg(path, t, data, start))
    print(json.dumps(res, indent=1))
