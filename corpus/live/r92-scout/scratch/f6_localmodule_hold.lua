
print("LocalModule type=" .. type(LocalModule))
local ok, mod = pcall(LocalModule, "libpipewire-module-filter-chain", [==[node.description=r92s_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},audio.channels=1,audio.position=[MONO],capture.props={node.name=r92s_wpx_in,node.autoconnect=false,media.class=Audio/Sink},playback.props={node.name=r92s_wpx_out,node.autoconnect=false}]==])
print("pcall ok=" .. tostring(ok) .. " mod=" .. tostring(mod))
Core.timeout_add(2500, function() print("quitting"); Core.quit() end)
