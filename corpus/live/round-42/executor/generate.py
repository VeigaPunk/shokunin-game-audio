import hashlib, math, wave
from pathlib import Path
import numpy as np
out=Path(__file__).parent
for peak_count in (31129,31130):
    n=np.arange(5760,dtype=np.float64)
    pcm=np.rint(peak_count*np.cos(2*math.pi*1000*n/48000)).astype("<i2")
    assert int(np.max(pcm))==peak_count and int(np.min(pcm))==-peak_count
    path=out/f"ui-peak-{peak_count}.wav"
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(pcm.tobytes())
    print(path.name, len(pcm), int(pcm.max()), int(pcm.min()), hashlib.sha256(path.read_bytes()).hexdigest())
