#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is used to create the package we'll publish to PyPI.

.. currentmodule:: setup.py
.. moduleauthor:: Ian Sillitoe <i.sillitoe@ucl.ac.uk>
"""

import importlib.util
import os
from pathlib import Path
from setuptools import setup, find_packages
from codecs import open  # Use a consistent encoding.
from os import path


setup(
    name='Bio3DBeaconCLI',
    description="Tool to manage local 3D Beacon install",
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*molstar*", "*gemmi*"]),
    version="0.0.1",
    install_requires=[
        # Include dependencies here
        'typer',
        'fastapi'
    ],
    entry_points="""
    [console_scripts]
    bio3dbeacon-cli=bio3dbeacon.cli
    """,
    python_requires=">=0.0.1",
    license='MIT',  # noqa
    author='Ian Sillitoe',
    author_email='i.sillitoe@ucl.ac.uk',
    # Use the URL to the github repo.
    url='https://github.com/isillitoe/bio3dbeacon',
    keywords=[
        # Add package keywords here.
    ],
    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    classifiers=[
      # How mature is this project? Common values are
      #   3 - Alpha
      #   4 - Beta
      #   5 - Production/Stable
      'Development Status :: 3 - Alpha',

      # Indicate who your project is intended for.
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Libraries',

      # Pick your license.  (It should match "license" above.)
        # noqa
      '''License :: OSI Approved :: MIT License''',
        # noqa
      # Specify the Python versions you support here. In particular, ensure
      # that you indicate whether you support Python 2, Python 3 or both.
      'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True
)
