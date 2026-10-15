#!/usr/bin/env python3
"""r83-verifier verdict-surface extractor — three tiers.

EXACT tier (must be identical run-to-run after pid normalization):
  rc/signal/class/killed, linked, move_rc, failopen flags,
  out_port_names, post_move_consumers, content_witness, stderr_tail,
  tap_stats {exists,rate,settled_frames,all_zero}, window_amps.exists.
NAMED tier (arm outcomes — membership in the documented vocabulary,
  recorded honestly; compared as SETS not values):
  outcome, mono_outcome, control_outcome, artifact_outcome.
ANALOG tier (reported separately, range-checked, never diffed):
  tap_stats channel numbers, window_amps amplitudes, dev ratios,
  transport_s/onset_s/wall_s.
"""
import json, re, sys

EXACT = ("exit_code", "signal", "error_class", "error_hit",
         "killed_at_bound", "linked", "move_rc",
         "failopen_target_is_default", "out_port_names",
         "post_move_consumers", "content_witness", "stderr_tail",
         "tap_exit", "nodes_after")
NAMED = ("outcome", "mono_outcome", "control_outcome",
         "artifact_outcome")

_FREQ_ROLE = {}
for i in range(4):
    L = 997 + i * 211
    _FREQ_ROLE[L] = "L"
    _FREQ_ROLE[L + 503] = "R"
    _FREQ_ROLE[2 * L] = "L2"
    _FREQ_ROLE[2 * (L + 503)] = "R2"

def _ampkey(k):
    m = re.match(r"^(a\d+|amp_at)_(\d+)$", k)
    if m and int(m.group(2)) in _FREQ_ROLE:
        return f"{m.group(1)}_{_FREQ_ROLE[int(m.group(2))]}"
    return k

def norm(x):
    if isinstance(x, str):
        x = re.sub(r"r83a_\d+_", "r83a_<pid>_", x)
        x = re.sub(r"r83a_(ns[a-z0-9_]*?)_\d+", r"r83a_\1_<pid>", x)
        x = re.sub(r"r83v_\d+_", "r83v_<pid>_", x)
        x = re.sub(r"r83v_(ns[a-z0-9_]*?)_\d+", r"r83v_\1_<pid>", x)
        x = re.sub(r"\b\d{5,}\b", "<n>", x)
        return x
    if isinstance(x, dict):
        return {norm(_ampkey(str(k))): norm(v) for k, v in x.items()}
    if isinstance(x, list):
        return [norm(v) for v in x]
    return x

def leg_tiers(lv):
    exact = {k: norm(lv.get(k)) for k in EXACT if k in lv}
    named = {k: norm(lv.get(k)) for k in NAMED if k in lv}
    analog = {}
    si = lv.get("sink_input")
    if isinstance(si, dict):
        exact["sink_input"] = {k: norm(v) for k, v in si.items()
                               if k not in ("index", "sink")}
    tp = lv.get("tap")
    if isinstance(tp, dict):
        exact["tap.carries_tone"] = tp.get("carries_tone")
    pm = lv.get("pre_move")
    if isinstance(pm, dict):
        exact["pre_move.consumers"] = norm(pm.get("consumers"))
    o = lv.get("out")
    if isinstance(o, dict):
        exact["out.exists"] = o.get("exists")
        exact["out.rate"] = (o.get("fmt") or {}).get("rate") \
            if isinstance(o.get("fmt"), dict) else o.get("rate")
    t = lv.get("tap_stats")
    if isinstance(t, dict):
        exact["tap.exists"] = t.get("exists")
        exact["tap.rate"] = t.get("rate")
        exact["tap.settled_frames"] = t.get("settled_frames")
        exact["tap.all_zero"] = [c.get("all_zero")
                                 for c in t.get("channels", [])]
        chans = []
        for c in t.get("channels", []):
            leaf = {}
            for k, v in c.items():
                mk = _ampkey(k)
                if mk != k or k in ("min", "max", "mean", "peak_abs",
                                    "zero_frac", "neg_frac"):
                    leaf[mk] = v
            chans.append(leaf)
        analog["tap.channels"] = norm(chans)
    w = lv.get("window_amps")
    if isinstance(w, dict):
        exact["win.exists"] = w.get("exists")
        analog["win.windows"] = norm(
            [{_ampkey(k): v for k, v in win.items() if k != "at_s"}
             for win in w.get("windows", [])])
    for k in ("mono_mix_dev_ratio", "stereo_pass_dev_ratio",
              "transport_s", "onset_s", "tap_onset_s", "wall_s"):
        if k in lv:
            analog[k] = norm(lv[k])
    return exact, named, analog

def surface(path):
    d = json.load(open(path))
    m = d["measurements"]
    surf = {}
    for ek, e in m.items():
        legs = e.get("legs")
        rec = {"failures": e.get("failures"),
               "sinks_gone": norm(e.get("sinks_gone")),
               "own_nodes_after": norm(e.get("own_nodes_after"))}
        if not legs:
            rec["_nolegs"] = True
            surf[ek] = rec
            continue
        es = {}
        for ln, lv in legs.items():
            x, n, a = leg_tiers(lv)
            es[ln] = {"exact": x, "named": n, "analog": a}
        rec["legs"] = es
        surf[ek] = rec
    return surf

def diff(a, b, path=""):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                out.append(f"{path}.{k}: only-in-B {b[k]!r}")
            elif k not in b:
                out.append(f"{path}.{k}: only-in-A {a[k]!r}")
            else:
                out.extend(diff(a[k], b[k], f"{path}.{k}"))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: len {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            out.extend(diff(x, y, f"{path}[{i}]"))
    elif a != b:
        out.append(f"{path}: {a!r} != {b!r}")
    return out

def strip_tier(surf, keep=("exact",)):
    """Return surf with only the requested per-leg tiers + entry meta."""
    out = {}
    for ek, rec in surf.items():
        r = {k: v for k, v in rec.items() if k != "legs"}
        if "legs" in rec:
            r["legs"] = {ln: {t: lv.get(t) for t in keep if t in lv}
                         for ln, lv in rec["legs"].items()}
        out[ek] = out.get(ek) or r
    return out

if __name__ == "__main__":
    mode = sys.argv[1]           # exact | named | analog | all
    sa = surface(sys.argv[2])
    sb = surface(sys.argv[3])
    if mode == "all":
        d = diff(sa, sb)
    else:
        d = diff(strip_tier(sa, (mode,)), strip_tier(sb, (mode,)))
    print(f"{mode} surface {sys.argv[2]} vs {sys.argv[3]}: {len(d)} diffs")
    for line in d[:300]:
        print(" ", line)
