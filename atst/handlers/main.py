import tornado
from atst.handler import BaseHandler


class Main(BaseHandler):
    def initialize(self, page):
        self.page = page

    @tornado.web.authenticated
    def get(self):
        self.render("%s.html.to" % self.page, page=self.page)
