from flask import render_template

import atst.domain.exceptions as exceptions


def make_error_pages(app):
    @app.errorhandler(exceptions.NotFoundError)
    @app.errorhandler(exceptions.UnauthorizedError)
    # pylint: disable=unused-variable
    def not_found(e):
        app.logger.error(e.message)
        return render_template("not_found.html"), 404

    @app.errorhandler(exceptions.UnauthenticatedError)
    # pylint: disable=unused-variable
    def unauthorized(e):
        app.logger.error(e.message)
        return render_template("unauthenticated.html"), 401

    return app
