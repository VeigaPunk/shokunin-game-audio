set output 'Timing4.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients scheduling latency (scheduled -> active)"
set xlabel "audio cycles"
set ylabel "usec"
plot "eager_x" using 9 title "r98s_stall/224" with lines, "eager_x" using 17 title "r98s_stall/102" with lines
unset multiplot
unset output
