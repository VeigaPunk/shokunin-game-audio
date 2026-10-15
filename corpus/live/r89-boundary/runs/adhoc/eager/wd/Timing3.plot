set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "eager_x" using 1 title "Audio period" with lines, "eager_x" using 8 title "r98s_stall/224" with lines, "eager_x" using 16 title "r98s_stall/102" with lines
unset multiplot
unset output
