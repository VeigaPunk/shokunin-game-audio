import hashlib
import importlib.util
import wave
from pathlib import Path
import numpy as np

base = Path(__file__).resolve().parents[4]
out = Path(__file__).resolve().parent
rate = 48000
n = np.arange(5760)
t = n / rate
spec = importlib.util.spec_from_file_location("measure_audio", base / "corpus/fixtures/measure_audio.py")
measure_audio = importlib.util.module_from_spec(spec)
spec.loader.exec_module(measure_audio)
for label, frequency in (("below", 3982), ("above", 3985)):
    samples = .28 * np.sin(2 * np.pi * frequency * t) * np.hanning(len(n))
    pcm = np.rint(np.clip(samples, -1, 1) * 32767).astype("<i2")
    path = out / f"alt-ui-upper-{label}.wav"
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())
    result = measure_audio.measure("ui", measure_audio.SPECS["ui"], path.resolve())
    print(label, "sha256=" + hashlib.sha256(path.read_bytes()).hexdigest(), result)
