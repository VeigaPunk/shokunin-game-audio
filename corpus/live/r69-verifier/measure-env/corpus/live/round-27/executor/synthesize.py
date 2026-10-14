import numpy as np, wave
from pathlib import Path
out=Path(__file__).parent
rate=48000
for name,n in (("base",5760),("var6719",6719),("var6720",6720)):
    t=np.arange(n,dtype=np.float64)/rate
    # Extend the same UI analytic waveform used for every duration: chirped sine with exponential decay.
    x=.38*np.sin(2*np.pi*(700*t+800*t*t))*np.exp(-30*t)
    pcm=np.round(np.clip(x,-1,1)*32767).astype('<i2')
    with wave.open(str(out/(name+'.wav')),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes())
