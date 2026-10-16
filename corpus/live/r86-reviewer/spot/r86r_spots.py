#!/usr/bin/env python3
"""r86 reviewer — independent spot battery on this host.

Re-measures the sharpest r86 claims with the reviewer's OWN code and its
OWN `r86r_<pid>` namespace (no fixture import): the addressing split,
the pw-dump silent-empty surface, the pw-cli stdin trichotomy, the
pw-top batch/TUI signal split, the pw-link rc=255 lattice, the pw-jack
env shim, the pw-metadata echo-lies law, and two set-param refusals.
Every own object is unloaded name-verified; crash-class spots run with
RLIMIT_CORE=0; no set-default-*, no subject-0 writes, no foreign object
touched.
"""
import json
import os
import re
import resource
import signal
import subprocess
import sys
import time

PID = os.getpid()
NS = f"r86r_ns_{PID}"
TOOL = f"r86r_{PID}"
OUT = {"pid": PID, "ns": NS, "spots": {}, "window": []}


def sh(argv, timeout=15, stdin_data=None, nocore=False, sig=None, at=1.2,
       bound=6.0):
    t0 = time.time()
    def nocorefn():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if sig is None:
        try:
            p = subprocess.run(argv, capture_output=True, timeout=timeout,
                               input=stdin_data,
                               preexec_fn=nocorefn if nocore else None,
                               stdin=(None if stdin_data is not None
                                      else subprocess.DEVNULL))
            return {"argv": " ".join(argv), "rc": p.returncode,
                    "signal": None, "killed": False,
                    "out": p.stdout.decode(errors="replace"),
                    "err": p.stderr.decode(errors="replace"),
                    "wall": round(time.time() - t0, 3)}
        except subprocess.TimeoutExpired as exc:
            return {"argv": " ".join(argv), "rc": None, "signal": None,
                    "killed": True,
                    "out": (exc.stdout or b"").decode(errors="replace"),
                    "err": (exc.stderr or b"").decode(errors="replace"),
                    "wall": round(time.time() - t0, 3)}
    p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         stdin=subprocess.DEVNULL,
                         start_new_session=True,
                         preexec_fn=nocorefn if nocore else None)
    time.sleep(at)
    try:
        os.killpg(p.pid, sig)
    except ProcessLookupError:
        pass
    try:
        o, e = p.communicate(timeout=max(0.2, bound - at))
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, signal.SIGKILL)
        o, e = p.communicate()
    return {"argv": " ".join(argv), "rc": p.returncode,
            "signal": (signal.Signals(-p.returncode).name
                       if (p.returncode or 0) < 0 else None),
            "killed": False, "out": o.decode(errors="replace"),
            "err": e.decode(errors="replace"),
            "wall": round(time.time() - t0, 3)}


def dump_graph():
    p = subprocess.run(["pw-dump"], capture_output=True, timeout=20)
    return json.loads(p.stdout or b"[]")


def sink_node(name):
    for o in dump_graph():
        if str(o.get("type", "")).endswith("Node") and \
                (o.get("info") or {}).get("props", {}).get(
                    "node.name") == name:
            return o["id"], str((o.get("info") or {}).get("props", {})
                                .get("object.serial"))
    return None, None


def load_ns():
    p = subprocess.run(["pactl", "load-module", "module-null-sink",
                        f"sink_name={NS}",
                        f"sink_properties=device.description={NS}"],
                       capture_output=True, timeout=15)
    return p.returncode, p.stdout.decode().strip()


def unload_ns(mod_id):
    lst = subprocess.run(["pactl", "list", "short", "modules"],
                         capture_output=True, timeout=15).stdout.decode()
    line = next((ln for ln in lst.splitlines()
                 if f"sink_name={NS}" in ln and ln.split()[0] == mod_id),
                None)
    res = {"module": mod_id, "verified_line": line}
    if line:
        p = subprocess.run(["pactl", "unload-module", mod_id],
                           capture_output=True, timeout=15)
        res["rc"] = p.returncode
    sinks = subprocess.run(["pactl", "list", "short", "sinks"],
                           capture_output=True, timeout=15).stdout.decode()
    res["sink_gone"] = NS not in sinks
    return res


def spot(name, data):
    OUT["spots"][name] = data
    print(json.dumps({name: data})[:600])


