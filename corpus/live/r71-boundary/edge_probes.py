#!/usr/bin/env python3
"""r71-boundary edge probes: what the landed ffprobe transport matrix does NOT
cover. Read-only against tracked corpus bytes; scratch output only.

A) fifo writer-hold sweep for DIRECT ffprobe/ffmpeg on dec_act — does the
   second decoder need the r70 transition band (sox bridge open-#2 deadlock
   was 10/10 blocked at oneshot hold 0)? Reuses the LANDED ffprobe_leg feed
   path verbatim (per-subprocess fifo + writer + reap).

B) truncation / probesize cliffs: minimum detection size per member, the
   hcom->wav->none internal cliff (FSSD@65, HCOM@128 inside a RIFF shell),
   explicit -probesize sweeps, and oversized (>5MB default window) variants
   on file:/pipe:/fifo transports.

C) `pipe:` on a redirected real-file fd on OTHER members (posttable,
   extsuffix_*): the SoX detect-ok/decode-fail anonymous-'-' split — does a
   seekable fd under `pipe:` fork ffmpeg the way SoX's name/pending-buffer
   routing forked? Plus a seekability witness (format=size, lseek strace).

Run: python3 edge_probes.py <probe-a|probe-b|probe-c|all>
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FIXTURE = REPO / "corpus" / "fixtures" / "measure_audio.py"
OUT = Path(__file__).resolve().parent

spec = importlib.util.spec_from_file_location("measure_audio", FIXTURE)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

MEMBERS = {name: REPO / "corpus" / "live" / d / f
           for name, (d, f) in ma.TRANSPORT_R71_MEMBERS.items()}
TMO = ma.TRANSPORT_R71_ARM_TIMEOUT_S  # 15 s — same bound the landed arm uses


def orphans_with(needle: bytes):
    """PIDs whose cmdline carries `needle` (the reap_fifo_orphans sweep,
    read-only version — count, don't kill)."""
    hits = []
    for p in Path("/proc").iterdir():
        if not p.name.isdigit():
            continue
        try:
            cmd = (p / "cmdline").read_bytes()
        except OSError:
            continue
        if needle in cmd:
            hits.append(int(p.name))
    return hits


def _spawn_kw(data=None, stdin=None, stdin_path=None):
    """stdin arrangement for ONE subprocess. stdin_path mirrors the LANDED
    semantics: each subprocess gets a FRESH fd at offset 0 (caller opens one
    per leg). Returns (kwargs, owned_fh_to_close)."""
    if stdin_path is not None:
        fh = open(stdin_path, "rb")
        return {"stdin": fh}, fh
    if data is not None:
        return {"input": data}, None
    if stdin is not None:
        return {"stdin": stdin}, None
    return {}, None


def ffprobe_json(input_spec, extra=(), data=None, stdin=None, stdin_path=None,
                 show=None):
    sel = show or "format=format_name,probe_score"
    cmd = ["ffprobe", "-v", "error", *extra, "-show_entries", sel,
           "-of", "json", input_spec]
    kw, fh = _spawn_kw(data, stdin, stdin_path)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=TMO, **kw)
        out = p.stdout.decode(errors="replace")
        fmt = score = size = None
        if out.strip():
            j = json.loads(out).get("format", {})
            fmt, score, size = (j.get("format_name"), j.get("probe_score"),
                                j.get("size"))
        tail = p.stderr.decode(errors="replace").strip().splitlines()
        return {"ffprobe_format": fmt, "probe_score": score, "size": size,
                "ffprobe_exit": p.returncode,
                "ffprobe_err": tail[-1][-140:] if tail else None}
    except subprocess.TimeoutExpired:
        return {"ffprobe_format": "BLOCKED", "probe_score": None, "size": None,
                "ffprobe_exit": None, "ffprobe_err": f"blocked>{TMO}s"}
    finally:
        if fh is not None:
            fh.close()


