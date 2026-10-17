#!/usr/bin/env python3
"""r97 verifier single-entry driver: import the fixture module and run ONE
entry function (bounded mutation/negative control — the family's own CLI runs
all five entries plus the base analysis set).

    python3 r97v_entry.py <fixture.py> <entry_fn> <out.json>
"""
import importlib.util
import json
import sys
from pathlib import Path


def main():
    fixture, entry, out = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = importlib.util.spec_from_file_location("ma_r97v", fixture)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, entry)
    rec = fn()
    Path(out).write_text(json.dumps({"measurements": {entry: rec}}, indent=1))
    print(json.dumps({"entry": entry,
                      "failures": rec.get("failures", []),
                      "blocked": rec.get("coverage_blocked", []),
                      "keys": len(rec)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
