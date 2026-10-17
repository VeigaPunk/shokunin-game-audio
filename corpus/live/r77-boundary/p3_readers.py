"""r77 BOUNDARY probe 3 — reader-matrix gaps + the split sentinel.

Gaps the scout left: ffplay (does a PLAYER trust the inflated declared size?),
soxi -s vs -D on the same wound, mediainfo / python soundfile availability,
RF64 container readability, and a decode-to-null read bound.
"""

from __future__ import annotations

import json
import os
import struct
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from r77b_lib import (  # noqa: E402
    LINE_SRC,
    SCRATCH,
    inspect_wav,
    readers,
    reader_digest,
    save_receipt,
    sever,
    sh,
    wipe_scratch,
)


def wound_pwrecord_kill():
    """pw-record KILL -> placeholder_8 / data zero (libsndfile never finalizes)."""
    out = SCRATCH / "w_pwrecord_KILL.wav"
    r = sever(["pw-record", "--target", LINE_SRC, str(out)], out, wall=1.2)
    return out, r


def wound_arecord_kill():
    """arecord -D hw:0,0 KILL -> data 0x80000000 (the 2 GiB split sentinel)."""
    out = SCRATCH / "w_arecord_KILL.wav"
    r = sever(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", str(out)], out, wall=1.2)
    return out, r


def wound_arecord_term_sysdefault():
    """arecord sysdefault TERM -> alsa_read_eintr unfinalized wound."""
    import signal

    out = SCRATCH / "w_arecord_sysdefault_TERM.wav"
    r = sever(["arecord", "-D", "sysdefault", "-f", "cd", "-t", "wav", str(out)], out,
              wall=1.2, sig=signal.SIGTERM)
    return out, r


def wound_ffmpeg_kill():
    out = SCRATCH / "w_ffmpeg_KILL.wav"
    r = sever(["ffmpeg", "-v", "error", "-f", "pulse", "-i", LINE_SRC, "-y", str(out)], out, wall=2.5)
    return out, r


def wound_ffmpeg_term():
    import signal

    out = SCRATCH / "w_ffmpeg_TERM.wav"
    r = sever(["ffmpeg", "-v", "error", "-f", "pulse", "-i", LINE_SRC, "-y", str(out)], out,
              wall=2.5, sig=signal.SIGTERM)
    return out, r


def wound_arecord_term_hw():
    import signal

    out = SCRATCH / "w_arecord_hw_TERM.wav"
    r = sever(["arecord", "-D", "hw:0,0", "-f", "cd", "-t", "wav", str(out)], out,
              wall=1.2, sig=signal.SIGTERM)
    return out, r


def wound_empty44():
    """A 44-byte finalized empty wav: unresolvable target under the prop."""
    out = SCRATCH / "w_empty44.wav"
    r = sh(["pw-record", "-P", "stream.capture.sink=true", "--target", "no_such_node_xyz",
            "-n", "48000", str(out)], timeout=12)
    return out, r


def rf64_file():
    """pw-record --container rf64: libsndfile's answer to the 4 GiB boundary."""
    out = SCRATCH / "c_rf64.wav"
    r = sh(["pw-record", "-P", "stream.capture.sink=true", "--target", LINE_SRC,
            "--container", "rf64", "-n", "48000", str(out)], timeout=12)
    return out, r


def main():
    wipe_scratch()
    rec = {"probe": "r77-boundary/p3-readers", "t0": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["availability"] = {
        "mediainfo": sh(["bash", "-lc", "command -v mediainfo || echo MISSING"])["out"].strip(),
        "python_soundfile": sh(["python3", "-c", "import soundfile"])["rc"],
        "python_soundfile_err": sh(["python3", "-c", "import soundfile"])["err"].strip()[-160:],
        "pip_cache_wheels": sh(["bash", "-lc", "ls ~/.cache/pip 2>/dev/null | head -5 || echo none"])["out"].strip(),
        "sndfile_info": sh(["bash", "-lc", "command -v sndfile-info"])["out"].strip(),
        "ffplay": sh(["bash", "-lc", "command -v ffplay"])["out"].strip(),
    }

    wounds = {}
    for name, fn in [
        ("pwrecord_KILL", wound_pwrecord_kill),
        ("arecord_hw_KILL", wound_arecord_kill),
        ("arecord_hw_TERM", wound_arecord_term_hw),
        ("arecord_sysdefault_TERM", wound_arecord_term_sysdefault),
        ("ffmpeg_KILL", wound_ffmpeg_kill),
        ("ffmpeg_TERM", wound_ffmpeg_term),
        ("empty44", wound_empty44),
        ("rf64_container", rf64_file),
    ]:
        path, sev = fn()
        insp = inspect_wav(path)
        wounds[name] = {
            "file": {k: insp.get(k) for k in ("bytes", "riff_magic", "riff_size_field", "form_type",
                                              "chunks", "fmt", "data_declared_field", "payload_bytes_actual",
                                              "frames", "peak", "nonzero_frac")},
            "sever": {k: sev.get(k) for k in ("rc", "killed_by_us", "err", "wall_before_signal_s")},
            "path": str(path),
        }
    rec["wounds"] = wounds

    # reader matrix on every wound
    matrix = {}
    for name, w in wounds.items():
        p = Path(w["path"])
        if not p.exists():
            matrix[name] = {"absent": True}
            continue
        rd = readers(p)
        d = reader_digest(rd)
        d["soxi_s_raw"] = rd["soxi_s"]["out"].strip()
        d["soxi_D_raw"] = rd["soxi_D"]["out"].strip()
        d["soxi_s_err"] = rd["soxi_s"]["err"].strip()[:160]
        d["sndfile_frames_raw"] = (rd["sndfile_info"]["out"] or "").strip()[:200]
        d["ffprobe_dur_raw"] = rd["ffprobe_dur"]["out"].strip()
        d["ffprobe_err"] = rd["ffprobe_dur"]["err"].strip()[:160]
        d["sndfile_rc"] = rd["sndfile_info"]["rc"]
        matrix[name] = d
    rec["reader_matrix"] = matrix

    # THE PLAYER QUESTION: does an inflated declared size make a player run long?
    play = {}
    for name in ("arecord_hw_KILL", "arecord_hw_TERM", "empty44", "pwrecord_KILL", "ffmpeg_KILL", "rf64_container"):
        p = Path(wounds[name]["path"])
        if not p.exists():
            play[name] = {"absent": True}
            continue
        cap_s = 6.0
        r = __import__("r77b_lib").ffplay_wall(p, cap_s=cap_s)
        dec = __import__("r77b_lib").ffmpeg_null_decode(p, cap_s=10.0)
        play[name] = {
            "ffplay_wall_s": r["wall_measured_s"],
            "ffplay_hit_cap": r["hit_cap"],
            "ffplay_rc": r["rc"],
            "ffplay_err": r["err"].strip()[:200],
            "ffmpeg_null_wall_s": dec["wall_measured_s"],
            "ffmpeg_null_rc": dec["rc"],
            "ffmpeg_null_err": dec["err"].strip()[:200],
            "declared_data": wounds[name]["file"].get("data_declared_field"),
            "declared_duration_if_trusted_s": None,
        }
        dd = wounds[name]["file"].get("data_declared_field")
        if dd == "placeholder_80000000":
            play[name]["declared_duration_if_trusted_s"] = round(2147483648 / (44100 * 2 * 2), 1)
        elif dd == "placeholder_ff":
            play[name]["declared_duration_if_trusted_s"] = None
    rec["player_behaviour"] = play

    save_receipt("probe-p3-readers.json", rec)

    print("== availability ==")
    print(json.dumps(rec["availability"], indent=1))
    print("== wounds ==")
    for k, v in wounds.items():
        f = v["file"]
        print(f"{k:24s} rc={v['sever']['rc']:>4} bytes={str(f.get('bytes')):>8} riff={f.get('riff_size_field'):<20} "
              f"data={f.get('data_declared_field'):<20} frames={f.get('frames')}")
    print("== reader matrix ==")
    for k, d in matrix.items():
        if d.get("absent"):
            print(f"{k:24s} ABSENT")
            continue
        print(f"{k:24s} soxi_s={str(d['soxi_s']):>10} soxi_D={str(d['soxi_D']):>14} "
              f"sndfile_frames={str(d['sndfile_frames']):>10} ffprobe={str(d['ffprobe_duration']):>10} "
              f"wave={str(d['python_wave_frames']):>8} wave_err={(d['python_wave_error'] or '')[:34]}")
    print("== player behaviour (ffplay/ffmpeg null decode) ==")
    for k, d in play.items():
        print(f"{k:24s} ffplay={d.get('ffplay_wall_s')}s hit_cap={d.get('ffplay_hit_cap')} rc={d.get('ffplay_rc')} "
              f"| ffmpeg_null={d.get('ffmpeg_null_wall_s')}s rc={d.get('ffmpeg_null_rc')} "
              f"declared_if_trusted={d.get('declared_duration_if_trusted_s')}s")


if __name__ == "__main__":
    main()
