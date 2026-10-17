#!/usr/bin/env python3
"""r95 SIMPLIFIER — differential narrow check: shared vs FOLDED copy.

Loads the folded scratch module (corpus/live/r95-simplifier/
measure_audio-folded.py) and re-runs the daemon-free narrow checks that
prove_daemonfree.py ran against the shared copy, then compares the two
observables key by key.  Any key that differs is a rejected fold.

Writes prove-folded.json next to this file.
"""
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = json.loads((HERE / "prove-daemonfree.json").read_text())

spec = importlib.util.spec_from_file_location(
    "measure_audio_folded", HERE / "measure_audio-folded.py")
M = importlib.util.module_from_spec(spec)
sys.modules["measure_audio_folded"] = M
spec.loader.exec_module(M)

NO_DAEMON_OUT = 'R95AJSON {"mode":"open","ok":false,"status":17}\n'
UNKNOWN_OUT = 'R95AJSON {"mode":"unknown","mode_arg":"bogusmode"}\n'
now = {}
now["errclass_no_daemon_stdout_only"] = M._jack_r95_errclass(NO_DAEMON_OUT)
now["errclass_unknown_stdout_only"] = M._jack_r95_errclass(UNKNOWN_OUT)
now["errclass_empty"] = M._jack_r95_errclass("")
sym = M._jack_r95_symbols()
now["symbols"] = {k: sym.get(k) for k in
                  ("export_count", "absent", "present", "export_kinds")}
with tempfile.TemporaryDirectory(prefix="r95s-fold-") as tmp:
    tp = Path(tmp) / "tone997.wav"
    tone = M._jack_r95_tone(tp, 1.5)
    stats = M._jack_r95_wav_stats(tp)
    now["tone"] = {k: tone.get(k) for k in
                   ("frames", "rate", "freq_hz", "amp_i16", "peak_i16")}
    now["wav_stats"] = {k: stats.get(k) for k in
                        ("frames", "rate", "peak", "nonzero")}
now["settings_at_prove"] = M._jack_r95_settings()
now["json_parse_unknown"] = M._jack_r95_json({"stdout_raw": UNKNOWN_OUT})
now["json_parse_absent"] = M._jack_r95_json({"stdout_raw": "no json here\n"})
now["norm_scrub"] = M._jack_r95_norm(
    f"client.name = r95a_{os.getpid()}_shape seq=12345")

cmp_keys = ["errclass_no_daemon_stdout_only", "errclass_unknown_stdout_only",
            "errclass_empty", "symbols", "tone", "wav_stats",
            "settings_at_prove", "json_parse_unknown", "json_parse_absent",
            "norm_scrub"]
rows = {k: {"shared": BASE.get(k),
            "folded": json.loads(json.dumps(now.get(k))),
            "equal": BASE.get(k) == json.loads(json.dumps(now.get(k)))}
        for k in cmp_keys}
OUT = {"rows": rows, "all_equal": all(r["equal"] for r in rows.values()),
       "errclass_table_folded": [[n, p] for n, p in M._JACK_R95_ERR_CLASSES]}
(HERE / "prove-folded.json").write_text(
    json.dumps(OUT, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in OUT.items() if k != "rows"}, indent=2))
for k, r in rows.items():
    print(f"  {k:36s} equal={r['equal']}")
