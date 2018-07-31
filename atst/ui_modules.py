from tornado.web import UIModule
# from tornado.template import raw
import re


    # def Alert(title, message=None, actions=None, level='info')
    #     return self.render_string(
    #         "components/alert.html.to",
    #         title=title,
    #         message=message,
    #         actions=actions,
    #         level=level
    #     )

    # class TextInput(UIModule):
    #     def render(self, field, placeholder=''):
    #         return self.render_string(
    #         "components/text_input.html.to",
    #         field=field,
    #         label=re.sub('<[^<]+?>', '', str(field.label)),
    #         errors=field.errors,
    #         placeholder=placeholder,
    #         description=field.description)

    # class OptionsInput(UIModule):
    #     def render(self, field, inline=False):
    #         return self.render_string(
    #         "components/options_input.html.to",
    #         field=field,
    #         label=re.sub('<[^<]+?>', '', str(field.label)),
    #         errors=field.errors,
    #         description=field.description,
    #         inline=inline)

def get_template(*args, **kwargs):
    pass

def Icon(name, classes=''):
    with open('static/icons/%s.svg' % name) as svg:
        return get_template("components/icon.html.to").render(
            svg=svg.read(), name=name, classes=classes)


def SidenavItem(label=None, href=None, active=False, icon=None, subnav=None):
    return get_template("navigation/_sidenav_item.html.to").render(
        label=label,
        href=href,
        active=active,
        icon=icon,
        subnav=subnav
    )
