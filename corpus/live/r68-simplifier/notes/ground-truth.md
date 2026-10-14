# r68-simplifier pre-landing ground truth (measured on this host, /tmp/r68s-nomatch)

SoX_ng 14.8.0.1; all legs `sox -V6 <input> -n stat`.

## No-match member (zeros 512B named .wav / .bin / noext; RIFF@257 / deep-RIFF@4096 variants)

| arm | .wav | .bin | noext |
|---|---|---|---|
| file | RIFF header not found | no handler for file extension `bin' | can't determine type of file `<path>' |
| stdin_pipe (`-`) | can't determine type of  `-' | same | same |
| redirected_fd (`-`) | can't determine type of  `-' | same | same |
| fifo_path (named .wav) | RIFF header not found | no handler `bin' | can't determine type of file `<tmp path>' |

=> Post-table fork = {file, fifo} vs {pipe, redir}: the NAMED/extension axis.
The declared claim's {file,redir}|{pipe,fifo} seekable partition is falsified
for post-table members: redirected_fd is seekable but `-` has no extension;
fifo is non-seekable but named .wav reaches the extension-dispatched reader.

## Mechanism (strace)

- file: openat -> lseek SEEK_CUR ok -> read 4096B -> ext-fallback reader seeks
  (lseek 300 SET / lseek 1 SET) -> reader verdict.
- fifo: openat -> ESPIPE -> read 4096B -> ESPIPE -> reader runs on
  pending_buffer (prefetch is REPLAYED, not consumed) -> identical verdict.
- `-` (pipe or redir): ESPIPE or rewind-ok, then `can't determine type of  `-''
  — the `type` label stays "" for stdin (double space verbatim), so the
  signature is identical on seekable and non-seekable stdin.
- Fallback reader NEVER re-opens the path (one openat total) — so fifo needs
  no writer-linger for native extension readers (writer linger only matters
  for the act ffmpeg bridge's second open).

## Seekable-visible member inside fallback family

`.txw`-named no-match member: file -> `invalid filetype ID ... != LM8953`;
fifo -> `input must be a file, not a pipe` (reader's seekable gate fires on
the fallback path); `-` arms -> can't determine. = 3-group split pinning both
axes in ONE member (name reaches fallback; seekable gates the txw reader).

## txw detected member (r66-boundary g_txw_hcom.bin, 300B; and author txw128 128B)

{file, redir} -> detected txw -> decode (178 / 64); {pipe, fifo} -> refusal
`input must be a file, not a pipe`. Pure seekable fork AFTER a CHECK match —
the reader's `if (!seekable)` gate, not post-table dispatch.

## Harness notes for the landing

- `transport_error` returns post-`':` message; `-` arm errors have no `':` ->
  error = whole FAIL line (`sox FAIL formats: can't determine type of  `-'`)
  — deterministic (literal `-`) but line-shaped, not message-shaped.
- A NO-EXTENSION member would embed the volatile mkdtemp path in fifo's error
  (`can't determine type of file '/tmp/transport-r67-*/x'`) -> nondeterministic
  receipts. Ext-bearing member names are required for byte-stable receipts.
- Prefix-safety: a truncated fifo writer can flip DETECTION when member has a
  CHECK-matching prefix — member must be no-match at every prefix length.
