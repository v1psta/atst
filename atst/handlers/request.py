from atst.handler import BaseHandler

class Request(BaseHandler):
    def initialize(self, page):
        self.page = page

    def get(self):
        self.render('requests.html.to', page = self.page)

