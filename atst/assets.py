from webassets import Environment, Bundle
from atst.home import home

environment = Environment(
    directory=home.child("scss"),
    url="/static"
)

css = Bundle(
    "atat.scss",
    filters="scss",
    output="../static/assets/out.%(version)s.css",
    depends=("**/*.scss"),
)

environment.register("css", css)
