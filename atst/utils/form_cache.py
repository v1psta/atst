from hashlib import sha256
import pickle


DEFAULT_CACHE_NAME = "formcache"


class FormCache(object):
    def __init__(self, redis):
        self.redis = redis

    def from_request(self, http_request):
        cache_key = http_request.args.get("formCache")
        if cache_key:
            return self.read(cache_key)

    def write(self, formdata, expiry_seconds=3600, key_prefix=DEFAULT_CACHE_NAME):
        value = pickle.dumps(formdata)
        hash_ = sha256().hexdigest()
        self.redis.setex(
            name=self._key(key_prefix, hash_), value=value, time=expiry_seconds
        )
        return hash_

    def read(self, formdata_key, key_prefix=DEFAULT_CACHE_NAME):
        data = self.redis.get(self._key(key_prefix, formdata_key))
        return pickle.loads(data) if data is not None else {}

    @staticmethod
    def _key(prefix, hash_):
        return "{}:{}".format(prefix, hash_)
