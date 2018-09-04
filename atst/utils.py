def first_or_none(predicate, lst):
    return next((x for x in lst if predicate(x)), None,)
