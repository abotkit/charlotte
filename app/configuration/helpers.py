import os

from configobj import ConfigObj


def read_config_file(path: str):
    if path is not None and path.endswith('.ini') and os.path.isfile(path):
        return ConfigObj(path)
    else:
        return None


def get_debug_level(debug_level: str):
    if debug_level.upper() == 'DEBUG':
        return '--debug'
    elif debug_level.upper() == 'INFO':
        return '--verbose'
    elif debug_level.upper() == 'WARNING':
        return '--quiet'
    else:
        return '--debug'


def get_default_model(path: str):
    if os.path.exists(os.path.join(path, 'models')):
        files = os.listdir(os.path.join(path, 'models'))
        return os.path.join(path, 'models', files[0])
    else:
        return None


def get_default_actions_file(path: str):
    if os.path.exists(os.path.join(path, 'actions')):
        files = os.listdir(os.path.join(path, 'actions'))
        return os.path.join(path, 'actions', files[files.index('actions.py')])
    else:
        return None


def get_default_domain_file(path: str):
    if os.path.exists(os.path.join(path, 'domain.yml')):
        return os.path.join(path, 'domain.yml')
    else:
        return None


def get_default_nlu_file(path: str):
    if os.path.exists(os.path.join(path, 'data', 'nlu.yml')):
        return os.path.join(path, 'data', 'nlu.yml')
    else:
        return None


def is_valid_rasa_folder(endpoints: str, model: str):
    if os.path.exists(endpoints) and os.path.exists(model):
        return True
    else:
        return False