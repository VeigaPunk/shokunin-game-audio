#!/usr/bin/env python3
"""r72-scout: libsndfile 1.2.2 verdict matrix on the canonical 9-member
transport corpus (TRANSPORT_R71_MEMBERS), in the r71 ffprobe-arm shape.

Arms (mirroring TRANSPORT_R67_ARMS, one fresh child process per leg so the
15 s r71 arm timeout bounds the blocking ctypes calls):
  file          sf_open(member path)                 named,   seekable
  stdin_pipe    sf_open_fd(0) with member bytes piped unnamed, unseekable
  redirected_fd sf_open_fd(0) with member file as fd unnamed, seekable
  fifo_path     sf_open(fifo path) + writer thread   named,   unseekable
                (r67/r70 protocol: one-shot write + writer lingers hold_s)

Detection = SF_INFO.format (sf_command name tables); decode = sf_readf_short
count. CLI cross-checks on named arms: sndfile-info (stdout parsed) and
sndfile-convert (file arm only). Read-only against tracked corpus bytes;
writes scratch JSON + logs only.

Usage: sndfile_matrix.py [tag]
"""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]                      # audio-shokunin
sys.path.insert(0, str(ROOT / "corpus" / "fixtures"))
import measure_audio as MA                  # noqa: E402  (protocol reuse)

OUT = HERE / "runs"
LOGS = HERE / "logs"
TRANSPORTS = ("file", "stdin_pipe", "redirected_fd", "fifo_path")
TIMEOUT_S = MA.TRANSPORT_R71_ARM_TIMEOUT_S
LEG = str(HERE / "sndfile_leg.py")


def run_child(mode, path=None, data=None, stdin=None):
    argv = [sys.executable, LEG, mode] + ([str(path)] if path else [])
    kw = {"input": data} if data is not None else ({"stdin": stdin} if stdin else {})
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=TIMEOUT_S,
                              **kw)
        out = proc.stdout.decode(errors="replace")
        try:
            leg = json.loads(out)
        except json.JSONDecodeError:
            leg = {"opened": None, "error": "unparseable child json: "
                   + (out.strip()[-120:] or proc.stderr.decode(errors="replace")[-120:])}
        leg["timeout"] = None
        leg["child_exit"] = proc.returncode
        return leg
    except subprocess.TimeoutExpired:
        return {"opened": None, "error": f"blocked: no verdict within {TIMEOUT_S} s",
                "timeout": True, "child_exit": None}


def clean_tail(text):
    text = re.sub(r"0x[0-9a-f]+", "0x<addr>", text)
    lines = text.strip().splitlines()
    return lines[-1][-160:] if lines else None


def info_leg(path, log_name):
    """sndfile-info CLI cross-check. Exits 0 even on failure -- verdicts are
    stdout text ('Error : Not able to open input file' / 'Format not
    recognised.')."""
    try:
        proc = subprocess.run(["sndfile-info", str(path)], capture_output=True,
                              timeout=TIMEOUT_S)
        out = proc.stdout.decode(errors="replace")
        err = proc.stderr.decode(errors="replace")
    except subprocess.TimeoutExpired:
        return {"sndfile_info_exit": None, "sndfile_info_error":
                f"blocked: no verdict within {TIMEOUT_S} s"}
    LOGS.mkdir(exist_ok=True)
    log_rel = f"logs/info-{log_name}.txt"
    (LOGS / f"info-{log_name}.txt").write_text(out + err)
    fmt = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                if re.match(r"^Format\s*:", l)), None)
    frames = next((l.split(":", 1)[1].strip() for l in out.splitlines()
                   if re.match(r"^Frames\s*:", l)), None)
    error = next((l.strip() for l in out.splitlines()
                  if l.startswith("Error :")), None)
    if error is not None:                      # normalize the concrete path
        error = re.sub(r"input file .*$", "input file <input>.", error)
    if "Format not recognised." in out:
        error = "Format not recognised."
    elif "File contains data in an unimplemented format." in out:
        error = "File contains data in an unimplemented format."
    return {"sndfile_info_exit": proc.returncode, "sndfile_info_format": fmt,
            "sndfile_info_frames": frames, "sndfile_info_error": error,
            "log": log_rel}


def convert_leg(path):
    """sndfile-convert CLI decode cross-check (file arm only). Exit code
    propagates (1 on reject, 0 on convert) unlike sndfile-info."""
    with tempfile.TemporaryDirectory(prefix="r72-convert-") as tmp:
        outp = Path(tmp) / "out.wav"
        try:
            proc = subprocess.run(["sndfile-convert", str(path), str(outp)],
                                  capture_output=True, timeout=TIMEOUT_S)
        except subprocess.TimeoutExpired:
            return {"sndfile_convert_exit": None, "sndfile_convert_error":
                    f"blocked: no verdict within {TIMEOUT_S} s"}
        return {"sndfile_convert_exit": proc.returncode,
                "sndfile_convert_error": clean_tail(proc.stderr.decode(errors="replace")),
                "sndfile_convert_out_bytes": outp.stat().st_size if outp.exists() else 0}


