from atst.handler import BaseHandler

mock_workspaces = [
          {
            'name' : 'Unclassified IaaS and PaaS for Defense Digital Service (DDS)',
            'task_order' : {
                'number' : 123456,
            },
            'user_count' : 23,
          }
        ]

class Workspace(BaseHandler):

    def initialize(self, page):
        self.page = page

    def get(self):
        self.render( 'workspaces.html.to', page = self.page, workspaces = mock_workspaces )
