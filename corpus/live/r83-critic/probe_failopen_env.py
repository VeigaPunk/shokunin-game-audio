"""r83 critic probe D — env override of the fail-open `-P ''` shape (entry 7).

Entry 7 pins `-P ''` as "fail-open to the SESSION default sink" and records
`default_sink_now` beside it. The legs spawn with env=None. This probe runs the
exact `-P ''` shape with a scrubbed env vs PIPEWIRE_NODE / PULSE_SINK set, and
reports the realized output consumers. If the env node wins, the leg still
passes its (route-shape) gate while `failopen_target_is_default` silently reads
False — the "default" in the claim is env-steered.
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


def sh(*a):
    p = subprocess.run(list(a), capture_output=True, timeout=15)
    return p.returncode, p.stdout.decode(errors="replace").strip()


def load(name):
    rc, out = sh("pactl", "load-module", "module-null-sink",
                 f"sink_name={name}")
    return int(out) if out.isdigit() else None


def sample(tag, extra_env):
    env = {"PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp"),
           "XDG_RUNTIME_DIR": os.environ.get("XDG_RUNTIME_DIR", "")}
    env.update(extra_env or {})
    argv = ["pw-loopback", "-n", tag, "-C", E1, "-i",
            "stream.capture.sink=true", "-P", ""]
    p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, env=env,
                         start_new_session=True)
    time.sleep(1.6)
    g = ma._pwcat_r83_graph()
    s = {"out_consumers": ma._pwcat_r83_consumers(g, f"output.{tag}"),
         "in_producers": ma._pwcat_r83_producers(g, f"input.{tag}"),
         "pactl_default": ma._pwcat_r83_default_now()}
    try:
        os.killpg(p.pid, 9)
    except Exception:
        pass
    p.wait()
    return {"env": extra_env, "argv": " ".join(argv), **s}


out = {}
i1, i2 = load(E1), load(E2)
time.sleep(1.0)
try:
    out["ctl"] = sample("r83c_fo_ctl", None)
    out["pw_node"] = sample("r83c_fo_pn", {"PIPEWIRE_NODE": E2})
    out["pulse_sink"] = sample("r83c_fo_ps", {"PULSE_SINK": E2})
finally:
    for i in (i1, i2):
        if i:
            sh("pactl", "unload-module", str(i))
    out["residual"] = [ln for ln in sh("pactl", "list", "sinks", "short")[1]
                       .splitlines() if "r83c_" in ln]
print(json.dumps(out, indent=1))
