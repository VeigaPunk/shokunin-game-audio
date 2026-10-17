#!/usr/bin/env python3
"""r73 reviewer independent replay of the frontier-pipewire consumer claims.

Seat: reviewer (leaf). Writes only inside corpus/live/r73-reviewer/.
Every arm is bounded (timeout -s KILL); nothing is killed by name.
"""
import json
import os
import shlex
import subprocess
import sys
import time
from pathlib import Path

REPO = Path.home() / "Projects/shokunin/audio-shokunin"
SCRATCH = REPO / "corpus/live/r73-reviewer"
MEMBERS = {
    "pair_dec_hcom": REPO / "corpus/live/round-66/pair_dec_hcom.wav",
    "pair_dec_act": REPO / "corpus/live/round-66/pair_dec_act.wav",
    "pair_lengate_gsrt_25": REPO / "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "txw_piperefuse": REPO / "corpus/live/round-68/txw_piperefuse.wav",
    "extsuffix_nomatch_wav": REPO / "corpus/live/round-69/extsuffix_nomatch.wav",
    "extsuffix_nomatch_txw": REPO / "corpus/live/round-69/extsuffix_nomatch.txw",
}
TONE = SCRATCH / "tone4s.wav"
EMPTYRT = SCRATCH / "emptyrt"

results = []


def run(cmd, timeout, env=None, stdin=None, cwd=None, wall=True):
    t0 = time.monotonic()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           env=env, stdin=stdin, cwd=cwd)
        rc, out, err = p.returncode, p.stdout, p.stderr
        killed = False
    except subprocess.TimeoutExpired as e:
        rc, killed = "TIMEOUT", True
        out = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = (e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
    wall_s = round(time.monotonic() - t0, 2) if wall else None
    return {"cmd": " ".join(shlex.quote(c) for c in cmd), "rc": rc, "timeout": killed,
            "wall_s": wall_s, "stdout": out, "stderr": err}


def pwcat_file(member):
    r = run(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(MEMBERS[member])], 25)
    r.update({"arm": "pwcat-file", "member": member})
    return r


def pwcat_fifo(member, writer_delay=0.3, chunk=None, chunk_gap=0.0, empty_writer=False):
    fifo = SCRATCH / f"fifo-{member}"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    label = "pwcat-fifo"
    if empty_writer:
        label += "-empty"
    if chunk:
        label += "-chunked"
    # start reader first (it blocks in open()), then attach the writer
    t0 = time.monotonic()
    reader = subprocess.Popen(["timeout", "-s", "KILL", "15", "pw-cat", "-p", str(fifo)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    time.sleep(writer_delay)
    if empty_writer:
        writer = subprocess.Popen(["true"], stdout=open(fifo, "wb"))
    elif chunk:
        code = ("import sys,time\n"
                "d=open(sys.argv[1],'rb').read()\n"
                "f=open(sys.argv[2],'wb',buffering=0)\n"
                "for i in range(0,len(d),int(sys.argv[3])):\n"
                "    f.write(d[i:i+int(sys.argv[3])]); time.sleep(float(sys.argv[4]))\n"
                "f.close()\n")
        writer = subprocess.Popen([sys.executable, "-c", code, str(MEMBERS[member]), str(fifo),
                                   str(chunk), str(chunk_gap)])
    else:
        writer = subprocess.Popen(["cat", str(MEMBERS[member])], stdout=open(fifo, "wb"))
    try:
        out, err = reader.communicate(timeout=20)
        rc, killed = reader.returncode, False
    except subprocess.TimeoutExpired:
        reader.kill()
        out, err = reader.communicate()
        rc, killed = "TIMEOUT", True
    wall_s = round(time.monotonic() - t0, 2)
    try:
        writer.wait(timeout=5)
    except subprocess.TimeoutExpired:
        writer.kill()
    fifo.unlink()
    return {"arm": label, "member": member, "cmd": f"pw-cat -p {fifo.name} <writer>",
            "rc": rc, "timeout": killed, "wall_s": wall_s, "writer_rc": writer.returncode,
            "stdout": out, "stderr": err}


def pwcat_fifo_no_writer():
    fifo = SCRATCH / "fifo-nowriter"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    r = run(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(fifo)], 20)
    r.update({"arm": "pwcat-fifo-no-writer", "member": None})
    fifo.unlink()
    return r


def pwcat_nodaemon(member):
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(EMPTYRT))
    r = run(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(MEMBERS[member])], 20, env=env)
    r.update({"arm": "pwcat-nodaemon", "member": member})
    return r


