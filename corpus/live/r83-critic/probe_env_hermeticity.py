"""r83 critic probe C — ambient-env hermeticity of the r83 leg shapes.

The fixture spawns every leg with env=None (inherits the operator's whole
environment). This probe asks whether any ambient PIPEWIRE_*/PULSE_* variable
changes what an r83-shaped leg realizes:

  1. PIPEWIRE_LATENCY=1024/48000 + `pw-loopback -l 5`  -> node.latency?
  2. PIPEWIRE_PROPS='{ node.name=... }' + pw-cat       -> node.name?
  3. PULSE_SINK=<sink> + `pw-cat --target ''`          -> consumer identity?
  4. PIPEWIRE_NODE=<sink> + `pw-cat` (no --target)     -> consumer identity?

Each leg is compared against the same leg with a scrubbed env. Read-only w.r.t.
the repo (runs from the /tmp export, own r83c_* sinks, unloaded at exit).
"""
import importlib.util
import json
import os
import subprocess
import time

EXPORT = "/tmp/r83critic-src"
spec = importlib.util.spec_from_file_location(
    "ma_r83", os.path.join(EXPORT, "corpus", "fixtures", "measure_audio.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

E1, E2 = "r83c_e1", "r83c_e2"
TMP = "/tmp/r83critic-out"
TONE = os.path.join(TMP, "r83c_tone.wav")
os.makedirs(TMP, exist_ok=True)


def sh(*a):
    p = subprocess.run(list(a), capture_output=True, timeout=15)
    return p.returncode, p.stdout.decode(errors="replace").strip(), \
        p.stderr.decode(errors="replace").strip()


def load(name):
    rc, out, err = sh("pactl", "load-module", "module-null-sink",
                      f"sink_name={name}")
    return int(out) if out.isdigit() else None


def unload(idx):
    if idx:
        sh("pactl", "unload-module", str(idx))


def sample(tag, extra_env, argv, wait=1.6):
    env = {"PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp"),
           "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", "")}
    env.update(extra_env or {})
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env,
                         start_new_session=True)
    time.sleep(wait)
    g = ma._pwcat_r83_graph()
    node = ma._pwcat_r83_find(g, tag)
    cons = ma._pwcat_r83_consumers(g, tag) if tag else None
    prods = ma._pwcat_r83_producers(g, tag) if tag else None
    streams = {}
    for nid, n in (g.get("nodes") or {}).items():
        nm = n.get("name")
        if not nm or nm in (E1, E2):
            continue
        props = n.get("props") or {}
        if str(props.get("media.class") or "").startswith("Stream") or \
                props.get("stream.is-live") is not None or \
                "pw-cat" in nm or "pw_play" in nm or "r83c" in nm:
            streams[nm] = {"consumers": ma._pwcat_r83_consumers(g, nm),
                           "producers": ma._pwcat_r83_producers(g, nm),
                           "node.name": props.get("node.name"),
                           "node.latency": props.get("node.latency"),
                           "media.class": props.get("media.class")}
    try:
        os.killpg(p.pid, 9)
    except Exception:
        pass
    p.wait()
    return {"argv": " ".join(argv), "env": extra_env, "node": node,
            "consumers": cons, "producers": prods, "streams": streams}


ma._playback_r78_write_tone(TONE, 4.0)
out = {"sinks": {}, "legs": {}}
out["sinks"]["e1"] = load(E1)
out["sinks"]["e2"] = load(E2)
time.sleep(1.0)
out["sinks"]["e1_seen"], out["sinks"]["e2_seen"] = \
    (E1 in (ma._capture_r77_sink_names() or [])), \
    (E2 in (ma._capture_r77_sink_names() or []))
try:
    base_lb = ["pw-loopback", "-n", "r83c_pl_ctl", "-C", E1, "-i",
               "stream.capture.sink=true", "-P", E2, "-l", "5"]
    out["legs"]["lb_ctl"] = sample(
        "input.r83c_pl_ctl", None, base_lb)
    out["legs"]["lb_pwlat"] = sample(
        "input.r83c_pl_lat", {"PIPEWIRE_LATENCY": "1024/48000"},
        ["pw-loopback", "-n", "r83c_pl_lat", "-C", E1, "-i",
         "stream.capture.sink=true", "-P", E2, "-l", "5"])
    out["legs"]["pc_ctl"] = sample(
        "r83c_pc_ctl", None,
        ["pw-cat", "-p", "-P", "node.name=r83c_pc_ctl", "--target", E2,
         TONE])
    out["legs"]["pc_envprops"] = sample(
        "r83c_envname", {"PIPEWIRE_PROPS": "{ node.name=r83c_envname }"},
        ["pw-cat", "-p", "--target", E2, TONE])
    out["legs"]["pc_nametarget"] = sample(
        "r83c_pc_nt", None,
        ["pw-cat", "-p", "--target", "", TONE])
    out["legs"]["pc_pulsesink"] = sample(
        "r83c_pc_ps", {"PULSE_SINK": E2},
        ["pw-cat", "-p", "--target", "", TONE])
    out["legs"]["pc_pwnode"] = sample(
        "r83c_pc_pn", {"PIPEWIRE_NODE": E2},
        ["pw-cat", "-p", TONE])
finally:
    for k, v in out["sinks"].items():
        if k in ("e1", "e2"):
            unload(v)
    out["residual"] = {nm: [ln for ln in (sh("pactl", "list", "sinks",
                                              "short")[1] or "").splitlines()
                            if nm in ln] for nm in (E1, E2)}
print(json.dumps(out, indent=1))
