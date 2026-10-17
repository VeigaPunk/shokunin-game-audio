#!/usr/bin/env python3
"""Apply the r76-simplifier deletion set D1..D8 to a copy of the fixture.

Every anchor must match exactly once (assert), so the patch cannot drift
silently.  Prints the per-deletion hit count and the byte delta.
"""
import sys
from pathlib import Path

src = Path(sys.argv[1])
dst = Path(sys.argv[2])
text = src.read_text()

DELETIONS = [
    # D1 — _capture_wav_inspect: data_4k_aligned is computed but copied
    # into NO receipt leaf (_capture_file_leg / _capture_sever_cell copy
    # only named keys) and is asserted nowhere: grep count == 1.
    ("D1 data_4k_aligned (computed, never serialized/asserted)",
     '            insp["data_4k_aligned"] = actual % 4096 == 0\n', ""),
    # D2 — capture_gate_r76_entry: hw0 bound, never loaded (AST proof);
    # the gate's arecord legs are literal -D default/pipewire/does_not_exist.
    ("D2 gate: dead hw0 binding",
     '             "inventory": inv}\n'
     "    src, mon, hw0 = _capture_leg_targets(inv)\n"
     '    entry["viability"] = {',
     '             "inventory": inv}\n'
     "    src, mon, _ = _capture_leg_targets(inv)\n"
     '    entry["viability"] = {'),
    # D3 — capture_sever_r76_entry: mon and hw0 bound, never loaded; the
    # arecord cells iterate inv["alsa_capture_devices"] directly.
    ("D3 sever: dead mon + hw0 bindings",
     '    entry = {"probe": "capture sever classes — TERM/KILL mid-record"}\n'
     "    src, mon, hw0 = _capture_leg_targets(inv)\n"
     "    cells = {}\n",
     '    entry = {"probe": "capture sever classes — TERM/KILL mid-record"}\n'
     "    src, _, _ = _capture_leg_targets(inv)\n"
     "    cells = {}\n"),
    # D4 — capture_name_axis_r76_entry: hw0 bound, never loaded; the name
    # legs use -D null only.
    ("D4 name axis: dead hw0 binding",
     "    src, mon, hw0 = _capture_leg_targets(inv)\n"
     "    legs = {}\n"
     '    with tempfile.TemporaryDirectory(prefix="capture-r76-") as tmp:\n'
     '        tgt = src or "alsa_input.nonexistent-r76"\n',
     "    src, mon, _ = _capture_leg_targets(inv)\n"
     "    legs = {}\n"
     '    with tempfile.TemporaryDirectory(prefix="capture-r76-") as tmp:\n'
     '        tgt = src or "alsa_input.nonexistent-r76"\n'),
    # D5 — capture_bounded_r76_entry parec byte-cap: the error LINE is
    # never recorded (the leaf carries error_class only, and the same
    # stderr text is still witnessed by stderr_tail via _capture_tail).
    ("D5 bounded: dead parec error-line binding",
     "            cls, line = _capture_errclass(err)\n"
     '            spec = re.search(r"sample spec(?:ification)? \'([^\']+)\'",\n',
     "            cls, _ = _capture_errclass(err)\n"
     '            spec = re.search(r"sample spec(?:ification)? \'([^\']+)\'",\n'),
    # D6 — sever expected map: the ffmpeg entry's kill_riff is never read
    # (the ffmpeg branch asserts the unfinalized UNION class instead).
    ("D6 sever: dead ffmpeg kill_riff expectation",
     '        "ffmpeg": {"term_rc": 255, "term_final": True,\n'
     '                   "kill_rc": -signal.SIGKILL, "kill_riff": None},\n',
     '        "ffmpeg": {"term_rc": 255, "term_final": True,\n'
     '                   "kill_rc": -signal.SIGKILL},\n'),
    # D7 — name axis: the exists-is-False branch duplicates what
    # _capture_out_kind already returns for a non-existent leaf
    # ("missing"), and the elif is unreachable (fin always carries
    # "exists", so a present `file` leaf is never falsy).
    ("D7 name axis: over-defensive out_kind branch",
     '    for leg in legs.values():\n'
     '        if "file" in leg and leg["file"].get("exists") is not False:\n'
     '            leg["out_kind"] = _capture_out_kind(leg["file"])\n'
     '        elif leg.get("file"):\n'
     '            leg["out_kind"] = "missing"\n',
     '    for leg in legs.values():\n'
     '        if leg.get("file"):\n'
     '            leg["out_kind"] = _capture_out_kind(leg["file"])\n'),
    # D8 — roundtrip: cap_rel is an ABSOLUTE path under a _rel name
    # (stale name) and a single-use alias; the value passed is unchanged.
    ("D8 roundtrip: misnamed single-use cap_rel alias",
     "        cap_rel = str(cap)\n", ""),
    ("D8b roundtrip: inline the alias at its only use",
     '        sox_cap = transport_leg(["sox", "-V6", cap_rel, "-n", "stat"],\n',
     '        sox_cap = transport_leg(["sox", "-V6", str(cap), "-n", "stat"],\n'),
    # D9 — _capture_sever_cell: the `env` parameter is passed by NO caller
    # (AST call-site scan over all 26 _capture_* call sites: only
    # _capture_file_leg ever passes env=, at line 3371), and the internal
    # {**os.environ, **(env or {})} merge is then just a copy of an
    # unmutated os.environ (grep: no os.environ[...] / putenv / update in
    # the module).  Dropping it makes the child inherit — the same
    # environment — and leaves ONE env convention (merge at the caller).
    ("D9 sever: dead env parameter + merge",
     "def _capture_sever_cell(argv, fname, sig,\n"
     "                        wait_s=CAPTURE_R76_SEVER_WAIT_S,\n"
     "                        kill_wait_s=CAPTURE_R76_KILL_WAIT_S, env=None):\n",
     "def _capture_sever_cell(argv, fname, sig,\n"
     "                        wait_s=CAPTURE_R76_SEVER_WAIT_S,\n"
     "                        kill_wait_s=CAPTURE_R76_KILL_WAIT_S):\n"),
    ("D9b sever: inherit instead of merging an unused env",
     "                                stderr=subprocess.PIPE,\n"
     "                                env={**os.environ, **(env or {})},\n"
     "                                start_new_session=True)\n",
     "                                stderr=subprocess.PIPE,\n"
     "                                start_new_session=True)\n"),
]

for label, old, new in DELETIONS:
    n = text.count(old)
    assert n == 1, f"{label}: anchor matched {n} times, expected 1"
    text = text.replace(old, new)
    print(f"applied {label}")

dst.write_text(text)
print(f"baseline {src.stat().st_size} B -> variant {dst.stat().st_size} B "
      f"({dst.stat().st_size - src.stat().st_size:+d} B)")
