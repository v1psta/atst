import tornado
from atst.handler import BaseHandler

class Login(BaseHandler):

    def initialize(self, page):
        self.page = page

    def get(self):
        self.render( '%s.html.to' % self.page, page = self.page )
