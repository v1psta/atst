import re


def first_or_none(predicate, lst):
    return next((x for x in lst if predicate(x)), None)


def deep_merge(source, destination: dict):
    """
    Merge source dict into destination dict recursively.
    """

    def _deep_merge(a, b):
        for key, value in a.items():
            if isinstance(value, dict):
                node = b.setdefault(key, {})
                _deep_merge(value, node)
            else:
                b[key] = value

        return b

    return _deep_merge(source, dict(destination))


def getattr_path(obj, path, default=None):
    _obj = obj
    for item in path.split("."):
        if isinstance(_obj, dict):
            _obj = _obj.get(item)
        else:
            _obj = getattr(_obj, item, default)
    return _obj


def update_obj(obj, dct):
    for k, v in dct.items():
        if hasattr(obj, k) and v is not None:
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
