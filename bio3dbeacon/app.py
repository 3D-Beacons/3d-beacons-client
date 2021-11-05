import logging
import os
from pathlib import Path

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from bio3dbeacon.config import get_current_config

LOG = logging.getLogger(__name__)

DB = SQLAlchemy()
MA = Marshmallow()

CONFIG_ATTRIBUTES = (
    'WORK_DIR', 
    'QMEAN_SUBMIT_URL', 
    'QMEAN_DOCKER_IMAGE', 
    'PATH_TO_LOCAL_UNICLUST',
    'PATH_TO_LOCAL_QMTL',
    'CONTACT_EMAIL', 
    'GEMMI_EXE', 
    'MOLSTAR_PREPROCESS_EXE')

def create_app(config=None):
    """Creates an instance of Flask app"""

    LOG.debug("Creating app ...")

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        config = get_current_config()

    app.config.from_object(config)

    # copy over config that we want to save
    for key in CONFIG_ATTRIBUTES:
        app.config[key] = getattr(config, key)

    RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    RESTX_ERROR_404_HELP = False

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from bio3dbeacon.database import get_db
    from bio3dbeacon.database.models import ma

    with app.app_context():
        LOG.debug("Creating app ... db.init_app()")
        DB.init_app(app)

        LOG.debug("Creating app ... ma.init_app()")
        MA.init_app(app)

        LOG.debug("Creating app ... Migrate")
        migrate = Migrate(app, DB)

        LOG.debug("Creating app ... done")

    from bio3dbeacon.api.restx import api  #  NOQA
    from bio3dbeacon.frontend.frontend import frontend_bp  # NOQA

    api.init_app(app)

    app.register_blueprint(frontend_bp)

    return app


def flask_cli():
    return create_app()


def main():
    app = create_app()
    app.run()


if __name__ == "__main__":
    main()
