from flask import render_template, g

from . import requests_bp
from atst.domain.requests import Requests


def task_order_dictionary(task_order):
    return {
        c.name: getattr(task_order, c.name)
        for c in task_order.__table__.columns
        if c.name not in ["id", "attachment_id"]
    }


@requests_bp.route("/requests/approval/<string:request_id>", methods=["GET"])
def approval(request_id):
    request = Requests.get(g.current_user, request_id)
    data = request.body
    if request.task_order:
        data["task_order"] = task_order_dictionary(request.task_order)

    return render_template("requests/approval.html", data=data, financial_review=True)
