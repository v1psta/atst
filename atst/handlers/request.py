import tornado
import pendulum

from atst.handler import BaseHandler

mock_requests = [
    {
        "order_id": 36552612,
        "date": "5/17/2018",
        "is_new": True,
        "full_name": "Friedrich Straat",
        "app_count": 2,
        "status": "Pending",
    },
    {
        "order_id": 87362910,
        "date": "10/2/2017",
        "is_new": False,
        "full_name": "Pietro Quirinis",
        "app_count": 1,
        "status": "Complete",
    },
    {
        "order_id": 29938172,
        "date": "1/7/2017",
        "is_new": False,
        "full_name": "Marina Borsetti",
        "app_count": 1,
        "status": "Denied",
    },
]


def map_request(user, request):
    time_created = pendulum.parse(request['time_created'])
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        'order_id': request['id'],
        'is_new': is_new,
        'status': request['status'],
        'app_count': 1,
        'is_new': False,
        'date': time_created.format('M/DD/YYYY'),
        'full_name': '{} {}'.format(user['first_name'], user['last_name'])
    }


class Request(BaseHandler):
    def initialize(self, page, requests_client):
        self.page = page
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        user = self.get_current_user()
        response = yield self.requests_client.get(
            '/users/{}/requests'.format(user['id']))
        requests = response.json['requests']
        mapped_requests = [map_request(user, request) for request in requests]
        self.render('requests.html.to', page=self.page, requests=mapped_requests)
