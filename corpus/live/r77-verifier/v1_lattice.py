#!/usr/bin/env python3
"""r77 verifier — independent re-derivation of the stream.capture.sink
fallback lattice (claim 1) and the provenance trap.

Own implementation: does NOT import corpus/fixtures/measure_audio.py.
Byte discipline: every leg is `-n 24000` frames (0.5 s @48k/2ch/s16 =
96044 B max), serialized, scratch in a TemporaryDirectory.
Witnesses: (a) `pw-link -l` producers on BOTH input channels, differenced
against a pre-spawn snapshot (foreign clients cancel); (b) capture content
peak / nonzero fraction; (c) the capture node's own `target.object` prop
(intent, not consumption).
"""
import array
import json
import re
import signal
import struct
import subprocess
import tempfile
import time
from pathlib import Path

REPO = Path("/home/vgpnk/Projects/shokunin/audio-shokunin")
OUT = REPO / "corpus/live/r77-verifier"
TONE = REPO / "corpus/artifacts/stem_sections.wav"
FRAMES = 96000                          # 2.0 s — the topology sample at
                                        # 0.8 s must land INSIDE the capture
BOUND_BYTES = 44 + FRAMES * 4          # 384044
EMPTY_BYTES = 44
TIMEOUT_S = 30


def sh(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def default_sink():
    m = re.search(r"^Default Sink:\s*(.*)$", sh(["pactl", "info"]).stdout, re.M)
    return m.group(1).strip() if m else None


def sink_names():
    return [ln.split()[1] for ln in
            sh(["pactl", "list", "sinks", "short"]).stdout.splitlines()
            if len(ln.split()) > 1]


def source_names():
    return [ln.split()[1] for ln in
            sh(["pactl", "list", "sources", "short"]).stdout.splitlines()
            if len(ln.split()) > 1]


def link_map():
    """port -> sorted producers, from `pw-link -l` (indented `|<-` lines)."""
    per = {}
    port = None
    for ln in sh(["pw-link", "-l"]).stdout.splitlines():
        if not ln or not ln[0].isspace():
            port = ln.strip() if ln.strip().startswith("pw-record:input_") \
                else None
            continue
        if port and "|<-" in ln:
            per.setdefault(port, set()).add(ln.split("|<-", 1)[1].strip())
    return {k: sorted(v) for k, v in per.items()}


def consumed(per):
    fl = set(per.get("pw-record:input_FL", []))
    fr = set(per.get("pw-record:input_FR", []))
    both = fl & fr or (fl | fr)
    return sorted({p.rsplit(":", 1)[0] for p in both})


def pcm(path):
    p = Path(path)
    st = {"exists": p.exists()}
    if not p.exists():
        return st
    b = p.read_bytes()
    st["bytes"] = len(b)
    if len(b) < 44 or b[:4] != b"RIFF":
        return st
    tag, ch, rate, _br, _ba, bits = struct.unpack("<HHIIHH", b[20:36])
    st["fmt"] = {"tag": tag, "channels": ch, "rate": rate, "bits": bits}
    off, declared = 12, None
    while off + 8 <= len(b):
        cid = b[off:off + 4]
        csz = struct.unpack("<I", b[off + 4:off + 8])[0]
        if cid == b"data":
            declared = csz
            break
        off += 8 + csz + (csz & 1)
    st["data_declared"] = declared
    payload = b[off + 8:] if declared is not None else b""
    a = array.array("h")
    if len(payload) >= 2:
        a.frombytes(payload[:len(payload) // 2 * 2])
    st["samples"] = len(a)
    st["peak"] = max((abs(x) for x in a), default=0)
    st["nonzero_frac"] = round(
        (sum(1 for x in a if x) / len(a)), 4) if a else 0.0
    st["carries_tone"] = st["nonzero_frac"] > 0.05
    return st


def target_object_props():
    """Live pw-record nodes' own advertised target (intent witness)."""
    dump = json.loads(sh(["pw-dump"]).stdout or "[]")
    return [{"target_object": (((n.get("info") or {}).get("props")
                               or {}).get("target.object")),
             "stream_capture_sink": (((n.get("info") or {}).get("props")
                                      or {}).get("stream.capture.sink"))}
            for n in dump
            if (((n.get("info") or {}).get("props") or {})
                .get("application.name") == "pw-record")]


def cell(name, target, prop, tmp, sink, expect_tone):
    out = Path(tmp) / f"{name}.wav"
    argv = ["pw-record"]
    if prop:
        argv += ["-P", "stream.capture.sink=true"]
    if target:
        argv += ["--target", target]
    argv += ["-n", str(FRAMES), "--rate", "48000", "--channels", "2",
             "--format", "s16", str(out)]
    before = link_map()
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True)
    time.sleep(0.3)
    player = subprocess.Popen(["pw-cat", "-p", "--target", sink, str(TONE)],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL, start_new_session=True)
    time.sleep(0.5)
    during = link_map()
    dump = target_object_props()
    rec_live_at_sample = proc.poll() is None
    try:
        proc.wait(timeout=TIMEOUT_S)
    except subprocess.TimeoutExpired:
        import os
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    if player.poll() is None:
        player.terminate()
    try:
        player.wait(timeout=5)
    except subprocess.TimeoutExpired:
        import os
        os.killpg(player.pid, signal.SIGKILL)
        player.wait()
    err = proc.stderr.read().decode(errors="replace")
    merged = {p: sorted(set(during.get(p, [])) - set(before.get(p, [])))
              for p in set(before) | set(during)}
    got = consumed(merged)
    rec = {"target_arg": target, "capture_sink_prop": prop,
           "default_sink_at_cell": default_sink(),
           "live_at_sample": rec_live_at_sample,
           "exit_code": proc.returncode,
           "stderr": err.strip().splitlines()[:2],
           "consumed_nodes": got,
           "ambiguous": len(got) > 1,
           "target_object_props": [d["target_object"] for d in dump],
           "target_object_is_request": (
               bool(dump) and dump[0]["target_object"] == target),
           "file": pcm(out)}
    rec["expect_tone"] = expect_tone
    return rec


def main():
    sink = default_sink()
    other = next((s for s in sink_names() if s != sink), None)
    src = next((s for s in source_names() if not s.endswith(".monitor")), None)
    entry = {"probe": "r77-verifier independent fallback lattice",
             "inventory": {"default_sink": sink, "other_sink": other,
                           "source": src, "bound_bytes": BOUND_BYTES},
             "legs": {}, "failures": []}
    cases = [
        ("prop_default_sink", sink, True, True),
        ("prop_garbage", "no_such_node_v77", True, True),
        ("prop_source", src, True, True),
        ("prop_other_sink", other, True, False),
        ("noprop_default_sink", sink, False, None),
        ("noprop_source", src, False, None),
    ]
    with tempfile.TemporaryDirectory(prefix="r77v-lattice-") as tmp:
        for name, target, prop, tone in cases:
            if target is None:
                entry["legs"][name] = {"blocked": "no such node on host"}
                continue
            entry["legs"][name] = cell(name, target, prop, tmp, sink, tone)
            time.sleep(0.8)
    f = entry["failures"]
    for name, target, prop, tone in cases:
        leg = entry["legs"].get(name)
        if leg is None or "blocked" in leg:
            continue
        got = leg["consumed_nodes"]
        live_expected = name.startswith("prop_") or name == "noprop_source"
        if live_expected and not leg.get("live_at_sample"):
            f.append(f"{name}: the capture had already exited at the topology "
                     f"sample — an empty witness here is a timing artifact, "
                     f"not an absence")
            continue
        if name.startswith("noprop_"):
            # no prop: a sink target never resolves (44-byte empty wav);
            # only a real source node resolves.
            if name == "noprop_source":
                if got != [src]:
                    f.append(f"{name}: expected consumption of the source "
                             f"{src}, got {got}")
                if leg["file"].get("bytes") != BOUND_BYTES:
                    f.append(f"{name}: expected {BOUND_BYTES} B, got "
                             f"{leg['file'].get('bytes')}")
                if leg["file"].get("carries_tone") is not False:
                    f.append(f"{name}: the host's default source is digital "
                             f"silence; got tone="
                             f"{leg['file'].get('carries_tone')}")
            elif leg["file"].get("bytes") != EMPTY_BYTES:
                f.append(f"{name}: expected the 44-byte empty wav, got "
                         f"{leg['file'].get('bytes')} B "
                         f"(rc={leg['exit_code']})")
            continue
        want = sink if name in ("prop_default_sink", "prop_garbage",
                                "prop_source") else other
        if got != [want]:
            f.append(f"{name}: expected consumption of {want}, got {got}")
        if leg["file"].get("carries_tone") is not tone:
            f.append(f"{name}: tone witness expected {tone}, got "
                     f"{leg['file'].get('carries_tone')} "
                     f"(peak={leg['file'].get('peak')})")
        if not leg["target_object_is_request"]:
            f.append(f"{name}: the capture node did not advertise the "
                     f"requested target (provenance trap witness)")
        if leg["file"].get("bytes") != BOUND_BYTES:
            f.append(f"{name}: expected {BOUND_BYTES} B, got "
                     f"{leg['file'].get('bytes')}")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v1_lattice.json").write_text(json.dumps(entry, indent=2) + "\n")
    print(json.dumps({"receipt": str(OUT / "v1_lattice.json"),
                      "failures": entry["failures"]}))


if __name__ == "__main__":
    main()
