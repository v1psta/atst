from flask import render_template


def make_error_pages(app):
    @app.errorhandler(404)
    def not_found(e):
        return render_template("not_found.html"), 404


    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('unauthorized.html'), 401

