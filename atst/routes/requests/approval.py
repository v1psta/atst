from flask import render_template

from . import requests_bp
from atst.forms.data import SERVICE_BRANCHES


@requests_bp.route("/request_approval", methods=["GET"])
def requests_approval():
    return render_template("request_approval.html", service_branches=SERVICE_BRANCHES)
