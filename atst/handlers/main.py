from atst.handler import BaseHandler

class MainHandler(BaseHandler):
    def get(self):
        self.render("hello.html.to")
