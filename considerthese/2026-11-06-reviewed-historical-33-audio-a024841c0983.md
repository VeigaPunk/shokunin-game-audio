# Antialiasing must survive its position in the chain

[Parker and colleagues](https://www.dafx.de/paper-archive/2016/dafxpapers/20-DAFx-16_paper_41-PN.pdf),2016, derive an antiderivative difference quotient through linear interpolation and continuous-time filtering. Nearly equal samples require numerical care. The rectangular-kernel linear limit averages neighbors, changing magnitude and delay. Feedback insertion needs structural compensation; rearrangement can change time-varying behavior.

[Zheleznov and Bilbao](https://dafx.de/paper-archive/2024/papers/DAFx24_paper_33.pdf),2024, investigate cubic interpolation in the IIR extension. Memoryless results improve conditionally, with numerical-integration tradeoffs. Stateful compensation faces tighter stability restrictions and can amplify residual aliases. The stationary metric omits temporal masking; perceptual evaluation remains future work.

A quieter alias spectrum does not establish quiet-signal transparency, preserved attacks or safe recurrent behavior. Isolated success does not authorize feedback insertion.

Selected primary prose read, not equations or sound validated. No open2016 document license established. The2024 article explicitly grants CC BY4.0; software and audio rights remain separate. Original commentary only, no source figures, listings or recordings. No synthesis, implementation or benchmark execution.

Optional exercises omitted; originals retained.
