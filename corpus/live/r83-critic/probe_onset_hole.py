"""r83 critic probe A — the entry-3 silent-unmeasured hole.

Loads the COMMITTED fixture (a151a226 export) and calls the real
pwcat_latency_props_r83_entry() with `_pwcat_r83_onset_leg` monkeypatched so
that the -d 0.25 and -l 1000 arms return a blocked/unmeasured cell (exactly
the shape the real function returns when the loopback never links:
`{"name":..., "linked": False, "blocked": ...}` with no `transport_s`).

Hypothesis to falsify: "the entry fails (or at least records a failure) when
both -d 0.25 legs AND both -l 1000 legs produce no transport."  If the entry
comes back with an empty failures list, the two pins are silently unmeasured
while the entry reads green.

Read-only w.r.t. the repo: runs from the /tmp export, PYTHONDONTWRITEBYTECODE=1.
"""
import importlib.util
import json
import os
import sys

EXPORT = "/tmp/r83critic-src"
spec = importlib.util.spec_from_file_location(
    "ma_r83", os.path.join(EXPORT, "corpus", "fixtures", "measure_audio.py"))
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

real = ma._pwcat_r83_onset_leg
calls = []


def fake(name, ctx, extra=()):
    calls.append((name, list(extra)))
    if name.startswith("onset_d025") or name.startswith("onset_l1000"):
        return {"name": name, "ltag": f"{ma.PWCAT_R83_PREFIX}_{name}",
                "argv": "pw-loopback ... (simulated)", "extra": list(extra),
                "linked": False, "link_waited_s": 9.0,
                "blocked": "loopback never linked both sides"}
    return real(name, ctx, extra)


ma._pwcat_r83_onset_leg = fake
entry = ma.pwcat_latency_props_r83_entry()
print(json.dumps({
    "failures": entry.get("failures"),
    "onset_summary": entry.get("onset_summary"),
    "simulated_legs": [n for n, _ in calls
                       if n.startswith(("onset_d025", "onset_l1000"))],
    "blocked_flags": {n: entry["legs"][n].get("blocked")
                      for n in entry["legs"]
                      if n.startswith(("onset_d025", "onset_l1000"))},
    "real_legs_ran": [n for n, _ in calls
                      if not n.startswith(("onset_d025", "onset_l1000"))],
}, indent=1))
