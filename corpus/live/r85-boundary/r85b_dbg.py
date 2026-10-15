#!/usr/bin/env python3
"""r85b focused debug: (a) which tap shape actually carries sink content,
(b) capture-side freeze-vs-zeros discriminator after target deletion.
Scratch under corpus/live/r85-boundary/. Seat objects r85b_*."""
import json, os, signal, subprocess, sys, time, wave
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
from r85b_probe import (HERE, TAGS, RUNS, RCPT, sh, spawn, killp, board, nid_by_name, linkstr,
                        sha, size, gen_tone, read_wav, windows, fft_amp, mod_line, load_sink,
                        unload_verified, wait_node, loadavg, ensure_tones)

D = HERE / "runs" / "dbg"
D.mkdir(parents=True, exist_ok=True)


def amp(path):
    if not Path(path).exists() or size(path) < 1000:
        return None
    a, fr = read_wav(path)
    return {"max": int(np.abs(a).max()), "L1000": round(fft_amp(a[:, 0], 1000), 1),
            "R1000": round(fft_amp(a[:, 1], 1000), 1) if a.shape[1] > 1 else None,
            "frames": int(a.shape[0])}


def tap_links(tag):
    b = board()
    ids = nid_by_name(b, tag)
    return {"nodes": ids, "links": [linkstr(b, i) for i in ids],
            "props": [{k: b["nodes"][i]["props"].get(k) for k in
                       ("node.name", "target.object", "stream.capture.sink", "media.class")} for i in ids]}


def run_tap_leg(name, sink, tap_prop=True, order="tapfirst", tgt=None, secs=3.0, frames=144000):
    f = D / f"tap_{name}.wav"
    if f.exists():
        f.unlink()
    tgt = tgt or sink
    props = "-P stream.capture.sink=true" if tap_prop else ""
    rows = {"leg": name, "tap_prop": tap_prop, "order": order, "target": str(tgt)}
    if order == "tapfirst":
        rec = spawn(f"pw-record {props} -P node.name=r85b_tapdbg --target {tgt} --rate 48000 "
                    f"--channels 2 --format s16 -n {frames} {f}")
        time.sleep(0.45)
        pl = spawn(f"pw-play -P node.name=r85b_playdbg --target {sink} {TAGS/'a1k.wav'}")
    else:
        pl = spawn(f"pw-play -P node.name=r85b_playdbg --target {sink} {TAGS/'a1k.wav'}")
        time.sleep(0.5)
        rec = spawn(f"pw-record {props} -P node.name=r85b_tapdbg --target {tgt} --rate 48000 "
                    f"--channels 2 --format s16 -n {frames} {f}")
    time.sleep(1.0)
    rows["links_midplay"] = tap_links("r85b_tapdbg")
    rows["player_links"] = tap_links("r85b_playdbg")
    killp(pl)
    killp(rec)
    time.sleep(0.3)
    rows["content"] = amp(f)
    return rows


