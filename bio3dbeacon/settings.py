import os
from pathlib import Path
from prettyconf import config

BEACON_NAME = 'ModelsRUs (London)'


RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTX_VALIDATE = True
RESTX_MASK_SWAGGER = False
RESTX_ERROR_404_HELP = False

DATABASE_DRIVER = config('DATABASE_DRIVER', default='postgresql')
DATABASE_HOST = config('DATABASE_HOST', default='localhost')
DATABASE_NAME = config('DATABASE_NAME')
DATABASE_PORT = config('DATABASE_PORT', default='5432')
DATABASE_READER_USER = config(
    'DATABASE_READER_USER', default='bio3dbeacon_reader')
DATABASE_READER_PASSWORD = config(
    'DATABASE_READER_PASSWORD', default='bio3dbeacon_reader')
DATABASE_WRITER_USER = config('DATABASE_WRITER_USER')
DATABASE_WRITER_PASSWORD = config('DATABASE_WRITER_PASSWORD')

SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = f'{DATABASE_DRIVER}://{DATABASE_WRITER_USER}:{DATABASE_WRITER_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'

ROOT_DIR = (Path(__file__) / '..' / '..').resolve()
MOLSTAR_GITHUB_URL = 'https://github.com/molstar/molstar.git'
QMEAN_SUBMIT_URL = 'https://swissmodel.expasy.org/qmean/submit/'
CONTACT_EMAIL = 'i.sillitoe@ucl.ac.uk'
GEMMI_EXE = ROOT_DIR / 'gemmi' / 'gemmi'
WORK_DIR = ROOT_DIR / 'work_dir'
MOLSTAR_PREPROCESS_EXE = ROOT_DIR / 'molstar' / \
    'build' / 'model-server' / 'preprocess.js'

SECRET_KEY = config(
    'SECRET_KEY', default='fourteen-ants-marching-over-mushrooms')
