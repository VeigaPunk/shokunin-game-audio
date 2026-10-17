#!/usr/bin/env python3
"""r75 CRITIC counterexample probes — attack the landed db46fba arm.

Leaf-seat discipline: writes only under corpus/live/r75-critic/; no git
mutation; no subagents; every fifo-adjacent arm bounded (own subprocess
timeouts + killpg escalation, outer run under `timeout -s KILL`).

Sections
  P1 kill-ladder : writerless-fifo TERM ladder (up to 3 TERMs, 1.0 s each)
                   per consumer. Tests the landed `sigterm_immune` field
                   semantics (one-TERM artifact vs true immunity).
  P2 vacuity     : the LANDED consumer2_transport_entry(dec_act) re-run under
                   a live vs dead PULSE_SERVER. Tests whether the
                   transport-invariance verdict can be vacuously true when the
                   paplay daemon gate fails (all arms collapse to one key).
  P3 name-axis   : paplay on identical no-magic bytes under
                   {.snd,.au,.wav,.bin,.SND} (file+fifo) and on WAV content
                   under {.snd,.au,.bin} — closes the landed control's .au hole
                   and measures the 'content wins' positive the landed ops row
                   does not carry. Plus aplay file-arm .au.
  P4 tail-scrub  : the landed scrubber + racy-line regexes vs synthetic and
                   real tails; witness-destruction and latent holes; scan of
                   the committed receipt's 121 tails.
  P5 receipt     : re-audit of the committed r75 receipt (groups, failures,
                   racy leaf classes, path tokens).
"""
import hashlib
import importlib.util
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = Path(__file__).resolve().parent
FIXTURE = ROOT / "corpus/fixtures/measure_audio.py"
RECEIPT = ROOT / "corpus/live/runs/20261014T165017429491Z-consumers2-r75/measurements.json"
ARM_TIMEOUT_S = 15.0
NOWRITER_WAIT_S = 3.0
TERM_WAIT_S = 1.0
FIFO_HOLD_S = 1.0
FFPLAY_ENV = {"SDL_AUDIODRIVER": "dummy"}


