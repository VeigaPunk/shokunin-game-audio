#!/usr/bin/env python3
"""Probe B — pw-link consumption lattice (the honest producer witness).

Questions:
 1. --target 0: are ports published while unlinked? Does a manual pw-link
    then start the capture (and does -n still bind)?
 2. pw-link -d mid-run: does the file stall, produce silence, or error?
    Distinguish from r77 `sustained_after_target_loss` (node destroyed).
 3. Single-channel pin (FL only): FR channel content?
 4. Can two producers feed one input port (mixing)?
 5. Refusal classes: bogus port, wrong direction, duplicate link.
"""
import json
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78_probe import (SEAT, SCRATCH, M_NS, NS, LINE, sh, load_ns, unload_ns,
                       gen_tone, inspect, audio_stats, payload_sha, out_kind,
                       errclass, norm_err, pwlink_map, mk, emit, du)


def fsize(p):
    try:
        return os.path.getsize(p)
    except OSError:
        return None


def pwlink(*args, timeout=6):
    return sh(["pw-link"] + list(args), timeout=timeout)


def ports_of(node="r78b"):
    rc, so, _se, _w, _t = sh(["pw-link", "-i"], timeout=6)
    txt = so.decode(errors="replace")
    return [ln.strip() for ln in txt.splitlines() if node in ln]


