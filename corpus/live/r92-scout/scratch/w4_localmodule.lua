
print("LocalModule type=" .. type(LocalModule))
local args = "node.description=r92s_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},audio.channels=1,audio.position=[MONO],capture.props={node.name=r92s_wpx_in,node.autoconnect=false,media.class=Audio/Sink},playback.props={node.name=r92s_wpx_out,node.autoconnect=false}"
local ok, mod = pcall(LocalModule, "libpipewire-module-filter-chain", args)
print("LocalModule pcall ok=" .. tostring(ok) .. " mod=" .. tostring(mod))
if ok and mod then
  print("mod type=" .. type(mod) .. " name=" .. tostring(mod.name))
end
Core.quit()
