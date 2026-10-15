set output 'Timing4.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients scheduling latency (scheduled -> active)"
set xlabel "audio cycles"
set ylabel "usec"
plot "profiler.log" using 9 title "pw-play/146" with lines, "profiler.log" using 17 title "pw-play/202" with lines
unset multiplot
unset output
