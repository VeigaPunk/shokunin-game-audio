cells read: 229 -> /home/vgpnk/Projects/shokunin/audio-shokunin/corpus/live/r76-boundary/runs/verdicts-r76/verdicts.json

## sever ladder
| target | phase | class | rc | wall@term1 | wall | bytes@term1 | size | captured_s | header |
|---|---|---|---|---|---|---|---|---|---|
| ar-hw | mid | term1-fatal(rc=-15) | -15 | 1.505 | 1.525 | 264044 | 264044 | 1.375 | stale(57600036/264044) |
| ar-hw | early | term1-fatal(rc=-15) | -15 | 0.061 | 0.081 | 44 | 44 | None | stale(57600036/44) |
| ar-null | mid | term1-fatal(rc=0) | 0 | 1.505 | 1.525 | 288000044 | 288000044 | 3000.0 | finalised |
| ar-null | early | term1-fatal(rc=-15) | -15 | 0.061 | 0.081 | 200688044 | 200760044 | 2091.25 | finalised |
| ff-alsa-hw | mid | term1-fatal(rc=255) | 255 | 1.505 | 1.566 | 262144 | 262144 | 1.365 | lavf-placeholder(0xFFFFFFFF) |
| ff-alsa-hw | early | term1-fatal(rc=255) | 255 | 0.061 | 0.563 | 0 | 0 | None | no-file |
| ff-alsa-null | mid | term1-fatal(rc=255) | 255 | 1.505 | 1.525 | 3145728 | 3145728 | 16.384 | lavf-placeholder(0xFFFFFFFF) |
| ff-alsa-null | early | term1-fatal(rc=255) | 255 | 0.061 | 0.141 | 0 | 0 | None | no-file |
| ff-pulse | mid | term1-fatal(rc=255) | 255 | 1.505 | 1.645 | 262144 | 262144 | 1.365 | lavf-placeholder(0xFFFFFFFF) |
| ff-pulse | early | term1-immune | 123 | 0.061 | 0.582 | 0 | 0 | None | no-file |
| pa | mid | term1-fatal(rc=0) | 0 | 1.505 | 1.525 | 44 | 44 | None | finalised |
| pa | early | term1-fatal(rc=0) | 0 | 0.06 | 0.081 | 44 | 44 | None | finalised |
| pw | mid | term1-fatal(rc=1) | 1 | 1.506 | 1.526 | 290860 | 290860 | 1.515 | finalised |
| pw | early | term1-fatal(rc=1) | 1 | 0.06 | 0.081 | 4140 | 4140 | 0.021 | finalised |

