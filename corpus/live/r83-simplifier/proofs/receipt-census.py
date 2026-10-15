#!/usr/bin/env python3
"""r83-simplifier receipt census — 0-hit / realization census over the two
pinned r83 author runs (corpus/live/r83-author/measurements-run{1,2}.json).

Read-only. Prints PASS/FAIL per predicate and the counts behind it.
Run:  python3 receipt-census.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]          # audio-shokunin/
AUTHOR = ROOT / "corpus" / "live" / "r83-author"
RUNS = ["run1", "run2"]
ENTRIES = [
    "pwcat_props_parse_r83_probe",
    "pwcat_empty_props_segv_r83_probe",
    "pwcat_latency_props_r83_probe",
    "pwcat_channel_matrix_r83_probe",
    "pwcat_remix_props_r83_probe",
    "pwcat_resample_props_r83_probe",
    "pwcat_failopen_args_r83_probe",
]

data = {}
for r in RUNS:
    data[r] = json.load(open(AUTHOR / f"measurements-{r}.json"))["measurements"]

results = []


def check(name, ok, detail):
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def legs_of(run, key):
    return data[run][key].get("legs") or {}


# ---------------------------------------------------------------- A: totals
tot = {r: sum(len(legs_of(r, k)) for k in ENTRIES) for r in RUNS}
check("A legs == 128 per run", all(v == 128 for v in tot.values()),
      f"{tot}")
fl = {r: {k: data[r][k].get("failures") for k in ENTRIES} for r in RUNS}
check("A zero failures on every entry", all(
    v in ([], None) for r in RUNS for v in fl[r].values()),
      f"{ {r: sorted({str(v) for v in fl[r].values()}) for r in RUNS} }")

# --------------------------------------------- B: every leg carries a verdict
# leg shapes: lb/play/rec legs carry exit_code; the -d onset legs are a
# different shape by design (linked / onset_s / transport_s / tap_exit).
KEYS = {
    "pwcat_props_parse_r83_probe": ["exit_code", "killed_at_bound"],
    "pwcat_empty_props_segv_r83_probe": ["exit_code"],
    "pwcat_latency_props_r83_probe": ["exit_code"],
    "pwcat_channel_matrix_r83_probe": ["exit_code"],
    "pwcat_remix_props_r83_probe": ["exit_code"],
    "pwcat_resample_props_r83_probe": ["exit_code"],
    "pwcat_failopen_args_r83_probe": ["exit_code"],
}
ONSET = {"linked", "link_waited_s", "tap_exit", "onset_s", "transport_s"}
bad = []
n_onset = 0
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            if ONSET <= set(leg):            # an onset leg: its own shape
                n_onset += 1
                continue
            for kk in KEYS[k]:
                if kk not in leg:
                    bad.append(f"{r}/{k}/{ln}:{kk}")
check("B every non-onset leg has exit_code (+killed_at_bound)",
      not bad, f"{bad[:8]}  (onset legs: {n_onset // len(RUNS)}/run)")

# --------------------------------------------------- C: tap arms realization
def tap_leaf(run, key, legname, sub=None):
    leg = legs_of(run, key).get(legname) or {}
    t = leg.get("tap") or {}
    return t.get(sub) if sub else t


c_prod = {r: [] for r in RUNS}
c_bound = {r: [] for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            t = leg.get("tap") or {}
            if "bound_producers" in t:
                c_prod[r].append((k, ln, t["bound_producers"],
                                  t.get("bound_to_target")))
            if "bound_to_target" in t:
                c_bound[r].append(t["bound_to_target"])
check("C lb_leg tap bound_producers present",
      all(c_prod[r] for r in RUNS),
      f"{ {r: len(c_prod[r]) for r in RUNS} }")
nempty = [x for r in RUNS for x in c_prod[r] if not x[2]]
check("C lb_leg bound_producers non-empty (the leaf is realizable)",
      not nempty, f"{nempty[:4]}")
ntrue = [x for r in RUNS for x in c_prod[r] if x[3] is not True]
check("C lb_leg bound_to_target always True", not ntrue, f"{ntrue[:4]}")

# play_leg sample.tap_producers
ptp = {r: [] for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            s = leg.get("sample") or {}
            if "tap_producers" in s:
                ptp[r].append((k, ln, s["tap_producers"]))
check("C play_leg sample.tap_producers leaf present",
      all(ptp[r] for r in RUNS), f"{ {r: len(ptp[r]) for r in RUNS} }")
nonnull = [x for r in RUNS for x in ptp[r] if x[2]]
check("C play_leg tap_producers non-null somewhere",
      bool(nonnull), f"{nonnull[:4]}")

# ------------------------------------------------- D: feed / probe_default
feeds = {r: [] for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            if leg.get("feeds"):
                feeds[r].append((k, ln, leg["feeds"]))
check("D feed leaves present in both runs", all(feeds[r] for r in RUNS),
      f"{ {r: len(feeds[r]) for r in RUNS} }")

pdef = {r: [] for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            if "default_sink_now" in leg:
                pdef[r].append((k, ln, leg["default_sink_now"]))
check("D probe_default realized", all(pdef[r] for r in RUNS),
      f"{ {r: len(pdef[r]) for r in RUNS} }")

# ------------------------------------------------------- E: absence probes
ab = {r: [] for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            for s in leg.get("samples") or []:
                if s.get("absent_probe"):
                    ab[r].append((k, ln, s["absent_probe"]))
check("E probe_absent realized", all(ab[r] for r in RUNS),
      f"{ {r: len(ab[r]) for r in RUNS} }")

# ------------------------------------------------ F: never-fired verdict arms
never = {}


def collect(run, key, pred, label):
    hits = 0
    for ln, leg in legs_of(run, key).items():
        if pred(leg):
            hits += 1
    never.setdefault(label, {})[run] = hits


for r in RUNS:
    collect(r, "pwcat_props_parse_r83_probe",
            lambda l: l.get("killed_at_bound") is False,
            "F1 props_parse: a leg that exited early")
    collect(r, "pwcat_empty_props_segv_r83_probe",
            lambda l: l.get("exit_code") != -11, "F2 segv: non-SIGSEGV leg")
    collect(r, "pwcat_empty_props_segv_r83_probe",
            lambda l: bool(l.get("nodes_after")), "F3 segv: nodes published")
    collect(r, "pwcat_latency_props_r83_probe",
            lambda l: l.get("transport_s") is None and "onset_s" in l,
            "F4 latency: onset unmeasured")
    collect(r, "pwcat_latency_props_r83_probe",
            lambda l: l.get("linked") is False, "F5 latency: unlinked onset leg")
    collect(r, "pwcat_channel_matrix_r83_probe",
            lambda l: l.get("control_outcome") == "silent",
            "F6 matrix: silent control")
    collect(r, "pwcat_channel_matrix_r83_probe",
            lambda l: l.get("mono_outcome") == "deviating",
            "F7 matrix: c1 deviating")
    collect(r, "pwcat_channel_matrix_r83_probe",
            lambda l: l.get("mono_outcome") == "unmeasured",
            "F8 matrix: m_alone unmeasured")
    collect(r, "pwcat_remix_props_r83_probe",
            lambda l: l.get("move_skipped") is not None,
            "F9 remix: move skipped")
    collect(r, "pwcat_resample_props_r83_probe",
            lambda l: l.get("artifact_outcome") == "deviates"
            or str(l.get("artifact_outcome", "")).startswith("deviates"),
            "F10 resample: deviating artifact")
    collect(r, "pwcat_resample_props_r83_probe",
            lambda l: str(l.get("artifact_outcome", "")).startswith(
                "artifact_or_deviation"),
            "F11 resample: non-upsample artifact")
    collect(r, "pwcat_failopen_args_r83_probe",
            lambda l: l.get("outcome") == "nodes_not_seen",
            "F12 failopen: nodes not seen")
    collect(r, "pwcat_resample_props_r83_probe",
            lambda l: l.get("tap_stats", {}).get("unsupported") is not None,
            "F13 resample: unsupported tap_stats")

print("\n== F. never-fired verdict arms (0-hit counts across both runs) ==")
for lab in sorted(never, key=lambda s: int(s.split()[0][1:])):
    print(f"  {lab}: {never[lab]}")

# ------------------------------------------------- G: error-class realization
cls = {r: {} for r in RUNS}
for r in RUNS:
    for k in ENTRIES:
        for ln, leg in legs_of(r, k).items():
            c = leg.get("error_class")
            if c:
                cls[r][c] = cls[r].get(c, 0) + 1
check("G error classes realized in both runs",
      all(cls[r] for r in RUNS), f"{cls}")

# ----------------------------------------------- H: serial / sinks witnesses
for r in RUNS:
    ser = data[r]["pwcat_failopen_args_r83_probe"].get("serials")
    check(f"H {r} serials read", bool(ser and ser.get("nsa")
                                      and ser.get("nsb")), f"{ser}")
    sg = data[r]["pwcat_failopen_args_r83_probe"].get("sinks_gone")
    check(f"H {r} sinks_gone all true", bool(sg) and all(sg.values()),
          f"{sg}")
    oa = data[r]["pwcat_failopen_args_r83_probe"].get("own_nodes_after")
    check(f"H {r} own_nodes_after empty", oa == [], f"{oa}")

# ----------------------------------------------------- I: onset_summary pin
for r in RUNS:
    os_ = data[r]["pwcat_latency_props_r83_probe"].get("onset_summary") or {}
    check(f"I {r} onset_summary has ctl_median + d10 deltas",
          os_.get("ctl_median_s") is not None
          and os_.get("d10_deltas_vs_ctl") is not None,
          f"ctl_median={os_.get('ctl_median_s')} "
          f"d10_deltas={os_.get('d10_deltas_vs_ctl')} "
          f"d025={os_.get('d025_transports')} "
          f"l1000={os_.get('l1000_transports')}")

print("\n== summary ==")
nfail = [n for n, ok, _ in results if not ok]
print(f"  predicates: {len(results)}  FAIL: {nfail}")
sys.exit(0)
