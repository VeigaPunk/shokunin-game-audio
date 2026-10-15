local ok, mod = pcall(LocalModule, 'libpipewire-module-filter-chain', [==[node.description=r92b_wpx,filter.graph={nodes=[{type=builtin,name=n0,label=copy}]},audio.channels=1,audio.position=[MONO],capture.props={node.name=r92b_wpx_in,node.autoconnect=false,media.class=Audio/Sink},playback.props={node.name=r92b_wpx_out,node.autoconnect=false}]==])
print('lm-ok pcall ok=' .. tostring(ok) .. ' mod=' .. tostring(mod))
Core.timeout_add(2200, function() Core.quit() end)
