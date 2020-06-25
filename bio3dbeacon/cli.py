#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is the entry point for the command-line interface (CLI) application.

It can be used as a handy facility for running the task from a command line.

.. note::

    To learn more about Click visit the
    `project website <http://click.pocoo.org/5/>`_.  There is also a very
    helpful `tutorial video <https://www.youtube.com/watch?v=kNke39OZ2k0>`_.

    To learn more about running Luigi, visit the Luigi project's
    `Read-The-Docs <http://luigi.readthedocs.io/en/stable/>`_ page.

.. currentmodule:: bio3dbeacon.cli
.. moduleauthor:: Ian Sillitoe <i.sillitoe@ucl.ac.uk>
"""
import logging
import os
import pathlib
import subprocess

# pip
import click
import luigi

# local
from bio3dbeacon import __version__
from bio3dbeacon.app import flask_cli
from .tasks import ProcessModelPdb, get_uid_from_file

app = flask_cli()

LOGGING_LEVELS = {
    0: logging.NOTSET,
    1: logging.ERROR,
    2: logging.WARN,
    3: logging.INFO,
    4: logging.DEBUG,
}  #: a mapping of `verbose` option counts to logging levels

logging.basicConfig(level='INFO', format='%(message)s')
LOG = logging.getLogger(__name__)


class Info(object):
    """An information object to pass data between CLI functions."""

    def __init__(self):  # Note: This object must have an empty constructor.
        """Create a new instance."""
        self.verbose: int = 0
        self.root_dir: str = pathlib.Path(__file__).parent.parent.resolve()
        self.molstar_github_url = 'https://github.com/molstar/molstar.git'
        self.molstar_dir = self.root_dir / 'molstar'


# pass_info is a decorator for functions that pass 'Info' objects.
#: pylint: disable=invalid-name
pass_info = click.make_pass_decorator(Info, ensure=True)


# Change the options to below to suit the actual options for your task (or
# tasks).
@click.group()
@click.option("--verbose", "-v", count=True, help="Enable verbose output.")
@pass_info
def cli(info: Info, verbose: int):
    """Run bio3d-beacon-cli."""
    # Use the verbosity count to determine the logging level...
    if verbose > 0:
        logging.basicConfig(
            level=LOGGING_LEVELS[verbose]
            if verbose in LOGGING_LEVELS
            else logging.DEBUG,
            format='%(message)s'
        )
        click.echo(
            click.style(
                f"Verbose logging is enabled. "
                f"(LEVEL={logging.getLogger().getEffectiveLevel()})",
                fg="yellow",
            )
        )
    info.verbose = verbose


@cli.group()
@pass_info
def molstar(_: Info):
    """Functions relating to the MolStar (Coordinate Server)."""


def _run(cmd_args, stderr=None, stdout=None, check=True, work_dir=None):

    cwd = os.getcwd()

    if not stderr:
        stderr = subprocess.PIPE
    if not stdout:
        stdout = subprocess.PIPE
    if not work_dir:
        work_dir = cwd

    try:
        os.chdir(work_dir)
        click.echo(f"CMD: `{' '.join(cmd_args)}`")
        result = subprocess.run(cmd_args, stderr=stderr,
                                stdout=stdout, check=check, encoding='utf-8')
    except subprocess.CalledProcessError as err:
        msg = f"ERROR: failed to run `{' '.join(cmd_args)}`: {err}"
        click.echo(click.style(msg, fg='red'))
        raise
    finally:
        os.chdir(cwd)

    return result


@molstar.command()
@pass_info
def init(info: Info):
    """Initialise the coordinate server."""

    git_repo = info.molstar_github_url

    if os.path.isdir(info.molstar_dir):
        click.echo(
            f"submodule 'molstar' already exists (updating)")
        _run(['git', 'submodule', 'update'])
    else:
        click.echo(
            f"submodule 'molstar' does not exist (adding)")
        _run(['git', 'submodule', 'add', git_repo])

    _run(['NODE_ENV=production', 'npm', 'run', 'build'],
         work_dir=info.molstar_dir)

    _run(['npm', 'install', '-g', 'forever', 'http-server'],
         work_dir=info.molstar_dir)


@molstar.command()
@pass_info
def run(info: Info):
    """Start the molstar coordinate server."""
    click.echo('Starting the molstar server ...')
    _run(['forever', 'start', 'build/server'],
         work_dir=info.molstar_dir)


@molstar.command()
@pass_info
def stop(info: Info):
    """Stop the molstar coordinate server."""
    click.echo('Stopping the coordinate server ...')
    _run(['forever', 'stop', 'build/server'],
         work_dir=info.molstar_dir)


@cli.group()
@pass_info
def model(_: Info):
    """Functions relating to model files."""


@model.command('add')
@click.option('--pdbfile', required=True,
              help='input model PDB file')
@click.option('--workers', default=5,
              help='number of workers')
@pass_info
def add(info: Info, pdbfile, workers):
    """Add a local PDB file"""

    pdbfile = pathlib.Path(pdbfile).resolve()
    click.echo('Working on file: {}'.format(pdbfile))
    uid = get_uid_from_file(pdbfile)
    task = ProcessModelPdb(pdb_file=str(pdbfile), uid=uid)
    try:
        luigi.build([task], workers=workers)
    except Exception as err:
        LOG.error('caught error: %s', err)
        raise


@cli.command()
def version():
    """Get the library version."""
    click.echo(click.style(f"{__version__}", bold=True))
