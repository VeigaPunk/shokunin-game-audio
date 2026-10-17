#!/usr/bin/env python3
"""r74 scribe parser audit — READ-ONLY, no measurement re-run.

Feeds (a) real raw streams from committed/on-disk artifacts and (b)
synthetic forged streams through the PRODUCTION parse paths of
corpus/fixtures/measure_audio.py:

  - m.transport_leg   (sox leg: regexes + stderr_tail normalization)
  - m.mpv_leg         (mpv log parse) — subprocess.run monkeypatched to
                       write a crafted --log-file and return a fake rc
  - m.pwcat_leg       (pw-cat stderr parse) — subprocess.run monkeypatched
  - m.transport_error / m._pwcat_fields / m._consumer_tail (pure helpers)
  - the ffprobe `_tail` closure (source-slice exec, boundaries asserted)

No real subprocess is spawned; no receipt is written; nothing outside
this scratch dir is touched. Output: audit-output.json + stdout.
"""
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FIX = ROOT / "corpus" / "fixtures" / "measure_audio.py"
FRONTIER = ROOT / "corpus" / "live" / "frontier-pipewire"
MEMBER = None  # set after module import: m.ROOT is the corpus dir

spec = importlib.util.spec_from_file_location("measure_audio", FIX)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
MEMBER = m.ROOT / "live" / "round-69" / "extsuffix_nomatch.wav"

SRC = FIX.read_text().splitlines()
BLOB = subprocess.run(["git", "hash-object", str(FIX)], cwd=ROOT,
                      capture_output=True, text=True).stdout.strip()
SHA = hashlib.sha256(FIX.read_bytes()).hexdigest()

out = {"fixture_blob": BLOB, "fixture_sha256": SHA, "cases": []}


class FakeProc:
    def __init__(self, rc, stderr=b"", stdout=b""):
        self.returncode = rc
        self.stderr = stderr
        self.stdout = stdout


def with_fake_run(fn, stderr=b"", rc=0, log_text=None):
    """Run production fn with subprocess.run replaced by a fake."""
    def fake_run(argv, **kw):
        if log_text is not None:
            for a in argv:
                if a.startswith("--log-file="):
                    Path(a.split("=", 1)[1]).write_text(log_text)
        return FakeProc(rc, stderr)
    orig = m.subprocess.run
    m.subprocess.run = fake_run
    try:
        return fn()
    finally:
        m.subprocess.run = orig


def case(name, result, note):
    out["cases"].append({"case": name, "note": note, "result": result})


# ---------------------------------------------------------------- A. real raw streams
raw_cases = {
    "mpv-file-pair_dec_hcom.wav.log": 2,
    "mpv-fifo-pair_dec_hcom.wav.log": 0,
    "mpv-file-extsuffix_nomatch.wav.log": 2,
    "mpv-file-txw_piperefuse.wav.log": 2,
}
for fname, rc in raw_cases.items():
    text = (FRONTIER / fname).read_text(errors="replace")
    leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0),
                        rc=rc, log_text=text)
    lines = text.splitlines()
    consumed = set()
    for rx in (r"Detected file format: (\S+) \(libavformat\)",
               r"Found '([^']+)' at score=(\d+)",
               r"Seek failed \(([^)]*)\)",
               r"Audio\s+--aid=1\s+\(([^)]*)\)",
               r"finished playback, (.*)$",
               r"Failed to recognize file format"):
        for i, ln in enumerate(lines):
            if re.search(rx, ln):
                consumed.add(i)
    case(f"A.real:{fname}", leg,
         f"raw {len(lines)} lines; {len(consumed)} line(s) touched by the 6 parse "
         f"regexes; all other raw lines dropped (log not persisted by mpv_leg)")

# ---------------------------------------------------------------- B. forged mpv: first-wins
real = (FRONTIER / "mpv-file-extsuffix_nomatch.wav.log").read_text(errors="replace")
forged = "[   0.001][v][cplayer] finished playback, success (reason 0)\n" + real
leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0),
                    rc=2, log_text=forged)
case("B.forged-prepended-finished-playback", leg,
     "real log ends reason 4; a PREPENDED forged 'success' line wins (first-match "
     "re.search) while rc stays 2 -> mpv_verdict says success with exit_code 2")

