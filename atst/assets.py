from webassets import Environment, Bundle
from atst.home import home

assets = Environment(
    directory=home.child("scss"),
    url="/static"
)
print(assets.url_expire)
css = Bundle(
    "atat.scss",
    filters="scss",
    output="../static/assets/out.%(version)s.css",
    depends=("**/*.scss"),
)

assets.register("css", css)
