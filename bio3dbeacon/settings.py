import os
from pathlib import Path

BEACON_NAME = 'ModelsRUs (London)'

FLASK_SERVER_NAME = 'localhost:5000'
FLASK_DEBUG = True

RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTX_VALIDATE = True
RESTX_MASK_SWAGGER = False
RESTX_ERROR_404_HELP = False

DATABASE_DRIVER = os.environ.get('DATABASE_DRIVER', 'postgresql')
DATABASE_HOST = os.environ.get('DATABASE_HOST', 'localhost')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'bio3dbeacon_client')
DATABASE_READER_USER = os.environ.get(
    'DATABASE_READER_USER', 'bio3dbeacon_reader')
DATABASE_READER_PASSWORD = os.environ.get(
    'DATABASE_READER_PASSWORD', 'bio3dbeacon_reader')
DATABASE_WRITER_USER = os.environ.get(
    'DATABASE_WRITER_USER', 'bio3dbeacon_writer')
DATABASE_WRITER_PASSWORD = os.environ.get('DATABASE_WRITER_PASSWORD', None)

SQLALCHEMY_TRACK_MODIFICATIONS = False

ROOT_DIR = (Path(__file__) / '..' / '..').resolve()
MOLSTAR_GITHUB_URL = 'https://github.com/molstar/molstar.git'
QMEAN_SUBMIT_URL = 'https://swissmodel.expasy.org/qmean/submit/'
CONTACT_EMAIL = 'i.sillitoe@ucl.ac.uk'
GEMMI_EXE = ROOT_DIR / 'gemmi' / 'gemmi'
WORK_DIR = ROOT_DIR / 'work_dir'
MOLSTAR_PREPROCESS_EXE = ROOT_DIR / 'molstar' / \
    'build' / 'model-server' / 'preprocess.js'

SECRET_KEY = 'fourteen-ants-marching-over-mushrooms'
