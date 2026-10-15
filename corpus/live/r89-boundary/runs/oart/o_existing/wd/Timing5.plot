set output 'Timing5.svg
set terminal svg
set multiplot
set grid
set key tmargin
set title "Clients duration (active -> finished)"
set xlabel "audio cycles"
set ylabel "usec"
plot "o_exist" using 10 title "r87bsp_recl/211" with lines, "o_exist" using 18 title "r87bsp_pr/211" with lines
unset multiplot
unset output
