local keys = {"linking.follow-default-target","node.stream.restore-props",
              "node.features.audio.no-dsp","device.routes.default-sink-volume",
              "bluetooth.profile-preference","node.stream.default-media-role"}
local o = {}
for _, k in ipairs(keys) do
  o[#o+1] = string.format("%s=%s/%s/%s", k, tostring(Settings.get_boolean(k)),
            tostring(Settings.get_float(k)), tostring(Settings.get_string(k)))
end
print(table.concat(o, " "))
Core.quit()
