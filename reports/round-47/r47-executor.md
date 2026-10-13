# Round 47 executor — UI upper-centroid boundary pair

## Result

Generated two original .12 s (5760-frame), 48 kHz, mono PCM16 scratch controls under `corpus/live/round-47/executor/`. The project helper decodes with SoX to f32 and computes the whole-wave magnitude-FFT weighted centroid. One control measures narrowly below 4000 Hz and passes all checks; the other measures above 4000 Hz and has only the expected spectrum-band failure.

| Control | SHA-256 | Frames / format | Project-decoded centroid | Peak FS | RMS dBFS | Failures |
|---|---|---|---:|---:|---:|---|
| `upper-below.wav` | `b04d00164fc57a97a0cdd591a589a44792d0084ba66cdc2118989183ae22fc17` | 5760, 48k mono PCM16 | 3999.922795974407 Hz | 0.279754638671875 | -18.327854015660773 | none |
| `upper-above.wav` | `8f6dd0411d240e46ea619c32e3c344b8c03491d860ebc6ab32b248cbd51e4383` | 5760, 48k mono PCM16 | 4000.427101452783 Hz | 0.2789306640625 | -18.32785200392649 | `spectrum: centroid outside fixture band` only |

Both measured durations were exactly 0.12 s; both are 48 kHz mono PCM16, peak < .95, and RMS > .001. Integrated LUFS was null (not a gate). The lower control has no failures; the upper control's other format/duration/level checks pass. Hashes are distinct. These are numeric fixture calibration controls only, not claims about spectral quality or sound.

## Recipe and numeric fitting

For each final WAV: `n=5760`, `t=np.arange(n)/48000`, `x=.28*np.sin(2*pi*f*t)*np.hanning(n)`, quantize as `np.rint(np.clip(x,-1,1)*32767).astype('<i2')`, and write one channel, 2-byte samples at 48000 Hz. Final nominal frequencies were 3983 Hz (below) and 3984 Hz (above). Nominal tone frequency is not the decoded centroid; the reported values are measured by the project helper after SoX decoding.

Broad initial candidate nominal 3950/4050 measured 3967.0910519284344/4066.3960394571586 Hz and bracketed the limit, but was not narrow. Tuning nominal 3980/4020 measured 3996.0324472283264/4035.6751535337717 Hz; this was a valid but broad numeric bracket. At 3983/3984, the respective decoded results were 3999.9227959744053 and 4000.427101452797 Hz, yielding the final narrow bracket. No failed numeric fit remained in the final pair. This is a gate-level bracket, not causal single-variable spectral isolation: the sample sequences, nominal frequencies, and FFT distributions differ. No exact-4000 equality inference.

## Exact commands and exits

Generator file is `corpus/live/round-47/executor/generate.py`. Final generation invocations (both exit **0**):

```sh
python3 /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/generate.py /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/upper-below.wav 3983
python3 /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/generate.py /home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/upper-above.wav 3984
```

The second absolute path above should be the same project path as the first; correction: `/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/upper-above.wav`.

Final project-helper measurement command (exit **0**):

```sh
python3 -c 'import importlib.util,json; from pathlib import Path; p=Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/fixtures/measure_audio.py"); s=importlib.util.spec_from_file_location("measure_audio",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); print(json.dumps({k:m.measure(k,(.12,250,4000,False),Path("/home/vgpnk/Projects/prymeagnt/audio/.shokunin/audio/corpus/live/round-47/executor/upper-"+k+".wav")) for k in ("below","above")},indent=2))'
```

A prior helper call using a relative WAV path raised `ValueError` at `path.relative_to(ROOT)` because the helper requires a path beneath its absolute corpus root. That was a setup/path error, not a decode or numeric-fit failure; rerunning with absolute paths succeeded. No transcription errors in this report. No audition or quality, perception, production, rights, engine, publishing, or promotion inference was made.
