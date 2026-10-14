#!/usr/bin/env python3
"""r71-scout: ffmpeg/ffprobe verdict matrix over the corpus member sets.

Read-only probes against tracked corpus bytes; writes JSON to scratch only.

Members:
  - 17 corpus/artifacts/*.wav fixtures (SPECS names)
  - 17 transport members: r67 x10, r68 x2, r69 x5 (as resolved by
    measure_audio.py TRANSPORT_R6{7,8,9}_MEMBERS)

Per member x transport leg:
  ffprobe: ffprobe -v error -show_format -of json <input>
           -> exit, format_name, probe_score, format stderr tail
  ffmpeg : ffmpeg -v error -i <input> -f null -
           -> exit, stderr tail (verdict)

Transports (mirrors TRANSPORT_R67_ARMS named/seekable):
  file          input = member path
  stdin_pipe    member bytes piped via subprocess input=  (input "pipe:0")
  redirected_fd member opened rb and passed as stdin      (input "pipe:0"
                on a seekable fd — ffmpeg decides from the fd itself)
  fifo_path     named fifo carrying the member bytes, writer lingers
                HOLD_S after write (r67 protocol: default 1.0 s)
"""
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TIMEOUT_S = 10
HOLD_S = float(os.environ.get("MEASURE_FIFO_WRITER_HOLD_S", "1.0"))

ARTIFACT_MEMBERS = {p.stem: p for p in sorted((ROOT / "corpus" / "artifacts").glob("*.wav"))}

TRANSPORT_MEMBERS = {
    "r67/preempt_act": ROOT / "corpus/live/round-65/pair_preempt_act.wav",
    "r67/preempt_gsrt": ROOT / "corpus/live/round-65/pair_preempt_gsrt.wav",
    "r67/preempt_hcom": ROOT / "corpus/live/round-65/pair_preempt_hcom.wav",
    "r67/preempt_both": ROOT / "corpus/live/round-65/pair_preempt_both.wav",
    "r67/dec_hcom": ROOT / "corpus/live/round-66/pair_dec_hcom.wav",
    "r67/dec_act": ROOT / "corpus/live/round-66/pair_dec_act.wav",
    "r67/lengate_gsrt_24": ROOT / "corpus/live/round-66/pair_lengate_gsrt_24.wav",
    "r67/lengate_gsrt_25": ROOT / "corpus/live/round-66/pair_lengate_gsrt_25.wav",
    "r67/lengate_hcom_131": ROOT / "corpus/live/round-66/pair_lengate_hcom_131.wav",
    "r67/lengate_hcom_132": ROOT / "corpus/live/round-66/pair_lengate_hcom_132.wav",
    "r68/posttable_nomatch": ROOT / "corpus/live/round-68/posttable_nomatch.wav",
    "r68/txw_piperefuse": ROOT / "corpus/live/round-68/txw_piperefuse.wav",
    "r69/extsuffix_wav": ROOT / "corpus/live/round-69/extsuffix_nomatch.wav",
    "r69/extsuffix_bin": ROOT / "corpus/live/round-69/extsuffix_nomatch.bin",
    "r69/extsuffix_txw": ROOT / "corpus/live/round-69/extsuffix_nomatch.txw",
    "r69/extsuffix_f32": ROOT / "corpus/live/round-69/extsuffix_nomatch.f32",
    "r69/extsuffix_snd": ROOT / "corpus/live/round-69/extsuffix_nomatch.snd",
}


def clean(text):
    # strip ASLR context addresses + concrete paths so output stays comparable
    text = re.sub(r"0x[0-9a-f]+", "0x<addr>", text)
    return text.strip().splitlines()[-1][-200:] if text.strip() else None


def run(args, data=None, stdin=None, timeout=TIMEOUT_S):
    kw = {"input": data} if data is not None else ({"stdin": stdin} if stdin else {})
    try:
        proc = subprocess.run(args, capture_output=True, timeout=timeout, **kw)
        return proc.returncode, proc.stdout, proc.stderr.decode(errors="replace"), False
    except subprocess.TimeoutExpired as exc:
        return None, exc.stdout or b"", (exc.stderr or b"").decode(errors="replace"), True


