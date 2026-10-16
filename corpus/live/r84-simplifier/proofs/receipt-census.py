#!/usr/bin/env python3
"""r84 simplifier RECEIPT census over BOTH pinned author runs (the replay
oracle). Read-only. Output: receipt-census.txt

R1..R9 assert the surfaces the patch touches; every check is derived from the
two committed receipts, nothing from the patch author's memory.
"""
import json
import sys
from pathlib import Path

RUNS = ["../r84-author/runs/run1/measurements.json",
        "../r84-author/runs/run2/measurements.json"]
ENTRIES = ["alsapw_dev_lattice_r84_probe", "alsapw_pw_args_r84_probe",
           "alsapw_pulseprop_r84_probe", "alsapw_pactl_write_r84_probe",
           "alsapw_monstream_r84_probe", "alsapw_negctl_r84_probe"]
out = []
PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
    else:
        FAIL += 1
    out.append(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")


D = [json.loads(Path(r).read_text()) for r in RUNS]
M = [d["measurements"] for d in D]

# R1 — the oracle shape
legs = [sum(len(M[i][e].get("legs") or {}) for e in ENTRIES) for i in (0, 1)]
fails = [[e for e in ENTRIES if M[i][e].get("failures")] for i in (0, 1)]
check("R1 oracle: 147 legs per run, 6 entries, no failures, no coverage_block",
      legs == [147, 147] and fails == [[], []] and
      all(M[i][e].get("coverage_blocked") is None for i in (0, 1)
          for e in ENTRIES),
      f"legs={legs} entries-with-failures={fails}")

# R2 — T1: no receipt surface for the unused constant
txt = [Path(r).read_text() for r in RUNS]
check("R2 no `link_wait`/`LINK_WAIT` key or value in either receipt (T1)",
      all(t.count("link_wait") == 0 and t.count("LINK_WAIT") == 0 for t in txt),
      f"occurrences run1={txt[0].count('link_wait')}/"
      f"{txt[0].count('LINK_WAIT')} run2={txt[1].count('link_wait')}/"
      f"{txt[1].count('LINK_WAIT')}")

# R3 — T2/T9: the loads domain is dicts; teardown receipts are clean
un_types = []
for i in (0, 1):
    for e in ENTRIES:
        for tag, leaf in (M[i][e].get("unloads") or {}).items():
            un_types.append(type(leaf).__name__)
check("R3 every `unloads` value is a dict (T2/T9 guard domain)",
      set(un_types) == {"dict"} and len(un_types) == 10,
      f"value types={sorted(set(un_types))} across {len(un_types)} entries "
      f"(run1+run2: 1+1+1+2 per run)")

# R4 — T3: st_leg argv carries no tmp path and the leg keys are stable
st = [(i, k, v) for i in (0, 1)
      for k, v in (M[i]["alsapw_pw_args_r84_probe"].get("legs") or {}).items()
      if k.startswith("st_")]
check("R4 st_leg records: argv has no /tmp token, key set identical (T3)",
      len(st) == 4 and
      all("tmp" not in v["argv"] and "r84a_ns_" in v["argv"] for _, _, v in st)
      and len({tuple(sorted(v.keys())) for _, _, v in st}) == 1,
      f"{len(st)} st_ legs; argv={[v['argv'] for _, _, v in st]}")

# R5 — T4: no `hit` key on any prop_leg record or on ctl_sigkill
prop_hit = [k for i in (0, 1)
            for k, v in (M[i]["alsapw_pulseprop_r84_probe"].get("legs")
                         or {}).items() if "hit" in v]
sig_hit = [i for i in (0, 1)
           if "hit" in (M[i]["alsapw_negctl_r84_probe"].get("legs")
                        or {}).get("ctl_sigkill", {})]
sig_keys = sorted((M[0]["alsapw_negctl_r84_probe"]["legs"]["ctl_sigkill"])
                  .keys())
check("R5 the two dead `hit` stores have no receipt surface (T4)",
      prop_hit == [] and sig_hit == [] and
      sig_keys == ["argv", "error_class", "exit_code", "signal", "stderr_tail"]
      and all(v.get("error_class") is None and v.get("signal") == "SIGKILL"
              for i in (0, 1)
              for v in [(M[i]["alsapw_negctl_r84_probe"]["legs"]["ctl_sigkill"])]),
      f"prop_leg records with `hit`={prop_hit}; ctl_sigkill with `hit`={sig_hit};"
      f" ctl_sigkill keys={sig_keys}")

# R6 — T7 domain: the sticky leg realized the armed path in both runs
sticky = [M[i]["alsapw_monstream_r84_probe"]["legs"]["sticky"] for i in (0, 1)]
check("R6 sticky realized: spawn1 100%, respawn 30%, tap 221, repaired 100%",
      all(s["spawn1_percent"] == 100 and s["respawn_percent"] == 30 and
          s["respawn_tap_med"] == 221.0 and s["repaired_percent"] == 100 and
          s.get("skipped") is None for s in sticky),
      f"run1/run2 respawn_percent={[s['respawn_percent'] for s in sticky]} "
      f"tap_med={[s['respawn_tap_med'] for s in sticky]}")

# R7 — T8/T10 domain: the ebusy hold record exists with the three keys
hold = [M[i]["alsapw_dev_lattice_r84_probe"]["legs"]["ebusy_hold"]
        for i in (0, 1)]
check("R7 ebusy_hold records carry held_pcm/pcm_states_at_hold/hold_note",
      all({"held_pcm", "pcm_states_at_hold", "hold_note", "hold_alive"} <=
          set(h) for h in hold),
      f"run1={ {k: hold[0][k] for k in ('held_pcm', 'hold_note')} } "
      f"run2={ {k: hold[1][k] for k in ('held_pcm', 'hold_note')} }")

# R8 — the touched verdict surfaces are all realized (not vacuous arms)
sink_index = [M[i]["alsapw_pactl_write_r84_probe"].get("sink_index")
              for i in (0, 1)]
vol25 = ["vol_25_idx" in (M[i]["alsapw_pactl_write_r84_probe"].get("legs")
                          or {}) for i in (0, 1)]
reset = [M[i]["alsapw_pactl_write_r84_probe"].get("reset_sink") for i in (0, 1)]
reset_end = [M[i]["alsapw_pactl_write_r84_probe"].get("reset_sink_end")
             for i in (0, 1)]
check("R8 pactl-write surfaces realized (index leg + reset leaves)",
      all(isinstance(s, int) and s > 0 for s in sink_index) and all(vol25) and
      all(r == [0, 0, 0, 0] for r in reset + reset_end),
      f"sink_index={sink_index} vol_25_idx={vol25} reset={reset} "
      f"reset_end={reset_end}")

# R9 — the four x0.125/x3.375/x0.015625 laws and the 221 pin, per run
def ratio(v):
    return round(v["post_amp"] / v["base_amp"], 4) if v.get("base_amp") else None


laws = {}
for i, tag in ((0, "run1"), (1, "run2")):
    L = M[i]["alsapw_pactl_write_r84_probe"]["legs"]
    mono = M[i]["alsapw_monstream_r84_probe"]["legs"]
    laws.setdefault("vol_50", {})[tag] = ratio(L["vol_50_0"])
    laws.setdefault("vol_150", {})[tag] = ratio(L["vol_150"])
    laws.setdefault("vol_25_idx", {})[tag] = ratio(L["vol_25_idx"])
    laws.setdefault("src_vol50", {})[tag] = ratio(L["src_vol50_0"])
    laws.setdefault("monA_sivol", {})[tag] = ratio(mono["monA_sivol_0"])
check("R9 encoded gain laws realized in both runs",
      all(abs(laws[k]["run1"] - laws[k]["run2"]) < 1e-9 for k in laws) and
      abs(laws["vol_50"]["run1"] - 0.125) < 0.02 and
      abs(laws["vol_150"]["run1"] - 3.375) < 0.05 and
      abs(laws["vol_25_idx"]["run1"] - 0.015625) < 0.004 and
      abs(laws["monA_sivol"]["run1"] - 0.125) < 0.02,
      f"{laws}")

out.append(f"\nTOTAL: {PASS} PASS / {FAIL} FAIL")
Path("proofs/receipt-census.txt").write_text("\n".join(out) + "\n")
print("\n".join(out))
sys.exit(1 if FAIL else 0)