def main():
    OUT["window"].append(f"start {time.strftime('%H:%M:%S')} "
                         f"loadavg {open('/proc/loadavg').read().strip()}")
    rc, mod = load_ns()
    OUT["load"] = {"rc": rc, "module": mod}
    if rc != 0:
        print(json.dumps(OUT))
        return 2
    try:
        nid, ser = None, None
        for _ in range(20):
            nid, ser = sink_node(NS)
            if nid is not None:
                break
            time.sleep(0.3)
        OUT["ns"] = {"node_id": nid, "serial": ser}
        # S1 addressing split
        s1 = {}
        s1["ls_serial"] = sh(["pw-cli", "ls", ser])
        s1["ls_id"] = sh(["pw-cli", "ls", str(nid)])
        s1["info_id"] = sh(["pw-cli", "info", str(nid)])
        s1["info_serial"] = sh(["pw-cli", "info", ser])
        spot("S1_addressing_split", {
            "ls_serial_has_serial": f'object.serial = "{ser}"'
            in s1["ls_serial"]["out"],
            "ls_serial_rc": s1["ls_serial"]["rc"],
            "ls_id_bytes": len(s1["ls_id"]["out"]),
            "ls_id_rc": s1["ls_id"]["rc"],
            "info_id_has_id": f"id: {nid}" in s1["info_id"]["out"],
            "info_serial_unknown_global":
                "unknown global" in s1["info_serial"]["err"],
            "info_serial_rc": s1["info_serial"]["rc"]})
        # S2 pw-dump surface
        s2 = {}
        for nm, argv in (("bad_id", ["pw-dump", "99999"]),
                         ("bogus", ["pw-dump", "bogus"]),
                         ("color_sep", ["pw-dump", "-C", "never"]),
                         ("color_join", ["pw-dump", "-Cnever"]),
                         ("color_eq", ["pw-dump", "-C=never"])):
            r = sh(argv)
            s2[nm] = {"rc": r["rc"], "bytes": len(r["out"]),
                      "err_head": r["err"].strip().splitlines()[:1]}
        spot("S2_pw_dump_surface", s2)
        # S3 pw-cli stdin trichotomy
        devnull = sh(["pw-cli"], 7, nocore=True)
        quit_ = sh(["pw-cli"], 10, stdin_data=b"quit\n")
        pipe = sh(["pw-cli"], 4, stdin_data=b"ls\n")
        spot("S3_pwcli_stdin", {
            "devnull": {"rc": devnull["rc"], "signal": devnull["signal"],
                        "assert": "remove_from_poll" in devnull["err"]},
            "quit": {"rc": quit_["rc"], "signal": quit_["signal"],
                     "killed": quit_["killed"]},
            "pipe": {"rc": pipe["rc"], "signal": pipe["signal"],
                     "killed": pipe["killed"]}})
        # S4 pw-top signal split
        r_batch = sh(["pw-top", "-b", "-n", "100000"], sig=signal.SIGTERM,
                     at=1.0, bound=6.0)
        r_tui = sh(["pw-top"], sig=signal.SIGTERM, at=1.4, bound=7.0)
        spot("S4_pw_top_signal_split", {
            "batch_term": {"rc": r_batch["rc"], "signal": r_batch["signal"],
                           "assert": "remove_from_poll" in r_batch["err"]},
            "tui_term": {"rc": r_tui["rc"], "signal": r_tui["signal"],
                         "assert": "remove_from_poll" in r_tui["err"]}})
        # S5 pw-link rc lattice on own ports
        link = sh(["pw-link", f"{NS}:monitor_FL", f"{NS}:playback_FL"])
        time.sleep(0.3)
        dup = sh(["pw-link", f"{NS}:monitor_FL", f"{NS}:playback_FL"])
        usage = sh(["pw-link"])
        i_alone = sh(["pw-link", "-I"])
        v_alone = sh(["pw-link", "-v"])
        # find the link id + a port id (one graph snapshot)
        graph = dump_graph()
        names = {o["id"]: (o.get("info") or {}).get("props", {}).get(
            "node.name") for o in graph
            if str(o.get("type", "")).endswith("Node")}
        lid, port_id = None, None
        for o in graph:
            t = str(o.get("type", ""))
            if t.endswith("Link"):
                info = o.get("info") or {}
                onames = {names.get(info.get("output-node-id")),
                          names.get(info.get("input-node-id"))}
                if NS in onames:
                    lid = o["id"]
            if t.endswith("Port") and (o.get("info") or {}).get(
                    "props", {}).get("node.name") == NS and \
                    (o.get("info") or {}).get("props", {}).get(
                        "port.name") == "playback_FL":
                port_id = o["id"]
        d_port = sh(["pw-link", "-d", str(port_id)]) if port_id else None
        d_link = sh(["pw-link", "-d", str(lid)]) if lid else None
        time.sleep(0.3)
        survivors = [o["id"] for o in dump_graph()
                     if str(o.get("type", "")).endswith("Link")
                     and o["id"] == lid]
        spot("S5_pw_link_lattice", {
            "create_rc": link["rc"], "dup_rc": dup["rc"],
            "dup_err": dup["err"].strip()[:80],
            "usage_rc": usage["rc"], "I_alone_rc": i_alone["rc"],
            "v_alone_rc": v_alone["rc"],
            "port_id": port_id, "d_port_rc": (d_port or {}).get("rc"),
            "link_id": lid, "d_link_rc": (d_link or {}).get("rc"),
            "survivors": survivors})
        # S6 pw-jack env shim
        def jack(*args, env=None):
            e = dict(os.environ)
            if env:
                e.update(env)
            p = subprocess.run(["pw-jack", *args, "sh", "-c",
                                'echo Q=${PIPEWIRE_QUANTUM-unset} '
                                'D=${PIPEWIRE_DEBUG-unset} '
                                'R=${PIPEWIRE_REMOTE-unset}'],
                               capture_output=True, timeout=10, env=e)
            return {"rc": p.returncode,
                    "out": p.stdout.decode().strip()}
        spot("S6_pw_jack_shim", {
            "p512": jack("-p", "512"), "sp": jack("-s", "44100", "-p", "256"),
            "s_only": jack("-s", "44100"), "v": jack("-v"),
            "vv": jack("-v", "-v"),
            "v_preset": jack("-v", env={"PIPEWIRE_DEBUG": "4"}),
            "bogus": jack(f"{TOOL}_nocmd")})
        # S7 pw-metadata echo-lies + bogus store (subject 99997 only)
        dead_w = sh(["pw-metadata", "-n", "default", "99997",
                     f"{TOOL}_k", "v"])
        dead_r = sh(["pw-metadata", "-n", "default", "99997", f"{TOOL}_k"])
        bogus = sh(["pw-metadata", "-n", f"{TOOL}_nope"])
        subj0 = sh(["pw-metadata", "-n", "default", "0"])
        spot("S7_pw_metadata_laws", {
            "dead_write_echo": "set property:" in dead_w["out"],
            "dead_write_rc": dead_w["rc"],
            "dead_read_update_rows": dead_r["out"].count("update:"),
            "bogus_rc": bogus["rc"], "bogus_bytes": len(bogus["out"]),
            "subj0_rc": subj0["rc"],
            "subj0_found": 'Found "default"' in subj0["out"],
            "subj0_keys": sorted(set(re.findall(r"key:'([^']+)'",
                                                subj0["out"])))})
        # S8 set-param refusals (own node + own port)
        garbage = sh(["pw-cli", "set-param", str(nid), "Props", "garbage"])
        enumf = sh(["pw-cli", "set-param", str(nid), "EnumFormat",
                    "{ mediaType: 1, mediaSubtype: 1 }"])
        port_lat = (sh(["pw-cli", "set-param", str(port_id), "Latency",
                        "{ minQuantum: 2.0 }"]) if port_id else None)
        re_port = (sh(["pw-cli", "enum-params", str(port_id), "Latency"])
                   if port_id else None)
        spot("S8_set_param_refusals", {
            "garbage_out": garbage["out"].strip()[:40],
            "garbage_rc": garbage["rc"],
            "enumf_rc": enumf["rc"],
            "enumf_res95": "res:-95" in enumf["err"],
            "port_lat_rc": (port_lat or {}).get("rc"),
            "port_lat_notimpl":
                "not implemented" in (port_lat or {}).get("err", ""),
            "re_port_minQuantum_zero":
                bool(re.search(r"minQuantum[\s\S]{0,140}?Float 0\.000000",
                               (re_port or {}).get("out", "")))})
    finally:
        OUT["unload"] = unload_ns(mod)
        OUT["window"].append(f"end {time.strftime('%H:%M:%S')} "
                             f"loadavg {open('/proc/loadavg').read().strip()}")
    print(json.dumps(OUT, indent=1))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "spots.json"), "w") as fh:
        json.dump(OUT, fh, indent=2)
        fh.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
