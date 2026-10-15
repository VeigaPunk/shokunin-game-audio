#!/usr/bin/env python3
"""r97-boundary (r97b) bounded harness library.

Seat-scoped: every path is inside corpus/live/r97-boundary; every external
process runs in its own session (process-group kill on timeout) and every
object this seat creates is named r97b_*. The shared daemons are never
signalled: PIPEWIRE_RUNTIME_DIR/XDG_RUNTIME_DIR point at this seat's run dir,
so the socket is private.
"""
import json, os, signal, subprocess, sys, time

SEAT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(SEAT, "run")
SCR = os.path.join(SEAT, "scratch")
REC = os.path.join(SEAT, "receipts")
LOGS = os.path.join(SEAT, "runs")

ENV = dict(os.environ)
ENV.update({
    "PIPEWIRE_RUNTIME_DIR": RUN,
    "XDG_RUNTIME_DIR": RUN,
    "XDG_CONFIG_HOME": SEAT + "/conf/xdg-config",
    "XDG_STATE_HOME": SEAT + "/conf/xdg-state",
    "XDG_DATA_HOME": SEAT + "/conf/xdg-data",
})
ENV.pop("WIREPLUMBER_CONFIG_DIR", None)
ENV.pop("WIREPLUMBER_DATA_DIR", None)

HOG_PIDFILE = os.path.join(RUN, "hogs.pid")


# ---------------------------------------------------------------- load probe
def loadavg():
    try:
        return open("/proc/loadavg").read().strip()
    except Exception:
        return "?"


def loadavg1():
    try:
        return float(open("/proc/loadavg").read().split()[0])
    except Exception:
        return -1.0


def foreign_census():
    """Read-only census of foreign audio/seat processes. Never kills anything."""
    out = {}
    try:
        r = subprocess.run(["ps", "-eo", "pid,ppid,etimes,args"],
                           capture_output=True, text=True, timeout=20)
        yes = [l for l in r.stdout.splitlines() if l.split()[-1:] == ["yes"]]
        out["foreign_yes_hogs"] = len(yes)
        seats = {}
        for l in r.stdout.splitlines():
            for tag in ("r90-author", "r91-boundary", "r92-boundary", "r95", "r96",
                        "r97-scout", "r98", "r99-scout", "r97-boundary"):
                if "corpus/live/" + tag in l:
                    seats[tag] = seats.get(tag, 0) + 1
        out["seat_procs"] = seats
    except Exception as e:
        out["error"] = str(e)
    return out


def hog_count():
    try:
        pids = [int(x) for x in open(HOG_PIDFILE).read().split()]
    except Exception:
        return 0
    n = 0
    for p in pids:
        try:
            os.kill(p, 0)
            n += 1
        except OSError:
            pass
    return n


# ---------------------------------------------------------------- process run
def run(cmd, timeout=8.0, byte_cap=1 << 20, stdin_data=None, env=None):
    t0 = time.monotonic()
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, env=env or ENV,
                         start_new_session=True)
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
        "load_before": None,
    }


def bounded(cmd, timeout=8.0, **kw):
    """run() with the load average stamped in."""
    la = loadavg()
    r = run(cmd, timeout=timeout, **kw)
    r["load_at_start"] = la
    return r


# ---------------------------------------------------------------- instance
def ensure_up(verbose=False, clock=None, require_wp=True):
    """Arm the private pair if it is not answering. Bounded. clock = fragment text.

    r97b: a healthy CORE is not a healthy PAIR. Stage E's e13 legs stop
    WirePlumber on purpose, and a following stage that only probed the core
    would run with WP down (measured: f_settings in the first hogs chain got
    rc 3 / 0 keys because of exactly that). So the pair check also requires the
    WirePlumber `sm-settings` metadata object unless require_wp=False.
    """
    if clock is not None:
        write_clock_fragment(clock)
    r = run(["pw-dump"], timeout=12.0)
    core_ok = r["rc"] == 0 and r["stdout"].strip().startswith("[")
    wp_ok = core_ok and ('"sm-settings"' in r["stdout"])
    if core_ok and (wp_ok or not require_wp):
        return {"already": True, "objects": len(json.loads(r["stdout"])),
                "wp_ready": wp_ok}
    down("both")
    time.sleep(0.5)
    u = subprocess.run([os.path.join(SEAT, "probes", "up.sh"), "both"],
                       capture_output=True, text=True, timeout=120, env=ENV)
    time.sleep(1.5)
    r2 = run(["pw-dump"], timeout=12.0)
    ok = r2["rc"] == 0 and r2["stdout"].strip().startswith("[")
    if verbose:
        print("ensure_up:", u.stdout.strip().replace("\n", " | "), "ok=", ok)
    return {"already": False, "up": u.stdout.strip(), "ok": ok,
            "objects": len(json.loads(r2["stdout"])) if ok else 0}


