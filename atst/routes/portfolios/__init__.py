from flask import Blueprint, request as http_request, g, render_template
from operator import attrgetter

portfolios_bp = Blueprint("portfolios", __name__)

from . import index
from . import invitations
from . import admin
from atst.utils.context_processors import portfolio as portfolio_context_processor


portfolios_bp.context_processor(portfolio_context_processor)
