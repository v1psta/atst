from flask import Blueprint, g, render_template
import pendulum

from atst.domain.requests import Requests

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
    if "review_and_approve_jedi_workspace_request" in g.current_user["atat_permissions"]:
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator_id=g.current_user["id"])

    mapped_requests = [map_request(g.current_user, r) for r in requests]

    return render_template("requests.html", requests=mapped_requests)


@requests_bp.route("/requests/new/<int:screen>", methods=["GET"])
def requests_new():
    pass


@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["GET"])
def requests_form_update():
    pass


@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification():
    pass


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification():
    pass
