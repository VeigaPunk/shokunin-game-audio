#!/usr/bin/env python3
"""r97b stage D — replay of the r97 scout linking law (claims 6-7, rows
`wp.link.*`) with fresh processes, plus the axes the scout did not vary:

  flag order      : `--target` before the mode flags, `--target=<n>` equals form,
                    `--target` after the input argument
  prop forms      : `-P { target.object = <serial|id> }` vs `-P { node.target = ... }`
                    (the scout's mechanism claim says node.target is a node.id and
                    target.object is an object.serial; never armed behaviourally)
  linger branch   : `node.dont-fallback` + `node.linger` (r97 scout [?]7)
  moving streams  : `linking.allow-moving-streams=false` vs follow-default-target
                    (r97 scout [?]2 — which path moves the stream?)

Cells, one private graph with two sinks A(session 100) and B(session 500, so B
is default), stream node name r97b_str, links read from pw-dump:
  d1 --target 0                    -> 0 links
  d2 auto                          -> default (B)
  d3 --target <A global id>        -> scout: silent fallback to default (B)
  d4 --target <A object.serial>    -> A
  d5 --target <A node.name>        -> A
  d6 --target 99999                -> fallback to default (B), rc 0, empty stderr
  d7 bogus + node.dont-fallback    -> 0 links, client error -2, stream node destroyed
  d8 bogus + dont-fallback + linger-> 0 links, stream node stays (waits)
  d9 flag order / equals form / target after input  (serial target each time -> A)
  d10 prop forms: target.object=<serial>, target.object=<id>, node.target=<id>,
      node.target=<serial>
  d11 allow-moving-streams=false: stream on default B, set-default A -> moved?
  d12 follow-default-target=false: same shape (scout's inert cell, re-armed)
Bounded: every stream killed by process group; 8 s per leg cap.
"""
import json, os, signal, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r97blib import (SEAT, ENV, REC, SCR, run, dump, nodes, nullsink, sink_by_name,
                     sink_serial, default_sink_value, node_props, ensure_up,
                     stage_out, stage_write, loadavg, PwCli)

BIG = 1 << 20


