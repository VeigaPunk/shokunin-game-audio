print("argv_type=" .. type(arg))
print("select=" .. tostring(select("#", ...)))
print("ENV_Core=" .. tostring(_ENV.Core ~= nil))
Core.quit()
