import numpy as np
from pathlib import Path
import wave, hashlib
rate=48000
out=Path(__file__).parent
for frames,label in ((5713,"pass-5713"),(5711,"fail-5711")):
    n=np.arange(frames)
    t=n/rate
    samples=.28*np.sin(2*np.pi*(700*t+700*t*t))*np.exp(-5*t)
    pcm=np.rint(np.clip(samples,-1,1)*32767).astype("<i2")
    path=out/(label+".wav")
    with wave.open(str(path),"wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(pcm.tobytes())
    print(f"{path.name} frames={frames} sha256={hashlib.sha256(path.read_bytes()).hexdigest()}")
