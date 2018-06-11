import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from json import dumps, loads


class ApiClient(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.client = AsyncHTTPClient()

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        return (yield self.make_request('GET', self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def put(self, path, **kwargs):
        return (yield self.make_request('PUT', self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def post(self, path, **kwargs):
        return (yield self.make_request('POST', self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def delete(self, path, **kwargs):
        return (yield self.make_request('DELETE', self.base_url + path, **kwargs))

    @tornado.gen.coroutine
    def make_request(self, method, url, **kwargs):
        # If 'json' kwarg is specified, serialize it to 'body' and update
        # the Content-Type.
        if 'json' in kwargs:
            kwargs['body'] = dumps(kwargs['json'])
            del kwargs['json']
            headers = kwargs.get('headers', {})
            headers['Content-Type'] = 'application-json'
            kwargs['headers'] = headers

        response = yield self.client.fetch(url, method=method, **kwargs)
        return self.adapt_response(response)

    def adapt_response(self, response):
        if response.headers['Content-Type'] == 'application/json':
            json = loads(response.body)
            setattr(response, 'json', json)
        return response