def matrix(member, path):
    data = path.read_bytes()
    rel = str(path.relative_to(MA.ROOT))
    arms = {}
    arms["file"] = run_child("path", path=path)
    arms["file"]["input"] = rel
    arms["stdin_pipe"] = run_child("fd", data=data)
    arms["stdin_pipe"]["input"] = "pipe"
    with path.open("rb") as fh:
        arms["redirected_fd"] = run_child("fd", stdin=fh)
    arms["redirected_fd"]["input"] = "fd"
    with tempfile.TemporaryDirectory(prefix="transport-r72-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        hold = MA.fifo_writer_hold_s()
        writer = threading.Thread(target=MA.fifo_feed,
                                  args=(fifo, data, hold), daemon=True)
        writer.start()
        try:
            arms["fifo_path"] = run_child("path", path=fifo)
            arms["fifo_path"]["input"] = path.name
        finally:
            writer.join(timeout=hold + 5)
            MA.reap_fifo_orphans(fifo)
            fifo.unlink(missing_ok=True)
    for transport, named, seekable in MA.TRANSPORT_R67_ARMS:
        arms[transport]["named"] = named
        arms[transport]["seekable"] = seekable
    return rel, arms


def cli_cross_checks(member, path):
    data = path.read_bytes()
    out = {"info_file": info_leg(path, f"{member}-file")}
    with tempfile.TemporaryDirectory(prefix="transport-r72-cli-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        hold = MA.fifo_writer_hold_s()
        writer = threading.Thread(target=MA.fifo_feed,
                                  args=(fifo, data, hold), daemon=True)
        writer.start()
        try:
            out["info_fifo"] = info_leg(fifo, f"{member}-fifo")
        finally:
            writer.join(timeout=hold + 5)
            MA.reap_fifo_orphans(fifo)
            fifo.unlink(missing_ok=True)
    out["convert_file"] = convert_leg(path)
    return out


def norm_error(err):
    return None if err in (None, "No Error.") else err


def entry(member, path, cli):
    rel, arms = matrix(member, path)
    groups, dgroups = [], []
    for t in TRANSPORTS:
        a = arms[t]
        sig = (a.get("format_name"), a.get("read_frames"),
               norm_error(a.get("error")), a.get("timeout"))
        dsig = (a.get("format_name"), norm_error(a.get("error")),
                a.get("timeout"))
        for g in groups:
            if g[0] == sig:
                g[1].append(t)
                break
        else:
            groups.append((sig, [t]))
        for g in dgroups:
            if g[0] == dsig:
                g[1].append(t)
                break
        else:
            dgroups.append((dsig, [t]))
    e = {"path": rel, "pair_member": member, "decoder": "libsndfile-1.2.2",
         "transport_axis": arms,
         "transport_protocol": {"arm_timeout_s": TIMEOUT_S,
                                "fifo_writer_hold_s": MA.fifo_writer_hold_s(),
                                "fifo_feed": "one-shot write then writer lingers",
                                "leg": "sf_open/sf_open_fd + sf_readf_short (child process per leg)",
                                "detection": "SF_INFO.format via sf_command name tables",
                                "decode": "sf_readf_short frame count"},
         "transport_verdict_groups": [
             {"transports": ts, "sndfile_format": s[0],
              "sndfile_read_frames": s[1], "sndfile_error": s[2],
              "timeout": s[3]} for s, ts in groups],
         "sndfile_detect_groups": [
             {"transports": ts, "sndfile_format": s[0], "sndfile_error": s[1],
              "timeout": s[2]} for s, ts in dgroups],
         "cli_cross_checks": cli,
         "transport_fork": len(groups) > 1,
         "failures": []}
    if e["transport_fork"]:
        desc = " vs ".join("/".join(ts) + "=" + (s[2] or f"{s[0]}:{s[1]} fr")
                           for s, ts in groups)
        e["failures"].append(
            f"transport: libsndfile verdict forks across transports ({desc})")
    return e


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "run"
    OUT.mkdir(exist_ok=True)
    members = MA.TRANSPORT_R71_MEMBERS
    out = {"protocol": {"arm_timeout_s": TIMEOUT_S,
                        "fifo_writer_hold_s": MA.fifo_writer_hold_s(),
                        "libsndfile": "1.2.2",
                        "member_set": "TRANSPORT_R71_MEMBERS (r71 canonical 9)"},
           "members": {}}
    for member, (directory, filename) in members.items():
        path = MA.ROOT / "live" / directory / filename
        cli = cli_cross_checks(member, path)
        e = entry(member, path, cli)
        out["members"][member] = e
        print(f"== {member} ({filename})", file=sys.stderr)
        for t in TRANSPORTS:
            a = e["transport_axis"][t]
            print(f"   {t:14s} open={a.get('opened')} "
                  f"fmt={a.get('format_name')} read={a.get('read_frames')} "
                  f"err={norm_error(a.get('error'))} "
                  f"cli_info={cli['info_file']['sndfile_info_error'] or cli['info_file']['sndfile_info_format']} "
                  f"convert_exit={cli['convert_file']['sndfile_convert_exit']}",
                  file=sys.stderr)
    p = OUT / f"sndfile-matrix-{tag}.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
