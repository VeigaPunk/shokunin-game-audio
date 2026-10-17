#!/usr/bin/env python3
"""r97 verifier forgery suite: mutate a recorded receipt and check that the
independent law set (r97v_laws.py) catches the fabrication.

    python3 r97v_forge.py --base <green-receipt.json> \
        --cross-root <frozen-tree/corpus/live> --out <json>

Each case deep-copies the base receipt, applies one fabrication, evaluates the
law set over it, and records the derived FAIL/BLOCKED counts.  A case is
CAUGHT when the derived FAIL count grows or the case turns BLOCKED (never
green); the no-op controls must stay at the base's 0 FAIL / 0 BLOCKED.
"""
import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_laws():
    spec = importlib.util.spec_from_file_location(
        "r97v_laws", HERE / "r97v_laws.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def evaluate(L, m, ctx):
    R = L.Res()
    for name in L.ENTRIES:
        if name in m:
            fn = {"wppol_arming_r97_probe": L.laws_arming,
                  "wppol_defaults_r97_probe": L.laws_defaults,
                  "wppol_linking_r97_probe": L.laws_linking,
                  "wppol_wpexec_r97_probe": L.laws_wpexec,
                  "wppol_settings_r97_probe": L.laws_settings}[name]
            fn(m[name], R, ctx)
    L.laws_global(m, R)
    n = {s: sum(1 for _, st, _ in R.rows if st == s)
         for s in ("PASS", "FAIL", "BLOCKED")}
    return n, R


def case(name, m, mutate):
    mm = copy.deepcopy(m)
    note = mutate(mm)
    return name, mm, note


def build_cases(m):
    E = m
    A = E["wppol_arming_r97_probe"]
    D = E["wppol_defaults_r97_probe"]
    LK = E["wppol_linking_r97_probe"]
    W = E["wppol_wpexec_r97_probe"]
    S = E["wppol_settings_r97_probe"]
    SINK = lambda s: [k for k in A["conf_paths"].values()]  # noqa: E731
    pid = A["contention"]["own_pid"]

    def sink(tag):
        return f"r97a_{tag}_{pid}"

    cases = []
    cases.append(case("none-control", m, lambda x: "no mutation"))
    cases.append(case("blank-failures-control", m,
                      lambda x: [x[n].__setitem__("failures", [])
                                 for n in E] and "verdict lists blanked"))
    cases.append(case("forge-a3-rc", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a3_conf_dir_missing"].__setitem__("rc", 0)))
    cases.append(case("forge-a2-rc", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a2_status_wp_down"].__setitem__("rc", 1)))
    cases.append(case("forge-a7-mark", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a7_data_dir_replaces"]["scan"]["marks"].__setitem__(
                              "Could not locate script 'sm-objects.lua'",
                              False)))
    cases.append(case("forge-a8-alive", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a8_core_no_modules"].__setitem__(
                              "alive_after_1s", False)))
    cases.append(case("forge-a10-hang", m,
                      lambda x: x["wppol_arming_r97_probe"]["a10_access_off"][
                          "pw_dump"].__setitem__("timed_out", False)))
    cases.append(case("forge-a11-client", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a11_access_on"].__setitem__("has_client", False)))
    cases.append(case("forge-a12-hits", m,
                      lambda x: x["wppol_arming_r97_probe"][
                          "a12_shared_untouched"].__setitem__(
                              "own_hits", ["r97a_sa_1"])))
    cases.append(case("forge-d1-got", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d1_first_sink_wins"].__setitem__(
                              "got", sink("sb"))))
    cases.append(case("forge-d7-got", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d7_driver_fallback_takes"].__setitem__(
                              "got", sink("sk"))))
    cases.append(case("forge-d9-configured", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d9_explicit_beats_priority"]["metadata_rows"]
                      .__setitem__("default.configured.audio.sink", None)))
    cases.append(case("forge-d9-state", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d9_explicit_beats_priority"].__setitem__(
                              "state_file", "")))
    cases.append(case("forge-d10-configured", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d10_clear_default"].__setitem__(
                              "configured_after", sink("sc"))))
    cases.append(case("forge-d12-flush", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d12_restart_race_lost"].__setitem__(
                              "flushed_before_restart", True)))
    cases.append(case("forge-d12-default", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d12_restart_race_lost"].__setitem__(
                              "default_after", sink("sp"))))
    cases.append(case("forge-d13-state", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "d13_restart_durable"].__setitem__(
                              "state_file_row", None)))
    cases.append(case("forge-l1-links", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l1_auto_default"].__setitem__("links", [])))
    cases.append(case("forge-l4-target", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l4_target_global_id"].__setitem__(
                              "links", [[f"r97a_str_{pid}", sink("sa")]])))
    cases.append(case("forge-l6-stderr", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l6_bogus_falls_back"].__setitem__(
                              "stderr", "boom\n")))
    cases.append(case("forge-l7-gone", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l7_node_gone"].__setitem__("gone", False)))
    cases.append(case("forge-l8-alive", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l8_linger_waits"].__setitem__("alive_at_cap",
                                                         False)))
    cases.append(case("forge-l18-row", m,
                      lambda x: x["wppol_linking_r97_probe"][
                          "l18_follow_default_recorded"].__setitem__(
                              "sm_settings_row_after", True)))
    cases.append(case("forge-w1-found", m,
                      lambda x: x["wppol_wpexec_r97_probe"][
                          "w1_inventory"]["lines"].__setitem__(
                              0, "FOUND Core=table")))
    cases.append(case("forge-w2-rc", m,
                      lambda x: x["wppol_wpexec_r97_probe"][
                          "w2_compile_error_located"].__setitem__("rc", 0)))
    cases.append(case("forge-w7-timeout", m,
                      lambda x: x["wppol_wpexec_r97_probe"][
                          "w7_no_quit"].__setitem__("timed_out", False)))
    cases.append(case("forge-w13-identical", m,
                      lambda x: x["wppol_wpexec_r97_probe"][
                          "w13_settings_unbound"].__setitem__(
                              "identical", False)))
    cases.append(case("forge-w14-inventory", m,
                      lambda x: x["wppol_wpexec_r97_probe"][
                          "w14_sandbox_without_daemon"].__setitem__(
                              "inventory_identical", False)))
    cases.append(case("forge-s1-nkeys", m,
                      lambda x: x["wppol_settings_r97_probe"][
                          "s1_lattice"].__setitem__("n_keys", 24)))
    cases.append(case("forge-s1-sha", m,
                      lambda x: x["wppol_settings_r97_probe"][
                          "s1_lattice"].__setitem__(
                              "sha256", "deadbeef" * 8)))
    cases.append(case("forge-s2-rows", m,
                      lambda x: x["wppol_settings_r97_probe"][
                          "s2_metadata_faces"]["sm-settings"].__setitem__(
                              "rows", 24)))
    cases.append(case("forge-s3-shared", m,
                      lambda x: x["wppol_settings_r97_probe"][
                          "s3_write_scope"].__setitem__(
                              "shared_after", "Value: false\n")))
    cases.append(case("forge-s4-samekeys", m,
                      lambda x: x["wppol_settings_r97_probe"][
                          "s4_shared_lattice"].__setitem__(
                              "same_key_set", False)))
    cases.append(case("pop-leg-l3", m,
                      lambda x: x["wppol_linking_r97_probe"].pop(
                          "l3_target_serial", None)))
    cases.append(case("pop-hygiene-own-procs", m,
                      lambda x: x["wppol_settings_r97_probe"].pop(
                          "own_procs_after", None)))
    cases.append(case("forge-pid-suffix", m,
                      lambda x: x["wppol_defaults_r97_probe"][
                          "own_nodes_before_teardown"][0].__setitem__(
                              1, "r97a_sq_1")))
    cases.append(case("forge-coverage-block", m,
                      lambda x: x["wppol_settings_r97_probe"].__setitem__(
                          "coverage_blocked", ["injected"])))
    cases.append(case("forge-pactl", m,
                      lambda x: x["wppol_settings_r97_probe"].__setitem__(
                          "note", "pactl set-default-sink was used")))
    return cases


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--cross-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    L = load_laws()
    ctx = L.load_cross(Path(args.cross_root))
    receipt = json.loads(Path(args.base).read_text())
    m = receipt["measurements"]
    base_n, base_R = evaluate(L, m, ctx)
    rows = []
    print(f"base: PASS={base_n['PASS']} FAIL={base_n['FAIL']} "
          f"BLOCKED={base_n['BLOCKED']}")
    for name, mm, note in build_cases(m):
        n, R = evaluate(L, mm, ctx)
        if name.endswith("control"):
            verdict = "CONTROL-OK" if n["FAIL"] == base_n["FAIL"] and \
                n["BLOCKED"] == base_n["BLOCKED"] else "CONTROL-TRIPPED"
        elif n["FAIL"] > base_n["FAIL"]:
            verdict = "CAUGHT-FAIL"
        elif n["BLOCKED"] > base_n["BLOCKED"]:
            verdict = "CAUGHT-BLOCKED"
        else:
            verdict = "MISSED"
        fails = [r[0] for r in R.rows if r[1] == "FAIL"
                 and r[0] not in [q[0] for q in base_R.rows if q[1] == "FAIL"]]
        rows.append({"case": name, "note": note, "PASS": n["PASS"],
                     "FAIL": n["FAIL"], "BLOCKED": n["BLOCKED"],
                     "verdict": verdict, "new_fails": fails[:6]})
        print(f"{verdict:15s} {name:28s} FAIL={n['FAIL']:3d} "
              f"BLOCKED={n['BLOCKED']:3d} {fails[:3]}")
    Path(args.out).write_text(json.dumps(
        {"base": args.base, "base_summary": base_n, "cases": rows},
        indent=1))
    missed = [r["case"] for r in rows
              if r["verdict"] in ("MISSED", "CONTROL-TRIPPED")]
    print("MISSED/CONTROL-TRIPPED:", missed if missed else "none")
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