def ffmpeg_null(input_spec, extra=(), data=None, stdin=None, stdin_path=None):
    cmd = ["ffmpeg", "-v", "error", *extra, "-i", input_spec, "-f", "null", "-"]
    kw, fh = _spawn_kw(data, stdin, stdin_path)
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=TMO, **kw)
        tail = p.stderr.decode(errors="replace").strip().splitlines()
        return {"ffmpeg_exit": p.returncode,
                "ffmpeg_err": tail[-1][-140:] if tail else None}
    except subprocess.TimeoutExpired:
        return {"ffmpeg_exit": None, "ffmpeg_err": f"blocked>{TMO}s"}
    finally:
        if fh is not None:
            fh.close()


def leg(input_spec, shared_fh=None, **kw):
    """Detection+decode pair. Default: independent stdin per leg —
    stdin_path=<file> opens a FRESH fd each leg (landed semantics).
    shared_fh=<open file> instead hands ONE fd to both legs (the
    fd-consumption artifact the landed docstring warns about)."""
    if shared_fh is not None:
        kw["stdin"] = shared_fh
        kw.pop("stdin_path", None)
    r = {}
    r.update(ffprobe_json(input_spec, **kw))
    r.update(ffmpeg_null(input_spec, **kw))
    return r


# ---------- probe A: fifo writer-hold sweep, direct ffprobe/ffmpeg ----------
def probe_a(reps=10):
    member = "dec_act"
    path = MEMBERS[member]
    data = path.read_bytes()
    print(f"[A] {member} {path.name} {len(data)}B, {reps} reps/hold")
    cells = {}
    for hold in (0, 0.05, 0.2, 0.5, 1.0, 2.0):
        rows = []
        for rep in range(reps):
            with tempfile.TemporaryDirectory(
                    prefix=f"r71b-fifo-h{hold}-") as tmp:
                t0 = time.monotonic()
                # the LANDED fifo arm: ffprobe_leg feed=(dir, name, data, hold)
                row = ma.ffprobe_leg(None, path.name,
                                     feed=(tmp, path.name, data, hold))
                row["elapsed_s"] = round(time.monotonic() - t0, 3)
                row["rep"] = rep
                row["orphans_after"] = orphans_with(str(tmp).encode())
                rows.append(row)
        dist = {}
        for row in rows:
            sig = json.dumps([row["ffprobe_format"], row["probe_score"],
                              row["ffprobe_exit"], row["ffprobe_error"],
                              row["ffmpeg_exit"], row["ffmpeg_error"]])
            dist[sig] = dist.get(sig, 0) + 1
        cells[str(hold)] = {
            "reps": rows,
            "distribution": [
                {"signature": json.loads(s), "count": c}
                for s, c in sorted(dist.items(), key=lambda kv: -kv[1])]}
        print(f"  hold={hold}: {[(d['count'], d['signature'][:2]) for d in cells[str(hold)]['distribution']]}")
    return cells


