#!/usr/bin/env python3
"""r97-scout: minimal pw-cli session helper + default-node policy probe.

Bounded: every external process has a wall cap and is killed by process group.
"""
import json, os, signal, subprocess, sys, time

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(SEAT, "run")
ENV = dict(os.environ)
ENV.update({
    "PIPEWIRE_RUNTIME_DIR": RUN,
    "XDG_RUNTIME_DIR": RUN,
    "XDG_CONFIG_HOME": SEAT + "/conf/xdg-config",
    "XDG_STATE_HOME": SEAT + "/conf/xdg-state",
    "XDG_DATA_HOME": SEAT + "/conf/xdg-data",
})
ENV.pop("WIREPLUMBER_CONFIG_DIR", None)


def ensure_up(verbose=True):
    """Arm the private pair if it is not answering. Bounded."""
    r = run(["pw-dump"], timeout=8.0)
    if r["rc"] == 0 and r["stdout"].strip().startswith("["):
        return {"already": True, "objects": len(json.loads(r["stdout"]))}
    # the pid files can say "alive" while the core is wedged (observed twice:
    # process alive, sockets present, no reply to any client). Force a full
    # re-arm in that case.
    subprocess.run([os.path.join(SEAT, "probes", "down.sh"), "both"],
                   capture_output=True, text=True, timeout=60, env=ENV)
    time.sleep(0.5)
    u = subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "both"],
                       capture_output=True, text=True, timeout=90, env=ENV)
    time.sleep(1.5)
    r2 = run(["pw-dump"], timeout=8.0)
    ok = r2["rc"] == 0 and r2["stdout"].strip().startswith("[")
    if verbose:
        print("ensure_up:", u.stdout.strip().replace("\n", " | "), "ok=", ok)
    return {"already": False, "up": u.stdout.strip(), "ok": ok,
            "objects": len(json.loads(r2["stdout"])) if ok else 0}


def run(cmd, timeout=8.0, byte_cap=1 << 20, stdin_data=None):
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=ENV, start_new_session=True)
    timed = False
    try:
        out, err = p.communicate(input=stdin_data, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
        timed = True
    dur = round(time.monotonic() - t0, 3)
    return {
        "argv": cmd, "rc": p.returncode, "timed_out": timed, "dur_s": dur,
        "stdout": out[:byte_cap].decode("utf-8", "replace"),
        "stderr": err[:byte_cap].decode("utf-8", "replace"),
        "bytes": len(out) + len(err), "truncated": (len(out) + len(err)) > byte_cap,
    }


class PwCli:
    """Keeps one `pw-cli` alive so created nodes outlive the command."""
    def __init__(self, timeout=30.0, logpath=None):
        self.logpath = logpath or os.path.join(SEAT, "scratch", "pwcli_session.log")
        self._log = open(self.logpath, "w")
        self.p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                                  stdout=self._log, stderr=subprocess.STDOUT,
                                  env=ENV, start_new_session=True, text=True)
        self.timeout = timeout

    def cmd(self, line, settle=0.5):
        self.p.stdin.write(line + "\n")
        self.p.stdin.flush()
        time.sleep(settle)
        return line

    def close(self):
        try:
            self.p.stdin.close()
        except Exception:
            pass
        try:
            self.p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            self._log.close()
        except Exception:
            pass


def dump():
    r = run(["pw-dump"], timeout=10.0)
    try:
        return json.loads(r["stdout"])
    except Exception:
        return None


def nodes(objs):
    out = []
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            pr = (o.get("info") or {}).get("props") or {}
            out.append((o["id"], pr.get("node.name"), pr.get("media.class"),
                        pr.get("priority.session"), pr.get("node.description")))
    return sorted(out)


def meta_rows(objs, name="default"):
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Metadata":
            pr = o.get("props") or {}
            if pr.get("metadata.name") == name:
                return (o["id"], o.get("metadata") or [])
    return (None, None)


def nullsink(cli, name, session=100, driver=100, desc=None, extra=""):
    desc = desc or name
    # NOTE (measured): spa-json values must not contain commas unquoted
    # (audio.position=FL,FR -> "Expected object value"); leave the sink's
    # default stereo position in place.
    props = (f"{{ factory.name=support.null-audio-sink node.name={name} "
             f"node.description={desc} media.class=Audio/Sink "
             f"priority.session={session} priority.driver={driver} {extra} }}")
    # NOTE (measured): pw-cli create-node takes the props as a bare { ... }
    # group; shell-style outer quotes are part of the string when no shell is
    # involved and produce "syntax error in properties ... Expected object key".
    return cli.cmd(f"create-node adapter {props}")


def sink_by_name(objs, name):
    for i, n, mc, ps, d in nodes(objs):
        if n == name:
            return i
    return None


def default_sink_value(objs):
    mid, rows = meta_rows(objs)
    for r in rows or []:
        if r.get("key") == "default.audio.sink":
            v = r.get("value")
            return (mid, v)
    return (mid, None)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "c"
    if stage == "smoke":
        cli = PwCli()
        nullsink(cli, "r97s_smoke", 100, 100)
        time.sleep(1.0)
        objs = dump()
        print(json.dumps(nodes(objs), indent=1))
        print("default:", default_sink_value(objs))
        cli.close()
