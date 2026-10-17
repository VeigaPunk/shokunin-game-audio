#!/usr/bin/env python3
"""r96 simplifier folds — exact-string, occurrence-asserted, py_compile-gated.

Targets (inside the pulsecli r96 block of corpus/fixtures/measure_audio.py):
  C5    : delete the byte-equivalent duplicate cell `t_proc_lat_b`
  C4rep : re-key the two dead `_pulsecli_r96_row(..., 0)` lookups to the
          leg's own child pid (recorded as `rec["pid"]` in
          `_pulsecli_r96_run`, the r84 `_alsapw_r84_prop_leg` convention)
  C4del : delete both dead pid-0 lookups instead (weight-first alternative)

Variants written (fixture only):
  f1  = base + C5
  f2  = base + C4rep
  f3  = base + C4del
  f12 = base + C5 + C4rep
  f13 = base + C5 + C4del
"""
import hashlib
import py_compile
import subprocess
import sys
from pathlib import Path

R96S = Path("/home/vgpnk/Projects/shokunin/r96s")
REL = "corpus/fixtures/measure_audio.py"

C5_OLD = '''        _attr_leg("t_proc_lat_a", 2, latency_ms=100, process_ms=5)
        _attr_leg("t_proc_lat_b", 2, latency_ms=100, process_ms=5,
                  extra=())
'''
C5_NEW = '''        _attr_leg("t_proc_lat_a", 2, latency_ms=100, process_ms=5)
'''

C4R_PID_OLD = '''            stdin=subprocess.DEVNULL, env=env, cwd=cwd,
            start_new_session=True)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    t0 = time.monotonic()
    killed = False
'''
C4R_PID_NEW = '''            stdin=subprocess.DEVNULL, env=env, cwd=cwd,
            start_new_session=True)
    except OSError as exc:
        rec["spawn_error"] = str(exc)[:160]
        return rec
    rec["pid"] = proc.pid
    t0 = time.monotonic()
    killed = False
'''

C4_A_OLD = '''            if _pulsecli_r96_row("sink-inputs", 0) is not None:
                leaf["failures"].append(
                    "an index-0 sink-input exists while the malformed "
                    "property leg ran — the no-stream claim is "
                    "unwitnessed")
'''
C4R_A_NEW = '''            if _pulsecli_r96_row("sink-inputs",
                                 leaf.get("pid")) is not None:
                leaf["failures"].append(
                    "a sink-input for this leg's pid exists while the "
                    "malformed property leg ran — the no-stream claim "
                    "is unwitnessed")
'''

C4_B_OLD = '''            leaf["row"] = _pulsecli_r96_row_view(
                _pulsecli_r96_row("sink-inputs", 0))
'''
C4R_B_NEW = '''            leaf["row"] = _pulsecli_r96_row_view(
                _pulsecli_r96_row("sink-inputs", leaf.get("pid")))
'''


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sub_once(s, old, new, label):
    n = s.count(old)
    assert n == 1, f"{label}: anchor occurs {n}x (want 1)"
    return s.replace(old, new, 1)


def apply_c5(s):
    return sub_once(s, C5_OLD, C5_NEW, "C5")


def apply_c4rep(s):
    s = sub_once(s, C4R_PID_OLD, C4R_PID_NEW, "C4rep/pid")
    s = sub_once(s, C4_A_OLD, C4R_A_NEW, "C4rep/A")
    s = sub_once(s, C4_B_OLD, C4R_B_NEW, "C4rep/B")
    return s


def apply_c4del(s):
    s = sub_once(s, C4_A_OLD, "", "C4del/A")
    s = sub_once(s, C4_B_OLD, "", "C4del/B")
    return s


VARIANTS = {
    "f1": [apply_c5],
    "f2": [apply_c4rep],
    "f3": [apply_c4del],
    "f12": [apply_c5, apply_c4rep],
    "f13": [apply_c5, apply_c4del],
}


def main():
    base_path = R96S / "base" / REL
    base = base_path.read_text()
    base_sha = sha256(base_path)
    base_lines = base.count("\n")
    print(f"base {base_path} sha256={base_sha} lines={base_lines}")
    for variant, fns in VARIANTS.items():
        s = base
        for fn in fns:
            s = fn(s)
        out = R96S / variant / REL
        # NEVER write through a hardlinked inode: unlink first (the trees
        # are `cp -al` copies, so an in-place write would hit every copy).
        if out.exists():
            out.unlink()
        with open(out, "w") as fh:
            fh.write(s)
        tmp_pyc = R96S / f"pyc-{variant}.pyc"
        rc = py_compile.compile(str(out), cfile=str(tmp_pyc),
                                doraise=False)
        pyc_ok = Path(rc).exists() if rc else False
        st = subprocess.run(
            [sys.executable, "-c",
             "import ast,sys;ast.parse(open(sys.argv[1]).read())",
             str(out)], capture_output=True)
        print(f"{variant}: sha256={sha256(out)} lines={s.count(chr(10))} "
              f"delta={s.count(chr(10)) - base_lines} pyc={pyc_ok} "
              f"ast_rc={st.returncode}")
        if st.returncode != 0:
            print(st.stderr.decode()[:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
