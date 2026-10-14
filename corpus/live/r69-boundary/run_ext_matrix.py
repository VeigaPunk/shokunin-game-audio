#!/usr/bin/env python3
"""r69 boundary: EXTENSION-SUFFIX edge matrix on no-match bytes.

Member-independent mechanism probe (raw `sox -V6` CLI, not the author modes).
Same byte buffer renamed under edge names x {file, fifo_path, stdin_pipe,
redirected_fd}. Verdict = (detected, route, exit, samples, normalized error).

Byte variants:
  nm_ascii - data[0]='u' (no .snd gate possible; r68 posttable_nomatch shape)
  nm_z2    - data[0]=0, data[1]=0, data[7]=0  -> arms the ext-gated sndr CHECK
  nm_z2x   - data[0]=0, data[1]=0, data[7]=1  -> sndr CHECK fails -> .snd post-table
All three verified no-CHECK-match on the anonymous '-' transport at runtime.
"""
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROBES = HERE / "probes"
RUNS = HERE / "runs"
LOGS = RUNS / "logs"
TIMEOUT_S = 10
FIFO_HOLD_S = 1.0


def make_members():
    PROBES.mkdir(parents=True, exist_ok=True)
    # deterministic pad avoiding table magic at every covered offset:
    # byte i = (0x11 + 7*i) & 0xff  (same family as r68's ramp)
    pad = bytes((0x11 + 7 * i) & 0xFF for i in range(512))
    ascii_head = b"ufo-r69 boundary ext-suffix no-match member: ascii lead\n"
    z2 = bytearray(pad)
    z2[0] = 0
    z2[1] = 0
    z2[7] = 0
    z2x = bytearray(z2)
    z2x[7] = 0x21
    members = {
        "nm_ascii": ascii_head + pad[: 512 - len(ascii_head)],
        "nm_z2": bytes(z2),
        "nm_z2x": bytes(z2x),
    }
    for name, data in members.items():
        (PROBES / name).write_bytes(data)
    return members


# name -> (suffix applied to member stem). "." entries are literal basenames.
NAMES = [
    "m.wav", "m.WAV", "m.Wav", "m.wAv",
    "m.bin", "m.BIN",
    "m.txw", "m.TXW",
    "m.f32", "m.F32",
    "m.snd", "m.SND", "m.Snd", "m.au",
    "m.tar.gz", "m.snd.gz", "m.tar.snd",
    "m.mp3", "m.ogg", "m.aptx", "m.dts",
    "m.", "m", "m..wav", ".wav", ".snd",
]
# extra byte variants only where the name can interact with byte gates:
# ext 'snd' (any case) arms the sndr CHECK row; '.au' exercises the sibling
# post-table handler for contrast.
SND_VARIANT_NAMES = ["m.snd", "m.SND", "m.Snd", ".snd", "m.tar.snd", "m.snd.gz", "m.au"]


def norm_error(text):
    fails = [l for l in text.strip().splitlines() if "sox FAIL" in l]
    if not fails:
        return None
    m = re.search(r"':\s*(.*)$", fails[-1])
    return m.group(1) if m else fails[-1]


def leg(args, data=None, stdin=None, log=None):
    kw = {"input": data} if data is not None else ({"stdin": stdin} if stdin else {})
    try:
        p = subprocess.run(args, capture_output=True, timeout=TIMEOUT_S, **kw)
        text = p.stderr.decode(errors="replace")
        code = p.returncode
        err = norm_error(text)
    except subprocess.TimeoutExpired as e:
        text = (e.stderr or b"").decode(errors="replace")
        code = None
        err = f"blocked: no verdict within {TIMEOUT_S} s"
    if log is not None:
        log.write_text(text)
    det = re.search(r"detected file format type `(\S+?)'", text)
    read = re.search(r"Samples read:\s*(\d+)", text)
    tail = text.strip().splitlines()
    return {
        "detected": det.group(1) if det else None,
        "route": ("ffmpeg" if (det and det.group(1) == "act") or "(ffmpeg)" in text
                  else "native" if det else "none"),
        "exit": code,
        "samples": int(read.group(1)) if read else None,
        "error": err,
        "tail": (re.sub(r"`[^']*'", "`<input>'",
                        re.sub(r" @ 0x[0-9a-f]+\]", "]", tail[-1]))[-140:]
                 if tail else ""),
    }


def matrix(path):
    arms = {}
    arms["file"] = leg(["sox", "-V6", str(path), "-n", "stat"],
                       log=LOGS / f"{path.name}__file.log")
    arms["stdin_pipe"] = leg(["sox", "-V6", "-", "-n", "stat"],
                             data=path.read_bytes(),
                             log=LOGS / f"{path.name}__stdin_pipe.log")
    with path.open("rb") as fh:
        arms["redirected_fd"] = leg(["sox", "-V6", "-", "-n", "stat"], stdin=fh,
                                    log=LOGS / f"{path.name}__redirected_fd.log")
    with tempfile.TemporaryDirectory(prefix="r69-ext-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)

        def feed():
            try:
                with fifo.open("wb") as fh:
                    fh.write(path.read_bytes())
                    fh.flush()
                    time.sleep(FIFO_HOLD_S)
            except OSError:
                pass

        t = threading.Thread(target=feed, daemon=True)
        t.start()
        try:
            arms["fifo_path"] = leg(["sox", "-V6", str(fifo), "-n", "stat"],
                                    log=LOGS / f"{path.name}__fifo_path.log")
        finally:
            t.join(timeout=FIFO_HOLD_S + 5)
    return arms


def sig(a):
    return (a["detected"], a["route"], a["exit"], a["samples"], a["error"])


def main():
    members = make_members()
    LOGS.mkdir(parents=True, exist_ok=True)
    rows = []
    t0 = time.time()
    for member in members:
        names = NAMES if member == "nm_ascii" else SND_VARIANT_NAMES
        for name in names:
            path = PROBES / f"{member}__{name}"
            path.write_bytes(members[member])
            arms = matrix(path)
            groups = {}
            for tr in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
                groups.setdefault(sig(arms[tr]), []).append(tr)
            for transports, s in groups.items():
                pass
            row = {"member": member, "name": name, "ngroups": len(groups)}
            for tr in ("file", "stdin_pipe", "redirected_fd", "fifo_path"):
                a = arms[tr]
                row[tr] = "|".join(str(x) for x in sig(a))
            rows.append(row)
            print(f"{member:8s} {name:12s} groups={len(groups)} "
                  + "  ".join(f"{tr}={row[tr]}" for tr in
                             ("file", "stdin_pipe", "redirected_fd", "fifo_path")))
    out = RUNS / "ext_matrix.tsv"
    with out.open("w") as fh:
        fh.write("member\tname\tngroups\tfile\tstdin_pipe\tredirected_fd\tfifo_path\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) for k in
                               ("member", "name", "ngroups", "file", "stdin_pipe",
                                "redirected_fd", "fifo_path")) + "\n")
    print(f"\n{len(rows)} member-name rows in {time.time()-t0:.1f}s -> {out}")


if __name__ == "__main__":
    sys.exit(main())
