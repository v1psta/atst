import tornado
from atst.handler import BaseHandler

mock_requests = [
        {
            'order_id'  : 36552612,
            'date'      : '5/17/2018',
            'is_new'    : True,
            'full_name' : 'Friedrich Straat',
            'app_count' : 2,
            'status'    : 'Pending'
        },
        {
            'order_id'  : 87362910,
            'date'      : '10/2/2017',
            'is_new'    : False,
            'full_name' : 'Pietro Quirinis',
            'app_count' : 1,
            'status'    : 'Complete'
        },
        {
            'order_id'  : 29938172,
            'date'      : '1/7/2017',
            'is_new'    : False,
            'full_name' : 'Marina Borsetti',
            'app_count' : 1,
            'status'    : 'Denied'
        },
        ]

class Request(BaseHandler):
    def initialize(self, page):
        self.page = page

    @tornado.web.authenticated
    def get(self):
        self.render('requests.html.to', page = self.page, requests = mock_requests )
