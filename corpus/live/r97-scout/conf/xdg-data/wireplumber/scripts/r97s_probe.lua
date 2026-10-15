-- r97-scout in-daemon settings probe (loaded only by the private instance)
local log = Log.open_topic("r97s")
local keys = {"linking.follow-default-target", "node.stream.restore-props",
              "node.features.audio.no-dsp", "device.routes.default-sink-volume",
              "bluetooth.profile-preference", "node.stream.default-media-role",
              "monitor.alsa.autodetect-hdmi-channels"}
log:info("r97s probe script loaded, lua=" .. _VERSION)
for _, k in ipairs(keys) do
  log:info(string.format("SET %s bool=%s float=%s str=%s", k,
      tostring(Settings.get_boolean(k)), tostring(Settings.get_float(k)),
      tostring(Settings.get_string(k))))
end
