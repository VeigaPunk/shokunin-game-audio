# R74 adjudicator (Sol) — lavf no-seek demuxer sweep + pw-cat ops-2

Round: 74. Wave: `shokunin-train-20261101-w13`. Work commit `168b165` + folds `6727fed`.

## Declared move

(1) X2: mpv's inverted seekability fork generalized across the lavf
demuxer inventory — the four-condition rule (probe-detected, no
`.read_seek`/`.read_timestamp`, no index rescue, non-pcm codec) tested
per-demuxer on byte-deterministic generated members.
(2) X3: pw-cat ops-2 — hang taxonomy + `-a/--raw` bypass.

## Claim adjudication

- **The four-condition rule is FALSIFIED as stated** — `acm` satisfies
  all four yet does not fork at the output level (rc=0 + identical
  868 B PCM both arms). Critic source-trace (`seek.c:628-636`): the
  real gate is `AVFMT_NOGENSEARCH` — the generic-search *fallback*
  (which consumes the stream) is gated on it, not on GENERIC_INDEX
  (which decides whether the fallback could succeed). Refined rule
  lands in the fixture comment + `fork_kind` lattice.
- **Confirmed forks:** iss + apc `output_rc` (rc2 EPERM vs rc0),
  iss_multi `truncation` (constant-2-packet head loss — 4064 B PCM
  delta, refresh-seek path discards fsi's buffer), acm `wound`
  (seek_failed partition only), adx/aifc/dec_act invariant,
  `mpv --start=2` position fork (2.0 s vs 4.0 s decoded).
- **Ops-2 measured:** writerless-fifo SIGTERM-immune (−9, wchan
  wait_for_partner); `--target 0` TERM-terminable (rc124@4s — a
  distinct hang class, boundary-confirmed under 8× load); `--raw`
  kills the name axis (rc0 on .wav/.bin/.snd identical bytes);
  private zero-sink daemon hangs → −9 (recorded blockage, not pinned
  — wireplumber rescue breaks isolation, boundary §9 incident noted).
- **Wound-shape law corrected:** multi-packet no-seek members lose a
  CONSTANT 2 packets (one per av_seek_frame attempt), not
  whole-stream — critic F2 folded into cell semantics.

## Seat accounting

9/9: author `168b165` (+544/−3, generation machinery + sweep + ops-2,
failures:{}, insertion-only); scout falsified acm pre-landing and
confirmed --raw/--target-0 cells; critic F1/F2 HIGH corrections folded
(fork_kind lattice, stale-claim comment, NOGENSEARCH gate);
boundary 185-cell edge lattice byte-identical ×2 + size-gating
correction (fork is member-size-gated: small iss forks rc2, multi-pkt
truncates); reviewer verified the landed diff pre-commit (F1 folded);
simplifier D1 folded (single declared timeout bound); scribe parser
audit (forge surfaces catalogued — mpv first-match, sox last-match);
baseline zero-drift on freeze `1ba8103` (120/121 mode-keyed, the band
only); verifier **AGREE 12/12** on `168b165` (receipts byte-identical
×3 including author's landed run).

## Verdict

**ADMIT-corr** — lavf no-seek axis measured as a 3-valued wound
partition {output_rc | truncation | wound-only} gated on
NOGENSEARCH; pw-cat ops surface classified {SIGTERM-immune open-block,
TERM-terminable unlinked-stream, zero-sink hang, raw name-axis kill}.
Bounded: mpv 0.41.0, lavf 63.1.101, libpipewire 1.6.8, hand-built
member bytes (manifest sha256s), this host.
