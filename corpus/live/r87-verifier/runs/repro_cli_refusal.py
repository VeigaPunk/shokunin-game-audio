#!/usr/bin/env python3
"""r87-verifier mechanism repro (verifier-owned; no fixture import).

Question: the r87 `create_badfac` / `create_usage` arms send a refusal
create-node into a held pw-cli session, sleep 1.6 s, send `quit`, and
then require the refusal text ("res:-2" / "usage: factory.name=") to be
present in the last 500 chars of the merged session log. Five runs in
this wave failed at least one of those two arms. This repro measures,
with the verifier's own code:

  (a) whether the refusal text is printed at all, and at what latency
      after the command is written;
  (b) whether it is inside the last-500-char window at the harness's
      sampling point (t+1.6 s);
  (c) whether foreign registry-event churn (short-lived pw-cli clients,
      exactly what concurrent seats produce) pushes the refusal text out
      of that window;
  (d) what the full session log looks like at quit.

Commands used are pure refusals (missing / bogus factory.name) — no node
is created, nothing is torn down. Read-only churn clients (`pw-cli ls
Node`) only. Usage: repro_cli_refusal.py [reps]
"""
import json
import subprocess
import sys
import threading
import time

BADFAC = 'create-node adapter { factory.name="no_such_r87v_factory" }'
USAGE = 'create-node adapter { }'
CASES = (("create_badfac", BADFAC, "res:-2"),
         ("create_usage", USAGE, "usage: factory.name="))


def open_session():
    proc = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            start_new_session=True)
    chunks = []

    def drain():
        try:
            while True:
                b = proc.stdout.read(65536)
                if not b:
                    return
                chunks.append(b)
        except (OSError, ValueError):
            return

    threading.Thread(target=drain, daemon=True).start()
    return proc, chunks


def logof(chunks):
    return b"".join(chunks).decode(errors="replace")


def send(proc, line):
    proc.stdin.write(line.encode() + b"\n")
    proc.stdin.flush()


def close(proc, chunks, bound_s=8.0):
    try:
        send(proc, "quit")
    except (BrokenPipeError, OSError, ValueError):
        pass
    try:
        proc.stdin.close()
    except OSError:
        pass
    try:
        proc.wait(timeout=bound_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=3)
    time.sleep(0.3)
    return logof(chunks)


def churn(n=6):
    """Short-lived read-only pw-cli clients: each connect/disconnect is a
    registry event in every held session on the host."""
    procs = []
    for _ in range(n):
        procs.append(subprocess.Popen(["pw-cli", "ls", "Node"],
                                      stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL,
                                      stdin=subprocess.DEVNULL,
                                      start_new_session=True))
    for p in procs:
        try:
            p.wait(timeout=10)
        except subprocess.TimeoutExpired:
            p.kill()


def rep(cmd, marker, sample_s=1.6, bound_s=12.0, do_churn=False,
        warmup=1.2):
    proc, chunks = open_session()
    time.sleep(warmup)
    t0 = time.monotonic()
    send(proc, cmd)
    seen_at = None
    window_at_sample = None
    loglen_at_sample = None
    window_after_churn = None
    churn_at = None
    while True:
        t = time.monotonic() - t0
        L = logof(chunks)
        if seen_at is None and marker in L:
            seen_at = t
        if do_churn and churn_at is None and t >= 0.25:
            churn_at = t
            churn(6)
            time.sleep(0.15)
            L2 = logof(chunks)
            window_after_churn = marker in L2[-500:]
        if t >= sample_s and window_at_sample is None:
            window_at_sample = marker in L[-500:]
            loglen_at_sample = len(L)
            if seen_at is not None and not do_churn:
                break
        if t >= bound_s:
            break
        time.sleep(0.05)
    final = close(proc, chunks)
    return {
        "marker": marker,
        "seen_at_all": marker in final,
        "seen_at_s": None if seen_at is None else round(seen_at, 3),
        "in_last500_at_sample": window_at_sample,
        "log_bytes_at_sample": loglen_at_sample,
        "in_last500_after_churn": window_after_churn,
        "in_last500_final": marker in final[-500:],
        "final_log_bytes": len(final),
        "tail_after_marker": (len(final) - final.index(marker)
                              if marker in final else None),
        "churn": do_churn,
        "tail": final[-400:],
    }


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    out = {"host_loadavg_at_start": open("/proc/loadavg").read().strip(),
           "reps": []}
    for i in range(reps):
        for name, cmd, marker in CASES:
            for do_churn in (False, True):
                r = rep(cmd, marker, do_churn=do_churn)
                r["case"] = name
                r["rep"] = i
                out["reps"].append(r)
                print(json.dumps({k: v for k, v in r.items()
                                  if k != "tail"}))
        print(f"# rep {i} done", file=sys.stderr)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
