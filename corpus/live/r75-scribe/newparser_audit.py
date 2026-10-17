#!/usr/bin/env python3
"""r75 scribe (recovery gen) — LANDED-parser raw-vs-parsed audit.

The r75 author arm landed in the worktree during this seat's window
(fixture blob b057bab6b367…, 888 insertions / 3 line-replacements vs HEAD
e3ef52e1…). This script audits the NEW parse helpers against the RAW
surfaces captured by this seat and the dead seat, using the exact argv the
new legs use:

  paplay  : paplay -v [<path>]                       (new paplay_leg)
  aplay   : aplay -D null [<path>]                   (new aplay_leg matrix)
  ffplay  : ffplay -nodisp -autoexit -v debug <path> (new ffplay_leg, SDL dummy)

All invocations bounded by `timeout -s KILL`; silence/text inputs only; no
probe mode runs; no receipt is written. Output: newparser-audit.json.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
SCR = ROOT / "corpus/live/r75-scribe"
RAW = SCR / "raw"
FIX = ROOT / "corpus/fixtures/measure_audio.py"

spec = importlib.util.spec_from_file_location("measure_audio", FIX)
ma = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ma)

out = {"fixture_sha256": hashlib.sha256(FIX.read_bytes()).hexdigest(),
       "fixture_blob": subprocess.run(
           ["git", "hash-object", str(FIX)], capture_output=True,
           text=True).stdout.strip(),
       "cases": {}, "fresh_runs": {}}


def run_bounded(argv, env_extra=None, stdin_file=None, seconds=20):
    env = {**os.environ, **(env_extra or {})}
    argv = ["timeout", "-s", "KILL", str(seconds)] + argv
    with open(stdin_file, "rb") if stdin_file else open(os.devnull, "rb") as fh:
        p = subprocess.run(argv, capture_output=True, stdin=fh, env=env)
    return p.returncode, p.stdout, p.stderr


# ---- A. new parsers on the raw captures already on disk ---------------------
def case(name, path, fn):
    p = RAW / path
    if not p.exists():
        out["cases"][name] = {"path": path, "MISSING": True}
        return
    text = p.read_text(errors="replace")
    out["cases"][name] = {"path": path, "bytes": len(text), "result": fn(text)}
    print(f"  {name}: {json.dumps(out['cases'][name]['result'])[:200]}")


print("fixture blob:", out["fixture_blob"], "sha256:", out["fixture_sha256"][:16])
print("new helpers:", {n: hasattr(ma, n) for n in
                       ("_paplay_fields", "_aplay_fields", "_ffplay_fields",
                        "paplay_leg", "aplay_leg", "ffplay_leg")})
print("== A. new parsers on captured raw surfaces")
case("paplay_invalid", "rv-paplay-noise.stderr",
     lambda t: {"fields": ma._paplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "noise.wav")})
case("paplay_xdg_severed", "rv-pp-xdg.stderr",
     lambda t: {"fields": ma._paplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "silence.wav")})
case("paplay_pulseserver", "rv-pp-pulseserver.stderr",
     lambda t: {"fields": ma._paplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "silence.wav")})
case("aplay_raw_fallback", "rv-aplay-noise.stderr",
     lambda t: {"fields": ma._aplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "noise.wav")})
case("aplay_valid_verbose", "aplay-valid.stderr",
     lambda t: {"fields": ma._aplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "silence.wav")})
case("ffplay_invalid_info", "rv-ffplay-noise.stderr",
     lambda t: {"fields": ma._ffplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "noise.wav")})
case("ffplay_valid_info", "ffplay-file.stderr",
     lambda t: {"fields": ma._ffplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "silence.wav")})
case("ffplay_sdl_gate", "ffplay-bogusdrv.stderr",
     lambda t: {"fields": ma._ffplay_fields(t),
                "tail": ma._consumer_tail(t, RAW / "silence.wav")})

# ---- B. fresh bounded runs with the new legs' exact argv --------------------
print("== B. fresh runs with the new argv shapes")
SIL = RAW / "silence.wav"
NOI = RAW / "noise.wav"

# paplay -v, valid + invalid (live pulse daemon)
for tag, path in (("paplay_v_valid", SIL), ("paplay_v_invalid", NOI)):
    rc, so, se = run_bounded(["paplay", "-v", str(path)], seconds=20)
    t = se.decode(errors="replace")
    (RAW / f"np-{tag}.stderr").write_bytes(se)
    out["fresh_runs"][tag] = {"rc": rc, "stderr_bytes": len(se),
                              "fields": ma._paplay_fields(t),
                              "tail": ma._consumer_tail(t, path)}
    print(f"  {tag}: rc={rc} fields={out['fresh_runs'][tag]['fields']}")

# aplay -D null, valid + invalid
for tag, path in (("aplay_null_valid", SIL), ("aplay_null_invalid", NOI)):
    rc, so, se = run_bounded(["aplay", "-D", "null", str(path)], seconds=20)
    t = se.decode(errors="replace")
    (RAW / f"np-{tag}.stderr").write_bytes(se)
    out["fresh_runs"][tag] = {"rc": rc, "stderr_bytes": len(se),
                              "fields": ma._aplay_fields(t),
                              "tail": ma._consumer_tail(t, path)}
    print(f"  {tag}: rc={rc} fields={out['fresh_runs'][tag]['fields']}")

# ffplay -v debug, valid + invalid (SDL dummy) — the new leg's exact shape
for tag, path in (("ffplay_dbg_valid", SIL), ("ffplay_dbg_invalid", NOI)):
    rc, so, se = run_bounded(
        ["ffplay", "-nodisp", "-autoexit", "-v", "debug", str(path)],
        env_extra=ma.FFPLAY_R75_ENV, seconds=25)
    t = se.decode(errors="replace")
    (RAW / f"np-{tag}.stderr").write_bytes(se)
    fields = ma._ffplay_fields(t)
    tail = ma._consumer_tail(t, path)
    out["fresh_runs"][tag] = {
        "rc": rc, "stderr_bytes": len(se),
        "stderr_lines_splitlines": len(t.splitlines()),
        "stderr_lines_nl": t.count("\n"),
        "cr_bytes": t.count("\r"), "esc2k": t.count("\x1b[2K"),
        "fields": fields, "tail": tail,
        "tail_has_nan_token": "nan" in (tail or ""),
        "tail_has_hex_ctx": "0x" in (tail or ""),
        "raw_log_has_ctx_addr": "ctx @ 0x" in t,
        "statistics_lines": t.count("Statistics:")}
    print(f"  {tag}: rc={rc} bytes={len(se)} fields={json.dumps(fields)[:180]}")
    print(f"     tail={tail!r}"[:180])

(SCR / "newparser-audit.json").write_text(json.dumps(out, indent=1, default=str))
print("wrote corpus/live/r75-scribe/newparser-audit.json")