class Stream:
    """A bounded pw-cat playback stream whose stdin stays open (no data)."""

    def __init__(self, argv, cap=8.0, name="r97b_str"):
        self.argv = argv
        self.name = name
        self.cap = cap
        self.p = subprocess.Popen(argv, stdin=subprocess.PIPE,
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
        return {"rc": self.p.returncode, "stderr": err[:400]}


def base_argv(target=None, props=None, role=None, rate="48000", extra=()):
    cmd = ["pw-cat", "-p", "--raw", "--rate", rate, "--channels", "1", "--format", "s16"]
    if target is not None:
        cmd += ["--target", str(target)]
    if props:
        cmd += ["-P", props]
    if role:
        cmd += ["--media-role", role]
    cmd += list(extra)
    cmd += ["-"]
    return cmd


def link_map(objs):
    by_id = {}
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            by_id[o["id"]] = (o.get("info") or {}).get("props", {}).get("node.name")
    out = []
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Link":
            info = o.get("info") or {}
            out.append([by_id.get(info.get("output-node-id")),
                        by_id.get(info.get("input-node-id"))])
    return out


def stream_links(objs, name="r97b_str"):
    return [l for l in link_map(objs) if name in l]


def leg(obs, tag, argv, settle=2.0, name="r97b_str"):
    st = Stream(argv, name=name)
    time.sleep(settle)
    objs = dump()
    sl = stream_links(objs, name)
    props = node_props(objs, name)
    _, d = default_sink_value(objs)
    stop = st.stop()
    obs.append({"tag": tag, "argv": argv, "links": sl, "default": d,
                "stream_props": props, "stop": stop, "loadavg": loadavg()})
    return sl


def main():
    arm = sys.argv[1] if len(sys.argv) > 1 else "ambient"
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    out = stage_out("d_linking")
    out["arm"] = arm
    e = ensure_up(verbose=True)
    out["pair"] = e
    if not e.get("ok") and not e.get("already"):
        out["fatal"] = "private pair did not come up"
        stage_write(out, "d_linking.json")
        return

    for n in range(reps):
        cli = PwCli(logpath=os.path.join(SCR, f"pwcli_d{n}.log"))
        obs = []
        try:
            run(["wpctl", "clear-default"], timeout=8.0)
            nullsink(cli, f"r97b_sa{n}", 100, 100)
            nullsink(cli, f"r97b_sb{n}", 500, 100)
            time.sleep(1.5)
            objs = dump()
            ida = sink_by_name(objs, f"r97b_sa{n}")
            idb = sink_by_name(objs, f"r97b_sb{n}")
            sera = sink_serial(objs, f"r97b_sa{n}")
            _, d = default_sink_value(objs)
            obs.append({"tag": "setup", "id_a": ida, "id_b": idb, "serial_a": sera,
                        "default": d, "loadavg": loadavg()})
            P = "{ node.name = r97b_str }"

            leg(obs, "d1_target_0", base_argv(target=0, props=P))
            leg(obs, "d2_auto_default", base_argv(props=P))
            leg(obs, "d3_target_global_id_A", base_argv(target=ida, props=P))
            leg(obs, "d4_target_object_serial_A", base_argv(target=sera, props=P))
            leg(obs, "d5_target_name_A", base_argv(target=f"r97b_sa{n}", props=P))
            leg(obs, "d6_bogus_99999", base_argv(target=99999, props=P))
            leg(obs, "d7_bogus_dont_fallback",
                base_argv(target=99999,
                          props="{ node.name = r97b_str node.dont-fallback = true }"))
            leg(obs, "d8_bogus_dont_fallback_linger",
                base_argv(target=99999,
                          props="{ node.name = r97b_str node.dont-fallback = true node.linger = true }"))
            leg(obs, "d9a_target_before_mode_flags",
                ["pw-cat", "--target", str(sera), "-p", "--raw", "--rate", "48000",
                 "--channels", "1", "--format", "s16", "-P", P, "-"])
            leg(obs, "d9b_target_equals_form",
                ["pw-cat", f"--target={sera}", "-p", "--raw", "--rate", "48000",
                 "--channels", "1", "--format", "s16", "-P", P, "-"])
            leg(obs, "d9c_target_after_input",
                ["pw-cat", "-p", "--raw", "--rate", "48000", "--channels", "1",
                 "--format", "s16", "-P", P, "-", "--target", str(sera)])
            leg(obs, "d9d_target_after_props",
                ["pw-cat", "-p", "--raw", "--rate", "48000", "--channels", "1",
                 "--format", "s16", "-P", P, "--target", str(sera), "-"])
            leg(obs, "d10a_prop_target_object_serial",
                base_argv(props="{ node.name = r97b_str target.object = %s }" % sera))
            leg(obs, "d10b_prop_target_object_id",
                base_argv(props="{ node.name = r97b_str target.object = %s }" % ida))
            leg(obs, "d10c_prop_node_target_id",
                base_argv(props="{ node.name = r97b_str node.target = %s }" % ida))
            leg(obs, "d10d_prop_node_target_serial",
                base_argv(props="{ node.name = r97b_str node.target = %s }" % sera))
            leg(obs, "d13_rate_44100_serial_target",
                base_argv(target=sera, props=P, rate="44100"))

            # d11/d12: which path moves a stream when the default changes?
            for setting, tag in (("linking.allow-moving-streams", "d11_allow_moving_streams_false"),
                                 ("linking.follow-default-target", "d12_follow_default_false")):
                run(["wpctl", "settings", setting, "false"], timeout=10.0)
                rd = run(["wpctl", "settings", setting], timeout=10.0)
                run(["wpctl", "set-default", str(idb)], timeout=8.0)
                time.sleep(1.0)
                st = Stream(base_argv(props=P))
                time.sleep(1.5)
                before = stream_links(dump())
                run(["wpctl", "set-default", str(ida)], timeout=8.0)
                time.sleep(2.5)
                after = stream_links(dump())
                stop = st.stop()
                obs.append({"tag": tag, "readback": rd["stdout"].strip()[:120],
                            "before": before, "after": after, "stop": stop,
                            "loadavg": loadavg()})
                run(["wpctl", "settings", setting, "true"], timeout=10.0)
            run(["wpctl", "clear-default"], timeout=8.0)
        finally:
            cli.close()
            time.sleep(0.6)
        out["reps"].append({"rep": n, "obs": obs})
        out["loadavg_end_rep"] = loadavg()

    for r in out["reps"]:
        print(f"--- rep {r['rep']}")
        for o in r["obs"]:
            if o["tag"] == "setup":
                print(f"   setup id_a={o['id_a']} id_b={o['id_b']} serial_a={o['serial_a']} default={o['default']}")
            elif "links" in o:
                print(f"   {o['tag']:<34} links={o['links']} default={o['default']} "
                      f"stderr={o['stop']['stderr'].strip()[:50]!r}")
            else:
                print(f"   {o['tag']:<34} before={o['before']} after={o['after']}")
    stage_write(out, "d_linking.json")


if __name__ == "__main__":
    main()
