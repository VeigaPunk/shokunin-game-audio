set output 'Timing3.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients end date (scheduled -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_exist" using 1 title "Audio period" with lines, "o_exist" using 8 title "r87bsp_recl/211" with lines, "o_exist" using 16 title "r87bsp_pr/211" with lines
unset multiplot
unset output
