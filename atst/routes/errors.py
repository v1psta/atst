from flask import render_template

import atst.domain.exceptions as exceptions


def make_error_pages(app):
    @app.errorhandler(exceptions.NotFoundError)
    @app.errorhandler(exceptions.UnauthorizedError)
    # pylint: disable=unused-variable
    def not_found(e):
        app.logger.error(e.message)
        return render_template("error.html", message="Not Found"), 404

    @app.errorhandler(exceptions.UnauthenticatedError)
    # pylint: disable=unused-variable
    def unauthorized(e):
        app.logger.error(e.message)
        return render_template("error.html", message="Log in Failed"), 401

    @app.errorhandler(Exception)
    # pylint: disable=unused-variable
    def exception(e):
        app.logger.error(e.message)
        return render_template("error.html", message="An Unexpected Error Occurred"), 500

    return app