## capture ratio (captured_s / wall_s)
| cell | wall | captured_s | ratio | rc | header | probe_dur |
|---|---|---|---|---|---|---|
| bound-ar-hw00-d1 | 1.043 | 1.0 | 0.959 | 0 | finalised | 1.0 |
| bound-ar-null-d1 | 0.021 | 1.0 | 47.619 | 0 | finalised | 1.0 |
| bound-ar-null-s48000 | 0.021 | 1.0 | 47.619 | 0 | finalised | 1.0 |
| bound-ff-alsa-hw00-t1 | 1.084 | 1.003 | 0.925 | 0 | finalised | 1.002375 |
| bound-ff-alsa-null-t1 | 1.023 | 13.533 | 13.229 | 0 | finalised | 13.532729 |
| bound-ff-alsa-null-t2 | 2.026 | 23.675 | 11.685 | 0 | finalised | 23.674646 |
| bound-ff-pulse-src-fs100k | 0.702 | 0.55 | 0.784 | 0 | finalised | 0.55 |
| bound-ff-pulse-src-t1 | 1.164 | 1.005 | 0.864 | 0 | finalised | 1.005229 |
| bound-pa-term1 | 2.027 | 0.341 | 0.168 | 0 | finalised | 0.341333 |
| bound-pw-src-n24000 | 0.562 | 0.5 | 0.89 | 1 | finalised | 0.5 |
| bound-pw-src-n48000 | 1.084 | 1.0 | 0.923 | 1 | finalised | 1.0 |
| gate-ar-hw00 | 1.044 | 1.0 | 0.958 | 0 | finalised | 1.0 |
| gate-ar-hw00-dead-rt | 1.044 | 1.0 | 0.958 | 0 | finalised | 1.0 |
| gate-ar-null | 0.02 | 1.0 | 50.0 | 0 | finalised | 1.0 |
| gate-ar-null-stereo | 0.02 | 1.0 | 50.0 | 0 | finalised | 1.0 |
| gate-ff-alsa-hw00 | 1.084 | 1.001 | 0.924 | 0 | finalised | 1.001271 |
| gate-ff-alsa-hw00-dead-rt | 1.085 | 1.003 | 0.924 | 0 | finalised | 1.0025 |
| gate-ff-alsa-null | 1.044 | 12.027 | 11.52 | 0 | finalised | 12.027063 |
| gate-ff-pulse-mon | 1.185 | 1.044 | 0.881 | 0 | finalised | 1.043708 |
| gate-ff-pulse-src | 1.144 | 1.008 | 0.881 | 0 | finalised | 1.008021 |
| gate-pa-absent-source | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pa-dead-runtime | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pa-default-mon | 4.014 | 2.048 | 0.51 | -9 | libsndfile-placeholder(8/0) | 2.048 |
| gate-pa-default-src | 4.014 | 2.048 | 0.51 | -9 | libsndfile-placeholder(8/0) | 2.048 |
| gate-pa-named-src | 4.014 | 2.048 | 0.51 | -9 | libsndfile-placeholder(8/0) | 2.048 |
| gate-pa-pulse-server-dead | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-no-target | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-absent | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-mon | 0.021 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-mon-bare | 0.021 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-mon-pulse-name | 0.021 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-sink-wrongdir | 0.02 | 0.0 | 0.0 | 1 | finalised | nan |
| gate-pw-target-src | 1.084 | 1.0 | 0.923 | 1 | finalised | 1.0 |
| gate-pw-target0 | 4.013 | 0.0 | 0.0 | -9 | libsndfile-placeholder(8/0) | nan |

## bound honour
| cell | requested | wall | captured_s | rc | size | header | probe_dur | killed_by |
|---|---|---|---|---|---|---|---|---|
| bound-ar-hw00-d1 | seconds=1 | 1.043 | 1.0 | 0 | 192044 | finalised | 1.0 | None |
| bound-ar-null-d1 | seconds=1 | 0.021 | 1.0 | 0 | 96044 | finalised | 1.0 | None |
| bound-ar-null-s48000 | samples=48000 | 0.021 | 1.0 | 0 | 96044 | finalised | 1.0 | None |
| bound-ff-alsa-hw00-t1 | seconds=1 | 1.084 | 1.003 | 0 | 192534 | finalised | 1.002375 | None |
| bound-ff-alsa-null-t1 | seconds=1 | 1.023 | 13.533 | 0 | 2598362 | finalised | 13.532729 | None |
| bound-ff-alsa-null-t2 | seconds=2 | 2.026 | 23.675 | 0 | 4545610 | finalised | 23.674646 | None |
| bound-ff-pulse-src-fs100k | bytes=100000 | 0.702 | 0.55 | 0 | 105678 | finalised | 0.55 | None |
| bound-ff-pulse-src-t1 | seconds=1 | 1.164 | 1.005 | 0 | 193082 | finalised | 1.005229 | None |
| bound-pa-term1 | wrapper-TERM=2.0 | 2.027 | 0.341 | 0 | 65580 | finalised | 0.341333 | term1 |
| bound-pw-src-n24000 | samples=24000 | 0.562 | 0.5 | 1 | 96044 | finalised | 0.5 | None |
| bound-pw-src-n48000 | samples=48000 | 1.084 | 1.0 | 1 | 192044 | finalised | 1.0 | None |

