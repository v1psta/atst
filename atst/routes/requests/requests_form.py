from flask import g, redirect, render_template, url_for, request as http_request

from . import requests_bp
from atst.domain.requests import Requests
from atst.routes.requests.jedi_request_flow import JEDIRequestFlow
from atst.models.permissions import Permissions
from atst.domain.exceptions import UnauthorizedError


@requests_bp.route("/requests/new/<int:screen>", methods=["GET"])
def requests_form_new(screen):
    jedi_flow = JEDIRequestFlow(screen, request=None)

    return render_template(
        "requests/screen-%d.html" % int(screen),
        f=jedi_flow.form,
        data=jedi_flow.current_step_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=screen + 1,
        can_submit=jedi_flow.can_submit,
    )


@requests_bp.route(
    "/requests/new/<int:screen>", methods=["GET"], defaults={"request_id": None}
)
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["GET"])
def requests_form_update(screen=1, request_id=None):
    if request_id:
        _check_can_view_request(request_id)

    request = Requests.get(request_id) if request_id is not None else None
    jedi_flow = JEDIRequestFlow(screen, request, request_id=request_id)

    return render_template(
        "requests/screen-%d.html" % int(screen),
        f=jedi_flow.form,
        data=jedi_flow.current_step_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=screen + 1,
        request_id=request_id,
        can_submit=jedi_flow.can_submit,
    )


@requests_bp.route(
    "/requests/new/<int:screen>", methods=["POST"], defaults={"request_id": None}
)
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["POST"])
def requests_update(screen=1, request_id=None):
    screen = int(screen)
    post_data = http_request.form
    current_user = g.current_user
    existing_request = Requests.get(request_id) if request_id is not None else None
    jedi_flow = JEDIRequestFlow(
        screen,
        post_data=post_data,
        request_id=request_id,
        current_user=current_user,
        existing_request=existing_request,
    )

    rerender_args = dict(
        f=jedi_flow.form,
        data=post_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=jedi_flow.next_screen,
        request_id=jedi_flow.request_id,
    )

    if jedi_flow.validate():
        jedi_flow.create_or_update_request()
        valid = jedi_flow.validate_warnings()
        if valid:
            if jedi_flow.next_screen > len(jedi_flow.screens):
                where = "/requests"
            else:
                where = url_for(
                    "requests.requests_form_update",
                    screen=jedi_flow.next_screen,
                    request_id=jedi_flow.request_id,
                )
            return redirect(where)

        else:
            return render_template(
                "requests/screen-%d.html" % int(screen), **rerender_args
            )

    else:
        return render_template("requests/screen-%d.html" % int(screen), **rerender_args)


@requests_bp.route("/requests/submit/<string:request_id>", methods=["POST"])
def requests_submit(request_id=None):
    request = Requests.get(request_id)
    Requests.submit(request)

    if request.status == "approved":
        return redirect("/requests?modal=True")

    else:
        return redirect("/requests")


# TODO: generalize this, along with other authorizations, into a policy-pattern
# for authorization in the application
def _check_can_view_request(request_id):
    if Permissions.REVIEW_AND_APPROVE_JEDI_WORKSPACE_REQUEST in g.current_user.atat_permissions:
        pass
    elif Requests.exists(request_id, g.current_user.id):
        pass
    else:
        raise UnauthorizedError(g.current_user, "view request {}".format(request_id))

