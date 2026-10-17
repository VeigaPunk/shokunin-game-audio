import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(".shokunin/audio/corpus/fixtures").resolve()))
import build_artifacts as b
import measure_audio as m
out=Path(".shokunin/audio/corpus/live/round-29/alt")
t=np.arange(5760)/48000
base=.38*np.sin(2*np.pi*(700*t+800*t*t))*np.exp(-30*t)
b.save("r29_base",base,out)
for k in (.96,.95,.94,.93,.92,.91,.90,.89):
    x=.38*np.sin(2*np.pi*(700*k*t+800*k*t*t))*np.exp(-30*t)
    b.save(f"r29_k{k:.2f}",x,out)
print("baseline",m.measure("ui",m.SPECS["ui"],(Path.cwd()/out/"r29_base.wav").resolve()))
for k in (.96,.95,.94,.93,.92,.91,.90,.89):
    print(k,m.measure("ui",m.SPECS["ui"],(Path.cwd()/out/f"r29_k{k:.2f}.wav").resolve()))
