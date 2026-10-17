#!/usr/bin/env python3
"""r82-simplifier: independent verdict-surface stability check on the two
pinned replay pairs (run1/run2 and final3/final4).

The r82 family is live-host data: bytes written, module indices, pid-stamped
sink names and the `-sources/-sinks` enumerations are volatile by
construction (the author's own stability-r82-final34.txt classifies the
same fields). This script compares only the VERDICT surface:
  per leg   : exit_code, error_class, killed, artifact class (exists/riff/
              fmt/ch/rate/bits), the T5 zero-hit `out` (None for e1..e6),
              the T7 d2 key set, and `fired` kinds + non-index results
  per entry : failures, recorded arms, sinks_gone (pid-normalized),
              own_nodes_after, coverage_blocked
Exit 0 = identical in both pairs.
"""
import json
import re
import sys

PAIRS = [("run1.measurements.json", "run2.measurements.json"),
         ("final3.measurements.json", "final4.measurements.json")]
DIR = "corpus/live/r82-author/ffmpeg-r82-runs/"
TAG = re.compile(r"r82ff(?:x|_ns)?_\d+")
fails = []

ARTIFACT_KEYS = ("exists", "riff", "fmt", "ch", "rate", "bits", "data",
                 "frames_declared", "data_declared")
# enumeration legs print the LIVE foreign graph (environmental by
# construction — the author's stability file classifies these leaves as
# environmental): compare rc/class only, never the node list.
ENUM_LEGS = {"d2_sources_pipewire", "d3_sources_pulse", "d4_sinks_pulse"}
FIRED_VOLATILE = ("verified_index", "captured", "stderr_tail")


def norm(v):
    if isinstance(v, str):
        return TAG.sub("r82ff_<pid>", v)
    if isinstance(v, list):
        return [norm(x) for x in v]
    if isinstance(v, dict):
        return {TAG.sub("r82ff_<pid>", str(k)): norm(x) for k, x in v.items()}
    return v


def artifact(out):
    if not isinstance(out, dict):
        return out                      # None stays None (T5 evidence)
    return {k: out.get(k) for k in ARTIFACT_KEYS if k in out}


def surface(m):
    out = {}
    for k, v in m.items():
        if not k.startswith("ffpw_"):
            continue
        e = {"failures": v.get("failures")}
        for arm in ("c3_default_realizations", "a5_realization",
                    "p6_env_vs_flag_winner", "p7_env_vs_flag_winner",
                    "a6_clamped_rate", "p11_env_target",
                    "sinks_gone", "own_nodes_after", "coverage_blocked"):
            if arm in v:
                e[arm] = norm(v[arm])
        legs = {}
        for ln, leg in (v.get("legs") or {}).items():
            if not isinstance(leg, dict):
                continue
            leaf = {"rc": leg.get("exit_code"),
                    "cls": leg.get("error_class"),
                    "killed": leg.get("killed")}
            if "out" in leg and ln not in ENUM_LEGS:
                leaf["out"] = artifact(leg.get("out"))
            if ln == "d2_sources_pipewire":        # T7 zero-hit evidence
                leaf["keys"] = sorted(leg.keys())
            if leg.get("fired"):
                leaf["fired"] = [
                    {"kind": f.get("kind"),
                     "result": {kk: norm(vv) for kk, vv in
                                (f.get("result") or {}).items()
                                if kk not in FIRED_VOLATILE}}
                    for f in leg["fired"]]
            legs[ln] = leaf
        e["legs"] = legs
        out[k] = e
    return out


for a, b in PAIRS:
    A = surface(json.load(open(DIR + a))["measurements"])
    B = surface(json.load(open(DIR + b))["measurements"])
    keys_a, keys_b = sorted(A), sorted(B)
    print(f"== {a} vs {b} ==")
    print(f"   r82 entries: {len(keys_a)} vs {len(keys_b)} "
          f"({'same set' if keys_a == keys_b else 'DIFFERENT'})")
    if keys_a != keys_b:
        fails.append(f"{a}/{b}: entry sets differ")
        continue
    diffs = []
    for k in keys_a:
        if A[k] != B[k]:
            diffs.append(k)
            for sub in sorted(set(A[k]) | set(B[k])):
                if A[k].get(sub) != B[k].get(sub):
                    if sub == "legs":
                        for ln in sorted(set(A[k][sub]) | set(B[k][sub])):
                            if A[k][sub].get(ln) != B[k][sub].get(ln):
                                print(f"   DIFF {k}.legs.{ln}:")
                                print(f"     A={A[k][sub].get(ln)}")
                                print(f"     B={B[k][sub].get(ln)}")
                    else:
                        print(f"   DIFF {k}.{sub}: A={A[k].get(sub)} "
                              f"B={B[k].get(sub)}")
    print(f"   identical verdict surface: {len(keys_a) - len(diffs)}/"
          f"{len(keys_a)} entries"
          + (f"  DIFFERING: {diffs}" if diffs else ""))
    if diffs:
        fails.append(f"{a}/{b}: differing entries {diffs}")
    print()

if fails:
    print(f"RESULT: {len(fails)} FAILURE(S)")
    sys.exit(1)
print("RESULT: BOTH PINNED PAIRS ARE VERDICT-SURFACE IDENTICAL")
