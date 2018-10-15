from flask import render_template
import werkzeug.exceptions as werkzeug_exceptions

import atst.domain.exceptions as exceptions


def make_error_pages(app):
    def log_error(e):
        error_message = e.message if hasattr(e, "message") else str(e)
        app.logger.error(error_message)

    @app.errorhandler(werkzeug_exceptions.NotFound)
    @app.errorhandler(exceptions.NotFoundError)
    @app.errorhandler(exceptions.UnauthorizedError)
    # pylint: disable=unused-variable
    def not_found(e):
        log_error(e)
        return render_template("error.html", message="Not Found"), 404

    @app.errorhandler(exceptions.UnauthenticatedError)
    # pylint: disable=unused-variable
    def unauthorized(e):
        log_error(e)
        return render_template("error.html", message="Log in Failed"), 401

    @app.errorhandler(Exception)
    # pylint: disable=unused-variable
    def exception(e):
        log_error(e)
        return (
            render_template("error.html", message="An Unexpected Error Occurred"),
            500,
        )

    return app
