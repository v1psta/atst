from tornado.web import UIModule

class Alert(UIModule):
    def render(self, title, message=None, actions=None, level='info'):
        return self.render_string(
          "components/alert.html.to",
          title=title,
          message=message,
          actions=actions,
          level=level)

class Icon(UIModule):
    def render(self, name, classes=''):
        with open('static/icons/%s.svg' % name) as svg:
            return self.render_string(
              "components/icon.html.to", svg=svg.read(), name=name, classes=classes)

class SidenavItem(UIModule):
    def render(self, label, href, active=False, icon=None):
        return self.render_string(
          "navigation/_sidenav_item.html.to",
          label=label,
          href=href,
          active=active,
          icon=icon)
