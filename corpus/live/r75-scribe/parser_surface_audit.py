#!/usr/bin/env python3
"""r75 scribe — raw-stream vs production-parse-path audit (read-only).

Inputs: the RAW stderr/stdout captured by raw_surface.sh / raw_surface2.sh on
this host (real paplay/aplay/ffplay invocations, scribe scratch only) plus the
PRODUCTION parse helpers of corpus/fixtures/measure_audio.py as imported
(blob e3ef52e1e02c742d4f6dabda5c8658cc8f80a0bb).

Question: if the r75 consumer legs reuse the r73-era helper layer, what does
that layer see on the NEW consumers' raw surfaces?  Findings are capability
demonstrations on real raw streams; they are NOT product claims and NOT
measurements (no receipt is written, no probe mode runs).

Run with `python3 -B` (no bytecode write).
"""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
RAW = ROOT / "corpus/live/r75-scribe/raw"
FIX = ROOT / "corpus/fixtures/measure_audio.py"

spec = importlib.util.spec_from_file_location("measure_audio", FIX)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

out = {"fixture_sha256": hashlib.sha256(FIX.read_bytes()).hexdigest(),
       "cases": {}}
print("fixture sha256:", out["fixture_sha256"][:16])
print("helpers:", hasattr(ma, "_consumer_tail"), hasattr(ma, "_pwcat_fields"))
print("fixture has ffplay/paplay/aplay refs:",
      {n: FIX.read_text().count(n) for n in ("ffplay", "paplay", "aplay")})


def case(name, path, fn):
    p = RAW / path
    if not p.exists():
        out["cases"][name] = {"path": path, "MISSING": True}
        print(f"  {name}: MISSING {path}")
        return
    text = p.read_text(errors="replace")
    r = fn(text)
    out["cases"][name] = {"path": path, "bytes": len(text),
                          "result": r if not isinstance(r, tuple) else list(r),
                          "tail_repr": None}
    if name.startswith("tail"):
        out["cases"][name]["tail_repr"] = repr(r)[:200]
    print(f"  {name}: {r!r}"[:220])


# 1. production tail helper on the three ffplay raw surfaces
case("tail_ffplay_valid", "ffplay-file.stderr",
     lambda t: ma._consumer_tail(t, RAW / "silence.wav"))
case("tail_ffplay_invalid", "ffplay-noise.stderr",
     lambda t: ma._consumer_tail(t, RAW / "noise.wav"))
case("tail_ffplay_bogusdrv", "ffplay-bogusdrv.stderr",
     lambda t: ma._consumer_tail(t, RAW / "silence.wav"))
case("tail_paplay_invalid", "paplay-noise.stderr",
     lambda t: ma._consumer_tail(t, RAW / "noise.wav"))
case("tail_aplay_invalid_verbose", "aplay-noise2.stderr",
     lambda t: ma._consumer_tail(t, RAW / "noise.wav"))
case("tail_aplay_valid", "aplay-valid.stderr",
     lambda t: ma._consumer_tail(t, RAW / "silence.wav"))

# 2. the pw-cat field extractor applied to the NEW consumers' surfaces
case("pwcatfields_paplay_invalid", "paplay-noise.stderr",
     ma._pwcat_fields)
case("pwcatfields_aplay_invalid", "aplay-noise2.stderr",
     ma._pwcat_fields)
case("pwcatfields_ffplay_invalid", "ffplay-noise.stderr",
     ma._pwcat_fields)

# 3. line-structure hazards: CR/ESC interleaving in ffplay stderr
ff = (RAW / "ffplay-file.stderr").read_text(errors="replace")
lines = ff.splitlines()
info_lines = [i for i, ln in enumerate(lines) if "Input #0" in ln]
out["cr_esc"] = {
    "splitlines_count": len(lines),
    "lines_with_input_tag": info_lines,
    "input_line_is_line_initial": [
        lines[i].lstrip().startswith("Input #0") for i in info_lines],
    "line_with_input_head": repr(lines[info_lines[0]])[:160] if info_lines else None,
    "escape_bytes": ff.count("\x1b[2K"),
    "cr_bytes": ff.count("\r"),
}
print("  CR/ESC:", json.dumps(out["cr_esc"], indent=1)[:600])

# 4. repeated-run determinism of the ffplay tail (two real runs of the same cmd)
t1 = ma._consumer_tail((RAW / "ffplay-file.stderr").read_text(errors="replace"),
                       RAW / "silence.wav")
t2 = ma._consumer_tail((RAW / "ffplay-noise2.stderr").read_text(errors="replace"),
                       RAW / "noise.wav")
out["tail_pair"] = {"valid_run": t1, "invalid_run": t2,
                    "equal": t1 == t2}
print("  tail pair equal:", t1 == t2, "|", repr(t1)[:90], "|", repr(t2)[:90])

# 5. hex-value class in the new raw surfaces (feeds the ASLR/path scan noise)
hexes = sorted(set(re.findall(r"0x[0-9a-fA-F]+", ff)))
out["hex_tokens_in_ffplay_log"] = hexes
print("  hex tokens in ffplay log:", hexes)

# 6. path echo in the new surfaces (byte-stability hazard)
for f in ("ffplay-noise.stderr", "ffplay-file.stderr", "paplay-noise.stderr"):
    t = (RAW / f).read_text(errors="replace")
    hits = re.findall(r"[^\s']*corpus/live/r75-scribe/raw/[^\s':]*", t)
    out.setdefault("path_echo", {})[f] = sorted(set(hits))[:4]
print("  path echo:", json.dumps(out["path_echo"]))

# 7. aplay quiet-mode: any positive witness at all?
q = (RAW / "aplay-noise3.stderr").read_text(errors="replace")
out["aplay_quiet_invalid"] = {"stderr_bytes": len(q), "stdout_witness": False}
print("  aplay -q invalid: stderr bytes =", len(q))

(ROOT / "corpus/live/r75-scribe/parser-surface-audit.json").write_text(
    json.dumps(out, indent=1, default=str))
print("wrote corpus/live/r75-scribe/parser-surface-audit.json")
