local keys = {"linking.follow-default-target","follow-default-target",
              "node.stream.restore-props","restore-props",
              "node.features.audio.no-dsp","device.routes.default-sink-volume"}
for _,k in ipairs(keys) do
  local b = Settings.get_boolean(k)
  local f = Settings.get_float(k)
  local s = Settings.get_string(k)
  print(string.format("%-38s bool=%s float=%s str=%s", k, tostring(b), tostring(f), tostring(s)))
end
Core.quit()
