import logging
import os
from pathlib import Path

from flask import Flask, Blueprint
from flask_migrate import Migrate

LOG = logging.getLogger(__name__)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        settings_file = Path(__file__).parent / 'settings.py'
        app.config.from_pyfile(settings_file, silent=False)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from bio3dbeacon.database import get_db

    with app.app_context():
        db = get_db()
        db.init_app(app)
        migrate = Migrate(app, db)

    from bio3dbeacon.api.restx import api
    from bio3dbeacon.frontend.frontend import frontend_bp

    api.init_app(app)

    app.register_blueprint(frontend_bp)

    return app


def flask_cli():
    return create_app()


def main():
    app = create_app()
    app.run(debug=settings.FLASK_DEBUG)


if __name__ == "__main__":
    main()
