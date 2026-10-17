#!/usr/bin/env python3
"""r95 SIMPLIFIER — daemon-free narrow proof harness (scratch only).

Exercises the r95 block's non-graph helpers directly (imported read-only
from corpus/fixtures/measure_audio.py) so that fold candidates whose
affected legs are pure-Python / nm / pw-metadata can be proven without a
live JACK client.  The pw-dump-dependent legs are NOT exercised here (the
host's daemon is saturated; recorded in the report as a named blocker).

Writes prove-daemonfree.json next to this file.  TMPDIR must be
/home/vgpnk/Projects/shokunin/tmp.  No tracked file is touched.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]               # corpus/live/r95-simplifier -> repo root
SHARED = ROOT / "corpus" / "fixtures" / "measure_audio.py"
SCRATCH = HERE / "measure_audio.py"
assert SCRATCH.read_bytes() == SHARED.read_bytes(), \
    "scratch copy is not byte-identical to the shared tree"
sys.path.insert(0, str(HERE))

import measure_audio as M            # noqa: E402  (scratch copy, read-only)

OUT = {}

# --- 1. the r95-local error-class table, against the REAL fixture bytes
#        (captured from the built fixture in this scratch dir)
NO_DAEMON_OUT = 'R95AJSON {"mode":"open","ok":false,"status":17}\n'
UNKNOWN_OUT = 'R95AJSON {"mode":"unknown","mode_arg":"bogusmode"}\n'
OUT["errclass_no_daemon_stdout_only"] = M._jack_r95_errclass(NO_DAEMON_OUT)
OUT["errclass_unknown_stdout_only"] = M._jack_r95_errclass(UNKNOWN_OUT)
OUT["errclass_empty"] = M._jack_r95_errclass("")
OUT["errclass_table"] = [[n, p] for n, p in M._JACK_R95_ERR_CLASSES]

# --- 2. the availability census (nm -D over the host's only libjack)
sym = M._jack_r95_symbols()
OUT["symbols"] = {k: sym.get(k) for k in
                  ("export_count", "absent", "present", "export_kinds")}
OUT["symbols_want_absent"] = sorted(M.JACK_R95_ABSENT_SYMS)
OUT["symbols_want_present"] = sorted(M.JACK_R95_PRESENT_SYMS)
OUT["symbols_libjack"] = str(M.JACK_R95_LIBJACK)
OUT["symbols_libjack_exists"] = M.JACK_R95_LIBJACK.exists()

# --- 3. the tone fixture + own DFT (the PW->JACK sample-exactness source)
with tempfile.TemporaryDirectory(prefix="r95s-prove-") as tmp:
    tone_path = Path(tmp) / "tone997.wav"
    tone = M._jack_r95_tone(tone_path, 1.5)
    stats = M._jack_r95_wav_stats(tone_path)
    OUT["tone"] = {k: tone.get(k) for k in
                   ("frames", "rate", "freq_hz", "amp_i16", "peak_i16")}
    OUT["tone_amp_want"] = M.JACK_R95_AMP_I16
    OUT["tone_peak_law_holds"] = tone.get("peak_i16") == M.JACK_R95_AMP_I16
    OUT["in_peak_expected"] = tone.get("peak_i16", 0) / 32768.0
    OUT["wav_stats"] = {k: stats.get(k) for k in
                        ("frames", "rate", "peak", "nonzero")}

# --- 4. the host settings store through _jack_r95_run + pw-metadata
OUT["settings_at_prove"] = M._jack_r95_settings()
OUT["settings_force_quantum_clean"] = \
    OUT["settings_at_prove"].get("clock.force-quantum") == "0"

# --- 5. the R95AJSON reader on real fixture lines
OUT["json_parse_unknown"] = M._jack_r95_json({"stdout_raw": UNKNOWN_OUT})
OUT["json_parse_absent"] = M._jack_r95_json({"stdout_raw": "no json here\n"})

# --- 6. the volatile scrub (r95a_<pid> class)
OUT["norm_scrub"] = M._jack_r95_norm(
    f"client.name = r95a_{os.getpid()}_shape seq=12345")

(HERE / "prove-daemonfree.json").write_text(
    json.dumps(OUT, indent=2, sort_keys=True) + "\n")
print(json.dumps(OUT, indent=2, sort_keys=True))
