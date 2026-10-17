#!/usr/bin/env python3
"""Create the original one-sample-side slope mismatch probe for round 11."""
from pathlib import Path
import wave
import numpy as np

root = Path(__file__).resolve().parents[2]
source = root / "artifacts" / "stem_layer.wav"
dest = Path(__file__).resolve().parent / "slope_candidate.wav"
with wave.open(str(source), "rb") as wav:
    params = wav.getparams()
    samples = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").copy()
# Add 0.0004 FS at the first sample to the right of the internal boundary.
samples[96001] = round(samples[96001] + 0.0004 * 32767)
with wave.open(str(dest), "wb") as wav:
    wav.setparams(params)
    wav.writeframes(samples.tobytes())
print(dest)
