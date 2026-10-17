#!/usr/bin/env python3
"""r77 verifier — independent re-derivation of the pw-record format axis
(claim 6): every legal --format/--rate/--channels is honored and reported
back verbatim; every illegal request is a pre-capture `usage_refusal` at
rc=1 that leaves NO FILE AT ALL.

Byte discipline: `-n 4800` frames (0.1 s) — 19-77 KB per leg, all < 16 MB.
"""
import importlib.util
import json
import subprocess
import tempfile
import time
from pathlib import Path

_here = Path(__file__).with_name("v1_lattice.py")
_spec = importlib.util.spec_from_file_location("v1", _here)
v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(v1)

OUT = v1.OUT
FRAMES = 4800
LEGAL = (
    ("baseline", (), {"tag": 1, "channels": 2, "rate": 48000, "bits": 16}),
    ("s24", ("--format", "s24"), {"tag": 1, "bits": 24}),
    ("f32", ("--format", "f32"), {"tag": 3, "bits": 32}),
    ("u8", ("--format", "u8"), {"tag": 1, "bits": 8}),
    ("rate_192000", ("--rate", "192000"), {"rate": 192000}),
    ("channels_1", ("--channels", "1"), {"channels": 1}),
    ("channels_6", ("--channels", "6"), {"channels": 6, "tag": 65534}),
)
REFUSALS = (
    ("format_bogus", ("--format", "bogus")),
    ("rate_0", ("--rate", "0")),
    ("channels_0", ("--channels", "0")),
    ("channel_map_mismatch", ("--channels", "1", "--channel-map", "FL,FR")),
)


def run(argv, out):
    p = subprocess.run(argv + [str(out)], capture_output=True, text=True,
                       timeout=30)
    rec = {"argv": " ".join(argv) + " <out>", "exit_code": p.returncode,
           "stderr": p.stderr.strip().splitlines()[:3],
           "usage_dump": "pw-record [options]" in p.stderr}
    rec["file"] = v1.pcm(out)
    return rec


def main():
    src = next((s for s in v1.source_names() if not s.endswith(".monitor")),
               None)
    tgt = src or v1.default_sink()
    entry = {"probe": "r77-verifier pw-record format axis", "target": tgt,
             "frames": FRAMES, "legs": {}, "failures": []}
    if not tgt:
        entry["blocked"] = "no pw-record target"
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "v5_format.json").write_text(json.dumps(entry, indent=2) + "\n")
        print(json.dumps({"receipt": str(OUT / "v5_format.json"),
                          "failures": entry["failures"]}))
        return
    with tempfile.TemporaryDirectory(prefix="r77v-format-") as tmp:
        for name, extra, expect in LEGAL:
            leg = run(["pw-record", "--target", tgt, "-n", str(FRAMES),
                       "--rate", "48000", "--channels", "2", "--format",
                       "s16", *extra], Path(tmp) / f"l_{name}.wav")
            leg["requested"] = list(extra)
            leg["expected_fmt"] = expect
            entry["legs"][name] = leg
            time.sleep(0.4)
        for name, extra in REFUSALS:
            leg = run(["pw-record", "--target", tgt, "-n", str(FRAMES),
                       *extra], Path(tmp) / f"r_{name}.wav")
            leg["requested"] = list(extra)
            entry["legs"][name] = leg
    f = entry["failures"]
    for name, extra, expect in LEGAL:
        leg = entry["legs"][name]
        if leg["exit_code"] != 1:
            f.append(f"{name}: expected rc=1 (bounded capture), got "
                     f"{leg['exit_code']}")
        fin = leg["file"]
        if not fin.get("exists") or not fin.get("bytes"):
            f.append(f"{name}: expected a written file, got {fin}")
            continue
        got = fin.get("fmt") or {}
        for key, want in expect.items():
            if got.get(key) != want:
                f.append(f"{name}: fmt.{key} expected {want}, got "
                         f"{got.get(key)}")
        if fin.get("data_declared") != FRAMES * got.get("channels", 0) * \
                (got.get("bits", 0) // 8):
            f.append(f"{name}: header not finalized to truth "
                     f"({fin.get('data_declared')})")
    if entry["legs"]["baseline"]["file"].get("bytes") != 19244:
        f.append("baseline: expected exactly 44 + 4800 x 4 = 19244 B, got "
                 f"{entry['legs']['baseline']['file'].get('bytes')}")
    for name, extra in REFUSALS:
        leg = entry["legs"][name]
        if not leg["usage_dump"]:
            f.append(f"{name}: expected the pw-record usage dump on stderr")
        if leg["file"].get("exists") is not False:
            f.append(f"{name}: a refused argument must leave NO file at all "
                     f"(got {leg['file']})")
    entry["refusal_class"] = "usage_refusal"
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v5_format.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v5_format.json"),
                      "failures": entry["failures"]}))


if __name__ == "__main__":
    main()
