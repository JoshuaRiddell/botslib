# This file is executed on every boot (including wake-boot from deepsleep)
import sys, gc

sys.path[1] = '/flash/lib'
sys.path.append('/flash/assets')
sys.path.append('/flash/core')

def reload(mod):
  "De-allocate module, garbage collect and then reload module."

  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)
