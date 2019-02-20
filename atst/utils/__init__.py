import re


def first_or_none(predicate, lst):
    return next((x for x in lst if predicate(x)), None)


def getattr_path(obj, path, default=None):
    _obj = obj
    for item in path.split("."):
        if isinstance(_obj, dict):
            _obj = _obj.get(item)
        else:
            _obj = getattr(_obj, item, default)
    return _obj


def update_obj(obj, dct, ignore_vals=[None]):
    for k, v in dct.items():
        if hasattr(obj, k) and v not in ignore_vals:
            setattr(obj, k, v)
    return obj


def camel_to_snake(camel_cased):
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_cased)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def drop(keys, dct):
    _keys = set(keys)
    return {k: v for k, v in dct.items() if k not in _keys}


def pick(keys, dct):
    _keys = set(keys)
    return {k: v for (k, v) in dct.items() if k in _keys}
