#!/usr/bin/env python3
"""r85-critic unit replay (read-only): the committed fixture's pure
helpers re-run against canned inputs — the negctl classifier table, the
post-loss flush boundary, and the mixclip rail/peak witness.

Imports corpus/fixtures/measure_audio.py (byte-identical to commit
2a49d540) and calls ONLY pure helpers. No host mutation: no module
loads, no streams, no pactl/pw-* invocations.
"""
import importlib.util
import sys as _sys

_sys.dont_write_bytecode = True
import json
import os
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
FIX = ROOT / "corpus/fixtures/measure_audio.py"

spec = importlib.util.spec_from_file_location("measure_audio_r85", FIX)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
import numpy as np  # noqa: E402

out = {"fixture_sha_expected": "714564a32141f134f849401dd029e1e10c4aa19bb848a43fd50f70a251499ee2"}

# ---- 1. negctl classifier table replay (the 13 canned cases) ----
cases = [
    ("u_getinfo", "Failed to get sink information: No such entity\n", "pa_get_info_noent"),
    ("u_getinfo_src", "Failed to get source information: No such entity\n", "pa_get_info_noent"),
    ("u_failure_noent", "Failure: No such entity\n", "pa_failure_noent"),
    ("u_stream_noent", "Stream error: No such entity\n", "pa_stream_noent"),
    ("u_invalid_arg", "Operation failed: Invalid argument\n", "pa_invalid_arg"),
    ("u_pwcli_global", "Error: \"info: unknown global '232456'\"\n", "pwcli_unknown_global"),
    ("u_no_target", "stream node 84 error: no target node available\nremote error: id=2 seq:7 res:-2 (No such file or directory): no target node available\n", "no_target_node"),
    ("u_move_parse", "Failed to move sink input to 'x': No such entity\n", "pa_no_such_entity"),
    ("u_empty", "", None),
    ("u_noise", "Volume: front-left: 65536 / 100% / 0.00 dB\n", None),
    ("u_segv_words", "Segmentation fault (core dumped)\n", None),
    ("u_recording", "Recording WAVE 'x.wav' : Signed 16 bit Little Endian\n", None),
    ("u_unknown_pcm", "Unknown PCM pulse\n", "alsa_unknown_pcm"),
]
tab = []
for name, text, want in cases:
    got, hit = mod._pactlmon_r85_errclass(text)
    tab.append({"case": name, "want": want, "got": got, "match": got == want})
out["classifier_table"] = tab
out["classifier_all_match"] = all(t["match"] for t in tab)

# ---- 2. post-loss flush boundary (_pactlmon_r85_post_stats) ----
def write_wav(path, nframes, fill):
    pcm = np.zeros((nframes, 2), dtype="<i2")
    if fill == "content":
        pcm[:, :] = 8192
    elif fill == "zeros":
        pcm[:, :] = 0
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm.tobytes())


def size_at_frame(nframes):
    return 44 + nframes * 4


tmp = Path(tempfile.mkdtemp(prefix="r85c-unit-", dir=os.environ.get("TMPDIR") or None))
rows = []
for label, total, loss_frames, fill in (
        ("flush_2048_content", 3000, 952, "content"),
        ("froze", 3000, 3000, "zeros"),
        ("grew_zeros", 3000, 1000, "zeros"),
        ("flush_at_bound_16384", 20000, 3616, "content"),
        ("flush_over_bound_16385", 20000, 3615, "content"),
):
    p = tmp / f"{label}.wav"
    write_wav(p, total, fill)
    st = mod._pactlmon_r85_post_stats(str(p), size_at_frame(loss_frames))
    # the entry arm: post_frames > FLUSH_BOUND -> failure
    arm_fails = (st.get("post_frames") or 0) > mod.PACTLMON_R85_FLUSH_BOUND
    rows.append({"case": label, "post": st, "bound": mod.PACTLMON_R85_FLUSH_BOUND,
                 "arm_would_fail": arm_fails})
out["post_stats"] = rows

# ---- 3. mixclip rail witness (_pactlmon_r85_amps) ----
p = tmp / "clip.wav"
n = 48000
t = np.arange(n) / 48000
left = np.clip((24576 * np.sin(2 * np.pi * 1000 * t)) * 2.0, -32768, 32767).astype("<i2")
right = np.clip((24576 * np.sin(2 * np.pi * 3214 * t)) * 2.0, -32768, 32767).astype("<i2")
pcm = np.empty(n * 2, dtype="<i2")
pcm[0::2], pcm[1::2] = left, right
with wave.open(str(p), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(48000)
    w.writeframes(pcm.tobytes())
amps = mod._pactlmon_r85_amps(str(p), {"a": 1000.0, "c": 3214.0}, win_s=0.25, skip_s=0.35)
wins = amps.get("windows") or []
pk = mod._pactlmon_r85_med(wins, "peak")
rail = mod._pactlmon_r85_med(wins, "rail_frac")
out["clip"] = {
    "peak_med": pk, "rail_frac_med": rail,
    "arm_peak_ok": (pk is not None and pk >= 32767),
    "arm_rail_env_ok": (rail is not None and mod.PACTLMON_R85_RAIL_ENV[0] <= rail <= mod.PACTLMON_R85_RAIL_ENV[1]),
    "rail_env": mod.PACTLMON_R85_RAIL_ENV,
    "solo_env": mod.PACTLMON_R85_SOLO_ENV,
    "flush_bound": mod.PACTLMON_R85_FLUSH_BOUND,
    "dup_env": mod.PACTLMON_R85_DUP_ENV,
    "classes": dict(mod._PACTLMON_R85_ERR_CLASSES),
    "negctl_legs": sorted(
        ["u_getinfo", "u_getinfo_src", "u_failure_noent", "u_stream_noent",
         "u_invalid_arg", "u_pwcli_global", "u_no_target", "u_move_parse",
         "u_empty", "u_noise", "u_segv_words", "u_recording", "u_unknown_pcm"]),
}

# ---- 4. leg-count invariant (the 87 claim) from the committed receipts ----
tot = 0
per = {}
for run in ("run1", "run2"):
    d = json.load(open(ROOT / f"corpus/live/r85-author/runs/{run}/measurements.json"))
    m = d["measurements"]
    counts = {k: len(m[k]["legs"]) for k in
              ("pactlmon_addr_r85_probe", "pactlmon_mix_r85_probe",
               "pactlmon_aplayenv_r85_probe", "pactlmon_capture_r85_probe",
               "pactlmon_negctl_r85_probe")}
    per[run] = {"counts": counts, "total": sum(counts.values()),
                "failures": {k: m[k]["failures"] for k in counts},
                "blocked": {k: m[k].get("blocked") for k in counts}}
    tot = per[run]["total"]
out["leg_counts"] = per
out["leg_total"] = tot

print(json.dumps(out, indent=2, default=str))