## name axis
| cell | rc | size | header | codec | dur | tail |
|---|---|---|---|---|---|---|
| name-ar-n_bin | 0 | 96044 | finalised | pcm_s16le | 1.0 | ar_n.bin' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ar-n_flac | 0 | 96044 | finalised | pcm_s16le | 1.0 | r_n.flac' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ar-n_foo | 0 | 96044 | finalised | pcm_s16le | 1.0 | ar_n.foo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ar-n_raw | 0 | 96044 | finalised | pcm_s16le | 1.0 | ar_n.raw' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ar-n_wav | 0 | 96044 | finalised | pcm_s16le | 1.0 | ar_n.wav' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ar-t-raw | 0 | 96000 | no-header | None | None | traw.wav' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| name-ff-explicit-f | 0 | 199390 | finalised | pcm_s16le | 1.038083 |  |
| name-ff-n_bin | 234 | None | no-file | None | None | ut/nm_ff_n.bin.
Error opening output files: Invalid argument |
| name-ff-n_flac | 0 | 8622 | no-header | flac | 1.046563 |  |
| name-ff-n_foo | 234 | None | no-file | None | None | ut/nm_ff_n.foo.
Error opening output files: Invalid argument |
| name-ff-n_raw | 234 | None | no-file | None | None | ut/nm_ff_n.raw.
Error opening output files: Invalid argument |
| name-ff-n_wav | 0 | 193014 | finalised | pcm_s16le | 1.004875 |  |
| name-pa-n_bin | -9 | 196652 | libsndfile-placeholder(8/0) | pcm_s16le | 1.024 |  |
| name-pa-n_flac | -9 | 262188 | libsndfile-placeholder(8/0) | pcm_s16le | 1.365333 |  |
| name-pa-n_foo | -9 | 196652 | libsndfile-placeholder(8/0) | pcm_s16le | 1.024 |  |
| name-pa-n_raw | -9 | 262188 | libsndfile-placeholder(8/0) | pcm_s16le | 1.365333 |  |
| name-pa-n_wav | -9 | 196652 | libsndfile-placeholder(8/0) | pcm_s16le | 1.024 |  |
| name-pw-container-override | 1 | 96044 | finalised | pcm_s16le | 0.5 | io-shokunin/corpus/live/r76-boundary/out/nm_pw_container.raw |
| name-pw-n_bin | 1 | 96044 | finalised | pcm_s16le | 0.5 | unin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.bin |
| name-pw-n_flac | 1 | 172 | no-header | flac | 0.5 | nin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.flac |
| name-pw-n_foo | 1 | 96044 | finalised | pcm_s16le | 0.5 | unin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.foo |
| name-pw-n_raw | 1 | 96000 | no-header | None | None | unin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.raw |
| name-pw-n_wav | 1 | 96044 | finalised | pcm_s16le | 0.5 | unin/audio-shokunin/corpus/live/r76-boundary/out/nm_pw_n.wav |
| name-pw-raw-flag | 1 | 96000 | no-header | None | None |  |

