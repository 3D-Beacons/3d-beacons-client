from pathlib import Path
from prettyconf import config

BEACON_NAME = 'ModelsRUs (London)'

ROOT_DIR = (Path(__file__) / '..' / '..').resolve()
MOLSTAR_GITHUB_URL = 'https://github.com/molstar/molstar.git'
QMEAN_SUBMIT_URL = 'https://swissmodel.expasy.org/qmean/submit/'
CONTACT_EMAIL = 'i.sillitoe@ucl.ac.uk'
GEMMI_EXE = ROOT_DIR / 'gemmi' / 'gemmi'
WORK_DIR = ROOT_DIR / 'work_dir'
MOLSTAR_PREPROCESS_EXE = ROOT_DIR / 'molstar' / \
    'build' / 'model-server' / 'preprocess.js'


class Config(object):
    DEBUG = False
    TESTING = False

    RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    RESTX_ERROR_404_HELP = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = config(
        'SECRET_KEY', default='fourteen-ants-marching-over-mushrooms')

    SQLALCHEMY_ECHO = False

    SQLALCHEMY_DATABASE_URI = None


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        db_uri = config('DATABASE_URI',
                        default='postgres://{}:{}@{}:{}/{}'.format(
                            config('DATABASE_USER'),
                            config('DATABASE_PASSWORD'),
                            config('DATABASE_HOST', default='localhost'),
                            config('DATABASE_PORT', default='5432'),
                            config('DATABASE_NAME'),
                        ))
        return db_uri


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True


def get_current_config():
    app_mode = config('FLASK_ENV', default='Development').upper()
    if app_mode == 'TESTING':
        return TestingConfig()
    elif app_mode == 'DEVELOPMENT':
        return DevelopmentConfig()
    elif app_mode == 'PRODUCTION':
        return ProductionConfig()
    else:
        raise RuntimeError(f'unrecognised FLASK_ENV={app_mode}')
