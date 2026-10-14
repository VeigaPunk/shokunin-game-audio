import sys, pathlib, wave, json
import numpy as np
sys.path.insert(0, str(pathlib.Path(".shokunin/audio/corpus/fixtures").resolve()))
from measure_audio import measure, SPECS
out=pathlib.Path(".shokunin/audio/corpus/live/round-28/executor")
rate=48000; n=5760; t=np.arange(n)/rate
rows={}
for label, f0 in [("baseline",700.0),("below",630.0),("above",626.0)]:
    x=.38*np.sin(2*np.pi*(f0*t+800*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2")
    p=(out/(label+".wav")).resolve()
    with wave.open(str(p),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
    rows[label]={"parameter_f0_hz":f0,"frames":len(pcm),"measurements":measure(label,SPECS["ui"],p)}
for label in ("below","above"):
    b=rows["baseline"]["measurements"]; v=rows[label]["measurements"]
    dr=abs(v["duration_s"]-b["duration_s"])
    cr=abs(v["spectral_centroid_hz"]-b["spectral_centroid_hz"])/b["spectral_centroid_hz"]
    rows[label]["comparison"]={"baseline":"baseline","duration_delta_s":dr,"centroid_relative_delta":cr,"distinctness_pass":dr>=.020 or cr>=.10}
receipt={"generator":".38*sin(2*pi*(f0*t+800*t*t))*exp(-30*t); t=arange(5760)/48000; round/clip PCM16","sample_rate_hz":48000,"frames":5760,"ui_spec":list(SPECS["ui"]),"rows":rows}
(out/"fit-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
for k,v in rows.items(): print(k,v["parameter_f0_hz"],v["measurements"]["spectral_centroid_hz"],v.get("comparison"),v["measurements"]["failures"])
