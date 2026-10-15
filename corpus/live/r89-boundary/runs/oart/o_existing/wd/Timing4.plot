set output 'Timing4.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients scheduling latency (scheduled -> active)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_exist" using 9 title "r87bsp_recl/211" with lines, "o_exist" using 17 title "r87bsp_pr/211" with lines
unset multiplot
unset output
