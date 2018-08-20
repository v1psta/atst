def iconSvg(name):
    with open('static/icons/'+name+'.svg') as contents:
        return contents.read()


def dollars(value):
    try:
        numberValue = float(value)
    except ValueError:
        numberValue = 0
    return "${:,.0f}".format(numberValue)


def register_filters(app):
    app.jinja_env.filters['iconSvg'] = iconSvg
    app.jinja_env.filters['dollars'] = dollars