def load_fixture():
    spec = importlib.util.spec_from_file_location("measure_audio_landed", FIXTURE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


# ---------------------------------------------------------------- P1 ladder

def term_ladder(argv, env_extra=None, name="cell"):
    """Writerless fifo; sample wchan; TERM xN (1.0 s windows); KILLPG."""
    with tempfile.TemporaryDirectory(prefix="r75critic-ladder-") as tmp:
        fifo = Path(tmp) / "nowriter.wav"
        os.mkfifo(fifo)
        env = {**os.environ, **(env_extra or {})}
        proc = subprocess.Popen(argv + [str(fifo)], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env,
                                start_new_session=True)
        rec = {"cell": name, "argv": " ".join(argv + ["<fifo>"]),
               "env_extra": env_extra or {}, "term_waits_s": TERM_WAIT_S}
        try:
            proc.wait(timeout=NOWRITER_WAIT_S)
            rec.update({"blocked": False, "exit_code": proc.returncode})
            return rec
        except subprocess.TimeoutExpired:
            rec["blocked"] = True
        try:
            rec["wchan"] = Path(f"/proc/{proc.pid}/wchan").read_text().strip()
        except OSError:
            rec["wchan"] = None
        ladder = []
        for n in (1, 2, 3):
            try:
                proc.send_signal(signal.SIGTERM)
            except ProcessLookupError:
                ladder.append({"term_n": n, "send": "process gone"})
                break
            t0 = time.monotonic()
            try:
                proc.wait(timeout=TERM_WAIT_S)
                ladder.append({"term_n": n, "died": True,
                               "exit_code": proc.returncode,
                               "after_s": round(time.monotonic() - t0, 3)})
                break
            except subprocess.TimeoutExpired:
                ladder.append({"term_n": n, "died": False,
                               "alive_after_s": TERM_WAIT_S})
        if proc.poll() is None:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
            ladder.append({"escalation": "killpg SIGKILL",
                           "exit_code": proc.returncode})
        rec["term_ladder"] = ladder
        try:
            err = proc.stderr.read().decode(errors="replace").strip()
        except Exception:
            err = ""
        if err:
            rec["stderr_tail"] = err.splitlines()[-1][-160:]
        rec["survived_term1"] = not ladder[0].get("died", False)
        rec["killed_by_term2"] = (len(ladder) > 1 and ladder[0].get("died") is False
                                  and ladder[1].get("died") is True)
        rec["survived_all_terms"] = all(not e.get("died", True) for e in ladder
                                        if "term_n" in e)
        rec["exit_code"] = proc.returncode
        return rec


def p1_kill_ladder():
    cells = [
        term_ladder(["paplay"], name="paplay"),
        term_ladder(["aplay", "-D", "null"], name="aplay -D null"),
        term_ladder(["ffplay", "-nodisp", "-autoexit", "-v", "info"],
                    env_extra=FFPLAY_ENV, name="ffplay"),
        term_ladder(["pw-cat", "-p"], name="pw-cat -p (contrast)"),
    ]
    return {"probe": "P1 writerless-fifo TERM ladder (3 x 1.0 s)",
            "prediction_landed": {
                "paplay": "dies on TERM1 -> -15 (sigterm_immune False)",
                "aplay": "sigterm_immune True, -9 (landed field)",
                "ffplay": "TERM1 -> graceful 123 (sigterm_immune False)"},
            "cells": cells}


# ---------------------------------------------------------------- P2 vacuity

def _paplay_sig(leg):
    return [leg["exit_code"], leg["pa_sample_spec"], leg["pa_error"]]


def p2_vacuity():
    mod = load_fixture()
    directory, filename = mod.TRANSPORT_R67_MEMBERS["dec_act"]
    path = mod.ROOT / "live" / directory / filename
    arms = {}
    old = os.environ.get("PULSE_SERVER")
    try:
        for arm, env_val in (("live", None),
                             ("dead_pulse_server",
                              "unix:/nonexistent-r75-critic-gate")):
            if env_val is None:
                os.environ.pop("PULSE_SERVER", None)
            else:
                os.environ["PULSE_SERVER"] = env_val
            entry = mod.consumer2_transport_entry("dec_act", path)
            pa = entry["consumers"]["paplay"]
            sigs = {t: _paplay_sig(pa["transport_axis"][t])
                    for t in ("file", "stdin_pipe", "redirected_fd",
                              "fifo_path")}
            arms[arm] = {
                "env": {"PULSE_SERVER": env_val},
                "paplay_sigs": sigs,
                "paplay_groups": len(pa["transport_verdict_groups"]),
                "paplay_transport_fork": pa["transport_fork"],
                "entry_failures": entry["failures"],
                "entry_all_failures": {
                    c: entry["consumers"][c]["transport_fork"]
                    for c in entry["consumers"]},
                "distinct_paplay_sigs": len({json.dumps(s) for s in
                                             sigs.values()}),
                "collapse_to_one_key": len({json.dumps(s) for s in
                                            sigs.values()}) == 1,
            }
    finally:
        if old is None:
            os.environ.pop("PULSE_SERVER", None)
        else:
            os.environ["PULSE_SERVER"] = old
    live = arms["live"]
    dead = arms["dead_pulse_server"]
    verdict = ("VACUOUS-INVARIANCE CONFIRMED: dead daemon collapses all four "
               "paplay transports to one connect-error key and the entry "
               "still reports transport_fork=False with failures=[]"
               if (dead["collapse_to_one_key"]
                   and not dead["paplay_transport_fork"]
                   and not dead["entry_failures"]
                   and "Connection" in json.dumps(dead["paplay_sigs"]))
               else "not confirmed")
    return {"probe": "P2 transport-invariance vacuity (landed entry re-run)",
            "member": "dec_act", "arms": arms, "verdict": verdict}


# ---------------------------------------------------------------- P3 name

def _run_bounded(argv, env=None, input_bytes=None, stdin=None):
    t0 = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=ARM_TIMEOUT_S,
                              env=env, input=input_bytes, stdin=stdin)
        return proc.returncode, round(time.monotonic() - t0, 3), \
            proc.stderr.decode(errors="replace"), None
    except subprocess.TimeoutExpired as exc:
        return None, round(time.monotonic() - t0, 3), \
            (exc.stderr or b"").decode(errors="replace"), "blocked/killed"