# ---------- probe B: truncation + probesize + oversized ----------
def probe_b():
    res = {"truncation": {}, "probesize": {}, "oversized": {}}
    grid = [0, 4, 8, 11, 12, 16, 24, 32, 36, 40, 44, 48, 64, 65, 69, 80,
            100, 128, 129, 132, 160, 200, 256, 300, 400, 500, 512, 599, 600]
    for member in ("dec_act", "dec_hcom", "posttable_nomatch"):
        path = MEMBERS[member]
        data = path.read_bytes()
        rows = []
        with tempfile.TemporaryDirectory(prefix="r71b-trunc-") as tmp:
            for n in grid:
                if n > len(data):
                    continue
                cut = Path(tmp) / f"{member}_{n}{path.suffix}"
                cut.write_bytes(data[:n])
                r = leg(str(cut))
                r["bytes"] = n
                rows.append(r)
        res["truncation"][member] = rows
        print(f"[B-trunc] {member}:")
        for r in rows:
            print(f"   {r['bytes']:>4}B fmt={r['ffprobe_format']} "
                  f"score={r['probe_score']} pexit={r['ffprobe_exit']} "
                  f"dexit={r['ffmpeg_exit']} err={(r['ffmpeg_err'] or r['ffprobe_err'] or '')[:70]}")

    # fine grid over the dec_hcom hcom dead-zone (128..176)
    path = MEMBERS["dec_hcom"]
    data = path.read_bytes()
    rows = []
    with tempfile.TemporaryDirectory(prefix="r71b-hcomzone-") as tmp:
        for n in range(128, 177):
            cut = Path(tmp) / f"hcom_{n}.wav"
            cut.write_bytes(data[:n])
            r = leg(str(cut))
            r["bytes"] = n
            rows.append(r)
    res["hcom_zone"] = rows
    print("[B-hcomzone] " + "; ".join(
        f"{r['bytes']}:{r['ffprobe_format']}" for r in rows))

    for member in ("dec_act", "dec_hcom"):
        path = MEMBERS[member]
        rows = []
        for n in (16, 32, 48, 64, 128, 256, 512, 1024, 4096, 65536, 5000000):
            r = leg(str(path), extra=("-probesize", str(n)))
            r["probesize"] = n
            rows.append(r)
        res["probesize"][member] = rows
        print(f"[B-psize] {member}: " + "; ".join(
            f"{r['probesize']}->{r['ffprobe_format']}/{r['probe_score']}/"
            f"d{r['ffmpeg_exit']}" for r in rows))

    # probesize mechanism demo: hcom signature pushed past the probe window.
    # hcom needs FSSD@65 & HCOM@128 inside the buffer ffmpeg actually reads;
    # a 3000-B prefix puts them at 3065/3128 — under -probesize small enough
    # they are never seen. (wav can't test this — its magic must sit at 0.)
    with tempfile.TemporaryDirectory(prefix="r71b-pshift-") as tmp:
        shifted = Path(tmp) / "hcom_shifted.wav"
        shifted.write_bytes(b"\0" * 3000 + MEMBERS["dec_hcom"].read_bytes())
        rows = []
        for n in (2048, 3072, 4096, 5000000):
            r = leg(str(shifted), extra=("-probesize", str(n)))
            r["probesize"] = n
            rows.append(r)
        res["probesize_shifted_hcom"] = rows
        print("[B-pshift] " + "; ".join(
            f"{r['probesize']}->{r['ffprobe_format']}/{r['probe_score']}/"
            f"d{r['ffmpeg_exit']}" for r in rows))

    # oversized: pad dec_act to >5MB default probe window.
    path = MEMBERS["dec_act"]
    data = path.read_bytes()
    with tempfile.TemporaryDirectory(prefix="r71b-oversize-") as tmp:
        big = Path(tmp) / "dec_act_6M.wav"
        big.write_bytes(data + b"\0" * (6_000_000 - len(data)))
        rows = {}
        rows["file"] = leg(str(big))
        rows["stdin_pipe"] = leg("pipe:", data=big.read_bytes())
        rows["redirected_fd"] = leg("pipe:", stdin_path=str(big))
        with big.open("rb") as fh:          # artifact arm: ONE fd, both legs
            rows["redirected_fd_shared_fh"] = leg("pipe:", shared_fh=fh)
        with tempfile.TemporaryDirectory(prefix="r71b-oversize-fifo-") as ft:
            rows["fifo_path"] = ma.ffprobe_leg(
                None, big.name,
                feed=(ft, big.name, big.read_bytes(), 1.0))
        res["oversized"] = rows
        print("[B-oversize] 6MB dec_act+pads: " + "; ".join(
            f"{k}={v['ffprobe_format']}/{v.get('probe_score')}/d{v['ffmpeg_exit']}"
            for k, v in rows.items()))
        # a "true" oversized wav: size fields rewritten to cover the pad
        import struct
        raw = bytearray(data + b"\0" * (6_000_000 - len(data)))
        struct.pack_into("<I", raw, 4, 6_000_000 - 8)
        struct.pack_into("<I", raw, 40, 6_000_000 - 44)
        big2 = Path(tmp) / "dec_act_6M_true.wav"
        big2.write_bytes(bytes(raw))
        r = leg(str(big2))
        res["oversized"]["file_true_size"] = r
        print(f"[B-oversize-true] {r['ffprobe_format']}/{r['probe_score']}/d{r['ffmpeg_exit']} err={r['ffmpeg_err']}")
    return res


