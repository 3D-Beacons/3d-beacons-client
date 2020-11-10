# bio3dbeacon

Tool to manage local 3D Beacon install

[![Build Status](https://travis-ci.com/3D-Beacons/3d-beacons-client.svg?branch=master)](https://travis-ci.com/3D-Beacons/3d-beacons-client)

## Project Features

* [bio3dbeacon](http://Bio3DBeaconCLI.readthedocs.io/)
* a starter [Click](http://click.pocoo.org/5/) command-line application
* automated unit tests you can run with [pytest](https://docs.pytest.org/en/latest/)
* a [Sphinx](http://www.sphinx-doc.org/en/master/) documentation project

## Getting Started

The project's documentation contains a section to help you
[get started](https://Bio3DBeaconCLI.readthedocs.io/en/latest/getting_started.html) as a developer or
user of the library.

## Develop

Run the required services (db, etc):

```
docker-compose -f docker-compose.dev.yml up -d
```

Install and run the webserver

```
python3 -m venv venv
pip install -r requirements.txt
export FLASK_ENV=development
flask run
```

## Deploy

```
cp env.prod.template env.prod
vim env.prod
export FLASK_ENV=production
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

## Resources

Below are some handy resource links.

* [Project Documentation](http://Bio3DBeaconCLI.readthedocs.io/)
* [Click](http://click.pocoo.org/5/) is a Python package for creating beautiful command line interfaces in a composable way with as little code as necessary.
* [Sphinx](http://www.sphinx-doc.org/en/master/) is a tool that makes it easy to create intelligent and beautiful documentation, written by Geog Brandl and licnsed under the BSD license.
* [pytest](https://docs.pytest.org/en/latest/) helps you write better programs.
* [GNU Make](https://www.gnu.org/software/make/) is a tool which controls the generation of executables and other non-source files of a program from the program's source files.


## Authors

* **Ian Sillitoe** - *Initial work* - [github](https://github.com/isillitoe)

See also the list of [contributors](https://github.com/3D-Beacons/3d-beacons-client/contributors) who participated in this project.
