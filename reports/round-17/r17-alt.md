# Round 17 alternate 200 Hz fit (r17-alt)

## Scope and method

I independently synthesized `.shokunin/audio/corpus/live/round-17/layer200_other.wav` as 4 seconds, mono, PCM16 at 48 kHz. It uses a 200 Hz sine with first/second two-second amplitudes `.015/.050` full scale, matching the declared proposed layer geometry. I measured this scratch WAV with the existing `measure_audio.py` functions using the existing 100–2000 Hz, 4-second loop fixture spec, and called `section_contrast(path, 200)` for the 200 Hz component. The current runner does not yet expose a 200 Hz fixture mode, so this is direct scratch analysis, not integrated runner or canonical-fixture evidence.

## Exact commands and results

Synthesis command (exit **0**):

```sh
python3 -c 'import numpy as np, wave; from pathlib import Path; rate=48000; t=np.arange(4*rate)/rate; x=np.where(t<2,.015,.050)*np.sin(2*np.pi*200*t); pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2"); p=Path(".shokunin/audio/corpus/live/round-17"); p.mkdir(parents=True,exist_ok=True); w=wave.open(str(p/"layer200_other.wav"),"wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm.tobytes()); w.close()'
```

Measurement command (exit **0**):

```sh
python3 -c 'import importlib.util, pathlib, hashlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=pathlib.Path(".shokunin/audio/corpus/live/round-17/layer200_other.wav").resolve(); x=m.measure("layer200_other",(4.0,100,2000,True),w); sec=m.section_contrast(w,200); print({"measurement":x,"section":sec,"sha256":hashlib.sha256(w.read_bytes()).hexdigest()})'
```

Results: decoded format 48,000 Hz mono, duration 4.0 s; peak `.04998779296875` FS; RMS `-31.66724765274306 dBFS`; centroid `287.93805923844434 Hz` (within declared 100–2000 Hz fixture band); outer endpoint delta `.001312255859375` FS (≤.03); outer slope mismatch `.00091552734375` FS/sample (≤.001). For the 200 Hz component, measured section amplitudes are `.014999984892417233` and `.04999803906398615` FS (both ≥.01); section RMS `.0106065941723389` and `.03535395349843577` FS (both ≥.001); signed second/first contrast `+10.457242997641432 dB` (≥6). Internal join adjacent gap `.000396728515625` FS (≤.03), and join-side slope mismatch `.00091552734375` FS/sample (≤.001). All these measured gates pass. Scratch SHA-256: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`.

One attempted measurement used a relative path; it failed because the measurement helper requires a path under its resolved corpus root. Exact command (exit **1**, setup/path error, not evidence):

```sh
python3 -c 'import importlib.util, pathlib, hashlib; p=pathlib.Path(".shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=pathlib.Path(".shokunin/audio/corpus/live/round-17/layer200_other.wav"); x=m.measure("layer200_other",(4.0,100,2000,True),w); sec=m.section_contrast(w,200); print({"measurement":x,"section":sec,"sha256":hashlib.sha256(w.read_bytes()).hexdigest()})'
```

I corrected this by resolving the WAV path before measurement. No alternative frequency was needed for this scratch fit. No failed audio fit is claimed. These deterministic fixture measurements establish neither audibility nor engine/production behavior or perceptual quality.
