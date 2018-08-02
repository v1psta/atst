from flask import Blueprint, render_template, g
import pendulum

from atst.domain.requests import Requests

bp = Blueprint("atst", __name__)


@bp.route("/")
def home():
    return render_template("home.html")
