# This file is executed on every boot (including wake-boot from deepsleep)
import sys, gc

sys.path[1] = '/flash/lib'

def reload(mod):
  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)
