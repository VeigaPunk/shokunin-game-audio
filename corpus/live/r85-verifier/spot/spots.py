#!/usr/bin/env python3
"""r85 verifier — independent spot battery (own code, own r85v_* namespace).

No fixture import. Own tone generation / graph parsing / spectral
amplitude / module bookkeeping. Takes the family flock (same TMPDIR) so
no concurrent pactlmon fixture run can cross-credit the spots.

Spot shapes
  s1  pactl serial-vs-object.id + name equivalence + `0`=live default +
      `""`=Invalid argument
  s2  pw-cli namespace inversion (id resolves / serial -> rc0 lie)
  s3  serial monotonicity + module-index recycle (3 load/unload cycles)
  s4  move-sink-input name/serial/collision (digits-name cannot shadow
      the serial holder)
  s5  mix tap + same-run solo reference (validated monitor tap; solo
      ~8192; 2-stream full-amp zero-bleed; 4 links -> 2 ports)
  s6  aplay -D pipewire env targeting (NODE, PROPS, conflict props-win,
      bogus NODE -> silent default fallback on a SILENCE file)
  s7  capture --target lattice (source name/serial -> capture_*; sink
      serial noprop -> monitor_*; sink name noprop -> never monitor_*;
      prop -> default monitor)
  s8  loss law (name-verified remap unload mid-record: links die, never
      re-form, alive, growth ceases, bounded flush)
  s9  Audio/Source self-destruct (idle survives; pw-record bind kills
      module+node <=1.5 s)
  s10 live negative controls (pa_invalid_arg shape, rc-0 unknown-global,
      clean controls, SIGKILL discriminator)
"""
import fcntl
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path

import numpy as np

PID = os.getpid()
P = f"r85v_{PID}"
TMP = Path(tempfile.gettempdir())
LOCK = TMP / "measure_audio-pactlmon-r85.lock"
TONE_AMP = 8192
SOLO_ENV = (0.85, 1.18)
BLEED_MAX = 0.05
FLUSH_BOUND = 16384
RECORDS = []


def rec(spot, ok, detail, **kw):
    r = {"spot": spot, "ok": bool(ok), "detail": detail, **kw}
    RECORDS.append(r)
    print(json.dumps(r, default=str)[:2000], flush=True)
    return r


