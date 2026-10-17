#!/usr/bin/env python3
"""r92 simplifier — apply the proven folds to a scratch copy of the audited
blob. Every anchor is asserted to occur exactly once (or exactly N times for
the repeated shapes); py_compile runs on the result; nothing is written unless
all asserts pass.

Usage: python3 fold_apply.py <src.py> <dst.py> [--with-f6]

Folds (all inside the r92 block):
  F1  _fc92_shift_ok dead second return + 5 call sites (dead `ks`/`_ks`)
  F2  d_fhi fail-open arm -> fail-closed (critic F3), reusing d_copy's form
  F3  a_ports_none.feed_link fail-open -> fail-closed (critic F4b)
  F4  i_* silent legs: arm the recorded load reply (critic F4a)
  F5  daemon gate: 4 byte-identical 16-line copies -> one helper (duplicate
      authority)
  F6  (optional, --with-f6) _fc92_block's unreachable ctx branch
"""
import ast
import hashlib
import sys
from pathlib import Path


def must_replace(s, old, new, n=1, what=""):
    got = s.count(old)
    assert got == n, f"{what}: anchor occurs {got}x, expected {n}x"
    return s.replace(old, new)


F1_OLD = """    if delta is None:
        return False, None
    ks = []
    for k in range(-4, 5):
        if abs(delta - (want + k * FILTERCHAIN_R92_BLOCKSIZE)) <= tol:
            ks.append(k)
    return bool(ks), ks
"""
F1_NEW = """    if delta is None:
        return False
    return any(abs(delta - (want + k * FILTERCHAIN_R92_BLOCKSIZE)) <= tol
               for k in range(-4, 5))
"""

F2_OLD = """    if any(abs(v) > 0.05 for v in gains("d_fhi").values()):
"""
F2_NEW = """    if any(abs(v) > 0.05 for v in gains("d_fhi").values()) or \\
            len(gains("d_fhi")) != 5:
"""

F3_OLD = """            (l.get("feed_link") or {}).get("rc") == 0:
        _fc92_leg_fail(failures, "a_ports_none", l,
"""
F3_NEW = """            (l.get("feed_link") or {}).get("rc") in (0, None):
        _fc92_leg_fail(failures, "a_ports_none", l,
"""

F4_OLD = """    for tag, cls in silent_cls.items():
        a = an(tag)
        if a.get("out_nz_exact") != 0:
"""
F4_NEW = """    for tag, cls in silent_cls.items():
        a = an(tag)
        lt = (legs[tag].get("load") or {}).get("load_text") or ""
        if "[E]" in lt or "failed file" in lt:
            _fc92_leg_fail(failures, tag, legs[tag],
                           "the silent class is not silent at LOAD (the "
                           f"load reply carries a failure line): {lt[:160]}")
        if a.get("out_nz_exact") != 0:
"""

F5_OLD = """    if not (entry.get("daemon") or {}).get("ok"):
        # a wedged/saturated daemon makes the WHOLE entry unmeasurable:
        # it is named as a block AND as a failure — a battery that
        # measured nothing must never read as green.
        failures.append(
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s — the "
            "entry is unmeasurable")
        return _fc92_block(
            entry, failures,
            "daemon unreachable or saturated: pactl info "
            f"rc={(entry.get('daemon') or {}).get('exit_code')} "
            f"killed={(entry.get('daemon') or {}).get('killed_at_bound')} "
            f"wall={(entry.get('daemon') or {}).get('wall_s')}s")
"""
F5_NEW = """    blocked = _fc92_daemon_gate(entry, failures)
    if blocked is not None:
        return blocked
"""

F5_HELPER_OLD = """def _fc92_block(entry, failures, msg, ctx=None):
"""
F5_HELPER_NEW = '''def _fc92_daemon_gate(entry, failures):
    """A wedged/saturated daemon makes the WHOLE entry unmeasurable: it is
    named as a block AND as a failure — a battery that measured nothing
    must never read as green. Returns the blocked entry, or None."""
    d = entry.get("daemon") or {}
    if d.get("ok"):
        return None
    why = (f"daemon unreachable or saturated: pactl info "
           f"rc={d.get('exit_code')} killed={d.get('killed_at_bound')} "
           f"wall={d.get('wall_s')}s")
    failures.append(why + " — the entry is unmeasurable")
    return _fc92_block(entry, failures, why)


def _fc92_block(entry, failures, msg, ctx=None):
'''

