#!/usr/bin/env python3
"""r84-critic probe C — un-gated r84 pins, live (committed entry function).

Two falsifiable holes in the committed `alsapw_pactl_write_r84_entry`:

  (i)  `vol_neg` records `volume_value` but the verdict only checks
       rc==0 + value-not-None. Intercepting the `-10%` call and storing
       an ABSOLUTE 10% (6553) instead of the relative 90% (58982) must
       therefore stay green while the pinned semantics are violated.
  (ii) `vol_150` / `vol_25_idx` carry no absolute base floor (unlike
       `vol_50_*`/`src_vol50_*` which require base>=500). A synthetic
       64-amp base (0.8% of the real 8192 tone) with post=216 (x3.375)
       and post=1 (x0.015625 — pure quantization, i.e. a silent post
       window) must therefore pass.

Everything else in the entry runs for real on a probe-owned null sink
(`r84a_ns_<probe pid>`); only `_alsapw_r84_tap_leg` is replaced (so no
monitor taps / tones are spawned for the envelope arms) and the single
`-10%` pactl call is intercepted. The entry's own teardown unloads its
sink; a residual check follows. No tracked writes.
"""
import json
import os
import sys
import time
from pathlib import Path

SRC = Path("/home/vgpnk/Projects/shokunin/tmp/r84critic-src/corpus/fixtures")
sys.path.insert(0, str(SRC))
import measure_audio as M  # noqa: E402

OUT = Path(__file__).with_name("probeC-ungated-pins.json")


def fake_series(base, post):
    s = [(round(i / 10.0, 2), base) for i in range(0, 25)]
    s += [(round(i / 10.0, 2), post) for i in range(26, 73)]
    return s


RATIOS = {"vol_50_0": 0.125, "vol_50_1": 0.125,
          "src_vol50_0": 0.125, "src_vol50_1": 0.125,
          "vol_150": 3.375, "vol_25_idx": 0.015625}
BASE = 64


def fake_tap_leg(name, ctx, actions, dur_s=7.2, role=None):
    ratio = RATIOS.get(name)
    post = max(0, int(round(BASE * ratio))) if ratio is not None else BASE
    return {"name": name, "tag": f"{M.ALSAPW_R84_PREFIX}_{name}",
            "series": fake_series(BASE, post), "dur_s": dur_s,
            "synthetic": {"base": BASE, "post": post},
            "pre_reset": {"writes": []},
            "actions": {}}


def main():
    rec = {"probe": "probeC-ungated-pins", "pid": os.getpid(),
           "loadavg": open("/proc/loadavg").read().split()[:3],
           "synthetic_base": BASE}
    real_pactl = M._alsapw_r84_pactl
    ns = M.ALSAPW_R84_NS
    intercepts = []

    def pactl(*args, **kw):
        if args == ("set-sink-volume", ns, "-10%"):
            res = real_pactl("set-sink-volume", ns, "10%")
            intercepts.append({"intercepted": list(args),
                               "really_wrote": ["set-sink-volume", ns,
                                                "10%"],
                               "rc": res.get("exit_code")})
            return res
        return real_pactl(*args, **kw)

    real_tap_leg = M._alsapw_r84_tap_leg
    M._alsapw_r84_tap_leg = fake_tap_leg
    M._alsapw_r84_pactl = pactl
    try:
        entry = M.alsapw_pactl_write_r84_entry()
    finally:
        M._alsapw_r84_tap_leg = real_tap_leg
        M._alsapw_r84_pactl = real_pactl
    rec["intercepts"] = intercepts
    rec["failures"] = entry.get("failures")
    legs = entry.get("legs") or {}
    rec["evidence"] = {
        "vol_neg": {k: (legs.get("vol_neg") or {}).get(k)
                    for k in ("volume_value", "volume_percent",
                              "get_sink_volume")},
        "vol_150": {k: (legs.get("vol_150") or {}).get(k)
                    for k in ("base_amp", "post_amp", "ratio")},
        "vol_25_idx": {k: (legs.get("vol_25_idx") or {}).get(k)
                       for k in ("base_amp", "post_amp", "ratio")},
        "vol_50_0": {k: (legs.get("vol_50_0") or {}).get(k)
                     for k in ("base_amp", "post_amp", "ratio")},
        "src_vol50_0": {k: (legs.get("src_vol50_0") or {}).get(k)
                        for k in ("base_amp", "post_amp", "ratio")},
    }
    rec["vol_neg_in_failures"] = [f for f in (entry.get("failures") or [])
                                  if f.startswith("vol_neg")]
    rec["vol_150_in_failures"] = [f for f in (entry.get("failures") or [])
                                  if f.startswith("vol_150")]
    rec["vol_25_idx_in_failures"] = [
        f for f in (entry.get("failures") or [])
        if f.startswith("vol_25_idx")]
    rec["vol_50_in_failures"] = [f for f in (entry.get("failures") or [])
                                 if f.startswith(("vol_50", "src_vol50"))]
    rec["coverage_blocked"] = entry.get("coverage_blocked")
    rec["sinks_gone"] = entry.get("sinks_gone")
    rec["own_nodes_after"] = entry.get("own_nodes_after")
    rec["unloads"] = entry.get("unloads")
    rec["teardown_failures"] = [f for f in (entry.get("failures") or [])
                                if f.startswith("teardown")]
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))


if __name__ == "__main__":
    main()
