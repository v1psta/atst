from flask import Blueprint, g, render_template, url_for, redirect, request
import pendulum

from atst.routes.requests.jedi_request_flow import JEDIRequestFlow
from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm


requests_bp = Blueprint("requests", __name__)


def map_request(user, request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status,
        "app_count": 1,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": "{} {}".format(user["first_name"], user["last_name"]),
    }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    requests = []
    if (
        "review_and_approve_jedi_workspace_request"
        in g.current_user["atat_permissions"]
    ):
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator_id=g.current_user["id"])

    mapped_requests = [map_request(g.current_user, r) for r in requests]

    return render_template("requests.html", requests=mapped_requests)


@requests_bp.route("/requests/new", defaults={"screen": 1})
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


@requests_bp.route("/requests/new/<int:screen>", methods=["GET"], defaults={"request_id": None})
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["GET"])
def requests_form_update(screen=1, request_id=None):
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


@requests_bp.route("/requests/new/<int:screen>", methods=["POST"], defaults={"request_id": None})
@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["POST"])
def requests_update(screen=1, request_id=None):
    screen = int(screen)
    post_data = request.form
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


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id=None):
    request = Requests.get(request_id)
    form = FinancialForm(data=request.body.get("financial_verification"))
    return render_template(
        "requests/financial_verification.html", f=form, request_id=request_id
    )


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification():
    pass


@requests_bp.route("/requests/submit/<string:request_id>", methods=["POST"])
def requests_submit(request_id=None):
    request = Requests.get(request_id)
    Requests.submit(request)

    if request.status == "approved":
        return redirect("/requests?modal=True")
    else:
        return redirect("/requests")