LEDGER = os.path.join(REC, "wedge_ledger.jsonl")


def note_wedge(kind, context, extra=None):
    """Append a wedge/health event to the seat's ledger (append-only)."""
    os.makedirs(REC, exist_ok=True)
    row = {"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "kind": kind, "context": context, "loadavg": loadavg(),
           "hogs": hog_count()}
    if extra:
        row.update(extra)
    with open(LEDGER, "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def health(cap=5.0, context="", record=False):
    """One bounded liveness probe of the private core (pw-dump)."""
    r = run(["pw-dump"], timeout=cap)
    ok = r["rc"] == 0 and r["stdout"].strip().startswith("[")
    out = {"ok": ok, "rc": r["rc"], "timed_out": r["timed_out"],
           "dur_s": r["dur_s"], "bytes": len(r["stdout"]),
           "loadavg": loadavg(), "hogs": hog_count(), "context": context}
    if not ok and record:
        note_wedge("health_fail", context, out)
    return out


def health_or_rearm(cap=5.0, context="", verbose=False):
    """If the private core is wedged, record the event and re-arm the pair."""
    h = health(cap=cap, context=context, record=True)
    if h["ok"]:
        return {"wedge": False, "health": h}
    h["rearmed"] = ensure_up(verbose=verbose)
    h2 = health(cap=cap, context=context + "/after_rearm")
    return {"wedge": True, "health": h, "after_rearm": h2,
            "recovered": h2["ok"]}


def down(target="both"):
    return subprocess.run([os.path.join(SEAT, "probes", "down.sh"), target],
                          capture_output=True, text=True, timeout=90, env=ENV)


def write_clock_fragment(text):
    """Write the clock/quantum override fragment of the private core."""
    p = os.path.join(SEAT, "conf", "pw", "r97b-pipewire.conf.d", "20-r97b-clock.conf")
    with open(p, "w") as f:
        f.write(text)
    return p


def core_clock():
    """Read the live core's default.clock.* from pw-dump (object 0 props)."""
    objs = dump()
    for o in objs or []:
        if o.get("id") == 0:
            pr = (o.get("info") or {}).get("props") or o.get("props") or {}
            return {k: pr.get(k) for k in pr if k.startswith("default.clock")}
    return None


def wp_ready(timeout=15.0):
    """True readiness gate for the private WirePlumber.

    MEASURED (r97b e13c): `wpctl status` exits 0 with an EMPTY but well-formed
    listing while WirePlumber is down, so its exit status is not a WP gate.
    WirePlumber's sm-objects component is what publishes the `sm-settings`
    metadata object, so that object is the gate used here.
    """
    t0 = time.monotonic()
    while time.monotonic() - t0 < timeout:
        objs = dump()
        if objs is not None:
            for o in objs:
                if o.get("type") == "PipeWire:Interface:Metadata":
                    if (o.get("props") or {}).get("metadata.name") == "sm-settings":
                        return True, round(time.monotonic() - t0, 3)
        time.sleep(0.25)
    return False, round(time.monotonic() - t0, 3)


class PwCli:
    """Keeps one `pw-cli` alive so created nodes outlive the command."""
    def __init__(self, logpath=None, timeout=30.0, env=None):
        self.logpath = logpath or os.path.join(SCR, "pwcli_session.log")
        self._log = open(self.logpath, "w")
        self.p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE,
                                  stdout=self._log, stderr=subprocess.STDOUT,
                                  env=env or ENV, start_new_session=True, text=True)
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
            self.p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self.p.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            self._log.close()
        except Exception:
            pass


def dump(timeout=15.0):
    r = run(["pw-dump"], timeout=timeout)
    try:
        return json.loads(r["stdout"])
    except Exception:
        return None


# The operator's session is reached through the DEFAULT XDG_RUNTIME_DIR
# (/run/user/1000). Only the seat's PIPEWIRE_* overrides are dropped: dropping
# XDG_RUNTIME_DIR too would make pw-dump unable to find the operator socket at
# all (measured: shared_objects=0 in the first g pass).
SHARED_ENV = {k: v for k, v in os.environ.items()
              if k not in ("PIPEWIRE_RUNTIME_DIR", "WIREPLUMBER_CONFIG_DIR",
                           "WIREPLUMBER_DATA_DIR")}


def shared_dump(timeout=20.0):
    """Read-only dump of the OPERATOR's shared graph (never mutated)."""
    r = run(["pw-dump"], timeout=timeout, env=SHARED_ENV)
    try:
        return json.loads(r["stdout"])
    except Exception:
        return None


