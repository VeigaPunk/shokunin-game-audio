#!/usr/bin/env python3
"""r87-critic live read-only corroboration.

READ VERBS ONLY (pw-dump, pactl get-*/list, pw-cli info/--version,
sha256sum, readlink). No graph mutation, no default-* writes, no
stream spawn. Corroborates claims that are checkable without a battery:

  * the modes binary-identity lattice (pw-play/pw-record/pw-midiplay/
    pw-midirecord ARE pw-cat; pw-mididump/pw-cli are NOT)
  * the midi pin precondition (Midi-Bridge capture port + ALSA seq 14:0)
  * the remote-surface census (no raop/zeroconf/airplay nodes or .so)
  * post-run residue (zero r87a_* nodes/sinks)
  * the default sink/source the lattice READS (never writes)
"""
import hashlib
import json
import os
import re
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def run(argv, timeout=20):
    try:
        p = subprocess.run(argv, capture_output=True, timeout=timeout)
        return {"argv": " ".join(argv), "rc": p.returncode,
                "stdout": p.stdout.decode(errors="replace"),
                "stderr": p.stderr.decode(errors="replace")}
    except Exception as ex:
        return {"argv": " ".join(argv), "rc": None, "error": str(ex)[:200]}


def sha(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception as ex:
        return f"<{ex}>"


def main():
    out = {"loadavg": open("/proc/loadavg").read().strip()}

    # ---- 1. binary-identity lattice (the modes entry's first arm) ----
    bins = ("pw-cat", "pw-play", "pw-record", "pw-midiplay",
            "pw-midirecord", "pw-mididump", "pw-cli")
    ident = {}
    for b in bins:
        p = shutil.which(b)
        if not p:
            ident[b] = {"present": False}
            continue
        real = os.path.realpath(p)
        ident[b] = {"which": p, "realpath": real,
                    "sha256": sha(real)}
    base = ident.get("pw-cat", {}).get("sha256")
    for b in bins:
        if ident[b].get("present", True) is False:
            continue
        ident[b]["same_as_pwcat"] = (ident[b].get("sha256") == base)
    out["binary_identity"] = ident

    # ---- 2. midi pin precondition ----
    g = run(["pw-dump"])
    nodes = []
    try:
        doc = json.loads(g["stdout"])
        for o in doc:
            if o.get("type") == "PipeWire:Interface:Node":
                info = o.get("info") or {}
                props = info.get("props") or {}
                nodes.append({"id": o.get("id"),
                              "name": props.get("node.name"),
                              "media_class": props.get("media.class")})
    except Exception as ex:
        g["parse_error"] = str(ex)[:200]
    out["pw_dump_nodes"] = nodes
    out["bridge_present"] = [n for n in nodes
                             if n.get("name") == "Midi-Bridge"]
    out["seq"] = run(["bash", "-lc", "ls /dev/snd/seq 2>&1; "
                                    "cat /proc/asound/seq/clients 2>/dev/null "
                                    "| grep -A3 'Client 14' | head -8"])
    out["aplaymidi"] = run(["aplaymidi", "-l"])

    # ---- 3. remote-surface census ----
    out["module_dir"] = run(
        ["bash", "-lc",
         "ls /usr/lib/pipewire-0.3/ 2>/dev/null | wc -l; "
         "ls /usr/lib/pipewire-0.3/ 2>/dev/null "
         "| grep -Ei 'raop|zeroconf|airplay' ; echo '--- done'"])
    out["remote_named_nodes"] = [
        n for n in nodes
        if re.search(r"raop|zeroconf|airplay", str(n.get("name") or ""),
                     re.I)]

    # ---- 4. residue ----
    out["r87a_nodes"] = [n for n in nodes
                         if "r87a_" in str(n.get("name") or "")]
    out["pactl_sinks"] = run(["pactl", "list", "sinks", "short"])
    out["r87a_sinks"] = [l for l in
                         out["pactl_sinks"]["stdout"].splitlines()
                         if "r87a_" in l]
    out["pactl_modules"] = run(["pactl", "list", "modules", "short"])
    out["r87a_modules"] = [l for l in
                           out["pactl_modules"]["stdout"].splitlines()
                           if "r87a_" in l]

    # ---- 5. the default the lattice reads ----
    out["default_sink"] = run(["pactl", "get-default-sink"])
    out["default_source"] = run(["pactl", "get-default-source"])

    # ---- 6. the serial-vs-id addressing law (read-only) ----
    ds = out["default_sink"]["stdout"].strip()
    out["default_sink_name"] = ds
    if ds:
        out["get_sink_volume_by_name"] = run(
            ["pactl", "get-sink-volume", ds])
        out["pw_cli_info_by_name"] = run(["pw-cli", "info", ds])

    json.dump(out, open(os.path.join(HERE, "live-readonly.json"), "w"),
              indent=1, sort_keys=True)

    lines = [f"loadavg: {out['loadavg']}", "",
             "== binary identity (modes entry arm 1) =="]
    for b in bins:
        i = ident.get(b, {})
        lines.append(f"  {b:14s} present={i.get('present', True)!s:5s} "
                     f"same_as_pwcat={i.get('same_as_pwcat')!s:5s} "
                     f"realpath={i.get('realpath')}")
    lines += ["", "== midi pin precondition ==",
              f"  Midi-Bridge node: {out['bridge_present']}",
              f"  seq devices: {(out['seq'].get('stdout') or '').strip()[:200]}",
              f"  aplaymidi -l: {(out['aplaymidi'].get('stdout') or '').strip()[:300]}",
              "", "== remote surface census ==",
              f"  module dir probe: {(out['module_dir'].get('stdout') or '').strip()}",
              f"  remote-named nodes: {out['remote_named_nodes']}",
              "", "== residue ==",
              f"  r87a_* nodes in pw-dump: {out['r87a_nodes']}",
              f"  r87a_* sinks in pactl:    {out['r87a_sinks']}",
              f"  r87a_* modules in pactl:  {out['r87a_modules']}",
              f"  total nodes enumerated:   {len(nodes)}",
              "", "== default (read, never written) ==",
              f"  default sink:   {out['default_sink']['stdout'].strip()!r}",
              f"  default source: {out['default_source']['stdout'].strip()!r}",
              f"  get-sink-volume by name rc={out['get_sink_volume_by_name']['rc']}",
              f"  pw-cli info by name  rc={out['pw_cli_info_by_name']['rc']}",
              f"    stderr: {out['pw_cli_info_by_name']['stderr'].strip()[:120]!r}"]
    txt = "\n".join(lines) + "\n"
    open(os.path.join(HERE, "live-readonly.out"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
