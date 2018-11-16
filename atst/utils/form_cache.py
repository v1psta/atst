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


class FormCache(object):

    def __init__(self, redis):
        self.redis = redis

    def from_request(self, http_request):
        cache_key = http_request.args.get("formCache")
        if cache_key:
            return self.read(cache_key)

    def write(self, formdata, expiry_seconds=3600, key_prefix="formcache"):
        value = pickle.dumps(formdata)
        hash_ = hashlib.sha1(os.urandom(64)).hexdigest()
        self.redis.setex(name=self._key(key_prefix, hash_), value=value, time=expiry_seconds)
        return hash_

    def read(self, formdata_key, key_prefix="formcache"):
        data = self.redis.get(self._key(key_prefix, formdata_key))
        return pickle.loads(data) if data is not None else {}

    @staticmethod
    def _key(prefix, hash_):
        return "{}:{}".format(prefix, hash_)
