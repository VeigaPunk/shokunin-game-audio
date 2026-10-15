set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "profiler.log" using 10 title "pw-play/146" with lines, "profiler.log" using 18 title "pw-play/202" with lines
unset multiplot
unset output
