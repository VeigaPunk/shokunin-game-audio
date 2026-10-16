#!/usr/bin/env python3
"""r86-simplifier symdiff: the fold removes exactly the self_serials
binding and introduces no new unread name in any r86 scope (symtable,
which is comprehension-aware; nested-scope-only reads are reported as
'unreferenced' by symtable and are treated as a known false-positive
class — identical in both copies)."""
import symtable
import sys

B = "base-measure_audio.py"
F = "folded/measure_audio.py"
results = []


def ck(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'PASS' if cond else 'FAIL'} {name} {detail}")


def r86_scopes(path):
    st = symtable.symtable(open(path, encoding="utf-8").read(), path,
                           "exec")
    out = {}

    def walk(s):
        nm = s.get_name()
        if nm.startswith("_pwctl_r86") or nm.endswith("_r86_entry"):
            out[nm] = {
                "symbols": {x.get_name() for x in s.get_symbols()},
                "unread": {x.get_name() for x in s.get_symbols()
                           if x.is_assigned() and not x.is_referenced()
                           and not x.is_parameter()},
            }
        for c in s.get_children():
            walk(c)

    walk(st)
    return out


bs, fs = r86_scopes(B), r86_scopes(F)
ck("SD1 same r86 scope set", set(bs) == set(fs), str(sorted(bs)))
new_unread = {k: fs[k]["unread"] - bs.get(k, {}).get("unread", set())
              for k in fs}
ck("SD2 no new unread names introduced by the fold",
   all(not v for v in new_unread.values()), str(new_unread))
removed = {k: bs[k]["symbols"] - fs[k]["symbols"] for k in bs}
# `s`/`set` are the set-comprehension variable and the builtin name
# referenced ONLY by the two deleted self_serials.append(...) lines.
removed_nonempty = {k: v for k, v in removed.items() if v}
ck("SD3 removed symbols are exactly the self_serials write-site "
   "closure {self_serials, s, set}, nowhere else",
   removed_nonempty == {"pwctl_addr_r86_entry":
                        {"self_serials", "s", "set"}},
   str(removed_nonempty))
added = {k: fs[k]["symbols"] - bs[k]["symbols"] for k in bs}
ck("SD4 no symbols added", all(not v for v in added.values()), str(added))

n_fail = results.count(False)
print(f"\n{len(results) - n_fail}/{len(results)} PASS")
sys.exit(1 if n_fail else 0)
