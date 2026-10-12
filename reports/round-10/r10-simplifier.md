# Round 10 simplifier — reuse decoded PCM, keep one join gate

## Recommendation

Treat the internal join check as a single measurement on the already-decoded `stem_layer` PCM, not as a second section-specific validator. The boundary is the adjacent decoded pair `samples[95999]`, `samples[96000]` (2 s at 48 kHz); its absolute difference is the join gap. Add that observed value to the normal `stem_layer` measurement and append one clearly named failure only when it exceeds the existing `.03` full-scale bound. Do not duplicate format/level/section gates or create another receipt. Keep the existing 120 Hz section contrast as-is; it answers a separate question.

There is already duplicated decoding on this path: `measure()` decodes the WAV with SoX, then `section_contrast()` decodes it again. The smallest clean reuse is a small decoded-sample loader/cache for the invocation, passed to both analyses (or an equivalent narrow parameter); do not retain PCM in the JSON receipt. Parent integration should preserve existing receipts and controls, and avoid counting a single join failure twice.

## Candidate evidence

I inspected the assigned scratch candidates. `join_candidate.wav` is an original 4 s, 48 kHz mono PCM candidate, with join gap `0.040191650390625`, outer endpoint delta `0.000946044921875`, outer slope delta `0.000762939453125`, peak `0.05999755859375`, and RMS `0.03059310849989651`. Its half-section 120 Hz amplitudes are approximately `0.01199958745` and `0.05999774520`, contrast `13.9793722838 dB`, so the existing contrast minimum is met. This is a viable isolated >.03 join-gap control by the declared controls, subject to full integrated replay.

The existing clean `stem_layer.wav` has corresponding join gap `0.00018310546875`; 120 Hz contrast is `13.97937228298 dB`. `join_alt_candidate.wav` is not a viable isolated control: it is 8 s, with outer endpoint delta `0.539337158203125`, slope delta `0.6488037109375`, and peak `0.99896240234375`, so it violates multiple existing bounds. Do not use it to evidence sole-failure isolation.

These are sample-gap proxy measurements only. They do not establish slope continuity at the internal join, audibility, click-free transitions, engine behavior, or production quality.

## Commands / exits

- `git status --short && git rev-parse --short HEAD && git log -1 --oneline` — exit **0**; observed HEAD `f32ab7f` and pre-existing modifications/untracked round-10 scratch. No source or shared-file edits made.
- `python3 -c 'import wave,numpy as np,sys; from pathlib import Path; ps=[Path(".shokunin/audio/corpus/artifacts/stem_layer.wav"),Path(".shokunin/audio/corpus/live/round-10/join_candidate.wav"),Path(".shokunin/audio/corpus/live/round-10/join_alt_candidate.wav")];
for p in ps:
 w=wave.open(str(p),"rb"); x=np.frombuffer(w.readframes(w.getnframes()),"<i2").astype(np.float64)/32768; print(p, "rate/ch/frames",w.getframerate(),w.getnchannels(),len(x), "join",abs(x[96000]-x[95999]) if len(x)>96000 else None, "outer",abs(x[0]-x[-1]), "slope",abs((x[-1]-x[-2])-(x[1]-x[0])), "peak",np.max(np.abs(x)),"rms",np.sqrt(np.mean(x*x)));
 if len(x)==192000:
  a=[2*abs(np.fft.rfft(h)[120*len(h)//48000])/len(h) for h in np.split(x,2)]; print("120hz amplitudes",a,"contrast_db",20*np.log10(a[1]/a[0]))'` — exit **0**.
- Python inspection of WAV headers and hashes (REPL, not a shell command): `join_candidate.wav` SHA-256 `c4818b9a2fdf4c6479a945f2f2739c6c0caf1559b1b31d62c4c630af84396e2d`; alternate SHA-256 `a0380aae02b1f202af45718b7e548ea3ca4abe3557caa2c751c6cc0c70eb945b`.

No project test/replay was run by this role; no shell command failed. This is an integration recommendation, not validation of a landed gate.