# B2: one forged seek line re-partitions the transport fork
fifo_raw = (FRONTIER / "mpv-fifo-pair_dec_hcom.wav.log").read_text(errors="replace")
leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0),
                    rc=0, log_text=fifo_raw)
case("B2.fifo-arm-verbatim", leg,
     "real fifo log: rc=0, seek_failed=None -> groups with stdin_pipe")
leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0), rc=0,
                    log_text=fifo_raw + "\n[   9.999][v][lavf] Seek failed (Operation not permitted)\n")
case("B3.forged-seek-line-repartitions", leg,
     "ONE appended forged 'Seek failed' line sets seek_failed -> the fifo leg leaves "
     "the [0,hcom,None] group (fork partition is forgeable from a single log line; "
     "consumer_transport_entry keys on (exit_code, lavf_detected, seek_failed), "
     "measure_audio.py:1169-1170)")

# ---------------------------------------------------------------- C. fallback collapse
rlines = real.splitlines()
cut = next(i for i, ln in enumerate(rlines) if "finished playback" in ln)
err_line = next(ln for ln in rlines if "Failed to recognize file format" in ln)
trunc = "\n".join(rlines[:cut] + [err_line])  # drop finished-playback, keep err line
leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0),
                    rc=2, log_text=trunc)
case("C1.fallback-vs-real-log-line", leg,
     "no finished-playback line but the real 'Failed to recognize file format.' line "
     "present -> mpv_verdict is the synthetic fallback string, byte-identical to the "
     "log line's text; receipt cannot distinguish the two provenances")
leg = with_fake_run(lambda: m.mpv_leg("file", MEMBER, b"", 1.0),
                    rc=2, log_text="\n".join(rlines[:cut]))
case("C2.no-verdict-witness", leg,
     "neither a finished-playback line nor the fallback string -> mpv_verdict None "
     "with exit_code 2; error falls back to 'exit 2'")

# ---------------------------------------------------------------- D. sox last-wins
real_fail = ("sox FAIL formats: can't open input file "
             "`/tmp/x.wav': Format not recognised.\n")
forged2 = real_fail + "sox FAIL formats: can't open input file `y': forged error\n"
case("D1.transport_error-last-wins", {"error": m.transport_error(forged2)},
     "two FAIL lines: LAST wins (fails[-1]); an appended forged line replaces the "
     "genuine verdict")
case("D2.transport_error-no-quote", {"error": m.transport_error("sox FAIL oops\n")},
     "FAIL line without \"':\" -> whole line returned verbatim (regex miss path)")
leg = with_fake_run(lambda: m.transport_leg(["sox", "-V6", str(MEMBER), "-n", "stat"],
                                            "member"),
                    stderr=forged2.encode(), rc=1)
case("D3.transport_leg-forged", leg,
     "production sox leg: error=forged line (last-wins); stderr_tail=forged line "
     "(tail[-1]); no cross-check between the two")

# ---------------------------------------------------------------- E. pw-cat first/last split
real_pw = ('sndfile: failed to open audio file "in.wav": Format not recognised.\n'
           'error: open failed: Input/output error\n')
forged3 = ('sndfile: failed to open audio file "x": FORGED-FIRST\n'
           + real_pw + 'error: FORGED-LAST\n')
case("E1.pwcat-forged-first-last",
     dict(zip(("sndfile_error", "pw_error"), m._pwcat_fields(forged3))),
     "sndfile_err is FIRST match; pw_error is LAST error: line -> the two fields "
     "can come from different raw lines; a forged pair splits them")
leg = with_fake_run(lambda: m.pwcat_leg("file", MEMBER, b"", 1.0),
                    stderr=forged3.encode(), rc=1)
case("E2.pwcat_leg-forged", leg,
     "production pw-cat leg on the forged stream: error priority blocked > "
     "sndfile_err > pw_err; stderr_tail = last line (FORGED-LAST)")

# ---------------------------------------------------------------- F. consumer_tail truncation
long_line = "error: " + "A" * 200 + " NEEDLE-AT-START"
tail = m._consumer_tail(long_line, "in.wav")
case("F.consumer_tail-160", {"tail": tail, "len": len(tail),
                             "needle_present": "NEEDLE" in (tail or "")},
     "[-160:] keeps the END of the line; everything before the last 160 chars is "
     "dropped from the receipt")