def main():
    tmp = mk()
    tone = gen_tone(os.path.join(tmp, "tone6.wav"), secs=6.0)
    idx, note = load_ns()
    res = {"ns_module": idx, "ns_note": note, "cases": {}}
    if idx is None:
        emit(res, "probe-pwlink-r78.json")
        return
    try:
        # ---- CASE 1: --target 0 manual pin -----------------------------
        out = os.path.join(tmp, "t0.wav")
        argv = ["pw-record", "-P", "node.name=r78b",
                "-P", "stream.capture.sink=true", "--target", "0",
                "-n", "192000", out]
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
        time.sleep(1.0)
        ports_unlinked = ports_of()
        sz_at_1s = fsize(out)
        links_at_1s = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        # manual pin: r78_ns monitor FL/FR -> r78b input FL/FR
        l1 = pwlink("r78_ns:monitor_FL", "r78b:input_FL")
        l2 = pwlink("r78_ns:monitor_FR", "r78b:input_FR")
        time.sleep(1.2)
        sz_after_pin = fsize(out)
        links_after = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        prc = p.wait(timeout=10)
        se = p.stderr.read().decode(errors="replace")
        try:
            play.wait(timeout=6)
        except subprocess.TimeoutExpired:
            play.kill()
        insp = inspect(out)
        st = audio_stats(out)
        res["cases"]["target0_manual_pin"] = {
            "argv": argv, "ports_while_unlinked": ports_unlinked,
            "links_while_unlinked": links_at_1s,
            "sz_at_1s_unlinked": sz_at_1s, "sz_at_2.2s_after_pin":
            sz_after_pin,
            "pin_rc": [l1[0], l2[0]], "pin_err": norm_err(l1[2] + l2[2]),
            "links_after_pin": links_after, "rc": prc,
            "err_class": errclass(se)[0], "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "data_actual": insp.get("data_actual"),
            "riff_size_field": insp.get("riff_size_field"),
            "peak": st.get("peak"), "nz_frac": st.get("nz_frac")}

        # ---- CASE 2: pw-link -d mid-run --------------------------------
        out = os.path.join(tmp, "disc.wav")
        argv = ["pw-record", "-P", "node.name=r78b",
                "-P", "stream.capture.sink=true", "--target", NS,
                "-n", "240000", out]
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
        time.sleep(1.5)
        sz_pre = fsize(out)
        # disconnect both links
        d1 = pwlink("-d", "r78_ns:monitor_FL", "r78b:input_FL")
        d2 = pwlink("-d", "r78_ns:monitor_FR", "r78b:input_FR")
        time.sleep(0.2)
        sz_d0 = fsize(out)
        time.sleep(1.0)
        sz_d1 = fsize(out)
        links_disc = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        # re-link
        r1 = pwlink("r78_ns:monitor_FL", "r78b:input_FL")
        r2 = pwlink("r78_ns:monitor_FR", "r78b:input_FR")
        time.sleep(1.2)
        sz_rel = fsize(out)
        links_rel = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        if p.poll() is None:
            p.send_signal(signal.SIGTERM)
        prc = p.wait(timeout=5)
        se = p.stderr.read().decode(errors="replace")
        try:
            play.wait(timeout=6)
        except subprocess.TimeoutExpired:
            play.kill()
        insp = inspect(out)
        res["cases"]["disconnect_midrun"] = {
            "sz_pre_disc_1.5s": sz_pre,
            "disc_rc": [d1[0], d2[0]], "disc_err": norm_err(d1[2] + d2[2]),
            "sz_just_after_disc": sz_d0, "sz_1s_while_disc": sz_d1,
            "growth_while_disc": (None if sz_d1 is None or sz_d0 is None
                                  else sz_d1 - sz_d0),
            "links_while_disc": links_disc,
            "relink_rc": [r1[0], r2[0]],
            "sz_1.2s_after_relink": sz_rel,
            "growth_after_relink": (None if sz_rel is None or sz_d1 is None
                                    else sz_rel - sz_d1),
            "links_after_relink": links_rel,
            "rc": prc, "err_class": errclass(se)[0],
            "err_line": norm_err(se), "out_kind": out_kind(insp),
            "bytes": insp.get("bytes"),
            "riff_size_field": insp.get("riff_size_field"),
            "data_actual": insp.get("data_actual")}

        # ---- CASE 3: single-channel pin (FL only) ----------------------
        out = os.path.join(tmp, "flonly.wav")
        argv = ["pw-record", "-P", "node.name=r78b",
                "-P", "stream.capture.sink=true", "--target", "0",
                "-n", "48000", out]
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
        time.sleep(0.8)
        l1 = pwlink("r78_ns:monitor_FL", "r78b:input_FL")
        links_fl = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        prc = None
        t0 = time.monotonic()
        while prc is None and time.monotonic() - t0 < 10:
            prc = p.poll()
            time.sleep(0.05)
        if prc is None:
            p.send_signal(signal.SIGTERM)
            prc = p.wait(timeout=4)
        se = p.stderr.read().decode(errors="replace")
        try:
            play.wait(timeout=6)
        except subprocess.TimeoutExpired:
            play.kill()
        insp = inspect(out)
        st = audio_stats(out)
        # channel-split content: read payload, separate L/R peaks
        ch = {}
        try:
            d = open(out, "rb").read()
            off = d.find(b"data")
            pay = d[off + 8:]
            import struct as st2
            n = len(pay) // 4
            pl = [abs(v) for v in st2.unpack(f"<{n*2}h", pay[:n*4])[0::2]]
            pr = [abs(v) for v in st2.unpack(f"<{n*2}h", pay[:n*4])[1::2]]
            ch = {"peak_L": max(pl) if pl else 0,
                  "peak_R": max(pr) if pr else 0}
        except Exception as e:  # noqa: BLE001
            ch = {"err": str(e)[:80]}
        res["cases"]["single_channel_fl"] = {
            "pin_rc": l1[0], "links": links_fl, "rc": prc,
            "err_line": norm_err(se), "out_kind": out_kind(insp),
            "bytes": insp.get("bytes"), "data_actual":
            insp.get("data_actual"), **ch}

        # ---- CASE 4: two producers -> one input port -------------------
        out = os.path.join(tmp, "twoprod.wav")
        argv = ["pw-record", "-P", "node.name=r78b",
                "-P", "stream.capture.sink=true", "--target", "0",
                "-n", "48000", out]
        play = subprocess.Popen(["pw-cat", "-p", "--target", NS, tone],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL)
        time.sleep(0.3)
        p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                             stderr=subprocess.PIPE)
        time.sleep(0.8)
        a = pwlink("r78_ns:monitor_FL", "r78b:input_FL")
        b = pwlink(LINE + ":capture_FL", "r78b:input_FL")
        c = pwlink("r78_ns:monitor_FR", "r78b:input_FR")
        links2 = pwlink_map(sh(["pw-link", "-l"])[1].decode(
            errors="replace"), "r78b:input")
        prc = None
        t0 = time.monotonic()
        while prc is None and time.monotonic() - t0 < 10:
            prc = p.poll()
            time.sleep(0.05)
        if prc is None:
            p.send_signal(signal.SIGTERM)
            prc = p.wait(timeout=4)
        se = p.stderr.read().decode(errors="replace")
        try:
            play.wait(timeout=6)
        except subprocess.TimeoutExpired:
            play.kill()
        insp = inspect(out)
        stt = audio_stats(out)
        res["cases"]["two_producers_one_port"] = {
            "pin_rcs": [a[0], b[0], c[0]],
            "pin_errs": norm_err(a[2] + b[2] + c[2]),
            "links": links2, "rc": prc, "err_line": norm_err(se),
            "out_kind": out_kind(insp), "bytes": insp.get("bytes"),
            "peak": stt.get("peak"), "nz_frac": stt.get("nz_frac")}

        # ---- CASE 5: refusal lattice ------------------------------------
        ref = {}
        for nm, args in (
            ("bogus_out_port", ["no.such:port", "r78b:input_FL"]),
            ("bogus_in_port", ["r78_ns:monitor_FL", "no.such:port"]),
            ("input_to_input", ["r78b:input_FL", "r78b:input_FR"]),
            ("output_to_output", ["r78_ns:monitor_FL",
                                  LINE + ":capture_FL"]),
            ("disconnect_never_linked", ["-d", "r78_ns:monitor_FL",
                                         "no.such:port"]),
        ):
            r = pwlink(*args)
            ref[nm] = {"rc": r[0], "err_class": errclass(r[2])[0],
                       "err_line": norm_err(r[2]), "stdout":
                       r[1].decode(errors="replace").strip()[:160]}
        res["cases"]["refusals"] = ref

        # ---- CASE 6: -m monitor mode shape ------------------------------
        r = sh(["pw-link", "-m", "-l"], timeout=1.5)
        res["cases"]["monitor_mode"] = {"rc": r[0], "timed_out": r[4],
                                        "head": r[1].decode(
                                            errors="replace")[:400]}
    finally:
        unload_ns(idx)
    res["scratch_bytes"] = du()
    emit(res, "probe-pwlink-r78.json")


if __name__ == "__main__":
    main()