def ffprobe_leg(input_spec, data=None, stdin=None):
    args = ["ffprobe", "-v", "error", "-show_format", "-of", "json", input_spec]
    code, out, err, timed = run(args, data=data, stdin=stdin)
    leg = {"input": input_spec, "tool": "ffprobe", "exit_code": code,
           "format_name": None, "probe_score": None, "error": None}
    if timed:
        leg["error"] = f"blocked: no verdict within {TIMEOUT_S} s"
    else:
        try:
            fmt = json.loads(out or b"{}").get("format", {})
            leg["format_name"] = fmt.get("format_name")
            leg["probe_score"] = fmt.get("probe_score")
        except json.JSONDecodeError:
            leg["error"] = "unparseable json output"
        if code != 0 or not leg["format_name"]:
            tail = clean(err)
            leg["error"] = leg["error"] or tail
    return leg


def ffmpeg_leg(input_spec, data=None, stdin=None):
    args = ["ffmpeg", "-v", "error", "-i", input_spec, "-f", "null", "-"]
    code, out, err, timed = run(args, data=data, stdin=stdin)
    leg = {"input": input_spec, "tool": "ffmpeg", "exit_code": code,
           "stderr_tail": clean(err), "error": None}
    if timed:
        leg["error"] = f"blocked: no verdict within {TIMEOUT_S} s"
    elif code != 0:
        leg["error"] = leg["stderr_tail"]
    return leg


def fifo_feed(fifo, data, hold_s):
    try:
        with fifo.open("wb") as fh:
            fh.write(data)
            fh.flush()
            time.sleep(hold_s)
    except OSError:
        pass


def reap(fifo):
    needle = str(fifo).encode()
    for pid_dir in Path("/proc").iterdir():
        if not pid_dir.name.isdigit():
            continue
        try:
            cmd = (pid_dir / "cmdline").read_bytes()
        except OSError:
            continue
        if needle in cmd:
            try:
                os.kill(int(pid_dir.name), signal.SIGKILL)
            except OSError:
                pass


def matrix(path, tools=("ffprobe", "ffmpeg")):
    arms = {}
    legs = {"ffprobe": ffprobe_leg, "ffmpeg": ffmpeg_leg}
    # file
    for t in tools:
        arms.setdefault("file", {})[t] = legs[t](str(path))
    # stdin_pipe
    data = path.read_bytes()
    for t in tools:
        arms.setdefault("stdin_pipe", {})[t] = legs[t]("pipe:0", data=data)
    # redirected_fd (seekable fd as stdin)
    with path.open("rb") as fh:
        for t in tools:
            arms.setdefault("redirected_fd", {})[t] = legs[t]("pipe:0", stdin=fh)
    # fifo_path
    with tempfile.TemporaryDirectory(prefix="r71-scout-fifo-") as tmp:
        fifo = Path(tmp) / path.name
        os.mkfifo(fifo)
        writer = threading.Thread(target=fifo_feed, args=(fifo, data, HOLD_S), daemon=True)
        writer.start()
        try:
            for t in tools:
                arms.setdefault("fifo_path", {})[t] = legs[t](str(fifo))
        finally:
            writer.join(timeout=HOLD_S + 5)
            reap(fifo)
    return arms


def verdict(leg):
    if leg["tool"] == "ffprobe":
        if leg["format_name"]:
            return f"probe:{leg['format_name']}@{leg['probe_score']}"
        return f"reject:{leg['error']}"
    if leg["exit_code"] == 0:
        return "decode:ok"
    return f"reject:{leg['error']}"


def main():
    members = {**ARTIFACT_MEMBERS, **TRANSPORT_MEMBERS}
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    out = {"protocol": {"timeout_s": TIMEOUT_S, "fifo_writer_hold_s": HOLD_S,
                        "ffprobe": "ffprobe -v error -show_format -of json <input>",
                        "ffmpeg": "ffmpeg -v error -i <input> -f null -",
                        "anonymous_input": "pipe:0"},
           "members": {}}
    for name, path in members.items():
        if only and name not in only:
            continue
        if not path.exists():
            out["members"][name] = {"path": str(path.relative_to(ROOT)), "missing": True}
            continue
        arms = matrix(path)
        out["members"][name] = {
            "path": str(path.relative_to(ROOT)),
            "arms": arms,
            "verdicts": {t: {tool: verdict(leg) for tool, leg in arms[t].items()}
                         for t in arms},
        }
        print(f"== {name} ({path.name})", file=sys.stderr)
        for t, vs in out["members"][name]["verdicts"].items():
            print(f"   {t:14s} ffprobe={vs.get('ffprobe')}  ffmpeg={vs.get('ffmpeg')}", file=sys.stderr)
    (OUT / "ffprobe_matrix.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
