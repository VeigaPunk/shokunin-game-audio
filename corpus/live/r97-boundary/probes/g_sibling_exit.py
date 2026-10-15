#!/usr/bin/env python3
"""r97b stage G — the sibling-presence axis and the exit census.

  g1 sibling emulation: a SECOND private pair of this seat (own conf dir, own
     runtime dir run-sibling/) is armed while the main pair is up. Both pairs
     create a sink (r97b_sib / r97b_main). Asserts: each pair sees only its own
     sink; neither leaks into the shared graph.
  g2 real foreign contention census (read-only ps / pw-dump of the shared graph)
  g3 shared-graph namespace census: count of objects whose props mention `r97b`
     (must be 0), shared daemon pids and start times (must be unchanged)
  g4 exit census: stop this seat's pair and sibling pair, re-count
  g5 shared state-file fingerprint (size + sha + mtime) — never written by this
     seat; foreign growth is disclosed, not modified.
Bounded: 12 s caps, guarded kills only (cmdline must mention the seat dir).
"""
import hashlib, json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, RUN, run, dump, nodes, nullsink,
                     sink_by_name, ensure_up, down, stage_out, stage_write,
                     loadavg, shared_dump, foreign_census, hog_count, PwCli)

SIB = os.path.join(SEAT, "run-sibling")
SIB_CONF = os.path.join(SEAT, "conf", "pw-sibling")
SHARED_STATE = os.path.expanduser("~/.local/state/wireplumber")


def shared_daemons():
    out = {}
    for pid in (2060, 2063, 2694):
        try:
            st = open(f"/proc/{pid}/stat").read().split()
            cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ").strip()
            out[pid] = {"alive": True, "starttime": st[21], "cmd": cmd[:80]}
        except Exception:
            out[pid] = {"alive": False}
    return out


def namespace_census():
    """Count r97b objects in the SHARED graph (read-only) and in this seat's."""
    priv = dump() or []
    priv_hits = []
    for o in priv:
        pr = (o.get("info") or {}).get("props") or o.get("props") or {}
        for k, v in pr.items():
            if isinstance(v, str) and "r97b" in v:
                priv_hits.append((o.get("id"), k, v))
                break
    shared = shared_dump() or []
    sh_hits = []
    for o in shared:
        pr = (o.get("info") or {}).get("props") or o.get("props") or {}
        for k, v in pr.items():
            if isinstance(v, str) and "r97b" in v:
                sh_hits.append((o.get("id"), k, v))
                break
    return {"private_objects": len(priv), "private_r97b_hits": priv_hits,
            "shared_objects": len(shared), "shared_r97b_hits": sh_hits}


def state_fingerprint():
    out = {}
    for f in ("default-nodes", "stream-properties"):
        p = os.path.join(SHARED_STATE, f)
        try:
            b = open(p, "rb").read()
            st = os.stat(p)
            out[f] = {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                      "mtime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(st.st_mtime)),
                      "head": b[:120].decode("utf-8", "replace")}
        except Exception as e:
            out[f] = {"error": str(e)}
    return out


