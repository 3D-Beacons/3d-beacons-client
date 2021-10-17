#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: test_cli
.. moduleauthor:: Ian Sillitoe <i.sillitoe@ucl.ac.uk>

This is the test module for the project's command-line interface (CLI)
module.
"""

import json
import luigi

# fmt: off
import bio3dbeacon
import bio3dbeacon.cli as cli
from bio3dbeacon import __version__
# fmt: on
from click.testing import Result

from .conftest import FIXTURE_PATH


# To learn more about testing Click applications, visit the link below.
# http://click.pocoo.org/5/testing/


def test_version_displays_library_version(cli_runner):
    """
    Arrange/Act: Run the `version` subcommand.
    Assert: The output matches the library version.
    """
    result: Result = cli_runner.invoke(cli.cli, ["version"])
    assert (
        __version__ in result.output.strip()
    ), "Version number should match library version."


def test_verbose_output(cli_runner):
    """
    Arrange/Act: Run the `version` subcommand with the '-v' flag.
    Assert: The output indicates verbose logging is enabled.
    """
    result: Result = cli_runner.invoke(cli.cli, ["-v", "version"])
    assert (
        "Verbose" in result.output.strip()
    ), "Verbose logging should be indicated in output."


def test_model_displays_expected_message(cli_runner):
    """
    Arrange/Act: Run the `model` subcommand.
    Assert:  The output matches the library version.
    """
    result: Result = cli_runner.invoke(cli.cli, ["model"])
    # fmt: off
    assert 'cli' in result.output.strip(), \
        "'model' messages should contain the CLI name."
    # fmt: on


def test_model_add(cli_runner, monkeypatch):
    """
    Arrange/Act: Run the `model add` subsubcommand
    Assert: The PDB file is added to the database
    """

    baker_pfam_path = FIXTURE_PATH / 'baker_pfam'
    orig_pdb_file = baker_pfam_path / 'original' / 'pdb' / 'PF05017.pdb'
    expected_qmean_json_file = baker_pfam_path / \
        'generated' / 'qmean' / 'PF05017_qmean.json'

    original_build = luigi.build

    def mock_build(*args, **kwargs):
        kwargs['local_scheduler'] = True
        return original_build(*args, **kwargs)

    monkeypatch.setattr(luigi, 'build', mock_build)

    def mock_qmean(*args):
        with open(expected_qmean_json_file, 'rt') as fp:
            data = json.load(fp)
        return data

    monkeypatch.setattr(bio3dbeacon.tasks.QmeanRunner,
                        'run_remote', mock_qmean)

    result: Result = cli_runner.invoke(
        cli.cli, ["model", "add", "--pdbfile", str(orig_pdb_file)])

    assert result.exit_code == 0
