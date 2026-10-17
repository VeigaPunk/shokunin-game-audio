import hashlib, wave
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[3]
source=root/"artifacts/stem_layer_third.wav"
out=Path(__file__).resolve().parent
with wave.open(str(source),"rb") as w:
    assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,48000,192000)
    original=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").copy()
t=np.arange(192000)/48000
base=np.where(t<2,.015,.050)*np.sin(2*np.pi*200*t)+.08*np.sin(2*np.pi*220*t)+.04*np.sin(2*np.pi*330*t)
frames=np.round(np.clip(base,-1,1)*32767).astype("<i2")
print("base join counts",frames[95998:96002].tolist())
for tag,target in (("pass983",838),("fail984",839)):
    pcm=frames.copy()
    pcm[96000]=target
    pcm[96001]=pcm[96000]+pcm[95999]-pcm[95998]
    path=out/f"join200_{tag}.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(48000);w.writeframes(pcm.astype("<i2").tobytes())
    print(f"{path}: sha256={hashlib.sha256(path.read_bytes()).hexdigest()}, frames95998:96002={pcm[95998:96002].tolist()}")
