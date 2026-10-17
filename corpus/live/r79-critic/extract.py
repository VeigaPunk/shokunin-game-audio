import json,sys,collections
R=json.load(open(sys.argv[1]))
ms=R.get("measurements") or R
if isinstance(ms,list):
    d={m.get("name") or m.get("probe"):m for m in ms}
else:
    d=ms
print("TOPKEYS", list(R.keys())[:20])
for k,v in d.items():
    if "r79" not in str(k): continue
    print("="*70); print("ENTRY",k)
    print(" failures:", json.dumps(v.get("failures"))[:600])
    print(" coverage_blocked:", json.dumps(v.get("coverage_blocked"))[:400])
    print(" named_outcomes:", json.dumps(v.get("named_outcomes"))[:900])
    print(" confound_observed:", v.get("confound_observed"))
    legs=v.get("legs") or {}
    for ln,l in legs.items():
        if not isinstance(l,dict): continue
        print("  LEG",ln,"|kind",l.get("expected_kind"),"|outcome",l.get("outcome"),
              "|producers",l.get("producers_union"),"|exp",l.get("expected_producers"),
              "|consumers",l.get("consumers_union"),"|expc",l.get("expected_consumers"),
              "|confound",(l.get("confound") or "")[:90])
        print("       tail",l.get("tail"),"|oracle",json.dumps(l.get("oracle_at_leg")),
              "|fed",l.get("fed"),"|lies",l.get("target_object_lies"),
              "|adv",l.get("target_object_advertised"),"|req",l.get("target_requested"))
        t=l.get("tap") or {}
        if t: print("       tap",{kk:t.get(kk) for kk in ("target","bound_to_target","bound_producers","never_bound","ran","carries_tone","mine_windows","peak_l","peak_r")})
        if l.get("foreign_tone_witness"): print("       FTW",l["foreign_tone_witness"])
