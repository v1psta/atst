from atst.handler import BaseHandler

class Request(BaseHandler):
    screens = [
            { 'title' : 'Details of Use', 
              'subitems' : [
                {'title' : 'Application Details',
                 'id' : 'application-details'},
                {'title' : 'Computation',
                  'id' : 'computation' },
                {'title' : 'Storage',
                  'id' : 'storage' },
                {'title' : 'Usage',
                  'id' : 'usage' },
            ]},
            { 'title' : 'Organizational Info', },
            { 'title' : 'Funding/Contracting', },
            { 'title' : 'Readiness Survey', },
            { 'title' : 'Review & Submit', }
     ]

    def initialize(self, page):
        self.page = page

    def get(self, screen = 1):
        self.render( 'requests/screen-%d.html.to' % int(screen),
                    page = self.page,
                    screens = self.screens,
                    current = int(screen),
                    next_screen = int(screen) + 1 )

