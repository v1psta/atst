from atst.handler import BaseHandler

class Request(BaseHandler):
    screens = [
            { 'title' : 'first screen', },
            { 'title' : 'second screen', },
            { 'title' : 'third screen', }
     ]

    def initialize(self, page):
        self.page = page

    def get(self, screen = 1):
        self.render( 'requests/screen-%d.html.to' % int(screen),
                    page = self.page,
                    screens = self.screens,
                    current = int(screen),
                    next_screen = int(screen) + 1 )

