# Separate string tuning from decay

[Karplus and Strong1983](https://www.moforte.com/wp-content/uploads/2020/05/Karplus-Strong-CMJ-1983.pdf) repeatedly average a noise-initialized wavetable. Higher harmonics decay faster; short buffers constrain tuning and persistence. Decay stretching already affects pitch.

[Jaffe and Smith1983](https://musicweb.ucsd.edu/~trsmyth/papers/KSExtensions.pdf) add fractional allpass tuning without magnitude attenuation. Weighted averaging lengthens decay but changes phase delay, requiring retuning. Uniform loop gain cannot safely lengthen decay beyond unity because DC grows. Excitation filtering changes articulation separately from amplitude.

[Karjalainen1999](https://www.dafx.de/paper-archive/1999/karjalainen2.pdf) discusses commuted body/excitation responses and tension-dependent delay. Nonlinear operations cannot generally be reordered. Changing allpass parameters can cause recursive transients; FIR interpolation avoids that tail but can still produce discontinuities. Discrete-time passivity is not automatic.

Keep pitch, attenuation, articulation and change-time behavior specified. More controls do not imply independence. Selected prose read, not equations, listening or synthesis validated. Both1983 scans carry MIT/JSTOR restrictions; no open grant established for1999. Original commentary only, no scans, code or figures. No training.

Optional exercises omitted; originals retained.
