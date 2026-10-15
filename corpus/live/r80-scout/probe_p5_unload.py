#!/usr/bin/env python3
"""P5 — module-index allocation law + the unload argument matrix.

Board is enumerated before/after every single operation, and every unload's
rc is recorded (the p4 run left unverified unloads; this one does not).
REPS reps per row.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r80_probe import Receipt, load, unload, pactl, snap

REPS = 3
T = "r80_p5"


def mods():
    r = pactl("list", "short", "modules")
    out = {}
    for ln in r["stdout"].splitlines():
        f = ln.split("\t")
        if len(f) >= 2 and f[0].strip().isdigit():
            out[int(f[0])] = f[1].strip()
    return out


def ours(m):
    return {k: v for k, v in m.items() if k >= 536870912 and T in json.dumps(v) or
            (k >= 536870912 and v == "module-null-sink" and k in OWNED)}


OWNED = set()


def alloc_probe(rc, rep):
    """Clean board first: only kill modules this seat created (never by name)."""
    global OWNED
    before = mods()
    seq = []
    live = dict(before)
    # load 4 one at a time, record live set after each
    idxs = []
    for i in range(4):
        idx, r = load("module-null-sink", f"sink_name={T}_a{i}")
        idxs.append(idx)
        if idx:
            OWNED.add(idx)
        live = mods()
        seq.append({"op": f"load a{i}", "idx": idx, "rc": r["rc"],
                    "err": r["stderr"].strip(), "live_after": sorted(live)})
    # unload the 2nd (verified), reload
    u1 = unload(idxs[1])
    live = mods()
    seq.append({"op": "unload a1", "idx": idxs[1], "rc": u1["rc"],
                "err": u1["stderr"].strip(), "live_after": sorted(live)})
    idx_n, r_n = load("module-null-sink", f"sink_name={T}_b")
    if idx_n:
        OWNED.add(idx_n)
    live = mods()
    seq.append({"op": "load b", "idx": idx_n, "rc": r_n["rc"],
                "err": r_n["stderr"].strip(), "live_after": sorted(live),
                "reused_a1": idx_n == idxs[1]})
    # unload a3 then reload -> lowest free?
    u2 = unload(idxs[3])
    idx_m, r_m = load("module-null-sink", f"sink_name={T}_c")
    if idx_m:
        OWNED.add(idx_m)
    live = mods()
    seq.append({"op": "unload a3 then load c", "unloaded": idxs[3], "u_rc": u2["rc"],
                "idx": idx_m, "rc": r_m["rc"], "err": r_m["stderr"].strip(),
                "live_after": sorted(live), "reused_a3": idx_m == idxs[3]})
    # unload a0 (lowest of ours) then reload -> lowest free?
    u3 = unload(idxs[0])
    idx_k, r_k = load("module-null-sink", f"sink_name={T}_d")
    if idx_k:
        OWNED.add(idx_k)
    live = mods()
    seq.append({"op": "unload a0 then load d", "unloaded": idxs[0], "u_rc": u3["rc"],
                "idx": idx_k, "rc": r_k["rc"], "err": r_k["stderr"].strip(),
                "live_after": sorted(live), "reused_a0": idx_k == idxs[0]})
    rc.leg(f"alloc-rep{rep}", {"before": sorted(before), "seq": seq})
    rc.note(f"rep{rep} alloc: a={idxs} b={idx_n}(reuse_a1={idx_n==idxs[1]}) "
            f"c={idx_m}(reuse_a3={idx_m==idxs[3]}) d={idx_k}(reuse_a0={idx_k==idxs[0]}) "
            f"before={sorted(before)}")
    # cleanup ONLY our indices, with rc
    cl = []
    for i in list(OWNED):
        u = unload(i)
        cl.append({"idx": i, "rc": u["rc"], "err": u["stderr"].strip()})
        OWNED.discard(i)
    rc.leg(f"alloc-cleanup-rep{rep}", {"cleanup": cl})
    rc.note(f"rep{rep} cleanup {cl}")


def unload_matrix(rc, rep):
    """(arg form) x (module state) -> (rc, stderr). Every leg creates its own
    module and never touches a foreign index."""
    rows = []
    for label, argfn in [
        ("bare-live", lambda i: str(i)),
        ("hash-live", lambda i: f"#{i}"),
        ("bare-dead", lambda i: str(i)),
        ("hash-dead", lambda i: f"#{i}"),
        ("bare-below-base", lambda i: "536870000"),
        ("bare-name-string", lambda i: "module-null-sink"),
        ("bogus-string", lambda i: "no-such-module-name"),
        ("bare-huge", lambda i: "999999999"),
    ]:
        idx, r = load("module-null-sink", f"sink_name={T}_m_{label}")
        time.sleep(0.25)
        before = mods()
        if label.endswith("dead"):
            unload(idx)                      # kill it first, then address the dead index
            time.sleep(0.25)
            alive_before = idx in mods()
        else:
            alive_before = idx in mods()
        arg = argfn(idx)
        if label == "bare-name-string":
            # this form nukes EVERY instance of the name incl. foreign ones:
            # only run it when no foreign null-sink module is live.
            foreign = [k for k, v in mods().items()
                       if v == "module-null-sink" and k not in OWNED and k != idx]
            if foreign:
                rows.append({"label": label, "skipped": "foreign module-null-sink live",
                             "foreign": foreign})
                rc.note(f"rep{rep} {label} SKIPPED (foreign null-sink modules live: {foreign})")
                unload(idx)
                continue
        u = pactl("unload-module", arg)
        time.sleep(0.3)
        after = mods()
        rows.append({"label": label, "arg": arg, "created_idx": idx, "load_rc": r["rc"],
                     "alive_before": alive_before, "unload": u,
                     "alive_after": idx in after, "before": sorted(before),
                     "after": sorted(after)})
        rc.note(f"rep{rep} {label:18s} arg={arg!r} alive_before={alive_before} "
                f"rc={u['rc']} err={u['stderr'].strip()[:60]!r} alive_after={idx in after}")
        if idx in after:
            unload(idx)
        time.sleep(0.2)
    rc.leg(f"unload-matrix-rep{rep}", {"rows": rows})


def main():
    rc = Receipt("p5-index-law")
    rc.note("board at start: " + json.dumps(mods()))
    for rep in range(REPS):
        alloc_probe(rc, rep)
    for rep in range(REPS):
        unload_matrix(rc, rep)
    rc.leg("board-at-end", {"mods": mods()})
    rc.close()


if __name__ == "__main__":
    main()
