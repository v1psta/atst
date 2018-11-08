from werkzeug.datastructures import ImmutableDict

from atst.utils.form_cache import DEFAULT_CACHE_NAME, cache_form_data, retrieve_form_data

def test_cache_form_data(app):
    data = ImmutableDict({"kessel_run": "12 parsecs"})
    key = cache_form_data(app.redis, data)
    assert app.redis.get("{}:{}".format(DEFAULT_CACHE_NAME, key))


def test_retrieve_form_data(app):
    data = ImmutableDict({"class": "corellian"})
    key = cache_form_data(app.redis, data)
    retrieved = retrieve_form_data(app.redis, key)
    assert retrieved == data
