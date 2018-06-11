import requests
import tornado.gen
from concurrent.futures import ThreadPoolExecutor
from tornado.httpclient import AsyncHTTPClient


class ApiClient(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.executor = ThreadPoolExecutor()

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return (yield self.make_request('GET', self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return self.make_request('PUT', self.base_url + path, **kwargs)

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return self.make_request('POST', self.base_url + path, **kwargs)

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return self.make_request('DELETE', self.base_url + path, **kwargs)

    @tornado.gen.coroutine
    def make_request(self, method, url, **kwargs):
        def _make_request(_method, _url, **kwargs):
            return requests.request(_method, _url, **kwargs)

        return (yield self.executor.submit(_make_request, 'GET', url))
