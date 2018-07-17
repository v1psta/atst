class UI:

    def icon(name):
        with open("../static/icons/%(name)s.svg") as svg:
            return svg.read()
