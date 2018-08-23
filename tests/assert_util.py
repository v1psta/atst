def dict_contains(superset, subset):
    """
    Returns True if dict a is a superset of dict b.
    """
    return all(item in superset.items() for item in subset.items())
