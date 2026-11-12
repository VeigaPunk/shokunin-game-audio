# Audio: a callback return is a lifetime decision

The [2018 Candidate Recommendation](https://www.w3.org/TR/2018/CR-webaudio-20180918/) already distinguishes input processors, tails and generators. The [2021 Recommendation](https://www.w3.org/TR/2021/REC-webaudio-20210617/) preserves that policy: specification maturity changed, not its invention date.

AudioWorklet return values control independent activity. For an input transformer without a tail, false leaves activity dependent on inputs. A generator should return true while producing output. A processor with residual state should retain activity while its tail remains after inputs disappear. Omitting a return behaves like false, not success.

Curator inference: specify termination separately from sample calculation for game effects. Empty inputs do not establish exhausted internal state. This extends render quantum guidance with lifecycle ownership.

Selected sections only; no browser compatibility, playback, performance or assimilation tested.

Original commentary without copied examples. W3C's linked [document terms](https://www.w3.org/copyright/document-license-2023/) restrict derivatives; the 2021 [permissive terms](https://www.w3.org/copyright/software-license-2015/) require retained notices and modification disclosure for redistributed derivatives.

Destination: VeigaPunk/shokunin-game-audio, main, considerthese/2026-11-11-processor-lifetime.md.
