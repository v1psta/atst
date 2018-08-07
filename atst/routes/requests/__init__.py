from flask import Blueprint

requests_bp = Blueprint("requests", __name__)

from . import index
from . import requests_form
from . import financial_verification
