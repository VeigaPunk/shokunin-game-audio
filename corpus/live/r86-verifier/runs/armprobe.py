#!/usr/bin/env python3
"""r86-verifier executed arm probe (verifier-owned).

Extracts the COMMITTED verdict slices for the three caveat legs verbatim by
anchor from the frozen-tree fixture and execs them against synthetic `legs`
dicts (mutation-style unit probe of the verdict logic; no live audio):

  dump_color_eq  record-only (armed False) — every realization must pass
  d_route        record-only (armed False) — every realization must pass
  n_format       armed rc-only — pod presence either-way; rc!=0 must fail
"""
import json
import re
import sys
import textwrap
from pathlib import Path

TREE = Path(sys.argv[1]).resolve()
src = (TREE / "corpus" / "fixtures" / "measure_audio.py").read_text()


def extract(pat):
    m = re.search(pat, src, re.M)
    if not m:
        raise SystemExit(f"anchor not found: {pat[:60]}")
    return m.group(0)


def extract_block(first, last):
    lines = src.splitlines(keepends=True)
    i = next(i for i, ln in enumerate(lines) if ln.rstrip("\n") == first)
    j = next(j for j in range(i, len(lines)) if lines[j].rstrip("\n") == last)
    return "".join(lines[i:j + 1])


slices = {
    "dump_color_eq": extract(
        r'^    legs\["dump_color_eq"\]\["armed"\] = False[^\n]*$'),
    "d_route": extract(
        r'^    legs\["d_route"\]\["armed"\] = False[^\n]*$'),
    "n_format": extract_block('    l = legs["n_format"]',
                              '    legs["n_format"]["armed"] = "rc_only"'),
}

# Anchor sanity: each caveat leg is referenced nowhere else in a failure path.
counts = {k: src.count(f'legs["{k}"]') for k in slices}
out = {"slice_shas": {}, "ref_counts": counts, "cases": []}
import hashlib
for k, v in slices.items():
    out["slice_shas"][k] = hashlib.sha256(v.encode()).hexdigest()[:16]


def run_case(leg_name, leg, slice_key):
    ns = {"legs": {leg_name: leg}, "failures": []}
    exec(textwrap.dedent(slices[slice_key]), ns)
    return {"leg": leg_name, "case": dict(leg), "failures": ns["failures"],
            "armed": ns["legs"][leg_name].get("armed")}


# ---- dump_color_eq: record-only, all three realizations must pass ----
for tag, leg in (("observed_rc255_unknown_color",
                  {"exit_code": 255, "stdout_bytes": 0, "stderr": "Unknown color: =never"}),
                 ("boundary_boot_rc0_0B",
                  {"exit_code": 0, "stdout_bytes": 0, "stderr": ""}),
                 ("hypothetical_rc0_full_dump",
                  {"exit_code": 0, "stdout_bytes": 245396, "stderr": ""})):
    c = run_case("dump_color_eq", leg, "dump_color_eq")
    c["expect_failures"] = 0
    out["cases"].append(c)

# ---- d_route: record-only, both realizations must pass ----
for tag, leg in (("silent_0B_rc0", {"exit_code": 0, "stdout_bytes": 0}),
                 ("dump_pod_rc0", {"exit_code": 0, "stdout_bytes": 512, "has_pod": True})):
    c = run_case("d_route", leg, "d_route")
    c["expect_failures"] = 0
    out["cases"].append(c)

# ---- n_format: rc-only either-way ----
for tag, leg, exp in (("pod_present_rc0", {"exit_code": 0, "has_pod": True}, 0),
                      ("pod_absent_rc0", {"exit_code": 0, "has_pod": False}, 0),
                      ("hostile_rc1", {"exit_code": 1, "has_pod": False}, 1)):
    c = run_case("n_format", leg, "n_format")
    c["expect_failures"] = exp
    out["cases"].append(c)

ok = True
for c in out["cases"]:
    good = (len(c["failures"]) == c["expect_failures"])
    if c["leg"] == "n_format":
        good = good and c["armed"] == "rc_only"
    else:
        good = good and c["armed"] is False
    c["ok"] = bool(good)
    ok = ok and c["ok"]
out["verdict"] = "SUSTAINED" if ok else "FALSIFIED"
print(json.dumps(out, indent=1))
sys.exit(0 if ok else 1)
