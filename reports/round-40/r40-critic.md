# R40 critic — independent endpoint-isolation falsification

**Result: inconclusive / target claim not independently demonstrated.** I generated two distinct PCM16 scratch candidates and decoded them independently with SoX. The decoded endpoint integers bracket `.03` exactly as declared, but neither meets all ordinary checks, so these do **not** establish the requested 983-pass / 984-sole-endpoint-fail pair. No assertion of exact equality at `.03` follows from this bracket. I made no source, LOG, SCORECARD, canonical artifact, or other report edits; scratch files are under `/tmp/r40-critic/` only.

## Scratch and decoded values

Both files are mono 48,000-Hz PCM16 WAV, 96,000 frames (2.000 s). They are distinct, with SHA-256:

- `endpoint-983.wav`: `803581ec4d9830d312cc8e6bda92d74d84700d98095bad6c9d91bbeb62cb970b`
- `endpoint-984.wav`: `4703d3ca7c39a940b333365c8329e0385d36acb70d70f76037ecf3e60f1555e0`

Decoded PCM values are normalized to full scale; first sample is 0.0 in both. Last samples are respectively `-983/32768 = -0.029998779296875` and `-984/32768 = -0.030029296875`; endpoint deltas exactly those values. This supports the strict comparison `delta > .03` distinguishing the cases, not an equality claim.

The independent scratch synthesis used a low-frequency sine with a direct final-sample adjustment and aligned preceding sample to make the side-slope mismatch zero. The R40 comparator’s slope measurement is a *difference of first and last adjacent-sample increments*, not a slope bound at each side. The candidates’ endpoint values are thus isolated algebraically, but the unwanted terminal adjustment makes the spectrum fail the ambience 5–200 Hz centroid band: **983 centroid 354.7337 Hz; 984 centroid 355.0793 Hz** (outside band). Both peak values are 0.8999939 FS, duration/format pass; reported slope mismatch is 0 for both. The centroid is a numeric failed fit, not a setup error. Thus 984 also has its expected endpoint failure, but it is not the *sole* failure; 983 is not a passing control.

Gate measurements from the checker: 983 endpoint `0.029998779296875`, slope `0.0`, peak `0.899993896484375`, RMS `-3.9254499524 dBFS`, centroid `354.7337067 Hz`, failures `['spectrum: centroid outside fixture band']`; 984 endpoint `0.030029296875`, slope `0.0`, peak `0.899993896484375`, RMS `-3.9254499520 dBFS`, centroid `355.0792705 Hz`, failures `['spectrum: centroid outside fixture band', 'loop seam: endpoint jump > .03 full scale']`.

## Commands / exits

Exact decoder invocation used for each file (substitute the respective filename); both invocations exited **0**:

```sh
python -c 'import subprocess,numpy as np,sys; x=np.frombuffer(subprocess.run(["sox",sys.argv[1],"-t","f32","-e","floating-point","-"],capture_output=True,check=True).stdout,dtype="<f4").astype(float); c=np.abs(np.fft.rfft(x)); f=np.fft.rfftfreq(len(x),1/48000); print(dict(first=x[0],last=x[-1],endpoint=abs(x[0]-x[-1]),slope=abs((x[-1]-x[-2])-(x[1]-x[0])),peak=max(abs(x)),rms=np.sqrt(np.mean(x*x)),centroid=f@c/c.sum()))' /tmp/r40-critic/endpoint-983.wav
```

The same command with `endpoint-984.wav` also exited **0**. I then invoked the existing `measure_audio.measure()` against each scratch file with `(2.0, 5, 200, True)` and the checker ROOT redirected to `/tmp/r40-critic`; the Python command exited **0** (it prints a result rather than failing on measured failures). It produced the gate numbers above. An earlier measurement attempt without redirecting ROOT exited **1** with `ValueError: ... '/tmp/r40-critic/endpoint-983.wav' is not in the subpath of .../corpus`; that was a harness path/setup error, not a failed numeric fit, and was corrected by setting the temporary checker root to scratch.

## Falsification assessment

The current `measure()` computes endpoint delta from decoded first/last samples, and tests `> .03`; at integer PCM16 increments the requested values genuinely straddle the comparator. Its independent outer slope-mismatch test is also active and could cause a second failure in a naive splice. In this attempt aligning terminal and initial increments suppressed that slope failure, but altered the global spectrum enough to invalidate both fits. Therefore this scratch attempt does not falsify the comparator; it does falsify any claim that merely synthesizing the stated endpoint counts is sufficient evidence of a clean isolated gate. Do not describe this pair as meeting the R40 gate.

Scope is numeric fixture calibration only. No audition or claims about sound quality, audible clicks, production, rights, engine behavior, publishing, or promotion.