## fifo / sink edges
| cell | rc | wall | killed_by | non_regular | size | tail |
|---|---|---|---|---|---|---|
| fifo-drain-ar | 0 | 0.02 | None | True | None | y/rt/drain-ar.fifo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| fifo-drain-ff-pulse | 234 | 0.121 | None | True | None | y/rt/drain-ff-pulse.fifo.
Error opening output files: Invalid argument |
| fifo-drain-pa | 1 | 0.02 | None | True | None | Failed to open audio file. |
| fifo-drain-pw | 1 | 0.02 | None | True | None | at does not support pipe write.
error: open failed: Input/output error |
| fifo-early-ar | -13 | 0.021 | None | True | None | y/rt/early-ar.fifo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| fifo-early-ff-pulse | 234 | 0.101 | None | True | None | y/rt/early-ff-pulse.fifo.
Error opening output files: Invalid argument |
| fifo-early-pa | 1 | 0.02 | None | True | None | Failed to open audio file. |
| fifo-early-pw | 1 | 0.02 | None | True | None | at does not support pipe write.
error: open failed: Input/output error |
| fifo-earlyexit-ar | -9 | 5.016 | harness | True | None | dary/rt/ep-ar.fifo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| fifo-earlyexit-ff-pulse | 234 | 0.101 | None | True | None | dary/rt/ep-ff-pulse.fifo.
Error opening output files: Invalid argument |
| fifo-earlyexit-pa | -9 | 5.016 | harness | True | None |  |
| fifo-earlyexit-pw | -9 | 5.016 | harness | True | None | rojects/shokunin/audio-shokunin/corpus/live/r76-boundary/rt/ep-pw.fifo |
| fifo-none-ar | -9 | 4.013 | harness | True | None | ry/rt/none-ar.fifo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| fifo-none-ff-pulse | 234 | 0.141 | None | True | None | ry/rt/none-ff-pulse.fifo.
Error opening output files: Invalid argument |
| fifo-none-pa | -9 | 4.013 | harness | True | None |  |
| fifo-none-pw | -9 | 4.013 | harness | True | None | jects/shokunin/audio-shokunin/corpus/live/r76-boundary/rt/none-pw.fifo |
| fifo-noreader-ar | -9 | 4.013 | harness | True | None | dary/rt/nr-ar.fifo' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| fifo-noreader-ff-pulse | 234 | 0.081 | None | True | None | dary/rt/nr-ff-pulse.fifo.
Error opening output files: Invalid argument |
| fifo-noreader-pa | -9 | 4.013 | harness | True | None |  |
| fifo-noreader-pw | -9 | 4.013 | harness | True | None | rojects/shokunin/audio-shokunin/corpus/live/r76-boundary/rt/nr-pw.fifo |
| sink-devfull-ar | 1 | 0.02 | None | None | None | ttle Endian, Rate 48000 Hz, Mono
arecord: begin_wave:2773: write error |
| sink-devfull-ff-pulse | 234 | 0.1 | None | None | None | ng output file /dev/full.
Error opening output files: Invalid argument |
| sink-devfull-pa | 1 | 0.02 | None | None | None | Failed to open audio file. |
| sink-devfull-pw | 1 | 0.02 | None | None | None | rror : No space left on device.
error: open failed: Input/output error |
| sink-devnull-ar | 0 | 0.02 | None | None | None | ng WAVE '/dev/null' : Signed 16 bit Little Endian, Rate 48000 Hz, Mono |
| sink-devnull-ff-pulse | 234 | 0.121 | None | None | None | ng output file /dev/null.
Error opening output files: Invalid argument |
| sink-devnull-pa | -9 | 4.013 | harness | None | None |  |
| sink-devnull-pw | -9 | 4.013 | harness | None | None | /dev/null |
| sink-dir-as-target | 1 | 0.02 | None | None | None | s/shokunin/audio-shokunin/corpus/live/r76-boundary/out: Is a directory |
| sink-unwritable | 1 | 0.02 | None | None | None | an, Rate 48000 Hz, Mono
/proc/self/nope.wav: No such file or directory |

## load replay
| cell | class | rc | wall | size | header |
|---|---|---|---|---|---|
| load8-ar-null-2 | term1-fatal(rc=0) | 0 | 1.525 | 288000044 | finalised |
| load8-ar-null-7 | term1-fatal(rc=0) | 0 | 1.525 | 288000044 | finalised |
| load8-ff-alsa-null-4 | term1-fatal(rc=255) | 255 | 1.525 | 3203450 | finalised |
| load8-ff-pulse-3 | term1-fatal(rc=255) | 255 | 1.625 | 262144 | lavf-placeholder(0xFFFFFFFF) |
| load8-pa-1 | term1-fatal(rc=0) | 0 | 1.525 | 44 | finalised |
| load8-pa-6 | term1-fatal(rc=0) | 0 | 1.525 | 44 | finalised |
| load8-pw-0 | term1-fatal(rc=1) | 1 | 1.525 | 278572 | finalised |
| load8-pw-5 | term1-fatal(rc=1) | 1 | 1.525 | 286764 | finalised |
| loadcpu16-ar-null-2 | term1-fatal(rc=0) | 0 | 1.526 | 288000044 | finalised |
| loadcpu16-ff-pulse-3 | term1-fatal(rc=255) | 255 | 1.645 | 262144 | lavf-placeholder(0xFFFFFFFF) |
| loadcpu16-pa-1 | term1-fatal(rc=0) | 0 | 1.527 | 44 | finalised |
| loadcpu16-pw-0 | term1-fatal(rc=1) | 1 | 1.525 | 286764 | finalised |
