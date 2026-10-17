import hashlib, wave
from pathlib import Path
import numpy as np
root=Path(__file__).resolve().parents[3]
art=root/"artifacts"; out=Path(__file__).resolve().parent
with wave.open(str(art/"stem_layer_third.wav"),"rb") as w:
    src=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").astype(np.float64)/32767
t=np.arange(len(src))/48000
common=.08*np.sin(2*np.pi*220*t)+.04*np.sin(2*np.pi*330*t)
base=np.round(np.clip(src+common,-1,1)*32767).astype("<i2")
for name,target in (("alt_pass",838),("alt_fail",839)):
    x=base.copy(); x[96000]=target; x[96001]=x[96000]+x[95999]-x[95998]
    path=out/f"{name}.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(x.tobytes())
    print(name,"sha256="+hashlib.sha256(path.read_bytes()).hexdigest(),"four_counts="+repr(x[95998:96002].tolist()),"join_counts="+str(abs(int(x[96000])-int(x[95999]))))
