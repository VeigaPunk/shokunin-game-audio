#!/usr/bin/env python3
"""r90 verifier — receipt forgery / mutation suite for the law set.

Each fabrication edits a COPY of a real receipt's recorded fields; the law set
is then re-derived and the fabrication must be CAUGHT (>=1 non-PASS law). Two
controls must be no-ops:
  * `none`             — no edit at all
  * `blank-verdicts`   — blank both verdict lists on a GREEN receipt (the
                         lists are not the detector; the fields are)

`silence-failures-on-red` runs against a RED receipt (a mutation battery's
receipt) with its `failures` list blanked: the derived FAILs must survive, so
silencing a verdict list cannot launder a red.

Usage:  python3 r90v_forge.py <green.json> <red.json> [out.json]
"""
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from r90v_laws import derive, summarize  # noqa: E402

M = "measurements"
STORE = "wpstate_store_r90_probe"
PMOD = "wpstate_pmod_r90_probe"
WLINK = "wplink_r90_probe"
WFORMAT = "wpformat_r90_probe"


def fabrications(base):
    """name -> (receipt, expectation) with expectation in {catch, noop}."""
    f = {}

    def add(name, fn, expect="catch"):
        r = copy.deepcopy(base)
        fn(r)
        f[name] = (r, expect)

    add("none", lambda r: None, "noop")
    add("blank-verdicts", lambda r: [e.update(failures=[], coverage_blocked=[])
                                     for e in r[M].values()], "noop")
    add("forge-settings-types",
        lambda r: r[M][STORE]["legs"]["w_settings"]["types"].update({"Integer": 2}))
    add("forge-settings-at-default",
        lambda r: r[M][STORE]["legs"]["w_settings"]["at_default"].pop())
    add("forge-settings-attempts",
        lambda r: r[M][STORE]["legs"]["w_settings"]["attempts"][-1].update(
            {"exit_code": -11, "entries": 0}))
    add("forge-meta-key-drop",
        lambda r: r[M][STORE]["legs"]["w_meta"]["objects"][1]["keys"].pop())
    add("forge-state-dir-settings-file",
        lambda r: r[M][STORE]["legs"]["w_state_dir"]["entries"].append("settings"))
    add("forge-cross-volume",
        lambda r: r[M][STORE]["legs"]["w_cross_volume"].update({"value": "Value: 0.5"}))
    add("forge-create-band",
        lambda r: r[M][STORE]["legs"]["w_create"].update({"t_row_s": 0.01}))
    add("forge-create-row-default",
        lambda r: r[M][STORE]["legs"]["w_create"]["row"].update(
            {"channelVolumes": [0.5, 0.5]}))
    add("forge-props-field-split",
        lambda r: r[M][STORE]["legs"]["w_props"]["row"].update(
            {"channelVolumes": [0.5, 0.5]}))
    add("forge-pulse-cmd-ms",
        lambda r: r[M][STORE]["legs"]["w_pulse"].update({"cmd_ms": 900}))
    add("forge-pulse-band",
        lambda r: r[M][STORE]["legs"]["w_pulse"].update({"t_change_s": 0.008}))
    add("forge-pulse-field-split",
        lambda r: r[M][STORE]["legs"]["w_pulse"]["row"].update({"volume": 0.5}))
    add("forge-target-band",
        lambda r: r[M][STORE]["legs"]["w_target"].update({"t_target_s": 5.0}))
    add("forge-replay-fields",
        lambda r: r[M][STORE]["legs"]["w_replay_fields"]["live"].update(
            {"channelVolumes": [1.0, 1.0]}))
    add("forge-explicit-swap",
        lambda r: r[M][STORE]["legs"]["w_explicit_target"].update(
            {"edges_in_explicit": [], "edges_in_stored":
                r[M][STORE]["legs"]["w_explicit_target"]["edges_in_explicit"]}))
    add("forge-vanish-outcome",
        lambda r: r[M][STORE]["legs"]["w_vanished_target"].update(
            {"outcome": "no_link"}))
    add("forge-optout-row",
        lambda r: r[M][STORE]["legs"]["w_optout_stream"].update({"row_present": True}))
    add("forge-phantom-mine",
        lambda r: r[M][PMOD]["legs"]["m_phantom"]["probes"][0].update({"mine": True}))
    add("forge-unassignable-rc",
        lambda r: r[M][PMOD]["legs"]["m_unassignable"]["cmd"].update({"exit_code": 0}))
    add("forge-byname-count",
        lambda r: r[M][PMOD]["legs"]["m_byname_control"]["after"].update({"count": 1}))
    add("forge-ids-count",
        lambda r: r[M][WLINK]["legs"]["k_ids"].update({"mine": r[M][WLINK]["legs"]["k_ids"]["mine"][:1]}))
    add("forge-dup-rc",
        lambda r: r[M][WLINK]["legs"]["k_dup"].update({"exit_code": 0}))
    add("forge-w-late-wall",
        lambda r: r[M][WLINK]["legs"]["k_w_late"].update({"wall_s": 0.2}))
    add("forge-passive-visible",
        lambda r: r[M][WLINK]["legs"]["k_p_passive"]["own_links"][0]["props"].update(
            {"link.passive": True}))
    add("forge-t-out-len",
        lambda r: r[M][WLINK]["legs"]["k_t"].update({"out_len": 12}))
    add("forge-sha-stream48",
        lambda r: r[M][WFORMAT]["legs"]["f_mid48"]["stream_format"].update(
            {"sha12": "000000000000"}))
    add("forge-echo-bytes",
        lambda r: r[M][WFORMAT]["legs"]["f_setparam_sink"]["cmd"].update(
            {"stdout_bytes": 600}))
    add("forge-sticky",
        lambda r: r[M][WFORMAT]["legs"]["f_post"]["node_format"].update(
            {"sha12": "000000000000"}))
    add("forge-unload-rc",
        lambda r: list(r[M][STORE]["unloads"].values())[0].update({"exit_code": 1}))
    add("forge-sinks-gone",
        lambda r: list(r[M][STORE]["sinks_gone"].keys()) and
        r[M][STORE]["sinks_gone"].update(
            {list(r[M][STORE]["sinks_gone"].keys())[0]: False}))
    add("pop-leg",
        lambda r: r[M][STORE]["legs"].pop("w_create"))
    add("pop-hygiene",
        lambda r: r[M][STORE].pop("own_modules_after"))
    return f


