set output 'Timing4.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients scheduling latency (scheduled -> active)"
set xlabel "audio cycles"
set ylabel "usec"
plot "/dev/null" using 9 title "r98s_drain/194" with lines
unset multiplot
unset output
