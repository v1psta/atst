from flask import render_template, current_app, url_for, redirect, request
from flask_wtf.csrf import CSRFError
import werkzeug.exceptions as werkzeug_exceptions

import atst.domain.exceptions as exceptions
from atst.domain.invitations import (
    InvitationError,
    ExpiredError as InvitationExpiredError,
    WrongUserError as InvitationWrongUserError,
)


def log_error(e):
    error_message = e.message if hasattr(e, "message") else str(e)
    current_app.logger.error(error_message)


def handle_error(e, message="Not Found", code=404):
    log_error(e)
    return render_template("error.html", message=message), code


def make_error_pages(app):
    @app.errorhandler(werkzeug_exceptions.NotFound)
    @app.errorhandler(exceptions.NotFoundError)
    @app.errorhandler(exceptions.UnauthorizedError)
    # pylint: disable=unused-variable
    def not_found(e):
        return handle_error(e)

    @app.errorhandler(exceptions.UnauthenticatedError)
    # pylint: disable=unused-variable
    def unauthorized(e):
        return handle_error(e, message="Log in Failed", code=401)

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
    @app.errorhandler(InvitationWrongUserError)
    # pylint: disable=unused-variable
    def invalid_invitation(e):
        return handle_error(e, message="The link you followed is invalid.", code=404)

    @app.errorhandler(InvitationExpiredError)
    # pylint: disable=unused-variable
    def invalid_invitation(e):
        return handle_error(
            e, message="The invitation you followed has expired.", code=404
        )

    return app