def run(argv, timeout=10.0, env=None, stdin=subprocess.DEVNULL):
    try:
        p = subprocess.Popen(argv, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, stdin=stdin,
                             env=env, start_new_session=True)
    except OSError as exc:
        return {"argv": " ".join(map(str, argv)), "spawn_error": str(exc)}
    try:
        out, err = p.communicate(timeout=timeout)
        killed = False
    except subprocess.TimeoutExpired:
        killed = True
        try:
            os.killpg(p.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = p.communicate()
    return {"argv": " ".join(map(str, argv)), "exit_code": p.returncode,
            "killed": killed,
            "stdout": out.decode(errors="replace"),
            "stderr": err.decode(errors="replace")}


def killpg(p, sig=signal.SIGKILL):
    try:
        os.killpg(p.pid, sig)
    except (ProcessLookupError, PermissionError):
        pass


def pactl(*args, timeout=10.0):
    return run(["pactl", *map(str, args)], timeout)


def graph():
    try:
        p = subprocess.run(["pw-dump"], capture_output=True, timeout=20)
        dump = json.loads(p.stdout or b"[]")
    except Exception as exc:                       # noqa: BLE001
        return {"error": type(exc).__name__}
    nodes, ports, links = {}, {}, []
    for o in dump:
        t = str(o.get("type", ""))
        info = o.get("info") or {}
        props = info.get("props") or {}
        if t.endswith("Node"):
            nodes[o["id"]] = {"name": props.get("node.name"),
                              "media_class": props.get("media.class"),
                              "serial": props.get("object.serial"),
                              "oid": props.get("object.id"),
                              "target_object": props.get("target.object"),
                              "state": info.get("state")}
        elif t.endswith("Port"):
            ports[o["id"]] = {"node": info.get("node-id")
                              or props.get("node.id"),
                              "name": props.get("port.name")}
        elif t.endswith("Link"):
            links.append({"out_node": info.get("output-node-id"),
                          "out_port": info.get("output-port-id"),
                          "in_node": info.get("input-node-id"),
                          "in_port": info.get("input-port-id")})
    return {"nodes": nodes, "ports": ports, "links": links}


def node(g, name):
    for nid, n in (g.get("nodes") or {}).items():
        if n.get("name") == name:
            return {"id": nid, **n}
    return None


def edges_in(g, node_name):
    out = []
    nodes, ports = g.get("nodes", {}), g.get("ports", {})
    for l in g.get("links", []):
        if (nodes.get(l["in_node"]) or {}).get("name") == node_name:
            out.append({
                "out_node": (nodes.get(l["out_node"]) or {}).get("name"),
                "out_port": (ports.get(l["out_port"]) or {}).get("name"),
                "in_port": (ports.get(l["in_port"]) or {}).get("name")})
    return out


def module_index(field, value):
    p = subprocess.run(["pactl", "list", "modules", "short"],
                       capture_output=True, timeout=15)
    for ln in p.stdout.decode(errors="replace").splitlines():
        f = ln.split("\t")
        if not (f and f[0].strip().isdigit()):
            continue
        m = re.search(re.escape(field) + r"=(\S+)", ln)
        if m and m.group(1).strip("\"'") == value:
            return int(f[0].strip())
    return None


def unload_own(module_id, field, value):
    idx = module_index(field, value)
    if idx is None:
        return {"skipped": "not_listed"}
    p = subprocess.run(["pactl", "unload-module", str(idx)],
                       capture_output=True, timeout=15)
    return {"verified_index": idx, "captured": module_id,
            "recycled": module_id is not None and idx != module_id,
            "exit_code": p.returncode}


def load_null_sink(name, media_class=None):
    argv = ["pactl", "load-module", "module-null-sink", f"sink_name={name}"]
    if media_class:
        argv.append(f"media.class={media_class}")
    p = subprocess.run(argv, capture_output=True, timeout=15)
    mid = p.stdout.decode(errors="replace").strip()
    mid = int(mid) if mid.isdigit() else None
    t0 = time.monotonic()
    seen = None
    while time.monotonic() - t0 < 6.0:
        seen = node(graph(), name)
        if seen:
            break
        time.sleep(0.1)
    return {"module_id": mid, "rc": p.returncode,
            "node": seen, "waited_s": round(time.monotonic() - t0, 3)}


def load_remap(master_monitor, source_name):
    p = subprocess.run(
        ["pactl", "load-module", "module-remap-source",
         f"master={master_monitor}", f"source_name={source_name}"],
        capture_output=True, timeout=15)
    mid = p.stdout.decode(errors="replace").strip()
    mid = int(mid) if mid.isdigit() else None
    t0 = time.monotonic()
    n = None
    while time.monotonic() - t0 < 6.0:
        g = graph()
        n = node(g, source_name)
        if n and edges_in(g, source_name) is not None:
            break
        time.sleep(0.1)
    return {"module_id": mid, "node": n,
            "waited_s": round(time.monotonic() - t0, 3)}


def tone(path, secs, lhz, rhz, amp=TONE_AMP):
    n = int(48000 * secs)
    t = np.arange(n) / 48000
    left = (amp * np.sin(2 * np.pi * lhz * t)).astype("<i2")
    right = (amp * np.sin(2 * np.pi * rhz * t)).astype("<i2")
    pcm = np.empty(n * 2, dtype="<i2")
    pcm[0::2], pcm[1::2] = left, right
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(48000)
        w.writeframes(pcm.tobytes())


def play(tag, target, tone_path):
    return subprocess.Popen(
        ["pw-play", "-P", f"node.name={tag}", "-P",
         f"application.name={tag}", "-P", f"media.role={P}role",
         "--target", str(target), str(tone_path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL, start_new_session=True)


def read_wav(path):
    with wave.open(str(path), "rb") as w:
        rate = w.getframerate()
        ch = w.getnchannels()
        frames = w.readframes(w.getnframes())
    pcm = np.frombuffer(frames, dtype="<i2")
    if ch == 2:
        pcm = pcm.reshape(-1, 2)
    return rate, pcm


def amp_at(x, rate, f):
    n = len(x)
    if n < 64:
        return 0.0
    w = np.hanning(n)
    t = np.arange(n) / rate
    c = np.sum(x.astype(np.float64) * w * np.exp(-2j * np.pi * f * t))
    return float(2 * np.abs(c) / np.sum(w))


def window_amps(path, freqs, win_s=0.25, skip_s=0.4):
    rate, pcm = read_wav(path)
    n = int(rate * win_s)
    rows = []
    for i in range(int(rate * skip_s), len(pcm) - n + 1, n):
        seg = pcm[i:i + n]
        row = {"at_s": round(i / rate, 2)}
        for k, f in freqs.items():
            row[f"l_{k}"] = round(amp_at(seg[:, 0], rate, f), 1)
            row[f"r_{k}"] = round(amp_at(seg[:, 1], rate, f), 1)
        rows.append(row)
    return rows


def med(rows, key):
    vals = [r[key] for r in rows if key in r]
    return float(np.median(vals)) if vals else None


def tap(sink, path, frames, tag):
    return subprocess.Popen(
        ["pw-record", "-P", f"node.name={tag}", "-P",
         "stream.capture.sink=true", "--target", sink,
         "--rate", "48000", "--channels", "2", "--format", "s16",
         str(path)],
        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL, start_new_session=True)


def wait_tap_link(sink, tag, timeout=6.0):
    t0 = time.monotonic()
    last = []
    while time.monotonic() - t0 < timeout:
        last = edges_in(graph(), tag)
        if last and all((e.get("out_port") or "").startswith("monitor_")
                        for e in last):
            return last, round(time.monotonic() - t0, 2)
        time.sleep(0.1)
    return last, round(time.monotonic() - t0, 2)


def get_vol_pct(r):
    m = re.search(r"(\d+)\s*%", r.get("stdout") or "")
    return int(m.group(1)) if m else None


def main():
    # serialize against concurrent fixture probe runs (same TMPDIR)
    fd = os.open(str(LOCK), os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(fd, fcntl.LOCK_EX)
    os.ftruncate(fd, 0)
    os.write(fd, f"pid={PID} seat=r85-verifier spots\n".encode())
    with tempfile.TemporaryDirectory(prefix="r85v-spot-") as tmp:
        tmp = Path(tmp)
        A = f"{P}_a"
        B = f"{P}_b"
        la = load_null_sink(A)
        lb = load_null_sink(B)
        rec("setup", bool(la["node"] and lb["node"]),
            f"A={la['module_id']} B={lb['module_id']}",
            a_serial=(la["node"] or {}).get("serial"),
            b_serial=(lb["node"] or {}).get("serial"),
            a_id=(la["node"] or {}).get("id"))
        if not (la["node"] and lb["node"]):
            rec("setup", False, "sinks never enumerated")
            return 1
        a_serial = la["node"]["serial"]
        a_id = la["node"]["id"]
        b_serial = lb["node"]["serial"]

        # ---- s1: pactl arg lattice -----------------------------------
        g_name = pactl("get-sink-volume", A)
        g_serial = pactl("get-sink-volume", a_serial)
        g_objid = pactl("get-sink-volume", a_id)
        g_def = pactl("get-sink-volume", "@DEFAULT_SINK@")
        g_zero = pactl("get-sink-volume", "0")
        g_empty = pactl("get-sink-volume", "")
        g_uscr = pactl("get-sink-volume",
                       f"{str(a_serial)[:-3]}_{str(a_serial)[-3:]}")
        ok = (g_name["exit_code"] == 0 and g_serial["exit_code"] == 0
              and get_vol_pct(g_serial) == get_vol_pct(g_name)
              and g_objid["exit_code"] == 1
              and "No such entity" in (g_objid.get("stderr") or "")
              and g_zero["exit_code"] == 0
              and get_vol_pct(g_zero) == get_vol_pct(g_def)
              and g_empty["exit_code"] == 1
              and "Invalid argument" in (g_empty.get("stderr") or "")
              and g_uscr["exit_code"] == 1)
        rec("s1_pactl_serial_lattice", ok,
            f"name_rc={g_name['exit_code']} ser_rc={g_serial['exit_code']} "
            f"ser_pct={get_vol_pct(g_serial)} name_pct={get_vol_pct(g_name)} "
            f"objid_rc={g_objid['exit_code']} zero_pct={get_vol_pct(g_zero)} "
            f"def_pct={get_vol_pct(g_def)} empty={g_empty.get('stderr','').strip()[:60]}",
            uscr_rc=g_uscr["exit_code"])

        # ---- s2: pw-cli inversion ------------------------------------
        p_id = run(["pw-cli", "info", str(a_id)])
        p_ser = run(["pw-cli", "info", str(a_serial)])
        blob = (p_ser.get("stderr") or "") + (p_ser.get("stdout") or "")
        ok = (p_id["exit_code"] == 0 and str(a_id) in p_id["stdout"]
              and p_ser["exit_code"] == 0 and "unknown global" in blob)
        rec("s2_pwcli_inversion", ok,
            f"id_rc={p_id['exit_code']} serial_rc={p_ser['exit_code']} "
            f"lie={'unknown global' in blob}")

        # ---- s3: serial monotonicity + index recycle -----------------
        ser, mods = [], []
        C = f"{P}_cyc"
        for _ in range(3):
            lc = load_null_sink(C)
            ser.append((lc["node"] or {}).get("serial"))
            mods.append(lc["module_id"])
            unload_own(lc["module_id"], "sink_name", C)
        ok = (len(ser) == 3 and all(isinstance(s, int) for s in ser)
              and ser == sorted(ser) and len(set(ser)) == 3)
        rec("s3_serial_monotonic", ok, f"serials={ser}", module_indices=mods)

        # ---- s4: move-sink-input + collision -------------------------
        tA = tmp / "tA.wav"
        tone(tA, 9.0, 1000, 2500)   # outlives both moves + the digits load
        tag = f"{P}_mv"
        pl = play(tag, A, tA)
        time.sleep(1.0)

        def stream_sink():
            p = subprocess.run(["pactl", "list", "sink-inputs"],
                               capture_output=True, timeout=10)
            for blk in p.stdout.decode(errors="replace").split("\n\n"):
                if tag in blk:
                    m = re.search(r"Sink:\s*(\d+)", blk)
                    return int(m.group(1)) if m else None
            return None

        def stream_index():
            p = subprocess.run(["pactl", "list", "sink-inputs"],
                               capture_output=True, timeout=10)
            for blk in p.stdout.decode(errors="replace").split("\n\n"):
                if tag in blk:
                    m = re.search(r"Sink Input #(\d+)", blk)
                    return m.group(1) if m else None
            return None

        st_idx = stream_index()
        p = subprocess.run(["pactl", "list", "short", "sinks"],
                           capture_output=True, timeout=10)
        idx = {}
        for ln in p.stdout.decode(errors="replace").splitlines():
            f = ln.split("\t")
            if len(f) > 1:
                idx[f[1]] = int(f[0])
        cur0 = stream_sink()
        mv_name = pactl("move-sink-input", st_idx, B) if st_idx else {"exit_code": None}
        time.sleep(0.8)
        cur1 = stream_sink()
        # load a sink NAMED with A's serial, then move to the digits
        dup = load_null_sink(str(a_serial))
        p = subprocess.run(["pactl", "list", "short", "sinks"],
                           capture_output=True, timeout=10)
        idx2 = {}
        for ln in p.stdout.decode(errors="replace").splitlines():
            f = ln.split("\t")
            if len(f) > 1:
                idx2[f[1]] = int(f[0])
        named_idx = idx2.get(str(a_serial))
        # the digits-named sink is proven by its pactl index + module id
        # (the pw-dump node lookup is redundant and can race enumeration)
        named_alive = (dup.get("module_id") is not None
                       and named_idx is not None
                       and named_idx != idx.get(A))
        mv_digits = pactl("move-sink-input", st_idx, str(a_serial)) if st_idx else {"exit_code": None}
        time.sleep(0.8)
        cur2 = stream_sink()
        ok = (st_idx is not None and cur0 == idx.get(A)
              and mv_name.get("exit_code") == 0 and cur1 == idx.get(B)
              and named_alive
              and mv_digits.get("exit_code") == 0 and cur2 == idx.get(A)
              and named_idx != idx.get(A))
        rec("s4_move_collision", bool(ok),
            f"stream={st_idx} cur={cur0}->{cur1}->{cur2} "
            f"holder_idx={idx.get(A)} b_idx={idx.get(B)} "
            f"named_idx={named_idx} named_alive={named_alive} "
            f"name_move_rc={mv_name.get('exit_code')} "
            f"digits_move_rc={mv_digits.get('exit_code')}",
            digits_name=str(a_serial),
            dup_module=dup.get("module_id"))
        killpg(pl)
        pl.wait()
        unload_own(dup["module_id"], "sink_name", str(a_serial))

        # ---- s5: mix tap + solo reference ----------------------------
        M = f"{P}_mix"
        lm = load_null_sink(M)
        t1 = tmp / "t1.wav"
        t2 = tmp / "t2.wav"
        tone(t1, 4.5, 1000, 2500)
        tone(t2, 4.5, 2711, 3214)
        tapp = tmp / "mix_tap.wav"
        ttag = f"{P}_mixtap"
        tap_p = tap(M, tapp, int(48000 * 5.5), ttag)
        tlinks, waited = wait_tap_link(M, ttag)
        p1 = play(f"{P}_p1", M, t1)
        time.sleep(0.4)
        p2 = play(f"{P}_p2", M, t2)
        time.sleep(2.6)
        g = graph()
        mix_edges = [e for e in edges_in(g, M)
                     if (e.get("in_port") or "").startswith("playback_")]
        killpg(tap_p, signal.SIGTERM)
        try:
            tap_p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            killpg(tap_p)
            tap_p.wait()
        killpg(p1)
        killpg(p2)
        p1.wait()
        p2.wait()
        rows = window_amps(tapp, {"a": 1000, "b": 2500, "c": 2711,
                                  "d": 3214})
        la_, rb = med(rows, "l_a"), med(rows, "r_b")
        lc, rd = med(rows, "l_c"), med(rows, "r_d")
        ra, lb_ = med(rows, "r_a"), med(rows, "l_b")
        lo, hi = SOLO_ENV
        ok = (bool(tlinks) and all((e.get("out_port") or "").startswith("monitor_")
                                   for e in tlinks)
              and la_ is not None and lo * TONE_AMP <= la_ <= hi * TONE_AMP
              and rb is not None and lo * TONE_AMP <= rb <= hi * TONE_AMP
              and (ra or 0) <= BLEED_MAX * TONE_AMP
              and (lb_ or 0) <= BLEED_MAX * TONE_AMP
              and lc is not None and lo * TONE_AMP <= lc <= hi * TONE_AMP
              and rd is not None and lo * TONE_AMP <= rd <= hi * TONE_AMP
              and len(mix_edges) == 4
              and len({e.get("in_port") for e in mix_edges}) == 2)
        rec("s5_mix_solo", ok,
            f"tap_links={len(tlinks)} l_a={la_} r_b={rb} l_c={lc} r_d={rd} "
            f"bleed r_a={ra} l_b={lb_} edges={len(mix_edges)}",
            ports=sorted({e.get("in_port") for e in mix_edges}))
        unload_own(lm["module_id"], "sink_name", M)

        # ---- s6: aplay env -------------------------------------------
        sil = tmp / "sil.wav"
        tone(sil, 2.0, 20, 20, amp=0)
        base = {k: v for k, v in os.environ.items()
                if not k.startswith("PIPEWIRE_")}

        def aplay_live(env, path, wait=0.8):
            """Spawn aplay, sample the graph WHILE it plays, then kill."""
            ap = subprocess.Popen(["aplay", "-D", "pipewire", str(path)],
                                  stdout=subprocess.DEVNULL,
                                  stderr=subprocess.PIPE,
                                  stdin=subprocess.DEVNULL, env=env,
                                  start_new_session=True)
            time.sleep(wait)
            g = graph()
            alive = ap.poll() is None
            if alive:
                killpg(ap, signal.SIGTERM)
            try:
                ap.wait(timeout=4)
            except subprocess.TimeoutExpired:
                killpg(ap)
                ap.wait()
            return g, alive, ap.returncode
        g, alive1, rc1 = aplay_live({**base, "PIPEWIRE_NODE": A}, t1)
        hits = [n for n in g["nodes"].values()
                if str(n.get("target_object")) == str(A)]
        g2, alive2, rc2 = aplay_live(
            {**base, "PIPEWIRE_NODE": B,
             "PIPEWIRE_PROPS": "{ target.object=" + A + " }"}, t1)
        hits2 = [n for n in g2["nodes"].values()
                 if str(n.get("target_object")) == str(A)]
        g3, alive3, rc3 = aplay_live(
            {**base, "PIPEWIRE_NODE": "no_such_r85v"}, sil)
        bhit = [n for n in g3["nodes"].values()
                if str(n.get("target_object")) == "no_such_r85v"]
        no_b = not any(str(n.get("target_object")) == str(B)
                       for n in g2["nodes"].values())
        ok = (bool(hits) and alive1 and bool(hits2) and alive2 and no_b
              and bool(bhit) and alive3)
        rec("s6_aplay_env", ok,
            f"alive={alive1}/{alive2}/{alive3} hits={len(hits)} "
            f"hits2={len(hits2)} no_B={no_b} bogus_published={len(bhit)}")

        # ---- s7: capture --target lattice ----------------------------
        T = f"{P}_tone"
        lt = load_null_sink(T)
        tt = tmp / "carrier.wav"
        tone(tt, 20.0, 1000, 2500)
        feeder = play(f"{P}_feed", T, tt)
        V = f"{P}_vsrc"
        lv = load_remap(f"{T}.monitor", V)
        time.sleep(0.6)
        vn = node(graph(), V) or {}
        t_sn = node(graph(), T) or {}
        def cap_leg(nm, target, prop=False, dur=2.2):
            out = tmp / f"{nm}.wav"
            argv = ["pw-record", "-P", f"node.name={P}_{nm}"]
            if prop:
                argv += ["-P", "stream.capture.sink=true"]
            argv += ["--target", str(target), "--rate", "48000",
                     "--channels", "2", "--format", "s16", str(out)]
            p = subprocess.Popen(argv, stdout=subprocess.DEVNULL,
                                 stderr=subprocess.PIPE,
                                 stdin=subprocess.DEVNULL,
                                 start_new_session=True)
            time.sleep(dur)
            g = graph()
            lk = edges_in(g, f"{P}_{nm}")
            alive = p.poll() is None
            if alive:
                killpg(p, signal.SIGTERM)
            try:
                p.wait(timeout=4)
            except subprocess.TimeoutExpired:
                killpg(p)
                p.wait()
            return {"links": lk, "alive": alive,
                    "ports": sorted({e.get("out_port") for e in lk})}
        r_srcname = cap_leg("t_srcname", V)
        r_srcser = cap_leg("t_srcser", vn.get("serial"))
        r_sinkser = cap_leg("t_sinkser", t_sn.get("serial"))
        r_sinkname = cap_leg("t_sinkname", T)
        r_prop = cap_leg("t_prop", V, prop=True)
        ok = (r_srcname["ports"] and all(p.startswith("capture_") for p in r_srcname["ports"])
              and r_srcser["ports"] and all(p.startswith("capture_") for p in r_srcser["ports"])
              and r_sinkser["ports"] and all(p.startswith("monitor_") for p in r_sinkser["ports"])
              and not any(p.startswith("monitor_") for p in r_sinkname["ports"])
              and r_prop["ports"] and all(p.startswith("monitor_") for p in r_prop["ports"]))
        rec("s7_capture_lattice", ok,
            f"srcname={r_srcname['ports']} srcser={r_srcser['ports']} "
            f"sinkser={r_sinkser['ports']} sinkname={r_sinkname['ports']} "
            f"prop={r_prop['ports']}",
            sinkname_realization=("stalled" if not r_sinkname["ports"]
                                  and r_sinkname["alive"] else
                                  "bound_source" if r_sinkname["ports"]
                                  else "refused"))

        # ---- s8: loss law --------------------------------------------
        out = tmp / "loss.wav"
        p = subprocess.Popen(
            ["pw-record", "-P", f"node.name={P}_loss", "--target", V,
             "--rate", "48000", "--channels", "2", "--format", "s16",
             str(out)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True)
        time.sleep(1.2)
        g = graph()
        pre = edges_in(g, f"{P}_loss")
        size_pre = out.stat().st_size if out.exists() else None
        un = unload_own(lv["module_id"], "source_name", V)
        time.sleep(1.4)
        g = graph()
        post = edges_in(g, f"{P}_loss")
        size_mid = out.stat().st_size if out.exists() else None
        time.sleep(1.6)
        size_end = out.stat().st_size if out.exists() else None
        alive = p.poll() is None
        if alive:
            killpg(p, signal.SIGTERM)
        try:
            p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            killpg(p)
            p.wait()
        rate, pcm = read_wav(out)
        data_off = 44
        loss_frame = (size_mid - data_off) // 4 if size_mid else 0
        post_pcm = pcm[int(loss_frame):]
        post_frames = len(post_pcm)
        ok = (bool(pre) and not post and alive
              and un.get("exit_code") == 0
              and post_frames <= FLUSH_BOUND
              and size_end == size_mid)
        rec("s8_loss_law", ok,
            f"pre_links={len(pre)} post_links={len(post)} alive={alive} "
            f"unload_rc={un.get('exit_code')} post_frames={post_frames} "
            f"sizes={size_pre}->{size_mid}->{size_end}")
        killpg(feeder)
        feeder.wait()
        unload_own(lt["module_id"], "sink_name", T)

        # ---- s9: Audio/Source self-destruct --------------------------
        S = f"{P}_sd"
        ls = load_null_sink(S, media_class="Audio/Source")
        idle_mod = module_index("sink_name", S)
        time.sleep(3.6)
        idle_alive = module_index("sink_name", S) is not None
        unload_own(ls["module_id"], "sink_name", S)
        ls = load_null_sink(S, media_class="Audio/Source")
        p = subprocess.Popen(
            ["pw-record", "-P", f"node.name={P}_sdrec", "--target", S,
             "--rate", "48000", "--channels", "2", "--format", "s16",
             str(tmp / "sdr.wav")],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True)
        t0 = time.monotonic()
        dead = None
        while time.monotonic() - t0 < 2.6:
            if module_index("sink_name", S) is None:
                dead = round(time.monotonic() - t0, 2)
                break
            time.sleep(0.06)
        alive = p.poll() is None
        if alive:
            killpg(p, signal.SIGTERM)
        try:
            p.wait(timeout=4)
        except subprocess.TimeoutExpired:
            killpg(p)
            p.wait()
        rec("s9_sd_selfdestruct", bool(idle_alive and dead is not None and dead <= 1.5),
            f"idle_alive={idle_alive} bind_dead_at_s={dead}")

        # ---- s10: live negative controls -----------------------------
        c1 = pactl("get-sink-volume", "")
        c2 = run(["pw-cli", "info", str(a_serial)])
        c3 = run(["pactl", "info"])
        c4 = run(["pw-dump"], timeout=20)
        kp = subprocess.Popen(
            ["pw-play", "-P", f"node.name={P}_killctl", "-P",
             f"media.role={P}role", "--target", A, str(tA)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, start_new_session=True)
        time.sleep(0.8)
        killpg(kp)
        kp.wait()
        kerr = kp.stderr.read().decode(errors="replace") if kp.stderr else ""
        blob = (c2.get("stderr") or "") + (c2.get("stdout") or "")
        ok = ("Invalid argument" in (c1.get("stderr") or "")
              and c2["exit_code"] == 0 and "unknown global" in blob
              and c3["exit_code"] == 0 and "Server Name" in (c3.get("stdout") or "")
              and c4["exit_code"] == 0
              and kp.returncode == -9 and "entity" not in kerr
              and "error" not in kerr.lower())
        rec("s10_live_negctl", ok,
            f"empty={c1.get('stderr','').strip()[:50]} "
            f"pwcli_rc={c2['exit_code']} lie={'unknown global' in blob} "
            f"info_rc={c3['exit_code']} dump_rc={c4['exit_code']} "
            f"kill_rc={kp.returncode} kill_err={kerr.strip()[:40]}")

        # ---- teardown ------------------------------------------------
        unload_own(lb["module_id"], "sink_name", B)
        unload_own(la["module_id"], "sink_name", A)
        time.sleep(0.3)
        g = graph()
        leftover = sorted(n.get("name") for n in g["nodes"].values()
                          if (n.get("name") or "").startswith(P))
        rec("teardown", not leftover, f"leftover={leftover}")
    fails = [r for r in RECORDS if not r["ok"]]
    print(json.dumps({"spots": len(RECORDS), "failures": len(fails),
                      "failed": [r["spot"] for r in fails]}))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