def _paplay_case(argv, mod, env=None, input_bytes=None, stdin=None):
    rc, wall, err, blocked = _run_bounded(argv, env=env,
                                          input_bytes=input_bytes, stdin=stdin)
    spec, perr = mod._paplay_fields(err)
    return {"argv": " ".join(argv), "exit_code": rc, "wall_s": wall,
            "pa_sample_spec": spec, "pa_error": perr, "blocked": blocked}


def _aplay_case(argv, mod, env=None, input_bytes=None):
    rc, wall, err, blocked = _run_bounded(argv, env=env,
                                          input_bytes=input_bytes)
    (kind, spec), aerr = mod._aplay_fields(err)
    return {"argv": " ".join(argv), "exit_code": rc, "wall_s": wall,
            "alsa_kind": kind, "alsa_spec": spec, "alsa_error": aerr,
            "blocked": blocked}


def _fifo_case(argv, data, mod, name, env=None):
    with tempfile.TemporaryDirectory(prefix="r75critic-name-") as tmp:
        fifo = Path(tmp) / name
        os.mkfifo(fifo)
        def feed():
            try:
                with open(fifo, "wb") as fh:
                    fh.write(data)
                    fh.flush()
                    time.sleep(FIFO_HOLD_S)
            except OSError:
                pass
        w = threading.Thread(target=feed, daemon=True)
        w.start()
        try:
            return _run_bounded(argv + [str(fifo)], env=env)
        finally:
            w.join(timeout=FIFO_HOLD_S + 5)
            mod.reap_fifo_orphans(fifo)


