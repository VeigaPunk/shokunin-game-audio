r65-boundary scratch index
gen_probes.py   - fixture generator (35 probes in probes/)
run_matrix.sh   - 8-mode probe runner (file/pipe/redir/pipe-t*/file-tgsrt/info/ffprobe)
runs/matrix.tsv    - first-pass summary (samples column empty: single-space regex miss)
runs/matrix2.tsv   - re-parsed summary with sample counts (authoritative)
runs/probe-shas.txt- sha256 of all fixtures (n_gsrt_enc2 appended post-pass)
runs/logs/<fixture>.<mode>.log - verbatim sox -V4 / --i / ffprobe output
runs/strace-badck-{file,pipe}.txt - lseek evidence for the seekable gate
