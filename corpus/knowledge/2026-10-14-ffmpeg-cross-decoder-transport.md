# r71 — second decoder (ffmpeg/ffprobe) on the transport matrix

The SoX named-axis partition ({file,fifo} named vs {stdin,redir}
anonymous; suffix-dispatched post-table fallback) has NO ffmpeg analogue:

- ffmpeg content-probes on every transport; suffix plays no role — the
  five identical-byte members all reject "Invalid data" on all 4
  transports where SoX split them 5 ways by name alone.
- dec_act/dec_hcom detect+decode on all 4 transports — transport-
  invariant (no named-axis fork).
- Fixture mechanics that mattered: (a) a fifo consumer chain
  (ffprobe + ffmpeg sequentially) needs a fresh fifo+writer PER
  subprocess — the second process opens after the first writer exits;
  (b) an fd redirected to `pipe:` must be opened fresh per subprocess —
  a consumed offset reads EOF downstream.
- `pipe:` over a seekable fd == `pipe:` over a true pipe on this build —
  redirected_fd is not a distinct ffmpeg transport class.
- ffprobe `-show_entries format=probe_score` returns no probe_score key
  on n9.0.1 — recorded null.