def p3_name_axis():
    mod = load_fixture()
    nomagic = (ROOT / "corpus/live/round-69/extsuffix_nomatch.snd").read_bytes()
    wav = (ROOT / "corpus/live/round-66/pair_dec_act.wav").read_bytes()
    out = {"probe": "P3 paplay/aplay name axis + content-wins positive",
           "member_nomagic_sha256": hashlib.sha256(nomagic).hexdigest(),
           "member_wav_sha256": hashlib.sha256(wav).hexdigest(),
           "paplay_file_nomagic": {}, "paplay_file_wavcontent": {},
           "paplay_fifo_nomagic": {}, "paplay_fifo_wavcontent": {},
           "paplay_rfd_nomagic": None, "paplay_raw_bypass": None,
           "aplay_file_nomagic": {}, "aplay_file_wavcontent": {}}
    with tempfile.TemporaryDirectory(prefix="r75critic-axis-") as tmp:
        tmp = Path(tmp)
        for ext in ("snd", "au", "wav", "bin", "SND", "au2"):
            p = tmp / f"axis.{ext}"
            p.write_bytes(nomagic)
            out["paplay_file_nomagic"][f".{ext}"] = _paplay_case(
                ["paplay", "-v", str(p)], mod)
        for ext in ("snd", "au", "bin"):
            p = tmp / f"wavc.{ext}"
            p.write_bytes(wav)
            out["paplay_file_wavcontent"][f".{ext}"] = _paplay_case(
                ["paplay", "-v", str(p)], mod)
            out["aplay_file_wavcontent"][f".{ext}"] = _aplay_case(
                ["aplay", "-D", "null", str(p)], mod)
        # aplay on no-magic bytes under .snd/.au (extends the landed fifo-only set)
        for ext in ("snd", "au"):
            p = tmp / f"rawc.{ext}"
            p.write_bytes(nomagic)
            out["aplay_file_nomagic"][f"nomagic-.{ext}"] = _aplay_case(
                ["aplay", "-D", "null", str(p)], mod)
        for ext in ("snd", "au"):
            rc, wall, err, blocked = _fifo_case(["paplay", "-v"], nomagic, mod,
                                                f"axis.{ext}")
            spec, perr = mod._paplay_fields(err)
            out["paplay_fifo_nomagic"][f".{ext}"] = {
                "exit_code": rc, "wall_s": wall, "pa_sample_spec": spec,
                "pa_error": perr, "blocked": blocked}
        rc, wall, err, blocked = _fifo_case(["paplay", "-v"], wav, mod,
                                            "wavc.snd")
        spec, perr = mod._paplay_fields(err)
        out["paplay_fifo_wavcontent"][".snd"] = {
            "exit_code": rc, "wall_s": wall, "pa_sample_spec": spec,
            "pa_error": perr, "blocked": blocked}
        rc, wall, err, blocked = _fifo_case(["paplay", "-v", "--raw"], nomagic,
                                            mod, "axis.snd")
        spec, perr = mod._paplay_fields(err)
        out["paplay_raw_bypass"] = {"exit_code": rc, "pa_error": perr,
                                    "blocked": blocked}
        # rfd: no-magic bytes through a redirected fd
        p = tmp / "axis.rfd"
        p.write_bytes(nomagic)
        with p.open("rb") as fh:
            out["paplay_rfd_nomagic"] = _paplay_case(["paplay", "-v"], mod,
                                                     stdin=fh)
    # verdicts
    file_nm = out["paplay_file_nomagic"]
    file_wc = out["paplay_file_wavcontent"]
    fifo_nm = out["paplay_fifo_nomagic"]
    fifo_wc = out["paplay_fifo_wavcontent"]
    out["verdicts"] = {
        "name_blind_all_reject": all(v["exit_code"] == 1 for v in
                                     list(file_nm.values()) +
                                     list(fifo_nm.values()) +
                                     [out["paplay_rfd_nomagic"]]),
        "au_reject": file_nm[".au"]["exit_code"] == 1,
        "content_wins_file": all(v["exit_code"] == 0 and
                                 v["pa_sample_spec"] for v in file_wc.values()),
        "content_wins_fifo": fifo_wc[".snd"]["exit_code"] == 0,
        "raw_bypass_rc0": out["paplay_raw_bypass"]["exit_code"] == 0,
        "aplay_au_accept_raw": (out["aplay_file_nomagic"]["nomagic-.au"]
                                ["alsa_kind"] == "raw data"),
    }
    return out


# ---------------------------------------------------------------- P4 tails

