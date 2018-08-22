from flask import Blueprint

from atst.domain.requests import Requests

requests_bp = Blueprint("requests", __name__)

from . import index
from . import requests_form
from . import financial_verification

@requests_bp.context_processor
def annual_spend_threshold():
    return { "annual_spend_threshold": Requests.ANNUAL_SPEND_THRESHOLD }
