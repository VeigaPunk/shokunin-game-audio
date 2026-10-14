import wave, struct, math, subprocess, json, numpy as np
from pathlib import Path
out=Path(__file__).parent
rate=48000
# Analytic chirp envelope matching the existing synthetic UI fixture equation.
for label,n in (("base",5760),("n6719",6719),("n6720",6720)):
    with wave.open(str(out/(label+".wav")),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        frames=[]
        for i in range(n):
            t=i/rate; x=.38*math.sin(2*math.pi*(700*t+800*t*t))*math.exp(-30*t)
            frames.append(struct.pack("<h",round(x*32767)))
        w.writeframes(b"".join(frames))
def info(path):
    p=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate,channels,codec_name,bits_per_sample:format=duration","-of","json",str(path)],check=True,capture_output=True,text=True).stdout)
    raw=subprocess.run(["sox",str(path),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout
    x=np.frombuffer(raw,dtype="<f4").astype(np.float64); rate=int(p["streams"][0]["sample_rate"]); f=np.fft.rfftfreq(len(x),1/rate); a=np.abs(np.fft.rfft(x)); c=float(np.dot(f,a)/a.sum())
    return {"duration":float(p["format"]["duration"]),"samples":len(x),"centroid_hz":c,"stream":p["streams"][0]}
rows={k:info(out/(k+".wav")) for k in ("base","n6719","n6720")}
for k in ("n6719","n6720"):
    d=abs(rows[k]["duration"]-rows["base"]["duration"]); c=abs(rows[k]["centroid_hz"]-rows["base"]["centroid_hz"])/rows["base"]["centroid_hz"]
    print(k,json.dumps(rows[k]),"duration_delta",repr(d),"centroid_relative_delta",repr(c),"duration_branch",d>=.020,"centroid_branch",c>=.10,"both_pass",d>=.020 or c>=.10)
print("base",json.dumps(rows["base"]))
