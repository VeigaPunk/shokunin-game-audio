local t = {}
for _, n in ipairs({'Core','Settings'}) do t[#t+1] = n end
print('ipairs ok ' .. #t)
Core.quit()
