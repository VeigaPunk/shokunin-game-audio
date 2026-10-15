#!/usr/bin/env python3
"""r97-scout stage D — the linking policy (prepare-link / target selection).

A real `pw-cat` playback stream is armed against this seat's private graph and
the resulting links are read from pw-dump. Bounded: every stream is killed by
process group, every leg has a wall cap.

Cells: --target 0 (documented no-link), auto, global id, object.serial, name,
bogus target with/without node.dont-fallback, media.role, and the
`linking.follow-default-target` setting as a *behavioural* settings witness.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97lib import (SEAT, ENV, PwCli, run, dump, nodes, meta_rows, nullsink,
                    sink_by_name, default_sink_value, ensure_up)

REC = os.path.join(SEAT, "receipts")
SCR = os.path.join(SEAT, "scratch")


class Stream:
    """A bounded pw-cat playback stream whose stdin stays open (no data)."""
    def __init__(self, extra=(), target=None, props=None, role=None, cap=8.0):
        cmd = ["pw-cat", "-p", "--raw", "--rate", "48000", "--channels", "1",
               "--format", "s16"]
        if target is not None:
            cmd += ["--target", str(target)]
        if props:
            cmd += ["-P", props]
        if role:
            cmd += ["--media-role", role]
        cmd += ["-"]
        self.cmd = cmd
        self.cap = cap
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                                  env=ENV, start_new_session=True, text=True)

    def stop(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        try:
            self.p.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        err = ""
        try:
            err = self.p.stderr.read() or ""
        except Exception:
            pass
        return {"argv": self.cmd, "rc": self.p.returncode, "stderr": err[:400]}


def link_map(objs):
    by_id = {}
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            by_id[o["id"]] = (o.get("info") or {}).get("props", {}).get("node.name")
    out = []
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Link":
            info = o.get("info") or {}
            out.append((by_id.get(info.get("output-node-id")),
                        by_id.get(info.get("input-node-id")),
                        info.get("output-port-id"), info.get("input-port-id")))
    return out


def wait_stream(name, cap=5.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        objs = dump()
        i = sink_by_name(objs, name)   # same lookup: by node.name
        if i is not None:
            return i, objs
        time.sleep(0.2)
    return None, dump()


def stream_links(objs, name):
    sid = sink_by_name(objs, name)
    if sid is None:
        return None
    return [l for l in link_map(objs) if l[0] == name or l[1] == name]


def leg(cli, tag, obs, **kw):
    st = Stream(**kw)
    time.sleep(1.6)
    objs = dump()
    sl = stream_links(objs, "r97s_str")
    _, d = default_sink_value(objs)
    res = st.stop()
    obs.append({"tag": tag, "stream_args": st.cmd, "links": sl, "default": d,
                "stop": {k: v for k, v in res.items() if k != "argv"}})
    return sl


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ensure_up()
    out = {"stage": "d_linking", "reps": []}
    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SCR, f"pwcli_d{n}.log"))
        obs = []
        try:
            run(["wpctl", "clear-default"], timeout=6.0)
            nullsink(cli, f"r97s_sa{n}", 100, 100)
            ida = sink_by_name(dump(), f"r97s_sa{n}")
            nullsink(cli, f"r97s_sb{n}", 500, 100)
            time.sleep(1.2)
            objs = dump()
            idb = sink_by_name(objs, f"r97s_sb{n}")
            serials = {}
            for o in objs:
                if o.get("type") == "PipeWire:Interface:Node":
                    nm = (o.get("info") or {}).get("props", {}).get("node.name")
                    if nm in (f"r97s_sa{n}", f"r97s_sb{n}"):
                        serials[nm] = o.get("info", {}).get("props", {}).get("object.serial")
            _, d = default_sink_value(objs)
            obs.append({"tag": "setup", "id_a": ida, "id_b": idb, "serial": serials,
                        "default": d})

            P = "{ node.name = r97s_str }"
            leg(cli, "target_0_no_link", obs, target=0, props=P)
            leg(cli, "auto_default", obs, props=P)
            leg(cli, "target_global_id_A", obs, target=ida, props=P)
            leg(cli, "target_object_serial_A", obs, target=serials.get(f"r97s_sa{n}"), props=P)
            leg(cli, "target_name_A", obs, target=f"r97s_sa{n}", props=P)
            leg(cli, "bogus_target_99999", obs, target=99999, props=P)
            leg(cli, "bogus_target_dont_fallback", obs, target=99999,
                props="{ node.name = r97s_str node.dont-fallback = true }")
            leg(cli, "media_role_Communication", obs,
                props="{ node.name = r97s_str media.role = Communication }")

            # behavioural settings witness: follow-default-target
            run(["wpctl", "settings", "linking.follow-default-target", "true"], timeout=8.0)
            st = Stream(props=P)
            time.sleep(1.5)
            before = stream_links(dump(), "r97s_str")
            run(["wpctl", "set-default", str(ida)], timeout=6.0)
            time.sleep(2.0)
            after = stream_links(dump(), "r97s_str")
            st.stop()
            obs.append({"tag": "follow_default_true", "before": before, "after": after})

            run(["wpctl", "settings", "linking.follow-default-target", "false"], timeout=8.0)
            run(["wpctl", "set-default", str(idb)], timeout=6.0)
            time.sleep(1.0)
            st = Stream(props=P)
            time.sleep(1.5)
            before = stream_links(dump(), "r97s_str")
            run(["wpctl", "set-default", str(ida)], timeout=6.0)
            time.sleep(2.0)
            after = stream_links(dump(), "r97s_str")
            st.stop()
            obs.append({"tag": "follow_default_false", "before": before, "after": after})
            run(["wpctl", "settings", "linking.follow-default-target", "true"], timeout=8.0)
            run(["wpctl", "clear-default"], timeout=6.0)
        finally:
            cli.close()
            time.sleep(0.6)
        out["reps"].append({"rep": n, "obs": obs})
    os.makedirs(REC, exist_ok=True)
    json.dump(out, open(os.path.join(REC, "d_linking.json"), "w"), indent=1)
    for rep in out["reps"]:
        print(f"--- rep {rep['rep']}")
        for o in rep["obs"]:
            if o["tag"] == "setup":
                print("   setup ids", o["id_a"], o["id_b"], "serials", o["serial"], "default", o["default"])
            elif "links" in o:
                print(f"   {o['tag']:<30} links={o['links']} default={o['default']} stderr={o['stop']['stderr'].strip()[:60]!r}")
            else:
                print(f"   {o['tag']:<30} before={o['before']} after={o['after']}")


if __name__ == "__main__":
    main()
