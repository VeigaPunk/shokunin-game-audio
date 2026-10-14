# SoX_ng post-table fallback — full CHECK-table miss resolves by NAME (extension dispatch), never by seekability; txw member pins the genuine seekable-gated pipe refusal (round 68)

- Source: round-68 seat evidence (`reports/round-68/r68-{scout,critic,boundary,scribe}.md`; independent matrices `corpus/live/r68-{scout,critic,boundary,scribe}/…`); upstream sox_ng-14.8.0.1 `src/formats.c` (lane-verified copy `corpus/live/r64-reviewer/r64rev-formats.c`, sha256 `82c3058e…`), `tx16w.c`, `smp.c` — citations corroborative; load-bearing claims empirical.
- Verified at: 2026-10-14, host `/usr/bin/sox` SoX_ng v14.8.0.1 (USING_FFMPEG), ffmpeg/ffprobe n9.0.1.
- Recheck when: SoX version/build changes, when the CHECK table changes, when `AUTO_DETECT_SIZE` changes, when `lsx_find_file_extension`/`sox_find_format` or `ft->io_type` handling changes, or when member names/extensions change.

## The measured law (falsifies the round's declared wording)

After `auto_detect_format` returns NULL, `open_read` (formats.c ~910-933) resolves a handler purely by **name**:

    io_type == lsx_io_pipe   → filetype = "sox"     (|cmd pseudo-paths only)
    no extension             → "can't determine type of <io-str> `X'"
    unknown extension        → "no handler for file extension `X'"
    known extension          → that handler runs on the buffered prefetch

`ft->seekable` is never read on this path. On the tracked 4-arm transport set the verdict therefore partitions `{file, fifo_path}` (named → extension dispatch) vs `{stdin_pipe, redirected_fd}` (both spell `-`, extensionless → `can't determine type of  '-'`) — the **named axis**, the exact transpose of the declared seekable partition. The seekable rewind demonstrably happens (`lseek(0,-300,SEEK_CUR)=0` on `sox - < f`) and buys nothing — there is no second classification pass to feed.

## Prefetch bytes are replayed, not consumed

`lsx_readbuf_rewind` (formats_i.c ~178-218): seekable → `rewind()`; non-seekable → bytes stashed in `ft->pending_buffer` and replayed to whichever reader the dispatch selects. Proof classes: a `.wav`-named fifo gets the identical `RIFF header not found` verdict as the file (strace: ESPIPE, single read, no re-read); a `.f32`-named fifo decodes all samples (r68-critic, 150/150). "≤257 bytes consumed on pipes" is wrong as mechanism; consumption only matters to the ffmpeg bridge's *external* re-open (r67), which bypasses the buffer.

## Post-table verdict classes (5, measured)

extension-handler verdict | `can't determine type of <io-str> 'X'` | `no handler for file extension 'X'` | assume-`sox` (`|cmd` only) | `--magic` detected-MIME with no handler (off-ledger flag). None is selected by seekability.

## The genuine seekability fork lives on matched members

`txw` (`LM8953`@0-5, len≥6) and `smp` (`SOUND SAMPLE DATA`@0-16, len≥17) readers open with `if (!ft->seekable) → "input must be a file, not a pipe"` (tx16w.c:88-94, smp.c:226-233) — before any content read. Tracked member `txw_piperefuse` shape: detected `txw` on all four transports; `{file, redirected_fd}` decode N samples exit 0 vs `{stdin_pipe, fifo_path}` refusal exit 2 — the seekable partition, inside the reader. txw preferred over smp: 6-B predicate + positive decode (300-B body → 178 samples: (len−32)÷3×2 for the 12-bit packing).

## Edges

- `.snd`-named members arm an ext-gated CHECK row (formats.c:247-248) → *detection itself* forks on the name (first counterexample to r67's detection-invariance). Never name the fallback member `.snd`.
- Extension-less member names embed the volatile path in the `error` field → non-deterministic receipts; keep an extension or scrub `error`.
- Starved fifo delivery can flip a *detected* member's detection at its len gate (protocol artifact); all-zero bodies are prefix-safe.
