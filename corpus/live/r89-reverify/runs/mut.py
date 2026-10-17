#!/usr/bin/env python3
"""r89 RE-VERIFY mutation spot-check — revert-the-fix mutants on the
COMMITTED bytes, run in scratch trees (never the frozen tree).

M1 `mut-sigreset`  : `_pwprof_r89_sigreset` -> no-op (pre-fold behavior).
     Run under nohup: g_hup must RED again (rc -9 at the harness bound).
M2 `mut-footglobal`: the own-scoped x_foot verdict -> the pre-fold GLOBAL
     census law (`pwprof_during == before+1 and nodes_delta == 0`).
     Run with a HELD foreign pw-profiler client in the window: must RED
     (`pwprof_before=1/during=1`), while the committed arm under the same
     context is green (held-foreign run in battery-cot.sh).

Usage: mut.py <committed-fixture> <outdir-root>
"""
import shutil
import sys
from pathlib import Path

M1_OLD = """    for _s in (signal.SIGHUP, signal.SIGINT, signal.SIGQUIT,
               signal.SIGTERM, signal.SIGUSR1):
        try:
            signal.signal(_s, signal.SIG_DFL)
        except (OSError, ValueError):
            pass
"""
M1_NEW = """    return None  # MUTANT M1: pre-fold behavior (no disposition reset)
"""

M2_OLD = """    elif len(l["own_clients"]) != 1 or l.get("own_objects"):
        failures.append(
            f"x_foot: own clients={l.get('own_clients')} "
            f"own objects={l.get('own_objects')} — the one-Client "
            "footprint fails")
"""
M2_NEW = """    elif l.get("pwprof_during") != \\
            (l.get("pwprof_before") or 0) + 1 or l.get("nodes_delta") != 0:
        failures.append(
            f"x_foot GLOBAL-ARM-MUTANT: {l} — the one-Client footprint "
            "fails")
"""


def make(src, root, name, old, new):
    d = Path(root) / name / "corpus" / "fixtures"
    d.mkdir(parents=True, exist_ok=True)
    (d / "build_artifacts.py").write_bytes(
        (Path(src).parent / "build_artifacts.py").read_bytes())
    text = Path(src).read_text()
    assert text.count(old) == 1, f"{name}: anchor not unique ({text.count(old)})"
    (d / "measure_audio.py").write_text(text.replace(old, new))
    art = Path(root) / name / "corpus" / "artifacts"
    if art.exists():
        shutil.rmtree(art)
    shutil.copytree(Path(src).parent.parent / "artifacts", art)
    (Path(root) / name / "corpus" / "live" / "runs").mkdir(
        parents=True, exist_ok=True)
    print(f"made {name}: {d / 'measure_audio.py'}")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    src, root = sys.argv[1], sys.argv[2]
    make(src, root, "mut-sigreset", M1_OLD, M1_NEW)
    make(src, root, "mut-footglobal", M2_OLD, M2_NEW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
