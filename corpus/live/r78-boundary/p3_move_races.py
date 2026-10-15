#!/usr/bin/env python3
"""r78b p3 — move-sink-input races and hostile indices."""
import os, sys, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r78b_lib import *

out = {"probe": "p3-move-races", "ts": time.time(),
       "env": foreign_note()}
out["cleanup"] = unload_all_mine()
TONE6 = os.path.join(RAW, "tone6.wav")
make_tone(TONE6, dur=6.0)
make_tone(TONE, dur=1.8)

m1, _, _ = load_null(NS, "r78b probe A")
m2, _, _ = load_null(NS2, "r78b probe B")
time.sleep(0.6)
out["mods"] = {"ns": m1, "ns2": m2}
legs = {}

def mv(idx, dest):
    rc, o, e, w, to = pactl("move-sink-input", str(idx), str(dest))
    return f"rc={rc} err={e.strip()[:70]}"

def idx_of(tag):
    return sink_input_index(tag)

# -- L1 baseline move ns -> ns2 ------------------------------------------
tag = "r78bE_base"
def _mv1():
    i = idx_of(tag)
    return f"idx={i} " + (mv(i, NS2) if i is not None else "NOIDX")
legs["baseline_ns_to_ns2"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=12.0, actions=[(2.0, _mv1)], timeline_every=0.4)

# -- L2 move to nonexistent sink ------------------------------------------
tag = "r78bE_nosuch"
def _mv2():
    i = idx_of(tag)
    return f"idx={i} " + (mv(i, "no_such_sink_r78b") if i is not None else "NOIDX")
legs["move_nonexistent"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=12.0, actions=[(2.0, _mv2)], timeline_every=0.5)

# -- L3 rapid double move ns -> ns2 -> spdif -------------------------------
tag = "r78bE_double"
def _mv3a():
    i = idx_of(tag); return f"idx={i} " + (mv(i, NS2) if i is not None else "NOIDX")
def _mv3b():
    i = idx_of(tag); return f"idx={i} " + (mv(i, S_SPDIF) if i is not None else "NOIDX")
legs["double_move_50ms"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=12.0, actions=[(2.0, _mv3a), (2.06, _mv3b)],
    timeline_every=0.25)

# -- L4 move then unload destination --------------------------------------
tag = "r78bE_mvkill"
def _mv4():
    i = idx_of(tag); return f"idx={i} " + (mv(i, NS2) if i is not None else "NOIDX")
def _kill4():
    r = unload(m2); return f"unload_rc={r[0]}"
legs["move_then_unload_dest"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=13.0, actions=[(2.0, _mv4), (2.35, _kill4)],
    timeline_every=0.35)

# -- L5 hostile indices ----------------------------------------------------
tag = "r78bE_idx"
def _mv5a():  # stale index: a dead stream's index (use a definitely-dead one)
    return "staleidx " + mv(999999, NS2)
def _mv5b():  # source name as destination
    i = idx_of(tag); return f"idx={i} " + (mv(i, LINE) if i is not None else "NOIDX")
def _mv5c():  # monitor name as destination
    i = idx_of(tag); return f"idx={i} " + (mv(i, f"{NS}.monitor") if i is not None else "NOIDX")
legs["hostile_indices"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=12.0, actions=[(1.6, _mv5a), (2.2, _mv5b), (2.8, _mv5c)],
    timeline_every=0.5)

# -- L6 move of a source-output index into sink-input verb -----------------
# start an OWN capture so it has a source-output index, then try to move it
cap = subprocess.Popen(
    ["pw-record", "-P", "node.name=r78bE_cap", "-P",
     "stream.capture.sink=true", "--target", NS, "--format", "s16",
     "--rate", "48000", "--channels", "2",
     os.path.join(RAW, "p3cap.wav")],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
d, _, _ = pactl_json("list", "source-outputs")
so_idx = None
if isinstance(d, list):
    for it in d:
        if (it.get("properties", {}) or {}).get("node.name") == "r78bE_cap":
            so_idx = it.get("index")
out["src_output_idx"] = so_idx
rc, o_, e_, _, _ = pactl("move-sink-input", str(so_idx), NS2) \
    if so_idx is not None else (None, b"", "noidx")
out["move_source_output_as_sink_input"] = {"idx": so_idx, "rc": rc,
                                           "err": e_.strip()[:120]}
cap.send_signal(signal.SIGTERM); cap.wait(timeout=5)

# -- L7 move during unlinked_sustained_playout (revive by move?) -----------
tag = "r78bE_revive"
def _unlink():
    r1 = sh(["pw-link", "-d", f"{tag}:output_FL"], timeout=6)
    r2 = sh(["pw-link", "-d", f"{tag}:output_FR"], timeout=6)
    return f"d1={r1[0]} d2={r2[0]}"
def _mv7():
    i = idx_of(tag); return f"idx={i} " + (mv(i, NS2) if i is not None else "NOIDX")
legs["move_after_manual_unlink"] = play_leg(
    ["pw-play", "-P", f"node.name={tag}", "--target", NS, TONE6],
    tag, timeout=13.0, actions=[(1.8, _unlink), (2.6, _mv7)],
    timeline_every=0.35)

out["legs"] = legs
out["post_cleanup"] = unload_all_mine()
out["post_default"] = get_default_sink()
save("probe-p3-move-races-r78b.json", out)
for k, l in legs.items():
    print(f"== {k}: rc={l['rc']} wall={l['wall_s']} carried={l['carried']}")
    print("   actions:", l["actions"])
    tl = [(t, {p.split(':')[0][-14:]: [x.split(':')[0][:26] for x in v]
               for p, v in c.items()}) for t, c in l["timeline"]]
    for t, c in tl:
        print("   t", t, c)
