import logging

from flask_restx import Api

log = logging.getLogger(__name__)

api = Api(version='1.0', title='3D-Beacons Client API',
          description='3D Beacon Client API')
