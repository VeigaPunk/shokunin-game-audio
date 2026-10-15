set output 'Timing4.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients scheduling latency (scheduled -> active)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_int" using 9 title "pw-play/258" with lines, "o_int" using 17 title "pw-play/164" with lines
unset multiplot
unset output
