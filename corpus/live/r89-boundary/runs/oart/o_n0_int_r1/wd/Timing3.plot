set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_int" using 1 title "Audio period" with lines, "o_int" using 8 title "r98s_drain/194" with lines
unset multiplot
unset output
