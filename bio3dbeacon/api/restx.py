import logging

from flask import Blueprint
import flask_restx

from .query.endpoints import api as api_query_ns

LOG = logging.getLogger(__name__)

api = flask_restx.Api(version='1.0',
                      title='3D-Beacons Client API',
                      description='3D Beacon Client API',
                      prefix='/api',
                      doc='/swaggerdocs'
                      )

api.add_namespace(api_query_ns, path='/uniprot')
