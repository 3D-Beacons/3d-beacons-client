from flask import Blueprint
from flask import current_app as app

swagger_server_bp = Blueprint(
    'swagger_server_bp', __name__,
)
