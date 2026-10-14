import json, math, wave, subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
RATE=48000; t=np.arange(5760)/RATE
def save(name,k):
    x=.38*np.sin(2*np.pi*(700*k*t+800*k*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2")
    p=OUT/(name+".wav")
    with wave.open(str(p),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm.tobytes())
    return p
def measured(p):
    probe=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate,channels,codec_name,bits_per_sample:format=duration","-of","json",str(p)],check=True,capture_output=True,text=True).stdout)
    raw=subprocess.run(["sox",str(p),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout
    x=np.frombuffer(raw,dtype="<f4").astype(np.float64); f=np.fft.rfftfreq(len(x),1/RATE); a=np.abs(np.fft.rfft(x)); c=float(np.dot(f,a)/a.sum())
    stream=probe["streams"][0]; duration=float(probe["format"]["duration"]); peak=float(np.max(np.abs(x))); rms=float(np.sqrt(np.mean(x*x)))
    return {"duration_s":duration,"frames":len(x),"rate":int(stream["sample_rate"]),"channels":int(stream["channels"]),"codec":stream["codec_name"],"bits":int(stream["bits_per_sample"]),"peak":peak,"rms":rms,"centroid_hz":c}
base=save("baseline",1.0); bm=measured(base)
results=[]
for k in [0.960,0.955,0.950,0.945,0.940,0.935,0.930,0.925,0.920]:
    p=save("k_"+str(k),k); m=measured(p); d=abs(m["centroid_hz"]-bm["centroid_hz"])/bm["centroid_hz"]
    fails=[]
    if abs(m["duration_s"]-.12)>.001:fails.append("duration")
    if m["rate"]!=48000 or m["channels"]!=1 or m["codec"]!="pcm_s16le" or m["bits"]!=16:fails.append("format")
    if m["peak"]>=.95 or m["rms"]<.001:fails.append("level")
    if not 250<=m["centroid_hz"]<=4000:fails.append("centroid-band")
    results.append({"k":k,"measurement":m,"relative_delta":d,"class":"below" if d<.10 else "above","ordinary_failures":fails})
(OUT/"sweep.json").write_text(json.dumps({"baseline":bm,"results":results},indent=2)+"\n")
print(json.dumps({"baseline":bm,"results":results},indent=2))
