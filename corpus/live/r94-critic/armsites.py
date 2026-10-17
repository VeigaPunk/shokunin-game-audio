#!/usr/bin/env python3
"""List every _sox_r94_arm / _sox_r94_block / _sox_r94_fail call site with
its full argument text (balanced-paren scan), for false-positive review."""
import re, sys

src = open(sys.argv[1]).read()
lines = src.split("\n")

def sites(name):
    out = []
    for m in re.finditer(r"\b" + name + r"\(", src):
        i = m.end()
        depth = 1
        while i < len(src) and depth:
            if src[i] == "(":
                depth += 1
            elif src[i] == ")":
                depth -= 1
            i += 1
        ln = src[:m.start()].count("\n") + 1
        text = src[m.start():i]
        out.append((ln, text))
    return out

for name in ("_sox_r94_arm", "_sox_r94_block", "_sox_r94_fail"):
    ss = sites(name)
    print("### %s: %d sites" % (name, len(ss)))
    if name == "_sox_r94_arm":
        for ln, t in ss:
            if t.startswith("def "):
                continue
            body = re.sub(r"\s+", " ", t)
            print("%5d %s" % (ln, body[:400]))
