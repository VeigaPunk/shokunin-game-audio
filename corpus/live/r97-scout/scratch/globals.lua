local ks = {}
for k,v in pairs(_G) do ks[#ks+1] = k .. ":" .. type(v) end
table.sort(ks)
print(table.concat(ks, " "))
Core.quit()
