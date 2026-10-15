local ok, mod = pcall(LocalModule, 'libpipewire-module-nope', 'x=1')
print('lm-badmodule pcall ok=' .. tostring(ok) .. ' mod=' .. tostring(mod))
Core.quit()
