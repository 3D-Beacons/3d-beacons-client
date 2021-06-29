from pathlib import Path
from prettyconf import config

from prettyconf.loaders import EnvFile

config.loaders = [
    EnvFile('.env.local', var_format=str.upper),
    EnvFile('.env', var_format=str.upper),
]

class Config(object):
    DEBUG = False
    TESTING = False

    BEACON_NAME = config('BEACON_NAME', default='ModelsRUs (London)')

    SECRET_KEY = config(
        'SECRET_KEY', default='fourteen-ants-marching-over-mushrooms')

    QMEAN_DOCKER_IMAGE = config('QMEAN_DOCKER_IMAGE')
    PATH_TO_LOCAL_UNICLUST = config('PATH_TO_LOCAL_UNICLUST')
    PATH_TO_LOCAL_QMTL = config('PATH_TO_LOCAL_QMTL')


    ROOT_DIR = config('BEACON_ROOT', 
        default=(Path(__file__) / '..' / '..').resolve())
    MOLSTAR_GITHUB_URL = config('BEACON_MOLSTAR_GITHUB_URL', 
        default='https://github.com/molstar/molstar.git')
    QMEAN_SUBMIT_URL = config('BEACON_QMEAN_SUBMIT_URL', 
        default='https://swissmodel.expasy.org/qmean/submit/')
    CONTACT_EMAIL = config('BEACON_CONTACT', 
        default='i.sillitoe@ucl.ac.uk')
    GEMMI_EXE = config('BEACON_GEMMI_EXE', 
        default=ROOT_DIR / 'gemmi' / 'gemmi')
    WORK_DIR = config('BEACON_WORKDIR', 
        default=ROOT_DIR / 'work_dir')
    MOLSTAR_PREPROCESS_EXE = ROOT_DIR / 'molstar' / \
        'build' / 'model-server' / 'preprocess.js'

    RESTX_SWAGGER_UI_DOC_EXPANSION = 'list'
    RESTX_VALIDATE = True
    RESTX_MASK_SWAGGER = False
    RESTX_ERROR_404_HELP = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_ECHO = False

    SQLALCHEMY_DATABASE_URI = config('SQL_DATABASE_URI', default=None)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_ECHO = False



class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True

    SQLALCHEMY_DATABASE_URI = None


def get_current_config():
    
    mode = config('FLASK_ENV', default='Development').upper()
        
    if mode == 'TESTING':
        return TestingConfig()
    elif mode == 'DEVELOPMENT':
        return DevelopmentConfig()
    elif mode == 'PRODUCTION':
        return ProductionConfig()
    else:
        raise RuntimeError(f'unrecognised FLASK_ENV={mode}')
