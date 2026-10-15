local names = { "Core","Settings","Log","LocalModule","LocalNode","SpaDevice","StaticObject",
  "ObjectManager","Object","Node","Device","Client","Link","Metadata","Session","Endpoint",
  "SiLink","SiAdapter","SiNode","Wp","utils","table","string","math","os","io","debug","load",
  "loadstring","dofile","require","require_api","print","type","pairs","ipairs","next","select",
  "pcall","xpcall","error","assert","setmetatable","getmetatable","rawget","rawset","tonumber",
  "tostring","unpack","_G","_ENV","_VERSION","json","spa","GObject","GLib","module","bit32","utf8" }
for _,n in ipairs(names) do
  local ok, v = pcall(function() return _ENV and _ENV[n] or nil end)
  if ok and v ~= nil then print(n .. " = " .. type(v)) end
end
Core.quit()