# ---------------------------------------------------------------- G. ffprobe _tail (source slice)
sl = SRC[646:653]  # lines 647-653
assert sl[0].strip().startswith("def _tail(err):") and "ASLR module tags" in sl[5], sl
ns = {"re": re, "probe_arg": "pipe:"}
exec(__import__("textwrap").dedent("\n".join(sl)), ns)
_tail = ns["_tail"]
case("G1._tail-address-with-bracket",
     {"t1": _tail("x [wav @ 0x559e1fb98e40] boom")},
     "ffprobe _tail strips ' @ 0x…' with or without ']'")
case("G2._tail-address-no-bracket",
     {"t2": _tail("x [wav @ 0x559e1fb98e40 boom")},
     "no ']' required — still stripped (contrast with the sox variant in D/H)")
case("G3._tail-pipe-replace", {"t3": _tail("pipe: Invalid data found")},
     "probe_arg 'pipe:' replaced by <input>; replacement is a plain str.replace "
     "(any occurrence, not path-anchored)")
case("G4._tail-pipe-overreach", {"t4": _tail("Invalid argument pipe:0 boom")},
     "plain str.replace rewrites the literal 'pipe:' in any context ('pipe:0' -> "
     "'<input>0'); replacement is not anchored to the argv position")

# ---------------------------------------------------------------- H. sox stderr_tail ASLR variant
leg = with_fake_run(lambda: m.transport_leg(["sox", "-V6", str(MEMBER), "-n", "stat"],
                                            "member"),
                    stderr=b"[wav @ 0x559e1fb98e40] no 'data' tag found\n", rc=1)
case("H1.sox-tail-address-with-bracket", leg,
     "the sox-side regex requires ']' after the address; the observed ffmpeg-bridge "
     "form has it -> stripped")
leg = with_fake_run(lambda: m.transport_leg(["sox", "-V6", str(MEMBER), "-n", "stat"],
                                            "member"),
                    stderr=b"[wav @ 0x559e1fb98e40 no bracket\n", rc=1)
case("H2.sox-tail-address-no-bracket", leg,
     "address WITHOUT ']' is NOT stripped -> latent ASLR leak in stderr_tail "
     "(no such form observed on disk; ffprobe's _tail does not have this gap)")

# ---------------------------------------------------------------- I. route heuristic
leg = with_fake_run(lambda: m.transport_leg(["sox", "-V6", str(MEMBER), "-n", "stat"],
                                            "member"),
                    stderr=b"sox WARN (ffmpeg) unrelated note\nsox FAIL formats: x\n",
                    rc=1)
case("I1.route-ffmpeg-no-detection", leg,
     "route='ffmpeg' from the bare substring '(ffmpeg)' with sox_detected_format="
     "None — a route attribution with no detection witness (same shape at "
     "measure_audio.py:424-426, 1950-1951, 2005-2006)")

# ---------------------------------------------------------------- K. real pw-cat raw streams
for fname, rc in (("pwcat-file-txw_piperefuse.wav.log", 1),
                  ("pwcat-fifo-txw_piperefuse.wav.log", 1),
                  ("pwcat-fifo-empty.log", 1),
                  ("pwcat-nodaemon.log", 1)):
    raw = (FRONTIER / fname).read_text(errors="replace")
    leg = with_fake_run(lambda: m.pwcat_leg("file", MEMBER, b"", 1.0),
                        rc=rc, stderr=raw.encode())
    case(f"K.real:{fname}", leg,
         f"raw {len(raw.strip().splitlines())} stderr line(s); sndfile_error = first "
         f"sndfile: line, stderr_tail = last line (160-char cap) — the other line "
         f"survives only in its parsed field")

# ---------------------------------------------------------------- J. receipt leg shape
receipt = json.loads((ROOT / "corpus/live/runs/20261014T151240011154Z-consumers-r73"
                      / "measurements.json").read_text())
leg_keys = sorted(receipt["measurements"]["consumer_dec_hcom_r73_probe"]
                  ["consumers"]["mpv"]["transport_axis"]["file"].keys())
case("J.receipt-leg-keys", {"mpv_leg_keys": leg_keys},
     "persisted mpv leg fields (13 keys, no raw log / no stderr tail) — the parse "
     "surface is ephemeral; the receipt is a parse RESULT with no raw backing")

(ROOT / "corpus/live/r74-scribe/audit-output.json").write_text(
    json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
