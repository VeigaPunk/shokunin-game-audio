#!/usr/bin/env python3
"""r73-scout: fold the two consumer matrices + special legs into one summary
the author/verifier can diff against."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
RUNS = OUT / "runs"


def load(name):
    return json.loads((RUNS / name).read_text())


def classify_pwcat(c):
    if c["rc"] == 0:
        return "accept"
    if "Format not recognised" in c["stderr"]:
        return "reject:format-not-recognised"
    if "unimplemented format" in c["stderr"]:
        return "reject:unimplemented-format"
    if "Host is down" in c["stderr"]:
        return "blocked:no-daemon"
    return "reject:other"


def classify_mpv(c):
    p = c["playback"] or ""
    if c["rc"] == 0 and "success" in p:
        return "accept:played"
    if "no audio or video data played" in p:
        return "reject:no-data(seek-flush)"
    if "unrecognized file format" in p:
        return "reject:format-not-recognized"
    return "reject:other"


def fold(cells, classify, arms):
    out = {}
    for c in cells:
        out.setdefault(c["member"], {})[c["arm"]] = {
            "rc": c["rc"], "class": classify(c), "log": c["log"]}
    for m, a in out.items():
        a["fork"] = len({v["class"] for v in a.values() if isinstance(v, dict)}) > 1
    return out


pw = load("pwcat-matrix-run1.json")
mv = load("mpv-matrix-run1.json")
doc = {
    "probe": "r73-scout summary (independent pre-measurement)",
    "pwcat": fold(pw["cells"], classify_pwcat, ("file", "fifo_path")),
    "mpv": fold(mv["cells"], classify_mpv,
                ("file", "fifo_path", "stdin_pipe", "stdin_file")),
    "pwcat_name_axis_probe": {
        "note": "same .snd bytes, fifo path extension is the only variable",
        "fifo_named_g1.fifo": {"rc": 1, "stderr": "Format not recognised."},
        "fifo_named_g2.snd": {"rc": 0, "stderr": ""},
        "stdin_dash": {"rc": 1, "stderr": "Format not recognised."},
    },
    "special_legs": {
        "daemon_gate": {
            "pw_cat_file_empty_runtime": {"rc": 1, "wall_s": 0.003,
                "msg": "error: pw_context_connect() failed: Host is down",
                "log": "logs/special/A1.out"},
            "pw_cat_fifo_empty_runtime_no_writer": {"rc": 1, "wall_s": 0.003,
                "note": "fifo open never reached", "log": "logs/special/A2.out"},
        },
        "writerless_fifo": {
            "wchan": "wait_for_partner", "state": "S",
            "sigterm": "still alive 1.5s after SIGTERM",
            "timeout_kill_5": {"rc": 137, "wall_s": 5.001},
            "timeout_k2_4": {"rc": 137, "wall_s": 6.001,
                "note": "TERM at 4s ignored; KILL after 2s"},
            "log": "logs/special/B1.status",
        },
        "zero_byte_writer": {"rc": 1, "wall_s": 0.203,
            "msg": "Format not recognised.", "log": "logs/special/C1.out"},
        "pacing": {
            "instant_dump_4s_tone": {"rc": 0, "wall_s": 4.035,
                "log": "logs/special/D1.out"},
            "chunked_1600B_0.2s": {"rc": 0, "wall_s": 8.209,
                "log": "logs/special/D2.out"},
            "raw_mode_a": {"rc": 0, "wall_s": 0.350,
                "log": "logs/special/D3.out"},
        },
        "target_0_unlinked": {"rc": 124, "wall_s": 4.002,
            "note": "hangs (no drain) but TERM-terminable at deadline",
            "log": "logs/special/E1.out"},
        "mpv_writerless_fifo": {"rc": 137, "wall_s": 5.001,
            "log": "logs/special/F1.log"},
        "mpv_linger_1s": {"rc": 0, "wall_s": 1.235,
            "log": "logs/special/F2.log"},
        "mpv_zero_byte_writer": {"rc": 2, "wall_s": 0.237,
            "class": "unrecognized file format",
            "log": "logs/special/F3.log"},
    },
    "mpv_hcom_pcm_probe": {
        "file_arm": {"rc": 2, "pcm_bytes": None,
                     "note": "no PCM file created; 0 samples decoded"},
        "fifo_arm": {"rc": 0, "pcm_bytes": 3520,
                     "note": "3520 samples u8 @22050Hz = ffmpeg's single 440B packet"},
        "cmd": "mpv --ao=pcm --ao-pcm-file=<raw> --ao-pcm-waveheader=no",
    },
    "mechanism": {
        "seek_failed_string": "av_strerror(-1) == 'Operation not permitted' "
            "(libavutil 61.1.101 ctypes probe)",
        "no_syscall": "strace -f: 0 lseek during refresh seek; "
            "ffmpeg -ss 0.005: 'could not seek to position', AVIO stats '0 seeks'",
        "hcom_demuxer": "no read_seek / read_timestamp (upstream hcom.c)",
    },
}
out = RUNS / "scout-summary.json"
out.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
print("wrote", out)
for consumer in ("pwcat", "mpv"):
    print("=" * 10, consumer)
    for m, arms in doc[consumer].items():
        print(f"  {m:20s} fork={arms['fork']!s:5s} " +
              " ".join(f"{a}={arms[a]['class']}(rc{arms[a]['rc']})"
                       for a in arms if isinstance(arms[a], dict)))
