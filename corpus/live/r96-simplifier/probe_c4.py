#!/usr/bin/env python3
"""r96 simplifier — C4 narrow probe.

Question 1 (deadness): can `_pulsecli_r96_row("sink-inputs", 0)` ever witness
the leg's own stream?  It keys on `application.process.id == "0"`.

Question 2 (liveness of the repair): does the pid-keyed form
`_pulsecli_r96_row("sink-inputs", <child pid>)` return the row of a stream
that child created — i.e. would the repaired predicate fire?

Method (all bounded; own `r96s_<pid>` namespace; name-verified unload):
  1. load a seat null sink through the family's own loader;
  2. run a real `pacat` playback on it and poll BOTH predicates while it is
     live (plus a full pid census of the sink-inputs table);
  3. run the exact `p_malformed` command and poll both predicates around it;
  4. forgery control: `--property=application.process.id=0` — does the server
     let a client claim pid 0 (i.e. is the old predicate merely dead, or
     misdirected?);
  5. evaluate the same predicates through the FOLDED module too (the helper
     must be byte-identical);
  6. teardown + census.

Usage: probe_c4.py BASE_FIXTURE FOLDED_FIXTURE OUT.json
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def pid_census():
    """[(index, application.process.id)] over the live sink-inputs table."""
    try:
        proc = subprocess.run(["pactl", "-f", "json", "list", "sink-inputs"],
                              capture_output=True, timeout=12)
        rows = json.loads(proc.stdout or b"[]")
    except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
        return {"error": str(exc)[:120]}
    return [(r.get("index"),
             (r.get("properties") or {}).get("application.process.id"))
            for r in rows]


def main():
    base_path, folded_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    m = load_module(base_path, "ma_base")
    mf = load_module(folded_path, "ma_folded")
    pid = os.getpid()
    rec = {"base": base_path, "folded": folded_path, "probe_pid": pid,
           "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["helper_source_equal"] = (
        __import__("inspect").getsource(m._pulsecli_r96_row)
        == __import__("inspect").getsource(mf._pulsecli_r96_row))
    name = f"r96s_ns_{pid}"
    tmp = tempfile.mkdtemp(prefix="r96s_c4_")
    procs = []
    loads = {}
    try:
        tone = m._pulsecli_r96_tone(os.path.join(tmp, "r96s_tone.wav"),
                                    3.0, 8192)
        env = m._pulsecli_r96_env()
        loads["ns"] = m._pwcat_r83_ns_load(name)
        rec["load"] = loads["ns"]
        if not (loads["ns"] or {}).get("module_id"):
            rec["verdict"] = "BLOCKED: null sink never enumerated"
            return write(rec, out_path)

        # --- 2. a real live stream -------------------------------------
        argv_live = ["pacat", "--playback", "--device", name,
                     "--format=s16le", "--channels=1", "--rate=48000",
                     "--latency-msec=100", tone]
        live = subprocess.Popen(
            argv_live, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, env=env, start_new_session=True,
            preexec_fn=m._pulsecli_r96_sigreset)
        procs.append(live)
        t0 = time.monotonic()
        row_live = row_live_folded = None
        pid0_live = pid0_live_folded = "unpolled"
        polls = 0
        while time.monotonic() - t0 < 8.0:
            polls += 1
            row_live = m._pulsecli_r96_row("sink-inputs", live.pid)
            row_live_folded = mf._pulsecli_r96_row("sink-inputs", live.pid)
            pid0_live = m._pulsecli_r96_row("sink-inputs", 0)
            pid0_live_folded = mf._pulsecli_r96_row("sink-inputs", 0)
            if row_live is not None:
                break
            if live.poll() is not None:
                break
            time.sleep(0.08)
        rec["live"] = {
            "argv": argv_live[:4] + ["<tone>"], "child_pid": live.pid,
            "polls": polls, "child_alive": live.poll() is None,
            "row_pid_keyed": m._pulsecli_r96_row_view(row_live),
            "row_pid_keyed_folded": m._pulsecli_r96_row_view(row_live_folded),
            "row_pid0": m._pulsecli_r96_row_view(pid0_live),
            "row_pid0_folded": m._pulsecli_r96_row_view(pid0_live_folded),
            "pid0_is_none": pid0_live is None,
            "pid0_is_none_folded": pid0_live_folded is None,
            "pid_census_while_live": pid_census(),
            "pid0_forgery_control": None,
        }

        # --- 3. the exact p_malformed command (family's own _run) ------
        argv_mal = ["pacat", "--playback", "--device", name,
                    "--property=noequals", tone]
        rec["malformed"] = {
            "family_run": m._pulsecli_r96_run(argv_mal, 8.0,
                                              env=m._pulsecli_r96_env(),
                                              keep_chars=700),
        }
        rec["malformed"]["family_run"].pop("stdout", None)
        # a second copy we can watch by pid while it is alive
        mal = subprocess.Popen(
            argv_mal, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, env=env, start_new_session=True,
            preexec_fn=m._pulsecli_r96_sigreset)
        procs.append(mal)
        seen_pid0 = seen_pid_keyed = None
        t0 = time.monotonic()
        while time.monotonic() - t0 < 4.0:
            seen_pid0 = m._pulsecli_r96_row("sink-inputs", 0)
            seen_pid_keyed = m._pulsecli_r96_row("sink-inputs", mal.pid)
            if seen_pid0 is not None or seen_pid_keyed is not None:
                break
            if mal.poll() is not None:
                break
            time.sleep(0.05)
        rec["malformed"]["watched"] = {
            "child_pid": mal.pid, "child_rc": mal.wait(timeout=10),
            "row_pid0": m._pulsecli_r96_row_view(seen_pid0),
            "row_pid_keyed": m._pulsecli_r96_row_view(seen_pid_keyed),
            "row_pid0_is_none": seen_pid0 is None,
            "row_pid_keyed_is_none": seen_pid_keyed is None,
            "pid_census_after": pid_census(),
        }

        # --- 4. forgery control: can a client claim pid 0? --------------
        argv_forge = ["pacat", "--playback", "--device", name,
                      "--property=application.process.id=0",
                      "--latency-msec=100", tone]
        forge = subprocess.Popen(
            argv_forge, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, env=env, start_new_session=True,
            preexec_fn=m._pulsecli_r96_sigreset)
        procs.append(forge)
        forged_row = None
        t0 = time.monotonic()
        while time.monotonic() - t0 < 6.0:
            forged_row = m._pulsecli_r96_row("sink-inputs", 0)
            if forged_row is not None:
                break
            if forge.poll() is not None:
                break
            time.sleep(0.08)
        rec["pid0_forgery_control"] = {
            "child_pid": forge.pid,
            "row_pid0": m._pulsecli_r96_row_view(forged_row),
            "row_pid0_found": forged_row is not None,
            "pid_census": pid_census(),
            "own_pid_row_seen": m._pulsecli_r96_row(
                "sink-inputs", forge.pid) is not None,
        }
    finally:
        for p in procs:
            m._pulsecli_r96_kill(p)
        rec["unload"] = m._pactlmon_r85_unload_own(
            (loads.get("ns") or {}).get("module_id"), "sink_name", name)
        time.sleep(0.4)
        rec["sinks_after"] = m._capture_r77_sink_names_strict()
        names = m._playback_r78_node_names()
        rec["own_nodes_after"] = sorted(
            n for n in (names or [])
            if f"r96s_ns_{pid}" in n or f"r96s_" in n)
        rec["sink_gone"] = (rec["sinks_after"] is not None
                            and name not in rec["sinks_after"])
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)
    return write(rec, out_path)


def write(rec, out_path):
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
    print(json.dumps({k: rec.get(k) for k in
                      ("verdict", "sink_gone", "own_nodes_after")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