def pwcat_nodaemon_fifo():
    fifo = SCRATCH / "fifo-nodaemon"
    if fifo.exists():
        fifo.unlink()
    os.mkfifo(fifo)
    env = dict(os.environ, PIPEWIRE_RUNTIME_DIR=str(EMPTYRT))
    r = run(["timeout", "-s", "KILL", "8", "pw-cat", "-p", str(fifo)], 20, env=env)
    r.update({"arm": "pwcat-nodaemon-fifo", "member": None})
    fifo.unlink()
    return r


def mpv_arm(member, transport):
    log = SCRATCH / f"mpv-{transport}-{member}.log"
    target = str(MEMBERS[member]) if transport == "file" else str(SCRATCH / f"fifo-mpv-{member}")
    if transport == "fifo":
        fifo = SCRATCH / f"fifo-mpv-{member}"
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        reader = subprocess.Popen(
            ["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null", "--ao=null",
             "--audio-display=no", "--really-quiet", f"--log-file={log}", str(fifo)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(0.3)
        writer = subprocess.Popen(["cat", str(MEMBERS[member])], stdout=open(fifo, "wb"))
        try:
            out, err = reader.communicate(timeout=20)
            rc, killed = reader.returncode, False
        except subprocess.TimeoutExpired:
            reader.kill()
            out, err = reader.communicate()
            rc, killed = "TIMEOUT", True
        try:
            writer.wait(timeout=5)
        except subprocess.TimeoutExpired:
            writer.kill()
        fifo.unlink()
        return {"arm": f"mpv-{transport}", "member": member, "rc": rc, "timeout": killed,
                "stdout": out, "stderr": err, "log": str(log.relative_to(REPO))}
    r = run(["timeout", "-s", "KILL", "15", "mpv", "--no-config", "--vo=null", "--ao=null",
             "--audio-display=no", "--really-quiet", f"--log-file={log}", target], 25)
    r.update({"arm": f"mpv-{transport}", "member": member,
              "log": str(log.relative_to(REPO))})
    return r


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "pwcat-file"):
        for m in MEMBERS:
            results.append(pwcat_file(m))
    if which in ("all", "pwcat-fifo"):
        for m in ("pair_dec_hcom", "pair_dec_act", "txw_piperefuse", "extsuffix_nomatch_wav"):
            results.append(pwcat_fifo(m))
        results.append(pwcat_fifo("pair_dec_hcom", empty_writer=True))
        results.append(pwcat_fifo("pair_dec_hcom", chunk=1600, chunk_gap=0.2))
    if which in ("all", "pwcat-bounds"):
        results.append(pwcat_fifo_no_writer())
        results.append(pwcat_nodaemon("pair_dec_hcom"))
        results.append(pwcat_nodaemon_fifo())
    if which in ("all", "mpv"):
        for m in ("pair_dec_hcom", "txw_piperefuse", "extsuffix_nomatch_wav"):
            results.append(mpv_arm(m, "file"))
            results.append(mpv_arm(m, "fifo"))
    out = SCRATCH / f"replay-{which}.json"
    out.write_text(json.dumps(results, indent=1))
    for r in results:
        err = (r.get("stderr") or "").strip().replace("\n", " | ")[-160:]
        print(f"{r['arm']:24s} {str(r.get('member')):22s} rc={str(r['rc']):8s} "
              f"wall={r.get('wall_s')} err={err}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
