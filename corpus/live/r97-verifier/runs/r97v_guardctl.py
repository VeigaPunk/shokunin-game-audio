#!/usr/bin/env python3
"""r97 verifier kill-guard control: the family's teardown guard must kill ONLY
processes whose cmdline/environ names the private root, and must REFUSE a
foreign pid (the boundary's §2.5 environ-aware guard).

Three arms, all on disposable processes this script owns:
  A. foreign pid (no private root anywhere)  -> REFUSED, survives
  B. own pid (private root in its environ)   -> killed
  C. live run's private core (read-only)     -> own() True, NOT killed

    python3 r97v_guardctl.py <fixture.py> <out.json> [live_private_root]
"""
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def load_mod(fixture):
    spec = importlib.util.spec_from_file_location("ma_guardctl", fixture)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    fixture, out = sys.argv[1], sys.argv[2]
    live_root = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    mod = load_mod(fixture)
    rec = {}

    # A. foreign pid: no private root in cmdline or environ.
    fake = Path("/tmp/r97v-guardctl-fake-root")
    pa = subprocess.Popen(["sleep", "600"], start_new_session=True)
    time.sleep(0.3)
    own_a = mod._wppol_r97_own(fake, pa.pid)
    res_a = mod._wppol_r97_kill(fake, pa.pid)
    time.sleep(0.3)
    alive_a = pa.poll() is None
    rec["A_foreign"] = {"own": own_a, "kill": res_a, "survived": alive_a}
    if alive_a:
        pa.kill()
        pa.wait(timeout=5)

    # B. own pid: the private root rides in the environment (a private
    # `wireplumber -c wireplumber.conf -p main` has no seat path in argv).
    mine = Path("/tmp/r97v-guardctl-mine-root")
    env = dict(os.environ)
    env["R97V_PRIVATE_ROOT"] = str(mine)
    env["XDG_RUNTIME_DIR"] = str(mine / "rt")
    pb = subprocess.Popen(["sleep", "600"], start_new_session=True, env=env)
    time.sleep(0.3)
    own_b = mod._wppol_r97_own(mine, pb.pid)
    res_b = mod._wppol_r97_kill(mine, pb.pid, grace=2.0)
    time.sleep(0.3)
    alive_b = pb.poll() is None
    rec["B_own"] = {"own": own_b, "kill": res_b, "survived": alive_b}
    if alive_b:
        pb.kill()
        pb.wait(timeout=5)

    # C. the live run's private core: read-only identity check.
    rec["C_live"] = None
    if live_root is not None:
        try:
            pid = int((live_root / "run" / "core.pid").read_text().strip())
        except (OSError, ValueError):
            pid = None
        if pid:
            try:
                os.kill(pid, 0)
                alive = True
            except OSError:
                alive = False
            rec["C_live"] = {"root": str(live_root), "pid": pid,
                             "alive": alive,
                             "own": mod._wppol_r97_own(live_root, pid)}
    Path(out).write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec))
    ok = (rec["A_foreign"]["own"] is False
          and rec["A_foreign"]["kill"].get("reason") == "REFUSED foreign pid"
          and rec["A_foreign"]["survived"] is True
          and rec["B_own"]["own"] is True
          and rec["B_own"]["kill"].get("killed") is True
          and rec["B_own"]["survived"] is False)
    print("GUARD CONTROL:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
