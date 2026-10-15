#!/usr/bin/env python3
"""r87b supplement 3 — fresh-session witnesses (async interleaving defense).

Under heavy registry churn, response lines from a single pw-cli session can be
swallowed by the async event stream. These legs use ONE fresh pw-cli session
per command so each response has a clean window:
  - send-command Suspend / Start / Pause + separate info witnesses
  - set-param Format on an UNLINKED (autoconnect=false) stream, witnessed by a
    fresh enum session (scout's unknown: pre-negotiation Format write)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87b_lib import (  # noqa: E402
    TAG, NS, TONE, RECEIPTS, RUNS, sh, pw_dump, nodes_by_name, spawn, stop,
    pw_cli, pwcli_errors)
from r87b_probe import parse_format  # noqa: E402,F401  (placeholder, replaced below)
from r87b_reparse import parse_format as _pf  # corrected parser


def fmt_of(log):
    return _pf(log)


def main():
    out = {}
    d = pw_dump()
    sink = nodes_by_name(NS, d)
    sid = sink[0]["id"] if sink else None
    # send-command matrix, one fresh session each
    for cmd in ("Suspend", "Start", "Pause"):
        r1 = pw_cli([(0, f"send-command {sid} {cmd} {{}}")], wait_s=6,
                    label=f"s3-sendcmd-{cmd}")
        r2 = pw_cli([(0, f"info {sid}")], wait_s=6, label=f"s3-info-after-{cmd}")
        states = [l.strip() for l in r2["log"].splitlines() if "state:" in l]
        out[cmd] = {"cmd_errors": pwcli_errors(r1["log"]),
                    "info_errors": pwcli_errors(r2["log"]),
                    "state_lines": states}
    r3 = pw_cli([(0, f"send-command {sid} Resume {{}}")], wait_s=6,
                label="s3-sendcmd-Resume")
    out["Resume"] = {"cmd_errors": pwcli_errors(r3["log"])}
    # unlinked-stream Format write, fresh sessions
    pp = spawn(["pw-play", "-P", f"node.name={TAG}s3_fmtu",
                "-P", "node.autoconnect=false", "--target", "0", str(TONE)])
    time.sleep(1.2)
    d = pw_dump()
    nds = nodes_by_name(TAG + "s3_fmtu", d)
    uid = nds[0]["id"] if nds else None
    out["unlinked_stream_id"] = uid
    if uid is not None:
        a = pw_cli([(0, f"enum-params {uid} Format")], wait_s=6,
                   label="s3-fmtu-enum-before")
        b = pw_cli([(0, f"set-param {uid} Format {{ mediaType: 1, mediaSubtype: 1,"
                       " format: 259, rate: 96000, channels: 2 }}")],
                   wait_s=6, label="s3-fmtu-set")
        time.sleep(1.0)
        c = pw_cli([(0, f"enum-params {uid} Format")], wait_s=6,
                   label="s3-fmtu-enum-after")
        out["unlinked_fmt"] = {
            "before": {"errors": pwcli_errors(a["log"]), "fmt": fmt_of(a["log"])},
            "set": {"errors": pwcli_errors(b["log"]), "fmt": fmt_of(b["log"])},
            "after": {"errors": pwcli_errors(c["log"]), "fmt": fmt_of(c["log"])},
            "links": sh(["pw-link", "-l"])["out"].count(TAG + "s3_fmtu"),
        }
    rc, err = stop(pp)
    out["unlinked_play_rc"] = rc
    (RECEIPTS / "b3z-fresh-sessions.json").write_text(
        json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
