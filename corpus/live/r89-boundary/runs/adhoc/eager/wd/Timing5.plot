set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "eager_x" using 10 title "r98s_stall/224" with lines, "eager_x" using 18 title "r98s_stall/102" with lines
unset multiplot
unset output
