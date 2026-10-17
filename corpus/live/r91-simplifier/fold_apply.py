#!/usr/bin/env python3
"""The r91 (gstfrz) block folds — exact-string, occurrence-asserted.

Usage: fold_apply.py <tree> <fold>

  fold 1  delete the dead `hooks` timed-event mechanism from
          `_gstfrz_r91_leg` (the parameter, its init, its loop) — the
          r91 block's own live mechanism is `gates`; `hooks` is never
          supplied by any of the 10 call sites in the whole module.
  fold 2  delete the dead knobs `want_state_drop` / `want_header` from
          `_gstfrz_r91_frozen_checks` (1/1 call site supplies only
          `want_silent`) and unwrap the two conditions they guarded.

Every replacement asserts its own occurrence count, so a drifted tree
refuses instead of folding something else. Writes the file in place and
prints the before/after sha256 + line count.
"""
import hashlib
import pathlib
import sys

FOLD1 = [
    # (needle, replacement, expected occurrences)
    ("                    hooks=(), gates=(), stdout_cap=262144,\n",
     "                    gates=(), stdout_cap=262144,\n", 1),
    ("    pending = sorted(hooks, key=lambda h: h[0])\n", "", 1),
    ("        while pending and el >= pending[0][0]:\n"
     "            _, kind, payload = pending.pop(0)\n"
     "            try:\n"
     "                res = _gstfrz_r91_hook(kind, payload)\n"
     "            except Exception as exc:            "
     "# a hook must not kill the loop\n"
     "                res = {\"exc\": repr(exc)[:200]}\n"
     "            rec[\"fired\"].append({\"at\": round(el, 3), "
     "\"kind\": kind,\n"
     "                                 \"result\": res})\n", "", 1),
]

FOLD2 = [
    ("                              want_silent=True, want_state_drop=True,\n"
     "                              want_header=True, margin=0.2):\n",
     "                              want_silent=True, margin=0.2):\n", 1),
    ("    if want_state_drop and states and states[-1] == \"running\":\n",
     "    if states and states[-1] == \"running\":\n", 1),
    ("    if want_header and (out.get(\"riff_size\") != "
     "GSTFRZ_R91_RIFF_SIZE or\n"
     "                        out.get(\"data_declared\") != "
     "GSTFRZ_R91_DATA_SIZE):\n",
     "    if (out.get(\"riff_size\") != GSTFRZ_R91_RIFF_SIZE or\n"
     "            out.get(\"data_declared\") != GSTFRZ_R91_DATA_SIZE):\n", 1),
]

FOLDS = {"1": FOLD1, "2": FOLD2}


def main():
    tree, fold = pathlib.Path(sys.argv[1]), sys.argv[2]
    path = tree / "corpus" / "fixtures" / "measure_audio.py"
    src = path.read_text()
    before = hashlib.sha256(src.encode()).hexdigest()
    for needle, repl, want in FOLDS[fold]:
        n = src.count(needle)
        assert n == want, f"fold {fold}: occurrence {n} != {want} for " \
                          f"{needle[:60]!r}"
        src = src.replace(needle, repl)
    path.write_text(src)
    after = hashlib.sha256(src.encode()).hexdigest()
    print(f"tree={tree} fold={fold}")
    print(f"  before sha256 {before}  ({len(src.splitlines())} lines)")
    print(f"  after  sha256 {after}  ({len(src.splitlines())} lines)")


if __name__ == "__main__":
    main()
