from atst.handler import BaseHandler
import requests
import tornado.gen

mock_workspaces = [
    {
        'name' : 'Unclassified IaaS and PaaS for Defense Digital Service (DDS)',
        'id': '5966187a-eff9-44c3-aa15-4de7a65ac7ff',
        'task_order' : {
            'number' : 123456,
        },
        'user_count' : 23,
    }
]

session = requests.Session()

class Workspace(BaseHandler):

    def initialize(self, page, authz_client):
        self.page = page
        self.authz_client = authz_client

    @tornado.gen.coroutine
    def get(self):
        self.render( 'workspaces.html.to', page = self.page, workspaces = mock_workspaces )
