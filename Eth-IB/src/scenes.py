"""Registry of scenes (order = video order)."""
from collections import OrderedDict
import importlib
ORDER = ["open","history","stack","three","verbs","credits","routing","congestion","sharp","fattree","dragonfly","hardware","universe","close","refs"]
REGISTRY = OrderedDict()
_found = {}
for _m in ["scenes_a","scenes_b","scenes_c","scenes_d","scenes_e"]:
    try:
        m = importlib.import_module(_m)
    except ModuleNotFoundError as e:
        if e.name != _m: raise
        continue
    for n in dir(m):
        o = getattr(m, n)
        if isinstance(o, type) and getattr(o, "id", "") and o.__module__ == m.__name__:
            _found[o.id] = o
for _i in ORDER:
    if _i in _found: REGISTRY[_i] = _found[_i]
