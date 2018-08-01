from flask_assets import Environment, Bundle
from atst.home import home

assets = Environment()

css = Bundle(
    "../scss/atat.scss",
    filters="scss",
    output="../static/assets/out.%(version)s.css",
    depends=("**/*.scss"),
)

assets.register("css", css)