def p4_tail_scrub():
    mod = load_fixture()
    cases = {
        "pacat_racy_match_real_line": bool(mod._PACAT_RACY_TAIL.match(
            "Time: 0.040 sec; Latency: 159959 usec.")),
        "pacat_racy_match_truncated": bool(mod._PACAT_RACY_TAIL.match(
            "Time: 0.040 sec; Latency:")),
        "pacat_racy_match_drain": bool(mod._PACAT_RACY_TAIL.match(
            "Draining connection to server.")),
        "pacat_racy_match_spec": bool(mod._PACAT_RACY_TAIL.match(
            "Using sample spec 's16le 1ch 8000Hz'")),
        "ffplay_status_filter_nan_fragment": bool(
            mod._FFPLAY_STATUS_TAIL.search(
                "    nan    :  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B")),
        "ffplay_status_filter_detects": bool(
            mod._FFPLAY_STATUS_TAIL.search(
                "   3.87 M-A:  0.000 fd=   0 aq=    0KB vq=    0KB sq=    0B")),
    }
    synthetic = {
        "spec_line": mod._consumer2_tail(
            "Using sample spec 's16le 1ch 8000Hz'", "-"),
        "aplay_quoted_abs_path": mod._consumer2_tail(
            "Playing WAVE '/tmp/aplay-r75-x/axis.snd' : Signed 16 bit", "axis.snd"),
        "aplay_quoted_abs_path_spaced": mod._consumer2_tail(
            "Playing WAVE '/tmp/a b/x.wav' : Signed 16 bit", "x.wav"),
        "ffplay_unquoted_abs_path": mod._consumer2_tail(
            "/tmp/ffplay-r75-x/pair_dec_act.wav: Invalid data found", "pair_dec_act.wav"),
        "ffplay_unquoted_abs_path_spaced": mod._consumer2_tail(
            "/tmp/a b/x.wav: Invalid data found", "x.wav"),
        "ffplay_dev_stdin": mod._consumer2_tail(
            "Input #0, wav, from '/dev/stdin':", "-"),
    }
    # receipt scan
    d = json.loads(RECEIPT.read_text())

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                yield from walk(v, path + "/" + k)
        elif isinstance(o, list):
            for i, v in enumerate(o):
                yield from walk(v, path + f"[{i}]")
        else:
            yield path, o

    tails = [(k, v) for k, v in walk(d) if k.endswith("stderr_tail")]
    racy = [(k, v) for k, v in tails
            if re.match(r"^Time: .*Latency:", v or "") or
            "nan" in (v or "") or v.startswith("ALSA lib")]
    hostpaths = [(k, v) for k, v in tails
                 if "/home/" in (v or "") or "/tmp/" in (v or "")]
    return {"probe": "P4 tail scrub / racy-line filter audit",
            "regex_cases": cases, "synthetic": synthetic,
            "receipt": {
                "path": str(RECEIPT.relative_to(ROOT)),
                "sha256": sha256(RECEIPT),
                "tails": len(tails),
                "racy_tail_leaves": len(racy),
                "racy_tail_sample": [[k, v] for k, v in racy[:6]],
                "hostpath_tails": len(hostpaths),
                "witness_destroyed_spec_line": synthetic["spec_line"],
            }}


# ---------------------------------------------------------------- P5 receipt

def p5_receipt_audit():
    d = json.loads(RECEIPT.read_text())
    m = d["measurements"]
    members = [k for k in m if re.match(r"consumer2_(?!.*ops).*_r75_probe$", k)]
    groups = 0
    forks = []
    fails = []
    for k in members:
        for c, cv in m[k]["consumers"].items():
            groups += len(cv["transport_verdict_groups"])
            if cv["transport_fork"]:
                forks.append([k, c])
        fails += [[k, f] for f in m[k]["failures"]]
    for k in (k for k in m if "ops_r75_probe" in k):
        fails += [[k, f] for f in m[k]["failures"]]
    # committed family identity
    fam = sorted((ROOT / "corpus/live/runs").glob("*consumers2-r75"))
    shas = {p.name: sha256(p / "measurements.json") for p in fam}
    return {"probe": "P5 committed receipt audit",
            "receipt": str(RECEIPT.relative_to(ROOT)),
            "member_entries": len(members),
            "verdict_groups": groups,
            "expected_groups": len(members) * 3,
            "forks": forks,
            "entry_failures": fails,
            "family": shas,
            "family_distinct_shas": len(set(shas.values())),
            "top_level_has_failures_key": "failures" in d}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("all", "p1"):
        results["P1"] = p1_kill_ladder()
    if which in ("all", "p2"):
        results["P2"] = p2_vacuity()
    if which in ("all", "p3"):
        results["P3"] = p3_name_axis()
    if which in ("all", "p4"):
        results["P4"] = p4_tail_scrub()
    if which in ("all", "p5"):
        results["P5"] = p5_receipt_audit()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    out = OUT / f"{stamp}-critic-probes-r75-{which}.json"
    out.write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps({"receipt": str(out.relative_to(ROOT)),
                      "sections": list(results),
                      "verdicts": {k: v.get("verdicts", v.get("verdict"))
                                   for k, v in results.items()}},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
