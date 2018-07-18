from tornado.web import UIModule

class Icon(UIModule):
    def render(self, name, classes=''):
        with open('static/icons/%s.svg' % name) as svg:
            return self.render_string(
              "components/icon.html.to", svg=svg.read(), name=name, classes=classes)
