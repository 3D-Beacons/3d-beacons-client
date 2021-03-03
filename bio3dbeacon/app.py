import logging
import os
from pathlib import Path

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

from . import config

LOG = logging.getLogger(__name__)

DB = SQLAlchemy()
MA = Marshmallow()


def create_app():
    """Creates an instance of Flask app"""

    LOG.debug("Creating app ...")

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    conf = config.get_current_config()

    app.config.from_object(conf)

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
