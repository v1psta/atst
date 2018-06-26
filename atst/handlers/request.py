import tornado
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


def map_request(request):
    return {
        "order_id": request["id"],
        "is_new": False,
        "status": "Pending",
        "app_count": 1,
        "is_new": False,
        "date": "",
        "full_name": "Richard Howard",
    }


class Request(BaseHandler):
    def initialize(self, page, requests_client):
        self.page = page
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        response = yield self.requests_client.get(
            "/users/{}/requests".format(self.get_current_user())
        )
        requests = response.json["requests"]
        mapped_requests = [map_request(request) for request in requests]
        self.render("requests.html.to", page=self.page, requests=mapped_requests)
