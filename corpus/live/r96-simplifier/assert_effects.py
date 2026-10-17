#!/usr/bin/env python3
"""r96 simplifier — intended-effect assertions per pair.

Usage: assert_effects.py BASE.json VARIANT.json --kind KIND [--json-out F]
Checks the specific expected effects of each fold and prints PASS/FAIL per
assertion.  Every assertion is on the RECEIPT (what a consumer sees).
"""
import argparse
import json
import sys

ENTRIES = ("pulsecli_avail_r96_probe", "pulsecli_target_r96_probe",
           "pulsecli_attr_r96_probe", "pulsecli_props_r96_probe",
           "pulsecli_cork_r96_probe")


def legs(r, entry):
    return ((r.get("measurements") or {}).get(entry) or {}).get("legs") or {}


def run_legs(r):
    out = []
    for e in ENTRIES:
        for k, v in legs(r, e).items():
            if isinstance(v, dict) and "error_hit" in v:
                out.append((e, k, v))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--kind", required=True)
    ap.add_argument("--json-out")
    args = ap.parse_args()
    A, B = json.load(open(args.a)), json.load(open(args.b))
    kind = args.kind
    res = []

    def chk(name, ok, detail=""):
        res.append({"check": name, "ok": bool(ok), "detail": str(detail)[:200]})

    la, lb = legs(A, "pulsecli_attr_r96_probe"), legs(B, "pulsecli_attr_r96_probe")
    if "c5" in kind:
        chk("C5 base has the duplicate pair",
            all(f"t_proc_lat_{s}__r{r}" in la
                for s in ("a", "b") for r in (1, 2)))
        chk("C5 folded drops only t_proc_lat_b",
            all(f"t_proc_lat_a__r{r}" in lb for r in (1, 2))
            and not any("t_proc_lat_b" in k for k in lb))
        # the duplicate pair is byte-equivalent as a REQUEST in base
        for r in (1, 2):
            a, b = la[f"t_proc_lat_a__r{r}"], la[f"t_proc_lat_b__r{r}"]
            chk(f"C5 base r{r}: argv byte-equal",
                a.get("argv") == b.get("argv"), a.get("argv"))
            chk(f"C5 base r{r}: env_keys equal",
                a.get("env_keys") == b.get("env_keys"))
            chk(f"C5 base r{r}: predicted equal",
                a.get("predicted") == b.get("predicted"))
            chk(f"C5 base r{r}: frame_size equal",
                a.get("frame_size") == b.get("frame_size"))
            chk(f"C5 base r{r}: measured attrs equal",
                a.get("attrs_after_resnapshot")
                == b.get("attrs_after_resnapshot"),
                f"{a.get('attrs_after_resnapshot')}")
        for r in (1, 2):
            chk(f"C5 folded r{r}: t_proc_lat_a predicted unchanged",
                lb[f"t_proc_lat_a__r{r}"].get("predicted")
                == la[f"t_proc_lat_a__r{r}"].get("predicted"))
            chk(f"C5 folded r{r}: t_proc_lat_a measured unchanged",
                lb[f"t_proc_lat_a__r{r}"].get("attrs_after_resnapshot")
                == la[f"t_proc_lat_a__r{r}"].get("attrs_after_resnapshot"))
        chk("C5 folded census 41/27/66/20/22",
            [len(legs(B, e)) for e in ENTRIES] == [41, 27, 66, 20, 22],
            [len(legs(B, e)) for e in ENTRIES])
        chk("C5 folded late_attr_census.legs == 64",
            ((B["measurements"]["pulsecli_attr_r96_probe"]
              .get("late_attr_census") or {}).get("legs")) == 64)
        chk("C5 base late_attr_census.legs == 66",
            ((A["measurements"]["pulsecli_attr_r96_probe"]
              .get("late_attr_census") or {}).get("legs")) == 66)
    if "c4rep" in kind:
        rl = run_legs(B)
        chk("C4rep: every _run-shaped leg records an int pid",
            rl and all(isinstance(v.get("pid"), int) and v["pid"] > 0
                       for _, _, v in rl),
            f"n={len(rl)}")
        chk("C4rep: base has no pid keys",
            not any("pid" in v for _, _, v in run_legs(A)))
        for r in (1, 2):
            a = legs(A, "pulsecli_attr_r96_probe").get(f"t_f32le_invalid__r{r}") or {}
            b = legs(B, "pulsecli_attr_r96_probe").get(f"t_f32le_invalid__r{r}") or {}
            chk(f"C4rep r{r}: t_f32le_invalid rc/class unchanged",
                (a.get("exit_code"), a.get("error_class"))
                == (b.get("exit_code"), b.get("error_class")),
                (b.get("exit_code"), b.get("error_class")))
            chk(f"C4rep r{r}: t_f32le_invalid row still None",
                b.get("row") is None and "row" in b)
        for r in (1, 2):
            a = legs(A, "pulsecli_props_r96_probe").get(f"p_malformed__r{r}") or {}
            b = legs(B, "pulsecli_props_r96_probe").get(f"p_malformed__r{r}") or {}
            chk(f"C4rep r{r}: p_malformed rc/class/failures unchanged",
                (a.get("exit_code"), a.get("error_class"), a.get("failures"))
                == (b.get("exit_code"), b.get("error_class"), b.get("failures")),
                (b.get("exit_code"), b.get("error_class"), b.get("failures")))
    if "c4del" in kind:
        for r in (1, 2):
            b = legs(B, "pulsecli_attr_r96_probe").get(f"t_f32le_invalid__r{r}") or {}
            a = legs(A, "pulsecli_attr_r96_probe").get(f"t_f32le_invalid__r{r}") or {}
            chk(f"C4del r{r}: t_f32le_invalid row key removed",
                "row" not in b and "row" in a and a.get("row") is None)
            chk(f"C4del r{r}: t_f32le_invalid rc/class unchanged",
                (a.get("exit_code"), a.get("error_class"))
                == (b.get("exit_code"), b.get("error_class")))
        for r in (1, 2):
            a = legs(A, "pulsecli_props_r96_probe").get(f"p_malformed__r{r}") or {}
            b = legs(B, "pulsecli_props_r96_probe").get(f"p_malformed__r{r}") or {}
            chk(f"C4del r{r}: p_malformed rc/class/failures unchanged",
                (a.get("exit_code"), a.get("error_class"), a.get("failures"))
                == (b.get("exit_code"), b.get("error_class"), b.get("failures")))
        chk("C4del: no pid keys anywhere",
            not any("pid" in v for _, _, v in run_legs(B)))
    bad = [r for r in res if not r["ok"]]
    for r in res:
        print(f"  {'PASS' if r['ok'] else 'FAIL'}  {r['check']}"
              + (f"  [{r['detail']}]" if not r["ok"] else ""))
    print(f"== {args.kind}: {len(res) - len(bad)}/{len(res)} assertions pass")
    if args.json_out:
        json.dump(res, open(args.json_out, "w"), indent=1)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
