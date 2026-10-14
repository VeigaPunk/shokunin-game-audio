import json, subprocess, wave
from pathlib import Path
import numpy as np
R=48000; out=Path(__file__).parent
t=np.arange(5760)/R
def save(name,k):
 x=.38*np.sin(2*np.pi*(700*k*t+800*k*t*t))*np.exp(-30*t)
 pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2")
 p=out/(name+".wav")
 with wave.open(str(p),"wb") as w:
  w.setnchannels(1); w.setsampwidth(2); w.setframerate(R); w.writeframes(pcm.tobytes())
 return p
def measure(p):
 q=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate,channels,codec_name,bits_per_sample:format=duration","-of","json",str(p)],check=True,capture_output=True).stdout)
 pcm=subprocess.run(["sox",str(p),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout
 x=np.frombuffer(pcm,dtype="<f4").astype(float); f=np.fft.rfftfreq(len(x),1/R); a=np.abs(np.fft.rfft(x)); c=float(f@a/a.sum())
 return {"duration":q["format"]["duration"],"rate":q["streams"][0]["sample_rate"],"channels":q["streams"][0]["channels"],"codec":q["streams"][0]["codec_name"],"bits":q["streams"][0]["bits_per_sample"],"peak":float(np.max(np.abs(x))),"rms":float(np.sqrt(np.mean(x*x))),"centroid":c}
base=measure(save("baseline",1.0)); rows=[]
for k in [1.104,1.105,1.106,1.107,1.108,1.109,1.110]:
 p=save("scale_"+str(k),k); m=measure(p); m.update(scale=k,rel=abs(m["centroid"]-base["centroid"])/base["centroid"]); rows.append(m)
print(json.dumps({"baseline":base,"variants":rows},indent=2))
