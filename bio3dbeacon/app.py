import logging
import os
from pathlib import Path

from flask import Flask, Blueprint
from flask_migrate import Migrate

from . import config

LOG = logging.getLogger(__name__)


def create_app(conf=None):

    LOG.info("Creating app ... (test_config=%s)", conf)

    # create and configure the app---------+
    app = Flask(__name__, instance_relative_config=True)

    if conf is not None:
        conf = config.get_current_config()

    app.config.from_object(conf)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from bio3dbeacon.database import get_db

    with app.app_context():
        db = get_db()
        LOG.debug("Creating app ... db.init_app()")
        db.init_app(app)

    from bio3dbeacon.api.restx import api
    from bio3dbeacon.frontend.frontend import frontend_bp

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