# ---------- probe C: `pipe:` on redirected real-file fd ----------
def probe_c():
    res = {}
    for member in ("posttable_nomatch", "txw_piperefuse", "extsuffix_wav",
                   "extsuffix_snd", "dec_act", "dec_hcom"):
        path = MEMBERS[member]
        data = path.read_bytes()
        row = {}
        row["file"] = leg(str(path))
        row["stdin_pipe"] = leg("pipe:", data=data)
        row["redirected_fd"] = leg("pipe:", stdin_path=str(path))
        with path.open("rb") as fh:        # artifact arm: ONE fd, both legs
            row["redirected_fd_shared_fh"] = leg("pipe:", shared_fh=fh)
        res[member] = row
        print(f"[C] {member}: " + "; ".join(
            f"{k}={v['ffprobe_format']}/s{v['probe_score']}/d{v['ffmpeg_exit']}"
            for k, v in row.items()))

    # seekability witness: format=size on `pipe:` real-fd vs `pipe:` pipe.
    wit = {}
    path = MEMBERS["dec_act"]
    wit["pipe_on_fd"] = ffprobe_json(
        "pipe:", stdin_path=str(path),
        show="format=format_name,probe_score,size")
    wit["pipe_on_pipe"] = ffprobe_json(
        "pipe:", data=path.read_bytes(),
        show="format=format_name,probe_score,size")
    wit["file"] = ffprobe_json(
        str(path), show="format=format_name,probe_score,size")
    res["seekability_witness"] = wit
    print("[C-witness] " + json.dumps(wit))

    # truncated-member detect-ok/decode check across the two anonymous arms:
    # dec_act cut mid-data (300B < data claim 556B): does the seekable fd arm
    # fork from the true-pipe arm the way SoX's '-' did?
    cut = {}
    with tempfile.TemporaryDirectory(prefix="r71b-middata-") as tmp:
        p300 = Path(tmp) / "dec_act_300.wav"
        p300.write_bytes(path.read_bytes()[:300])
        cut["file"] = leg(str(p300))
        cut["stdin_pipe"] = leg("pipe:", data=p300.read_bytes())
        cut["redirected_fd"] = leg("pipe:", stdin_path=str(p300))
    res["middata_300B"] = cut
    print("[C-300B] " + "; ".join(
        f"{k}={v['ffprobe_format']}/d{v['ffmpeg_exit']}:{(v['ffmpeg_err'] or v['ffprobe_err'] or '')[:60]}"
        for k, v in cut.items()))
    return res


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    out = {"fixture": str(FIXTURE),
           "git_head": subprocess.run(
               ["git", "-C", str(REPO), "rev-parse", "HEAD"],
               capture_output=True, text=True).stdout.strip(),
           "fixture_dirty": bool(subprocess.run(
               ["git", "-C", str(REPO), "diff", "--name-only",
                "corpus/fixtures/measure_audio.py"],
               capture_output=True, text=True).stdout.strip()),
           "ffmpeg_version": subprocess.run(
               ["ffmpeg", "-version"], capture_output=True, text=True
           ).stdout.splitlines()[0],
           "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if which in ("all", "probe-a"):
        out["probe_a_fifo_hold_sweep"] = probe_a(reps=10)
    if which in ("all", "probe-b"):
        out["probe_b_trunc_probesize"] = probe_b()
    if which in ("all", "probe-c"):
        out["probe_c_redirected_fd"] = probe_c()
    dest = OUT / f"edge_results_{which}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
