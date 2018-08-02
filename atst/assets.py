from flask_assets import Environment, Bundle

environment = Environment()

css = Bundle(
    "../scss/atat.scss",
    filters="scss",
    output="../static/assets/out.%(version)s.css",
    depends=("**/*.scss"),
)

environment.register("css", css)
