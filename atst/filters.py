def iconSvg(name):
    with open('static/icons/'+name+'.svg') as contents:
        return contents.read()


def register_filters(app):
    app.jinja_env.filters['iconSvg'] = iconSvg
