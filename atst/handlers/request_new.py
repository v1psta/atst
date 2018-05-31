import tornado
from atst.handler import BaseHandler
import tornado.httputil

class RequestNew(BaseHandler):
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

    @tornado.web.authenticated
    def post(self, screen = 1):
        self.check_xsrf_cookie()
        all = {
                    arg: self.get_argument(arg)
                        for arg in self.request.arguments
                        if not arg.startswith('_')
               }
        print( all )
        import json
        self.write( json.dumps( all ) )

    @tornado.web.authenticated
    def get(self, screen = 1):
        self.render( 'requests/screen-%d.html.to' % int(screen),
                    page = self.page,
                    screens = self.screens,
                    current = int(screen),
                    next_screen = int(screen) + 1 )