def main(argv):
    green_path, red_path = argv[1], argv[2]
    out = argv[3] if len(argv) > 3 else None
    green = json.loads(open(green_path).read())
    red = json.loads(open(red_path).read())
    rows = []
    for name, (r, expect) in fabrications(green).items():
        L = derive(r)
        s = summarize(L)
        caught = [x["law"] for x in L.rows if x["status"] != "PASS"]
        status = "CAUGHT" if caught else "no-op"
        ok = (status == "CAUGHT") == (expect == "catch")
        rows.append({"forge": name, "expect": expect, "result": status,
                     "ok": ok, "summary": s, "caught_by": caught[:6]})
        print(f"{'OK ' if ok else 'BAD'} {name:28s} {status:7s} "
              f"PASS={s['PASS']} FAIL={s['FAIL']} BLOCKED={s['BLOCKED']} "
              f"by={caught[:3]}")

    # Silencing control A: a FIELD-VISIBLE red with its verdict list blanked.
    # The law set derives reds from fields, so the red must survive.
    silenced_field = copy.deepcopy(green)
    silenced_field[M][STORE]["legs"]["w_create"].update({"t_row_s": 0.01})
    for e in silenced_field[M].values():
        e.update(failures=[], coverage_blocked=[])
    L = derive(silenced_field)
    s = summarize(L)
    caught = [x["law"] for x in L.rows if x["status"] == "FAIL"]
    rows.append({"forge": "silence-failures-on-field-red", "expect": "catch",
                 "result": "CAUGHT" if caught else "no-op", "ok": bool(caught),
                 "summary": s, "caught_by": caught[:6]})
    print(f"{'OK ' if caught else 'BAD'} {'silence-failures-on-field-red':32s} "
          f"{'CAUGHT' if caught else 'no-op':7s} PASS={s['PASS']} "
          f"FAIL={s['FAIL']} BLOCKED={s['BLOCKED']} by={caught[:3]}")

    # Silencing control B — the documented LIMIT: a MUTATED FIXTURE CONSTANT
    # (e.g. the armed echo byte count) leaves the recorded fields equal to the
    # shipped law set's expectations, so the red lives only in the verdict
    # list; blanking it is indistinguishable from green AT THE RECEIPT LEVEL.
    # No field-based law set can see the fixture's constant; the mutation gate
    # (the battery's own failure string) is the witness for that class.
    silenced_mut = copy.deepcopy(red)
    for e in silenced_mut[M].values():
        e.update(failures=[], coverage_blocked=[])
    L = derive(silenced_mut)
    s = summarize(L)
    caught = [x["law"] for x in L.rows if x["status"] != "PASS"]
    rows.append({"forge": "silence-failures-on-mutated-constant",
                 "expect": "limit", "result": "no-op" if not caught else "CAUGHT",
                 "ok": not caught, "summary": s, "caught_by": caught[:6]})
    print(f"LIM {'silence-failures-on-mutated-constant':32s} "
          f"{'no-op (limit)' if not caught else 'CAUGHT':7s} PASS={s['PASS']} "
          f"FAIL={s['FAIL']} BLOCKED={s['BLOCKED']}")

    bad = [r for r in rows if not r["ok"]]
    print(json.dumps({"forgeries": len(rows), "failures": len(bad),
                      "all_caught_as_expected": not bad}))
    if out:
        open(out, "w").write(json.dumps(
            {"green": green_path, "red": red_path, "rows": rows}, indent=2) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
