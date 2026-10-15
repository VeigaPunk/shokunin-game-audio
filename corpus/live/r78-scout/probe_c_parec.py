#!/usr/bin/env python3
"""Probe C — parec --file-format / --fix-* / --monitor-stream lattice.

Questions:
 1. Which of the 27 advertised file formats actually write on THIS source,
    what does each header look like, and what are the named refusals?
    (r77: format on non-seekable stdout is a hard fail; here: seekable file)
 2. --fix-format/--fix-rate/--fix-channels: does the delivered header
    reflect the SOURCE spec (s16le/48k monitor vs s24le/48k Line) or the
    requested spec (default 44100 s16ne)? Refusal vs conversion lattice
    vs pw-record's.
 3. --monitor-stream=IDX: captures ONE sink-input pre-mix? and its refusal.
"""
import json
import os
import re
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78_probe import (SEAT, SCRATCH, M_NS, NS, LINE, M_SPDIF, sh, load_ns,
                       unload_ns, gen_tone, inspect, audio_stats, payload_sha,
                       out_kind, errclass, norm_err, mk, emit, du)

FORMATS = ["wav", "aiff", "au", "flac", "oga", "caf", "rf64", "w64", "voc",
           "raw", "pvf", "iff", "mat", "sf", "avr", "htk", "sds", "sd2",
           "mpc", "m1a", "paf", "xi", "wve", "bogus_fmt"]


def parec_file(name, args, tmp, timeout=8, term_after=1.3):
    """parec to a seekable file; TERM after term_after; inspect."""
    out = os.path.join(tmp, name)
    if os.path.exists(out):
        os.unlink(out)
    p = subprocess.Popen(["parec"] + args + [out],
                         stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    t0 = time.monotonic()
    time.sleep(term_after)
    prc = p.poll()
    if prc is None:
        p.send_signal(signal.SIGTERM)
        try:
            prc = p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            p.send_signal(signal.SIGKILL)
            prc = p.wait(timeout=4)
    se = p.stderr.read().decode(errors="replace")
    p.stderr.close()
    insp = inspect(out)
    return {"leg": name, "argv": ["parec"] + args + ["<out>"],
            "rc": prc, "wall_s": round(time.monotonic() - t0, 3),
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "head8": insp.get("head8"), "fmt": insp.get("fmt"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_declared_field": insp.get("data_declared_field")}


def main():
    tmp = mk()
    tone = gen_tone(os.path.join(tmp, "tone.wav"))
    idx, note = load_ns()
    res = {"ns_module": idx, "formats": [], "fix": [], "monstream": [],
           "defaults": []}
    if idx is None:
        emit(res, "probe-parec-format-r78.json")
        return
    try:
        # 1. format lattice on my null-sink monitor (tone playing each leg)
        for fmt in FORMATS:
            play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
            time.sleep(0.25)
            leg = parec_file("fmt_" + fmt,
                             ["-d", M_NS, f"--file-format={fmt}"], tmp)
            try:
                play.wait(timeout=4)
            except subprocess.TimeoutExpired:
                play.kill()
            res["formats"].append(leg)
            print(f"fmt={fmt}: rc={leg['rc']} kind={leg['out_kind']} "
                  f"bytes={leg['bytes']} head={leg['head8']} "
                  f"err={leg['err_line'][:60]}", file=sys.stderr)
        # bare --file-format (no value)
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.25)
        leg = parec_file("fmt_bareflag", ["-d", M_NS, "--file-format"], tmp)
        try:
            play.wait(timeout=4)
        except subprocess.TimeoutExpired:
            play.kill()
        res["formats"].append(leg)

        # 2. fix-* lattice: source spec vs delivered spec.
        #    Line = s24le 2ch 48k; ns monitor = s16le 2ch 48k (module arg)
        for nm, dev, extra in (
            ("mon_default", M_NS, []),
            ("mon_req_44k1", M_NS, ["--rate=44100", "--channels=1"]),
            ("mon_fixrate", M_NS, ["--fix-rate"]),
            ("mon_fixformat", M_NS, ["--fix-format"]),
            ("mon_fixchannels", M_NS, ["--fix-channels"]),
            ("mon_fix_all", M_NS, ["--fix-format", "--fix-rate",
                                   "--fix-channels"]),
            ("mon_fix_all_req", M_NS, ["--rate=44100", "--channels=1",
                                       "--format=s32le", "--fix-format",
                                       "--fix-rate", "--fix-channels"]),
            ("line_default", LINE, []),
            ("line_fix_all", LINE, ["--fix-format", "--fix-rate",
                                    "--fix-channels"]),
            ("line_fixformat", LINE, ["--fix-format"]),
            ("line_noremix_c1", LINE, ["--channels=1", "--no-remix"]),
            ("line_c6", LINE, ["--channels=6"]),
        ):
            leg = parec_file("fix_" + nm,
                             ["-d", dev, "--file-format=wav"] + extra, tmp)
            leg["src"] = dev
            res["fix"].append(leg)
            print(f"fix={nm}: rc={leg['rc']} fmt={leg['fmt']} "
                  f"bytes={leg['bytes']} err={leg['err_line'][:60]}",
                  file=sys.stderr)

        # raw + fix-rate on Line: does raw byte-rate reveal the delivered
        # rate? cap stdout at 1.0s and count.
        from r78_probe import sh_capped
        for nm, extra in (("line_raw_default", []),
                          ("line_raw_fixrate", ["--fix-rate"]),
                          ("line_raw_96k", ["--rate=96000"])):
            rc, n, se, wall, cap, sig, raw = sh_capped(
                ["parec", "-d", LINE, "--raw"] + extra,
                cap=3 * 1024 * 1024, timeout=6, term_after=1.0)
            res["defaults"].append(
                {"leg": nm, "rc": rc, "nbytes_1s": n, "sig": sig,
                 "err_line": norm_err(se)})

        # 3. --monitor-stream: capture one sink-input pre-mix
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        rc, so, _se, _w, _t = sh(["pactl", "list", "sink-inputs", "short"], 8)
        idxs = re.findall(r"^(\d+)\s", so.decode(errors="replace"), re.M)
        res["sink_inputs_seen"] = so.decode(errors="replace").strip()
        # choose the sink-input whose sink is r78_ns
        mine = None
        for ln in so.decode(errors="replace").splitlines():
            cols = ln.split()
            if len(cols) >= 2 and cols[1] == NS:
                mine = cols[0]
        res["my_sink_input_idx"] = mine
        if mine:
            leg = parec_file("monstream_mine",
                             ["-d", NS, f"--monitor-stream={mine}",
                              "--file-format=wav"], tmp)
            st = audio_stats(os.path.join(tmp, "monstream_mine"))
            leg["peak"] = st.get("peak")
            leg["nz_frac"] = st.get("nz_frac")
            res["monstream"].append(leg)
        for nm, dev, midx in (("monstream_bogus", NS, "999999"),
                              ("monstream_0", NS, "0")):
            leg = parec_file(nm,
                             ["-d", dev, f"--monitor-stream={midx}",
                              "--file-format=wav"], tmp)
            res["monstream"].append(leg)
        try:
            play.wait(timeout=4)
        except subprocess.TimeoutExpired:
            play.kill()
    finally:
        unload_ns(idx)
    res["scratch_bytes"] = du()
    emit(res, "probe-parec-format-r78.json")


if __name__ == "__main__":
    main()
