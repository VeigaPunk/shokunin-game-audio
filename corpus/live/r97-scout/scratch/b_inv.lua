local names = {"Core","Settings","Log","LocalModule","LocalNode","SpaDevice","StaticObject","ObjectManager","Object","Node","Device","Client","Link","Metadata","Session","Endpoint","SiLink","SiAdapter","SiNode","Wp","utils","table","string","math","os","io","debug","load","loadstring","dofile","require","require_api","print","type","pairs","ipairs","next","select","pcall","xpcall","error","assert","setmetatable","getmetatable","rawget","rawset","tonumber","tostring","unpack","_G","_ENV","_VERSION","json","spa","GObject","GLib","bit32","utf8","Script","Feature","Features","Interest","Constraint","ImplMetadata","ImplModule"}

local found, missing = {}, {}
for _, n in ipairs(names) do
  local v = _ENV[n]
  if v == nil then missing[#missing+1] = n else found[#found+1] = n .. "=" .. type(v) end
end
print("FOUND " .. table.concat(found, " "))
print("MISSING " .. table.concat(missing, " "))
print("ENV=" .. type(_ENV) .. " G=" .. tostring(_G) .. " VERSION=" .. _VERSION)
print("debug.getregistry=" .. type(debug.getregistry))
Core.quit()
