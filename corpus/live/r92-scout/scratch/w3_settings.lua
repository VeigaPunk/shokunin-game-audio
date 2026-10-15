
print("api=" .. tostring(Core.require_api("support.settings")))
local keys = { "node.stream.restore-props", "node.stream.restore-target",
               "device.routes.default-sink-volume", "device.routes.default-source-volume",
               "node.restore-default-targets", "device.restore-profile",
               "bluetooth.use-persistent-storage", "node.features.audio.monitor-ports" }
for _, k in ipairs(keys) do
  local b = Settings.get_boolean(k)
  local f = Settings.get_float(k)
  local s = Settings.get_string(k)
  print(string.format("SET %s bool=%s float=%s str=%s", k, tostring(b), tostring(f), tostring(s)))
end
Core.quit()
