import sys
from pathlib import Path
import numpy as np
import importlib.util
root=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location("measure_audio", root/"fixtures/measure_audio.py")
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
rate=48000
t=np.arange(2*rate)/rate
samples=.20*np.sin(2*np.pi*90*t) + .025*np.sin(2*np.pi*130*t)
out=Path(__file__).resolve().parent/"ambience_alt_candidate.wav"
module_save=__import__("wave")
import wave
with wave.open(str(out),"wb") as wav:
 wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
 wav.writeframes(np.round(np.clip(samples,-1,1)*32767).astype("<i2").tobytes())
result=module.measure("ambience_alt_candidate",(2.0,5,200,True),out)
print(result)
