from flask import Blueprint

task_orders_bp = Blueprint("task_orders", __name__)

from . import new
