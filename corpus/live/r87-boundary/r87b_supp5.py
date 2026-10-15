#!/usr/bin/env python3
"""r87b supplement 5 — remaining verbatim replays:
  - create-node default (no linger): session-bound death?
  - create-node nonexistent factory / missing factory.name classes
  - destroy <module-owned node id> -> whole module unload?
  - pw-cat -R pipewire-0 -p --target 0 -n 48000: unlinked stall?
All objects r87b_*; the destroyed sink is seat-owned r87b_kill.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from r87b_lib import (  # noqa: E402
    TAG, TONE, RECEIPTS, RUNS, sh, norm, pw_dump, nodes_by_name, spawn, stop,
    pw_cli, pwcli_errors, load_own_sink, unload_own_sink, own_module_idx,
    mod_lines)


def create_node_leg(name, pod, linger_check=True):
    out_file = RUNS / f"s5-create-{name}.log"
    fh = open(out_file, "wb")
    p = subprocess.Popen(["pw-cli"], stdin=subprocess.PIPE, stdout=fh,
                         stderr=subprocess.STDOUT)
    res = {"pod": pod}
    try:
        p.stdin.write((pod + "\n").encode())
        p.stdin.flush()
        time.sleep(2.0)
        d = pw_dump()
        nds = nodes_by_name(f"r87b_{name}", d)
        res["present_while_session"] = bool(nds)
        res["live_id"] = nds[0]["id"] if nds else None
        p.stdin.write(b"quit\n")
        p.stdin.flush()
        p.stdin.close()
        try:
            p.wait(timeout=6)
        except subprocess.TimeoutExpired:
            p.kill()
            p.wait(timeout=3)
    except (BrokenPipeError, OSError):
        pass
    fh.close()
    res["rc"] = p.returncode
    time.sleep(0.8)
    d = pw_dump()
    nds = nodes_by_name(f"r87b_{name}", d)
    res["present_after_quit"] = bool(nds)
    if nds:
        c = pw_cli([(0, f"destroy {nds[0]['id']}")], wait_s=5,
                   label=f"s5-destroy-{name}")
        res["destroy_errors"] = pwcli_errors(c["log"])
        time.sleep(0.5)
        res["present_after_destroy"] = bool(nodes_by_name(f"r87b_{name}"))
    txt = out_file.read_text(errors="replace")
    res["proxy_lines"] = [l.strip() for l in txt.splitlines()
                          if "@proxy" in l or "error id:" in l][:6]
    res["error_lines"] = [l.strip() for l in txt.splitlines()
                          if "Error:" in l and "unsupported" not in l][:6]
    return res


def main():
    out = {}
    out["cn_default"] = create_node_leg(
        "sess", 'create-node adapter { factory.name="support.null-audio-sink" '
                'node.name="r87b_sess" media.class="Audio/Sink" }')
    out["cn_badfactory"] = create_node_leg(
        "badf", "create-node nonexistent_factory_r87b {}")
    out["cn_missing_factory"] = create_node_leg(
        "nof", 'create-node adapter { node.name="r87b_nof" '
               'media.class="Audio/Sink" }')
    # destroy a module-owned node -> module fate
    idx = load_own_sink("r87b_kill")
    time.sleep(0.6)
    d = pw_dump()
    kn = nodes_by_name("r87b_kill", d)
    out["destroy_sink"] = {"module_idx": idx,
                           "node_id": kn[0]["id"] if kn else None,
                           "module_before": own_module_idx("r87b_kill")}
    if kn:
        c = pw_cli([(0, f"destroy {kn[0]['id']}"),
                    (0.6, f"info {kn[0]['id']}")], wait_s=6,
                   label="s5-destroy-sink")
        out["destroy_sink"]["errors"] = pwcli_errors(c["log"])
    time.sleep(0.8)
    out["destroy_sink"]["node_after"] = bool(nodes_by_name("r87b_kill"))
    out["destroy_sink"]["module_after"] = own_module_idx("r87b_kill")
    out["destroy_sink"]["mod_lines_r87b_kill"] = [
        l for l in mod_lines() if "r87b_kill" in l]
    unload_own_sink("r87b_kill")
    # remote stall replay
    t0 = time.time()
    r = sh(["pw-cat", "-R", "pipewire-0", "-p", "--target", "0",
            "-n", "48000", str(TONE)], timeout=10)
    out["remote_stall"] = {"rc": r["rc"], "elapsed_s": round(time.time() - t0, 2),
                           "err": norm(r["err"])[-200:]}
    (RECEIPTS / "b5x-supplement5.json").write_text(
        json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