F6_VALID_OLD_DSP = """    for tag, _ in legs_spec + CLAMP_EXTRA:
        l = legs[tag]
        if l.get("gate"):
            _fc92_leg_fail(failures, tag, l, f"blocked: {l['gate']}")
        elif not l.get("valid"):
            if not l.get("links_ok"):
                entry.setdefault("coverage_blocked", []).append(
                    f"{tag}: taps never bound — contention class")
            else:
                _fc92_leg_fail(failures, tag, l,
                               "the leg did not measure (valid=False)")
"""
F6_VALID_NEW_DSP = """    _fc92_valid_gate(entry, failures,
                     [t for t, _ in legs_spec + CLAMP_EXTRA], legs)
"""
F6_VALID_OLD_IR = """    for tag, _, _, _ in specs:
        l = legs[tag]
        if l.get("gate"):
            _fc92_leg_fail(failures, tag, l, f"blocked: {l['gate']}")
        elif not l.get("valid"):
            if not l.get("links_ok"):
                entry.setdefault("coverage_blocked", []).append(
                    f"{tag}: taps never bound — contention class")
            else:
                _fc92_leg_fail(failures, tag, l,
                               "the leg did not measure (valid=False)")
"""
F6_VALID_NEW_IR = """    _fc92_valid_gate(entry, failures, [t for t, _, _, _ in specs], legs)
"""

F6_VALID_HELPER_OLD = """def _fc92_block(entry, failures, msg, ctx=None):
"""
F6_VALID_HELPER_NEW = '''def _fc92_valid_gate(entry, failures, tags, legs):
    """An unmeasurable leg is a failure, never a silent green: a blocked
    leg is named, a never-bound tap is the contention class. The two
    audio entries ran this gate as two byte-identical loop bodies."""
    for tag in tags:
        l = legs[tag]
        if l.get("gate"):
            _fc92_leg_fail(failures, tag, l, f"blocked: {l['gate']}")
        elif not l.get("valid"):
            if not l.get("links_ok"):
                entry.setdefault("coverage_blocked", []).append(
                    f"{tag}: taps never bound — contention class")
            else:
                _fc92_leg_fail(failures, tag, l,
                               "the leg did not measure (valid=False)")


def _fc92_block(entry, failures, msg, ctx=None):
'''

F7_CTX_OLD = """def _fc92_block(entry, failures, msg, ctx=None):
    entry["blocked"] = msg
    entry.setdefault("coverage_blocked", []).append(msg)
    if ctx is not None:
        for proc in ctx.get("procs") or ():
            _fc92_reap(proc)
        for name in list(ctx.get("loads") or {}):
            entry.setdefault("unloads", {})[name] = _fc92_unload_ns(ctx,
                                                                   name)
    entry["failures"] = failures
    return entry
"""
F7_CTX_NEW = """def _fc92_block(entry, failures, msg):
    entry["blocked"] = msg
    entry.setdefault("coverage_blocked", []).append(msg)
    entry["failures"] = failures
    return entry
"""


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    src, dst = args[0], args[1]
    apply_all = "--all" in sys.argv
    only_secondary = "--only-secondary" in sys.argv
    only_ctx = "--only-ctx" in sys.argv
    s = Path(src).read_text()

    if not only_secondary and not only_ctx:
        s = must_replace(s, F1_OLD, F1_NEW, 1, "F1 shift_ok body")
        s = must_replace(s, "    ok, ks = _fc92_shift_ok(",
                         "    ok = _fc92_shift_ok(",
                         4, "F1 call sites (ok, ks)")
        s = must_replace(s, "    ok, _ks = _fc92_shift_ok(",
                         "    ok = _fc92_shift_ok(",
                         1, "F1 call site (ok, _ks)")
        s = must_replace(s, F2_OLD, F2_NEW, 1, "F2 d_fhi")
        s = must_replace(s, F3_OLD, F3_NEW, 1, "F3 a_ports_none")
        s = must_replace(s, F4_OLD, F4_NEW, 1, "F4 i_* load half")
        s = must_replace(s, F5_HELPER_OLD, F5_HELPER_NEW, 1,
                         "F5 helper insert")
        s = must_replace(s, F5_OLD, F5_NEW, 4, "F5 gate call sites")
    if apply_all or only_secondary:
        s = must_replace(s, F6_VALID_HELPER_OLD, F6_VALID_HELPER_NEW, 1,
                         "F6 helper insert")
        s = must_replace(s, F6_VALID_OLD_DSP, F6_VALID_NEW_DSP, 1,
                         "F6 dsp validity gate")
        s = must_replace(s, F6_VALID_OLD_IR, F6_VALID_NEW_IR, 1,
                         "F6 ir validity gate")
    if apply_all or only_secondary or only_ctx:
        s = must_replace(s, F7_CTX_OLD, F7_CTX_NEW, 1, "F7 ctx branch")

    tree = ast.parse(s)  # refuse a syntactically broken fold
    del tree
    src_lines = Path(src).read_text().count(chr(10))
    Path(dst).write_text(s)
    out = Path(dst).read_bytes()
    print(f"folded {dst}")
    print(f"  sha256 {hashlib.sha256(out).hexdigest()}")
    print(f"  lines {s.count(chr(10))} (source {src_lines}, "
          f"delta {s.count(chr(10)) - src_lines})")
    print(f"  set: {'all(F1-F7)' if apply_all else 'secondary(F6-F7)' if only_secondary else 'ctx-only(F7)' if only_ctx else 'primary(F1-F5)'}")


if __name__ == "__main__":
    main()
