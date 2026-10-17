import json, sys
from pathlib import Path
for p in sys.argv[1:]:
    recs = json.loads(Path(p).read_text())
    print(f"### {p}  ({len(recs)} cells)")
    for r in recs:
        ri = r.get("riff") or {}
        pr = r.get("probe") or {}
        dur = pr.get("duration")
        dur = f"{dur:.3f}" if isinstance(dur, float) else str(dur)
        print(f"{r['cell']:34s} rc={str(r.get('rc')):>5s} wall={r.get('wall_s'):>7} "
              f"size={str(r.get('size')):>9s} riff={str(ri.get('wave')):5s} "
              f"decl={str(ri.get('declared')):>10s} act={str(ri.get('actual')):>9s} "
              f"data={str(ri.get('data_declared')):>10s} probe_rc={pr.get('rc')} dur={dur} "
              f"rate={pr.get('rate')} ch={pr.get('ch')} codec={pr.get('codec')} "
              f"killed={r.get('killed_by')} | {r.get('stdout_tail','')[-90:]!r}")
