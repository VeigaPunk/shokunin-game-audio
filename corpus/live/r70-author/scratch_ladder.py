#!/usr/bin/env python3
"""r70-author scratch: coarse fifo writer-hold ladder on dec_act.

Same mechanism as measure_audio.py transport_matrix() fifo arm, plus a
chunked-feed variant. Popen in a new session + killpg so a blocked ffmpeg
bridge child (open #2 on a writerless fifo) cannot orphan.
"""
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
MEMBER = ROOT / "corpus" / "live" / "round-66" / "pair_dec_act.wav"
TIMEOUT = 10.0
CHUNK_BYTES, CHUNK_GAP = 100, 0.05


def terr(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def leg(hold, feed):
    data = MEMBER.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r70auth-") as tmp:
        fifo = Path(tmp) / MEMBER.name
        os.mkfifo(fifo)

        def writer():
            try:
                with fifo.open("wb") as fh:
                    if feed == "chunked":
                        for i in range(0, len(data), CHUNK_BYTES):
                            fh.write(data[i:i + CHUNK_BYTES])
                            fh.flush()
                            time.sleep(CHUNK_GAP)
                    else:
                        fh.write(data)
                        fh.flush()
                    time.sleep(hold)
            except OSError:
                pass

        t = threading.Thread(target=writer, daemon=True)
        t0 = time.monotonic()
        t.start()
        proc = subprocess.Popen(["sox", "-V6", str(fifo), "-n", "stat"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        blocked = False
        try:
            _, err = proc.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            blocked = True
            os.killpg(proc.pid, signal.SIGKILL)
            _, err = proc.communicate()
        wall = time.monotonic() - t0
        text = err.decode(errors="replace")
        t.join(timeout=hold + 6)
    det = re.search(r"detected file format type `(\S+?)'", text)
    read = re.search(r"Samples read:\s*(\d+)", text)
    return {"hold": hold, "feed": feed,
            "det": det.group(1) if det else None,
            "exit": None if blocked else proc.returncode,
            "samples": int(read.group(1)) if read else None,
            "err": f"blocked: no verdict within {TIMEOUT} s" if blocked else terr(text),
            "wall": round(wall, 3)}


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    holds = [float(x) for x in (sys.argv[2].split(",") if len(sys.argv) > 2
                                else "0,0.05,0.2,0.5,1.0,2.0".split(","))]
    feeds = sys.argv[3].split(",") if len(sys.argv) > 3 else ["oneshot", "chunked"]
    rows = []
    for feed in feeds:
        for h in holds:
            for r in range(reps):
                row = leg(h, feed)
                row["rep"] = r
                rows.append(row)
                print(f"{feed:8s} h={h:<5} rep{r}: exit={row['exit']} "
                      f"det={row['det']} samples={row['samples']} "
                      f"wall={row['wall']} err={row['err']!r}", flush=True)
    out = Path(__file__).parent / "scratch_ladder.json"
    out.write_text(json.dumps(rows, indent=1) + "\n")
    print("WROTE", out)


if __name__ == "__main__":
    main()
