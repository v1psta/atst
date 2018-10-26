from flask import render_template, current_app, url_for, redirect, request
from flask_wtf.csrf import CSRFError
import werkzeug.exceptions as werkzeug_exceptions

import atst.domain.exceptions as exceptions
from atst.domain.invitations import InvitationError


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

    @app.errorhandler(CSRFError)
    # pylint: disable=unused-variable
    def session_expired(e):
        log_error(e)
        return redirect(url_for("atst.root", sessionExpired=True, next=request.path))

    @app.errorhandler(Exception)
    # pylint: disable=unused-variable
    def exception(e):
        log_error(e)
        if current_app.debug:
            raise e
        return (
            render_template("error.html", message="An Unexpected Error Occurred"),
            500,
        )

    @app.errorhandler(InvitationError)
    # pylint: disable=unused-variable
    def expired_invitation(e):
        log_error(e)
        return (
            render_template(
                "error.html", message="The invitation you followed has expired."
            ),
            404,
        )

    return app
