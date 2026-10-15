set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "profiler.log" using 1 title "Audio period" with lines, "profiler.log" using 8 title "pw-play/146" with lines, "profiler.log" using 16 title "pw-play/202" with lines
unset multiplot
unset output
