# Round 19 executor — one-frame 200 Hz PCM16 boundary pair

## Scope and method

Built two scratch WAVs by copying the original canonical `stem_layer_third.wav` PCM16 frames byte-for-byte, then changing only frame index 96001 (zero-based) by +2 or +3 integer counts. The source at that frame is 43; resulting values are 45 and 46. Files are in `.shokunin/audio/corpus/live/round-19/`. Canonical/source artifacts and fixture code were not changed. WAV format is mono, signed PCM16, 48 kHz, 192000 frames.

Exact commands and exits (run from repository root):

```sh
python3 - <<'PY'
import wave, numpy as np
from pathlib import Path
source=Path('.shokunin/audio/corpus/artifacts/stem_layer_third.wav')
out=Path('.shokunin/audio/corpus/live/round-19')
out.mkdir(parents=True,exist_ok=True)
with wave.open(str(source),'rb') as w:
    frames=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').copy()
for name,delta in [('edgepass_candidate',2),('edgefail_candidate',3)]:
    changed=frames.copy(); changed[96001]+=delta
    with wave.open(str(out/(name+'.wav')),'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000)
        w.writeframes(changed.tobytes())
PY
```
Exit **0**. (The setup was a successful direct Python construction; it did not invoke the project builder or runner.)

Decoded measurements use SoX float32 decode, matching fixture `measure_audio.py`'s decode path. Commands:

```sh
sox .shokunin/audio/corpus/live/round-19/edgepass_candidate.wav -t f32 -e floating-point -
sox .shokunin/audio/corpus/live/round-19/edgefail_candidate.wav -t f32 -e floating-point -
```
Both exit **0**. Exact numerical results are reported below. The section detector is computed over the two 96000-sample halves at the 200 Hz FFT bin, as in `section_contrast`.

## Measurements

| Measure | `edgepass_candidate.wav` (+2) | `edgefail_candidate.wav` (+3) |
|---|---:|---:|
| Full WAV SHA-256 | `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496` | `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38` |
| Source SHA-256 | `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445` | same source |
| Changed PCM16 sample, frame 96001 | 43 → 45 | 43 → 46 |
| Decoded length / format | 192000 / 48000 Hz / mono | 192000 / 48000 Hz / mono |
| Peak full scale | 0.04998779296875 | 0.04998779296875 |
| RMS full scale | 0.026099826336718004 | 0.026099826345174153 |
| Spectral centroid | 291.7447792447708 Hz | 293.69622632525545 Hz |
| Spectral bandwidth | 961.1296239263436 Hz | 979.0114696914828 Hz |
| Outer endpoint delta | 0.001312255859375 | 0.001312255859375 |
| Outer seam slope mismatch | 0.00091552734375 | 0.00091552734375 |
| 200 Hz amplitudes (first, second section) | 0.014999984892417233, 0.049998039097271886 | 0.014999984892417233, 0.049998039113914754 |
| 200 Hz section RMS | 0.0106065941723389, 0.03535395352258335 | 0.0106065941723389, 0.03535395353506875 |
| 200 Hz contrast | 10.457243003423983 dB | 10.45724300631526 dB |
| Internal join sample gap | 0.000396728515625 | 0.000396728515625 |
| Internal join side-slope mismatch | **0.0009765625** | **0.001007080078125** |
| PCM count units (`delta * 32768`) | **32/32768** | **33/32768** |
| Generic format/duration/level/centroid gates | pass | pass |
| Outer endpoint/slope gates | pass | pass |
| Section amplitude/RMS validity and contrast gate | pass | pass |
| Internal join gap gate (`<= .03`) | pass | pass |
| Strict internal slope gate (`> .001` fails) | pass | fail |

The observed slope values equal 32/32768 and 33/32768 exactly in the SoX float32 decode. The comparator already present in the runner is strict `>` against `.001`: .0009765625 passes; .001007080078125 fails. This pair brackets the threshold at adjacent observed count steps for these controlled PCM edits; it does not establish a universal threshold grid for arbitrary signals or decoder paths.

## Independent section and hash verification

The table's whole-file centroid/bandwidth/peak values come from separate FFprobe/SoX/NumPy inspection; the values below for section amplitude and contrast come from the existing `section_contrast` function (FFT implementation and float32 decode). They are intentionally reported from that function and need not reproduce a separately written FFT spot-check.

The earlier direct FFT spot-check values above were not the authoritative section-conformance output. I independently called the existing `section_contrast` implementation on both **absolute scratch paths**, and obtained the exact distinct second-section amplitudes and contrasts shown in the table. The exact command and exit:

```sh
python3 - <<'PY'
import importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location("measure_audio", "/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py")
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
for name in ("edgepass_candidate", "edgefail_candidate"):
    path=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-19")/(name+".wav")
    print(name, module.section_contrast(path, 200))
PY
```
Exit **0**. Results: edge-pass amplitudes `[0.014999984892417233, 0.049998039097271886]`, contrast `10.457243003423983` dB; edge-fail amplitudes `[0.014999984892417233, 0.049998039113914754]`, contrast `10.45724300631526` dB. Both return `valid: True`, `passed: True`; both report gap `0.000396728515625`, with side slopes `0.0009765625` and `0.001007080078125` respectively.

Exact hash command:

```sh
sha256sum /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/artifacts/stem_layer_third.wav /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-19/edgepass_candidate.wav /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-19/edgefail_candidate.wav
```
Exit **0**. Hashes: source `3d2048e48a6a16ef2a669736ad1168c9368223fb3a0702478f874e4d2588d445`; edge-pass `512b38026eb102fac4773bca1b61e7994261b6f6297e0ec544fb4b47b1104496`; edge-fail `48e2167dd405d05dc66aab304fc7b3c4712d2734dca021fdfd92d15a3e8d2a38`.

## Limits

This is decoded numerical evidence for two synthetic scratch files only. No runner mode was wired or run in this executor lane. No claim about hearing, clicks, music, production behavior, engines, security, rights, or external compatibility. No threshold was modified. No setup errors occurred; no shell command failed.