def main():
    out = {"load_at_start": loadavg()}
    ensure_tones()
    sink = "r85b_dbgmix"
    ls = load_sink(sink)
    ok, b = wait_node(sink)
    out["sink"] = {"load": ls, "node": nid_by_name(b, sink),
                   "serial": b["nodes"][nid_by_name(b, sink)[0]]["serial"] if nid_by_name(b, sink) else None,
                   "pactl_vol": sh(f"pactl get-sink-volume {sink}")[1].splitlines()[0] if True else None}
    # tap legs
    out["tap_legs"] = []
    out["tap_legs"].append(run_tap_leg("prop_tapfirst", sink, True, "tapfirst"))
    out["tap_legs"].append(run_tap_leg("noprop_tapfirst", sink, False, "tapfirst"))
    out["tap_legs"].append(run_tap_leg("prop_playfirst", sink, True, "playfirst"))
    out["tap_legs"].append(run_tap_leg("prop_serial", sink, True, "tapfirst", tgt=out["sink"]["serial"]))
    out["tap_legs"].append(run_tap_leg("noprop_serial", sink, False, "tapfirst", tgt=out["sink"]["serial"]))
    out["tap_legs"].append(run_tap_leg("prop_bogus", sink, True, "tapfirst", tgt="no_such_r85b_sink"))

    # ---- capture-side freeze-vs-zeros discriminator
    tone = TAGS / "tone60.wav"
    if not tone.exists():
        gen_tone(tone, 60.0, 2, [(0, 1000, 12000), (1, 1000, 12000)])
    out["capture_legs"] = []
    vsrc_n = 0

    def cap_leg(name, extra_stream=False, stop_tone_before=False, delete_kind="module",
                target_kind="name", tone_on=True):
        nonlocal vsrc_n
        vsrc_n += 1
        vsrc = f"r85b_vd{vsrc_n}"
        rc, o, e = sh(f"pactl load-module module-remap-source master={sink}.monitor source_name={vsrc}")
        ok, b = wait_node(vsrc, t=6)
        time.sleep(0.4)
        tp = None
        if tone_on:
            tp = spawn(f"pw-play -P node.name=r85b_vdplay --target {sink} {tone}")
            time.sleep(0.5)
        extra = None
        if extra_stream:
            extra = spawn(f"pw-record -P node.name=r85b_extra_rec --target {vsrc} --rate 48000 "
                          f"--channels 2 --format s16 -n 480000 {D/name}_extra.wav")
        b = board()
        vs = nid_by_name(b, vsrc)
        serial = b["nodes"][vs[0]]["serial"] if vs else None
        tgt = vsrc if target_kind == "name" else (serial if target_kind == "serial" else (vs[0] if vs else None))
        f = D / f"cap_{name}.wav"
        p = spawn(f"pw-record -P node.name=r85b_capdbg --target {tgt} --rate 48000 --channels 2 "
                  f"--format s16 -n 288000 {f}")
        tl = []
        t0 = time.time()
        acted = False
        while time.time() - t0 < 4.6:
            el = time.time() - t0
            if not acted and el >= 1.5:
                if stop_tone_before and tp:
                    killp(tp)
                    time.sleep(0.4)
                if delete_kind == "module":
                    unload_verified(vsrc)
                else:
                    bb = board()
                    for i in nid_by_name(bb, vsrc):
                        sh(f"pw-cli destroy {i}")
                acted = True
            bb = board()
            tl.append({"t": round(el, 2), "sz": size(f),
                       "links": linkstr(bb, nid_by_name(bb, "r85b_capdbg")[0])
                       if nid_by_name(bb, "r85b_capdbg") else []})
            time.sleep(0.1)
        rc = p.poll(); alive = rc is None
        if alive:
            rc = killp(p)
        if extra:
            killp(extra)
        if tp:
            killp(tp)
        unload_verified(vsrc)
        time.sleep(0.3)
        szs = [x["sz"] for x in tl]
        grew_after = None
        if len(szs) > 20:
            grew_after = szs[-1] - szs[20]
        return {"leg": name, "target": str(tgt), "target_kind": target_kind, "alive": alive, "rc": rc,
                "final_bytes": size(f), "sizes": szs, "delta_after_loss": grew_after,
                "content": amp(f), "extra_stream": extra_stream,
                "stop_tone_before": stop_tone_before, "delete_kind": delete_kind}

    out["capture_legs"].append(cap_leg("base_name"))
    out["capture_legs"].append(cap_leg("base_name_rep2"))
    out["capture_legs"].append(cap_leg("extra_stream", extra_stream=True))
    out["capture_legs"].append(cap_leg("stop_tone", stop_tone_before=True))
    out["capture_legs"].append(cap_leg("pwcli_destroy", delete_kind="destroy"))
    out["capture_legs"].append(cap_leg("serial_target", target_kind="serial"))
    out["capture_legs"].append(cap_leg("no_tone", tone_on=False))

    unload_verified(sink)
    out["load_at_end"] = loadavg()
    (RCPT / "dbg.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: v for k, v in out.items() if k not in ("tap_legs", "capture_legs")}, indent=1, default=str))
    for r in out["tap_legs"]:
        print("TAP", r["leg"], "prop", r["tap_prop"], r["order"], "->",
              json.dumps(r["links_midplay"]["links"])[:160], "content", r["content"])
    for r in out["capture_legs"]:
        print("CAP", r["leg"], "alive", r["alive"], "final", r["final_bytes"],
              "delta_after_loss", r["delta_after_loss"], "content", r["content"],
              "sizes_tail", r["sizes"][18:24], r["sizes"][-2:])


if __name__ == "__main__":
    main()
