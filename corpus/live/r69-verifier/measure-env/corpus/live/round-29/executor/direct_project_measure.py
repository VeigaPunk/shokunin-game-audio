import json, runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
fit=Path(__file__).resolve().parent
measure=runpy.run_path(str(ROOT/"fixtures"/"measure_audio.py"))["measure"]
spec=(.12,250,4000,False)
rows={name:measure(name,spec,fit/(name+".wav")) for name in ("baseline","k_0.95","k_0.94")}
base=rows["baseline"]["spectral_centroid_hz"]
for name in ("k_0.95","k_0.94"):
    rows[name]["centroid_relative_delta"] = abs(rows[name]["spectral_centroid_hz"]-base)/base
    rows[name]["duration_delta_s"] = abs(rows[name]["duration_s"]-rows["baseline"]["duration_s"])
receipt={"spec":list(spec),"rows":rows}
(fit/"direct_project_measure.json").write_text(json.dumps(receipt,indent=2)+"\n")
print(json.dumps(receipt,indent=2))
