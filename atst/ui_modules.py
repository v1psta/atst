from tornado.web import UIModule

# from tornado.template import raw
import re


class Alert(UIModule):
    def render(self, title, message=None, actions=None, level="info"):
        return self.render_string(
            "components/alert.html.to",
            title=title,
            message=message,
            actions=actions,
            level=level,
        )


class TextInput(UIModule):
    def render(self, field, placeholder=""):
        return self.render_string(
            "components/text_input.html.to",
            field=field,
            label=re.sub("<[^<]+?>", "", str(field.label)),
            errors=field.errors,
            placeholder=placeholder,
            description=field.description,
        )


class OptionsInput(UIModule):
    def render(self, field, inline=False):
        return self.render_string(
            "components/options_input.html.to",
            field=field,
            label=re.sub("<[^<]+?>", "", str(field.label)),
            errors=field.errors,
            description=field.description,
            inline=inline,
        )


class Icon(UIModule):
    def render(self, name, classes=""):
        with open("static/icons/%s.svg" % name) as svg:
            return self.render_string(
                "components/icon.html.to", svg=svg.read(), name=name, classes=classes
            )


class SidenavItem(UIModule):
    def render(self, label, href, active=False, icon=None, subnav=None):
        return self.render_string(
            "navigation/_sidenav_item.html.to",
            label=label,
            href=href,
            active=active,
            icon=icon,
            subnav=subnav,
        )


class EmptyState(UIModule):
    def render(self, message, actionLabel, actionHref, icon=None):
        return self.render_string(
            "components/empty_state.html.to",
            message=message,
            actionLabel=actionLabel,
            actionHref=actionHref,
            icon=icon,
        )
