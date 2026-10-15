#!/usr/bin/env python3
"""r87b reparse — recover Format/Props values from saved raw pw-cli logs.

The in-run parser missed `Format:Audio:rate` (it searched for a non-existent
`Props:Format:` key). This script re-reads the raw .pwcli logs written by the
harness and extracts, per command, the negotiated rate/format id + Props
volume, using a corrected splitter (verb followed by whitespace; response
body lines such as `permissions: rwxm-` are not treated as commands).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUNS = ROOT / "runs"
RECEIPTS = ROOT / "receipts"

CMD_RE = re.compile(
    r"^\s*(?:pipewire-0>>\s*)?"
    r"(info|enum-params|set-param|send-command|destroy|create-node|create-device|"
    r"get-permissions|list-remotes|load-module|connect|quit)(?:\s|$)")


def split_log(log):
    out = []
    cur, seg = None, []
    for line in log.splitlines():
        m = CMD_RE.match(line)
        if m:
            if cur is not None:
                out.append((cur, "\n".join(seg)))
            cur = line.strip()
            seg = []
        else:
            if cur is not None:
                seg.append(line)
    if cur is not None:
        out.append((cur, "\n".join(seg)))
    return out


def parse_format(seg):
    rate = fmt = None
    m = re.search(r"Format:Audio:rate \(65539\)(.*?)(?=\n\s*Prop:|\Z)", seg, re.S)
    if m:
        mm = re.search(r"\bInt (\d+)", m.group(1))
        rate = int(mm.group(1)) if mm else None
    m2 = re.search(r"Format:Audio:format \(65537\)(.*?)(?=\n\s*Prop:|\Z)", seg, re.S)
    if m2:
        mm = re.search(r"\bId (\d+)", m2.group(1))
        fmt = int(mm.group(1)) if mm else None
    return {"rate": rate, "format_id": fmt}


def parse_volume(seg):
    m = re.search(r"Props:volume \(65539\)(.*?)(?=\n\s*Prop:|\Z)", seg, re.S)
    if not m:
        return None
    mm = re.search(r"\bFloat ([0-9.]+)", m.group(1))
    return float(mm.group(1)) if mm else None


def parse_state(seg):
    return re.findall(r'state: "([a-z]+)"', seg)


def analyze(path):
    log = Path(path).read_text(errors="replace")
    rows = []
    for cmd, seg in split_log(log):
        row = {"cmd": cmd}
        if cmd.startswith("enum-params") and "Format" in cmd:
            row.update(parse_format(seg))
        elif cmd.startswith("set-param") and "Format" in cmd:
            row.update(parse_format(seg))
        elif cmd.startswith("enum-params") and "Props" in cmd:
            row["volume"] = parse_volume(seg)
        elif cmd.startswith("set-param") and "Props" in cmd:
            row["volume"] = parse_volume(seg)
        elif cmd.startswith("send-command"):
            row["states"] = parse_state(seg)
        elif cmd.startswith("info"):
            row["states"] = parse_state(seg)
        rows.append(row)
    return rows


def main():
    out = {}
    for name in sys.argv[1:]:
        p = RUNS / (name + ".pwcli")
        if p.exists():
            out[name] = analyze(p)
    (RECEIPTS / "reparse.json").write_text(json.dumps(out, indent=1))
    for name, rows in out.items():
        print("=" * 12, name)
        for r in rows:
            if "rate" in r or "volume" in r or "states" in r:
                print(" ", r)


if __name__ == "__main__":
    main()
