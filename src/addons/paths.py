import os
from configparser import RawConfigParser

config = RawConfigParser()
path = os.path.join(os.path.split(__file__)[0], 'config.cfg')
config.read('config.cfg')

PROJECTS = config.get('paths', 'projects')
MODELS = { option: os.path.join(*val.split('/')) for option, val in config['paths'].items() if 'models' in val }
TEXTURES = { option: os.path.join(*val.split('/')) for option, val in config['paths'].items() if 'textures' in val }
SOUNDS = { option: os.path.join(*val.split('/')) for option, val in config['paths'].items() if 'sounds' in val }