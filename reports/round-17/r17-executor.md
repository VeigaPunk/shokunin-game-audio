# Round 17 executor — 200 Hz candidate

## Synthesis

I synthesized a scratch-only, original 4 s, 48 kHz mono PCM16 candidate with a 200 Hz sine component, first-half synthesis amplitude `.015` FS and second-half `.050` FS. This checks the proposed coverage shape; it is not a production or perceptual result. Scratch path: `.shokunin/audio/corpus/live/round-17/layer200_candidate.wav`.

Exact synthesis command and exit:

```sh
python3 -c 'import numpy as np,wave; r=48000; t=np.arange(4*r)/r; x=np.where(t<2,.015,.050)*np.sin(2*np.pi*200*t); pcm=np.round(np.clip(x,-1,1)*32767).astype("<i2"); w=wave.open(".shokunin/audio/corpus/live/round-17/layer200_candidate.wav","wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(r); w.writeframes(pcm.tobytes()); w.close()'
```

Exit: **0**.

## Independent decoded measurements

I independently decoded PCM16 samples from the completed WAV using Python `wave` and NumPy (not from the synthesis array). The decode asserted 1 channel, 2-byte samples, 48,000 Hz, and exactly 192,000 frames. For section amplitude I computed the magnitude of the 200 Hz FFT bin separately on each 96,000-sample half, scaled by `2/N`. I computed signed contrast as `20*log10(second/first)`. Outer and internal joins use adjacent decoded samples.

Exact decode/measurement command and exit:

```sh
python3 -c 'import hashlib,wave,numpy as np; p=".shokunin/audio/corpus/live/round-17/layer200_candidate.wav"; b=open(p,"rb").read(); w=wave.open(p,"rb"); assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(1,2,48000,192000); x=np.frombuffer(w.readframes(w.getnframes()),dtype="<i2").astype(np.float64)/32768; w.close(); halves=np.split(x,2); amps=[2*abs(np.fft.rfft(z)[200*len(z)//48000])/len(z) for z in halves]; delta=20*np.log10(amps[1]/amps[0]); centroid=np.dot(np.fft.rfftfreq(len(x),1/48000),abs(np.fft.rfft(x)))/abs(np.fft.rfft(x)).sum(); peak=abs(x).max(); rms=(np.mean(x*x))**.5; outer=abs(x[0]-x[-1]); outer_slope=abs((x[-1]-x[-2])-(x[1]-x[0])); jgap=abs(x[96000]-x[95999]); jslope=abs((x[96001]-x[96000])-(x[95999]-x[95998])); print("format=mono PCM16/48000/192000 duration=4.0"); print("sha256="+hashlib.sha256(b).hexdigest()); print("peak=%.12f rms=%.12f centroid=%.12f outer_gap=%.12f outer_slope=%.12f"%(peak,rms,centroid,outer,outer_slope)); print("200Hz_section_amplitudes=%r contrast_db=%.12f internal_gap=%.12f internal_slope=%.12f"%(amps,delta,jgap,jslope))'
```

Exit: **0**. Results:

- Format/duration: mono PCM16, 48,000 Hz, 192,000 frames (4.000 s).
- SHA-256: `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`.
- Peak `.049987792969` FS; RMS `.026099826320` FS (above `.001`, below `.95` peak cap).
- Whole-wave FFT-magnitude weighted centroid `287.938059238444` Hz, within generic 100–2,000 Hz band.
- Outer endpoint gap `.001312255859` FS (≤ `.03`); outer slope mismatch `.000915527344` FS/sample (≤ `.001`).
- Decoded section 200 Hz amplitudes `[.014999984892417233, .04999803906398615]` FS; both meet `.01` minimum. Signed second/first contrast `+10.457242997641` dB (≥ `+6`).
- Internal join adjacent gap `.000396728516` FS (≤ `.03`); internal side-slope mismatch `.000915527344` FS/sample (≤ `.001`).

Format was independently checked by ffprobe:

```sh
ffprobe -v error -show_entries stream=sample_rate,channels,bits_per_sample:format=duration -of json .shokunin/audio/corpus/live/round-17/layer200_candidate.wav
```

Exit: **0**. It reported 48,000 Hz, mono, 16 bits/sample, duration 4.000000 s.

## Fit outcome and limits

This proposed `.015/.050` fit passes the generic level, centroid, outer seam, section-amplitude contrast/validity, and internal join checks with the recorded thresholds. No alternate/failed synthesis fits were attempted in this executor lane. This is scratch-only author evidence, not runner integration or independent verification; the waveform is a generated deterministic fixture. It supports no claim about audibility, seamlessness as heard, musical quality, engine behavior, or production suitability.
