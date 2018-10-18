# This file is executed on every boot (including wake-boot from deepsleep)
import sys
sys.path[1] = '/flash/lib'

import gc
from sys import modules
def reload(mod):
  mod_name = mod.__name__
  del sys.modules[mod_name]
  gc.collect()
  return __import__(mod_name)