def shared_namespace_count(prefix="r97b"):
    objs = shared_dump()
    n = 0
    for o in objs or []:
        pr = (o.get("info") or {}).get("props") or o.get("props") or {}
        if any(isinstance(v, str) and prefix in v for v in pr.values()):
            n += 1
    return n, (len(objs) if objs is not None else -1)


def nodes(objs):
    out = []
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            pr = (o.get("info") or {}).get("props") or {}
            out.append((o["id"], pr.get("node.name"), pr.get("media.class"),
                        pr.get("priority.session"), pr.get("node.description")))
    return sorted(out)


def node_props(objs, name, prefixes=("node.", "target.", "priority.", "object.")):
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            pr = (o.get("info") or {}).get("props") or {}
            if pr.get("node.name") == name:
                return {k: v for k, v in pr.items()
                        if any(k.startswith(p) for p in prefixes)}
    return None


def meta_rows(objs, name="default"):
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Metadata":
            pr = o.get("props") or {}
            if pr.get("metadata.name") == name:
                return (o["id"], o.get("metadata") or [])
    return (None, None)


def nullsink(cli, name, session=100, driver=100, desc=None, extra=""):
    desc = desc or name
    props = (f"{{ factory.name=support.null-audio-sink node.name={name} "
             f"node.description={desc} media.class=Audio/Sink "
             f"priority.session={session} priority.driver={driver} {extra} }}")
    return cli.cmd(f"create-node adapter {props}")


def sink_by_name(objs, name):
    for i, n, mc, ps, d in nodes(objs):
        if n == name:
            return i
    return None


def sink_serial(objs, name):
    for o in objs or []:
        if o.get("type") == "PipeWire:Interface:Node":
            pr = (o.get("info") or {}).get("props") or {}
            if pr.get("node.name") == name:
                return pr.get("object.serial")
    return None


def default_sink_value(objs):
    mid, rows = meta_rows(objs)
    for r in rows or []:
        if r.get("key") == "default.audio.sink":
            return (mid, r.get("value"))
    return (mid, None)


def meta_value(objs, key, name="default"):
    mid, rows = meta_rows(objs, name)
    for r in rows or []:
        if r.get("key") == key:
            return (mid, r.get("value"))
    return (mid, None)


def state_file():
    p = os.path.join(SEAT, "conf", "xdg-state", "wireplumber", "default-nodes")
    return open(p).read() if os.path.exists(p) else None


def wait_default(name, cap=8.0):
    t0 = time.monotonic()
    val = None
    while time.monotonic() - t0 < cap:
        _, val = default_sink_value(dump())
        got = (val or {}).get("name") if isinstance(val, dict) else val
        if got == name:
            return True, val, round(time.monotonic() - t0, 3)
        time.sleep(0.25)
    return False, val, round(time.monotonic() - t0, 3)


def wait_node(name, cap=8.0):
    t0 = time.monotonic()
    while time.monotonic() - t0 < cap:
        i = sink_by_name(dump(), name)
        if i is not None:
            return i
        time.sleep(0.2)
    return None


def stage_out(stage):
    os.makedirs(REC, exist_ok=True)
    return {"stage": stage, "host": os.uname().nodename,
            "seat": SEAT, "loadavg_start": loadavg(),
            "hogs_at_start": hog_count(),
            "foreign_at_start": foreign_census(),
            "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "reps": []}


def stage_write(out, fname):
    """Write the receipt, and also an arm-suffixed copy so both arms survive.

    r97b: the ambient and hogs arms run in the same seat, so `<name>.json`
    always holds the newest arm and `<name>.<arm>.json` pins each arm.
    """
    os.makedirs(REC, exist_ok=True)
    out["loadavg_end"] = loadavg()
    p = os.path.join(REC, fname)
    with open(p, "w") as f:
        json.dump(out, f, indent=1)
    arm = out.get("arm")
    if arm:
        base, ext = os.path.splitext(fname)
        p2 = os.path.join(REC, f"{base}.{arm}{ext}")
        with open(p2, "w") as f:
            json.dump(out, f, indent=1)
    print("wrote", p, "loadavg", out["loadavg_start"], "->", out["loadavg_end"])
    return p


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        print("loadavg", loadavg())
        print("foreign", json.dumps(foreign_census()))
        print("ensure_up", ensure_up(verbose=True))
        cli = PwCli()
        nullsink(cli, "r97b_smoke", 100, 100)
        time.sleep(1.0)
        objs = dump()
        print("clock", core_clock())
        print(json.dumps(nodes(objs), indent=1))
        print("default:", default_sink_value(objs))
        cli.close()
