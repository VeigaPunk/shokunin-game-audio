#!/usr/bin/env python3
"""r77 CRITIC — prior-row stability check for --probe-capture-r76.

Compares a fresh replay against the two committed post/pre-edit r76
receipts. Two comparison modes:
  * STRUCTURAL  — every pinned field the gate itself asserts
                  (exit_code, error_class, early_exit_code, out_kind,
                  file.data_finalized, data_declared_field, blocked,
                  cap_honored, viability booleans, argv, file bytes when
                  the leg is bounded-and-exact).
  * EXACT       — full leaf walk, used only for the fields whose value is
                  deterministic (the bounded legs); time-dependent
                  (sever) byte counts are reported separately.
"""
import json
import sys
from pathlib import Path

STRUCT = (
    "exit_code", "error_class", "early_exit_code", "blocked", "out_kind",
    "cap_honored", "device", "signal", "sever_after_s", "argv",
    "file_zero_bytes", "riff_size_field", "data_declared_field",
    "data_finalized", "data_actual_zero", "data_64k_aligned",
    "data_256k_aligned", "fmt", "parsers", "bytes", "exists",
    "content_magic", "detect_class", "kind", "detect", "blockage",
    "arecord_term_blockage", "arecord_kill_blockage",
)

VOLATILE = ("wall", "wall_s", "wall_lt_0_5s", "wall_lt_0.5s", "seconds",
            "rate_bps", "duration_s", "error", "stderr_tail", "peak",
            "rms", "sha256", "elapsed")


def walk(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}" if path else k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")
    else:
        yield path, node


def main(fresh, priors):
    fresh_d = json.loads(Path(fresh).read_text())
    fresh_m = {k: v for k, v in fresh_d["measurements"].items()
               if k.endswith("r76_probe")}
    print(f"fresh mode: {fresh_d.get('mode')}  entries: {sorted(fresh_m)}")
    for prior in priors:
        p_d = json.loads(Path(prior).read_text())
        p_m = {k: v for k, v in p_d["measurements"].items()
               if k.endswith("r76_probe")}
        print(f"\n=== vs {Path(prior).parent.name} (mode={p_d.get('mode')}) ===")
        for entry in sorted(fresh_m):
            f_leaves = dict(walk(fresh_m[entry]))
            p_leaves = dict(walk(p_m.get(entry, {})))
            keys = sorted(set(f_leaves) | set(p_leaves))
            drift = []
            for k in keys:
                if any(v in k for v in VOLATILE):
                    continue
                fv, pv = f_leaves.get(k, "<absent>"), p_leaves.get(k, "<absent>")
                if fv != pv:
                    drift.append((k, pv, fv))
            print(f"  {entry}: {len(drift)} structural drifts "
                  f"({len(keys)} leaves)")
            for k, pv, fv in drift[:24]:
                print(f"      {k}: prior={pv!r} fresh={fv!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
