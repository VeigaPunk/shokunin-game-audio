import wave,struct,math,subprocess,json,numpy as np
from pathlib import Path
out=Path(__file__).parent
for label,n in (("tone_base",5760),("tone6719",6719),("tone6720",6720)):
 with wave.open(str(out/(label+".wav")),"wb") as w:
  w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
  w.writeframes(b"".join(struct.pack("<h",round(.30*math.sin(2*math.pi*700*i/48000)*math.exp(-20*i/48000)*32767)) for i in range(n)))
def m(k):
 p=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","stream=sample_rate,channels,codec_name,bits_per_sample:format=duration","-of","json",str(out/(k+".wav"))],check=True,capture_output=True,text=True).stdout)
 raw=subprocess.run(["sox",str(out/(k+".wav")),"-t","f32","-e","floating-point","-"],check=True,capture_output=True).stdout; x=np.frombuffer(raw,dtype="<f4").astype(float); f=np.fft.rfftfreq(len(x),1/48000); a=np.abs(np.fft.rfft(x)); return float(p["format"]["duration"]),float(np.dot(f,a)/a.sum())
b=m("tone_base")
for k in ("tone6719","tone6720"):
 q=m(k); d=abs(q[0]-b[0]); c=abs(q[1]-b[1])/b[1]; print(k,"duration",q[0],"centroid",q[1],"duration_delta",repr(d),"centroid_rel",repr(c),"duration_branch",d>=.020,"centroid_branch",c>=.10,"distinct",d>=.020 or c>=.10)
print("tone_base",b)
