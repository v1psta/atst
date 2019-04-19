from flask import Blueprint

task_orders_bp = Blueprint("task_orders", __name__)

from . import index
from . import new
from . import invitations
from . import officer_reviews
from . import signing
from . import downloads
from atst.utils.context_processors import portfolio as portfolio_context_processor

task_orders_bp.context_processor(portfolio_context_processor)
