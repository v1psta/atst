from flask import Blueprint, render_template, g
import pendulum

from atst.domain.requests import Requests

bp = Blueprint("atst", __name__)


@bp.route("/")
def root():
    return render_template("root.html")


@bp.route("/home")
def home():
    return render_template("home.html")


@bp.route("/styleguide")
def styleguide():
    return render_template("styleguide.html")


@bp.route('/<path:path>')
def catch_all(path):
    return render_template("{}.html".format(path))
