from flask import render_template, g

from . import requests_bp
from atst.forms.data import SERVICE_BRANCHES
from atst.domain.requests import Requests


@requests_bp.route("/requests/approval/<string:request_id>", methods=["GET"])
def approval(request_id):
    request = Requests.get(g.current_user, request_id)
    return render_template("requests/approval.html", data=request.body, service_branches=SERVICE_BRANCHES)
