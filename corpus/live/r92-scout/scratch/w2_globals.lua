
local names = { "Core", "Settings", "Log", "LocalModule", "PipewireObject",
                "ObjectManager", "SessionItem", "EventDispatcher", "Script",
                "Components", "Metadata", "Node", "Device", "Client", "Link",
                "Plugin", "Conf", "Json", "Utils", "Debug", "Loop", "Timer" }
for _, n in ipairs(names) do
  local v = rawget(_G, n)
  print(string.format("GLOBAL %s type=%s", n, type(v)))
end
print("_VERSION " .. tostring(_VERSION))
Core.quit()