def guarded_kill(pid):
    try:
        cmd = open(f"/proc/{pid}/cmdline").read().replace("\0", " ")
        env = open(f"/proc/{pid}/environ").read().replace("\0", "\n")
    except Exception:
        return "gone"
    # a seat `wireplumber -c wireplumber.conf -p main` carries no seat path in
    # its cmdline; its seat identity is in the environment (measured).
    if SEAT in cmd or SEAT in env:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except Exception:
            try:
                os.kill(pid, signal.SIGKILL)
            except Exception:
                pass
        return "killed"
    return f"REFUSED (foreign cmd={cmd})"


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    out = stage_out("g_sibling_exit")
    out["arm"] = arm
    os.makedirs(SIB, exist_ok=True)
    os.makedirs(os.path.join(SIB_CONF, "r97b2-pipewire.conf.d"), exist_ok=True)
    # sibling core conf: same shape, own fragment, own socket dir
    src = open(os.path.join(SEAT, "conf", "pw", "r97b-pipewire.conf")).read()
    open(os.path.join(SIB_CONF, "r97b2-pipewire.conf"), "w").write(src)
    open(os.path.join(SIB_CONF, "r97b2-pipewire.conf.d", "10-r97b2.conf"), "w").write(
        "context.properties = {\n  module.rt = false\n  module.profiler = false\n"
        "  module.portal = false\n}\n")
    os.makedirs(os.path.join(SIB_CONF, "xdg-config", "wireplumber",
                             "wireplumber.conf.d"), exist_ok=True)
    open(os.path.join(SIB_CONF, "xdg-config", "wireplumber", "wireplumber.conf.d",
                      "10-r97b2.conf"), "w").write(
        "wireplumber.profiles = {\n  main = {\n    hardware.audio = disabled\n"
        "    hardware.bluetooth = disabled\n    hardware.video-capture = disabled\n  }\n}\n")

    out["g2_foreign_at_start"] = foreign_census()
    out["g2_shared_daemons_at_start"] = shared_daemons()
    out["g5_state_at_start"] = state_fingerprint()
    e = ensure_up(verbose=True)
    out["pair"] = e

    # ---- g1 sibling pair ----
    se = dict(ENV)
    se["PIPEWIRE_RUNTIME_DIR"] = SIB
    se["XDG_RUNTIME_DIR"] = SIB
    se["XDG_CONFIG_HOME"] = os.path.join(SIB_CONF, "xdg-config")
    se["XDG_STATE_HOME"] = os.path.join(SIB_CONF, "xdg-state")
    os.makedirs(se["XDG_STATE_HOME"], exist_ok=True)
    sc = subprocess.Popen(["pipewire", "-c", os.path.join(SIB_CONF, "r97b2-pipewire.conf")],
                          env=se, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          start_new_session=True, text=True)
    sw = None
    try:
        for _ in range(60):
            if os.path.exists(os.path.join(SIB, "pipewire-0")):
                break
            time.sleep(0.25)
        sw = subprocess.Popen(["wireplumber", "-c", "wireplumber.conf", "-p", "main"],
                              env=se, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              start_new_session=True, text=True)
        for _ in range(80):
            r = run(["wpctl", "status"], timeout=10.0, env=se)
            if r["rc"] == 0:
                break
            time.sleep(0.25)
        # a real WP gate for the sibling too (wpctl rc is not one, see r97blib)
        sib_ready = False
        for _ in range(60):
            d = run(["pw-dump"], timeout=12.0, env=se)
            if d["rc"] == 0 and '"sm-settings"' in d["stdout"]:
                sib_ready = True
                break
            time.sleep(0.25)
        time.sleep(1.5)
        # create one sink in each pair
        cli_main = PwCli(logpath=os.path.join(SCR, "pwcli_g_main.log"))
        nullsink(cli_main, "r97b_main_g", 100, 100)
        # BUG FIXED (first g pass): PwCli defaulted to the MAIN pair's env, so
        # the "sibling" sink was created in the main graph and the isolation
        # test was vacuous. The sibling session now carries the sibling env.
        cli_sib = PwCli(logpath=os.path.join(SCR, "pwcli_g_sib.log"), env=se)
        cli_sib.p.stdin.write("create-node adapter { factory.name=support.null-audio-sink "
                              "node.name=r97b_sib_g node.description=r97b_sib_g "
                              "media.class=Audio/Sink priority.session=100 priority.driver=100 }\n")
        cli_sib.p.stdin.flush()
        time.sleep(2.0)
        main_objs = dump()
        sib_objs = run(["pw-dump"], timeout=12.0, env=se)
        try:
            sib_objs = json.loads(sib_objs["stdout"])
        except Exception:
            sib_objs = None
        sh = shared_dump()
        def names(objs):
            return sorted({n for _, n, *_ in nodes(objs) if n})
        out["g1_sibling"] = {
            "main_pair_names": names(main_objs),
            "sibling_pair_names": names(sib_objs),
            "main_sees_sibling_sink": sink_by_name(main_objs, "r97b_sib_g") is not None,
            "sibling_sees_main_sink": sink_by_name(sib_objs, "r97b_main_g") is not None,
            "shared_sees_either": any("r97b" in (n or "") for _, n, *_ in nodes(sh)),
            "sibling_socket": os.path.join(SIB, "pipewire-0").replace(SEAT, "$SEAT"),
            "main_socket": os.path.join(RUN, "pipewire-0").replace(SEAT, "$SEAT"),
            "sibling_wp_ready": sib_ready,
            "loadavg": loadavg(),
        }
        cli_main.close()
        cli_sib.close()
    finally:
        for p in (sw, sc):
            if p is not None:
                out.setdefault("g1_kills", []).append(guarded_kill(p.pid))
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass
    # remove the sibling runtime dir sockets only if they are ours
    for f in ("pipewire-0", "pipewire-0-manager", "pipewire-0.lock",
              "pipewire-0-manager.lock"):
        p = os.path.join(SIB, f)
        if os.path.exists(p):
            try:
                os.unlink(p)
            except Exception:
                pass

    # ---- g3 census while the main pair is still up ----
    out["g3_census_with_main_up"] = namespace_census()

    # ---- g4 exit census ----
    down("both")
    time.sleep(1.5)
    out["g4_after_down"] = {
        "census": namespace_census(),
        "seat_procs": subprocess.run(
            ["bash", "-lc", f"pgrep -af '{SEAT}' | grep -v pgrep | wc -l"],
            capture_output=True, text=True, timeout=20).stdout.strip(),
        "own_pid_files": sorted(f for f in os.listdir(RUN) if f.endswith(".pid")),
        "hogs_running": hog_count(),
        "loadavg": loadavg(),
    }
    out["g2_foreign_at_end"] = foreign_census()
    out["g2_shared_daemons_at_end"] = shared_daemons()
    out["g5_state_at_end"] = state_fingerprint()
    print(json.dumps({k: v for k, v in out.items() if k.startswith(("g1", "g3", "g4"))},
                     indent=1)[:4000])
    stage_write(out, "g_sibling_exit.json")


if __name__ == "__main__":
    main()
