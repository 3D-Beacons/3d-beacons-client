import logging

import click
from flask import g
from flask import current_app
from flask.cli import with_appcontext

from .models import db as _db

LOG = logging.getLogger(__name__)


def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called
    again.
    """
    if "db" not in g:
        g.db = _db

    return g.db


def close_db():
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""

    db = get_db()
    LOG.debug("init_db.drop_all")
    db.drop_all()

    LOG.debug("init_db.create_all")
    db.create_all()
    LOG.debug("init_db.session.commit")
    db.session.commit()


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
