# Round 10 join-glitch probe candidate (`r10-probe`)

## Candidate and recipe

Scratch artifact: `corpus/live/round-10/join_candidate.wav` (4 s, mono PCM16, 48 kHz; 192,000 frames). Generated from the checked-in analytic `stem_layer.wav`: decode source PCM16 to float using division by 32767, add a 0.03-FS 60 Hz sinusoid across all frames, round/clamp back to PCM16, then set frame 96000 to `round(0.0305*32767)`. The single-frame edit is at the first sample of the second 2 s section. The added sinusoid keeps the ordinary whole-file centroid within the existing `stem_layer` band; it is not claimed as an audio-quality improvement.

Generation command (exit 0):

```sh
python3 -c 'import wave,numpy as np; from pathlib import Path; src=Path(".shokunin/audio/corpus/artifacts/stem_layer.wav"); dst=Path(".shokunin/audio/corpus/live/round-10/join_candidate.wav");
with wave.open(str(src),"rb") as w:
 p=w.getparams(); x0=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").astype(np.float64)/32767
n=np.arange(len(x0)); x=np.round(np.clip(x0+.03*np.sin(2*np.pi*60*n/48000),-1,1)*32767).astype("<i2"); x[96000]=round(.0305*32767)
with wave.open(str(dst),"wb") as w:
 w.setparams(p); w.writeframes(x.tobytes())
import hashlib; print(hashlib.sha256(dst.read_bytes()).hexdigest())'
```

SHA-256: `2c3b158b6ea3c29f03f785f900b18b36b5c7e26010262ecd4f9285c61bceabe4`.

## Measurement

Measurement command using existing `measure_audio.py` helpers (exit 0):

```sh
python3 -c 'import sys,wave,numpy as np; from pathlib import Path; sys.path.insert(0,".shokunin/audio/corpus/fixtures"); import measure_audio as m; p=Path(".shokunin/audio/corpus/live/round-10/join_candidate.wav").resolve(); a=m.measure("join_candidate",(4.,100,2000,True),p); b=m.section_contrast(p,120); print(a); print(b); w=wave.open(str(p),"rb"); x=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").astype(float)/32767; print("join_jump_full_scale",abs(x[96000]-x[95999]))'
```

Observed: 4.0 s, 48 kHz mono; peak 0.0820618 FS; RMS −28.5827 dBFS; centroid 1769.517 Hz (within 100–2000 Hz fixture band); generic `failures: []`. Outer endpoint delta 0.00119019 FS and outer adjacent-slope delta 0.000732422 FS/sample, both within existing bounds. The two-half 120 Hz component amplitudes are 0.0119996 and 0.0599977 FS; contrast 13.97937 dB, valid/pass (>=6 dB). Decoded PCM adjacent-sample jump at frame boundary (samples 95999→96000) is 0.03091525 FS, exceeding the proposed local 0.03 bound.

## Scope and limits

This is an original analytic PCM scratch negative-control candidate that appears to satisfy generic format/level/duration/spectrum and existing outer-seam checks plus the 120 Hz section contrast while exhibiting the targeted internal sample jump. It supports feasibility of an isolated numeric probe; it does not establish click-free or smooth transitions, perceptual quality, engine/adaptive timing, or a portable/audibility-calibrated threshold. No canonical artifact or shared measurement source was edited.
