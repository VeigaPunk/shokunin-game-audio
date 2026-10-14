r66-boundary runs index
=======================

matrix.tsv    1,184 rows = header + 91 fixtures x 13 modes.
              modes: file | pipe (cat f | sox -) | redir (sox - < f)
                     pipe-t{wve,gsrt,hcom,act,wav}  (forced -t on pipe)
                     file-t{wve,gsrt,hcom}         (forced -t on file)
                     info (sox --i) | ffprobe
              columns: fixture  mode  detected  exit  samples  info_or_fail
sweep.tsv     768 rows = probes/sweep/sw_wve_p{00,07,14}_v{00..ff}.bin,
              detect-only (file mode). 3 detections: p00@0x41, p07@0x6e,
              p14@0x2a — the exact magic bytes at those positions.
logs/         verbatim `sox -V4`/`--i`/ffprobe output per fixture x mode
              (logs/<fixture>.<mode>.log).
probe-shas.txt    sha256 of the 91 main fixtures.
sweep-shas.txt    sha256 of the 768 sweep fixtures.
strace-wve-{pipe,file}.txt — lseek evidence for wve's seekable-gated
              declared-length WARN (pipe: lseek(0,0,SEEK_CUR)=-1 ESPIPE).

Generators:   ../gen_probes.py   (a..z families; byte-deterministic —
              regen into a clean dir diffed identical 2026-10-14)
              ../gen_probes_p.py (p_* voc/smp pins + t_* tracked copies)
Runners:      ../run_matrix.sh   (original 79-fixture battery)
              ../run_matrix_p.sh (p_*/t_* append, same 13 modes)
              ../run_sweep.sh    (regenerates sweep.tsv; reproduced
              the pre-existing sweep.tsv byte-identical)
