#!/usr/bin/env python3
"""r87b supplement 2 — confirm the node.target-vs---target precedence split.

Scout §1.2 inferred: target.object > node.target > --target flag.
Seat b1x measured: --target NS beat -P node.target=NS2 (flag > node.target).
This script runs the reverse + three-way + garbage-flag legs to pin it.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87b_lib import TAG, NS, NS2, TONE, RECEIPTS, play_leg  # noqa: E402


def main():
    out = {}
    legs = [
        ("y_nt_rev", ["pw-play", "-P", f"node.name={TAG}y_ntrev",
                      "-P", f"node.target={NS}",
                      "--target", NS2, str(TONE)], None),
        ("y_three", ["pw-play", "-P", f"node.name={TAG}y_three",
                     "-P", f"target.object={NS2}",
                     "-P", f"node.target={NS}",
                     "--target", NS, str(TONE)], None),
        ("y_nt_only", ["pw-play", "-P", f"node.name={TAG}y_ntonly",
                       "-P", f"node.target={NS2}", str(TONE)], None),
        ("y_flag_only", ["pw-play", "-P", f"node.name={TAG}y_flagonly",
                         "--target", NS2, str(TONE)], None),
        ("y_garbage_flag_nt", ["pw-play", "-P", f"node.name={TAG}y_garbnt",
                               "-P", f"node.target={NS2}",
                               "--target", "r87b_no_such_target", str(TONE)], None),
        ("y_tobj_vs_flag", ["pw-play", "-P", f"node.name={TAG}y_tobj",
                            "-P", f"target.object={NS2}",
                            "--target", NS, str(TONE)], None),
    ]
    for leg, args, env in legs:
        nm = [a.split("=", 1)[1] for a in args if a.startswith("node.name=")][0]
        out[leg] = play_leg(nm, args, env=env, observe_s=(1.0, 1.6))
    (RECEIPTS / "b1y-supplement2.json").write_text(
        json.dumps(out, indent=1, default=str))
    for k, v in out.items():
        snap = v["snaps"][-1]
        links = {p: sorted(set(x for x in peers))
                 for p, peers in snap["links"].items()}
        print(k, "rc", v["rc"], "links", json.dumps(links))


if __name__ == "__main__":
    main()
