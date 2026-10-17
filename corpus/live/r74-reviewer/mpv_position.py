#!/usr/bin/env python3
"""r74 reviewer — positional wound-shape probe: how much audio does mpv
actually play per transport? `--ao=pcm --ao-pcm-file=<out>` writes decoded
PCM; compare byte counts file vs fifo. Independent of the fixture.

Usage: mpv_position.py <member> ...
"""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

TIMEOUT = 15


def feed(fifo, data, hold):
    try:
        with open(fifo, "wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold)
    except OSError:
        pass


def leg(path, transport, data, hold):
    with tempfile.TemporaryDirectory(prefix="rv-pos-") as tmp:
        out = Path(tmp) / "played.wav"
        argv = ["mpv", "--no-config", "--vo=null", "--audio-display=no",
                "--really-quiet", "--ao=pcm", f"--ao-pcm-file={out}"]
        if transport == "file":
            argv.append(str(path))
            kw = {}
        elif transport == "stdin_pipe":
            argv.append("-")
            kw = {"input": data}
        else:
            fifo = Path(tmp) / path.name
            os.mkfifo(fifo)
            w = threading.Thread(target=feed, args=(fifo, data, hold), daemon=True)
            w.start()
            argv.append(str(fifo))
            kw = {}
        try:
            p = subprocess.run(argv, capture_output=True, timeout=TIMEOUT, **kw)
            rc = p.returncode
        except subprocess.TimeoutExpired:
            rc = None
        finally:
            if transport == "fifo_path":
                w.join(timeout=hold + 5)
        played = out.stat().st_size if out.exists() else 0
        return {"transport": transport, "exit_code": rc, "played_bytes": played}


def main():
    for name in sys.argv[1:]:
        path = Path(name).resolve()
        data = path.read_bytes()
        legs = {t: leg(path, t, data, 1.0) for t in ("file", "fifo_path")}
        print(json.dumps({"member": name, "legs": legs}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
