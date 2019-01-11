import sys
import gc

def reload(mod):
    "De-allocate module, garbage collect and then reload module."

    mod_name = mod.__name__
    del sys.modules[mod_name]
    gc.collect()
    return __import__(mod_name)

def not_implemented(*args, **kwargs):
    raise NotImplementedError()
