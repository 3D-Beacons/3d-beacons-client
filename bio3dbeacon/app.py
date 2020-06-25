import logging

import connexion
from flask import Flask, Blueprint
from flask_migrate import Migrate

from bio3dbeacon import settings
from bio3dbeacon.api.query.endpoints import ns as query_ns
from bio3dbeacon.api.restx import api
from bio3dbeacon.database import db
from bio3dbeacon.frontend.frontend import frontend_bp
from swagger_server import encoder

LOG = logging.getLogger(__name__)


app = Flask(__name__)


def configure_app(flask_app):
    flask_app.config['SERVER_NAME'] = settings.FLASK_SERVER_NAME
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTX_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTX_VALIDATE'] = settings.RESTX_VALIDATE
    flask_app.config['RESTX_MASK_SWAGGER'] = settings.RESTX_MASK_SWAGGER
    flask_app.config['ERROR_404_HELP'] = settings.RESTX_ERROR_404_HELP
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = '{driver}://{user}:{pwd}@{host}/{dbname}'.format(
        driver=settings.DATABASE_DRIVER,
        user=settings.DATABASE_WRITER_USER, pwd=settings.DATABASE_WRITER_PASSWORD,
        host=settings.DATABASE_HOST, dbname=settings.DATABASE_NAME)


def initialise_app(flask_app):
    configure_app(flask_app)

    db.init_app(flask_app)

    migrate = Migrate(app, db)

    api_bp = Blueprint('api', __name__, url_prefix='/api')

    api.init_app(api_bp)
    api.add_namespace(query_ns)
    flask_app.register_blueprint(api_bp)

    flask_app.register_blueprint(frontend_bp)

    swagger_app = connexion.FlaskApp(__name__.split('.')[0])
    swagger_app.app.json_encoder = encoder.JSONEncoder
    swagger_app.add_api('../swagger_server/swagger/swagger.yaml')

    for bp in swagger_app.app.iter_blueprints():
        LOG.info("swagger blueprint: %s", bp)
        flask_app.register_blueprint(bp, url_prefix='/client')


def flask_cli():
    initialise_app(app)
    return app


def main():
    initialise_app(app)
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
