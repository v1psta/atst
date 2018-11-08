import os
import hashlib
import pickle


DEFAULT_CACHE_NAME = "formcache"


def cache_form_data(redis, formdata, expiry_seconds=3600, key_prefix=DEFAULT_CACHE_NAME):
    value = pickle.dumps(formdata)
    key = hashlib.sha1(os.urandom(64)).hexdigest()
    redis.setex(name="{}:{}".format(key_prefix, key), value=value, time=expiry_seconds)
    return key


def retrieve_form_data(redis, formdata_key, key_prefix="formcache"):
    data = redis.get("{}:{}".format(key_prefix, formdata_key))
    return pickle.loads(data)
